---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW11_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW11 治理杂项车道台账
# SW11 治理杂项打包车道台账（sid=st-nightsweep-sw11-20260929，总筹=st-nightsweep-chief-20260929）
# 生成：2026-09-29 夜战；verdict 纪律=铁律7（id/verdict/evidence）
session: st-nightsweep-sw11-20260929
cards:
  - id: W-56 悬空裁定号清理
    verdict: DONE-VERIFIED-ZERO
    evidence: >-
      ruling_registry 245 条/max#428；全树 grep 裁定#N 引用 247 个号，悬空 13：
      9=测试桩号（777/778/888/901/999/1001/9001/9002/9999，tests/ 内合法假号）；
      #2=architecture_issue_registry L8464/8480 "本裁定#2 战略项"（ARCH 裁定项内编号，非注册表引用）；
      #4/#5/#24=archive design_memos 内部"待裁定"编号（归档区禁改）；
      #34'=d_dead_letter_lineage reason_head 80 字符截断伪影（原为裁定#34x）。
      确凿悬空=0 → 零修正零补登记（卡令：只处理确凿悬空者）。
      附观察：主区 ruling_registry 有他会话 staged 的 #419 去重件（删 #419 留 #420，无 claim，未触碰）。

  - id: N-3 files_trigger 超宽收窄
    verdict: DONE-LANED(q-20260929-st-nightsweep-sw11-20260929-0001 入队待落地)
    evidence: >-
      消费端真语义=commit_gate_registry._files_trigger_hit 四路 OR；18670 tracked 文件实测：
      ≥1354 触发面门 16 台。逐台读实现后收窄 5 门（内滤证据）：ASYNCIO .py→src/zephyr/*.py
      （_is_src_zephyr_file，8856→3753）；MAP-ALIGNMENT→镜像 _TRIGGER_PATTERNS 十条（4843→4798）；
      META-TESTS-COVERAGE tests/→src/zephyr/gov_enforcement/commit_gates/（门内真触发条件，3875→124）；
      RECONCILER-FILE-OPS governance→镜像 _SCAN_PREFIXES 四前缀（2430→1272，顺补 scripts/backup/ 漏触发）；
      BLOOD-FLESH .py→src/zephyr/*.py+scripts/*.py+翻译册（_is_in_scope 同口径，8856→4830）。
      净回收 13,783。机械校验：5 门×3 正例全保+3 负例全灭 ALL-PASS；registrar _validate_files_trigger 全过；
      files_trigger 回归 21+门引用 76=97 测试绿；total_gates=104 不变。
      留置 11 门理由（读实现定位职责面即宽，收窄=行为变更）：.py 族 5 门（FUNCTION-DUP/FILE-COPY/
      COMPLEXITY-GUARD/GATE-DOMAIN-FK/UNSAFE-DICT-SPREAD 职责=非测试 .py 全仓，include-only 语义无法表达
      tests 排除）；R5-DIGIT-SUFFIX（全路径命名规则，现触发面已窄于职责）；STATE-VOCAB-REGISTRY（全仓 .py 职责）；
      REFERENCE-INTEGRITY（触发面窄于门域，反向问题）；DEPGRAPH-FRESHNESS（src/+scripts/=代码域职责）；
      RECONCILER-HEALTH（INVARIANTS 明示 always-on 项目态检查，收窄=语义变更）。
      注：入队时 capability_lookup 反查已补（CAPABILITY-LOOKUP gate 拦截后合规补做）。

  - id: audit_fix_ledger §11-13 入册
    verdict: DONE-VERIFIED-ABSENT
    evidence: >-
      三查皆空：盘面 audit_fix_ledger.md 仅 §1-§10（与 HEAD 节数一致，唯一盘面差异=他会话加的
      frontmatter created: 一行，非本卡面）；docs/_working/audit_fix/ 与 audit_all/ 全目录无 §11/§12/§13；
      git log -S "## 11." 与 -S "§11" 全历史零命中=§11-13 从未存在。无可入册项。
      audit_all 三文件的 created: 一行属他会话在途，登记让路。

  - id: 96_final_report_wave2 §七回填
    verdict: DONE-LANED(搭 q-0001 同袋，消息归因瑕疵披露)
    evidence: >-
      §七由待写桩回填为实录：队列正门 4 袋 qid↔landed（0002→5081f0ca91e/0004→9d71b563bd9/
      0014→ec0dd4f43a0/0022→3ae33e7ffed，done/ 实录含落地时刻）；死袋 4（0001 DIRECTORY-CONTRACT/
      0016 ENCODING-SAFETY/0019 CREATE-GUARD/0021 ALGO-NOTE-SYNC）；直连 30505c93f6c＋他队代投
      8f03ef44bf7/6a4124cd8fd（git log --all 全史核）；0003/0005-0013/0015/0017-0018/0020 未见于
      done|dead 与全史=直连或记录已清，标注诚实缺口不虚补。循环检查/临时清理两项留原会话口径。
      披露：队列 C1 同会话短窗把本件与 N-3 合批进 q-0001，袋消息=N-3 的（msg_q7 被合批吞），
      文件内容自带 provenance，落地后归属以此台账补记。

  - id: miniQMT 文案修正 4 件
    verdict: DONE-LANED(2bd67c05)
    evidence: >-
      按裁定#339 口径改 4 文件纯文案：miniqmt_channel_manager.py:59 "全面清退"→"实盘退役；模拟盘
      供数继续"；ch_tick_replay.py:19 "退役后断供"→"实盘退役（模拟盘供数继续；原生 provider 取数
      路径停用）"；br-page.js:54→"实盘已退役（模拟盘供数继续）"；bridge.html:26 同口径。
      随批修复两处拦路历史带病件（同触面合法同批）：ch_tick_replay.py 补 [ALGO_FLOW] external 锚
      （docstring 内，ast.get_docstring 面）+外置真源 docs/03_modules/_domain_backtest/algo_flow/
      ch_tick_replay.yaml（creation_token 已登记 capability_canonical_file_registry 纯插入 1 条）；
      miniqmt_channel_manager.py:231 run_channel_call 裸 Any→TypeVar _T 透传（注解级零运行时）。
      验证：py_compile×2+node --check+ruff 过+消费测试 21+16 绿。队列无 multi-domain 通道且 C1 合批
      有跨域落地死信风险→按 §2.4 正门 git_commit.py 直连 --allow-multi-domain 留痕（一条 commit message
      三域披露）。commit=2bd67c05c98dcd92fb223044986acb23a2363ec8（worktree 分支，待 merge train 归 dev）。

  - id: 备份三小件 H04/H06/H08
    verdict: DONE-LANED(2ad4f15d)
    evidence: >-
      H04 backup.ps1：增 Copy-FileShareTolerant（FileStream 句柄复制，dst 全新流不遗传只读位，
      src FileShare.ReadWrite）替换 vault 两处 File.Copy；事故形态=只读位源遗传致 mtime 对齐写回炸
      →error_sample 失败。测试 tests/dr/test_backup_copy_share.py：正则抽函数体守卫+同进程红绿对拍
      （旧路只读位必炸/新路绿+只读位不遗传+字节一致）+mtime 逐刻一致。
      H06 restore_drill.py：演练库 collate 保真治本——读活库 datcollate/datctype/encoding→
      template0+显式 locale 建库（根因=旧 CREATE DATABASE 继承 template1 Chinese_PRC vs 活库 C，
      C3 头段零交集）；回落 C/C/UTF8 入 report[drill_db_locale_source]（schema 只增）；
      _PK_ORDER COLLATE "C" 钉保留双保险；测试+3。
      H08 process_reaper.py：keep 免死名单改身份段匹配（程序基名/python -m 紧随位/脚本基名，
      "git commit -m \"pytest docs\"" 参数文本不再误免死，7 用例矩阵过）+<子串>|session=<sid>
      标记行+--keep-cleanup（只清死会话标记行，裸行永不自动删，safe_write_text CAS）；
      keep.txt 本会话错误行（pytest/t1_t2/factory_grid 合并单行）改 3 行带标记正确条目（只动自留行）。
      全量 104+75 测试绿，ruff 净。commit=2ad4f15d（worktree 分支，待 merge train 归 dev）。

  - id: I6:I34 178 陌生 blueprint 甄别
    verdict: DONE-VERIFIED-PREMISE-ABSENT
    evidence: >-
      四路核数全不匹配"178 新增"：docs/03_modules tracked blueprint=553（长期存量）；
      git --diff-filter=A 近两周=11、09-26 后=0；untracked blueprint=0（untracked 45 件全是
      index.md/algo_flow yaml=他会话 P2-1 出仓在途）；deleted blueprint=0。
      无样本可抽、无误写可隔离→物理删除 OWNER-GATE 无对象。主区 docs/03_modules 320 M/A/D 批次
      =他会话在途（M 样本为实content 编辑+algo_flow 出仓新建），登记让路不代修。

  - id: 补-12 flags 轮转评估
    verdict: OWNER-GATE(评估已交，执行待 Owner 停窗令)
    evidence: >-
      实测：.runtime/audit/feature_flags.jsonl=1,768,620,851 字节（1.77GB）/6,313,346 记录，
      最后写入 2026-09-29 07:13（活）。写方唯一=flags.py:310 global_flag_registry(persist_audit=True)：
      逐记录 open("a")→write→close，无常驻句柄；尾部突发=进程启动全目册重登记（每次 gateway/
      消费方 import 重注册数十条）。读方=无独立消费代码（全仓仅 flags.py 自身与 gateway 引用）。
      轮转方案（推荐 A）：A=静止刻 rename feature_flags.jsonl→feature_flags.jsonl.rotated-<ts>，
      下一次 append 自动重建新文件；因无常驻句柄，Windows rename 冲突窗=毫秒级，撞上即该条审计
      写失败→flags.py:246 fail-open warning（设计内不阻断），重试即可——严格说无需停写窗；
      B=代码化 _record_audit 阈值轮转（>512MB os.replace），需代码落地窗。
      归档去向（G:/backup 镜像 or 本地留存 TTL）与执行时点=Owner 门位。
      未执行（卡令：停窗才能动=OWNER-GATE），本条即登记。
owner_gate_list:
  - id: flags 轮转执行
    reason: 1.77GB 审计文件 rename/清理涉及审计留存政策与执行窗（卡令明示 OWNER-GATE；虽评估显示
      无常驻句柄使技术风险低，留存政策归 Owner）
    proposal: A 方案 rename+自动重建；归档建议 G:/backup 或 .rotated 前缀本地留 90 天
  - id: 蓝图物理删除（I6:I34 若 Owner 持 178 清单他源）
    reason: 本车道四路核数未复现该集合；若 Owner 侧另有 178 清单出处，请提供源文件后按卡令甄别
pending_landing:
  - q-20260929-st-nightsweep-sw11-20260929-0001（N-3 收窄+§七回填 2 文件，pending 队列第 ~27 位，
    serializer 活跃在处理，非死袋）
merge_pending:
  - worktree 分支 session/st-nightsweep-sw11-20260929 直连批 2bd67c05+2ad4f15d 待 merge train 归 dev

merge_train_note:
  attempt_1: >-
    2026-09-29 SW11 曾按 §2.9 尝试 session_worktree merge（ai/st-nightsweep-sw11-20260929/nightsweep-sw11→dev），
    因 dev 已大幅推进（86ed076a0b→7f9de37b2a+）且主区 3300 脏面属他会话在途，ort 策略失败；
    工具失败路径自清理，主区无 MERGE_HEAD 残留（已核实）。为避免主区连坐，本车道停止重试，
    branch 合并归总筹 merge train（Wave 2 在册）。分支=2bd67c05+2ad4f15d 两 commit，文件面与
    队列 q-0001 袋零交集，可安全快进式合并。
final_queue_check: q-20260929-st-nightsweep-sw11-20260929-0001 pending（serializer 活跃 lease 持有中，
  45 pending 排队为全队列共性，非本袋异常）
```
