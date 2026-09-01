/* 数据服务层·HTTP 通道（services/api.js——TRAE-086 目录归属：services/<域>.js 按域分文件，本文件=通道基建）
 * 职责：前端↔后端唯一接触点；所有取数经此；失败必 reject（调用方负责回退演示数据并标"演示"——演示诚实纪律）
 * 对端：src/zephyr/frontend/dashboard/api_server.py（只读 FastAPI，127.0.0.1:8890）
 */
window.ZK = window.ZK || {};
ZK.api = (function(){
  var BASE = 'http://127.0.0.1:8890';
  function fetchJson(path, timeoutMs, opts){
    /* opts（可选）: {method:'POST', headers:{...}, body:'...'}——GET 缺省；POST 超时放宽由调用方传 timeoutMs */
    timeoutMs = timeoutMs || (opts && opts.method === 'POST' ? 15000 : 5000);
    return new Promise(function(res, rej){
      var ctrl = new AbortController();
      var t = setTimeout(function(){ ctrl.abort(); }, timeoutMs);
      var init = {signal: ctrl.signal};
      if(opts && opts.method){ init.method = opts.method; init.headers = opts.headers; init.body = opts.body; }
      fetch(BASE + path, init).then(function(r){
        clearTimeout(t);
        if(!r.ok) throw new Error('http '+r.status);
        return r.json();
      }).then(res, function(e){ clearTimeout(t); rej(e); });
    });
  }
  /* 页面中文周期 → API 周期（未支持的周期=reject，调用方回退演示） */
  var KLP_PERIOD_API = {'1分':'1m','5分':'5m','15分':'15m','30分':'30m','60分':'60m','日':'1d','周':'1w','月':'1M'};
  return {
    fetchJson: fetchJson,   /* 通用通道（GET/POST opts）——组件临时接口（如 /api/strategies）用 */
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
    },
    fetchPosition: function(){   /* QMT 文件桥真实持仓（sq-position-list） */
      return fetchJson('/api/position');
    },
    fetchOrderbook: function(symbol){   /* QMT 文件桥五档盘口（sq-order-book） */
      return fetchJson('/api/orderbook?symbol='+encodeURIComponent(symbol));
    },
    fetchEvents: function(){   /* 宏观事件日历（sq-event-row） */
      return fetchJson('/api/events');
    },
    fetchBacktestList: function(){   /* 回测产物列表（backtest 页真源；34+ 产物逐个读 JSON，冷盘 5s 不够） */
      return fetchJson('/api/backtest-list', 15000);
    },
    fetchBacktestDetail: function(runId){   /* 回测产物详情（绩效三图/明细） */
      return fetchJson('/api/backtest-detail?run_id='+encodeURIComponent(runId), 10000);
    },
    postBacktestRun: function(body){   /* 页面发起回测（POST，BTRUN 引擎后台执行） */
      return fetchJson('/api/backtest-run', 15000, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    },
    fetchBacktestRunStatus: function(taskId){   /* 轮询回测任务状态 */
      return fetchJson('/api/backtest-run?task_id='+encodeURIComponent(taskId));
    },
    fetchSignals: function(symbols){   /* 个股最新信号（pos-signal-board：factor_synth+strategy_weight 双源） */
      return fetchJson('/api/signals?symbols='+encodeURIComponent(symbols.join(',')), 8000);
    },
    fetchSignalsOverview: function(){   /* 信号总览聚合（warroom） */
      return fetchJson('/api/signals-overview');
    }
  };
})();
