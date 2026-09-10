<template>
  <!-- 执行用例对话框 -->
  <el-dialog v-model="runTimesVisible" title="执行用例" width="500" class="elegant-dialog">
    <el-form :model="caseForm" label-position="right">
      <el-form-item label="执行环境" label-width="100">
        <el-select v-model="caseRunForm.env_id" placeholder="请选择环境" class="select" size='large' popper-class='select-dropdown-rounded'>
          <el-option
            v-for="item in env_list.results"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
	  <el-form-item label="执行失败" label-width="100" >
	    <el-select v-model="caseRunForm.fail_is_continue" class="select" size='large' popper-class='select-dropdown-rounded'>
	      <el-option label="停止测试" :value="0" />
	      <el-option label="继续执行不忽略失败" :value="1" />
            <el-option label="继续执行并忽略失败" :value="2" />
	    </el-select>
	  </el-form-item>
      <el-form-item label="App执行器" label-width="100" v-if="case_info.type === 3">
        <el-select v-model="caseRunForm.app_executor_id" placeholder="请选择APP设备" class="select" size='large' popper-class='select-dropdown-rounded'>
          <el-option v-for="(item, index) in this.app_executor_list" :label="item.device_desc" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="用例执行次数" label-width="100">
        <el-input-number v-model="caseRunForm.run_times" :min="1" style="width: 100%;" class="input" size='large' />
      </el-form-item>
       <el-form-item label="用例数据集" label-width="100" v-if="case_info.data && 'value' in case_info.data && case_info.data['value'].length > 0">
        <el-select v-model="caseRunForm.case_data" placeholder="请选择数据集" class="select" size='large' popper-class='select-dropdown-rounded'>
          <el-option label="全部" :value="-1" />
          <el-option
             v-for="(one_case_data, index) in case_info.data.value"
             :key="one_case_data.id"
             :label="one_case_data._name_"
             :value="index"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="是否异步执行" label-width="100">
        <el-select v-model="caseRunForm.is_async" placeholder="请选择" class="select" size='large' popper-class='select-dropdown-rounded'>
          <el-option label="是" :value="true" />
          <el-option label="否" :value="false" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="runTimesVisible = false" class="dialog-cancel-btn">
          <span class="button-text">取消</span>
        </el-button>
        <el-button type="primary" @click="caseRun" class="dialog-confirm-btn">
          <span class="button-text">执行</span>
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 执行单个步骤对话框 -->
  <el-dialog v-model="StepControlCaseData" title="请选择测试数据集" width="600" class="elegant-dialog">
    <el-form :model="caseForm" label-position="right">
       <el-form-item>
             <el-alert
            title='该用例为数据驱动用例, 请选择一个测试用例数据集作为该步骤测试数据'
            type="info"
            :closable="false"
            show-icon
            style='width: 500px;'
        />
       </el-form-item>

       <el-form-item label="用例数据集" label-width="100" v-if="case_info.data && 'value' in case_info.data && case_info.data['value'].length > 0">
        <el-select v-model="caseRunForm.case_data" placeholder="请选择数据集" class="select" size='large' popper-class='select-dropdown-rounded'>
          <el-option
             v-for="(one_case_data, index) in case_info.data.value"
             :key="one_case_data.id"
             :label="one_case_data._name_"
             :value="index"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="StepControlCaseData = false" class="dialog-cancel-btn">
          <span class="button-text">取消</span>
        </el-button>
        <el-button type="primary" @click="step_run(true)" class="dialog-confirm-btn">
          <span class="button-text">执行</span>
        </el-button>
      </div>
    </template>
  </el-dialog>


  <!-- 性能压测对话框 -->
  <el-dialog v-model="locustRunVisible" width="520" class="elegant-dialog">
    <template #header>
      <div class="dialog-title-section">
        <h4 class="dialog-title">性能压测</h4>
        <el-tag size="small" type="warning" effect="light">高并发用户数下优先下载压测工具利用分布式模式压测</el-tag>
      </div>
    </template>
    <el-tabs type="card" v-model="tab_name" class="elegant-tabs">
      <el-tab-pane label="压测配置" name="config">
        <el-form :model="caseForm" label-position="right">
          <el-form-item label="执行环境" label-width="110">
            <el-select v-model="locustRunForm.env_id" placeholder="请选择环境" class="select" size='large' popper-class='select-dropdown-rounded'>
              <el-option
                v-for="item in env_list.results"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="并发用户数" label-width="110">
            <el-input-number v-model="locustRunForm.concurrent_users" :min="1" style="width: 100%;" class="input" size='large' />
          </el-form-item>
          <el-form-item label="每秒启动用户数" label-width="110">
            <el-input-number v-model="locustRunForm.users_per_second" :min="1" style="width: 100%;" class="input" size='large' />
          </el-form-item>
          <el-form-item label="压测时间/s" label-width="110">
            <el-input-number v-model="locustRunForm.durations" :min="1" style="width: 100%;"class="input" size='large' />
          </el-form-item>
        </el-form>
      </el-tab-pane>
      <el-tab-pane label="压测工具下载" name="tool">
        <div class="download-buttons">
          <el-button type="primary" class="download-btn" @click="downloadWindows" style='margin-left: 12px'>
            <el-icon><Download /></el-icon>Windows下载
          </el-button>
          <el-button type="primary" class="download-btn" @click="downloadLinux" disabled>
            <el-icon><Download /></el-icon>Linux下载
          </el-button>
          <el-button type="primary" class="download-btn" @click="downloadMacos" disabled>
            <el-icon><Download /></el-icon>MacOS下载
          </el-button>
        </div>
      </el-tab-pane>
    </el-tabs>
    <template #footer>
      <div class="dialog-footer" v-if="tab_name == 'config'">
        <el-button @click="locustRunVisible = false" class="dialog-cancel-btn">
          <span class="button-text">取消</span>
        </el-button>
        <el-button type="primary" @click="locustRun" class="dialog-confirm-btn">
          <span class="button-text">执行</span>
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 从接口同步请求数据对话框 -->
  <el-dialog v-model="loadApiVisible" title="从接口文档同步" width="670" :z-index="1001" :append-to-body="true" destroy-on-close class="elegant-dialog">
    <div class="sync-options">
      <el-checkbox-group v-model="loadTypeList" siz='large'>
		<el-checkbox label="Url" />
        <el-checkbox label="Headers" />
        <el-checkbox label="Params" />
        <el-checkbox label="Body" />
        <!-- <el-checkbox label="Data" /> -->
      </el-checkbox-group>
      <el-select v-model="loadResponseIndex" placeholder="请选择接口响应体" class="select" size='large' popper-class='select-dropdown-rounded' style="width: 200px; margin-left: 25px; " clearable >
        <el-option v-for="(item, index) in this.one_step_obj.api_all.response" :label="`Response[${item.response_status}]`" :value="index" />
      </el-select>
	  <el-alert
	  	title='参数同步的时候只会同步新增/修改/删除“参数名”，不会覆盖“参数值”。'
	  	type="info"
	  	:closable="false"
	  	show-icon
	  	style='width: 500px;'
	  />
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="loadApiVisible = false" class="dialog-cancel-btn">
          <span class="button-text">取消</span>
        </el-button>
        <el-button @click="loadApi()" class="dialog-confirm-btn">
          <span class="button-text">确定</span>
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 各种选择抽屉 -->
  <el-drawer v-model="chooseApiVisible" :with-header="false" direction="ttb" show-close :append-to-body="true" :z-index="1001" fullscreen="true" destroy-on-close size="97%">
    <ApiList :parentPermission="permission" :isCanChoose="true" v-model:chooseApiVisible="chooseApiVisible" @setApiData="setApiData"></ApiList>
  </el-drawer>

  <el-dialog v-model="choosePythonFuncVisible" :show-close="show_close" :z-index="1001" fullscreen="true" destroy-on-close class="elegant-dialog">
    <PythonFunctionList :isCanChoose="true" v-model:choosePythonFuncVisible="choosePythonFuncVisible" @setPythonFuncData="setPythonFuncData"></PythonFunctionList>
  </el-dialog>

  <el-drawer v-model="chooseStepVisible" :with-header="false" direction="ttb" :append-to-body="true" show-close :z-index="1001" fullscreen="true" destroy-on-close :size="'calc(100vh - 30px)'">
    <StepList :parentPermission="permission" :isCanChoose="true" v-model:chooseStepVisible="chooseStepVisible" @setStepData="setStepData" @setManyStepData="setManyStepData"></StepList>
  </el-drawer>

  <el-drawer v-model="chooseComStepVisible" :with-header="false" direction="ttb" show-close :z-index="1001" fullscreen="true" destroy-on-close :size="'calc(100vh - 30px)'">
    <StepList :parentPermission="permission" :isCanChoose="true" :is_com="true" v-model:chooseComStepVisible="chooseComStepVisible" @setComStepData="setComStepData" @setManyComStepData="setManyComStepData"></StepList>
  </el-drawer>

  <el-drawer v-model="chooseSeleniumVisible" :with-header="false" direction="ttb" show-close :z-index="1001" fullscreen="true" destroy-on-close :size="'calc(100vh - 30px)'">
    <SeleniumList :isCanChoose="true" v-model:chooseSeleniumVisible="chooseSeleniumVisible" @setSeleniumData="setSeleniumData"></SeleniumList>
  </el-drawer>

  <el-drawer v-model="chooseAppiumVisible" :with-header="false" direction="ttb" show-close :z-index="1001" fullscreen="true" destroy-on-close :size="'calc(100vh - 30px)'">
    <AppiumList :isCanChoose="true" v-model:chooseAppiumVisible="chooseAppiumVisible" @setAppiumData="setAppiumData"></AppiumList>
  </el-drawer>

  <!-- 测试历史抽屉 -->
  <el-drawer v-model="lookLogVisible" direction="rtl" :show-close="true" destroy-on-close size="100%" class="elegant-drawer">
    <template #header="{ close, titleId, titleClass }">
      <div class="drawer-header">
        <div class="drawer-title-section">
          <h4 class="drawer-title">测试历史</h4>
        </div>
      </div>
    </template>
	<el-row :gutter="20" style="display: flex; align-items: center; margin: 0px 20px;">
	  <!-- 左侧筛选部分，自动占据剩余空间 -->
	  <el-col :span="12" :xs="24" :sm="16" :md="14" :lg="16" style="display: flex; align-items: center;">
	    <el-radio-group v-model="run_result" @change="resultChange" :fill="fill_color">
	      <el-badge :value="case_info.all_run_times" class="item" color="green">
	        <el-radio-button :value="0">全部</el-radio-button>
	      </el-badge>
	      <el-badge :value="case_info.all_success_times" class="item" color="green">
	        <el-radio-button :value="1">成功</el-radio-button>
	      </el-badge>
	      <el-badge :value="case_info.all_fail_times" class="item">
	        <el-radio-button :value="2">失败</el-radio-button>
	      </el-badge>
	      <el-badge :value="case_info.all_error_times" class="item">
	        <el-radio-button :value="3">错误</el-radio-button>
	      </el-badge>
	    </el-radio-group>
	  </el-col>
	  
	  <!-- 右侧分页部分，根据内容自动调整宽度 -->
	  <el-col :span="12" :xs="24" :sm="8" :md="10" :lg="8" style="display: flex; justify-content: flex-end; align-items: center;">
	    <el-pagination
	      v-model:current-page="page_size_params.page"
	      v-model:page-size="page_size_params.size"
	      :page-sizes="[1, 3, 6, 9, 12]"
	      layout="total, sizes, prev, pager, next, jumper"
	      :total="case_logs.count"
	      @size-change="handleSizeChange"
		  class='select input'
	      @current-change="handleCurrentChange"
	      :background="true"
	    >
	    </el-pagination>
	  </el-col>
	</el-row>
    <div class="drawer-content">
      <el-scrollbar >
        <el-timeline v-for="(case_log, case_index) in case_logs.results" :key="case_log.id" style='padding-left: 0px; padding-top: 15px'>
          <el-timeline-item center :timestamp="case_log.create_time" placement="top">
            <el-collapse v-model="caseActive" accordion class="elegant-collapse">
              <el-collapse-item :name="case_index">
                <template #title>
                  <div class="case-log-header">
                    <el-text v-if="case_log.result_value === '成功'" type="success">
                      【用例名称: {{ case_log.case_name }}】【用例执行人: {{ case_log.create_by_name }}】【用例执行环境: {{ case_log.env_name }}】【用例花费时间: {{case_log.time.toFixed(2)}}秒】【用例执行结果: {{case_log.result_value}}】
                    </el-text>
                    <el-text v-if="case_log.result_value === '失败'" type="danger">
                      【用例名称: {{ case_log.case_name }}】【用例执行人: {{ case_log.create_by_name }}】 【用例执行环境: {{ case_log.env_name }}】【用例花费时间: {{case_log.time.toFixed(2)}}秒】【用例执行结果: {{case_log.result_value}}】
                    </el-text>
                    <el-text v-if="case_log.result_value === '错误'" type="danger">
                      【用例名称: {{ case_log.case_name }}】【用例执行人: {{ case_log.create_by_name }}】 【用例执行环境: {{ case_log.env_name }}】【用例花费时间: {{case_log.time.toFixed(2)}}秒】【用例执行结果: {{case_log.result_value}}】
                    </el-text>
                  </div>
                </template>
                <template v-for="(step_log, step_index) in case_log.logs" :key="step_index">
                  <el-collapse v-model="stepActive" accordion class="step-collapse">
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
                          <el-collapse-item :title="log_info.title" :name="log_info.title" v-if="log_info.hasOwnProperty('uri')" class="item">
                            <template #title>
                              <el-text truncated v-if="log_info.title.includes('【INFO】')" type="success">{{ log_info.title }}</el-text>
                              <el-text truncated v-if="log_info.title.includes('【ERROR】')" type="danger">{{ log_info.title }}</el-text>
                            </template>
                            <el-image
                              v-if="log_info.hasOwnProperty('uri')"
                              :src="log_info.uri"
                              :zoom-rate="1.2"
                              :max-scale="7"
                              :min-scale="0.2"
                              :preview-src-list="[log_info.uri]"
                              :initial-index="0"
                              fit="cover"
                            />
                          </el-collapse-item>
                          <el-collapse-item :title="log_info.title" :name="log_info.title" v-else class="item">
                            <template #title>
                              <el-text truncated v-if="log_info.title.includes('【INFO】')" type="success">{{ log_info.title }}</el-text>
                              <el-text truncated v-if="log_info.title.includes('【ERROR】')" type="danger">{{ log_info.title }}</el-text>
                            </template>
                            <TraceReplay v-if="log_info.trace_url || log_info.video_url" :log-info="log_info" />
                            <BodyEdit v-else :bind_case_data="case_info.data.name" v-model="case_logs.results[case_index].logs[step_index].logs[log_index].value"></BodyEdit>
                          </el-collapse-item>
                        </el-collapse>
                      </template>
                    </el-collapse-item>
                  </el-collapse>
                </template>
              </el-collapse-item>
            </el-collapse>
          </el-timeline-item>
        </el-timeline>
      </el-scrollbar>
    </div>
  </el-drawer>

  <!-- 添加数据集抽屉 -->
  <el-drawer v-model="editDataVisible" direction="rtl" size="90%" :show-close="false" :before-close="handleBeforeClose" destroy-on-close class="elegant-drawer">
    <template #header="{ close, titleId, titleClass }">
      <div class="drawer-header">
        <h4 class="drawer-title">添加数据集</h4>
      </div>
    </template>
    <div class="drawer-content">
      <CaseData
        :params_columns="case_info.data.name"
        :tableData="case_info.data.value"
        :step_index="one_step_obj.step_index"
        :steps="case_info.step"
        :isApi="false"
        :func_list="func_list"
        :bind_env_params="bind_env_params"
        :bind_global_params="bind_global_params"
        :case_params_data="case_info.params"
      ></CaseData>
    </div>
  </el-drawer>

  <!-- 设置用例变量对话框 -->
  <el-dialog v-model="editParamsVisible" title="设置用例变量" width="1200" :show-close="false" class="elegant-dialog">
    <CaseParams :bind_case_data="case_info.data.name" :tableData="case_info.params" :func_list="func_list" :bind_env_params="bind_env_params" :bind_global_params="bind_global_params"></CaseParams>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="updateCaseParams" class="dialog-confirm-btn">
          <span class="button-text">确认</span>
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 设置步骤变量对话框 -->
  <el-dialog v-model="editStepParamsVisible" title="设置步骤变量" width="1100" :show-close="false" class="elegant-dialog">
    <StepParams
      :bind_case_data="case_info.data.name"
      :tableData="stepRowInfo.step_params"
      :step_index="stepRowInfo.step_index"
      :func_list="func_list"
      :bind_env_params="bind_env_params"
      :bind_global_params="bind_global_params"
      :case_params_data="case_info.params"
      :steps="case_info.step"
    ></StepParams>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="updateStepParams" class="dialog-confirm-btn">
          <span class="button-text">确认</span>
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 步骤详情抽屉 -->
  <el-drawer class="step" :z-index="1000" v-model="editStepDetailVisible" :with-header="false" direction="rtl" :show-close="false" :append-to-body="true" :close-on-click-modal="false" size="calc(100vw)" >
    <el-card class="content-card elegant-shadow">
	  <el-form :disabled="stepView" :rules="stepRules" ref="stepRef" :model="one_step_obj">
		<div class="fixed-content-header">
			<!-- 第一行：用例名称 + 操作按钮 -->
			<div class="header-top">
			  <div class="case-title-area">
				<h3 class="content-title">{{ one_step_obj.desc }}</h3>
			  </div>
			  <div class="action-buttons">
          <el-select  @change="editStepTwo" class="select" size='large' popper-class='select-dropdown-rounded' style='width: 300px' placeholder="请选择步骤切换编辑">
				      <el-option v-for="(step_obj, index) in case_info.step" :label="`${index + 1}. ${step_obj.desc}`"  :value="step_obj" :title="`${index + 1}. ${step_obj.desc}`"/>
				  </el-select>
          <el-dropdown @command="controlStepCommand" class="action-btn control-dropdown" v-if="permission.has_add_permission">
            <el-button type="primary" class="dialog-confirm-btn">
            添加步骤
            </el-button>
			  <template #dropdown>
			    <el-dropdown-menu class="control-menu">
			      <el-dropdown-item divided :command="5" class="control-item">
			        <el-icon><Link /></el-icon>HTTP接口请求
			      </el-dropdown-item>
				  <el-dropdown-item divided :command="8" class="control-item">
				    <el-icon><CircleCheck /></el-icon>数据库操作
				  </el-dropdown-item>
			      <el-dropdown-item divided :command="10" class="control-item" v-if='case_info.type === 2'>
			        <el-icon><Mouse /></el-icon>Web自动化
			      </el-dropdown-item>
			      <el-dropdown-item divided :command="7" class="control-item" v-if='case_info.type === 3'>
			        <el-icon><Iphone /></el-icon>App自动化
			      </el-dropdown-item>
			      <el-dropdown-item divided :command="3" class="control-item">
			        <el-icon><Connection /></el-icon>复用已有步骤
			      </el-dropdown-item>
				  <el-dropdown-item divided :command="6" class="control-item">
				    <el-icon><Postcard /></el-icon>引用并创建新步骤
				  </el-dropdown-item>
			    </el-dropdown-menu>
			  </template>
			</el-dropdown>
			  </div>
			</div>
	    
			<!-- 第二行：用例信息 -->
			<div class="header-bottom">
			  <div class="case-meta">
				<div class="meta-item">
				  <span class="meta-label">步骤ID</span>
				  <el-tag class="meta-value">{{ one_step_obj.case_step_id || '-' }}</el-tag>
				</div>
				<div class="meta-divider"></div>
				<div class="meta-item">
				  <span class="meta-label">创建人</span>
				  <span class="meta-value">{{ one_step_obj.create_by_name || '-' }}</span>
				</div>
				<div class="meta-divider"></div>
					<div class="meta-item">
					  <span class="meta-label">创建时间</span>
					  <span class="meta-value">{{ formatTime(one_step_obj.create_time) || '-' }}</span>
					</div>
					<div class="meta-divider"></div>
				<div class="meta-item">
				  <span class="meta-label">更新人</span>
				  <span class="meta-value">{{ one_step_obj.update_by_name || '-' }}</span>
				</div>
					<div class="meta-divider"></div>
					<div class="meta-item">
					  <span class="meta-label">更新时间</span>
					  <span class="meta-value">{{ formatTime(one_step_obj.update_time) || '-' }}</span>
					</div>
          <div class="meta-divider"></div>
          <el-tag v-if="one_step_obj.id !==0 && one_step_obj.case_step_id !==0">{{ `第 ${one_step_obj.step_index + 1} 步` }}</el-tag>
          <el-tag v-else>{{ `第 ${case_info.step.length + 1} 步` }}</el-tag>
          <el-tag  v-if='one_step_obj.type === 3'style='margin-right: 10px'>公共步骤</el-tag>
          <el-tag  v-if='one_step_obj.type === 5 ' >HTTP接口请求</el-tag>
          <el-tag  v-if='one_step_obj.type === 10'>WEB自动化</el-tag>
          <el-tag  v-if='one_step_obj.type === 7 '>APP自动化</el-tag>     
          <el-tag  v-if='one_step_obj.type === 8 '>数据库操作</el-tag>
          <el-tag  v-if='one_step_obj.type === 9 '>逻辑控制器</el-tag>
          <el-tag  v-if='one_step_obj.type === 3 && one_step_obj.com_step_type ===5'>HTTP接口请求</el-tag>
          <el-tag  v-if='one_step_obj.type === 3 && one_step_obj.com_step_type ===10'>WEB自动化</el-tag>
          <el-tag  v-if='one_step_obj.type === 3 && one_step_obj.com_step_type ===7'>APP自动化</el-tag>
          <el-tag  v-if='one_step_obj.type === 3 && one_step_obj.com_step_type ===8'>数据库操作</el-tag>
          <el-tag  v-if='one_step_obj.type === 3 && one_step_obj.com_step_type ===9'>逻辑控制器</el-tag>
			  </div>
			</div>
	    </div>
      <el-collapse v-model="activeNames" class="step-collapse-panel" accordion ref="collapse" @change="onCollapseChange">
		  <el-card class='step_item_card' >
			  <el-collapse-item  name="1" >
					<template #title="{ isActive }">
						  <div class="section-divider">
							<span class="section-title">步骤变量</span>
							<el-alert
								v-if='one_step_obj.type === StepType.ComStep'
								title='公共步骤下不会共用步骤变量'
								type="info"
								:closable="false"
								show-icon
								style='width: 250px;'
							/>
						  </div>
					</template>
				<StepParams
				  :bind_case_data="case_info.data.name"
				  :tableData="one_step_obj.step_params"
				  :step_index="one_step_obj.step_index"
				  :steps="case_info.step"
				  :func_list="func_list"
				  :bind_env_params="bind_env_params"
                  :bind_global_params="bind_global_params"
				  :case_params_data="case_info.params"
				></StepParams>
			  </el-collapse-item>
		  </el-card>
		  
		  <el-card class='step_item_card' v-if="one_step_obj.type !== StepType.Control && one_step_obj.com_step_type !== StepType.Control">
			  <el-collapse-item name="2" >
					<template #title="{ isActive }">
						  <div class="section-divider">
							<span class="section-title">前置步骤</span>
						  </div>
					</template>
				<BodyEdit
				  :isShowBtn="true"
				  :bind_case_data="case_info.data.name"
				  v-model="one_step_obj.setup"
				  lang="python"
				  :is_function="false"
				  height="300px"
				  :step_index="one_step_obj.step_index"
				  :steps="case_info.step"
				  :func_list="func_list"
				  :bind_env_params="bind_env_params"
                  :bind_global_params="bind_global_params"
				  :case_params_data="case_info.params"
				></BodyEdit>
			  </el-collapse-item>
		  </el-card>
		  
		  <el-card class='step_item_card' v-if="one_step_obj.type !== StepType.Control && one_step_obj.com_step_type != StepType.Control" >
		  	<!-- <div class="section-divider" >
		  	  <span class="section-title" style='margin-left: 17px;'>基础信息</span>
			  <el-divider v-if="one_step_obj.type !== StepType.Control" style='margin-top: 0px'></el-divider>
		  	</div> -->
			<el-collapse-item  name="3" >
				<template #title="{ isActive }">
					  <div class="section-divider">
						<span class="section-title">基础信息</span>
					  </div>
				</template>
				<div class="step-base-info" v-if="one_step_obj.type !== StepType.Control">
				  <el-row :gutter="20" style='margin-top: 20px'>
				    <el-col :span="12">
				      <el-form-item label="步骤名称" prop="desc" label-width="95px" class="dialog-form-item" >
				        <FuncAndParams
				          :value="one_step_obj.desc"
				          :bind_case_data="case_info.data.name"
				          :row="row"
				          :step_index="one_step_obj.step_index"
				          :steps="case_info.step"
				          :bind_env_params="bind_env_params"
                          :bind_global_params="bind_global_params"
				          :case_table_data="case_info.params"
				          :func_list="func_list"
				          @update:value="handleUpdateDesc(one_step_obj, $event)"
				        ></FuncAndParams>
				      </el-form-item>
				    </el-col>
				    <el-col :span="6">
				      <el-form-item prop="plant" class="dialog-form-item" label-width="155px">
				        <template #label>
				          <span>步骤所属产品</span>
				          <el-tooltip placement="top" effect="light">
				            <template #content>
				              <ul>
				                <li>默认赋值为当前用例所属模块对应的产品</li>
				              </ul>
				            </template>
				            <el-icon color="green" class="info-icon"><InfoFilled /></el-icon>
				          </el-tooltip>
				        </template>
				        <el-select v-model="one_step_obj.plant" @change="getRequestHosts" class="select" size='large' popper-class='select-dropdown-rounded'>
				          <el-option v-for="plant in plant_list.results" :label="plant.name" :value="plant.id" />
				        </el-select>
				      </el-form-item>
				    </el-col>
				    <el-col :span="6">
				      <el-form-item class="dialog-form-item">
				        <template #label>
				          <span>步骤执行失败</span>
				          <el-tooltip placement="top" effect="light">
				            <template #content>
				              <ul>
				                <li>当设置为步骤执行失败(包含断言错误和脚本错误)继续执行并忽略失败时, 会把当前的测试结果设置为成功并继续执行下一步</li>
				              </ul>
				            </template>
				            <el-icon color="green" class="info-icon"><InfoFilled /></el-icon>
				          </el-tooltip>
				        </template>
				        <el-select v-model="one_step_obj.fail_is_continue" class="select" size='large' popper-class='select-dropdown-rounded'>
				            <el-option label="停止测试" :value="0" />
				            <el-option label="继续执行不忽略失败" :value="1" />
                            <el-option label="继续执行并忽略失败" :value="2" />
				        </el-select>
				      </el-form-item>
				    </el-col>
				  </el-row>
				  <el-row :gutter="20" v-if="one_step_obj.type === StepType.Request || one_step_obj.com_step_type === StepType.Request">
				    <el-col :span="5">
				      <el-form-item label="所属服务" class="dialog-form-item" prop="api_service">
				        <template #label>
						  <span>所属服务</span>
				          <el-tooltip placement="top" effect="light">
				            <template #content>
				              <ul>
				                <li>对应接口文档中的所属服务</li>
				              </ul>
				            </template>
				            <el-icon color="green" class="info-icon"><InfoFilled /></el-icon>
				          </el-tooltip>
				        </template>
				        <el-select v-model="one_step_obj.api_service" @change="getRequestHosts" disabled class="select" size='large' popper-class='select-dropdown-rounded'>
				          <el-option v-for="service in service_list" :label="service.name" :value="service.id" />
				        </el-select>
				      </el-form-item>
				    </el-col>
					<el-col :span="7" style="padding-right: 0px;">
					  <el-form-item class="dialog-form-item" >
					    <template #label>
					      <span>请求域名</span>
					      <el-tooltip placement="top" effect="light">
					        <template #content>
					          <ul>
					            <li>当前的请求域名仅用来查看该接口在当前配置下在不同环境下对应的请求域名</li>
								<li>当前接口所属服务中的接口域名配置为 -> {{ envServiceList.is_server_host ? '跟随服务域名配置': '跟随产品域名配置'}}</li>
					            <li>当接口所属服务的接口域名配置为跟随产品域名配置时, 根据当前步骤所属产品取[环境管理-产品配置-产品域名配置下对应环境和产品的产品域名]</li>
					            <li>当接口所属服务的接口域名配置为跟随服务域名配置时, 根据当前步骤所属服务取[环境管理-服务配置-服务域名配置下对应环境和服务的服务域名]</li>
					            <li v-if='envServiceList.is_server_host' style="color: red;">
					          	  <el-link type="danger" underline @click="() => this.$router.push({ name: 'service' })">如果下拉框没有显示对应的环境, 则需要去配置,点击去添加</el-link>
					            </li>
					            <li v-if='!envServiceList.is_server_host' style="color: red;">
					              <el-link type="danger" underline @click="() => this.$router.push({ name: 'plant' })">如果下拉框没有显示对应的环境, 则需要去配置,点击去添加</el-link>
					            </li>
					          </ul>
					        </template>
					        <el-icon color="green" class="info-icon"><InfoFilled /></el-icon>
					      </el-tooltip>
					    </template>
					    <el-input v-model="one_step_obj.api_host"  class="input" size='large' placeholder="选择环境后显示对应的请求域名" disabled>
					      <template #prepend>
							<el-select v-model='one_step_obj.api_host' style='width: 130px;' size='large'  popper-class='select-dropdown-rounded' placeholder="请选择环境">
								<el-option v-for="obj in envServiceList.env_hosts"  color="#50E3C2" size="large"  :label='obj.env_name' :value="obj.host"></el-option>
							</el-select>
					      </template>
					    </el-input>
					  </el-form-item>
					</el-col>
				   <el-col :span="4" style="padding-left: 40px; padding-right: 0px">
				      <el-form-item class="dialog-form-item" prop="api_method">
				        <template #label>
						  <span>请求方法/地址</span>
				        </template>
					  <el-select v-model='one_step_obj.api_method'  size='large' class="select" popper-class='select-dropdown-rounded' style='margin-left: 15px'>
					  	<el-option color="#409EFF" size="large" effect="dark" class="method-tag" label='GET' value="GET" v-if='one_step_obj.api_method === "GET"'></el-option>
					  	<el-option  size="large" color="#49CC90" effect="dark" class="method-tag" label='POST' value="POST" v-if='one_step_obj.api_method === "POST"'></el-option>
					  	<el-option  color="#F93E3E" size="large" effect="dark" class="method-tag" label='DELETE' value="DELETE" v-if='one_step_obj.api_method === "DELETE"'></el-option>
					  	<el-option  color="#FCA130" size="large" effect="dark" class="method-tag" label='PUT' value="PUT" v-if='one_step_obj.api_method === "PUT"'></el-option>
						<el-option  color="#2B6CB0" size="large" effect="dark" class="method-tag" label='OPTIONS' value="OPTIONS" v-if='one_step_obj.api_method === "OPTIONS"'></el-option>
					  	<el-option  color="#50E3C2" size="large" effect="dark" class="method-tag" label='PATCH' value="PATCH" v-if='one_step_obj.api_method === "PATCH"'></el-option>
					  	<el-option color="#9012FE" size="large" effect="dark" class="method-tag" label='HEAD' value="HEAD" v-if='one_step_obj.api_method === "HEAD"'></el-option>
					  </el-select>
				      </el-form-item>
				    </el-col>
					<el-col :span="8" style="padding-left: 0px">
					  <el-form-item class="dialog-form-item" prop="api_uri" >
					   <FuncAndParams
					     :value="one_step_obj.api_uri"
					     :bind_case_data="case_info.data.name"
					     :row="row"
					     :step_index="one_step_obj.step_index"
					     :steps="case_info.step"
					     :bind_env_params="bind_env_params"
                         :bind_global_params="bind_global_params"
					     :case_table_data="case_info.params"
					     :func_list="func_list"
					     @update:value="handleUpdateUri(one_step_obj, $event)"
					   ></FuncAndParams>
					  </el-form-item>
					</el-col>
				  </el-row>
				  <el-row :gutter="20" v-if="[StepType.Appium, StepType.Playwright].includes(one_step_obj.type) || [StepType.Appium, StepType.Playwright].includes(one_step_obj.com_step_type)">
				    <el-col :span="12">
				      <el-form-item label="步骤关键字" class="dialog-form-item" prop="keyword" label-width="95px">
				        <template #label>
				  		  	<span>步骤关键字</span>
				        </template>
				        <el-tree-select
							class='select'
							size='large'
              popper-class='select-tree-dropdown-rounded'
							v-model="one_step_obj.keyword"
							:data="web_keys"
							:props="{
							  value: 'id',
							  label: 'name',
							  children: 'children'
							}"
							placeholder="请选择关键字"
							filterable
							check-strictly
							@node-click="handleNodeClick"
							@change="handleKeywordChange"
				        />
				      </el-form-item>
				    </el-col>
					<el-col :span="24" v-if='one_step_obj.keyword'>
						<SeleniumFunc
						  :bind_case_data="case_info.data.name"
						  :permission="permission"
						  :func_params="one_step_obj.func_params"
						  :seleniumFuncData="seleniumFuncData"
						  :step_index="one_step_obj.step_index"
						  :steps="case_info.step"
						  :func_list="func_list"
						  :bind_env_params="bind_env_params"
                          :bind_global_params="bind_global_params"
						  :case_params_data="case_info.params"
						></SeleniumFunc>
					</el-col>
				</el-row>
				<el-row :gutter="20" v-if="one_step_obj.type === StepType.SQL || one_step_obj.com_step_type === StepType.SQL">
				    <el-col :span="12">
				      <el-form-item label="所属数据库" class="dialog-form-item" prop="database_name" label-width="95px">
				        <template #label>
				  		  	<span>所属数据库</span>
				        </template>
				        <el-select
				          v-model="one_step_obj.database_name" 
				          placeholder="请选择所属数据库" 
				          clearable 
				          class="select" size='large' popper-class='select-dropdown-rounded'
				        >
				          <el-option 
				            v-for="db_obj in db_list.results" 
				            :key="db_obj.id"
				            :label="db_obj.name" 
				            :value="db_obj.id" 
				          />
				        </el-select>
				      </el-form-item>
				    </el-col>
					<el-col :span="12">
						<el-form-item label="数据库操作" class="dialog-form-item" prop="keyword" label-width="155px">
						  <template #label>
							<span>数据库操作</span>
							<el-tooltip placement="top" effect="light">
							  <template #content>
							    <ul>
							      <li>默认赋值为当前用例所属模块对应的产品</li>
							    </ul>
							  </template>
							  <el-icon color="green" class="info-icon"><InfoFilled /></el-icon>
							</el-tooltip>
						  </template>
						  <el-select
						    v-model="one_step_obj.keyword"
						    placeholder="请选择数据库操作" 
						    clearable 
						    class="select" size='large' popper-class='select-dropdown-rounded'
						  >
							   <el-option label="查询数据库并获取一条数据" value='SelectFetchone'></el-option>
							   <el-option label="查询数据库并获取所有数据" value='SelectFetchall'></el-option>
							   <el-option label="更新数据库记录" value='Update'></el-option>
							   <el-option label="删除数据库记录" value='Delete'></el-option>
							   <el-option label="获取Redis数据" value='RedisGet'></el-option>
							   <el-option label="删除Redis数据" value='RedisDelete'></el-option>
						  </el-select>
						</el-form-item>
					</el-col>
				</el-row>
				<BodyEdit 
				   v-if="one_step_obj.type === StepType.SQL || one_step_obj.com_step_type === StepType.SQL"
				   :bind_case_data="case_info.data.name"
				   v-model="one_step_obj.script"
				   lang="sql" 
				   :is_function="false" 
				   height="300px">
				</BodyEdit>
				</div>
			</el-collapse-item>
		  </el-card>
		  
		  <el-card class='step_item_card'  v-if="one_step_obj.type === StepType.Control || one_step_obj.com_step_type === StepType.Control" style='margin-left: 20px'>
			  <div class="section-divider" >
				<span class="section-title" >基础信息</span>
			  </div>
			  <el-divider></el-divider>
			  <el-form-item label="步骤名称" prop="desc" label-width="90px" style="margin-top: 20px" class="dialog-form-item">
				<FuncAndParams
				  :value="one_step_obj.desc"
				  :bind_case_data="case_info.data.name"
				  :row="row"
				  :step_index="one_step_obj.step_index"
				  :steps="case_info.step"
				  :bind_env_params="bind_env_params"
                  :bind_global_params="bind_global_params"
				  :case_table_data="case_info.params"
				  :func_list="func_list"
				  @update:value="handleUpdateDesc(one_step_obj, $event)"
				></FuncAndParams>
			  </el-form-item>
			  
			  <el-form-item label="等待时间(秒)" prop="timeout" label-width="120px" v-if="(one_step_obj.type === StepType.Control || one_step_obj.com_step_type ===StepType.Control) && one_step_obj.keyword === '5'" class="dialog-form-item">
				<el-input-number v-model="one_step_obj.timeout" :step="1" :min="0.1" :precision="1" style="width: 100%;" class="input" size='large' />
			  </el-form-item>
		  </el-card>
          
		  <el-card class='step_item_card' v-if="one_step_obj.type === StepType.Request || one_step_obj.com_step_type === StepType.Request">
			  <el-collapse-item  name="4" >
				<template #title="{ isActive }">
					  <div class="section-divider">
						<span class="section-title">请求参数</span>
					  </div>
				</template>
			    <el-tabs v-model="one_step_obj.step_active_tab" class="elegant-tabs">
			      <el-tab-pane lazy="true" v-if="one_step_obj.type === StepType.Request || one_step_obj.com_step_type === StepType.Request" label="请求头" name="headers">
			        <el-row>
			          <el-form-item class="dialog-form-item">
			            <template #label>
			              <span>设置为公共请求头</span>
			              <el-tooltip placement="left" effect="light">
			                <template #content>
			                  <ul>
			                    <li>开关开启后，在当前用例下该步骤之后的所有步骤的请求头都会带上该步骤请求头参数</li>
								<li>调试时会在【环境管理-环境配置-全局请求头配置下取当前执行环境下当前用户创建的对应产品的非批跑全局请求头添加到该接口的请求头】</li>
								<li>批跑时会在【环境管理-环境配置-全局请求头配置下取当前执行环境下对应产品为批跑全局请求头添加到该接口的请求头】</li>
								<li>请求头优先级: 全局请求头 < 公共请求头 < 步骤自定义请求头</li>
			                  </ul>
			                </template>
			                <el-icon color="green" class="info-icon"><InfoFilled /></el-icon>
			              </el-tooltip>
			            </template>
			            <el-switch v-model="one_step_obj.common_headers" />
			          </el-form-item>
			        </el-row>
			        <Header
			          :bind_case_data="case_info.data.name"
			          :tableData="one_step_obj.api_headers"
			          :isApi="false"
			          :step_index="one_step_obj.step_index"
			          :steps="case_info.step"
			          :func_list="func_list"
			          :bind_env_params="bind_env_params"
                      :bind_global_params="bind_global_params"
			          :case_params_data="case_info.params"
			        ></Header>
			      </el-tab-pane>
			      <el-tab-pane lazy="true" v-if="one_step_obj.type === StepType.Request || one_step_obj.com_step_type === StepType.Request" label="Query参数" name="params">
			        <Params
			          :bind_case_data="case_info.data.name"
			          :tableData="one_step_obj.api_params"
			          :step_index="one_step_obj.step_index"
			          :steps="case_info.step"
			          :isApi="false"
			          :func_list="func_list"
			          :bind_env_params="bind_env_params"
                      :bind_global_params="bind_global_params"
			          :case_params_data="case_info.params"
			        ></Params>
			      </el-tab-pane>
			      <el-tab-pane label="请求体" name="body" v-if="one_step_obj.type === StepType.Request || one_step_obj.com_step_type === StepType.Request">
			       <el-row style="display: flex; align-items: center; gap: 30px; margin-bottom: 20px; padding: 16px; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #e4e7ed;">
			         <div style="display: flex; align-items: center; gap: 15px;">
			           <span style="font-weight: 600; color: #303133; width: 80px;">请求体类型</span>
			           <el-radio-group v-model="one_step_obj.body_type" size="large">
			             <el-radio-button :label="1" style=" text-align: center;">Json</el-radio-button>
			             <el-radio-button :label="2" style=" text-align: center;">Form</el-radio-button>
			           </el-radio-group>
			         </div>
			         
			         <div v-if="one_step_obj.body_type === 1" style="display: flex; align-items: center; gap: 15px; padding-left: 20px; border-left: 1px solid #dcdfe6;">
			           <span style="font-weight: 600; color: #303133; width: 100px;">JSON根类型</span>
			           <el-select 
			             v-model="one_step_obj.api_json_type" 
						 class="select" size='large' popper-class='select-dropdown-rounded'
			             style="width: 150px;"
			             placeholder="请选择"
			           >
			             <el-option v-for="value in json_root_type" :label="value" :value="value"></el-option>
			           </el-select>
			         </div>
			       </el-row>
			        <Data
			          v-if="one_step_obj.body_type === 2"
			          :bind_case_data="case_info.data.name"
			          :tableData="one_step_obj.api_data"
			          :isApi="false"
			          :step_index="one_step_obj.step_index"
			          :steps="case_info.step"
			          :func_list="func_list"
			          :bind_env_params="bind_env_params"
                      :bind_global_params="bind_global_params"
			          :case_params_data="case_info.params"
			        ></Data>
			        <Json
			          v-if="one_step_obj.body_type === 1"
			          :bind_case_data="case_info.data.name"
			          :tableData="one_step_obj.api_json"
			          :isApi="false"
			          :step_index="one_step_obj.step_index"
			          :steps="case_info.step"
			          :func_list="func_list"
			          :bind_env_params="bind_env_params"
                      :bind_global_params="bind_global_params"
			          :case_params_data="case_info.params"
			        ></Json>
			      </el-tab-pane>
				  <el-tab-pane lazy="true" v-if="one_step_obj.type === StepType.Request || one_step_obj.com_step_type === StepType.Request" label="请求设置" name="setting">
					<div class="request-config">
					    <div class="config-item">
					      <span class="label">超时时间
							<el-tooltip placement="left" effect="light">
							  <template #content>
							    超时时间（秒）（连接和读取总超时）。
							  </template>
							  <el-icon color="green" ><InfoFilled /></el-icon>
							</el-tooltip>
						  </span>
					      <div class="control-group">
					        <el-input-number 
					          v-model="one_step_obj.timeout" 
					          :step="1" 
					          :precision="0" 
					          :min="1" 
							  class='input'
					        
					        />
					    </div>
					   </div>
					   <div class="config-item">
						  <span class="label">验证 SSL 证书
						   <el-tooltip placement="left" effect="light">
						     <template #content>
						       是否验证 SSL 证书（默认 True）。可设为 False 跳过验证（不安全），或传入 CA 证书文件路径。
						     </template>
						     <el-icon color="green" ><InfoFilled /></el-icon>
						   </el-tooltip>
						  </span>
					      <div class="control-group">
					        <el-switch
					          v-model="one_step_obj.verify" 
					          size="large"
					          style="margin-left: 4px;"
					        />
					    </div>
					   </div>
					   <div class="config-item">
					      <span class="label">自动跟随请求重定向
							<el-tooltip placement="left" effect="light">
							  <template #content>
							    是否允许自动重定向（默认 True 用于 GET/OPTIONS，False 用于其他方法）。
							  </template>
							  <el-icon color="green" ><InfoFilled /></el-icon>
							</el-tooltip>
						  </span>
					      <div class="control-group">
					        <el-switch
					          v-model="one_step_obj.allow_redirects" 
					          size="large"
					          style="margin-left: 4px;"
					        />
					    </div>
					   </div>
					</div>
				  </el-tab-pane>
			    </el-tabs>
			  </el-collapse-item>
		  </el-card>
          
		  <el-card class='step_item_card' v-if="one_step_obj.type !== StepType.Control && one_step_obj.com_step_type !== StepType.Control">
			  <el-collapse-item  name="5" >
			    <template #title="{ isActive }">
			    	  <div class="section-divider">
			    		<span class="section-title">后置步骤</span>
			    	  </div>
			    </template>
			  			<BodyEdit
			      :isShowBtn="true"
			      :bind_case_data="case_info.data.name"
			      v-model="one_step_obj.teardown"
			      lang="python"
			      :is_function="false"
			      height="300px"
			      :step_index="one_step_obj.step_index"
			      :steps="case_info.step"
			      :func_list="func_list"
			      :bind_env_params="bind_env_params"
                  :bind_global_params="bind_global_params"
			      :case_params_data="case_info.params"
			    ></BodyEdit>
			  </el-collapse-item>
		  </el-card>
          
		  <el-card class='step_item_card'  v-if="(one_step_obj.type === StepType.Control || one_step_obj.com_step_type === StepType.Control) && one_step_obj.keyword === '1'">
			  <div class="section-divider" >
				<span class="section-title" >IF条件控制器
				</span>
				<!-- 提示文案 -->
				 <el-alert
					title='满足下面设置条件才会执行改步骤下所有子步骤'
					type="info"
					:closable="false"
					show-icon
					style='width: 350px;'
				 />
			  </div>
			  <el-divider></el-divider>
			  <IfRun
				:bind_case_data="case_info.data.name"
			   
				:tableData="one_step_obj.run_params"
				:step_index="one_step_obj.step_index"
				:steps="case_info.step"
				:func_list="func_list"
				:bind_env_params="bind_env_params"
                :bind_global_params="bind_global_params"
				:method="method"
				:case_params_data="case_info.params"
			  ></IfRun>
		  </el-card>
		  
		  
		  <el-card class='step_item_card'  v-if="(one_step_obj.type === StepType.Control || one_step_obj.com_step_type=== StepType.Control) && one_step_obj.keyword === '2'">
			  <div class="section-divider" >
				<span class="section-title" >For循环控制器</span>
				<el-alert
					title='重复执行改步骤下所有子步骤N次'
					type="info"
					:closable="false"
					show-icon
					style='width: 280px;'
				/>
			  </div>
			  <el-divider></el-divider>
			  <Loop
				:bind_case_data="case_info.data.name"
				:tableData="one_step_obj.loop"
				:step_index="one_step_obj.step_index"
				:steps="case_info.step"
				:func_list="func_list"
				:bind_env_params="bind_env_params"
                :bind_global_params="bind_global_params"
				:case_params_data="case_info.params"
			  ></Loop>
		  </el-card>
		  
		  <el-card class='step_item_card'  v-if="(one_step_obj.type === StepType.Control || one_step_obj.com_step_type === StepType.Control) && one_step_obj.keyword === '6'">
			  <div class="section-divider" >
				<span class="section-title" >Foreach循环控制器</span>
				<el-radio-group v-model="one_step_obj.body_type"  @change='foreachChange' size='small' style='margin-left:15px'>
					<el-radio-button :value="2">变量引用</el-radio-button>
					<el-radio-button :value="1">自定义数据</el-radio-button>
				</el-radio-group>
			  </div>
			  <el-divider></el-divider>
			  <Loop
			    v-if='one_step_obj.body_type === 2'
				:bind_case_data="case_info.data.name"
				:tableData="one_step_obj.loop"
				:step_index="one_step_obj.step_index"
				:steps="case_info.step"
				:func_list="func_list"
				:bind_env_params="bind_env_params"
                :bind_global_params="bind_global_params"
				:case_params_data="case_info.params"
			  ></Loop>
			  <div  v-if="one_step_obj.body_type === 1">
				  <el-row>
					  <div style="display: flex; align-items: center; gap: 15px; padding-bottom: 20px;padding-left: 20px; border-left: 1px solid #dcdfe6;">
						  <span style="font-weight: 600; color: #303133; width: 100px;">数据根类型</span>
						  <el-select 
							v-model="one_step_obj.api_json_type" 
							class="select" size='large' popper-class='select-dropdown-rounded'
							style="width: 150px;"
							placeholder="请选择"
						  >
							<el-option v-for="value in json_root_type" :label="value" :value="value"></el-option>
						  </el-select>
						  <el-alert
								title='迭代字典类型数据,参数名对应循环索引变量，参数值对应循环值变量'
								type="info"
								:closable="false"
								show-icon
								style='width: 500px;'
						 />
						 <el-alert
							title='迭代列表类型数据,循环次数对应循环索引变量，参数值对应循环值变量'
							type="info"
							:closable="false"
							show-icon
							style='width: 500px;'
						 />
						</div>
				  </el-row>
				   <Json
				     :bind_case_data="case_info.data.name"
				     :tableData="one_step_obj.loop"
				     :isApi="false"
				     :step_index="one_step_obj.step_index"
				     :steps="case_info.step"
				     :func_list="func_list"
				     :bind_env_params="bind_env_params"
                     :bind_global_params="bind_global_params"
				     :case_params_data="case_info.params"
				   ></Json>
			  </div>
		  </el-card>
		  
		  <el-card class='step_item_card'  v-if="(one_step_obj.type === StepType.Control || one_step_obj.com_step_type === StepType.Control) && one_step_obj.keyword === '3'">
			  <div class="section-divider" >
				<span class="section-title" >While条件循环控制器</span>
				<el-alert
					title='满足下面设置条件就会重复执行改步骤下所有子步骤,直到条件不满足或超过设置最大的执行次数'
					type="info"
					:closable="false"
					show-icon
					style='width: 650px;'
			 />
			  </div>
			  <el-divider></el-divider>
			  <Until
				:bind_case_data="case_info.data.name"
				
				:tableData="one_step_obj.until"
				:step_index="one_step_obj.step_index"
				:steps="case_info.step"
				:func_list="func_list"
				:method="method"
				:bind_env_params="bind_env_params"
                :bind_global_params="bind_global_params"
				:case_params_data="case_info.params"
			  ></Until>
		  </el-card>
		  
		  <el-card class='step_item_card' v-if="one_step_obj.type !== StepType.Control && one_step_obj.com_step_type !== StepType.Control">
		  	<el-collapse-item  name="6" >
		  	  <template #title="{ isActive }">
		  	  	  <div class="section-divider">
		  	  		<span class="section-title">断言规则</span>
		  	  	  </div>
		  	  </template>
			  <el-tabs  class="elegant-tabs">
				<el-tab-pane lazy="true"  label="自定义断言" >
				  <Check
				    :bind_case_data="case_info.data.name"
				    :tableData="one_step_obj.check_params"
				    :step_index="one_step_obj.step_index"
				    :steps="case_info.step"
				    :func_list="func_list"
				    :method="method"
				    :bind_env_params="bind_env_params"
                    :bind_global_params="bind_global_params"
				    :case_params_data="case_info.params"
				  ></Check>
				</el-tab-pane>
			    <el-tab-pane lazy="true"  label="JSON 文档结构校验" v-if="one_step_obj.type === StepType.Request || one_step_obj.com_step_type === StepType.Request">
			  	  <el-row style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding: 0 10px; background-color: #f8f9fa; border-radius: 8px; height: 70px;">
			  	    <div style="display: flex; align-items: center;">
			  	      <span style="margin-right: 8px; font-weight: 500; white-space: nowrap;">JSON根类型</span>
			  	      <el-select 
			  	        v-model="one_step_obj.api_response_type" 
			  	        style="width: 150px;" 
			  	        class="select" size='large' popper-class='select-dropdown-rounded'
			  	      >
			  	        <el-option v-for="value in josn_root_type" :label="value" :value="value"></el-option>
			  	      </el-select>
			  	    </div>
			  	    
			  	    <div style="display: flex; align-items: center; gap: 8px;">
			  	      <span style="font-weight: 500; white-space: nowrap;">是否开启JSON文档结构校验</span>
			  	      <el-switch 
			  	        v-model="one_step_obj.is_check" 
			  	        size="large"
			  	        style="margin-left: 4px;"
			  	      />
			  	    </div>
			  	  </el-row>
			  	  <Response
			  	    :bind_case_data="case_info.data.name"
			  	    :check_method="method"
			  	    :tableData="one_step_obj.api_response"
			  	    :isApi="false"
			  	    :step_index="one_step_obj.step_index"
			  	    :steps="case_info.step"
			  	    :func_list="func_list"
			  	    :bind_env_params="bind_env_params"
                    :bind_global_params="bind_global_params"
			  	    :case_params_data="case_info.params"
			  	  ></Response>
			    </el-tab-pane>
			  </el-tabs>
		  	</el-collapse-item>	  
		  </el-card>

           <el-card class='step_item_card'  v-if="api_test_result">
               <el-collapse-item  name="20" >
			    <template #title="{ isActive }">
			    	  <div class="section-divider" >
			    		<span class="section-title" >执行日志</span>
			    	  </div>
			    </template>
                <div class="step-log-popover-content" ref="bottomMarker">
                <el-collapse v-model="stepLogActive" accordion class="step-log-collapse">
                  <template v-for="(log, logIndex) in api_test_result" :key="logIndex">
                    <el-collapse-item :title="log.title" :name="log.title" v-if="log.hasOwnProperty('uri')" class="log-collapse-item">
                      <template #title>
                        <el-text truncated v-if="log.title.includes('【INFO】')" type="success">{{ log.title }}</el-text>
                        <el-text truncated v-if="log.title.includes('【ERROR】')" type="danger">{{ log.title }}</el-text>
                      </template>
                      <el-image
                        v-if="log.hasOwnProperty('uri')"
                        :src="log.uri"
                        :zoom-rate="1.2"
                        :max-scale="7"
                        :min-scale="0.2"
                        :preview-src-list="[log.uri]"
                        :initial-index="0"
                        fit="cover"
                      />
                    </el-collapse-item>
                    <el-collapse-item :title="log.title" :name="logIndex" class="log-collapse-item" v-else>
                      <template #title>
                        <el-text v-if="log.title.includes('【INFO】')" type="success" size="small">{{ log.title }}</el-text>
                        <el-text v-if="log.title.includes('【ERROR】')" type="danger" size="small">{{ log.title }}</el-text>
                      </template>
                      <div class="log-content">
                        <BodyEdit :bind_case_data="case_info.data.name" v-model="api_test_result[logIndex].value" readonly height="250px"></BodyEdit>
                      </div>
                    </el-collapse-item>
                  </template>
                </el-collapse>
              </div>
			  </el-collapse-item>
		  </el-card>
          
      </el-collapse>
	  </el-form>
    </el-card>
    <template #footer>
      <div class="drawer-footer">
        <el-button type="primary" @click="() => { this.editStepDetailVisible = false; this.getCase() }" class="dialog-cancel-btn">
          <span class="button-text">取消</span>
        </el-button>
		<el-button
		  @click="setApiVisible" 
		  class="dialog-confirm-btn" 
		 
		  v-if="one_step_obj.type === StepType.Request || one_step_obj.com_step_type === StepType.Request"
		><span class="button-text">从接口文档同步</span>
		</el-button>
		<el-button
		  @click="actionChange" 
		  class="dialog-confirm-btn" 
		  v-if="one_step_obj.type === 5 || one_step_obj.com_step_type ===5"
		>
		  <span class="button-text">选择接口</span>
		</el-button>
		<el-button
		  @click="step_control_run(one_step_obj.step_index)"
		  class="dialog-confirm-btn"
		  style='margin-left: 20px'
		  v-if='(one_step_obj.type === 5 && this.one_step_obj.id) ||(one_step_obj.com_step_type === 5 && this.one_step_obj.id)'
		>
		  <span class="button-text">执行步骤</span>
		</el-button>
		<el-button v-if="!caseView && !stepView" type="primary" @click="saveStepClose(false)" :loading="loading" class="dialog-confirm-btn">
		  <span class="button-text">保存</span>
		</el-button>
        <el-button v-if="!caseView && !stepView" type="primary" @click="saveStepClose(true)" :loading="loading" class="dialog-confirm-btn">
          <span class="button-text" >保存并关闭</span>
        </el-button>
      </div>
    </template>
  </el-drawer>

  <!-- 主内容区域 -->
  <div class="case-edit-container">
    <el-card class="content-card elegant-shadow">
      <div class="content-header">
        <!-- 第一行：用例名称 + 操作按钮 -->
        <div class="header-top">
          <div class="case-title-area">
            <h3 class="content-title">{{ case_info.name }}</h3>
          </div>
          <div class="action-buttons">
            <!-- 返回按钮保持原样 -->
            <el-button class="action-btn back-btn" @click="() => { this.$router.go(-1) }">
              <el-icon><ArrowLeft /></el-icon>返回
            </el-button>
			
            <!-- 其他按钮保持完整文字 -->
            <el-button class="action-btn history-btn" @click="look_logs">
              <el-icon><Clock /></el-icon>测试历史
            </el-button>
			<el-button v-if="permission.has_edit_permission" class="action-btn params-btn" @click="editParamsVisible = true">
			  <el-icon><Setting /></el-icon>添加变量
			</el-button>
			<el-button v-if="permission.has_edit_permission" class="action-btn data-btn" @click="editDataVisible = true">
			  <el-icon><DocumentAdd /></el-icon>数据驱动
			</el-button>
            <el-button class="action-btn run-btn" @click="run" v-if="!caseView">
              <el-icon><VideoPlay /></el-icon>执行用例
            </el-button>
            <el-button class="action-btn load-btn" @click="() => { this.locustRunVisible = true }" v-if="!caseView && case_info.type === 5">
              <el-icon><TrendCharts /></el-icon>性能压测
            </el-button>
            <el-dropdown @command="controlCommand" style='padding-right: 10px;padding-left: 10px' class="control-dropdown" v-if="permission.has_add_permission">
              <el-button type="primary" class="action-btn control-btn">
                <el-icon><SetUp /></el-icon>添加控制器
              </el-button>
              <template #dropdown>
                <el-dropdown-menu class="control-menu">
                  <el-dropdown-item divided command="1" class="control-item">
                    <el-icon><CircleCheck /></el-icon>IF条件控制器
                  </el-dropdown-item>
                  <el-dropdown-item divided command="2" class="control-item">
                    <el-icon><RefreshRight /></el-icon>For循环控制器
                  </el-dropdown-item>
				  <el-dropdown-item divided command="6" class="control-item">
				    <el-icon><RefreshLeft /></el-icon>Foreach循环控制器
				  </el-dropdown-item>
                  <el-dropdown-item divided command="3" class="control-item">
                    <el-icon><Refresh /></el-icon>While条件控制器
                  </el-dropdown-item>
                  <el-dropdown-item v-if="case_info.type === 5" divided command="4" class="control-item">
                    <el-icon><Document /></el-icon>事务控制器
                  </el-dropdown-item>
                  <el-dropdown-item divided command="5" class="control-item">
                    <el-icon><Timer /></el-icon>等待时间控制器
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
			
			<el-dropdown @command="controlStepCommand" class="control-dropdown" v-if="permission.has_add_permission">
			  <el-button type="primary" class="action-btn add-btn">
			    <el-icon><Plus /></el-icon>添加步骤
			  </el-button>
			  <template #dropdown>
			    <el-dropdown-menu class="control-menu">
			      <el-dropdown-item divided :command="5" class="control-item">
			        <el-icon><Link /></el-icon>HTTP接口请求
			      </el-dropdown-item>
				  <el-dropdown-item divided :command="8" class="control-item">
				    <el-icon><CircleCheck /></el-icon>数据库操作
				  </el-dropdown-item>
			      <el-dropdown-item divided :command="10" class="control-item" v-if='case_info.type === 2'>
			        <el-icon><Mouse /></el-icon>Web自动化
			      </el-dropdown-item>
			      <el-dropdown-item divided :command="7" class="control-item" v-if='case_info.type === 3'>
			        <el-icon><Iphone /></el-icon>App自动化
			      </el-dropdown-item>
			      <el-dropdown-item divided :command="3" class="control-item">
			        <el-icon><Connection /></el-icon>复用已有步骤
			      </el-dropdown-item>
				  <el-dropdown-item divided :command="6" class="control-item">
				    <el-icon><Postcard /></el-icon>引用并创建新步骤
				  </el-dropdown-item>
			    </el-dropdown-menu>
			  </template>
			</el-dropdown>
            
          </div>
        </div>
        
        <!-- 第二行：用例信息 -->
        <div class="header-bottom">
          <div class="case-meta">
			<div class="meta-item">
			  <span class="meta-label">用例标签</span>
			  <el-tag class="meta-value" v-for="obj in case_info.tag_name" >{{ obj.name }}</el-tag>
			</div>
			<div class="meta-divider"></div>
            <div class="meta-item">
              <span class="meta-label">创建人</span>
              <span class="meta-value">{{ case_info.create_by_name || '未知' }}</span>
            </div>
            <div class="meta-divider"></div>
			<div class="meta-item">
			  <span class="meta-label">创建时间</span>
			  <span class="meta-value">{{ formatTime(case_info.create_time) }}</span>
			</div>
			<div class="meta-divider"></div>
            <div class="meta-item">
              <span class="meta-label">更新人</span>
              <span class="meta-value">{{ case_info.update_by_name || '未知' }}</span>
            </div>
			<div class="meta-divider"></div>
			<div class="meta-item">
			  <span class="meta-label">更新时间</span>
			  <span class="meta-value">{{ formatTime(case_info.update_time) }}</span>
			</div>
            <div class="meta-divider"></div>
            <div class="stats-item">
              <span class="stat-label">总步骤数</span>
              <span class="stat-value">{{ case_info.step ? case_info.step.length : 0 }}</span>
            </div>
            <div class="stats-item">
              <span class="stat-label">执行次数</span>
              <span class="stat-value">{{ case_info.all_run_times || 0 }}</span>
            </div>
            <div class="stats-item">
              <span class="stat-label">成功率</span>
              <span class="stat-value success-rate">{{ case_info.all_run_times ? ((case_info.all_success_times / case_info.all_run_times) * 100).toFixed(1) + '%' : '0%' }}</span>
			  
            </div>
			<div>
				<el-alert
					title='按住鼠标左键拖动可以修改步骤顺序,按住Ctrl拖动可以为逻辑控制器添加子步骤'
					type="info"
					:closable="false"
					show-icon
					
				/>
			</div>
			
          </div> 
        </div>
      </div>
	  
      <!-- 步骤表格 -->
      <div class="table-wrapper">
        <vxe-table
          ref="tableRef"
          header-align="center"
          @cell-dblclick="editStep"
          @row-dragend="rowdrageEnd"
          :row-drag-config="{ trigger: 'row', isCrossDrag: true, isSelfToChildDrag: false, isToChildDrag: true, isPeerDrag: true }"
          :row-config="{ drag: true, keyField: 'case_step_id' }"
          :cell-config="{ height: 45 }"
          show-overflow
          :tree-config="treeConfig"
          :data="case_info.step"
          class="elegant-vxe-table"
        >
          <vxe-column field="desc" title="步骤名称" min-width="300" align="left" tree-node>
            <template #default="{ row }">
              <el-tooltip effect="dark" :content="row.desc" placement="top-start">
                <el-link v-if="row.desc.length <= 30" type="primary" @click="editStepTwo(row)" class="step-link">
                  {{ row.step_index + 1 }}. {{ row.desc }}
                </el-link>
                <el-link v-else type="primary" @click="editStepTwo(row)" class="step-link">
                  {{ row.step_index + 1 }}. {{ row.desc.slice(0, 30) }}...
                </el-link>
              </el-tooltip>
			  <!-- 关键改动：遍历该步骤的所有执行记录，生成多个标签 -->
                <template
                  v-for="(execution, execIndex) in getStepExecutions(row.step_index)"
                  :key="execIndex"
                >
                  <el-popover
                    placement="right"
                    width="50vw"
                    trigger="hover"
                    :popper-class="'step-log-popover'"
                  >
                    <!-- 引用插槽：显示状态标签（第N次执行） -->
                    <template #reference>
                      <!-- 判断本次执行是否有 ERROR -->
                      <el-tag
                        style="margin-left: 10px"
                        :type="hasExecutionError(execution) ? 'danger' : 'success'"
                      >
                        {{ hasExecutionError(execution) ? '失败' : '成功' }}
                      </el-tag>
                    </template>

                    <!-- 悬浮弹窗内容：只显示本次执行（execution）的详细日志 -->
                    <template #default>
                      <div class="step-log-popover-content">
                        <h4 class="step-log-title">
                          <template v-if="getStepExecutions(row.step_index).length > 1">
                            步骤【{{ row.desc }}】- 第 {{ execIndex + 1 }} 次执行日志
                          </template>
                          <template v-else>
                            步骤【{{ row.desc }}】执行日志
                          </template>
                        </h4>

                        <el-collapse v-model="stepLogActive" accordion class="step-log-collapse">
                          <!-- 遍历本次执行中的详细子日志 -->
                          <template v-for="(subLog, subIdx) in execution.logs" :key="subIdx">
                            <el-collapse-item
                              :title="subLog.title"
                              :name="`${row.step_index}-${execIndex}-${subIdx}`"
                              class="log-collapse-item"
                            >
                              <template #title>
                                <el-text
                                  v-if="subLog.title && subLog.title.includes('【INFO】')"
                                  type="success"
                                  size="small"
                                >
                                  {{ subLog.title }}
                                </el-text>
                                <el-text
                                  v-if="subLog.title && subLog.title.includes('【ERROR】')"
                                  type="danger"
                                  size="small"
                                >
                                  {{ subLog.title }}
                                </el-text>
                              </template>

                              <!-- 如果是图片（截图） -->
                              <div v-if="subLog.hasOwnProperty('uri')">
                                <el-image
                                  :src="subLog.uri"
                                  :zoom-rate="1.2"
                                  :max-scale="7"
                                  :min-scale="0.2"
                                  :preview-src-list="[subLog.uri]"
                                  fit="cover"
                                />
                              </div>
                              <!-- 如果是普通日志内容 -->
                              <div v-else class="log-content">
                                <BodyEdit
                                  :bind_case_data="case_info.data.name"
                                  v-model="subLog.value"
                                  readonly
                                  height="250px"
                                />
                              </div>
                            </el-collapse-item>
                          </template>
                        </el-collapse>
                      </div>
                    </template>
                  </el-popover>
                </template>
            </template>
          </vxe-column>
          <vxe-column field="type_name" title="步骤类型" min-width="150" align="center" header-align="center">
            <template #default="{ row }">
              <div >
                <el-tag v-if="row.type === 5 || row.com_step_type === 5"  effect="light" class="type-tag method-tag">HTTP接口请求</el-tag>
				<el-tag v-if="row.type === 10 || row.com_step_type === 10"  effect="light" class="type-tag method-tag">Web自动化</el-tag>
                <el-tag v-if="row.type === 7 || row.com_step_type === 7"  effect="light" class="type-tag method-tag">APP自动化</el-tag>
				<el-tag v-if="row.type === 8 || row.com_step_type === 8"  effect="light" class="type-tag method-tag">数据库操作</el-tag>
                <el-tag v-if="(row.type === 9 || row.com_step_type === 9) && row.keyword === '1'"  effect="light" class="type-tag method-tag">IF条件控制器</el-tag>
                <el-tag v-if="(row.type === 9 || row.com_step_type === 9) && row.keyword === '2'"  effect="light" class="type-tag method-tag">FOR循环控制器</el-tag>
                <el-tag v-if="(row.type === 9 || row.com_step_type === 9) && row.keyword === '3'"  effect="light" class="type-tag method-tag">WHILE控制器</el-tag>
                <el-tag v-if="(row.type === 9 || row.com_step_type === 9) && row.keyword === '4'"  effect="light" class="type-tag method-tag">事务控制器</el-tag>
                <el-tag v-if="(row.type === 9 || row.com_step_type === 9) && row.keyword === '5'"  effect="light" class="type-tag method-tag">等待时间控制器</el-tag>
              </div>
            </template>
          </vxe-column>
          <vxe-column field="is_run" title="是否执行" width="80" align="center">
              <template #header>
              <el-tooltip
                content="是否执行该用例步骤"
                placement="top"
                :disabled="!permission.has_edit_permission"
              >
                <el-switch
                  v-model="isAllRun"
                  @change="toggleAllRun"
                  :disabled="!permission.has_edit_permission"
                  class="run-switch"
                />
              </el-tooltip>
            </template>
            <template #default="{ row }">
                <el-tooltip
                content="是否执行该用例步骤"
                placement="top"
                :disabled="!permission.has_edit_permission"
              >
                <el-switch v-model="row.is_run" @change="isRunChange(row.case_step_id, row.is_run)" :disabled="!permission.has_edit_permission" class="run-switch" />
              </el-tooltip>

            </template>
          </vxe-column>
          <vxe-column field="plant_name" title="所属产品" width="150" align="center" />
          <vxe-column field="fail_is_continue" title="步骤失败" width="150" align="center">
            <template #default="{ row, rowIndex }">
              <el-tag v-if="row.fail_is_continue === 0" type="warning" size="small" effect="light">停止测试</el-tag>
              <el-tag v-if="row.fail_is_continue === 1" type="danger" size="small" effect="light">继续执行不忽略失败</el-tag>
                <el-tag v-if="row.fail_is_continue === 2" type="info" size="small" effect="light">继续执行并忽略失败</el-tag>
            </template>
          </vxe-column>
		  
           <!-- 合并创建人和创建时间 -->
		 <vxe-column field="create_info" title="创建信息" width="200" align="center">
			  <template #default="{ row }">
				<div class="user-time-cell">
				  <div class="user-info">
				    <i class="icon-user"></i>
				    <span class="user-name">{{ row.create_by_name || '-' }}</span>
				  </div>
				  <div class="time-info">
				    <i class="icon-time-small"></i>
				    <span class="time-text">{{ formatTime(row.create_time) }}</span>
				  </div>
				</div>
			  </template>
			</vxe-column>
			<!-- 合并更新人和更新时间 -->
			<vxe-column field="update_info" title="更新信息" width="200" align="center">
			  <template #default="{ row }">
				<div class="user-time-cell">
				  <div class="user-info">
				    <i class="icon-user"></i>
				    <span class="user-name">{{ row.create_by_name || '-' }}</span>
				  </div>
				  <div class="time-info">
				    <i class="icon-time-small"></i>
				    <span class="time-text">{{ formatTime(row.create_time) }}</span>
				  </div>
				</div>
			  </template>
			</vxe-column>
			<vxe-column title="操作" :width="calcMinWidth" header-align="center" align="center">
			  <template #default="{ row, rowIndex }">
				<div class="table-action-buttons">
				  <el-tooltip content="查看步骤">
					<el-button type="success" v-if="permission.has_read_permission" :icon="View" @click="viewStep(row)" circle class="table-action-btn view-btn"></el-button>
				  </el-tooltip>
				  <el-tooltip content="编辑步骤" v-if="permission.has_edit_permission">
					<el-button type="warning" :icon="EditPen" @click="editStepTwo(row)" circle class="table-action-btn edit-btn"></el-button>
				  </el-tooltip>
				  <el-tooltip content="复制" v-if="permission.has_add_permission">
					<el-button type="primary" :icon="CopyDocument" @click="copyStep(row)" circle class="table-action-btn copy-btn"></el-button>
				  </el-tooltip>
				  <el-tooltip content="删除" v-if="permission.has_delete_permission">
					<el-button type="danger" :icon="Delete" @click="confimDeleteStep(row)" circle class="table-action-btn delete-btn"></el-button>
				  </el-tooltip>
				</div>
			  </template>
			</vxe-column>
        </vxe-table>
      </div>
    </el-card>
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Delete,
  EditPen,
  CopyDocument,
  View,
  Link,
  Pointer,
  ArrowDown,
  ArrowLeft,
  Clock,
  VideoPlay,
  TrendCharts,
  Plus,
  SetUp,
  CircleCheck,
  Refresh,
  RefreshRight,
  Document,
  Timer,
  DocumentAdd,
  Setting,
  Download,
  InfoFilled
} from '@element-plus/icons-vue'
import ApiList from '../../components/ApiList.vue'
import {v4 as uuidv4} from 'uuid'
import PythonFunctionList from '../../components/PythonFunctionList.vue'
import FuncAndParams from '../../components/FuncAndParams.vue'
import StepList from '../../components/StepList.vue'
import SeleniumList from '../../components/SeleniumList.vue'
import AppiumList from '../../components/AppiumList.vue'
import BodyEdit from '../../components/BodyEdit.vue'
import PythonFunc from '../../components/PythonFunc.vue'
import SeleniumFunc from '../../components/SeleniumFunc.vue'
import TraceReplay from '../../components/TraceReplay.vue'
import Header from '../../components/Header.vue'
import Params from '../../components/Params.vue'
import CaseData from '../../components/CaseData.vue'
import SqlInsert from '../../components/SqlInsert.vue'
import Json from '../../components/Json.vue'
import Data from '../../components/Data.vue'
import CaseParams from '../../components/CaseParams.vue'
import StepParams from '../../components/StepParams.vue'
import Check from '../../components/Check.vue'
import Args from '../../components/Args.vue'
import IfRun from '../../components/IfRun.vue'
import Loop from '../../components/Loop.vue'
import Until from '../../components/Until.vue'
import Response from '../../components/Response.vue'
import * as common from '../../utils/common.js'

