# 旧工作流静态审计（交接记录）

日期：2026-10-19  
范围：`runtime/comfy/user/default/workflows` 中的 7 个旧工作流，以及它们实际引用的归档 custom nodes。  
审计方式：读取工作流 JSON、归档插件源码/README/许可证、当前 ComfyUI `/object_info`，并核对上游仓库。没有加载或执行归档插件。

## 结论先行

这些文件包含两类资产：

1. 五个小型 Anima 文生图 API 工作流：结构清楚，但把模型加载、实验性采样、缓存和 RTX 2 倍放大耦合在一起。
2. 一个 167 节点的个人综合工作台，加一个 31 节点的 Danbooru 插件测试图。综合工作台同时处理图片反推、标签整理、三种生图模型、文生图/图生图、参数切换和结果对比，不适合原样作为 Agent 自动化底座。

建议恢复顺序：

1. 先把 `anima-txt2img-base.json` 重建为“核心节点优先”的可运行基线；把缓存、FLS 和 RTX 放大做成可选阶段。
2. 再恢复 `anima-txt2img-aesthetic-lora-fixed.json`，验证两个审美 LoRA 的真实增益。
3. 从综合工作台中只提取“本地 VLM 图片描述 → 标签整理 → 提示词组合”能力，移除人工暂停节点和 UI 组开关。
4. Artist Mixer 与 Layer Replay 分别作为后续风格实验和细节实验，不进入首个稳定配方。

当前没有任何旧 custom node 被启用。本报告不是“兼容性已通过”的证明。

## 工作流逐项理解

| 工作流 | 真实用途 | 关键设置 | 当前判断 |
|---|---|---|---|
| `anima-txt2img-base.json` | Anima 基础文生图，附带加速、细节采样和 2 倍 RTX 放大 | 1024×1536、30 步、CFG 4.5、DPM++ 2M SDE GPU、beta57、TeaCache、FLS、最终 2× | 最适合先拆解恢复；当前输出目标相当于 2048×3072，8 GB 显存上应先关闭放大验证 |
| `anima-txt2img-aesthetic-lora.json` | 基础流加两个仅作用于模型的审美 LoRA | highres aesthetic + masterpiece v51，权重均 1；scheduler 为 `beta` | 旧版本；相对 fixed 版唯一明确差异是 scheduler |
| `anima-txt2img-aesthetic-lora-fixed.json` | 上一工作流的修正版 | scheduler 改为 `beta57` | 作为审美版候选，但尚未执行验证 |
| `anima-txt2img-aesthetic-lora-enhancer.json` | 审美版再加 Anima 内部层重放，以加强后半程细节 | replay blocks 3/4/5，作用区间 50%–100%；Spectrum 关闭 | 实验配方，效果和耗时必须 A/B 测试 |
| `anima-txt2img-aesthetic-lora-artist-mixer.json` | 把多个画师标签分开编码后在注意力层混合，减少 Anima 的画师风格互相污染 | output average、interpolate、strength 1、negative 不应用 | 文件里的 `artist_chain` 为空；填入画师链以前不会发挥目标能力 |
| `动漫通用反推流自用V2.6.json` | 图片反推与生图一体化工作台，不只是“反推流” | 167 节点；95 active、72 bypass；当前启用 Anima 分支与本地 VLM；另有 Noob/CKNoob、在线反推、WD14 等旁路分支 | 有可复用知识，但不适合作为机器稳定调用的单个配方 |
| `测试D站插件0.2.json` | Danbooru/Anima 标签插件的诊断和 UI 测试图 | 31 节点，19 个 PreviewAny；不含生图链 | 仅保留作插件行为参考，不列为产品工作流 |

### 综合工作台的当前激活状态

- 当前生图模型：Anima（UNet `anima-base-v1.0`、Qwen 3 0.6B 文本编码器、Qwen Image VAE）。
- 当前采样：36 步、CFG 4、Euler/simple、denoise 0.65；这更像图生图重绘设置，而不是纯文生图默认值。
- 文生图与图生图 latent 通过开关汇合；分辨率当前为 896×1152。
- 本地反推使用 Qwen3.5 9B GGUF + mmproj，8,192 context；系统提示要求客观描述主体、空间关系、动作和镜头，并避免风格词。
- 在线 LLM 分支处于 bypass，API key 为空；该节点会把图片或视频编码后发送到配置的外部 OpenAI-compatible 服务。
- WD14 两个节点均处于 bypass。
- Noob 和 CKNoob 两个 checkpoint 分支处于 bypass，而且对应两个 checkpoint 文件目前不存在。
- 两个 active 的 `LoraLoader`（节点 911、912）没有任何连线，是残留孤立节点，不会把 LoRA 应用到输出。
- `DanbooruTextPassthrough` 会暂停后端执行并等待网页端人工点击继续。这与无人值守 Agent 调用直接冲突，抽取时必须替换。
- 工作流内含成人内容相关的旧提示词数据。审计文档不复制这些文本；后续导出模板前应将提示词和可能的凭据视为用户数据清理。

