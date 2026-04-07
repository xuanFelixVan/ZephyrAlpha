---
module_id: VERSION_MANAGEMENT_GUIDE
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - VERSION_MANAGEMENT操作指南
---

﻿---
module_id: VERSION_MANAGEMENT_GUIDE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟ?standard_type: ﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟﻝﮔ؛ﻝ؟۰ﻝﻟ۶ﻟ?applicable_scope: ﻛﺕ۹ﻛﭦﭦﻠ۰ﺗﻝ؟ﻝﮔ؛ﮔ۶ﮒﭘ
responsibility:
  - 操作指南编写与使用说明与系统维护管理
compliance_level: ﻝ؟ﮒﮔﮒ?parent_document: ../README.md
implementation_status: Active---


# ﻝﮔ؛ﻝ؟۰ﻝﻟ۶ﻟﺅﺙﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟﻝﺅﺙ?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容

> **ﻝﮔ؛**: v1.0  
> **ﻠﻝ۷ﮒﺁﺗﻟﺎ۰**: ﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟﻙAIﻝﭨﺑﮔ۳ﻠ۰ﺗﻝ؟  
> **ﮔﺕﮒﺟﻝﮒﺟﭖ**: ﻝ؟ﮒﻙﻠ،ﮔﻙﻟ۹ﮒ۷ﮒ
> **ﮒﺓ۴ﮒﺓ**: Git + ﻟﺁﻛﺗﮒﻝﮔ?
---

## ﻭﺁ **ﻝﮔ؛ﻝ؟۰ﻝﻝ؟ﮔ**

### **ﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻟﻝﮔﺕﮒﺟﻠﮔﺎ?*

- ﻗ?**ﻝ؟ﮒ?*: ﻛﺕﻠﻟ۵ﮒ۳ﮔﻝﮒ؟۰ﮔﺗﮔﭖﻝ۷
- ﻗ?**ﻠ،ﮔ**: ﻟ۹ﮒ۷ﮒﻝﮔ؛ﻝ؟۰ﻝ?- ﻗ?**ﮔﺕﮔﺍ**: ﻝﮔ؛ﮒﮒﺎﻛﺕﻝ؟ﻛﭦﻝ?- ﻗ?**ﮒﺁﻠ**: Gitﻝﮔ؛ﮔ۶ﮒﭘﻛﺟﻠ

### **ﻛﺕﻠﻟ۵ﻝﮒﮒ؟ﺗ**

- ﻗ?ﮒ۳ﻛﭦﭦﮒﻛﺛﻝﮒ؟۰ﮔﺗﮔﭖﻝ۷?- ﻗ?ﮒ۳ﮔﻝﻝﮔ؛ﮒﻠﮔﭦﮒﭘ
- ﻗ?ﮒﮔﺁﻝ؟۰ﻝﻝﻝ۴ﺅﺙﻛﺕ۹ﻛﭦﭦﮒﺙﮒﻝ۷mainﮒﮔﺁﮒﺏﮒﺁﺅﺙ?- ﻗ?ﻛﭨ۲ﻝﮒ؟۰ﮔ۴ﮔﭖﻝ۷

---

## ﻭ **ﻝﮔ؛ﮒﺛﮒﻟ۶ﻟ**

### **ﻟﺁﻛﺗﮒﻝﮔ?*

ﮔﺙﮒﺙ: `vMAJOR.MINOR.PATCH`

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
ﮒﺙﮒﮒ؟ﮔ?ﻗ?ﮔﻛﭦ۳Git ﻗ?ﮒﮒﭨﭦﻝﮔ؛ﮔﻝﺝ ﻗ?ﮔﺑﮔﺍCHANGELOG ﻗ?ﻝﭨ۶ﻝﭨ
ﻗ?         ﻗ?          ﻗ?             ﻗ?          ﻗ?  ﻛﭨ۲ﻝ      commit      git tag      ﻟ؟ﺍﮒﺛﮒﮔﺑ      ﻛﺕﻛﺕﻛﺕ۹ﮒﻟ?```

### **ﻟﺁ۵ﻝﭨﮔ۴ﻠ۹۳**

#### **Step 1: ﮒﺙﮒﮒ؟ﮔ?*

```bash
# ﻝ۰؟ﻛﺟﻛﭨ۲ﻝﮒﺓﺎﮔﭖﻟﺁ?pytest tests/