export default {
  name: 'CaseEdit',
  setup() {
    return {
      Delete,
      EditPen,
      CopyDocument,
      View,
      Link,
      Pointer,
      ArrowDown,
      ArrowLeft,
      Clock,
      VideoPlay,
      TrendCharts,
      Plus,
      SetUp,
      CircleCheck,
      Refresh,
      RefreshRight,
      Document,
      Timer,
      DocumentAdd,
      Setting,
      Download,
      InfoFilled
    }
  },
  data() {
    return {
      fill_color: 'green',
      activeNames: '3',
      selenium_label: '',
      tab_name: 'config',
      name: '',
      caseView: false,
      stepView: false,
	  api_test_result: '',
      json_root_type: ['object', 'array'],
      //用例信息
      case_info: {},
      db_list: [],
      caseRunForm: {
        env_id: '',
        case_id: '',
        case_data: 0,
        run_times: 1,
		fail_is_continue: 0, //步骤失败是否重复执行
        is_async: false,
        step_index: 0,
        web_executor_id: '',
        app_executor_id: '',
        // header_id: '',
        // cooke_id: ''
      },
      locustRunForm: {
        env_id: '',
        case_id: '',
        users_per_second: 1,
        concurrent_users: 1,
        durations: 1,
        // is_async: false,
        // web_executor_id: '',
        // app_executor_id: '',
        // header_id: '',
        // cooke_id: ''
      },
      treeConfig: {
        transform: true,
        rowField: 'case_step_id',
        parentField: 'parent_id',
        expandAll: true,
        iconOpen: 'vxe-icon-square-minus',
        iconClose: 'vxe-icon-square-plus'
      },
      loading: false,
      runTimesVisible: false,
      locustRunVisible: false,
      web_executor_list: [],
      app_executor_list: [],
      run_result: 0,
      apiData: '',
      josn_root_type: ['object', 'array'],
      //用来存放系统函数
      func_list: [],
      caseActive: '',
      stepActive: '',
      logActive: '',
      stepLogActive: '',
      bind_env_params: [],
      bind_global_params: [],
      bind_case_params: [],
      bind_step_params: [],
      chooseApiVisible: false,
      choosePythonFuncVisible: false,
      chooseSeleniumVisible: false,
      chooseAppiumVisible: false,
      pythonFuncData: {},
      seleniumFuncData: {},
      appiumFuncData: {},
      chooseStepVisible: false,
      chooseComStepVisible: false,
      loadApiVisible: false,
      loadResponseIndex: 0,
      loadTypeList: ['Url', 'Headers', 'Params', 'Body'],
      permissions: [],
      permission: {},
	  web_keys: [],
	  tmp_logs: [],
      editParamsVisible: false,
      StepControlCaseData: false,
      editDataVisible: false,
      editStepParamsVisible: false,
      stepRowInfo: {},
      editStepDetailVisible: false,
      lookLogVisible: false,
      single_step_tab: 'step_base_info',
      condition_tab: 'If',
      one_step_obj_tmp: {},
      one_step_obj: {
        id: 0,
        parent_id: null,
        step_index: '',
        step_active_tab: 'body',
		api_host: '',
        timeout: 7,
		allow_redirects: true,
		verify: false,
        project: 0, //所属项目
        database_name: '', //所属数据库
        desc: '新增步骤', //步骤名称
        type: '', //步骤类型
        tmp_type: '',
        com_step_type: '', //步骤类型
        keyword: '', //步骤关键字
        is_run: true, //步骤是否执行
        is_check: false, //是否开启json文档校验
        common_headers: false, //步骤是否添加请求头
        fail_is_continue: 0, //步骤失败是否重复执行
        api_all: '', //返回的api总数据
        api_service: '', //api所属服务
        plant: '',
        api_method: '', //api请求方法
        api_uri: '', //api请求网址
        api_headers: [], //api 请求头
        response_body_deal: '',
        data_body_deal: '',
        json_body_deal: '',
        api_json: [], //api 请求体
        api_json_tree: [],
        api_json_type: 'object',
        api_data: [], //api 请求体 form-data
        body_type: 1,
        api_response: [], //api返回体
        api_response_tree: [],
        api_response_type: 'object',
        api_params: [], //api查询参数
        step_after: false,
        extract: [], //数据提取参数
        check_params: [], //断言参数
        run_params: [], //是否执行条件参数
        step_params: [], //步骤变量参数
        loop: [], //循环执行参数
        until: [],
        script: '',
        teardown: '',
        setup: '',
        func_params: [] //函数入参
      },
      title: '',
      stepRules: {
        desc: [
          {
            required: true,
            message: '请输入用例步骤名称',
            trigger: 'blur'
          }
        ],
		keyword: [
		  {
		    required: true,
		    message: '请选择步骤关键字',
		    trigger: 'change'
		  }
		],
		database_name: [
		  {
		    required: true,
		    message: '请选择所属数据库',
		    trigger: 'change'
		  }
		],
		api_uri: [
		  {
		    required: true,
		    message: '请输入请求地址',
		    trigger: 'blur'
		  }
		],
		api_method: [
		  {
		    required: true,
		    message: '请输入请求方方法',
		    trigger: 'blur'
		  }
		],
		api_service: [
		  {
		    required: true,
		    message: '请选择所属服务',
		    trigger: 'blur'
		  }
		],
        timeout: [
          {
            required: true,
            message: '等待时间不能为空',
            trigger: 'blur'
          }
        ],
        type: [
          {
            required: true,
            message: '请选择步骤类型',
            trigger: 'change'
          }
        ],
        plant: [
          {
            required: true,
            message: '请选择所属产品',
            trigger: 'change'
          }
        ]
      },
      page_size_params: {
        page: 1,
        size: 1
      },
      env_list: [],
      envServiceList: [],
      method: [],
      case_logs: {},
      service_list: [],
      plant_list: [],
      StepType: {
        Request: 5,
        Selenium: 2,
		Playwright: 10,
        Appium: 7,
        ComStep: 3,
        Step: 6,
        PythonScript: 4,
        SQL: 8,
        Control: 9
      }
    }
  },
  components: {
    BodyEdit,
    TraceReplay,
    Header,
    Params,
    Json,
    Data,
    CaseParams,
    FuncAndParams,
    PythonFunctionList,
    PythonFunc,
    SeleniumFunc,
    Check,
    Args,
    IfRun,
    Loop,
    Until,
    Response,
    ApiList,
    StepList,
    SeleniumList,
    AppiumList,
    StepParams,
    CaseData,
    SqlInsert
  },
  computed: {
    ...mapState(['projectInfo', 'env_id', 'userInfo', 'pathPermission']),
    isAllRun: {
        get() {
          // 如果列表为空，返回 false
          if (!this.case_info.step || this.case_info.step.length === 0) return false;
          // 只有当所有行的 is_run 都为 true 时，表头开关才为开启状态
          return this.case_info.step.every(row => row.is_run === true);
        },
        set(val) {
          // val 为 true 表示全开，false 表示全关
          // 批量更新所有行的状态
          const ids = this.case_info.step.map(row => row.case_step_id);
          this.case_info.step.forEach(row => {
            row.is_run = val;
          });
          this.isRunChange(1, val, true, ids)
          // 【重要】关于后续保存逻辑的说明，见下方“特别建议”
          // 如果你需要实时触发接口保存，建议在此处调用批量保存接口，而不是循环调用 this.isRunChange
        }
    },
    isWebUI() {
      return this.case_info.type?.includes?.('WEB_UI') || false
    },
    isAppUI() {
      return this.case_info.type?.includes?.('APP_UI') || false
    },
    calcMinWidth() {
      let visibleButtons = 0
      if (this.permission.has_read_permission) visibleButtons += 1
      if (this.permission.has_add_permission) visibleButtons += 1 // header中的新增按钮
      if (this.permission.has_edit_permission) visibleButtons += 1
      if (this.permission.has_delete_permission) visibleButtons += 1

      // 每个按钮约85px，加上一些边距
      return Math.max(10, visibleButtons * 55)
    }
  },
  methods: {
    getStepExecutions(stepIndex) {
      if (!this.tmp_logs || !Array.isArray(this.tmp_logs)) return [];
      // 根据后端传的 step_index 或 case_step_id 进行过滤
      return this.tmp_logs.filter(log => log.step_index === stepIndex);
    },

    // 2. 判断某次执行中是否包含错误（决定标签颜色）
    hasExecutionError(execution) {
      if (!execution.logs) return false;
      return execution.logs.some(subLog =>
        subLog.title && subLog.title.includes('【ERROR】')
      );
    },
    async getEnvs() {
      const response = await this.$api.getEnvs({ project: this.projectInfo.id })
      if (response.status === 200) {
        this.env_list = { ...response.data }
      }
    },

    async getGlobalPars() {
      const response = await this.$api.getGlobalPars({ project: this.projectInfo.id })
      if (response.status === 200) {
        this.bind_global_params = [...response.data.results]
      }
    },
	
	foreachChange(){
		this.one_step_obj.loop = []
	},
	// 格式化时间显示
	formatTime(timeString) {
	  if (!timeString) return ''
	  if (timeString === undefined ) return ''
	  const date = new Date(timeString)
	  const year = date.getFullYear()
	  const month = String(date.getMonth() + 1).padStart(2, '0')
	  const day = String(date.getDate()).padStart(2, '0')
	  const hours = String(date.getHours()).padStart(2, '0')
	  const minutes = String(date.getMinutes()).padStart(2, '0')
	  return `${year}-${month}-${day} ${hours}:${minutes}`
	},
	
    controlCommand(command) {
      this.stepView = false
      this.loading = false
      this.one_step_obj = { ...this.one_step_obj_tmp }
      this.one_step_obj.type = this.StepType.Control
      this.single_step_tab = 'control'
      this.editStepDetailVisible = true
      this.one_step_obj.step_index = this.case_info.step.length - 1
      this.one_step_obj.plant = this.case_info.plant
      this.one_step_obj.com_step_type = this.StepType.Control
      if (command === '1') {
        this.one_step_obj.keyword = '1'
        this.one_step_obj.desc = '新增IF条件控制器'
      } else if (command === '2') {
        this.one_step_obj.keyword = '2'
        this.one_step_obj.desc = '新增For循环控制器'
      } else if (command === '3') {
        this.one_step_obj.keyword = '3'
        this.one_step_obj.desc = '新增While条件控制器'
      } else if (command === '4') {
        this.one_step_obj.keyword = '4'
        this.one_step_obj.desc = '新增事务件控制器'
      } else if (command === '5') {
        this.one_step_obj.keyword = '5'
        this.one_step_obj.desc = '新增等待时间控制器'
      }else if (command === '6') {
        this.one_step_obj.keyword = '6'
        this.one_step_obj.desc = '新增Foreach循环控制器'
      }
    },
	controlStepCommand(command) {
	  this.stepView = false
	  this.loading = false
	  this.one_step_obj = { ...this.one_step_obj_tmp }
	  this.one_step_obj.type = command
	  this.editStepDetailVisible = true
	  this.one_step_obj.step_index = this.case_info.step.length - 1
	  this.one_step_obj.plant = this.case_info.plant
	  this.one_step_obj.com_step_type = command
	  this.actionChange(command)
	  this.$refs.collapse.setActiveNames('3')
	},
    handleUpdateDesc(one_step_obj, newValue) {
      one_step_obj.desc = newValue // 更新父组件的数据
    },
	handleUpdateUri(one_step_obj, newValue) {
	  console.log(newValue, 'test')
	  one_step_obj.api_uri = newValue // 更新父组件的数据
	},
    handleUpdateJson(one_step_obj, newValue) {
      one_step_obj.json_body_deal = newValue // 更新父组件的数据
    },
    handleUpdateData(one_step_obj, newValue) {
      one_step_obj.data_body_deal = newValue // 更新父组件的数据
    },
    handleUpdateResponse(one_step_obj, newValue) {
      one_step_obj.response_body_deal = newValue // 更新父组件的数据
    },
    resultChange() {
      this.getCaseLogs()
    },
    handleCurrentChange() {
      this.getCaseLogs()
    },
    handleSizeChange() {
      this.getCaseLogs()
    },
    editStepParams(row) {
      this.editStepParamsVisible = true
      this.stepRowInfo = { ...row }
    },
    setApiVisible() {
      this.getApi()
    },
    async getApi() {
      const response = await this.$api.getApi(this.one_step_obj.keyword)
      if (response.status === 200) {
        this.setApiData(response.data.result)
      }
    },
    rowdrageEnd({ newRow, oldRow, dragPos, dragToChild, offsetIndex, $event }) {
      if (dragToChild) {
        if (newRow.type !== this.StepType.Control) {
          ElMessage({ message: '父级必须是逻辑控制器', type: 'error' })
          this.getCase()
          return
        }
        if (newRow.keyword === '5') {
          ElMessage({ message: '父级不能是等待时间控制器', type: 'error' })
          this.getCase()
          return
        }
      }
      const data = this.$refs.tableRef.getTableData().fullData
      this.change_step_index({ data: data })
    },
    loadApi() {
      this.one_step_obj.desc = this.one_step_obj.api_all.name
	  if (this.loadTypeList.includes('Url')) {
	    this.one_step_obj.api_uri = this.one_step_obj.api_all.url
	  }
      if (this.loadTypeList.includes('Headers')) {
		 this.one_step_obj.api_headers = this.mergeParamLists(this.one_step_obj.api_all.headers, this.one_step_obj.api_headers);
        // this.one_step_obj.api_headers = this.one_step_obj.api_all.headers
      }
      if (this.loadTypeList.includes('Params')) {
		this.one_step_obj.api_params = this.mergeParamLists(this.one_step_obj.api_all.params, this.one_step_obj.api_params);
        // this.one_step_obj.api_params = this.one_step_obj.api_all.params
      }
      if (this.loadTypeList.includes('Body')) {
		this.one_step_obj.api_json = this.mergeParamLists(this.one_step_obj.api_all.json, this.one_step_obj.api_json);
		this.one_step_obj.api_data = this.mergeParamLists(this.one_step_obj.api_all.data, this.one_step_obj.api_data);
  //       this.one_step_obj.api_json = this.one_step_obj.api_all.json
		// this.one_step_obj.api_data = this.one_step_obj.api_all.data
      }
      if (this.loadResponseIndex !== '') {
        this.one_step_obj.api_response = this.one_step_obj.api_all.response[this.loadResponseIndex].response_data
      }
      this.loadApiVisible = false
    },
	/**
	 * 合并接口文档参数列表与测试用例现有参数列表（扁平数组，通过 parentId 关联）
	 * @param {Array} sourceList 接口文档中的参数列表（扁平数组）
	 * @param {Array} targetList 测试用例中已有的参数列表（扁平数组）
	 * @returns {Array} 合并后的新参数列表（扁平数组）
	 */
	mergeParamLists(sourceList, targetList) {
	  // 防御性处理
	  const src = Array.isArray(sourceList) ? sourceList : [];
	  const tgt = Array.isArray(targetList) ? targetList : [];
	
	  // ----- 1. 构建源数据映射，并计算每个源参数的路径（用于匹配）-----
	  const srcMap = new Map(); // id -> source对象
	  src.forEach(item => srcMap.set(item.id, item));
	
	  // 计算源参数路径的函数（递归获取父节点名称）
	  const getSrcPath = (item, pathArr = []) => {
	    const name = item.name;
	    const currentPath = [name, ...pathArr];
	    if (item.parentId && srcMap.has(item.parentId)) {
	      const parent = srcMap.get(item.parentId);
	      return getSrcPath(parent, currentPath);
	    }
	    return currentPath.reverse().join('/'); // 从根到当前节点的路径
	  };
	
	  const srcPathMap = new Map(); // 路径 -> 源对象（注意：同一路径应唯一，因为同一父节点下 name 唯一）
	  src.forEach(item => {
	    const path = getSrcPath(item);
	    srcPathMap.set(path, item);
	  });
	
	  // ----- 2. 构建目标数据映射，并计算每个目标参数的路径 -----
	  const tgtMap = new Map(); // id -> target对象
	  tgt.forEach(item => tgtMap.set(item.id, item));
	
	  const getTgtPath = (item, pathArr = []) => {
	    const name = item.name;
	    const currentPath = [name, ...pathArr];
	    if (item.parentId && tgtMap.has(item.parentId)) {
	      const parent = tgtMap.get(item.parentId);
	      return getTgtPath(parent, currentPath);
	    }
	    return currentPath.reverse().join('/');
	  };
	
	  const tgtPathMap = new Map(); // 路径 -> 目标对象
	  tgt.forEach(item => {
	    const path = getTgtPath(item);
	    tgtPathMap.set(path, item);
	  });
	
	  // ----- 3. 拓扑排序源参数：按层级从根到叶 -----
	  // 先找出所有根节点（parentId 为空或不存在于 srcMap 中）
	  const srcItems = [...src];
	  const srcParentMap = new Map(); // parentId -> 子节点数组
	  srcItems.forEach(item => {
	    const pid = item.parentId || 'null';
	    if (!srcParentMap.has(pid)) srcParentMap.set(pid, []);
	    srcParentMap.get(pid).push(item);
	  });
	
	  const sortedSrc = [];
	  const queue = srcParentMap.get('null') || []; // 根节点
	  while (queue.length) {
	    const current = queue.shift();
	    sortedSrc.push(current);
	    const children = srcParentMap.get(current.id) || [];
	    queue.push(...children);
	  }
	
	  // ----- 4. 合并处理，记录源id到目标id的映射 -----
	  const result = [];
	  const idMapping = new Map(); // 源id -> 新id（目标id或新生成id）
	
	  for (const srcItem of sortedSrc) {
	    const path = getSrcPath(srcItem); // 路径已在第1步计算过，这里直接复用（但需确保函数已定义）
	    // 更高效：直接从 srcPathMap 获取路径（但我们有路径计算函数）
	    // 这里为清晰，重新计算（可优化）
	    const srcPath = getSrcPath(srcItem);
	    const targetItem = tgtPathMap.get(srcPath);
	
	    let newId, newValue;
	
	    if (targetItem) {
	      // 已存在：保留目标的 id 和 value
	      newId = targetItem.id;
	      newValue = targetItem.value;
	    } else {
	      // 新增：生成新 id，value 使用源的值（示例值）
	      newId = uuidv4();
	      newValue = srcItem.value; // 保持源中的示例值
	    }
	
	    // 记录映射
	    idMapping.set(srcItem.id, newId);
	
	    // 构造新参数对象：深拷贝源，然后覆盖关键字段
	    const newItem = JSON.parse(JSON.stringify(srcItem));
	    newItem.id = newId;
	    newItem.value = newValue;
	    // 转换 parentId：如果源 parentId 存在，则从映射中获取对应的新 id；否则为 null
	    if (srcItem.parentId && idMapping.has(srcItem.parentId)) {
	      newItem.parentId = idMapping.get(srcItem.parentId);
	    } else {
	      newItem.parentId = null;
	    }
	
	    result.push(newItem);
	  }
	
	  return result;
	},
    setApiData(apiData) {
      this.apiData = apiData
      this.one_step_obj.keyword = apiData.id
      this.one_step_obj.api_all = JSON.parse(JSON.stringify(apiData))
      this.one_step_obj.api_method = apiData.method
      this.one_step_obj.api_service = apiData.service
      this.loadApiVisible = true
      this.getRequestHosts()
	  this.$refs.collapse.setActiveNames('3')
    },
    setPythonFuncData(data) {
      this.pythonFuncData = { ...data }
      this.one_step_obj.keyword = data.id
      this.one_step_obj.func_params = [...data.params]
      this.choosePythonFuncVisible = false
    },
    setSeleniumData(data) {
      this.one_step_obj.keyword = data.id
      this.seleniumFuncData = { ...data }
      this.one_step_obj.func_params = [...data.params]
      this.chooseSeleniumVisible = false
    },
	setPlaywrightData(data) {
	  this.one_step_obj.keyword = data.id
	  this.seleniumFuncData = { ...data }
	  this.one_step_obj.func_params = [...data.params]
	  this.chooseSeleniumVisible = false
	},
	handleNodeClick(nodeData, node, component) {
		// 如果点击的是父节点，则展开/收起子节点
		if (nodeData.children && nodeData.children.length > 0) {
			// 切换节点的展开状态
			node.expanded = !node.expanded
			// 立即重置选中值为空，确保父节点不会被选中
			this.$nextTick(() => {
				this.one_step_obj.keyword = ''
			})
			// 阻止事件冒泡和默认行为
			return false
		}
	},
	findItemById(nodes, id) {
	  for (const node of nodes) {
	    if (node.id === id) {
	      return node
	    }
	    if (node.children && node.children.length > 0) {
	      const found = this.findItemById(node.children, id)
	      if (found) return found
	    }
	  }
	  return null
	},
	handleKeywordChange(value) {
		// 根据选中的id查找对应的完整对象
		const selectedItem = this.findItemById(this.web_keys, value)
		if(this.case_info.type ===2){
			this.setSeleniumData(selectedItem)
		}else{
			this.setAppiumData(selectedItem)
		}
	},
    setAppiumData(data) {
      this.one_step_obj.keyword = data.id
      this.appiumFuncData = { ...data }
      this.one_step_obj.func_params = [...data.params]
      this.chooseAppiumVisible = false
    },
    setStepData(data) {
      const case_id = data.case_info[0].id
      this.getStep(case_id, data.id, 0, true, false, true)
      this.chooseStepVisible = false
    },
    setComStepData(data) {
      const case_id = data.case_info[0].id
      this.getStep(case_id, data.id, 0, false, true, true)
      this.chooseComStepVisible = false
      // this.single_step_tab = 'step_params_info'
    },
	async setManyComStepData(datas) {
		this.editStepDetailVisible = false
		const response = await this.$api.addManyStep({case_id: this.$route.query.id, is_com_step: true, data: datas})
		if (response.status === 200) {
		  this.getCase()
		  ElMessage({ message: '添加成功', type: 'success' })
		}
	},
	async setManyStepData(datas) {
		this.editStepDetailVisible = false
		const response = await this.$api.addManyStep({case_id: this.$route.query.id, is_com_step: false, data: datas})
		if (response.status === 200) {
		  this.getCase()
		  ElMessage({ message: '添加成功', type: 'success' })
		}
	},
    actionChange(value) {
      if (value === undefined) {
        return
        // this.one_step_obj.type = this.one_step_obj.tmp_type
      } else {
        this.one_step_obj.tmp_type = value
      }
      if (this.one_step_obj.type === this.StepType.Request) {
        this.chooseApiVisible = true
        this.one_step_obj.step_active_tab = 'body'
        this.one_step_obj.com_step_type = this.StepType.Request
        // this.getApi(step_key, index)
      }else if (this.one_step_obj.type === this.StepType.PlayWright) {
        this.one_step_obj.com_step_type = this.StepType.PlayWright
        this.one_step_obj.step_active_tab = 'playwright_func'
      }else if (this.one_step_obj.type === this.StepType.Appium) {
        this.one_step_obj.com_step_type = this.StepType.Appium
        this.one_step_obj.step_active_tab = 'appium_func'
      } else if (this.one_step_obj.type === this.StepType.Step) {
        this.chooseStepVisible = true
      } else if (this.one_step_obj.type === this.StepType.ComStep) {
        this.chooseComStepVisible = true
      } else if (this.one_step_obj.type === this.StepType.SQL) {
        this.one_step_obj.step_active_tab = 'sql'
        this.one_step_obj.com_step_type = this.StepType.SQL
		this.one_step_obj.keyword = 'SelectFetchone'
      }
    },
    run() {
      this.runTimesVisible = true
    },
    async caseRun() {
      if (this.case_info.type === 2 && this.case_info.web_engine_type === 1 && this.caseRunForm.web_executor_id === '') {
        ElMessage({ message: '请选择Web执行机', type: 'error' })
        return
      } else if (this.case_info.type === 3 && this.caseRunForm.app_executor_id === '') {
        ElMessage({ message: '请选择手机设备', type: 'error' })
        return
      } else if (!this.caseRunForm.env_id) {
        ElMessage({ message: '请选择执行环境', type: 'error' })
        return
      }
      this.tmp_logs = []
      this.runTimesVisible = false
      this.caseRunForm.case_id = this.$route.query.id
      const response = await this.$api.caseRun(this.caseRunForm)
      if (response.status === 200) {
        if ('result' in response.data){
             ElMessage({
          message: '【' + this.case_info.name + '】' + '用例执行中，请稍后在测试历史中查看执行结果',
          type: 'success'
        })
        }else{
            this.tmp_logs = [...response.data.results]
             ElMessage({
              message: '【' + this.case_info.name + '】' + '用例执行完成',
              type: 'success'
            })
        }

      }
    },
    async locustRun() {
      if (!this.locustRunForm.env_id) {
        ElMessage({ message: '请选择执行环境', type: 'error' })
        return
      }
      this.locustRunVisible = false
      this.locustRunForm.case_id = this.$route.query.id
      this.locustRunForm.project_id = this.projectInfo.id
      const response = await this.$api.locustRun(this.locustRunForm)
      if (response.status === 200) {
        ElMessage({
          message: '【' + this.case_info.name + '】' + '用例压测中，请在报告管理中查看性能测试报告',
          type: 'success'
        })
        this.$router.push({ path: '/report/locust/detail', query: { id: response.data.result.report_id } })
      }
    },
    downloadWindows() {
      window.open(this.$api.base_url + '/test/download/windows', '_blank')
      ElMessage({ message: '下载中', type: 'success' })
    },
    downloadLinux() {
      window.open(this.$api.base_url + '/test/download/linux', '_blank')
      ElMessage({ message: '下载中', type: 'success' })
    },
    downloadMacos() {
      window.open(this.$api.base_url + '/test/download/macos', '_blank')
      ElMessage({ message: '下载中', type: 'success' })
    },
    isRunChange(id, is_run, is_all=false, ids=[]) {
      this.UpdateIsRun({ id: id, is_run: is_run, is_all: is_all, ids:ids })
    },
    look_logs() {
      this.lookLogVisible = true
      this.caseActive = ''
      this.stepActive = ''
      this.logActive = ''
      this.getCaseLogs()
    },
    async getCaseLogs() {
      const query_data = { case: this.$route.query.id }
      if (this.run_result != 0) {
        query_data.result = this.run_result
      }
      const response = await this.$api.getCaseLogs(Object.assign(query_data, this.page_size_params))
      if (response.status === 200) {
        this.case_logs = { ...response.data }
      }
    },
    async getDbs() {
      const response = await this.$api.getDbs({ project: this.projectInfo.id })
      if (response.status === 200) {
        this.db_list = { ...response.data }
      }
    },
    editStepTwo(row) {
      this.stepView = false
      this.api_test_result = ''
      this.loading = false
      this.editStepDetailVisible = true
      this.single_step_tab = 'step_base_info'
      this.one_step_obj.step_index = row.step_index
      this.getStep(this.$route.query.id, row.id, row.case_step_id)
    },
    viewStep(row) {
      this.stepView = true
      this.loading = false
      this.api_test_result = ''
      this.editStepDetailVisible = true
      this.one_step_obj.step_index = row.step_index
      this.getStep(this.$route.query.id, row.id, row.case_step_id)
    },
    editStep({ row, column }) {
      this.stepView = false
      this.api_test_result = ''
      this.loading = false
      this.single_step_tab = 'step_base_info'
      this.editStepDetailVisible = true
      this.getStep(this.$route.query.id, row.id, row.case_step_id)
    },
    copyStep(row) {
      this.stepView = false
      this.api_test_result = ''
      this.loading = false
      this.editStepDetailVisible = true
      this.copyStepApi(row.id, row.case_step_id)
    },
    confimDeleteStep(row) {
      ElMessageBox.confirm('删除该步骤后数据无法恢复,确定删除该步骤?', '删除步骤', {
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      })
        .then(() => {
          console.log(row.children, 'data')
          if (row.children.length !== 0) {
            ElMessage({
              type: 'error',
              message: '父节点不能删除'
            })
          } else {
            this.deleteStep(row)
          }
        })
        .catch(() => {})
    },
    async deleteStep(row) {
      const case_id = this.$route.query.id
      const response = await this.$api.deleteStep(`${case_id}_${row.id}_${row.step_index}`)
      if (response.status === 200) {
        ElMessage({
          type: 'success',
          message: '删除成功'
        })
        this.getCase()
      }
    },
    remove_vxe_table_info() {
      this.one_step_obj.api_json_tree = JSON.parse(JSON.stringify(this.one_step_obj.api_json))
      console.log(this.one_step_obj.api_json_tree, 'tree')
      this.one_step_obj.api_response_tree = JSON.parse(JSON.stringify(this.one_step_obj.api_response))
      for (let index = this.one_step_obj.api_json.length - 1; index >= 0; index--) {
        delete this.one_step_obj.api_json[index].children
        delete this.one_step_obj.api_json[index]._X_ROW_CHILD
        delete this.one_step_obj.api_json[index]._X_ROW_KEY
        if (this.one_step_obj.api_json_tree[index].parentId !== null) {
          this.one_step_obj.api_json_tree.splice(index, 1)
        }
      }
      this.delExtraInfo(this.one_step_obj.api_json_tree)
      for (let index = this.one_step_obj.api_data.length - 1; index >= 0; index--) {
        delete this.one_step_obj.api_data[index].children
        delete this.one_step_obj.api_data[index]._X_ROW_CHILD
        delete this.one_step_obj.api_data[index]._X_ROW_KEY
      }
      for (const index in this.one_step_obj.api_headers) {
        delete this.one_step_obj.api_headers[index].children
        delete this.one_step_obj.api_headers[index]._X_ROW_CHILD
        delete this.one_step_obj.api_headers[index]._X_ROW_KEY
      }
      for (const index in this.one_step_obj.api_params) {
        delete this.one_step_obj.api_params[index].children
        delete this.one_step_obj.api_params[index]._X_ROW_CHILD
        delete this.one_step_obj.api_params[index]._X_ROW_KEY
      }
      for (let index = this.one_step_obj.api_response.length - 1; index >= 0; index--) {
        delete this.one_step_obj.api_response[index].children
        delete this.one_step_obj.api_response[index]._X_ROW_CHILD
        delete this.one_step_obj.api_response[index]._X_ROW_KEY
        if (this.one_step_obj.api_response_tree[index].parentId !== null) {
          this.one_step_obj.api_response_tree.splice(index, 1)
        }
      }
      this.delExtraInfo(this.one_step_obj.api_response_tree)
    },
    delExtraInfo(data) {
      for (let index = 0; index < data.length; index++) {
        delete data[index]._X_ROW_CHILD
        delete data[index]._X_ROW_KEY
        if (data[index].hasOwnProperty('children')) {
          this.delExtraInfo(data[index].children)
        } else {
          delete data[index].children
        }
      }
    },
    saveStep(is_close) {
      if (!this.one_step_obj.keyword && this.one_step_obj.type != this.StepType.PythonScript) {
        ElMessage({ message: '请选择步骤关键字', type: 'error' })
        return
      }
      if (
        this.one_step_obj.type === this.StepType.Control &&
        this.one_step_obj.keyword === '1' &&
        common.hasEmptyValues(this.one_step_obj.run_params, ['andOr', 'method', 'exp_value', 'act_value'])
      ) {
        ElMessage({ message: '请完善IF条件控制表格数据，所有字段必填', type: 'error' })
        return
      }
      if (this.one_step_obj.type === this.StepType.Control && this.one_step_obj.keyword === '1' && this.one_step_obj.run_params.length === 0) {
        ElMessage({ message: 'IF条件控制器不能为空', type: 'error' })
        return
      }
      if (this.one_step_obj.type === this.StepType.Control && this.one_step_obj.keyword === '2' && this.one_step_obj.loop.length === 0) {
        ElMessage({ message: 'FOR循环控制器不能为空', type: 'error' })
        return
      }
      if (this.one_step_obj.type === this.StepType.Control && this.one_step_obj.keyword === '3' && this.one_step_obj.until.length === 0) {
        ElMessage({ message: 'While条件控制器不能为空', type: 'error' })
        return
      }
      if (
        this.one_step_obj.type === this.StepType.Control &&
        this.one_step_obj.keyword === '2' &&
        common.hasEmptyValues(this.one_step_obj.loop, ['loop_times'])
      ) {
        ElMessage({ message: '请完善FOR循环控制表格数据，所有字段必填', type: 'error' })
        return
      }
      if (
        this.one_step_obj.type === this.StepType.Control &&
        this.one_step_obj.keyword === '3' &&
        common.hasEmptyValues(this.one_step_obj.until, ['andOr', 'method', 'exp_value', 'act_value', 'max_loop_times'])
      ) {
        ElMessage({ message: '请完善While条件控制表格数据，所有字段必填', type: 'error' })
        return
      }
      if (common.hasEmptyValues(this.one_step_obj.step_params, ['name', 'value'])) {
        ElMessage({ message: '请完善步骤变量下中的参数名称和参数值', type: 'error' })
        return
      } else if (common.hasEmptyValues(this.one_step_obj.check_params, ['method', 'act_value', 'exp_value'])) {
        ElMessage({ message: '请完善断言规则中的表格数据，所有字段必填', type: 'error' })
        return
      }
      if (this.one_step_obj.type === this.StepType.ComStep) {
        ElMessageBox.confirm('保存公共步骤后，其他关联该步骤的用例也会影响，确定保存该步骤?', '保存测试步骤', {
          confirmButtonText: '确定',
          cancelButtonText: '取消'
        })
          .then(() => {
            this.remove_vxe_table_info()
            if (this.one_step_obj.id === 0) {
              this.CreateStep(is_close)
            } else {
              this.UpdateStep(this.one_step_obj.id, this.one_step_obj, is_close)
            }
          })
          .catch(() => {})
      } else {
        this.remove_vxe_table_info()
        if (this.one_step_obj.id === 0) {
          this.CreateStep(is_close)
        } else {
          this.UpdateStep(this.one_step_obj.id, this.one_step_obj, is_close)
        }
      }
    },
    saveStepClose(is_close) {
      this.saveStep(is_close)
    },
    async CreateStep(is_close) {
	  console.log(is_close, 'is_close')
      this.$refs['stepRef'].validate(async (valid, fields) => {
        if (valid) {
          this.one_step_obj.project = this.projectInfo.id
          this.one_step_obj.case_id = this.$route.query.id
          const response = await this.$api.createStep(this.one_step_obj)
          if (response.status === 201) {
            this.getCase()
            ElMessage({ message: '保存成功', type: 'success' })
			if(is_close){
				this.editStepDetailVisible = false
				this.loading = true
			}else{
				this.getStep(this.$route.query.id, response.data.result.step_id, response.data.result.case_step_id)
			}
          }
        }
      })
    },
    async UpdateStep(id, params, is_close) {
      this.$refs['stepRef'].validate(async (valid, fields) => {
        if (valid) {
          const response = await this.$api.updateStep(
            `${this.$route.query.id}_${id}_${params.case_step_id}`,
            params
          )
          if (response.status === 200) {
            this.getCase()
            ElMessage({ message: '保存成功', type: 'success' })
			if(is_close){
				this.editStepDetailVisible = false
				this.loading = true
			}else{
				this.getStep(this.$route.query.id, response.data.result.id, response.data.result.case_step_id)
			}
          }
        }
      })
    },
    async UpdateIsRun(params) {
      const response = await this.$api.update_is_run(params)

    },
    async change_step_index(params) {
      const response = await this.$api.change_step_index(params)
      if (response.status === 200) {
        this.getCase()
        ElMessage({ message: '保存成功', type: 'success' })
      }
    },
    async getCase() {
      const response = await this.$api.getCase(this.$route.query.id)
      if (response.status === 200) {
        this.case_info = { ...response.data.result }
		if(this.case_info.type ===2){
			this.getPlaywrightKeyGroup()
		}else if(this.case_info.type ===3){
			this.getAppExecutors()
			this.getAppiumKeyGroup()
		}
        const $table = this.$refs.tableRef
        this.$nextTick(() => {
          if (this.$refs.tableRef) {
            this.$refs.tableRef.setAllTreeExpand(true)
          }
        })
      }
    },
    async getCheck() {
      const response = await this.$api.getCheck()
      if (response.status === 200) {
        this.method = response.data.results
      }
    },
    async getStep(case_id, step_id, case_step_id, set_id_zero = false, is_com_step = false, is_update_step_index = false) {
      const response = await this.$api.getStep(`${case_id}_${step_id}_${case_step_id}`)
      if (response.status === 200) {
        this.one_step_obj = { ...response.data.result }
        this.title = this.one_step_obj.desc
        if (this.one_step_obj.type === this.StepType.Appium) {
          this.getAppiumKey(this.one_step_obj.keyword)
        }else if(this.one_step_obj.type === this.StepType.Playwright){
		     this.getPlaywrightKey(this.one_step_obj.keyword)
		}
        if (set_id_zero) {
          this.one_step_obj.id = 0
          this.one_step_obj.type = this.one_step_obj.com_step_type
        } else if (is_com_step) {
          const step_type = this.one_step_obj.com_step_type
          this.one_step_obj.type = this.StepType.ComStep
		  this.one_step_obj.case_step_id = 0
          this.one_step_obj.com_step_type = step_type
        }
        if (this.one_step_obj.api_service) {
          this.getRequestHosts()
          this.$refs.collapse.setActiveNames('3')
        }
        if (is_update_step_index){
          this.one_step_obj.step_index = this.case_info.step.length - 1
        }
      }
    },
    async copyStepApi(id, case_step_id) {
      const response = await this.$api.getStep(`${this.$route.query.id}_${id}_${case_step_id}`)
      if (response.status === 200) {
        this.one_step_obj = { ...response.data.result }
        this.one_step_obj.id = 0
        this.one_step_obj.desc = this.one_step_obj.desc + '-副本'
      }
    },
    async getfuncs() {
      const response = await this.$api.getFuncs({ project: this.projectInfo.id })
      if (response.status === 200) {
        this.func_list = [...response.data.results]
      }
    },
    async updateCaseParams() {
      if (common.hasEmptyValues(this.case_info.params, ['name', 'value'])) {
        ElMessage({ message: '请完善表格数据中参数名称和参数值', type: 'error' })
        return
      }
      const response = await this.$api.updateCase(this.$route.query.id, this.case_info)
      if (response.status === 200) {
        this.editParamsVisible = false
        ElMessage({ message: '保存成功', type: 'success' })
      }
    },
    handleBeforeClose(done) {
      if (common.hasEmptyValues(this.case_info.data.value, this.case_info.data.name)) {
        ElMessage({ message: '请完善表格数据，所有字段都必填', type: 'error' })
      } else if (this.hasDuplicateValues(this.case_info.data.value, '_name_')) {
        ElMessage({ message: '数据用例名称存在重复值', type: 'error' })
      } else {
        this.saveCaseData()
        done()
      }
    },
    hasDuplicateValues(array, key) {
      if (!Array.isArray(array)) return false

      const values = array.map((item) => item[key])
      const uniqueValues = new Set(values)

      return uniqueValues.size !== values.length
    },
    async saveCaseData() {
      const response = await this.$api.updateCase(this.$route.query.id, this.case_info)
      if (response.status === 200) {
        this.editDataVisible = false
      }
    },
    async updateStepParams() {
      if (common.hasEmptyValues(this.stepRowInfo.step_params, ['name', 'value'])) {
        ElMessage({ message: '请完善表格数据中的参数名称和参数值', type: 'error' })
        return
      }
      this.stepRowInfo.case = this.$route.query.id
      this.stepRowInfo.step = this.stepRowInfo.id
      const response = await this.$api.updateCaseSteps(this.stepRowInfo.case_step_id, this.stepRowInfo)
      if (response.status === 200) {
        this.editStepParamsVisible = false
        ElMessage({ message: '保存成功', type: 'success' })
      }
    },
    async getServices() {
      const response = await this.$api.getServices({ project: this.projectInfo.id })
      if (response.status === 200) {
        this.service_list = response.data.results
      }
    },
    async getRequestHosts() {
      const response = await this.$api.getRequestHost({ service: this.one_step_obj.api_service, plant: this.one_step_obj.plant })
      if (response.status === 200) {
        this.envServiceList = { ...response.data.result }
        if (this.envServiceList.env_hosts.length === 0) {
		  const msg = this.envServiceList.is_server_host ? '该步骤所属服务还没添加服务域名配置,': '该步骤所属产品还没添加产品域名配置,'
		  const name = this.envServiceList.is_server_host ? 'service': 'plant'
		  ElMessageBox.confirm(
		       msg + '未添加会导致接口请求无法匹配域名',
		      '提示',
		      {
		        confirmButtonText: '去添加',
		        cancelButtonText: '取消',
		        type: 'warning',
		      }
		    )
		      .then(() => {
		        this.$router.push({'name': name})
		      })
		      .catch(() => {
		        ElMessage({
		          type: 'info',
		          message: '已取消',
		        })
		      })
        }
      }
    },
	async getPlaywrightKey(name) {
	  const response = await this.$api.getPlaywrightKey(
	    Object.assign({ name: name, find_equal: 'true' }, this.page_size_params)
	  )
	  if (response.status === 200) {
	    this.seleniumFuncData = { ...response.data.results[0] }
	  }
	},
	async getSeleniumKeyGroup() {
	  try {
	    const response = await this.$api.getSeleniumKey({group: true})
	    if (response.status === 200) {
	      // 处理数据，为父节点添加isParent属性
	      this.web_keys = response.data.results
	    }
	  } catch (error) {
	    console.error('获取WEB自动化关键字操作失败:', error)
	  }
	},
	async getPlaywrightKeyGroup() {
	  try {
	    const response = await this.$api.getPlaywrightKey({group: true})
	    if (response.status === 200) {
	      // 处理数据，为父节点添加isParent属性
	      this.web_keys = response.data.results
	    }
	  } catch (error) {
	    console.error('获取WEB自动化关键字操作失败:', error)
	  }
	},
	async getAppiumKeyGroup() {
	  try {
	    const response = await this.$api.getAppiumKey({group: true})
	    if (response.status === 200) {
	      // 处理数据，为父节点添加isParent属性
	      this.web_keys = response.data.results
	    }
	  } catch (error) {
	    console.error('获取WEB自动化关键字操作失败:', error)
	  }
	},
    async getAppiumKey(name) {
      const response = await this.$api.getAppiumKey(Object.assign({ name: name, find_equal: 'true' }, this.page_size_params))
      if (response.status === 200) {
        this.appiumFuncData = { ...response.data.results[0] }
      }
    },
    async getPython(id) {
      const response = await this.$api.getPython(id)
      if (response.status === 200) {
        this.pythonFuncData = { ...response.data.result }
      }
    },
    async getPars() {
      const response = await this.$api.getPars({ project: this.projectInfo.id })
      if (response.status === 200) {
        this.bind_env_params = [...response.data.results]
      }
    },
    async getWebExecutors() {
      //project: this.projectInfo.id, s
      const response = await this.$api.getWebExecutors({ type: '1,2', status: 1 })
      if (response.status === 200) {
        this.web_executor_list = [...response.data.results]
      }
    },
	
	ensureString(value) {
	  // 注意：typeof null === 'object'，所以要排除 null
	  if (typeof value === 'object' ) {
	    return JSON.stringify(value, null, 4);
	  }
	  return value;
	},
	
	getEnvByHost(envHosts, host) {
	    if (!Array.isArray(envHosts) || !host) return null;
	    const found = envHosts.find(item => item.host === host);
	    return found ? found.env : null;
	},

	step_control_run(step_index){
	     this.caseRunForm.step_index = step_index
	     if (!this.one_step_obj.api_host){
		   ElMessage({message: "请选择环境", type: 'warning'})
		 }else if(!this.one_step_obj.api_uri){
			 ElMessage({message: "请输入请求地址", type: 'warning'})
		 }else if(this.case_info.data && 'value' in this.case_info.data && this.case_info.data['value'].length > 0){
		     this.StepControlCaseData = true
		 }else{
            this.step_run(false)
		 }
	},
	
	async step_run(close){
	       if (close){
	           this.StepControlCaseData = false
	       }
		   // this.remove_vxe_table_info()
		   this.one_step_obj.env_id = this.getEnvByHost(this.envServiceList.env_hosts, this.one_step_obj.api_host)
		   this.caseRunForm.env_id = this.one_step_obj.env_id
		   this.caseRunForm.case_id = this.$route.query.id
		   const response = await this.$api.StepRun(this.caseRunForm)
		   if(response.status === 200){
			 this.api_test_result = response.data.results
			 this.activeNames = '20'
			 // 尝试等待DOM更新，但即使出错也继续
              try {
                await this.$nextTick();
              } catch (e) {
                console.warn('DOM更新异常，继续执行滚动', e);
              }

              // 4. 定义滚动函数：检测元素是否存在且可见（高度>0），再滚动
              let retries = 0;
              const maxRetries = 30; // 最多尝试 30 次（每次 100ms，共 3 秒）
              const scrollToMarker = () => {
                const el = this.$refs.bottomMarker;
                // 额外检查：元素是否在 DOM 中且具有实际高度（避免刚创建但未布局）
                if (el && el.offsetParent !== null && el.offsetHeight > 0) {
                  el.scrollIntoView({ behavior: "smooth", block: "end" });
                  return; // 成功
                }
                retries++;
                if (retries < maxRetries) {
                  setTimeout(scrollToMarker, 100);
                } else {
                  // 超时降级：滚动对话框主体
                  const body = document.querySelector(".el-dialog__body");
                  if (body) body.scrollTop = body.scrollHeight;
                }
              };

              // 5. 初始延迟 100ms（让动画开始），然后进入轮询
              setTimeout(scrollToMarker, 100);

			 ElMessage({message: "执行完成", type: 'success'})
		 }
	},
    async getAppExecutors() {
      //project: this.projectInfo.id, s
      const response = await this.$api.getAppExecutors({ status: 1 })
      if (response.status === 200) {
        this.app_executor_list = [...response.data.results]
      }
    },
    async getHeaders() {
      const response = await this.$api.getHeaders({ project: this.projectInfo.id, create_by: this.user_id })
      if (response.status === 200) {
        this.header_list = { ...response.data }
      }
    },
    async getCookies() {
      const response = await this.$api.getCookies({ project: this.projectInfo.id, create_by: this.user_id })
      if (response.status === 200) {
        this.cookie_list = { ...response.data }
      }
    },
    async getPlants() {
      const response = await this.$api.getPlants({ project: this.projectInfo.id })
      if (response.status === 200) {
        this.plant_list = { ...response.data }
      }
    },
    async check_permission(){
      const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission['/resource/scriptCase']}
      const response = await this.$api.check_permission(params)
      if (response.status === 200){
        this.permission = { ...response.data.result }
        if (this.permission.has_edit_permission || this.permission.has_add_permission) {
          this.caseView = false
         } else {
          this.caseView = true
        }
      }
    }
  },
  created() {
    this.check_permission()
    this.one_step_obj_tmp = { ...this.one_step_obj }
    this.getDbs()
    this.getServices()
    this.getfuncs()
    this.getCase()
    this.getCheck()
    this.getPars()
    this.getGlobalPars()
    this.getPlants()
    this.getEnvs()
    // this.getHeaders()
    // this.getCookies()
  }
}
</script>

