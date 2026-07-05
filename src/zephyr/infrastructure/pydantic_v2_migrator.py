# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructuredantic_v2_migrator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_pydantic_v2_migrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
M-15 PydanticV2Migrator — Pydantic V2 迁移工具
===============================================
职责：辅助项目代码从 Pydantic V1 迁移到 V2——自动检测模式、提供迁移建议、生成兼容层。
对标：bump-pydantic + pydantic-v2-migration-guide
使用方式：
    migrator = PydanticV2Migrator()
    report = migrator.scan("src/zephyr/")
    migrator.apply_migrations(report, dry_run=True)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "MigrationFinding",
    "MigrationReport",
    "PydanticV2Migrator",
]


@dataclass
class MigrationFinding:
    file_path: str
    line: int
    pattern: str
    severity: str = "medium"
    v1_code: str = ""
    v2_suggestion: str = ""


@dataclass
class MigrationReport:
    files_scanned: int = 0
    findings: list[MigrationFinding] = field(default_factory=list)
    error_files: list[str] = field(default_factory=list)

    @property
    def total_findings(self) -> int:
        return len(self.findings)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "critical")


_MIGRATION_PATTERNS: list[dict[str, str]] = [
    {
        "pattern": "class Config:",
        "severity": "high",
        "v1": "class Config:",
        "v2": "model_config = ConfigDict(...)",
        "note": "Pydantic V2 使用 model_config = ConfigDict() 替代内部 Config 类",
    },
    {
        "pattern": "schema_extra",
        "severity": "medium",
        "v1": "schema_extra",
        "v2": "json_schema_extra",
        "note": "Pydantic V2 中 schema_extra 更名为 json_schema_extra",
    },
    {
        "pattern": "orm_mode",
        "severity": "high",
        "v1": "class Config: orm_mode = True",
        "v2": "model_config = ConfigDict(from_attributes=True)",
        "note": "Pydantic V2 中 orm_mode 改为 from_attributes",
    },
    {
        "pattern": "allow_population_by_field_name",
        "severity": "medium",
        "v1": "allow_population_by_field_name",
        "v2": "populate_by_name",
        "note": "Pydantic V2 中 allow_population_by_field_name 改为 populate_by_name",
    },
    {
        "pattern": "regex=|min_items=|max_items=",
        "severity": "medium",
        "v1": "Field(regex=...) / conlist(min_items=...)",
        "v2": "Field(pattern=...) / Field(min_length=...) 在Annotated中",
        "note": "Pydantic V2 中部分 validator 参数名和用法已改变",
    },
    {
        "pattern": "@validator",
        "severity": "high",
        "v1": "@validator('field')",
        "v2": "@field_validator('field')",
        "note": "Pydantic V2 中 @validator 改为 @field_validator",
    },
    {
        "pattern": "from pydantic import BaseModel",
        "severity": "low",
        "v1": "from pydantic import BaseModel",
        "v2": "from pydantic import BaseModel  # V2兼容，无需改动",
        "note": "Pydantic V2 BaseModel 使用方式基本兼容",
        "skip": True,
    },
    {
        "pattern": "json_encoders",
        "severity": "medium",
        "v1": "json_encoders",
        "v2": "model_config = ConfigDict(ser_json_timedelta='float', ...)",
        "note": "Pydantic V2 中 json_encoders 改为 model_config 中的序列化配置",
    },
]


class PydanticV2Migrator:
    """Pydantic V2 迁移辅助工具

    自动扫描项目中的 Pydantic V1 模式并生成 V2 兼容迁移方案。
    """

    def __init__(self):
        self._patterns = _MIGRATION_PATTERNS

    def scan(
        self,
        directory: str | Path,
        pattern: str = "*.py",
    ) -> MigrationReport:
        dpath = Path(directory)
        report = MigrationReport()

        if not dpath.exists():
            return report

        for py_file in dpath.rglob(pattern):
            try:
                findings = self._scan_file(py_file)
                report.findings.extend(findings)
                report.files_scanned += 1
            except Exception as e:
                report.error_files.append(f"{py_file}: {e}")

        return report

    def _scan_file(self, filepath: Path) -> list[MigrationFinding]:
        findings: list[MigrationFinding] = []
        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return findings

        for i, line in enumerate(lines, 1):
            for pat in self._patterns:
                if pat.get("skip"):
                    continue
                if pat["pattern"] in line:
                    findings.append(
                        MigrationFinding(
                            file_path=str(filepath),
                            line=i,
                            pattern=pat["pattern"],
                            severity=pat.get("severity", "medium"),
                            v1_code=pat.get("v1", ""),
                            v2_suggestion=pat.get("v2", ""),
                        )
                    )
        return findings

    def apply_migrations(
        self,
        report: MigrationReport,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "dry_run": dry_run,
            "files_modified": 0,
            "changes": [],
            "errors": [],
        }

        by_file: dict[str, list[MigrationFinding]] = {}
        for f in report.findings:
            if f.file_path not in by_file:
                by_file[f.file_path] = []
            by_file[f.file_path].append(f)

        for filepath, findings in by_file.items():
            try:
                if dry_run:
                    for f_item in findings:
                        result["changes"].append(
                            {
                                "file": filepath,
                                "line": f_item.line,
                                "from": f_item.v1_code,
                                "to": f_item.v2_suggestion,
                            }
                        )
                    result["files_modified"] += 1
                else:
                    self._apply_to_file(filepath, findings)
                    result["files_modified"] += 1
            except Exception as e:
                result["errors"].append(f"{filepath}: {e}")

        return result

    def _apply_to_file(
        self,
        filepath: str,
        findings: list[MigrationFinding],
    ) -> None:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        for f_item in sorted(findings, key=lambda x: x.line, reverse=True):
            if f_item.v1_code and f_item.v2_suggestion:
                content = content.replace(f_item.v1_code, f_item.v2_suggestion, 1)

        tmp_path = filepath + f".{os.getpid()}.migrate.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, filepath)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    def generate_migration_checklist(self, report: MigrationReport) -> list[str]:
        checklist: list[str] = []
        if report.total_findings == 0:
            checklist.append("✅ 未发现Pydantic V1模式——代码已是V2兼容")
            return checklist

        checklist.append(f"📋 发现 {report.total_findings} 处 V1 模式待迁移")

        severity_counts: dict[str, int] = {}
        for f in report.findings:
            severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

        for sev in ("critical", "high", "medium", "low"):
            count = severity_counts.get(sev, 0)
            if count > 0:
                checklist.append(f"  - [{sev.upper()}] {count} 处")

        checklist.append("\n建议迁移步骤:")
        checklist.append("  1. 运行 migrator.apply_migrations(report, dry_run=True) 预览")
        checklist.append("  2. 确认无误后 dry_run=False 执行迁移")
        checklist.append("  3. 运行全量测试验证: pytest -x --tb=short")
        return checklist


if __name__ == "__main__":
    migrator = PydanticV2Migrator()
    report = migrator.scan("src/zephyr/")
    print(f"\nScanned {report.files_scanned} files")
    print(f"Found {report.total_findings} V1 patterns")
    for line in migrator.generate_migration_checklist(report):
        print(line)
