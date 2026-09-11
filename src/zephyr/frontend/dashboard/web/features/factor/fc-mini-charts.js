/* 功能模块：factor 页迷你走势启动批（fc-mini-charts）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：确定性模拟（genCandles 种子）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L3588-3590），逻辑零改动。
 * 验收单：ACC-F-FACTOR-MINI-CHARTS
 */
/* A1/A8 默认曲线初始化（须待 N_BARS/genCandles 就绪后执行；sd-curve 已随策略档案并入回测页退役） */
drawLine('fc-nav',genCandles(2000).map(function(k){return k.c;}),'var(--up)',400,170);
drawLine('fc-ic',genCandles(3000).map(function(k){return k.c;}),'var(--accent)',400,110);
