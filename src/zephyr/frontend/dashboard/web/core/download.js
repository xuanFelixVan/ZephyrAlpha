/* ── 数据下载监管页 v2（Owner 2026-09-03：中文名/源/时间段/实时速率/质量/VPN 联动全上）──
 * 真源=GET /api/download-status：CH system.parts（新鲜度+时间段）+ query_log（近 15 分钟 INSERT 实时速率）+ tasks.yaml（源/调度映射）+ 源级 VPN 属性登记 */
var DL_ST = null;
var DL_TIMER = null;
var DL_DB = "全部库";
var DL_ONLY_ISSUE = false;
var DL_ORDER = { red: 0, yellow: 1, green: 2, gray: 3 };
var DL_STATE = { downloading: ["g", "正在下载"], idle: ["g", "正常"], lagging: ["y", "滞后"], stalled: ["r", "疑似断更"] };

function dlDot(l) { return { green: 'g', yellow: 'y', red: 'r', gray: 'w' }[l] || 'w'; }
function dlDotTxt(l) { return { green: '正常', yellow: '滞后', red: '疑似断更', gray: '无分区' }[l] || l; }

function dlLoad() {
  if (!ZK.api) return;
  ZK.api.fetchDownloadStatus().then(function (st) {
    if (!st || !st.ok) throw new Error(st && st.error || 'bad payload');
    DL_ST = st;
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
  dlLoad();
  if (!DL_TIMER) DL_TIMER = setInterval(dlLoad, 30000);
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
  var h = '<table><tr><th style="width:76px">下载状态</th><th>数据（中文/表名）</th><th style="width:110px">数据源</th>'
    + '<th style="width:150px">数据时间段</th><th style="width:110px">下载速率</th><th style="width:60px">质量</th>'
    + '<th style="width:120px">VPN</th><th style="width:80px">行数</th></tr>';
  rows.forEach(function (t) {
    var stt = DL_STATE[t.state] || ['w', t.state];
    var rate = t.state === 'downloading' ? '<b>' + t.rate + '</b> 行/s' : '—';
    var vpn = t.vpn_need === '需'
      ? '<span class="' + (vpn ? 'up' : 'down') + '">' + (vpn ? '需 VPN·已开 ✓' : '需 VPN·未开 ✗') + '</span>'
      : t.vpn_need === '禁'
        ? '<span class="dim">禁 VPN</span>'
        : '<span class="dim">—</span>';
    h += '<tr><td><span class="dot ' + stt[0] + '"></span>' + stt[1] + '</td>'
      + '<td><b>' + (t.name_zh || t.table) + '</b>' + (t.name_zh ? ' <span class="dim" style="font-size:10px">' + t.table + '</span>' : '')
      + (t.schedule_zh ? '<br><span class="dim" style="font-size:10px">⏰ ' + t.schedule_zh + '</span>' : '') + '</td>'
      + '<td style="font-size:11px">' + t.source + (t.vpn_note ? '<br><span class="dim" style="font-size:10px">' + t.vpn_note + '</span>' : '') + '</td>'
      + '<td style="font-size:11px">' + t.period + '</td>'
      + '<td style="font-size:11px">' + rate + '</td>'
      + '<td style="font-size:11px">' + t.quality + '</td>'
      + '<td style="font-size:11px">' + vpn + '</td>'
      + '<td style="font-size:11px">' + (t.rows >= 1e8 ? (t.rows / 1e8).toFixed(1) + ' 亿' : t.rows >= 1e4 ? (t.rows / 1e4).toFixed(1) + ' 万' : t.rows.toLocaleString()) + '</td></tr>';
  });
  box.innerHTML = h + '</table><div class="dim" style="font-size:11px;padding:6px 2px">' + rows.length + ' / ' + st.tables.length + ' 张表</div>';
}

function dlToggleIssue(el) {
  DL_ONLY_ISSUE = !DL_ONLY_ISSUE;
  el.classList.toggle('primary', DL_ONLY_ISSUE);
  dlRender();
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
