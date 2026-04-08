---
module_id: SENTIMENT_LAYER_SUPPLEMENTARY_MODULES_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席架构师
responsibility:
  - 舆情分析层补充模块综合蓝图
  - P1级和P2级模块设计
  - 开源项目集成方案
standard_type: 专业量化机构蓝图
applicable_scope: 舆情分析层（Layer 3）
compliance_level: 专业标准
---

# 舆情分析层补充模块综合蓝图 (Sentiment Layer Supplementary Modules Blueprint)

> **核心职责**: 补充模块设计和架构规划
> **职责边界**: 
> - ✅ 本文档负责：P1级和P2级补充模块设计和架构规划
> - ❌ 本文档不负责：P0级核心模块（已单独设计）

> **模块ID**: SLSM_001
> **版本**: v1.0.0
> **创建日期**: 2026-04-07
> **Layer定位**: Layer 3 - 舆情分析层
> **包含模块**: P1级5个 + P2级4个

---

## 📋 执行摘要

### 模块清单

| 优先级 | 模块名称 | 开源方案 | 工作量 |
|--------|---------|---------|--------|
| **P1** | 舆情因子归因分析 | SHAP + Alphalens | 60h |
| **P1** | 舆情事件时间线分析 | Timeline.js + D3.js | 50h |
| **P1** | 舆情数据血缘追踪 | OpenLineage | 40h |
| **P1** | 舆情数据质量监控 | Great Expectations | 40h |
| **P1** | 舆情模型性能监控 | Evidently AI | 40h |
| **P2** | 舆情特征工程平台 | Feast | 60h |
| **P2** | 舆情模型压缩与加速 | ONNX Runtime | 50h |
| **P2** | 舆情数据缓存系统 | Redis | 30h |
| **P2** | 舆情API网关 | Kong | 40h |
| **总计** | **9个模块** | **9个开源项目** | **410h** |

---

## 一、P1级模块设计（重要模块）

### 1.1 舆情因子归因分析模块

**模块ID**: SFA_001
**优先级**: P1（重要）
**预计工作量**: 60小时

#### 核心功能

1. **因子贡献度分析**: 分析每个舆情因子对收益的贡献度
2. **特征重要性排序**: 使用SHAP值排序特征重要性
3. **因子有效性评估**: 使用Alphalens评估因子预测能力
4. **可视化报告**: 生成交互式归因报告

#### 技术架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    舆情因子归因分析模块架构                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         SHAP (模型解释)                                       │   │
│  │  - 特征重要性分析                                             │   │
│  │  - 因子贡献度计算                                             │   │
│  │  - 可视化报告生成                                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         Alphalens (因子分析)                                  │   │
│  │  - 因子收益预测能力分析                                       │   │
│  │  - 因子换手分析                                               │   │
│  │  - 因子衰减分析                                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         报告生成 (Report Generation)                          │   │
│  │  - 归因报告                                                   │   │
│  │  - 因子有效性报告                                             │   │
│  │  - 可视化图表                                                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### 核心代码

```python
import shap
import alphalens
from alphalens.tears import create_full_tear_sheet

class SentimentFactorAttribution:
    """舆情因子归因分析"""
    
    def __init__(self, model, factor_data: pd.DataFrame):
        self.model = model
        self.factor_data = factor_data
        self.explainer = shap.TreeExplainer(model)
        
    def calculate_feature_importance(self) -> pd.DataFrame:
        """计算特征重要性"""
        shap_values = self.explainer.shap_values(self.factor_data)
        feature_importance = pd.DataFrame({
            'feature': self.factor_data.columns,
            'importance': np.abs(shap_values).mean(axis=0)
        }).sort_values('importance', ascending=False)
        
        return feature_importance
        
    def generate_factor_tear_sheet(self, factor_data: pd.DataFrame, price_data: pd.DataFrame):
        """生成因子分析报告"""
        factor_data = alphalens.utils.get_clean_factor_and_forward_returns(
            factor_data,
            price_data,
            quantiles=5,
            periods=(1, 5, 10)
        )
        
        create_full_tear_sheet(factor_data)
```

#### 部署方案

```yaml
version: '3.8'

services:
  attribution-engine:
    build: .
    container_name: attribution-engine
    ports:
      - "8001:8000"
    volumes:
      - ./data:/app/data
      - ./reports:/app/reports
```

---

### 1.2 舆情事件时间线分析模块

**模块ID**: SET_001
**优先级**: P1（重要）
**预计工作量**: 50小时

#### 核心功能

