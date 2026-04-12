---

module_id: DATA_SOURCE_QUALITY_MONITORING_001

version: 1.0.0

status: Active

created_date: 2026-04-06

last_updated: '2026-04-07'

owner: 首席架构师

layer: layer_00

standard_type: 专业量化机构级数据源质量监控蓝图

applicable_scope: Layer 0数据源质量监控

compliance_level: 顶级专业标准

reference_models:

- Two Sigma Data Quality

- Citadel Data Validation

- Bridgewater Data Governance

related_documents:

- DATA_LAYER_IMPLEMENTATION_BLUEPRINT.md

- DATA_QUALITY_MONITORING_BLUEPRINT.md

- DATA_QUALITY_ASSESSMENT_BLUEPRINT.md

- DATA_QUALITY_MANAGEMENT_BLUEPRINT.md

- DATA_QUALITY_GOVERNANCE_BLUEPRINT.md

parent_document: ../ARCHITECTURE.md

implementation_status: 设计阶段

responsibility_boundary: '**本文档职责（Layer 0 数据源层）**：





  **与本文档职责边界**：



  - Layer 1（数据层）: DATA_QUALITY_ASSESSMENT_BLUEPRINT.md - 负责多维度质量评估



  - Layer 4（机器学习层）: DATA_QUALITY_MONITORING_BLUEPRINT.md - 负责实时质量监控



  - Layer 10（治理层）: DATA_QUALITY_MANAGEMENT_BLUEPRINT.md - 负责规则定义和改进跟踪



  - Layer 10（治理层）: DATA_QUALITY_GOVERNANCE_BLUEPRINT.md - 负责顶层治理协调



  '

responsibility:

- 数据管理架构设计与实施规范与优化维护

---

# 数据源质量监控蓝图

> **核心职责**: Data Source Quality Monitoring蓝图设计

> **职责边界**: 

> - ✅ 本文档负责：Data Source Quality Monitoring蓝图设计相关内容

> - ❌ 本文档不负责：其他模块内容





> **版本**: v1.0  

> **创建日期**: 2026-04-06  

> **实施周期**: 1周  

> **目标**: 构建专业级数据源质量监控体系，对标Two Sigma、Citadel数据质量标准



## 接口与契约（蓝图终稿）



- 全库 API 与事件约定真源：`API_Contract.md`。质量指标上报、阈值与告警、与 Layer 1/4/10 质量模块的协同查询若通过接口/事件实现，须在该真源或本文后续接口说明中闭合。



## 验收标准（可检查）



- 能在本文中明确至少一条“采集/样本检查 → 指标计算 → 告警或工单 → 审计记录”的可检查闭环，并能映射到 `API_Contract.md` 的对应契约入口（或写明豁免与补全计划）。



## 已知限制



- 与 `DATA_QUALITY_*` 系列蓝图的职责切分以本文「职责边界」为准；指标口径与 SLA 在施工文档阶段锁定。



---



## 📋 执行摘要



### 核心定位



数据源质量监控是Layer 0数据源层的**质量保障系统**，负责：

- 数据源健康状态监控

- 数据质量实时验证

- 数据完整性检查

- 异常数据告警



### 个人使用价值



| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评分 |

|---------|-------------|-------------|---------|

| **质量保障** | 专业数据质量团队 | Great Expectations自动化 | ⭐⭐⭐⭐⭐ |

| **异常检测** | 实时监控系统 | Prometheus + Grafana | ⭐⭐⭐⭐⭐ |

| **成本控制** | 数据质量预算 | 自动化质量检查 | ⭐⭐⭐⭐ |

| **风险预防** | 数据质量风险控制 | 提前发现数据问题 | ⭐⭐⭐⭐⭐ |



**综合价值评分**: ⭐⭐⭐⭐⭐ (5/5) - **强烈推荐实施**



---



## 一、架构设计



### 1.1 整体架构



