---
module_id: KE-1110
status: active
title: 决策流程总图（Decision Flow Map）
category: governance
ttl: permanent
---

# 决策流程总图（Decision Flow Map）

决策流程总图（Decision Flow Map）

> **AI 导航指引**：此图为 MTH-001~009 的完整决策链路。每次承担治理任务时，先执行总则（最优先行——判断"怎么做最好"），再从此图入口开始，按箭头方向执行。方法论细节见各 MTH-XXX 条目。

```mermaid
flowchart TD
    START["🚀 任务启动<br/><i>（先执行总则：最优先行原则</br>——判断最优方案后再查约束）</i>"] --> MTH002["MTH-002<br/>架构上下文自检<br/>我在哪一层？"]
    MTH002 --> MTH001["MTH-001<br/>标准先行<br/>专业机构怎么说？"]
    MTH001 --> Q1{"发现问题？"}
    Q1 -->|是| MTH006["MTH-006<br/>根源分析<br/>追问到底治根"]
    Q1 -->|否| MTH009["MTH-009<br/>补漏+够用双检"]
    MTH006 --> Q2{"SSoT 冲突？"}
    Q2 -->|是| MTH008["MTH-008<br/>SSoT 冲突裁决<br/>时序→语义→先例→裁决"]
    Q2 -->|否| MTH007["MTH-007<br/>决策质量四问<br/>埋雷→容量→对标→建议"]
    MTH008 --> MTH007
    MTH007 --> OWNER["👤 Owner 决策"]
    OWNER --> MTH004["MTH-004<br/>对标架构标准"]
    MTH004 --> MTH005["MTH-005<br/>1500+ 自治预留"]
    MTH005 --> Q3{"目标冲突？"}
    Q3 -->|是| MTH003["MTH-003<br/>目标优先原则"]
    Q3 -->|否| EXEC["⚡ 执行修复"]
    MTH003 --> EXEC
    EXEC --> MTH009
    MTH009 --> Q4{"够用？"}
    Q4 -->|是| DONE["✅ 任务完成"]
    Q4 -->|否| BACKLOG["📋 进入 Backlog<br/>标注触发条件"]
```

**ASCII 速查版**（纯文本 AI session）：

```
  START ──→ [总则:最优先行] ──→ MTH-002 ──→ MTH-001
                ↓
          [发现问题?]── 否 ──→ MTH-009 ──→ [够用?]── 是 ──→ ✅
                ↓ 是                          ↓ 否
           MTH-006 (追问到底)              📋 Backlog
                ↓
          [SSoT冲突?]── 是 ──→ MTH-008 ──┐
                ↓ 否                      ↓
           MTH-007 (四问) ←──────────────┘
                ↓
           👤 Owner 决策
                ↓
           MTH-004 → MTH-005 → [目标冲突?]── 是 ──→ MTH-003
                                     ↓ 否              ↓
                                    ⚡执行 ←──────────┘
                                       ↓
                                    MTH-009 → ...
```

---
