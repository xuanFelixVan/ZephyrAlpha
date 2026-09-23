# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.algo_flow_link_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.gov_enforcement.commit_gates._diff_helpers (_read_staged_file); zephyr.shared.utils.time_utils;
#   scripts.governance._shared.code_algorithm_extractor（解析+死块几何）; scripts.governance._shared.algo_flow_validate_marker（validate_graph 图判据真源）
# [CONSUMERS] in_process_gate_registry.yaml（auto_register_gates YAML 驱动注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——本 commit 触碰的 .py 中 ``# [ALGO_FLOW] external: <path>`` 锚指向的 yaml 必须存在且
#   algo_flow 块可解析（parse_algo_flow 有节点）+ 图可达（validate_graph：节点 id 合法唯一/至少一条边/
#   边端点已定义/断点一致——图坏=全景图静默空图，判据真源在 algo_flow_validate_marker 不重写第二份），
#   本 commit 触碰的 */algo_flow/*.yaml 必须自身可解析且
#   source_of_truth 指向实存源文件（Owner 批7 认可，2026-09-16）；不可读≠已删除——仅当该 yaml
#   出现在本次 staged 删除清单（``git diff --cached --diff-filter=D``）**且** HEAD 中无任何
#   live external 锚指向它（同批删除的 .py 上的锚不计，否则"源+镜像同批退役"永远提不进）
#   才判退役放行，其余不可读（权限/半写/漏声明删除）照旧硬阻断，
#   git 探测故障=按"仍有锚"处理（#ARCH-326 清偿通道：镜像该能被删，但删早了必须红），且本 commit 触碰的 src/zephyr .py
#   不得在 module docstring 之外另留 ALGO_FLOW 机器块，
#   docstring 之内只允许一个载体（锚或块二选一，两处并存=永不被消费的副本=双真源；P2-1 死块批
#   2026-09-16 增、体内多块线 2026-09-17 增、锚块并存同日经红蓝实弹哑火后并入同一判据；
#   几何判据共用 extractor.algo_flow_dead_block_spans 与
#   extractor.duplicate_inline_algo_flow_spans，判据真源**按盘上文件直载并按指纹重载**
#   （常驻进程 sys.modules 旧缓存=判据静默失效，2026-09-17 R1/R3 落地根因）；
#   判据源不在盘上=环境降级仅结构校验，在盘上却加载不出=fail-closed 阻断）；
#   own-diff 扫描——只查本次 commit files 清单，
#   他会话 staged 文件零接触（#ARCH-GATE-OWN-SCOPE-001 单一真源模式）；staged 内容优先（锚校验读 staged，
#   经 _diff_helpers._read_staged_file=``git show :<path>``，无 staged 回退工作区）；
#   fail-open（git/文件不可读/yaml 解析器不可用等基础设施故障放行，logger.warning）；
#   检出本 commit 违规 fail-closed
# [MODIFY-GUARD] gate_id="ALGO-FLOW-LINK"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——基础设施异常降级 fail-open（passed=True）；检出违规 fail-closed
# [TESTS] tests/governance/commit_gates/test_algo_flow_link_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 本模块由 commit 事件触发（非 cron/manual）
"""algo_flow_link_gate.py — ALGO_FLOW external 锚链接校验门禁（ALGO-FLOW-LINK）

    # [ALGO_FLOW]
    # 层: 输入
    # - id: I1
    #   name: 模块内部数据
    #   fields: 无公共形参/无再导出（AST 事实）
    #   code: algo_flow_link_gate.py
    # 层: 算法
    # - id: A1
    #   name_zh: ① make_algo_flow_link_gate
    #   name_en: make_algo_flow_link_gate
    #   intro: 构造 ALGO_FLOW 锚链接校验门禁。
    #   desc: external 锚 yaml 存在可解析、source_of_truth 实存、同批退役反向锚豁免。 Returns: GateSpec(gate_id="ALGO-FLOW-LINK", priority=108)。
    #   inputs: 无参数
    #   outputs: GateSpec
    # 层: 输出
    # - id: O1
    #   name_zh: GateSpec
    #   name_en: GateSpec
    #   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
    #   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
    #
    # 边:
    # I1 --> A1
    # A1 --> O1
    # [/ALGO_FLOW]

病根（第一性原理）
-----------------
P2-1 ALGO_FLOW 出仓战役后，源码 docstring 以单行 external 锚引用
docs/03_modules/<domain>/algo_flow/<stem>.yaml，算法图真源在 yaml 侧。
锚与 yaml 是跨文件双真源对——删 yaml/改锚路径/yaml 块语法坏/锚指向不存在文件，
全景图消费方（extractor）静默拿空图，无任何门禁拦截（批9 收尾批红蓝预演实证
"锚改道产生重复 yaml+锚错位"与"yaml 落盘而源锚缺失"两类真实漂移）。

治本方案（Owner 批7 认可，2026-09-16 落地）
--------
pre-commit 注册（priority=108，own-diff）：
  1. 本 commit files 中每个 .py：扫 external 锚 → 目标 yaml 存在 + algo_flow 块可解析 + 图可达
  2. 本 commit files 中每个 */algo_flow/*.yaml：可解析 + 图可达 + source_of_truth 实存
  3. 图可达判据 = algo_flow_validate_marker.validate_graph（id 合法唯一 / 至少一条边 /
     边端点已定义 / 断点边一致）——"可解析"曾经是太弱的门槛：2026-09-16 全仓普查实证
     "- id: I1 中文描述" 让 17 件节点 id 吞掉描述（mermaid 节点键含空格必炸 + 边端点全体悬空）、
     "# I1,I2 --> F1" 并列写法让 29 件边数静默归零、yaml 块标量的行首缩进让边行整体不匹配
     （三处都在 extractor 治本）——坏图在门禁全绿下存活，正是"假绿"类
  4. 本 commit files 中每个 src/zephyr .py：module docstring 之外不得另留 ALGO_FLOW 机器块
     （P2-1 死块普查实证：14 字段契约头里的副本所有读卡路径都看不见，锚+副本=双真源，
     184 件长期静默存活；几何判据与出仓器共用 extractor.algo_flow_dead_block_spans）
  5. 同件 docstring **之内**只允许一个 ALGO_FLOW 载体（锚或机器块二选一）：
     - 块+块：parse_algo_flow 只认首个起→止 对（§4.16），第 2 块连同其边段全体不可达，
       全景图显示半张图而作者以为显示整张；
     - 锚+块：锚已外链，写回的块永不被读卡路径消费=货真价实的第二真源——2026-09-17
       红蓝实弹 R2 经生产队列链路真落地（HEAD=b873ee71d3）暴露本形态原判据哑火，
       因原判据把锚行排除在候选外，"锚+一块"数出来只有 1，遂判合法。
     与死块同属"静默不可达"类、只是几何位置相反，故判据分家：
     extractor.duplicate_inline_algo_flow_spans（2026-09-17 普查 src/zephyr 3576 件
     体内多块=0、锚块并存=0，本判据是零存量防复发线）
  6. 违规聚合一次给全，硬阻断；基础设施故障 fail-open

设计权衡
--------
1. own-diff：files 参数即本次 commit 清单（gateway 构造性保证不含他会话文件），
   外来 staged 零接触——对称 IMPORT-INTEGRITY 的 own-scope 治本口径。
2. staged 内容优先：优先读 staged 版本（commit 语义真源），读不到回退工作区。
3. parse_algo_flow 复用 extractor 管线（_shared.code_algorithm_extractor），
   与全景图消费方同一解析器——门禁判"可解析"即消费方可解析，无第二真源。
4. fail-open 只用于基础设施故障；链接断/块坏=真违规，阻断。
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

_ANCHOR_RE = re.compile(r"^\s*#\s*\[ALGO_FLOW\]\s+external:\s*(\S+)\s*$", re.MULTILINE)
_ALGO_FLOW_DIR_SEG = "algo_flow"
_ALGO_FLOW_START = "# [ALGO_FLOW]"
_ALGO_FLOW_END = "# [/ALGO_FLOW]"


def _norm_posix(f: str | Path, repo_root: Path) -> str:
    p = Path(f)
    try:
        p = p.relative_to(repo_root)
    except ValueError:
        pass
    return p.as_posix()


_RULES_FILES = ("code_algorithm_extractor.py", "algo_flow_validate_marker.py")
# 判据符号位点 (文件, 符号)——缺任一即判据不完整，必须显形（静默缺判据=假绿）
_RULES_SYMBOLS = (
    ("code_algorithm_extractor.py", "parse_algo_flow"),
    ("algo_flow_validate_marker.py", "validate_graph"),
    ("code_algorithm_extractor.py", "algo_flow_dead_block_spans"),
    ("code_algorithm_extractor.py", "duplicate_inline_algo_flow_spans"),
)
# (判据目录, 两源文件指纹) → 判据四元组：盘上一变即重载，一版代码至多 exec 一次
_FRESH_RULES_CACHE: dict[tuple[str, tuple[tuple[int, int], ...]], tuple[Callable, ...]] = {}


def _rules_dir(root: Path) -> Path | None:
    """判据真源目录（`_shared`）：先本 commit 所属根（落地 worktree 与主仓同构），再本模块所在仓。"""
    for c in (
        root / "scripts" / "governance",
        Path(__file__).resolve().parents[4] / "scripts" / "governance",
    ):
        if (c / "_shared" / _RULES_FILES[0]).is_file():
            return c / "_shared"
    return None


def _rules_source_present(root: Path) -> bool:
    """判据源文件是否都在盘上——True 时仍取不到判据=仓库自身缺陷（调用侧据此 fail-closed）。"""
    d = _rules_dir(root)
    return d is not None and all((d / f).is_file() for f in _RULES_FILES)


def _fresh_rules(shared: Path) -> tuple[Callable, ...] | None:
    """绕过 sys.modules 按文件直载判据（独立模块名，不污染他人在用的 `code_algorithm_extractor`）。"""
    import importlib.util  # noqa: PLC0415
    import sys  # noqa: PLC0415

    mods: dict[str, object] = {}
    for f in _RULES_FILES:
        path = shared / f
        spec = importlib.util.spec_from_file_location(f"_algo_flow_link_rules.{f[:-3]}", path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        key = f"_algo_flow_link_rules.{f[:-3]}"
        sys.modules[key] = mod  # exec 期间的自引用（如有）解析到本次副本而非缓存副本
        try:
            spec.loader.exec_module(mod)
        except Exception:  # noqa: BLE001 — 加载失败上抛给调用侧按缺陷处置，不在此静默
            sys.modules.pop(key, None)
            logger.exception("ALGO-FLOW-LINK 判据直载失败: %s", path)
            return None
        mods[f] = mod
    out = []
    for f, sym in _RULES_SYMBOLS:
        fn = getattr(mods[f], sym, None)
        if not callable(fn):
            logger.error("ALGO-FLOW-LINK 判据缺符号: %s.%s", f, sym)
            return None
        out.append(fn)
    return tuple(out)


def _load_graph_rules(root: Path) -> tuple[Callable, Callable, Callable, Callable] | None:
    """取判据真源 (parse_algo_flow, validate_graph, algo_flow_dead_block_spans,
    duplicate_inline_algo_flow_spans)，**以盘上版本为准**。

    判据一律不在门禁内重写第二份：解析/图规则真源在 scripts/governance/_shared，
    几何规则真源在 extractor。

    为什么不再 `from _shared... import`（2026-09-17 R1/R3 双落地根因治本）：走
    sys.modules 的导入形态下，常驻进程（belt 守护 / serializer）只要在判据新增符号
    **之前** import 过 extractor，之后每次取判据都撞 ImportError → 返回 None →
    死块/体内多块/图可达三条判据整体静默关闭，而不依赖判据的锚存在性与
    source_of_truth 两条照常开火——"门还在、牙没了"，红蓝实弹实测同一条门禁
    R4/R5 阻断、R1/R3 落地（PID 28552/28648 自 07:17 常驻，
    `algo_flow_dead_block_spans` 21:58 才进 extractor）。现按 (目录, 源文件指纹)
    缓存直载结果：判据语义恒等于提交时刻的仓库内容，不再受进程寿命摆布。

    返回 None 只保留一种含义：**判据源文件不在盘上**（环境降级，结构性兜底仍在）；
    在盘上却加载不出=仓库自身缺陷，由调用侧 `_rules_source_present` 判并 fail-closed。
    """
    shared = _rules_dir(root)
    if shared is None:
        return None
    try:
        fp = (str(shared), tuple(
            (lambda st: (st.st_mtime_ns, st.st_size))((shared / f).stat()) for f in _RULES_FILES
        ))
    except OSError:
        return None
    hit = _FRESH_RULES_CACHE.get(fp)
    if hit is not None:
        return hit  # type: ignore[return-value]
    rules = _fresh_rules(shared)
    if rules is not None:
        _FRESH_RULES_CACHE[fp] = rules
    return rules  # type: ignore[return-value]


def check_algo_flow_links(
    files: list[str] | None,
    project_root: str | Path,
    read_staged: Callable[[str], str | None] | None = None,
    deleted: Callable[[str], bool] | None = None,
    reverse_anchor: Callable[[str], list[str]] | None = None,
) -> tuple[bool, str]:
    """纯逻辑核心（可单测，不触 git）。

    Args:
        files: 本次 commit 文件清单（相对/绝对路径混合容忍）。
        project_root: 仓库根。
        read_staged: staged 内容读取器（测试注入/网关注入）；None=直接读工作区。
        deleted: 该路径是否为本次 commit 的删除项（网关注入 staged 删除清单判定）；
            None=按"不可读即违规"旧行为（fail-closed 默认，退役方向必须显式声明）。
        reverse_anchor: 删除项的反向锚探测（哪些 live .py 仍 ``external:`` 指它）；
            仅在 deleted=True 时调用。

    Returns:
        (blocked, message)
    """
    if not files:
        return False, ""
    root = Path(project_root)
    py_files: list[str] = []
    yaml_files: list[str] = []
    for f in files:
        rel = _norm_posix(f, root)
        if rel.endswith(".py"):
            py_files.append(rel)
        elif rel.endswith(".yaml") and f"/{_ALGO_FLOW_DIR_SEG}/" in f"/{rel}":
            yaml_files.append(rel)

    def _read(rel: str) -> str | None:
        if read_staged is not None:
            content = read_staged(rel)
            if content is not None:
                return content
        try:
            return (root / rel).read_text(encoding="utf-8")
        except OSError:
            return None

    # 延迟导入 yaml（失败=基础设施故障 fail-open）；extractor 可用则全解析，否则结构校验
    try:
        import yaml as pyyaml
    except Exception:  # noqa: BLE001 — 基础设施故障 fail-open
        logger.warning("ALGO-FLOW-LINK fail-open: yaml 解析器加载失败", exc_info=True)
        return False, ""

    # 判据一次加载复用（按盘上指纹缓存，盘上一变即重载——见 _load_graph_rules 病根段）
    rules = _load_graph_rules(root)
    if rules is None:
        if _rules_source_present(root):
            # 判据源在盘上却拿不到=仓库自身缺陷，此时放行等于把"死块/体内多块/图可达"
            # 三条线整体关掉而门禁全绿（2026-09-17 R1/R3 经生产队列真落地的形态）。
            return True, (
                "ALGO-FLOW-LINK：判据真源 scripts/governance/_shared/{code_algorithm_extractor,"
                "algo_flow_validate_marker}.py 在盘上但加载失败——本门无法判定，按 fail-closed 阻断"
                "（判据不可得时放行=静默假绿，与它要防的双真源/坏图同害）。查 logger 记录的"
                " ImportError/缺符号明细，修复判据源后重新提交。"
            )
        logger.warning("ALGO-FLOW-LINK 判据降级：scripts/governance/_shared 不在盘上，仅结构校验")

    def _validate_block(content: str) -> tuple[bool, str]:
        """yaml 文本 → (ok, why)：可解析 + algo_flow 块结构完整（+extractor 全解析当可用）。"""
        try:
            doc = pyyaml.safe_load(content) or {}
        except Exception as e:  # noqa: BLE001
            return False, f"yaml 解析失败: {type(e).__name__}"
        block = (doc or {}).get("algo_flow")
        if not isinstance(block, str) or not block.strip():
            return False, "缺 algo_flow 块"
        if _ALGO_FLOW_START not in block or _ALGO_FLOW_END not in block:
            return False, "algo_flow 块缺起/收标记"
        if "# - id:" not in block:
            return False, "algo_flow 块无节点行"
        if rules is None:
            return True, ""  # extractor 不在 sys.path——结构校验兜底（判据不重写第二份）
        parse_algo_flow, validate_graph = rules[0], rules[1]
        try:
            data = parse_algo_flow(block)
        except Exception as e:  # noqa: BLE001
            return False, f"parse_algo_flow 异常: {type(e).__name__}"
        if data is None:
            return False, "parse_algo_flow 无节点"
        problems = validate_graph(data)
        if problems:
            return False, "推导图不可达：" + "；".join(problems[:4])
        return True, ""

    failures: list[str] = []

    def _dead_block_lines(content: str) -> list[int]:
        """docstring 外的 ALGO_FLOW 块起行（1 基）；判据不可用=基础设施故障放行。"""
        if rules is None:
            return []
        try:
            return [s + 1 for s, _e, _c in rules[2](content)]
        except Exception as e:  # noqa: BLE001
            logger.warning("ALGO-FLOW-LINK 双真源检出异常: %s", e)
            return []

    def _dup_inline_lines(content: str) -> list[int]:
        """docstring 内第 2+ 个 ALGO_FLOW 块起行（1 基）——与死块同族但几何位置相反。"""
        if rules is None:
            return []
        try:
            return [s + 1 for s, _e, _c in rules[3](content)]
        except Exception as e:  # noqa: BLE001
            logger.warning("ALGO-FLOW-LINK 体内多块检出异常: %s", e)
            return []

    for rel in py_files:
        content = _read(rel)
        if content is None:
            continue  # 文件读取失败（删除/权限）——非本门职责
        for m in _ANCHOR_RE.finditer(content):
            target = m.group(1)
            tgt = root / target
            if not tgt.is_file():
                failures.append(f"{rel} external 锚指向不存在的 yaml: {target}")
                continue
            ok, why = _validate_block(tgt.read_text(encoding="utf-8"))
            if not ok:
                failures.append(f"{rel} external 锚 yaml 不可解析: {target}（{why}）")
        if rel.startswith("src/zephyr/"):
            dead = _dead_block_lines(content)
            if dead:
                failures.append(
                    f"{rel} 有 {len(dead)} 处 ALGO_FLOW 机器块落在 module docstring 之外"
                    f"（起行 {dead[:3]}）——锚与体外副本并存=双真源，所有读卡路径只读 "
                    "docstring，副本永不被消费也永不更新；清偿："
                    f"python scripts/governance/d5_architecture/generators/externalize_algo_flow.py --file {rel}"
                )
            dup = _dup_inline_lines(content)
            if dup:
                failures.append(
                    f"{rel} 的 module docstring 内有 {len(dup)} 处多余 ALGO_FLOW 机器块"
                    f"（起行 {dup[:3]}）——一个 docstring 只能有一个 ALGO_FLOW 载体：parse_algo_flow "
                    "只认首个 起→止 对，其后每块连同自己的边段全体不可达；锚已在场外指真源，"
                    "体内再写块=永不被消费的副本。全景图显示半张图而作者以为显示整张，"
                    "与体外死块同属静默不可达类（只是几何位置相反，故判据分家）。清偿："
                    "把多块合并成单一块，或跑 externalize_algo_flow.py 外迁后留一行锚"
                )

    def _yaml_unreadable(rel: str) -> str | None:
        """yaml 读不到时的分岔判据：不可读≠已删除。

        旧写法一律判红 ⇒ 镜像退役（源已消失、镜像该删）永远提不进仓，与 #ARCH-326
        要求的清偿路径正相抵。退役方向改判"还有没有 live 锚指过来"：有锚=删早了必须红，
        无锚=放行。未声明为删除的不可读（权限/编码/半写）照旧硬阻断，判据不放松；
        声明了删除却没给探测器=无从确认无锚，同样阻断（核心 API 不许"没查=没锚"）。
        """
        if deleted is None or not deleted(rel):
            return f"{rel} algo_flow yaml 不可读（已删除?）"
        if reverse_anchor is None:
            return (
                f"{rel} 已声明为本次删除，但调用方未提供反向锚探测器——"
                "无从确认是否仍有 external 锚指向它，按 fail-closed 阻断"
            )
        hits = reverse_anchor(rel)
        if hits:
            return (
                f"{rel} 已删除但仍有 {len(hits)} 处 external 锚指向它"
                f"（{', '.join(hits[:3])}）——先清锚（改锚或删块）再退役镜像"
            )
        return None

    for rel in yaml_files:
        content = _read(rel)
        if content is None:
            why = _yaml_unreadable(rel)
            if why:
                failures.append(why)
            continue
        ok, why = _validate_block(content)
        if not ok:
            failures.append(f"{rel} algo_flow 块不可解析（{why}）")
            continue
        try:
            doc = pyyaml.safe_load(content) or {}
            sot = (doc or {}).get("source_of_truth")
        except Exception:  # noqa: BLE001 — 已由 _validate_block 兜底
            sot = None
        if not sot:
            failures.append(f"{rel} 缺 source_of_truth 头")
        elif not (root / str(sot)).is_file():
            failures.append(f"{rel} source_of_truth 指向不存在的源文件: {sot}")

    if failures:
        return True, (
            f"ALGO-FLOW-LINK：{len(failures)} 处 ALGO_FLOW 锚/卡片链接断裂——"
            "external 锚指向的 yaml 必须存在且可解析，yaml 的 source_of_truth 必须实存"
            "（Owner 批7 认可，2026-09-16）。"
            + "；".join(failures[:20])
        )
    return False, ""


def make_algo_flow_link_gate() -> object:
    """构造 ALGO_FLOW 锚链接校验 GateSpec（硬阻断型，priority=108，own-diff）。"""
    from zephyr.gov_enforcement.commit_gates._diff_helpers import _read_staged_file
    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

    def _check(gateway: object, files: list[str] | None, **kwargs: object) -> tuple[bool, str]:
        try:
            project_root = Path(str(gateway.project_root))

            def _read_staged(rel: str) -> str | None:
                """staged blob 真源（#ARCH-321 治本）。

                原写法调 ``gateway.read_staged_file``——网关无此方法，异常被宽 except
                吞掉后静默回退读磁盘：门禁判的于是是工作区内容，而 commit 落的是 index
                内容。staged≠磁盘（他会话 staged 未改、或本会话改完未 add）时双向误判，
                与 #ARCH-316 治的"观测面错位"同病。判据不重写第二份，复用同包
                ``_diff_helpers._read_staged_file``（``git show :<path>`` + run_git 双解码）。
                """
                return _read_staged_file(gateway, rel)

            def _staged_deleted() -> frozenset[str]:
                """本次 staged 的删除清单（同 derived_file_deletion_gate 观测姿势）。

                单次 commit 一趟取好即可（每门一次 git 调用）：拿不到=空集，
                于是所有不可读 yaml 回到旧的硬阻断，不会因观测故障放行。
                """
                try:
                    r = gateway.run_git(
                        ["git", "diff", "--cached", "--name-only", "--diff-filter=D"]
                    )
                except Exception:  # noqa: BLE001 — git 不可达=判不了，退回旧硬阻断
                    return frozenset()
                if r.returncode != 0:
                    return frozenset()
                return frozenset(
                    str(x).strip().replace("\\", "/")
                    for x in (r.stdout or "").splitlines()
                    if str(x).strip()
                )

            deleted_set = _staged_deleted()

            def _is_deleted(rel: str) -> bool:
                return rel in deleted_set

            def _reverse_anchor(rel: str) -> list[str]:
                """HEAD 里仍把该镜像当 external 真源的 .py（删镜像前的最后一道闸）。

                命中项里扣掉本次同批删除的 .py：整模块退役=源与镜像同 commit 消失，
                HEAD 侧的锚必然还在（HEAD 是改前快照），不扣就是"该删的删不掉"；被扣文件
                连自己带锚一起消失，不存在"扣掉后留下坏锚"。既不删也不改的残留锚仍留在
                命中集里——那种"只删镜像不救锚"=全景图当场断链，照旧红。
                """
                try:
                    r = gateway.run_git(["git", "grep", "-l", "-F", rel, "HEAD", "--", "*.py"])
                except Exception as exc:  # noqa: BLE001 — 探测失败按"仍有锚"处理（fail-closed）
                    return [f"<git grep 不可达: {type(exc).__name__}>"]
                if r.returncode not in (0, 1):  # 1=无命中，其它=git 故障
                    return [f"<git grep exit={r.returncode}>"]

                def _strip_rev(line: str) -> str:
                    # git grep 对 tree-ish 检索输出 `<rev>:<path>` 形态（HEAD:src/...）——
                    # 不剥前缀则与 deleted_set（纯相对路径）永不相等，同批退役豁免失效
                    #（st-gslim-20260923 实证：三台退役连坐误杀，模块+镜像同批必被拦）。
                    return line.split(":", 1)[-1] if line != rel else line

                return [
                    _strip_rev(p)
                    for p in (str(x).strip() for x in (r.stdout or "").splitlines())
                    if p and _strip_rev(p) not in deleted_set
                ]

            blocked, msg = check_algo_flow_links(
                files, project_root, read_staged=_read_staged,
                deleted=_is_deleted, reverse_anchor=_reverse_anchor,
            )
            return (not blocked), msg
        except Exception as exc:  # noqa: BLE001 — 基础设施故障 fail-open
            logger.warning("ALGO-FLOW-LINK fail-open: %s", exc)
            return True, ""

    return GateSpec(gate_id="ALGO-FLOW-LINK", check=_check, priority=108)
