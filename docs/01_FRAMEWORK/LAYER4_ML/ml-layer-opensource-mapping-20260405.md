---
module_id: 01_FRAMEWORK_LAYER4_ML_ML_LAYER_OPENSOURCE_MAPPING_20260405
layer: layer_01
version: 1.0.0
status: Active
responsibility:
  - Ml Layer Opensource Mapping 20260405相关业务
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 专业标准
---

## 1. 核心原则



### 1.1 开源选择标准



| 标准 | 权重 | 说明 |

|------|------|------|

| 成熟度 | 30% | 生产环境验证、版本稳定 |

| 社区活跃度 | 25% | GitHub Stars、近期更新 |

| 许可证 | 20% | Apache 2.0、MIT、BSD优先 |

| 企业支持 | 15% | 大公司背书、商业支持 |

| 可扩展性 | 10% | 插件系统、API完善 |



### 1.2 自研决策矩阵



| 场景 | 开源 | 自研 | 决策依据 |

|------|------|------|----------|

| 基础设施 | ✅ | ❌ | 成熟方案多、无差异化 |

| 模型架构 | ✅ | 部分 | 基础模型开源、量化定制自研 |

| 训练优化 | ✅ | ❌ | 优化充分、无需重复 |

| 模型治理 | ✅ | 部分 | 框架开源、流程定制 |

| 安全隐私 | 部分 | 部分 | 加密库开源、策略自研 |

| 部署推理 | ✅ | ❌ | 生产级方案成熟 |

| 量化专用 | 部分 | ✅ | 核心策略必须自研 |

| LLM相关 | ✅ | 部分 | 基础模型开源、Prompt自研 |



---



## 2. 详细映射表



### 2.1 基础设施类 (必须使用开源)



#### 实验追踪 (EXPERIMENT_TRACKING)



| 项目 | 推荐度 | 许可证 | Stars | 特点 |

|------|--------|--------|-------|------|

| **MLflow** | ⭐⭐⭐⭐⭐ | Apache 2.0 | 18k+ | 全功能、易部署、社区活跃 |

| W&B | ⭐⭐⭐⭐⭐ | 商业 | 9k+ | 可视化强、协作好 |

| Neptune | ⭐⭐⭐⭐ | 商业 | - | 轻量级、易用 |

| ClearML | ⭐⭐⭐⭐ | Apache 2.0 | 5k+ | 开源免费 |



**推荐方案**: MLflow (首选) + W&B (可选)



```python

import mlflow



mlflow.start_run()

mlflow.log_param("learning_rate", 0.01)

mlflow.log_metric("accuracy", 0.95)

mlflow.log_artifact("model.pkl")

mlflow.end_run()

```



#### 超参数优化 (HYPERPARAMETER_OPTIMIZATION)



| 项目 | 推荐度 | 许可证 | Stars | 特点 |

|------|--------|--------|-------|------|

| **Optuna** | ⭐⭐⭐⭐⭐ | MIT | 10k+ | 剪枝算法、易用 |

| Ray Tune | ⭐⭐⭐⭐⭐ | Apache 2.0 | 5k+ | 分布式、可扩展 |

| Hyperopt | ⭐⭐⭐⭐ | BSD | 7k+ | 经典方案 |

| Nevergrad | ⭐⭐⭐⭐ | BSD | 1k+ | 无梯度优化 |



**推荐方案**: Optuna (首选)



```python

import optuna



def objective(trial):

    lr = trial.suggest_float("lr", 1e-5, 1e-1, log=True)

    return train_and_evaluate(lr)



study = optuna.create_study(direction="maximize")

study.optimize(objective, n_trials=100)

```



#### 分布式训练 (DISTRIBUTED_TRAINING)



| 项目 | 推荐度 | 许可证 | Stars | 特点 |

|------|--------|--------|-------|------|

| **DeepSpeed** | ⭐⭐⭐⭐⭐ | MIT | 35k+ | ZeRO优化、内存高效 |

| FSDP | ⭐⭐⭐⭐⭐ | BSD | - | PyTorch原生 |

| Megatron-LM | ⭐⭐⭐⭐⭐ | Apache 2.0 | 10k+ | NVIDIA支持 |

| Colossal-AI | ⭐⭐⭐⭐ | Apache 2.0 | 38k+ | 多种并行策略 |



**推荐方案**: DeepSpeed (首选)



