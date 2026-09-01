/* 功能模块：持仓列表（sq-position-list）——QMT 文件桥真源版（v2）
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：/api/position（E:\qmt_bridge\Stock\PositionStatics.csv + Account.csv，QMT 自动导出 GBK）
 * 背景：miniQMT 通道 2026-09-18 券商关停，实盘数据一律走文件桥（Owner 2026-09-01 裁定）
 * 四态灯：绿=真源（导出文件 1h 内） / 黄=延迟（>1h，显示截至时间） / 红=断线（回退演示 SQ_HOLD） / 灰=未启动（DS-12）
 * 轮询：30s 刷新（仅持仓 tab 且无搜索词时）
 * 交互：点击行切换股票（sqSel，非池内股票先入池带真名）
 * 验收单：ACC-F-STOCKQ-POSITION-LIST（rev 2）
 */
(function(){
  var POLL_MS = 30000;
  var FRESH_SEC = 3600;   /* <1h=真源（QMT 终端 10s 自动导出；超时=终端未开/非交易时段→延迟 */

  function injectStyles(){
    if(document.getElementById('sq-position-list-styles')) return;
    var st = document.createElement('style');
    st.id = 'sq-position-list-styles';
    st.textContent = '.sq-pos-status{display:flex;justify-content:space-between;align-items:center;gap:6px;font-size:10px;padding:2px 8px;cursor:help}'
      + '.sq-pos-status .st{display:flex;align-items:center;gap:4px}'
      + '.sq-pos-status .dot{width:6px;height:6px;border-radius:50%;flex:none}'
      + '.sq-pos-status.dm-真源{color:#25A750}'
      + '.sq-pos-status.dm-真源 .dot{background:#25A750}'
      + '.sq-pos-status.dm-延迟{color:#F0B90B}'
      + '.sq-pos-status.dm-延迟 .dot{background:#F0B90B}'
      + '.sq-pos-status.dm-断线{color:#CA3F64}'
      + '.sq-pos-status.dm-断线 .dot{background:#CA3F64}'
      + '.sq-pos-status.dm-未启动{color:var(--faint)}'
      + '.sq-pos-status.dm-未启动 .dot{background:var(--faint)}'
      + '.sq-pos-status .acct{color:var(--faint);font-variant-numeric:tabular-nums}'
      + '.sq-pos-row .qty{font-size:10px;color:var(--faint);font-variant-numeric:tabular-nums}';
    document.head.appendChild(st);
  }

  var STATUS_TITLE = '数据源状态灯（DS-12）：绿=真源（QMT 文件桥导出 1h 内） / 黄=延迟（终端未开/非交易时段，显示截至时间） / 红=断线（回退演示数据） / 灰=服务未启动。真源 E:\\qmt_bridge\\Stock（miniQMT 2026-09-18 关停后唯一实盘通道）';

  function modeLabel(mode, mtime){
    if(mode==='真源') return '真源';
    if(mode==='延迟') return '延迟·截至 ' + (mtime ? mtime.slice(5,10) : '--');
    if(mode==='断线') return '断线·演示';
    return '未启动';
  }

  function fmtWan(v){
    if(!v) return '--';
    if(Math.abs(v) >= 1e8) return (v/1e8).toFixed(2)+' 亿';
    if(Math.abs(v) >= 1e4) return (v/1e4).toFixed(2)+' 万';
    return v.toFixed(0);
  }

  var mod = {
    id: 'sq-position-list',
    chart: null,
    _timer: null,
    _mode: '未启动',
    _mtime: null,
    _account: null,

    init: function(chart, ctx){
      this.chart = chart;
      injectStyles();
      var self = this;
      clearInterval(this._timer);   /* 幂等：sqInit 每次 go('stockq') 都调 init */
      this._timer = setInterval(function(){ self._poll(); }, POLL_MS);
    },

    _visible: function(){
      var q = ((document.getElementById('sq-srch') || {}).value || '').trim();
      return !!document.getElementById('sq-list')
        && (typeof sqListMode !== 'undefined') && sqListMode === 'hold'
        && !q;
    },

    _poll: function(){
      if(this._visible()) this._fetch();
    },

    _statusHtml: function(){
      var acct = this._account;
      var acctHtml = acct ? '<span class="acct" title="账户摘要（文件桥 Account.csv）">总资产 ' + fmtWan(acct.total) + ' · 可用 ' + fmtWan(acct.available) + '</span>' : '';
      return '<div class="sq-pos-status dm-' + this._mode + '" title="' + STATUS_TITLE + '">'
        + '<span class="st"><span class="dot"></span>' + modeLabel(this._mode, this._mtime) + '</span>'
        + acctHtml + '</div>';
    },

    /* 真源行：名称+代码 / 现价·盈亏% */
    _rowReal: function(p){
      var up = p.pnl >= 0;
      var cls = up ? 'up' : 'down';
      var px = p.price > 0 ? p.price.toFixed(2) : '--';
      var pc = p.pnl_pct || '--';
      return '<div class="sq-si sq-pos-row' + (p.symbol === sqCur ? ' on' : '') + '" onclick="sqSelFromPos(\'' + p.symbol + '\',\'' + p.name + '\',\'' + p.code + '\')" title="数量 ' + p.qty + '（可用 ' + p.available + '）· 成本 ' + (p.cost_price > 0 ? p.cost_price.toFixed(3) : '--') + ' · 市值 ' + fmtWan(p.market_value) + '">'
        + '<span><span class="nm">' + p.name + '</span> <span class="cd">' + p.code + '</span><br><span class="qty">' + p.qty + ' 股</span></span>'
        + '<span class="rt"><span class="px ' + cls + '">' + px + '</span><br><span class="pc ' + cls + '">' + pc + '</span></span>'
        + '</div>';
    },

    /* 演示回退行（断线时，诚实标注） */
    _rowDemo: function(sym){
      var p = (typeof sqPoolFind === 'function') ? sqPoolFind(sym) : null;
      if(!p) return '';
      var cls = p.dir >= 0 ? 'up' : 'down';
      return '<div class="sq-si' + (sym === sqCur ? ' on' : '') + '" onclick="sqSel(\'' + sym + '\')">'
        + '<span><span class="nm">' + p.nm + '</span> <span class="cd">' + p.code + '</span></span>'
        + '<span class="rt"><span class="px ' + cls + '">' + p.px + '</span><br><span class="pc ' + cls + '">' + p.pc + '</span></span>'
        + '</div>';
    },

    render: function(d){
      if(!this._visible()) return;
      var box = document.getElementById('sq-list');
      if(!box) return;
      d = d || this._last;   /* 无参调用（切 tab 委托）回退到已缓存数据 */
      var h = this._statusHtml();
      var self = this;
      if(d && d.data && d.data.length){
        d.data.forEach(function(p){ h += self._rowReal(p); });
      } else if(this._mode === '断线' || this._mode === '未启动'){
        var holds = (typeof SQ_HOLD !== 'undefined') ? SQ_HOLD : [];
        holds.forEach(function(sym){ h += self._rowDemo(sym); });
      }
      box.innerHTML = h || (this._statusHtml() + '<div class="sq-intro">无持仓数据</div>');
      if(this._mode === '未启动') this._fetch();
    },

    _fetch: function(){
      if(!(window.ZK && ZK.api && ZK.api.fetchPosition)) return;
      var self = this;
      ZK.api.fetchPosition().then(function(r){
        if(r && r.ok){
          self._mode = (r.file_age_seconds !== undefined && r.file_age_seconds < 3600) ? '真源' : '延迟';
          self._mtime = r.file_mtime || null;
          self._account = r.account || null;
          self._last = r;
        } else {
          self._mode = '断线';   /* 桥文件缺失/解析异常 → 回退演示，诚实标注 */
          self._account = null;
          self._last = null;
        }
        if(self._visible()) self.render(self._last);
      }).catch(function(){
        self._mode = '断线';
        self._account = null;
        if(self._visible()) self.render(null);
      });
    },

    destroy: function(){
      clearInterval(this._timer);
      this._account = null;
    }
  };

  /* 持仓行点击桥接：非池内股票先入池（带真名真码），再走 sqSel 切换 K 线 */
  window.sqSelFromPos = function(sym, name, code){
    if(typeof sqPoolFind === 'function' && !sqPoolFind(sym) && typeof SQ_POOL !== 'undefined'){
      SQ_POOL.push({sym: sym, nm: name, code: code || sym, px: '--', pc: '--', dir: 0});
    }
    if(typeof sqSel === 'function') sqSel(sym);
  };

  ZK.registerFeature(mod);
  /* 加载链竞态兜底：若宿主已渲染过列表（hold tab），注册后主动接管渲染 */
  if(typeof sqCur !== 'undefined' && document.getElementById('sq-list')){
    mod.init();
    mod.render();
  }
})();
