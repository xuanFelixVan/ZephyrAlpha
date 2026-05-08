---
module_id: KE-documentat-7_5_3____cold_path-000
title: 7.5.3 前端 Cold Path 场景
category: documentation
---

# 7.5.3 前端 Cold Path 场景

7.5.3 前端 Cold Path 场景

| 场景 | 触发 | 执行路径 |
|------|------|---------|
| **批量报表导出（PDF / Excel / 周报）** | `risk-dashboard` 点击 "导出周报" | 前端发 POST `/api/v1/reports/generate` → L08 接收 → 转发 L12 批处理 → SSR 服务渲染（1-300s）→ 生成完成后 WebSocket 通知前端下载链接 |
| **策略回测历史回放** | `research-ide` 启动回测 | 前端仅发任务 ID，**不等待结果**；回测 Cold Path 运行时长可达分钟-小时级；完成后通过 Feishu/Email/WebSocket 异步通知 |
| **AI 训练任务触发**（G4 G5 激活后）| `ai-cockpit` 提交模型训练 | 前端仅启动任务 + 轮询状态；训练在 L11 ml_platform Cold Path（小时-天级） |
