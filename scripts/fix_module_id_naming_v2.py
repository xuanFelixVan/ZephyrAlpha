import os
import re

BLUEPRINTS_DIR = r"d:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS"

MODULE_ID_MAPPING = {
    "IMPL_HIGH_PERF_PIPELINE_BP_001": "HIGH_PERFORMANCE_DATA_PIPELINE_001",
    "IMPL_DATA_SECURITY_BP_001": "DATA_SECURITY_COMPLIANCE_001",
    "IMPL_DATA_SOURCE_MGMT_BP_001": "DATA_SOURCE_MANAGEMENT_001",
    "SMART_ORDER_ROUTER_BLUEPRINT_001": "SMART_ORDER_ROUTER_001",
    "TRADING_SIGNAL_VALIDATOR_BLUEPRINT_001": "TRADING_SIGNAL_VALIDATOR_001",
    "ALGORITHMIC_TRADING_OPTIMIZER_BLUEPRINT_001": "ALGORITHMIC_TRADING_OPTIMIZER_001",
    "TRANSACTION_COST_ANALYSIS_ENGINE_BLUEPRINT_001": "TRANSACTION_COST_ANALYSIS_ENGINE_001",
    "EXECUTION_STRATEGY_BACKTESTER_BLUEPRINT_001": "EXECUTION_STRATEGY_BACKTESTER_001",
    "LAYER7_INTEGRATION_BLUEPRINT_001": "SYSTEM_INTEGRATION_001",
    "LAYER7_ENHANCEMENT_BLUEPRINT_001": "SYSTEM_ENHANCEMENT_001",
    "STRATEGIC_ALLOCATION_ENGINE_BLUEPRINT_001": "STRATEGIC_ALLOCATION_ENGINE_001",
    "MONITORING_DASHBOARD_ENHANCEMENT_BLUEPRINT_001": "MONITORING_DASHBOARD_ENHANCEMENT_001",
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
    
    print(f"\nTotal files updated: {updated_count}")

if __name__ == "__main__":
    main()
