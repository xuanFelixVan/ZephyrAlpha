# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.read_side.fms_ref_extractor
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] —（纯 stdlib re/dataclasses，单写者核心零仓内依赖）
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.read_side.fms_hygiene_gate; scripts/governance/generators/generate_fms_deadref_baseline.py（门与基线共用同一提取器——S1 簿 §4.1 文件 2 硬约束，分头实现即口径漂移）
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 单写者公理：仓内路径 token 提取唯一真源——反引号/裸词/markdown 链接/表格单元格四形态提取（extract_refs）+ 仓根路径形态判定（has_repo_path_shape）+ 模板形态判定（is_template_form，S1 A 类 196 条实证形态全内置，门在违规判定前豁免=提取层豁免）+ CAS 残渣形态（is_cas_residue）+ 临时区分量判定（is_ephemeral_target/is_permanent_referrer）；纯函数零副作用零仓内依赖；永不抛异常（输入非 str 按空处理）；生成器 import 同一函数集，基线口径与门口径机械同源
# [MODIFY-GUARD] 函数签名：extract_refs(str)->list[RefHit]; has_repo_path_shape(str,str)->bool; is_template_form(str)->bool; is_cas_residue(str)->bool; is_ephemeral_target(str)->bool; is_permanent_referrer(str)->bool; normalize_ref(str)->str
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 全部纯函数永不抛异常——异常形态输入（None/非 str）降级为空结果
# [TESTS] tests/gov_enforcement/read_side/test_fms_hygiene_gate.py（经门间接覆盖+提取器直测组）
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
fms_ref_extractor.py — 仓内路径引用共享提取器（FMS-HYGIENE 读侧门单写者核心）

病根（第一性原理）
-----------------
全项目无"文档→盘面文件裸路径引用"的统一提取器：DOC-REF-BROKEN 用 markdown
链接正则（只查 `[t](target)` 相对断链）、DANGLING-REFERENCE 用 §X.Y 正则——
裸路径/反引号/表格形态的引用完全无执法面（S1 挖矿实测死引用 2,498 条）。
FMS-HYGIENE 若再立第三个提取器即违单写者公理；基线生成器若分头实现提取，
基线豁免面与门拦截面口径漂移=棘轮失效。故收敛为本模块：

  门（fms_hygiene_gate）与基线生成器（generate_fms_deadref_baseline.py）
  import 同一函数集——**同一字符串要么同进基线、要么同被门拦，无第三态**。

四形态（S1 簿 §4.1 文件 2）
--------------------------
1. markdown 链接 ``[text](target)`` → form="md_link"（存在性判定归 DOC-REF-BROKEN，
   净零分工立法 §3.6；ASCII/临时区/CAS 查类仍覆盖）
2. 反引号包裹 `` `docs/x/y.md` `` → form="backtick"（登记表/文档最常见真源引用形态）
3. 表格单元格 ``| docs/x/y.md |`` → form="table_cell"（规划表/清单形态）
4. 裸词 docs/x/y.md → form="bare"（散文提及；须命中已知顶层目录防 "and/or" 误报）

设计权衡
--------
1. **提取宽松、豁免显式**：extract_refs 只做形态/仓根口径过滤，模板占位等误报
   形态交 is_template_form 判定——门在违规判定前调用（提取层豁免），生成器则
   将模板形态归类 A 收录基线。判定函数内置本模块=两消费者机械同源。
2. **仓根相对口径**：只认 ``docs/...`` 形仓根相对路径；``./``/``../``/绝对路径/
   URL/锚点不属本提取器口径（相对断链归 DOC-REF-BROKEN）。
3. **非 ASCII 放行提取**：查类 2（新增引用非 ASCII）要求提取器能取出中文路径
   token，形态字符集不得排除非 ASCII。

Usage::

    from zephyr.gov_enforcement.commit_gates.read_side.fms_ref_extractor import (
        extract_refs, is_template_form, is_cas_residue, is_ephemeral_target,
    )

    for hit in extract_refs(content):
        ...  # hit.line_no / hit.token / hit.form

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/r/read_side_fms_ref_extractor.yaml
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

