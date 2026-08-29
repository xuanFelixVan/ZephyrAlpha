/* 长城任务四·批 2：作战指挥 8 态概率条 + 全景校验反馈 + 健康明细 */
(function(){
var d=document.getElementById('wr-8state');if(d){var rows=[['高开高走',24],['高开震荡',14],['平开高走',22],['平开震荡',18],['低开高走',9],['低开震荡',7],['低开低走',4],['极端',2]];rows.forEach(function(r){var b=document.createElement('div');b.style.cssText='flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:2px';var hgt=r[1]*2.4;b.innerHTML='<div style="font-size:10px;color:#EDEFF2">'+r[1]+'%</div><div style="width:100%;height:'+hgt+'px;background:'+(r[1]>=20?'#CA3F64':(r[1]>=10?'rgba(202,63,100,.45)':'rgba(139,148,158,.35)'))+';border-radius:2px"></div><div style="font-size:9px;color:#8B949E;white-space:nowrap">'+r[0]+'</div>';d.appendChild(b);});}
})();
function ovxVfy(btn,ok){
  var td=btn.parentElement;td.innerHTML=ok?'<span class="badge b-pass">✓ 已记录</span>':'<span class="badge b-fail">✗ 已记录</span>';
  (window.__fbQueue=window.__fbQueue||[]).push({t:Date.now(),kind:'ovx_vfy',ok:ok});
  if(typeof gToast==='function')gToast(ok?'✓ 校验一致，已记录':'✗ 校验不一致——样本已入纠错队列（后台日志）');
}
function ovxHealthTgl(a){var d=document.getElementById('ovx-health-d');if(!d)return;var on=d.style.display!=='none';d.style.display=on?'none':'block';a.textContent=on?'展开明细 ▾':'收起明细 ▴';}
