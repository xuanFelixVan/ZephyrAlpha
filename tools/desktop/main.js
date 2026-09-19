/* ZephyrAlpha 桌面壳（Electron main 进程）
 * 背景：浏览器访问 8891 反复出现"改了看不到"（用户侧缓存/环境黑盒，2026-09-01 三轮排查未定位）——
 *       Owner 裁定前端桌面化（Electron），自带 Chromium 环境 100% 可控。
 * 模式：
 *   生产（默认）：入口 http://127.0.0.1:8890/（api_server StaticFiles 页面+数据一体，W6-2
 *                 2026-09-19）+ 自动拉起/复用 8890 API；load 失败回退 app:// 直读磁盘（断线·演示态）
 *   开发（--dev）：窗口指向 http://127.0.0.1:8891（热更新工作流不变），不拉起 API
 * 路径约定：本目录=tools/desktop/（根目录白名单内；src/zephyr 为 Python 包根禁 .json），
 *           web 根=<仓库根>/src/zephyr/frontend/dashboard/web/，仓库根=上两级
 */
const { app, BrowserWindow, protocol, net, dialog, shell } = require('electron');
const { pathToFileURL } = require('url');
const { spawn, execFile } = require('child_process');
const path = require('path');
const fs = require('fs');

// 单实例锁（2026-09-03）：重复点图标=聚焦已有窗口，不再开第二个实例
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (win) {
      if (win.isMinimized()) win.restore();
      win.focus();
    }
  });
}

// 首页主视觉视频带声自动播放（Owner 2026-09-01）：Chromium 默认禁无手势有声 autoplay，
// 桌面应用属可信环境，放开该策略（浏览器 8891 访问仍受限，前端有静音兜底）
app.commandLine.appendSwitch('autoplay-policy', 'no-user-gesture-required');

const IS_DEV = process.argv.includes('--dev');
const DESKTOP_DIR = __dirname;
const REPO_ROOT = path.resolve(DESKTOP_DIR, '..', '..');
const WEB_ROOT = path.join(REPO_ROOT, 'src', 'zephyr', 'frontend', 'dashboard', 'web');
const API_HEALTH = 'http://127.0.0.1:8890/api/health';
const API_PORT = 8890;
// API 拉起日志（2026-09-03 实证：stdio ignore 时拉起失败零痕迹，用户只见断线白屏无从排查）
const API_LOG = path.join(REPO_ROOT, 'data', 'runtime', 'api_server_desktop.log');

/* app:// 需注册为特权 scheme（standard 才支持相对路径解析；supportFetchAPI 才能 fetch 页面片段） */
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { standard: true, secure: true, supportFetchAPI: true, stream: true } },
]);

let apiProc = null;
let docsProc = null;
let win = null;

/* ── API 后端生命周期 ── */
async function apiAlive() {
  try {
    const r = await net.fetch(API_HEALTH, { signal: AbortSignal.timeout(1500) });
    return r.ok;
  } catch { return false; }
}

function spawnApi() {
  // 输出落盘（uvicorn log_level=warning 平时安静，拉起失败时这里是唯一现场）
  fs.mkdirSync(path.dirname(API_LOG), { recursive: true });
  const log = fs.openSync(API_LOG, 'a');
  fs.writeSync(log, `\n===== spawn ${new Date().toLocaleString()} =====\n`);
  apiProc = spawn('python', ['-m', 'zephyr.frontend.dashboard.api_server'], {
    cwd: REPO_ROOT,
    windowsHide: true,
    stdio: ['ignore', log, log],
  });
  apiProc.on('error', (e) => fs.writeSync(log, `[desktop] spawn error: ${e.message}\n`));
  apiProc.on('exit', (code) => fs.writeSync(log, `[desktop] API exited code=${code}\n`));
  return apiProc;
}

