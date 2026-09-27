---
ttl: task_bound
title: "Owner 门位登记台账（宪法 §5 high 域，只登记不代裁）"
session: zc-chief-20260927
---

# Owner 门位登记（99_skipped_for_owner）

> Owner 令"不留待裁"与宪法 §5 冲突，依裁-03 全部登记跳过。本台账随战役推进追加。

| # | 事项 | 来源 | 状态 |
|---|---|---|---|
| 1 | DDL：kline_weekly_hfq/kline_monthly_hfq 补 lineage_version | M3 §8.1 | 登记跳过 |
| 2 | 空壳表 9 张建腿 vs 退役（含 l2_tick） | M3 §8.2 | 登记跳过 |
| 3 | 真源收敛三处（recon/consensus/news_sentiment_score） | M3 §8.3 | 登记跳过 |
| 4 | Ollama 11434 恢复（重启提案封矿） | M3 C12 | 登记跳过 |
| 5 | heartbeat 计划任务兜底 | M4 C6 | 登记跳过 |
| 6 | 门禁 diff 化批门位确认+恒绿贵门处置窗 | M4 C3/C5/C9 | 登记跳过 |
| 7 | dead 系 2397 件归档净删 | M4 §11.4 | 登记跳过 |
| 8 | M2 候选 A 见证层并案出厂（含候选 C） | M2 §10.1 | 登记跳过（Q 线只做 W17 补填与预检封旁路的代码准备，出厂 flag 归 Owner） |
| 9 | requires-sync"宁停勿吃"适用交互正门 | M2 §10.2 | 登记跳过 |
| 10 | --base-head 契约二选一 | M2 §10.3 | 登记跳过（代码按"补 base_blobs"准备，flag 默认不启用） |
| 11 | [GW:] 归属去文本化 | M2 §10.4 | 登记跳过 |
| 12 | gate_registry 174≠180 归位+自洽台双锚 | M2 §10.5 | 登记跳过 |
| 13 | single-writer 检测器提为 reconciler | M2 §10.6 | 登记跳过 |
| 14 | commit_queue_interactive 出厂翻转 | M1 O-1 | 登记跳过 |
| 15 | 预检原则改册净零声明 | M1 O-2 | 登记跳过（随施工批呈） |
| 16 | 热册三向合并策略变更 | M1 O-3 | 登记跳过 |
| 17 | M5 三件：四停用定性/三悬空方向/43 红样排期 | M5 §8 | 登记跳过（43 红样采集若日班带宽许可由矿道卷登记） |
| 18 | 挖矿新发现门位项 | W1 产出 | 待追加 |
| 19 | etf_benchmark 数据源_stub 重写：`akshare_provider._fetch_etf_benchmark` 现为恒空 yield（rows=[] 永远 0 行=SUCCESS 假绿），且实调 `index_stock_info(symbol="000300")` 与 tasks.yaml 声明 `fund_etf_fund_info_em` 不符；修复须实弹验证 akshare 通道后选定真源接口重写（date_col: publish_date 已修，P3） | P 线 census :106 | 登记跳过（禁实弹） |
| 20 | realtime_snapshot 换源决策+suspend 双源反爬持续性观察：112 个降级件（08-26~09-21）全数 realtime_snapshot_incremental，错误=`Can not decode value starting with character '<'`（新浪 stock_zh_a_spot 反爬返 HTML；原东财源因 #ARCH-AKSHARE-ANTICRAWLER-001 IP 封锁弃用）——换源三候选（东财冷却复用/腾讯源/qmt_bridge）选定与验证须实弹；suspend 三腿 census 时点 0 行=东财 stop_em+百度双源反爬暂态（09-27 复测 36 行 max=09-23），持续观察归哨兵（P4 修后尺不再被骗） | P 线只读诊断（lane_p_notes.md §P5） | 登记跳过（禁实弹） |

（追加规则：矿道/施工线报来"涉生产流转/净删/flag/资金"项一律入此表并回填 91_progress。）
