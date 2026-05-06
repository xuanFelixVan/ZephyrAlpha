---
classification: internal
date: '2026-05-02'
doc_type: index
generated: '2026-05-02'
merged_from: README.md + index.md
module_id: DIR-03-README
status: active
title: 03_modules 鐩綍璇存槑 鈥?妯″潡鐢熷懡鍛ㄦ湡鍞竴鐪熸簮
---

# 03_modules 鈥?妯″潡鐢熷懡鍛ㄦ湡鏂囨。锛堝敮涓€鐪熸簮锛?
## 璐ｄ换澹版槑锛圫ingle Responsibility锛?
鏈洰褰曞彧瀛樻斁锛?*鍏ㄩ噺妯″潡鐢熷懡鍛ㄦ湡鏂囨。鈥斺€擟 杞?14 灞?+ B 杞ㄦí鍒囧熀纭€璁炬柦銆傝摑鍥撅紙鍚柦宸ユ寚寮曪級銆佹帴鍙ｈ鑼冦€佷氦浠樿褰曠粺涓€鍦ㄦ鐩綍鏍戜笅**銆?
> **2026-05-02 鏇存柊**锛氳摑鍥惧拰鏂藉伐鎸囧紩宸插悎骞朵负涓€浠?`blueprint.md`锛埪?-搂11 鏋舵瀯璁捐 + 搂12 鏂藉伐鎸囧紩锛夈€備笉鍐嶉渶瑕佺嫭绔嬬殑 `construction-plan.md`銆傚浜?100% AI 寮€鍙戯紝涓€浠芥枃妗ｈ鐩栧叏娴佺▼銆?
## 鏂囦欢娓呭崟

| 鏂囦欢 | 璇存槑 |
|------|------|
| module-registry.yaml | 妯″潡鐢熷懡鍛ㄦ湡鐧昏琛紙YAML锛?|
| blueprint-registry.yaml | 钃濆浘娣卞害璇勪及鐧昏琛紙YAML锛?|
| README.md | 璺宠浆鑷?index.md |

## 涓€銆佹娊灞夎矗浠伙紙Single Responsibility锛?
> **涓€鍙ヨ瘽**锛氳繖涓洰褰曟槸 ZephyrAlpha **鎵€鏈変笟鍔℃ā鍧?*鐨勬枃妗ｄ箣瀹躲€備竴涓ā鍧椾粠鐢熷埌姝荤殑鎵€鏈夋枃妗ｉ兘鍦ㄨ繖閲屻€?
| 鏀句粈涔?| 涓嶆斁浠€涔堬紙鈫?鍘诲摢锛?|
|--------|-------------------|
| 妯″潡钃濆浘锛坄blueprint.md`锛墊 浼佷笟绾ф灦鏋勮鍥撅紙鈫?`02_enterprise_architecture/target-architecture/`锛?|
| 妯″潡鏂藉伐鍥撅紙鏁村悎鍦?`blueprint.md` 涓級| 鈥?|
| 妯″潡浜や粯璁板綍锛坄delivery/`锛墊 鏋舵瀯鍐崇瓥璁板綍 ADR锛堚啋 `02_enterprise_architecture/adr/`锛?|
| 鈥?| AI 鏈嶅姟鎺ュ彛鍚堝悓锛堚啋 `_b_track_interfaces/`锛墊
| 鈥?| 鍚堣瑙勮寖锛堚啋 `10_compliance/`锛?|
| 鈥?| 娌荤悊瑙勫垯锛堚啋 `01_policies_and_standards/`锛?|

