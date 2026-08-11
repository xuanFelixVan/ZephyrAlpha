$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dir = 'd:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos'

# Check if key findings are already covered
$checks = @(
    @{file='35_drawdown_protocol_impl.md'; keywords='Brownian|非高斯|分数布朗|长记忆|Rej-Seager|RSB|查找表|lookup table|drawdown.*beyond'},
    @{file='37_liquidity_crisis_protocol.md'; keywords='microstructure|LOB|latent.*build|lead-time|隐含.*build|盘前.*检测'},
    @{file='55_monitoring_review.md'; keywords='Berry Phase|geometric observable|几何可观|Spectral Entropy|spectral embedding'},
    @{file='30_multi_strategy_concurrency.md'; keywords='inverse-vol|inverse volatility|risk parity.*book|Morwane|multi-strategy-alpha-book'},
    @{file='37_liquidity_crisis_protocol.md'; keywords='统计跳跃|Statistical Jump|DD_10|Sortino_20|中金'},
    @{file='36_var_es_monitoring.md'; keywords='CAESar|CAViaR.*ES|Conditional Autoregressive ES'},
    @{file='36_var_es_monitoring.md'; keywords='BAWS|Adaptive Window|bootstrap.*window|自适应窗口'},
    @{file='31_position_sizing.md'; keywords='BlackRock|proportional control|vol target.*反馈|比例控制'},
    @{file='40_execution_broker.md'; keywords='market resistance|市场阻力|concave.*impact|Fredholm'}
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
