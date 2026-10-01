$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dir = 'd:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos'

$checks = @{
    '37_liquidity_crisis_protocol.md' = @('microstructure', '2604.20949', 'lead-time', 'latent')
    '55_monitoring_review.md' = @('Berry Phase', '2605.17117', 'geometric observable', 'Spectral Entropy', '2603.04441')
    '30_multi_strategy_concurrency.md' = @('Morwane', 'multi-strategy-alpha-book', 'inverse-vol')
    '36_var_es_monitoring.md' = @('CAESar', 'CAViaR', '2606.23492', 'BAWS', '2603.01157')
    '31_position_sizing.md' = @('BlackRock', '2603.01298', 'proportional control')
    '40_execution_broker.md' = @('2601.03215', 'market resistance', 'Fredholm')
}

foreach ($filename in $checks.Keys) {
    $file = Join-Path $dir $filename
    if (-not (Test-Path $file)) { continue }
    $content = Get-Content $file -Encoding UTF8 -Raw
    $found = @()
    foreach ($kw in $checks[$filename]) {
        if ($content -like "*$kw*") {
            $found += $kw
        }
    }
    if ($found.Count -gt 0) {
        Write-Output "COVERED: $filename -> $($found -join ', ')"
    } else {
        Write-Output "MISSING: $filename -> none of $($checks[$filename] -join ', ')"
    }
}
