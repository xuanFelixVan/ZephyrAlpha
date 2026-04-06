---
module_id: DOC_VERSIONING_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: ﻠ۵ﮒﺕ­ﮔﮔ۰۲ﮔﭘﮔ?
responsibility:
  - 因子计算
  - 机器学习
  - 文档治理
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔ۰۲
applicable_scope: ﮒ۷ﻝﺏﭨ?
compliance_level: ﮒﮒ۶ﮔ ﮒ
parent_document: INDEX.md
implementation_status: ﻟﺟﻟ۰?---



# VERSIONING.md - ﻝﮔ؛ﻝ؟۰ﻝﻟ۶ﻟ

> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨﻝﮔ؛ﮒﺓﻝ؟۰ﻝﮒﮒﻝﭦ۶ﻟ۶ﮒ


## ﻝﮔ؛ﮒﺓﮔ ﺙ?

```
{ﻛﺕﭨﻝﮔ؛}.{ﮔ؛۰ﻝﮔ؛}.{ﻟ۰۴ﻛﺕﻝﮔ؛}
```

ﻝ۳ﭦﻛﺝ: `4.0.2`


## ﻝﮔ؛ﮒﻝﭦ۶ﻟ۶ﮒ

### ﻛﺕﭨﻝﮔ؛ﮒﻝﭦ۶ﺅﺙv4.0 ?v5.0?

**ﻟ۶۵ﮒﮔ۰ﻛﭨﭘ**:
- ﮔﭘﮔﮔﺗﮒﺅﺙLayer 0-11ﻠﻝﭨ?
- ﮔ ﺕﮒﺟﮔ۷۰ﮒﮔﺟﮔ۱
- ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻛﺕﮒﺙ?
- ﮔ۴ﮒ۲ﻝﮔ؛ﮒﻝﭦ۶ﺅﺙinterface_version: 1.0 ?2.0?

**ﮔﻛﺛ**:
1. ﮔﺑﮔﺍ `System_Manifest.md` ﻛﺕ­ﻝ `version` ﮒ­ﮔ؟ﭖ
2. ﮔﺑﮔﺍ `CONTEXT_SNAPSHOT.json` ﻛﺕ­ﻝ `system_version`
3. ?`CHANGELOG.md` ﻛﺕ­ﻟ؟ﺍﮒﺛﻠﮒ۳۶ﮒ?
4. ﮒ۳ﻛﭨﺛﮔ۶ﻝﮔ؛ﮒﺍ `archives/v4.0/`

**ﻝ۳ﭦﻛﺝ**:
```json
{
  "system_version": "5.0",
  "interface_version": "2.0",
  "breaking_changes": [
    "Layer 0-11ﮔﭘﮔﻠﻝﭨ",
    "ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻛﭨParquetﮔﺗﻛﺕﭦArrow"
  ]
}
```

### ﮔ؛۰ﻝﮔ؛ﮒﻝﭦ۶ﺅﺙv4.0 ?v4.1?

**ﻟ۶۵ﮒﮔ۰ﻛﭨﭘ**:
- ﮔﺍﮒ۱ﮔ۷۰ﮒ
- ﮔﺍﮒ۱ﮒ ﮒ­ﮒﭦﺅﺙ>10ﻛﺕ۹ﮒ ﮒ­ﺅﺙ
- ﮔﺍﮒ۱ﻝ­ﻝ۴?5ﻛﺕ۹ﻝ­ﻝ۴ﺅﺙ
- ﮔﺍﮒ۱ﮒﻟﺛﺅﺙﻛﺕﮒﺛﺎﮒﻝﺍﮔﮔ۴ﮒ۲?

**ﮔﻛﺛ**:
1. ﮔﺑﮔﺍ `System_Manifest.md` ﻛﺕ­ﻝ `version` ﮒ­ﮔ؟ﭖ
2. ﮔﺑﮔﺍ `CONTEXT_SNAPSHOT.json` ﻛﺕ­ﻝ `system_version`
3. ?`CHANGELOG.md` ﻛﺕ­ﻟ؟ﺍﮒﺛﮔﺍﮒ۱ﮒ?
4. ﮔﺑﮔﺍ `02_ALPHA_FACTORS_INDEX.md` ﻛﺕ­ﻝﮒ ﮒ­ﻝﭨﻟ؟۰

