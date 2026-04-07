---
module_id: DATA_VERSION_CONTROL_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 1 æ°æ®å±?
compliance_level: ä¸ä¸æ å
responsibility:
  - æ°æ®çæ¬ç®¡ç
  - æ°æ®åæº¯
  - æ°æ®å®¡è®¡
  - çæ¬æ§å¶
layer: Layer 5.1 (数据处理)
---

# æ°æ®çæ¬æ§å¶èå¾

> **æ ¸å¿èè´£**: æ°æ®çæ¬æ§å¶ï¼ç®¡çæ°æ®éçæ¬ï¼æ¯ææ°æ®åæº¯åå®¡è®¡
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼æ°æ®çæ¬ç®¡çãæ°æ®åæº¯ãæ°æ®å®¡è®¡ãçæ¬æ§å?
> - â?æ¬ææ¡£ä¸è´è´£ï¼æ°æ®å­å¨ãæ°æ®å¤çãæ°æ®è´¨éçæ?

> **æ ¸å¿å®ä½**: æ°æ®çæ¬æ§å¶èå¾çæ ¸å¿åè½å®ç?


> æ¸é£éåç³»ç» v5.3 - æ°æ®çæ¬æ§å¶ç³»ç»è¯¦ç»è®¾è®¡
> **æ¨¡åID**: `DATA_VERSION_CTRL_001`
> **å®æ½å¨æ**: Week 29-30ï¼?å¨ï¼
> **ä¼åçº?*: P2ï¼ä¼åï¼
> **é¢ææ¶ç**: æåæ°æ®å¯è¿½æº¯æ?5%ï¼æ¯ææ°æ®åæ»åå®¡è®¡

## æ ¸å¿å®ä½

> æ ¸å¿èè´£: æ°æ®çæ¬æ§å¶ï¼ç®¡çæ°æ®éçæ¬ï¼æ¯ææ°æ®åæº¯åå®¡è®¡
> èè´£è¾¹ç: 
> - â?æ¬ææ¡£è´è´£ï¼æ°æ®çæ¬ç®¡çãæ°æ®åæº¯ãæ°æ®å®¡è®¡ãçæ¬æ§å?
> - â?æ¬ææ¡£ä¸è´è´£ï¼æ°æ®å­å¨ãæ°æ®å¤çãæ°æ®è´¨éçæ§ï¼ç¡®ä¿ç³»ç»åè½çç¨³å®è¿è¡åé«ææ§è¡ã?


## ä¸ãè®¾è®¡èæ¯ä¸ç®æ 

### 1.1 ä¸å¡éæ±?

**å½åçç¹**:
- æ°æ®åæ´æ æ³è¿½æº¯
- æ°æ®åæ»å°é¾
- æ°æ®å®¡è®¡æ¯æä¸è¶³
- æ°æ®åä½å²çª

**ä¸å¡ç®æ **:
- å»ºç«æ°æ®çæ¬æ§å¶ç³»ç»
- æ¯ææ°æ®å¿«ç§ååæ»?
- æä¾æ°æ®åæ´åå²
- æ¯ææ°æ®åä½ååæ¯ç®¡ç?

### 1.2 ææ¯ç®æ ?

| ææ  | ç®æ å?| è¯´æ |
|------|--------|------|
| **çæ¬å¿«ç§éåº¦** | <10ç§?| æ°æ®å¿«ç§åå»ºéåº¦<10ç§?|
| **çæ¬åæ»éåº¦** | <30ç§?| æ°æ®åæ»éåº¦<30ç§?|
| **çæ¬åå²ä¿ç** | â?å¹?| ä¿çè³å°1å¹´ççæ¬åå² |
| **çæ¬å²çªç?* | <5% | çæ¬å²çªç?5% |

## ä¸ãæ ¸å¿æ¨¡åè®¾è®?

