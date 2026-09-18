<template>
  <div class="audit-log-container">
    <!-- 搜索筛选区域 -->
    <el-card class="filter-card elegant-shadow">
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-search"></i>
          <h3 class="filter-title">审计日志筛选</h3>
          <el-tag size="small" type="info" effect="plain">操作记录</el-tag>
        </div>
        <div class="header-action-section">
          <el-button class="reset-btn" @click="reset">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
          <el-button type="primary" @click="search" class="search-btn">
            <el-icon><Search /></el-icon>查询
          </el-button>
        </div>
      </div>

      <div class="filter-form-wrapper">
        <el-form :model="searchForm" class="filter-form inline-form">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-project"></i>
                  <span class="label-text">项目</span>
                </div>
                <el-select v-model="searchForm.project" placeholder="请选择项目" clearable filterable size="large" class="select" popper-class="select-dropdown-rounded">
                  <el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-module"></i>
                  <span class="label-text">模块</span>
                </div>
                <el-cascader
                  v-model="searchForm.module"
                  :options="moduleOptions"
                  :props="{ emitPath: false, checkStrictly: true }"
                  placeholder="请选择模块"
                  clearable
                  filterable
                  size="large"
                  class="cascader-module"
                  style="width: 100%; flex: 1;"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-action"></i>
                  <span class="label-text">操作类型</span>
                </div>
                <el-select v-model="searchForm.action" placeholder="请选择操作类型" clearable size="large" class="select" popper-class="select-dropdown-rounded">
                  <el-option label="新增" value="create" />
                  <el-option label="修改" value="update" />
                  <el-option label="删除" value="delete" />
                  <el-option label="登录" value="login" />
                  <el-option label="登出" value="logout" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-method"></i>
                  <span class="label-text">HTTP方法</span>
                </div>
                <el-select v-model="searchForm.method" placeholder="请选择方法" clearable size="large" class="select" popper-class="select-dropdown-rounded">
                  <el-option label="POST" value="POST" />
                  <el-option label="PUT" value="PUT" />
                  <el-option label="PATCH" value="PATCH" />
                  <el-option label="DELETE" value="DELETE" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-status"></i>
                  <span class="label-text">状态码</span>
                </div>
                <el-select v-model="searchForm.status_code" placeholder="请选择状态码" clearable size="large" class="select" filterable popper-class="select-dropdown-rounded">
                  <el-option label="200 OK (成功)" value="200" />
                  <el-option label="201 Created (创建)" value="201" />
                  <el-option label="204 No Content (无内容)" value="204" />
                  <el-option label="301 Moved (永久重定向)" value="301" />
                  <el-option label="302 Found (临时重定向)" value="302" />
                  <el-option label="400 Bad Request (错误请求)" value="400" />
                  <el-option label="401 Unauthorized (未认证)" value="401" />
                  <el-option label="403 Forbidden (禁止访问)" value="403" />
                  <el-option label="404 Not Found (未找到)" value="404" />
                  <el-option label="405 Method Not Allowed (方法不允许)" value="405" />
                  <el-option label="409 Conflict (冲突)" value="409" />
                  <el-option label="422 Unprocessable (实体错误)" value="422" />
                  <el-option label="500 Internal Error (服务器错误)" value="500" />
                  <el-option label="502 Bad Gateway (网关错误)" value="502" />
                  <el-option label="503 Unavailable (服务不可用)" value="503" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-time-filter"></i>
                  <span class="label-text">时间范围</span>
                </div>
                <el-date-picker
                  v-model="dateRange"
                  type="datetimerange"
                  range-separator="至"
                  start-placeholder="开始时间"
                  end-placeholder="结束时间"
                  size="large"
                  class="date"
                  style="width: 100%;"
                  :default-time="defaultTimeRange"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-user"></i>
                  <span class="label-text">操作人</span>
                </div>
                <el-select v-model="searchForm.username" placeholder="请选择操作人" clearable filterable size="large" class="select" popper-class="select-dropdown-rounded">
                  <el-option v-for="u in userOptions" :key="u.id" :label="u.username" :value="u.username" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>
    </el-card>

    <!-- 主内容区域 -->
    <el-card class="content-card elegant-shadow">
      <div class="content-header">
        <div class="content-title-section">
          <div class="title-with-stats">
            <h3 class="content-title">审计日志</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">总计</span>
                <span class="stat-value">{{ logList.count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">当前页</span>
                <span class="stat-value">{{ pageParams.page }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="table-wrapper">
        <el-table :data="logList.results" :max-height="'calc(100vh - 550px)'" class="elegant-table" :header-row-style="headerRowStyle">
          <el-table-column label="序号" width="70" type="index" align="center" class-name="index-column">
            <template #default="scope">
              <div class="index-cell">
                {{ scope.$index + 1 + (pageParams.page - 1) * pageParams.size }}
              </div>
            </template>
          </el-table-column>

          <el-table-column label="项目" prop="project_name" min-width="120" align="center" show-overflow-tooltip>
            <template #default="scope">
              {{ scope.row.project_name || scope.row.project || '-' }}
            </template>
          </el-table-column>

          <el-table-column label="操作描述" prop="description" min-width="120" show-overflow-tooltip />

          <el-table-column label="模块" prop="module" min-width="90" align="center" show-overflow-tooltip />

          <el-table-column label="操作类型" prop="action_display" width="90" align="center">
            <template #default="scope">
              <el-tag :type="getActionTagType(scope.row.action)" effect="light" size="small">
                {{ scope.row.action_display }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="方法" prop="method" width="100" align="center">
            <template #default="scope">
              <el-tag :type="getMethodTagType(scope.row.method)" effect="plain" size="small">
                {{ scope.row.method }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="状态码" prop="status_code" width="80" align="center" :show-overflow-tooltip="true">
            <template #default="scope">
              <span :style="{ color: scope.row.status_code >= 200 && scope.row.status_code < 300 ? '#67c23a' : '#f56c6c', fontWeight: '600' }">
                {{ scope.row.status_code }}
              </span>
            </template>
          </el-table-column>

          <el-table-column label="请求路径" prop="path" min-width="260" show-overflow-tooltip>
            <template #default="scope">
              <div class="path-cell">
                <span class="path-link" :title="scope.row.path">{{ scope.row.path }}</span>
                <el-button
                  type="primary"
                  link
                  class="path-copy-btn"
                  @click.stop="copyText(scope.row.path)"
                  title="复制"
                >
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="IP地址" prop="ip" width="130" align="center" />

          <el-table-column label="操作人" prop="username" width="150" align="center" />

          <el-table-column label="操作时间" prop="create_time" width="180" align="center" class-name="time-column">
            <template #default="scope">
              <div class="time-cell">
                <i class="icon-time"></i>
                <span>{{ formatTime(scope.row.create_time) }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="120" align="center" class-name="action-column" fixed="right">
            <template #default="scope">
              <div class="action-buttons">
                <el-tooltip content="查看详情" placement="top" effect="dark">
                  <el-button type="success" class="action-btn view-btn" @click.stop="viewDetail(scope.row)" circle>
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="版本回退" placement="top" effect="dark" v-if="canRollback(scope.row)">
                  <el-button type="warning" class="action-btn rollback-btn" @click.stop="rollback(scope.row)" circle>
                    <el-icon><RefreshLeft /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pageParams.page"
          v-model:page-size="pageParams.size"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="logList.count"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="select input"
          popper-class="select-dropdown-rounded"
          :background="true"
        />
      </div>
    </el-card>

    <!-- 详情抽屉 — 参考 FunCaseList 编辑用例弹窗布局 -->
    <el-drawer
      v-model="detailVisible"
      :with-header="false"
      direction="rtl"
      :show-close="false"
      :append-to-body="true"
      :close-on-click-modal="false"
      size="calc(100vw)"
      class="audit-detail-drawer"
    >
      <el-card class="content-card elegant-shadow" v-if="currentLog">
        <div class="content-header">
          <div class="header-top">
            <div class="drawer-title-with-bar">
              <span class="drawer-title-text">{{ currentLog.description || '操作描述' }}</span>
            </div>
            <el-button
              text
              class="header-close-btn"
              @click="detailVisible = false"
              title="关闭"
            >
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>

        <div class="drawer-split-layout">
          <!-- 左侧：数据内容 -->
          <div class="drawer-left">
            <div class="section-title">数据内容</div>
            <el-divider class="section-divider"></el-divider>
            <div class="drawer-left-content">
              <el-tabs v-model="activeJsonTab" class="json-tabs">
                <el-tab-pane label="字段对比" name="diff" v-if="hasDiffData">
                  <div class="diff-toolbar">
                    <div class="diff-summary">
                      <span class="diff-badge diff-badge-change">变更 {{ diffStats.changed }} 项</span>
                      <span class="diff-badge diff-badge-add">新增 {{ diffStats.added }} 项</span>
                      <span class="diff-badge diff-badge-del">删除 {{ diffStats.removed }} 项</span>
                      <span class="diff-badge diff-badge-same">未变 {{ diffStats.same }} 项</span>
                    </div>
                    <div class="diff-actions">
                      <el-checkbox v-model="showOnlyChanged" size="small">仅显示变更项</el-checkbox>
                    </div>
                  </div>
                  <div class="diff-table-wrap">
                    <table class="diff-table" v-if="filteredDiffRows.length">
                      <thead>
                        <tr>
                          <th class="diff-col-field">字段</th>
                          <th class="diff-col-before">修改前</th>
                          <th class="diff-col-after">修改后</th>
                          <th class="diff-col-status">状态</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="row in filteredDiffRows" :key="row.key" :class="['diff-row', `diff-row-${row.status}`]">
                          <td class="diff-cell diff-cell-field"><code>{{ row.key }}</code></td>
                          <td class="diff-cell diff-cell-before">
                            <pre v-if="row.before !== '' && row.before !== null"><code>{{ row.before }}</code></pre>
                            <span v-else class="diff-empty">-</span>
                          </td>
                          <td class="diff-cell diff-cell-after">
                            <pre v-if="row.after !== '' && row.after !== null"><code>{{ row.after }}</code></pre>
                            <span v-else class="diff-empty">-</span>
                          </td>
                          <td class="diff-cell diff-cell-status">
                            <el-tag v-if="row.status === 'changed'" type="warning" size="small" effect="light">修改</el-tag>
                            <el-tag v-else-if="row.status === 'added'" type="success" size="small" effect="light">新增</el-tag>
                            <el-tag v-else-if="row.status === 'removed'" type="danger" size="small" effect="light">删除</el-tag>
                            <el-tag v-else type="info" size="small" effect="plain">未变</el-tag>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <el-empty v-else description="暂无变更数据" />
                  </div>
                </el-tab-pane>
                <el-tab-pane label="请求体" name="request" v-if="currentLog.request_body">
                  <div class="json-toolbar">
                    <span class="json-meta">{{ (currentLog.request_body_pretty || currentLog.request_body || '').length }} 字符</span>
                    <el-button size="small" class="icon-copy-btn" @click="copyJson(currentLog.request_body_pretty || currentLog.request_body)" title="复制">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </div>
                  <pre class="json-block">{{ currentLog.request_body_pretty || currentLog.request_body }}</pre>
                </el-tab-pane>
                <el-tab-pane label="响应体" name="response" v-if="currentLog.response_body">
                  <div class="json-toolbar">
                    <span class="json-meta">{{ (currentLog.response_body_pretty || currentLog.response_body || '').length }} 字符</span>
                    <el-button size="small" class="icon-copy-btn" @click="copyJson(currentLog.response_body_pretty || currentLog.response_body)" title="复制">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </div>
                  <pre class="json-block">{{ currentLog.response_body_pretty || currentLog.response_body }}</pre>
                </el-tab-pane>
                <el-tab-pane label="操作前数据" name="before" v-if="currentLog.before_data">
                  <div class="json-toolbar">
                    <span class="json-meta">{{ beforeDataPretty.length }} 字符</span>
                    <el-button size="small" class="icon-copy-btn" @click="copyJson(beforeDataPretty)" title="复制">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </div>
                  <pre class="json-block">{{ beforeDataPretty }}</pre>
                </el-tab-pane>
                <el-tab-pane label="操作后数据" name="after" v-if="currentLog.after_data">
                  <div class="json-toolbar">
                    <span class="json-meta">{{ afterDataPretty.length }} 字符</span>
                    <el-button size="small" class="icon-copy-btn" @click="copyJson(afterDataPretty)" title="复制">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </div>
                  <pre class="json-block">{{ afterDataPretty }}</pre>
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
          <!-- 右侧：基础信息 -->
          <div class="drawer-right">
            <div class="section-title">基础信息</div>
            <el-divider class="section-divider"></el-divider>
            <div class="step-base-info">
              <el-form label-position="top" class="info-form">
                <el-form-item label="项目">
                  <el-input :model-value="currentLog.project_name || currentLog.project || '-'" readonly size="large" />
                </el-form-item>
                <el-form-item label="操作描述">
                  <el-input :model-value="currentLog.description || '-'" readonly size="large" type="textarea" :rows="2" />
                </el-form-item>
                <el-form-item label="模块">
                  <el-input :model-value="currentLog.module || '-'" readonly size="large" />
                </el-form-item>
                <el-form-item label="操作类型">
                  <el-tag :type="getActionTagType(currentLog.action)" effect="light" size="large">
                    {{ currentLog.action_display }}
                  </el-tag>
                </el-form-item>
                <el-form-item label="HTTP方法">
                  <el-tag :type="getMethodTagType(currentLog.method)" effect="plain" size="large">
                    {{ currentLog.method }}
                  </el-tag>
                </el-form-item>
                <el-form-item label="状态码">
                  <span :style="{ color: currentLog.status_code >= 200 && currentLog.status_code < 300 ? '#67c23a' : '#f56c6c', fontWeight: '600', fontSize: '16px' }">
                    {{ currentLog.status_code }}
                  </span>
                </el-form-item>
                <el-form-item label="对象ID">
                  <el-input :model-value="currentLog.object_id || '-'" readonly size="large" />
                </el-form-item>
                <el-form-item label="IP地址">
                  <el-input :model-value="currentLog.ip || '-'" readonly size="large" />
                </el-form-item>
                <el-form-item label="请求路径">
                  <el-input :model-value="currentLog.path || '-'" readonly size="large" type="textarea" :rows="2" />
                </el-form-item>
                <el-form-item label="操作人">
                  <el-input :model-value="currentLog.username || '-'" readonly size="large" />
                </el-form-item>
                <el-form-item label="操作时间">
                  <el-input :model-value="formatTime(currentLog.create_time)" readonly size="large" />
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>
      </el-card>
    </el-drawer>
  </div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, View, RefreshLeft, CopyDocument, Close } from '@element-plus/icons-vue'
import { mapState } from 'vuex'
import api from '../../api/index.js'

export default {
  name: 'AuditLog',
  components: { Refresh, Search, View, RefreshLeft, CopyDocument },
  data() {
    return {
      searchForm: {
        username: '',
        action: '',
        project: '',
        module: '',
        method: '',
        status_code: '',
      },
      dateRange: [],
      // default-time 必须使用 Date 对象数组（Element Plus datetimerange 内部用 Date 做解析）
      // 字符串数组形式在本版本会触发 dayjs 解析 NaN -> monthNaN
      defaultTimeRange: [
        new Date(2000, 0, 1, 0, 0, 0),
        new Date(2000, 0, 1, 23, 59, 59),
      ],
      logList: { count: 0, results: [] },
      pageParams: { page: 1, size: 20 },
      detailVisible: false,
      currentLog: null,
      activeJsonTab: 'request',
      showOnlyChanged: false,
      userOptions: [],
      projectOptions: [],
      menuOptions: [],
    }
  },
  computed: {
    ...mapState(['userInfo', 'projectInfo']),
    moduleOptions() {
      // 级联数据：一级菜单作为父节点，二级菜单作为子节点
      const systemMgmt = {
        value: '系统管理',
        label: '系统管理',
        children: [
          { value: '用户列表', label: '用户列表' },
          { value: '权限列表', label: '权限列表' },
          { value: '角色列表', label: '角色列表' },
        ]
      }
      const menuOpts = (this.menuOptions || []).map(group => ({
        value: group.name,
        label: group.name,
        children: (group.children || []).map(child => ({ value: child.name, label: child.name }))
      }))
      return [systemMgmt, ...menuOpts]
    },
    // 能否展示字段对比：before_data / after_data 至少有一个
    hasDiffData() {
      return !!(this.currentLog && (this.currentLog.before_data || this.currentLog.after_data))
    },
    // 解析 before/after 中的 fields 对象（Django serializers.serialize 格式：[{model, pk, fields}]）
    _beforeFields() {
      return this._extractDjangoFields(this.currentLog?.before_data)
    },
    _afterFields() {
      return this._extractDjangoFields(this.currentLog?.after_data)
    },
    // 字段对比行：[{ key, before, after, status: 'changed'|'added'|'removed'|'same' }]
    diffRows() {
      if (!this.hasDiffData) return []
      const before = this._beforeFields || {}
      const after = this._afterFields || {}
      const allKeys = Array.from(new Set([...Object.keys(before), ...Object.keys(after)]))
      return allKeys.map(key => {
        const hasBefore = Object.prototype.hasOwnProperty.call(before, key)
        const hasAfter = Object.prototype.hasOwnProperty.call(after, key)
        const b = hasBefore ? before[key] : undefined
        const a = hasAfter ? after[key] : undefined
        const bStr = this._stringifyValue(b)
        const aStr = this._stringifyValue(a)
        let status = 'same'
        if (!hasBefore && hasAfter) status = 'added'
        else if (hasBefore && !hasAfter) status = 'removed'
        else if (bStr !== aStr) status = 'changed'
        return { key, before: bStr, after: aStr, status }
      })
    },
    diffStats() {
      const rows = this.diffRows
      return {
        changed: rows.filter(r => r.status === 'changed').length,
        added: rows.filter(r => r.status === 'added').length,
        removed: rows.filter(r => r.status === 'removed').length,
        same: rows.filter(r => r.status === 'same').length,
      }
    },
    filteredDiffRows() {
      const rows = this.diffRows
      // 展示顺序：先变更项，再新增，再删除，最后未变
      const order = { changed: 0, added: 1, removed: 2, same: 3 }
      const list = this.showOnlyChanged ? rows.filter(r => r.status !== 'same') : rows
      return [...list].sort((a, b) => order[a.status] - order[b.status])
    },
    // 格式化展示操作前/后数据（仅提取 fields 并 pretty-print）
    beforeDataPretty() {
      const fields = this._beforeFields
      if (!fields || Object.keys(fields).length === 0) return ''
      return JSON.stringify(fields, null, 2)
    },
    afterDataPretty() {
      const fields = this._afterFields
      if (!fields || Object.keys(fields).length === 0) return ''
      return JSON.stringify(fields, null, 2)
    },
  },
  mounted() {
    if (!this.userInfo.is_superuser){
        // 重定向到权限页面，并传递from参数
        this.$router.push({name: 'noPermission', query: {from: this.$route.fullPath}})
    } else {
        this.fetchLogs()
        this.fetchUserNames()
        this.fetchProjects()
        this.fetchMenuOptions()
    }
  },
  methods: {
    async fetchMenuOptions() {
      try {
        const res = await api.getRole(0, { is_add: false })
        if (res.status === 200 && res.data && res.data.result) {
          this.menuOptions = res.data.result.role_permissions || []
        }
      } catch (e) {
        // 获取菜单选项失败时静默处理
      }
    },
    async fetchUserNames() {
      try {
        const res = await api.getUserNames()
        if (res.status === 200) {
          this.userOptions = res.data.results || []
        }
      } catch (e) {
        // 获取用户列表失败时静默处理
      }
    },
    async fetchProjects() {
      try {
        const res = await api.getProjects({ size: 1000 })
        if (res.status === 200) {
          this.projectOptions = res.data.results || []
        }
      } catch (e) {
        // 获取项目列表失败时静默处理
      }
    },
    headerRowStyle() {
      return {
        'font-weight': '600',
        'color': 'var(--qm-text-1)',
        'background-color': 'var(--qm-bg-1)',
        'border-bottom': '1px solid var(--qm-line-strong)',
        'height': '56px'
      }
    },
    async fetchLogs() {
      const params = {
        page: this.pageParams.page,
        size: this.pageParams.size,
        ...this.searchForm,
      }
      if (this.dateRange && this.dateRange.length === 2) {
        const pad = n => String(n).padStart(2, '0')
        const fmt = d => {
          if (!(d instanceof Date) || isNaN(d.getTime())) return ''
          return (
            d.getFullYear() + '-' +
            pad(d.getMonth() + 1) + '-' +
            pad(d.getDate()) + ' ' +
            pad(d.getHours()) + ':' +
            pad(d.getMinutes()) + ':' +
            pad(d.getSeconds())
          )
        }
        const sp = fmt(this.dateRange[0])
        const ep = fmt(this.dateRange[1])
        if (sp && ep) {
          params.create_time_start = sp
          params.create_time_end = ep
        }
      }
      const res = await api.getAuditLogs(params)
      if (res.status === 200) {
        const data = res.data.result || res.data
        this.logList = {
          count: data.count || 0,
          results: data.results || []
        }
      }
    },
    search() {
      this.pageParams.page = 1
      this.fetchLogs()
    },
    reset() {
      this.searchForm = { username: '', action: '', project: '', module: '', method: '', status_code: '' }
      this.dateRange = []
      this.pageParams.page = 1
      this.fetchLogs()
    },
    handleSizeChange() {
      this.pageParams.page = 1
      this.fetchLogs()
    },
    handleCurrentChange() {
      this.fetchLogs()
    },
    viewDetail(row) {
      this.currentLog = row
      this.showOnlyChanged = false
      // 自动选择第一个有数据的 tab（优先字段对比）
      const hasBeforeOrAfter = !!(row.before_data || row.after_data)
      if (hasBeforeOrAfter && ['update', 'delete', 'create'].includes(row.action)) this.activeJsonTab = 'diff'
      else if (row.request_body) this.activeJsonTab = 'request'
      else if (row.response_body) this.activeJsonTab = 'response'
      else if (row.before_data) this.activeJsonTab = 'before'
      else this.activeJsonTab = 'diff'
      this.detailVisible = true
    },
    // 从 Django serializers.serialize('json') 输出中提取 fields 对象
    _extractDjangoFields(raw) {
      if (!raw) return {}
      try {
        const arr = typeof raw === 'string' ? JSON.parse(raw) : raw
        if (Array.isArray(arr) && arr[0] && arr[0].fields) {
          return arr[0].fields
        }
        if (arr && typeof arr === 'object' && !Array.isArray(arr)) {
          return arr
        }
        return {}
      } catch (e) {
        return {}
      }
    },
    // 把字段值格式化成字符串（保留空字符串/ null 语义：用于判断 before/after 是否为空）
    _stringifyValue(v) {
      if (v === null || v === undefined) return v
      if (typeof v === 'object') {
        try {
          return JSON.stringify(v, null, 2)
        } catch (e) {
          return String(v)
        }
      }
      return String(v)
    },
    canRollback(row) {
      return ['create', 'update', 'delete'].includes(row.action) && row.before_data
    },
    async rollback(row) {
      try {
        await ElMessageBox.confirm(
          `确认要回退此操作吗？${row.description}（操作时间：${this.formatTime(row.create_time)}）`,
          '版本回退确认',
          { type: 'warning', confirmButtonText: '确认回退', cancelButtonText: '取消' }
        )
        const res = await api.rollbackAuditLog(row.id)
        if (res.status === 200) {
          ElMessage.success(res.data.detail || '回退成功')
          this.fetchLogs()
        } else {
          ElMessage.error(res.data.detail || '回退失败')
        }
      } catch (e) {
        if (e !== 'cancel') {
          ElMessage.error('回退失败')
        }
      }
    },
    formatTime(time) {
      if (!time) return '-'
      return new Date(time).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).replace(/\//g, '-')
    },
    getActionTagType(action) {
      const map = { create: 'success', update: 'warning', delete: 'danger', login: 'info', logout: 'info' }
      return map[action] || ''
    },
    getMethodTagType(method) {
      const map = { POST: 'success', PUT: 'warning', PATCH: 'warning', DELETE: 'danger' }
      return map[method] || ''
    },
    async copyJson(text) {
      try {
        await navigator.clipboard.writeText(text)
        ElMessage.success('已复制到剪贴板')
      } catch {
        ElMessage.error('复制失败')
      }
    },
    async copyText(text) {
      try {
        await navigator.clipboard.writeText(text)
        ElMessage.success('已复制到剪贴板')
      } catch {
        ElMessage.error('复制失败')
      }
    },
  },
}
</script>

<style scoped>
.audit-log-container {
  width: 100%;
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  padding: 20px 15px 15px 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: calc(100vh - 75px);
  min-height: calc(100vh - 75px);
  max-height: calc(100vh - 75px);
  overflow: hidden;
}

/* 优雅阴影效果 */
.elegant-shadow {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06),
              0 1px 4px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.elegant-shadow:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1),
              0 2px 8px rgba(0, 0, 0, 0.12);
}

/* 筛选卡片 */
.filter-card {
  background: var(--qm-bg-2);
  border: none;
  border-radius: 16px;
  overflow: hidden;
  flex-shrink: 0;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 24px 10px 24px;
  border-bottom: 1px solid var(--qm-bg-3);
}

.header-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-search {
  display: inline-block;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  border-radius: 8px;
  position: relative;
}

.icon-search::before {
  content: '';
  position: absolute;
  top: 7px;
  left: 7px;
  width: 8px;
  height: 8px;
  border: 2px solid white;
  border-radius: 50%;
}

.icon-search::after {
  content: '';
  position: absolute;
  top: 15px;
  left: 15px;
  width: 6px;
  height: 2px;
  background: var(--qm-bg-2);
  transform: rotate(45deg);
}

.filter-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--qm-text-1);
  background: linear-gradient(135deg, var(--qm-text-1) 0%, var(--qm-text-2) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-action-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.reset-btn {
  padding: 10px 20px;
  border-radius: 10px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  color: var(--qm-text-2);
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reset-btn:hover {
  background: var(--qm-bg-1);
  border-color: var(--qm-line-strong);
  transform: translateY(-1px);
}

.reset-btn .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

.search-btn {
  padding: 10px 24px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.search-btn .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

.filter-card :deep(.el-card__body) {
  padding: 20px 20px 0 20px;
}

.filter-form-wrapper {
  padding: 25px 24px 0px 24px;
}

.inline-form {
  margin-bottom: 0;
}

.form-item-inline {
  margin-bottom: 25px;
  display: flex;
  flex-direction: row;
  align-items: center;
  height: 40px;
}

.form-item-inline :deep(.el-form-item__content) {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  flex-wrap: nowrap !important;
  margin-left: 0 !important;
  width: 100%;
}

.label-with-icon {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--qm-text-2);
  width: 90px;
  margin-right: 10px;
  flex-shrink: 0;
  white-space: nowrap;
}

.label-text {
  white-space: nowrap;
}

/* 级联选择器样式 — 移到非 scoped 块（见文件末尾） */

/* 筛选区小图标 */
.icon-user, .icon-action, .icon-project, .icon-module, .icon-method, .icon-status, .icon-time-filter {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
}

.icon-user { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-action { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); }
.icon-project { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-module { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.icon-method { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-status { background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); }
.icon-time-filter { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }

/* 内容卡片 */
.content-card {
  flex: 1;
  background: var(--qm-bg-2);
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding-bottom: 0px;
  max-height: 100%;
  overflow: hidden;
}

.content-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--qm-bg-3);
  flex-shrink: 0;
}

.content-title-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-with-stats {
  display: flex;
  align-items: center;
  gap: 20px;
}

.content-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--qm-text-1);
  position: relative;
  padding-left: 16px;
}

.content-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 2px;
}

.stats-info {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--qm-bg-1);
  border-radius: 8px;
  border: 1px solid var(--qm-line-strong);
}

