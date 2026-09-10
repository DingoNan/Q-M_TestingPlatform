<template>
  <div class="performance-report-container">
    <!-- 报告标题和基本信息 -->
    <el-card class="report-header-card elegant-shadow" style='padding: 5px; padding-left: 0px'>
      <div class="report-header">
        <div class="report-left-section">
          <div class="report-title-section">
            <i class="icon-report-header"></i>
            <h1 class="report-title">{{ report_detail.case_name }}性能测试报告</h1>
            <el-tag size="medium" type="primary" effect="plain">性能报告</el-tag>
          </div>
          <div class="report-status">
            <el-tag :type="getStatusType(report_detail.test_process_name)" size="medium" effect="light">
              {{ report_detail.test_process_name }}
            </el-tag>
          </div>
        </div>
        <el-button @click="goBack" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>返回
        </el-button>
      </div>
    </el-card>

    <!-- 基本信息卡片 -->
    <el-card class="info-card elegant-shadow">
      <div class="info-header">
        <div class="info-title-section">
          <i class="icon-info"></i>
          <h3 class="info-title">测试基本信息</h3>
          <el-tag size="small" type="info" effect="plain">基础配置</el-tag>
        </div>
      </div>
      
      <div class="info-content-grid">
        <div class="info-item">
          <div class="info-label">
            <i class="icon-user"></i>
            <span>执行人员</span>
          </div>
          <div class="info-value">{{ report_detail.user_name || '-' }}</div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-env"></i>
            <span>执行环境</span>
          </div>
          <div class="info-value">{{ report_detail.env_name || '-' }}</div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-start-time"></i>
            <span>开始时间</span>
          </div>
          <div class="info-value">{{ report_detail.start_time || '-' }}</div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-end-time"></i>
            <span>结束时间</span>
          </div>
          <div class="info-value">{{ report_detail.end_time || '-' }}</div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-duration"></i>
            <span>持续时间</span>
          </div>
          <div class="info-value">{{ report_detail.duration || '-' }}</div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-users"></i>
            <span>并发用户数</span>
          </div>
          <div class="info-value">
            <el-tag size="small" type="warning" effect="plain">{{ report_detail.max_user || 0 }}</el-tag>
          </div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-rate"></i>
            <span>每秒启动用户数</span>
          </div>
          <div class="info-value">
            <el-tag size="small" type="warning" effect="plain">{{ report_detail.rate || 0 }}</el-tag>
          </div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-cpu"></i>
            <span>CPU使用率</span>
          </div>
          <div class="info-value">
            <el-tag :type="getCpuLevel(report_detail.cpu)" size="small" effect="plain">
              {{ report_detail.cpu || 0 }}%
            </el-tag>
          </div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-memory"></i>
            <span>内存占用</span>
          </div>
          <div class="info-value">
            <el-tag :type="getMemoryLevel(report_detail.memory)" size="small" effect="plain">
              {{ report_detail.memory || 0 }}M
            </el-tag>
          </div>
        </div>
        
        <div class="info-item full-width">
          <div class="info-label">
            <i class="icon-case"></i>
            <span>关联测试用例</span>
          </div>
          <div class="info-value">
            <el-link 
              type="primary" 
              :underline="false" 
              class="case-link"
              @click="jumpCase(report_detail.case)"
            >
              <i class="icon-link"></i>
              {{ report_detail.case_name || '无' }}
            </el-link>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 请求统计 -->
    <el-card class="data-card elegant-shadow">
      <div class="card-header">
        <div class="card-title-section">
          <i class="icon-request"></i>
          <h3 class="card-title">请求统计</h3>
          <el-badge :value="report_detail.requests_statistics?.length || 0" type="info" class="data-badge" />
        </div>
        <div class="card-subtitle">Request Statistics</div>
      </div>
      
      <el-table 
        :data="report_detail.requests_statistics" 
        class="data-table"
        :show-overflow-tooltip="true"
        :header-row-style="getTableHeaderStyle"
        :row-class-name="tableRowClassName"
      >
        <el-table-column label="请求类型" prop="method" width="120" align="center">
          <template #default="scope">
            <el-tag size="small" :type="getMethodType(scope.row.method)" effect="plain" v-if='scope.row.method'>
              {{ scope.row.method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="接口名称" prop="name" min-width="180" align="center" />
        <el-table-column label="请求总数" prop="num_requests" width="120" align="center">
          <template #default="scope">
            <div class="number-value">{{ scope.row.num_requests || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="失败数" prop="num_failures" width="120" align="center">
          <template #default="scope">
            <div class="error-value">{{ scope.row.num_failures || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="平均响应时间(ms)" prop="avg_response_time" width="150" align="center">
          <template #default="scope">
            <div class="time-value">{{ (scope.row.avg_response_time || 0).toFixed(2) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="最小响应时间(ms)" prop="min_response_time" width="150" align="center">
          <template #default="scope">
            <div class="time-value">{{ scope.row.min_response_time || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="最大响应时间(ms)" prop="max_response_time" width="150" align="center">
          <template #default="scope">
            <div class="time-value">{{ scope.row.max_response_time || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="中位数(ms)" prop="median_response_time" width="120" align="center">
          <template #default="scope">
            <div class="time-value">{{ scope.row.median_response_time || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="平均大小(bytes)" prop="avg_content_length" width="150" align="center">
          <template #default="scope">
            <div class="size-value">{{ scope.row.avg_content_length || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="RPS" prop="total_rps" width="100" align="center">
          <template #default="scope">
            <div class="rps-value">{{ (scope.row.total_rps || 0).toFixed(2) }}</div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 响应时间统计 -->
    <el-card class="data-card elegant-shadow">
      <div class="card-header">
        <div class="card-title-section">
          <i class="icon-response"></i>
          <h3 class="card-title">响应时间统计</h3>
          <el-badge :value="report_detail.response_time_statistics?.length || 0" type="success" class="data-badge" />
        </div>
        <div class="card-subtitle">Response Time Statistics</div>
      </div>
      
      <el-table
        :data="report_detail.response_time_statistics"
        class="data-table"
        :show-overflow-tooltip="true"
        :header-row-style="getTableHeaderStyle"
      >
        <el-table-column label="请求类型" prop="method" width="120" align="center">
          <template #default="scope">
            <el-tag size="small" :type="getMethodType(scope.row.method)" effect="plain" v-if='scope.row.method'>
              {{ scope.row.method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="接口名称" prop="name" min-width="180" align="center" />
        <el-table-column label="50%分位数(ms)" prop="0.5" width="140" align="center">
          <template #default="scope">
            <div class="percentile-value">{{ scope.row['0.5'] || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="60%分位数(ms)" prop="0.6" width="140" align="center">
          <template #default="scope">
            <div class="percentile-value">{{ scope.row['0.6'] || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="70%分位数(ms)" prop="0.7" width="140" align="center">
          <template #default="scope">
            <div class="percentile-value">{{ scope.row['0.7'] || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="80%分位数(ms)" prop="0.8" width="140" align="center">
          <template #default="scope">
            <div class="percentile-value">{{ scope.row['0.8'] || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="90%分位数(ms)" prop="0.9" width="140" align="center">
          <template #default="scope">
            <div class="percentile-value">{{ scope.row['0.9'] || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="95%分位数(ms)" prop="0.95" width="140" align="center">
          <template #default="scope">
            <div class="percentile-value">{{ scope.row['0.95'] || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="99%分位数(ms)" prop="0.99" width="140" align="center">
          <template #default="scope">
            <div class="percentile-value">{{ scope.row['0.99'] || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="100%分位数(ms)" prop="1.0" width="140" align="center">
          <template #default="scope">
            <div class="percentile-value">{{ scope.row['1.0'] || 0 }}</div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 异常统计 -->
    <el-card v-if="report_detail.exceptions_statistics?.length !== 0" class="data-card elegant-shadow">
      <div class="card-header">
        <div class="card-title-section">
          <i class="icon-exception"></i>
          <h3 class="card-title">异常统计</h3>
          <el-badge :value="report_detail.exceptions_statistics?.length || 0" type="danger" class="data-badge" />
        </div>
        <div class="card-subtitle">Exceptions Statistics</div>
      </div>
      
      <el-table 
        :data="report_detail.exceptions_statistics" 
        class="data-table"
        :show-overflow-tooltip="true"
        :header-row-style="getTableHeaderStyle"
      >
        <el-table-column label="出现次数" prop="count" width="120" align="center">
          <template #default="scope">
            <div class="error-count">{{ scope.row.count || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="异常信息" prop="msg" min-width="200" align="center" />
        <el-table-column label="堆栈跟踪" prop="traceback" min-width="300" align="center" />
      </el-table>
    </el-card>

    <!-- 失败统计 -->
    <el-card v-if="report_detail.failures_statistics?.length !== 0" class="data-card elegant-shadow">
      <div class="card-header">
        <div class="card-title-section">
          <i class="icon-failure"></i>
          <h3 class="card-title">失败统计</h3>
          <el-badge :value="report_detail.failures_statistics?.length || 0" type="warning" class="data-badge" />
        </div>
        <div class="card-subtitle">Failures Statistics</div>
      </div>
      
      <el-table 
        :data="report_detail.failures_statistics" 
        class="data-table"
        :show-overflow-tooltip="true"
        :header-row-style="getTableHeaderStyle"
      >
        <el-table-column label="失败次数" prop="occurrences" width="120" align="center">
          <template #default="scope">
            <div class="error-count">{{ scope.row.occurrences || 0 }}</div>
          </template>
        </el-table-column>
        <el-table-column label="请求类型" prop="method" width="120" align="center">
          <template #default="scope">
            <el-tag size="small" :type="getMethodType(scope.row.method)" effect="plain">
              {{ scope.row.method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="接口名称" prop="name" min-width="180" align="center" />
        <el-table-column label="错误信息" prop="error" min-width="250" align="center" />
      </el-table>
    </el-card>

    <!-- 图表区域 -->
    <div class="charts-container">
      <!-- 第一行：请求统计图表 -->
      <el-card class="chart-card elegant-shadow">
        <div class="chart-header">
          <div class="chart-title-section">
            <i class="icon-chart-request"></i>
            <h3 class="chart-title">每秒请求数统计</h3>
          </div>
          <div class="chart-subtitle">Total Requests Per Second</div>
        </div>
        <v-chart :option="requestOption" autoresize class="chart-content" />
      </el-card>

      <!-- 第二行：两个图表 -->
      <div class="chart-row two-col">
        <el-card class="chart-card elegant-shadow">
          <div class="chart-header">
            <div class="chart-title-section">
              <i class="icon-chart-response"></i>
              <h3 class="chart-title">响应时间统计</h3>
            </div>
            <div class="chart-subtitle">Response Times (ms)</div>
          </div>
          <v-chart :option="responseOption" autoresize class="chart-content" />
        </el-card>

        <el-card class="chart-card elegant-shadow">
          <div class="chart-header">
            <div class="chart-title-section">
              <i class="icon-chart-user"></i>
              <h3 class="chart-title">并发用户数统计</h3>
            </div>
            <div class="chart-subtitle">Number of Users</div>
          </div>
          <v-chart :option="userOption" autoresize class="chart-content" />
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { ArrowLeft } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

export default {
  data() {
    return {
      pollTimer: null,
      requestOption: {
        color: ['#52c41a', '#f5222d'],
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#94a3b8',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: 'var(--qm-line-strong)',
          textStyle: { color: '#94a3b8' },
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        xAxis: {
          type: 'time',
          axisLine: { lineStyle: { color: 'var(--qm-line-strong)' } },
          axisLabel: { color: 'var(--qm-text-2)' },
          splitLine: { lineStyle: { color: 'var(--qm-bg-3)' } }
        },
        yAxis: {
          type: 'value',
          name: '请求数/秒',
          axisLine: { lineStyle: { color: 'var(--qm-line-strong)' } },
          axisLabel: { color: 'var(--qm-text-2)' },
          splitLine: { lineStyle: { color: 'var(--qm-bg-3)' } }
        },
        legend: {
          show: true,
          data: ['RPS', '失败率'],
          top: 10,
          textStyle: { color: 'var(--qm-text-2)' }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        series: [
          {
            name: 'RPS',
            type: 'line',
            data: [],
            smooth: true,
            lineStyle: { width: 3 },
            symbolSize: 6,
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
                  { offset: 1, color: 'rgba(82, 196, 26, 0.05)' }
                ]
              }
            }
          },
          {
            name: '失败率',
            type: 'line',
            data: [],
            smooth: true,
            lineStyle: { width: 2, type: 'dashed' },
            symbolSize: 6
          }
        ]
      },
      responseOption: {
        color: ['#f59e0b', '#f97316', '#f59e0b'],
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#94a3b8',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: 'var(--qm-line-strong)',
          textStyle: { color: '#94a3b8' },
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        xAxis: {
          type: 'time',
          axisLine: { lineStyle: { color: 'var(--qm-line-strong)' } },
          axisLabel: { color: 'var(--qm-text-2)' },
          splitLine: { lineStyle: { color: 'var(--qm-bg-3)' } }
        },
        yAxis: {
          type: 'value',
          name: '响应时间(ms)',
          axisLine: { lineStyle: { color: 'var(--qm-line-strong)' } },
          axisLabel: { color: 'var(--qm-text-2)' },
          splitLine: { lineStyle: { color: 'var(--qm-bg-3)' } }
        },
        legend: {
          show: true,
          data: ['50%分位数', '95%分位数', '平均响应时间'],
          top: 10,
          textStyle: { color: 'var(--qm-text-2)' }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        series: [
          {
            name: '50%分位数',
            type: 'line',
            data: [],
            smooth: true,
            lineStyle: { width: 3 },
            symbolSize: 6
          },
          {
            name: '95%分位数',
            type: 'line',
            data: [],
            smooth: true,
            lineStyle: { width: 3 },
            symbolSize: 6
          },
          {
            name: '平均响应时间',
            type: 'line',
            data: [],
            smooth: true,
            lineStyle: { width: 2, type: 'dashed' },
            symbolSize: 6,
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(245, 158, 11, 0.3)' },
                  { offset: 1, color: 'rgba(245, 158, 11, 0.05)' }
                ]
              }
            }
          }
        ]
      },
      userOption: {
        color: ['#10b981'],
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#94a3b8',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: 'var(--qm-line-strong)',
          textStyle: { color: '#94a3b8' },
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        xAxis: {
          type: 'time',
          axisLine: { lineStyle: { color: 'var(--qm-line-strong)' } },
          axisLabel: { color: 'var(--qm-text-2)' },
          splitLine: { lineStyle: { color: 'var(--qm-bg-3)' } }
        },
        yAxis: {
          type: 'value',
          name: '用户数',
          axisLine: { lineStyle: { color: 'var(--qm-line-strong)' } },
          axisLabel: { color: 'var(--qm-text-2)' },
          splitLine: { lineStyle: { color: 'var(--qm-bg-3)' } }
        },
        legend: {
          show: true,
          data: ['并发用户数'],
          top: 10,
          textStyle: { color: 'var(--qm-text-2)' }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        series: [
          {
            name: '并发用户数',
            type: 'line',
            data: [],
            smooth: true,
            lineStyle: { width: 3 },
            symbolSize: 8,
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
                  { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }
                ]
              }
            }
          }
        ]
      },
      report_detail: {
        exceptions_statistics: [],
        failures_statistics: [],
        requests_statistics: [],
        response_time_statistics: []
      }
    }
  },
  components: {
    'v-chart': VChart
  },
  setup() {
    return {
      ArrowLeft
    }
  },
  computed: {
    ...mapState(['projectInfo', 'userInfo', 'pathPermission'])
  },
  methods: {
    goBack() {
      this.$router.back()
    },
    getTableHeaderStyle() {
      return {
        'font-weight': '600',
        'color': 'var(--qm-text-1)',
        'background-color': 'var(--qm-bg-1)',
        'border-bottom': '2px solid var(--qm-line-strong)'
      }
    },
    
    tableRowClassName({ row }) {
      return row.num_failures > 0 ? 'error-row' : ''
    },
    
    getMethodType(method) {
      const types = {
        'GET': 'success',
        'POST': 'primary',
        'PUT': 'warning',
        'DELETE': 'danger',
        'PATCH': 'info',
        'HEAD': 'info',
        'OPTIONS': 'info'
      }
      return types[method] || 'info'
    },
    
    getStatusType(status) {
      const types = {
        '运行中': 'success',
        '已完成': 'primary',
        '失败': 'danger',
        '停止': 'warning',
        '等待中': 'info'
      }
      return types[status] || 'info'
    },
    
    getCpuLevel(cpu) {
      if (!cpu) return 'info'
      if (cpu > 80) return 'danger'
      if (cpu > 60) return 'warning'
      return 'success'
    },
    
    getMemoryLevel(memory) {
      if (!memory) return 'info'
      // 假设内存阈值可以根据实际情况调整
      if (memory > 4096) return 'danger'
      if (memory > 2048) return 'warning'
      return 'success'
    },
    
    jumpCase(case_id) {
      this.$router.push({ path: '/resource/caseEdit', query: { id: case_id } })
    },
    
    startProgressPoll(reportId) {
      if (this.pollTimer) {
        clearInterval(this.pollTimer)
      }
      
      this.pollTimer = setInterval(async () => {
        try {
          const response = await this.$api.getLocustReport(reportId)
          if (response.status === 200) {
            this.updateChartData(response)
            
            if (this.report_detail.test_process !== 2) {
              this.stopProgressPoll()
              this.$message.success('压测完成！')
            }
          }
        } catch (error) {
          console.error('轮询失败:', error)
        }
      }, 2000)
    },
    
    stopProgressPoll() {
      if (this.pollTimer) {
        clearInterval(this.pollTimer)
        this.pollTimer = null
      }
    },
    
    updateChartData(response) {
      this.report_detail = { ...response.data.result }
      
      // 更新图表数据
      if (this.report_detail.history) {
        this.requestOption.xAxis.data = [...this.report_detail.history.x_time]
        this.requestOption.series[0].data = [...this.report_detail.history.y_rps]
        this.requestOption.series[1].data = [...this.report_detail.history.y_f_rps]
        
        this.responseOption.xAxis.data = [...this.report_detail.history.x_time]
        this.responseOption.series[0].data = [...this.report_detail.history.half_res_time]
        this.responseOption.series[1].data = [...this.report_detail.history.nine_five_res_time]
        this.responseOption.series[2].data = [...this.report_detail.history.avg_res_time]
        
        this.userOption.xAxis.data = [...this.report_detail.history.x_time]
        this.userOption.series[0].data = [...this.report_detail.history.user_count]
      }
    },

    async check_permission(){
			const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission['/report/locust']}
			const response = await this.$api.check_permission(params)
			if (response.status === 200){
			this.permission = { ...response.data.result }
			}
		},
    
    async getLocustReport() {
      const response = await this.$api.getLocustReport(this.$route.query.id)
      if (response.status === 200) {
        this.updateChartData(response)
        if (this.report_detail.test_process === 2) {
          this.startProgressPoll(this.$route.query.id)
        } else {
          this.stopProgressPoll()
        }
      }
    }
  },
  created() {
    this.check_permission()
    this.getLocustReport()
  },
  
  beforeUnmount() {
    this.stopProgressPoll()
  }
}
</script>

<style scoped>
.performance-report-container {
  width: 100%;
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  padding: 20px 5px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: calc(100vh - 75px);
}

/* 优雅阴影效果 */
.elegant-shadow {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06),
              0 1px 4px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 16px;
  background: var(--qm-bg-2);
  border: none;
}

.elegant-shadow:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1),
              0 2px 8px rgba(0, 0, 0, 0.12);
}

/* 报告标题卡片 */
.report-header-card {
  padding: 24px;
  margin-bottom: 10px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-left-section {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.report-title-section {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 10px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  color: var(--qm-text-2);
  font-weight: 500;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.back-btn:hover {
  background: var(--qm-bg-1);
  border-color: var(--qm-line-strong);
  transform: translateY(-1px);
}

.icon-report-header {
  display: inline-block;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border-radius: 10px;
  position: relative;
}

.icon-report-header::before {
  content: '';
  position: absolute;
  top: 7px;
  left: 7px;
  right: 7px;
  bottom: 7px;
  background: var(--qm-bg-2);
  border-radius: 5px;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

.report-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--qm-text-1);
}

.report-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 基本信息卡片 */
.info-card {
  padding: 24px;
}

.info-header {
  margin-bottom: 24px;
}

.info-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-info {
  display: inline-block;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 8px;
  position: relative;
}

.icon-info::before {
  content: '';
  position: absolute;
  top: 5px;
  left: 5px;
  right: 5px;
  bottom: 5px;
  background: var(--qm-bg-2);
  border-radius: 3px;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

.info-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--qm-text-1);
}

.info-content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--qm-text-2);
}

.icon-user,
.icon-env,
.icon-start-time,
.icon-end-time,
.icon-duration,
.icon-users,
.icon-rate,
.icon-cpu,
.icon-memory,
.icon-case,
.icon-link {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-user {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
}

.icon-env {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM5 19V5h14v14H5z'/%3E%3C/svg%3E");
}

.icon-start-time {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
}

.icon-end-time {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ef4444' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
}

.icon-duration {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%238b5cf6' d='M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z'/%3E%3C/svg%3E");
}

.icon-users {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z'/%3E%3C/svg%3E");
}

.icon-rate {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M13 6.06V3h-2v3.06c-4.5.5-8 4.31-8 8.93C3 16.1 3.9 17 5.01 17H8c0 2.21 1.79 4 4 4s4-1.79 4-4h2.99c1.11 0 2.01-.9 2.01-2.01 0-4.62-3.5-8.43-8-8.93zM12 19c-1.1 0-2-.9-2-2h4c0 1.1-.9 2-2 2zm0-4H5c0-3.86 3.14-7 7-7s7 3.14 7 7H12z'/%3E%3C/svg%3E");
}

.icon-cpu {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ef4444' d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z'/%3E%3C/svg%3E");
}

.icon-memory {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M15 9H9v6h6V9zm-2 4h-2v-2h2v2zm8-2V9h-2V7c0-1.1-.9-2-2-2h-2V3h-2v2h-2V3H9v2H7c-1.1 0-2 .9-2 2v2H3v2h2v2H3v2h2v2c0 1.1.9 2 2 2h2v2h2v-2h2v2h2v-2h2c1.1 0 2-.9 2-2v-2h2v-2h-2v-2h2zm-4 6H7V7h10v10z'/%3E%3C/svg%3E");
}

.icon-case {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
}

.icon-link {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z'/%3E%3C/svg%3E");
}

.info-value {
  font-size: 15px;
  color: var(--qm-text-1);
  font-weight: 500;
  padding: 10px 12px;
  background: var(--qm-bg-1);
  border-radius: 10px;
  border: 1px solid var(--qm-line-strong);
  transition: all 0.3s ease;
}

.info-value:hover {
  background: var(--qm-bg-2);
  border-color: var(--qm-line-strong);
}

.case-link {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

/* 数据卡片样式 */
.data-card {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--qm-line-strong);
}

.card-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-request,
.icon-response,
.icon-exception,
.icon-failure {
  display: inline-block;
  width: 24px;
  height: 24px;
  border-radius: 8px;
  position: relative;
}

.icon-request {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.icon-response {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.icon-exception {
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
}

.icon-failure {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.icon-request::before,
.icon-response::before,
.icon-exception::before,
.icon-failure::before {
  content: '';
  position: absolute;
  top: 6px;
  left: 6px;
  right: 6px;
  bottom: 6px;
  background: var(--qm-bg-2);
  border-radius: 4px;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--qm-text-1);
}

.card-subtitle {
  font-size: 14px;
  color: var(--qm-text-2);
  font-weight: 500;
}

.data-badge {
  margin-left: 8px;
}

/* 表格样式 */
.data-table {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
}

.data-table ::v-deep(.el-table__header-wrapper) {
  border-radius: 8px 8px 0 0;
}

.data-table ::v-deep(.el-table__body) {
  border-radius: 0 0 8px 8px;
}

.data-table ::v-deep(.el-table__row) {
  transition: all 0.3s ease;
}

.data-table ::v-deep(.el-table__row:hover) {
  background-color: var(--qm-bg-1);
}

.data-table ::v-deep(.error-row) {
  background-color: #fef2f2;
}

.data-table ::v-deep(.error-row:hover) {
  background-color: #fee2e2;
}

.number-value,
.time-value,
.size-value,
.rps-value,
.percentile-value,
.error-count {
  font-weight: 600;
  font-family: 'Consolas', 'Monaco', monospace;
}

.number-value { color: #f59e0b; }
.time-value { color: #10b981; }
.size-value { color: #f97316; }
.rps-value { color: #f59e0b; }
.percentile-value { color: var(--qm-text-2); }
.error-count { color: #ef4444; }

/* 图表容器 */
.charts-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-card {
  padding: 24px;
  overflow: hidden;
  height: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.chart-card ::v-deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.chart-header {
  margin-bottom: 20px;
}

.chart-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.icon-chart-request,
.icon-chart-response,
.icon-chart-user {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-chart-request {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2352c41a' d='M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z'/%3E%3C/svg%3E");
}

.icon-chart-response {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z'/%3E%3C/svg%3E");
}

.icon-chart-user {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z'/%3E%3C/svg%3E");
}

.chart-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--qm-text-1);
}

.chart-subtitle {
  font-size: 14px;
  color: var(--qm-text-2);
  margin-left: 32px;
}

.chart-content {
  flex: 1;
  min-height: 320px;
  max-height: 400px;
  overflow: hidden;
}

/* 图表行布局 */
.chart-row {
  display: grid;
  gap: 20px;
  width: 100%;
  align-items: stretch;
}

.chart-row.two-col {
  grid-template-columns: repeat(2, 1fr);
}

.chart-row .chart-card {
  height: 100%;
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.report-header-card {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.info-card {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
}

.data-card:nth-of-type(1) {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both;
}

.data-card:nth-of-type(2) {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.3s both;
}

.data-card:nth-of-type(3) {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.4s both;
}

.data-card:nth-of-type(4) {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.5s both;
}

.charts-container > .chart-card:nth-of-type(1) {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.6s both;
}

.chart-row {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.7s both;
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .info-content-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart-row.two-col {
    grid-template-columns: 1fr;
  }
}

@media screen and (max-width: 768px) {
  .performance-report-container {
    padding: 12px;
  }
  
  .info-content-grid {
    grid-template-columns: 1fr;
  }
  
  .report-left-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .report-title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .data-table ::v-deep(.el-table__body-wrapper),
  .data-table ::v-deep(.el-table__header-wrapper) {
    overflow-x: auto;
  }

  .data-table ::v-deep(.el-table) {
    min-width: 1200px;
  }
}

/* 加载状态 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: var(--qm-bg-2);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.loading-content {
  text-align: center;
}

.loading-text {
  margin-top: 16px;
  color: var(--qm-text-2);
  font-size: 14px;
}
</style>