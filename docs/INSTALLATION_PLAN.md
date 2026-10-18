# 第一阶段安装计划

状态：已完成  
日期：2026-10-19

## 目标

只安装打通“Agent → 官方 MCP → 本地 ComfyUI”的基础运行环境。暂不下载大型生成模型，不安装第三方 custom nodes，不连接付费云服务。

## 已确认的机器条件

- Windows；
- NVIDIA GeForce RTX 5060，约 8 GB 显存；
- NVIDIA 驱动 581.57；
- E 盘剩余约 305 GB；
- 当前只有 Python 3.14；
- 未发现 ComfyUI、`comfy-cli` 或 `comfy-mcp`；
- 未发现正在运行的 ComfyUI。

## 推荐安装方式

### 1. 位置

所有项目运行时文件放在：

```text
E:\Project-AIGC\runtime\
```

该目录加入 `.gitignore`，不进入项目版本库。项目代码、schema 和文档继续保存在仓库中。

实际结构：

```text
runtime/
├─ python/       # 隔离的 Python 3.12 环境
└─ comfy/        # comfy-cli 管理的 ComfyUI 工作区
```

### 2. Python

创建独立 Python 3.12 环境，不修改系统 Python 3.14。

理由：ComfyUI 官方说明 Python 3.14 可以运行，但部分 custom nodes 可能有问题；官方 comfy-cli 的 Windows CI 使用 Python 3.12。隔离环境更容易删除、重建和交接。

### 3. ComfyUI

使用官方 `comfy-cli` 安装到指定 workspace，不采用 Windows portable 压缩包。

理由：官方 comfy-cli 当前有一项仍开放的问题：管理 Windows portable 工作区时，可能错误使用系统 Python 而不是 portable 自带解释器。由 comfy-cli 在隔离环境中直接安装能避开这条已知路径。

安装时：

- 使用 NVIDIA 路径；
- 让当前 comfy-cli 根据驱动选择合适的 PyTorch/CUDA 包；
- 固定并记录最终版本；
- 第一轮跳过 ComfyUI-Manager，减少自动安装节点的能力和供应链范围；
- 仅监听 `127.0.0.1`，不使用 `--listen 0.0.0.0`。

### 4. MCP

在同一隔离环境安装官方：

- `comfy-cli`；
- `comfy-mcp`。

先在命令行验证版本和 MCP 握手，再为 Codex 添加客户端配置。其他 Agent 的配置在核心链路稳定后作为薄适配器增加。

### 5. 模型

本阶段不下载模型。完成服务和 MCP 检查后，再单独选择：

- 一个用于最小生成验证的模型；
- 一个面向角色参考的候选模型或工作流。

每个模型下载前单独报告体积、许可证、显存要求和用途。

## 预计影响

- 基础运行时预计占用约 8–15 GB，实际取决于 PyTorch/CUDA 包；
- 后续模型通常每个约数 GB 到数十 GB，不包含在本次范围；
- 会从网络下载 Python 包和 ComfyUI 源码；
- 会写入 `E:\Project-AIGC\runtime`；
- 不会修改系统 Python，不会写入 C 盘模型目录，不会开放网络端口；
- 不会调用付费 API。

实际基础运行时约 4.53 GB。另有 comfy-cli 按上游设计写入 `%LOCALAPPDATA%\comfy-cli\config.ini` 的少量状态数据。

## 安装后的验收

1. 隔离环境中的 Python 为 3.12；
2. `comfy` 和 `comfy-mcp` 能报告版本；
3. ComfyUI 能在 `127.0.0.1:8188` 启动；
4. 系统能识别 RTX 5060 与显存；
5. 官方 MCP 能完成握手并返回服务器信息；
6. 停止服务后不残留未知后台进程；
7. 将实际版本、路径、磁盘占用和问题写入项目日志。

以上七项均已完成。图片生成属于下一阶段，因为基础计划明确不下载模型。

## 回退方式

基础环境完全位于被忽略的 `runtime/`。若安装失败，先保存诊断日志，再删除该隔离运行时即可，不影响系统 Python和项目文档。删除前仍需确认目标路径。

## 依据

- comfy-cli 安装与 workspace 机制：https://github.com/Comfy-Org/comfy-cli
- ComfyUI Python 版本说明：https://github.com/Comfy-Org/ComfyUI
- 官方本地 MCP 前置要求：https://github.com/Comfy-Org/comfy-mcp
- Windows portable 环境识别问题：https://github.com/Comfy-Org/comfy-cli/issues/906
