# Anima 核心基线恢复提案

日期：2026-10-19  
状态：提案，未安装插件、未执行 Anima 生成

## 要恢复的能力

先恢复一条最小、可解释的 Anima 文生图配方：输入提示词、宽高和 seed，使用本机已有 Anima 模型生成一张图片，并保存完整运行记录。

第一条配方不追求同时复刻旧工作流的加速、细节增强和 2 倍放大。那些能力会在核心基线成功后逐项比较。这样才能知道画质或故障究竟来自模型本身，还是来自某个优化节点。

## 已确认的官方核心基线

当前 ComfyUI 0.41.3 所带 `Text to Image (Anima Base 1.0)` 与 Comfy Org 当前公开模板一致。它只使用核心节点：

1. `UNETLoader`：`anima-base-v1.0.safetensors`，dtype 为 default；
2. `CLIPLoader`：`qwen_3_06b_base.safetensors`，type 为 `stable_diffusion`，device 为 default；
3. 正、负两路 `CLIPTextEncode`；
4. `EmptyLatentImage`：官方默认 1024×1024、batch 1；
5. `KSampler`：30 步、CFG 4、`er_sde` sampler、`simple` scheduler、denoise 1；
6. `VAEDecode`：`qwen_image_vae.safetensors`；
7. 项目配方另接核心 `SaveImage`，并由运行器记录 seed、输入、模型和工作流哈希。

本机已存在三份所需模型，磁盘文件约为 3.90 GiB、1.11 GiB 和 0.24 GiB。文件大小不是显存需求，但说明权重本身合计约 5.25 GiB，8 GB 显存下必须为激活值、采样过程和解码保留空间。

## 旧节点如何处理

| 旧工作流节点或设计 | 核心基线处理 | 后续候选与约束 |
|---|---|---|
| `AnimaBoosterLoader` | 换成官方 `UNETLoader` | 基线不需要。旧上游是限制性版权声明，不复制进项目 |
| `AnimaTeaCache` | 完全关闭 | 可优先评估归档中的 `daraskme/comfy_anima_tea_cache` 候选；其归档含 Apache-2.0，但安装前仍需复核当前上游、兼容性并取得用户确认 |
| `FLS_SamplerV4` | 换成官方 `KSampler` 的 `er_sde/simple` | 它会主动改变局部细节，不是普通采样器替身；上游限制再分发，只能作为独立实验依赖评估 |
| `beta57` scheduler | 换成官方模板的 `simple` | 不为复刻旧参数而先安装 RES4LYF；若以后比较纹理，再单独评估 |
| `AnimaLayerReplayPatcher` | 完全关闭 | 当前上游没有可用 LICENSE，暂不列入可安装候选 |
| `RTXVideoSuperResolution` | 基线不放大 | 后续可评估官方 NVIDIA VFX Nodes（Apache-2.0）；非 AI 尺寸变换可用核心缩放，核心 AI 放大则另需 upscaler 模型 |
| 两枚 aesthetic LoRA | 第一轮关闭 | 不需要 custom node，可用核心 `LoraLoaderModelOnly` 分别 A/B |
| Artist Mixer | 第一轮关闭 | GPL-3.0、Anima 专用；待普通 LoRA 基线稳定后再研究 |
| `TTResolutionSelector` | 请求 schema 直接传 `width`、`height` 整数 | 无需插件；它只是预设列表，不提供生成能力 |

结论：首条 Anima 核心配方所需 custom node 数量是 **0**。

## 8 GB 显存策略

- 第一次只用 batch 1，不同时驻留本地 9B VLM，也不接放大节点。
- 先以 768×768 做冒烟测试，确认模型加载、编码、采样和解码链路；这一步只验证能否运行，不作为画质基准。
- 再运行官方 1024×1024 设置，才建立正式核心基线。
- 旧流程的 1024×1536 比官方方图多约 50% 像素；随后 2 倍边长放大会产生 2048×3072、即 4 倍输出像素。两步不应在第一次运行中耦合。
- 若出现显存不足，记录发生阶段和真实错误，依次降到 896×896、768×768；不通过同时启用缓存或未知优化来掩盖问题。
- 每个实验结束后明确释放不再使用的模型；本地 VLM 反推与 Anima 生图先作为串行任务，而不是同一工作流的常驻分支。

