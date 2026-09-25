---
ttl: task_bound
session: st-ailayer-fullflow-sc
creation_token: m5sc-supplement-overview-20260925
---

# M5 补挖波 2026-09-25 总览（组 SC 接续）

> **一句话**：M5 主波（49 计划任务+13 常驻族）已挖干；本波接分工册 SC 行五项补挖——FBL（F84）、启动链（F85）、备份冷储、性能水位、F82 order_daemon 接线取证——全部六向台账+自审闸三态闭合，零 commit 零主区写入。
> 挖矿会话 st-ailayer-fullflow-sc；实测基线 2026-09-25（进程/任务/盘面均为当日活探）。

## 一、补挖册清单与三态汇总

| 册 | 对应环节 | 一句话结论 | 自审闸三态 |
|----|---------|-----------|-----------|
| [01_fbl_feedback_loop.md](01_fbl_feedback_loop.md) | F84 | FLE 340 模块巨族；五段闭环 tick() 全仓零生产调用（trae_053 废轮询后事件沿未施工）＝回路零触发；裁定驱动提案回路 4 个月仅 1 件 | 挖干可施工（附 1 待裁：触发沿形态） |
| [02_boot_chain.md](02_boot_chain.md) | F85 | 五层启动形态齐备：Windows 服务建成未部署（sc query 1060+零入口）、桌面壳 .lnk 在册本次未活、LogOn 任务群绿、CLI/冷启动三步常态、AI wrapper PT1M 注入活 | 挖干可施工 |
| [03_backup_coldstore.md](03_backup_coldstore.md) | D 组共担项（备份冷储 3-2-1） | 六 STAGE 流水线+G 兜底镜像在轨（今晨快照 20260925 实证）；恢复演练双件 10-01 才首跑＝"可恢复性"未实证；state log_verified=False 待核 | 挖干可施工 |
| [04_perf_watermark.md](04_perf_watermark.md) | F79 水位面+F80 画像+F81 阈值 | 三层水位闸（进程 10GB 收割/系统 YAML 规则/注册表 SSoT 49 条）全链在轨当日绿（RAM 69.8%/commit 77.6%，breached=[]）；总册计数漂移 2 处回填 | 挖干可施工 |
| [05_order_daemon_wiring.md](05_order_daemon_wiring.md) | F82（P0 断链点） | 六断点取证闭合：零生产 emit→journal 零实例→守护零 spawn→sink dry-run→下游挂接预留→回执线设计态；policy/DDL/maturity 三件已备 | 挖干可施工（附 1 待裁：守护拉起形态） |

**三态计**：挖干可施工 5 / 待挖 0 / 待裁 0（两册各附 1 个内嵌待裁点，不降册级三态）。

## 二、跨册发现（回填义务）

1. **总册口径漂移 2 处**：F81"38 条阈值"→实测 49（v1.4~v1.6 增补未回写）；F80"96 实体"→registry `total_entities: 98`（09-24 再生）。按分工册 §三.5 回填总册。
2. **F84/F82 同 root cause**：宪法 §9.3"事件触发"在两处都是**声明态**——FLE 的 tick 事件沿、L5 的胜者 emit 沿都缺第一根线。建议总筹把"事件沿接线"立为跨车道工单族。
3. **tmp 住客病第三例**：FBL audit trail 住 `.runtime/tmp/feedback_audit_trail`（空目录）——与 04 册 S2 tilib 同族（依赖可清区），已入 01 册堵点。
4. **CAS 残留 2 件**：`docs/01_.../_registry/catalogs/` 下 `alert_threshold_registry.yaml.tmp.21732.*`、`infrastructure_registry.yaml.tmp.45444.*`（09-22，safe_write 中断残骸）——卫生工单（他区，只登记不动手）。

## 三、矿脉增补（分工册未列）

- `config/evolution_schedule_seeds.yaml`×`ai_layer/scheduling/seed_writer.py`：F84 进化与 F82 排产的交叉轴——排班登记=写种子→生成器再生；生成器新源 I7 缺口已在 seed_writer 头注在册（"另行单派施工"）。
- `scripts/backup/backup_reconciler.py` INV-11 假绿闸（09-24 新装）：CH 段 ok 落账前须过 `system.backup_log` 交叉核验——备份链可信度的机械闸，供 D 组引用。
