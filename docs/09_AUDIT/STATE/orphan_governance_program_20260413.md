---
module_id: ORPHAN_GOVERNANCE_PROGRAM_001
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
standard_type: 专项治理方案
applicable_scope: 2,939个孤儿文档
compliance_level: 强制标准
priority: P0
layer: layer_09
responsibility:
  - 治理2,939个孤儿文件
  - 建立入链或归档决策机制
  - 重构索引系统
  - 防止新增孤儿文件
---

# 孤儿文件治理专项方案

> **紧急度**: P0  
> **影响范围**: 2,939个文件 (87.7%的docs/)  
> **预计工时**: 40-60小时  
> **治理目标**: 孤儿率从87.7%降至<10%

```
```---
```

## 1. 问题定义

### 1.1 什么是孤儿文件

**定义**: 入度(in-degree) = 0 的文件，即没有任何其他文件通过链接引用它。

**影响**:
- 无法通过导航索引抵达
- 搜索引擎无法发现
- 形成信息孤岛
- 文档价值无法发挥

### 1.2 当前状况

| 指标 | 数值 | 严重程度 |
|------|------|---------|
| 总文档数 | 3,346 | - |
| 孤儿文件数 | **2,939** | 🔴 极高 |
| 孤儿率 | **87.7%** | 🔴 极高 |
| 活跃区孤儿 | ~500 | 🟠 高 |
| 归档区孤儿 | ~2,400 | 🟡 中 |

```
```---
```

## 2. 治理策略

### 2.1 决策树

```
孤儿文件
    ├── 活跃区文档?
    │   ├── 是 → 补充入链(挂载到INDEX.md)
    │   └── 否(归档区)
    │       ├── 有价值保留?
    │       │   ├── 是 → 归档并保留
    │       │   └── 否 → 删除
    │       └── 过时/重复?
    │           ├── 是 → 删除
    │           └── 否 → 保留
    └── 蓝图文档?
        ├── 是 → 挂载到blueprint-index.md
        └── 否 → 常规处理
```

### 2.2 分类标准

| 类别 | 判定标准 | 处理方式 | 预计数量 |
|------|---------|---------|---------|
| **A类-活跃区核心** | 01-11层关键文档 | 补充INDEX.md入链 | ~200 |
| **B类-活跃区一般** | 实施/运维文档 | 挂载到对应模块INDEX | ~300 |
| **C类-归档区有价值** | 历史审计/蓝图 | 保留，可选添加归档索引 | ~1,500 |
| **D类-归档区过时** | 重复/临时/过期 | 删除 | ~900 |

```
```---
```

## 3. 执行计划

### Phase 1: 扫描与分类 (4-6小时)

**步骤**:
1. 运行完整孤儿扫描
2. 按目录和类型分类
3. 生成孤儿文件清单
4. 初步标记处理类别

**输出**:
- `orphan_files_inventory_20260413.json`
- `orphan_files_by_category.md`

### Phase 2: 批量决策 (8-12小时)

**A类处理 (活跃区核心)**:
```bash
# 目标: ~200个核心文档
# 方法: 补充到对应层级的INDEX.md

# 01_FRAMEWORK/ → docs/01_FRAMEWORK/INDEX.md
# 02_FACTOR_LIBRARY/ → docs/02_FACTOR_LIBRARY/INDEX.md
# ...以此类推
```

**B类处理 (活跃区一般)**:
```bash
# 目标: ~300个一般文档
# 方法: 挂载到对应子模块INDEX

# 如: docs/05_IMPLEMENTATION/02_DEVELOPMENT/*.md
#     → docs/05_IMPLEMENTATION/INDEX.md
```

**C类处理 (归档区有价值)**:
```bash
# 目标: ~1,500个归档文档
# 方法: 保留，可选添加轻量化归档索引

# 创建: docs/06_ARCHIVE/INDEX.md 轻量化版本
# 只列出主要类别，不逐一列举
```

**D类处理 (归档区过时)**:
```bash
# 目标: ~900个过时文档
# 方法: 删除

