/* 功能模块：量化分析（sq-quant-analysis）——右栏双源模型信号真源版 v1
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：/api/signals（CH.market_signal_history 两管道：
 *        factor_synth=因子截面「股票强不强」（momentum_20d 排名百分位） /
 *        strategy_weight=BTRUN 权重面板「系统想不想持有」）
 * #BT-PIPELINE-001 阶段四：交易页看到量化系统反馈（sq-quant-analysis 第 23 号组件）
 * 四态灯：绿=双源新鲜（factor≤4天） / 黄=过期 / 红=断线（显示提示无演示兜底） / 灰=未启动
 * 验收单：ACC-F-STOCKQ-QUANT-ANALYSIS
 */
(function(){
  var FACTOR_FRESH_DAYS = 4, STRATEGY_FRESH_DAYS = 7;

  function injectStyles(){
    if(document.getElementById('sq-qa-styles')) return;
    var st = document.createElement('style');
    st.id = 'sq-qa-styles';
    st.textContent = '.sq-qa-mode{font-size:10px;padding:2px 8px;border-radius:3px;cursor:help;float:right}'
      + '.sq-qa-mode.m-ok{background:rgba(37,167,80,.15);color:#25A750}'
      + '.sq-qa-mode.m-warn{background:rgba(240,185,11,.15);color:#F0B90B}'
      + '.sq-qa-mode.m-err{background:rgba(202,63,100,.15);color:#CA3F64}'
      + '.sq-qa-mode.m-na{background:rgba(255,255,255,.08);color:var(--faint)}'
      + '.sq-qa-dir{display:inline-block;padding:1px 7px;border-radius:9px;font-size:11px;font-weight:600;margin-right:6px}'
      + '.sq-qa-dir-buy{background:rgba(202,63,100,.18);color:#CA3F64}'
      + '.sq-qa-dir-sell{background:rgba(37,167,80,.18);color:#25A750}'
      + '.sq-qa-dir-hold{background:rgba(255,255,255,.08);color:var(--dim)}'
      + '.sq-qa-row{display:flex;justify-content:space-between;align-items:baseline;padding:4px 0;border-bottom:1px dashed var(--hair)}'
      + '.sq-qa-row .lab{color:var(--dim);font-size:11px}'
      + '.sq-qa-row .val{font-variant-numeric:tabular-nums;font-weight:600}'
      + '.sq-qa-sub{font-size:10px;color:var(--faint)}';
    document.head.appendChild(st);
  }

  function daysAgo(s){
    if(!s) return 999;
    var d = new Date(s.slice(0,10));
    return Math.round((Date.now() - d.getTime())/86400000);
  }
  function dirBadge(dir){
    var lb = dir==='buy'?'买入':(dir==='sell'?'卖出':(dir==='hold'?'持有':'中性'));
    return '<span class="sq-qa-dir sq-qa-dir-'+(dir||'hold')+'">'+lb+'</span>';
  }
  function esc(s){
    return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});
  }

  var mod = {
    id: 'sq-quant-analysis',
    chart: null,
    init: function(chart, ctx){ this.chart = chart; injectStyles(); },
    render: function(d){
      injectStyles();
      var box = document.getElementById('sq-quant-analysis');
      if(!box) return;
      var sym = (typeof sqCur !== 'undefined') ? String(sqCur).split('.')[0] : null;
      if(!sym || !(window.ZK && ZK.api && ZK.api.fetchSignals)){ box.innerHTML = sec('未启动'); return; }
      box.innerHTML = sec('加载中…');
      ZK.api.fetchSignals([sym]).then(function(r){
        if(!r || !r.ok){ box.innerHTML = sec('断线', 'm-err', 'API 不可达——本块无演示兜底（真实数据纪律）'); return; }
        var fs = null, sw = null;
        (r.data||[]).forEach(function(s){
          if(s.symbol !== sym) return;
          if(s.source==='factor_synth') fs = s;
          if(s.source==='strategy_weight') sw = s;
        });
        var h = '';
        /* 因子信号（管道B） */
        if(fs){
          var m = fs.meta || {};
          h += '<div class="sq-qa-row"><span class="lab">因子信号（股票强不强）</span><span class="val">'+dirBadge(fs.direction)
            + (fs.score>=0?'+':'')+fs.score.toFixed(2)+' <span class="sq-qa-sub">截面 #'+fs.rank+'/'+(m.universe_size||'—')+'</span></span></div>'
            + '<div class="sq-qa-row"><span class="lab">动量因子 20d</span><span class="val">'+(m.momentum_20d!=null?((m.momentum_20d>=0?'+':'')+(m.momentum_20d*100).toFixed(1)+'%'):'--')+'</span></div>';
        } else {
          h += '<div class="sq-qa-row"><span class="lab">因子信号</span><span class="sq-qa-sub">未覆盖（不在因子宇宙：HS300∪持仓∪附加）</span></div>';
        }
        /* 策略信号（管道A） */
        if(sw){
          h += '<div class="sq-qa-row"><span class="lab">策略信号（系统想不想持有）</span><span class="val">'+dirBadge(sw.direction)
            + (sw.score*100).toFixed(1)+'% <span class="sq-qa-sub">'+esc(sw.signal_id)+'</span></span></div>';
        } else {
          h += '<div class="sq-qa-row"><span class="lab">策略信号</span><span class="sq-qa-sub">未选入（最新回测无此票）</span></div>';
        }
        /* 四态 */
        var fAge = fs ? daysAgo(fs.trade_date) : 999;
        var sAge = sw ? daysAgo(sw.trade_date) : 999;
        var cls = 'm-ok', lab = '真源', tip = 'factor '+fAge+'天 / strategy '+sAge+'天前';
        if(!fs && !sw){ cls='m-na'; lab='未覆盖'; tip='该股两条管道均无信号'; }
        else if(fAge>FACTOR_FRESH_DAYS && sAge>STRATEGY_FRESH_DAYS){ cls='m-err'; lab='过期'; }
        else if(fAge>FACTOR_FRESH_DAYS || sAge>STRATEGY_FRESH_DAYS){ cls='m-warn'; lab='延迟'; }
        box.innerHTML = sec(lab, cls, tip) + h
          + '<div class="note">两列互补：因子分高≠系统持有（top_n/风控可拦截）；策略持有≠因子强（组合约束）。DEC-INV-002：信号仅供参考不触发下单</div>';
      }).catch(function(){
        box.innerHTML = sec('断线','m-err','API 不可达——本块无演示兜底');
      });
      function sec(lab, cls, tip){
        return '<div class="sq-sec"><span>量化分析</span>'
          + '<span class="sq-qa-mode '+(cls||'m-na')+'" title="'+(tip||'DS-12 四态：绿=双源新鲜(factor≤4天/strategy≤7天) / 黄=单源过期 / 红=断线 / 灰=未启动或未覆盖')+'">'+(lab||'未启动')+'</span></div>';
      }
    },
    destroy: function(){}
  };
  ZK.registerFeature(mod);
  if(typeof sqCur !== 'undefined' && document.getElementById('sq-quant-analysis')){ mod.render(); }
})();
