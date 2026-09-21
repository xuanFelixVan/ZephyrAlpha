---
ttl: task_bound
title: W4-1 290 条无传导边链三分法定性+墓碑链终裁材料
owner: st-final3-20260919
created: 2026-09-19
---

# W4-1 290 条无传导边链三分法定性 + 墓碑链终裁材料

- 日期：2026-09-19｜会话：st-final3-20260919｜性质：final3 战役 W4 全景图捋顺（00_master_directive.md §W4-1）
- 纪律：PG 只读连接（`get_depgraph_pg_connection(read_only=True)`），零 UPDATE/DELETE；墓碑链只列不删，处置=Owner 门位（本文仅备料）
- 证据等级：**A 级=SQL 直查 PG 实测**（口径已复现 583/290，见 §1）；定性判据与 merged_into 解析为规则化推导（B 级）

## 1. 数据基线与覆盖口径

| 项 | 值 | 备注 |
|---|---|---|
| ig_chain 总链数 | 873 | 实测 |
| 被覆盖链（有链内传导边） | 583 | 实测，口径见下 |
| 无传导边链 | **290** | 873-583，本文对象 |
| 活跃传导边 | 1253 | structure 1005 + supply 212 + supplies_to 36 |
| ig_node | 5560 | 活跃 4742 + 盖戳失效 818 |
| ig_io_edge | 16859 | **sector 级**（from/to_sector），无 node_id，不参与链定性 |

覆盖判定 canonical 口径（复现 583/290，与任务硬事实一致）：**链被覆盖 ⇔ 存在链内传导边（ig_edge 两端节点同属该链，不限 valid_to）**：

```sql
SELECT count(DISTINCT a.chain_id) FROM ig_node a
JOIN ig_edge e ON e.from_node = a.node_id
JOIN ig_node b ON b.node_id = e.to_node AND b.chain_id = a.chain_id;  -- = 583
```

注意：跨链传导边（两端分属两链）**不**计入本链覆盖；链内边含已盖 `valid_to` 的失效边。

## 2. 三分法总表

| 类 | 判据 | 计数 | 处置 |
|---|---|---|---|
| A1 显性墓碑 | status∈{deprecated,…} 或 source_note/name 含墓碑标记（merged_into/废弃/停用/僵尸/分流） | **135** | 列清单禁删；状态翻转/补 merged_into=Owner 门位 |
| A2 隐性墓碑 | status 仍 active 但零节点（空壳登记） | **2** | 同上，建议补标 deprecated |
| B 新入库未补边 | 活链且存在可锚定上游/同位候选（同名/别名节点已在被覆盖链） | **5** | 可补边建议见 §4 |
| C 上游断供 | 活链但无可锚定候选、无跨链边（源数据缺边信息） | **148** | 数据债登记见 §5 |
| 合计 | | **290** | = 290 ✓ |

根因：新链入库无"至少 1 条链内传导边才算活链"强制卡（W4-3 另立项，判据建议见 §6）。

## 3. A 类墓碑链清单（终裁材料）

### 3.1 A1 显性墓碑（135 条）

- status='deprecated'：123 条；status='active' 但带墓碑标记：12 条（详见 3.2）
- 带 merged_into 指针：131/135 条；缺指针 4 条（其中 4 条为 S24 僵尸链分流治理标记）
- 规模分布（活跃节点数）：1 节点 34 条｜2 节点 39 条｜3 节点 56 条｜≥12 节点 5 条（见 3.3）｜0 节点 1 条

