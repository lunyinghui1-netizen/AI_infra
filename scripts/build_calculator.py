# -*- coding: utf-8 -*-
"""Build the AI Infra GPU throughput calculator workbook."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = r"D:\AI_infra\calculator\gpu-throughput-calculator.xlsx"

NAVY = "1F3864"
BLUE = "2E5C8A"
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
OUT_FILL = PatternFill("solid", fgColor="EDF2F9")
HEAD_FILL = PatternFill("solid", fgColor=NAVY)
SUB_FILL = PatternFill("solid", fgColor="D6E0EF")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

wb = Workbook()

# ---------------------------------------------------------------- 计算器
ws = wb.active
ws.title = "计算器"
ws.sheet_view.showGridLines = False
ws.column_dimensions["A"].width = 26
ws.column_dimensions["B"].width = 14
ws.column_dimensions["C"].width = 16
ws.column_dimensions["D"].width = 62

ws["A1"] = "AI Infra 推理算力计算器"
ws["A1"].font = Font(bold=True, size=18, color=NAVY)
ws["A2"] = "只改黄色格子。核心公式：tok/s 上限 ≈ 显存带宽 ÷ 权重字节数（decode 阶段是带宽瓶颈）"
ws["A2"].font = Font(size=10, italic=True, color="595959")
ws.row_dimensions[1].height = 26

def section(row, text):
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(bold=True, size=12, color="FFFFFF")
    for col in range(1, 5):
        ws.cell(row=row, column=col).fill = HEAD_FILL
    ws.row_dimensions[row].height = 20

section(4, "①  输入（只改这一块）")
for col, head in zip(range(1, 5), ["参数", "值", "单位", "说明 / 常见取值"]):
    c = ws.cell(row=5, column=col, value=head)
    c.font = Font(bold=True, size=10, color=NAVY)
    c.fill = SUB_FILL
    c.alignment = Alignment(horizontal="center", vertical="center")

inputs = [
    (6, "模型参数量", 8, "B（十亿）", "Llama-3.1-8B → 8 ｜ Qwen2.5-7B → 7 ｜ 70B → 70"),
    (7, "每参数字节", 2, "字节/参数", "FP16/BF16 = 2 ｜ FP8/INT8 = 1 ｜ INT4 = 0.5 ｜ FP32 = 4"),
    (8, "显存带宽", 3350, "GB/s", "H100 = 3350 ｜ A100-80G = 2040 ｜ RTX 4090 = 1008 ｜ 3090 = 936"),
    (9, "峰值稠密算力", 990, "TFLOPS", "BF16/FP16 稠密值；厂商写 \"with sparsity\" 的标称要除以 2"),
    (10, "显存容量", 80, "GB", "H100 = 80 ｜ A100 = 80 ｜ H200 = 141 ｜ 4090 = 24"),
    (11, "batch / 并发", 1, "个请求", "同时处理的请求数。加大 batch 提吞吐、抬延迟"),
    (12, "单请求上下文长度", 8192, "token", "prompt + 已生成长度。长上下文主要吃 KV cache"),
    (13, "模型层数", 32, "层", "Llama-3.1-8B = 32 ｜ Qwen2.5-7B = 28"),
    (14, "KV head 数", 8, "个", "GQA 时远小于注意力头数；Llama-3.1-8B 的 KV 头 = 8"),
    (15, "head_dim", 128, "维", "8B 级别常见 128"),
    (16, "KV cache 精度字节", 2, "字节", "与权重同精度时填 2；KV 量化时填 1"),
]
for row, name, val, unit, note in inputs:
    ws.cell(row=row, column=1, value=name).font = Font(size=11)
    c = ws.cell(row=row, column=2, value=val)
    c.fill = INPUT_FILL
    c.font = Font(bold=True, size=12, color="7F6000")
    c.alignment = Alignment(horizontal="center")
    c.border = BOX
    ws.cell(row=row, column=3, value=unit).font = Font(size=10, color="595959")
    ws.cell(row=row, column=4, value=note).font = Font(size=9, color="595959")

section(18, "②  输出（自动计算，别手改）")
for col, head in zip(range(1, 5), ["输出项", "结果", "单位", "含义 / 怎么用"]):
    c = ws.cell(row=19, column=col, value=head)
    c.font = Font(bold=True, size=10, color=NAVY)
    c.fill = SUB_FILL
    c.alignment = Alignment(horizontal="center")

outputs = [
    (20, "权重显存", "=B6*B7", "GB", "= 参数量 × 每参数字节。只是权重，不含 KV cache", "0.0"),
    (21, "单 token 权重搬运时间", "=1000*B20/B8", "ms", "= 权重 GB ÷ 带宽。decode 每一步至少要这么多时间", "0.00"),
    (22, "单请求 tok/s 上限", "=B8/B20", "token/s", "★ 本课核心：这是物理天花板，任何框架都突破不了", "0.0"),
    (23, "算术强度（当前 batch）", "=2*B11/B7", "FLOP/byte", "decode 阶段 = 2×batch ÷ 每参数字节", "0.0"),
    (24, "脊点（本卡）", "=B9*1000/B8", "FLOP/byte", "= 稠密算力 ÷ 带宽。H100 约 295，A100 约 153", "0.0"),
    (25, "瓶颈判断", '=IF(B23>=B24,"算力瓶颈 compute-bound","带宽瓶颈 memory-bound")', "", "算术强度低于脊点 → 加算力没用，要么加带宽，要么降精度", "@"),
    (26, "聚合吞吐上限", "=IF(B23>=B24,B9*1000/(2*B6),B11*B22)", "token/s", "整机每秒产出。带宽瓶颈时 ≈ batch × 单请求上限（线性摊薄权重）", "0.0"),
    (27, "单请求实际 tok/s", "=B26/B11", "token/s", "每个用户感受到的速度。batch 越大，这个数越不涨（甚至跌）", "0.0"),
    (28, "算力利用率（decode）", "=2*B6*B11*B22/(B9*1000)", "%", "≈ MFU。decode 阶段通常是个位数百分比，属正常", "0.0%"),
    (29, "KV cache / token", "=2*B13*B14*B15*B16", "字节", "= 2 × 层数 × KV头数 × head_dim × 精度字节（Llama-3.1-8B ≈ 131072）", "#,##0"),
    (30, "KV cache 总占用", "=B11*B12*B29/1000000000", "GB", "= batch × 上下文 × 每 token 字节。长上下文 + 高并发的真正杀手", "0.0"),
    (31, "显存总需求", "=B20+B30", "GB", "权重 + KV cache。超过显存容量就是 OOM", "0.0"),
    (32, "显存是否够", '=IF(B31<=B10,"✅ 够（余 "&TEXT(B10-B31,"0.0")&" GB）","❌ 不够（差 "&TEXT(B31-B10,"0.0")&" GB）")', "", "不够时：降精度 / 减上下文 / 减并发 / 加卡", "@"),
    (33, "该上下文下最多并发", '=IF(B10-B20<=0,"权重就装不下",FLOOR((B10-B20)*1000000000/(B12*B29),1))', "个请求", "★ 回答「我这台机器能同时服务几个人」", "0"),
    (34, "显存利用率", "=B31/B10", "%", ">100% 直接 OOM；80% 以上基本没有安全余量", "0.0%"),
]
for row, name, formula, unit, note, fmt in outputs:
    ws.cell(row=row, column=1, value=name).font = Font(size=11, bold=(row in (22, 33)))
    c = ws.cell(row=row, column=2, value=formula)
    c.fill = OUT_FILL
    c.font = Font(bold=True, size=12, color=NAVY)
    c.number_format = fmt
    c.alignment = Alignment(horizontal="center")
    c.border = BOX
    ws.cell(row=row, column=3, value=unit).font = Font(size=10, color="595959")
    ws.cell(row=row, column=4, value=note).font = Font(size=9, color="595959")

ws["A36"] = "③  怎么用"
ws["A36"].font = Font(bold=True, size=12, color="FFFFFF")
for col in range(1, 5):
    ws.cell(row=36, column=col).fill = HEAD_FILL
tips = [
    "1. 先按自己手上的模型 / 卡改 6–16 行，看第 22 行（单请求天花板）和第 33 行（最多并发）。",
    "2. 把精度从 2 改成 1（INT8）：权重显存减半、tok/s 上限翻倍 —— 这就是「量化为什么快」。",
    "3. 把 batch 从 1 加到 64：第 26 行（聚合吞吐）涨、第 27 行（单请求）不涨 —— 这就是吞吐与延迟的对立。",
    "4. 把上下文从 8192 改成 32768：第 30 行（KV cache）暴涨、第 33 行（并发）暴跌 —— 下一课的主题。",
]
for i, t in enumerate(tips):
    ws.cell(row=37 + i, column=1, value=t).font = Font(size=10, color="404040")

# ---------------------------------------------------------------- 速查表
w2 = wb.create_sheet("速查表")
w2.sheet_view.showGridLines = False
for col, width in zip("ABCDEFG", [16, 14, 14, 14, 20, 30, 6]):
    w2.column_dimensions[col].width = width

w2["A1"] = "GPU 速查（规格以下单 / 官方 line card 为准）"
w2["A1"].font = Font(bold=True, size=14, color=NAVY)
gpu_head = ["GPU", "显存容量", "带宽", "脊点", "BF16/FP16 稠密", "备注"]
for j, h in enumerate(gpu_head, start=1):
    c = w2.cell(row=3, column=j, value=h)
    c.font = Font(bold=True, size=10, color="FFFFFF")
    c.fill = HEAD_FILL
    c.alignment = Alignment(horizontal="center")

gpus = [
    ("A100 40GB SXM", "40 GB", "1.55 TB/s", "≈200", "312 TFLOPS", "非 Tensor Core 仅 19.5 TFLOPS"),
    ("A100 80GB SXM", "80 GB", "2.04 TB/s", "≈153", "312 TFLOPS", "同算力、带宽更高"),
    ("H100 SXM", "80 GB", "3.35 TB/s", "≈295", "≈990 TFLOPS", "70B FP16 需 TP=2"),
    ("H200 SXM", "141 GB", "4.8 TB/s", "≈206", "≈990 TFLOPS", "厂商标称值"),
    ("B200", "192 GB", "8 TB/s", "≈280", "≈2250 TFLOPS", "厂商标称值"),
    ("RTX 4090", "24 GB", "1.01 TB/s", "≈163", "≈165 TFLOPS", "带宽是天花板"),
    ("RTX 3090", "24 GB", "0.94 TB/s", "≈76", "≈71 TFLOPS", "老卡，带宽仍关键"),
]
for i, row in enumerate(gpus, start=4):
    for j, v in enumerate(row, start=1):
        c = w2.cell(row=i, column=j, value=v)
        c.font = Font(size=10)
        c.border = BOX
        if j == 1:
            c.font = Font(size=10, bold=True)

w2["A13"] = "模型权重显存 = 参数量 × 每参数字节"
w2["A13"].font = Font(bold=True, size=12, color=NAVY)
w_head = ["参数量", "FP32 (4B)", "FP16 (2B)", "INT8 (1B)", "INT4 (0.5B)"]
for j, h in enumerate(w_head, start=1):
    c = w2.cell(row=15, column=j, value=h)
    c.font = Font(bold=True, size=10, color="FFFFFF")
    c.fill = HEAD_FILL
    c.alignment = Alignment(horizontal="center")
models = [(7, 28, 14, 7, 3.5), (8, 32, 16, 8, 4), (14, 56, 28, 14, 7),
          (32, 128, 64, 32, 16), (70, 280, 140, 70, 35), (405, 1620, 810, 405, 202)]
for i, row in enumerate(models, start=16):
    w2.cell(row=i, column=1, value=f"{row[0]}B").font = Font(size=10, bold=True)
    w2.cell(row=i, column=1).border = BOX
    for j, v in enumerate(row[1:], start=2):
        c = w2.cell(row=i, column=j, value=f"{v} GB" if v >= 1 else f"{v} GB")
        c.font = Font(size=10)
        c.border = BOX
        c.alignment = Alignment(horizontal="center")

w2["A24"] = "四个随时能用的公式"
w2["A24"].font = Font(bold=True, size=12, color=NAVY)
formulas = [
    "权重显存 (GB)         = 参数量 (B) × 每参数字节",
    "decode 单请求上限     = 显存带宽 (B/s) ÷ 权重字节 (B)",
    "算术强度 (FLOP/byte)  = 2 × batch ÷ 每参数字节",
    "脊点 (FLOP/byte)      = 稠密算力 (FLOP/s) ÷ 带宽 (B/s)",
    "KV cache 每 token 字节 = 2 × 层数 × KV头数 × head_dim × 精度字节",
]
for i, f in enumerate(formulas):
    c = w2.cell(row=25 + i, column=1, value=f)
    c.font = Font(size=10, name="Consolas")

# ---------------------------------------------------------------- 练习
w3 = wb.create_sheet("练习")
w3.sheet_view.showGridLines = False
for col, width in zip("ABCDE", [10, 52, 18, 46, 4]):
    w3.column_dimensions[col].width = width

w3["A1"] = "练习：先自己算，再看参考答案（答案在右侧，用手或纸挡住）"
w3["A1"].font = Font(bold=True, size=14, color=NAVY)

ex_head = ["#", "题目", "你的答案", "参考答案 / 思路"]
for j, h in enumerate(ex_head, start=1):
    c = w3.cell(row=3, column=j, value=h)
    c.font = Font(bold=True, size=10, color="FFFFFF")
    c.fill = HEAD_FILL
    c.alignment = Alignment(horizontal="center")

exercises = [
    ("1", "70B 模型用 FP16 跑在 2 张 H100 上（TP=2），单请求 tok/s 上限约多少？",
     "约 48 tok/s。每卡只搬 70 GB：3350 ÷ 70 ≈ 48"),
    ("2", "8B 模型用 INT4 跑在 RTX 4090（1.01 TB/s）上，权重占多少 GB？理论上限多少 tok/s？",
     "权重 4 GB；1008 ÷ 4 ≈ 252 tok/s（真机达不到，KV cache 读取会吃掉一部分）"),
    ("3", "Llama-3.1-8B（32 层、8 个 KV 头、head_dim 128、FP16）在 32K 上下文下，KV cache 每 token 多少字节？单请求占多少 GB？",
     "每 token = 2×32×8×128×2 = 131072 B ≈ 0.13 MB；32K 上下文 ≈ 4.3 GB"),
    ("4", "同一模型，80 GB H100，上下文 32K，权重 16 GB：最多能同时服务几个请求？",
     "(80−16) ÷ 4.3 ≈ 14.9 → 最多 14 个并发。算完就明白「长上下文吃并发」"),
    ("5", "某服务商宣传：8B 模型单张 H100、单请求 800 tok/s。可能吗？为什么？",
     "不可能。物理上限 = 3350 ÷ 16 ≈ 209 tok/s。除非换了更小/更精度的模型，或那是含缓存的「平均」"),
    ("6", "把 batch 从 1 加到 64，第 26/27 行会怎么变？用自己的话解释一次。",
     "聚合吞吐涨到约 64×209（受算力墙限制），单请求延迟基本不变或略差 —— 权重搬一次服务 64 个请求"),
]
for i, (num, q, a) in enumerate(exercises, start=4):
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
    w3.row_dimensions[i].height = 46

w3["B12"] = "做完把答案发我，或者直接在计算器里代入验证。做错比做对更有价值 —— 告诉我你错在哪，我改下一步的教学。"
w3["B12"].font = Font(size=10, italic=True, color="7F6000")

wb.calculation.fullCalcOnLoad = True  # 打开时强制重算，保证可见数值
wb.save(OUT)
print("saved:", OUT)
