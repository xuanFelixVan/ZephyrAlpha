# [MODULE] scripts.run_post_settlement_daily
# [DOMAIN] D_TRADING
# [CONSUMERS] Windows scheduled task ZephyrAlpha_PostSettlement (daily 15:30)
# [MATURITY] testing
# [STARTUP] scheduled
# [TTL] permanent
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# Purpose: scheduler wrapper for post-settlement reconcile + daily audit
# (57 doc section 3 GAP-3; Owner approved scheduling 2026-08-22).
# --if-trading-day guard: script exits 0 silently on non-trading days (zero noise).
# Logs append to .runtime/logs/post_settlement.log (runtime dir, not in git).
# Disable/restore: schtasks /change /tn ZephyrAlpha_PostSettlement /disable
# (disable-not-delete precedent, tracker #84).

Set-Location D:\ZephyrAlpha
& "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe" scripts\run_post_settlement.py --if-trading-day *>> ".runtime\logs\post_settlement.log"
exit $LASTEXITCODE