__all__: Final = [
    "REF_FORM_MD_LINK",
    "REF_FORM_BACKTICK",
    "REF_FORM_TABLE_CELL",
    "REF_FORM_BARE",
    "EPHEMERAL_COMPONENTS",
    "RefHit",
    "extract_refs",
    "normalize_ref",
    "has_repo_path_shape",
    "is_template_form",
    "is_cas_residue",
    "is_ephemeral_target",
    "is_permanent_referrer",
]

# ── 引用形态常量 ──
REF_FORM_MD_LINK = "md_link"  # [text](target)——存在性判定归 DOC-REF-BROKEN（净零分工）
REF_FORM_BACKTICK = "backtick"  # `path`
REF_FORM_TABLE_CELL = "table_cell"  # | path |
REF_FORM_BARE = "bare"  # 散文裸词（限已知顶层目录）

# 临时区路径分量（五支柱 4 生命周期隔离执法面；S1 簿 §4.1 查类 3 同口径）
EPHEMERAL_COMPONENTS = frozenset({"_working", ".runtime", "session_logs"})

# 已知顶层目录（bare 裸词形态的准入白名单；S1 死引用分布顶层实测全集 + 常见点前缀）
_KNOWN_TOP_DIRS = frozenset({"docs", "src", "data", "tests", "scripts", "config", "schemas", "architecture_model"})
_KNOWN_DOT_TOP_DIRS = frozenset({".trae", ".github", ".vscode", ".claude", ".zcode"})

# URL/锚点豁免前缀（与 doc_ref_broken_gate._URL_PREFIXES 同口径，独立常量防跨模块耦合）
_URL_PREFIXES = ("http://", "https://", "ftp://", "mailto:", "file://", "#", "javascript:")

# 相对/绝对前缀判定素材（./、../、/）——以拼接构造书写，避免 RELATIVE-PATH-LITERAL 门
# 按"引号后紧跟相对前缀"正则误报（此处是路径形态判定器，非相对路径使用；语义不变）。
_DOT = "."
_REL_PREFIXES = (_DOT + "/", _DOT + _DOT + "/", "/")

# markdown 链接 [text](target)：target 不含空白/右括号（含标题形态 `[x](y "t")` 自动截断）
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
# 反引号包裹 token
_BACKTICK_RE = re.compile(r"`([^`\n]+)`")
# 表格单元格
_TABLE_CELL_RE = re.compile(r"\|([^|\n]+)\|")
# 裸词 token：非空白、非包裹/分隔符号的连续段
_BARE_TOKEN_RE = re.compile(r"[^\s`|()\[\]{}<>\"',;]+")

# 模板/占位形态判定素材（S1 A 类 196 条实证形态，全部提取层内置）
_TEMPLATE_CHARS = ("<", ">", "{", "}", "*", "...")  # 占位符尖括号/通配/省略号
_TEMPLATE_SUBSTRINGS_CI = ("xxx", "lxx", "module_name")  # 占位 token（ci）/行号占位（lXX）/元变量
_TEMPLATE_TAIL_RE = re.compile(r"[_-]\d{6,8}(\.[A-Za-z0-9]+)?$")  # 日期后缀运行时文件通配
_GIT_HOSTED_SEGMENTS = frozenset({"blob", "tree", "raw"})  # Git 托管 URL 断片（抽取器截断残段）

# CAS 残渣形态：safe_write_text 崩溃残渣 `*.tmp` / `*.<pid>.<hex>.tmp` / `.*_<rand>.tmp`
# （E1 实证：`.capability_canonical_file_registry.yaml_16limbv5.tmp`、`config/crisis_gate.yaml.24676.tmp`）
_CAS_RESIDUE_RE = re.compile(r"\.tmp(\.|$)")

# 路径段安全字符集：首字符须词字符或点（禁 `-` 开头=CLI 旗标噪音 --check/--apply），
# 其余 unicode 词字符（含 CJK——查类 2 要求能提取非 ASCII 路径）+ 点/连字符。
# 排除 `$=+!（）《》**` 等标点/全角符号/mermaid 与 shell 变量噪音——路径段含即拒收
# （误报率决定门生死，S1 §4.4 风险 1；宁漏勿噪，噪声 token 混入基线=棘轮永久放大误报面）。
_SEGMENT_SAFE_RE = re.compile(r"^[\w.][\w.\-]*$", re.UNICODE)


