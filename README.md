# CPE Gateway DevOps 自动化测试项目

本项目根据“基于 DevOps 的 CPE 网关 Web 界面持续测试”课题设计并实现了一个可落地的示范工程，覆盖以下核心能力：

- **持续集成/持续交付**：使用 `Jenkinsfile` 编排从代码拉取、环境准备、测试执行到 Allure 报告归档的完整流水线。
- **自动化测试**：基于 `Pytest + Selenium` 实现面向 CPE 网关 Web 管理界面的 UI 自动化测试框架。
- **容器化运行**：通过 `docker-compose.yml` 启动 Mock CPE Web、Selenium Chrome 和测试执行容器，模拟隔离的持续交付环境。
- **结果反馈**：生成 `pytest` 覆盖率报告与 `Allure` 结果文件，便于在 Jenkins 中可视化展示。

- **真实设备协议接入层**：`app/device_adapter.py` 已支持 `http / ssh / telnet / serial` 四类适配器，可通过环境变量切换，不再只依赖 mock。
- **前端演示界面**：Mock CPE 平台现已提供浅色高级风格页面，并补充控制台、网络设置、固件升级、运行诊断等模块，适合论文展示与自动化测试演示。

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
- 运行诊断页面 `/diagnostics`

这些页面可作为 Selenium 自动化测试的被测对象，用于验证登录、参数修改、升级文件校验、环境健康检查等典型场景。

### 2. 当前界面能力
当前 Web 页面已经具备以下演示功能：

- **控制台首页**：显示设备型号、固件版本、WAN 状态、在线终端、运行指标、最近活动。
- **网络设置**：支持配置 SSID、无线密码、联网模式、Wi‑Fi 信道、访客 Wi‑Fi，并展示最近保存时间。
- **固件升级**：支持校验固件文件名、显示最近固件、最近校验结果与发布时间。
- **运行诊断**：支持展示 Ping、DNS、云端连通性、丢包率，并模拟重新执行诊断。

### 3. 自动化测试框架设计
框架采用 Page Object Model（POM）：

- `BasePage`：统一处理元素等待、点击、输入、截图等通用能力。
- `LoginPage`、`DashboardPage`、`NetworkPage`、`UpgradePage`：分别封装业务页面行为。
- `conftest.py`：提供浏览器驱动、环境变量、失败截图与 Allure 附件能力。

### 4. 流水线能力
`Jenkinsfile` 包含以下阶段：

1. Checkout：拉取代码
2. Build Test Image：构建测试镜像
3. Start Services：启动 mock app 与 Selenium 环境
4. Run Unit Tests：执行单元测试并生成覆盖率
5. Run UI Tests：执行 Selenium 测试并输出 Allure 结果
6. Publish Reports：归档测试结果并发布 Allure 报告

## 快速开始

### 方式一：本地 Python 运行（Windows PowerShell）

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m flask --app app.main run --host 0.0.0.0 --port 5000
```

另开一个 PowerShell 窗口执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pytest tests/unit -q
```

如果你已准备好 Selenium Server（例如 Docker 中的 `selenium/standalone-chrome`）：

```powershell
$env:BASE_URL = 'http://127.0.0.1:5000'
$env:SELENIUM_REMOTE_URL = 'http://127.0.0.1:4444/wd/hub'
pytest tests/ui --alluredir=allure-results
```

### 方式二：本地 Python 运行（Linux / macOS）

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

### 方式三：Docker Compose 运行

```bash
docker compose up --build --abort-on-container-exit test-runner
```



## 新增的正式项目模块（已实现）

本轮已按你的要求补充 4 个更接近论文目标的模块：

1. **固件制品管理模块**
   - 支持登记固件包；
   - 记录版本号、来源、制品路径、MD5、SHA256、大小；
   - 支持 `git` / `path` / `upload` 三种来源标识；
   - 对应页面：`/artifacts`；接口：`/api/v1/artifacts`。

2. **设备升级执行模块**
   - 新增设备适配器抽象的 mock 实现；
   - 模拟上传固件、触发升级、等待设备重新在线；
   - 对应页面：`/jobs`；接口：`/api/v1/upgrade-jobs`。

3. **升级后验证模块**
   - 记录升级后设备版本号；
   - 输出 API 检查 / Web 检查结果；
   - 可与 Selenium UI 回归测试结合形成“接口校验 + 页面校验”。

4. **实验统计模块**
   - 自动记录每轮升级任务对应的实验结果；
   - 统计覆盖率、通过率、Flaky 率、平均耗时、失败原因；
   - 对应页面：`/stats`；接口：`/api/v1/experiments`。

