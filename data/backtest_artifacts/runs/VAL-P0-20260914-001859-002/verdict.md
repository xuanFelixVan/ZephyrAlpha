# 判定书：VAL-P0-20260914-001859-002

对象：BT-P0-002 / TDM-E-L1-AGG ｜ method=agg_discrimination ｜ 窗口=2019-04~2026-09
结论：verdict=pending ｜ significance=ok ｜ verdict_reason=discrimination_below_threshold
判定链：冻结口径（backlog plan，2026-09-12 frozen）代码执行，未手调。

关键数字：{
 "min_p": 7.619116497560379e-10,
 "p_vals": {
  "r3>r2": 0.006189235212478284,
  "r2>r1": 5.505062617790253e-05,
  "r1>r4": 7.619116497560379e-10
 },
 "spread": -0.07880102217594698,
 "total": 2229,
 "dropped_small_buckets": [
  "r10",
  "r11",
  "r12"
 ],
 "bucket_counts": {
  "r1": 394,
  "r2": 620,
  "r3": 651,
  "r4": 564,
  "r10": 0,
  "r11": 0,
  "r12": 0
 },
 "bucket_means": {
  "r1": -1.085813753755654,
  "r2": 0.3301976395513015,
  "r3": 1.199192417317971,
  "r4": 1.277993439493918,
  "r10": null,
  "r11": null,
  "r12": null
 },
 "verdict": "pending",
 "reason": "discrimination_below_threshold"
}

分段：IS={"min_p": 1.0440857248543795e-05, "p_vals": {"r3>r2": 0.061795235794459905, "r2>r1": 1.0440857248543795e-05, "r1>r4": 5.574716859245793e-05}, "spread": -0.7163957658698681, "total": 1156, "dropped_small_buckets": ["r10", "r11", "r12"], "bucket_counts": {"r1": 192, "r2": 356, "r3": 429, "r4": 179, "r10": 0, "r11": 0, "r12": 0}, "bucket_means": {"r1": -1.823395013993668, "r2": 0.3658439338941887, "r3": -0.27054949980548254, "r4": 0.4458462660643856, "r10": null, "r11": null, "r12": null}, "verdict": "pending", "reason": "discrimination_below_threshold"}
OOS={"min_p": 2.991225138479299e-07, "p_vals": {"r3>r2": 2.991225138479299e-07, "r2>r1": 0.8877068424328585, "r1>r4": 0.0001230433977496687}, "spread": 1.73238416282294, "total": 653, "dropped_small_buckets": ["r10", "r11", "r12"], "bucket_counts": {"r1": 125, "r2": 207, "r3": 148, "r4": 173, "r10": 0, "r11": 0, "r12": 0}, "bucket_means": {"r1": -0.16540680743257027, "r2": -0.10625036377007997, "r3": 3.3967677655041233, "r4": 1.6643836026811833, "r10": null, "r11": null, "r12": null}, "verdict": "valid", "reason": "discrimination_confirmed"}
lag_recheck：1.1294991245172934e-09

台账回执：node_verdict run_id=VAL-P0-20260914-001859-002
