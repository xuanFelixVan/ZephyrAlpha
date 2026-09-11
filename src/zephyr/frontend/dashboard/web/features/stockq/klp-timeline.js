/* 功能模块：K 线时间轴（klp-timeline）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：周期自适应刻度+事件图标
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L6358-6452），逻辑零改动。
 * 验收单：ACC-F-STOCKQ-KLP-TIMELINE
 */
/* ==================== 时间轴模块（v4.5：K 线与指标栏之间；周期自适应刻度 + 事件圆形图标带数字 + 点击弹层 + 拖拽调高） ==================== */
function klpTimelineRender(){
  var track=document.getElementById('klp-tl-track'); if(!track||!klpChart) return;
  var evtRow=document.getElementById('klp-evtrow');
  var d=klpChart.getDataList?klpChart.getDataList():[];
  if(!d.length){ track.innerHTML=''; if(evtRow) evtRow.innerHTML=''; return; }
  var vr=klpChart.getVisibleRange?klpChart.getVisibleRange():null;
  var from=vr?Math.max(0,vr.from):0,to=vr?Math.min(d.length-1,vr.to):d.length-1;
  var per=klpPeriodMap[sqTf]||{type:'day'};
  var isMin=(per.type==='minute'||per.type==='hour');   /* 分钟/小时级显示时分，日/周/月显示日期 */
  var h='',he='',i;
  /* 日期刻度：可见范围均匀取 ~7 个 */
  var stepN=Math.max(1,Math.round((to-from)/7));
  for(i=from;i<=to;i+=stepN){
    var x=klpChart.convertToPixel({dataIndex:i},{paneId:'candle_pane'});
    if(!x) continue;
    var t=new Date(d[i].timestamp);
    var txt=isMin?(String(t.getHours()).padStart(2,'0')+':'+String(t.getMinutes()).padStart(2,'0')):(String(t.getMonth()+1).padStart(2,'0')+'-'+String(t.getDate()).padStart(2,'0'));
    h+='<span class="klp-tl-date" style="left:'+x.x+'px">'+txt+'</span>';
  }
  /* 事件圆形图标+数字：独立行（MACD 与时间轴之间，紧挨时间轴上方但不在轨道上；同日聚合；随 evt 标注开关）
     数据源 v2：sq-event-row 组件（CH.calendar_event 宏观真源）优先，未加载/断线回退演示 SQ_EVENTS */
  var evMap={};
  if(klpMarks.evt){
    var EVS=(window.ZK && ZK.features && ZK.features['sq-event-row'] && ZK.features['sq-event-row'].getEvents())||SQ_EVENTS;
    EVS.forEach(function(ev,idx){
      var bi=klpFindBar(d,ev.dt);
      if(bi<0||bi<from||bi>to) return;
      if(!evMap[bi]) evMap[bi]=[];
      evMap[bi].push(idx);
    });
  }
  Object.keys(evMap).forEach(function(bi){
    var x=klpChart.convertToPixel({dataIndex:+bi},{paneId:'candle_pane'});
    if(!x) return;
    var idxs=evMap[bi];
    he+='<span class="klp-tl-evt" style="left:'+x.x+'px" title="'+idxs.length+' 条重要信息，点击查看" onclick="klpTlEvtPop(\''+bi+'\',event)"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h12.5v13.5H6.75A2.75 2.75 0 0 1 4 15.75V5z"/><path d="M16.5 8h2.25A1.25 1.25 0 0 1 20 9.25V16a2.5 2.5 0 0 1-2.5 2.5h-1"/><line x1="7" y1="8.5" x2="13.5" y2="8.5"/><line x1="7" y1="11.5" x2="13.5" y2="11.5"/><line x1="7" y1="14.5" x2="10.5" y2="14.5"/></svg><i>'+idxs.length+'</i></span>';   /* 白色线条新闻图标（Owner 要求替换◎）；数字缩小贴紧跟在右侧 */
  });
  /* 未来事件簇（v2）：K 线末日之后的事件无柱可锚，右端钉"⚑ 未来 N"点击弹清单 */
  if(klpMarks.evt && window.ZK && ZK.features && ZK.features['sq-event-row']){
    var ups=ZK.features['sq-event-row'].getUpcoming();
    if(ups.length){
      he+='<span class="klp-tl-evt" style="right:10px;left:auto;position:absolute" title="未来 '+ups.length+' 条事件（K 线末日之后），点击查看" onclick="klpTlUpcomingPop(event)">⚑<i>'+ups.length+'</i></span>';
    }
  }
  track.innerHTML=h;
  if(evtRow) evtRow.innerHTML=he;
  window.__klpTlEvMap=evMap;   /* 弹层取数 */
}
function klpTlEvtPop(bi,e){
  if(e) e.stopPropagation();
  var idxs=(window.__klpTlEvMap||{})[bi]||[];
  if(!idxs.length) return;
  var pop=document.getElementById('sq-evtpop'); if(!pop) return;
  var d=klpChart.getDataList();
  var t=new Date(d[+bi].timestamp);
  var ds=t.getFullYear()+'/'+String(t.getMonth()+1).padStart(2,'0')+'/'+String(t.getDate()).padStart(2,'0');
  /* 数据源 v2：与 klpTimelineRender 同源（sq-event-row 真源优先，回退演示 SQ_EVENTS） */
  var EVS=(window.ZK && ZK.features && ZK.features['sq-event-row'] && ZK.features['sq-event-row'].getEvents())||SQ_EVENTS;
  var isLive=!!(window.ZK && ZK.features && ZK.features['sq-event-row'] && ZK.features['sq-event-row'].isLive());
  var h='<div class="tl-date">'+ds+(isLive?' <span style="font-size:10px;color:#25A750">● calendar_event 真源</span>':' <span style="font-size:10px;color:#CA3F64">● 断线·演示</span>')+'</div>';
  idxs.forEach(function(idx){
    var ev=EVS[idx];
    h+='<div class="tl-ev"><div class="tt">'+ev.ic+' '+ev.tt+'</div><div class="tm">'+(ev.dateISO||'2026/'+ev.dt)+'</div>'
      +'<div class="kv"><span>公布</span><b>'+ev.pub+'</b></div>'
      +'<div class="kv"><span>预期</span><b>'+ev.exp+'</b></div>'
      +'<div class="kv"><span>前值</span><b>'+ev.prev+'</b></div></div>';
  });
  h+='<div class="tl-foot" onclick="document.getElementById(\'sq-evtpop\').style.display=\'none\';klpTglMark(\'evt\',null);sqRenderHead();">⚙ 显示设置（点此关闭事件图标）</div>';
  pop.innerHTML=h;
  pop.style.left=Math.min((e?e.clientX:400)+10,window.innerWidth-360)+'px';
  pop.style.top=Math.max(50,Math.min((e?e.clientY:200)-100,window.innerHeight-380))+'px';
  pop.style.display='block';
  setTimeout(function(){ document.addEventListener('click',sqEvtPopClose,{once:true}); },0);
}
/* 未来事件弹窗（v2，Owner 2026-09-01 指令）：K 线末日之后的事件清单（日期+描述+值状态） */
function klpTlUpcomingPop(e){
  if(e) e.stopPropagation();
  var pop=document.getElementById('sq-evtpop'); if(!pop) return;
  var ups=(window.ZK && ZK.features && ZK.features['sq-event-row'] && ZK.features['sq-event-row'].getUpcoming())||[];
  if(!ups.length) return;
  var h='<div class="tl-date">未来事件（K 线末日之后） <span style="font-size:10px;color:#25A750">● calendar_event 真源</span></div>';
  ups.forEach(function(ev){
    h+='<div class="tl-ev"><div class="tt">'+ev.ic+' '+ev.tt+'</div><div class="tm">'+ev.dateISO+'</div>'
      +'<div class="kv"><span>公布</span><b>'+ev.pub+'</b></div>'
      +'<div class="kv"><span>预期</span><b>'+ev.exp+'</b></div>'
      +'<div class="kv"><span>前值</span><b>'+ev.prev+'</b></div></div>';
  });
  h+='<div class="tl-foot" onclick="document.getElementById(\'sq-evtpop\').style.display=\'none\';klpTglMark(\'evt\',null);sqRenderHead();">⚙ 显示设置（点此关闭事件图标）</div>';
  pop.innerHTML=h;
  pop.style.left=Math.min((e?e.clientX:600)+10,window.innerWidth-360)+'px';
  pop.style.top=Math.max(50,Math.min((e?e.clientY:200)-100,window.innerHeight-420))+'px';
  pop.style.display='block';
  setTimeout(function(){ document.addEventListener('click',sqEvtPopClose,{once:true}); },0);
}
