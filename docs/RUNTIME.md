# 本地运行环境

状态：基础环境已验证  
最后验证：2026-10-19

## 已安装

- Python 3.12.15，项目内隔离环境；
- ComfyUI 0.41.3；
- comfy-cli 1.22.0；
- comfy-mcp 0.10.0；
- PyTorch 2.14.1 + CUDA 13.0；
- 官方 Workflow Templates 0.11.87。

完整机器可读清单见 `config/runtime-versions.yaml`。

## 目录

```text
runtime/
├─ python/     # Python、comfy-cli、comfy-mcp 与 GPU 依赖
└─ comfy/      # ComfyUI 工作区
```

`runtime/` 不进入 Git。`comfy-cli` 还会按其上游设计在 `%LOCALAPPDATA%\comfy-cli\config.ini` 保存少量 workspace 和后台进程状态；模型、工作流和 Python 包仍位于 E 盘项目运行时目录。

## 日常命令

从项目根目录执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-comfy.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\stop-comfy.ps1
runtime\python\python.exe scripts\verify-mcp.py
```

## 已验证结果

- ComfyUI 仅监听 `127.0.0.1:8188`；
- ComfyUI 正确识别 RTX 5060 和约 8 GB 显存；
- 启动、停止及重启测试通过；
- 标准 Python MCP 客户端成功初始化 `comfy-mcp`；
- MCP 暴露 39 个工具；
- `server_info` 调用成功并返回硬件、workspace、版本和运行状态；
- Codex 已添加全局 `comfy-mcp` stdio 配置；
- Z-Image-Turbo Int8 三个组件已安装并通过官方模板检查；
- 标准 MCP 客户端已完成两次 1024×1024 本地图片生成。

## 已知事项

- Windows 后台启动器会按名称重新调用 `comfy`。`start-comfy.ps1` 只在自己的进程环境中添加隔离环境的 Scripts 路径，不修改系统 PATH。
- comfy-cli 的云端模型知识包需要 Comfy Cloud 登录；项目没有登录，也不依赖该功能。
- ComfyUI-Manager 和第三方 custom nodes 当前未安装。
- `server_info` 的非关键更新检查偶尔会在 15 秒后超时；本地服务状态、MCP 握手和工具调用仍成功。不得把该 `freshness` 字段单独当作服务故障。
- comfy-mcp 0.10.0 的 `validate_workflow` 仍调用已弃用的 `comfy validate`，在当前 Windows/comfy-cli 1.22.0 组合中会超时。官方模板已先由 `templates check` 判定为 `runnable`，MVP 运行时使用显式 `--skip-validation` 兼容开关；不得把此开关用于未经独立检查的任意工作流。
- comfy-cli 的任务句柄默认写入 `%LOCALAPPDATA%\comfy-cli\jobs`。受限沙箱必须获得该目录写权限；普通用户终端不受项目沙箱限制。
- 当前会话实测到进程级写限制：python 只能写工作区与 TEMP，给 `%LOCALAPPDATA%` 目录加 `Everyone:F` 仍被拒绝，说明限制来自令牌而非 ACL。`run-mvp.py` 因此把子进程的 `USERPROFILE`/`LOCALAPPDATA` 指向工作区内的 `runtime/comfy-cli-home/`，让 comfy-cli 的状态文件落进可写范围；该目录位于 `runtime/` 下，不进入 Git。

## 最小生成命令

```powershell
runtime\python\python.exe scripts\run-mvp.py --skip-validation --prompt "你的画面描述"
```

该脚本是普通 MCP stdio 客户端，不依赖 Codex。每次运行会在 `runtime/runs/` 保存准备后的工作流、提示词、任务 ID、结果和输出文件。

## 配方生成命令

`workflows/recipes/` 保存由旧工作流重建的项目配方，均为零 custom-node 的 API 格式：

```powershell
# Anima 核心基线（1024×1024，euler/simple，30 步，CFG 4）
runtime\python\python.exe scripts\run-mvp.py --workflow workflows\recipes\anima-base-core.json `
  --prompt "英文或标签式提示词" `
  --negative "worst quality, low quality, score_1, score_2, score_3, blurry" `
  --seed 12345 --skip-validation

# 加上两枚审美 LoRA 的版本
runtime\python\python.exe scripts\run-mvp.py --workflow workflows\recipes\anima-base-aesthetic-lora.json `
  --prompt "..." --negative "..." --seed 12345 --skip-validation
```

`--seed -1` 会随机取种并记录到清单；`--width`/`--height` 可覆盖配方里的 latent 尺寸。**Anima Base v1.0 不识别中文提示词**，中文输入会产出伪文字图，必须先在提示词编译层转成英文/标签。
