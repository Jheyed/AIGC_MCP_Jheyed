# 旧 ComfyUI 资产迁移

状态：已复制并完成数量/字节核对  
日期：2026-10-19

## 来源

旧环境：``E:\`resource\AIGC\ComfyUI-zove4\ComfyUI``

本次只复制，不移动、不删除、也不修改旧环境。

## 已复制内容

| 内容 | 数量 | 大小 | 新位置 | 状态 |
|---|---:|---:|---|---|
| 模型 | 44 个文件 | 27.57 GiB | `runtime/comfy/models/` | 已激活，可被新 ComfyUI 扫描 |
| 用户工作流 | 8 个 JSON | 208.3 KiB | `runtime/comfy/user/default/workflows/` | 已进入新 ComfyUI 工作流目录 |
| 输入素材 | 5 个文件 | 4.51 MiB | `runtime/comfy/input/` | 已激活 |
| 历史输出 | 154 个文件 | 179.02 MiB | `runtime/comfy/output/imported-zove4/` | 只作历史留存 |
| 第三方节点 | 6,630 个文件 | 4.73 GiB | `runtime/legacy-imports/ComfyUI-zove4/custom_nodes/` | **非激活归档** |

源与目标的文件数量和总字节已逐类核对一致。新模型目录另有 5 个由新版 ComfyUI 自带的零字节目录占位文件，不属于旧环境。

## 旧模型概况

- `models/LLM/`：约 21.83 GiB，主要为多个 Qwen 3.5 GGUF 量化版本；
- `models/diffusion_models/`：约 3.90 GiB，包含 `anima-base-v1.0.safetensors`；
- `models/text_encoders/`：约 1.11 GiB；
- `models/loras/`：约 0.50 GiB；
- `models/vae/`：约 0.24 GiB；
- 其他目录包含 ControlNet、IPAdapter、放大模型等目录或占位文件。

## 用户工作流

- `测试D站插件0.2.json`
- `动漫通用反推流自用V2.6.json`
- `anima-txt2img-aesthetic-lora-artist-mixer.json`
- `anima-txt2img-aesthetic-lora-enhancer.json`
- `anima-txt2img-aesthetic-lora-fixed.json`
- `anima-txt2img-aesthetic-lora.json`
- `anima-txt2img-base.json`
- `.index.json`

## 为什么第三方节点暂不激活

旧目录包含约 30 个节点项目，其中部分附带数 GiB 模型、缓存或 Python 依赖。直接把它们放进 ComfyUI 0.41.3 的活动 `custom_nodes/` 目录，可能造成启动失败、依赖冲突或执行未知代码。

后续按以下方式逐个恢复：

1. 审计一个目标工作流实际使用的节点类型；
2. 确认节点的原始仓库、许可证和当前兼容版本；
3. 从上游干净安装，而不是直接激活归档副本；
4. 启动测试、工作流验证和一次真实生成均通过后，才标记为可用；
5. 把版本、来源和验证结果写入 `THIRD_PARTY.md` 与 `CHANGELOG.md`。

归档副本用于找回配置、确认旧版本和处理上游项目消失的情况，不作为默认执行代码。
