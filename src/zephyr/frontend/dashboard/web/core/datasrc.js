/* ── 数据源监管页（Owner 2026-09-03：全接通真源）──
 * 真源=GET /api/sources-status：logs/source_health_*.log（scheduler 启动全源实探）+ data/failures/*.json（alerter 真实告警）
 * SLA burn-rate 块保持演示（30 日 SLA 落盘未接入，I-2）——诚实纪律不造数 */
var DS_ST = null;
var DS_TIMER = null;

function dsDot(l) { return { green: 'g', yellow: 'y', red: 'r', gray: 'w' }[l] || 'w'; }
function dsDotTxt(l) { return { green: '正常', yellow: '受限', red: '异常', gray: '退役' }[l] || l; }

function dsLoad() {
  if (!ZK.api) return;
  ZK.api.fetchSourcesStatus().then(function (st) {
    if (!st || !st.ok) throw new Error(st && st.error || 'bad payload');
    DS_ST = st;
    dsRenderKpi();
    dsRenderTable();
    dsRenderAlerts();
  }).catch(function (e) {
    var k = document.getElementById('ds-kpi');
    if (k && !k.innerHTML) {
      k.innerHTML = '<div class="card" style="border-left:3px solid var(--up);grid-column:1/-1"><b style="color:var(--up)">⚠ API 拉取失败（' + (e && e.message || e)
        + '）</b><div class="dim" style="font-size:11px;margin-top:4px">面板 API 未运行，10 秒后自动重试</div></div>';
    }
  });
}
function dsBoot() {
  dsLoad();
  if (!DS_TIMER) DS_TIMER = setInterval(dsLoad, 30000);   /* 健康探针结果低频变化，30s 轮询足够 */
}
dsBoot();

function dsRenderKpi() {
  var st = DS_ST; var k = document.getElementById('ds-kpi'); if (!k || !st) return;
  var srcN = st.sources.length;
  var lastFail = (st.failures && st.failures[0]) || null;
  k.innerHTML =
    '<div class="card metric"><div class="l">注册数据源</div><div class="v">' + srcN + '</div><div class="s">全源实探清单</div></div>'
    + '<div class="card metric"><div class="l">正常</div><div class="v up">' + st.ok_n + '</div><div class="s">探针通过（含行数实测）</div></div>'
    + '<div class="card metric"><div class="l">受限/异常</div><div class="v ' + (st.bad_n ? 'down' : '') + '">' + st.bad_n + '</div><div class="s">环境缺失或连接失败</div></div>'
    + '<div class="card metric"><div class="l">最近检查</div><div class="v" style="font-size:16px">' + (st.checked_at || '—').slice(5) + '</div><div class="s">scheduler 启动时全源实探</div></div>'
    + '<div class="card metric"><div class="l">最新告警</div><div class="v ' + (lastFail && lastFail.level === 'CRITICAL' ? 'down' : '') + '" style="font-size:16px">' + (lastFail ? lastFail.level : '—') + '</div><div class="s">' + (lastFail ? (lastFail.task_id || '').slice(0, 26) : '无失败汇总') + '</div></div>';
}

function dsRenderTable() {
  var st = DS_ST; var box = document.getElementById('ds-table'); if (!box || !st) return;
  var ca = document.getElementById('ds-checked-at');
  if (ca) ca.textContent = st.checked_at || '—';
  var order = { green: 0, yellow: 1, red: 2, gray: 3 };
  var rows = st.sources.slice().sort(function (a, b) { return order[a.light] - order[b.light]; });
  var h = '<table><tr><th>源</th><th>能力</th><th>状态</th><th>探针实测</th></tr>';
  rows.forEach(function (s) {
    h += '<tr><td><b>' + s.name + '</b></td><td>' + s.caps + '</td>'
      + '<td><span class="dot ' + dsDot(s.light) + '"></span>' + dsDotTxt(s.light) + '</td>'
      + '<td style="font-size:11px;color:var(--dim)">' + (s.detail || '—') + '</td></tr>';
  });
  box.innerHTML = h + '</table>';
}

function dsRenderAlerts() {
  var st = DS_ST; var box = document.getElementById('ds-alerts'); if (!box || !st) return;
  var list = st.failures || [];
  if (!list.length) { box.innerHTML = '<div class="dim" style="padding:6px 0">无失败汇总（failures/ 空）——各源运行干净</div>'; return; }
  var lvBadge = function (lv) {
    if (lv === 'CRITICAL' || lv === 'ERROR') return '<span class="badge b-fail">' + lv + '</span>';
    if (lv === 'WARN') return '<span class="badge b-warn">WARN</span>';
    return '<span class="badge b-na">' + lv + '</span>';
  };
  box.innerHTML = '<table><tr><th style="width:118px">时间</th><th>事件</th><th style="width:76px">级别</th></tr>'
    + list.map(function (a) {
      return '<tr><td style="font-size:11px">' + a.ts.slice(5, 16) + '</td>'
        + '<td style="font-size:11px"><b>' + a.task_id + '</b> <span class="dim">[' + a.source + ']</span><br><span class="dim">' + a.error + '</span></td>'
        + '<td>' + lvBadge(a.level) + '</td></tr>';
    }).join('') + '</table>';
}
