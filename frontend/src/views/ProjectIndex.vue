<template>
  <div class="project-dashboard-container">
    <!-- 项目信息区域 -->
    <div class="top-info-section">
      <el-card class="info-card elegant-shadow">
        <div class="info-header">
          <div class="info-title-section">
            <i class="icon-project"></i>
            <h3 class="info-title">项目基本信息</h3>
            <el-tag size="small" type="primary" effect="plain">项目概览</el-tag>
          </div>
        </div>
        
        <div class="info-content-compact">
          <div class="info-compact-grid">
            <div class="compact-item">
              <div class="compact-label">
                <i class="icon-name"></i>
                <span class="compact-label-text">项目名称</span>
              </div>
              <div class="compact-value">{{ projectDetail.name }}</div>
            </div>
            
            <div class="compact-item">
              <div class="compact-label">
                <i class="icon-creator"></i>
                <span class="compact-label-text">创建人</span>
              </div>
              <div class="compact-value">{{ projectDetail.create_by_name }}</div>
            </div>
            
            <div class="compact-item">
              <div class="compact-label">
                <i class="icon-updater"></i>
                <span class="compact-label-text">更新人</span>
              </div>
              <div class="compact-value">{{ projectDetail.update_by_name }}</div>
            </div>
            
            <div class="compact-item">
              <div class="compact-label">
                <i class="icon-time"></i>
                <span class="compact-label-text">创建时间</span>
              </div>
              <div class="compact-value">{{ formatTime(projectDetail.create_time) }}</div>
            </div>
            
            <div class="compact-item">
              <div class="compact-label">
                <i class="icon-time"></i>
                <span class="compact-label-text">更新时间</span>
              </div>
              <div class="compact-value">{{ formatTime(projectDetail.update_time) }}</div>
            </div>
    
          </div>
          
          <div class="info-full-row">
            <div class="info-full-item">
              <div class="compact-label">
                <i class="icon-desc"></i>
                <span class="compact-label-text">项目描述</span>
              </div>
              <div class="compact-value desc-value">{{ projectDetail.desc || '暂无描述' }}</div>
            </div>
          </div>
          
        </div>
      </el-card>
      
      <el-card class="members-card elegant-shadow">
        <div class="members-header">
          <div class="members-title-section">
            <i class="icon-members"></i>
            <h3 class="members-title">项目成员</h3>
            <el-badge :value="projectDetail.user_names?.length || 0" type="primary" class="member-badge" />
          </div>
        </div>
        
        <div class="members-list">
          <div v-for="item in projectDetail.user_names" :key="item.id" class="member-item">
            <el-avatar :size="40" :src="item.avatar" class="member-avatar">
              {{ item.username?.charAt(0) }}
            </el-avatar>
            <div class="member-info">
              <span class="member-name">{{ item.username }}</span>
              <span v-if="item.role" class="member-role">{{ item.role }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 数据统计看板 -->
    <el-card class="dashboard-card elegant-shadow">
      <div class="dashboard-header">
        <div class="dashboard-title-section">
          <i class="icon-dashboard"></i>
          <h3 class="dashboard-title">数据看板</h3>
          <el-tag size="small" type="success" effect="plain">实时数据</el-tag>
        </div>
      </div>
      
      <div class="dashboard-stats">
        <div class="stats-grid">
		  
          <div class="stat-item" @click="$router.push({name: 'env'})">
            <div class="stat-icon env-icon">
              <i class="icon-env"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ projectDetail.env_number || 0 }}</div>
              <div class="stat-label">环境个数</div>
            </div>
          </div>
          
          <div class="stat-item" @click="$router.push({name: 'service'})">
            <div class="stat-icon service-icon">
              <i class="icon-service"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ projectDetail.service_number || 0 }}</div>
              <div class="stat-label">服务个数</div>
            </div>
          </div>
          
          <div class="stat-item" @click="$router.push({name: 'plant'})">
            <div class="stat-icon plant-icon">
              <i class="icon-plant"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ projectDetail.plant_number || 0 }}</div>
              <div class="stat-label">产品个数</div>
            </div>
          </div>
		  
		  <div class="stat-item" @click="$router.push({name: 'db'})">
		    <div class="stat-icon module-icon">
		      <i class="icon-module"></i>
		    </div>
		    <div class="stat-content">
		      <div class="stat-value">{{ projectDetail.db_number || 0 }}</div>
		      <div class="stat-label">数据库个数</div>
		    </div>
		  </div>
          
          <div class="stat-item" @click="$router.push({name: 'file'})">
            <div class="stat-icon page-icon">
              <i class="icon-page"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ projectDetail.file_number || 0 }}</div>
              <div class="stat-label">文件个数</div>
            </div>
          </div>
          
          <div class="stat-item" @click="$router.push({name: 'element'})">
            <div class="stat-icon element-icon">
              <i class="icon-element"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ projectDetail.element_number || 0 }}</div>
              <div class="stat-label">元素个数</div>
            </div>
          </div>
          
          <div class="stat-item" @click="$router.push({name: 'step'})">
            <div class="stat-icon step-icon">
              <i class="icon-step"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ projectDetail.step_number || 0 }}</div>
              <div class="stat-label">步骤个数</div>
            </div>
          </div>
          
          <div class="stat-item" @click="$router.push({name: 'tag'})">
            <div class="stat-icon tag-icon">
              <i class="icon-tag"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ projectDetail.tag_number || 0 }}</div>
              <div class="stat-label">标签个数</div>
            </div>
          </div>
          
          <div class="stat-item" @click="$router.push({name: 'suite'})">
            <div class="stat-icon suite-icon">
              <i class="icon-suite"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ projectDetail.suite_number || 0 }}</div>
              <div class="stat-label">计划个数</div>
            </div>
          </div>
          
          <div class="stat-item" @click="$router.push({name: 'python'})">
            <div class="stat-icon script-icon">
              <i class="icon-script"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ projectDetail.script_number || 0 }}</div>
              <div class="stat-label">函数个数</div>
            </div>
          </div>
          
          <div class="stat-item" @click="$router.push({name: 'report'})">
            <div class="stat-icon report-icon">
              <i class="icon-report"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ projectDetail.report_number || 0 }}</div>
              <div class="stat-label">功能报告</div>
            </div>
          </div>
          
          <div class="stat-item" @click="$router.push({name: 'reportlocust'})">
            <div class="stat-icon perf-report-icon">
              <i class="icon-perf-report"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ projectDetail.p_report_number || 0 }}</div>
              <div class="stat-label">性能报告</div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 测试报告历史趋势图 -->
    <el-card class="chart-card elegant-shadow">
      <div class="chart-header">
        <div class="chart-title-section">
          <i class="icon-trend"></i>
          <h3 class="chart-title">测试报告历史趋势图</h3>
        </div>
      </div>
      <v-chart :option="suiteResultOption" autoresize class="chart-content" />
    </el-card>
	
    <div class="chart-row two-col">
      <el-card class="chart-card elegant-shadow">
        <div class="chart-header">
          <div class="chart-title-section">
            <i class="icon-api"></i>
            <h3 class="chart-title">接口类型分布</h3>
          </div>
        </div>
        <v-chart :option="apiOption" autoresize class="chart-content" />
      </el-card>
      
      <el-card class="chart-card elegant-shadow">
        <div class="chart-header">
          <div class="chart-title-section">
            <i class="icon-server"></i>
            <h3 class="chart-title">接口所属服务数量统计</h3>
          </div>
        </div>
        <v-chart :option="serverOption" autoresize class="chart-content" />
      </el-card>
    </div>

    <!-- 第三行：2个图表（各占50%） -->
    <div class="chart-row two-col">
      <el-card class="chart-card elegant-shadow">
        <div class="chart-header">
          <div class="chart-title-section">
            <i class="icon-tag-chart-script"></i>
            <h3 class="chart-title">脚本用例各标签数量统计</h3>
          </div>
        </div>
        <v-chart :option="caseTagOption" autoresize class="chart-content" />
      </el-card>
      
      <el-card class="chart-card elegant-shadow">
        <div class="chart-header">
          <div class="chart-title-section">
            <i class="icon-tag-chart-func"></i>
            <h3 class="chart-title">功能用例各标签数量统计</h3>
          </div>
        </div>
        <v-chart :option="fCaseTagOption" autoresize class="chart-content" />
      </el-card>
    </div>

    <!-- 数据分析图表区域 -->
    <div class="charts-container">
      <!-- 第一行：3个图表 -->
      <div class="chart-row three-col">
        <el-card class="chart-card elegant-shadow">
          <div class="chart-header">
            <div class="chart-title-section">
              <i class="icon-api-coverage"></i>
              <h3 class="chart-title">接口自动化覆盖率</h3>
            </div>
          </div>
          <v-chart :option="apiCoverageOption" autoresize class="chart-content" />
        </el-card>
        
        <el-card class="chart-card elegant-shadow">
          <div class="chart-header">
            <div class="chart-title-section">
              <i class="icon-func-coverage"></i>
              <h3 class="chart-title">功能用例自动化覆盖率</h3>
            </div>
          </div>
          <v-chart :option="caseCoverageOption" autoresize class="chart-content" />
        </el-card>
        
        <el-card class="chart-card elegant-shadow">
          <div class="chart-header">
            <div class="chart-title-section">
              <i class="icon-test-type"></i>
              <h3 class="chart-title">功能用例和脚本用例占比图</h3>
            </div>
          </div>
          <v-chart :option="testOption" autoresize class="chart-content" />
        </el-card>
      </div>
	  
      <div class="chart-row three-col">
        <el-card class="chart-card elegant-shadow">
          <div class="chart-header">
            <div class="chart-title-section">
              <i class="icon-test-result"></i>
              <h3 class="chart-title">脚本用例最近测试结果分布</h3>
            </div>
          </div>
          <v-chart :option="testResultOption" autoresize class="chart-content" />
        </el-card>
        
        <el-card class="chart-card elegant-shadow">
          <div class="chart-header">
            <div class="chart-title-section">
              <i class="icon-test-detail"></i>
              <h3 class="chart-title">脚本用例类型分布图</h3>
            </div>
          </div>
          <v-chart :option="testTypeOption" autoresize class="chart-content" />
        </el-card>
        
        <el-card class="chart-card elegant-shadow">
          <div class="chart-header">
            <div class="chart-title-section">
              <i class="icon-test-count"></i>
              <h3 class="chart-title">测试用例数量统计</h3>
            </div>
          </div>
          <v-chart :option="testCountOption" autoresize class="chart-content" />
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

