﻿---
module_id: VERSION_MANAGEMENT_GUIDE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟ?standard_type: ﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟﻝﮔ؛ﻝ؟۰ﻝﻟ۶ﻟ?applicable_scope: ﻛﺕ۹ﻛﭦﭦﻠ۰ﺗﻝ؟ﻝﮔ؛ﮔ۶ﮒﭘ
responsibility:
  - 实施指南、部署文档
  - 数据源
  - 文档治理
compliance_level: ﻝ؟ﮒﮔ ﮒ?parent_document: ../README.md
implementation_status: Active---


# ﻝﮔ؛ﻝ؟۰ﻝﻟ۶ﻟﺅﺙﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟﻝﺅﺙ?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容

> **ﻝﮔ؛**: v1.0  
> **ﻠﻝ۷ﮒﺁﺗﻟﺎ۰**: ﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟﻙAIﻝﭨﺑﮔ۳ﻠ۰ﺗﻝ؟  
> **ﮔ ﺕﮒﺟﻝﮒﺟﭖ**: ﻝ؟ﮒﻙﻠ،ﮔﻙﻟ۹ﮒ۷ﮒ  
> **ﮒﺓ۴ﮒﺓ**: Git + ﻟﺁ­ﻛﺗﮒﻝﮔ?
---

## ﻭﺁ **ﻝﮔ؛ﻝ؟۰ﻝﻝ؟ﮔ **

### **ﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟﻝﮔ ﺕﮒﺟﻠﮔﺎ?*

- ﻗ?**ﻝ؟ﮒ?*: ﻛﺕﻠﻟ۵ﮒ۳ﮔﻝﮒ؟۰ﮔﺗﮔﭖﻝ۷
- ﻗ?**ﻠ،ﮔ**: ﻟ۹ﮒ۷ﮒﻝﮔ؛ﻝ؟۰ﻝ?- ﻗ?**ﮔﺕﮔﺍ**: ﻝﮔ؛ﮒﮒﺎﻛﺕﻝ؟ﻛﭦﻝ?- ﻗ?**ﮒﺁﻠ **: Gitﻝﮔ؛ﮔ۶ﮒﭘﻛﺟﻠ

### **ﻛﺕﻠﻟ۵ﻝﮒﮒ؟ﺗ**

- ﻗ?ﮒ۳ﻛﭦﭦﮒﻛﺛﻝﮒ؟۰ﮔﺗﮔﭖﻝ۷?- ﻗ?ﮒ۳ﮔﻝﻝﮔ؛ﮒﻠﮔﭦﮒﭘ
- ﻗ?ﮒﮔﺁﻝ؟۰ﻝﻝ­ﻝ۴ﺅﺙﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻝ۷mainﮒﮔﺁﮒﺏﮒﺁﺅﺙ?- ﻗ?ﻛﭨ۲ﻝ ﮒ؟۰ﮔ۴ﮔﭖﻝ۷

---

## ﻭ **ﻝﮔ؛ﮒﺛﮒﻟ۶ﻟ**

### **ﻟﺁ­ﻛﺗﮒﻝﮔ?*

ﮔ ﺙﮒﺙ: `vMAJOR.MINOR.PATCH`

```
v1.0.0  ﻗ?ﮒﮒ۶ﻝﮔ؛
v1.1.0  ﻗ?ﮔﺍﮒ۱ﮒﻟﺛﺅﺙMINORﺅﺙ?v1.1.1  ﻗ?Bugﻛﺟ؟ﮒ۳ﺅﺙPATCHﺅﺙ?v2.0.0  ﻗ?ﻠﮒ۳۶ﮒﮔﺑﺅﺙMAJORﺅﺙ?```

### **ﻝﮔ؛ﻝﺎﭨﮒﻟﺁﺑﮔ**

| ﻝﮔ؛ﻝﺎﭨﮒ | ﻟﺁﺑﮔ | ﻝ۳ﭦﻛﺝ |
|---------|------|------|
| **MAJOR** | ﻛﺕﮒﺙﮒ؟ﺗﻝAPIﮒﮔﺑ | v1.0.0 ﻗ?v2.0.0 |
| **MINOR** | ﮒﮒﮒﺙﮒ؟ﺗﻝﮒﻟﺛﮔﺍﮒ۱?| v1.0.0 ﻗ?v1.1.0 |
| **PATCH** | ﮒﮒﮒﺙﮒ؟ﺗﻝBugﻛﺟ؟ﮒ۳ | v1.0.0 ﻗ?v1.0.1 |

---

## ﻭ **ﻝﮔ؛ﻝ؟۰ﻝﮔﭖﻝ۷**

