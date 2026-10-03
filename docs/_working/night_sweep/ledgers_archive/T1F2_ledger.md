---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# T1F2_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# T1-F2 t0三版本裁定+小件包车道 · 夜战台账（sid=st-menu-t1f2-20260930）
# 总筹=st-nightsweep-chief-20260929 · 生成 2026-09-30 菜单执行夜
session: st-menu-t1f2-20260930
coldstart:
  path_python: "3.12.8 OK"
  setup_dev_env_check: "usercustomize installed (points to D:/ZephyrAlpha)"
  lock_files_cleanup: "CLEAN"
  reaper: "alive (last_run 2026-09-30 21:35:50, killed=2 reported=10)"
  session_registry: "registered pid=0 (逻辑 session)"
cards:
  - id: F2-1
    card: "t0 甲位三版本：对比表→五要素裁定→施工（Owner 批文①'对比表出来你自己裁定，然后直接施工执行'）"
    verdict: DONE-LANED
    disposition: "定版本=V2 唯一真源；V1/V3 deprecated+successor 注记；闸/配置指向统一；红蓝测试"
    evidence: >
      三版本实测（本班复测）：V1 主区 7316d34b0bd7/61,143B（无去重无 start 参数）｜V2 worktree
      LF 归一 e4dc2de62355/63,374B（双写去重+dominant 分歧 fail-closed+_SQL_SNAPSHOT_DOMINANT，
      ruff 双 PASS，tmp 副本逐字节互证）｜V3 blob 07cb0777c8e7（V2+7B 折行，ruff format FAIL，
      0033 袋已亡 blob 犹在）。决定性事实=拆批D(1b46889a9f,09-28)已把 V2 的判据与消费端落 HEAD
      而本体缺位→三处断裂实测：TestAutoMountDedupeRegression 3 failed（KeyError:'start'）/
      t0_six_phase_materialize:56 load_phase_panel(start=) TypeError / six_phase_history_v1.csv
      在库但其 meta.truth_source 生成代码版本不在库。裁定#460（取号遇竞态：预案 #455 已被
      W2-CARD 占号，实测 max=459 顺延 #460）；施工=V2 CAS 写回（before=V1 after=V2 进程外复核）
      +echo-guard acknowledged 2 条存量克隆对（Z-C1 前置①）+红转蓝 3 failed→14 passed、
      基线 81 passed 保持、ruff 双 PASS。事故处置：裁定册遭他会话旧基座覆写冲掉 7 条在册裁定
      （#429/#439/#440/#449/#450/#454/#455）→三向合并修复 275=270+5 纯增量（REGISTRY-MASS-
      DELETION 拦截正确，line-anchored 重建+yaml safe_load+对 HEAD 纯增量 diff 复核）。
      #ARCH-370 载体议题登记（PROTECTED-PATHS 正门标记，#ARCH-368/369 同款先例）。
      token 先行批=f32a46a8；主批=a80e121aff（git log -1 --name-only 核实恰 5 件零搭便车）。
      实盘暴露=0（GRADUATED_PACKAGES frozenset() 空，裁定#305 安全态；只动版本管理/指向/标记）。
      Z-C1 前置②（脏口径下游点名+重算）转 93 册排期尾项。worktree st-t0-matrix-20260924 死车道
      归档建议留 Wave 3 清理段。
  - id: F2-2
    card: "REAL-KEY 门改进：白名单纳入从真源派生断言的测试面（Owner 批文②）"
    verdict: DONE-LANED
    disposition: "derived_assertion_exempt 三重门+闸内放行标注派生源+红蓝五测"
    evidence: >
      derived_assertion_exempt 纯函数核=三重门（①测试文件 tests/ 或 test_*/ *_test.py 命名
      ②真源绑定 secret_registry/ai_secret_exposure/loader 引用 ③逐行派生形态=断言/比较+派生
      符号[re.IGNORECASE]），缺一照拦；闸内放行 audit action=allow+derived_from。
      红蓝：蓝=测试面派生断言放行+审计标注；红=无真源绑定照拦/有绑定裸字面量照拦/非测试面带
      注册表提及照拦/存量非测试硬编码引用照拦（test_real_key_reference_blocked 保持红）。
      tests/ai_layer/redline/ 全目录 110 passed+ruff 双 PASS。capability_lookup 补审计
      （redline→obj_s_redline/secret→bare_getenv_gate）。队列=q-20260930-st-menu-t1f2-20260930-0001。
      插曲披露：Edit 工具对目标文件两次超时→改 CAS 脚本通道；一次头部补丁越界覆盖 [TTL] 行与
      docstring 开行→即时修复 ast.parse 复核；heredoc 转义被环境二次处理两次→改 Write 落盘
      生成器通道。
  - id: F2-3
    card: "补-1 排期登记：限价单相位判据=拒单（保守）+判别器波3 前置"
    verdict: DONE-LANED
    disposition: "排期条目落 93 册（引用 Owner 批文②原文），不翻任何运行旗"
    evidence: "docs/_working/total_command_closeout/93_owner_menu.md §排期登记（2026-09-30 菜单执行夜）"
  - id: F2-4
    card: "补-2 排期登记：盘后退出码拆 0/4（牵 38 条冻结契约）→3 后窗"
    verdict: DONE-LANED
    disposition: "排期条目落 93 册（批拆+先出逐条受影响清单，冻结契约走声明通道）"
    evidence: "同上 93 册排期节（与补-1 同批 CAS 落册）"
  - id: F2-5
    card: "批复归档：本夜全部新批复汇总 99_owner_gate_menu.md 尾部已批复执行段"
    verdict: DONE-LANED
    disposition: "恢复件升级落位（SW17 汇编）+已批复执行段（B1/B2/B5/B6/c1/F2/门改进/补1补2 八项，每项引批文短语+执行车道）"
    evidence: >
      docs/_working/night_sweep/99_owner_gate_menu.md（token 先行，恢复件 14,917B+追加段 118 行）；
      归档纪律=批复映射+车道归属，他车道 verdict 不代报。事故处置：token 册被他车陈旧快照压掉
      2 条（R-063/Q-7 同型）→按工具处方增量补回（禁整片覆盖）；补回块首插位置错压列表闭合标记
      →双标记去重修复+yaml safe_load 12,407 tokens 复核。
queue:
  - q-20260930-st-menu-t1f2-20260930-0001 (F2-2 两件)
commits:
  - f32a46a8 (token 先行批)
  - a80e121aff (F2-1 主批 5 件)
handoff:
  - "st-t0-matrix-20260924 worktree 死车道归档建议→Wave 3 清理段"
  - "capability_canonical_file_registry.yaml 本班插入 token 1 条+修复 2 条，与 t1b1 持有窗并发——提交时以 CAS+三向合并防冲突"
```
