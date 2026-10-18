# 首个本地模型选择

状态：已下载并完成真实生成验证  
日期：2026-10-19

## 推荐：Z-Image-Turbo Int8

建议先用官方 `image_z_image_turbo_int8` 工作流完成第一张本地图。

理由：

- 官方模板，无第三方 custom nodes；
- 完全本地，不依赖付费 API；
- Int8 版本比 BF16 更适合 8 GB 显存；
- 模型支持中英文提示词；
- 后续已有官方 Z-Image ControlNet 模板，可继续探索姿势控制；
- Apache-2.0 模型许可证相对清晰。

需要下载的三个文件：

| 文件 | 用途 | 大小 |
|---|---|---:|
| `z_image_turbo_int8_convrot.safetensors` | 图像扩散模型 | 5.78 GB |
| `qwen_3_4b_fp8_mixed.safetensors` | 文本编码器 | 5.25 GB |
| `ae.safetensors` | VAE | 0.31 GB |
| **合计** |  | **约 11.34 GB** |

来源：https://huggingface.co/Comfy-Org/z_image_turbo

## 实际安装结果

| 文件 | 实际字节 | SHA-256 |
|---|---:|---|
| `qwen_3_4b_fp8_mixed.safetensors` | 5,631,994,051 | `72450b19758172c5a7273cf7de729d1c17e7f434a104a00167624cba94f68f15` |
| `z_image_turbo_int8_convrot.safetensors` | 6,201,001,296 | `be517ebd47c912a5626a588e1aeea43e6be4a43c0cdcd2b48a2a780d9f358635` |
| `ae.safetensors` | 335,304,388 | `afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38` |

官方 `templates check image_z_image_turbo_int8` 结果为 `runnable`：三个模型全部存在，无 API 依赖、无第三方节点依赖、无警告。

标准 MCP 客户端已完成两次中文提示词生成，输出均为 1024×1024 PNG。第二次完整经过 `run_workflow`、`job(wait)` 和 `fetch_outputs`。

## 它能验证什么

- 官方模板获取与兼容性检查；
- MCP 提交、等待和输出下载；
- 8 GB 显存下的模型卸载/权重调度；
- 中英文自然语言到提示词的基础链路；
- 完整运行清单和复现记录。

## 它暂时不能证明什么

- 角色参考一致性；
- 多张角色参考图；
- 精确姿势遵从；
- 自动视觉评价。

这些能力需要后续图像编辑模型、ControlNet 或其他参考机制。第一张图成功后再选，避免一次下载多个大型模型却无法判断问题来源。

## 后续候选

### Qwen Image 2.1 Turbo Image Edit

官方模板明确面向多参考图和角色一致性，但需要四个大型组件，下载和运行负担明显高于第一阶段；其模型卡许可证是 `qwen-research`，需要进一步审阅。

来源：https://huggingface.co/Comfy-Org/Qwen-Image-2.1

### FLUX 3 Image Klein

支持文本生成、单参考编辑和最多十张参考图，也有面向 8 GB GPU 的量化文件。但完整官方工作流还需要独立文本编码器和提示词扩写器，总下载量较大；仓库需要登录并接受条件，许可证也不是 Apache/MIT，因此暂不作为第一步。

来源：https://huggingface.co/black-forest-labs/flux-3-image-klein-comfy