```python

import deepspeed



ds_config = {

    "train_batch_size": 16,

    "zero_optimization": {"stage": 2}

}



model_engine, _, _, _ = deepspeed.initialize(

    model=model, config=ds_config

)

```



---



### 2.2 模型架构类 (开源为主)



#### 时序预测模型



| 蓝图 | 推荐项目 | Stars | 说明 |

|------|----------|-------|------|

| TFT | pytorch-forecasting | 3k+ | 内置TFT实现 |

| DeepAR | GluonTS | 4k+ | AWS官方支持 |

| N-BEATS | pytorch-forecasting | 3k+ | 内置N-BEATS |

| Neural ODE | torchdiffeq | 5k+ | 原版实现 |



**推荐方案**: pytorch-forecasting (统一框架)



```python

from pytorch_forecasting import TemporalFusionTransformer



tft = TemporalFusionTransformer.from_dataset(

    training,

    learning_rate=0.03,

    hidden_size=16

)

```



#### 图神经网络 (GRAPH_NEURAL_NETWORK)



| 项目 | 推荐度 | Stars | 特点 |

|------|--------|-------|------|

| **PyG** | ⭐⭐⭐⭐⭐ | 21k+ | 最全面、性能好 |

| DGL | ⭐⭐⭐⭐⭐ | 13k+ | AWS支持 |

| GraphNets | ⭐⭐⭐⭐ | 5k+ | DeepMind原版 |



**推荐方案**: PyG (首选)



```python

from torch_geometric.nn import GCNConv



class GNN(torch.nn.Module):

    def __init__(self):

        super().__init__()

        self.conv1 = GCNConv(num_features, 16)

        self.conv2 = GCNConv(16, num_classes)

```



#### 扩散模型 (DIFFUSION_MODEL)



| 项目 | 推荐度 | Stars | 特点 |

|------|--------|-------|------|

| **diffusers** | ⭐⭐⭐⭐⭐ | 25k+ | Hugging Face官方 |

| DDPM | ⭐⭐⭐⭐ | 5k+ | 原版实现 |

| Score-Based | ⭐⭐⭐⭐ | 3k+ | 基于分数 |



**推荐方案**: diffusers (首选)



```python

from diffusers import DDPMPipeline



pipeline = DDPMPipeline.from_pretrained("google/ddpm-cifar10-32")

image = pipeline().images[0]

```



---



### 2.3 部署推理类 (必须使用开源)



#### 推理服务 (INFERENCE_ACCELERATION)



| 项目 | 推荐度 | Stars | 特点 |

|------|--------|-------|------|

| **Triton** | ⭐⭐⭐⭐⭐ | 8k+ | NVIDIA支持、高性能 |

| **vLLM** | ⭐⭐⭐⭐⭐ | 25k+ | LLM专用、PagedAttention |

| TorchServe | ⭐⭐⭐⭐⭐ | 4k+ | AWS/Meta支持 |

| ONNX Runtime | ⭐⭐⭐⭐⭐ | 14k+ | 跨平台、高效 |



**推荐方案**: 

- 通用推理: Triton

- LLM推理: vLLM



```python

# Triton部署

import tritonclient.http as httpclient



client = httpclient.InferenceServerClient(url="localhost:8000")

response = client.infer("model_name", inputs)

```



```python

# vLLM推理

from vllm import LLM, SamplingParams



llm = LLM(model="meta-llama/Llama-2-7b-hf")

outputs = llm.generate(prompts, SamplingParams())

```



#### 模型监控 (MODEL_MONITORING)



| 项目 | 推荐度 | Stars | 特点 |

|------|--------|-------|------|

| **Evidently AI** | ⭐⭐⭐⭐⭐ | 5k+ | 漂移检测、可视化 |

| Alibi Detect | ⭐⭐⭐⭐⭐ | 6k+ | 异常检测全面 |

| WhyLabs | ⭐⭐⭐⭐ | 商业 | 企业级监控 |



**推荐方案**: Evidently AI



```python

from evidently.report import Report

from evidently.metric_preset import DataDriftPreset



report = Report(metrics=[DataDriftPreset()])

report.run(reference_data=ref, current_data=cur)

```



---



### 2.4 数据管理类 (开源为主)



#### 特征存储 (FEATURE_STORE)



| 项目 | 推荐度 | Stars | 特点 |

