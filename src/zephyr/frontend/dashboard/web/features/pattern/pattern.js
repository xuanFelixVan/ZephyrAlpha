/* ── 图形库页（消费班 W-C4）· 数据源 /api/pattern-winrate /api/pattern-events /api/pattern-evidence ──
 * 房规对齐：factory/tdm 同款——API_BASE 绝对 8890（app:// 相对 fetch 必断）；仅 p-pattern
 * 可见才轮询；取数失败回退灰字不落缓存（演示诚实纪律）；弱证据 n<30 灰标（信号侧
 * 真实低胜率自动降权不亮绿灯，展示侧如实呈现不粉饰）。
 * 依赖：services/api.js（ZK.api.fetchJson）先于 loader 引擎链加载。
 */
(function(){
  'use strict';

  function esc(s){
    return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }

  function heatColor(rate){
    if(rate == null) return '#8a94a6';
    if(rate >= 0.60) return '#4caf7d';
    if(rate >= 0.45) return '#c9a227';
    return '#d46a6a';
  }

  function pct(rate){
    return rate == null ? '—' : (rate * 100).toFixed(1) + '%';
  }

  function visible(){
    var el = document.getElementById('p-pattern');
    return !!(el && el.classList.contains('active'));
  }

  /* ── 胜率切片 ───────────────────────────────────────────────────────── */

  function patternLoadWinrate(){
    var body = document.getElementById('pat-wr-body');
    var meta = document.getElementById('pat-wr-meta');
    if(!body) return;
    var dir = (document.getElementById('pat-wr-dir')||{}).value || '';
    var win = (document.getElementById('pat-wr-win')||{}).value || '10';
    var regime = (document.getElementById('pat-wr-regime')||{}).value || '';
    var q = 'fwd_window=' + encodeURIComponent(win) + '&min_n=0&limit=500';
    if(dir) q += '&direction=' + encodeURIComponent(dir);
    if(regime) q += '&regime_tag=' + encodeURIComponent(regime);
    ZK.api.fetchPatternWinrate({ direction: dir, fwdWindow: win, regimeTag: regime, minN: 0, limit: 500 }).then(function(r){
      if(!r || !r.ok){ meta.textContent = '取数失败'; return; }
      var rows = (r.data || []).filter(function(d){ return !d.low_sample && d.pattern_id !== '__baseline__'; });
      var weak = (r.data || []).length - rows.length;
      meta.textContent = '在册 ' + (r.count || 0) + ' 切片 · 展示 ' + rows.length + '（弱证据 ' + weak + ' 隐藏）';
      if(!rows.length){ body.innerHTML = '<tr><td colspan="7" style="padding:8px;color:#8a94a6">该切片无 ≥30 样本的形态</td></tr>'; return; }
      body.innerHTML = rows.map(function(d){
        var badge = '';
        if(d.cert_state === 'certified' || d.cert_state === 'resurrected') badge = '<span style="background:#0e2612;border:1px solid #2e7d32;border-radius:4px;padding:0 6px;color:#7dc48f;font-size:11px">' + (d.cert_state === 'resurrected' ? '复活' : '认证') + '</span>';
        else if(d.cert_state === 'probation') badge = '<span style="background:#2a1c0e;border:1px solid #8a4a12;border-radius:4px;padding:0 6px;color:#d9a441;font-size:11px">观察</span>';
        else if(d.cert_state === 'retired') badge = '<span style="background:#141a24;border:1px solid #33405c;border-radius:4px;padding:0 6px;color:#6b7890;font-size:11px">退役</span>';
        else if(d.cert_state === 'frozen') badge = '<span style="background:#1c1010;border:1px solid #5a2e2e;border-radius:4px;padding:0 6px;color:#a06a6a;font-size:11px">冻结</span>';
        else if(d.cert_state === 'failed') badge = '<span style="background:#1c1010;border:1px solid #5a2e2e;border-radius:4px;padding:0 6px;color:#a06a6a;font-size:11px">未过</span>';
        else badge = '<span style="color:#5a6478">—</span>';
        var weakBadge = d.low_sample ? '<span style="color:#8a94a6">弱样本</span>' : '';
        var shr = d.shrunk_rate == null ? '—' : (d.shrunk_rate * 100).toFixed(1) + '%';
        var shrColor = d.shrunk_rate == null ? '#8a94a6' : heatColor(d.shrunk_rate);
        return '<tr style="border-top:1px solid #1c2333">'
          + '<td style="padding:4px 8px">' + esc(d.pattern_id) + '</td>'
          + '<td style="padding:4px 8px">' + esc(d.direction) + '</td>'
          + '<td style="padding:4px 8px;color:' + heatColor(d.hit_rate) + ';font-weight:600">' + pct(d.hit_rate)
          + ' <span style="color:#8a94a6;font-weight:400">/ ' + (d.n_events == null ? '—' : d.n_events) + '</span></td>'
          + '<td style="padding:4px 8px;color:' + shrColor + '">' + shr + '</td>'
          + '<td style="padding:4px 8px">' + (d.n_events == null ? '—' : d.n_events) + '</td>'
          + '<td style="padding:4px 8px">' + esc(d.regime_tag || '全') + '</td>'
          + '<td style="padding:4px 8px">' + esc(d.fwd_window) + 'd</td>'
          + '<td style="padding:4px 8px">' + badge + weakBadge + '</td>'
          + '</tr>';
      }).join('');
    }).catch(function(){
      meta.textContent = '取数失败';
      body.innerHTML = '<tr><td colspan="7" style="padding:8px;color:#8a94a6">后端不可达（8890）——本页无演示数据，如实留空</td></tr>';
    });
  }

  /* ── 逐标的形态事件 ─────────────────────────────────────────────────── */

  function patternQueryEvents(){
    var body = document.getElementById('pat-ev-body');
    var meta = document.getElementById('pat-ev-meta');
    var input = document.getElementById('pat-ev-symbol');
    var days = (document.getElementById('pat-ev-days')||{}).value || '30';
    if(!body || !input) return;
    var sym = (input.value || '').trim();
    if(!sym){ body.innerHTML = '<tr><td colspan="7" style="padding:8px;color:#8a94a6">请输入代码</td></tr>'; return; }
    body.innerHTML = '<tr><td colspan="7" style="padding:8px;color:#8a94a6">查询中…</td></tr>';
    ZK.api.fetchPatternEvents(sym, { daysBack: days, limit: 200, timeout: 20000 }).then(function(r){
      if(!r || !r.ok){ meta.textContent = r && r.error ? ('失败：' + r.error) : '取数失败'; return; }
      meta.textContent = '命中 ' + (r.count || 0) + ' 条';
      if(!r.data || !r.data.length){ body.innerHTML = '<tr><td colspan="7" style="padding:8px;color:#8a94a6">窗口内无形态事件</td></tr>'; return; }
      body.innerHTML = r.data.map(function(d){
        var color = d.direction === '向上' ? '#4caf7d' : (d.direction === '向下' ? '#d46a6a' : '#c9a227');
        return '<tr style="border-top:1px solid #1c2333">'
          + '<td style="padding:4px 8px">' + esc((d.confirmed_at || '').replace('T', ' ').slice(0, 19)) + '</td>'
          + '<td style="padding:4px 8px">' + esc(d.name || d.pattern_id) + '</td>'
          + '<td style="padding:4px 8px;color:' + color + ';font-weight:600">' + esc(d.direction) + '</td>'
          + '<td style="padding:4px 8px">' + (d.confidence == null ? '—' : (d.confidence * 100).toFixed(0) + '%') + '</td>'
          + '<td style="padding:4px 8px">' + esc(d.timeframe) + '</td>'
          + '<td style="padding:4px 8px">' + esc(d.anchor_trade_date || '—') + '</td>'
          + '<td style="padding:4px 8px">' + esc(d.regime_tag || '—') + '</td>'
          + '</tr>';
      }).join('');
    }).catch(function(){
      meta.textContent = '取数失败';
      body.innerHTML = '<tr><td colspan="7" style="padding:8px;color:#8a94a6">后端不可达（8890）——如实留空</td></tr>';
    });
  }

  /* ── 机生证据 ───────────────────────────────────────────────────────── */

  function patternLoadEvidence(){
    var body = document.getElementById('pat-evd-body');
    var meta = document.getElementById('pat-evd-meta');
    if(!body) return;
    ZK.api.fetchPatternEvidence().then(function(r){
      if(!r || !r.ok){ meta.textContent = '取数失败'; return; }
      meta.textContent = '在册机生证据 ' + (r.evidence_total || 0) + ' 条';
      body.innerHTML = (r.data || []).map(function(d){
        return '<div style="border-left:2px solid #1e5a8f;padding:2px 0 2px 8px">'
          + '<b style="color:#7db4e8">' + esc(d.pattern_id) + '</b> '
          + '<span style="color:#8a94a6">' + esc(d.name_zh || '') + '</span> '
          + '<span style="background:#0e2612;border:1px solid #2e7d32;border-radius:4px;padding:0 6px;color:#7dc48f;font-size:11px">' + esc(d.status || '') + '</span>'
          + '<div style="color:#a8b2c4;margin-top:2px">' + esc(d.evidence) + '</div>'
          + '</div>';
      }).join('') || '<span class="dim">暂无机生证据</span>';
    }).catch(function(){
      meta.textContent = '取数失败';
      body.innerHTML = '<span class="dim">后端不可达（8890）——如实留空</span>';
    });
  }

  /* ── 启动 + 30s 轮询（仅本页可见才取数，factory 同款） ───────────────── */

  function patternTick(){
    if(!visible()) return;
    patternLoadWinrate();
    patternLoadEvidence();
    var body = document.getElementById('pat-ev-body');
    if(body && !body.querySelector('td')) patternQueryEvents();
  }

  patternTick();
  setInterval(patternTick, 30000);

  window.patternLoadWinrate = patternLoadWinrate;
  window.patternQueryEvents = patternQueryEvents;
  window.patternLoadEvidence = patternLoadEvidence;
})();