**瀵规爣**锛欸oogle Monorepo 鐨?涓€涓」鐩?= 涓€涓洰褰曪紝鎵€鏈夋枃妗ｅ拰浠ｇ爜鍦ㄤ竴璧?鍘熷垯銆侺inux FHS 鐨?鎸変富浣撳垎鐩綍锛屼笉鎸夋枃浠剁被鍨嬪垎鐩綍"鍘熷垯銆?
## 浜屻€佸唴閮ㄧ粨鏋?
```
03_modules/
鈹溾攢鈹€ module-registry.yaml          鈫?鈽?妯″潡鐧昏琛紙AI 鐨勭涓€鍏ュ彛锛孻AML 缁撴瀯鍖栨暟鎹級
鈹溾攢鈹€ blueprint-registry.yaml       鈫?鈽?钃濆浘鐧昏琛紙鏂藉伐杩涘害/瀹屾暣搴?浠ｉ檯璇勪及锛?鈹溾攢鈹€ index.md                      鈫?鏈枃浠讹紙鍞竴鐪熸簮锛?鈹溾攢鈹€ README.md                     鈫?璺宠浆鑷?index.md
鈹?鈹溾攢鈹€ _b_track_interfaces/          鈫?B 杞ㄦ帴鍙ｈ鑼冿紙鍘?07_ai_engineering/锛寁2.0.0 杩佺Щ鑷虫锛?鈹?  鈹溾攢鈹€ index.md
鈹?  鈹溾攢鈹€ agent-orchestrator-interface.md
鈹?  鈹溾攢鈹€ context-engine-interface.md
鈹?  鈹溾攢鈹€ feedback-loop-engine-interface.md
鈹?  鈹溾攢鈹€ llm-security-gateway-interface.md
鈹?  鈹斺攢鈹€ vector-memory-service-interface.md
鈹?鈹溾攢鈹€ l01_infrastructure/           鈫?L01 鍩虹璁炬柦灞?鈹?  鈹溾攢鈹€ README.md                 鈫?鏈眰鑱岃矗澹版槑
鈹?  鈹溾攢鈹€ index.md                  鈫?灞傜骇绱㈠紩
鈹?  鈹溾攢鈹€ <module-name>/            鈫?姣忎釜妯″潡涓€涓瓙鐩綍锛堝叏灏忓啓 kebab-case锛?鈹?  鈹?  鈹溾攢鈹€ blueprint.md          鈫?鈽?钃濆浘锛氭灦鏋勮璁★紙搂1-搂11锛? 鏂藉伐鎸囧紩锛埪?2锛?鈹?  鈹?  鈹斺攢鈹€ delivery/             鈫?浜や粯璁板綍锛堟寜鐗堟湰锛?鈹?  鈹?      鈹斺攢鈹€ index.md
鈹?  鈹斺攢鈹€ ...
鈹?鈹溾攢鈹€ l02-l13/                      鈫?棰勭暀缁欐湭鏉ュ悇灞傦紙experimental+ 闅忔ā鍧楀垱寤洪€愭寤虹珛锛?```

## 涓夈€佹ā鍧楃敓鍛藉懆鏈燂紙浠庤摑鍥惧埌浜や粯锛?
> **2026-05-02 鏇存柊**锛氳摑鍥句笌鏂藉伐鍥惧凡鍚堝苟銆俙blueprint.md` 搂1-搂11 涓烘灦鏋勮璁★紝搂12 涓烘柦宸ユ寚寮曘€備笉鍐嶇嫭绔嬬淮鎶?`construction-plan.md`銆?
```
闃舵 1: 钃濆浘锛圔lueprint锛?  鈹?浜у嚭: blueprint.md锛埪?-搂11 鏋舵瀯璁捐 + 搂12 鏂藉伐鎸囧紩锛?  鈹?鍐呭: 鏋舵瀯璁捐銆佹ā鍧楄竟鐣屻€佷緷璧栧叧绯汇€佹帴鍙ｅ绾︺€佸疄鏂芥楠?  鈹?鐘舵€? drafting 鈫?review 鈫?approved
  鈹?闃舵 2: 浜や粯锛圖elivery锛?  鈹?浜у嚭: delivery/vX.Y.Z.md
  鈹?鍐呭: 瀹為檯鍋氫簡浠€涔堛€佸亸宸鏄庛€佺粡楠屾暀璁?  鈹?鐘舵€? pending 鈫?delivered 鈫?verified
```

**鐘舵€佹満瀹屾暣瀹氫箟**瑙?`module-registry.yaml` 鈫?`_schema.status_values`銆?
## 鍥涖€丄I 浣跨敤鎸囧崡锛圸ero-Memory 鍙嬪ソ锛?
### 鍏ュ彛娴佺▼

```
Step 1: 璇?module-registry.yaml 鈫?浜嗚В鍏ㄩ儴妯″潡姒傚喌
        鈹溾攢鈹€ 鎸?layer 杩囨护: 杩欎釜灞傛湁鍝簺妯″潡锛?        鈹溾攢鈹€ 鎸?domain 杩囨护: 杩欎釜鍔熻兘鍩熸秹鍙婂摢浜涙ā鍧楋紵
        鈹斺攢鈹€ 鎸?status 杩囨护: 鍝簺钃濆浘閫氳繃浜嗭紵鍝簺鏂藉伐涓紵