/* ── 僵尸端口占用：检测 + 一键提权修复（2026-09-09 实证：旧 API 卡死后占 8890 不响应，
 *    新 API bind 10048 秒退，面板静默进断线态，用户无从排查）── */

/* netstat 找出 LISTENING 在 port 上的 PID；无占用/netstat 失败返回 null（失败时落回原排查路径） */
function findPortPid(port) {
  return new Promise((resolve) => {
    execFile('netstat', ['-ano'], { windowsHide: true, timeout: 5000 }, (err, stdout) => {
      if (err) return resolve(null);
      const line = stdout.split('\n').find((l) => /LISTENING/i.test(l) && l.includes(`:${port} `));
      const pid = line ? parseInt(line.trim().split(/\s+/).pop(), 10) : NaN;
      resolve(Number.isInteger(pid) && pid > 0 ? pid : null);
    });
  });
}

/* 提权 taskkill（触发 UAC，用户点「是」生效；成败不信任返回码，以端口是否释放为准） */
function killElevated(pid) {
  return new Promise((resolve) => {
    const ps = spawn('powershell.exe', ['-NoProfile', '-Command',
      `Start-Process taskkill -ArgumentList '/PID ${pid} /F' -Verb RunAs -Wait`], { windowsHide: true });
    ps.on('exit', () => resolve());
    ps.on('error', () => resolve());
  });
}

async function waitApiReady() {
  for (let i = 0; i < 40; i++) {          // 最多 20s；CH 连接首建可能偏慢
    await new Promise((r) => setTimeout(r, 500));
    if (await apiAlive()) return true;
  }
  return false;
}

function apiFailBox() {
  dialog.showErrorBox(
    'ZephyrAlpha 面板 API 未能启动',
    '点击图标后 20 秒内 API（127.0.0.1:8890）未就绪，页面将以断线·演示态渲染。\n\n' +
    '启动日志：' + API_LOG + '\n（排查：日志末尾看 python 报错；确认 8890 端口是否被占用）'
  );
}

/* 端口被僵尸占用 → 明示弹窗 + 一键提权修复，替代静默断线态 */
async function offerZombieFix(pid) {
  const { response } = await dialog.showMessageBox({
    type: 'warning',
    title: '8890 端口被占用，API 无法启动',
    message: `端口 8890 被进程 PID ${pid} 占用，且健康检查无响应（疑似卡死的旧 API）`,
    detail: '新拉起的 API 绑定端口失败（10048），面板只能以断线·演示态渲染。\n\n' +
            '「提权修复并重试」会弹出 UAC 窗口请求管理员权限结束该进程，请点「是」；\n' +
            '若跳过，面板以断线态打开，结束占用进程后重启面板即可恢复。',
    buttons: ['提权修复并重试', '跳过，断线态打开'],
    defaultId: 0,
    cancelId: 1,
    noLink: true,
  });
  if (response !== 0) return;
  await killElevated(pid);
  if ((await findPortPid(API_PORT)) !== null) {
    dialog.showErrorBox(
      '提权修复未生效',
      `PID ${pid} 仍在占用 8890（UAC 被取消或权限不足）。\n` +
      `可手动在任务管理器结束该进程，或用管理员终端执行：taskkill /PID ${pid} /F`
    );
    return;
  }
  spawnApi();
  if (!(await waitApiReady())) apiFailBox();
}

async function ensureApi() {
  if (await apiAlive()) return;   // 已有实例（如开发中手动起的）→ 复用不重复拉起
  spawnApi();
  let retried = false;
  // 健康等待（最多 20s）
  for (let i = 0; i < 40; i++) {
    await new Promise((r) => setTimeout(r, 500));
    if (await apiAlive()) return;
    // 秒退先查端口：被他人占用=僵尸占口，重试无意义，直接走修复弹窗（2026-09-09 实证）
    if (apiProc && apiProc.exitCode !== null) {
      const pid = await findPortPid(API_PORT);
      if (pid) return offerZombieFix(pid);
      // 端口干净 → 瞬态失败（端口刚释放/启动竞态——2026-09-03 实证需要），重试一次
      if (!retried) { retried = true; spawnApi(); }
    }
  }
  apiFailBox();
}

