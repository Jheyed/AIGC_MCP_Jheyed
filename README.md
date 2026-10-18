# Project AIGC

一个面向普通创作者的、与具体 AI Agent 无关的 ComfyUI 智能创作层。

用户描述“想要什么”，系统负责选择经过验证的工作流、模型与参数，驱动本地 ComfyUI，并保存可解释、可复现的结果。项目首先支持 Codex，但不得把核心能力绑定在 Codex 上；其他支持 MCP 或命令行调用的 Agent 应能顺畅接手。

## 当前阶段

治理规范和基础运行环境已经建立。官方 ComfyUI、comfy-cli 与 comfy-mcp 已完成标准 MCP 验证；Z-Image-Turbo Int8 已通过中文自然语言完成两次 1024×1024 本地生成。旧 ComfyUI 的模型、工作流和素材也已复制，第三方节点暂存为非激活归档。

## 文档入口

所有参与者，包括 AI Agent，都应按以下顺序阅读：

1. [项目根本要求](docs/PROJECT_CHARTER.md)
2. [当前状态](docs/STATUS.md)
3. [协作与编辑规范](docs/DEVELOPMENT_RULES.md)
4. [架构原则](docs/ARCHITECTURE_PRINCIPLES.md)
5. [质量与验收标准](docs/QUALITY_GATES.md)
6. [架构决策记录](docs/decisions/README.md)
7. [变更日志](CHANGELOG.md)

已执行的基础环境方案见 [第一阶段安装计划](docs/INSTALLATION_PLAN.md)。

当前运行环境见 [本地运行环境](docs/RUNTIME.md)，首个模型建议见 [首个本地模型选择](docs/MODEL_SELECTION.md)。

旧环境资产迁移范围和安全策略见 [旧 ComfyUI 资产迁移](docs/LEGACY_ASSET_IMPORT.md)。

面向自动化 Agent 的强制规则位于 [AGENTS.md](AGENTS.md)。

## 目标体验

```text
用户自然语言 + 角色/姿势等参考资产
                ↓
任意 AI Agent
                ↓ 标准 MCP 或 CLI
本项目的创作专家层
                ↓
经过验证的 ComfyUI 工作流
                ↓
本地模型生成结果 + 完整运行记录
```

## 核心原则摘要

- 多 Agent 通用，不把核心逻辑只写在某个 Agent 的专属配置中。
- 优先复用网络上已有且得到验证的方案，再做个性化扩展。
- 本地优先，云端与付费能力必须显式选择。
- 先使用可靠的工作流配方，再逐步开放自动构图能力。
- 每次生成和每次项目修改都可追溯、可解释、可复现。
