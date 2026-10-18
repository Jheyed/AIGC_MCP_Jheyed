# ComfyUI Agent 方案调研（第一轮）

日期：2026-10-18  
性质：基于官方文档、项目仓库和论文的一轮桌面调研；尚未在本机安装或运行。

## 结论摘要

目前不建议从零编写 ComfyUI 控制层，也不建议直接完整接管某个社区“大而全”套件。

推荐的起点是：

1. 使用 Comfy Org 官方 `comfy-mcp` / `comfy-cli` 作为底层控制基线；
2. 使用 Comfy Org 官方 `workflow_templates` 作为初始工作流来源；
3. 借鉴 ComfyUI-Agent-Kit 的“共享核心 + 每个 Agent 的薄适配器”结构、硬件感知和知识路由；
4. 在本项目中逐步建立目标级请求、角色包、配方注册表和运行清单；
5. 只有当现有 MCP 的目标级能力明显不足时，才新增独立的创作型 MCP 服务。

这能最大限度复用官方能力，同时避免把项目绑定到某个社区工具或某个 Agent。

## 候选方案对比

| 方案 | 优点 | 局限或风险 | 建议用途 |
|---|---|---|---|
| Comfy Org `comfy-mcp` | 官方；标准 MCP；本地优先；可查询模型/节点/模板、验证和运行工作流、管理任务；核心链路已有端到端验证 | 仍标为 beta；更像控制层而不是完整创作专家；AGPL-3.0-or-later/商业双许可需要保持边界清晰 | **首选底层控制基线** |
| Comfy Org `workflow_templates` | 官方维护；MIT；有 schema、CI 和节点兼容性检查；包含完整工作流与可复用蓝图 | 模板数量多但不等于都适合本机；部分模型可能很大或依赖云 API | **首选配方来源** |
| ComfyUI-Agent-Kit | 明确采用共享核心和多 Agent 薄适配器；硬件感知；大量模型知识和官方模板索引；Apache-2.0 | 能力面很大，安装会拉取多个第三方组件；知识更新快，维护面和供应链面较宽；不能仅凭项目自述视为全部本机已验证 | **重点借鉴架构与知识组织，不先整套安装** |
| HighCWu/artokun `comfyui-mcp` 系列 | 工具面广；支持工作流构建、实时画布、模型和节点管理；展示了统一后端接口与 Codex/Claude 适配 | 系统更复杂；包含面板、编排器、Agent 后端和可选隧道；超过当前 MVP 所需范围 | 借鉴工具分类、画布同步和能力降级 |
| ComfyUI-Agent-Bridge | MCP over HTTP；可在工作流中让图与外部 Agent 交换文本和图片；实现较小 | 需要安装 custom node；主要解决“工作流中途与 Agent 通信”，不是通用创作专家层 | 以后做视觉评价闭环时再评估 |
| ComfyUI-Copilot | 有论文和较完整实现；提供节点/模型推荐及自动工作流构建；针对新手痛点 | 形态是 ComfyUI 内部 Copilot/custom node，而不是通用外部 MCP；与我们跨 Agent 接口目标不完全一致 | 借鉴意图分析、知识库和分层 Agent 设计 |

## 关键证据

### 1. 官方本地 MCP 已经覆盖底层控制

官方仓库将本地 MCP 定义为通过 `comfy-cli` 驱动本地 ComfyUI 的 stdio MCP。仓库当前标注 beta，并说明有 40 个工具，核心链路已经按 `server_info → run_workflow → fetch_outputs` 在真实本地 ComfyUI 上验证。

这意味着本项目没有理由重新实现任务提交、状态轮询、模型/节点查询和输出获取等基础能力，除非实测发现阻塞。

来源：https://github.com/Comfy-Org/comfy-mcp

### 2. 官方模板适合作为“配方事实来源”

官方 `workflow_templates` 仓库提供工作流模板、子图蓝图、索引 schema 和 CI 校验。官方模板原则上不使用第三方节点，降低了新手安装失败概率；仓库也提供与本地 ComfyUI 节点的兼容性检查。