| chain_id | 名称 | status | 活跃/总节点 | merged_into | 创建日 | source_note |
|---|---|---|---|---|---|---|
| CH-04f1a263078d | 互联网行业：AI产业链剖析，阵营分化谁能笑到最后 | deprecated | 2/2 | CH-1a1ed46a4a8f（AI产业链行业系列） | 2026-08-28 | p3a_auto \| merged_into:CH-1a1ed46a4a8f |
| CH-0597d457a07f | 智驾SoC芯片 | deprecated | 1/1 | CH-2e115b2541ee（算力芯片） | 2026-08-28 | p3a_auto \| merged_into:CH-2e115b2541ee |
| CH-06c9bb15ca4f | G用均热板行业 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-0955b49c527b | 自研垂直大模型及海量数据打造壁垒，知识 | deprecated | 2/2 | CH-1b61bdf99d16（人工智能场景化） | 2026-08-28 | p3a_auto \| merged_into:CH-1b61bdf99d16 |
| CH-0fdcd634f2c0 | 产业赛道与主题投资风向标：AI Agent投资 | deprecated | 3/3 | CH-b4124ec6adeb（AI Agent智能体） | 2026-08-28 | p3a_auto \| merged_into:CH-b4124ec6adeb |
| CH-10bfbb6b1730 | 天然气产业链介绍（三）——中国天然气市场概况 | deprecated | 2/2 | CH-50e7fe4d6fe6（天然气产业链） | 2026-08-28 | p3a_auto \| merged_into:CH-50e7fe4d6fe6 |
| CH-16ccd51d2de7 | 手术机器人 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-18dd42b5777d | 唐山地区黑色产业链调研（四 | deprecated | 1/1 | CH-8d1ff75d3b2d（黑色产业链） | 2026-08-28 | p3a_auto \| merged_into:CH-8d1ff75d3b2d |
| CH-1c985697669c | 跨境资产配置产业链系列 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-1cbdc043ddee | GLP_1赛道全解析，研发 | deprecated | 1/1 | CH-ed86e3ffe203（GLP_1） | 2026-08-28 | p3a_auto \| merged_into:CH-ed86e3ffe203 |
| CH-1e02a03c21b3 | 版全球与中国中成药产业供需贸易 | deprecated | 1/1 | CH-af8032c399eb（中国中药行业） | 2026-08-28 | p3a_auto \| merged_into:CH-af8032c399eb |
| CH-1f17fa27f86b | 呼吸行业 | deprecated | 3/3 | CH-eb2765cf5239（化学制药行业） | 2026-08-28 | p3a_auto \| merged_into:CH-eb2765cf5239 |
| CH-1fef6586f473 | 中国AIGC应用 | deprecated | 3/3 | CH-adaf10e10aff（文化传媒行业） | 2026-08-28 | p3a_auto \| merged_into:CH-adaf10e10aff |
| CH-231baee4219a | 全球AI应用平台市场 | deprecated | 1/1 | CH-1b61bdf99d16（人工智能场景化） | 2026-08-28 | p3a_auto \| merged_into:CH-1b61bdf99d16 |
| CH-23f40fea2741 | 超节点 | deprecated | 3/3 | CH-00607d464e8f（通信设备行业） | 2026-08-28 | p3a_auto \| merged_into:CH-00607d464e8f |
| CH-257e21df0c79 | 东南亚餐饮 | deprecated | 1/1 | CH-1c61d83340d6（其他社会服务行业） | 2026-08-28 | p3a_auto \| merged_into:CH-1c61d83340d6 |
| CH-2a9513c31962 | AI行业2026阿里妈妈产品 | deprecated | 1/1 | CH-adaf10e10aff（文化传媒行业） | 2026-08-28 | p3a_auto \| merged_into:CH-adaf10e10aff |
| CH-2be46f46091a | 电力电子产业链 | deprecated | 2/2 | CH-5a976fef25de（电网设备行业） | 2026-08-28 | p3a_auto \| merged_into:CH-5a976fef25de |
| CH-2d53b6777ffb | 从传统模式到精准医疗：中美六大癌症治疗标准十年演进 | deprecated | 2/2 | CH-eb2765cf5239（化学制药行业） | 2026-08-28 | p3a_auto \| merged_into:CH-eb2765cf5239 |
| CH-307b0c490447 | Meta智能眼镜产品深度解析：技术、生态与商业化 | deprecated | 3/3 | CH-5eef6079252e（AI眼镜） | 2026-08-28 | p3a_auto \| merged_into:CH-5eef6079252e |
| CH-30e20ff0523c | 橡胶产业链概况及套利交易模式 | deprecated | 2/2 | CH-d7bf2f0ca48d（橡胶） | 2026-08-28 | p3a_auto \| merged_into:CH-d7bf2f0ca48d |
| CH-32de53f7a776 | 骨科材料及骨科医疗器械市场 | deprecated | 2/2 | CH-0bbecb582893（骨科行业） | 2026-08-28 | p3a_auto \| merged_into:CH-0bbecb582893 |
| CH-37c07858e656 | 海洋新材料行业 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-38f87926216f | 纳米纤维材料行业 | deprecated | 3/3 | CH-464f524130fa（绿色甲醇） | 2026-08-28 | p3a_auto \| merged_into:CH-464f524130fa |
| CH-3b995a96388b | 端侧AI | deprecated | 2/2 | CH-db242c748ae2（中国端侧AI） | 2026-08-28 | p3a_auto \| merged_into:CH-db242c748ae2 |
| CH-3d3c25fb2d4d | 一张图看懂手机陶瓷外壳产业链 | deprecated | 3/3 | CH-c84f7fdc58a6（手机外壳） | 2026-08-28 | p3a_auto \| merged_into:CH-c84f7fdc58a6 |
| CH-3e4893806935 | 工业基础材料行业基建投资 | deprecated | 3/3 | CH-2f0b74dae1a4（基建投资） | 2026-08-28 | p3a_auto \| merged_into:CH-2f0b74dae1a4 |
| CH-464f524130fa | 绿色甲醇 | deprecated | 3/3 | CH-4673d5804561（建筑装饰行业） | 2026-08-28 | p3a_auto \| merged_into:CH-4673d5804561 |
| CH-4a0cee1bf95a | 超全MIM | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-4b13e1110dca | 商业航天行业产业链 | deprecated | 1/1 | CH-3be4e01f6112（商业航天） | 2026-08-28 | p3a_auto \| merged_into:CH-3be4e01f6112 |
| CH-4d2ed2374041 | 从“药明系”看创新药产业链的经营趋势 | deprecated | 3/3 | CH-2934ea0c9c75（创新药） | 2026-08-28 | p3a_auto \| merged_into:CH-2934ea0c9c75 |
| CH-4db6fed69f79 | 富士达创远信科等北证4家产业链布局全 | deprecated | 3/3 | CH-acd01c39edc8（AI算力上游材料） | 2026-08-28 | p3a_auto \| merged_into:CH-acd01c39edc8 |
| CH-4dd7639ef2cf | NeoCloud（新兴云）商业模式与业绩深度剖析 | deprecated | 3/3 | CH-f510e9e13c1a（算力租赁） | 2026-08-28 | p3a_auto \| merged_into:CH-f510e9e13c1a |
| CH-50488ea1d0af | 半导体硅材料行业 | deprecated | 3/3 | CH-c4902e175ffb（半导体材料产业链） | 2026-08-28 | merged_into:CH-c4902e175ffb |
| CH-507e0b34d6b2 | 抖音八大宠物心智人群 | deprecated | 2/2 | CH-b943b2a47f94（油脂油料） | 2026-08-28 | p3a_auto \| merged_into:CH-b943b2a47f94 |
| CH-509ad59a1381 | 中国企业出海数据合规服务商 | deprecated | 2/2 | CH-1b61bdf99d16（人工智能场景化） | 2026-08-28 | p3a_auto \| merged_into:CH-1b61bdf99d16 |
| CH-50e7fe4d6fe6 | 天然气产业链 | deprecated | 3/3 | CH-e8111d5fafa7（钢铁行业） | 2026-08-28 | p3a_auto \| merged_into:CH-e8111d5fafa7 |
| CH-51adeab8350e | 东南亚新能源 | deprecated | 1/1 | CH-5a976fef25de（电网设备行业） | 2026-08-28 | p3a_auto \| merged_into:CH-5a976fef25de |
| CH-56a5d2e555d5 | 机构行为 | deprecated | 1/1 | CH-234a92ef7584（可转债） | 2026-08-28 | p3a_auto \| merged_into:CH-234a92ef7584 |
| CH-58f941907cd9 | 全球棉纺产业链进出口格局 | deprecated | 2/2 | CH-2b0421bd2a17（服装家纺行业） | 2026-08-28 | p3a_auto \| merged_into:CH-2b0421bd2a17 |
| CH-5d3e1c0bdb5d | Agent厂商 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-5dd1566bb800 | 一张图看懂偏光片产业 | deprecated | 2/2 | CH-f78fdf089b56（偏光片行业） | 2026-08-28 | p3a_auto \| merged_into:CH-f78fdf089b56 |
| CH-6275b8b6889e | 全球新兴经济体 | deprecated | 1/1 | CH-234a92ef7584（可转债） | 2026-08-28 | p3a_auto \| merged_into:CH-234a92ef7584 |
| CH-63999aeb966c | 北交所科技产业 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-640c8a8005ca | 洗衣机 | active | 14/22 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-645c4ae97d4b | 中国储能行业出口 | deprecated | 2/2 | CH-5a976fef25de（电网设备行业） | 2026-08-28 | p3a_auto \| merged_into:CH-5a976fef25de |
| CH-662348e16edb | 生育 | deprecated | 1/1 | CH-eb2765cf5239（化学制药行业） | 2026-08-28 | p3a_auto \| merged_into:CH-eb2765cf5239 |
| CH-662e728b76ab | 智慧旅游产业链 | active | 0/2 | CH-1c61d83340d6（其他社会服务行业） | 2026-08-28 | p3a_auto \| merged_into:CH-1c61d83340d6 |
| CH-6a52df446f58 | smart beta配置系列之三：质量类指数 | deprecated | 3/3 | CH-acd01c39edc8（AI算力上游材料） | 2026-08-28 | p3a_auto \| merged_into:CH-acd01c39edc8 \| merged_into:CH-ec1fdb66a48e |
| CH-6a8a872f9570 | 医药冷链行业供应链发展 | deprecated | 3/3 | CH-eb2765cf5239（化学制药行业） | 2026-08-28 | p3a_auto \| merged_into:CH-eb2765cf5239 |
| CH-6b80d642bb80 | 知识 | deprecated | 2/2 | CH-234a92ef7584（可转债） | 2026-08-28 | p3a_auto \| merged_into:CH-234a92ef7584 |
| CH-6dde36dc203a | 算力基础设施 | deprecated | 2/2 | CH-134de3632513（计算机设备行业） | 2026-08-28 | p3a_auto \| merged_into:CH-134de3632513 |
| CH-7194568b42a5 | 光纤产业链 | deprecated | 3/3 | CH-71b352cc3490（军工电子行业） | 2026-08-28 | p3a_auto \| merged_into:CH-71b352cc3490 |
| CH-7201aad7e1ac | 无人叉车 | deprecated | 3/3 | CH-2555b2c62876（工程机械行业） | 2026-08-28 | p3a_auto \| merged_into:CH-2555b2c62876 |
| CH-724ee6219fdb | 全球海洋物理AI行业市场 | deprecated | 2/2 | CH-1b61bdf99d16（人工智能场景化） | 2026-08-28 | p3a_auto \| merged_into:CH-1b61bdf99d16 |
| CH-74751b41769b | 我国就业市场 | deprecated | 2/2 | CH-234a92ef7584（可转债） | 2026-08-28 | p3a_auto \| merged_into:CH-234a92ef7584 |
| CH-748d8e598f29 | 小红书商业产品 | deprecated | 2/2 | CH-f510e9e13c1a（算力租赁） | 2026-08-28 | p3a_auto \| merged_into:CH-f510e9e13c1a |
| CH-7874e5e3429f | 特斯拉modelX | deprecated | 1/1 | CH-9042f765fc5f（汽车零部件行业） | 2026-08-28 | p3a_auto \| merged_into:CH-9042f765fc5f |
| CH-78ac88845fcc | 8大岗位AI技能 | deprecated | 2/2 | CH-234a92ef7584（可转债） | 2026-08-28 | p3a_auto \| merged_into:CH-234a92ef7584 |
| CH-79e9c07d533e | 一季度全国信用债增信市场与主体 | deprecated | 1/1 | CH-acd01c39edc8（AI算力上游材料） | 2026-08-28 | p3a_auto \| merged_into:CH-acd01c39edc8 |
| CH-7d99e8d2be2a | OTA产业链 | deprecated | 3/3 | CH-379e68a0e8a1（机场航运行业） | 2026-08-28 | p3a_auto \| merged_into:CH-379e68a0e8a1 |
| CH-80c60fdd4586 | 金属表面处理 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-82232182a27f | 伺服电机 | active | 4/4 | CH-a2e61f87f470（自动化设备行业） | 2026-08-28 | p3a_auto \| merged_into:CH-a2e61f87f470 |
| CH-84ca24dfc4ff | 中国新能源智能汽车行业产业链出海 | deprecated | 1/1 | CH-978b571438e5（新能源汽车） | 2026-08-28 | p3a_auto \| merged_into:CH-978b571438e5 |
| CH-878507c7675c | 中国AI应用行业 | deprecated | 2/2 | CH-fe3c659bf7cd（中国AI应用） | 2026-08-28 | p3a_auto \| merged_into:CH-fe3c659bf7cd |
| CH-886c7ab4fd51 | 铝基复合材料产业链 | deprecated | 3/3 | CH-85cb0ea8b49f（能源金属产业） | 2026-08-28 | p3a_auto \| merged_into:CH-85cb0ea8b49f |
| CH-891cc6f7ef54 | 史上最全膜 | deprecated | 2/2 | CH-4e3d6cd09ceb（反渗透膜行业） | 2026-08-28 | p3a_auto \| merged_into:CH-4e3d6cd09ceb |
| CH-8964ce0a04bb | 中国新能源汽车全产业链数据 | deprecated | 2/2 | CH-978b571438e5（新能源汽车） | 2026-08-28 | p3a_auto \| merged_into:CH-978b571438e5 |
| CH-8d1ff75d3b2d | 黑色产业链 | deprecated | 1/1 | CH-e8111d5fafa7（钢铁行业） | 2026-08-28 | p3a_auto \| merged_into:CH-e8111d5fafa7 |
| CH-8d85c64777ee | 电生理行业 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-8d99e6710cd3 | 医疗行业 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-924fe5772f3f | 2026年短剧内容消费偏好 | deprecated | 1/1 | CH-adaf10e10aff（文化传媒行业） | 2026-08-28 | p3a_auto \| merged_into:CH-adaf10e10aff |
| CH-936371ba62dc | G用热管行业 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-948d2c0d6de6 | 金融消费行业趋势 | deprecated | 3/3 | CH-ad2ec6f7d1d8（证券行业） | 2026-08-28 | p3a_auto \| merged_into:CH-ad2ec6f7d1d8 |
| CH-95cbab5d2ed5 | 中国企业AI工具生态 | deprecated | 2/2 | CH-1b61bdf99d16（人工智能场景化） | 2026-08-28 | p3a_auto \| merged_into:CH-1b61bdf99d16 |
| CH-96a81f7fba78 | 中国餐饮市场 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-9851fa217103 | 富勒烯调研 | deprecated | 3/3 | CH-3e13b1b29bb0（化学制品行业） | 2026-08-28 | p3a_auto \| merged_into:CH-3e13b1b29bb0 |
| CH-9b303fec9f01 | 合成橡胶产业链 | active | 2/3 | CH-3e13b1b29bb0（化学制品行业） | 2026-08-28 | p3a_auto \| merged_into:CH-3e13b1b29bb0 \| merged_into:CH-0fd528e459dd |
| CH-9b561eb06183 | 处方药销售 | deprecated | 1/1 | CH-eb2765cf5239（化学制药行业） | 2026-08-28 | p3a_auto \| merged_into:CH-eb2765cf5239 |
| CH-9cc3cf7800b1 | 一张图看懂微创医疗 | deprecated | 2/2 | CH-eb2765cf5239（化学制药行业） | 2026-08-28 | p3a_auto \| merged_into:CH-eb2765cf5239 |
| CH-9ccfdb055645 | 医用钛合金行业市场 | deprecated | 2/2 | CH-7e9cbc35d2ab（医用钛合金行业） | 2026-08-28 | p3a_auto \| merged_into:CH-7e9cbc35d2ab |
| CH-9e01659ccc1a | 深研系列（四）：全球智能投顾 | deprecated | 1/1 | CH-acd01c39edc8（AI算力上游材料） | 2026-08-28 | p3a_auto \| merged_into:CH-acd01c39edc8 |
| CH-9ede6a228867 | 洁净室 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-9f9d36327d96 | 手机 | deprecated | 3/3 | CH-a175f5a492e6（光学光电子行业） | 2026-08-28 | p3a_auto \| merged_into:CH-a175f5a492e6 |
| CH-a5fb09ff4d5c | 智启万物-全球AI应用平台市场 | deprecated | 1/1 | CH-231baee4219a（全球AI应用平台市场） | 2026-08-28 | p3a_auto \| merged_into:CH-231baee4219a |
| CH-acea20811781 | 冰箱 | active | 20/34 | CH-a175f5a492e6（光学光电子行业） | 2026-08-28 | p3a_auto \| merged_into:CH-a175f5a492e6 |
| CH-b007bac27170 | 中国对美出口产业链期货品种 | deprecated | 3/3 | CH-acd01c39edc8（AI算力上游材料） | 2026-08-28 | p3a_auto \| merged_into:CH-acd01c39edc8 |
| CH-b3ce5016ad8e | 核电材料行业 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-b42d72c11346 | 医药行业2025年10月处方药销售 | deprecated | 2/2 | CH-9b561eb06183（处方药销售） | 2026-08-28 | p3a_auto \| merged_into:CH-9b561eb06183 |
| CH-b642af974b64 | 从碎片到体系：供应链管理知识 | deprecated | 1/1 | CH-acd01c39edc8（AI算力上游材料） | 2026-08-28 | p3a_auto \| merged_into:CH-acd01c39edc8 |
| CH-b81468a2268f | 中国茶饮咖啡数据 | deprecated | 1/1 | CH-b4253bc8a577（食品加工制造行业） | 2026-08-28 | p3a_auto \| merged_into:CH-b4253bc8a577 |
| CH-ba0b7f2c25ba | 中国铜加工新材料发展和应用 | deprecated | 3/3 | CH-0c51b79476e3（铜和铜合金行业） | 2026-08-28 | p3a_auto \| merged_into:CH-0c51b79476e3 |
| CH-bc34af48d487 | 玻璃表面处理链 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-bd9537f9f5c8 | 行业链 | deprecated | 3/3 | CH-201086b060df（房地产行业） | 2026-08-28 | p3a_auto \| merged_into:CH-201086b060df |
| CH-c0c139446e8f | 医疗器械 | active | 93/95 | CH-d4f3ad7fc942（医疗器械行业） | 2026-08-28 | p3a_auto \| merged_into:CH-d4f3ad7fc942 |
| CH-c460c51fc7c8 | 中国新生代群体 | deprecated | 1/1 | CH-234a92ef7584（可转债） | 2026-08-28 | p3a_auto \| merged_into:CH-234a92ef7584 |
| CH-c84f7fdc58a6 | 手机外壳 | deprecated | 3/3 | CH-b97ffc1a1f77（通用设备行业） | 2026-08-28 | p3a_auto \| merged_into:CH-b97ffc1a1f77 |
| CH-d12b589118d1 | 机构行为100篇（一）：可转债市场机构行为 | deprecated | 1/1 | CH-acd01c39edc8（AI算力上游材料） | 2026-08-28 | p3a_auto \| merged_into:CH-acd01c39edc8 |
| CH-d197221efe50 | 中国旅客出境游：人群调研及 | deprecated | 1/1 | CH-1c61d83340d6（其他社会服务行业） | 2026-08-28 | p3a_auto \| merged_into:CH-1c61d83340d6 |
| CH-d1c519da7588 | 前沿科技与产业趋势 | deprecated | 2/2 | CH-234a92ef7584（可转债） | 2026-08-28 | p3a_auto \| merged_into:CH-234a92ef7584 |
| CH-d42d9b958f93 | 汽车尾气催化剂行业 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-d4c38977656e | 家居 | deprecated | 3/3 | CH-a175f5a492e6（光学光电子行业） | 2026-08-28 | p3a_auto \| merged_into:CH-a175f5a492e6 |
| CH-d54945f6b459 | 碳纳米管材料市场 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 \| merged_into:CH-99056d106545 |
| CH-d9434b7d0f66 | 中国金融机构人才发展与培训 | deprecated | 2/2 | CH-acd01c39edc8（AI算力上游材料） | 2026-08-28 | p3a_auto \| merged_into:CH-acd01c39edc8 |
| CH-d9b0103e7403 | 电子陶瓷 | deprecated | 2/2 | CH-184e5d57e8e8（电子陶瓷行业） | 2026-08-28 | p3a_auto \| merged_into:CH-184e5d57e8e8 |
| CH-d9b746e06a50 | 金融机构AI应用 | deprecated | 2/2 | CH-ad2ec6f7d1d8（证券行业） | 2026-08-28 | p3a_auto \| merged_into:CH-ad2ec6f7d1d8 |
| CH-d9f7d079b8ef | 一张图看懂医用钛合金行业 | deprecated | 2/2 | CH-7e9cbc35d2ab（医用钛合金行业） | 2026-08-28 | p3a_auto \| merged_into:CH-7e9cbc35d2ab |
| CH-dc3a6c32f5a8 | IC | deprecated | 3/3 | CH-74af4f035d18（半导体产业链） | 2026-08-28 | p3a_auto \| merged_into:CH-74af4f035d18 |
| CH-dc969427acc7 | 天然气产业链介绍（四）——天然气衍生品 | deprecated | 2/2 | CH-50e7fe4d6fe6（天然气产业链） | 2026-08-28 | p3a_auto \| merged_into:CH-50e7fe4d6fe6 |
| CH-dec7228c7be9 | 刀具 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-ded2d2837efe | 神经介入行业 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-df3e009efcac | 陶瓷表面处理 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-e1e73f8c9d52 | 中国风味 | deprecated | 1/1 | CH-b4253bc8a577（食品加工制造行业） | 2026-08-28 | p3a_auto \| merged_into:CH-b4253bc8a577 |
| CH-e2a4a45d5bf4 | 功能食品行业消费者 | deprecated | 1/1 | CH-b4253bc8a577（食品加工制造行业） | 2026-08-28 | p3a_auto \| merged_into:CH-b4253bc8a577 |
| CH-e564789e266c | 全球创新药临床试验十年趋势 | deprecated | 1/1 | CH-eb2765cf5239（化学制药行业） | 2026-08-28 | p3a_auto \| merged_into:CH-eb2765cf5239 |
| CH-e8468ad2acaf | “反内卷”之风对聚酯产业链的影响 | deprecated | 2/2 | CH-1319d5204b88（聚酯产业链） | 2026-08-28 | p3a_auto \| merged_into:CH-1319d5204b88 |
| CH-e8884580822e | IAA消除类小游戏玩家群体行为趋势 | deprecated | 3/3 | CH-aeb3418ba358（游戏行业应用） | 2026-08-28 | p3a_auto \| merged_into:CH-aeb3418ba358 |
| CH-ec19d2faf656 | 教育行业智慧校园电气应用方案 | deprecated | 3/3 | CH-86e02ad60c16（光伏） | 2026-08-28 | p3a_auto \| merged_into:CH-86e02ad60c16 |
| CH-ec1fdb66a48e | smartbeta配置系列之三：质量类指数 | deprecated | 3/3 | CH-acd01c39edc8（AI算力上游材料） | 2026-08-28 | p3a_auto \| merged_into:CH-acd01c39edc8 |
| CH-ed85ccfc3eb3 | 一张图看懂硬质合金 | deprecated | 2/2 | CH-dd477c435dfe（硬质合金行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dd477c435dfe |
| CH-eda9e140b2fc | 法国深度技术 | deprecated | 2/2 | CH-acd01c39edc8（AI算力上游材料） | 2026-08-28 | p3a_auto \| merged_into:CH-acd01c39edc8 |
| CH-ee525ef23878 | AI化工 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-ef8a9f751393 | 虚拟现实（VR） | deprecated | 3/3 | CH-bae090703b15（半导体行业） | 2026-08-28 | p3a_auto \| merged_into:CH-bae090703b15 |
| CH-f0a4862a36dc | 唐山、天津地区黑色产业链调研（二 | deprecated | 1/1 | CH-8d1ff75d3b2d（黑色产业链） | 2026-08-28 | p3a_auto \| merged_into:CH-8d1ff75d3b2d |
| CH-f396c5043207 | 智能汽车产品功能 | deprecated | 1/1 | CH-9042f765fc5f（汽车零部件行业） | 2026-08-28 | p3a_auto \| merged_into:CH-9042f765fc5f |
| CH-f83ee26025d3 | 全球及中国印刷油墨产业供需贸易 | deprecated | 2/2 | CH-01c14183c4e0（油墨行业） | 2026-08-28 | p3a_auto \| merged_into:CH-01c14183c4e0 |
| CH-f96046bdad43 | 塑料表面处理 | deprecated | 3/3 | CH-dc6473ac96a7（综合行业） | 2026-08-28 | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-fb48c9fdc350 | 中国模具及模具材料市场和应用 调研 | deprecated | 3/3 | CH-75c6002562ac（模具） | 2026-08-28 | p3a_auto \| merged_into:CH-75c6002562ac |
| CH-fee44951b730 | AI+厨电行业趋势 | deprecated | 2/2 | CH-36b687566485（家电产业链） | 2026-08-28 | p3a_auto \| merged_into:CH-36b687566485 |
| CH-3757654c9547 | 建筑材料行业 | active | 1/1 |  | 2026-09-11 | 治理\|S24僵尸链分流 批B\|2026-09-11 |
| CH-81ef6769096e | 电池行业 | active | 1/1 |  | 2026-09-11 | 治理\|S24僵尸链分流 批B\|2026-09-11 |
| CH-d412836999f5 | 电机行业 | active | 1/1 |  | 2026-09-11 | 治理\|S24僵尸链分流 批B\|2026-09-11 |
| CH-c9446551840c | 贵金属行业 | active | 1/1 |  | 2026-09-11 | 治理\|S24僵尸链分流 批B\|2026-09-11 |
| CH-265aa1aac920 | 铝电解电容器产业链 | active | 2/2 | CH-dc6473ac96a7（综合行业） | 2026-09-11 | 治理\|S24僵尸链分流 批B\|2026-09-11 \| merged_into:CH-dc6473ac96a7 \| merged_i… |
| CH-9f5646045956 | 充电桩产业链 | active | 12/12 | CH-5a976fef25de（电网设备行业） | 2026-09-11 | 治理\|S24僵尸链分流 批C冗余落位收缩\|2026-09-11 \| merged_into:CH-5a976fef25de |

