#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
职责描述修复脚本
为69个职责描述过短的文档添加详细说明
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class ResponsibilityFixer:
    def __init__(self):
        self.project_root = Path(r"D:\ZephyrAlpha")
        self.audit_result_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / "layer4_deep_audit_result_v6.json"
        self.fixed_count = 0
        self.error_count = 0
        self.results = []
        
        self.responsibility_templates = {
            "风险预算": "风险预算管理与分配，包括风险限额设定、预算动态调整、风险预算监控与预警",
            "因子计算": "因子计算与特征工程，包括因子挖掘、因子预处理、因子有效性检验、因子组合优化",
            "组合优化": "投资组合优化，包括权重分配、约束条件处理、优化算法实现、组合再平衡",
            "数据质量": "数据质量监控与治理，包括数据完整性检查、一致性验证、异常检测、数据修复",
            "市场状态识别": "市场状态识别与分类，包括市场环境判断、状态转换检测、状态预测模型",
            "交易执行": "交易执行与订单管理，包括执行算法、滑点控制、冲击成本优化、执行监控",
            "机器学习": "机器学习模型开发与优化，包括模型训练、超参数调优、模型评估、模型部署",
            "特征工程": "特征工程与特征管理，包括特征提取、特征转换、特征选择、特征存储",
            "数据源": "数据源管理与数据接入，包括数据采集、数据清洗、数据存储、数据服务"
        }
    
    def load_audit_results(self) -> Dict:
        with open(self.audit_result_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_yaml_header(self, content: str) -> Tuple[Optional[str], Optional[str]]:
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, content, re.DOTALL)
        if match:
            return match.group(1), match.group(0)
        return None, None
    
    def extract_responsibility_boundary(self, content: str) -> Optional[str]:
        patterns = [
            r'responsibility_boundary:\s*\|?\s*\n([^\n]+(?:\n(?!\w+:)[^\n]+)*)',
            r'本文档职责[:：]\s*(.+?)(?:\n\n|\n#)',
            r'核心定位[:：]\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                text = match.group(1).strip()
                text = re.sub(r'^\s*-\s*', '', text, flags=re.MULTILINE)
                text = text.strip()
                if len(text) > 20:
                    return text
        return None
    
    def generate_detailed_responsibility(self, doc_path: str, current_resp: str) -> str:
        doc_name = Path(doc_path).stem
        
        for keyword, template in self.responsibility_templates.items():
            if keyword in current_resp:
                return template
        
        if "VOLATILITY" in doc_name.upper():
            return "波动率预测与建模，包括GARCH模型、神经网络预测、波动率曲面构建"
        elif "TEXT_ENCODER" in doc_name.upper():
            return "文本编码器设计，包括文本预处理、语义编码、向量表示、编码优化"
        elif "SYNTHETIC_DATA" in doc_name.upper():
            return "合成数据生成，包括数据增强、GAN模型、数据隐私保护、生成质量评估"
        elif "SPARSE_ATTENTION" in doc_name.upper():
            return "稀疏注意力机制，包括注意力优化、计算加速、内存优化、长序列处理"
        elif "RAG_SYSTEM" in doc_name.upper():
            return "RAG检索增强生成系统，包括向量检索、知识库构建、检索优化、生成增强"
        elif "NBEATS" in doc_name.upper():
            return "N-BEATS时序预测模型，包括模型架构、训练优化、预测精度提升"
        elif "MODEL_WATERMARK" in doc_name.upper():
            return "模型水印技术，包括水印嵌入、水印检测、知识产权保护、防篡改"
        elif "MODEL_VERSIONING" in doc_name.upper():
            return "模型版本管理，包括版本控制、模型回滚、版本对比、变更追踪"
        elif "MODEL_QUANTIZATION" in doc_name.upper():
            return "模型量化技术，包括权重量化、激活量化、混合精度、量化感知训练"
        elif "MODEL_PRUNING" in doc_name.upper():
            return "模型剪枝优化，包括结构化剪枝、非结构化剪枝、剪枝策略、稀疏模型"
        elif "MODEL_PERFORMANCE" in doc_name.upper():
            return "模型性能基准测试，包括性能评估、基准对比、性能优化、瓶颈分析"
        elif "MODEL_DEBUGGING" in doc_name.upper():
            return "模型调试工具集，包括错误诊断、性能分析、可视化调试、问题定位"
        elif "MODEL_AB_TESTING" in doc_name.upper():
            return "模型A/B测试框架，包括实验设计、流量分配、效果评估、统计检验"
        elif "MODEL_CARD" in doc_name.upper():
            return "模型卡片文档，包括模型说明、性能指标、使用限制、伦理考虑"
        elif "MIXED_PRECISION" in doc_name.upper():
            return "混合精度训练，包括FP16训练、梯度缩放、精度优化、训练加速"
        elif "MIXTURE_OF_EXPERTS" in doc_name.upper():
            return "专家混合模型，包括专家网络、门控机制、负载均衡、专家路由"
        elif "MIA_DEFENSE" in doc_name.upper():
            return "成员推理攻击防御，包括隐私保护、攻击检测、防御策略、模型加固"
        elif "MEMORY_AUGMENTED" in doc_name.upper():
            return "记忆增强神经网络，包括外部记忆、记忆读写、记忆检索、记忆更新"
        elif "MAMBA_SSM" in doc_name.upper():
            return "Mamba状态空间模型，包括SSM架构、序列建模、计算效率、长序列处理"
        elif "LIQUID_NEURAL" in doc_name.upper():
            return "液态神经网络，包括连续时间动态、自适应计算、实时推理"
        elif "INFERENCE_ACCELERATION" in doc_name.upper():
            return "推理加速技术，包括模型优化、硬件加速、批处理优化、延迟降低"
        elif "HOMOMORPHIC_ENCRYPTION" in doc_name.upper():
            return "同态加密机器学习，包括加密计算、隐私保护、安全推理、性能优化"
        elif "GRAPH_NEURAL" in doc_name.upper():
            return "图神经网络，包括图结构建模、消息传递、图注意力、图池化"
        elif "GRADIENT_CHECKPOINTING" in doc_name.upper():
            return "梯度检查点技术，包括内存优化、计算重用、训练加速、大模型训练"
        elif "GRADIENT_ACCUMULATION" in doc_name.upper():
            return "梯度累积技术，包括小批量训练、内存优化、梯度更新、大模型训练"
        elif "FEDERATED_LEARNING" in doc_name.upper():
            return "联邦学习框架，包括分布式训练、隐私保护、模型聚合、通信优化"
        elif "DIFFUSION_MODEL" in doc_name.upper():
            return "扩散模型，包括去噪过程、生成采样、条件生成、图像合成"
        elif "DIFFERENTIAL_PRIVACY" in doc_name.upper():
            return "差分隐私机器学习，包括噪声添加、隐私预算、隐私保护、模型训练"
        elif "CODE_GENERATION" in doc_name.upper():
            return "代码生成模型，包括代码补全、代码翻译、代码生成、代码理解"
        elif "BATCH_INFERENCE" in doc_name.upper():
            return "批量推理优化，包括批处理策略、吞吐量优化、资源调度、延迟平衡"
        elif "DATA_AUGMENTATION" in doc_name.upper():
            return "数据增强技术，包括数据变换、合成数据、增强策略、增强效果评估"
        elif "DATA_ANNOTATION" in doc_name.upper():
            return "数据标注平台，包括标注工具、质量控制、标注管理、标注效率"
        elif "BACKDOOR_DETECTION" in doc_name.upper():
            return "后门攻击检测，包括模型安全、攻击检测、防御机制、安全审计"
        elif "AUTOML" in doc_name.upper():
            return "AutoML自动化机器学习，包括自动特征工程、自动调参、模型选择、管道优化"
        elif "AI_AGENT" in doc_name.upper():
            return "AI智能体框架，包括智能体设计、决策规划、环境交互、多智能体协作"
        elif "ACCEPTANCE_CRITERIA" in doc_name.upper():
            return "验收标准定义，包括功能验收、性能验收、质量验收、交付标准"
        elif "DATAFLOW_ARCHITECTURE" in doc_name.upper():
            return "数据流架构设计，包括数据管道、流处理、批处理、架构优化"
        elif "AI_TRUST_CALIBRATION" in doc_name.upper():
            return "AI信任校准，包括置信度校准、不确定性估计、信任度量、校准评估"
        elif "AI_CAPABILITY_GAP" in doc_name.upper():
            return "AI能力差距分析，包括能力评估、差距识别、改进路径、能力规划"
        elif "ADAPTIVE_MODEL" in doc_name.upper():
            return "自适应模型系统，包括模型适应、在线学习、概念漂移、动态调整"
        elif "NEURAL_ODE" in doc_name.upper():
            return "神经ODE模型，包括连续深度、常微分方程、自适应计算、时序建模"
        elif "MODEL_SERVING" in doc_name.upper():
            return "模型服务框架，包括模型部署、服务架构、负载均衡、服务监控"
        elif "TRUSTED_EXECUTION" in doc_name.upper():
            return "可信执行环境，包括安全计算、隐私保护、可信硬件、安全隔离"
        elif "MARKET_MICROSTRUCTURE" in doc_name.upper():
            return "市场微观结构模型，包括订单簿建模、价格形成、市场冲击、流动性分析"
        elif "TAIL_RISK" in doc_name.upper():
            return "尾部风险预测，包括极端事件建模、风险度量、压力测试、风险预警"
        elif "SENTIMENT_ANALYSIS" in doc_name.upper():
            return "情感分析层，包括文本情感、舆情监控、情绪指标、情感因子"
        elif "SELF_SUPERVISED" in doc_name.upper():
            return "自监督学习，包括预训练任务、对比学习、自监督表示、迁移学习"
        elif "SECURE_MULTI_PARTY" in doc_name.upper():
            return "安全多方计算，包括隐私计算、联合建模、安全协议、数据协作"
        elif "OPEN_SOURCE_INTEGRATION" in doc_name.upper():
            return "开源项目集成，包括MLflow集成、Qlib集成、工具链整合、架构参考"
        elif "CONFIG_MANAGEMENT" in doc_name.upper():
            return "配置管理系统，包括配置存储、版本控制、配置分发、配置验证"
        elif "REPORTING" in doc_name.upper():
            return "报告生成系统，包括报告模板、数据聚合、可视化展示、报告分发"
        elif "ALERTING_SYSTEM" in doc_name.upper():
            return "告警系统，包括告警规则、告警路由、告警聚合、告警通知"
        elif "LIQUIDITY_CONSTRAINED" in doc_name.upper():
            return "流动性约束优化，包括流动性建模、约束处理、优化求解、交易成本"
        elif "CONSTRAINT_SOLVER" in doc_name.upper():
            return "约束求解器，包括约束建模、求解算法、优化引擎、约束验证"
        elif "AUTO_REPAIR" in doc_name.upper():
            return "自动修复引擎，包括问题检测、修复策略、自动修复、修复验证"
        elif "AI_ENHANCEMENT" in doc_name.upper():
            return "AI增强集成，包括AI辅助、智能优化、增强功能、AI能力注入"
        elif "REINFORCEMENT_LEARNING" in doc_name.upper():
            return "强化学习技术规范，包括RL算法、策略优化、环境建模、奖励设计"
        elif "PROBABILISTIC_FORECASTING" in doc_name.upper():
            return "概率预测技术规范，包括不确定性量化、概率分布、预测区间、校准评估"
        elif "MODEL_MONITORING" in doc_name.upper():
            return "模型监控技术规范，包括性能监控、漂移检测、告警机制、监控指标"
        elif "MODEL_INTERPRETABILITY" in doc_name.upper():
            return "模型可解释性技术规范，包括特征重要性、解释方法、可视化、可解释AI"
        elif "MLOPS_PLATFORM" in doc_name.upper():
            return "MLOps平台技术规范，包括模型生命周期、自动化管道、监控运维、持续集成"
        elif "DRIFT_DETECTION" in doc_name.upper():
            return "漂移检测技术规范，包括数据漂移、概念漂移、检测算法、漂移适应"
        elif "CAUSAL_INFERENCE" in doc_name.upper():
            return "因果推断技术规范，包括因果发现、因果效应、反事实推理、因果图"
        elif "DEEPAR" in doc_name.upper():
            return "DeepAR时序预测模型，包括自回归模型、概率预测、多序列学习、预测优化"
        elif "FEATURE_STORE" in doc_name.upper():
            return "特征存储系统，包括特征管理、特征服务、特征版本控制、特征血缘"
        elif "MACHINE_LEARNING_LAYER" in doc_name.upper():
            return "机器学习层架构，包括模型管理、训练管道、推理服务、监控运维"
        elif "MODEL_REGISTRY" in doc_name.upper():
            return "模型注册中心，包括模型存储、版本管理、模型元数据、模型共享"
        elif "EXPERIMENT_TRACKING" in doc_name.upper():
            return "实验追踪系统，包括实验记录、参数管理、结果对比、实验复现"
        elif "MLOPS_PLATFORM_BLUEPRINT" in doc_name.upper():
            return "MLOps平台蓝图，包括平台架构、组件集成、流程设计、最佳实践"
        else:
            return f"负责{doc_name.replace('_', ' ').replace('BLUEPRINT', '').strip()}相关功能的设计与实现"
    
    def update_yaml_responsibility(self, yaml_content: str, new_responsibility: str) -> str:
        lines = yaml_content.split('\n')
        updated_lines = []
        in_responsibility = False
        responsibility_updated = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith('responsibility:'):
                in_responsibility = True
                updated_lines.append(f'responsibility:')
                updated_lines.append(f'  - {new_responsibility}')
                responsibility_updated = True
            elif in_responsibility:
                if line.strip().startswith('-') and not responsibility_updated:
                    continue
                elif not line.strip().startswith('-') and not line.strip().startswith(' '):
                    in_responsibility = False
                    updated_lines.append(line)
                elif responsibility_updated:
                    if not line.strip().startswith('-'):
                        in_responsibility = False
                        updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        return '\n'.join(updated_lines)
    
    def fix_document(self, doc_path: str, current_resp: str) -> Dict:
        full_path = self.project_root / doc_path
        
        if not full_path.exists():
            return {
                "doc": doc_path,
                "status": "error",
                "message": "文件不存在"
            }
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(full_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except Exception as e:
                return {
                    "doc": doc_path,
                    "status": "error",
                    "message": f"编码错误: {str(e)}"
                }
        
        yaml_content, yaml_block = self.extract_yaml_header(content)
        if not yaml_content:
            return {
                "doc": doc_path,
                "status": "error",
                "message": "未找到YAML头部"
            }
        
        responsibility_boundary = self.extract_responsibility_boundary(content)
        
        if responsibility_boundary:
            new_responsibility = responsibility_boundary
        else:
            new_responsibility = self.generate_detailed_responsibility(doc_path, current_resp)
        
        updated_yaml = self.update_yaml_responsibility(yaml_content, new_responsibility)
        
        new_content = content.replace(yaml_block, f"---\n{updated_yaml}\n---\n")
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.fixed_count += 1
            return {
                "doc": doc_path,
                "status": "success",
                "old_responsibility": current_resp,
                "new_responsibility": new_responsibility,
                "source": "responsibility_boundary" if responsibility_boundary else "generated"
            }
        except Exception as e:
            self.error_count += 1
            return {
                "doc": doc_path,
                "status": "error",
                "message": f"写入失败: {str(e)}"
            }
    
    def run(self):
        print("=" * 80)
        print("职责描述修复脚本")
        print("=" * 80)
        
        audit_results = self.load_audit_results()
        unclear_docs = audit_results.get('unclear_responsibility', [])
        
        print(f"\n发现 {len(unclear_docs)} 个需要修复的文档")
        print("-" * 80)
        
        for i, doc_info in enumerate(unclear_docs, 1):
            doc_path = doc_info['doc']
            current_resp = doc_info['responsibility']
            
            print(f"\n[{i}/{len(unclear_docs)}] 处理: {doc_path}")
            print(f"  当前职责: {current_resp}")
            
            result = self.fix_document(doc_path, current_resp)
            self.results.append(result)
            
            if result['status'] == 'success':
                print(f"  ✓ 新职责: {result['new_responsibility'][:60]}...")
            else:
                print(f"  ✗ 错误: {result.get('message', '未知错误')}")
        
        print("\n" + "=" * 80)
        print("修复完成统计")
        print("=" * 80)
        print(f"成功修复: {self.fixed_count} 个文档")
        print(f"修复失败: {self.error_count} 个文档")
        
        report = {
            "fix_time": str(Path(__file__).stat().st_mtime),
            "total_docs": len(unclear_docs),
            "fixed_count": self.fixed_count,
            "error_count": self.error_count,
            "results": self.results
        }
        
        report_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / "responsibility_fix_result.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细报告已保存至: {report_path}")
        print("=" * 80)

if __name__ == "__main__":
    fixer = ResponsibilityFixer()
    fixer.run()
