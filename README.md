# BlackBagTest 自动化测试平台

**🧠 AI 赋能 · 开源 · 全栈 · 一体化** —— BlackBagTest 是一个覆盖接口全生命周期管理与端到端测试的 **智能化自动化测试平台**。通过 **AI 辅助生成用例与脚本**、**自然语言驱动 UI 自动化** 等创新体验，以及一站式的测试管理能力，显著降低自动化测试门槛，提升团队协作与交付效率。

本仓库为**前后端统一仓库**，包含完整后端（Django）与前端（Vue3）源码，并自带 Docker Compose 一键部署脚本。

## 📁 目录结构

```
BlackBagTest/
├── backend/                # 后端：Django + DRF + Django-Q + LangGraph(AI)
│   ├── apps/               # 业务应用（users/projects/interfaces/tests/ai_service ...）
│   ├── black_bag/          # Django 项目配置（settings_dev / settings_pro / settings_docker）
│   ├── core/               # 自动化引擎（接口/UI/性能/数据驱动）
│   ├── utils/             # 公共工具
│   ├── requirements.txt
│   ├── Dockerfile
│   └── entrypoint.sh
├── frontend/              # 前端：Vue3 + ElementPlus + Vxe-table
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── Dockerfile          # 多阶段构建（node 构建 → nginx 托管）
│   └── nginx.conf
├── docker-compose.yml      # 一键部署编排
├── .env.example            # 环境变量模板
└── README.md
```

## 🎯 核心特性

### 📦 全栈测试，一站搞定
原生支持 **接口测试**、**Web 自动化**、**App 自动化**、**性能测试**，无需在多套工具间切换，所有测试资产统一管理，降低维护成本。

### 🔐 精细化权限管控
支持 **按钮级权限** 和 **项目级隔离**，可灵活配置不同角色的操作范围，满足多项目团队的安全协作需求。

### 🧠 AI 智能辅助测试（核心亮点）
基于大语言模型能力，平台现已支持：

- **一键生成功能用例**：输入业务描述或接口信息，AI 自动生成结构化的功能测试用例（含前置条件、步骤、预期结果）。
- **一键生成单接口脚本用例**：针对单个接口，AI 自动生成可执行的自动化测试脚本（含参数构造、断言、动态数据绑定），零脚本基础也可快速产出。
- **自然语言驱动 UI 自动化**：通过集成的 AI Agent，用户只需用自然语言描述操作（如"点击登录按钮，输入用户名和密码"），Agent 即可自动解析并执行对应的 UI 自动化操作，真正实现 **零代码、零脚本** 的智能化测试。

**🤖 AI 助手**
平台内置智能 **AI 助手**，以对话交互的方式贯穿测试全流程：
- 在用例管理、接口测试、UI 自动化等任一界面，均可随时唤起 AI 助手。
- 通过自然语言向 AI 助手下达指令，如"为登录接口生成 5 条边界值测试用例"、"帮我检查这个接口的断言是否完整"等。
- AI 助手可智能理解上下文，提供用例补充建议、脚本优化提示、测试数据推荐等辅助能力，成为测试人员的 **7×24 小时智能副驾**。

### 📋 接口全生命周期管理
提供从 **接口文档、调试、Mock** 到 **接口自动化、依赖管理、版本演进** 的统一协作空间。
- 独创的 **树表格接口编辑器**，支持 JSON 一键导入/导出
- 每个单元格均可独立绑定 **变量**、**Faker 动态数据**、**前置接口返回值**
- 让接口配置更直观、更高效，告别繁琐的脚本编写
- **🔗 接口依赖零代码配置**：通过 **一键绑定** 功能，可直接引用前置接口的返回字段，无需编写 JSONPath 或正则提取脚本，让复杂场景编排像搭积木一样简单。

### 📅 测试计划与测试套件分层管理
平台将测试组织划分为清晰的**两层结构**：

| 层级 | 管理对象 | 核心职责 | 执行方式 |
|------|----------|----------|----------|
| **测试计划** | **功能用例** | 面向业务需求的整体执行计划，跟踪功能验证进度，把控迭代质量 | 手动/定时触发，跟踪执行进度与结果 |
| **测试套件** | **脚本用例**（接口/UI/性能脚本） | 面向自动化执行的技术集合，支持按**脚本用例**或**功能用例**组织执行 | 支持批量执行、CI/CD 集成、定时调度 |

- **测试计划**：聚焦功能用例的完整执行周期，用于版本发布前的全量回归验证，并跟踪每个功能用例的执行状态。
- **测试套件**：是自动化脚本的"容器"，可灵活组装接口、UI、性能脚本。测试套件支持**关联功能用例**，实现"功能 → 脚本"的双向追溯，让自动化执行结果直接服务于功能验证。

### ⚡ 功能用例一键执行 & 脚本关联回归
平台提供**功能用例与脚本用例的深度联动执行机制**：

