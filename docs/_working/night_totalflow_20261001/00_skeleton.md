---
ttl: task_bound
---

# 00 骨架总册——夜战全流通施工（night_totalflow_20261001）

总包：st-storageswap-20260930 ｜ Owner 睡眠令：全线挖矿建档→挖干即施工→并行流水→红蓝对抗→双轮零→端到端交付。注：本文件夹首版曾遭工作树清扫蒸发，此为重建版（内容全息压缩版；M1/M2/M3 代理全文存档=C:\Users\fanzi\.zcode\cli\agents\sess_483a3e80-*\agent_*/output.txt）。

## 六线终态一览

| 线 | 内容 | 终态 |
|---|---|---|
| L-A 收敛线 | 板块分钟线双真源并一 | ✅ 裁定甲落地：internal_eqw（scripts/kline_sector_intraday_from_constituents.py，五周期727板，真值保护+回补清场，Windows任务 sector_eqw_intraday@15:40 实注册）为唯一生产者；J 腿 runner 转 --dry-run 留观（S12 不注销）；tdx 五任务标注退役留观；resample 判死（kline_sector_880 全表仅 1d）随 Owner 门位批退役 |
| L-B TI 线 | TI 分钟级停产（1m/5m 停 09-21，15/30m 停 09-23） | ⚖️ 回填 HOLD：直驱脚本已建+两轮校准实证计算核 09-19 后语义漂移（macd 日界冷值 0 vs 基线连续值）；漂移期数据不混史；校准污染已清（FINAL 40 键复原）；结构性修复卡（语义考古+per-period 拆分+运行保障+缺口感知锚）归 Owner 门位批；daily 自愈✓、分钟级 10-12 起新语义产出 |
| L-C cffex 线 | 写端诞生即坏（83ddfdf4f5d 剥 symbol 列） | ✅ 一行修入袋 q-0006（*row 恢复 15 字段）；0921-0930 历史已抢救；次日 18:06 死信归零=终验 |
| L-D 元数据线 | valid_from DEFAULT toDate(list_date) 撞 NULL | ✅ 全库普查四表（cb/etf/index/stock_list）DDL ifNull 治本+Memory 引擎语义实测+回滚键在案（D_mine.md） |
| L-E 队列线 | 落地 Popen(timeout=) TypeError 杀袋 | ✅ 根因=process_pool.py run_subprocess_hidden（G2 队 S4-F 引入），G2 队已修 staged（+33/-2）勿动；q-0004 死因另含 WinError 233 管道环境失败（重投类）；全场 index.lock 僵尸（03:28 挂死 git diff 双进程+0字节锁 2.5h）已清 |
| L-F T5 线 | capability 册哈希折入 | 👁 他队 G2 在途编辑中（折入机制=validate_rules_integrity.py --fold+rules_integrity_db.json，DB 哈希停 09-30 21:56 未折）；CEF_mine.md 处方备；10-02 死线盯 |

## 链路面终态

1. tick 链 ✅（0929=2842万行满/0930=2984万/auction 5572）
2. 板块分钟链 ✅ 收敛完成（0930=171,351行/711板 J 补；10-09 起 internal_eqw 产；3 交易日验收 10-09 起）
3. cffex 链 ✅ 历史+写端双修
4. 元数据清单链 ✅ DDL 治本
5. TI 派生链 ⚖️ daily 自愈/分钟 HOLD+结构性卡
6. 队列落地链 ✅ 僵尸锁清+G2 修 staged

## 交付单

见 99_delivery.md（红蓝 R1-R8 结果+循环检查+遗留=Owner 门位批清单）。
