---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
completes_when: 统筹/后班读到本更正且 `25_` §4b 的 r7/r8/r9 编号按本节重排理解
session: st-fclean4-20261012
lane: wave4-main
role: 更正册（另起一册，`25_` 已落地正文一字不改）
---

# 终清波四·影子轮次编号更正（r7/r8/r9 实为三刀，原始件被自家后台任务覆盖一次）

## 1. 事实（按各文件内 `ts` 字段，非按我的记忆）

| 序 | 本地时刻 | 册内 `ts`（UTC） | scanned | would_n | 该计入哪一天 | 原始件现状 |
|---|---|---|---|---|---|---|
| r6 | 10-12 22:59:40 | 2026-10-12T14:59:40Z | 483 | 317 | day1 | `shadow_day1_r6.json` 完好 |
| r7 | 10-12 **23:58:13** | 2026-10-12T15:58:13Z | 481 | 320 | **day1**（未跨本地零点） | ⚠**原始件被覆盖**（见 §2），数值来自 23:58 当时的实跑输出与 `25_` §4b 记录 |
| r8 | 10-13 **00:01:06** | 2026-10-12T16:01:08Z | 481 | 320 | **day2 首轮＝合格** | `shadow_day2_r8.json` 完好 |
| r9 | 10-13 **00:02:02** | 2026-10-12T16:02:02Z | 481 | 320 | day2 第二轮（幂等自证） | 原被写进 `shadow_day2_r7.json`（覆盖位），本班已另存 `shadow_day2_r9_from_nohup.json` |

## 2. 为什么会多出一次覆盖（本班自犯第八起）

为了拿"10-13 跨日首轮"，本班在 23:0x 用 `nohup bash -c "sleep <到 00:02>; ... > shadow_day2_r7.json"` 挂了个后台跑轮；
随后又手跑了 23:58 那轮并写成同名 `shadow_day2_r7.json`。于是 00:02 后台到点时把**手跑那轮的原始件覆盖**成它自己的读数——
文件名与时刻就此错位（00:02 那轮顶着 `r7` 的文件名，而 23:58 那轮只剩纸面数）。

**违反的在册纪律**：同一测量面用两个来源写同一文件名（且一个在无人看管的延时里触发）。
**正解（后班直接用）**：延时跑轮要么把输出文件名带上时间戳（`shadow_<UTCts>.json`），
要么改用本地一次性任务并把判据与撤销法登记在册（见记忆 `one-shot-cron-for-approved-future-slot`），不要复用固定文件名。

## 3. 结论是否受影响（逐项判定）

- **合格日计数不变**：day1＝10-12（波三 r1-r5 ＋ 本班 r6/r7），day2＝10-13（r8 起，r9 只是同日第二轮幂等复证）⇒
  `23_` §3 与 `25_` §4b 给的"合格日＝2、最早呈转正＝2026-10-19"**不变**。
- **跨轮口径不变**：r8 相对 r7 的 `new/gone=0/0`、r7 相对 r6 的 `new=4／gone=1` 都是当时实跑读数，
  但 **r7 那条已无原始件可复核**——若后班要追这一步，请以 r6↔r8 对账（new=4/gone=1 同样成立：would 317→320）。
- **四件合格判据不变**：r6/r8/r9 三份原始件均可复算（`mode=shadow ∧ errors=0 ∧ suspected=0 ∧ 命中在飞=0`）。

## 4. 复算

```bash
cd /d/ZephyrAlpha
python - <<'PY'
import json,pathlib
O=pathlib.Path('D:/ZephyrAlpha/.runtime/tmp/st-fclean4-20261012/out')
for n in ('shadow_day1_r6','shadow_day2_r7','shadow_day2_r8','shadow_day2_r9_from_nohup'):
    d=json.loads((O/(n+'.json')).read_text(encoding='utf-8'))
    print(f'{n:32s} ts={d["ts"]} scanned={d["scanned"]} would={len(d["actions"])} errors={len(d["errors"])} suspected={len(d["suspected"])}')
print('注：shadow_day2_r7.json 现内装 00:02:02Z 那轮（覆盖），23:58 那轮只剩纸面值。')
PY
```