- **功能用例一键执行**：在测试计划中，针对单个功能用例或批量功能用例，点击 **"一键执行"** 按钮，系统自动调起其关联的所有脚本用例（接口/UI/性能脚本）并执行。
- **执行过程实时可视**：执行过程中实时展示脚本运行日志与进度，测试人员可随时掌握执行动态。
- **执行结果自动回填**：执行完成后，脚本用例的测试结果自动 **回填至功能用例**，标记功能用例为"通过/失败"，让测试人员无需切换界面即可完成功能验证。
- **闭环价值**：形成 **"功能用例设计 → 关联脚本用例 → 一键执行回归 → 结果自动回填"** 的完整闭环，彻底解决功能验证与自动化执行"两张皮"的问题，大幅提升回归测试效率。

### 🐛 内置缺陷管理
平台原生集成轻量级**缺陷管理**系统，告别多工具切换：
- **一键提交缺陷**：测试执行失败时，可一键提交缺陷，自动携带请求/响应日志、截图及环境信息，无需手动粘贴。
- **完整流转流程**：支持自定义状态流转（新建 → 处理中 → 已修复 → 已关闭）、优先级分级、责任人指派。
- **深度关联**：缺陷与测试用例、测试计划深度绑定，形成"**发现 → 追踪 → 回归验证**"的完整闭环，让质量管理有据可查。

### 🤖 多引擎关键字驱动 UI 自动化
基于 **Selenium**、**Appium** 和 **Playwright** 封装，提供 **元素库 + 关键字驱动** 模式：
- 手工测试人员也能快速上手，大幅降低脚本编写与维护成本。
- 支持 Web、移动端（Android/iOS）及现代浏览器自动化，灵活适配不同测试场景。
- 结合 AI Agent，支持自然语言驱动执行，让 UI 自动化像与人对话一样简单。

### ⚡ 灵活的性能测试引擎
深度集成 Locust，通过 Python 库函数直接调用，支持分布式压测、自定义指标和实时监控，让性能测试更贴近开发流程。

### 🌐 开源免费，数据自主
采用 **MIT 协议**，支持 **私有化部署**，所有数据完全由您掌控，无商业产品的功能限制和人头费困扰。

## 🖼️ 平台预览

### 登录页
![登录页](backend/images/login.png)

### 导航页
![导航页](backend/images/guide.png)

### 项目管理页
![项目管理页](backend/images/project.png)

### 项目首页
![项目首页1](backend/images/index_1.png)
![项目首页2](backend/images/index_2.png)
![项目首页3](backend/images/index_3.png)

### 项目用户角色控制
![项目用户角色控制](backend/images/role_1.png)
![项目用户角色控制](backend/images/role_2.png)
![项目用户角色控制](backend/images/role_3.png)

### 接口管理
![接口管理](backend/images/api_list_mng.png)

### 接口文档
![接口文档](backend/images/api_doc_mng.png)

### 接口测试
![接口测试](backend/images/api_test_mng.png)

### 接口 Mock
![接口 Mock](backend/images/api_mock.png)

### 接口自动化
- **接口场景自动化步骤编写**
  ![接口场景自动化](backend/images/api_scene_test.png)
- **接口依赖无需参数提取，一键绑定**
  ![一键绑定](backend/images/step_params_bind.png)
- **接口动态数据生成**
  ![动态数据生成](backend/images/api_mock_test.png)
- **接口文档字段格式和类型校验**
  ![字段校验](backend/images/api_respone_check.png)
- **接口断言校验一键绑定变量**
  ![断言绑定](backend/images/check_info.png)
- **详细的用例执行日志**
  ![执行日志](backend/images/api_test_detail_log.png)

### 测试计划与测试套件
- **测试计划列表（功能用例执行计划）**
  ![测试计划](backend/images/test_plan_list.png)
- **测试套件管理（脚本用例集合）**
  ![测试套件](backend/images/test_suite_list.png)
  ![测试套件](backend/images/test_suite_list_detail.png)
- **测试计划执行进度看板**
  ![测试计划执行](backend/images/test_plan_execute.png)
  ![测试计划执行](backend/images/test_plan_execute_1.png)

### 功能用例一键执行（关联脚本回归）
- **功能用例关联脚本用例**（配置关联关系）
  ![功能用例关联脚本](backend/images/func_case_link_script.png)
- **功能用例一键执行**（点击执行，自动调起关联脚本，执行结果自动回填）
  ![功能用例一键执行](backend/images/func_case_one_click_run.png)

### AI 功能展示
- **AI 一键生成功能用例**
  ![AI生成功能用例](backend/images/ai_func_case.png)
- **AI 一键生成单接口脚本用例**
  ![AI生成单接口脚本用例](backend/images/ai_single_api_case.png)
- **AI 助手对话交互界面**
  ![AI助手](backend/images/ai_assistant.png)

### 缺陷管理
- **缺陷列表与状态流转**
  ![缺陷管理](backend/images/defect_manage.png)
  ![缺陷管理](backend/images/defect_manage_detail.png)

### 性能测试报告
![性能报告1](backend/images/locust_1.png)
![性能报告2](backend/images/locust_2.png)
![性能报告3](backend/images/locust_3.png)

