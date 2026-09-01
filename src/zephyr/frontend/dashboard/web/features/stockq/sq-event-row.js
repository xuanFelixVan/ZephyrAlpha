/* 功能模块：事件时间行（sq-event-row）——宏观事件真源版
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：/api/events（CH.calendar_event：期权到期/LPR/交割日/月末等宏观日历，非个股事件）
 * 边界（诚实口径）：个股财报/解禁暂无真源（待接入）；本组件只供数据+图标映射，
 *   渲染宿主=klpTimelineRender（时间轴组件，#klp-evtrow），弹窗=klpTlEvtPop
 * 演示回退：SQ_EVENTS（app1.js 4 条混合演示），断线时由宿主回退
 * 验收单：ACC-F-STOCKQ-EVENT-ROW
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
    _mkt: [],   /* 真源事件（SQ_EVENTS 兼容格式：dt='MM-DD'/tt/ic/type） */

    init: function(chart, ctx){
      this.chart = chart;
      this.fetch();
    },

    /* 供宿主（klpTimelineRender/klpTlEvtPop）取数：真源优先，断线回退演示 */
    getEvents: function(){
      return this._mkt.length ? this._mkt : null;
    },

    /* 标题栏 ⓘ 状态提示：真源/演示（由 getEvents 推断） */
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
            tt: e.description,
            ic: TYPE_IC[e.type] || '📌',
            type: e.type,
            pub: '—', exp: '—', prev: '—',
            src: 'calendar_event 真源'
          };
        });
        /* 数据更新后触发时间轴重绘（事件图标挂 K 线柱上） */
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
