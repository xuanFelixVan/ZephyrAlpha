$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dir = 'd:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos'

# Check if key findings are already covered.
# CJK terms are written as .NET regex XXXX escapes (ASCII-only source, gate INJ-007).
$checks = @(
    @{file='35_drawdown_protocol_impl.md'; keywords='Brownian|\u975E\u9AD8\u65AF|\u5206\u6570\u5E03\u6717|\u957F\u8BB0\u5FC6|Rej-Seager|RSB|\u67E5\u627E\u8868|lookup table|drawdown.*beyond'},
    @{file='37_liquidity_crisis_protocol.md'; keywords='microstructure|LOB|latent.*build|lead-time|\u9690\u542B.*build|\u76D8\u524D.*\u68C0\u6D4B'},
    @{file='55_monitoring_review.md'; keywords='Berry Phase|geometric observable|\u51E0\u4F55\u53EF\u89C2|Spectral Entropy|spectral embedding'},
    @{file='30_multi_strategy_concurrency.md'; keywords='inverse-vol|inverse volatility|risk parity.*book|Morwane|multi-strategy-alpha-book'},
    @{file='37_liquidity_crisis_protocol.md'; keywords='\u7EDF\u8BA1\u8DF3\u8DC3|Statistical Jump|DD_10|Sortino_20|\u4E2D\u91D1'},
    @{file='36_var_es_monitoring.md'; keywords='CAESar|CAViaR.*ES|Conditional Autoregressive ES'},
    @{file='36_var_es_monitoring.md'; keywords='BAWS|Adaptive Window|bootstrap.*window|\u81EA\u9002\u5E94\u7A97\u53E3'},
    @{file='31_position_sizing.md'; keywords='BlackRock|proportional control|vol target.*\u53CD\u9988|\u6BD4\u4F8B\u63A7\u5236'},
    @{file='40_execution_broker.md'; keywords='market resistance|\u5E02\u573A\u963B\u529B|concave.*impact|Fredholm'}
)

foreach ($c in $checks) {
    $file = Join-Path $dir $c.file
    if (Test-Path $file) {
        $content = Get-Content $file -Encoding UTF8 -Raw
        $found = $false
        foreach ($kw in $c.keywords -split '\|') {
            if ($content -match $kw) {
                $found = $true
                Write-Output ("COVERED: $($c.file) has [$kw]")
                break
            }
        }
        if (-not $found) {
            Write-Output ("MISSING: $($c.file) does NOT have any of [$($c.keywords)]")
        }
    }
}
