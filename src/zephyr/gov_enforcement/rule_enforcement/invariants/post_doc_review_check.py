# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §16
# [MODULE] zephyr.gov_enforcement.rule_enforcement.invariants.post_doc_review_check
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS] gate_engine.py (ct=="post_doc_review_check"); project_rules.md 关门步骤12
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 不立即删除待规格化项；标记数>=3触发规格化流程
# [MODIFY-GUARD] trae_030_doc_numbering_metadata.yaml §1.2; post_doc_review.yaml
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] modified_files.json不存在->PASS(无文档可审查); 解析失败->RED
# [TESTS] tests/test_post_doc_review.py
# [A_module] module_id=MOD-GOV_post_doc_review_check | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
PostDocReviewScanner — Session 关门时文档内容审查扫描器。

实现 trae_030 §1.2 执行后文档审查协议：
- 按 §0 时态判定 + §1 可删清单 + GOV-DOC-016 纯陈述原则
- 扫描过程陈述/噪音/冲突
- 标记"待规格化"（不立即删除）
- 标记数>=3 触发规格化流程
"""

import json
import logging
import re
import subprocess
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

__all__: list[str] = [
    "DocReviewFinding",
    "DocReviewReport",
    "GitUnavailableError",
    "PostDocReviewScanner",
    "TamperingError",
]

# session_id 合法字符——只允许字母/数字/下划线/连字符（防路径遍历 R7）
_SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_\-]+$")

# 文件大小上限 5MB（防超大文件内存耗尽 R9）
_MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

# 单行最大长度 10000 字符（防 ReDoS R8）
_MAX_LINE_LENGTH = 10000

# R1 防御：commit hash 校验（40位十六进制，防命令注入）
_COMMIT_HASH_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class GitUnavailableError(Exception):
    """git 不可用时抛出——门禁必须 RED，不允许降级到自报告。"""
    error_code = "ZA-GV-0039"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class TamperingError(Exception):
    """检测到 modified_files.json 篡改时抛出。"""
    error_code = "ZA-GV-0040"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


# trae_030 §1 可删清单——文化类比对标段
_CULTURAL_BENCHMARK_PATTERNS: list[str] = [
    r"对标\s*K8s",
    r"对标\s*ITIL",
    r"对标\s*Unix",
    r"对标\s*OpenAI",
    r"对标\s*Anthropic",
    r"对标\s*Cursor",
    r"对标\s*Rails",
    r"对标\s*航空业",
    r"对标\s*法庭",
    r"对标\s*Git",
    r"对标\s*kubectl",
]

# trae_030 §1 可删清单——AI 意识植入散文
_AI_CONSCIOUSNESS_PATTERNS: list[str] = [
    r"你创建的每一个",
    r"你写下的每一",
    r"作为AI",
    r"你的使命",
    r"你的职责是",
    r"你将成为",
]

# trae_030 §1 可删清单——过渡/桥梁句
_TRANSITION_PATTERNS: list[str] = [
    r"接下来让我们看看",
    r"下面我们来看",
    r"让我们一起来",
    r"首先.{0,10}然后.{0,10}最后",
]

# trae_030 §0 时态判定——过程陈述（过去时态）
_PROCESS_STATEMENT_PATTERNS: list[str] = [
    r"之前是.{0,20}现在改为",
    r"原来是.{0,20}现在",
    r"曾.{0,10}使用",
    r"已改为",
    r"已更新为",
    r"已变更为",
]

# GOV-DOC-016 纯陈述原则——否定陈述（已废止/已取代/旧定义）
_NEGATIVE_STATEMENT_PATTERNS: list[str] = [
    r"已废止",
    r"已取代",
    r"旧定义",
    r"不再使用",
    r"已弃用",
    r"已删除的",
    r"历史版本",
]

# trae_030 §1 可删清单——修订记录/变更历史（在正文中，不在 git log）
_REVISION_HISTORY_PATTERNS: list[str] = [
    r"修订记录",
    r"变更历史",
    r"修改记录",
    r"更新历史",
]

# 待规格化阈值——trae_030 §1.2
_REGULARIZATION_THRESHOLD: int = 3

# 扫描的文件扩展名
_SCANNABLE_EXTENSIONS: frozenset[str] = frozenset({".md", ".yaml", ".yml"})


@dataclass
class DocReviewFinding:
    """单个待规格化项。"""

    file_path: str
    line_number: int
    issue_type: str  # process_statement | noise | conflict | negative_statement | revision_history
    issue_text: str
    rule_ref: str  # trae_030 §0 | §1 | GOV-DOC-016


@dataclass
class DocReviewReport:
    """文档审查报告。"""

    session_id: str = ""
    reviewed_files: list[str] = field(default_factory=list)
    pending_regularization: list[DocReviewFinding] = field(default_factory=list)
    regularization_triggered: bool = False
    regularization_task_id: str = ""
    is_clean: bool = True
    # R1 防御：篡改检测字段
    git_authoritative: bool = False  # 是否使用了 git 权威列表
    git_unavailable: bool = False  # git 是否不可用
    tampering_detected: bool = False  # 是否检测到篡改
    tampering_details: list[str] = field(default_factory=list)  # 篡改详情

    def add_finding(
        self,
        file_path: str,
        line_number: int,
        issue_type: str,
        issue_text: str,
        rule_ref: str,
    ) -> None:
        self.is_clean = False
        self.pending_regularization.append(
            DocReviewFinding(
                file_path=file_path,
                line_number=line_number,
                issue_type=issue_type,
                issue_text=issue_text,
                rule_ref=rule_ref,
            )
        )

    @property
    def needs_regularization(self) -> bool:
        return len(self.pending_regularization) >= _REGULARIZATION_THRESHOLD

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "reviewed_files": self.reviewed_files,
            "pending_regularization": [
                {
                    "file_path": f.file_path,
                    "line_number": f.line_number,
                    "issue_type": f.issue_type,
                    "issue_text": f.issue_text,
                    "rule_ref": f.rule_ref,
                }
                for f in self.pending_regularization
            ],
            "regularization_triggered": self.regularization_triggered,
            "regularization_task_id": self.regularization_task_id,
            "is_clean": self.is_clean,
            "git_authoritative": self.git_authoritative,
            "git_unavailable": self.git_unavailable,
            "tampering_detected": self.tampering_detected,
            "tampering_details": self.tampering_details,
        }


class PostDocReviewScanner:
    """Session 关门时文档内容审查扫描器。"""

    def __init__(self, project_root: Path | None = None, session_id: str = "") -> None:
        if project_root is None:
            project_root = REPO_ROOT
        self._root = project_root
        # R7 防御：session_id 校验——禁止路径遍历字符
        if session_id and not _SESSION_ID_PATTERN.match(session_id):
            raise ValueError("session_id 含非法字符（只允许字母/数字/下划线/连字符）")
        self._session_id = session_id
        self._session_log_dir = project_root / "session_logs"

    def scan(self) -> DocReviewReport:
        """执行文档内容审查，返回报告。

        R1 防御：优先使用 git 权威列表，git 不可用时 RED 拒绝通过。
        """
        report = DocReviewReport(session_id=self._session_id)

        # R1 防御：获取 git 权威修改列表
        try:
            git_modified = self._get_modified_files_from_git()
            self_reported = self._load_modified_files()
            report.git_authoritative = True

            # 篡改检测：对比 git 权威列表 vs 自报告列表
            self._detect_tampering(git_modified, self_reported, report)

            # 使用 git 权威列表（不可篡改）
            modified_files = git_modified
        except GitUnavailableError:
            # git 不可用 -> RED 拒绝通过（不允许降级到自报告）
            report.git_unavailable = True
            report.is_clean = False
            report.tampering_detected = True
            report.tampering_details.append("git 不可用——门禁 RED 拒绝通过（不允许降级到自报告模式）")
            return report

        if not modified_files:
            # 无文档修改 -> PASS
            report.is_clean = True and not report.tampering_detected
            return report

        # 过滤可扫描的文档文件
        scannable_files = [f for f in modified_files if Path(f).suffix.lower() in _SCANNABLE_EXTENSIONS]

        for file_rel in scannable_files:
            file_path = self._root / file_rel
            if not file_path.exists():
                logger.warning("文件不存在，跳过: %s", file_path)
                continue
            self._scan_file(file_path, file_rel, report)

        # 标记数 >= 3 -> 触发规格化流程
        if report.needs_regularization:
            report.regularization_triggered = True
            # 实际任务卡创建由调用方处理（避免循环依赖）
            report.regularization_task_id = f"PENDING-{self._session_id}"

        return report

    def _get_session_start_commit(self) -> str:
        """读取 session 开始时记录的 commit hash。

        从 session_logs/<session_id>/session_start_commit.txt 读取。
        如果文件不存在 -> GitUnavailableError（session 未正确初始化）。
        """
        if not self._session_id:
            raise GitUnavailableError("session_id 为空")

        commit_file = self._session_log_dir / self._session_id / "session_start_commit.txt"
        if not commit_file.exists():
            raise GitUnavailableError(f"session_start_commit.txt 不存在——session 未正确初始化: {commit_file}")

        commit_hash = commit_file.read_text(encoding="utf-8").strip()
        # R1 防御：commit hash 校验（防命令注入）
        if not _COMMIT_HASH_PATTERN.match(commit_hash):
            raise GitUnavailableError(f"commit hash 格式非法（应为40位十六进制）: {commit_hash!r}")
        return commit_hash

    def _get_modified_files_from_git(self) -> list[str]:
        """用 git diff 获取权威修改文件列表（不可篡改）。

        1. 读取 session_start_commit
        2. git diff --name-only <start_commit> HEAD（已跟踪文件的修改）
        3. git ls-files --others --exclude-standard（新建未跟踪文件）
        4. 合并去重
        """
        start_commit = self._get_session_start_commit()

        try:
            # 已跟踪文件的修改（start_commit -> HEAD）
            tracked_result = subprocess.run(
                ["git", "diff", "--name-only", start_commit, "HEAD"],
                cwd=str(self._root),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if tracked_result.returncode != 0:
                raise GitUnavailableError(f"git diff 失败 (exit={tracked_result.returncode}): {tracked_result.stderr}")

            # 新建未跟踪文件
            untracked_result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=str(self._root),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if untracked_result.returncode != 0:
                raise GitUnavailableError(
                    f"git ls-files 失败 (exit={untracked_result.returncode}): {untracked_result.stderr}"
                )

            # 合并去重
            tracked_files = [f for f in tracked_result.stdout.strip().splitlines() if f]
            untracked_files = [f for f in untracked_result.stdout.strip().splitlines() if f]
            all_files = list(dict.fromkeys(tracked_files + untracked_files))

            # 过滤掉 session_logs/ 目录下的辅助文件——这些是门禁自身管理的文件
            # （modified_files.json / session_start_commit.txt / doc_review_report.json），
            # 不属于被审查的文档修改范围。
            all_files = [f for f in all_files if not f.replace("\\", "/").startswith("session_logs/")]
            return all_files

        except subprocess.TimeoutExpired as exc:
            raise GitUnavailableError(f"git 命令超时: {exc}") from exc
        except FileNotFoundError as exc:
            raise GitUnavailableError(f"git 命令不可用: {exc}") from exc

    def _detect_tampering(
        self,
        git_modified: list[str],
        self_reported: list[str],
        report: DocReviewReport,
    ) -> None:
        """R1 防御：篡改检测——对比 git 权威列表 vs 自报告列表。

        - git 有但自报告无 -> 删除修改记录（篡改）
        - 自报告有但 git 无 -> 虚报告（可疑）
        """
        git_set = set(git_modified)
        reported_set = set(self_reported)

        # git 有但自报告无 -> 删除修改记录
        deleted_from_report = git_set - reported_set
        if deleted_from_report:
            report.tampering_detected = True
            report.is_clean = False
            for f in sorted(deleted_from_report):
                report.tampering_details.append(f"篡改：文件 '{f}' 在 git 中有修改但 modified_files.json 中缺失")

        # 自报告有但 git 无 -> 虚报告
        fabricated_in_report = reported_set - git_set
        if fabricated_in_report:
            report.tampering_detected = True
            report.is_clean = False
            for f in sorted(fabricated_in_report):
                report.tampering_details.append(f"虚报告：文件 '{f}' 在 modified_files.json 中有但 git 中无修改")

    def _load_modified_files(self) -> list[str]:
        """从 session_logs/<session_id>/modified_files.json 加载修改文件列表。"""
        if not self._session_id:
            return []
        json_path = self._session_log_dir / self._session_id / "modified_files.json"
        if not json_path.exists():
            return []
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "files" in data:
                return data["files"]
            return []
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("解析 modified_files.json 失败: %s", exc)
            return []

    def _scan_file(self, file_path: Path, file_rel: str, report: DocReviewReport) -> None:
        """扫描单个文件的内容。"""
        # R9 防御：文件大小限制
        try:
            file_size = file_path.stat().st_size
            if file_size > _MAX_FILE_SIZE_BYTES:
                logger.warning(
                    "文件过大跳过扫描 (%d bytes > %d): %s",
                    file_size,
                    _MAX_FILE_SIZE_BYTES,
                    file_path,
                )
                return
        except OSError as exc:
            logger.warning("获取文件大小失败 %s: %s", file_path, exc)
            return

        try:
            raw_content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            # R10 防御：二进制文件伪装 .md -> 优雅跳过
            logger.warning("读取文件失败 %s: %s", file_path, exc)
            return

        # 文件通过大小和读取检查，添加到已审查列表
        report.reviewed_files.append(file_rel)

        # R4 防御：Unicode NFKC 归一化（全角->半角）
        content = unicodedata.normalize("NFKC", raw_content)
        lines = content.splitlines()

        # 逐行扫描
        for line_num, line in enumerate(lines, start=1):
            # R8 防御：超长行截断
            if len(line) > _MAX_LINE_LENGTH:
                line = line[:_MAX_LINE_LENGTH]
            self._check_patterns(
                line,
                line_num,
                file_rel,
                _CULTURAL_BENCHMARK_PATTERNS,
                "noise",
                "trae_030 §1",
                report,
            )
            self._check_patterns(
                line,
                line_num,
                file_rel,
                _AI_CONSCIOUSNESS_PATTERNS,
                "noise",
                "trae_030 §1",
                report,
            )
            self._check_patterns(
                line,
                line_num,
                file_rel,
                _TRANSITION_PATTERNS,
                "noise",
                "trae_030 §1",
                report,
            )
            self._check_patterns(
                line,
                line_num,
                file_rel,
                _PROCESS_STATEMENT_PATTERNS,
                "process_statement",
                "trae_030 §0",
                report,
            )
            self._check_patterns(
                line,
                line_num,
                file_rel,
                _NEGATIVE_STATEMENT_PATTERNS,
                "negative_statement",
                "GOV-DOC-016",
                report,
            )
            self._check_patterns(
                line,
                line_num,
                file_rel,
                _REVISION_HISTORY_PATTERNS,
                "revision_history",
                "trae_030 §1",
                report,
            )

        # R6 防御：跨行扫描——用滑动窗口检查跨行模式
        self._scan_cross_line(content, file_rel, report)

    def _check_patterns(
        self,
        line: str,
        line_num: int,
        file_rel: str,
        patterns: list[str],
        issue_type: str,
        rule_ref: str,
        report: DocReviewReport,
    ) -> None:
        """检查一行是否匹配任意模式，匹配则添加到报告。"""
        for pattern in patterns:
            # R5 防御：re.IGNORECASE 大小写不敏感
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                report.add_finding(
                    file_path=file_rel,
                    line_number=line_num,
                    issue_type=issue_type,
                    issue_text=line.strip()[:200],
                    rule_ref=rule_ref,
                )
                return  # 每行每类只报一次

    def _scan_cross_line(self, content: str, file_rel: str, report: DocReviewReport) -> None:
        """R6 防御：跨行扫描——检测被换行符分割的模式。

        检查策略：将换行符替换为空格后重新扫描，如果发现新匹配则标记。
        只检查文化类比对标段（最可能被跨行分割的模式）。
        """
        # 将连续空白（含换行符）归一化为单个空格
        normalized = re.sub(r"\s+", " ", content)
        # 只检查前 50000 字符（防超大文件性能问题）
        if len(normalized) > 50000:
            normalized = normalized[:50000]

        for pattern in _CULTURAL_BENCHMARK_PATTERNS:
            match = re.search(pattern, normalized, re.IGNORECASE)
            if match:
                # 检查这个匹配是否已经在逐行扫描中报告过
                match_text = match.group()
                already_reported = any(
                    f.issue_type == "noise" and match_text in f.issue_text for f in report.pending_regularization
                )
                if not already_reported:
                    report.add_finding(
                        file_path=file_rel,
                        line_number=0,  # 跨行匹配，行号设为0表示多行
                        issue_type="noise",
                        issue_text=f"[跨行] {match_text}",
                        rule_ref="trae_030 §1",
                    )

    def save_report(self, report: DocReviewReport) -> Path:
        """保存报告到 session_logs/<session_id>/doc_review_report.json。"""
        if not self._session_id:
            raise ValueError("session_id 为空，无法保存报告")
        out_dir = self._session_log_dir / self._session_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "doc_review_report.json"
        out_path.write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return out_path


def main() -> None:
    """CLI 入口——扫描指定 session 的文档。"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python post_doc_review_check.py <session_id>")
        sys.exit(1)
    session_id = sys.argv[1]
    scanner = PostDocReviewScanner(session_id=session_id)
    report = scanner.scan()
    out_path = scanner.save_report(report)
    print(f"报告已保存: {out_path}")
    print(f"审查文件数: {len(report.reviewed_files)}")
    print(f"待规格化项: {len(report.pending_regularization)}")
    print(f"触发规格化: {report.regularization_triggered}")
    if not report.is_clean:
        print("\n待规格化项详情:")
        for f in report.pending_regularization:
            print(f"  [{f.issue_type}] {f.file_path}:{f.line_number} ({f.rule_ref})")
            print(f"    {f.issue_text}")


if __name__ == "__main__":
    main()
