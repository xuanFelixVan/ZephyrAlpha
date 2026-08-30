# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] zephyr.clone_guard.engines.vendetect_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig); zephyr.clone_guard.engines.echo_guard_adapter (Finding); subprocess; csv; io; shutil; logging; pathlib
# [CONSUMERS] zephyr.clone_guard.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Adapter 模式——封装 Vendetect CLI 调用，统一 detect() 接口；CLI 不可用/未配 remote 降级；AGPL 许可证隔离（仅 subprocess，不链接进 src/）；永不抛异常
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect() 永不抛异常——CLI 失败/超时/未配 remote_url 返回 ([], degraded=True)
# [TESTS] tests/clone_guard/test_vendetect_adapter.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
VendetectAdapter — Vendetect 跨仓库合规审计适配器（Phase C L3）。

封装 Vendetect CLI 的 compare 命令，对编排层暴露统一 detect() 接口。
Vendetect 职责：检测跨仓库 vendored 代码，识别许可证合规风险（如 AGPL 代码
混入项目）。AGPL-3.0 许可证——本适配器仅 subprocess 调 CLI，不 import/链接
Vendetect 源码进 src/，守许可证隔离铁律。

真实 CLI（核实自 trailofbits/vendetect，位置参数）::

    vendetect TEST_REPO SOURCE_REPO --format csv --min-similarity <thr> --type py

输出格式采用 CSV 而非 JSON——Vendetect v0.0.3 的 JSON 输出含 numpy int64
导致序列化崩溃（``TypeError: Object of type int64 is not JSON serializable``），
CSV 稳定可用（见 tests/fixtures/vendetect_sample.csv）。

CSV 表头：``Test File,Source File,Test Slice Start,Test Slice End,
Source Slice Start,Source Slice End,Similarity``。同一 (Test File, Source File)
对可能有多行切片——按对聚合，相似度取最大。

severity 策略（CSV 无 license 字段，按相似度判定；license 合规分档待
Vendetect JSON 序列化修复后补全）：
  - similarity≥0.95 → extract（高相似跨仓库代码 = 合规风险，须人工核验许可证）
  - similarity≥0.7  → review
  - 其余 → acknowledged

降级策略（守 blueprint §5.2）：
  - Vendetect 未安装 → degraded=True, 返回空列表
  - 未配 remote_url → degraded=True, 返回空列表
  - 超时 → degraded=True, 返回空列表
  - CLI 崩溃 → degraded=True, 返回空列表
  - 正常执行 → 返回 Finding 列表

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: repo_root 参数
#   fields: 参数 repo_root（无注解）
#   code: vendetect_adapter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: vendetect_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① VendetectAdapter
#   name_en: VendetectAdapter
#   intro: Vendetect 跨仓库合规审计适配器（Phase C L3）。
#   desc: Vendetect 跨仓库合规审计适配器（Phase C L3）。 封装 Vendetect CLI 调用（位置参数 TEST_REPO SOURCE_REPO + --form…；公共方法（定义序）: health_…
#   inputs: repo_root config
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: VendetectAdapter
#   downstream: zephyr.clone_guard.orchestrator
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import csv
import io
import logging
import os
import shutil
import subprocess  # noqa: bare-subprocess  Vendetect CLI 调用需要 subprocess
from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import Finding

logger = logging.getLogger(__name__)

__all__ = ["VendetectAdapter"]

# Vendetect --min-similarity 默认阈值（CSV 输出无 license，仅按相似度分档）
_DEFAULT_MIN_SIMILARITY: float = 0.7


