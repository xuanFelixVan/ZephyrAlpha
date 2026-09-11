/* 功能模块：任务进度下钻（task-progress）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据 TASK_LIST
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L4723-4768），逻辑零改动。
 * 验收单：ACC-F-TASK-PROGRESS
 */
/* ==================== I-8 循环升级 R7：任务进度下钻/重跑/全量清单（taskXxx） ==================== */
function taskDrill(row,id){
  var b=document.getElementById(id); if(!b)return;
  var open=b.style.display==='none';
  b.style.display=open?'':'none';
  var c=row.cells[0]; c.textContent=c.textContent.replace(open?'▸':'▾',open?'▾':'▸');
}
function taskRerun(name,el){
  if(el.__busy)return;
  if(!confirm('human_gated 确认：重跑任务「'+name+'」？\n（演示——真实执行通道待接入 I-2；操作将留痕）'))return;
  el.__busy=1; var old=el.textContent; el.textContent='排队中…';
  setTimeout(function(){el.textContent='已触发(演示)';setTimeout(function(){el.textContent=old;el.__busy=0;},1500);},800);
}
var TASK_LIST=[
  ['kline_daily_incremental','数据采集','08-25 06:31','4m12s','g','成功'],
  ['tick_data_record','数据采集','实时常驻','—','g','运行中'],
  ['tick 回补 08-14','数据采集','08-19 06:40','12m','r','失败'],
  ['macro_fred_incremental','数据采集','08-24 21:05','1m48s','g','成功'],
  ['qweather_now_incremental','数据采集','08-25 08:00','22s','g','成功'],
  ['factor_alpha_pipeline','因子计算','08-25 06:45','18m','g','成功'],
  ['ic_ir_daily','因子计算','08-25 07:02','6m33s','g','成功'],
  ['ic_decay_watch','因子计算','08-22 07:10','3m05s','y','久未运行'],
  ['backfill_checker_daily','治理','08-25 06:35','9m','g','成功'],
  ['architecture_fitness','治理','08-25 06:50','2m40s','g','成功'],
  ['backup_daily_trigger','运维','08-25 02:00','14m','g','成功'],
  ['ch_health_probe','运维','常驻 5min','8s','g','成功']
];
var taskStage='all';
function taskListRender(){
  var q=(document.getElementById('task-q')||{}).value||''; q=q.trim().toLowerCase();
  var rows=TASK_LIST.filter(function(r){
    return (taskStage==='all'||r[1]===taskStage)&&(!q||r[0].toLowerCase().indexOf(q)>=0);
  });
  var h='<tr><th>任务</th><th>阶段</th><th>上次运行</th><th>耗时</th><th>状态</th></tr>';
  rows.forEach(function(r){
    var lamp=r[4]==='g'?'<span class="dot g"></span>':(r[4]==='y'?'<span class="dot y"></span>':'<span class="dot r"></span>');
    h+='<tr><td>'+r[0]+'</td><td>'+r[1]+'</td><td>'+r[2]+'</td><td>'+r[3]+'</td><td>'+lamp+' '+r[5]+'</td></tr>';
  });
  if(!rows.length) h+='<tr><td colspan="5" class="dim">无匹配任务</td></tr>';
  document.getElementById('task-list-body').innerHTML=h;
  document.getElementById('task-list-count').textContent=rows.length+' / 演示 12 行（全量 167 I-2）';
}
function taskStageSet(st,el){
  document.querySelectorAll('#task-stage-tabs .tab').forEach(function(t){t.classList.remove('on');});
  if(el)el.classList.add('on'); taskStage=st; taskListRender();
}