### 3.2 A1 中 status='active' 的 12 条（状态翻转候选——Owner 门位）

墓碑语义已由 source_note 承载但 status 未翻转，属状态字段与事实不一致，建议 Owner 裁定后统一翻转 deprecated：

| chain_id | 名称 | 标记类型 | source_note 摘要 |
|---|---|---|---|
| CH-640c8a8005ca | 洗衣机 | merged_into | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-662e728b76ab | 智慧旅游产业链 | merged_into | p3a_auto \| merged_into:CH-1c61d83340d6 |
| CH-82232182a27f | 伺服电机 | merged_into | p3a_auto \| merged_into:CH-a2e61f87f470 |
| CH-9b303fec9f01 | 合成橡胶产业链 | merged_into | p3a_auto \| merged_into:CH-3e13b1b29bb0 \| merged_into:CH-0fd528e459dd |
| CH-acea20811781 | 冰箱 | merged_into | p3a_auto \| merged_into:CH-a175f5a492e6 |
| CH-c0c139446e8f | 医疗器械 | merged_into | p3a_auto \| merged_into:CH-d4f3ad7fc942 |
| CH-3757654c9547 | 建筑材料行业 | S24 分流治理标记 | 治理\|S24僵尸链分流 批B\|2026-09-11 |
| CH-81ef6769096e | 电池行业 | S24 分流治理标记 | 治理\|S24僵尸链分流 批B\|2026-09-11 |
| CH-d412836999f5 | 电机行业 | S24 分流治理标记 | 治理\|S24僵尸链分流 批B\|2026-09-11 |
| CH-c9446551840c | 贵金属行业 | S24 分流治理标记 | 治理\|S24僵尸链分流 批B\|2026-09-11 |
| CH-265aa1aac920 | 铝电解电容器产业链 | merged_into | 治理\|S24僵尸链分流 批B\|2026-09-11 \| merged_into:CH-dc6473ac96a7 \| merged_into:CH-a3b… |
| CH-9f5646045956 | 充电桩产业链 | merged_into | 治理\|S24僵尸链分流 批C冗余落位收缩\|2026-09-11 \| merged_into:CH-5a976fef25de |

