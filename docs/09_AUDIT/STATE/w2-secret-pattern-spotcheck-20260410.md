---
module_id: W2_SECRET_PATTERN_SPOTCHECK_20260410
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_09
responsibility: STATE
---







# W2 等价检查 — 密钥型字面量模式抽查（2026-04-10）

> **目的**：满足 全库蓝图终稿任务清单 **W2（可选）**「密钥/秘密扫描或等价检查」的**可复跑记录**；**不**替代专业 secret scanner 或 CI。

## 方法

1. 对象：`git ls-files` 已跟踪、后缀属于 `{.md,.py,.yaml,.yml,.toml,.json,.env,.example,.txt,.ps1,.bat}` 的文件（各文件最多读取前 **128KiB** UTF-8，忽略解码错误）。  
2. 正则（命中任一即计 1 次，按文件去重）：  
   - `AKIA[0-9A-Z]{16}`（类 AWS Access Key ID）  
   - `-----BEGIN … PRIVATE KEY-----`（类 PEM 私钥块）  
   - `sk-[a-zA-Z0-9]{32,}`（类长 live secret 前缀）  

## 结果

| 指标 | 值 |
|------|-----|
| 按后缀纳入扫描的已跟踪文件数 | 4366 |
| **命中文件数** | **0** |

## 复跑（仓库根）

```powershell
python -c "import re,subprocess; from pathlib import Path; root=Path('.'); files=subprocess.check_output(['git','ls-files'],text=True).splitlines(); pats=[(re.compile(r'AKIA[0-9A-Z]{16}'),'aws'),(re.compile(r'-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----'),'pem'),(re.compile(r'sk-[a-zA-Z0-9]{32,}'),'sk')]; suf=('.md','.py','.yaml','.yml','.toml','.json','.env','.example','.txt','.ps1','.bat'); hits=[]; 
for f in files:
    if not f.endswith(suf): continue
    p=root/f
    if not p.is_file(): continue
    try: d=p.read_text(encoding='utf-8',errors='ignore')[:131072]
    except OSError: continue
    for rx,_ in pats:
        if rx.search(d): hits.append(f); break
print('hits',len(hits))"
```

若将来命中 >0：须**不要**将密钥写入审计正文；在 PR 中轮换密钥、从 Git 历史中清除（按安全流程），并更新本表。