Step 2: 瀹氫綅鍒扮洰鏍囨ā鍧楃洰褰?鈫?璇诲叿浣撴枃浠?        鈹溾攢鈹€ 璇?blueprint.md 鈫?浜嗚В妯″潡璁捐锛埪?-搂11锛変笌鏂藉伐鎸囧紩锛埪?2锛?        鈹斺攢鈹€ 璇?delivery/ 鈫?浜嗚В鍘嗗彶浜や粯

Step 3: 淇敼鍚?鈫?鏇存柊 module-registry.yaml 瀵瑰簲鏉＄洰鐨勭姸鎬?```

### 鍒涘缓鏂版ā鍧楁椂

```
0. 鈽呫€愬己鍒舵煡閲嶃€戝厛鍦?module-registry.yaml 涓悳绱㈠悓鍚?鍚岃矗妯″潡鈥斺€?      鈹溾攢鈹€ 鏄惁鏈?status=deprecated 浣嗚矗浠昏寖鍥撮噸鍙犵殑钃濆浘锛?      鈹?    鈫?鏈?鈫?璧?钃濆浘鍗囩骇娴佺▼"锛堣 搂鍏級锛岀姝㈡柊寤?      鈹?    鈫?鏃?鈫?缁х画涓嬩竴姝?1. 鍦?module-registry.yaml 鐨?modules 鍒楄〃涓坊鍔犱竴鏉¤褰?2. 鍦ㄥ搴斿眰绾х洰褰曚笅鍒涘缓妯″潡瀛愮洰褰曪紙鍏ㄥ皬鍐?kebab-case锛?3. 鍒涘缓 blueprint.md锛堝彲鍙傝€?templates/blueprint-template.md锛屄?-搂11 鏋舵瀯 + 搂12 鏂藉伐鎸囧紩锛?4. 鏂藉伐瀹屾垚鍚庯紝鍦?delivery/ 涓嬪垱寤虹増鏈褰曟枃浠?```

### 鐧昏琛ㄦ牎楠?
```
pre-commit 鑴氭湰浼氳嚜鍔?
  鈹溾攢鈹€ 鎵弿 03_modules/ 涓嬪疄闄呭瓨鍦ㄧ殑妯″潡鐩綍
  鈹溾攢鈹€ 涓?module-registry.yaml 姣斿
  鈹溾攢鈹€ 鐗╃悊瀛樺湪浣嗘湭鐧昏 鈫?鍛婅
  鈹斺攢鈹€ 宸茬櫥璁颁絾鐩綍涓嶅瓨鍦?鈫?鍛婅
```

## 浜斻€佷笌鍏朵粬鐩綍鐨勫叧绯?
```
01_policies_and_standards/  鈫?鎬庝箞绠★紙娌荤悊瑙勫垯銆佹ā鏉匡級
    鈹溾攢鈹€ templates/blueprint-template.md        鈫?钃濆浘妯℃澘
    鈹溾攢鈹€ governance/module/                     鈫?妯″潡鍑嗗叆/鐢熷懡鍛ㄦ湡/娉ㄥ叆瑙勫垯
    鈹?                                            bootstrap-plans/ 宸蹭簬 2026-05-02 搴熼櫎锛?    鈹?                                            鏂藉伐鍐呭杩佸叆鍚勬ā鍧?blueprint.md 涓?
02_enterprise_architecture/  鈫?涓轰粈涔堣繖鏍疯璁★紙浼佷笟鏋舵瀯 + ADR锛?    鈹斺攢鈹€ target-architecture/                   鈫?TOGAF 鏋舵瀯瑙嗗浘

03_modules/                  鈫?鈽?鏈洰褰曪細姣忎釜妯″潡鐨勫畬鏁存枃妗?    鈹斺攢鈹€ module-registry.yaml                  鈫?鐧昏琛?
src/zephyr/                  鈫?浠ｇ爜锛堜笌 03_modules 鎸夊眰瀵归綈锛?    鈹斺攢鈹€ l{NN}_*/                              鈫?浠ｇ爜鐩綍锛屼笌鏂囨。鐩綍涓€涓€瀵瑰簲
```

## 鍏€佽妯￠獙璇侊紙1500 涓ā鍧楋級

```
1500 涓ā鍧?梅 14 灞?鈮?107 涓ā鍧?灞?姣忓眰 107 涓瓙鐩綍 脳 姣忕洰褰?2-4 涓枃浠?= 鏂囦欢绯荤粺鏃犲帇鍔?
AI 瀹氫綅娴佺▼:
  module-registry.yaml锛? 娆¤鍙栵紝浜嗚В鍏ㄩ儴 1500 涓級鈫?  瀹氫綅鍒版ā鍧楃洰褰曪紙1 娆¤鍙栵紝浜嗚В璇ユā鍧楀畬鏁寸敓鍛藉懆鏈燂級
  鏃犻渶閬嶅巻銆佹棤闇€鐚滄祴
```