.stat-label {
  font-size: 12px;
  color: var(--qm-text-2);
  font-weight: 500;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--qm-text-1);
}

/* 表格区域 */
.table-wrapper {
  flex: 1;
  padding: 0 0px;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.elegant-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: transparent;
  border-radius: 12px;
  overflow: hidden;
}

.elegant-table :deep(.el-table__header-wrapper th) {
  background: linear-gradient(180deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  font-weight: 600;
  color: var(--qm-text-1);
  border-bottom: 1px solid var(--qm-line-strong);
  padding: 16px 0;
}

.elegant-table :deep(.el-table__header-wrapper .cell) {
  padding: 0 16px;
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row) {
  transition: all 0.3s ease;
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row:nth-child(even)) {
  background: var(--qm-bg-1);
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row:hover) {
  background: var(--qm-warning-soft);
  transform: translateX(4px);
}

.elegant-table :deep(.el-table__body-wrapper td) {
  border-bottom: 1px solid var(--qm-bg-3);
  padding: 16px 0;
  transition: all 0.3s ease;
}

.elegant-table :deep(.el-table__body-wrapper .cell) {
  padding: 0 16px;
}

.path-cell {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
  min-width: 0;
}
.path-link {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #f59e0b;
  cursor: pointer;
  font-size: 13px;
  text-decoration: underline;
  text-underline-offset: 2px;
  text-decoration-color: rgba(245, 158, 11, 0.4);
  transition: all 0.2s ease;
}
.path-link:hover {
  color: #d97706;
  text-decoration-color: #d97706;
}
.path-copy-btn {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  padding: 0 !important;
  color: var(--qm-text-2) !important;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s ease !important;
}
.path-copy-btn:hover {
  background: var(--qm-bg-3) !important;
  color: #f59e0b !important;
}
.path-copy-btn .el-icon {
  width: 14px;
  height: 14px;
}

.index-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--qm-bg-3) 0%, var(--qm-line-strong) 100%);
  border-radius: 8px;
  font-weight: 600;
  color: var(--qm-text-2);
  margin: 0 auto;
}

