# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/base.py | §
# [MODULE] scripts.governance._shared.base
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
base.py — 审计脚本基类

对标 SCRIPT-QUALITY-001 多项条款的根因修复：
  D-B-02: main() 必须声明 -> None（基类强制约束）
  D-D-04: 同一概念只在一处定义（REPO_ROOT/EXCLUDE_DIRS 由基类提供）
  D-D-05: 禁止跨脚本复制粘贴逻辑（共享方法集中到基类）
  D-D-07: 禁止本地重定义 _shared API（基类提供 iter_files/add_finding）
  D-D-08: 禁止 os.walk + 手动 EXCLUDE_DIRS（基类提供 iter_files）
  D-G-01a: 路径从项目根推导（基类统一 REPO_ROOT）
  D-A-01: UTF-8 stdout 强制重声明（基类自动调用）

新编写的治理审计脚本**推荐**继承此基类，只需实现 check() 方法。
存量脚本可在后续重构中逐步迁移，**不强制**一次性全量改写。

Usage:
    class MyChecker(BaseAuditScript):
        def check(self) -> None:
            for f in self.iter_files(self.repo_root / "src", extensions=SCAN_EXTENSIONS_PY):
                content = f.read_text(encoding="utf-8", errors="replace")
                if "bad_pattern" in content:
                    self.add_finding(
                        dimension=Dimension.D7,
                        severity=Severity.MEDIUM,
                        target_file=str(f.relative_to(self.repo_root)),
                        description="发现 bad_pattern",
                    )

    if __name__ == "__main__":
        MyChecker().run()
