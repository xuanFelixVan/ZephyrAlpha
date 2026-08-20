# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_registry_code_anchor.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_registry_code_anchor
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.registry_code_anchor_gate
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 15 个含 code 锚点的业务注册表 code_path/code_symbol 存在性校验; 条目 id 键 vs 所在列表纯净性校验（[List-Purity]，#118 DS-104 错位治本）; 合并态豁免
# [MODIFY-GUARD] gate_id="REGISTRY-CODE-ANCHOR"; #ARCH-BREG-002 门禁A
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 检测失败→exit 1+violation清单; 成功→exit 0; 环境异常→exit 2
# [TESTS] tests/governance/commit_gates/test_registry_code_anchor_gate.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_registry_code_anchor.py —— 业务注册表代码锚点存在性校验（#ARCH-BREG-002 门禁A）

病根：18 个业务注册表的 code_path 仅到文件级且无任何存在性校验——代码改名/删除后
库条目静默漂移（data_asset 已有 13 条存量锚点漂移实证），algorithm_status=quantized
无机制保证代码真实存在。

检查内容（分域真源：实现域 owner=代码，库侧锚点必须真实）：
  1. code_path 非空 → 指向的文件/目录必须存在（目录锚点合法；支持 "+" 连接的多路径；
     剥离中文/英文括号注释后缀，如 "src/x.py（已删除）" → "src/x.py"）
  2. code_symbol 非空 → 格式 <relative_path>::<symbol>；文件必须存在；
     .py 文件额外做 AST 符号存在性校验（顶层 def/class 名或 Class.method 点号）
  3. status ∈ {deprecated, retired} 的条目豁免——锚点为历史记录（tombstone），非活链接
  4. [List-Purity] 列表纯净性（#118，2026-08-17）：条目缺本列表期望 id 键却携带
     外列表 id 键 → 错位违规（如 dataset 条目被追加进 jobs 列表——AI 只写文件尾
     不看分区实证的静默漂移；错位条目对"按列表键读取"的未来消费者会整条蒸发）

合并态豁免（同 check_rule_four_way_alignment.py 惯例）：
  .git/MERGE_HEAD 存在时半合并工作区不可信 → SKIP 返回 exit 0。

Usage:
    python check_registry_code_anchor.py            # 全量 15 库扫描
    python check_registry_code_anchor.py --files docs/.../factor_registry.yaml  # 限定范围
exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML 未安装")
    sys.exit(EXIT_ERROR)

__manifest__ = """
args:
- --ci
- --files
description: 业务注册表代码锚点存在性校验（code_path/code_symbol，#ARCH-BREG-002 门禁A）
dimensions:
- D5
priority: P1
timeout_seconds: 60
warn_only: false
"""

_CATALOGS = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"

# 含 code 锚点（code_path/code_symbol）的 15 个业务注册表（seat/event/macro 无锚点豁免）
# file -> (主条目列表键, 条目 id 字段)
REGISTRY_LISTS: dict[str, list[str]] = {
    "factor_registry.yaml": ["factors"],
    "strategy_registry.yaml": ["strategies"],
    "technical_indicator_registry.yaml": ["indicators"],
    "universe_registry.yaml": ["universes"],
    "benchmark_registry.yaml": ["benchmarks"],
    "cost_model_registry.yaml": ["cost_models"],
    "execution_algo_registry.yaml": ["execution_algos"],
    "risk_limit_registry.yaml": ["risk_limits"],
    "data_asset_registry.yaml": ["sources", "datasets", "jobs"],
    "chart_pattern_registry.yaml": ["chart_patterns"],
    "field_dictionary.yaml": ["fields"],
    "experiment_registry.yaml": ["experiments"],
    "model_registry.yaml": ["models"],
    "regime_cycle_registry.yaml": ["cycles"],
    "portfolio_model_registry.yaml": ["portfolio_models"],
}

# 条目 id 字段探测顺序（取首个命中的非空字段）
_ID_KEYS = (
    "factor_id",
    "strategy_id",
    "indicator_id",
    "universe_id",
    "benchmark_id",
    "cost_model_id",
    "execution_algo_id",
    "risk_limit_id",
    "source_id",
    "dataset_id",
    "job_id",
    "pattern_id",
    "field_id",
    "experiment_id",
    "model_id",
    "cycle_id",
    "event_type_id",
)

