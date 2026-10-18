# 变更日志

本项目记录每个可独立审阅的工作单元。版本发布时，将 `Unreleased` 中的内容整理到对应版本。

## Unreleased

### 2026-10-19 — 建立 Git 版本基线并推送远端

- 变更：为仓库配置提交者身份（账户 `Jheyed` + GitHub 匿名邮箱，仅写入本仓库 local config，未改全局设置）；本地分支 `master` 更名为 `main`；新增首个提交 `52209ef`，纳入治理文档、运行环境记录、脚本、官方工作流与上一轮审计成果共 28 个文件、3229 行；推送到 `origin/main` 并建立跟踪关系。
- 原因：此前仓库零提交、全部文件未跟踪，项目承诺的“可追溯”缺少版本层支撑；远端仓库为空，首次推送同时确定默认分支。
- 验证：提交前全仓扫描 `sk-`、`api_key`、`password`、`ghp_`、Bearer 模式均无命中；`runtime/`、模型权重与缓存由 `.gitignore` 排除，实际入库约 134 KB；`git status` 干净；`git push` 退出码 0，远端新建 `main`。
- 已知问题：上一轮 Agent 的收尾写入发生在本次读取文档期间（01:33–01:36），已确认其成果全部包含在 `52209ef` 中，没有覆盖或丢失；全仓文件为 LF，全局 `core.autocrlf=true` 会在后续检出时转 CRLF，可能产生整文件 diff 噪声。

### 2026-10-19 — 完成旧工作流兼容性复核与 Anima 恢复提案

- 变更：用当前 Comfy Org 官方模板确认 Anima 的 Qwen 0.6B 文本编码器应使用 `CLIPLoader.type=stable_diffusion`；复核 Anima Enhancer、llama-cpp_vlm、TT Resolution Selector 与来源不明 Danbooru 插件的许可状态；将静态审计脚本升级为 schema v2，分别输出 inactive backend custom、core/frontend virtual 和 missing；新增零 custom-node 的 Anima 核心恢复提案、8 GB 显存策略和逐项 A/B 矩阵。
- 原因：消除旧工作流中最关键的加载器歧义，避免因前端虚拟节点误报而误装插件，并给下一 Agent 留下可直接实施但不会擅自安装依赖的恢复路径。
- 验证：脚本通过 Python 编译；连接当前 ComfyUI 0.41.3 的 `/object_info`（987 种节点）扫描全部 7 个工作流；所有工作流的 `missing_types` 均为空，Reroute/Note/MarkdownNote 正确归为前端虚拟节点；本机与当前公开的官方 Anima Base 1.0 模板都显示 `stable_diffusion`。本轮没有运行 Anima、加载归档代码、安装节点、下载资产或调用外部服务。
- 已知问题：Anima Enhancer 与 llama-cpp_vlm 当前仓库仍缺少 pyproject 所引用的 LICENSE；TT Selector 只有 MIT 元数据声明且含模板占位符；Danbooru-Anima-Prompt 仍无可信公开来源。它们均不进入核心基线。

### 2026-10-19 — 完成旧工作流第一轮静态审计并建立交接记录

- 变更：新增 `scripts/audit-legacy-workflows.py` 和旧工作流审计报告；扫描 7 个工作流，记录每条工作流的真实用途、当前分支、模型可用性、全部相关 custom node 的职责、联网/人工交互边界、许可证与恢复优先级。
- 原因：在启用历史插件前先理解旧资产，避免把个人交互工作台直接当作稳定 Agent 配方，也为不同 Agent 的后续审查保留共同事实。
- 验证：脚本通过 Python 编译检查；从当前 ComfyUI `/object_info` 取得 987 个节点类型并完成静态扫描；核对归档源码、README、许可证、Git remote 和当前上游仓库；确认本轮没有加载旧插件或调用外部服务。
- 已知问题：静态扫描仍会把 Reroute/Note 等前端虚拟节点列为服务端缺失；Anima 文本编码器类型存在不一致；部分插件缺少可核实许可证或原始上游；这些已列入接手任务。

### 2026-10-19 — 跑通首个自然语言 MCP 生图 MVP

- 变更：下载并校验 Z-Image-Turbo Int8 的三个官方模型组件；保存官方工作流；新增 Agent 无关的标准 MCP 客户端 `scripts/run-mvp.py`；完成两次中文提示词的 1024×1024 本地生成。
- 原因：验证“自然语言 → 标准 MCP → 本地 ComfyUI → 本地模型 → 输出与运行清单”的最小闭环。
- 验证：官方模板检查为 `runnable`、三个模型齐全、无 API/custom nodes；第二次生成完整通过 `run_workflow`、`job(wait)`、`fetch_outputs`，任务 `f052bccf-3911-4c0b-bb92-5085ed55123f` 成功。
- 已知问题：`validate_workflow` 在 comfy-mcp 0.10.0/comfy-cli 1.22.0 Windows 组合中调用弃用命令并超时；只对已由官方模板检查确认的工作流使用显式兼容开关。受限沙箱还需写入 `%LOCALAPPDATA%\comfy-cli\jobs` 的权限。

