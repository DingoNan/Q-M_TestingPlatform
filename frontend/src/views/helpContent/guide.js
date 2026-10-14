/**
 * 帮助文档 · 平台指南：AI 助手 / 变量引用语法 / 常见问题与避坑
 */

export const guideChildren = {
  'guide-ai': {
    description: 'AI 助手的入口、前置条件与全部 AI 能力清单',
    anchors: [
      { id: 'sub-ai-entry', title: '入口在哪' },
      { id: 'sub-ai-prepare', title: '使用前置条件' },
      { id: 'sub-ai-capability', title: 'AI 能力清单' },
      { id: 'sub-ai-workflow', title: '一次完整的 AI 生成流程' },
      { id: 'sub-ai-rules', title: '使用建议与边界' }
    ],
    content: `
      <h3 id="sub-ai-entry">入口在哪</h3>
      <p>AI 助手是一个固定在页面<b>右下角的圆形悬浮按钮</b>——<b>只有图标、没有文字</b>，
      带一点脉冲动效，容易被忽略。它出现在已进入项目的页面中，例如：</p>
      <ul>
        <li>项目主页（项目概览）</li>
        <li>功能用例列表</li>
        <li>元素配置列表</li>
        <li>脚本用例列表</li>
      </ul>
      <p>点击后展开全屏「AI助手」面板，包含三部分：<b>选择模型</b>、<b>会话区</b>、
      <b>快速动作</b>（AI生成功能测试用例 / AI生成元素）。按钮支持拖动，拖动后会记住位置。</p>

      <h3 id="sub-ai-prepare">使用前置条件</h3>
      <table class="doc-table">
        <thead><tr><th style="width:60px">序号</th><th style="width:240px">条件</th><th>不满足时的表现</th></tr></thead>
        <tbody>
          <tr><td>1</td><td>已经从「我的项目」<b>进入项目</b></td><td>悬浮按钮根本不出现；或菜单缺失</td></tr>
          <tr><td>2</td><td>项目设置中已配置并启用 <b>AI 供应商</b></td><td>面板里模型列表为空，「选择模型」无内容</td></tr>
          <tr><td>3</td><td>已在面板中<b>选择模型</b></td><td>发送按钮为灰色不可点（这是最容易卡住的一步）</td></tr>
          <tr><td>4</td><td>已选择<b>目标模块</b>（生成用例类动作）</td><td>生成结果无法落库或落到错误模块</td></tr>
        </tbody>
      </table>
      <div class="callout callout-warn">
        <h4>发送按钮点不动怎么办</h4>
        <p>按顺序排查：①是否已进入项目 → ②面板顶部是否已「选择模型」 →
        ③模型列表是否为空 → 为空则到<b>项目设置 → AI 供应商</b>配置 API Key 并启用。这三步能覆盖绝大多数情况。</p>
      </div>

      <h3 id="sub-ai-capability">AI 能力清单</h3>
      <table class="doc-table">
        <thead><tr><th style="width:200px">能力</th><th>入口位置</th><th>产出</th></tr></thead>
        <tbody>
          <tr><td><b>AI 生成功能测试用例</b></td><td>AI 助手快速动作 / 功能用例列表</td><td>功能用例（自动保存，标记 <code>case_mark='AI生成'</code>）</td></tr>
          <tr><td><b>AI 生成元素</b></td><td>AI 助手快速动作 / 元素配置 → AI 生成</td><td>页面元素与定位方式</td></tr>
          <tr><td><b>AI 生成场景脚本</b></td><td>功能用例列表 → AI 生成脚本</td><td>脚本用例骨架（步骤序列）</td></tr>
          <tr><td><b>AI 生成配置</b></td><td>接口管理 → 编辑接口 → AI 生成配置</td><td>请求头 / 请求体 / 返回体结构</td></tr>
        </tbody>
      </table>
      <p>生成类任务均为<b>后台异步执行</b>：提交后页面会显示生成中状态，完成后把结果写回数据库，
      无需停留在页面等待。用例类结果完成后会提示「已生成 N 条用例（已自动保存）」。</p>

      <h3 id="sub-ai-workflow">一次完整的 AI 生成流程</h3>
      <ol class="step-list">
        <li><h4>1. 进入项目</h4><p>到我的项目点击目标项目的「进入」。</p></li>
        <li><h4>2. 补充知识上下文（推荐）</h4><p>把需求文档、接口文档上传到<b>测试资产 → 向量智仓</b>，
        AI 生成时会检索这些内容，产出更贴合本项目。</p></li>
        <li><h4>3. 确保模块已建好</h4><p>生成用例需要选择所属模块，请先在<b>环境管理 → 服务配置</b>下建好服务模块。</p></li>
        <li><h4>4. 打开 AI 助手并选模型</h4><p>点击右下角悬浮按钮，在面板顶部选择模型。</p></li>
        <li><h4>5. 发起生成</h4><p>用快速动作「AI生成功能测试用例」，或在输入框描述你的测试目标（模块、业务点、要覆盖的场景）。</p></li>
        <li><h4>6. 等待后台完成</h4><p>生成结果自动落库，可在提示中看到生成条数。</p></li>
        <li><h4>7. 筛选并复核</h4><p>到功能用例列表按 <code>AI生成</code> 标记筛选，逐条核对字段、步骤与预期结果。</p></li>
        <li><h4>8. 修正并推进状态</h4><p>修正后把用例状态从「待修改」推进到「待评审」→「已评审」。</p></li>
      </ol>

      <h3 id="sub-ai-rules">使用建议与边界</h3>
      <div class="callout callout-tip">
        <h4>描述得越具体，产出越可用</h4>
        <p>与其说「生成登录的用例」，不如说「针对登录模块生成用例：覆盖账号密码正确、密码错误、
        账号不存在、连续错误 5 次锁定、验证码过期、密码含特殊字符、超长密码」。
        把边界条件直接说清楚，比事后再补要省事得多。</p>
      </div>
      <div class="callout callout-warn">
        <h4>AI 产出是初稿，不是终稿</h4>
        <p>常见问题：遗漏业务特有的边界值、引用了不存在的字段、把接口返回结构写错、
        步骤不可执行（缺少前置登录）。因此<b>所有 AI 生成的资产都必须人工复核</b>后才能用于回归。
        建议统一用 <code>AI生成</code> 标记筛出来集中评审。</p>
      </div>
      <div class="callout callout-info">
        <h4>密钥与敏感信息</h4>
        <p>AI 供应商的 API Key 保存在项目设置中。请不要在对话内容里粘贴生产环境的密钥、
        真实用户隐私数据或内部敏感信息。</p>
      </div>
    `
  },

  'guide-vars': {
    description: '变量引用语法大全：写法、取值来源、优先级与排错',
    anchors: [
      { id: 'sub-var-basic', title: '基本语法' },
      { id: 'sub-var-scope', title: '变量的四个来源与作用域' },
      { id: 'sub-var-const', title: '引用常量' },
      { id: 'sub-var-where', title: '哪些地方可以引用' },
      { id: 'sub-var-debug', title: '排错方法' },
      { id: 'sub-var-pitfall', title: '常见坑' }
    ],
    content: `
      <h3 id="sub-var-basic">基本语法</h3>
      <p>变量引用统一写成 <code>\${变量名}</code>。引擎在执行时用正则匹配
      <code>\${...}</code> 并把内容替换为实际值，替换发生在 URL、请求方法、请求头、
      请求体（JSON / Form-data）、查询参数与断言的取值上。</p>
      <table class="doc-table">
        <thead><tr><th style="width:280px">写法</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><code>\${Token}</code></td><td>引用名为 Token 的变量</td></tr>
          <tr><td><code>Bearer \${Token}</code></td><td>可以嵌在字符串中间，替换后拼接</td></tr>
          <tr><td><code>\${OrderStatus.PAID}</code></td><td>点号形式：优先按执行上下文的字段路径解析；解析不到则去常量表查找</td></tr>
        </tbody>
      </table>
      <div class="callout callout-info">
        <h4>变量名区分大小写</h4>
        <p><code>\${Token}</code> 与 <code>\${token}</code> 是两个不同的变量。命名请保持前后一致，
        建议统一用首字母大写的驼峰（如 <code>Token</code>、<code>OrderId</code>）。</p>
      </div>

      <h3 id="sub-var-scope">变量的四个来源与作用域</h3>
      <table class="doc-table">
        <thead><tr><th style="width:180px">来源</th><th>作用域</th><th>典型用途</th></tr></thead>
        <tbody>
          <tr><td><b>环境全局变量</b></td><td>该环境下的所有用例</td><td>账号、租户号、随环境变化的值</td></tr>
          <tr><td><b>用例全局变量设置</b></td><td>该用例下的所有步骤</td><td>该用例特有的固定值与初始值</td></tr>
          <tr><td><b>步骤变量参数</b></td><td>该步骤内</td><td>仅本步骤的参数覆盖</td></tr>
          <tr><td><b>步骤提取结果</b></td><td>提取之后的步骤</td><td>上游接口返回的 token、ID、流水号</td></tr>
        </tbody>
      </table>
      <p>执行时的查找顺序：<b>先按执行上下文查找</b>（步骤提取结果、用例变量、环境变量等），
      查不到才转向<b>常量表</b>匹配。</p>
      <div class="callout callout-warn">
        <h4>只能向后引用</h4>
        <p>变量的可见性是单向的——只能引用<b>当前步骤之前</b>已经赋值（提取 / 声明）的变量。
        第 2 步无法引用第 5 步才会产生的值。若执行时报「参数解析失败」，
        请先确认该变量在那个时点是否已经存在。</p>
      </div>

      <h3 id="sub-var-const">引用常量</h3>
      <p>常量在<b>公共资源 → 常量配置</b>中定义，由「常量类名 + 常量项名」两级构成：</p>
      <table class="doc-table">
        <thead><tr><th style="width:180px">配置</th><th>示例</th></tr></thead>
        <tbody>
          <tr><td>常量类名（唯一）</td><td><code>OrderStatus</code></td></tr>
          <tr><td>常量项 name</td><td><code>PAID</code> / <code>SHIPPED</code> / <code>CLOSED</code></td></tr>
          <tr><td>常量项 value</td><td><code>1</code> / <code>2</code> / <code>9</code></td></tr>
          <tr><td>用例中引用</td><td><code>\${OrderStatus.PAID}</code> → 替换为 <code>1</code></td></tr>
        </tbody>
      </table>

      <h3 id="sub-var-where">哪些地方可以引用</h3>
      <table class="doc-table">
        <thead><tr><th style="width:200px">位置</th><th>是否支持</th><th>典型用法</th></tr></thead>
        <tbody>
          <tr><td>请求地址（含路径参数）</td><td>支持</td><td><code>/order/\${OrderId}</code></td></tr>
          <tr><td>请求头</td><td>支持</td><td><code>Authorization: Bearer \${Token}</code></td></tr>
          <tr><td>请求体 JSON 字段值</td><td>支持</td><td><code>"userId": "\${UserId}"</code></td></tr>
          <tr><td>Form-data 字段值</td><td>支持</td><td><code>amount=\${Amount}</code></td></tr>
          <tr><td>查询参数</td><td>支持</td><td><code>pageSize=\${PageSize}</code></td></tr>
          <tr><td>断言期望值</td><td>支持</td><td>断言 <code>\${resp.code}</code> 等于 <code>0</code></td></tr>
          <tr><td>数据库操作 SQL</td><td>支持</td><td><code>WHERE order_id = '\${OrderId}'</code></td></tr>
        </tbody>
      </table>

      <h3 id="sub-var-debug">排错方法</h3>
      <div class="flow">
        <div class="flow-step"><span class="flow-idx">1</span><b>看日志定位步骤</b><p>在日志列表找到报参数解析失败的那一步</p></div>
        <div class="flow-step"><span class="flow-idx">2</span><b>看变量名</b><p>报错信息里会带上没解析成功的表达式，对照实际变量名与大小写</p></div>
        <div class="flow-step"><span class="flow-idx">3</span><b>看请求体原文</b><p>若日志里请求体还含 <code>\${...}</code> 原文，说明该变量此时无值</p></div>
        <div class="flow-step"><span class="flow-idx">4</span><b>往前找赋值</b><p>确认该变量是否被前置步骤正确提取、变量名是否完全一致</p></div>
        <div class="flow-step"><span class="flow-idx">5</span><b>核对常量表</b><p>点号形式引用失败时，确认常量类与常量项确实存在</p></div>
      </div>

      <h3 id="sub-var-pitfall">常见坑</h3>
      <table class="doc-table">
        <thead><tr><th style="width:60px">序号</th><th style="width:250px">坑</th><th>说明与对策</th></tr></thead>
        <tbody>
          <tr><td>1</td><td>变量名为 <code>stepResponse.N</code> 形态时解析异常</td><td>点号形式的引用会先按字段路径解析，再回落常量表。若既不是上下文字段、也不是常量项，就会抛解析失败。建议把响应字段<b>显式提取</b>成命名清晰的变量（如 <code>Token</code>）再引用，而不是直接引深层路径</td></tr>
          <tr><td>2</td><td>常量类名与变量名撞名</td><td>上下文优先于常量。若同名，实际取到的是上下文中那个值，与预期不符。常量类名请加业务前缀</td></tr>
          <tr><td>3</td><td>大小写不一致</td><td><code>\${token}</code> 与 <code>\${Token}</code> 不等价</td></tr>
          <tr><td>4</td><td>跨步骤向前引用</td><td>引用尚未赋值的变量必然失败，检查步骤顺序</td></tr>
          <tr><td>5</td><td>常量项名拼错</td><td>报参数解析失败；逐字核对常量配置里的 <code>name</code></td></tr>
          <tr><td>6</td><td>在非支持字段里写变量</td><td>变量只在请求与断言的取值上替换，不要写在字段名或结构层级上</td></tr>
          <tr><td>7</td><td>环境变量与用例变量同名</td><td>建议加前缀区分（环境用 <code>env_</code>，用例用 <code>case_</code>），避免覆盖造成混乱</td></tr>
        </tbody>
      </table>
    `
  },

  'guide-recording': {
    description: '把网页操作变成 Web 自动化用例：三个入口分清、插件安装、录制流程、审阅落库',
    anchors: [
      { id: 'sub-rec-entry', title: '三个入口先分清' },
      { id: 'sub-rec-install', title: '安装录制插件' },
      { id: 'sub-rec-flow', title: '实时录制流程' },
      { id: 'sub-rec-review', title: '审阅与落库' },
      { id: 'sub-rec-import', title: '导入录制（HAR / 脚本）' },
      { id: 'sub-rec-faq', title: '录制常见问题' }
    ],
    content: `
      <h3 id="sub-rec-entry">三个入口先分清</h3>
      <p>Web 自动化的「录制」并不是一个按钮，而是<b>三条互补的路径</b>。第一次使用时最容易迷路的地方就在这里，
      先看这张表对号入座：</p>
      <table class="doc-table">
        <thead><tr><th style="width:130px">入口</th><th style="width:150px">在哪里</th><th>什么时候用</th></tr></thead>
        <tbody>
          <tr>
            <td><b>实时录制</b></td>
            <td>浏览器插件<br/>「Q·M 录制器」</td>
            <td><b>主流方式</b>。在真实网页上正常操作，插件自动记录点击、输入、页面跳转，
            适合从零开始把一条业务流程录成用例</td>
          </tr>
          <tr>
            <td><b>导入录制</b></td>
            <td>新增 / 编辑脚本用例页<br/>「导入录制」按钮</td>
            <td>手里已有材料时用：浏览器导出的 <code>.har</code> 文件、
            Chrome DevTools Recorder 录制的脚本</td>
          </tr>
          <tr>
            <td><b>录制履历</b></td>
            <td>脚本用例 → Web 自动化<br/>工具栏「录制履历」</td>
            <td>不是录制动作，而是<b>录制结果的管理台</b>：看历史会话、审阅事件、转成用例</td>
          </tr>
        </tbody>
      </table>
      <div class="callout callout-info">
        <h4>为什么必须装插件才能「实时录制」</h4>
        <p>采集点击、输入、iframe 内元素、SPA 路由跳转这些信息，只有运行在页面里的扩展能做到；
        服务端只能拿到接口请求，拿不到「用户点了哪个按钮」。所以平台把实时采集做成了
        Chrome / Edge 扩展（MV3），插件复用你浏览器的平台登录态，不需要单独登录。</p>
      </div>

      <h3 id="sub-rec-install">安装录制插件</h3>
      <p>插件包在平台里直接下载，不用去别处找：</p>
      <ol class="step-list">
        <li><h4>1. 下载插件包</h4>
          <p>进入<b>脚本用例 → Web 自动化</b>页签，在<b>用例列表右上角的工具条</b>里找到
          <b>「录制插件」</b>按钮（按钮右上角带小红点，表示还没看过）。<b>把鼠标移上去</b>会展开浮层，
          里面有安装三步与<b>下载插件</b>按钮；点击即可得到
          <code>qm-recorder-extension.zip</code>（包内附《安装说明.txt》）。
          同一浮层里还有<b>使用手册</b>按钮，可直接跳到本章节。</p></li>
        <li><h4>2. 解压</h4>
          <p>解压得到一个 <code>qm-recorder-extension</code> 文件夹。<b>不要删除它</b>——
          浏览器加载的是这个文件夹本身，不是 zip。</p></li>
        <li><h4>3. 打开扩展管理页</h4>
          <p>浏览器地址栏输入 <code>chrome://extensions</code> 回车（Edge 同样适用）。</p></li>
        <li><h4>4. 开启开发者模式</h4>
          <p>打开页面右上角的<b>开发者模式</b>开关。</p></li>
        <li><h4>5. 加载已解压的扩展程序</h4>
          <p>点<b>加载已解压的扩展程序</b>，选中第 2 步解压出来的 <code>qm-recorder-extension</code> 文件夹。</p></li>
        <li><h4>6. 确认安装成功</h4>
          <p>浏览器工具栏出现<b>「Q·M 录制器」</b>图标（可在扩展管理页点图钉固定到工具栏）。</p></li>
      </ol>
      <div class="callout callout-warn">
        <h4>为什么不是「一键安装」的 .crx</h4>
        <p>插件尚未上架 Chrome 应用商店，因此走开发者模式加载。这是内网部署下的正常形态，
        安装一次后随浏览器启动自动生效；平台升级插件时会更新版本号，重新下载覆盖即可。</p>
      </div>
      <div class="callout callout-tip">
        <h4>插件需要访问平台后端</h4>
        <p>插件要把事件上传到平台后端（<code>http://172.16.21.161:8000</code>）。
        如果公司网络策略拦截了该地址，录制事件会留在本地缓冲区，网络恢复后自动补传——
        但在那之前录制履历里是空的。</p>
      </div>

      <div class="callout callout-info">
        <h4>零配置：登录态与项目全自动识别</h4>
        <p>插件会自动读取浏览器里的平台登录态和当前项目（你<b>不需要</b>按 F12 查令牌，
        也<b>不需要</b>找项目 ID）。安装后打开一次平台页面，再点插件图标：
        顶部出现绿色<b>「✅ 已自动连接平台」</b>和你的账号名即表示配置完成；
        项目下拉框会自动列出所有项目（中文名）并默认选中你当前进入的项目。</p>
      </div>

      <h3 id="sub-rec-flow">实时录制流程</h3>
      <ol class="step-list">
        <li><h4>1. 先登录平台</h4>
          <p>插件复用浏览器里的平台登录态，所以录制前请先在平台页面完成登录。
          换账号重新登录后，插件会自动跟随新登录态，无需任何手工更新。</p></li>
        <li><h4>2. 打开插件面板</h4>
          <p>点工具栏的<b>「Q·M 录制器」</b>图标，确认顶部状态为绿色「已自动连接平台」。
          在<b>项目下拉框</b>里选择目标项目（默认已选中平台当前项目），填写<b>录制名称</b>
          （可留空自动生成，建议用业务场景命名，如「下单流程-正常路径」），点<b>开始录制</b>。</p></li>
        <li><h4>3. 正常操作页面</h4>
          <p>在目标网页上按业务流程操作即可：点击、输入、下拉选择、文件上传、页面跳转都会被记录；
          iframe 内的元素与单页应用（SPA）的路由变化同样能采到。</p></li>
        <li><h4>4. 结束录制</h4>
          <p>再次点插件图标，点<b>完成录制</b>。插件会先把缓冲区里的事件全部冲传完成再收尾，
          随后就可以回平台处理。</p></li>
        <li><h4>5. 回平台审阅</h4>
          <p>进入<b>脚本用例 → Web 自动化 → 录制履历</b>，找到刚结束的会话，点进去审阅并转成用例。</p></li>
      </ol>
      <div class="callout callout-info">
        <h4>录制中断网、误关页面都不会丢</h4>
        <p>事件先进入插件本地缓冲区，批量上传成功后才清除；失败按指数退避重试。
        因此临时断网、误刷新页面都不会丢已录制的操作——网络恢复后事件会自动补齐。</p>
      </div>

      <h3 id="sub-rec-review">审阅与落库</h3>
      <p>录制履历里点开一个会话，进入<b>审阅台</b>（与 HAR 导入共用同一套审阅组件）：</p>
      <table class="doc-table">
        <thead><tr><th style="width:150px">区域</th><th>作用</th></tr></thead>
        <tbody>
          <tr><td><b>统计条</b></td><td>本次会话共采集多少条事件、已选多少条、忽略多少条、可生成多少步</td></tr>
          <tr><td><b>事件列表</b></td><td>逐条勾选 / 取消。误录的操作（如点错的地方）直接取消勾选，不会被写进用例</td></tr>
          <tr><td><b>忽略项</b></td><td>导航噪音、重复输入等系统建议忽略的条目，可一键恢复</td></tr>
          <tr><td><b>导入选中</b></td><td>把勾选的事件转成用例步骤，落库到当前用例下</td></tr>
          <tr><td><b>导入回执</b></td><td>显示实际新增了几步、跳过了几条、失败原因，落库结果以回执为准</td></tr>
        </tbody>
      </table>
      <div class="callout callout-tip">
        <h4>落库后得到什么</h4>
        <p>勾选的事件会转成 <b>Web 自动化步骤</b>（步骤类型为页面操作），用到的页面元素自动进入
        <b>公共资源 → 元素配置</b>并被打上录制来源标记。之后改定位值只改元素，不用逐条改用例——
        这与手写 UI 用例完全同一条链路。</p>
      </div>
      <div class="callout callout-warn">
        <h4>步骤是「快照」</h4>
        <p>导入时写入的是当时页面结构的快照。如果页面随后改版导致定位失效，
        请到元素配置里更新对应元素的定位值，而不是重新录一遍。</p>
      </div>

      <h3 id="sub-rec-import">导入录制（HAR / 脚本）</h3>
      <p>没有插件或不方便实时录制时，用<b>新增 / 编辑脚本用例页的「导入录制」</b>按钮导入既有材料：</p>
      <table class="doc-table">
        <thead><tr><th style="width:150px">材料</th><th>怎么得到</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>HAR 文件</b></td>
            <td>浏览器 F12 → Network → 勾选 Preserve log → 操作一遍 → 右键 → Save all as HAR</td>
            <td>适合把「已经发生过的一次完整操作」转成接口步骤。可在审阅台勾选只导入关心的请求</td></tr>
          <tr><td><b>DevTools Recorder 脚本</b></td>
            <td>Chrome F12 → Recorder 面板录制 → 导出 JSON / Puppeteer 脚本</td>
            <td>适合轻量补录，无需安装平台插件</td></tr>
        </tbody>
      </table>
      <div class="callout callout-warn">
        <h4>HAR 会丢登录态</h4>
        <p>Chrome 出于安全考虑，导出的 HAR 会<b>剥离 Authorization 等请求头</b>。
        因此导入后的登录接口往往带不上令牌。解决办法：先在接口管理里取到 token 存为变量，
        再给相关步骤统一补上 <code>Authorization</code> 公共头。</p>
      </div>

      <h3 id="sub-rec-faq">录制常见问题</h3>
      <table class="doc-table">
        <thead><tr><th style="width:230px">现象</th><th>原因与处置</th></tr></thead>
        <tbody>
          <tr><td>插件面板提示创建会话失败</td>
            <td>①未登录平台——先在任何平台页面登录；②后端不可达——确认 <code>172.16.21.161:8000</code> 能访问</td></tr>
          <tr><td>插件一直显示「未识别到平台登录态」</td>
            <td>登录态由插件自动读取：先在平台页面完成登录并<b>进入任一项目</b>（我的项目 → 进入项目），
            然后回到任意平台页面按 F5 刷新一次，再点插件面板右上角的<b>「重新识别」</b>。
            若仍不行，检查是否在无痕窗口（无痕窗口的登录态与普通窗口不共享）</td></tr>
          <tr><td>录完了但录制履历里是空的</td>
            <td>事件还在插件本地缓冲区没上传成功（断网 / 后端不可达）。恢复网络后稍等，
            或重新打开插件面板触发一次补传</td></tr>
          <tr><td>工具栏找不到插件图标</td>
            <td>点浏览器工具栏的拼图图标，把「Q·M 录制器」固定出来；
            若列表里没有，回 <code>chrome://extensions</code> 确认开发者模式仍开启</td></tr>
          <tr><td>审阅台里很多条目被建议忽略</td>
            <td>正常。页面跳转、重复聚焦等是导航噪音，不影响用例语义；
            如果误杀了真实操作，在「忽略项」里恢复即可</td></tr>
          <tr><td>想重新录一条用例</td>
            <td>直接开新的会话即可，历史会话都保留在录制履历里，不会互相覆盖</td></tr>
          <tr><td>准备卸载 / 重装插件</td>
            <td>先把未完成的会话点<b>完成录制</b>。卸载会清掉浏览器本地缓冲，未上传的事件找不回来</td></tr>
        </tbody>
      </table>
      <div class="callout callout-info">
        <h4>一条推荐的练习路径</h4>
        <p>装好插件 → 录一次「登录 → 进入某列表页 → 打开详情」→ 审阅时只留 3~5 个关键步骤 →
        导入选中 → 执行一次看日志。跑通这一遍，录制的用法就全部掌握了。</p>
      </div>
    `
  },

  'guide-faq': {
    description: '21 条高频问题的现象、原因与处置路径速查',
    anchors: [
      { id: 'sub-faq-quick', title: '速查表' },
      { id: 'sub-faq-top3', title: '三大高频问题详解' },
      { id: 'sub-faq-diagnose', title: '通用排查思路' }
    ],
    content: `
      <h3 id="sub-faq-quick">速查表</h3>
      <table class="doc-table">
        <thead><tr><th style="width:50px">#</th><th style="width:250px">现象</th><th>原因与处置</th></tr></thead>
        <tbody>
          <tr><td>1</td><td>刷新页面后左侧菜单少了一半，环境/用例/报告都找不到</td><td><b>项目上下文丢失</b>。当前项目只存在浏览器内存中，刷新即清空。回<b>我的项目</b>重新点「进入」</td></tr>
          <tr><td>2</td><td>在地址栏直接改 hash 跳转，进入后功能报错</td><td>同上。手工改 URL 不会加载项目上下文，请始终通过导航进入页面</td></tr>
          <tr><td>3</td><td>AI 助手悬浮球不出现</td><td>未进入项目。悬浮球挂在项目上下文中，进入项目后才会挂载</td></tr>
          <tr><td>4</td><td>AI 助手发送按钮灰色点不动</td><td>未「选择模型」。在面板顶部选模型；若模型列表为空，先到<b>项目设置 → AI 供应商</b>配置并启用</td></tr>
          <tr><td>5</td><td>压测直接失败，提示「未解析到任何目标主机」</td><td>环境里所选服务没填域名。到<b>环境配置</b>为用到的服务补齐服务域名</td></tr>
          <tr><td>6</td><td>性能报告状态「失败」，但看不出为什么</td><td>打开报告详情，看<b>「失败原因」</b>卡片的结论式说明；需要堆栈证据时展开下方的<b>「异常统计」</b></td></tr>
          <tr><td>7</td><td>失败报告里的响应时间/吞吐数据很怪</td><td>压测未跑完，数据只覆盖部分时段，<b>不具备参考价值</b>。按失败原因修复后重跑</td></tr>
          <tr><td>8</td><td>接口调试 404，URL 看起来重复了域名</td><td>请求地址填了绝对路径。接口的请求地址必须填<b>相对路径</b>，域名由环境的服务域名提供</td></tr>
          <tr><td>9</td><td>执行报「参数解析失败」</td><td>变量没取到值。检查变量名大小写、赋值步骤是否在前面、点号引用是否命中常量项。详见<b>变量引用语法</b></td></tr>
          <tr><td>10</td><td>用例结果是「错误」而不是「失败」</td><td>「错误」=执行中抛异常，属平台/环境/依赖问题，不是业务缺陷。查日志里的异常堆栈</td></tr>
          <tr><td>11</td><td>接口返回明明正常，断言却失败</td><td>接口的返回体结构没同步更新，或断言已过期。更新接口返回体后核对引用该字段的用例</td></tr>
          <tr><td>12</td><td>功能用例里「添加步骤」看不到 Web / App 自动化选项</td><td>这两个选项按用例类型条件显示：Web 仅在 WEB_UI 用例出现，App 仅在 APP_UI 用例出现。请检查用例类型</td></tr>
          <tr><td>13</td><td>给用户改了角色，对方界面没变化</td><td>权限在登录时写入会话，需<b>重新登录</b>才生效</td></tr>
          <tr><td>14</td><td>「新增 / 编辑 / 删除」按钮不显示</td><td>多为只读权限。依次查：权限列表 → 角色列表勾选 → 用户列表分配角色 → 重新登录</td></tr>
          <tr><td>15</td><td>环境 / 服务 / 数据库删不掉</td><td>被引用保护。先去引用方（环境绑定、接口引用、用例引用）解除依赖</td></tr>
          <tr><td>16</td><td>刚删除的同名用例 / 接口又能重建</td><td>正常。删除是软删除，名称唯一性只在未删除集合内校验</td></tr>
          <tr><td>17</td><td>定时任务到点没执行</td><td>检查三处：任务「启用」是否开启、cron 表达式是否正确（用工具箱验证）、套件所用的环境是否绑齐资源</td></tr>
          <tr><td>18</td><td>打开某条执行日志页面很卡</td><td>该接口返回体很大（如全量列表查询），单次日志体积可能达数 MB。按步骤定点查看，不要一次展开全部</td></tr>
          <tr><td>19</td><td>AI 生成元素提示「成功 24」，但元素列表里一条都看不到</td><td>弹窗只报告了「AI 识别到多少」，不代表「落库成功」。到<b>站内信</b>看同一条通知的<b>落库异常</b>段落，里面写了具体失败原因；另外「页面需登录」类页面要先配登录态（见下条）</td></tr>
          <tr><td>20</td><td>AI 生成元素对需要登录的页面采不到内容</td><td>AI 抓取默认不带登录态。两种配法二选一：①在<b>环境配置 → 全局会话配置</b>里存一份 Cookie，该环境所有 AI 抓取都用它；②在 AI 生成弹窗的<b>「本次登录态」</b>里就地粘贴 Cookie，只对本次生效</td></tr>
          <tr><td>21</td><td>Web 自动化里没找到「录制」按钮，只有一个「录制履历」</td><td>三者不是一回事：<b>录制履历</b>看历史、<b>导入录制</b>传文件、<b>实时录制</b>靠浏览器插件。插件在<b>脚本用例 → Web 自动化</b>页<b>用例列表右上角工具条</b>的<b>「录制插件」</b>按钮里（鼠标悬浮展开，浮层内可下载）。详见<b>Web 自动化录制</b>章节</td></tr>
        </tbody>
      </table>

      <h3 id="sub-faq-top3">三大高频问题详解</h3>

      <div class="callout callout-warn">
        <h4>① 刷新后「功能不见了」</h4>
        <p><b>现象</b>：正常用着，按了 F5 或从别的标签页切回来，左侧只剩几个菜单，
        环境管理、公共资源、测试资产全都不见了；有些页面点进去还报错。</p>
        <p><b>原因</b>：当前项目信息仅保存在前端内存（Vuex）中，不做持久化。
        刷新后内存清空，但 URL 的 hash 还停在内页，于是出现「在内页但没有项目上下文」的中间态。</p>
        <p><b>处置</b>：回到<b>项目管理 → 我的项目</b>，重新点击目标项目的「进入」。
        这是设计如此的行为，不是 Bug。</p>
        <p><b>规避</b>：把「进入项目」当作每次打开平台的第一个动作；
        不要把内页地址存成书签当作入口使用。</p>
      </div>

      <div class="callout callout-warn">
        <h4>② 压测「未解析到任何目标主机」</h4>
        <p><b>现象</b>：发起压测后报告立刻变为失败，失败原因是「压测无法开始：未解析到任何目标主机」。</p>
        <p><b>原因</b>：压测需要把用例中的请求地址解析成真实 URL。平台的做法是
        「环境的服务域名 + 接口相对路径」，如果环境里没有为你用到的服务配置服务域名，
        就拼不出任何可访问的主机。</p>
        <p><b>处置</b>：到<b>环境管理 → 环境配置</b>，编辑当前环境，勾选并填写用到的每个服务的
        <b>服务域名</b>（带协议头，如 <code>http://172.16.21.141:8000</code>），保存后重跑。</p>
        <p><b>自检</b>：在环境配置里数一下——用例用到了几个服务？每个都填域名了吗？</p>
      </div>

      <div class="callout callout-warn">
        <h4>③ 「错误」与「失败」分不清</h4>
        <p><b>现象</b>：报告里一堆红，但打开日志看接口返回是正常的；或者反过来，
        接口返回明显不对但结果是「错误」。</p>
        <p><b>口径</b>：<b>失败</b> = 断言未通过，业务结果与预期不符 → 查被测系统。
        <b>错误</b> = 执行过程中抛异常 → 查平台、环境、依赖。</p>
        <p><b>处置</b>：先集中清掉所有「错误」（通常一次环境配置修复能消掉一大批），
        再把剩下的「失败」逐条当业务问题分析。统计质量时两者分开计数，不要混进一个通过率。</p>
        <p><b>提示</b>：日志里出现 "error" 字样不代表失败——返回体中天然含 error 字段的情况很常见，
        判断依据是断言结果与用例结果状态，不是关键词搜索。</p>
      </div>

      <h3 id="sub-faq-diagnose">通用排查思路</h3>
      <p>遇到任何「不工作」的问题，按下面这条链路走，能覆盖绝大多数场景：</p>
      <div class="flow">
        <div class="flow-step"><span class="flow-idx">1</span><b>有没有进项目</b><p>菜单齐不齐？AI 悬浮球在不在？</p></div>
        <div class="flow-step"><span class="flow-idx">2</span><b>环境绑齐了吗</b><p>服务域名、平台、数据库是否都绑定并填好</p></div>
        <div class="flow-step"><span class="flow-idx">3</span><b>资产配完整了吗</b><p>接口所属服务/模块、返回体结构、用例的前置步骤</p></div>
        <div class="flow-step"><span class="flow-idx">4</span><b>看日志定位步骤</b><p>哪一步失败？请求有没有发出？变量替换后的值对不对？</p></div>
        <div class="flow-step"><span class="flow-idx">5</span><b>区分失败与错误</b><p>有异常堆栈=环境/平台问题；断言不符=业务问题</p></div>
        <div class="flow-step"><span class="flow-idx">6</span><b>查权限与审计</b><p>按钮缺失查权限；配置被改查审计日志</p></div>
      </div>
      <div class="callout callout-info">
        <h4>提报平台问题时的最小信息集</h4>
        <p>如果排查后确认是平台问题，请在反馈时附上：①操作路径（哪个页面、什么操作）；
        ②期望结果与实际结果；③执行日志中的相关片段（含请求与响应）；
        ④发生时间与使用的环境名。有这四项，定位效率会高很多。</p>
      </div>
    `
  }
}

export default guideChildren
