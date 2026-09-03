/* ── 服务总闸页（Owner 2026-09-02 裁定：启动编排统一上桌面——总电箱）──
 * 真源=GET /api/services-status（services_registry.SERVICE_CATALOG 16 启动项，psutil+心跳+端口探测）
 * 控制=POST /api/services-control（分级闸门：free 直执行 / confirm 二次确认 / guard·external·self 只读）
 * 总闸=拉起型（一键拉起标准套装，幂等跳过已运行的），不设一键全停 */
var SVC_ST = null;          /* 最近一次 /api/services-status 快照 */
var SVC_TIMER = null;

function svcDot(l) { return { green: 'g', yellow: 'y', red: 'r', gray: 'w' }[l] || 'w'; }
function svcDotTxt(l) { return { green: '正常', yellow: '延迟', red: '断线', gray: '未启动' }[l] || l; }

function svcLoad() {
  if (!ZK.api) return;
  ZK.api.fetchServicesStatus().then(function (st) {
    if (!st || !st.ok) throw new Error(st && st.error || 'bad payload');
    SVC_ST = st;
    svcRenderMaster();
    svcRenderGroups();
  }).catch(function (e) {
    /* 失败必显示（Owner 2026-09-02 实证：静默 catch=空白页，"什么都没有"无法自查）——保留上帧列表但总闸区标红提示 */
    var m = document.getElementById('svc-master');
    if (m && (!SVC_ST || !m.innerHTML)) {
      m.innerHTML = '<div class="card" style="border-left:3px solid var(--up)"><b style="color:var(--up)">⚠ API 拉取失败（' + (e && e.message || e)
        + '）</b><div class="dim" style="font-size:11px;margin-top:4px">面板 API（127.0.0.1:8890）未运行或请求超时——先确认 api_server 存活，10 秒后自动重试</div></div>';
    }
  });
}
function svcBoot() {
  svcLoad();
  if (!SVC_TIMER) SVC_TIMER = setInterval(svcLoad, 10000);   /* 10s 轮询——心跳 15s 一跳，10s 采样不失真 */
}
svcBoot();

/* ── 总闸区：系统大灯+四态计数+整机水位三杆+一键拉起+操作日志尾 ── */
function svcRenderMaster() {
  var m = document.getElementById('svc-master'); if (!m || !SVC_ST) return;
  var st = SVC_ST;
  var overallTxt = { green: '系统正常', yellow: '有服务延迟', red: '有服务断线' }[st.overall] || st.overall;
  var h = '<div class="card" style="margin-bottom:14px">'
    + '<div style="display:flex;gap:20px;align-items:center;flex-wrap:wrap">'
    + '<div><span class="dot ' + svcDot(st.overall) + '" style="width:14px;height:14px"></span>'
    + '<b style="font-size:20px;vertical-align:2px">' + overallTxt + '</b></div>'
    + '<span style="font-size:12px"><span class="dot g"></span>运行 <b>' + st.counts.green + '</b></span>'
    + '<span style="font-size:12px"><span class="dot y"></span>延迟 <b>' + st.counts.yellow + '</b></span>'
    + '<span style="font-size:12px"><span class="dot r"></span>断线 <b>' + st.counts.red + '</b></span>'
    + '<span style="font-size:12px"><span class="dot w"></span>未启动 <b>' + st.counts.gray + '</b></span>'
    + '<span class="btn primary" style="margin-left:auto" onclick="svcBootAll()">⚡ 一键拉起标准套装</span>'
    + '<span class="btn" style="color:var(--up)" onclick="svcShutdownAll()">⏻ 一键全部关闭</span>'
    + '</div>';
  if (st.host && st.host.mem_total_gb) {
    h += '<div style="display:flex;gap:18px;flex-wrap:wrap;margin-top:10px;font-size:11px;color:var(--dim)">'
      + svcWater('本机 CPU', st.host.cpu, '%')
      + svcWater('本机内存', st.host.mem, '%', st.host.mem_used_gb + ' / ' + st.host.mem_total_gb + ' GB');
    (st.host.disks || []).forEach(function (d) {
      h += svcWater(d.label, d.pct, '%', '余 ' + d.free_gb + ' GB');
    });
    if (st.host.gpu) {   /* GPU 杆（RTX 3090 实测可用；无卡/无驱动自动隐藏） */
      var g = st.host.gpu;
      h += svcWater('GPU × ' + g.gpus, g.util, '%', '显存 ' + g.mem_used_gb + ' / ' + g.mem_total_gb + ' GB');
    }
    h += '</div>';
  }
  var log = st.control_log || [];
  if (log.length) {
    h += '<div style="margin-top:10px;border-top:1px solid var(--hair);padding-top:8px;font-size:11px;color:var(--dim)">最近操作：'
      + log.slice().reverse().map(function (x) {
        return '<span style="margin-right:14px;display:inline-block">' + x.ts.slice(5, 16)
          + ' <b style="color:var(--text)">' + x.name + '</b> ' + (x.action === 'start' ? '启动' : '停止')
          + (x.ok ? ' ✓' : ' <span style="color:var(--up)">✗ ' + (x.msg || '').slice(0, 30) + '</span>') + '</span>';
      }).join('') + '</div>';
  }
  m.innerHTML = h + '</div>';
}
function svcWater(label, pct, unit, sub) {
  var warn = pct >= 90 ? ' style="color:var(--up)"' : (pct >= 75 ? ' style="color:var(--yellow)"' : '');
  return '<div style="min-width:180px;flex:1"><div style="display:flex;justify-content:space-between">'
    + '<span>' + label + (sub ? ' <span style="font-size:10px">(' + sub + ')</span>' : '') + '</span><b' + warn + '>' + pct + unit + '</b></div>'
    + '<div class="bar" style="margin-top:3px"><i style="width:' + Math.min(100, pct) + '%"></i></div></div>';
}

