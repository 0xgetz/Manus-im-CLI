# Audit Awal: `0xgetz/Manus-im-CLI`

**Tanggal audit:** 18 Agustus 2026  
**Pemeriksa:** Manus AI  
**Cakupan:** audit statis terhadap commit `e1756e1` pada cabang `master`, konfigurasi CI publik, metadata repositori, dan metadata rilis. Audit ini tidak menjalankan CLI, tidak memakai kredensial, dan tidak menguji endpoint produksi.

## Kesimpulan eksekutif

**Ya, repositori ini perlu diaudit sebelum diperlakukan sebagai CLI produksi atau direkomendasikan untuk menyimpan API key.** Kode menunjukkan beberapa praktik yang baik, terutama penyimpanan konfigurasi berizin ketat (`0700` pada direktori dan `0600` pada berkas) serta upaya menyamarkan API key pada sebagian output debug. Namun, ada kelemahan yang berisiko terhadap **keandalan pemantauan tugas, keamanan kredensial, kontrol konfirmasi tindakan, dan ketertelusuran rilis**.

Risiko yang paling mendesak adalah logika `task watch`: ia meminta 50 pesan pertama secara ascending tetapi tidak memakai cursor/pagination dan selalu membuang status yang sudah pernah dilihat. Pada tugas yang menghasilkan lebih dari satu halaman event, pemantauan dapat berhenti melihat pembaruan baru atau gagal mengenali status terminal. Selain itu, API key dapat dikirim ke URL dasar yang dapat diubah lewat flag, environment variable, atau konfigurasi tanpa verifikasi skema HTTPS/host, sementara konfirmasi tindakan generik menerima pilihan **accept** sebagai default. [1] [2] [3]

| Penilaian | Jumlah | Makna |
|---|---:|---|
| Tinggi | 2 | Dapat mengganggu fungsi utama atau melemahkan kontrol tindakan secara material. |
| Sedang | 6 | Berpotensi mengekspos data, menyebabkan kegagalan operasional, atau melemahkan rantai pasok. |
| Rendah | 1 | Kerapian tata kelola yang sebaiknya dibereskan saat perbaikan prioritas dilakukan. |
| Kritis | 0 | Tidak ditemukan dalam audit statis terbatas ini. |

## Hal yang sudah baik

Repositori sudah memiliki file `SECURITY.md`, alur CI untuk lint/format/test, dan pemisahan modul antara konfigurasi, transport API, serta perintah CLI. Penyimpanan API key juga secara eksplisit mengatur izin direktori dan file lokal. Mekanisme redaksi khusus API key pada keluaran debug dan `config list` merupakan dasar yang baik, meskipun belum menyelesaikan seluruh jalur kebocoran. [4] [5] [6]

| Kontrol yang ada | Bukti | Catatan audit |
|---|---|---|
| Izin penyimpanan lokal | `~/.config/manus` diatur `0700`; `config.toml` `0600`. | Baik untuk sistem POSIX; perlu penanganan kegagalan dan pengujian izin. |
| Penyaringan token dasar | API key saat ini diganti menjadi `[REDACTED]` dalam beberapa log/debug. | Tidak mencakup rahasia lain di payload. |
| Otomasi kualitas | Workflow menjalankan Ruff, Black, dan Pytest. | Run CI terbaru yang tersedia berstatus gagal dan tidak menjadi pengaman cabang. |
| Kebijakan pengungkapan | `SECURITY.md` tersedia. | Versi yang disebutkan tidak konsisten dengan rilis `v1.0.0`. |

## Temuan terprioritas

### F-01 — Tinggi: `task watch` dapat berhenti menerima event baru dan status terminal

Fungsi `_watch_task_loop` selalu memanggil `list_messages(..., order="asc", limit=50)` tanpa menggunakan `starting_after` atau cursor. Setelah event dicatat dalam `seen_event_ids`, iterasi berikutnya melewati event tersebut; variabel `latest_status` pun direset ke `"running"` pada setiap putaran. Jika API mengembalikan halaman awal ketika urutan ascending dipakai, event setelah 50 pertama tidak pernah dibaca. Bahkan bila halaman berubah, status yang sebelumnya telah dilihat tidak dipertahankan. Konsekuensinya, `--watch` dapat tidak menampilkan instruksi baru, melewatkan pesan kesalahan, atau terus berjalan walaupun tugas sudah berhenti. [1] [7]