```

┌─────────────────────────────────────────────────────────────────┐

│                  数据源质量监控系统架构                           │

├─────────────────────────────────────────────────────────────────┤

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │              1. 数据源健康监控层                           │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ 数据源状态监控                                       │ │ │

│  │  │  ├── TuShare连接状态                               │ │ │

│  │  │  ├── AKShare连接状态                               │ │ │

│  │  │  ├── 东方财富连接状态                               │ │ │

│  │  │  └── 其他数据源状态                                 │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ 数据源性能监控                                       │ │ │

│  │  │  ├── 响应时间监控                                   │ │ │

│  │  │  ├── 吞吐量监控                                     │ │ │

│  │  │  ├── 错误率监控                                     │ │ │

│  │  │  └── 可用性监控                                     │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │              2. 数据质量验证层                             │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ 数据完整性验证                                       │ │ │

│  │  │  ├── 字段完整性检查                                 │ │ │

│  │  │  ├── 记录完整性检查                                 │ │ │

│  │  │  ├── 时间序列完整性检查                             │ │ │

│  │  │  └── 数据范围完整性检查                             │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ 数据准确性验证                                       │ │ │

│  │  │  ├── 价格范围验证                                   │ │ │

│  │  │  ├── 成交量验证                                     │ │ │

│  │  │  ├── 财务数据验证                                   │ │ │

│  │  │  └── 业务规则验证                                   │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │              3. 异常检测与告警层                           │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ 异常检测                                             │ │ │

│  │  │  ├── 数据缺失检测                                   │ │ │

│  │  │  ├── 数据异常检测                                   │ │ │

│  │  │  ├── 数据延迟检测                                   │ │ │

│  │  │  └── 数据冲突检测                                   │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ 告警系统                                             │ │ │

│  │  │  ├── 邮件告警                                       │ │ │

│  │  │  ├── 钉钉告警                                       │ │ │

│  │  │  ├── 企业微信告警                                   │ │ │

│  │  │  └── 日志记录                                       │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  └───────────────────────────────────────────────────────────┘ │

│                                                                 │

│  ┌───────────────────────────────────────────────────────────┐ │

│  │              4. 质量报告与可视化层                         │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ 质量报告                                             │ │ │

│  │  │  ├── 每日质量报告                                   │ │ │

│  │  │  ├── 每周质量报告                                   │ │ │

│  │  │  ├── 每月质量报告                                   │ │ │

│  │  │  └── 自定义质量报告                                 │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  │  ┌─────────────────────────────────────────────────────┐ │ │

│  │  │ 可视化仪表板                                         │ │ │

│  │  │  ├── Grafana仪表板                                  │ │ │

│  │  │  ├── 质量趋势图                                     │ │ │

│  │  │  ├── 异常统计图                                     │ │ │

│  │  │  └── 数据源健康度                                   │ │ │

│  │  └─────────────────────────────────────────────────────┘ │ │

│  └───────────────────────────────────────────────────────────┘ │

└─────────────────────────────────────────────────────────────────┘

```



### 1.2 模块职责边界



| 模块 | 核心职责 | 输入 | 输出 | 对接模块 |

|------|---------|------|------|---------|

| **数据源健康监控层** | 监控数据源状态和性能 | 数据源连接信息 | 健康状态报告 | 数据质量验证层 |

| **数据质量验证层** | 验证数据完整性和准确性 | 原始数据 | 质量验证结果 | 异常检测与告警层 |

| **异常检测与告警层** | 检测异常并发送告警 | 质量验证结果 | 告警信息 | 质量报告与可视化层 |

| **质量报告与可视化层** | 生成报告和可视化 | 告警信息 | 质量报告 | Layer 1 |



---



## 二、开源方案集成



### 2.1 Great Expectations集成



**项目信息**:

- **GitHub**: https://github.com/great-expectations/great_expectations

- **Stars**: 9k+

- **许可证**: Apache 2.0

- **成熟度**: ⭐⭐⭐⭐⭐



**核心功能**:

- 数据质量验证

- 自动化测试

- 数据文档生成

- 集成多种数据源



### 2.2 技术栈选择



| 组件 | 开源方案 | 版本 | 用途 |

|------|---------|------|------|

| **数据质量验证** | Great Expectations | 0.18+ | 数据质量验证 |

| **监控** | Prometheus | 2.45+ | 指标收集 |

| **可视化** | Grafana | 10.0+ | 可视化仪表板 |

| **告警** | AlertManager | 0.26+ | 告警管理 |

| **数据库** | PostgreSQL | 15+ | 数据存储 |

| **缓存** | Redis | 7.0+ | 缓存 |



---



## 三、核心代码实现



### 3.1 数据源质量监控器