# 包括: 临时报告、重复草稿、过期版本
```

### Phase 3: 执行修复 (20-30小时)

**批量处理脚本**:
```python
# orphan_governance_executor.py
# 功能:
# 1. 自动补充INDEX.md入链
# 2. 自动删除D类文件
# 3. 生成处理报告
```

**人工审查**:
- A类文件逐一确认
- D类文件删除前二次确认

### Phase 4: 验证与闭环 (4-6小时)

**验证指标**:
- 孤儿率 < 10%
- 活跃区孤儿率 < 5%
- 索引覆盖率 > 90%

**持续机制**:
- 每周孤儿扫描
- 新增孤儿自动告警
- 季度深度审计

```
```---
```

## 4. 执行脚本

### 4.1 孤儿扫描脚本

```python
#!/usr/bin/env python3
"""
严格孤儿扫描器
计算每个.md文件的入度(in-degree)
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

DOCS_DIR = Path("docs")

def extract_links(content: str) -> list:
    """提取markdown中的所有链接"""
    # [text]<!-- -->(path) 格式
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    return [m[1] for m in matches if not m[1].startswith(('http', '#'))]

def resolve_link(link: str, base_path: Path) -> Path:
    """解析相对链接为绝对路径"""
    if link.startswith('/'):
        return DOCS_DIR / link.lstrip('/')
    return base_path.parent / link

def scan_orphans():
    """扫描孤儿文件"""
    # 1. 收集所有.md文件
    all_files = list(DOCS_DIR.rglob("*.md"))
    file_set = set(str(f.relative_to(DOCS_DIR)) for f in all_files)
    
    # 2. 统计入度
    in_degree = defaultdict(int)
    
    for md_file in all_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            links = extract_links(content)
            for link in links:
                target = resolve_link(link, md_file)
                target_rel = str(target.relative_to(DOCS_DIR))
                if target_rel in file_set:
                    in_degree[target_rel] += 1
        except Exception:
            continue
    
    # 3. 找出孤儿文件(入度=0)
    orphans = []
    for f in all_files:
        rel_path = str(f.relative_to(DOCS_DIR))
        if in_degree[rel_path] == 0:
            orphans.append({
                'path': rel_path,
                'size': f.stat().st_size,
                'layer': rel_path.split('/')[0] if '/' in rel_path else 'root'
            })
    
    return orphans

if __name__ == "__main__":
    orphans = scan_orphans()
    print(f"发现 {len(orphans)} 个孤儿文件")
    
    # 保存结果
    with open('orphan_scan_result.json', 'w', encoding='utf-8') as f:
        json.dump(orphans, f, ensure_ascii=False, indent=2)
```

### 4.2 批量挂载脚本

```python
#!/usr/bin/env python3
"""
孤儿文件批量挂载器
自动将孤儿文件挂载到对应的INDEX.md
"""

import json
from pathlib import Path

DOCS_DIR = Path("docs")

def mount_to_index(orphan_path: str, index_path: str):
    """将孤儿文件挂载到指定INDEX"""
    index_file = DOCS_DIR / index_path
    orphan_rel = orphan_path.replace('.md', '')
    
    # 读取现有INDEX
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成挂载链接
    link_line = f"- [{Path(orphan_path).name}]<!-- -->(./{orphan_rel}.md)\n"
    
    # 在"## 文档列表"后插入
    if '## 文档列表' in content:
        content = content.replace('## 文档列表\n', f'## 文档列表\n{link_line}')
    else:
        content += f"\n## 文档列表\n{link_line}"
    
    # 写回
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 挂载: {orphan_path} -> {index_path}")

def auto_mount_orphans(orphans: list):
    """自动挂载孤儿文件"""
    for orphan in orphans:
        path = orphan['path']
        parts = path.split('/')
        
        if len(parts) >= 2:
            # 挂载到对应层级的INDEX
            layer = parts[0]
            index_path = f"{layer}/INDEX.md"
            
            if (DOCS_DIR / index_path).exists():
                mount_to_index(path, index_path)
            else:
                # 挂载到根INDEX
                mount_to_index(path, "INDEX.md")

if __name__ == "__main__":
    with open('orphan_scan_result.json', 'r', encoding='utf-8') as f:
        orphans = json.load(f)
    
    # 只处理活跃区(01-11层)
    active_orphans = [o for o in orphans if o['layer'][:2].isdigit()]
    
    print(f"处理 {len(active_orphans)} 个活跃区孤儿文件")
    auto_mount_orphans(active_orphans)
```

