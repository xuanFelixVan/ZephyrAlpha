---
ttl: task_bound
completes_when: 09-17 tick 全市场回补验收通过+五档界定结论登记（随 data_fix_campaign 归档）
session: st-data-fix-20260921
issue: DATAFIX-P0-0917-TICK-RECOVERY
---

# 分包0 交付报告：09-17 tick 全市场找回 + 五档界定（2026-09-21 夜班）

> 会话 st-data-fix-20260921（重派 incarnation）；CH 重写入车道占用于 01:45-（协调板 ACTIVE）；
> 数据源=模拟盘 QMT 客户端（E:\国金QMT交易端模拟，sim env，`config/qmt_environments.yaml`），
> Owner 挂机只读下载，全程未触其进程。evidence 等级标注：[亲验]=本会话实测；[转报]=总包/他包转述；[推断]=分析结论。

## 一、红证→绿证（主表 c1_market.tick_data）

| 时点 | 09-17 行数 | 依据 |
|---|---|---|
| 09-20 22:00（总包红证基线） | 0 | [转报] 总包实测 |
| 09-20 22:15-23:19（本包前 incarnation） | +18,334,896 | done 4900+49err，status.json [亲验] |
| 09-21 01:45（本 incarnation 接手时） | 18,579,875 | CH count() [亲验] |
| 09-21 02:20（本 incarnation 补齐后） | **28,327,322** | CH count() [亲验] |

本 incarnation 增量：宇宙从「沪深A股主单 4,903」扩到「09-16 存量反推全宇宙 8,073」，本轮 +3,176 标的 / +9,734,718 行 / 0 新错。

**验收命令**（reader 角色经 DatabaseService）：

```sql
SELECT countIf(trade_date='2026-09-17') FROM c1_market.tick_data;   -- 28,327,322（≥2000 万门槛，超邻日 09-16 的 23,908,666）
```

## 二、分市场覆盖率结构（09-17 vs 09-16，[亲验]）

| market_type | 09-17 | 09-16 | 备注 |
|---|---|---|---|
| stock | 20,383,626 | 20,491,380 | 沪深主板/创业板/科创板，覆盖 99.5% |
| etf | 3,938,980 | 1,722,639 | 模拟盘源比 09-16 桥存量覆盖更广 |
| index | 2,743,946 | 1,079,237 | 沪深指数（000xxx.SH/399xxx.SZ）全量可下 |
| stock_bj | 562,679 | 256,999 | 京市 920xxx 实测可下（920855=2365 行） |
| cb | 531,007 | 242,719 | 转债部分可下（见 §四） |
| lof | 167,084 | 67,233 | — |
| futures | 0 | 48,459 | **域外**：p0 宇宙不含期货（另一管线，非本批范围） |
| 合计标的 | 7,799 | 7,977 | — |

**缺口长尾（180 只，如实列）**：09-16 有行而 09-17 无行 = cb 5 / etf 12 / stock 40 / lof 86 / stock_bj 33 / futures 4（域外）。
全部在宇宙内被处理过、返回 0 行（判模拟源无此标的：退市/停牌/模拟环境未收录）。样本：110815、123112、127033、159047、160137（LOF 集中缺——16 开头 LOF 大多为源缺）、002731 等。
未逐一核验停牌牌表（后续如需可对 kline_daily 09-17 停牌标记交叉核验）[推断]。

**同键重复**：ReplacingMergeTree 未合并前 09-17 有 20,427 组同键多版本（resume 重灌所致，同键同值幂等，合并后收敛）[亲验]。

## 三、过程坑记录（复用价值）

