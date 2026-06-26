---
module_id: KE-1760
title: 2.2 depends_on 声明
category: module_blueprint
ttl: permanent
---

# 2.2 depends_on 声明

2.2 depends_on 声明

| target | at | why |
|--------|-----|-----|
| MOD-INF-006 | §4 | G0-G7门禁体系——脚本失败→任务BLOCKED的状态转换定义 |
| MOD-INF-006 | §5 | 管线M1-M11——run_all.py批量运行→管线节点判定逻辑 |
| MOD-INF-006 | §3.2.1 + §4.2 + §3.1.2 | TaskCard 模型 + 10状态机 + task_id格式——Finding→任务卡关联 |
| MOD-KB-001 | §3.2 + §6 | KE Schema + KB 入库——MEDIUM Finding→KB + C5 知识沉淀 |
| PS-STD-001 | §7 | metadata注册表——脚本注册字段定义 |
| SCRIPT-QUALITY-001 | §2 | 脚本退出码约定（0/1/2/3）——编码铁律在质量标准中定义 |