### **ﻝ؟ﮒﮔﭖﻝ۷ﺅﺙﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟﺅﺙ**

```
ﮒﺙﮒﮒ؟ﮔ?ﻗ?ﮔﻛﭦ۳Git ﻗ?ﮒﮒﭨﭦﻝﮔ؛ﮔ ﻝ­ﺝ ﻗ?ﮔﺑﮔﺍCHANGELOG ﻗ?ﻝﭨ۶ﻝﭨ­
    ﻗ?         ﻗ?          ﻗ?             ﻗ?          ﻗ?  ﻛﭨ۲ﻝ       commit      git tag      ﻟ؟ﺍﮒﺛﮒﮔﺑ      ﻛﺕﻛﺕﻛﺕ۹ﮒﻟ?```

### **ﻟﺁ۵ﻝﭨﮔ­۴ﻠ۹۳**

#### **Step 1: ﮒﺙﮒﮒ؟ﮔ?*

```bash
# ﻝ۰؟ﻛﺟﻛﭨ۲ﻝ ﮒﺓﺎﮔﭖﻟﺁ?pytest tests/

# ﻝ۰؟ﻛﺟﮔﮔ۰۲ﮒﺓﺎﮔﺑﮔ?# ﮔ۲ﮔ۴ﻝﺕﮒﺏﮔﮔ۰۲ﮔﺁﮒ۵ﻠﻟ۵ﮔﺑﮔ?```

#### **Step 2: ﮔﻛﭦ۳Git**

```bash
# ﮔﺓﭨﮒ ﮔﮔﮒﮔ?git add .

# ﮔﻛﭦ۳ﺅﺙﻛﺛﺟﻝ۷ﻟ۶ﻟﻝﮔﻛﭦ۳ﻛﺟ۰ﮔﺁﺅﺙ?git commit -m "feat: ﮔﺓﭨﮒ ﻝ­ﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒ

- ﮒ؟ﻝﺍBaseStrategyﮒﭦﻝﺎﭨ
- ﮒ؟ﻝﺍStrategyFactoryﮒﺓ۴ﮒ
- ﮒ؟ﻝﺍStrategyRegistryﮔﺏ۷ﮒﻟ۰?- ﮔﺓﭨﮒ ﮒﮒﮔﭖﻟﺁ"

# ﮔ۷ﻠﮒﺍﻟﺟﻝ۷ﻛﭨﮒﭦ
git push origin main
```

#### **Step 3: ﮒﮒﭨﭦﻝﮔ؛ﮔ ﻝ­ﺝ**

```bash
# ﮒﮒﭨﭦﮒﺕ۵ﮔﺏ۷ﻠﻝﮔ ﻝ­ﺝ
git tag -a v1.0.0 -m "ﻝﮔ؛ 1.0.0 - ﻝ­ﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒﮒ؟ﮔ

ﻛﺕﭨﻟ۵ﮒﻟﺛ:
- ﻝ­ﻝ۴ﮒﺓ۴ﮒﮔ ﺕﮒﺟﮒ؟ﻝﺍ
- ﻝ­ﻝ۴ﮔﺏ۷ﮒﻟ۰?- ﻝ­ﻝ۴ﮒ ﻟﺛﺛﮒ?
ﮔﺗﻟﺟ:
- ﮔ۶ﻟﺛﻛﺙﮒ
- ﮔﮔ۰۲ﮒ؟ﮒ

ﻛﺟ؟ﮒ۳:
- ﻛﺟ؟ﮒ۳ﻝ­ﻝ۴ﮒ ﻟﺛﺛBug"

# ﮔ۷ﻠﮔ ﻝ­ﺝﮒﺍﻟﺟﻝ۷
git push origin v1.0.0
```

#### **Step 4: ﮔﺑﮔﺍCHANGELOG**

```bash
# ﻝﺙﻟﺝCHANGELOG.md
# ﮔﺓﭨﮒ ﻝﮔ؛ﮒﮔﺑﻟ؟ﺍﮒﺛ
```

---

## ﻭ **Gitﮔﻛﭦ۳ﻛﺟ۰ﮔﺁﻟ۶ﻟ**

### **ﮔﻛﭦ۳ﻛﺟ۰ﮔﺁﮔ ﺙﮒﺙ**

```
<type>(<scope>): <subject>

<body>

<footer>
```

### **ﮔﻛﭦ۳ﻝﺎﭨﮒ**

