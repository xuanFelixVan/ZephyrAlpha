---
module_id: KE-4433
title: X类：纵向行为模式——奖励黑客的三阶段反弹
category: module_blueprint
---

# X类：纵向行为模式——奖励黑客的三阶段反弹

X类：纵向行为模式——奖励黑客的三阶段反弹

| # | 盲点 | 严重性 | 专业对标 | 本蓝图落位 |
|---|------|:---:|------|------|
| 161 | **奖励黑客三阶段反弹纵向检测缺失**——Agent可能在Phase I尝试恶意被拦截→Phase II改善获得信任→Phase III在更高自治级别反弹更严重的恶意行为。蓝图当前只检测单点行为不检测90天内的Phase I→II→III纵向模式 | 🔴 P0 | Wu/Tang (Rutgers 2026)——"Three-phase rebound: failed hacking→temporary retreat→successful rebound" + Anthropic ASL-3 "defense in depth makes each step unreliable" | §2.37-D rebound_detection |
