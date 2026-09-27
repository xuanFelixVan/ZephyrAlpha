/* 功能模块：L5 排产门闸页（schedulegate-page，L5 DESIGN C9）
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 自举：registerFeature 只登记不初始化（加载链竞态惯例，先例 promotion.js）——样式注入+首渲染
 *       在文件顶层做；全局入口 sgRefresh/sgConfirm 供页面 onclick 直绑
 * 数据源：GET  /api/schedulegate-queue   排产队列投影（score 排序+四读数+挂起态；只读）
 *         GET  /api/schedulegate-skeletons  骨架级提案包（利弊对照+两问打分展示；只读）
 *         POST /api/schedulegate-confirm    骨架级一键确认（confirm/reject）——★本页唯一写路由★
 * 写路由纪律（C9 验收）：确认按钮=唯一写路由；其余全只读；改判留痕（approve/reject 回执
 *         持久渲染在该卡，不删不改，复刻 promotion 拍板回执惯例）
 * 拍板交互：两段式确认（window.confirm，sv-page/promotion need_confirm 先例）；
 *           确认文案锚定语义「确认=工单转派工队列；驳回=工单作废归档（审计链留痕不删）」
 * 三态配色：pending=蓝 b-info / deferred|held=灰 b-na / dispatched=绿 b-pass / dead=红 b-fail
 *           （全站 badge 六族惯例）
 * 接线记录：api_server.py 三路由已挂（AI 层接线批）；services/api.js 三方法（fetchSchedulegateQueue/
 *         fetchSchedulegateSkeletons/postSchedulegateConfirm）+loader PAGES/feature 接线由 M6C1 批补齐（2026-09-25）；
 *         confirm 路由已接 ConfirmGate（回执卡按 ok 渲染；改判需带 allow_amend 的显式调用面，本路由恒 False）
 */