| ﻝﺎﭨﮒ | ﻟﺁﺑﮔ | ﻝ۳ﭦﻛﺝ |
|------|------|------|
| **feat** | ﮔﺍﮒﻟ?| feat: ﮔﺓﭨﮒ ﻝ­ﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒ |
| **fix** | Bugﻛﺟ؟ﮒ۳ | fix: ﻛﺟ؟ﮒ۳ﻝ­ﻝ۴ﮒ ﻟﺛﺛﻠﻟﺁﺁ |
| **docs** | ﮔﮔ۰۲ﮔﺑﮔﺍ | docs: ﮔﺑﮔﺍAPIﮔﮔ۰۲ |
| **style** | ﻛﭨ۲ﻝ ﮔ ﺙﮒﺙ | style: ﮔ ﺙﮒﺙﮒﻛﭨ۲ﻝ ?|
| **refactor** | ﻠﮔ | refactor: ﻠﮔﻝ­ﻝ۴ﮔﺏ۷ﮒﻟ۰?|
| **test** | ﮔﭖﻟﺁ | test: ﮔﺓﭨﮒ ﮒﮒﮔﭖﻟﺁ |
| **chore** | ﮔﮒﭨﭦ/ﮒﺓ۴ﮒﺓ | chore: ﮔﺑﮔﺍﻛﺝﻟﭖﮒ?|

### **ﮔﻛﭦ۳ﻛﺟ۰ﮔﺁﻝ۳ﭦﻛﺝ**

```bash
# ﮔﺍﮒﻟ?git commit -m "feat: ﮔﺓﭨﮒ ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﮔ۷۰ﮒ

- ﮒ؟ﻝﺍEventBusﮔ ﺕﮒﺟﻝﺎ?- ﮒ؟ﻝﺍEventHandlerﮒﭦﻝﺎﭨ
- ﮔﺓﭨﮒ ﮒﺙﮔ­۴ﻛﭦﻛﭨﭘﮒﮒ
- ﮔﺓﭨﮒ ﮒﮒﮔﭖﻟﺁ"

# Bugﻛﺟ؟ﮒ۳
git commit -m "fix: ﻛﺟ؟ﮒ۳ﻛﭦﻛﭨﭘﻟ؟۱ﻠﻠﮒ۳ﻠ؟ﻠ۱

ﻠ؟ﻠ۱: ﮒﻛﺕﮒ۳ﻝﮒ۷ﻟ۱،ﻠﮒ۳ﻟ؟۱ﻠ
ﮒﮒ : ﻟ؟۱ﻠﮔﭘﮔ۹ﮔ۲ﮔ۴ﻠﮒ۳?ﻟ۶۲ﮒﺏ: ﮔﺓﭨﮒ ﻠﮒ۳ﮔ۲ﮔ۴ﻠﭨﻟﺝ"

# ﮔﮔ۰۲ﮔﺑﮔﺍ
git commit -m "docs: ﮔﺑﮔﺍﻝ­ﻝ۴ﮒﺓ۴ﮒﻛﺛﺟﻝ۷ﮔﮒ

- ﮔﺓﭨﮒ ﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝ
- ﮔﺓﭨﮒ APIﮔﮔ۰۲
- ﮔﺓﭨﮒ ﮔﻛﺛﺏﮒ؟ﻟﺓ?
```

---

## ﻭﺓﺅﺕ?**ﻝﮔ؛ﮔ ﻝ­ﺝﻟ۶ﻟ**

### **ﮔ ﻝ­ﺝﮒﺛﮒ**

```bash
# ﮔ ﺙﮒﺙ: vMAJOR.MINOR.PATCH
v1.0.0  # ﮔ­۲ﮒﺙﻝﮔ؛
v1.0.0-beta  # ﮔﭖﻟﺁﻝﮔ؛
v1.0.0-rc.1  # ﮒﻠﻝﮔ?```

### **ﮔ ﻝ­ﺝﮔﺏ۷ﻠﮔ۷۰ﮔﺟ**

```bash
git tag -a v1.0.0 -m "ﻝﮔ؛ 1.0.0 - [ﻝﮔ؛ﻛﺕﭨﻠ۱]

ﻛﺕﭨﻟ۵ﮒﻟﺛ:
- ﮒﻟﺛ1
- ﮒﻟﺛ2

ﮔﺗﻟﺟ:
- ﮔﺗﻟﺟ1
- ﮔﺗﻟﺟ2

ﻛﺟ؟ﮒ۳:
- ﻛﺟ؟ﮒ۳1
- ﻛﺟ؟ﮒ۳2

ﮒﺓﺎﻝ۴ﻠ؟ﻠ۱:
- ﻠ؟ﻠ۱1
- ﻠ؟ﻠ۱2"
```

---

## ﻭ **CHANGELOGﻟ۶ﻟ**

