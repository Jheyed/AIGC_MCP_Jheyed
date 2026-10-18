# 第三方组件与许可证

本文件记录项目当前实际采用的外部组件。版本升级时必须同步更新。

| 组件 | 当前版本 | 用途 | 许可证 | 来源 |
|---|---:|---|---|---|
| ComfyUI | 0.41.3 | 本地图像工作流执行引擎 | GPL-3.0 | https://github.com/Comfy-Org/ComfyUI |
| comfy-cli | 1.22.0 | 安装、启动、查询和运行 ComfyUI | GPL-3.0-only | https://github.com/Comfy-Org/comfy-cli |
| comfy-mcp | 0.10.0 | 向标准 MCP 客户端暴露 ComfyUI 工具 | AGPL-3.0-or-later 或商业许可 | https://github.com/Comfy-Org/comfy-mcp |
| PyTorch | 2.14.1+cu130 | NVIDIA GPU 推理运行时 | 组合开源许可证，详见上游包 | https://pytorch.org/ |
| ComfyUI Workflow Templates | 0.11.87 | 官方工作流模板库 | MIT | https://github.com/Comfy-Org/workflow_templates |

## 边界说明

- 这些组件安装在被 Git 忽略的 `runtime/` 中，不复制进本项目源码。
- 本项目目前通过命令行、HTTP 和 MCP 进程边界调用它们，没有修改或重新发布其源码。
- 模型权重拥有各自独立许可证。下载任何模型前必须单独记录许可证。

