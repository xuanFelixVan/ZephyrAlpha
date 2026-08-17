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

Check-Coverage '35_drawdown_protocol_impl.md' @('Brownian', '\u975E\u9AD8\u65AF', '\u5206\u6570\u5E03\u6717', '\u957F\u8BB0\u5FC6', 'Rej-Seager', '\u67E5\u627E\u8868')
Check-Coverage '37_liquidity_crisis_protocol.md' @('microstructure', 'latent.*build', 'lead-time', '\u9690\u542B.*build')
Check-Coverage '55_monitoring_review.md' @('Berry Phase', 'geometric observable', '\u51E0\u4F55\u53EF\u89C2', 'Spectral Entropy')
Check-Coverage '30_multi_strategy_concurrency.md' @('inverse-vol', 'Morwane', 'multi-strategy-alpha-book')
Check-Coverage '37_liquidity_crisis_protocol.md' @('\u7EDF\u8BA1\u8DF3\u8DC3', 'Statistical Jump', 'DD_10', '\u4E2D\u91D1')
Check-Coverage '36_var_es_monitoring.md' @('CAESar', 'CAViaR.*ES', 'Conditional Autoregressive ES')
Check-Coverage '36_var_es_monitoring.md' @('BAWS', 'Adaptive Window', 'bootstrap.*window', '\u81EA\u9002\u5E94\u7A97\u53E3')
Check-Coverage '31_position_sizing.md' @('BlackRock', 'proportional control', '\u6BD4\u4F8B\u63A7\u5236')
Check-Coverage '40_execution_broker.md' @('market resistance', '\u5E02\u573A\u963B\u529B', 'Fredholm')
Check-Coverage '36_var_es_monitoring.md' @('2608.00127', '2608.04987', '2608.04305')
Check-Coverage '55_monitoring_review.md' @('2605.17117', '2603.04441')
