# archive_minidumps.ps1 - Preserve Windows crash dumps before cleanup tools delete them.
# Trigger: scheduled task on WER-SystemErrorReporting event 1001 (bugcheck) + system boot.
# English comments only (PS5.1 misreads CJK comments in no-BOM UTF-8).

$ErrorActionPreference = 'Continue'
$dest = 'D:\ZephyrAlpha\data\diagnostics\minidumps'
$log  = Join-Path $dest 'archive.log'
$keepLatest = 20

try {
    if (-not (Test-Path $dest)) { New-Item -ItemType Directory -Path $dest -Force | Out-Null }

    $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $sources = @()
    if (Test-Path 'C:\Windows\Minidump') {
        $sources += Get-ChildItem 'C:\Windows\Minidump\*.dmp' -ErrorAction SilentlyContinue
    }
    if (Test-Path 'C:\Windows\MEMORY.DMP') {
        $sources += Get-Item 'C:\Windows\MEMORY.DMP' -ErrorAction SilentlyContinue
    }

    $copied = 0
    foreach ($f in $sources) {
        $target = Join-Path $dest ("{0}_{1}" -f $stamp, $f.Name)
        if (-not (Test-Path $target)) {
            Copy-Item $f.FullName $target -Force -ErrorAction SilentlyContinue
            if (Test-Path $target) { $copied++ }
        }
    }

    # Retention: keep newest N dumps
    $all = Get-ChildItem (Join-Path $dest '*.dmp') -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    if ($all.Count -gt $keepLatest) {
        $all | Select-Object -Skip $keepLatest | Remove-Item -Force -ErrorAction SilentlyContinue
    }

    $msg = "{0} sources={1} copied={2} total_kept={3}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $sources.Count, $copied, ([math]::Min($all.Count, $keepLatest))
    Add-Content -Path $log -Value $msg -Encoding UTF8
} catch {
    try { Add-Content -Path $log -Value ("{0} ERROR: {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $_.Exception.Message) -Encoding UTF8 } catch {}
}
