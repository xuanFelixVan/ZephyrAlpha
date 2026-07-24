-- =====================================================================
-- 幂等迁移脚本：cross_domain 列自动维护触发器（#ARCH-CROSS-DOMAIN-TRIGGER-001）
-- =====================================================================
-- 裁定: 见本次治本修复（2026-07-25）
-- 严重级别: P1（数据完整性缺陷——cross_domain 列系统性说谎）
--
-- 根因:
--   edges.cross_domain 是派生字段 = (from_node.domain_id != to_node.domain_id)。
--   但 5 个 INSERT 路径中：
--     - apply_depgraph.py SQL_INSERT_DESIGN_EDGE/PRODUCTION_EDGE 硬编码 cross_domain=0
--     - sync_yaml_to_depgraph.py 不设 cross_domain（依赖 DEFAULT，但 PG 无 DEFAULT）
--     - generate_project_depgraph.py 2 路径信任源数据
--   导致跨域边被标记为 cross_domain=0（FALSE NEGATIVE）。
--   5 个消费方（cross_domain_matrix/constraint_violations/integration_topology/
--   decision_diagram/domain_doc）全部通过 JOIN 重算，不读该列——列成为"说谎缓存"。
--   域迁移（cmd_rename_domain line 2362）明确跳过该列维护。
--
-- 修复（治本，DB 层单点强制）:
--   1. 辅助函数 edge_cross_domain_value(from_domain, to_domain) — IMMUTABLE
--   2. 触发器 trg_edges_cross_domain_bi — BEFORE INSERT ON edges
--   3. 触发器 trg_edges_cross_domain_bu — BEFORE UPDATE OF from_node_id,to_node_id ON edges
--   4. 触发器 trg_nodes_domain_id_au — AFTER UPDATE OF domain_id ON nodes（重算受影响边）
--   5. ALTER COLUMN cross_domain SET DEFAULT 0（对齐 SQLite DDL；replica 模式写兜底）
--   6. 一次性回填：修正所有 cross_domain 与实际不符的行
--
-- 为何选触发器而非删列/App层修复（100% AI 开发场景）:
--   - 删列：过度纠正，丢失查询便利性与索引，破坏 AI 惯用 WHERE cross_domain=1
--   - App 层：AI 新增 INSERT 路径会再次硬编码 0；域迁移无法覆盖
--   - 触发器：单点强制，覆盖全部 5 路径 + 未来新增；自动跟随域迁移；
--     与项目现有触发器保护模式（chk_nodes_blueprint_id/trg_edges_protect_apply_depgraph）一致
--
-- 无限循环防护:
--   - edges BU 触发器仅在 UPDATE OF from_node_id,to_node_id 时触发
--   - nodes AU 触发器执行 UPDATE edges SET cross_domain=... 只动 cross_domain 列
--   → nodes AU 的 UPDATE 不触发 edges BU（列不匹配），无循环
--
-- replica 模式（session_replication_role='replica'）会禁用所有触发器：
--   - 当前无任何脚本使用 replica=True 写 depgraph（已核查）
--   - DEFAULT 0 提供 replica 模式写的安全哨兵值
--   - 审计 reconciler（detect_constraint_violations.py cross_domain_mismatch）兜底检测漂移
--
-- 幂等性:
--   - CREATE OR REPLACE FUNCTION 可重复执行
--   - DROP TRIGGER IF EXISTS + CREATE TRIGGER 可重复执行
--   - 回填 UPDATE 第二次执行影响 0 行（WHERE 条件已不满足）
--
-- 验证:
--   1. 回填后 Defect A (FALSE NEGATIVE) = 0
--   2. 触发器测试：INSERT 跨域边 → cross_domain 自动=1
--   3. 触发器测试：INSERT 同域边 → cross_domain 自动=0
--   4. 域迁移测试：UPDATE nodes SET domain_id → 受影响边 cross_domain 自动重算
-- =====================================================================

