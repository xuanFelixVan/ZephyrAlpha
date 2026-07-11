# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] zephyr.governance.kb.integrity
# [DOMAIN] D_GOV_KB
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
# [A_module] module_id=MOD-DAT_integrity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""SHA256源码manifest + CI防篡改检测
==================================
蓝图: MOD-KB-001 7.10.3
任务: KB-INF-0049

三层完整性:
  L1-KE文件   — 每个ke-*.md的SHA256 (manifest)
  L2-KB源码   — 每个src/zephyr/governance/kb/*.py的SHA256
  L3-全局     — 整个kb包的aggregate hash

CI检查:
  python -m zephyr.knowledge.kb.integrity verify --layer 1|2|3|all
    -> 对比manifest vs 当前磁盘
    -> 发现漂移 -> exit 1 + 详细diff

Manifest文件:
  data/snapshots/kb-integrity-manifest.json
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


@dataclass
class HashEntry:
    path: str
    sha256: str
    size: int
    mtime: str


@dataclass
class Manifest:
    version: str
    generated_at: str
    layer1_kes: list[HashEntry] = field(default_factory=list)
    layer2_sources: list[HashEntry] = field(default_factory=list)
    layer3_aggregate: str = ""


@dataclass
class DriftReport:
    timestamp: str
    layer: int
    total: int
    matched: int
    mismatches: list[dict] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    is_clean: bool = True


def _get_project_root() -> Path:
    env = os.environ.get("ZEPHYR_PROJECT_ROOT")
    if env:
        return Path(env)
    return REPO_ROOT


class IntegrityGuard:
    _MANIFEST_FILE = "kb-integrity-manifest.json"
    _KE_DIR = "docs/08_knowledge/01_raw_intake"
    _KB_SRC_DIR = "src/zephyr/governance/kb"

    def __init__(self, project_root: Path | None = None):
        self._root = project_root or _get_project_root()

    @property
    def manifest_path(self) -> Path:
        snap_dir = self._root / "data" / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)
        return snap_dir / self._MANIFEST_FILE

    @property
    def ke_dir(self) -> Path:
        return self._root / self._KE_DIR

    @property
    def kb_src_dir(self) -> Path:
        return self._root / self._KB_SRC_DIR

    def generate(self) -> Manifest:
        kes = self._hash_directory(self.ke_dir, "ke-*.md")
        sources = self._hash_directory(self.kb_src_dir, "*.py")
        all_hashes = sorted([e.sha256 for e in kes] + [e.sha256 for e in sources])
        aggregate = hashlib.sha256("".join(all_hashes).encode("utf-8")).hexdigest()

        manifest = Manifest(
            version="1.0",
            generated_at=datetime.now(UTC).isoformat(),
            layer1_kes=kes,
            layer2_sources=sources,
            layer3_aggregate=aggregate,
        )
        self._save(manifest)
        return manifest

    def _save(self, manifest: Manifest) -> None:
        data = {
            "version": manifest.version,
            "generated_at": manifest.generated_at,
            "layer1_kes": [
                {"path": e.path, "sha256": e.sha256, "size": e.size, "mtime": e.mtime} for e in manifest.layer1_kes
            ],
            "layer2_sources": [
                {"path": e.path, "sha256": e.sha256, "size": e.size, "mtime": e.mtime} for e in manifest.layer2_sources
            ],
            "layer3_aggregate": manifest.layer3_aggregate,
        }
        self.manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> Manifest | None:
        if not self.manifest_path.exists():
            return None
        try:
            data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            return Manifest(
                version=data.get("version", "1.0"),
                generated_at=data.get("generated_at", ""),
                layer1_kes=[HashEntry(**e) for e in data.get("layer1_kes", [])],
                layer2_sources=[HashEntry(**e) for e in data.get("layer2_sources", [])],
                layer3_aggregate=data.get("layer3_aggregate", ""),
            )
        except Exception as e:
            logger.warning("Failed to load integrity manifest: %s", e, exc_info=True)
            return None

    def verify(self, layer: int) -> DriftReport:
        stored = self.load()
        if stored is None:
            return DriftReport(
                timestamp=datetime.now(UTC).isoformat(),
                layer=layer,
                total=0,
                matched=0,
                is_clean=False,
            )

        mismatches: list[dict] = []
        added: list[str] = []
        removed: list[str] = []

        if layer in (1, 3):
            stored_map = self._verify_layer(stored.layer1_kes, self.ke_dir, "ke-*.md")
            mismatches.extend(stored_map["mismatches"])
            added.extend([f"ke:{a}" for a in stored_map["added"]])
            removed.extend([f"ke:{r}" for r in stored_map["removed"]])

        if layer in (2, 3):
            stored_map = self._verify_layer(stored.layer2_sources, self.kb_src_dir, "*.py")
            mismatches.extend(stored_map["mismatches"])
            added.extend([f"src:{a}" for a in stored_map["added"]])
            removed.extend([f"src:{r}" for r in stored_map["removed"]])

        total = len(mismatches) + len(stored_map.get("matched", []))
        matched = stored_map.get("matched_count", 0)

        is_clean = len(mismatches) == 0 and len(added) == 0 and len(removed) == 0
        return DriftReport(
            timestamp=datetime.now(UTC).isoformat(),
            layer=layer,
            total=max(total, 1),
            matched=matched,
            mismatches=mismatches,
            added=added,
            removed=removed,
            is_clean=is_clean,
        )

    def _verify_layer(
        self,
        stored_entries: list[HashEntry],
        directory: Path,
        pattern: str,
    ) -> dict:
        stored_map: dict[str, HashEntry] = {e.path: e for e in stored_entries}
        current_entries = self._hash_directory(directory, pattern)

        mismatches: list[dict] = []
        added: list[str] = []
        matched: list[str] = []

        for ce in current_entries:
            if ce.path in stored_map:
                se = stored_map[ce.path]
                if ce.sha256 == se.sha256:
                    matched.append(ce.path)
                else:
                    mismatches.append(
                        {
                            "path": ce.path,
                            "expected": se.sha256,
                            "actual": ce.sha256,
                        }
                    )
            else:
                added.append(ce.path)

        removed = [p for p in stored_map if p not in {e.path for e in current_entries}]

        return {
            "mismatches": mismatches,
            "added": added,
            "removed": removed,
            "matched": matched,
            "matched_count": len(matched),
        }

    def _hash_directory(self, directory: Path, pattern: str) -> list[HashEntry]:
        if not directory.exists():
            return []
        entries: list[HashEntry] = []
        for f in sorted(directory.glob(pattern)):
            try:
                content = f.read_bytes()
                entries.append(
                    HashEntry(
                        path=str(f.relative_to(self._root)).replace("\\", "/"),
                        sha256=hashlib.sha256(content).hexdigest(),
                        size=len(content),
                        mtime=datetime.fromtimestamp(f.stat().st_mtime, tz=UTC).isoformat(),
                    )
                )
            except Exception as e:
                logger.warning("Failed to hash %s: %s", f, e, exc_info=True)
        return entries


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="KB Integrity Guard - SHA256 Source Manifest + CI Tamper Detection")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("generate", help="Generate fresh integrity manifest")
    v = sub.add_parser("verify", help="Verify against stored manifest")
    v.add_argument("--layer", type=int, choices=[1, 2, 3], default=3, help="Layer to verify (1=KEs, 2=sources, 3=all)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even with drifts")

    args = parser.parse_args()
    guard = IntegrityGuard()

    if args.cmd == "generate":
        manifest = guard.generate()
        print(f"Manifest generated: {len(manifest.layer1_kes)} KEs + {len(manifest.layer2_sources)} sources")
        print(f"  Aggregate: {manifest.layer3_aggregate}")
        return

    if args.cmd == "verify":
        report = guard.verify(layer=args.layer)
        if args.json:
            print(
                json.dumps(
                    {
                        "timestamp": report.timestamp,
                        "layer": report.layer,
                        "total": report.total,
                        "matched": report.matched,
                        "mismatches": report.mismatches,
                        "added": report.added,
                        "removed": report.removed,
                        "is_clean": report.is_clean,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"Integrity Verification (Layer {report.layer}):")
            print(f"  Total:     {report.total}")
            print(f"  Matched:   {report.matched}")
            print(f"  Mismatches: {len(report.mismatches)}")
            print(f"  Added:     {len(report.added)}")
            print(f"  Removed:   {len(report.removed)}")
            if report.mismatches:
                print("  Mismatched files:")
                for m in report.mismatches:
                    print(f"    {m['path']}: expected={m['expected'][:16]}..., actual={m['actual'][:16]}...")
            if report.added:
                print(f"  Added files: {report.added}")
            if report.removed:
                print(f"  Removed files: {report.removed}")
            verdict = "CLEAN" if report.is_clean else "DRIFT DETECTED"
            print(f"  Verdict: {verdict}")
        if not report.is_clean and not args.warn_only:
            sys.exit(1)
        return

    parser.print_help()


if __name__ == "__main__":
    main()