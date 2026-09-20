---
ttl: task_bound
completes_when: 判据式豁免谓词设计在册 + 真实面重估完成；施工（改 skip 常数族）须落 externalize/report 生成器且经再生成窗，本环节交判据不交手工白名单
title: W4 — 24 自指 fixture 判据式豁免（禁手工白名单，裁定#273）
owner: ZephyrAlpha-Owner
session: st-anchorfix-20260918
date: 2026-09-18
---

# W4 — 自指 fixture 判据式豁免

## 前提纠正（关键）

初判"scripts/ 5 文件 6 处 + tests/ 19 文件 22 处 = 24"。实测：`_iter_targets` 的
prune 集含 `tests/` → **tests/ 22 处根本不在扫描面**（不会真红）。ALGO_FLOW 自指
真实面 ≤ scripts/ 若干文件（解析器自引用 fixture）。24 的账面把已被 prune 的 tests/
误计，虚高。

## 豁免必须"判据式"非"清单式"（裁定#273：白名单=治理逃逸）

机械谓词（命中即豁免，无逐文件白名单）：
- **谓词A（自指 fixture）**：被报克隆块整体位于某字符串字面量内（fixture 样本正文，
  非真实两实现）——AST 定位克隆区间 ⊆ 单一 `Constant str` 节点即豁免；
- **谓词B（解析器自引用）**：宿主文件是 ALGO_FLOW 解析器/外化器本身，其内嵌示例
  天然"像"被它解析的目标——文件 ∈ {externalize_algo_flow.py, report_algo_flow_author_debt.py
  等 parser 家族} 且命中块在其测试性示例段。

## 落地位置（施工时）

- `externalize_algo_flow.py` 的 skip-常数族：新增上述机械谓词入口（读 AST 判定，非路径白名单）；
- `report_algo_flow_author_debt.py` 的分类：把"自指 fixture"归入豁免态、不计作者欠账。

## 现状

判据设计完成在册；施工=改 ALGO_FLOW 生成器族，须走再生成窗 + 双向钉（谓词命中/
不误伤真克隆各一）。在串行器活跃窗内不动生成器（同 W2 理由）。
