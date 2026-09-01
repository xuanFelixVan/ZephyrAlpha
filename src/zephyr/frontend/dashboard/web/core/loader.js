/* R22 拆分版加载器：fetch 41 页面片段注入 main → 顺序加载 core/app1~4.js → backtest.js（保持原单文件执行时序；backtest.js 依赖 app1 全局工具故最后） */
(function(){
  var PAGES = ["home", "overview", "warroom", "live", "sector", "sentiment", "news", "policy", "overseas", "t0", "review", "index", "position", "backtest", "experiment", "task", "fitness", "govana", "modledger", "sysstatus", "pano", "projmap", "macro", "chainmap", "strategy", "factor", "stock", "screener", "calendar", "reglib", "datainfo", "stockq", "cryptomarket", "cryptopos", "cryptostrat", "cryptobt", "cryptoinfo", "design", "modlib", "rating", "datasrc", "models", "aichat", "aitask"];
  var main = document.getElementById('main-root');
  function loadJs(src){
    return new Promise(function(res, rej){
      var s = document.createElement('script');
      s.src = src+(src.indexOf('?')<0?'?':'&')+'v='+Date.now();   /* 迭代期破缓存（Owner 实测"改了看不到"事故根治，同 pages no-cache） */
      s.onload = res; s.onerror = function(){ rej(new Error('load fail: '+src)); };
      document.body.appendChild(s);
    });
  }
  Promise.all(PAGES.map(function(id){
    return fetch('pages/'+id+'.html', {cache:'no-cache'}).then(function(r){   /* 迭代期防浏览器缓存旧片段（Owner 实测"改了看不到"事故根治） */
      if(!r.ok) throw new Error('page '+id+' http '+r.status);
      return r.text();
    });
  })).then(function(frags){
    main.innerHTML = frags.join('\n');
  }).then(function(){
    return loadJs('klinecharts.min.js');   /* KLineChart v10 — 个股行情页 K 线引擎（替代自研 canvas） */
  }).then(function(){
    return loadJs('core/app1.js');
  }).then(function(){
    return loadJs('core/event_bus.js');   /* 薄事件总线+功能模块注册表（模块契约基建，四件套之三） */
  }).then(function(){
    return loadJs('services/api.js');   /* 数据服务层·HTTP 通道（dashboard-api:8890，失败回退演示） */
  }).then(function(){
    return loadJs('features/cost-line.js');   /* 成本线功能模块（模块契约 pilot，验收单 ACC-F-STOCKQ-COSTLINE） */
  }).then(function(){
    return loadJs('features/stockq/sq-stock-header.js');   /* 股票标题功能模块（模块契约，验收单 ACC-F-STOCKQ-STOCK-HEADER） */
  }).then(function(){
    return loadJs('features/stockq/sq-search-box.js');   /* 股票搜索框功能模块（模块契约，验收单 ACC-F-STOCKQ-SEARCH-BOX） */
  })
  .then(function(){
    return loadJs('features/stockq/sq-key-data.js');   /* 关键数据表功能模块（模块契约，验收单 ACC-F-STOCKQ-KEY-DATA） */
  })
  .then(function(){
    return loadJs('features/stockq/sq-sector-tags.js');   /* 行业标签功能模块（模块契约，验收单 ACC-F-STOCKQ-SECTOR-TAGS） */
  })
  .then(function(){
    return loadJs('features/stockq/sq-fav-list.js');   /* 自选列表功能模块（模块契约，验收单 ACC-F-STOCKQ-FAV-LIST） */
  })
  .then(function(){
    return loadJs('features/stockq/sq-position-list.js');   /* 持仓列表功能模块·QMT 文件桥真源（模块契约，验收单 ACC-F-STOCKQ-POSITION-LIST） */
  }).then(function(){
    return loadJs('core/app2.js');
  }).then(function(){
    return loadJs('core/app3.js');
  }).then(function(){
    return loadJs('core/app4.js');
  }).then(function(){
    return loadJs('core/backtest.js');
  }).then(function(){
    return loadJs('core/home.js');   /* 首页三件套（结论墙/布局引擎/AI 对话框）——最后加载，依赖全部页面片段已在 DOM */
  }).then(function(){
    return loadJs('vendor/dockview/dockview.min.js');   /* Dockview 库先行（dockpilot 依赖） */
  }).then(function(){
    return loadJs('core/dockpilot.js');   /* 停靠布局引擎（Owner 四裁：全景总览首站推广，依赖全部页面片段已在 DOM） */
  }).then(function(){
    /* hash 路由（Owner 2026-08-30：#stockq 等深链直达）——必须在全部片段+app1.js 加载后执行，确保 go() 可用且页面在 DOM */
    var h=location.hash.replace('#','');
    if(h&&document.getElementById('p-'+h)&&typeof go==='function'){ go(h); }
  }).catch(function(e){
    main.innerHTML = '<div style="padding:40px;color:#CA3F64">页面片段加载失败：'+e.message+'（需通过 http 服务访问，file:// 不支持 fetch）</div>';
    console.error(e);
  });
})();
