/* 功能模块：组合容忍带（tolerance-band）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据（real/paper 两档）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L4675-4689），逻辑零改动。
 * 验收单：ACC-F-POS-TOLERANCE-BAND
 */
function renderTolBand(key){
  var tb=document.getElementById('tol-band-body'); if(!tb)return;
  if(key&&key!=='real'){
    tb.innerHTML='<tr><td class="dim" colspan="4">'+(key==='sim'?'模拟账户口径（演示）':'分账户口径')+'——容忍带按账号输出后转真（I-2，负反馈）</td></tr>';
    return;
  }
  tb.innerHTML='<tr><th>检查项</th><th>政策基准/上限</th><th>当前</th><th>判定</th></tr>'
    +'<tr><td>单票偏离（贵州茅台）</td><td>目标 10% ±5pp</td><td>13.3%（+3.3pp）</td><td><span class="badge b-pass">带内</span></td></tr>'
    +'<tr><td>单票偏离（宁德时代）</td><td>目标 8% ±5pp</td><td>5.5%（-2.5pp）</td><td><span class="badge b-pass">带内</span></td></tr>'
    +'<tr><td>单票偏离（中芯国际）</td><td>目标 6% ±5pp</td><td>7.2%（+1.2pp）</td><td><span class="badge b-pass">带内</span></td></tr>'
    +'<tr><td>行业集中度（新能源）</td><td>≤25%</td><td>21.4%</td><td><span class="badge b-warn">接近上限</span></td></tr>'
    +'<tr><td>行业集中度（白酒）</td><td>≤25%</td><td>18.3%</td><td><span class="badge b-pass">带内</span></td></tr>'
    +'<tr><td>单票建仓硬顶</td><td>≤8% 总资产（firm 层）</td><td>今日新买最大 6.2%</td><td><span class="badge b-pass">未触顶</span></td></tr>'
    +'<tr><td colspan="4" class="dim">越限告警：0 次/近 5 日；触发后动作=告警+禁止加仓方向委托（联动 9 限额与禁做清单）</td></tr>';
}