目前没有实测 Anima 峰值显存和耗时，所以这里只能标记为“可尝试但有显存压力”，不能宣称 1024×1024 已在本机通过。

## 分阶段 A/B 测试矩阵

所有对比都固定同一提示词、负面提示、seed、尺寸、步数和模型版本；每次只改变一项。至少保存生成时间、峰值显存、输出文件、工作流哈希和人工观察。

| 阶段 | A | B | 目的 | 进入条件 |
|---|---|---|---|---|
| 0：链路冒烟 | 核心基线，768×768 | 无 | 只确认完整链路和记录机制 | 静态验证通过，用户同意真实运行 |
| 1：官方基线 | 核心基线，1024×1024 | 同配置重复一次 | 确认稳定性与可复现性 | 阶段 0 无错误 |
| 2：分辨率 | 1024×1024 | 1024×1536 | 测显存、耗时与竖图构图 | 阶段 1 稳定 |
| 3a：LoRA 1 | 不加载 LoRA | highres aesthetic，权重 1 | 判断第一枚 LoRA 的独立增益 | 核心画质可接受 |
| 3b：LoRA 2 | 不加载 LoRA | masterpiece v51，权重 1 | 判断第二枚 LoRA 的独立增益 | 同上 |
| 3c：双 LoRA | 更好的单枚配置 | 两枚均为 1 | 检查增益是否叠加、是否过度风格化 | 3a、3b 有明确结论 |
| 4：缓存 | 核心基线 | 单一 TeaCache 候选 | 比较速度、画质漂移和稳定性 | 用户批准安装，许可/版本复核完成 |
| 5：FLS | 核心 KSampler | FLS 原参数 | 判断细节是否真实改善及额外耗时 | 用户批准安装，明确其限制性许可 |
| 6：Layer Replay | 最佳无 replay 配置 | blocks 3/4/5，50%–100% | 判断细节、构图漂移和耗时 | 上游补齐许可或获得明确授权后 |
| 7：放大 | 原尺寸结果 | 独立 2× 放大 | 把生成质量与放大质量分开评价 | 基础生成稳定，用户批准插件或 upscaler 模型 |

缓存、FLS、Layer Replay 和放大不得在其各自完成单项 A/B 前组合。若单项没有稳定收益，就不进入默认配方。

## 恢复时的验收门槛

- 使用 API 格式工作流，且只有提示词、负面提示、seed、宽高等明确槽位可修改。
- 静态检查确认只引用当前可用的核心节点和三份已有模型。
- 首次真实运行前再次获得用户授权；本提案本身不授权安装节点或执行旧代码。
- 真实运行成功后保存规范化请求、实际工作流、模型版本、seed、耗时、错误和输出引用。
- 1024×1024 至少连续成功两次，才把它标为本机已验证基线。
- 任何第三方节点均单独记录仓库、固定版本、许可证、安装内容和退出方式。

## 下一实施步骤

从当前官方模板导出一份简化 API 工作流，增加项目运行记录所需的保存节点和受控槽位，然后只做静态验证。完成后向用户展示将要执行的配置与预计资源，再请求是否进行第一次 Anima 冒烟运行。

## 一手依据

- ComfyUI 官方 Anima 文档：https://docs.comfy.org/tutorials/image/anima/anima
- Comfy Org 官方 Anima Base 1.0 模板：https://github.com/Comfy-Org/workflow_templates/blob/main/packages/blueprints/src/comfyui_subgraph_blueprints/blueprints/text_to_image_anima_base_1_0.json
- 本机对应模板：`runtime/comfy/blueprints/Text to Image (Anima Base 1.0).json`

