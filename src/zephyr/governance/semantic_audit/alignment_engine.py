# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §4.1
# [MODULE] zephyr.governance.semantic_audit.alignment_engine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.semantic_audit.models; zephyr.governance.semantic_audit.reference_extractor
# [CONSUMERS] issue_aggregator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 对比蓝图声明 vs 磁盘文件 vs import 引用链三元对齐；输出 alignment_score + staleness_severity
# [MODIFY-GUARD] 修改对齐规则必须同步蓝图 §4.3 对齐检测规则
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 蓝图不存在时返回空 AlignmentReport（aligned=0, zombie=0, orphan=0）
# [TESTS] tests/semantic-auditor/test_alignment_engine.py
# [A_module] module_id=MOD-GOV_alignment_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-028 — 对齐引擎 Stage 4

三元对齐检测：蓝图声明清单 vs 磁盘实际文件 vs import 引用链。
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from zephyr.governance.semantic_audit.models import AlignmentReport, Severity
from zephyr.governance.semantic_audit.reference_extractor import ReferenceExtractor

logger = logging.getLogger(__name__)

_BLUEPRINT_FILE_RE = re.compile(r"^\|\s*\d+\s*\|\s*`?([^`|]+)`?\s*\|", re.MULTILINE)
_BLUEPRINT_PATH_RE = re.compile(r"blueprint\.md$")
_ACTUAL_DISK_PATH_RE = re.compile(r"actual_disk_path:\s*\"?([^\"\n]+)\"?", re.MULTILINE)
_S01_SECTION_RE = re.compile(r"### §0\.1.*?\n(.*?)(?=### §)", re.DOTALL)


class AlignmentEngine:
    def __init__(self, project_root: str | Path = ".") -> None:
        self._root = Path(project_root).resolve()
        self._extractor = ReferenceExtractor()

    def align(self, module_id: str) -> AlignmentReport:
        blueprint_dir = self._resolve_blueprint_dir(module_id)
        if not blueprint_dir:
            blueprint_dir = self._resolve_from_file_path(module_id)
        if not blueprint_dir:
            logger.warning("Cannot resolve blueprint directory for %s", module_id)
            return AlignmentReport(
                aligned_count=0,
                zombie_count=0,
                orphan_count=0,
                alignment_score=0.0,
                staleness_severity=Severity.INFO,
                missing_files=[],
                extra_files=[],
                misregistered=[],
            )

        declared = self._load_blueprint_files(blueprint_dir)
        disk_path = self._resolve_disk_path(blueprint_dir)
        disk_files = self._scan_disk_files(disk_path)
        disk_basenames = {Path(f).name for f in disk_files}
        import_refs = self._collect_import_refs(disk_files)

        aligned = {d for d in declared if d in disk_basenames}
        missing_files = declared - disk_basenames
        extra_files = disk_basenames - declared

        aligned_count = len(aligned)
        zombie_count = len(missing_files)
        orphan_count = len(extra_files)
        total = len(declared)
        alignment_score = aligned_count / max(total, 1)

        if alignment_score < 0.5:
            staleness = Severity.RED
        elif alignment_score < 0.8:
            staleness = Severity.YELLOW
        else:
            staleness = Severity.INFO

        return AlignmentReport(
            aligned_count=aligned_count,
            zombie_count=zombie_count,
            orphan_count=orphan_count,
            alignment_score=alignment_score,
            staleness_severity=staleness,
            missing_files=sorted(missing_files),
            extra_files=sorted(extra_files),
            misregistered=sorted(self._basename_set(import_refs) - declared),
        )

    def _load_blueprint_files(self, blueprint_dir: Path) -> set[str]:
        bp_path = blueprint_dir / "blueprint.md"
        if not bp_path.exists():
            logger.warning("blueprint.md not found at %s", bp_path)
            return set()

        content = bp_path.read_text(encoding="utf-8")
        section_m = _S01_SECTION_RE.search(content)
        scan_text = section_m.group(1) if section_m else content

        files: set[str] = set()
        for m in _BLUEPRINT_FILE_RE.finditer(scan_text):
            name = m.group(1).strip()
            if name and not name.startswith("§") and not name.startswith("`"):
                files.add(name)
        return files

    def _resolve_blueprint_dir(self, module_id: str) -> Path | None:
        docs = self._root / "docs"
        if not docs.exists():
            return None

        candidates = list(docs.rglob("blueprint.md"))
        for c in candidates:
            content = c.read_text(encoding="utf-8")
            if module_id in content[:500]:
                return c.parent
        return None

    def _resolve_from_file_path(self, spec: str) -> Path | None:
        path = Path(spec)
        if not path.is_absolute():
            path = self._root / path
        if path.exists() and _BLUEPRINT_PATH_RE.search(str(path)):
            return path.parent
        bp_path = path / "blueprint.md"
        if bp_path.exists():
            return path
        return None

    def _resolve_disk_path(self, blueprint_dir: Path) -> Path:
        bp_path = blueprint_dir / "blueprint.md"
        if bp_path.exists():
            content = bp_path.read_text(encoding="utf-8")
            m = _ACTUAL_DISK_PATH_RE.search(content)
            if m:
                disk_rel = m.group(1).strip()
                disk_path = self._root / disk_rel
                if disk_path.exists():
                    return disk_path
        dir_name = blueprint_dir.name
        inferred = self._root / "src" / "zephyr" / dir_name
        if inferred.exists():
            return inferred
        inferred_underscore = self._root / "src" / "zephyr" / dir_name.replace("-", "_")
        if inferred_underscore.exists():
            return inferred_underscore
        inferred_hyphen = self._root / "src" / "zephyr" / dir_name.replace("_", "-")
        if inferred_hyphen.exists():
            return inferred_hyphen
        return self._root / "src" / "zephyr"

    def _scan_disk_files(self, disk_path: Path) -> set[str]:
        if not disk_path.exists():
            return set()

        files: set[str] = set()
        for py_file in disk_path.rglob("*.py"):
            rel = py_file.relative_to(self._root)
            files.add(str(rel).replace("\\", "/"))
        for yaml_file in disk_path.rglob("*.yaml"):
            rel = yaml_file.relative_to(self._root)
            files.add(str(rel).replace("\\", "/"))
        return files

    def _collect_import_refs(self, disk_files: set[str]) -> set[str]:
        refs: set[str] = set()
        for fp in disk_files:
            full_path = self._root / fp
            if not full_path.exists():
                continue
            extracted = self._extractor.extract(full_path)
            for dep in extracted.depends_on_targets:
                target = dep.get("target", "")
                if target:
                    refs.add(target)
            refs.update(extracted.file_paths)
        return refs

    def _basename_set(self, items: set[str]) -> set[str]:
        result: set[str] = set()
        for item in items:
            last = item.replace("\\", "/").rsplit("/", 1)[-1]
            if not last.endswith(".py"):
                last = last.rsplit(".", 1)[-1] + ".py"
            result.add(last)
        return result
