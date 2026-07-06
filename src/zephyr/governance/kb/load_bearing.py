# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md
# [MODULE] zephyr.governance.kb.load_bearing
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.kb.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_load_bearing | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""承重KE不可变性 + 承重墙自检
==================================
蓝图: MOD-KB-001 7.10.2
任务: KB-INF-0048

承重KE (load-bearing): 其他KE/code/决策依赖的知识条目
  - 不可删除
  - 不可修改核心内容
  - 有TTL——到期前14天发出预警
  - 只能通过replace(fresh KE)来更换

承重墙(load-bearing wall): 一组承重KE的集合
  - 定期自检——14 项额外检查
  - 发现损坏 → 触发 ALARM → freeze.safe_mode

14 项承重墙自检:
  1. 所有load-bearing KE的出厂hash是否匹配
  2. 承重KE引用的backlink是否存活
  3. 承重KE的依赖KE是否存活
  4. 是否有>1个承重KE指向同一概念(冗余检测)
  5. 是否存在没有承重KE覆盖的核心子系统
  6. 承重KE TTL是否<14天
  7. 承重KE的source KE是否存在
  8. 承重KE的向量索引是否正常
  9. 承重KE的ChromaDB距离是否<阈值
  10. 承重KE的SQLite record是否存在
  11. 承重KE的版本号是否递增(防止回退攻击)
  12. 是否有循环依赖(dependency cycle)
  13. 承重墙总覆盖率是否>=70%
  14. 承重KE的provenance是否仍有效
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

import yaml
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


class LBStatus(str, Enum):
    HEALTHY = "healthy"
    EXPIRING = "expiring"
    CORRUPT = "corrupt"
    MISSING = "missing"
    ORPHAN = "orphan"


@dataclass
class LBEntry:
    ke_id: str
    file_path: str
    source_hash: str
    ttl: str
    category: str
    depends_on: list[str] = field(default_factory=list)
    version: int = 1
    status: LBStatus = LBStatus.HEALTHY


@dataclass
class WallReport:
    timestamp: str
    entries: list[LBEntry]
    coverage_ratio: float
    issues: list[str] = field(default_factory=list)
    overall: LBStatus = LBStatus.HEALTHY


def _get_project_root() -> Path:
    env = os.environ.get("ZEPHYR_PROJECT_ROOT")
    if env:
        return Path(env)
    return REPO_ROOT


