import os
import re

BLUEPRINTS_DIR = r"d:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS"
INDEX_FILE = os.path.join(BLUEPRINTS_DIR, "INDEX.md")

MODULE_ID_MAPPING = {
    "IMPL_DATA_VERSION_CTRL_BP_001": "DATA_VERSION_CONTROL_001",
    "IMPL_DATA_LIFECYCLE_BP_001": "DATA_LIFECYCLE_MANAGEMENT_001",
    "IMPL_DATA_OBSERVABILITY_BP_001": "DATA_OBSERVABILITY_001",
    "IMPL_PORTFOLIO_REBAL_BP_001": "PORTFOLIO_REBALANCING_001",
    "IMPL_DATA_GOVERNANCE_BP_001": "DATA_GOVERNANCE_PLATFORM_001",
    "IMPL_DATA_FABRIC_BP_001": "DATA_FABRIC_001",
    "IMPL_DATA_MESH_BP_001": "DATA_MESH_001",
    "IMPL_STRATEGIC_WEIGHTING_BP_001": "STRATEGIC_WEIGHTING_001",
    "IMPL_STRESS_TESTING_BP_001": "STRESS_TESTING_SYSTEM_001",
    "IMPL_RISK_CONTROL_BP_001": "RISK_CONTROL_001",
    "IMPL_QUALITY_SCORING_BP_001": "QUALITY_SCORING_SYSTEM_001",
    "IMPL_QUARTERLY_REBALANCE_BP_001": "QUARTERLY_REBALANCE_001",
    "IMPL_REALTIME_DATA_LAKE_BP_001": "REALTIME_DATA_LAKE_001",
    "IMPL_QUALITY_REPORT_AUTO_BP_001": "QUALITY_REPORT_AUTOMATION_001",
    "IMPL_INTRADAY_STRATEGY_BP_001": "INTRADAY_STRATEGY_001",
    "IMPL_OPENING_STRATEGY_BP_001": "OPENING_STRATEGY_001",
    "IMPL_BARRA_RISK_MODEL_BP_001": "BARRA_RISK_MODEL_001",
    "IMPL_SIMPLIFIED_TIMEFRAME_COORD_BP_001": "SIMPLIFIED_TIMEFRAME_COORDINATION_001",
    "IMPL_ALPHA_FACTOR_FACTORY_BP_001": "ALPHA_FACTOR_FACTORY_001",
    "IMPL_AUTO_REPAIR_ENGINE_BP_001": "AUTO_REPAIR_ENGINE_001",
    "IMPL_MARKET_REGIME_DETECTION_BP_001": "MARKET_REGIME_DETECTION_001",
    "IMPL_DATA_QUALITY_MONITORING_BP_001": "DATA_QUALITY_MONITORING_001",
    "IMPL_DATA_CATALOG_METADATA_BP_001": "DATA_CATALOG_METADATA_001",
    "IMPL_UNIFIED_DATA_INFRASTRUCTURE_BP_001": "UNIFIED_DATA_INFRASTRUCTURE_001",
    "IMPL_TRADING_COST_OPT_BP_001": "TRADING_COST_OPTIMIZATION_001",
    "IMPL_TAIL_RISK_HEDGE_BP_001": "TAIL_RISK_HEDGING_001",
    "IMPL_STATISTICAL_ARBITRAGE_BP_001": "STATISTICAL_ARBITRAGE_MODULE_001",
    "IMPL_SMART_EXECUTION_BP_001": "SMART_EXECUTION_ENGINE_001",
    "IMPL_RL_REBALANCING_BP_001": "RL_REBALANCING_SYSTEM_001",
    "IMPL_RISK_ATTRIBUTION_BP_001": "RISK_ATTRIBUTION_SYSTEM_001",
    "IMPL_REALTIME_RISK_HEDGE_BP_001": "REALTIME_RISK_HEDGE_ENGINE_001",
    "IMPL_PORTFOLIO_INSURANCE_BP_001": "PORTFOLIO_INSURANCE_STRATEGY_001",
    "IMPL_MULTI_STRATEGY_HIER_BP_001": "MULTI_STRATEGY_HIERARCHICAL_SYSTEM_001",
    "IMPL_MODULE_RESPONSIBILITY_BP_001": "MODULE_RESPONSIBILITY_BOUNDARIES_001",
    "IMPL_MARKET_IMPACT_BP_001": "MARKET_IMPACT_MODEL_001",
    "IMPL_LIQUIDITY_MGMT_BP_001": "LIQUIDITY_MANAGEMENT_SYSTEM_001",
    "IMPL_FINANCING_OPT_BP_001": "FINANCING_OPTIMIZATION_001",
    "IMPL_ECONOMIC_REGIME_BP_002": "ECONOMIC_REGIME_ENGINE_002",
    "IMPL_DYNAMIC_LEVERAGE_BP_001": "DYNAMIC_LEVERAGE_MANAGEMENT_001",
    "IMPL_DYNAMIC_CORRELATION_BP_001": "DYNAMIC_CORRELATION_MODELING_001",
    "IMPL_DATA_CATALOG_BP_001": "DATA_CATALOG_001",
    "IMPL_ALTERNATIVE_DATA_BP_001": "ALTERNATIVE_DATA_INTEGRATION_001",
    "IMPL_AI_PATTERN_RECOGNITION_BP_001": "AI_PATTERN_RECOGNITION_ENGINE_001",
}

def update_blueprint_file(filepath, old_id, new_id):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content.replace(f"module_id: {old_id}", f"module_id: {new_id}")
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def update_index_file():
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old_id, new_id in MODULE_ID_MAPPING.items():
        new_content = new_content.replace(old_id, new_id)
    
    if new_content != content:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    updated_count = 0
    
    for filename in os.listdir(BLUEPRINTS_DIR):
        if filename.endswith('.md') and filename != 'INDEX.md':
            filepath = os.path.join(BLUEPRINTS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for old_id, new_id in MODULE_ID_MAPPING.items():
                if f"module_id: {old_id}" in content:
                    if update_blueprint_file(filepath, old_id, new_id):
                        print(f"[OK] {filename}: {old_id} -> {new_id}")
                        updated_count += 1
                    break
    
    if update_index_file():
        print(f"[OK] INDEX.md updated")
    
    print(f"\nTotal files updated: {updated_count}")

if __name__ == "__main__":
    main()