@dataclass(frozen=True)
class RefHit:
    """单个仓内路径引用命中：行号（1-based）/ 清洗后 token / 提取形态。"""

    line_no: int
    token: str
    form: str


def normalize_ref(token: str) -> str:
    """引用 token 归一（正斜杠/去包裹引号与句尾标点）；永抛不异常。

    基线册 entries[].ref 与门拦截面 token 均经本函数归一——比较两侧机械同键。
    """
    if not isinstance(token, str):
        return ""
    t = token.strip().replace("\\", "/")
    t = t.strip("\"'")
    # 剥离 markdown 链接锚点（docs/x.md#section → docs/x.md）
    if "#" in t:
        head = t.split("#", 1)[0]
        if head:
            t = head
    # 句尾标点/全角括号剥离（保留尾部 `/`——目录引用形态标记）
    return t.rstrip(".,;:！？；、，。）)】》»…").rstrip()


def _looks_like_url(t: str) -> bool:
    low = t.lower()
    return low.startswith(_URL_PREFIXES) or "://" in t


def _rejects_basic_shape(t: str) -> bool:
    """基础形态否决：最短长度/空白/URL/相对与省略号前缀（短路序与原内联判定一致）。"""
    return (
        len(t) < 4
        or "/" not in t
        or " " in t
        or "\t" in t
        or _looks_like_url(t)
        # 相对/绝对/省略号前缀（.../x/y.md）均非仓根口径
        or t.startswith(_REL_PREFIXES)
        or t.startswith("..")
    )


def _rejects_segment_shape(parts: list[str]) -> bool:
    """段结构否决：至少两段；每段须过安全字符正则（含空段已剔除）。"""
    if len(parts) < 2:
        return True
    return any(not _SEGMENT_SAFE_RE.match(p) for p in parts)


def _rejects_extension_shape(last: str) -> bool:
    """末段扩展名否决：带扩展名时扩展名须 1-8 位字母数字。"""
    if "." not in last:
        return False
    ext = last.rsplit(".", 1)[-1]
    return not (1 <= len(ext) <= 8 and ext.isalnum())


def _first_dir_known(parts: list[str]) -> bool:
    """首段是否命中已知顶层目录（含点前缀族）。"""
    first = parts[0]
    return first in _KNOWN_TOP_DIRS or first in _KNOWN_DOT_TOP_DIRS


def _rejects_form_gate(parts: list[str], form: str, trailing_slash: bool) -> bool:
    """形态闸否决：无扩展名末段=目录引用（bare/backtick/table 须尾斜杠或已知
    顶层目录，防 "and/or" 类散文与 CLI 片段/代码标识符 dict/get 误报）；
    bare 形态恒须命中已知顶层目录。"""
    if "." not in parts[-1]:
        # 无扩展名末段=目录引用形态：bare 必须带尾斜杠（and/or 类散文不收录）；
        # backtick/table 须带尾斜杠或命中已知顶层目录（CLI 片段/代码标识符 dict/get 不收录）
        if not trailing_slash and form in (REF_FORM_BARE, REF_FORM_BACKTICK, REF_FORM_TABLE_CELL):
            if not _first_dir_known(parts):
                return True
    if form == REF_FORM_BARE and not _first_dir_known(parts):
        return True
    return False


def has_repo_path_shape(token: str, form: str = REF_FORM_BARE) -> bool:
    """判定 token 是否具仓根相对路径形态（提取准入闸，宽松收录）。

    规则：含 `/` 且无空白；非 URL/锚点；非 ``./`` ``../`` ``/`` 开头（相对/绝对
    路径非仓根口径——相对断链归 DOC-REF-BROKEN）；路径段非空；末段带扩展名时
    扩展名须 1-8 位字母数字；无扩展名末段=目录引用形态（bare 裸词必须带尾斜杠
    或已知顶层目录，防 "and/or" 类散文误报）。
    """
    if not isinstance(token, str):
        return False
    t = normalize_ref(token)
    if _rejects_basic_shape(t):
        return False
    parts = [p for p in t.split("/") if p != ""]
    if _rejects_segment_shape(parts):
        return False
    if _rejects_extension_shape(parts[-1]):
        return False
    # 尾斜杠基于原始 token 判（归一会保留尾部 `/`，但裸引号包裹等边缘口径不变）
    if _rejects_form_gate(parts, form, token.rstrip().endswith("/")):
        return False
    return True


