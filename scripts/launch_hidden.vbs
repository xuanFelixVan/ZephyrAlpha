' [MODULE] scripts.launch_hidden
' [DOMAIN] D_DATA
' [TTL] permanent
' launch_hidden.vbs - Task Scheduler 无闪窗启动器
' ============================================================================
' 用途: 消除 Task Scheduler 启动控制台程序(powershell.exe)时的闪窗
'
' 病根(#ARCH-BOOT-WINDOW-FLASH):
'   powershell.exe 是控制台子系统程序。Task Scheduler 以 Interactive 方式拉起它时
'   会瞬间分配一个控制台窗口; "-WindowStyle Hidden" 只能在 PowerShell 主窗口创建
'   之后再隐藏, 来不及阻止那一瞬间的闪现。3 个 watchdog 任务每 5min 重复触发 =>
'   每 5min 闪 3 次窗口。
'
' 原理:
'   wscript.exe 是 GUI 子系统程序, 不创建控制台窗口;
'   WScript.Shell.Run cmd, 0 (SW_HIDE) 启动目标 powershell 时, 控制台窗口被隐藏创建,
'   从根本上消除闪窗。
'
' 用法 (Task Scheduler Action):
'   Execute:    wscript.exe
'   Arguments:  "D:\ZephyrAlpha\scripts\launch_hidden.vbs" "<ps1 full path>"
'
' 等待策略: True (等待子进程退出)
'   guard 脚本是 while-true 常驻, wscript 随之常驻; guard 崩溃 => wscript 返回其退出码
'   => Task Scheduler 检测失败 => RestartOnFailure 触发。与原 powershell 直接常驻行为
'   一致, 且避免 wscript 立即退出导致 Task Scheduler job object 误杀孙进程 guard。
' ============================================================================
Option Explicit
Dim sh, ps1Path, cmd
If WScript.Arguments.Count < 1 Then WScript.Quit(1)
ps1Path = WScript.Arguments(0)
Set sh = CreateObject("WScript.Shell")
cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & ps1Path & """"
' 0 = SW_HIDE (隐藏窗口), True = 等待子进程退出 (guard 常驻则 wscript 常驻)
sh.Run cmd, 0, True
Set sh = Nothing
