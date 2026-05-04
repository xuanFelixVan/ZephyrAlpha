# 贡献指南（Contributing）

本仓库以 **个人 Owner + AI 辅助** 为主。AI 操作准则详见 [AGENTS.md](AGENTS.md)。

## 代码与风格

- Python **3.10+**
- 格式化/Lint：`ruff`（替代 `black` + `isort`）
- 类型检查：`mypy`
- 提交前运行 `pytest`

## PR 约定

- **范围聚焦**：单 PR 解决一类问题
- **文档登记**：新建文件须在 `master-document-inventory.yaml` 中登记
- **SSoT 验证**：提交前运行 `python scripts/governance/d5_architecture/validate_ssot.py`