.time-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--qm-text-2);
  font-size: 13px;
}

.icon-time {
  width: 14px;
  height: 14px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  padding: 0;
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.3s, height 0.3s;
}

.action-btn:hover {
  transform: translateY(-2px) scale(1.1);
}

.action-btn:hover::before {
  width: 100%;
  height: 100%;
}

.action-btn.view-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.action-btn.rollback-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.action-btn.view-btn:hover {
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4);
}

.action-btn.rollback-btn:hover {
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.action-btn:active {
  transform: translateY(0) scale(0.95);
}

.action-btn .el-icon {
  color: white;
  font-size: 16px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 分页组件样式 */
.pagination-wrapper {
  padding: 20px 24px 0px 24px;
  float: right;
  flex-shrink: 0;
  display: block !important;
  min-height: 40px;
  background: var(--qm-bg-2);
  z-index: 10;
}

/* 全屏对话框样式 — 见文件末尾非 scoped 块（dialog 使用 append-to-body） */

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .audit-log-container {
    padding: 16px;
    height: calc(100vh - 60px);
    min-height: calc(100vh - 60px);
    max-height: calc(100vh - 60px);
  }

  .filter-card .filter-header,
  .filter-card .filter-form-wrapper,
  .content-card .content-header,
  .content-card .table-wrapper {
    padding: 16px 20px;
  }

  .label-with-icon {
    width: 78px;
    font-size: 13px;
  }
}

@media screen and (max-width: 768px) {
  .audit-log-container {
    padding: 12px;
    height: auto;
    min-height: calc(100vh - 60px);
    max-height: none;
    overflow-y: auto;
  }

  .filter-card .filter-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-title-section,
  .header-action-section {
    justify-content: center;
  }

  .filter-form .el-row .el-col {
    width: 100%;
    margin-bottom: 16px;
  }

  .form-item-inline {
    flex-direction: column;
    align-items: flex-start;
    height: auto;
  }

  .form-item-inline :deep(.el-form-item__content) {
    flex-direction: column !important;
    align-items: flex-start !important;
  }

  .label-with-icon {
    margin-bottom: 8px;
    margin-right: 0;
    min-width: auto;
  }

  .content-card .content-header .content-title-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .title-with-stats {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .stats-info {
    justify-content: center;
  }

  .table-wrapper {
    overflow-x: auto;
  }

  .elegant-table {
    min-width: 800px;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.filter-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>

<!-- 非 scoped 样式：审计日志详情抽屉（drawer 使用 append-to-body，scoped 样式无法穿透） — 参考 FunCaseList 编辑用例弹窗 -->
<style>
/* 抽屉容器：移除默认内边距，让 content-card 撑满 */
.audit-detail-drawer .el-drawer__body {
  padding: 16px;
  background: var(--qm-bg-1);
}

/* 优雅阴影 */
.audit-detail-drawer .elegant-shadow {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* content-card 主体卡片 */
.audit-detail-drawer .content-card {
  flex: 1;
  background: var(--qm-bg-1);
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  padding: 0;
}
.audit-detail-drawer .content-card .el-card__body {
  padding: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

/* 顶部 header — 样式参考原 audit-detail-dialog 的 title */
.audit-detail-drawer .content-header {
  padding: 16px 24px;
  background: var(--qm-bg-1);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  border-bottom: 1px solid var(--qm-line-strong);
}
.audit-detail-drawer .header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: nowrap;
  min-height: 22px;
}
.audit-detail-drawer .header-close-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--qm-bg-1);
  color: var(--qm-text-2);
  transition: all 0.2s;
  flex-shrink: 0;
  padding: 0;
}
.audit-detail-drawer .header-close-btn:hover {
  background: var(--qm-red-soft);
  color: #ef4444;
}
.audit-detail-drawer .header-close-btn .el-icon {
  font-size: 18px;
}
/* 标题：左侧 4×22 蓝紫渐变竖杠 + 文字本身蓝紫渐变（参考消息弹窗 .platform-name 样式） */
.audit-detail-drawer .drawer-title-with-bar {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}
.audit-detail-drawer .drawer-title-with-bar::before {
  content: '';
  width: 4px;
  height: 22px;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  border-radius: 2px;
  flex-shrink: 0;
}
.audit-detail-drawer .drawer-title-text {
  font-size: 18px;
  font-weight: 800;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.3px;
  line-height: 1.3;
  white-space: nowrap;
}

/* 元信息相关样式暂时保留，避免误删影响其他地方；不使用即不渲染 */
.audit-detail-drawer .meta-divider-placeholder {
  width: 1px;
  height: 14px;
  background: var(--qm-line-strong);
}

.audit-detail-drawer .drawer-split-layout {
  display: flex;
  gap: 16px;
  flex: 1;
  min-height: 0;
  padding: 10px 16px 16px 16px;
  overflow: hidden;
}

.audit-detail-drawer .drawer-left {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: var(--qm-bg-1);
  border: 1px solid var(--qm-line-strong);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  padding: 20px 20px 40px 20px;
}
.audit-detail-drawer .section-divider {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 12px 4px 20px 4px;
  padding: 0;
  border-top: 1px solid var(--qm-line-strong);
}
.audit-detail-drawer .section-divider.el-divider--horizontal {
  background: transparent;
}
.audit-detail-drawer .section-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--qm-text-1);
  padding-left: 14px;
  padding-bottom: 5px;
  position: relative;
  display: inline-block;
  line-height: 1.5;
}
.audit-detail-drawer .section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
  border-radius: 2px;
}
.audit-detail-drawer .drawer-left-content {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
  min-height: 0;
  margin-left: -25px;
}
.audit-detail-drawer .drawer-left-content::-webkit-scrollbar {
  width: 6px;
}
.audit-detail-drawer .drawer-left-content::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 4px;
}
.audit-detail-drawer .drawer-left-content::-webkit-scrollbar-thumb {
  background: var(--qm-line-strong);
  border-radius: 4px;
}
.audit-detail-drawer .drawer-left-content::-webkit-scrollbar-thumb:hover {
  background: var(--qm-line-strong);
}