1. **前 incarnation 已跑完主宇宙**（22:15-23:19）：接手时红证已非 0，先核 CH 现状再动手，避免重灌整表。done 断点文件（`.runtime/tmp/st-data-fix-20260921/p0/done_20260917.txt`）幂等 resume 有效。
2. **49 标的 CH write failed**（23:05 乙线 CH 重启余波）：未记 done，resume 自动重灌，pilot 3 只实测 12,729 行 0 错后全量通过。
3. **模拟盘 `get_stock_list_in_sector` 板块残缺**：京市A股/沪深转债/沪深指数/沪深基金几乎返回空（各 0-2 只），前 incarnation 宇宙因此只有沪深A股。**修正：宇宙改从 `tick_data 09-16 DISTINCT (symbol, market_type)` 反推 QMT 码单**（8,073 只；注意 SH 转债裸码 11xxxx 在存量被 `infer_market_type` 判为 stock，需按裸码前缀特判）。清单=`.runtime/tmp/st-data-fix-20260921/p0/universe_0916_derived.txt`。
4. **8073 只超命令行长度**：p0 脚本补 `--symbols-file` 参数（本批代码改动，见 §六）。
5. **队列 prestage 与 .gitignore 通配冲突**：`scripts/data/*` 通配误伤 tracked 常驻件 p0_tick_backfill.py，commit_queue prestage 拒绝快照（q-0015/q-0016 两次 dead 同因）。精确豁免 .gitignore=受保护路径（ARCH-MODEL-LIFECYCLE-001，Owner 门位，无 CLI 逃生旗）→ **本批未硬闯**，脚本改动留暂存区，停手项见 §六。

## 四、五档（tick_depth_5）界定结论

- **可下性 [亲验]**：dry-run 实测 5 类代表标的 09-17 全部可下——000001.SZ=4,847 / 510300.SH=5,134 / 000300.SH=5,449 / 127045.SZ(转债)=4,012 / 920002.BJ(京市)=2,168，19 列含完整五档。
- **全市场回补 [亲验]**：按 `backfill_tick_depth5.py` 配方（计算层 `tick_depth_backfill.fetch_symbol_day_depth`）自建断点驱动（`.runtime/tmp/st-data-fix-20260921/depth5_driver.py`，分片 ≤4000 行/write，ReplacingMergeTree 同键幂等），对同一 8,073 宇宙执行完毕。
- **验收数字**：`SELECT count() FROM c1_market.tick_depth_5 WHERE trade_date='2026-09-17'` = **28,819,429 行 / 7,844 标的**（对照 09-16 = 12,205,343 行，覆盖 2.4 倍）；结构：stock 20,259,229 / etf 4,028,005 / index 2,751,389 / cb 1,206,801 / stock_bj 574,005。
- **过程坑**：驱动进程 03:2x 遭杀（七杀实测），done 断点幂等 resume 重启续跑至完成（5850→8073，两进程合计 0 错）。
- **界定**：五档 09-17 缺口=已全市场回补，类别覆盖与 tick 主表一致（部分 cb/LOF/BJ 长尾源缺）。
- **口径注**：depth5 计算层用 `MiniQmtIngestProvider.detect_market_type`、tick 主表用 `tick_subscriber.infer_market_type`，两分类器对 LOF/ETF 边缘标的标签有差（depth5 分组无 lof 行，系标签并入他类）——两表同键各管各表无冲突，属既有口径现实，登记备查。

## 五、已知残余与不在本批范围

- futures 09-17（4 标的 48,459 行当量）：域外管线，未处理。
- 180 只源缺长尾：未逐一核验停牌/退市牌表。
- tick_depth_5 驱动为会话级运维件（.runtime/tmp），已完成退出（exit 0）；如未来需重跑（如别日缺口），done 断点幂等 resume，命令在驱动文件头。

## 六、代码改动与提交状态

- `scripts/data/p0_tick_backfill.py`：+`--symbols-file`（宇宙文件传入）；表名改走 `TableRegistry.table("market_tick")` 派生（#ARCH-CH-024，过 TABLE-NAME-REGISTRY gate）。**未落地**：被 commit_queue prestage 以 .gitignore 通配拒（q-0015/q-0016 dead 留痕；豁免 .gitignore=Owner 门位）。改动在主区暂存区，Owner 批豁免（加一行 `!scripts/data/p0_tick_backfill.py`）后 `commit_queue.py requeue` 即可落地；或按 dead_reason 处方①移出 scripts/data/（需同步 3 个生成器注册表+depgraph，不推荐今晚做）。
- depth5 驱动为会话级运维件（.runtime/tmp），如需转正另行按 CREATE-GUARD 走收编。