-- ========== 1. 辅助函数：从两个 domain_id 计算 cross_domain 值 ==========
-- IMMUTABLE：仅依赖输入参数，可被索引/用于 CHECK
-- 语义：两端 domain_id 均非空且不同 → 1；否则 → 0（NULL/空=未知，哨兵值0）
CREATE OR REPLACE FUNCTION edge_cross_domain_value(p_from_domain TEXT, p_to_domain TEXT)
RETURNS INTEGER AS $$
BEGIN
    IF p_from_domain IS NOT NULL AND p_from_domain <> ''
       AND p_to_domain IS NOT NULL AND p_to_domain <> ''
       AND p_from_domain <> p_to_domain THEN
        RETURN 1;
    END IF;
    RETURN 0;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ========== 2. edges BEFORE INSERT/UPDATE 触发器函数 ==========
-- 查询 from/to 节点的 domain_id，自动设置 NEW.cross_domain
CREATE OR REPLACE FUNCTION trg_fn_edges_cross_domain()
RETURNS TRIGGER AS $$
DECLARE
    v_from_domain TEXT;
    v_to_domain TEXT;
BEGIN
    SELECT domain_id INTO v_from_domain FROM nodes WHERE node_id = NEW.from_node_id;
    SELECT domain_id INTO v_to_domain FROM nodes WHERE node_id = NEW.to_node_id;
    NEW.cross_domain := edge_cross_domain_value(v_from_domain, v_to_domain);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ========== 3. nodes AFTER UPDATE OF domain_id 触发器函数 ==========
-- 当节点 domain_id 变化时，重算所有以该节点为端点的边
CREATE OR REPLACE FUNCTION trg_fn_nodes_domain_id_recompute_edges()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.domain_id IS DISTINCT FROM OLD.domain_id THEN
        UPDATE edges SET cross_domain = edge_cross_domain_value(
            (SELECT domain_id FROM nodes WHERE node_id = edges.from_node_id),
            (SELECT domain_id FROM nodes WHERE node_id = edges.to_node_id)
        )
        WHERE from_node_id = NEW.node_id OR to_node_id = NEW.node_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ========== 4. 创建/重建触发器（幂等：DROP IF EXISTS + CREATE） ==========
DROP TRIGGER IF EXISTS trg_edges_cross_domain_bi ON edges;
CREATE TRIGGER trg_edges_cross_domain_bi
    BEFORE INSERT ON edges
    FOR EACH ROW EXECUTE FUNCTION trg_fn_edges_cross_domain();

DROP TRIGGER IF EXISTS trg_edges_cross_domain_bu ON edges;
CREATE TRIGGER trg_edges_cross_domain_bu
    BEFORE UPDATE OF from_node_id, to_node_id ON edges
    FOR EACH ROW EXECUTE FUNCTION trg_fn_edges_cross_domain();

DROP TRIGGER IF EXISTS trg_nodes_domain_id_au ON nodes;
CREATE TRIGGER trg_nodes_domain_id_au
    AFTER UPDATE OF domain_id ON nodes
    FOR EACH ROW EXECUTE FUNCTION trg_fn_nodes_domain_id_recompute_edges();

-- ========== 5. 对齐 SQLite DDL：cross_domain 列加 DEFAULT 0 ==========
-- 用途：replica 模式（触发器禁用）写入时的安全哨兵；与 depgraph_schema.py DDL 对齐
ALTER TABLE edges ALTER COLUMN cross_domain SET DEFAULT 0;

-- ========== 6. 一次性回填：修正所有 cross_domain 与实际不符的行 ==========
-- 修正 FALSE NEGATIVE（跨域但=0）和 FALSE POSITIVE（同域但=1）
-- Defect D（端点 domain_id NULL/空）不在此修正范围——0 是正确的"未知"哨兵
UPDATE edges SET cross_domain = edge_cross_domain_value(
    (SELECT domain_id FROM nodes WHERE node_id = edges.from_node_id),
    (SELECT domain_id FROM nodes WHERE node_id = edges.to_node_id)
)
WHERE COALESCE(edges.cross_domain, 0) <> edge_cross_domain_value(
    (SELECT domain_id FROM nodes WHERE node_id = edges.from_node_id),
    (SELECT domain_id FROM nodes WHERE node_id = edges.to_node_id)
);

