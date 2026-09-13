/* ── 作战池（warroom pool）共享真源：localStorage 'zk-warroom-pool' ──
 * 单写者纪律：所有读写经 ZK.Pool（消费方=作战室 wr-pool 面板/产业链受益清单/筛选器 scrPool）；
 * 变更后 ZK.bus 广播 'wr:pool'（跨页联动）。localStorage 数据源先例=sq-fav-list。
 * 上限 50 条 FIFO；条目={code,name,source,ts}。Owner 2026-09-14"全部开工"解除 HOLD。 */
(function () {
  'use strict';
  var KEY = 'zk-warroom-pool', CAP = 50;
  function load() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY) || '[]');
      return Array.isArray(v) ? v : [];
    } catch (e) { return []; }
  }
  function save(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list.slice(0, CAP))); } catch (e) { /* 配额满则本会话内存态 */ }
    if (window.ZK && ZK.bus) ZK.bus.emit('wr:pool', { count: list.length });
  }
  window.ZK = window.ZK || {};
  ZK.Pool = {
    list: load,
    cap: CAP,
    has: function (code) { return load().some(function (x) { return x.code === code; }); },
    add: function (code, name, source) {
      if (!code) return false;
      var list = load();
      if (list.some(function (x) { return x.code === code; })) return false;
      list.unshift({ code: code, name: name || '', source: source || '', ts: Date.now() });
      save(list);
      return true;
    },
    remove: function (code) { save(load().filter(function (x) { return x.code !== code; })); },
    clear: function () { save([]); }
  };
})();
