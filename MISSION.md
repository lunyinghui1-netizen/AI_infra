# Mission: AI Infrastructure —— 从「调 API 的应用工程师」到「听得懂硬件语言的人」

## Why

你已经在做 AI 应用（RAG / Agent / 微调），也跑过 Ollama、vLLM 这类本地推理，但硬件对你还是一个黑箱。你想学的不是调 kernel，而是在面试、评审、跨团队会议上，听到「80G 卡」「3.35 TB/s」「KV cache 爆了」「上 TP=8」这些话时，**能自己用算术判断它是否合理，而不是只记住名词**。

这门课的立场：硬件不是靠背，是靠算。你已经会的软件概念（token、上下文、并发、批处理）就是最好的落脚点——每节课都从你熟悉的东西出发，把硬件语言翻译过去，然后让你亲手算一个数。

## Success looks like

- 听到「这张卡 80 GB 显存、3.35 TB/s 带宽」，能当场估出某个 N B 模型单请求的理论 tok/s 上限，并说出这个数为什么是天花板而不是玄学
- 在评审里听到一个吞吐/延迟声称，能判断它是否越过了物理上限：「这个 tok/s 合理」「这个 batch 下不可能这么快」「这是算力瓶颈不是带宽瓶颈」
- 面对自己的 Agent / RAG 工作流，能用显存算术回答「长上下文 + 高并发的 KV cache 要多少 GB，需要几张什么卡」
- 能正确使用并解释这些黑话：显存容量 vs 显存带宽、FLOPs 与 Tensor Core、算术强度 / roofline、KV cache、prefill 与 decode、TTFT 与 TPOT、batch 与 continuous batching、TP / PP / EP、NVLink vs PCIe、量化、MFU
- 有一个可复用的判据挂在脑子里：任何「优化 / 加速」的说法，都能归到**少搬数据 / 多并行 / 降精度**三者之一

## Constraints

- **没有硬件背景**，不需要从晶体管、电路、制程讲起；但也不接受「反正就是这么设计的」这种答案
- 已有软件侧基础：Python、调 API、RAG / Agent、微调、跑过 Ollama / LM Studio / vLLM，理解 token、上下文窗口、批处理的概念
- 每节 **20–30 分钟**，必须含动手算例或小实验
- 交付物只要 **Markdown + Excel**，不要 PPT
- 以「黑话能不能用对」为通过标准，不以覆盖多少知识点为标准

## Out of scope

- CUDA kernel 编写、Triton、算子级性能调优
- 芯片设计、制程、封装、SerDes / 电路细节
- 大规模训练集群运维（IB 网络调优、故障恢复、集群调度）
- 云厂商报价谈判与采购流程