.audit-detail-drawer .drawer-right {
  width: 320px;
  flex-shrink: 0;
  background: var(--qm-bg-1);
  padding: 20px 20px 40px 20px;
  border: 1px solid var(--qm-line-strong);
  border-radius: 12px;
  overflow-y: auto;
  overflow-x: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}
.audit-detail-drawer .drawer-right::-webkit-scrollbar {
  width: 6px;
}
.audit-detail-drawer .drawer-right::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 4px;
}
.audit-detail-drawer .drawer-right::-webkit-scrollbar-thumb {
  background: var(--qm-line-strong);
  border-radius: 4px;
}
.audit-detail-drawer .drawer-right::-webkit-scrollbar-thumb:hover {
  background: var(--qm-line-strong);
}
.audit-detail-drawer .step-base-info {
  background: transparent;
  padding: 0;
  border-radius: 0;
  border: none;
  margin-bottom: 0;
}
.audit-detail-drawer .info-form .el-form-item {
  margin-bottom: 16px;
}
.audit-detail-drawer .info-form .el-form-item__label {
  color: var(--qm-text-2);
  font-weight: 600;
  font-size: 13px;
  padding-bottom: 6px;
}
.audit-detail-drawer .info-form .el-input__wrapper {
  box-shadow: none;
  background: transparent;
  padding: 0;
}
.audit-detail-drawer .info-form .el-input__wrapper:hover,
.audit-detail-drawer .info-form .el-input__wrapper.is-focus {
  box-shadow: none;
}
.audit-detail-drawer .info-form .el-input.is-disabled .el-input__wrapper,
.audit-detail-drawer .info-form .el-input__wrapper {
  background-color: transparent;
}
.audit-detail-drawer .info-form .el-input__inner {
  padding-left: 0;
  padding-right: 0;
  color: var(--qm-text-1);
  font-weight: 500;
  font-size: 13px;
  font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
}
.audit-detail-drawer .info-form .el-textarea__inner {
  border: none;
  background: transparent;
  padding-left: 0;
  padding-right: 0;
  color: var(--qm-text-1);
  font-weight: 500;
  font-size: 13px;
  font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
  resize: none;
  box-shadow: none;
}
.audit-detail-drawer .info-form .el-textarea__inner:hover,
.audit-detail-drawer .info-form .el-textarea__inner:focus {
  border: none;
  box-shadow: none;
}

