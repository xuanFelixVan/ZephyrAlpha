-- P2 PostgreSQL迁移：扩展初始化脚本
-- 创建扩展（pg_stat_statements用于监控，pgcrypto用于UUID生成）
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- P3阶段将添加的扩展（预先创建占位注释）：
-- CREATE EXTENSION IF NOT EXISTS vector;  -- P3: pgvector
