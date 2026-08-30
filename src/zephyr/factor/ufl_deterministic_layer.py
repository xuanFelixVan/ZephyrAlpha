# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.ufl_deterministic_layer
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] 无 zephyr import（纯标记/过滤/SQL 生成核；feature_store 落库面=MOD-L02-FS feature_store_writer、UFL 追加式事实语义锚=MOD-L00-004 storage_tiering.UFLFactLayer——均为语义引用不 import）
# [CONSUMERS] （候选：factor_production_pipeline 落库批/盘前因子评估/ML 训练特征抽取的确定性子集过滤接线）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 未标记因子 fail-closed=非确定性；标记同值幂等、异值冲突拒绝（UFL 追加式事实语义）；行级打标不改原行；视图 SQL 表名白名单校验+单引号双写转义；空确定性集合→空视图(1=0)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 factor_id/冲突标记/缺 factor_id 列/非法表名 → ValueError（fail-closed）
# [TESTS] tests/factor/test_ufl_deterministic_layer.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 因子级 is_deterministic 标记（显式 mark 或 classify_from_inputs 推导）+ 特征值长表行
# A1: 标记台账——fail-closed 查询；同值幂等/异值冲突拒绝（追加式）
# A2: 行级打标——tag_feature_rows 为每行附加 is_deterministic 键（元数据层，不碰 CH DDL）
# A3: 确定性查询视图——build_deterministic_view_sql 生成 factor_id IN 确定性集合的 VIEW（空集→1=0）
# A4: 读侧过滤——filter_deterministic 只留确定性因子行
# O1: 打标行/过滤行/视图 SQL/确定性因子集合
# [/ALGO_FLOW]
"""



UFL 确定性事实层（v8.1，CAND-FAC-011 / B10-01176）。

feast 式"标记+视图"管理特征子集：确定性事实层 = 特征仓（feature_store）中
is_deterministic=True 的因子子集。确定性 = 同一输入同一输出可重放（纯价量派生）；
非确定性 = 依赖外部状态（新闻语料/LLM/实时会话/随机源）。

落地形态（两条通道，不碰 CH DDL——factor_feature_value 表结构为 human_only
schema-change 守卫件，is_deterministic 不落成物理列，落元数据层）：
  ① 显式标记：mark(factor_id, is_deterministic, evidence)；
  ② 推导标记：classify_from_inputs——输入全集 ⊆ 价量基础集 → 确定性。
查询视图两条消费路径：CH 侧 CREATE VIEW SQL（build_deterministic_view_sql）与
读侧行过滤（filter_deterministic），语义同一确定性集合。

查重裁定（不重复既有件）：
  - MOD-L00-004 storage_tiering.UFLFactLayer：D_DATA 通用存储层内存追加式事实层
    （key→value 禁改校验），不触及特征仓/因子维度；本件复用其"确定性门+追加式"
    语义（同值幂等/异值拒绝），作用域为 feature_store 因子子集标记与视图。
  - MOD-L02-FS feature_store_writer：CH 长表写入器（列序 INSERT_COLUMNS 真源），
    无 is_deterministic 标记与确定性视图；本件不修改写入器与 DDL，打标落元数据层。

依据: A1交易决策架构 §1.1（§29.24 Feature Store 子集 is_deterministic=True）；
construction_backlog_dig.tsv B10-01176。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: inputs 参数
#   fields: 参数 inputs，类型注解 Iterable[str]
#   code: ufl_deterministic_layer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: rows 参数
#   fields: 参数 rows，类型注解 Iterable[Mapping]
#   code: ufl_deterministic_layer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: layer 参数
#   fields: 参数 layer，类型注解 UflDeterministicLayer
#   code: ufl_deterministic_layer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: table 参数
#   fields: 参数 table，类型注解 str
#   code: ufl_deterministic_layer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① classify_from_inputs
#   name_en: classify_from_inputs
#   intro: 输入集推导确定性：非空且全集 ⊆ 价量基础集 → True。
#   desc: 输入集推导确定性：非空且全集 ⊆ 价量基础集 → True。 空输入集 fail-closed=False（无输入证据不可断定为确定性）。；源码 L171-L179
#   inputs: inputs
#   outputs: bool
# - id: A2
#   name_zh: ② UflDeterministicLayer
#   name_en: UflDeterministicLayer
#   intro: UFL 确定性事实层门面：标记台账 + 行级打标 + 确定性视图 + 读侧过滤。
#   desc: UFL 确定性事实层门面：标记台账 + 行级打标 + 确定性视图 + 读侧过滤。 Args: markings: 初始标记映射 {factor_id: is_determinis…；公共方法（定义序）: mark, i…
#   inputs: markings
#   outputs: 返回值
# - id: A3
#   name_zh: ③ tag_feature_rows
#   name_en: tag_feature_rows
#   intro: 特征值长表行 → 附加 is_deterministic 键的新行列表（原行不被修改）。
#   desc: 特征值长表行 → 附加 is_deterministic 键的新行列表（原行不被修改）。 Args: rows: 长表行（至少含 factor_id 键；其余键原样保留）。 la…；源码 L256-L276
#   inputs: rows layer
#   outputs: list[dict]
# - id: A4
#   name_zh: ④ filter_deterministic
#   name_en: filter_deterministic
#   intro: 读侧过滤：只留确定性因子的行（未标记 fail-closed 滤除）。
#   desc: 读侧过滤：只留确定性因子的行（未标记 fail-closed 滤除）。 Args: rows: 长表行（含 factor_id 键）。 layer: 确定性标记台账。 Retur…；源码 L279-L298
#   inputs: rows layer
#   outputs: list[dict]
# - id: A5
#   name_zh: ⑤ build_deterministic_view_sql
#   name_en: build_deterministic_view_sql
#   intro: 确定性查询视图 DDL：feature_store 上 is_deterministic=True 因子子集。
#   desc: 确定性查询视图 DDL：feature_store 上 is_deterministic=True 因子子集。 空确定性集合 → WHERE 1=0 空视图（fail-close…；源码 L301-L330
#   inputs: table layer view_name
#   outputs: str
#   （注：A5 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: （候选：factor_production_pipeline 落库批/盘前因子评估/ML 训练特征抽取的确定性子集过滤接线）
# - id: O2
#   name_zh: list[dict]
#   name_en: list[dict]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: （候选：factor_production_pipeline 落库批/盘前因子评估/ML 训练特征抽取的确定性子集过滤接线）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Iterable, Mapping

__all__: Final = [
    "DeterminismMarking",
    "UflDeterministicLayer",
    "build_deterministic_view_sql",
    "classify_from_inputs",
    "filter_deterministic",
    "tag_feature_rows",
]

#: 价量基础输入封闭集（输入全集 ⊆ 本集 → 可重放确定性）
_DETERMINISTIC_BASE_INPUTS: Final = frozenset(
    {"open", "high", "low", "close", "volume", "amount", "vwap", "turnover", "trade_date", "symbol"}
)

#: CH 表名/视图名合法字符（防注入白名单）
_IDENTIFIER_RE: Final = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$")


@dataclass(frozen=True)
class DeterminismMarking:
    """单因子确定性标记（不可变）。

    Attributes:
        factor_id: 因子 ID。
        is_deterministic: 是否确定性（可重放）。
        evidence: 标记依据（审计留痕）。
    """

    factor_id: str
    is_deterministic: bool
    evidence: str = ""


def classify_from_inputs(inputs: Iterable[str]) -> bool:
    """输入集推导确定性：非空且全集 ⊆ 价量基础集 → True。

    空输入集 fail-closed=False（无输入证据不可断定为确定性）。
    """
    normalized = {str(i).strip().lower() for i in inputs if str(i).strip()}
    if not normalized:
        return False
    return normalized <= _DETERMINISTIC_BASE_INPUTS


def _quote_literal(value: str) -> str:
    """SQL 字符串字面量：单引号双写转义。"""
    return "'" + value.replace("'", "''") + "'"


def _validate_identifier(name: str, what: str) -> None:
    if not _IDENTIFIER_RE.match(name):
        raise ValueError(f"{what} 非法标识符: {name!r}（仅允许 letter/digit/_. 且分段以字母或下划线起）")


class UflDeterministicLayer:
    """UFL 确定性事实层门面：标记台账 + 行级打标 + 确定性视图 + 读侧过滤。

    Args:
        markings: 初始标记映射 {factor_id: is_deterministic}（可选）。
    """

    def __init__(self, *, markings: Mapping[str, bool] | None = None) -> None:
        self._markings: dict[str, DeterminismMarking] = {}
        if markings:
            for factor_id, flag in markings.items():
                self.mark(factor_id, bool(flag))

    # ---------------------------------------------------------------- 标记台账

    def mark(self, factor_id: str, is_deterministic: bool, evidence: str = "") -> DeterminismMarking:
        """登记因子确定性标记。同值幂等；异值=篡改，冲突拒绝（UFL 追加式语义）。"""
        if not factor_id or not str(factor_id).strip():
            raise ValueError("factor_id 不能为空")
        factor_id = str(factor_id).strip()
        existing = self._markings.get(factor_id)
        if existing is not None:
            if existing.is_deterministic == bool(is_deterministic):
                return existing  # 幂等重放
            raise ValueError(
                f"确定性标记冲突: {factor_id!r} 已标记 is_deterministic={existing.is_deterministic}"
                f"（依据 {existing.evidence!r}），拒绝改为 {bool(is_deterministic)}——追加式事实层禁改"
            )
        marking = DeterminismMarking(factor_id=factor_id, is_deterministic=bool(is_deterministic), evidence=evidence)
        self._markings[factor_id] = marking
        return marking

    def is_deterministic(self, factor_id: str) -> bool:
        """因子是否确定性。未标记 fail-closed=False。"""
        marking = self._markings.get(factor_id)
        return marking.is_deterministic if marking is not None else False

    def marking_of(self, factor_id: str) -> DeterminismMarking | None:
        """因子标记详情（未标记 None）。"""
        return self._markings.get(factor_id)

    def deterministic_factor_ids(self) -> frozenset[str]:
        """确定性因子集合（只读快照）。"""
        return frozenset(fid for fid, m in self._markings.items() if m.is_deterministic)

    def markings_snapshot(self) -> Mapping[str, DeterminismMarking]:
        """全量标记快照（只读）。"""
        return MappingProxyType(dict(self._markings))

    # ---------------------------------------------------------------- 打标/过滤/视图

    def tag_rows(self, rows: Iterable[Mapping]) -> list[dict]:
        """行级打标门面（见 tag_feature_rows）。"""
        return tag_feature_rows(rows, self)

    def filter_deterministic(self, rows: Iterable[Mapping]) -> list[dict]:
        """读侧过滤门面（见 filter_deterministic）。"""
        return filter_deterministic(rows, self)

    def deterministic_view_sql(self, table: str, *, view_name: str = "v_factor_feature_value_deterministic") -> str:
        """确定性查询视图 SQL 门面（见 build_deterministic_view_sql）。"""
        return build_deterministic_view_sql(table, self, view_name=view_name)


def tag_feature_rows(rows: Iterable[Mapping], layer: UflDeterministicLayer) -> list[dict]:
    """特征值长表行 → 附加 is_deterministic 键的新行列表（原行不被修改）。

    Args:
        rows: 长表行（至少含 factor_id 键；其余键原样保留）。
        layer: 确定性标记台账。

    Returns:
        list[dict]：每行 = 原行字段 + is_deterministic(bool)。

    Raises:
        ValueError: 行缺 factor_id 键。
    """
    tagged: list[dict] = []
    for row in rows:
        if "factor_id" not in row:
            raise ValueError(f"特征值行缺 factor_id 键: {sorted(row.keys())!r}")
        new_row = dict(row)
        new_row["is_deterministic"] = layer.is_deterministic(str(row["factor_id"]))
        tagged.append(new_row)
    return tagged


def filter_deterministic(rows: Iterable[Mapping], layer: UflDeterministicLayer) -> list[dict]:
    """读侧过滤：只留确定性因子的行（未标记 fail-closed 滤除）。

    Args:
        rows: 长表行（含 factor_id 键）。
        layer: 确定性标记台账。

    Returns:
        list[dict]：确定性因子行（原行对象不改，浅拷贝）。

    Raises:
        ValueError: 行缺 factor_id 键。
    """
    kept: list[dict] = []
    for row in rows:
        if "factor_id" not in row:
            raise ValueError(f"特征值行缺 factor_id 键: {sorted(row.keys())!r}")
        if layer.is_deterministic(str(row["factor_id"])):
            kept.append(dict(row))
    return kept


def build_deterministic_view_sql(
    table: str,
    layer: UflDeterministicLayer,
    *,
    view_name: str = "v_factor_feature_value_deterministic",
) -> str:
    """确定性查询视图 DDL：feature_store 上 is_deterministic=True 因子子集。

    空确定性集合 → WHERE 1=0 空视图（fail-closed：无标记即无确定性子集，
    视图语义明确而非缺省全量）。

    Args:
        table: 特征值表全名（如 c1_market.factor_feature_value；白名单校验）。
        layer: 确定性标记台账。
        view_name: 视图名（白名单校验）。

    Returns:
        CREATE OR REPLACE VIEW 语句（不执行，执行属 Owner 窗口）。

    Raises:
        ValueError: 表名/视图名非法标识符。
    """
    _validate_identifier(table, "表名")
    _validate_identifier(view_name, "视图名")
    factor_ids = sorted(layer.deterministic_factor_ids())
    if factor_ids:
        predicate = "factor_id IN (" + ", ".join(_quote_literal(fid) for fid in factor_ids) + ")"
    else:
        predicate = "1=0"
    return f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM {table} WHERE {predicate}"
