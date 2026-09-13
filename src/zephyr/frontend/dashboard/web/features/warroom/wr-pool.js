/* ── 作战池面板（warroom 页 W 区）· 真源 ZK.Pool（localStorage 'zk-warroom-pool'）──
 * Owner 2026-09-14"全部开工"解除 HOLD 后建成：跨页共享选中（产业链受益清单/筛选器/后续入口），
 * 条目=代码+名称+来源徽章+入池时间，支持单删/清空；空态诚实提示（零演示数据）。
 * 变更经 ZK.bus 'wr:pool' 联动重渲。验收单：ACC-F-WR-POOL */
(function () {
  'use strict';
  function el() { return document.getElementById('wr-pool'); }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function srcCls(source) {
    if (source.indexOf('产业链') >= 0) return 'b-buy';
    if (source.indexOf('筛选') >= 0) return 'b-na';
    return 'b-warn';
  }
  function fmtTs(ts) {
    try {
      var d = new Date(ts);
      return (d.getMonth() + 1) + '-' + d.getDate() + ' ' + ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2);
    } catch (e) { return ''; }
  }
  function render() {
    var host = el();
    if (!host) return;
    var list = (window.ZK && ZK.Pool) ? ZK.Pool.list() : [];
    if (!list.length) {
      host.innerHTML = '<div class="dim" style="padding:8px 0">作战池空——在产业链受益清单或筛选器点「入作战池/作战池→」即入池（本机 localStorage 真源，不上云）</div>';
      return;
    }
    var h = '<table><tr><th>代码</th><th>名称</th><th>来源</th><th>入池</th><th>操作</th></tr>';
    list.forEach(function (x) {
      h += '<tr><td><b>' + esc(x.code) + '</b></td><td>' + esc(x.name || '—') + '</td>' +
        '<td><span class="badge ' + srcCls(x.source || '') + '">' + esc(x.source || '手动') + '</span></td>' +
        '<td class="dim">' + fmtTs(x.ts) + '</td>' +
        '<td><span class="btn" data-del="' + esc(x.code) + '" style="padding:1px 8px;font-size:11px;cursor:pointer">移出</span></td></tr>';
    });
    h += '</table><div style="margin-top:6px"><span class="btn" data-clear="1" style="padding:2px 10px;font-size:11px;cursor:pointer">清空作战池（' + list.length + '/' + ZK.Pool.cap + '）</span> <span class="dim" style="font-size:11px">点击代码列可在筛选器/个股页检索（跳转按既有页内机制）</span></div>';
    host.innerHTML = h;
    Array.prototype.forEach.call(host.querySelectorAll('[data-del]'), function (b) {
      b.addEventListener('click', function () { ZK.Pool.remove(b.getAttribute('data-del')); render(); });
    });
    var clr = host.querySelector('[data-clear]');
    if (clr) clr.addEventListener('click', function () { ZK.Pool.clear(); render(); });
  }
  function boot() {
    render();
    if (window.ZK && ZK.bus) ZK.bus.on('wr:pool', render);
  }
  if (document.getElementById('p-warroom')) boot();
  else {
    var t = setInterval(function () {
      if (document.getElementById('p-warroom')) { clearInterval(t); boot(); }
    }, 1000);
  }
  window.wrPoolRender = render;   /* 页面激活重渲入口（切页返回时间戳新鲜） */
})();