# ﻝ۰؟ﻛﺟﮔﮔ۰۲ﮒﺓﺎﮔﺑﮔ?# ﮔ۲ﮔ۴ﻝﺕﮒﺏﮔﮔ۰۲ﮔﺁﮒ۵ﻠﻟ۵ﮔﺑﮔ?```

#### **Step 2: ﮔﻛﭦ۳Git**

```bash
# ﮔﺓﭨﮒﮔﮔﮒﮔ?git add .

# ﮔﻛﭦ۳ﺅﺙﻛﺛﺟﻝ۷ﻟ۶ﻟﻝﮔﻛﭦ۳ﻛﺟ۰ﮔﺁﺅﺙ?git commit -m "feat: ﮔﺓﭨﮒﻝﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒ

- ﮒ؟ﻝﺍBaseStrategyﮒﭦﻝﺎﭨ
- ﮒ؟ﻝﺍStrategyFactoryﮒﺓ۴ﮒ
- ﮒ؟ﻝﺍStrategyRegistryﮔﺏ۷ﮒﻟ۰?- ﮔﺓﭨﮒﮒﮒﮔﭖﻟﺁ"

# ﮔ۷ﻠﮒﺍﻟﺟﻝ۷ﻛﭨﮒﭦ
git push origin main
```

#### **Step 3: ﮒﮒﭨﭦﻝﮔ؛ﮔﻝﺝ**

```bash
# ﮒﮒﭨﭦﮒﺕ۵ﮔﺏ۷ﻠﻝﮔﻝﺝ
git tag -a v1.0.0 -m "ﻝﮔ؛ 1.0.0 - ﻝﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒﮒ؟ﮔ

ﻛﺕﭨﻟ۵ﮒﻟﺛ:
- ﻝﻝ۴ﮒﺓ۴ﮒﮔﺕﮒﺟﮒ؟ﻝﺍ
- ﻝﻝ۴ﮔﺏ۷ﮒﻟ۰?- ﻝﻝ۴ﮒﻟﺛﺛﮒ?
ﮔﺗﻟﺟ:
- ﮔ۶ﻟﺛﻛﺙﮒ
- ﮔﮔ۰۲ﮒ؟ﮒ

ﻛﺟ؟ﮒ۳:
- ﻛﺟ؟ﮒ۳ﻝﻝ۴ﮒﻟﺛﺛBug"

# ﮔ۷ﻠﮔﻝﺝﮒﺍﻟﺟﻝ۷
git push origin v1.0.0
```

#### **Step 4: ﮔﺑﮔﺍCHANGELOG**

```bash
# ﻝﺙﻟﺝCHANGELOG.md
# ﮔﺓﭨﮒﻝﮔ؛ﮒﮔﺑﻟ؟ﺍﮒﺛ
```

---

## ﻭ **Gitﮔﻛﭦ۳ﻛﺟ۰ﮔﺁﻟ۶ﻟ**

### **ﮔﻛﭦ۳ﻛﺟ۰ﮔﺁﮔﺙﮒﺙ**

```
<type>(<scope>): <subject>

<body>

<footer>
```

### **ﮔﻛﭦ۳ﻝﺎﭨﮒ**

| ﻝﺎﭨﮒ | ﻟﺁﺑﮔ | ﻝ۳ﭦﻛﺝ |
|------|------|------|
| **feat** | ﮔﺍﮒﻟ?| feat: ﮔﺓﭨﮒﻝﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒ |
| **fix** | Bugﻛﺟ؟ﮒ۳ | fix: ﻛﺟ؟ﮒ۳ﻝﻝ۴ﮒﻟﺛﺛﻠﻟﺁﺁ |
| **docs** | ﮔﮔ۰۲ﮔﺑﮔﺍ | docs: ﮔﺑﮔﺍAPIﮔﮔ۰۲ |
| **style** | ﻛﭨ۲ﻝﮔﺙﮒﺙ | style: ﮔﺙﮒﺙﮒﻛﭨ۲ﻝ?|
| **refactor** | ﻠﮔ | refactor: ﻠﮔﻝﻝ۴ﮔﺏ۷ﮒﻟ۰?|
| **test** | ﮔﭖﻟﺁ | test: ﮔﺓﭨﮒﮒﮒﮔﭖﻟﺁ |
| **chore** | ﮔﮒﭨﭦ/ﮒﺓ۴ﮒﺓ | chore: ﮔﺑﮔﺍﻛﺝﻟﭖﮒ?|

