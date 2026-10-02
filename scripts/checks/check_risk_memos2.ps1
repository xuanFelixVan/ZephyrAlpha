$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dir = 'd:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos'
$targets = @('35_drawdown_protocol_impl', '36_var_es_monitoring', '31_position_sizing', '33_budget_change_handler')
foreach ($t in $targets) {
    $file = Join-Path $dir "$t.md"
    if (Test-Path $file) {
        $lines = Get-Content $file -Encoding UTF8
        Write-Output ("=== $t (total $($lines.Count) lines) ===")
        # Find last 5 non-empty lines
        $lastLines = @()
        for ($i = $lines.Count - 1; $i -ge 0 -and $lastLines.Count -lt 3; $i--) {
            if ($lines[$i].Trim() -ne '') { $lastLines = @($lines[$i]) + $lastLines }
        }
        foreach ($ll in $lastLines) {
            $s = $ll
            if ($s.Length -gt 150) { $s = $s.Substring(0, 150) + '...' }
            Write-Output "  $s"
        }
        # Find revision section
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match '\u4FEE\u8BA2|revision|\u53D8\u66F4|\u66F4\u65B0\u8BB0\u5F55') {
                $s = $lines[$i]
                if ($s.Length -gt 100) { $s = $s.Substring(0, 100) + '...' }
                Write-Output ("  Revision section at L" + ($i+1) + ": " + $s)
                break
            }
        }
        Write-Output ""
    }
}
