/* 功能模块：关键数据表（sq-key-data）
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：/api/stock-header（kline_daily 价格 + daily_valuation 估值 + stock_basic 资料）
 * 四态灯：绿=真源（数据新鲜） / 黄=延迟（>5 日） / 红=断线（回退演示） / 灰=未启动（DS-12）
 * 演示回退：STOCKQ_D[sqCur].kv（仅 3 只演示标的）或"待接入"占位，均诚实标注
 * 验收单：ACC-F-STOCKQ-KEY-DATA
 */
(function(){
  function injectStyles(){
    if(document.getElementById('sq-key-data-styles')) return;
    var st = document.createElement('style');
    st.id = 'sq-key-data-styles';
    st.textContent = '.sq-kd-mode{font-size:10px;padding:2px 8px;border-radius:3px;cursor:help;float:right}'
      + '.sq-kd-mode.dm-真源{background:rgba(37,167,80,.15);color:#25A750}'
      + '.sq-kd-mode.dm-延迟{background:rgba(240,185,11,.15);color:#F0B90B}'
      + '.sq-kd-mode.dm-断线{background:rgba(202,63,100,.15);color:#CA3F64}'
      + '.sq-kd-mode.dm-未启动{background:rgba(255,255,255,.08);color:var(--faint)}';
    document.head.appendChild(st);
  }

  function modeLabel(mode){
    return mode==='真源'?'● 真源':mode==='延迟'?'● 延迟':mode==='断线'?'● 断线·演示':'○ 未启动';
  }

  /* 数据新鲜度：trade_date 距今 >5 自然日=延迟（容忍周末+短假） */
  function fresh(iso){
    if(!iso) return false;
    var t = new Date(iso + 'T00:00:00');
    return (Date.now() - t.getTime()) < 5 * 86400000;
  }

  function fmtVol(v){ return (v / 10000).toFixed(2) + ' 万手'; }
  function fmtAmt(a){ return (a / 1e8).toFixed(2) + ' 亿'; }

  var mod = {
    id: 'sq-key-data',
    chart: null,

    init: function(chart, ctx){
      this.chart = chart;
      injectStyles();
    },

    _kvHtml: function(rows, mode){
      var h = '<div class="sq-sec"><span>关键数据</span>'
        + '<span class="sq-kd-mode dm-' + mode + '" title="数据源状态灯（DS-12）：绿=真源（kline_daily 最新日线） / 黄=数据延迟（>5 日） / 红=断线（回退演示） / 灰=服务未启动">' + modeLabel(mode) + '</span></div>'
        + '<div class="sq-kv-grid">';
      rows.forEach(function(kv){
        h += '<span class="k">' + kv[0] + '</span><span class="v" style="grid-column:span 2">' + kv[1] + '</span>';
      });
      return h + '</div>';
    },

    render: function(d){
      var box = document.getElementById('sq-key-data');
      if(!box) return;
      var sym = (typeof sqCur !== 'undefined') ? sqCur : null;

      /* 第一拍：演示回退（诚实标注），API 回来后第二拍覆盖 */
      var demo = (typeof STOCKQ_D !== 'undefined' && sym) ? STOCKQ_D[sym] : null;
      if(demo && demo.kv){
        box.innerHTML = this._kvHtml(demo.kv, '断线');
      } else {
        box.innerHTML = '<div class="sq-sec"><span>关键数据</span>'
          + '<span class="sq-kd-mode dm-未启动" title="数据源状态灯（DS-12）：绿=真源 / 黄=延迟 / 红=断线·演示 / 灰=服务未启动">○ 未启动</span></div>'
          + '<div class="sq-intro">关键数据待接入（真源 /api/stock-header：kline_daily + daily_valuation）</div>';
      }

      var self = this;
      if(window.ZK && ZK.api && ZK.api.fetchStockHeader && sym){
        ZK.api.fetchStockHeader(sym).then(function(r){
          if(!(r && r.ok && r.data)) return;   /* 失败保持演示回退，状态灯已标"断线·演示" */
          var v = r.data;
          var f2 = function(x){ return (x === null || x === undefined) ? '--' : Number(x).toFixed(2); };
          var amp = (v.preclose > 0 && v.high !== null && v.low !== null)
            ? ((v.high - v.low) / v.preclose * 100).toFixed(2) + '%' : '--';
          var rows = [
            ['最高', f2(v.high)],
            ['最低', f2(v.low)],
            ['开盘', f2(v.open)],
            ['昨收', f2(v.preclose)],
            ['量比', (v.volume_ratio === null || v.volume_ratio === undefined) ? '--' : Number(v.volume_ratio).toFixed(2)],
            ['换手', (v.turnover === null || v.turnover === undefined) ? '--（待接入）' : Number(v.turnover).toFixed(2) + '%'],
            ['市盈TTM', (v.pe_ttm === null || v.pe_ttm === undefined) ? '--' : Number(v.pe_ttm).toFixed(1)],
            ['市净MRQ', (v.pb_mrq === null || v.pb_mrq === undefined) ? '--' : Number(v.pb_mrq).toFixed(2)],
            ['成交量', v.volume ? fmtVol(v.volume) : '--'],
            ['成交额', v.amount ? fmtAmt(v.amount) : '--'],
            ['振幅', amp]
          ];
          box.innerHTML = self._kvHtml(rows, fresh(v.trade_date) ? '真源' : '延迟');
        }).catch(function(){ /* 静默：演示回退已标"断线·演示" */ });
      }
    },

    destroy: function(){ /* 纯 DOM 渲染，无定时器/监听需清理 */ }
  };

  ZK.registerFeature(mod);
  /* 加载链竞态兜底：若 sqRenderInfo 已执行（容器已在 DOM），注册后主动渲染 */
  if(typeof sqCur !== 'undefined' && document.getElementById('sq-key-data')){ mod.render(); }
})();
