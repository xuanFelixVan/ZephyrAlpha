$file = "d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\40_execution_broker.md"
$patterns = @('Barzykin', 'Hawkes', 'passive impact', 'Passive Market', 'Point Process', 'self-exciting', 'fill probability', 'exponential decay', 'SquareRoot', 'square root', 'Bouchaud', 'Propagator', 'MPC', 'Model Predictive', 'SOR', 'Smart Order', (-join [char[]](0x8BA2,0x5355,0x8DEF,0x7531)))
$lines = Get-Content $file -Encoding UTF8
for ($i = 0; $i -lt $lines.Count; $i++) {
    foreach ($p in $patterns) {
        if ($lines[$i] -match [regex]::Escape($p)) {
            $snippet = $lines[$i]
            if ($snippet.Length -gt 220) { $snippet = $snippet.Substring(0, 220) }
            Write-Output "L$($i+1) [$p]: $snippet"
            break
        }
    }
}