| Dampak | Bukti | Perbaikan yang disarankan |
|---|---|---|
| Pemantauan tugas tidak andal; pengguna dapat menunggu tanpa batas atau melewatkan interaksi penting. | Loop pada baris 170–223 meminta halaman fixed-size tanpa cursor dan mereset status lokal. | Simpan cursor event terakhir (`starting_after`) atau gunakan endpoint stream. Pertahankan `latest_status` lintas iterasi, dan lakukan fallback berkala ke `task.detail`. Tambahkan uji >50 event, event terminal, event duplikat, dan event yang datang setelah polling pertama. |

### F-02 — Tinggi: pengamanan rilis dan quality gate belum efektif

Metadata paket, changelog, dan kebijakan keamanan menyebut `0.1.0`/`0.1.x`, sedangkan GitHub Release dan tag publik bernama `v1.0.0`. Rilis tersebut tidak memiliki artefak, tag-nya lightweight, dan workflow CI terakhir yang tersedia berakhir gagal sebelum memiliki langkah yang tercatat. Selain itu, endpoint GitHub melaporkan `master` tidak memiliki branch protection. Kombinasi ini membuat konsumen sulit mengetahui kode mana yang telah tervalidasi, versi mana yang menerima patch keamanan, dan pemeriksaan apa yang wajib lulus sebelum perubahan bergabung. [6] [8] [9] [10]

| Dampak | Bukti | Perbaikan yang disarankan |
|---|---|---|
| Patch keamanan dan distribusi tidak mudah dilacak; perubahan dapat masuk tanpa gate yang tervalidasi. | `pyproject.toml` dan changelog `0.1.0`; release/tag `v1.0.0`; CI gagal; `master` tak terlindungi. | Satu sumber versi menggunakan `hatch-vcs` atau pipeline rilis; buat tag annotated dan signed; bangun wheel/sdist serta checksum/SBOM; perbaiki CI hingga hijau; aktifkan protected branch dengan required checks dan review. |

### F-03 — Sedang: API key dapat diarahkan ke endpoint arbitrer tanpa validasi HTTPS atau host

`get_base_url` menerima nilai dari `--base-url`, `MANUS_BASE_URL`, atau `config.toml`. Nilai tersebut langsung dipakai `httpx.Client`, dan semua request yang memiliki API key selalu menambahkan header `x-manus-api-key`. Tidak ada validasi bahwa URL memakai HTTPS atau host tepercaya. Jalur ini juga digunakan pada `auth login` ketika key diuji. Pengguna yang memasukkan URL salah, konfigurasi yang dimodifikasi pihak lain, atau automation yang salah konfigurasi dapat mengirim key ke layanan yang tidak tepat. [2] [3] [11]

| Dampak | Bukti | Perbaikan yang disarankan |
|---|---|---|
| Kebocoran API key ke host non-tepercaya atau koneksi tanpa TLS. | Resolusi URL dasar dan penyisipan header dilakukan tanpa allowlist/validasi. | Wajibkan `https`; allowlist host resmi secara default; pisahkan mode endpoint kustom yang memerlukan `--allow-custom-endpoint`; jangan kirim API key sampai endpoint lolos validasi; simpan peringatan keamanan yang eksplisit. |

### F-04 — Sedang: konfirmasi tindakan default ke **accept**

Pada event konfirmasi generik, `Confirm.ask` menggunakan `default=True`. Menekan Enter, menjalankan alur noninteraktif secara tidak tepat, atau membaca prompt yang kurang jelas dapat menyebabkan persetujuan tindakan yang seharusnya membutuhkan keputusan eksplisit. Karena command ini memediasi tindakan agen, perilaku fail-open tidak sesuai untuk operasi yang berpotensi eksternal atau berdampak. [1]

| Dampak | Bukti | Perbaikan yang disarankan |
|---|---|---|
| Persetujuan tidak disengaja atas tindakan agen. | Konfirmasi umum diatur `default=True`; skema yang diterima server dapat menawarkan `always_allow`/`global_allow`. | Ubah default menjadi `False`; tampilkan tipe tindakan, target, dan ringkasan dampak; tolak pada input EOF/non-TTY kecuali ada flag eksplisit `--yes`; perlakukan `always_allow` dan `global_allow` sebagai keputusan terpisah yang lebih ketat. |

### F-05 — Sedang: unggahan berkas tidak membatasi tujuan, ukuran, maupun penggunaan memori

