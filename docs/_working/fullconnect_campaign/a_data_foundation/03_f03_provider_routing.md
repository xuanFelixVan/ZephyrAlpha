---
ttl: task_bound
title: "F03 Provider 实现与源路由——46 文件×23 源策略路由复飞案卷"
session: zc-l01-20260927
---

# F03 Provider 实现与源路由（复飞案卷）

> 前序：M1 册 01_ingest.md §三 Provider 层表；本卷=十子包实扫独立复核（今日 46 py 实数）+壳包发现。

## 一、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游 | 外部 23 源 API 契约（akshare/tushare/东财/QMT 桥/币安 vision 等）+capability 声明（provider_base.py 基类） |
| 下游 | F01 调度器策略路由（scheduler 按 source 字段选 provider）；capability 三闸校验后放行 |
| 自动触发 | 被 DataScheduler 进程内调用（非独立常驻）；熔断经 policy_registry pause/resume |
| 真源注册表 | 实现=src/zephyr/data/implementations/（**46 py 实数**，含 __init__.py）；源策略=PolicyRegistry；源资产=data_sources_registry.yaml v2.6.0；能力画像=resource_profile_registry.yaml（29 slot 去重） |
| 门禁质量尺 | capability 三闸（validator/semantic/symbol）路由前拦截；speed-tester 测速选主备源 |
| 运行状态 | **绿**：akshare/akshare_alt/tushare/tqcenter/tdx/crypto 族/宏观另类 4 源均在产（census GREEN_WITH_DATA 主力承载）；miniqmt_provider.py 8000+ 行=清退残留（56 任务引用，#ARCH-351） |

## 二、子模块三级枚举（十子包×实现，本日实扫基准）

| 子包 | py 数 | 成员 | 判定 |
|---|---|---|---|
| implementations | 46 | akshare/akshare_alt/miniqmt/qmt_bridge/tushare/tqcenter/tdx/crypto 族 8/宏观 4（fred/eia/fx_ecb/qweather）/新闻族 5/internal_compute（18 能力项 :97-124）/tickflow/irm/板块资金 3/breadth/limit_up_pool/tick_depth_backfill/provider_base 等 | production 主承载 |
| redundant_source | 7 | source_switcher/sina_tencent_provider/backup_tick_poller/heartbeat_monitor/recovery/sqlite_fallback | 备援族（QMT 清退后 sina 快照接管先例=裁定#339） |
| calendar | 4 | base/ashare/crypto | production（交易日历） |
| normalizers | 4 | normalizer_base/ohlcv_normalizer/format_transformer | production |
| connectors | 3 | connector_base/file_connector | production（文件源） |
| wal_codec | 3 | codec_registry/tsv_codec | production（tick WAL 编码） |
| symbol_normalizer | 2 | normalizer.py | production（代码归一） |
| transport | 2 | cross_border_dual.py | production（跨境双通道） |
| satellite_geospatial_engine | 1 | 仅 __init__.py（头注 pending_review，CONSUMERS/TESTS 全空） | **登记态壳包**（零实件） |
| config | 0 py/6 yaml | tasks/schedule/data_supply_sentinel/known_data_gaps/policies/manual_calendar_events_schema | 真源配置面 |

对照账：M1 册记 implementations 45 → 本日实扫 **46**（+1，eastmoney/衍生 compute 族增量），骨架勘误④。

## 三、接线四态独立复核

- 总册：built/P2/D3。独立复核：**built 成立**（23 源全路由在产，census 数据面佐证）。
- 勘误⑤：总册 F03 真源列只写 implementations/，漏 redundant_source 7 件备援族与 symbol_normalizer/normalizers 归一路面——F03 语义=路由+归一+备援全层，册行锚点建议扩。
- 关联：姊妹定版卷 D-05 判 market_data（20 py）并入 F03/F10（双真源嫌疑消解）——本卷登记待裁，勿改总册。

## 四、缺口清单

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| P1 | miniqmt_provider 8000+ 行×56 任务清退残留 | 挂起+解锁=#ARCH-351 退役映射表落地后整文件退役（最大单体净删） | P1 |
| P2 | satellite_geospatial_engine 壳包（pending_review 空转） | Owner 门：立项实件化或退役登记 | P2 |
| P3 | capability 三闸仅运行时消费，登记时点无强制 | 施工：并入 F02 O1 向导校验 | P2 |
| P4 | 冗余面：speed-tester(29KB) 与 source_health_check(24KB) 同域重复 | 施工：合并探针宿主两档深度（内收判据） | P2 |

## 五、自审闸三态

挖干可施工（十子包实扫双源：ls+yaml 解析；P2/P4 可直开；P1 挂起；P2 壳包=Owner 门）。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
for d in implementations redundant_source calendar normalizers connectors wal_codec symbol_normalizer transport satellite_geospatial_engine config; do echo -n "$d: "; ls src/zephyr/data/$d/*.py 2>/dev/null | wc -l; done
grep -o "data_slot_[a-z_0-9]*" config/resource_profile_registry.yaml | sort -u | wc -l   # 29
head -15 src/zephyr/data/satellite_geospatial_engine/__init__.py   # 壳包 pending_review
wc -l src/zephyr/data/implementations/miniqmt_provider.py
```
