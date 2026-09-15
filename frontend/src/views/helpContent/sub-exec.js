/**
 * 帮助文档 · 二级页面详述（三）：执行中心 / 报告管理 / 缺陷管理
 */

export const execChildren = {
  /* ================= 执行中心 ================= */
  'suite-plan': {
    description: '面向人工与排期的测试计划：起止时间、执行跟踪、测试结论',
    anchors: [
      { id: 'sub-plan-fields', title: '字段说明' },
      { id: 'sub-plan-how', title: '操作步骤' },
      { id: 'sub-plan-status', title: '执行状态口径' },
      { id: 'sub-plan-rules', title: '使用建议' }
    ],
    content: `
      <h3 id="sub-plan-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:180px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>计划名称</b></td><td>如「2026-09 版本回归计划」</td></tr>
          <tr><td><b>计划起止时间</b></td><td>测试周期，用于排期与进度对比</td></tr>
          <tr><td><b>计划描述</b></td><td>测试范围、目标与注意事项</td></tr>
          <tr><td><b>测试结论</b></td><td>计划结束后的整体结论（如「本轮共 21 条用例，通过 19 条，2 条遗留」）</td></tr>
          <tr><td><b>关联功能用例</b></td><td>把要执行的功能用例加入计划</td></tr>
          <tr><td><b>执行状态</b></td><td>逐条用例标记，见下表</td></tr>
          <tr><td><b>执行人 / 执行时间</b></td><td>记录谁在什么时候执行了这条用例</td></tr>
          <tr><td><b>评论</b></td><td>执行过程中的备注与沟通记录</td></tr>
        </tbody>
      </table>

      <h3 id="sub-plan-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新建计划</h4><p>填写计划名称、起止时间与描述，保存。</p></li>
        <li><h4>2. 加入用例</h4><p>在计划中把本轮要执行的功能用例加进来。</p></li>
        <li><h4>3. 执行并标记</h4><p>按用例逐条执行，标记执行状态、执行人、执行时间。</p></li>
        <li><h4>4. 留评论</h4><p>遇到阻塞或异常时在对应用例下写评论，保留上下文。</p></li>
        <li><h4>5. 填写测试结论</h4><p>全部执行完后填写整体结论，作为准出依据。</p></li>
        <li><h4>6. 看概览</h4><p>计划提供<b>详情</b>与<b>概览</b>两个视图：详情用于逐条执行，概览用于看整体进度分布。</p></li>
      </ol>

      <h3 id="sub-plan-status">执行状态口径</h3>
      <table class="doc-table">
        <thead><tr><th style="width:140px">状态</th><th>含义</th></tr></thead>
        <tbody>
          <tr><td><b>未执行</b></td><td>还没开始执行</td></tr>
          <tr><td><b>进行中</b></td><td>正在执行</td></tr>
          <tr><td><b>已通过</b></td><td>执行结果符合预期</td></tr>
          <tr><td><b>未通过</b></td><td>执行结果不符预期，通常需要登记缺陷</td></tr>
          <tr><td><b>暂缓</b></td><td>因依赖未就绪等原因暂时不执行（需说明原因）</td></tr>
        </tbody>
      </table>

      <h3 id="sub-plan-rules">使用建议</h3>
      <div class="callout callout-tip">
        <h4>计划与人、套件与机器</h4>
        <p><b>测试计划</b>解决的是「这轮测什么、谁测的、测到哪了、结论是什么」——它是管理视图。</p>
        <p><b>套件</b>解决的是「让机器把这些用例跑一遍」——它是执行视图。</p>
        <p>两者不要互相替代：需要人工验证与验收记录的走计划，需要自动回归的走套件。</p>
      </div>
      <div class="callout callout-info">
        <h4>「未通过」及时转缺陷</h4>
        <p>用例标记为「未通过」后建议立刻到<b>缺陷管理</b>登记缺陷，并在缺陷上关联这条功能用例与测试计划，
        这样缺陷修复后能直接反查要回归哪些用例。</p>
      </div>
    `
  },

  'suite-suite': {
    description: '套件编排：选用例、配执行策略、触发自动执行',
    anchors: [
      { id: 'sub-suite-fields', title: '字段说明' },
      { id: 'sub-suite-mode', title: '静态模式 vs 动态模式' },
      { id: 'sub-suite-how', title: '操作步骤' },
      { id: 'sub-suite-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-suite-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:190px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>计划名称</b></td><td>套件名称，≤50 字</td></tr>
          <tr><td><b>计划描述</b></td><td>套件用途说明，≤200 字</td></tr>
          <tr><td><b>计划类型</b></td><td>
            <span class="badge">功能用例</span><span class="badge">脚本用例</span>
          </td></tr>
          <tr><td><b>计划模式</b></td><td>
            <span class="badge">静态模式</span><span class="badge">动态模式</span>
          </td></tr>
          <tr><td><b>脚本用例类型</b></td><td>
            <span class="badge">API</span><span class="badge">WEB_UI</span><span class="badge">APP_UI</span>
          </td></tr>
          <tr><td><b>脚本用例失败重试次数</b></td><td>失败后自动重跑次数</td></tr>
          <tr><td><b>Web / App 执行器节点</b></td><td>UI 自动化所需的执行机</td></tr>
          <tr><td><b>用例执行完是否推送消息</b></td><td>开启后执行完成按项目消息设置推送</td></tr>
          <tr><td><b>动态模式筛选用例条件</b></td><td>动态模式下用于实时筛选用例的条件</td></tr>
          <tr><td><b>关联自动化用例 / 功能用例</b></td><td>静态模式下手工挑选的用例集合</td></tr>
          <tr><td><b>计划起止时间</b></td><td>套件的有效时间段</td></tr>
        </tbody>
      </table>

      <h3 id="sub-suite-mode">静态模式 vs 动态模式</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">模式</th><th>用例来源</th><th>适合</th></tr></thead>
        <tbody>
          <tr><td><b>静态模式</b></td><td>手工挑选具体用例，范围固定</td><td>发布前回归、验收，需要精确控制范围</td></tr>
          <tr><td><b>动态模式</b></td><td>按条件实时筛选，用例增删自动跟随</td><td>每日巡检，希望新用例自动纳入</td></tr>
        </tbody>
      </table>
      <div class="callout callout-warn">
        <h4>动态模式的范围会变</h4>
        <p>动态模式下，新增的用例一旦命中筛选条件就会被自动纳入执行范围，
        导致执行耗时与结果数量变化。做结果对比（这次比上次好还是差）时要注意基数是否一致。
        需要可比性时请改用静态模式。</p>
      </div>

      <h3 id="sub-suite-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新建套件</h4><p>填写名称、描述，选择计划类型与计划模式。</p></li>
        <li><h4>2. 选用例</h4><p>静态模式手工勾选用例；动态模式配置筛选条件。</p></li>
        <li><h4>3. 配执行策略</h4><p>设置失败重试次数。UI 自动化还需选择 Web / App 执行器节点。</p></li>
        <li><h4>4. 配消息推送</h4><p>按需开启「执行完是否推送消息」（需项目已配好消息渠道）。</p></li>
        <li><h4>5. 执行</h4><p>保存后触发执行，随后到<b>报告管理</b>查看结果。</p></li>
        <li><h4>6. 如需周期执行</h4><p>到<b>定时任务</b>为本套件挂上 crontab。</p></li>
      </ol>

      <h3 id="sub-suite-rules">注意事项</h3>
      <div class="callout callout-tip">
        <h4>重试是把双刃剑</h4>
        <p>重试能压掉环境抖动引起的偶发失败，让回归结果更可信；但它也会掩盖真实的偶现缺陷。
        建议轻度重试（1~2 次），并单独统计「首次失败、重试通过」的用例做稳定性跟进。</p>
      </div>
      <div class="callout callout-warn">
        <h4>UI 套件要选对执行器</h4>
        <p>Web_UI 与 APP_UI 套件必须选择对应的执行器节点，否则无法启动执行。
        执行器节点配置在环境管理的执行机配置中维护。</p>
      </div>
    `
  },

  'suite-task': {
    description: '给套件挂上 crontab，实现定时自动执行',
    anchors: [
      { id: 'sub-task-fields', title: '字段说明' },
      { id: 'sub-task-how', title: '操作步骤' },
      { id: 'sub-task-cron', title: 'Cron 表达式速查' },
      { id: 'sub-task-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-task-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:170px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>套件名称</b></td><td>要定时执行的套件，必选</td></tr>
          <tr><td><b>环境名称</b></td><td>执行时使用的环境，必选</td></tr>
          <tr><td><b>定时策略</b></td><td>crontab 表达式，必填</td></tr>
          <tr><td><b>启用</b></td><td>总开关。停用后不再触发，但配置保留</td></tr>
          <tr><td><b>定时任务描述</b></td><td>说明这个任务的用途</td></tr>
        </tbody>
      </table>

      <h3 id="sub-task-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 准备套件</h4><p>确认要定时的套件已建好并单次跑通。</p></li>
        <li><h4>2. 新建定时任务</h4><p>选择套件与环境，填写 crontab 表达式与描述。</p></li>
        <li><h4>3. 用工具校验表达式</h4><p>到<b>测试工具箱 → 生成 Cron 表达式 / 验证表达式 / 下次执行时间</b>
        确认表达式正确，并核对接下来几次的执行时间。</p></li>
        <li><h4>4. 启用并观察</h4><p>开启启用。第一次触发后到<b>报告管理</b>确认报告已生成，并确认消息推送正常。</p></li>
      </ol>

      <h3 id="sub-task-cron">Cron 表达式速查</h3>
      <table class="doc-table">
        <thead><tr><th style="width:220px">需求</th><th>表达式</th></tr></thead>
        <tbody>
          <tr><td>每天凌晨 2 点</td><td><code>0 2 * * *</code></td></tr>
          <tr><td>每天凌晨 3 点 30 分</td><td><code>30 3 * * *</code></td></tr>
          <tr><td>每小时整点</td><td><code>0 * * * *</code></td></tr>
          <tr><td>工作日（周一至周五）早上 9 点</td><td><code>0 9 * * 1-5</code></td></tr>
          <tr><td>每周一早上 8 点</td><td><code>0 8 * * 1</code></td></tr>
          <tr><td>每月 1 日凌晨 1 点</td><td><code>0 1 1 * *</code></td></tr>
        </tbody>
      </table>
      <p>字段顺序为「分 时 日 月 周」。不确定时请用工具箱验证，不要凭记忆填写。</p>

      <h3 id="sub-task-rules">注意事项</h3>
      <div class="callout callout-warn">
        <h4>定时执行的环境必须绑齐资源</h4>
        <p>定时任务无人值守，环境没配好就会静默产生一批失败报告。
        新配任务前请先用同一套件 + 同一环境手工跑一次确认无误。</p>
      </div>
      <div class="callout callout-tip">
        <h4>多个任务错峰启动</h4>
        <p>把多个定时任务安排在同一时间点会互相争抢被测系统资源，导致响应时间虚高、失败率上升。
        建议错开几分钟，并避免与压测时间重叠。</p>
      </div>
      <div class="callout callout-info">
        <h4>临时停用比删除更合适</h4>
        <p>版本冻结期或被测环境维护期间，把任务「启用」关掉即可，不必删除，
        维护结束后重新开启，配置与历史执行记录都还在。</p>
      </div>
    `
  },

  /* ================= 报告管理 ================= */
  'report-log': {
    description: '逐步骤执行日志——排查失败的第一入口',
    anchors: [
      { id: 'sub-log-what', title: '日志内容' },
      { id: 'sub-log-how', title: '怎么用日志排查' },
      { id: 'sub-log-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-log-what">日志内容</h3>
      <p>日志列表按时间倒序记录每一次用例执行的过程，粒度到<b>步骤级</b>。一条典型的执行记录包含：</p>
      <table class="doc-table">
        <thead><tr><th style="width:170px">内容</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>执行时间 / 环境</b></td><td>什么时候、在哪个环境跑的</td></tr>
          <tr><td><b>用例名称</b></td><td>哪条用例</td></tr>
          <tr><td><b>步骤序号与描述</b></td><td>执行到第几步</td></tr>
          <tr><td><b>请求信息</b></td><td>方法、URL、请求头、请求体（变量已替换后的实际值）</td></tr>
          <tr><td><b>响应信息</b></td><td>状态码、响应头、响应体</td></tr>
          <tr><td><b>断言结果</b></td><td>每条断言的实际值与期望值</td></tr>
          <tr><td><b>变量赋值</b></td><td>「某变量被设置为某值」的提取记录</td></tr>
          <tr><td><b>异常堆栈</b></td><td>出错时的原始异常信息</td></tr>
        </tbody>
      </table>

      <h3 id="sub-log-how">怎么用日志排查</h3>
      <div class="flow">
        <div class="flow-step"><span class="flow-idx">1</span><b>定位失败步骤</b><p>先从报告里拿到失败的用例名，在日志列表中检索该用例</p></div>
        <div class="flow-step"><span class="flow-idx">2</span><b>看请求是否发出</b><p>没有请求记录 → 前面步骤已失败或被跳过</p></div>
        <div class="flow-step"><span class="flow-idx">3</span><b>对照实际请求</b><p>URL / 请求头 / 请求体是否与预期一致（重点看变量替换后的值）</p></div>
        <div class="flow-step"><span class="flow-idx">4</span><b>看响应与断言</b><p>响应码是多少、断言哪一条不通过、实际值是什么</p></div>
        <div class="flow-step"><span class="flow-idx">5</span><b>区分失败与错误</b><p>有异常堆栈 → 平台/环境问题；无堆栈但断言不符 → 业务问题</p></div>
      </div>

      <h3 id="sub-log-rules">注意事项</h3>
      <div class="callout callout-warn">
        <h4>日志里出现 "error" 字样不等于失败</h4>
        <p>被测系统返回体里可能天然包含 <code>error</code> 字样（如 <code>error_code: 0</code> 表示成功），
        正常流程的日志也可能提到 error 字段。判断是否失败请以<b>断言结果</b>和<b>用例结果状态</b>为准，
        不要用关键词搜索来判定。</p>
      </div>
      <div class="callout callout-tip">
        <h4>变量替换后的实际值是排错关键</h4>
        <p>日志里记录的是<b>替换之后</b>的真实请求，这正是定位「变量取不到值」类问题的依据。
        如果发现请求体里出现了 <code>\${...}</code> 原文未替换，说明该变量在此时点还没有值——
        请检查提取步骤的执行顺序。</p>
      </div>
      <div class="callout callout-info">
        <h4>大响应体的日志很长</h4>
        <p>返回大量数据的接口（如全量列表查询）会使单次日志体积很大，页面加载会变慢。
        排查时建议按步骤定位，不要一次性展开全部内容。</p>
      </div>
    `
  },

  'report-reportList': {
    description: '功能报告——一轮执行的整体结果与用例明细',
    anchors: [
      { id: 'sub-report-fields', title: '字段说明' },
      { id: 'sub-report-how', title: '怎么用' },
      { id: 'sub-report-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-report-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:180px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>报告名称</b></td><td>一般由「套件名 + 执行时间」组成</td></tr>
          <tr><td><b>总用例数</b></td><td>本次执行涉及的用例总数</td></tr>
          <tr><td><b>成功用例数</b></td><td>断言全部通过</td></tr>
          <tr><td><b>失败用例数</b></td><td>断言未通过（业务结果不符预期）</td></tr>
          <tr><td><b>错误用例数</b></td><td>执行中抛异常（脚本 / 环境 / 依赖问题）</td></tr>
          <tr><td><b>关联对象</b></td><td>报告可关联套件、测试计划、接口或环境</td></tr>
          <tr><td><b>明细</b></td><td>逐条用例的执行记录，可下钻到步骤级日志</td></tr>
        </tbody>
      </table>

      <h3 id="sub-report-how">怎么用</h3>
      <table class="doc-table">
        <thead><tr><th style="width:230px">目的</th><th>做法</th></tr></thead>
        <tbody>
          <tr><td>快速判断这轮质量</td><td>看成功 / 失败 / 错误三个数字的比例。错误占比高说明环境或平台有问题，先别急着评价被测系统</td></tr>
          <tr><td>定位具体问题</td><td>从失败列表中打开用例，下钻到步骤日志看是哪条断言不符</td></tr>
          <tr><td>对比两轮结果</td><td>确保两轮报告的用例集合一致，再比较失败清单的差异</td></tr>
          <tr><td>准出决策</td><td>以「失败用例是否都有明确处置（修复 / 转缺陷 / 确认可接受）」为准则，而不是只看通过率</td></tr>
        </tbody>
      </table>

      <h3 id="sub-report-rules">注意事项</h3>
      <div class="callout callout-info">
        <h4>报告是快照，不可变</h4>
        <p>报告生成时用例数等统计即被固化。<b>重跑会生成一份新报告</b>，不会覆盖旧报告。
        因此历史报告始终可作为当时的证据留存。</p>
      </div>
      <div class="callout callout-warn">
        <h4>「错误」不要混进失败率</h4>
        <p>把错误当作失败来计算通过率，会得出偏悲观且无法改进的结论。建议分三个口径统计：
        通过率（成功/总数）、业务失败率（失败/总数）、执行错误数（单独跟进）。
        错误的常见原因包括：环境未绑定服务域名、变量解析失败、被测系统不可用、步骤类型不支持等。</p>
      </div>
      <div class="callout callout-tip">
        <h4>先看错误再看失败</h4>
        <p>排查顺序建议：<b>先清掉所有「错误」</b>（它们往往是环境或配置问题，一次修好能消掉一批红灯），
        剩下的「失败」才是需要逐条分析的真实业务问题。</p>
      </div>
    `
  },

  'report-locust': {
    description: '性能压测报告——响应时间、请求统计、异常与资源占用',
    anchors: [
      { id: 'sub-locust-fields', title: '字段说明' },
      { id: 'sub-locust-status', title: '报告状态：已完成 / 压测中 / 失败' },
      { id: 'sub-locust-fail', title: '失败原因（独立字段）' },
      { id: 'sub-locust-read', title: '怎么读性能数据' },
      { id: 'sub-locust-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-locust-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:200px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>状态</b></td><td>已完成 / 压测中 / 失败</td></tr>
          <tr><td><b>并发用户数</b></td><td>本次压测的目标并发</td></tr>
          <tr><td><b>每秒启动用户数</b></td><td>加压速率（rate），决定压力爬升的快慢</td></tr>
          <tr><td><b>持续时间</b></td><td>压测时长</td></tr>
          <tr><td><b>开始时间 / 结束时间</b></td><td>执行窗口</td></tr>
          <tr><td><b>请求统计</b></td><td>请求数、失败数、吞吐（每秒请求数）、响应时间分位（P50 / P90 / P95 / P99 等）</td></tr>
          <tr><td><b>响应时间统计</b></td><td>按时间轴记录的响应时间变化</td></tr>
          <tr><td><b>异常统计</b></td><td>原始异常明细（含堆栈），用于问题溯源</td></tr>
          <tr><td><b>失败原因</b></td><td>结论式的一句话说明（面向用户），压测未正常完成时出现</td></tr>
          <tr><td><b>CPU / 内存</b></td><td>压测期间被测服务的资源占用</td></tr>
          <tr><td><b>历史</b></td><td>并发与指标的历史曲线数据</td></tr>
        </tbody>
      </table>

      <h3 id="sub-locust-status">报告状态：已完成 / 压测中 / 失败</h3>
      <table class="doc-table">
        <thead><tr><th style="width:140px">状态</th><th>含义</th><th>数据是否可用</th></tr></thead>
        <tbody>
          <tr><td><b>压测中</b></td><td>压测进程正在运行</td><td>尚未产出最终数据</td></tr>
          <tr><td><b>已完成</b></td><td>压测正常跑完整个时长</td><td>可用，可作为结论依据</td></tr>
          <tr><td><b>失败</b></td><td>压测中途中断或执行异常退出</td><td><b>不可用</b>——本次未产生有效压测数据</td></tr>
        </tbody>
      </table>

      <h3 id="sub-locust-fail">失败原因（独立字段）</h3>
      <p>状态为「失败」时，报告详情页会显示一张独立的<b>「失败原因」</b>卡片，
      给出「为什么会失败」的结论式说明。列表页把鼠标悬停在失败标签上也能直接看到该原因。</p>
      <p>常见失败原因与处置：</p>
      <table class="doc-table">
        <thead><tr><th style="width:290px">失败原因提示</th><th>处置方向</th></tr></thead>
        <tbody>
          <tr><td>压测无法开始：未解析到任何目标主机，请检查环境的「平台/服务」配置</td><td>到环境配置为用到的服务填写服务域名</td></tr>
          <tr><td>压测异常中断（守护进程自动判定）</td><td>压测进程非正常退出（被杀、OOM、崩溃）；结合「异常统计」中的堆栈与服务器资源排查</td></tr>
          <tr><td>压测执行异常退出：某异常类型</td><td>用例本身或数据存在问题，按异常信息修正用例后重跑</td></tr>
          <tr><td>压测进程启动失败</td><td>多为运行环境（执行机、依赖）问题，需运维侧介入</td></tr>
        </tbody>
      </table>
      <div class="callout callout-info">
        <h4>「失败原因」与「异常统计」的分工</h4>
        <p><b>失败原因</b>：结论式说明，回答「为什么会失败」，面向用户，一两句话讲清。</p>
        <p><b>异常统计</b>：原始异常明细（含完整 traceback），用于深度溯源，面向排障人员。</p>
        <p>两者不再混用：排查时先读「失败原因」定位方向，需要堆栈证据时再展开「异常统计」。</p>
      </div>

      <h3 id="sub-locust-read">怎么读性能数据</h3>
      <table class="doc-table">
        <thead><tr><th style="width:160px">指标</th><th>怎么看</th></tr></thead>
        <tbody>
          <tr><td><b>吞吐（RPS）</b></td><td>压力上升时吞吐应同步上升；若并发增加而吞吐不再增长，说明已达到瓶颈</td></tr>
          <tr><td><b>响应时间 P95 / P99</b></td><td>平均值会被大量快请求拉低，判断体验要看高百分位。P99 突增往往预示瓶颈</td></tr>
          <tr><td><b>失败请求数</b></td><td>出现非零失败说明压力已超出系统承载，或被测服务存在错误</td></tr>
          <tr><td><b>CPU / 内存</b></td><td>与吞吐曲线对照：CPU 打满而吞吐不涨=算力瓶颈；内存持续上涨不回落=疑似泄漏</td></tr>
          <tr><td><b>响应时间随时间的走势</b></td><td>同样并发下响应时间逐渐劣化，说明系统存在累积效应（连接/内存/锁）</td></tr>
        </tbody>
      </table>

      <h3 id="sub-locust-rules">注意事项</h3>
      <div class="callout callout-warn">
        <h4>失败报告的数字不要用</h4>
        <p>状态为「失败」说明压测没跑完，此时报告里的请求数、响应时间只覆盖了部分时段，
        不具备统计意义。请按失败原因修复后重新执行，使用新报告出结论。</p>
      </div>
      <div class="callout callout-warn">
        <h4>压测前确认环境与数据</h4>
        <p>压测会产生大量真实数据写入。执行前请：①确认环境指向的是压测环境而非生产；
        ②确认环境的服务域名已配置；③确认测试数据可重复使用（写入类接口需要唯一数据源，否则会因主键冲突报错）。</p>
      </div>
      <div class="callout callout-tip">
        <h4>单接口压测与混合场景不要混为一谈</h4>
        <p>评估某个接口的真实容量，请对该接口<b>单独压测</b>；混合场景的总体 TPS 只能反映系统整体吞吐，
        无法反推单个接口的能力上限。做容量评估时请保持压测对象单一。</p>
      </div>
    `
  },

  /* ================= 缺陷管理 ================= */
  'defect-defectList': {
    description: '缺陷登记、流转与关联追溯',
    anchors: [
      { id: 'sub-defect-fields', title: '字段说明' },
      { id: 'sub-defect-how', title: '操作步骤' },
      { id: 'sub-defect-flow', title: '状态流转' },
      { id: 'sub-defect-rules', title: '提单规范' }
    ],
    content: `
      <h3 id="sub-defect-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:180px">字段</th><th>取值 / 说明</th></tr></thead>
        <tbody>
          <tr><td><b>缺陷标题</b></td><td>≤500 字。写「模块 + 操作 + 现象」</td></tr>
          <tr><td><b>缺陷描述</b></td><td>复现步骤、环境信息、账号与数据</td></tr>
          <tr><td><b>实际结果</b></td><td>实际发生了什么</td></tr>
          <tr><td><b>预期结果</b></td><td>按需求应该发生什么</td></tr>
          <tr><td><b>严重程度</b></td><td>
            <span class="badge">致命</span><span class="badge">严重</span><span class="badge">一般</span><span class="badge">轻微</span>
          </td></tr>
          <tr><td><b>优先级</b></td><td>
            <span class="badge">紧急</span><span class="badge">高</span><span class="badge">中</span><span class="badge">低</span>
          </td></tr>
          <tr><td><b>BUG 类型</b></td><td>
            <span class="badge">代码问题-前端</span><span class="badge">代码问题-后端</span><span class="badge">设计如此</span>
            <span class="badge">重复BUG</span><span class="badge">需求变动</span><span class="badge">UI样式</span><span class="badge">设计缺陷</span>
          </td></tr>
          <tr><td><b>状态</b></td><td>
            <span class="badge">待处理</span><span class="badge">处理中</span><span class="badge">已解决</span><span class="badge">已关闭</span>
          </td></tr>
          <tr><td><b>所属模块</b></td><td>服务模块，与接口、用例共用同一套模块树</td></tr>
          <tr><td><b>处理人</b></td><td>实际修复的人</td></tr>
          <tr><td><b>负责人</b></td><td>跟踪闭环的人（可为测试侧）</td></tr>
          <tr><td><b>关联功能用例</b></td><td>可关联多条，等于附上复现步骤</td></tr>
          <tr><td><b>关联测试计划</b></td><td>记录缺陷是在哪轮计划中发现的</td></tr>
          <tr><td><b>附件</b> / <b>评论</b></td><td>截图、日志与沟通记录</td></tr>
        </tbody>
      </table>

      <h3 id="sub-defect-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 登记缺陷</h4><p>填写标题、描述、实际结果、预期结果，选择模块与严重程度 / 优先级。</p></li>
        <li><h4>2. 关联用例与计划</h4><p>把发现该缺陷的功能用例与所在测试计划挂上。</p></li>
        <li><h4>3. 指定处理人与负责人</h4><p>处理人负责修，负责人负责跟踪闭环。</p></li>
        <li><h4>4. 跟进流转</h4><p>随修复进度更新状态，必要时在评论中同步信息。</p></li>
        <li><h4>5. 验证并关闭</h4><p>修复后按关联用例回归，确认修复再把状态置为「已关闭」。</p></li>
      </ol>

      <h3 id="sub-defect-flow">状态流转</h3>
      <div class="flow">
        <div class="flow-step"><span class="flow-idx">1</span><b>待处理</b><p>测试提交，指定处理人</p></div>
        <div class="flow-step"><span class="flow-idx">2</span><b>处理中</b><p>研发接单修复</p></div>
        <div class="flow-step"><span class="flow-idx">3</span><b>已解决</b><p>修复完成，转测试验证</p></div>
        <div class="flow-step"><span class="flow-idx">4</span><b>已关闭</b><p>验证通过后关闭</p></div>
      </div>

      <h3 id="sub-defect-rules">提单规范</h3>
      <div class="callout callout-tip">
        <h4>好缺陷的四个特征</h4>
        <p><b>可复现</b>：写明环境、账号、数据与操作序列，别人能照着复现。</p>
        <p><b>可判定</b>：实际结果与预期结果分开写，修复与否能客观对照。</p>
        <p><b>可定位</b>：标题含模块，便于分派；描述含关键日志与请求响应。</p>
        <p><b>可追溯</b>：关联功能用例与测试计划，避免重复提单。</p>
      </div>
      <div class="callout callout-warn">
        <h4>哪些不该提业务缺陷</h4>
        <p>以下属于<b>环境或平台侧问题</b>，不应登记为被测系统缺陷：
        用例执行结果为「错误」（变量解析失败、主机解析不到、步骤类型不支持）、
        测试数据不可复用导致的重复执行失败、压测状态为「失败」的报告。
        请先处置这些前置问题，再评估剩下的「失败」是否为真实业务缺陷。</p>
      </div>
      <div class="callout callout-info">
        <h4>严重程度与优先级分开评估</h4>
        <p><b>严重程度</b>是技术影响（会不会崩、数据对不对）；<b>优先级</b>是业务紧迫度（要不要立刻修）。
        一个「偶现的报表金额四舍五入错误」严重程度是一般，但如果用于对外结算，优先级应是紧急。
        两者不要默认划等号。</p>
      </div>
    `
  }
}

export default execChildren
