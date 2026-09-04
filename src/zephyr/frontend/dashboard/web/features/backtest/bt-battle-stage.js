/* 功能模块：策略所处环节（bt-battle-stage）
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 数据源：api:/api/battle-map-flow（作战地图阶段树，BattleMapReader 真源）
 *         + BT_STRATEGY_META[sid].battle_map_ref（策略环节归属声明，/api/strategies 透传）
 *         + BT_STRATEGY_META[sid].modes（可回测撮合模式，tick_only 推导）
 * 验收单：ACC-F-BACKTEST-BATTLE-STAGE
 * Owner 2026-09-04 一期（交易策略地图：直观看到策略处于作战地图哪个环节+能回测哪些撮合模式）
 */
(function(){
  function injectStyles(){
    if(document.getElementById('bt-battle-stage-style'))return;
    var st=document.createElement('style');st.id='bt-battle-stage-style';
    st.textContent=[
      '.bts-flow{display:flex;gap:4px;align-items:stretch;flex-wrap:wrap}',
      '.bts-stage{flex:1 1 0;min-width:74px;background:var(--input);border:1px solid var(--border);border-radius:5px;padding:6px 4px;text-align:center;position:relative}',
      '.bts-stage .bts-nm{font-size:11px;color:var(--dim)}',
      '.bts-stage .bts-cnt{font-size:10px;color:var(--faint);margin-top:2px}',
      '.bts-stage.on{border-color:var(--text);background:rgba(61,139,255,.12)}',
      '.bts-stage.on .bts-nm{color:var(--text);font-weight:600}',
      '.bts-arrow{align-self:center;color:var(--faint);font-size:10px}',
      '.bts-step{margin-top:8px;font-size:12px;padding:6px 10px;background:var(--panel2);border:1px solid var(--hair);border-radius:5px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}',
      '.bts-modes{display:flex;gap:6px;align-items:center;margin-top:8px;font-size:11px}'
    ].join('');
    document.head.appendChild(st);
  }
  var MODE_ZH={vectorized:'日频向量化',minute:'分钟级',tick:'Tick 完全仿真'};
  var mod={
    id:'bt-battle-stage',
    chart:null,
    _flow:null,   /* 阶段树缓存 [{flow_stage,name_zh,steps:[{step_id,step_name,maturity}]}] */
    init:function(chart,ctx){ this.chart=chart; injectStyles(); },
    _loadFlow:function(){
      var self=this;
      if(!window.ZK||!ZK.api)return;
      ZK.api.fetchBattleMapFlow().then(function(r){
        if(r&&r.ok&&r.data){ self._flow=r.data; self.render(); }
        else{ self._fail('后端不可达'); }
      }).catch(function(){ self._fail('断线·演示禁用'); });   /* 演示诚实纪律：失败红灯不造数据 */
    },
    _fail:function(msg){
      var box=document.getElementById('bt-battle-stage-body');
      if(box)box.innerHTML='<div class="dim" style="padding:6px 0">作战地图加载失败（'+msg+'）——15s 后自动重试</div>';
      var self=this;
      setTimeout(function(){ self._loadFlow(); },15000);   /* 15s 自动重试至真源（TRAE-086 §truth_source_wiring） */
    },
    render:function(d){
      var box=document.getElementById('bt-battle-stage-body');
      if(!box)return;
      var sid=(window.BTR_CFG&&BTR_CFG.strategies[0])||null;
      var meta=(window.BT_STRATEGY_META&&BT_STRATEGY_META[sid])||{};
      var ref=meta.battle_map_ref||null;
      if(!this._flow){ box.innerHTML='<div class="dim" style="padding:6px 0">加载中…</div>'; this._loadFlow(); return; }
      /* 定位环节：ref → step → 所属阶段 */
      var hitStage=null,hitStep=null;
      if(ref){
        this._flow.forEach(function(st){
          (st.steps||[]).forEach(function(sp){
            if(sp.step_id===ref){ hitStage=st; hitStep=sp; }
          });
        });
      }
      /* 11 阶段横向流程条 */
      var h='<div class="bts-flow">';
      this._flow.forEach(function(st,i){
        var on=hitStage&&hitStage.flow_stage===st.flow_stage;
        if(i>0)h+='<span class="bts-arrow">▶</span>';
        h+='<div class="bts-stage'+(on?' on':'')+'" title="'+st.flow_stage+'（'+(st.steps||[]).length+' 环节）">'
          +'<div class="bts-nm">'+st.name_zh+'</div><div class="bts-cnt">'+(st.steps||[]).length+'</div></div>';
      });
      h+='</div>';
      /* 环节定位详情 */
      if(ref&&hitStep){
        h+='<div class="bts-step"><span class="badge b-pass">'+hitStep.step_id+'</span>'
          +'<b>'+hitStep.step_name+'</b>'
          +'<span class="dim">所属阶段：'+(hitStage?hitStage.name_zh:ref)+'</span>'
          +'<span class="badge '+(hitStep.maturity==='production'?'b-pass':'b-warn')+'">'+(hitStep.maturity==='production'?'运营态':'设计态')+'</span></div>';
      }else{
        h+='<div class="bts-step"><span class="badge b-na">待定位</span><span class="dim">该策略未声明作战地图环节（StrategyMeta.battle_map_ref 为空）——策略类补声明后自动显示</span></div>';
      }
      /* 可回测撮合模式（tick_only 推导真源，/api/strategies modes 字段） */
      var modes=meta.modes||[];
      h+='<div class="bts-modes"><span class="dim">可回测撮合模式：</span>';
      if(modes.length){
        modes.forEach(function(m){
          var tick=m==='tick';
          h+='<span class="badge '+(tick?'b-warn':'b-pass')+'">'+(MODE_ZH[m]||m)+'</span>';
        });
      }else{
        h+='<span class="dim">未知（策略元数据缺失）</span>';
      }
      h+='</div>';
      box.innerHTML=h;
    },
    destroy:function(){
      var st=document.getElementById('bt-battle-stage-style');
      if(st)st.remove();
    }
  };
  if(window.ZK&&ZK.registerFeature){ ZK.registerFeature(mod); }
  else{ window.ZK=window.ZK||{}; ZK._pendingFeatures=ZK._pendingFeatures||[]; ZK._pendingFeatures.push(mod); }
  injectStyles();   /* 加载即注入（ACC 复盘：init 无人调——registerFeature 只登记不初始化，样式必须在文件顶层注入） */
  /* 竞态兜底：宿主 backtest.js 已载入且页面已注入 → 主动首渲染 */
  if(typeof btRenderStage!=='undefined'&&document.getElementById('bt-battle-stage-body')){ mod.render(); }
})();
/* 宿主联动入口：backtest.js btGridSel/btLoadStratGrid 调 btRenderStage() */
window.btRenderStage=function(){
  if(window.ZK&&ZK.features&&ZK.features['bt-battle-stage'])ZK.features['bt-battle-stage'].render();
};
