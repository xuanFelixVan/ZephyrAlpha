# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] zephyr.clone_guard.engines.echo_guard_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig); subprocess; json; logging; ast (平凡访问器族 AST 判定，AI-GOVFIX-ECHO-001); ruamel.yaml (acknowledge/prune 写入路径，lazy import); filelock (_embedding_lock 跨进程锁，lazy import)
# [CONSUMERS] zephyr.clone_guard.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Adapter 模式——封装 echo-guard CLI 调用，对编排层暴露统一 detect() 接口；echo-guard 不可用时返回空列表 + degraded 标记；永不抛异常；OOB 治本（P2 #ARCH-ECHO-GUARD-EMBEDDING-OOB）：_embedding_lock 跨进程文件锁序列化 echo-guard CLI 调用（detect/scan），防 EmbeddingStore 无锁并发写导致 153 函数 embedding_row OOB（0.74%）；锁超时→degraded 不执行 CLI（避免无锁竞态）；filelock 未安装/锁目录不可写→fail-open 无锁执行（守 _GlobalCommitLock 先例）；平凡访问器族治本（AI-GOVFIX-ECHO-001）：_parse_findings 漏斗 AST 层剔除"两侧皆平凡访问器"finding（函数体剥 docstring 后 ≤1 语句=平凡），根治 echo-guard _is_trivial_function 物理行口径 docstring 逃逸致的 Type-2 单行访问器 extract 假阳性族（实证五 hub 82+ 对）；判定失败保守保留；多语句真克隆检测面不动
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect()/scan()/acknowledge()/prune() 永不抛异常——CLI/ruamel 失败/超时/异常返回降级标记（detect/scan: ([], True)；acknowledge: (False, error)；prune: (False, error, 0)）
# [TESTS] tests/clone_guard/test_echo_guard_adapter.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
EchoGuardAdapter — Echo-Guard 引擎适配器（Phase A MVP）。

封装 echo-guard CLI 的 check 命令，对编排层暴露统一 detect() 接口。
通过 `echo-guard check --output json FILES...` 调用，解析 JSON 输出为 Finding 列表。

降级策略（守 blueprint §5.2）：
  - echo-guard 未安装 → degraded=True, 返回空列表
  - 索引不存在 → degraded=True, 返回空列表
  - 超时 → degraded=True, 返回空列表
  - CLI 崩溃 → degraded=True, 返回空列表
  - 正常执行 → 返回 Finding 列表

平凡访问器族过滤（治本 AI-GOVFIX-ECHO-001）：
  echo-guard 行数口径为 tree-sitter function_definition 跨度（def→末行，
  含 docstring、不含 decorator），``@property+def+docstring+return self._X``
  3 行模板恰过 min_function_lines=3 入库；Tier-1 归一化 AST 哈希对该模板
  100% 撞车（Type-2 口径）；而其 _is_trivial_function 按物理行计函数体，
  docstring 被计入致带注释单行访问器逃逸"单语句体=平凡"抑制——3+ 副本聚组
  即 extract 级硬阻断（实证 agent_id/traces/links/core_writer/initial_capital
  五 hub 82+ 对全假阳性，2026-08-28）。本适配器在 _parse_findings 漏斗以
  Python AST 重判：函数体剥 docstring 后 ≤1 条语句即平凡访问器（getter/
  setter/单行表达式同族），source/existing 两侧皆平凡则剔除；判定失败
  （文件缺失/解析失败/定位失败/歧义）一律保守保留；多语句函数（真克隆
  检测面）不受影响。回归锁定：tests/clone_guard/test_echo_guard_adapter.py
  TestTrivialAccessorFilter。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: repo_root 参数
