# [BLUEPRINT] MOD-METAQ-WO-A2LEGS-W4 | docs/_working/meta_question_answers/01_phase2_plan.md §数据施工需求清单(PQ-0080)
# [MODULE] scripts.governance.meta_question.wo_a2legs.prepare_io_2018
# [DOMAIN] D_DATA
# [DEPENDENCIES] scripts/industry_graph/io_ingest.py（在册装载器，本件 import 复用其 parse 逻辑不另造）;
#                 pyreadr; GitHub raw（ionet 学术包转存官方表，与 year=2020 同一在册渠道）
# [CONSUMERS] 产物册 data/registers/metaq_io_2018/（2018 矩阵 JSON + 部门对齐册 + 误差界取证）
#             → 待落地：由 PG 单写者执行 io_ingest.py load --matrix io_2018_153.matrix.json
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 零 PG 写（本工单 PG 通道=只读；落库交总包单写者，本件只出可执行落地指令）；
#              复用在册 parse 的 sanity 硬校验（列中间流量和≈TII ±0.1%，违和即拒出）；
#              取证数字全部来自官方表本体计算，禁以估算冒充；
#              下载文件带 sha256 溯源入册。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 下载失败/parse 非零退出→本件非零退出并打印原因（fail-visible，不出半成品册）。
# [TESTS] 无（数据施工脚本，验收=册内 sanity/对齐统计可复核）
# [A_module] module_id=MOD-METAQ-WO-A2LEGS-W4 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""国家统计局 2018 版投入产出表（153 部门）取得+解析+2020 版对齐取证（PQ-0080 前置）。

用法：python scripts/governance/meta_question/wo_a2legs/prepare_io_2018.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import urllib.request
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_ROOT / "src"))

OUT = _ROOT / "data" / "registers" / "metaq_io_2018"
REPO = "Carol-seven/ionet"
SUBDIR = "data"
FILES = ["china_2018_153.rda", "china_2020_153.rda"]


