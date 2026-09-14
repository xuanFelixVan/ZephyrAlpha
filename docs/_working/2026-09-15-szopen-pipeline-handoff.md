---
ttl: task_bound
---

# 交接指令：深圳开放数据 47 接口全量接入管线（新对话执行）

> **给新对话的 AI**：本文件是完整交接。按"任务清单"顺序执行，全部坑位与解法已写明。执行前先读本文件全文 + 必读文件三件。

## 一、项目背景简介（大白话）

ZephyrAlpha（D:\ZephyrAlpha）是 Owner 的个人量化系统。另类数据消费端建设进行中：深圳开放数据平台（opendata.sz.gov.cn）的 **47 个接口已全部订阅**（appKey 已入库），其中 **19 个已接入管线并回补约 64 万行数据**，剩余 **28 个已订阅但未接入**（卡在服务地址发现，见任务 3）。本轮已完成：数据源挖掘（全库 3,157 接口 + 4,845 数据资源两轮）、20+ 个因子位（F1-F27）的挖矿与判定（7 个存活上线、7 个封矿淘汰、2 个观察项、6 个 GAP 积累中）。

## 二、必读文件（按序）

| 文件 | 作用 |
|------|------|
| `D:\ZephyrAlpha\AGENTS.md` | 宪法 L0（冷启动/提交纪律/热文件规则） |
| `D:\ZephyrAlpha\docs\01_policies_and_standards\sop\mining_sop\mining_sop_policy.md` | 挖矿 SOP（新因子位开挖必读） |
| `D:\ZephyrAlpha\docs\_working\2026-09-14-typhoon-bdi-factor-mining-plan.md` | **本域总台账**：全部因子位判定/结果矩阵/方法论文训/复开条件 |
| `D:\ZephyrAlpha\docs\_working\alt_data_consumption_plan.md` | 因子位菜单 F1-F27（消费设计卡） |
| `D:\ZephyrAlpha\docs\_working\2026-09-12-alt-data-handoff.md` | 前序交接（密钥状态/话术） |

## 三、工作文件与代码路径

