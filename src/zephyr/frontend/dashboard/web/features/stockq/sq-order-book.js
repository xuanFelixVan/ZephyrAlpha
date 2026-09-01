/* 功能模块：五档挂单（sq-order-book）——QMT 文件桥真源版
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：/api/orderbook（E:\qmt_bridge\quote.csv，QMT 终端订阅标的快照导出）
 * 背景：miniQMT 2026-09-18 券商关停，盘口走文件桥（Owner 2026-09-01 裁定）
 * 边界（诚实口径）：quote.csv 只含 QMT 订阅标的；未订阅→灰灯"未订阅"，
 *   三只演示标的（600519/300750/688981）断线回退演示 l2 数据（标"断线·演示"）
 * 四态灯：绿=真源（timetag 当日） / 黄=延迟（timetag 非当日，显示时间） / 红=断线·演示 / 灰=未订阅（DS-12）
 * 验收单：ACC-F-STOCKQ-ORDER-BOOK
 */
(function(){
  function injectStyles(){
    if(document.getElementById('sq-order-book-styles')) return;
    var st = document.createElement('style');
    st.id = 'sq-order-book-styles';
    st.textContent = '.sq-ob-mode{font-size:10px;padding:2px 8px;border-radius:3px;cursor:help;float:right}'
      + '.sq-ob-mode.dm-真源{background:rgba(37,167,80,.15);color:#25A750}'
      + '.sq-ob-mode.dm-延迟{background:rgba(240,185,11,.15);color:#F0B90B}'
      + '.sq-ob-mode.dm-断线{background:rgba(202,63,100,.15);color:#CA3F64}'
      + '.sq-ob-mode.dm-未订阅{background:rgba(255,255,255,.08);color:var(--faint)}';
    document.head.appendChild(st);
  }

  var MODE_TITLE = '数据源状态灯（DS-12）：绿=真源（文件桥 quote.csv 当日快照） / 黄=延迟（快照非当日） / 红=断线·演示（回退演示五档） / 灰=未订阅（QMT quote.csv 无此标的）。miniQMT 2026-09-18 关停，盘口走文件桥';

  /* '20260826 15:00:17' → '08-26 15:00' */
  function fmtTag(t){
    if(!t || t.length < 14) return t || '--';
    return t.slice(4, 6) + '-' + t.slice(6, 8) + ' ' + t.slice(9, 14);
  }

  function modeLabel(mode, timetag){
    if(mode === '真源') return '● 真源 · ' + fmtTag(timetag);
    if(mode === '延迟') return '● 延迟 · 截至 ' + fmtTag(timetag);
    if(mode === '断线') return '● 断线·演示';
    return '○ 未订阅';
  }

  var mod = {
    id: 'sq-order-book',
    chart: null,

    init: function(chart, ctx){
      this.chart = chart;
      injectStyles();
    },

    /* 通用盘口 HTML（档位自适应：bids/asks 为 [[价,量]×N]，N=5 五档 / N=10 十档，导出列决定） */
    _bookHtml: function(asks, bids, mode, timetag){
      var n = Math.min(asks.length, bids.length);
      if(!n) return '';
      var vmax = 0;
      asks.concat(bids).forEach(function(l){ vmax = Math.max(vmax, l[1]); });
      var h = '<div class="sq-sec"><span>' + (n >= 10 ? '十档挂单' : '五档挂单') + '</span>'
        + '<span class="sq-ob-mode dm-' + mode + '" title="' + MODE_TITLE + '">' + modeLabel(mode, timetag) + '</span></div>'
        + '<div class="sq-l2">';
      var i;
      for(i = n - 1; i >= 0; i--){
        h += '<div class="lr"><span style="color:var(--down)">卖' + (i + 1) + '</span><span class="lbar"><i style="width:' + (vmax ? (asks[i][1] / vmax * 100).toFixed(0) : 0) + '%;background:#25A750;opacity:.35"></i></span><span class="lp" style="color:var(--down)">' + Number(asks[i][0]).toFixed(2) + '</span><span class="lv">' + asks[i][1] + '</span></div>';
      }
      for(i = 0; i < n; i++){
        h += '<div class="lr"><span style="color:var(--up)">买' + (i + 1) + '</span><span class="lbar"><i style="width:' + (vmax ? (bids[i][1] / vmax * 100).toFixed(0) : 0) + '%;background:#CA3F64;opacity:.35"></i></span><span class="lp" style="color:var(--up)">' + Number(bids[i][0]).toFixed(2) + '</span><span class="lv">' + bids[i][1] + '</span></div>';
      }
      return h + '</div>';
    },

    _placeholder: function(mode, note){
      return '<div class="sq-sec"><span>五档挂单</span>'
        + '<span class="sq-ob-mode dm-' + mode + '" title="' + MODE_TITLE + '">' + modeLabel(mode) + '</span></div>'
        + '<div class="sq-intro">' + note + '</div>';
    },

    render: function(d){
      var box = document.getElementById('sq-order-book');
      if(!box) return;
      var sym = (typeof sqCur !== 'undefined') ? sqCur : null;
      if(!sym) return;

      /* 第一拍：演示回退（诚实标注），真源回来后覆盖 */
      var demo = (typeof STOCKQ_D !== 'undefined') ? STOCKQ_D[sym] : null;
      if(demo && demo.l2){
        box.innerHTML = this._bookHtml(demo.l2.slice(0, 5), demo.l2.slice(5, 10), '断线', '');
      } else {
        box.innerHTML = this._placeholder('未订阅', '五档待接入（真源 /api/orderbook：文件桥 quote.csv）');
      }

      var self = this;
      if(window.ZK && ZK.api && ZK.api.fetchOrderbook){
        ZK.api.fetchOrderbook(sym).then(function(r){
          if(!(r && r.ok && r.data)) return;   /* 未订阅/失败：保持回退（演示标的）或占位 */
          var v = r.data;
          if(!v.bids || !v.bids.length || !v.asks || !v.asks.length) return;
          var today = new Date().toISOString().slice(0, 10);
          var mode = (v.timetag || '').slice(0, 10) === today ? '真源' : '延迟';
          box.innerHTML = self._bookHtml(v.asks, v.bids, mode, v.timetag);
        }).catch(function(){ /* 静默：演示回退已标注 */ });
      }
    },

    destroy: function(){ /* 纯 DOM 渲染，无定时器/监听需清理 */ }
  };

  ZK.registerFeature(mod);
  /* 加载链竞态兜底：若 sqRenderInfo 已执行（容器已在 DOM），注册后主动渲染 */
  if(typeof sqCur !== 'undefined' && document.getElementById('sq-order-book')){ mod.render(); }
})();
