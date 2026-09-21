# [BLUEPRINT] MOD-GOV_SCRIPTS-001 | docs/03_modules/_domain_governance/blueprint.md | 标准族注册表生成器
# [MODULE] scripts.governance.standards_governance.generate_standard_family_registry
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.io.file_utils (content_sha256, safe_write_text); yaml
# [CONSUMERS] 人工/派生批调用（docs/01_policies_and_standards/_registry/catalogs/standard_family_registry.yaml 唯一写者）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 输出幂等（相同输入→相同输出，时间戳不入面）; 只读真源; 计数一律现算写入（宪法 §4.3 禁散文写死）; 族名合法性以 governance_family_vocabulary.yaml 为唯一判据（VOCAB-HARDCODE 同源）
# [MODIFY-GUARD] 修改需通过任务卡
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源缺失→stderr 报错并 exit 1（禁静默产出空册冒充"已建"；路径经异常 details 通道，不入消息面）; 族名非法→记 illegal_family 并不阻断（如实呈现）
# [TESTS] tests/governance/standards_governance/test_generate_standard_family_registry.py
# [A_module] module_id=MOD-GOV_SCRIPTS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 派生自动册再生 CLI（--check 是对账只读腿、写盘是 CAS 再生腿），manual 触发即设计语义；周期再生归排班/对账事件腿，不在本件内建 sleep/Timer（宪法 §9.3 铁律）
"""G-std-family-registry: 标准↔治理族派生注册表生成器（派生自动档，归 #307 口径）。

治本对象 = 全流通战役 lane-J 立案 req_tdchainJ_02（#306 红队条款①的可执行判据载体）：
"红队条款有没有落地"此前只能靠人读散文判断；本生成器把它变成一张**可机检的册**——
每条 STD-* 的族归属、状态、历史被毙次数与判据出处都在册，缺哪项就显式记缺，
禁手工维护（宪法 §9.5）、禁散文写死计数（宪法 §4.3）。

三要素（按 R-011 定案执行）：
  ① 生成器落 `scripts/governance/standards_governance/` 子包（ARCH-031：governance 根禁新增 .py）
  ② 条目来源 = `config/standards.yaml` 全部 STD-*（解析 std_id/status/version/frozen_at）
     + `_registry/vocabularies/governance_family_vocabulary.yaml`（族名合法性 A/B/C/D）
     + 历史被毙/重考证据 = `ruling_registry.yaml` 对本册 STD-* 的提及计数（reexam_evidence/N_eff 口径）
  ③ 计数字段 `total_families` / `total_standards` 由本生成器写入，散文引用一律用字段

诚实条款：`config/standards.yaml` 现无逐条 `family` 字段（实测 4 条 STD-* 全无族声明），
故本册**不臆造族归属**——族未声明者记 `family: null` + `family_source: undeclared`，
并计入 `family_unassigned`。"有判据"与"有数据"是两件事：本册先把判据立起来，
缺的输入以缺口形式在册可见（比编一个族名更接近目的）。

用法
----
    python scripts/governance/standards_governance/generate_standard_family_registry.py [--check]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

_GOV_DIR = next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists())
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

import yaml  # noqa: E402
from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # noqa: E402

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT

STD_SOURCE: Final[Path] = REPO_ROOT / "config" / "standards.yaml"
VOCAB_SOURCE: Final[Path] = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "vocabularies"
    / "governance_family_vocabulary.yaml"
)
RULINGS_SOURCE: Final[Path] = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "ruling_registry.yaml"
)
OUTPUT: Final[Path] = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "standard_family_registry.yaml"
)

GENERATOR_PATH: Final[str] = "scripts/governance/standards_governance/generate_standard_family_registry.py"
# 被毙/重考证据的机检词族（ruling_registry 正文里对某条标准的否决、打回、重考表述）
REJECTED_PATTERNS: Final[tuple[str, ...]] = ("否决", "打回", "驳回", "毙", "reexam", "重考", "作废")
HEADER_TMPL: Final = (
    "# [A_registry] registry_id=REG-STD-FAMILY-001 | tier=tier_1_governance | "
    "maintenance=auto（{gen}）\n"
    "# 本文件是**派生自动册**：唯一写者=上述生成器，手工编辑会在下次再生时被覆盖\n"
    "# （宪法 §9.5 静态清单禁手工维护 / §4.3 计数用字段不写死在散文）。\n"
)


def _rel_posix(doc_ref: Path) -> str:
    """仓内相对路径（正斜杠）——派生册 derived_from 字段的唯一口径。

    不写死字面量：路径真源=上面的 REPO_ROOT 锚定常量（VOCAB-CHAIN 口径：
    SSoT 路径经常量反查，不散落字符串）。
    """
    return doc_ref.relative_to(REPO_ROOT).as_posix()


def _with_location(exc: Exception, doc_ref: Path) -> Exception:
    """把定位信息挂到异常 details 通道（MSG-EXPOSURE 口径：路径不入消息文本）。"""
    exc.details = {"path": str(doc_ref)}  # type: ignore[attr-defined]
    return exc


def _load_yaml(doc_ref: Path) -> dict:
    """读 YAML（真源缺失即抛错，禁降级成空册冒充"已建"）。

    异常消息只说"哪个真源坏了"，具体路径经 details 通道由 main() 打 stderr。
    """
    if not doc_ref.is_file():
        raise _with_location(FileNotFoundError("真源缺失，无法派生标准族册"), doc_ref)
    data = yaml.safe_load(doc_ref.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise _with_location(ValueError("真源结构非 mapping，拒绝派生"), doc_ref)
    return data


def _legal_families(vocab: dict) -> list[str]:
    """从 governance_family 受控词表取合法族名（与 VOCAB-HARDCODE 同一真源，不复制字面量）。"""
    values = vocab.get("values") or []
    return [str(v.get("value")) for v in values if isinstance(v, dict) and v.get("value")]


def _ruling_text(rulings: dict) -> str:
    """把裁定登记册摊平成文本（用于逐条标准的被毙/重考提及计数）。"""
    entries = rulings.get("entries") or []
    return "\n".join(yaml.safe_dump(entries, allow_unicode=True, sort_keys=False).splitlines())


def _count_mentions(text: str, std_id: str) -> dict[str, int]:
    """统计某条标准在裁定册中的提及数与否决/重考证据数（#306 红队条款①的"历史被毙次数"口径）。"""
    hits = [ln for ln in text.splitlines() if std_id in ln]
    rejected = sum(1 for ln in hits for kw in REJECTED_PATTERNS if kw in ln)
    return {"cited_in_rulings": len(hits), "reexam_or_rejected_evidence": rejected}


