---
ttl: task_bound
title: 批2 消费端即贴补丁——daily_gate_snapshot L2 三原料接线（乙档治本最后 5 行）
created: 2026-09-23
sid: st-secbuild-20260923
lane: sector_line
status: ready_to_apply（供料端已全量上线并实测；消费端因目标文件带他会话在途 WIP 避让，出即贴补丁）
---

# 批2 消费端接线即贴补丁（apply 前置条件：主区 daily_gate_snapshot.py 的水位桥 WIP 落地后）

## §1 为什么只出补丁不直接贴

- `src/zephyr/strategy_pipeline/daily_gate_snapshot.py` 主区存在**未提交在途 WIP**（水位桥
  方案甲改造，+249 行，盘点册 §4 实证"桥接在位"）——按并行协调纪律（他会话在途不代修、
  HOT-FILE 不外科改写），本班不直接编辑，出即贴补丁。
- 补丁目标状态 = WIP 落地后的 `_collect_l2`（`water_temp_response` 查表版，返回 dict 带
  `gate_level="not_evaluated"`）。

## §2 供料端现状（已上线，实测通过）

- 表 `c1_market.sector_state`（469 板 × close_final/pre_open，09-22/09-23 实弹落库）
  + `c1_market.sector_preference`（OFFENSIVE tilt=1.2 banned=lagging，emotion 真值 v0.1.0）。
- 读端 API：`zephyr.data.sector_state_pipeline.load_l2_admission(trade_date=None)` →
  `{"status":"ok","top":[...5 板],"retained_sectors":[...294 板],"score":57.0,
  "preference_label":"OFFENSIVE","banned_quadrant":"lagging","tilt":1.2,"asof":"2026-09-23"}`
  （fail-open：任何异常恒 `{"status":"absent"}`，不炸门）。

## §3 补丁正文（两处）

### 3.1 `daily_gate_snapshot.py` `_collect_l2` 返回前注入（return dict 组装处）

```python
    # 乙档供料（st-secbuild-20260923 批2）：sector_state 三原料首次有着落。
    # fail-open：load_l2_admission 任何异常恒 absent，不改变本函数缺席语义。
    try:
        from zephyr.data.sector_state_pipeline import load_l2_admission

        admission = load_l2_admission()
    except Exception:  # noqa: BLE001 — 供料异常=门未评，保持 not_evaluated
        admission = {"status": "absent"}
    ...
    return {
        ...原有键不变...,
        "gate_level": "evaluated" if admission.get("status") == "ok" else "not_evaluated",
        "admission": admission,  # top/retained_sectors/score 三原料 + 偏好标签/tilt/banned
    }
```

### 3.2 `daily_decision_orchestrator.py` `_s3_gate_leg`（可观测注记，零行为变更）

```python
    l2 = gate.get("l2") or {}
    adm = l2.get("admission") or {}
    if adm.get("status") == "ok":
        ctx.notes.append(
            f"板块门供料: top={','.join(adm.get('top')[:3])} "
            f"偏好={adm.get('preference_label')} tilt={adm.get('tilt')} "
            f"score={adm.get('score')}"
        )
```

（仅注记，不改 position_cap/packages/no_trade 判定——丁线行为变更归丁线 Owner 门位。）

## §4 验收口径

- 贴补丁后跑 `collect_gate_snapshot`：l2.gate_level 从恒 `not_evaluated` → `evaluated`
  （sector_state 当日有 pre_open 行时）；断供日自动退回 `not_evaluated`（fail-open）。
- `tests/strategy_pipeline/test_daily_gate_snapshot_l2.py`（水位桥 WIP 所带测试文件）同批
  增补 admission 断言。