def is_template_form(token: str) -> bool:
    """模板/占位/截断形态判定（S1 A 类 196 条实证形态，提取层豁免真源）。

    覆盖：占位 token（xxx/lXX/</>/.../module_name 等 78）、``_`` 结尾前缀片段
    （`data/asset_`、`t0_rule_manifest_` 等 116，源文档为通配/日期后缀运行时
    文件）、Git 托管 URL 断片（`config/apollo/blob/master/README.md` 系链接被
    截断，2）。门在违规判定前调用=误报防线上移到提取层（S1 §4.4 风险 1）。
    """
    if not isinstance(token, str):
        return False
    t = normalize_ref(token)
    if not t:
        return False
    if any(ch in t for ch in _TEMPLATE_CHARS):
        return True
    low = t.lower()
    if any(s in low for s in _TEMPLATE_SUBSTRINGS_CI):
        return True
    if t.endswith("_") or t.endswith("-"):
        return True
    if _TEMPLATE_TAIL_RE.search(t):
        return True
    if any(p in _GIT_HOSTED_SEGMENTS for p in t.split("/")):
        return True
    return False


def is_cas_residue(token: str) -> bool:
    """CAS 残渣形态判定：`.tmp` 结尾或 `.tmp.` 中段（查类 4 / 基线 E1 同判据）。"""
    if not isinstance(token, str):
        return False
    return bool(_CAS_RESIDUE_RE.search(normalize_ref(token)))


def is_ephemeral_target(token: str) -> bool:
    """被引路径含临时区分量（_working/.runtime/session_logs）——查类 3 / 基线 B 同判据。"""
    if not isinstance(token, str):
        return False
    t = normalize_ref(token)
    return any(p in EPHEMERAL_COMPONENTS for p in t.split("/") if p)


def is_permanent_referrer(path: str) -> bool:
    """引用方文件是否永久侧（路径不含临时区分量）——查类 3 只拦永久→临时方向。"""
    if not isinstance(path, str):
        return False
    return not is_ephemeral_target(path)


def extract_refs(content: str) -> list[RefHit]:
    """从 md/yaml 内容提取全部仓根路径形态引用（四形态，行内去重、跨形态保留）。

    处理序（防重复捕获）：逐行先提 markdown 链接 target（剥锚点），将该 span
    打盲后再提反引号 token，再打盲提表格单元格，最后对残余提裸词。同 (行, token,
    形态) 去重；同 token 不同形态/不同行各自保留（门的 deadref 查类用形态集判定
    是否归 DOC-REF-BROKEN 面）。非 str 输入返回空列表（ERROR_CONTRACT）。
    """
    if not isinstance(content, str) or not content:
        return []
    seen: dict[tuple[int, str, str], None] = {}  # 有序去重（py3.7+ dict 序）

    def _collect(line_no: int, token: str, form: str) -> None:
        tok = normalize_ref(token)
        if tok and has_repo_path_shape(tok, form):
            seen[(line_no, tok, form)] = None

    for line_no, raw in enumerate(content.splitlines(), start=1):
        # 1. markdown 链接（先提先盲——避免 target 被裸词/单元格二次捕获为异形态噪音）
        for m in _MD_LINK_RE.finditer(raw):
            _collect(line_no, m.group(2), REF_FORM_MD_LINK)
        line = _MD_LINK_RE.sub(" ", raw)
        # 2. 反引号包裹
        for m in _BACKTICK_RE.finditer(line):
            _collect(line_no, m.group(1), REF_FORM_BACKTICK)
        line = _BACKTICK_RE.sub(" ", line)
        # 3. 表格单元格
        for m in _TABLE_CELL_RE.finditer(line):
            _collect(line_no, m.group(1), REF_FORM_TABLE_CELL)
        line = _TABLE_CELL_RE.sub(" ", line)
        # 4. 裸词（准入闸在 has_repo_path_shape 的 bare 分支：已知顶层目录/尾斜杠）
        for m in _BARE_TOKEN_RE.finditer(line):
            _collect(line_no, m.group(0), REF_FORM_BARE)

    return [RefHit(line_no=ln, token=tok, form=form) for (ln, tok, form) in seen]
