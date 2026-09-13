/* R22 拆分版加载器：fetch 47 页面片段注入 main → 顺序加载 core/app1.js（宿主 chrome）→ 2026-09-12 拆件批 37 个页面引擎文件（保序）→ core/app2~4.js → features/backtest/bt-engine.js（回测页逻辑族，2026-09-12 自 core/ 迁入，依赖 app1 全局工具故居后）
 * 版本戳 ZK_BUILD：loader.js 经 ?v=Date.now() 破缓存加载，必为最新——页头品牌行若缺"b<版本>"即浏览器在跑旧代码（"改了看不到"类问题一键定位，2026-09-01 实证：⚑12 不显示=浏览器残留 2.5h 前旧 JS） */
window.ZK_BUILD='20260912-2';
(function(){try{var el=document.querySelector('.tb-brand small');if(el&&(' '+el.textContent+' ').indexOf('b'+window.ZK_BUILD)<0)el.textContent+=' · b'+window.ZK_BUILD;}catch(e){}})();
(function(){
  var PAGES = ["home", "overview", "warroom", "live", "sector", "sentiment", "news", "policy", "overseas", "t0", "review", "index", "position", "backtest", "experiment", "task", "fitness", "govana", "modledger", "sysstatus", "services", "pano", "projmap", "macro", "chainmap", "strategy", "factor", "stock", "screener", "calendar", "reglib", "tdm", "stockq", "cryptomarket", "cryptopos", "cryptostrat", "cryptobt", "cryptoinfo", "design", "modlib", "rating", "datasrc", "download", "bridge", "models", "aichat", "aitask"];
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
    return loadJs('core/app1.js');   /* 全局宿主 chrome（go/主题/折叠/ticker/fsArm/slimAnnot）——2026-09-12 拆件批后收敛为薄宿主 */
  }).then(function(){
    /* ── 2026-09-12 拆件批：app1.js 7116 行/441 声明 → 37 个页面引擎文件（features/<page>/）（保序挂接=原区块相对顺序；
       全局函数名零改动；顺序约束：srch-overlay 垫底依赖 IND_CAT(idx-engine)/REGLIB_D(reg-engine)；
       wr-risk-cards 启动批依赖 usyc-curve 先行。清单：docs/_working/2026-09-12-frontend-split-inventory.md ── */
    return loadJs('features/warroom/wr-scenario-matrix.js');   /* 作战室 3×3 情景矩阵+决策弹层（原 app1 L77-176） */
  }).then(function(){
    return loadJs('features/index/idx-patterns.js');   /* 指数页指标计算+形态识别纯函数库（原 L251-2267，对齐 PAT-* 注册表） */
  }).then(function(){
    return loadJs('features/index/idx-engine.js');   /* 指数详情页渲染引擎（原 L177-250+L2268-3343） */
  }).then(function(){
    return loadJs('features/factor/fc-mini-charts.js');   /* factor 页迷你走势启动批（依赖 idx-engine.drawLine/idx-patterns.genCandles） */
  }).then(function(){
    return loadJs('features/overseas/ov-mini-cards.js');   /* 外盘迷你卡（原 L3344-3380） */
  }).then(function(){
    return loadJs('features/overseas/ov-rank.js');   /* 全球市场排名榜（IIFE，依赖 drawLine/genCandles） */
  }).then(function(){
    return loadJs('features/t0/t0-intraday.js');   /* T 分析分时图+做T回验（原 L3381-3428+L5204-5220） */
  }).then(function(){
    return loadJs('features/sector/sector-contrib.js');   /* 板块贡献度（原 L3429-3451） */
  }).then(function(){
    return loadJs('features/sector/sector-arc.js');   /* 板块档案下钻（原 L4629-4656） */
  }).then(function(){
    return loadJs('features/overseas/usyc-curve.js');   /* 美债收益率曲线（wr-risk-cards 启动批前必须就绪） */
  }).then(function(){
    return loadJs('features/position/tolerance-band.js');   /* 组合容忍带（perf-analysis 启动批前就绪） */
  }).then(function(){
    return loadJs('features/warroom/wr-risk-cards.js');   /* 作战室风险卡族+启动批（renderOverseas/renderT0/renderSectorContrib/usycRender） */
  }).then(function(){
    return loadJs('features/live/ord-ticket.js');   /* 盘中下单票据+日志过滤（原 L3591-3593+L3670-3707） */
  }).then(function(){
    return loadJs('features/stock/stock-profile.js');   /* 个股档案页引擎（原 L3708-4055+F9 补强 L5221-5252） */
  }).then(function(){
    return loadJs('features/screener/scr-engine.js');   /* 条件选股引擎（原 L4056-4356） */
  }).then(function(){
    return loadJs('features/calendar/cal-engine.js');   /* 事件日历引擎（原 L4357-4471） */
  }).then(function(){
    return loadJs('features/review/rev-engine.js');   /* 盘后复盘引擎（原 L4472-4563） */
  }).then(function(){
    return loadJs('features/news/ann-panel.js');   /* 公司公告面板（原 L4564-4599） */
  }).then(function(){
    return loadJs('features/policy/pol-panel.js');   /* 政策资金面板（原 L4600-4628） */
  }).then(function(){
    return loadJs('features/live/live-equity.js');   /* 盘中实时权益分时（原 L4690-4722） */
  }).then(function(){
    return loadJs('features/task/task-progress.js');   /* 任务进度下钻（原 L4723-4768） */
  }).then(function(){
    return loadJs('features/position/pos-attribution.js');   /* 盈亏归因+experiment 阶段门控（原 L4881-4908） */
  }).then(function(){
    return loadJs('features/position/acct-multi.js');   /* 多账号持仓视图（原 L4909-5044） */
  }).then(function(){
    return loadJs('features/position/perf-analysis.js');   /* 收益分析区+init 批调用（原 L5045-5147） */
  }).then(function(){
    return loadJs('features/sentiment/sent-margin.js');   /* 市场情绪·两融（原 L5148-5203） */
  }).then(function(){
    return loadJs('features/reglib/reg-engine.js');   /* 注册表库引擎（原 L5253-5514；srch-overlay 前必须就绪） */
  }).then(function(){
    return loadJs('features/pano/pano-engine.js');   /* 架构全景页引擎（原 L5515-5598） */
  }).then(function(){
    return loadJs('features/modledger/mod-engine.js');   /* 模块总账引擎（原 L5599-5733） */
  }).then(function(){
    return loadJs('features/backtest/btr-links.js');   /* 回测+策略链接 fwInit（原 L5734-5764） */
  }).then(function(){
    return loadJs('features/stockq/sq-host-engine.js');   /* 个股行情二级页宿主引擎（sq-* 组件宿主/回退层，原 L5866-6197） */
  }).then(function(){
    return loadJs('features/stockq/klp-mark-layer.js');   /* 主图标注层（原 L6198-6357） */
  }).then(function(){
    return loadJs('features/stockq/klp-timeline.js');   /* K 线时间轴（原 L6358-6452） */
  }).then(function(){
    return loadJs('features/stockq/klp-period-picker.js');   /* 周期选择弹层（原 L6453-6510） */
  }).then(function(){
    return loadJs('features/stockq/klp-indicator-dialog.js');   /* 指标设置弹窗（原 L6511-6798） */
  }).then(function(){
    return loadJs('features/cryptomarket/cm-engine.js');   /* 币圈组引擎（原 L6799-6946） */
  }).then(function(){
    return loadJs('features/design/ds-spec-chart.js');   /* DS-5 K 线规范图（原 L6947-7061） */
  }).then(function(){
    return loadJs('features/search/srch-overlay.js');   /* 全局搜索（垫底：依赖 IND_CAT/REGLIB_D；含 srchLate() 尾调用迁入） */
  }).then(function(){
    return loadJs('core/event_bus.js');   /* 薄事件总线+功能模块注册表（模块契约基建，四件套之三） */
  }).then(function(){
    return loadJs('services/api.js');   /* 数据服务层·HTTP 通道（dashboard-api:8890，失败回退演示） */
  }).then(function(){
    return loadJs('core/pool.js');   /* 作战池共享真源（ZK.Pool，localStorage zk-warroom-pool；chainmap/筛选器写、作战室读） */
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
    return loadJs('features/stockq/sq-order-book.js');   /* 五档挂单功能模块·文件桥真源（模块契约，验收单 ACC-F-STOCKQ-ORDER-BOOK） */
  })
  .then(function(){
    return loadJs('features/stockq/sq-event-row.js');   /* 事件时间行功能模块·calendar_event 真源（模块契约，验收单 ACC-F-STOCKQ-EVENT-ROW） */
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
    return loadJs('features/position/pos-signal-board.js');   /* 量化信号看板·持仓页真源（QMT持仓×market_signal_history双管道，验收单 ACC-F-POS-SIGNAL-BOARD） */
  }).then(function(){
    return loadJs('features/stockq/sq-quant-analysis.js');   /* 量化分析·右栏双源信号真源（验收单 ACC-F-STOCKQ-QUANT-ANALYSIS） */
  }).then(function(){
    return loadJs('features/warroom/wr-signal-strip.js');   /* 量化信号总览·warroom 聚合真源（验收单 ACC-F-WR-SIGNAL-STRIP） */
  }).then(function(){
    return loadJs('features/warroom/wr-pool.js');   /* 作战池面板·跨页共享选中真源 ZK.Pool（验收单 ACC-F-WR-POOL） */
  }).then(function(){
    return loadJs('core/app2.js');
  }).then(function(){
    return loadJs('core/app3.js');
  }).then(function(){
    return loadJs('core/app4.js');
  }).then(function(){
    return loadJs('features/backtest/bt-engine.js');   /* 回测页逻辑族（2026-09-12 拆件批自 core/ 迁入 features/backtest/，依赖 app1 全局工具故居后） */
  }).then(function(){
    return loadJs('features/backtest/bt-battle-stage.js');   /* 策略所处环节（作战地图阶段树真源 /api/battle-map-flow，Owner 2026-09-04 一期） */
  }).then(function(){
    return loadJs('features/services/sv-page.js');   /* 服务总闸页（启动编排：17 启动项四态灯+分级开关，真源 /api/services-status；2026-09-12 迁入 features/） */
  }).then(function(){
    return loadJs('features/datasrc/ds-page.js');   /* 数据源监管页（源清单健康探针真源+alerter 告警流水，真源 /api/sources-status；2026-09-12 迁入 features/） */
  }).then(function(){
    return loadJs('features/download/dl-page.js');   /* 数据下载监管页（表级下载实况 146 表新鲜度四态灯，真源 /api/download-status；2026-09-12 迁入 features/） */
  }).then(function(){
    return loadJs('features/bridge/br-page.js');   /* 交易通道监控页（HTTP 桥全环节健康+速度 vs miniqmt 对比，真源 /api/bridge-status；2026-09-12 迁入 features/） */
  }).then(function(){
    return loadJs('features/home/hm-engine.js');   /* 首页三件套（结论墙/布局引擎/AI 对话框；2026-09-12 迁入 features/）——最后加载，依赖全部页面片段已在 DOM */
  }).then(function(){
    return loadJs('vendor/three/three.min.js');   /* three.js r147 UMD（chainmap 3D 星云渲染引擎，B2；UMD 全局 THREE，dockview vendor 先例） */
  }).then(function(){
    return loadJs('features/chainmap/chainmap-galaxy.js');   /* 产业星系图（L1 族聚合 3D 星云，/api/chainmap-galaxy；B2 起渲染=vendor/three r147，依赖前一行先行加载） */
  }).then(function(){
    return loadJs('features/chainmap/chainmap-nav.js');   /* 产业导航树（族→链两级） */
  }).then(function(){
    return loadJs('features/chainmap/chainmap-search.js');   /* 产业全局搜索（链/环节/代码/公司名落位） */
  }).then(function(){
    return loadJs('features/chainmap/chainmap-cluster.js');   /* 产业链层（L2 上中下游列式+环节公司面板） */
  }).then(function(){
    return loadJs('features/chainmap/chainmap-company-card.js');   /* 公司详情卡（/api/chainmap-company，二期 Commit A） */
  }).then(function(){
    return loadJs('features/tdm.js');   /* 交易决策全景（横向树实时映射 /api/tdm，Owner 2026-09-07 裁定） */
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
