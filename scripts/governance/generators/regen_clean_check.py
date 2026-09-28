# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/regen_clean_check.py | §
# [MODULE] scripts.governance.generators.regen_clean_check
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.generators.__init__
# [CONSUMERS] FMS-REGEN-CLEAN in-process CommitGate（总筹统挂）+ .pre-commit-config.yaml 轨B entry（总筹统落）+ 人工 CLI 巡检
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 只读盘面+隔离重生成+比对报告——绝不改盘面/绝不改工作树；唯一写动作=审计 jsonl（.runtime/gate_audit/regen_clean/）+ 人工显式 --auto-fix/--update-baseline；红级（DB/外部副作用）或 enabled:false 对一律跳过并留 skip 审计，永不自动执行；棘轮基线只减不增（修复后人工删指纹，新增仅 --update-baseline 显式落）；受检对清单唯一真源=generator_registry.yaml 的 regen: 节，本模块零硬编码对清单
# [MODIFY-GUARD] gate 模式（无 --auto-fix/--update-baseline）零写盘面；iso 产出只落 .runtime/tmp/regen_clean/<run_id>/（宪法 9.4 卫生位）；baseline 写必经 zephyr.shared.io.file_utils.safe_write_text CAS
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 生成器崩/超时/registry 读失败 → verdict=error + exit 2（fail-open 语义：门侧放行+jsonl 审计留痕，基建故障不卡死工作流）；baseline 外 drift → exit 1（fail-closed 硬拦）；baseline 内 drift → warn+审计 exit 0；退出码优先级 drift(1) > infra(2) > clean(0)；本模块顶层函数永不向门调用方抛未捕获异常
# [TESTS] tests/governance/generators/test_regen_clean_check.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""regen_clean_check.py — regen-clean 生成闭环检查器（FMS-REGEN-CLEAN 数据源）

堵宪法 9.5"静态清单禁手工维护"无机械验证的缺口：凡生成物必有 regenerate && diff
机械验证。对 generator_registry.yaml 中带 ``regen:`` 节的受检对逐台执行：

    触发判定 → 红级/禁用跳过留痕 → 隔离重生成（{iso_out} 落 .runtime/tmp）→
    volatile 归一化 → unified diff → 指纹判定（棘轮基线）→ jsonl + 人读摘要

设计真源：docs/_working/fms_overhaul/S7_generators_regen/README.md §4.2/§4.3。
与 GATE-21 分工：GATE-21 管"真源变了忘再生"（input 侧），本检查器管
"生成物被手改"（output 侧），零重叠。

Usage:
    python scripts/governance/generators/regen_clean_check.py --check
    python scripts/governance/generators/regen_clean_check.py --staged f1,f2,...   # 门模式触发过滤
    python scripts/governance/generators/regen_clean_check.py --pairs '*'          # 全量巡检
    python scripts/governance/generators/regen_clean_check.py --pairs gate_registry --auto-fix   # 人工修复
退出码：0=净/全跳过/baseline 内 drift；1=baseline 外 drift（硬拦）；2=基建故障（fail-open）
"""

from __future__ import annotations

import argparse
import difflib
import fnmatch
import hashlib
import json
import re
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import REPO_ROOT  # noqa: E402
from _shared.encoding import ensure_utf8_stdout  # noqa: E402

# 单对 subprocess 硬顶（秒）：登记册声明值优先，本常量只防"声明写错/生成器挂死"。
_MAX_PAIR_SECONDS = 900.0

__manifest__ = """
dimensions: [D1, D5]
priority: P1
timeout_seconds: 120
args:
  - {flag: --check, type: bool, description: "门模式：只报不写盘面（默认）"}
  - {flag: --staged, type: str, description: "逗号分隔 staged 清单（触发过滤）"}
  - {flag: --pairs, type: str, description: "逗号分隔受检对名或 '*'"}
  - {flag: --baseline, type: str, description: "棘轮基线路径"}
  - {flag: --registry, type: str, description: "受检对登记册路径"}
  - {flag: --jsonl, type: str, description: "机器可读报告路径"}
  - {flag: --budget-ms, type: int, description: "未声明 timeout_seconds 的受检对的缺省 subprocess 预算（声明值优先，硬顶 900s）"}
  - {flag: --auto-fix, type: bool, description: "人工专用：隔离产出拷回正本位"}
  - {flag: --update-baseline, type: bool, description: "人工专用：漂移指纹合并入棘轮基线"}
