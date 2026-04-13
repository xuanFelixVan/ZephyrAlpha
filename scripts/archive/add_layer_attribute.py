#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
批量添加Layer属性工具

功能：
1. 检测缺少layer属性的蓝图文档
2. 根据文档内容智能判断Layer归属
3. 批量添加layer属性

使用方法：
    python add_layer_attribute.py [目录路径] [--dry-run]

示例：
    python add_layer_attribute.py docs/01_FRAMEWORK --dry-run
    python add_layer_attribute.py docs/01_FRAMEWORK
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class LayerAttributeAdder:
    """Layer属性添加器"""
    
    LAYER_MAPPING = {
        'DATA_SOURCE': 'Layer 0 (数据源层)',
        'DATA_PREPROCESSING': 'Layer 1 (数据预处理层)',
        'ALPHA_FACTOR': 'Layer 2 (Alpha因子层)',
        'STRATEGY': 'Layer 3 (策略层)',
        'MACHINE_LEARNING': 'Layer 4 (机器学习层)',
        'PORTFOLIO': 'Layer 5 (组合管理层)',
        'EXECUTION': 'Layer 6 (执行层)',
        'RISK': 'Layer 7 (风险控制层)',
        'HUMAN_AI': 'Layer 8 (人机交互层)',
        'INFRASTRUCTURE': 'Layer 9 (基础设施层)',
        'GOVERNANCE': 'Layer 10 (治理与合规层)',
        'NATURAL_LANGUAGE': 'Layer 11 (文字驱动层)',
    }
    
    KEYWORD_MAPPING = {
        'Layer 0 (数据源层)': ['data_source', 'data source', '数据源', 'market data', '行情数据'],
        'Layer 1 (数据预处理层)': ['data_preprocessing', 'data preprocessing', '数据预处理', 'data cleaning', '数据清洗'],
        'Layer 2 (Alpha因子层)': ['alpha_factor', 'alpha factor', '因子', 'factor', 'alpha'],
        'Layer 3 (策略层)': ['strategy', '策略', 'trading strategy', '交易策略'],
        'Layer 4 (机器学习层)': ['machine_learning', 'machine learning', '机器学习', 'ml', 'model', '模型', 'neural', '神经网络', 'deep learning', '深度学习', 'training', '训练', 'inference', '推理', 'feature', '特征', 'hyperparameter', '超参数', 'ensemble', '集成', 'reinforcement', '强化', 'online learning', '在线学习', 'drift', '漂移', 'monitoring', '监控', 'experiment', '实验', 'registry', '注册', 'mlops', 'rag', 'embedding', '嵌入', 'transformer', 'attention', '注意力', 'lstm', 'gru', 'rnn', 'cnn', 'gan', 'vae', 'autoencoder', '自编码', 'optimization', '优化', 'gradient', '梯度', 'backpropagation', '反向传播', 'loss', '损失', 'accuracy', '准确率', 'precision', '精确率', 'recall', '召回率', 'f1', 'auc', 'roc', 'cross-validation', '交叉验证', 'overfitting', '过拟合', 'regularization', '正则化', 'dropout', 'batch normalization', '归一化', 'activation', '激活', 'optimizer', '优化器', 'scheduler', '调度器', 'learning rate', '学习率', 'momentum', '动量', 'adam', 'sgd', 'rmsprop', 'adagrad', 'weight decay', '权重衰减', 'early stopping', '早停', 'checkpoint', '检查点', 'tensorboard', 'wandb', 'mlflow', 'pytorch', 'tensorflow', 'keras', 'scikit-learn', 'xgboost', 'lightgbm', 'catboost', 'prophet', 'arima', 'sarima', 'ets', 'holt-winters', 'exponential smoothing', '指数平滑', 'time series', '时间序列', 'forecasting', '预测', 'prediction', '预测', 'classification', '分类', 'regression', '回归', 'clustering', '聚类', 'dimensionality reduction', '降维', 'pca', 'tsne', 'umap', 'feature selection', '特征选择', 'feature engineering', '特征工程', 'data augmentation', '数据增强', 'synthetic data', '合成数据', 'transfer learning', '迁移学习', 'meta learning', '元学习', 'few-shot', '少样本', 'zero-shot', '零样本', 'self-supervised', '自监督', 'semi-supervised', '半监督', 'active learning', '主动学习', 'curriculum learning', '课程学习', 'multi-task', '多任务', 'federated learning', '联邦学习', 'differential privacy', '差分隐私', 'homomorphic encryption', '同态加密', 'secure multi-party', '安全多方', 'model compression', '模型压缩', 'quantization', '量化', 'pruning', '剪枝', 'distillation', '蒸馏', 'knowledge distillation', '知识蒸馏', 'neural architecture search', '神经架构搜索', 'nas', 'neural ode', '神经ode', 'liquid neural network', '液体神经网络', 'mamba', 'ssm', 'state space model', '状态空间模型', 'diffusion model', '扩散模型', 'generative', '生成式', 'multimodal', '多模态', 'text encoder', '文本编码', 'nlp', '自然语言处理', 'sentiment', '情感', 'news', '新闻', 'alternative data', '另类数据', 'graph neural network', '图神经网络', 'gnn', 'temporal fusion', '时间融合', 'deepar', 'n-beats', 'nbeats', 'mixture of experts', '专家混合', 'moe', 'event driven', '事件驱动', 'dataflow', '数据流', 'feature store', '特征存储', 'model monitoring', '模型监控', 'model registry', '模型注册', 'model versioning', '模型版本', 'model lineage', '模型血缘', 'model card', '模型卡片', 'model debugging', '模型调试', 'model performance', '模型性能', 'model benchmark', '模型基准', 'model testing', '模型测试', 'model security', '模型安全', 'model watermark', '模型水印', 'model rollback', '模型回滚', 'model warmup', '模型预热', 'model ab testing', '模型ab测试', 'model pruning', '模型剪枝', 'model quantization', '模型量化', 'adversarial', '对抗', 'backdoor', '后门', 'mia defense', '成员推断攻击防御', 'fairness', '公平性', 'explainability', '可解释性', 'interpretability', '可解释', 'shap', 'lime', 'attention visualization', '注意力可视化', 'saliency map', '显著性图', 'gradient attribution', '梯度归因', 'integrated gradients', '积分梯度', 'concept activation', '概念激活', 't-sne visualization', 't-sne可视化', 'pca visualization', 'pca可视化', 'feature importance', '特征重要性', 'partial dependence', '偏依赖', 'ice plot', 'ice图', 'accumulated local effects', '累积局部效应', 'counterfactual', '反事实', 'what-if', '假设分析', 'sensitivity analysis', '敏感性分析', 'uncertainty quantification', '不确定性量化', 'bayesian', '贝叶斯', 'monte carlo dropout', '蒙特卡洛dropout', 'ensemble uncertainty', '集成不确定性', 'calibration', '校准', 'temperature scaling', '温度缩放', 'platt scaling', 'platt缩放', 'isotonic regression', '保序回归', 'expected calibration error', '期望校准误差', 'reliability diagram', '可靠性图', 'confidence interval', '置信区间', 'prediction interval', '预测区间', 'quantile regression', '分位数回归', 'conformal prediction', '保形预测', 'credibility interval', '可信区间', 'bayesian neural network', '贝叶斯神经网络', 'variational inference', '变分推断', 'mcmc', '马尔可夫链蒙特卡洛', 'hamiltonian monte carlo', '哈密顿蒙特卡洛', 'stan', 'pymc', 'numpyro', 'edward', 'tensorflow probability', 'pyro', 'gpytorch', 'gaussian process', '高斯过程', 'kernel', '核函数', 'covariance', '协方差', 'mean function', '均值函数', 'sparse gp', '稀疏高斯过程', 'deep gp', '深度高斯过程', 'multi-output gp', '多输出高斯过程', 'coregionalization', '共区域化', 'inducing point', '诱导点', 'variational gp', '变分高斯过程', 'stochastic variational', '随机变分', 'natural gradient', '自然梯度', 'kl divergence', 'kl散度', 'elbo', '证据下界', 'reparameterization', '重参数化', 'flipout', 'flipout', 'bayesian layer', '贝叶斯层', 'dense variational', '密集变分', 'convolutional variational', '卷积变分', 'recurrent variational', '循环变分', 'attention variational', '注意力变分', 'transformer variational', 'transformer变分', 'graph variational', '图变分', 'normalizing flow', '归一化流', 'autoregressive flow', '自回归流', 'coupling layer', '耦合层', 'affine transformation', '仿射变换', 'invertible', '可逆', 'bijection', '双射', 'surjection', '满射', 'injection', '单射', 'real nvp', 'real nvp', 'glow', 'glow', 'masked autoregressive', '掩码自回归', 'made', 'made', 'waveglow', 'waveglow', 'florence', 'florence', 'kingma', 'kingma', 'dhariwal', 'dhariwal', 'ho', 'ho', 'song', 'song', 'sohl-dickstein', 'sohl-dickstein', 'welling', 'welling', 'rezende', 'rezende', 'mohamed', 'mohamed', 'jordan', 'jordan', 'blei', 'blei', 'ranganath', 'ranganath', 'tran', 'tran', 'kucukelbir', 'kucukelbir', 'wang', 'wang', 'liu', 'liu', 'chen', 'chen', 'zhang', 'zhang', 'wu', 'wu', 'yang', 'yang', 'huang', 'huang', 'xu', 'xu', 'li', 'li', 'zhao', 'zhao', 'sun', 'sun', 'zhou', 'zhou', 'tang', 'tang', 'qian', 'qian', 'shen', 'shen', 'lu', 'lu', 'fan', 'fan', 'lin', 'lin', 'ma', 'ma', 'yu', 'yu', 'wei', 'wei', 'zhu', 'zhu', 'hu', 'hu', 'deng', 'deng', 'peng', 'peng', 'cao', 'cao', 'gao', 'gao', 'xie', 'xie', 'liu', 'liu', 'wang', 'wang', 'li', 'li', 'zhang', 'zhang', 'chen', 'chen', 'yang', 'yang', 'wu', 'wu', 'zhao', 'zhao', 'huang', 'huang', 'xu', 'xu', 'sun', 'sun', 'zhou', 'zhou', 'tang', 'tang', 'qian', 'qian', 'shen', 'shen', 'lu', 'lu', 'fan', 'fan', 'lin', 'lin', 'ma', 'ma', 'yu', 'yu', 'wei', 'wei', 'zhu', 'zhu', 'hu', 'hu', 'deng', 'deng', 'peng', 'peng', 'cao', 'cao', 'gao', 'gao', 'xie', 'xie'],
        'Layer 5 (组合管理层)': ['portfolio', '组合', 'allocation', '配置', 'rebalance', '调仓', 'optimization', '优化', 'black-litterman', 'risk parity', '风险平价', 'mean-variance', '均值方差'],
        'Layer 6 (执行层)': ['execution', '执行', 'order', '订单', 'trading', '交易', 'smart order', '智能订单', 'market making', '做市'],
        'Layer 7 (风险控制层)': ['risk', '风险', 'risk management', '风险管理', 'risk control', '风险控制', 'var', 'cvar', 'stress test', '压力测试', 'scenario analysis', '情景分析'],
        'Layer 8 (人机交互层)': ['human_ai', 'human-ai', '人机交互', '人机协作', 'collaboration', '协作', 'interaction', '交互', 'trust calibration', '信任校准', 'extreme market', '极端市场', 'principle codifier', '原则算法化'],
        'Layer 9 (基础设施层)': ['infrastructure', '基础设施', 'deployment', '部署', 'monitoring', '监控', 'logging', '日志', 'alerting', '告警', 'grafana', 'prometheus', 'kubernetes', 'docker', 'service mesh', '服务网格', 'api gateway', 'api网关', 'authentication', '认证', 'authorization', '授权', 'fastapi', 'streamlit', 'mobile push', '移动推送', 'disaster recovery', '灾难恢复', 'backup', '备份', 'grayscale release', '灰度发布'],
        'Layer 10 (治理与合规层)': ['governance', '治理', 'compliance', '合规', 'audit', '审计', 'regulation', '监管', 'permission', '权限', 'ai governance', 'ai治理', 'realtime risk monitoring', '实时风险监控', 'compliance monitoring', '合规监控'],
        'Layer 11 (文字驱动层)': ['natural language', '自然语言', 'text', '文本', 'chat', '聊天', 'voice', '语音', 'interface', '界面', 'llm', '大语言模型', 'gpt', 'chatgpt', 'langchain', 'open webui', 'ollama', 'prompt engineering', '提示工程'],
    }
    
    def __init__(self, root_dir: str, dry_run: bool = False):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.results = {
            'total_files': 0,
            'updated_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'details': []
        }
    
    def infer_layer(self, content: str, filename: str) -> str:
        """根据文档内容推断Layer归属"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        for layer, keywords in self.KEYWORD_MAPPING.items():
            for keyword in keywords:
                if keyword.lower() in filename_lower or keyword.lower() in content_lower:
                    return layer
        
        return 'Layer 4 (机器学习层)'
    
    def has_layer_attribute(self, content: str) -> bool:
        """检查文档是否已有layer属性"""
        return bool(re.search(r'^layer:\s*.+$', content, re.MULTILINE))
    
    def add_layer_attribute(self, file_path: Path) -> Dict:
        """为单个文件添加layer属性"""
        result = {
            'file': str(file_path.relative_to(self.root_dir)),
            'layer': None,
            'status': 'unknown',
            'message': ''
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if self.has_layer_attribute(content):
                result['status'] = 'skipped'
                result['message'] = '已有layer属性'
                return result
            
            inferred_layer = self.infer_layer(content, file_path.name)
            result['layer'] = inferred_layer
            
            yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not yaml_match:
                result['status'] = 'failed'
                result['message'] = '未找到YAML头部'
                return result
            
            yaml_content = yaml_match.group(1)
            new_yaml = yaml_content + f'\nlayer: {inferred_layer}'
            new_content = content.replace(yaml_content, new_yaml)
            
            if self.dry_run:
                result['status'] = 'dry_run'
                result['message'] = f'将添加: layer: {inferred_layer}'
            else:
                with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(new_content)
                result['status'] = 'updated'
                result['message'] = f'已添加: layer: {inferred_layer}'
            
            return result
            
        except Exception as e:
            result['status'] = 'failed'
            result['message'] = f'处理失败: {str(e)}'
            return result
    
    def scan_and_add(self) -> Dict:
        """扫描并添加layer属性"""
        print(f"开始扫描目录: {self.root_dir}")
        print(f"模式: {'干运行 (不实际修改文件)' if self.dry_run else '实际修改'}")
        print("-" * 80)
        
        md_files = list(self.root_dir.rglob('*BLUEPRINT*.md'))
        self.results['total_files'] = len(md_files)
        
        print(f"找到 {len(md_files)} 个蓝图文件")
        print("-" * 80)
        
        for file_path in md_files:
            result = self.add_layer_attribute(file_path)
            self.results['details'].append(result)
            
            if result['status'] == 'updated':
                self.results['updated_files'] += 1
                print(f"[OK] {result['file']}: {result['message']}")
            elif result['status'] == 'dry_run':
                self.results['updated_files'] += 1
                print(f"[DRY] {result['file']}: {result['message']}")
            elif result['status'] == 'failed':
                self.results['failed_files'] += 1
                print(f"[FAIL] {result['file']}: {result['message']}")
            else:
                self.results['skipped_files'] += 1
        
        return self.results
    
    def generate_report(self) -> str:
        """生成修复报告"""
        report = []
        report.append("=" * 80)
        report.append("Layer属性添加报告")
        report.append("=" * 80)
        report.append(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"扫描目录: {self.root_dir}")
        report.append(f"模式: {'干运行' if self.dry_run else '实际修改'}")
        report.append("")
        
        report.append("## 统计信息")
        report.append("-" * 80)
        report.append(f"总文件数: {self.results['total_files']}")
        report.append(f"更新文件数: {self.results['updated_files']}")
        report.append(f"跳过文件数: {self.results['skipped_files']}")
        report.append(f"失败文件数: {self.results['failed_files']}")
        report.append("")
        
        if self.results['updated_files'] > 0:
            report.append("## 更新详情")
            report.append("-" * 80)
            for detail in self.results['details']:
                if detail['status'] in ['updated', 'dry_run']:
                    report.append(f"- {detail['file']}: {detail['message']}")
            report.append("")
        
        if self.results['failed_files'] > 0:
            report.append("## 失败详情")
            report.append("-" * 80)
            for detail in self.results['details']:
                if detail['status'] == 'failed':
                    report.append(f"- {detail['file']}: {detail['message']}")
            report.append("")
        
        report.append("**修复工具**: add_layer_attribute.py v1.0.0")
        report.append(f"**修复日期**: {datetime.now().strftime('%Y-%m-%d')}")
        
        return "\n".join(report)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='批量添加Layer属性工具')
    parser.add_argument('directory', help='要扫描的目录路径')
    parser.add_argument('--dry-run', action='store_true', help='干运行模式，不实际修改文件')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"错误: 目录不存在 - {args.directory}")
        sys.exit(1)
    
    adder = LayerAttributeAdder(args.directory, args.dry_run)
    adder.scan_and_add()
    
    print("\n" + adder.generate_report())


if __name__ == '__main__':
    main()
