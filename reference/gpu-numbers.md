# GPU 关键数字速查（AI Infra）

> 用途：**,给「硬件人」的数字做量级判断**。看到一个模型 / 一张卡，先用这里的表估出上限，再听对方说的数字。
> 规格会随型号和批次变，**要确切数字请查一手来源**：[NVIDIA Data Center GPU Line Card (PDF)](https://docs.nvidia.com/data-center-gpu/line-card.pdf)。

## 1. 数据中心 / 消费级 GPU 速查

| GPU | 显存容量 | 显存带宽 | **脊点** | BF16/FP16 稠密算力 | 备注 |
|---|---|---|---|---|---|
| A100 40 GB SXM | 40 GB HBM2 | 1.55 TB/s | ~200 FLOP/B | 312 TFLOPS | 上一代主力；非 Tensor Core 只有 19.5 TFLOPS |
| A100 80 GB SXM | 80 GB HBM2e | 2.04 TB/s | ~153 FLOP/B | 312 TFLOPS | 同算力、带宽更高 |
| H100 SXM | 80 GB HBM3 | 3.35 TB/s | ~295 FLOP/B | ~990 TFLOPS | TP=2 才能放下 70B FP16 |
| H200 SXM* | 141 GB HBM3e | 4.8 TB/s | ~206 FLOP/B | ~990 TFLOPS | 算力同 H100，显存/带宽更大 |
| B200* | 192 GB HBM3e | 8 TB/s | ~280 FLOP/B | ~2250 TFLOPS | 数字按厂商标称 |
| RTX 4090 | 24 GB GDDR6X | 1.01 TB/s | ~163 FLOP/B | ~165 TFLOPS | 消费级，带宽是它的天花板 |
| RTX 3090 | 24 GB GDDR6X | 0.94 TB/s | ~76 FLOP/B | ~71 TFLOPS (FP16 TC) | 老卡跑推理，带宽仍是关键 |

\* H200 / B200 为厂商标称值的量级参考，确切规格查官方 line card。

**脊点 = 稠密算力 ÷ 带宽**，含义见 `glossary.md` 的「算术强度 / 脊点」。

## 2. 模型权重显存 = 参数量 × 每参数字节

| 模型参数量 | FP32 (4 B) | FP16/BF16 (2 B) | INT8/FP8 (1 B) | INT4 (0.5 B) |
|---|---|---|---|---|
| 7B | 28 GB | **14 GB** | 7 GB | 3.5 GB |
| 8B | 32 GB | **16 GB** | 8 GB | 4 GB |
| 14B | 56 GB | 28 GB | 14 GB | 7 GB |
| 32B | 128 GB | 64 GB | 32 GB | 16 GB |
| 70B | 280 GB | **140 GB** | 70 GB | 35 GB |
| 405B | 1.6 TB | 810 GB | 405 GB | 202 GB |

注意：**这只是权重**。能跑起来还要加 KV cache（见 `glossary.md` 的 KV cache 公式），所以「80 GB 卡跑 70B INT4」实际会很紧。

## 3. 三个随时能用的公式

```
权重显存 (GB)        = 参数量 (B) × 每参数字节
decode 单请求上限    = 显存带宽 (B/s) ÷ 权重字节 (B)
算术强度 (FLOP/B)    = 2 × batch ÷ 每参数字节      # decode 阶段
脊点 (FLOP/B)        = 稠密算力 (FLOP/s) ÷ 带宽 (B/s)
KV cache 每token字节 = 2 × 层数 × KV头数 × head_dim × 精度字节
```

**用法**：算术强度 < 脊点 → 带宽瓶颈（快不了靠换算力）；> 脊点 → 算力瓶颈（该加大 batch 或减少计算）。

## 4. 常用换算

- 1 TB/s = 1000 GB/s = 1×10¹² B/s
- 1 TFLOPS = 1×10¹² FLOP/s；1 PFLOPS = 1000 TFLOPS
- 1 token ≈ 4 个英文字符 ≈ 0.75 个英文单词；中文约 1–2 字符 / token
- 7B 模型 FP16 单 token 计算量 ≈ 2 × 7×10⁹ ≈ 14 GFLOP（decode 阶段）
