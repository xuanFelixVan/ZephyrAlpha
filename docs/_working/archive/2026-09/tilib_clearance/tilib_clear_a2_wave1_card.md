---
ttl: task_bound
session: st-tilib-clear-20260920
title: 波1施工卡（M-L1/M-L2/M-L3 共15指标16列）
---

# 波1施工卡（总包→车道）

- 目标：+15 指标 / +16 列 / +约 70 测试；注册表 102→117，DDL 162→178，metas 101→116。
- L1（trend.py 硬车道）：MAMA+FAMA（列 mama/fama，fastlimit 0.5/slowlimit 0.05，Ehlers 口径）、FRAMA（frama_16）、JMA（jma_7, phase 50, power 2）。
- L2（statistics.py）：LINEARREG_ANGLE（linearreg_angle_14）/SLOPE（slope_14）/INTERCEPT（intercept_14）/STDERR（stderr_14），复用 _rolling_linefit；顺手修行1蓝图号 MOD-L02-001→MOD-L02-028。
- L3（trend.py 易车道，L1 落盘后开）：TEMA（tema_10）/TRIMA（trima_10）/T3（t3_10, a=0.7）/VIDYA（vidya_14, CMO9）/AVGPRICE（avgprice）/MEDPRICE（medprice）/TYPPRICE（typprice）/WCPRICE（wcprice）。
- 公式权威源：本地 talib 实测对照 + pandas-ta/TA-Lib 文档；禁凭记忆发明系数。
- 每指标测试 ≥4：注册/meta 契约、黄金样本（pytest.importorskip("talib")，200 bar 种子合成数据，warmup 后容差对照）、预热 NaN/首有效位、空表/缺列边界。
- 参数默认=pandas-ta 惯例（TEMA/TRIMA/T3=10，VIDYA=14，FRAMA=16，JMA=7）；MAMA 用 TA-Lib 默认限值。
- 车道只改自己两个文件（族文件+测试文件）；注册表/schema/契约常量/memo 由总包统一办。
- test_trend.py 计数断言：L1 落地后 24，L3 落地后 32；test_statistics 计数同步 +4。
- 验收：总包跑 tests/zephyr/factor/technical_indicators/ 全量绿（test_indicator_base 契约常量在总包侧同步后才生效）。