/* ── 分组列表：每行=四态灯+名称大白话+级别徽标+CPU/内存+detail+开关 ── */
function svcRenderGroups() {
  var box = document.getElementById('svc-groups'); if (!box || !SVC_ST) return;
  var st = SVC_ST;
  var order = ['services', 'data', 'trading', 'infra', 'guard'];
  var h = '';
  order.forEach(function (g) {
    var meta = (st.groups && st.groups[g]) || { title: g, sub: '' };
    var items = st.services.filter(function (s) { return s.group === g; });
    if (!items.length) return;
    var ctlable = items.filter(function (s) { return s.tier === 'free' || s.tier === 'confirm'; });
    h += '<div class="sec-title">' + meta.title + ' <span class="dim">' + meta.sub + '</span>'
      + (ctlable.length ? '<span class="btn" style="float:right;font-size:11px;padding:2px 10px" onclick="svcGroupStart(\'' + g + '\')">全部启动</span>' : '')
      + '</div>'
      + '<div class="card" style="margin-bottom:14px;padding:0"><table style="margin:0">'
      + '<tr><th style="width:34px"></th><th style="width:150px">服务</th><th>功能（大白话）</th><th style="width:130px">资源</th><th style="width:150px">状态</th><th style="width:110px">操作</th></tr>';
    items.forEach(function (s) {
      var locked = (s.tier === 'guard' || s.tier === 'external' || s.tier === 'self');
      var res = (s.mem != null)
        ? 'CPU <b>' + (s.cpu != null ? s.cpu : 0) + '%</b> · 内存 <b>' + s.mem + '</b> MB'
        : '<span class="dim">—</span>';
      var off = s.light === 'gray';
      var btn = locked
        ? '<span class="dim" title="' + s.tier_label + '">🔒 只读</span>'
        : (off
          ? '<span class="btn" style="font-size:11px;padding:2px 10px" onclick="svcCtl(\'' + s.id + '\',\'start\')">▶ 启动</span>'
          : '<span class="btn" style="font-size:11px;padding:2px 10px" onclick="svcCtl(\'' + s.id + '\',\'stop\')">■ 停止</span>');
      h += '<tr>'
        + '<td><span class="dot ' + svcDot(s.light) + '" title="' + svcDotTxt(s.light) + '"></span></td>'
        + '<td><b>' + s.name + '</b><br><span class="badge ' + (s.tier === 'guard' ? 'b-warn' : s.tier === 'confirm' ? 'b-na' : s.tier === 'free' ? 'b-pass' : 'b-na') + '" style="font-size:9px">' + s.tier_label + '</span></td>'
        + '<td style="font-size:11px;color:var(--dim)">' + s.desc + '</td>'
        + '<td style="font-size:11px">' + res + '</td>'
        + '<td style="font-size:11px">' + svcDotTxt(s.light) + ' · <span class="dim">' + (s.detail || '') + '</span>';
      if (s.ch_space) {   /* CH 库内余量可视化：杆画已用率（100-余%），余量数字醒目——Owner 口径"库里剩多少要一眼看到" */
        var used = Math.round(100 - s.ch_space.free_gb / s.ch_space.total_gb * 100);
        h += '<div style="display:flex;align-items:center;gap:8px;margin-top:4px">'
          + '<div class="bar" style="flex:1"><i style="width:' + used + '%"></i></div>'
          + '<b style="color:' + (s.ch_space.free_gb < 100 ? 'var(--up)' : 'var(--text)') + '">余 ' + s.ch_space.free_gb + ' GB</b></div>';
      }
      h += '</td>'
        + '<td>' + btn + '</td>'
        + '</tr>';
    });
    h += '</table></div>';
  });
  box.innerHTML = h;
}