### 3.1 çæ¬ç®¡çå?(VersionManager)

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class VersionStatus(Enum):
    """çæ¬ç¶æ?""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

@dataclass
class DataVersion:
    """æ°æ®çæ¬"""
    version_id: str
    table_name: str
    version_number: int
    commit_message: str
    author: str
    created_at: datetime = field(default_factory=datetime.now)
    status: VersionStatus = VersionStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VersionTag:
    """çæ¬æ ç­¾"""
    tag_name: str
    version_id: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)

class VersionManager:
    """çæ¬ç®¡çå?""
    
    def __init__(self):
        self.versions: Dict[str, DataVersion] = {}
        self.tags: Dict[str, VersionTag] = {}
        self.branches: Dict[str, str] = {"main": "latest"}
    
    def create_version(self, table_name: str, commit_message: str,
                       author: str, metadata: Dict[str, Any] = None) -> DataVersion:
        """åå»ºçæ¬"""
        version_number = self._get_next_version_number(table_name)
        
        version = DataVersion(
            version_id=f"{table_name}_v{version_number}",
            table_name=table_name,
            version_number=version_number,
            commit_message=commit_message,
            author=author,
            metadata=metadata or {}
        )
        
        self.versions[version.version_id] = version
        return version
    
    def _get_next_version_number(self, table_name: str) -> int:
        """è·åä¸ä¸ä¸ªçæ¬å·"""
        table_versions = [v for v in self.versions.values() if v.table_name == table_name]
        
        if not table_versions:
            return 1
        
        return max(v.version_number for v in table_versions) + 1
    
    def create_tag(self, tag_name: str, version_id: str,
                   description: str) -> VersionTag:
        """åå»ºæ ç­¾"""
        tag = VersionTag(
            tag_name=tag_name,
            version_id=version_id,
            description=description
        )
        
        self.tags[tag_name] = tag
        return tag
    
    def get_version(self, version_id: str) -> Optional[DataVersion]:
        """è·åçæ¬"""
        return self.versions.get(version_id)
    
    def get_version_by_tag(self, tag_name: str) -> Optional[DataVersion]:
        """éè¿æ ç­¾è·åçæ¬"""
        tag = self.tags.get(tag_name)
        if not tag:
            return None
        
        return self.versions.get(tag.version_id)
    
    def list_versions(self, table_name: str = None) -> List[DataVersion]:
        """ååºçæ¬"""
        if table_name:
            return [v for v in self.versions.values() if v.table_name == table_name]
        return list(self.versions.values())
```

### 3.2 åæ´è¿½è¸ªå?(ChangeTracker)

```python
from typing import Dict, List, Any, Tuple
import pandas as pd
from datetime import datetime

@dataclass
class DataChange:
    """æ°æ®åæ´"""
    change_id: str
    version_id: str
    change_type: str
    row_count: int
    column_changes: List[str]
    detected_at: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)

class ChangeTracker:
    """åæ´è¿½è¸ªå?""
    
    def __init__(self):
        self.changes: List[DataChange] = []
    
    def detect_changes(self, old_df: pd.DataFrame,
                       new_df: pd.DataFrame) -> DataChange:
        """æ£æµåæ?""
        row_count_change = len(new_df) - len(old_df)
        
        old_columns = set(old_df.columns)
        new_columns = set(new_df.columns)
        
        added_columns = new_columns - old_columns
        removed_columns = old_columns - new_columns
        column_changes = list(added_columns | removed_columns)
        
        if row_count_change > 0:
            change_type = "insert"
        elif row_count_change < 0:
            change_type = "delete"
        else:
            change_type = "update"
        
        return DataChange(
            change_id=f"change_{datetime.now().timestamp()}",
            version_id="",
            change_type=change_type,
            row_count=abs(row_count_change),
            column_changes=column_changes,
            details={
                "added_columns": list(added_columns),
                "removed_columns": list(removed_columns)
            }
        )
    
    def compare_versions(self, version1: DataVersion,
                         version2: DataVersion) -> Dict[str, Any]:
        """å¯¹æ¯çæ¬"""
        df1 = self._load_version_data(version1)
        df2 = self._load_version_data(version2)
        
        change = self.detect_changes(df1, df2)
        
        return {
            "version1": version1.version_id,
            "version2": version2.version_id,
            "change_type": change.change_type,
            "row_count_change": change.row_count,
            "column_changes": change.column_changes,
            "details": change.details
        }
    
    def _load_version_data(self, version: DataVersion) -> pd.DataFrame:
        """å è½½çæ¬æ°æ®"""
        # å®ç°çæ¬æ°æ®å è½½é»è¾
        return pd.DataFrame()
    
    def get_change_history(self, table_name: str,
                           start_time: datetime = None,
                           end_time: datetime = None) -> List[DataChange]:
        """è·ååæ´åå²"""
        filtered_changes = self.changes
        
        if start_time:
            filtered_changes = [c for c in filtered_changes if c.detected_at >= start_time]
        
        if end_time:
            filtered_changes = [c for c in filtered_changes if c.detected_at <= end_time]
        
        return filtered_changes
