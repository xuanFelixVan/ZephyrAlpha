/* ── 数据监管页 v3（Owner 2026-09-10：数据总览并入本页一表——下载实况 30s + 库内资产慢档 10min/手动体检）──
 * 真源=GET /api/download-status（CH system.parts+query_log+tasks.yaml，30s 轮询）
 *     + GET /api/data-asset（列扫描聚合审计：宽度/深度/完整度/缺口/存储层，内存缓存 10min 慢档+手动"深度体检"） */
var DL_ST = null;
var DL_TIMER = null;
var DL_ASSET = null;         /* 库内资产审计结果 {running,done,total,audited_at,tables:{"db.table":rec}} */
var DL_AS_TIMER = null;
var DL_DB = "全部库";
var DL_ONLY_ISSUE = false;
var DL_ORDER = { red: 0, yellow: 1, green: 2, gray: 3 };
var DL_STATE = { downloading: ["g", "正在下载"], idle: ["g", "正常"], lagging: ["y", "滞后"], stalled: ["r", "疑似断更"] };
var DL_TIER_ZH = { hot: "热", warm: "常规", cold: "冷" };
/* Excel 式表头排序（Owner 2026-09-04）：点表头升序、同列再点切降序，来回切换；换列重置升序；箭头指示当前方向
 * 列分两组（2026-09-10 合并裁定）：下载情况（30s 刷新）| 库内资产（慢档体检）——未体检行排最后（9e15 哨兵） */
var DL_SORT = { key: null, dir: 1 };
function dlAssetOf(t) { return (DL_ASSET && DL_ASSET.tables && DL_ASSET.tables[t.db + "." + t.table]) || null; }
var DL_COLS = {
  name:   { label: "数据（中文/表名）", w: 0,   str: 1, get: function (t) { return (t.name_zh || "\uFF3F" + t.table) + "\u0001" + t.table; } },
  state:  { label: "下载状态", w: 96,  num: 1, get: function (t) { return { downloading: 1, lagging: 2, stalled: 3, idle: 4 }[t.state] || 9; } },
  rate:   { label: "速率·质量", w: 96,  num: 1, get: function (t) { return t.rate || 0; } },
  today:  { label: "今日新增", w: 84,  num: 1, get: function (t) { return t.today_rows || 0; } },
  next:   { label: "下次下载", w: 120, str: 1, get: function (t) { return t.next_dl || "\uFF5E"; } },
  period: { label: "数据时间段", w: 150, str: 1, get: function (t) { return t.latest || ""; } },
  awidth: { label: "宽度 覆盖/应有", w: 110, num: 1, get: function (t) { var a = dlAssetOf(t); if (!a || a.width == null) return 9e15; return a.expected_width ? a.width / a.expected_width : a.width; } },
  adepth: { label: "深度 时间范围", w: 168, str: 1, get: function (t) { var a = dlAssetOf(t); return a && a.dmin ? a.dmin + "~" + (a.dmax || "") : "\uFF5E"; } },
  acompl: { label: "完整度", w: 74,  num: 1, get: function (t) { var a = dlAssetOf(t); return a && a.completeness != null ? a.completeness : 9e15; } },
  agap:   { label: "缺口", w: 62,  num: 1, get: function (t) { var a = dlAssetOf(t); return a && a.gap_days != null ? a.gap_days : 9e15; } },
  tier:   { label: "存储层", w: 60,  str: 1, get: function (t) { var a = dlAssetOf(t); return a ? (a.tier || "warm") : "\uFF5E"; } },
  source: { label: "数据源", w: 100, str: 1, get: function (t) { return t.source || ""; } },
  vpn:    { label: "VPN", w: 110, str: 1, get: function (t) { return t.vpn_need || "\uFF5E"; } },
  rows:   { label: "行数", w: 70,  num: 1, get: function (t) { return t.rows || 0; } },
  fail:   { label: "关联告警", w: 130, num: 1, get: function (t) { return t.fail_cnt || 0; } }
};
function dlSortBy(key) {
  if (DL_SORT.key === key) DL_SORT.dir = -DL_SORT.dir;   /* 同列二连点：升↔降 */
  else { DL_SORT.key = key; DL_SORT.dir = 1; }           /* 换列：回到升序（Excel 惯例） */
  dlRender();
}
function dlTh(key) {
  var c = DL_COLS[key];
  var on = DL_SORT.key === key;
  var arrow = on ? '<span style="color:#3D8BFF">' + (DL_SORT.dir === 1 ? "▲" : "▼") + "</span>" : "";
  return "<th" + (c.w ? ' style="width:' + c.w + 'px"' : "")
    + ' onclick="dlSortBy(\'' + key + '\')" title="点击排序 · 再点同列切换升/降"'
    + '><span style="cursor:pointer;-webkit-user-select:none;user-select:none"' + (on ? ";color:var(--text)" : "") + ">"
    + c.label + (arrow ? " " + arrow : "") + "</span></th>";
}

