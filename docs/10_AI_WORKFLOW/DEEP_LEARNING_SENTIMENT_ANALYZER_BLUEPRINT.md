---
module_id: AIWF_DLSA_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-04
owner: 首席架构师
standard_type: 专业机构级蓝图
applicable_scope: 深度学习情感分析模块
compliance_level: 专业标准
layer: 舆情分析层
priority: P0
estimated_effort: 60h
---

# 深度学习情感分析模块蓝图 (Deep Learning Sentiment Analyzer Blueprint)

> **模块ID**: L3_DLSA_001
> **版本**: v1.0
> **创建日期**: 2026-04-02
> **Layer定位**: Layer 3 - 舆情分析层
> **优先级**: P0 (阻断性)
> **预计工作量**: 60小时

---

## 一、模块概述

### 1.1 设计背景

**业务需求**:
- 提升情感分析的准确性和深度
- 从基础的情感评分升级到深度学习模型
- 实现多维度情感分析（正面、负面、中性、恐惧、贪婪等）
- 支持金融领域专业情感分析

**技术痛点**:
- 当前使用jieba + snownlp，准确率有限
- 缺少深度学习模型应用
- 缺少金融领域专业模型
- 缺少多维度情感评估

**预期价值**:
- 情感分析准确率提升至85%以上
- 实现多维度情感分析
- 提升金融领域情感分析专业性
- 为策略提供更精准的情感信号

### 1.2 模块定位

**Layer归属**: Layer 3 - 舆情分析层
**模块类别**: 核心分析模块
**架构角色**: 情感分析引擎，为策略执行层提供情感信号

---

## 二、详细架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                    深度学习情感分析模块架构                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          DLSentimentAnalyzer (主分析器)                       │  │
│  │  - 模型管理                                                   │  │
│  │  - 情感分析                                                   │  │
│  │  - 结果聚合                                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           ↓                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          模型层                                               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────┐ │  │
│  │  │FinBERT      │  │BERT-Chinese │  │FinGPT       │  │自研  │ │  │
│  │  │Model        │  │Model        │  │Model        │  │Model │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └──────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           ↓                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          分析引擎                                             │  │
│  │  - 文本预处理 (TextPreprocessor)                              │  │
│  │  - 情感推理 (SentimentInference)                              │  │
│  │  - 结果后处理 (ResultPostprocessor)                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           ↓                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          服务层                                               │  │
│  │  - 批量分析服务 (BatchAnalysisService)                        │  │
│  │  - 实时分析服务 (RealTimeAnalysisService)                     │  │
│  │  - 模型微调服务 (ModelFineTuningService)                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件设计

#### 2.2.1 FinBERT模型集成

**模型选择**: FinBERT (金融领域预训练BERT模型)

**模型特点**:
- 基于BERT架构
- 在金融文本上预训练
- 支持三分类情感（正面、负面、中性）
- 准确率高（85%+）

**模型来源**:
- Hugging Face: `ProsusAI/finbert`
- GitHub: https://github.com/ProsusAI/finBERT

**模型配置**:
```python
{
    "model_name": "ProsusAI/finbert",
    "model_type": "bert",
    "num_labels": 3,
    "labels": ["positive", "negative", "neutral"],
    "max_length": 512,
    "batch_size": 16,
    "device": "cuda"  # or "cpu"
}
```

---

#### 2.2.2 BERT-Chinese模型集成

**模型选择**: BERT-Base-Chinese (中文预训练BERT模型)

**模型特点**:
- 基于BERT架构
- 在中文文本上预训练
- 支持中文情感分析
- 可微调用于金融领域

**模型来源**:
- Hugging Face: `bert-base-chinese`

**模型配置**:
```python
{
    "model_name": "bert-base-chinese",
    "model_type": "bert",
    "num_labels": 3,
    "labels": ["正面", "负面", "中性"],
    "max_length": 512,
    "batch_size": 16,
    "device": "cuda"
}
```

---

#### 2.2.3 多维度情感分析

**情感维度**:
1. **基础情感**: 正面、负面、中性
2. **情绪维度**: 恐惧、贪婪、愤怒、惊讶、悲伤、喜悦
3. **强度维度**: 强烈、中等、微弱
4. **时间维度**: 短期、中期、长期影响

**分析流程**:
```
文本输入 → 文本预处理 → 模型推理 → 结果后处理 → 多维度输出
```

