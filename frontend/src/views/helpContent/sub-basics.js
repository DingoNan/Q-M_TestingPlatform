/**
 * 帮助文档 · 二级页面详述（一）：项目管理 / 用户管理 / 环境管理
 * key 规则：`${一级模块 path}-${二级菜单 id}`，与 menu.js 严格对应。
 */

export const basicsChildren = {
  /* ================= 项目管理 ================= */
  'project-myProjects': {
    description: '已加入项目的入口列表——登录后的第一站，也是每次刷新后的必经之路',
    anchors: [
      { id: 'sub-myProjects-what', title: '页面用途' },
      { id: 'sub-myProjects-how', title: '操作步骤' },
      { id: 'sub-myProjects-trap', title: '关键陷阱' }
    ],
    content: `
      <h3 id="sub-myProjects-what">页面用途</h3>
      <p>列出当前账号已加入的所有项目。每个项目卡片上有「进入」按钮，
      点击后平台才把<b>项目上下文</b>加载到内存，左侧随即出现环境管理、公共资源、测试资产、
      执行中心、报告管理、缺陷管理等项目级菜单，右下角的 AI 助手悬浮球也会挂载出来。</p>

      <h3 id="sub-myProjects-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 登录</h4><p>使用账号密码登录。登录成功后默认进入我的项目页。</p></li>
        <li><h4>2. 找到目标项目</h4><p>用页面上的搜索框按项目名称筛选，或在列表中直接定位。</p></li>
        <li><h4>3. 点击「进入」</h4><p>这是最关键的一步。进入成功后左侧导航会刷新为项目级菜单。</p></li>
        <li><h4>4. 开始工作</h4><p>此后所有操作都在该项目的数据范围内进行。</p></li>
      </ol>

      <h3 id="sub-myProjects-trap">关键陷阱</h3>
      <div class="callout callout-warn">
        <h4>刷新页面 = 退出项目上下文</h4>
        <p>当前项目信息仅保存在浏览器内存中，<b>不做持久化</b>。按 F5 刷新、或在地址栏直接改 hash
        （例如手工把地址改成 <code>#/resource/funcCase</code>）都不会加载项目上下文，
        结果就是菜单缺失、功能报错、AI 助手不出现。</p>
        <p><b>正确做法</b>：刷新后先回到<b>我的项目</b>，重新点击「进入」，再继续操作。
        不要通过手工改 URL 的方式在项目内跳转。</p>
      </div>
      <div class="callout callout-info">
        <h4>看不到任何项目怎么办</h4>
        <p>说明当前账号还没有被加入任何项目。请联系管理员在<b>项目设置 → 成员管理</b>中把你加入，
        或到<b>项目申请</b>提交加入申请等待审批。</p>
      </div>
    `
  },

  'project-projectList': {
    description: '全量项目的新建与维护',
    anchors: [
      { id: 'sub-projectList-model', title: '字段说明' },
      { id: 'sub-projectList-how', title: '操作步骤' },
      { id: 'sub-projectList-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-projectList-model">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>项目名称</b></td><td>项目标识，建议用被测系统全称，如「支付电子化监测平台」</td></tr>
          <tr><td><b>项目描述</b></td><td>补充说明项目的测试范围、负责人或对接信息</td></tr>
        </tbody>
      </table>

      <h3 id="sub-projectList-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新建项目</h4><p>点击「新增」，填写项目名称与项目描述后保存。</p></li>
        <li><h4>2. 编辑项目</h4><p>在列表中点击编辑，修改名称或描述。</p></li>
        <li><h4>3. 删除项目</h4><p>点击删除并确认。删除前请确认该项目下已无需要保留的资产。</p></li>
      </ol>

      <h3 id="sub-projectList-rules">注意事项</h3>
      <div class="callout callout-warn">
        <h4>项目是数据隔离边界</h4>
        <p>不同项目之间环境、接口、用例、报告等数据互不可见。删除项目将无法再访问其名下所有资产，
        操作前请与团队确认，必要时先导出报告与用例清单。</p>
      </div>
      <div class="callout callout-tip">
        <h4>建完项目别停在这一步</h4>
        <p>新建项目后需要回到<b>我的项目</b>点击「进入」，再去做环境与资产配置。</p>
      </div>
    `
  },

  'project-projectAppeal': {
    description: '申请加入不属于自己的项目',
    anchors: [
      { id: 'sub-appeal-how', title: '申请流程' },
      { id: 'sub-appeal-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-appeal-how">申请流程</h3>
      <div class="flow">
        <div class="flow-step"><span class="flow-idx">1</span><b>提交申请</b><p>在项目申请页选择目标项目并提交</p></div>
        <div class="flow-step"><span class="flow-idx">2</span><b>等待审批</b><p>申请状态为「未通过」（待审）</p></div>
        <div class="flow-step"><span class="flow-idx">3</span><b>管理员审批</b><p>项目管理员在审批入口处理</p></div>
        <div class="flow-step"><span class="flow-idx">4</span><b>加入成功</b><p>审批通过后项目出现在「我的项目」中</p></div>
      </div>

      <h3 id="sub-appeal-rules">注意事项</h3>
      <div class="callout callout-info">
        <h4>申请通过后还需分配角色</h4>
        <p>加入项目只解决「能进项目」，具体能操作哪些功能仍由平台角色与项目成员角色决定。
        如果进去后按钮大量不可用，请让管理员检查你的角色权限。</p>
      </div>
      <div class="callout callout-tip">
        <h4>提前说清用途能加快审批</h4>
        <p>提交申请时一并告知项目负责人你的用途（如「参与 XX 版本回归，需读写用例权限」），
        可避免反复沟通。</p>
      </div>
    `
  },

  'project-systemSetting': {
    description: '项目级配置：AI 供应商接入与消息推送',
    anchors: [
      { id: 'sub-setting-tabs', title: '两个配置项' },
      { id: 'sub-setting-ai', title: 'AI 供应商配置' },
      { id: 'sub-setting-msg', title: '消息设置' }
    ],
    content: `
      <h3 id="sub-setting-tabs">两个配置项</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">配置项</th><th>作用</th></tr></thead>
        <tbody>
          <tr><td><b>AI 供应商</b></td><td>接入大模型，决定 AI 助手与各处「AI 生成」能否使用、用哪个模型</td></tr>
          <tr><td><b>消息设置</b></td><td>配置执行结果的通知渠道与推送策略</td></tr>
        </tbody>
      </table>

      <h3 id="sub-setting-ai">AI 供应商配置</h3>
      <p>平台不内置模型密钥，需要自行接入。内置供应商及其默认接口地址：</p>
      <table class="doc-table">
        <thead><tr><th style="width:140px">供应商</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>DeepSeek</b></td><td>默认地址 <code>https://api.deepseek.com</code>，可选模型含 deepseek-v4-pro、deepseek-v4-flash 等</td></tr>
          <tr><td><b>腾讯混元</b></td><td>腾讯云混元大模型</td></tr>
          <tr><td><b>腾讯云</b></td><td>腾讯云大模型服务</td></tr>
          <tr><td><b>阿里云百炼</b></td><td>阿里云百炼平台模型</td></tr>
          <tr><td><b>智谱</b></td><td>智谱 GLM 系列</td></tr>
          <tr><td><b>火山引擎</b></td><td>火山方舟模型服务</td></tr>
          <tr><td><b>MiniMax</b></td><td>MiniMax 系列</td></tr>
          <tr><td><b>月之暗面</b></td><td>Kimi 系列</td></tr>
          <tr><td><b>硅基流动</b></td><td>SiliconFlow 模型聚合</td></tr>
          <tr><td><b>自定义</b></td><td>任何 OpenAI 兼容接口，自行填写地址与模型名</td></tr>
        </tbody>
      </table>
      <ol class="step-list">
        <li><h4>1. 选择供应商</h4><p>在 AI 供应商页选择供应商，接口地址与可选模型会自动带出。</p></li>
        <li><h4>2. 填 API Key</h4><p>粘贴该供应商控制台生成的密钥。</p></li>
        <li><h4>3. 选择模型并保存</h4><p>从模型下拉中选择要用的模型，保存配置。</p></li>
        <li><h4>4. 启用为可用</h4><p>确认该配置处于启用状态。平台只把<b>已启用</b>的模型提供给 AI 助手。若配置了多个，可指定一个为默认。</p></li>
        <li><h4>5. 回到 AI 助手选择模型</h4><p>首次打开 AI 面板需手动「选择模型」，之后即可正常对话与生成。</p></li>
      </ol>

      <h3 id="sub-setting-msg">消息设置</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">渠道</th><th>需要填写的信息</th></tr></thead>
        <tbody>
          <tr><td><b>钉钉</b></td><td>Webhook URL、加签密钥</td></tr>
          <tr><td><b>飞书</b></td><td>Webhook URL、加签密钥</td></tr>
          <tr><td><b>邮箱</b></td><td>SMTP 服务器、端口、发件人邮箱、授权码、收件人邮箱</td></tr>
          <tr><td><b>消息推送</b></td><td>推送内容模板、推送频率（实时 / 每小时 / 每天 / 每周）、推送人群</td></tr>
        </tbody>
      </table>
      <div class="callout callout-warn">
        <h4>邮箱要填「授权码」不是登录密码</h4>
        <p>多数邮箱服务商要求使用 SMTP 授权码而非账号登录密码，填写错误会导致推送静默失败。
        配置后建议先在套件上手动跑一次，确认能收到通知。</p>
      </div>
      <div class="callout callout-info">
        <h4>项目级开关与套件级开关叠加生效</h4>
        <p>只有「项目设置里配好了渠道」且「套件上的『执行完是否推送消息』处于开启」时，
        执行完成才会真正发出通知。只配了一边是不会推的。</p>
      </div>
    `
  },

  'project-tools': {
    description: '63 个离线小工具，覆盖造数据、转格式、算签名、写定时表达式',
    anchors: [
      { id: 'sub-tools-groups', title: '六大工具分组' },
      { id: 'sub-tools-how', title: '使用方式' },
      { id: 'sub-tools-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-tools-groups">六大工具分组</h3>
      <table class="doc-table">
        <thead><tr><th style="width:170px">分组</th><th>代表工具</th></tr></thead>
        <tbody>
          <tr><td><b>测试数据生成</b></td><td>中文姓名、手机号、邮箱地址、地址信息、公司名称、营业执照号、统一社会信用代码、身份证正反面、银行卡号、证件号、经纬度坐标、用户档案、随机字符串、UUID、MAC地址、IP地址、随机日期</td></tr>
          <tr><td><b>JSON 处理</b></td><td>JSON 格式化、JSON 校验、JSON 对比增强、JSONPath 查询、JSON 扁平化、JSON 路径列表、JSON 转 XML、XML 转 JSON、JSON 转 YAML、YAML 转 JSON</td></tr>
          <tr><td><b>编码转换</b></td><td>条形码、二维码、二维码解析、时间戳转换、进制转换、Unicode 转换、ASCII 转换、颜色转换、URL 编码、JWT 解析、Base64 编码、图片转 Base64、Base64 转图片</td></tr>
          <tr><td><b>加密哈希</b></td><td>MD5、SHA-1、SHA-256、SHA-512、哈希对比、AES 加密、AES 解密、密码强度、生成盐值</td></tr>
          <tr><td><b>字符串处理</b></td><td>文本对比、正则测试、去除空格、字符替换、字符转义/反转义、字数统计、大小写转换、文本格式化</td></tr>
          <tr><td><b>定时任务</b></td><td>生成 Cron 表达式、解析表达式、下次执行时间、验证表达式</td></tr>
        </tbody>
      </table>

      <h3 id="sub-tools-how">使用方式</h3>
      <ol class="step-list">
        <li><h4>1. 选择工具</h4><p>在工具卡片网格中按分组浏览，或用顶部搜索框按工具名、描述搜索。</p></li>
        <li><h4>2. 点开弹窗</h4><p>点击卡片打开该工具的弹窗，填入输入，结果实时或点击按钮后生成。</p></li>
        <li><h4>3. 复制结果</h4><p>复制生成结果，粘贴到接口配置或用例参数中。</p></li>
      </ol>

      <h3 id="sub-tools-rules">注意事项</h3>
      <div class="callout callout-tip">
        <h4>造压测与联调数据很方便</h4>
        <p>「测试数据生成」分组里的数据是本地合成、不走网络，可以批量生成。
        做参数化压测需要大量唯一数据时，建议先用这里的工具生成，再导入文件管理作为数据文件。</p>
      </div>
      <div class="callout callout-warn">
        <h4>加密类工具用于对拍，不要用于生产密钥</h4>
        <p>AES 加解密、哈希类工具适合做「签名算得对不对」的对拍与联调。
        真实业务密钥不要在工具页面长期留存或传播。</p>
      </div>
      <div class="callout callout-info">
        <h4>Cron 表达式可直接用于定时任务</h4>
        <p>「生成 Cron 表达式」产出的表达式可直接填进<b>执行中心 → 定时任务</b>的定时策略字段。</p>
      </div>
    `
  },

  'project-auditLog': {
    description: '平台关键操作的可追溯记录',
    anchors: [
      { id: 'sub-audit-what', title: '记录内容' },
      { id: 'sub-audit-how', title: '典型用法' }
    ],
    content: `
      <h3 id="sub-audit-what">记录内容</h3>
      <p>审计日志记录平台内发生的关键操作，一般包含：操作时间、操作人、操作对象（哪个模块的哪条数据）、
      操作类型（新增 / 修改 / 删除等）。用于回答「这条配置是谁在什么时候改的」。</p>

      <h3 id="sub-audit-how">典型用法</h3>
      <table class="doc-table">
        <thead><tr><th style="width:230px">场景</th><th>怎么查</th></tr></thead>
        <tbody>
          <tr><td>用例突然大面积失败，怀疑有人改了断言</td><td>按时间范围倒查，定位到改动用例的时间点与操作人</td></tr>
          <tr><td>环境域名被改，导致请求打到错误环境</td><td>查环境配置相关的修改记录</td></tr>
          <tr><td>某条用例 / 接口不见了</td><td>查删除记录，确认是被删除还是被改名</td></tr>
          <tr><td>做操作合规回查</td><td>按操作人筛选，汇总其在一段时间内的操作</td></tr>
        </tbody>
      </table>
      <div class="callout callout-info">
        <h4>排障顺序建议</h4>
        <p>遇到「昨天还好今天全挂」这类问题，先看<b>报告管理 → 日志列表</b>确认失败现象，
        再用<b>审计日志</b>回查配置是否被改动。两条线结合能快速区分「代码问题」还是「配置被人改了」。</p>
      </div>
    `
  },

  /* ================= 用户管理 ================= */
  'user-userList': {
    description: '平台用户的增删改、状态管理与角色分配',
    anchors: [
      { id: 'sub-userList-fields', title: '字段说明' },
      { id: 'sub-userList-how', title: '操作步骤' },
      { id: 'sub-userList-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-userList-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>用户名</b></td><td>登录标识</td></tr>
          <tr><td><b>邮箱</b></td><td>用于通知与标识</td></tr>
          <tr><td><b>状态</b></td><td>启用 / 停用，停用后无法登录</td></tr>
          <tr><td><b>角色</b></td><td>决定该用户能看到哪些菜单、能做什么操作</td></tr>
          <tr><td><b>密码</b></td><td>新增时设置，后续可通过「重置密码」修改</td></tr>
        </tbody>
      </table>

      <h3 id="sub-userList-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新增用户</h4><p>点击「新增」，填写用户名、邮箱、密码，勾选角色后保存。</p></li>
        <li><h4>2. 分配 / 调整角色</h4><p>编辑用户，在角色项中勾选或取消角色。</p></li>
        <li><h4>3. 停用用户</h4><p>编辑用户把状态置为停用。离职或临时账号用这个方式最稳妥。</p></li>
        <li><h4>4. 重置密码</h4><p>用户忘记密码时由管理员重置，重置后请提醒用户尽快自行修改。</p></li>
        <li><h4>5. 删除用户</h4><p>确认该用户已无未交接的数据后再删除。</p></li>
      </ol>

      <h3 id="sub-userList-rules">注意事项</h3>
      <div class="callout callout-warn">
        <h4>改权限后要重新登录</h4>
        <p>角色调整不会实时作用于已登录会话，需要用户<b>重新登录</b>后新权限才生效。
        不要因为「改完没反应」而反复修改。</p>
      </div>
      <div class="callout callout-tip">
        <h4>优先停用而不是删除</h4>
        <p>删除用户可能影响其创建过的用例负责人、缺陷处理人等字段的展示。
        人员变动建议先「停用」，保留历史可追溯性。</p>
      </div>
    `
  },

  'user-roleList': {
    description: '角色定义与权限点勾选',
    anchors: [
      { id: 'sub-roleList-fields', title: '字段说明' },
      { id: 'sub-roleList-how', title: '操作步骤' },
      { id: 'sub-roleList-builtin', title: '内置角色' }
    ],
    content: `
      <h3 id="sub-roleList-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:170px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>角色名称</b></td><td>项目内唯一，建议按职责命名（如「测试工程师」「只读观察者」）</td></tr>
          <tr><td><b>权限点</b></td><td>与菜单一一对应的权限项，每项可单独勾选下面 5 个开关</td></tr>
          <tr><td><b>has_permission</b></td><td>菜单是否可见</td></tr>
          <tr><td><b>has_read_permission</b></td><td>是否可查看</td></tr>
          <tr><td><b>has_add_permission</b></td><td>是否可新增</td></tr>
          <tr><td><b>has_edit_permission</b></td><td>是否可编辑</td></tr>
          <tr><td><b>has_delete_permission</b></td><td>是否可删除</td></tr>
        </tbody>
      </table>

      <h3 id="sub-roleList-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新建角色</h4><p>点击「新增」或「创建角色」，填写角色名称。</p></li>
        <li><h4>2. 勾选权限</h4><p>在权限树中按模块展开，逐项勾选。可先整模块勾「可见 + 只读」，再对需要维护的模块补新增 / 编辑 / 删除。</p></li>
        <li><h4>3. 保存并分配</h4><p>保存后到<b>用户列表</b>把该角色分配给对应用户。</p></li>
        <li><h4>4. 验证</h4><p>用被授权账号重新登录，确认菜单与按钮显示符合预期。</p></li>
      </ol>

      <h3 id="sub-roleList-builtin">内置角色</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">角色</th><th>权限范围</th></tr></thead>
        <tbody>
          <tr><td><b>全部权限</b></td><td>所有权限点的 5 个开关全部开启</td></tr>
          <tr><td><b>只读权限</b></td><td>仅「可见 + 查看」，不可新增 / 编辑 / 删除</td></tr>
        </tbody>
      </table>
      <p>这两个角色在平台初始化时自动创建，可直接使用，也可作为新建角色的参考模板。</p>
      <div class="callout callout-warn">
        <h4>超级管理员角色不可改</h4>
        <p>超级管理员拥有全部权限且不能被修改或删除。请勿试图通过编辑该角色来收紧管理员权限。</p>
      </div>
    `
  },

  'user-permissionList': {
    description: '平台权限点总览——核对权限覆盖面的地方',
    anchors: [
      { id: 'sub-perm-what', title: '权限点与菜单的关系' },
      { id: 'sub-perm-how', title: '典型用法' }
    ],
    content: `
      <h3 id="sub-perm-what">权限点与菜单的关系</h3>
      <p>权限点表与平台菜单是<b>一一对应</b>的两级结构，每个权限点记录了名称、图标、跳转路径与层级：
      一级权限点对应左侧模块，二级权限点对应模块下的页面。因此这份列表同时也是「平台有哪些功能」的权威清单。</p>
      <table class="doc-table">
        <thead><tr><th style="width:130px">模块</th><th>包含的权限点（页面）</th></tr></thead>
        <tbody>
          <tr><td><b>环境管理</b></td><td>环境配置、服务配置、产品配置、数据库配置</td></tr>
          <tr><td><b>公共资源</b></td><td>文件管理、元素配置、常量配置、用户函数、步骤管理</td></tr>
          <tr><td><b>测试资产</b></td><td>向量智仓、标签管理、接口管理、功能用例、脚本用例</td></tr>
          <tr><td><b>执行中心</b></td><td>测试计划、套件管理、定时任务</td></tr>
          <tr><td><b>报告管理</b></td><td>日志列表、功能报告、性能报告</td></tr>
          <tr><td><b>缺陷管理</b></td><td>缺陷列表</td></tr>
        </tbody>
      </table>

      <h3 id="sub-perm-how">典型用法</h3>
      <table class="doc-table">
        <thead><tr><th style="width:250px">场景</th><th>怎么做</th></tr></thead>
        <tbody>
          <tr><td>某菜单不显示，想知道是权限还是 Bug</td><td>先在这里确认该权限点存在且名称正确，再去角色核对该角色是否勾了「可见」</td></tr>
          <tr><td>新建角色时不知道平台一共多少功能</td><td>用这份列表当勾选清单，逐项过一遍，避免漏授权</td></tr>
          <tr><td>页面提示无权限但菜单可见</td><td>菜单可见只说明勾了 has_permission；请再确认对应的读 / 增 / 改 / 删开关</td></tr>
        </tbody>
      </table>
      <div class="callout callout-tip">
        <h4>排障顺序</h4>
        <p>菜单 / 按钮异常时的判断顺序：<b>权限列表确认权限点存在</b> → <b>角色列表确认开关已勾</b> →
        <b>用户列表确认角色已分配</b> → <b>让用户重新登录</b>。四步都过了还异常，才可能是平台问题。</p>
      </div>
    `
  },

  /* ================= 环境管理 ================= */
  'env-envConfig': {
    description: '建环境并把服务、平台、数据库绑成一套可执行的环境',
    anchors: [
      { id: 'sub-env-fields', title: '字段说明' },
      { id: 'sub-env-how', title: '操作步骤' },
      { id: 'sub-env-script', title: '前置 / 后置脚本与环境变量' },
      { id: 'sub-env-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-env-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:190px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>环境名称</b></td><td>全局唯一，≤20 字。建议 <code>系统名-环境</code> 形式</td></tr>
          <tr><td><b>服务</b>（多选）</td><td>勾选本环境要用的后端服务，并为每个服务填<b>服务域名</b>（如 <code>http://172.16.21.141:8000</code>）</td></tr>
          <tr><td><b>平台</b>（多选）</td><td>勾选前端平台，填 <b>WEB 平台域名</b>（WEB 类）、<b>APP 包名</b>与 <b>APP 主页面入口名</b>（APP 类）</td></tr>
          <tr><td><b>数据库</b>（多选）</td><td>勾选数据库资源，并在环境侧填写地址、用户名、密码、端口、库名与类型</td></tr>
          <tr><td><b>前置 Python 脚本</b></td><td>setup，本环境下每次执行前运行</td></tr>
          <tr><td><b>后置 Python 脚本</b></td><td>teardown，本环境下每次执行后运行</td></tr>
          <tr><td><b>环境全局变量</b></td><td>该环境专属的变量（名称 / 值 / 备注），用例中以 <code>\${名称}</code> 引用</td></tr>
        </tbody>
      </table>

      <h3 id="sub-env-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 准备资源</h4><p>先到<b>服务配置 / 产品配置 / 数据库配置</b>把要用到的服务、平台、数据库建好。</p></li>
        <li><h4>2. 新建环境</h4><p>点击「新增」，填写环境名称，选择所属项目。</p></li>
        <li><h4>3. 绑定服务</h4><p>勾选服务并逐个填入域名。域名要带协议头，末尾不要多写斜杠，避免拼出 <code>//</code>。</p></li>
        <li><h4>4. 绑定平台（可选）</h4><p>只做接口测试可跳过；做 UI 自动化必须绑定，并填对 WEB 域名或 APP 包名 / 入口名。</p></li>
        <li><h4>5. 绑定数据库（可选）</h4><p>需要数据库校验或数据准备的用例必须绑定。类型可选：
        <span class="badge">MySQL</span><span class="badge">PostgreSQL</span><span class="badge">REDIS</span><span class="badge">Oracle</span><span class="badge">达梦8</span>。</p></li>
        <li><h4>6. 保存并验证</h4><p>保存后，找一条已知可用的接口用例，选该环境跑一次，确认请求能通。</p></li>
      </ol>

      <h3 id="sub-env-script">前置 / 后置脚本与环境变量</h3>
      <p>环境级脚本用于放置「每次执行都要做」的公共动作：</p>
      <table class="doc-table">
        <thead><tr><th style="width:130px">脚本</th><th>典型用途</th></tr></thead>
        <tbody>
          <tr><td><b>setup</b></td><td>登录预置 Token、准备基础数据、设置全局变量</td></tr>
          <tr><td><b>teardown</b></td><td>清理本次执行产生的数据、释放资源</td></tr>
        </tbody>
      </table>
      <div class="callout callout-tip">
        <h4>环境变量是跨环境复用用例的关键</h4>
        <p>把账号、租户号、密钥这类「随环境不同而不同」的值放进<b>环境全局变量</b>，
        用例里统一写 <code>\${变量名}</code>。这样同一份用例在测试环境和预发环境都能直接跑，不用复制两份。</p>
      </div>

      <h3 id="sub-env-rules">注意事项</h3>
      <div class="callout callout-warn">
        <h4>环境没绑齐，用例就跑不通</h4>
        <p>请记住这条因果链：</p>
        <p>没绑<b>服务域名</b> → 接口请求解析不到主机（压测会直接报「未解析到任何目标主机」）。</p>
        <p>没绑<b>数据库</b> → 数据库操作步骤无法执行。</p>
        <p>没绑<b>平台</b> → UI 自动化步骤无法执行。</p>
        <p>排查接口失败时，请先确认当前选的这个环境把这些资源都绑了。</p>
      </div>
      <div class="callout callout-warn">
        <h4>环境被引用时不可删除</h4>
        <p>已被套件、定时任务或报告引用的环境无法直接删除，需先解除引用。</p>
      </div>
    `
  },

  'env-serviceConfig': {
    description: '后端服务与服务模块树——接口、用例、缺陷共同的归类维度',
    anchors: [
      { id: 'sub-service-fields', title: '字段说明' },
      { id: 'sub-service-module', title: '服务模块' },
      { id: 'sub-service-how', title: '操作步骤' },
      { id: 'sub-service-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-service-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:200px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>服务名称</b></td><td>后端微服务名，建议与网关路由前缀一致，便于对照</td></tr>
          <tr><td><b>接口请求是否跟随服务</b></td><td>开启后，接口请求地址按「服务域名 + 接口路径」自动拼接</td></tr>
          <tr><td><b>所属项目</b></td><td>服务归属的项目</td></tr>
        </tbody>
      </table>

      <h3 id="sub-service-module">服务模块</h3>
      <p>服务下可建<b>服务模块</b>，支持父子层级（模块树）。模块是平台最重要的归类维度之一，
      以下对象都挂在模块上：</p>
      <ul>
        <li>接口（接口管理）</li>
        <li>功能用例（功能用例）</li>
        <li>脚本用例（脚本用例）</li>
        <li>缺陷（缺陷列表）</li>
        <li>用户函数与常量（公共资源）</li>
      </ul>
      <p>因此模块划分要一次想清楚：按业务域划分（如「登录」「订单」「支付」）通常比按接口技术分组更好用。</p>

      <h3 id="sub-service-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新建服务</h4><p>点击「新增」，填写服务名称，按需勾选「接口请求是否跟随服务」。</p></li>
        <li><h4>2. 建服务模块</h4><p>在服务下展开模块区域，新建一级模块；如需二级，选中父模块后新建子模块。</p></li>
        <li><h4>3. 在环境里绑定服务并填域名</h4><p>到<b>环境配置</b>勾选该服务，填入本环境的服务域名。</p></li>
        <li><h4>4. 新建接口时选择服务与模块</h4><p>接口管理新增接口时，所属服务与模块都取自这里。</p></li>
      </ol>

      <h3 id="sub-service-rules">注意事项</h3>
      <div class="callout callout-warn">
        <h4>本平台使用「服务模块」而非「模块」</h4>
        <p>平台里有两套容易混淆的对象：<b>服务模块</b>（挂在服务下，服务于接口与用例的归类）
        与<b>模块</b>（挂在组织维度上）。帮助文档与界面中提到「所属模块」时，
        接口、功能用例、脚本用例、缺陷用的都是<b>服务模块</b>。建数据时请到「服务配置」下建，
        不要在别处找。</p>
      </div>
      <div class="callout callout-info">
        <h4>被引用的服务与模块不可删</h4>
        <p>服务一旦被环境绑定，模块一旦被接口 / 用例 / 缺陷引用，删除会被拒绝。
        要删请先到引用方解除依赖。</p>
      </div>
    `
  },

  'env-plantConfig': {
    description: '前端平台（WEB / APP / H5 / 小程序 / 桌面端）的资源定义',
    anchors: [
      { id: 'sub-plant-fields', title: '字段说明' },
      { id: 'sub-plant-how', title: '操作步骤' },
      { id: 'sub-plant-rules', title: '什么时候才需要配' }
    ],
    content: `
      <h3 id="sub-plant-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:200px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>平台名称</b></td><td>前端平台标识，如「支付平台-Web」「支付App-Android」</td></tr>
          <tr><td><b>平台类型</b></td><td>
            <span class="badge">WEB</span>
            <span class="badge">PHONE_APP</span>
            <span class="badge">H5</span>
            <span class="badge">MINI</span>
            <span class="badge">DESKTOP_APP</span>
          </td></tr>
        </tbody>
      </table>
      <p>环境侧绑定平台时需要补充的字段：</p>
      <table class="doc-table">
        <thead><tr><th style="width:190px">字段</th><th>适用类型</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>WEB 平台域名</b></td><td>WEB / H5</td><td>被测前端首页地址</td></tr>
          <tr><td><b>APP 包名</b></td><td>APP / 小程序</td><td>应用包名，供 Appium 启动</td></tr>
          <tr><td><b>APP 主页面入口名</b></td><td>APP</td><td>主 Activity，供 Appium 拉起应用</td></tr>
        </tbody>
      </table>

      <h3 id="sub-plant-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新建平台</h4><p>填写平台名称并选择平台类型。</p></li>
        <li><h4>2. 环境绑定</h4><p>到<b>环境配置</b>勾选该平台，按类型填入域名或包名 / 入口名。</p></li>
        <li><h4>3. 建元素与 UI 步骤</h4><p>到<b>元素配置</b>建页面元素，在脚本用例中用 Web / App 自动化步骤引用。</p></li>
      </ol>

      <h3 id="sub-plant-rules">什么时候才需要配</h3>
      <div class="callout callout-info">
        <h4>只做接口测试可以不配</h4>
        <p>平台 / 产品配置只服务于 UI 自动化（Web 与 App 步骤）。如果团队当前只做接口与性能测试，
        这一项可以完全不配置，不影响接口用例的执行。</p>
      </div>
      <div class="callout callout-warn">
        <h4>UI 自动化还需执行器节点</h4>
        <p>真正跑 Web / App 自动化还需要在环境侧配置<b>执行机节点</b>（Web 执行器 / App 执行器），
        并在套件中选择对应的执行器。相关配置在环境管理的执行机配置中维护。</p>
      </div>
    `
  },

  'env-dbConfig': {
    description: '数据库资源定义与环境侧连接信息',
    anchors: [
      { id: 'sub-db-fields', title: '字段说明' },
      { id: 'sub-db-how', title: '操作步骤' },
      { id: 'sub-db-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-db-fields">字段说明</h3>
      <p>数据库分两层：资源层只定义名称，连接信息在环境侧填写，从而支持同一数据库在不同环境连不同实例。</p>
      <table class="doc-table">
        <thead><tr><th style="width:190px">字段</th><th>所在层</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>数据库名称</b></td><td>资源定义</td><td>如「支付核心库」「达梦主库」</td></tr>
          <tr><td><b>数据库地址</b></td><td>环境绑定</td><td>IP 或主机名</td></tr>
          <tr><td><b>数据库用户名</b></td><td>环境绑定</td><td>要有目标表的查询权限；做数据准备时需写权限</td></tr>
          <tr><td><b>数据库密码</b></td><td>环境绑定</td><td>—</td></tr>
          <tr><td><b>数据库端口号</b></td><td>环境绑定</td><td>MySQL 3306 / PostgreSQL 5432 / Redis 6379 / Oracle 1521 / 达梦 5236</td></tr>
          <tr><td><b>连接的数据库名</b></td><td>环境绑定</td><td>目标 schema / database 名</td></tr>
          <tr><td><b>数据库类型</b></td><td>环境绑定</td><td>
            <span class="badge">MySQL</span>
            <span class="badge">PostgreSQL</span>
            <span class="badge">REDIS</span>
            <span class="badge">Oracle</span>
            <span class="badge">达梦8</span>
          </td></tr>
        </tbody>
      </table>

      <h3 id="sub-db-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新建数据库资源</h4><p>填写数据库名称并保存。</p></li>
        <li><h4>2. 在环境里绑定并填连接信息</h4><p>到<b>环境配置</b>勾选该数据库，填写地址、账号、密码、端口、库名与类型。</p></li>
        <li><h4>3. 建数据库操作步骤</h4><p>到<b>公共资源 → 步骤管理</b>新建步骤，类型选<b>数据库操作</b>，选择要用的数据库，填写 SQL。</p></li>
        <li><h4>4. 在用例中引用并执行</h4><p>脚本用例中添加「数据库操作」步骤，或在「引用已有步骤」中选择刚建好的步骤。</p></li>
      </ol>

      <h3 id="sub-db-rules">注意事项</h3>
      <div class="callout callout-warn">
        <h4>被环境绑定的数据库不可删除</h4>
        <p>平台对数据库做了引用保护：已被某个环境绑定的数据库无法删除，
        需先在所有环境中解除绑定。</p>
      </div>
      <div class="callout callout-tip">
        <h4>数据校验的两条思路</h4>
        <p><b>接口层校验</b>：直接用请求步骤断言返回体，快、不依赖库表结构。</p>
        <p><b>库层校验</b>：用数据库操作步骤查库核对，能验证落库是否正确、字段是否按预期写入。
        涉及资金、状态流转等关键数据，建议两层都做。</p>
      </div>
      <div class="callout callout-warn">
        <h4>数据准备步骤要可重复执行</h4>
        <p>用 SQL 做数据准备时，建议写成「先删后插」或使用唯一键避免冲突，
        否则第二次执行会因主键重复而报错，造成「跑一次成功、跑两次失败」的假象。</p>
      </div>
    `
  }
}

export default basicsChildren
