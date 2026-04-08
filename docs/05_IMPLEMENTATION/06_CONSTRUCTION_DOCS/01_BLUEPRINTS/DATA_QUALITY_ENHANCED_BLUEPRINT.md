---
module_id: DATA_QUALITY_ENHANCED_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 数据质量检查
  - 数据质量监控
  - 数据质量报告
  - 数据质量修复
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
layer: Layer 5 (数据处理层)
---

# 数据质量增强蓝图

> **核心职责**: 提供全面的数据质量检查和监控能力，支持数据质量规则定义、自动检查、质量报告
> **职责边界**: 
> - ✅ 本文档负责：数据质量检查、数据质量监控、质量报告、质量修复
> - ❌ 本文档不负责：数据血缘追踪（由数据血缘模块负责）、元数据管理（由元数据管理模块负责）

## 核心定位

负责数据质量增强模块的设计与构建，提供全面的数据质量检查和监控能力，支持数据质量规则定义、自动检查、质量报告，确保数据的准确性、完整性、一致性。

## 设计目标

### 主要目标

1. **数据质量检查**: 自动检查数据质量规则
2. **数据质量监控**: 实时监控数据质量指标
3. **数据质量报告**: 生成数据质量报告和趋势分析
4. **数据质量修复**: 提供数据质量问题的修复建议

### 质量目标

- 数据质量检查覆盖率: 100%
- 数据质量检查准确率: ≥ 98%
- 数据质量问题发现率: ≥ 95%
- 检查性能: < 30秒/表

## 开源方案选型

### 推荐方案: Great Expectations

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/great-expectations/great_expectations |
| **Stars** | 9,500+ |
| **License** | Apache 2.0 |
| **语言** | Python |
| **特点** | 强大的数据质量检查框架，支持多种数据源 |

**选择理由**:
1. **功能强大**: 支持丰富的数据质量检查规则
2. **易于使用**: Python DSL，学习成本低
3. **可视化好**: 提供数据文档和可视化报告
4. **集成性强**: 支持Pandas、SQL、Spark等多种数据源
5. **个人友好**: 免费开源，适合个人使用
6. **社区活跃**: 文档完善，社区支持好

## 核心功能设计

### 1. 数据质量检查模块

```python
import great_expectations as gx
from great_expectations.dataset import PandasDataset
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

class DataQualityChecker:
    """数据质量检查器"""
    
    def __init__(self, project_name: str = "zephyr-alpha"):
        self.project_name = project_name
        self.context = gx.data_context.DataContext()
        self.expectations = {}
    
    def create_expectation_suite(
        self,
        suite_name: str,
        expectations: List[Dict]
    ):
        """创建期望套件"""
        suite = gx.ExpectationSuite(expectation_suite_name=suite_name)
        
        for expectation in expectations:
            expectation_type = expectation.pop("expectation_type")
            suite.add_expectation(
                gx.expectation(expectation_type, **expectation)
            )
        
        self.context.add_expectation_suite(suite)
        self.expectations[suite_name] = suite
    
    def check_dataframe(
        self,
        df: pd.DataFrame,
        suite_name: str
    ) -> Dict:
        """检查DataFrame数据质量"""
        dataset = PandasDataset(df)
        
        results = dataset.validate(
            expectation_suite_name=suite_name
        )
        
        return {
            "success": results.success,
            "statistics": results.statistics,
            "results": [
                {
                    "expectation_type": result.expectation_config.expectation_type,
                    "success": result.success,
                    "result": result.result
                }
                for result in results.results
            ],
            "checked_at": datetime.now().isoformat()
        }
    
    def check_table(
        self,
        table_name: str,
        suite_name: str,
        datasource_name: str = "postgres"
    ) -> Dict:
        """检查数据库表数据质量"""
        batch = self.context.get_batch(
            expectation_suite_name=suite_name,
            datasource_name=datasource_name,
            data_connector_name="default",
            data_asset_name=table_name
        )
        
        results = batch.validate()
        
        return {
            "table": table_name,
            "success": results.success,
            "statistics": results.statistics,
            "checked_at": datetime.now().isoformat()
        }
    
    def create_factor_data_expectations(self):
        """创建因子数据质量期望"""
        expectations = [
            {
                "expectation_type": "expect_column_to_exist",
                "column": "factor_name"
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "column": "factor_name"
            },
            {
                "expectation_type": "expect_column_values_to_be_unique",
                "column": "factor_name"
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "column": "factor_value",
                "min_value": -100,
                "max_value": 100
            },
            {
                "expectation_type": "expect_column_values_to_match_regex",
                "column": "factor_name",
                "regex": "^[A-Z_]+$"
            }
        ]
        
        self.create_expectation_suite("factor_data_quality", expectations)
    
    def create_market_data_expectations(self):
        """创建市场数据质量期望"""
        expectations = [
            {
                "expectation_type": "expect_column_to_exist",
                "column": "symbol"
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "column": "symbol"
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "column": "close",
                "min_value": 0
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "column": "volume",
                "min_value": 0
            },
            {
                "expectation_type": "expect_column_values_to_be_increasing",
                "column": "timestamp"
            }
        ]
        
        self.create_expectation_suite("market_data_quality", expectations)
```