#   fields: 参数 repo_root（无注解）
#   code: echo_guard_adapter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: echo_guard_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① EchoGuardAdapter
#   name_en: EchoGuardAdapter
#   intro: Echo-Guard 引擎适配器。
#   desc: Echo-Guard 引擎适配器。 封装 echo-guard CLI 调用，对编排层暴露统一 detect() 接口。 引擎升级/替换不影响编排层（Adapter 模式）。；公共方法（定义序）: health_che…
#   inputs: repo_root config
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: EchoGuardAdapter
#   downstream: zephyr.clone_guard.orchestrator
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import ast
import json
import logging
import os
import subprocess  # noqa: bare-subprocess  echo-guard CLI 调用需要 subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig

logger = logging.getLogger(__name__)

__all__ = ["EchoGuardAdapter", "Finding"]

# OOB 治本（P2 #ARCH-ECHO-GUARD-EMBEDDING-OOB）：跨进程文件锁序列化 echo-guard CLI 调用。
# 锁文件与 _GlobalCommitLock 同目录（.ailocks/），60s 超时守 _LOCK_TIMEOUT_DEFAULT 先例。
_EMBEDDING_LOCK_FILE = "echo_guard_embedding.lock"
_EMBEDDING_LOCK_TIMEOUT = 60.0


class _EmbeddingLockTimeout(RuntimeError):
    """echo-guard embedding 锁等待超时——调用方降级（不执行 CLI 防 OOB 竞态）。"""


@dataclass(frozen=True)
class Finding:
    """统一的克隆检测结果（跨引擎统一格式）。

    Phase A 简化版——仅包含 Echo-Guard 返回的核心字段。
    Phase B 起由 aggregator.py 合并多引擎结果后补充 engines/saved_lines 等字段。
    """

    finding_id: str
    severity: str  # extract / review
    clone_type: str  # T1 / T2 / T3 / T4
    similarity: float
    source_file: str
    source_function: str
    source_lineno: int
    existing_file: str
    existing_function: str
    existing_lineno: int
    import_suggestion: str | None = None


