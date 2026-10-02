$file = "d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos\31_position_sizing.md"
$patterns = @('Conformal', 'Bayesian Kelly', 'Sukhov', 'DRO', 'Distributional Robust', 'HRP', 'Hierarchical Risk', 'MFCCA', 'Kakinaka', 'Lopez de Prado', 'Ledoit', 'shrinkage', 'Ryan', '2608.01494', 'Xing', 'risk parity')
$lines = Get-Content $file -Encoding UTF8
for ($i = 0; $i -lt $lines.Count; $i++) {
    foreach ($p in $patterns) {
        if ($lines[$i] -match [regex]::Escape($p)) {
            $snippet = $lines[$i]
            if ($snippet.Length -gt 200) { $snippet = $snippet.Substring(0, 200) }
            Write-Output "L$($i+1) [$p]: $snippet"
            break
        }
    }
}
