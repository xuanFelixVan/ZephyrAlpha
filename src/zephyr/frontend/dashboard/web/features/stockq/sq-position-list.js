/* 功能模块：持仓列表（sq-position-list）——空壳占位版
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：QMT 持仓接口（延后开发）——当前为演示数据（SQ_HOLD 池），诚实标注
 * 四态灯：灰=未启动（QMT 通道待接入，DS-12）；接口就绪后升级为绿/黄/红实态
 * 交互：点击行切换股票（sqSel）
 * 验收单：ACC-F-STOCKQ-POSITION-LIST
 */
(function(){
  function injectStyles(){
    if(document.getElementById('sq-position-list-styles')) return;
    var st = document.createElement('style');
    st.id = 'sq-position-list-styles';
    st.textContent = '.sq-pos-status{display:flex;justify-content:flex-end;align-items:center;gap:4px;font-size:10px;padding:2px 8px;cursor:help;color:var(--faint)}'
      + '.sq-pos-status .dot{width:6px;height:6px;border-radius:50%;background:var(--faint);flex:none}';
    document.head.appendChild(st);
  }

  var mod = {
    id: 'sq-position-list',
    chart: null,

    init: function(chart, ctx){
      this.chart = chart;
      injectStyles();
    },

    _statusHtml: function(){
      return '<div class="sq-pos-status" title="数据源状态灯（DS-12）：灰=QMT 持仓接口待接入，以下为演示数据（与汇总持仓 3 账户同源）">'
        + '<span class="dot"></span>QMT 待接入·演示</div>';
    },

    _rowHtml: function(sym){
      var p = (typeof sqPoolFind === 'function') ? sqPoolFind(sym) : null;
      if(!p) return '';
      var cls = p.dir >= 0 ? 'up' : 'down';
      return '<div class="sq-si' + (sym === sqCur ? ' on' : '') + '" onclick="sqSel(\'' + sym + '\')">'
        + '<span><span class="nm">' + p.nm + '</span> <span class="cd">' + p.code + '</span></span>'
        + '<span class="rt"><span class="px ' + cls + '">' + p.px + '</span><br><span class="pc ' + cls + '">' + p.pc + '</span></span>'
        + '</div>';
    },

    render: function(d){
      /* 可见性：持仓 tab + 无搜索词（搜索态由 sq-search-box 接管） */
      var q = ((document.getElementById('sq-srch') || {}).value || '').trim();
      if(q || (typeof sqListMode === 'undefined') || sqListMode !== 'hold') return;
      var box = document.getElementById('sq-list');
      if(!box) return;
      var h = this._statusHtml();
      var holds = (typeof SQ_HOLD !== 'undefined') ? SQ_HOLD : [];
      var self = this;
      holds.forEach(function(sym){ h += self._rowHtml(sym); });
      box.innerHTML = h || (this._statusHtml() + '<div class="sq-intro">无持仓数据</div>');
    },

    destroy: function(){ /* 空壳版：无定时器/监听需清理；QMT 接入后补齐 */ }
  };

  ZK.registerFeature(mod);
  /* 加载链竞态兜底：若宿主已渲染过列表（hold tab），注册后主动接管渲染 */
  if(typeof sqCur !== 'undefined' && document.getElementById('sq-list')){
    mod.init();
    mod.render();
  }
})();
