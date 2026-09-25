# [BLUEPRINT] MOD-QCURE-HYGIENE | scripts/governance/registry_dedup_audit.py | §登记册数据卫生对账
# [MODULE] scripts.governance.registry_dedup_audit
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib（re/json/argparse/difflib）；PyYAML；zephyr.shared.io.file_utils.safe_write_text/content_sha256；zephyr.shared.io.paths.REPO_ROOT
# [CONSUMERS] QMine 战役总包（st-qmine-20260925 施工线 A2G 验收）；commit_queue landing 死信钩（事件触发，禁 cron）；AI session 按需 CLI
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 默认 dry-run 全程只读（无 --heal-equal 不落一字）；身份键=册自声明 unique_key 优先（list[str] 全册默认 / 含"."的 container.field 点分 / {container: [fields]} dict 三形态），无声明退「首标量字段」复合；判等=yaml.safe_load 后按对象相等（json canonical），同键同侧 data 全等=真重复（可净删）、「不等」=真冲突（只报告 dump 双条，撞号裁定属 Owner 门，本器绝不代择优）；heal 只净删语义全等条目的后至者（保留首条），文本级块切除禁 yaml 往返（保字节），写必经 safe_write_text CAS（expected_base_sha256+allow_mass_edit=True，写后重解析核等值，不等即拒写abort）；解析失败册（坏字节/坏转义）只报告不修；枚举=entry_schema 行内 # 注释（剥括注后按 |/ 切分，token 须全词），注释与实值互为子串=胶连污染→该字段跳过（algorithm_status 假阳教训）；漂移=同容器字段名 difflib≥0.75 候选对
# [MODIFY-GUARD] none（只读报表器+裁定授权的净删外科件；--heal-equal 即净删通道，撞号只报告）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单册解析失败→计入 parse_fail 继续扫；heal 前解析核验失败→拒写该册计 healed_failed，exit 2；--catalogs 目录不存在→exit 1；零发现=诚实零
# [TESTS] tests/governance/test_registry_dedup_audit.py
# [A_module] module_id=QCURE-HYGIENE-1 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""registry_dedup_audit.py — 登记册全 catalog 对账器（QMine M2 施工线 A2G 承重件）。

背景：workbook 01_hot_registry_merge §3.5——撞号/同键重复无工具发现，每个触册落地项
反复付死信成本；workbook 02_registry_hygiene——76 册普查出精确重复/真冲突/枚举违规/
字段漂移四类缺陷，须机械对账器持续盯（静态清单禁手工维护铁律 §9.5）。

四类报告：精确重复（data 全等，可净删）｜同键异内容真冲突（dump 双条，只报告）｜
枚举违规（schema 注释枚举 vs 实值）｜字段漂移（同容器近名字段对）。

用法（仓库根，Python 3.12）：
    python scripts/governance/registry_dedup_audit.py                  # 全 catalog dry-run，stdout
    python scripts/governance/registry_dedup_audit.py --heal-equal    # 净删语义全等条目（裁定授权）
    python scripts/governance/registry_dedup_audit.py --catalogs DIR  # 指定目录（测试注入）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

import yaml

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: PLC0415
from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415 — SSOT canonical

DEFAULT_CATALOG_DIR = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
_DUMP_CHARS = 400  # 冲突双条 dump 截断
_ENUM_TOKEN = re.compile(r"^[\w\u4e00-\u9fff-]+$")
_PAREN = re.compile(r"[（(][^（）()]*[）)]")
_ITEM = re.compile(r"^( *)- ")


def discover_catalogs(directory: Path) -> list[Path]:
    """列 catalog yaml；.bak/.tmp 垃圾件排除（workbook 02 D13 口径）。"""
    return sorted(p for p in Path(directory).glob("*.yaml")
                  if not p.name.endswith((".bak",)) and ".tmp." not in p.name and ".bak" not in p.name)


def _entry_containers(doc: object) -> dict[str, list]:
    """顶层键值为 list 的容器：全 dict 条目册 / 全标量清单；空与混型跳过。"""
    out: dict[str, list] = {}
    if isinstance(doc, dict):
        for k, v in doc.items():
            if isinstance(v, list) and v and all(isinstance(i, dict) for i in v):
                out[k] = v
            elif isinstance(v, list) and v and all(isinstance(i, (str, int, float, bool)) for i in v):
                out[k] = v
    elif isinstance(doc, list) and doc:
        out["__root__"] = doc
    return out