```python

import great_expectations as gx

from typing import Dict, List, Optional

import pandas as pd

from datetime import datetime

import logging



class DataSourceQualityMonitor:

    """数据源质量监控器"""

    

    def __init__(self, config: Dict):

        self.config = config

        self.context = gx.get_context()

        self.expectation_suites = {}

        self.validators = {}

        self.logger = logging.getLogger(__name__)

        

        self._initialize_expectation_suites()

    

    def _initialize_expectation_suites(self):

        """初始化期望套件"""

        # 股票数据期望套件

        stock_suite = gx.ExpectationSuite(name="stock_data_quality")

        

        # 价格范围期望

        stock_suite.add_expectation(

            gx.expectations.ExpectColumnValuesToBeBetween(

                column="open",

                min_value=0,

                max_value=100000

            )

        )

        stock_suite.add_expectation(

            gx.expectations.ExpectColumnValuesToBeBetween(

                column="close",

                min_value=0,

                max_value=100000

            )

        )

        stock_suite.add_expectation(

            gx.expectations.ExpectColumnValuesToBeBetween(

                column="high",

                min_value=0,

                max_value=100000

            )

        )

        stock_suite.add_expectation(

            gx.expectations.ExpectColumnValuesToBeBetween(

                column="low",

                min_value=0,

                max_value=100000

            )

        )

        

        # 成交量期望

        stock_suite.add_expectation(

            gx.expectations.ExpectColumnValuesToBeBetween(

                column="volume",

                min_value=0,

                max_value=10000000000

            )

        )

        

        # 完整性期望

        stock_suite.add_expectation(

            gx.expectations.ExpectColumnValuesToNotBeNull(

                column="close"

            )

        )

        stock_suite.add_expectation(

            gx.expectations.ExpectColumnValuesToNotBeNull(

                column="volume"

            )

        )

        

        # 唯一性期望

        stock_suite.add_expectation(

            gx.expectations.ExpectColumnValuesToBeUnique(

                column="date"

            )

        )

        

        self.expectation_suites["stock"] = stock_suite

        self.context.add_expectation_suite(expectation_suite=stock_suite)

    

    def validate_data_source(self, df: pd.DataFrame, source_name: str) -> Dict:

        """验证数据源质量"""

        try:

            # 创建验证器

            validator = self.context.get_validator(

                batch_request=gx.RuntimeBatchRequest(

                    datasource_name="pandas_datasource",

                    data_connector_name="runtime_connector",

                    data_asset_name=source_name,

                    batch_identifiers={"default": "default"},

                    runtime_parameters={"batch_data": df}

                ),

                expectation_suite_name="stock_data_quality"

            )

            

            # 执行验证

            results = validator.validate()

            

            # 生成质量报告

            quality_report = {

                "source_name": source_name,

                "timestamp": datetime.now().isoformat(),

                "success": results.success,

                "statistics": {

                    "evaluated_expectations": results.statistics["evaluated_expectations"],

                    "successful_expectations": results.statistics["successful_expectations"],

                    "unsuccessful_expectations": results.statistics["unsuccessful_expectations"],

                    "success_percent": results.statistics["success_percent"]

                },

                "details": []

            }

            

            # 添加详细结果

            for result in results.results:

                quality_report["details"].append({

                    "expectation_type": result.expectation_config.expectation_type,

                    "column": result.expectation_config.kwargs.get("column"),

                    "success": result.success,

                    "result": result.result

                })

            

            return quality_report

            

        except Exception as e:

            self.logger.error(f"数据源质量验证失败: {e}")

            return {

                "source_name": source_name,

                "timestamp": datetime.now().isoformat(),

                "success": False,

                "error": str(e)

            }

    

    def check_data_completeness(self, df: pd.DataFrame, date_column: str = "date") -> Dict:

        """检查数据完整性"""

        try:

            # 检查日期连续性

            df_sorted = df.sort_values(date_column)

            dates = pd.to_datetime(df_sorted[date_column])

            

            # 计算缺失日期

            date_range = pd.date_range(start=dates.min(), end=dates.max(), freq='D')

            missing_dates = date_range.difference(dates)

            

            completeness_report = {

                "total_records": len(df),

                "date_range": {

                    "start": dates.min().isoformat(),

                    "end": dates.max().isoformat()

                },

                "expected_records": len(date_range),

                "missing_records": len(missing_dates),

                "completeness_rate": 1 - (len(missing_dates) / len(date_range)),

                "missing_dates": [d.isoformat() for d in missing_dates[:10]]  # 只显示前10个

            }

            

            return completeness_report

            

        except Exception as e:

            self.logger.error(f"数据完整性检查失败: {e}")

            return {"error": str(e)}

    

    def check_data_accuracy(self, df: pd.DataFrame) -> Dict:

        """检查数据准确性"""

        try:

            accuracy_issues = []

            

            # 检查价格逻辑

            if (df['high'] < df['low']).any():

                accuracy_issues.append("存在最高价低于最低价的记录")

            

            if (df['close'] > df['high']).any():

                accuracy_issues.append("存在收盘价高于最高价的记录")

            

            if (df['close'] < df['low']).any():

                accuracy_issues.append("存在收盘价低于最低价的记录")

            

            # 检查成交量

            if (df['volume'] < 0).any():

                accuracy_issues.append("存在负成交量的记录")

            

            # 检查价格跳跃

            price_change = df['close'].pct_change()

            abnormal_changes = price_change[abs(price_change) > 0.3]  # 单日涨跌幅超过30%

            if len(abnormal_changes) > 0:

                accuracy_issues.append(f"存在{len(abnormal_changes)}个异常价格变动记录")

            

            accuracy_report = {

                "total_records": len(df),

                "accuracy_issues": accuracy_issues,

                "accuracy_rate": 1 - (len(accuracy_issues) / 4) if accuracy_issues else 1.0,

                "is_accurate": len(accuracy_issues) == 0

            }

            

            return accuracy_report

            

        except Exception as e:

            self.logger.error(f"数据准确性检查失败: {e}")

            return {"error": str(e)}

    

    def generate_quality_score(self, validation_result: Dict, 

                               completeness_result: Dict, 

                               accuracy_result: Dict) -> Dict:

        """生成质量评分"""

        try:

            # 计算各维度得分

            validation_score = validation_result["statistics"]["success_percent"] / 100

            completeness_score = completeness_result.get("completeness_rate", 0)

            accuracy_score = accuracy_result.get("accuracy_rate", 0)

            

            # 综合质量评分 (加权平均)

            overall_score = (

                validation_score * 0.4 +

                completeness_score * 0.3 +

                accuracy_score * 0.3

            )

            

            quality_score = {

                "overall_score": overall_score,

                "validation_score": validation_score,

                "completeness_score": completeness_score,

                "accuracy_score": accuracy_score,

                "grade": self._get_quality_grade(overall_score),

                "timestamp": datetime.now().isoformat()

            }

            

            return quality_score

            

        except Exception as e:

            self.logger.error(f"质量评分生成失败: {e}")

            return {"error": str(e)}

    

    def _get_quality_grade(self, score: float) -> str:

        """获取质量等级"""

        if score >= 0.95:

            return "A+"

        elif score >= 0.90:

            return "A"

        elif score >= 0.85:

            return "B+"

        elif score >= 0.80:

            return "B"

        elif score >= 0.70:

            return "C"

        else:

            return "D"

```



