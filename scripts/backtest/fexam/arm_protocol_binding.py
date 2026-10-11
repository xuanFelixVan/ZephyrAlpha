# [BLUEPRINT] MOD-BT-249 | docs/03_modules/_domain_backtest/blueprint.md | §臂协议绑定层（对照/消融双臂敞口变换）
# [MODULE] scripts.backtest.fexam.arm_protocol_binding
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; stdlib(re/pathlib/sys/typing); yaml;
#   scripts/backtest/fexam/card_binding（仅数据面同名单：底座序列由绑定册算子产出，本件不重实现取数）;
#   zephyr.data.table_registry.get_registry（表名唯一真源，本件代码零表名字面量）
# [CONSUMERS] 矿考循环班 W-A 车道（臂协议试点批：总包用 build_arms 产双臂后交 calibration_exam.run_card 出分）;
#   tests/backtest/test_arm_protocol_binding.py；docs/_working/mineloop_campaign/W-A_arm_pilot_spec.yaml（分箱与接线方案数据面）
# [STARTUP] manual
# [MATURITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] 本件只管"卡面 arm_protocol → 两臂日频敞口序列"，不取数不判分不改册——
#   底座序列由调用方（总包）经绑定册算子传入，本件只做敞口变换；
#   每个臂算子必须带卡面 arm_protocol 原文引句，引句在该卡文本中找不到即 ArmQuoteNotFound 拒绑（反自造口径，
#   与 card_binding.run_binding_book 的 prose_quote 双校验同思路，但校验面是臂协议段）；
#   臂参数无冻结数值（如"前档权重"未给数）= ArmParamUnfrozen / triage 态 unfrozen_arm_definition，禁替卡拍数值；
#   判据面（window/buckets/pillars/pillars_numeric/target/signal_kind）本件零读零写零裁量——分箱只读臂协议文本面；
#   triage_card 三态判据全部来自卡面文本模式，禁 card_id 白名单硬分箱（可复算、可审计）；
#   代码内禁表名字面量（TABLE-NAME-REGISTRY 门），表名一律 get_registry() 解析或由数据册 args 携带。
# [MODIFY-GUARD] ARM_OPS 增删算子必须同步 tests/backtest/test_arm_protocol_binding.py 的引句拒绑与未知算子用例
# [STABILITY] experimental
# [ERROR_CONTRACT] ArmOpUnknown: 算子名不在 ARM_OPS 册；ArmQuoteNotFound: 引句不在该卡臂协议文本（拒绑）；
#   ArmParamUnfrozen: 臂参数缺冻结数值（拒变换，须先补卡面）；ArmBaseMissing: 底座序列未注入（禁近似）；
#   卡无臂协议面 → triage_card 不抛，state=needs_matching_engine + reason=no_arm_protocol_face（计入普查）
# [TESTS] tests/backtest/test_arm_protocol_binding.py
# [A_module] module_id=MOD-BT-249 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  人工 CLI 分箱/接线驱动器（按需触发），非常驻自动系统
# create-guard-not-dup: 本件是"卡面 arm_protocol → 双臂日频敞口序列"的唯一算子册与分箱器，
#   不是 card_binding（MOD-BT-248）的第二实现——card_binding 管"单臂 data_binding → 一条序列"，
#   本件管"同一底座 → 两条敞口"，消费面是臂协议段（arm_protocol/paired_arm_protocol），绑定册不覆盖该段；
#   亦非 calibration_exam（MOD-BT-243）_arm_nav_metrics 的第二实现：本件不回放 NAV、不算 sharpe/maxdd，
#   只产出喂给 run_card(signal=, signal_b=) 的两条敞口，判据与配对差全由执行核负责（零裁量面不搬）。
"""arm_protocol_binding — 臂协议→双臂敞口绑定层（MOD-BT-249，矿考循环班 W-A 车道主交付）。

背景：`calibration_exam.run_card` 的 comparison/ablation 分支要求 `signal`/`signal_b` **两臂序列**，
`_comparison_metrics` 里每臂各走 `_series_metrics`（IC 面）＋ `_arm_nav_metrics`（t 敞口 × t+1 目标 NAV 回放
＋换手扣费），配对差 maxdd_improvement_pp / sharpe_delta / turnover_delta_annual_x 在核内部完成。
⇒ 只要卡面臂定义能写成"同一底座上的敞口变换 f(base)"，本件即可出双臂，**无需另建重放引擎**；
只有臂本身要求重新撮合（逐笔成交价/分批/排队顺序/持仓状态机）的卡才真缺件。

三态分箱（机判，凭据=命中的卡面原文片段）：
  feasible_now            臂=日频标量敞口变换（置常数 / 档 cap 乘子 / 条件门 / 取子集），且臂参数已给数值
  unfrozen_arm_definition 臂变换形状可表达，但卡面未给数值（禁替卡拍数）
  needs_matching_engine   臂定义落在逐笔/横截面持仓路径面上，标量敞口变换表达不出
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

# ──────────────────────────────────────────────────────────────────────────────
# 异常面（ERROR_CONTRACT 对偶，调用方按类型分派，禁字符串匹配判因）
# ──────────────────────────────────────────────────────────────────────────────


class ArmBindingError(RuntimeError):
    """臂协议绑定层基类。"""


class ArmOpUnknown(ArmBindingError):
    """算子名不在 ARM_OPS 册（禁猜算子）。"""


class ArmQuoteNotFound(ArmBindingError):
    """引句不在该卡臂协议文本面 = 自造口径形态，拒绑（对齐 run_binding_book 双校验思路）。"""


class ArmParamUnfrozen(ArmBindingError):
    """臂参数缺冻结数值（如"降风险预算"未给数）——禁替卡拍数值，拒出敞口。"""


class ArmBaseMissing(ArmBindingError):
    """底座序列未注入——本件不取数，禁以近似序列冒充分母。"""


class ArmFaceMismatch(ArmBindingError):
    """e/r 两位语义错配（敞口位喂成收益/净值面，或反之）。

    为什么要有这道机械闸：判官 `_arm_nav_metrics` 把喂进来的臂序列当**敞口**（:236 原文
    `ret = df["e"].shift(0) * df["r"].shift(-1)`，t 敞口吃 t+1 收益）。若卡面语义是
    "池组合收益回放"而适配器把那条收益序列喂进 e 位，算出来是**收益×收益**——
    它不抛异常，只安静地出一个像模像样的假分。故量纲错必须在这里就红，不靠注释自觉。
    """


# ──────────────────────────────────────────────────────────────────────────────
# 卡面臂协议文本面（引句校验域 / 分箱判据域，两面分开）
# ──────────────────────────────────────────────────────────────────────────────

#: 臂定义面键名（卡面实测：data_binding.arm_protocol 为主键；paired_arm_protocol/frozen_note/buckets.on
#: 三处也定义臂——L2 族两张卡只在 frozen_note 散文里声明臂，无 arm_protocol 键）
_ARM_DEF_KEYS = ("arm_protocol", "paired_arm_protocol", "frozen_note", "on")
#: 出处面键名（底座序列与装置从哪来；这些键里出现 simulate(/分钟 属"底座 provenance"，
#: 不构成"臂要重新撮合"的证据——臂证据只看臂定义面）
_PROVENANCE_KEYS = (
    "device_ref",
    "implementation_gap",
    "signal_derivation",
    "target_source",
    "signal_table",
    "signal_column",
    "data_window_evidence",
    "primary",
    "executor",
    "blocked_scope",
    "impl_ref",
)


def _walk(node: Any, keynames: tuple[str, ...], depth: int = 0) -> list[str]:
    """递归收集指定键名的字符串值（卡面层级不一：顶层/window/pillars/buckets/data_binding）。"""
    if depth > 8 or isinstance(node, (str, int, float, bool)) or node is None:
        return []
    out: list[str] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if str(k) in keynames and isinstance(v, (str, int, float, bool)):
                out.append(str(v))
            elif isinstance(v, (dict, list)):
                out.extend(_walk(v, keynames, depth + 1))
    elif isinstance(node, list):
        for v in node:
            out.extend(_walk(v, keynames, depth + 1))
    return out


def arm_def_text(card: dict) -> str:
    """臂定义面原文（分箱判据域：只看"臂是什么"，不看"底座从哪来"）。"""
    return " | ".join(_walk(card, _ARM_DEF_KEYS))


def provenance_text(card: dict) -> str:
    """底座/装置出处面（供凭据说明底座如何取，不参与臂型判定）。"""
    return " | ".join(_walk(card, _PROVENANCE_KEYS))


def arm_blob(card: dict) -> str:
    """引句校验域＝臂定义面 ∪ 出处面（只读卡面对象，零改动）。"""
    return " | ".join([arm_def_text(card), provenance_text(card)])


def _squash(text: str) -> str:
    """空格归一（同 card_binding.run_binding_book 的 prose_quote 校验形，防排版空格误伤）。"""
    return str(text or "").replace(" ", "").replace("\u3000", "").replace("\n", "")


def verify_arm_quote(card: dict, quote: str, op: str) -> None:
    """引句必须逐字落在该卡臂协议面上；找不到即拒绑（反"我给自己发假绿"）。"""
    q = _squash(quote)
    if not q:
        raise ArmQuoteNotFound(f"arm_quote_empty:{op}")
    if q not in _squash(arm_blob(card)):
        raise ArmQuoteNotFound(f"arm_quote_not_found_on_card:{op}:{str(quote)[:40]}")


# ──────────────────────────────────────────────────────────────────────────────
# 表名面（TABLE-NAME-REGISTRY：代码内零表名字面量，一律经品类 id 走真源解析）
# ──────────────────────────────────────────────────────────────────────────────


def table_from_category(category_id: str) -> str:
    """品类 id → 全限定表名（唯一真源 zephyr.data.table_registry；禁在本文件写字面量表名）。"""
    from zephyr.data.table_registry import get_registry

    return str(get_registry().table(category_id))


def require_column(args: dict, key: str, op: str) -> Any:
    v = (args or {}).get(key)
    if v is None:
        raise ArmParamUnfrozen(f"arm_param_missing:{op}:{key}（卡面未给数值，禁替卡拍数）")
    return v


# ──────────────────────────────────────────────────────────────────────────────
# 臂算子（fn(base, params, args) -> pd.Series 日频敞口；base=同一底座序列）
# ──────────────────────────────────────────────────────────────────────────────


def _base_or_raise(base: Any, op: str) -> pd.Series:
    if base is None:
        raise ArmBaseMissing(f"arm_base_series_missing:{op}（底座序列须由绑定册/调用方注入，本件不取数）")
    if isinstance(base, pd.DataFrame):
        raise ArmBaseMissing(f"arm_base_is_panel:{op}（横截面权重帧需逐标的回放，本册只接日频标量敞口底座）")
    return pd.Series(base).sort_index()


def _to_dates(series: pd.Series) -> pd.Series:
    out = series.copy()
    out.index = pd.to_datetime(out.index)
    return out


# ──────────────────────────────────────────────────────────────────────────────
# e/r 两位面的机械校验（Owner 批令"假分雷必须先解后写、量纲错必红、禁靠注释自觉"）
# ──────────────────────────────────────────────────────────────────────────────

#: 敞口位（判官 e 位）容差与日收益位（r 位）量纲帽——两者都是**结构判据**，不是文档承诺
_EXPOSURE_EPS = 1e-9
_DAILY_RETURN_ABS_CAP = 0.5
#: 日收益面判"含负"所需的最少样本数（短样本可能全涨，不足此数不做该判，防误杀）
_RETURN_SIGN_MIN_N = 20


def require_exposure_face(series: Any, *, name: str, card_id: str) -> pd.Series:
    """e 位＝当日敞口/仓位系数：须落在 [0,1]（含 1e-9 容差）。

    越界（尤其出现负值）即判"收益/净值面误喂敞口位"——这正是那颗会出假分不报错的雷。
    """
    s = pd.Series(series).dropna()
    if s.empty:
        raise ArmFaceMismatch(f"empty_face:{name}:{card_id}（该位无任何读数，禁以空序列冒充满敞口或空仓）")
    n_bad = int((s < -_EXPOSURE_EPS).sum() + (s > 1.0 + _EXPOSURE_EPS).sum())
    if n_bad:
        raise ArmFaceMismatch(
            f"not_exposure_face:{name}:{card_id} e 位须 0..1 的当日敞口；"
            f"实测 min={float(s.min()):.6g} max={float(s.max()):.6g} 越界 {n_bad}/{len(s)} 日"
            f"＝收益或净值面喂进敞口位，判官 e×r.shift(-1) 会算成收益×收益（假分非报错）"
        )
    return pd.Series(series)


def require_daily_return_face(series: Any, *, name: str = "target", card_id: str = "") -> pd.Series:
    """r 位＝底座**日收益**：量级须像日收益（|x|≤0.5）且不得是单调非负的累计/净值面。

    两道判据各拦一种错法：max>1.5 或全非负且长样本＝拿净值/累计面当分母（会把 e×r 变成
    e×level）；|x| 超 0.5＝喂了别的量纲（如百分比未除 100，或分钟累计）。
    """
    s = pd.Series(series).dropna()
    if s.empty:
        raise ArmFaceMismatch(f"empty_face:{name}:{card_id}（r 位无读数，禁以空序列冒充底座日收益）")
    mx = float(s.abs().max())
    if mx > _DAILY_RETURN_ABS_CAP:
        raise ArmFaceMismatch(
            f"not_daily_return_face:{name}:{card_id} |r| 上限 {_DAILY_RETURN_ABS_CAP}（日频），"
            f"实测 max|r|={mx:.6g}＝疑似净值/累计面或百分比未归一量纲"
        )
    if len(s) >= _RETURN_SIGN_MIN_N and bool((s >= -_EXPOSURE_EPS).all()):
        raise ArmFaceMismatch(
            f"not_daily_return_face:{name}:{card_id} 长样本全非负＝敞口/仓位面特征（日收益必含负日），"
            f"疑似把 e 位序列喂到了 r 位（实测 min={float(s.min()):.6g} max={float(s.max()):.6g}）"
        )
    return pd.Series(series)


def verify_face_pair_quotes(card: dict, entry: dict) -> dict:
    """逐卡面声明 e/r 两位语义：两条引句都必须落在该卡面上（缺一即拒，禁默认值兜底）。

    e 引句取自臂定义面（build_arms 已校的同一域）；r 引句须取自底座/目标出处面
    （provenance_text：derivation/target_source/data_binding），因为"r 位到底吃谁的次日收益"
    是底座语义不是臂语义——把这两域混为一谈就是量纲错的起点。
    """
    e_q = str(entry.get("e_face_quote") or "")
    r_q = str(entry.get("r_face_quote") or "")
    if not e_q or not r_q:
        raise ArmFaceMismatch(
            f"face_contract_undeclared:{card.get('card_id')}（册格必须同时写 e_face_quote 与 r_face_quote，"
            f"缺任一即拒——不靠注释自觉）"
        )
    if e_q.replace(" ", "") not in arm_def_text(card).replace(" ", ""):
        raise ArmQuoteNotFound(f"e_face_quote_not_on_arm_face:{e_q[:24]}")
    if r_q.replace(" ", "") not in provenance_text(card).replace(" ", ""):
        raise ArmQuoteNotFound(f"r_face_quote_not_on_base_face:{r_q[:24]}")
    return {"e_face_quote": e_q, "r_face_quote": r_q}


def arm_identity(base: pd.Series, params: dict, args: dict) -> pd.Series:
    """基臂＝底座敞口原样（配对的另一边，卡面"共用同一底座"声明的直接实现）。"""
    return _to_dates(_base_or_raise(base, "arm_identity"))


def arm_constant(base: pd.Series, params: dict, args: dict) -> pd.Series:
    """臂＝敞口置常数（全清=0 / 满仓=1 / 任意冻结档值）；value 须由卡面或数据册给数值。"""
    b = _base_or_raise(base, "arm_constant")
    value = float(require_column(params, "value", "arm_constant"))
    return _to_dates(pd.Series(value, index=b.index, name=getattr(b, "name", None)))


def arm_level_cap_multiply(base: pd.Series, params: dict, args: dict) -> pd.Series:
    """臂＝"级别→仓位映射"乘子：level 序列（在册判定件产出，本件不重写判定）经 level_map 换成 cap 系数。

    level_map 的数值必须逐字来自卡面（如 L1 100%/L3 80/60/40%/L4 0%），缺一档数值即 ArmParamUnfrozen；
    base 传"敞口底座"（1=满仓基线）时本算子即"按级别比例改写净值路径，现金停放 0 收益"的标量面实现。
    """
    op = "arm_level_cap_multiply"
    b = _to_dates(_base_or_raise(base, op))
    level_map = params.get("level_map")
    if not isinstance(level_map, dict) or not level_map:
        raise ArmParamUnfrozen(f"{op}:level_map 未给（卡面级别→仓位映射数值须整表传入，禁自拟档位）")
    levels = params.get("levels")
    if levels is None:
        raise ArmParamUnfrozen(f"{op}:levels 未注入（级别序列须由在册判定件回放产出，本件禁重写迟滞解除逻辑）")
    lv = _to_dates(pd.Series(levels)).astype(str)
    missing = [str(k) for k in lv.dropna().unique() if str(k) not in {str(x) for x in level_map}]
    if missing:
        raise ArmParamUnfrozen(f"{op}:level_map 缺档位数值 {sorted(missing)}")
    cap = lv.map({str(k): float(v) for k, v in level_map.items()}).reindex(b.index)
    return _to_dates(b * cap.fillna(1.0))


def arm_gate_multiply(base: pd.Series, params: dict, args: dict) -> pd.Series:
    """臂＝条件门乘子：门为真时敞口乘 factor（0≤factor≤1 须给数值），门为假时原样。

    门序列由调用方从在册体制面注入（如 T-1 体制标签趋势门）；factor 没给数值＝卡面未冻结，拒出。
    """
    op = "arm_gate_multiply"
    b = _to_dates(_base_or_raise(base, op))
    gate = params.get("gate")
    if gate is None:
        raise ArmParamUnfrozen(f"{op}:gate 未注入（体制/条件门序列须由在册面产出，本件不取数）")
    g = _to_dates(pd.Series(gate))
    factor = params.get("factor")
    if factor is None:
        raise ArmParamUnfrozen(f"{op}:factor 未给数值（卡面降预算幅度未冻结＝禁替卡拍数）")
    f = float(factor)
    if not 0.0 <= f <= 1.0:
        raise ArmParamUnfrozen(f"{op}:factor={f} 不在 [0,1]（减仓乘子面，超出即另立口径须另卡）")
    on = g.reindex(b.index).astype(str).isin({str(x) for x in params.get("on_values", ["true", "True", "1"])})
    return _to_dates(b.where(~on, b * f))


def arm_subset_mask(base: pd.Series, params: dict, args: dict) -> pd.Series:
    """臂＝取子集（同一底座上按布尔掩码保留敞口，掩码外按 fill 档处置）。

    适用面=卡面把两臂定义成"同一行集/同一事件清单，仅入组条件异"且入组条件落在**日频**轴上；
    若入组条件落在 symbol×日（面板）轴上，本算子不适用（须逐标的回放，见 triage 的 panel 判据）。
    """
    op = "arm_subset_mask"
    b = _to_dates(_base_or_raise(base, op))
    mask = params.get("mask")
    if mask is None:
        raise ArmParamUnfrozen(f"{op}:mask 未注入（日频入组条件序列缺失，禁凭记忆造子集）")
    m = _to_dates(pd.Series(mask)).astype(bool)
    fill = float(require_column(params, "fill", op))
    return _to_dates(b.where(m.reindex(b.index).fillna(False), fill))


#: 臂算子册（每格 quote=卡面 arm_protocol 原文逐字片段；新增算子须同步 tests，见 MODIFY-GUARD）
ARM_OPS: dict[str, dict[str, Any]] = {
    "arm_identity": {
        "fn": arm_identity,
        "quote": "三臂输入同一基线净值序列与同一成交口径",
        "face": "scalar_exposure",
        "note": "配对基臂＝底座原样；卡面声明三臂/两臂共用同一底座时才可用",
    },
    "arm_constant": {
        "fn": arm_constant,
        "quote": "影子臂的现金停放 0 收益",
        "face": "scalar_exposure",
        "note": "敞口置常数档（全清/满仓/冻结档值）；value 由数据册按卡面数值传入",
    },
    "arm_level_cap_multiply": {
        "fn": arm_level_cap_multiply,
        "quote": "级别→仓位映射（L1 100%/L2 100% 禁新开/L3 梯度 80/60/40%/L4 0%）冻结于本卡",
        "face": "scalar_exposure",
        "note": "档位数值整表来自卡面；判定/迟滞序列由在册件回放，本件零重写",
    },
    "arm_gate_multiply": {
        "fn": arm_gate_multiply,
        "quote": "体制标签做趋势门",
        "face": "scalar_exposure",
        "note": "门=真时乘 factor；factor 无卡面数值即拒（本册不为未冻结档拍数）",
    },
    "arm_subset_mask": {
        "fn": arm_subset_mask,
        "quote": "仅入组条件异",
        "face": "scalar_exposure",
        "note": "日频子集掩码；卡面入组条件落在 symbol×日者不适用（见 triage）",
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# 双臂装配（喂 calibration_exam.run_card(signal=开臂, signal_b=基臂, target=同一底座收益)）
# ──────────────────────────────────────────────────────────────────────────────


def build_arms(card: dict, entry: dict, base: pd.Series | None = None) -> tuple[pd.Series, pd.Series, dict]:
    """臂册格 → (开臂敞口, 基臂敞口, 凭据)；双校验＝算子存在性 + 引句在卡面（缺一即拒）。

    entry 形：{card_id, op_open, op_base, quote_open?, quote_base?, params_open?, params_base?, status}
    引句缺省取 ARM_OPS[op]["quote"]，册内可逐卡覆写（同一算子服务多卡时各引各卡的原文）。
    """
    cid = str(card.get("card_id"))
    out: list[pd.Series] = []
    ev: dict[str, Any] = {"card_id": cid, "op": {}, "quote": {}}
    for side in ("open", "base"):
        op = entry.get(f"op_{side}")
        if op is None:
            raise ArmOpUnknown(f"arm_op_not_declared:{side}（册格须同时声明开臂与基臂算子）:{cid}")
        spec = ARM_OPS.get(str(op))
        if spec is None:
            raise ArmOpUnknown(f"arm_op_not_in_book:{op}")
        quote = entry.get(f"quote_{side}") or spec["quote"]
        verify_arm_quote(card, str(quote), str(op))
        params = dict(entry.get(f"params_{side}") or {})
        series = spec["fn"](base, params, entry.get("args") or {})
        # 算子产出必过 e 位面校验（含 arm_identity 直喂底座那条路——底座是收益面时这里就红）
        series = require_exposure_face(series, name=f"arm_{side}", card_id=cid)
        out.append(series)
        ev["op"][side] = op
        ev["quote"][side] = str(quote)
        ev.setdefault("params", {})[side] = {
            k: (f"<Series len={len(v)}>" if isinstance(v, pd.Series) else v) for k, v in params.items()
        }
    ev["target_face"] = "同一底座日收益（run_card 的 t 敞口 × t+1 目标即卡面按次日开/收盘改写净值路径的标量读法）"
    return out[0], out[1], ev


def build_arm_pair(
    card: dict, entry: dict, *, base: pd.Series | None, target: pd.Series | None
) -> tuple[pd.Series, pd.Series, pd.Series, dict]:
    """双臂＋底座日收益三面装配，直接对接 `run_card(signal=开臂, signal_b=基臂, target=日收益)`。

    与 build_arms 的差别只有一件、也是 Owner 批令①要的那件：这里**强制**逐卡面声明
    e/r 两位语义（e_face_quote/r_face_quote 双引句校验），并对 r 位做日收益量纲校验。
    build_arms 单独调用仍可出双臂（旧 10 支测试面零改动），但那是"半成品"——
    没声明 r 位的装配一旦喂进判官，就正是那颗"出假分不报错"的雷。
    """
    face = verify_face_pair_quotes(card, entry)
    open_arm, base_arm, ev = build_arms(card, entry, base=base)
    if target is None:
        raise ArmBaseMissing(
            f"arm_target_series_missing:{card.get('card_id')}（r 位须由绑定册注入底座日收益，本件不取数）"
        )
    tgt = _to_dates(pd.Series(target).sort_index())
    require_daily_return_face(tgt, name="target", card_id=str(card.get("card_id")))
    ev.update(face_contract=face, target_len=int(len(tgt)))
    return open_arm, base_arm, tgt, ev


# ──────────────────────────────────────────────────────────────────────────────
# 分箱器（机判，凭据=命中的卡面原文片段；禁 card_id 白名单硬分箱）
# ──────────────────────────────────────────────────────────────────────────────

#: 持仓路径臂信号（逐笔成交价/分钟切片/横截面构成/次序/分批）——臂效果落在"哪些标的、
#: 什么成交价、什么次序、拆几笔"上，执行核 comparison 分支（共享 target 的日频标量配对）表达不出。
#: 判据域＝臂定义面（arm_protocol/paired_arm_protocol/frozen_note/buckets.on），不含底座 provenance。
#: 词表真源=calibration_exam._COMPARISON_KNOWN_KEYS（本件只读不复制，防第二真源）
_TRADE_PATH_TOKENS = (
    "simulate(",
    "tp_rule",
    "ladder",
    "urgency",
    "time_stop",
    "成交价",
    "执行价",
    "分钟",
    "卖单",
    "成交清单",
    "触发清单",
    "持仓快照",
    "逐笔",
    "分批",
    "排队",
    "切片",
    "涨停",
    "可成交",
    "不可买",
    "确认模式",
    "分流确认",
    "路由",
    "权重字典",
    "调权",
    "离场判定函数",
    "触发集合",
    "顺序",
    "参与率",
    "出清",
    "追单",
    "条件单",
    "按臂权重",
    "行业×日",
    "再投",
    "顺延续",
    "结转",
)
#: 敞口缩放臂信号（同一底仓上的乘子/常数/条件门/日频子集）——标量配对可即刻出分
_SCALAR_TOKENS = (
    "基线净值",
    "同一底层组合净值路径",
    "同一份基线臂净值",
    "仓位映射",
    "现金停放",
    "趋势门",
    "入组条件",
    "假想全清",
    "同一成交口径",
    "同一底座",
    "共用同一",
    "敞口",
)
#: 敞口常数语义（0/1 数值由语义自明，不需另给档位数字；"不接入"这类消融接缝描述不算数值凭据）
_CONSTANT_ARM_TOKENS = ("全清", "满仓", "全买回", "一次性买回")
#: 臂参数数值凭据=带档值单位的数（%/pp/bp/倍/0.x/权重表 0.9/0.7 形），THD 编号里的裸数字串不算
_NUM_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:%|pp|bp|倍)|0\.\d+(?:\s*/\s*0?\.\d+)+|0\.\d+")
_STATE_FEASIBLE = "feasible_now"
_STATE_ENGINE = "needs_matching_engine"
_STATE_UNFROZEN = "unfrozen_arm_definition"


def has_arm_face(card: dict) -> bool:
    """该卡是否声明了臂协议面（arm_protocol 键，或散文里的 paired_arm_protocol 声明）。"""
    if any(str(v).strip() for v in _walk(card, ("arm_protocol",))):
        return True
    return "paired_arm_protocol" in arm_def_text(card)


def _vocab_outside(card: dict) -> list[str]:
    """该卡 pillars_numeric 里执行核 comparison 词表外的门柱键（只读卡面，判据零动）。

    词表读不到时返回哨兵串而非空表——空表会被下游读成"全在机判面内"＝谎报（fail-closed）。
    """
    vocab = None
    _bt = str(Path(__file__).resolve().parents[1])  # scripts/backtest（执行核内部用 fexam.* 绝对导入）
    if _bt not in sys.path:
        sys.path.insert(0, _bt)
    for _mod in ("fexam.calibration_exam", "scripts.backtest.fexam.calibration_exam"):
        try:
            vocab = importlib.import_module(_mod)._COMPARISON_KNOWN_KEYS
            break
        except Exception:  # noqa: BLE001  换下一条导入路径再试，两条皆败=如实标未读
            continue
    if vocab is None:
        return ["_vocab_unread_from_execution_core"]
    p = card.get("pillars_numeric") or {}
    return sorted(set(p) - set(vocab))


def _arm_count(blob: str) -> int | None:
    for token, n in (("四臂", 4), ("三臂", 3), ("双臂", 2), ("两臂", 2)):
        if token in blob:
            return n
    return None


#: 臂"幅度词"（这些词后面本该跟档值数值；卡面只提不赋值＝未冻结，凭据面点名，禁替卡拍数）
_MAGNITUDE_HINTS = ("预算", "趋势门", "降风险", "仓位映射", "敞口上限", "参与率上限")


def pending_numeric_params(card: dict) -> list[str]:
    """机械凭据：臂/底座文本里提到幅度词但相邻 16 字内无数字的面（不改三态，只供册主补冻结）。"""
    txt = arm_def_text(card) + " | " + provenance_text(card)
    out: list[str] = []
    for hint in _MAGNITUDE_HINTS:
        for m in re.finditer(re.escape(hint), txt):
            if not re.search(r"\d", txt[m.end() : m.end() + 16]):
                out.append(f"{hint}@无相邻数值")
                break
    return sorted(set(out))


def _missing_device(def_txt: str, prov_txt: str, kind: str) -> str:
    """缺件点名（给总包排产用，禁写"缺引擎"这种不可执行的一句话）。"""
    if "减仓" in def_txt and ("部分减仓" in prov_txt or "全仓进出" in prov_txt):
        return "在册装置的部分减仓能力（卡面自证 simulate 仅全仓进出）＋按臂参数化调用适配器＋逐臂日净值配对面"
    minute = any(t in def_txt for t in ("分钟", "切片", "成交价", "执行价", "参与率", "排队", "追单", "出清", "分批"))
    if minute:
        return "分钟/逐笔执行切片器（卡面自证：exit_simulator 仅日频全仓进出）＋按臂参数化调用装置的适配器"
    if kind == "panel":
        return "横截面权重帧日频组合回放（含逐标的可成交性约束）＋逐臂日净值配对面"
    if "simulate(" in prov_txt or "exit_simulator" in prov_txt:
        return "按臂参数化调用在册装置的适配器＋逐臂日净值配对面"
    return "逐臂日净值配对面（执行核 comparison 分支只支持共享 target 的敞口配对）"


def triage_card(card: dict) -> dict:
    """三态分箱（机判，凭据=命中的卡面原文片段；禁 card_id 白名单硬分箱）。

    返回 {card_id, state, credential, arm_count, family, signal_kind, scalar_expressible,
          numeric_frozen, out_of_vocab_pillars, missing_device, secondary_states}。
    优先级：结构缺件（持仓路径臂/panel 面）> 卡面未冻结（臂参数无数值）> 可行——
    补数值替代不了缺件，两缺同报（secondary_states）；feasible_now 要求两关全过。
    """
    def_txt = arm_def_text(card)
    prov_txt = provenance_text(card)
    family = str(card.get("family"))
    kind = str(card.get("signal_kind"))
    trade_hits = [t for t in _TRADE_PATH_TOKENS if t in def_txt]
    scalar_hits = [s for s in _SCALAR_TOKENS if s in def_txt]
    numeric = bool(_NUM_RE.search(def_txt)) or any(t in def_txt for t in _CONSTANT_ARM_TOKENS)
    secondary: list[str] = []
    if not has_arm_face(card):
        state = _STATE_ENGINE
        cred = "卡面无臂协议声明（arm_protocol/paired_arm_protocol 皆缺）→ 臂定义未落文本，禁凭记忆补"
    elif kind == "panel":
        state = _STATE_ENGINE
        cred = (
            "signal_kind=panel：臂定义落在 symbol×日横截面持仓路径面上，而执行核 comparison 分支对两臂恒走 "
            "_series_metrics/_arm_nav_metrics（日频标量；DataFrame 上 cumprod/mean 的轴会走偏）"
        )
        if trade_hits:
            cred += f"；臂定义面另命中持仓路径片段：{trade_hits[0]}"
        if scalar_hits:
            secondary.append("shared_base_declared:" + scalar_hits[0])
            secondary.append("panel_replay_only(缺横截面回放，非逐笔撮合)")
    elif trade_hits:
        state = _STATE_ENGINE
        cred = f"臂效果落在持仓路径面（臂定义原文命中：{trade_hits[0]}）→ 日频标量敞口配对表达不出"
    elif not numeric:
        state = _STATE_UNFROZEN
        cred = (
            f"臂变换形状可表达（臂定义原文命中：{(scalar_hits or ['arm_protocol'])[0]}），"
            "但卡面未给臂参数数值 → 禁替卡拍数，须先由册主补冻结档值"
        )
        secondary.append("scalar_expressible")
    elif scalar_hits:
        state = _STATE_FEASIBLE
        cred = f"臂=同一底座上的标量敞口变换（臂定义原文命中：{scalar_hits[0]}）且臂参数已给数值"
    else:
        state = _STATE_ENGINE
        cred = "臂定义未落在'同一底座上的敞口缩放'面上（无标量变换凭据）→ 缺件按 _missing_device 点名"
    if family not in ("comparison", "ablation"):
        secondary.append(f"family_not_routed:{family}（执行核只在 comparison/ablation 分支配对）")
    ov = _vocab_outside(card)
    if ov:
        secondary.append("out_of_vocab_pillars_need_legislation(见 P1)")
    return {
        "card_id": card.get("card_id"),
        "state": state,
        "credential": cred,
        "arm_count": _arm_count(def_txt),
        "family": family,
        "signal_kind": kind,
        "scalar_expressible": bool(scalar_hits) and kind != "panel",
        "numeric_frozen": numeric,
        "missing_device": None if state == _STATE_FEASIBLE else _missing_device(def_txt, prov_txt, kind),
        "out_of_vocab_pillars": ov,
        "pending_numeric_params": pending_numeric_params(card),
        "secondary_states": secondary,
    }


def triage_dir(cards_dir: str | Path) -> list[dict]:
    """目录内全部带臂协议面的卡逐张开分箱凭据（零 CH 零写；供普查复核，不做白名单）。"""
    rows: list[dict] = []
    for p in sorted(Path(cards_dir).rglob("*.yaml")):
        try:
            card = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:  # noqa: BLE001  非卡件/解析失败=跳过（凭据面不覆盖它，不谎报全量）
            continue
        if not isinstance(card, dict) or not card.get("card_id") or not has_arm_face(card):
            continue
        r = triage_card(card)
        r["path"] = str(p).replace("\\", "/")
        rows.append(r)
    return rows


# 人工CLI设计如此（同域 MOD-BT-243/248 先例）：分箱凭据按需打印，非永久自动系统面
if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  人工 CLI（按需分箱），非常驻自动系统
    import argparse
    import json

    ap = argparse.ArgumentParser(description="臂协议三态分箱凭据（零 CH 零写）")
    ap.add_argument("--cards-dir", required=True)
    ap.add_argument("--out", help="可选：凭据 json 落点（须指本班 tmp，禁写 data/ 业务目录）")
    a = ap.parse_args()
    _rows = triage_dir(a.cards_dir)
    _txt = json.dumps(_rows, ensure_ascii=False, indent=2, default=str)
    if a.out:
        Path(a.out).write_text(_txt, encoding="utf-8")
    print(_txt)