1. **事件时间线构建**: 构建舆情事件演化时间线
2. **事件关联分析**: 分析事件之间的关联关系
3. **事件影响评估**: 评估事件对市场的影响
4. **可视化展示**: 生成交互式时间线图表

#### 技术架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    舆情事件时间线分析模块架构                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         Timeline.js (时间线可视化)                            │   │
│  │  - 事件时间线展示                                             │   │
│  │  - 多媒体内容支持                                             │   │
│  │  - 交互式探索                                                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         D3.js (自定义可视化)                                  │   │
│  │  - 事件关联网络图                                             │   │
│  │  - 影响传导图                                                 │   │
│  │  - 热力图                                                     │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         事件分析引擎 (Event Analysis Engine)                  │   │
│  │  - 事件检测                                                   │   │
│  │  - 事件关联                                                   │   │
│  │  - 影响评估                                                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### 核心代码

```python
from datetime import datetime
from typing import List, Dict

class EventTimelineAnalyzer:
    """事件时间线分析器"""
    
    def __init__(self):
        self.events = []
        
    def add_event(self, event: Dict):
        """添加事件"""
        self.events.append({
            'start_date': event['date'],
            'text': event['title'],
            'description': event['description'],
            'media': event.get('media', None)
        })
        
    def generate_timeline_json(self) -> Dict:
        """生成Timeline.js JSON格式"""
        return {
            'title': {
                'text': {'headline': '舆情事件时间线', 'text': '舆情事件演化过程'}
            },
            'events': self.events
        }
        
    def export_timeline_html(self, output_path: str):
        """导出HTML时间线"""
        timeline_json = self.generate_timeline_json()
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <link title="timeline-styles" rel="stylesheet" 
                  href="https://cdn.knightlab.com/libs/timeline3/latest/css/timeline.css">
            <script src="https://cdn.knightlab.com/libs/timeline3/latest/js/timeline.js"></script>
        </head>
        <body>
            <div id='timeline-embed' style="width: 100%; height: 600px"></div>
            <script>
                var timeline_json = {timeline_json};
                window.timeline = new TL.Timeline('timeline-embed', timeline_json);
            </script>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_template)
```

---

### 1.3 舆情数据血缘追踪模块

**模块ID**: SDL_001
**优先级**: P1（重要）
**预计工作量**: 40小时

#### 核心功能

1. **数据血缘追踪**: 追踪数据从源头到目标的完整路径
2. **数据影响分析**: 分析数据变更对下游的影响
3. **数据质量关联**: 关联数据质量与血缘关系
4. **可视化展示**: 生成数据血缘图谱

#### 技术架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    舆情数据血缘追踪模块架构                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         OpenLineage (血缘追踪标准)                            │   │
│  │  - 血缘数据采集                                               │   │
│  │  - 血缘数据存储                                               │   │
│  │  - 血缘数据查询                                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         Marquez (血缘可视化)                                  │   │
│  │  - 血缘图谱展示                                               │   │
│  │  - 影响分析                                                   │   │
│  │  - 数据探索                                                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         血缘分析引擎 (Lineage Analysis Engine)                │   │
│  │  - 影响分析                                                   │   │
│  │  - 血缘查询                                                   │   │
│  │  - 血缘报告                                                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### 核心代码

```python
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run
from openlineage.client.facet import SourceCodeJobFacet

class DataLineageTracker:
    """数据血缘追踪器"""
    
    def __init__(self, lineage_url: str):
        self.client = OpenLineageClient(url=lineage_url)
        
    def track_data_flow(
        self,
        job_name: str,
        inputs: List[Dict],
        outputs: List[Dict]
    ):
        """追踪数据流"""
        run_event = RunEvent(
            eventType=RunState.COMPLETE,
            eventTime='2026-04-07T00:00:00Z',
            run=Run(runId='run-123'),
            job={
                'namespace': 'sentiment-analysis',
                'name': job_name,
                'facets': {
                    'sourceCode': SourceCodeJobFacet(
                        language='python',
                        sourceCode='...'
                    )
                }
            },
            inputs=inputs,
            outputs=outputs
        )
        
        self.client.emit(run_event)
        
    def get_lineage_graph(self, dataset_name: str) -> Dict:
        """获取血缘图谱"""
        # 实现血缘图谱查询
        pass
```

---

### 1.4 舆情数据质量监控模块

**模块ID**: SDQ_001
**优先级**: P1（重要）
**预计工作量**: 40小时

#### 核心功能