function dlDot(l) { return { green: 'g', yellow: 'y', red: 'r', gray: 'w' }[l] || 'w'; }
function dlDotTxt(l) { return { green: '正常', yellow: '滞后', red: '疑似断更', gray: '无分区' }[l] || l; }

function dlLoad() {
  if (!ZK.api) return;
  ZK.api.fetchDownloadStatus().then(function (st) {
    if (!st || !st.ok) throw new Error(st && st.error || 'bad payload');
    DL_ST = st;
    ZK.api.swrSave('zk_dl_v1', st);   /* SWR：新数据落缓存供下次刷新秒出 */
    dlRenderKpi();
    dlRender();
  }).catch(function (e) {
    var k = document.getElementById('dl-kpi');
    if (k && !k.innerHTML) {
      k.innerHTML = '<div class="card" style="border-left:3px solid var(--up);grid-column:1/-1"><b style="color:var(--up)">⚠ API 拉取失败（' + (e && e.message || e)
        + '）</b><div class="dim" style="font-size:11px;margin-top:4px">面板 API 未运行或 CH 断连，30 秒后自动重试</div></div>';
    }
  });
}
function dlBoot() {
  /* SWR（2026-09-03）：刷新先渲染上次数据（KPI 区尾标「缓存·上次 HH:MM」），后台拉新到达自动覆盖 */
  if (ZK.api) ZK.api.swrLoad('zk_dl_v1', function (st, ts) {
    DL_ST = st;
    dlRenderKpi();
    dlRender();
    var k = document.getElementById('dl-kpi');
    if (k) k.innerHTML += '<div class="card metric"><div class="l">缓存</div><div class="v" style="font-size:14px">上次 '
      + ts.toTimeString().slice(0, 5) + '</div><div class="s">正在拉取最新…</div></div>';
  });
  dlLoad();
  if (!DL_TIMER) DL_TIMER = setInterval(dlLoad, 30000);
  /* 库内资产慢档（2026-09-10 合并裁定）：60s 拉缓存秒回（后端超龄 10min 自动重审）+ SWR 首屏 */
  if (ZK.api) ZK.api.swrLoad('zk_asset_v1', function (st) {
    DL_ASSET = st;
    dlRender();
  });
  dlAssetLoad(false);
  if (!DL_AS_TIMER) DL_AS_TIMER = setInterval(function () { dlAssetLoad(false); }, 60000);
}

function dlAssetLoad(kick) {
  if (!ZK.api) return;
  ZK.api.fetchDataAsset(kick).then(function (st) {
    if (!st || !st.ok) return;
    DL_ASSET = st;
    ZK.api.swrSave('zk_asset_v1', st);   /* SWR：资产审计结果落缓存供刷新秒出 */
    var b = document.getElementById('dl-asset-btn');
    if (b) b.textContent = st.running ? '体检中 ' + (st.done || 0) + '/' + (st.total || '?') : '深度体检';
    var ts = document.getElementById('dl-asset-ts');
    if (ts) ts.textContent = st.audited_at ? '资产列上次体检 ' + st.audited_at.slice(5, 16) : '';
    dlRender();
  }).catch(function () {});
}
function dlAssetKick(el) {
  el.textContent = '体检中…';
  dlAssetLoad(true);
}
dlBoot();

