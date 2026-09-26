---
ttl: task_bound
completes_when: 双总筹碰撞有单一指挥位、本道已落面与在途面逐件可核、热册唯一写手交接完成
---

# 波13 双总筹碰撞 · 交接与并发指挥位（st-zmaster2-20260926 → st-chief3-20260926）

> **本册存在的理由**：Owner 于 2026-09-26 22:2x 就寝前另任 `st-chief3-20260926` 为总包/总筹，而本会话（`st-zmaster2-20260926`，20:3x 受命）已在 20:5x–22:5x 落了波 13 的四批。chief3 的接管台账实测"前总筹道心跳停在 20:51"并据此判本道inactive——**这条读数是它从我这里继承的一个假象**，根因见 §三。
> **纪律**：本册不改写 chief3 的 `docs/_working/wave13_chief3/`（它已裁"新册单列"），也不改 `total_command_closeout/` 两本总册（他道 claim 在途）。**碰撞消解靠位点声明，不靠谁覆盖谁。**

## 一、本道已进 HEAD 的面（只认 `git show HEAD:`，附短码，chief3 勿重复落）

| 短码 | 内容 | 复算命令 |
|---|---|---|
| `32389d3123` | 波13 方案册 + 执行台账（两件） | `git show --stat 32389d3123` |
| `461b25d0e8` | 册先行袋：token 68 条 + 翻译 9 条 | `git show HEAD:<能力册> \| grep -c "capability: three_piece_infra"` → 62 |
| （队列 q-...-0004） | 册先行袋二：收敛案卷 2 token + reconciler 1 翻译 | 同上，纯插入 10/0 与 12/0 |
| `858a2ca1fb` | 挖矿叶子批一：族 1/2/3/4/5/11/12/13 共 30 份叶簿 + 总勾表 | `git show --stat 858a2ca1fb` |
| （队列 q-...-0006） | 封矿复核批 11 件（判"万无一失"不成立，四条 P0 带命令） | `python scripts/commit_queue.py status` |

## 二、本道在途、**尚未落地**的面（chief3 若要落，请先取本表；勿自行从车道副本猜权威版）

| 包 | 权威字节在哪 | 状态 | 落地前置（我已实测的门禁契约，缺一项整袋死） |
|---|---|---|---|
| 13.1 CREATE-GUARD 查功能 | `.worktrees/st-p1-gate`（乙道），我已把 5 件取到本道并预跑到硬阻断 0 | **主动暂停**（§四） | 主区 `create_guard.py` 为 `MM`（他道"T8 簇1 册解析进程内缓存"28/15 在途）。落我的版本＝覆写他道未落地字节；且落地侧收敛 `skipped_dirty` 后门禁会读主区陈旧盘字节，把我袋里的测试误判成"符号不存在"假红（两文件实测各 5 处命中该符号）。**重投条件：主区该文件 clean，或他道该件先进 HEAD** |
| 13.2+13.3+13.4 合流袋（治理面 14 件） | `.worktrees/st-p8-integrate`（癸道在修 11 红） | 在飞 | 见 §五 门禁契约清单 |
| 图形接线袋（P0 G-A） | `.worktrees/st-p9-fixchart`（甲道在修 7 红） | 在飞 | 同上 + `TableRegistry` 替硬编码表名 + `save_pack` 禁二次实现 |
| 桥两缺陷袋（TRD-A10） | `.worktrees/st-p4-bridge`（巳道交付未修门）预跑 5 红 | 待修 | GATE-DOMAIN-FK / FUNCTION-DUP / COMPLEXITY / MUTABLE-CONST-WITHOUT-FINAL |
| T1 分析案卷袋 | `.worktrees/st-p6-t1top`（未交件已固化） | 待落 | 纯 docs，token 已在 `461b25d0e8` |

## 三、碰撞根因（这是**在册缺陷 W-29 的活体复现**，不是任何一方的错）

`session_worktree.py create` 起的 `heartbeat_daemon` 明文"**idle>1800s 自动退出**"。总筹道的工作形态是"长会话 + 每次工具调用起一个短命 python 进程"：
- 短命进程若按 R-0 注册 `pid=0`，它不产生车道 heartbeat；
- 守护腿在 30 分钟无本地活动后自退，`heartbeat.jsonl` mtime 就冻在最后一次；
- 于是**本道在 20:51 之后一直干活，但对任何观测面表现为已死**。

⇒ 后果不是观感问题：另一个会话据此合法地接管，形成双总包。修法建议（一条，非新机制）：把 `heartbeat_daemon` 的退出条件从"本地 idle 时长"改为"**SessionRegistry 里该 session 是否仍被 claim/心跳续期**"，与 `pid=0` 注册形态对齐；或在注册时同步登记"逻辑会话"标志使守护不退。**这条与 chief3 台账里"车道全部存活、本道停摆"的判读互证，应进 Owner 菜单外施工项（属 W-29 面，非门位）。**

