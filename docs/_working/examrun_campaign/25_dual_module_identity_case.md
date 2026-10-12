---
ttl: task_bound
title: 同一文件两个模块身份（zephyr.* 与 src.zephyr.*）——空 patch 隐患案卷（转判官域／维护线）
created: "2026-10-13"
sid: st-examrun-20261012
family_id: EXAMRUN-CAMPAIGN-20261012
---

# 一、现象（实测，一行可复算）

本仓 `src/` 目录在测试运行时位于 `sys.path` 上（`conftest`/`pytest` rootdir 注入），
于是同一个物理文件可以**以两个模块身份被导入**：

```
python -c "import importlib; a=importlib.import_module('zephyr.data.ch_writer');
           b=importlib.import_module('src.zephyr.data.ch_writer'); print(a is b, a.http_insert is b.http_insert)"
→ False False        # 同一文件 D:\ZephyrAlpha\src\zephyr\data\ch_writer.py，两个互不相干的模块对象
```

⇒ 对 `zephyr.data.ch_writer.http_insert` 的 patch **不会**影响 `src.zephyr.data.ch_writer.http_insert`，反之亦然。
命名空间包（`src/` 无 `__init__.py` 也能导入）是根因，不是配置意外。

# 二、影响面（本班尺，全量扫 `src`＋`scripts`＋`tests` 的 .py）

| 顶层目录 | 含 `import src.zephyr…` 的文件数 |
|---|---|
| `src/` | **0** |
| `scripts/` | **0** |
| `tests/` | **34**（全部落在 `tests/legacy_zephyr/**`） |

- 生产码与脚本面**只用一个身份**（`zephyr.*`），所以双身份目前只在遗留测试树里。
- 25 个 `tests/**/conftest.py` 里未出现对这些面的 `patch(...)`（自动 fixture 层不掺面）。
- **混面（导入一面、patch 另一面）当前实测 = 0**。

# 三、一次自我撤稿（诚实项，防后人照抄我的错）

本班初扫时用正则 `patch\(\s*["'](src\.)?zephyr` 把"patch 了生产面"的文件数算成 **2**
（`test_ch_writer.py`、`test_data_scheduler.py`）。逐行复核后**该数字作废**：
两文件都是 `from src.zephyr.data.…` ＋ `patch("src.zephyr.data.…")` **同面自洽**——
是我的正则把 `src.zephyr.` 也算进了"生产面"。修正后混面数＝**0**。
教训：判"混面"必须**两侧各自取面再求差集**，不能各用一个宽正则数命中（同族病见班账 §22.4／§25.9）。

# 四、危害模型（为什么现在 0 也要立项）

1. **空 patch＝真写生产库**：谁在 `tests/**` 里"导入 `zephyr.data.ch_writer`、却 patch `src.zephyr.data.ch_writer`"
   （或反向），mock 静默无效——`write_tsv("c1_market.kline_daily", …)`／`delete_where(...)` 会**打到真库**。
   遗留树里已有这种调用形（`tests/legacy_zephyr/data/test_ch_writer.py` 内**直调写口共 7 处**，
   行号 160／167／175／197／291／304 等，含 `write_tsv("c1_market.kline_daily", …)` 与
   `delete_where("c1_market.kline_daily", "date = '2026-07-05'")`），
   今天靠同面自洽才没出事 ⇒ **距离一次生产写事故只差一次复制粘贴**。
2. **模块级状态双份**：`_ch_lock`、HTTP host 失效位、连接/查询缓存、阈值常量各存一份 ⇒
   跨面调用时锁不互斥、失效位不共享，故障表现会"不可复现"。
3. 与本班 CH 破口同族：那次是"测试头自述 vs 真行为"，这次是"patch 面 vs 生效面"——**都是自述类安全声明不被验证**。

# 五、建议两道（归属：判官域／维护线，本班不代改）

- **甲（便宜、先上）静态 lint 或 commit 闸**：对 `tests/**` 逐文件取
  ①导入面集合（`from|import (src\.)?zephyr\.`）②`patch("…zephyr.*"` 的面集合，
  **两侧差集非空即红**；命中信息给出该文件的具体两面。零运行时成本，能挡住"复制粘贴引入混面"。
- **乙（治本）在 `tests/conftest.py` 做 collector-time 断言**：禁止生产包以 `src.` 前缀被导入
  （例如把 `src.zephyr` 加入导入黑名单或在收集阶段断言
  `not any(m.startswith("src.zephyr.") for m in sys.modules)`），
  让"第二个身份"根本无法出现 ⇒ 一旦混面即刻 ImportError 而非静默。
  注意：这会**打红 34 个遗留测试**（全在 `tests/legacy_zephyr/`），需配套一次性改面
  （`src.zephyr.` → `zephyr.`，属机械改名，但**属主是数据域遗留树**，须其班次做，勿由闸侧硬改）。
- 归档关联：与统筹指示的 **CH/PG 双库写口沙箱化**同族（都是"测试与生产共用同一入口而无人验证隔离"），
  建议同一批次实施，护栏一次到位。

# 六、验收法（给实施班）

1. 复算本件二/三节两张表（命令照抄即可）；
2. 甲闸上线后**反向自证**：造一个混面样本文件（一面导入、另一面 patch），闸必须红；
   再把样本改成同面，闸必须绿——不红即白；
3. 乙上线后再跑 `tests/legacy_zephyr/data/test_ch_writer.py` 全目录一次，
   跑前跑后各取 `system.query_log` 中 `c1_market.kline_daily` 的 INSERT/DELETE 计数，**必须都是 0**（这才算证伪"会写库"）。

出处：班账 `docs/_working/examrun_campaign/00_ledger.md` §卅四；
同族案卷 `docs/_working/examrun_campaign/22_landing_test_isolation_dossier.md`、名单 `23_ch_writing_test_nodeids.md`。
