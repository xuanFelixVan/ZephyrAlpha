# run_optimize_merge_hidden.ps1 - hidden-launch target for scheduled task ZephyrAlpha_CH-OptimizeMerge-Weekly
# 2026-09-08 no-flash sweep (#ARCH-BOOT-WINDOW-FLASH): python.exe is a console-subsystem
# program; Task Scheduler Interactive launch flashed a window on every weekly fire.
# Now run under launch_hidden.vbs; console output is captured to a log (previously discarded).
Set-Location D:\ZephyrAlpha
& 'C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe' 'D:\ZephyrAlpha\scripts\ch\optimize_merge.py' --weekly *>> 'D:\ZephyrAlpha\logs\ch_optimize_merge_weekly.log'
exit $LASTEXITCODE
