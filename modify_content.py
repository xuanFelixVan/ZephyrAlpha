import re

file_path = r'D:\ZephyrAlpha\docs\01_FRAMEWORK\HUMAN_AI_INTERACTION_BLUEPRINT.md'

with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

print(f"Content length: {len(content)}")

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

lines = content.split('\n')
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if '二、AI治理框架' in line and start_idx is None:
        start_idx = i
        print(f"Found start at line {i}: {line[:60]}")
    if '三、' in line or '风险分级' in line:
        end_idx = i
        print(f"Found end at line {i}: {line[:60]}")
        break

if start_idx is not None and end_idx is not None:
    print(f"\nReplacing lines {start_idx} to {end_idx-1}")
    
    for j in range(start_idx-1, -1, -1):
        if lines[j].strip() == '---':
            start_idx = j
            print(f"Adjusted start to line {start_idx} (found ---)")
            break
    
    new_lines = lines[:start_idx] + new_section.strip().split('\n') + lines[end_idx-1:]
    content = '\n'.join(new_lines)
    print("Content replaced successfully")
else:
    print(f"Could not find markers: start_idx={start_idx}, end_idx={end_idx}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nFile saved")
print(f"Final content length: {len(content)}")