|------|--------|-------|------|

| **Feast** | ⭐⭐⭐⭐⭐ | 5k+ | 生产级、可扩展 |

| Hopsworks | ⭐⭐⭐⭐ | 商业 | 企业级功能 |

| Tecton | ⭐⭐⭐⭐ | 商业 | 托管服务 |



**推荐方案**: Feast



```python

from feast import FeatureStore



store = FeatureStore(repo_path=".")

features = store.get_online_features(

    features=["user:age", "user:gender"],

    entity_rows=[{"user_id": 1001}]

).to_dict()

```



#### 数据版本控制 (DATA_VERSION_CONTROL)



| 项目 | 推荐度 | Stars | 特点 |

|------|--------|-------|------|

| **DVC** | ⭐⭐⭐⭐⭐ | 14k+ | Git工作流集成 |

| LakeFS | ⭐⭐⭐⭐ | 4k+ | S3兼容、分支管理 |

| Pachyderm | ⭐⭐⭐⭐ | 6k+ | 数据管道 |



**推荐方案**: DVC



```bash

dvc init

dvc add data/dataset.csv

git add data/dataset.csv.dvc

git commit -m "Add dataset"

dvc push

```



---



### 2.5 安全隐私类 (开源+自研混合)



#### 差分隐私 (DIFFERENTIAL_PRIVACY)



| 项目 | 推荐度 | Stars | 特点 |

|------|--------|-------|------|

| **Opacus** | ⭐⭐⭐⭐⭐ | 1.5k+ | Meta支持、PyTorch原生 |

| Diffprivlib | ⭐⭐⭐⭐ | 500+ | IBM支持、算法丰富 |

| TF Privacy | ⭐⭐⭐⭐ | 2k+ | Google支持 |



**推荐方案**: Opacus



```python

from opacus import PrivacyEngine



privacy_engine = PrivacyEngine()

model, optimizer, dataloader = privacy_engine.make_private(

    module=model,

    optimizer=optimizer,

    data_loader=dataloader,

    noise_multiplier=1.1,

    max_grad_norm=1.0

)

```



#### 安全多方计算 (SECURE_MULTI_PARTY_COMPUTATION)



| 项目 | 推荐度 | Stars | 特点 |

|------|--------|-------|------|

| **CrypTen** | ⭐⭐⭐⭐⭐ | 1.5k+ | Meta支持、易用 |

| MP-SPDZ | ⭐⭐⭐⭐ | 500+ | 协议全面 |

| PySyft | ⭐⭐⭐⭐ | 9k+ | OpenMined支持 |



**推荐方案**: CrypTen



```python

import crypten



crypten.init()

x_enc = crypten.encrypt(x)

y_enc = crypten.encrypt(y)

z_enc = x_enc + y_enc

```



---



### 2.6 量化专用类 (核心自研)



#### 量化研究平台



| 项目 | 推荐度 | Stars | 特点 |

|------|--------|-------|------|

| **Qlib** | ⭐⭐⭐⭐⭐ | 15k+ | 微软支持、全流程 |

| **FinRL** | ⭐⭐⭐⭐⭐ | 10k+ | 强化学习交易 |

| Backtrader | ⭐⭐⭐⭐ | 12k+ | 回测框架 |

| VectorBT | ⭐⭐⭐⭐⭐ | 5k+ | 向量化回测 |



**推荐方案**: Qlib (研究) + 自研 (核心策略)



```python

import qlib

from qlib.constant import REG_CN



qlib.init(provider_uri='./qlib_data/cn_data', region=REG_CN)



from qlib.data.dataset import DatasetH

dataset = DatasetH(handler={"class": "Alpha360"})

```



#### 风险建模



| 项目 | 推荐度 | Stars | 特点 |

|------|--------|-------|------|

| **arch** | ⭐⭐⭐⭐⭐ | 1k+ | GARCH族全面 |

| **PyPortfolioOpt** | ⭐⭐⭐⭐⭐ | 4k+ | 组合优化 |

| Riskfolio-Lib | ⭐⭐⭐⭐ | 3k+ | 风险模型丰富 |



**推荐方案**: arch (波动率) + PyPortfolioOpt (组合)



```python

from arch import arch_model



am = arch_model(returns, vol='Garch', p=1, q=1)

res = am.fit()

forecast = res.forecast(horizon=1)

```



---