class VendetectAdapter:
    """Vendetect 跨仓库合规审计适配器（Phase C L3）。

    封装 Vendetect CLI 调用（位置参数 TEST_REPO SOURCE_REPO + --format csv），
    对编排层暴露统一 detect() 接口。AGPL 许可证隔离：仅 subprocess 调 CLI，不链接进 src/。
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = Path(repo_root)
        self._config = config or CloneGuardConfig()

    def health_check(self) -> bool:
        """检查 Vendetect 是否可用（CLI 存在 + 已配 remote_url）。"""
        if shutil.which("vendetect") is None:
            return False
        return bool(self._config.vendetect_remote_url)

    def detect(self, files: list[str], timeout: int | None = None) -> tuple[list[Finding], bool]:
        """检测给定文件在远程仓库中的 vendored 代码（L3 跨边界审计）。

        Args:
            files: 待检测文件路径列表（相对路径）。Vendetect 对整个 TEST_REPO 与
                SOURCE_REPO 做对比，files 仅用于空值守卫。
            timeout: 超时秒数（None 时使用 compare_timeout_sec）。

        Returns:
            (findings, degraded) 元组：degraded=True 表示不可用/超时/未配 remote。
        """
        if not files:
            return [], False

        if not self._config.vendetect_enabled:
            logger.debug("Vendetect 已在配置中禁用，跳过检测")
            return [], True

        if shutil.which("vendetect") is None:
            logger.debug("VendetectAdapter: Vendetect CLI 未安装，跳过检测")
            return [], True

        remote_url = self._config.vendetect_remote_url
        if not remote_url:
            logger.debug("VendetectAdapter: 未配 vendetect_remote_url，跳过检测")
            return [], True

        timeout_sec = timeout or self._config.compare_timeout_sec
        cmd = self._build_command(remote_url)

        try:
            result = subprocess.run(  # noqa: bare-subprocess  Vendetect CLI 调用
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                cwd=str(self._repo_root),
                env={**os.environ, **self._config.env},
            )
        except FileNotFoundError:
            logger.warning("VendetectAdapter degraded: Vendetect CLI 未安装")
            return [], True
        except subprocess.TimeoutExpired:
            logger.warning("VendetectAdapter degraded: Vendetect 超时(%ds)", timeout_sec)
            return [], True
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("VendetectAdapter degraded: Vendetect 异常(%s: %s)", type(e).__name__, e)
            return [], True

        # Vendetect exit codes: 0=无 vendored, 1=发现 vendored, 其他=错误
        if result.returncode not in (0, 1):
            logger.warning(
                "VendetectAdapter degraded: Vendetect 退出码=%d, stderr=%s",
                result.returncode,
                result.stderr[:200] if result.stderr else "",
            )
            return [], True

        findings = self._parse_csv(result.stdout)
        return findings, False

    def _build_command(self, remote_url: str) -> list[str]:
        """构造 Vendetect 命令（位置参数 TEST_REPO SOURCE_REPO + CSV 格式）。"""
        return [
            "vendetect",
            str(self._repo_root),
            remote_url,
            "--format",
            "csv",
            "--min-similarity",
            str(_DEFAULT_MIN_SIMILARITY),
            "--type",
            "py",
        ]

    def _parse_csv(self, stdout: str) -> list[Finding]:
        """将 Vendetect CSV 输出解析为 Finding 列表。

        按 (test_file, source_file) 聚合切片：相似度取最大，记录切片数与首切片起始行。
        跳过表头行（含 "Test File"）。
        """
        if not stdout or not stdout.strip():
            return []

        reader = csv.reader(io.StringIO(stdout))
        rows = list(reader)
        if not rows:
            return []

        # 跳过表头行
        data_rows = rows
        if rows and rows[0] and "Test File" in rows[0][0]:
            data_rows = rows[1:]

        # 按 (test_file, source_file) 聚合
        pairs: dict[tuple[str, str], dict] = {}
        for row in data_rows:
            parsed = self._parse_row(row)
            if parsed is None:
                continue
            test_file, source_file, similarity, slice_start = parsed
            key = (test_file, source_file)
            if key not in pairs:
                pairs[key] = {
                    "test_file": test_file,
                    "source_file": source_file,
                    "similarity": similarity,
                    "slice_count": 1,
                    "first_slice_start": slice_start,
                }
            else:
                pairs[key]["slice_count"] += 1
                if similarity > pairs[key]["similarity"]:
                    pairs[key]["similarity"] = similarity

        findings: list[Finding] = []
        for idx, p in enumerate(pairs.values()):
            findings.append(self._to_finding(p, idx))
        return findings

    @staticmethod
    def _parse_row(row: list[str]) -> tuple[str, str, float, int] | None:
        """解析单行 CSV → (test_file, source_file, similarity, test_slice_start)。

        CSV 列：Test File, Source File, Test Slice Start, Test Slice End,
                Source Slice Start, Source Slice End, Similarity
        """
        if len(row) < 7:
            return None
        try:
            test_file = str(row[0]).strip()
            source_file = str(row[1]).strip()
            slice_start = int(row[2])
            similarity = float(row[6])
        except (ValueError, IndexError):
            return None
        if not test_file or not source_file:
            return None
        return test_file, source_file, similarity, slice_start

    def _to_finding(self, p: dict, idx: int) -> Finding:
        """将聚合后的切片对转为 Finding。"""
        similarity = float(p["similarity"])
        test_file = self._to_relative_path(p["test_file"])
        source_file = str(p["source_file"]).replace("\\", "/")  # 远程仓库路径归一化斜杠

        return Finding(
            finding_id=f"VD-{idx}-{test_file}-{source_file}",
            severity=self._severity_for(similarity),
            clone_type="vendored",  # 跨仓库 vendored 代码
            similarity=similarity,
            source_file=test_file,
            source_function="unknown",  # CSV 输出无函数名
            source_lineno=int(p.get("first_slice_start", 0)),
            existing_file=source_file,
            existing_function="unknown",
            existing_lineno=0,
            import_suggestion=self._config.vendetect_remote_url,  # 远程 URL 作为溯源
        )

    @staticmethod
    def _severity_for(similarity: float) -> str:
        """合规 severity 判定（CSV 无 license，按相似度分档）。

        - similarity≥0.95 → extract（高相似跨仓库代码 = 合规风险，须核验许可证）
        - similarity≥0.7  → review
        - 其余 → acknowledged

        注：license 维度分档待 Vendetect JSON 序列化修复（numpy int64）后补全。
        """
        if similarity >= 0.95:
            return "extract"  # 合规硬阻断（vendored 高相似 = 须人工核验）
        if similarity >= 0.7:
            return "review"
        return "acknowledged"

    def _to_relative_path(self, file_path: str) -> str:
        """将绝对路径转为相对仓库根目录的路径（归一化斜杠）。"""
        try:
            p = Path(file_path)
            if p.is_absolute():
                rel = p.relative_to(self._repo_root)
                return str(rel).replace("\\", "/")
            return file_path.replace("\\", "/")
        except ValueError:
            return file_path.replace("\\", "/")
