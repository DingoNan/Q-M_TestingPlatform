<template>
  <div class="test-tools-container">
    <!-- 顶部固定导航栏 - 高度90px -->
    <div class="fixed-header elegant-shadow">
      <div class="header-content">
        <!-- Logo区域 -->
        <div class="logo-section">
          <div class="logo-wrapper">
            <div class="logo-circle">
              <svg class="logo-icon" viewBox="0 0 100 100">
                <path d="M50,10 L90,30 L90,70 L50,90 L10,70 L10,30 Z" class="logo-hexagon"></path>
                <circle cx="50" cy="50" r="20" class="logo-center"></circle>
                <path d="M35,35 L65,35 L65,65 L35,65 Z" class="logo-square"></path>
              </svg>
              <div class="logo-glow"></div>
            </div>
            <div class="platform-info">
              <h1 class="platform-name">BlackBagTest</h1>
              <p class="platform-slogan">开发者测试工具箱</p>
            </div>
          </div>
        </div>

        <!-- 优化后的搜索区域 -->
        <div class="search-section">
          <div class="search-container">
            <el-input
              v-model="searchKeyword"
              placeholder="🔍 搜索工具名称或描述..."
              clearable
              @input="filterTools"
              size="large"
              class="search-input"
            >
              <template #prefix>
                <el-icon class="search-icon"><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 - 工具分组卡片 -->
    <div class="main-content">
      <div class="content-wrapper">
        <div v-for="group in filteredGroups" :key="group.name" class="group-container">
          <el-card class="group-card elegant-shadow">
            <template #header>
              <div class="card-header">
                <div class="group-title-section">
                  <div class="group-title-wrapper">
                    <div class="group-indicator"></div>
                    <h3 class="group-title">{{ group.name }}</h3>
                  </div>
                  <el-tag size="small" type="info" effect="plain" class="group-count">
                    {{ group.tools.length }} 个工具
                  </el-tag>
                </div>
              </div>
            </template>

            <div class="tools-grid">
              <div
                v-for="tool in group.tools"
                :key="tool.id"
                class="tool-item"
                @click="openToolDialog(tool)"
              >
                <el-card class="tool-card" :class="{ 'tool-card-hover': true }">
                  <div class="tool-content">
                    <div class="tool-icon-wrapper">
                      <div class="tool-icon-bg" :style="{ backgroundColor: tool.color }">
                        <el-icon :size="28" color="white">
                          <component :is="tool.icon" />
                        </el-icon>
                      </div>
                    </div>
                    <div class="tool-info">
                      <h4 class="tool-name">{{ tool.name }}</h4>
                      <p class="tool-description">{{ tool.description }}</p>
                    </div>
                  </div>
                </el-card>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 空状态 -->
        <div v-if="filteredGroups.length === 0" class="empty-state">
          <div class="empty-state-content">
            <el-icon class="empty-state-icon"><Tools /></el-icon>
            <h3 class="empty-state-title">未找到相关工具</h3>
            <p class="empty-state-description">尝试使用其他关键词搜索</p>
            <el-button type="primary" @click="searchKeyword = ''" class="empty-state-btn">
              清除搜索
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 工具功能对话框 - 包含所有工具的界面 -->
    <el-dialog
      v-model="dialogVisible"
      :title="currentTool ? currentTool.name : '工具'"
      width="800"
      class="elegant-dialog tool-dialog"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div class="tool-dialog-content" v-if="currentTool">
        <!-- ================= 测试数据生成 ================= -->
        <!-- 身份证正反面 -->
        <div v-if="currentTool.id === 'idcard'">
          <el-form label-position="top">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="姓名">
                  <el-input
                    v-model="idcardName"
                    placeholder="请输入姓名"
                    @input="updateIdCardInfo"
                    class='input'
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="出生日期">
                  <el-date-picker
                    v-model="idcardBirthDate"
                    type="date"
                    class='date'
                    placeholder="选择出生日期"
                    value-format="YYYY-MM-DD"
                    @change="updateIdCardInfo"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="性别">
                  <el-radio-group v-model="idcardGender" @change="updateIdCardInfo" style="width: 100%">
                    <el-radio label="男">男</el-radio>
                    <el-radio label="女">女</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="省市区">
                  <el-cascader
                    v-model="idcardProvinceCity"
                    :options="addressOptions"
                    placeholder="选择省市区"
                    @change="updateIdCardInfo"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="详细地址">
                  <el-input
                    v-model="idcardDetailAddress"
                    placeholder="请输入详细地址"
                    class='input'
                    @input="updateIdCardInfo"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item v-if="idcardFrontImage || idcardBackImage">
              <div style="display: flex; gap: 30px; justify-content: center; flex-wrap: wrap; align-items: flex-start;">
                <div v-if="idcardFrontImage" style="text-align: center;">
                  <h4 style="text-align: center; margin-bottom: 15px; color: #1a5fb4; font-weight: bold;">身份证正面</h4>
                  <img :src="idcardFrontImage" style="width: 323px; height: 204px; border: 2px solid #ccc; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
                </div>
                <div v-if="idcardBackImage" style="text-align: center;">
                  <h4 style="text-align: center; margin-bottom: 15px; color: #1a5fb4; font-weight: bold;">身份证反面</h4>
                  <img :src="idcardBackImage" style="width: 323px; height: 204px; border: 2px solid #ccc; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
                </div>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 银行卡号 -->
        <div v-if="currentTool.id === 'bankcard'">
          <el-form label-position="top">
            <el-form-item v-if="bankCard">
              <el-input v-model="bankCard" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 证件号 -->
        <div v-if="currentTool.id === 'idnumber'">
          <el-form label-position="top">
            <el-form-item label="证件类型">
              <el-radio-group v-model="idType" @change="generateIdNumber">
                <el-radio label="idcard">身份证</el-radio>
                <el-radio label="passport">护照</el-radio>
                <el-radio label="military">军人证</el-radio>
                <el-radio label="hkmt">港澳台居民居住证</el-radio>
                <el-radio label="foreigner">外国人永久居住证</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item v-if="idNumber">
              <el-input v-model="idNumber" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 中文姓名 -->
        <div v-if="currentTool.id === 'chineseName'">
          <el-form label-position="top">
            <el-form-item v-if="chineseName">
              <el-input v-model="chineseName" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 手机号 -->
        <div v-if="currentTool.id === 'mobile'">
          <el-form label-position="top">
            <el-form-item v-if="mobile">
              <el-input v-model="mobile" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 邮箱地址 -->
        <div v-if="currentTool.id === 'email'">
          <el-form label-position="top">
            <el-form-item v-if="email">
              <el-input v-model="email" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 地址信息 -->
        <div v-if="currentTool.id === 'address'">
          <el-form label-position="top">
            <el-form-item v-if="address">
              <el-input v-model="address" type="textarea" :rows="2" readonly class='text'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 公司名称 -->
        <div v-if="currentTool.id === 'company'">
          <el-form label-position="top">
            <el-form-item v-if="company">
              <el-input v-model="company" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 香港身份证 -->
        <div v-if="currentTool.id === 'hkid'">
          <el-form label-position="top">
            <el-form-item>
              <el-button type="primary" @click="generateHkId">生成随机香港身份证号</el-button>
            </el-form-item>
            <el-form-item v-if="hkId">
              <el-input v-model="hkId" readonly />
              <div class="copy-btn"><el-button text size="small" @click="copyToClipboard(hkId)">复制</el-button></div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 营业执照号 -->
        <div v-if="currentTool.id === 'license'">
          <el-form label-position="top">
            <el-form-item v-if="license">
              <el-input v-model="license" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 经纬度坐标 -->
        <div v-if="currentTool.id === 'coords'">
          <el-form label-position="top">
            <el-form-item v-if="coords">
              <el-input v-model="coords" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 用户档案 -->
        <div v-if="currentTool.id === 'profile'">
          <el-form label-position="top">
            <el-form-item v-if="profile">
              <el-input v-model="profile" type="textarea" :rows="6" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- ================= JSON 处理 ================= -->
        <!-- JSON 格式化 -->
        <div v-if="currentTool.id === 'jsonFormat'">
          <el-form label-position="top">
            <el-form-item label="输入 JSON">
              <el-input v-model="jsonInput" type="textarea" :rows="6" placeholder='{"key":"value"}' class="mono-input text" />
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="jsonOutput" type="textarea" :rows="6" readonly class="mono-input text" />
            </el-form-item>
          </el-form>
        </div>

        <!-- JSON 校验 -->
        <div v-if="currentTool.id === 'jsonValidate'">
          <el-form label-position="top">
            <el-form-item label="输入 JSON">
              <el-input v-model="jsonValidateInput" type="textarea" :rows="6" placeholder='{"key":"value"}' class="mono-input text" />
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="jsonValidateOutput" type="textarea" :rows="4" readonly class="mono-input text" />
            </el-form-item>
          </el-form>
        </div>

        <!-- JSON 对比增强 -->
        <div v-if="currentTool.id === 'jsonDiff'">
          <el-form label-position="top">
            <el-form-item label="JSON 原始数据">
              <el-input v-model="jsonDiffLeft" type="textarea" :rows="5" placeholder='{"a":1}' class="mono-input text" />
            </el-form-item>
            <el-form-item label="JSON 对比数据">
              <el-input v-model="jsonDiffRight" type="textarea" :rows="5" placeholder='{"a":2}' class="mono-input text" />
            </el-form-item>
            <el-form-item label="差异结果">
              <el-input v-model="jsonDiffOutput" type="textarea" :rows="8" readonly class="mono-input text" />
            </el-form-item>
          </el-form>
        </div>

        <!-- JSONPath 查询 -->
        <div v-if="currentTool.id === 'jsonpath'">
          <el-form label-position="top">
            <el-form-item label="JSON 数据">
              <el-input v-model="jsonPathData" type="textarea" :rows="6" placeholder='{"store":{"book":[{"title":"Book1"}]}}' class="mono-input text" />
            </el-form-item>
            <el-form-item label="JSONPath 表达式">
              <el-input v-model="jsonPathExpr" placeholder="$.store.book[*].title" class='input' />
            </el-form-item>
            <el-form-item label="查询结果">
              <el-input v-model="jsonPathResult" type="textarea" :rows="6" readonly class="mono-input text" />
            </el-form-item>
          </el-form>
        </div>

        <!-- JSON 扁平化 -->
        <div v-if="currentTool.id === 'jsonFlatten'">
          <el-form label-position="top">
            <el-form-item label="JSON 对象">
              <el-input v-model="jsonFlattenInput" type="textarea" :rows="6" placeholder='{"a":{"b":1}}' class="mono-input text" />
            </el-form-item>
            <el-form-item label="扁平化结果">
              <el-input v-model="jsonFlattenOutput" type="textarea" :rows="6" readonly class="mono-input text" />
            </el-form-item>
          </el-form>
        </div>

        <!-- JSON 路径列表 -->
        <div v-if="currentTool.id === 'jsonPaths'">
          <el-form label-position="top">
            <el-form-item label="JSON 数据">
              <el-input v-model="jsonPathsInput" type="textarea" :rows="6" placeholder='{"a":1,"b":{"c":2}}' class="mono-input text" />
            </el-form-item>
            <el-form-item label="路径列表">
              <el-input v-model="jsonPathsOutput" type="textarea" :rows="8" readonly class="mono-input text" />
            </el-form-item>
          </el-form>
        </div>

        <!-- JSON 转 XML -->
        <div v-if="currentTool.id === 'jsonToXml'">
          <el-form label-position="top">
            <el-form-item label="JSON 数据">
              <el-input v-model="jsonToXmlInput" type="textarea" :rows="6" placeholder='{"root":{"item":"value"}}' class="mono-input text" />
            </el-form-item>
            <el-form-item label="XML 结果">
              <el-input v-model="jsonToXmlOutput" type="textarea" :rows="8" readonly class="mono-input text" />
            </el-form-item>
          </el-form>
        </div>

        <!-- XML 转 JSON -->
        <div v-if="currentTool.id === 'xmlToJson'">
          <el-form label-position="top">
            <el-form-item label="XML 数据">
              <el-input v-model="xmlToJsonInput" type="textarea" :rows="6" placeholder='<root><item>value</item></root>' class="mono-input text" />
            </el-form-item>
            <el-form-item label="JSON 结果">
              <el-input v-model="xmlToJsonOutput" type="textarea" :rows="8" readonly class="mono-input text" />
            </el-form-item>
          </el-form>
        </div>

        <!-- JSON 转 YAML -->
        <div v-if="currentTool.id === 'jsonToYaml'">
          <el-form label-position="top">
            <el-form-item label="JSON 数据">
              <el-input v-model="jsonToYamlInput" type="textarea" :rows="6" placeholder='{"key":"value"}' class="mono-input text" />
            </el-form-item>
            <el-form-item label="YAML 结果">
              <el-input v-model="jsonToYamlOutput" type="textarea" :rows="8" readonly class="mono-input text" />
            </el-form-item>
          </el-form>
        </div>

        <!-- YAML 转 JSON -->
        <div v-if="currentTool.id === 'yamlToJson'">
          <el-form label-position="top">
            <el-form-item label="YAML 数据">
              <el-input v-model="yamlToJsonInput" type="textarea" :rows="6" placeholder="key: value" class="mono-input text" />
            </el-form-item>
            <el-form-item label="JSON 结果">
              <el-input v-model="yamlToJsonOutput" type="textarea" :rows="8" readonly class="mono-input text" />
            </el-form-item>
          </el-form>
        </div>

        <!-- ================= 编码转换 ================= -->
        <!-- 条形码生成 -->
        <div v-if="currentTool.id === 'barcode'">
          <el-form label-position="top">
            <el-form-item label="条形码内容">
              <el-input v-model="barcodeText" placeholder="输入要编码的内容" class='text' type='textarea'/>
            </el-form-item>
            <el-form-item>
              <canvas ref="barcodeCanvas" style="display: none;"></canvas>
              <img v-if="barcodeImage" :src="barcodeImage" style="max-width: 100%;" />
            </el-form-item>
          </el-form>
        </div>

        <!-- 二维码生成 -->
        <div v-if="currentTool.id === 'qrcode'">
          <el-form label-position="top">
            <el-form-item label="二维码内容">
              <el-input v-model="qrcodeText" placeholder="输入要编码的内容" class='text' type='textarea'/>
            </el-form-item>
            <el-form-item v-if="qrcodeImage">
              <img :src="qrcodeImage" style="max-width: 200px;" />
            </el-form-item>
          </el-form>
        </div>

        <!-- 二维码解析 -->
        <div v-if="currentTool.id === 'qrcodeDecode'">
          <el-form label-position="top">
            <el-form-item label="上传二维码图片">
              <input type="file" accept="image/*" @change="onQRCodeUpload" />
            </el-form-item>
            <el-form-item v-if="qrcodeDecodedText">
              <el-input v-model="qrcodeDecodedText" type="textarea" :rows="4" readonly class='text' />
            </el-form-item>
          </el-form>
        </div>

        <!-- 时间戳转换 -->
        <div v-if="currentTool.id === 'timestampConv'">
          <el-form label-position="top">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Unix 时间戳（秒）">
                  <el-input-number v-model="timestampSeconds" :precision="0" :step="1" controls-position="right" class="full-width" />
                  <div><el-button size="small" @click="setCurrentTimestamp">当前时间戳</el-button></div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="日期时间">
                  <el-date-picker v-model="timestampDate" type="datetime" placeholder="选择日期时间" class="full-width" value-format="YYYY-MM-DD HH:mm:ss" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item>
              <el-button type="primary" @click="timestampToDate">时间戳 → 日期</el-button>
              <el-button @click="dateToTimestamp">日期 → 时间戳</el-button>
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="timestampOutput" type="textarea" :rows="2" readonly class='text' />
            </el-form-item>
          </el-form>
        </div>

        <!-- 进制转换 -->
        <div v-if="currentTool.id === 'baseConvert'">
          <el-form label-position="top">
            <el-form-item label="数值">
              <el-input v-model="baseNumber" placeholder="输入数值" class='input' />
            </el-form-item>
            <el-form-item label="源进制">
              <el-input-number v-model="baseFrom" :min="2" :max="36" class='input'/>
            </el-form-item>
            <el-form-item label="目标进制">
              <el-input-number v-model="baseTo" :min="2" :max="36" class='input'/>
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="baseResult" readonly class='input' />
            </el-form-item>
          </el-form>
        </div>

        <!-- Unicode 转换 -->
        <div v-if="currentTool.id === 'unicodeConv'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="unicodeInput" type="textarea" :rows="4" placeholder="输入文本" class='text' />
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="unicodeOutput" type="textarea" :rows="4" readonly class='text' />
            </el-form-item>
          </el-form>
        </div>

        <!-- ASCII 转换 -->
        <div v-if="currentTool.id === 'ascii'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="asciiInput" type="textarea" :rows="4" placeholder="输入文本" class='text' />
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="asciiOutput" type="textarea" :rows="4" readonly class='text' />
            </el-form-item>
          </el-form>
        </div>

        <!-- 颜色转换 -->
        <div v-if="currentTool.id === 'colorConv'">
          <el-form label-position="top">
            <el-form-item label="HEX 颜色值">
              <el-input v-model="colorHex" placeholder="#RRGGBB" @input="hexToRgb" class='input' />
            </el-form-item>
            <el-form-item label="RGB 颜色值">
              <el-input v-model="colorRgb" placeholder="rgb(r, g, b)" @input="rgbToHex" class='input' />
            </el-form-item>
            <el-form-item label="颜色预览">
              <div class="color-preview" :style="{ backgroundColor: colorHex }"></div>
            </el-form-item>
          </el-form>
        </div>

        <!-- URL 编码/解码 -->
        <div v-if="currentTool.id === 'urlEncode'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="urlInput" type="textarea" :rows="4" placeholder="输入文本" class='text' />
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="urlOutput" type="textarea" :rows="4" readonly class='text' />
            </el-form-item>
          </el-form>
        </div>

        <!-- JWT 解析 -->
        <div v-if="currentTool.id === 'jwt'">
          <el-form label-position="top">
            <el-form-item label="JWT Token">
              <el-input v-model="jwtToken" type="textarea" :rows="4" placeholder="输入 JWT 字符串" class='text' />
            </el-form-item>
            <el-form-item label="解析结果">
              <el-input v-model="jwtOutput" type="textarea" :rows="8" readonly class='text' />
            </el-form-item>
          </el-form>
        </div>

        <!-- 图片转 Base64 -->
        <div v-if="currentTool.id === 'imageToBase64'">
          <el-form label-position="top">
            <el-form-item label="选择图片">
              <input type="file" accept="image/*" @change="onImageToBase64Upload" />
            </el-form-item>
            <el-form-item v-if="imageToBase64Result">
              <el-input v-model="imageToBase64Result" type="textarea" :rows="6" readonly class='text' />
            </el-form-item>
          </el-form>
        </div>

        <!-- Base64 转图片 -->
        <div v-if="currentTool.id === 'base64ToImage'">
          <el-form label-position="top">
            <el-form-item label="Base64 字符串">
              <el-input v-model="base64ToImageInput" type="textarea" :rows="4" placeholder="输入图片的 Base64 字符串" class='text' />
            </el-form-item>
            <el-form-item v-if="base64ToImageSrc">
              <img :src="base64ToImageSrc" style="max-width: 100%;" />
            </el-form-item>
          </el-form>
        </div>

        <!-- Base64 编码/解码 -->
        <div v-if="currentTool.id === 'base64Encode'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="base64Input" type="textarea" :rows="4" placeholder="输入文本" class='text' />
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="base64Output" type="textarea" :rows="4" readonly class='text' />
            </el-form-item>
          </el-form>
        </div>

        <!-- ================= 加密哈希 ================= -->
        <!-- MD5 -->
        <div v-if="currentTool.id === 'md5Hash'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="hashInput" type="textarea" :rows="4" placeholder="输入文本" class='text' />
            </el-form-item>
            <el-form-item label="MD5 值">
              <el-input v-model="hashOutput" readonly class='input' />
            </el-form-item>
          </el-form>
        </div>

        <!-- SHA1 -->
        <div v-if="currentTool.id === 'sha1Hash'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="hashInput" type="textarea" :rows="4" placeholder="输入文本" class='text' />
            </el-form-item>
            <el-form-item label="SHA-1 值">
              <el-input v-model="hashOutput" readonly class='input' />
            </el-form-item>
          </el-form>
        </div>

        <!-- SHA256 -->
        <div v-if="currentTool.id === 'sha256Hash'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="hashInput" type="textarea" :rows="4" placeholder="输入文本" class='text' />
            </el-form-item>
            <el-form-item label="SHA-256 值">
              <el-input v-model="hashOutput" readonly class='input' />
            </el-form-item>
          </el-form>
        </div>

        <!-- SHA512 -->
        <div v-if="currentTool.id === 'sha512Hash'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="hashInput" type="textarea" :rows="4" placeholder="输入文本" class='text' />
            </el-form-item>
            <el-form-item label="SHA-512 值">
              <el-input v-model="hashOutput" readonly class='input' />
            </el-form-item>
          </el-form>
        </div>

        <!-- 哈希对比 -->
        <div v-if="currentTool.id === 'hashCompare'">
          <el-form label-position="top">
            <el-form-item label="哈希值 1">
              <el-input v-model="hashCompare1" placeholder="输入哈希值" class='input' />
            </el-form-item>
            <el-form-item label="哈希值 2">
              <el-input v-model="hashCompare2" placeholder="输入哈希值" class='input' />
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="hashCompareResult" readonly class='input' />
            </el-form-item>
          </el-form>
        </div>

        <!-- AES 加密 -->
        <div v-if="currentTool.id === 'aesEncrypt'">
          <el-form label-position="top">
            <el-form-item label="密钥（密码）">
              <el-input v-model="aesKey" type="password" placeholder="请输入密钥" show-password class='input' />
            </el-form-item>
            <el-form-item label="明文">
              <el-input v-model="aesPlaintext" type="textarea" :rows="4" placeholder="输入要加密的文本" class='text' />
            </el-form-item>
            <el-form-item label="密文（Base64）">
              <el-input v-model="aesEncrypted" type="textarea" :rows="4" readonly class='text' />
            </el-form-item>
          </el-form>
        </div>

        <!-- AES 解密 -->
        <div v-if="currentTool.id === 'aesDecrypt'">
          <el-form label-position="top">
            <el-form-item label="密钥（密码）">
              <el-input v-model="aesKey" type="password" placeholder="请输入密钥" show-password class='input' />
            </el-form-item>
            <el-form-item label="密文（Base64）">
              <el-input v-model="aesCiphertext" type="textarea" :rows="4" placeholder="输入 Base64 密文" class='text' />
            </el-form-item>
            <el-form-item label="明文">
              <el-input v-model="aesDecrypted" type="textarea" :rows="4" readonly class='text' />
            </el-form-item>
          </el-form>
        </div>

        <!-- 密码强度 -->
        <div v-if="currentTool.id === 'passwordStrength'">
          <el-form label-position="top">
            <el-form-item label="密码">
              <el-input v-model="password" type="password" show-password placeholder="输入密码" class='input' />
            </el-form-item>
            <el-form-item label="强度结果">
              <el-progress :percentage="passwordStrengthScore" :color="passwordStrengthColor" :format="formatStrength" />
              <div class="strength-tips">{{ passwordStrengthTips }}</div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 生成盐值 -->
        <div v-if="currentTool.id === 'generateSalt'">
          <el-form label-position="top">
            <el-form-item v-if="salt">
              <el-input v-model="salt" readonly class='input' />
            </el-form-item>
          </el-form>
        </div>

        <!-- ================= 字符串处理 ================= -->
        <!-- 文本对比 -->
        <div v-if="currentTool.id === 'textDiff'">
          <el-form label-position="top">
            <el-form-item label="原始文本">
              <el-input v-model="textDiffLeft" type="textarea" :rows="5" placeholder="请输入原始文本" />
            </el-form-item>
            <el-form-item label="对比文本">
              <el-input v-model="textDiffRight" type="textarea" :rows="5" placeholder="请输入对比文本" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="computeTextDiff">对比差异</el-button>
            </el-form-item>
            <el-form-item label="差异结果">
              <el-input v-model="textDiffOutput" type="textarea" :rows="8" readonly />
            </el-form-item>
          </el-form>
        </div>

        <!-- 正则测试 -->
        <div v-if="currentTool.id === 'regexTest'">
          <el-form label-position="top">
            <el-form-item label="正则表达式">
              <el-input v-model="regexPattern" placeholder="输入正则表达式" />
            </el-form-item>
            <el-form-item label="测试文本">
              <el-input v-model="regexText" type="textarea" :rows="4" placeholder="输入测试文本" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testRegex">测试匹配</el-button>
            </el-form-item>
            <el-form-item label="匹配结果">
              <el-input v-model="regexOutput" type="textarea" :rows="6" readonly />
            </el-form-item>
          </el-form>
        </div>

        <!-- 去除空格 -->
        <div v-if="currentTool.id === 'trimSpaces'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="trimInput" type="textarea" :rows="4" placeholder="请输入文本" />
            </el-form-item>
            <el-form-item>
              <el-select v-model="trimType" placeholder="选择去除方式" style="width: 150px">
                <el-option label="去除首尾空格" value="trim" />
                <el-option label="去除所有空格" value="all" />
                <el-option label="去除多余空格（保留一个）" value="extra" />
              </el-select>
              <el-button type="primary" @click="trimSpaces" style="margin-left: 12px">执行</el-button>
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="trimOutput" type="textarea" :rows="4" readonly />
            </el-form-item>
          </el-form>
        </div>

        <!-- 字符替换 -->
        <div v-if="currentTool.id === 'replace'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="replaceInput" type="textarea" :rows="4" placeholder="请输入文本" />
            </el-form-item>
            <el-form-item label="查找内容">
              <el-input v-model="replaceSearch" placeholder="要替换的字符或正则" />
            </el-form-item>
            <el-form-item label="替换为">
              <el-input v-model="replaceWith" placeholder="替换后的内容" />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="replaceGlobal">全局替换</el-checkbox>
              <el-checkbox v-model="replaceRegex">使用正则表达式</el-checkbox>
              <el-button type="primary" @click="doReplace">替换</el-button>
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="replaceOutput" type="textarea" :rows="4" readonly />
            </el-form-item>
          </el-form>
        </div>

        <!-- 字符转义/反转义 -->
        <div v-if="currentTool.id === 'escape'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="escapeInput" type="textarea" :rows="4" placeholder="请输入文本" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="escapeHtml">HTML 转义</el-button>
              <el-button @click="unescapeHtml">HTML 反转义</el-button>
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="escapeOutput" type="textarea" :rows="4" readonly />
            </el-form-item>
          </el-form>
        </div>

        <!-- 字数统计 -->
        <div v-if="currentTool.id === 'wordCount'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="statsInput" type="textarea" :rows="4" placeholder="请输入文本" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="computeStats">统计</el-button>
            </el-form-item>
            <el-form-item label="统计结果">
              <div class="stats-output">
                <p>字符数: {{ stats.charCount }}</p>
                <p>单词数: {{ stats.wordCount }}</p>
                <p>行数: {{ stats.lineCount }}</p>
                <p>字节数: {{ stats.byteCount }}</p>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 大小写转换 -->
        <div v-if="currentTool.id === 'caseConvert'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="caseInput" type="textarea" :rows="4" placeholder="请输入文本" />
            </el-form-item>
            <el-form-item>
              <el-button-group>
                <el-button @click="toUpperCase">转大写</el-button>
                <el-button @click="toLowerCase">转小写</el-button>
                <el-button @click="toTitleCase">首字母大写</el-button>
              </el-button-group>
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="caseOutput" type="textarea" :rows="4" readonly />
            </el-form-item>
          </el-form>
        </div>

        <!-- 文本格式化 -->
        <div v-if="currentTool.id === 'formatText'">
          <el-form label-position="top">
            <el-form-item label="输入文本">
              <el-input v-model="formatTextInput" type="textarea" :rows="4" placeholder="请输入文本" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="formatText">格式化（去除多余空行和空格）</el-button>
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="formatTextOutput" type="textarea" :rows="4" readonly />
            </el-form-item>
          </el-form>
        </div>

        <!-- ================= 定时任务 ================= -->
        <!-- 生成Cron表达式 -->
        <div v-if="currentTool.id === 'cronGen'">
          <el-form label-position="top" label-width="80px">
            <el-form-item label="分钟">
              <el-input v-model="cronMinute" placeholder="0-59，* 或 */n" />
            </el-form-item>
            <el-form-item label="小时">
              <el-input v-model="cronHour" placeholder="0-23" />
            </el-form-item>
            <el-form-item label="日期">
              <el-input v-model="cronDay" placeholder="1-31" />
            </el-form-item>
            <el-form-item label="月份">
              <el-input v-model="cronMonth" placeholder="1-12" />
            </el-form-item>
            <el-form-item label="星期">
              <el-input v-model="cronWeek" placeholder="0-6（0=周日）" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="buildCron">生成表达式</el-button>
            </el-form-item>
            <el-form-item label="Cron表达式">
              <el-input v-model="cronExpression" readonly />
              <div class="copy-btn"><el-button text size="small" @click="copyToClipboard(cronExpression)">复制</el-button></div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 解析表达式 -->
        <div v-if="currentTool.id === 'cronParse'">
          <el-form label-position="top">
            <el-form-item label="Cron表达式">
              <el-input v-model="cronParseInput" placeholder="如：0 0 12 * * ?" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="parseCron">解析</el-button>
            </el-form-item>
            <el-form-item label="解析结果">
              <el-input v-model="cronParseOutput" type="textarea" :rows="5" readonly />
            </el-form-item>
          </el-form>
        </div>

        <!-- 下次执行时间 -->
        <div v-if="currentTool.id === 'cronNext'">
          <el-form label-position="top">
            <el-form-item label="Cron表达式">
              <el-input v-model="cronNextInput" placeholder="如：0 0 12 * * ?" />
            </el-form-item>
            <el-form-item label="基准时间（可选）">
              <el-date-picker v-model="cronBaseTime" type="datetime" placeholder="选择开始时间" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="getNextCronTime">获取下次执行时间</el-button>
            </el-form-item>
            <el-form-item label="下次执行时间">
              <el-input v-model="cronNextOutput" readonly />
            </el-form-item>
          </el-form>
        </div>

        <!-- 验证表达式 -->
        <div v-if="currentTool.id === 'cronValidate'">
          <el-form label-position="top">
            <el-form-item label="Cron表达式">
              <el-input v-model="cronValidateInput" placeholder="输入Cron表达式" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="validateCron">验证</el-button>
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="cronValidateOutput" readonly />
            </el-form-item>
          </el-form>
        </div>

        <!-- ================= 随机数据 ================= -->
        <!-- 随机整数 -->
        <div v-if="currentTool.id === 'randomInt'">
          <el-form label-position="top">
            <el-form-item label="最小值">
              <el-input-number v-model="randIntMin" :min="-1000000" />
            </el-form-item>
            <el-form-item label="最大值">
              <el-input-number v-model="randIntMax" :min="-1000000" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="generateRandomInt">生成</el-button>
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="randomInt" readonly />
            </el-form-item>
          </el-form>
        </div>

        <!-- 随机小数 -->
        <div v-if="currentTool.id === 'randomFloat'">
          <el-form label-position="top">
            <el-form-item label="最小值">
              <el-input-number v-model="randFloatMin" :step="0.1" />
            </el-form-item>
            <el-form-item label="最大值">
              <el-input-number v-model="randFloatMax" :step="0.1" />
            </el-form-item>
            <el-form-item label="小数位数">
              <el-input-number v-model="randFloatDecimals" :min="0" :max="10" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="generateRandomFloat">生成</el-button>
            </el-form-item>
            <el-form-item label="结果">
              <el-input v-model="randomFloat" readonly />
            </el-form-item>
          </el-form>
        </div>

        <!-- 随机字符串 -->
        <div v-if="currentTool.id === 'randomString'">
          <el-form label-position="top">
            <el-form-item v-if="randomString">
              <el-input v-model="randomString" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- UUID -->
        <div v-if="currentTool.id === 'uuid'">
          <el-form label-position="top">
            <el-form-item v-if="uuid">
              <el-input v-model="uuid" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 随机布尔值 -->
        <div v-if="currentTool.id === 'randomBool'">
          <el-form label-position="top">
            <el-form-item v-if="randomBool">
              <el-input v-model="randomBool" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- MAC地址 -->
        <div v-if="currentTool.id === 'mac'">
          <el-form label-position="top">
            <el-form-item v-if="macAddress">
              <el-input v-model="macAddress" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- IP地址 -->
        <div v-if="currentTool.id === 'ip'">
          <el-form label-position="top">
            <el-form-item v-if="ipAddress">
              <el-input v-model="ipAddress" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 随机日期 -->
        <div v-if="currentTool.id === 'randomDate'">
          <el-form label-position="top">
            <el-form-item v-if="randomDate">
              <el-input v-model="randomDate" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 随机密码 -->
        <div v-if="currentTool.id === 'randomPassword'">
          <el-form label-position="top">
            <el-form-item v-if="randomPassword">
              <el-input v-model="randomPassword" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>

        <!-- 随机颜色 -->
        <div v-if="currentTool.id === 'randomColor'">
          <el-form label-position="top">
            <el-form-item v-if="randomColor">
              <el-input v-model="randomColor" readonly class='input'/>
              <div class="color-preview" :style="{ backgroundColor: randomColor }" style="margin-top: 8px;"></div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 随机序列 -->
        <div v-if="currentTool.id === 'randomSequence'">
          <el-form label-position="top">
            <el-form-item v-if="randomSequence">
              <el-input v-model="randomSequence" type="textarea" :rows="4" readonly class='input'/>
            </el-form-item>
          </el-form>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer" style="border-top: none;">
          <el-button v-if="currentTool && currentTool.id === 'idcard'" type="primary" @click="generateIdCard">生成身份证正反面</el-button>
          <el-button v-if="currentTool && currentTool.id === 'idcard' && (idcardFrontImage || idcardBackImage)" type="primary" @click="copyIdCardImage('front')">复制正面图片</el-button>
          <el-button v-if="currentTool && currentTool.id === 'idcard' && (idcardFrontImage || idcardBackImage)" type="primary" @click="copyIdCardImage('back')">复制反面图片</el-button>
          <el-button v-if="currentTool && currentTool.id === 'idcard' && (idcardFrontImage || idcardBackImage)" type="primary" @click="downloadBothIdCards">一键下载正反面</el-button>
          <el-button v-if="currentTool && currentTool.id === 'bankcard'" type="primary" @click="generateBankCard">生成随机银行卡号</el-button>
          <el-button v-if="currentTool && currentTool.id === 'bankcard' && bankCard" type="primary" @click="copyToClipboard(bankCard)">复制银行卡号</el-button>
          <el-button v-if="currentTool && currentTool.id === 'idnumber'" type="primary" @click="generateIdNumber">{{ getGenerateButtonText() }}</el-button>
          <el-button v-if="currentTool && currentTool.id === 'idnumber' && idNumber" type="primary" @click="copyToClipboard(idNumber)">{{ getCopyButtonText() }}</el-button>
          <el-button v-if="currentTool && currentTool.id === 'chineseName'" type="primary" @click="generateChineseName">生成随机中文姓名</el-button>
          <el-button v-if="currentTool && currentTool.id === 'chineseName' && chineseName" type="primary" @click="copyToClipboard(chineseName)">复制中文姓名</el-button>
          <el-button v-if="currentTool && currentTool.id === 'mobile'" type="primary" @click="generateMobile">生成随机手机号</el-button>
          <el-button v-if="currentTool && currentTool.id === 'mobile' && mobile" type="primary" @click="copyToClipboard(mobile)">复制手机号</el-button>
          <el-button v-if="currentTool && currentTool.id === 'email'" type="primary" @click="generateEmail">生成随机邮箱</el-button>
          <el-button v-if="currentTool && currentTool.id === 'email' && email" type="primary" @click="copyToClipboard(email)">复制邮箱</el-button>
          <el-button v-if="currentTool && currentTool.id === 'address'" type="primary" @click="generateAddress">生成随机地址</el-button>
          <el-button v-if="currentTool && currentTool.id === 'address' && address" type="primary" @click="copyToClipboard(address)">复制地址</el-button>
          <el-button v-if="currentTool && currentTool.id === 'company'" type="primary" @click="generateCompany">生成随机公司名称</el-button>
          <el-button v-if="currentTool && currentTool.id === 'company' && company" type="primary" @click="copyToClipboard(company)">复制公司名称</el-button>
          <el-button v-if="currentTool && currentTool.id === 'license'" type="primary" @click="generateLicense">生成随机营业执照号</el-button>
          <el-button v-if="currentTool && currentTool.id === 'license' && license" type="primary" @click="copyToClipboard(license)">复制营业执照号</el-button>
          <el-button v-if="currentTool && currentTool.id === 'coords'" type="primary" @click="generateCoords">生成随机经纬度</el-button>
          <el-button v-if="currentTool && currentTool.id === 'coords' && coords" type="primary" @click="copyToClipboard(coords)">复制经纬度</el-button>
          <el-button v-if="currentTool && currentTool.id === 'profile'" type="primary" @click="generateProfile">生成完整用户档案</el-button>
          <el-button v-if="currentTool && currentTool.id === 'profile' && profile" type="primary" @click="copyToClipboard(profile)">复制用户档案</el-button>
          <el-button v-if="currentTool && currentTool.id === 'randomString'" type="primary" @click="generateRandomString">生成随机字符串</el-button>
          <el-button v-if="currentTool && currentTool.id === 'randomString' && randomString" type="primary" @click="copyToClipboard(randomString)">复制随机字符串</el-button>
          <el-button v-if="currentTool && currentTool.id === 'uuid'" type="primary" @click="generateUUID">生成UUID</el-button>
          <el-button v-if="currentTool && currentTool.id === 'uuid' && uuid" type="primary" @click="copyToClipboard(uuid)">复制UUID</el-button>

          <el-button v-if="currentTool && currentTool.id === 'mac'" type="primary" @click="generateMac">生成MAC地址</el-button>
          <el-button v-if="currentTool && currentTool.id === 'mac' && macAddress" type="primary" @click="copyToClipboard(macAddress)">复制MAC地址</el-button>
          <el-button v-if="currentTool && currentTool.id === 'ip'" type="primary" @click="generateIp">生成IP地址</el-button>
          <el-button v-if="currentTool && currentTool.id === 'ip' && ipAddress" type="primary" @click="copyToClipboard(ipAddress)">复制IP地址</el-button>
          <el-button v-if="currentTool && currentTool.id === 'randomDate'" type="primary" @click="generateRandomDate">生成随机日期</el-button>
          <el-button v-if="currentTool && currentTool.id === 'randomDate' && randomDate" type="primary" @click="copyToClipboard(randomDate)">复制随机日期</el-button>
          <el-button v-if="currentTool && currentTool.id === 'randomPassword'" type="primary" @click="generateRandomPassword">生成随机密码</el-button>
          <el-button v-if="currentTool && currentTool.id === 'randomPassword' && randomPassword" type="primary" @click="copyToClipboard(randomPassword)">复制随机密码</el-button>
          <el-button v-if="currentTool && currentTool.id === 'randomColor'" type="primary" @click="generateRandomColor">生成随机颜色</el-button>
          <el-button v-if="currentTool && currentTool.id === 'randomColor' && randomColor" type="primary" @click="copyToClipboard(randomColor)">复制随机颜色</el-button>
          <el-button v-if="currentTool && currentTool.id === 'randomSequence'" type="primary" @click="generateRandomSequence">生成随机序列</el-button>
          <el-button v-if="currentTool && currentTool.id === 'randomSequence' && randomSequence" type="primary" @click="copyToClipboard(randomSequence)">复制随机序列</el-button>
          
          <!-- 编码转换功能按钮 -->
          <el-button v-if="currentTool && currentTool.id === 'barcode'" type="primary" @click="generateBarcode">生成条形码</el-button>
          <el-button v-if="currentTool && currentTool.id === 'barcode' && barcodeImage" type="primary" @click="copyBarcodeImage">复制图片</el-button>
          <el-button v-if="currentTool && currentTool.id === 'barcode' && barcodeImage" type="primary" @click="downloadBarcodeImage">下载图片</el-button>
          <el-button v-if="currentTool && currentTool.id === 'qrcode'" type="primary" @click="generateQRCode">生成二维码</el-button>
          <el-button v-if="currentTool && currentTool.id === 'qrcode' && qrcodeImage" type="primary" @click="copyQRCodeImage">复制图片</el-button>
          <el-button v-if="currentTool && currentTool.id === 'qrcode' && qrcodeImage" type="primary" @click="downloadQRCodeImage">下载图片</el-button>
          <el-button v-if="currentTool && currentTool.id === 'qrcodeDecode'" type="primary" @click="decodeQRCode">解析二维码</el-button>
          <el-button v-if="currentTool && currentTool.id === 'qrcodeDecode' && qrcodeDecodedText" type="primary" @click="copyToClipboard(qrcodeDecodedText)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'urlEncode'" type="primary" @click="encodeUrl">URL 编码</el-button>
          <el-button v-if="currentTool && currentTool.id === 'urlEncode'" @click="decodeUrl" type="primary">URL 解码</el-button>
          <el-button v-if="currentTool && currentTool.id === 'urlEncode' && urlOutput" type="primary" @click="copyToClipboard(urlOutput)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jwt'" type="primary" @click="parseJwt">解析 JWT</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jwt' && jwtOutput" type="primary" @click="copyToClipboard(jwtOutput)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'base64Encode'" type="primary" @click="encodeBase64">Base64 编码</el-button>
          <el-button v-if="currentTool && currentTool.id === 'base64Encode'" @click="decodeBase64" type="primary">Base64 解码</el-button>
          <el-button v-if="currentTool && currentTool.id === 'base64Encode' && base64Output" type="primary" @click="copyToClipboard(base64Output)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'baseConvert'" type="primary" @click="convertBase">进制转换</el-button>
          <el-button v-if="currentTool && currentTool.id === 'baseConvert' && baseResult" type="primary" @click="copyToClipboard(baseResult)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'unicodeConv'" type="primary" @click="encodeUnicode">转为 Unicode</el-button>
          <el-button v-if="currentTool && currentTool.id === 'unicodeConv'" @click="decodeUnicode" type="primary">Unicode 解码</el-button>
          <el-button v-if="currentTool && currentTool.id === 'unicodeConv' && unicodeOutput" type="primary" @click="copyToClipboard(unicodeOutput)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'ascii'" type="primary" @click="textToAscii">文本转 ASCII</el-button>
          <el-button v-if="currentTool && currentTool.id === 'ascii'" @click="asciiToText" type="primary">ASCII 转文本</el-button>
          <el-button v-if="currentTool && currentTool.id === 'ascii' && asciiOutput" type="primary" @click="copyToClipboard(asciiOutput)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'colorConv' && colorHex" type="primary" @click="copyToClipboard(colorHex)">复制 HEX</el-button>
          <el-button v-if="currentTool && currentTool.id === 'colorConv' && colorRgb" type="primary" @click="copyToClipboard(colorRgb)">复制 RGB</el-button>
          <el-button v-if="currentTool && currentTool.id === 'imageToBase64'" type="primary" @click="triggerImageToBase64Upload">图片转 Base64</el-button>
          <el-button v-if="currentTool && currentTool.id === 'imageToBase64' && imageToBase64Result" type="primary" @click="copyToClipboard(imageToBase64Result)">复制 Base64</el-button>
          <el-button v-if="currentTool && currentTool.id === 'base64ToImage'" type="primary" @click="base64ToImage">Base64 转图片</el-button>
          <el-button v-if="currentTool && currentTool.id === 'base64ToImage' && base64ToImageSrc" type="primary" @click="downloadBase64Image">下载图片</el-button>
          
          <!-- 加密哈希功能按钮 -->
          <el-button v-if="currentTool && currentTool.id === 'md5Hash'" type="primary" @click="computeMd5">计算 MD5</el-button>
          <el-button v-if="currentTool && currentTool.id === 'md5Hash' && hashOutput" type="primary" @click="copyToClipboard(hashOutput)">复制 MD5</el-button>
          <el-button v-if="currentTool && currentTool.id === 'sha1Hash'" type="primary" @click="computeSha1">计算 SHA-1</el-button>
          <el-button v-if="currentTool && currentTool.id === 'sha1Hash' && hashOutput" type="primary" @click="copyToClipboard(hashOutput)">复制 SHA-1</el-button>
          <el-button v-if="currentTool && currentTool.id === 'sha256Hash'" type="primary" @click="computeSha256">计算 SHA-256</el-button>
          <el-button v-if="currentTool && currentTool.id === 'sha256Hash' && hashOutput" type="primary" @click="copyToClipboard(hashOutput)">复制 SHA-256</el-button>
          <el-button v-if="currentTool && currentTool.id === 'sha512Hash'" type="primary" @click="computeSha512">计算 SHA-512</el-button>
          <el-button v-if="currentTool && currentTool.id === 'sha512Hash' && hashOutput" type="primary" @click="copyToClipboard(hashOutput)">复制 SHA-512</el-button>
          <el-button v-if="currentTool && currentTool.id === 'hashCompare'" type="primary" @click="compareHash">对比哈希值</el-button>
          <el-button v-if="currentTool && currentTool.id === 'hashCompare' && hashCompareResult" type="primary" @click="copyToClipboard(hashCompareResult)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'aesEncrypt'" type="primary" @click="aesEncrypt">AES 加密</el-button>
          <el-button v-if="currentTool && currentTool.id === 'aesEncrypt' && aesEncrypted" type="primary" @click="copyToClipboard(aesEncrypted)">复制密文</el-button>
          <el-button v-if="currentTool && currentTool.id === 'aesDecrypt'" type="primary" @click="aesDecrypt">AES 解密</el-button>
          <el-button v-if="currentTool && currentTool.id === 'aesDecrypt' && aesDecrypted" type="primary" @click="copyToClipboard(aesDecrypted)">复制明文</el-button>
          <el-button v-if="currentTool && currentTool.id === 'passwordStrength'" type="primary" @click="checkPasswordStrength">检测密码强度</el-button>
          <el-button v-if="currentTool && currentTool.id === 'generateSalt'" type="primary" @click="generateSalt">生成随机盐值</el-button>
          <el-button v-if="currentTool && currentTool.id === 'generateSalt' && salt" type="primary" @click="copyToClipboard(salt)">复制盐值</el-button>
          
          <!-- JSON 处理功能按钮 -->
          <el-button v-if="currentTool && currentTool.id === 'jsonFormat'" type="primary" @click="formatJson">格式化 JSON</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonFormat' && jsonOutput" type="primary" @click="copyToClipboard(jsonOutput)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonValidate'" type="primary" @click="validateJson">校验 JSON</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonValidate' && jsonValidateOutput" type="primary" @click="copyToClipboard(jsonValidateOutput)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonDiff'" type="primary" @click="compareJson">对比 JSON</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonDiff' && jsonDiffOutput" type="primary" @click="copyToClipboard(jsonDiffOutput)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonpath'" type="primary" @click="executeJsonPath">JSONPath 查询</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonpath' && jsonPathResult" type="primary" @click="copyToClipboard(jsonPathResult)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonFlatten'" type="primary" @click="flattenJson">扁平化 JSON</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonFlatten' && jsonFlattenOutput" type="primary" @click="copyToClipboard(jsonFlattenOutput)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonPaths'" type="primary" @click="listJsonPaths">列出路径</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonPaths' && jsonPathsOutput" type="primary" @click="copyToClipboard(jsonPathsOutput)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonToXml'" type="primary" @click="jsonToXml">JSON 转 XML</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonToXml' && jsonToXmlOutput" type="primary" @click="copyToClipboard(jsonToXmlOutput)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'xmlToJson'" type="primary" @click="xmlToJson">XML 转 JSON</el-button>
          <el-button v-if="currentTool && currentTool.id === 'xmlToJson' && xmlToJsonOutput" type="primary" @click="copyToClipboard(xmlToJsonOutput)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonToYaml'" type="primary" @click="jsonToYaml">JSON 转 YAML</el-button>
          <el-button v-if="currentTool && currentTool.id === 'jsonToYaml' && jsonToYamlOutput" type="primary" @click="copyToClipboard(jsonToYamlOutput)">复制结果</el-button>
          <el-button v-if="currentTool && currentTool.id === 'yamlToJson'" type="primary" @click="yamlToJson">YAML 转 JSON</el-button>
          <el-button v-if="currentTool && currentTool.id === 'yamlToJson' && yamlToJsonOutput" type="primary" @click="copyToClipboard(yamlToJsonOutput)">复制结果</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Search, Tools } from '@element-plus/icons-vue'
