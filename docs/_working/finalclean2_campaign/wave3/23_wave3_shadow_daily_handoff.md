---
ttl: task_bound
completes_when: 归档器影子连续 7 天零异常且统筹签认转正；本卡移交的 Q3/T8 两条各有承接方
---
# 终清波三·影子日检交接卡（执行方＝周期班/维护三班，非波三本班会话）

> 为什么这张卡存在：统筹裁定"归档器影子跑 7 天，注册计划任务随转正一并定"⇒ 影子期**不许**注册任务，
> 那这 7 天就**不能依赖本班会话活着**。会话心跳停更与"这一轮没跑"同形（在册教训），所以日检必须落到
> 一个不随会话消亡的执行方。本卡自带全部前置，接手方无需读波三上下文。
> 发起方＝st-fclean3-20261012（终清波三总包），裁定方＝总统筹 2026-10-11 深夜/10-12 凌晨批复。

## 一、每日一条（只读，零 mv）

```bash
cd /d/ZephyrAlpha
python scripts/governance/_tasks/session_closeout_reconciler.py --dry-run --json \
  > .runtime/tmp/st-fclean3-20261012/out/shadow_roundN.json    # N＝当日序号，接 round1 续编
python - <<'PY'
import json,sys,time
from pathlib import Path
sys.path.insert(0, r"D:/ZephyrAlpha/src")
from zephyr.security.access_control.session_concurrency import SessionRegistry
p = Path(r"D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out")
f = sorted(p.glob("shadow_round*.json"))[-1]
d = json.loads(f.read_text(encoding="utf-8"))
will = {k for k, v in d.get("actions", {}).items() if isinstance(v, dict) and v.get("would_level2_archive")}
live = {s.session_id for s in SessionRegistry(Path(r"D:/ZephyrAlpha")).list_active_readonly()}
hits = sorted(will & live)
print(f"{f.name}: mode={d.get('mode')} scanned={d.get('scanned')} would={len(will)} "
      f"errors={d.get('errors')} suspected={d.get('suspected')} 命中在飞={hits}")
assert d.get("mode") == "shadow", "非 shadow 态，立即停手上报"
assert not d.get("errors"), "本轮有 errors，不得计为零异常日"
assert not hits, f"⚑告警：点名集命中在飞会话 {hits}——这就是影子期要抓的病，停转正并上报统筹"
print("本轮合格（计一天）")
PY
```

判据＝**四件齐**才算一天：`mode=shadow` ∧ `errors=[]` ∧ `suspected=[]` ∧ `命中在飞=[]`。
任一件不齐：**当日不计**，且**暂停转正**，把 JSON 原样贴呈统筹。零异常满 7 个自然日＋统筹签认，才允许
`--execute` 转真 mv（mv 可逆，`sessions → sessions_archive/YYYY-MM/`）；**注册计划任务与转正同批定，影子期不注册**。

## 二、round1 基线（2026-10-12 01:31 实测，接手方据此校尺）

| 项 | round1 值 |
|---|---|
| mode / scanned | shadow / 466 |
| would_level2_archive | **288** |
| errors / suspected / merge_warned | 0 / 0 / 0 |
| skipped | 一组 `orphan_keep` 豁免（`AI-PROBE-001` age≈6.3d、`st-acure-*` age≈345ks）⇒ 白名单在起作用，非空转 |
| 与在飞三源交叉核 | **0 命中**（点名集 ∩ `list_active_readonly()`＝∅；今晚六班∪本班九支全不在集内） |
| 口径差因（勿硬合） | 波三手工"mtime>7d"代理得 268，机制自算 288 ⇒ **以机制口径为准**，差 20 枚已登记 |

⚠ 两条不可违反的取数纪律（都是本班实测换来的）：
1. 活死判定**只用 `list_active_readonly()`**。`list_active()` 是 **mutating 版会写接管台账**；
   单文件 `.runtime/session_registry.json` 只是**滞后兼容副本**（实测曾瞬时 6/8/14 而真源恒 15，
   且当时**看不见在飞的 `st-datalane-20261010`**——照它判孤儿就会误杀在飞车道）。
2. 在册工具的 `--help` **不是只读动作**（波二 27 支里 22 支无 argparse，`--help` 即跑主逻辑，
   已造成误删他人分支＋覆写 793 枚受保护存证件）。要看行为就读源码。

## 三、随本卡移交的两条裁定承接项

- **Q3（→ 册主车道出证，波三不自裁）**：quarantine 里 `drift_*` 独有字节 **382.8 MB（占独有面 65%）**
  集中于两本 GENERATED 投影册（`capability_canonical_file_registry` 270.5 MB＋`module_translation_registry` 112.2 MB）。
  定性＝"可重导噪声"还是"漂移前像取证"，需要跑 `--render`（**写面**）＋查 PG `registry_ledger.registry_snapshot` 的
  `snapshot_version` 历史行逐版对拍。波三权限内已把判据备齐（车道 `lane_quarantine.md`：全集 9,388 件零抽样，
  A 450／B 228／C1 7,328／C2 1,382，REDUNDANT 488 枚仅占 2.0% 字节；去重可省 −39.4% 枚数但只 −14.7% 字节），
  **出证需由册主车道做**（波三禁出"重打投影袋"，那 1600+ 行是他班登记，混进本班 commit＝归属篡改）。
- **T8（→ 有权道处置，波三不动手）**：`.aidrafts/st-regsolo-20261010/config/.env.clickhouse`（596 B）与
  `.env.postgres`（451 B）**与主仓 sha256 全等且 git 未跟踪**＝第二份未纳管明文密钥副本（违 RULE-SECRETS 精神面）。
  波三只登记**路径＋字节＋sha**，**未复制第三份明文**（存证面 `MANIFEST.jsonl` 的 2 条 `hash_only_manifest` 即此二件）。
  删除前须先核该车道是否还有别的路径读本地 `.env`（部分作业依赖本地件），故**禁无脑 rm**。

## 四、波三本班侧的未闭合项（供收班核）

- 两袋（`q-20261012-st-fclean3-20261012-0001` 六件／`-0002` 三件）截至 01:5x 均 `state=pending`
  （0001 前面 13 袋、0002 前面 30 袋）⇒ **落地尚未发生**，判落地只认 `git log -- <path>`／`git show dev:<path>`，
  不认工棚自证。⚠ 后继袋**禁把 21_/22_ 已投件重复装入同会话后袋**（在册坑：同 sid 同件后袋会静默吞前袋条目且无死信声明）。
- 真删账＝46 个零文件目录（清单 sha256 `0b0cae988df22cca4767662b0f01a1e882a7ababb6b03ec8868fc42008065f7a`，
  deleted=46／failed=0／复存=0）；存证账＝`.runtime/quarantine/fclean3_safety/aidrafts_irreplaceable/MANIFEST.jsonl`
  25 行（23 件 `byte_copy` 且 sha 回验全等，合计 111,428 B；2 件 `hash_only_manifest`＝T8 密钥）。
- 三件"看着像垃圾实为唯一证据"的反转与本班自犯三起，均在 `21_/22_` 册内**另起一节**留档，未改写旧案卷。
