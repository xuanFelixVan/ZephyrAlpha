---
module_id: 07_RESEARCH_04_EXPERIMENT_TRACKING_EXPERIMENT_TRACKING
layer: layer_00
version: 1.0.0
status: Active
responsibility:
  - Experiment Tracking相关业务
created_date: 2026-04-01
last_updated: 2026-04-07
owner: 首席文档架构?
standard_type: 专业量化机构研究标准
applicable_scope: 量化研究实验
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---

## 1. 概述



实验追踪系统记录每次量化研究的参数、结果、代码版本，确保研究可复现?



**设计原则**?

- **极简** - 单人开发，不需要复杂系统

- **自动?* - 脚本自动记录，无需人工干预

- **可复?* - 记录足够信息重现实验



```
```---
```



## 2. 实验记录结构



### 2.1 实验记录模板



```json

{

    "experiment_id": "EXP_20260328_001",

    "experiment_name": "ALPHA_001_MACD参数优化",

    "created_at": "2026-03-28 10:30:00",

    "status": "COMPLETED",

    "researcher": "system",



    "research_type": "factor_optimization",

    "target": "ALPHA_001",



    "parameters": {

        "fast_period": 12,

        "slow_period": 26,

        "signal_period": 9,

        "stock_pool": "全市?,

        "rebalance_freq": "D"

    },



    "results": {

        "ic_mean": 0.0523,

        "ic_ir": 0.842,

        "sharpe_ratio": 1.23,

        "max_drawdown": 0.082

    },



    "code_version": {

        "file": "factors/alpha_001_macd.py",

        "commit": "a1b2c3d4"

    },



    "data_version": {

        "price_data": "v202603",

        "factor_data": "v202603"

    },



    "parent_experiment": "EXP_20260327_005",

    "notes": "优化后IC提升15%",

    "tags": ["macd", "optimization", "参数调优"]

}

```



```
```---
```



## 3. 实验记录?



### 3.1 基础记录?



```python

import json

import csv

from datetime import datetime

from pathlib import Path

from typing import Optional



class ExperimentTracker:

    """实验追踪?""



    def __init__(self, storage_path: str = "data/experiments"):

        self.storage_path = Path(storage_path)

        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.experiments_file = self.storage_path / "experiments.jsonl"

        self.experiments_file.touch(exist_ok=True)



    def record(

        self,

        experiment_name: str,

        research_type: str,

        parameters: dict,

        results: dict,

        parent_id: Optional[str] = None,

        notes: str = "",

        tags: list = None

    ) -> str:

        """

        记录实验



        Parameters:

        -----------

        experiment_name : str

            实验名称

        research_type : str

            研究类型: factor_test | optimization | backtest | strategy

        parameters : dict

            实验参数

        results : dict

            实验结果

        parent_id : str

            父实验ID（用于追踪迭代）

        notes : str

            实验笔记

        tags : list

            标签



        Returns:

        --------

        str: 实验ID

        """

        experiment_id = self._generate_id()



        record = {

            "experiment_id": experiment_id,

            "experiment_name": experiment_name,

            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            "status": "COMPLETED",

            "researcher": "system",

            "research_type": research_type,

            "parameters": parameters,

            "results": results,

            "code_version": self._get_code_version(),

            "data_version": self._get_data_version(),

            "parent_experiment": parent_id,

            "notes": notes,

            "tags": tags or []

        }



        # 追加到文?

        with open(self.experiments_file, 'a', encoding='utf-8') as f:

            f.write(json.dumps(record, ensure_ascii=False) + '\n')



        return experiment_id



    def _generate_id(self) -> str:

        """生成实验ID"""

        date_str = datetime.now().strftime("%Y%m%d")

        # 计算当天实验?

        n_today = self._count_today_experiments() + 1

        return f"EXP_{date_str}_{n_today:03d}"



    def _count_today_experiments(self) -> int:

        """统计当天实验?""

        today = datetime.now().strftime("%Y-%m-%d")

        count = 0

        try:

            with open(self.experiments_file, 'r', encoding='utf-8') as f:

                for line in f:

                    record = json.loads(line)

                    if record['created_at'].startswith(today):

                        count += 1

        except:

            pass

        return count



    def _get_code_version(self) -> dict:

        """获取代码版本"""

        return {

            "file": "unknown",

            "commit": "unknown"

        }



    def _get_data_version(self) -> dict:

        """获取数据版本"""

        return {

            "price_data": "unknown",

            "factor_data": "unknown"

        }

```



