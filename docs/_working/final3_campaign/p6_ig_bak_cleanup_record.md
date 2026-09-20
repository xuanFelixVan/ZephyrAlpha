---
ttl: task_bound
completes_when: P14 终局报告落盘
---

# P6 主题四：PG 图库 ig_*_bak_* 92 表清理记录（裁定#374 ②）

- 执行会话：st-maxexec-20260920（P6 分包）｜执行日期：2026-09-20｜连接入口：`get_depgraph_pg_connection`（src/zephyr/governance/depgraph_schema.py:1594）
- 库：depgraph PostgreSQL，schema=public

## RULE-DATA-OPS 三步验证

1. **必要性**：92 张 `ig_<族>_bak_YYYYMMDD` 备份表共 658.0MB，由 `scripts/industry_graph/websearch_ingest.py cmd_backup`（L245-263）按日生成、逐日续增；全仓 grep `_bak_` 消费面=零读引用（src/ 与 scripts/ 下仅写面 cmd_backup 生成逻辑+无关 kline_daily_bak_256 标签），逐日备份零消费。
2. **真实性**：pg_class 实测（superuser 只读 SELECT）：92 表全部匹配严格正则 `^ig_[a-z0-9_]+_bak_\d{8}$`，零不合规表名；分族 12 族，日期区间 2026-09-07~2026-09-18；活表（非 bak 的 ig_*）16 张在位不受影响。
3. **可逆性**：①下方 92 表结构+行数全量导出备查（DROP 后可按列定义重建结构）；②每族保留最近 1 份（12 张，93.2MB）+当日活表 16 张不动；③DROP 范围=80 张旧份（564.8MB），逐表名单先 dry-run 核对后执行。

## 处置规则（裁定#374 ②）

每族（12 族）保留日期最近 1 份 bak；其余 DROP。保留清单（12）：

- ig_chain_bak_20260914
- ig_chunk_bak_20260914
- ig_company_edge_bak_20260914
- ig_company_metric_bak_20260914
- ig_document_bak_20260914
- ig_edge_bak_20260914
- ig_equity_edge_bak_20260914
- ig_fact_bak_20260914
- ig_node_bak_20260914
- ig_node_company_bak_20260914
- ig_product_revenue_bak_20260918
- ig_unlisted_entity_bak_20260914

## DROP 清单（80 张，dry-run 核对名单）

- ig_chain_bak_20260907
- ig_chain_bak_20260908
- ig_chain_bak_20260909
- ig_chain_bak_20260910
- ig_chain_bak_20260911
- ig_chain_bak_20260912
- ig_chain_bak_20260913
- ig_chunk_bak_20260907
- ig_chunk_bak_20260908
- ig_chunk_bak_20260909
- ig_chunk_bak_20260910
- ig_chunk_bak_20260911
- ig_chunk_bak_20260912
- ig_chunk_bak_20260913
- ig_company_edge_bak_20260907
- ig_company_edge_bak_20260908
- ig_company_edge_bak_20260909
- ig_company_edge_bak_20260910
- ig_company_edge_bak_20260911
- ig_company_edge_bak_20260912
- ig_company_edge_bak_20260913
- ig_company_metric_bak_20260907
- ig_company_metric_bak_20260908
- ig_company_metric_bak_20260909
- ig_company_metric_bak_20260910
- ig_company_metric_bak_20260911
- ig_company_metric_bak_20260912
- ig_company_metric_bak_20260913
- ig_document_bak_20260907
- ig_document_bak_20260908
- ig_document_bak_20260909
- ig_document_bak_20260910
- ig_document_bak_20260911
- ig_document_bak_20260912
- ig_document_bak_20260913
- ig_edge_bak_20260907
- ig_edge_bak_20260908
- ig_edge_bak_20260909
- ig_edge_bak_20260910
- ig_edge_bak_20260911
- ig_edge_bak_20260912
- ig_edge_bak_20260913
- ig_equity_edge_bak_20260909
- ig_equity_edge_bak_20260910
- ig_equity_edge_bak_20260911
- ig_equity_edge_bak_20260912
- ig_equity_edge_bak_20260913
- ig_fact_bak_20260907
- ig_fact_bak_20260908
- ig_fact_bak_20260909
- ig_fact_bak_20260910
- ig_fact_bak_20260911
- ig_fact_bak_20260912
- ig_fact_bak_20260913
- ig_node_bak_20260907
- ig_node_bak_20260908
- ig_node_bak_20260909
- ig_node_bak_20260910
- ig_node_bak_20260911
- ig_node_bak_20260912
- ig_node_bak_20260913
- ig_node_company_bak_20260907
- ig_node_company_bak_20260908
- ig_node_company_bak_20260909
- ig_node_company_bak_20260910
- ig_node_company_bak_20260911
- ig_node_company_bak_20260912
- ig_node_company_bak_20260913
- ig_product_revenue_bak_20260909
- ig_product_revenue_bak_20260910
- ig_product_revenue_bak_20260911
- ig_product_revenue_bak_20260912
- ig_product_revenue_bak_20260913
- ig_product_revenue_bak_20260914
- ig_unlisted_entity_bak_20260908
- ig_unlisted_entity_bak_20260909
- ig_unlisted_entity_bak_20260910
- ig_unlisted_entity_bak_20260911
- ig_unlisted_entity_bak_20260912
- ig_unlisted_entity_bak_20260913