## 为什么它不再只是演示壳

当前项目已经不只是静态演示页面，而是增加了更接近真实项目落地的后端结构：

- **持久化状态存储**：通过 `app/repository.py` 使用 SQLite 管理设备状态，并以 `app/data/state.json` 作为初始化种子数据，而不是把所有页面内容写死在视图函数里。
- **业务服务层**：通过 `app/services.py` 封装网络配置保存、固件命名规范校验、运行诊断、活动记录等业务逻辑。
- **可集成 API**：新增 `/api/v1/health`、`/api/v1/readiness`、`/api/v1/dashboard`、`/api/v1/network`、`/api/v1/network/export`、`/api/v1/network/import`、`/api/v1/upgrade`、`/api/v1/diagnostics`、`/api/v1/reset` 等接口，便于后续接入前端、真实设备代理层或自动化平台。
- **可替换真实设备适配层**：当前 JSON 存储可作为开发/测试阶段的设备代理，后续只需把服务层的数据读写替换为真实设备 API、SSH/串口指令或厂商 SDK，即可演进为实际项目。

这意味着它现在已经具备了“UI + 服务层 + 状态存储 + API + 自动化测试骨架”的基本形态，后续扩展不需要推翻重来。


## 进一步接近生产项目的增强

本轮又补充了几项更贴近生产部署的能力：

- **环境化配置**：新增 `app/config.py`，管理员账号、密码、SQLite 数据库路径、种子数据路径、API 前缀都可通过环境变量配置。
- **版本化 API**：在兼容旧 `/api/*` 的同时，新增 `/api/v1/*` 路由，便于后续接口演进。
- **就绪检查**：新增 `/api/v1/readiness`，用于给反向代理、容器编排和发布流水线做应用就绪判断。
- **配置模板导入导出**：新增网络配置导入/导出接口，可作为后续“配置备份恢复”能力的基础。

推荐下一阶段继续接入：

1. PostgreSQL 替代当前 SQLite，并引入 Alembic 迁移。
2. 真正的用户体系与权限控制。
3. 设备适配层（HTTP / SSH / Telnet / 串口）。
4. 更完整的审计日志、配置备份与发布审批流。

## 默认登录账号

| 项目 | 默认值 |
|---|---|
| 用户名 | `admin` |
| 密码 | `admin123` |

## 关键环境变量

| 变量 | 默认值 | 说明 |
|---|---:|---|
| `BASE_URL` | `http://mock-cpe:5000` | 被测 Web 地址 |
| `SELENIUM_REMOTE_URL` | `http://selenium:4444/wd/hub` | Selenium Grid / Standalone Chrome 地址 |
| `BROWSER` | `chrome` | 浏览器类型 |
| `HEADLESS` | `true` | 是否启用无头模式 |
| `SCREENSHOT_DIR` | `artifacts/screenshots` | 失败截图输出目录 |
| `DATABASE_PATH` | `app/data/cpe_gateway.db` | SQLite 数据库文件路径 |
| `SEED_PATH` | `app/data/state.json` | 数据初始化种子文件路径 |
| `API_PREFIX` | `/api/v1` | 版本化 API 前缀 |
| `DEVICE_PROTOCOL` | `mock` | 设备接入协议：`mock/http/ssh/telnet/serial` |
| `DEVICE_BASE_URL` | `http://192.168.1.1` | HTTP 协议设备管理地址 |
| `DEVICE_PORT` | `22` | SSH/Telnet 端口（SSH 常用 22，Telnet 常用 23） |
| `DEVICE_USERNAME` | `admin` | 设备登录用户名 |
| `DEVICE_PASSWORD` | `admin` | 设备登录密码 |
| `DEVICE_VERIFY_SSL` | `false` | HTTP 协议是否校验证书 |
| `SERIAL_PORT` | `/dev/ttyUSB0` | 串口设备路径 |
| `SERIAL_BAUDRATE` | `115200` | 串口波特率 |

## 测试覆盖建议

- 核心业务优先：登录、网络配置保存、固件升级输入校验、诊断页访问。
- 在 Jenkins 中通过 `pytest-cov` 监控测试代码的逻辑覆盖率。
- 对 UI 用例启用失败截图、显式等待和重试机制，提高执行稳定性。
- 可继续扩展真实设备接口校验、参数化测试和数据驱动测试。

## 后续可扩展方向

- 接入真实 CPE 固件刷写与设备状态采集接口。
- 接入企业微信、钉钉或邮件通知。
- 补充更细粒度的系统设置、用户管理、日志中心等页面。
- 接入 GitHub Actions、GitLab CI 或企业内部 DevOps 平台形成多平台流水线。
