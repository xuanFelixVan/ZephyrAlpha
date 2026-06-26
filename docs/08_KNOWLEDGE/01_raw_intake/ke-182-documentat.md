---
module_id: KE-164
title: 2.1 与业界对标原则的对应关系
category: documentation
ttl: permanent
---

# 2.1 与业界对标原则的对应关系

2.1 与业界对标原则的对应关系

| 本原则 | Bloomberg Terminal | Refinitiv Workspace | QuantConnect Cloud | IBKR TWS | Spotify Backstage |
|--------|-------------------|-------------------|-------------------|---------|------------------|
| FE-P1 异构 | ✅ C++ / Electron | ✅ Web Components | ✅ React SPA 独立 repo | ✅ Java Swing / Web Trader | ✅ 独立 TypeScript monorepo |
| FE-P2 Gateway | ✅ BQuant API | ✅ Elektron API | ✅ Lean API | ✅ TWS API | ✅ Backstage Backend |
| FE-P3 契约 | 🟡 Proprietary | ✅ OpenAPI-like | ✅ OpenAPI | 🟡 Proprietary | ✅ OpenAPI |
| FE-P4 MFE | ✅ Plug-in Model | ✅ Web Components | 🟡 Single SPA | N/A | ✅ Plug-in Architecture |
| FE-P5 DS | ✅ Bloomberg UI | ✅ Refinitiv Design | ✅ QC Design | ✅ TWS Design | ✅ Material UI 扩展 |
