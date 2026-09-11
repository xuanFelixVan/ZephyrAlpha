# [BLUEPRINT] MOD-INT_CHAIN_IMPACT | 待统筹登记（蓝图未建，真源=docs/_working/2026-09-09-news-industry-wiring-directive.md W4 行 + §3 入图交接协议）
# [MODULE] zephyr.intelligence.chain_impact_resolver
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.news_chain_node_linker（ChainNodeHit 输入契约）; zephyr.governance.depgraph_schema（ig_edge/ig_node/ig_node_company 只读连接）; zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.intelligence.chain_impact_stream（W5 盘中事件冲击流）; TDM 预留节点 TDM-E-L2-09-2（冲击标的生成，module_ref 由增长轨落图时挂本模块）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 扩散=ig_edge 无向邻接 BFS N 跳（默认 2；supply 边方向=上游→下游但情绪传导 MVP 按无向扩散）；方向口径（融合口径写明）：方向由调用方传入 polarity∈[-1,1]（来源=L1-S0-1 新闻情绪 polarity 或 event_score surprise_direction，两者同 [-1,1] 有向口径），sign 映射 ±0.15 死区→±1/0；方向符号全跳同向保留（板块联动假设；成本反号传导留事件类型细分后迭代，known simplification）；置信度=种子 hit.confidence×hop_decay^hop×公司映射 confidence（空=1.0），截断 [0,1]；扩散只走 ig_node 活节点表（墓碑节点不入扩散图，与 W3 词表同口径）；标的去重=同 symbol 取（hop 升序, 置信度降序）最优并记 sources 数；公司映射只取 ig_node_company.valid_to IS NULL（PIT 有效行）；命中节点本身=hop 0；polarity 落死区或 hits 为空→空输出不抛
# [MODIFY-GUARD] 待统筹登记（真源=接线指令 W4 行，蓝图由施工轨补画）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ChainImpactResolverError(ZA-IT-0030)——注入图数据畸形（边空端点/公司行空 symbol/max_hops<0/hop_decay∉(0,1]）时抛；PG 不可达由 from_pg 显式抛（W5 流层 catch 降级）；空图/空命中 fail-open 返回空
# [TESTS] tests/intelligence/test_chain_impact_resolver.py
# [A_module] module_id=MOD-INT_CHAIN_IMPACT | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] 接线指令 W4（冲击标的生成器；与 event_score 融合口径见 INVARIANTS 方向条款）

