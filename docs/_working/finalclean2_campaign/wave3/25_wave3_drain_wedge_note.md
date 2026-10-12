---
ttl: task_bound
completes_when: 本件登记的排水卡位被维护三班（通宵令 §五 其节"队列完整性簇"）认领或落地后自动失效
---
# 终清波三·排水卡位观测件（只登记，不代修；sid=st-fclean3-20261012）

> 为什么单独一件：本包所属的波三与其余六班今夜全部走队列正门，**一条卡位会决定"Owner 醒来时可执行的是否都在 HEAD"**。
> 本班按宪法 §3.4"他会话在途违规不代修：owner 责任制"处理＝测量＋登记，**零触碰他班袋、零放锁、零 requeue**。

## 一、实测（2026-10-12 02:1x，全部只读）

| 面 | 读数 |
|---|---|
| `pending` | 44 袋；最老 **131.2 min**；最近写 1.3 min ⇒ 入队侧仍在活跃进料 |
| `processing` | **1 袋 = `q-20261012-st-gpuwo-20261011-0006`，已挂 133.2 min** |
| `done` | 746 袋；**最近写 7.6 min** ⇒ 排水并未全线停摆 |
| `dead` | 1,456 袋；最近写 18.1 min |
| `.git/index.lock` | **不存在**（非锁毒型卡位） |
| 活体排水工 | PowerShell `Get-CimInstance` 全表 grep `0006|drain|convoy|serializer|reconcile_launch`＝**零命中**，即无存活进程指向该袋 |
| 该袋字段 | 仅 `base_head/branch/created_at/files/meta/qid/session_id`，**无 `claimed_by/attempt/state/pid` 位**（袋体本身不带租约字段） |

## 二、判读与边界

- **形态**：单袋被取入 `processing` 后无活体消费者，而同窗他袋仍能完成（`done` 7.6min 前还在写）⇒ 属**该袋/该 worktree 通道的租约悬挂**，不是全局楔死。
- 本班**不做**的动作与理由：①不 `requeue` 他班袋（在册处方"袋在飞禁放锁"，且属他班 owner 责任面）；②不删 `processing` 文件（＝可能吞掉他班一次未落地的施工内容，归属篡改级）；③不碰 `serializer.lease.renew-26548` 残件（车道 `lane_face_ownership.md` 已把它登记为"根 1,066 枚 `.seq`＋租约残件"收敛项，处置权在维护面）。
- **对本波的实际影响（如实）**：波三 `q-0001` 当时 `position_ahead=10`，`0002/0003/0004` 为 27/30/42 ⇒ 四袋**均未落 dev**（`git ls-tree -r dev` 对 `finalclean2_campaign/wave3` 命中数＝0）。本班不称任何一袋完成，落地判据只认 `git log -- <path>`／`git show dev:<path>`（见 `24_...md` §一 尾行）。

## 三、给维护三班的可复算测量（其节"队列完整性簇 LANDED_ID_FOREIGN 探针＋claim TTL/租约错配修法"同域，建议并案）

```bash
# 单袋挂起时长与"有无活体消费者"的配对判据（本件所用两命令）
python -c "import time,pathlib;p=pathlib.Path(r'D:/ZephyrAlpha/.runtime/commit_queue/processing');print([(f.name,round((time.time()-f.stat().st_mtime)/60,1)) for f in p.iterdir()])"
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe' or Name='pythonw.exe'\" | Select-Object ProcessId,CommandLine" | grep -i -E "drain|convoy|serializer|reconcile_launch"
# 排水是否"单通道停他通道行"（done 最近写时刻）
python -c "import time,pathlib;q=pathlib.Path(r'D:/ZephyrAlpha/.runtime/commit_queue');print({s:round((time.time()-max((f.stat().st_mtime for f in (q/s).iterdir() if f.is_file()),default=0))/60,1) for s in ('pending','processing','done','dead')})"
```

**建议默认（不点即按此保守停）**：把"取入 `processing` 但无活体消费者超 N 分钟"做成**可观测断言**（只报警不自动动袋），
与 0002 册 §五-M1 记的"7d TTL 把审计散件**无声吃掉**"同属一类病：**失败形态与正常形态同形**。
阈值与实现归维护三班，本班不自建探针（净零：不新增第二套观测面）。