def _load_ingest():
    spec = importlib.util.spec_from_file_location(
        "io_ingest_reuse", _ROOT / "scripts" / "industry_graph" / "io_ingest.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "zephyr-metaq-a2legs", "Accept": "application/octet-stream"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 — 域名白名单常量
        return r.read()


def _fetch(name: str) -> Path:
    """多通道取官方表文件（在册渠道=ionet GitHub 转存）：raw → jsDelivr → GitHub API base64。

    本机网络实测 raw.githubusercontent 大文件读超时/RemoteDisconnected，故必须多通道退避；
    三条通道同源（同一 repo 同一 commit 的文件内容），以 sha256 记录供跨通道一致性核对。
    """
    dest = OUT / name
    OUT.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 10_000:
        return dest
    import base64

    urls = [
        f"https://raw.githubusercontent.com/{REPO}/master/{SUBDIR}/{name}",
        f"https://cdn.jsdelivr.net/gh/{REPO}@master/{SUBDIR}/{name}",
    ]
    last: Exception | None = None
    for url in urls:
        try:
            dest.write_bytes(_get(url))
            if dest.stat().st_size > 10_000:
                return dest
        except Exception as exc:  # noqa: BLE001 — 通道级退避，逐条试
            last = exc
    try:
        api = f"https://api.github.com/repos/{REPO}/contents/{SUBDIR}/{name}?ref=master"
        payload = json.loads(_get(api).decode("utf-8"))
        dest.write_bytes(base64.b64decode(payload["content"]))
        if dest.stat().st_size > 10_000:
            return dest
    except Exception as exc:  # noqa: BLE001
        last = exc
    raise RuntimeError(f"三通道均失败 {name}: {type(last).__name__}: {str(last)[:150]}")


def _sectors(payload: dict) -> dict[str, dict]:
    return {s["code"]: s for s in payload["sectors"]}


def _coeff(payload: dict) -> dict[tuple[str, str], float]:
    return {(e["from"], e["to"]): float(e["coefficient"]) for e in payload["edges"]}


def _error_bound(p18: dict, p20: dict, common: list[str]) -> dict:
    """2018→2020 同部门码边的相对差分布（外推误差界取证，数字全部由官方表本体计算，禁估算冒充）。"""
    c18, c20 = _coeff(p18), _coeff(p20)
    keys = [(f, t) for f in common for t in common]
    both = [(k, c18[k], c20[k]) for k in keys if k in c18 and k in c20]
    rel = [abs(a - b) / abs(b) for (_, a, b) in both if b != 0]
    rel.sort()
    n = len(rel)
    return {
        "compared_pairs_both_nonzero": n,
        "max_rel_diff": round(rel[-1], 6) if n else None,
        "p99_rel_diff": round(rel[int(n * 0.99) - 1], 6) if n else None,
        "p95_rel_diff": round(rel[int(n * 0.95) - 1], 6) if n else None,
        "median_rel_diff": round(rel[n // 2], 6) if n else None,
        "mean_rel_diff": round(sum(rel) / n, 6) if n else None,
        "share_over_30pct": round(sum(1 for x in rel if x > 0.30) / n, 6) if n else None,
        "threshold_verdict_preview": (
            "≤30% 界内（按全边最大相对差）" if n and rel[-1] <= 0.30 else "超 30%（按全边最大相对差；判据口径见 notes）"
        ),
    }


def main() -> int:
    ingest = _load_ingest()
    mats: dict[int, dict] = {}
    provenance = {}
    for name in FILES:
        rda = _fetch(name)
        sha = hashlib.sha256(rda.read_bytes()).hexdigest()
        matrix = rda.with_name(rda.stem + ".matrix.json")
        rc = ingest.cmd_parse(str(rda), str(matrix))
        if rc != 0:
            print(f"[FAIL] parse rc={rc} for {name}")
            return 3
        mats[int(name.split("_")[1])] = json.loads(matrix.read_text(encoding="utf-8"))
        provenance[name] = {
            "sha256": sha,
            "bytes": rda.stat().st_size,
            "url_channel": "github:" + REPO + ":" + SUBDIR + "/" + name,
            "matrix": str(matrix),
        }

    p18, p20 = mats[2018], mats[2020]
    s18, s20 = _sectors(p18), _sectors(p20)
    common = sorted(set(s18) & set(s20))
    only18 = sorted(set(s18) - set(s20))
    only20 = sorted(set(s20) - set(s18))
    name_diff = [(c, s18[c]["cn"], s20[c]["cn"]) for c in common if s18[c]["cn"] != s20[c]["cn"]]

    err = _error_bound(p18, p20, common)
    agg_only18 = sum(1 for c in only18)
    report = {
        "meta": {
            "title": "metaq_io_2018 — 2018 版投入产出表（153 部门）取得与 2020 版对齐取证",
            "work_order": "WO-A2LEGS",
            "session": "st-metaq-gc-20260924",
            "purpose": "PQ-0080 前置：2018 版机读全表取得 + 部门口径对齐 + 外推误差界取证",
            "channel": "ionet 学术包转存官方《中国投入产出表》（与库内 year=2020 同一在册渠道，"
            "见 scripts/industry_graph/io_ingest.py 头注 [数据来源]）",
            "provenance": provenance,
            "landing_pending": {
                "reason": "本工单 PG 通道=只读（数据访问通道明令），落库须由 PG 单写者执行",
                "command": "python scripts/industry_graph/io_ingest.py load --matrix "
                + str((OUT / "china_2018_153.matrix.json").relative_to(_ROOT)),
                "caveat": "io_ingest.cmd_load 的 valid_from 硬编码 '2022-08-31'（2020 版发布时点），"
                "装载 2018 版须按年参数化，否则 PIT 可知时戳错标——落地前须先修该常量"
                "（本件不改 src/scripts 既有文件，登记为待落地补丁建议）",
            },
            "root_cause_note": "库内缺 2018 版的机制原因：io_ingest.cmd_check/_targets_new 只取"
            " year>max(库内年) 的'更新'表，2018<2020 被永久跳过；"
            "补齐须显式 cmd_fetch --year 2018（本件即走显式取表）",
        },
        "alignment": {
            "sectors_2018": len(s18),
            "sectors_2020": len(s20),
            "code_common": len(common),
            "code_only_2018": only18,
            "code_only_2020": only20,
            "code_only_2018_names": [s18[c]["cn"] for c in only18],
            "code_only_2020_names": [s20[c]["cn"] for c in only20],
            "same_code_renamed": name_diff[:60],
            "same_code_renamed_count": len(name_diff),
            "note": "对齐键=3 位部门码（官方表本体码）；码同名异=分类口径微调，"
            "异码=部门拆并，两侧差集如实列出，不做拍脑袋映射",
        },
        "extrapolation_error_bound": err,
        "edges": {
            "edges_2018": len(p18["edges"]),
            "edges_2020": len(p20["edges"]),
            "sanity_2018": p18["sanity"],
            "sanity_2020": p20["sanity"],
        },
    }
    (OUT / "io_2018_alignment_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    # 待落地补丁：仅含 2018 版 edges 的精简矩阵（load 用，路径与在册 loader 约定一致）
    print(
        json.dumps(
            {
                "written": str(OUT / "io_2018_alignment_report.json"),
                "edges_2018": len(p18["edges"]),
                "code_common": len(common),
                "only_2018": len(only18),
                "only_2020": len(only20),
                "renamed": len(name_diff),
                "error_bound": err,
            },
            ensure_ascii=False,
            indent=1,
        )
    )
    print(f"[NOTE] only_2018={agg_only18}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