### 3.2 数据源健康监控



```python

import time

import requests

from typing import Dict, List

from datetime import datetime, timedelta

import pandas as pd

import logging



class DataSourceHealthMonitor:

    """数据源健康监控"""

    

    def __init__(self, config: Dict):

        self.config = config

        self.data_sources = config.get("data_sources", {})

        self.health_status = {}

        self.performance_metrics = {}

        self.logger = logging.getLogger(__name__)

    

    def check_data_source_health(self, source_name: str) -> Dict:

        """检查数据源健康状态"""

        try:

            source_config = self.data_sources.get(source_name, {})

            

            health_check = {

                "source_name": source_name,

                "timestamp": datetime.now().isoformat(),

                "status": "unknown",

                "response_time": None,

                "error": None

            }

            

            # 测试连接

            start_time = time.time()

            

            if source_name == "tushare":

                status = self._check_tushare_health(source_config)

            elif source_name == "akshare":

                status = self._check_akshare_health(source_config)

            else:

                status = self._check_generic_health(source_config)

            

            end_time = time.time()

            response_time = end_time - start_time

            

            health_check["status"] = status

            health_check["response_time"] = response_time

            

            # 更新健康状态

            self.health_status[source_name] = health_check

            

            return health_check

            

        except Exception as e:

            self.logger.error(f"数据源健康检查失败: {e}")

            return {

                "source_name": source_name,

                "timestamp": datetime.now().isoformat(),

                "status": "error",

                "error": str(e)

            }

    

    def _check_tushare_health(self, config: Dict) -> str:

        """检查TuShare健康状态"""

        try:

            import tushare as ts

            pro = ts.pro_api(config.get("token"))

            

            # 测试获取数据

            df = pro.daily(ts_code="000001.SZ", start_date="20240101", end_date="20240110")

            

            if df is not None and len(df) > 0:

                return "healthy"

            else:

                return "degraded"

                

        except Exception as e:

            self.logger.error(f"TuShare健康检查失败: {e}")

            return "error"

    

    def _check_akshare_health(self, config: Dict) -> str:

        """检查AKShare健康状态"""

        try:

            import akshare as ak

            

            # 测试获取数据

            df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20240101", end_date="20240110")

            

            if df is not None and len(df) > 0:

                return "healthy"

            else:

                return "degraded"

                

        except Exception as e:

            self.logger.error(f"AKShare健康检查失败: {e}")

            return "error"

    

    def _check_generic_health(self, config: Dict) -> str:

        """检查通用数据源健康状态"""

        try:

            url = config.get("url")

            if not url:

                return "unknown"

            

            response = requests.get(url, timeout=5)

            

            if response.status_code == 200:

                return "healthy"

            else:

                return "degraded"

                

        except Exception as e:

            self.logger.error(f"通用数据源健康检查失败: {e}")

            return "error"

    

    def monitor_performance(self, source_name: str, duration: int = 60) -> Dict:

        """监控数据源性能"""

        try:

            metrics = {

                "source_name": source_name,

                "start_time": datetime.now().isoformat(),

                "duration": duration,

                "samples": []

            }

            

            for i in range(duration):

                health = self.check_data_source_health(source_name)

                

                metrics["samples"].append({

                    "timestamp": health["timestamp"],

                    "response_time": health["response_time"],

                    "status": health["status"]

                })

                

                time.sleep(1)

            

            # 计算性能指标

            response_times = [s["response_time"] for s in metrics["samples"] if s["response_time"]]

            

            if response_times:

                metrics["performance"] = {

                    "avg_response_time": sum(response_times) / len(response_times),

                    "max_response_time": max(response_times),

                    "min_response_time": min(response_times),

                    "availability": len([s for s in metrics["samples"] if s["status"] == "healthy"]) / len(metrics["samples"])

                }

            

            # 更新性能指标

            self.performance_metrics[source_name] = metrics

            

            return metrics

            

        except Exception as e:

            self.logger.error(f"性能监控失败: {e}")

            return {"error": str(e)}

    

    def get_health_summary(self) -> Dict:

        """获取健康状态摘要"""

        try:

            summary = {

                "timestamp": datetime.now().isoformat(),

                "data_sources": {},

                "overall_health": "unknown"

            }

            

            healthy_count = 0

            total_count = len(self.health_status)

            

            for source_name, health in self.health_status.items():

                summary["data_sources"][source_name] = {

                    "status": health["status"],

                    "response_time": health.get("response_time"),

                    "last_check": health["timestamp"]

                }

                

                if health["status"] == "healthy":

                    healthy_count += 1

            

            if total_count > 0:

                if healthy_count == total_count:

                    summary["overall_health"] = "healthy"

                elif healthy_count > total_count / 2:

                    summary["overall_health"] = "degraded"

                else:

                    summary["overall_health"] = "critical"

            

            return summary

            

        except Exception as e:

            self.logger.error(f"健康状态摘要生成失败: {e}")

            return {"error": str(e)}

```



