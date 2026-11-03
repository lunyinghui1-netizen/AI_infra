# KV cache 算术速查

> 用途：回答三个问题——「长上下文为什么慢」「这台机器能同时服务几个人」「上下文开多长会 OOM」。
> 公式来源：[NVIDIA Mastering LLM Techniques](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/)、[kipply](https://kipp.ly/transformer-inference-arithmetic/)、[vLLM 论文](https://arxiv.org/abs/2309.06180)。

## 1. 核心公式

```
KV cache 每 token 字节 = 2 × 层数 × KV头数 × head_dim × 精度字节
                       └ K 和 V 各一份

单请求 KV cache (GB) = 上下文长度 × 每 token 字节 ÷ 10⁹

显存预算：  权重 GB + batch × 单请求 KV ≤ 显存容量

最多并发   = (容量 − 权重) ÷ 单请求 KV

decode 每步搬运 ≈ 权重字节 + batch × 单请求 KV字节      ← 分母变大，tok/s 就掉
单请求 tok/s   ≈ 带宽 ÷ (权重字节 + 单个请求 KV字节)
```

最后一条是「上下文越长越慢」的全部机制：长的不是计算，是**每一步都要把那几十 GB 的 KV 再读一遍**。

## 2. 怎么从 config.json 查出参数（别背，去查）

Hugging Face 模型页 → `Files and versions` → `config.json`，找这四个字段：

| config.json 字段 | 进公式的位置 | 例（Llama-3.1-8B） |
|---|---|---|
| `num_hidden_layers` | 层数 | 32 |
| `num_key_value_heads` | KV 头数（**不是** `num_attention_heads`） | 8 |
| `head_dim`（或 `hidden_size / num_attention_heads`） | head_dim | 128 |
| `torch_dtype` / 你的量化设置 | 精度字节 | bfloat16 → 2 |

> ⚠️ 最常见的错：把 `num_attention_heads`（32）当成 KV 头数。GQA 模型里 KV 头只有 8，差 4 倍——这也正是 GQA 存在的理由。

## 3. 常见模型对照（FP16，上下文长度 → 单请求 KV）

| 模型 | 层 | KV头 | KV / token | 8K | 32K | 128K |
|---|---|---|---|---|---|---|
| Qwen2.5-7B | 28 | 4 | 56 KiB | 0.47 GB | 1.9 GB | 7.5 GB |
| Llama-3.1-8B | 32 | 8 | 128 KiB | 1.1 GB | 4.3 GB | 17 GB |
| Llama-3.1-70B | 80 | 8 | 320 KiB | 2.7 GB | 10.7 GB | 43 GB |
| 若不用 GQA（32 头） | 32 | 32 | 512 KiB | 4.3 GB | 17 GB | 67 GB |

最后一行是「同一个 8B 模型、只是没有 GQA」会变成什么样：**KV 大 4 倍**，128K 上下文直接放不进 80 GB 卡。这就是为什么现在的新模型基本都上 GQA。

## 4. 一张表看懂「上下文的三重代价」（Llama-3.1-8B，H100 80 GB，权重 16 GB）

| 上下文 | KV / 请求 | 最多并发 | 单请求 tok/s | 聚合吞吐 |
|---|---|---|---|---|
| 8K | 1.07 GB | 59 | 196 | 约 2 490 |
| 32K | 4.29 GB | 14 | 165 | 约 616 |
| 128K | 17.2 GB | 3 | 101 | 约 149 |

> 聚合吞吐 = 并发 × 带宽 ÷ (权重 + 并发 × KV/请求)。上下文一长，**并发、单请求速度、聚合吞吐三样一起掉**——这就是「长上下文贵」的算术。
> 并发足够大时聚合吞吐趋近 `带宽 ÷ 单请求 KV`：8K 约 3 120，128K 约 195。

## 5. 相关黑话 ↔ 机制

| 黑话 | 机制 |
|---|---|
| 「KV cache 爆了」 | batch × 上下文 × 每 token 字节 > 剩余显存 |
| 「显存还剩不少却 OOM」 | 碎片：请求长度不一，预留的 KV 块用不上（[PagedAttention](https://arxiv.org/abs/2309.06180) 治这个，吞吐 2–4×） |
| 「为什么用 GQA」 | KV 头少 → KV cache 小 → 能塞更多并发 / 更长上下文 |
| 「prefix caching / RadixAttention」 | 共享前缀（system prompt、RAG 文档、Agent 工具描述）只算一次 prefill，复用 KV |
| 「KV cache 量化到 FP8」 | 每 token 字节减半 → 并发翻倍，轻微质量损失 |
| 「chunked prefill」 | 把超长 prefill 拆块，和 decode 交替跑，避免一个长请求把所有人卡住 |
| 「上下文军备竞赛」 | 不是免费功能：128K 意味着 KV 预算里能放的并发只剩个位数 |