<style scoped>
.case-edit-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px 15px 15px 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: calc(100vh - 75px);
  height: calc(100vh - 75px);
  max-height: calc(100vh - 75px);
}

/* 步骤日志弹窗样式 */
:deep(.step-log-popover) {
  max-height: 400px;
  overflow-y: auto;
  border-radius: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15) !important;
  border: 1px solid #e2e8f0;
  max-width: 50vw;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* 确保弹窗内容容器也有圆角 */
:deep(.step-log-popover .el-popper) {
  border-radius: 16px !important;
}

:deep(.step-log-popover .el-popover) {
  border-radius: 16px !important;
}

:deep(.step-log-popover .el-popover__reference) {
  border-radius: 16px !important;
}

:deep(.step-log-popover .el-popover--plain) {
  border-radius: 16px !important;
}

:deep(.step-log-popover .el-popover.el-popover--plain) {
  border-radius: 16px !important;
}

:deep(.step-log-popover .el-popper__arrow) {
  display: none !important;
}

/* 强制设置所有弹窗相关元素的圆角 */
:deep(.step-log-popover) * {
  border-radius: 16px !important;
}

.step-log-popover-content {
  padding: 16px;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  box-sizing: border-box;
}

.step-log-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 8px;
  word-break: break-all;
  overflow-wrap: break-word;
  max-width: 100%;
}

