---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW4_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW4 考试与判据车道台账（st-nightsweep-sw4-20260929 | 总筹=st-nightsweep-chief-20260929）
# 生成：2026-09-29 夜战；会话保活守护 4h（heartbeat_sw4.py，PowerShell Start-Process 分离）
session: st-nightsweep-sw4-20260929
cold_start:
  python_312: "3.12.8 OK"
  lock_cleanup: "CLEAN"
  reaper_status: "alive (last_run 2026-09-29 03:47, killed=0)"
  session_registry: "registered + 4h keeper（bare register 的 pid 死亡会被判死——必须长命进程持有）"
  reaper_keep: "追加 t1_t2_handover 子串（CAS，after=e7e00c805fb7；pytest/factory_grid_executor 原已在册）"

cards:
  C1_t1_three_blockers:
    id: "D19/I2-56 T1 三阻断 + D20 T2 发车"
    verdict: "ADVANCED（2/3 阻断修复转绿；T2 按预注册 fail-closed 不发车）"
    evidence:
      fix: "2 阴格(d6759a48a594/4bdf3555a27d, kelly_050×halflife60×all_a 系)三证对拍定性=配方内生零方差阴性：executor A/B 双跑(grid_20260929-040003/040141)死因逐字段一致 + 直调引擎净值哈希一致(342432347427, sum_w=0 全 1622 日零仓位)"
      merged: "manifest 3698→3700(negative_note 标注)+negatives 清空+summary dead 2→0(repair 留痕)；哨兵复跑 5/6 判据绿(manifest3700/dead0/degraded0/negatives守恒/n_eff19)"
      still_red: "cost_gate_spot=30/50 破 40bp 存活地板(fresh replay, 非单调=0, 失败中位 -1.689)；归因=lambda_0 84%/top10 85%/drift_band 70%——高换手高集中簇结构性；修复前样本 28/50 同病→网格质量属性非修复引入"
      t2: "T2 未发车（VERDICT_RED→发车序列未进入=正确 fail-closed）；解锁路径=Owner 门位调整 survival_floor 判据（声明通道）或新搜索空间 T1"
      bonus_fix: "t1_t2_handover 发车命令 --subspace-json 传路径串而执行器按内联 JSON 解析=GREEN 后也必秒崩 LAUNCH_FAILED 循环——改传内联内容+测试断言同步（7 passed）"
      report: "docs/_working/night_sweep_20260929/sw4_t1_repair_pairing_report.md（token 已登记）"
    commits: "q-20260929-st-nightsweep-sw4-20260929-0001 (14 files, pending→传送带)"

  C2_w180_strict_read:
    id: "F46 W-180"
    verdict: "DONE-LANED"
    evidence:
      ported: "ch_writer 严格族(ClickHouseQueryError/parse_tsv_rows/_READ_ONLY_PREFIXES/last_transport/query_strict——复用既有传输层只换错误契约)+ch_reader(query_rows/count_strict/query_rows_table/inject_final_strict)+ch_probe(落 scripts/governance/data_supply/——卡面 scripts/data/* 系 .gitignore:604 无法入库,按 aidrafts 原位)+ch_read_shape_ruler(scripts/governance/wave1a/,尺为脚本原型自身不注册 gate——卡面 commit_gates 系猜测位,按其自带设计落位)"
      bugfix: "aidrafts 原件 _REPO_ROOT=parents[2] 深度病(指到 scripts/)：产物误落 scripts/.runtime、src 注入失效——修 parents[3]"
      tests: "27 passed(strict canary 14+ruler 10+probe 序列化 3, 全程 mock 传输)+真连 E2E(tcp count_strict/探针实测)+错列名必抛双链证据实测"
      ruler_state: "HEAD 树 132 候选文件零形状违约（P1/P2 病样本已不在 HEAD；尺能红由自带红样本测试证）"
      w102_family: "test_no_cache_and_cli_rc.py 依赖 no_cache_endorsement/check_wave3_rulers/strict_truth_reader 整族——超卡面四件范围，未连带移植（内收）"
      tokens: "probe/ruler 的 creation_token+翻译条目 aidrafts 批已入册（复用零新增）；翻译册存在 ch_read_shape_ruler 退化重复条目(61591 行 ch_read_shap)——--dedupe 通道在册未跑（共享热册 60k 行避免夜战并发写，留维护班）"
    commits: "q-20260929-st-nightsweep-sw4-20260929-0002 (7 files, pending)"

  C3_priority_collisions:
    id: "C36 红五簇"
    verdict: "DONE-LANED（实为六簇）"
    evidence:
      red: "新增全册唯一性机械校验测试（commit_gates 全 GateSpec 面 AST 扫描）证红=6 簇同号 70/79/80/82/92/113（卡面五簇系审计快照，+79 同病簇）；每簇=被吸收薄工厂(休眠)与在册 union 面同 priority——与 gate_registry.yaml 无关（该册无 priority 字段，卡面定位有误）"
      fix: "后到者让位先例：6 个 legacy 单门工厂迁 152-157 空带（族内相对序+docstring 区间约束保持，union 面保位零漂移）+6 模块头迁移注记+6 测试断言同步"
      green: "134 passed（含新唯一性测试转绿）+in_process 名册 104 台装载复核零撞号"
      out_of_scope: "ai_layer DROP-GATE(148) vs FACTORY-MAP(148) 跨域休眠对——册外不同病，登记不扩面交后续裁定"
    commits: "q-20260929-st-nightsweep-sw4-20260929-0003 (13 files, pending)"

  C4_archiver_false_green:
    id: "H32"
    verdict: "DONE-LANED"
    evidence:
      fix: "verify_partition_ex 三态(verified/sample_skipped/failed+reason+计数)：空分区/超大分区显式 skip 不再与全证据 verified 混同；矛盾态(行数>0 抽样 0)保持 09-28 fail-closed；布尔面保留 drop 门语义+docstring 两态声明；清单增 verify_status 字段（verified=false+sample_skipped 单列，缺省=1865 条存量形态兼容）"
      tests: "46 passed（新增 7 例：空样本 skip/正常 verified/样本不符 fail/矛盾态 fail/行数差 fail/清单穿线/缺省兼容）+rolling_archive_reconciler 回归 5 passed"
    commits: "q-20260929-st-nightsweep-sw4-20260929-0004 (2 files, pending)"

  C5_w178_board_census:
    id: "G30 W-178"
    verdict: "DONE-CROSSCHECK"
    evidence:
      existing: "wave11 案卷已完整落地（w178_sector_universe_strict.md + w178_universe_facts.yaml，57 读数双通道一致）：gap=134(601 名册口径−467)=8803:61+8804:71+8808:2；补齐=新增采集腿非数据修复（成分基表/快照表对 134 码零覆盖）；两套口径合并=案卷已标'只给事实不裁真源'+§E DRAFT_NOT_FROZEN 等 Owner 定案"
      fresh_recheck: "2026-09-29 重测逐数互证：sector_constituent 595 板/95124 行(880 段 467+881 段 128)、concept_board 375(akshare)、成分新鲜度 update_date max=09-03"
      increment: "tdx 行情真值口径互证：峰值日 880 段=599（名册 601 基准偏高 2），缺失=132(8803=61+8804=71) 与 known_data_gaps.yaml 既有条目 sector_constituent_8803_8804_missing 完全互证（源天然无，881 体系可替代）——经既有采集腿可补采=0，无需新增登记（条目已在册）"
      owner_gate: "两口径(concept_board akshare 375 vs sector_constituent tqcenter 595)合并/映射=OWNER-GATE 登记（案卷 §C 在册），本车道不裁"

  C6_t2_followup:
    id: "T2 后续+W-173 声明前置"
    verdict: "ADVANCED"
    evidence:
      t2: "T2 未发车（cost_gate RED）——run 目录=无新 T2 run；原 T1=grid_20260926-024947（修复后 5/6 绿）；恢复条件=Owner 裁定 survival_floor 或新 T1；发车入口修复后为 python scripts/backtest/t1_t2_handover.py --t1-run <run>（subspace 内联 bug 已修）"
      w173: "resonance_per_cell_seconds_target 键确认缺失于 config/search_space_prereg.yaml（grep 无命中）——声明通道准备：①需 GPU 队实测 per-cell seconds 后按裁定模板登记声明（禁直改 prereg）；②归 GPU 队 st-gpu-conv2 主责（总纲§二注），本车道仅登记键缺失事实"

