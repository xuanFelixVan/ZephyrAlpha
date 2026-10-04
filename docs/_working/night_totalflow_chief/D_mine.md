---
ttl: task_bound
---

# L-D 元数据线作业簿（重建版）

六向：①列表刷新四表写方 ②PIT 时点查询 ③c1_market 四表 valid_from DEFAULT toDate(list_date) ④月度/日度刷新 ⑤09-30 三表死信+stock_list 第四雷 ⑥#ARCH-CH-024。施工：四表 ALTER MODIFY COLUMN DEFAULT ifNull(toDate(list_date), toDate('2000-01-01')) 全生效；Memory 引擎注入实测 NULL→2000-01-01/有值→透传；数据面 cb 1059=键去重健康态/etf 4377/index 9744/stock 5921。回滚键=各表单句改回。自审闸：挖干+已施工+已验证。