## 涓冦€佽鍒?
| # | 瑙勫垯 | 璇存槑 |
|:--:|------|------|
| 1 | 妯″潡鐩綍鍚?*鍏ㄥ皬鍐?kebab-case** | 濡?`market-data-ingestor`锛屼笉鐢?`MarketDataIngestor` 鎴?`market_data_ingestor` |
| 2 | 鍚屾ā鍧楁墍鏈夋枃浠舵斁鍚屼竴鐩綍 | blueprint.md锛堝惈鏂藉伐鎸囧紩锛? delivery/ 涓嶅垎鏁?|
| 3 | 鍦ㄧ櫥璁拌〃鐧昏鍚庡啀鍒涘缓鐩綍 | module-registry.yaml 鍏堟湁涓€鏉¤褰曪紝鍐嶅垱寤虹墿鐞嗙洰褰?|
| 4 | 钃濆浘蹇呴』鍚?搂12 鏂藉伐鎸囧紩 | 涓嶅厑璁歌摑鍥剧己澶卞叿浣撳疄鏂芥楠?|
| 5 | 姣忎釜灞傜骇鐩綍蹇呴』鍚?README.md | 澹版槑鏈眰鑱岃矗鍜屽寘鍚殑妯″潡姒傝堪 |
| 6 | **涓€涓?module_id 鍙湁涓€涓?blueprint.md** | 鍚屼竴绯荤粺鐨勬枃妗ｄ笉鍙媶鍒嗕负澶氫釜钃濆浘銆傚闇€鎵╁睍鈫掑崌绾х幇鏈夎摑鍥撅紝涓嶆柊寤恒€傝繚鍙嶅嵆閲嶅閫犺疆瀛?|
| 7 | **鍒涘缓鏂拌摑鍥惧墠蹇呴』鏌ラ噸** | 蹇呴』鍦?module-registry.yaml 涓悳绱㈢浉鍚?閲嶅彔鑱岃矗銆傚彂鐜板凡閫€褰圭殑瀹屾垚钃濆浘鈫掕蛋鍗囩骇娴佺▼锛埪у叓锛?|
| 8 | **宸插畬鎴愯摑鍥惧繀鍚疄鐜扮姸鎬佽妭** | `construction_progress = phase_N_complete` 鐨勮摑鍥炬鏂囧繀椤诲垪鍑哄疄闄呬唬鐮佹枃浠舵槧灏勶紙搂鍏烽搧寰嬩簲锛?|
| 9 | **construction_progress 蹇呴』 LS 纾佺洏楠岃瘉** | AI 璁惧畾 construction_progress 鍓嶅繀椤诲厛鐢?`LS` 鎵弿鐩爣婧愮爜鐩綍锛屽嚟纾佺洏浜嬪疄鑰岄潪璁板繂/璁捐鎰忓浘濉啓锛埪у叓路閾佸緥鍏級 |

## 鍏€佽摑鍥炬煡閲嶄笌澶嶇敤鍗囩骇閾佸緥

> **瀵规爣**锛欿8s Admission Controller鈥斺€斾笉鍏佽閲嶅 CRD 杩涘叆闆嗙兢銆侷TIL Change Enablement鈥斺€斿彉鏇翠紭鍏堝崌绾х幇鏈?CI锛岀姝㈡柊寤洪噸澶嶉厤缃」銆?
### 閾佸緥涓€锛氳摑鍥惧敮涓€鐪熸簮

**涓€涓?module_id 鍙搴斾竴浠借摑鍥俱€?* 鍚屼竴绯荤粺/鍚屼竴鑱岃矗棰嗗煙蹇呴』鍙湁涓€涓摑鍥俱€傚鏋滃彂鐜颁袱浠借摑鍥炬弿杩板悓涓€绯荤粺鈥斺€旈偅鏄紡娲烇紝涓嶆槸鐗硅壊銆?
- 鉁?姝ｇ‘锛歚task-card-kms/` 钃濆浘 鈫?鍐呭鍗囩骇涓?`task-system/` 钃濆浘 鈫?鏃ц摑鍥炬爣璁板畬鎴?- 鉂?閿欒锛歚task-card-kms/` 鍜?`task-system/` 涓ゅ钃濆浘鍚屾椂 active 鈥斺€?璐ｄ换閲嶅彔

