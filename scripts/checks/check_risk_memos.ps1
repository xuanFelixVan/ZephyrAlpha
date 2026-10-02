$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dir = 'd:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos'
$targets = @('31_position_sizing', '33_budget_change_handler', '35_drawdown_protocol_impl', '36_var_es_monitoring')
foreach ($t in $targets) {
    $file = Join-Path $dir "$t.md"
    if (Test-Path $file) {
        Write-Output "=== $t ==="
        $lines = Get-Content $file -Encoding UTF8
        # Find revision records
        $inRevision = $false
        $count = 0
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match '## \d+\. \u4FEE\u8BA2\u8BB0\u5F55') { $inRevision = $true }
            if ($inRevision -and $lines[$i] -match '^\| 2026-08') {
                $line = $lines[$i]
                if ($line.Length -gt 200) { $line = $line.Substring(0, 200) + '...' }
                Write-Output ("  L" + ($i+1) + ": " + $line)
                $count++
            }
        }
        Write-Output ("  Total revisions: $count")
        Write-Output ""
    }
}
