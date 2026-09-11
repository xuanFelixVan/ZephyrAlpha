/* 功能模块：全球市场排名榜（ov-rank）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：确定性模拟数据演示版式（待接入标记）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L3625-3669），逻辑零改动。
 * 验收单：ACC-F-OV-RANK
 */
/* ---- 全球市场排名榜：数据驱动自动排序（涨跌幅降序，待接入垫底不排；涨幅前三↑/跌幅前三↓标注） ---- */
(function ovxRank(){
  var M=[
    {n:'科创综指',c:'000680.SH',px:'986.12',chg:1.48,seed:4404},
    {n:'深证成指',c:'399001.SZ',px:'9,741.20',chg:1.05,seed:4202},
    {n:'比特币 BTC',c:'24/7',px:'85,062',chg:1.24,seed:4801},
    {n:'上证指数',c:'000001.SH',px:'3,087.53',chg:0.72,seed:4101},
    {n:'纳斯达克',c:'NDX · 昨收',px:'18,245.60',chg:0.61,seed:4606},
    {n:'标普500',c:'SPX · 昨收',px:'5,612.34',chg:0.38,seed:4505},
    {n:'创业板指',c:'399006.SZ',px:'1,892.44',chg:-0.31,seed:4303},
    {n:'恒生指数',c:'HSI',px:'17,890.22',chg:-0.42,seed:4707},
    {n:'以太坊 ETH',c:'24/7',px:'3,128.40',chg:-0.83,seed:4902},
    {n:'日经 225',c:'N225',na:1},
    {n:'韩国 KOSPI',c:'KS11',na:1},
    {n:'A股股指期货 IF',c:'IF2509',na:1},
    {n:'美股股指期货 ES',c:'CME · 盘前',na:1},
    {n:'黄金 COMEX',c:'GC',na:1},
    {n:'WTI 原油',c:'CL',na:1}
  ];
  M.sort(function(a,b){return (b.chg===undefined?-999:b.chg)-(a.chg===undefined?-999:a.chg);});
  var chgN=M.filter(function(m){return m.chg!==undefined;}).length;
  var h='<tr><th style="width:20px">#</th><th>市场</th><th style="text-align:right">最新</th><th style="text-align:right">涨跌幅</th><th style="width:104px">近 30 日</th></tr>';
  M.forEach(function(m,i){
    var tag='';
    if(m.chg!==undefined){
      if(i<3) tag=' <span style="color:var(--up);font-size:10px;font-weight:600">↑'+(i+1)+'</span>';
      else if(i>=chgN-3) tag=' <span style="color:var(--down);font-size:10px;font-weight:600">↓'+(chgN-i)+'</span>';
    }
    h+='<tr><td class="dim">'+(i+1)+'</td><td>'+m.n+' <span class="dim" style="font-size:11px">'+m.c+'</span>'+tag+'</td>';
    if(m.na){
      h+='<td style="text-align:right"><span class="badge b-na">待接入</span></td><td style="text-align:right" class="dim">—</td><td></td>';
    }else{
      var up=m.chg>=0;
      h+='<td style="text-align:right">'+m.px+'</td><td style="text-align:right" class="'+(up?'up':'down')+'">'+(up?'+':'')+m.chg.toFixed(2)+'%</td>'
        +'<td><svg class="spark" id="ovx-rk-'+i+'" viewBox="0 0 100 32" preserveAspectRatio="none" style="width:100px;height:32px"></svg></td>';
    }
    h+='</tr>';
  });
  var tb=document.getElementById('ovx-rank'); if(!tb) return;
  tb.innerHTML=h;
  M.forEach(function(m,i){
    if(m.na) return;
    drawLine('ovx-rk-'+i, genCandles(m.seed).map(function(k){return k.c;}), m.chg>=0?'#CA3F64':'#25A750', 100, 32);
  });
})();