.step-log-list {
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  margin-bottom: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.log-item:last-child {
  margin-bottom: 0;
}

.log-collapse-item {
  max-width: 100%;
  overflow: hidden;
}

.log-collapse-item .el-collapse-item__header {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.log-collapse-item .el-collapse-item__header .el-text {
  max-width: calc(100% - 40px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
  vertical-align: middle;
}

.log-content {
  margin-top: 8px;
  padding: 8px;
  background: white;
  border-radius: 4px;
  font-size: 12px;
  color: #64748b;
  border: 1px solid #e2e8f0;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 优雅阴影效果 */
.elegant-shadow {
  /* box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.08); */
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.elegant-shadow:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.12);
}

/* 内容卡片 */
.content-card {
  flex: 1;
  background: white;
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.step_item_card {
  flex: 1;
  background: white;
  margin: 0px 10px 20px 10px;
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

/* 整体样式 - 基于您的样式优化 */
/* 整体样式 */
.content-header {
  padding: 0px 10px 10px 10px;
  /* border-bottom: 1px solid #f1f5f9; */
  background: white;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.fixed-content-header {
  padding: 0px 10px 10px 10px;
  /* border-bottom: 1px solid #f1f5f9; */
  background: white;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 第一行：标题 + 按钮 */
.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: nowrap;
  min-height: 40px;
}

.case-title-area {
  flex: 1;
  min-width: 0;
}

/* 用例名称 - 保留左侧蓝色竖杠 */
.content-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
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
  height: 20px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 2px;
}

/* 操作按钮区域 */
.action-buttons {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  flex-wrap: nowrap;
  align-items: center;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 13px;
  height: 36px;
  transition: all 0.2s ease;
  border: none;
  white-space: nowrap;
}

.action-btn .el-icon {
  font-size: 14px;
}

/* 按钮颜色 - 保留您原来的颜色方案 */
.back-btn {
  background: white;
  border: 1px solid #e2e8f0 !important;
  color: #64748b;
}

.back-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1 !important;
  transform: translateY(-1px);
}

.history-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.history-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.run-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.run-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.load-btn {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.load-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.add-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
}

.add-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.control-dropdown {
  display: inline-flex;
}

.control-btn {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
}

.control-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.control-menu {
  border-radius: 8px;
  padding: 6px 0;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.control-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 13px;
  transition: all 0.2s ease;
}

.control-item:hover {
  background-color: #f8fafc;
}

.control-item .el-icon {
  color: #6366f1;
}

.data-btn {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  color: white;
}

.data-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
}

.params-btn {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  color: white;
}

.params-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
}

/* 第二行：用例信息 */
.header-bottom {
  display: flex;
  align-items: center;
  gap: 8px;
}

.case-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 13px;
  color: #64748b;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-label {
  color: #94a3b8;
  font-weight: 500;
}

.meta-value {
  color: #475569;
  font-weight: 600;
}

.meta-time {
  color: #cbd5e1;
  font-size: 12px;
}

.meta-divider {
  width: 1px;
  height: 14px;
  background: #e2e8f0;
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.stat-label {
  color: #64748b;
}

.stat-value {
  color: #1a1a1a;
  font-weight: 600;
}

.success-rate {
  color: #10b981 !important;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .action-buttons {
    overflow-x: auto;
    padding-bottom: 4px;
    max-width: 800px;
  }
  
  .action-buttons::-webkit-scrollbar {
    height: 4px;
  }
  
  .action-buttons::-webkit-scrollbar-track {
    background: #f5f5f5;
    border-radius: 2px;
  }
  
  .action-buttons::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 2px;
  }
}

