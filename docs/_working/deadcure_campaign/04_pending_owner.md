---
ttl: task_bound
completes_when: Owner 对各项给一句话批或不批
---
# 待 Owner 门位与属主退回清单（本专案不代裁）

| 类别 | 袋数 | 代表 qid 尾号 | 请您回的话 |
|---|---:|---|---|
| Owner 门位（业务资产/受保护路径） | 35 | `-chief-20261008-0002` | 批=开落地通道／不批=判废留痕 |
| ④属主退回（会话心跳仍活，袋留原位） | 12 | `chiefc-20261009-0002` | 知悉即可，属主自处 |
| Owner 门位（业务资产/受保护路径） | 4 | `rombag-20261005-0054` | 批=开落地通道／不批=判废留痕 |
| Owner 门位（业务资产/受保护路径） | 1 | `-chief-20261005-0002` | 批=开落地通道／不批=判废留痕 |

属主活会话：`st-fullflow2-20261008`（心跳<1h，仍在投袋）、`st-chiefc-20261009`（修宪五件套当班）。

Owner 门位构成：R-8 业务资产唯一内容未落地（数据/因子/策略/指标）＝概念退役门位在您；R-9 受保护路径（`docs/03_modules/AGENTS.md` 等，门禁 PROTECTED-PATHS 实测硬阻断）。

## 待裁项 · G4 嵌套局部宪法命名闸冲突（Owner 2026-10-09 批文后新增）

- **这是什么**：FMS 战役在 `docs/03_modules/` 放一份 14 行局部宪法导航件 `AGENTS.md`（Owner 09-27 总筹令 + #ARCH-360 载体，3 个死信袋同一内容）。批文已批 A，可它每次都进不了门。
- **卡在哪把门**：GATE-NAMING **N-16 文件名项目内唯一性**——新增 `docs/03_modules/AGENTS.md` 与已入库 `src/zephyr/AGENTS.md` 同名，硬拦。审批号（#ARCH-360 标记）只过 PROTECTED-PATHS，过不了 N-16。
- **为何要您点头**：唯一合法豁免口是规则册 `trae_028_doc_structure_naming.yaml §n16_config.exempt_names_docs_extra`，而该白名单在代码里写死「改动须 Owner 批准」；专车不自签 Owner 门位。
- **不点的后果**：该导航件继续蹲 dead/（3 袋），docs/03_modules/ 无门口文件，检索阶梯仍 6 跳。
- **两选项（建议①）**：①把 `AGENTS.md` 加入 n16 豁免清单（保住嵌套局部宪法的自动发现语义，代价=同名文件允许多份，N-16 对本名失效）；②改名 `index.md`（已在豁免表，但 AGENTS.md 的 agent 自动读取语义丢失）。
- **复跑取证**：`python scripts/governance/d3_metadata/check_naming_convention.py --check-new docs/03_modules/AGENTS.md`；死因原文见 `python -c "import json;print(json.load(open(r'.runtime/commit_queue/dead/q-20261006-st-cure-p10-20261006-0005.json',encoding='utf-8'))['dead_reason'][-500:])"`
