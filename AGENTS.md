# AI Agent 工作规则

本文件对所有修改本项目的 AI Agent 生效。核心规则不得只依赖 Codex、Claude 或其他单一产品的专属能力。

## 开始工作前必须阅读

按顺序阅读：

1. `docs/PROJECT_CHARTER.md`
2. `docs/STATUS.md`
3. `docs/DEVELOPMENT_RULES.md`
4. `docs/ARCHITECTURE_PRINCIPLES.md`
5. `docs/QUALITY_GATES.md`
6. `docs/decisions/README.md` 及与当前任务相关的 ADR
7. `CHANGELOG.md` 中最近的记录

若这些文件互相冲突，优先级为：用户当前明确要求 > `PROJECT_CHARTER.md` > 已接受的 ADR > 其他项目文档。

## 修改规则

- 修改前先检查现状，不假设依赖、模型、ComfyUI 或 Git 已存在。
- 优先寻找并评估已发布、活跃且有验证证据的实现；只有现有方案不能满足要求时才自建。
- 不得将核心业务逻辑只实现为某个 Agent 的提示词、Skill、插件或私有配置。
- MCP 工具的输入输出必须有明确 schema；同一核心能力应可由普通 CLI 或测试代码调用。
- 不自动安装未知 custom nodes，不自动下载大型模型，不自动产生云端费用。
- 不提交密钥、访问令牌、个人路径或大型模型文件。
- 不隐藏失败或用伪造输出代替真实验证。
- 保持修改范围聚焦，尊重其他 Agent 和用户留下的未提交修改。

## 每个工作单元结束前必须完成

一个“工作单元”指一次有明确目的、可以独立审阅的修改，而不是每次保存文件。

1. 运行与风险相称的检查或测试。
2. 在 `CHANGELOG.md` 的 `Unreleased` 下记录改了什么、如何验证。
3. 更新 `docs/STATUS.md`：当前状态、已知问题和下一步。
4. 若做出了长期架构或依赖选择，新增 ADR；不得悄悄改变方向。
5. 确认文档、示例和实现没有明显不一致。

## 交接要求

无法完成时，不要只写“未完成”。必须在 `docs/STATUS.md` 中记录：

- 已完成内容；
- 阻塞点和证据；
- 尝试过的方法；
- 推荐的下一步；
- 是否需要用户授权或选择。

