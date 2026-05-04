"""D3 元数据合规 — Markdown/YAML 文档元数据（frontmatter）合规性审计。

检查项：
- YAML frontmatter 必填字段（doc_type / status / version / title）
- 命名规范一致性校验
- 版本号 semver 格式 + 状态受控词表校验
- 登记表/注册表与索引文件一致性
"""