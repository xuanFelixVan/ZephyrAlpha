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
    fetchBattleMapFlow: function(){   /* 作战地图阶段树（策略所处环节模块真源，BattleMapReader 后端缓存 10min） */
      return fetchJson('/api/battle-map-flow', 15000);
    },
    fetchFrameworkPlans: function(){   /* 整装方案清单（二期组合回测：防御/均衡/激进，config/framework_plans.yaml 真源，fail-closed） */
      return fetchJson('/api/framework-plans', 15000);
    },
    postFrameworkBacktestRun: function(body){   /* 发起整装回测（POST，后台串行线程池，与 backtest-run 同模式） */
      return fetchJson('/api/framework-backtest-run', 15000, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    },
    fetchFrameworkBacktestRunStatus: function(taskId){   /* 轮询整装回测状态 */
      return fetchJson('/api/framework-backtest-run?task_id='+encodeURIComponent(taskId));
    },
    fetchBacktestDetail: function(runId){   /* 回测产物详情（绩效三图/明细）；20s：tick 产物 127 万点冷盘读取 10s 必超时→误标「断线」（2026-09-03 实证） */
      return fetchJson('/api/backtest-detail?run_id='+encodeURIComponent(runId), 20000);
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
    },
    fetchServicesStatus: function(){   /* 服务总闸状态（34 启动项四态灯+CPU/内存+心跳；后端冷扫描实测 3-8s，15s 兜底） */
      return fetchJson('/api/services-status', 15000);
    },
    postServicesControl: function(id, action, confirm){   /* 服务启停（分级闸门在服务端，confirm=二次确认） */
      return fetchJson('/api/services-control', 10000, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id:id, action:action, confirm:!!confirm})});
    },
    fetchSourcesStatus: function(){   /* 数据源监管真源（健康探针日志解析+alerter 告警流水） */
      return fetchJson('/api/sources-status', 8000);
    },
    fetchDownloadStatus: function(){   /* 数据下载监管真源（146 表最新分区/行数/新鲜度） */
      return fetchJson('/api/download-status', 10000);
    },
    fetchDataAsset: function(kick){   /* 库内资产总览真源（宽度/深度/完整度/缺口/存储层·内存缓存秒回，kick=1 后台重审） */
      return fetchJson('/api/data-asset' + (kick ? '?refresh=1' : ''), 8000);
    },
    fetchBridgeStatus: function(){   /* 交易通道监控真源（HTTP 桥探活+桥文件族活性+miniqmt 存活）。
                                      * ⚠ miniqmt 信号 2026-09-18 退役（券商清退，93 备忘 §2.1）：
                                      * 响应内 mini_alive 仅在退役日前是"存活"信号，退役日后消费方
                                      * （bridge.js）应展示"已退役"占位而非"已停"（防误读为故障）；
                                      * 判定依据 retire_date 字段（后端真源），前端本地比较日期即可。 */
      return fetchJson('/api/bridge-status', 10000);
    },
    fetchChainmapGalaxy: function(market){   /* 产业地图 L1 星系（chainmap-galaxy/nav 真源；ig_* 聚类首算 3-6s，20s 兜底）；market=all/cn/global（项4，缺省 all 基线档） */
      var q = (market && market !== 'all') ? '?market=' + encodeURIComponent(market) : '';
      return fetchJson('/api/chainmap-galaxy' + q, 20000);
    },
    fetchChainmapCluster: function(cid, market){   /* 产业地图 L2 链层（chainmap-cluster 真源）；cid 是 per-market 聚类空间，须与取簇时 market 同档 */
      var q = (market && market !== 'all') ? '&market=' + encodeURIComponent(market) : '';
      return fetchJson('/api/chainmap-cluster?cid='+encodeURIComponent(cid) + q, 20000);
    },
    fetchChainmapNode: function(nodeId){   /* 环节公司面板（chainmap-cluster 右侧抽屉） */
      return fetchJson('/api/chainmap-node?node_id='+encodeURIComponent(nodeId), 15000);
    },
    fetchChainmapSearch: function(q){   /* 产业地图搜索（chainmap-search：链/环节/代码/公司名） */
      return fetchJson('/api/chainmap-search?q='+encodeURIComponent(q), 15000);
    },
    fetchChainmapCompany: function(symbol){   /* 公司详情卡（chainmap-company-card 真源：落位+关系+行情/估算市值） */
      return fetchJson('/api/chainmap-company?symbol='+encodeURIComponent(symbol), 15000);
    },
    fetchChainmapCatalyst: function(cid, market){   /* 产业链催化剂·簇视角（F-CHAINMAP-CATALYST：环节催化角标映射；零命中=空映射不造数据） */
      var q = (market && market !== 'all') ? '&market=' + encodeURIComponent(market) : '';
      return fetchJson('/api/chainmap-catalyst?cid='+encodeURIComponent(cid) + q, 15000);
    },
    fetchChainmapCatalystNode: function(nodeId){   /* 产业链催化剂·环节视角（受益清单：命中事件方向语义+落位个股） */
      return fetchJson('/api/chainmap-catalyst?node_id='+encodeURIComponent(nodeId), 15000);
    },
    /* ── SWR 缓存（stale-while-revalidate，2026-09-03 Owner「刷新立即出画面」诉求）──
     * 刷新后先渲染 localStorage 里上次响应（毫秒级，数据自带时间戳可见新鲜度），后台拉新到达后覆盖。
     * 演示诚实纪律：缓存态渲染时由调用方标注"上次更新 HH:MM"，新数据到达后消失。 */
    swrLoad: function(key, renderFn){
      try{
        var c = JSON.parse(localStorage.getItem(key) || 'null');
        if(c && c.data) renderFn(c.data, new Date(c.ts));
      }catch(e){}
    },
    swrSave: function(key, data){
      try{ localStorage.setItem(key, JSON.stringify({ ts: Date.now(), data: data })); }catch(e){}
    },
    /* 通用 SWR（stale-while-revalidate）：先渲染缓存（isCache=true 供调用方标注）→ 后台拉新落缓存并覆盖。
     * 各数据页统一接法：ZK.api.swr('key', fetcher, renderFn)；fetcher 失败/空数据不落缓存。 */
    swr: function(key, fetcher, renderFn){
      try{
        var c = JSON.parse(localStorage.getItem(key) || 'null');
        if(c && c.data != null) renderFn(c.data, new Date(c.ts), true);
      }catch(e){}
      return Promise.resolve().then(fetcher).then(function(d){
        if(d != null){
          try{ localStorage.setItem(key, JSON.stringify({ ts: Date.now(), data: d })); }catch(e){}
          renderFn(d, new Date(), false);
        }
        return d;
      });
    }
  };
})();
