# Obsidian 同步说明

> 记录本文件夹与 Obsidian 的关联方式。**本文件本身也是被关联的**，在这里改就能在 Obsidian 里看到。

## 一句话

`D:\AI_infra` 通过一个 **NTFS 目录联接（junction）** 出现在 Obsidian 仓库里，两边是**同一份文件**，不是副本。

```
D:\TFC_konwleage\TFC_RAG_Knowleage\AI_infra   ==>   D:\AI_infra
   Obsidian 里看到的文件夹路径                        真实文件所在处
   仓库：TFC_RAG_Knowleage（当前打开的）              本工作区
```

## 建立方式（已执行，留存备查）

```cmd
cmd /c mklink /J "D:\TFC_konwleage\TFC_RAG_Knowleage\AI_infra" "D:\AI_infra"
```

需要写仓库所在目录，普通权限即可；`/J` 是联接，不需要管理员、不需要开发者模式。

## 已验证的事实

| 检查项 | 结果 |
|---|---|
| 联接类型 / 目标 | `Junction` / `D:\AI_infra` |
| Obsidian 索引到的笔记 | 8 个 md 全部索引（含正文） |
| 新建文件后多久被 Obsidian 看到 | 实测约 5–8 秒 |
| 是否需要后台进程 / 计划任务 / 插件 | 都不需要 |
| 重启后是否有效 | 有效（联接是磁盘上的元数据，持久） |

因此行为等价于：

- 在 `D:\AI_infra` 里改 md → Obsidian 里几乎立刻看到新内容；
- 在 Obsidian 里改 md → 磁盘上 `D:\AI_infra` 里就是改过的内容。

## 使用注意

1. **不要从 Obsidian 的文件列表里删除/重命名 `AI_infra` 这个文件夹**。要整理内容，直接在 `D:\AI_infra` 里操作。
2. 风险点：如果某个工具顺着这个联接做"递归删除"，会删到 `D:\AI_infra` 里的真实文件。撤销配置只删链接，见下。
3. Obsidian 只把 `.md` 当笔记；`calculator\*.xlsx`、`scripts\*.py`、`assets\` 会以附件/文件形式出现，属正常。
4. README 里的相对链接（如 `lessons/0001-tokens-per-second-ceiling.md`）在 Obsidian 里可正常跳转。
5. 只在仓库 `TFC_RAG_Knowleage` 里生效。外层仓库 `D:\TFC_konwleage` 打开时看不到本文件夹；需要的话再补一个同样的联接。
6. 万一 Obsidian 界面里没看到这个文件夹（极少见），重启一次 Obsidian 强制重新扫描即可。

## 撤销（只删链接，不动任何文件）

```cmd
cmd /c rmdir "D:\TFC_konwleage\TFC_RAG_Knowleage\AI_infra"
```

⚠️ 不要用带 `-Recurse` / `/S` 的删除命令指向该联接路径 —— 那种情形下可能顺着链接把 `D:\AI_infra` 的真实文件一起删掉。
