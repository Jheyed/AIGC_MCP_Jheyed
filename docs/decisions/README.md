# 架构决策记录（ADR）

ADR 用于保存会长期影响项目的决定，使新的 Agent 不依赖历史对话也能理解“为什么这样做”。

## 状态

- `Proposed`：正在讨论；
- `Accepted`：当前采用；
- `Deprecated`：仍可能存在，但不建议继续使用；
- `Superseded`：已被新的 ADR 替代。

## 命名

```text
NNNN-short-decision-title.md
```

## 索引

- [ADR-0001：采用多 Agent、标准接口优先的架构](0001-agent-neutral-standard-interfaces.md)
- [ADR-0002：MVP 采用已验证配方优先](0002-validated-recipes-first.md)
- [ADR-0003：以官方 Comfy MCP 和官方模板作为首选基线](0003-official-control-plane.md)（Proposed）

## 新 ADR 模板

```markdown
# ADR-NNNN：标题

- 状态：Proposed
- 日期：YYYY-MM-DD

## 背景

## 决策

## 理由

## 后果

## 替代方案

## 验证或复审条件
```