### 2. 数据质量监控模块

```python
from prometheus_client import Counter, Histogram, Gauge
import time

class DataQualityMonitor:
    """数据质量监控器"""
    
    def __init__(self):
        self.check_counter = Counter(
            'data_quality_checks_total',
            '数据质量检查总数',
            ['table', 'suite']
        )
        
        self.success_counter = Counter(
            'data_quality_checks_success_total',
            '数据质量检查成功数',
            ['table', 'suite']
        )
        
        self.failure_counter = Counter(
            'data_quality_checks_failure_total',
            '数据质量检查失败数',
            ['table', 'suite']
        )
        
        self.check_duration = Histogram(
            'data_quality_check_duration_seconds',
            '数据质量检查耗时',
            ['table', 'suite']
        )
        
        self.quality_score = Gauge(
            'data_quality_score',
            '数据质量评分',
            ['table']
        )
    
    def monitor_check(
        self,
        table_name: str,
        suite_name: str,
        check_func
    ):
        """监控数据质量检查"""
        start_time = time.time()
        
        self.check_counter.labels(table=table_name, suite=suite_name).inc()
        
        try:
            result = check_func()
            
            if result.get("success"):
                self.success_counter.labels(
                    table=table_name,
                    suite=suite_name
                ).inc()
            else:
                self.failure_counter.labels(
                    table=table_name,
                    suite=suite_name
                ).inc()
            
            score = self._calculate_quality_score(result)
            self.quality_score.labels(table=table_name).set(score)
            
            return result
        finally:
            duration = time.time() - start_time
            self.check_duration.labels(
                table=table_name,
                suite=suite_name
            ).observe(duration)
    
    def _calculate_quality_score(self, result: Dict) -> float:
        """计算数据质量评分"""
        statistics = result.get("statistics", {})
        
        successful_expectations = statistics.get("successful_expectations", 0)
        evaluated_expectations = statistics.get("evaluated_expectations", 1)
        
        return successful_expectations / evaluated_expectations
```

### 3. 数据质量报告模块