def _key_fields_for(decl: object, container: str) -> list[str] | None:
    """unique_key 三形态解析：list[str]（全册默认）/点分 container.field/{container: [fields]}。"""
    if isinstance(decl, dict):
        v = decl.get(container)
        return [str(x) for x in v] if isinstance(v, list) and v else None
    if isinstance(decl, list) and decl:
        dotted: dict[str, list[str]] = {}
        plain: list[str] = []
        for item in decl:
            if not isinstance(item, str):
                return None
            if "." in item:
                c, f = item.split(".", 1)
                dotted.setdefault(c, []).append(f)
            else:
                plain.append(item)
        return dotted.get(container) if dotted else plain
    return None


def _identity(entry: object, fields: list[str] | None) -> tuple | None:
    """声明字段值 tuple；键字段缺失/非标量=身份判不了（None，只报告不判等）。"""
    if not fields or not isinstance(entry, dict):
        return None
    vals: list[object] = []
    for f in fields:
        if f not in entry or isinstance(entry[f], (dict, list)) or entry[f] is None:
            return None
        vals.append(entry[f])
    return tuple(vals)


def _fallback_identity(entry: object) -> tuple | None:
    """无声明退路：条目首个标量字段（与 landing 合并键同口径）。"""
    if isinstance(entry, dict):
        for k, v in entry.items():
            if isinstance(v, (str, int, float, bool)):
                return (f"first:{k}", v)
    elif isinstance(entry, (str, int, float, bool)):
        return (str(entry),)
    return None


def _canonical(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)


def _schema_enums(text: str) -> dict[str, dict[str, list[str]]]:
    """*_schema 块行内 # 注释→字段枚举（注释被 safe_load 剥除，必须按原文解析）；
    token<2 弃；token 须含 ASCII 字母数字（纯中文注释词不入枚举）；胶连污染由调用方判。"""
    out: dict[str, dict[str, list[str]]] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        head = re.match(r"^([A-Za-z_]\w*_schema):\s*$", lines[i])
        if not head:
            i += 1
            continue
        owner, indent, fields, j = head.group(1)[:-7], None, {}, i + 1
        while j < len(lines):
            ln = lines[j]
            if ln.strip() == "":
                j += 1
                continue
            im = re.match(r"^( +)([A-Za-z_]\w*):\s*(.*)$", ln)
            if not im:
                break
            if indent is None:
                indent = len(im.group(1))
            if len(im.group(1)) != indent:
                break  # 缩进回落=块结束；嵌套行缩进更深也落入此分支
            comment = im.group(3).split("#", 1)[1] if "#" in im.group(3) else ""
            toks = [t.strip() for t in re.split(r"[|/]", _PAREN.sub("", comment))]
            toks = [t for t in toks if t and _ENUM_TOKEN.match(t) and re.search(r"[A-Za-z0-9]", t)]
            if len(toks) >= 2:
                fields[im.group(2)] = toks
            j += 1
        if fields:
            out[owner] = fields
        i = j
    return out