```
```---
```



## 4. 实验查询



### 4.1 查询接口



```python

class ExperimentQuery:

    """实验查询"""



    def __init__(self, tracker: ExperimentTracker):

        self.tracker = tracker



    def load_all(self) -> list:

        """加载所有实?""

        experiments = []

        try:

            with open(self.tracker.experiments_file, 'r', encoding='utf-8') as f:

                for line in f:

                    experiments.append(json.loads(line))

        except:

            pass

        return experiments



    def query_by_name(self, name: str) -> list:

        """按名称查?""

        all_exps = self.load_all()

        return [e for e in all_exps if name in e.get('experiment_name', '')]



    def query_by_type(self, research_type: str) -> list:

        """按类型查?""

        all_exps = self.load_all()

        return [e for e in all_exps if e.get('research_type') == research_type]



    def query_by_tag(self, tag: str) -> list:

        """按标签查?""

        all_exps = self.load_all()

        return [e for e in all_exps if tag in e.get('tags', [])]



    def query_by_date_range(self, start_date: str, end_date: str) -> list:

        """按日期范围查?""

        all_exps = self.load_all()

        return [

            e for e in all_exps

            if start_date <= e.get('created_at', '')[:10] <= end_date

        ]



    def find_parent_chain(self, experiment_id: str) -> list:

        """查找父实验链"""

        chain = []

        current_id = experiment_id



        while current_id:

            exp = self.find_by_id(current_id)

            if exp:

                chain.append(exp)

                current_id = exp.get('parent_experiment')

            else:

                break



        return chain



    def find_by_id(self, experiment_id: str) -> Optional[dict]:

        """按ID查询"""

        all_exps = self.load_all()

        for exp in all_exps:

            if exp.get('experiment_id') == experiment_id:

                return exp

        return None

```



```
```---
```



## 5. 实验对比



### 5.1 对比分析



```python

class ExperimentComparison:

    """实验对比"""



    def compare(self, exp_id1: str, exp_id2: str) -> dict:

        """

        对比两个实验



        Returns:

        --------

        dict: 对比结果

        """

        tracker = ExperimentTracker()

        query = ExperimentQuery(tracker)



        exp1 = query.find_by_id(exp_id1)

        exp2 = query.find_by_id(exp_id2)



        if not exp1 or not exp2:

            return {"error": "Experiment not found"}



        results1 = exp1.get('results', {})

        results2 = exp2.get('results', {})



        comparison = {

            "experiment1": exp_id1,

            "experiment2": exp_id2,

            "name1": exp1.get('experiment_name'),

            "name2": exp2.get('experiment_name'),

            "metrics_comparison": {}

        }



        # 对比每个指标

        all_metrics = set(results1.keys()) | set(results2.keys())

        for metric in all_metrics:

            val1 = results1.get(metric, 0)

            val2 = results2.get(metric, 0)



            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):

                diff = val2 - val1

                pct_change = (diff / val1 * 100) if val1 != 0 else 0



                comparison["metrics_comparison"][metric] = {

                    "exp1": val1,

                    "exp2": val2,

                    "diff": diff,

                    "pct_change": pct_change,

                    "winner": "exp1" if diff > 0 else "exp2"

                }



        return comparison



    def generate_comparison_report(self, exp_id1: str, exp_id2: str) -> str:

        """生成对比报告"""

        comparison = self.compare(exp_id1, exp_id2)



        if "error" in comparison:

            return f"Error: {comparison['error']}"



        report = f"""

