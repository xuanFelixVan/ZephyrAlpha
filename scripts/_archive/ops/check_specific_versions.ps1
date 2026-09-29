$dir = "d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos"
$targets = @(
    "54_reconciliation_attribution.md",
    "53_simulation_live_path.md",
    "61_lifecycle_multi_ai.md",
    "30_multi_strategy_concurrency.md",
    "20_first_batch_strategies.md",
    "21_stock_selection_engine.md",
    "22_sector_rotation_spec.md",
    "23_strategy_correlation_validation.md",
    "26_event_driven_strategy_detail.md",
    "31_position_sizing.md",
    "32_firm_risk_aggregator.md",
    "35_drawdown_protocol_impl.md",
    "36_var_es_monitoring.md",
    "01_design_memo_management_spec.md",
    "10_regime_detector_spec.md",
    "11_regime_backtest_validation_plan.md",
    "13_regime_phase3_engineering_plan.md",
    "15_data_feature_layer_spec.md"
)

Write-Output "=== Actual frontmatter versions ==="
foreach ($t in $targets) {
    $p = Join-Path $dir $t
    if (Test-Path $p) {
        $content = Get-Content $p -Raw
        if ($content -match '(?m)^version:\s*([^\s\r\n]+)') {
            $v = $matches[1].Trim()
            Write-Output "$t => $v"
        } else {
            Write-Output "$t => NO version field"
        }
    } else {
        Write-Output "$t => FILE NOT FOUND"
    }
}