## custom node 逐项说明

### 五个小型 Anima 工作流

| 节点 | 来源 | 用途 | 审计意见 |
|---|---|---|---|
| `AnimaBoosterLoader` | `BlackSnowSkill/ANIMA_BOOSTER` | 以优化路径加载 Anima DiT；可选 SageAttention 和 `torch.compile`，缺失时回落到 PyTorch 路径 | 工作流关闭了 SageAttention 与 compile。上游 README 为 all-rights-reserved 且禁止未经许可复制、合并和再托管；可以依赖安装，但不可把代码收入本项目 |
| `AnimaTeaCache` | 同上 | 根据相邻去噪状态跳过部分 Transformer 计算；v1 偏速度，v2 偏精确 | 工作流使用 v1、threshold 0.15、adaptive；可能改变画质，必须有关闭缓存的对照测试 |
| `FLS_SamplerV4` | `BlackSnowSkill/ComfyUI-BSS_FLSampler` | 比较各步预测 clean latent，生成活动区域 mask，在局部做 latent 锐化和微噪声注入 | 它不是普通 KSampler 的同义替换；会主动改变细节。上游同样为限制性版权声明，不可 vendor/修改后分发 |
| `RTXVideoSuperResolution` | `Comfy-Org/ComfyUI_Nvidia_VFX_Nodes`（旧名 Nvidia RTX Nodes） | NVIDIA VFX SDK 的 AI 放大；旧文件选 2×、ULTRA | 官方插件，Apache-2.0，仅 NVIDIA RTX；当前 RTX 5060、CUDA 13 满足新上游基本条件。先在生成后单独验证，以免掩盖基础图质量或触发显存问题 |
| `AnimaLayerReplayPatcher` | `AdamNizol/ComfyUI-Anima-Enhancer` | 在指定去噪区间重复若干 Anima 内部 block，目标是增强细节和一致性；可选 Spectrum 加速 | 只用于 enhancer 变体；当前上游仍缺少其 `pyproject.toml` 所引用的 LICENSE 文件，不能纳入稳定依赖 |
| `AnimaArtistPack` | `An1X3R/Anima-Artist-Mixer` | 拆分画师链，用同一个基础提示分别编码 | Anima 专用 |
| `AnimaArtistOptions` | 同上 | 设置参与的 block、采样区间、归一化和筛选规则 | 高级选项容器 |
| `AnimaArtistCrossAttn` | 同上 | 克隆并 patch 模型，在 cross-attention 中混合各画师输出 | GPL-3.0；上游明确说明仍可能改变构图。当前工作流的空 artist chain 需先修正 |

### 综合工作台和插件测试图