function dlRenderKpi() {
  var st = DL_ST; var k = document.getElementById('dl-kpi'); if (!k || !st) return;
  var c = st.counts;
  var vpn = st.vpn_on;
  k.innerHTML =
    '<div class="card metric"><div class="l">在管数据表</div><div class="v">' + st.tables.length + '</div><div class="s">c0/c1/c3 业务库</div></div>'
    + '<div class="card metric"><div class="l">正在下载</div><div class="v up">' + (st.dl_now || 0) + '</div><div class="s">近 15 分钟有写入（rows/s 实测）</div></div>'
    + '<div class="card metric"><div class="l">正常</div><div class="v up">' + c.green + '</div><div class="s">最新数据在预期周期内</div></div>'
    + '<div class="card metric"><div class="l">滞后/断更</div><div class="v ' + (c.red ? 'down' : '') + '" style="color:' + (c.red ? '' : 'var(--yellow)') + '">' + c.yellow + ' / <b style="color:var(--up)">' + c.red + '</b></div><div class="s">滞后观察 / 疑似断更</div></div>'
    + '<div class="card metric"><div class="l">VPN 通道</div><div class="v ' + (vpn ? 'up' : 'na') + '" style="font-size:16px">' + (vpn ? '● 开启中' : '○ 关闭') + '</div><div class="s">海外源需开 · 国内源需关（详见表内 VPN 列）</div></div>';
}