Perintah upload menerima `upload_url` dari respons API dan melakukan `httpx.put` langsung tanpa validasi skema/host, sementara berkas dibaca seluruhnya melalui `path.read_bytes()`. Dengan file besar, proses dapat menghabiskan memori dan timeout tetap 60 detik dapat gagal pada jaringan lambat. Tanpa batas ukuran dan kontrol redirect/destinasi, keamanan data bergantung sepenuhnya pada respons API dan konfigurasi endpoint. [12] [13]

| Dampak | Bukti | Perbaikan yang disarankan |
|---|---|---|
| Gagal upload untuk file besar; risiko pengiriman data ke tujuan yang tidak diharapkan jika respons upload disalahgunakan. | `path.read_bytes()` dan `httpx.put(upload_url, ...)` tanpa pemeriksaan tujuan atau streaming. | Validasi URL presigned (`https`, domain/object-storage allowlist bila dapat ditentukan), nonaktifkan redirect lintas-host, lakukan streaming/chunked upload, cek ukuran maksimum sebelum upload, dan tampilkan tujuan upload secara aman bila perlu. |

### F-06 — Sedang: rahasia dan data sensitif masih dapat muncul pada output pengguna/log

`manus config get api_key` mencetak nilai konfigurasi apa adanya. Selain itu, mode debug mencetak `json_data` tanpa redaksi umum; prompt tugas dan pesan dapat berisi token, data pribadi, atau secret lain yang bukan API key saat ini. Walaupun `config list` dan beberapa log HTTP menyamarkan API key, pengguna tetap mudah membocorkan secret ke shell history, terminal recording, CI log, atau tangkapan layar. [5] [14]

| Dampak | Bukti | Perbaikan yang disarankan |
|---|---|---|
| Rahasia lokal dan data prompt dapat terekspos pada kanal observabilitas. | `config get` tidak memperlakukan `api_key` sebagai secret; debug mencetak payload utuh. | Redaksi `api_key` pada `config get` secara default dan gunakan flag `--show-secret` dengan peringatan/Tty check. Jangan cetak payload request secara penuh; implementasikan redaktor rekursif berbasis nama field/regex dan mode debug aman. |

### F-07 — Sedang: dependensi tidak direproduksi secara deterministik dan belum dipindai di CI

Semua dependensi runtime/dev hanya memiliki batas minimum, tanpa lockfile atau constraints. CI memasang `.[dev]` pada saat run, sehingga versi dependency yang diuji hari ini dapat berbeda dari esok hari. Workflow juga memakai action berdasarkan major tag, bukan commit SHA, dan belum mencakup audit dependency, secret scanning, SAST, atau generation SBOM. [6] [15]

| Dampak | Bukti | Perbaikan yang disarankan |
|---|---|---|
| Risiko supply-chain dan hasil CI yang tidak konsisten; CVE sulit dibuktikan terhadap versi yang dipakai. | Rentang `>=` tanpa lockfile; instalasi langsung dari resolver; action `@v4`/`@v5`. | Tambahkan lock/constraints untuk CI dan rilis; jalankan `pip-audit` atau scanner setara; aktifkan Dependabot/Renovate; pin GitHub Actions ke SHA dan beri komentar versi; publikasi CycloneDX/SPDX SBOM. |

### F-08 — Sedang: cakupan pengujian belum memadai untuk jalur berisiko

Repositori berisi sekitar **1.102 baris** kode Python produksi dan satu berkas test dengan **88 baris**. Pengujian yang ada memeriksa beberapa respons API dasar, tetapi tidak mencakup persistensi/izin konfigurasi, redaksi secret, endpoint kustom, upload berkas, retry transport, pagination watch loop, ataupun keputusan konfirmasi. Karena CI publik terbaru gagal, bukti otomatis bahwa skenario ini terus bekerja juga belum tersedia. [1] [6] [15]

| Dampak | Bukti | Perbaikan yang disarankan |
|---|---|---|
| Regresi pada keamanan dan alur CLI dapat lolos tanpa terdeteksi. | Satu modul test berfokus pada empat kasus wrapper API. | Tambahkan unit test parametrik untuk temuan F-01–F-07, integration test dengan mock HTTP, test noninteraktif, serta threshold coverage yang realistis. Jadikan status test wajib pada pull request. |

### F-09 — Rendah: kebijakan keamanan tidak konsisten dengan versi rilis

