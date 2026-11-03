# AI Infrastructure Resources

每一节课的知识都必须能追溯到这里的一个来源。**不要凭记忆讲硬件规格**——所有数字都去翻下面这些一手资料。

## Knowledge

- [Article: "Transformer Inference Arithmetic" — kipply](https://kipp.ly/transformer-inference-arithmetic/)
  从第一原理推导 LLM 推理的延迟、KV cache 容量、roofline 与 batch 的关系，全部是「纸上算术 + 实测对账」。**本课程的核心教材**。Use for: 任何 tok/s、KV cache、显存容量的算例与公式来源。
- [Article: "Making Deep Learning go Brrrr From First Principles" — Horace He](https://horace.io/brrr_intro.html)
  把 GPU 时间拆成「计算 / 带宽 / 开销」三块，讲清楚 memory-bound 是什么意思。Use for: 建立「为什么慢」的三分类直觉，以及 A100 的 312 TFLOPS vs 19.5 TFLOPS（非 Tensor Core）这类规格陷阱。
- [Blog: "Mastering LLM Techniques: Inference Optimization" — NVIDIA](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/)
  官方口径的 prefill / decode、KV cache 公式、TP / PP、量化与 in-flight batching。Use for: 引用官方术语定义与 KV cache 字节公式。
- [Blog: "NVIDIA Hopper Architecture In-Depth" — NVIDIA](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/)
  H100 官方规格与架构（80 GB HBM3、约 3 TB/s 级带宽、SM / Tensor Core / L2 / NVLink 900 GB/s）。Use for: 一手硬件规格，避免用二手博客的错数字。
- [PDF: NVIDIA Data Center GPU Line Card](https://docs.nvidia.com/data-center-gpu/line-card.pdf)
  各代数据中心卡的容量 / 带宽 / 算力速查表。Use for: 查具体型号规格，比官网产品页好翻。
- [Paper: "Efficient Memory Management for LLM Serving with PagedAttention" (vLLM, SOSP'23)](https://arxiv.org/abs/2309.06180)
  KV cache 为什么会碎片化、分页管理为什么能让吞吐涨 2–4×。Use for: 解释「显存不够用」的真实原因不只是容量小。
- [Paper: "Roofline: An Insightful Visual Performance Model" — Williams, Waterman, Patterson (CACM 2009)](https://dl.acm.org/doi/10.1145/1498765.1498785)
  roofline 模型的原始出处（算术强度 vs 峰值算力/带宽）。Use for: 讲「脊点」时引一手来源。
- [Blog: "Which GPU(s) to Get for Deep Learning" — Tim Dettmers](https://timdettmers.com/2023/01/30/which-gpu-for-deep-learning/)
  用带宽和显存而不是「算力数字」来选卡的长文，含实测。Use for: 选型话题，以及反「只看 TFLOPS」的思维。

## Wisdom (Communities)

- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
  真实用户的 tok/s 实测、量化效果、单机 / 多卡踩坑。Use for: 验证理论值与实测差多少，问「我这配置能跑多大模型」。
- [vLLM GitHub Discussions](https://github.com/vllm-project/vllm/discussions)
  推理引擎的实际吞吐 / 显存问题，作者和高频用户都在。Use for: 把「为什么我的 vLLM 吞吐上不去」拿去问真人和搜历史。
- [NVIDIA Developer Forums](https://forums.developer.nvidia.com/)
  规格、驱动、多卡通信的官方答疑区。Use for: 规格歧义、NVLink / PCIe 拓扑类问题。
- [MLPerf Inference 结果](https://mlcommons.org/benchmarks/inference-datacenter/)
  业界公认的推理基准，厂商提交的成绩。Use for: 判断某张卡「业界最好能跑到多少」，校准自己算的理论值。

## Gaps

- 缺一份**中文**、可信、系统的 AI infra 入门材料（现有中文内容多为二手复述，规格常错）→ 这也是本课程存在的理由，课件本身要成为可复用材料。
- 缺公开可信的**云实例性价比**对比数据（各家价格变动快，且 spot / 包年差异大）→ 等学到成本那课时再定向搜索。
- 缺本地 GPU 实测环境信息：尚不知道你自己机器上是什么卡（影响「在自己机器上验证」类练习的设计）→ 见 NOTES.md，下次先问。
