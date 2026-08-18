# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/add_module_translation.py | §
# [MODULE] scripts.governance.d3_metadata.add_module_translation
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.module_translation_loader (is_generic_plain_zh, is_generic_plain_suffix, get_module_translation); docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml (翻译真源)
# [CONSUMERS] AI 新建/更新模块时调用以合规写入大白话简介；TRANSLATION-COVERAGE gate 修复指引引用
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 按 module_path 唯一键 upsert；写入前 MUST 通过 is_generic_plain_zh/is_generic_plain_suffix 校验（拒模板化简介，治本）；强制双引号转义；写后 YAML 解析校验；写入后失效 module_translation_loader 缓存；module_path 正斜杠归一化
# [MODIFY-GUARD] scripts/governance/d3_metadata/add_module_translation.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=SUCCESS, exit 1=VALIDATION_ERROR(简介不合规/字段缺失), exit 2=IO/YAML_ERROR
# [TESTS] tests/governance/d3_metadata/test_add_module_translation.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""add_module_translation.py — 模块翻译条目合规写入工具（TRANSLATION-COVERAGE 配套）。

把"在哪里更新 / 怎么更新"落地为一条命令：AI 新建或更新模块时，调用本脚本向
翻译真源 ``module_translation_registry.yaml`` upsert 一条 entry（含大白话 plain_zh）。

真源边界（SSoT 分类铁律 TRAE-062）
----------------------------------
模块翻译属**规则数据** → 真源是 YAML 文件。本脚本是 YAML 的合规写入入口，
禁止在生成器代码/DB 里硬编码模块翻译。与 ``apply_depgraph.py``（写 DB 架构数据）
是正交真源，互不写入，只能校验对方。

治本（防蔓延闭环）
------------------
病根：此前大白话简介靠事后治理（审计→批量修→提交），新模块仍会持续制造缺口。
本工具 + TRANSLATION-COVERAGE gate + reconciler 构成"写入入口→提交阻断→存量对账"
三层闭环：AI 创新模块后跑本命令合规写入，gate 在提交时校验，reconciler 持续对账。

写入前校验（治本，非事后）
--------------------------
1. plain_zh 非空且 CJK≥8（与本次治理基线一致）
2. 复用 module_translation_loader.is_generic_plain_zh 拒全串通用模板
3. 复用 is_generic_plain_suffix 拒剥离 name 前缀后的通用后缀
任一不过 → exit 1，拒绝写入（防 AI 填"提供包入口和模块加载功能"糊弄）。

用法 / Usage::

    python scripts/governance/d3_metadata/add_module_translation.py \\
        --path src/zephyr/xxx/yyy.py \\
        --domain D_GOV_RULE \\
        --name-zh "中文名" --name-en "English Name" \\
        --desc-zh "技术简介" --desc-en "English desc" \\
        --plain-zh "大白话：做什么/解决什么/怎么做"

Exit codes:
    0 = SUCCESS（upsert 成功）
    1 = VALIDATION_ERROR（简介不合规 / 必填字段缺失）
    2 = IO/YAML_ERROR（文件读写或解析失败）
"""
from __future__ import annotations

__manifest__ = """
args: []
description: add_module_translation.py — 模块翻译条目合规写入工具（TRANSLATION-COVERAGE 配套）。
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import re
import sys
from pathlib import Path

# bootstrap _shared（与同目录其他 d3_metadata 脚本一致，使 module_translation_loader 可 import）
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT  # noqa: E402
from _shared.module_translation_loader import (  # noqa: E402
    is_generic_plain_zh,
    is_generic_plain_suffix,
)

# 翻译真源路径（SSoT：规则数据真源是 YAML 文件）
REGISTRY_YAML = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
    / "module_translation_registry.yaml"
)

# plain_zh 最低 CJK 字符数（与本次治理基线一致，防过短无信息简介）
_MIN_CJK = 8

EXIT_SUCCESS = 0
EXIT_VALIDATION = 1
EXIT_IO = 2


def _cjk_len(s: str) -> int:
    """统计 CJK 字符数（大白话最低信息量基线）。"""
    return len(re.findall(r"[\u4e00-\u9fff]", s or ""))