-- ========== 7. 授予执行权限 ==========
GRANT EXECUTE ON FUNCTION edge_cross_domain_value(TEXT, TEXT) TO depgraph_reader, depgraph_writer;
GRANT EXECUTE ON FUNCTION trg_fn_edges_cross_domain() TO depgraph_reader, depgraph_writer;
GRANT EXECUTE ON FUNCTION trg_fn_nodes_domain_id_recompute_edges() TO depgraph_reader, depgraph_writer;

-- ========== 8. 验证 ==========
DO $$
DECLARE
    v_total BIGINT;
    v_false_neg BIGINT;
    v_false_pos BIGINT;
    v_correct BIGINT;
BEGIN
    SELECT COUNT(*) INTO v_total FROM edges;

    SELECT COUNT(*) INTO v_false_neg FROM edges e
    JOIN nodes n1 ON e.from_node_id = n1.node_id
    JOIN nodes n2 ON e.to_node_id = n2.node_id
    WHERE COALESCE(e.cross_domain, 0) = 0
      AND n1.domain_id IS NOT NULL AND n1.domain_id <> ''
      AND n2.domain_id IS NOT NULL AND n2.domain_id <> ''
      AND n1.domain_id <> n2.domain_id;

    SELECT COUNT(*) INTO v_false_pos FROM edges e
    JOIN nodes n1 ON e.from_node_id = n1.node_id
    JOIN nodes n2 ON e.to_node_id = n2.node_id
    WHERE COALESCE(e.cross_domain, 0) = 1
      AND n1.domain_id IS NOT NULL AND n1.domain_id <> ''
      AND n2.domain_id IS NOT NULL AND n2.domain_id <> ''
      AND n1.domain_id = n2.domain_id;

    SELECT COUNT(*) INTO v_correct FROM edges e
    JOIN nodes n1 ON e.from_node_id = n1.node_id
    JOIN nodes n2 ON e.to_node_id = n2.node_id
    WHERE n1.domain_id IS NOT NULL AND n1.domain_id <> ''
      AND n2.domain_id IS NOT NULL AND n2.domain_id <> ''
      AND COALESCE(e.cross_domain, 0) = (CASE WHEN n1.domain_id <> n2.domain_id THEN 1 ELSE 0 END);

    RAISE NOTICE 'ARCH-CROSS-DOMAIN-TRIGGER-001: total_edges=%, false_neg=%, false_pos=%, correct=%',
        v_total, v_false_neg, v_false_pos, v_correct;

    IF v_false_neg + v_false_pos > 0 THEN
        RAISE EXCEPTION 'ARCH-CROSS-DOMAIN-TRIGGER-001 FAILED: still % false_neg + % false_pos after backfill',
            v_false_neg, v_false_pos;
    END IF;
END $$;

-- ========== 9. 触发器在位性验证 ==========
DO $$
DECLARE
    v_cnt BIGINT;
BEGIN
    SELECT COUNT(*) INTO v_cnt FROM pg_trigger
    WHERE tgname IN ('trg_edges_cross_domain_bi','trg_edges_cross_domain_bu','trg_nodes_domain_id_au')
      AND NOT tgisinternal;
    IF v_cnt <> 3 THEN
        RAISE EXCEPTION 'ARCH-CROSS-DOMAIN-TRIGGER-001: expected 3 triggers, found %', v_cnt;
    END IF;
    RAISE NOTICE 'ARCH-CROSS-DOMAIN-TRIGGER-001: 3 triggers in place ✓';
END $$;