## 92 表结构+行数导出（DROP 前采集，可逆性证据）

| 表名 | 行数 | 大小 | 列定义（列名 类型 约束） |
|---|---|---|---|
| ig_chain_bak_20260907 | 691 | 0.1MB | chain_id text NULL; name text NULL; category text NULL; version_year smallint NULL; market text NULL; status text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL |
| ig_chain_bak_20260908 | 691 | 0.1MB | chain_id text NULL; name text NULL; category text NULL; version_year smallint NULL; market text NULL; status text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL |
| ig_chain_bak_20260909 | 803 | 0.1MB | chain_id text NULL; name text NULL; category text NULL; version_year smallint NULL; market text NULL; status text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL |
| ig_chain_bak_20260910 | 816 | 0.1MB | chain_id text NULL; name text NULL; category text NULL; version_year smallint NULL; market text NULL; status text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; level smallint NULL |
| ig_chain_bak_20260911 | 833 | 0.1MB | chain_id text NULL; name text NULL; category text NULL; version_year smallint NULL; market text NULL; status text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; level smallint NULL |
| ig_chain_bak_20260912 | 887 | 0.3MB | chain_id text NULL; name text NULL; category text NULL; version_year smallint NULL; market text NULL; status text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; level smallint NULL |
| ig_chain_bak_20260913 | 887 | 0.3MB | chain_id text NULL; name text NULL; category text NULL; version_year smallint NULL; market text NULL; status text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; level smallint NULL |
| ig_chain_bak_20260914 | 895 | 0.3MB | chain_id text NULL; name text NULL; category text NULL; version_year smallint NULL; market text NULL; status text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; level smallint NULL |
| ig_chunk_bak_20260907 | 0 | 0.0MB | chunk_id text NULL; doc_id text NULL; title text NULL; doc_type text NULL; year smallint NULL; chunk_text text NULL; created_at timestamp with time zone NULL |
| ig_chunk_bak_20260908 | 0 | 0.0MB | chunk_id text NULL; doc_id text NULL; title text NULL; doc_type text NULL; year smallint NULL; chunk_text text NULL; created_at timestamp with time zone NULL |
| ig_chunk_bak_20260909 | 5200 | 3.1MB | chunk_id text NULL; doc_id text NULL; title text NULL; doc_type text NULL; year smallint NULL; chunk_text text NULL; created_at timestamp with time zone NULL |
| ig_chunk_bak_20260910 | 5200 | 3.1MB | chunk_id text NULL; doc_id text NULL; title text NULL; doc_type text NULL; year smallint NULL; chunk_text text NULL; created_at timestamp with time zone NULL |
| ig_chunk_bak_20260911 | 5200 | 3.1MB | chunk_id text NULL; doc_id text NULL; title text NULL; doc_type text NULL; year smallint NULL; chunk_text text NULL; created_at timestamp with time zone NULL |
| ig_chunk_bak_20260912 | 5200 | 3.1MB | chunk_id text NULL; doc_id text NULL; title text NULL; doc_type text NULL; year smallint NULL; chunk_text text NULL; created_at timestamp with time zone NULL |
| ig_chunk_bak_20260913 | 5200 | 3.1MB | chunk_id text NULL; doc_id text NULL; title text NULL; doc_type text NULL; year smallint NULL; chunk_text text NULL; created_at timestamp with time zone NULL |
| ig_chunk_bak_20260914 | 5200 | 3.1MB | chunk_id text NULL; doc_id text NULL; title text NULL; doc_type text NULL; year smallint NULL; chunk_text text NULL; created_at timestamp with time zone NULL |
| ig_company_edge_bak_20260907 | 58029 | 8.0MB | edge_id bigint NULL; from_symbol text NULL; to_symbol text NULL; year smallint NULL; product text NULL; weight real NULL; weight_type text NULL; source text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; from_name text NULL; to_name text NULL; amount numeric NULL; rank smallint NULL; valid_from date NULL; valid_to date NULL; as_of date NULL; evidence_type text NULL; revenue_pct real NULL; subsidiary text NULL; relevance smallint NULL; transmission_type ARRAY NULL |
| ig_company_edge_bak_20260908 | 58029 | 8.0MB | edge_id bigint NULL; from_symbol text NULL; to_symbol text NULL; year smallint NULL; product text NULL; weight real NULL; weight_type text NULL; source text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; from_name text NULL; to_name text NULL; amount numeric NULL; rank smallint NULL; valid_from date NULL; valid_to date NULL; as_of date NULL; evidence_type text NULL; revenue_pct real NULL; subsidiary text NULL; relevance smallint NULL; transmission_type ARRAY NULL |
| ig_company_edge_bak_20260909 | 58158 | 8.0MB | edge_id bigint NULL; from_symbol text NULL; to_symbol text NULL; year smallint NULL; product text NULL; weight real NULL; weight_type text NULL; source text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; from_name text NULL; to_name text NULL; amount numeric NULL; rank smallint NULL; valid_from date NULL; valid_to date NULL; as_of date NULL; evidence_type text NULL; revenue_pct real NULL; subsidiary text NULL; relevance smallint NULL; transmission_type ARRAY NULL; capacity text NULL; exclusivity text NULL; keywords ARRAY NULL |
| ig_company_edge_bak_20260910 | 58158 | 8.0MB | edge_id bigint NULL; from_symbol text NULL; to_symbol text NULL; year smallint NULL; product text NULL; weight real NULL; weight_type text NULL; source text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; from_name text NULL; to_name text NULL; amount numeric NULL; rank smallint NULL; valid_from date NULL; valid_to date NULL; as_of date NULL; evidence_type text NULL; revenue_pct real NULL; subsidiary text NULL; relevance smallint NULL; transmission_type ARRAY NULL; capacity text NULL; exclusivity text NULL; keywords ARRAY NULL |
| ig_company_edge_bak_20260911 | 58178 | 8.0MB | edge_id bigint NULL; from_symbol text NULL; to_symbol text NULL; year smallint NULL; product text NULL; weight real NULL; weight_type text NULL; source text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; from_name text NULL; to_name text NULL; amount numeric NULL; rank smallint NULL; valid_from date NULL; valid_to date NULL; as_of date NULL; evidence_type text NULL; revenue_pct real NULL; subsidiary text NULL; relevance smallint NULL; transmission_type ARRAY NULL; capacity text NULL; exclusivity text NULL; keywords ARRAY NULL |
| ig_company_edge_bak_20260912 | 58207 | 8.0MB | edge_id bigint NULL; from_symbol text NULL; to_symbol text NULL; year smallint NULL; product text NULL; weight real NULL; weight_type text NULL; source text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; from_name text NULL; to_name text NULL; amount numeric NULL; rank smallint NULL; valid_from date NULL; valid_to date NULL; as_of date NULL; evidence_type text NULL; revenue_pct real NULL; subsidiary text NULL; relevance smallint NULL; transmission_type ARRAY NULL; capacity text NULL; exclusivity text NULL; keywords ARRAY NULL |
| ig_company_edge_bak_20260913 | 58207 | 8.0MB | edge_id bigint NULL; from_symbol text NULL; to_symbol text NULL; year smallint NULL; product text NULL; weight real NULL; weight_type text NULL; source text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; from_name text NULL; to_name text NULL; amount numeric NULL; rank smallint NULL; valid_from date NULL; valid_to date NULL; as_of date NULL; evidence_type text NULL; revenue_pct real NULL; subsidiary text NULL; relevance smallint NULL; transmission_type ARRAY NULL; capacity text NULL; exclusivity text NULL; keywords ARRAY NULL |
| ig_company_edge_bak_20260914 | 58207 | 8.0MB | edge_id bigint NULL; from_symbol text NULL; to_symbol text NULL; year smallint NULL; product text NULL; weight real NULL; weight_type text NULL; source text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; from_name text NULL; to_name text NULL; amount numeric NULL; rank smallint NULL; valid_from date NULL; valid_to date NULL; as_of date NULL; evidence_type text NULL; revenue_pct real NULL; subsidiary text NULL; relevance smallint NULL; transmission_type ARRAY NULL; capacity text NULL; exclusivity text NULL; keywords ARRAY NULL |
| ig_company_metric_bak_20260907 | 235367 | 24.5MB | id bigint NULL; symbol text NULL; year smallint NULL; metric text NULL; value real NULL; value_aux real NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_company_metric_bak_20260908 | 235367 | 24.5MB | id bigint NULL; symbol text NULL; year smallint NULL; metric text NULL; value real NULL; value_aux real NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_company_metric_bak_20260909 | 235369 | 24.5MB | id bigint NULL; symbol text NULL; year smallint NULL; metric text NULL; value real NULL; value_aux real NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL; as_of date NULL; valid_from date NULL; valid_to date NULL |
| ig_company_metric_bak_20260910 | 235370 | 27.0MB | id bigint NULL; symbol text NULL; year smallint NULL; metric text NULL; value real NULL; value_aux real NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL; as_of date NULL; valid_from date NULL; valid_to date NULL |
| ig_company_metric_bak_20260911 | 235386 | 27.0MB | id bigint NULL; symbol text NULL; year smallint NULL; metric text NULL; value real NULL; value_aux real NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL; as_of date NULL; valid_from date NULL; valid_to date NULL |
| ig_company_metric_bak_20260912 | 235392 | 27.0MB | id bigint NULL; symbol text NULL; year smallint NULL; metric text NULL; value real NULL; value_aux real NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL; as_of date NULL; valid_from date NULL; valid_to date NULL |
| ig_company_metric_bak_20260913 | 235392 | 27.0MB | id bigint NULL; symbol text NULL; year smallint NULL; metric text NULL; value real NULL; value_aux real NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL; as_of date NULL; valid_from date NULL; valid_to date NULL |
| ig_company_metric_bak_20260914 | 235392 | 27.0MB | id bigint NULL; symbol text NULL; year smallint NULL; metric text NULL; value real NULL; value_aux real NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL; as_of date NULL; valid_from date NULL; valid_to date NULL |
| ig_document_bak_20260907 | 3049 | 1.9MB | doc_id text NULL; relative_path text NULL; bundle text NULL; file_name text NULL; ext text NULL; size_bytes bigint NULL; mtime timestamp with time zone NULL; file_hash text NULL; dedup_group text NULL; is_canonical boolean NULL; doc_type text NULL; title text NULL; year smallint NULL; org text NULL; market text NULL; excluded boolean NULL; exclude_reason text NULL; parse_status text NULL; extracted_text_path text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; source_root text NULL; parent_doc text NULL |
| ig_document_bak_20260908 | 3049 | 1.9MB | doc_id text NULL; relative_path text NULL; bundle text NULL; file_name text NULL; ext text NULL; size_bytes bigint NULL; mtime timestamp with time zone NULL; file_hash text NULL; dedup_group text NULL; is_canonical boolean NULL; doc_type text NULL; title text NULL; year smallint NULL; org text NULL; market text NULL; excluded boolean NULL; exclude_reason text NULL; parse_status text NULL; extracted_text_path text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; source_root text NULL; parent_doc text NULL |
| ig_document_bak_20260909 | 3050 | 1.9MB | doc_id text NULL; relative_path text NULL; bundle text NULL; file_name text NULL; ext text NULL; size_bytes bigint NULL; mtime timestamp with time zone NULL; file_hash text NULL; dedup_group text NULL; is_canonical boolean NULL; doc_type text NULL; title text NULL; year smallint NULL; org text NULL; market text NULL; excluded boolean NULL; exclude_reason text NULL; parse_status text NULL; extracted_text_path text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; source_root text NULL; parent_doc text NULL |
| ig_document_bak_20260910 | 3050 | 1.9MB | doc_id text NULL; relative_path text NULL; bundle text NULL; file_name text NULL; ext text NULL; size_bytes bigint NULL; mtime timestamp with time zone NULL; file_hash text NULL; dedup_group text NULL; is_canonical boolean NULL; doc_type text NULL; title text NULL; year smallint NULL; org text NULL; market text NULL; excluded boolean NULL; exclude_reason text NULL; parse_status text NULL; extracted_text_path text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; source_root text NULL; parent_doc text NULL |
| ig_document_bak_20260911 | 3050 | 1.9MB | doc_id text NULL; relative_path text NULL; bundle text NULL; file_name text NULL; ext text NULL; size_bytes bigint NULL; mtime timestamp with time zone NULL; file_hash text NULL; dedup_group text NULL; is_canonical boolean NULL; doc_type text NULL; title text NULL; year smallint NULL; org text NULL; market text NULL; excluded boolean NULL; exclude_reason text NULL; parse_status text NULL; extracted_text_path text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; source_root text NULL; parent_doc text NULL |
| ig_document_bak_20260912 | 3050 | 1.9MB | doc_id text NULL; relative_path text NULL; bundle text NULL; file_name text NULL; ext text NULL; size_bytes bigint NULL; mtime timestamp with time zone NULL; file_hash text NULL; dedup_group text NULL; is_canonical boolean NULL; doc_type text NULL; title text NULL; year smallint NULL; org text NULL; market text NULL; excluded boolean NULL; exclude_reason text NULL; parse_status text NULL; extracted_text_path text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; source_root text NULL; parent_doc text NULL |
| ig_document_bak_20260913 | 3050 | 1.9MB | doc_id text NULL; relative_path text NULL; bundle text NULL; file_name text NULL; ext text NULL; size_bytes bigint NULL; mtime timestamp with time zone NULL; file_hash text NULL; dedup_group text NULL; is_canonical boolean NULL; doc_type text NULL; title text NULL; year smallint NULL; org text NULL; market text NULL; excluded boolean NULL; exclude_reason text NULL; parse_status text NULL; extracted_text_path text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; source_root text NULL; parent_doc text NULL |
| ig_document_bak_20260914 | 3050 | 1.9MB | doc_id text NULL; relative_path text NULL; bundle text NULL; file_name text NULL; ext text NULL; size_bytes bigint NULL; mtime timestamp with time zone NULL; file_hash text NULL; dedup_group text NULL; is_canonical boolean NULL; doc_type text NULL; title text NULL; year smallint NULL; org text NULL; market text NULL; excluded boolean NULL; exclude_reason text NULL; parse_status text NULL; extracted_text_path text NULL; source_note text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; source_root text NULL; parent_doc text NULL |
| ig_edge_bak_20260907 | 1133 | 0.1MB | edge_id bigint NULL; from_node text NULL; to_node text NULL; edge_type text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_edge_bak_20260908 | 1133 | 0.1MB | edge_id bigint NULL; from_node text NULL; to_node text NULL; edge_type text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_edge_bak_20260909 | 1229 | 0.2MB | edge_id bigint NULL; from_node text NULL; to_node text NULL; edge_type text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_edge_bak_20260910 | 1278 | 0.2MB | edge_id bigint NULL; from_node text NULL; to_node text NULL; edge_type text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_edge_bak_20260911 | 1393 | 0.2MB | edge_id bigint NULL; from_node text NULL; to_node text NULL; edge_type text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_edge_bak_20260912 | 1400 | 0.2MB | edge_id bigint NULL; from_node text NULL; to_node text NULL; edge_type text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_edge_bak_20260913 | 1476 | 0.2MB | edge_id bigint NULL; from_node text NULL; to_node text NULL; edge_type text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; valid_to date NULL |
| ig_edge_bak_20260914 | 1542 | 0.2MB | edge_id bigint NULL; from_node text NULL; to_node text NULL; edge_type text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; valid_to date NULL |
| ig_equity_edge_bak_20260909 | 621 | 0.3MB | edge_id bigint NULL; holder text NULL; held text NULL; stake_pct numeric NULL; layer smallint NULL; relation text NULL; as_of date NULL; valid_from date NULL; valid_to date NULL; source text NULL; source_doc text NULL; evidence text NULL; created_at timestamp with time zone NULL; acquisition_cost numeric NULL; acquisition_date date NULL; voting_pct numeric NULL; control_method text NULL; holder_name text NULL; holder_country text NULL; verification text NULL |
| ig_equity_edge_bak_20260910 | 621 | 0.3MB | edge_id bigint NULL; holder text NULL; held text NULL; stake_pct numeric NULL; layer smallint NULL; relation text NULL; as_of date NULL; valid_from date NULL; valid_to date NULL; source text NULL; source_doc text NULL; evidence text NULL; created_at timestamp with time zone NULL; acquisition_cost numeric NULL; acquisition_date date NULL; voting_pct numeric NULL; control_method text NULL; holder_name text NULL; holder_country text NULL; verification text NULL |
| ig_equity_edge_bak_20260911 | 804 | 0.3MB | edge_id bigint NULL; holder text NULL; held text NULL; stake_pct numeric NULL; layer smallint NULL; relation text NULL; as_of date NULL; valid_from date NULL; valid_to date NULL; source text NULL; source_doc text NULL; evidence text NULL; created_at timestamp with time zone NULL; acquisition_cost numeric NULL; acquisition_date date NULL; voting_pct numeric NULL; control_method text NULL; holder_name text NULL; holder_country text NULL; verification text NULL |
| ig_equity_edge_bak_20260912 | 804 | 0.3MB | edge_id bigint NULL; holder text NULL; held text NULL; stake_pct numeric NULL; layer smallint NULL; relation text NULL; as_of date NULL; valid_from date NULL; valid_to date NULL; source text NULL; source_doc text NULL; evidence text NULL; created_at timestamp with time zone NULL; acquisition_cost numeric NULL; acquisition_date date NULL; voting_pct numeric NULL; control_method text NULL; holder_name text NULL; holder_country text NULL; verification text NULL |
| ig_equity_edge_bak_20260913 | 804 | 0.3MB | edge_id bigint NULL; holder text NULL; held text NULL; stake_pct numeric NULL; layer smallint NULL; relation text NULL; as_of date NULL; valid_from date NULL; valid_to date NULL; source text NULL; source_doc text NULL; evidence text NULL; created_at timestamp with time zone NULL; acquisition_cost numeric NULL; acquisition_date date NULL; voting_pct numeric NULL; control_method text NULL; holder_name text NULL; holder_country text NULL; verification text NULL |
| ig_equity_edge_bak_20260914 | 804 | 0.3MB | edge_id bigint NULL; holder text NULL; held text NULL; stake_pct numeric NULL; layer smallint NULL; relation text NULL; as_of date NULL; valid_from date NULL; valid_to date NULL; source text NULL; source_doc text NULL; evidence text NULL; created_at timestamp with time zone NULL; acquisition_cost numeric NULL; acquisition_date date NULL; voting_pct numeric NULL; control_method text NULL; holder_name text NULL; holder_country text NULL; verification text NULL |
| ig_fact_bak_20260907 | 264072 | 30.0MB | fact_id bigint NULL; subject text NULL; relation text NULL; object text NULL; value text NULL; evidence_chunk_id text NULL; confidence real NULL; as_of date NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_fact_bak_20260908 | 264072 | 30.0MB | fact_id bigint NULL; subject text NULL; relation text NULL; object text NULL; value text NULL; evidence_chunk_id text NULL; confidence real NULL; as_of date NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_fact_bak_20260909 | 264072 | 30.0MB | fact_id bigint NULL; subject text NULL; relation text NULL; object text NULL; value text NULL; evidence_chunk_id text NULL; confidence real NULL; as_of date NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_fact_bak_20260910 | 264072 | 30.0MB | fact_id bigint NULL; subject text NULL; relation text NULL; object text NULL; value text NULL; evidence_chunk_id text NULL; confidence real NULL; as_of date NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_fact_bak_20260911 | 264072 | 30.0MB | fact_id bigint NULL; subject text NULL; relation text NULL; object text NULL; value text NULL; evidence_chunk_id text NULL; confidence real NULL; as_of date NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL |
| ig_fact_bak_20260912 | 264072 | 30.0MB | fact_id bigint NULL; subject text NULL; relation text NULL; object text NULL; value text NULL; evidence_chunk_id text NULL; confidence real NULL; as_of date NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL; valid_to date NULL |
| ig_fact_bak_20260913 | 264072 | 30.0MB | fact_id bigint NULL; subject text NULL; relation text NULL; object text NULL; value text NULL; evidence_chunk_id text NULL; confidence real NULL; as_of date NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL; valid_to date NULL |
| ig_fact_bak_20260914 | 264072 | 30.0MB | fact_id bigint NULL; subject text NULL; relation text NULL; object text NULL; value text NULL; evidence_chunk_id text NULL; confidence real NULL; as_of date NULL; source text NULL; market text NULL; created_at timestamp with time zone NULL; valid_to date NULL |
| ig_node_bak_20260907 | 2939 | 0.4MB | node_id text NULL; chain_id text NULL; name text NULL; tier text NULL; aliases ARRAY NULL; description text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL |
| ig_node_bak_20260908 | 2939 | 0.4MB | node_id text NULL; chain_id text NULL; name text NULL; tier text NULL; aliases ARRAY NULL; description text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL |
| ig_node_bak_20260909 | 3211 | 0.4MB | node_id text NULL; chain_id text NULL; name text NULL; tier text NULL; aliases ARRAY NULL; description text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; child_chain_id text NULL; drill_status text NULL; function_role text NULL |
| ig_node_bak_20260910 | 3250 | 0.6MB | node_id text NULL; chain_id text NULL; name text NULL; tier text NULL; aliases ARRAY NULL; description text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; child_chain_id text NULL; drill_status text NULL; function_role text NULL |
| ig_node_bak_20260911 | 3346 | 0.6MB | node_id text NULL; chain_id text NULL; name text NULL; tier text NULL; aliases ARRAY NULL; description text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; child_chain_id text NULL; drill_status text NULL; function_role text NULL |
| ig_node_bak_20260912 | 3354 | 0.6MB | node_id text NULL; chain_id text NULL; name text NULL; tier text NULL; aliases ARRAY NULL; description text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; child_chain_id text NULL; drill_status text NULL; function_role text NULL |
| ig_node_bak_20260913 | 5279 | 0.8MB | node_id text NULL; chain_id text NULL; name text NULL; tier text NULL; aliases ARRAY NULL; description text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; child_chain_id text NULL; drill_status text NULL; function_role text NULL; valid_to date NULL |
| ig_node_bak_20260914 | 5348 | 0.8MB | node_id text NULL; chain_id text NULL; name text NULL; tier text NULL; aliases ARRAY NULL; description text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; child_chain_id text NULL; drill_status text NULL; function_role text NULL; valid_to date NULL |
| ig_node_company_bak_20260907 | 11156 | 2.0MB | id bigint NULL; node_id text NULL; symbol text NULL; role text NULL; confidence real NULL; evidence_text text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL |
| ig_node_company_bak_20260908 | 11156 | 2.0MB | id bigint NULL; node_id text NULL; symbol text NULL; role text NULL; confidence real NULL; evidence_text text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL |
| ig_node_company_bak_20260909 | 16650 | 3.2MB | id bigint NULL; node_id text NULL; symbol text NULL; role text NULL; confidence real NULL; evidence_text text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; valid_from date NULL; valid_to date NULL; pit_strength text NULL |
| ig_node_company_bak_20260910 | 16698 | 3.7MB | id bigint NULL; node_id text NULL; symbol text NULL; role text NULL; confidence real NULL; evidence_text text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; valid_from date NULL; valid_to date NULL; pit_strength text NULL |
| ig_node_company_bak_20260911 | 16900 | 4.0MB | id bigint NULL; node_id text NULL; symbol text NULL; role text NULL; confidence real NULL; evidence_text text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; valid_from date NULL; valid_to date NULL; pit_strength text NULL |
| ig_node_company_bak_20260912 | 16962 | 4.0MB | id bigint NULL; node_id text NULL; symbol text NULL; role text NULL; confidence real NULL; evidence_text text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; valid_from date NULL; valid_to date NULL; pit_strength text NULL |
| ig_node_company_bak_20260913 | 18349 | 4.1MB | id bigint NULL; node_id text NULL; symbol text NULL; role text NULL; confidence real NULL; evidence_text text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; valid_from date NULL; valid_to date NULL; pit_strength text NULL |
| ig_node_company_bak_20260914 | 18616 | 4.2MB | id bigint NULL; node_id text NULL; symbol text NULL; role text NULL; confidence real NULL; evidence_text text NULL; source_doc text NULL; market text NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; valid_from date NULL; valid_to date NULL; pit_strength text NULL |
| ig_product_revenue_bak_20260909 | 0 | 0.0MB | id bigint NULL; symbol text NULL; year smallint NULL; product text NULL; revenue_pct real NULL; node_ref text NULL; source text NULL; source_doc text NULL; evidence text NULL; as_of date NULL; created_at timestamp with time zone NULL |
| ig_product_revenue_bak_20260910 | 0 | 0.0MB | id bigint NULL; symbol text NULL; year smallint NULL; product text NULL; revenue_pct real NULL; node_ref text NULL; source text NULL; source_doc text NULL; evidence text NULL; as_of date NULL; created_at timestamp with time zone NULL |
| ig_product_revenue_bak_20260911 | 0 | 0.0MB | id bigint NULL; symbol text NULL; year smallint NULL; product text NULL; revenue_pct real NULL; node_ref text NULL; source text NULL; source_doc text NULL; evidence text NULL; as_of date NULL; created_at timestamp with time zone NULL |
| ig_product_revenue_bak_20260912 | 52404 | 14.5MB | id bigint NULL; symbol text NULL; year smallint NULL; product text NULL; revenue_pct real NULL; node_ref text NULL; source text NULL; source_doc text NULL; evidence text NULL; as_of date NULL; created_at timestamp with time zone NULL |
| ig_product_revenue_bak_20260913 | 52404 | 14.5MB | id bigint NULL; symbol text NULL; year smallint NULL; product text NULL; revenue_pct real NULL; node_ref text NULL; source text NULL; source_doc text NULL; evidence text NULL; as_of date NULL; created_at timestamp with time zone NULL |
| ig_product_revenue_bak_20260914 | 52404 | 14.5MB | id bigint NULL; symbol text NULL; year smallint NULL; product text NULL; revenue_pct real NULL; node_ref text NULL; source text NULL; source_doc text NULL; evidence text NULL; as_of date NULL; created_at timestamp with time zone NULL |
| ig_product_revenue_bak_20260918 | 52404 | 14.5MB | id bigint NULL; symbol text NULL; year smallint NULL; product text NULL; revenue_pct real NULL; node_ref text NULL; source text NULL; source_doc text NULL; evidence text NULL; as_of date NULL; created_at timestamp with time zone NULL |
| ig_unlisted_entity_bak_20260908 | 7 | 0.0MB | ue_id text NULL; name text NULL; country text NULL; status text NULL; listed_symbol text NULL; source_doc text NULL; as_of date NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL |
| ig_unlisted_entity_bak_20260909 | 13983 | 2.7MB | ue_id text NULL; name text NULL; country text NULL; status text NULL; listed_symbol text NULL; source_doc text NULL; as_of date NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL |
| ig_unlisted_entity_bak_20260910 | 13985 | 2.7MB | ue_id text NULL; name text NULL; country text NULL; status text NULL; listed_symbol text NULL; source_doc text NULL; as_of date NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL |
| ig_unlisted_entity_bak_20260911 | 14070 | 2.8MB | ue_id text NULL; name text NULL; country text NULL; status text NULL; listed_symbol text NULL; source_doc text NULL; as_of date NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; covered boolean NULL |
| ig_unlisted_entity_bak_20260912 | 14070 | 2.8MB | ue_id text NULL; name text NULL; country text NULL; status text NULL; listed_symbol text NULL; source_doc text NULL; as_of date NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; covered boolean NULL |
| ig_unlisted_entity_bak_20260913 | 14070 | 2.8MB | ue_id text NULL; name text NULL; country text NULL; status text NULL; listed_symbol text NULL; source_doc text NULL; as_of date NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; covered boolean NULL |
| ig_unlisted_entity_bak_20260914 | 14070 | 2.8MB | ue_id text NULL; name text NULL; country text NULL; status text NULL; listed_symbol text NULL; source_doc text NULL; as_of date NULL; created_at timestamp with time zone NULL; updated_at timestamp with time zone NULL; covered boolean NULL |

