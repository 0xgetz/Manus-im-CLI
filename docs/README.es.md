<div align="center">
  <img src="../assets/logo.png" alt="Manus-im-CLI Logo" width="160" height="160" />
  <h1>Manus-im-CLI</h1>
  <p><b>Tu Plataforma de Agentes de IA Autónomos en la Terminal</b></p>
  
  <p>
    <a href="../README.md">English</a> |
    <a href="README.zh.md">中文</a> |
    <a href="README.es.md">Español</a> |
    <a href="README.fr.md">Français</a> |
    <a href="README.ja.md">日本語</a>
  </p>

  <p>
    <img src="https://github.com/0xgetz/Manus-im-CLI/actions/workflows/ci.yml/badge.svg?branch=master" alt="CI Status" />
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License" />
    <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python Version" />
    <img src="https://img.shields.io/badge/version-0.1.0-orange.svg" alt="Version" />
  </p>
</div>

---

## 🌟 Descripción General

`Manus-im-CLI` es un cliente de interfaz de línea de comandos completo y listo para producción para la **plataforma de agentes de IA Manus** (`https://manus.im`), que envuelve la API REST oficial de Manus v2 [1]. Permite a desarrolladores, ingenieros y usuarios avanzados crear, monitorear, interactuar y gestionar tareas de agentes de IA autónomos directamente desde la terminal de Linux.

<div align="center">
  <img src="../assets/demo.png" alt="Manus-im-CLI Terminal Demo" width="90%" />
  <p><em>Creación de tareas interactiva y transmisión de eventos en tiempo real con Manus-im-CLI</em></p>
</div>

---

## 🔑 Obtener una Clave API

Antes de realizar llamadas a la API o autenticarse, debe crear una clave API:
1. Vaya a la configuración de [Integración de API de Manus](https://manus.im/app?show_settings=integrations&app_name=api) en la aplicación web de Manus [2].
2. Haga clic en **Create API Key** y asígnele un nombre descriptivo (por ejemplo, `cli-production`) [2].
3. Copie la clave inmediatamente y guárdela de forma segura [2].

---

## 📦 Instalación

En Linux Ubuntu (20.04 / 22.04 / 24.04), asegúrese de tener instalado Python 3.10+ y `pip`:

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv
```

### Opción A: Instalar mediante `pipx` (Recomendado)
```bash
pipx install .
```

### Opción B: Instalar en modo editable mediante `pip`
```bash
pip install -e .
```

---

## 🚀 Inicio Rápido

1. **Autenticarse de forma segura**:
   ```bash
   manus auth login
   ```
   *(O configure la variable de entorno `MANUS_API_KEY`).*

2. **Verificar autenticación**:
   ```bash
   manus auth whoami
   ```

3. **Crear y supervisar una tarea autónoma**:
   ```bash
   manus task create "Analizar las tendencias del mercado tecnológico en el Q2 y recopilar conclusiones clave" --watch
   ```

---

## 📋 Referencia de Comandos

### Autenticación (`manus auth`)
| Comando | Descripción |
| :--- | :--- |
| `manus auth login [--api-key KEY]` | Almacena de forma segura tu clave API de Manus en `~/.config/manus/config.toml` (permisos `0600`) [3]. |
| `manus auth whoami` | Verifica el estado de autenticación actual y recupera los créditos disponibles [3]. |

### Tareas (`manus task`)
| Comando | Descripción |
| :--- | :--- |
| `manus task create "<prompt>" [options]` | Crea una nueva tarea. Soporta `--file`, `--project`, `--connector`, `--skill`, `--json` y `--watch`. Acepta entrada estándar (stdin) si el prompt es `-` o se omite [3]. |
| `manus task list [options]` | Lista tareas filtrando por `--status` (`running`, `stopped`, `waiting`, `error`), `--project` y `--limit` [3]. |
| `manus task get <task_id>` | Recupera metadatos detallados y el estado de una tarea específica [3]. |
| `manus task watch <task_id>` | Transmite eventos en tiempo real, muestra indicadores de carga y maneja confirmaciones interactivas (`waiting`) [3]. |
| `manus task send <task_id> "<message>"` | Continúa una conversación de múltiples turnos con una tarea activa o en espera [3]. |
| `manus task confirm <task_id> <event_id> [options]` | Confirma o rechaza manualmente acciones pendientes (`--accept`, `--reject`, `--input '<json>'`) [3]. |

### Proyectos (`manus project`)
| Comando | Descripción |
| :--- | :--- |
| `manus project create <name> [--instruction TEXT]` | Crea un nuevo proyecto con instrucciones compartidas que se aplican automáticamente a las tareas [4]. |
| `manus project list` | Lista todos los proyectos disponibles en tu cuenta [4]. |

### Archivos (`manus file`)
| Comando | Descripción |
| :--- | :--- |
| `manus file upload <path>` | Sube archivos locales (PDFs, imágenes, CSVs) mediante URLs firmadas para adjuntarlos a tareas [5]. |

### Navegador y Configuración (`manus browser` / `manus config`)
| Comando | Descripción |
| :--- | :--- |
| `manus browser list` | Lista los clientes de navegador conectados en línea para eventos de espera `needConnectMyBrowser` [6]. |
| `manus config set <key> <value>` | Establece valores de configuración persistentes (por ejemplo, cambios en la URL base) [7]. |
| `manus config list` | Muestra la configuración actual con ocultación automática de la clave API [7]. |

---

## 🌐 Opciones Globales

Todos los comandos admiten las siguientes opciones globales:
- `--json`: Genera JSON estructurado legible por máquina para scripts y canalizaciones de automatización.
- `--verbose` / `--debug`: Muestra registros de solicitudes y respuestas HTTP sin procesar pero enmascarados para la solución de problemas.
- `--base-url <url>`: Sobrescribe la URL base de la API predeterminada (`https://api.manus.ai`).
- `--no-color`: Desactiva el formato de terminal Rich con colores.

---

## 🛠️ Pruebas y Desarrollo

Ejecute la suite de pruebas usando `pytest` y `respx` para simulación HTTP:
```bash
pytest
```

Ejecute linters y verificaciones de formato:
```bash
ruff check src tests
black --check src tests
```

---

## 📄 Licencia

Distribuido bajo la **Licencia MIT**. Consulte `LICENSE` para obtener más información.

---

## 📚 Referencias

- [1] Manus API v2 Introduction: `https://open.manus.ai/docs/v2/introduction`
- [2] Manus Authentication Guide: `https://open.manus.ai/docs/v2/authentication.md`
- [3] Manus Task Lifecycle Guide: `https://open.manus.ai/docs/v2/task-lifecycle.md`
- [4] Manus Projects Documentation: `https://open.manus.ai/docs/v2/project.create.md`
- [5] Manus Files Documentation: `https://open.manus.ai/docs/v2/file.upload.md`
- [6] Manus Browser Integration: `https://open.manus.ai/docs/v2/browser.onlineList.md`
- [7] Manus CLI Configuration: `https://open.manus.ai/docs/v2/introduction`