conflicts_and_deviations:
  - "卡面'gate_registry.yaml priority 五簇同号'定位不成立：该册条目无 priority 字段；真身=commit_gates 代码面 6 簇（含 79 同病簇），已修"
  - "卡面'ch_probe.py → scripts/data/'不可落地：.gitignore:604 scripts/data/* 整目录忽略；按 aidrafts 原位落 scripts/governance/data_supply/"
  - "卡面'commit_gates 下扫描尺'：aidrafts 之尺为脚本原型（自带'不注册 gate'设计），按原设计落 scripts/governance/wave1a/，升 gate 另立项"
  - "卡面'5 簇'实为 6 簇（+blueprint_amodule 79），机械校验验收口径=全册唯一性故全修；DROP-GATE/FACTORY-MAP 148 对册外不扩面"
  - "W-102 no_cache_endorsement 测试族超 W-180 卡面范围未移植（依赖 3 模块族，内收）"
  - "SESSION-REQUIRED 实障：bare SessionRegistry.register 的 pid 进程退出即判死——必须长命 keeper 进程持有（heartbeat_sw4.py 4h，PowerShell Start-Process 分离式才不被 bash 退出连杀）；本会话直改主区已登记（夜战并发窗口，小面+claim+队列串行）"

queue:
  enqueued: ["q-20260929-st-nightsweep-sw4-20260929-0001(A,14)", "q-...-0002(B,7)", "q-...-0003(C,13)", "q-...-0004(D,2)"]
  status_at_write: "4 批 pending（队列总深 1167，daemon online，传送带自动消化）"
  claims: "全部涉及文件已 claim（含补 claim），落地由 gateway finally 释放；keep 文件系运行态未入库（git log 零历史=从未提交，非本车道遗漏）"
```
