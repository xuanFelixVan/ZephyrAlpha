# register_desktop_shell_startup.ps1
# Purpose: Register the ZephyrAlpha Electron desktop shell to start at user logon
#          (ruling #374 topic 5 plan B). Creates a .lnk shortcut in the user
#          Startup folder pointing at the local Electron binary. The shell's
#          main process (tools/desktop/main.js) already auto-spawns and reuses
#          the 8890 api_server and the 8765 serve_docs backend, so one shortcut
#          covers the whole "shell + services" chain (ensureApi/ensureDocs).
# Usage:   powershell -ExecutionPolicy Bypass -File scripts\register_desktop_shell_startup.ps1
# Idempotent: re-running recreates the same .lnk (overwrite = update in place).
# Rollback: delete "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ZephyrAlpha Dashboard.lnk"
# Note: this file must stay pure ASCII (Windows PowerShell 5.1 GBK decode rule).

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$electron = Join-Path $repoRoot 'tools\desktop\node_modules\electron\dist\electron.exe'
$appDir = Join-Path $repoRoot 'tools\desktop'

if (-not (Test-Path $electron)) {
    Write-Error "electron.exe not found at $electron - run npm install in tools\desktop first"
    exit 1
}

$startupFolder = [Environment]::GetFolderPath('Startup')
$lnkPath = Join-Path $startupFolder 'ZephyrAlpha Dashboard.lnk'

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($lnkPath)
$shortcut.TargetPath = $electron
$shortcut.Arguments = '.'
$shortcut.WorkingDirectory = $appDir
$shortcut.Description = 'ZephyrAlpha Dashboard desktop shell (auto-spawns api_server 8890 + serve_docs 8765)'
$shortcut.WindowStyle = 1
$shortcut.Save()

Write-Output "CREATED: $lnkPath"
Write-Output "TARGET : $electron"
Write-Output "ARGS   : .  (app dir = $appDir)"

# Verify by reading the shortcut back
$check = $shell.CreateShortcut($lnkPath)
if ($check.TargetPath -eq $electron -and $check.WorkingDirectory -eq $appDir) {
    Write-Output 'VERIFY : OK (target and working directory read back correctly)'
    exit 0
} else {
    Write-Error "VERIFY : FAILED (target=$($check.TargetPath) workdir=$($check.WorkingDirectory))"
    exit 1
}