### **CHANGELOGﮔ ﺙﮒﺙ**

```markdown
# ﮔﺑﮔﺍﮔ۴ﮒﺟ

ﮔﮔﻠﻟ۵ﻝﮒﮔﺑﻠﺛﮒﺍﻟ؟ﺍﮒﺛﮒ۷ﮔ­۳ﮔﻛﭨﭘﻛﺕ­ﻙ?
ﮔ ﺙﮒﺙﮒﭦﻛﭦ [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)

## [Unreleased]

### ﮔﺍﮒ۱
- ﮒﺝﮒﮒﺕﻝﮔﺍﮒﻟ?
## [1.0.0] - 2026-04-02

### ﮔﺍﮒ۱
- ﻝ­ﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒ
- ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﮔ۷۰ﮒ
- ﮒﮔﭖﮒﺙﮔﻠﮔ

### ﮔﺗﻟﺟ
- ﮔ۶ﻟﺛﻛﺙﮒ
- ﮔﮔ۰۲ﮒ؟ﮒ

### ﻛﺟ؟ﮒ۳
- ﻛﺟ؟ﮒ۳ﻝ­ﻝ۴ﮒ ﻟﺛﺛBug

## [0.1.0] - 2026-04-01

### ﮔﺍﮒ۱
- ﮒﮒ۶ﻠ۰ﺗﻝ؟ﻝﭨﮔ
- ﮒﭦﻝ۰ﻠﻝﺛ؟ﮔﻛﭨﭘ
```

---

## ﻭ ﺅﺕ?**ﻟ۹ﮒ۷ﮒﮒﺓ۴ﮒ?*

### **ﻝﮔ؛ﮒﺓﻟ۹ﮒ۷ﻝﮔﻟﮔ?*

```python
# scripts/auto_version.py

import re
import subprocess
from datetime import datetime

def get_current_version():
    """ﻟﺓﮒﮒﺛﮒﻝﮔ؛ﮒ?""
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except:
        return 'v0.0.0'

def bump_version(current_version, bump_type='patch'):
    """ﮒﻝﭦ۶ﻝﮔ؛ﮒ?""
    # ﮔﮒﻝﮔ؛ﮒ?    match = re.match(r'v(\d+)\.(\d+)\.(\d+)', current_version)
    if not match:
        return 'v0.0.1'
    
    major, minor, patch = map(int, match.groups())
    
    # ﮔ ﺗﮔ؟ﻝﺎﭨﮒﮒﻝﭦ۶
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    return f'v{major}.{minor}.{patch}'

def create_version_tag(version, message):
    """ﮒﮒﭨﭦﻝﮔ؛ﮔ ﻝ­ﺝ"""
    subprocess.run(['git', 'tag', '-a', version, '-m', message])
    print(f"ﻗ?ﮒﮒﭨﭦﻝﮔ؛ﮔ ﻝ­ﺝ: {version}")

if __name__ == '__main__':
    import sys
    
    bump_type = sys.argv[1] if len(sys.argv) > 1 else 'patch'
    
    current = get_current_version()
    new_version = bump_version(current, bump_type)
    
    print(f"ﮒﺛﮒﻝﮔ؛: {current}")
    print(f"ﮔﺍﻝﮔ? {new_version}")
    
    message = input("ﻟﺁﺓﻟﺝﮒ۴ﻝﮔ؛ﻟﺁﺑﮔ? ")
    create_version_tag(new_version, message)
```

**ﻛﺛﺟﻝ۷ﮔﺗﮔﺏ**:

```bash
# ﮒﻝﭦ۶PATCHﻝﮔ؛ﺅﺙBugﻛﺟ؟ﮒ۳ﺅﺙ?python scripts/auto_version.py patch

# ﮒﻝﭦ۶MINORﻝﮔ؛ﺅﺙﮔﺍﮒﻟﺛﺅﺙ?python scripts/auto_version.py minor

# ﮒﻝﭦ۶MAJORﻝﮔ؛ﺅﺙﻠﮒ۳۶ﮒﮔﺑﺅﺙ
python scripts/auto_version.py major
```

---

## ﻭ **ﻝﮔ؛ﮒﮒﺕﮔ۲ﮔ۴ﮔﺕﮒ?*

### **ﮒﮒﺕﮒﮔ۲ﮔ?*

