# AI Infra 术语表（Glossary）

> 和硬件人对话时，**用对词**比用对数字更容易被信任。本表是本课程的统一口径，所有课程都遵守这里的定义。
> 遇到表中没有的词，问我，我会补进来。

## A. 机器三件套：算力 / 容量 / 带宽

| 中文      | 英文（对话用这个词）                        | 一句话定义                                            | 怎么判断                              |
| ------- | --------------------------------- | ------------------------------------------------ | --------------------------------- |
| 流式多处理器  | **SM** (Streaming Multiprocessor) | GPU 里的「小核」，一张 H100 有 132 个；真正干活的单位               | 听到「kernel 占用率低」通常指 SM 没吃满         |
| 张量核心    | **Tensor Core**                   | SM 里专门做矩阵乘的电路。标称 TFLOPS 基本只对它能达到                 | 非矩阵运算（layernorm、softmax、激活）跑不到标称值 |
| 显存      | **HBM / VRAM / GPU memory**       | 卡上的内存，容量单位 GB。`nvidia-smi` 里那个数字                 | 决定「模型能不能装下」，OOM 就发生在这里            |
| 显存带宽    | **memory bandwidth** (TB/s)       | 每秒能从显存搬多少字节到计算单元                                 | 决定 decode 快不快，是推理最常撞的墙            |
| 二级缓存    | **L2 cache**                      | 显存和 SM 之间的中转（H100 约 50 MB）                       | 远小于模型，所以基本还是要回显存读                 |
| 共享内存    | **SRAM / shared memory**          | SM 内部的高速小内存                                      | FlashAttention 这类优化靠它省搬运          |
| 算力      | **FLOPS / TFLOPS**                | 每秒浮点运算次数。注意**稠密(dense)** 与**稀疏(sparse)** 标称差 2 倍 | 厂商标称常写「with sparsity」，砍半才是常规值     |
| 有效算力利用率 | **MFU** (Model FLOPs Utilization) | 实测 FLOPS ÷ 峰值 FLOPS                              | 训练 40%+ 算好；推理 decode 阶段常在个位数      |

## B. 决定性能的核心概念

| 中文 | 英文 | 一句话定义 | 为什么重要 |
|---|---|---|---|
| 算术强度 | **arithmetic intensity** | 一次操作里 算的 FLOP ÷ 搬的字节（FLOP/byte） | 判断你在算力墙还是带宽墙 |
| 屋脊线 | **roofline** | 把「算力上限」和「带宽上限」画在一起的性能模型 | 一眼看出某操作的性能天花板 |
| 脊点 | **ridge point** | 峰值算力 ÷ 峰值带宽，单位 FLOP/byte。H100 约 295 | 算术强度 < 脊点 = 带宽瓶颈 |
| 带宽瓶颈 | **memory-bound** | 时间花在搬数据上，算力闲着 | decode、量化后的推理、小 batch 服务 |
| 算力瓶颈 | **compute-bound** | 时间花在算上，带宽有富余 | prefill、大 batch decode、训练 |
| 预填充 | **prefill** (也叫 processing / prompt phase) | 一次性并行处理整段 prompt，算出 KV | 决定 **TTFT**，通常是算力瓶颈 |
| 解码 | **decode** (也叫 generation phase) | 一次生成一个 token，自回归 | 决定 **TPOT**，几乎总是带宽瓶颈 |
| 首个 token 延迟 | **TTFT** (Time To First Token) | 从发请求到收到第一个 token 的时间 | 用户「感觉快不快」的主要来源；RAG 长 prompt 会拉高它 |
| 每 token 延迟 | **TPOT / ITL** (Time Per Output Token / Inter-Token Latency) | 之后每个 token 的间隔 | = 1000 ÷ 单请求 tok/s |
| 吞吐 | **throughput** | 整机每秒产出多少 token（聚合） | 和延迟是**对立**的：加大 batch 提吞吐、抬延迟 |
| 批大小 | **batch size** | 一次同时处理多少请求 | 摊薄权重读取成本，是服务端最有效的「免费」加速 |
| 连续批处理 | **continuous batching / in-flight batching** | 请求完成即退出、新请求立刻补位，不等整批 | vLLM / TensorRT-LLM 的默认行为，白话叫「动态拼车」 |

## C. 显存容量相关