来源：

- https://github.com/Comfy-Org/workflow_templates
- https://github.com/Comfy-Org/workflow_templates/blob/main/docs/SPEC.md
- https://docs.comfy.org/interface/features/template

### 3. “共享核心 + 薄适配器”已有社区实践

ComfyUI-Agent-Kit 将共同知识和 MCP 驱动放在共享层，为 Claude Code、Codex、Gemini CLI 和 Qwen Code 提供各自适配器。这个结构与本项目的多 Agent 根本要求一致。

但该套件还会获取 MCP 驱动、模板库、图内 LLM 节点和节点构建技能等多个第三方组件。当前更适合作为架构和知识参考，而不是未经审查直接整套安装。

来源：

- https://github.com/SlavaSexton/ComfyUI-Agent-Kit
- https://github.com/SlavaSexton/ComfyUI-Agent-Kit/blob/master/docs/AGENTS.md
- https://github.com/SlavaSexton/ComfyUI-Agent-Kit/blob/master/ATTRIBUTION.md

### 4. 自动自由构建工作流仍需要验证闭环

ComfyUI-Copilot、ComfyBench/ComfyAgent 等工作表明，意图分析、知识检索、专用 Agent 和执行反馈能够改善自动工作流构建。但这也说明仅让语言模型一次性输出节点 JSON 并不足够，可靠方案需要知识库、分步规划和运行反馈。

来源：

- https://github.com/AIDC-AI/ComfyUI-Copilot
- https://arxiv.org/abs/2506.05010
- https://arxiv.org/abs/2409.01392

## 初步架构建议

### 第一层：现成控制面

先原样使用官方 `comfy-mcp`，不 fork、不修改。它负责：

- 环境和硬件检查；
- 模型、节点和模板查询；
- 工作流验证与运行；
- 队列、日志、错误和输出管理。

### 第二层：本项目的可移植知识与数据

使用普通文件保存：

- 目标级生成请求 schema；
- 角色资产包 schema；
- 配方元数据与兼容性；
- 镜头、姿势和风格预设；
- 运行清单与评价结果。

这些内容不依赖任何 Agent。

### 第三层：创作规划

MVP 先让 Agent 根据同一份项目规则，把自然语言转换为结构化请求并选择配方。待积累真实案例后，再把稳定规则下沉为代码和目标级 MCP 工具。

这样可以避免在需求尚未清楚时过早设计一个错误的 MCP 工具集合。

### 第四层：客户端适配

每个 Agent 只包含：

- 如何连接 MCP；
- 如何加载共享项目说明；
- 客户端特有的显示或确认方式。

不得复制并分叉核心创作知识。

## 为什么现在不直接安装某个“大而全”套件

- 当前工作区还没有 ComfyUI，无法验证安装器会修改哪些路径。
- 机器只有约 8 GB 显存，模型选择必须先做本机能力判断。
- 一次安装大量节点和模板会扩大故障面，不利于建立可解释的 MVP。
- 用户希望边做边改，因此需要先获得最小真实反馈，再决定哪些高级功能值得固化。

## 下一步验证计划

在用户批准安装范围后：

1. 确认 ComfyUI 的安装方式和位置；
2. 安装并固定一个官方 ComfyUI 版本；
3. 独立安装官方 `comfy-mcp` 和符合要求的 `comfy-cli`；
4. 验证服务状态、硬件查询、模板搜索和一个最小工作流；
5. 记录 Windows、RTX 5060 8 GB 和路径处理的实际结果；
6. 再决定是否需要引入 Agent-Kit 的知识文件或社区 MCP 的部分能力。

## 当前推荐但尚未验证的选择

- 底层控制：官方 `Comfy-Org/comfy-mcp`；
- 工作流来源：官方 `Comfy-Org/workflow_templates`；
- 项目层：本仓库自有的轻量目标 schema、角色包、配方注册表和运行记录；
- 多 Agent 方式：共享核心文档与数据 + 各客户端薄配置；
- 第一版策略：固定配方优先，不开放任意 custom node 自动安装。