use([
  CanvasRenderer,
  PieChart,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

export default {
  data() {
    return {
      projectDetail: {
        case_info: {},
        user_names: []
      },
      suiteResultOption: {
        color: ['#52c41a', '#f5222d', '#a8071a'],
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#1a1a1a',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' }
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: ['1', '2', '3'],
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: { color: '#64748b' }
        },
        yAxis: {
          type: 'value',
          name: '百分比(%)',
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: { color: '#64748b' },
          splitLine: { lineStyle: { color: '#f1f5f9' } }
        },
        legend: {
          show: true,
          data: ['成功率', '失败率', '错误率'],
          top: 10,
          textStyle: { color: '#64748b' }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        series: [
          {
            name: '成功率',
            type: 'line',
            data: [],
            smooth: true,
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
                  { offset: 1, color: 'rgba(82, 196, 26, 0.05)' }
                ]
              }
            },
            lineStyle: { width: 3 },
            symbolSize: 8
          },
          {
            name: '失败率',
            type: 'line',
            data: [],
            smooth: true,
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(245, 34, 45, 0.3)' },
                  { offset: 1, color: 'rgba(245, 34, 45, 0.05)' }
                ]
              }
            },
            lineStyle: { width: 3 },
            symbolSize: 8
          },
          {
            name: '错误率',
            type: 'line',
            data: [],
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(168, 7, 26, 0.3)' },
                  { offset: 1, color: 'rgba(168, 7, 26, 0.05)' }
                ]
              }
            },
            smooth: true,
            lineStyle: { width: 3 },
            symbolSize: 8
          }
        ]
      },
      caseTagOption: {
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#1a1a1a',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' },
          formatter: '{b}: {c}'
        },
        xAxis: {
          type: 'category',
          data: [],
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: {
            rotate: 45,
            interval: 0,
            textStyle: { 
              fontSize: 12,
              color: '#64748b'
            }
          }
        },
        yAxis: {
          type: 'value',
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: { color: '#64748b' },
          splitLine: { lineStyle: { color: '#f1f5f9' } }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        series: [
          {
            data: [],
            type: 'bar',
            barMaxWidth: 40, // 限制柱子最大宽度
            itemStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: '#3b82f6' },
                  { offset: 1, color: '#1d4ed8' }
                ]
              },
              borderRadius: [6, 6, 0, 0]
            },
            barWidth: '60%'
          }
        ]
      },
      fCaseTagOption: {
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#1a1a1a',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' },
          formatter: '{b}: {c}'
        },
        xAxis: {
          type: 'category',
          data: [],
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: {
            rotate: 45,
            interval: 0,
            textStyle: { 
              fontSize: 12,
              color: '#64748b'
            }
          }
        },
        yAxis: {
          type: 'value',
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: { color: '#64748b' },
          splitLine: { lineStyle: { color: '#f1f5f9' } }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        series: [
          {
            data: [],
            type: 'bar',
            barMaxWidth: 40, // 限制柱子最大宽度
            itemStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: '#8b5cf6' },
                  { offset: 1, color: '#6d28d9' }
                ]
              },
              borderRadius: [6, 6, 0, 0]
            },
            barWidth: '60%'
          }
        ]
      },
      serverOption: {
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#1a1a1a',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' },
          formatter: '{b}: {c}'
        },
        xAxis: {
          type: 'category',
          data: [],
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: {
            rotate: 45,
            interval: 0,
            textStyle: { 
              fontSize: 12,
              color: '#64748b'
            }
          }
        },
        yAxis: {
          type: 'value',
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: { color: '#64748b' },
          splitLine: { lineStyle: { color: '#f1f5f9' } }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        series: [
          {
            data: [],
            type: 'bar',
            barMaxWidth: 40, // 限制柱子最大宽度
            itemStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: '#10b981' },
                  { offset: 1, color: '#059669' }
                ]
              },
              borderRadius: [6, 6, 0, 0]
            },
            barWidth: '60%'
          }
        ]
      },
      testCountOption: {
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#1a1a1a',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' },
          formatter: '{b}: {c}'
        },
        xAxis: {
          type: 'category',
          data: [],
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: {
            color: '#64748b',
            rotate: 45,
            interval: 0,
            overflow: 'break',
            width: 80
          }
        },
        yAxis: {
          type: 'value',
          name: '数量',
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: { color: '#64748b' },
          splitLine: { lineStyle: { color: '#f1f5f9' } }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '0%', // 改为4%
          containLabel: true
        },
        series: [
          {
            data: [],
            type: 'bar',
            itemStyle: {
              color: function(params) {
                const colorList = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
                return colorList[params.dataIndex % colorList.length]
              },
              borderRadius: [6, 6, 0, 0]
            },
            barWidth: '60%'
          }
        ]
      },
      apiOption: {
        color: ['#f59e0b', '#3b82f6', '#10b981', '#ef4444', '#8b5cf6', '#ec4899', '#64748b'],
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#1a1a1a',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' },
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          top: 'center',
          data: ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH'],
          textStyle: { color: '#64748b' }
        },
        series: [
          {
            name: '',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['60%', '50%'],
            data: [],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            itemStyle: {
              borderRadius: 8,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              color: '#64748b',
              formatter: '{b}: {d}%'
            }
          }
        ]
      },
      caseCoverageOption: {
        color: ['#10b981', '#e2e8f0'],
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#1a1a1a',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' },
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',      // 改为水平
          left: 'center',
          bottom: 0,                // 放在底部
          data: ['已覆盖', '未覆盖'],
          textStyle: { color: '#64748b' }
        },
        series: [
          {
            name: '',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '50%'],
            data: [],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            itemStyle: {
              borderRadius: 8,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              color: '#64748b',
              formatter: '{b}: {d}%'
            }
          }
        ]
      },
      apiCoverageOption: {
        color: ['#3b82f6', '#e2e8f0'],
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#1a1a1a',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' },
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',      // 改为水平
          left: 'center',
          bottom: 0,                // 放在底部
          data: ['已覆盖', '未覆盖'],
          textStyle: { color: '#64748b' }
        },
        series: [
          {
            name: '',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '50%'],
            data: [],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            itemStyle: {
              borderRadius: 8,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              color: '#64748b',
              formatter: '{b}: {d}%'
            }
          }
        ]
      },
      testOption: {
        color: ['#3b82f6', '#f59e0b'],
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#1a1a1a',
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' },
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',      // 改为水平
          left: 'center',
          bottom: 0,                // 放在底部
          data: ['功能用例', '脚本用例'],
          textStyle: { color: '#64748b' }
        },
        series: [
          {
            name: '',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '50%'],
            data: [],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            itemStyle: {
              borderRadius: 8,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              color: '#64748b',
              formatter: '{b}: {d}%'
            }
          }
        ]
      },
      testTypeOption: {
        color: ['#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#ec4899'],
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#1a1a1a',
            fontSize: 14,
            fontWeight: 'bold',
            overflow: 'break',
            width: '100%'
          }
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' },
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',      // 改为水平
          left: 'center',
          bottom: 10,                // 放在底部
          data: ['接口用例数', 'WEB用例数', 'APP用例数', '造数用例数', '性能用例数'],
          textStyle: { color: '#64748b' },
          itemWidth: 25,
          itemHeight: 14
        },
        series: [
          {
            name: '',
            type: 'pie',
            radius: ['35%', '60%'],   // 调整半径
            center: ['50%', '45%'],    // 向上移动
            data: [],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            itemStyle: {
              borderRadius: 8,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              color: '#64748b',
              formatter: '{b}: {d}%',
              fontSize: 11            // 稍微减小标签字体
            }
          }
        ]
      },
      testResultOption: {
        color: ['#52c41a', '#f5222d', '#a8071a', '#94a3b8'],
        
		title: {
		  text: '',
		  left: 'center',
		  textStyle: {
		    color: '#1a1a1a',
		    fontSize: 14,
		    fontWeight: 'bold',
		    overflow: 'break',
		    width: '100%'
		  }
		},
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' },
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',      // 改为水平
		  left: 'center',
		  bottom: 0,                // 放在底部
          data: ['成功', '失败', '错误', '未执行'],
          textStyle: { color: '#64748b' }
        },
        series: [
          {
            name: '',
            type: 'pie',
            radius: ['35%', '60%'],   // 调整半径
            center: ['50%', '45%'],    // 向上移动
            data: [],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            itemStyle: {
              borderRadius: 8,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              color: '#64748b',
              formatter: '{b}: {d}%'
            }
          }
        ]
      }
    }
  },
  components: {
    'v-chart': VChart
  },
  computed: {
    ...mapState(['projectInfo'])
  },
  methods: {
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
    
    async getProject() {
      const response = await this.$api.getProject(this.projectInfo.id)
      if (response.status === 200) {
        this.projectDetail = { ...response.data.result }
        
        // 更新图表数据
        this.testOption.series[0].data = [...this.projectDetail.case_info.test_case_type]
        this.testTypeOption.series[0].data = [...this.projectDetail.case_info.case_type]
        this.testResultOption.series[0].data = [...this.projectDetail.recent_test_result]
        this.apiOption.series[0].data = [...this.projectDetail.api_info.api_type]
        this.apiCoverageOption.series[0].data = [...this.projectDetail.api_info.api_coverage_type]
        this.caseCoverageOption.series[0].data = [...this.projectDetail.case_info.func_case_autoed_persent]
        this.serverOption.xAxis.data = [...this.projectDetail.api_info.services]
        this.serverOption.series[0].data = [...this.projectDetail.api_info.service_count]
        this.testCountOption.xAxis.data = [...this.projectDetail.case_info.name]
        this.testCountOption.series[0].data = [...this.projectDetail.case_info.count]
        this.caseTagOption.xAxis.data = [...this.projectDetail.tag_info.tag_names]
        this.caseTagOption.series[0].data = [...this.projectDetail.tag_info.tag_count]
        this.fCaseTagOption.xAxis.data = [...this.projectDetail.tag_info.f_tag_names]
        this.fCaseTagOption.series[0].data = [...this.projectDetail.tag_info.f_tag_count]
        this.suiteResultOption.xAxis.data = [...this.projectDetail.suite_info.x_data]
        this.suiteResultOption.series[0].data = [...this.projectDetail.suite_info.s_data]
        this.suiteResultOption.series[1].data = [...this.projectDetail.suite_info.f_data]
        this.suiteResultOption.series[2].data = [...this.projectDetail.suite_info.e_data]
      }
    }
  },
  created() {
    this.getProject()
  }
}
</script>