"""
MOD-INT_CHAIN_IMPACT ChainImpactResolver — 图谱节点冲击→受影响标的清单生成器（接线 W4）。

功能边界（MVP）：
- 输入：W3 ChainNodeHit 集 + polarity（[-1,1] 有向情绪/事件方向）
- 扩散：ig_edge 无向 BFS N 跳（默认 2），路径留痕（node_id 链），只走活节点表
- 标的：ig_node_company（valid_to IS NULL）按节点收集，role/confidence 透传
- 方向：全跳同向保留（置信度按 hop 衰减）——融合口径详见模块 INVARIANTS
- 输出 ImpactTarget frozen dataclass 列表，按（hop, -confidence, symbol）排序

不做什么：不读新闻（文本→节点属 MOD-INT_NEWS_CHAIN，新闻窗属 MOD-INT_IMPACT_STREAM）；
         不做事件类型细分（涨价/降价/断供/扩产的方向反号模型留后续迭代）；
         不写库不挂调度（清单由调用方消费）。

依据: docs/_working/2026-09-09-news-industry-wiring-directive.md W4 行
SSoT: depgraph MOD-INT_CHAIN_IMPACT（design 态 node 见 depgraph DB）
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: hits 参数
#   fields: 参数 hits，Sequence[ChainNodeHit]
#   code: resolve 方法形参（W3 链接产出）
# - id: I2
#   name: polarity 参数
#   fields: 参数 polarity，float，[-1,1]
#   code: resolve 方法形参（情绪/事件方向）
# - id: I3
#   name: edges/nodes/company_rows 图数据
#   fields: (from_node, to_node, edge_type) + (node_id, chain_id, name, tier) + (node_id, symbol, role, confidence)
#   code: 构造注入或 from_pg 加载
# 层: 算法
# - id: A1
#   name_zh: ① 邻接表构建
#   name_en: build_adjacency
#   intro: ig_edge 无向化（from↔to 双向入邻接表），自环剔除，端点限活节点表。
#   desc: 无向扩散假设=结构边不承载方向语义；supply 方向语义留类型细分迭代。
#   inputs: I3
#   outputs: dict[node_id, set[node_id]]
#   invariant: 自环/墓碑端点零入表
# - id: A2
#   name_zh: ② BFS N 跳扩散
#   name_en: expand
#   intro: 从命中节点集合出发层序扩散，路径留痕（种子在 path[0]），跳数≤max_hops。
#   desc: deque 层序；visited 防环；每跳衰减 hop_decay。
#   inputs: A1 I1
#   outputs: dict[node_id, (hop, path)]
#   invariant: 零环行；命中节点 hop=0
# - id: A3
#   name_zh: ③ 方向映射与标的落点
#   name_en: resolve
#   intro: polarity 死区映射 ±1/0，扩散节点收集公司映射成 ImpactTarget。
#   desc: 置信度=种子 hit.confidence×decay^hop×company_conf；同 symbol 去重取最优。
#   inputs: A2 I2 I3
#   outputs: tuple[ImpactTarget, ...]
#   invariant: confidence∈[0,1]；symbol 唯一；排序确定
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Final, Iterable, Sequence

from zephyr.intelligence.news_chain_node_linker import ChainNodeHit
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "DEFAULT_HOP_DECAY",
    "DEFAULT_MAX_HOPS",
    "DIRECTION_DEAD_ZONE",
    "ChainImpactResolver",
    "ChainImpactResolverError",
    "ImpactTarget",
    "direction_label",
]


class ChainImpactResolverError(ZephyrBaseError):
    """ZA-IT-0030: 图谱冲击标的生成错误（注入图数据畸形/参数越界等）。"""

    error_code = "ZA-IT-0030"


DEFAULT_MAX_HOPS: Final[int] = 2
DEFAULT_HOP_DECAY: Final[float] = 0.6
# polarity 死区半宽：|polarity| < 0.15 → 中性（0），与 [-1,1] 有向口径一致
DIRECTION_DEAD_ZONE: Final[float] = 0.15

_LABEL_MAP: Final[dict[int, str]] = {1: "利好", -1: "利空", 0: "中性"}


def direction_label(direction: int) -> str:
    """方向整数→中文标签（+1 利好 / -1 利空 / 0 中性）。"""
    return _LABEL_MAP.get(int(direction), "中性")


def _sign(polarity: float) -> int:
    """[-1,1] 有向值→方向整数（死区外保号，死区内中性）。"""
    if polarity >= DIRECTION_DEAD_ZONE:
        return 1
    if polarity <= -DIRECTION_DEAD_ZONE:
        return -1
    return 0


@dataclass(frozen=True)
class ImpactTarget:
    """图谱冲击扩散产出的受影响标的。

    Attributes
    ----------
    symbol : 标的代码（ig_node_company 原样；canonical 化属消费方口径）。
    node_id / chain_id / node_name / tier : 冲击落点环节（该标的映射来源节点）及其链归属。
    hop : 0=命中节点本身，1..N=扩散跳数。
    path : node_id 传导链（path[0]=种子命中节点，长度=hop+1）。
    direction : +1 利好 / -1 利空 / 0 中性（全跳同向，见模块 INVARIANTS）。
    confidence : [0,1]，种子 hit.confidence × hop_decay^hop × company_confidence。
    role / role_confidence : 公司在该环节的角色（龙头/核心/参与…）与映射置信度。
    sources : 同一 symbol 命中不同环节的来源数（多环节共振观察位）。
    """

    symbol: str
    node_id: str
    chain_id: str
    node_name: str
    tier: str
    hop: int
    path: tuple[str, ...]
    direction: int
    confidence: float
    role: str
    role_confidence: float
    sources: int

    @property
    def direction_label(self) -> str:
        """方向中文标签（利好/利空/中性，派生自 direction）。"""
        return direction_label(self.direction)


def _build_node_table(nodes: Iterable[tuple[str, str, str, str]]) -> dict[str, tuple[str, str, str]]:
    """活节点元数据表（扩散图顶点白名单：墓碑不入扩散图，INVARIANTS）。"""
    table: dict[str, tuple[str, str, str]] = {}
    for node_id, chain_id, name, tier in nodes:
        nid = str(node_id or "").strip()
        name_s = str(name or "").strip()
        if not nid or not name_s:
            raise ChainImpactResolverError(f"节点条目畸形（空 node_id/空 name）: {(node_id, name)!r}")
        if "已并入" in name_s:
            continue  # 注入侧墓碑防御（from_pg SQL 已滤，双保险）
        table[nid] = (str(chain_id or "").strip(), name_s, str(tier or "").strip())
    return table


def _build_adjacency(
    edges: Iterable[tuple[str, str, str]],
    node_table: dict[str, tuple[str, str, str]],
) -> dict[str, set[str]]:
    """无向邻接表（端点须为活节点；自环剔除）。"""
    adj: dict[str, set[str]] = {}
    for from_node, to_node, _edge_type in edges:
        f = str(from_node or "").strip()
        t = str(to_node or "").strip()
        if not f or not t:
            raise ChainImpactResolverError(f"边条目畸形（空端点）: {(from_node, to_node)!r}")
        if f == t or f not in node_table or t not in node_table:
            continue
        adj.setdefault(f, set()).add(t)
        adj.setdefault(t, set()).add(f)
    return adj


def _build_company_map(
    company_rows: Iterable[tuple[str, str, str | None, float | None]],
) -> dict[str, list[tuple[str, str, float]]]:
    """公司映射表：node_id -> [(symbol, role, confidence)]（PIT 有效行）。"""
    companies: dict[str, list[tuple[str, str, float]]] = {}
    for node_id, symbol, role, confidence in company_rows:
        nid = str(node_id or "").strip()
        sym = str(symbol or "").strip()
        if not nid or not sym:
            raise ChainImpactResolverError(f"公司映射条目畸形（空 node_id/空 symbol）: {(node_id, symbol)!r}")
        conf = 1.0 if confidence is None else float(confidence)
        companies.setdefault(nid, []).append((sym, str(role or "").strip(), conf))
    return companies


class ChainImpactResolver:
    """图谱节点冲击→标的清单解析器（规则法 MVP，无向 BFS+同向传导）。

    图数据经构造注入（测试/离线）或 :meth:`from_pg` 加载（生产）；
    空图/空命中 fail-open：resolve() 返回空元组不抛。
    """

    def __init__(
        self,
        edges: Iterable[tuple[str, str, str]] = (),
        nodes: Iterable[tuple[str, str, str, str]] = (),
        company_rows: Iterable[tuple[str, str, str | None, float | None]] = (),
        *,
        max_hops: int = DEFAULT_MAX_HOPS,
        hop_decay: float = DEFAULT_HOP_DECAY,
    ) -> None:
        """
        Parameters
        ----------
        edges : (from_node, to_node, edge_type) 三元组；空端点抛错，自环剔除。
        nodes : (node_id, chain_id, name, tier) 活节点元数据（墓碑已在 SQL 侧剔除；
                注入侧含"已并入"标记的节点视为墓碑同样剔除）。
        company_rows : (node_id, symbol, role, confidence)；空 symbol 抛错。
        max_hops / hop_decay : 扩散跳数上限与每跳置信度衰减底数。
        """
        if max_hops < 0:
            raise ChainImpactResolverError(f"max_hops 须≥0: {max_hops}")
        if not 0.0 < hop_decay <= 1.0:
            raise ChainImpactResolverError(f"hop_decay 须∈(0,1]: {hop_decay}")
        self._max_hops = max_hops
        self._hop_decay = hop_decay
        self._nodes = _build_node_table(nodes)
        self._adj = _build_adjacency(edges, self._nodes)
        self._companies = _build_company_map(company_rows)

    # ------------------------------------------------------------------
    # 图数据加载
    # ------------------------------------------------------------------

    @classmethod
    def from_pg(
        cls,
        conn_factory: Callable[[], Any] | None = None,
        *,
        max_hops: int = DEFAULT_MAX_HOPS,
        hop_decay: float = DEFAULT_HOP_DECAY,
    ) -> ChainImpactResolver:
        """从 depgraph PG 加载 ig_node 活节点 + ig_edge 全量边 + 公司有效映射。

        conn_factory 可注入（测试 mock）；None 走 depgraph_schema 只读连接。
        PG 不可达异常显式上抛（调用方 W5 流层 catch 降级）。
        """
        if conn_factory is None:
            from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

            conn_factory = get_depgraph_pg_connection
        conn = conn_factory()
        try:
            cur = conn.cursor()
            cur.execute(_SQL_NODES)
            node_rows = cur.fetchall()
            cur.execute(_SQL_EDGES)
            edge_rows = cur.fetchall()
            cur.execute(_SQL_COMPANIES)
            company_rows = cur.fetchall()
        finally:
            try:
                conn.close()
            except Exception:  # noqa: BLE001 — 连接关闭失败静默（只读查询已完成）
                pass
        return cls(
            ((r[0], r[1], r[2]) for r in edge_rows),
            node_rows,
            company_rows,
            max_hops=max_hops,
            hop_decay=hop_decay,
        )

    # ------------------------------------------------------------------
    # 扩散与标的生成
    # ------------------------------------------------------------------

    def graph_size(self) -> tuple[int, int, int]:
        """（活节点数, 邻接节点数, 公司映射节点数）诊断口径。"""
        return len(self._nodes), len(self._adj), len(self._companies)

    def resolve(
        self,
        hits: Sequence[ChainNodeHit],
        polarity: float,
    ) -> tuple[ImpactTarget, ...]:
        """节点命中+方向→受影响标的清单（去重排序后输出；死区/空输入→空元组）。"""
        direction = _sign(polarity)
        if direction == 0 or not hits:
            return ()
        # 种子：同节点多 hit 取最高 confidence 作种子强度（歧义命中合并强度）
        seeds: dict[str, ChainNodeHit] = {}
        for hit in hits:
            prev = seeds.get(hit.node_id)
            if prev is None or hit.confidence > prev.confidence:
                seeds[hit.node_id] = hit
        # ② BFS 扩散（只走活节点表；visited 防环）
        reach: dict[str, tuple[int, tuple[str, ...]]] = {
            node_id: (0, (node_id,)) for node_id in seeds
        }
        queue: deque[tuple[str, int, tuple[str, ...]]] = deque(
            (node_id, 0, (node_id,)) for node_id in seeds
        )
        visited: set[str] = set(seeds)
        while queue:
            cur, hop, path = queue.popleft()
            if hop >= self._max_hops:
                continue
            for nxt in sorted(self._adj.get(cur, ())):
                if nxt in visited:
                    continue
                visited.add(nxt)
                reach[nxt] = (hop + 1, path + (nxt,))
                queue.append((nxt, hop + 1, path + (nxt,)))
        # ③ 标的落点：节点 × 公司映射 → ImpactTarget；同 symbol 取（hop, -conf）最优
        best_by_symbol: dict[str, ImpactTarget] = {}
        sources: dict[str, int] = {}
        for node_id, (hop, path) in reach.items():
            seed_hit = seeds[path[0]]
            base_conf = seed_hit.confidence
            meta = self._nodes.get(node_id)
            if meta is None:  # 防御：注入图不一致时跳过无元数据节点
                continue
            chain_id, node_name, tier = meta
            for symbol, role, company_conf in self._companies.get(node_id, ()):
                conf = min(1.0, base_conf * (self._hop_decay**hop) * company_conf)
                target = ImpactTarget(
                    symbol=symbol,
                    node_id=node_id,
                    chain_id=chain_id,
                    node_name=node_name,
                    tier=tier,
                    hop=hop,
                    path=path,
                    direction=direction,
                    confidence=conf,
                    role=role,
                    role_confidence=company_conf,
                    sources=1,
                )
                sources[symbol] = sources.get(symbol, 0) + 1
                prev = best_by_symbol.get(symbol)
                if prev is None or (target.hop, -target.confidence, target.symbol) < (
                    prev.hop,
                    -prev.confidence,
                    prev.symbol,
                ):
                    best_by_symbol[symbol] = target
        out = [
            ImpactTarget(**{**t.__dict__, "sources": sources[t.symbol]})
            for t in best_by_symbol.values()
        ]
        out.sort(key=lambda t: (t.hop, -t.confidence, t.symbol))
        return tuple(out)


# SQL 常量（NO-BARE-SQL gate 豁免：_SQL_ 前缀，与 news_symbol_linker 同约定）
# 活节点表（剔墓碑，与 W3 词表同口径）；边全量（1.3k 行小表）；公司映射只取 PIT 有效行
# （valid_to IS NULL，与 api_server cm_* 通道同口径）
_SQL_NODES: Final[str] = (
    "SELECT node_id, chain_id, name, tier FROM ig_node WHERE name NOT LIKE '%已并入%'"  # noqa: bare-sql  模块级 SQL 常量（集中化专项另行治理）
)
_SQL_EDGES: Final[str] = "SELECT from_node, to_node, edge_type FROM ig_edge"  # noqa: bare-sql  模块级 SQL 常量（集中化专项另行治理）
_SQL_COMPANIES: Final[str] = (
    "SELECT node_id, symbol, role, confidence FROM ig_node_company WHERE valid_to IS NULL"  # noqa: bare-sql  模块级 SQL 常量（集中化专项另行治理）
)
