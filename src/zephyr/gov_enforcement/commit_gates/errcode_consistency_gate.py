# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-ERRCODE-001
# [MODULE] zephyr.gov_enforcement.commit_gates.errcode_consistency_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); tests/governance/test_error_code_consistency.py（判定逻辑 SSoT，importlib 按路径加载调用，不重实现）
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（in_process_gate_registry.yaml 自动注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] staged 含 src/zephyr/**.py 或 error_code_registry.yaml 才执行；判定逻辑零重实现（调用测试 SSoT 六断言）；非 Zephyr 项目 fail-open；priority=131 唯一
# [MODIFY-GUARD] gate_id="GATE-ERRCODE-CONSISTENCY"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 阻断 detail 含违规清单+受影响前缀下一可用号
# [TESTS] tests/governance/commit_gates/test_errcode_consistency_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""errcode_consistency_gate.py — error_code 注册表↔代码真源对账门禁 in-process 版（GATE-ERRCODE-CONSISTENCY）

裁定 2026-08-21-errorcode-stability-adjudication.md（#ARCH-ERRCODE-001 通道补齐）：

病根（第一性原理）
-----------------
1. GATE-ERRCODE（08-18 建）只挂 .pre-commit-config.yaml 外部链；
   GitCommitGateway 设计上永远 --no-verify，外部链在合法路径不触发。
2. 100% AI 开发全部合法提交走 gateway in-process 通道——errcode 门禁对
   AI 主通道等于不存在，43 未登记码+5 重号（08-20 夜班批目测取号事故）
   由此洞入仓。
3. 存在于旁路通道的门禁=不存在；门禁的价值=在写入点阻断。

治本方案
--------
1. 本 gate 把六断言判定搬进 gateway in-process：importlib 按路径加载
   tests/governance/test_error_code_consistency.py（判定逻辑 SSoT，同
   外部 hook「仅调用不重实现」口径），逐个调用三测试类六方法，
   AssertionError 即违规证据。
2. 阻断 detail 内嵌受影响前缀的下一可用号（扫描真源+注册表取 max+1），
   被拦 AI 直接获得可执行答案——编号分配靠工具不靠纪律。
3. files 触发（staged 含 src/zephyr/**.py 或注册表 yaml 才执行），
   控制 commit 时延；非 Zephyr 项目 fail-open。

priority=131（ISSUE-RESOLVED-INTEGRITY=130 之后、200 段之前，2026-08-21 实测空位）。
"""

from __future__ import annotations

import importlib.util
import logging
import re
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_errcode_consistency_gate"]

_SSDOT_TEST_REL = "tests/governance/test_error_code_consistency.py"
_REGISTRY_REL = "architecture_model/contracts/error_code_registry.yaml"
_CODE_NUM_RE = re.compile(r"^ZA-([A-Z0-9]+)-(\d+)$")


def _load_ssot_module(project_root: Path):
    """按路径加载判定逻辑 SSoT 测试模块（仅调用不重实现）。"""
    test_path = project_root / _SSDOT_TEST_REL
    spec = importlib.util.spec_from_file_location("errcode_consistency_ssot", test_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load SSoT spec: {test_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _next_free_hints(mod, project_root: Path, bad_codes: list[str]) -> str:
    """受影响前缀的下一可用号提示（扫描真源+注册表并集取 max+1）。"""
    prefixes = sorted({m.group(1) for c in bad_codes if (m := _CODE_NUM_RE.match(c))})
    if not prefixes:
        return ""
    try:
        rows = mod.scan_code_definitions()
        reg = mod.load_registry()
    except Exception:  # noqa: BLE001 — 提示计算失败不遮蔽主判定
        return ""
    used: dict[str, set[int]] = {}
    for e in reg["error_codes"]:
        if m := _CODE_NUM_RE.match(e["code"]):
            used.setdefault(m.group(1), set()).add(int(m.group(2)))
    for r in rows:
        if m := _CODE_NUM_RE.match(r["code"]):
            used.setdefault(m.group(1), set()).add(int(m.group(2)))
    hints = [f"{p}-{(max(used.get(p, {0})) + 1):04d}" for p in prefixes]
    return "下一可用号: " + ", ".join(hints)


def make_errcode_consistency_gate() -> GateSpec:
    """构造 GATE-ERRCODE-CONSISTENCY pre-commit 门禁（priority=131，硬阻断）。

    staged 含 src/zephyr/**.py 或 error_code_registry.yaml 时，调用判定 SSoT
    六断言（方向A 未登记/未声明前缀、方向B 存活锚定/注册表内部唯一、重码
    白名单外零容忍/白名单防腐）——AssertionError 即阻断证据。
    """

    def _check(gateway, files: list[str], **_kwargs) -> tuple[bool, str]:
        project_root = Path(gateway.project_root)
        # 非 Zephyr 项目 skip（对标 GATE-PRECOMMIT-OFFLINE）
        if not (project_root / "scripts" / "governance").is_dir():
            return True, "non-Zephyr project, skipping GATE-ERRCODE-CONSISTENCY"

        # files 触发：staged 含 src .py 或注册表才执行
        triggered = False
        for f in files:
            rel = str(f).replace("\\", "/")
            if ("/src/zephyr/" in rel or rel.startswith("src/zephyr/")) and rel.endswith(".py"):
                triggered = True
                break
            if rel.endswith(_REGISTRY_REL):
                triggered = True
                break
        if not triggered:
            return True, ""

        try:
            mod = _load_ssot_module(project_root)
        except Exception as e:  # SSoT 缺失=治理资产事故，fail-closed
            return False, f"GATE-ERRCODE-CONSISTENCY: 判定 SSoT 加载失败（{_SSDOT_TEST_REL}）: {e}"

        failures: list[str] = []
        for cls_name in ("TestCodeToRegistry", "TestRegistryToCode", "TestDuplicates"):
            cls = getattr(mod, cls_name)
            inst = cls()
            for meth_name in dir(inst):
                if not meth_name.startswith("test_"):
                    continue
                try:
                    getattr(inst, meth_name)()
                except AssertionError as ae:
                    failures.append(f"[{cls_name}.{meth_name}] {ae}")
                except Exception as e:  # noqa: BLE001 — 断言外异常=扫描环境事故，fail-closed
                    failures.append(f"[{cls_name}.{meth_name}] 非断言异常: {type(e).__name__}: {e}")

        if not failures:
            return True, ""

        bad_codes = re.findall(r"ZA-[A-Z0-9]+(?:-[A-Z0-9]+)*", "\n".join(failures))
        hints = _next_free_hints(mod, project_root, sorted(set(bad_codes)))
        detail = (
            "GATE-ERRCODE-CONSISTENCY 阻断: error_code 注册表↔代码真源对账失败 "
            f"（{len(failures)} 断言红，#ARCH-ERRCODE-001；治本=先登记/改号再提交）:\n"
            + "\n".join(failures[:6])
        )
        if hints:
            detail += f"\n{hints}（取号以扫描真源+注册表并集 max+1 为准）"
        return False, detail

    return GateSpec(gate_id="GATE-ERRCODE-CONSISTENCY", check=_check, priority=131)