# 列表键 → 期望条目 id 键的 fallback 映射（[List-Purity]，#118）。
# 首选真源是各注册表文件自身的 unique_key 声明（见 _expected_id_keys，SSoT 防
# 第二真源漂移——portfolio_models 的合法 id 键实为 model_id 即实证）；本映射仅在
# 注册表未声明 unique_key 时兜底。条目缺本列表期望键却含其他已知 id 键 = 写错列表
# （如 DS-104 混入 jobs）。
_LIST_ID_KEYS: dict[str, str] = {
    "factors": "factor_id",
    "strategies": "strategy_id",
    "indicators": "indicator_id",
    "universes": "universe_id",
    "benchmarks": "benchmark_id",
    "cost_models": "cost_model_id",
    "execution_algos": "execution_algo_id",
    "risk_limits": "risk_limit_id",
    "sources": "source_id",
    "datasets": "dataset_id",
    "jobs": "job_id",
    "chart_patterns": "pattern_id",
    "fields": "field_id",
    "experiments": "experiment_id",
    "models": "model_id",
    "cycles": "cycle_id",
    "portfolio_models": "model_id",
}


def _expected_id_keys(reg_name: str, data: dict) -> dict[str, str]:
    """列表键→期望条目 id 键：优先读注册表自身 unique_key 声明（SSoT），
    未声明的列表回退 _LIST_ID_KEYS 静态映射。"""
    out: dict[str, str] = {}
    uk = data.get("unique_key")
    if isinstance(uk, dict):  # data_asset 多列表形态：{列表键: [id键, ...]}
        for lk, keys in uk.items():
            if isinstance(keys, list) and keys:
                out[lk] = str(keys[0])
    elif isinstance(uk, list) and uk:  # 单列表形态：[id键]
        for lk in REGISTRY_LISTS.get(reg_name, []):
            out[lk] = str(uk[0])
    for lk in REGISTRY_LISTS.get(reg_name, []):
        if lk not in out and lk in _LIST_ID_KEYS:
            out[lk] = _LIST_ID_KEYS[lk]
    return out


# code_symbol 格式： <relative_path>::<symbol>
_SYMBOL_SEP = "::"