/* ── 控制：confirm 级走二次确认；guard/external 后端闸门拒绝（前端按钮已置灰兜底）── */
function svcCtl(id, action, _unused) {
  ZK.api.postServicesControl(id, action).then(function (r) {
    if (r && r.ok) { svcLoad(); return; }
    if (r && r.need_confirm) {
      if (window.confirm(r.error)) {
        ZK.api.postServicesControl(id, action, true).then(function (r2) {
          if (!r2 || !r2.ok) alert('操作失败：' + (r2 && r2.error || '?'));
          svcLoad();
        }).catch(function (e) { alert('请求失败：' + e); });
      }
      return;
    }
    alert('操作被拒：' + (r && r.error || '?'));
  }).catch(function (e) { alert('请求失败：' + e); });
}

/* ── 一键全部关闭：停掉所有「有开关」的运行中服务（free+confirm；guard/external/self 天生无开关不受影响）──
 * 与一键拉起对称（Owner 2026-09-02 裁定补上）；强确认列出全部将关服务+代价警示。api_server（self）不在关闭范围。 */
function svcShutdownAll() {
  if (!SVC_ST) return;
  var targets = SVC_ST.services.filter(function (s) {
    return (s.tier === 'free' || s.tier === 'confirm') && s.light !== 'gray' && s.id !== 'api_server';
  });
  if (!targets.length) { alert('有开关的服务全部已停止，无需关闭'); return; }
  var names = targets.map(function (s) { return s.name; }).join('、');
  var inDay = targets.some(function (s) { return s.id === 'tick_sub' || s.id === 'scheduler'; });
  var msg = '关闭以下服务（守护域/外部程序不受影响）：\n' + names
    + (inDay ? '\n\n⚠ 盘中执行会漏行情数据、断模拟盘口粮！' : '');
  if (!window.confirm(msg)) return;
  var chain = Promise.resolve();
  targets.forEach(function (s) {
    chain = chain.then(function () {
      return ZK.api.postServicesControl(s.id, 'stop', true).catch(function () { });
    });
  });
  chain.then(function () { setTimeout(svcLoad, 1500); });
}

/* ── 一键拉起标准套装：灰灯的可控项批量拉起（幂等，活着的跳过）；confirm 级合并一次确认 ── */
function svcBootAll() {
  if (!SVC_ST) return;
  var targets = SVC_ST.services.filter(function (s) {
    return (s.tier === 'free' || s.tier === 'confirm') && s.light === 'gray' && s.id !== 'proto8010';
  });
  if (!targets.length) { alert('标准套装全部在运行，无需拉起'); return; }
  var names = targets.map(function (s) { return s.name; }).join('、');
  if (!window.confirm('拉起以下未启动服务（幂等，已运行的跳过）：\n' + names)) return;
  var chain = Promise.resolve();
  targets.forEach(function (s) {
    chain = chain.then(function () {
      return ZK.api.postServicesControl(s.id, 'start', true).catch(function () { });
    });
  });
  chain.then(function () { setTimeout(svcLoad, 1500); });
}
