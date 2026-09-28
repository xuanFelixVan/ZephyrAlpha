---
ttl: task_bound
title: L09 案卷 F87 — AI 红线（negative_list/年审/会话环境守卫/严重度路由）
session: zc-l09-20260927
---

# F87 AI 红线（J 段 A2，骨架态=partial/P1）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | OBJ_S 自由域 DESIGN（negative_list NL-1..6 编号层）；CONSTITUTION-LINE-LIMIT 判据②=AGENTS.md ≤300 行硬上限（宪法 §6，gate register_line 注记原文） |
| 下游消费 | 提交链三 gate（in_process_gate_registry.yaml:710 REAL-KEY-REFERENCE-SCAN / :716 TASK-ORDER-DOCS-LOCK / :722 CONSTITUTION-LINE-LIMIT，本日三条 enabled:true）；dashboard_pipeline→前端投影；freedom_weekly_report/annual_review→治理周报/年审面 |
| 自动化触发 | 三 gate=提交链内自动（每次 commit 经网关）；sev_router=严重度路由（事件内）；年审/周报=manual CLI |
| 真源与注册表 | `src/zephyr/ai_layer/redline/` 10 件（本日实扫）；gate 工厂=negative_list_gates.make_*（module_path 实锚） |
| 门禁与质量尺 | tests/ai_layer/redline/test_negative_list_gates.py（register_line 注记指认）；09-26 st-ddup 翻回注记"三工厂实测可导入" |
| 当前运行状态 | **黄**：三 gate 在岗自动（提交链内）；但 session_env_guard 被 09-27 接线普查判"装饰"（仅 noqa 静态 import）；周报/年审 manual 且无周/年节拍宿主证据 |

## 二、子模块三级枚举（redline/ 10 件实扫）

1. `negative_list.py`：NL-1..6 编号层负面清单本体。
2. `negative_list_gates.py`：三 gate 工厂（make_real_key_reference_scan/make_task_order_docs_lock/make_constitution_line_limit，priority 149/150/151）。
3. `session_env_guard.py`：会话环境守卫——**接线普查判装饰**（wiring_gap §1.6 C 类装饰 2："仅 noqa 静态 import"）。
4. `drop_gate.py`：丢弃闸。
5. `no_delete_manifest.py`：禁删清单。
6. `sev_router.py`：严重度路由（M4：import OK 实测在案）。
7. `dashboard_pipeline.py`：红线面板投影管线。
8. `freedom_weekly_report.py`：自由域周报。
9. `annual_review.py`：年审。
10. `__init__.py`：红线句（"ModuleNotFoundError 之谜"已解=环境性误报，M4 分册01 §三.8 在案）。

## 三、接线四态独立复核

- **三 gate=已接线**：enabled:true 本日复核（710/716/722），own-diff 作用域，提交链自动触发。曾停用→09-26 翻回（册内注记 W4 看守项）。
- **session_env_guard=装饰（半接线偏下）**：09-27 接线普查（wiring_gap §1.6）列为"C 类装饰 2"——静态 import 无运行时消费方；骨架所称"会话环境守卫"四能力中此件名实待核。
- **周报/年审=建成未接线（缺节拍）**：manual CLI 无周/年宿主登记证据（类比 perceive 外扫宿主缺位模式）。
- **drop_gate/no_delete_manifest/dashboard_pipeline=待核态**：本卷未逐件追运行时调用方（登记待挖，不冒判）。

## 骨架勘误

1. 骨架"partial（M4：redline 之谜已解在案）"成立且收口：10 件本日全在盘、三 gate enabled。
2. 新增缺口定性：**session_env_guard 装饰化**是 F87 的当前主要 redline 缺口（骨架括注未点名）；三 gate 的 priority 149/150/151 在册注记与本日行号 710/716/722 对齐（M4 记 707-725 段，漂移 3 行，无实质矛盾）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | session_env_guard 零运行时调用方（装饰） | 按接线普查 C 类处置：读码定性→接线或降档/退役登记 | P1 |
| 2 | freedom_weekly_report/annual_review 无节拍宿主 | 周报挂既有周历（F80 五模块）或登记 manual 语义 | P2 |
| 3 | drop_gate/no_delete_manifest/dashboard_pipeline 消费方未逐件核 | 待挖（列 M5/M4 后续普查面） | P2 |

## 五、自审闸三态

**挖干（10 件穷举+三 gate 册页实锚+装饰判定引今日普查）✅；待裁（缺口#1 处置方向）；待挖（缺口#3 三件消费面——本卷不越判）。**

## 六、复跑命令

```bash
ls src/zephyr/ai_layer/redline/*.py | wc -l                         # 10
sed -n '710,728p' docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml | grep -E "gate_id|enabled"
python -c "import zephyr.ai_layer.redline.sev_router"               # 导入 OK
grep -rn "session_env_guard" src/ scripts/ --include="*.py" | grep -v "redline/session_env_guard.py\|test" | head -4
```