(function(){
  function injectStyles(){
    if(document.getElementById('sg-page-style'))return;
    var st=document.createElement('style');st.id='sg-page-style';
    st.textContent=[
      '.sg-card{margin-bottom:14px}',
      '.sg-head{display:flex;gap:10px;align-items:center;flex-wrap:wrap}',
      '.sg-evi{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;font-size:11px;color:var(--dim)}',
      '.sg-evi b{color:var(--text)}',
      '.sg-act{display:flex;gap:8px;align-items:center;margin-top:10px;padding-top:8px;border-top:1px solid var(--hair);flex-wrap:wrap}',
      '.sg-receipt{margin-top:8px;padding:8px 10px;background:var(--input);border:1px solid var(--hair);border-radius:5px;font-size:11px}',
      '.sg-quota{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;font-size:11px;color:var(--dim)}',
      '.sg-quota b{color:var(--text)}'
    ].join('');
    document.head.appendChild(st);
  }
  /* 状态三态 → 徽章（唯一映射表，禁散落 if） */
  var STATE_BADGE={
    pending:['b-info','待派工'],held_maturity:['b-na','成熟度挂起'],held_incomplete:['b-na','缺字段挂起'],
    dispatched:['b-pass','已派工'],deferred:['b-na','资源推迟'],done:['b-pass','已关单'],dead:['b-fail','已死单']};
  var EMPTY_TXT='暂无进化工单——L4 对比胜者过成熟度门闸后自动出现在这里';
  var LIST=null;        /* /api/schedulegate-queue 快照 */
  var SKELETONS=null;   /* /api/schedulegate-skeletons 快照 */
  var SG_TIMER=null;
  var SG_BUSY=false;    /* 拍板在途暂停轮询重绘（防 confirm 期间 DOM 被换） */

  function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
  function num(v,d){return (v==null||isNaN(Number(v)))?'—':Number(v).toFixed(d==null?2:d);}
  function stateBadge(st){
    var m=STATE_BADGE[st]||['b-na',st||'未知'];
    return '<span class="badge '+m[0]+'">'+esc(m[1])+'</span>';
  }
  /* 配额四读数横条（Q1-Q4；只读投影，超限红显） */
  function quotaHtml(q){
    if(!q)return '';
    function cell(k,label,v,cap,over){
      return '<span>'+label+' <b class="'+(over?'down':'')+'">'+esc(v)+'</b>/'+esc(cap)+'</span>';
    }
    return '<div class="sg-quota">'
      +cell('q1','并发槽',q.q1_active_sessions,q.q1_active_session_cap,q.q1_active_sessions>=q.q1_active_session_cap)
      +cell('q2','子代理',q.q2_subagents_requested,q.q2_subagent_max,q.q2_subagents_requested>q.q2_subagent_max)
      +cell('q3','当日 token',q.q3_tokens_today,q.q3_daily_token_budget,q.q3_tokens_today>=q.q3_daily_token_budget)
      +cell('q4','提交队列',q.q4_commit_queue_pending,q.q4_commit_queue_pending_cap,q.q4_commit_queue_pending>=q.q4_commit_queue_pending_cap)
      +'</div>';
  }
  function cardHtml(o,i){
    var h='<div class="card sg-card" id="sg-card-'+i+'">'
      +'<div class="sg-head"><b>'+esc(o.order_id)+'</b>'
      +stateBadge(o.state)
      +(o.starred?'<span class="badge b-warn">带星胜 win*</span>':'')
      +(o.owner_gate?'<span class="badge b-warn">骨架级·Owner 门</span>':'')
      +'<span class="dim" style="margin-left:auto;font-size:10px">score '+num(o.score)+' · '+esc(o.domain_id||'')+'</span></div>'
      +'<div class="sg-evi">'
      +'<span>人工段 <b>'+esc(o.labor_segments!=null?o.labor_segments:'—')+'</b></span>'
      +'<span>优势桶 <b>'+esc(o.advantage_bucket||'—')+'</b></span>'
      +'<span>defer 计数 <b>'+esc(o.defer_count!=null?o.defer_count:0)+'</b></span>'
      +(o.held_reason?'<span class="down">'+esc(o.held_reason)+'</span>':'')
      +'</div>';
    /* 改判留痕：拍板回执持久渲染（审计链留痕不删） */
    if(o.confirm_receipt){
      var r=o.confirm_receipt;
      var ok=r.decision==='confirm';
      h+='<div class="sg-receipt"><span class="badge '+(ok?'b-pass':'b-fail')+'">'+(ok?'已确认派工':'已驳回归档')+'</span> '
        +(r.decided_at?'<span class="dim">拍板于 '+esc(String(r.decided_at)).slice(0,19).replace('T',' ')+'</span> · ':'')
        +(r.reason?'<span class="dim">'+esc(r.reason)+'</span> · ':'')
        +'<span class="dim" style="word-break:break-all">留痕回执 '+esc(typeof r.receipt==='string'?r.receipt:JSON.stringify(r.receipt))+'</span></div>';
    }else if(o.owner_gate&&o.state==='pending'){
      h+='<div class="sg-act">'
        +'<span class="btn" style="color:var(--text)" onclick="sgConfirm('+i+',\'confirm\')">✓ 一键确认（转派工）</span>'
        +'<span class="btn" style="color:var(--up)" onclick="sgConfirm('+i+',\'reject\')">✗ 驳回（作废归档）</span>'
        +'<span class="dim" style="font-size:10px">骨架级工单=AI 提案+Owner 门位；确认后才进自动派工队列</span>'
        +'</div>';
    }
    return h+'</div>';
  }
  function render(){
    var box=document.getElementById('schedulegate-body');if(!box)return;
    if(!LIST){box.innerHTML='<div class="dim" style="padding:20px 0">加载中…</div>';return;}
    var q=(LIST&&LIST.quota)||null;
    var rows=(LIST&&LIST.orders)||[];
    var sk=(SKELETONS&&SKELETONS.orders)||[];
    if(!rows.length&&!sk.length){
      box.innerHTML='<div class="card" style="border-left:3px solid var(--hair);text-align:center;padding:26px 0;color:var(--dim)">'+EMPTY_TXT+'</div>';
      return;
    }
    var html=quotaHtml(q);
    /* 骨架级提案包在前（Owner 门位优先可见）；其余队列按服务端 score 排序原样投影 */
    html+=sk.map(cardHtml).join('');
    html+=rows.map(cardHtml).join('');
    box.innerHTML=html;
  }
  function load(){
    if(!window.ZK||!ZK.api)return;
    Promise.all&&Promise.all([
      ZK.api.fetchSchedulegateQueue?ZK.api.fetchSchedulegateQueue():Promise.resolve(null),
      ZK.api.fetchSchedulegateSkeletons?ZK.api.fetchSchedulegateSkeletons():Promise.resolve(null)
    ]).then(function(rs){
      LIST=rs[0]&&rs[0].data||{orders:[]};
      SKELETONS=rs[1]&&rs[1].data||{orders:[]};
      render();
      if(rs[0]&&rs[0].ok===false){
        var box=document.getElementById('schedulegate-body');
        if(box)box.innerHTML+='<div class="dim" style="font-size:10px;margin-top:-6px">队列 API 未就绪：'+esc(rs[0].error||'')+'</div>';
      }
    }).catch(function(e){
      var box=document.getElementById('schedulegate-body');
      if(box&&!box.innerHTML.trim()){
        box.innerHTML='<div class="card" style="border-left:3px solid var(--up)"><b style="color:var(--up)">⚠ API 拉取失败（'+esc(e&&e.message||e)+'）</b><div class="dim" style="font-size:11px;margin-top:4px">面板 API 未运行或超时——15 秒后自动重试</div></div>';
      }
      setTimeout(load,15000);   /* 15s 自动重试至真源（promotion 同款） */
    });
  }
  /* 拍板：两段式确认 → POST /api/schedulegate-confirm（唯一写路由）→ 成功局部刷新该卡 */
  function confirmOrder(i,decision){
    var source=(SKELETONS&&SKELETONS.orders&&SKELETONS.orders[i])||(LIST&&LIST.orders&&LIST.orders[i]);
    if(!source)return;
    var isCfm=decision==='confirm';
    var msg=(isCfm?'确认【'+source.order_id+'】转派工队列？':'确认驳回【'+source.order_id+'】？')
      +'\n域：'+(source.domain_id||'—')+' · score：'+num(source.score)
      +(isCfm?'\n\n确认=工单转派工队列（进自动派工）。':'\n\n驳回=工单作废归档（审计链留痕不删）。')
      +'\n拍板将服务端留痕回执。';
    if(!window.confirm(msg))return;
    SG_BUSY=true;
    var btn=document.getElementById('sg-card-'+i);
    if(btn)btn.querySelector('.sg-act').innerHTML='<span class="dim">拍板提交中…</span>';
    ZK.api.postSchedulegateConfirm(source.order_id,decision).then(function(r){
      SG_BUSY=false;
      if(r&&r.ok){
        source.confirm_receipt={decision:decision,message:r.message,receipt:r.receipt,decided_at:new Date().toISOString()};
        render();   /* 改判留痕：整卡转回执态 */
      }else{
        render();
        alert('拍板被拒：'+(r&&r.message||r&&r.error||'?'));
      }
    }).catch(function(e){
      SG_BUSY=false;
      render();
      alert('拍板请求失败：'+(e&&e.message||e));
    });
  }
  /* 全局入口（页面 onclick 直绑） */
  window.sgRefresh=function(){LIST=null;SKELETONS=null;render();load();};
  window.sgConfirm=confirmOrder;

  var mod={
    id:'schedulegate-page',
    chart:null,
    init:function(chart,ctx){this.chart=chart;injectStyles();},
    render:function(d){render();},
    destroy:function(){
      if(SG_TIMER){clearInterval(SG_TIMER);SG_TIMER=null;}
      var st=document.getElementById('sg-page-style');if(st)st.remove();
    }
  };
  if(window.ZK&&ZK.registerFeature){ZK.registerFeature(mod);}
  else{window.ZK=window.ZK||{};ZK._pendingFeatures=ZK._pendingFeatures||[];ZK._pendingFeatures.push(mod);}
  injectStyles();   /* 加载即注入（registerFeature 只登记不初始化惯例） */
  /* 自举：容器已注入即首拉+30s 轮询（拍板在途跳过；只读轮询，写动作唯一走 confirm 路由） */
  if(document.getElementById('schedulegate-body')){
    load();
    SG_TIMER=setInterval(function(){if(!SG_BUSY&&document.getElementById('schedulegate-body'))load();},30000);
  }
})();
