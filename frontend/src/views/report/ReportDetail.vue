<template>
  <el-dialog v-model="lookLogVisible" direction="rtl" :show-close="true"  destroy-on-close fullscreen >
    <template #header="{ close, titleId, titleClass }">
      <h4>{{ this.one_case_log.case_name }}</h4>
    </template>
    <div>
      <el-collapse v-model="caseActive" accordion>
        <el-collapse-item :name="case_index">
          <template #title>
            <div class="case-header-info">
              <el-text v-if="one_case_log.result_value === '成功'" type="success">
                【用例执行人: {{ one_case_log.create_by_name }}】【用例执行环境: {{ one_case_log.env_name }}】【用例花费时间: {{one_case_log.time.toFixed(2)}}秒】【用例执行结果: {{one_case_log.result_value}}】
              </el-text>
              <el-text v-if="one_case_log.result_value === '失败'" type="danger">
                【用例执行人: {{ one_case_log.create_by_name }}】【用例执行环境: {{ one_case_log.env_name }}】【用例花费时间: {{one_case_log.time.toFixed(2)}}秒】【用例执行结果: {{one_case_log.result_value}}】
              </el-text>
              <el-text v-if="one_case_log.result_value === '错误'" type="danger">
                【用例执行人: {{ one_case_log.create_by_name }}】【用例执行环境: {{ one_case_log.env_name }}】【用例花费时间: {{one_case_log.time.toFixed(2)}}秒】【用例执行结果: {{one_case_log.result_value}}】
              </el-text>
            </div>
          </template>
          <template v-for="(step_log, step_index) in one_case_log.logs" :key="step_index">
            <el-collapse v-model="stepActive" accordion>
              <el-collapse-item :name="step_index">
                <template #title>
					<el-text
					  type="danger" 
					  v-if="step_log.logs && step_log.logs.some(log => log.title && log.title.includes('【ERROR】'))">
					  【{{ step_log.step_desc }}】
					</el-text>
					<el-text type="success" v-else>【{{ step_log.step_desc }}】</el-text>
                </template>
                <template v-for="(log_info, log_index) in step_log.logs" :key="log_index">
                  <el-collapse v-model="logActive" accordion>
                    <el-collapse-item :title="log_info.title" :name="log_info.title">
                      <template #title>
                        <div class="log-header">
                          <el-text v-if="log_info.title.includes('【INFO】')" type="success">{{ log_info.title }}</el-text>
                          <el-text v-if="log_info.title.includes('【ERROR】')" type="danger">{{ log_info.title }}</el-text>
                          <el-image
                            v-if="log_info.hasOwnProperty('uri')"
                            style="width: 30px; height: 30px; margin-left: 10px;"
                            :src="log_info.uri"
                            :zoom-rate="1.2"
                            :max-scale="7"
                            :min-scale="0.2"
                            :preview-src-list="[log_info.uri]"
                            :initial-index="4"
                            fit="cover"
                          />
                        </div>
                      </template>
                      <TraceReplay v-if="log_info.trace_url || log_info.video_url" :log-info="log_info" />
                      <BodyEdit v-else :bind_case_data="bind_case_data" v-model="one_case_log.logs[step_index].logs[log_index].value"></BodyEdit>
                    </el-collapse-item>
                  </el-collapse>
                </template>
              </el-collapse-item>
            </el-collapse>
          </template>
        </el-collapse-item>
      </el-collapse>
    </div>
  </el-dialog>
  
  <el-dialog v-model="lookFunCaseDetail" direction="rtl" :show-close="true"  destroy-on-close fullscreen >
    <template #header="{ close, titleId, titleClass }">
      <h4>{{ lookFunCaseTitle }}</h4>
    </template>
    <div>
      <div class="card-header">
        <div class="card-title-section">
          <i class="icon-log"></i>
          <h3 class="card-title">用例执行日志</h3>
      		  <el-tag size="medium" type="primary" effect="plain" >脚本用例</el-tag>
      		  <el-badge :value="report_logs?.count || 0" type="warning" class="data-badge">
      		    <template #content>
      		      {{ report_logs?.count || 0 }}
      		    </template>
      		  </el-badge>
        </div>
      </div>
      
      <el-table 
        :data="report_logs.results" 
        class="data-table"
        @filter-change="filterChange"
        :show-overflow-tooltip="true"
        :header-row-style="getTableHeaderStyle"
      >
        <el-table-column label="序号" width="80" type="index" align="center" />
        <el-table-column label="用例名称" prop="case_name" min-width="200" align="center">
          <template #default="scope">
            <el-link 
              type="primary" 
              :underline="false" 
              class="case-link"
              :href="`/#/resource/scriptCaseEdit?id=${scope.row.case}`" 
              target="_blank"
            >
              <i class="icon-link"></i>
              {{ scope.row.case_name }}
            </el-link>
          </template>
        </el-table-column>
      		
        <el-table-column 
          column-key="tag" 
          label="用例标签" 
          prop="tag_name" 
          min-width="150" 
          :formatter="formatter_tag" 
          align="center"
        >
          <template #default="scope">
            <div class="tag-container">
              <el-tag 
                v-for="(item, index) in scope.row.tag_name" 
                :key="index" 
                size="small" 
                effect="plain" 
                type="info"
                class="case-tag"
              >
                {{ item.name }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column 
          column-key="plant" 
          label="所属平台" 
          prop="case_plant" 
          min-width="120" 
          align="center"
        />
        <el-table-column 
          column-key="module" 
          label="所属模块" 
          prop="case_module" 
          min-width="120" 
          align="center"
        />
        <el-table-column label="耗时" width="100" align="center">
          <template #default="scope">
            <div class="time-value">{{ scope.row.time?.toFixed(2) || '0.00' }} 秒</div>
          </template>
        </el-table-column>
        <el-table-column 
          column-key="result" 
          label="执行结果" 
          width="120" 
          align="center"
        >
          <template #default="scope">
            <el-tag 
              :type="getResultType(scope.row.result_value)" 
              size="small" 
              effect="light"
              class="result-tag"
            >
              {{ scope.row.result_value }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column align="center" width="60" label="操作">
          <template #default="scope">
            <el-tooltip content="查看详细日志" placement="top">
              <el-button 
                :icon="View" 
                @click="view(scope.row)" 
                class="view-btn"
                size="small"
                type="primary"
                circle
              />
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </el-dialog>
  
  <div class="test-report-container">
    <!-- 报告标题和基本信息 -->
    <el-card class="report-header-card elegant-shadow" style='padding: 5px; padding-left: 0px'>
      <div class="report-header">
        <div class="report-left-section">
          <div class="report-title-section">
            <i class="icon-report-header"></i>
            <h1 class="report-title">{{ report_base_detail.name }}</h1>
            <el-tag size="medium" type="primary" effect="plain">测试报告</el-tag>
		  <el-tag size="medium" type="primary" effect="plain"  v-if='report_base_detail.suite_type ===1'>功能用例</el-tag>
      <el-tag size="medium" type="primary" effect="plain"  v-if='report_base_detail.suite_model ===2'>脚本用例</el-tag>
		  <el-tag size="medium" type="primary" effect="plain" v-if='report_base_detail.suite_model ===1'>静态模式</el-tag>
		  <el-tag size="medium" type="primary" effect="plain" v-if='report_base_detail.suite_model ===2'>动态模式</el-tag>
          </div>
          <div class="report-status">
            <el-tag :type="getSuccessType(report_base_detail.success_percent)" size="medium" effect="light">
              成功率: {{ report_base_detail.success_percent }}%
            </el-tag>
            <el-tag :type="getDurationType(calculateTotalDuration())" size="medium" effect="light" class="duration-tag">
              总计耗时: {{ calculateTotalDuration() }}
            </el-tag>
          </div>
        </div>
        <el-button @click="goBack" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>返回
        </el-button>
      </div>
    </el-card>

    <!-- 基本信息卡片 -->
    <el-card class="info-card elegant-shadow" style='padding: 0px'>
      <div class="info-header">
        <div class="info-title-section">
          <i class="icon-info"></i>
          <h3 class="info-title">测试执行概览</h3>
          <el-tag size="small" type="info" effect="plain">执行摘要</el-tag>
        </div>
      </div>
      
      <div class="info-content-grid">
        <div class="info-item">
          <div class="info-label">
            <i class="icon-user"></i>
            <span>执行人员</span>
          </div>
          <div class="info-value">{{ report_base_detail.create_by_name || '-' }}</div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-env"></i>
            <span>执行环境</span>
          </div>
          <div class="info-value">{{ report_base_detail.env_name || '-' }}</div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-start-time"></i>
            <span>开始时间</span>
          </div>
          <div class="info-value">{{ report_base_detail.create_time || '-' }}</div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-end-time"></i>
            <span>结束时间</span>
          </div>
          <div class="info-value">{{ report_base_detail.update_time || '-' }}</div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-case"></i>
            <span>用例总数</span>
          </div>
          <div class="info-value">
            <el-tag :type="getCaseType(report_base_detail.all_case_number)" size="small" effect="plain">
              {{ report_base_detail.all_case_number || 0 }}
            </el-tag>
          </div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-success"></i>
            <span>成功用例</span>
          </div>
          <div class="info-value">
            <el-tag type="success" size="small" effect="plain">{{ report_base_detail.success_case_number || 0 }}</el-tag>
          </div>
        </div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-failure"></i>
            <span>失败用例</span>
          </div>
          <div class="info-value">
            <el-tag type="danger" size="small" effect="plain">{{ report_base_detail.fail_case_number || 0 }}</el-tag>
          </div>
        </div>
        
        <div class="info-item" >
          <div class="info-label">
            <i class="icon-error"></i>
            <span>错误用例</span>
          </div>
          <div class="info-value">
            <el-tag type="warning" size="small" effect="plain">{{ report_base_detail.error_case_number || 0 }}</el-tag>
          </div>
        </div>
		
		<div class="info-item">
		  <div class="info-label">
		    <i class="icon-percent"></i>
		    <span>成功率</span>
		  </div>
		  <div class="info-value">
		    <el-tag :type="getSuccessType(report_base_detail.success_percent)" size="small" effect="plain">
		      {{ report_base_detail.success_percent || 0 }}%
		    </el-tag>
		  </div>
		</div>
        
        <div class="info-item">
          <div class="info-label">
            <i class="icon-failure-rate"></i>
            <span>失败率</span>
          </div>
          <div class="info-value">
            <el-tag :type="getFailureRateType(calculateFailureRate())" size="small" effect="plain">
              {{ calculateFailureRate().toFixed(2) }}%
            </el-tag>
          </div>
        </div>
        
      </div>
    </el-card>

    <!-- 图表区域 - 拆分为两个卡片 -->
    <div class="charts-row">
      <el-card class="chart-card elegant-shadow">
        <div class="chart-header">
          <div class="chart-title-section">
            <i class="icon-chart-pie"></i>
            <h3 class="chart-title">测试结果分布</h3>
          </div>
        </div>
        <v-chart :option="testResultOption" autoresize class="chart-content" />
      </el-card>
      
      <el-card class="chart-card elegant-shadow">
        <div class="chart-header">
          <div class="chart-title-section">
            <i class="icon-chart-line"></i>
            <h3 class="chart-title">测试结果趋势</h3>
          </div>
        </div>
        <v-chart :option="historyResultOption" autoresize class="chart-content" />
      </el-card>
    </div>

    <!-- 标签统计和模块统计 -->
    <div class="stats-container">
      <!-- 标签统计 -->
      <el-card class="stats-card elegant-shadow">
        <div class="card-header">
          <div class="card-title-section">
            <i class="icon-tag"></i>
            <h3 class="card-title">用例标签统计</h3>
            <el-badge :value="tags?.length || 0" type="info" class="data-badge" />
          </div>
        </div>
        
        <div class="table-container">
          <el-table 
            :data="tags" 
            class="data-table"
            :show-overflow-tooltip="true"
            :header-row-style="getTableHeaderStyle"
            :max-height="300"
          >
            <el-table-column label="用例标签" min-width="120" align="center">
              <template #default="scope">
                <span class="tag-name">{{ scope.row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column label="用例总数" prop="all_case_number" width="90" align="center">
              <template #default="scope">
                <div class="number-value">{{ scope.row.all_case_number || 0 }}</div>
              </template>
            </el-table-column>
            <el-table-column label="成功数" prop="success_number" width="80" align="center">
              <template #default="scope">
                <div class="success-value">{{ scope.row.success_number || 0 }}</div>
              </template>
            </el-table-column>
            <el-table-column label="失败数" prop="fail_number" width="80" align="center">
              <template #default="scope">
                <div class="error-value">{{ scope.row.fail_number || 0 }}</div>
              </template>
            </el-table-column>
            <el-table-column label="错误数" prop="error_number" width="80" align="center">
              <template #default="scope">
                <div class="warning-value">{{ scope.row.error_number || 0 }}</div>
              </template>
            </el-table-column>
            <el-table-column label="成功率" width="100" align="center">
              <template #default="scope">
                <div class="percent-value" :class="getPercentClass(scope.row.success_number, scope.row.all_case_number)">
                  {{ scope.row.all_case_number ? ((scope.row.success_number / scope.row.all_case_number * 100).toFixed(2)) : '0.00' }}%
                </div>
              </template>
            </el-table-column>
            <el-table-column label="失败率" width="100" align="center">
              <template #default="scope">
                <div class="percent-value" :class="getPercentClass(scope.row.fail_number + scope.row.error_number, scope.row.all_case_number, true)">
                  {{ scope.row.all_case_number ? (((scope.row.fail_number + scope.row.error_number) / scope.row.all_case_number * 100).toFixed(2)) : '0.00' }}%
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>

      <!-- 模块统计 -->
      <el-card class="stats-card elegant-shadow">
        <div class="card-header">
          <div class="card-title-section">
            <i class="icon-module"></i>
            <h3 class="card-title">用例模块统计</h3>
            <el-badge :value="modules?.length || 0" type="success" class="data-badge" />
          </div>
        </div>
        
        <div class="table-container">
          <el-table 
            :data="modules" 
            class="data-table"
            :show-overflow-tooltip="true"
            :header-row-style="getTableHeaderStyle"
            :max-height="300"
          >
            <el-table-column label="模块名称" min-width="150" align="center">
              <template #default="scope">
                <span class="module-name">{{ scope.row.plant_name }}_{{ scope.row.module_name }}</span>
              </template>
            </el-table-column>
            <el-table-column label="用例总数" prop="all_case_number" width="90" align="center">
              <template #default="scope">
                <div class="number-value">{{ scope.row.all_case_number || 0 }}</div>
              </template>
            </el-table-column>
            <el-table-column label="成功数" prop="success_number" width="80" align="center">
              <template #default="scope">
                <div class="success-value">{{ scope.row.success_number || 0 }}</div>
              </template>
            </el-table-column>
            <el-table-column label="失败数" prop="fail_number" width="80" align="center">
              <template #default="scope">
                <div class="error-value">{{ scope.row.fail_number || 0 }}</div>
              </template>
            </el-table-column>
            <el-table-column label="错误数" prop="error_number" width="80" align="center">
              <template #default="scope">
                <div class="warning-value">{{ scope.row.error_number || 0 }}</div>
              </template>
            </el-table-column>
            <el-table-column label="成功率" width="100" align="center">
              <template #default="scope">
                <div class="percent-value" :class="getPercentClass(scope.row.success_number, scope.row.all_case_number)">
                  {{ scope.row.all_case_number ? ((scope.row.success_number / scope.row.all_case_number * 100).toFixed(2)) : '0.00' }}%
                </div>
              </template>
            </el-table-column>
            <el-table-column label="失败率" width="100" align="center">
              <template #default="scope">
                <div class="percent-value" :class="getPercentClass(scope.row.fail_number + scope.row.error_number, scope.row.all_case_number, true)">
                  {{ scope.row.all_case_number ? (((scope.row.fail_number + scope.row.error_number) / scope.row.all_case_number * 100).toFixed(2)) : '0.00' }}%
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>

    <!-- 执行日志（放在最后） -->
    <el-card class="data-card elegant-shadow" style="margin-top: 0; padding: 0;" v-if='report_base_detail.suite_type ===2'>
      <div class="card-header">
        <div class="card-title-section">
          <i class="icon-log"></i>
          <h3 class="card-title">用例执行日志</h3>
		  <el-tag size="medium" type="primary" effect="plain" >脚本用例</el-tag>
		  <el-tag size="medium" type="primary" effect="plain" v-if='report_base_detail.suite_model ===1'>静态模式</el-tag>
		  <el-tag size="medium" type="primary" effect="plain" v-if='report_base_detail.suite_model ===2'>动态模式</el-tag>
		  <el-badge :value="report_logs?.count || 0" type="warning" class="data-badge">
		    <template #content>
		      {{ report_logs?.count || 0 }}
		    </template>
		  </el-badge>
        </div>
      </div>
      
      <el-table 
        :data="report_logs.results" 
        class="data-table"
        @filter-change="filterChange"
        :show-overflow-tooltip="true"
        :header-row-style="getTableHeaderStyle"
      >
        <el-table-column label="序号" width="80" type="index" align="center" />
        <el-table-column label="用例名称" prop="case_name" min-width="200" align="center">
          <template #default="scope">
            <el-link 
              type="primary" 
              :underline="false" 
              class="case-link"
              :href="`/#/resource/scriptCaseEdit?id=${scope.row.case}`" 
              target="_blank"
            >
              <i class="icon-link"></i>
              {{ scope.row.case_name }}
            </el-link>
          </template>
        </el-table-column>
		
        <el-table-column 
          column-key="tag" 
          label="用例标签" 
          prop="tag_name" 
          min-width="150" 
          :formatter="formatter_tag" 
          :filters="tag_filter" 
          align="center"
        >
          <template #default="scope">
            <div class="tag-container">
              <el-tag 
                v-for="(item, index) in scope.row.tag_name" 
                :key="index" 
                size="small" 
                effect="plain" 
                type="info"
                class="case-tag"
              >
                {{ item.name }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column 
          column-key="plant" 
          label="所属平台" 
          prop="case_plant" 
          min-width="120" 
          :filters="plant_filter" 
          align="center"
        />
        <el-table-column 
          column-key="module" 
          label="所属模块" 
          prop="case_module" 
          min-width="120" 
          :filters="module_filter" 
          align="center"
        />
        <el-table-column label="耗时" width="100" align="center">
          <template #default="scope">
            <div class="time-value">{{ scope.row.time?.toFixed(2) || '0.00' }} 秒</div>
          </template>
        </el-table-column>
        <el-table-column 
          column-key="result" 
          label="执行结果" 
          width="120" 
          align="center"
          :filters="[{ text: '成功', value: '1' }, { text: '失败', value: '2' }, { text: '错误', value: '3' }]"
        >
          <template #default="scope">
            <el-tag 
              :type="getResultType(scope.row.result_value)" 
              size="small" 
              effect="light"
              class="result-tag"
            >
              {{ scope.row.result_value }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column align="center" width="60" label="操作">
          <template #default="scope">
            <el-tooltip content="查看详细日志" placement="top">
              <el-button 
                :icon="View" 
                @click="view(scope.row)" 
                class="view-btn"
                size="small"
                type="primary"
                circle
              />
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="page_size_params.page"
          v-model:page-size="page_size_params.size"
          :page-sizes="[10, 20, 30, 50]"
          :hide-on-single-page="false"
          layout="total, sizes, prev, pager, next, jumper"
          :total="report_logs.count"
          @size-change="handleSizeChange"
		  class='select input'
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
	
	<!-- 执行日志（放在最后） -->
	<el-card class="data-card elegant-shadow" style="margin-top: 0; padding: 0;" v-if='report_base_detail.suite_type ===1'>
	  <div class="card-header">
	    <div class="card-title-section">
	      <i class="icon-log"></i>
	      <h3 class="card-title">用例执行日志</h3>
		  <el-tag size="medium" type="primary" effect="plain" >功能用例</el-tag>
		  <el-tag size="medium" type="primary" effect="plain" v-if='report_base_detail.suite_model ===1'>静态模式</el-tag>
		  <el-tag size="medium" type="primary" effect="plain" v-if='report_base_detail.suite_model ===2'>动态模式</el-tag>
		  <el-badge :value="report_logs?.count || 0" type="warning" class="data-badge">
		    <template #content>
		      {{ report_func_cases.count }}
		    </template>
		  </el-badge>
	    </div>
	  </div>
	  
	  <el-table 
	    :data="report_func_cases.results" 
	    class="data-table"
	    @filter-change="filterChange"
	    :show-overflow-tooltip="true"
	    :header-row-style="getTableHeaderStyle"
	  >
	    <el-table-column label="序号" width="80" type="index" align="center" />
	    <el-table-column label="用例名称" prop="name" min-width="200" align="center">
	      <template #default="scope">
	        <el-link 
	          type="primary" 
	          :underline="false" 
	          class="case-link"
	          :href="`/#/resource/scriptCaseEdit?id=${scope.row.id}`" 
	          target="_blank"
	        >
	          <i class="icon-link"></i>
	          {{ scope.row.name }}
	        </el-link>
	      </template>
	    </el-table-column>
		
		<el-table-column
		  label="自动化状态" 
		  width="120" 
		  align="center"
		  prop="auto_status_name" 
		  class-name="case-info-column"
		>
		 
		</el-table-column>
		
	    <el-table-column 
	      column-key="tag" 
	      label="用例标签" 
	      prop="tag_name" 
	      min-width="150" 
	      :formatter="formatter_tag" 
	      :filters="tag_filter" 
	      align="center"
	    >
	      <template #default="scope">
	        <div class="tag-container">
	          <el-tag 
	            v-for="(item, index) in scope.row.tag_name" 
	            :key="index" 
	            size="small" 
	            effect="plain" 
	            type="info"
	            class="case-tag"
	          >
	            {{ item.name }}
	          </el-tag>
	        </div>
	      </template>
	    </el-table-column>
	    <el-table-column 
	      column-key="plant" 
	      label="所属平台" 
	      prop="plant_name" 
	      min-width="120" 
	      :filters="plant_filter" 
	      align="center"
	    />
	    <el-table-column 
	      column-key="module" 
	      label="所属模块" 
	      prop="module_name" 
	      min-width="120" 
	      :filters="module_filter" 
	      align="center"
	    />
		
		<el-table-column
		  column-key="result" 
		  label="脚本运行结果" 
		  width="180" 
		  align="center"
		>
		  <template #default="scope">
			  <el-badge :value="scope.row.auto_s" class="item" color="green" v-if='scope.row.auto_s !=0' :offset="[0, 8]" style='margin-right: 20px'>
			    <el-tag  type='success' size="small" >成功</el-tag>
			  </el-badge>
			  <el-badge :value="scope.row.auto_f" class="item" color="rgb(245, 108, 108)" v-if='scope.row.auto_f !=0' :offset="[0, 8]" style='margin-right: 20px'>
			    <el-tag  type='error' size="small" >失败</el-tag>
			  </el-badge>
			  <el-badge :value="scope.row.auto_e" class="item" color="rgb(245, 108, 108)" v-if='scope.row.auto_e !=0' :offset="[0, 8]">
			    <el-tag  type='error' size="small">错误</el-tag>
			  </el-badge>
		  </template>
		</el-table-column>
		
	   <!-- <el-table-column label="耗时" width="100" align="center">
	      <template #default="scope">
	        <div class="time-value">{{ scope.row.time?.toFixed(2) || '0.00' }} 秒</div>
	      </template>
	    </el-table-column> -->
	    <el-table-column 
	      column-key="result" 
	      label="执行结果" 
	      width="120" 
	      align="center"
	      :filters="[{ text: '成功', value: '1' }, { text: '失败', value: '2' }]"
	    >
	      <template #default="scope">
	        <el-tag 
	          :type="getResultType(scope.row.func_result_text)" 
	          size="small" 
	          effect="light"
	          class="result-tag"
	        >
	          {{ scope.row.func_result_text }}
	        </el-tag>
	      </template>
	    </el-table-column>
		
	    <el-table-column align="center" width="60" label="操作">
	      <template #default="scope">
			<el-tooltip content="查看关联脚本用例" placement="top">
			  <el-button 
			    :icon="View" 
			    @click="viewFuncCaseDetail(scope.row)" 
			    class="view-btn"
			    size="small"
			    type="primary"
				v-if='report_base_detail.suite_type ===1'
			    circle
			  />
			</el-tooltip>
	      </template>
	    </el-table-column>
	  </el-table>
	  
	  <div class="pagination-container">
	    <el-pagination
	      v-model:current-page="page_size_params.page"
	      v-model:page-size="page_size_params.size"
	      :page-sizes="[10, 20, 30, 50]"
	      :hide-on-single-page="false"
	      layout="total, sizes, prev, pager, next, jumper"
	      :total="report_func_cases.count"
	      @size-change="handleSizeChange"
		  class='select input'
	      @current-change="handleCurrentChange"
	    />
	  </div>
	</el-card>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { View, ArrowLeft } from '@element-plus/icons-vue'
import BodyEdit from '../../components/BodyEdit.vue'
import TraceReplay from '../../components/TraceReplay.vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, LineChart } from 'echarts/charts'
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
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

export default {
  computed: {
    ...mapState(['pathPermission', 'projectInfo', 'userInfo']),
  },
  components: {
    BodyEdit,
    TraceReplay,
    'v-chart': VChart
  },
  data() {
    return {
	  lookFunCaseDetail: false,
	  lookFunCaseTitle: '',
      page_size_params: {
        page: 1,
        size: 10,
      },
      testResultOption: {
        color: ['#52c41a', '#f5222d', '#fa8c16'],
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#1a1a1a',
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' },
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 0,
          textStyle: { color: '#64748b' }
        },
        series: [
          {
            name: '测试结果分布',
            type: 'pie',
            radius: ['40%', '65%'],
            center: ['50%', '45%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: true,
              formatter: '{b}: {d}%'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '14',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: true
            },
            data: [
              { value: 0, name: '成功' },
              { value: 0, name: '失败' },
              { value: 0, name: '错误' }
            ]
          }
        ]
      },
      historyResultOption: {
        color: ['#52c41a', '#f5222d', '#fa8c16'],
        title: {
          text: '',
          left: 'center',
          textStyle: {
            color: '#1a1a1a',
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e2e8f0',
          textStyle: { color: '#1a1a1a' },
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: { color: '#64748b' },
          splitLine: { lineStyle: { color: '#f1f5f9' } }
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
          bottom: 0,
          textStyle: { color: '#64748b' }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '10%',
          containLabel: true
        },
        series: [
          {
            name: '成功率',
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
          },
          {
            name: '错误率',
            type: 'line',
            data: [],
            smooth: true,
            lineStyle: { width: 2 },
            symbolSize: 6
          }
        ]
      },
      tmpFilters: {},
      bind_case_data: [],
      activeName: 'log',
      lookLogVisible: false,
      report_base_detail: {},
      stepActive: '',
      logActive: '',
      report_logs: { results: [], count: 0 },
	  report_func_cases: {},
      one_case_log: {},
      editDrawerVisible: false,
      plant_filter: [],
      module_filter: [],
      tag_filter: [],
      modules: [],
      tags: [],
    }
  },
  setup() {
    return {
      View,
      ArrowLeft,
    }
  },
  methods: {
    goBack() {
      this.$router.back()
    },
    getTableHeaderStyle() {
      return {
        'font-weight': '600',
        'color': '#1a1a1a',
        'background-color': '#f8fafc',
        'border-bottom': '2px solid #e2e8f0'
      }
    },
    
    getResultType(result) {
      const types = {
        '成功': 'success',
        '失败': 'danger',
        '错误': 'warning'
      }
      return types[result] || 'info'
    },
	
	viewFuncCaseDetail(data){
		this.lookFunCaseDetail = true
		this.lookFunCaseTitle = data.name
		this.getLogs({func_case: data.id}, false)
	},
    
    getSuccessType(percent) {
      if (!percent) return 'info'
      if (percent >= 90) return 'success'
      if (percent >= 70) return 'warning'
      return 'danger'
    },
    
    getDurationType(duration) {
      if (duration === '-' || !duration) return 'info'
      
      // 解析持续时间字符串
      const dayMatch = duration.match(/(\d+)天/)
      const hourMatch = duration.match(/(\d+)小时/)
      const minMatch = duration.match(/(\d+)分钟/)
      const secMatch = duration.match(/(\d+)秒/)
      
      let totalMinutes = 0
      
      if (dayMatch) totalMinutes += parseInt(dayMatch[1]) * 24 * 60
      if (hourMatch) totalMinutes += parseInt(hourMatch[1]) * 60
      if (minMatch) totalMinutes += parseInt(minMatch[1])
      
      if (totalMinutes > 60) return 'danger' // 超过1小时
      if (totalMinutes > 30) return 'warning' // 超过30分钟
      return 'success' // 30分钟以内
    },
    
    getCaseType(count) {
      if (!count) return 'info'
      if (count > 100) return 'warning'
      if (count > 50) return 'primary'
      return 'success'
    },
    
    getFailureRateType(rate) {
      if (!rate) return 'info'
      if (rate <= 10) return 'success'
      if (rate <= 30) return 'warning'
      return 'danger'
    },
    
    getPercentClass(successCount, totalCount, isFailure = false) {
      if (!totalCount) return ''
      const percent = (successCount / totalCount) * 100
      
      if (isFailure) {
        // 失败率
        if (percent <= 10) return 'percent-good'
        if (percent <= 30) return 'percent-warning'
        return 'percent-danger'
      } else {
        // 成功率
        if (percent >= 90) return 'percent-good'
        if (percent >= 70) return 'percent-warning'
        return 'percent-danger'
      }
    },
    
    calculateFailureRate() {
      const all = this.report_base_detail.all_case_number || 0
      const fail = this.report_base_detail.fail_case_number || 0
      const error = this.report_base_detail.error_case_number || 0
      
      if (all === 0) return 0
      return ((fail + error) / all) * 100
    },
    
    calculateTotalDuration() {
      const startTime = this.report_base_detail.create_time
      const endTime = this.report_base_detail.update_time
      
      if (!startTime || !endTime) {
        return '-'
      }
      
      try {
        // 解析时间字符串为Date对象
        const start = new Date(startTime)
        const end = new Date(endTime)
        
        // 计算时间差（毫秒）
        const durationMs = end.getTime() - start.getTime()
        
        if (durationMs < 0) {
          return '-'
        }
        
        // 转换为秒
        const durationSec = Math.floor(durationMs / 1000)
        
        if (durationSec < 60) {
          return `${durationSec}秒`
        }
        
        // 转换为分钟
        const durationMin = Math.floor(durationSec / 60)
        const remainingSec = durationSec % 60
        
        if (durationMin < 60) {
          return `${durationMin}分钟${remainingSec > 0 ? `${remainingSec}秒` : ''}`
        }
        
        // 转换为小时
        const durationHour = Math.floor(durationMin / 60)
        const remainingMin = durationMin % 60
        
        if (durationHour < 24) {
          return `${durationHour}小时${remainingMin > 0 ? `${remainingMin}分钟` : ''}`
        }
        
        // 转换为天
        const durationDay = Math.floor(durationHour / 24)
        const remainingHour = durationHour % 24
        
        return `${durationDay}天${remainingHour > 0 ? `${remainingHour}小时` : ''}`
      } catch (error) {
        console.error('计算总耗时出错:', error)
        return '-'
      }
    },
    
    toCase(row) {
      this.$router.push({ name: 'caseStepEdit', query: { id: row.case } })
    },
    
    filterChange(filters) {
      this.tmpFilters = { ...filters }
      const params = {}
      for (const filter of Object.keys(filters)) {
        params[filter] = filters[filter].join(',')
      }
	  if (this.report_base_detail.suite_type === 2){
	  	this.getLogs(params)
	  }else{
	  	this.getReportFunCases(params)
	  }
    },
    
    filterPlant(value, row) {
      return row.case_plant === value
    },
    
    filterModule(value, row) {
      return row.case_plant + '_' + row.case_module === value
    },
    
    filterType(value, row) {
      return row.case_type === value
    },
    
    formatter_tag(row, column, cellValue, index) {
      if (row.tag_name.length !== 0) {
        var tags = []
        for (var i = 0; i < row.tag_name.length; i++) {
          tags[i] = row.tag_name[i].name
        }
        return tags.join('/')
      } else {
        return '-'
      }
    },
    
    view(row) {
      this.lookLogVisible = true
      this.one_case_log = { ...row }
    },
    
    handleCurrentChange() {
      this.filterChange(this.tmpFilters)
    },
    
    handleSizeChange() {
      this.filterChange(this.tmpFilters)
    },
    
    async getReport() {
      const response = await this.$api.getReport(this.$route.query.id)
      if (response.status === 200) {
        this.report_base_detail = { ...response.data.result }
		if (this.report_base_detail.suite_type === 2){
			this.getLogs({})
		}else{
			this.getReportFunCases()
		}
        this.tag_filter = this.report_base_detail.detail?.tag_filter || []
        this.plant_filter = this.report_base_detail.detail?.plant_filter || []
        this.module_filter = this.report_base_detail.detail?.module_filter || []
        this.modules = this.report_base_detail.modules || []
        this.tags = this.report_base_detail.tags || []
        
        // 更新饼图数据
        this.testResultOption.series[0].data = [
          { value: this.report_base_detail.success_case_number || 0, name: '成功' },
          { value: this.report_base_detail.fail_case_number || 0, name: '失败' },
          { value: this.report_base_detail.error_case_number || 0, name: '错误' }
        ]
        
        // 更新折线图数据
        if (this.report_base_detail.history) {
          this.historyResultOption.xAxis.data = [...(this.report_base_detail.history.x_data || [])]
          this.historyResultOption.series[0].data = [...(this.report_base_detail.history.s_data || [])]
          this.historyResultOption.series[1].data = [...(this.report_base_detail.history.f_data || [])]
          this.historyResultOption.series[2].data = [...(this.report_base_detail.history.e_data || [])]
        }
      }
    },
    
    async getLogs(params, is_page_size=true) {
      const searchLog = Object.assign({ report: this.$route.query.id, distinct_case: true}, params)
	  if (is_page_size){
		  const response = await this.$api.getCaseLogs(Object.assign(searchLog, this.page_size_params))
		  if (response.status === 200) {
		    this.report_logs = response.data
		  } else if (response.status === 404) {
		    this.report_logs = { results: [], count: 0 }
		  }
	  }else{
		  const response = await this.$api.getCaseLogs(searchLog)
		  if (response.status === 200) {
		    this.report_logs = response.data
		  } else if (response.status === 404) {
		    this.report_logs = { results: [], count: 0 }
		  }
	  }
      
    },

    async check_permission(){
        const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission['/report/list']}
        const response = await this.$api.check_permission(params)
        if (response.status === 200){
          this.permission = { ...response.data.result }
        }
		},
	
	async getReportFunCases(params) {
	  const searchLog = Object.assign({ report: this.$route.query.id }, params)
	  const response = await this.$api.getReportFunCases(Object.assign(searchLog, this.page_size_params))
	  if (response.status === 200) {
	    this.report_func_cases = response.data
	  }
	},
  },
  created() {
    this.check_permission()
    this.getReport()
  }
}
</script>

<style scoped>
.test-report-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
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
  background: white;
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
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  font-weight: 500;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.back-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.icon-report-header {
  display: inline-block;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
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
  background: white;
  border-radius: 5px;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

.report-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
}

.report-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.duration-tag {
  background-color: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

/* 基本信息卡片 */
.info-card {
  padding: 24px;
  margin-bottom: 10px;
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
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
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
  background: white;
  border-radius: 3px;
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

.info-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.info-content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
}

.icon-user,
.icon-env,
.icon-start-time,
.icon-end-time,
.icon-case,
.icon-success,
.icon-failure,
.icon-error,
.icon-percent,
.icon-failure-rate {
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

.icon-case {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-Six-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
}

.icon-success {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2352c41a' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z'/%3E%3C/svg%3E");
}

.icon-failure {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f5222d' d='M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z'/%3E%3C/svg%3E");
}

.icon-error {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23fa8c16' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z'/%3E%3C/svg%3E");
}

.icon-percent {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%238b5cf6' d='M7.5 11C8.88 11 10 9.88 10 8.5S8.88 6 7.5 6 5 7.12 5 8.5 6.12 11 7.5 11zm9 0c1.38 0 2.5-1.12 2.5-2.5S17.88 6 16.5 6 14 7.12 14 8.5s1.12 2.5 2.5 2.5zm-9 7c1.38 0 2.5-1.12 2.5-2.5S8.88 13 7.5 13 5 14.12 5 15.5 6.12 18 7.5 18zm9 0c1.38 0 2.5-1.12 2.5-2.5S17.88 13 16.5 13 14 14.12 14 15.5s1.12 2.5 2.5 2.5z'/%3E%3C/svg%3E");
}

.icon-failure-rate {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f5222d' d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z'/%3E%3C/svg%3E");
}

.info-value {
  font-size: 15px;
  color: #1a1a1a;
  font-weight: 500;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.info-value:hover {
  background: white;
  border-color: #cbd5e1;
}

/* 图表行 */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
  margin-bottom: 10px;
}

.chart-card {
  padding: 0px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chart-header {
  margin-bottom: 15px;
}

.chart-title-section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.icon-chart-pie,
.icon-chart-line {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-chart-pie {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%238b5cf6' d='M11 2v20c-5.07-.5-9-4.79-9-10s3.93-9.5 9-10zm2.03 0v8.99H22c-.47-4.74-4.24-8.52-8.97-8.99zm0 11.01V22c4.74-.47 8.5-4.25 8.97-8.99h-8.97z'/%3E%3C/svg%3E");
}

.icon-chart-line {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z'/%3E%3C/svg%3E");
}

.chart-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.chart-content {
  flex: 1;
  height: 280px;
  height: 280px;
}

/* 统计卡片容器 */
.stats-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 10px;
}

.stats-card {
  padding: 0px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.card-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-tag,
.icon-module,
.icon-log {
  display: inline-block;
  width: 24px;
  height: 24px;
  border-radius: 8px;
  position: relative;
}

.icon-tag {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.icon-module {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.icon-log {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.icon-tag::before,
.icon-module::before,
.icon-log::before {
  content: '';
  position: absolute;
  top: 6px;
  left: 6px;
  right: 6px;
  bottom: 6px;
  background: white;
  border-radius: 4px;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.data-badge {
  margin-left: 8px;
}

.table-container {
  flex: 1;
  overflow: hidden;
}

/* 数据卡片 */
.data-card {
  padding: 24px;
  margin-top: 0;
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
  background-color: #f8fafc;
}

.tag-name,
.module-name {
  font-weight: 500;
  color: #1a1a1a;
}

.number-value,
.time-value,
.success-value,
.error-value,
.warning-value,
.percent-value {
  font-weight: 600;
  font-family: 'Consolas', 'Monaco', monospace;
}

.number-value { color: #3b82f6; }
.time-value { color: #8b5cf6; }
.success-value { color: #52c41a; }
.error-value { color: #f5222d; }
.warning-value { color: #fa8c16; }
.percent-value { color: #64748b; }

.percent-good {
  color: #52c41a !important;
}

.percent-warning {
  color: #fa8c16 !important;
}

.percent-danger {
  color: #f5222d !important;
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
}

.case-tag {
  margin: 1px;
}

.result-tag {
  font-weight: 500;
}

.case-link {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.icon-link {
  width: 14px;
  height: 14px;
  display: inline-block;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.view-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

/* 抽屉样式优化 */
.case-header-info {
  padding: 8px 0;
}

.step-title {
  font-weight: 500;
}

.log-header {
  display: flex;
  align-items: center;
  gap: 8px;
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

.charts-row {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both;
}

.stats-container {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.3s both;
}

.data-card {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.4s both;
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .info-content-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-row {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .stats-container {
    grid-template-columns: 1fr;
  }
}

@media screen and (max-width: 768px) {
  .test-report-container {
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
  
  .data-table ::v-deep(.el-table__body-wrapper),
  .data-table ::v-deep(.el-table__header-wrapper) {
    overflow-x: auto;
  }
  
  .data-table ::v-deep(.el-table) {
    min-width: 1200px;
  }
  
  .chart-title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>