/* Tabs 与 JSON 区 */
.audit-detail-drawer .json-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.audit-detail-drawer .json-tabs .el-tabs__header {
  margin: 0 0 16px 0;
  padding: 0 20px;
  flex-shrink: 0;
  border-bottom: 1px solid var(--qm-line-strong);
  background: transparent;
  border-radius: 8px 8px 0 0;
  overflow: visible !important;
}

.audit-detail-drawer .json-tabs .el-tabs__nav-wrap {
  overflow: visible !important;
}

.audit-detail-drawer .json-tabs .el-tabs__nav-scroll {
  overflow: visible !important;
}

.audit-detail-drawer .json-tabs .el-tabs__nav-wrap::after {
  display: none;
}

.audit-detail-drawer .json-tabs .el-tabs__item {
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 0;
  margin: 0 16px;
  height: 48px;
  line-height: 48px;
  font-size: 14px;
  color: var(--qm-text-2);
}

.audit-detail-drawer .json-tabs .el-tabs__item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 3px;
  border-radius: 3px;
  background: transparent;
  transition: width 0.3s ease, background 0.3s ease;
}

.audit-detail-drawer .json-tabs .el-tabs__item:hover::after {
  width: 100%;
  background: rgba(245, 158, 11, 0.5);
}

.audit-detail-drawer .json-tabs .el-tabs__item.is-active::after {
  width: 100%;
  background: #f59e0b;
}