<style scoped>
.project-dashboard-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 15px;
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
  background: white;
  border: none;
}

.elegant-shadow:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1),
              0 2px 8px rgba(0, 0, 0, 0.12);
}

/* 顶部信息区域 */
.top-info-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

/* 项目信息卡片 */
.info-card {
  padding: 20px;
}

.info-header {
  margin-bottom: 20px;
}

.info-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-project {
  display: inline-block;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 8px;
  position: relative;
}

.icon-project::before {
  content: '';
  position: absolute;
  top: 6px;
  left: 6px;
  right: 6px;
  bottom: 6px;
  background: white;
  border-radius: 4px;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

.info-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

/* 紧凑型信息布局 */
.info-content-compact {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-compact-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.compact-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-full-row {
  margin-top: 8px;
}

.info-full-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.compact-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-name,
.icon-creator,
.icon-updater,
.icon-time,
.icon-message,
.icon-desc,
.icon-url {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-name {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V6h16v12zM6 10h2v2H6v-2zm0 4h8v2H6v-2zm10 0h2v2h-2v-2zm-6-4h8v2h-8v-2z'/%3E%3C/svg%3E");
}

.icon-creator {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
}

.icon-updater {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E");
}

.icon-time {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
}

.icon-message {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%238b5cf6' d='M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12zm-9-4h2v2h-2zm0-6h2v4h-2z'/%3E%3C/svg%3E");
}

.icon-desc {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ef4444' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
}

.icon-url {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ec4899' d='M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z'/%3E%3C/svg%3E");
}

.compact-label-text {
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
}

.compact-value {
  font-size: 14px;
  color: #1a1a1a;
  font-weight: 500;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.compact-value:hover {
  background: white;
  border-color: #cbd5e1;
}

.desc-value,
.url-value {
  word-break: break-all;
  border-left: 3px solid #3b82f6;
  background: #f0f7ff;
}

.url-value {
  border-left-color: #10b981;
}

/* 成员卡片 */
.members-card {
  padding: 20px;
}

.members-header {
  margin-bottom: 20px;
}

.members-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-members {
  display: inline-block;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border-radius: 8px;
  position: relative;
}

.icon-members::before {
  content: '';
  position: absolute;
  top: 6px;
  left: 6px;
  right: 6px;
  bottom: 6px;
  background: white;
  border-radius: 50%;
}

.icon-members::after {
  content: '';
  position: absolute;
  top: 4px;
  left: 4px;
  right: 4px;
  bottom: 4px;
  border: 2px solid white;
  border-radius: 50%;
}

.members-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.member-badge {
  margin-left: auto;
}

.members-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 8px;
}

.members-list::-webkit-scrollbar {
  width: 6px;
}

.members-list::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.members-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.members-list::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  cursor: pointer;
}

.member-item:hover {
  background: white;
  border-color: #cbd5e1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.member-avatar {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  font-weight: 600;
}

.member-info {
  display: flex;
  flex-direction: column;
}

.member-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.member-role {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

/* 数据看板卡片 */
.dashboard-card {
  padding: 24px;
}

.dashboard-header {
  margin-bottom: 24px;
}

.dashboard-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-dashboard {
  display: inline-block;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 8px;
  position: relative;
}

.icon-dashboard::before {
  content: '';
  position: absolute;
  top: 5px;
  left: 5px;
  right: 5px;
  bottom: 5px;
  background: white;
  border-radius: 4px;
}

.icon-dashboard::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  right: 3px;
  bottom: 3px;
  border: 2px solid white;
  border-radius: 4px;
}

.dashboard-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

/* 统计网格 */
.dashboard-stats {
  margin: 0 -8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-item:hover {
  background: white;
  border-color: #cbd5e1;
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.env-icon { background: linear-gradient(135deg, #61a0a8 0%, #2a7b88 100%); }
.service-icon { background: linear-gradient(135deg, #409eff 0%, #1d4ed8 100%); }
.plant-icon { background: linear-gradient(135deg, #6e7079 0%, #4b5563 100%); }
.module-icon { background: linear-gradient(135deg, #ea7ccc 0%, #d946ef 100%); }
.page-icon { background: linear-gradient(135deg, #9a60b4 0%, #7c3aed 100%); }
.element-icon { background: linear-gradient(135deg, #fc8452 0%, #f97316 100%); }
.step-icon { background: linear-gradient(135deg, #3ba272 0%, #16a34a 100%); }
.tag-icon { background: linear-gradient(135deg, #73c0de 0%, #0ea5e9 100%); }
.suite-icon { background: linear-gradient(135deg, #ee6666 0%, #dc2626 100%); }
.script-icon { background: linear-gradient(135deg, #fac858 0%, #f59e0b 100%); }
.report-icon { background: linear-gradient(135deg, #91cc75 0%, #22c55e 100%); }
.perf-report-icon { background: linear-gradient(135deg, #5470c6 0%, #3b82f6 100%); }

.icon-env,
.icon-service,
.icon-plant,
.icon-module,
.icon-page,
.icon-element,
.icon-step,
.icon-tag,
.icon-suite,
.icon-script,
.icon-report,
.icon-perf-report {
  width: 24px;
  height: 24px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  filter: brightness(0) invert(1);
}

.icon-env { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM5 19V5h14v14H5z'/%3E%3C/svg%3E"); }
.icon-service { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M2 2v20h20V2H2zm9 16H5v-2h6v2zm0-4H5v-2h6v2zm0-4H5V8h6v2zm4 8h-2v-2h2v2zm0-4h-2v-2h2v2zm0-4h-2V8h2v2z'/%3E%3C/svg%3E"); }
.icon-plant { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M19 5v14H5V5h14m0-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z'/%3E%3C/svg%3E"); }
.icon-module { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M4 8h4V4H4v4zm6 12h4v-4h-4v4zm-6 0h4v-4H4v4zm0-6h4v-4H4v4zm6 0h4v-4h-4v4zm6-10v4h4V4h-4zm-6 4h4V4h-4v4zm6 6h4v-4h-4v4zm0 6h4v-4h-4v4z'/%3E%3C/svg%3E"); }
.icon-page { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z'/%3E%3C/svg%3E"); }
.icon-element { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z'/%3E%3C/svg%3E"); }
.icon-step { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/%3E%3C/svg%3E"); }
.icon-tag { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M20 10V8h-4V4h-2v4h-4V4H8v4H4v2h4v4H4v2h4v4h2v-4h4v4h2v-4h4v-2h-4v-4h4zm-6 4h-4v-4h4v4z'/%3E%3C/svg%3E"); }
.icon-suite { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z'/%3E%3C/svg%3E"); }
.icon-script { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z'/%3E%3C/svg%3E"); }
.icon-report { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4-2h2v12h-2z'/%3E%3C/svg%3E"); }
.icon-perf-report { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z'/%3E%3C/svg%3E"); }

/* 新增独立图标 */
.icon-tag-chart-script,
.icon-tag-chart-func,
.icon-api-coverage,
.icon-func-coverage {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-tag-chart-script {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z'/%3E%3C/svg%3E");
}

.icon-tag-chart-func {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%238b5cf6' d='M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z'/%3E%3C/svg%3E");
}

.icon-api-coverage {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M14 12l-2 2-2-2 2-2 2 2zm-2-6l2.12 2.12 2.5-2.5L12 1 7.38 5.62l2.5 2.5L12 6zm-6 6l2.12-2.12-2.5-2.5L1 12l4.62 4.62 2.5-2.5L6 12zm12 0l-2.12 2.12 2.5 2.5L23 12l-4.62-4.62-2.5 2.5L18 12zm-6 6l-2.12-2.12-2.5 2.5L12 23l4.62-4.62-2.5-2.5L12 18z'/%3E%3C/svg%3E");
}

.icon-func-coverage {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ec4899' d='M14 12l-2 2-2-2 2-2 2 2zm-2-6l2.12 2.12 2.5-2.5L12 1 7.38 5.62l2.5 2.5L12 6zm-6 6l2.12-2.12-2.5-2.5L1 12l4.62 4.62 2.5-2.5L6 12zm12 0l-2.12 2.12 2.5 2.5L23 12l-4.62-4.62-2.5 2.5L18 12zm-6 6l-2.12-2.12-2.5 2.5L12 23l4.62-4.62-2.5-2.5L12 18z'/%3E%3C/svg%3E");
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
}

/* 图表区域 */
.chart-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  margin: 0 !important;
}

.chart-header {
  margin-bottom: 16px;
}

.chart-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.icon-trend,
.icon-server,
.icon-api,
.icon-test-result,
.icon-test-type,
.icon-test-detail,
.icon-test-count,
.icon-tag-chart-script,
.icon-tag-chart-func,
.icon-api-coverage,
.icon-func-coverage {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-trend { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z'/%3E%3C/svg%3E"); }
.icon-server { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M20 13H4c-.55 0-1 .45-1 1v6c0 .55.45 1 1 1h16c.55 0 1-.45 1-1v-6c0-.55-.45-1-1-1zM7 19c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zM20 3H4c-.55 0-1 .45-1 1v6c0 .55.45 1 1 1h16c.55 0 1-.45 1-1V4c0-.55-.45-1-1-1zM7 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z'/%3E%3C/svg%3E"); }
.icon-api { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M14 12l-2 2-2-2 2-2 2 2zm-2-6l2.12 2.12 2.5-2.5L12 1 7.38 5.62l2.5 2.5L12 6zm-6 6l2.12-2.12-2.5-2.5L1 12l4.62 4.62 2.5-2.5L6 12zm12 0l-2.12 2.12 2.5 2.5L23 12l-4.62-4.62-2.5 2.5L18 12zm-6 6l-2.12-2.12-2.5 2.5L12 23l4.62-4.62-2.5-2.5L12 18z'/%3E%3C/svg%3E"); }
.icon-test-result { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2352c41a' d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/%3E%3C/svg%3E"); }
.icon-test-type { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%238b5cf6' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z'/%3E%3C/svg%3E"); }
.icon-test-detail { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ef4444' d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4-2h2v12h-2z'/%3E%3C/svg%3E"); }
.icon-test-count { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V6h5.17l2 2H20v10zm-8-4h2v2h2v-2h2v-2h-2v-2h-2v2h-2z'/%3E%3C/svg%3E"); }

.chart-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  white-space: normal;
  word-break: break-word;
  line-height: 1.4;
}

.chart-content {
  flex: 1;
  min-height: 280px;
  max-height: 280px;
}

/* 图表容器 */
.charts-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-row {
  display: grid;
  gap: 20px;
  width: 100%;
}

/* 两列布局 */
.chart-row.two-col {
  grid-template-columns: 1fr 1fr;
}

/* 三列布局 */
.chart-row.three-col {
  grid-template-columns: repeat(3, 1fr);
}

/* 响应式设计 */
@media screen and (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .chart-row.three-col {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media screen and (max-width: 1200px) {
  .top-info-section {
    grid-template-columns: 1fr;
  }
  
  .info-compact-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media screen and (max-width: 992px) {
  .project-dashboard-container {
    padding: 12px;
  }
  
  .info-card,
  .members-card,
  .dashboard-card,
  .chart-card {
    padding: 16px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart-row.two-col,
  .chart-row.three-col {
    grid-template-columns: 1fr;
  }
}

@media screen and (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .info-compact-grid {
    grid-template-columns: 1fr;
  }
  
  .members-list {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
  
  .chart-content {
    min-height: 240px;
  }
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

.info-card {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.members-card {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
}

.dashboard-card {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both;
}

.chart-card {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.3s both;
}

.charts-container .chart-row:nth-child(1) {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.4s both;
}

.charts-container .chart-row:nth-child(2) {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.5s both;
}

.charts-container .chart-row:nth-child(3) {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.6s both;
}
</style>