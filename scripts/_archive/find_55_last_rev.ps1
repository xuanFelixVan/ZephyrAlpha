$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$file = 'd:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\55_monitoring_review.md'
$lines = Get-Content $file -Encoding UTF8
Write-Output ("Total lines: " + $lines.Count)
$lastRev = 0
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\| 2026-08') { $lastRev = $i }
}
if ($lastRev -gt 0) {
    $line = $lines[$lastRev]
    if ($line.Length -gt 120) { $line = $line.Substring(0, 120) + '...' }
    Write-Output ("Last revision L" + ($lastRev+1) + ": " + $line)
}
