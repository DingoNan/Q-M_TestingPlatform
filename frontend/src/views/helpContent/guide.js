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

  'guide-faq': {
    description: '18 条高频问题的现象、原因与处置路径速查',
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