**输出格式**:
```python
{
    "text": "原始文本",
    "basic_sentiment": {
        "label": "positive",
        "confidence": 0.85
    },
    "emotion": {
        "fear": 0.1,
        "greed": 0.6,
        "anger": 0.05,
        "surprise": 0.15,
        "sadness": 0.05,
        "joy": 0.05
    },
    "intensity": {
        "label": "strong",
        "score": 0.75
    },
    "time_horizon": {
        "short_term": 0.3,
        "medium_term": 0.5,
        "long_term": 0.2
    },
    "keywords": ["关键词1", "关键词2"],
    "entities": ["股票代码", "公司名称"]
}
```

---

### 2.3 模型微调策略

#### 2.3.1 微调数据准备

**数据来源**:
- 中文财经新闻（已采集）
- 财经社交媒体数据（Twitter、Reddit）
- 财报文本
- 分析师报告

**数据标注**:
- 使用现有情感分析结果作为弱标签
- 人工标注部分高质量数据
- 使用主动学习选择标注样本

**数据增强**:
- 同义词替换
- 回译（中→英→中）
- 随机插入/删除

---

#### 2.3.2 微调流程

```
准备数据 → 数据预处理 → 模型加载 → 微调训练 → 模型评估 → 模型部署
```

**微调参数**:
```python
{
    "learning_rate": 2e-5,
    "batch_size": 16,
    "num_epochs": 3,
    "warmup_steps": 500,
    "weight_decay": 0.01,
    "max_grad_norm": 1.0,
    "save_steps": 500,
    "eval_steps": 500
}
```

---

## 三、接口定义

### 3.1 主接口类

```python
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import torch
from transformers import BertTokenizer, BertForSequenceClassification


@dataclass
class SentimentConfig:
    """情感分析配置"""
    model_name: str
    model_type: str
    device: str = "cuda"
    max_length: int = 512
    batch_size: int = 16
    use_fp16: bool = False


@dataclass
class SentimentResult:
    """情感分析结果"""
    text: str
    basic_sentiment: Dict[str, Any]
    emotion: Dict[str, float]
    intensity: Dict[str, Any]
    time_horizon: Dict[str, float]
    keywords: List[str]
    entities: List[str]
    confidence: float


class DLSentimentAnalyzer:
    """深度学习情感分析主类"""
    
    def __init__(self, config: SentimentConfig):
        """初始化情感分析器
        
        Args:
            config: 情感分析配置
        """
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = torch.device(config.device)
        self._load_model()
    
    def _load_model(self) -> None:
        """加载预训练模型"""
        pass
    
    def analyze(
        self,
        text: str,
        return_all_scores: bool = False
    ) -> SentimentResult:
        """分析单条文本情感
        
        Args:
            text: 待分析文本
            return_all_scores: 是否返回所有分数
            
        Returns:
            情感分析结果
        """
        pass
    
    def analyze_batch(
        self,
        texts: List[str],
        return_all_scores: bool = False
    ) -> List[SentimentResult]:
        """批量分析文本情感
        
        Args:
            texts: 待分析文本列表
            return_all_scores: 是否返回所有分数
            
        Returns:
            情感分析结果列表
        """
        pass
    
    def fine_tune(
        self,
        train_data: List[Dict[str, Any]],
        val_data: Optional[List[Dict[str, Any]]] = None,
        output_dir: str = "./models/finbert_finetuned"
    ) -> Dict[str, Any]:
        """微调模型
        
        Args:
            train_data: 训练数据
            val_data: 验证数据
            output_dir: 输出目录
            
        Returns:
            微调结果
        """
        pass
    
    def save_model(self, output_dir: str) -> None:
        """保存模型
        
        Args:
            output_dir: 输出目录
        """
        pass
    
    def load_model(self, model_dir: str) -> None:
        """加载模型
        
        Args:
            model_dir: 模型目录
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息
        
        Returns:
            模型信息
        """
        pass
```

### 3.2 文本预处理接口

```python
class TextPreprocessor:
    """文本预处理器"""
    
    def __init__(self):
        """初始化预处理器"""
        pass
    
    def preprocess(self, text: str) -> str:
        """预处理文本
        
        Args:
            text: 原始文本
            
        Returns:
            预处理后的文本
        """
        pass
    
    def clean_text(self, text: str) -> str:
        """清洗文本
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        pass
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词
        
        Args:
            text: 文本
            top_k: 返回前k个关键词
            
        Returns:
            关键词列表
        """
        pass
    
    def extract_entities(self, text: str) -> List[str]:
        """提取实体
        
        Args:
            text: 文本
            
        Returns:
            实体列表
        """
        pass
```

