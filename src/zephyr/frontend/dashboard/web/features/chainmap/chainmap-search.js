/* ── 产业地图全局搜索（链/环节/公司代码/公司名）· 真源 /api/chainmap-search ──
 * 结果点击→定位跳转：链/环节/公司落到 L2 链层并高亮（cm:goto-chain 带 focus_node）。
 * 已知边界（如实提示）：公司名映射来自 ig_company_edge 名称列，覆盖不全。验收单：ACC-F-CHAINMAP-SEARCH */
(function () {
  'use strict';
  var S = { timer: null, lastQ: '', dd: null };

  function inputEl() { return document.querySelector('#cm-search-slot .cm-si'); }

  function closeDD() {
    if (S.dd && S.dd.parentNode) S.dd.parentNode.removeChild(S.dd);
    S.dd = null;
  }

  function goCluster(payload) {
    closeDD();
    var inp = inputEl();
    if (inp) inp.blur();
    ZK.bus.emit('cm:view', { view: 'cluster' });
    ZK.bus.emit('cm:goto-chain', payload);
  }

  function renderDD(d) {
    closeDD();
    var slot = document.getElementById('cm-search-slot');
    if (!slot) return;
    var dd = document.createElement('div');
    dd.className = 'cm-sd';
    var n = d.chains.length + d.nodes.length + d.symbols.length;
    if (!n) {
      dd.innerHTML = '<div class="cm-se">无匹配结果（链/环节/代码/公司名）</div>';
    } else {
      if (d.chains.length) {
        dd.insertAdjacentHTML('beforeend', '<div class="cm-sg">产业链</div>');
        d.chains.forEach(function (c) {
          var r = document.createElement('div');
          r.className = 'cm-sr';
          r.innerHTML = '<span class="a" title="' + c.name + '">' + c.name + '</span><span class="b">' + c.cluster + '</span>';
          r.addEventListener('mousedown', function (e) {
            e.preventDefault();
            goCluster({ chain_id: c.chain_id, cluster: c.cluster, chain_name: c.name });
          });
          dd.appendChild(r);
        });
      }
      if (d.nodes.length) {
        dd.insertAdjacentHTML('beforeend', '<div class="cm-sg">环节</div>');
        d.nodes.forEach(function (nd) {
          var r = document.createElement('div');
          r.className = 'cm-sr';
          r.innerHTML = '<span class="a" title="' + nd.chain_name + '">' + nd.name + '</span><span class="b">' + nd.chain_name + '</span>';
          r.addEventListener('mousedown', function (e) {
            e.preventDefault();
            goCluster({ chain_id: nd.chain_id, cluster: nd.cluster, chain_name: nd.chain_name, focus_node: nd.node_id });
          });
          dd.appendChild(r);
        });
      }
      if (d.symbols.length) {
        dd.insertAdjacentHTML('beforeend', '<div class="cm-sg">公司（名称映射覆盖不全）</div>');
        d.symbols.forEach(function (s) {
          var r = document.createElement('div');
          r.className = 'cm-sr';
          r.innerHTML = '<span class="a" title="' + s.chain_name + '">' + (s.name || s.symbol) +
            ' <span style="color:#525d70;font-size:10px">' + s.symbol + '</span></span><span class="b">' + s.node_name + '</span>';
          r.addEventListener('mousedown', function (e) {
            e.preventDefault();
            goCluster({ chain_id: s.chain_id, cluster: s.cluster, chain_name: s.chain_name, focus_node: s.node_id, focus_symbol: s.symbol });
          });
          dd.appendChild(r);
        });
      }
    }
    slot.appendChild(dd);
    S.dd = dd;
  }

  function search(q) {
    if (!q) { closeDD(); return; }
    ZK.api.fetchChainmapSearch(q)
      .then(function (d) {
        if (S.lastQ !== q) return;   /* 竞态：只认最新关键词 */
        if (!d.ok) { closeDD(); return; }
        renderDD(d);
      }).catch(function () { /* 断线静默：输入框不打断用户 */ });
  }

  function bind() {
    var slot = document.getElementById('cm-search-slot');
    if (!slot || slot.dataset.bound) return;
    slot.dataset.bound = '1';
    var inp = document.createElement('input');
    inp.className = 'cm-si';
    inp.placeholder = '搜链 / 环节 / 代码 / 公司…';
    slot.appendChild(inp);
    inp.addEventListener('input', function () {
      var q = inp.value.trim();
      S.lastQ = q;
      if (S.timer) clearTimeout(S.timer);
      if (!q) { closeDD(); return; }
      S.timer = setTimeout(function () { search(q); }, 250);
    });
    inp.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { closeDD(); inp.blur(); }
      if (e.key === 'Enter') {
        var first = S.dd && S.dd.querySelector('.cm-sr');
        if (first) first.dispatchEvent(new Event('mousedown'));
      }
    });
    inp.addEventListener('blur', function () { setTimeout(closeDD, 180); });
  }

  ZK.registerFeature({
    id: 'chainmap-search',
    init: function () { bind(); },
    render: function () { /* 无常驻渲染体 */ },
    destroy: function () { closeDD(); }
  });

  if (document.getElementById('p-chainmap')) bind();
})();
