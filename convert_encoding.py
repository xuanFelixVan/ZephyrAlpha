import subprocess
import re

file_path = r'D:\ZephyrAlpha\docs\01_FRAMEWORK\HUMAN_AI_INTERACTION_BLUEPRINT.md'

result = subprocess.run(['git', 'show', 'HEAD:docs/01_FRAMEWORK/HUMAN_AI_INTERACTION_BLUEPRINT.md'], 
                       capture_output=True)

if result.returncode != 0:
    print(f"Git show failed: {result.stderr.decode('utf-8', errors='replace')}")
    exit(1)

raw_bytes = result.stdout

print(f"Raw bytes length: {len(raw_bytes)}")
print(f"First 10 bytes: {raw_bytes[:10]}")

if raw_bytes.startswith(b'\xff\xfe'):
    encoding = 'utf-16-le'
    print("Detected UTF-16-LE encoding")
elif raw_bytes.startswith(b'\xfe\xff'):
    encoding = 'utf-16-be'
    print("Detected UTF-16-BE encoding")
else:
    encoding = 'utf-8'
    print("Assuming UTF-8 encoding")

try:
    content = raw_bytes.decode(encoding)
    print(f"Successfully decoded with {encoding}, length: {len(content)}")
except Exception as e:
    print(f"Failed to decode with {encoding}: {e}")
    content = raw_bytes.decode('utf-8', errors='replace')
    print(f"Used replacement, length: {len(content)}")

print(f"\nFirst 200 characters:")
print(content[:200])

new_section = '''---

## 🛡️ 二、AI治理框架（引用）

> **详细内容请参考**: [AI治理框架蓝图](./AI_GOVERNANCE_BLUEPRINT.md)
> 
> 本节仅提供概要，详细内容请参阅专门文档。

### 2.1 AI治理框架核心要点

| 治理维度 | 核心内容 | 详细文档 |
|---------|---------|---------|
| **AI行为准则** | 核心行为准则、操作行为准则、风险控制准则 | [AI_GOVERNANCE_BLUEPRINT.md](./AI_GOVERNANCE_BLUEPRINT.md) |
| **AI决策透明度** | 透明度等级定义、透明度要求矩阵 | [AI_GOVERNANCE_BLUEPRINT.md](./AI_GOVERNANCE_BLUEPRINT.md) |
| **AI错误责任归属** | 错误类型分类、责任归属、处理流程 | [AI_GOVERNANCE_BLUEPRINT.md](./AI_GOVERNANCE_BLUEPRINT.md) |
| **AI持续学习机制** | 学习机制分类、学习效果评估 | [AI_EVOLUTION_LOOP_BLUEPRINT.md](./AI_EVOLUTION_LOOP_BLUEPRINT.md) |

### 2.2 AI治理框架架构

```
┌─────────────────────────────────────────────────────────────────┐
│                   AI治理框架架构（引用）                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  AI行为准则体系 ──────────────────────────────────────────────► │
│  ├── 核心行为准则 (CP-001 ~ CP-005)                             │
│  ├── 操作行为准则 (OR-001 ~ OR-006)                             │
│  └── 风险控制准则 (RC-001 ~ RC-005)                             │
│                                                                 │
│  AI决策透明度体系 ────────────────────────────────────────────► │
│  ├── L1-L5透明度等级定义                                        │
│  ├── 透明度要求矩阵                                             │
│  └── 可解释性工具集                                             │
│                                                                 │
│  详细内容请参阅: AI_GOVERNANCE_BLUEPRINT.md                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**桥水案例对标**：
- "安全花园"算法化体系：所有投资原则转化为可执行规则
- AI决策必须通过规则检查，否则拦截
- 每次AI错误都转化为新的约束规则

**文艺复兴案例对标**：
- 所有AI决策都有完整的推理链记录
- 关键决策提供反事实解释
- 支持人类随时查询AI决策依据

---

'''

pattern = r'## 🛡️ 二、AI治理框架.*?(?=\n---\n\n## ⚠️ 三、风险分级体系)'

match = re.search(pattern, content, flags=re.DOTALL)
if match:
    print(f"\nPattern found at position {match.start()}-{match.end()}")
    content = re.sub(pattern, new_section.strip(), content, flags=re.DOTALL)
    print("Content replaced successfully")
else:
    print("\nPattern not found, searching for alternative...")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'AI治理框架' in line or '二、' in line:
            print(f"Line {i}: {line[:80]}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nFile saved as UTF-8")
print(f"Final content length: {len(content)}")
