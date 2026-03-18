from __future__ import annotations

from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = 'devops-demo-secret'

STATE = {
    'network': {'ssid': 'CPE-5G', 'password': 'ChangeMe123', 'mode': 'dhcp'},
    'upgrade': {'last_filename': None, 'status': 'idle'},
}

LOGIN_TEMPLATE = """
<!doctype html>
<html lang="zh-CN">
<head><title>CPE 登录</title></head>
<body>
  <h1 id="page-title">CPE 管理后台</h1>
  {% if error %}<div id="error-message">{{ error }}</div>{% endif %}
  <form method="post">
    <label>用户名<input id="username" name="username" /></label>
    <label>密码<input id="password" type="password" name="password" /></label>
    <button id="login-btn" type="submit">登录</button>
  </form>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!doctype html>
<html lang="zh-CN">
<head><title>控制台</title></head>
<body>
  <h1 id="dashboard-title">设备控制台</h1>
  <nav>
    <a id="nav-network" href="{{ url_for('network') }}">网络设置</a>
    <a id="nav-upgrade" href="{{ url_for('upgrade') }}">固件升级</a>
    <a id="nav-logout" href="{{ url_for('logout') }}">退出</a>
  </nav>
  <div id="welcome-banner">欢迎您，{{ username }}</div>
</body>
</html>
"""

NETWORK_TEMPLATE = """
<!doctype html>
<html lang="zh-CN">
<head><title>网络设置</title></head>
<body>
  <h1 id="network-title">网络设置</h1>
  {% if message %}<div id="network-message">{{ message }}</div>{% endif %}
  <form method="post">
    <label>SSID<input id="ssid" name="ssid" value="{{ data['ssid'] }}" /></label>
    <label>密码<input id="wifi-password" name="password" value="{{ data['password'] }}" /></label>
    <label>模式
      <select id="mode" name="mode">
        <option value="dhcp" {% if data['mode'] == 'dhcp' %}selected{% endif %}>DHCP</option>
        <option value="pppoe" {% if data['mode'] == 'pppoe' %}selected{% endif %}>PPPoE</option>
      </select>
    </label>
    <button id="save-network" type="submit">保存</button>
  </form>
  <a id="back-dashboard" href="{{ url_for('dashboard') }}">返回控制台</a>
</body>
</html>
"""

UPGRADE_TEMPLATE = """
<!doctype html>
<html lang="zh-CN">
<head><title>固件升级</title></head>
<body>
  <h1 id="upgrade-title">固件升级</h1>
  {% if message %}<div id="upgrade-message">{{ message }}</div>{% endif %}
  <form method="post">
    <label>固件文件名<input id="firmware-file" name="filename" /></label>
    <button id="upload-btn" type="submit">上传并校验</button>
  </form>
  <div id="upgrade-status">状态：{{ status }}</div>
  <a id="back-dashboard" href="{{ url_for('dashboard') }}">返回控制台</a>
</body>
</html>
"""


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
    return render_template_string(LOGIN_TEMPLATE, error=error)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    guard = require_login()
    if guard:
        return guard
    return render_template_string(DASHBOARD_TEMPLATE, username=session['username'])


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
    return render_template_string(NETWORK_TEMPLATE, data=STATE['network'], message=message)


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
    return render_template_string(
        UPGRADE_TEMPLATE,
        status=STATE['upgrade']['status'],
        message=message,
    )


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
