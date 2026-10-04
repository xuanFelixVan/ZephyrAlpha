---
ttl: task_bound
completes_when: tests 治理战役终报出具（gov 域批7 与循环检查终态回填后闭环）
---
# tests/ 治理战役 · 终报（99_delivery）

- 总包: st-tests-chief-20261004 | Owner 令: 2026-10-04 晚（三拍板+全部开工+总包制）
- 状态: 主体完工收尾中（本文档随 gov 批与循环检查终态回填）

## 一、Owner 三拍板执行回执

1. **8 域切法** → 已落地 7/8 域（129 目录中 116 归位；gov 32 目录待 G2 车道 staged 面释放即搬）。归并裁定表=04_merge_verdicts.md（机生真源，21 个 need_review 全裁定，依据=import 面实测）。
2. **两步走顺序** → 批0（空壳清除）→ 线A 门禁收窄（**已落 d61877c3**）→ 分类批（7/8 域）→ 清理批（L1/L2/L3/L4 全裁）。顺序完全按批执行。
3. **豁免收窄现在改** → FOLDER-CAPACITY "一级豁免、二级受限"已生效（_tests_depth_exceeded 谓词；共享谓词 is_test_exempt 零改动；fail-open 保持；18 例专测补历史欠账）。落地即拦面实测=零（现存二级无 >120）。

## 二、已打通（按提交/入队）

| 批 | 内容 | 状态 |
|---|---|---|
| 线A | 门禁收窄+骨架册 | **落 HEAD d61877c3**（3 文件） |
| 批0 | xt4tmp/ml_serve 空壳 | 物理清除（零 tracked） |
| 批1+2 | data(13)+infra(10) 两域 23 目录 | 入队 q-…-0001（397 文件快照） |
| 批3-8 | trade/ai/meta/research/legacy_zephyr 六域 93 目录 | 入队 q-…-0002（2194 文件快照） |
| 清理批一 | 删 3 死测试+修活 2 断链 | 入队 q-…-0003 |
| 批7 gov | 32 目录+P0 四处修 | 待 G2 staged 释放（宪法 §3.4 不硬闯） |

## 三、治本四件（膨胀机理逐一对应）

1. **平铺惯性** → 129 目录→8 域归位（148→8 一级收敛）；一级域名封顶由裁定表固化（新增域=净零申报）。
2. **迁移烂尾** → tests/zephyr 残局收容为 tests/legacy_zephyr（150 文件 3716 items 复收在册）；双树并存终结。
3. **豁免缺口** → 门禁收窄落地（二级起受限），分类批每域搬迁即受闸验收（棘轮生效：commit_gates 120 压线+legacy_zephyr/data 115 贴顶均在册监控）。
4. **锚定脆弱** → 锚定链平移治本（parents[k≥1]+1/parent 链≥2+1 的 HEAD 对拍确定性修复器）；554 文件 parents 耦合全量处置零回归。

## 四、验证

- 七域 collect 全绿零 error：data 2557+infra 4440+trade 7624+ai 9420(存量1已删)+meta 7593+research 10374+legacy 3716(存量1已修活) ≈ **45724 items**
- data 域实跑详分诊：2456 过/17 failed 全数存量或他会话在途（Set-VaultMtime 滞后封印批×9/SourceType 枚举演进×7/tdm sop 瞬态×1/#ARCH-084 误归因×1）=零搬迁回归
- 七域全量实跑：run1（回填中）
- 循环检查：待 run1 后连续两轮

## 五、关键裁定记录（总包自裁，依据留痕）

1. gov 域暂缓（G2 在途面在我 mv 范围=活会话冲突，等落地不硬闯）
2. L3 七对=互补覆盖零删除（抽验 internal_compute_provider：263 行算法单元 vs 110 行集成行为）
3. L4 184 件原地保留（隔离格方案撤销，内收少一动少一险）
4. P0#7 判休眠回滚（目标全仓不存在，改向无验证面归维护班）
5. capability 册随批策略=册出白名单（热文件被他队持锁+overlap 5 次熔断后，token 走账本+staged 册面供 gate 读，册面投影由下个持窗者落）

## 六、学费档案（配方固化）

- git mv 自撞名两步中转（data/ai/research 三起：mv→staging→mkdir→mv 回→域目录上提）
- 索引被并发进程重建（物理=终态时 git add -A 十三路径重收 rename）
- 修复器幂等化（HEAD 对拍确定性变换，治重跑叠加 parents 越界）
- unique 化与修复器次序（修复器会回写 HEAD 原文→独特化必须每域 migrate 后重跑）
- Defender 间歇 Errno 22（写重试 4 次指数退避）
- Windows 参数 32K 上限（2194 文件清单走 enqueue_item API 全快照）
- TAKEOVER 自咬（ZCode 壳 pid 亡+心跳守护 idle timeout=分离守护重启配方）

## 七、遗留与移交

- gov 批7 工单就绪（migrate_domain.py gov 一键+P0 四处修单）——**唯一未完成环**
- 队列三袋消化确认（q-0001/0002/0003）
- 防膨胀立法注记：一级目录数封顶（≤10）挂季度内收审计（w5_1）