```
```---
```

## 5. 进度跟踪

### 5.1 治理看板

| 类别 | 总数 | 已处理 | 剩余 | 进度 |
|------|------|--------|------|------|
| A类-活跃区核心 | ~200 | 0 | 200 | 0% |
| B类-活跃区一般 | ~300 | 0 | 300 | 0% |
| C类-归档区有价值 | ~1,500 | 0 | 1,500 | 0% |
| D类-归档区过时 | ~900 | 0 | 900 | 0% |
| **总计** | **2,900** | **0** | **2,900** | **0%** |

### 5.2 关键里程碑

- [ ] **M1**: 完成扫描与分类 (4-6h)
- [ ] **M2**: 完成D类删除 (4-6h)
- [ ] **M3**: 完成A类挂载 (8-12h)
- [ ] **M4**: 完成B类挂载 (8-12h)
- [ ] **M5**: 完成C类归档索引 (4-6h)
- [ ] **M6**: 验证孤儿率<10% (2-4h)

```
```---
```

## 6. 预防措施

### 6.1 Pre-commit钩子增强

```yaml
# .pre-commit-config.yaml 新增
- id: orphan-guard
  name: 孤儿文件守卫
  entry: python scripts/check_orphan_before_commit.py
  language: system
  files: ^docs/.*\.md$
  pass_filenames: false
```

### 6.2 新文档创建检查清单

```markdown
## 新文档创建检查清单

- [ ] 文档已挂载到对应INDEX.md
- [ ] 文档可通过SITEMAP导航抵达
- [ ] 文档有至少一个入链
- [ ] 前置检查: python scripts/check_orphan_status.py docs/new-file.md
```

### 6.3 周度扫描

```bash
# 添加到crontab (每周一上午9点)
0 9 * * 1 cd /path/to/project && python scripts/strict_orphan_inbound_scan.py --report
```

```
```---
```

## 7. 风险评估

### 7.1 执行风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 误删有价值文档 | 中 | 高 | D类删除前二次确认 |
| INDEX.md冲突 | 高 | 中 | 批量更新时顺序执行 |
| 挂载后格式错误 | 中 | 低 | 验证每个INDEX.md格式 |

### 7.2 回滚方案

```bash
# 所有操作前创建Git备份
git checkout -b orphan-governance-backup-$(date +%Y%m%d)

# 如出现问题，回滚到备份
git reset --hard orphan-governance-backup-20260413
```

```
```---
```

## 8. 成功标准

### 8.1 量化指标

| 指标 | 当前 | 目标 | 验证方法 |
|------|------|------|---------|
| 孤儿率 | 87.7% | <10% | strict_orphan_inbound_scan.py |
| 活跃区孤儿率 | ~70% | <5% | 按layer过滤扫描 |
| 索引覆盖率 | ~12% | >90% | 抽样点击测试 |
| 新增孤儿/周 | N/A | 0 | 周度扫描报告 |

### 8.2 定性指标

- [ ] 用户可通过导航找到任何活跃区文档
- [ ] 无"404死链"报告
- [ ] 新文档创建流程包含防孤儿检查

```
```---
```

**专项启动时间**: 2026-04-13  
**预计完成时间**: 2026-04-20 (7天内)  
**负责人**: 首席文档架构师  
**状态**: 🟡 待启动