### 2.7 LLM相关类 (开源为主)



#### LLM微调 (LLM_FINE_TUNING)



| 项目 | 推荐度 | Stars | 特点 |

|------|--------|-------|------|

| **PEFT** | ⭐⭐⭐⭐⭐ | 15k+ | LoRA、QLoRA |

| DeepSpeed-Chat | ⭐⭐⭐⭐⭐ | 4k+ | RLHF训练 |

| Axolotl | ⭐⭐⭐⭐ | 7k+ | 配置化微调 |



**推荐方案**: PEFT



```python

from peft import LoraConfig, get_peft_model



config = LoraConfig(r=8, lora_alpha=32)

model = get_peft_model(model, config)

```



#### RAG系统 (RAG_SYSTEM)



| 项目 | 推荐度 | Stars | 特点 |

|------|--------|-------|------|

| **LlamaIndex** | ⭐⭐⭐⭐⭐ | 35k+ | 数据连接丰富 |

| LangChain | ⭐⭐⭐⭐⭐ | 100k+ | 生态全面 |

| Haystack | ⭐⭐⭐⭐⭐ | 17k+ | 生产级RAG |



**推荐方案**: LlamaIndex



```python

from llama_index import VectorStoreIndex, SimpleDirectoryReader



documents = SimpleDirectoryReader('data').load_data()

index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()

response = query_engine.query("question")

```



---



## 3. 实施路线图



### 3.1 第一阶段 (1个月) - 基础设施



| 模块 | 开源项目 | 工作量 |

|------|----------|--------|

| 实验追踪 | MLflow | 2天 |

| 超参数优化 | Optuna | 2天 |

| 数据版本控制 | DVC | 1天 |

| 特征存储 | Feast | 3天 |



### 3.2 第二阶段 (2个月) - 训练部署



| 模块 | 开源项目 | 工作量 |

|------|----------|--------|

| 分布式训练 | DeepSpeed | 3天 |

| 混合精度训练 | PyTorch AMP | 1天 |

| 推理服务 | Triton | 3天 |

| 模型监控 | Evidently | 2天 |



### 3.3 第三阶段 (3个月) - 量化专用



| 模块 | 开源项目 | 工作量 |

|------|----------|--------|

| 量化研究平台 | Qlib | 5天 |

| 强化学习交易 | FinRL | 5天 |

| 风险建模 | arch/PyPortfolioOpt | 3天 |

| 核心策略 | 自研 | 20天 |



---



## 4. 避免重复造轮子清单



### 4.1 绝对不要自研



| 模块 | 原因 | 开源替代 |

|------|------|----------|

| 实验追踪 | 成熟方案多 | MLflow |

| 超参数优化 | 算法复杂 | Optuna |

| 分布式训练 | 优化充分 | DeepSpeed |

| 推理服务 | 生产级方案 | Triton |

| 数据版本控制 | Git集成成熟 | DVC |

| 特征存储 | 架构复杂 | Feast |



### 4.2 谨慎自研



| 模块 | 考虑因素 | 建议 |

|------|----------|------|

| 模型架构 | 开源模型是否满足需求 | 优先开源 |

| 训练优化 | 是否有特殊优化需求 | 优先开源 |

| 安全隐私 | 是否有特殊安全要求 | 开源+定制 |



### 4.3 必须自研



| 模块 | 原因 | 优先级 |

|------|------|--------|

| 核心交易策略 | 竞争优势 | P0 |

| 因子挖掘逻辑 | Alpha来源 | P0 |

| 风险模型定制 | 机构特定 | P0 |

| 执行算法 | 交易成本 | P1 |



---



## 5. 总结



### 5.1 核心建议



1. **基础设施100%开源** - MLflow、DVC、Triton等

2. **模型架构70%开源** - 基础模型开源，量化定制自研

3. **训练优化90%开源** - DeepSpeed、Optuna等

4. **部署推理100%开源** - Triton、vLLM等

5. **量化核心30%开源** - Qlib辅助，策略自研



### 5.2 预期收益



| 指标 | 预期提升 |

|------|----------|

| 开发效率 | +50% |

| 系统稳定性 | +30% |

| 维护成本 | -40% |

| 技术债务 | -50% |

| 上线速度 | +60% |



---



**文档维护**: 首席蓝图架构师

**更新频率**: 季度更新

**下次更新**: 2026-07-05