# 实验对比报告



## 实验信息



| 项目 | 实验1 | 实验2 |

|------|-------|-------|

| ID | {comparison['experiment1']} | {comparison['experiment2']} |

| 名称 | {comparison['name1']} | {comparison['name2']} |



## 指标对比



| 指标 | 实验1 | 实验2 | 差异 | 变化?| 胜出 |

|------|-------|-------|------|--------|------|

"""



        for metric, data in comparison["metrics_comparison"].items():

            report += f"| {metric} | {data['exp1']:.4f} | {data['exp2']:.4f} | {data['diff']:+.4f} | {data['pct_change']:+.2f}% | {data['winner']} |\n"



        return report

```



```
```---
```



## 6. 自动记录装饰?



### 6.1 实验记录装饰?



```python

from functools import wraps



def track_experiment(tracker: ExperimentTracker, experiment_name: str = None):

    """

    实验追踪装饰?



    Usage:

    ------

    @track_experiment(tracker, "MACD优化")

    def run_macd_experiment(fast=12, slow=26):

        # 实验代码

        return results

    """

    def decorator(func):

        @wraps(func)

        def wrapper(*args, **kwargs):

            name = experiment_name or func.__name__



            # 记录参数

            params = {"args": args, "kwargs": kwargs}



            try:

                # 执行实验

                results = func(*args, **kwargs)



                # 记录成功

                tracker.record(

                    experiment_name=name,

                    research_type="experiment",

                    parameters=params,

                    results=results

                )



                return results



            except Exception as e:

                # 记录失败

                tracker.record(

                    experiment_name=name,

                    research_type="experiment",

                    parameters=params,

                    results={"error": str(e)},

                    notes="Experiment failed"

                )

                raise



        return wrapper

    return decorator

```



```
```---
```



## 7. 配置模板



```yaml

# config/experiment_tracking.yaml

experiment_tracking:

  # 存储路径

  storage_path: "data/experiments/"



  # 自动记录

  auto_record:

    enabled: true

    record_parameters: true

    record_code_version: true

    record_data_version: true



  # 代码版本控制

  version_control:

    enabled: false  # 单人开发不需要git

    git_repo: ""



  # 保留策略

  retention:

    keep_days: 365    # 保留365?

    archive_old: true  # 归档旧实?

```



```
```---
```



## 8. 目录结构



```

07_RESEARCH/

├── 04_EXPERIMENT_TRACKING/

?  ├── README.md

?  ├── experiment_tracking.md      # 本文??

?  └── auto_recording.md           # 自动记录(简化版)

```



```
```---
```



## 9. 接口定义



| 接口 | 说明 |

|------|------|

| **上游接口** | 所有研?回测函数（通过装饰器） |

| **下游接口** | 研究报告、策略迭代|

| **存储格式** | JSONL文件（每行一个实验） |



```
```---
```



## 10. 使用示例



```python

# 示例：运行因子实验并自动记录

tracker = ExperimentTracker()



@track_experiment(tracker, "RSI参数实验")

def run_rsi_experiment(period=14, overbought=70, oversold=30):

    """RSI参数实验"""

    # 1. 获取数据

    data = get_price_data("2020-01-01", "2025-12-31")



    # 2. 计算因子

    rsi_values = calculate_rsi(data, period)



    # 3. IC分析

    ic_result = analyze_ic(rsi_values, data['return'])



    # 4. 返回结果

    return {

        "ic_mean": ic_result['ic_mean'],

        "ic_ir": ic_result['ic_ir'],

        "sharpe": ic_result['sharpe']

    }



# 运行实验

results = run_rsi_experiment(period=14, overbought=70, oversold=30)



# 查询实验

query = ExperimentQuery(tracker)

exps = query.query_by_name("RSI参数实验")

```



```
```---
```



## 更新记录



| 版本 | 日期 | 变更内容 |

|------|------|----------|

| v1.0 | 2026-03-28 | 初始版本 |