| 中文 | 英文 | 一句话定义 | 关键数字 |
|---|---|---|---|
| 键值缓存 | **KV cache** | 缓存每层每 token 的 K/V 向量，避免重复计算 | 每 token 字节 = 2 × 层数 × KV头数 × head_dim × 精度字节 |
| 分组查询注意力 | **GQA** (Grouped-Query Attention) | 多个 query 头共享一组 K/V 头 | Llama-3-8B：8 个 KV 头而非 32 个 → KV cache 小 4 倍 |
| 分页注意力 | **PagedAttention** | 把 KV cache 按固定块分页管理（vLLM 的核心） | 消除碎片，吞吐提升 2–4×（[论文](https://arxiv.org/abs/2309.06180)） |
| 显存碎片 | **fragmentation** | 分配了但用不上的显存 | 为什么「显存还够却 OOM」 |
| 显存不足 | **OOM** (Out Of Memory) | 分配失败 | 权重 + KV cache + 激活值 > 容量 |
| 多实例 GPU | **MIG** (Multi-Instance GPU) | 把一张卡切成多个独立小卡 | 云上「1/7 A100」就是 MIG |
| 单卡显存上限 | **HBM capacity** | 决定单卡能装多大模型 | 70B FP16 = 140 GB → 单卡 80 GB 放不下 |

## D. 精度与量化

| 中文 | 英文 | 每参数字节 | 备注 |
|---|---|---|---|
| 单精度 | **FP32** | 4 | 训练老标准，推理很少用 |
| 半精度 | **FP16 / BF16** | 2 | 推理默认。BF16 动态范围更大，更稳 |
| 八位浮点/整数 | **FP8 / INT8** | 1 | 权重量化常用，理论 tok/s 翻倍 |
| 四位整数 | **INT4** | 0.5 | 单机跑大模型的主力，质量有损需评估 |
| 权重量化 | **weight-only quantization** | — | 只压权重、激活仍 FP16 → 主要省带宽和显存 |
| 量化感知训练 | **QAT** | — | 训练时就模拟量化，质量更好但成本高 |
| 投机解码 | **speculative decoding** | — | 小模型草稿 + 大模型校验，用算力换延迟 |
| 稀疏 | **sparsity** | — | 厂商标称的 2× 算力就是它；实际能否吃到看框架 |

## E. 多卡与互联

| 中文 | 英文 | 一句话定义 | 关键数字 |
|---|---|---|---|
| 张量并行 | **TP** (Tensor Parallelism) | 把单层权重切成几份放不同卡，每层都要通信 | 单机内首选，受 NVLink 带宽限制 |
| 流水并行 | **PP** (Pipeline Parallelism) | 按层切分到不同卡，卡间传激活值 | 通信少但有「气泡」 |
| 专家并行 | **EP** (Expert Parallelism) | MoE 模型把不同专家放不同卡 | MoE 推理的关键 |
| 数据并行 | **DP** (Data Parallelism) | 每卡一份完整权重，切分 batch | 主要是训练用 |
| 卡间互联 | **NVLink / NVSwitch** | 机内 GPU 直连 | H100：约 900 GB/s（NVLink 4） |
| 主板总线 | **PCIe Gen5** | 通用外设总线 | 单卡约 64 GB/s 单向，比 NVLink 慢一个数量级 |
| 机间网络 | **InfiniBand / RoCE** | 跨机器互联（如 400G NDR IB） | 决定多机扩展效率 |
| 集合通信 | **all-reduce / all-gather** | 多卡同步权重的操作 | TP 越大，通信占比越高 |

## F. 常见「黑话」直译

| 听到          | 真实含义                                                      |
| ----------- | --------------------------------------------------------- |
| 「这张卡算力多少」   | 通常指 BF16/FP16 Tensor Core 稠密 TFLOPS（问一句「带不带 sparsity」很专业） |
| 「显存爆了」      | KV cache 或激活值 + 权重超容量，不是模型本身装不下                           |
| 「上 TP=8」    | 模型单卡装不下或想提速，用 8 卡切分，代价是每层都要通信                             |
| 「batch 打满」  | 把并发顶到显存能容纳的上限，用延迟换吞吐                                      |
| 「MFU 才 30%」 | 实测只用到峰值算力的 30%，其余在等数据/开销                                  |
| 「这个模型要几张卡」  | 先算权重 GB，再看要不要留 KV cache 空间，再决定 TP 阶数                      |
| 「推理比训练便宜」   | 单次 forward 只需训练 1/3 的 FLOPs，且不用存优化器状态                     |