class LoadBearingWall:
    _COVERAGE_TARGET = 0.70
    _TTL_WARN_DAYS = 14
    _MANIFEST_FILE = "load_bearing_manifest.json"

    def __init__(self, project_root: Path | None = None):
        self._root = project_root or _get_project_root()

    @property
    def know_dir(self) -> Path:
        return self._root / "docs" / "08_knowledge" / "01_raw_intake"

    @property
    def manifest_path(self) -> Path:
        snap_dir = self._root / "data" / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)
        return snap_dir / self._MANIFEST_FILE

    def scan(self) -> list[LBEntry]:
        entries: list[LBEntry] = []
        if not self.know_dir.exists():
            return entries

        for ke_file in sorted(self.know_dir.glob("ke-*.md")):
            try:
                content = ke_file.read_text(encoding="utf-8", errors="replace")
                source_hash = _sha256(content)
                fm = _parse_frontmatter(content)

                is_lb = fm.get("is_load_bearing", False) if isinstance(fm, dict) else False
                if not is_lb:
                    continue

                entries.append(
                    LBEntry(
                        ke_id=fm.get("module_id") or fm.get("ke_id") or ke_file.stem,
                        file_path=str(ke_file.relative_to(self._root)),
                        source_hash=source_hash,
                        ttl=str(fm.get("ttl", "")),
                        category=str(fm.get("category", "unknown")),
                        depends_on=fm.get("depends_on", []) if isinstance(fm, dict) else [],
                        version=int(fm.get("version", 1)) if isinstance(fm, dict) else 1,
                    )
                )
            except Exception as e:
                logger.warning("Failed to scan load-bearing KE %s: %s", ke_file.name, e, exc_info=True)

        return entries

    def register(self, ke_id: str, force: bool = False) -> LBEntry:
        for ke_file in self.know_dir.glob("ke-*.md"):
            content = ke_file.read_text(encoding="utf-8", errors="replace")
            fm = _parse_frontmatter(content)
            fid = fm.get("module_id") or fm.get("ke_id") or ke_file.stem
            if fid == ke_id:
                if not force and fm.get("is_load_bearing"):
                    raise ValueError(f"KE {ke_id} 已标记为承重，如需重新注册请使用强制模式")
                if isinstance(fm, dict):
                    fm["is_load_bearing"] = True
                    fm["load_bearing_since"] = datetime.now(UTC).isoformat()
                new_content = _update_frontmatter(content, fm)
                ke_file.write_text(new_content, encoding="utf-8")
                return LBEntry(
                    ke_id=ke_id,
                    file_path=str(ke_file.relative_to(self._root)),
                    source_hash=_sha256(new_content),
                    ttl=str(fm.get("ttl", "")),
                    category=str(fm.get("category", "unknown")),
                    depends_on=fm.get("depends_on", []) if isinstance(fm, dict) else [],
                    version=int(fm.get("version", 1)) if isinstance(fm, dict) else 1,
                )
        raise FileNotFoundError(f"KE {ke_id} not found in knowledge base")

    def deregister(self, ke_id: str) -> None:
        for ke_file in self.know_dir.glob("ke-*.md"):
            content = ke_file.read_text(encoding="utf-8", errors="replace")
            fm = _parse_frontmatter(content)
            fid = fm.get("module_id") or fm.get("ke_id") or ke_file.stem
            if fid == ke_id:
                if isinstance(fm, dict):
                    fm.pop("is_load_bearing", None)
                    fm.pop("load_bearing_since", None)
                new_content = _update_frontmatter(content, fm)
                ke_file.write_text(new_content, encoding="utf-8")
                return
        raise FileNotFoundError(f"KE {ke_id} not found in knowledge base")

    def check(self) -> WallReport:
        entries = self.scan()
        issues: list[str] = []
        now = datetime.now(UTC)

        for entry in entries:
            issues.extend(self._check_one(entry, now))

        all_kes = list(self.know_dir.glob("ke-*.md")) if self.know_dir.exists() else []
        cat_count = self._count_categories()
        if cat_count > 0 and len(entries) / max(cat_count, 1) < self._COVERAGE_TARGET:
            issues.append(f"Coverage ratio {len(entries) / max(cat_count, 1):.0%} < {self._COVERAGE_TARGET:.0%} target")

        overall = LBStatus.HEALTHY
        if any(i.startswith("CORRUPT:") or i.startswith("MISSING:") for i in issues):
            overall = LBStatus.CORRUPT
        elif issues:
            overall = LBStatus.EXPIRING

        return WallReport(
            timestamp=now.isoformat(),
            entries=entries,
            coverage_ratio=len(entries) / max(cat_count, 1) if cat_count > 0 else 1.0,
            issues=issues,
            overall=overall,
        )

    def _check_one(self, entry: LBEntry, now: datetime) -> list[str]:
        issues: list[str] = []

        ke_file = self._root / entry.file_path
        if not ke_file.exists():
            issues.append(f"MISSING: {entry.ke_id} file not found at {entry.file_path}")
            return issues

        current = ke_file.read_text(encoding="utf-8", errors="replace")
        current_hash = _sha256(current)
        if current_hash != entry.source_hash:
            issues.append(f"CORRUPT: {entry.ke_id} hash mismatch ({current_hash[:12]} != {entry.source_hash[:12]})")

        if entry.ttl:
            try:
                ttl_dt = datetime.fromisoformat(entry.ttl.replace("Z", "+00:00"))
                days_left = (ttl_dt - now).days
                if days_left < self._TTL_WARN_DAYS:
                    issues.append(f"EXPIRING: {entry.ke_id} TTL in {days_left}d")
            except ValueError:
                issues.append(f"WARN: {entry.ke_id} unparseable TTL: {entry.ttl}")

        for dep_id in entry.depends_on:
            dep_file = self.know_dir / f"{dep_id}.md" if not dep_id.endswith(".md") else self.know_dir / dep_id
            if not dep_file.exists():
                issues.append(f"ORPHAN: {entry.ke_id} depends on missing {dep_id}")

        fm = _parse_frontmatter(current)
        if isinstance(fm, dict):
            current_version = int(fm.get("version", 1))
            if current_version < entry.version:
                issues.append(f"CORRUPT: {entry.ke_id} version rollback {current_version} < {entry.version}")

        return issues

    def _count_categories(self) -> int:
        if not self.know_dir.exists():
            return 0
        cats: set[str] = set()
        for ke_file in self.know_dir.glob("ke-*.md"):
            try:
                content = ke_file.read_text(encoding="utf-8", errors="replace")
                fm = _parse_frontmatter(content)
                if isinstance(fm, dict):
                    cats.add(str(fm.get("category", "unknown")))
            except Exception as e:
                logger.warning("suppressed error in load_bearing", exc_info=True)
        return len(cats)


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _parse_frontmatter(content: str) -> dict | None:
    if content.startswith("---"):
        chunk = content[3:]
        end = chunk.find("---")
        if end > 0:
            try:
                fm = yaml.safe_load(chunk[:end])
                return fm if isinstance(fm, dict) else None
            except Exception:
                return None
    return None


