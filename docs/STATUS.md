# 当前状态

最后更新：2026-10-19

## 当前阶段

首个自然语言到本地图像的 MCP MVP 已跑通；旧工作流两轮静态审计、关键兼容性复核和 Anima 核心恢复提案已完成，准备从官方模板导出零 custom-node 的 API 配方。

## 已完成

- 建立项目使命、最终目标和不可破坏的根本约束。
- 确立多 Agent 通用、本地优先、优先复用成熟方案的方向。
- 建立编辑流程、变更日志、ADR、交接和质量门槛。
- 记录首批架构原则：核心与适配器分离、目标级接口、配方优先。
- 完成第一轮官方与社区方案桌面调研，并提出官方控制面优先的候选方案。
- 核实本机 GPU、磁盘、Python 和常见 ComfyUI 路径，并形成隔离安装计划。
- 已连接 GitHub 远程仓库 `Jheyed/AIGC_MCP_Jheyed`。
- 已安装并验证隔离 Python、ComfyUI、comfy-cli 和官方 comfy-mcp。
- 已建立可移植的启动、停止和标准 MCP 验证脚本。
- 已完成首个本地模型候选筛选。
- 已将旧 ComfyUI 的模型、工作流、输入素材和历史输出复制到新项目；第三方节点保存在非激活归档中。
- 已下载 Z-Image-Turbo Int8 官方模型和工作流。
- 已建立 Agent 无关的命令行 MCP 运行器 `scripts/run-mvp.py`。
- 已通过中文自然语言完成两次 1024×1024 本地图片生成。
- 已静态扫描 7 个旧工作流，逐项理解其用途、模型引用和 custom node 职责，并形成 `docs/audits/2026-10-19-legacy-workflows.md`。
- 已确认综合“反推流”实际是 167 节点的一体化个人工作台；当前启用 Anima 与本地 VLM 分支，另外两条 checkpoint 分支缺少模型。
- 已确认旧 custom nodes 仍保持非激活；本轮未安装、加载、执行或修改它们。
- 已用当前 Comfy Org 官方 Anima Base 1.0 模板确认 `qwen_3_06b_base.safetensors` 的 `CLIPLoader.type` 应为 `stable_diffusion`；旧小工作流正确，综合工作台的 `qwen_image` 需要迁移时纠正。
- 已复核 Anima Enhancer、llama-cpp_vlm 和 TT Resolution Selector 的当前许可元数据，并再次确认 Danbooru-Anima-Prompt 没有可信公开来源。
- 已将旧工作流扫描结果拆分为 inactive backend custom、core/frontend virtual 和 missing，避免把 Reroute/Note 误报成缺失插件。
- 已形成不安装任何插件的 `docs/proposals/2026-10-19-anima-baseline-recovery.md`，定义核心替代节点、8 GB 显存策略与逐项 A/B 矩阵。

## 已验证

- 当前 `E:\Project-AIGC` 工作区开始时为空。
- 已初始化本地 Git 仓库。
- 治理文件清单检查通过，文档入口和 ADR 引用存在。
- ComfyUI 0.41.3 启动、停止、重启和系统状态接口均验证通过。
- MCP 0.10.0 标准 stdio 握手成功，发现 39 个工具，`server_info` 调用成功。
- Codex 已注册本地 `comfy-mcp`；标准 Python MCP 客户端也验证成功。
- 官方 Z-Image-Turbo Int8 模板检查结果为 `runnable`，无 API 和第三方节点依赖。
- 第二次生成完整通过 MCP `run_workflow`、`job(wait)` 和 `fetch_outputs`，并保存运行清单。
- 当前 ComfyUI 0.41.3 自带的 Anima Base 1.0 模板与当前公开官方模板一致：1024×1024、30 步、CFG 4、`er_sde/simple`，且只需核心节点。
- 审计脚本 schema v2 扫描 7 个工作流成功；综合工作台识别 27 种 inactive backend custom 和 3 种前端虚拟节点，全部工作流的 `missing_types` 为空。

## 尚未完成

- 尚未最终确定项目层实现语言或目标级 schema。
- 旧工作流第三方节点已完成职责与关键许可证复核，但尚未做当前版本运行兼容性或效果验证，也未激活。
- 尚未从官方 Anima 模板导出项目 API 配方，也没有在本机执行 Anima 生成。
- 尚未验证角色参考、姿势控制或镜头结构化控制。

## 已知风险

- 官方 Comfy MCP 仍可能处于快速变化阶段，需要锁定版本和验证 Windows 行为。
- RTX 5060 约 8 GB 显存会限制模型和组合工作流选择。
- 角色一致性与严格姿势控制可能需要额外模型和 custom nodes，不能在实测前承诺效果。
- 综合工作台把 Anima 的 Qwen 文本编码器写成 `CLIPLoader.type=qwen_image`，与当前官方模板不一致；抽取该分支时必须改为 `stable_diffusion`。
- 综合工作台依赖人工暂停、节点 ID、画布 group/bypass 和多个交互式节点，不适合原样作为 Agent API 配方。
- `ComfyUI-Danbooru-Anima-Prompt` 的归档副本没有可确认的 Git 来源或许可证，不能直接纳入项目发布物。
- Anima Enhancer 与 llama-cpp_vlm 当前上游的 pyproject 都引用不存在的 LICENSE 文件，许可不能确认；TT Resolution Selector 只有 MIT 元数据声明且项目元数据未清理。三者都不进入首个基线。
- ANIMA_BOOSTER 与 BSS FLSampler 使用限制性版权声明，不得把其代码复制、合并或再托管进本项目。
- Git 尚无提交者身份配置，因此当前只初始化了仓库，没有伪造身份创建初始提交。
- 官方 comfy-cli 云端知识包需要 Comfy Cloud 登录；项目没有登录，也不依赖该能力。
- comfy-cli 在 Windows 后台启动时需要命令级 PATH 修正，已封装在项目脚本中。
- MCP `server_info` 的附加更新检查可能超时；本地服务检测与工具调用不受影响。
- MCP `validate_workflow` 与 comfy-cli 1.22.0 存在弃用命令兼容问题；当前只对已由官方模板检查确认可运行的工作流使用显式绕过。
- 受限沙箱若无权写 `%LOCALAPPDATA%\comfy-cli\jobs`，任务提交后无法保存句柄；宿主权限运行已完成端到端验证。

## 下一步

1. 从官方 Anima Base 1.0 模板导出零 custom-node 的 API 工作流，加入受控槽位和运行记录，先做静态验证。
2. 向用户展示 768×768 冒烟配置并取得运行授权，再实测 8 GB 显存下的 1024×1024 官方基线。
3. 定义第一版目标级请求 schema：提示词、角色参考、姿势、镜头、风格和输出参数。
4. 从综合工作台中抽取可替换的“本地图片理解 → 标签整理 → 提示词编译”能力；不得复制来源/许可不明的归档代码。

## 当前是否等待用户决定

否。下一步可以先生成并静态验证核心 API 配方；执行 Anima、安装任何第三方节点或新增大型模型前仍需用户确认。
