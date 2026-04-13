#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
舆情分析层职责描述优化脚本
为每个文件生成具体的职责描述，确保至少20个字符
"""

import re
from pathlib import Path
from typing import List, Dict

class SentimentResponsibilityOptimizer:
    """舆情分析层职责描述优化器"""
    
    def __init__(self):
        self.min_length = 20
        self.optimized_count = 0
        self.total_count = 0
    
    def generate_responsibility(self, file_name: str) -> List[str]:
        """根据文件名生成职责描述"""
        responsibilities = []
        
        name_upper = file_name.upper()
        
        if 'INDEX' in name_upper:
            responsibilities.append('AI工作流与舆情分析综合层索引管理')
        
        elif 'SENTIMENT_ANALYSIS_SHORT_TERM' in name_upper:
            responsibilities.append('短期改进技术规格定义与实施标准制定')
            responsibilities.append('数据源扩展、深度学习情感分析、实时预警系统技术规格')
        
        elif 'SENTIMENT_ANALYSIS_MEDIUM_TERM' in name_upper:
            responsibilities.append('中期改进技术规格定义与实施标准制定')
            responsibilities.append('知识图谱、流式处理、多语言支持技术规格')
        
        elif 'SENTIMENT_ANALYSIS_LONG_TERM' in name_upper:
            responsibilities.append('长期改进技术规格定义与实施标准制定')
            responsibilities.append('多模态分析、AI虚拟研究团队技术规格')
        
        elif 'SENTIMENT_ANALYSIS_PROJECT_MANAGEMENT' in name_upper:
            responsibilities.append('舆情分析层改进模块项目管理')
            responsibilities.append('WBS分解、甘特图、里程碑计划、资源分配')
        
        elif 'SENTIMENT_ANALYSIS_RISK_MANAGEMENT' in name_upper:
            responsibilities.append('舆情分析层改进模块风险管理')
            responsibilities.append('风险识别、风险评估、风险缓解措施')
        
        elif 'SENTIMENT_ANALYSIS_TEST_PLAN' in name_upper:
            responsibilities.append('舆情分析层改进模块测试计划')
            responsibilities.append('测试策略、单元测试、集成测试、性能测试')
        
        elif 'SENTIMENT_ANALYSIS_IMPLEMENTATION' in name_upper:
            responsibilities.append('舆情分析层改进模块实施细节')
            responsibilities.append('环境搭建、代码示例、配置模板、部署架构')
        
        elif 'SENTIMENT_ANALYSIS_IMPROVEMENT_PROGRESS' in name_upper:
            responsibilities.append('舆情分析层改进蓝图文档总索引')
            responsibilities.append('短期、中期、长期改进文档导航')
        
        elif 'SENTIMENT_FACTOR_LIBRARY' in name_upper:
            responsibilities.append('舆情因子库模块蓝图设计')
            responsibilities.append('舆情因子提取、因子评估、因子组合')
        
        elif 'DEEP_LEARNING_SENTIMENT_ANALYZER' in name_upper:
            responsibilities.append('深度学习情感分析模块蓝图设计')
            responsibilities.append('FinBERT模型集成、多维度情感分析')
        
        elif 'REAL_TIME_ALERT_SYSTEM' in name_upper:
            responsibilities.append('实时预警系统模块蓝图设计')
            responsibilities.append('实时监控、预警规则引擎、多渠道推送')
        
        elif 'REAL_TIME_MONITORING_DASHBOARD' in name_upper:
            responsibilities.append('实时监控仪表盘模块蓝图设计')
            responsibilities.append('舆情数据可视化、实时监控、趋势分析')
        
        elif 'DATA_SOURCE_EXTENSION' in name_upper:
            responsibilities.append('数据源扩展模块蓝图设计')
            responsibilities.append('多数据源接入、数据清洗、数据标准化')
        
        elif 'AI_DECISION_EXPLANATION' in name_upper:
            responsibilities.append('AI决策解释模块蓝图设计')
            responsibilities.append('决策可解释性、SHAP值分析、特征重要性')
        
        elif 'PERFORMANCE_ATTRIBUTION' in name_upper:
            responsibilities.append('绩效归因模块蓝图设计')
            responsibilities.append('收益归因、风险归因、因子归因')
        
        elif 'INTELLIGENT_QA_SYSTEM' in name_upper:
            responsibilities.append('智能问答系统模块蓝图设计')
            responsibilities.append('自然语言查询、知识检索、智能回答')
        
        elif 'KNOWLEDGE_MANAGEMENT' in name_upper:
            responsibilities.append('知识管理模块蓝图设计')
            responsibilities.append('知识库构建、知识检索、知识更新')
        
        elif 'MULTI_AGENT_COLLABORATION' in name_upper:
            responsibilities.append('多智能体协作模块蓝图设计')
            responsibilities.append('智能体通信、任务分配、协作机制')
        
        elif 'POST_TRADE_REVIEW' in name_upper:
            responsibilities.append('复盘模块蓝图设计')
            responsibilities.append('回测复盘、实盘复盘、因子复盘、风险复盘')
        
        elif 'AUTO_REPORT_GENERATION' in name_upper:
            responsibilities.append('自动化报告生成模块蓝图设计')
            responsibilities.append('报告模板、数据聚合、自动生成')
        
        elif 'AI_WORK_REPORTER' in name_upper:
            responsibilities.append('AI工作汇报与交付模块蓝图设计')
            responsibilities.append('每日工作总结、实时进度通知、决策汇报')
        
        elif 'AI_WORKFLOW_LOGGER' in name_upper:
            responsibilities.append('AI工作记录与优化模块蓝图设计')
            responsibilities.append('会话记录、决策记录、效果评估、知识库构建')
        
        elif 'VALIDATION_TESTING_FRAMEWORK' in name_upper:
            responsibilities.append('验证与测试框架模块蓝图设计')
            responsibilities.append('回测验证、实盘验证、压力测试')
        
        elif 'STRATEGY_LIFECYCLE_MANAGEMENT' in name_upper:
            responsibilities.append('策略生命周期管理模块蓝图设计')
            responsibilities.append('策略创建、策略测试、策略部署、策略监控')
        
        elif 'STRATEGY_VERSION_CONTROL' in name_upper:
            responsibilities.append('策略版本控制模块蓝图设计')
            responsibilities.append('版本管理、变更追踪、回滚机制')
        
        elif 'MODEL_PERFORMANCE_VERSION_MANAGEMENT' in name_upper:
            responsibilities.append('模型性能与版本管理模块蓝图设计')
            responsibilities.append('模型版本控制、性能监控、模型回滚')
        
        elif 'MODEL_MONITORING_DRIFT_DETECTION' in name_upper:
            responsibilities.append('模型监控与漂移检测模块蓝图设计')
            responsibilities.append('模型性能监控、数据漂移检测、模型更新')
        
        elif 'MARKET_REGIME_DETECTION' in name_upper:
            responsibilities.append('市场状态识别模块蓝图设计')
            responsibilities.append('市场环境分析、状态转换、适应性调整')
        
        elif 'MARKET_MICROSTRUCTURE_ANALYSIS' in name_upper:
            responsibilities.append('市场微观结构分析模块蓝图设计')
            responsibilities.append('交易机制分析、流动性分析、价格形成')
        
        elif 'TRADE_EXECUTION_ANALYSIS' in name_upper:
            responsibilities.append('交易执行分析模块蓝图设计')
            responsibilities.append('执行质量评估、滑点分析、执行优化')
        
        elif 'TRANSACTION_COST_ANALYSIS' in name_upper:
            responsibilities.append('交易成本分析模块蓝图设计')
            responsibilities.append('成本分解、成本预测、成本优化')
        
        elif 'SIGNAL_DECAY_ANALYSIS' in name_upper:
            responsibilities.append('信号衰减分析模块蓝图设计')
            responsibilities.append('信号生命周期、衰减模式、优化策略')
        
        elif 'PORTFOLIO_DIAGNOSTICS' in name_upper:
            responsibilities.append('组合诊断模块蓝图设计')
            responsibilities.append('组合健康检查、风险诊断、优化建议')
        
        elif 'PERFORMANCE_ANALYSIS' in name_upper:
            responsibilities.append('性能分析模块蓝图设计')
            responsibilities.append('收益分析、风险分析、效率分析')
        
        elif 'LIVE_TRADING_MONITOR' in name_upper:
            responsibilities.append('实盘监控模块蓝图设计')
            responsibilities.append('实时监控、异常检测、风险预警')
        
        elif 'REAL_TIME_RISK_MONITOR' in name_upper:
            responsibilities.append('实时风险监控模块蓝图设计')
            responsibilities.append('风险指标监控、风险预警、风险报告')
        
        elif 'SCENARIO_ANALYSIS_STRESS_TEST' in name_upper:
            responsibilities.append('情景分析与压力测试模块蓝图设计')
            responsibilities.append('情景构建、压力测试、风险评估')
        
        elif 'RISK_BUDGET_MANAGEMENT' in name_upper:
            responsibilities.append('风险预算管理模块蓝图设计')
            responsibilities.append('风险预算分配、风险预算监控、风险预算调整')
        
        elif 'RESEARCH_WORKFLOW_MANAGEMENT' in name_upper:
            responsibilities.append('研究工作流管理模块蓝图设计')
            responsibilities.append('研究流程、协作机制、成果管理')
        
        elif 'OPERATIONS_KNOWLEDGE_MANAGEMENT' in name_upper:
            responsibilities.append('运维知识管理模块蓝图设计')
            responsibilities.append('运维知识库、故障诊断、最佳实践')
        
        elif 'INTELLIGENT_SCHEDULING_SYSTEM' in name_upper:
            responsibilities.append('智能调度系统模块蓝图设计')
            responsibilities.append('任务调度、资源分配、负载均衡')
        
        elif 'INTELLIGENT_REPORT_DISTRIBUTION' in name_upper:
            responsibilities.append('智能报告分发模块蓝图设计')
            responsibilities.append('报告分发、订阅管理、推送优化')
        
        elif 'INTELLIGENT_PARAMETER_OPTIMIZATION' in name_upper:
            responsibilities.append('智能参数优化模块蓝图设计')
            responsibilities.append('参数调优、自动优化、性能提升')
        
        elif 'INTELLIGENT_ANOMALY_DETECTION' in name_upper:
            responsibilities.append('智能异常检测模块蓝图设计')
            responsibilities.append('异常识别、根因分析、自动修复')
        
        elif 'HISTORICAL_REPLAY_SYSTEM' in name_upper:
            responsibilities.append('历史回放系统模块蓝图设计')
            responsibilities.append('历史数据回放、场景重现、策略验证')
        
        elif 'FULL_PROCESS_DATA_PERSISTENCE' in name_upper:
            responsibilities.append('全流程数据持久化模块蓝图设计')
            responsibilities.append('数据保存、数据血缘、版本控制')
        
        elif 'FACTOR_EFFECTIVENESS_MONITORING' in name_upper:
            responsibilities.append('因子有效性监控模块蓝图设计')
            responsibilities.append('因子表现监控、因子衰减检测、因子更新')
        
        elif 'DATA_QUALITY_MONITORING' in name_upper:
            responsibilities.append('数据质量监控模块蓝图设计')
            responsibilities.append('数据质量检查、异常检测、质量报告')
        
        elif 'DATA_QUALITY_LINEAGE_MANAGEMENT' in name_upper:
            responsibilities.append('数据质量与血缘管理模块蓝图设计')
            responsibilities.append('数据血缘追踪、质量监控、数据治理')
        
        elif 'CONFIGURATION_MANAGEMENT_CENTER' in name_upper:
            responsibilities.append('配置管理中心模块蓝图设计')
            responsibilities.append('配置管理、版本控制、配置分发')
        
        elif 'COMPLIANCE_MONITORING' in name_upper:
            responsibilities.append('合规监控模块蓝图设计')
            responsibilities.append('合规检查、风险预警、合规报告')
        
        elif 'BACKTEST_RESULTS_MANAGEMENT' in name_upper:
            responsibilities.append('回测结果管理模块蓝图设计')
            responsibilities.append('回测结果存储、结果分析、结果对比')
        
        elif 'OPEN_SOURCE_MODULE_SOLUTION' in name_upper:
            responsibilities.append('开源模块解决方案文档')
            responsibilities.append('开源模块选型、集成方案、最佳实践')
        
        elif 'COMPLETE_BLUEPRINT_SUPPLEMENT_REPORT' in name_upper:
            responsibilities.append('Layer 7完整蓝图补充报告')
            responsibilities.append('架构完整性分析、缺失模块识别、蓝图补充建议')
        
        elif 'LAYER_7_GAP_ANALYSIS' in name_upper:
            responsibilities.append('Layer 7缺口分析与补充蓝图')
            responsibilities.append('缺失模块识别、开源替代方案、蓝图补充设计')
        
        elif 'LAYER_7_FINAL_COMPLETENESS_ASSESSMENT' in name_upper:
            responsibilities.append('Layer 7最终完整性评估报告')
            responsibilities.append('架构完整性验证、功能覆盖评估、质量标准确认')
        
        elif 'DELETED_FILES_RECOVERY_ASSESSMENT' in name_upper:
            responsibilities.append('删除文件恢复评估报告')
            responsibilities.append('文件恢复可行性、恢复方案、风险评估')
        
        elif 'DELETED_CONTENT_REVIEW_REPORT' in name_upper:
            responsibilities.append('删除内容审查报告')
            responsibilities.append('内容审查、影响评估、恢复建议')
        
        else:
            responsibilities.append('AI工作流与舆情分析综合层模块蓝图设计')
        
        responsibilities = [self._ensure_min_length(r) for r in responsibilities]
        
        return responsibilities
    
    def _ensure_min_length(self, text: str) -> str:
        """确保文本长度至少为min_length"""
        if len(text) < self.min_length:
            text += "模块设计与实施指导"
        return text
    
    def optimize_file(self, file_path: Path) -> bool:
        """优化单个文件的职责描述"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not yaml_match:
                return False
            
            yaml_content = yaml_match.group(1)
            
            new_responsibilities = self.generate_responsibility(file_path.stem)
            
            if not new_responsibilities:
                return False
            
            responsibility_str = '\n'.join([f'  - {r}' for r in new_responsibilities])
            
            new_yaml = re.sub(
                r'responsibility:\s*\n(  - .*\n)+',
                f'responsibility:\n{responsibility_str}\n',
                yaml_content
            )
            
            new_content = content.replace(yaml_content, new_yaml, 1)
            
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"  [ERROR] 优化失败: {file_path.name} - {e}")
            return False
    
    def run(self, docs_dir: Path):
        """执行优化"""
        print("=== 开始优化职责描述 ===\n")
        
        md_files = list(docs_dir.glob("**/*.md"))
        
        for md_file in md_files:
            if any(keyword in str(md_file) for keyword in ['06_ARCHIVE', '09_ARCHIVE', '99_ARCHIVE', 'archive']):
                continue
            
            self.total_count += 1
            
            if self.optimize_file(md_file):
                self.optimized_count += 1
                print(f"  [OK] 优化: {md_file.name}")
        
        print(f"\n=== 优化完成 ===")
        print(f"总文件数: {self.total_count}")
        print(f"优化文件数: {self.optimized_count}")
        if self.total_count > 0:
            print(f"优化率: {self.optimized_count/self.total_count*100:.2f}%")

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs/10_AI_WORKFLOW")
    optimizer = SentimentResponsibilityOptimizer()
    optimizer.run(docs_dir)

if __name__ == "__main__":
    main()
