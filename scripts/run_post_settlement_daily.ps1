# [MODULE] scripts.run_post_settlement_daily
# [DOMAIN] D_TRADING
# [CONSUMERS] none (manual/backup entry, NOT a scheduled-task target; W-141/W-156 2026-09-28)
# [MATURITY] testing
# [STARTUP] scheduled
# [TTL] permanent
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# Purpose: manual/backup wrapper for post-settlement reconcile + daily audit
# (57 doc section 3 GAP-3; Owner approved scheduling 2026-08-22).
# Truth (W-141, 2026-09-28): scheduled task ZephyrAlpha_PostSettlement executes
# scriptsun_post_settlement.py directly (schtasks /xml ACTION verified); the
# scheduler never invokes this file. This wrapper differs semantically by
# adding --if-trading-day (silent no-op on non-trading days).
# --if-trading-day guard: script exits 0 silently on non-trading days (zero noise).
# Logs append to .runtime/logs/post_settlement.log (runtime dir, not in git).
# Disable/restore: schtasks /change /tn ZephyrAlpha_PostSettlement /disable
# (disable-not-delete precedent, tracker #84).

Set-Location D:\ZephyrAlpha
& "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe" scripts\run_post_settlement.py --if-trading-day *>> ".runtime\logs\post_settlement.log"
exit $LASTEXITCODE
