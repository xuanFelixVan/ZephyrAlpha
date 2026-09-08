/* ── 公司详情卡（chainmap 二期 Commit A）· 真源 /api/chainmap-company ──
 * 打开：ZK.bus cm:open-company {symbol, name?}（环节公司面板行点击）；卡片自建 DOM 挂 #p-chainmap。
 * 行情段独立降级：quote=null → '—'（CH 失败不拖垮图谱段）；市值=最新总股本(周更)×收盘 估算，标"约"。
 * 关系按来源分组：supply=供应（483/名录/websearch 有方向：from=供应商→to=客户），collab=合作
 * （J88 专利边无方向——Owner 红线禁臆断箭头）；对手方未上市（symbol=''）以名称展示。
 * 跳个股=go('stockq')+sqSel(裸码)（一期 go+setTimeout 先例）；断线 15s 自动重试（演示诚实纪律）。
 * 跨链徽章=Commit B（F-CHAINMAP-CROSS-LINK）。验收单：ACC-F-CHAINMAP-COMPANY-CARD */
(function () {
  'use strict';
  var opened = null;      /* 当前卡 symbol（防旧响应覆盖新卡） */
  var hintName = '';      /* 事件携带的公司名（后端名称映射覆盖不全时兜底展示） */

  function pageEl() { return document.getElementById('p-chainmap'); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function injectStyles() {
    if (window.__CMCC_CSS) return;
    window.__CMCC_CSS = true;
    var st = document.createElement('style');
    st.textContent =
      '#cm-company-card{position:absolute;inset:0;z-index:920;display:flex;justify-content:flex-end}' +   /* z>ticker-bar(900)：打开时连底部行情条一起罩住，防其拦截 footer 点击 */
      '#cm-company-card::before{content:\'\';position:absolute;inset:0;background:rgba(4,8,14,.55)}' +
      '#cm-company-card .cc-panel{position:relative;width:500px;max-width:94%;background:#0d131d;' +
      'border-left:1px solid #263042;box-shadow:-12px 0 32px rgba(0,0,0,.45);overflow:auto;padding:16px;' +
      'font-size:12px;color:#dbe4f0}' +
      '#cm-company-card .cc-x{position:absolute;top:10px;right:14px;cursor:pointer;color:#7d8aa0;font-size:18px;line-height:1}' +
      '#cm-company-card .cc-x:hover{color:#dbe4f0}' +
      '#cm-company-card .cc-load,#cm-company-card .cc-bad,#cm-company-card .cc-empty{color:#7d8aa0;font-size:12px;padding:10px 0}' +
      '#cm-company-card .cc-bad{color:#CA3F64}' +
      '#cm-company-card .cc-head{margin:2px 0 10px;padding-right:24px}' +
      '#cm-company-card .cc-name{font-size:17px;font-weight:700;color:#dbe4f0}' +
      '#cm-company-card .cc-sym{margin-left:8px;color:#525d70;font-size:11px}' +
      '#cm-company-card .cc-quote{display:flex;flex-wrap:wrap;gap:8px 18px;padding:10px 12px;background:#111927;' +
      'border:1px solid #1d2736;border-radius:8px;margin-bottom:6px}' +
      '#cm-company-card .cc-q i{display:block;font-style:normal;font-size:9.5px;color:#525d70;letter-spacing:1px;margin-bottom:2px}' +
      '#cm-company-card .cc-q{font-size:13px;font-weight:700;color:#dbe4f0}' +
      '#cm-company-card .cc-up{color:#e05d5d}#cm-company-card .cc-down{color:#45b47c}#cm-company-card .cc-dim{color:#7d8aa0;font-weight:400}' +
      '#cm-company-card .cc-qd{flex-basis:100%;font-size:10px;color:#525d70}' +
      '#cm-company-card .cc-sec{margin-top:14px}' +
      '#cm-company-card .cc-st{font-size:11px;font-weight:700;color:#7d8aa0;letter-spacing:1px;margin-bottom:4px}' +
      '#cm-company-card .cc-more{font-weight:400;color:#525d70;margin-left:8px}' +
      '#cm-company-card .cc-row{display:flex;align-items:baseline;gap:7px;padding:4px 6px;border-radius:6px}' +
      '#cm-company-card .cc-row:hover{background:#131a26}' +
      '#cm-company-card .cc-chain{flex:none;max-width:38%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#7db4e8}' +
      '#cm-company-card .cc-node{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#b9c4d6}' +
      '#cm-company-card .cc-role{flex:none;margin-left:auto;font-size:9.5px;padding:1.5px 6px;border-radius:99px;' +
      'border:1px solid #263042;color:#8a94a6}' +
      '#cm-company-card .cc-rn{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#dbe4f0}' +
      '#cm-company-card .cc-rs{flex:none;color:#525d70;font-size:10.5px}' +
      '#cm-company-card .cc-rm{flex:none;max-width:46%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#525d70;font-size:10.5px}' +
      '#cm-company-card .cc-row[data-chain]:hover .cc-role{color:#e6c34c;border-color:#8a6d1f}' +
      '#cm-company-card .cc-foot{margin-top:18px;display:flex;align-items:center;gap:10px}' +
      '#cm-company-card .cc-jump{cursor:pointer;background:#e6c34c;color:#0d131d;font-weight:700;padding:6px 14px;' +
      'border-radius:6px;font-size:12px}' +
      '#cm-company-card .cc-jump:hover{background:#f0d36a}' +
      '#cm-company-card .cc-note{font-size:10px;color:#525d70;line-height:1.5}';
    document.head.appendChild(st);
  }

  function close() {
    var card = document.getElementById('cm-company-card');
    if (card) card.parentNode.removeChild(card);
    opened = null;
  }

  function fmtPct(p) {
    if (p == null) return '<span class="cc-dim">—</span>';
    var cls = p > 0 ? 'cc-up' : (p < 0 ? 'cc-down' : 'cc-dim');
    return '<span class="' + cls + '">' + (p > 0 ? '+' : '') + p.toFixed(2) + '%</span>';
  }

  function srcTag(s) {
    if (s === 'J88_collab_patent') return '专利合作';
    if (s === '483_top5_customer') return '前五大客户披露';
    if (s === 'match_list_2012_2023') return '供应名录';
    if (s === 'websearch') return '网络检索';
    return esc(s || '');
  }

  function sec(title, total, arr, rowFn) {
    var list = arr || [];
    var body = list.map(rowFn).join('');
    if (!body) body = '<div class="cc-empty">暂无数据</div>';
    var more = total > list.length ? '<span class="cc-more">共 ' + total + ' 条，展示前 ' + list.length + '</span>' : '';
    return '<div class="cc-sec"><div class="cc-st">' + title + more + '</div>' + body + '</div>';
  }

  function posRow(p) {
    return '<div class="cc-row" data-chain="' + esc(p.chain_id) + '" data-cluster="' + esc(p.cluster) + '" ' +
      'data-chain-name="' + esc(p.chain_name) + '" data-node="' + esc(p.node_id) + '" title="跳转到该链（跨链跳转）" style="cursor:pointer">' +
      '<span class="cc-chain" title="' + esc(p.chain_name) + '">' + esc(p.chain_name) + '</span>' +
      '<span class="cc-node" title="' + esc(p.node_name) + '">' + esc(p.node_name) + '</span>' +
      '<span class="cc-role">' + esc(p.role || '提及') + '</span></div>';
  }

  function relRow(r) {
    var nm = r.name || (r.symbol || (r.unlisted ? '未上市对手方' : '—'));
    var meta = [];
    if (r.product) meta.push(esc(r.product));
    if (r.year) meta.push(r.year + '年');
    if (r.weight != null && r.weight_type === 'sales_pct') meta.push('销售额占比 ' + r.weight + '%');
    if (r.source) meta.push(srcTag(r.source));
    return '<div class="cc-row"><span class="cc-rn" title="' + esc(nm) + '">' + esc(nm) + '</span>' +
      '<span class="cc-rs">' + esc(r.symbol || '未上市') + '</span>' +
      '<span class="cc-rm">' + (meta.join(' · ') || '&nbsp;') + '</span></div>';
  }

  function render(card, d) {
    var q = d.quote || {};
    var co = d.company || {};
    var name = co.name || hintName || co.symbol || opened;
    var bare = String(co.symbol || opened).split('.')[0];
    card.querySelector('.cc-panel').innerHTML =
      '<span class="cc-x" title="关闭">×</span>' +
      '<div class="cc-head"><span class="cc-name">' + esc(name) + '</span>' +
      '<span class="cc-sym">' + esc(co.symbol || '') + '</span></div>' +
      '<div class="cc-quote">' +
      '<span class="cc-q"><i>收盘</i>' + (q.close != null ? q.close : '—') + '</span>' +
      '<span class="cc-q"><i>涨跌幅</i>' + fmtPct(q.pct_change) + '</span>' +
      '<span class="cc-q"><i>总市值</i>' + (q.total_mv_yi != null ? '约 ' + q.total_mv_yi + ' 亿' : '<span class="cc-dim">—</span>') + '</span>' +
      '<span class="cc-q"><i>PE(TTM)</i>' + (q.pe_ttm != null ? q.pe_ttm : '<span class="cc-dim">—</span>') + '</span>' +
      '<span class="cc-q"><i>PB</i>' + (q.pb_mrq != null ? q.pb_mrq : '<span class="cc-dim">—</span>') + '</span>' +
      '<span class="cc-qd">' + (q.trade_date ? '行情 ' + q.trade_date : '行情断线') +
      (q.valuation_asof ? ' · 估值 ' + q.valuation_asof : '') + '（总市值为估算值）</span>' +
      '</div>' +
      sec('链上落位（链 · 环节 · 角色）', d.total_placements || 0, d.placements, posRow) +
      sec('供应商（上游 → 本司）', d.n_suppliers || 0, d.suppliers, relRow) +
      sec('客户（本司 → 下游）', d.n_customers || 0, d.customers, relRow) +
      sec('合作（专利共同研发，无方向）', d.n_collabs || 0, d.collabs, relRow) +
      '<div class="cc-foot"><span class="cc-jump">在个股页打开 →</span>' +
      '<span class="cc-note">市值=最新总股本×收盘（估算）；关系方向按来源标注，专利合作边无方向。</span></div>';
    var x = card.querySelector('.cc-x');
    if (x) x.addEventListener('click', close);
    Array.prototype.forEach.call(card.querySelectorAll('.cc-row[data-chain]'), function (el) {
      el.addEventListener('click', function () {
        close();
        ZK.bus.emit('cm:view', { view: 'cluster' });
        ZK.bus.emit('cm:open-cluster', { cid: el.getAttribute('data-cluster'), name: el.getAttribute('data-chain-name') });
        ZK.bus.emit('cm:goto-chain', { chain_id: el.getAttribute('data-chain'), cluster: el.getAttribute('data-cluster'),
                                       chain_name: el.getAttribute('data-chain-name'), focus_node: el.getAttribute('data-node') });
      });
    });
    var jp = card.querySelector('.cc-jump');
    if (jp) jp.addEventListener('click', function () {
      close();
      go('stockq');
      setTimeout(function () { if (typeof sqSel === 'function') sqSel(bare); }, 80);
    });
  }

  function open(symbol, name) {
    if (!symbol) return;
    injectStyles();
    close();
    opened = symbol;
    hintName = name || '';
    var page = pageEl();
    if (!page) return;
    var card = document.createElement('div');
    card.id = 'cm-company-card';
    card.innerHTML = '<div class="cc-panel"><div class="cc-load">加载公司数据…</div></div>';
    card.addEventListener('click', function (e) { if (e.target === card) close(); });   /* 点遮罩关 */
    page.appendChild(card);
    ZK.api.fetchChainmapCompany(symbol).then(function (d) {
      if (opened !== symbol) return;   /* 已换卡/已关：丢弃旧响应 */
      if (!d.ok) {
        card.querySelector('.cc-panel').innerHTML =
          '<span class="cc-x" title="关闭">×</span><div class="cc-bad">加载失败：' + esc(d.error || '') + ' · 15s 后重试</div>';
        var x1 = card.querySelector('.cc-x');
        if (x1) x1.addEventListener('click', close);
        setTimeout(function () { if (opened === symbol) open(symbol, hintName); }, 15000);
        return;
      }
      render(card, d);
    }).catch(function (e) {
      if (opened !== symbol) return;
      card.querySelector('.cc-panel').innerHTML =
        '<span class="cc-x" title="关闭">×</span><div class="cc-bad">加载失败（' + esc((e && e.message) || 'fetch') + '）· 15s 后重试</div>';
      var x2 = card.querySelector('.cc-x');
      if (x2) x2.addEventListener('click', close);
      setTimeout(function () { if (opened === symbol) open(symbol, hintName); }, 15000);
    });
  }

  function onOpenCompany(d) { open(d && d.symbol, d && d.name); }

  ZK.bus.on('cm:open-company', onOpenCompany);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && opened) close(); });

  ZK.registerFeature({
    id: 'chainmap-company-card',
    init: function () { /* bus 常驻监听（文件级绑定），无页面初始化体 */ },
    render: function () { /* 无常驻渲染体 */ },
    destroy: function () { ZK.bus.off('cm:open-company', onOpenCompany); close(); }
  });
})();
