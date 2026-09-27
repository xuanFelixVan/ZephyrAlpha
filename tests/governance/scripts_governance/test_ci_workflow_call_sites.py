# [A_test] module_id: MOD-GOV_ci_workflow_call_sites | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_DQ | scripts/governance/run_all.py | §CI 调用面
# [MODULE] tests.governance.scripts_governance.test_ci_workflow_call_sites
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""test_ci_workflow_call_sites.py — CI 调用面与脚本真源一致性回归（自动化假绿战役 2026-09-27）。

病根（本件存在理由）：`.github/workflows/governance.yml` 曾以 `run_all.py --ci` 调用
全量治理回归，而 run_all.py argparse 从未声明 `--ci` → CI 侧 exit 2，"最后防线"从未
跑起来；同文件另一处给 argv-blind 脚本传装饰性旗标被静默吞。属"自动化上报成功而实未
工作"族。本尺把"调用面旗标必须被目标脚本声明"变成机判，回归即红。

另守 mutation_test_reconciliation_registry 的 SSoT 路径漂移（同役缺陷 1b）：
其 _SSOT_PATH 指向不存在文件时变异测试直接 FATAL exit 2——路径必须可存在。
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
GOVERNANCE_YML = REPO_ROOT / ".github" / "workflows" / "governance.yml"

_PY_INVOCATION_RE = re.compile(r"python\s+(?:-m\s+[\w.]+|([\w/_.\-]+\.py))([^\n]*)")
_FLAG_RE = re.compile(r"--[\w][\w\-]*")


def _iter_call_sites():
    """yield (行号, 脚本相对路径, 长旗标清单)——governance.yml 全部 python .py 调用行。"""
    text = GOVERNANCE_YML.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), 1):
        m = _PY_INVOCATION_RE.search(line)
        if not m or not m.group(1):
            continue
        script = m.group(1).replace("\\", "/")
        flags = _FLAG_RE.findall(m.group(2))
        if not flags:
            continue
        yield lineno, script, flags


def test_governance_yml_exists_and_nonempty() -> None:
    assert GOVERNANCE_YML.is_file(), f"CI 入口缺失: {GOVERNANCE_YML}"
    assert GOVERNANCE_YML.stat().st_size > 0


def test_every_flag_passed_to_governance_script_is_declared() -> None:
    """调用面每个 --flag 必须出现在目标脚本源码中（argparse 声明的字面量面）。

    红样：向 governance.yml 任一调用行重新加脚本未声明的旗标（如历史病根
    run_all.py --ci），本尺必红。
    """
    violations: list[str] = []
    checked = 0
    for lineno, script, flags in _iter_call_sites():
        path = REPO_ROOT / script
        if not path.is_file():
            violations.append(f"yml:{lineno} 调用的脚本不存在: {script}")
            continue
        src = path.read_text(encoding="utf-8", errors="replace")
        for flag in flags:
            checked += 1
            if flag not in src:
                violations.append(f"yml:{lineno} {script} 收到未声明旗标 {flag}")
    assert not violations, "CI 调用面漂移（未声明旗标=被 argparse exit2 拒绝或被静默吞）:\n" + "\n".join(violations)
    assert checked >= 10, f"扫描面异常收窄（checked={checked}）——正则失配即尺失效，不允许静默归零"


def test_run_all_yml_invocation_parses_and_starts() -> None:
    """精确守门：按 governance.yml 里 run_all.py 那一行的参数实跑 --dry-run，rc 必为 0。

    病根行 `run_all.py --ci` 下本尺以 rc=2 红；删掉旗标后同参数+--dry-run 绿。
    不 import 该模块（避免重依赖副作用），用与 CI 同构的进程面判。
    """
    text = GOVERNANCE_YML.read_text(encoding="utf-8")
    m = re.search(r"python\s+scripts/governance/run_all\.py([^\n]*)", text)
    assert m, "governance.yml 不再调用 run_all.py——CI 全量治理回归位消失，请同步本尺"
    argv = m.group(1).split()
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "governance" / "run_all.py"), *argv, "--dry-run"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    assert r.returncode == 0, (
        f"run_all.py {' '.join(argv)} 起不来 rc={r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}"
    )


def test_mutation_test_ssot_path_resolves() -> None:
    """变异测试件的 _SSOT_PATH 必须指向真实存在的 SSoT（漂移=FATAL exit 2 假死）。"""
    path = REPO_ROOT / "scripts" / "governance" / "meta" / "mutation_test_reconciliation_registry.py"
    spec = importlib.util.spec_from_file_location("_mut_rr_under_test", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    # 先注册再 exec：件内 @dataclass 在 exec 期解析 __module__，缺登记即 NoneType 崩
    sys.modules["_mut_rr_under_test"] = mod
    try:
        spec.loader.exec_module(mod)
        ssot = Path(mod._SSOT_PATH)  # noqa: SLF001 — 白盒：本尺专守该常量
    finally:
        sys.modules.pop("_mut_rr_under_test", None)
    assert ssot.is_file(), f"SSoT 真源不存在（变异测试将 FATAL）: {ssot}"
    assert ssot.name == "reconciliation_registry.py"