### **ﮔﻛﭦ۳ﻛﺟ۰ﮔﺁﻝ۳ﭦﻛﺝ**

```bash
# ﮔﺍﮒﻟ?git commit -m "feat: ﮔﺓﭨﮒﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﮔ۷۰ﮒ

- ﮒ؟ﻝﺍEventBusﮔﺕﮒﺟﻝﺎ?- ﮒ؟ﻝﺍEventHandlerﮒﭦﻝﺎﭨ
- ﮔﺓﭨﮒﮒﺙﮔ۴ﻛﭦﻛﭨﭘﮒﮒ
- ﮔﺓﭨﮒﮒﮒﮔﭖﻟﺁ"

# Bugﻛﺟ؟ﮒ۳
git commit -m "fix: ﻛﺟ؟ﮒ۳ﻛﭦﻛﭨﭘﻟ؟۱ﻠﻠﮒ۳ﻠ؟ﻠ۱

ﻠ؟ﻠ۱: ﮒﻛﺕﮒ۳ﻝﮒ۷ﻟ۱،ﻠﮒ۳ﻟ؟۱ﻠ
ﮒﮒ: ﻟ؟۱ﻠﮔﭘﮔ۹ﮔ۲ﮔ۴ﻠﮒ۳?ﻟ۶۲ﮒﺏ: ﮔﺓﭨﮒﻠﮒ۳ﮔ۲ﮔ۴ﻠﭨﻟﺝ"

# ﮔﮔ۰۲ﮔﺑﮔﺍ
git commit -m "docs: ﮔﺑﮔﺍﻝﻝ۴ﮒﺓ۴ﮒﻛﺛﺟﻝ۷ﮔﮒ

- ﮔﺓﭨﮒﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝ
- ﮔﺓﭨﮒAPIﮔﮔ۰۲
- ﮔﺓﭨﮒﮔﻛﺛﺏﮒ؟ﻟﺓ?
```

---

## ﻭﺓﺅﺕ?**ﻝﮔ؛ﮔﻝﺝﻟ۶ﻟ**

### **ﮔﻝﺝﮒﺛﮒ**

```bash
# ﮔﺙﮒﺙ: vMAJOR.MINOR.PATCH
v1.0.0  # ﮔ۲ﮒﺙﻝﮔ؛
v1.0.0-beta  # ﮔﭖﻟﺁﻝﮔ؛
v1.0.0-rc.1  # ﮒﻠﻝﮔ?```

### **ﮔﻝﺝﮔﺏ۷ﻠﮔ۷۰ﮔﺟ**

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

### **CHANGELOGﮔﺙﮒﺙ**

```markdown
# ﮔﺑﮔﺍﮔ۴ﮒﺟ

ﮔﮔﻠﻟ۵ﻝﮒﮔﺑﻠﺛﮒﺍﻟ؟ﺍﮒﺛﮒ۷ﮔ۳ﮔﻛﭨﭘﻛﺕﻙ?
ﮔﺙﮒﺙﮒﭦﻛﭦ [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)

## [Unreleased]

### ﮔﺍﮒ۱
- ﮒﺝﮒﮒﺕﻝﮔﺍﮒﻟ?
## [1.0.0] - 2026-04-02

### ﮔﺍﮒ۱
- ﻝﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒ
- ﻛﭦﻛﭨﭘﮔﭨﻝﭦﺟﮔ۷۰ﮒ
- ﮒﮔﭖﮒﺙﮔﻠﮔ

### ﮔﺗﻟﺟ
- ﮔ۶ﻟﺛﻛﺙﮒ
- ﮔﮔ۰۲ﮒ؟ﮒ

### ﻛﺟ؟ﮒ۳
- ﻛﺟ؟ﮒ۳ﻝﻝ۴ﮒﻟﺛﺛBug

## [0.1.0] - 2026-04-01

### ﮔﺍﮒ۱
- ﮒﮒ۶ﻠ۰ﺗﻝ؟ﻝﭨﮔ
- ﮒﭦﻝ۰ﻠﻝﺛ؟ﮔﻛﭨﭘ
```