### 3.3 异常检测与告警



```python

from typing import Dict, List, Optional

from datetime import datetime, timedelta

import pandas as pd

import smtplib

from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart

import logging

import requests



class AnomalyDetector:

    """异常检测器"""

    

    def __init__(self, config: Dict):

        self.config = config

        self.anomaly_rules = config.get("anomaly_rules", {})

        self.logger = logging.getLogger(__name__)

    

    def detect_anomalies(self, df: pd.DataFrame, source_name: str) -> Dict:

        """检测数据异常"""

        try:

            anomalies = []

            

            # 检测缺失数据

            missing_anomalies = self._detect_missing_data(df, source_name)

            anomalies.extend(missing_anomalies)

            

            # 检测异常数据

            abnormal_anomalies = self._detect_abnormal_data(df, source_name)

            anomalies.extend(abnormal_anomalies)

            

            # 检测数据延迟

            delay_anomalies = self._detect_data_delay(df, source_name)

            anomalies.extend(delay_anomalies)

            

            # 检测数据冲突

            conflict_anomalies = self._detect_data_conflict(df, source_name)

            anomalies.extend(conflict_anomalies)

            

            anomaly_report = {

                "source_name": source_name,

                "timestamp": datetime.now().isoformat(),

                "total_anomalies": len(anomalies),

                "anomalies": anomalies,

                "severity": self._calculate_severity(anomalies)

            }

            

            return anomaly_report

            

        except Exception as e:

            self.logger.error(f"异常检测失败: {e}")

            return {"error": str(e)}

    

    def _detect_missing_data(self, df: pd.DataFrame, source_name: str) -> List[Dict]:

        """检测缺失数据"""

        anomalies = []

        

        # 检查列缺失

        for column in df.columns:

            missing_count = df[column].isnull().sum()

            missing_rate = missing_count / len(df)

            

            if missing_rate > 0.05:  # 缺失率超过5%

                anomalies.append({

                    "type": "missing_data",

                    "column": column,

                    "missing_count": missing_count,

                    "missing_rate": missing_rate,

                    "severity": "high" if missing_rate > 0.1 else "medium",

                    "message": f"列 {column} 缺失率为 {missing_rate:.2%}"

                })

        

        return anomalies

    

    def _detect_abnormal_data(self, df: pd.DataFrame, source_name: str) -> List[Dict]:

        """检测异常数据"""

        anomalies = []

        

        # 检查价格异常

        if 'close' in df.columns:

            price_change = df['close'].pct_change()

            abnormal_changes = price_change[abs(price_change) > 0.3]

            

            if len(abnormal_changes) > 0:

                anomalies.append({

                    "type": "abnormal_data",

                    "column": "close",

                    "count": len(abnormal_changes),

                    "severity": "medium",

                    "message": f"发现 {len(abnormal_changes)} 个异常价格变动"

                })

        

        # 检查成交量异常

        if 'volume' in df.columns:

            volume_mean = df['volume'].mean()

            volume_std = df['volume'].std()

            abnormal_volumes = df[df['volume'] > volume_mean + 3 * volume_std]

            

            if len(abnormal_volumes) > 0:

                anomalies.append({

                    "type": "abnormal_data",

                    "column": "volume",

                    "count": len(abnormal_volumes),

                    "severity": "low",

                    "message": f"发现 {len(abnormal_volumes)} 个异常成交量"

                })

        

        return anomalies

    

    def _detect_data_delay(self, df: pd.DataFrame, source_name: str) -> List[Dict]:

        """检测数据延迟"""

        anomalies = []

        

        if 'date' in df.columns:

            latest_date = pd.to_datetime(df['date']).max()

            current_date = datetime.now()

            delay_days = (current_date - latest_date).days

            

            if delay_days > 1:

                anomalies.append({

                    "type": "data_delay",

                    "delay_days": delay_days,

                    "latest_date": latest_date.isoformat(),

                    "severity": "high" if delay_days > 3 else "medium",

                    "message": f"数据延迟 {delay_days} 天"

                })

        

        return anomalies

    

    def _detect_data_conflict(self, df: pd.DataFrame, source_name: str) -> List[Dict]:

        """检测数据冲突"""

        anomalies = []

        

        # 检查价格逻辑冲突

        if all(col in df.columns for col in ['high', 'low', 'close']):

            conflicts = df[

                (df['high'] < df['low']) |

                (df['close'] > df['high']) |

                (df['close'] < df['low'])

            ]

            

            if len(conflicts) > 0:

                anomalies.append({

                    "type": "data_conflict",

                    "count": len(conflicts),

                    "severity": "high",

                    "message": f"发现 {len(conflicts)} 个价格逻辑冲突"

                })

        

        return anomalies

    

    def _calculate_severity(self, anomalies: List[Dict]) -> str:

        """计算严重程度"""

        if not anomalies:

            return "none"

        

        high_count = len([a for a in anomalies if a.get("severity") == "high"])

        medium_count = len([a for a in anomalies if a.get("severity") == "medium"])

        

        if high_count > 0:

            return "critical"

        elif medium_count > 2:

            return "high"

        elif medium_count > 0:

            return "medium"

        else:

            return "low"





class AlertManager:

    """告警管理器"""

    

    def __init__(self, config: Dict):

        self.config = config

        self.alert_channels = config.get("alert_channels", {})

        self.logger = logging.getLogger(__name__)

    

    def send_alert(self, anomaly_report: Dict, channels: List[str] = None):

        """发送告警"""

        if channels is None:

            channels = list(self.alert_channels.keys())

        

        for channel in channels:

            try:

                if channel == "email":

                    self._send_email_alert(anomaly_report)

                elif channel == "dingtalk":

                    self._send_dingtalk_alert(anomaly_report)

                elif channel == "wechat":

                    self._send_wechat_alert(anomaly_report)

                elif channel == "log":

                    self._log_alert(anomaly_report)

                    

            except Exception as e:

                self.logger.error(f"发送告警失败 ({channel}): {e}")

    

    def _send_email_alert(self, anomaly_report: Dict):

        """发送邮件告警"""

        email_config = self.alert_channels.get("email", {})

        

        msg = MIMEMultipart()

        msg['From'] = email_config.get("sender")

        msg['To'] = email_config.get("receiver")

        msg['Subject'] = f"[数据质量告警] {anomaly_report['source_name']} - {anomaly_report['severity']}"

        

        body = f"""

数据源: {anomaly_report['source_name']}

时间: {anomaly_report['timestamp']}

严重程度: {anomaly_report['severity']}

异常数量: {anomaly_report['total_anomalies']}



异常详情:

"""

        

        for anomaly in anomaly_report['anomalies']:

            body += f"\n- {anomaly['message']}"

        

        msg.attach(MIMEText(body, 'plain'))

        

        # 发送邮件

        with smtplib.SMTP(email_config.get("smtp_server"), email_config.get("smtp_port")) as server:

            server.starttls()

            server.login(email_config.get("sender"), email_config.get("password"))

            server.send_message(msg)

    

    def _send_dingtalk_alert(self, anomaly_report: Dict):

        """发送钉钉告警"""

        webhook = self.alert_channels.get("dingtalk", {}).get("webhook")

        

        if not webhook:

            return

        

        message = {

            "msgtype": "text",

            "text": {

                "content": f"[数据质量告警]\n数据源: {anomaly_report['source_name']}\n严重程度: {anomaly_report['severity']}\n异常数量: {anomaly_report['total_anomalies']}"

            }

        }

        

        requests.post(webhook, json=message)

    

    def _send_wechat_alert(self, anomaly_report: Dict):

        """发送企业微信告警"""

        webhook = self.alert_channels.get("wechat", {}).get("webhook")

        

        if not webhook:

            return

        

        message = {

            "msgtype": "text",

            "text": {

                "content": f"[数据质量告警]\n数据源: {anomaly_report['source_name']}\n严重程度: {anomaly_report['severity']}\n异常数量: {anomaly_report['total_anomalies']}"

            }

        }

        

        requests.post(webhook, json=message)

    

    def _log_alert(self, anomaly_report: Dict):

        """记录日志告警"""

        self.logger.warning(

            f"数据质量告警 - 数据源: {anomaly_report['source_name']}, "

            f"严重程度: {anomaly_report['severity']}, "

            f"异常数量: {anomaly_report['total_anomalies']}"

        )

```



