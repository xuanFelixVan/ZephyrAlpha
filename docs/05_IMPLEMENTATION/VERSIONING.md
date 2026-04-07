﻿---
module_id: VERSIONING_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 实施指南、部署文档

---
---

---
module_id: DOC_VERSIONING_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: ﻠ۵ﮒﺕ­ﮔﮔ۰۲ﮔﭘﮔ?
responsibility:
  - 因子计算
  - 机器学习
  - 文档治理
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔ۰۲
applicable_scope: ﮒ۷ﻝﺏﭨ?
compliance_level: ﮒﮒ۶ﮔ ﮒ
parent_document: INDEX.md
implementation_status: ﻟﺟﻟ۰?---



# VERSIONING.md - ﻝﮔ؛ﻝ؟۰ﻝﻟ۶ﻟ
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨﻝﮔ؛ﮒﺓﻝ؟۰ﻝﮒﮒﻝﭦ۶ﻟ۶ﮒ


## ﻝﮔ؛ﮒﺓﮔ ﺙ?

```
{ﻛﺕﭨﻝﮔ؛}.{ﮔ؛۰ﻝﮔ؛}.{ﻟ۰۴ﻛﺕﻝﮔ؛}
```

ﻝ۳ﭦﻛﺝ: `4.0.2`


## ﻝﮔ؛ﮒﻝﭦ۶ﻟ۶ﮒ

### ﻛﺕﭨﻝﮔ؛ﮒﻝﭦ۶ﺅﺙv4.0 ?v5.0?

**ﻟ۶۵ﮒﮔ۰ﻛﭨﭘ**:
- ﮔﭘﮔﮔﺗﮒﺅﺙLayer 0-11ﻠﻝﭨ?
- ﮔ ﺕﮒﺟﮔ۷۰ﮒﮔﺟﮔ۱
- ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻛﺕﮒﺙ?
- ﮔ۴ﮒ۲ﻝﮔ؛ﮒﻝﭦ۶ﺅﺙinterface_version: 1.0 ?2.0?

**ﮔﻛﺛ**:
1. ﮔﺑﮔﺍ `System_Manifest.md` ﻛﺕ­ﻝ `version` ﮒ­ﮔ؟ﭖ
2. ﮔﺑﮔﺍ `CONTEXT_SNAPSHOT.json` ﻛﺕ­ﻝ `system_version`
3. ?`CHANGELOG.md` ﻛﺕ­ﻟ؟ﺍﮒﺛﻠﮒ۳۶ﮒ?
4. ﮒ۳ﻛﭨﺛﮔ۶ﻝﮔ؛ﮒﺍ `archives/v4.0/`

**ﻝ۳ﭦﻛﺝ**:
```json
{
  "system_version": "5.0",
  "interface_version": "2.0",
  "breaking_changes": [
    "Layer 0-11ﮔﭘﮔﻠﻝﭨ",
    "ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻛﭨParquetﮔﺗﻛﺕﭦArrow"
  ]
}
```

### ﮔ؛۰ﻝﮔ؛ﮒﻝﭦ۶ﺅﺙv4.0 ?v4.1?

**ﻟ۶۵ﮒﮔ۰ﻛﭨﭘ**:
- ﮔﺍﮒ۱ﮔ۷۰ﮒ
- ﮔﺍﮒ۱ﮒ ﮒ­ﮒﭦﺅﺙ>10ﻛﺕ۹ﮒ ﮒ­ﺅﺙ
- ﮔﺍﮒ۱ﻝ­ﻝ۴?5ﻛﺕ۹ﻝ­ﻝ۴ﺅﺙ
- ﮔﺍﮒ۱ﮒﻟﺛﺅﺙﻛﺕﮒﺛﺎﮒﻝﺍﮔﮔ۴ﮒ۲?

**ﮔﻛﺛ**:
1. ﮔﺑﮔﺍ `System_Manifest.md` ﻛﺕ­ﻝ `version` ﮒ­ﮔ؟ﭖ
2. ﮔﺑﮔﺍ `CONTEXT_SNAPSHOT.json` ﻛﺕ­ﻝ `system_version`
3. ?`CHANGELOG.md` ﻛﺕ­ﻟ؟ﺍﮒﺛﮔﺍﮒ۱ﮒ?
4. ﮔﺑﮔﺍ `02_ALPHA_FACTORS_INDEX.md` ﻛﺕ­ﻝﮒ ﮒ­ﻝﭨﻟ؟۰