| 节点或节点族 | 来源 | 用途 | 自动化影响 |
|---|---|---|---|
| `AnimaDexBrowser` | 归档 `ComfyUI-Danbooru-Anima-Prompt` | 联网浏览 animadex.net，选取画师标签 | 交互式、联网；不应成为核心运行必需项 |
| `DanbooruBrowser` | 同上 | 在节点 UI 搜索 Danbooru 图片并输出图片及分类标签 | 联网、交互式，并注册多条 Web 路由；适合作为素材探索工具，不适合无头核心 |
| `DanbooruTagClassifier` | 同上 | 把原始标签分成质量、人数、角色、系列、画师，以及身体、服装、姿势、表情、背景、配饰等 | 有本地数据库时可本地查表，未命中可调用 Danbooru API；分类逻辑值得抽取为普通服务/纯函数 |
| `AnimaPromptConverter` | 同上 | 按 Anima 或 Noob/CKNoob 规则排序、格式化标签；为 Anima 画师加 `@`，可转义括号和处理下划线 | 高复用价值，应从 UI 节点解耦为 Agent 可直接调用的提示词编译器 |
| `DanbooruText` | 同上 | 普通字符串输入/输出 | 可由核心文本参数替代 |
| `DanbooruTextAdvanced` | 同上 | 带模糊搜索 UI 的文本输入 | UI 辅助，不是推理能力 |
| `DanbooruTextConcat` | 同上 | 最多合并 6 路文本，可选分隔符 | 可用简单核心逻辑替代 |
| `DanbooruTextPassthrough` | 同上 | 在队列执行中弹出内容并暂停，允许用户编辑后继续 | 阻塞自动化，必须删除或替换为“可选审批步骤” |
| `DanbooruTagDedup` | 同上 | 按原顺序去除重复逗号标签 | 简单、值得在提示词编译阶段复用 |
| `DanbooruTagPreview` | 同上 | 在 UI 显示标签并透传 | 仅 UI 观察用途 |
| `DanbooruNodeBypass` | 同上 | 配合前端按节点 ID 控制 bypass | 高度绑定某张图的节点 ID，不应进入目标级 MCP 契约 |
| `TagMapper` | 同上 | 让用户为未分类 tag 选择分类，并把映射写回插件 JSON | 会修改插件目录中的状态；知识应迁移到项目自己的版本化数据文件 |
| `GroupIgnoreManager` | `Aaalice233/ComfyUI-Danbooru-Gallery` | 纯 UI 虚拟节点，管理整组 ignore 状态和组间联动 | 不执行推理；Agent 配方应使用显式参数/分支，不依赖画布组状态 |
| `Comfly_LLm_API` | `T8mars/Comfyui-zhenzhen` | 调 OpenAI-compatible 外部 LLM/VLM；图片/视频会 base64 后上传 | 当前旁路且无 key。属于外部数据传输和潜在付费能力，默认不得启用 |
| `LayerUtility: ImageScaleByAspectRatio V2` | `aining2022/ComfyUI_Swwan` | 依宽高比做 letterbox/crop/fill，按长边、短边、宽高或像素数缩放，并同步 mask | 能用核心图像缩放组合替代；若保留需固定 fit 语义，防止参考图被裁错 |
| `Lora Loader (LoraManager)` | `willmiao/ComfyUI-Lora-Manager` | 从文本/元数据选择并堆叠多个 LoRA，输出触发词与加载清单 | 工作台当前该节点没有配置 LoRA，只负责将模型传入 KSampler；核心 Agent 不应依赖其大型管理 UI |
| `TTResolutionSelector` | `AICoderTudou/ComfyUI-TT-Resolution_selector-Node` | 把分辨率预设或自定义宽高输出成整数 | 可直接由目标级 schema 的 width/height 取代；归档缺少独立 LICENSE，pyproject 声称 MIT 但元数据仍含模板占位符 |
| `WD14Tagger\|pysssss` | `pythongosssss/ComfyUI-WD14-Tagger` | 用 WD14 ONNX 模型从图片提取 booru tags，可设一般/角色阈值 | MIT；首次可能下载模型。适合以后作为本地标签补充，但当前工作流旁路 |
| `llama_cpp_model_loader` | `lihaoyun6/ComfyUI-llama-cpp_vlm` | 从 `models/LLM` 加载 GGUF；mmproj 使文本模型具备图片输入；可按 VRAM 限制决定 GPU layers | 本地隐私友好，但 9B Q6 + BF16 mmproj 在 8 GB GPU 上资源较重。当前上游仍缺少其 `pyproject.toml` 所引用的 LICENSE 文件，不能纳入稳定依赖 |
| `llama_cpp_instruct_adv` | 同上 | 把系统提示、用户提示和图片交给本地 VLM，返回文本/列表 | 这是综合工作台最值得保留的“本地图片理解”能力；应独立成一个可替换的视觉描述接口 |
| `Any Switch (rgthree)` | `rgthree/rgthree-comfy` | 从多个任意类型输入中选择有效输入，用于分支汇流 | UI 工作台方便；Agent 配方宜在提交前确定分支，避免运行时图开关 |
| `Image Comparer (rgthree)` | 同上 | 在前端滑动对比两张图 | 仅人工评审 UI，不是自动评价 |
| `Seed (rgthree)` | 同上 | 集中控制 seed 及随机/固定策略 | 可由目标级请求的 seed 字段替代 |
| `easy float` | `yolain/ComfyUI-Easy-Use` | 输出浮点常量 | 可由原生 primitive/请求参数替代 |
| `easy showAnything` | 同上 | 把任意值序列化显示到节点 UI，并透传 | 调试辅助 |
| `easy cleanGpuUsed` | 同上 | 触发显存/缓存清理后透传输入 | 运行策略辅助，不应散落在业务图中；需要在配方层统一管理模型卸载 |
| `Float` | 归档 `ComfyLiterals` | 把字符串转为 float | 简单常量节点，可移除 |
| `ComfySwitchNode` | `comfy-core` 元数据显示为核心节点 | 布尔开关选择输入；该旧图来自 core 0.19.1 | 不是第三方插件；当前 ComfyUI 0.41.3 已在 `/object_info` 注册同名实验性 `If/Else Switch`，但稳定 Agent 配方仍宜在提交前确定分支 |
| `PrimitiveBoolean`、`PrimitiveInt`、`PreviewAny` | ComfyUI 核心 | 常量和预览 | 非第三方依赖 |
| `Reroute`、`Note`、`MarkdownNote` | 画布/前端辅助 | 整理连线和说明 | 不参与生成结果；静态脚本把它们列为“服务端未注册”，不代表缺插件 |