### 閾佸緥浜岋細鍒涘缓鍓嶅己鍒舵煡閲?
AI 鍦ㄥ垱寤轰换浣曟柊钃濆浘鍓嶏紝**蹇呴』鍏堟墽琛屼互涓嬫煡閲嶆祦绋?*锛?
```
Step 1: 鍦?module-registry.yaml 涓悳绱?        鈹溾攢鈹€ 鎸?name 鎼滅储锛氭槸鍚︽湁鍚屽悕/鐩镐技鍚嶆ā鍧楋紵
        鈹溾攢鈹€ 鎸?tags 鎼滅储锛氭槸鍚︽湁鐩稿悓鏍囩缁勫悎鐨勬ā鍧楋紵
        鈹斺攢鈹€ 鎸?purpose/summary 鎼滅储锛氭槸鍚︽湁瑕嗙洊鐩稿悓璐ｄ换棰嗗煙鐨勬ā鍧楋紵

Step 2: 濡傛灉鍙戠幇宸插瓨鍦ㄧ殑妯″潡
        鈹溾攢鈹€ status=deprecated 涓旀湁 superseded_by 鈫?杩欐槸宸插畬鎴愬伐浣?        鈹?    鈫?闇€瑕佹棰嗗煙鐨勬洿鏂帮紵
        鈹?      鈹溾攢鈹€ 鏄?鈫?璧?钃濆浘鍗囩骇娴佺▼"锛堣涓嬶級
        鈹?      鈹斺攢鈹€ 鍚?鈫?浣犱负浠€涔堣寤烘柊钃濆浘锛?        鈹斺攢鈹€ status=active/draft 鈫?璐ｄ换鍐茬獊
              鈫?鍋滄鍒涘缓銆傚悜 Owner 璇存槑鍐茬獊鎯呭喌锛岀瓑寰呰瀹氥€?
Step 3: 纭鏃犻噸鍙犲悗 鈫?姝ｅ父鍒涘缓鏂拌摑鍥?```

### 閾佸緥涓夛細澶嶇敤鍗囩骇娴佺▼锛堟浛鎹?鏂板缓"锛?
褰撳凡閫€褰圭殑瀹屾垚钃濆浘鐨勮矗浠婚鍩熷嚭鐜版柊闇€姹傛椂锛?*绂佹鏂板缓钃濆浘鈥斺€斿繀椤诲崌绾х幇鏈夎摑鍥?*锛?
```
钃濆浘鍗囩骇娴佺▼:
  1. 閿佸畾鐩爣钃濆浘锛氱‘璁?status=deprecated 鐨勮摑鍥惧唴瀹逛笌褰撳墠闇€姹傞珮搴﹂噸鍙?  2. 鐘舵€侀噸寮€锛氬皢璇ヨ摑鍥?status 浠?deprecated 鏀逛负 draft锛堝姞 frontmatter 澶囨敞"reopened for Phase N upgrade"锛?  3. 鍗囩骇瑙勫垯锛?     鈹溾攢鈹€ 鍘熷唴瀹瑰繀椤讳繚鐣欏湪 搂1-搂11 涓紝鏂板鍐呭杩藉姞/鎻掑叆锛屼笉鍙垹闄?     鈹溾攢鈹€ Version bump锛氬 v2.0.0 鈫?v3.0.0
     鈹溾攢鈹€ ADR 鍒涘缓锛氶噸澶у崌绾у繀椤诲垱寤?ADR锛堝 adr-nnnn-reopen-<module>.md锛?     鈹斺攢鈹€ superseded 閾炬洿鏂帮細濡傛灉璇ヨ摑鍥炬浘琚?superseded_by锛岄渶璇勪及鏄惁浠嶆寚鍚戞纭洰鏍?  4. 鎭㈠鏂藉伐锛氭寜 搂12 鏂藉伐鎸囧紩閲嶆柊鏂藉伐
  5. 瀹屾垚鍚庯細status 鈫?deprecated锛堟垨 approved锛夛紝construction_progress 鈫?phase_N_complete

  绂佹:
    鈹溾攢鈹€ 鉂?鐩存帴鍒涘缓鏂?module_id 瑕嗙洊鐩稿悓鑱岃矗
    鈹溾攢鈹€ 鉂?鍒犻櫎鏃ц摑鍥惧唴瀹?    鈹斺攢鈹€ 鉂?鏃犺鏌ラ噸娴佺▼鐩存帴寮€宸?```

