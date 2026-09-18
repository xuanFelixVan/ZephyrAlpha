# [BLUEPRINT] MOD-AUTO-L3-001 | docs/_working/automation/campaign/blueprints/intel_harvester_blueprint.md | §
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] scripts.automation.validate_intel_registry
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] yaml; urllib.parse
# [CONSUMERS] config/intel_sources.yaml; config/intel_keywords.yaml（班前自检/pre-commit 校验对象）
# [STARTUP] manual
# [MATURITY] testing
# [MODIFY-GUARD] none
# [INVARIANTS] 静态清单红线配套（AGENTS.md §9 运维红线第 5 条"静态清单禁手工维护"）——两注册表任何改动过本件自检绿才可提交;
#   校验面=schema/URL 格式/词干正则可编译/计数字段一致性，fail-closed 退出非零;
#   只校验不修改：本件零写盘（只读注册表，报告走 stdout）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一校验不过→打印 FAIL 明细并 return 1；文件缺失/不可解析=FAIL（降级是 harvester 运行态语义，不是登记态语义）
# [TESTS] tests/automation/test_intel_harvester.py
# [A_module] module_id=MOD-AUTO-L3-001(暂编号) | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 班前自检/pre-commit 调用的手动校验 CLI，非常驻服务（自动触发无意义——无状态只读校验）
"""validate_intel_registry — intel 源注册表+关键词词表校验器（WO-①-01/03 配套）。

登记流程（两注册表 config/intel_sources.yaml、config/intel_keywords.yaml）：
    1. 追加/修改条目；
    2. python scripts/automation/validate_intel_registry.py 自检绿（schema/URL/正则/计数）；
    3. 提交（git_commit.py 正门）。
harvester 运行态另有降级语义：注册表缺失/损坏→内置默认+warn（班不炸）；本件是登记态
门禁——缺文件/坏 schema 直接 FAIL，两者职责不同勿混。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

import yaml

SUPPORTED_KINDS = ("rss", "rsshub")
SUPPORTED_FLAGS = (None, "IGNORECASE")

# ReDoS 防线（与 intel_harvester._RE_DOS_NESTED_QUANT 保持同式；本件刻意零仓内依赖，
# 故本地持有同式而非 import——两处同改）：嵌套量词（组内含量词+组外再量词）在恶意
# 文本上指数回溯，可编译≠安全，登记态 fail-closed 拒入。
_RE_DOS_NESTED_QUANT = re.compile(r"\([^()]*[+*{][^()]*\)\s*[+*{]")


def _looks_redos(stem: str) -> bool:
    return bool(_RE_DOS_NESTED_QUANT.search(stem))


def _check_source_url(e: dict, sid: str, kind: str, ref: str) -> list[str]:
    """单条目 enabled/url|route 校验 → FAIL 明细。"""
    issues: list[str] = []
    enabled = e.get("enabled")
    if not isinstance(enabled, bool):
        issues.append(f"{ref}({sid}): enabled 必须显式 bool")
    if kind == "rss":
        url = e.get("url")
        if not isinstance(url, str) or not url:
            issues.append(f"{ref}({sid}): rss 缺 url")
        else:
            parts = urlsplit(url)
            if parts.scheme not in ("http", "https") or not parts.netloc:
                issues.append(f"{ref}({sid}): url 格式非法（{url!r}，须 http(s)://host/...）")
            elif parts.username or parts.password:
                # user:pass@ 形态=密钥入册（RULE-SECRETS 邻接面）+ 凭据随注册表明文落盘
                issues.append(f"{ref}({sid}): url 禁带 userinfo（user:pass@=密钥入册违规）")
            elif not parts.netloc.isascii():
                # unicode 域名 urllib 直接 UnicodeEncodeError：登记态要求 punycode (xn--)
                issues.append(f"{ref}({sid}): url host 须 ASCII（unicode 域名请转 punycode）")
    elif kind == "rsshub":
        route = e.get("route")
        if not isinstance(route, str) or not route.startswith("/"):
            issues.append(f"{ref}({sid}): rsshub 缺 route（须以 / 开头）")
    return issues


def _check_source_entry(e, i: int, seen: set[str]) -> list[str]:
    """单条目校验 → FAIL 明细（kind 非法短路，与 harvester 降级口径一致）。"""
    ref = f"sources[{i}]"
    if not isinstance(e, dict):
        return [f"{ref}: 非映射"]
    sid = e.get("source_id")
    if not sid or not isinstance(sid, str):
        return [f"{ref}: 缺非空 source_id"]
    issues: list[str] = []
    if sid in seen:
        issues.append(f"{ref}: source_id 重复（{sid}）")
    seen.add(sid)
    kind = e.get("kind")
    if kind not in SUPPORTED_KINDS:
        issues.append(f"{ref}({sid}): kind 非法（{kind!r}，仅 {'/'.join(SUPPORTED_KINDS)}）")
        return issues
    issues += _check_source_url(e, sid, kind, ref)
    politeness = e.get("politeness")
    if politeness is not None and (not isinstance(politeness, str) or not politeness.strip()):
        issues.append(f"{ref}({sid}): politeness 须非空 UA 字符串")
    return issues


def _check_sources(path: Path) -> list[str]:
    """源注册表校验 → FAIL 明细列表（空=过）。"""
    issues: list[str] = []
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — 登记态 fail-closed
        return [f"sources: 文件不可读/不可解析: {exc}"]
    if not isinstance(raw, dict):
        return ["sources: 顶层必须是映射"]
    entries = raw.get("sources")
    if not isinstance(entries, list) or not entries:
        return ["sources: 缺非空 sources 列表"]
    declared = raw.get("source_count")
    # isinstance(True, int)==True 陷阱：source_count: true 在单源清单上会与 1 相等蒙混过关
    if isinstance(declared, bool) or not isinstance(declared, int) or declared != len(entries):
        issues.append(f"sources: source_count 计数漂移（声明 {declared!r}，实际 {len(entries)}）")
    seen: set[str] = set()
    for i, e in enumerate(entries, 1):
        issues += _check_source_entry(e, i, seen)
    return issues


def _check_keywords(path: Path) -> list[str]:
    """词表校验 → FAIL 明细列表（空=过）。"""
    issues: list[str] = []
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — 登记态 fail-closed
        return [f"keywords: 文件不可读/不可解析: {exc}"]
    if not isinstance(raw, dict):
        return ["keywords: 顶层必须是映射"]
    stems = raw.get("stems")
    if not isinstance(stems, list) or not stems:
        return ["keywords: 缺非空 stems 列表"]
    declared = raw.get("stem_count")
    if isinstance(declared, bool) or not isinstance(declared, int) or declared != len(stems):
        issues.append(f"keywords: stem_count 计数漂移（声明 {declared!r}，实际 {len(stems)}）")
    flags = raw.get("flags")
    if flags not in SUPPORTED_FLAGS:
        issues.append(f"keywords: flags 仅支持 {SUPPORTED_FLAGS}（现 {flags!r}）")
    for i, s in enumerate(stems, 1):
        if not isinstance(s, str) or not s.strip():
            issues.append(f"stems[{i}]: 非非空字符串")
            continue
        try:
            re.compile(s)
        except re.error as exc:
            issues.append(f"stems[{i}]: 正则不可编译（{s!r}: {exc}）")
            continue
        if _looks_redos(s):
            issues.append(f"stems[{i}]: 疑似灾难性回溯（嵌套量词，ReDoS）禁入词表: {s!r}")
    return issues


def validate(registry_dir: Path) -> list[str]:
    """两注册表全量校验 → FAIL 明细汇总（空=全绿）。"""
    issues: list[str] = []
    src = registry_dir / "intel_sources.yaml"
    if not src.exists():
        issues.append(f"sources: 文件缺失（{src}）")
    else:
        issues += _check_sources(src)
    kw = registry_dir / "intel_keywords.yaml"
    if not kw.exists():
        issues.append(f"keywords: 文件缺失（{kw}）")
    else:
        issues += _check_keywords(kw)
    return issues


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="intel 源注册表+关键词词表校验器（班前自检/pre-commit）")
    ap.add_argument("--registry-dir", type=str, default=None,
                    help="注册表目录（默认 <repo>/config；测试用）")
    args = ap.parse_args(argv)
    root = Path(args.registry_dir) if args.registry_dir else Path(__file__).resolve().parents[2] / "config"
    issues = validate(root)
    if issues:
        print(f"FAIL: intel 注册表校验不过（{len(issues)} 项）:")
        for it in issues:
            print(f"  - {it}")
        return 1
    print(f"OK: intel 注册表校验全绿（{root}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
