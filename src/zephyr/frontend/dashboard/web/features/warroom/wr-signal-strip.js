/* 功能模块：量化信号总览（wr-signal-strip）——warroom 双管道聚合真源版 v1
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：/api/signals-overview（CH.market_signal_history：
 *        factor_synth=因子截面 buy/sell/hold 分布 + top5/bottom5 /
 *        strategy_weight=BTRUN 最新权重面板持有清单）
 * #BT-PIPELINE-001 阶段四；轮询 5min；无演示兜底（真源纪律）
 * 验收单：ACC-F-WR-SIGNAL-STRIP
 */
(function(){
  var POLL_MS = 300000;

  function esc(s){
    return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});
  }
  function fmtSym(sym){
    var label = sym;
    return '<span style="cursor:pointer;text-decoration:underline" onclick="go(\'stockq\');setTimeout(function(){if(window.sqSel)sqSel(\''+esc(sym)+'\')},80)" title="去个股行情页">'+esc(label)+'</span>';
  }

  function render(r){
    var box = document.getElementById('wr-signal-body');
    if(!box) return;
    if(!r || !r.ok || !r.data || !r.data.length){
      box.innerHTML = '<div class="dim" style="padding:8px 0">信号表空或 API 不可达——跑 python scripts/compute_signals.py（管道B）或页面发起回测（管道A）</div>';
      return;
    }
    var ex = r.extremes || {};
    var h = '<table><tr><th>管道</th><th>截至</th><th>买入</th><th>卖出</th><th>持有</th><th>最强 5（点击跳转）</th><th>最弱 5</th></tr>';
    r.data.forEach(function(s){
      var key = s.source + ':' + s.signal_id;
      var e = ex[key] || {top5:[], bottom5:[]};
      var srcName = s.source==='factor_synth' ? '因子截面（股票强不强）' : 'BTRUN 权重（系统想不想持有）';
      var fmt5 = function(arr){ return arr.length ? arr.map(function(x){ return fmtSym(x.symbol)+' <span class="dim">'+(x.score>=0?'+':'')+x.score.toFixed(2)+'</span>'; }).join(' · ') : '<span class="dim">—</span>'; };
      h += '<tr><td><b>'+esc(s.signal_id)+'</b><br><span class="dim" style="font-size:10px">'+srcName+'</span></td>'
        + '<td class="dim">'+esc(s.trade_date)+'</td>'
        + '<td class="up"><b>'+s.buy+'</b></td><td class="down"><b>'+s.sell+'</b></td><td>'+s.hold+'</td>'
        + '<td>'+fmt5(e.top5)+'</td><td>'+fmt5(e.bottom5)+'</td></tr>';
    });
    h += '</table>';
    box.innerHTML = h;
  }

  function fetchAll(){
    if(!(window.ZK && ZK.api && ZK.api.fetchSignalsOverview)){ return; }
    ZK.api.fetchSignalsOverview().then(render).catch(function(){
      var box = document.getElementById('wr-signal-body');
      if(box) box.innerHTML = '<div class="dim" style="padding:8px 0">API 断线——本卡无演示兜底（真源纪律）</div>';
    });
  }

  var mod = {
    id: 'wr-signal-strip',
    chart: null,
    _timer: null,
    init: function(){ fetchAll(); this._timer = setInterval(fetchAll, POLL_MS); },
    render: function(){ fetchAll(); },
    destroy: function(){ if(this._timer) clearInterval(this._timer); }
  };
  ZK.registerFeature(mod);
  if(document.readyState !== 'loading'){ mod.init(); }
  else { document.addEventListener('DOMContentLoaded', function(){ mod.init(); }); }
})();