### 2026-10-19 — 迁移旧 ComfyUI 资产

- 变更：从 ``E:\`resource\AIGC\ComfyUI-zove4\ComfyUI`` 复制 27.57 GiB 模型、8 个工作流、5 个输入素材和 154 个历史输出；把 6,630 个第三方节点文件保存为非激活归档。
- 原因：复用用户已经使用过的资产，同时避免把未知版本的第三方代码直接注入已验证的新运行环境。
- 验证：工作流、输入、输出和节点归档的源/目标文件数与总字节一致；模型源文件的总字节一致，新目录仅额外包含 5 个新版 ComfyUI 的零字节占位文件。
- 后续：按旧工作流实际依赖逐个确认上游来源、许可证和兼容版本，再干净安装所需节点。

### 2026-10-19 — 安装并验证官方本地控制链路

- 变更：连接 GitHub 远程仓库；安装隔离 Python 3.12.15、ComfyUI 0.41.3、comfy-cli 1.22.0、comfy-mcp 0.10.0 和 PyTorch 2.14.1+cu130；添加启动、停止与标准 MCP 验证脚本；记录第三方许可证与机器可读版本清单。
- 原因：建立可跨 Agent 使用的官方本地控制基线，为后续目标级创作能力提供真实运行环境。
- 验证：ComfyUI 启停与 `system_stats` 通过；正确识别 RTX 5060 8151 MB；标准 MCP 客户端握手成功并发现 39 个工具；`server_info` 成功；Codex 已注册同一 stdio MCP；基础运行时约 4.53 GB。
- 已知问题：首次后台启动因隔离环境 Scripts 不在 PATH 而失败，现已通过命令级 PATH 修正封装在 `scripts/start-comfy.ps1`；没有修改系统 PATH。`server_info` 的非关键更新检查偶尔会在 15 秒后超时，但本地服务状态与 MCP 调用成功。
- ADR：ADR-0003 仍为 Proposed，等待真实工作流执行和输出获取验证。

### 2026-10-19 — 筛选首个本地模型

- 变更：比较官方 Z-Image-Turbo Int8、Qwen Image 2.1 Turbo Image Edit 和 FLUX 3 Image Klein 工作流，推荐先用 Z-Image-Turbo Int8 完成最小生成验证。
- 原因：它使用官方无第三方节点模板、适合 8 GB 显存、许可清晰，并可把第一轮下载控制在约 11.34 GB。
- 验证：官方模板兼容性检查确认只缺三个模型文件且不依赖 API/custom nodes；文件大小来自 Hugging Face 官方模型仓库元数据。尚未下载模型或生成图片。

### 2026-10-18 — 制定隔离安装计划

- 变更：记录本机 GPU、磁盘、Python 和 ComfyUI 状态；制定基于 E 盘、隔离 Python 3.12、官方 comfy-cli/comfy-mcp 且暂不下载模型的安装计划。
- 原因：降低对系统环境的影响，并避开当前 Windows portable 工作区的官方已知问题。
- 验证：通过本机只读命令确认 RTX 5060 8 GB、驱动 581.57、E 盘约 305 GB 可用、Python 3.14 以及未发现现有 ComfyUI；安装尚未执行。
- ADR：ADR-0003（仍为 Proposed）。

### 2026-10-18 — 完成第一轮现有方案调研

- 变更：比较官方 Comfy MCP、官方工作流模板、ComfyUI-Agent-Kit、社区 MCP/Bridge 和 ComfyUI-Copilot；提出以官方控制面和官方模板为首选基线的候选架构。
- 原因：落实“优先寻找已发布且得到验证的相似方案”，避免重复实现底层控制能力。
- 验证：所有关键结论均链接到项目官方仓库、官方文档或原始论文；尚未进行本机运行验证，已在调研文档和状态文件中明确区分。
- ADR：ADR-0003（Proposed，等待本机验证）。

### 2026-10-18 — 建立项目治理基线

- 变更：建立项目根本要求、架构原则、协作规范、质量门槛、当前状态、ADR 机制和 Agent 强制规则。
- 原因：确保不同 Agent 可以依据项目内的共同事实继续工作，并防止核心能力绑定单一 Agent。
- 验证：必需治理文件清单、文档入口与 ADR 引用检查通过；`git diff --check` 无格式错误；已初始化本地 Git 仓库。因未配置提交者身份，未创建初始提交。
- ADR：ADR-0001、ADR-0002。