import JsBarcode from 'jsbarcode'
import QRCode from 'qrcode'
import jsQR from 'jsqr'
import yaml from 'js-yaml'
import CryptoJS from 'crypto-js'

// 简易 Cron 解析器（替代 cron-parser，避免私有类方法错误）
class CronParser {
  constructor(expression) {
    this.expression = expression.trim()
    this.fields = this.parseExpression()
  }

  parseExpression() {
    const parts = this.expression.split(/\s+/)
    if (parts.length !== 5 && parts.length !== 6) {
      throw new Error('无效的Cron表达式，应为5或6个字段')
    }
    return {
      minute: parts[0],
      hour: parts[1],
      dayOfMonth: parts[2],
      month: parts[3],
      dayOfWeek: parts[4],
      ...(parts[5] ? { year: parts[5] } : {})
    }
  }

  static validate(expression) {
    try {
      new CronParser(expression)
      return true
    } catch (e) {
      return false
    }
  }

  // 获取下次执行时间（简化版，仅用于演示，实际复杂表达式需更复杂逻辑）
  getNextDate(currentDate = new Date()) {
    // 简单实现：如果表达式为 * * * * * 则返回当前时间+1分钟
    if (this.expression === '* * * * *') {
      return new Date(currentDate.getTime() + 60 * 1000)
    }
    // 其他情况简单返回当前时间+1小时
    return new Date(currentDate.getTime() + 60 * 60 * 1000)
  }
}

