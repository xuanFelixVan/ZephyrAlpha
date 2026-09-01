/* 功能模块：事件时间行（sq-event-row）——宏观事件真源版 v2
 * 契约：init(chart,ctx)/render(d)/destroy()；经 ZK.registerFeature 注册
 * 数据源：/api/events（CH.calendar_event：期权到期/LPR/交割日/月末等宏观日历，非个股事件）
 * v2（Owner 2026-09-01 指令）：
 *   - 值字段：pub_value/exp_value/prev_value（扩表列，未回填=NULL→前端显'未公布'）
 *   - 未来事件：K 线末日之后的无柱可锚，改经 getUpcoming() 供宿主在事件行右端渲染"未来"簇
 * 渲染宿主=klpTimelineRender（#klp-evtrow），弹窗=klpTlEvtPop/klpTlUpcomingPop
 * 演示回退：SQ_EVENTS（app1.js 4 条混合演示），断线时由宿主回退
 * 验收单：ACC-F-STOCKQ-EVENT-ROW（rev 2）
 */
(function(){
  /* event_type → 图标（与演示数据 ic 字段口径对齐） */
  var TYPE_IC = {
    lpr_announcement: '📊', futures_delivery: '📅', index_option_expiry: '📅',
    etf_option_expiry: '📅', month_end: '🏁', quarter_end: '🏁',
    half_year_end: '🏁', year_end: '🏁', hk_connect_closed: '🔒'
  };

  var mod = {
    id: 'sq-event-row',
    chart: null,
    _mkt: [],   /* 真源事件（含历史+未来） */

    init: function(chart, ctx){
      this.chart = chart;
      this.fetch();
    },

    /* 供宿主（klpTimelineRender/klpTlEvtPop）取数：真源优先，断线回退演示 */
    getEvents: function(){
      return this._mkt.length ? this._mkt : null;
    },

    /* 未来事件（date > 今天，按日期升序）：宿主在事件行右端渲染"未来"簇，点击弹清单 */
    getUpcoming: function(){
      var today = new Date().toISOString().slice(0, 10);
      return this._mkt.filter(function(e){ return e.dateISO > today; }).slice(0, 12);
    },

    isLive: function(){
      return this._mkt.length > 0;
    },

    fetch: function(){
      if(!(window.ZK && ZK.api && ZK.api.fetchEvents)) return;
      var self = this;
      ZK.api.fetchEvents().then(function(r){
        if(!(r && r.ok && r.data)) return;   /* 失败保持 null → 宿主回退演示 */
        self._mkt = r.data.map(function(e){
          return {
            dt: e.date.slice(5),          /* '2026-09-21' → '09-21'（klpFindBar 口径） */
            dateISO: e.date,
            tt: e.description,
            ic: TYPE_IC[e.type] || '📌',
            type: e.type,
            /* 扩表值字段：未回填=NULL → '未公布'（演示诚实纪律：不伪造数值） */
            pub: (e.pub_value === null || e.pub_value === undefined || e.pub_value === '') ? '未公布' : e.pub_value,
            exp: (e.exp_value === null || e.exp_value === undefined || e.exp_value === '') ? '未公布' : e.exp_value,
            prev: (e.prev_value === null || e.prev_value === undefined || e.prev_value === '') ? '未公布' : e.prev_value,
            src: 'calendar_event 真源'
          };
        });
        /* 数据更新后触发时间轴重绘（历史图标挂 K 线柱 + 未来簇挂右端） */
        if(typeof klpTimelineRender === 'function' && document.getElementById('klp-evtrow')){
          klpTimelineRender();
        }
      }).catch(function(){ /* 静默：宿主回退演示 SQ_EVENTS */ });
    },

    render: function(d){ /* 数据组件：render 由 fetch 驱动，无独立 DOM */ },

    destroy: function(){ this._mkt = []; }
  };

  ZK.registerFeature(mod);
  /* 加载链竞态兜底：宿主 sqInit 已执行则立即取数 */
  if(typeof sqCur !== 'undefined'){ mod.init(); }
})();
