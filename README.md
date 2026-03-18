# CPE Gateway DevOps 自动化测试项目

本项目根据“基于 DevOps 的 CPE 网关 Web 界面持续测试”课题设计并实现了一个可落地的示范工程，覆盖以下核心能力：

- **持续集成/持续交付**：使用 `Jenkinsfile` 编排从代码拉取、环境准备、测试执行到 Allure 报告归档的完整流水线。
- **自动化测试**：基于 `Pytest + Selenium` 实现面向 CPE 网关 Web 管理界面的 UI 自动化测试框架。
- **容器化运行**：通过 `docker-compose.yml` 启动 Mock CPE Web、Selenium Chrome 和测试执行容器，模拟隔离的持续交付环境。
- **结果反馈**：生成 `pytest` 覆盖率报告与 `Allure` 结果文件，便于在 Jenkins 中可视化展示。

## 项目结构

```text
.
├── app/                     # 模拟 CPE 网关 Web 管理界面（Flask）
├── cpe_devops/             # 自动化测试框架核心代码
│   ├── pages/              # Page Object 封装
│   └── utils/              # 配置、截图、等待等工具
├── tests/
│   ├── ui/                 # Selenium UI 自动化测试
│   └── unit/               # 可在无浏览器环境运行的单元测试
├── Jenkinsfile             # Jenkins CI/CD 流水线定义
├── docker-compose.yml      # 本地/CI 一体化编排
├── Dockerfile              # 测试执行镜像
└── requirements.txt        # Python 依赖
```

## 功能说明

### 1. Mock CPE 网关 Web
示例 Web 应用提供以下页面与交互：

- 登录页面 `/login`
- 仪表盘页面 `/dashboard`
- 网络配置页面 `/network`
- 固件升级页面 `/upgrade`

这些页面可作为 Selenium 自动化测试的被测对象，用于验证登录、参数修改、升级文件校验等典型场景。

### 2. 自动化测试框架设计
框架采用 Page Object Model（POM）：

- `BasePage`：统一处理元素等待、点击、输入、截图等通用能力。
- `LoginPage`、`DashboardPage`、`NetworkPage`、`UpgradePage`：分别封装业务页面行为。
- `conftest.py`：提供浏览器驱动、环境变量、失败截图与 Allure 附件能力。

### 3. 流水线能力
`Jenkinsfile` 包含以下阶段：

1. Checkout：拉取代码
2. Build Test Image：构建测试镜像
3. Start Services：启动 mock app 与 Selenium 环境
4. Run Unit Tests：执行单元测试并生成覆盖率
5. Run UI Tests：执行 Selenium 测试并输出 Allure 结果
6. Publish Reports：归档测试结果并发布 Allure 报告

## 快速开始

### 方式一：本地 Python 运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m flask --app app.main run --host 0.0.0.0 --port 5000
```

另开终端执行：

```bash
pytest tests/unit -q
```

如果你已准备好 Selenium Server（例如 Docker 中的 `selenium/standalone-chrome`）：

```bash
export BASE_URL=http://127.0.0.1:5000
export SELENIUM_REMOTE_URL=http://127.0.0.1:4444/wd/hub
pytest tests/ui --alluredir=allure-results
```

### 方式二：Docker Compose 运行

```bash
docker compose up --build --abort-on-container-exit test-runner
```

## 关键环境变量

| 变量 | 默认值 | 说明 |
|---|---:|---|
| `BASE_URL` | `http://mock-cpe:5000` | 被测 Web 地址 |
| `SELENIUM_REMOTE_URL` | `http://selenium:4444/wd/hub` | Selenium Grid / Standalone Chrome 地址 |
| `BROWSER` | `chrome` | 浏览器类型 |
| `HEADLESS` | `true` | 是否启用无头模式 |
| `SCREENSHOT_DIR` | `artifacts/screenshots` | 失败截图输出目录 |

## 测试覆盖建议

- 核心业务优先：登录、网络配置保存、固件升级输入校验。
- 在 Jenkins 中通过 `pytest-cov` 监控测试代码的逻辑覆盖率。
- 对 UI 用例启用失败截图、显式等待和重试机制，提高执行稳定性。

## 后续可扩展方向

- 接入真实 CPE 固件刷写与设备状态采集接口
- 增加参数化数据驱动用例
- 增加邮件/企业微信/钉钉通知
- 接入 GitHub Actions 或 GitLab CI 形成多平台流水线