1. **数据质量检查**: 自动检查数据质量
2. **数据质量报告**: 生成数据质量报告
3. **数据质量告警**: 数据质量异常告警
4. **数据质量趋势**: 数据质量趋势分析

#### 核心代码

```python
import great_expectations as gx

class DataQualityMonitor:
    """数据质量监控器"""
    
    def __init__(self, project_root: str):
        self.context = gx.get_context(project_root=project_root)
        
    def create_expectation_suite(self, suite_name: str):
        """创建期望套件"""
        suite = self.context.add_expectation_suite(
            expectation_suite_name=suite_name
        )
        
        # 添加期望
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToNotBeNull(column='sentiment_score')
        )
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeBetween(
                column='sentiment_score',
                min_value=-1,
                max_value=1
            )
        )
        
        return suite
        
    def run_validation(self, batch_request: Dict) -> Dict:
        """运行验证"""
        results = self.context.run_validation_operator(
            'action_list_operator',
            assets_to_validate=[batch_request]
        )
        
        return results
```

---

### 1.5 舆情模型性能监控模块

**模块ID**: SMP_001
**优先级**: P1（重要）
**预计工作量**: 40小时

#### 核心功能

1. **模型性能监控**: 监控模型性能指标
2. **数据漂移检测**: 检测数据分布变化
3. **模型漂移检测**: 检测模型性能下降
4. **性能报告生成**: 生成模型性能报告

#### 核心代码

```python
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, ClassificationPreset

class ModelPerformanceMonitor:
    """模型性能监控器"""
    
    def __init__(self):
        self.column_mapping = ColumnMapping(
            target='actual',
            prediction='predicted',
            numerical_features=['sentiment_score', 'discussion_heat']
        )
        
    def generate_performance_report(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame
    ) -> Dict:
        """生成性能报告"""
        report = Report(metrics=[
            ClassificationPreset(),
            DataDriftPreset()
        ])
        
        report.run(
            reference_data=reference_data,
            current_data=current_data,
            column_mapping=self.column_mapping
        )
        
        return report.as_dict()
        
    def detect_drift(self, reference_data: pd.DataFrame, current_data: pd.DataFrame) -> bool:
        """检测漂移"""
        report = self.generate_performance_report(reference_data, current_data)
        
        # 检查数据漂移
        data_drift = report['metrics'][1]['result']['dataset_drift']
        
        return data_drift
```

---

## 二、P2级模块设计（优化模块）

### 2.1 舆情特征工程平台

**模块ID**: SFE_001
**优先级**: P2（优化）
**预计工作量**: 60小时

#### 核心功能

1. **特征定义**: 定义舆情特征
2. **特征存储**: 存储特征数据
3. **特征服务**: 提供特征查询服务
4. **特征版本管理**: 管理特征版本

#### 核心代码

```python
from feast import Entity, Feature, FeatureView, FileSource, ValueType

# 定义实体
sentiment_entity = Entity(
    name='sentiment_id',
    value_type=ValueType.STRING,
    description='Sentiment data entity'
)

# 定义特征视图
sentiment_features = FeatureView(
    name='sentiment_features',
    entities=['sentiment_id'],
    ttl=timedelta(days=1),
    features=[
        Feature(name='sentiment_score', dtype=ValueType.FLOAT),
        Feature(name='discussion_heat', dtype=ValueType.FLOAT),
        Feature(name='event_count', dtype=ValueType.INT64)
    ],
    input=FileSource(
        path='data/sentiment_features.parquet',
        event_timestamp_column='timestamp'
    )
)
```

---

### 2.2 舆情模型压缩与加速

**模块ID**: SMC_001
**优先级**: P2（优化）
**预计工作量**: 50小时

#### 核心功能

1. **模型导出**: 将PyTorch模型导出为ONNX格式
2. **模型优化**: 使用ONNX Runtime优化模型
3. **模型量化**: 模型量化加速
4. **性能测试**: 测试模型性能提升

#### 核心代码

```python
import torch
import onnxruntime as ort

class ModelCompressor:
    """模型压缩器"""
    
    def export_to_onnx(self, model: torch.nn.Module, output_path: str):
        """导出为ONNX格式"""
        dummy_input = torch.randn(1, 512)
        
        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            opset_version=11,
            input_names=['input'],
            output_names=['output']
        )
        
    def optimize_model(self, onnx_path: str) -> ort.InferenceSession:
        """优化模型"""
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        session = ort.InferenceSession(onnx_path, sess_options)
        
        return session
```

---

### 2.3 舆情数据缓存系统