class EchoGuardAdapter:
    """Echo-Guard 引擎适配器。

    封装 echo-guard CLI 调用，对编排层暴露统一 detect() 接口。
    引擎升级/替换不影响编排层（Adapter 模式）。
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = repo_root
        self._config = config or CloneGuardConfig()

    @contextmanager
    def _embedding_lock(self):
        """跨进程文件锁——序列化 echo-guard CLI 调用防 EmbeddingStore 并发写 OOB。

        OOB 治本（P2 #ARCH-ECHO-GUARD-EMBEDDING-OOB）：echo-guard EmbeddingStore 无文件锁，
        多进程并发写 ``embeddings.npy`` 导致 153 函数 embedding_row 越界（0.74%）。本锁序列化
        所有 echo-guard CLI 调用（detect/scan/acknowledge-CLI），消除并发写竞态。

        降级策略（守 INVARIANTS + ``_GlobalCommitLock`` 先例）：
        - filelock 未安装 → fail-open（无锁执行，落 warning）
        - 锁目录不可写 → fail-open（无锁执行，落 warning）
        - 锁超时（60s）→ raise ``_EmbeddingLockTimeout``（调用方降级，不执行 CLI——避免无锁竞态）

        fail-open 理由：filelock 是可选依赖，缺失时不应阻断所有 echo-guard 检测
        （守 ``_GlobalCommitLock`` OSError fail-open 先例）。锁超时不 fail-open 而降级的理由：
        基础设施可用但竞争失败时，无锁执行会重新引入 OOB 竞态——宁可本次跳过检测
        （degraded，``fail_closed=False`` 不阻断 commit）也不冒险。
        """
        try:
            from filelock import FileLock, Timeout  # noqa: PLC0415 — lazy import
        except ImportError:
            logger.warning(
                "EchoGuardAdapter: filelock 未安装，fail-open 无锁执行 echo-guard CLI"
                "（存在 EmbeddingStore 并发写 OOB 风险）"
            )
            yield
            return

        lock_dir = self._repo_root / ".ailocks"
        try:
            lock_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.warning(
                "EchoGuardAdapter: 锁目录不可写(%s: %s)，fail-open 无锁执行 echo-guard CLI",
                type(e).__name__,
                e,
            )
            yield
            return

        lock = FileLock(str(lock_dir / _EMBEDDING_LOCK_FILE), timeout=_EMBEDDING_LOCK_TIMEOUT)
        try:
            lock.acquire()
        except Timeout:
            raise _EmbeddingLockTimeout(
                f"echo-guard embedding 锁等待超时({_EMBEDDING_LOCK_TIMEOUT}s)——"
                f"另一进程正在执行 echo-guard CLI，本次降级跳过以防 EmbeddingStore 并发写 OOB"
            ) from None
        try:
            yield
        finally:
            try:
                lock.release()
            except OSError:
                pass  # 锁已释放或进程异常——filelock 自身有锁文件清理机制

    def health_check(self) -> bool:
        """检查 echo-guard 是否可用（CLI 存在 + 索引已建）。"""
        index_path = self._repo_root / ".echo-guard" / "index.duckdb"
        if not index_path.exists():
            return False
        try:
            result = subprocess.run(  # noqa: bare-subprocess  echo-guard CLI 健康检查
                ["echo-guard", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(self._repo_root),
                env={**os.environ, **self._config.env},
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def detect(self, files: list[str], timeout: int | None = None) -> tuple[list[Finding], bool]:
        """检测给定文件的克隆。

        Args:
            files: 待检测文件路径列表（相对路径）。
            timeout: 超时秒数（None 时使用配置默认值）。

        Returns:
            (findings, degraded) 元组：
            - findings: Finding 列表（检测失败时为空列表）
            - degraded: True 表示 echo-guard 不可用/超时/崩溃
        """
        if not files:
            return [], False

        if not self._config.echo_guard_enabled:
            logger.debug("echo-guard 已在配置中禁用，跳过检测")
            return [], True

        timeout_sec = timeout or self._config.pre_commit_timeout_sec

        try:
            with self._embedding_lock():
                result = subprocess.run(  # noqa: bare-subprocess  echo-guard CLI check 调用
                    ["echo-guard", "check", "--output", "json"] + files,
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                    cwd=str(self._repo_root),
                    env={**os.environ, **self._config.env},
                )
        except _EmbeddingLockTimeout:
            logger.warning("EchoGuardAdapter degraded: embedding 锁超时，跳过 check 防 OOB")
            return [], True
        except FileNotFoundError:
            logger.warning("EchoGuardAdapter degraded: echo-guard CLI 未安装")
            return [], True
        except subprocess.TimeoutExpired:
            logger.warning("EchoGuardAdapter degraded: echo-guard check 超时(%ds)", timeout_sec)
            return [], True
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("EchoGuardAdapter degraded: echo-guard check 异常(%s: %s)", type(e).__name__, e)
            return [], True

        # echo-guard exit codes: 0=无阻断发现, 1=有阻断发现, 2=无索引
        if result.returncode == 2:
            logger.warning("EchoGuardAdapter degraded: echo-guard 索引不存在，运行 `echo-guard index` 构建")
            return [], True

        if result.returncode not in (0, 1):
            logger.warning(
                "EchoGuardAdapter degraded: echo-guard check 退出码=%d, stderr=%s",
                result.returncode,
                result.stderr[:200] if result.stderr else "",
            )
            return [], True

        # 解析 JSON 输出
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.warning("EchoGuardAdapter degraded: JSON 解析失败(%s)", e)
            return [], True

        findings = self._parse_findings(data)
        return findings, False

    def scan(self, timeout: int | None = None) -> tuple[list[Finding], bool]:
        """L2 全量审计——echo-guard scan 全仓库冗余扫描（无文件参数）。

        与 detect()（check 命令，比对索引的 pre-commit 快速路径）互补：scan 做
        全仓库冗余扫描，不取文件参数，规避 L2 全量审计传入数千文件超 Windows
        CreateProcess 命令行上限的问题。scan 与 check 输出同构（均为
        {"findings":[...]} JSON），复用 _parse_findings。

        守 ERROR_CONTRACT：CLI 失败/超时/索引缺失返回 ([], degraded=True)。

        Args:
            timeout: 超时秒数（None 时用 config.audit_timeout_sec）。

        Returns:
            (findings, degraded) 元组。
        """
        if not self._config.echo_guard_enabled:
            logger.debug("echo-guard 已在配置中禁用，跳过扫描")
            return [], True

        timeout_sec = timeout or self._config.audit_timeout_sec

        try:
            with self._embedding_lock():
                result = subprocess.run(  # noqa: bare-subprocess  echo-guard CLI scan 调用
                    ["echo-guard", "scan", "--output", "json"],
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                    cwd=str(self._repo_root),
                    env={**os.environ, **self._config.env},
                )
        except _EmbeddingLockTimeout:
            logger.warning("EchoGuardAdapter degraded: embedding 锁超时，跳过 scan 防 OOB")
            return [], True
        except FileNotFoundError:
            logger.warning("EchoGuardAdapter degraded: echo-guard CLI 未安装")
            return [], True
        except subprocess.TimeoutExpired:
            logger.warning("EchoGuardAdapter degraded: echo-guard scan 超时(%ds)", timeout_sec)
            return [], True
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("EchoGuardAdapter degraded: echo-guard scan 异常(%s: %s)", type(e).__name__, e)
            return [], True

        # echo-guard exit codes: 0=无发现, 1=有发现, 2=无索引
        if result.returncode == 2:
            logger.warning("EchoGuardAdapter degraded: echo-guard 索引不存在，运行 `echo-guard index` 构建")
            return [], True

        if result.returncode not in (0, 1):
            logger.warning(
                "EchoGuardAdapter degraded: echo-guard scan 退出码=%d, stderr=%s",
                result.returncode,
                result.stderr[:200] if result.stderr else "",
            )
            return [], True

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.warning("EchoGuardAdapter degraded: JSON 解析失败(%s)", e)
            return [], True

        findings = self._parse_findings(data)
        return findings, False

    def acknowledge(
        self,
        finding_id: str,
        verdict: str,
        note: str,
        timeout: int | None = None,
    ) -> tuple[bool, str | None]:
        """将 finding 加入 echo-guard.yml acknowledged 白名单（L2 acknowledged 机制）。

        两条写入路径（裁定 #ARCH-ECHO-GUARD-YML-COMMENT-LOSS 治本）：
        - 项目层 ruamel.yaml round-trip（默认，``acknowledge_via_cli=False``）：保留注释/格式
        - echo-guard CLI（``acknowledge_via_cli=True``，诊断/兼容）：PyYAML 重写丢注释

        verdict 语义：
        - intentional: 保留两份副本（函数变化时重新浮现，非永久豁免）
        - dismissed:   标记为非重复（永久豁免）

        守 ERROR_CONTRACT：CLI/ruamel 失败/超时/异常返回 ``(False, error)``，不抛异常。

        Args:
            finding_id: 来自 ``echo-guard scan --output json`` 的 finding ID。
            verdict: ``"intentional"`` 或 ``"dismissed"``（由调用方校验，本方法透传）。
            note: 说明为何 acknowledge（留痕防滥用，由调用方强制非空）。
            timeout: 超时秒数（仅 CLI 路径用；None 时用 ``config.pre_commit_timeout_sec``）。

        Returns:
            ``(success, error)`` 元组：
            - success: True 表示已写入 echo-guard.yml acknowledged 列表
            - error: 失败原因（成功时为 None）
        """
        if not self._config.echo_guard_enabled:
            logger.debug("echo-guard 已在配置中禁用，跳过 acknowledge")
            return False, "echo-guard 已禁用"

        if self._config.acknowledge_via_cli:
            return self._acknowledge_via_cli(finding_id, verdict, note, timeout)
        return self._acknowledge_via_roundtrip(finding_id, verdict, note)

    def _acknowledge_via_cli(
        self,
        finding_id: str,
        verdict: str,
        note: str,
        timeout: int | None,
    ) -> tuple[bool, str | None]:
        """CLI 写入路径——调 ``echo-guard acknowledge``（PyYAML 重写，丢注释）。

        诊断/兼容用（``acknowledge_via_cli=True``）。默认路径走 ``_acknowledge_via_roundtrip``。
        """
        timeout_sec = timeout or self._config.pre_commit_timeout_sec

        try:
            with self._embedding_lock():
                result = subprocess.run(  # noqa: bare-subprocess  echo-guard CLI acknowledge 调用
                    [
                        "echo-guard",
                        "acknowledge",
                        finding_id,
                        "--verdict",
                        verdict,
                        "--note",
                        note,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                    cwd=str(self._repo_root),
                    env={**os.environ, **self._config.env},
                )
        except _EmbeddingLockTimeout:
            logger.warning("EchoGuardAdapter acknowledge(CLI) degraded: embedding 锁超时，跳过防 OOB")
            return False, "echo-guard embedding 锁超时（并发写 OOB 防护），请重试"
        except FileNotFoundError:
            logger.warning("EchoGuardAdapter acknowledge(CLI) degraded: echo-guard CLI 未安装")
            return False, "echo-guard CLI 未安装"
        except subprocess.TimeoutExpired:
            logger.warning("EchoGuardAdapter acknowledge(CLI) degraded: 超时(%ds)", timeout_sec)
            return False, f"echo-guard acknowledge 超时({timeout_sec}s)"
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("EchoGuardAdapter acknowledge(CLI) degraded: 异常(%s: %s)", type(e).__name__, e)
            return False, f"{type(e).__name__}: {e}"

        if result.returncode != 0:
            err = (result.stderr or result.stdout or "").strip()[:200]
            logger.warning(
                "EchoGuardAdapter acknowledge(CLI) 失败: exit=%d, stderr=%s",
                result.returncode,
                err,
            )
            return False, f"echo-guard acknowledge 退出码={result.returncode}: {err}"

        return True, None

    def _acknowledge_via_roundtrip(
        self,
        finding_id: str,
        verdict: str,
        note: str,
    ) -> tuple[bool, str | None]:
        """项目层 ruamel.yaml round-trip 写 echo-guard.yml acknowledged 段（保留注释）。

        治本 #ARCH-ECHO-GUARD-YML-COMMENT-LOSS：echo-guard CLI 用 PyYAML 重写丢注释，
        本方法用 ruamel round-trip 只更新 acknowledged 段，保留其他注释/格式/引号风格。

        复现 echo-guard CLI 的 acknowledged 段格式（echo_guard/config.py:238-255）：
        - intentional: ``{id, verdict, source_hash[:8], existing_hash[:8]}``
        - dismissed:   ``{id, verdict, stable_key=make_stable_key(finding_id)}``

        兼容性：echo-guard ``is_suppressed``（config.py:171-221）完全基于 yml acknowledged
        段判定，本方法写的格式与 CLI 写的一致，echo-guard check/scan 正确识别并跳过。
        不写 DuckDB 索引（仅影响 VS Code 扩展展示，不影响 L1/L2 检测）。
        """
        yml_path = self._repo_root / "echo-guard.yml"
        if not yml_path.exists():
            return False, "echo-guard.yml 不存在"

        try:
            from ruamel.yaml import YAML  # noqa: PLC0415 — lazy import，仅写入路径需要
        except ImportError:
            logger.warning("EchoGuardAdapter acknowledge(roundtrip): ruamel.yaml 未安装")
            return False, "ruamel.yaml 未安装（pip install ruamel.yaml）"

        # 构造 entry（复现 echo_guard/config.py:248-254）
        if verdict == "intentional":
            src_hash, ext_hash = self._parse_finding_id_hashes(finding_id)
            entry = {
                "id": finding_id,
                "verdict": verdict,
                "source_hash": src_hash[:8] if src_hash else "",
                "existing_hash": ext_hash[:8] if ext_hash else "",
            }
        elif verdict == "dismissed":
            entry = {
                "id": finding_id,
                "verdict": verdict,
                "stable_key": self._make_stable_key(finding_id),
            }
        else:
            return False, f"verdict 非法: {verdict!r}（须 intentional 或 dismissed）"

        try:
            ryaml = YAML()
            ryaml.preserve_quotes = True
            ryaml.width = 4096  # 防长行折行（守 load_acquisition_decisions.py 先例）
            with yml_path.open("r", encoding="utf-8") as f:
                data = ryaml.load(f)
            if data is None:
                data = {}

            # acknowledged 段——不存在则初始化
            if data.get("acknowledged") is None:
                data["acknowledged"] = []
            ack_list = data["acknowledged"]

            # 去重：移除同 id 旧 entry（复现 echo_guard/config.py:247）
            to_remove = [i for i, e in enumerate(ack_list) if isinstance(e, dict) and e.get("id") == finding_id]
            for i in reversed(to_remove):
                del ack_list[i]
            ack_list.append(entry)

            with yml_path.open("w", encoding="utf-8") as f:
                ryaml.dump(data, f)
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("EchoGuardAdapter acknowledge(roundtrip) 失败: %s: %s", type(e).__name__, e)
            return False, f"{type(e).__name__}: {e}"

        logger.info(
            "acknowledge(roundtrip): %s verdict=%s 已写入 echo-guard.yml（注释保留）",
            finding_id[:60],
            verdict,
        )
        return True, None

    def prune(
        self,
        scan_finding_ids: set[str] | None = None,
    ) -> tuple[bool, str | None, int]:
        """移除 echo-guard.yml acknowledged 中已不存在的 intentional finding（白名单清理）。

        项目层 ruamel round-trip 写入（保留注释）。复现 echo-guard prune CLI 语义
        （cli.py:2050-2155）的简化版：丢弃 intentional 类型的 stale entry
        （id 不再出现在 scan 结果）。**dismissed 类型保留**——dismissed 是永久豁免，
        依赖 stable_key 匹配（非 id），需人工清理，避免 id 匹配误删。

        Args:
            scan_finding_ids: 当前 scan 返回的所有 finding_id 集合。None 时本方法
                调 ``self.scan()`` 自取（全仓库扫描，较慢）。

        Returns:
            ``(success, error, removed_count)`` 元组：
            - success: True 表示 prune 完成（含 0 移除）
            - error: 失败原因（成功时为 None）
            - removed_count: 移除的 stale entry 数
        """
        if not self._config.echo_guard_enabled:
            return False, "echo-guard 已禁用", 0

        # 获取当前 scan 的 finding_ids
        if scan_finding_ids is None:
            findings, degraded = self.scan()
            if degraded:
                return False, "scan 降级，无法 prune", 0
            scan_finding_ids = {f.finding_id for f in findings}

        yml_path = self._repo_root / "echo-guard.yml"
        if not yml_path.exists():
            return False, "echo-guard.yml 不存在", 0

        try:
            from ruamel.yaml import YAML  # noqa: PLC0415 — lazy import
        except ImportError:
            return False, "ruamel.yaml 未安装", 0

        try:
            ryaml = YAML()
            ryaml.preserve_quotes = True
            ryaml.width = 4096
            with yml_path.open("r", encoding="utf-8") as f:
                data = ryaml.load(f)
            if data is None:
                data = {}

            ack_list = data.get("acknowledged")
            if not ack_list:
                return True, None, 0  # 无 acknowledged，无需 prune

            # 只 prune intentional stale（id 不在 scan 结果）；dismissed 保留
            to_remove = []
            for i, entry in enumerate(ack_list):
                if not isinstance(entry, dict):
                    continue
                if entry.get("verdict") != "intentional":
                    continue  # dismissed 保留（永久豁免，需人工清理）
                eid = entry.get("id", "")
                if eid and eid not in scan_finding_ids:
                    to_remove.append(i)
            for i in reversed(to_remove):
                del ack_list[i]

            if to_remove:
                with yml_path.open("w", encoding="utf-8") as f:
                    ryaml.dump(data, f)
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("EchoGuardAdapter prune 失败: %s: %s", type(e).__name__, e)
            return False, f"{type(e).__name__}: {e}", 0

        logger.info("prune(roundtrip): 移除 %d 个 stale intentional entry", len(to_remove))
        return True, None, len(to_remove)

    @staticmethod
    def _make_stable_key(finding_id: str) -> str:
        """复现 echo-guard ``config.py:224-236 make_stable_key``。

        finding_id 格式: ``filepath:name:hash||filepath:name:hash``
        stable_key = 排序两侧 ``filepath:name``（去 hash），``||`` 连接。
        同一对函数无论哪侧是 source/existing 都产生相同 key。
        """
        parts = finding_id.split("||")
        if len(parts) != 2:
            return finding_id
        sides = sorted(p.rsplit(":", 1)[0] for p in parts)
        return "||".join(sides)

    @staticmethod
    def _parse_finding_id_hashes(finding_id: str) -> tuple[str, str]:
        """从 finding_id 解析 source_hash/existing_hash（复现 echo-guard ``cli.py:1961-1968``）。

        finding_id 格式: ``filepath:name:hash||filepath:name:hash``
        返回 ``(source_hash, existing_hash)``；解析失败返回 ``("", "")``。
        """
        parts = finding_id.split("||")
        if len(parts) != 2:
            return "", ""
        a = parts[0].rsplit(":", 1)
        b = parts[1].rsplit(":", 1)
        src_hash = a[1] if len(a) == 2 else ""
        ext_hash = b[1] if len(b) == 2 else ""
        return src_hash, ext_hash

    def _parse_findings(self, data: dict) -> list[Finding]:
        """将 echo-guard JSON 输出解析为 Finding 列表（含平凡访问器族过滤）。

        detect()/scan() 共用漏斗——平凡访问器对过滤在此统一生效（AI-GOVFIX-ECHO-001）。
        """
        findings: list[Finding] = []
        for item in data.get("findings", []):
            try:
                if item.get("type") == "match":
                    findings.append(self._parse_match(item))
                elif item.get("type") == "group":
                    findings.extend(self._parse_group(item))
            except (KeyError, TypeError) as e:
                logger.debug("跳过无法解析的 finding: %s (%s)", item.get("finding_id", "?"), e)
        return self._drop_trivial_accessor_pairs(findings)

    # ------------------------------------------------------------------
    # 平凡访问器族过滤（治本 AI-GOVFIX-ECHO-001）
    # ------------------------------------------------------------------

    def _drop_trivial_accessor_pairs(self, findings: list[Finding]) -> list[Finding]:
        """剔除 source/existing 两侧均为平凡访问器的 finding（Type-2 单行模板撞车假阳性族）。

        根因：echo-guard ``_is_trivial_function`` 按物理行计函数体，docstring 被计为
        body line——``@property def f(): "doc"; return self._x``（def+docstring+return
        3 行模板，恰过 min_function_lines=3）逃逸"单语句体=平凡"抑制；而 Tier-1 归一化
        AST 哈希对该模板 100% 撞车（``return self._X`` 标识符位置归一后全同构），
        3+ 副本聚组即 extract 级硬阻断（实证五 hub 82+ 对全假阳性）。

        治本：AST 层重判——函数体剥 docstring 后 ≤1 条语句即平凡访问器（getter/
        setter/单行表达式同族），两侧皆平凡则剔除。判定失败（文件缺失/解析失败/
        函数定位失败/同名歧义）一律保守保留。多语句函数（真克隆检测面）不受影响。
        """
        if not findings:
            return findings
        ast_cache: dict[str, ast.Module | None] = {}
        kept: list[Finding] = []
        for f in findings:
            if self._is_trivial_accessor(f.source_file, f.source_function, f.source_lineno, ast_cache) and (
                self._is_trivial_accessor(f.existing_file, f.existing_function, f.existing_lineno, ast_cache)
            ):
                logger.debug(
                    "剔除平凡访问器族 finding: %s:%s ↔ %s:%s（两侧皆单语句体，Type-2 模板撞车非真重复）",
                    f.source_file,
                    f.source_function,
                    f.existing_file,
                    f.existing_function,
                )
                continue
            kept.append(f)
        return kept

    def _is_trivial_accessor(
        self,
        filepath: str,
        name: str,
        lineno: int,
        ast_cache: dict[str, ast.Module | None],
    ) -> bool:
        """AST 判定指定函数是否平凡访问器（函数体剥 docstring 后 ≤1 条语句）。

        定位策略：按函数名收集候选，优先 lineno 精确命中（echo-guard tree-sitter
        lineno 与 Python ast FunctionDef.lineno 同指 def 行，口径一致）；未命中且
        名字唯一时回退唯一候选（容忍索引后文件编辑致行号偏移）；同名多定义
        （property+setter）且行号未命中属歧义，保守判非平凡。

        保守语义：文件缺失/不可读/语法错误/函数定位失败 → False（保留 finding）。
        """
        key = str(self._repo_root / filepath)
        if key not in ast_cache:
            try:
                ast_cache[key] = ast.parse(Path(key).read_text(encoding="utf-8"))
            except (OSError, SyntaxError, ValueError):
                ast_cache[key] = None
        tree = ast_cache[key]
        if tree is None:
            return False

        candidates = [
            n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name
        ]
        if not candidates:
            return False
        node = next((n for n in candidates if n.lineno == lineno), None)
        if node is None:
            node = candidates[0] if len(candidates) == 1 else None
        if node is None:
            return False

        body = node.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body = body[1:]  # 剥 docstring——语句计数口径，非物理行口径
        return len(body) <= 1

    def _parse_match(self, item: dict) -> Finding:
        """解析 type=match 的 finding。"""
        source = item["source"]
        existing = item["existing"]
        return Finding(
            finding_id=item["finding_id"],
            severity=item["severity"],
            clone_type=item.get("clone_type", "T?"),
            similarity=float(item.get("similarity_score", 0.0)),
            source_file=source["filepath"],
            source_function=source["name"],
            source_lineno=int(source.get("lineno", 0)),
            existing_file=existing["filepath"],
            existing_function=existing["name"],
            existing_lineno=int(existing.get("lineno", 0)),
            import_suggestion=existing.get("import_suggestion"),
        )

    def _parse_group(self, item: dict) -> list[Finding]:
        """解析 type=group 的 finding（多副本组）。"""
        findings: list[Finding] = []
        functions = item.get("functions", [])
        if len(functions) < 2:
            return findings
        # group 的第一个函数是 source，其余是 existing
        source = functions[0]
        for existing in functions[1:]:
            findings.append(
                Finding(
                    finding_id=item.get("finding_id", ""),
                    severity=item["severity"],
                    clone_type=item.get("clone_type", "T?"),
                    similarity=float(item.get("similarity_score", 0.0)),
                    source_file=source["filepath"],
                    source_function=source["name"],
                    source_lineno=int(source.get("lineno", 0)),
                    existing_file=existing["filepath"],
                    existing_function=existing["name"],
                    existing_lineno=int(existing.get("lineno", 0)),
                    import_suggestion=None,
                )
            )
        return findings
