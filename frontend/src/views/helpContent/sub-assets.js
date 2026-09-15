/**
 * 帮助文档 · 二级页面详述（二）：公共资源 / 测试资产
 */

export const assetsChildren = {
  /* ================= 公共资源 ================= */
  'common-file': {
    description: '测试文件的集中存放与引用',
    anchors: [
      { id: 'sub-file-fields', title: '字段说明' },
      { id: 'sub-file-how', title: '操作步骤' },
      { id: 'sub-file-rules', title: '使用场景' }
    ],
    content: `
      <h3 id="sub-file-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:160px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>文件名称</b></td><td>平台内的文件标识，建议与业务用途对应</td></tr>
          <tr><td><b>文件描述</b></td><td>说明这个文件是干什么用的</td></tr>
          <tr><td><b>文件本体</b></td><td>上传的实际文件</td></tr>
        </tbody>
      </table>
      <p>常见可存放的类型：文本 / 数据（<code>.txt .csv .json .xml</code>）、脚本（<code>.py .js .sh</code>）、
      文档（<code>.doc .pdf .xlsx</code>）、图片（<code>.png .jpg .gif</code>）等。</p>

      <h3 id="sub-file-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 上传文件</h4><p>点击「新增」，填写名称与描述，选择本地文件上传。</p></li>
        <li><h4>2. 在用例中引用</h4><p>接口步骤需要上传文件时，把请求体设为 Form-data，选择文件类型的参数引用该文件。</p></li>
        <li><h4>3. 作为参数化数据源</h4><p>CSV 类文件可作为批量数据来源，供用例循环取值。</p></li>
      </ol>

      <h3 id="sub-file-rules">使用场景</h3>
      <table class="doc-table">
        <thead><tr><th style="width:200px">场景</th><th>做法</th></tr></thead>
        <tbody>
          <tr><td>测试上传类接口</td><td>上传后引用该文件作为表单文件参数</td></tr>
          <tr><td>批量导入业务数据</td><td>存放导入模板并上传，验证导入接口</td></tr>
          <tr><td>证书 / 密钥文件</td><td>存放 <code>.pem</code> 类文件供签名步骤读取</td></tr>
          <tr><td>造大批量唯一数据</td><td>先用「测试工具箱 → 测试数据生成」造数据，导出成文件后上传</td></tr>
        </tbody>
      </table>
      <div class="callout callout-tip">
        <h4>公共资源的目的是复用</h4>
        <p>一份文件被多条用例引用时，只上传一次即可；更新文件后所有引用方自动用新版本，
        不必逐条用例替换。</p>
      </div>
    `
  },

  'common-element': {
    description: 'UI 自动化的页面元素定位库',
    anchors: [
      { id: 'sub-element-what', title: '元素是什么' },
      { id: 'sub-element-locator', title: '定位方式' },
      { id: 'sub-element-ai', title: 'AI 生成元素' },
      { id: 'sub-element-rules', title: '维护建议' }
    ],
    content: `
      <h3 id="sub-element-what">元素是什么</h3>
      <p>元素是对页面上一个可操作对象的抽象描述（页面地址 + 定位方式 + 定位值），
      例如「登录页的账号输入框」。UI 自动化步骤通过引用元素来操作页面，
      从而把「怎么定位」与「怎么操作」分开——页面改版时只改元素，不用改用例。</p>

      <h3 id="sub-element-locator">定位方式</h3>
      <p>平台支持多种定位方式，按稳定性从高到低推荐使用：</p>
      <table class="doc-table">
        <thead><tr><th style="width:160px">定位方式</th><th>说明</th><th style="width:130px">稳定性</th></tr></thead>
        <tbody>
          <tr><td><b>ID</b></td><td>按元素 id 定位</td><td>高（前提是 id 稳定）</td></tr>
          <tr><td><b>name</b></td><td>按元素 name 属性定位</td><td>高</td></tr>
          <tr><td><b>CSS 选择器</b></td><td>按 CSS 规则定位，写法简洁</td><td>中</td></tr>
          <tr><td><b>XPath</b></td><td>按路径定位，最灵活但易受层级变化影响</td><td>低（尽量避免绝对路径）</td></tr>
          <tr><td><b>链接文本</b></td><td>按 <code>&lt;a&gt;</code> 文本定位</td><td>中</td></tr>
        </tbody>
      </table>
      <div class="callout callout-tip">
        <h4>优先选稳定的定位</h4>
        <p>XPath 里凡是出现 <code>/div[3]/div[2]</code> 这类「按序号定位」的写法，页面一动就会失败。
        优先选 id、name、<code>data-*</code> 属性，或带业务语义的 class。</p>
      </div>

      <h3 id="sub-element-ai">AI 生成元素</h3>
      <p>元素列表页提供<b>「AI 生成」</b>：粘贴页面 HTML 片段或页面地址，由 AI 推断出元素名称与定位方式，
      批量生成元素记录。生成后请逐一核对定位值的正确性，AI 结果作为初稿而非终稿。</p>

      <h3 id="sub-element-rules">维护建议</h3>
      <div class="callout callout-warn">
        <h4>元素改了会波及所有引用它的用例</h4>
        <p>元素是共享资源。修改定位值前请先确认引用范围；只想为个别页面调整时，
        建议新建一个元素而不是改公用元素。</p>
      </div>
      <div class="callout callout-info">
        <h4>命名要带页面前缀</h4>
        <p>建议命名形如 <code>登录页-账号输入框</code>、<code>订单页-提交按钮</code>，
        元素多了以后靠名字就能定位，不必点开看定位值。</p>
      </div>
    `
  },

  'common-enumConfig': {
    description: '常量类与常量项——用例中可以按名字引用的字典',
    anchors: [
      { id: 'sub-enum-fields', title: '字段说明' },
      { id: 'sub-enum-how', title: '操作步骤' },
      { id: 'sub-enum-ref', title: '在用例中怎么引用' },
      { id: 'sub-enum-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-enum-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:180px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>枚举值名称</b>（常量类名）</td><td>常量类的名字，<b>项目内唯一</b>，≤20 字</td></tr>
          <tr><td><b>枚举值描述</b></td><td>这个常量类用来描述什么，≤300 字</td></tr>
          <tr><td><b>枚举值</b></td><td>常量项列表，每项由 <code>name</code>（项名）与 <code>value</code>（实际值）组成</td></tr>
        </tbody>
      </table>
      <p>示例：常量类名 <code>OrderStatus</code>，包含常量项 <code>PAID = 1</code>、<code>SHIPPED = 2</code>、
      <code>CLOSED = 9</code>。用例里写 <code>OrderStatus.PAID</code> 即可拿到 <code>1</code>。</p>

      <h3 id="sub-enum-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新建常量类</h4><p>填写枚举值名称与描述。名称保持稳定，因为它会被用例引用。</p></li>
        <li><h4>2. 添加常量项</h4><p>逐条添加 <code>name</code> 与 <code>value</code>。值可以是数字、字符串或 JSON 片段。</p></li>
        <li><h4>3. 在用例中引用</h4><p>在请求体、参数或断言中写 <code>\${常量类名.常量项名}</code>，执行时自动替换为对应值。</p></li>
      </ol>

      <h3 id="sub-enum-ref">在用例中怎么引用</h3>
      <table class="doc-table">
        <thead><tr><th style="width:280px">写法</th><th>结果</th></tr></thead>
        <tbody>
          <tr><td><code>\${OrderStatus.PAID}</code></td><td>替换为 <code>1</code></td></tr>
        </tbody>
      </table>
      <div class="callout callout-warn">
        <h4>常量优先级的坑</h4>
        <p>引擎替换 <code>\${...}</code> 时会<b>先在执行上下文中查找同名变量</b>，找不到才去常量表里找。
        因此如果上下文里恰好存在同名变量（例如你把某个响应字段也提取成了同名变量），
        实际取到的可能不是你期望的那个值。常量类名建议加业务前缀以避免撞名。</p>
      </div>
      <div class="callout callout-warn">
        <h4>常量项写错会在执行时报错</h4>
        <p>引用的常量类或常量项不存在时，执行会抛出参数解析失败（ParseParamsException），
        该步骤被判为错误。看到这类报错，请优先核对常量类名与项名的大小写是否与配置一致。</p>
      </div>

      <h3 id="sub-enum-rules">注意事项</h3>
      <div class="callout callout-tip">
        <h4>什么该做成常量</h4>
        <p>1. 会随版本变化的枚举（状态码、类型码）——集中维护，改动只改一处。</p>
        <p>2. 多个用例反复出现的固定值（租户号、渠道号）。</p>
        <p>3. <b>不要</b>把随环境变化的值做成常量，那属于<b>环境全局变量</b>。</p>
      </div>
    `
  },

  'common-python': {
    description: '用 Python 封装可复用逻辑，在步骤中调用',
    anchors: [
      { id: 'sub-python-fields', title: '字段说明' },
      { id: 'sub-python-how', title: '操作步骤' },
      { id: 'sub-python-when', title: '什么时候该写用户函数' },
      { id: 'sub-python-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-python-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:170px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>函数名称</b></td><td><b>全局唯一</b>，≤20 字。用例按这个名字调用它，建好后不建议改名</td></tr>
          <tr><td><b>函数描述</b></td><td>说明函数的用途与返回值，≤300 字</td></tr>
          <tr><td><b>导包信息</b></td><td>函数体需要的 import 语句，单独填写</td></tr>
          <tr><td><b>函数体</b></td><td>Python 代码主体</td></tr>
          <tr><td><b>所属模块</b></td><td>服务模块，用于归类</td></tr>
        </tbody>
      </table>

      <h3 id="sub-python-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新建用户函数</h4><p>填写函数名称、描述、导包信息与函数体，选择所属模块，保存。</p></li>
        <li><h4>2. 在用例步骤中引用</h4><p>脚本用例添加步骤时选择<b>用户自定义函数</b>类型，选中该函数并配置入参与返回值提取。</p></li>
        <li><h4>3. 把返回值提取为变量</h4><p>在步骤的提取配置中把返回的第一个值（或按序号取值）设成变量，供后续步骤引用。</p></li>
      </ol>

      <h3 id="sub-python-when">什么时候该写用户函数</h3>
      <table class="doc-table">
        <thead><tr><th style="width:230px">场景</th><th>示例</th></tr></thead>
        <tbody>
          <tr><td>自定义签名 / 加解密</td><td>把参数按规则拼接后做 HMAC 或 AES，产出签名串</td></tr>
          <tr><td>复杂数据加工</td><td>把上一接口的返回加工成下一接口需要的结构</td></tr>
          <tr><td>时间与格式处理</td><td>生成本次执行专属的流水号、格式化时间戳</td></tr>
          <tr><td>公共前置逻辑</td><td>登录、获取租户上下文</td></tr>
        </tbody>
      </table>

      <h3 id="sub-python-rules">注意事项</h3>
      <div class="callout callout-warn">
        <h4>函数名唯一且被用例引用</h4>
        <p>函数名称在项目内唯一，且用例是通过名字调用的。改名或删除会直接导致引用它的用例执行失败，
        请先确认引用范围再操作。</p>
      </div>
      <div class="callout callout-tip">
        <h4>保持函数单一职责</h4>
        <p>一个函数只做一件事，且返回值尽量简单（字符串或简单结构）。
        函数体越长越难维护，复杂逻辑建议拆成多个函数串起来用。
        另外注意导包信息要写在「导包信息」字段里，不要混在函数体中。</p>
      </div>
    `
  },

  'common-step': {
    description: '可被多条用例复用的步骤——接口自动化的复用基石',
    anchors: [
      { id: 'sub-step-fields', title: '字段说明' },
      { id: 'sub-step-types', title: '五类步骤' },
      { id: 'sub-step-how', title: '操作步骤' },
      { id: 'sub-step-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-step-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:180px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>步骤描述</b></td><td>写意图，如「登录并获取 Token」，≤100 字</td></tr>
          <tr><td><b>步骤类型</b></td><td>HTTP 接口请求 / 数据库操作 / Web / App 自动化等</td></tr>
          <tr><td><b>所属平台</b></td><td>步骤归属的前端平台</td></tr>
          <tr><td><b>数据库</b></td><td>数据库操作类步骤必填，选择要连的数据库资源</td></tr>
          <tr><td><b>超时时间</b></td><td>步骤最长等待秒数，默认 7 秒</td></tr>
          <tr><td><b>是否重定向</b></td><td>请求是否自动跟随 302 跳转</td></tr>
          <tr><td><b>是否验证 SSL 证书</b></td><td>自签名证书的内网环境通常需要关闭</td></tr>
          <tr><td><b>是否设置为公共请求头</b></td><td>开启后该请求头在此环境内全局生效</td></tr>
          <tr><td><b>请求方法 / 请求 uri</b></td><td>HTTP 步骤的接口方法与相对路径</td></tr>
          <tr><td><b>请求头 / 请求体 / 查询参数</b></td><td>接口请求的完整定义，支持 <code>\${...}</code> 变量</td></tr>
          <tr><td><b>响应体 / 响应体结构树</b></td><td>用于断言与取值引用的返回结构</td></tr>
          <tr><td><b>断言参数</b></td><td>状态码、字段值、JSON 结构等校验规则</td></tr>
          <tr><td><b>执行条件参数</b></td><td>满足条件才执行该步骤</td></tr>
          <tr><td><b>循环执行参数</b></td><td>让该步骤重复执行（如轮询）</td></tr>
          <tr><td><b>跳出循环参数</b></td><td>满足条件时跳出循环</td></tr>
        </tbody>
      </table>

      <h3 id="sub-step-types">五类步骤</h3>
      <table class="doc-table">
        <thead><tr><th style="width:160px">类型</th><th>用途</th></tr></thead>
        <tbody>
          <tr><td><b>HTTP 接口请求</b></td><td>发送 HTTP 请求并断言响应，接口自动化主力</td></tr>
          <tr><td><b>数据库操作</b></td><td>执行 SQL 做数据准备或结果校验</td></tr>
          <tr><td><b>Web 自动化</b></td><td>基于 Playwright 的浏览器操作，引用元素配置</td></tr>
          <tr><td><b>App 自动化</b></td><td>基于 Appium 的移动端操作</td></tr>
          <tr><td><b>逻辑控制器</b></td><td>条件 / 循环 / 等待等流程控制</td></tr>
        </tbody>
      </table>

      <h3 id="sub-step-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新建步骤</h4><p>选择步骤类型，填写描述与基础配置。</p></li>
        <li><h4>2. 配置请求与断言</h4><p>HTTP 步骤需填完整的请求定义与断言规则；数据库步骤填 SQL；UI 步骤引用元素。</p></li>
        <li><h4>3. 保存为公共步骤</h4><p>保存后该步骤即可被任意用例引用。</p></li>
        <li><h4>4. 在用例中引用</h4><p>在脚本用例的「添加步骤」中选择<b>复用已有步骤</b>（引用原件）或
        <b>引用并创建新步骤</b>（复制一份独立修改）。</p></li>
      </ol>

      <h3 id="sub-step-rules">注意事项</h3>
      <div class="callout callout-info">
        <h4>复用 vs 复制</h4>
        <table class="doc-table">
          <thead><tr><th style="width:200px">方式</th><th>语义</th></tr></thead>
          <tbody>
            <tr><td><b>复用已有步骤</b></td><td>用例与公共步骤是同一个对象。改公共步骤，所有引用方一起变</td></tr>
            <tr><td><b>引用并创建新步骤</b></td><td>复制一份到用例下，改动只影响该用例</td></tr>
          </tbody>
        </table>
        <p>公共逻辑（登录、初始化）用前者；需要个别化的逻辑用后者。</p>
      </div>
      <div class="callout callout-warn">
        <h4>改公共步骤前先看引用范围</h4>
        <p>公共步骤往往被大量用例引用，改断言或改参数结构会让一批用例同时变红。
        改动前请确认影响面，或用「引用并创建新步骤」在用例内做实验。</p>
      </div>
      <div class="callout callout-tip">
        <h4>断言写「业务结果」而不只是「请求成功」</h4>
        <p>只断言 HTTP 200 会漏掉「接口通了但业务失败」的情况。
        建议同时断言业务码字段与关键数据字段，例如 <code>\${resp.code} == 0</code>。</p>
      </div>
    `
  },

  /* ================= 测试资产 ================= */
  'case-knowledgeBase': {
    description: '向量智仓——为 AI 提供业务知识检索上下文',
    anchors: [
      { id: 'sub-kb-what', title: '页面用途' },
      { id: 'sub-kb-how', title: '操作步骤' },
      { id: 'sub-kb-rules', title: '使用建议' }
    ],
    content: `
      <h3 id="sub-kb-what">页面用途</h3>
      <p>向量智仓用于沉淀被测系统的业务知识与接口规范，并把它们切成片段、生成向量存起来，
      供 AI 在生成用例、元素、接口配置时检索参考。可以理解为「给 AI 看的项目知识库」。</p>
      <p>把需求文档、接口文档、业务规则说明放进来，AI 生成的用例会更贴合本项目的实际业务，
      而不是产出一批通用套话。</p>

      <h3 id="sub-kb-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新建知识库</h4><p>创建一个知识库容器，填写名称与描述。</p></li>
        <li><h4>2. 上传文档</h4><p>把需求 / 接口文档上传，平台会解析文本并切分为片段。</p></li>
        <li><h4>3. 等待向量化</h4><p>平台对片段做向量化处理，处理完成后即可被检索。</p></li>
        <li><h4>4. 验证效果</h4><p>在知识库中做一次检索，确认能召回相关片段。</p></li>
      </ol>

      <h3 id="sub-kb-rules">使用建议</h3>
      <div class="callout callout-tip">
        <h4>放什么进来最有价值</h4>
        <p>1. <b>接口文档</b>：字段含义、必填性、取值范围——直接决定生成用例的字段覆盖度。</p>
        <p>2. <b>业务规则</b>：金额上下限、状态流转条件、权限边界——决定边界值用例的质量。</p>
        <p>3. <b>历史缺陷复盘</b>：把踩过的坑写进去，AI 生成的用例会覆盖这些回归点。</p>
      </div>
      <div class="callout callout-warn">
        <h4>不要放过期文档</h4>
        <p>向量检索会召回语义相近的片段，过期的接口文档会污染检索结果，导致 AI 生成基于旧字段的用例。
        版本迭代时请同步更新或清理知识库内容。</p>
      </div>
    `
  },

  'case-tag': {
    description: '用例标签体系——用于筛选与批量组织',
    anchors: [
      { id: 'sub-tag-fields', title: '字段说明' },
      { id: 'sub-tag-how', title: '操作步骤' },
      { id: 'sub-tag-rules', title: '打标建议' }
    ],
    content: `
      <h3 id="sub-tag-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>标签名称</b></td><td>标签标识，建议简短且含义明确</td></tr>
          <tr><td><b>标签描述</b></td><td>说明这个标签的使用约定</td></tr>
        </tbody>
      </table>
      <p>标签会同时出现在<b>功能用例</b>与<b>脚本用例</b>上（用例与标签是多对多关系，一条用例可打多个标签）。</p>

      <h3 id="sub-tag-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 建立标签</h4><p>先规划好标签体系再建，避免后期出现「冒烟 / smoke / 主流程」三套同义标签。</p></li>
        <li><h4>2. 给用例打标</h4><p>在功能用例或脚本用例的新增 / 编辑中勾选标签。</p></li>
        <li><h4>3. 按标签筛选</h4><p>在用例列表用标签筛选，快速圈定要回归的范围。</p></li>
        <li><h4>4. 批量组织</h4><p>套件使用动态模式时，可把标签作为筛选用例的条件之一。</p></li>
      </ol>

      <h3 id="sub-tag-rules">打标建议</h3>
      <table class="doc-table">
        <thead><tr><th style="width:150px">维度</th><th>示例标签</th><th>用途</th></tr></thead>
        <tbody>
          <tr><td><b>优先级</b></td><td>P0、P1、P2</td><td>决定回归深度，P0 必跑</td></tr>
          <tr><td><b>测试类型</b></td><td>冒烟、回归、边界、异常</td><td>按测试目的圈范围</td></tr>
          <tr><td><b>业务域</b></td><td>登录、订单、支付</td><td>按业务模块圈范围</td></tr>
          <tr><td><b>状态</b></td><td>稳定、待优化、已知失败</td><td>标记用例本身质量，避免长期红灯被无视</td></tr>
        </tbody>
      </table>
      <div class="callout callout-tip">
        <h4>标签不宜过多</h4>
        <p>标签的价值在于「筛得准」。控制维度在 2~3 个、每个维度 3~5 个值最实用。
        超过这个量级，说明应该用模块或套件来组织，而不是继续加标签。</p>
      </div>
    `
  },

  'case-api': {
    description: '接口文档管理、在线调试与 Mock',
    anchors: [
      { id: 'sub-api-fields', title: '字段说明' },
      { id: 'sub-api-how', title: '新建接口的完整步骤' },
      { id: 'sub-api-debug', title: '在线调试' },
      { id: 'sub-api-mock', title: 'Mock 功能' },
      { id: 'sub-api-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-api-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:180px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>接口名称</b></td><td>业务语义命名，≤50 字</td></tr>
          <tr><td><b>接口状态</b></td><td>
            <span class="badge">已发布</span><span class="badge">设计中</span><span class="badge">待确定</span>
            <span class="badge">开发</span><span class="badge">对接</span><span class="badge">测试</span>
            <span class="badge">完成</span><span class="badge">异常</span><span class="badge">维护</span><span class="badge">废弃</span>
          </td></tr>
          <tr><td><b>所属服务</b></td><td>来自「环境管理 → 服务配置」</td></tr>
          <tr><td><b>所属模块</b></td><td>来自该服务下的服务模块</td></tr>
          <tr><td><b>请求地址</b></td><td><b>填相对路径</b>，如 <code>/user/login/</code>；域名由环境的服务域名提供</td></tr>
          <tr><td><b>请求方法</b></td><td>GET / POST / PUT / PATCH / DELETE 等</td></tr>
          <tr><td><b>请求头</b></td><td>键值对形式，支持变量引用</td></tr>
          <tr><td><b>body 类型</b></td><td><span class="badge">JSON</span><span class="badge">Form-data</span></td></tr>
          <tr><td><b>json 请求体</b></td><td>body 类型为 JSON 时填写，支持变量引用</td></tr>
          <tr><td><b>查询参数</b></td><td>URL 上的 Query 参数</td></tr>
          <tr><td><b>数据返回体</b></td><td>接口返回样例，平台据此解析字段树</td></tr>
          <tr><td><b>返回体结构树</b></td><td>解析后的字段树，供断言与取值引用选择</td></tr>
          <tr><td><b>json 根类型</b> / <b>response 根类型</b></td><td>object 或 array，影响字段树解析方式</td></tr>
        </tbody>
      </table>

      <h3 id="sub-api-how">新建接口的完整步骤</h3>
      <ol class="step-list">
        <li><h4>1. 填基本信息</h4><p>接口名称、所属服务、所属模块、请求方法、请求地址（相对路径）。</p></li>
        <li><h4>2. 配请求头</h4><p>把该接口必需的头部写全（如 <code>Content-Type</code>、鉴权头）。</p></li>
        <li><h4>3. 配请求体</h4><p>选择 body 类型并填写内容。敏感值（密码、token）用变量而不是明文。</p></li>
        <li><h4>4. 配查询参数</h4><p>GET 接口参数写在这里，POST 接口如需 Query 参数也一并填写。</p></li>
        <li><h4>5. 贴返回体并解析</h4><p>切换到返回体页签，粘贴真实返回样例；若是数组返回，把 response 根类型设为 array。</p></li>
        <li><h4>6. 调试</h4><p>选择环境后发起调试请求，对照返回确认配置无误（请求头、方法、路径、编码）。</p></li>
        <li><h4>7. 保存</h4><p>保存后即可在脚本用例中以 HTTP 步骤引用。</p></li>
      </ol>
      <div class="callout callout-tip">
        <h4>用「AI 生成配置」省录入时间</h4>
        <p>接口编辑页提供<b>AI 生成配置</b>：把接口文档文本粘进去，自动产出请求头、请求体与返回体结构。
        生成是后台异步任务，页面会显示「AI 生成中…」状态。生成结果请核对后再保存。</p>
      </div>

      <h3 id="sub-api-debug">在线调试</h3>
      <p>调试功能让接口在落库前先验证一遍，是「先确认接口真的能通，再写用例」的关键一步。
      调试时请注意：</p>
      <ul>
        <li>必须先选择<b>环境</b>，否则域名无从确定。</li>
        <li>鉴权类接口的 token 需要先通过登录接口拿到，或使用环境全局变量预置。</li>
        <li>请求地址写相对路径；若写成绝对地址，会与环境的服务域名拼接产生错误 URL。</li>
      </ul>

      <h3 id="sub-api-mock">Mock 功能</h3>
      <p>每个接口可配置多个 Mock：</p>
      <table class="doc-table">
        <thead><tr><th style="width:170px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>mock 名称 / 描述</b></td><td>便于区分不同场景（如「成功返回」「余额不足」）</td></tr>
          <tr><td><b>是否启用</b></td><td>总开关</td></tr>
          <tr><td><b>Mock 响应状态码</b></td><td>默认 200，可模拟 4xx / 5xx</td></tr>
          <tr><td><b>Mock 延长响应时间</b></td><td>人为延迟，用于验证前端超时处理与弱网表现</td></tr>
          <tr><td><b>resbody 类型</b></td><td>自定义 JSON，或跟随 API 文档的返回体</td></tr>
          <tr><td><b>请求头 / 返回体 / 参数</b></td><td>Mock 返回的头部与数据体</td></tr>
        </tbody>
      </table>
      <div class="callout callout-tip">
        <h4>Mock 的典型用途</h4>
        <p>1. 后端接口还没开发完，前端联调与测试用例可以先行。</p>
        <p>2. 模拟异常分支：把状态码改成 500、返回体改成错误结构，验证被测系统的容错逻辑。</p>
        <p>3. 用「延长响应时间」验证超时与重试机制。</p>
      </div>

      <h3 id="sub-api-rules">注意事项</h3>
      <div class="callout callout-warn">
        <h4>请求地址务必写相对路径</h4>
        <p>这是最常见的接口失败原因：把 <code>http://xxx/api/user</code> 整段填进请求地址，
        平台再拼上环境的服务域名，就会生成 <code>域名/域名/api/user</code> 这样的错误 URL。</p>
      </div>
      <div class="callout callout-warn">
        <h4>返回体结构变更要同步更新</h4>
        <p>断言与 <code>\${...}</code> 取值都依赖返回体结构树。被测系统改了字段名或层级后，
        请先更新接口的返回体，再检查引用该字段的用例。</p>
      </div>
      <div class="callout callout-info">
        <h4>接口被用例引用时不会丢</h4>
        <p>删除接口采用软删除，历史记录保留，且名称唯一性只在未删除集合内校验——
        因此删除后的同名接口可以重建。</p>
      </div>
    `
  },

  'case-funcCase': {
    description: '面向人工执行的功能用例：前置条件、步骤、预期结果与评审状态',
    anchors: [
      { id: 'sub-func-fields', title: '字段说明' },
      { id: 'sub-func-how', title: '操作步骤' },
      { id: 'sub-func-ai', title: 'AI 生成用例' },
      { id: 'sub-func-rules', title: '编写建议' }
    ],
    content: `
      <h3 id="sub-func-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:190px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>用例名称</b></td><td>业务语义命名，≤50 字</td></tr>
          <tr><td><b>所属模块</b></td><td>服务模块，决定用例归类</td></tr>
          <tr><td><b>负责人</b></td><td>用例维护责任人</td></tr>
          <tr><td><b>标签</b></td><td>可多选，用于筛选与组织</td></tr>
          <tr><td><b>前置条件</b></td><td>执行该用例前必须满足的条件（账号、数据、状态）</td></tr>
          <tr><td><b>用例备注</b></td><td>补充说明、设计思路、已知限制</td></tr>
          <tr><td><b>步骤类型</b></td><td><span class="badge">文本描述</span><span class="badge">步骤描述</span></td></tr>
          <tr><td><b>文本步骤</b></td><td>步骤类型为「文本描述」时用纯文字描述执行过程</td></tr>
          <tr><td><b>期望结果</b></td><td>用例执行后应有的结果</td></tr>
          <tr><td><b>表格步骤</b></td><td>步骤类型为「步骤描述」时，用表格式维护步骤与预期</td></tr>
          <tr><td><b>是否可实现自动化</b></td><td>
            <span class="badge">全自动化</span><span class="badge">半自动化</span><span class="badge">手工测试</span>
          </td></tr>
          <tr><td><b>自动化状态</b></td><td>
            <span class="badge">已完成</span><span class="badge">进行中</span><span class="badge">待开始</span><span class="badge">手工测试</span>
          </td></tr>
          <tr><td><b>用例状态</b></td><td>
            <span class="badge">待修改</span><span class="badge">待评审</span><span class="badge">已评审</span>
          </td></tr>
          <tr><td><b>关联自动化用例</b></td><td>把功能用例与实现它的脚本用例挂起来</td></tr>
        </tbody>
      </table>

      <h3 id="sub-func-how">操作步骤</h3>
      <ol class="step-list">
        <li><h4>1. 新建用例</h4><p>填写用例名称，选择模块、负责人与标签。</p></li>
        <li><h4>2. 写前置条件</h4><p>把执行依赖写清楚：用什么账号、需要什么数据、系统处于什么状态。</p></li>
        <li><h4>3. 写步骤</h4><p>选择步骤类型。建议用<b>步骤描述</b>的表格形式，好处是「操作 + 预期」一一对应，便于人工执行时逐条打勾。</p></li>
        <li><h4>4. 写期望结果</h4><p>结论性描述，要与步骤中的预期一致。</p></li>
        <li><h4>5. 标注自动化属性</h4><p>设置「是否可实现自动化」与「自动化状态」，便于统计自动化覆盖率。</p></li>
        <li><h4>6. 关联脚本用例</h4><p>如果已有对应脚本用例，在关联项中挂上。</p></li>
        <li><h4>7. 送评审</h4><p>用例状态从「待修改」推进到「待评审」，评审通过后置为「已评审」。</p></li>
      </ol>

      <h3 id="sub-func-ai">AI 生成用例</h3>
      <p>两种入口：</p>
      <table class="doc-table">
        <thead><tr><th style="width:200px">入口</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>AI 助手悬浮球</b></td><td>对话式生成，生成的用例自动保存并标记 <code>case_mark='AI生成'</code></td></tr>
          <tr><td><b>功能用例列表 → AI 生成</b></td><td>按模块批量生成用例</td></tr>
          <tr><td><b>功能用例列表 → AI 生成脚本</b></td><td>把功能用例转成脚本用例骨架</td></tr>
        </tbody>
      </table>
      <div class="callout callout-warn">
        <h4>AI 生成必须复核</h4>
        <p>AI 产出的是<b>初稿</b>：可能遗漏边界条件、引用不存在的字段、或与业务规则不符。
        请务必逐条核对后再把状态置为「已评审」。可在列表页按 <code>AI生成</code> 标记筛选出这批用例集中复核。</p>
      </div>

      <h3 id="sub-func-rules">编写建议</h3>
      <div class="callout callout-tip">
        <h4>四条质量线</h4>
        <p><b>独立</b>：尽量不依赖其他用例的执行结果，能单独跑。</p>
        <p><b>可重复</b>：同样条件下多次执行结果一致，不产生脏数据。</p>
        <p><b>针对</b>：一条用例聚焦一个验证点，不要把五个检查塞进一条。</p>
        <p><b>可维护</b>：步骤写业务动作而不是控件操作，改版时不必重写。</p>
      </div>
      <div class="callout callout-info">
        <h4>边界与异常要有姓名</h4>
        <p>除了主流程，请覆盖：空值、超长、特殊字符、权限不足、并发冲突、金额边界（0 / 负数 / 上限 / 上限+1）。
        这些用例才是缺陷的主要来源。</p>
      </div>
    `
  },

  'case-scriptCase': {
    description: '面向机器执行的自动化用例：步骤序列、变量、断言',
    anchors: [
      { id: 'sub-script-fields', title: '字段说明' },
      { id: 'sub-script-type', title: '用例类型与可选步骤' },
      { id: 'sub-script-how', title: '编排一条接口用例' },
      { id: 'sub-script-var', title: '变量与断言' },
      { id: 'sub-script-rules', title: '注意事项' }
    ],
    content: `
      <h3 id="sub-script-fields">字段说明</h3>
      <table class="doc-table">
        <thead><tr><th style="width:190px">字段</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>用例名称</b></td><td>≤50 字，建议与对应功能用例同名，便于对照</td></tr>
          <tr><td><b>用例类型</b></td><td>
            <span class="badge">API Case</span><span class="badge">WEB_UI Case</span><span class="badge">APP_UI Case</span>
            <span class="badge">DATA CASE</span><span class="badge">Performance Case</span>
          </td></tr>
          <tr><td><b>所属模块</b></td><td>服务模块</td></tr>
          <tr><td><b>标签</b></td><td>可多选</td></tr>
          <tr><td><b>用例全局变量设置</b></td><td>该用例特有的变量（名称 / 值）</td></tr>
          <tr><td><b>测试数据集合</b></td><td>数据驱动用的数据集，让同一条用例跑多组数据</td></tr>
          <tr><td><b>步骤</b></td><td>用例的执行序列，含步骤序号、步骤变量、是否执行、失败处理策略</td></tr>
          <tr><td><b>用例执行结果</b></td><td>最近一次执行的结果：成功 / 失败 / 错误 / 未执行</td></tr>
        </tbody>
      </table>
      <p>步骤级可配置：</p>
      <table class="doc-table">
        <thead><tr><th style="width:190px">配置</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td><b>所属用例的第几步</b></td><td>步骤在序列中的位置</td></tr>
          <tr><td><b>步骤变量参数</b></td><td>该步骤特有的变量覆盖值</td></tr>
          <tr><td><b>父步骤</b></td><td>归属哪个控制器（用于条件 / 循环体）</td></tr>
          <tr><td><b>是否执行该步骤</b></td><td>临时跳过某步做调试</td></tr>
          <tr><td><b>失败后如何处理</b></td><td>
            <span class="badge">停止测试</span><span class="badge">继续执行</span><span class="badge">继续执行并忽略失败</span>
          </td></tr>
        </tbody>
      </table>

      <h3 id="sub-script-type">用例类型与可选步骤</h3>
      <table class="doc-table">
        <thead><tr><th style="width:170px">用例类型</th><th>可用的附加步骤</th></tr></thead>
        <tbody>
          <tr><td><b>API Case</b></td><td>HTTP 接口请求、数据库操作、复用步骤、用户函数</td></tr>
          <tr><td><b>WEB_UI Case</b></td><td>UI 类型为 2 时才会出现「Web 自动化」步骤选项</td></tr>
          <tr><td><b>APP_UI Case</b></td><td>UI 类型为 3 时才会出现「App 自动化」步骤选项</td></tr>
          <tr><td><b>Performance Case</b></td><td>用于性能压测，可加事务控制器合并统计</td></tr>
        </tbody>
      </table>
      <div class="callout callout-info">
        <h4>「添加步骤」里为什么看不到 Web / App 选项</h4>
        <p>这两个选项是<b>按用例类型条件显示</b>的：Web 自动化只在 WEB_UI 用例下出现，
        App 自动化只在 APP_UI 用例下出现。如果看不到，请先检查用例类型是否选对。</p>
      </div>

      <h3 id="sub-script-how">编排一条接口用例</h3>
      <ol class="step-list">
        <li><h4>1. 新建用例</h4><p>填写名称，选择用例类型（接口测试选 API Case）与模块。</p></li>
        <li><h4>2. 加登录步骤</h4><p>「添加步骤 → 复用已有步骤」，选择公共的登录步骤（或用 HTTP 接口请求步骤直接引用登录接口）。</p></li>
        <li><h4>3. 提取 Token</h4><p>在登录步骤上配置提取，把返回体中的 token 字段存为变量，例如 <code>Token</code>。</p></li>
        <li><h4>4. 加业务请求步骤</h4><p>继续添加业务接口步骤，在请求头中写 <code>Authorization: \${Token}</code> 引用上一步提取的值。</p></li>
        <li><h4>5. 配断言</h4><p>给业务步骤加断言：状态码、业务码字段、关键数据字段。</p></li>
        <li><h4>6. 调试执行</h4><p>保存后单跑一次，看日志确认每一步的请求与响应符合预期。</p></li>
        <li><h4>7. 加入套件</h4><p>确认无误后，到<b>执行中心 → 套件管理</b>把用例加入套件做批量回归。</p></li>
      </ol>

      <h3 id="sub-script-var">变量与断言</h3>
      <p>变量按生效范围分为三层，命名时注意区分以免互相覆盖：</p>
      <table class="doc-table">
        <thead><tr><th style="width:190px">层级</th><th>生效范围</th><th>适用内容</th></tr></thead>
        <tbody>
          <tr><td><b>环境全局变量</b></td><td>该环境内所有用例</td><td>账号、域名派生值、租户号——随环境变化的值</td></tr>
          <tr><td><b>用例全局变量</b></td><td>该用例内所有步骤</td><td>该用例特有的固定值与中间结果</td></tr>
          <tr><td><b>步骤变量</b></td><td>该步骤内</td><td>仅本步骤使用的参数覆盖</td></tr>
          <tr><td><b>步骤提取结果</b></td><td>提取之后的所有步骤</td><td>上一个接口返回的 token、ID、流水号</td></tr>
        </tbody>
      </table>
      <div class="callout callout-warn">
        <h4>作用域是单向的</h4>
        <p>只能「后面的步骤引用前面提取的变量」。如果第 3 步引用了第 5 步才会产生的变量，
        执行时必然解析失败。排错时先看日志里是<b>哪一步</b>报参数解析失败，再往前找该变量是否已被赋值。</p>
      </div>

      <h3 id="sub-script-rules">注意事项</h3>
      <div class="callout callout-tip">
        <h4>失败处理策略怎么选</h4>
        <p><b>停止测试</b>（默认）：后续步骤依赖前面结果时用，避免连环报错。</p>
        <p><b>继续执行</b>：步骤彼此独立时用，一次跑完拿到完整失败清单。</p>
        <p><b>继续执行并忽略失败</b>：用于非关键步骤（如某些清理动作、可选埋点校验），失败不影响整体结论。</p>
      </div>
      <div class="callout callout-info">
        <h4>数据驱动让一条用例跑多组数据</h4>
        <p>把变化的输入抽成变量，在<b>测试数据集合</b>中准备多组值，同一条用例即可覆盖多组场景，
        比复制多条用例更好维护。</p>
      </div>
      <div class="callout callout-warn">
        <h4>用例结果里的「错误」不等于「失败」</h4>
        <p>「失败」是断言未通过（业务不符）；「错误」是执行中抛异常（变量解析失败、主机解析不到、
        步骤类型不支持等）。定位方式完全不同：前者查业务，后者查日志里的异常堆栈。</p>
      </div>
    `
  }
}

export default assetsChildren