**ﻝ۳ﭦﻛﺝ**:
```markdown
## [v4.1] - 2026-04-15

### Added
- ﮔﺍﮒ۱10ﻛﺕ۹ﮒ۷ﻠﮒ ﮒ­ﺅﺙALPHA_065-074?
- ﮔﺍﮒ۱5ﻛﺕ۹ﻝ­ﻝ۴ﺅﺙS010-S014?
- ﮔﺍﮒ۱ﮒﺕﮒﭦﻝﭘﮔﻟﺁﮒ،ﮔ۷۰?
```

### ﻟ۰۴ﻛﺕﻝﮔ؛ﮒﻝﭦ۶ﺅﺙv4.0 ?v4.0.1?

**ﻟ۶۵ﮒﮔ۰ﻛﭨﭘ**:
- Bugﻛﺟ؟ﮒ۳
- ﮔﮔ۰۲ﮔﺑﮔﺍ
- ﮔ۶ﻟﺛﻛﺙﮒ
- ﮒ ﮒ­ﮒﮔﺍﻟﺍﮔﺑ

**ﮔﻛﺛ**:
1. ﮔﺑﮔﺍ `System_Manifest.md` ﻛﺕ­ﻝ `version` ﮒ­ﮔ؟ﭖ
2. ﮔﺑﮔﺍ `CONTEXT_SNAPSHOT.json` ﻛﺕ­ﻝ `system_version`
3. ?`CHANGELOG.md` ﻛﺕ­ﻟ؟ﺍﮒﺛﻛﺟ؟ﮒ۳ﮒ?

**ﻝ۳ﭦﻛﺝ**:
```markdown
## [v4.0.1] - 2026-03-29

### Fixed
- ﻛﺟ؟ﮒ۳MA5ﻟ؟۰ﻝ؟ﻛﺕ­ﻝNaNﮒ۳ﻝ
- ﻛﺟ؟ﮒ۳PE_TTMﮒ ﮒ­ﻝﮔﺍﮔ؟ﮔﭦﻠﻟﺁﺁ

### Changed
- ﻛﺙﮒﮒ ﮒ­ﻟ؟۰ﻝ؟ﮔ۶ﻟﺛﺅﺙﮔ?5%?
```


## ﻝﮔ؛ﮒﺙﮒ؟ﺗﮔ۶ﻟ۶?

| ﻝﮔ؛ﻝﺎﭨﮒ | ﮒﺙﮒ؟ﺗ?| ﻟﺁﺑﮔ |
|---------|--------|------|
| ﻛﺕﭨﻝ?| ?ﻛﺕﮒﺙ?| v4.0 ﻝﮔﺍ?ﮔ۴ﮒ۲ﻛﺕﻟﺛﻝ۷ﻛﭦ v5.0 |
| ﮔ؛۰ﻝ?| ?ﮒﮒﮒﺙﮒ؟ﺗ | v4.0 ﻝﻛﭨ۲ﻝ ﮒﺁﻛﭨ۴ﻝ۷?v4.1 |
| ﻟ۰۴ﻛﺕﻝﮔ؛ | ?ﮒ؟ﮒ۷ﮒﺙﮒ؟ﺗ | v4.0 ?v4.0.1 ﮒ؟ﮒ۷ﮒﺙﮒ؟ﺗ |


## ﻝﮔ؛ﮔ۲ﮔ۴ﮔﭦ?

### ﮒﺁﮒ۷ﮔﭘﮔ۲?

```python
def check_version_compatibility():
    """ﮔ۲ﮔ۴ﻝﺏﭨﻝﭨﻝﮔ؛ﮒﺙﮒ؟?""
    
    # ﻟﺁﭨﮒﮒﺛﮒﻝﮔ؛
    current_version = read_system_version()
    
    # ﻟﺁﭨﮒﮒﺟ،ﻝ۶ﻝﮔ؛
    snapshot_version = read_snapshot_version()
    
    # ﮔ۲ﮔ۴ﮒﺙﮒ؟?
    if current_version.major != snapshot_version.major:
        raise VersionMismatchError(
            f"ﻛﺕﭨﻝﮔ؛ﻛﺕﮒﺗﻠ: {current_version} vs {snapshot_version}"
        )
    
    if current_version.minor < snapshot_version.minor:
        raise VersionMismatchError(
            f"ﮔ؛۰ﻝﮔ؛ﻟﺟ? {current_version} < {snapshot_version}"
        )
```

### ﮔ۴ﮒ۲ﻝﮔ؛ﮒﮒ