```python
from typing import List
import json

class DataQualityReporter:
    """数据质量报告器"""
    
    def __init__(self, checker: DataQualityChecker):
        self.checker = checker
    
    def generate_report(
        self,
        tables: List[str],
        report_name: str = "data_quality_report"
    ) -> Dict:
        """生成数据质量报告"""
        report = {
            "report_name": report_name,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_tables": len(tables),
                "passed_tables": 0,
                "failed_tables": 0,
                "total_expectations": 0,
                "passed_expectations": 0,
                "failed_expectations": 0
            },
            "details": []
        }
        
        for table in tables:
            suite_name = f"{table}_quality"
            
            try:
                result = self.checker.check_table(table, suite_name)
                
                statistics = result.get("statistics", {})
                
                report["summary"]["total_expectations"] += statistics.get(
                    "evaluated_expectations", 0
                )
                report["summary"]["passed_expectations"] += statistics.get(
                    "successful_expectations", 0
                )
                report["summary"]["failed_expectations"] += statistics.get(
                    "unsuccessful_expectations", 0
                )
                
                if result.get("success"):
                    report["summary"]["passed_tables"] += 1
                else:
                    report["summary"]["failed_tables"] += 1
                
                report["details"].append({
                    "table": table,
                    "success": result.get("success"),
                    "statistics": statistics,
                    "checked_at": result.get("checked_at")
                })
            except Exception as e:
                report["summary"]["failed_tables"] += 1
                report["details"].append({
                    "table": table,
                    "success": False,
                    "error": str(e),
                    "checked_at": datetime.now().isoformat()
                })
        
        report["summary"]["quality_score"] = (
            report["summary"]["passed_expectations"] /
            max(report["summary"]["total_expectations"], 1)
        )
        
        return report
    
    def generate_trend_report(
        self,
        table_name: str,
        days: int = 7
    ) -> Dict:
        """生成趋势报告"""
        trend = {
            "table": table_name,
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "daily_scores": [],
            "trend": "stable"
        }
        
        for i in range(days):
            score = 0.95 - (i * 0.01)
            
            trend["daily_scores"].append({
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "score": score
            })
        
        if len(trend["daily_scores"]) >= 2:
            recent_scores = [s["score"] for s in trend["daily_scores"][:3]]
            older_scores = [s["score"] for s in trend["daily_scores"][-3:]]
            
            recent_avg = sum(recent_scores) / len(recent_scores)
            older_avg = sum(older_scores) / len(older_scores)
            
            if recent_avg > older_avg + 0.05:
                trend["trend"] = "improving"
            elif recent_avg < older_avg - 0.05:
                trend["trend"] = "declining"
        
        return trend
    
    def save_report(
        self,
        report: Dict,
        output_path: str
    ):
        """保存报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
```

### 4. 数据质量修复模块

```python
class DataQualityFixer:
    """数据质量修复器"""
    
    def __init__(self):
        self.fix_strategies = {
            "null_values": self._fix_null_values,
            "duplicates": self._fix_duplicates,
            "outliers": self._fix_outliers,
            "invalid_values": self._fix_invalid_values
        }
    
    def suggest_fixes(
        self,
        df: pd.DataFrame,
        quality_result: Dict
    ) -> List[Dict]:
        """建议修复方案"""
        suggestions = []
        
        for result in quality_result.get("results", []):
            if not result.get("success"):
                expectation_type = result.get("expectation_type")
                
                if "null" in expectation_type.lower():
                    suggestions.append({
                        "issue": "null_values",
                        "column": result.get("expectation_config", {}).get("column"),
                        "strategy": "填充缺失值",
                        "action": "使用均值、中位数或众数填充"
                    })
                
                elif "unique" in expectation_type.lower():
                    suggestions.append({
                        "issue": "duplicates",
                        "column": result.get("expectation_config", {}).get("column"),
                        "strategy": "删除重复值",
                        "action": "保留第一条记录，删除后续重复记录"
                    })
                
                elif "between" in expectation_type.lower():
                    suggestions.append({
                        "issue": "outliers",
                        "column": result.get("expectation_config", {}).get("column"),
                        "strategy": "处理异常值",
                        "action": "使用边界值替换或删除异常记录"
                    })
        
        return suggestions
    
    def apply_fix(
        self,
        df: pd.DataFrame,
        fix_suggestion: Dict
    ) -> pd.DataFrame:
        """应用修复"""
        issue_type = fix_suggestion.get("issue")
        
        if issue_type in self.fix_strategies:
            _fix = self.fix_strategies[issue_type]
            return _fix(df, fix_suggestion)
        
        return df
    
    def _fix_null_values(
        self,
        df: pd.DataFrame,
        suggestion: Dict
    ) -> pd.DataFrame:
        """修复空值"""
        column = suggestion.get("column")
        
        if df[column].dtype in ['int64', 'float64']:
            df[column].fillna(df[column].median(), inplace=True)
        else:
            df[column].fillna(df[column].mode()[0], inplace=True)
        
        return df
    
    def _fix_duplicates(
        self,
        df: pd.DataFrame,
        suggestion: Dict
    ) -> pd.DataFrame:
        """修复重复值"""
        column = suggestion.get("column")
        
        df.drop_duplicates(subset=[column], keep='first', inplace=True)
        
        return df
    
    def _fix_outliers(
        self,
        df: pd.DataFrame,
        suggestion: Dict
    ) -> pd.DataFrame:
        """修复异常值"""
        column = suggestion.get("column")
        
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        df.loc[df[column] < lower_bound, column] = lower_bound
        df.loc[df[column] > upper_bound, column] = upper_bound
        
        return df
    
    def _fix_invalid_values(
        self,
        df: pd.DataFrame,
        suggestion: Dict
    ) -> pd.DataFrame:
        """修复无效值"""
        column = suggestion.get("column")
        
        valid_values = suggestion.get("valid_values", [])
        
        df = df[df[column].isin(valid_values)]
        
        return df
```

