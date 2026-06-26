---
module_id: KE-3579---------g1-ingest-yaml-000
title: 4.1.2 检查项（对应 `g1-ingest.yaml`）
category: governance
ttl: permanent
---

# 4.1.2 检查项（对应 `g1-ingest.yaml`）

4.1.2 检查项（对应 `g1-ingest.yaml`）

| ID | 检查名 | 类型 | 级别 | 阈值/参数 | on_failure |
|----|-------|------|:---:|----------|-----------|
| G1-C00 | `no_deprecated_path` | `path_blacklist` | **P0** | `_legacy/ ARCHIVE/ deprecated/ _trash/ zephyralpha-1-0/ old_tree/ __OLD__` | `reject` |
| G1-C01 | `file_exists` | `condition` | **P0** | `os.path.exists + R_OK` | `reject` |
| G1-C02 | `encoding_compliant` | `encoding` | **P0** | UTF-8 + no BOM | `reject` |
| G1-C03 | `line_ending_compliant` | `line_ending` | P1 | 无 CRLF | `auto_fix`（转换为 LF）|
| G1-C04 | `frontmatter_present` | `frontmatter` | **P0** | 必须有 `---` 分隔块 | `reject` |
| G1-C05 | `frontmatter_required_fields` | `frontmatter` | **P0** | `doc_type, title, version, status, date, owner, ttl` | `reject` |
| G1-C06 | `file_size_within_limit` | `content_length` | P1 | ≤ 512 KB（.md）| `flag` |
| G1-C07 | `no_binary_content` | `content_quality` | **P0** | `chardet` 文本检测通过 | `reject` |
