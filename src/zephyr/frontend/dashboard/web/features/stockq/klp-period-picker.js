/* 功能模块：周期选择弹层（klp-period-picker）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：纯前端交互（全量周期矩阵）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L6453-6510），逻辑零改动。
 * 验收单：ACC-F-STOCKQ-PERIOD-PICKER
 */
/* ==================== 周期选择弹层（v4.4 欧易式：全量矩阵 + 编辑主栏显示 + 数字键 1~9 快切） ==================== */
var klpTfEditing=false;
function klpTfPop(e){
  if(e) e.stopPropagation();
  var pop=document.getElementById('klp-tfpop'); if(!pop) return;
  if(pop.style.display==='block'){ pop.style.display='none'; return; }
  klpTfRenderGrid();
  pop.style.display='block';
  var r=e?e.target.getBoundingClientRect():null;
  pop.style.left=Math.max(8,Math.min(r?r.left-160:200,window.innerWidth-440))+'px';
  pop.style.top=((r?r.bottom:60)+6)+'px';
  setTimeout(function(){ document.addEventListener('click',klpTfPopClose,{once:true}); },0);
}
function klpTfPopClose(e){
  var pop=document.getElementById('klp-tfpop');
  if(!pop) return;
  if(e&&pop.contains(e.target)){ document.addEventListener('click',klpTfPopClose,{once:true}); return; }   /* 弹层内点击消耗 once 后重新武装 */
  pop.style.display='none';
  if(klpTfEditing){ klpTfEditing=false; }   /* 关闭时退出编辑态 */
}
function klpTfRenderGrid(){
  var g=document.getElementById('klp-tf-grid'); if(!g) return;
  g.innerHTML=KLP_ALL_TFS.map(function(t){
    var vis=klpTfVis.indexOf(t)>=0;
    return '<span class="tp-cell'+(t===sqTf?' on':'')+(klpTfEditing&&vis?' vis':'')+'" onclick="klpTfPick(\''+t+'\',event)">'
      +(klpTfEditing?'<i class="ck">'+(vis?'✓':'')+'</i>':'')+t+'</span>';
  }).join('');
  var ed=document.getElementById('klp-tf-edit'); if(ed) ed.classList.toggle('on',klpTfEditing);
}
function klpTfPick(t,e){
  if(e) e.stopPropagation();
  if(klpTfEditing){   /* 编辑模式：切换主栏显示集合 */
    var i=klpTfVis.indexOf(t);
    if(i>=0){ if(klpTfVis.length<=1){ sqToast('主栏至少保留 1 个周期'); return; } klpTfVis.splice(i,1); }
    else klpTfVis.push(t);
    try{localStorage.setItem('zk-klp-tfvis',JSON.stringify(klpTfVis));}catch(err){}
    klpTfRenderGrid(); sqRenderHead();
    return;
  }
  /* 正常模式：切换周期 */
  var pop=document.getElementById('klp-tfpop'); if(pop) pop.style.display='none';
  sqTfSet(t,null);
  sqRenderHead();
}
function klpTfEditMode(e){
  if(e) e.stopPropagation();
  klpTfEditing=!klpTfEditing;
  klpTfRenderGrid();
}
/* 数字键 1~9 快切主栏周期（仅 stockq 页激活且焦点不在输入框时） */
document.addEventListener('keydown',function(e){
  var pg=document.getElementById('p-stockq');
  if(!pg||!pg.classList.contains('active')) return;
  if(e.target&&(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA')) return;
  if(e.ctrlKey||e.altKey||e.metaKey) return;
  var n=parseInt(e.key,10);
  if(n>=1&&n<=9&&n<=klpTfVis.length){ sqTfSet(klpTfVis[n-1],null); sqRenderHead(); }
});
