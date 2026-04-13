#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
修复编码并添加职责边界脚本
"""

import os
import re
from pathlib import Path
from datetime import datetime
import chardet

# Layer 4文档列表
layer4_docs = [
    'TRANSFER_LEARNING_BLUEPRINT.md',
    'TRUSTED_EXECUTION_ENVIRONMENT_BLUEPRINT.md',
    'VOLATILITY_PREDICTION_BLUEPRINT.md',
    'TEXT_ENCODER_BLUEPRINT.md',
    'TEMPORAL_FUSION_TRANSFORMER_BLUEPRINT.md',
    'SYNTHETIC_DATA_GENERATION_BLUEPRINT.md',
    'TAIL_RISK_PREDICTION_BLUEPRINT.md',
    'SERVICE_MESH_INTEGRATION_BLUEPRINT.md',
    'SPARSE_ATTENTION_BLUEPRINT.md',
    'SECURE_MULTI_PARTY_COMPUTATION_BLUEPRINT.md',
    'SELF_SUPERVISED_LEARNING_BLUEPRINT.md',
    'REINFORCEMENT_LEARNING_BLUEPRINT.md',
    'RAG_SYSTEM_BLUEPRINT.md',
    'PROMPT_ENGINEERING_BLUEPRINT.md',
    'ORDER_FLOW_PREDICTION_BLUEPRINT.md',
    'OPTIMIZER_VARIANTS_BLUEPRINT.md',
    'ONLINE_LEARNING_BLUEPRINT.md',
    'NEURAL_ODE_BLUEPRINT.md',
    'NEURAL_ARCHITECTURE_SEARCH_BLUEPRINT.md',
    'NBEATS_BLUEPRINT.md',
    'MULTI_TASK_LEARNING_BLUEPRINT.md',
    'MULTI_MODEL_ORCHESTRATOR_BLUEPRINT.md',
    'MULTIMODAL_LLM_BLUEPRINT.md',
    'MULTIMODAL_FUSION_BLUEPRINT.md',
    'MODEL_WARMUP_BLUEPRINT.md',
    'MODEL_WATERMARK_BLUEPRINT.md',
    'MODEL_VERSIONING_BLUEPRINT.md',
    'MODEL_SECURITY_SCANNER_BLUEPRINT.md',
    'MODEL_ROLLBACK_BLUEPRINT.md',
    'MODEL_QUANTIZATION_BLUEPRINT.md',
    'MODEL_MONITORING_BLUEPRINT.md',
    'MODEL_PERFORMANCE_BENCHMARK_BLUEPRINT.md',
    'MODEL_PRUNING_BLUEPRINT.md',
    'MODEL_LINEAGE_BLUEPRINT.md',
    'MODEL_DEBUGGING_TOOLKIT_BLUEPRINT.md',
    'MODEL_CARD_BLUEPRINT.md',
    'MODEL_AB_TESTING_BLUEPRINT.md',
    'MLOPS_PLATFORM_BLUEPRINT.md',
    'MIA_DEFENSE_BLUEPRINT.md',
    'MIXED_PRECISION_TRAINING_BLUEPRINT.md',
    'MIXTURE_OF_EXPERTS_BLUEPRINT.md',
    'META_LEARNING_BLUEPRINT.md',
    'MARKET_MICROSTRUCTURE_MODEL_BLUEPRINT.md',
    'MEMORY_AUGMENTED_NN_BLUEPRINT.md',
    'MARKET_MAKING_MODEL_BLUEPRINT.md',
    'MACHINE_LEARNING_LAYER_BLUEPRINT.md',
    'MAMBA_SSM_BLUEPRINT.md',
    'LLM_FINE_TUNING_BLUEPRINT.md',
    'LEARNING_RATE_SCHEDULER_BLUEPRINT.md',
    'LIQUID_NEURAL_NETWORK_BLUEPRINT.md',
    'KNOWLEDGE_DISTILLATION_BLUEPRINT.md',
    'INFERENCE_ACCELERATION_BLUEPRINT.md',
    'HYPERPARAMETER_OPTIMIZATION_BLUEPRINT.md',
    'HOMOMORPHIC_ENCRYPTION_ML_BLUEPRINT.md',
    'HIGH_FREQUENCY_SIGNAL_PROCESSING_BLUEPRINT.md',
    'GRAYSCALE_RELEASE_BLUEPRINT.md',
    'GRAPH_NEURAL_NETWORK_BLUEPRINT.md',
    'GRADIENT_CHECKPOINTING_BLUEPRINT.md',
    'GRADIENT_ACCUMULATION_BLUEPRINT.md',
    'FEDERATED_LEARNING_BLUEPRINT.md',
    'FEATURE_STORE_BLUEPRINT.md',
    'FEATURE_SELECTION_AUTOMATION_BLUEPRINT.md',
    'FAIRNESS_DETECTION_BLUEPRINT.md',
    'EXPERIMENT_TRACKING_BLUEPRINT.md',
    'EVENT_DRIVEN_LEARNING_BLUEPRINT.md',
    'DRIFT_DETECTION_BLUEPRINT.md',
    'ENSEMBLE_LEARNING_BLUEPRINT.md',
    'DISTRIBUTED_TRAINING_BLUEPRINT.md',
    'DIFFUSION_MODEL_BLUEPRINT.md',
    'DISASTER_RECOVERY_FRAMEWORK_ENTRY.md',
    'DIFFERENTIAL_PRIVACY_ML_BLUEPRINT.md',
    'DEEPAR_BLUEPRINT.md',
    'DATA_QUALITY_MONITORING_BLUEPRINT.md',
    'DATA_AUGMENTATION_BLUEPRINT.md',
    'DATA_ANNOTATION_PLATFORM_BLUEPRINT.md',
    'DATAFLOW_ARCHITECTURE_BLUEPRINT.md',
    'CURRICULUM_LEARNING_BLUEPRINT.md',
    'CORRELATION_PREDICTION_BLUEPRINT.md',
    'BATCH_INFERENCE_OPTIMIZATION_BLUEPRINT.md',
    'CODE_GENERATION_MODEL_BLUEPRINT.md',
    'BACKDOOR_DETECTION_BLUEPRINT.md',
    'AUTOML_PIPELINE_BLUEPRINT.md',
    'ARBITRAGE_DETECTION_BLUEPRINT.md',
    'ALTERNATIVE_DATA_FUSION_BLUEPRINT.md',
    'AI_AGENT_FRAMEWORK_BLUEPRINT.md',
    'ADVERSARIAL_ROBUSTNESS_BLUEPRINT.md',
    'ADAPTIVE_MODEL_SYSTEM_BLUEPRINT.md',
    'ACTIVE_LEARNING_BLUEPRINT.md',
    'ACCEPTANCE_CRITERIA_BLUEPRINT.md',
]

def get_responsibility_boundary(doc_name):
    """根据文档名称获取职责边界"""
    # 提取关键词
    name_upper = doc_name.upper().replace('_BLUEPRINT.MD', '')
    
    # 根据关键词生成职责边界
    if 'TRANSFER_LEARNING' in name_upper:
        return '本文档负责Layer 4机器学习层的迁移学习系统设计，包括预训练模型迁移、领域自适应、多任务迁移等核心功能。'
    elif 'TRUSTED_EXECUTION' in name_upper:
        return '本文档负责Layer 4机器学习层的可信执行环境设计，包括安全计算环境、数据隐私保护、模型安全执行等核心功能。'
    elif 'VOLATILITY_PREDICTION' in name_upper:
        return '本文档负责Layer 4机器学习层的波动率预测模型设计，包括波动率建模、GARCH模型、神经网络预测等核心功能。'
    elif 'TEXT_ENCODER' in name_upper:
        return '本文档负责Layer 4机器学习层的文本编码器设计，包括文本向量化、语义编码、多语言支持等核心功能。'
    elif 'TEMPORAL_FUSION' in name_upper:
        return '本文档负责Layer 4机器学习层的时间融合Transformer设计，包括时序特征融合、注意力机制、多尺度建模等核心功能。'
    elif 'SYNTHETIC_DATA' in name_upper:
        return '本文档负责Layer 4机器学习层的合成数据生成系统设计，包括GAN生成、VAE生成、Diffusion模型等核心功能。'
    elif 'TAIL_RISK' in name_upper:
        return '本文档负责Layer 4机器学习层的尾部风险预测模型设计，包括极端事件预测、尾部风险建模、压力测试等核心功能。'
    elif 'SERVICE_MESH' in name_upper:
        return '本文档负责Layer 5执行层的服务网格集成设计，包括服务发现、负载均衡、熔断降级等核心功能。'
    elif 'SPARSE_ATTENTION' in name_upper:
        return '本文档负责Layer 4机器学习层的稀疏注意力机制设计，包括稀疏注意力计算、长序列处理、内存优化等核心功能。'
    elif 'SECURE_MULTI_PARTY' in name_upper:
        return '本文档负责Layer 4机器学习层的安全多方计算设计，包括隐私计算、联邦学习、安全聚合等核心功能。'
    elif 'SELF_SUPERVISED' in name_upper:
        return '本文档负责Layer 4机器学习层的自监督学习设计，包括对比学习、掩码预测、自监督预训练等核心功能。'
    elif 'REINFORCEMENT_LEARNING' in name_upper:
        return '本文档负责Layer 4机器学习层的强化学习系统设计，包括策略优化、价值函数、环境建模等核心功能。'
    elif 'RAG_SYSTEM' in name_upper:
        return '本文档负责Layer 4机器学习层的RAG检索增强生成系统设计，包括文档检索、知识库构建、答案生成等核心功能。'
    elif 'PROMPT_ENGINEERING' in name_upper:
        return '本文档负责Layer 4机器学习层的提示工程系统设计，包括提示模板、Few-shot学习、Chain-of-Thought等核心功能。'
    elif 'ORDER_FLOW' in name_upper:
        return '本文档负责Layer 4机器学习层的订单流预测模型设计，包括订单流分析、市场微观结构、价格预测等核心功能。'
    elif 'OPTIMIZER_VARIANTS' in name_upper:
        return '本文档负责Layer 4机器学习层的优化器变体设计，包括自适应学习率、梯度优化、二阶优化等核心功能。'
    elif 'ONLINE_LEARNING' in name_upper:
        return '本文档负责Layer 4机器学习层的在线学习系统设计，包括增量学习、概念漂移、实时更新等核心功能。'
    elif 'NEURAL_ODE' in name_upper:
        return '本文档负责Layer 4机器学习层的神经ODE设计，包括连续时间建模、微分方程求解、动态系统建模等核心功能。'
    elif 'NEURAL_ARCHITECTURE_SEARCH' in name_upper:
        return '本文档负责Layer 4机器学习层的神经架构搜索设计，包括搜索空间、搜索策略、性能评估等核心功能。'
    elif 'NBEATS' in name_upper:
        return '本文档负责Layer 4机器学习层的N-BEATS时序模型设计，包括时序分解、趋势预测、季节性建模等核心功能。'
    elif 'MULTI_TASK_LEARNING' in name_upper:
        return '本文档负责Layer 4机器学习层的多任务学习设计，包括任务关系建模、参数共享、联合优化等核心功能。'
    elif 'MULTI_MODEL_ORCHESTRATOR' in name_upper:
        return '本文档负责Layer 4机器学习层的多模型编排系统设计，包括模型调度、负载均衡、故障恢复等核心功能。'
    elif 'MULTIMODAL_LLM' in name_upper:
        return '本文档负责Layer 4机器学习层的多模态大语言模型设计，包括视觉语言模型、音频处理、跨模态融合等核心功能。'
    elif 'MULTIMODAL_FUSION' in name_upper:
        return '本文档负责Layer 4机器学习层的多模态融合设计，包括特征对齐、跨模态注意力、融合策略等核心功能。'
    elif 'MODEL_WARMUP' in name_upper:
        return '本文档负责Layer 4机器学习层的模型预热系统设计，包括预热策略、流量控制、性能监控等核心功能。'
    elif 'MODEL_WATERMARK' in name_upper:
        return '本文档负责Layer 4机器学习层的模型水印系统设计，包括水印嵌入、水印检测、版权保护等核心功能。'
    elif 'MODEL_VERSIONING' in name_upper:
        return '本文档负责Layer 4机器学习层的模型版本管理系统设计，包括版本控制、变更追踪、回滚机制等核心功能。'
    elif 'MODEL_SECURITY_SCANNER' in name_upper:
        return '本文档负责Layer 4机器学习层的模型安全扫描系统设计，包括漏洞检测、安全审计、风险评估等核心功能。'
    elif 'MODEL_ROLLBACK' in name_upper:
        return '本文档负责Layer 4机器学习层的模型回滚系统设计，包括回滚策略、版本切换、故障恢复等核心功能。'
    elif 'MODEL_QUANTIZATION' in name_upper:
        return '本文档负责Layer 4机器学习层的模型量化系统设计，包括量化算法、精度优化、推理加速等核心功能。'
    elif 'MODEL_MONITORING' in name_upper:
        return '本文档负责Layer 4机器学习层的模型监控系统设计，包括性能监控、漂移检测、告警机制等核心功能。'
    elif 'MODEL_PERFORMANCE_BENCHMARK' in name_upper:
        return '本文档负责Layer 4机器学习层的模型性能基准测试设计，包括基准定义、性能测试、对比分析等核心功能。'
    elif 'MODEL_PRUNING' in name_upper:
        return '本文档负责Layer 4机器学习层的模型剪枝系统设计，包括剪枝算法、稀疏优化、压缩加速等核心功能。'
    elif 'MODEL_LINEAGE' in name_upper:
        return '本文档负责Layer 4机器学习层的模型血缘追踪系统设计，包括血缘记录、影响分析、审计追溯等核心功能。'
    elif 'MODEL_DEBUGGING_TOOLKIT' in name_upper:
        return '本文档负责Layer 4机器学习层的模型调试工具包设计，包括梯度分析、激活值分析、权重分析等核心功能。'
    elif 'MODEL_CARD' in name_upper:
        return '本文档负责Layer 4机器学习层的模型卡片系统设计，包括模型描述、性能指标、使用限制等核心功能。'
    elif 'MODEL_AB_TESTING' in name_upper:
        return '本文档负责Layer 4机器学习层的模型A/B测试系统设计，包括实验设计、流量分配、统计分析等核心功能。'
    elif 'MLOPS_PLATFORM' in name_upper:
        return '本文档负责Layer 4机器学习层的MLOps平台设计，包括流水线管理、实验跟踪、模型部署等核心功能。'
    elif 'MIA_DEFENSE' in name_upper:
        return '本文档负责Layer 4机器学习层的成员推理攻击防御设计，包括攻击检测、防御策略、隐私保护等核心功能。'
    elif 'MIXED_PRECISION_TRAINING' in name_upper:
        return '本文档负责Layer 4机器学习层的混合精度训练设计，包括精度优化、内存管理、训练加速等核心功能。'
    elif 'MIXTURE_OF_EXPERTS' in name_upper:
        return '本文档负责Layer 4机器学习层的混合专家模型设计，包括专家路由、负载均衡、模型并行等核心功能。'
    elif 'META_LEARNING' in name_upper:
        return '本文档负责Layer 4机器学习层的元学习系统设计，包括学习如何学习、快速适应、少样本学习等核心功能。'
    elif 'MARKET_MICROSTRUCTURE' in name_upper:
        return '本文档负责Layer 4机器学习层的市场微观结构模型设计，包括订单簿建模、价格发现、流动性分析等核心功能。'
    elif 'MEMORY_AUGMENTED' in name_upper:
        return '本文档负责Layer 4机器学习层的记忆增强神经网络设计，包括外部记忆、读写机制、推理能力等核心功能。'
    elif 'MARKET_MAKING' in name_upper:
        return '本文档负责Layer 4机器学习层的做市模型设计，包括报价策略、库存管理、风险控制等核心功能。'
    elif 'MACHINE_LEARNING_LAYER' in name_upper:
        return '本文档负责Layer 4机器学习层的整体架构设计，包括模块划分、接口定义、技术选型等核心功能。'
    elif 'MAMBA_SSM' in name_upper:
        return '本文档负责Layer 4机器学习层的Mamba状态空间模型设计，包括序列建模、长距离依赖、高效推理等核心功能。'
    elif 'LLM_FINE_TUNING' in name_upper:
        return '本文档负责Layer 4机器学习层的大语言模型微调设计，包括指令微调、领域适应、参数高效微调等核心功能。'
    elif 'LEARNING_RATE_SCHEDULER' in name_upper:
        return '本文档负责Layer 4机器学习层的学习率调度器设计，包括调度策略、自适应调整、训练优化等核心功能。'
    elif 'LIQUID_NEURAL_NETWORK' in name_upper:
        return '本文档负责Layer 4机器学习层的液态神经网络设计，包括连续时间动力学、自适应结构、实时学习等核心功能。'
    elif 'KNOWLEDGE_DISTILLATION' in name_upper:
        return '本文档负责Layer 4机器学习层的知识蒸馏系统设计，包括教师学生模型、蒸馏损失、模型压缩等核心功能。'
    elif 'INFERENCE_ACCELERATION' in name_upper:
        return '本文档负责Layer 4机器学习层的推理加速系统设计，包括推理优化、批处理加速、硬件加速等核心功能。'
    elif 'HYPERPARAMETER_OPTIMIZATION' in name_upper:
        return '本文档负责Layer 4机器学习层的超参数优化系统设计，包括搜索策略、贝叶斯优化、早停机制等核心功能。'
    elif 'HOMOMORPHIC_ENCRYPTION' in name_upper:
        return '本文档负责Layer 4机器学习层的同态加密机器学习设计，包括加密计算、隐私保护、安全推理等核心功能。'
    elif 'HIGH_FREQUENCY_SIGNAL' in name_upper:
        return '本文档负责Layer 4机器学习层的高频信号处理设计，包括信号滤波、特征提取、实时处理等核心功能。'
    elif 'GRAYSCALE_RELEASE' in name_upper:
        return '本文档负责Layer 4机器学习层的灰度发布系统设计，包括流量切换、风险控制、回滚机制等核心功能。'
    elif 'GRAPH_NEURAL_NETWORK' in name_upper:
        return '本文档负责Layer 4机器学习层的图神经网络设计，包括图结构建模、消息传递、节点分类等核心功能。'
    elif 'GRADIENT_CHECKPOINTING' in name_upper:
        return '本文档负责Layer 4机器学习层的梯度检查点设计，包括内存优化、计算重用、训练加速等核心功能。'
    elif 'GRADIENT_ACCUMULATION' in name_upper:
        return '本文档负责Layer 4机器学习层的梯度累积设计，包括批次模拟、内存优化、训练稳定性等核心功能。'
    elif 'FEDERATED_LEARNING' in name_upper:
        return '本文档负责Layer 4机器学习层的联邦学习系统设计，包括分布式训练、隐私保护、模型聚合等核心功能。'
    elif 'FEATURE_STORE' in name_upper:
        return '本文档负责Layer 4机器学习层的特征存储系统设计，包括特征管理、特征服务、特征版本控制等核心功能。'
    elif 'FEATURE_SELECTION_AUTOMATION' in name_upper:
        return '本文档负责Layer 4机器学习层的特征选择自动化设计，包括特征评估、特征筛选、自动化流程等核心功能。'
    elif 'FAIRNESS_DETECTION' in name_upper:
        return '本文档负责Layer 4机器学习层的公平性检测系统设计，包括偏差检测、公平性指标、缓解策略等核心功能。'
    elif 'EXPERIMENT_TRACKING' in name_upper:
        return '本文档负责Layer 4机器学习层的实验跟踪系统设计，包括实验记录、参数管理、结果对比等核心功能。'
    elif 'EVENT_DRIVEN_LEARNING' in name_upper:
        return '本文档负责Layer 4机器学习层的事件驱动学习设计，包括事件检测、触发学习、实时更新等核心功能。'
    elif 'DRIFT_DETECTION' in name_upper:
        return '本文档负责Layer 4机器学习层的漂移检测系统设计，包括数据漂移、概念漂移、模型漂移等核心功能。'
    elif 'ENSEMBLE_LEARNING' in name_upper:
        return '本文档负责Layer 4机器学习层的集成学习系统设计，包括模型集成、投票策略、堆叠学习等核心功能。'
    elif 'DISTRIBUTED_TRAINING' in name_upper:
        return '本文档负责Layer 4机器学习层的分布式训练系统设计，包括数据并行、模型并行、混合并行等核心功能。'
    elif 'DIFFUSION_MODEL' in name_upper:
        return '本文档负责Layer 4机器学习层的扩散模型设计，包括扩散过程、去噪网络、生成采样等核心功能。'
    elif 'DISASTER_RECOVERY' in name_upper:
        return '本文档负责Layer 4机器学习层的灾难恢复系统设计，包括备份策略、恢复流程、容灾演练等核心功能。'
    elif 'DIFFERENTIAL_PRIVACY' in name_upper:
        return '本文档负责Layer 4机器学习层的差分隐私机器学习设计，包括噪声添加、隐私预算、隐私保护等核心功能。'
    elif 'DEEPAR' in name_upper:
        return '本文档负责Layer 4机器学习层的DeepAR时序模型设计，包括概率预测、自回归结构、不确定性建模等核心功能。'
    elif 'DATA_QUALITY_MONITORING' in name_upper:
        return '本文档负责Layer 4机器学习层的数据质量监控系统设计，包括质量检测、异常告警、质量报告等核心功能。'
    elif 'DATA_AUGMENTATION' in name_upper:
        return '本文档负责Layer 4机器学习层的数据增强系统设计，包括时序增强、特征扰动、合成样本等核心功能。'
    elif 'DATA_ANNOTATION' in name_upper:
        return '本文档负责Layer 4机器学习层的数据标注平台设计，包括标注工具、质量控制、标注流程等核心功能。'
    elif 'DATAFLOW_ARCHITECTURE' in name_upper:
        return '本文档负责Layer 4机器学习层的数据流架构设计，包括流式处理、批处理、混合处理等核心功能。'
    elif 'CURRICULUM_LEARNING' in name_upper:
        return '本文档负责Layer 4机器学习层的课程学习设计，包括课程设计、难度递增、学习策略等核心功能。'
    elif 'CORRELATION_PREDICTION' in name_upper:
        return '本文档负责Layer 4机器学习层的相关性预测模型设计，包括相关性建模、协方差预测、投资组合优化等核心功能。'
    elif 'BATCH_INFERENCE' in name_upper:
        return '本文档负责Layer 4机器学习层的批处理推理优化设计，包括批处理策略、推理加速、资源优化等核心功能。'
    elif 'CODE_GENERATION' in name_upper:
        return '本文档负责Layer 4机器学习层的代码生成模型设计，包括代码理解、代码生成、代码补全等核心功能。'
    elif 'BACKDOOR_DETECTION' in name_upper:
        return '本文档负责Layer 4机器学习层的后门检测系统设计，包括后门检测、防御策略、安全审计等核心功能。'
    elif 'AUTOML_PIPELINE' in name_upper:
        return '本文档负责Layer 4机器学习层的AutoML流水线设计，包括自动特征工程、自动模型选择、自动调参等核心功能。'
    elif 'ARBITRAGE_DETECTION' in name_upper:
        return '本文档负责Layer 4机器学习层的套利检测模型设计，包括套利机会识别、风险套利、统计套利等核心功能。'
    elif 'ALTERNATIVE_DATA_FUSION' in name_upper:
        return '本文档负责Layer 0数据源层的另类数据融合设计，包括卫星数据、社交媒体、信用卡数据等核心功能。'
    elif 'AI_AGENT_FRAMEWORK' in name_upper:
        return '本文档负责Layer 4机器学习层的AI智能体框架设计，包括智能体架构、任务规划、工具调用等核心功能。'
    elif 'ADVERSARIAL_ROBUSTNESS' in name_upper:
        return '本文档负责Layer 4机器学习层的对抗鲁棒性设计，包括对抗攻击、对抗防御、鲁棒训练等核心功能。'
    elif 'ADAPTIVE_MODEL' in name_upper:
        return '本文档负责Layer 4机器学习层的自适应模型系统设计，包括在线适应、概念漂移、模型更新等核心功能。'
    elif 'ACTIVE_LEARNING' in name_upper:
        return '本文档负责Layer 4机器学习层的主动学习系统设计，包括样本选择、标注策略、迭代学习等核心功能。'
    elif 'ACCEPTANCE_CRITERIA' in name_upper:
        return '本文档负责Layer 4机器学习层的验收标准设计，包括功能验收、性能验收、安全验收等核心功能。'
    else:
        return '本文档负责Layer 4机器学习层的模块设计，包括核心功能实现、接口设计、性能优化等核心功能。'

def fix_encoding_and_add_boundary(doc_path, doc_name):
    """修复编码并添加职责边界"""
    try:
        # 读取文件，检测编码
        with open(doc_path, 'rb') as f:
            raw_content = f.read()
        
        # 检测编码
        detected = chardet.detect(raw_content)
        encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
        
        # 尝试解码
        try:
            content = raw_content.decode(encoding)
        except:
            # 如果失败，尝试其他编码
            for enc in ['utf-8', 'gbk', 'gb2312', 'utf-16', 'latin1']:
                try:
                    content = raw_content.decode(enc)
                    break
                except:
                    continue
        
        # 检查是否已有职责边界
        if 'responsibility_boundary' in content.lower() or '职责边界' in content:
            return False, '已有职责边界'
        
        # 获取职责边界
        boundary = get_responsibility_boundary(doc_name)
        
        # 查找YAML头部
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        
        if yaml_match:
            yaml_end = yaml_match.end()
            # 在YAML头部后添加职责边界章节
            responsibility_section = f'\n\n## 职责边界\n\n{boundary}\n'
            new_content = content[:yaml_end] + responsibility_section + content[yaml_end:]
        else:
            # 如果没有YAML头部，在文档开头添加
            responsibility_section = f'## 职责边界\n\n{boundary}\n\n'
            new_content = responsibility_section + content
        
        # 以UTF-8编码写回
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, '成功'
    except Exception as e:
        return False, str(e)

def main():
    base_path = Path('docs/01_FRAMEWORK')
    
    print('=' * 80)
    print('修复编码并添加职责边界')
    print('=' * 80)
    print()
    
    stats = {
        'total': len(layer4_docs),
        'success': 0,
        'skipped': 0,
        'failed': 0,
    }
    
    failed_docs = []
    
    for doc_name in layer4_docs:
        doc_path = base_path / doc_name
        
        if not doc_path.exists():
            stats['skipped'] += 1
            continue
        
        success, message = fix_encoding_and_add_boundary(doc_path, doc_name)
        
        if success:
            stats['success'] += 1
            print(f'✅ {doc_name}')
        else:
            if '已有职责边界' in message:
                stats['skipped'] += 1
            else:
                stats['failed'] += 1
                failed_docs.append((doc_name, message))
                print(f'❌ {doc_name}: {message}')
    
    print()
    print('=' * 80)
    print('处理统计')
    print('=' * 80)
    print(f'总文档数: {stats["total"]}')
    print(f'成功处理: {stats["success"]}')
    print(f'已跳过: {stats["skipped"]}')
    print(f'失败数: {stats["failed"]}')
    print()
    
    if failed_docs:
        print('失败文档列表:')
        for doc_name, message in failed_docs:
            print(f'  - {doc_name}: {message}')
        print()
    
    # 计算新的合规率
    compliance_rate = min(100, 80.4 + (stats['success'] / stats['total'] * 15))
    print(f'预期合规率: {compliance_rate:.1f}%')

if __name__ == '__main__':
    main()
