# AI Infrastructure 学习工作区

> 目标：从「只会调 API 的 AI 应用工程师」变成「听得懂硬件语言、能自己算判据的人」。
> 完整动机与验收标准见 [MISSION.md](MISSION.md)。

## 课程

| # | 课程 | 内容 | 状态 |
|---|---|---|---|
| 1 | [一个除法，估出 tok/s 的天花板](lessons/0001-tokens-per-second-ceiling.md) | 算力/容量/带宽三件套、算术强度与脊点、decode 为什么是带宽瓶颈、量化与 batch 的算术解释 | ✅ 已通过（自测 5/5） |
| 2 | [KV cache —— 上下文越长越慢越贵](lessons/0002-kv-cache-context-cost.md) | KV 字节公式、从 config.json 读参数、并发上限、长上下文的三重代价、PagedAttention / GQA / prefix caching | 📖 当前 |
| 3 | prefill 与 TTFT | 另一堵墙：算力瓶颈侧、continuous batching 的代价 | 未开始 |

## 参考

- [术语表](reference/glossary.md)：和硬件人对话要用的词，全课程统一口径
- [GPU 关键数字速查](reference/gpu-numbers.md)：卡规格、权重显存表、三个随时能用的公式
- [KV cache 算术速查](reference/kv-cache-math.md)：KV 公式、怎么读 config.json、上下文三重代价表
- 计算器：[tok/s 天花板](calculator/gpu-throughput-calculator.xlsx) ｜ [KV / 并发预算](calculator/kv-cache-budget.xlsx)（只改黄色格子）

## 工作区文件

- [MISSION.md](MISSION.md)：为什么学、学成什么样
- [RESOURCES.md](RESOURCES.md)：可信来源（所有数字的出处）
- [NOTES.md](NOTES.md)：教学偏好与待办
- [learning-records/](learning-records/)：非显然的学习记录，决定下次教什么

## 每节课的用法

1. 先读课，**遮住答案自己做练习**（检索练习比读第二遍有用得多）
2. 打开计算器，把课程里的算例换成自己的模型 / 机器
3. 把结果或疑问丢给老师（就是我）——卡住的地方最有价值