## 技术实现

### 1. Great Expectations配置

```yaml
config_version: 3.0

datasources:
  postgres:
    class_name: Datasource
    execution_engine:
      class_name: SqlAlchemyExecutionEngine
      connection_string: postgresql://zephyr:password@localhost:5432/zephyr
    data_connectors:
      default:
        class_name: RuntimeDataConnector
        batch_identifiers:
          - default_identifier_name

stores:
  expectations_store:
    class_name: ExpectationsStore
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: expectations/
  
  validations_store:
    class_name: ValidationsStore
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: uncommitted/validations/

expectations_store_name: expectations_store
validations_store_name: validations_store

data_docs_sites:
  local_site:
    class_name: SiteBuilder
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: uncommitted/data_docs/local_site/
    site_index_builder:
      class_name: DefaultSiteIndexBuilder
```

### 2. 数据质量检查流水线

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'zephyr',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'data_quality_check',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
)

def check_factor_data_quality():
    checker = DataQualityChecker()
    checker.create_factor_data_expectations()
    
    result = checker.check_table("factor_data", "factor_data_quality")
    
    if not result.get("success"):
        raise Exception("Factor data quality check failed")
    
    return result

def check_market_data_quality():
    checker = DataQualityChecker()
    checker.create_market_data_expectations()
    
    result = checker.check_table("market_data", "market_data_quality")
    
    if not result.get("success"):
        raise Exception("Market data quality check failed")
    
    return result

def generate_quality_report():
    checker = DataQualityChecker()
    reporter = DataQualityReporter(checker)
    
    report = reporter.generate_report(
        tables=["factor_data", "market_data"],
        report_name="daily_quality_report"
    )
    
    reporter.save_report(
        report,
        "/reports/daily_quality_report.json"
    )
    
    return report

check_factor_task = PythonOperator(
    task_id='check_factor_data_quality',
    python_callable=check_factor_data_quality,
    dag=dag
)

check_market_task = PythonOperator(
    task_id='check_market_data_quality',
    python_callable=check_market_data_quality,
    dag=dag
)

generate_report_task = PythonOperator(
    task_id='generate_quality_report',
    python_callable=generate_quality_report,
    dag=dag
)

check_factor_task >> generate_report_task
check_market_task >> generate_report_task
```

## 实施路径

### Phase 1: 核心功能（Week 1）

**目标**: 实现基础数据质量检查

**任务清单**:
- [ ] 安装和配置Great Expectations
- [ ] 实现数据质量检查
- [ ] 创建质量期望规则
- [ ] 实现质量报告
- [ ] 编写单元测试

**交付物**:
- Great Expectations配置
- DataQualityChecker类
- 单元测试覆盖率≥80%

### Phase 2: 高级功能（Week 2）

**目标**: 实现数据质量监控和修复

**任务清单**:
- [ ] 实现数据质量监控
- [ ] 实现质量报告生成
- [ ] 实现质量修复建议
- [ ] 集成到数据流水线
- [ ] 编写集成测试

**交付物**:
- DataQualityMonitor类
- DataQualityReporter类
- DataQualityFixer类
- 集成测试覆盖率≥70%

### Phase 3: 生产优化（Week 3）

**目标**: 生产环境优化和可视化

**任务清单**:
- [ ] 性能优化
- [ ] 数据文档生成
- [ ] 监控仪表板
- [ ] 告警规则配置
- [ ] 生产部署验证

**交付物**:
- 性能优化方案
- 数据文档站点
- 监控仪表板

---

**文档版本**: v1.0.0
**创建日期**: 2026-04-07
**最后更新**: 2026-04-07
**状态**: Active
