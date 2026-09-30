# 判定书：VAL-P0-20260914-001639-002

对象：BT-P0-002 / TDM-E-L1-AGG ｜ method=agg_discrimination ｜ 窗口=2019-04~2026-09
结论：verdict=pending ｜ significance=ok ｜ verdict_reason=discrimination_below_threshold
判定链：冻结口径（backlog plan，2026-09-12 frozen）代码执行，未手调。

关键数字：{
 "min_p": 2.710199230856572e-07,
 "p_vals": {
  "r3>r2": 0.824061632113436,
  "r2>r1": 0.0002811379696763753,
  "r1>r4": 2.710199230856572e-07
 },
 "spread": -0.47778436741686314,
 "total": 4458,
 "dropped_small_buckets": [
  "r10",
  "r11",
  "r12"
 ],
 "bucket_counts": {
  "r1": 557,
  "r2": 843,
  "r3": 1619,
  "r4": 1439,
  "r10": 0,
  "r11": 0,
  "r12": 0
 },
 "bucket_means": {
  "r1": -0.4157768397879746,
  "r2": 0.5923486784468149,
  "r3": 0.5417827616453004,
  "r4": 1.0195671290621635,
  "r10": null,
  "r11": null,
  "r12": null
 },
 "verdict": "pending",
 "reason": "discrimination_below_threshold"
}

分段：IS={"min_p": 0.001439807889279852, "p_vals": {"r3>r2": 0.006552941394022028, "r2>r1": 0.001439807889279852, "r1>r4": 0.23040553082500706}, "spread": -0.014957767916692066, "total": 2312, "dropped_small_buckets": ["r10", "r11", "r12"], "bucket_counts": {"r1": 325, "r2": 478, "r3": 846, "r4": 663, "r10": 0, "r11": 0, "r12": 0}, "bucket_means": {"r1": -0.7224203918898177, "r2": 0.46562463769290635, "r3": -0.33791932511911565, "r4": -0.3229615572024236, "r10": null, "r11": null, "r12": null}, "verdict": "pending", "reason": "discrimination_below_threshold"}
OOS={"min_p": 4.066136392734844e-09, "p_vals": {"r3>r2": 0.26709055376546764, "r2>r1": 0.10082834182875001, "r1>r4": 4.066136392734844e-09}, "spread": -1.7478462784168958, "total": 1306, "dropped_small_buckets": ["r10", "r11", "r12"], "bucket_counts": {"r1": 154, "r2": 291, "r3": 514, "r4": 347, "r10": 0, "r11": 0, "r12": 0}, "bucket_means": {"r1": -0.022135933859083252, "r2": 0.5592500005398514, "r3": 0.9199891262597708, "r4": 2.6678354046766666, "r10": null, "r11": null, "r12": null}, "verdict": "valid", "reason": "discrimination_confirmed"}
lag_recheck：1.4221207307087617e-07

台账回执：node_verdict run_id=VAL-P0-20260914-001639-002
