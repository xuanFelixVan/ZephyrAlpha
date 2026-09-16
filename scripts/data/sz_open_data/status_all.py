# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §alt-data
# [MODULE] scripts.data.sz_open_data.status_all
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.shared.security.secrets; stdlib
# [CONSUMERS] Owner 夜班巡检 / 数据体检会话 / sz_open_data_catalog
# [STARTUP] manual
# [MATURITY] beta
# [INVARIANTS] 双钥匙探测（平台订阅按应用隔离，主钥匙+新钥匙逐接口轮试）；
#              仅两把钥匙全部无权限才判"未生效"进补订清单——单验主钥匙会集体误报
# [MODIFY-GUARD] none
# [STABILITY] beta
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单接口网络异常->记"受阻"不阻断全量核验
# [TESTS] 实弹脚本（输出 .runtime/tmp/szcatalog/subscribe_status.json 留痕）
# [TTL] permanent
"""47 接口订阅状态全量核验（双钥匙探测）+ 生成补订清单（含直达链接）。

2026-09-16 治本：深圳开放平台订阅按应用（appkey）隔离，本账号两个应用——
主钥匙 SZ_OPEN_DATA_APPKEY（首轮 23 接口）+ 新钥匙 SZ_OPEN_DATA_APPKEY_NEW
（0914 扩容批 24 接口）。旧版只拿主钥匙逐个验，绑定新钥匙的接口被集体误报
"未经许可的证书"（连续两班 AI 中招）。现改为双钥匙探测并输出每接口的钥匙归属，
仅两把钥匙都无权限的接口才进补订清单。
"""
import json
import threading
import urllib.request
import urllib.parse

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "X-Requested-With": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded"}
from zephyr.shared.security.secrets import get_secret_or_default
KEYS = {
    "主": get_secret_or_default("SZ_OPEN_DATA_APPKEY"),
    "新": get_secret_or_default("SZ_OPEN_DATA_APPKEY_NEW"),
}
MISSING = [k for k, v in KEYS.items() if not v]
if MISSING:
    print(f"⚠️ .env 缺少钥匙: {MISSING}（对应应用名下的接口将无法验证）")

ALL = {
    # 首轮 17（已验证过的）
    "29200/00901034": "热带气旋数据", "29200/00900329": "灾害性天气预警",
    "29200/00900289": "海洋气象预警", "29200/00903514": "历史登陆气旋",
    "29200/00903513": "台风中英文对照",
    "29200/03302370": "月报-国民经济核算", "29200/03302383": "月报-物价",
    "29200/03302382": "月报-财政金融", "29200/03302377": "月报-运输",
    "29200/03302379": "月报-对外贸易", "29200/51400003": "海港集装箱吞吐",
    "29200/51400004": "口岸进出口货物", "29200/51400006": "机场空运货物",
    "29200/03302369": "统计快报", "29200/03302375": "月报-固定资产投资",
    "29200/01903510": "一手商品房成交", "29200/01903513": "二手房成交",
    # 二轮 30
    "29200/00900227": "气候资料历史数据", "29200/00900273": "地面观测实况",
    "29200/00900291": "环境气象预报", "29200/01403151": "水库日降雨量",
    "29200/01000198": "空气质量日报", "29200/01003608": "区域空气质量",
    "29200/01903509": "二手房源信息", "29200/01903508": "商品房批准预售",
    "29200/01903511": "一手按面积成交", "29200/01300964": "市场主体发展统计",
    "29200/03302396": "企业登记发展", "29200/51400001": "口岸出入境人员",
    "29200/51400002": "口岸出入境车辆", "29200/00902986": "能见度探测",
    "29200/01400986": "水库水位表", "29200/01403149": "水库月降雨量",
    "29200/51400005": "机场出入境旅客", "29200/51400020": "客船进出港",
    "29200/03302384": "月报-民营经济", "29200/03302373": "月报-工业",
    "29200/03302374": "月报-工业经济效益", "29200/03302386": "月报-战略性新兴产业",
    "29200/03302380": "月报-外商直接投资", "29200/03302381": "月报-旅游",
    "29200/03302378": "月报-国内贸易", "29200/03302376": "月报-商品房建设",
    "29200/03302385": "月报-分区主要经济指标", "29200/03302387": "月报-年度主要经济指标",
    "29200/03302388": "月报-年度分区GDP", "29200/03302372": "统计分析",
}

def post(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA["User-Agent"]})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def probe(rid):
    """双钥匙逐把探测。返回 (状态, 生效钥匙名, 末次拒绝原因)。

    状态: "✅生效" / "未生效"（两把钥匙都无权限）/ "受阻"（网络/结构异常）。
    单钥匙被拒≠未订阅（订阅按应用隔离），只有全部钥匙都拒绝才判未生效。
    """
    doc = post("https://opendata.sz.gov.cn/data/api/getApiDocument", {"resId": rid})
    ctx = doc[0].get("api_context", "") if isinstance(doc, list) and doc else ""
    if not ctx:
        return "受阻", "", "NO api_context"
    api = f"https://opendata.sz.gov.cn/{ctx}"
    last_err = ""
    for key_name, key in KEYS.items():
        if not key:
            last_err = "钥匙未配置"
            continue
        r = get(f"{api}?{urllib.parse.urlencode({'page': 1, 'rows': 1, 'appKey': key})}")
        if isinstance(r, dict) and r.get("errorCode"):
            last_err = str(r.get("message"))[:20]
            continue
        return "✅生效", key_name, ""
    return "未生效", "", last_err

def main() -> None:
    """全量核验入口（__main__ 守卫：被 probe_all_new import 时零副作用）。"""
    status = []
    for rid, name in ALL.items():
        try:
            st, bound, msg = probe(rid)
            url = f"https://opendata.sz.gov.cn/data/api/toApiDetails/{rid.replace('/', '_')}" if st == "未生效" else ""
            label = st if st != "✅生效" else f"✅生效({bound}钥匙)"
            status.append((name, rid, label, msg, url, bound))
        except Exception as e:  # noqa: BLE001 — 单接口网络异常不阻断全量核验
            status.append((name, rid, "受阻", type(e).__name__, "", ""))
        threading.Event().wait(0.35)  # 限频退避：Event().wait 可中断（provider_base 惯例，PERM-TRIGGER 防复发）

    ok = [s for s in status if s[2].startswith("✅")]
    ok_main = sum(1 for s in ok if s[5] == "主")
    ok_new = sum(1 for s in ok if s[5] == "新")
    print(f"生效 {len(ok)}/{len(status)}（主钥匙 {ok_main} + 新钥匙 {ok_new}）\n")
    print("== 未生效/受阻清单（两把钥匙都无权限才会列出；去链接点订阅）==")
    for name, rid, st, msg, url, _ in status:
        if not st.startswith("✅"):
            print(f"  {name:<14} {rid}  {st} {msg}  {url}")
    json.dump(status, open('.runtime/tmp/szcatalog/subscribe_status.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print("\nsaved subscribe_status.json")


if __name__ == "__main__":
    main()
