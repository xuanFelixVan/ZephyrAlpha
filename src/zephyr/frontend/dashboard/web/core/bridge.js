/* ── 交易通道监控页（Owner 2026-09-04：量化系统主动脉专职监护）──
 * 真源=GET /api/bridge-status：HTTP 桥 GET /health（EXEC v16.4 沙箱 18901）+ 桥文件族活性 + miniqmt 存活
 * 速度对比基线=93 号备忘 §12.6 盘中实测（HTTP 32ms / mini 41ms / 文件 5.7s 中位）+ 当前探活实测 */
var BR_ST = null;
var BR_TIMER = null;

/* 盘中实测基线（93 号备忘 §12.6，2026-09-04 三方对比 5 次取中位） */
var BR_SPEED_BASE = [
  { item: '下单端到端（指令→柜台受理）', http: '32ms', mini: '41ms', note: 'HTTP 已追平基线（0.78×）' },
  { item: '撤单指令', http: '亚秒（直投）', mini: '41ms', note: 'HTTP 撤单同通道直投' },
  { item: '行情快照滞后', http: '3-6s（v17 线程）', mini: '1.2-3.2s', note: '数据源同为 3s 快照，桥开销 +2-4s' },
  { item: '成交回报感知', http: '秒级（deals_events）', mini: '回调即时', note: '轮询模型，盯盘够用' },
  { item: '文件兜底通道（降级）', http: '5.7s', mini: '—', note: 'handlebar 驱动，HTTP 失效时自动切换' },
  { item: '订阅广度', http: '200 只实测零丢', mini: '不限', note: 'quote_symbols.txt 热更新' }
];

function brDot(l) { return { green: 'g', yellow: 'y', red: 'r', gray: 'w' }[l] || 'w'; }
function brDotTxt(l) { return { green: '正常', yellow: '观察', red: '断线', gray: '休市/停滞' }[l] || l; }

function brLoad() {
  if (!ZK.api) return;
  ZK.api.fetchBridgeStatus().then(function (st) {
    if (!st || !st.ok) throw new Error(st && st.error || 'bad payload');
    BR_ST = st;
    brRenderKpi();
    brRenderSpeed();
    brRenderHttp();
    brRenderFiles();
  }).catch(function (e) {
    var k = document.getElementById('br-kpi');
    if (k && !k.innerHTML) {
      k.innerHTML = '<div class="card" style="border-left:3px solid var(--up);grid-column:1/-1"><b style="color:var(--up)">⚠ API 拉取失败（' + (e && e.message || e)
        + '）</b><div class="dim" style="font-size:11px;margin-top:4px">面板 API 未运行，10 秒后自动重试</div></div>';
    }
  });
}
function brBoot() {
  brLoad();
  if (!BR_TIMER) BR_TIMER = setInterval(brLoad, 10000);
}
brBoot();

function brRenderKpi() {
  var st = BR_ST; var k = document.getElementById('br-kpi'); if (!k || !st) return;
  var h = st.http || {};
  var alive = h.alive;
  // 倒计时
  var cd = document.getElementById('br-countdown');
  if (cd) {
    var days = Math.ceil((new Date(st.retire_date) - new Date()) / 86400000);
    cd.textContent = 'miniQMT 退役倒计时 ' + Math.max(0, days) + ' 天';
  }
  var httpOk = h.stats ? (parseInt(h.stats.http_ok || '0', 10) + parseInt(h.stats.thread_ok || '0', 10)) : 0;
  var badFiles = (st.files || []).filter(function (f) { return f.light === 'red'; }).length;
  k.innerHTML =
    '<div class="card metric"><div class="l">HTTP 桥</div><div class="v ' + (alive ? 'up' : 'down') + '">' + (alive ? '在线' : '离线') + '</div><div class="s">探活 ' + (h.ms || '--') + 'ms · 18901</div></div>'
    + '<div class="card metric"><div class="l">桥累计下单</div><div class="v">' + httpOk + '</div><div class="s">http+thread 计数器</div></div>'
    + '<div class="card metric"><div class="l">文件族异常</div><div class="v ' + (badFiles ? 'down' : 'up') + '">' + badFiles + '</div><div class="s">红=文件缺失</div></div>'
    + '<div class="card metric"><div class="l">miniQMT 基线</div><div class="v" style="color:' + (st.mini_alive ? 'var(--text)' : 'var(--dim)') + '">' + (st.mini_alive ? '存活' : '已停') + '</div><div class="s">退役后转历史基线</div></div>'
    + '<div class="card metric"><div class="l">当前探活延迟</div><div class="v" style="font-size:16px">' + (alive ? (h.ms + 'ms') : '--') + '</div><div class="s">GET /health 往返</div></div>';
}