```

### 3.3 çæ¬åæ»å¼æ (VersionRollbackEngine)

```python
from typing import Dict, Any, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class VersionRollbackEngine:
    """çæ¬åæ»å¼æ"""
    
    def __init__(self, version_manager: VersionManager):
        self.version_manager = version_manager
    
    def rollback_to_version(self, table_name: str,
                            version_id: str) -> bool:
        """åæ»å°æå®çæ?""
        version = self.version_manager.get_version(version_id)
        
        if not version:
            logger.error(f"Version {version_id} not found")
            return False
        
        if version.table_name != table_name:
            logger.error(f"Version {version_id} does not belong to table {table_name}")
            return False
        
        try:
            version_data = self._load_version_data(version)
            
            self._apply_version_data(table_name, version_data)
            
            logger.info(f"Successfully rolled back table {table_name} to version {version_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to rollback to version {version_id}: {e}")
            return False
    
    def rollback_to_tag(self, table_name: str,
                        tag_name: str) -> bool:
        """åæ»å°æå®æ ç­?""
        version = self.version_manager.get_version_by_tag(tag_name)
        
        if not version:
            logger.error(f"Tag {tag_name} not found")
            return False
        
        return self.rollback_to_version(table_name, version.version_id)
    
    def _load_version_data(self, version: DataVersion) -> pd.DataFrame:
        """å è½½çæ¬æ°æ®"""
        # å®ç°çæ¬æ°æ®å è½½é»è¾
        return pd.DataFrame()
    
    def _apply_version_data(self, table_name: str, data: pd.DataFrame):
        """åºç¨çæ¬æ°æ®"""
        # å®ç°çæ¬æ°æ®åºç¨é»è¾
        pass
```

---
## åãæ¥å£è®¾è®?

### 4.1 RESTful API

#### 4.1.1 åå»ºçæ¬

```http
POST /api/v1/version/create
```

**è¯·æ±ç¤ºä¾**:
```json
{
  "table_name": "stock_prices",
  "commit_message": "æ´æ°2026-04-06æ°æ®",
  "author": "data_team"
}
```

#### 4.1.2 åæ»çæ¬

```http
POST /api/v1/version/rollback
```

**è¯·æ±ç¤ºä¾**:
```json
{
  "table_name": "stock_prices",
  "version_id": "stock_prices_v123"
}
```

#### 4.1.3 å¯¹æ¯çæ¬

```http
GET /api/v1/version/compare?version1=stock_prices_v122&version2=stock_prices_v123
```

---

## äºãé¨ç½²æ¶æ?

```yaml
version: '3.8'
services:
  lakefs:
    image: treeverse/lakefs:latest
    ports:
      - "8000:8000"
    environment:
      - LAKEFS_DATABASE_CONNECTION_STRING=postgres://user:pass@postgres:5432/lakefs
      - LAKEFS_AUTH_ENCRYPT_SECRET_KEY=secret
    volumes:
      - lakefs-data:/data
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=lakefs
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - pg-data:/var/lib/postgresql/data

volumes:
  lakefs-data:
  pg-data:
```

---

## å­ãçæ§ææ ?

| ææ åç§° | ææ ç±»å | è¯´æ |
|---------|---------|------|
| `version_total_versions` | Gauge | çæ¬æ»æ° |
| `version_creates_total` | Counter | åå»ºçæ¬æ»æ° |
| `version_rollbacks_total` | Counter | åæ»æ»æ° |
| `version_size_bytes` | Gauge | çæ¬å­å¨å¤§å° |

---

## ä¸ãå®æ½è®¡å?

| é¶æ®µ | ä»»å¡ | é¢è®¡æ¶é´ |
|------|------|---------|
| **é¶æ®µ1** | æ­å»ºLakeFSå¹³å° | 2å¤?|
| **é¶æ®µ2** | å¼åçæ¬ç®¡çå¨ | 3å¤?|
| **é¶æ®µ3** | å¼ååæ´è¿½è¸ªå¨ | 3å¤?|
| **é¶æ®µ4** | å¼ååæ»å¼æ?| 2å¤?|
| **é¶æ®µ5** | æµè¯åä¼å?| 2å¤?|

---

## å«ãç¸å³ææ¡?

- [å®æ¶æ°æ®æ¹èå¾](./REALTIME_DATA_LAKE_BLUEPRINT.md)
- æ°æ®è¡ç¼è¿½è¸ªèå?
- [æ°æ®çå½å¨æç®¡çèå¾](./DATA_LIFECYCLE_MANAGEMENT_BLUEPRINT.md)

---

**ææ¡£çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç»´æ¤è?*: é¦å¸­èå¾æ¶æå¸?
---


---

## ð ç¸å³ææ¡£

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [DATA CATALOG BLUEPRINT](./DATA_CATALOG_BLUEPRINT.md) | DATA_CATALOG_001 | ä¸­ä¾èµ?| è·åæ°æ®èµäº§ä¿¡æ¯ |

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [DATA GOVERNANCE PLATFORM BLUEPRINT](./DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md) | DATA_GOVERNANCE_PLATFORM_001 | ä¸­ä¾èµ?| æä¾çæ¬ç®¡çæ¯æ |

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **DVC** | 3.0+ | æ°æ®çæ¬æ§å¶ | [å®æ¹ææ¡£](https://dvc.org/) |
| **Git** | 2.40+ | çæ¬ç®¡ç | [å®æ¹ææ¡£](https://git-scm.com/) |
| **LakeFS** | 1.0+ | æ°æ®æ¹çæ¬æ§å?| [å®æ¹ææ¡£](https://lakefs.io/) |

### å¼ç¨å³ç³»å?

```mermaid
graph LR
    U0["DATA CATALOG BL"] --> B
    B["DATA VERSION CO"]
    B --> D0["DATA GOVERNANCE"]
    
    style B fill:#ff6b6b
    style U0 fill:#4ecdc4
    style D0 fill:#45b7d1
```

## 1. ææ¡£æ²»ç

### 1.1 System_Manifest.mdç´¢å¼

```markdown
#### Layer 6: ç»åä¼åå±?
##### 6.001. Data Version Control
- **æ¨¡åID**: DATA_VERSION_CONTROL_001
- **èå¾ææ¡£**: DATA_VERSION_CONTROL_BLUEPRINT.md
- **ææ¯è§æ ¼ä¹¦**: å¾åå»?
- **èè´£**: Layer 0æ°æ®æºå± | ä¸å¡æ¶æ: ä¸çº§æ¶é´æ¡æ¶èåæ¶æ
- **ç¶æ?*: Active
```

### 1.2 æ¨¡åèè´£è¾¹ç

| æ¨¡å | èè´£ | è¾¹ç |
|------|------|------|
| **Data Version Control** | Layer 0æ°æ®æºå± | ä¸å¡æ¶æ: ä¸çº§æ¶é´æ¡æ¶èåæ¶æ | **æ ¸å¿æ¨¡å** |

### 1.3 çæ¬ç®¡ç

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-06 | **ç¶æ?*: Active