def _yaml_quote(s: str) -> str:
    """YAML 双引号转义（治本：plain_zh 含冒号/引号/破折号时安全）。

    对标 tmp/_apply_handwritten.py 验证过的转义逻辑：反斜杠→双反斜杠，
    双引号→\\\\\"，控制字符→转义序列。始终用双引号包裹，确保含 ``: ``/``#``
    的值不被 YAML 误解析。
    """
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    s = s.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return '"%s"' % s


def _normalize_path(p: str) -> str:
    """module_path 正斜杠归一化（Windows 反斜杠兼容）。"""
    return (p or "").replace("\\", "/").strip()


def _validate_plain(plain_zh: str, name_zh: str) -> tuple[bool, str]:
    """写入前校验 plain_zh 合规性（治本：拒模板化简介）。

    Returns:
        (ok, reason)——ok=True 合规；ok=False 时 reason 说明不合规原因。
    """
    if not plain_zh or not plain_zh.strip():
        return False, "plain_zh 为空"
    if _cjk_len(plain_zh) < _MIN_CJK:
        return False, f"plain_zh CJK 字符数 {_cjk_len(plain_zh)} < {_MIN_CJK}（信息量不足）"
    if is_generic_plain_zh(plain_zh):
        return False, "plain_zh 是多模块共用的通用模板（is_generic_plain_zh 命中），需写模块特异简介"
    if name_zh and is_generic_plain_suffix(plain_zh, name_zh):
        return False, "plain_zh 剥离 name_zh 前缀后的后缀是通用模板（is_generic_plain_suffix 命中），需写模块特异简介"
    return True, ""


def _format_entry_block(entry: dict) -> str:
    """格式化一条 entry 为 YAML 块字符串（2 空格缩进，与现有条目风格一致）。

    module_path/domain_id 为简单标识符，不转义；5 个文本字段强制双引号转义
    （含冒号/破折号等 YAML 特殊字符时安全）。
    """
    lines = [
        f"- module_path: {_normalize_path(entry['module_path'])}",
        f"  domain_id: {entry['domain_id']}",
        f"  name_zh: {_yaml_quote(entry['name_zh'])}",
        f"  name_en: {_yaml_quote(entry['name_en'])}",
        f"  desc_zh: {_yaml_quote(entry['desc_zh'])}",
        f"  desc_en: {_yaml_quote(entry['desc_en'])}",
        f"  plain_zh: {_yaml_quote(entry['plain_zh'])}",
    ]
    return "\n".join(lines)


def _split_entries_section(yaml_text: str) -> tuple[str, str, str]:
    """把 YAML 文本切成 (前导, entries 列表区, 后续段落) 三段。

    真源 YAML 结构：顶层含 ``entries:`` 列表，其后还有 ``battle_map_steps:`` /
    ``battle_map_cross_cutting:`` 等同顶层段落。新增条目 MUST 落在 entries 列表区内，
    追加到文件末尾会脱离 entries 作用域导致 YAML 解析失败（治本：2026-08-02 首版
    误追加到文件尾损坏真源，git checkout 回滚后改为段落感知切分）。

    Returns:
        ``(preamble, entries_body, tail)``——preamble 含 ``entries:`` 行及之前所有内容；
        entries_body 为列表项文本（不含 ``entries:`` 行，不含尾随段落）；tail 为
        ``battle_map_steps:`` 及之后所有内容。无 entries 段时 entries_body 为空、
        tail 为空。
    """
    lines = yaml_text.split("\n")
    # 定位 entries: 行（列 0 顶层键）
    entries_idx = None
    for i, ln in enumerate(lines):
        if ln.startswith("entries:") and ln.rstrip() == "entries:":
            entries_idx = i
            break
    if entries_idx is None:
        # 无 entries 段——整体当 preamble，无法 upsert（调用方会报错）
        return yaml_text, "", ""

    # 定位 entries 之后的下一个顶层键（列 0 的 `word:` 形式，非列表项 `-`/缩进）
    next_section_idx = None
    for j in range(entries_idx + 1, len(lines)):
        ln = lines[j]
        if ln and not ln[0].isspace() and not ln.startswith("-") and not ln.startswith("#"):
            # 顶层键：形如 `battle_map_steps:` ——冒号在前半段
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", ln):
                next_section_idx = j
                break

    if next_section_idx is None:
        # entries 是最后一个段落
        preamble = "\n".join(lines[: entries_idx + 1])
        entries_body = "\n".join(lines[entries_idx + 1 :])
        return preamble, entries_body, ""

    preamble = "\n".join(lines[: entries_idx + 1])
    entries_body = "\n".join(lines[entries_idx + 1 : next_section_idx])
    tail = "\n".join(lines[next_section_idx:])
    return preamble, entries_body, tail


