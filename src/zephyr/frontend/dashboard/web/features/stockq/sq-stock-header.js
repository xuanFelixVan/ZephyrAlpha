/* 功能模块：股票标题（sq-stock-header）
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：/api/stock-header（CH.daily_valuation + stock_basic）
 * 四态灯：绿=真源正常 / 黄=数据延迟 / 红=断线（回退演示） / 灰=服务未启动（DS-12）
 * 验收单：ACC-F-STOCKQ-STOCK-HEADER
 */
(function(){
  function injectStyles(){
    if(document.getElementById('sq-stock-header-styles')) return;
    var st = document.createElement('style');
    st.id = 'sq-stock-header-styles';
    st.textContent = '.sq-stock-header{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:8px}'
      + '.sq-stock-header .nm{font-size:16px;font-weight:700}'
      + '.sq-stock-header .cd{color:var(--faint);font-size:11px}'
      + '.sq-stock-header .px{font-size:20px;font-weight:500;font-variant-numeric:tabular-nums}'
      + '.sq-stock-header .chg{font-size:13px;font-variant-numeric:tabular-nums}'
      + '.sq-stock-header .up{color:var(--up)}'
      + '.sq-stock-header .down{color:var(--down)}'
      + '.sq-stock-header .klp-datamode{font-size:10px;padding:2px 8px;border-radius:3px;cursor:help}'
      + '.sq-stock-header .dm-真源{background:rgba(37,167,80,.15);color:#25A750}'
      + '.sq-stock-header .dm-延迟{background:rgba(240,185,11,.15);color:#F0B90B}'
      + '.sq-stock-header .dm-断线{background:rgba(202,63,100,.15);color:#CA3F64}'
      + '.sq-stock-header .dm-未启动{background:rgba(255,255,255,.08);color:var(--faint)}';
    document.head.appendChild(st);
  }

  function modeLabel(mode){
    return mode==='真源'?'● 真源':mode==='延迟'?'● 延迟':mode==='断线'?'● 断线·演示':'○ 未启动';
  }

  var mod = {
    id: 'sq-stock-header',
    chart: null,
    _el: null,
    _symbol: null,

    init: function(chart, ctx){
      this.chart = chart;
      injectStyles();
      this._el = document.getElementById('sq-head');
      this._symbol = (typeof sqCur !== 'undefined') ? sqCur : '600519';
    },

    _renderAll: function(poolItem, apiData, mode){
      var box = this._el || document.getElementById('sq-head');
      if(!box) return;
      var name = apiData ? apiData.name : poolItem.nm;
      var code = apiData ? apiData.code : poolItem.code;
      var price = apiData ? apiData.price.toFixed(2) : poolItem.px;
      var pctStr = apiData ? apiData.pct_change_str : poolItem.pc;
      var dir = apiData ? apiData.direction : (poolItem.dir >= 0 ? 'up' : 'down');
      var modeClass = 'dm-' + (mode || '未启动');
      var ml = modeLabel(mode);

      var tfVis = (typeof klpTfVis !== 'undefined') ? klpTfVis : ['1分','5分','15分','30分','60分','日','周','月'];
      var curTf = (typeof sqTf !== 'undefined') ? sqTf : '日';
      var tfHtml = '<span class="sq-tfs">' + tfVis.map(function(t){
        return '<span class="tab' + (t===curTf?' on':'') + '" onclick="sqTfSet(\''+t+'\',this)">'+t+'</span>';
      }).join('') + '<span class="tab klp-tf-more" title="更多周期（含自定义主栏显示/快捷键 1~9）" onclick="klpTfPop(event)">▾</span></span>';

      var marks = (typeof klpMarks !== 'undefined') ? klpMarks : {bs:true,trade:true,chip:true,evt:true,cost:false};
      var marksHtml = '<span class="klp-marks">'
        + '<span class="klp-mark-tgl' + (marks.bs?' on':'') + '" title="量化买卖点：±3 根摆动高低点信号标注（▲买 ▼卖，灰色弱提示）" onclick="klpTglMark(\'bs\',this)">⇅</span>'
        + '<span class="klp-mark-tgl' + (marks.trade?' on':'') + '" title="真实成交买卖点：实盘/回测成交标记（红框 B=买入 绿框 S=卖出）" onclick="klpTglMark(\'trade\',this)">◍</span>'
        + '<span class="klp-mark-tgl' + (marks.chip?' on':'') + '" title="筹码峰：48 桶成本分布+POC 成本线+获利比例，随光标重算" onclick="klpTglMark(\'chip\',this)">▤</span>'
        + '<span class="klp-mark-tgl' + (marks.evt?' on':'') + '" title="事件时间线：财报/解禁/宏观事件图标（整行收展），点击查看详情" onclick="klpTglMark(\'evt\',this)">⚑</span>'
        + '<span class="klp-mark-tgl' + (marks.cost?' on':'') + '" title="成本线：筹码峰平均成本横线（黄色虚线，悬停显示成本/数量）" onclick="klpTglMark(\'cost\',this)">¥</span>'
        + '</span>';

      var h = '<div class="sq-stock-header">'
        + '<span class="nm">' + name + '</span>'
        + '<span class="cd">' + code + (apiData ? '' : '（资料待接入）') + '</span>'
        + '<span class="px ' + dir + '">' + price + '</span>'
        + '<span class="chg ' + dir + '">' + pctStr + '</span>'
        + '<span class="klp-datamode ' + modeClass + '" title="数据源状态灯（DS-12）：绿=真源正常 / 黄=数据延迟（取到但过期） / 红=断线（回退演示数据） / 灰=服务未启动">' + ml + '</span>'
        + tfHtml + marksHtml
        + '<span class="sq-togs"><span class="sq-fb" onclick="fbReport(\'chart\',\'K线工作台（' + name + '）\',this)">⚑报错</span></span>'
        + '</div>';
      box.innerHTML = h;
    },

    _updateTitle: function(apiData){
      var box = this._el || document.getElementById('sq-head');
      if(!box) return;
      var nm = box.querySelector('.nm');
      var cd = box.querySelector('.cd');
      var px = box.querySelector('.px');
      var chg = box.querySelector('.chg');
      var dm = box.querySelector('.klp-datamode');
      if(nm) nm.textContent = apiData.name;
      if(cd) cd.textContent = apiData.code;
      if(px){ px.textContent = apiData.price.toFixed(2); px.className = 'px ' + apiData.direction; }
      if(chg){ chg.textContent = apiData.pct_change_str; chg.className = 'chg ' + apiData.direction; }
      if(dm){ dm.className = 'klp-datamode dm-真源'; dm.textContent = '● 真源'; }
    },

    render: function(d){
      var box = this._el || document.getElementById('sq-head');
      if(!box) return;
      var symbol = this._symbol || (typeof sqCur !== 'undefined' ? sqCur : '600519');
      var mode = (typeof klpDataMode !== 'undefined') ? klpDataMode : '未启动';
      var p = (typeof sqPoolFind === 'function') ? sqPoolFind(symbol) : null;
      if(!p) p = {nm:symbol, code:symbol, px:'--', pc:'--', dir:0};

      this._renderAll(p, null, mode);

      var self = this;
      if(window.ZK && ZK.api && ZK.api.fetchStockHeader){
        ZK.api.fetchStockHeader(symbol).then(function(r){
          if(r && r.ok && r.data){ self._updateTitle(r.data); }
        }).catch(function(){ /* 静默：状态灯已标示断线/演示 */ });
      }
    },

    destroy: function(){
      if(this._el) this._el.innerHTML = '';
      this._el = null; this._symbol = null;
    }
  };

  ZK.registerFeature(mod);
  /* 加载链竞态兜底：若 sqInit 已执行（sqRenderHead 走了老代码路径），注册后主动触发渲染 */
  if(typeof sqCur !== 'undefined' && typeof sqPoolFind === 'function'){ mod.render(); }
})();