## 四、包 13.1 的处置与理由（Owner 点名的第一件，为何本窗没落）

不是没做完：代码+红证+120 样本/328 类逐字节等价重放（328 grep/34.6s → 1 grep/0.84s）在乙道成件，本道预跑硬阻断 0。是**落地会与在途道互踩**，且踩了就是静默回退弹（本仓在册教训）。按"不吸收、不回退他道"处置为暂停 + 重投条件明确，比硬落更负责。

## 五、给 chief3 的门禁契约清单（本窗实测，六道全在这里翻过车；派单第一句就贴这段）

1. `[TESTS]` 头部**只准一个路径**：`tests_coverage_gate.py:132` 用 `match.group(1).strip()` 单捕获，逗号多值会整串当文件名→判"测试不存在"（实测踩中）。
2. `[DOMAIN]` 必须是 `functional_domain_registry.yaml` 注册值：**`D_GOV` 被 depgraph domains 表与 GATE-DOMAIN-FK 双拒**，但翻译册里仍有 4 条 `D_GOV` 历史条目 ⇒ 跨存储词表漂移实证，施工一律用注册值。
3. 新 .py **禁放 `src/zephyr/governance/` 根**（ARCH-031），进功能子目录。
4. 新 .py 需 15 字段头 + `[TTL]` 在前 30 行 + `creation_token` + `add_module_translation`（plain_zh ≥8 字）+ depgraph 节点；**token 批与内容同袋或先行**。
5. 圈复杂度 >15 硬拦（用门禁自家 `_cyclomatic_complexity` 复算，别拿第三方数）；参数 >7 拆（参数对象/dataclass）。
6. 硬编码 CH 表名必走 `TableRegistry.table(<category_id>)`。
7. 同一函数实现禁二次（FUNCTION-DUP 按 hash 抓，实测抓到 `save_pack`）。
8. 异常消息禁插路径/凭据（MSG-EXPOSURE），走 details 面。
9. `docs/_working` 新 .md：frontmatter **只 `ttl`（可带 `completes_when`）**，且**值内禁裸引号/裸冒号**——实测 `completes_when: "X"的...` 会让 YAML 解析失败，TTL 门误报"缺 ttl"（在册旧坑复现）。
10. 禁 `#ARCH-NNN`/`裁定#NNN` 未登记引用（REFERENCE-INTEGRITY 双形态）；禁 `.json` 进 `docs/_working`；目录/文件名禁以数字结尾。
11. 一袋只 stage 本袋路径，其余 `git restore --staged`——否则文档袋会被别袋的码拖进 GATE-DOMAIN-FK/TTL 门（本道实测）。
12. claim 一律走 `git_commit.py --claim-only`（网关路径）+ 注册 `pid=0` 且与提交同一条命令链；`lock_files.py acquire` 的相对路径 claim 对 CLAIM-REQUIRED **不可见**。
13. 车道建好即 `git reset --soft $(git rev-parse dev)` 对齐 head，否则存在性/符号类门禁读老字节假红。

## 六、本道自审（我自己的错，交给 chief3 一并防重演）

- **S-1 我差点造成本役第二次蒸发**：我写的热册重放脚本把 `entries:` 段当成"到文件末尾"，将块写到文件尾、压掉 `battle_map_steps:` 段 ⇒ 341 条 step 身份消失。被 `REGISTRY-MASS-DELETION` + `MAP-ALIGNMENT` 双门在落地前拦下。**更险的是我先用的安全证据是错的**：`git diff --numstat` 显示 `deleted=0` 我一度判安全——行级"零删除"完全掩盖段结构错位。处方：热册安全性一律按**根键分段身份集合差**判（`- module_path:` / `- step_id:` / `^- file:` 各自 vanished 必 0），行级 numstat 不得作热册安全证据；该自造重放器已废弃，只用 `add_module_translation.py`/`batch_creation_tokens.py`。
- **S-2 先行袋只打了一拍**：后续批次（收敛案卷、丙道翻译）成文晚于册先行袋 ⇒ 内容袋必死 CREATE-GUARD。两拍是按批循环，不是一次性。
- **S-3 任务书缺门禁契约**：六道全在合流期撞同类红，等于我把返工转嫁给了集成阶段（详见 §五，已由本窗实测补成清单）。
- **S-4/S-5**：`lock_files.py` 相对路径 claim 对门禁不可见；车道 head 未对齐 dev 致存在性判定假红。均已进 §五。