def _upsert_entry(yaml_text: str, entry: dict) -> tuple[str, bool]:
    """按 module_path 唯一键 upsert 一条 entry，返回 (新文本, 是否新增)。

    段落感知（治本）：只在 ``entries:`` 列表区内操作，命中已有条目→替换整块；
    未命中→插到 entries 列表末尾（下一个顶层段落之前），绝不追加到文件尾。
    采用块切分（按 ``\\n- module_path:`` 分隔）保留现有格式与注释，对标
    tmp/_apply_handwritten.py 验证过的文本操作模式。
    """
    norm_path = _normalize_path(entry["module_path"])
    preamble, entries_body, tail = _split_entries_section(yaml_text)
    if not preamble:
        raise ValueError("YAML 中未找到 `entries:` 顶层段，无法 upsert")

    # 定位首个条目（行首 `- module_path:`），其前为 lead（空白/注释），其后全部为 blocks。
    # 治本：首条目在 entries_body 行首无前置 \n，单纯按 \n 切分会把首条目误并入 lead，
    # 导致更新首条目时漏匹配→追加重复（2026-08-02 首版 bug）。
    first = re.search(r"(?m)^- module_path:", entries_body)
    if first is None:
        lead = entries_body
        blocks: list[str] = []
    else:
        lead = entries_body[: first.start()]
        rest = entries_body[first.start() :]
        # rest 以 "- module_path:" 开头，按 "\n- module_path:" 边界切块
        blocks = re.split(r"\n(?=- module_path:)", rest)
    new_block = _format_entry_block(entry)

    for i, blk in enumerate(blocks):
        m = re.match(r"- module_path:\s*(\S+)\n", blk)
        if m and _normalize_path(m.group(1)) == norm_path:
            blocks[i] = new_block
            return _reassemble(preamble, lead, blocks, tail), False  # 更新

    # 未命中 → 追加到 entries 列表末尾（tail 之前）
    blocks.append(new_block)
    return _reassemble(preamble, lead, blocks, tail), True  # 新增


def _reassemble(preamble: str, lead: str, blocks: list[str], tail: str) -> str:
    """重排 YAML 文本：preamble + entries 列表区 + tail，保证段落间换行合法。

    entries 列表区 = lead（前导空白/注释）+ 各 entry 块用单换行连接。
    preamble 末尾需有换行；tail 前需有换行分隔。整体末尾保留单个换行。
    """
    # 列表区主体：lead + 块连接（块之间单换行，lead 与首块间单换行）
    body_parts = []
    if lead.strip():
        body_parts.append(lead.rstrip("\n"))
    body_parts.extend(b.rstrip("\n") for b in blocks)
    entries_section = "\n".join(body_parts)

    # 组装：preamble 末尾确保换行 → entries_section → 换行 → tail
    pre = preamble if preamble.endswith("\n") else preamble + "\n"
    mid = entries_section + "\n" if entries_section else ""
    post = tail if tail else ""
    # tail 与 mid 之间需换行分隔（tail 是新顶层键，必须另起一行）
    if post and not post.startswith("\n"):
        post = "\n" + post
    new_text = pre + mid + post
    if not new_text.endswith("\n"):
        new_text += "\n"
    return new_text


def _invalidate_loader_cache() -> None:
    """写入后失效 module_translation_loader 缓存，使同进程后续读取看到新条目。

    loader 用模块级 _PATH_CACHE 缓存；CLI 一次性进程不严格需要，但批量场景
    /测试场景下避免脏读。fail-open：失效失败不阻断（只是缓存陈旧，下次进程自然刷新）。
    """
    try:
        import _shared.module_translation_loader as mtl  # noqa: WPS433

        mtl._PATH_CACHE = None
        mtl._GENERIC_PLAIN_CACHE = None
        mtl._GENERIC_DESC_CACHE = None
        mtl._GENERIC_SUFFIX_CACHE = None
    except Exception:  # noqa: BLE001 — 缓存失效失败不阻断写入
        pass