```python
def negotiate_interface_version():
    """ﮒﮒﮔ۴ﮒ۲ﻝﮔ؛"""
    
    client_version = "1.0"
    server_version = "1.0"
    
    if client_version == server_version:
        return True
    elif client_version < server_version:
        # ﮒﮒﮒﺙﮒ؟ﺗ
        return True
    else:
        # ﮒ؟۱ﮔﺓﻝ،ﺁﻝﮔ؛ﻟﺟ?
        raise InterfaceVersionError()
```


## ﻝﮔ؛ﮒﮒﺕﮔﭖﻝ۷

### ﻝ؛؛ﻛﺕﮔ­۴ﺅﺙﮒﮒ۳

- [ ] ﮔﺑﮔﺍﮔﮔﻝﮔ؛ﮒﺓﮒ­ﮔ؟ﭖ
- [ ] ﮔﺑﮔﺍ `CHANGELOG.md`
- [ ] ﮔﺑﮔﺍ `System_Manifest.md`
- [ ] ﮔﺑﮔﺍ `CONTEXT_SNAPSHOT.json`

### ﻝ؛؛ﻛﭦﮔ­۴ﺅﺙﻠ۹ﻟﺁ

- [ ] ﻟﺟﻟ۰ﮔﮔﮒﮒﮔﭖ?
- [ ] ﻟﺟﻟ۰ﻠﮔﮔﭖﻟﺁ
- [ ] ﻠ۹ﻟﺁﮒﮒﮒﺙﮒ؟ﺗ?
- [ ] ﻠ۹ﻟﺁﮔ۴ﮒ۲ﻝﮔ؛

### ﻝ؛؛ﻛﺕﮔ­۴ﺅﺙﮒﮒﺕ

- [ ] ﮒﮒﭨﭦGitﮔ ﻝ­ﺝﺅﺙv4.0.2?
- [ ] ﮒ۳ﻛﭨﺛﮔ۶ﻝ?
- [ ] ﮔﺑﮔﺍﮔﮔ۰۲
- [ ] ﮒﮒﺕﮒﮔﺑﮔ۴ﮒﺟ

### ﻝ؛؛ﮒﮔ­۴ﺅﺙﻠ۹ﻟﺁ

- [ ] ﻠ۹ﻟﺁﮔﺍﻝﮔ؛ﮒﺁﮔ­۲ﮒﺕﺕﮒﺁﮒ۷
- [ ] ﻠ۹ﻟﺁﮔﺍﮔ؟ﻟﺟﻝ۶ﭨﮔﮒ
- [ ] ﻠ۹ﻟﺁﮔﮔﮔ۷۰ﮒﮔ­۲ﮒﺕﺕﻟﺟ?


## ﻝﮔ؛ﮒﺓﮒ­ﮔ؟ﭖﻛﺛ?

| ﮔﻛﭨﭘ | ﮒ­ﮔ؟ﭖ | ﮔ ﺙﮒﺙ |
|------|------|------|
| `System_Manifest.md` | `version` | `4.0.2` |
| `CONTEXT_SNAPSHOT.json` | `system_version` | `4.0.2` |
| `CONTEXT_SNAPSHOT.json` | `interface_version` | `1.0` |
| `CHANGELOG.md` | ﮔ ﻠ۱ | `[v4.0.2]` |
| `pyproject.toml` | `version` | `4.0.2` |


## ﻝﮔ؛ﮒﮒﺎ

| ﻝﮔ؛ | ﮒﮒﺕﮔ۴ﮔ | ﻛﺕﭨﻟ۵ﮒﮔﺑ |
|------|---------|---------|
| v4.0.2 | 2026-03-28 | ﮒ؟ﮔﻠﭘﮔ؟ﭖﻛﺕﻛﭦ۳ﻛﭨﺅﺙﻛﺙﮒﮒ ﮒ­ﮒﭦﻝﭨﮔ |
| v4.0.1 | 2026-03-28 | ﮒﮒ۶ﻝﮔ؛ﺅﺙﮒ؟ﮔﻝﺏﭨﻝﭨﮔﭘﮔﻟ؟ﺝ?|
| v4.0 | 2026-03-28 | ﻠ۵ﮔ؛۰ﮒﮒﺕ |


**ﻝﮔ؛**: 1.0 | **ﮔﺑﮔﺍ**: 2026-03-28 | **ﻝ?*: ?ﮔﺑﭨﻟﺓ
