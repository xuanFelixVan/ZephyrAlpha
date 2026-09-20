---
ttl: task_bound
completes_when: 战役 st-vocabconsol-20260918 W8 封账提交后转 archived
---

# W4 施工留痕——归层映射真源 + DB 域合并 + 补标/职责层生成器

批次志 W4（2026-09-18 通宵班，裁定#335 结论⑤⑥授权面内施工）。

## W4a 归层映射真源（子代理施工，主会话收口）

- 产出：`docs/01_policies_and_standards/_registry/catalogs/domain_responsibility_layer_mapping.yaml`
  （scaffold 新建，creation_token 经 safe_write_text CAS 补登 capability registry）。
- 域全集 84 = 词表 v1.1.0 62 values ∪ 10 aliases ∪ functional_domain_registry 68 ∪ w1d 在用增量
  （9 脚本族域 + D_TEST）；分布 governance 28 / business 33 / ai 11 / infrastructure 12。
- 10 个"?"域自裁定（一行理由入 reason 字段，判例锚点见 w1d_layers.md）：
  D_FBL_VERIFICATION→governance、D_SECURITY→governance、D_AUTONOMY_PERM→governance、
  D_OPS→infrastructure、D_ML_SERVE→ai、D_INTEGRATION→infrastructure、
  D_INTEGRATION_GATEWAY→infrastructure、D_DATA_GOV→governance（#335 判例）、
  D_DATA_SEC→governance、D_TEST→governance。
- 主会话终局两项 pending（Owner 睡觉中，按裁定框架自裁）：
  ① D_TEST：定稿 governance（D_AUDITTEST 同构先例；depgraph 0 节点=无运行面误伤；
     若整域退役走骨架 §7 变更纪律改行）。
  ② D_RESEARCH：定稿 ai（层随 canonical D_INTELLIGENCE；"研究域独立"争点 C10 已由
     #335 折叠结论终结，无新证不重开）。pending_owner_review 标记已移除。
- 别名行带 alias_of 且层随 canonical——保证 #335 三段式折叠后职责层不缺失（结论④同构要求）。

## W4-B组 DB 域合并（子代理施工，官方通道）

- `apply_depgraph.py --merge-domain` 两次：D_INFRASTRUCTURE→D_INFRA_OPS（84 节点，
  affected 2697 含子串引用/路径映射/依赖边）；D_RESEARCH→D_INTELLIGENCE（2 节点，affected 427）。
- 复核三判据 PASS：domains 无旧行（75→73）/canonical 计数=原+迁入（100/164）/
  12 身份列 distinct ⊆ domains（孤儿 0）；重复 merge RC=4 零写入（幂等安全）。
- 备份：`.runtime/tmp/vocabconsol_db_merge/backup_pre_merge.json` + 官方 19 表快照。
- 插曲：①首次 merge 因 arch_constraints PK 撞 4 条 detector 属主陈旧违规行整事务回滚（零残留），
  经官方 --delete-constraint 清行后放行（该类行每次检测 DELETE+重插，自重生成）；
  ②POST-RENAME-CHECK 18 行告警为假阳（scan_residual LIKE 未转义，命中连字符 D-RESEARCH）
  ——登记为后续治本候选（非本战役范围）；③五图 reconcile 19 生成器 exit 0，align_all 域不一致=0。
- **过渡期已知现象（不修，#335 结论③设计使然）**：functional_domain_registry.yaml L1205/L1717
  两旧域条目经 sync_yaml_to_depgraph UPSERT 会重建 DB 旧域行（实测 06:47/06:54 两次；
  节点不回退，仅空行）。终局删除=注册表净删 Owner 门位+退役审计，本战役零净删纪律覆盖。

## W4c domain 补标生成器（后台施工中）

- 输入 no_domain_list.csv 2115 行；工具 `backfill_module_domain.py`（兄弟票→path_ownership_map
  →depgraph DB 三级推断，推断不出留白；dry-run 默认，--apply 跳脏文件+sha256 审计）。

## W4b responsibility_layer 生成器接线（后台施工中）

- add_module_translation.py 新条目按 domain 自动填层 + `--sync-layer` 全表重算（幂等）；
  loader 透传；映射加载 fail-fast 入 yaml_utils SSoT。真实全量 sync 待 W4c 落定后主会话放量。

## W4c 放量终态（主会话收口，2026-09-18 晨）

- 干跑 1703 候选 → 实写 **1686** 文件（audit.jsonl 全量留痕：inserted_after_module 1582 /
  inserted_in_anchor 77 / replaced 27；verify_body_unchanged 全 True）。
- 未写差分：34 幽灵路径（清单有/磁盘无，主区被他会话重命名）+ ~17 放量窗口内变脏
  （他会话 WIP，skip_git_dirty 护栏正确生效）。
- 收口复核：post-check 干跑 would_change=1（`src/zephyr/data/config/known_data_gaps.yaml`，
  他人在途 MM 文件）→ 归属会话提交时自过本闸，非残留问题。
- **事故+治本（schemas 7 件）**：放量发现 `schemas/categories/market/*.py` 既有废弃值
  D_DATA 被兄弟票盖成 D_GOVERNANCE（语义错误）。手工钉正为 D_MKT_DATA
  （记录 .runtime/tmp/vocabconsol_backfill/manual_fixes.json）+ 工具治本：
  `load_deprecated_replacements`（N/A/多靶"、"目标不入图）+ m_deprecated_migration
  短路优先于三级推断（backfill_module_domain.py:870-884）。
- 回归用例 3 件（TestDeprecatedMigration）：唯一 replacement 压过兄弟票 / N/A 回落投票 /
  映射图排除非唯一靶——判红性由用例结构自证（迁移分支失效则 inferred=D_BETA 断言必红）。
  d3_metadata 目录全套 190 passed。

## W4b 放量终态（主会话执行 --sync-layer）

- 实跑：entries 7106，写入 4988 / 无 domain 跳过 2118 / 缺映射 0 / 不可解析 0；
  二次干跑 未变 4988 / 写入 0（幂等收敛）。TR diff +5009/-0 纯插入（无 mass-deletion 风险）。
