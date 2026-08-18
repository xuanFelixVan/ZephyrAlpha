$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dir = 'd:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos'
$targets = @('55_monitoring_review.md', '31_position_sizing.md', '40_execution_broker.md')
foreach ($t in $targets) {
    $file = Join-Path $dir $t
    $lines = Get-Content $file -Encoding UTF8
    Write-Output "=== $t ($($lines.Count) lines) ==="
    # Find key sections
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^## 8\.|^### 8\.|^## 9\.|\u4FEE\u8BA2\u8BB0\u5F55') {
            $line = $lines[$i]
            if ($line.Length -gt 100) { $line = $line.Substring(0, 100) }
            Write-Output ("  L" + ($i+1) + ": " + $line)
        }
    }
    # Find last revision record
    $lastRev = 0
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^\| 2026-08') { $lastRev = $i }
    }
    if ($lastRev -gt 0) {
        $line = $lines[$lastRev]
        if ($line.Length -gt 120) { $line = $line.Substring(0, 120) + '...' }
        Write-Output ("  Last revision L" + ($lastRev+1) + ": " + $line)
    }
    Write-Output ""
}
