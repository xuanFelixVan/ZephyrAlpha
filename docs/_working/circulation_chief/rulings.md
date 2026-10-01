---
ttl: task_bound
---

# 总包裁定簿（st-ffchief-20261001）

> Owner 2026-10-01 总令授权自裁（架构师第一性原理/长远战略/100% AI 开发前提）。终局并入 ruling_registry（取号时查册避竞态，同 commit 原子）。

## CR-5 hk_connect_flow 僵尸任务停用
HKEX 2024-08 源级终止（survey §2 实证），任务僵尸在册空转。裁定：schtasks disable（可逆）+ 数据缺口登记不补历史；若 HKEX 复供再重评。

## CR-6 归档搬迁对收编
3 件脚本（grep_coverage/quick_profile/run_ollama_exam）旧删+新归同袋落地（git mv 语义补全）；归档件 ruff noqa/format 最小面修复；token 随批。

## CR-7 数据产物 git 政策（grid/跑批族）
小体积语义件（manifest/verdict/README/meta json）入库；大体二进制（.npy/.parquet/.rda/.pkl 结果件）不入 git：gitignore 政策 + 留盘（数据真源在盘/CH/冷库，git 只载代码与小册）。已 tracked 的存量二进制不动（不追溯）。

## CR-8 session_start_commit.txt 入库
4 件入库（考古证据链现用、生成脚本 tracked、33 件 retrospective 先例）。

## CR-9 争议件 top10 定谳（triage_untracked §6）
1. bridge_instruction_kernel：废弃归档同 commit 同步 CCR token + 翻译册词条墓碑（RULE-RULING 同 commit 原子）。
2. grep_coverage 三位：以 `_archive/` 根位为唯一归档位（st-commitfix token 处方），同批净删 `_archive/ops/` 旧位与 `scripts/` 根位（净零收编；-0008 已删根位，ops 位列 S9 收尾批）。
3. run_ollama_exam 分歧：✅ 已定谳（13:55 blob 三向对比）——归档位=根位+1 行 noqa 注释，根位零独有内容→归档版为准，根位删除正确，无内容损失。
4. closed_book/chart_cell（L20）：补 token+翻译词条随批落地（0 token 0 词条=登记缺位非设计豁免）。
5. grid 65 件：按 CR-7 政策拆分（小件落地/二进制 gitignore）。
6. session_start_commit.txt：按 CR-8 入库。
7. tmp.18376：PID 存活期不动，S9 收官复核后归档。
8. test_c4_pit_red_injection：随 L16 正常落地（新测试文件与友军 _c4_engine 在飞编辑无盘面冲突）。
9. t0 族 token 缺位：补 token 落地（L15），翻译册 pg_only 词条态一并收口。

## CR-10 死袋 husk 处置
-0001/-0002/-0003 为 -0004/-0005/-0006 重投链的旧壳（requeue 换号留痕），维持 dead 态不再重投，S9 清账批量核销。
## CR-12 F72 供单源裁定（W3-2 移交的 Owner 门，总包依授权自裁）
bridge-execute 委托批次文件 orders_<day>.csv 供单源三选一：**裁定=in-repo 自动生产**——plan-execute（SIM-PLAN-001 链）落导出腿，交易日 plan 执行后导出当日计划单；目录 mkdir 归属化；空单日诚实空文件（现 honest-SKIP 契约保持）。人工投放降级为覆盖通道（SOP 注记非主源）。配套补 sch_sim_bridge_execute 的 resource_profile 采样接线。理由：100% AI 开发前提下人工 SOP=单点依赖；sim 环境自动供单零资金风险；执行腿已有窗口闸/幂等预扫/两级风控（sim_daily_runner.py:1264-1315）。

## CR-13 战役目录改名（R5 合规）
docs/_working/fullflow_chief_20261001 → docs/_working/circulation_chief（R5-DIGIT-SUFFIX 实测两袋死于此门：-0013/-0021；74+1 件 staged 已迁新路径重挂；六车道已广播）。

## CR-14 F62/F73/F82 判词过期认定（W3-2/W3-3 实证）
F62 合规门五闸链已注入（order_manager.py:348/:371+sim_saga_assembly.py:163-177，fa9ae365）；F73 晋升判据执行器已实跑（league_judge+judgment-2026-10.json 10-01 05:51 UTC）；F82 order_daemon 已接线（scheduler.py:816-821→pipeline_events.py 三点，09-30 st-circ-a7）。骨架原 P0 判词过期，lane 车道改验证口径。
## CR-8'（CR-8 反转裁定）session_logs 留盘不入库
落地实测被 DIRECTORY-CONTRACT 拦（session_logs/*.txt ∉ 目录契约 allowed 清单）。四件为运行时簿记证据、价值低；扩目录契约=范围蔓延违内收原则。反转：留盘不入 git（ .gitignore 语义同类）。原 CR-8 作废存档。

## CR-15 D14-G10 幽灵复活作废（图14 契约 12→11 槽收缩）
图14 gap 节点 D14-G10（官方状态词表模块不存在/双册同谎）的幽灵件 src/zephyr/shared/vocab 已于 2026-09-26 复活落仓（a2e820034bd 词表读取层落仓；词表立法线全链闭合：01/02 卷+shared/vocab+state_vocab_registry_gate 在册），CV-GHOST 判其断言复活即红，且该节点自身 invalidation 条款明文"幽灵件复活⇒本 gap 节点作废，须回写骨架后重生成"。裁定：按条款作废——00_skeleton.md R-08 回写注记+91 提案件撤 G10 条目+图重生成（gaps 29→28 节点）+校验器契约全集 GAP_NODES 收缩为 11 槽（槽位号不回收复用）+对抗尺同步改判。理由：保留已复活幽灵断言=图数据说谎；另造新断言=虚构缺口；唯一诚实路径=条款既定的作废程序，判据改动系机械执行节点自带的失效条款非放宽。

## CR-16 死信袋 0118 销账（已被 0118v4 收官手术吸收）
q-20261001-st-ffchief-20261001-0118（reexam CPCV 族 3 件）已于 2026-10-02 01:53 由 b26627f715（收官手术·0118v4）携双册直投落地，工作区与 HEAD 逐字节一致（sha256 三件全同），死袋记录维持 dead 态销账不重投。

## 终局并册记录（2026-10-02 final closeout）
CR-1~CR-16 已并入 docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml：裁定#461(CR-1)/#462(CR-2)/#463(CR-3)/#464(CR-4)/#465(CR-5)/#466(CR-6)/#467(CR-7)/#468(CR-8,superseded)/#469(CR-9)/#470(CR-10)/#471(CR-12)/#472(CR-13)/#473(CR-14)/#474(CR-8'反转)/#475(CR-15)/#476(CR-16)。取号时册内最大=#460，16 连号无跳号；CR-8 按册铁律#9 记 superseded_by=#474。本簿自此冻结（历史档）。