---



## 四、实施步骤



### 4.1 环境准备 (1小时)



```bash

# 1. 安装依赖

pip install great-expectations pandas numpy requests



# 2. 安装监控工具

pip install prometheus-client grafana-api



# 3. 初始化Great Expectations

great_expectations init

```



### 4.2 配置数据源 (2小时)



```python

# config/data_sources.yaml



data_sources:

  tushare:

    type: tushare

    token: "your_tushare_token"

    enabled: true

    

  akshare:

    type: akshare

    enabled: true

    

  eastmoney:

    type: eastmoney

    url: "https://dataapi.eastmoney.com"

    enabled: true



quality_thresholds:

  completeness: 0.95

  accuracy: 0.98

  timeliness: 1  # 天



alert_channels:

  email:

    enabled: true

    sender: "your_email@gmail.com"

    receiver: "alert_receiver@gmail.com"

    smtp_server: "smtp.gmail.com"

    smtp_port: 587

    password: "your_password"

    

  dingtalk:

    enabled: true

    webhook: "https://oapi.dingtalk.com/robot/send?access_token=your_token"

    

  log:

    enabled: true

    level: "WARNING"

```



### 4.3 实现核心功能 (3小时)



```python

# src/data_quality/monitor.py



from data_source_quality_monitor import DataSourceQualityMonitor

from data_source_health_monitor import DataSourceHealthMonitor

from anomaly_detector import AnomalyDetector, AlertManager

import yaml

import schedule

import time



class DataQualityMonitoringSystem:

    """数据质量监控系统"""

    

    def __init__(self, config_path: str):

        with open(config_path, 'r') as f:

            self.config = yaml.safe_load(f)

        

        self.quality_monitor = DataSourceQualityMonitor(self.config)

        self.health_monitor = DataSourceHealthMonitor(self.config)

        self.anomaly_detector = AnomalyDetector(self.config)

        self.alert_manager = AlertManager(self.config)

    

    def run_quality_check(self, source_name: str, df):

        """运行质量检查"""

        # 1. 数据源健康检查

        health = self.health_monitor.check_data_source_health(source_name)

        

        # 2. 数据质量验证

        validation = self.quality_monitor.validate_data_source(df, source_name)

        

        # 3. 数据完整性检查

        completeness = self.quality_monitor.check_data_completeness(df)

        

        # 4. 数据准确性检查

        accuracy = self.quality_monitor.check_data_accuracy(df)

        

        # 5. 生成质量评分

        quality_score = self.quality_monitor.generate_quality_score(

            validation, completeness, accuracy

        )

        

        # 6. 异常检测

        anomalies = self.anomaly_detector.detect_anomalies(df, source_name)

        

        # 7. 发送告警

        if anomalies['severity'] in ['critical', 'high']:

            self.alert_manager.send_alert(anomalies)

        

        return {

            "health": health,

            "validation": validation,

            "completeness": completeness,

            "accuracy": accuracy,

            "quality_score": quality_score,

            "anomalies": anomalies

        }

    

    def start_monitoring(self):

        """启动监控"""

        # 定时任务

        schedule.every(1).hours.do(self._periodic_check)

        schedule.every(1).days.do(self._daily_report)

        

        while True:

            schedule.run_pending()

            time.sleep(60)

    

    def _periodic_check(self):

        """定期检查"""

        for source_name in self.config['data_sources'].keys():

            # 获取数据

            df = self._fetch_data(source_name)

            

            # 运行质量检查

            result = self.run_quality_check(source_name, df)

            

            # 记录结果

            self._log_result(result)

    

    def _daily_report(self):

        """生成日报"""

        # 生成每日质量报告

        pass

```



