from __future__ import annotations

from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = 'devops-demo-secret'

STATE = {
    'network': {'ssid': 'CPE-5G', 'password': 'ChangeMe123', 'mode': 'dhcp'},
    'upgrade': {'last_filename': None, 'status': 'idle'},
}

BASE_TEMPLATE = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ title }}</title>
  <style>
    :root {
      --bg: #07111f;
      --bg-elevated: rgba(10, 23, 41, 0.78);
      --panel: rgba(14, 30, 54, 0.88);
      --panel-soft: rgba(22, 42, 72, 0.72);
      --line: rgba(148, 163, 184, 0.18);
      --text: #e5eefb;
      --muted: #94a3b8;
      --primary: #6ee7f9;
      --primary-strong: #38bdf8;
      --accent: #8b5cf6;
      --success: #34d399;
      --danger: #fb7185;
      --warning: #fbbf24;
      --shadow: 0 24px 80px rgba(2, 8, 23, 0.45);
      --radius-xl: 28px;
      --radius-lg: 20px;
      --radius-md: 14px;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Inter", "PingFang SC", "Microsoft YaHei", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 28%),
        radial-gradient(circle at top right, rgba(139, 92, 246, 0.18), transparent 30%),
        linear-gradient(160deg, #030712 0%, #07111f 45%, #0b1730 100%);
    }

    body::before,
    body::after {
      content: "";
      position: fixed;
      inset: auto;
      width: 320px;
      height: 320px;
      border-radius: 999px;
      filter: blur(72px);
      opacity: 0.35;
      pointer-events: none;
      z-index: 0;
    }

    body::before {
      top: 80px;
      left: -40px;
      background: rgba(56, 189, 248, 0.25);
    }

    body::after {
      right: -60px;
      bottom: 0;
      background: rgba(139, 92, 246, 0.24);
    }

    .page-shell {
      position: relative;
      z-index: 1;
      width: min(1180px, calc(100% - 40px));
      margin: 0 auto;
      padding: 32px 0 48px;
    }

    .hero {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 28px;
      padding: 22px 26px;
      border: 1px solid var(--line);
      border-radius: var(--radius-xl);
      background: rgba(7, 17, 31, 0.58);
      backdrop-filter: blur(20px);
      box-shadow: var(--shadow);
    }

    .hero h1,
    .card-title,
    .section-title,
    .stat-value {
      margin: 0;
      letter-spacing: -0.03em;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
      padding: 6px 12px;
      border: 1px solid rgba(110, 231, 249, 0.18);
      border-radius: 999px;
      color: var(--primary);
      background: rgba(14, 165, 233, 0.09);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }

    .subtitle,
    .helper,
    .meta,
    .stat-label,
    .nav-link,
    label,
    .status-chip {
      color: var(--muted);
    }

    .subtitle {
      margin-top: 10px;
      line-height: 1.7;
      max-width: 700px;
    }

    .hero-badge {
      min-width: 180px;
      padding: 18px 20px;
      border: 1px solid rgba(110, 231, 249, 0.16);
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(14, 30, 54, 0.92), rgba(8, 20, 38, 0.92));
      text-align: right;
    }

    .hero-badge strong {
      display: block;
      margin-top: 8px;
      font-size: 24px;
      color: #f8fafc;
    }

    .layout,
    .stats-grid,
    .action-grid {
      display: grid;
      gap: 22px;
    }

    .layout {
      grid-template-columns: repeat(12, 1fr);
    }

    .card,
    .panel,
    .stat-card,
    .action-card {
      border: 1px solid var(--line);
      border-radius: var(--radius-xl);
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(11, 19, 35, 0.92));
      box-shadow: var(--shadow);
      backdrop-filter: blur(16px);
    }

    .card,
    .panel {
      padding: 28px;
    }

    .card h2,
    .panel h2,
    .section-title {
      font-size: 24px;
    }

    .login-card {
      grid-column: 4 / span 6;
      overflow: hidden;
    }

    .dashboard-main,
    .settings-main,
    .upgrade-main {
      grid-column: span 8;
    }

    .dashboard-side,
    .settings-side,
    .upgrade-side {
      grid-column: span 4;
    }

    .helper {
      margin: 12px 0 0;
      font-size: 14px;
      line-height: 1.7;
    }

    .field-group {
      display: grid;
      gap: 18px;
      margin-top: 26px;
    }

    label {
      display: grid;
      gap: 10px;
      font-size: 14px;
      font-weight: 600;
    }

    input,
    select {
      width: 100%;
      padding: 14px 16px;
      border: 1px solid rgba(148, 163, 184, 0.16);
      border-radius: var(--radius-md);
      background: rgba(8, 15, 28, 0.92);
      color: var(--text);
      outline: none;
      transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    }

    input:focus,
    select:focus {
      border-color: rgba(110, 231, 249, 0.58);
      box-shadow: 0 0 0 4px rgba(34, 211, 238, 0.12);
      transform: translateY(-1px);
    }

    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      margin-top: 24px;
    }

    .btn,
    .ghost-link,
    .nav-link {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      text-decoration: none;
      transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }

    .btn {
      border: 0;
      border-radius: 14px;
      padding: 14px 18px;
      cursor: pointer;
      font-size: 15px;
      font-weight: 700;
      color: #03121f;
      background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%);
      box-shadow: 0 18px 36px rgba(14, 165, 233, 0.24);
    }

    .btn:hover,
    .ghost-link:hover,
    .nav-link:hover,
    .action-card:hover {
      transform: translateY(-2px);
    }

    .btn-secondary {
      color: var(--text);
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.96), rgba(15, 23, 42, 0.96));
      border: 1px solid rgba(148, 163, 184, 0.18);
      box-shadow: none;
    }

    .ghost-link,
    .nav-link {
      padding: 12px 16px;
      border: 1px solid rgba(148, 163, 184, 0.14);
      border-radius: 14px;
      background: rgba(9, 18, 33, 0.68);
    }

    .nav {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 22px;
    }

    .message {
      margin-top: 18px;
      padding: 14px 16px;
      border-radius: 16px;
      border: 1px solid rgba(52, 211, 153, 0.2);
      background: rgba(16, 185, 129, 0.1);
      color: #d1fae5;
      font-size: 14px;
      line-height: 1.6;
    }

    .message.error {
      border-color: rgba(251, 113, 133, 0.22);
      background: rgba(244, 63, 94, 0.1);
      color: #ffe4e6;
    }

    .stats-grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin-top: 28px;
    }

    .stat-card {
      padding: 22px;
    }

    .stat-value {
      margin-top: 12px;
      font-size: 28px;
      font-weight: 800;
      color: #f8fafc;
    }

    .stat-label {
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .action-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
      margin-top: 24px;
    }

    .action-card {
      padding: 22px;
      text-decoration: none;
      color: var(--text);
    }

    .action-card p {
      margin: 10px 0 0;
      line-height: 1.7;
      color: var(--muted);
    }

    .status-chip {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-top: 14px;
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid rgba(148, 163, 184, 0.16);
      background: rgba(10, 18, 33, 0.72);
      font-size: 13px;
      font-weight: 700;
    }

    .status-chip strong {
      color: #f8fafc;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .status-chip.validated { border-color: rgba(52, 211, 153, 0.28); color: #bbf7d0; }
    .status-chip.rejected { border-color: rgba(251, 113, 133, 0.28); color: #fecdd3; }
    .status-chip.idle { border-color: rgba(251, 191, 36, 0.24); color: #fde68a; }

    .list {
      margin: 18px 0 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.9;
    }

    .footer-note {
      margin-top: 16px;
      padding-top: 18px;
      border-top: 1px solid rgba(148, 163, 184, 0.12);
      color: var(--muted);
      font-size: 13px;
    }

    @media (max-width: 980px) {
      .layout { grid-template-columns: 1fr; }
      .login-card,
      .dashboard-main,
      .dashboard-side,
      .settings-main,
      .settings-side,
      .upgrade-main,
      .upgrade-side { grid-column: auto; }
      .hero { flex-direction: column; align-items: flex-start; }
      .hero-badge { width: 100%; text-align: left; }
      .stats-grid,
      .action-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="page-shell">
    {{ content | safe }}
  </div>
</body>
</html>
"""

LOGIN_CONTENT = """
<section class="layout">
  <div class="card login-card">
    <span class="eyebrow">CPE Gateway</span>
    <h1 id="page-title" class="card-title">统一接入的设备管理后台</h1>
    <p class="subtitle">以简洁的视觉层次展示登录入口、设备状态与运维动作，适合在持续测试与演示场景中快速验证核心流程。</p>
    {% if error %}<div id="error-message" class="message error">{{ error }}</div>{% endif %}
    <form method="post" class="field-group">
      <label>用户名
        <input id="username" name="username" placeholder="请输入管理员账号" />
      </label>
      <label>密码
        <input id="password" type="password" name="password" placeholder="请输入密码" />
      </label>
      <div class="actions">
        <button id="login-btn" class="btn" type="submit">登录系统</button>
      </div>
    </form>
    <p class="footer-note">默认演示账号用于本地自动化测试场景，可在后续接入数据库或统一认证服务。</p>
  </div>
</section>
"""

DASHBOARD_CONTENT = """
<section class="hero">
  <div>
    <span class="eyebrow">Overview</span>
    <h1 id="dashboard-title">设备控制台</h1>
    <p id="welcome-banner" class="subtitle">欢迎您，{{ username }}。当前页面提供网络设置、固件升级与持续交付验证的统一入口。</p>
    <div class="nav">
      <a id="nav-network" class="nav-link" href="{{ url_for('network') }}">网络设置</a>
      <a id="nav-upgrade" class="nav-link" href="{{ url_for('upgrade') }}">固件升级</a>
      <a id="nav-logout" class="nav-link" href="{{ url_for('logout') }}">安全退出</a>
    </div>
  </div>
  <div class="hero-badge">
    <span class="meta">系统状态</span>
    <strong>Stable</strong>
    <div class="status-chip idle">流水线模式：<strong>Ready</strong></div>
  </div>
</section>

<section class="layout">
  <div class="panel dashboard-main">
    <span class="eyebrow">Metrics</span>
    <h2 class="section-title">关键运行指标</h2>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">自动化覆盖</div>
        <div class="stat-value">95%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">最近构建</div>
        <div class="stat-value">12 min</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">运行状态</div>
        <div class="stat-value">Pass</div>
      </div>
    </div>

    <div class="action-grid">
      <a class="action-card" href="{{ url_for('network') }}">
        <h3>网络配置管理</h3>
        <p>集中维护 SSID、接入模式与基础参数，适合演示页面表单类回归测试。</p>
      </a>
      <a class="action-card" href="{{ url_for('upgrade') }}">
        <h3>固件升级验证</h3>
        <p>通过文件名校验与状态反馈，模拟持续交付前的升级包核验流程。</p>
      </a>
    </div>
  </div>

  <aside class="panel dashboard-side">
    <span class="eyebrow">Summary</span>
    <h2 class="section-title">运维提示</h2>
    <ul class="list">
      <li>每次配置变更都可由 Selenium 自动回归验证。</li>
      <li>升级入口适合接入 Jenkins 与 Allure 报告链路。</li>
      <li>当前界面采用响应式布局，便于扩展更多模块。</li>
    </ul>
    <p class="footer-note">页面样式已统一为深色玻璃拟态风格，适合项目演示、论文截图与前端自动化定位。</p>
  </aside>
</section>
"""

NETWORK_CONTENT = """
<section class="hero">
  <div>
    <span class="eyebrow">Network Settings</span>
    <h1 id="network-title">网络设置</h1>
    <p class="subtitle">管理网关无线名称、接入密码与联网模式，保存后可直接用于配置类 UI 自动化回归测试。</p>
  </div>
  <div class="hero-badge">
    <span class="meta">当前模式</span>
    <strong>{{ data['mode'] | upper }}</strong>
  </div>
</section>

<section class="layout">
  <div class="panel settings-main">
    <span class="eyebrow">Configuration</span>
    <h2 class="section-title">编辑网络参数</h2>
    {% if message %}<div id="network-message" class="message">{{ message }}</div>{% endif %}
    <form method="post" class="field-group">
      <label>SSID
        <input id="ssid" name="ssid" value="{{ data['ssid'] }}" />
      </label>
      <label>密码
        <input id="wifi-password" name="password" value="{{ data['password'] }}" />
      </label>
      <label>模式
        <select id="mode" name="mode">
          <option value="dhcp" {% if data['mode'] == 'dhcp' %}selected{% endif %}>DHCP</option>
          <option value="pppoe" {% if data['mode'] == 'pppoe' %}selected{% endif %}>PPPoE</option>
        </select>
      </label>
      <div class="actions">
        <button id="save-network" class="btn" type="submit">保存配置</button>
        <a id="back-dashboard" class="ghost-link" href="{{ url_for('dashboard') }}">返回控制台</a>
      </div>
    </form>
  </div>

  <aside class="panel settings-side">
    <span class="eyebrow">Tips</span>
    <h2 class="section-title">建议校验点</h2>
    <ul class="list">
      <li>保存前验证输入框默认值是否正确加载。</li>
      <li>切换 DHCP / PPPoE 时验证下拉框选中状态。</li>
      <li>提交后断言成功提示与回填数据保持一致。</li>
    </ul>
  </aside>
</section>
"""

UPGRADE_CONTENT = """
<section class="hero">
  <div>
    <span class="eyebrow">Firmware Delivery</span>
    <h1 id="upgrade-title">固件升级</h1>
    <p class="subtitle">上传升级包文件名并执行校验，模拟交付前的网关固件发布门禁流程。</p>
  </div>
  <div class="hero-badge">
    <span class="meta">升级状态</span>
    <strong>{{ status | upper }}</strong>
  </div>
</section>

<section class="layout">
  <div class="panel upgrade-main">
    <span class="eyebrow">Validation</span>
    <h2 class="section-title">上传并校验升级包</h2>
    {% if message %}
      <div id="upgrade-message" class="message {% if status == 'rejected' %}error{% endif %}">{{ message }}</div>
    {% endif %}
    <form method="post" class="field-group">
      <label>固件文件名
        <input id="firmware-file" name="filename" placeholder="例如：cpe_gateway_v2.1.0.bin" />
      </label>
      <div class="actions">
        <button id="upload-btn" class="btn" type="submit">上传并校验</button>
        <a id="back-dashboard" class="ghost-link" href="{{ url_for('dashboard') }}">返回控制台</a>
      </div>
    </form>
    <div id="upgrade-status" class="status-chip {{ status }}">状态：<strong>{{ status }}</strong></div>
  </div>

  <aside class="panel upgrade-side">
    <span class="eyebrow">Policy</span>
    <h2 class="section-title">发布规则</h2>
    <ul class="list">
      <li>仅允许 `.bin` 后缀的固件文件通过基础校验。</li>
      <li>校验成功后可在 CI 中继续执行自动化回归测试。</li>
      <li>校验失败时应阻断发布并通知相关研发人员。</li>
    </ul>
  </aside>
</section>
"""


def render_page(title: str, content: str, **context):
    return render_template_string(BASE_TEMPLATE, title=title, content=content, **context)


def require_login():
    if not session.get('username'):
        return redirect(url_for('login'))
    return None


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == 'admin' and password == 'admin123':
            session['username'] = username
            return redirect(url_for('dashboard'))
        error = '用户名或密码错误'
    return render_page('CPE 登录', LOGIN_CONTENT, error=error)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    guard = require_login()
    if guard:
        return guard
    return render_page('控制台', DASHBOARD_CONTENT, username=session['username'])


@app.route('/network', methods=['GET', 'POST'])
def network():
    guard = require_login()
    if guard:
        return guard

    message = None
    if request.method == 'POST':
        STATE['network'] = {
            'ssid': request.form.get('ssid', '').strip(),
            'password': request.form.get('password', '').strip(),
            'mode': request.form.get('mode', 'dhcp').strip(),
        }
        message = '网络配置已保存'
    return render_page('网络设置', NETWORK_CONTENT, data=STATE['network'], message=message)


@app.route('/upgrade', methods=['GET', 'POST'])
def upgrade():
    guard = require_login()
    if guard:
        return guard

    message = None
    if request.method == 'POST':
        filename = request.form.get('filename', '').strip()
        if not filename.endswith('.bin'):
            STATE['upgrade']['status'] = 'rejected'
            message = '仅允许上传 .bin 固件文件'
        else:
            STATE['upgrade']['last_filename'] = filename
            STATE['upgrade']['status'] = 'validated'
            message = f'固件 {filename} 校验通过，允许发布'
    return render_page('固件升级', UPGRADE_CONTENT, status=STATE['upgrade']['status'], message=message)


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