function dlRender() {
  var st = DL_ST; var box = document.getElementById('dl-table'); if (!box || !st) return;
  var q = (document.getElementById('dl-q') || {}).value || '';
  var rows = st.tables.filter(function (t) {
    if (DL_DB !== "全部库" && t.db !== DL_DB) return false;
    if (DL_ONLY_ISSUE && t.light === 'green' && t.light === 'gray') return false;
    if (DL_ONLY_ISSUE && !(t.light === 'red' || t.light === 'yellow')) return false;
    return !q || t.table.toLowerCase().indexOf(q.toLowerCase()) >= 0
      || (t.name_zh && t.name_zh.indexOf(q) >= 0);
  }).sort(function (a, b) {
    if (DL_SORT.key) {   /* Excel 式：点了表头按该列排 */
      var c = DL_COLS[DL_SORT.key];
      var x = c.get(a), y = c.get(b);
      return (c.num ? x - y : String(x).localeCompare(String(y), "zh-CN")) * DL_SORT.dir;
    }
    return DL_ORDER[a.light] - DL_ORDER[b.light] || a.db.localeCompare(b.db) || a.table.localeCompare(b.table);
  });
  var dbs = {};
  st.tables.forEach(function (t) { dbs[t.db] = 1; });
  var menu = document.getElementById('dl-db-menu');
  if (menu && !menu.dataset.built) {
    menu.dataset.built = 1;
    menu.innerHTML = ['全部库'].concat(Object.keys(dbs).sort()).map(function (d) {
      return '<span class="acct-mi' + (d === DL_DB ? ' on' : '') + '" data-v="' + d + '" onclick="dlPickDb(\'' + d + '\',event)">' + (d === DL_DB ? '✓ ' : '') + d + '</span>';
    }).join('');
  }
  var h = "<table><tr>" + Object.keys(DL_COLS).map(dlTh).join("") + "</tr>";
  rows.forEach(function (t) {
    var stt = DL_STATE[t.state] || ['w', t.state];
    var rate = t.state === 'downloading' ? '<b>' + t.rate + '</b> 行/s · ' + t.quality : '—';
    var vpn = t.vpn_need === '需'
      ? '<span class="' + (vpn ? 'up' : 'down') + '">' + (vpn ? '需·已开 ✓' : '需·未开 ✗') + '</span>'
      : t.vpn_need === '禁'
        ? '<span class="dim">禁 VPN</span>'
        : '<span class="dim">—</span>';
    var fail = t.fail_cnt
      ? '<span class="down">' + t.fail_cnt + ' 条</span><br><span class="dim" style="font-size:10px">' + t.fail_last + '</span>'
      : '<span class="dim">—</span>';
    h += '<tr>'
      + '<td><b>' + (t.name_zh || t.table) + '</b>' + (t.name_zh ? ' <span class="dim" style="font-size:10px">' + t.table + '</span>' : '')
      + (t.schedule_zh ? '<br><span class="dim" style="font-size:10px">⏰ ' + t.schedule_zh + '</span>' : '') + '</td>'
      + '<td><span class="dot ' + stt[0] + '"></span>' + stt[1] + '</td>'
      + '<td style="font-size:11px">' + rate + '</td>'
      + '<td style="font-size:11px">' + dlTodayCell(t) + '</td>'
      + '<td style="font-size:11px">' + (t.next_dl || '<span class="dim">—</span>') + '</td>'
      + '<td style="font-size:11px">' + t.period + '</td>'
      + '<td style="font-size:11px">' + dlAssetWidthCell(dlAssetOf(t)) + '</td>'
      + '<td style="font-size:11px">' + dlAssetDepthCell(dlAssetOf(t)) + '</td>'
      + '<td style="font-size:11px">' + dlAssetPctCell(dlAssetOf(t)) + '</td>'
      + '<td style="font-size:11px">' + dlAssetGapCell(dlAssetOf(t)) + '</td>'
      + '<td style="font-size:11px">' + dlAssetTierCell(dlAssetOf(t)) + '</td>'
      + '<td style="font-size:11px">' + t.source + '</td>'
      + '<td style="font-size:11px">' + vpn + '</td>'
      + '<td style="font-size:11px">' + (t.rows >= 1e8 ? (t.rows / 1e8).toFixed(1) + ' 亿' : t.rows >= 1e4 ? (t.rows / 1e4).toFixed(1) + ' 万' : t.rows.toLocaleString()) + '</td>'
      + '<td style="font-size:11px">' + fail + '</td></tr>';
  });
  box.innerHTML = h + '</table><div class="dim" style="font-size:11px;padding:6px 2px">' + rows.length + ' / ' + st.tables.length + ' 张表</div>';
}

/* F6（迁移台账 2026-09-09）：tick_data 今日新增按 data_source 分组渲染（mini/桥 两段并存）。
 * 背景：9/18 miniqmt 退役停写后，合计"今日新增"将从 ~2000 万缩水到 ~70 万（30 倍），
 * 合计口径会被误读为断；分组后桥通道行独立可见。无分组明细的表走原合计渲染。 */
function dlFmtWan(n) {
  return n >= 1e4 ? (n / 1e4).toFixed(1) + ' 万' : n.toLocaleString();
}
function dlTodayCell(t) {
  var by = t.today_rows_by_source;
  if (t.table !== 'tick_data' || !by) {
    return t.today_rows ? '<b class="up">' + dlFmtWan(t.today_rows) + '</b>' : '—';
  }
  var parts = [];
  if (by.miniqmt) parts.push('<span class="dim">mini</span> ' + dlFmtWan(by.miniqmt));
  if (by.qmt_bridge) parts.push('<b class="up">桥 ' + dlFmtWan(by.qmt_bridge) + '</b>');
  if (!parts.length) return t.today_rows ? '<b class="up">' + dlFmtWan(t.today_rows) + '</b>' : '—';
  return parts.join('<br>') + (t.today_rows ? '<br><span class="dim" style="font-size:10px">合计 ' + dlFmtWan(t.today_rows) + '</span>' : '');
}