### 3.3 大型墓碑（活跃节点 ≥12，删并影响面大，重点复核）

| chain_id | 名称 | 活跃/总节点 | merged_into | source_note 摘要 |
|---|---|---|---|---|
| CH-c0c139446e8f | 医疗器械 | 93/95 | CH-d4f3ad7fc942（医疗器械行业） | p3a_auto \| merged_into:CH-d4f3ad7fc942 |
| CH-acea20811781 | 冰箱 | 20/34 | CH-a175f5a492e6（光学光电子行业） | p3a_auto \| merged_into:CH-a175f5a492e6 |
| CH-640c8a8005ca | 洗衣机 | 14/22 | CH-dc6473ac96a7（综合行业） | p3a_auto \| merged_into:CH-dc6473ac96a7 |
| CH-9f5646045956 | 充电桩产业链 | 12/12 | CH-5a976fef25de（电网设备行业） | 治理\|S24僵尸链分流 批C冗余落位收缩\|2026-09-11 \| merged_into:CH-5a976fef… |

### 3.4 A2 隐性墓碑（2 条，空壳登记）

| chain_id | 名称 | status | 节点数 | 创建日 | source_note |
|---|---|---|---|---|---|
| CH-c762b798d10f | 改性塑料产业链 | active | 0 | 2026-09-09 | r1_merge_plan_new\|长城任务\|2026-09-09 |
| CH-edcf3d2ec393 | 有机硅产业链 | active | 0 | 2026-09-09 | r1_merge_plan_new\|长城任务\|2026-09-09 |

