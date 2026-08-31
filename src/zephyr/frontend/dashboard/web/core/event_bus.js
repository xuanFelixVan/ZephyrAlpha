/* 薄事件总线 + 功能模块注册表（模块契约基建，Owner 2026-08-31 裁定四件套之三）
 * 纪律：模块间只允许经 ZK.bus 交互，禁止跨模块直接改对方 DOM/状态（防散件重新缠成一坨）
 * 契约：模块=一个独立文件 features/<id>.js，经 ZK.registerFeature 注册，暴露 init(chart,ctx)/render(d)/destroy()
 */
window.ZK = window.ZK || {};
ZK.bus = (function(){
  var m = {};
  return {
    on: function(ev, fn){ (m[ev] = m[ev] || []).push(fn); },
    off: function(ev, fn){ if(m[ev]) m[ev] = m[ev].filter(function(f){ return f !== fn; }); },
    emit: function(ev, data){
      (m[ev] || []).forEach(function(f){
        try{ f(data); }catch(e){ console.error('[ZK.bus]', ev, e); }
      });
    }
  };
})();
ZK.features = ZK.features || {};
ZK.registerFeature = function(def){
  if(!def || !def.id){ console.error('[ZK] registerFeature: missing id'); return; }
  ZK.features[def.id] = def;
};
