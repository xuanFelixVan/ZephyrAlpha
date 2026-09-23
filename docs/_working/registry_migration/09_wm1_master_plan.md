---
ttl: task_bound
title: "W-M1 施工总图 v1.0（三设计合体+波次计划+Owner 决策包，2026-09-23 呈签）"
session: st-regfix-lane0b-20260923
---

# W-M1 注册表迁 PG 行级账本·施工总图

> 真源三件套：01_inventory.md（甲·盘点）/02_ledger_design.md（乙·账本）/03_projection_design.md（丙·投影），全部已在 HEAD。
> 立项依据：Owner 2026-09-23 口谕"直接用最好的方案一口气搞定"；对标两份调研（06/07 号文，67 源）证实此为终局架构无更远期。

## 一、终局架构（一张图）

```
会话（10-20 并发）──意图API──▶ PG 行级账本（唯一真源）
  register/update/retire            条目表(唯一约束+version CAS+持条会话)
  按条目声明，禁整文件              事件表(只增不改，who/when/what)
                                   快照表(发布=不可变全量+单调版本)
        │                                │
        ▼                                ▼
  本地投影状态文件              生成器：YAML := render(PG) 纯函数
  (content_sha256+revision)     字节确定性重打，排序键=(file,token)与合并器同构
        │                                │
        ▼                                ▼
  漂移检测四象限(门禁只读本地)    YAML=只读投影（11 读端零改动，PG 宕机不阻塞）
  私改=PG wins 自动再生成+留证
```

## 二、迁移范围（甲号文盘点定案）

- **P0 第一波（多写者热表，R2 级）**：capability_canonical_file_registry（churn 512/30d，6 门禁直读）、module_translation_registry（7194 条最大）、rule_catalog(166)、architecture_issue(114)、error_code(78)、candidate_module(69)、ruling_registry(68)
- **留 git**：生成器工件(R5)/低频人工长尾(R4)/纯文档(R6b)/密钥册(R7 明令不迁)
- **PG 先例已在**：depgraph 双表+meta_question 三表，ROOR 介质字段已支持 postgresql://

## 三、波次计划（乙号文四相）

| 相 | 内容 | 出口判据 |
|---|---|---|
| Phase 0 | 基线导入（dry-run 报告+Owner 验收门对账 W1 口径） | 对账零未解释差 |
| Phase 1 | 双轨并行（落地器 hook 逐条对账，drift 走 belt daemon 记账） | 连续 7 天零未解释 drift |
| Phase 2 | 按册切主（试点=rule_registry） | 试点册三绿 |
| Phase 3 | 回滚预案演练（末快照 render 重生成翻回真源） | 红蓝一次过 |

## 四、Owner 决策包（B 包，签字栏）

### 乙·账本六决策点
| # | 决策 | 推荐 |
|---|---|---|
| D-1 | 与馆员 B1 账本"视图引用不重建" | 批（同一 PG 实例复用） |
| D-2 | v1 写路径走 Python API+白名单 gate 复用 depgraph 既有件 | 批 |
| D-3 | 条目租约 TTL 与 belt daemon 记账联动口径 | 批（30min 对齐） |
| D-4 | 快照保留窗口 | 批（14 天+月档） |
| D-5 | force 接管门位（需 Owner 显式批文才可用） | 批（high 域） |
| D-6 | 事件表留存年限 | 批（6 年，FINRA 基准） |

### 丙·投影六决策点
| # | 决策 | 推荐 |
|---|---|---|
| P-1 | capabilities 378 行同波全量迁 | 批 |
| P-2 | 26 条脏数据呈报制（2 无 token/6 无 created_by/18 无 capability） | 批（呈报非阻断） |
| P-3 | 影子期 3 天后执法翻转 | 批 |
| P-4 | golden hash 零改动保留 | 批 |
| P-5 | REG-GEN-001 并条（w5_1 同真源必并） | 批 |
| P-6 | outbox 缓建（宕机时 token 登记延后可容忍） | 批 |

### 甲·盘点确认
| # | 决策 | 推荐 |
|---|---|---|
| A-1 | P0 七表第一波名单 | 批 |
| A-2 | ROOR summary 76→77 漂移修正+35 未册补登（RULE-FOUR-WAY） | 批 |
| A-3 | 同文件多 ID 两簇（CAPCAN≡GEN/STD-005..008）w5_1 内收 | 批（随迁移一并） |

## 五、验收判据（Owner 终极目标映射）

1. 20 路并发提交全落地零死信；同文件 20 条互踩零丢失（压测 Phase B）
2. 任意册私改≤1 个落地周期内被自动纠正（漂移四象限执法）
3. PG 宕机期间读端零阻塞、施工不中断（容灾不变量）
4. 事件账本可回答"谁在何时改了什么"（SQL 三秒内）
5. YAML 永不再手工维护（重生成+diff 与 HEAD 零差）

## 六、施工分工（批后即开）

- 波0：DDL 部署器+API 骨架+生成器（Flash 两车道，写域互斥）
- 波1：Phase 0 基线导入+对账门（我 Lane 0 验收）
- 波2：双轨+试点切主（我盯出口判据）
- 与馆员系统汇流：同一 PG 底座，B1 视图引用