## DROP 执行记录（P6 续班会话，2026-09-20）

1. **前置核实**：read_only 连接实测 bak 表计数=92（未执行态）；keep 清单 12 张全部在位；活表 ig_*（非 bak）16 张在位。
2. **dry-run 核对**：由 PG 实时 pg_tables 计算待删集合（live_bak − keep=80 张），与 `.runtime/tmp/p6_drop_list.txt` 逐表比对：对称差=∅（mismatch_vs_file=[]），80 张全部匹配严格正则 `^ig_[a-z0-9_]+_bak_\d{8}$`。
3. **执行**：单事务（BEGIN→80×`DROP TABLE IF EXISTS public.<t> CASCADE`→COMMIT），连接 `get_depgraph_pg_connection(superuser=True, read_only=False, autocommit=False)`。
4. **执行后计数对照（红证）**：

| 指标 | 执行前 | 执行后 |
|------|--------|--------|
| `ig_*_bak_*` 表数 | 92 | **12**（=keep 清单全量） |
| 活表 ig_*（非 bak） | 16 | 16（未受影响） |
| public schema 总表数 | — | 87 |

5. **结论**：80 张旧份（≈564.8MB）已 DROP；12 族各留最近 1 份+16 张活表完好；结构导出（上节）保可逆性。收口完成。
