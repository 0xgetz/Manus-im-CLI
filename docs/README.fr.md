<div align="center">
  <img src="../assets/logo.png" alt="Manus-im-CLI Logo" width="160" height="160" />
  <h1>Manus-im-CLI</h1>
  <p><b>Votre Plateforme d'Agents IA Autonomes dans le Terminal</b></p>
  
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

## 🌟 Aperçu

`Manus-im-CLI` est un client d'interface en ligne de commande complet et prêt pour la production pour la **plateforme d'agents IA Manus** (`https://manus.im`), intégrant l'API REST officielle Manus v2 [1]. Il permet aux développeurs, ingénieurs et utilisateurs avancés de créer, surveiller, interagir avec et gérer des tâches d'agents IA autonomes directement depuis le terminal Linux.

<div align="center">
  <img src="../assets/demo.png" alt="Manus-im-CLI Terminal Demo" width="90%" />
  <p><em>Création de tâches interactive et diffusion d'événements en temps réel avec Manus-im-CLI</em></p>
</div>

---

## 🔑 Obtenir une Clé API

Avant d'effectuer des appels API ou de vous authentifier, vous devez créer une clé API :
1. Accédez aux [Paramètres d'intégration de l'API Manus](https://manus.im/app?show_settings=integrations&app_name=api) dans l'application web Manus [2].
2. Cliquez sur **Create API Key** et donnez-lui un nom descriptif (par exemple, `cli-production`) [2].
3. Copiez la clé immédiatement et conservez-la en lieu sûr [2].

---

## 📦 Installation

Sur Linux Ubuntu (20.04 / 22.04 / 24.04), assurez-vous que Python 3.10+ et `pip` sont installés :

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv
```

### Option A : Installation via `pipx` (Recommandé)
```bash
pipx install .
```

### Option B : Installation en mode éditable via `pip`
```bash
pip install -e .
```

---

## 🚀 Démarrage Rapide

1. **S'authentifier en toute sécurité** :
   ```bash
   manus auth login
   ```
   *(Ou définissez la variable d'environnement `MANUS_API_KEY`).*

2. **Vérifier l'authentification** :
   ```bash
   manus auth whoami
   ```

3. **Créer et surveiller une tâche autonome** :
   ```bash
   manus task create "Analyser les tendances du marché technologique au Q2 et compiler les insights clés" --watch
   ```

---

## 📋 Référence des Commandes

### Authentification (`manus auth`)
| Commande | Description |
| :--- | :--- |
| `manus auth login [--api-key KEY]` | Stocke de manière interactive ou via un indicateur votre clé API Manus dans `~/.config/manus/config.toml` (permissions `0600`) [3]. |
| `manus auth whoami` | Vérifie l'état de l'authentification actuelle et récupère les crédits disponibles [3]. |

### Tâches (`manus task`)
| Commande | Description |
| :--- | :--- |
| `manus task create "<prompt>" [options]` | Crée une nouvelle tâche. Prend en charge les indicateurs `--file`, `--project`, `--connector`, `--skill`, `--json` et `--watch`. Accepte l'entrée standard (stdin) si le prompt est `-` ou omis [3]. |
| `manus task list [options]` | Liste les tâches avec filtrage par `--status` (`running`, `stopped`, `waiting`, `error`), `--project` et `--limit` [3]. |
| `manus task get <task_id>` | Récupère les métadonnées détaillées et le statut d'une tâche spécifique [3]. |
| `manus task watch <task_id>` | Diffuse des événements en temps réel, affiche des indicateurs de progression et gère les invites de confirmation interactives (`waiting`) [3]. |
| `manus task send <task_id> "<message>"` | Poursuit une conversation à plusieurs tours avec une tâche active ou en attente [3]. |
| `manus task confirm <task_id> <event_id> [options]` | Confirme ou rejette manuellement les actions en attente (`--accept`, `--reject`, `--input '<json>'`) [3]. |

### Projets (`manus project`)
| Commande | Description |
| :--- | :--- |
| `manus project create <name> [--instruction TEXT]` | Crée un nouveau projet avec des instructions partagées qui s'appliquent automatiquement aux tâches [4]. |
| `manus project list` | Liste tous les projets disponibles sur votre compte [4]. |

### Fichiers (`manus file`)
| Commande | Description |
| :--- | :--- |
| `manus file upload <path>` | Télécharge des fichiers locaux (PDF, images, CSV) via des URL pré-signées pour les pièces jointes aux tâches [5]. |

### Navigateur et Configuration (`manus browser` / `manus config`)
| Commande | Description |
| :--- | :--- |
| `manus browser list` | Liste les clients de navigateur connectés en ligne pour les événements d'attente `needConnectMyBrowser` [6]. |
| `manus config set <key> <value>` | Définit des valeurs de configuration persistantes (par exemple, modifications de l'URL de base) [7]. |
| `manus config list` | Affiche les paramètres de configuration actuels avec masquage automatique de la clé API [7]. |

---

## 🌐 Options Globales

Toutes les commandes prennent en charge les indicateurs globaux suivants :
- `--json` : Génère du JSON structuré lisible par machine pour les scripts et les pipelines d'automatisation.
- `--verbose` / `--debug` : Affiche les journaux de requêtes et de réponses HTTP bruts masqués pour le dépannage.
- `--base-url <url>` : Remplace l'URL de base de l'API par défaut (`https://api.manus.ai`).
- `--no-color` : Désactive le formatage de terminal coloré Rich.

---

## 🛠️ Tests et Développement

Exécutez la suite de tests à l'aide de `pytest` et `respx` pour le mock HTTP :
```bash
pytest
```

Exécutez les linters et les vérifications de format :
```bash
ruff check src tests
black --check src tests
```

---

## 📄 Licence

Distribué sous la **licence MIT**. Voir `LICENSE` pour plus d'informations.

---

## 📚 Références

- [1] Manus API v2 Introduction: `https://open.manus.ai/docs/v2/introduction`
- [2] Manus Authentication Guide: `https://open.manus.ai/docs/v2/authentication.md`
- [3] Manus Task Lifecycle Guide: `https://open.manus.ai/docs/v2/task-lifecycle.md`
- [4] Manus Projects Documentation: `https://open.manus.ai/docs/v2/project.create.md`
- [5] Manus Files Documentation: `https://open.manus.ai/docs/v2/file.upload.md`
- [6] Manus Browser Integration: `https://open.manus.ai/docs/v2/browser.onlineList.md`
- [7] Manus CLI Configuration: `https://open.manus.ai/docs/v2/introduction`