def scan_catalog(path: Path) -> dict:
    """单册四类扫描；返回结构化报告（dry-run 主路径）。"""
    rpt: dict = {"file": str(path), "parse_fail": None, "exact_dup": [], "conflicts": [],
                 "unresolved_identity": 0, "enum_violations": {}, "drift_pairs": []}
    try:
        text = path.read_text(encoding="utf-8")
        doc = yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001 — 坏字节/坏转义如实报告
        rpt["parse_fail"] = f"{type(exc).__name__}: {str(exc)[:160]}"
        return rpt
    containers = _entry_containers(doc)
    if isinstance(doc, dict):
        schemas = _schema_enums(text)
        decl = doc.get("unique_key")
    else:
        schemas, decl = {}, None
    for name, items in containers.items():
        fields = _key_fields_for(decl, name) if decl is not None else None
        groups: dict[tuple, list[int]] = {}
        for idx, entry in enumerate(items):
            ident = _identity(entry, fields) or _fallback_identity(entry)
            if ident is None:
                rpt["unresolved_identity"] += 1
                continue
            groups.setdefault(ident, []).append(idx)
        for ident, idxs in groups.items():
            if len(idxs) < 2:
                continue
            payload = [_canonical(items[i]) for i in idxs]
            if len(set(payload)) == 1:
                rpt["exact_dup"].append({"container": name, "key": list(ident) if isinstance(ident, tuple) else ident,
                                         "count": len(idxs)})
            else:
                rpt["conflicts"].append({"container": name, "key": list(ident) if isinstance(ident, tuple) else ident,
                                         "entries": [p[:_DUMP_CHARS] for p in payload]})
        # 枚举违规：schema 归属（entry_ 广播 / dataset→datasets 复数匹配）
        for schema_owner, enums in schemas.items():
            if not isinstance(items[0], dict):
                continue
            if not (name == schema_owner or name == schema_owner + "s" or schema_owner == "entry"):
                continue
            observed: dict[str, Counter] = {}
            for e in items:  # type: ignore[union-attr]
                for f, sv in enums.items():
                    v = e.get(f)
                    if isinstance(v, str) and v:
                        observed.setdefault(f, Counter())[v] += 1
            for f, toks in enums.items():
                vals = observed.get(f, Counter())
                if vals and all(any(v in t for t in toks) for v in vals):
                    continue  # 胶连污染（algorithm_status 教训：全部实值均系 token 子串）→ 注释不可机读
                bad = {v: n for v, n in vals.items()
                       if v not in toks and len(v) <= 40 and _ENUM_TOKEN.match(v) and re.search(r"[A-Za-z0-9]", v)}
                if bad:
                    rpt["enum_violations"][f"{name}.{f}"] = bad
        # 字段漂移：同容器近名字段对（difflib≥0.75，最短≥5）
        if isinstance(items[0], dict):
            freq = Counter(f for e in items for f in e)  # type: ignore[union-attr]
            names = sorted(freq)
            for i, a in enumerate(names):
                for b in names[i + 1:]:
                    if min(len(a), len(b)) >= 5 and SequenceMatcher(None, a, b).ratio() >= 0.75:
                        rpt["drift_pairs"].append({"container": name, "fields": [a, b],
                                                   "counts": [freq[a], freq[b]]})
    return rpt


def _iter_blocks(lines: list[str], container: str) -> list[tuple[int, int]] | None:
    """块扫描（heal 专用）：返回条目块 [start,end) 行区间（content 界，吃尾随空行）。"""
    if container == "__root__":
        starts = [i for i, ln in enumerate(lines) if _ITEM.match(ln) and ln.startswith("- ")]
    else:
        key_at = next((i for i, ln in enumerate(lines) if re.match(rf"^{re.escape(container)}:\s*(#.*)?$", ln)), None)
        if key_at is None:
            return None
        ind = next((_ITEM.match(ln).end(1) for ln in lines[key_at + 1:] if _ITEM.match(ln)), None)  # type: ignore[union-attr]
        if ind is None:
            return None
        starts = [i for i, ln in enumerate(lines) if i > key_at and ln.startswith(" " * ind + "- ")]
    if not starts:
        return None
    blocks = []
    for j, s in enumerate(starts):
        e = starts[j + 1] if j + 1 < len(starts) else len(lines)
        while e > s + 1 and (lines[e - 1].strip() == "" or lines[e - 1].lstrip().startswith("#")):
            e -= 1  # 尾随空行/注释留在原位（注释属后块，不误吞）
        blocks.append((s, e))
    return blocks


def heal_equal(path: Path) -> tuple[bool, int]:
    """净删语义全等后至块：文本级切除+CAS 写+重解析核等值；任何核验不过=拒写不落盘。"""
    old_text = path.read_text(encoding="utf-8")
    try:
        doc = yaml.safe_load(old_text)
    except Exception:  # noqa: BLE001 — 解析失败册不 heal
        return False, 0
    containers = _entry_containers(doc)
    decl = doc.get("unique_key") if isinstance(doc, dict) else None
    lines = old_text.splitlines(keepends=True)
    doomed: set[int] = set()
    removed: dict[str, set[int]] = {}
    total = 0
    for name, items in containers.items():
        fields = _key_fields_for(decl, name) if decl is not None else None
        groups: dict[tuple, list[int]] = {}
        for idx, entry in enumerate(items):
            ident = _identity(entry, fields) or _fallback_identity(entry)
            if ident is None:
                groups = {}
                break
            groups.setdefault(ident, []).append(idx)
        dup_idxs: set[int] = set()
        for idxs in groups.values():
            if len(idxs) >= 2 and len({_canonical(items[i]) for i in idxs}) == 1:
                dup_idxs.update(idxs[1:])  # 保留首条，后至全等者净删
                total += len(idxs) - 1
        if not dup_idxs:
            continue
        blocks = _iter_blocks(lines, name)
        if blocks is None or len(blocks) != len(items):
            return False, 0
        for (s, e), idx in zip(blocks, range(len(items))):
            if idx not in dup_idxs:
                continue
            try:  # 块↔条目逐一核验（块文本解析必须等于该条目，防误切）
                if yaml.safe_load("".join(lines[s:e])) != [items[idx]]:
                    return False, 0
            except Exception:  # noqa: BLE001
                return False, 0
            doomed.update(range(s, e))
        removed[name] = dup_idxs
    if not doomed:
        return False, 0
    new_text = "".join(ln for i, ln in enumerate(lines) if i not in doomed)
    new_doc = yaml.safe_load(new_text)
    want = doc
    for name, idxs in removed.items():
        src = list(containers[name])
        if isinstance(want, dict):
            want = dict(want)
            want[name] = [e for i, e in enumerate(src) if i not in idxs]
        else:
            want = [e for i, e in enumerate(src) if i not in idxs]
    if new_doc != want:
        return False, 0
    safe_write_text(path, new_text, expected_base_sha256=content_sha256(old_text),
                    allow_mass_edit=True, repo_root=None)
    if yaml.safe_load(Path(path).read_text(encoding="utf-8")) != new_doc:
        # MSG-EXPOSURE（5.99.20）：完整路径属敏感面，消息只留文件名，全路径落 detail 属性
        raise HealVerifyError(f"heal 后读回核验失败: {Path(path).name}", path=str(path))
    return True, total