### 4.4 部署与测试 (2小时)



```bash

# 1. 运行测试

pytest tests/test_data_quality_monitor.py



# 2. 启动监控服务

python src/data_quality/monitor.py



# 3. 查看监控面板

# 访问 Grafana: http://localhost:3000

```



---



## 五、监控指标



### 5.1 核心指标



| 指标名称 | 说明 | 目标值 | 告警阈值 |

|---------|------|--------|---------|

| **数据源可用性** | 数据源正常可用时间占比 | ≥99% | <95% |

| **数据完整性** | 数据记录完整度 | ≥95% | <90% |

| **数据准确性** | 数据准确度 | ≥98% | <95% |

| **数据时效性** | 数据延迟天数 | ≤1天 | >3天 |

| **质量评分** | 综合质量评分 | ≥90分 | <80分 |



### 5.2 Grafana仪表板



```json

{

  "dashboard": {

    "title": "数据源质量监控",

    "panels": [

      {

        "title": "数据源健康状态",

        "type": "stat",

        "targets": [

          {

            "expr": "data_source_health_status"

          }

        ]

      },

      {

        "title": "数据质量评分",

        "type": "gauge",

        "targets": [

          {

            "expr": "data_quality_score"

          }

        ]

      },

      {

        "title": "异常数量趋势",

        "type": "graph",

        "targets": [

          {

            "expr": "data_anomaly_count"

          }

        ]

      }

    ]

  }

}

```



