---
ttl: task_bound
---

# L-D 元数据线作业簿（重建版，内容全息）

六向台账：①上游=列表刷新任务四表写方 ②下游=PIT 时点查询/回测标的池 ③读写=c1_market 四表 valid_from DEFAULT toDate(list_date)（system.columns 实证）④调度=月度/日度刷新 ⑤断点=09-30 三表死信+stock_list 第四雷（普查新发现）⑥治理=#ARCH-CH-024/契约 v1.5.0。

施工：四表 `ALTER TABLE MODIFY COLUMN valid_from DEFAULT ifNull(toDate(list_date), toDate('2000-01-01'))` 全部生效（system.columns 复读）；Memory 引擎等价注入实测 NULL→2000-01-01/有值→透传；数据面复核 cb 1059/etf 4377/index 9,744(=键去重收敛无丢失)/stock 5,921。回滚键=各表单句改回原 DEFAULT。自审闸：**挖干+已施工+已验证**。