---

## ﻭﺅﺕ?**ﻟ۹ﮒ۷ﮒﮒﺓ۴ﮒ?*

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
    
# ﮔﺗﮔ؟ﻝﺎﭨﮒﮒﻝﭦ۶
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
"""ﮒﮒﭨﭦﻝﮔ؛ﮔﻝﺝ"""
    subprocess.run(['git', 'tag', '-a', version, '-m', message])
print(f"ﻗ?ﮒﮒﭨﭦﻝﮔ؛ﮔﻝﺝ: {version}")

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
### ﻛﭨ۲ﻝﻟﺑ۷ﻠ
- [ ] ﮔﮔﮔﭖﻟﺁﻠﻟﺟ
- [ ] ﻛﭨ۲ﻝﮔﻟ۵ﮒ?- [ ] ﮔﮔ۰۲ﮒﺓﺎﮔﺑﮔ?
### ﻝﮔ؛ﻝ؟۰ﻝ
- [ ] CHANGELOGﮒﺓﺎﮔﺑﮔ?- [ ] ﻝﮔ؛ﮒﺓﮒﺓﺎﮒﻝﭦ۶
- [ ] Gitﮔﻝﺝﮒﺓﺎﮒﮒﭨ?
### ﮔﮔ۰۲
- [ ] READMEﮒﺓﺎﮔﺑﮔ?- [ ] APIﮔﮔ۰۲ﮒﺓﺎﮔﺑﮔ?- [ ] ﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝﮒﺓﺎﮔﺓﭨﮒ?```

---

## ﻭﺁ **ﮔﻛﺛﺏﮒ؟ﻟﺓ?*

### **1. ﻠ۱ﻝﺗﮔﻛﭦ۳**

```bash
# ﻗ?ﮒ۴ﺛﻝﮒﮔﺏ - ﮒﺍﮔ۴ﮔﻛﭦ۳
git commit -m "feat: ﮔﺓﭨﮒBaseStrategyﮒﭦﻝﺎﭨ"
git commit -m "feat: ﮔﺓﭨﮒStrategyFactoryﮒﺓ۴ﮒ"
git commit -m "test: ﮔﺓﭨﮒﻝﻝ۴ﮒﺓ۴ﮒﮒﮒﮔﭖﻟﺁ"

# ﻗ?ﻛﺕﮒ۴ﺛﻝﮒﮔﺏ?- ﮒ۳۶ﮔ۴ﮔﻛﭦ۳
git commit -m "feat: ﮒ؟ﮔﻝﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒ"
```

### **2. ﮔﺕﮔﺍﻝﮔﻛﭦ۳ﻛﺟ۰ﮔ?*

```bash
# ﻗ?ﮒ۴ﺛﻝﮒﮔﺏ
git commit -m "feat: ﮔﺓﭨﮒﻝﻝ۴ﮒﺓ۴ﮒﮔ۷۰ﮒ

- ﮒ؟ﻝﺍBaseStrategyﮒﭦﻝﺎﭨ
- ﮒ؟ﻝﺍStrategyFactoryﮒﺓ۴ﮒ
- ﮔﺓﭨﮒﮒﮒﮔﭖﻟﺁ"

# ﻗ?ﻛﺕﮒ۴ﺛﻝﮒﮔﺏ?git commit -m "update"
```

### **3. ﮒ؟ﮔﮔ۷ﻠ?*

```bash
# ﮔﺁﮒ۳۸ﻝﭨﮔﮒﮔ۷ﻠ?git push origin main

# ﮒﮒﭨﭦﮔﻝﺝﮒﮔ۷ﻠ?git push origin v1.0.0
```

---

## ﻭ **ﮒﻟﻟﭖﮔ?*

### **ﮒﻠ۷ﮔﮔ۰۲**

- ﻟﮒﺝﮔﺛﮒﺓ۴ﻟﺁﺑﮔﻛﺗ۵
- ﮔﮔ۰۲ﻟﺑ۷ﻠﻠ۷ﻝ۵

### **ﮒ۳ﻠ۷ﻟﭖﮔﭦ**

- [ﻟﺁﻛﺗﮒﻝﮔ؛](https://semver.org/lang/zh-CN/)
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
