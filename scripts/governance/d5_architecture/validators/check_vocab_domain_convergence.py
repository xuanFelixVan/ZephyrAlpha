# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/check_vocab_domain_convergence.py | §
# [MODULE] scripts.governance.d5_architecture.validators.check_vocab_domain_convergence
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 硬条件=(FDR 在用域 ∪ 翻译注册表在用域) − (词表 values∪aliases∪deprecated) = ∅，非空 exit 1；DB domains 表差集仅 --with-db 时输出且永远 advisory（不置 exit）；词表合法值经 yaml_utils SSoT 加载，本件零硬编码域清单（裁定#335 反散文计数）
# [MODIFY-GUARD] 新增在用域未进词表时本件变红——修复方向=收编词表或标别名，禁止反向放宽本件
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 词表/注册文件缺失或 YAML 解析失败→exit 2（观测工具不静默吞错）；DB 连接失败→--with-db 下打印告警并降级为无 DB 视图，不改 exit 语义
# [TESTS] tests/governance/d5_architecture/test_check_vocab_domain_convergence.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动/CI 触发的观测型校验器，与 validate_target_layer 同族非驻留件
r"""
对标：target_layer_vocabulary.yaml（裁定#335 收编后 v1.1.0）——三源域差集常驻收敛校验
职责：把"词表滞后于在用注册表"从季度考古变成命令级红灯（裁定#335 结论 8）

口径：
- 词表 known = values[].value ∪ values[].aliases ∪ deprecated_values（经 yaml_utils SSoT）
- 在用 = functional_domain_registry.yaml 的 D_* 域 ∪ module_translation_registry.yaml 的 domain_id
- 硬条件：在用 − known = ∅，否则 exit 1 并逐值列账
- advisory：depgraph DB domains 表 − known（--with-db），列出但不置非零——
  DB 侧 *_SCRIPTS 家族+D_TEST 约 10 域属脚本治理命名空间，收编与否另案（w2 裁定文档留案）

三层防线定位：Layer 2 — 检测（W6 循环检查/CI 手动运行）

exit codes: 0=收敛, 1=差集非空, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- --with-db
- --quiet
description: 词表×FDR×翻译注册表在用域差集收敛校验（裁定#335 常驻观测件）
dimensions:
- D5
priority: P1
timeout_seconds: 60
warn_only: false
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from zephyr.shared.io.yaml_utils import (  # noqa: E402
    load_vocabulary_deprecated_map,
    load_vocabulary_values,
)

FDR_PATH = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml"
TR_PATH = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"


def _load_known() -> set[str]:
    """词表 known 集合（values+aliases 经 SSoT 加载器，deprecated 键并入）。"""
    known = set(load_vocabulary_values("target_layer_vocabulary.yaml"))
    known.update(load_vocabulary_deprecated_map("target_layer_vocabulary.yaml").keys())
    return known


def _struct_load(path: Path) -> dict:
    """_struct_load implementation."""
    if not path.exists():
        print(f"ERROR: 注册表文件不存在: {path}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    try:
        import yaml  # noqa: PLC0415

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: 解析失败 {path}: {exc}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    if not isinstance(data, dict):
        print(f"ERROR: 顶层非 dict: {path}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    return data


def _fdr_domains() -> set[str]:
    """FDR 只认 entries[].domain 字段位——注释里的退役留案/通配示例不算在用。"""
    data = _struct_load(FDR_PATH)
    return {str(e["domain"]) for e in data.get("entries", []) or [] if isinstance(e, dict) and e.get("domain")}


def _tr_domains() -> set[str]:
    """翻译注册表只认 entries/algo_submodules 的 domain_id 字段位。"""
    data = _struct_load(TR_PATH)
    out: set[str] = set()
    for section in ("entries", "algo_submodules"):
        for e in data.get(section, []) or []:
            if isinstance(e, dict) and e.get("domain_id"):
                out.add(str(e["domain_id"]))
    return out


def _db_domains_advisory() -> list[str]:
    """--with-db 时读 depgraph domains 表（advisory，失败降级不置错）。"""
    try:
        from _shared.constants import get_depgraph_pg_connection  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001 — 可选观测面：DB 依赖不可用时降级为无 DB 视图
        print(f"[ADVISORY] DB 通道不可用，跳过 domains 表核对: {exc}", file=sys.stderr)
        return []
    try:
        conn = get_depgraph_pg_connection(read_only=True)
        raw = conn.execute("SELECT domain_id FROM domains").fetchall()  # noqa: bare-sql  只读枚举 domains 单表做差集对账，无集中化收益，属门禁豁免场景
        rows = [(r["domain_id"] if isinstance(r, dict) else r[0]) for r in raw]
    except Exception as exc:  # noqa: BLE001 — 同上：查询失败仅告警降级
        print(f"[ADVISORY] depgraph domains 查询失败，跳过: {exc}", file=sys.stderr)
        return []
    return rows


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="target_layer 三源域差集收敛校验")
    parser.add_argument("--with-db", action="store_true", help="附加 depgraph domains 表 advisory 核对")
    parser.add_argument("--quiet", action="store_true", help="仅输出差集结论行")
    args = parser.parse_args()

    known = _load_known()
    fdr = _fdr_domains()
    tr = _tr_domains()
    used = fdr | tr
    missing = sorted(used - known)

    if not args.quiet:
        print(
            f"[CONVERGENCE] known(词表+aliases+deprecated)={len(known)} FDR={len(fdr)} TR={len(tr)} "
            f"在用并集={len(used)}",
            file=sys.stderr,
        )
    if missing:
        print(f"✗ 在用未收编域 {len(missing)} 个（词表滞后，修复=收编 values/aliases 或标 deprecated）:", file=sys.stderr)
        for d in missing:
            where = []
            if d in fdr:
                where.append("FDR")
            if d in tr:
                where.append("TR")
            print(f"    {d}  [{'/'.join(where)}]", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)

    if args.with_db:
        db_rows = _db_domains_advisory()
        db_missing = sorted(set(r for r in db_rows if r.startswith("D_")) - known)
        if db_missing:
            print(
                f"[ADVISORY] depgraph DB 未收编域 {len(db_missing)} 个（不置非零，见头部 docstring 留案）: "
                + ", ".join(db_missing),
                file=sys.stderr,
            )

    print("✅ 三源域差集收敛（在用 ⊆ known）", file=sys.stderr)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