"""

from __future__ import annotations

import argparse
import sys
from abc import ABC, abstractmethod
from pathlib import Path

from _shared.constants import REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

sys.path.insert(0, str(REPO_ROOT / "src"))
try:
    from zephyr.infrastructure.finding import (
        BlastRadius,
        Dimension,
        Finding,
        FindingCollection,
        RemediationAction,
        Severity,
    )

    _FINDING_AVAILABLE = True
except ImportError:
    _FINDING_AVAILABLE = False


class BaseAuditScript(ABC):
    """所有治理脚本的基类。

    子类只需实现 check() 方法，通过 self.add_finding() 报告发现。
    基类自动处理：
    - UTF-8 编码重声明
    - --warn-only 参数解析
    - 退出码（0=通过 / 1=有发现 / 2=异常）
    - Finding Schema JSONL 输出（如果可用）
    - 统一的 iter_files() 目录遍历
    """

    def __init__(self) -> None:
        ensure_utf8_stdout()
        self.repo_root: Path = REPO_ROOT
        self.warn_only: bool = False
        self._findings_raw: list[dict] = []
        self._collection: FindingCollection | None = FindingCollection() if _FINDING_AVAILABLE else None

    def iter_files(
        self,
        root: Path | None = None,
        extensions: frozenset[str] | None = None,
        exclude_dirs: frozenset[str] | None = None,
        exclude_files: frozenset[str] | None = None,
    ) -> list[Path]:
        """递归遍历目录，返回符合条件的文件路径列表。

        对标 D-D-08：禁止 os.walk + 手动 EXCLUDE_DIRS，必须使用此方法。

        Args:
            root: 遍历根目录，默认 self.repo_root
            extensions: 允许的文件扩展名集合
            exclude_dirs: 额外排除的目录名集合（会合并到默认 EXCLUDE_DIRS）
            exclude_files: 排除的文件名集合
        """
        return iter_files(
            root or self.repo_root,
            extensions=extensions,
            exclude_dirs=exclude_dirs,
            exclude_files=exclude_files,
        )

    def add_finding(
        self,
        dimension: Dimension,
        severity: Severity,
        target_file: str,
        description: str,
        category: str = "",
        evidence: str = "",
        target_line_range: str = "",
        blast_radius: BlastRadius | None = None,
        remediation_action: RemediationAction | None = None,
        remediation_priority: str = "P2",
    ) -> None:
        """添加一个审计发现。

        对标 D-D-05：统一 Finding 构造，禁止各脚本自行 print + 正则解析。

        Args:
            dimension: 审计维度（D1-D12）
            severity: 严重度（CRITICAL/HIGH/MEDIUM/LOW/INFO）
            target_file: 目标文件路径（相对项目根）
            description: 人类可读描述
            category: 分类标签
            evidence: 原始证据
            target_line_range: 目标行范围
            blast_radius: 影响半径
            remediation_action: 修复动作
            remediation_priority: 修复优先级
        """
        entry = {
            "dimension": dimension if isinstance(dimension, str) else dimension.value,
            "severity": severity if isinstance(severity, str) else severity.value,
            "target_file": target_file,
            "description": description,
            "category": category,
            "evidence": evidence,
            "target_line_range": target_line_range,
            "remediation_priority": remediation_priority,
        }
        self._findings_raw.append(entry)

        if _FINDING_AVAILABLE and self._collection is not None:
            br = blast_radius or BlastRadius.FILE
            ra = remediation_action or RemediationAction.FIX
            cat = category or f"{dimension.label} — {type(self).__name__}"
            f = Finding(
                dimension=dimension,
                severity=severity,
                category=cat,
                target_file=target_file,
                description=description,
                evidence=evidence,
                target_line_range=target_line_range,
                blast_radius=br,
                remediation_action=ra,
                remediation_priority=remediation_priority,
            )
            self._collection.add(f)

    def print_finding(
        self,
        priority_tag: str,
        target_file: str,
        description: str,
    ) -> None:
        """以人类可读格式打印一个发现到 stderr。

        保持与 run_all.py 正则解析的兼容性。
        格式：[P0] path/to/file: 描述

        Args:
            priority_tag: 优先级标签（P0/P1/P2/P3）
            target_file: 目标文件路径
            description: 描述文本
        """
        print(f"[{priority_tag}] {target_file}: {description}", file=sys.stderr)

    @property
    def finding_count(self) -> int:
        """当前已收集的发现数量。"""
        return len(self._findings_raw)

    @property
    def has_findings(self) -> bool:
        """是否存在任何发现。"""
        return self.finding_count > 0

    def has_critical_or_high(self) -> bool:
        """是否存在 CRITICAL 或 HIGH 严重度的发现。"""
        for f in self._findings_raw:
            sev = f.get("severity", "")
            if sev in ("CRITICAL", "HIGH"):
                return True
        return False

    @abstractmethod
    def check(self) -> None:
        """子类实现检查逻辑。

        通过 self.add_finding() 报告发现，
        通过 self.iter_files() 遍历文件，
        通过 self.print_finding() 打印人类可读输出。
        """
        ...

    @property
    def collection(self) -> FindingCollection | None:
        return self._collection

    def run(self) -> None:
        """入口——解析参数、执行检查、输出结果。

        对标 D-B-02：main() 声明 -> None，退出码通过 sys.exit() 返回。

        --jsonl: 将 Finding Schema 结构化数据写为 JSONL 到 stdout（一行一个 JSON）
        --jsonl-file: 将 JSONL 写入指定文件（不输出到 stdout）
        """
        parser = argparse.ArgumentParser(description=self.__class__.__doc__ or "")
        parser.add_argument("--warn-only", action="store_true", help="警告模式：发现不阻塞（exit 0）")
        parser.add_argument("--jsonl", action="store_true", help="输出结构化 JSONL（Finding Schema）到 stdout")
        parser.add_argument("--jsonl-file", type=str, default="", help="JSONL 输出文件路径（不指定则输出到 stdout）")
        args = parser.parse_args()
        self.warn_only = args.warn_only

        try:
            self.check()
        except Exception as exc:
            print(f"❌ 脚本异常: {exc}", file=sys.stderr)
            sys.exit(2)

        if args.jsonl or args.jsonl_file:
            self._emit_jsonl(args.jsonl_file or "")

        if self.has_findings:
            print(f"\n  共 {self.finding_count} 个发现", file=sys.stderr)

        if self.warn_only:
            sys.exit(0)
        sys.exit(1 if self.has_findings else 0)

    def _emit_jsonl(self, file_path: str = "") -> None:
        if _FINDING_AVAILABLE and self._collection is not None:
            jl = self._collection.to_jsonl()
        else:
            import json

            jl = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in self._findings_raw)

        if file_path:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            Path(file_path).write_text(jl, encoding="utf-8")
        else:
            sys.stdout.write(jl)
            sys.stdout.flush()