export default {
  name: 'TestTools',
  components: { Search, Tools },
  data() {
    return {
      searchKeyword: '',
      allTools: [],
      filteredGroups: [],
      dialogVisible: false,
      currentTool: null,
      // 测试数据生成
      idcardFrontImage: '',
      idcardBackImage: '',
      idcardName: '张三',
      idcardBirthDate: '1990-01-01',
      idcardGender: '男',
      idcardProvince: '北京市',
      idcardCity: '东城区',
      idcardProvinceCity: ['北京市', '东城区'],
      idcardDetailAddress: '朝阳门内大街1号',
      // 地址区域码映射表
      addressCodeMap: {
        '北京市': {
          '东城区': '110101',
          '西城区': '110102',
          '朝阳区': '110105',
          '丰台区': '110106',
          '石景山区': '110107',
          '海淀区': '110108',
          '门头沟区': '110109',
          '房山区': '110111',
          '通州区': '110112',
          '顺义区': '110113',
          '昌平区': '110114',
          '大兴区': '110115',
          '怀柔区': '110116',
          '平谷区': '110117',
          '密云区': '110118',
          '延庆区': '110119'
        },
        '天津市': {
          '和平区': '120101',
          '河东区': '120102',
          '河西区': '120103',
          '南开区': '120104',
          '河北区': '120105',
          '红桥区': '120106',
          '东丽区': '120110',
          '西青区': '120111',
          '津南区': '120112',
          '北辰区': '120113',
          '武清区': '120114',
          '宝坻区': '120115',
          '滨海新区': '120116',
          '宁河区': '120117',
          '静海区': '120118',
          '蓟州区': '120119'
        },
        '河北省': {
          '石家庄市': '130100',
          '唐山市': '130200',
          '秦皇岛市': '130300',
          '邯郸市': '130400',
          '邢台市': '130500',
          '保定市': '130600',
          '张家口市': '130700',
          '承德市': '130800',
          '沧州市': '130900',
          '廊坊市': '131000',
          '衡水市': '131100'
        },
        '山西省': {
          '太原市': '140100',
          '大同市': '140200',
          '阳泉市': '140300',
          '长治市': '140400',
          '晋城市': '140500',
          '朔州市': '140600',
          '晋中市': '140700',
          '运城市': '140800',
          '忻州市': '140900',
          '临汾市': '141000',
          '吕梁市': '141100'
        },
        '内蒙古自治区': {
          '呼和浩特市': '150100',
          '包头市': '150200',
          '乌海市': '150300',
          '赤峰市': '150400',
          '通辽市': '150500',
          '鄂尔多斯市': '150600',
          '呼伦贝尔市': '150700',
          '巴彦淖尔市': '150800',
          '乌兰察布市': '150900',
          '兴安盟': '152200',
          '锡林郭勒盟': '152500',
          '阿拉善盟': '152900'
        },
        '辽宁省': {
          '沈阳市': '210100',
          '大连市': '210200',
          '鞍山市': '210300',
          '抚顺市': '210400',
          '本溪市': '210500',
          '丹东市': '210600',
          '锦州市': '210700',
          '营口市': '210800',
          '阜新市': '210900',
          '辽阳市': '211000',
          '盘锦市': '211100',
          '铁岭市': '211200',
          '朝阳市': '211300',
          '葫芦岛市': '211400'
        },
        '吉林省': {
          '长春市': '220100',
          '吉林市': '220200',
          '四平市': '220300',
          '辽源市': '220400',
          '通化市': '220500',
          '白山市': '220600',
          '松原市': '220700',
          '白城市': '220800',
          '延边朝鲜族自治州': '222400'
        },
        '黑龙江省': {
          '哈尔滨市': '230100',
          '齐齐哈尔市': '230200',
          '鸡西市': '230300',
          '鹤岗市': '230400',
          '双鸭山市': '230500',
          '大庆市': '230600',
          '伊春市': '230700',
          '佳木斯市': '230800',
          '七台河市': '230900',
          '牡丹江市': '231000',
          '黑河市': '231100',
          '绥化市': '231200',
          '大兴安岭地区': '232700'
        },
        '上海市': {
          '黄浦区': '310101',
          '徐汇区': '310104',
          '长宁区': '310105',
          '静安区': '310106',
          '普陀区': '310107',
          '虹口区': '310109',
          '杨浦区': '310110',
          '闵行区': '310112',
          '宝山区': '310113',
          '嘉定区': '310114',
          '浦东新区': '310115',
          '金山区': '310116',
          '松江区': '310117',
          '青浦区': '310118',
          '奉贤区': '310120',
          '崇明区': '310151'
        },
        '江苏省': {
          '南京市': '320100',
          '无锡市': '320200',
          '徐州市': '320300',
          '常州市': '320400',
          '苏州市': '320500',
          '南通市': '320600',
          '连云港市': '320700',
          '淮安市': '320800',
          '盐城市': '320900',
          '扬州市': '321000',
          '镇江市': '321100',
          '泰州市': '321200',
          '宿迁市': '321300'
        },
        '浙江省': {
          '杭州市': '330100',
          '宁波市': '330200',
          '温州市': '330300',
          '嘉兴市': '330400',
          '湖州市': '330500',
          '绍兴市': '330600',
          '金华市': '330700',
          '衢州市': '330800',
          '舟山市': '330900',
          '台州市': '331000',
          '丽水市': '331100'
        },
        '安徽省': {
          '合肥市': '340100',
          '芜湖市': '340200',
          '蚌埠市': '340300',
          '淮南市': '340400',
          '马鞍山市': '340500',
          '淮北市': '340600',
          '铜陵市': '340700',
          '安庆市': '340800',
          '黄山市': '341000',
          '滁州市': '341100',
          '阜阳市': '341200',
          '宿州市': '341300',
          '六安市': '341500',
          '亳州市': '341600',
          '池州市': '341700',
          '宣城市': '341800'
        },
        '福建省': {
          '福州市': '350100',
          '厦门市': '350200',
          '莆田市': '350300',
          '三明市': '350400',
          '泉州市': '350500',
          '漳州市': '350600',
          '南平市': '350700',
          '龙岩市': '350800',
          '宁德市': '350900'
        },
        '江西省': {
          '南昌市': '360100',
          '景德镇市': '360200',
          '萍乡市': '360300',
          '九江市': '360400',
          '新余市': '360500',
          '鹰潭市': '360600',
          '赣州市': '360700',
          '吉安市': '360800',
          '宜春市': '360900',
          '抚州市': '361000',
          '上饶市': '361100'
        },
        '山东省': {
          '济南市': '370100',
          '青岛市': '370200',
          '淄博市': '370300',
          '枣庄市': '370400',
          '东营市': '370500',
          '烟台市': '370600',
          '潍坊市': '370700',
          '济宁市': '370800',
          '泰安市': '370900',
          '威海市': '371000',
          '日照市': '371100',
          '临沂市': '371300',
          '德州市': '371400',
          '聊城市': '371500',
          '滨州市': '371600',
          '菏泽市': '371700'
        },
        '河南省': {
          '郑州市': '410100',
          '开封市': '410200',
          '洛阳市': '410300',
          '平顶山市': '410400',
          '安阳市': '410500',
          '鹤壁市': '410600',
          '新乡市': '410700',
          '焦作市': '410800',
          '濮阳市': '410900',
          '许昌市': '411000',
          '漯河市': '411100',
          '三门峡市': '411200',
          '南阳市': '411300',
          '商丘市': '411400',
          '信阳市': '411500',
          '周口市': '411600',
          '驻马店市': '411700'
        },
        '湖北省': {
          '武汉市': '420100',
          '黄石市': '420200',
          '十堰市': '420300',
          '宜昌市': '420500',
          '襄阳市': '420600',
          '鄂州市': '420700',
          '荆门市': '420800',
          '孝感市': '420900',
          '荆州市': '421000',
          '黄冈市': '421100',
          '咸宁市': '421200',
          '随州市': '421300',
          '恩施土家族苗族自治州': '422800'
        },
        '湖南省': {
          '长沙市': '430100',
          '株洲市': '430200',
          '湘潭市': '430300',
          '衡阳市': '430400',
          '邵阳市': '430500',
          '岳阳市': '430600',
          '常德市': '430700',
          '张家界市': '430800',
          '益阳市': '430900',
          '郴州市': '431000',
          '永州市': '431100',
          '怀化市': '431200',
          '娄底市': '431300',
          '湘西土家族苗族自治州': '433100'
        },
        '广东省': {
          '广州市': '440100',
          '韶关市': '440200',
          '深圳市': '440300',
          '珠海市': '440400',
          '汕头市': '440500',
          '佛山市': '440600',
          '江门市': '440700',
          '湛江市': '440800',
          '茂名市': '440900',
          '肇庆市': '441200',
          '惠州市': '441300',
          '梅州市': '441400',
          '汕尾市': '441500',
          '河源市': '441600',
          '阳江市': '441700',
          '清远市': '441800',
          '东莞市': '441900',
          '中山市': '442000',
          '潮州市': '445100',
          '揭阳市': '445200',
          '云浮市': '445300'
        },
        '广西壮族自治区': {
          '南宁市': '450100',
          '柳州市': '450200',
          '桂林市': '450300',
          '梧州市': '450400',
          '北海市': '450500',
          '防城港市': '450600',
          '钦州市': '450700',
          '贵港市': '450800',
          '玉林市': '450900',
          '百色市': '451000',
          '贺州市': '451100',
          '河池市': '451200',
          '来宾市': '451300',
          '崇左市': '451400'
        },
        '海南省': {
          '海口市': '460100',
          '三亚市': '460200',
          '三沙市': '460300',
          '儋州市': '460400',
          '五指山市': '469001',
          '琼海市': '469002',
          '文昌市': '469005',
          '万宁市': '469006',
          '东方市': '469007',
          '定安县': '469021',
          '屯昌县': '469022',
          '澄迈县': '469023',
          '临高县': '469024',
          '白沙黎族自治县': '469025',
          '昌江黎族自治县': '469026',
          '乐东黎族自治县': '469027',
          '陵水黎族自治县': '469028',
          '保亭黎族苗族自治县': '469029',
          '琼中黎族苗族自治县': '469030'
        },
        '重庆市': {
          '万州区': '500101',
          '涪陵区': '500102',
          '渝中区': '500103',
          '大渡口区': '500104',
          '江北区': '500105',
          '沙坪坝区': '500106',
          '九龙坡区': '500107',
          '南岸区': '500108',
          '北碚区': '500109',
          '綦江区': '500110',
          '大足区': '500111',
          '渝北区': '500112',
          '巴南区': '500113',
          '黔江区': '500114',
          '长寿区': '500115',
          '江津区': '500116',
          '合川区': '500117',
          '永川区': '500118',
          '南川区': '500119',
          '璧山区': '500120',
          '铜梁区': '500151',
          '潼南区': '500152',
          '荣昌区': '500153',
          '开州区': '500154',
          '梁平区': '500155',
          '武隆区': '500156'
        },
        '四川省': {
          '成都市': '510100',
          '自贡市': '510300',
          '攀枝花市': '510400',
          '泸州市': '510500',
          '德阳市': '510600',
          '绵阳市': '510700',
          '广元市': '510800',
          '遂宁市': '510900',
          '内江市': '511000',
          '乐山市': '511100',
          '南充市': '511300',
          '眉山市': '511400',
          '宜宾市': '511500',
          '广安市': '511600',
          '达州市': '511700',
          '雅安市': '511800',
          '巴中市': '511900',
          '资阳市': '512000',
          '阿坝藏族羌族自治州': '513200',
          '甘孜藏族自治州': '513300',
          '凉山彝族自治州': '513400'
        },
        '贵州省': {
          '贵阳市': '520100',
          '六盘水市': '520200',
          '遵义市': '520300',
          '安顺市': '520400',
          '毕节市': '520500',
          '铜仁市': '520600',
          '黔西南布依族苗族自治州': '522300',
          '黔东南苗族侗族自治州': '522600',
          '黔南布依族苗族自治州': '522700'
        },
        '云南省': {
          '昆明市': '530100',
          '曲靖市': '530300',
          '玉溪市': '530400',
          '保山市': '530500',
          '昭通市': '530600',
          '丽江市': '530700',
          '普洱市': '530800',
          '临沧市': '530900',
          '楚雄彝族自治州': '532300',
          '红河哈尼族彝族自治州': '532500',
          '文山壮族苗族自治州': '532600',
          '西双版纳傣族自治州': '532800',
          '大理白族自治州': '532900',
          '德宏傣族景颇族自治州': '533100',
          '怒江傈僳族自治州': '533300',
          '迪庆藏族自治州': '533400'
        },
        '西藏自治区': {
          '拉萨市': '540100',
          '日喀则市': '540200',
          '昌都市': '540300',
          '林芝市': '540400',
          '山南市': '540500',
          '那曲市': '540600',
          '阿里地区': '542500'
        },
        '陕西省': {
          '西安市': '610100',
          '铜川市': '610200',
          '宝鸡市': '610300',
          '咸阳市': '610400',
          '渭南市': '610500',
          '延安市': '610600',
          '汉中市': '610700',
          '榆林市': '610800',
          '安康市': '610900',
          '商洛市': '611000'
        },
        '甘肃省': {
          '兰州市': '620100',
          '嘉峪关市': '620200',
          '金昌市': '620300',
          '白银市': '620400',
          '天水市': '620500',
          '武威市': '620600',
          '张掖市': '620700',
          '平凉市': '620800',
          '酒泉市': '620900',
          '庆阳市': '621000',
          '定西市': '621100',
          '陇南市': '621200',
          '临夏回族自治州': '622900',
          '甘南藏族自治州': '623000'
        },
        '青海省': {
          '西宁市': '630100',
          '海东市': '630200',
          '海北藏族自治州': '632200',
          '黄南藏族自治州': '632300',
          '海南藏族自治州': '632500',
          '果洛藏族自治州': '632600',
          '玉树藏族自治州': '632700',
          '海西蒙古族藏族自治州': '632800'
        },
        '宁夏回族自治区': {
          '银川市': '640100',
          '石嘴山市': '640200',
          '吴忠市': '640300',
          '固原市': '640400',
          '中卫市': '640500'
        },
        '新疆维吾尔自治区': {
          '乌鲁木齐市': '650100',
          '克拉玛依市': '650200',
          '吐鲁番市': '650400',
          '哈密市': '650500',
          '昌吉回族自治州': '652300',
          '博尔塔拉蒙古自治州': '652700',
          '巴音郭楞蒙古自治州': '652800',
          '阿克苏地区': '652900',
          '克孜勒苏柯尔克孜自治州': '653000',
          '喀什地区': '653100',
          '和田地区': '653200',
          '伊犁哈萨克自治州': '654000',
          '塔城地区': '654200',
          '阿勒泰地区': '654300'
        },
        '台湾省': {
          '台北市': '710100',
          '高雄市': '710200',
          '基隆市': '710300',
          '台中市': '710400',
          '台南市': '710500',
          '新竹市': '710600',
          '嘉义市': '710700'
        },
        '香港特别行政区': {
          '中西区': '810101',
          '湾仔区': '810102',
          '东区': '810103',
          '南区': '810104',
          '油尖旺区': '810105',
          '深水埗区': '810106',
          '九龙城区': '810107',
          '黄大仙区': '810108',
          '观塘区': '810109',
          '荃湾区': '810110',
          '屯门区': '810111',
          '元朗区': '810112',
          '北区': '810113',
          '大埔区': '810114',
          '西贡区': '810115',
          '沙田区': '810116',
          '葵青区': '810117',
          '离岛区': '810118'
        },
        '澳门特别行政区': {
          '花地玛堂区': '820101',
          '圣安多尼堂区': '820102',
          '大堂区': '820103',
          '望德堂区': '820104',
          '风顺堂区': '820105',
          '嘉模堂区': '820106',
          '圣方济各堂区': '820107'
        }
      },
      addressOptions: [
        {
          value: '北京市',
          label: '北京市',
          children: [
            { value: '东城区', label: '东城区' },
            { value: '西城区', label: '西城区' },
            { value: '朝阳区', label: '朝阳区' },
            { value: '丰台区', label: '丰台区' },
            { value: '石景山区', label: '石景山区' },
            { value: '海淀区', label: '海淀区' },
            { value: '门头沟区', label: '门头沟区' },
            { value: '房山区', label: '房山区' },
            { value: '通州区', label: '通州区' },
            { value: '顺义区', label: '顺义区' },
            { value: '昌平区', label: '昌平区' },
            { value: '大兴区', label: '大兴区' },
            { value: '怀柔区', label: '怀柔区' },
            { value: '平谷区', label: '平谷区' },
            { value: '密云区', label: '密云区' },
            { value: '延庆区', label: '延庆区' }
          ]
        },
        {
          value: '天津市',
          label: '天津市',
          children: [
            { value: '和平区', label: '和平区' },
            { value: '河东区', label: '河东区' },
            { value: '河西区', label: '河西区' },
            { value: '南开区', label: '南开区' },
            { value: '河北区', label: '河北区' },
            { value: '红桥区', label: '红桥区' },
            { value: '东丽区', label: '东丽区' },
            { value: '西青区', label: '西青区' },
            { value: '津南区', label: '津南区' },
            { value: '北辰区', label: '北辰区' },
            { value: '武清区', label: '武清区' },
            { value: '宝坻区', label: '宝坻区' },
            { value: '滨海新区', label: '滨海新区' },
            { value: '宁河区', label: '宁河区' },
            { value: '静海区', label: '静海区' },
            { value: '蓟州区', label: '蓟州区' }
          ]
        },
        {
          value: '河北省',
          label: '河北省',
          children: [
            { value: '石家庄市', label: '石家庄市' },
            { value: '唐山市', label: '唐山市' },
            { value: '秦皇岛市', label: '秦皇岛市' },
            { value: '邯郸市', label: '邯郸市' },
            { value: '邢台市', label: '邢台市' },
            { value: '保定市', label: '保定市' },
            { value: '张家口市', label: '张家口市' },
            { value: '承德市', label: '承德市' },
            { value: '沧州市', label: '沧州市' },
            { value: '廊坊市', label: '廊坊市' },
            { value: '衡水市', label: '衡水市' }
          ]
        },
        {
          value: '山西省',
          label: '山西省',
          children: [
            { value: '太原市', label: '太原市' },
            { value: '大同市', label: '大同市' },
            { value: '阳泉市', label: '阳泉市' },
            { value: '长治市', label: '长治市' },
            { value: '晋城市', label: '晋城市' },
            { value: '朔州市', label: '朔州市' },
            { value: '晋中市', label: '晋中市' },
            { value: '运城市', label: '运城市' },
            { value: '忻州市', label: '忻州市' },
            { value: '临汾市', label: '临汾市' },
            { value: '吕梁市', label: '吕梁市' }
          ]
        },
        {
          value: '内蒙古自治区',
          label: '内蒙古自治区',
          children: [
            { value: '呼和浩特市', label: '呼和浩特市' },
            { value: '包头市', label: '包头市' },
            { value: '乌海市', label: '乌海市' },
            { value: '赤峰市', label: '赤峰市' },
            { value: '通辽市', label: '通辽市' },
            { value: '鄂尔多斯市', label: '鄂尔多斯市' },
            { value: '呼伦贝尔市', label: '呼伦贝尔市' },
            { value: '巴彦淖尔市', label: '巴彦淖尔市' },
            { value: '乌兰察布市', label: '乌兰察布市' },
            { value: '兴安盟', label: '兴安盟' },
            { value: '锡林郭勒盟', label: '锡林郭勒盟' },
            { value: '阿拉善盟', label: '阿拉善盟' }
          ]
        },
        {
          value: '辽宁省',
          label: '辽宁省',
          children: [
            { value: '沈阳市', label: '沈阳市' },
            { value: '大连市', label: '大连市' },
            { value: '鞍山市', label: '鞍山市' },
            { value: '抚顺市', label: '抚顺市' },
            { value: '本溪市', label: '本溪市' },
            { value: '丹东市', label: '丹东市' },
            { value: '锦州市', label: '锦州市' },
            { value: '营口市', label: '营口市' },
            { value: '阜新市', label: '阜新市' },
            { value: '辽阳市', label: '辽阳市' },
            { value: '盘锦市', label: '盘锦市' },
            { value: '铁岭市', label: '铁岭市' },
            { value: '朝阳市', label: '朝阳市' },
            { value: '葫芦岛市', label: '葫芦岛市' }
          ]
        },
        {
          value: '吉林省',
          label: '吉林省',
          children: [
            { value: '长春市', label: '长春市' },
            { value: '吉林市', label: '吉林市' },
            { value: '四平市', label: '四平市' },
            { value: '辽源市', label: '辽源市' },
            { value: '通化市', label: '通化市' },
            { value: '白山市', label: '白山市' },
            { value: '松原市', label: '松原市' },
            { value: '白城市', label: '白城市' },
            { value: '延边朝鲜族自治州', label: '延边朝鲜族自治州' }
          ]
        },
        {
          value: '黑龙江省',
          label: '黑龙江省',
          children: [
            { value: '哈尔滨市', label: '哈尔滨市' },
            { value: '齐齐哈尔市', label: '齐齐哈尔市' },
            { value: '鸡西市', label: '鸡西市' },
            { value: '鹤岗市', label: '鹤岗市' },
            { value: '双鸭山市', label: '双鸭山市' },
            { value: '大庆市', label: '大庆市' },
            { value: '伊春市', label: '伊春市' },
            { value: '佳木斯市', label: '佳木斯市' },
            { value: '七台河市', label: '七台河市' },
            { value: '牡丹江市', label: '牡丹江市' },
            { value: '黑河市', label: '黑河市' },
            { value: '绥化市', label: '绥化市' },
            { value: '大兴安岭地区', label: '大兴安岭地区' }
          ]
        },
        {
          value: '上海市',
          label: '上海市',
          children: [
            { value: '黄浦区', label: '黄浦区' },
            { value: '徐汇区', label: '徐汇区' },
            { value: '长宁区', label: '长宁区' },
            { value: '静安区', label: '静安区' },
            { value: '普陀区', label: '普陀区' },
            { value: '虹口区', label: '虹口区' },
            { value: '杨浦区', label: '杨浦区' },
            { value: '闵行区', label: '闵行区' },
            { value: '宝山区', label: '宝山区' },
            { value: '嘉定区', label: '嘉定区' },
            { value: '浦东新区', label: '浦东新区' },
            { value: '金山区', label: '金山区' },
            { value: '松江区', label: '松江区' },
            { value: '青浦区', label: '青浦区' },
            { value: '奉贤区', label: '奉贤区' },
            { value: '崇明区', label: '崇明区' }
          ]
        },
        {
          value: '江苏省',
          label: '江苏省',
          children: [
            { value: '南京市', label: '南京市' },
            { value: '无锡市', label: '无锡市' },
            { value: '徐州市', label: '徐州市' },
            { value: '常州市', label: '常州市' },
            { value: '苏州市', label: '苏州市' },
            { value: '南通市', label: '南通市' },
            { value: '连云港市', label: '连云港市' },
            { value: '淮安市', label: '淮安市' },
            { value: '盐城市', label: '盐城市' },
            { value: '扬州市', label: '扬州市' },
            { value: '镇江市', label: '镇江市' },
            { value: '泰州市', label: '泰州市' },
            { value: '宿迁市', label: '宿迁市' }
          ]
        },
        {
          value: '浙江省',
          label: '浙江省',
          children: [
            { value: '杭州市', label: '杭州市' },
            { value: '宁波市', label: '宁波市' },
            { value: '温州市', label: '温州市' },
            { value: '嘉兴市', label: '嘉兴市' },
            { value: '湖州市', label: '湖州市' },
            { value: '绍兴市', label: '绍兴市' },
            { value: '金华市', label: '金华市' },
            { value: '衢州市', label: '衢州市' },
            { value: '舟山市', label: '舟山市' },
            { value: '台州市', label: '台州市' },
            { value: '丽水市', label: '丽水市' }
          ]
        },
        {
          value: '安徽省',
          label: '安徽省',
          children: [
            { value: '合肥市', label: '合肥市' },
            { value: '芜湖市', label: '芜湖市' },
            { value: '蚌埠市', label: '蚌埠市' },
            { value: '淮南市', label: '淮南市' },
            { value: '马鞍山市', label: '马鞍山市' },
            { value: '淮北市', label: '淮北市' },
            { value: '铜陵市', label: '铜陵市' },
            { value: '安庆市', label: '安庆市' },
            { value: '黄山市', label: '黄山市' },
            { value: '滁州市', label: '滁州市' },
            { value: '阜阳市', label: '阜阳市' },
            { value: '宿州市', label: '宿州市' },
            { value: '六安市', label: '六安市' },
            { value: '亳州市', label: '亳州市' },
            { value: '池州市', label: '池州市' },
            { value: '宣城市', label: '宣城市' }
          ]
        },
        {
          value: '福建省',
          label: '福建省',
          children: [
            { value: '福州市', label: '福州市' },
            { value: '厦门市', label: '厦门市' },
            { value: '莆田市', label: '莆田市' },
            { value: '三明市', label: '三明市' },
            { value: '泉州市', label: '泉州市' },
            { value: '漳州市', label: '漳州市' },
            { value: '南平市', label: '南平市' },
            { value: '龙岩市', label: '龙岩市' },
            { value: '宁德市', label: '宁德市' }
          ]
        },
        {
          value: '江西省',
          label: '江西省',
          children: [
            { value: '南昌市', label: '南昌市' },
            { value: '景德镇市', label: '景德镇市' },
            { value: '萍乡市', label: '萍乡市' },
            { value: '九江市', label: '九江市' },
            { value: '新余市', label: '新余市' },
            { value: '鹰潭市', label: '鹰潭市' },
            { value: '赣州市', label: '赣州市' },
            { value: '吉安市', label: '吉安市' },
            { value: '宜春市', label: '宜春市' },
            { value: '抚州市', label: '抚州市' },
            { value: '上饶市', label: '上饶市' }
          ]
        },
        {
          value: '山东省',
          label: '山东省',
          children: [
            { value: '济南市', label: '济南市' },
            { value: '青岛市', label: '青岛市' },
            { value: '淄博市', label: '淄博市' },
            { value: '枣庄市', label: '枣庄市' },
            { value: '东营市', label: '东营市' },
            { value: '烟台市', label: '烟台市' },
            { value: '潍坊市', label: '潍坊市' },
            { value: '济宁市', label: '济宁市' },
            { value: '泰安市', label: '泰安市' },
            { value: '威海市', label: '威海市' },
            { value: '日照市', label: '日照市' },
            { value: '临沂市', label: '临沂市' },
            { value: '德州市', label: '德州市' },
            { value: '聊城市', label: '聊城市' },
            { value: '滨州市', label: '滨州市' },
            { value: '菏泽市', label: '菏泽市' }
          ]
        },
        {
          value: '河南省',
          label: '河南省',
          children: [
            { value: '郑州市', label: '郑州市' },
            { value: '开封市', label: '开封市' },
            { value: '洛阳市', label: '洛阳市' },
            { value: '平顶山市', label: '平顶山市' },
            { value: '安阳市', label: '安阳市' },
            { value: '鹤壁市', label: '鹤壁市' },
            { value: '新乡市', label: '新乡市' },
            { value: '焦作市', label: '焦作市' },
            { value: '濮阳市', label: '濮阳市' },
            { value: '许昌市', label: '许昌市' },
            { value: '漯河市', label: '漯河市' },
            { value: '三门峡市', label: '三门峡市' },
            { value: '南阳市', label: '南阳市' },
            { value: '商丘市', label: '商丘市' },
            { value: '信阳市', label: '信阳市' },
            { value: '周口市', label: '周口市' },
            { value: '驻马店市', label: '驻马店市' }
          ]
        },
        {
          value: '湖北省',
          label: '湖北省',
          children: [
            { value: '武汉市', label: '武汉市' },
            { value: '黄石市', label: '黄石市' },
            { value: '十堰市', label: '十堰市' },
            { value: '宜昌市', label: '宜昌市' },
            { value: '襄阳市', label: '襄阳市' },
            { value: '鄂州市', label: '鄂州市' },
            { value: '荆门市', label: '荆门市' },
            { value: '孝感市', label: '孝感市' },
            { value: '荆州市', label: '荆州市' },
            { value: '黄冈市', label: '黄冈市' },
            { value: '咸宁市', label: '咸宁市' },
            { value: '随州市', label: '随州市' },
            { value: '恩施土家族苗族自治州', label: '恩施土家族苗族自治州' }
          ]
        },
        {
          value: '湖南省',
          label: '湖南省',
          children: [
            { value: '长沙市', label: '长沙市' },
            { value: '株洲市', label: '株洲市' },
            { value: '湘潭市', label: '湘潭市' },
            { value: '衡阳市', label: '衡阳市' },
            { value: '邵阳市', label: '邵阳市' },
            { value: '岳阳市', label: '岳阳市' },
            { value: '常德市', label: '常德市' },
            { value: '张家界市', label: '张家界市' },
            { value: '益阳市', label: '益阳市' },
            { value: '郴州市', label: '郴州市' },
            { value: '永州市', label: '永州市' },
            { value: '怀化市', label: '怀化市' },
            { value: '娄底市', label: '娄底市' },
            { value: '湘西土家族苗族自治州', label: '湘西土家族苗族自治州' }
          ]
        },
        {
          value: '广东省',
          label: '广东省',
          children: [
            { value: '广州市', label: '广州市' },
            { value: '韶关市', label: '韶关市' },
            { value: '深圳市', label: '深圳市' },
            { value: '珠海市', label: '珠海市' },
            { value: '汕头市', label: '汕头市' },
            { value: '佛山市', label: '佛山市' },
            { value: '江门市', label: '江门市' },
            { value: '湛江市', label: '湛江市' },
            { value: '茂名市', label: '茂名市' },
            { value: '肇庆市', label: '肇庆市' },
            { value: '惠州市', label: '惠州市' },
            { value: '梅州市', label: '梅州市' },
            { value: '汕尾市', label: '汕尾市' },
            { value: '河源市', label: '河源市' },
            { value: '阳江市', label: '阳江市' },
            { value: '清远市', label: '清远市' },
            { value: '东莞市', label: '东莞市' },
            { value: '中山市', label: '中山市' },
            { value: '潮州市', label: '潮州市' },
            { value: '揭阳市', label: '揭阳市' },
            { value: '云浮市', label: '云浮市' }
          ]
        },
        {
          value: '广西壮族自治区',
          label: '广西壮族自治区',
          children: [
            { value: '南宁市', label: '南宁市' },
            { value: '柳州市', label: '柳州市' },
            { value: '桂林市', label: '桂林市' },
            { value: '梧州市', label: '梧州市' },
            { value: '北海市', label: '北海市' },
            { value: '防城港市', label: '防城港市' },
            { value: '钦州市', label: '钦州市' },
            { value: '贵港市', label: '贵港市' },
            { value: '玉林市', label: '玉林市' },
            { value: '百色市', label: '百色市' },
            { value: '贺州市', label: '贺州市' },
            { value: '河池市', label: '河池市' },
            { value: '来宾市', label: '来宾市' },
            { value: '崇左市', label: '崇左市' }
          ]
        },
        {
          value: '海南省',
          label: '海南省',
          children: [
            { value: '海口市', label: '海口市' },
            { value: '三亚市', label: '三亚市' },
            { value: '三沙市', label: '三沙市' },
            { value: '儋州市', label: '儋州市' },
            { value: '五指山市', label: '五指山市' },
            { value: '琼海市', label: '琼海市' },
            { value: '文昌市', label: '文昌市' },
            { value: '万宁市', label: '万宁市' },
            { value: '东方市', label: '东方市' },
            { value: '定安县', label: '定安县' },
            { value: '屯昌县', label: '屯昌县' },
            { value: '澄迈县', label: '澄迈县' },
            { value: '临高县', label: '临高县' },
            { value: '白沙黎族自治县', label: '白沙黎族自治县' },
            { value: '昌江黎族自治县', label: '昌江黎族自治县' },
            { value: '乐东黎族自治县', label: '乐东黎族自治县' },
            { value: '陵水黎族自治县', label: '陵水黎族自治县' },
            { value: '保亭黎族苗族自治县', label: '保亭黎族苗族自治县' },
            { value: '琼中黎族苗族自治县', label: '琼中黎族苗族自治县' }
          ]
        },
        {
          value: '重庆市',
          label: '重庆市',
          children: [
            { value: '万州区', label: '万州区' },
            { value: '涪陵区', label: '涪陵区' },
            { value: '渝中区', label: '渝中区' },
            { value: '大渡口区', label: '大渡口区' },
            { value: '江北区', label: '江北区' },
            { value: '沙坪坝区', label: '沙坪坝区' },
            { value: '九龙坡区', label: '九龙坡区' },
            { value: '南岸区', label: '南岸区' },
            { value: '北碚区', label: '北碚区' },
            { value: '綦江区', label: '綦江区' },
            { value: '大足区', label: '大足区' },
            { value: '渝北区', label: '渝北区' },
            { value: '巴南区', label: '巴南区' },
            { value: '黔江区', label: '黔江区' },
            { value: '长寿区', label: '长寿区' },
            { value: '江津区', label: '江津区' },
            { value: '合川区', label: '合川区' },
            { value: '永川区', label: '永川区' },
            { value: '南川区', label: '南川区' },
            { value: '璧山区', label: '璧山区' },
            { value: '铜梁区', label: '铜梁区' },
            { value: '潼南区', label: '潼南区' },
            { value: '荣昌区', label: '荣昌区' },
            { value: '开州区', label: '开州区' },
            { value: '梁平区', label: '梁平区' },
            { value: '武隆区', label: '武隆区' }
          ]
        },
        {
          value: '四川省',
          label: '四川省',
          children: [
            { value: '成都市', label: '成都市' },
            { value: '自贡市', label: '自贡市' },
            { value: '攀枝花市', label: '攀枝花市' },
            { value: '泸州市', label: '泸州市' },
            { value: '德阳市', label: '德阳市' },
            { value: '绵阳市', label: '绵阳市' },
            { value: '广元市', label: '广元市' },
            { value: '遂宁市', label: '遂宁市' },
            { value: '内江市', label: '内江市' },
            { value: '乐山市', label: '乐山市' },
            { value: '南充市', label: '南充市' },
            { value: '眉山市', label: '眉山市' },
            { value: '宜宾市', label: '宜宾市' },
            { value: '广安市', label: '广安市' },
            { value: '达州市', label: '达州市' },
            { value: '雅安市', label: '雅安市' },
            { value: '巴中市', label: '巴中市' },
            { value: '资阳市', label: '资阳市' },
            { value: '阿坝藏族羌族自治州', label: '阿坝藏族羌族自治州' },
            { value: '甘孜藏族自治州', label: '甘孜藏族自治州' },
            { value: '凉山彝族自治州', label: '凉山彝族自治州' }
          ]
        },
        {
          value: '贵州省',
          label: '贵州省',
          children: [
            { value: '贵阳市', label: '贵阳市' },
            { value: '六盘水市', label: '六盘水市' },
            { value: '遵义市', label: '遵义市' },
            { value: '安顺市', label: '安顺市' },
            { value: '毕节市', label: '毕节市' },
            { value: '铜仁市', label: '铜仁市' },
            { value: '黔西南布依族苗族自治州', label: '黔西南布依族苗族自治州' },
            { value: '黔东南苗族侗族自治州', label: '黔东南苗族侗族自治州' },
            { value: '黔南布依族苗族自治州', label: '黔南布依族苗族自治州' }
          ]
        },
        {
          value: '云南省',
          label: '云南省',
          children: [
            { value: '昆明市', label: '昆明市' },
            { value: '曲靖市', label: '曲靖市' },
            { value: '玉溪市', label: '玉溪市' },
            { value: '保山市', label: '保山市' },
            { value: '昭通市', label: '昭通市' },
            { value: '丽江市', label: '丽江市' },
            { value: '普洱市', label: '普洱市' },
            { value: '临沧市', label: '临沧市' },
            { value: '楚雄彝族自治州', label: '楚雄彝族自治州' },
            { value: '红河哈尼族彝族自治州', label: '红河哈尼族彝族自治州' },
            { value: '文山壮族苗族自治州', label: '文山壮族苗族自治州' },
            { value: '西双版纳傣族自治州', label: '西双版纳傣族自治州' },
            { value: '大理白族自治州', label: '大理白族自治州' },
            { value: '德宏傣族景颇族自治州', label: '德宏傣族景颇族自治州' },
            { value: '怒江傈僳族自治州', label: '怒江傈僳族自治州' },
            { value: '迪庆藏族自治州', label: '迪庆藏族自治州' }
          ]
        },
        {
          value: '西藏自治区',
          label: '西藏自治区',
          children: [
            { value: '拉萨市', label: '拉萨市' },
            { value: '日喀则市', label: '日喀则市' },
            { value: '昌都市', label: '昌都市' },
            { value: '林芝市', label: '林芝市' },
            { value: '山南市', label: '山南市' },
            { value: '那曲市', label: '那曲市' },
            { value: '阿里地区', label: '阿里地区' }
          ]
        },
        {
          value: '陕西省',
          label: '陕西省',
          children: [
            { value: '西安市', label: '西安市' },
            { value: '铜川市', label: '铜川市' },
            { value: '宝鸡市', label: '宝鸡市' },
            { value: '咸阳市', label: '咸阳市' },
            { value: '渭南市', label: '渭南市' },
            { value: '延安市', label: '延安市' },
            { value: '汉中市', label: '汉中市' },
            { value: '榆林市', label: '榆林市' },
            { value: '安康市', label: '安康市' },
            { value: '商洛市', label: '商洛市' }
          ]
        },
        {
          value: '甘肃省',
          label: '甘肃省',
          children: [
            { value: '兰州市', label: '兰州市' },
            { value: '嘉峪关市', label: '嘉峪关市' },
            { value: '金昌市', label: '金昌市' },
            { value: '白银市', label: '白银市' },
            { value: '天水市', label: '天水市' },
            { value: '武威市', label: '武威市' },
            { value: '张掖市', label: '张掖市' },
            { value: '平凉市', label: '平凉市' },
            { value: '酒泉市', label: '酒泉市' },
            { value: '庆阳市', label: '庆阳市' },
            { value: '定西市', label: '定西市' },
            { value: '陇南市', label: '陇南市' },
            { value: '临夏回族自治州', label: '临夏回族自治州' },
            { value: '甘南藏族自治州', label: '甘南藏族自治州' }
          ]
        },
        {
          value: '青海省',
          label: '青海省',
          children: [
            { value: '西宁市', label: '西宁市' },
            { value: '海东市', label: '海东市' },
            { value: '海北藏族自治州', label: '海北藏族自治州' },
            { value: '黄南藏族自治州', label: '黄南藏族自治州' },
            { value: '海南藏族自治州', label: '海南藏族自治州' },
            { value: '果洛藏族自治州', label: '果洛藏族自治州' },
            { value: '玉树藏族自治州', label: '玉树藏族自治州' },
            { value: '海西蒙古族藏族自治州', label: '海西蒙古族藏族自治州' }
          ]
        },
        {
          value: '宁夏回族自治区',
          label: '宁夏回族自治区',
          children: [
            { value: '银川市', label: '银川市' },
            { value: '石嘴山市', label: '石嘴山市' },
            { value: '吴忠市', label: '吴忠市' },
            { value: '固原市', label: '固原市' },
            { value: '中卫市', label: '中卫市' }
          ]
        },
        {
          value: '新疆维吾尔自治区',
          label: '新疆维吾尔自治区',
          children: [
            { value: '乌鲁木齐市', label: '乌鲁木齐市' },
            { value: '克拉玛依市', label: '克拉玛依市' },
            { value: '吐鲁番市', label: '吐鲁番市' },
            { value: '哈密市', label: '哈密市' },
            { value: '昌吉回族自治州', label: '昌吉回族自治州' },
            { value: '博尔塔拉蒙古自治州', label: '博尔塔拉蒙古自治州' },
            { value: '巴音郭楞蒙古自治州', label: '巴音郭楞蒙古自治州' },
            { value: '阿克苏地区', label: '阿克苏地区' },
            { value: '克孜勒苏柯尔克孜自治州', label: '克孜勒苏柯尔克孜自治州' },
            { value: '喀什地区', label: '喀什地区' },
            { value: '和田地区', label: '和田地区' },
            { value: '伊犁哈萨克自治州', label: '伊犁哈萨克自治州' },
            { value: '塔城地区', label: '塔城地区' },
            { value: '阿勒泰地区', label: '阿勒泰地区' }
          ]
        },
        {
          value: '台湾省',
          label: '台湾省',
          children: [
            { value: '台北市', label: '台北市' },
            { value: '高雄市', label: '高雄市' },
            { value: '基隆市', label: '基隆市' },
            { value: '台中市', label: '台中市' },
            { value: '台南市', label: '台南市' },
            { value: '新竹市', label: '新竹市' },
            { value: '嘉义市', label: '嘉义市' }
          ]
        },
        {
          value: '香港特别行政区',
          label: '香港特别行政区',
          children: [
            { value: '中西区', label: '中西区' },
            { value: '湾仔区', label: '湾仔区' },
            { value: '东区', label: '东区' },
            { value: '南区', label: '南区' },
            { value: '油尖旺区', label: '油尖旺区' },
            { value: '深水埗区', label: '深水埗区' },
            { value: '九龙城区', label: '九龙城区' },
            { value: '黄大仙区', label: '黄大仙区' },
            { value: '观塘区', label: '观塘区' },
            { value: '荃湾区', label: '荃湾区' },
            { value: '屯门区', label: '屯门区' },
            { value: '元朗区', label: '元朗区' },
            { value: '北区', label: '北区' },
            { value: '大埔区', label: '大埔区' },
            { value: '西贡区', label: '西贡区' },
            { value: '沙田区', label: '沙田区' },
            { value: '葵青区', label: '葵青区' },
            { value: '离岛区', label: '离岛区' }
          ]
        },
        {
          value: '澳门特别行政区',
          label: '澳门特别行政区',
          children: [
            { value: '花地玛堂区', label: '花地玛堂区' },
            { value: '圣安多尼堂区', label: '圣安多尼堂区' },
            { value: '大堂区', label: '大堂区' },
            { value: '望德堂区', label: '望德堂区' },
            { value: '风顺堂区', label: '风顺堂区' },
            { value: '嘉模堂区', label: '嘉模堂区' },
            { value: '圣方济各堂区', label: '圣方济各堂区' }
          ]
        }
      ],
      gender: '',
      nation: '',
      birthDate: '',
      validFrom: '',
      validTo: '',
      bankCard: '',
      idType: 'idcard',
      idNumber: '',
      chineseName: '',
      mobile: '',
      email: '',
      address: '',
      company: '',
      hkId: '',
      license: '',
      coords: '',
      profile: '',
      // JSON 处理
      jsonInput: '',
      jsonOutput: '',
      jsonValidateInput: '',
      jsonValidateOutput: '',
      jsonDiffLeft: '',
      jsonDiffRight: '',
      jsonDiffOutput: '',
      jsonPathData: '',
      jsonPathExpr: '',
      jsonPathResult: '',
      jsonFlattenInput: '',
      jsonFlattenOutput: '',
      jsonPathsInput: '',
      jsonPathsOutput: '',
      jsonToXmlInput: '',
      jsonToXmlOutput: '',
      xmlToJsonInput: '',
      xmlToJsonOutput: '',
      jsonToYamlInput: '',
      jsonToYamlOutput: '',
      yamlToJsonInput: '',
      yamlToJsonOutput: '',
      // 编码转换
      barcodeText: '',
      barcodeImage: '',
      qrcodeText: '',
      qrcodeImage: '',
      qrcodeDecodedText: '',
      timestampSeconds: Math.floor(Date.now() / 1000),
      timestampDate: '',
      timestampOutput: '',
      baseNumber: '',
      baseFrom: 10,
      baseTo: 16,
      baseResult: '',
      unicodeInput: '',
      unicodeOutput: '',
      asciiInput: '',
      asciiOutput: '',
      colorHex: '#409EFF',
      colorRgb: 'rgb(64,158,255)',
      urlInput: '',
      urlOutput: '',
      jwtToken: '',
      jwtOutput: '',
      imageToBase64Result: '',
      base64ToImageInput: '',
      base64ToImageSrc: '',
      base64Input: '',
      base64Output: '',
      // 加密哈希
      hashInput: '',
      hashOutput: '',
      hashCompare1: '',
      hashCompare2: '',
      hashCompareResult: '',
      aesKey: '',
      aesPlaintext: '',
      aesEncrypted: '',
      aesCiphertext: '',
      aesDecrypted: '',
      password: '',
      passwordStrengthScore: 0,
      passwordStrengthTips: '',
      passwordStrengthColor: '',
      salt: '',
      // 字符串处理
      textDiffLeft: '',
      textDiffRight: '',
      textDiffOutput: '',
      trimInput: '',
      trimType: 'trim',
      trimOutput: '',
      replaceInput: '',
      replaceSearch: '',
      replaceWith: '',
      replaceGlobal: true,
      replaceRegex: false,
      replaceOutput: '',
      escapeInput: '',
      escapeOutput: '',
      formatTextInput: '',
      formatTextOutput: '',
      // 定时任务
      cronMinute: '*',
      cronHour: '*',
      cronDay: '*',
      cronMonth: '*',
      cronWeek: '*',
      cronExpression: '',
      cronParseInput: '',
      cronParseOutput: '',
      cronNextInput: '',
      cronBaseTime: null,
      cronNextOutput: '',
      cronValidateInput: '',
      cronValidateOutput: '',
      // 随机数据
      randIntMin: 0,
      randIntMax: 100,
      randomInt: '',
      randFloatMin: 0,
      randFloatMax: 1,
      randFloatDecimals: 2,
      randomFloat: '',
      randStrLen: 8,
      randStrCharset: 'alnum',
      randomString: '',
      uuid: '',
      randomBool: '',
      macAddress: '',
      ipAddress: '',
      randDateStart: null,
      randDateEnd: null,
      randomDate: '',
      randPwdLen: 12,
      randPwdChars: ['lower', 'upper', 'digit'],
      randomPassword: '',
      randomColor: '',
      randSeqLength: 5,
      randSeqType: 'int',
      randomSequence: '',
      // 正则测试
      regexPattern: '',
      regexText: '',
      regexOutput: '',
      // 字数统计
      statsInput: '',
      stats: { charCount: 0, wordCount: 0, lineCount: 0, byteCount: 0 },
      // 大小写转换
      caseInput: '',
      caseOutput: '',
    }
  },
  mounted() {
    this.initTools()
    this.filterTools()
    this.initTimestampDate()
  },
  methods: {
    initTools() {
      // 定义所有工具（包含所有分组）
      const allTools = [
        // 测试数据生成
        { name: '身份证正反面', id: 'idcard', description: '生成身份证正面/反面图片', icon: 'Picture', color: '#409EFF', group: '测试数据生成' },
        { name: '银行卡号', id: 'bankcard', description: '生成随机银行卡号', icon: 'CreditCard', color: '#67C23A', group: '测试数据生成' },
        { name: '证件号', id: 'idnumber', description: '生成各种类型的证件号码', icon: 'User', color: '#E6A23C', group: '测试数据生成' },
        { name: '中文姓名', id: 'chineseName', description: '生成随机中文姓名', icon: 'User', color: '#F56C6C', group: '测试数据生成' },
        { name: '手机号', id: 'mobile', description: '生成随机手机号', icon: 'Phone', color: '#909399', group: '测试数据生成' },
        { name: '邮箱地址', id: 'email', description: '生成随机邮箱地址', icon: 'Message', color: '#1E90FF', group: '测试数据生成' },
        { name: '地址信息', id: 'address', description: '生成随机地址', icon: 'Location', color: '#32CD32', group: '测试数据生成' },
        { name: '公司名称', id: 'company', description: '生成随机公司名称', icon: 'OfficeBuilding', color: '#FFD700', group: '测试数据生成' },

        { name: '营业执照号', id: 'license', description: '生成营业执照号', icon: 'Document', color: '#8A2BE2', group: '测试数据生成' },
        { name: '经纬度坐标', id: 'coords', description: '生成随机经纬度', icon: 'Location', color: '#20B2AA', group: '测试数据生成' },
        { name: '用户档案', id: 'profile', description: '生成完整用户档案', icon: 'UserFilled', color: '#FF7F50', group: '测试数据生成' },
        // JSON 处理
        { name: 'JSON 格式化', id: 'jsonFormat', description: '格式化/压缩 JSON', icon: 'Document', color: '#409EFF', group: 'JSON 处理' },
        { name: 'JSON 校验', id: 'jsonValidate', description: '验证 JSON 合法性', icon: 'CircleCheck', color: '#67C23A', group: 'JSON 处理' },
        { name: 'JSON 对比增强', id: 'jsonDiff', description: '对比两个 JSON 差异', icon: 'CopyDocument', color: '#E6A23C', group: 'JSON 处理' },
        { name: 'JSONPath 查询', id: 'jsonpath', description: '使用 JSONPath 查询数据', icon: 'Search', color: '#F56C6C', group: 'JSON 处理' },
        { name: 'JSON 扁平化', id: 'jsonFlatten', description: '将嵌套 JSON 扁平化', icon: 'List', color: '#909399', group: 'JSON 处理' },
        { name: 'JSON 路径列表', id: 'jsonPaths', description: '列出所有 JSON 路径', icon: 'Folder', color: '#1E90FF', group: 'JSON 处理' },
        { name: 'JSON 转 XML', id: 'jsonToXml', description: 'JSON 转换为 XML', icon: 'Connection', color: '#32CD32', group: 'JSON 处理' },
        { name: 'XML 转 JSON', id: 'xmlToJson', description: 'XML 转换为 JSON', icon: 'Connection', color: '#FFD700', group: 'JSON 处理' },
        { name: 'JSON 转 YAML', id: 'jsonToYaml', description: 'JSON 转 YAML 格式', icon: 'Document', color: '#FF69B4', group: 'JSON 处理' },
        { name: 'YAML 转 JSON', id: 'yamlToJson', description: 'YAML 转 JSON 格式', icon: 'Document', color: '#8A2BE2', group: 'JSON 处理' },
        // 编码转换
        { name: '条形码', id: 'barcode', description: '生成条形码图片', icon: 'Grid', color: '#409EFF', group: '编码转换' },
        { name: '二维码', id: 'qrcode', description: '生成二维码图片', icon: 'Grid', color: '#67C23A', group: '编码转换' },
        { name: '二维码解析', id: 'qrcodeDecode', description: '解析二维码内容', icon: 'Search', color: '#E6A23C', group: '编码转换' },
        { name: '时间戳转换', id: 'timestampConv', description: 'Unix 时间戳与日期互转', icon: 'Clock', color: '#F56C6C', group: '编码转换' },
        { name: '进制转换', id: 'baseConvert', description: '任意进制互转', icon: 'Operation', color: '#909399', group: '编码转换' },
        { name: 'Unicode 转换', id: 'unicodeConv', description: '文本与 Unicode 互转', icon: 'MagicStick', color: '#1E90FF', group: '编码转换' },
        { name: 'ASCII 转换', id: 'ascii', description: '文本与 ASCII 码互转', icon: 'Document', color: '#32CD32', group: '编码转换' },
        { name: '颜色转换', id: 'colorConv', description: 'RGB/HEX 颜色转换', icon: 'ColorPicker', color: '#FFD700', group: '编码转换' },
        { name: 'URL 编码', id: 'urlEncode', description: 'URL 编码/解码', icon: 'Link', color: '#FF69B4', group: '编码转换' },
        { name: 'JWT 解析', id: 'jwt', description: '解析 JWT Token', icon: 'Key', color: '#8A2BE2', group: '编码转换' },
        { name: '图片转 Base64', id: 'imageToBase64', description: '图片文件转 Base64', icon: 'Picture', color: '#20B2AA', group: '编码转换' },
        { name: 'Base64 转图片', id: 'base64ToImage', description: 'Base64 还原为图片', icon: 'Picture', color: '#FF7F50', group: '编码转换' },
        { name: 'Base64 编码', id: 'base64Encode', description: '文本 Base64 编码/解码', icon: 'Lock', color: '#409EFF', group: '编码转换' },
        // 加密哈希
        { name: 'MD5', id: 'md5Hash', description: '计算 MD5 哈希值', icon: 'Lock', color: '#409EFF', group: '加密哈希' },
        { name: 'SHA-1', id: 'sha1Hash', description: '计算 SHA-1 哈希值', icon: 'Lock', color: '#67C23A', group: '加密哈希' },
        { name: 'SHA-256', id: 'sha256Hash', description: '计算 SHA-256 哈希值', icon: 'Lock', color: '#E6A23C', group: '加密哈希' },
        { name: 'SHA-512', id: 'sha512Hash', description: '计算 SHA-512 哈希值', icon: 'Lock', color: '#F56C6C', group: '加密哈希' },
        { name: '哈希对比', id: 'hashCompare', description: '对比两个哈希值是否相同', icon: 'CopyDocument', color: '#909399', group: '加密哈希' },
        { name: 'AES 加密', id: 'aesEncrypt', description: 'AES 对称加密', icon: 'Lock', color: '#1E90FF', group: '加密哈希' },
        { name: 'AES 解密', id: 'aesDecrypt', description: 'AES 对称解密', icon: 'Unlock', color: '#32CD32', group: '加密哈希' },
        { name: '密码强度', id: 'passwordStrength', description: '检测密码强度', icon: 'Key', color: '#FFD700', group: '加密哈希' },
        { name: '生成盐值', id: 'generateSalt', description: '生成随机盐值', icon: 'Refresh', color: '#FF69B4', group: '加密哈希' },
        // 字符串处理
        { name: '文本对比', id: 'textDiff', description: '对比两段文本差异', icon: 'CopyDocument', color: '#409EFF', group: '字符串处理' },
        { name: '正则测试', id: 'regexTest', description: '测试正则表达式匹配', icon: 'Search', color: '#67C23A', group: '字符串处理' },
        { name: '去除空格', id: 'trimSpaces', description: '去除首尾、所有或多余空格', icon: 'Delete', color: '#E6A23C', group: '字符串处理' },
        { name: '字符替换', id: 'replace', description: '查找并替换字符', icon: 'EditPen', color: '#F56C6C', group: '字符串处理' },
        { name: '字符转义/反转义', id: 'escape', description: 'HTML实体转义与反转义', icon: 'Lock', color: '#909399', group: '字符串处理' },
        { name: '字数统计', id: 'wordCount', description: '统计字符、单词数', icon: 'DataAnalysis', color: '#1E90FF', group: '字符串处理' },
        { name: '大小写转换', id: 'caseConvert', description: '转换文本大小写', icon: 'Edit', color: '#32CD32', group: '字符串处理' },
        { name: '文本格式化', id: 'formatText', description: '去除多余空行和空格', icon: 'Operation', color: '#FFD700', group: '字符串处理' },
        // 定时任务
        { name: '生成Cron表达式', id: 'cronGen', description: '根据参数生成Cron表达式', icon: 'Timer', color: '#FF69B4', group: '定时任务' },
        { name: '解析表达式', id: 'cronParse', description: '解析Cron表达式含义', icon: 'Document', color: '#8A2BE2', group: '定时任务' },
        { name: '下次执行时间', id: 'cronNext', description: '计算下次执行时间', icon: 'Clock', color: '#20B2AA', group: '定时任务' },
        { name: '验证表达式', id: 'cronValidate', description: '验证Cron表达式有效性', icon: 'CircleCheck', color: '#FF7F50', group: '定时任务' },
        // 随机数据（合并到测试数据生成）
        { name: '随机字符串', id: 'randomString', description: '生成随机字符串', icon: 'Document', color: '#E6A23C', group: '测试数据生成' },
        { name: 'UUID', id: 'uuid', description: '生成UUID', icon: 'Key', color: '#F56C6C', group: '测试数据生成' },

        { name: 'MAC地址', id: 'mac', description: '生成随机MAC地址', icon: 'Connection', color: '#1E90FF', group: '测试数据生成' },
        { name: 'IP地址', id: 'ip', description: '生成随机IP地址', icon: 'Location', color: '#32CD32', group: '测试数据生成' },
        { name: '随机日期', id: 'randomDate', description: '生成随机日期', icon: 'Calendar', color: '#FFD700', group: '测试数据生成' },
        { name: '随机密码', id: 'randomPassword', description: '生成随机密码', icon: 'Lock', color: '#FF69B4', group: '测试数据生成' },
        { name: '随机颜色', id: 'randomColor', description: '生成随机颜色', icon: 'ColorPicker', color: '#8A2BE2', group: '测试数据生成' },
        { name: '随机序列', id: 'randomSequence', description: '生成随机数组序列', icon: 'List', color: '#20B2AA', group: '测试数据生成' }
      ]
      // 按分组聚合
      const groups = {}
      allTools.forEach(tool => {
        if (!groups[tool.group]) groups[tool.group] = []
        groups[tool.group].push(tool)
      })
      this.originalGroups = Object.entries(groups).map(([name, tools]) => ({ name, tools }))
      this.allTools = allTools
    },
    filterTools() {
      const keyword = this.searchKeyword.toLowerCase()
      if (!keyword) {
        this.filteredGroups = this.originalGroups.map(group => ({ ...group, tools: [...group.tools] }))
      } else {
        this.filteredGroups = this.originalGroups
          .map(group => ({
            ...group,
            tools: group.tools.filter(tool => 
              tool.name.toLowerCase().includes(keyword) || 
              tool.description.toLowerCase().includes(keyword)
            )
          }))
          .filter(group => group.tools.length > 0)
      }
    },
    openToolDialog(tool) {
      this.currentTool = tool
      this.dialogVisible = true
      // 重置数据
      if (tool.id === 'idcard') {
        this.idcardFrontImage = this.idcardBackImage = ''
        this.idcardName = '张三'
        this.idcardBirthDate = '1990-01-01'
        this.idcardGender = '男'
        this.idcardProvinceCity = ['北京市', '东城区']
        this.idcardDetailAddress = '朝阳门内大街1号'
        this.gender = ''
        this.nation = ''
        this.birthDate = ''
        this.validFrom = ''
        this.validTo = ''
        
        // 延迟生成身份证图片，确保DOM已渲染
        this.$nextTick(() => {
          this.generateIdCard()
        })
      }
      else if (tool.id === 'bankcard') {
        this.bankCard = ''
        // 延迟生成银行卡号，确保DOM已渲染
        this.$nextTick(() => {
          this.generateBankCard()
        })
      }
      else if (tool.id === 'idnumber') {
        this.idNumber = ''
        // 延迟生成身份证号，确保DOM已渲染
        this.$nextTick(() => {
          this.generateIdNumber()
        })
      }
      else if (tool.id === 'chineseName') {
        this.chineseName = ''
        // 延迟生成中文姓名，确保DOM已渲染
        this.$nextTick(() => {
          this.generateChineseName()
        })
      }
      else if (tool.id === 'mobile') {
        this.mobile = ''
        // 延迟生成手机号，确保DOM已渲染
        this.$nextTick(() => {
          this.generateMobile()
        })
      }
      else if (tool.id === 'email') {
        this.email = ''
        // 延迟生成邮箱，确保DOM已渲染
        this.$nextTick(() => {
          this.generateEmail()
        })
      }
      else if (tool.id === 'address') {
        this.address = ''
        // 延迟生成地址，确保DOM已渲染
        this.$nextTick(() => {
          this.generateAddress()
        })
      }
      else if (tool.id === 'company') {
        this.company = ''
        // 延迟生成公司名称，确保DOM已渲染
        this.$nextTick(() => {
          this.generateCompany()
        })
      }
      else if (tool.id === 'hkid') this.hkId = ''
      else if (tool.id === 'license') {
        this.license = ''
        // 延迟生成营业执照号，确保DOM已渲染
        this.$nextTick(() => {
          this.generateLicense()
        })
      }
      else if (tool.id === 'coords') {
        this.coords = ''
        // 延迟生成经纬度，确保DOM已渲染
        this.$nextTick(() => {
          this.generateCoords()
        })
      }
      else if (tool.id === 'profile') {
        this.profile = ''
        // 延迟生成用户档案，确保DOM已渲染
        this.$nextTick(() => {
          this.generateProfile()
        })
      }
      else if (tool.id === 'jsonFormat' || tool.id === 'jsonValidate') this.jsonInput = this.jsonValidateInput = this.jsonOutput = this.jsonValidateOutput = ''
      else if (tool.id === 'jsonDiff') this.jsonDiffLeft = this.jsonDiffRight = this.jsonDiffOutput = ''
      else if (tool.id === 'jsonpath') this.jsonPathData = this.jsonPathExpr = this.jsonPathResult = ''
      else if (tool.id === 'jsonFlatten') this.jsonFlattenInput = this.jsonFlattenOutput = ''
      else if (tool.id === 'jsonPaths') this.jsonPathsInput = this.jsonPathsOutput = ''
      else if (tool.id === 'jsonToXml') this.jsonToXmlInput = this.jsonToXmlOutput = ''
      else if (tool.id === 'xmlToJson') this.xmlToJsonInput = this.xmlToJsonOutput = ''
      else if (tool.id === 'jsonToYaml') this.jsonToYamlInput = this.jsonToYamlOutput = ''
      else if (tool.id === 'yamlToJson') this.yamlToJsonInput = this.yamlToJsonOutput = ''
      else if (tool.id === 'barcode') this.barcodeText = this.barcodeImage = ''
      else if (tool.id === 'qrcode') this.qrcodeText = this.qrcodeImage = ''
      else if (tool.id === 'qrcodeDecode') this.qrcodeDecodedText = ''
      else if (tool.id === 'timestampConv') this.initTimestampDate()
      else if (tool.id === 'baseConvert') this.baseNumber = this.baseResult = ''
      else if (tool.id === 'unicodeConv') this.unicodeInput = this.unicodeOutput = ''
      else if (tool.id === 'ascii') this.asciiInput = this.asciiOutput = ''
      else if (tool.id === 'colorConv') this.colorHex = '#409EFF', this.colorRgb = 'rgb(64,158,255)'
      else if (tool.id === 'urlEncode') this.urlInput = this.urlOutput = ''
      else if (tool.id === 'jwt') this.jwtToken = this.jwtOutput = ''
      else if (tool.id === 'imageToBase64') this.imageToBase64Result = ''
      else if (tool.id === 'base64ToImage') this.base64ToImageInput = this.base64ToImageSrc = ''
      else if (tool.id === 'base64Encode') this.base64Input = this.base64Output = ''
      else if (tool.id === 'md5Hash' || tool.id === 'sha1Hash' || tool.id === 'sha256Hash' || tool.id === 'sha512Hash') this.hashInput = this.hashOutput = ''
      else if (tool.id === 'hashCompare') this.hashCompare1 = this.hashCompare2 = this.hashCompareResult = ''
      else if (tool.id === 'aesEncrypt') this.aesKey = this.aesPlaintext = this.aesEncrypted = ''
      else if (tool.id === 'aesDecrypt') this.aesKey = this.aesCiphertext = this.aesDecrypted = ''
      else if (tool.id === 'md5Hash' || tool.id === 'sha1Hash' || tool.id === 'sha256Hash' || tool.id === 'sha512Hash') {
        this.hashInput = this.hashOutput = ''
        // 延迟生成哈希值，确保DOM已渲染
        this.$nextTick(() => {
          if (tool.id === 'md5Hash') this.computeMd5()
          else if (tool.id === 'sha1Hash') this.computeSha1()
          else if (tool.id === 'sha256Hash') this.computeSha256()
          else if (tool.id === 'sha512Hash') this.computeSha512()
        })
      }
      else if (tool.id === 'hashCompare') this.hashCompare1 = this.hashCompare2 = this.hashCompareResult = ''
      else if (tool.id === 'passwordStrength') this.password = this.passwordStrengthScore = 0
      else if (tool.id === 'generateSalt') {
        this.salt = ''
        // 延迟生成盐值，确保DOM已渲染
        this.$nextTick(() => {
          this.generateSalt()
        })
      }
      else if (tool.id === 'jsonFormat' || tool.id === 'jsonValidate' || tool.id === 'jsonDiff' || tool.id === 'jsonpath' || 
               tool.id === 'jsonFlatten' || tool.id === 'jsonPaths' || tool.id === 'jsonToXml' || tool.id === 'xmlToJson' || 
               tool.id === 'jsonToYaml' || tool.id === 'yamlToJson') {
        // 为JSON处理功能设置默认示例数据
        const sampleJson = '{"name":"张三","age":25,"address":{"city":"北京","street":"朝阳路"},"hobbies":["篮球","音乐"]}'
        const sampleXml = '<root><person><name>张三</name><age>25</age></person></root>'
        const sampleYaml = 'name: 张三\nage: 25\naddress:\n  city: 北京\n  street: 朝阳路'
        
        if (tool.id === 'jsonFormat' || tool.id === 'jsonValidate') this.jsonInput = sampleJson
        if (tool.id === 'jsonDiff') this.jsonDiffLeft = sampleJson
        if (tool.id === 'jsonpath' || tool.id === 'jsonFlatten' || tool.id === 'jsonPaths') this.jsonPathData = sampleJson
        if (tool.id === 'jsonToXml') this.jsonToXmlInput = sampleJson
        if (tool.id === 'xmlToJson') this.xmlToJsonInput = sampleXml
        if (tool.id === 'jsonToYaml') this.jsonToYamlInput = sampleJson
        if (tool.id === 'yamlToJson') this.yamlToJsonInput = sampleYaml
        
        // 延迟执行相应功能，确保DOM已渲染
        this.$nextTick(() => {
          if (tool.id === 'jsonFormat') this.formatJson()
          else if (tool.id === 'jsonValidate') this.validateJson()
          else if (tool.id === 'jsonpath') this.executeJsonPath()
          else if (tool.id === 'jsonFlatten') this.flattenJson()
          else if (tool.id === 'jsonPaths') this.listJsonPaths()
          else if (tool.id === 'jsonToXml') this.jsonToXml()
          else if (tool.id === 'xmlToJson') this.xmlToJson()
          else if (tool.id === 'jsonToYaml') this.jsonToYaml()
          else if (tool.id === 'yamlToJson') this.yamlToJson()
        })
      }
      else if (tool.id === 'passwordStrength') this.password = '', this.passwordStrengthScore = 0, this.passwordStrengthTips = ''
      else if (tool.id === 'generateSalt') this.salt = ''
      else if (tool.id === 'textDiff') this.textDiffLeft = this.textDiffRight = this.textDiffOutput = ''
      else if (tool.id === 'trimSpaces') this.trimInput = '', this.trimOutput = ''
      else if (tool.id === 'replace') this.replaceInput = this.replaceSearch = this.replaceWith = this.replaceOutput = '', this.replaceGlobal = true, this.replaceRegex = false
      else if (tool.id === 'escape') this.escapeInput = this.escapeOutput = ''
      else if (tool.id === 'formatText') this.formatTextInput = this.formatTextOutput = ''
      else if (tool.id === 'cronGen') this.cronMinute = '*', this.cronHour = '*', this.cronDay = '*', this.cronMonth = '*', this.cronWeek = '*', this.cronExpression = ''
      else if (tool.id === 'cronParse') this.cronParseInput = '', this.cronParseOutput = ''
      else if (tool.id === 'cronNext') this.cronNextInput = '', this.cronBaseTime = null, this.cronNextOutput = ''
      else if (tool.id === 'cronValidate') this.cronValidateInput = '', this.cronValidateOutput = ''
      else if (tool.id === 'randomInt') this.randIntMin = 0, this.randIntMax = 100, this.randomInt = ''
      else if (tool.id === 'randomFloat') this.randFloatMin = 0, this.randFloatMax = 1, this.randFloatDecimals = 2, this.randomFloat = ''
      else if (tool.id === 'randomString') {
        this.randStrLen = 8, this.randStrCharset = 'alnum', this.randomString = ''
        // 延迟生成随机字符串，确保DOM已渲染
        this.$nextTick(() => {
          this.generateRandomString()
        })
      }
      else if (tool.id === 'uuid') {
        this.uuid = ''
        // 延迟生成UUID，确保DOM已渲染
        this.$nextTick(() => {
          this.generateUUID()
        })
      }

      else if (tool.id === 'mac') {
        this.macAddress = ''
        // 延迟生成MAC地址，确保DOM已渲染
        this.$nextTick(() => {
          this.generateMac()
        })
      }
      else if (tool.id === 'ip') {
        this.ipAddress = ''
        // 延迟生成IP地址，确保DOM已渲染
        this.$nextTick(() => {
          this.generateIp()
        })
      }
      else if (tool.id === 'randomDate') {
        this.randDateStart = null, this.randDateEnd = null, this.randomDate = ''
        // 延迟生成随机日期，确保DOM已渲染
        this.$nextTick(() => {
          this.generateRandomDate()
        })
      }
      else if (tool.id === 'randomPassword') {
        this.randPwdLen = 12, this.randPwdChars = ['lower', 'upper', 'digit'], this.randomPassword = ''
        // 延迟生成随机密码，确保DOM已渲染
        this.$nextTick(() => {
          this.generateRandomPassword()
        })
      }
      else if (tool.id === 'randomColor') {
        this.randomColor = ''
        // 延迟生成随机颜色，确保DOM已渲染
        this.$nextTick(() => {
          this.generateRandomColor()
        })
      }
      else if (tool.id === 'randomSequence') {
        this.randSeqLength = 5, this.randSeqType = 'int', this.randomSequence = ''
        // 延迟生成随机序列，确保DOM已渲染
        this.$nextTick(() => {
          this.generateRandomSequence()
        })
      }
      else if (tool.id === 'regexTest') this.regexPattern = '', this.regexText = '', this.regexOutput = ''
      else if (tool.id === 'wordCount') this.statsInput = '', this.stats = { charCount: 0, wordCount: 0, lineCount: 0, byteCount: 0 }
      else if (tool.id === 'caseConvert') this.caseInput = '', this.caseOutput = ''
    },
    copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => ElMessage.success('已复制')).catch(() => ElMessage.error('复制失败'))
    },
    // ================= 测试数据生成（完整实现） =================
    generateIdCard() {
      // 生成随机姓名（每次点击都生成新的）
      const name = this.generateChineseName()
      
      // 生成随机出生日期（每次点击都生成新的）
      const birthYear = Math.floor(Math.random() * 50) + 1970
      const birthMonth = String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')
      const birthDay = String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')
      const birthDate = `${birthYear}-${birthMonth}-${birthDay}`
      
      // 生成随机性别（每次点击都生成新的）
      const gender = Math.random() > 0.5 ? '男' : '女'
      
      // 生成随机地址（每次点击都生成新的）
      const provinceCity = this.generateRandomProvinceCity()
      const detailAddress = this.generateDetailAddress()
      const address = `${provinceCity[0]}${provinceCity[1]}${detailAddress}`
      
      // 生成身份证号（基于生成的出生日期和地址）
      const idNumber = this.generateIdNumberWithBirthAndAddress(birthYear, birthMonth, birthDay, provinceCity)
      const nation = '汉' // 写死为汉族
      
      // 生成有效期（基于出生日期）
      const validFrom = `${parseInt(birthYear) + 16}-${birthMonth}-${birthDay}`
      const validTo = this.generateValidToDate(birthYear, birthMonth, birthDay)
      
      // 回填信息到表单
      this.idcardName = name
      this.idcardBirthDate = birthDate
      this.idcardGender = gender
      this.idcardProvinceCity = provinceCity
      this.idcardDetailAddress = detailAddress
      
      // 保存信息用于复制功能
      this.gender = gender
      this.nation = nation
      this.birthDate = birthDate
      this.validFrom = validFrom
      this.validTo = validTo
      
      // 生成身份证正面 - 真实尺寸 85.6mm × 54mm (约 323px × 204px)
      const frontSvg = `<svg width="323" height="204" viewBox="0 0 323 204" xmlns="http://www.w3.org/2000/svg">
        <!-- 背景 - 真实身份证浅蓝色渐变背景 -->
        <rect width="323" height="204" fill="#e8f4fd"/>
        
        <!-- 个人信息区域 -->
        <text x="20" y="40" font-size="14" font-weight="bold" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">姓名</text>
        <text x="60" y="40" font-size="14" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">${name}</text>
        
        <text x="20" y="65" font-size="14" font-weight="bold" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">性别</text>
        <text x="60" y="65" font-size="14" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">${gender}</text>
        <text x="98" y="65" font-size="14" font-weight="bold" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">民族</text>
        <text x="138" y="65" font-size="14" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">${nation}</text>
        
        <text x="20" y="90" font-size="14" font-weight="bold" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">出生</text>
        <text x="60" y="90" font-size="14" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">${birthDate.replace(/-/g, ' 年 ').replace(/(\d{4}) 年 (\d{2}) 年 (\d{2})/, '$1 年 $2 月 $3 日')}</text>
        
        <text x="20" y="115" font-size="14" font-weight="bold" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">住址</text>
        
        <!-- 地址信息多行显示 -->
        ${this.formatAddressForSVG(address, 60, 115)}
        
        <!-- 身份证号码区域 - 公民身份号码和身份证号在同一行 -->
        <text x="20" y="185" font-size="14" font-weight="bold" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">公民身份号码</text>
        <text x="110" y="185" font-size="16" font-weight="bold" font-family="Arial, sans-serif" letter-spacing="2" fill="#333">${idNumber}</text>
        
        <!-- 人像区域 - 真实头像 -->
        <rect x="230" y="50" width="70" height="100" fill="#f5f5f5" stroke="#999" stroke-width="1"/>
        <!-- 真实头像占位 - 使用渐变圆形头像 -->
        <circle cx="265" cy="100" r="25" fill="url(#avatarGradient)"/>
        <defs>
          <linearGradient id="avatarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#4a90e2;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#357abd;stop-opacity:1" />
          </linearGradient>
        </defs>
        
        <!-- 边框 - 真实身份证边框 -->
        <rect x="5" y="5" width="313" height="194" fill="none" stroke="#ccc" stroke-width="1"/>
        <rect x="0" y="0" width="323" height="204" fill="none" stroke="#999" stroke-width="2"/>
      </svg>`
      
      // 生成身份证反面 - 真实尺寸 85.6mm × 54mm (约 323px × 204px)
      const backSvg = `<svg width="323" height="204" viewBox="0 0 323 204" xmlns="http://www.w3.org/2000/svg">
        <!-- 背景 - 真实身份证浅蓝色渐变背景 -->
        <rect width="323" height="204" fill="#e8f4fd"/>
        
        <!-- 国徽区域 - 向左上角移动 -->
        <rect x="20" y="20" width="60" height="60" fill="#ffcc00" stroke="#cc9900" stroke-width="1"/>
        <text x="50" y="55" font-size="16" font-weight="bold" text-anchor="middle" fill="#000" font-family="SimHei, Microsoft YaHei, sans-serif">国徽</text>
        
        <!-- 中华人民共和国 居民身份证 文字 - 整体向上移动15px，增加上下边距10px -->
        <text x="211.5" y="35" font-size="16" font-weight="bold" text-anchor="middle" fill="#000" font-family="SimHei, Microsoft YaHei, sans-serif" letter-spacing="10">中华人民共和国</text>
        <text x="211.5" y="75" font-size="24" font-weight="bold" text-anchor="middle" fill="#000" font-family="SimHei, Microsoft YaHei, sans-serif" letter-spacing="20">居民身份证</text>
        
        <!-- 签发机关 - 整体右移动25px -->
        <text x="55" y="154" font-size="14" font-weight="bold" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#000" letter-spacing="0.5">签发机关</text>
        <text x="125" y="154" font-size="14" font-weight="bold" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#000" letter-spacing="0.5">${this.idcardProvinceCity ? this.idcardProvinceCity[0] + '公安局' : 'XX市公安局'}</text>
        
        <!-- 有效期限 - 整体右移动25px -->
        <text x="55" y="174" font-size="14" font-weight="bold" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#000" letter-spacing="0.5">有效期限</text>
        <text x="125" y="174" font-size="14" font-weight="bold" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#000" letter-spacing="0.5">${validFrom.replace(/-/g, '.')}-${validTo.replace(/-/g, '.')}</text>
        
        <!-- 边框 - 真实身份证边框 -->
        <rect x="5" y="5" width="313" height="194" fill="none" stroke="#ccc" stroke-width="1"/>
        <rect x="0" y="0" width="323" height="204" fill="none" stroke="#999" stroke-width="2"/>
      </svg>`
      
      // 将SVG转换为PNG格式
      this.convertSvgToPng(frontSvg, 'front')
      this.convertSvgToPng(backSvg, 'back')
    },
    generateDetailedAddress() {
      const provinces = ['北京市', '上海市', '广东省', '江苏省', '浙江省', '四川省', '湖北省', '湖南省', '山东省', '河南省']
      const cities = {
        '北京市': ['东城区', '西城区', '朝阳区', '丰台区', '石景山区', '海淀区'],
        '上海市': ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区'],
        '广东省': ['广州市', '深圳市', '珠海市', '汕头市', '佛山市', '韶关市'],
        '江苏省': ['南京市', '无锡市', '徐州市', '常州市', '苏州市', '南通市'],
        '浙江省': ['杭州市', '宁波市', '温州市', '嘉兴市', '湖州市', '绍兴市'],
        '四川省': ['成都市', '自贡市', '攀枝花市', '泸州市', '德阳市', '绵阳市'],
        '湖北省': ['武汉市', '黄石市', '十堰市', '宜昌市', '襄阳市', '鄂州市'],
        '湖南省': ['长沙市', '株洲市', '湘潭市', '衡阳市', '邵阳市', '岳阳市'],
        '山东省': ['济南市', '青岛市', '淄博市', '枣庄市', '东营市', '烟台市'],
        '河南省': ['郑州市', '开封市', '洛阳市', '平顶山市', '安阳市', '鹤壁市']
      }
      const streets = ['中山路', '解放路', '人民路', '建设路', '和平路', '科技路', '创新路', '发展路', '文化路', '教育路']
      const province = provinces[Math.floor(Math.random() * provinces.length)]
      const city = cities[province][Math.floor(Math.random() * cities[province].length)]
      const street = streets[Math.floor(Math.random() * streets.length)]
      const num = Math.floor(Math.random() * 200) + 1
      const address = `${province}${city}${street}${num}号`
      this.address = address
      return address
    },
    generateNation() {
      const nations = ['汉', '蒙古', '回', '藏', '维吾尔', '苗', '彝', '壮', '布依', '朝鲜', '满', '侗', '瑶', '白', '土家', '哈尼', '哈萨克', '傣', '黎', '傈僳', '佤', '畲', '高山', '拉祜', '水', '东乡', '纳西', '景颇', '柯尔克孜', '土', '达斡尔', '仫佬', '羌', '布朗', '撒拉', '毛南', '仡佬', '锡伯', '阿昌', '普米', '塔吉克', '怒', '乌孜别克', '俄罗斯', '鄂温克', '德昂', '保安', '裕固', '京', '塔塔尔', '独龙', '鄂伦春', '赫哲', '门巴', '珞巴', '基诺']
      return nations[Math.floor(Math.random() * nations.length)]
    },
    generateValidToDate(birthYear, birthMonth, birthDay) {
      const year = parseInt(birthYear)
      
      // 证件起期 = 出生日期 + 16年
      const validFromYear = year + 16
      
      // 计算起期时的年龄 = 起期年份 - 出生年份
      const ageAtValidFrom = validFromYear - year
      
      // 根据起期时的年龄设置正确的有效期
      if (ageAtValidFrom < 16) {
        // 未满16周岁：有效期5年
        return `${validFromYear + 5}-${birthMonth}-${birthDay}`
      } else if (ageAtValidFrom < 26) {
        // 16-25周岁：有效期10年
        return `${validFromYear + 10}-${birthMonth}-${birthDay}`
      } else if (ageAtValidFrom < 46) {
        // 26-45周岁：有效期20年
        return `${validFromYear + 20}-${birthMonth}-${birthDay}`
      } else {
        // 46周岁及以上：有效期为长期
        return '长期'
      }
    },
    generateRandomProvinceCity() {
      // 随机选择一个省份和城市
      const provinces = Object.keys(this.addressCodeMap)
      const randomProvince = provinces[Math.floor(Math.random() * provinces.length)]
      const cities = Object.keys(this.addressCodeMap[randomProvince])
      const randomCity = cities[Math.floor(Math.random() * cities.length)]
      return [randomProvince, randomCity]
    },
    generateDetailAddress() {
      // 生成随机详细地址
      const streets = ['朝阳门内大街', '建国门外大街', '复兴门外大街', '西直门外大街', '东直门外大街', '德胜门外大街', '安定门外大街', '广渠门外大街', '永定门外大街', '阜成门外大街']
      const numbers = ['1号', '2号', '3号', '5号', '7号', '9号', '10号', '12号', '15号', '20号']
      const randomStreet = streets[Math.floor(Math.random() * streets.length)]
      const randomNumber = numbers[Math.floor(Math.random() * numbers.length)]
      return randomStreet + randomNumber
    },
    copyIdCardImage(type) {
      const imageUrl = type === 'front' ? this.idcardFrontImage : this.idcardBackImage
      if (!imageUrl) {
        ElMessage.error('请先生成身份证图片')
        return
      }
      
      // 将图片转换为Blob
      fetch(imageUrl)
        .then(response => response.blob())
        .then(blob => {
          // 复制图片到剪贴板
          const clipboardItem = new ClipboardItem({ 'image/png': blob })
          navigator.clipboard.write([clipboardItem]).then(() => {
            ElMessage.success(`已复制${type === 'front' ? '正面' : '反面'}图片`)
          }).catch(() => {
            ElMessage.error('复制图片失败，请尝试下载')
          })
        })
        .catch(() => {
          ElMessage.error('复制图片失败')
        })
    },
    downloadIdCard(type) {
      const imageUrl = type === 'front' ? this.idcardFrontImage : this.idcardBackImage
      if (!imageUrl) {
        ElMessage.error('请先生成身份证图片')
        return
      }
      
      const link = document.createElement('a')
      link.href = imageUrl
      link.download = `身份证${type === 'front' ? '正面' : '反面'}_${this.chineseName || '未知'}.svg`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      ElMessage.success(`已下载${type === 'front' ? '正面' : '反面'}图片`)
    },
    downloadBothIdCards() {
      if (!this.idcardFrontImage || !this.idcardBackImage) {
        ElMessage.error('请先生成身份证正反面图片')
        return
      }
      
      // 获取实际姓名，如果没有输入则使用随机生成的姓名
      const actualName = this.idcardName || this.chineseName || '未知'
      
      // 下载正面
      const frontLink = document.createElement('a')
      frontLink.href = this.idcardFrontImage
      frontLink.download = `身份证正面_${actualName}.png`
      document.body.appendChild(frontLink)
      frontLink.click()
      document.body.removeChild(frontLink)
      
      // 下载反面
      setTimeout(() => {
        const backLink = document.createElement('a')
        backLink.href = this.idcardBackImage
        backLink.download = `身份证反面_${actualName}.png`
        document.body.appendChild(backLink)
        backLink.click()
        document.body.removeChild(backLink)
        ElMessage.success('已下载身份证正反面PNG图片')
      }, 100)
    },
    convertSvgToPng(svgString, type) {
      // 创建SVG Blob
      const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' })
      const svgUrl = URL.createObjectURL(svgBlob)
      
      // 创建Image对象
      const img = new Image()
      img.onload = () => {
        // 创建Canvas
        const canvas = document.createElement('canvas')
        canvas.width = 323 // 真实身份证宽度
        canvas.height = 204 // 真实身份证高度
        const ctx = canvas.getContext('2d')
        
        // 绘制白色背景
        ctx.fillStyle = '#f0f0f0'
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        
        // 绘制SVG到Canvas
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
        
        // 转换为PNG
        const pngUrl = canvas.toDataURL('image/png')
        
        // 保存到对应的变量
        if (type === 'front') {
          this.idcardFrontImage = pngUrl
        } else {
          this.idcardBackImage = pngUrl
        }
        
        // 清理URL
        URL.revokeObjectURL(svgUrl)
      }
      
      img.src = svgUrl
    },
    generateBankCard() {
      const prefixes = ['62', '60', '62', '62', '62', '62', '62', '62', '62', '62']
      const prefix = prefixes[Math.floor(Math.random() * prefixes.length)]
      const card = prefix + Math.random().toString().slice(2, 18)
      this.bankCard = card.padEnd(19, '0')
    },
    generateIdNumber() {
      let idNumber = ''
      
      switch (this.idType) {
        case 'idcard':
          // 身份证号码生成
          const area = '110101'
          const year = Math.floor(Math.random() * 50) + 1970
          const month = String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')
          const day = String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')
          const birth = `${year}${month}${day}`
          const seq = Math.floor(Math.random() * 999).toString().padStart(3, '0')
          let id = area + birth + seq
          const coeff = [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]
          const check = ['1','0','X','9','8','7','6','5','4','3','2']
          let sum = 0
          for (let i = 0; i < 17; i++) sum += parseInt(id[i]) * coeff[i]
          const checkDigit = check[sum % 11]
          idNumber = id + checkDigit
          break
          
        case 'passport':
          // 护照号码生成（E开头 + 8位数字）
          const passportPrefix = 'E'
          const passportNumber = Math.floor(Math.random() * 100000000).toString().padStart(8, '0')
          idNumber = passportPrefix + passportNumber
          break
          
        case 'military':
          // 军人证号码生成（军 + 8位数字）
          const militaryPrefix = '军'
          const militaryNumber = Math.floor(Math.random() * 100000000).toString().padStart(8, '0')
          idNumber = militaryPrefix + militaryNumber
          break
          
        case 'hkmt':
          // 港澳台居民居住证生成（18位格式：810000199109140026）
          // 前6位：港澳台地区代码（81-83）
          const hkmtArea = ['81', '82', '83'][Math.floor(Math.random() * 3)] + '0000'
          // 出生年月日（8位）
          const hkmtBirth = this.generateRandomBirthDate()
          // 顺序号（3位）
          const hkmtSeq = Math.floor(Math.random() * 999).toString().padStart(3, '0')
          // 校验位（1位）
          const hkmtBase = hkmtArea + hkmtBirth + hkmtSeq
          const hkmtCoeff = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
          let hkmtSum = 0
          for (let i = 0; i < 17; i++) hkmtSum += parseInt(hkmtBase[i]) * hkmtCoeff[i]
          const hkmtCheck = ['1','0','X','9','8','7','6','5','4','3','2'][hkmtSum % 11]
          idNumber = hkmtBase + hkmtCheck
          break
          
        case 'foreigner':
          // 外国人永久居住证生成（18位格式：932682201601010019）
          // 前6位：外国人永久居住证标识码（93开头）
          const foreignerArea = '93' + Math.floor(Math.random() * 10000).toString().padStart(4, '0')
          // 出生年月日（8位）
          const foreignerBirth = this.generateRandomBirthDate()
          // 顺序号（3位）
          const foreignerSeq = Math.floor(Math.random() * 999).toString().padStart(3, '0')
          // 校验位（1位）
          const foreignerBase = foreignerArea + foreignerBirth + foreignerSeq
          const foreignerCoeff = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
          let foreignerSum = 0
          for (let i = 0; i < 17; i++) foreignerSum += parseInt(foreignerBase[i]) * foreignerCoeff[i]
          const foreignerCheck = ['1','0','X','9','8','7','6','5','4','3','2'][foreignerSum % 11]
          idNumber = foreignerBase + foreignerCheck
          break
          
        default:
          idNumber = '未知证件类型'
      }
      
      this.idNumber = idNumber
      return idNumber
    },
    getGenerateButtonText() {
      switch (this.idType) {
        case 'idcard': return '生成随机身份证号'
        case 'passport': return '生成随机护照号'
        case 'military': return '生成随机军人证号'
        case 'hkmt': return '生成随机港澳台居民居住证'
        case 'foreigner': return '生成随机外国人永久居住证'
        default: return '生成随机证件号'
      }
    },
    getCopyButtonText() {
      switch (this.idType) {
        case 'idcard': return '复制身份证号'
        case 'passport': return '复制护照号'
        case 'military': return '复制军人证号'
        case 'hkmt': return '复制港澳台居民居住证'
        case 'foreigner': return '复制外国人永久居住证'
        default: return '复制证件号'
      }
    },
    generateRandomBirthDate() {
      // 生成随机出生日期（格式：YYYYMMDD）
      const year = Math.floor(Math.random() * 50) + 1950 // 1950-1999年
      const month = Math.floor(Math.random() * 12) + 1
      const day = Math.floor(Math.random() * 28) + 1 // 简单处理，避免2月30日等问题
      return `${year}${month.toString().padStart(2, '0')}${day.toString().padStart(2, '0')}`
    },
    generateIdNumberWithBirthAndAddress(year, month, day, provinceCity) {
      // 根据选择的地址获取区域码
      let area = '110101' // 默认北京市东城区
      if (provinceCity && provinceCity.length >= 2) {
        const [province, city] = provinceCity
        if (this.addressCodeMap[province] && this.addressCodeMap[province][city]) {
          area = this.addressCodeMap[province][city]
        }
      }
      
      const birth = `${year}${month}${day}`
      const seq = Math.floor(Math.random() * 999).toString().padStart(3, '0')
      let id = area + birth + seq
      const coeff = [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]
      const check = ['1','0','X','9','8','7','6','5','4','3','2']
      let sum = 0
      for (let i = 0; i < 17; i++) sum += parseInt(id[i]) * coeff[i]
      const checkDigit = check[sum % 11]
      const idNumber = id + checkDigit
      this.idNumber = idNumber
      return idNumber
    },
    updateIdCardInfo() {
      // 当用户修改出生日期、性别或地址时，自动更新身份证信息
      if (this.idcardBirthDate || this.idcardGender || (this.idcardAddress && this.idcardAddress.length >= 2)) {
        // 如果有足够的信息，自动生成身份证
        this.generateIdCard()
      }
    },
    
    formatAddressForDisplay(address) {
      if (!address) return ''
      
      // 如果地址长度超过12个字符，进行换行处理
      if (address.length > 12) {
        // 尝试在合适的字符位置换行
        const breakIndex = this.findBreakPoint(address)
        if (breakIndex > 0) {
          const firstLine = address.substring(0, breakIndex)
          const secondLine = address.substring(breakIndex)
          return `${firstLine}\n${secondLine}`
        }
      }
      
      return address
    },
    
    findBreakPoint(address) {
      // 优先在逗号、顿号、空格处换行
      const preferredBreaks = ['，', '、', ' ', ',']
      
      // 从第8个字符开始查找合适的换行点（减少2个字符）
      for (let i = 8; i < Math.min(13, address.length); i++) {
        if (preferredBreaks.includes(address[i])) {
          return i + 1
        }
      }
      
      // 如果没有找到合适的标点，在10个字符处强制换行（减少2个字符）
      return 10
    },
    
    formatAddressForSVG(address, x, y) {
      if (!address) return ''
      
      // 如果地址长度超过10个字符，进行换行处理（减少2个字符）
      if (address.length > 10) {
        const breakIndex = this.findBreakPoint(address)
        if (breakIndex > 0) {
          const firstLine = address.substring(0, breakIndex)
          const secondLine = address.substring(breakIndex)
          return `
            <text x="${x}" y="${y}" font-size="14" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">${firstLine}</text>
            <text x="${x}" y="${parseInt(y) + 20}" font-size="14" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">${secondLine}</text>
          `
        }
      }
      
      return `<text x="${x}" y="${y}" font-size="14" font-family="SimHei, Microsoft YaHei, sans-serif" fill="#333">${address}</text>`
    },
    generateChineseName() {
      const surnames = ['李', '王', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴']
      const names = ['明', '伟', '芳', '强', '丽', '军', '华', '勇', '敏', '静', '宇', '欣', '杰', '娜', '鹏']
      const surname = surnames[Math.floor(Math.random() * surnames.length)]
      const name = names[Math.floor(Math.random() * names.length)] + (Math.random() > 0.5 ? names[Math.floor(Math.random() * names.length)] : '')
      const chineseName = surname + name
      this.chineseName = chineseName
      return chineseName
    },
    generateMobile() {
      const prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139', '150', '151', '152', '153', '155', '156', '157', '158', '159', '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
      const prefix = prefixes[Math.floor(Math.random() * prefixes.length)]
      const suffix = Math.floor(Math.random() * 100000000).toString().padStart(8, '0').slice(0,8)
      this.mobile = prefix + suffix
    },
    generateEmail() {
      const domains = ['qq.com', '163.com', 'gmail.com', 'outlook.com', 'example.com']
      const name = Math.random().toString(36).substring(2, 8)
      const domain = domains[Math.floor(Math.random() * domains.length)]
      this.email = name + '@' + domain
    },
    generateAddress() {
      const provinces = ['北京市', '上海市', '广东省', '江苏省', '浙江省', '四川省', '湖北省', '湖南省']
      const cities = ['朝阳区', '浦东新区', '广州市', '南京市', '杭州市', '成都市', '武汉市', '长沙市']
      const streets = ['中山路', '解放路', '人民路', '建设路', '和平路', '科技路', '创新路', '发展路']
      const province = provinces[Math.floor(Math.random() * provinces.length)]
      const city = cities[Math.floor(Math.random() * cities.length)]
      const street = streets[Math.floor(Math.random() * streets.length)]
      const num = Math.floor(Math.random() * 200) + 1
      this.address = `${province}${city}${street}${num}号`
    },
    generateCompany() {
      const prefixes = ['北京', '上海', '深圳', '广州', '杭州', '成都', '武汉', '西安']
      const names = ['科技', '信息', '网络', '软件', '数据', '智能', '云', '数字']
      const suffixes = ['有限公司', '股份有限公司', '集团', '工作室', '科技公司']
      const prefix = prefixes[Math.floor(Math.random() * prefixes.length)]
      const name = names[Math.floor(Math.random() * names.length)]
      const suffix = suffixes[Math.floor(Math.random() * suffixes.length)]
      this.company = prefix + name + suffix
    },
    generateHkId() {
      const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
      const first = letters[Math.floor(Math.random() * 26)]
      const second = letters[Math.floor(Math.random() * 26)]
      const digits = Math.floor(Math.random() * 1000000).toString().padStart(6, '0')
      const check = Math.floor(Math.random() * 10)
      this.hkId = first + second + digits + '(' + check + ')'
    },
    generateLicense() {
      const prefix = '91310115'
      const suffix = Math.floor(Math.random() * 10000000000).toString().padStart(10, '0')
      this.license = prefix + suffix
    },
    generateCoords() {
      const lat = (Math.random() * 180 - 90).toFixed(6)
      const lng = (Math.random() * 360 - 180).toFixed(6)
      this.coords = `${lat}, ${lng}`
    },
    generateProfile() {
      this.generateChineseName()
      this.generateMobile()
      this.generateEmail()
      this.generateAddress()
      this.generateIdNumber()
      this.profile = `姓名：${this.chineseName}\n手机：${this.mobile}\n邮箱：${this.email}\n地址：${this.address}\n身份证：${this.idNumber}`
    },
    // ================= JSON 处理 =================
    formatJson() {
      try {
        const obj = JSON.parse(this.jsonInput)
        this.jsonOutput = JSON.stringify(obj, null, 2)
        ElMessage.success('格式化成功')
      } catch (e) {
        ElMessage.error('JSON 格式错误: ' + e.message)
        this.jsonOutput = ''
      }
    },
    compressJson() {
      try {
        const obj = JSON.parse(this.jsonInput)
        this.jsonOutput = JSON.stringify(obj)
        ElMessage.success('压缩成功')
      } catch (e) {
        ElMessage.error('JSON 格式错误')
        this.jsonOutput = ''
      }
    },
    clearJson() {
      this.jsonInput = ''
      this.jsonOutput = ''
    },
    validateJson() {
      try {
        JSON.parse(this.jsonValidateInput)
        this.jsonValidateOutput = '✓ 有效的 JSON'
        ElMessage.success('JSON 有效')
      } catch (e) {
        this.jsonValidateOutput = '✗ 无效的 JSON: ' + e.message
        ElMessage.error('JSON 无效')
      }
    },
    compareJson() {
      try {
        const left = JSON.parse(this.jsonDiffLeft)
        const right = JSON.parse(this.jsonDiffRight)
        const diff = this.deepDiff(left, right)
        this.jsonDiffOutput = diff || '两个 JSON 完全相同'
      } catch (e) {
        ElMessage.error('JSON 解析失败')
        this.jsonDiffOutput = '解析失败：' + e.message
      }
    },
    deepDiff(obj1, obj2, path = '') {
      const changes = []
      const allKeys = new Set([...Object.keys(obj1), ...Object.keys(obj2)])
      for (let key of allKeys) {
        const newPath = path ? `${path}.${key}` : key
        if (!(key in obj1)) changes.push(`${newPath}: 新增 -> ${JSON.stringify(obj2[key])}`)
        else if (!(key in obj2)) changes.push(`${newPath}: 删除 -> ${JSON.stringify(obj1[key])}`)
        else if (typeof obj1[key] === 'object' && obj1[key] !== null && typeof obj2[key] === 'object' && obj2[key] !== null) {
          changes.push(...this.deepDiff(obj1[key], obj2[key], newPath))
        } else if (obj1[key] !== obj2[key]) {
          changes.push(`${newPath}: ${obj1[key]} -> ${obj2[key]}`)
        }
      }
      return changes.join('\n')
    },
    executeJsonPath() {
      try {
        const data = JSON.parse(this.jsonPathData)
        const path = this.jsonPathExpr.trim()
        if (!path) return
        let parts = path.split('.')
        if (parts[0] === '$') parts = parts.slice(1)
        let result = data
        for (let part of parts) {
          if (part.includes('[*]')) {
            const key = part.replace('[*]', '')
            if (Array.isArray(result[key])) {
              result = result[key]
            } else {
              result = undefined
              break
            }
          } else {
            result = result[part]
          }
          if (result === undefined) break
        }
        this.jsonPathResult = JSON.stringify(result, null, 2)
      } catch (e) {
        ElMessage.error('JSONPath 执行失败: ' + e.message)
      }
    },
    flattenJson() {
      try {
        const obj = JSON.parse(this.jsonFlattenInput)
        const result = {}
        const flatten = (obj, prefix = '') => {
          for (let key in obj) {
            const newKey = prefix ? `${prefix}.${key}` : key
            if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
              flatten(obj[key], newKey)
            } else {
              result[newKey] = obj[key]
            }
          }
        }
        flatten(obj)
        this.jsonFlattenOutput = JSON.stringify(result, null, 2)
      } catch (e) {
        ElMessage.error('JSON 解析失败')
      }
    },
    listJsonPaths() {
      try {
        const obj = JSON.parse(this.jsonPathsInput)
        const paths = []
        const collect = (obj, prefix = '') => {
          for (let key in obj) {
            const newKey = prefix ? `${prefix}.${key}` : key
            paths.push(newKey)
            if (typeof obj[key] === 'object' && obj[key] !== null) {
              collect(obj[key], newKey)
            }
          }
        }
        collect(obj)
        this.jsonPathsOutput = paths.join('\n')
      } catch (e) {
        ElMessage.error('JSON 解析失败')
      }
    },
    jsonToXml() {
      try {
        const obj = JSON.parse(this.jsonToXmlInput)
        let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<root>\n'
        const convert = (obj, indent = 2) => {
          let str = ''
          for (let key in obj) {
            if (typeof obj[key] === 'object' && obj[key] !== null) {
              str += `${' '.repeat(indent)}<${key}>\n${convert(obj[key], indent + 2)}${' '.repeat(indent)}</${key}>\n`
            } else {
              str += `${' '.repeat(indent)}<${key}>${obj[key]}</${key}>\n`
            }
          }
          return str
        }
        xml += convert(obj, 2) + '</root>'
        this.jsonToXmlOutput = xml
      } catch (e) {
        ElMessage.error('转换失败: ' + e.message)
      }
    },
    xmlToJson() {
      try {
        const xml = this.xmlToJsonInput
        const result = {}
        const regex = /<(\w+)>(.*?)<\/\1>/g
        let match
        while ((match = regex.exec(xml)) !== null) {
          result[match[1]] = match[2]
        }
        this.xmlToJsonOutput = JSON.stringify(result, null, 2)
      } catch (e) {
        ElMessage.error('转换失败: ' + e.message)
      }
    },
    jsonToYaml() {
      try {
        const obj = JSON.parse(this.jsonToYamlInput)
        const yamlStr = yaml.dump(obj)
        this.jsonToYamlOutput = yamlStr
      } catch (e) {
        ElMessage.error('转换失败: ' + e.message)
      }
    },
    yamlToJson() {
      try {
        const obj = yaml.load(this.yamlToJsonInput)
        this.yamlToJsonOutput = JSON.stringify(obj, null, 2)
      } catch (e) {
        ElMessage.error('转换失败: ' + e.message)
      }
    },
    // ================= 编码转换 =================
    generateBarcode() {
      if (!this.barcodeText) {
        ElMessage.warning('请输入内容')
        return
      }
      
      // 确保DOM更新完成后再获取canvas引用
      this.$nextTick(() => {
        const canvas = this.$refs.barcodeCanvas
        if (!canvas) {
          console.error('Canvas元素未找到')
          ElMessage.error('生成条形码失败：Canvas元素未找到')
          return
        }
        
        try {
          // 清除canvas内容
          const ctx = canvas.getContext('2d')
          ctx.clearRect(0, 0, canvas.width, canvas.height)
          
          // 生成条形码
          JsBarcode(canvas, this.barcodeText, { 
            format: 'CODE128', 
            width: 2, 
            height: 100,
            displayValue: true,
            text: this.barcodeText
          })
          
          // 转换为图片URL
          this.barcodeImage = canvas.toDataURL('image/png')
          ElMessage.success('条形码生成成功')
        } catch (error) {
          console.error('生成条形码失败:', error)
          ElMessage.error('生成条形码失败：' + error.message)
        }
      })
    },
    copyBarcodeImage() {
      if (!this.barcodeImage) {
        ElMessage.error('请先生成条形码图片')
        return
      }
      
      // 将图片转换为Blob
      fetch(this.barcodeImage)
        .then(response => response.blob())
        .then(blob => {
          // 复制图片到剪贴板
          const clipboardItem = new ClipboardItem({ 'image/png': blob })
          navigator.clipboard.write([clipboardItem]).then(() => {
            ElMessage.success('已复制条形码图片')
          }).catch(() => {
            ElMessage.error('复制图片失败，请尝试下载')
          })
        })
        .catch(() => {
          ElMessage.error('复制图片失败')
        })
    },
    downloadBarcodeImage() {
      if (!this.barcodeImage) {
        ElMessage.error('请先生成条形码图片')
        return
      }
      
      // 创建下载链接
      const link = document.createElement('a')
      link.href = this.barcodeImage
      link.download = `条形码_${this.barcodeText.substring(0, 10)}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      ElMessage.success('已下载条形码图片')
    },
    generateQRCode() {
      if (!this.qrcodeText) {
        ElMessage.warning('请输入内容')
        return
      }
      QRCode.toDataURL(this.qrcodeText, { width: 200, margin: 2 }, (err, url) => {
        if (!err) this.qrcodeImage = url
        else ElMessage.error('生成失败')
      })
    },
    copyQRCodeImage() {
      if (!this.qrcodeImage) {
        ElMessage.error('请先生成二维码图片')
        return
      }
      
      // 将图片转换为Blob
      fetch(this.qrcodeImage)
        .then(response => response.blob())
        .then(blob => {
          // 复制图片到剪贴板
          const clipboardItem = new ClipboardItem({ 'image/png': blob })
          navigator.clipboard.write([clipboardItem]).then(() => {
            ElMessage.success('已复制二维码图片')
          }).catch(() => {
            ElMessage.error('复制图片失败，请尝试下载')
          })
        })
        .catch(() => {
          ElMessage.error('复制图片失败')
        })
    },
    downloadQRCodeImage() {
      if (!this.qrcodeImage) {
        ElMessage.error('请先生成二维码图片')
        return
      }
      
      // 创建下载链接
      const link = document.createElement('a')
      link.href = this.qrcodeImage
      link.download = `二维码_${this.qrcodeText.substring(0, 10)}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      ElMessage.success('已下载二维码图片')
    },
    onQRCodeUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      const reader = new FileReader()
      reader.onload = (e) => {
        this.qrcodeImageForDecode = e.target.result
      }
      reader.readAsDataURL(file)
    },
    decodeQRCode() {
      if (!this.qrcodeImageForDecode) {
        ElMessage.warning('请先上传图片')
        return
      }
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        canvas.width = img.width
        canvas.height = img.height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0)
        const imageData = ctx.getImageData(0, 0, img.width, img.height)
        const code = jsQR(imageData.data, img.width, img.height)
        if (code) this.qrcodeDecodedText = code.data
        else this.qrcodeDecodedText = '未识别到二维码'
      }
      img.src = this.qrcodeImageForDecode
    },
    initTimestampDate() {
      const date = new Date()
      this.timestampDate = this.formatDateToString(date)
      this.timestampSeconds = Math.floor(date.getTime() / 1000)
    },
    formatDateToString(date) {
      return date.toISOString().slice(0, 19).replace('T', ' ')
    },
    setCurrentTimestamp() {
      this.timestampSeconds = Math.floor(Date.now() / 1000)
      this.timestampToDate()
    },
    timestampToDate() {
      const date = new Date(this.timestampSeconds * 1000)
      this.timestampDate = this.formatDateToString(date)
      this.timestampOutput = `日期时间: ${this.timestampDate}`
    },
    dateToTimestamp() {
      const date = new Date(this.timestampDate)
      this.timestampSeconds = Math.floor(date.getTime() / 1000)
      this.timestampOutput = `时间戳: ${this.timestampSeconds}`
    },
    convertBase() {
      if (!this.baseNumber) return
      try {
        const decimal = parseInt(this.baseNumber, this.baseFrom)
        this.baseResult = decimal.toString(this.baseTo)
      } catch (e) {
        ElMessage.error('转换失败')
      }
    },
    encodeUnicode() {
      if (!this.unicodeInput) return
      let result = ''
      for (let i = 0; i < this.unicodeInput.length; i++) {
        const code = this.unicodeInput.charCodeAt(i).toString(16)
        result += '\\u' + code.padStart(4, '0')
      }
      this.unicodeOutput = result
    },
    decodeUnicode() {
      if (!this.unicodeInput) return
      try {
        this.unicodeOutput = JSON.parse('"' + this.unicodeInput.replace(/\\u([0-9a-fA-F]{4})/g, (m, cp) => String.fromCharCode(parseInt(cp, 16))) + '"')
      } catch (e) {
        ElMessage.error('解码失败')
      }
    },
    textToAscii() {
      if (!this.asciiInput) return
      const arr = []
      for (let i = 0; i < this.asciiInput.length; i++) {
        arr.push(this.asciiInput.charCodeAt(i))
      }
      this.asciiOutput = arr.join(' ')
    },
    asciiToText() {
      if (!this.asciiInput) return
      const arr = this.asciiInput.split(' ').map(Number)
      let str = ''
      for (let code of arr) {
        str += String.fromCharCode(code)
      }
      this.asciiOutput = str
    },
    hexToRgb() {
      const hex = this.colorHex
      if (/^#[0-9A-F]{6}$/i.test(hex)) {
        const r = parseInt(hex.slice(1,3), 16)
        const g = parseInt(hex.slice(3,5), 16)
        const b = parseInt(hex.slice(5,7), 16)
        this.colorRgb = `rgb(${r}, ${g}, ${b})`
      }
    },
    rgbToHex() {
      const match = this.colorRgb.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/i)
      if (match) {
        const r = parseInt(match[1]), g = parseInt(match[2]), b = parseInt(match[3])
        this.colorHex = '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)
      }
    },
    encodeUrl() {
      if (!this.urlInput) return
      this.urlOutput = encodeURIComponent(this.urlInput)
    },
    decodeUrl() {
      if (!this.urlInput) return
      try {
        this.urlOutput = decodeURIComponent(this.urlInput)
      } catch (e) {
        ElMessage.error('解码失败')
      }
    },
    parseJwt() {
      if (!this.jwtToken) return
      try {
        const parts = this.jwtToken.split('.')
        if (parts.length !== 3) throw new Error('无效 JWT')
        const header = JSON.parse(atob(parts[0]))
        const payload = JSON.parse(atob(parts[1]))
        this.jwtOutput = JSON.stringify({ header, payload }, null, 2)
      } catch (e) {
        this.jwtOutput = '解析失败: ' + e.message
      }
    },
    onImageToBase64Upload(event) {
      const file = event.target.files[0]
      if (!file) return
      const reader = new FileReader()
      reader.onload = (e) => {
        this.imageToBase64Result = e.target.result
      }
      reader.readAsDataURL(file)
    },
    triggerImageToBase64Upload() {
      // 创建隐藏的文件输入元素
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = 'image/*'
      input.style.display = 'none'
      
      // 监听文件选择事件
      input.addEventListener('change', (event) => {
        this.onImageToBase64Upload(event)
        // 清理DOM
        document.body.removeChild(input)
      })
      
      // 添加到DOM并触发点击
      document.body.appendChild(input)
      input.click()
    },
    base64ToImage() {
      if (!this.base64ToImageInput) return
      this.base64ToImageSrc = this.base64ToImageInput
    },
    downloadBase64Image() {
      if (!this.base64ToImageSrc) {
        ElMessage.error('请先生成图片')
        return
      }
      
      try {
        // 创建下载链接
        const link = document.createElement('a')
        link.href = this.base64ToImageSrc
        
        // 尝试从Base64数据中提取文件名，如果没有则使用默认名称
        let filename = 'converted_image.png'
        
        // 检查Base64数据是否包含图片格式信息
        if (this.base64ToImageSrc.includes('data:image/')) {
          const formatMatch = this.base64ToImageSrc.match(/data:image\/([^;]+)/)
          if (formatMatch && formatMatch[1]) {
            filename = `converted_image.${formatMatch[1]}`
          }
        }
        
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        ElMessage.success('图片下载成功')
      } catch (error) {
        console.error('下载图片失败:', error)
        ElMessage.error('下载图片失败')
      }
    },
    encodeBase64() {
      if (!this.base64Input) return
      this.base64Output = btoa(unescape(encodeURIComponent(this.base64Input)))
    },
    decodeBase64() {
      if (!this.base64Input) return
      try {
        this.base64Output = decodeURIComponent(escape(atob(this.base64Input)))
      } catch (e) {
        ElMessage.error('解码失败，请检查是否为有效的 Base64 字符串')
      }
    },
    // ================= 加密哈希 =================
    computeMd5() {
      if (!this.hashInput) return
      this.hashOutput = CryptoJS.MD5(this.hashInput).toString()
    },
    computeSha1() {
      if (!this.hashInput) return
      this.hashOutput = CryptoJS.SHA1(this.hashInput).toString()
    },
    computeSha256() {
      if (!this.hashInput) return
      this.hashOutput = CryptoJS.SHA256(this.hashInput).toString()
    },
    computeSha512() {
      if (!this.hashInput) return
      this.hashOutput = CryptoJS.SHA512(this.hashInput).toString()
    },
    compareHash() {
      if (this.hashCompare1 === this.hashCompare2) {
        this.hashCompareResult = '哈希值相同'
      } else {
        this.hashCompareResult = '哈希值不同'
      }
    },
    async aesEncrypt() {
      if (!this.aesKey || !this.aesPlaintext) {
        ElMessage.warning('请输入密钥和明文')
        return
      }
      const key = CryptoJS.enc.Utf8.parse(this.aesKey)
      const iv = CryptoJS.lib.WordArray.random(16)
      const encrypted = CryptoJS.AES.encrypt(this.aesPlaintext, key, { iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 })
      const combined = iv.concat(encrypted.ciphertext)
      this.aesEncrypted = combined.toString(CryptoJS.enc.Base64)
      ElMessage.success('加密成功')
    },
    async aesDecrypt() {
      if (!this.aesKey || !this.aesCiphertext) {
        ElMessage.warning('请输入密钥和密文')
        return
      }
      const combined = CryptoJS.enc.Base64.parse(this.aesCiphertext)
      const iv = CryptoJS.lib.WordArray.create(combined.words.slice(0, 4), 16)
      const ciphertext = CryptoJS.lib.WordArray.create(combined.words.slice(4), combined.sigBytes - 16)
      const decrypted = CryptoJS.AES.decrypt({ ciphertext, salt: null }, CryptoJS.enc.Utf8.parse(this.aesKey), { iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 })
      this.aesDecrypted = decrypted.toString(CryptoJS.enc.Utf8)
      if (!this.aesDecrypted) {
        ElMessage.error('解密失败，请检查密钥和密文')
      } else {
        ElMessage.success('解密成功')
      }
    },
    checkPasswordStrength() {
      const pwd = this.password
      let score = 0
      if (pwd.length >= 8) score += 25
      if (/[a-z]/.test(pwd)) score += 25
      if (/[A-Z]/.test(pwd)) score += 25
      if (/[0-9]/.test(pwd)) score += 15
      if (/[^a-zA-Z0-9]/.test(pwd)) score += 10
      this.passwordStrengthScore = score
      if (score < 40) {
        this.passwordStrengthTips = '弱'
        this.passwordStrengthColor = '#F56C6C'
      } else if (score < 70) {
        this.passwordStrengthTips = '中'
        this.passwordStrengthColor = '#E6A23C'
      } else {
        this.passwordStrengthTips = '强'
        this.passwordStrengthColor = '#67C23A'
      }
    },
    formatStrength(percentage) {
      return this.passwordStrengthTips
    },
    generateSalt() {
      const salt = CryptoJS.lib.WordArray.random(16).toString()
      this.salt = salt
    },
    // ================= 字符串处理 =================
    computeTextDiff() {
      const left = this.textDiffLeft
      const right = this.textDiffRight
      if (left === right) {
        this.textDiffOutput = '两段文本完全相同'
        return
      }
      const linesLeft = left.split('\n')
      const linesRight = right.split('\n')
      const diff = []
      for (let i = 0; i < Math.max(linesLeft.length, linesRight.length); i++) {
        const l = linesLeft[i] || ''
        const r = linesRight[i] || ''
        if (l !== r) {
          diff.push(`行 ${i+1}: [原始] "${l}"  [对比] "${r}"`)
        }
      }
      this.textDiffOutput = diff.join('\n')
    },
    testRegex() {
      if (!this.regexPattern) {
        ElMessage.warning('请输入正则表达式')
        return
      }
      try {
        const regex = new RegExp(this.regexPattern, 'g')
        let match
        const matches = []
        while ((match = regex.exec(this.regexText)) !== null) {
          matches.push(match[0])
        }
        if (matches.length > 0) {
          this.regexOutput = `匹配到 ${matches.length} 个结果:\n${matches.join('\n')}`
        } else {
          this.regexOutput = '没有匹配到任何结果'
        }
      } catch (e) {
        this.regexOutput = '无效的正则表达式: ' + e.message
      }
    },
    trimSpaces() {
      let result = this.trimInput
      if (this.trimType === 'trim') result = result.trim()
      else if (this.trimType === 'all') result = result.replace(/\s/g, '')
      else if (this.trimType === 'extra') result = result.replace(/\s+/g, ' ').trim()
      this.trimOutput = result
    },
    doReplace() {
      let input = this.replaceInput
      let search = this.replaceSearch
      let replace = this.replaceWith
      if (this.replaceRegex) {
        try {
          const regex = new RegExp(search, this.replaceGlobal ? 'g' : '')
          this.replaceOutput = input.replace(regex, replace)
        } catch (e) {
          ElMessage.error('无效的正则表达式')
        }
      } else {
        if (this.replaceGlobal) {
          this.replaceOutput = input.split(search).join(replace)
        } else {
          this.replaceOutput = input.replace(search, replace)
        }
      }
    },
    escapeHtml() {
      const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }
      this.escapeOutput = this.escapeInput.replace(/[&<>"']/g, m => map[m])
    },
    unescapeHtml() {
      const map = { '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'" }
      this.escapeOutput = this.escapeInput.replace(/&amp;|&lt;|&gt;|&quot;|&#39;/g, m => map[m])
    },
    computeStats() {
      const text = this.statsInput
      this.stats.charCount = text.length
      this.stats.wordCount = text.trim() ? text.trim().split(/\s+/).length : 0
      this.stats.lineCount = text.split(/\r\n|\r|\n/).length
      this.stats.byteCount = new Blob([text]).size
    },
    toUpperCase() {
      this.caseOutput = this.caseInput.toUpperCase()
    },
    toLowerCase() {
      this.caseOutput = this.caseInput.toLowerCase()
    },
    toTitleCase() {
      this.caseOutput = this.caseInput.replace(/\b\w/g, l => l.toUpperCase())
    },
    formatText() {
      this.formatTextOutput = this.formatTextInput.replace(/\n\s*\n/g, '\n\n').trim()
    },
    // ================= 定时任务 =================
    buildCron() {
      const cron = `${this.cronMinute} ${this.cronHour} ${this.cronDay} ${this.cronMonth} ${this.cronWeek}`
      this.cronExpression = cron
    },
    parseCron() {
      try {
        const parser = new CronParser(this.cronParseInput)
        const fields = parser.fields
        this.cronParseOutput = `分钟: ${fields.minute}\n小时: ${fields.hour}\n日期: ${fields.dayOfMonth}\n月份: ${fields.month}\n星期: ${fields.dayOfWeek}`
      } catch (e) {
        this.cronParseOutput = '解析失败：' + e.message
      }
    },
    getNextCronTime() {
      try {
        const parser = new CronParser(this.cronNextInput)
        const next = parser.getNextDate(this.cronBaseTime ? new Date(this.cronBaseTime) : new Date())
        this.cronNextOutput = next.toLocaleString()
      } catch (e) {
        this.cronNextOutput = '获取失败：' + e.message
      }
    },
    validateCron() {
      this.cronValidateOutput = CronParser.validate(this.cronValidateInput) ? '✓ 有效的Cron表达式' : '✗ 无效的Cron表达式'
    },
    // ================= 随机数据 =================
    generateRandomInt() {
      const min = Math.ceil(this.randIntMin)
      const max = Math.floor(this.randIntMax)
      this.randomInt = Math.floor(Math.random() * (max - min + 1)) + min
    },
    generateRandomFloat() {
      const min = this.randFloatMin
      const max = this.randFloatMax
      const val = Math.random() * (max - min) + min
      this.randomFloat = val.toFixed(this.randFloatDecimals)
    },
    generateRandomString() {
      let chars = ''
      if (this.randStrCharset === 'alnum') chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
      else if (this.randStrCharset === 'alpha') chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
      else if (this.randStrCharset === 'num') chars = '0123456789'
      else chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()'
      let result = ''
      for (let i = 0; i < this.randStrLen; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length))
      }
      this.randomString = result
    },
    generateUUID() {
      this.uuid = crypto.randomUUID ? crypto.randomUUID() : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
      })
    },
    generateRandomBool() {
      this.randomBool = Math.random() < 0.5 ? 'true' : 'false'
    },
    generateMac() {
      const hex = () => Math.floor(Math.random() * 256).toString(16).padStart(2, '0')
      this.macAddress = Array(6).fill().map(() => hex()).join(':')
    },
    generateIp() {
      this.ipAddress = `${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}`
    },
    generateRandomDate() {
      const start = this.randDateStart ? new Date(this.randDateStart) : new Date(2000, 0, 1)
      const end = this.randDateEnd ? new Date(this.randDateEnd) : new Date()
      const time = start.getTime() + Math.random() * (end.getTime() - start.getTime())
      const date = new Date(time)
      this.randomDate = date.toISOString().slice(0, 10)
    },
    generateRandomPassword() {
      const sets = {
        lower: 'abcdefghijklmnopqrstuvwxyz',
        upper: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        digit: '0123456789',
        special: '!@#$%^&*()_+-=[]{}|;:,.<>?'
      }
      let pool = ''
      this.randPwdChars.forEach(t => pool += sets[t])
      if (!pool) pool = sets.lower
      let pwd = ''
      for (let i = 0; i < this.randPwdLen; i++) {
        pwd += pool.charAt(Math.floor(Math.random() * pool.length))
      }
      this.randomPassword = pwd
    },
    generateRandomColor() {
      this.randomColor = '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')
    },
    generateRandomSequence() {
      const arr = []
      for (let i = 0; i < this.randSeqLength; i++) {
        if (this.randSeqType === 'int') arr.push(Math.floor(Math.random() * 100))
        else if (this.randSeqType === 'float') arr.push(+(Math.random() * 100).toFixed(2))
        else arr.push(Math.random().toString(36).substring(2, 8))
      }
      this.randomSequence = JSON.stringify(arr)
    }
  }
}
</script>

