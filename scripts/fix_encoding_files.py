# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# -*- coding: utf-8 -*-
"""
修复编码问题文件的YAML头部
"""

import os
import re
from pathlib import Path

def fix_yaml_header(filepath, new_yaml):
    """修复文件的YAML头部"""
    try:
        # 读取文件内容
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 查找YAML块（更宽松的匹配）
        yaml_pattern = r'^---\n.*?\n---'
        match = re.search(yaml_pattern, content, re.DOTALL)
        
        if match:
            # 替换YAML块
            new_content = new_yaml + content[match.end():]
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True, "YAML头部已修复"
        else:
            # 如果没有找到YAML块，直接在文件开头添加
            new_content = new_yaml + "\n" + content
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True, "YAML头部已添加"
    except Exception as e:
        return False, f"错误: {str(e)}"

def main():
    """主函数"""
    base_path = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")
    
    # 需要修复的文件列表
    files_to_fix = {
        "BARRA_RISK_MODEL_BLUEPRINT.md": """---
module_id: IMPL_BARRA_RISK_MODEL_BP_001
version: 1.0.2
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: 2026-04-06
created_date: 2026-04-03
layer: "Layer 6 (组合优化层)"
index: BARRA_RISK_MODEL_001
estimated_hours: 100h
estimated_effort: 2.5周
review_status: Pending
reviewer: 首席技术评审官
review_date: 2026-04-03
owner: 组合优化层负责人
standard_type: 专业量化机构蓝图文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
personal_development: true
ai_maintenance: true
open_source_dependency: numpy, pandas, scipy
priority: P0
---""",
        
        "SIMPLIFIED_RISK_BUDGET_SYSTEM_BLUEPRINT.md": """---
module_id: IMPL_SIMPLIFIED_RISK_BUDGET_BP_001
version: 1.0.1
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: 2026-04-06
created_date: 2026-04-03
layer: "Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构"
index: SIMPLIFIED_RISK_BUDGET_SYSTEM_001
estimated_hours: 60h
estimated_effort: 1.5周
review_status: Pending
reviewer: 首席技术评审官
review_date: 2026-04-03
owner: 组合优化层负责人
standard_type: 专业量化机构蓝图文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
personal_development: true
ai_maintenance: true
simplified_version: true
open_source_dependency: numpy, pandas, scipy
priority: P0
---""",
        
        "SIMPLIFIED_TIMEFRAME_COORDINATION_BLUEPRINT.md": """---
module_id: IMPL_SIMPLIFIED_TIMEFRAME_BP_001
version: 1.0.1
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: 2026-04-06
created_date: 2026-04-03
layer: "Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构"
index: SIMPLIFIED_TIMEFRAME_COORDINATION_001
estimated_hours: 60h
estimated_effort: 1.5周
review_status: Pending
reviewer: 首席技术评审官
review_date: 2026-04-03
owner: 组合优化层负责人
standard_type: 专业量化机构蓝图文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
personal_development: true
ai_maintenance: true
simplified_version: true
open_source_dependency: numpy, pandas, scipy
priority: P0
---""",
        
        "STRESS_TESTING_SYSTEM_BLUEPRINT.md": """---
module_id: IMPL_STRESS_TESTING_BP_001
version: 1.0.1
spec_version: 1.0
status: Active
parent_doc: ../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md
last_updated: 2026-04-06
created_date: 2026-04-03
layer: "Layer 7 (风险控制层)"
index: STRESS_TESTING_SYSTEM_001
estimated_hours: 80h
estimated_effort: 2周
review_status: Pending
reviewer: 首席技术评审官
review_date: 2026-04-03
owner: 组合优化层负责人
standard_type: 专业量化机构蓝图文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
open_source_dependency: numpy, pandas, scipy
priority: P1
---""",
        
        "REALTIME_QUALITY_MONITOR_BLUEPRINT.md": """---
module_id: IMPL_REALTIME_QUALITY_MONITOR_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy, great_expectations
estimated_effort: 2周
priority: P0
---""",
        
        "AUTO_REPAIR_ENGINE_BLUEPRINT.md": """---
module_id: IMPL_AUTO_REPAIR_ENGINE_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy
estimated_effort: 2周
priority: P0
---""",
        
        "DATA_COST_MANAGEMENT_BLUEPRINT.md": """---
module_id: IMPL_DATA_COST_MGMT_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy
estimated_effort: 1.5周
priority: P1
---""",
        
        "DATA_FABRIC_BLUEPRINT.md": """---
module_id: IMPL_DATA_FABRIC_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy, dask
estimated_effort: 3周
priority: P1
---""",
        
        "DATA_LIFECYCLE_MANAGEMENT_BLUEPRINT.md": """---
module_id: IMPL_DATA_LIFECYCLE_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy
estimated_effort: 2周
priority: P1
---""",
        
        "DATA_LINEAGE_TRACKING_BLUEPRINT.md": """---
module_id: IMPL_DATA_LINEAGE_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy, openlineage
estimated_effort: 2周
priority: P1
---""",
        
        "DATA_MESH_BLUEPRINT.md": """---
module_id: IMPL_DATA_MESH_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy, dask
estimated_effort: 3周
priority: P1
---""",
        
        "DATA_SECURITY_COMPLIANCE_BLUEPRINT.md": """---
module_id: IMPL_DATA_SECURITY_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy
estimated_effort: 2周
priority: P0
---""",
        
        "DATA_SOURCE_MANAGEMENT_BLUEPRINT.md": """---
module_id: IMPL_DATA_SOURCE_MGMT_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy
estimated_effort: 1.5周
priority: P1
---""",
        
        "DATA_VIRTUALIZATION_BLUEPRINT.md": """---
module_id: IMPL_DATA_VIRTUALIZATION_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy, dask
estimated_effort: 2周
priority: P1
---""",
        
        "HIGH_PERFORMANCE_DATA_PIPELINE_BLUEPRINT.md": """---
module_id: IMPL_HIGH_PERF_PIPELINE_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy, dask, ray
estimated_effort: 3周
priority: P0
---""",
        
        "MODULE_RESPONSIBILITY_BOUNDARIES_BLUEPRINT.md": """---
module_id: IMPL_MODULE_RESPONSIBILITY_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: None
estimated_effort: 1周
priority: P1
---""",
        
        "QUALITY_REPORT_AUTOMATION_BLUEPRINT.md": """---
module_id: IMPL_QUALITY_REPORT_AUTO_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy, jinja2
estimated_effort: 1.5周
priority: P1
---""",
        
        "QUALITY_SCORING_SYSTEM_BLUEPRINT.md": """---
module_id: IMPL_QUALITY_SCORING_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy
estimated_effort: 1.5周
priority: P1
---""",
        
        "REALTIME_DATA_LAKE_BLUEPRINT.md": """---
module_id: IMPL_REALTIME_DATA_LAKE_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-02
last_updated: 2026-04-06
owner: 首席技术评审官
standard_type: 专业量化机构蓝图
applicable_scope: "Layer 1数据预处理层 | 业务架构: 三级时间框架融合架构"
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
implementation_progress: 0%
open_source_dependency: pandas, numpy, delta-lake
estimated_effort: 3周
priority: P0
---""",
    }
    
    print("开始修复编码问题文件...")
    
    for filename, new_yaml in files_to_fix.items():
        filepath = base_path / filename
        if filepath.exists():
            success, message = fix_yaml_header(filepath, new_yaml)
            status = "[OK]" if success else "[ERROR]"
            print(f"{status} {filename}: {message}")
        else:
            print(f"[SKIP] {filename}: 文件不存在")
    
    print("\n修复完成!")

if __name__ == "__main__":
    main()