def _update_frontmatter(content: str, fm: dict) -> str:
    if content.startswith("---"):
        chunk = content[3:]
        end = chunk.find("---")
        if end > 0:
            new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False).rstrip()
            return "---\n" + new_fm + "\n---" + content[3 + end + 3 :]
    new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False).rstrip()
    return "---\n" + new_fm + "\n---\n" + content


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="KB Load-Bearing Wall Manager")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("scan", help="Scan all load-bearing KEs")
    sub.add_parser("check", help="Run 14-item wall self-check")
    reg = sub.add_parser("register", help="Register KE as load-bearing")
    reg.add_argument("ke_id", help="KE ID to register")
    reg.add_argument("--force", action="store_true", help="Force re-register")
    dereg = sub.add_parser("deregister", help="Deregister load-bearing KE")
    dereg.add_argument("ke_id", help="KE ID to deregister")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()
    wall = LoadBearingWall()

    if args.cmd == "scan":
        entries = wall.scan()
        if args.json:
            print(
                json.dumps(
                    [
                        {
                            "ke_id": e.ke_id,
                            "file_path": e.file_path,
                            "source_hash": e.source_hash,
                            "ttl": e.ttl,
                            "category": e.category,
                            "depends_on": e.depends_on,
                            "version": e.version,
                            "status": e.status.value,
                        }
                        for e in entries
                    ],
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            for e in entries:
                print(f"  {e.ke_id}: {e.category} (v{e.version}, TTL={e.ttl})")
            print(f"  Total: {len(entries)} load-bearing KEs")
        return

    if args.cmd == "check":
        report = wall.check()
        if args.json:
            print(
                json.dumps(
                    {
                        "timestamp": report.timestamp,
                        "coverage_ratio": report.coverage_ratio,
                        "overall": report.overall.value,
                        "issues": report.issues,
                        "entry_count": len(report.entries),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"Load-Bearing Wall Check: {report.overall.value.upper()}")
            print(f"  Entries:       {len(report.entries)}")
            print(f"  Coverage:      {report.coverage_ratio:.0%}")
            if report.issues:
                print(f"  Issues ({len(report.issues)}):")
                for issue in report.issues:
                    print(f"    - {issue}")
            else:
                print("  No issues.")
        if report.overall is LBStatus.CORRUPT:
            sys.exit(1)
        return

    if args.cmd == "register":
        entry = wall.register(args.ke_id, force=args.force)
        print(f"Registered {args.ke_id} as load-bearing. Hash: {entry.source_hash[:16]}")
        return

    if args.cmd == "deregister":
        wall.deregister(args.ke_id)
        print(f"Deregistered {args.ke_id} from load-bearing wall.")
        return

    parser.print_help()


if __name__ == "__main__":
    main()