**ﻝ۳ﭦﻛﺝ**:
```markdown
## [v4.1] - 2026-04-15

### Added
- ﮔﺍﮒ۱10ﻛﺕ۹ﮒ۷ﻠﮒ ﮒ­ﺅﺙALPHA_065-074?
- ﮔﺍﮒ۱5ﻛﺕ۹ﻝ­ﻝ۴ﺅﺙS010-S014?
- ﮔﺍﮒ۱ﮒﺕﮒﭦﻝﭘﮔﻟﺁﮒ،ﮔ۷۰?
```

### ﻟ۰۴ﻛﺕﻝﮔ؛ﮒﻝﭦ۶ﺅﺙv4.0 ?v4.0.1?

**ﻟ۶۵ﮒﮔ۰ﻛﭨﭘ**:
- Bugﻛﺟ؟ﮒ۳
- ﮔﮔ۰۲ﮔﺑﮔﺍ
- ﮔ۶ﻟﺛﻛﺙﮒ
- ﮒ ﮒ­ﮒﮔﺍﻟﺍﮔﺑ

**ﮔﻛﺛ**:
1. ﮔﺑﮔﺍ `System_Manifest.md` ﻛﺕ­ﻝ `version` ﮒ­ﮔ؟ﭖ
2. ﮔﺑﮔﺍ `CONTEXT_SNAPSHOT.json` ﻛﺕ­ﻝ `system_version`
3. ?`CHANGELOG.md` ﻛﺕ­ﻟ؟ﺍﮒﺛﻛﺟ؟ﮒ۳ﮒ?

**ﻝ۳ﭦﻛﺝ**:
```markdown
## [v4.0.1] - 2026-03-29

### Fixed
- ﻛﺟ؟ﮒ۳MA5ﻟ؟۰ﻝ؟ﻛﺕ­ﻝNaNﮒ۳ﻝ
- ﻛﺟ؟ﮒ۳PE_TTMﮒ ﮒ­ﻝﮔﺍﮔ؟ﮔﭦﻠﻟﺁﺁ

### Changed
- ﻛﺙﮒﮒ ﮒ­ﻟ؟۰ﻝ؟ﮔ۶ﻟﺛﺅﺙﮔ?5%?
```


## ﻝﮔ؛ﮒﺙﮒ؟ﺗﮔ۶ﻟ۶?

| ﻝﮔ؛ﻝﺎﭨﮒ | ﮒﺙﮒ؟ﺗ?| ﻟﺁﺑﮔ |
|---------|--------|------|
| ﻛﺕﭨﻝ?| ?ﻛﺕﮒﺙ?| v4.0 ﻝﮔﺍ?ﮔ۴ﮒ۲ﻛﺕﻟﺛﻝ۷ﻛﭦ v5.0 |
| ﮔ؛۰ﻝ?| ?ﮒﮒﮒﺙﮒ؟ﺗ | v4.0 ﻝﻛﭨ۲ﻝ ﮒﺁﻛﭨ۴ﻝ۷?v4.1 |
| ﻟ۰۴ﻛﺕﻝﮔ؛ | ?ﮒ؟ﮒ۷ﮒﺙﮒ؟ﺗ | v4.0 ?v4.0.1 ﮒ؟ﮒ۷ﮒﺙﮒ؟ﺗ |


## ﻝﮔ؛ﮔ۲ﮔ۴ﮔﭦ?

### ﮒﺁﮒ۷ﮔﭘﮔ۲?

```python
def check_version_compatibility():
    """ﮔ۲ﮔ۴ﻝﺏﭨﻝﭨﻝﮔ؛ﮒﺙﮒ؟?""
    
    # ﻟﺁﭨﮒﮒﺛﮒﻝﮔ؛
    current_version = read_system_version()
    
    # ﻟﺁﭨﮒﮒﺟ،ﻝ۶ﻝﮔ؛
    snapshot_version = read_snapshot_version()
    
    # ﮔ۲ﮔ۴ﮒﺙﮒ؟?
    if current_version.major != snapshot_version.major:
        raise VersionMismatchError(
            f"ﻛﺕﭨﻝﮔ؛ﻛﺕﮒﺗﻠ: {current_version} vs {snapshot_version}"
        )
    
    if current_version.minor < snapshot_version.minor:
        raise VersionMismatchError(
            f"ﮔ؛۰ﻝﮔ؛ﻟﺟ? {current_version} < {snapshot_version}"
        )
```