class HealVerifyError(RuntimeError):
    """heal 写后读回核验失败（MSG-EXPOSURE 合规：路径走 path 属性不走消息文本）。"""

    def __init__(self, msg: str, path: str = "") -> None:
        super().__init__(msg)
        self.path = path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="登记册全 catalog 对账器（默认 dry-run）")
    ap.add_argument("--catalogs", type=Path, default=DEFAULT_CATALOG_DIR, help="catalog 目录（默认真源）")
    ap.add_argument("--heal-equal", action="store_true", help="净删语义全等重复条目（裁定授权，默认关）")
    args = ap.parse_args(argv)
    if not args.catalogs.is_dir():
        print(f"[FATAL] catalog 目录不存在: {args.catalogs}", file=sys.stderr)
        return 1
    files = discover_catalogs(args.catalogs)
    tot = Counter()
    print(f"[SCAN] {args.catalogs} → {len(files)} 册")
    healed = failed = 0
    for p in files:
        rpt = scan_catalog(p)
        tot["parse_fail"] += bool(rpt["parse_fail"])
        tot["exact_dup_removable"] += sum(d["count"] - 1 for d in rpt["exact_dup"])
        tot["conflict_groups"] += len(rpt["conflicts"])
        tot["unresolved_identity"] += rpt["unresolved_identity"]
        tot["enum_violations"] += sum(sum(b.values()) for b in rpt["enum_violations"].values())
        tot["drift_pairs"] += len(rpt["drift_pairs"])
        if rpt["parse_fail"]:
            print(f"[PARSE-FAIL] {p.name}: {rpt['parse_fail']}")
            continue
        if rpt["exact_dup"] or rpt["conflicts"]:
            for d in rpt["exact_dup"]:
                print(f"[EXACT-DUP] {p.name} {d['container']} key={d['key']} ×{d['count']}（可净删 {d['count'] - 1}）")
            for c in rpt["conflicts"]:
                print(f"[CONFLICT] {p.name} {c['container']} key={c['key']} 异内容双条（只报告，撞号归 Owner 裁定）")
                for e in c["entries"]:
                    print(f"  ├ {e}")
        for k, bad in rpt["enum_violations"].items():
            print(f"[ENUM] {p.name} {k}: {bad}")
        for d in rpt["drift_pairs"]:
            print(f"[DRIFT] {p.name} {d['container']} {d['fields'][0]}({d['counts'][0]}) ~ {d['fields'][1]}({d['counts'][1]})")
        if args.heal_equal and rpt["exact_dup"]:
            ok, n = heal_equal(p)
            if ok:
                healed += 1
                print(f"[HEALED] {p.name} 净删 {n} 条全等重复")
            else:
                failed += 1
                print(f"[HEAL-REFUSED] {p.name} 核验不过，未写盘")
                continue
    print(f"[SUMMARY] 册={len(files)} 解析失败={tot['parse_fail']} 精确重复可净删={tot['exact_dup_removable']} "
          f"真冲突组={tot['conflict_groups']} 身份判不了={tot['unresolved_identity']} "
          f"枚举违规={tot['enum_violations']} 漂移对={tot['drift_pairs']} heal册={healed} heal拒={failed}")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