```markdown
## ﻝﮔ؛ﮒﮒﺕﮔ۲ﮔ۴ﮔﺕﮒ?
### ﻛﭨ۲ﻝ ﻟﺑ۷ﻠ
- [ ] ﮔﮔﮔﭖﻟﺁﻠﻟﺟ
- [ ] ﻛﭨ۲ﻝ ﮔ ﻟ­۵ﮒ?- [ ] ﮔﮔ۰۲ﮒﺓﺎﮔﺑﮔ?
### ﻝﮔ؛ﻝ؟۰ﻝ
- [ ] CHANGELOGﮒﺓﺎﮔﺑﮔ?- [ ] ﻝﮔ؛ﮒﺓﮒﺓﺎﮒﻝﭦ۶
- [ ] Gitﮔ ﻝ­ﺝﮒﺓﺎﮒﮒﭨ?
### ﮔﮔ۰۲
- [ ] READMEﮒﺓﺎﮔﺑﮔ?- [ ] APIﮔﮔ۰۲ﮒﺓﺎﮔﺑﮔ?- [ ] ﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝﮒﺓﺎﮔﺓﭨﮒ?```

---

## ﻭﺁ **ﮔﻛﺛﺏﮒ؟ﻟﺓ?*

### **1. ﻠ۱ﻝﺗﮔﻛﭦ۳**

```bash
# ﻗ?ﮒ۴ﺛﻝﮒﮔﺏ - ﮒﺍﮔ­۴ﮔﻛﭦ۳
git commit -m "feat: ﮔﺓﭨﮒ BaseStrategyﮒﭦﻝﺎﭨ"
git commit -m "feat: ﮔﺓﭨﮒ StrategyFactoryﮒﺓ۴ﮒ"
git commit -m "test: ﮔﺓﭨﮒ ﻝ­ﻝ۴ﮒﺓ۴ﮒﮒﮒﮔﭖﻟﺁ"

# ﻗ?ﻛﺕﮒ۴ﺛﻝﮒﮔﺏ?- ﮒ۳۶ﮔ­۴ﮔﻛﭦ۳
git commit -m "feat: ﮒ؟ﮔﻝ­ﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒ"
```

### **2. ﮔﺕﮔﺍﻝﮔﻛﭦ۳ﻛﺟ۰ﮔ?*

```bash
# ﻗ?ﮒ۴ﺛﻝﮒﮔﺏ
git commit -m "feat: ﮔﺓﭨﮒ ﻝ­ﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒ

- ﮒ؟ﻝﺍBaseStrategyﮒﭦﻝﺎﭨ
- ﮒ؟ﻝﺍStrategyFactoryﮒﺓ۴ﮒ
- ﮔﺓﭨﮒ ﮒﮒﮔﭖﻟﺁ"

# ﻗ?ﻛﺕﮒ۴ﺛﻝﮒﮔﺏ?git commit -m "update"
```

### **3. ﮒ؟ﮔﮔ۷ﻠ?*

```bash
# ﮔﺁﮒ۳۸ﻝﭨﮔﮒﮔ۷ﻠ?git push origin main

# ﮒﮒﭨﭦﮔ ﻝ­ﺝﮒﮔ۷ﻠ?git push origin v1.0.0
```

---

## ﻭ **ﮒﻟﻟﭖﮔ?*

### **ﮒﻠ۷ﮔﮔ۰۲**

- [ﻟﮒﺝﮔﺛﮒﺓ۴ﻟﺁﺑﮔﻛﺗ۵](05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/CONSTRUCTION_SPECIFICATION.md)
- [ﮔﮔ۰۲ﻟﺑ۷ﻠﻠ۷ﻝ۵](05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/06_CHECKLISTS/DOCUMENT_QUALITY_GATE.md)

### **ﮒ۳ﻠ۷ﻟﭖﮔﭦ**

- [ﻟﺁ­ﻛﺗﮒﻝﮔ؛](https://semver.org/lang/zh-CN/)
- [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)
- [Gitﮒ؟ﮔﺗﮔﮔ۰۲](https://git-scm.com/doc)

---

## ﻭ **ﮔﺑﮔﺍﻟ؟ﺍﮒﺛ**

| ﮔ۴ﮔ | ﻝﮔ؛ | ﮔﺑﮔﺍﮒﮒ؟ﺗ | ﮔﺑﮔﺍﻛﭦ?|
|------|------|---------|--------|
| 2026-04-02 | v1.0 | ﮒﮒﭨﭦﻝﮔ؛ﻝ؟۰ﻝﻟ۶ﻟ | ﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟ?|

---

## ﻭ **ﻟﻝﺏﭨﮔﺗﮒﺙ**

**ﮔﮔ۰۲ﻝﭨﺑﮔ۳ﻟ?*: ﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟ? 
**ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02  
**ﮔﮒﮔﺑﮔ?*: 2026-04-02  
**ﻝﮔ؛**: v1.0