def build_registry() -> dict:
    """派生 standard_family_registry 内容（纯函数，不写盘——供 --check 与测试复用）。

    :return: 顶层含 total_standards / total_families 等**现算**计数字段的册 dict
    """
    std_doc = _load_yaml(STD_SOURCE)
    vocab = _load_yaml(VOCAB_SOURCE)
    rulings = _load_yaml(RULINGS_SOURCE)
    legal = _legal_families(vocab)
    text = _ruling_text(rulings)

    entries: list[dict] = []
    for item in std_doc.get("standards") or []:
        std_id = str(item.get("std_id") or "")
        if not std_id:
            continue
        fam = item.get("family")
        declared = str(fam) if fam else None
        entries.append(
            {
                "std_id": std_id,
                "name_zh": item.get("name_zh"),
                "version": item.get("version"),
                "status": item.get("status"),
                "frozen_at": item.get("frozen_at"),
                "family": declared,
                "family_source": "declared_in_standards_yaml" if declared else "undeclared",
                "family_legal": bool(declared) and declared in legal,
                **_count_mentions(text, std_id),
                "source_of_truth": "config/standards.yaml",
            }
        )
    used = sorted({str(e["family"]) for e in entries if e.get("family")})
    unassigned = sorted(e["std_id"] for e in entries if not e.get("family"))
    return {
        "registry_id": "REG-STD-FAMILY-001",
        "name": "标准↔治理族派生注册表",
        "tier": "tier_1_governance",
        "format": "yaml",
        "maintenance": "auto",
        "generated_by": GENERATOR_PATH,
        "derived_from": [_rel_posix(STD_SOURCE), _rel_posix(VOCAB_SOURCE), _rel_posix(RULINGS_SOURCE)],
        "counting_rule": "entries 条目数 = config/standards.yaml 中带 std_id 的条目数（生成器现算）",
        # —— 计数字段（宪法 §4.3：散文引用一律用这些字段，禁手写数字）——
        "total_standards": len(entries),
        "total_families": len(legal),
        "families_declared": len(used),
        "family_unassigned": len(unassigned),
        "illegal_family_entries": sorted(e["std_id"] for e in entries if e.get("family") and not e["family_legal"]),
        "family_unassigned_std_ids": unassigned,
        "legal_family_values_from_vocabulary": legal,
        "status_distribution": _dist(entries, "status"),
        "entries": entries,
        "honest_gap_note": (
            "family_unassigned>0 表示 config/standards.yaml 尚无逐条族声明字段——本册不臆造归属，"
            "缺口以计数形式在册可见；补齐输入=在 standards.yaml 每条 STD-* 增 family: A|B|C|D"
            "（合法域来自 governance_family_vocabulary.yaml），再生成本册即归零。"
        ),
    }