### 功能测试报告
![功能报告1](backend/images/func_report_3.png)
![功能报告2](backend/images/func_report_4.png)

### Web UI 自动化
![Web UI 自动化](backend/images/web_ui_test.png)

### App UI 自动化
![App UI 自动化](backend/images/app_ui_test.png)

### 元素库
![元素库](backend/images/loc_db.png)

### 用例管理
![用例管理](backend/images/case_mange.png)

### 数据驱动测试
![数据驱动测试](backend/images/case_data_test.png)

## 🚀 快速开始

### 一键部署（Docker Compose）

> 前置条件：已安装 [Docker](https://docs.docker.com/get-docker/) 与 Docker Compose（v2+）。

**1. 克隆并准备环境变量**

```bash
git clone <仓库地址> BlackBagTest
cd BlackBagTest
cp .env.example .env          # Windows: copy .env.example .env
# 按需修改 .env 中的 MySQL / Redis 密码
```

**2. 一键启动**

```bash
docker compose up -d --build
```

首次构建会拉取镜像并安装后端依赖（包含 AI 相关的 chromadb / sentence-transformers、Playwright chromium 浏览器与 tesseract OCR，耗时较长，请耐心等待）。

**3. 访问平台**

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:8080 |
| 后端 API | http://localhost:8000 |

默认管理员账号：`admin` / `admin`（首次启动时由 `entrypoint.sh` 自动创建，并初始化权限与角色）。

**4. 常用命令**

```bash
docker compose logs -f backend        # 查看后端日志
docker compose logs -f frontend       # 查看前端日志
docker compose restart backend        # 重启后端（改代码后）
docker compose down                   # 停止并移除容器
docker compose down -v                # 停止并清空数据（慎用，会删除 MySQL/Redis/向量库数据）
```

**环境变量说明（`.env`）**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MYSQL_ROOT_PASSWORD` | `blackbag_root` | MySQL root 密码 |
| `MYSQL_DATABASE` | `blackbag` | 业务库名 |
| `MYSQL_USER` / `MYSQL_PASSWORD` | `blackbag` / `blackbag` | 业务库账号 |
| `REDIS_PASSWORD` | （空） | Redis 密码，留空则内网无密码 |
| `DJANGO_DEBUG` | `false` | 生产环境保持 `false` |

**部署架构**

- **双端口架构**：前端 nginx（8080）托管 SPA，后端 gunicorn（8000）提供 API。前端通过 `window.location.hostname` 自动拼接后端 8000 地址，因此用任意 IP/域名访问前端都能正确回调后端。
- 前端使用 **hash 路由**（`createWebHashHistory`），所有页面路由在 `#` 之后，nginx 无需配置反向代理即可正确刷新。
- 后端通过 `supervisord` 同时托管 `gunicorn`（Web）与 `python manage.py qcluster`（Django-Q 异步任务，AI 用例生成等）。
- 数据持久化：MySQL、Redis、后端日志、AI 向量库（chroma_db）、上传文件均使用 docker volume 挂载，`down`（不带 `-v`）不会丢数据。

### 本地开发

**后端**

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate   | Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

# 默认使用 SQLite（settings_dev，release3.db），开箱即用
python manage.py migrate
python manage.py runserver 127.0.0.1:8000

# 另开终端启动异步任务 worker（AI 用例生成等需要）
python manage.py qcluster
```

> 通过 `RUN_ENV` 环境变量切换配置：`dev`（SQLite，默认）、`pro`（MySQL）、`docker`（容器，参数从环境变量读取）。
> 修改后端代码后需重启 Django-Q worker 才能加载新逻辑。

**前端**

```bash
cd frontend
npm install --legacy-peer-deps
npm run serve          # 默认 http://127.0.0.1:8080
# 构建生产包：npm run build
```

## 🧱 软件架构

| 层级 | 技术栈 |
|------|--------|
| **后端** | Python + Django + Django REST Framework + django-filter + Django-Q2 |
| **前端** | Vue3 + ElementPlus + Vxe-table + Axios + Vue-router |
| **自动化** | Requests + Selenium + Appium + Playwright + Faker + JsonPath |
| **AI** | LangGraph + LangChain + OpenAI + ChromaDB + sentence-transformers |
| **数据库 / 中间件** | MySQL 8 + Redis 7 |
| **性能测试** | Locust + gevent |

## 🔮 后期规划

1. **持续优化 AI 能力**：提升 AI 生成用例和自然语言理解的准确率，支持更复杂的业务逻辑与场景组合。
2. **完善 APP UI 自动化**：支持通过平台在线操作手机，实现元素定位和实时交互。
3. **完善性能压测**：增加阶梯压测功能，并提高单机压测并发数。

## 🌐 开源免费

采用 MIT 协议，支持私有化部署，所有数据完全由您掌控。

## 💬 学习交流

- QQ 群：`1042573503`
- 微信号：`19911509724`

> BlackBagTest —— 让自动化测试更简单、更智能。欢迎使用、贡献和反馈！
