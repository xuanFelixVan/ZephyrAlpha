/* 功能模块：持仓成本线（模块契约 pilot）
 * 契约：init(chart,ctx)/render(d)/destroy()；样式自注入；经 ZK.registerFeature 注册
 * 手册：FEH-KLC-001（plainLine 纯横线模板，points 只传 {value}）、FEH-KLC-003（取值须在 K 线价格域内）
 * 验收单：ACC-F-STOCKQ-COSTLINE
 * 依赖声明（manifest）：klinecharts / klpChipCalc / lcg / sqCur（app1.js 全局，筹码峰同口径）
 */
(function(){
  function injectStyles(){
    if(document.getElementById('cost-line-styles')) return;
    var st = document.createElement('style');
    st.id = 'cost-line-styles';
    st.textContent = '.klp-cost-tip{position:fixed;z-index:980;display:none;background:#1A1C1E;border:1px solid #F0B90B;border-radius:4px;padding:4px 10px;font-size:11.5px;color:#F0B90B;pointer-events:none;white-space:nowrap}';
    document.head.appendChild(st);
  }
  function registerTemplate(){
    if(window.__plainLineRegistered) return;
    window.__plainLineRegistered = 1;
    klinecharts.registerOverlay({
      name:'plainLine',
      totalStep:1,
      needDefaultPointFigure:false,
      needDefaultXAxisFigure:false,
      needDefaultYAxisFigure:false,
      createPointFigures:function(o){
        var c = o.coordinates;
        if(!c || !c.length) return [];
        var y = c[0].y;
        return [{type:'line',attrs:{coordinates:[{x:0,y:y},{x:9999,y:y}]},
          styles:{color:o.styles?o.styles.line.color:'#F0B90B',style:o.styles?o.styles.line.style:'dashed',size:o.styles?o.styles.line.size:1.2}}];
      }
    });
  }
  function qty(){ var r = lcg(+sqCur*5+29); return Math.round((10000+r()*90000)/100)*100; }   /* 演示持仓数量（沿用原口径） */
  function tipShow(chart){
    var tip = document.getElementById('klp-cost-tip');
    if(!tip){ tip = document.createElement('div'); tip.id = 'klp-cost-tip'; tip.className = 'klp-cost-tip'; document.body.appendChild(tip); }
    var d = chart.getDataList();
    tip.innerHTML = '成本: ' + klpChipCalc(d, d.length-1).avgCost.toFixed(2) + '&ensp;数量: ' + qty();   /* 与黄色线同口径（筹码峰平均成本） */
    tip.style.display = 'block';
    if(!window.__klpCostTipBound){
      window.__klpCostTipBound = 1;
      document.addEventListener('mousemove', function(e){
        var t = document.getElementById('klp-cost-tip');
        if(t && t.style.display === 'block'){ t.style.left = (e.clientX+12)+'px'; t.style.top = (e.clientY-32)+'px'; }
      });
    }
  }
  function tipHide(){ var tip = document.getElementById('klp-cost-tip'); if(tip) tip.style.display = 'none'; }

  var mod = {
    id: 'cost-line',
    chart: null,
    init: function(chart, ctx){ this.chart = chart; registerTemplate(); injectStyles(); },
    _ensure: function(){
      /* 懒绑定自愈：宿主 sqInit 的挂载可能早于本模块加载（加载链竞态），首次 render 时若 chart 空则自取全局 klpChart 补 init（手册 FEH-KLC-005） */
      if(!this.chart && typeof klpChart !== 'undefined' && klpChart){ this.init(klpChart); }
      return !!this.chart;
    },
    render: function(d){
      if(!this._ensure()) return;
      var c = klpChipCalc(d, d.length-1);
      var self = this;
      this.chart.createOverlay({name:'plainLine', groupId:'cost', lock:true,
        points:[{value:c.avgCost}],
        styles:{line:{color:'#F0B90B', style:'dashed', size:1.2}},
        onMouseEnter:function(){ tipShow(self.chart); return true; },
        onMouseLeave:function(){ tipHide(); return true; }});
    },
    destroy: function(){
      if(this.chart){ this.chart.removeOverlay({groupId:'cost'}); }
      tipHide();
      var tip = document.getElementById('klp-cost-tip');
      if(tip && tip.parentNode) tip.parentNode.removeChild(tip);
    }
  };
  ZK.registerFeature(mod);
})();