**模块ID**: SDC_001
**优先级**: P2（优化）
**预计工作量**: 30小时

#### 核心功能

1. **数据缓存**: 缓存热点数据
2. **缓存更新**: 自动更新缓存
3. **缓存失效**: 缓存失效策略
4. **缓存监控**: 监控缓存性能

#### 核心代码

```python
import redis
import json

class DataCache:
    """数据缓存"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        
    def get(self, key: str) -> Any:
        """获取缓存"""
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return None
        
    def set(self, key: str, value: Any, ttl: int = 3600):
        """设置缓存"""
        self.client.setex(key, ttl, json.dumps(value))
        
    def delete(self, key: str):
        """删除缓存"""
        self.client.delete(key)
```

---

### 2.4 舆情API网关

**模块ID**: SAG_001
**优先级**: P2（优化）
**预计工作量**: 40小时

#### 核心功能

1. **API路由**: 统一API路由管理
2. **负载均衡**: 负载均衡分发
3. **限流控制**: API限流控制
4. **监控日志**: API监控和日志

#### 核心代码

```yaml
# Kong配置
_format_version: "3.0"

services:
  - name: sentiment-analysis-service
    url: http://sentiment-api:8000
    routes:
      - name: sentiment-route
        paths:
          - /api/v1/sentiment
    plugins:
      - name: rate-limiting
        config:
          minute: 100
          policy: local
      - name: jwt
        config:
          secret_is_base64: false
```

---

## 三、部署架构

### 3.1 完整部署方案

```yaml
version: '3.8'

services:
  # P1级模块
  attribution-engine:
    build: ./attribution
    container_name: attribution-engine
    ports:
      - "8001:8000"
      
  timeline-analyzer:
    build: ./timeline
    container_name: timeline-analyzer
    ports:
      - "8002:8000"
      
  lineage-tracker:
    build: ./lineage
    container_name: lineage-tracker
    ports:
      - "8003:8000"
      
  quality-monitor:
    build: ./quality
    container_name: quality-monitor
    ports:
      - "8004:8000"
      
  performance-monitor:
    build: ./performance
    container_name: performance-monitor
    ports:
      - "8005:8000"
      
  # P2级模块
  feature-store:
    build: ./feature-store
    container_name: feature-store
    ports:
      - "8006:8000"
      
  model-optimizer:
    build: ./optimizer
    container_name: model-optimizer
    ports:
      - "8007:8000"
      
  redis-cache:
    image: redis:latest
    container_name: redis-cache
    ports:
      - "6379:6379"
      
  kong-gateway:
    image: kong:latest
    container_name: kong-gateway
    ports:
      - "8000:8000"
      - "8443:8443"
```

---

## 四、成本估算

### 4.1 开发成本

| 优先级 | 模块数量 | 总工作量 | 说明 |
|--------|---------|---------|------|
| **P1** | 5个 | 230小时 | 重要模块 |
| **P2** | 4个 | 180小时 | 优化模块 |
| **总计** | **9个** | **410小时** | 约2-3个月 |

### 4.2 运维成本

| 项目 | 月度成本 | 说明 |
|------|---------|------|
| **服务器** | 500元 | 4核8G云服务器 |
| **存储** | 100元 | 500GB SSD |
| **带宽** | 100元 | 10Mbps带宽 |
| **总计** | **700元/月** | - |

---

## 五、实施路线图

### 5.1 第一阶段（1-2个月）：P1级模块

- Week 1-2: 归因分析模块
- Week 3-4: 事件时间线模块
- Week 5-6: 数据血缘模块
- Week 7-8: 数据质量监控模块
- Week 9-10: 模型性能监控模块

### 5.2 第二阶段（1个月）：P2级模块

- Week 11-12: 特征工程平台
- Week 13-14: 模型压缩加速
- Week 15-16: 数据缓存系统
- Week 17-18: API网关

---

## 六、总结与建议

### 6.1 核心优势

1. **开源免费**: 所有模块都使用成熟开源项目
2. **功能全面**: 覆盖归因、监控、优化等各个方面
3. **易于部署**: Docker一键部署
4. **社区支持**: 所有开源项目社区活跃

### 6.2 实施建议

1. **优先级**: 先实施P1级模块，再实施P2级模块
2. **迭代开发**: 每个模块独立开发，逐步集成
3. **持续优化**: 根据使用情况持续优化

---

**蓝图创建时间**: 2026-04-07
**架构师**: 首席架构师
**下次更新建议**: 实施后1个月
**最终状态**: ✅ 完整蓝图已生成
