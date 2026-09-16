# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-ERRCODE-001
# [MODULE] zephyr.gov_enforcement.commit_gates.errcode_consistency_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); tests/governance/test_error_code_consistency.py（判定逻辑 SSoT，importlib 按路径加载调用 collect_violations，不重实现）
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__（in_process_gate_registry.yaml 自动注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] staged 含 src/zephyr/**.py 或 error_code_registry.yaml 才执行；判定逻辑零重实现（调用测试 SSoT collect_violations 六断言证据集）；观测面=git index（本 commit 后的仓库态），基线=HEAD——**只阻断本次新增违规**，存量违规降级 warn+留痕并归属其责任人（裁定#279；治 2026-09-16 起 4 小时全局卡死：他会话未入 git 的文件让所有含 src/zephyr 的批次连坐）；SSoT 缺 collect_violations=fail-closed（禁退回逐断言遍历＝禁把存量算到本次头上）；index 面全绿即短路返回（不扫 HEAD 基线——常态提交零额外开销，基线扫描仅在有违规时付）；非 Zephyr 项目 fail-open；priority=131 唯一
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
   外部 hook「仅调用不重实现」口径），调用其 ``collect_violations()`` 取
   六断言违规证据集（可差分口径），按基线差分决定阻断（见下节）。
2. 阻断 detail 内嵌受影响前缀的下一可用号（扫描真源+注册表取 max+1），
   被拦 AI 直接获得可执行答案——编号分配靠工具不靠纪律。
3. files 触发（staged 含 src/zephyr/**.py 或注册表 yaml 才执行），
   控制 commit 时延；非 Zephyr 项目 fail-open。

观测面与基线差分（2026-09-16 事故治本；裁定#279）
--------------------------------------
第一性原理：全局对账型门禁的**判定对象**必须是「本 commit 之后的仓库态」，
不是「本机磁盘上碰巧有什么」。旧实现两条都错：
  ① 观测面＝文件系统 rglob——未入 git 的文件（他会话在途/从未 add）照样被判，
     而 staged 内容（部分暂存）反而看不见；
  ② 无基线——存量违规算到本次提交人头上。
实证：2026-09-16 16:34 起，ZA-PA-0031/32/33 指向从未进 git 的 pf_alloc 文件，
GATE-ERRCODE-CONSISTENCY 挡死**所有**含 src/zephyr 的批次（含提交队列），
全局卡死 4 小时，责任人以外的会话全部连坐（q-…-0008 死信）。

治本两条（SSoT 侧实现，本 gate 只消费）：
  ① 观测面改 git index（``git grep --cached`` 枚举 + ``git cat-file --batch``
     批量读，实测 0.23s/640 文件，比 rglob 更快）；``tree=`` 可切任意 tree-ish；
     git 不可达时退回文件系统面**并告警**（禁静默换口径）。
  ② 基线差分：``NOW = collect_violations()``（index）与
     ``BASE = collect_violations(tree="HEAD")`` 取差，**只阻断 NOW−BASE**；
     NOW∩BASE（存量）降级 warn+留痕，归属其责任人（宪法 §3.4 他会话在途违规
     不代修）。对齐业界：Google Tricorder「只报新增告警」（《Software
     Engineering at Google》ch.20）、bors-ng「先合到 staging 分支验，坏了只
     退回该 PR」——存量债不得成为无辜提交的阻断理由。

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

_SSDOT_TEST_REL = "tests/governance/test_error_code_consistency.py"  # noqa: gate-vocab SSoT 测试模块路径常量（按路径 importlib 加载判定逻辑，非测试目录归属判定；is_test_exempt 不适用本场景）
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

    staged 含 src/zephyr/**.py 或 error_code_registry.yaml 时，调用判定 SSoT 的
    ``collect_violations()`` 取六断言证据集（方向A 未登记/未声明前缀、方向B 存活
    锚定/注册表内部唯一、重码白名单外零容忍/白名单防腐），观测面=git index、
    基线=HEAD，**只阻断本次新增**（2026-09-16 事故治本）。
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

        collect = getattr(mod, "collect_violations", None)
        if not callable(collect):
            # fail-closed，且**禁**退回旧的逐断言遍历：旧口径无基线，会把存量违规算到
            # 本次提交人头上（4 小时全局卡死的成因），不得以"向后兼容"名义复活。
            return False, (
                "GATE-ERRCODE-CONSISTENCY: 判定 SSoT 未提供 collect_violations（基线差分口径缺失，fail-closed）\n"
                f"-> 升级 {_SSDOT_TEST_REL} 至基线差分口径（观测面=git index + tree= 基线）后重提"
            )

        try:
            now = collect()  # 本 commit 之后的仓库态（git index）
        except Exception as e:  # noqa: BLE001 — 对账执行失败=扫描环境事故，fail-closed
            return False, f"GATE-ERRCODE-CONSISTENCY: 对账执行失败（fail-closed）: {type(e).__name__}: {e}"

        # 短路：index 面全绿 → 无需基线（存量必为空集）。HEAD 基线扫描 ≈2.7s（纯净 dev
        # sandbox 实测），本门禁每个含 src/zephyr 的提交都跑，常态零额外开销是硬要求；
        # 只有出现违规时才付第二次扫描的代价去区分"本次新增"与"存量连坐"。
        if not any(now.values()):
            return True, ""

        try:
            base = collect(tree="HEAD")  # 提交前基线：存量违规归属其责任人，不连坐本次
        except Exception as e:  # noqa: BLE001 — 基线不可得（如注册表在 HEAD 尚不存在）
            logger.warning(
                "GATE-ERRCODE-CONSISTENCY: HEAD 基线不可得（%s: %s）——退严格口径，"
                "NOW 全部违规视为本次新增",
                type(e).__name__,
                e,
            )
            base = {}

        introduced = {k: sorted(now[k] - base.get(k, set())) for k in now if now[k] - base.get(k, set())}
        inherited = {k: sorted(now[k] & base.get(k, set())) for k in now if now[k] & base.get(k, set())}
        if inherited:
            logger.warning(
                "GATE-ERRCODE-CONSISTENCY: %d 项存量违规（HEAD 基线已在，非本次引入）不阻断，"
                "归属其责任人（宪法 §3.4 他会话在途违规不代修）: %s",
                sum(len(v) for v in inherited.values()),
                "; ".join(f"{k}={v[:3]}" for k, v in list(inherited.items())[:4]),
            )
        if not introduced:
            return True, ""

        evidence = [
            f"[{k}] {', '.join(v[:8])}{' …' if len(v) > 8 else ''}" for k, v in sorted(introduced.items())
        ]
        bad_codes = re.findall(r"ZA-[A-Z0-9]+(?:-[A-Z0-9]+)*", "\n".join(evidence))
        hints = _next_free_hints(mod, project_root, sorted(set(bad_codes)))
        detail = (
            "GATE-ERRCODE-CONSISTENCY 阻断: error_code 注册表↔代码真源对账失败（本次新增 "
            f"{sum(len(v) for v in introduced.values())} 项违规，#ARCH-ERRCODE-001；"
            "观测面=git index，基线=HEAD，存量违规不在此列）:\n" + "\n".join(evidence)
        )
        if hints:
            detail += f"\n{hints}（取号以扫描真源+注册表并集 max+1 为准）"
        return False, detail

    return GateSpec(gate_id="GATE-ERRCODE-CONSISTENCY", check=_check, priority=131)