function killApi() {
  if (apiProc && !apiProc.killed) {
    try { apiProc.kill(); } catch { /* already dead */ }
    apiProc = null;
  }
}

/* ── 本地文档服务生命周期（8765，Owner 2026-09-07 裁定：随面板自动拉起+总闸可管）──
 * 用途：架构图 MD 里的"可缩放 HTML 版"链接（http://localhost:8765/...）依赖此服务；
 * 与总闸"本地文档服务"开关同一进程语义（探活复用——总闸先起了就不重复拉）。
 * --no-regen 秒起（全量重生成 72 域文档太慢，按需 python scripts/serve_docs.py --regen-only 手动跑） */
const DOCS_HEALTH = 'http://127.0.0.1:8765/';
const DOCS_LOG = path.join(REPO_ROOT, 'data', 'runtime', 'docs_server_desktop.log');

async function docsAlive() {
  try {
    const r = await net.fetch(DOCS_HEALTH, { signal: AbortSignal.timeout(1500) });
    return r.ok;
  } catch { return false; }
}

function spawnDocs() {
  fs.mkdirSync(path.dirname(DOCS_LOG), { recursive: true });
  const log = fs.openSync(DOCS_LOG, 'a');
  fs.writeSync(log, `\n===== spawn ${new Date().toLocaleString()} =====\n`);
  docsProc = spawn('python', ['scripts/serve_docs.py', '--no-regen'], {
    cwd: REPO_ROOT,
    windowsHide: true,
    stdio: ['ignore', log, log],
  });
  docsProc.on('error', (e) => fs.writeSync(log, `[desktop] spawn error: ${e.message}\n`));
  docsProc.on('exit', (code) => fs.writeSync(log, `[desktop] docs exited code=${code}\n`));
  return docsProc;
}

async function ensureDocs() {
  if (await docsAlive()) return;   // 已有实例（总闸起的/手动起的）→ 复用
  spawnDocs();
  for (let i = 0; i < 12; i++) {   // 健康等待最多 6s（纯静态服务，起得快）
    await new Promise((r) => setTimeout(r, 500));
    if (await docsAlive()) return;
  }
  // 不弹窗打断面板启动——文档服务是锦上添花，失败留痕日志+总闸页可见红灯
  fs.appendFileSync(DOCS_LOG, `[desktop] docs not ready within 6s (总闸页可手动拉起)\n`);
}

function killDocs() {
  if (docsProc && !docsProc.killed) {
    try { docsProc.kill(); } catch { /* already dead */ }
    docsProc = null;
  }
}

/* ── app:// 静态文件服务（无缓存：每次请求直读磁盘，根治"改了看不到"） ── */
function registerAppProtocol() {
  protocol.handle('app', (request) => {
    const u = new URL(request.url);
    let rel = decodeURIComponent(u.pathname);
    if (rel === '/' || rel === '') rel = '/index.html';
    const filePath = path.normalize(path.join(WEB_ROOT, rel));
    // 路径穿越防护：必须仍在 WEB_ROOT 内
    if (!filePath.startsWith(path.normalize(WEB_ROOT))) {
      return new Response('forbidden', { status: 403 });
    }
    if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
      return new Response('not found: ' + rel, { status: 404 });
    }
    return net.fetch(pathToFileURL(filePath).toString());
  });
}