### 閾佸緥鍥涳細宸插畬鎴愯摑鍥炬案涔呬繚鐣?
`construction_progress = phase_0_completed` 鎴?`phase_1_complete` 鐨勮摑鍥撅細
- **鏍囪 "鏋勫缓瀹屾垚"**锛氫笉鏄け璐ャ€佷笉鏄簾寮冣€斺€旀槸瀹屾垚浜嗚鍋氱殑浜?- **鐗╃悊鏂囦欢姘镐箙淇濈暀**锛氫綔涓虹郴缁熸紨杩涚殑鍘嗗彶璁板綍
- **鍙閲嶅紑鍗囩骇**锛氭湁鏂伴渶姹傛椂鎸夐搧寰嬩笁鍗囩骇

### 閾佸緥浜旓細钃濆浘蹇呴』璁拌浇瀹為檯瀹炵幇鐘舵€?
浠讳綍 `construction_progress = phase_N_complete` 鎴?`merged_into_blueprint` 鐨勮摑鍥撅紝**蹇呴』鍦ㄨ摑鍥炬鏂囦腑璁板綍瀹為檯浠ｇ爜瀹炵幇鎯呭喌**鈥斺€旇摑鍥剧殑鐪熸簮鑱岃矗涓嶄粎鍖呮嫭"璁捐浜嗕粈涔?锛岃繕鍖呮嫭"瀹炵幇浜嗕粈涔?銆?
**瑕佹眰**锛?- 钃濆浘蹇呴』鍚?`## 瀹為檯浠ｇ爜瀹炵幇鎯呭喌锛圕ode Implementation Status锛塦 鑺傦紙鎴栫瓑鏁堣妭鍙凤級
- 璇ヨ妭蹇呴』鍒楀嚭鐜版湁纾佺洏浠ｇ爜鏂囦欢鍙婂叾瀵瑰簲钃濆浘鑺傜殑鏄犲皠
- 鏃犱唬鐮佺殑绾璁¤摑鍥?鈫?`construction_progress` 蹇呴』涓?`not_started` 鎴?`skeleton`

**绂佹**锛?- 鉂?钃濆浘璇?宸插畬鎴?浣嗘棤浠ｇ爜鏂囦欢娓呭崟 鈫?铏氬亣澹版槑
- 鉂?钃濆浘 frontmatter 鏈?`construction_progress: phase_1_complete` 浣嗘鏂囨棤瀹炵幇鑺?鈫?鐘舵€佷笉涓€鑷?- 鉂?鍙洿鏂版敞鍐岃〃 YAML 浣嗕笉鏇存柊钃濆浘 .md 姝ｆ枃 鈫?钃濆浘鐪熸簮鍘熷垯琚繚鍙嶏紙YAML 娉ㄥ唽琛ㄦ槸绱㈠紩锛屼笉鏄湡婧愶級

> **澶х櫧璇?*锛欿8s 涓嶅厑璁镐袱涓悓鍚嶇殑 Deployment銆傛垜浠篃涓嶅厑璁镐袱濂楄摑鍥剧鍚屼竴浠朵簨銆傛煡閲嶆槸 AI 鐨勭涓€璐ｄ换鈥斺€斾笉鏌ュ氨寤虹瓑浜庨棴鐫€鐪肩潧閫犳ˉ銆傚彂鐜版棫鐨勫畬鎴愪簡鐨勮摑鍥撅紵鎵撳紑瀹冦€佸崌绾у畠銆佽褰曞畠鈥斺€斾笉瑕佸湪闅斿鍐嶇洊涓€鏍嬨€?

## 鎺掗櫎瑙勫垯锛堜笉搴旀斁鍏ユ湰鐩綍鐨勫唴瀹癸級

- 鉂?5 澶?AI 鏈嶅姟鐨勬帴鍙ｆ枃妗?鈫?`_b_track_interfaces/`锛堟湰鐩綍鍐咃級
- 鉂?椤圭洰绾у厓璁″垝/DevOps 娴佺▼ 鈫?`01_policies_and_standards/operational/devops/`
- 鉂?娌荤悊瑙勮寖/鏍囧噯 鈫?`01_policies_and_standards/governance/`
- 鉂?浼佷笟鏋舵瀯瑙嗗浘/ADR 鈫?`02_enterprise_architecture/`

## 鐖剁骇鐩綍

- 鐖剁骇锛歔docs 鏍圭洰褰昡(file:///D:/ZephyrAlpha/docs/index.md)
