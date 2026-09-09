/* ── 产业地图左侧导航树（族→链两级）· 真源 /api/chainmap-galaxy（与 galaxy 同源，后端 TTL 缓存自取）──
 * 点族=进 L2 链层；点链=进 L2 并聚焦该链；⌂ 返回全景。与 galaxy/search/cluster 只经 ZK.bus 通信。
 * 演示诚实纪律：断线空态+15s 重试，零演示数据。验收单：ACC-F-CHAINMAP-NAV */
(function () {
  'use strict';
  var N = { data: null, busy: false, loaded: false, timer: null, bootTimer: null, activeChain: null };

  function hostEl() { return document.getElementById('cm-nav'); }

  function render() {
    var d = N.data;
    var host = hostEl();
    if (!d || !host) return;
    host.innerHTML = '';
    var root = document.createElement('button');
    root.className = 'cm-nav-root';
    root.textContent = '⌂ 全景星系';
    root.addEventListener('click', function () { ZK.bus.emit('cm:view', { view: 'galaxy' }); });
    host.appendChild(root);
    var frag = document.createDocumentFragment();
    d.clusters.forEach(function (c) {
      var wrap = document.createElement('div');
      wrap.className = 'cm-cl';
      wrap.dataset.cid = c.id;
      var h = document.createElement('div');
      h.className = 'cm-cl-h';
      h.innerHTML = '<span class="tri">▶</span><span class="nm" title="' + c.name + '">' + c.name + '</span>' +
        '<span class="ct">' + c.n_chains + '链·' + c.n_companies + '公司</span>';
      h.addEventListener('click', function () {
        var open = wrap.classList.toggle('open');
        if (open) {   /* 点族头=展开并同时进入 L2（Owner 语义：点族进链层） */
          ZK.bus.emit('cm:view', { view: 'cluster' });
          ZK.bus.emit('cm:open-cluster', { cid: c.id, name: c.name });
        }
      });
      var chs = document.createElement('div');
      chs.className = 'cm-chs';
      d.chains.filter(function (x) { return x.cluster === c.id; })
        .sort(function (a, b) { return b.n_companies - a.n_companies; })
        .forEach(function (ch) {
          var row = document.createElement('div');
          row.className = 'cm-ch';
          row.dataset.chain = ch.chain_id;
          row.innerHTML = '<span class="nm" title="' + ch.name + '">' + ch.name + '</span>' +
            '<span class="ct">' + ch.n_companies + '</span>';
          row.addEventListener('click', function () {
            ZK.bus.emit('cm:view', { view: 'cluster' });
            ZK.bus.emit('cm:goto-chain', { chain_id: ch.chain_id, cluster: c.id, chain_name: ch.name });
          });
          chs.appendChild(row);
        });
      wrap.appendChild(h); wrap.appendChild(chs);
      frag.appendChild(wrap);
    });
    host.appendChild(frag);
    markActive();
  }

  function markActive() {
    var host = hostEl();
    if (!host) return;
    Array.prototype.forEach.call(host.querySelectorAll('.cm-ch'), function (el) {
      el.classList.toggle('act', el.dataset.chain === N.activeChain);
    });
  }

  ZK.bus.on('cm:chain-active', function (d) {
    N.activeChain = d && d.chain_id || null;
    markActive();
  });

  function fail(msg) {
    var host = hostEl();
    if (host) host.innerHTML = '<div class="cm-nav-tip cm-bad">导航断线（' + msg + '）——15s 后重试</div>';
    if (!N.timer) N.timer = setInterval(function () {
      if (N.loaded) { clearInterval(N.timer); N.timer = null; return; }
      var el = document.getElementById('p-chainmap');
      if (!el || el.offsetParent === null) return;
      load();
    }, 15000);
  }

  function load() {
    if (N.busy) return;
    N.busy = true;
    ZK.api.fetchChainmapGalaxy().then(function (d) {
      N.busy = false;
      if (!d.ok) { fail(d.error || '后端返回失败'); return; }
      N.loaded = true;
      N.data = d;
      render();
    }).catch(function (e) { N.busy = false; fail(e && e.message || 'fetch 失败'); });
  }

  ZK.registerFeature({
    id: 'chainmap-nav',
    init: function () {
      /* registerFeature 无统一 init 调度（ZK 契约：各模块自引导）——保留入口兼容手动调用 */
      bootNav();
    },
    render: function () { render(); },
    destroy: function () { if (N.timer) clearInterval(N.timer); if (N.bootTimer) { clearInterval(N.bootTimer); N.bootTimer = null; } }
  });

  /* 自引导（与 chainmap-galaxy.boot 同构）：loader 顺序预载时本页未必 active——offsetParent 判定
   * 在懒加载时代成立，预载模式下永不成立（存量缺陷 2026-09-10 实证：nav 永停"加载中"），改轮询等 visible */
  function bootNav() {
    if (N.bootTimer) return;
    if (visibleNow()) { load(); return; }
    N.bootTimer = setInterval(function () {
      if (N.loaded || visibleNow()) { clearInterval(N.bootTimer); N.bootTimer = null; if (!N.loaded) load(); }
    }, 1200);
  }

  function visibleNow() {
    var el = document.getElementById('p-chainmap');
    return !!(el && el.offsetParent !== null);
  }

  bootNav();
})();
