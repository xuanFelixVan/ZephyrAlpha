/* 数据服务层·HTTP 通道（services/api.js——TRAE-086 目录归属：services/<域>.js 按域分文件，本文件=通道基建）
 * 职责：前端↔后端唯一接触点；所有取数经此；失败必 reject（调用方负责回退演示数据并标"演示"——演示诚实纪律）
 * 对端：src/zephyr/frontend/dashboard/api_server.py（只读 FastAPI，127.0.0.1:8890）
 */
window.ZK = window.ZK || {};
ZK.api = (function(){
  var BASE = 'http://127.0.0.1:8890';
  function fetchJson(path, timeoutMs){
    timeoutMs = timeoutMs || 5000;
    return new Promise(function(res, rej){
      var ctrl = new AbortController();
      var t = setTimeout(function(){ ctrl.abort(); }, timeoutMs);
      fetch(BASE + path, {signal: ctrl.signal}).then(function(r){
        clearTimeout(t);
        if(!r.ok) throw new Error('http '+r.status);
        return r.json();
      }).then(res, function(e){ clearTimeout(t); rej(e); });
    });
  }
  /* 页面中文周期 → API 周期（未支持的周期=reject，调用方回退演示） */
  var KLP_PERIOD_API = {'1分':'1m','5分':'5m','15分':'15m','30分':'30m','60分':'60m','日':'1d','周':'1w','月':'1M'};
  return {
    fetchKline: function(symbol, tf){
      var p = KLP_PERIOD_API[tf];
      if(!p) return Promise.reject(new Error('period unsupported: '+tf));
      return fetchJson('/api/kline?symbol='+encodeURIComponent(symbol)+'&period='+p+'&limit=300');
    },
    fetchStockHeader: function(symbol){
      return fetchJson('/api/stock-header?symbol='+encodeURIComponent(symbol));
    },
    fetchStockSearch: function(q){
      return fetchJson('/api/stock-search?q='+encodeURIComponent(q));
    },
    fetchQuote: function(symbols){   /* 批量最新报价（sq-fav-list）：symbols=字符串数组 */
      return fetchJson('/api/quote?symbols='+encodeURIComponent(symbols.join(',')));
    }
  };
})();
