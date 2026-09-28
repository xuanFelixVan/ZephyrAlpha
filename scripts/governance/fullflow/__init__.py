# [BLUEPRINT] MOD-GOV_SCRIPTS
# [MODULE] scripts.governance.fullflow.__init__
# [DOMAIN] D_GOV_SCRIPTS
# [STARTUP] imported
# [TTL] permanent
# fullflow/ — 全流通战役机生尺（静态清单/对账表自动生成器）
# 对标宪法 §9.5「凡条目列表+计数清单必须生成器产出，手工维护必然漂移」
# 现有件：generate_fullflow_crosscheck.py（五向计数＋逐段挖矿覆盖矩阵＋漂移标志位）
__all__ = ["generate_fullflow_crosscheck"]