def _dist(entries: list[dict], key: str) -> dict[str, int]:
    """按某字段做计数分布（生成器现算，供散文引用字段）。"""
    out: dict[str, int] = {}
    for e in entries:
        k = str(e.get(key) or "<none>")
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items(), key=lambda x: (-x[1], x[0])))


def render(reg: dict) -> str:
    """把册渲染为 YAML 文本（头部声明唯一写者 + 幂等：不含时间戳）。"""
    body = yaml.safe_dump(reg, allow_unicode=True, sort_keys=False, default_flow_style=False, width=110)
    return HEADER_TMPL.format(gen=GENERATOR_PATH) + body


def check_freshness(text: str) -> bool:
    """盘上字节与再生字节是否一致（--check 用；不一致=派生册漂移）。"""
    return OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == text


def main() -> int:
    """入口：--check 只判漂移（不写盘），默认写盘（CAS 热文件口径）。"""
    parser = argparse.ArgumentParser(description="生成 standard_family_registry.yaml（派生自动册）")
    parser.add_argument("--check", action="store_true", help="只校验盘上派生册是否漂移，不写文件")
    parser.add_argument("--output", default=str(OUTPUT), help="输出路径（默认标准位置）")
    args = parser.parse_args()
    try:
        text = render(build_registry())
    except (FileNotFoundError, ValueError) as exc:
        # 定位信息走 details 通道（异常消息面不留路径）——运维侧仍能在 stderr 看到缺哪个真源
        details = getattr(exc, "details", None)
        suffix = f" [{details.get('path')}]" if isinstance(details, dict) and details.get("path") else ""
        print(f"ERROR: {exc}{suffix}", file=sys.stderr)
        return EXIT_FINDINGS
    out_path = Path(args.output)
    if args.check:
        stale = not check_freshness(text)
        print(f"{'STALE' if stale else 'FRESH'} {out_path.name}")
        return EXIT_FINDINGS if stale else EXIT_PASS
    base = out_path.read_text(encoding="utf-8") if out_path.is_file() else ""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    res = safe_write_text(out_path, text, expected_base_sha256=content_sha256(base) if base else None, newline="\n")
    reg = yaml.safe_load(text) or {}
    print(
        f"written={res.written} total_standards={reg.get('total_standards')} "
        f"total_families={reg.get('total_families')} family_unassigned={reg.get('family_unassigned')}"
    )
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
