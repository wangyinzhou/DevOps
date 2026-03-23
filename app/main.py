from __future__ import annotations

from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for

from app.config import get_settings, resolve_state_path
from app.repository import StateRepository
from app.services import GatewayService

settings = get_settings()
app = Flask(__name__)
app.secret_key = settings.secret_key

repository = StateRepository(resolve_state_path(settings))
service = GatewayService(repository)
API_PREFIX = settings.api_prefix.rstrip('/')

BASE_TEMPLATE = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ title }}</title>
  <style>
    :root {
      --bg: #f4f7fb;
      --bg-accent: #eef4ff;
      --surface: rgba(255, 255, 255, 0.92);
      --surface-soft: #f8fbff;
      --surface-strong: #ffffff;
      --line: #dbe4f0;
      --text: #162033;
      --muted: #66758f;
      --primary: #2563eb;
      --primary-soft: #eff6ff;
      --primary-border: #bfdbfe;
      --success: #059669;
      --success-soft: #ecfdf5;
      --warning: #d97706;
      --warning-soft: #fff7ed;
      --danger: #dc2626;
      --danger-soft: #fef2f2;
      --shadow-lg: 0 24px 60px rgba(37, 99, 235, 0.08);
      --shadow-md: 0 12px 30px rgba(15, 23, 42, 0.08);
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
        radial-gradient(circle at top left, rgba(96, 165, 250, 0.12), transparent 24%),
        radial-gradient(circle at right 15%, rgba(59, 130, 246, 0.08), transparent 28%),
        linear-gradient(180deg, #f8fbff 0%, #f4f7fb 48%, #eef4ff 100%);
    }

    a { color: inherit; }

    .shell {
      width: min(1240px, calc(100% - 32px));
      margin: 0 auto;
      padding: 24px 0 40px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 22px;
      border: 1px solid rgba(219, 228, 240, 0.95);
      border-radius: 22px;
      background: rgba(255, 255, 255, 0.86);
      box-shadow: var(--shadow-lg);
      backdrop-filter: blur(12px);
      margin-bottom: 20px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .brand-badge {
      display: grid;
      place-items: center;
      width: 46px;
      height: 46px;
      border-radius: 14px;
      background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
      color: white;
      font-size: 18px;
      font-weight: 800;
      box-shadow: 0 12px 24px rgba(37, 99, 235, 0.2);
    }

    .brand-title {
      margin: 0;
      font-size: 18px;
      font-weight: 800;
      letter-spacing: -0.02em;
    }

    .brand-subtitle,
    .helper,
    .meta,
    .muted,
    .stat-label,
    label,
    .nav-link,
    .table th,
    .timeline-time {
      color: var(--muted);
    }

    .brand-subtitle {
      margin-top: 4px;
      font-size: 13px;
    }

    .user-chip {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--surface-strong);
      font-weight: 700;
      color: var(--primary);
    }

    .page-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 22px;
      padding: 28px;
      border: 1px solid var(--line);
      border-radius: var(--radius-xl);
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(239, 246, 255, 0.95));
      box-shadow: var(--shadow-lg);
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
      padding: 6px 12px;
      border-radius: 999px;
      border: 1px solid var(--primary-border);
      background: var(--primary-soft);
      color: var(--primary);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }

    .page-title,
    .section-title,
    .stat-value,
    .card-title,
    .mini-title {
      margin: 0;
      letter-spacing: -0.03em;
    }

    .page-title {
      font-size: clamp(28px, 4vw, 42px);
    }

    .subtitle {
      margin: 12px 0 0;
      max-width: 760px;
      line-height: 1.75;
      color: var(--muted);
    }

    .header-side {
      min-width: 220px;
      padding: 18px 20px;
      border-radius: 18px;
      border: 1px solid var(--primary-border);
      background: white;
      box-shadow: var(--shadow-md);
    }

    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    .status-pill.validated,
    .status-pill.online,
    .status-pill.success {
      background: var(--success-soft);
      color: var(--success);
    }

    .status-pill.idle,
    .status-pill.warning {
      background: var(--warning-soft);
      color: var(--warning);
    }

    .status-pill.rejected,
    .status-pill.error {
      background: var(--danger-soft);
      color: var(--danger);
    }

    .layout,
    .grid-2,
    .stats-grid {
      display: grid;
      gap: 20px;
    }

    .layout {
      grid-template-columns: repeat(12, minmax(0, 1fr));
    }

    .main-col { grid-column: span 8; }
    .side-col { grid-column: span 4; }
    .full-col { grid-column: 1 / -1; }

    .panel,
    .stat-card,
    .tile,
    .login-card {
      border: 1px solid var(--line);
      border-radius: var(--radius-xl);
      background: var(--surface);
      box-shadow: var(--shadow-md);
    }

    .panel,
    .login-card {
      padding: 26px;
    }

    .login-wrap {
      display: grid;
      place-items: center;
      min-height: calc(100vh - 96px);
    }

    .login-card {
      width: min(560px, 100%);
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 251, 255, 0.98));
      box-shadow: var(--shadow-lg);
    }

    .field-grid,
    .actions,
    .nav,
    .summary-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
    }

    .form-grid {
      display: grid;
      gap: 18px;
      margin-top: 24px;
    }

    .field-grid > * {
      flex: 1 1 220px;
    }

    label {
      display: grid;
      gap: 8px;
      font-size: 14px;
      font-weight: 700;
    }

    input,
    select {
      width: 100%;
      padding: 14px 16px;
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      background: white;
      color: var(--text);
      outline: none;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    input:focus,
    select:focus {
      border-color: #93c5fd;
      box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
    }

    .btn,
    .ghost-btn,
    .nav-link,
    .tile-link {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      text-decoration: none;
      transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
    }

    .btn {
      padding: 13px 18px;
      border: none;
      border-radius: 14px;
      background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
      color: white;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 12px 24px rgba(37, 99, 235, 0.18);
    }

    .ghost-btn,
    .nav-link {
      padding: 12px 16px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: white;
      font-weight: 700;
    }

    .btn:hover,
    .ghost-btn:hover,
    .nav-link:hover,
    .tile-link:hover {
      transform: translateY(-1px);
    }

    .message {
      margin-top: 18px;
      padding: 14px 16px;
      border-radius: 16px;
      line-height: 1.65;
      font-size: 14px;
      font-weight: 600;
    }

    .message.success {
      background: var(--success-soft);
      color: var(--success);
      border: 1px solid #bbf7d0;
    }

    .message.error {
      background: var(--danger-soft);
      color: var(--danger);
      border: 1px solid #fecaca;
    }

    .stats-grid {
      grid-template-columns: repeat(4, minmax(0, 1fr));
      margin-top: 24px;
    }

    .stat-card {
      padding: 22px;
      background: linear-gradient(180deg, #ffffff, #f8fbff);
    }

    .stat-label {
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .stat-value {
      margin-top: 10px;
      font-size: 28px;
      font-weight: 800;
    }

    .summary-grid {
      margin-top: 20px;
    }

    .summary-item {
      flex: 1 1 180px;
      padding: 16px 18px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--surface-soft);
    }

    .summary-item strong {
      display: block;
      margin-top: 8px;
      font-size: 20px;
      color: var(--text);
    }

    .grid-2 {
      grid-template-columns: repeat(2, minmax(0, 1fr));
      margin-top: 22px;
    }

    .tile {
      padding: 22px;
      background: linear-gradient(180deg, #ffffff, #f8fbff);
    }

    .tile p,
    .mini-desc,
    .timeline-detail {
      margin: 10px 0 0;
      line-height: 1.7;
      color: var(--muted);
    }

    .table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 18px;
      overflow: hidden;
      border-radius: 18px;
      background: white;
    }

    .table th,
    .table td {
      text-align: left;
      padding: 14px 16px;
      border-bottom: 1px solid #edf2f7;
      font-size: 14px;
    }

    .table td {
      color: var(--text);
      font-weight: 600;
    }

    .timeline {
      display: grid;
      gap: 14px;
      margin-top: 18px;
    }

    .timeline-item {
      display: grid;
      gap: 6px;
      padding: 16px 18px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--surface-soft);
    }

    .timeline-title {
      font-weight: 800;
    }

    .mini-list {
      margin: 16px 0 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.9;
    }

    @media (max-width: 1080px) {
      .stats-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .main-col,
      .side-col { grid-column: 1 / -1; }
    }

    @media (max-width: 720px) {
      .shell { width: min(100% - 20px, 1240px); }
      .topbar,
      .page-header { padding: 20px; }
      .topbar,
      .page-header { flex-direction: column; align-items: flex-start; }
      .stats-grid,
      .grid-2 { grid-template-columns: 1fr; }
      .login-wrap { min-height: auto; padding-top: 24px; }
    }
  </style>
</head>
<body>
  <main class="shell">
    {% if show_nav %}
      <section class="topbar">
        <div class="brand">
          <div class="brand-badge">CPE</div>
          <div>
            <h1 class="brand-title">CPE Gateway 管理平台</h1>
            <div class="brand-subtitle">持续测试、持续交付与网关运维的统一演示工作台</div>
          </div>
        </div>
        <div class="user-chip">管理员：{{ username }}</div>
      </section>
    {% endif %}
    {{ content | safe }}
  </main>
</body>
</html>
"""

LOGIN_CONTENT = """
<section class="login-wrap">
  <div class="login-card">
    <span class="eyebrow">Sign In</span>
    <h2 id="page-title" class="page-title">欢迎进入 CPE 网关控制平台</h2>
    <p class="subtitle">该演示系统用于模拟 CPE 设备管理页面，并为 Jenkins + Pytest + Selenium 的持续回归测试提供稳定的被测对象。</p>
    {% if error %}<div id="error-message" class="message error">{{ error }}</div>{% endif %}
    <form method="post" class="form-grid">
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
    <div class="summary-grid">
      <div class="summary-item">
        <span class="muted">默认账号</span>
        <strong>{{ default_username }}</strong>
      </div>
      <div class="summary-item">
        <span class="muted">默认密码</span>
        <strong>{{ default_password }}</strong>
      </div>
    </div>
  </div>
</section>
"""

DASHBOARD_CONTENT = """
<section class="page-header">
  <div>
    <span class="eyebrow">Overview</span>
    <h2 id="dashboard-title" class="page-title">设备控制台</h2>
    <p id="welcome-banner" class="subtitle">欢迎您，{{ username }}。当前页面集中展示设备运行状态、连接终端、自动化测试结果以及常用运维入口。</p>
    <div class="nav">
      <a id="nav-network" class="nav-link" href="{{ url_for('network') }}">网络设置</a>
      <a id="nav-upgrade" class="nav-link" href="{{ url_for('upgrade') }}">固件升级</a>
      <a id="nav-diagnostics" class="nav-link" href="{{ url_for('diagnostics') }}">运行诊断</a>
      <a id="nav-logout" class="nav-link" href="{{ url_for('logout') }}">安全退出</a>
    </div>
  </div>
  <div class="header-side">
    <div class="muted">WAN 状态</div>
    <div style="margin-top: 10px;"><span class="status-pill online">{{ system['wan_status'] }}</span></div>
    <div class="helper" style="margin-top: 12px;">固件版本：{{ system['firmware_version'] }}<br/>设备型号：{{ system['device_model'] }}</div>
  </div>
</section>

<section class="stats-grid">
  <div class="stat-card">
    <div class="stat-label">在线终端</div>
    <div class="stat-value">{{ system['lan_clients'] }}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">CPU 使用率</div>
    <div class="stat-value">{{ system['cpu_usage'] }}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">内存使用率</div>
    <div class="stat-value">{{ system['memory_usage'] }}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">设备在线时长</div>
    <div class="stat-value">{{ system['uptime'] }}</div>
  </div>
</section>

<section class="layout" style="margin-top: 22px;">
  <div class="panel main-col">
    <span class="eyebrow">Operations</span>
    <h3 class="section-title">核心功能模块</h3>
    <div class="grid-2">
      <div class="tile">
        <h4 class="mini-title">网络配置中心</h4>
        <p>管理 SSID、工作模式、访客 Wi‑Fi 与信道策略，适合做表单型 UI 自动化回归。</p>
        <div class="actions"><a class="tile-link btn" href="{{ url_for('network') }}">进入网络设置</a></div>
      </div>
      <div class="tile">
        <h4 class="mini-title">固件交付门禁</h4>
        <p>校验待发布固件包、展示最近一次校验结果，并为持续交付决策提供可视化反馈。</p>
        <div class="actions"><a class="tile-link btn" href="{{ url_for('upgrade') }}">进入固件升级</a></div>
      </div>
      <div class="tile">
        <h4 class="mini-title">运行诊断中心</h4>
        <p>查看网关 Ping、DNS、云端连通性和丢包情况，模拟交付前的环境健康检查流程。</p>
        <div class="actions"><a class="tile-link ghost-btn" href="{{ url_for('diagnostics') }}">查看诊断报告</a></div>
      </div>
      <div class="tile">
        <h4 class="mini-title">自动化测试视图</h4>
        <p>该页面布局稳定、层级清晰，便于 Selenium 基于元素 ID 和文本内容构建可维护脚本。</p>
        <ul class="mini-list">
          <li>保留核心元素 ID，避免影响现有测试。</li>
          <li>页面已修复模板渲染问题，导航链接可正常访问。</li>
        </ul>
      </div>
    </div>
  </div>

  <aside class="panel side-col">
    <span class="eyebrow">Delivery</span>
    <h3 class="section-title">最近交付状态</h3>
    <div class="summary-grid">
      <div class="summary-item">
        <span class="muted">升级状态</span>
        <strong>{{ upgrade['status'] | upper }}</strong>
      </div>
      <div class="summary-item">
        <span class="muted">最近固件</span>
        <strong>{{ upgrade['last_filename'] }}</strong>
      </div>
    </div>
    <div class="helper" style="margin-top: 16px;">{{ upgrade['last_result'] }}</div>
  </aside>

  <div class="panel main-col">
    <span class="eyebrow">Clients</span>
    <h3 class="section-title">当前在线终端</h3>
    <table class="table">
      <thead>
        <tr>
          <th>设备名称</th>
          <th>IP 地址</th>
          <th>频段</th>
          <th>连接质量</th>
        </tr>
      </thead>
      <tbody>
        {% for client in clients %}
          <tr>
            <td>{{ client['name'] }}</td>
            <td>{{ client['ip'] }}</td>
            <td>{{ client['band'] }}</td>
            <td>{{ client['quality'] }}</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <aside class="panel side-col">
    <span class="eyebrow">Activity</span>
    <h3 class="section-title">最近活动</h3>
    <div class="timeline">
      {% for item in activities %}
        <div class="timeline-item">
          <div class="timeline-time">{{ item['time'] }}</div>
          <div class="timeline-title">{{ item['event'] }}</div>
          <div class="timeline-detail">{{ item['detail'] }}</div>
        </div>
      {% endfor %}
    </div>
  </aside>
</section>
"""

NETWORK_CONTENT = """
<section class="page-header">
  <div>
    <span class="eyebrow">Network Settings</span>
    <h2 id="network-title" class="page-title">网络设置</h2>
    <p class="subtitle">配置无线网络参数、模式和访客接入策略。页面保留了表单元素标识，适合直接用于自动化测试回归。</p>
  </div>
  <div class="header-side">
    <div class="muted">最近保存时间</div>
    <div style="margin-top: 10px; font-weight: 800;">{{ data['last_saved'] }}</div>
    <div class="helper" style="margin-top: 12px;">当前模式：{{ data['mode'] | upper }}<br/>访客 Wi‑Fi：{{ data['guest_wifi'] }}</div>
  </div>
</section>

<section class="layout">
  <div class="panel main-col">
    <span class="eyebrow">Configuration</span>
    <h3 class="section-title">编辑网络参数</h3>
    {% if message %}<div id="network-message" class="message success">{{ message }}</div>{% endif %}
    <form method="post" class="form-grid">
      <div class="field-grid">
        <label>SSID
          <input id="ssid" name="ssid" value="{{ data['ssid'] }}" />
        </label>
        <label>无线密码
          <input id="wifi-password" name="password" value="{{ data['password'] }}" />
        </label>
      </div>
      <div class="field-grid">
        <label>联网模式
          <select id="mode" name="mode">
            <option value="dhcp" {% if data['mode'] == 'dhcp' %}selected{% endif %}>DHCP</option>
            <option value="pppoe" {% if data['mode'] == 'pppoe' %}selected{% endif %}>PPPoE</option>
          </select>
        </label>
        <label>Wi‑Fi 信道
          <select name="channel">
            <option value="Auto" {% if data['channel'] == 'Auto' %}selected{% endif %}>Auto</option>
            <option value="1" {% if data['channel'] == '1' %}selected{% endif %}>1</option>
            <option value="6" {% if data['channel'] == '6' %}selected{% endif %}>6</option>
            <option value="11" {% if data['channel'] == '11' %}selected{% endif %}>11</option>
          </select>
        </label>
      </div>
      <div class="field-grid">
        <label>访客 Wi‑Fi
          <select name="guest_wifi">
            <option value="enabled" {% if data['guest_wifi'] == 'enabled' %}selected{% endif %}>启用</option>
            <option value="disabled" {% if data['guest_wifi'] == 'disabled' %}selected{% endif %}>禁用</option>
          </select>
        </label>
      </div>
      <div class="actions">
        <button id="save-network" class="btn" type="submit">保存配置</button>
        <a id="back-dashboard" class="ghost-btn" href="{{ url_for('dashboard') }}">返回控制台</a>
      </div>
    </form>
  </div>

  <aside class="panel side-col">
    <span class="eyebrow">Summary</span>
    <h3 class="section-title">当前生效配置</h3>
    <div class="summary-grid">
      <div class="summary-item"><span class="muted">SSID</span><strong>{{ data['ssid'] }}</strong></div>
      <div class="summary-item"><span class="muted">模式</span><strong>{{ data['mode'] | upper }}</strong></div>
      <div class="summary-item"><span class="muted">信道</span><strong>{{ data['channel'] }}</strong></div>
      <div class="summary-item"><span class="muted">访客 Wi‑Fi</span><strong>{{ data['guest_wifi'] }}</strong></div>
    </div>
    <ul class="mini-list">
      <li>保存后应断言成功提示可见。</li>
      <li>可继续扩展参数校验与数据驱动测试。</li>
      <li>推荐将更多真实配置项映射到此页面。</li>
    </ul>
  </aside>
</section>
"""

UPGRADE_CONTENT = """
<section class="page-header">
  <div>
    <span class="eyebrow">Firmware Delivery</span>
    <h2 id="upgrade-title" class="page-title">固件升级</h2>
    <p class="subtitle">模拟固件包发布前的门禁校验流程，保留升级状态提示和最近一次校验结果，便于 CI/CD 自动化回归。</p>
  </div>
  <div class="header-side">
    <div class="muted">当前校验状态</div>
    <div style="margin-top: 10px;"><span class="status-pill {{ status }}">{{ status }}</span></div>
    <div class="helper" style="margin-top: 12px;">最近更新时间：{{ upgrade['updated_at'] }}</div>
  </div>
</section>

<section class="layout">
  <div class="panel main-col">
    <span class="eyebrow">Validation</span>
    <h3 class="section-title">上传并校验升级包</h3>
    {% if message %}
      <div id="upgrade-message" class="message {% if status == 'rejected' %}error{% else %}success{% endif %}">{{ message }}</div>
    {% endif %}
    <form method="post" class="form-grid">
      <label>固件文件名
        <input id="firmware-file" name="filename" value="{{ upgrade['last_filename'] or '' }}" placeholder="例如：cpe_gateway_v2.1.0.bin" />
      </label>
      <div class="actions">
        <button id="upload-btn" class="btn" type="submit">上传并校验</button>
        <a id="back-dashboard" class="ghost-btn" href="{{ url_for('dashboard') }}">返回控制台</a>
      </div>
    </form>
    <div id="upgrade-status" style="margin-top: 18px;"><span class="status-pill {{ status }}">状态：{{ status }}</span></div>
  </div>

  <aside class="panel side-col">
    <span class="eyebrow">Release Gate</span>
    <h3 class="section-title">校验策略</h3>
    <div class="summary-grid">
      <div class="summary-item"><span class="muted">最近固件</span><strong>{{ upgrade['last_filename'] }}</strong></div>
      <div class="summary-item"><span class="muted">最近结果</span><strong>{{ upgrade['last_result'] }}</strong></div>
    </div>
    <ul class="mini-list">
      <li>仅允许 `.bin` 作为固件包后缀。</li>
      <li>校验通过后可继续执行 UI 自动化回归。</li>
      <li>失败时应阻断发布并回传报告。</li>
    </ul>
  </aside>
</section>
"""

DIAGNOSTICS_CONTENT = """
<section class="page-header">
  <div>
    <span class="eyebrow">Diagnostics</span>
    <h2 class="page-title">运行诊断</h2>
    <p class="subtitle">对网关基础连通性、DNS 解析和云端服务状态进行快速检查，可作为持续交付前的环境健康验证页面。</p>
    <div class="nav">
      <a class="nav-link" href="{{ url_for('dashboard') }}">返回控制台</a>
      <a class="nav-link" href="{{ url_for('network') }}">网络设置</a>
      <a class="nav-link" href="{{ url_for('upgrade') }}">固件升级</a>
    </div>
  </div>
  <div class="header-side">
    <div class="muted">最近诊断时间</div>
    <div style="margin-top: 10px; font-weight: 800;">{{ diagnostics['last_run'] }}</div>
  </div>
</section>

<section class="layout">
  <div class="panel main-col">
    <span class="eyebrow">Health Check</span>
    <h3 class="section-title">关键诊断结果</h3>
    {% if message %}<div class="message success">{{ message }}</div>{% endif %}
    <div class="grid-2">
      <div class="tile"><h4 class="mini-title">网关 Ping</h4><p>{{ diagnostics['gateway_ping'] }}</p></div>
      <div class="tile"><h4 class="mini-title">DNS 解析</h4><p>{{ diagnostics['dns_resolution'] }}</p></div>
      <div class="tile"><h4 class="mini-title">云端连接</h4><p>{{ diagnostics['cloud_connectivity'] }}</p></div>
      <div class="tile"><h4 class="mini-title">丢包率</h4><p>{{ diagnostics['packet_loss'] }}</p></div>
    </div>
    <form method="post" style="margin-top: 22px;">
      <button class="btn" type="submit">重新执行诊断</button>
    </form>
  </div>

  <aside class="panel side-col">
    <span class="eyebrow">Use Cases</span>
    <h3 class="section-title">适用场景</h3>
    <ul class="mini-list">
      <li>新固件部署后进行环境连通性确认。</li>
      <li>在 UI 自动化执行前检查测试目标是否可用。</li>
      <li>为 Jenkins/Allure 报告补充健康检查背景信息。</li>
    </ul>
  </aside>
</section>
"""


def render_page(title: str, content_template: str, *, show_nav: bool = True, **context):
    rendered_content = render_template_string(content_template, **context)
    return render_template_string(
        BASE_TEMPLATE,
        title=title,
        content=rendered_content,
        show_nav=show_nav,
        username=session.get('username', '未登录'),
    )



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
        if username == settings.admin_username and password == settings.admin_password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        error = '用户名或密码错误'
    return render_page('CPE 登录', LOGIN_CONTENT, show_nav=False, error=error, default_username=settings.admin_username, default_password=settings.admin_password)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    guard = require_login()
    if guard:
        return guard
    return render_page('控制台', DASHBOARD_CONTENT, username=session['username'], **service.dashboard_context())


@app.route('/network', methods=['GET', 'POST'])
def network():
    guard = require_login()
    if guard:
        return guard

    message = None
    if request.method == 'POST':
        result = service.update_network(request.form.to_dict())
        message = result['message']

    state = service.snapshot()
    return render_page('网络设置', NETWORK_CONTENT, data=state['network'], message=message)


@app.route('/upgrade', methods=['GET', 'POST'])
def upgrade():
    guard = require_login()
    if guard:
        return guard

    message = None
    if request.method == 'POST':
        result = service.register_firmware(request.form.get('filename', ''))
        message = result['message']

    state = service.snapshot()
    return render_page('固件升级', UPGRADE_CONTENT, status=state['upgrade']['status'], message=message, upgrade=state['upgrade'])


@app.route('/diagnostics', methods=['GET', 'POST'])
def diagnostics():
    guard = require_login()
    if guard:
        return guard

    message = None
    if request.method == 'POST':
        message = service.run_diagnostics()['message']

    state = service.snapshot()
    return render_page('运行诊断', DIAGNOSTICS_CONTENT, diagnostics=state['diagnostics'], message=message)


@app.route(f'{API_PREFIX}/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify(service.health())


@app.route(f'{API_PREFIX}/readiness', methods=['GET'])
def api_readiness():
    return jsonify(service.readiness())


@app.route(f'{API_PREFIX}/dashboard', methods=['GET'])
@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    return jsonify(service.dashboard_context())


@app.route(f'{API_PREFIX}/network', methods=['GET', 'POST'])
@app.route('/api/network', methods=['GET', 'POST'])
def api_network():
    if request.method == 'POST':
        result = service.update_network(request.get_json(silent=True) or request.form.to_dict())
        return jsonify({'message': result['message'], 'network': result['state']['network']})
    return jsonify({'network': service.snapshot()['network']})


@app.route(f'{API_PREFIX}/network/export', methods=['GET'])
def api_network_export():
    return jsonify(service.export_network_profile())


@app.route(f'{API_PREFIX}/network/import', methods=['POST'])
def api_network_import():
    payload = request.get_json(silent=True) or request.form.to_dict()
    result = service.import_network_profile(payload)
    status_code = 200 if result['ok'] else 400
    return jsonify({'message': result['message'], 'network': result['state']['network']}), status_code


@app.route(f'{API_PREFIX}/upgrade', methods=['GET', 'POST'])
@app.route('/api/upgrade', methods=['GET', 'POST'])
def api_upgrade():
    if request.method == 'POST':
        payload = request.get_json(silent=True) or request.form.to_dict()
        result = service.register_firmware(payload.get('filename', ''))
        return jsonify({'message': result['message'], 'status': result['status'], 'upgrade': result['state']['upgrade']})
    return jsonify({'upgrade': service.snapshot()['upgrade']})


@app.route(f'{API_PREFIX}/diagnostics', methods=['GET', 'POST'])
@app.route('/api/diagnostics', methods=['GET', 'POST'])
def api_diagnostics():
    if request.method == 'POST':
        result = service.run_diagnostics()
        return jsonify({'message': result['message'], 'diagnostics': result['state']['diagnostics']})
    return jsonify({'diagnostics': service.snapshot()['diagnostics']})


@app.route(f'{API_PREFIX}/reset', methods=['POST'])
@app.route('/api/reset', methods=['POST'])
def api_reset():
    state = repository.reset()
    return jsonify({'message': '系统状态已重置为初始值', 'state': state})


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