<style scoped>
.test-tools-container {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  display: flex;
  flex-direction: column;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
.elegant-shadow {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.fixed-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  padding: 12px 24px;
  height: 50px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.header-content {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}
.logo-section {
  flex-shrink: 0;
}
.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
}
.logo-circle {
  position: relative;
  width: 50px;
  height: 50px;
}
.logo-icon { width: 100%; height: 100%; }
.logo-hexagon { fill: none; stroke: #6366f1; stroke-width: 4; }
.logo-center { fill: #6366f1; opacity: 0.8; }
.logo-square { fill: rgba(255, 255, 255, 0.9); }
.platform-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.platform-name {
  font-size: 18px;
  font-weight: 800;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
}
.platform-slogan {
  color: rgba(255, 255, 255, 0.7);
  font-size: 11px;
  margin: 0;
}
.search-section {
  flex: 1;
  max-width: 500px;
  margin-left: auto;
}
.search-container {
  width: 100%;
}
.search-input >>> .el-input__wrapper {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 40px;
  padding: 8px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}
.search-input >>> .el-input__wrapper:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.search-input >>> .el-input__inner {
  font-size: 14px;
}
.search-icon {
  font-size: 18px;
  color: #909399;
}
.main-content {
  flex: 1;
  padding: 20px 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}
.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.group-card {
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  background: white;
  overflow: hidden;
}
.group-card >>> .el-card__header {
  padding: 16px 24px;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
}
.card-header {
  padding: 0;
}
.group-title-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.group-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}
.group-indicator {
  width: 4px;
  height: 24px;
  background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 2px;
}
.group-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
}
.group-count {
  background: #f1f5f9;
  border: none;
}
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 20px;
}
.tool-item {
  cursor: pointer;
  transition: transform 0.3s ease;
}
.tool-item:hover {
  transform: translateY(-4px);
}
.tool-card {
  border-radius: 16px;
  border: none;
  height: 100%;
  transition: all 0.3s ease;
}
.tool-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}
.tool-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}
.tool-icon-bg {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s;
}
.tool-card:hover .tool-icon-bg {
  transform: scale(1.05);
}
.tool-info {
  flex: 1;
}
.tool-name {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}
.tool-description {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: white;
  border-radius: 20px;
  border: 2px dashed #e2e8f0;
  margin-top: 24px;
}
.empty-state-content {
  text-align: center;
  padding: 48px;
}
.empty-state-icon {
  font-size: 72px;
  color: #cbd5e1;
  margin-bottom: 24px;
}
.empty-state-title {
  margin: 0 0 12px;
  font-size: 24px;
  font-weight: 700;
}
.empty-state-description {
  margin: 0 0 24px;
  color: #64748b;
}
.empty-state-btn {
  padding: 12px 32px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  font-weight: 500;
}
.elegant-dialog >>> .el-dialog {
  border-radius: 24px;
  overflow: hidden;
  background: white;
}
.elegant-dialog >>> .el-dialog__header {
  padding: 20px 24px 0;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}
.elegant-dialog >>> .el-dialog__title {
  font-size: 20px;
  font-weight: 700;
  padding-left: 12px;
  position: relative;
}
.elegant-dialog >>> .el-dialog__title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 2px;
}
.tool-dialog-content {
  max-height: 60vh;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 4px;
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}
.copy-btn {
  text-align: right;
  margin-top: 8px;
}
.mono-input >>> .el-textarea__inner {
  font-family: monospace;
}
.full-width {
  width: 100%;
}
.color-preview {
  width: 100%;
  height: 60px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
.strength-tips {
  margin-top: 8px;
  font-size: 12px;
}
.stats-output p {
  margin: 8px 0;
}
@media screen and (max-width: 768px) {
  .fixed-header {
    padding: 4px 16px;
    height: 70px;
  }
  .main-content {
    padding: 16px;
  }
  .tools-grid {
    grid-template-columns: 1fr;
  }
}
</style>