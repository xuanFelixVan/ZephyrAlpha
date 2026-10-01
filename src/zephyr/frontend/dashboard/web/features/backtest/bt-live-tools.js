/* 功能模块：回测页真源工具族（bt-live-tools）——W-E2/W-E4 通宵战役（2026-10-01，st-fullscore-20260930）
 * 契约：页面引擎全局函数族（页面 onclick 直接绑定全局名，同 bt-engine 模式）；
 * 数据源：/api/regime/current（7 态词表只读投影，MOD-REGIME-001 regime_detector.REGIME_STATES）
 *        + /api/tdm/verdicts?run_id=（node_verdict 台账按 run 反查，记录形状同 /api/tdm/validation）。
 * 演示诚实纪律：真源缺位/不可达=状态行显式降级披露，不填假序列、不冒充"未验证"。
 * 取数纪律：一律走 services/api.js（ZK.api，绝对 BASE）——app:// 回退模式裸相对 fetch 必断。
 * 消费者：pages/backtest.html（#btfw-regime-series 按钮 / #bt-verdict-card 台账区块）。
 */
function btRegimeFetch(){
  var st=document.getElementById('btfw-regime-status');
  var ta=document.getElementById('btfw-regime-series');
  function say(msg){ if(st) st.textContent=msg; }
  if(!(window.ZK&&ZK.api)){ say('API 通道未就绪（services/api.js 未加载）'); return; }
  say('拉取中…');
  ZK.api.fetchJson('/api/regime/current',8000).then(function(r){
    if(!r||!r.ok){ say('拉取失败：'+((r&&r.error)||'API 响应异常')); return; }
    var words=(r.states||[]).map(function(s){return s.state;}).join('/');
    if(r.recent_series&&r.recent_series.length&&ta){
      ta.value=JSON.stringify(r.recent_series);
      say('已填入 '+r.recent_series.length+' 天日序（真源序列）');
    }else{
      say('当前无持久化 regime 日序——'+String(r.reason||'真源缺位')+'；7 态词表：'+words);
    }
  }).catch(function(){ say('拉取失败（面板 API 未启动?）——日序仍可手贴 JSON'); });
}
function btVerdictUseCurrent(){
  var inp=document.getElementById('bt-verdict-run');
  if(inp&&typeof BT_STATE!=='undefined'&&BT_STATE.run) inp.value=BT_STATE.run;
  btVerdictLoad();
}
function btVerdictLoad(){
  var inp=document.getElementById('bt-verdict-run');
  var body=document.getElementById('bt-verdict-body');
  if(!inp||!body) return;
  var rid=(inp.value||'').trim();
  function esc(s){ return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];}); }
  if(!rid){ body.innerHTML='<div class="dim" style="padding:6px 0;font-size:12px">请先填 run_id（左屏 Runs 下拉选中后可点「用当前 run」）</div>'; return; }
  if(!(window.ZK&&ZK.api)){ body.innerHTML='<div class="dim">API 通道未就绪（services/api.js 未加载）</div>'; return; }
  body.innerHTML='<div class="dim" style="padding:6px 0;font-size:12px">查询中…</div>';
  ZK.api.fetchJson('/api/tdm/verdicts?run_id='+encodeURIComponent(rid),10000).then(function(r){
    if(!r||!r.ok){ body.innerHTML='<div class="dim" style="padding:6px 0;font-size:12px;color:var(--down)">台账不可达：'+esc((r&&r.reason)||'API 响应异常')+'（显式降级，不冒充"未验证"）</div>'; return; }
    var recs=r.records||[];
    if(!recs.length){ body.innerHTML='<div class="dim" style="padding:6px 0;font-size:12px">该 run 无验证台账行——verdict=untested（未验证态，非故障）</div>'; return; }
    var html='<table><tr><th>节点</th><th>验证窗口</th><th>方法</th><th>触发</th><th>命中率</th><th>显著性</th><th>判定</th><th>判定时刻</th></tr>';
    recs.forEach(function(x){
      html+='<tr><td>'+esc(x.node_id)+'</td><td>'+esc(x.window_start)+' ~ '+esc(x.window_end)+'</td><td>'+esc(x.validation_method)+'</td>'
        +'<td>'+esc(x.triggers)+'</td><td>'+(x.hit_ratio==null?'—':(Number(x.hit_ratio)*100).toFixed(1)+'%')+'</td><td>'+esc(x.significance)+'</td>'
        +'<td><b>'+esc(x.verdict)+'</b></td><td class="dim">'+esc(x.verdict_at)+'</td></tr>';
    });
    html+='</table><div class="dim" style="font-size:11px;margin-top:4px">当前判定：'+esc(r.verdict)+' · 共 '+recs.length+' 行（snapshot_commit '+(esc(recs[0].snapshot_commit)||'—')+'）</div>';
    body.innerHTML=html;
  }).catch(function(){ body.innerHTML='<div class="dim" style="padding:6px 0;font-size:12px;color:var(--down)">查询失败（面板 API 未启动?）</div>'; });
}
