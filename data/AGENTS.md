# data 局部宪法（投影，立法权在根宪法）

- 本目录是什么：数据与能力卡区——业务数据库/缓存/备份/capability_cards/（44 件渐进披露卡）。
- 真源指针：数据资产册=docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml（REG-DATAFLOW-001）；能力卡=本目录 capability_cards/*.yaml。
- 禁止：测试写本目录——输出一律 tmp_path fixture（根宪法 §9 条目 6）。
- 禁止：绕过 CapabilityLookup 手工加卡；破坏性 DB 操作不做三步验证（根宪法 §1 条目 7）。
- 单口：判重 `python scripts/check_tick_duplication.py`（禁聚合数）。
- 单口：数据操作规程=docs/01_policies_and_standards/sop/data_ops_sop/data_ops_policy.md；查资产 `python -m zephyr.library.lookup <关键词>`。
- 存储分工：冷库/备份/CH 双链地图=INFRA-STORE-003；访问一律走 DatabaseService，禁裸连。
- 冲突裁决：以根宪法为准；本文件仅局部提醒，不新增规则。
- 引用格式：引用根宪法用"根宪法 §N"字样。