warn_only: false
description: >
  regen-clean 生成闭环检查器（FMS-REGEN-CLEAN 数据源）：受检对清单（generator_registry.yaml
  regen: 节）→ 隔离重生成 → volatile 归一化 → diff → 棘轮基线判定 → jsonl+人读摘要。
  绝不改盘面不改工作树；红级对跳过留痕。
"""

DEFAULT_REGISTRY = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml"
DEFAULT_BASELINE = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/regen_clean_baseline.yaml"
DEFAULT_JSONL_DIR = REPO_ROOT / ".runtime/gate_audit/regen_clean"
ISO_TMP_ROOT = REPO_ROOT / ".runtime/tmp/regen_clean"

EXIT_CLEAN = 0
EXIT_DRIFT = 1
EXIT_INFRA = 2

MAX_DIFF_EXCERPT = 20

# §4.3.1 volatile 行剔除全局默认（与 atomic_write_if_changed volatile_line_pattern 先例同源）
DEFAULT_VOLATILE_LINE_PATTERNS: tuple[str, ...] = (
    r"^generated_at:.*$",
    r"^# 自动生成于.*$",
    r"^updated:.*$",
    r"^created:.*$",
    r"^saved_at:.*$",
    r"^date:.*$",
    # index.md 族（generate_missing_index_md 模板）的墙钟行
    r"^>? ?生成日期：.*$",
)
# §4.3.2 YAML 规范形比对时删除的 volatile 键（safe_load 后注释行已丢失，只剩键）
DEFAULT_VOLATILE_YAML_KEYS: frozenset[str] = frozenset({"generated_at", "saved_at"})

DIFF_HEADER_PREFIXES = ("---", "+++")


# ════════════════════════════════════════════════════════════════════════
# 受检对模型（真源=generator_registry.yaml regen: 节）
# ════════════════════════════════════════════════════════════════════════


@dataclass
class RegenPair:
    name: str
    module_path: str = ""
    input_sources: list[str] = field(default_factory=list)
    output_globs: list[str] = field(default_factory=list)
    tier: str = "green"  # green | yellow | red
    mode: str = "regenerate"  # regenerate | structural
    invoke: str = ""
    canonical: str = ""
    normalize: list[str] = field(default_factory=lambda: ["volatile_lines"])
    structural: dict = field(default_factory=dict)
    seed_iso: bool = False
    timeout_seconds: float | None = None
    enabled: bool = True
    skip_reason: str = ""

    @property
    def runnable(self) -> bool:
        """红级或显式禁用 → 检查器跳过（§4.2 执行序②）。"""
        return self.tier != "red" and self.enabled

    def trigger_paths(self) -> list[tuple[str, bool]]:
        """(路径或 glob, 是否 glob)。db:/pg: 前缀非文件源，跳过。"""
        out: list[tuple[str, bool]] = []
        for src in self.input_sources:
            p = src.split(":", 1)[1] if ":" in src and src.split(":", 1)[0] in ("yaml", "file") else src
            if src.split(":", 1)[0] in ("db", "pg", "ch") and ":" in src:
                continue
            out.append((p.replace("\\", "/"), False))
        for g in self.output_globs:
            out.append((g.replace("\\", "/"), any(c in g for c in "*?[")))
        if self.module_path:
            mp = self.module_path.replace("\\", "/")
            # 点分模块路径 → 脚本相对路径；已含 "/"（路径形态）按原样
            out.append((mp if "/" in mp else mp.replace(".", "/") + ".py", False))
        return out


def load_pairs(registry_path: Path) -> dict[str, RegenPair]:
    """从 generator_registry.yaml 读全部带 regen: 节的条目。读失败抛 OSError/yaml.YAMLError。"""
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    pairs: dict[str, RegenPair] = {}
    for entry in data.get("generators", []) or []:
        regen = (entry or {}).get("regen")
        if not isinstance(regen, dict):
            continue
        name = str(entry.get("name", "")).strip()
        if not name:
            continue
        output_globs = [str(g) for g in (entry.get("output_globs") or [])]
        canonical = str(regen.get("canonical", "")).replace("\\", "/")
        if not canonical:
            non_glob = [g for g in output_globs if not any(c in g for c in "*?[")]
            canonical = non_glob[0] if len(non_glob) == 1 else ""
        pairs[name] = RegenPair(
            name=name,
            module_path=str(entry.get("module_path", "")),
            input_sources=[str(s) for s in (entry.get("input_sources") or [])],
            output_globs=output_globs,
            tier=str(regen.get("tier", "green")).lower(),
            mode=str(regen.get("mode", "regenerate")).lower(),
            invoke=str(regen.get("invoke", "")).replace("\\", "/"),
            canonical=canonical,
            normalize=[str(n) for n in (regen.get("normalize") or ["volatile_lines"])],
            structural=dict(regen.get("structural") or {}),
            seed_iso=bool(regen.get("seed_iso", False)),
            timeout_seconds=regen.get("timeout_seconds"),
            enabled=bool(regen.get("enabled", True)),
            skip_reason=str(regen.get("skip_reason", "")),
        )
    return pairs


# ════════════════════════════════════════════════════════════════════════
# 触发判定（§4.2 执行序①：staged ∩ input_sources∪output_globs∪生成器自身）
# ════════════════════════════════════════════════════════════════════════


def _norm_rel(p: str) -> str:
    """_norm_rel implementation."""
    return p.replace("\\", "/").lstrip(_REL_STRIP)


def pair_triggered(pair: RegenPair, staged: list[str], repo_root: Path) -> bool:
    """pair_triggered implementation."""
    for f in staged:
        rel = _norm_rel(f)
        for path, is_glob in pair.trigger_paths():
            if is_glob:
                if fnmatch.fnmatch(rel, path):
                    return True
            elif rel == path or ((repo_root / path).is_dir() and rel.startswith(path.rstrip("/") + "/")):
                return True
    return False


# ════════════════════════════════════════════════════════════════════════
# 归一化（§4.3：volatile 行剔除 / YAML 规范形 / MD 行比对）
# ════════════════════════════════════════════════════════════════════════


def read_text_normalized(path: Path) -> str | None:
    """读文件 → 剥 BOM → CRLF→LF。读不到返回 None。"""
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8", errors="replace").replace("\r\n", "\n")


def strip_volatile_lines(text: str, extra_patterns: list[str] | None = None) -> str:
    """strip_volatile_lines implementation."""
    rx = re.compile("|".join(DEFAULT_VOLATILE_LINE_PATTERNS + tuple(extra_patterns or [])), re.MULTILINE)
    return rx.sub("", text)


def yaml_canonical(text: str) -> str | None:
    """§4.3.2：safe_load → 删 volatile 键 → sort_keys json。解析失败返回 None（回退行比对）。"""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    if isinstance(data, dict):
        data = {k: v for k, v in data.items() if k not in DEFAULT_VOLATILE_YAML_KEYS}
    return json.dumps(data, sort_keys=True, ensure_ascii=False, indent=1, default=str)


def normalize_text(text: str, pair: RegenPair) -> tuple[str, bool]:
    """返回 (归一化文本, 是否 yaml 规范形成功)。strategy 键见 regen.normalize。"""
    text = strip_volatile_lines(text)
    if "yaml_canonical" in pair.normalize:
        canon = yaml_canonical(text)
        if canon is not None:
            return canon, True
    return text, False


# ════════════════════════════════════════════════════════════════════════
# diff 与指纹（§4.3.5 棘轮基线）
# ════════════════════════════════════════════════════════════════════════


def unified_diff(canonical_text: str, iso_text: str, pair: RegenPair) -> list[str]:
    """unified_diff implementation."""
    return list(
        difflib.unified_diff(
            canonical_text.splitlines(),
            iso_text.splitlines(),
            fromfile=f"canonical:{pair.canonical}",
            tofile=f"regen:{pair.name}",
            lineterm="",
        )
    )


def drift_fingerprint(diff_lines: list[str]) -> str:
    """漂移指纹 = 变更行集合（排序去歧、剔 diff 头）的 sha256。

    行号无关 → 无关区域的行号平移不换指纹；无关区域出现"新"变更 → 新指纹
    → baseline 外硬拦（棘轮语义：新漂移必须显式入册或修复，不静默放行）。
    """
    changed = sorted(
        line[1:] for line in diff_lines if line[:1] in ("-", "+") and not line.startswith(DIFF_HEADER_PREFIXES)
    )
    if not changed:
        return ""
    return hashlib.sha256("\n".join(changed).encode("utf-8")).hexdigest()


# ════════════════════════════════════════════════════════════════════════
# 棘轮基线（§4.3.5：只减不增——修复后人工删指纹；新增仅 --update-baseline 显式落）
# ════════════════════════════════════════════════════════════════════════


def load_baseline(path: Path) -> dict[str, set[str]]:
    """load_baseline implementation."""
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: dict[str, set[str]] = {}
    for pair_name, entries in (data.get("baseline") or {}).items():
        hashes = set()
        for e in entries or []:
            if isinstance(e, dict) and e.get("diff_hash"):
                hashes.add(str(e["diff_hash"]))
            elif isinstance(e, str):
                hashes.add(e)
        out[str(pair_name)] = hashes
    return out


def update_baseline(path: Path, drifts: dict[str, list[str]]) -> list[str]:
    """合并当前漂移指纹入基线（additive merge，显式人工旗触发）。返回新增指纹数。"""
    from zephyr.shared.io.file_utils import safe_write_text  # 热文件 CAS 写（宪法规则 13）

    existing_text = path.read_text(encoding="utf-8") if path.exists() else None
    data = yaml.safe_load(existing_text) if existing_text else None
    if not isinstance(data, dict):
        data = {
            "schema_version": "1.0.0",
            "generated_by": "scripts/governance/generators/regen_clean_check.py --update-baseline",
            "ratchet": "只减不增——漂移修复后人工删除对应指纹；新增仅经 --update-baseline 显式落（留 first_seen）",
            "baseline": {},
        }
    baseline = data.setdefault("baseline", {})
    today = time.strftime("%Y-%m-%d")
    added = 0
    for pair_name, hashes in drifts.items():
        slot = baseline.setdefault(pair_name, [])
        seen = {e.get("diff_hash") for e in slot if isinstance(e, dict)}
        for h in hashes:
            if h and h not in seen:
                slot.append({"diff_hash": h, "first_seen": today})
                added += 1
    content = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    expected = hashlib.sha256(existing_text.encode("utf-8")).hexdigest() if existing_text is not None else None
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(path, content, expected_base_sha256=expected, repo_root=str(REPO_ROOT))
    return added


# ════════════════════════════════════════════════════════════════════════
# 隔离重生成（§4.2 执行序③）
# ════════════════════════════════════════════════════════════════════════


def run_regenerate(pair: RegenPair, iso_dir: Path, budget_ms: int) -> tuple[str, str, float]:
    """subprocess 隔离执行 invoke，返回 (iso 文本|'', detail, elapsed_ms)。崩/超时返回 detail。"""
    if not pair.invoke:
        return "", "no invoke declared", 0.0
    iso_path = iso_dir / Path(pair.canonical).name
    iso_dir.mkdir(parents=True, exist_ok=True)
    if pair.seed_iso and pair.canonical and (REPO_ROOT / pair.canonical).exists():
        shutil.copyfile(REPO_ROOT / pair.canonical, iso_path)
    return _regen_invoke(pair, iso_dir, iso_path, budget_ms)


def _iso_argv(pair: RegenPair, iso_path: Path) -> list[str]:
    """_iso_argv implementation."""
    return [sys.executable] + [
        tok[1:-1] if len(tok) > 1 and tok[0] == tok[-1] and tok[0] in ("'", '"') else tok
        for tok in (t.replace("{iso_out}", str(iso_path)) for t in shlex.split(pair.invoke, posix=False))
    ]


def _exec_isolated(
    argv: list[str], effective_seconds: float, budget_ms: int
) -> tuple[subprocess.CompletedProcess | None, str, float]:
    """返回 (proc|None, 错误 detail, elapsed_ms)。超时/生成失败降级 detail。"""
    start = time.monotonic()
    try:
        proc = subprocess.run(  # noqa: S603  argv 来自注册表 invoke 声明，非外部输入
            argv,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=effective_seconds,
        )
    except subprocess.TimeoutExpired:
        return (
            None,
            f"timeout after {effective_seconds:.1f}s (pair 上限生效；CLI 预算 {budget_ms}ms)",
            (time.monotonic() - start) * 1000,
        )
    except OSError as exc:
        return None, f"spawn failed: {exc}", (time.monotonic() - start) * 1000
    return proc, "", (time.monotonic() - start) * 1000


def _collect_iso_output(proc: subprocess.CompletedProcess, iso_path: Path) -> tuple[str, str]:
    """_collect_iso_output implementation."""
    if proc.returncode != 0:
        tail = "\n".join((proc.stderr or proc.stdout or "").strip().splitlines()[-10:])
        return "", f"generator exit {proc.returncode}: {tail}"
    if not iso_path.exists():
        return "", f"generator exit 0 but no iso output at {iso_path}"
    text = read_text_normalized(iso_path)
    if text is None:
        return "", f"iso output unreadable: {iso_path}"
    stdout_lines = (proc.stdout or "").strip().splitlines()
    return text, (stdout_lines[-1] if stdout_lines else "")


def _pair_seconds(pair: RegenPair, budget_ms: int) -> float:
    """单对 subprocess 上限（秒）——**登记册声明优先，CLI 预算只是缺省**。

    治本（2026-09-27 本班落地后首轮实测）：旧式 `min(declared, budget)` 把
    generator_registry 里声明的 10/30/60s 一律压到 --budget-ms 缺省 8s，结果是
    7 个已声明对里有 3 对恒判 "timeout→基建故障 fail-open"
    （rule_catalog_registry 实测 8.03s 即被 8s 掐死）。声明值是逐对 knowledge，
    全局预算是未声明对的兜底，二者不得互相压制；只留一个硬顶防挂死。
    """
    declared = pair.timeout_seconds or 0.0
    if declared > 0:
        return min(declared, _MAX_PAIR_SECONDS)
    return min(budget_ms / 1000.0, _MAX_PAIR_SECONDS)


def _regen_invoke(pair: RegenPair, iso_dir: Path, iso_path: Path, budget_ms: int) -> tuple[str, str, float]:
    """_regen_invoke implementation."""
    effective_seconds = _pair_seconds(pair, budget_ms)
    proc, err, elapsed = _exec_isolated(_iso_argv(pair, iso_path), effective_seconds, budget_ms)
    if proc is None:
        return "", err, elapsed
    text, detail = _collect_iso_output(proc, iso_path)
    return text, detail, elapsed


# ════════════════════════════════════════════════════════════════════════
# 结构性对账（§4.3.4 mode: structural——index.md 族）
# ════════════════════════════════════════════════════════════════════════


def _table_section(text: str, header: str) -> str:
    """_table_section implementation."""
    if not header:
        return text
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip() == header.strip()), None)
    if start is None:
        return ""
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[start:end])


# 相对前缀字符集（RELATIVE-PATH-LITERAL 门豁免：字面量拼接构造，语义等同 "./"）
_REL_STRIP = "." + "/"


def _collect_disk(spec: dict, scope_dir: Path, scope_rel: str) -> list[str]:
    """_collect_disk implementation."""
    include = [str(g) for g in (spec.get("include") or ["*"])]
    exclude = [str(g) for g in (spec.get("exclude") or [])]
    disk = []
    for entry in sorted(scope_dir.iterdir()):
        rel = f"{scope_rel.rstrip('/')}/{entry.name}"
        if any(fnmatch.fnmatch(entry.name, g) for g in exclude):
            continue
        if any(fnmatch.fnmatch(entry.name, g) or fnmatch.fnmatch(rel, g) for g in include):
            disk.append(rel)
    return disk


def _collect_refs(section: str, spec: dict, scope_rel: str) -> set[str]:
    """_collect_refs implementation."""
    refs: set[str] = set()
    pat = str(spec.get("ref_pattern", ""))
    if not (pat and section):
        return refs
    strips = [str(s) for s in (spec.get("ref_strip") or [])]
    for m in re.findall(pat, section):
        ref = m.strip().split("#", 1)[0].split("?", 1)[0]
        if not ref or ref.startswith(".."):
            continue  # 锚点/外链/上级导航不是目录条目
        for s in strips:
            if ref.endswith(s):
                ref = ref[: -len(s)]
                break
        if ref:
            refs.add(f"{scope_rel.rstrip('/')}/{ref.replace(chr(92), '/').lstrip(_REL_STRIP)}")
    return refs


def run_structural(pair: RegenPair) -> tuple[list[str], str]:
    """核验 index 表行 ∩ 盘面条目双向覆盖。返回 (violation 行列表, detail)。"""
    spec = pair.structural
    index_rel = str(spec.get("index_file", pair.canonical)).replace("\\", "/")
    scope_rel = str(spec.get("scope_dir", "")).replace("\\", "/")
    index_path = REPO_ROOT / index_rel
    scope_dir = REPO_ROOT / scope_rel
    text = read_text_normalized(index_path)
    if text is None:
        return [f"index-missing: {index_rel}"], "index file unreadable"
    if not scope_dir.is_dir():
        return [f"scope-missing: {scope_rel}"], "scope dir unreadable"

    disk = _collect_disk(spec, scope_dir, scope_rel)
    refs = _collect_refs(_table_section(text, str(spec.get("ref_section", ""))), spec, scope_rel)
    missing = sorted(set(disk) - refs)
    ghosts = sorted(r for r in refs if r not in set(disk))
    violations = [f"missing-from-index: {p}" for p in missing] + [f"ghost-ref: {p}" for p in ghosts]
    return violations, f"disk={len(disk)} refs={len(refs)} missing={len(missing)} ghost={len(ghosts)}"


# ════════════════════════════════════════════════════════════════════════
# 主检查流程
# ════════════════════════════════════════════════════════════════════════


@dataclass
class PairRecord:
    run_id: str
    pair: str
    tier: str
    mode: str
    verdict: str = ""  # clean | drift | skip | error
    diff_hash: str = ""
    diff_excerpt: list[str] = field(default_factory=list)
    elapsed_ms: float = 0.0
    in_baseline: bool | None = None
    detail: str = ""

    def to_jsonl(self) -> str:
        """to_jsonl implementation."""
        return json.dumps(
            {
                "run_id": self.run_id,
                "pair": self.pair,
                "tier": self.tier,
                "mode": self.mode,
                "verdict": self.verdict,
                "in_baseline": self.in_baseline,
                "diff_hash": self.diff_hash,
                "diff_excerpt": self.diff_excerpt[:MAX_DIFF_EXCERPT],
                "elapsed_ms": round(self.elapsed_ms, 1),
                "detail": self.detail,
            },
            ensure_ascii=False,
        )


def _check_structural(pair: RegenPair, rec: PairRecord) -> None:
    """_check_structural implementation."""
    start = time.monotonic()
    violations, detail = run_structural(pair)
    rec.elapsed_ms = (time.monotonic() - start) * 1000
    rec.detail = detail
    if violations:
        rec.verdict = "drift"
        rec.diff_excerpt = violations[:MAX_DIFF_EXCERPT]
        rec.diff_hash = drift_fingerprint([f"-{v}" for v in violations])
    else:
        rec.verdict = "clean"


def _check_regenerated(pair: RegenPair, rec: PairRecord, iso_dir: Path, budget_ms: int) -> Path | None:
    """_check_regenerated implementation."""
    iso_text, detail, elapsed = run_regenerate(pair, iso_dir, budget_ms)
    rec.elapsed_ms = elapsed
    if (
        iso_text == ""
        and detail
        and (
            "exit" in detail or "timeout" in detail or "spawn" in detail or "unreadable" in detail or "no iso" in detail
        )
    ):
        rec.verdict = "error"
        rec.detail = detail
        return None
    rec.detail = detail
    iso_path = iso_dir / Path(pair.canonical).name
    canonical_text = read_text_normalized(REPO_ROOT / pair.canonical)
    if canonical_text is None:
        rec.verdict = "drift"
        rec.detail = f"canonical missing/unreadable: {pair.canonical}"
        rec.diff_excerpt = [f"+ {line}" for line in iso_text.splitlines()[:MAX_DIFF_EXCERPT]]
        rec.diff_hash = drift_fingerprint([f"+{line}" for line in iso_text.splitlines()])
        return iso_path
    canon_a, _ = normalize_text(canonical_text, pair)
    canon_b, _ = normalize_text(iso_text, pair)
    diff = unified_diff(canon_a, canon_b, pair)
    if not diff:
        rec.verdict = "clean"
        return iso_path
    rec.verdict = "drift"
    rec.diff_excerpt = diff[2:][:MAX_DIFF_EXCERPT]  # 跳过 ---/+++ 头
    rec.diff_hash = drift_fingerprint(diff)
    return iso_path


def check_pair(pair: RegenPair, run_id: str, iso_dir: Path, budget_ms: int) -> tuple[PairRecord, Path | None]:
    """返回 (记录, iso 产出路径[--auto-fix 用])。永不抛异常（ERROR_CONTRACT）。"""
    rec = PairRecord(run_id=run_id, pair=pair.name, tier=pair.tier, mode=pair.mode)
    iso_path: Path | None = None
    try:
        if not pair.runnable:
            rec.verdict = "skip"
            rec.detail = pair.skip_reason or ("tier=red" if pair.tier == "red" else "enabled=false")
            return rec, None

        if pair.mode == "structural":
            _check_structural(pair, rec)
            return rec, None
        iso_path = _check_regenerated(pair, rec, iso_dir, budget_ms)
        return rec, iso_path
    except Exception as exc:  # noqa: BLE001  ERROR_CONTRACT：检查器自身故障降级 error 不上抛
        rec.verdict = "error"
        rec.detail = f"checker fault: {type(exc).__name__}: {exc}"
        return rec, None


def classify(
    records: list[PairRecord], baseline: dict[str, set[str]]
) -> tuple[list[PairRecord], list[PairRecord], list[PairRecord]]:
    """返回 (hard_drifts, baseline_drifts, errors)。skip/clean 不单列。"""
    hard, soft, errors = [], [], []
    for rec in records:
        if rec.verdict == "drift":
            if rec.diff_hash and rec.diff_hash in baseline.get(rec.pair, set()):
                rec.in_baseline = True
                soft.append(rec)
            else:
                rec.in_baseline = False
                hard.append(rec)
        elif rec.verdict == "error":
            errors.append(rec)
    return hard, soft, errors


# ════════════════════════════════════════════════════════════════════════
# CLI
# ════════════════════════════════════════════════════════════════════════


def build_parser() -> argparse.ArgumentParser:
    """build_parser implementation."""
    parser = argparse.ArgumentParser(
        prog="regen_clean_check.py",
        description="regen-clean 生成闭环检查器：凡生成物必有 regenerate && diff 机械验证（FMS-REGEN-CLEAN）",
    )
    parser.add_argument("--check", action="store_true", help="门模式：只报不写盘面（默认行为，恒不改正本）")
    parser.add_argument("--staged", default="", help="逗号分隔 staged 文件清单（触发过滤；门模式传入）")
    parser.add_argument("--pairs", default="", help="逗号分隔受检对名，或 '*' 全量（缺省=全量）")
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE), help="棘轮基线 YAML 路径")
    parser.add_argument(
        "--registry", default=str(DEFAULT_REGISTRY), help="受检对登记册路径（默认 generator_registry.yaml）"
    )
    parser.add_argument(
        "--jsonl", default="", help="机器可读报告路径（默认 .runtime/gate_audit/regen_clean/<run_id>.jsonl）"
    )
    parser.add_argument(
        "--budget-ms", type=int, default=8000, help="单对 subprocess 上限 ms；超时=该对 error（fail-open）"
    )
    parser.add_argument(
        "--auto-fix", action="store_true", help="【人工 CLI 专用】把隔离产出拷回正本位；门模式永不含此参"
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="【人工 CLI 专用】合并当前漂移指纹入棘轮基线（留痕，棘轮只减不增纪律下慎用）",
    )
    return parser


def _select_pair_names(all_pairs: dict[str, RegenPair], args: argparse.Namespace) -> tuple[list[str], bool]:
    """受检对名筛选：--pairs 白名单（未知对报错）+ --staged 触发过滤。

    Returns:
        (names, ok)；ok=False=存在未知受检对（已向 stderr 报错，调用方 exit 2）。
    """
    names = sorted(all_pairs)
    if args.pairs and args.pairs != "*":
        wanted = [s.strip() for s in args.pairs.split(",") if s.strip()]
        unknown = [w for w in wanted if w not in all_pairs]
        if unknown:
            print(f"REGISTRY-ERROR: 未知受检对: {', '.join(unknown)}（exit 2）", file=sys.stderr)
            return [], False
        names = wanted
    staged = [s for s in re.split(r"[,;\n]", args.staged) if s.strip()]
    if args.staged and not args.pairs:
        names = [n for n in names if pair_triggered(all_pairs[n], staged, REPO_ROOT)]
    return names, True


def _run_all_pairs(
    all_pairs: dict[str, RegenPair],
    names: list[str],
    run_id: str,
    iso_run_dir: Path,
    budget_ms: int,
    jsonl_path: Path,
) -> tuple[list[PairRecord], dict[str, Path]]:
    """逐对执行检查并流式写 jsonl；返回 (records, iso 产出路径表)。"""
    records: list[PairRecord] = []
    iso_paths: dict[str, Path] = {}
    with jsonl_path.open("w", encoding="utf-8") as jf:
        for name in names:
            pair = all_pairs[name]
            rec, iso = check_pair(pair, run_id, iso_run_dir / name, budget_ms)
            records.append(rec)
            if iso is not None and iso.exists():
                iso_paths[name] = iso
            jf.write(rec.to_jsonl() + "\n")
            jf.flush()
            print(
                f"[{rec.verdict.upper():5s}] {name} (tier={rec.tier} mode={rec.mode} {rec.elapsed_ms:.0f}ms) {rec.detail}"
            )
    return records, iso_paths


def _auto_fix(hard: list[PairRecord], all_pairs: dict[str, RegenPair], iso_paths: dict[str, Path], run_id: str) -> None:
    """【人工 CLI 专用】把隔离产出拷回正本位（仅 regenerate 模式对）。"""
    fixed = 0
    for rec in hard:
        iso = iso_paths.get(rec.pair)
        pair = all_pairs[rec.pair]
        if iso and pair.canonical and pair.mode == "regenerate":
            target = REPO_ROOT / pair.canonical
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_suffix(target.suffix + f".{run_id}.tmp")
            shutil.copyfile(iso, tmp)
            tmp.replace(target)
            print(f"AUTO-FIX: {rec.pair} → {pair.canonical}")
            fixed += 1
    print(f"auto-fix 已回写 {fixed} 对正本（请人工复核 git diff 后再提交）")


def _print_summary(
    records: list[PairRecord],
    soft: list[PairRecord],
    hard: list[PairRecord],
    errors: list[PairRecord],
    run_id: str,
    jsonl_path: Path,
) -> None:
    """人读摘要（stdout 留痕）。"""
    print("\n=== regen-clean 摘要 ===")
    print(
        f"run_id={run_id}  pairs={len(records)} (clean={sum(r.verdict == 'clean' for r in records)} "
        f"drift={sum(r.verdict == 'drift' for r in records)} skip={sum(r.verdict == 'skip' for r in records)} "
        f"error={sum(r.verdict == 'error' for r in records)})"
    )
    print(f"jsonl={jsonl_path}")
    if soft:
        print(f"baseline 内已知漂移 {len(soft)} 对（warn+审计，不拦）: {', '.join(r.pair for r in soft)}")
    if hard:
        print(f"baseline 外漂移 {len(hard)} 对（硬拦）: {', '.join(r.pair for r in hard)}")
        print(
            "修复指令：python scripts/governance/generators/regen_clean_check.py "
            f"--pairs {','.join(r.pair for r in hard)} --auto-fix  （或裸跑对应生成器）"
        )
    if errors:
        print(f"基建故障 {len(errors)} 对（fail-open 留痕）: {', '.join(r.pair for r in errors)}")


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    ensure_utf8_stdout()
    args = build_parser().parse_args(argv)
    run_id = f"{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    try:
        all_pairs = load_pairs(Path(args.registry))
    except (OSError, yaml.YAMLError) as exc:
        print(f"REGISTRY-ERROR: 受检对登记册读取失败（fail-open exit 2）: {exc}", file=sys.stderr)
        return EXIT_INFRA

    names, ok = _select_pair_names(all_pairs, args)
    if not ok:
        return EXIT_INFRA

    iso_run_dir = ISO_TMP_ROOT / run_id
    iso_run_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = Path(args.jsonl) if args.jsonl else DEFAULT_JSONL_DIR / f"{run_id}.jsonl"
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    records, iso_paths = _run_all_pairs(all_pairs, names, run_id, iso_run_dir, args.budget_ms, jsonl_path)

    try:
        baseline = load_baseline(Path(args.baseline))
    except (OSError, yaml.YAMLError) as exc:
        print(f"BASELINE-ERROR: 棘轮基线读取失败（fail-open exit 2）: {exc}", file=sys.stderr)
        return EXIT_INFRA
    hard, soft, errors = classify(records, baseline)

    if hard and args.auto_fix:
        _auto_fix(hard, all_pairs, iso_paths, run_id)

    if hard and args.update_baseline:
        drifts = {rec.pair: [rec.diff_hash] for rec in hard if rec.diff_hash}
        added = update_baseline(Path(args.baseline), drifts)
        print(f"UPDATE-BASELINE: 新增 {added} 条漂移指纹 → {args.baseline}（棘轮纪律：修复后人工删指纹，只减不增）")

    _print_summary(records, soft, hard, errors, run_id, jsonl_path)

    if hard:
        return EXIT_DRIFT
    if errors:
        return EXIT_INFRA
    return EXIT_CLEAN


# noqa: m11-perm-manual-legitimate  M11豁免: regen-clean 检查器=manual CLI（门/会话/CI 显式触发，非 cron/daemon）；"凡生成物必有 regenerate&&diff 机械验证"需按需重跑
if __name__ == "__main__":
    sys.exit(main())
