---
ttl: task_bound
title: "业务链流通施工战役宪章（总筹 st-chief5-20260927）"
session: st-chief5-20260927
completes_when: "本线全部车道收官+红蓝两轮零+全袋落地+终报后归档"
---

# 业务链流通施工战役宪章（00_orchestration）

> Owner 令（2026-09-27 睡前，本会话受理）：从股权穿透地图起，推进到线路接入所有模块、
> 全链打通、全管线灌水、全部可运行；挖干才施工、内收原则、线内先挖后干线间并行流水；
> 红蓝对抗至连续两轮零；全袋经 GitCommitGateway；无法裁定=登记+跳过。
> **碰撞协议声明**：今夜 `docs/_working/fullconnect_campaign/00_orchestration.md`（st-fms-chief-20260927）
> 持有挖矿 W1（L00-L12 十三矿道）与基建施工 G/L/P/Q 四线。本战役按波 13 车道防撞协议
> **不重挖、不重叠**，只认领其未覆盖的业务链施工面。他会在飞件不代修不覆盖。

## 一、领地声明（本役独占，他线勿入）

| 车道 | 内容 | 子会话 | 状态 |
|---|---|---|---|
| EC1 股权穿透接线 | 前端/API 从 ig_equity_edge(804 条)切换 entity_graph 六表(150 万边)；wo_equity_penetration_v1 工单点火（技术栈口径校准为 PG 底座）；三家样本 3 跳穿透验收；R1-R7 验收闭链 | st-ec1-equity | 在飞 |
| EC2 P0 断链处置 | S0 七断链现态复核（F26 E7前哨/F74 转正汇总器/F34 知识汇聚/F20 G事件/F62 合规门/F82 order_daemon/F04 清洗接线，09-26 后或已部分修复）+可修即修+Owner 门位登记 | st-ec2-p0 | 在飞 |
| EC3 灌水运行体检 | m5_scheduling/05_master_health_table.md 22 行全行重探+红行代码级修复+关键表数据新鲜度实证（只读查库） | st-ec3-water | 在飞 |
| EC4 回灌边+二波 | E9→E2/E6→E1 回灌边+EC1-EC3 收尾后视 CPU 余量派发 | 总筹 | 待 |

## 二、纪律（全车道生效）

1. 提交唯一正门=`scripts/git_commit.py --session <sid> --files <清单>`；重试带 `--adopt-prior-work`；
   落地后 `git log -1 --name-only` 核归属。
2. 改前 claim（`python scripts/lock_files.py acquire <file> <sid>`），毕后 release；发现文件被他会话
   claim=登记+跳过，不硬闯。
3. 新文件必须 token 先行或同袋（`scripts/governance/d3_metadata/batch_creation_tokens.py`）；
   新 .py 模块必须登记翻译（`find scripts -name "add_module_translation.py"`）。
4. 热注册表写入必经 safe_write_text（expected_base_sha256=CAS）；写后验读回。
5. 测试隔离：输出一律 tmp_path；只读查 CH/PG 允许，禁实弹写生产表；禁 kill belt/reaper；
   禁触碰 .runtime 根。
6. Owner 门位事项（资金/净删/production 流转/flag 出厂翻转）一律登记 `99_skipped_for_owner.md`
   （本目录）+跳过，不代裁。
7. 会话活性：本役各子会话首次 git_commit 时自动注册；长间隙由总筹心跳兜底
   （st-chief5 心跳 daemon 300s 在岗）。

## 三、验收口径（Owner 醒后可见）

1. EC1：前端股权徽章/公司卡实读六表现行版本；两公司 3 跳穿透冒烟留证；R1-R7 逐项销账。
2. EC2：七断链逐项三态销账（已修/本役修/登记跳过+原因），证据=命令输出。
3. EC3：健康表 22 行逐行现态+处置，关键管线灌水证据（行数/最新时间戳）。
4. 循环检查连续两轮零+红蓝对抗记录；全袋 landed 哈希台账 `91_progress.md`（本目录）。
5. 终报=终态四清单：已打通/已修复/登记跳过/下一步排序，零含糊。