function brRenderSpeed() {
  var st = BR_ST; var box = document.getElementById('br-speed'); if (!box || !st) return;
  var alive = st.http && st.http.alive;
  var h = '<table><tr><th>指标</th><th style="width:170px">QMT HTTP 桥</th><th style="width:170px">miniQMT（基线）</th><th>说明</th></tr>';
  BR_SPEED_BASE.forEach(function (r) {
    h += '<tr><td><b>' + r.item + '</b></td>'
      + '<td class="' + (alive ? 'up' : '') + '" style="font-weight:600">' + (alive ? r.http : r.http + '（桥离线）') + '</td>'
      + '<td style="color:var(--dim)">' + r.mini + '</td>'
      + '<td style="font-size:11px;color:var(--dim)">' + r.note + '</td></tr>';
  });
  // 探活实测行
  if (st.http) {
    h += '<tr><td><b>探活实测（当前）</b></td>'
      + '<td>' + (st.http.alive ? '<b class="up">' + st.http.ms + 'ms</b>' : '<span class="down">离线</span>') + '</td>'
      + '<td style="color:var(--dim)">' + (st.mini_alive ? '进程存活' : '—') + '</td>'
      + '<td style="font-size:11px;color:var(--dim)">' + (st.http.detail || '').slice(0, 60) + '</td></tr>';
  }
  box.innerHTML = h + '</table>';
}

function brRenderHttp() {
  var st = BR_ST; var box = document.getElementById('br-http'); if (!box || !st) return;
  var h = st.http || {};
  var rows = [
    { name: 'HTTP 桥（18901）', light: h.alive ? 'green' : 'red', detail: h.alive ? ('在线 · 探活 ' + h.ms + 'ms') : (h.detail || '离线') },
    { name: '沙箱 EXEC 策略', light: h.alive ? 'green' : 'gray', detail: h.alive ? '运行中（handlebar 驱动）' : '未确认（桥不在线）' },
  ];
  if (h.stats) {
    var tick = parseInt(h.stats.tick || '0', 10);
    var thOk = parseInt(h.stats.thread_ok || '0', 10);
    var thFail = parseInt(h.stats.thread_fail || '0', 10);
    rows.push({ name: '分笔心跳', light: tick > 0 ? 'green' : 'yellow', detail: 'tick=' + tick + '（0=休市/无分笔）' });
    rows.push({ name: '线程下单路径', light: thFail === 0 ? 'green' : 'yellow', detail: '成功 ' + thOk + ' / 失败 ' + thFail });
  }
  var html = '';
  rows.forEach(function (r) {
    html += '<div class="alert-row ' + (r.light === 'green' ? 'ok' : r.light === 'red' ? 'err' : r.light === 'yellow' ? 'warn' : 'info') + '">'
      + '<span class="dot ' + brDot(r.light) + '"></span><b>' + r.name + '</b> ' + r.detail + '</div>';
  });
  box.innerHTML = html;
}

function brRenderFiles() {
  var st = BR_ST; var box = document.getElementById('br-files'); if (!box || !st) return;
  var h = '';
  (st.files || []).forEach(function (f) {
    h += '<div class="alert-row ' + (f.light === 'green' ? 'ok' : f.light === 'red' ? 'err' : f.light === 'yellow' ? 'warn' : 'info') + '">'
      + '<span class="dot ' + brDot(f.light) + '"></span><b>' + f.name + '</b> ' + f.detail + '</div>';
  });
  box.innerHTML = h;
}