@media (max-width: 992px) {
  .content-header {
    padding: 10px 16px;
    gap: 10px;
  }
  
  .header-top {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .case-title-area {
    width: 100%;
  }
  
  .content-title {
    font-size: 16px;
    padding-left: 14px;
  }
  
  .content-title::before {
    height: 18px;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: flex-start;
  }
  
  .case-meta {
    justify-content: flex-start;
    width: 100%;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .action-btn {
    padding: 6px 12px;
    font-size: 12px;
    height: 32px;
  }
  
  .case-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .meta-divider {
    display: none;
  }
  
  .meta-item, .stats-item {
    width: 100%;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid #f1f5f9;
  }
  
  .stats-item {
    background: none;
    border: none;
  }
}

/* 表格区域 */
.table-wrapper {
  flex: 1;
  padding: 0 0px;
  min-height: 0;
  max-height: calc(100vh - 260px);
  overflow-y: auto;
  overflow-x: auto;
}

/* 合并列样式 */
.user-time-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 4px;
  line-height: 1.2;
}
.user-time-cell .user-info,
.user-time-cell .time-info {
  white-space: nowrap;
}

.user-info,
.time-info {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
}

.icon-user {
  width: 12px;
  height: 12px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-time-small {
  width: 12px;
  height: 12px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.user-name {
  font-size: 13px;
  color: #334155;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.time-text {
  font-size: 12px;
  color: #64748b;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}


.elegant-vxe-table {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #f1f5f9;
}

.elegant-vxe-table :deep(.vxe-table--header-wrapper) {
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

.elegant-vxe-table :deep(.vxe-table--header-wrapper .vxe-header--row) {
  background: transparent;
}

.elegant-vxe-table :deep(.vxe-table--header-wrapper th) {
  background: transparent;
  border-bottom: 1px solid #e2e8f0;
  font-weight: 600;
  color: #1a1a1a;
  padding: 10px 0;
}

.elegant-vxe-table :deep(.vxe-table--body-wrapper .vxe-body--row) {
  transition: all 0.3s ease;
}

.elegant-vxe-table :deep(.vxe-table--body-wrapper .vxe-body--row:nth-child(even)) {
  background: #f8fafc;
}

.elegant-vxe-table :deep(.vxe-table--body-wrapper .vxe-body--row:hover) {
  background: #f1f8ff;
  transform: translateX(4px);
}

.elegant-vxe-table :deep(.vxe-table--body-wrapper .vxe-body--column) {
  border-bottom: 1px solid #f1f5f9;
  padding: 16px 0;
  transition: all 0.3s ease;
}

.step-link {
  font-weight: 500;
  color: #3b82f6;
  transition: all 0.3s ease;
}

.step-link:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

.step-type-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.type-tag {
  padding: 4px 10px;
  margin-right: 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  border: none;
}

.method-tag {
  color: #3b82f6;
}

.keyword-tag {
  background: rgba(46, 204, 113, 0.1) !important;
  color: #2ecc71 !important;
}

.control-tag {
  background: rgba(26, 188, 156, 0.1) !important;
  color: #1abc9c !important;
}

.run-switch {
  --el-switch-on-color: #10b981;
  --el-switch-off-color: #94a3b8;
}

.table-action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.table-action-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  border: none;
}

.table-action-btn:hover {
  transform: translateY(-2px) scale(1.1);
}

.table-action-btn.view-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.table-action-btn.edit-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.table-action-btn.copy-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.table-action-btn.delete-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.table-action-btn .el-icon {
  color: white;
  font-size: 14px;
}

/* 对话框样式 */
.elegant-dialog :deep(.el-dialog) {
  border-radius: 20px !important;
  overflow: hidden !important;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4) !important;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  backdrop-filter: blur(10px) !important;
}

.elegant-dialog :deep(.el-dialog__header) {
  padding: 24px 24px 0 !important;
  margin: 0 !important;
}

.dialog-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.dialog-title {
  font-size: 20px !important;
  font-weight: 700 !important;
  color: #1a1a1a !important;
  margin: 0 !important;
}

.elegant-dialog :deep(.el-dialog__headerbtn) {
  top: 24px !important;
  right: 24px !important;
  width: 32px !important;
  height: 32px !important;
  border-radius: 50% !important;
  background: rgba(0, 0, 0, 0.05) !important;
  transition: all 0.3s ease !important;
}

.elegant-dialog :deep(.el-dialog__headerbtn:hover) {
  background: rgba(99, 102, 241, 0.1) !important;
  transform: rotate(90deg) !important;
}

.elegant-dialog :deep(.el-dialog__body) {
  padding: 24px !important;
  background: rgba(255, 255, 255, 0.7) !important;
}

.dialog-form-item {
  margin-bottom: 20px;
}

.dialog-form-item :deep(.el-form-item__label) {
  font-weight: 600;
  color: #334155;
  font-size: 14px;
}

.dialog-input :deep(.el-input__inner) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: white;
  padding: 0 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.dialog-input :deep(.el-input__inner:hover) {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-input :deep(.el-input__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.api-uri-input :deep(.el-input-group__prepend) {
  padding: 0;
  border: none;
  background: transparent;
}

.elegant-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px 24px;
  border-top: 1px solid #f1f5f9;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.dialog-cancel-btn,
.dialog-confirm-btn {
  position: relative;
  padding: 10px 24px !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: 15px !important;
  transition: all 0.3s ease !important;
  overflow: hidden;
}

.dialog-cancel-btn {
  border: 1px solid #e2e8f0 !important;
  background: white !important;
  color: #64748b !important;
}

.dialog-cancel-btn:hover {
  background: #f8fafc !important;
  border-color: #cbd5e1 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.15) !important;
}

.dialog-confirm-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
  border: none !important;
  color: white !important;
}

.dialog-confirm-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
}

/* 按钮文字容器 */
.button-text {
  position: relative;
  display: inline-block;
  padding-bottom: 3px; /* 为下划线留出空间 */
}

/* 下划线效果 */
.button-text::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: currentColor;
  transform: scaleX(0);
  transform-origin: bottom right;
  transition: transform 0.3s ease;
}

/* 取消按钮下划线颜色 */
.dialog-cancel-btn .button-text::after {
  background: #3b82f6; /* 蓝色下划线 */
}

/* 确认按钮下划线颜色 */
.dialog-confirm-btn .button-text::after {
  background: white; /* 白色下划线 */
}

/* 鼠标悬停时显示下划线 */
.dialog-cancel-btn:hover .button-text::after,
.dialog-confirm-btn:hover .button-text::after {
  transform: scaleX(1);
  transform-origin: bottom left;
}

/* 性能压测特定样式 */
.sync-options {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 20px;
}

.download-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
  padding: 30px 0;
}

.download-btn {
  width: 200px !important;
  padding: 12px 20px !important;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
}

.download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
}

