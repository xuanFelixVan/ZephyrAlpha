# [BLUEPRINT] MOD-SIG-093 | docs/_working/infoaxis/15_intraday_workbook.md §2
# [MODULE] zephyr.signal_intraday
# [DOMAIN] D_SIGNAL_INTRADAY
# [TTL] permanent
"""日内做T·Tick 信号域的包声明。

界定域边界、登记子模块、固化 Tick 延迟口径——QMT 桥比 miniQMT 慢 3-5 秒，
桥数据进回测必须显式计入该延迟，防前视红线。

重建留痕（2026-10-16 st-infoaxis-land-20261014 复工）：本件原为 10-14/15 战役在途产物，
经 10-15 D 盘事故后未落在任何存证面（队列 blob／quarantine／rescue 三面均无）。
本次按 `module_translation_registry.yaml` 已登记 desc_zh（本 docstring 正文即其忠实转写）＋
`docs/02_enterprise_architecture/02_domain_architecture_docs/69_d_signal_intraday.md`
记录的 module_id（MOD-SIG-093）重建，非新造身份。

# [ALGO_FLOW]
# 层: 包声明面（零算法流——orderflow_features 子模块承载 OFI/micro-price 实件）
# [/ALGO_FLOW]
"""
