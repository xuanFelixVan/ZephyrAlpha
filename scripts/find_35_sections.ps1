$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$file = 'd:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\35_drawdown_protocol_impl.md'
$lines = Get-Content $file -Encoding UTF8
Write-Output ("Total lines: " + $lines.Count)
# Find key sections
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^## \d|^### \d|MaxDD.*threshold|\u56DE\u64A4\u9608\u503C|keep-or-kill| Sharpe.*drawdown|\u67E5\u627E\u8868|lookup') {
        $line = $lines[$i]
        if ($line.Length -gt 120) { $line = $line.Substring(0, 120) + '...' }
        Write-Output ("L" + ($i+1) + ": " + $line)
    }
}