| 路径 | 内容 |
|------|------|
| `D:\ZephyrAlpha\data\sz_open_data_catalog\` | **工作数据归档**：catalog_full.csv（3,157 全目录）、subscribe_status.json（订阅状态）、mining_round2.json、dataset_delta.json、fields_probe.json、fields_round2.json、订阅核验与字段探测脚本已升 scripts/data/sz_open_data/ |
| `D:\ZephyrAlpha\src\zephyr\data\implementations\akshare_alt_provider.py` | **核心 provider**（source=akshare_alt）：已有 10 能力（alt_stock_comment/alt_shipping_index/alt_typhoon_track/alt_sz_stat_monthly/alt_sz_port_monthly/alt_sz_house_daily/alt_sz_weather_warning/alt_sz_marine_forecast/alt_typhoon_landfall_history/alt_typhoon_names）；spec 驱动通用拉取器 `_sz_open_fetch_rows` + `_SZ_OPEN_CAPS` setattr 生成法 |
| `D:\ZephyrAlpha\schemas\categories\market_alt_*.py` + `market_typhoon_*.py` | 已有 10 张表 DDL-as-Code |
| `D:\ZephyrAlpha\scripts\ch\apply_market_tables_ddl.py` | DDL 应用器（新表需加 import + _ALL_DDL + _EXPECTED_ENGINES 三处） |
| `D:\ZephyrAlpha\tests\zephyr\data\test_alt_sources.py` | 测试（21 passed 基线） |
| `D:\ZephyrAlpha\src\zephyr\data\config\tasks.yaml` / `schedule.yaml` | 调度 |
| `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\business_data_categories.yaml` | 表名真源（新表先登记此处，provider import 才不炸） |
| `D:\ZephyrAlpha\.env` | `SZ_OPEN_DATA_APPKEY`（**用这把**，见坑位①） |
| `.runtime\tmp\szcatalog\` | 运行时探测脚本与中间产物（可能被 TTL 清理，正本已在 sz_open_data_tools） |

## 四、任务清单（新对话按序执行）

### 任务 0：复测订阅状态（5 分钟）
```
python .runtime/tmp/szcatalog/../../scripts/data/sz_open_data/status_all.py 的归档版
（或按其逻辑重写：getApiDocument 取 ctx → appKey 实调 rows=1 → 10001=未生效）
```
预期：47 个中约 19 个生效（首轮 17+能见度+环境气象预报 1464350655）。**若仍未生效的 ≠29-1**，如实报 Owner；若 Owner 已从接口测试控制台拿到服务地址（任务 3 前置），直接用。

### 任务 1：向 Owner 收集剩余 28 个接口的工作服务地址（Owner 已订未生效的根因）
平台 getApiDocument 返回的服务 ID 与订阅绑定的服务 ID 可能不一致（实例：环境气象预报 文档给 675294854=10001，实际绑定 1464350655=OK）。**Owner 操作**：打开接口测试控制台（应用详情→接口测试），接口列表下拉逐个选择，复制"请求地址"。AI 收到后入 SPECS。

### 任务 2：已生效接口建管线（能见度 1580458478 + 环境气象预报 1464350655 两个立即可建）
1. 字段结构已探明（fields_round2.json / probe 输出：能见度 7 字段、环境气象 27 字段）
2. 照抄 002 批次模板：DDL-as-Code（schemas/categories/market_alt_*.py，头部 BLUEPRINT/MODULE/INVARIANTS 七件套）→ business_data_categories.yaml 登记 → provider `_SZ_SINGLE_APIS` + 解析器 + `_SZ_OPEN_CAPS` → applier 三处接线 → tasks.yaml（daily_event 增量/静态 weekend）→ registry v1.9.x（DS/JOB/源）→ creation_token（插 creation_tokens 列表内，**勿 EOF 追加**——新 gate REGISTRY-YAML-PARSE 会拦）→ add_module_translation → depgraph --add-design-node → 测试 → apply DDL → 回补 → git_commit.py
3. 会话 id 建议：st-altdata-20260914 续用或新开

### 任务 3：Owner 交来服务地址后的批量接入（28 个）
统计月报 12 系列 → 现有 `alt_sz_stat_monthly` 长表**只加 `_SZ_STAT_SERIES` 元组**（解析器通用，列名容错已内建，raw JSON 无损兜底）；其余按表族并表模式（参照 alt_sz_port_monthly 3 系列并表先例）。

### 任务 4：回补纪律
- 全量拉取：incremental=False（provider 忽略 scheduler 的月初 start——这是修过的 bug，勿回退）
- 大表（能见度 2,456 万行/水库水位 7,630 万行）：**首刷限近期窗口（如 startDate=近 90 天）**，全史回补单独报批（预计亿级行数，落库前查磁盘）
- 回补后 FINAL 核数 + uniq 幂等键校验（同 002 批次姿势）

## 五、坑位清单（全部实弹踩过，勿重踩）

1. **订阅两层**：数据资源页订阅≠数据接口页订阅，只有接口页（toApiDetails）的订阅让 appKey 生效（errorCode 10001=未订阅）
2. **appKey 只用 .env 的主钥匙**：订阅管理页显示的其他 key 是误导（账号级绑定，实测旧钥匙通吃）
3. **getApiDocument 的 ctx 可能未绑定**：工作服务 ID 以接口测试控制台为准（任务 1）
4. **事件研究钳位伪影**：组合/序列起点前的事件必须显式剔除（2005-2018 事件全部钳到首日=每场 +4.81% 假象）
5. **基线敏感性必须报告**：日历月基线 vs 配对对照可差 10 倍（+1.2% vs +12%），单基线结论不可信
6. **_last_key 显式取日期列最大值**（排序末行≠最大日期）
7. **api_ctx 归一化**：补 `/1/service.xhtml` 后缀（403 元凶）；`import re` 勿漏（_port_row 用）
8. **CAS 文本哈希**：safe_write_text 的 expected_base_sha256 用 universal-newlines 文本读后 encode；WriteVerificationError 可能良性（写后验磁盘实态）；热文件必须带 base
9. **CRLF**：data_asset_registry 全 CRLF，写回用 `newline='\r\n'`；ENCODING-SAFETY 拦 double-CR
10. **提交链**：allow_overlap 5 次/24h 熔断后→重 claim+撤 flag 重提；PERM-TRIGGER 咬他会话 staged 文件→原子窗 unstage+同命令提交或 allow-tracked-drift；锁忙自动入队是正门（q-XXX done=落地）
11. **registry 撞号**：提交前 findall 全表重号核验（JOB/DS 撞号已发生两次：财报批占 095/232，我方让号 097/098/233）
12. **热文件并发**：tasks.yaml/categories 常被他改——Edit 报 modified-since-read 就重读重写；absorb 他会话 hunks 在 message 交底
13. **actor registry**：DS/JOB 的 code_symbol 用 `Class.method` 点号格式（裸方法名过不了 Anchor↔Code 门禁）
14. **TTL-METADATA**：docs/_working 的 md 要 `ttl: task_bound` frontmatter；带 module_id 的登记 YAML 要 `ttl: permanent`

## 六、完成定义（DoD）

47 接口全部可调且入管线（或明确豁免留痕）；全部回补并 FINAL 核数；registry/.categories/tasks/applier/测试五处同步；git_commit.py 落库且 `git log -1 --name-only` 归属核实；零临时文件残留于项目根；向 Owner 报告（大白话+判定依据）。
