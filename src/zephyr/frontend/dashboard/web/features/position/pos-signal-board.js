/* 功能模块：量化信号看板（pos-signal-board）——持仓页模型反馈真源版 v1
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：/api/position（QMT 文件桥真实持仓）× /api/signals（market_signal_history 两管道：
 *        factor_synth=因子截面「股票强不强」 / strategy_weight=BTRUN 权重面板「系统想不想持有」）
 * #BT-PIPELINE-001 阶段四：交易页看到量化系统反馈（Owner 2026-09-01 裁定持仓页优先）
 * 四态灯：绿=持仓+双源信号均新鲜 / 黄=信号过期（factor>4天 或 strategy>7天，显示截至日） /
 *        红=API 断线（本卡无演示兜底——真实持仓页不许造假数据，断线明示） / 灰=未启动
 * 轮询：60s；交互：行点击跳个股行情页（stockq）
 * 验收单：ACC-F-POS-SIGNAL-BOARD
 */
(function(){
  var POLL_MS = 60000;
  var FACTOR_FRESH_DAYS = 4;    /* FEH-PC-006：日级数据新鲜窗口 4 天 */
  var STRATEGY_FRESH_DAYS = 7;  /* 回测批不定频，7 天窗口 */

  function injectStyles(){
    if(document.getElementById('pos-signal-styles')) return;
    var st = document.createElement('style');
    st.id = 'pos-signal-styles';
    st.textContent = '.pos-sig-status{display:flex;justify-content:space-between;align-items:center;gap:6px;font-size:11px;padding:2px 4px 8px;cursor:help}'
      + '.pos-sig-status .st{display:flex;align-items:center;gap:5px}'
      + '.pos-sig-status .dot{width:7px;height:7px;border-radius:50%;flex:none}'
      + '.pos-sig-dot-ok{background:#25A750}.pos-sig-dot-warn{background:#F0B90B}'
      + '.pos-sig-dot-err{background:#CA3F64}.pos-sig-dot-na{background:var(--faint)}'
      + '.pos-sig-dir{display:inline-block;padding:1px 7px;border-radius:9px;font-size:11px;font-weight:600;margin-right:6px}'
      + '.pos-sig-dir-buy{background:rgba(202,63,100,.18);color:#CA3F64}'
      + '.pos-sig-dir-sell{background:rgba(37,167,80,.18);color:#25A750}'
      + '.pos-sig-dir-hold{background:rgba(255,255,255,.08);color:var(--dim)}'
      + '.pos-sig-score{font-variant-numeric:tabular-nums;color:var(--text);font-weight:600}'
      + '.pos-sig-sub{font-size:10px;color:var(--faint)}'
      + '.pos-sig-row{cursor:pointer}.pos-sig-row:hover td{background:rgba(255,255,255,.04)}';
    document.head.appendChild(st);
  }

  var STATUS_TITLE = '数据源状态灯（DS-12）：绿=持仓文件+双源信号均新鲜 / 黄=信号过期（factor>4天或strategy>7天） / 红=API断线（本卡真实数据无演示兜底） / 灰=未启动。信号真源=c1_market.market_signal_history（管道A strategy_weight=BTRUN权重 / 管道B factor_synth=日频因子截面）';

  function api(){ return (window.ZK && ZK.api) ? ZK.api : null; }

  function daysAgo(dateStr){
    if(!dateStr) return 999;
    var d = new Date(dateStr.slice(0,10));
    return Math.round((Date.now() - d.getTime()) / 86400000);
  }

  function dirBadge(dir){
    var label = dir==='buy' ? '买入' : (dir==='sell' ? '卖出' : (dir==='hold' ? '持有' : '中性'));
    return '<span class="pos-sig-dir pos-sig-dir-'+(dir||'hold')+'">'+label+'</span>';
  }

  function esc(s){
    return String(s==null?'':s).replace(/[&<>"']/g, function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }

  function render(pos, sigs){
    injectStyles();
    var body = document.getElementById('pos-signal-body');
    var light = document.getElementById('pos-signal-light');
    var label = document.getElementById('pos-signal-label');
    if(!body) return;

    if(!pos || !pos.ok || !pos.data || !pos.data.length){
      body.innerHTML = '<tr><td colspan="7" class="dim" style="text-align:center;padding:14px">QMT 文件桥无持仓数据（终端未开或 E:\\qmt_bridge\\Stock 无导出）</td></tr>';
      if(light){ light.className = 'dot pos-sig-dot-err'; }
      if(label){ label.textContent = '断线·持仓源不可用'; }
      return;
    }

    /* signals 按 symbol+source 索引 */
    var byKey = {};
    (sigs && sigs.data || []).forEach(function(s){ byKey[s.symbol+'|'+s.source] = s; });

    var stale = [];
    var h = '<tr><th>标的</th><th>名称</th><th>数量</th><th>现价</th><th>因子信号<br><span class="pos-sig-sub">股票强不强（截面排名）</span></th><th>策略信号<br><span class="pos-sig-sub">系统想不想持有（BTRUN权重）</span></th><th>信号截至</th></tr>';
    pos.data.forEach(function(p){
      var code = p.symbol;
      var fs = byKey[code+'|factor_synth'];
      var sw = byKey[code+'|strategy_weight'];
      var fCell, sCell, asOf = '';
      if(fs){
        fCell = dirBadge(fs.direction)+'<span class="pos-sig-score">'+(fs.score>=0?'+':'')+fs.score.toFixed(2)+'</span>'
              + ' <span class="pos-sig-sub">#'+fs.rank+'/'+(fs.meta&&fs.meta.universe_size||'—')+'</span>';
        asOf = fs.trade_date;
      } else {
        fCell = '<span class="dim">未覆盖</span><span class="pos-sig-sub">（不在因子宇宙）</span>';
        stale.push(code+':factor');
      }
      if(sw){
        sCell = dirBadge(sw.direction)+'<span class="pos-sig-score">'+(sw.score*100).toFixed(1)+'%</span>'
              + ' <span class="pos-sig-sub">'+esc(sw.signal_id)+'</span>';
        if(!asOf || sw.trade_date > asOf) asOf = asOf || sw.trade_date;
      } else {
        sCell = '<span class="dim">未选入</span><span class="pos-sig-sub">（最新回测无此票）</span>';
      }
      h += '<tr class="pos-sig-row" onclick="go(\'stockq\');setTimeout(function(){if(window.sqSel)sqSel(\''+esc(code)+'\')},80)" title="点击去个股行情页">'
        + '<td><b>'+esc(code)+'</b></td><td>'+esc(p.name)+'</td>'
        + '<td class="pos-sig-score">'+p.qty+'</td><td class="pos-sig-score">'+p.price.toFixed(2)+'</td>'
        + '<td>'+fCell+'</td><td>'+sCell+'</td><td class="pos-sig-sub">'+esc(asOf||'—')+'</td></tr>';
    });
    body.innerHTML = h;

    /* 四态裁决 */
    var fAge = 999, sAge = 999;
    (sigs && sigs.data || []).forEach(function(s){
      if(s.source==='factor_synth') fAge = Math.min(fAge, daysAgo(s.trade_date));
      if(s.source==='strategy_weight') sAge = Math.min(sAge, daysAgo(s.trade_date));
    });
    var mode, txt;
    if(fAge > FACTOR_FRESH_DAYS && sAge > STRATEGY_FRESH_DAYS){
      mode = 'err'; txt = '信号过期·两条管道均未刷新（factor '+fAge+'天 / strategy '+sAge+'天）——跑 python scripts/compute_signals.py 或页面发起回测';
    } else if(fAge > FACTOR_FRESH_DAYS || sAge > STRATEGY_FRESH_DAYS){
      mode = 'warn'; txt = '延迟·factor '+fAge+'天 / strategy '+sAge+'天';
    } else {
      mode = 'ok'; txt = '真源·factor '+fAge+'天前 / strategy '+sAge+'天前';
    }
    if(light){ light.className = 'dot pos-sig-dot-'+mode; }
    if(label){ label.textContent = txt; }
  }

  function fetchAll(){
    var a = api();
    if(!a){ render(null, null); return; }
    a.fetchPosition().then(function(pos){
      if(!pos || !pos.ok){ render(pos, null); return; }
      var codes = pos.data.map(function(p){ return p.symbol; }).join(',');
      return a.fetchJson('/api/signals?symbols='+encodeURIComponent(codes)).then(function(sigs){
        render(pos, sigs);
      });
    }).catch(function(){ render(null, null); });
  }

  var mod = {
    id: 'pos-signal-board',
    chart: null,
    _timer: null,
    init: function(){ injectStyles(); fetchAll(); this._timer = setInterval(fetchAll, POLL_MS); },
    render: function(){ fetchAll(); },
    destroy: function(){ if(this._timer) clearInterval(this._timer); }
  };
  ZK.registerFeature(mod);
  /* 自启动兜底：宿主 posInit 未挂接时组件自行起跳（loader 保证 ZK.api 先就位） */
  if(document.readyState !== 'loading'){ mod.init(); }
  else { document.addEventListener('DOMContentLoaded', function(){ mod.init(); }); }
})();
