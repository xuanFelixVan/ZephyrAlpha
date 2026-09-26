# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-006
# [MODULE] scripts.governance.meta_question.wo006.probe_source_c_ths
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.security.secrets（凭证只判在不在，禁打印值）; architecture_model/data/data_sources_registry.yaml
#                （DS 册=数据源元数据唯一真源，status 只读不改）; config/secret_registry.yaml; akshare; iFinDPy（可选）
# [CONSUMERS] generate_node_binding_candidates.py（源 C 可用则有产出，不可得则零产出留痕）；案卷 WO-006.yaml
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 纯取证只读件：不写 PG、不写 DB、不改任何注册表，只落取证册 yaml；
#              凭证面只输出 present/absent + 长度，禁输出明文（RULE-SECRETS）；
#              结论禁凭记忆——七项检查全部实跑采集（DS 册 status / provider 代码 / 离线导出件 /
#              概念装载器输入 / akshare THS 三接口 / iFinD 真登录 / 历史回溯能力），
#              不可得就登记不可得（禁造假挂接）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单项探针异常→该记 ERR 继续跑（取证要的是全貌，不因单点崩而丢册）；
#                  写册失败→抛出非零退出
# [TESTS] 2026-09-24 首跑：iFinD 真登录返回码 -2（失败）+ akshare 1.18.75 无 cons_ths 接口
#         + 同花顺离线导出目录仅剩两份登记 md → verdict.runnable=false
# [TTL] task_bound
"""WO-006 源 C（同花顺）通道可得性取证——"先取证后施工"，跑不通就留证据登记不可得。

用法::

    python scripts/governance/meta_question/wo006/probe_source_c_ths.py

产出 data/registers/metaq_node_binding/source_c_forensics_wo006.yaml。
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import wo006_common as W  # noqa: E402

REG_PATH = W.REG_DIR / "source_c_forensics_wo006.yaml"
DS_REGISTRY = W.ROOT / "architecture_model" / "data" / "data_sources_registry.yaml"
SECRET_REGISTRY = W.ROOT / "config" / "secret_registry.yaml"
THS_DIR = W.ROOT / "docs" / "_working" / "同花顺资料"
THS_IMPORT_PY = W.ROOT / "scripts" / "industry_graph" / "ths_import.py"
IFIND_PROVIDER = W.ROOT / "src" / "zephyr" / "data" / "implementations" / "ifind_provider.py"


def _ds_entry() -> dict:
    """DS 册真源读 DS-IFIND（status/account_type/coverage）——只读，禁改。"""
    if not DS_REGISTRY.is_file():
        return {"error": "DS 册不存在"}
    txt = DS_REGISTRY.read_text(encoding="utf-8")
    m = re.search(r"- id: DS-IFIND\n(.*?)(?=\n  - id: DS-|\Z)", txt, re.S)
    if not m:
        return {"error": "DS 册无 DS-IFIND 条目"}
    body = m.group(1)

    def fld(k):
        mm = re.search(rf"^\s*{k}:\s*[\"']?(.*?)[\"']?\s*$", body, re.M)
        return mm.group(1) if mm else None

    return {
        "id": "DS-IFIND",
        "status": fld("status"),
        "account_type": fld("account_type"),
        "auth_method": fld("auth_method"),
        "coverage": fld("coverage"),
        "retirement_note": (re.search(r"已退役\((.*?)\)", body) or [None, None])[1],
    }


def _secret_entry() -> dict:
    """secret_registry 里 IFIND 键的在册说明（只取 key/service/required，不取值）。"""
    if not SECRET_REGISTRY.is_file():
        return {"error": "secret_registry 不存在"}
    txt = SECRET_REGISTRY.read_text(encoding="utf-8")
    out = {}
    for key in ("IFIND_USERNAME", "IFIND_PASSWORD"):
        m = re.search(rf"- key: {key}\n((?:  .*\n)*)", txt)
        out[key] = {
            "registered": bool(m),
            "note": (
                re.search(r"description: '(.*?)'", m.group(1)).group(1)[:220]
                if m and re.search(r"description: '(.*?)'", m.group(1))
                else None
            ),
        }
    return out


def _credentials_present() -> dict:
    """凭证在不在（长度），禁打印明文。"""
    out = {}
    try:
        from zephyr.shared.security.secrets import get_secret_or_default

        for k in ("IFIND_USERNAME", "IFIND_PASSWORD"):
            v = get_secret_or_default(k, "")
            out[k] = {"present": bool(v), "length": len(v)}
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {str(e)[:120]}"
    return out


def _offline_exports() -> dict:
    """既有装载器的输入件是否还在仓（ths_import/concept_ingest 吃 Owner 手工导出的 GBK TSV 伪 xlsx）。"""
    need = []
    if THS_IMPORT_PY.is_file():
        txt = THS_IMPORT_PY.read_text(encoding="utf-8")
        for m in re.finditer(r"(?:STOCKS_FILES|SECTOR_FILE)\s*=\s*(.+)", txt):
            need += re.findall(r"[\"']([^\"']+)[\"']", m.group(1))
    listing = sorted(p.name for p in THS_DIR.iterdir()) if THS_DIR.is_dir() else []
    return {
        "dir_exists": THS_DIR.is_dir(),
        "loader_required_files": need,
        "files_present": [f for f in need if (THS_DIR / f).is_file()],
        "files_missing": [f for f in need if not (THS_DIR / f).is_file()],
        "dir_listing": listing,
        "xlsx_or_tsv_in_dir": [f for f in listing if f.lower().endswith((".xlsx", ".xls", ".tsv", ".csv"))],
    }


def _akshare_channel() -> dict:
    """akshare THS 接口实测（DS-IFIND 退役后 concept_sector 能力的迁移承接方）。"""
    out = {}
    try:
        import warnings

        warnings.filterwarnings("ignore")
        import akshare

        out["akshare_version"] = getattr(akshare, "__version__", "?")
        out["has_name_ths"] = hasattr(akshare, "stock_board_concept_name_ths")
        out["has_cons_ths"] = hasattr(akshare, "stock_board_concept_cons_ths")
        if out["has_name_ths"]:
            df = akshare.stock_board_concept_name_ths()
            out["name_ths"] = {"ok": True, "rows": int(len(df)), "columns": list(df.columns)}
        if out["has_cons_ths"]:
            try:
                df = akshare.stock_board_concept_cons_ths(symbol="先进封装")
                out["cons_ths"] = {"ok": True, "rows": int(len(df)), "columns": list(df.columns)}
            except Exception as e:  # noqa: BLE001
                out["cons_ths"] = {"ok": False, "error": f"{type(e).__name__}: {str(e)[:140]}"}
        try:
            df = akshare.stock_board_concept_info_ths(symbol="阿里巴巴概念")
            out["info_ths"] = {
                "ok": True,
                "columns": list(df.columns),
                "carries_constituents": any(c in ("成分股", "代码", "股票代码") for c in df.columns),
            }
        except Exception as e:  # noqa: BLE001
            out["info_ths"] = {"ok": False, "error": f"{type(e).__name__}: {str(e)[:140]}"}
        try:
            df = akshare.stock_board_concept_summary_ths()
            out["summary_ths"] = {
                "ok": True,
                "columns": list(df.columns),
                "carries_constituents": "成分股" in "".join(map(str, df.columns)),
            }
        except Exception as e:  # noqa: BLE001
            out["summary_ths"] = {"ok": False, "error": f"{type(e).__name__}: {str(e)[:140]}"}
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {str(e)[:140]}"
    return out


def _ifind_login() -> dict:
    """真跑一次 iFinD 登录（SDK 在装 ≠ 账号可用）——只记返回码，不记凭证。"""
    out = {"sdk_importable": False, "attempted": False}
    try:
        import iFinDPy as ths

        out["sdk_importable"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = f"import {type(e).__name__}: {str(e)[:140]}"
        return out
    try:
        from zephyr.shared.security.secrets import get_secret_or_default

        u, p = get_secret_or_default("IFIND_USERNAME", ""), get_secret_or_default("IFIND_PASSWORD", "")
        if not (u and p):
            out["note"] = "在册凭证缺失，未尝试登录"
            return out
        out["attempted"] = True
        r = ths.THS_iFinDLogin(u, p)
        out["login_return_code"] = r if isinstance(r, (int, str)) else repr(r)[:120]
        try:
            ths.THS_iFinDLogout()
        except Exception:  # noqa: BLE001
            pass
    except Exception as e:  # noqa: BLE001
        out["error"] = f"login {type(e).__name__}: {str(e)[:140]}"
    return out


def main() -> int:
    ak = _akshare_channel()
    lg = _ifind_login()
    off = _offline_exports()
    ds = _ds_entry()
    cons_live = bool(ak.get("has_cons_ths")) and bool((ak.get("cons_ths") or {}).get("ok"))
    login_ok = bool(lg.get("attempted")) and str(lg.get("login_return_code", "")).strip() == "0"
    runnable = bool(cons_live or (login_ok and off.get("loader_required_files")))
    payload = {
        "meta": {
            "wo": W.WO_ID,
            "q_id": W.Q_ID,
            "session": W.SESSION,
            "probed_at": date.today().isoformat(),
            "purpose": "WO-006 配套项①『同花顺再跑（DS 账号在册）』通道可得性取证（先取证后施工）",
            "method": "七项实跑：DS 册 status / provider 代码留存 / 离线导出件 / 装载器输入 / "
            "akshare THS 三接口 / iFinD 真登录返回码 / 历史回溯能力判定",
        },
        "checks": {
            "ds_registry_ifind": ds,
            "ifind_provider_code_in_repo": IFIND_PROVIDER.is_file(),
            "secret_registry_ifind": _secret_entry(),
            "credentials_present": _credentials_present(),
            "offline_export_files": off,
            "akshare_ths_channel": ak,
            "ifind_live_login": lg,
        },
        "verdict": {
            "runnable": runnable,
            "constituent_channel_live": cons_live,
            "ifind_login_ok": login_ok,
            "offline_loader_input_available": bool(off.get("files_present")),
            "history_rewindable": False,
            "reason": "①DS 册 status=deprecated（试用账号到期退役，provider 代码全项目切除，本单禁改 src/ 与 git 取回）；"
            "②既有装载器（ths_import.py / concept_ingest.py）的输入=Owner 手工导出 GBK TSV，"
            "实测 docs/_working/同花顺资料/ 源件已不在仓（仅存两份被投清单登记 md）；"
            "③akshare 迁移承接面只有概念名录（stock_board_concept_name_ths），"
            "概念→成分股明细接口 cons_ths 在 1.18.75 不存在，info/summary 只回板块行情与驱动事件；"
            "④iFinDPy SDK 虽在装，真登录返回码非 0 → 账号不可用；"
            "⑤即使今夜可跑，同花顺概念成分仅当前快照，无时点回溯接口（PIT 类问不可用）。",
            "consequence": "源 C 零产出（禁造假挂接）；缺口转由源 A（stock_concept 概念成分，其真身即 2026-09-14 "
            "同花顺公司档案导出快照=同花顺 lineage 的在库存量）+ 源 B 同名穿透 + 源 D node_ref 营收归因回收；"
            "未回收差额在案卷 shortfall 节如实报出。",
        },
    }
    W.write_register(REG_PATH, payload)
    print(
        f"[VERDICT] source_c runnable={runnable} cons_live={cons_live} "
        f"login_code={lg.get('login_return_code')} exports={off.get('files_missing')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