def _is_merge_in_progress() -> bool:
    """检测合并是否进行中（.git/MERGE_HEAD 存在）——半合并工作区不可信，豁免。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(REPO_ROOT),
        )
        if result.returncode != 0:
            return False
        return (Path(result.stdout.strip()) / "MERGE_HEAD").exists()
    except Exception:  # noqa: BLE001 — 检测失败保守返回 False（不豁免，正常检查）
        return False


def _entry_id(entry: dict) -> str:
    """_entry_id implementation."""
    for k in _ID_KEYS:
        v = entry.get(k)
        if v:
            return str(v)
    return "(unknown)"


def _py_symbols(py_path: Path) -> set[str]:
    """提取 .py 文件的可用符号集（顶层 def/class 名 + Class.method 点号）。

    AST 解析失败（语法错误/编码问题）返回 None——调用方按 exit 2 环境异常处理。
    """
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None
    symbols: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.add(node.name)
        if isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.add(f"{node.name}.{sub.name}")
    return symbols


def _strip_anchor_annotation(token: str) -> str:
    """剥离锚点注释后缀（中文/英文括号起）：'src/x.py（已删除）' → 'src/x.py'。"""
    for sep in ("（", "("):
        if sep in token:
            token = token.split(sep, 1)[0]
    return token.strip()


def _split_code_paths(code_path: str) -> list[str]:
    """code_path 支持 "+" 连接多路径；仅返回含 "/" 的路径 token（滤掉 N/A 等非路径）。"""
    tokens = [t.strip() for t in str(code_path).split("+")]
    return [_strip_anchor_annotation(t) for t in tokens if "/" in t and not t.startswith("#")]


def check_registry_file(reg_path: Path, violations: list[str]) -> int:
    """校验单个注册表文件的条目锚点。返回检查条目数。"""
    try:
        data = yaml.safe_load(reg_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        violations.append(f"  - [Parse] {reg_path.name} YAML 解析失败: {e}")
        return 0
    lists = REGISTRY_LISTS[reg_path.name]
    expected_map = _expected_id_keys(reg_path.name, data)
    n = 0
    for lk in lists:
        for entry in data.get(lk) or []:
            if not isinstance(entry, dict):
                continue
            n += 1
            eid = _entry_id(entry)
            # [List-Purity]（#118）：缺本列表期望 id 键却携带外列表 id 键 → 错位违规。
            # 判定精准化：缺 id 且无外键的条目不报（保持现状语义）；deprecated/retired
            #  tombstone 同样须在正确列表（错位不豁免——漂移史即错位来源之一）。
            expected_key = expected_map.get(lk)
            if expected_key and not entry.get(expected_key):
                foreign = [k for k in _ID_KEYS if k != expected_key and entry.get(k)]
                if foreign:
                    violations.append(
                        f"  - [List-Purity] {reg_path.name} {lk}/{eid}: "
                        f"条目缺本列表 id 键 '{expected_key}'，却含外列表键 '{foreign[0]}'"
                        f"——条目疑似写错列表（错位）"
                    )
            # status ∈ {deprecated, retired}：锚点为历史记录（tombstone），豁免存在性校验
            if entry.get("status") in ("deprecated", "retired"):
                continue
            code_path = entry.get("code_path")
            if code_path:
                for rel in _split_code_paths(code_path):
                    if rel and not (REPO_ROOT / rel).exists():
                        violations.append(f"  - [Anchor↔Disk] {reg_path.name} {lk}/{eid}: code_path 不存在: {rel}")
            code_symbol = entry.get("code_symbol")
            if code_symbol:
                sym = str(code_symbol)
                if _SYMBOL_SEP not in sym:
                    violations.append(f"  - [Format] {reg_path.name} {lk}/{eid}: code_symbol 缺少 '::' 分隔: {sym}")
                    continue
                rel, _, symbol = sym.partition(_SYMBOL_SEP)
                rel = _strip_anchor_annotation(rel)
                target = REPO_ROOT / rel
                if not target.is_file():
                    violations.append(f"  - [Anchor↔Disk] {reg_path.name} {lk}/{eid}: code_symbol 文件不存在: {rel}")
                    continue
                if target.suffix == ".py" and symbol.strip():
                    symbols = _py_symbols(target)
                    if symbols is None:
                        violations.append(
                            f"  - [Parse] {reg_path.name} {lk}/{eid}: code_symbol 目标文件 AST 解析失败: {rel}"
                        )
                    elif symbol.strip() not in symbols:
                        violations.append(
                            f"  - [Anchor↔Code] {reg_path.name} {lk}/{eid}: 符号不存在: {rel}::{symbol.strip()}"
                        )
    return n


def check(files: list[str] | None = None) -> int:
    """主检查函数。files=None 全量 15 库；否则仅检查给定注册表文件。返回 exit code。"""
    if _is_merge_in_progress():
        print("[SKIP] 合并进行中（MERGE_HEAD 存在）——半合并态工作区不可信，锚点检查豁免")
        return EXIT_PASS

    if files:
        targets = []
        for f in files:
            p = Path(f)
            name = p.name
            if name in REGISTRY_LISTS:
                targets.append(p if p.is_absolute() else REPO_ROOT / p)
        if not targets:
            print("[PASS] 无注册表文件在检查范围内")
            return EXIT_PASS
    else:
        targets = [_CATALOGS / fn for fn in REGISTRY_LISTS]

    violations: list[str] = []
    total = 0
    for t in targets:
        if not t.is_file():
            violations.append(f"  - [Disk] 注册表文件不存在: {t.name}")
            continue
        total += check_registry_file(t, violations)

    if violations:
        print("[FAIL] 业务注册表代码锚点校验检测到违规（REGISTRY_CODE_ANCHOR_VIOLATION）：")
        for v in violations[:50]:
            print(v)
        if len(violations) > 50:
            print(f"  ... 共 {len(violations)} 条（前 50 条展示）")
        print(
            "\n修复：代码改名/删除后须同步更新库条目 code_path/code_symbol，"
            "或将条目标记 deprecated（分域真源：实现域 owner=代码，#ARCH-BREG-002）；"
            "[List-Purity] 错位条目须移入其 id 键对应的列表（datasets/jobs/sources 等，#118）。"
        )
        return EXIT_FINDINGS

    print(f"[PASS] 业务注册表代码锚点校验通过（扫描 {len(targets)} 库 {total} 条目）")
    return EXIT_PASS


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="业务注册表代码锚点存在性校验（code_path/code_symbol，#ARCH-BREG-002 门禁A）"
    )
    parser.add_argument("--ci", action="store_true", help="CI 模式（无交互，违规即 exit 1）")
    parser.add_argument("--files", nargs="*", default=None, help="限定检查的注册表文件（默认全量 15 库）")
    args = parser.parse_args()
    sys.exit(check(files=args.files))


if __name__ == "__main__":
    main()