## 模型资产核对

已存在：Anima UNet、Qwen 0.6B 文本编码器、Qwen Image VAE、三枚 Anima LoRA、Fenrir LoRA、Qwen3.5 9B GGUF 与对应 mmproj。

缺失：

- `ChenkinNoob-XL-v0.3-Rectified-Flow.safetensors`
- `Stable-diffusion\noobaiXLNAIXL_vPred10Version.safetensors`

因此综合工作台即使补齐所有插件，也不能原样恢复全部三条模型分支。

## 已发现的兼容与设计风险

1. 小型 Anima API 工作流把 Qwen 文本编码器的 `CLIPLoader.type` 写成 `stable_diffusion`，这与当前官方 Anima Base 1.0 模板一致；综合工作台写成 `qwen_image`，恢复该分支时应改为 `stable_diffusion`。
2. 小工作流最终固定做 2× ULTRA 放大；这会把 1024×1536 变成约 2048×3072，且让“生成质量”和“放大质量”难以分别评价。
3. TeaCache、FLS、Layer Replay 都会改变执行或图像，不应同时开启后再把结果当作模型基线。
4. 综合工作台用画布 group、bypass、节点 ID 和人工暂停组织逻辑，难以稳定转成 API workflow，也不利于不同 Agent 调用。
5. `ComfyUI-Danbooru-Anima-Prompt` 归档没有 Git remote 与许可证文件，来源和再分发权不明；它还会联网、注册 Web API、写入用户映射，并可自动下载约 2.2 GB BGE-M3。只能当作待验证原型代码，不能直接收入项目发布物。
6. 多个插件的 README 性能数字来自作者声明，尚未在本机验证。

## 来源与许可摘要

| 归档项目 | 上游 | 归档许可状态 |
|---|---|---|
| ANIMA_BOOSTER | https://github.com/BlackSnowSkill/ANIMA_BOOSTER | README 限制性版权声明，无 LICENSE 文件 |
| ComfyUI-BSS_FLSampler | https://github.com/BlackSnowSkill/ComfyUI-BSS_FLSampler | README 限制性版权声明，无 LICENSE 文件 |
| ComfyUI-Anima-Enhancer | https://github.com/AdamNizol/ComfyUI-Anima-Enhancer | 当前仓库根目录没有 LICENSE；pyproject 指向一个不存在的 LICENSE 文件，许可不能确认 |
| Anima-Artist-Mixer | https://github.com/An1X3R/Anima-Artist-Mixer | GPL-3.0 |
| Nvidia VFX Nodes | https://github.com/Comfy-Org/ComfyUI_Nvidia_VFX_Nodes | Apache-2.0 |
| Danbooru-Anima-Prompt | 未找到可确认的原始上游 | 无 LICENSE、无 `.git` 来源；用项目名、节点名和独有路由进行公开检索仍无精确结果，不得再分发 |
| ComfyUI-Danbooru-Gallery | https://github.com/Aaalice233/ComfyUI-Danbooru-Gallery | MIT |
| Comfyui-zhenzhen | https://github.com/T8mars/Comfyui-zhenzhen | Apache-2.0 |
| ComfyUI_Swwan | https://github.com/aining2022/ComfyUI_Swwan | MIT |
| ComfyUI-Lora-Manager | https://github.com/willmiao/ComfyUI-Lora-Manager | GPL-3.0 |
| TT Resolution Selector | https://github.com/AICoderTudou/ComfyUI-TT-Resolution_selector-Node | 当前 pyproject 以 SPDX 名称声明 MIT，但仓库仍无 LICENSE 全文，且作者/仓库 URL 留有模板占位符；只能记为“MIT 元数据声明、打包不完整” |
| ComfyUI-WD14-Tagger | https://github.com/pythongosssss/ComfyUI-WD14-Tagger | MIT |
| ComfyUI-Easy-Use | https://github.com/yolain/ComfyUI-Easy-Use | GPL-3.0 |
| ComfyUI-llama-cpp_vlm | https://github.com/lihaoyun6/ComfyUI-llama-cpp_vlm | 当前仓库根目录没有 LICENSE；pyproject 指向一个不存在的 LICENSE 文件，许可不能确认 |
| rgthree-comfy | https://github.com/rgthree/rgthree-comfy | MIT |
| ComfyLiterals | 归档没有 Git 元数据 | 尚未核实 |

