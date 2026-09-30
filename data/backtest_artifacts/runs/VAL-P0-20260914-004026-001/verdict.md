# 判定书：VAL-P0-20260914-004026-001

对象：BT-P0-001 / TDM-E-L1 ｜ method=agg_discrimination ｜ 窗口=2019-04~2026-09
主判据：return_discrimination（裁定#230）
结论：verdict=valid ｜ significance=ok ｜ verdict_reason=discrimination_confirmed
判定链：冻结口径（backlog plan，2026-09-12 frozen；判据对象变更=裁定#230）代码执行，未手调。

关键数字：{
 "primary": {
  "p": 4.54934076891809e-20,
  "delta": -2.058658753320423,
  "counts": {
   "Q1": 452,
   "Q2": 452,
   "Q3": 452,
   "Q4": 452
  },
  "total": 1808,
  "means": {
   "Q1": -4.672422547729804,
   "Q2": -3.1123307088769776,
   "Q3": -2.5603818832626577,
   "Q4": -2.613763794409381
  },
  "verdict": "valid",
  "reason": "discrimination_confirmed"
 },
 "primary_id": "return_discrimination",
 "return_discrimination": {
  "p": 4.54934076891809e-20,
  "delta": -2.058658753320423,
  "counts": {
   "Q1": 452,
   "Q2": 452,
   "Q3": 452,
   "Q4": 452
  },
  "total": 1808,
  "means": {
   "Q1": -4.672422547729804,
   "Q2": -3.1123307088769776,
   "Q3": -2.5603818832626577,
   "Q4": -2.613763794409381
  },
  "verdict": "valid",
  "reason": "discrimination_confirmed"
 },
 "risk_discrimination": null,
 "is_return": {
  "p": 5.501560635588145e-14,
  "delta": -1.7981105075162773,
  "counts": {
   "Q1": 289,
   "Q2": 289,
   "Q3": 289,
   "Q4": 289
  },
  "total": 1156,
  "means": {
   "Q1": -4.309282650345877,
   "Q2": -3.3474739357098433,
   "Q3": -2.7543097760657127,
   "Q4": -2.5111721428296
  },
  "verdict": "pending",
  "reason": "discrimination_confirmed"
 },
 "oos_return": {
  "p": 3.016673878341817e-08,
  "delta": -2.308859754051152,
  "counts": {
   "Q1": 163,
   "Q2": 163,
   "Q3": 163,
   "Q4": 163
  },
  "total": 652,
  "means": {
   "Q1": -5.215431723121297,
   "Q2": -3.008839914713484,
   "Q3": -1.893054493482676,
   "Q4": -2.9065719690701446
  },
  "verdict": "valid",
  "reason": "discrimination_confirmed"
 },
 "is_risk": null,
 "oos_risk": null
}

分段：IS={"p": 5.501560635588145e-14, "delta": -1.7981105075162773, "counts": {"Q1": 289, "Q2": 289, "Q3": 289, "Q4": 289}, "total": 1156, "means": {"Q1": -4.309282650345877, "Q2": -3.3474739357098433, "Q3": -2.7543097760657127, "Q4": -2.5111721428296}, "verdict": "pending", "reason": "discrimination_confirmed"}
OOS={"p": 3.016673878341817e-08, "delta": -2.308859754051152, "counts": {"Q1": 163, "Q2": 163, "Q3": 163, "Q4": 163}, "total": 652, "means": {"Q1": -5.215431723121297, "Q2": -3.008839914713484, "Q3": -1.893054493482676, "Q4": -2.9065719690701446}, "verdict": "valid", "reason": "discrimination_confirmed"}
lag_recheck：None

台账回执：node_verdict run_id=VAL-P0-20260914-004026-001
