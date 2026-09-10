<template>
  <!-- 查看函数体对话框 -->
  <el-dialog 
    v-model="viewAppiumVisiable" 
    title="查看函数体" 
    width="900"
    class="elegant-dialog appium-dialog"
    :close-on-click-modal="false"
  >
    <BodyEdit 
      :bind_case_data='[]' 
      v-model='script' 
      lang='python' 
      height="500px"
    ></BodyEdit>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="viewAppiumVisiable = false" class="dialog-cancel-btn">
          关闭
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 主内容区域 -->
  <div class="appium-management-container">
    <!-- 筛选卡片 -->
    <el-card class="filter-card elegant-shadow">
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-appium"></i>
          <h3 class="filter-title">Appium操作筛选</h3>
          <el-tag size="small" type="info" effect="plain">快速筛选</el-tag>
        </div>
      </div>
      
      <div class="filter-form-wrapper">
        <div class="appium-type-section">
          <div class="type-label">
            <i class="icon-type"></i>
            <span class="inline-label-text">操作类型</span>
          </div>
          <el-radio-group 
            v-model="appiumSearch.type" 
            class="appium-type-group"
            @change="getAppiumKey"
          >
            <el-radio-button 
              v-for="(value, label) in AppiumType" 
              :key="value"
              :value="value"
              class="type-radio-button"
            >
              {{ label }}
            </el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </el-card>

    <!-- 主内容卡片 -->
    <el-card class="content-card elegant-shadow">
      <div class="content-header">
        <div class="content-title-section">
          <div class="title-with-stats">
            <h3 class="content-title">Appium操作列表</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">总计</span>
                <span class="stat-value">{{ appium_results.count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">当前页</span>
                <span class="stat-value">{{ page_size_params.page }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作列表区域 -->
      <div class="appium-list-wrapper">
        <div class="appium-list" v-if="appium_results.results && appium_results.results.length > 0">
          <el-card 
            v-for="obj in appium_results.results" 
            :key="obj.id"
            class="appium-item-card elegant-shadow"
          >
            <div class="appium-item-header">
              <div class="item-tags">
                <el-tag 
                  type="primary" 
                  effect="dark" 
                  size="large"
                  class="main-tag"
                >
                  Appium
                </el-tag>
                <el-tag 
                  type="success" 
                  effect="light" 
                  size="large"
                  class="name-tag"
                >
                  {{ obj.name }}
                </el-tag>
              </div>
              <div class="item-actions">
                <el-tooltip 
                  content="查看函数体" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="success" 
                    @click="viewAppium(obj)"
                    class="action-btn view-btn"
                    circle
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip 
                  v-if="isCanChoose" 
                  content="选择操作" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="primary" 
                    @click="chooseAppium(obj)"
                    class="action-btn choose-btn"
                    circle
                  >
                    <el-icon><Pointer /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </div>
            
            <div class="appium-item-content">
              <div class="item-description">
                <i class="icon-desc"></i>
                <span class="desc-text">{{ obj.desc && obj.desc.length > 0 ? obj.desc[0] : '暂无描述' }}</span>
              </div>
            </div>
          </el-card>
        </div>
        
        <div v-else class="empty-state">
          <i class="icon-empty"></i>
          <p class="empty-text">暂无Appium操作数据</p>
        </div>
      </div>

      <!-- 分页组件 -->
      <div class="pagination-wrapper">
        <el-pagination
          :teleported="false"
          v-model:current-page="page_size_params.page"
          v-model:page-size="page_size_params.size"
          :page-sizes="[10, 20, 30, 50]"
          :hide-on-single-page="false"
          layout="total, sizes, prev, pager, next, jumper"
          :total="appium_results.count"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="select input"
          :background="true"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import { View, Pointer } from '@element-plus/icons-vue'
import BodyEdit from './BodyEdit.vue'

export default {
  name: 'AppiumManagement',
  computed: {
    ...mapState(['pathPermission', 'projectInfo']),
    chooseAppiumVisible: {
      get() {
        return this.chooseAppiumVisible
      },
      set(value) {
        this.$emit('update:chooseAppiumVisible', value)
      }
    },
  },
  emits: ['update:chooseAppiumVisible', 'setAppiumData'],
  props: {
    'isCanChoose': {
      type: Boolean,
      default: false,
    },
  },
  components: {
    BodyEdit,
  },
  data() {
    return {
      AppiumType: {
        '全部操作': 0,
        '手机操作': 2,
        '元素操作': 1,
        '弹窗操作': 3,
        '键盘操作': 4,
        '上下文切换': 6,
        '屏幕截图': 10,
      },
      viewAppiumVisiable: false,
      script: '',
      appium_results: [],
      permission: {},
      appiumSearch: {
        name: '',
        find_equal: false,
        type: 0
      },
      page_size_params: {
        page: 1,
        size: 10,
      },
      count: 1,
    }
  },
  methods: {
    ...mapActions(['getRolePermission']),
    
    chooseAppium(appiumData) {
      this.$emit('update:chooseAppiumVisible', false)
      this.$emit('setAppiumData', appiumData)
    },
    
    viewAppium(row) {
      this.viewAppiumVisiable = true
      this.script = row.script
    },
    
    handleCurrentChange() {
      this.getAppiumKey()
    },
    
    handleSizeChange() {
      this.getAppiumKey()
    },
    
    reset() {
      this.appiumSearch.name = ''
    },
    
    search() {
      this.getAppiumKey()
    },
    
    async getAppiumKey() {
      try {
        const response = await this.$api.getAppiumKey(Object.assign(this.appiumSearch, this.page_size_params))
        if (response.status === 200) {
          this.appium_results = { ...response.data }
        }
      } catch (error) {
        console.error('获取Appium操作失败:', error)
      }
    },
  },
  created() {
    if (!this.isCanChoose) {
      this.getRolePermission(this.pathPermission[this.$route.path]).then(res => {
        this.permission = { ...res.result }
      })
    }
    
    this.getAppiumKey()
  }
}
</script>

<style scoped>
.appium-management-container {
  width: 100%;
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  padding: 20px 15px 15px 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: calc(100vh - 80px);
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

.icon-appium {
  display: inline-block;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 8px;
  position: relative;
}

.icon-appium::before {
  content: 'A';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-weight: bold;
  font-size: 12px;
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

.filter-form-wrapper {
  padding: 20px 24px;
}

.appium-type-section {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.type-label {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 80px;
  padding-top: 8px;
}

.icon-type {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM7.07 18.28c.43-.9 3.05-1.78 4.93-1.78s4.51.88 4.93 1.78C15.57 19.36 13.86 20 12 20s-3.57-.64-4.93-1.72zm11.29-1.45c-1.43-1.74-4.9-2.33-6.36-2.33s-4.93.59-6.36 2.33C4.62 15.49 4 13.82 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8c0 1.82-.62 3.49-1.64 4.83zM12 6c-1.94 0-3.5 1.56-3.5 3.5S10.06 13 12 13s3.5-1.56 3.5-3.5S13.94 6 12 6zm0 5c-.83 0-1.5-.67-1.5-1.5S11.17 8 12 8s1.5.67 1.5 1.5S12.83 11 12 11z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.inline-label-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--qm-text-2);
  white-space: nowrap;
}

.appium-type-group {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.type-radio-button >>> .el-radio-button__inner {
  border-radius: 10px !important;
  border: 1px solid var(--qm-line-strong);
  padding: 8px 16px;
  background: var(--qm-bg-2);
  color: var(--qm-text-2);
  font-weight: 500;
  transition: all 0.3s ease;
}

.type-radio-button >>> .el-radio-button__original-radio:checked + .el-radio-button__inner {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.type-radio-button >>> .el-radio-button__inner:hover {
  border-color: var(--qm-line-strong);
  background: var(--qm-bg-1);
}

/* 内容卡片 */
.content-card {
  flex: 1;
  background: var(--qm-bg-2);
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
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

/* Appium列表区域 */
.appium-list-wrapper {
  flex: 1;
  padding: 0 24px;
  max-height: calc(100vh - 480px);
  overflow-y: auto;
  overflow-x: hidden;
}

.appium-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 16px;
  padding: 16px 0;
}

.appium-item-card {
  border: none;
  border-radius: 12px;
  background: var(--qm-bg-2);
  transition: all 0.3s ease;
  cursor: pointer;
}

.appium-item-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.appium-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--qm-bg-3);
}

.item-tags {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-tag {
  font-weight: 600;
  border: none;
  border-radius: 20px;
  padding: 6px 12px;
}

.name-tag {
  border-radius: 20px;
  padding: 6px 12px;
  font-weight: 500;
  border: 1px solid #10b981;
}

.item-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  transition: all 0.3s ease;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
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

.action-btn:active {
  transform: translateY(0) scale(0.95);
}

.action-btn.view-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
}

.action-btn.view-btn:hover {
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4);
}

.action-btn.choose-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border: none;
}

.action-btn.choose-btn:hover {
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
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

.appium-item-content {
  padding: 16px;
}

.item-description {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.icon-desc {
  width: 16px;
  height: 16px;
  min-width: 16px;
  margin-top: 2px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.desc-text {
  color: var(--qm-text-2);
  font-size: 14px;
  line-height: 1.5;
  flex: 1;
  word-break: break-word;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--qm-text-3);
}

.icon-empty {
  display: block;
  width: 80px;
  height: 80px;
  margin-bottom: 20px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 7h2v2H7zm0 4h2v2H7zm4-4h2v2h-2zm0 4h2v2h-2zm4-4h2v2h-2zm0 4h2v2h-2z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.5;
}

.empty-text {
  font-size: 16px;
  color: var(--qm-text-3);
  margin: 0;
}

/* 分页组件样式 */
.pagination-wrapper {
  padding: 20px 24px 0px 24px;
  border-top: 1px solid var(--qm-bg-3);
  flex-shrink: 0;
  float: right;
  display: block !important;
  min-height: 40px;
  background: var(--qm-bg-2);
  z-index: 10;
  position: relative;
  opacity: 1 !important;
  visibility: visible !important;
}



/* 对话框样式 */
.elegant-dialog >>> .el-dialog {
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.elegant-dialog >>> .el-dialog__header {
  padding: 24px 24px 0;
  margin: 0;
}

.elegant-dialog >>> .el-dialog__title {
  font-size: 20px;
  font-weight: 700;
  color: var(--qm-text-1);
  display: flex;
  align-items: center;
  gap: 12px;
}

.elegant-dialog >>> .el-dialog__title::before {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 2px;
}

.elegant-dialog >>> .el-dialog__body {
  padding: 24px;
}

.elegant-dialog >>> .el-dialog__footer {
  padding: 16px 24px 24px;
  border-top: 1px solid var(--qm-bg-3);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.dialog-cancel-btn {
  padding: 10px 24px;
  border-radius: 10px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  color: var(--qm-text-2);
  font-weight: 500;
  transition: all 0.3s ease;
}

.dialog-cancel-btn:hover {
  background: var(--qm-bg-1);
  border-color: var(--qm-line-strong);
  transform: translateY(-1px);
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .appium-management-container {
    padding: 16px;
  }
  
  .filter-card .filter-header,
  .filter-card .filter-form-wrapper,
  .content-card .content-header,
  .content-card .appium-list-wrapper {
    padding: 16px 20px;
  }
  
  .appium-list {
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  }
}

@media screen and (max-width: 992px) {
  .appium-list {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

@media screen and (max-width: 768px) {
  .appium-management-container {
    padding: 12px;
  }
  
  .appium-type-section {
    flex-direction: column;
    gap: 12px;
  }
  
  .appium-list {
    grid-template-columns: 1fr;
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
  
  .appium-item-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .item-actions {
    align-self: flex-end;
  }
}

@media screen and (max-width: 576px) {
  .appium-type-group {
    flex-direction: column;
  }
  
  .type-radio-button {
    width: 100%;
  }
  
  .type-radio-button >>> .el-radio-button__inner {
    width: 100%;
    text-align: center;
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

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.filter-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.content-card {
  animation: slideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
}

.appium-item-card {
  animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.appium-item-card:nth-child(1) { animation-delay: 0.1s; }
.appium-item-card:nth-child(2) { animation-delay: 0.15s; }
.appium-item-card:nth-child(3) { animation-delay: 0.2s; }
.appium-item-card:nth-child(4) { animation-delay: 0.25s; }
.appium-item-card:nth-child(5) { animation-delay: 0.3s; }
.appium-item-card:nth-child(6) { animation-delay: 0.35s; }
.appium-item-card:nth-child(7) { animation-delay: 0.4s; }
.appium-item-card:nth-child(8) { animation-delay: 0.45s; }
.appium-item-card:nth-child(9) { animation-delay: 0.5s; }
.appium-item-card:nth-child(10) { animation-delay: 0.55s; }
</style>