def add_translation(entry: dict, *, dry_run: bool = False) -> tuple[int, str]:
    """主入口：校验 + upsert + 写盘 + 解析校验。

    Args:
        entry: 含 module_path/domain_id/name_zh/name_en/desc_zh/desc_en/plain_zh 的 dict。
        dry_run: True 只校验不写盘。

    Returns:
        (exit_code, message)。
    """
    # 1. 必填字段校验
    required = ["module_path", "domain_id", "name_zh", "plain_zh"]
    missing = [f for f in required if not (entry.get(f) or "").strip()]
    if missing:
        return EXIT_VALIDATION, f"必填字段缺失: {missing}"

    # 2. plain_zh 合规校验（写入前治本）
    ok, reason = _validate_plain(entry["plain_zh"], entry["name_zh"])
    if not ok:
        return EXIT_VALIDATION, f"plain_zh 校验失败: {reason}"

    # 3. 读取真源
    try:
        yaml_text = REGISTRY_YAML.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return EXIT_IO, f"读取翻译真源失败: {type(e).__name__}: {e}"

    # 4. upsert
    new_text, is_new = _upsert_entry(yaml_text, entry)

    if dry_run:
        action = "新增" if is_new else "更新"
        return EXIT_SUCCESS, f"[dry-run] {action} {entry['module_path']} 校验通过"

    # 5. 写盘
    try:
        REGISTRY_YAML.write_text(new_text, encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return EXIT_IO, f"写入翻译真源失败: {type(e).__name__}: {e}"

    # 6. 写后 YAML 解析校验（防写入损坏真源）
    try:
        import yaml  # type: ignore[import-untyped]

        data = yaml.safe_load(REGISTRY_YAML.read_text(encoding="utf-8"))
        entries = (data or {}).get("entries", []) or []
        # 确认条目确实落盘
        norm_path = _normalize_path(entry["module_path"])
        hit = any(
            _normalize_path(e.get("module_path", "")) == norm_path
            for e in entries if isinstance(e, dict)
        )
        if not hit:
            return EXIT_IO, f"写后校验失败：entries 中未找到 {norm_path}"
    except Exception as e:  # noqa: BLE001
        return EXIT_IO, f"写后 YAML 解析失败（真源可能损坏）: {type(e).__name__}: {e}"

    # 7. 失效 loader 缓存
    _invalidate_loader_cache()

    action = "新增" if is_new else "更新"
    return EXIT_SUCCESS, f"{action} 翻译条目: {entry['module_path']}（entries 共 {len(entries)} 条）"


def _build_argparser() -> argparse.ArgumentParser:
    """_build_argparser implementation."""
    p = argparse.ArgumentParser(
        prog="add_module_translation.py",
        description="模块翻译条目合规写入工具（TRANSLATION-COVERAGE 配套）。按 module_path upsert 一条含大白话 plain_zh 的翻译条目。",
    )
    p.add_argument("--path", required=True, help="模块相对路径（如 src/zephyr/.../m.py）")
    p.add_argument("--domain", required=True, help="域 ID（如 D_GOV_RULE）")
    p.add_argument("--name-zh", required=True, help="模块中文名")
    p.add_argument("--name-en", default="", help="模块英文名（可选）")
    p.add_argument("--desc-zh", default="", help="技术简介中文（可选）")
    p.add_argument("--desc-en", default="", help="技术简介英文（可选）")
    p.add_argument("--plain-zh", required=True, help="大白话简介（做什么/解决什么/怎么做，CJK≥8，禁模板化）")
    p.add_argument("--dry-run", action="store_true", help="只校验不写盘")
    return p


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, run logic, return exit code."""
    args = _build_argparser().parse_args(argv)
    entry = {
        "module_path": _normalize_path(args.path),
        "domain_id": args.domain,
        "name_zh": args.name_zh,
        "name_en": args.name_en,
        "desc_zh": args.desc_zh,
        "desc_en": args.desc_en,
        "plain_zh": args.plain_zh,
    }
    code, msg = add_translation(entry, dry_run=args.dry_run)
    print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())