### 3.5 终裁材料要点（供 Owner 门位裁定）

1. **禁物理删除**：图库不变量"只增不删"（merge_semiconductor_chains.py 头注：子链 deprecated+merged_into 不物理删除）；墓碑链处置上限=状态/指针治理，不做 DELETE。
2. **裁定事项一**：3.2 节 12 条 status='active' 的墓碑链是否统一翻转为 deprecated（标记已在，翻转零数据变更）。
3. **裁定事项二**：4 条 S24 分流链（建筑材料行业/电池行业/电机行业/贵金属行业）缺 merged_into 指针，分流去向需对照 S24 治理记录补指针或确认无目标。
4. **裁定事项三**：3.3 节大型墓碑（含 93 活跃节点者）是否需先行节点迁移核验再定墓碑终态。
5. A2 空壳 2 条为 r1_merge_plan_new（长城任务 2026-09-09）登记后未落节点的存量反例——W4-3 门禁缺口直接证据。

## 4. B 类新入库未补边（可补边建议）

共 5 条。判据：本链活跃节点与被覆盖链节点**同名/别名精确匹配**（链内/跨链候选均无跨链边落地）。建议：优先判重并入目标链（涉注册表净删=Owner 门位）；若确认双链并存，则补 1 条 supply/structure 传导边并落 source_doc 留痕（方向待施工核）。

| chain_id | 名称 | 本链节点(名) | 候选目标 | 建议动作 |
|---|---|---|---|---|
| CH-2934ea0c9c75 | 创新药 | 创新药 | 创新药@医药行业（CH-a8ea51457566） | 判重并入或补传导边（方向待核） |
| CH-a46e4461b385 | 铝产业链铝土矿 | 铝土矿 | 铝土矿@铝产业链（CH-c2e50e6343ed） | 判重并入或补传导边（方向待核） |
| CH-c46c64cc0c3a | 种业 | 种业 | 种业@农业种植产业链（CH-bbe500f4d8a6） | 判重并入或补传导边（方向待核） |
| CH-fce4b7d0701b | 无人机 | 无人机 | 无人机@军工产业链（CH-e35a869354f3） | 判重并入或补传导边（方向待核） |
| CH-2c270ac42170 | 工程机械产业链 | 核心零部件 | 核心零部件@具身智能产业（CH-f59d6a45f919）；核心零部件@医疗机器人行业（CH-6525dfdaeffd） | 判重并入或补传导边（方向待核） |

