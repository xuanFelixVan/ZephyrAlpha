---
ttl: task_bound
completes_when: tests/ 治理战役八环节收官（分类+清理+防膨胀闸落地，终报 99_delivery.md 出具）
---
# tests/ 治理战役 · 总骨架册（00_skeleton）

- 生成: 2026-10-04 | 总包会话: st-tests-chief-20261004 | 状态: 施工中
- Owner 三拍板（2026-10-04，本战役立法基础）:
  1. 一级域切法: 8 域草案批准（gov/data/trade/research/infra/ai/meta/legacy_zephyr）
  2. 顺序: 批0 机械垃圾 → 拆簇+门禁收窄 → 分类批（纯位置归并零语义决策） → 清理批（L1-L4 逐档）
  3. 豁免收窄: **现在随批改**（"一级豁免、二级受限"）——理由=闸与战役解耦反烂尾 + 即时阻塞面≈零 + 收窄后门禁成为分类批棘轮

## 一、现状基线（2026-10-04 实测）

| 维度 | 值 |
|---|---|
| 顶层子目录 | 148 个（另 3 散文件: conftest.py / test_batch_creation_tokens_anchor.py / test_generate_governance_map.py） |
| 测试文件总量 | 4046 .py |
| 超限目录（120 口径） | governance(830 递归/165 直接) / zephyr(150) / signal_ashare(149) / backtest(143) / infrastructure(137) / trading(121) |
| 空壳目录 | xt4tmp / ml_serve（已批0清除，零 tracked） |
| 含 skip 文件 | 212 |
| 双树残局 | tests/zephyr(150) 镜像包结构 vs 147 按域平铺——两次分类运动烂尾遗存（前史: ARCH-029 禁 tests/unit） |

膨胀机理三股力: 平铺惯性（新模块=新一级目录，零结构约束）/ 迁移烂尾（双树+同名异父）/ 豁免缺口（FOLDER-CAPACITY tests/ 全豁免=全仓唯一无闸区）。

## 二、环节清单（8 环节，先挖后干、线间并行）

| # | 环节 | 产出 | 状态 |
|---|---|---|---|
| E1 | 挖矿·结构普查 | 01_structure_census.md（归并表数据+二级超限清单+同名异父+zephyr对撞） | 矿工1 在飞 |
| E2 | 挖矿·引用面普查 | 02_reference_census.md（P0会炸/P1需同步/P2叙述 分级） | 矿工2 在飞 |
| E3 | 挖矿·垃圾判据 | 03_garbage_census.md（L1 collection错/L2 skip分类/L3对撞/L4线索） | 矿工3 在飞 |
| E4 | 批0 机械垃圾 | xt4tmp/ml_serve 物理清除 | ✅ 完成（零 tracked 零 git 影响） |
| E5 | 门禁收窄 | folder_capacity_hard_limit_gate.py 单点改 + 18 例测试 | 代码面完成，待落地即拦面评估后提交 |
| E6 | 分类批 | 分域 git mv 下沉（每批一域+depgraph 重建+套件验证） | 待 E1/E2 矿回 |
| E7 | 清理批 | L1 断链删 / L2 永久 skip 处置 / L3 双树保活删腐 / L4 隔离 | 待 E3+E6 |
| E8 | 防膨胀收口 | 一级目录数封顶立法注记+季度审计挂账 w5_1 | 待 E6 |

## 三、施工纪律（多队并发窗口）

1. tests/ 与 src/zephyr/gov_enforcement/ 施工前逐批 claim；他会话持有=登记让路（宪法 §3.4）。
2. map_family/ 拆簇半成品=st-tclose-integ B2 在途成果，本战役只交叉验证（已验: panorama:302 引用同步、import OK），不代提交不代扩。
3. 分类批纯位置归并（git mv 保 rename 历史），零语义决策；L3 判重留清理批单独立案。
4. 每分类批: git mv → generate_project_depgraph.py --force → conftest/pytest 配置同步 → 套件跑 → git_commit.py 白名单提交。
5. 内收原则: 一级目录 148→8（净收敛）；新格子必须声明替代对象（宪法 §4）；不新增规则/册子——门禁收窄是改既有 gate 行为非新 gate。
6. 盘面 ruff 格式化噪音（39 文件未提交面）系他会话在途，本战役提交时逐笔 git log -1 --name-only 核实归属，不抹不回退。

## 四、风险登记

- R1: 门禁收窄落地即拦二级>120 存量（待 E1 数据定量；若拦面大=先拆格子后落地）。
- R2: 分类批撞在飞车道（tests/governance/commit_gates 119 贴顶+fig13 接线四件在途）——gov 域下沉排在 fig13 接线落地后或协调窗口。
- R3: pytest collection 全量慢（E3 矿工实测中）——分类批验证用分域子集+循环检查抽样。
- R4: tests/zephyr 对撞判重（L3）判错代价高——5.3 亲做不外派（Owner 模型分派原则）。

## 五、环节子文档索引

- 01_structure_census.md — 结构普查+归并表（E1 产出）
- 02_reference_census.md — 引用面普查（E2 产出）
- 03_garbage_census.md — 垃圾判据数据（E3 产出）
- 99_delivery.md — 终报（收尾产出）
