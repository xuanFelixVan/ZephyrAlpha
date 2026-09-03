/* ── 数据下载监管页（Owner 2026-09-03：所有数据（非数据源）的下载实况）──
 * 真源=GET /api/download-status：CH system.parts 按 (db,table) 聚合（最新分区/行数/parts）
 * 灯=数据龄 vs 表名启发预期周期（日频 3-4 天/周 12/月 45）；红表置顶=断更预警 */
var DL_ST = null;
var DL_TIMER = null;
var DL_DB = "全部库";
var DL_ORDER = { red: 0, yellow: 1, green: 2, gray: 3 };

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
  k.innerHTML =
    '<div class="card metric"><div class="l">在管数据表</div><div class="v">' + st.tables.length + '</div><div class="s">c0/c1/c3 业务库</div></div>'
    + '<div class="card metric"><div class="l">正常</div><div class="v up">' + c.green + '</div><div class="s">最新数据在预期周期内</div></div>'
    + '<div class="card metric"><div class="l">滞后观察</div><div class="v" style="color:var(--yellow)">' + c.yellow + '</div><div class="s">超预期 1-3 倍</div></div>'
    + '<div class="card metric"><div class="l">疑似断更</div><div class="v ' + (c.red ? 'down' : '') + '">' + c.red + '</div><div class="s">超预期 3 倍——优先排查</div></div>'
    + '<div class="card metric"><div class="l">无分区表</div><div class="v na">' + c.gray + '</div><div class="s">元数据小表，不算异常</div></div>';
}

function dlRender() {
  var st = DL_ST; var box = document.getElementById('dl-table'); if (!box || !st) return;
  var q = (document.getElementById('dl-q') || {}).value || '';
  var rows = st.tables.filter(function (t) {
    if (DL_DB !== "全部库" && t.db !== DL_DB) return false;
    return !q || t.table.toLowerCase().indexOf(q.toLowerCase()) >= 0;
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
  var h = '<table><tr><th style="width:34px"></th><th>表</th><th style="width:110px">最新数据</th><th style="width:120px">数据龄</th><th style="width:110px">行数</th><th style="width:70px">parts</th></tr>';
  rows.forEach(function (t) {
    h += '<tr><td><span class="dot ' + dlDot(t.light) + '" title="' + dlDotTxt(t.light) + '"></span></td>'
      + '<td><b>' + t.table + '</b> <span class="dim" style="font-size:10px">' + t.db + '</span></td>'
      + '<td style="font-size:11px">' + (t.latest === '' ? '—' : t.latest) + '</td>'
      + '<td style="font-size:11px">' + (t.days != null ? t.days + ' 天前' : '—') + '</td>'
      + '<td style="font-size:11px">' + (t.rows >= 1e8 ? (t.rows / 1e8).toFixed(1) + ' 亿' : t.rows >= 1e4 ? (t.rows / 1e4).toFixed(1) + ' 万' : t.rows.toLocaleString()) + '</td>'
      + '<td style="font-size:11px">' + t.parts + '</td></tr>';
  });
  box.innerHTML = h + '</table><div class="dim" style="font-size:11px;padding:6px 2px">' + rows.length + ' / ' + st.tables.length + ' 张表</div>';
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
