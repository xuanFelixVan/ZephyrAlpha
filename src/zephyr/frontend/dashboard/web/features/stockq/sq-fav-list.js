/* 功能模块：自选列表（sq-fav-list）
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：localStorage（zk-sq-fav 清单）+ /api/quote 批量报价（kline_daily 最新日线）
 * 轮询：30s 刷新报价（仅自选 tab 且无搜索词时）；失败回退演示池价格并标"断线·演示"
 * 四态灯：绿=真源（报价新鲜） / 黄=延迟（>5 日） / 红=断线（回退演示） / 灰=未启动（DS-12）
 * 交互：点击行切换股票（sqSel）、✕移出自选（sqFavRm）
 * 验收单：ACC-F-STOCKQ-FAV-LIST
 */
(function(){
  var POLL_MS = 30000;
  var STALE_DAYS = 5;

  function injectStyles(){
    if(document.getElementById('sq-fav-list-styles')) return;
    var st = document.createElement('style');
    st.id = 'sq-fav-list-styles';
    st.textContent = '.sq-list-status{display:flex;justify-content:flex-end;align-items:center;gap:4px;font-size:10px;padding:2px 8px;cursor:help}'
      + '.sq-list-status .dot{width:6px;height:6px;border-radius:50%;flex:none}'
      + '.sq-list-status.dm-真源{color:#25A750}'
      + '.sq-list-status.dm-真源 .dot{background:#25A750}'
      + '.sq-list-status.dm-延迟{color:#F0B90B}'
      + '.sq-list-status.dm-延迟 .dot{background:#F0B90B}'
      + '.sq-list-status.dm-断线{color:#CA3F64}'
      + '.sq-list-status.dm-断线 .dot{background:#CA3F64}'
      + '.sq-list-status.dm-未启动{color:var(--faint)}'
      + '.sq-list-status.dm-未启动 .dot{background:var(--faint)}';
    document.head.appendChild(st);
  }

  var STATUS_TITLE = '数据源状态灯（DS-12）：绿=真源（kline_daily 批量报价） / 黄=数据延迟（>5 日） / 红=断线（回退演示价格） / 灰=服务未启动';

  function modeLabel(mode){
    return mode==='真源'?'真源':mode==='延迟'?'延迟':mode==='断线'?'断线·演示':'未启动';
  }

  function fresh(iso){
    if(!iso) return false;
    var t = new Date(iso + 'T00:00:00');
    return (Date.now() - t.getTime()) < STALE_DAYS * 86400000;
  }

  var mod = {
    id: 'sq-fav-list',
    chart: null,
    _timer: null,
    _mode: '未启动',
    _quotes: {},   /* symbol → {name, price, pct_change_str, direction} */

    init: function(chart, ctx){
      this.chart = chart;
      injectStyles();
      this._startPoll();
    },

    /* 轮询幂等：sqInit 每次 go('stockq') 都会调 init，先清旧定时器 */
    _startPoll: function(){
      var self = this;
      clearInterval(this._timer);
      this._timer = setInterval(function(){ self._poll(); }, POLL_MS);
    },

    /* 可见性判定：自选 tab + 无搜索词 + 容器在 DOM（搜索态由 sq-search-box 接管） */
    _visible: function(){
      var q = ((document.getElementById('sq-srch') || {}).value || '').trim();
      return !!document.getElementById('sq-list')
        && (typeof sqListMode !== 'undefined') && sqListMode === 'fav'
        && !q;
    },

    _poll: function(){
      if(this._visible()) this._fetch();
    },

    _statusHtml: function(mode){
      return '<div class="sq-list-status dm-' + mode + '" title="' + STATUS_TITLE + '">'
        + '<span class="dot"></span>' + modeLabel(mode) + '</div>';
    },

    _rowHtml: function(sym){
      var p = (typeof sqPoolFind === 'function') ? sqPoolFind(sym) : null;
      var q = this._quotes[sym];
      var nm = (q && q.name) ? q.name : (p ? p.nm : sym);
      var code = p ? p.code : sym;
      var px = q ? Number(q.price).toFixed(2) : (p ? p.px : '--');
      var pc = q ? q.pct_change_str : (p ? p.pc : '--');
      var up = q ? (q.direction === 'up') : (p ? p.dir >= 0 : true);
      var cls = up ? 'up' : 'down';
      return '<div class="sq-si' + (sym === sqCur ? ' on' : '') + '" onclick="sqSel(\'' + sym + '\')">'
        + '<span><span class="nm">' + nm + '</span> <span class="cd">' + code + '</span></span>'
        + '<span class="rt"><span class="px ' + cls + '">' + px + '</span><br><span class="pc ' + cls + '">' + pc + '</span></span>'
        + '<span class="fav" onclick="event.stopPropagation();sqFavRm(\'' + sym + '\')" title="移出自选">✕</span></div>';
    },

    render: function(d){
      if(!this._visible()) return;
      var box = document.getElementById('sq-list');
      if(!box) return;
      var syms = (typeof sqFav !== 'undefined') ? sqFav : [];
      var h = this._statusHtml(this._mode);
      var self = this;
      syms.forEach(function(sym){ h += self._rowHtml(sym); });
      box.innerHTML = h || (this._statusHtml(this._mode) + '<div class="sq-intro">清单为空，搜索名称/代码加入自选</div>');
      this._fetch();
    },

    _fetch: function(){
      var syms = (typeof sqFav !== 'undefined') ? sqFav : [];
      if(!syms.length || !(window.ZK && ZK.api && ZK.api.fetchQuote)) return;
      var self = this;
      ZK.api.fetchQuote(syms).then(function(r){
        if(r && r.ok && r.data){
          var stale = false;
          self._quotes = {};
          r.data.forEach(function(q){
            self._quotes[q.symbol] = q;
            if(!fresh(q.trade_date)) stale = true;
          });
          self._mode = stale ? '延迟' : '真源';
        } else {
          self._mode = '断线';   /* ok:false（CH 异常等）→ 断线，保留演示价 */
        }
        if(self._visible()) self.render();
      }).catch(function(){
        self._mode = '断线';
        if(self._visible()) self.render();
      });
    },

    destroy: function(){
      clearInterval(this._timer);
      this._quotes = {};
    }
  };

  ZK.registerFeature(mod);
  /* 加载链竞态兜底：若宿主已渲染过列表（fav tab + 无搜索词），注册后主动接管渲染 */
  if(typeof sqCur !== 'undefined' && document.getElementById('sq-list')){
    mod.init();
    mod.render();
  }
})();