.audit-detail-drawer .json-tabs .el-tabs__item:hover {
  color: #f59e0b;
}

.audit-detail-drawer .json-tabs .el-tabs__item.is-active {
  color: #f59e0b;
  font-weight: 600;
}

.audit-detail-drawer .json-tabs .el-tabs__active-bar {
  display: none;
}

.audit-detail-drawer .json-tabs .el-tabs__content {
  flex: 1;
  overflow: hidden;
  padding: 16px 20px;
  background: transparent;
  border: none;
  border-radius: 0;
}

.audit-detail-drawer .json-tabs .el-tab-pane {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.audit-detail-drawer .json-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-shrink: 0;
  padding: 10px 14px;
  background: var(--qm-bg-3);
  border: 1px solid var(--qm-line-strong);
  border-radius: 8px;
}

.audit-detail-drawer .json-meta {
  font-size: 13px;
  color: var(--qm-text-2);
  font-weight: 500;
}

/* 图标-only 复制按钮 */
.audit-detail-drawer .icon-copy-btn {
  width: 28px;
  height: 28px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-1);
  color: var(--qm-text-2);
  transition: all 0.2s;
}
.audit-detail-drawer .icon-copy-btn:hover {
  background: #f59e0b;
  border-color: #f59e0b;
  color: #fff;
}
.audit-detail-drawer .icon-copy-btn .el-icon {
  font-size: 14px;
}