### 3.3 情感推理接口

```python
class SentimentInference:
    """情感推理引擎"""
    
    def __init__(self, model, tokenizer, device):
        """初始化推理引擎
        
        Args:
            model: 模型
            tokenizer: 分词器
            device: 设备
        """
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
    
    def inference(self, text: str) -> Dict[str, Any]:
        """推理单条文本
        
        Args:
            text: 文本
            
        Returns:
            推理结果
        """
        pass
    
    def inference_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """批量推理
        
        Args:
            texts: 文本列表
            
        Returns:
            推理结果列表
        """
        pass
    
    def predict_emotion(self, text: str) -> Dict[str, float]:
        """预测情绪
        
        Args:
            text: 文本
            
        Returns:
            情绪分数
        """
        pass
    
    def predict_intensity(self, text: str) -> Dict[str, Any]:
        """预测强度
        
        Args:
            text: 文本
            
        Returns:
            强度分数
        """
        pass
```

---

## 四、数据模型

### 4.1 模型存储结构

```
models/
├── finbert/
│   ├── config.json
│   ├── pytorch_model.bin
│   ├── vocab.txt
│   └── tokenizer_config.json
├── bert-base-chinese/
│   ├── config.json
│   ├── pytorch_model.bin
│   ├── vocab.txt
│   └── tokenizer_config.json
└── finbert_finetuned/
    ├── config.json
    ├── pytorch_model.bin
    ├── vocab.txt
    ├── tokenizer_config.json
    └── training_args.bin
```

### 4.2 分析结果存储

```sql
CREATE TABLE sentiment_analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_hash TEXT NOT NULL,
    text TEXT NOT NULL,
    source TEXT NOT NULL,
    basic_sentiment TEXT NOT NULL,  -- JSON
    emotion TEXT,  -- JSON
    intensity TEXT,  -- JSON
    time_horizon TEXT,  -- JSON
    keywords TEXT,  -- JSON
    entities TEXT,  -- JSON
    confidence REAL NOT NULL,
    model_name TEXT NOT NULL,
    analyzed_at TIMESTAMP NOT NULL,
    INDEX idx_text_hash (text_hash),
    INDEX idx_source (source),
    INDEX idx_analyzed_at (analyzed_at)
);
```

---

## 五、实施计划

### 5.1 第5-6周: FinBERT模型集成

#### 5.1.1 环境准备

**步骤1: 安装Python 3.9+环境**

```bash
# Windows系统
# 下载Python 3.9+安装包
# https://www.python.org/downloads/

# 验证安装
python --version  # 应显示 Python 3.9.x 或更高版本

# 创建虚拟环境
python -m venv zephyr_env

# 激活虚拟环境
zephyr_env\Scripts\activate  # Windows
```

**步骤2: 配置GPU驱动（如果有GPU）**

```bash
# 检查NVIDIA GPU
nvidia-smi

# 安装CUDA Toolkit 11.8+
# 下载地址: https://developer.nvidia.com/cuda-downloads

# 安装cuDNN 8.6+
# 下载地址: https://developer.nvidia.com/cudnn

# 验证CUDA安装
nvcc --version

# 安装PyTorch GPU版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**步骤3: 安装必要的依赖库**

```bash
# 安装核心依赖
pip install transformers==4.35.0
pip install torch==2.1.0
pip install tokenizers==0.14.1
pip install accelerate==0.24.1
pip install datasets==2.14.5
pip install scikit-learn==1.3.2
pip install numpy==1.24.3
pip install pandas==2.1.1

# 安装NLP相关库
pip install jieba==0.42.1
pip install snownlp==0.12.3

# 安装工具库
pip install tqdm==4.66.1
pip install requests==2.31.0
pip install python-dotenv==1.0.0

# 生成requirements.txt
pip freeze > requirements.txt
```

**环境验证脚本**:

```python
# verify_environment.py
import sys
import torch
import transformers

print("=" * 60)
print("环境验证报告")
print("=" * 60)

print(f"\n✅ Python版本: {sys.version}")
print(f"✅ PyTorch版本: {torch.__version__}")
print(f"✅ Transformers版本: {transformers.__version__}")