`SECURITY.md` menyatakan dukungan `0.1.x`, sementara release publik memakai `v1.0.0`. Ini bukan kerentanan langsung, tetapi dapat membingungkan pelapor dan pengguna saat menentukan apakah sebuah perbaikan keamanan telah diterapkan pada versi yang mereka jalankan. [4] [8]

| Dampak | Bukti | Perbaikan yang disarankan |
|---|---|---|
| Proses disclosure dan patch advisory menjadi ambigu. | Dukungan `0.1.x` tidak selaras dengan rilis `v1.0.0`. | Perbarui policy mengikuti sumber versi kanonis; tambahkan riwayat versi, CVE/advisory process, dan security contact yang terverifikasi. |

## Urutan perbaikan yang dianjurkan

Perbaikan awal sebaiknya memulihkan sifat aman dan dapat diprediksi dari alur utama: benahi pagination/watch loop, ubah konfirmasi menjadi fail-closed, dan lindungi API key dari endpoint kustom sebelum menambah fitur baru. Setelah itu, rilis harus direkonsiliasi dan CI dijadikan pengaman cabang, karena tanpa artefak yang konsisten serta pemeriksaan yang benar-benar lulus, perbaikan kode sulit dipercaya oleh pengguna akhir.

| Urutan | Jangka waktu | Hasil yang harus tersedia |
|---:|---|---|
| 1 | 0–2 hari | Patch F-01/F-03/F-04 dengan unit test regresi; default konfirmasi berubah menjadi reject. |
| 2 | 2–5 hari | Upload streaming terbatas ukuran, redaksi secret yang lebih aman, dan test konfigurasi/upload. |
| 3 | 1 minggu | CI hijau, branch protection, dependency audit, lock/constraints, dan action yang dipin ke SHA. |
| 4 | Sebelum rilis berikutnya | Versi tunggal yang konsisten, tag signed/annotated, wheel/sdist, checksum, SBOM, serta changelog dan security policy yang diperbarui. |

## Batasan audit

Audit ini merupakan **review statis awal**, bukan penetration test dan bukan verifikasi bahwa endpoint, identitas pengelola, atau API yang dirujuk oleh proyek tersebut resmi. Tidak ada token dimasukkan, tidak ada task dibuat, tidak ada berkas diunggah, dan tidak ada kode repositori dieksekusi. Karena tidak tersedia lockfile, inventaris versi dependency yang benar-benar terpasang tidak dapat ditentukan secara akurat; akibatnya, penilaian CVE tingkat paket tidak dimasukkan.

> Keputusan praktis: jangan gunakan CLI ini dengan API key produksi atau dokumen sensitif sampai F-01 sampai F-04 setidaknya telah diperbaiki, diuji, dan dirilis melalui pipeline yang tervalidasi.

## Referensi

[1]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/src/manus_cli/commands/task.py#L166-L280 "Task watch loop dan konfirmasi"
[2]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/src/manus_cli/config.py#L42-L61 "Resolusi API key dan URL dasar"
[3]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/src/manus_cli/api/client.py#L15-L61 "Klien HTTP dan header autentikasi"
[4]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/SECURITY.md "Kebijakan keamanan"
[5]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/src/manus_cli/output.py#L35-L46 "Utilitas redaksi output"
[6]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/.github/workflows/ci.yml "Workflow CI"
[7]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/src/manus_cli/api/tasks.py#L25-L35 "Wrapper pagination pesan tugas"
[8]: https://github.com/0xgetz/Manus-im-CLI/releases/tag/v1.0.0 "GitHub Release v1.0.0"
[9]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/pyproject.toml#L5-L30 "Metadata paket dan dependensi"
[10]: https://api.github.com/repos/0xgetz/Manus-im-CLI/branches/master/protection "Status perlindungan cabang master"
[11]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/src/manus_cli/__main__.py#L23-L45 "Penerusan opsi URL dasar"
[12]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/src/manus_cli/commands/file.py#L13-L49 "Perintah unggah berkas"
[13]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/src/manus_cli/api/files.py#L14-L23 "Unggah byte ke URL presigned"
[14]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/src/manus_cli/commands/config.py#L21-L40 "Perintah baca dan daftar konfigurasi"
[15]: https://github.com/0xgetz/Manus-im-CLI/blob/e1756e1/tests/test_api.py "Pengujian yang tersedia"