/* ── 窗口 ── */
function createWindow() {
  win = new BrowserWindow({
    width: 1600,
    height: 900,
    title: 'ZephyrAlpha',
    backgroundColor: '#101214',   // 深色底防白闪（与站点主题一致）
    autoHideMenuBar: true,
    icon: path.join(WEB_ROOT, 'assets', 'media', 'img', 'brand', 'zephyralpha-icon.ico'),
    // 黑色标题栏（Owner 2026-09-01 要求）：Window Controls Overlay——原生最小化/关闭按钮保留，
    // 栏色与页面顶栏（rgba(4,8,16,.55) 混深底）同色系无缝融合，高度=顶栏 46px
    titleBarStyle: 'hidden',
    titleBarOverlay: { color: '#0A0D14', symbolColor: '#EDEFF2', height: 46 },
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  // 外链拦截（Owner 2026-09-07）：页面里的 http(s) 链接（如 8765 架构图 HTML）交系统默认浏览器
  // 打开——否则 Electron 会在面板窗口内整页跳走，面板被顶掉
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https?:/i.test(url)) { shell.openExternal(url); return { action: 'deny' }; }
    return { action: 'allow' };
  });
  win.webContents.on('will-navigate', (e, url) => {
    // app:// 内部导航放行；http(s) 一律外部浏览器（含 <a href> 普通点击）
    if (/^https?:/i.test(url)) { e.preventDefault(); shell.openExternal(url); }
  });
  // WCO 配套：①顶栏可拖拽移动窗口（交互子元素豁免）②顶栏右侧元素避开原生窗口按钮区（~150px）
  win.webContents.on('did-finish-load', () => {
    win.webContents.insertCSS(
      '.topbar{-webkit-app-region:drag}' +
      '.topbar *{-webkit-app-region:no-drag}' +
      '.tb-right{margin-right:150px}'
    ).catch(() => {});
  });
  // 键盘刷新 F5 / Ctrl+R（Owner 2026-09-01 要求）：app:// 直读磁盘零缓存，重载即得最新代码；
  // hash 路由（#position 等）随 URL 保留——刷新后仍停留当前页面（与顶栏 ↻ 按钮同效）
  win.webContents.on('before-input-event', (e, input) => {
    if (input.type === 'keyDown' && !input.isAutoRepeat &&
        (input.key === 'F5' || (input.key.toLowerCase() === 'r' && (input.control || input.meta)))) {
      win.webContents.reload();
      e.preventDefault();
    }
  });
  if (IS_DEV) {
    // 开发模式：指向 8891 http.server（热更新工作流不变），彻底禁 HTTP 缓存
    win.loadURL('http://127.0.0.1:8891/index.html');
    win.webContents.session.clearCache().catch(() => {});
  } else {
    // 生产模式（W6-2，2026-09-19）：入口切 8890 单端口——api_server StaticFiles
    // 一体服务页面+数据（Owner 批准服务 2→1 故障面减半）；ensureApi 已先行保证
    // 8890 就绪。load 失败（API 挂死/被抢占）回退 app:// 直读磁盘——页面仍以
    // 断线·演示态渲染（保留既有产品行为：僵尸修复流「跳过，断线态打开」的前提）。
    win.loadURL('http://127.0.0.1:8890/').catch(() => {});
    win.webContents.on('did-fail-load', (_e, code, _desc, _url, isMainFrame) => {
      if (!isMainFrame || code === -3 /* ERR_ABORTED=主动导航打断，非真失败 */) return;
      if (win && !win.isDestroyed() && !win.webContents.getURL().startsWith('app://')) {
        win.loadURL('app://index.html').catch(() => {});
      }
    });
  }
  win.on('closed', () => { win = null; });
}

if (gotLock) {
  app.whenReady().then(async () => {
    registerAppProtocol();
    if (!IS_DEV) {
      await ensureApi();    // 生产模式托管 API；开发模式由外部服务自理
      ensureDocs();         // 文档服务（8765）随面板拉起——不 await，不阻断窗口出现
    }
    createWindow();
    app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
  });

  app.on('window-all-closed', () => {
    killApi();
    killDocs();
    app.quit();
  });
  app.on('before-quit', () => { killApi(); killDocs(); });
}
