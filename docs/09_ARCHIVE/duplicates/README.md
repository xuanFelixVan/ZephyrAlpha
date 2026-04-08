---
module_id: 02_FACTOR_LIBRARY_04_DATA_SOURCE_07_DATA_PIPELINE_001
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from enum import Enum
import logging
logger = logging.getLogger(__name__)
class DataSourceType(Enum):
AKSHARE = "akshare"
TUSHARE = "tushare"
IFIND = "ifind"
CHOICE = "choice"
class DataQuality(Enum):
EXCELLENT = "excellent"
GOOD = "good"
ACCEPTABLE = "acceptable"
POOR = "poor"
@dataclass
class DataRequest:
symbol: str
start_date: date
end_date: date
fields: List[str]
source_priority: List[DataSourceType]
timeout: int = 30
retry_count: int = 3
@dataclass
class DataResponse:
success: bool
data: Any
source: DataSourceType
quality: DataQuality
```
responsibility:
- 管理因子库
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