## 第二轮复核结论

- 当前官方 ComfyUI 文档把 Anima Base v1 描述为 2B 文生图模型，并指定同一组 UNet、Qwen 3 0.6B 文本编码器与 Qwen Image VAE。官方工作流模板的 `CLIPLoader` 值明确为 `qwen_3_06b_base.safetensors / stable_diffusion / default`。本机 ComfyUI 0.41.3 所带模板与当前公开模板一致。
- 官方模板的纯核心基线是 `UNETLoader + CLIPLoader + CLIPTextEncode + EmptyLatentImage + KSampler + VAEDecode`，默认 1024×1024、30 步、CFG 4、`er_sde/simple`。因此恢复第一条 Anima 配方不需要任何 custom node。
- Anima Enhancer 与 llama-cpp_vlm 的当前仓库文件列表均没有 LICENSE，而各自 pyproject 却声明 `license = {file = "LICENSE"}`。这不是有效的许可证证据，应继续视为许可未确认。
- TT Resolution Selector 当前 pyproject 明示 `license = {text = "MIT"}`，但没有 LICENSE 全文，而且项目元数据仍含 `Your Name` 和 `yourusername` 占位符。它的功能可直接由宽高整数参数取代，没有引入必要性。
- `ComfyUI-Danbooru-Anima-Prompt` 仍找不到可信公开上游。归档 README 只说明 ZIP 安装，代码引用的是 DanbooruSearchOnline 等数据来源，不能据此推断插件自身作者或许可。
- 审计脚本 schema 已升至 v2，将服务端未注册类型拆成 `backend_custom_types`、`core_frontend_virtual_types` 和 `missing_types`。本轮 7 个工作流中没有无法识别的 `missing` 类型；`Reroute`、`Note`、`MarkdownNote` 不再误报成第三方节点。
- 不安装恢复提案见 `docs/proposals/2026-10-19-anima-baseline-recovery.md`。

## 后续边界

1. 先从官方纯核心模板生成 API 工作流并静态验证，再请求用户授权做真实 Anima 运行。
2. 第三方节点必须一次只引入一个，并用固定 seed 做 A/B；不能把缓存、FLS、Layer Replay、放大同时打开。
3. 安装或启用任何 custom node 前必须再次取得用户确认。

## 本次验证记录

- `scripts/audit-legacy-workflows.py` 通过 Python 编译检查。
- 通过当前 ComfyUI `/object_info` 获取 987 个注册节点类型并完成 7 个工作流静态扫描。
- v2 分类结果：5 个小型工作流分别识别 4–7 种 inactive backend custom；综合工作台识别 27 种 backend custom 和 3 种前端虚拟节点；插件测试图识别 8 种 backend custom 和 1 种前端虚拟节点；全部工作流的 `missing_types` 均为空。
- 当前 `/object_info` 已确认 `ComfySwitchNode` 为核心实验性 `If/Else Switch`。
- 当前硬件再次核实为 RTX 5060 8,151 MiB，驱动 581.57；项目运行时为 PyTorch 2.14.1+cu130，CUDA 可用。
- 仅做静态审计，没有执行旧工作流、加载旧插件、调用外部 API 或下载额外资产。

## 本轮一手来源（访问于 2026-10-19）

- ComfyUI 官方 Anima 文档：https://docs.comfy.org/tutorials/image/anima/anima
- Comfy Org 官方 Anima Base 1.0 模板：https://github.com/Comfy-Org/workflow_templates/blob/main/packages/blueprints/src/comfyui_subgraph_blueprints/blueprints/text_to_image_anima_base_1_0.json
- Anima Enhancer 上游：https://github.com/AdamNizol/ComfyUI-Anima-Enhancer
- llama-cpp_vlm 上游：https://github.com/lihaoyun6/ComfyUI-llama-cpp_vlm
- TT Resolution Selector 上游：https://github.com/AICoderTudou/ComfyUI-TT-Resolution_selector-Node
