---
module_id: IMPL_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---

# 数据血缘管�?

> 自动追踪数据来源、转换过程、质量监�?

**版本**: v1.0
**更新**: 2026-03-29
**Layer**: Layer 1 (数据�?
**优先�?*: P1 - AI必需

---

## 1. 为什么AI需要数据血�?

```
�?监督) �?AI(执行) �?AI(优化) �?�?监督) �?AI(报告)

AI报告需要回答：
- "这个因子为什么是这个值？"
- "数据从哪里来的？"
- "计算过程是什么？"
�?需要数据血缘来保证AI输出的可解释�?
```

---

## 2. 数据血缘架�?

```python
@dataclass
class DataLineage:
    """数据血缘记�?""
    data_id: str
    source: str                           # 数据来源
    source_type: str                      # 'api' / 'crawl' / 'compute'
    timestamp: datetime
    transformation_steps: List[Transform]  # 转换步骤
    quality_score: float                   # 质量评分

@dataclass
class Transform:
    """转换步骤"""
    step_id: str
    operation: str                        # 'clean' / 'fillna' / 'normalize'
    input_fields: List[str]
    output_fields: List[str]
    parameters: dict
```

---

## 3. 自动血缘追�?

```python
class LineageTracker:
    """自动数据血缘追�?""

    def __init__(self):
        self.lineage_db = {}
        self.transform_registry = {}

    def record_extraction(self, data_id: str, source: str,
                        source_type: str, raw_data: pd.DataFrame) -> None:
        """记录数据提取"""
        self.lineage_db[data_id] = DataLineage(
            data_id=data_id,
            source=source,
            source_type=source_type,
            timestamp=datetime.now(),
            transformation_steps=[],
            quality_score=self._assess_quality(raw_data)
        )

    def record_transformation(self, data_id: str, transform: Transform) -> None:
        """记录数据转换"""
        if data_id in self.lineage_db:
            self.lineage_db[data_id].transformation_steps.append(transform)

    def get_lineage(self, data_id: str) -> DataLineage:
        """获取数据血�?""
        return self.lineage_db.get(data_id)

    def get_data_origin(self, data_id: str) -> str:
        """追溯数据源头"""
        lineage = self.lineage_db.get(data_id)
        if not lineage:
            return "Unknown"

        origin = lineage.source
        for step in lineage.transformation_steps:
            origin = f"{step.operation}({origin})"
        return origin
```

---

## 4. 数据质量监控

```python
class DataQualityMonitor:
    """数据质量监控"""

    def assess_quality(self, df: pd.DataFrame, data_type: str) -> dict:
        """评估数据质量"""
        return {
            'completeness': self._check_completeness(df),
            'accuracy': self._check_accuracy(df),
            'consistency': self._check_consistency(df),
            'timeliness': self._check_timeliness(df),
            'overall_score': self._calculate_score(df)
        }

    def _check_completeness(self, df: pd.DataFrame) -> float:
        """完整性检�?""
        non_null_ratio = df.notna().sum().sum() / df.size
        return non_null_ratio

    def _check_accuracy(self, df: pd.DataFrame) -> float:
        """准确性检�?""
        # 基础检查：价格是否为正、成交量是否非负
        if 'close' in df.columns:
            invalid_prices = (df['close'] <= 0).sum()
        else:
            invalid_prices = 0
        return 1 - (invalid_prices / len(df))

    def generate_quality_report(self, data_id: str) -> str:
        """生成质量报告（AI报告素材�?""
        lineage = self.lineage_tracker.get_lineage(data_id)
        quality = self.assess_quality(lineage)

        report = f"""
数据质量报告 - {data_id}
========================
数据来源: {lineage.source}
提取时间: {lineage.timestamp}
质量评分: {quality['overall_score']:.2%}

完整�? {quality['completeness']:.2%}
准确�? {quality['accuracy']:.2%}
一致�? {quality['consistency']:.2%}
时效�? {quality['timeliness']:.2%}

数据血�?
{self._format_lineage(lineage)}
"""
        return report
```

---

## 5. 血缘追踪应用场�?

### AI因子计算追溯

```python
class FactorLineageTracker:
    """因子血缘追�?""

    def track_factor_calculation(self, factor_name: str,
                                input_data: dict,
                                output: pd.Series) -> None:
        """追踪因子计算过程"""
        factor_id = f"{factor_name}_{datetime.now().strftime('%Y%m%d')}"

        # 记录输入数据血�?
        for name, data in input_data.items():
            self.lineage_tracker.record_extraction(
                data_id=f"{factor_id}_input_{name}",
                source=name,
                source_type='compute',
                raw_data=data
            )

        # 记录因子计算
        self.lineage_tracker.record_extraction(
            data_id=factor_id,
            source=f"factor:{factor_name}",
            source_type='compute',
            raw_data=output.to_frame()
        )

    def explain_factor(self, factor_id: str) -> str:
        """解释因子来源（AI输出�?""
        lineage = self.lineage_tracker.get_lineage(factor_id)
        return f"""
因子 {factor_id} 来源说明:
- 计算时间: {lineage.timestamp}
- 数据来源: {lineage.source}
- 转换步骤: {len(lineage.transformation_steps)} �?
- 质量评分: {lineage.quality_score:.2%}
"""
```

---

## 6. 层级关系

```
Layer 1 (数据�?
    �?上游
数据�?(API/爬虫/文件)
    �?下游
因子计算 �?策略信号 �?订单执行 �?AI报告
          �?
       需要血缘保证可解释�?
```

---

## 索引

- 父目�? [04_DATA_SOURCE/README.md](../../02_FACTOR_LIBRARY/04_DATA_SOURCE/README.md)
- 相关: [DAILY_PIPELINE.md](./DAILY_PIPELINE.md)