### ﮔ۴ﮒ۲ﻝﮔ؛ﮒﮒ

```python
def negotiate_interface_version():
    """ﮒﮒﮔ۴ﮒ۲ﻝﮔ؛"""
    
    client_version = "1.0"
    server_version = "1.0"
    
    if client_version == server_version:
        return True
    elif client_version < server_version:
        # ﮒﮒﮒﺙﮒ؟ﺗ
        return True
    else:
        # ﮒ؟۱ﮔﺓﻝ،ﺁﻝﮔ؛ﻟﺟ?
        raise InterfaceVersionError()
```


## ﻝﮔ؛ﮒﮒﺕﮔﭖﻝ۷

### ﻝ؛؛ﻛﺕﮔ­۴ﺅﺙﮒﮒ۳

- [ ] ﮔﺑﮔﺍﮔﮔﻝﮔ؛ﮒﺓﮒ­ﮔ؟ﭖ
- [ ] ﮔﺑﮔﺍ `CHANGELOG.md`
- [ ] ﮔﺑﮔﺍ `System_Manifest.md`
- [ ] ﮔﺑﮔﺍ `CONTEXT_SNAPSHOT.json`

### ﻝ؛؛ﻛﭦﮔ­۴ﺅﺙﻠ۹ﻟﺁ

- [ ] ﻟﺟﻟ۰ﮔﮔﮒﮒﮔﭖ?
- [ ] ﻟﺟﻟ۰ﻠﮔﮔﭖﻟﺁ
- [ ] ﻠ۹ﻟﺁﮒﮒﮒﺙﮒ؟ﺗ?
- [ ] ﻠ۹ﻟﺁﮔ۴ﮒ۲ﻝﮔ؛

### ﻝ؛؛ﻛﺕﮔ­۴ﺅﺙﮒﮒﺕ

- [ ] ﮒﮒﭨﭦGitﮔ ﻝ­ﺝﺅﺙv4.0.2?
- [ ] ﮒ۳ﻛﭨﺛﮔ۶ﻝ?
- [ ] ﮔﺑﮔﺍﮔﮔ۰۲
- [ ] ﮒﮒﺕﮒﮔﺑﮔ۴ﮒﺟ

### ﻝ؛؛ﮒﮔ­۴ﺅﺙﻠ۹ﻟﺁ

- [ ] ﻠ۹ﻟﺁﮔﺍﻝﮔ؛ﮒﺁﮔ­۲ﮒﺕﺕﮒﺁﮒ۷
- [ ] ﻠ۹ﻟﺁﮔﺍﮔ؟ﻟﺟﻝ۶ﭨﮔﮒ
- [ ] ﻠ۹ﻟﺁﮔﮔﮔ۷۰ﮒﮔ­۲ﮒﺕﺕﻟﺟ?


## ﻝﮔ؛ﮒﺓﮒ­ﮔ؟ﭖﻛﺛ?

| ﮔﻛﭨﭘ | ﮒ­ﮔ؟ﭖ | ﮔ ﺙﮒﺙ |
|------|------|------|
| `System_Manifest.md` | `version` | `4.0.2` |
| `CONTEXT_SNAPSHOT.json` | `system_version` | `4.0.2` |
| `CONTEXT_SNAPSHOT.json` | `interface_version` | `1.0` |
| `CHANGELOG.md` | ﮔ ﻠ۱ | `[v4.0.2]` |
| `pyproject.toml` | `version` | `4.0.2` |


## ﻝﮔ؛ﮒﮒﺎ

| ﻝﮔ؛ | ﮒﮒﺕﮔ۴ﮔ | ﻛﺕﭨﻟ۵ﮒﮔﺑ |
|------|---------|---------|
| v4.0.2 | 2026-03-28 | ﮒ؟ﮔﻠﭘﮔ؟ﭖﻛﺕﻛﭦ۳ﻛﭨﺅﺙﻛﺙﮒﮒ ﮒ­ﮒﭦﻝﭨﮔ |
| v4.0.1 | 2026-03-28 | ﮒﮒ۶ﻝﮔ؛ﺅﺙﮒ؟ﮔﻝﺏﭨﻝﭨﮔﭘﮔﻟ؟ﺝ?|
| v4.0 | 2026-03-28 | ﻠ۵ﮔ؛۰ﮒﮒﺕ |


**ﻝﮔ؛**: 1.0 | **ﮔﺑﮔﺍ**: 2026-03-28 | **ﻝ?*: ?ﮔﺑﭨﻟﺓ
