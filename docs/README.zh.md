<div align="center">
  <img src="../assets/logo.png" alt="Manus-im-CLI Logo" width="160" height="160" />
  <h1>Manus-im-CLI</h1>
  <p><b>终端中的自主 AI 智能体平台客户端</b></p>
  
  <p>
    <a href="../README.md">English</a> |
    <a href="README.zh.md">中文</a> |
    <a href="README.es.md">Español</a> |
    <a href="README.fr.md">Français</a> |
    <a href="README.ja.md">日本語</a>
  </p>

  <p>
    <img src="https://github.com/0xgetz/Manus-im-CLI/actions/workflows/ci.yml/badge.svg" alt="CI Status" />
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License" />
    <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python Version" />
    <img src="https://img.shields.io/badge/version-0.1.0-orange.svg" alt="Version" />
  </p>
</div>

---

## 🌟 概述

`Manus-im-CLI` 是 **Manus AI 智能体平台** (`https://manus.im`) 的功能完整、生产就绪的命令行接口客户端，全面封装了官方 Manus REST API v2 [1]。它赋予开发者、工程师和高级用户直接从 Linux 终端创建、监控、交互和管理自主 AI 智能体任务的能力。

<div align="center">
  <img src="../assets/demo.png" alt="Manus-im-CLI Terminal Demo" width="90%" />
  <p><em>Manus-im-CLI 交互式任务创建与实时事件流</em></p>
</div>

---

## 🔑 获取 API 密钥

在进行 API 调用或身份验证之前，您需要从账户中生成一个 API 密钥：
1. 访问 Manus Web 应用中的 [Manus API 集成设置](https://manus.im/app?show_settings=integrations&app_name=api) [2]。
2. 点击 **Create API Key** 并为其赋予描述性名称（例如 `cli-production`）[2]。
3. 立即复制密钥并将其安全保存 [2]。

---

## 📦 安装

在 Linux Ubuntu (20.04 / 22.04 / 24.04) 系统上，确保已安装 Python 3.10+ 和 `pip`：

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv
```

### 方式 A：通过 `pipx` 安装（推荐）
```bash
pipx install .
```

### 方式 B：通过 `pip` 以可编辑模式安装
```bash
pip install -e .
```

---

## 🚀 快速开始

1. **安全认证**：
   ```bash
   manus auth login
   ```
   *（或设置 `MANUS_API_KEY` 环境变量）。*

2. **验证认证状态**：
   ```bash
   manus auth whoami
   ```

3. **创建并监视自主任务**：
   ```bash
   manus task create "分析第二季度科技市场趋势并汇编关键洞察" --watch
   ```

---

## 📋 常用命令参考

### 身份认证 (`manus auth`)
| 命令 | 说明 |
| :--- | :--- |
| `manus auth login [--api-key KEY]` | 交互式或通过参数将 Manus API 密钥安全存储在 `~/.config/manus/config.toml` 中（权限 `0600`）[3]。 |
| `manus auth whoami` | 验证当前认证状态并检索可用平台额度 [3]。 |

### 任务管理 (`manus task`)
| 命令 | 说明 |
| :--- | :--- |
| `manus task create "<prompt>" [options]` | 创建新任务。支持 `--file`、`--project`、`--connector`、`--skill`、`--json` 和 `--watch` 标志。提示词为空或 `-` 时从标准输入读取 [3]。 |
| `manus task list [options]` | 列出任务，支持按 `--status`（`running`、`stopped`、`waiting`、`error`）、`--project` 和 `--limit` 过滤 [3]。 |
| `manus task get <task_id>` | 检索特定任务的详细元数据和状态 [3]。 |
| `manus task watch <task_id>` | 实时流式传输事件、显示加载动画并处理交互式确认提示 (`waiting`) [3]。 |
| `manus task send <task_id> "<message>"` | 与活动或等待中的任务继续进行多轮对话 [3]。 |
| `manus task confirm <task_id> <event_id> [options]` | 手动确认或拒绝挂起的动作（`--accept`、`--reject`、`--input '<json>'`）[3]。 |

### 项目管理 (`manus project`)
| 命令 | 说明 |
| :--- | :--- |
| `manus project create <name> [--instruction TEXT]` | 创建带有共享指令的新项目，该指令将自动应用于任务 [4]。 |
| `manus project list` | 列出账户中的所有可用项目 [4]。 |

### 文件上传 (`manus file`)
| 命令 | 说明 |
| :--- | :--- |
| `manus file upload <path>` | 通过预签名 URL 上传本地文件（PDF、图片、CSV 等）作为任务附件 [5]。 |

### 浏览器与配置 (`manus browser` / `manus config`)
| 命令 | 说明 |
| :--- | :--- |
| `manus browser list` | 列出在线连接的浏览器客户端，用于处理 `needConnectMyBrowser` 等待事件 [6]。 |
| `manus config set <key> <value>` | 设置持久化配置值（例如覆盖 API 基准 URL）[7]。 |
| `manus config list` | 显示当前配置设置，并自动对 API 密钥进行脱敏处理 [7]。 |

---

## 🌐 全局选项

所有命令均支持以下全局标志：
- `--json`：输出结构化机器可读的 JSON，用于脚本编写和自动化管道。
- `--verbose` / `--debug`：打印脱敏后的原始 HTTP 请求和响应日志，用于故障排查。
- `--base-url <url>`：覆盖默认的 API 基准 URL (`https://api.manus.ai`)。
- `--no-color`：禁用彩色 Rich 终端格式化。

---

## 🛠️ 测试与开发

使用 `pytest` 和用于 HTTP 模拟的 `respx` 运行测试套件：
```bash
pytest
```

运行代码检查与格式化：
```bash
ruff check src tests
black --check src tests
```

---

## 📄 许可证

本项目基于 **MIT 许可证** 开源。详情请参见 `LICENSE` 文件。

---

## 📚 参考文献

- [1] Manus API v2 Introduction: `https://open.manus.ai/docs/v2/introduction`
- [2] Manus Authentication Guide: `https://open.manus.ai/docs/v2/authentication.md`
- [3] Manus Task Lifecycle Guide: `https://open.manus.ai/docs/v2/task-lifecycle.md`
- [4] Manus Projects Documentation: `https://open.manus.ai/docs/v2/project.create.md`
- [5] Manus Files Documentation: `https://open.manus.ai/docs/v2/file.upload.md`
- [6] Manus Browser Integration: `https://open.manus.ai/docs/v2/browser.onlineList.md`
- [7] Manus CLI Configuration: `https://open.manus.ai/docs/v2/introduction`