function dlToggleIssue(el) {
  DL_ONLY_ISSUE = !DL_ONLY_ISSUE;
  el.classList.toggle('primary', DL_ONLY_ISSUE);
  dlRender();
}

/* ── 库内资产列渲染（2026-09-10 合并裁定：宽度/深度/完整度/缺口/存储层）──
 * 未体检（DL_ASSET 为空/该表无记录）=「…」；体检过但该列无值（无 symbol 列/7×24 表无缺口口径/空表深度）=「—」；
 * 完整度/缺口按表自身频率口径（a.freq：weekly/monthly/quarterly 按应出周期数比对，event=事件驱动不报） */
function dlAssetFreqUnit(a) {
  return {weekly: ' 周', monthly: ' 月', quarterly: ' 季'}[a.freq] || ' 天';
}
function dlAssetFreqTip(a) {
  return {weekly: '按周口径审计（应出周数比对）', monthly: '按月口径审计（应出月数比对）',
          quarterly: '按季口径审计（应出季数比对）'}[a.freq] || '按 A 股交易日口径审计';
}
function dlAssetWidthCell(a) {
  if (!a) return '<span class="dim">…</span>';
  if (a.width == null) return '<span class="dim">—</span>';
  var pct = a.expected_width ? Math.round(a.width / a.expected_width * 1000) / 10 : null;
  var col = pct == null ? 'var(--text)' : pct >= 99 ? 'var(--up)' : pct >= 90 ? 'var(--yellow)' : '#CA3F64';
  return '<b style="color:' + col + '">' + dlFmtWan(a.width) + '</b>'
    + (a.expected_width ? '<br><span class="dim" style="font-size:10px">/ ' + dlFmtWan(a.expected_width) + ' · ' + pct + '%</span>' : '');
}
function dlAssetDepthCell(a) {
  if (!a) return '<span class="dim">…</span>';
  return a.dmin ? a.dmin + ' ~ ' + (a.dmax || '?') : '<span class="dim">—</span>';
}
function dlAssetPctCell(a) {
  if (!a) return '<span class="dim">…</span>';
  if (a.completeness == null) {
    if (a.freq === 'event') return '<span class="dim" title="事件驱动表：行随事件出现，无完整度/缺口口径">事件</span>';
    return '<span class="dim">—</span>';
  }
  var v = a.completeness;
  var col = v >= 99 ? 'var(--up)' : v >= 90 ? 'var(--yellow)' : '#CA3F64';
  return '<b style="color:' + col + '">' + v + '%</b>';
}
function dlAssetGapCell(a) {
  if (!a) return '<span class="dim">…</span>';
  if (a.freq === 'event') return '<span class="dim">—</span>';
  if (a.gap_days == null) return '<span class="dim">—</span>';
  return a.gap_days > 0
    ? '<b style="color:#CA3F64" title="' + dlAssetFreqTip(a) + '">' + a.gap_days + dlAssetFreqUnit(a) + '</b>'
    : '<span class="up" title="' + dlAssetFreqTip(a) + '">0</span>';
}
function dlAssetTierCell(a) {
  if (!a) return '<span class="dim">…</span>';
  return '<span class="dim">' + (DL_TIER_ZH[a.tier] || a.tier || '常规') + '</span>';
}
function dlPickDb(d, e) {
  if (e && e.stopPropagation) e.stopPropagation();
  DL_DB = d;
  var t = document.getElementById('dl-db-t');
  if (t) t.textContent = d;
  var m = document.getElementById('dl-db-menu');
  if (m) m.classList.remove('open');
  dlRender();
}
function dlDropTgl(e) {
  e.stopPropagation();
  var m = e.currentTarget.querySelector('.acct-menu');
  if (m) m.classList.toggle('open');
}
document.addEventListener('click', function (e) {
  var m = document.getElementById('dl-db-menu');
  if (m && m.classList.contains('open') && !m.parentNode.contains(e.target)) m.classList.remove('open');
});
