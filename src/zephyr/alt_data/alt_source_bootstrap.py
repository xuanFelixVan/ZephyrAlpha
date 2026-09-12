#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-ALT-008 | docs/03_modules/_domain_alt_data/alt_data_catalog/blueprint.md | §bootstrap
# [MODULE] zephyr.alt_data.alt_source_bootstrap
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.alt_data.alt_data_catalog; zephyr.alt_data.alt_data_compliance_reviewer; zephyr.alt_data.alt_source_health_manager
# [CONSUMERS] scheduler 侧接线（后续批）；tests/zephyr/data/test_alt_sources.py
# [STARTUP] lazy
# [MATURITY] production
# [INVARIANTS] 新增另类源必须在本文件登记 spec（catalog 元数据+合规四要素+审查证据）后才算接入；
#              审查证据必须引用实证（接口实测/DDL 路径），禁空白证据（reviewer fail-closed）；
#              本模块不做采集、不做持久化调度（治理三件为进程内引擎，持久化接线属后续批）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] spec 不合法->AltDataCatalogError/AltComplianceError/AltSourceHealthError 透传（fail-closed）
# [TESTS] tests/zephyr/data/test_alt_sources.py
# [TTL] permanent
"""alt_source_bootstrap — 另类数据源治理三件（catalog/合规/健康）统一登记接线。

背景（2026-09-12 另类数据第 1 批，docs/_working/2026-09-12-alt-data-handoff.md §8-5）：
    alt_data 包治理三件（AltDataCatalog/AltDataComplianceReviewer/AltSourceHealthManager）
    此前 DORMANT 零调用方；本模块首次实弹接线——每新增一个免注册直连另类源，在
    ALT_SOURCES 登记一份 spec（目录元数据 + 合规四要素台账 + 逐项审查证据），
    build_governance_triple() 一次构建三件并完成登记→审查→放行闭环。

    健康探针的调度层接线（任务失败→record_sample→降级阶梯→告警）属后续批
    （与 social_sentiment_collector 唤醒同批），当前提供 record_fetch_outcome()
    供 provider 调用方/测试手工喂样本。

划界（蓝图 §0 查重分工）：
    - 采集在 zephyr.data.implementations.akshare_alt_provider（本模块零采集）
    - 持久登记在 data_asset_registry.yaml（SRC-AKSHARE-ALT-001/DS-230/DS-231，本模块不落盘）
    - 断供登记在 known_data_gaps.yaml（本模块不写缺口）
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Callable, Mapping

from zephyr.alt_data.alt_data_catalog import (
    AltDataCatalog,
    CatalogEntry,
    CatalogSourceType,
)
from zephyr.alt_data.alt_data_compliance_reviewer import (
    AltComplianceError,
    AltDataComplianceReviewer,
)
from zephyr.alt_data.alt_source_health_manager import (
    AltSourceHealthError,
    AltSourceHealthManager,
    HealthAlert,
)

__all__ = [
    "ALT_SOURCES",
    "COMPLIANCE_CHECKLIST",
    "AltSourceSpec",
    "build_governance_triple",
    "record_fetch_outcome",
]

# 上线前审查清单（逐项须给 (passed, evidence)；evidence 空白被 reviewer 拒绝）
COMPLIANCE_CHECKLIST: tuple[str, ...] = (
    "license_cleared",        # 许可/用途边界清晰（公开数据/学术用途声明已核）
    "attribution_recorded",   # 来源与接口名登记（可追溯）
    "no_personal_data",       # 不含个人信息（聚合/指数级数据）
    "rate_limit_declared",    # 限频/配额已声明并有自限速
    "no_redistribution",      # 不转售不二次分发承诺
)


@dataclass(frozen=True)
class AltSourceSpec:
    """另类数据源治理登记单（目录元数据 + 合规四要素 + 审查证据）。"""

    source_id: str
    source_type: CatalogSourceType
    update_frequency: str
    quality_score: float
    cost_quota: int
    description: str
    tags: tuple[str, ...]
    # 合规四要素（ComplianceRecord）
    collection_method: str
    tos_terms: str
    license_scope: str
    privacy_impact: str
    # 审查证据：checklist 项 -> (是否通过, 证据)
    review_evidence: Mapping[str, tuple[bool, str]] = field(default_factory=dict)


ALT_SOURCES: tuple[AltSourceSpec, ...] = (
    AltSourceSpec(
        source_id="alt_stock_comment",
        source_type=CatalogSourceType.SOCIAL,
        update_frequency="daily_snapshot",
        quality_score=0.85,
        cost_quota=60,  # RPM 自限速（与 meta.rate_limit_default 一致）
        description=(
            "千股千评全表日快照（东财数据中心综合评价）：关注指数/综合得分/机构参与度/"
            "排名及变动，约 5200 行/日；关注指数=股吧关注度代理（akshare 无股吧发帖量"
            "直连接口，2026-09-12 实测枚举确认）；接口仅当日无历史通道，每日累积。"
            "表 c1_market.alt_stock_comment，任务 alt_stock_comment_snapshot。"
        ),
        tags=("情绪", "关注度", "千股千评", "东财"),
        collection_method="akshare stock_comment_em（东财数据中心公开展示数据，HTTP 拉取）",
        tos_terms="东财数据中心公开页面展示数据；个人研究用途；遵守平台 robots 与限频礼节",
        license_scope="public_reference_data（不转售不二次分发，仅个人研究）",
        privacy_impact="none（聚合评价指标，无个人信息）",
        review_evidence={
            "license_cleared": (True, "东财公开展示数据+个人研究用途（SRC-AKSHARE-ALT-001 compliance 字段）"),
            "attribution_recorded": (True, "data_asset_registry DS-230/JOB-092；DDL schemas/categories/market_alt_stock_comment.py"),
            "no_personal_data": (True, "全表为股票级聚合评价指标（关注指数/得分/排名），无任何个人信息字段（接口 13 列实测）"),
            "rate_limit_declared": (True, "provider meta.rate_limit_default=60 RPM，_call_with_policy 统一限频重试"),
            "no_redistribution": (True, "SRC-AKSHARE-ALT-001 license_scope=public_reference_data 承诺不转售不分发"),
        },
    ),
    AltSourceSpec(
        source_id="alt_shipping_index",
        source_type=CatalogSourceType.OTHER,
        update_frequency="daily",
        quality_score=0.9,
        cost_quota=60,
        description=(
            "航运运价指数长表：BDI（金十源 1988-10 起含日涨跌幅）+ BCI/BSI/BHMI/HRCI/"
            "BCTI/BDTI（macro_china_freight_index 约 2006 起）；(trade_date,index_code) 粒度，"
            "BDI 双源重叠以 macro_shipping_bdi 为准免重。出口链/航运板块景气前瞻。"
            "表 c1_market.alt_shipping_index，任务 alt_shipping_index_incremental/full_refresh。"
        ),
        tags=("运价", "航运", "BDI", "产业景气"),
        collection_method="akshare macro_shipping_bdi + macro_china_freight_index（金十/公开指数数据）",
        tos_terms="公开运价指数数据；个人研究用途；日频拉取自带自限速",
        license_scope="public_reference_data（不转售不二次分发，仅个人研究）",
        privacy_impact="none（市场指数，无个人信息）",
        review_evidence={
            "license_cleared": (True, "公开运价指数（波罗的海交易所/金十公开页），无获取许可壁垒"),
            "attribution_recorded": (True, "data_asset_registry DS-231/JOB-093/094；DDL schemas/categories/market_alt_shipping_index.py"),
            "no_personal_data": (True, "市场指数值，无个人信息"),
            "rate_limit_declared": (True, "provider meta.rate_limit_default=60 RPM，_call_with_policy 统一限频重试"),
            "no_redistribution": (True, "SRC-AKSHARE-ALT-001 license_scope=public_reference_data 承诺不转售不分发"),
        },
    ),
)


def build_governance_triple(
    *,
    clock: Callable[[], datetime.datetime] | None = None,
    alert_sink: Callable[[HealthAlert], None] | None = None,
    fts_connection=None,
) -> tuple[AltDataCatalog, AltDataComplianceReviewer, AltSourceHealthManager]:
    """构建治理三件并完成 ALT_SOURCES 全量登记→审查→放行。

    Args:
        clock: 统一时钟注入（测试确定性）。
        alert_sink: 健康告警回调（接 alerter 属后续批，测试可注入收集器）。
        fts_connection: 目录 FTS5 SQLite 连接（可选；生产持久化接线属后续批）。

    Returns:
        (catalog, compliance_reviewer, health_manager)，三者均已登记全部 ALT_SOURCES，
        合规审查全部 APPROVED（fail-closed：任一项不过则异常上抛，不放行半审状态）。

    Raises:
        AltComplianceError: 审查项不齐/证据空白/overall 未全过。
        AltDataCatalogError: 目录元数据非法。
        AltSourceHealthError: 健康管理参数非法。
    """
    spec_ids = [s.source_id for s in ALT_SOURCES]

    catalog = AltDataCatalog(clock=clock, fts_connection=fts_connection)
    reviewer = AltDataComplianceReviewer(checklist=COMPLIANCE_CHECKLIST, clock=clock)
    health = AltSourceHealthManager(
        source_ids=spec_ids,
        clock=clock,
        alert_sink=alert_sink,
        # 日频另类源：数据陈旧容忍放宽到 48h（周末不更新属正常）
        max_staleness_seconds=48 * 3600.0,
        max_latency_seconds=60.0,  # akshare 全表拉取秒级~十秒级
    )

    for spec in ALT_SOURCES:
        # ① 目录登记（元数据 + FTS）
        catalog.register(
            CatalogEntry(
                source_id=spec.source_id,
                source_type=spec.source_type,
                update_frequency=spec.update_frequency,
                quality_score=spec.quality_score,
                cost_quota=spec.cost_quota,
                description=spec.description,
                tags=spec.tags,
            )
        )
        catalog.approve(spec.source_id)
        # ② 合规四要素台账 + 逐项审查
        reviewer.register(
            spec.source_id,
            collection_method=spec.collection_method,
            tos_terms=spec.tos_terms,
            license_scope=spec.license_scope,
            privacy_impact=spec.privacy_impact,
        )
        record = reviewer.review(spec.source_id, results=spec.review_evidence)
        if not record.overall_passed:
            raise AltComplianceError(
                f"另类源 {spec.source_id} 合规审查未全过，禁止接入（fail-closed）"
            )
    return catalog, reviewer, health


def record_fetch_outcome(
    health: AltSourceHealthManager,
    source_id: str,
    *,
    success: bool,
    latency_seconds: float,
    data_ts: datetime.datetime | None = None,
) -> None:
    """喂一次采集样本到健康滑动窗口（provider 调用方/调度接线/测试共用）。

    data_ts 缺省取当前时钟（调用方有接口自带数据日期时显式传入——PIT 锚优先运行时钟）。
    """
    if data_ts is None:
        data_ts = datetime.datetime.now()
    health.record_sample(
        source_id,
        success=success,
        latency_seconds=latency_seconds,
        data_ts=data_ts,
    )
