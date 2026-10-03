---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW7_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW7 现场修复与核销车道台账（sid=st-nightsweep-sw7-20260929，总筹=st-nightsweep-chief-20260929）
# 生成: 2026-09-29T06:52:05
# 环境冷启动: PATH 3.12.8 ✓ / lock cleanup CLEAN ✓ / reaper 活跃(killed=0, ghosts=0) ✓ / SessionRegistry 注册 ✓
# 工作区: 会话 worktree .worktrees/st-nightsweep-sw7-20260929（已建，零修改）；实质操作全部经主区+提交队列（chief 卡面显式指定的主区路径处置，登记原因=总筹改判 R5 改名令）

ledger:

  - id: 卡1_R5改名处置
    verdict: DONE-LANED-PENDING
    detail: |
      ①磁盘改名 git mv：docs/_working/night_sweep_20260929/ → docs/_working/night_sweep/（10 件全部暂存面 A 态随迁）。
      ②路径引用修正 5 面：.runtime/tmp/st-nightsweep-20260929/00_orchestration.md（2 处）、docs/_working/night_sweep/00_orchestration.md（3 处）、
      战情室 8 件 asset_id/正文 10 处、capability_canonical_file_registry.yaml 未暂存累积区 10 条（safe_write_text CAS，进程外核实 old=0/new=10）。
      ③队列换路径：原袋 sw1-0013 已死（R5-DIGIT-SUFFIX，dead 记录保留作审计）；原袋 sw4-0001 pending 撤回（我方自有袋）。
      重投=q-20260929-st-nightsweep-sw7-20260929-0003（15 件：骨架 1+sw4 件1 的 13 件+注册表累积快照；
      11 件 disk==原 blob 逐字节同；message 首行注 [R5 改名重投·原袋 sw1-0013+sw4-0001]。
      中途 q-0001/q-0002 为 C1 短窗自动合并产物，已撤回重投为单袋保 message 归属完整）。
      REGISTRY-MASS-DELETION 处置：sw6-0003 落地已吸收 sw1 两条旧路径 token 入 HEAD，改名=2 条身份消失，
      走官方逃生 [allow-mass-deletion:R5 改名账实修正…]（同数重登记非退役，message 永久留痕）。
      ④R5 验证：新路径 0 处命中 _\d+$ 目录后缀判据（night_sweep 合规；grid_20260926-024947 以 -数字 结尾不属 R5 面）。
      CREATE-GUARD 落地同源化（M2.1）应对：袋自带注册表快照使 token 判定走盘读面。
      遗留登记：主区 index 残留旧路径 staged-A 态（收敛序依赖落地侧衍生漂移容忍，禁裸 reset 共享暂存区）。
    evidence: "q-20260929-st-nightsweep-sw7-20260929-0003 (files=15) 在队待 drain；grep night_sweep_20260929 全仓内容面=0（.runtime/tmp 他车道工作稿除外）"

  - id: 卡2_GPU死袋代修归还原主
    verdict: CROSSCHECK-不触发
    detail: |
      原主已自救：dead q-20260929-st-gpu-conv2-20260928-0001（死因 BLUEPRINT-FORMAT，测试件头 module_id 用路径）
      → 原主 st-gpu-conv2-20260928 自行重投 conv3 袋（q-20260929-st-gpu-conv3-20260928-0001，04:51 在队 pending），
      测试件 blob 已换（295fe863→9011efa6），新头='# [BLUEPRINT] MOD-BT-233-T | docs/03_modules/_domain_backtest/blueprint.md' 合规格式。
      三件中另两件 blob 与死袋逐字节同（gpu_core.py 6c13ddc0/checklist b727c780）。代修协议不触发（修了必撞车），让路。
    evidence: "conv3 在队 blob 9011efa6f90c 首行核验 MOD- 前缀 ✓；避让图 GPU 领地零触碰"

  - id: 卡3_队列核销看板
    verdict: DONE-LANED
    detail: |
      watchboard v2 落盘=.runtime/tmp/st-nightsweep-sw7-20260929/queue_watchboard_v2.yaml。
      卡面 11 袋+sw6 系+sw3 系全量三态盘点：landed_verified=3（sw6-0001=eb2df8bf28、sw6-0002=c2ec2ff87a、sw6-0003=14dc95cb05，
      逐袋 git cat-file HEAD 验真）；processing=4（sw1-0014/sw2-0003/sw3-0002/sw5-0004 排空中）；
      still_pending=11（sw2-0004/0005、sw6-0005/0010/0011 回填三批 946+400+400 件、sw3-0003/0004、sw4-0002/0003/0004、sw7-0003）；
      dead=12（死因逐袋登记：GATE-PRECOMMIT-RUN×5、cascade_stale、CREATE-GUARD、自证读回、DEPGRAPH、R5（已由本车道核销）、GPU BLUEPRINT（原主已自救））。
      卡面 11 袋无一 landed：4 死 2 排空 2 pending + sw1-0013 死（本车道重投核销）+sw1-0012 死（未深查，SW1 自责面）。
    evidence: "queue_watchboard_v2.yaml 快照 06:41:05；drain 活跃（HEAD 推进实证：2060958a→14dc95cb→0eabbbf8）"

  - id: 卡4_dead缺件第一批代投
    verdict: DONE-0投20登记
    detail: |
      前 20 封逐封核验：blob 全部在档可恢复、目标路径全部不在 HEAD——但无一封属"丢失的工作"，全部属"已被继任/过时"，盲投=死信再生或回退事故：
      ①meta_question/registry.py×13 封（chainpile 0031/0055-0062/0065/0067/0069/0070）：功能已由继任件 meta_question_registry.py 落 HEAD
      （旧路径零 importer；其中 9 封 0923 当时就死于 CREATE-GUARD 能力重复——门禁当时已判 duplicate）；现投即 CLONEGUARD 第二真源+CREATE-GUARD 无 token 双死。
      ②check_meta_question_batch.py×4 封（0036/0063/0068/0071）：磁盘已存在进化版（1ea15e51/20469B > blob 96978402/14529B，untracked），
      投旧 blob=裂脑回退。登记建议：原主/维护班对磁盘新版补 token 入册。
      ③trae_087_meta_question_registry.yaml×2 封（0041/0066）：全仓零引用，规则面无此号。真缺失但无消费方。
      ④pf_alloc 系×3 封（combine 0001/0002/0003，LandingEnvironmentError/三向合并失败=环境死因）：pf_alloc 模块已由后续路线全量落地并进化
      （HEAD 面远超袋内 3 py；base_weight_mode 键已从 AllocationConfig dataclass 消失）——投旧 config/pf_alloc.yaml 将触发现行代码
      AllocationConfigError('未知配置键')=活故障。袋内另两册（capability/module_translation）为 0923 陈旧快照，投=注册表大回退。
      真缺失清单（登记不入库）：config/pf_alloc.yaml（缺但 0923 schema 与现行代码不兼容，需按现行 schema 重出，勿直投 blob）；
      trae_087_meta_question_registry.yaml（缺但零引用）；check_meta_question_batch.py（HEAD 缺但磁盘有新版）。
      后 297 封未动（本卡面只取前 20）。
    evidence: "逐封 blob sha/字节数/HEAD 判存/现行 dataclass fields 核验记录在案（fields 无 base_weight_mode 实证）"

  - id: 卡5_SW2让路两卡补投窗口
    verdict: BLOCKED-登记（窗口未满）
    detail: |
      前置核验：zc8-lane-docs64 袋已不在 pending（册争用解除）✓；SW2 八件磁盘现件全健在 ✓。
      但：卡4（l7_prior_opener）token×2 未入 HEAD 册（仅盘面累积区）；卡7（read_side 三 .py token 已入 HEAD ✓）
      但两个 algo_flow yaml（fms_hygiene_gate.yaml/fms_ref_extractor.yaml）token 未入 HEAD——两卡都还差注册表。
      注册表现状：st-chief7-20260928 活跃持有编辑期 claim（核验时点已锁 3.6m，非死锁 stale），且磁盘快照落后 HEAD
      （52s 预检窗口内他袋落地推进 HEAD→REGISTRY-MASS-DELETION 拦截实证）。
      按卡面铁律"仍被持→登记"：不做活跃持锁下的手工注册表合并（正中 claim 协议防的竞态）。
      重试处方：chief7 释放且其册先行袋落地（l7/fms-yaml token 入 HEAD）后，两卡按 SW2 台账 next 清单原样补投
      （卡7 可先试 5 件免注册表形态；卡4 需 5 件含册或等 token 入 HEAD 后 4 件）。
    evidence: "HEAD 册 grep 实证：fms .py token 在（L53606-53616）/l7 token 无；lock status 持有者 st-chief7-20260928"

  - id: 卡6_zcloseout0083同路径协调
    verdict: DONE-结局B落地
    detail: |
      实际结局=卡面预判的结局 B：0083（post-flush re-register）已落地 done/（landed=cea89252bc chore(integrity): post-flush re-register），
      我方出库袋 sw1-0003（Owner 批② tombstone 出库 rules_integrity_db.json）死于此前的 cascade_stale
      （stale_by=q-20260929-st-c8-rulings-0002 先落地同路径改写，非 0083 直接击杀）。
      处置：不重投出库袋——出库意图已与两次落地 re-register（c8-rulings-0002+0083 时序竞态治本）正面冲突，
      再投=对抗治本机制的无尾循环。登记 OWNER-GATE：Owner 批②出库令 vs re-register 治本机制二选一，
      若 Owner 维持出库，应由 Owner 面重颁（净删 registered 文件=human gate 域）。
    evidence: "done/q-20260929-st-zcloseout-20260928-0083.json + git log cea89252bc；dead sw1-0003 死因全文"

