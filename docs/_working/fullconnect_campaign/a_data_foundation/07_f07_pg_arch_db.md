---
ttl: task_bound
title: "F07 PG 架构库——depgraph 元数据底座（架构数据=DB）复飞案卷"
session: zc-l01-20260927
---

# F07 PG 架构库（复飞案卷，首次单独立卷）

> M1 册 03_ch_warehouse.md 仅在 D7 位置一段带过；本卷按总册职责独立立卷。PG 直连本日探针因凭据未走 secrets 通道失败（fe_sendauth），节点计数引用册面锚点并标注复跑方式。

## 一、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游 | 生成器族：scripts/governance/generate_project_depgraph.py（--force 重建）/extract_depgraph.py/apply_depgraph.py（--add-design-node 先登记后施工） |
| 下游 | 全部治理端（alignment_checklist 对齐键=module_id/step_id、R99 注册表校验、capability_lookup、chain_registry 真源 PG ig_chain 族、reconciler 链路） |
| 自动触发 | 无常驻（生成器 CLI+施工前登记制）；文件重命名后 MUST --force（宪法 §9.10，RENAME-DEPGRAPH-SYNC gate 硬拦） |
| 真源注册表 | postgresql://localhost:5432/depgraph（架构数据=DB 真源，宪法 RULE-SSOT：架构数据 apply_*.py 直写 DB）；ig_chain/ig_node/ig_edge 为 chain_registry.yaml（873 条机生）上游；REG-CROSS-002 跨模块依赖册→本库（L00 §二 B-15 判并入 F07） |
| 门禁质量尺 | HIGH drift pre-merge 阻断（RULE-DEPGRAPH/trae_080）；apply_depgraph 登记制；GATE-SRC-NO-DATA/GATE-SSOT-CODE 关联执法面（M5 census 列疑似判据失效 43 门内，治理侧账） |
| 运行状态 | **绿（引用锚点）**：M1 册记 9148 节点口径（2026-09-25）；generate_project_depgraph.py 在盘实核（scripts/governance/ 四件全家福）；chain_registry 生成器头注"真源: PG depgraph 库 ig_chain/ig_node/ig_edge"自证其在产（generated_at 2026-09-22） |

## 二、子模块三级枚举

1. 生成器族（scripts/governance/）：generate_project_depgraph.py/extract_depgraph.py/apply_depgraph.py/fix_depgraph_module_id.py
2. DB 对象：ig_node/ig_edge/ig_chain（DDL=scripts/industry_graph/apply_industry_graph_ddl.py）+depgraph_schema.py（governance/，get_depgraph_pg_connection :136）
3. 消费端：alignment_checklist/align_all.py 单入口；decision_map R99；capability_lookup；TDM module_ref 校验
4. 相邻新环（姊妹定版卷 L00 §二 B-9）：**F123 DB 迁移通道（P0）**——REG-MIGRATION-001 迁移册 276 行，判"F07 只写 depgraph 不含迁移纪律"，落 A 段 F07 邻位。本卷登记为带内相邻勘误：F07 卷语义边界不覆盖 schema 迁移，F123 立号前迁移面暂无环节归属（挂起）。

## 三、接线四态独立复核

- 总册：built/P2/D7。独立复核：**built 成立**（生成器在盘+ig_chain 供数 chain_registry 机生在产+对齐链路在用）。
- 复核留痕：本日 PG 直连探针失败（无密码供给，连接串不含凭据）——非故障证据，是凭据通道证据：连接须走 secrets.py 通道（RULE-SECRETS），节点数 9148 本卷未独立复测，标注"待复跑"进 §六命令。
- 勘误⑩：总册 F07 消费端列"全部治理端"无误，但漏列 F08 冷库域的 data_eng 相邻件（L00 D-02 判 F127 data_eng 与 F08 冷储存在交叠=姊妹定版卷自标勘误点）——F07 的 depgraph 必须收录 F127 域模块，否则新环落地即产生 drift 登记债。

## 四、缺口清单

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| D1 | 9148 节点数无本日独立复测（凭据通道） | 施工：走 secrets 通道复跑 §六命令，回填本卷 | P2 |
| D2 | F123 迁移通道缺位（迁移纪律无环节归属） | 挂起+解锁=裁-5 改写授权打包（L00 §二） | P0 |
| D3 | F127 data_eng 落地后的 depgraph 登记义务 | 施工：F123-F132 落号批随附 --add-design-node 登记 | P1 |
| D4 | depgraph drift 尺依赖 GATE-SRC-NO-DATA（列疑似判据失效 43 门） | 施工：红样采集（M5 43 门同批，治理侧主办） | P2 |

## 五、自审闸三态

挖干可施工（生成器/DDL/消费链 file:line 实核；节点数引用锚点已注明非独立复测）；D2=挂起 Owner 门（裁-5）；余可施工。首次单独立卷，无沿用。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
ls scripts/governance/ | grep depgraph   # 4 件全家福
head -8 docs/01_policies_and_standards/_registry/catalogs/chain_registry.yaml   # 真源自证
# 节点数（凭据走 secrets 通道后）：
python -c "
from zephyr.shared.security.secrets import get_secret
import psycopg
c=psycopg.connect(host='localhost',port=5432,dbname='depgraph',user=get_secret('PG_USER'),password=get_secret('PG_PASSWORD'))
cur=c.cursor(); cur.execute('SELECT count(*) FROM ig_node'); print('ig_node',cur.fetchone())"
```