if torch.cuda.is_available():
    print(f"✅ CUDA可用: {torch.cuda.is_available()}")
    print(f"✅ CUDA版本: {torch.version.cuda}")
    print(f"✅ GPU数量: {torch.cuda.device_count()}")
    print(f"✅ GPU名称: {torch.cuda.get_device_name(0)}")
    print(f"✅ GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("⚠️ CUDA不可用，将使用CPU模式")

print("\n" + "=" * 60)
print("环境验证完成！")
print("=" * 60)
```

---

#### 5.1.2 下载FinBERT预训练模型

**方法1: 使用Hugging Face Transformers自动下载（推荐）**

```python
# download_finbert.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

def download_finbert(save_dir: str = "./models/finbert"):
    """下载FinBERT预训练模型
    
    Args:
        save_dir: 模型保存目录
    """
    print("=" * 60)
    print("开始下载FinBERT预训练模型")
    print("=" * 60)
    
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    print("\n📥 正在下载tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    tokenizer.save_pretrained(save_dir)
    print(f"✅ Tokenizer已保存到: {save_dir}")
    
    print("\n📥 正在下载模型...")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    model.save_pretrained(save_dir)
    print(f"✅ 模型已保存到: {save_dir}")
    
    print("\n" + "=" * 60)
    print("FinBERT模型下载完成！")
    print("=" * 60)
    
    # 验证模型
    print("\n🔍 验证模型...")
    test_text = "Apple's revenue increased by 20% in Q4 2026."
    inputs = tokenizer(test_text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    print(f"\n测试文本: {test_text}")
    print(f"预测结果: {predictions}")
    print(f"情感标签: {['负面', '中性', '正面'][torch.argmax(predictions).item()]}")
    
    return tokenizer, model

if __name__ == "__main__":
    import torch
    tokenizer, model = download_finbert()
```

**方法2: 手动下载模型文件**

```bash
# 创建模型目录
mkdir -p models/finbert

# 使用Git LFS下载（需要安装Git LFS）
git lfs install
git clone https://huggingface.co/ProsusAI/finbert models/finbert

# 或者手动下载以下文件到 models/finbert/ 目录：
# 1. config.json - 模型配置文件
# 2. pytorch_model.bin - 模型权重文件（约420MB）
# 3. vocab.txt - 词汇表文件
# 4. tokenizer_config.json - Tokenizer配置文件
# 5. special_tokens_map.json - 特殊token映射

# 下载地址: https://huggingface.co/ProsusAI/finbert/tree/main
```

**方法3: 使用Hugging Face Hub CLI**

```bash
# 安装Hugging Face Hub
pip install huggingface-hub

# 登录Hugging Face（可选，如果模型是私有的）
huggingface-cli login

# 下载模型
huggingface-cli download ProsusAI/finbert --local-dir ./models/finbert

# 验证下载
ls -lh models/finbert/
```

**模型文件清单**:

```
models/finbert/
├── config.json              # 模型配置（2KB）
├── pytorch_model.bin        # 模型权重（420MB）
├── vocab.txt                # 词汇表（226KB）
├── tokenizer_config.json    # Tokenizer配置（201B）
└── special_tokens_map.json  # 特殊token映射（112B）
```

**验证模型下载**:

```python
# verify_finbert.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def verify_finbert(model_dir: str = "./models/finbert"):
    """验证FinBERT模型
    
    Args:
        model_dir: 模型目录
    """
    print("=" * 60)
    print("验证FinBERT模型")
    print("=" * 60)
    
    # 加载模型
    print("\n📥 加载tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    print("✅ Tokenizer加载成功")
    
    print("\n📥 加载模型...")
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    print("✅ 模型加载成功")
    
    # 测试推理
    test_texts = [
        "Apple's revenue increased by 20% in Q4 2026.",
        "The company reported a significant loss in the last quarter.",
        "The stock price remained stable during the trading session."
    ]
    
    print("\n" + "=" * 60)
    print("测试推理")
    print("=" * 60)
    
    for text in test_texts:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        labels = ["负面", "中性", "正面"]
        predicted_label = labels[torch.argmax(predictions).item()]
        confidence = torch.max(predictions).item()
        
        print(f"\n文本: {text}")
        print(f"预测: {predicted_label} (置信度: {confidence:.2%})")
        print(f"分数: 负面={predictions[0][0]:.4f}, 中性={predictions[0][1]:.4f}, 正面={predictions[0][2]:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ FinBERT模型验证通过！")
    print("=" * 60)

if __name__ == "__main__":
    verify_finbert()
```

---

#### 5.1.3 开发任务清单

**任务清单**:
- [x] 安装Python 3.9+环境
- [x] 配置GPU驱动（如果有GPU）
- [x] 安装必要的依赖库
- [x] 下载FinBERT预训练模型
- [x] 验证模型下载
- [ ] 开发模型加载接口
- [ ] 开发文本预处理模块
- [ ] 开发情感推理接口
- [ ] 开发批量分析接口
- [ ] 性能优化（GPU加速、批处理）
- [ ] 测试和验证

**交付物**:
- 环境配置文档
- FinBERT模型文件
- DLSentimentAnalyzer代码
- 测试报告

---

### 5.2 第7-8周: 深度学习情感分析模块开发

**任务清单**:
- [ ] 设计模块架构
- [ ] 开发多维度情感分析引擎
- [ ] 开发情绪识别模块
- [ ] 开发强度评估模块
- [ ] 开发时间维度分析
- [ ] 开发可视化界面
- [ ] 测试和验证

**交付物**:
- 多维度情感分析代码
- 可视化界面
- 测试报告

---

### 5.3 第9周: 模型微调和优化

**任务清单**:
- [ ] 准备中文金融语料
- [ ] 数据标注和增强
- [ ] 微调FinBERT模型
- [ ] 评估模型性能
- [ ] 优化推理速度
- [ ] 模型压缩和量化
- [ ] 测试和验证

**交付物**:
- 微调后的模型
- 性能评估报告
- 优化后的代码

---

### 5.4 第10周: 集成和测试

**任务清单**:
- [ ] 集成到现有系统
- [ ] 开发单元测试
- [ ] 开发集成测试
- [ ] 性能测试和优化
- [ ] 文档编写
- [ ] 部署上线

**交付物**:
- 集成后的系统
- 测试报告
- 技术文档

---

## 六、测试策略

### 6.1 单元测试

**测试范围**:
- 文本预处理功能测试
- 模型加载功能测试
- 情感推理功能测试
- 批量分析功能测试
- 结果后处理功能测试

**测试工具**:
- pytest
- unittest.mock

---

### 6.2 性能测试

**测试指标**:
- 单条文本分析速度
- 批量分析速度
- GPU利用率
- 内存使用

**性能目标**:
- 单条文本: < 100ms (GPU), < 500ms (CPU)
- 批量分析: > 100条/秒 (GPU), > 20条/秒 (CPU)
- GPU利用率: > 80%
- 内存使用: < 4GB

---

### 6.3 准确性测试

**测试数据**:
- 人工标注的测试集（1000条）
- 公开数据集（如Financial PhraseBank）

**测试指标**:
- 准确率 (Accuracy)
- 精确率 (Precision)
- 召回率 (Recall)
- F1分数

**准确性目标**:
- 准确率: > 85%
- F1分数: > 0.85

---

## 七、风险管理

### 7.1 技术风险

| 风险项 | 概率 | 影响 | 缓解措施 |
|--------|------|------|----------|
| 模型性能不足 | 中 | 高 | 使用预训练模型，进行微调 |
| GPU资源不足 | 中 | 中 | 使用CPU推理，优化模型 |
| 微调数据不足 | 中 | 中 | 数据增强，使用公开数据集 |
| 推理速度慢 | 中 | 中 | 模型压缩，批处理优化 |

### 7.2 资源风险

| 风险项 | 概率 | 影响 | 缓解措施 |
|--------|------|------|----------|
| GPU不可用 | 中 | 中 | 使用CPU推理，云GPU服务 |
| 存储空间不足 | 低 | 低 | 模型压缩，定期清理 |
| 计算资源不足 | 低 | 中 | 使用云服务，优化算法 |

---

## 八、验收标准

### 8.1 功能验收

- [ ] FinBERT模型集成完成
- [ ] 多维度情感分析功能正常
- [ ] 批量分析功能正常
- [ ] 模型微调功能正常
- [ ] 可视化界面正常

### 8.2 性能验收

- [ ] 单条文本分析速度达标
- [ ] 批量分析速度达标
- [ ] GPU利用率达标
- [ ] 内存使用在合理范围

### 8.3 准确性验收

- [ ] 准确率 > 85%
- [ ] F1分数 > 0.85
- [ ] 多维度情感分析准确率 > 80%

---

## 九、相关文档

| 文档 | 说明 |
|------|------|
| [Layer 3改进实施计划](./LAYER3_IMPROVEMENT_IMPLEMENTATION_PLAN.md) | 总体实施计划 |
| [舆情分析层对比报告](./LAYER3_SENTIMENT_ANALYSIS_COMPARISON_REPORT.md) | 专业对比分析 |
| [另类数据集成蓝图](./ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT.md) | 数据源扩展 |

---

**版本**: v1.0 | **更新**: 2026-04-02 | **状态**: ✅ 活跃