.elegant-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.elegant-tabs :deep(.el-tabs__nav-wrap) {
  overflow: visible !important;
}

.elegant-tabs :deep(.el-tabs__nav-scroll) {
  overflow: visible !important;
}

.elegant-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #e2e8f0;
}

.elegant-tabs :deep(.el-tabs__active-bar) {
  display: none;
}

.elegant-tabs :deep(.el-tabs__item) {
  position: relative;
  font-size: 16px;
  font-weight: 600;
  color: #64748b;
  padding: 0;
  margin: 0 16px;
  height: 48px;
  line-height: 48px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.elegant-tabs :deep(.el-tabs__item::after) {
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

.elegant-tabs :deep(.el-tabs__item:hover) {
  color: #6366f1;
}

.elegant-tabs :deep(.el-tabs__item:hover::after) {
  width: 100%;
  background: rgba(99, 102, 241, 0.5);
}

.elegant-tabs :deep(.el-tabs__item.is-active) {
  color: #6366f1;
  font-weight: 600;
}

.elegant-tabs :deep(.el-tabs__item.is-active::after) {
  width: 100%;
  background: #6366f1;
}

/* 抽屉样式 */
.elegant-drawer :deep(.el-drawer) {
  border-radius: 20px 20px 0 0;
  overflow: hidden;
}

.elegant-drawer :deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  background: white;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.drawer-title-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.drawer-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
}

.result-radio-group {
  float: right;
  display: flex;
  gap: 8px;
}

.result-radio-group :deep(.el-radio-button) {
  border-radius: 8px;
  overflow: hidden;
}

.result-radio-group :deep(.el-radio-button__inner) {
  border: none;
  padding: 8px 16px;
  transition: all 0.3s ease;
}

.result-radio-group :deep(.el-radio-button.is-active .el-radio-button__inner) {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-color: transparent;
  box-shadow: none;
}

.drawer-content {
  padding: 0px;
  
}

.case-log-header {
  padding: 4px 0;
}

.elegant-collapse :deep(.el-collapse-item__header) {
  font-weight: 600;
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 8px;
}

.elegant-collapse :deep(.el-collapse-item__content) {
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.step-collapse {
  margin-bottom: 12px;
}

/* 测试设置样式 */
	
.config-item {
  display: flex;
  align-items: center;
  justify-content: space-between; /* 让左右两端对齐 */
  border: 1.5px solid #dcdfe6;      /* 边框 */
  border-radius: 4px;             /* 圆角 */
  padding: 12px 16px;             /* 内边距 */
  margin-bottom: 10px;
  background-color: #fff;         /* 背景色，可选 */
  transition: border-color 0.2s;  /* 可选悬停效果 */
}



.label {
  margin-right: 16px;
  font-weight: 500;
  font-size: 14px;          /* 增大字体，可根据实际需要调整 */
  white-space: nowrap;
  color: #606266;           /* 更深的灰色，接近黑色 */
}

.control-group {
  display: flex;
  align-items: center;
  gap: 12px; /* 如果添加了额外按钮，按钮与输入框之间的间距 */
}

/* 可根据需要调整输入框宽度 */
.control-group .el-input-number {
  width: 150px;
}

/* 步骤详情抽屉 */
.step-detail-card {
  border: none;
  border-radius: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.step-detail-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  background: white;
}

.step-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.step-collapse-panel {
  flex: 1;
  /* overflow-y: scroll; */
  padding: 24px 0px;
  background: white;
}

.step-collapse-panel :deep(.el-collapse-item__header) {
  font-weight: 600;
  background: white;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 8px;
  border: 1px solid #e2e8f0;
}

.step-collapse-panel :deep(.el-collapse-item__content) {
  padding: 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  border-top: none;
  margin-bottom: 16px;
}

.section-divider {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 12px 0 12px 0;
  padding: 0 8px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #334155;
}

.section-icon {
  color: #94a3b8;
  width: 16px;
  height: 16px;
}

.step-base-info {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  margin-bottom: 20px;
}

.action-icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  transition: all 0.3s ease;
}

.action-icon-btn:hover {
  transform: translateY(-2px) scale(1.1);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.info-icon {
  margin-left: 4px;
  cursor: help;
}

.body-type-radio {
  margin-bottom: 20px;
}

.body-type-radio :deep(.el-radio) {
  margin-right: 20px;
}

.drawer-footer {
  padding: 20px 24px 0px 24px;
  border-top: 1px solid #f1f5f9;
  background: white;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .case-edit-container {
    padding: 16px;
  }

  .content-card .content-header,
  .content-card .table-wrapper {
    padding: 16px 20px;
  }

  .stats-info {
    min-width: 250px;
  }

  .stat-item {
    min-width: 80px;
    padding: 8px 12px;
  }
}

@media screen and (max-width: 768px) {
  .case-edit-container {
    padding: 12px;
  }

  .content-card .content-header {
    padding: 16px;
  }

  .title-with-stats {
    flex-direction: column;
    gap: 16px;
  }

  .stats-info {
    width: 100%;
    justify-content: space-between;
  }

  .action-buttons {
    justify-content: center;
  }

  .action-btn {
    width: 100%;
    justify-content: center;
  }

  .table-wrapper {
    padding: 0 16px;
    overflow-x: auto;
  }

  .elegant-vxe-table {
    min-width: 1000px;
  }

  .step-base-info .el-col {
    width: 100%;
    margin-bottom: 16px;
  }

  .step-base-info .el-row {
    margin: 0;
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

.content-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-dialog) {
  animation: slideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  position: relative;
  padding-left: 16px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 2px;
}

/* 修复后的样式 - 添加到现有style中 */

/* 1. 确保el-collapse-item__header固定高度，但保留原有布局 */
.step-collapse-panel :deep(.el-collapse-item__header) {
  /* 固定高度属性 */
  height: 60px !important; /* 稍微调高一点，给内边距留空间 */
  min-height: 60px !important;
  max-height: 60px !important;
  
  /* 恢复原有的内边距和布局 */
  padding: 0 20px !important; /* 保持原有的左右内边距 */
  margin: 0 !important;
  box-sizing: border-box !important;
  
  /* 使用flex确保内容垂直居中 */
  display: flex !important;
  align-items: center !important;
  flex-wrap: nowrap !important;
  
  /* 防止内容溢出 */
  overflow: hidden !important;
  
  /* 固定字体，防止缩放 */
  font-size: 15px !important;
  font-weight: 600 !important;
  color: #303133 !important;
  
  /* 恢复原有的背景色和边框 */
  background: #f8fafc !important;
  border-radius: 8px !important;
  border: 1px solid #e2e8f0 !important;
  margin-bottom: 8px !important;
  
  /* 保持原有的过渡效果 */
  transition: all 0.3s ease !important;
}

/* 2. 修复section-divider的布局 */
.step-collapse-panel :deep(.el-collapse-item__header .section-divider) {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  width: 100% !important;
  height: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
  
  /* 确保内部元素不会撑开高度 */
  line-height: 1 !important;
}

/* 3. 修复section-title的样式，确保左边框伪元素正确显示 */
.step-collapse-panel :deep(.section-title) {
  margin: 0 !important;
  padding: 0 !important;
  padding-left: 20px !important; /* 为左边蓝色竖条留出空间 */
  font-size: 16px !important;
  font-weight: 600 !important;
  color: #334155 !important;
  line-height: 1.5 !important;
  
  /* 确保垂直居中 */
  display: flex !important;
  align-items: center !important;
  position: relative !important;
  height: 100% !important;
}

/* 4. 修复section-title::before左边蓝色竖条的位置和大小 */
.step-collapse-panel :deep(.section-title::before) {
  content: '';
  position: absolute;
  left: 0; /* 紧贴父元素左侧 */
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px; /* 固定高度，不随内容变化 */
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 2px;
  margin: 0 !important;
}

/* 5. 确保el-radio-group正确对齐 */
.step-collapse-panel :deep(.el-radio-group) {
  display: inline-flex !important;
  align-items: center !important;
  height: 32px !important;
  margin-left: auto !important;
  
  /* 确保不影响父元素高度 */
  max-height: 32px !important;
}

/* 6. 修复el-radio-button样式 */
.step-collapse-panel :deep(.el-radio-button) {
  height: 32px !important;
}

.step-collapse-panel :deep(.el-radio-button__inner) {
  line-height: 30px !important;
  height: 32px !important;
  padding: 0 12px !important;
  font-size: 14px !important;
}

/* 7. 确保el-icon在标题中正确显示 */
.step-collapse-panel :deep(.el-collapse-item__header .el-icon) {
  margin-right: 8px !important;
  font-size: 16px !important;
  vertical-align: middle !important;
  line-height: 1 !important;
}

/* 8. 添加hover效果，保持原有的交互体验 */
.step-collapse-panel :deep(.el-collapse-item__header:hover) {
  background: #f1f8ff !important;
  border-color: #cbd5e1 !important;
  transform: translateX(2px) !important;
}

/* 9. 修复el-collapse-item__wrap的样式，确保内容区域正常 */
.step-collapse-panel :deep(.el-collapse-item__wrap) {
  border: none !important;
  background: transparent !important;
}

/* 10. 修复内容区域的样式 */
.step-collapse-panel :deep(.el-collapse-item__content) {
  padding: 20px !important;
  background: white !important;
  border-radius: 8px !important;
  border: 1px solid #e2e8f0 !important;
  border-top: none !important;
  margin-bottom: 16px !important;
}

/* 11. 修复激活状态下的样式 */
.step-collapse-panel :deep(.el-collapse-item.is-active .el-collapse-item__header) {
  background: #f1f8ff !important;
  border-bottom-left-radius: 0 !important;
  border-bottom-right-radius: 0 !important;
  border-bottom: none !important;
}

/* 12. 确保在不同屏幕下保持一致的字体渲染 */
.step-collapse-panel {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

/* 13. 针对高DPI屏幕的微调 */
@media (-webkit-min-device-pixel-ratio: 1.25), (min-resolution: 120dpi) {
  .step-collapse-panel :deep(.el-collapse-item__header) {
    font-size: 15.5px !important;
  }
  
  .step-collapse-panel :deep(.section-title) {
    font-size: 16.5px !important;
  }
}

/* 修复测试历史抽屉中的el-collapse-item标题高度 */
.elegant-drawer {
  /* 确保抽屉容器字体一致性 */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 1. 修复最外层的时间线折叠面板 */
.elegant-drawer .elegant-collapse :deep(.el-collapse-item__header) {
  height: 60px !important;
  min-height: 60px !important;
  max-height: 60px !important;
  line-height: 60px !important;
  padding: 0 16px !important;
  margin-bottom: 8px !important;
  
  /* 使用flex布局确保垂直居中 */
  display: flex !important;
  align-items: center !important;
  box-sizing: border-box !important;
  
  /* 保持原有样式 */
  background: #f8fafc !important;
  border-radius: 8px !important;
  border: 1px solid #e2e8f0 !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  color: #303133 !important;
}

/* 2. 修复第二层步骤折叠面板 */
.elegant-drawer .step-collapse :deep(.el-collapse-item__header) {
  height: 60px !important;
  min-height: 60px !important;
  max-height: 60px !important;
  line-height: 60px !important;
  padding: 0 10px !important;
  
  /* 使用flex布局 */
  display: flex !important;
  align-items: center !important;
  box-sizing: border-box !important;
  
  /* 保持原有样式 */
  background: white !important;
  border: 1px solid #e4e7ed !important;
  border-radius: 6px !important;
  margin-bottom: 4px !important;
  font-size: 14px !important;
}

/* 3. 修复最内层日志折叠面板 */
.elegant-drawer .el-collapse :deep(.el-collapse-item__header) {
  height: 60px !important;
  min-height: 60px !important;
  max-height: 60px !important;
  line-height: 60px !important;
  padding: 0 16px !important;
  
  /* 使用flex布局 */
  display: flex !important;
  align-items: center !important;
  box-sizing: border-box !important;
  
  /* 保持原有样式 */
  background: #f9fafb !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 4px !important;
  margin-bottom: 2px !important;
  font-size: 13px !important;
}

/* 4. 修复折叠面板内容区域的文本样式 */
.elegant-drawer .el-text {
  line-height: 1.5 !important;
  display: inline-flex !important;
  align-items: center !important;
  font-size: 14px !important;
}

/* 5. 修复折叠面板激活状态的样式 */
.elegant-drawer :deep(.el-collapse-item.is-active .el-collapse-item__header) {
  border-bottom-left-radius: 0 !important;
  border-bottom-right-radius: 0 !important;
  border-bottom: none !important;
}

/* 6. 修复折叠面板内容区域的样式 */
.elegant-drawer :deep(.el-collapse-item__content) {
  padding: 16px !important;
  background: white !important;
  border: 1px solid #e2e8f0 !important;
  border-top: none !important;
  border-radius: 0 0 8px 8px !important;
  margin-bottom: 8px !important;
}

/* 7. 确保内部元素正确显示 */
.elegant-drawer :deep(.el-image) {
  max-width: 100% !important;
}

/* 8. 针对不同DPI屏幕的调整 */
@media (-webkit-min-device-pixel-ratio: 1.25), (min-resolution: 120dpi) {
  .elegant-drawer .elegant-collapse :deep(.el-collapse-item__header) {
    font-size: 14.5px !important;
  }
  
  .elegant-drawer .step-collapse :deep(.el-collapse-item__header) {
    font-size: 14.5px !important;
  }
  
  .elegant-drawer .el-collapse :deep(.el-collapse-item__header) {
    font-size: 13.5px !important;
  }
}
</style>