.audit-detail-drawer .json-block {
  flex: 1;
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 16px 20px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--qm-line-strong);
  max-height: none;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.audit-detail-drawer .json-block::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.audit-detail-drawer .json-block::-webkit-scrollbar-track {
  background: #1e293b;
  border-radius: 4px;
}

.audit-detail-drawer .json-block::-webkit-scrollbar-thumb {
  background: var(--qm-text-2);
  border-radius: 4px;
}

.audit-detail-drawer .json-block::-webkit-scrollbar-thumb:hover {
  background: var(--qm-text-2);
}

/* 字段对比 */
.audit-detail-drawer .diff-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-3);
  border-radius: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 10px;
}
.audit-detail-drawer .diff-summary {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.audit-detail-drawer .diff-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.6;
}
.audit-detail-drawer .diff-badge-change {
  background: #fff7ed;
  color: #c2410c;
  border: 1px solid #fdba74;
}
.audit-detail-drawer .diff-badge-add {
  background: #f0fdf4;
  color: #15803d;
  border: 1px solid #86efac;
}
.audit-detail-drawer .diff-badge-del {
  background: var(--qm-red-soft);
  color: #b91c1c;
  border: 1px solid #fca5a5;
}
.audit-detail-drawer .diff-badge-same {
  background: var(--qm-bg-3);
  color: var(--qm-text-2);
  border: 1px solid var(--qm-line-strong);
}
.audit-detail-drawer .diff-actions {
  display: flex;
  align-items: center;
}
.audit-detail-drawer .diff-table-wrap {
  height: calc(100% - 56px);
  overflow: auto;
  padding: 0;
}
.audit-detail-drawer .diff-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;
  border: 1px solid var(--qm-line-strong);
  border-radius: 10px;
  overflow: hidden;
  background: var(--qm-bg-3);
  color: var(--qm-text-1);
  font-weight: 500;
}
.audit-detail-drawer .diff-table thead th {
  background: linear-gradient(to bottom, var(--qm-bg-1), var(--qm-bg-3));
  color: var(--qm-text-2);
  font-weight: 500;
  font-size: 13px;
  text-align: left;
  padding: 10px 14px;
  border-bottom: 1px solid var(--qm-line-strong);
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 2;
}
.audit-detail-drawer .diff-table tbody td {
  padding: 8px 14px;
  border-bottom: 1px solid var(--qm-bg-3);
  vertical-align: top;
}
.audit-detail-drawer .diff-table tbody tr:last-child td {
  border-bottom: none;
}
.audit-detail-drawer .diff-table .diff-col-field {
  width: 20%;
  min-width: 160px;
}
.audit-detail-drawer .diff-table .diff-col-before {
  width: 33%;
  min-width: 200px;
}
.audit-detail-drawer .diff-table .diff-col-after {
  width: 33%;
  min-width: 200px;
}
.audit-detail-drawer .diff-table .diff-col-status {
  width: 90px;
  text-align: center;
}
.audit-detail-drawer .diff-cell-field code {
  background: var(--qm-bg-3);
  color: var(--qm-text-1);
  padding: 2px 8px;
  border-radius: 6px;
  font-family: 'JetBrains Mono', 'Consolas', monospace;
  font-size: 12.5px;
  font-weight: 500;
}
.audit-detail-drawer .diff-cell-before pre,
.audit-detail-drawer .diff-cell-after pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  padding: 6px 10px;
  border-radius: 6px;
  font-family: 'JetBrains Mono', 'Consolas', monospace;
  font-size: 12.5px;
  line-height: 1.55;
  max-height: 220px;
  overflow: auto;
}
.audit-detail-drawer .diff-cell-before pre {
  background: #fff7ed;
  color: #7c2d12;
  border: 1px solid #fed7aa;
}
.audit-detail-drawer .diff-cell-after pre {
  background: #f0fdf4;
  color: #14532d;
  border: 1px solid #bbf7d0;
}
.audit-detail-drawer .diff-row-changed .diff-cell-before pre {
  background: var(--qm-red-soft);
  color: #7f1d1d;
  border-color: #fecaca;
}
.audit-detail-drawer .diff-row-added .diff-cell-after pre {
  background: #f0fdf4;
  border-color: #86efac;
}
.audit-detail-drawer .diff-row-removed .diff-cell-before pre {
  background: var(--qm-red-soft);
  border-color: #fca5a5;
}
.audit-detail-drawer .diff-row-same .diff-cell-before pre,
.audit-detail-drawer .diff-row-same .diff-cell-after pre {
  background: var(--qm-bg-1);
  color: var(--qm-text-2);
  border-color: var(--qm-line-strong);
}
.audit-detail-drawer .diff-empty {
  color: var(--qm-text-2);
  font-weight: 500;
  font-style: italic;
  padding: 6px 10px;
  display: inline-block;
}
.audit-detail-drawer .diff-table-wrap::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.audit-detail-drawer .diff-table-wrap::-webkit-scrollbar-track {
  background: var(--qm-bg-1);
}
.audit-detail-drawer .diff-table-wrap::-webkit-scrollbar-thumb {
  background: var(--qm-line-strong);
  border-radius: 3px;
}
.audit-detail-drawer .diff-table-wrap::-webkit-scrollbar-thumb:hover {
  background: var(--qm-line-strong);
}
.audit-detail-drawer .diff-cell-before pre::-webkit-scrollbar,
.audit-detail-drawer .diff-cell-after pre::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}
.audit-detail-drawer .diff-cell-before pre::-webkit-scrollbar-thumb,
.audit-detail-drawer .diff-cell-after pre::-webkit-scrollbar-thumb {
  background: var(--qm-line-strong);
  border-radius: 2px;
}

/* 级联选择器样式 — 与 select 风格保持一致（非 scoped：scoped 样式无法稳定作用到 el-cascader 内部） */
.cascader-module.el-cascader {
  flex: 1;
  width: 100%;
  min-width: 0;
  display: flex;
}

.cascader-module.el-cascader .el-input {
  width: 100%;
}

.cascader-module.el-cascader .el-input__wrapper {
  width: 100%;
  border-radius: 10px;
  border: 2px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  box-shadow: none;
  transition: all 0.3s ease;
}

.cascader-module.el-cascader .el-input__wrapper:hover {
  border-color: #f59e0b;
  box-shadow: 0 4px 12px rgba(251, 191, 36, 0.2);
}

.cascader-module.el-cascader .el-input__wrapper.is-focus {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(234, 88, 12, 0.3);
}
</style>
