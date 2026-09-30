# 判定书：VAL-P0-20260914-000856-002

对象：BT-P0-002 / TDM-E-L1-AGG ｜ method=agg_discrimination ｜ 窗口=2019-04~2026-09
结论：verdict=pending ｜ significance=ok ｜ verdict_reason=discrimination_below_threshold
判定链：冻结口径（backlog plan，2026-09-12 frozen）代码执行，未手调。

关键数字：{
 "min_p": 0.0005845697848615791,
 "p_vals": {
  "r3>r2": 0.0005845697848615791,
  "r2>r1": 0.33399677774809056,
  "r1>r4": 0.9730811406629284
 },
 "spread": -0.8173558342056662,
 "total": 2229,
 "dropped_small_buckets": [
  "r10",
  "r11",
  "r12"
 ],
 "bucket_counts": {
  "r1": 163,
  "r2": 223,
  "r3": 968,
  "r4": 875,
  "r10": 0,
  "r11": 0,
  "r12": 0
 },
 "bucket_means": {
  "r1": 0.8873010849221747,
  "r2": 1.3033534473536708,
  "r3": 0.05716415239026308,
  "r4": 0.8745199865959292,
  "r10": null,
  "r11": null,
  "r12": null
 },
 "verdict": "pending",
 "reason": "discrimination_below_threshold"
}

分段：IS={"min_p": 0.00015502162933217899, "p_vals": {"r3>r2": 0.035515760473795135, "r2>r1": 0.8486321529007989, "r1>r4": 0.00015502162933217899}, "spread": 0.2000655256961016, "total": 1156, "dropped_small_buckets": ["r10", "r11", "r12"], "bucket_counts": {"r1": 133, "r2": 122, "r3": 417, "r4": 484, "r10": 0, "r11": 0, "r12": 0}, "bucket_means": {"r1": 0.8669565061849137, "r2": 0.7567880028760499, "r3": -0.40722785044177423, "r4": -0.6072933761378758, "r10": null, "r11": null, "r12": null}, "verdict": "pending", "reason": "discrimination_below_threshold"}
OOS={"min_p": 3.0111361679740476e-08, "p_vals": {"r3>r2": 3.0111361679740476e-08, "r2>r1": 0.01867518788228922, "r1>r4": 0.000204599351678682}, "spread": -3.856419105209681, "total": 653, "dropped_small_buckets": ["r10", "r11", "r12"], "bucket_counts": {"r1": 29, "r2": 84, "r3": 366, "r4": 174, "r10": 0, "r11": 0, "r12": 0}, "bucket_means": {"r1": 0.5756494351889144, "r2": 2.106738799477403, "r3": -0.08154977704122361, "r4": 3.774869328168457, "r10": null, "r11": null, "r12": null}, "verdict": "valid", "reason": "discrimination_confirmed"}
lag_recheck：0.00035891802755212335

台账回执：node_verdict run_id=VAL-P0-20260914-000856-002
