# -*- coding: utf-8 -*-
"""Build the KV cache / concurrency budget workbook for lesson 2."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

OUT = r"D:\AI_infra\calculator\kv-cache-budget.xlsx"

NAVY = "1F3864"
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
OUT_FILL = PatternFill("solid", fgColor="EDF2F9")
HEAD_FILL = PatternFill("solid", fgColor=NAVY)
SUB_FILL = PatternFill("solid", fgColor="D6E0EF")
WARN_FILL = PatternFill("solid", fgColor="FCE4D6")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

wb = Workbook()

# ------------------------------------------------------- 显存预算
ws = wb.active
ws.title = "显存预算"
ws.sheet_view.showGridLines = False
for col, width in zip("ABCDE", [24, 14, 14, 20, 24]):
    ws.column_dimensions[col].width = width

ws["A1"] = "KV cache / 并发预算计算器"
ws["A1"].font = Font(bold=True, size=18, color=NAVY)
ws["A2"] = "只改黄色格子。核心：KV/token = 2 × 层数 × KV头数 × head_dim × 精度字节；并发 = 剩余显存 ÷ 单请求 KV"
ws["A2"].font = Font(size=10, italic=True, color="595959")
ws.row_dimensions[1].height = 26

def head_row(row, values):
    for j, v in enumerate(values, start=1):
        c = ws.cell(row=row, column=j, value=v)
        c.font = Font(bold=True, size=10, color="FFFFFF")
        c.fill = HEAD_FILL
        c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 20

ws["A4"] = "①  模型结构（去 Hugging Face 的 config.json 里抄）"
ws["A4"].font = Font(bold=True, size=12, color=NAVY)
head_row(5, ["参数", "值", "单位", "config.json 字段 / 说明"])

inputs = [
    (6, "模型名（备注用）", "Llama-3.1-8B", "", "随便写，只是标记"),
    (7, "层数", 32, "层", "num_hidden_layers"),
    (8, "KV 头数", 8, "个", "num_key_value_heads ← 不是 num_attention_heads！"),
    (9, "head_dim", 128, "维", "head_dim，或 hidden_size ÷ num_attention_heads"),
    (10, "KV 精度字节", 2, "字节", "FP16/BF16 = 2 ｜ KV 量化到 FP8/INT8 = 1"),
    (11, "权重参数量", 8, "B", "模型总参数量（十亿）"),
    (12, "权重每参数字节", 2, "字节", "FP16 = 2 ｜ INT8 = 1 ｜ INT4 = 0.5"),
    (13, "显存容量", 80, "GB", "H100/A100 = 80 ｜ 4090 = 24 ｜ H200 = 141"),
    (14, "显存带宽", 3350, "GB/s", "H100 = 3350 ｜ A100-80G = 2040 ｜ 4090 = 1008"),
    (15, "安全余量", 0.0, "%", "真实部署建议 10%；默认 0 是为了和课程算例对得上"),
]
for row, name, val, unit, note in inputs:
    ws.cell(row=row, column=1, value=name).font = Font(size=11)
    c = ws.cell(row=row, column=2, value=val)
    c.fill = INPUT_FILL
    c.font = Font(bold=True, size=12, color="7F6000")
    c.alignment = Alignment(horizontal="center")
    c.border = BOX
    if row == 15:
        c.number_format = "0%"
    ws.cell(row=row, column=3, value=unit).font = Font(size=10, color="595959")
    ws.cell(row=row, column=4, value=note).font = Font(size=9, color="595959")

ws["A17"] = "②  关键结果（自动算）"
ws["A17"].font = Font(bold=True, size=12, color=NAVY)
head_row(18, ["输出项", "结果", "单位", "含义"])
outputs = [
    (19, "KV cache / token", "=2*B7*B8*B9*B10", "字节", "单请求每存 1 个 token 要占的显存", "#,##0"),
    (20, "KV cache / token", "=B19/1024", "KiB", "换个单位好记（8B 约 128 KiB）", "0.0"),
    (21, "权重显存", "=B11*B12", "GB", "参数量 × 每参数字节", "0.0"),
    (22, "留给 KV 的显存", "=B13*(1-B15)-B21", "GB", "容量 ×(1−安全余量) − 权重", "0.0"),
    (23, "并发≥4 时最大上下文", "=B22*1000000000/(4*B19)", "token", "★ 想同时服务 4 个人，上下文最多能开多长", "#,##0"),
]
for row, name, formula, unit, note, fmt in outputs:
    ws.cell(row=row, column=1, value=name).font = Font(size=11, bold=(row == 23))
    c = ws.cell(row=row, column=2, value=formula)
    c.fill = OUT_FILL
    c.font = Font(bold=True, size=12, color=NAVY)
    c.number_format = fmt
    c.alignment = Alignment(horizontal="center")
    c.border = BOX
    ws.cell(row=row, column=3, value=unit).font = Font(size=10, color="595959")
    ws.cell(row=row, column=4, value=note).font = Font(size=9, color="595959")

ws["A25"] = "③  上下文扫描（改上面的输入，这张表全自动）"
ws["A25"].font = Font(bold=True, size=12, color=NAVY)
head_row(26, ["上下文 (token)", "KV / 请求 (GB)", "最多并发", "单请求 tok/s", "聚合吞吐 tok/s"])
contexts = [2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144]
for i, ctx in enumerate(contexts):
    r = 27 + i
    ws.cell(row=r, column=1, value=ctx).number_format = "#,##0"
    ws.cell(row=r, column=1).font = Font(size=11, bold=True)
    ws.cell(row=r, column=2, value=f"=A{r}*$B$19/1000000000").number_format = "0.00"
    ws.cell(row=r, column=3, value=f"=MAX(0,FLOOR($B$22/B{r},1))").number_format = "0"
    ws.cell(row=r, column=4, value=f"=IF(C{r}=0,\"放不下\",$B$14/($B$21+B{r}))").number_format = "0"
    ws.cell(row=r, column=5, value=f"=IF(C{r}=0,0,C{r}*$B$14/($B$21+C{r}*B{r}))").number_format = "#,##0"
    for j in range(1, 6):
        c = ws.cell(row=r, column=j)
        c.fill = OUT_FILL
        c.border = BOX
        c.alignment = Alignment(horizontal="center")
        if j > 1:
            c.font = Font(size=11, color=NAVY)

ws["A36"] = "④  读数（怎么用这张表）"
ws["A36"].font = Font(bold=True, size=12, color="FFFFFF")
for col in range(1, 6):
    ws.cell(row=36, column=col).fill = HEAD_FILL
tips = [
    "· 「最多并发」是硬上限：这是算术，不是调参能突破的。注意它随上下文长度成反比下降。",
    "· 「单请求 tok/s」随上下文变慢，因为每步除了权重还要把那几十 GB 的 KV 再读一遍。",
    "· 「聚合吞吐」随上下文变长而下降（8K 约 2 490 → 128K 约 149 tok/s）：KV 读取本身就是被迫的搬运，长上下文是三重收费。",
    "· 把 B10（KV 精度字节）从 2 改成 1，等于给 KV 预算翻倍：并发翻倍，代价是轻微质量损失。",
    "· 把 B9（head_dim）或 B8（KV 头数）改大，模拟「不用 GQA 的老模型」：看并发如何断崖式下跌。",
    "· 把「安全余量」从 0 调到 10%（真实部署建议值）：8K 的并发从 59 降到 52、32K 从 14 降到 13 —— 这就是工程上留的保守余量。",
]
for i, t in enumerate(tips):
    ws.cell(row=37 + i, column=1, value=t).font = Font(size=10, color="404040")

# ------------------------------------------------------- 公式与算例
w2 = wb.create_sheet("公式与算例")
w2.sheet_view.showGridLines = False
for col, width in zip("ABCDE", [26, 16, 16, 16, 16]):
    w2.column_dimensions[col].width = width

w2["A1"] = "KV cache 公式与已算好的算例"
w2["A1"].font = Font(bold=True, size=14, color=NAVY)

w2["A3"] = "公式"
w2["A3"].font = Font(bold=True, size=12, color=NAVY)
formulas = [
    "KV/token 字节      = 2 × 层数 × KV头数 × head_dim × 精度字节",
    "单请求 KV (GB)     = 上下文 × KV/token ÷ 10⁹",
    "最多并发           = (容量 − 权重) ÷ 单请求 KV",
    "单请求 tok/s       ≈ 带宽 ÷ (权重字节 + 单请求 KV字节)",
    "聚合吞吐 tok/s     = 并发 × 带宽 ÷ (权重字节 + 并发 × 单请求 KV字节)",
]
for i, f in enumerate(formulas):
    c = w2.cell(row=4 + i, column=1, value=f)
    c.font = Font(size=10, name="Consolas")

w2["A10"] = "常见模型（FP16）"
w2["A10"].font = Font(bold=True, size=12, color=NAVY)
head2 = ["模型", "层 / KV头 / head_dim", "KV / token", "8K 上下文", "32K 上下文"]
for j, h in enumerate(head2, start=1):
    c = w2.cell(row=11, column=j, value=h)
    c.font = Font(bold=True, size=10, color="FFFFFF")
    c.fill = HEAD_FILL
    c.alignment = Alignment(horizontal="center")
rows = [
    ("Qwen2.5-7B", "28 / 4 / 128", "56 KiB", "0.47 GB", "1.9 GB"),
    ("Llama-3.1-8B", "32 / 8 / 128", "128 KiB", "1.1 GB", "4.3 GB"),
    ("Llama-3.1-70B", "80 / 8 / 128", "320 KiB", "2.7 GB", "10.7 GB"),
    ("若无 GQA（32 头）", "32 / 32 / 128", "512 KiB", "4.3 GB", "17 GB"),
]
for i, row in enumerate(rows, start=12):
    for j, v in enumerate(row, start=1):
        c = w2.cell(row=i, column=j, value=v)
        c.font = Font(size=10, bold=(j == 1))
        c.border = BOX
        if j > 1:
            c.alignment = Alignment(horizontal="center")

w2["A18"] = "H100 80GB / Llama-3.1-8B FP16（权重 16 GB）"
w2["A18"].font = Font(bold=True, size=12, color=NAVY)
head3 = ["上下文", "单请求 KV", "最多并发", "单请求 tok/s", "聚合吞吐"]
for j, h in enumerate(head3, start=1):
    c = w2.cell(row=19, column=j, value=h)
    c.font = Font(bold=True, size=10, color="FFFFFF")
    c.fill = HEAD_FILL
    c.alignment = Alignment(horizontal="center")
rows2 = [
    ("8K", "1.07 GB", "59", "196", "约 2 490"),
    ("32K", "4.29 GB", "14", "165", "约 616"),
    ("128K", "17.2 GB", "3", "101", "约 149"),
]
for i, row in enumerate(rows2, start=20):
    for j, v in enumerate(row, start=1):
        c = w2.cell(row=i, column=j, value=v)
        c.font = Font(size=10, bold=(j == 1))
        c.border = BOX
        if j > 1:
            c.alignment = Alignment(horizontal="center")

w2["A25"] = "★ 一句话结论：上下文翻 4 倍，并发变 1/4，单请求还慢 16% —— 长上下文是三重收费。"
w2["A25"].font = Font(size=10, bold=True, color="7F6000")

# ------------------------------------------------------- 练习
w3 = wb.create_sheet("练习")
w3.sheet_view.showGridLines = False
for col, width in zip("ABCD", [8, 56, 20, 50]):
    w3.column_dimensions[col].width = width

w3["A1"] = "练习：先算，再看右边参考答案"
w3["A1"].font = Font(bold=True, size=14, color=NAVY)
for j, h in enumerate(["#", "题目", "你的答案", "参考答案 / 思路"], start=1):
    c = w3.cell(row=3, column=j, value=h)
    c.font = Font(bold=True, size=10, color="FFFFFF")
    c.fill = HEAD_FILL
    c.alignment = Alignment(horizontal="center")

ex = [
    ("1", "Llama-3.1-8B 开 128K 上下文，单个请求的 KV cache 占多少 GB？",
     "约 17.2 GB（131072 token × 128 KiB）"),
    ("2", "80 GB H100 上（权重 16 GB）跑上面那个 128K 请求，最多几个并发？",
     "3 个。(80−16) ÷ 17.2 ≈ 3.7 → 3"),
    ("3", "32K 上下文时，decode 每一步要搬多少 GB？单请求 tok/s 约多少？",
     "16 + 4.29 = 20.3 GB；3350 ÷ 20.3 ≈ 165 tok/s"),
    ("4", "Qwen2.5-7B（28 层、4 个 KV 头、head_dim 128、FP16）每 token 的 KV 是多少？",
     "2×28×4×128×2 = 57344 字节 = 56 KiB（比 Llama-3.1-8B 小一半多）"),
    ("5", "想用 8B 模型在 80 GB 卡上支持「16 并发 × 32K 上下文」，够吗？",
     "16 × 4.29 = 68.6 GB KV + 16 GB 权重 = 84.6 GB > 80 GB → 不够，差 4.6 GB"),
    ("6", "承上题：把 KV cache 量化到 FP8（每 token 字节减半）够了吗？还能更多吗？",
     "34.3 + 16 = 50.3 GB → 够了；剩余 (80−16)÷2.15 ≈ 29 个并发"),
]
for i, (num, q, a) in enumerate(ex, start=4):
    w3.cell(row=i, column=1, value=num).font = Font(size=11, bold=True, color=NAVY)
    w3.cell(row=i, column=1).alignment = Alignment(horizontal="center", vertical="top")
    cq = w3.cell(row=i, column=2, value=q)
    cq.font = Font(size=10)
    cq.alignment = Alignment(wrap_text=True, vertical="top")
    ca = w3.cell(row=i, column=3, value="")
    ca.fill = INPUT_FILL
    ca.border = BOX
    cr = w3.cell(row=i, column=4, value=a)
    cr.font = Font(size=9, color="595959")
    cr.alignment = Alignment(wrap_text=True, vertical="top")
    w3.row_dimensions[i].height = 40

w3["B12"] = "做完发我。尤其第 5、6 题——它们是真实采购/容量规划场景，你项目里一定会遇到。"
w3["B12"].font = Font(size=10, italic=True, color="7F6000")

wb.calculation.fullCalcOnLoad = True
wb.save(OUT)
print("saved:", OUT)
