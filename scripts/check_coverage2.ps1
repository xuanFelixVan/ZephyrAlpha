$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dir = 'd:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos'

function Check-Coverage($filename, $keywordArray) {
    $file = Join-Path $dir $filename
    if (-not (Test-Path $file)) { return }
    $content = Get-Content $file -Encoding UTF8 -Raw
    foreach ($kw in $keywordArray) {
        if ($content -match $kw) {
            Write-Output "COVERED: $filename has [$kw]"
            return
        }
    }
    Write-Output "MISSING: $filename does NOT have any of $keywordArray"
}

Check-Coverage '35_drawdown_protocol_impl.md' @('Brownian', '非高斯', '分数布朗', '长记忆', 'Rej-Seager', '查找表')
Check-Coverage '37_liquidity_crisis_protocol.md' @('microstructure', 'latent.*build', 'lead-time', '隐含.*build')
Check-Coverage '55_monitoring_review.md' @('Berry Phase', 'geometric observable', '几何可观', 'Spectral Entropy')
Check-Coverage '30_multi_strategy_concurrency.md' @('inverse-vol', 'Morwane', 'multi-strategy-alpha-book')
Check-Coverage '37_liquidity_crisis_protocol.md' @('统计跳跃', 'Statistical Jump', 'DD_10', '中金')
Check-Coverage '36_var_es_monitoring.md' @('CAESar', 'CAViaR.*ES', 'Conditional Autoregressive ES')
Check-Coverage '36_var_es_monitoring.md' @('BAWS', 'Adaptive Window', 'bootstrap.*window', '自适应窗口')
Check-Coverage '31_position_sizing.md' @('BlackRock', 'proportional control', '比例控制')
Check-Coverage '40_execution_broker.md' @('market resistance', '市场阻力', 'Fredholm')
Check-Coverage '36_var_es_monitoring.md' @('2608.00127', '2608.04987', '2608.04305')
Check-Coverage '55_monitoring_review.md' @('2605.17117', '2603.04441')
