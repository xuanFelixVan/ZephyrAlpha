$file = "d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\40_execution_broker.md"
$patterns = @('Barzykin', '2607.28323', 'passive market impact', 'Passive Market', 'fill prob', 'quote distance', 'Hawkes', 'self-exciting', 'limit-order fill', 'limit order fill')
$lines = Get-Content $file -Encoding UTF8
$found = $false
for ($i = 0; $i -lt $lines.Count; $i++) {
    foreach ($p in $patterns) {
        if ($lines[$i] -match [regex]::Escape($p)) {
            $snippet = $lines[$i]
            if ($snippet.Length -gt 220) { $snippet = $snippet.Substring(0, 220) }
            Write-Output "L$($i+1) [$p]: $snippet"
            $found = $true
            break
        }
    }
}
if (-not $found) {
    Write-Output "NONE FOUND"
}
# Also check S7.4 area (around L1040-1080)
Write-Output "`n=== Lines 1040-1090 ==="
for ($i = 1040; $i -lt 1090 -and $i -lt $lines.Count; $i++) {
    if ($lines[$i].Length -gt 0) {
        $snip = $lines[$i]
        if ($snip.Length -gt 200) { $snip = $snip.Substring(0, 200) }
        Write-Output "L$($i+1): $snip"
    }
}
