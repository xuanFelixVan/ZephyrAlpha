---
ttl: task_bound
session: st-collintake-20260920
topic: collection_intake_20260920
---

# Gemini / Nano Banana Pro 图解配方——工具笔记 2026-09-20

> 判定 D（存档工具笔记）：报告/晨报配图场景可用，接入须走 LSG。

## 名称与事实核实 `[外部]`

- "Nano Banana Pro" = **Gemini 3 Pro Image**（Google 2025-11-20 发布的旗舰图像生成/编辑模型的市场名）；API 正式可用：Gemini API / Google AI Studio 专页（文本+图像输入，1K/2K/4K 输出）；Vertex AI 以 `gemini-3-pro-image` 提供。
- 来源：https://aistudio.google.com/models/nano-banana 、Vertex 官方文档。

## 配方（源自幻方帖作者实操 `[亲验-帖内]`）

1. 输入=**原文全文 + 手绘 prompt**（不是丢 PDF 截图，是贴文字+手绘布局指令）。
2. **坑（必踩）**：默认绿涨红跌（美股口径）——prompt 必须显式指定 **A股口径：红涨绿跌**。原帖作者首轮直出即翻车后修正。

## 项目内合规与挂点

- **所有 LLM 调用必经 LSGSecurityGateway**（`zephyr.security.llm_defense.llm_security.gateway`，裸调被 GATE-20+运行时拦截器双捕）`[亲验]`——若项目内使用，先在 LSG 注册该模型/端点。
- 场景：晨报/战报配图、因子卡片图解（如幻方十因子卡）、前端静态素材。
- 不立项：当前报告体系无配图刚需，按需启用。
