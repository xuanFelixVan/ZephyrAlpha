---
ttl: task_bound
---

# 产业链修复 SQL 移植批（REPAIR-WO-001 batch1）

> 执行者：DBA/Owner（应用连接对 ig_* 只读）；逐节独立事务；执行前记录影响行数。备份：.runtime/tmp/backup_renaming_20260918.json、.runtime/tmp/sector_bridge_draft.json

```sql
-- REPAIR-WO-001 migration batch 1
-- 执行者：DBA/Owner（应用连接对 ig_* 只读，DDL/DML 需 postgres 属主）
-- 依据：docs/_working/altdata_line/07_industry_chain_repair_workorder.md
-- 备份：.runtime/tmp/backup_renaming_20260918.json（96 条改名旓名）；.runtime/tmp/sector_bridge_draft.json（55 条预演桥）
-- 事务建议：每节独立事务；执行前记录影响行数

-- ===== R4a: 行业聚合改名（96 行，备份已存） =====
UPDATE ig_node n SET name = c.name || '聚合', updated_at = now()
FROM ig_chain c
WHERE n.chain_id = c.chain_id AND n.name = '行业聚合';
-- 无链名的兜底（预期 0 行）
UPDATE ig_node SET name = '行业聚合(' || right(node_id, 6) || ')', updated_at = now() WHERE name = '行业聚合';

-- ===== R6: ig_edge 补 valid_from（PIT 对称） =====
ALTER TABLE ig_edge ADD COLUMN IF NOT EXISTS valid_from date;
UPDATE ig_edge SET valid_from = created_at::date WHERE valid_from IS NULL;

-- ===== R1: 行业桥表（结构） =====
CREATE TABLE IF NOT EXISTS ig_sector_bridge (
  bridge_id    bigserial PRIMARY KEY,
  sector_code  text        NOT NULL,
  sector_name  text,
  node_id      text        NOT NULL,
  match_method text        NOT NULL,          -- exact / contains / official_map / manual
  confidence   real        NOT NULL,          -- 1.0 / 0.7 / 人工定
  verified     boolean     DEFAULT false,     -- 人工核验旗
  valid_from   date        DEFAULT CURRENT_DATE,
  valid_to     date,
  created_at   timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sector_bridge_code ON ig_sector_bridge(sector_code);
CREATE INDEX IF NOT EXISTS idx_sector_bridge_node ON ig_sector_bridge(node_id);
-- 预演 55 条桥装载：DBA 用 .runtime/tmp/sector_bridge_draft.json
-- （\copy 或 python psycopg copy_expert；verified=false 待人工抽检 30 条）

-- ===== R5: IO 流量/系数回填（模板，需先下载 2020 年 153 部门表） =====
-- 步骤：国家数据平台 data.stats.gov.cn 下载 2020 年投入产出表（153 部门流量表+直接消耗系数表）
--       → 建 io_2020_staging(code_from text, code_to text, flow_wan numeric, coef numeric)
--       → 对齐回填：
-- UPDATE ig_io_edge io SET flow_wan = s.flow_wan, coefficient = s.coef
-- FROM io_2020_staging s WHERE io.from_sector_code = s.code_from AND io.to_sector_code = s.code_to;
-- 验收：非空率 100%；行和校验（每部门中间使用合计=总产出-最终需求）

-- ===== R2②: supplies_to 降级（噪声审计结论 63%>30%，已完成抽样判定） =====
-- 游走骨架换轴已裁定：主干=ig_io_edge。ig_fact.supplies_to 作为 C 级叙事边保留，
-- 建议加注释性登记（无 schema 变更）：
COMMENT ON TABLE ig_fact IS '来源=ckg_2021 外部数据集；supplies_to 噪声率约63%（2026-09-18 抽样30），降级C级叙事边，禁入自动决策；游走主干=ig_io_edge（官方2020 IO表）';

-- ===== R2① 备注：external_ref 列不再需要 =====
-- ig_fact.source 已 100%='ckg_2021'，数据集出处已由 source 列完整表达，无需新列。
```