---



## 六、成本评估



### 6.1 开发成本



| 成本项 | 数量 | 单价 | 总价 |

|--------|------|------|------|

| **开发时间** | 1周 | 0 | 0 |

| **云服务器** | 1个月 | 500 | 500 |

| **监控工具** | 开源 | 0 | 0 |

| **总计** | - | - | **500** |



### 6.2 维护成本



| 成本项 | 月度成本 | 年度成本 |

|--------|---------|---------|

| **服务器维护** | 100 | 1,200 |

| **监控维护** | 50 | 600 |

| **总计** | **150** | **1,800** |



---



## 七、成功指标



### 7.1 技术指标



| 指标 | 目标值 | 衡量方式 |

|------|--------|---------|

| **数据源可用性** | ≥99% | 监控系统 |

| **数据完整性** | ≥95% | Great Expectations |

| **数据准确性** | ≥98% | 质量验证 |

| **告警响应时间** | ≤5分钟 | 日志分析 |



### 7.2 业务指标



| 指标 | 目标值 | 衡量方式 |

|------|--------|---------|

| **数据问题发现率** | ≥95% | 问题统计 |

| **误报率** | ≤5% | 告警分析 |

| **问题解决时间** | ≤2小时 | 工单统计 |



---



## 八、风险与缓解措施



### 8.1 技术风险



| 风险 | 影响 | 概率 | 缓解措施 |

|------|------|------|---------|

| **Great Expectations集成失败** | 高 | 低 | 提前POC验证 |

| **监控性能影响** | 中 | 中 | 异步处理 |

| **告警风暴** | 高 | 中 | 告警聚合 |



### 8.2 实施风险



| 风险 | 影响 | 概率 | 缓解措施 |

|------|------|------|---------|

| **配置错误** | 中 | 中 | 配置验证 |

| **监控盲区** | 高 | 低 | 全面测试 |

| **维护成本高** | 中 | 中 | 自动化运维 |



---



## 九、总结与建议



### 9.1 核心优势



1. **开源优先**: 使用Great Expectations等成熟开源项目

2. **自动化**: 全自动化质量检查和告警

3. **可视化**: Grafana仪表板实时监控

4. **成本可控**: 开发成本仅500,维护成本仅1,800/年



### 9.2 实施建议



1. **优先实施**: 作为Layer 0的核心基础设施,优先实施

2. **渐进式**: 先实施核心功能,再扩展高级功能

3. **持续优化**: 根据实际使用情况持续优化规则



### 9.3 预期成果



通过实施本蓝图,将实现:

- ✅ 数据源可用性≥99%

- ✅ 数据完整性≥95%

- ✅ 数据准确性≥98%

- ✅ 异常发现率≥95%

- ✅ 告警响应时间≤5分钟



---



**版本**: v1.0 | **更新**: 2026-04-06 | **状态**: ✅ 活跃

---



## 1. 文档治理



### 1.1 System_Manifest.md索引



```markdown

#### Layer 0: 数据源层

##### 0.001. Data Source Quality Monitoring Blueprint

- **模块ID**: DATA_SOURCE_QUALITY_MONITORING_BLUEPRINT_001

- **蓝图文档**: DATA_SOURCE_QUALITY_MONITORING_BLUEPRINT.md

- **技术规格书**: 待创建

- **职责**: Layer 0数据源质量监控

- **状态**: Active

```



### 1.2 模块职责边界



| 模块 | 职责 | 边界 |

|------|------|------|

| **Data Source Quality Monitoring Blueprint** | Layer 0数据源质量监控 | **核心模块** |



### 1.3 版本管理



| 版本 | 日期 | 变更内容 | 变更人 |

|------|------|----------|--------|

| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |



---



**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active