## 5. C 类上游断供——数据债登记

共 148 条：活跃链、无任何候选锚点、无跨链边。来源分布：同花顺导出 83 条｜p3a_auto 65 条；规模以 1-2 节点微链为主（1 节点 100 条、2 节点 44 条）；创建时间集中于 2026-08-28 ~ 2026-09-08 批量入库窗口。

**数据债定性**：两类导入器（同花顺 xlsx / p3a_auto 抽取）只落链+节点、不落上下游关系，属**源数据缺边信息**而非链本身废弃；在 W4-3 链活性卡门禁生效前，该形态将持续增量产生。

**数据债处置建议**（不在本任务施工）：① 导入器补边/拒收开关随 W4-3 立项；② 存量 148 条按主题聚类后批量补边或并入主题母链；③ 消化优先级低于 A/B 类（不阻塞墓碑终裁）。

| # | chain_id | 名称 | 活跃节点 | 来源 | 创建日 |
|---|---|---|---|---|---|
| 1 | CH-00ff28b201eb | 小核酸药物 | 2 | p3a_auto | 2026-08-28 |
| 2 | CH-03b979275113 | 介入器材 | 2 | p3a_auto | 2026-08-28 |
| 3 | CH-0861ba308462 | 高尿酸血症和痛风行业 | 2 | p3a_auto | 2026-08-28 |
| 4 | CH-0c3bd43c20d2 | 智能手表 | 2 | p3a_auto | 2026-08-28 |
| 5 | CH-0f5b57ee88a6 | 电子包装材料 | 2 | p3a_auto | 2026-08-28 |
| 6 | CH-13480a82ccc1 | A股投资者结构 | 1 | p3a_auto | 2026-08-28 |
| 7 | CH-1a7b4efdb0cf | 医疗行业IgA肾病 | 2 | p3a_auto | 2026-08-28 |
| 8 | CH-1f402d484750 | 游艇 | 1 | p3a_auto | 2026-08-28 |
| 9 | CH-24128e85e41d | 共享单车 | 2 | p3a_auto | 2026-08-28 |
| 10 | CH-2af45e8a8930 | 玻纤 | 4 | p3a_auto | 2026-08-28 |
| 11 | CH-3210d1fc2dc9 | 生物医用材料市场 | 2 | p3a_auto | 2026-08-28 |
| 12 | CH-35604465944f | 纯电动车型 | 1 | p3a_auto | 2026-08-28 |
| 13 | CH-36bda34b8372 | 贵金属 | 3 | p3a_auto | 2026-08-28 |
| 14 | CH-3e0a5097b582 | 海外多资产与解决方案 | 1 | p3a_auto | 2026-08-28 |
| 15 | CH-3fc880004662 | Type-C | 2 | p3a_auto | 2026-08-28 |
| 16 | CH-41e054f309d9 | 反内卷 | 2 | p3a_auto | 2026-08-28 |
| 17 | CH-451779d35bfd | 特应性皮炎药物 | 2 | p3a_auto | 2026-08-28 |
| 18 | CH-49c5eb71750c | 锌产业链 | 2 | p3a_auto | 2026-08-28 |
| 19 | CH-4bd17c104b06 | 海外基金 | 1 | p3a_auto | 2026-08-28 |
| 20 | CH-53e0dbc06e48 | 发光二极管（LED） | 2 | p3a_auto | 2026-08-28 |
| 21 | CH-5656ad7a1491 | 空调 | 2 | p3a_auto | 2026-08-28 |
| 22 | CH-5992976be432 | 阻燃材料 | 2 | p3a_auto | 2026-08-28 |
| 23 | CH-5a8669a7dc0a | 指纹识别 | 2 | p3a_auto | 2026-08-28 |
| 24 | CH-5aee008761a6 | 美妆个护行业2025年度 | 1 | p3a_auto | 2026-08-28 |
| 25 | CH-60b458484425 | 中国实战化白帽人才能力 | 2 | p3a_auto | 2026-08-28 |
| 26 | CH-64c49f196494 | 面部识别 | 2 | p3a_auto | 2026-08-28 |
| 27 | CH-6ce6ed1854aa | 智算中心（AIDC） | 2 | p3a_auto | 2026-08-28 |
| 28 | CH-75c6002562ac | 模具 | 2 | p3a_auto | 2026-08-28 |
| 29 | CH-7b5e2aa4032d | 硝酸铵产业链 | 2 | p3a_auto | 2026-08-28 |
| 30 | CH-7c6f790ee890 | REITs系列 | 2 | p3a_auto | 2026-08-28 |
| 31 | CH-7cf5065c67aa | 中国现制饮品风味 | 1 | p3a_auto | 2026-08-28 |
| 32 | CH-84f71385f7a0 | 64家AMC经营 | 1 | p3a_auto | 2026-08-28 |
| 33 | CH-89b4ca81216c | 前列腺癌用药 | 2 | p3a_auto | 2026-08-28 |
| 34 | CH-8c3692cb1181 | 无线数据知识 | 2 | p3a_auto | 2026-08-28 |
| 35 | CH-8dc5fba6b88a | 中国留学生归国求职 | 1 | p3a_auto | 2026-08-28 |
| 36 | CH-91d19b2d284f | 印刷电路 | 2 | p3a_auto | 2026-08-28 |
| 37 | CH-9a9cd983c83a | 硫磺上市 | 2 | p3a_auto | 2026-08-28 |
| 38 | CH-9bfdb4f0fb6f | 潮玩 | 1 | p3a_auto | 2026-08-28 |
| 39 | CH-9c31d46534b8 | 中国医药行业中间体出口 | 1 | p3a_auto | 2026-08-28 |
| 40 | CH-9c51f16c83ed | 央国企DRP与穿透式监管 | 2 | p3a_auto | 2026-08-28 |
| 41 | CH-a1b7b03a3544 | 微波炉 | 2 | p3a_auto | 2026-08-28 |
| 42 | CH-a34c91da907c | 全面屏 | 2 | p3a_auto | 2026-08-28 |
| 43 | CH-a8d8d0d79c52 | 卫星通信 | 2 | p3a_auto | 2026-08-28 |
| 44 | CH-ac8886448142 | 建筑材料 | 3 | p3a_auto | 2026-08-28 |
| 45 | CH-aeb3418ba358 | 游戏行业应用 | 2 | p3a_auto | 2026-08-28 |
| 46 | CH-b4124ec6adeb | AI Agent智能体 | 2 | p3a_auto | 2026-08-28 |
| 47 | CH-b6bec12767e3 | 无人超市 | 2 | p3a_auto | 2026-08-28 |
| 48 | CH-bb2fac0ee82d | Robotaxi | 1 | p3a_auto | 2026-08-28 |
| 49 | CH-bc4002bc7739 | 环保行业ESG | 2 | p3a_auto | 2026-08-28 |
| 50 | CH-bfeab67a7a6f | 电饭煲 | 1 | p3a_auto | 2026-08-28 |
| 51 | CH-c43653ff8f11 | AI电脑（AIPC） | 2 | p3a_auto | 2026-08-28 |
| 52 | CH-cd2891bad0da | 专用芯片（ASIC） | 2 | p3a_auto | 2026-08-28 |
| 53 | CH-d3a36ebf1446 | 电控空气悬架 | 1 | p3a_auto | 2026-08-28 |
| 54 | CH-d48d9783fee1 | 液晶显示（LCD） | 2 | p3a_auto | 2026-08-28 |
| 55 | CH-d4f3ad7fc942 | 医疗器械行业 | 4 | p3a_auto | 2026-08-28 |
| 56 | CH-d7bf2f0ca48d | 橡胶 | 2 | p3a_auto | 2026-08-28 |
| 57 | CH-e112a886b709 | 体育赛事产业链 | 2 | p3a_auto | 2026-08-28 |
| 58 | CH-e1e9cbec0159 | 算电协同 | 2 | p3a_auto | 2026-08-28 |
| 59 | CH-e8b6d5c33261 | 公募基金2025年四季报 | 2 | p3a_auto | 2026-08-28 |
| 60 | CH-eacebe454add | 中国公关行业 | 1 | p3a_auto | 2026-08-28 |
| 61 | CH-ed86e3ffe203 | GLP_1 | 2 | p3a_auto | 2026-08-28 |
| 62 | CH-f10f74bff839 | 人群 | 2 | p3a_auto | 2026-08-28 |
| 63 | CH-f68ecfde4233 | 光电共封装（CPO） | 1 | p3a_auto | 2026-08-28 |
| 64 | CH-f79b274ac109 | 手机摄像头 | 1 | p3a_auto | 2026-08-28 |
| 65 | CH-fe3c659bf7cd | 中国AI应用 | 2 | p3a_auto | 2026-08-28 |
| 66 | CH-00607d464e8f | 通信设备行业 | 1 | 同花顺导出 | 2026-09-08 |
| 67 | CH-076353f534ea | 小金属行业 | 1 | 同花顺导出 | 2026-09-08 |
| 68 | CH-08c4ae2f7be0 | 物流行业 | 1 | 同花顺导出 | 2026-09-08 |
| 69 | CH-09f695ce9f0a | 厨卫电器行业 | 1 | 同花顺导出 | 2026-09-08 |
| 70 | CH-0beffd696265 | 贸易行业 | 1 | 同花顺导出 | 2026-09-08 |
| 71 | CH-0e071263b2f5 | 工业金属行业 | 1 | 同花顺导出 | 2026-09-08 |
| 72 | CH-0f155004e3b8 | 零售行业 | 1 | 同花顺导出 | 2026-09-08 |
| 73 | CH-134de3632513 | 计算机设备行业 | 1 | 同花顺导出 | 2026-09-08 |
| 74 | CH-16df49fd5d3f | 养殖业行业 | 1 | 同花顺导出 | 2026-09-08 |
| 75 | CH-1b597c6e6a89 | 风电设备行业 | 1 | 同花顺导出 | 2026-09-08 |
| 76 | CH-1c61d83340d6 | 其他社会服务行业 | 1 | 同花顺导出 | 2026-09-08 |
| 77 | CH-201086b060df | 房地产行业 | 1 | 同花顺导出 | 2026-09-08 |
| 78 | CH-2555b2c62876 | 工程机械行业 | 1 | 同花顺导出 | 2026-09-08 |
| 79 | CH-2714a8e61ca3 | 美容护理行业 | 1 | 同花顺导出 | 2026-09-08 |
| 80 | CH-2b0421bd2a17 | 服装家纺行业 | 1 | 同花顺导出 | 2026-09-08 |
| 81 | CH-307219289fdf | 电力行业 | 1 | 同花顺导出 | 2026-09-08 |
| 82 | CH-309d753f782a | 轨交设备行业 | 1 | 同花顺导出 | 2026-09-08 |
| 83 | CH-30f16fc3c5da | 金属新材料行业 | 1 | 同花顺导出 | 2026-09-08 |
| 84 | CH-310bb151a4bf | 银行行业 | 1 | 同花顺导出 | 2026-09-08 |
| 85 | CH-31caa0add226 | 其他电源设备行业 | 1 | 同花顺导出 | 2026-09-08 |
| 86 | CH-33c364a05be7 | 黑色家电行业 | 1 | 同花顺导出 | 2026-09-08 |
| 87 | CH-379e68a0e8a1 | 机场航运行业 | 1 | 同花顺导出 | 2026-09-08 |
| 88 | CH-385189731d9c | 家居用品行业 | 1 | 同花顺导出 | 2026-09-08 |
| 89 | CH-3b11a799b865 | 汽车整车行业 | 1 | 同花顺导出 | 2026-09-08 |
| 90 | CH-3d2c7eacedda | 非金属材料行业 | 1 | 同花顺导出 | 2026-09-08 |
| 91 | CH-3e13b1b29bb0 | 化学制品行业 | 1 | 同花顺导出 | 2026-09-08 |
| 92 | CH-40bbe49b5d09 | 港口航运行业 | 1 | 同花顺导出 | 2026-09-08 |
| 93 | CH-4673d5804561 | 建筑装饰行业 | 1 | 同花顺导出 | 2026-09-08 |
| 94 | CH-49b8b437c64c | 农化制品行业 | 1 | 同花顺导出 | 2026-09-08 |
| 95 | CH-56107c1dfd81 | 纺织制造行业 | 1 | 同花顺导出 | 2026-09-08 |
| 96 | CH-5a976fef25de | 电网设备行业 | 1 | 同花顺导出 | 2026-09-08 |
| 97 | CH-6cdddabb1526 | 环境治理行业 | 1 | 同花顺导出 | 2026-09-08 |
| 98 | CH-6dfdfad6b8bf | 教育行业 | 1 | 同花顺导出 | 2026-09-08 |
| 99 | CH-71b352cc3490 | 军工电子行业 | 1 | 同花顺导出 | 2026-09-08 |
| 100 | CH-72365d424d52 | 化学原料行业 | 1 | 同花顺导出 | 2026-09-08 |
| 101 | CH-78edd56fe2bd | 小家电行业 | 1 | 同花顺导出 | 2026-09-08 |
| 102 | CH-83e4feaa835c | 医药商业行业 | 1 | 同花顺导出 | 2026-09-08 |
| 103 | CH-85725fc6c7f5 | 造纸行业 | 1 | 同花顺导出 | 2026-09-08 |
| 104 | CH-9042f765fc5f | 汽车零部件行业 | 1 | 同花顺导出 | 2026-09-08 |
| 105 | CH-90fde9fa11f4 | 游戏行业 | 1 | 同花顺导出 | 2026-09-08 |
| 106 | CH-92f416f37a9b | 光伏设备行业 | 1 | 同花顺导出 | 2026-09-08 |
| 107 | CH-93a0bf66de04 | 电子化学品行业 | 1 | 同花顺导出 | 2026-09-08 |
| 108 | CH-95bebd12a26b | 橡胶制品行业 | 1 | 同花顺导出 | 2026-09-08 |
| 109 | CH-9dd50b277202 | 消费电子行业 | 1 | 同花顺导出 | 2026-09-08 |
| 110 | CH-9e997055ba9f | 中药行业 | 1 | 同花顺导出 | 2026-09-08 |
| 111 | CH-9f5ad3c82b5a | 公路铁路运输行业 | 1 | 同花顺导出 | 2026-09-08 |
| 112 | CH-9fb48d5d1822 | 通信服务行业 | 1 | 同花顺导出 | 2026-09-08 |
| 113 | CH-a175f5a492e6 | 光学光电子行业 | 1 | 同花顺导出 | 2026-09-08 |
| 114 | CH-a2e61f87f470 | 自动化设备行业 | 1 | 同花顺导出 | 2026-09-08 |
| 115 | CH-a3802b7c01ba | 石油加工贸易行业 | 1 | 同花顺导出 | 2026-09-08 |
| 116 | CH-a3b647224125 | 元件行业 | 1 | 同花顺导出 | 2026-09-08 |
| 117 | CH-a4c3a0efaf15 | 饮料制造行业 | 1 | 同花顺导出 | 2026-09-08 |
| 118 | CH-acf5191fa5e9 | 专用设备行业 | 1 | 同花顺导出 | 2026-09-08 |
| 119 | CH-ad2ec6f7d1d8 | 证券行业 | 1 | 同花顺导出 | 2026-09-08 |
| 120 | CH-adaf10e10aff | 文化传媒行业 | 1 | 同花顺导出 | 2026-09-08 |
| 121 | CH-b4253bc8a577 | 食品加工制造行业 | 1 | 同花顺导出 | 2026-09-08 |
| 122 | CH-b519576abbc8 | IT服务行业 | 1 | 同花顺导出 | 2026-09-08 |
| 123 | CH-b5208b92f572 | 种植业与林业行业 | 1 | 同花顺导出 | 2026-09-08 |
| 124 | CH-b97ffc1a1f77 | 通用设备行业 | 1 | 同花顺导出 | 2026-09-08 |
| 125 | CH-b9c021db343a | 环保设备行业 | 1 | 同花顺导出 | 2026-09-08 |
| 126 | CH-bae090703b15 | 半导体行业 | 1 | 同花顺导出 | 2026-09-08 |
| 127 | CH-c9b29cf45204 | 煤炭开采加工行业 | 1 | 同花顺导出 | 2026-09-08 |
| 128 | CH-cb0091017e77 | 油气开采及服务行业 | 1 | 同花顺导出 | 2026-09-08 |
| 129 | CH-cb00bf9623d5 | 旅游及酒店行业 | 1 | 同花顺导出 | 2026-09-08 |
| 130 | CH-cb9bd50b2571 | 保险行业 | 1 | 同花顺导出 | 2026-09-08 |
| 131 | CH-cf58b9e70019 | 化学纤维行业 | 1 | 同花顺导出 | 2026-09-08 |
| 132 | CH-cf8d94fd2920 | 包装印刷行业 | 1 | 同花顺导出 | 2026-09-08 |
| 133 | CH-d2a85e8746a6 | 军工装备行业 | 1 | 同花顺导出 | 2026-09-08 |
| 134 | CH-daa74871e280 | 汽车服务及其他行业 | 1 | 同花顺导出 | 2026-09-08 |
| 135 | CH-db0f4c3ecbc1 | 塑料制品行业 | 1 | 同花顺导出 | 2026-09-08 |
| 136 | CH-dc01a7d6d694 | 能源金属行业 | 1 | 同花顺导出 | 2026-09-08 |
| 137 | CH-dc6473ac96a7 | 综合行业 | 1 | 同花顺导出 | 2026-09-08 |
| 138 | CH-de763786257e | 农产品加工行业 | 1 | 同花顺导出 | 2026-09-08 |
| 139 | CH-df7ed5016320 | 影视院线行业 | 1 | 同花顺导出 | 2026-09-08 |
| 140 | CH-e201b9632e56 | 白色家电行业 | 1 | 同花顺导出 | 2026-09-08 |
| 141 | CH-e6fa1eafb743 | 医疗服务行业 | 1 | 同花顺导出 | 2026-09-08 |
| 142 | CH-e7c2325dfaf0 | 软件开发行业 | 1 | 同花顺导出 | 2026-09-08 |
| 143 | CH-e8111d5fafa7 | 钢铁行业 | 1 | 同花顺导出 | 2026-09-08 |
| 144 | CH-eb2765cf5239 | 化学制药行业 | 1 | 同花顺导出 | 2026-09-08 |
| 145 | CH-f4d98935515f | 其他电子行业 | 1 | 同花顺导出 | 2026-09-08 |
| 146 | CH-f6ef897decc4 | 生物制品行业 | 1 | 同花顺导出 | 2026-09-08 |
| 147 | CH-f78ca5a7aa8e | 多元金融行业 | 1 | 同花顺导出 | 2026-09-08 |
| 148 | CH-fc6694fb5903 | 互联网电商行业 | 1 | 同花顺导出 | 2026-09-08 |

