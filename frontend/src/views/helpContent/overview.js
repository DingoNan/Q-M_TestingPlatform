/**
 * 帮助文档 · 一级模块总览（menuContentMap）
 * key = 模块名称，需与 menu.js 中 platformMenu[].name 完全一致。
 */

export const menuContentMap = {
  '项目管理': {
    description: '项目的创建与维护、项目级 AI / 消息配置、审计追踪与测试小工具',
    anchors: [
      { id: 'ov-project-lifecycle', title: '项目生命周期' },
      { id: 'ov-project-pages', title: '各页面职责' },
      { id: 'ov-project-scope', title: '项目级配置的影响范围' }
    ],
    content: `
      <h3 id="ov-project-lifecycle">项目生命周期</h3>
      <p>项目是平台的数据隔离边界。一个项目内拥有独立的：环境、服务、平台、数据库、模块、接口、
      元素、常量、用户函数、步骤、用例、套件、测试计划、报告与缺陷。</p>
      <div class="flow">
        <div class="flow-step"><span class="flow-idx">1</span><b>建项目</b><p>项目列表 → 新建，填写项目名称与描述</p></div>
        <div class="flow-step"><span class="flow-idx">2</span><b>进入项目</b><p>我的项目 → 点击「进入」，加载项目上下文</p></div>
        <div class="flow-step"><span class="flow-idx">3</span><b>加成员授权</b><p>项目设置 → 成员管理，为成员分配项目内角色</p></div>
        <div class="flow-step"><span class="flow-idx">4</span><b>配置项目级能力</b><p>项目设置 → AI 供应商 / 消息设置</p></div>
        <div class="flow-step"><span class="flow-idx">5</span><b>开展测试</b><p>环境 → 资产 → 执行 → 报告 → 缺陷</p></div>
      </div>

      <h3 id="ov-project-pages">各页面职责</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">页面</th><th>职责</th><th>什么时候用</th></tr></thead>
        <tbody>
          <tr><td><b>我的项目</b></td><td>已加入项目的入口列表，点击「进入」加载项目上下文</td><td>每次登录后的第一站；刷新页面后需要重新进入</td></tr>
          <tr><td><b>项目列表</b></td><td>全量项目的新建、编辑、删除</td><td>创建新项目、维护项目基本信息</td></tr>
          <tr><td><b>项目申请</b></td><td>申请加入某个项目，走审核流程</td><td>需要访问他人创建的项目时</td></tr>
          <tr><td><b>项目设置</b></td><td>AI 供应商（模型接入）、消息设置（webhook / 邮箱推送）</td><td>要让 AI 助手可用、或需要执行结果自动推送时</td></tr>
          <tr><td><b>测试工具箱</b></td><td>63 个离线小工具：测试数据生成、JSON 处理、编码转换、加密哈希、字符串处理、Cron</td><td>造数据、转格式、算签名、写定时表达式</td></tr>
          <tr><td><b>审计日志</b></td><td>记录平台内的关键操作，可追溯「谁在什么时候改了什么」</td><td>排查配置被谁改动、做操作合规回查</td></tr>
        </tbody>
      </table>

      <h3 id="ov-project-scope">项目级配置的影响范围</h3>
      <div class="callout callout-info">
        <h4>AI 供应商是项目级配置</h4>
        <p>平台本身不内置模型密钥。只有在<b>项目设置 → AI 供应商</b>中配置了供应商（DeepSeek、腾讯混元、
        腾讯云、阿里云百炼、智谱、火山引擎、MiniMax、月之暗面、硅基流动，或自定义 OpenAI 兼容接口）
        并启用为默认模型后，AI 助手与各处的「AI 生成」功能才可用。</p>
        <p>内置供应商已带好 API 地址与可用模型列表；填好 API Key 后保存并启用即可。若 AI 助手提示
        「请先选择模型」而列表为空，先回到这里检查配置。</p>
      </div>
      <div class="callout callout-warn">
        <h4>消息推送按项目配置</h4>
        <p>执行完成后自动通知（钉钉 / 飞书 / 邮箱 / 站内消息）在<b>项目设置 → 消息设置</b>中配置，
        需要填写 Webhook URL 或 SMTP 信息。套件上的「执行完是否推送消息」开关只有在项目级配置完成后才真正生效。</p>
      </div>
    `
  },

  '用户管理': {
    description: '平台用户、角色与细粒度权限点——控制谁能看到什么、能改什么',
    anchors: [
      { id: 'ov-user-model', title: '权限模型' },
      { id: 'ov-user-pages', title: '各页面职责' },
      { id: 'ov-user-rules', title: '使用规则与注意事项' }
    ],
    content: `
      <h3 id="ov-user-model">权限模型</h3>
      <p>平台采用「用户 → 角色 → 权限点」三层模型，权限点与菜单一一对应，每个权限点有 5 个开关：</p>
      <table class="doc-table">
        <thead><tr><th style="width:170px">开关</th><th>含义</th></tr></thead>
        <tbody>
          <tr><td><b>has_permission</b></td><td>是否可见该菜单（不可见则左侧不显示）</td></tr>
          <tr><td><b>has_read_permission</b></td><td>是否可查看列表与详情</td></tr>
          <tr><td><b>has_add_permission</b></td><td>是否可新增（页面上的「新增」按钮是否显示）</td></tr>
          <tr><td><b>has_edit_permission</b></td><td>是否可编辑</td></tr>
          <tr><td><b>has_delete_permission</b></td><td>是否可删除</td></tr>
        </tbody>
      </table>
      <p>系统初始化时会自动创建两个角色：<b>全部权限</b>（5 个开关全开）与<b>只读权限</b>
      （仅 <code>has_permission</code> + <code>has_read_permission</code> 为真），可直接用，也可另建角色。</p>

      <h3 id="ov-user-pages">各页面职责</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">页面</th><th>职责</th></tr></thead>
        <tbody>
          <tr><td><b>用户列表</b></td><td>新增用户、编辑用户信息与状态、分配角色、重置密码</td></tr>
          <tr><td><b>角色列表</b></td><td>创建角色、为角色勾选权限点（含 5 个开关的粒度）</td></tr>
          <tr><td><b>权限列表</b></td><td>查看平台所有权限点（与菜单一一对应），用于核对权限覆盖面</td></tr>
        </tbody>
      </table>
      <p>另外，<b>项目</b>维度还有一层成员角色（项目设置 → 成员管理）：平台角色决定「能不能进这个功能」，
      项目成员角色决定「能不能进这个项目的这部分数据」，两者叠加生效。</p>

      <h3 id="ov-user-rules">使用规则与注意事项</h3>
      <div class="callout callout-warn">
        <h4>三条硬规则</h4>
        <p>1. 超级管理员拥有所有权限，<b>不能被修改或删除</b>；系统初始化账号为 <code>admin</code>，
        首次部署后请立即修改其密码。</p>
        <p>2. <b>权限变更后需重新登录才生效</b>——权限在登录时写入会话，改完不重登会出现
        「按钮时有时无」的错觉。</p>
        <p>3. 页面按钮不显示，<b>先查权限再报 Bug</b>。只读权限下「新增 / 编辑 / 删除」按钮本就不渲染。</p>
      </div>
      <div class="callout callout-tip">
        <h4>最小权限原则</h4>
        <p>日常执行人员给「只读 + 执行」即可；只有需要维护资产的角色才开新增 / 编辑；
        删除权限建议只给管理员，避免误删用例与接口。</p>
      </div>
    `
  },

  '环境管理': {
    description: '被测系统的四条配置线：环境、后端服务、前端平台、数据库',
    anchors: [
      { id: 'ov-env-relation', title: '四者关系' },
      { id: 'ov-env-pages', title: '各页面职责' },
      { id: 'ov-env-rules', title: '配置要点与联动影响' }
    ],
    content: `
      <h3 id="ov-env-relation">四者关系</h3>
      <p>「服务 / 平台 / 数据库」是<b>可复用的资源定义</b>，「环境」是<b>资源 + 具体地址的绑定关系</b>。
      同一个服务可以在测试环境与预发环境分别绑定不同域名，因此不必重复定义资源。</p>
      <table class="doc-table">
        <thead><tr><th style="width:140px">对象</th><th>定义层</th><th>绑定层（环境侧填什么）</th></tr></thead>
        <tbody>
          <tr><td><b>服务</b></td><td>服务名称、是否跟随服务域名、服务模块树</td><td>服务域名（host）</td></tr>
          <tr><td><b>平台</b></td><td>平台名称、平台类型（WEB / APP / H5 / 小程序 / 桌面端）</td><td>WEB 平台域名、APP 包名、APP 主页面入口名</td></tr>
          <tr><td><b>数据库</b></td><td>数据库名称</td><td>地址、用户名、密码、端口、库名、类型</td></tr>
        </tbody>
      </table>

      <h3 id="ov-env-pages">各页面职责</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">页面</th><th>职责</th></tr></thead>
        <tbody>
          <tr><td><b>环境配置</b></td><td>建环境、绑定服务 / 平台 / 数据库、配前置与后置 Python 脚本、环境全局变量</td></tr>
          <tr><td><b>服务配置</b></td><td>建后端服务与<b>服务模块</b>（模块树被接口、用例、缺陷共同引用）</td></tr>
          <tr><td><b>产品配置</b></td><td>建前端平台，供 UI 自动化定位与驱动</td></tr>
          <tr><td><b>数据库配置</b></td><td>建数据库资源，供数据库操作步骤取数、校验</td></tr>
        </tbody>
      </table>

      <h3 id="ov-env-rules">配置要点与联动影响</h3>
      <div class="callout callout-warn">
        <h4>环境名称全局唯一</h4>
        <p>环境名称长度不超过 20 字且<b>不允许重名</b>（含其他项目的环境）。建议按
        <code>系统名-环境</code> 命名，如 <code>支付平台-测试</code>。</p>
      </div>
      <div class="callout callout-warn">
        <h4>被引用的资源不能删除</h4>
        <p>数据库一旦被某个环境绑定，删除时会被拒绝（平台做了保护）。同理，服务被环境绑定、
        模块被接口或用例引用时也无法直接删除。要删请先解除依赖——这是为了防止「删一个资源导致一批用例集体报错」。</p>
      </div>
      <div class="callout callout-info">
        <h4>环境决定用例能跑成什么样</h4>
        <p>执行用例时必须选择环境。如果环境里没有绑定用例步骤所需的<b>服务域名</b>，
        请求会因解析不到主机而失败（压测会直接报「未解析到任何目标主机」）；
        如果没绑定<b>数据库</b>，数据库操作步骤无法执行；没绑定<b>平台</b>，UI 自动化步骤无法执行。
        因此「换个环境跑」之前，先确认这个环境把所需资源都绑齐了。</p>
      </div>
      <div class="callout callout-tip">
        <h4>前置 / 后置脚本与环境全局变量</h4>
        <p>环境级 <b>setup / teardown</b> 用 Python 编写，在该环境下每次执行前后运行，适合做登录预置、
        数据清理等公共动作。环境全局变量则用于存放该环境特有的值（账号、密钥、租户号），
        用例中同样以 <code>\${变量名}</code> 引用，从而让同一份用例跨环境复用。</p>
      </div>
    `
  },

  '公共资源': {
    description: '跨用例复用的五类资源：文件、元素、常量、用户函数、步骤',
    anchors: [
      { id: 'ov-common-what', title: '五类资源的分工' },
      { id: 'ov-common-when', title: '什么时候该放公共资源' },
      { id: 'ov-common-rules', title: '命名与维护建议' }
    ],
    content: `
      <h3 id="ov-common-what">五类资源的分工</h3>
      <table class="doc-table">
        <thead><tr><th style="width:140px">资源</th><th>用途</th><th style="width:190px">典型场景</th></tr></thead>
        <tbody>
          <tr><td><b>文件管理</b></td><td>存放测试用文件并供用例上传引用</td><td>批量导入模板、图片、证书、大文件</td></tr>
          <tr><td><b>元素配置</b></td><td>UI 自动化的页面元素定位信息</td><td>登录页账号输入框、提交按钮</td></tr>
          <tr><td><b>常量配置</b></td><td>可被用例引用的「常量类 + 常量项」字典</td><td>状态码对照、租户号、固定枚举</td></tr>
          <tr><td><b>用户函数</b></td><td>用 Python 封装可复用逻辑，在步骤中调用</td><td>自定义签名、复杂加解密、数据加工</td></tr>
          <tr><td><b>步骤管理</b></td><td>可被多条用例复用的步骤（HTTP / 数据库 / Web / APP）</td><td>登录、初始化、公共查询</td></tr>
        </tbody>
      </table>

      <h3 id="ov-common-when">什么时候该放公共资源</h3>
      <p>判断标准很简单：<b>这段配置是否会被第二条用例用到？</b>会，就抽到公共资源里。</p>
      <div class="flow">
        <div class="flow-step"><span class="flow-idx">1</span><b>重复两次以上</b><p>同样的登录请求、同样的字典，就该抽出来</p></div>
        <div class="flow-step"><span class="flow-idx">2</span><b>会被环境改变</b><p>域名、密钥、租户号这类随环境变化的值，放到环境变量</p></div>
        <div class="flow-step"><span class="flow-idx">3</span><b>逻辑复杂</b><p>超过几行的计算或加密，封装成用户函数</p></div>
        <div class="flow-step"><span class="flow-idx">4</span><b>定位易变</b><p>UI 元素统一走元素配置，改一处全用例生效</p></div>
      </div>

      <h3 id="ov-common-rules">命名与维护建议</h3>
      <div class="callout callout-tip">
        <h4>命名规范</h4>
        <p>用户函数与常量类的名称<b>在项目内唯一</b>，建议用「业务_用途」形式，如
        <code>auth_login</code>、<code>OrderStatus</code>；步骤描述写清意图而非实现，
        如「登录并获取 Token」而不是「发送 POST 请求」。</p>
      </div>
      <div class="callout callout-warn">
        <h4>改公共资源要评估影响面</h4>
        <p>公共步骤与元素被大量用例引用。修改前先确认引用范围，
        断言或参数结构上的破坏性变更会让一批用例同时失败。若只想为个别用例调整，
        请在用例里用<b>「引用并创建新步骤」</b>复制一份再改，而不是直接改公共步骤。</p>
      </div>
    `
  },

  '测试资产': {
    description: '接口文档、功能用例、脚本用例三大资产，以及标签与向量智仓',
    anchors: [
      { id: 'ov-case-assets', title: '资产全景' },
      { id: 'ov-case-diff', title: '功能用例 vs 脚本用例' },
      { id: 'ov-case-ai', title: 'AI 能力入口' },
      { id: 'ov-case-rules', title: '维护要点' }
    ],
    content: `
      <h3 id="ov-case-assets">资产全景</h3>
      <table class="doc-table">
        <thead><tr><th style="width:140px">页面</th><th>职责</th></tr></thead>
        <tbody>
          <tr><td><b>向量智仓</b></td><td>知识库 / 向量库管理，为 AI 提供业务知识与接口规范的检索上下文</td></tr>
          <tr><td><b>标签管理</b></td><td>维护标签体系，为用例打标以便筛选与批量组织（如「冒烟」「回归」「P0」）</td></tr>
          <tr><td><b>接口管理</b></td><td>接口文档的增删改查、调试、Mock 与返回体结构解析</td></tr>
          <tr><td><b>功能用例</b></td><td>面向人工执行的用例：前置条件、步骤描述、预期结果、评审状态</td></tr>
          <tr><td><b>脚本用例</b></td><td>面向机器执行的用例：步骤序列 + 变量 + 断言，是自动化与压测的执行单元</td></tr>
        </tbody>
      </table>

      <h3 id="ov-case-diff">功能用例 vs 脚本用例</h3>
      <table class="doc-table">
        <thead><tr><th style="width:160px">对比项</th><th>功能用例</th><th>脚本用例</th></tr></thead>
        <tbody>
          <tr><td>面向对象</td><td>人（测试人员）</td><td>平台执行引擎</td></tr>
          <tr><td>内容形态</td><td>文字 / 表格步骤描述</td><td>可执行步骤序列 + 变量 + 断言</td></tr>
          <tr><td>能否直接执行</td><td>人工执行，可登记到测试计划</td><td>平台自动执行，可组成套件与压测</td></tr>
          <tr><td>两者关系</td><td>可标注「是否可实现自动化」并<b>关联</b>对应脚本用例</td><td>可标注 <b>case 类型</b>与 <b>func_case</b> 反向关联功能用例</td></tr>
          <tr><td>状态字段</td><td>用例状态：待修改 / 待评审 / 已评审<br/>自动化状态：已完成 / 进行中 / 待开始 / 手工测试</td><td>最近执行结果：成功 / 失败 / 错误 / 未执行</td></tr>
        </tbody>
      </table>
      <div class="callout callout-tip">
        <h4>推荐做法</h4>
        <p>先写功能用例把「测什么」说清楚并通过评审，再据此写脚本用例实现自动化，
        然后用功能用例的「关联自动化用例」把两条线挂起来。这样需求变更时能快速定位到要改哪条脚本。</p>
      </div>

      <h3 id="ov-case-ai">AI 能力入口</h3>
      <table class="doc-table">
        <thead><tr><th style="width:170px">入口</th><th>能力</th></tr></thead>
        <tbody>
          <tr><td><b>AI 助手（悬浮球）</b></td><td>对话式生成功能测试用例，生成的用例自动保存并标记 <code>case_mark='AI生成'</code></td></tr>
          <tr><td><b>功能用例 → AI 生成</b></td><td>按模块批量生成功能用例</td></tr>
          <tr><td><b>功能用例 → AI 生成场景脚本</b></td><td>把功能用例转成脚本用例骨架</td></tr>
          <tr><td><b>接口管理 → AI 生成配置</b></td><td>从接口文档文本生成请求头 / 请求体 / 返回体结构</td></tr>
          <tr><td><b>元素配置 → AI 生成</b></td><td>生成 UI 元素定位</td></tr>
        </tbody>
      </table>
      <p>AI 能力依赖<b>项目设置 → AI 供应商</b>中配置的模型；首次使用需在 AI 面板中<b>选择模型</b>后方可发送消息。</p>

      <h3 id="ov-case-rules">维护要点</h3>
      <div class="callout callout-info">
        <h4>删除是软删除，名称可以复用</h4>
        <p>用例与接口的删除采用软删除（保留历史记录），并且名称唯一性校验只在「未删除」集合内进行。
        因此删除过的同名用例可以重新创建，不必为了绕过重名而改名。</p>
      </div>
      <div class="callout callout-warn">
        <h4>改了接口返回体，记得同步断言</h4>
        <p>接口的返回体结构是断言与取值引用（<code>\${...}</code>）的依据。若被测系统改了字段名或层级，
        请在接口管理中同步更新返回体，再核对引用该字段的用例，否则会大面积报「断言失败」或「解析参数失败」。</p>
      </div>
    `
  },

  '执行中心': {
    description: '三种执行组织方式：测试计划（人）、套件（机器）、定时任务（自动）',
    anchors: [
      { id: 'ov-suite-three', title: '三种方式怎么选' },
      { id: 'ov-suite-pages', title: '各页面职责' },
      { id: 'ov-suite-rules', title: '执行要点' }
    ],
    content: `
      <h3 id="ov-suite-three">三种方式怎么选</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">方式</th><th>面向</th><th>特点</th></tr></thead>
        <tbody>
          <tr><td><b>测试计划</b></td><td>人工执行</td><td>有起止时间与测试结论，逐条标记执行状态与执行人，适合版本验收</td></tr>
          <tr><td><b>套件管理</b></td><td>平台自动执行</td><td>一组用例 + 重试策略 + 执行器 + 消息推送，适合回归</td></tr>
          <tr><td><b>定时任务</b></td><td>平台自动执行</td><td>给套件挂上 crontab，到点自动跑，适合每日巡检</td></tr>
        </tbody>
      </table>

      <h3 id="ov-suite-pages">各页面职责</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">页面</th><th>职责</th></tr></thead>
        <tbody>
          <tr><td><b>测试计划</b></td><td>建计划、加入功能用例、跟踪执行进度、填测试结论；提供详情与概览两个视图</td></tr>
          <tr><td><b>套件管理</b></td><td>建套件、选用例、配计划类型 / 模式 / 执行器 / 重试 / 消息推送，并触发执行</td></tr>
          <tr><td><b>定时任务</b></td><td>把套件 + 环境 + crontab 绑成定时任务，可启用 / 停用</td></tr>
        </tbody>
      </table>

      <h3 id="ov-suite-rules">执行要点</h3>
      <table class="doc-table">
        <thead><tr><th style="width:170px">字段 / 配置</th><th>取值与含义</th></tr></thead>
        <tbody>
          <tr><td><b>计划类型</b></td><td>功能用例（面向人工）/ 脚本用例（面向自动执行）</td></tr>
          <tr><td><b>计划模式</b></td><td>静态模式=手工挑选具体用例；动态模式=按筛选条件自动纳入用例（用例增删后自动跟随）</td></tr>
          <tr><td><b>脚本用例类型</b></td><td>API / WEB_UI / APP_UI</td></tr>
          <tr><td><b>失败重试次数</b></td><td>脚本用例执行失败后自动重跑的次数，用于抵消环境抖动造成的偶发失败</td></tr>
          <tr><td><b>推送消息</b></td><td>执行完成后按项目设置的消息渠道通知</td></tr>
          <tr><td><b>Web / APP 执行器</b></td><td>UI 自动化所需的执行节点（配置在环境侧的执行机中）</td></tr>
          <tr><td><b>执行状态</b></td><td>未执行 / 暂缓 / 已通过 / 未通过 / 进行中（测试计划逐条用例）</td></tr>
        </tbody>
      </table>
      <div class="callout callout-warn">
        <h4>动态模式要留意用例范围</h4>
        <p>动态模式按条件实时筛选用例。新增用例若命中了筛选条件会被自动纳入执行范围，
        可能让执行时间与结果数量发生变化。需要精确控制范围时请用静态模式。</p>
      </div>
      <div class="callout callout-tip">
        <h4>重试次数不是越多越好</h4>
        <p>重试能压掉环境抖动引起的偶发失败，但也会掩盖真实的偶现缺陷。建议轻度重试（1~2 次），
        并把「首次失败后重试才通过」的用例单独列出来做稳定性跟进，而不是单纯依赖重试刷绿。</p>
      </div>
    `
  },

  '报告管理': {
    description: '日志、功能报告与性能报告——三条查结果的主路径',
    anchors: [
      { id: 'ov-report-three', title: '三种报告的分工' },
      { id: 'ov-report-status', title: '状态口径' },
      { id: 'ov-report-rules', title: '使用要点' }
    ],
    content: `
      <h3 id="ov-report-three">三种报告的分工</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">页面</th><th>内容</th><th>什么时候看</th></tr></thead>
        <tbody>
          <tr><td><b>日志列表</b></td><td>逐次执行的逐步骤日志（含请求、响应、断言、异常）</td><td>定位「为什么这条用例失败」</td></tr>
          <tr><td><b>功能报告</b></td><td>总用例数、成功 / 失败 / 错误用例数，以及每条用例的明细</td><td>看一轮回归的整体质量</td></tr>
          <tr><td><b>性能报告</b></td><td>请求统计、响应时间统计、异常统计、CPU / 内存、并发曲线</td><td>评估接口容量与稳定性</td></tr>
        </tbody>
      </table>

      <h3 id="ov-report-status">状态口径</h3>
      <table class="doc-table">
        <thead><tr><th style="width:120px">状态</th><th>含义</th><th>优先排查方向</th></tr></thead>
        <tbody>
          <tr><td><b>成功</b></td><td>所有断言通过</td><td>—</td></tr>
          <tr><td><b>失败</b></td><td>断言未通过，业务返回与预期不符</td><td>被测系统行为、断言是否过期、测试数据</td></tr>
          <tr><td><b>错误</b></td><td>执行过程中抛出异常（脚本、环境、依赖问题）</td><td>日志中的异常堆栈、环境配置、主机解析</td></tr>
          <tr><td><b>未执行</b></td><td>本次未跑到该用例</td><td>前置步骤失败导致中断</td></tr>
        </tbody>
      </table>
      <p>性能报告另有自己的状态：<b>已完成</b> / <b>压测中</b> / <b>失败</b>。其中「失败」表示压测未跑完，
      报告不具备参考价值，详情页会给出独立的<b>「失败原因」</b>结论。</p>

      <h3 id="ov-report-rules">使用要点</h3>
      <div class="callout callout-info">
        <h4>报告是快照，不会变</h4>
        <p>报告在生成时即固化为快照（含用例数统计）。<b>重跑会生成一份新报告</b>，不会覆盖旧报告。
        因此对比「这次比上次好还是差」时，要确保比的是同一条用例集合的两份报告。</p>
      </div>
      <div class="callout callout-warn">
        <h4>别把「错误」当「失败」</h4>
        <p>「错误」多为平台侧或环境侧问题（步骤类型未支持、变量解析异常、主机解析失败等），
        与被测系统质量无关。用例结果统计时建议把「错误」单独列出跟进，不要混进失败率里评价被测系统。</p>
      </div>
      <div class="callout callout-warn">
        <h4>压测失败先看「失败原因」</h4>
        <p>性能报告状态为「失败」时，详情页会有一张独立的<b>「失败原因」</b>卡片给出结论式说明；
        需要原始堆栈时再展开下方的<b>「异常统计」</b>。两者的分工是：
        失败原因=为什么失败（结论），异常统计=原始异常明细（溯源）。</p>
      </div>
    `
  },

  '缺陷管理': {
    description: '缺陷的登记、流转与评论，与用例和测试计划互相追溯',
    anchors: [
      { id: 'ov-defect-model', title: '缺陷字段说明' },
      { id: 'ov-defect-flow', title: '缺陷流转' },
      { id: 'ov-defect-rules', title: '提单建议' }
    ],
    content: `
      <h3 id="ov-defect-model">缺陷字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">字段</th><th>取值</th></tr></thead>
        <tbody>
          <tr><td><b>缺陷标题</b></td><td>一句话说清「在哪、做什么、得到什么错误结果」</td></tr>
          <tr><td><b>缺陷描述</b></td><td>复现路径与环境信息</td></tr>
          <tr><td><b>实际结果</b> / <b>预期结果</b></td><td>必须分开写，便于判定是否修复</td></tr>
          <tr><td><b>严重程度</b></td><td>致命 / 严重 / 一般 / 轻微</td></tr>
          <tr><td><b>优先级</b></td><td>紧急 / 高 / 中 / 低</td></tr>
          <tr><td><b>BUG 类型</b></td><td>代码问题-前端 / 代码问题-后端 / 设计如此 / 重复BUG / 需求变动 / UI样式 / 设计缺陷</td></tr>
          <tr><td><b>状态</b></td><td>待处理 / 处理中 / 已解决 / 已关闭</td></tr>
          <tr><td><b>所属模块</b></td><td>来自「服务配置 → 服务模块」，与接口、用例共用同一套模块树</td></tr>
          <tr><td><b>处理人</b> / <b>负责人</b></td><td>处理人=实际修的人；负责人=跟踪闭环的人</td></tr>
          <tr><td><b>关联</b></td><td>可关联功能用例与测试计划，便于回溯「哪个计划发现了它」</td></tr>
          <tr><td><b>附件</b> / <b>评论</b></td><td>截图、日志与沟通记录</td></tr>
        </tbody>
      </table>

      <h3 id="ov-defect-flow">缺陷流转</h3>
      <div class="flow">
        <div class="flow-step"><span class="flow-idx">1</span><b>待处理</b><p>测试提交，指定处理人与优先级</p></div>
        <div class="flow-step"><span class="flow-idx">2</span><b>处理中</b><p>研发接单修复</p></div>
        <div class="flow-step"><span class="flow-idx">3</span><b>已解决</b><p>研发修复完成，转回测试验证</p></div>
        <div class="flow-step"><span class="flow-idx">4</span><b>已关闭</b><p>测试验证通过后关闭</p></div>
      </div>

      <h3 id="ov-defect-rules">提单建议</h3>
      <div class="callout callout-tip">
        <h4>让缺陷可复现、可判定</h4>
        <p>1. 标题写「模块 + 操作 + 现象」，不要写「XX 不好用」。</p>
        <p>2. 实际结果与预期结果分开写，修复后能直接对照验收。</p>
        <p>3. 关联到具体功能用例，等于附上了复现步骤，省去重复描述。</p>
        <p>4. 环境信息（环境名、账号、数据）写在描述里——同一个缺陷在不同环境可能表现不同。</p>
      </div>
      <div class="callout callout-info">
        <h4>平台缺陷与用例失败的边界</h4>
        <p>报告里的「错误」（平台或环境异常）不应直接提缺陷给被测系统；应先确认是不是配置问题。
        只有确认是被测系统自身行为不符预期（即报告里的「失败」）才登记为业务缺陷。</p>
      </div>
    `
  },

  '平台指南': {
    description: 'AI 助手用法、变量引用语法大全、以及最常见的坑与排查路径',
    anchors: [
      { id: 'ov-guide-ai', title: 'AI 助手' },
      { id: 'ov-guide-vars', title: '变量引用' },
      { id: 'ov-guide-faq', title: '常见问题' }
    ],
    content: `
      <h3 id="ov-guide-ai">AI 助手</h3>
      <p>AI 助手是右下角的<b>悬浮按钮</b>（仅图标、无文字），在已进入项目的页面中都会出现，
      例如项目主页、功能用例、元素配置、脚本用例等页面。点击后打开全屏面板，包含「选择模型」、
      会话区和快速动作（<b>AI生成功能测试用例</b>、<b>AI生成元素</b>）。</p>
      <p>生成用例为后台异步任务，完成后会把用例自动落库并标记 <code>case_mark='AI生成'</code>，
      可在功能用例列表按该标记筛选复核。</p>
      <div class="callout callout-warn">
        <h4>AI 助手的两个前置条件</h4>
        <p>1. 必须先<b>进入项目</b>（悬浮球挂在项目上下文中，未进项目不显示）。</p>
        <p>2. 首次使用必须先在面板中<b>选择模型</b>，否则发送按钮不可用。可选模型来自
        <b>项目设置 → AI 供应商</b>中已启用的配置。详见「平台指南 → AI 助手」。</p>
      </div>

      <h3 id="ov-guide-vars">变量引用</h3>
      <p>用例中的 URL、请求头、请求体、查询参数与断言都支持变量引用，统一写法为
      <code>\${变量名}</code>，由引擎在执行时做替换。</p>
      <table class="doc-table">
        <thead><tr><th style="width:230px">写法</th><th>取值来源</th></tr></thead>
        <tbody>
          <tr><td><code>\${字段名}</code></td><td>用例全局变量 / 环境全局变量 / 已提取的变量</td></tr>
          <tr><td><code>\${响应对象.字段}</code></td><td>引用执行上下文中的响应对象字段</td></tr>
          <tr><td><code>\${常量类名.常量项名}</code></td><td>命中「常量配置」中的常量项，取回其值</td></tr>
        </tbody>
      </table>
      <p>完整规则、优先级与排错方法见「平台指南 → 变量引用语法」。</p>

      <h3 id="ov-guide-faq">常见问题</h3>
      <p>把最高频的 10 个问题与处置路径整理成了速查表，见「平台指南 → 常见问题与避坑」。
      其中前三名分别是：<b>刷新后菜单消失</b>（需重新进入项目）、
      <b>压测报未解析到目标主机</b>（环境未绑定服务域名）、
      <b>AI 发送按钮不可点</b>（未选模型或未配 AI 供应商）。</p>
    `
  }
}

export default menuContentMap
