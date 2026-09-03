/* ZephyrAlpha 桌面壳（Electron main 进程）
 * 背景：浏览器访问 8891 反复出现"改了看不到"（用户侧缓存/环境黑盒，2026-09-01 三轮排查未定位）——
 *       Owner 裁定前端桌面化（Electron），自带 Chromium 环境 100% 可控。
 * 模式：
 *   生产（默认）：静态文件经 app:// 自定义协议直读磁盘（无 HTTP 缓存语义）+ 自动拉起/复用 8890 API
 *   开发（--dev）：窗口指向 http://127.0.0.1:8891（热更新工作流不变），不拉起 API
 * 路径约定：本目录=tools/desktop/（根目录白名单内；src/zephyr 为 Python 包根禁 .json），
 *           web 根=<仓库根>/src/zephyr/frontend/dashboard/web/，仓库根=上两级
 */
const { app, BrowserWindow, protocol, net, dialog } = require('electron');
const { pathToFileURL } = require('url');
const { spawn } = require('child_process');
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
// API 拉起日志（2026-09-03 实证：stdio ignore 时拉起失败零痕迹，用户只见断线白屏无从排查）
const API_LOG = path.join(REPO_ROOT, 'data', 'runtime', 'api_server_desktop.log');

/* app:// 需注册为特权 scheme（standard 才支持相对路径解析；supportFetchAPI 才能 fetch 页面片段） */
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { standard: true, secure: true, supportFetchAPI: true, stream: true } },
]);

let apiProc = null;
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

async function ensureApi() {
  if (await apiAlive()) return;   // 已有实例（如开发中手动起的）→ 复用不重复拉起
  spawnApi();
  let retried = false;
  // 健康等待（最多 20s；CH 连接首建可能偏慢）
  for (let i = 0; i < 40; i++) {
    await new Promise((r) => setTimeout(r, 500));
    if (await apiAlive()) return;
    // 秒退重试一次（瞬态失败：端口刚释放/启动竞态——2026-09-03 实证需要）
    if (!retried && apiProc && apiProc.exitCode !== null) {
      retried = true;
      spawnApi();
    }
  }
  dialog.showErrorBox(
    'ZephyrAlpha 面板 API 未能启动',
    '点击图标后 20 秒内 API（127.0.0.1:8890）未就绪，页面将以断线·演示态渲染。\n\n' +
    '启动日志：' + API_LOG + '\n（排查：日志末尾看 python 报错；确认 8890 端口是否被占用）'
  );
}

function killApi() {
  if (apiProc && !apiProc.killed) {
    try { apiProc.kill(); } catch { /* already dead */ }
    apiProc = null;
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
    // 生产模式：app:// 直读磁盘，无缓存语义
    win.loadURL('app://index.html');
  }
  win.on('closed', () => { win = null; });
}

if (gotLock) {
  app.whenReady().then(async () => {
    registerAppProtocol();
    if (!IS_DEV) await ensureApi();   // 生产模式托管 API；开发模式由外部服务自理
    createWindow();
    app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
  });

  app.on('window-all-closed', () => {
    killApi();
    app.quit();
  });
  app.on('before-quit', killApi);
}