summary:
  new_qids: [q-20260929-st-nightsweep-sw7-20260929-0003]
  withdrawn_own_bags: [q-20260929-st-nightsweep-sw4-20260929-0001(pending 撤回), q-20260929-st-nightsweep-sw7-20260929-0001/0002(C1 合并产物撤回重投)]
  untouched_foreign: "他队袋零触碰（含 dead/processing）；nightclean-0017/sw3-0002 等注册表旧路径 blob 袋的 FIFO 位次风险已在 watchboard v2 标注"
  conflicts_for_chief:
    - "注册表旧路径回写风险：nightclean-0017(blob 含 10 旧路径)/sw3-0002(2 条) 仍在我袋之前 FIFO，若其先落地会短暂回写旧路径条目；我袋落地后终态正确（三向合并+我袋最后写）；若他队今晚再投含旧路径册的袋则再污染，建议 chief 广播 R5 改名令"
    - "sw1-0003 出库意图 vs re-register 治本冲突（OWNER-GATE，见卡6）"
    - "主区 index 旧路径 staged-A 残面+meta_question 系 staged-D 残面（他方 stale staging，零触碰移交）"
  worktree: ".worktrees/st-nightsweep-sw7-20260929 已建零修改（预检 WORKTREE-REQUIRED 合规通道），收尾留待总筹裁"
```