## 6. W4-3 备料："链活性卡"门禁判据建议（仅备料，不施工门禁）

1. **活链判据（主判据）**：`ig_chain.status='active'` ⇔ 该链存在 ≥1 条链内传导边（`ig_edge.from_node/to_node` 两端节点同属本链）。判据 SQL 即 §1 canonical 式取 NOT EXISTS 反面。
2. **新链准入校验点（入库口）**：链入库事务（concept_ingest / websearch_ingest / p3a_struct_extract / ths_import / r1_merge_plan 等全部写入方）在提交前校验：新链若无任何链内传导边 → 拒绝落 status='active'，要求改落 `status='stub'`（新增枚举值，Owner 裁定）或强制携带 ≥1 边。
3. **存量巡检校验点（reconciler）**：事件触发（禁 cron/Timer/sleep-loop）扫 `active 链 ∧ 零链内边` 集合（本文 §3.2/§3.4/§5 即首期全集 162 条），产出告警事件入治理队列，不自动改数据。
4. **门禁形态建议**：数据 gate（POST-COMMIT 段，own-diff 作用域：仅当本次提交触碰 ig_chain/ig_node/ig_edge 时校验其引入的链满足活性判据），gate 名建议 `IG-CHAIN-LIVENESS`；全仓扫描需按 perf 方案 §2.6 登记。
5. **反例证据**：A2 空壳 2 条（登记后零节点）= 准入校验缺失实证；C 类 148 条批量微链 = 导入器无活性约束实证。
6. **与三分法衔接**：门禁只拦增量；存量 290 条按本文 A/B/C 分类消化，墓碑处置走 Owner 门位，禁删。

## 7. 复核方式

- 连接：`zephyr.governance.depgraph_schema.get_depgraph_pg_connection(read_only=True, autocommit=True)`（只读角色）
- 清单生成脚本：`.runtime/tmp/w4_1_final_pull.py`（原始输出 `.runtime/tmp/w4_1_final_out.json`，assert 290 兜底口径漂移）
- 本文计数自检：A1(135)+A2(2)+B(5)+C(148)=290；与任务硬事实 583/873、活跃边 1253 全部对账一致

## 8. 未完成与限制

- ig_io_edge 为 sector 级（无 node_id），IO 锚信号未参与定性（对 290 条不构成定性影响，候选锚点已用节点名/别名全量精确匹配替代）。
- B 类补边方向（上游/下游）未判定，留施工阶段核；同名候选亦可能是重复主题链，并入与补边由 Owner/施工裁量。
- A1 中 4 条 S24 分流链 merged_into 指针缺失，去向待对照 S24 治理记录。
- 墓碑链处置（状态翻转/指针补全）未施工——Owner 门位，本文仅备料。

— 生成：2026-09-19 by st-final3-20260919（W4-1）
