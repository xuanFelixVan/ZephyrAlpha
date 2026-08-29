/* R22 拆分版加载器：fetch 41 页面片段注入 main → 顺序加载 core/app1~4.js → backtest.js（保持原单文件执行时序；backtest.js 依赖 app1 全局工具故最后） */
(function(){
  var PAGES = ["overview", "warroom", "live", "sector", "sentiment", "news", "policy", "overseas", "t0", "review", "index", "position", "backtest", "experiment", "task", "fitness", "govana", "modledger", "sysstatus", "pano", "macro", "chainmap", "strategy", "factor", "stock", "screener", "calendar", "reglib", "datainfo", "stockq", "cryptomarket", "cryptopos", "cryptostrat", "cryptobt", "cryptoinfo", "design", "rating", "datasrc", "models", "aichat", "aitask"];
  var main = document.getElementById('main-root');
  function loadJs(src){
    return new Promise(function(res, rej){
      var s = document.createElement('script');
      s.src = src; s.onload = res; s.onerror = function(){ rej(new Error('load fail: '+src)); };
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
    return loadJs('core/app1.js');
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
  }).catch(function(e){
    main.innerHTML = '<div style="padding:40px;color:#CA3F64">页面片段加载失败：'+e.message+'（需通过 http 服务访问，file:// 不支持 fetch）</div>';
    console.error(e);
  });
})();
