-- ============================================================
-- 04_create_roles.sql — depgraph 访问控制角色创建
-- ============================================================
-- 裁定#ARCH-DEPGRAPH_ACCESS_CONTROL (2026-07-15)
--
-- 目的：技术层阻断绕过 apply_depgraph.py 直连数据库写入
--   - depgraph_reader: 只读（SELECT）
--   - depgraph_writer: 读写（SELECT/INSERT/UPDATE/DELETE）
--   - 默认连接使用 reader，仅白名单脚本使用 writer
--
-- 幂等：可重复执行（DO 块检查角色是否存在）
-- 前置：需以 postgres 超级用户连接执行
-- ============================================================

-- 1. 创建角色（幂等）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'depgraph_reader') THEN
        CREATE ROLE depgraph_reader LOGIN PASSWORD 'reader_dev_2026';
        RAISE NOTICE 'Created role: depgraph_reader';
    ELSE
        RAISE NOTICE 'Role already exists: depgraph_reader';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'depgraph_writer') THEN
        CREATE ROLE depgraph_writer LOGIN PASSWORD 'writer_dev_2026';
        RAISE NOTICE 'Created role: depgraph_writer';
    ELSE
        RAISE NOTICE 'Role already exists: depgraph_writer';
    END IF;
END
$$;

-- 2. 撤销 PUBLIC 在 public schema 上的 CREATE 权限（防任意用户创建对象）
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- 3. 授予 schema USAGE 权限
GRANT USAGE ON SCHEMA public TO depgraph_reader, depgraph_writer;

-- 4. depgraph_reader: 只读权限（SELECT on all tables + sequences）
GRANT SELECT ON ALL TABLES IN SCHEMA public TO depgraph_reader;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO depgraph_reader;

-- 5. depgraph_writer: 读写权限（DML on all tables + sequence USAGE）
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO depgraph_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO depgraph_writer;

-- 6. 默认权限：zephyr 用户未来创建的表自动继承权限
ALTER DEFAULT PRIVILEGES FOR ROLE zephyr IN SCHEMA public
    GRANT SELECT ON TABLES TO depgraph_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE zephyr IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO depgraph_writer;
ALTER DEFAULT PRIVILEGES FOR ROLE zephyr IN SCHEMA public
    GRANT SELECT ON SEQUENCES TO depgraph_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE zephyr IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO depgraph_writer;

-- 7. 验证
SELECT rolname, rolcanlogin FROM pg_roles
    WHERE rolname IN ('depgraph_reader', 'depgraph_writer')
    ORDER BY rolname;
