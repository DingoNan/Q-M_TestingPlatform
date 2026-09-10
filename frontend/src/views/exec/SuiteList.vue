<template>
	<!-- 关联脚本用例弹窗 -->
	<el-drawer v-model="chooseCaseVisible" :with-header="false" direction="ttb" show-close   append-to-body fullscreen="true" destroy-on-close :size="'calc(100vh - 30px)'">
	  <CaseList :parentPermission="permission" :isCanChoose="true" v-model:chooseCaseVisible="chooseCaseVisible"  :existCaseIds="SuiteSave.auto_cases" @setCaseData="setCaseData" @setManyCaseData="setManyCaseData"></CaseList>
	</el-drawer>
	
	<!-- 关联功能用例弹窗 -->
	<el-drawer v-model="chooseFuncCaseVisible" :with-header="false" direction="ttb" show-close append-to-body fullscreen="true" destroy-on-close :size="'calc(100vh - 30px)'">
	  <FunCaseList :parentPermission="permission" :isCanChoose="true" v-model:chooseFuncCaseVisible="chooseFuncCaseVisible" :existCaseIds="SuiteSave.func_cases" @setFuncCaseData="setFuncCaseData" @setFuncManyCaseData="setFuncManyCaseData"></FunCaseList>
	</el-drawer>
	
	<!-- 执行测试套件对话框 -->
	<el-dialog v-model="runTimesVisible" title="执行测试套件" width="600" class="elegant-dialog">
	    <el-form :model="runSuiteForm" label-width="120px" class="run-dialog-form" :rules="runRules" ref='runRef' label-position='top'>
			<el-form-item label="执行环境" prop="env_id">
				<el-select v-model="runSuiteForm.env_id" class="select" placeholder="请选择执行环境" popper-class='select-dropdown-rounded' size='large'>
					<el-option
					  v-for="item in env_list.results"
					  :key="item.id"
					  :label="item.name"
					  :value="item.id"
					/>
				</el-select>
			</el-form-item>
			<el-form-item label="测试报告名称" prop="title">
				<el-input v-model='runSuiteForm.title' placeholder="请输入测试报告名称" class='input' size='large'></el-input>
			</el-form-item>
			<!-- <el-form-item label="是否并发执行" prop="is_async">
				<el-select v-model="runSuiteForm.is_async" class="select" popper-class='select-dropdown-rounded' size='large'>
					<el-option label='是' :value='true'/>
					<el-option  label='否' :value='false' />
				</el-select>
			</el-form-item>
			<el-form-item label="并发数" prop="count" v-if='runSuiteForm.is_async'>
				<el-input-number v-model="runSuiteForm.count" :min="1" :max="4" style="width: 100%;" size='large' class='input'/>
			</el-form-item> -->
	    </el-form>
	    <template #footer>
			<span class="dialog-footer">
				<el-button @click="runTimesVisible = false" class="dialog-cancel-btn">取消</el-button>
				<el-button type="primary" @click="caseRun" class="dialog-confirm-btn">执行</el-button>
			</span>
	    </template>
	</el-dialog>
	
	<!-- 测试套件编辑对话框 -->
	<el-dialog
		v-model="editDialogVisible" 
		:show-close="true" 
		:title="title" 
		fullscreen
		class="elegant-dialog"
	>
		<el-form :model="SuiteSave" :disabled="tagView" :rules="suiteRules" ref='suiteRef' class="dialog-form">
			<el-row :gutter="20">
				<el-col :span='8'>
					<el-form-item  prop='name'>
						<label class="dialog-label">
							<i class="icon-suite-name"></i>
							测试套件名称
						</label>
						<el-input v-model="SuiteSave.name" autocomplete="off" placeholder="请输入测试套件名称" class="input" size='large' show-word-limit maxlength="50"/>
					</el-form-item>
				</el-col>
				<el-col :span='8'>
					<el-form-item  prop='plant_type'>
						<label class="dialog-label">
							<i class="icon-suite-type"></i>
							测试套件类型
						</label>
						<el-select v-model="SuiteSave.plant_type" placeholder="请选择测试套件类型"  @change='change' class="select" size='large' popper-class='select-dropdown-rounded' :disabled='SuiteSave.id'>
							<el-option label='按功能用例收集' :value="1" />
							<el-option label='按脚本用例收集' :value="2" />
						</el-select>
					</el-form-item>
				</el-col>
				<el-col :span='8'>
					<el-form-item  prop='plant_model'>
						<label class="dialog-label">
							<i class="icon-suite-type"></i>
							用例收集模式
						</label>
						<el-select v-model="SuiteSave.plant_model" placeholder="请选择测试套件模式"  @change='change' class="select" size='large' popper-class='select-dropdown-rounded' :disabled='SuiteSave.id'>
							<el-option label='静态模式' :value="1" />
							<el-option label='动态模式' :value="2" />
						</el-select>
					</el-form-item>
				</el-col>
				<el-col :span='8' v-if='SuiteSave.plant_type === 2'>
					<el-form-item  prop='auto_type'>
						<label class="dialog-label">
							<i class="icon-suite-type"></i>
							脚本用例类型
						</label>
						<el-select v-model="SuiteSave.auto_type" placeholder="请选择脚本用例类型"  @change='change' class="select" size='large' popper-class='select-dropdown-rounded' :disabled='SuiteSave.id'>
							<el-option v-for="(value, label) in caseType" :label='label' :value="value" />
						</el-select>
					</el-form-item>
				</el-col>
				<el-col :span='8' v-if='SuiteSave.plant_type === 1 || (SuiteSave.plant_type ===2 && SuiteSave.auto_type === 2)'>
					<el-form-item  prop="web_executor" >
						<label class="dialog-label">
							<i class="icon-executor"></i>
							浏览器集群
						</label>
						<el-select v-model="SuiteSave.web_executor" placeholder="请选择浏览器集群" clearable class="select" size='large' popper-class='select-dropdown-rounded'>
							<el-option v-for="obj in web_executor_list" :label='obj.name' :value="obj.id" />
						</el-select>
					</el-form-item>
				</el-col>
				<el-col :span='8' v-if='SuiteSave.plant_type === 1 || (SuiteSave.plant_type ===2 && SuiteSave.auto_type === 3)'>
					<el-form-item  prop="app_executor" >
						<label class="dialog-label">
							<i class="icon-executor"></i>
							手机设备
						</label>
						<el-select v-model="SuiteSave.app_executor" placeholder="请选择手机设备" clearable class="select" size='large' popper-class='select-dropdown-rounded'>
							<el-option v-for="obj in android_executor_list" :label='obj.device_name' :value="obj.id" />
						</el-select>
					</el-form-item>
				</el-col>
				<el-col :span='8'>
					<el-form-item  prop='rerun_times'>
						<label class="dialog-label">
							<i class="icon-retry"></i>
							失败重试次数
						</label>
						<el-input-number v-model="SuiteSave.rerun_times" :precision="0" :step="1" :min='0' :max="3" style='width: 100%;' class="input" size='large' />
					</el-form-item>
				</el-col>
				<el-col :span='8'>
					<el-form-item  prop='push_msg'>
						<label class="dialog-label">
							<i class="icon-push"></i>
							是否推送消息
						</label>
						<el-select v-model="SuiteSave.push_msg" placeholder="请选择"  class="select" size='large' popper-class='select-dropdown-rounded'>
							<el-option label='是' :value="true" />
							<el-option label='否' :value="false" />
						</el-select>
					</el-form-item>
				</el-col>
				<el-col :span='8' >
					<el-form-item  prop='start_end_time'>
						<label class="dialog-label">
							<i class="icon-executor"></i>
							测试套件起止时间
						</label>
						 <el-date-picker
							v-model="SuiteSave.start_end_time"
							type="datetimerange"
							size='large'
							class='date'
							style='width: 100%;'
							start-placeholder="开始时间"
							end-placeholder="结束时间"
							
						/>
					</el-form-item>
				</el-col>
				<el-col :span='24' >
					<el-form-item  prop='desc'>
						<label class="dialog-label">
							<i class="icon-push"></i>
							测试套件描述
						</label>
						 <el-input
						   v-model="SuiteSave.desc" 
						   autocomplete="off" 
						   placeholder="请输入测试套件描述"
						   maxlength="200"
						   show-word-limit
						   type="textarea"
						   size='large'
						   class="text"
						 />
					</el-form-item>
				</el-col>
				<el-col :span='24' v-if='SuiteSave.plant_model === 2 '>
					<el-form-item  >
						<label class="dialog-label">
							<i class="icon-condition"></i>
							动态模式按条件收集用例
						</label>
						<div class="suite-condition-wrapper">
							<SuiteCondition :keyData='SuiteSave.dynamic_conditions'></SuiteCondition>
						</div>
					</el-form-item>
				</el-col>
				<el-col :span='24' v-if='SuiteSave.plant_model === 1 && SuiteSave.plant_type === 1'>
					<el-form-item  >
						<label class="dialog-label">
							<i class="icon-condition"></i>
							静态模式选择功能用例集
						</label>
						<div class="suite-condition-wrapper">
							<el-button
							  v-if="permission.has_edit_permission || permission.has_add_permission" 
							  @click="()=>{this.chooseFuncCaseVisible=true}" 
							  type="primary" 
							  class="add-btn"
							  style='float: right; margin-bottom: 20px;'
							>
							  <el-icon><Plus /></el-icon>关联功能用例
							</el-button>
							<el-table
							  :data="SuiteSave.func_cases_detail" 
							  :max-height="'calc(100vh - 480px)'"
							  class="elegant-table"
							  :header-row-style="headerRowStyle"
							>
							  <el-table-column 
							    label="序号" 
							    width="70" 
							    type="index" 
							    align="center"
							    class-name="index-column"
							  >
							    <template #default="scope">
							      <div class="index-cell">
							        {{ scope.$index + 1 + (page_size_params.page - 1) * page_size_params.size }}
							      </div>
							    </template>
							  </el-table-column>
							  
							  <el-table-column 
							    label="用例名称" 
							    min-width="250" 
							    align="center"
								prop="name" 
							    class-name="case-info-column"
							  >
							   
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
							    label="用例标签" 
							    prop="tag_name" 
							    min-width="160" 
							    align="center"
							    class-name="tag-column"
							  >
							    <template #default="scope">
							      <div class="tags-container">
							        <el-tag 
							          v-for='obj in scope.row.tag_name' 
							          :key="obj.id"
							          size="small"
							          :type="getTagType(obj.name)"
							          effect="light"
									  style='margin-right: 5px'
							          class="case-tag"
							        >
							          {{ obj.name }}
							        </el-tag>
							        <span v-if="!scope.row.tag_name || scope.row.tag_name.length === 0" class="no-tag">-</span>
							      </div>
							    </template>
							  </el-table-column>
										
							<el-table-column
							  label="负责人" 
							  width="120" 
							  align="center"
							  prop="owner_name" 
							  class-name="case-info-column"
							>
							 
							</el-table-column>
							  
							  <!-- 合并列：创建信息 -->
							  <el-table-column 
							    label="创建信息" 
							    width="200" 
							    align="center"
								prop='create_time'
								sortable
							    class-name="creator-column"
							  >
							    <template #default="scope">
							      <div class="user-time-cell">
							        <div class="user-info">
							          <i class="icon-user"></i>
							          <span class="user-name">{{ scope.row.create_by_name || '-' }}</span>
							        </div>
							        <div class="time-info">
							          <i class="icon-time-small"></i>
							          <span class="time-text">{{ formatTime(scope.row.create_time) }}</span>
							        </div>
							      </div>
							    </template>
							  </el-table-column>
							  
							  <!-- 合并列：更新信息 -->
							  <el-table-column 
							    label="更新信息" 
							    width="200" 
							    align="center"
								prop='update_time'
								sortable
							    class-name="updater-column"
							  >
							    <template #default="scope">
							      <div class="user-time-cell">
							        <div class="user-info">
							          <i class="icon-user"></i>
							          <span class="user-name">{{ scope.row.update_by_name || '-' }}</span>
							        </div>
							        <div class="time-info">
							          <i class="icon-time-small"></i>
							          <span class="time-text">{{ formatTime(scope.row.update_time) }}</span>
							        </div>
							      </div>
							    </template>
							  </el-table-column>
							  
							  <el-table-column 
							    align="center" 
							    width="80" 
							    label="操作"
							    class-name="action-column"
							    fixed="right"
							  >
							    <template #default="scope">
							      <div class="action-buttons">
									<el-tooltip
									  content="移除用例" 
									  placement="top" 
									  effect="dark"
									>
									  <el-button 
									    type="danger" 
									    v-if="permission.has_edit_permission || permission.has_add_permission" 
									    @click.stop="removeFuncCase(scope)" 
									    class="action-btn delete-btn"
									    circle
									  >
									    <el-icon><Delete /></el-icon>
									  </el-button>
									</el-tooltip>
							      </div>
							    </template>
							  </el-table-column>
							</el-table>
						</div>
					</el-form-item>
				</el-col>
				<el-col :span='24' v-if='SuiteSave.plant_model === 1 && SuiteSave.plant_type === 2'>
					<el-form-item  >
						<label class="dialog-label">
							<i class="icon-condition"></i>
							静态模式选择脚本用例集
						</label>
						<div class="suite-condition-wrapper">
							<el-button
							  v-if="permission.has_edit_permission || permission.has_add_permission" 
							  @click="()=>{this.chooseCaseVisible=true}" 
							  type="primary" 
							  class="add-btn"
							  style='float: right; margin-bottom: 20px;'
							>
							  <el-icon><Plus /></el-icon>关联脚本用例
							</el-button>
							<el-table
							    :data="SuiteSave.auto_cases_detail" 
							    :max-height="'calc(100vh - 580px)'" 
							    class="elegant-table"
							    :header-row-style="headerRowStyle"
							    @row-dblclick="editStep"
							  >
							    <el-table-column 
							      label="序号" 
							      width="70" 
							      type="index" 
							      align="center"
							      class-name="index-column"
							    >
							      <template #default="scope">
							        <div class="index-cell">
							          {{ scope.$index + 1 }}
							        </div>
							      </template>
							    </el-table-column>
							    
							    <el-table-column 
							      label="用例信息" 
							      min-width="250" 
							      align="center"
							      class-name="case-info-column"
							    >
							      <template #default='scope'>
							        <div class="case-info-cell">
							          <div class="case-type-badge">
							            <el-tag 
							              size="small" 
							              :type="getTypeTagType(scope.row.type_name)"
							              effect="light"
							              class="type-tag"
							            >
							              <i :class="`type-icon-cell type-icon-${scope.row.type}`"></i>
							              {{ scope.row.type_name }}
							            </el-tag>
							          </div>
							          <el-link type="primary" @click='editStepTwo(scope.row)' class="case-link">
							            {{ scope.row.name }}
							          </el-link>
							        </div>
							      </template>
							    </el-table-column>
							    
							    <el-table-column 
							      label="最近测试结果" 
							      prop="recent_test_result_name" 
							      width="120" 
							      align="center"
							      class-name="result-column"
							    >
							      <template #default="scope">
							        <el-tag 
							          v-if='scope.row.recent_test_result_name ==="成功"' 
							          effect="dark" 
							          type="success"
							          class="result-tag"
							        >{{ scope.row.recent_test_result_name }}</el-tag>
							        <el-tag 
							          v-if='scope.row.recent_test_result_name ==="失败"' 
							          effect="dark" 
							          type="danger"
							          class="result-tag"
							        >{{ scope.row.recent_test_result_name }}</el-tag>
							        <el-tag 
							          v-if='scope.row.recent_test_result_name ==="错误"' 
							          effect="dark" 
							          type="danger"
							          class="result-tag"
							        >{{ scope.row.recent_test_result_name }}</el-tag>
							        <el-tag 
							          v-if='scope.row.recent_test_result_name ==="未执行"' 
							          effect="dark" 
							          type="info"
							          class="result-tag"
							        >{{ scope.row.recent_test_result_name }}</el-tag>
							      </template>
							    </el-table-column>
							    
							    <el-table-column 
							      label="用例标签" 
							      prop="tag_name" 
							      min-width="160" 
							      align="center"
							      class-name="tag-column"
							    >
							      <template #default="scope">
							        <div class="tags-container">
							          <el-tag 
							            v-for='obj in scope.row.tag_name' 
							            :key="obj.id"
							            size="small"
							            :type="getTagType(obj.name)"
							            effect="light"
										style='margin-right: 5px'
							            class="case-tag"
							          >
							            {{ obj.name }}
							          </el-tag>
							          <span v-if="!scope.row.tag_name || scope.row.tag_name.length === 0" class="no-tag">-</span>
							        </div>
							      </template>
							    </el-table-column>
							    
							    <!-- 合并列：创建信息 -->
							    <el-table-column 
							      label="创建信息" 
							      width="200" 
							      align="center"
								  sortable 
								  prop='create_time'
							      class-name="creator-column"
							    >
							      <template #default="scope">
							        <div class="user-time-cell">
							          <div class="user-info">
							            <i class="icon-user"></i>
							            <span class="user-name">{{ scope.row.create_by_name || '-' }}</span>
							          </div>
							          <div class="time-info">
							            <i class="icon-time-small"></i>
							            <span class="time-text">{{ formatTime(scope.row.create_time) }}</span>
							          </div>
							        </div>
							      </template>
							    </el-table-column>
							    
							    <!-- 合并列：更新信息 -->
							    <el-table-column 
							      label="更新信息" 
							      width="200" 
							      align="center"
								  sortable
								   prop='update_time'
							      class-name="updater-column"
							    >
							      <template #default="scope">
							        <div class="user-time-cell">
							          <div class="user-info">
							            <i class="icon-user"></i>
							            <span class="user-name">{{ scope.row.update_by_name || '-' }}</span>
							          </div>
							          <div class="time-info">
							            <i class="icon-time-small"></i>
							            <span class="time-text">{{ formatTime(scope.row.update_time) }}</span>
							          </div>
							        </div>
							      </template>
							    </el-table-column>
							    
							    <el-table-column 
							      align="center" 
							      width="80" 
							      label="操作"
							      class-name="action-column"
							      fixed="right"
							    >
							      <template #default="scope">
							        <div class="action-buttons">
							          
							          <el-tooltip 
							            content="移除用例" 
							            placement="top" 
							            effect="dark"
							          >
							            <el-button 
							              type="danger" 
							              v-if="permission.has_edit_permission || permission.has_add_permission" 
							              @click.stop="removeCase(scope)" 
							              class="action-btn delete-btn"
							              circle
							            >
							              <el-icon><Delete /></el-icon>
							            </el-button>
							          </el-tooltip>
							        </div>
							      </template>
							    </el-table-column>
							  </el-table>
						</div>
					</el-form-item>
				</el-col>
			</el-row>
		</el-form>
		<template #footer>
			<span class="dialog-footer" v-if='!tagView'>
				<el-button @click="editDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
				<el-button type="primary" @click="save" v-if='permission.has_add_permission || permission.has_eidt_permission' class="dialog-confirm-btn">保存</el-button>
			</span>
		</template>
	</el-dialog>
	
	<!-- 主页面 -->
	<div class="suite-management-container">
		<!-- 搜索筛选区域 -->
		<el-card class="filter-card elegant-shadow">
			<div class="filter-header">
				<div class="header-title-section">
					<i class="icon-search"></i>
					<h3 class="filter-title">测试套件筛选</h3>
					<el-tag size="small" type="info" effect="plain">精准查询</el-tag>
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
				<el-form :model="suiteSearch" class="filter-form inline-form">
					<el-row :gutter="24">
						<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="form-item-inline">
								<div class="label-with-icon">
									<i class="icon-suite-name"></i>
									<span class='label-text'>套件名称</span>
								</div>
								<el-input 
									v-model="suiteSearch.name" 
									placeholder="请输入测试套件名称" 
									clearable
									size='large'
									class="input"
								/>
							</el-form-item>
						</el-col>
						
						<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="form-item-inline">
								<div class="label-with-icon">
									<i class="icon-creator"></i>
									<span classs='label-text'>创建人</span>
								</div>
								<el-select 
									v-model="suiteSearch.create_by" 
									placeholder="请选择创建人" 
									clearable 
									filterable
									size='large'
									class="select"
									popper-class='select-dropdown-rounded'
								>
									<el-option 
										v-for="user_obj in user_list" 
										:label='user_obj.username' 
										:value="user_obj.id"
										:key="user_obj.id"
									/>
								</el-select>
							</el-form-item>
						</el-col>
						
						<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="form-item-inline">
								<div class="label-with-icon">
									<i class="icon-updater"></i>
									<span class='label-text'>更新人</span>
								</div>
								<el-select 
									v-model="suiteSearch.update_by" 
									placeholder="请选择更新人" 
									clearable 
									filterable
									size='large'
									popper-class='select-dropdown-rounded'
									class="select"
								>
									<el-option 
										v-for="user_obj in user_list" 
										:label='user_obj.username' 
										:value="user_obj.id"
										:key="user_obj.id"
									/>
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
						<h3 class="content-title">测试套件列表</h3>
						<div class="stats-info">
							<div class="stat-item">
								<span class="stat-label">总计</span>
								<span class="stat-value">{{ suite_list.count || 0 }}</span>
							</div>
							<div class="stat-item">
								<span class="stat-label">当前页</span>
								<span class="stat-value">{{ page_size_params.page }}</span>
							</div>
						</div>
					</div>
					<el-button 
						v-if='permission.has_add_permission' 
						@click="addSuite" 
						type="primary" 
						class="add-btn"
					>
						<el-icon><Plus /></el-icon>新增测试套件
					</el-button>
				</div>
			</div>

			<!-- 数据表格 -->
			<div class="table-wrapper">
				<el-table 
					:data="suite_list.results" 
					:max-height="'calc(100vh - 490px)'" 
					class="elegant-table"
					:header-row-style="headerRowStyle"
					@sort-change='handleSortChange'
				>
					<el-table-column 
						label="序号" 
						width="70" 
						type="index" 
						align="center"
						class-name="index-column"
					>
						<template #default="scope">
							<div class="index-cell">
								{{ scope.$index + 1 + (page_size_params.page - 1) * page_size_params.size }}
							</div>
						</template>
					</el-table-column>
					
					<el-table-column 
						label="测试套件名称" 
						prop="name" 
						min-width="150" 
						align="center"
						class-name="suite-name-column"
					>
						<template #default="scope">
							<div class="suite-name-cell">
								<el-tooltip 
									effect="dark" 
									:content="scope.row.name" 
									placement="top-start"
								>
									<div class="suite-name-text">
										{{ scope.row.name && scope.row.name.length > 20 ? scope.row.name.slice(0, 20) + '...' : scope.row.name }}
									</div>
								</el-tooltip>
							</div>
						</template>
					</el-table-column>
					
					<el-table-column 
						label="测试套件类型" 
						prop="plant_type" 
						width="150" 
						align="center"
						class-name="suite-type-column"
					>
						<template #default="scope">
							<el-tag 
								v-if="scope.row.plant_type === 1" 
								type="success" 
								effect="light"
								class="suite-type-tag"
							>
								按功能用例收集
							</el-tag>
							<el-tag 
								v-if="scope.row.plant_type === 2" 
								type="warning" 
								effect="light"
								class="suite-type-tag"
							>
								按脚本用例收集
							</el-tag>
							
						</template>
					</el-table-column>
					
					<el-table-column
						label="用例收集模式" 
						prop="plant_model" 
						width="120" 
						align="center"
						class-name="suite-type-column"
					>
						<template #default="scope">
							<el-tag 
								v-if="scope.row.plant_model === 1" 
								type="success" 
								effect="light"
								class="suite-type-tag"
							>
								静态模式
							</el-tag>
							<el-tag 
								v-if="scope.row.plant_model === 2" 
								type="warning" 
								effect="light"
								class="suite-type-tag"
							>
								动态模式
							</el-tag>
							
						</template>
					</el-table-column>
					
					<el-table-column 
						label="失败重试" 
						prop="rerun_times" 
						width="120" 
						align="center"
						class-name="retry-column"
					>
						<template #default="scope">
							<div class="retry-cell">
								<el-tag 
									size="small" 
									:type="scope.row.rerun_times > 0 ? 'warning' : 'info'" 
									effect="light"
								>
									{{ scope.row.rerun_times || 0 }} 次
								</el-tag>
							</div>
						</template>
					</el-table-column>
					
					<!-- 合并列：创建信息 -->
					<el-table-column 
					  label="套件起止时间" 
					  width="200" 
					  align="center"
					 
					  prop='start_end_time'
					  class-name="creator-column"
					>
					  <template #default="scope">
					    <div class="user-time-cell">
					      <div class="time-info">
					        <i class="icon-time-small"></i>
					        <span class="time-text">{{ formatTime(scope.row.start_end_time[0]) }}</span>
					      </div>
					      <div class="time-info">
					        <i class="icon-time-small"></i>
					        <span class="time-text">{{ formatTime(scope.row.start_end_time[1]) }}</span>
					      </div>
					    </div>
					  </template>
					</el-table-column>
					
					<!-- 合并列：创建信息 -->
					<el-table-column 
					  label="创建信息" 
					  width="200" 
					  align="center"
					  sortable="custom"   
					  prop='create_time'
					  class-name="creator-column"
					>
					  <template #default="scope">
					    <div class="user-time-cell">
					      <div class="user-info">
					        <i class="icon-user"></i>
					        <span class="user-name">{{ scope.row.create_by_name || '-' }}</span>
					      </div>
					      <div class="time-info">
					        <i class="icon-time-small"></i>
					        <span class="time-text">{{ formatTime(scope.row.create_time) }}</span>
					      </div>
					    </div>
					  </template>
					</el-table-column>
					
					<!-- 合并列：更新信息 -->
					<el-table-column 
					  label="更新信息" 
					  width="200" 
					  align="center"
					  sortable="custom"  
					   prop='update_time'
					  class-name="updater-column"
					>
					  <template #default="scope">
					    <div class="user-time-cell">
					      <div class="user-info">
					        <i class="icon-user"></i>
					        <span class="user-name">{{ scope.row.update_by_name || '-' }}</span>
					      </div>
					      <div class="time-info">
					        <i class="icon-time-small"></i>
					        <span class="time-text">{{ formatTime(scope.row.update_time) }}</span>
					      </div>
					    </div>
					  </template>
					</el-table-column>
					
					<el-table-column 
						align="center" 
						:width='calcMinWidth' 
						label="操作"
						class-name="action-column"
						fixed="right"
					>
						<template #default="scope">
							<div class="action-buttons">
								<el-tooltip 
									content="查看测试套件" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type="success" 
										v-if="permission.has_read_permission" 
										:icon="View" 
										@click="viewSuite(scope.row)" 
										class="action-btn view-btn"
										circle
									></el-button>
								</el-tooltip>
								
								<el-tooltip 
									content="执行测试套件" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type='primary' 
										v-if="permission.has_eidt_permission || permission.has_add_permission" 
										:icon="VideoPlay" 
										@click="run(scope.row)" 
										class="action-btn run-btn"
										circle
									></el-button>
								</el-tooltip>
								
								<el-tooltip 
									content="编辑测试套件" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type='warning' 
										v-if="permission.has_edit_permission" 
										:icon="EditPen" 
										@click="editSuite(scope.row)" 
										class="action-btn edit-btn"
										circle
									></el-button>
								</el-tooltip>
								
								<el-tooltip 
									content="删除测试套件" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type="danger" 
										v-if="permission.has_delete_permission" 
										@click="deleteSuite(scope.row.id)" 
										class="action-btn delete-btn"
										circle
									>
										<el-icon><Delete /></el-icon>
									</el-button>
								</el-tooltip>
							</div>
						</template>
					</el-table-column>
				</el-table>
			</div>

			<!-- 分页组件 -->
			<div class="pagination-wrapper">
				<el-pagination
					v-model:current-page="page_size_params.page"
					v-model:page-size="page_size_params.size"
					:page-sizes="[10, 20, 30, 50]"
					layout="total, sizes, prev, pager, next, jumper"
					:total="suite_list.count"
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
import {mapState, mapActions, mapGetters} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, VideoPlay, Plus, EditPen, Cpu, Refresh, Search } from '@element-plus/icons-vue'
import SuiteCondition from '../../components/SuiteCondition.vue'
import CaseList from '../case/CaseList.vue'
import FunCaseList from '../case/FunCaseList.vue'
import * as common from '../../utils/common.js'
export default{
	computed:{
		...mapState(['pathPermission', 'projectInfo', 'env_id', 'userInfo']),
		calcMinWidth() {
		  let visibleButtons = 0;
		  if (this.permission.has_read_permission) visibleButtons += 1;
		  if (this.permission.has_edit_permission && this.permission.has_add_permission){
			  visibleButtons += 2
		  }else if(this.permission.has_edit_permission){
			  visibleButtons += 2
		  }else{
			   visibleButtons += 1
		  }
		  if (this.permission.has_delete_permission) visibleButtons += 1;
		  return Math.max(10, visibleButtons * 70);
		}
	},
	components: {
		SuiteCondition,
		CaseList,
		FunCaseList
	},
	data() {
		return {
			tagView: false,
			permission: {},
			chooseCaseVisible: false,
			chooseFuncCaseVisible: false,
			suiteSearch:{
				name: '',
				project: '',
				type: '',
				create_by: '',
				update_by: '',
			},
			page_size_params: {
				page: 1,
				size: 10,
			},
			count: 1,
			runTimesVisible: false,
			title: '新增测试套件',
			isAdd: true,
			editDialogVisible: false,
			suite_list: [],
			plant_module_list: [],
			module_list: [],
			ViewVisible: false,
			caseType:{'API': 1,'WEB_UI': 2, 'APP_UI': 3},
			runSuiteForm: {
				env_id: '',
				// is_async: false,
				suite_id: '',
				// count: 1,
				title: ''
				
			},
			runRules: {
				env_id: [{
					required: true,
					message: '请选择执行环境',
					trigger: 'change',
				}],
				title: [{
					required: true,
					message: '报告名称不能为空',
					trigger: 'blur',
				}],
				is_async: [{
					required: true,
					message: '请选择是否并发执行',
					trigger: 'change',
				}],
				count: [{
					required: true,
					message: '请输入并发数',
					trigger: 'blur',
				}],
			},
			env_list: [],
			automationTypes: [
			  { label: '接口自动化', value: '1' },
			  { label: 'Web自动化', value: '2' },
			  { label: 'App自动化', value: '3' },
			  { label: '造数脚本', value: '4' },
			  { label: '性能测试', value: '5' },
			],
			web_executor_list: [],
			android_executor_list: [],
			ios_executor_list: [],
			SuiteSave:{
				project: '',
				name: '',
				desc: '',
				auto_cases_detail: [],
				func_cases_detail: [],
				auto_cases: [],
				func_cases: [],
				plant_type: 2,
				plant_model: 2,
				auto_type: 1,
				web_executor: '',
				app_executor: '',
				push_msg: false,
				is_multi: false,
				dynamic_conditions: [],
				start_end_time: [],
				rerun_times: 0,
			},
			sort_params: {
			  ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
			},
			suiteRules: {
				name: [{
					required: true,
					message: '测试套件名称不能为空',
					trigger: 'blur',
				}],
				desc: [{
					required: true,
					message: '测试套件描述不能为空',
					trigger: 'blur',
				}],
				type: [{
					required: true,
					message: '请选择测试套件类型',
					trigger: 'change',
				}],
				start_end_time: [{
					required: true,
					message: '请选择测试套件起止时间',
					trigger: 'change',
				}],
				push_msg: [{
					required: true,
					message: '请选择是否推送消息',
					trigger: 'change',
				}],
				// web_executor: [{
				// 	required: false,
				// 	message: '请选择浏览器集群',
				// 	trigger: 'change',
				// }],
				// app_executor: [{
				// 	required: false,
				// 	message: '请选择手机设备',
				// 	trigger: 'change',
				// }],
				rerun_times: [{
					required: true,
					message: '失败重试次数不能为空',
					trigger: 'blur',
				}],
			},
			role_names: [],
		}
	},
	setup() {
		return {
			VideoPlay,
			Delete,
			Plus,
			View,
			EditPen,
			Cpu,
			Refresh,
			Search
		}
	},
	methods:{
		...mapActions(['getRolePermission']),
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
		
		setManyCaseData(manyCaseData){
			let duplicateCount = 0
			let newCaseIds = []
			for (const data of manyCaseData) {
				if (this.SuiteSave.auto_cases.includes(data.id)) {
					duplicateCount++
					continue
				}
				if (this.SuiteSave.auto_type ===1 && data.type !=1) {
					continue
				}else if (this.SuiteSave.auto_type ===2 && data.type !=2) {
					continue
				}
				if (this.SuiteSave.auto_type ===3 && data.type !=3) {
					continue
				}
				this.SuiteSave.auto_cases.push(data.id)
				this.SuiteSave.auto_cases_detail.push(data)
				newCaseIds.push(data.id)
			}
			if (newCaseIds.length === 0) {
				this.$message.warning('所选用例已全部存在或类型不匹配，无需重复添加')
			} else if (duplicateCount > 0) {
				this.$message.success(`成功添加 ${newCaseIds.length} 个用例（跳过 ${duplicateCount} 个已存在的用例）`)
			} else {
				this.$message.success(`成功添加 ${newCaseIds.length} 个用例`)
			}
		},
		
		setCaseData(caseData) {
			if (this.SuiteSave.auto_cases.includes(caseData.id)) {
				// 使用 Element Plus 的提示组件
				this.$message.warning('该用例已关联')
				return // 直接返回，不执行后面的添加操作
			}
			if (this.SuiteSave.auto_type ===1 && caseData.type !=1) {
				  // 使用 Element Plus 的提示组件
				  this.$message.warning('只能选择API用例')
				  return // 直接返回，不执行后面的添加操作
			}else if (this.SuiteSave.auto_type ===2 && caseData.type !=2) {
				  // 使用 Element Plus 的提示组件
				  this.$message.warning('只能选择WEB用例')
				  return // 直接返回，不执行后面的添加操作
			}
			if (this.SuiteSave.auto_type ===3 && caseData.type !=3) {
				  // 使用 Element Plus 的提示组件
				  this.$message.warning('只能选择APP用例')
				  return // 直接返回，不执行后面的添加操作
			}
			 this.SuiteSave.auto_cases.push(caseData.id)
			 console.log(this.SuiteSave.auto_cases, 'push', caseData.id)
			 this.SuiteSave.auto_cases_detail.push(caseData)
		},
		
		setFuncManyCaseData(manyCaseData){
			let duplicateCount = 0
			let newCaseIds = []
			for (const data of manyCaseData) {
				if (this.SuiteSave.func_cases.includes(data.id)) {
					duplicateCount++
					continue
				}
				this.SuiteSave.func_cases.push(data.id)
				this.SuiteSave.func_cases_detail.push(data)
				newCaseIds.push(data.id)
			}
			if (newCaseIds.length === 0) {
				this.$message.warning('所选用例已全部存在，无需重复添加')
			} else if (duplicateCount > 0) {
				this.$message.success(`成功添加 ${newCaseIds.length} 个用例（跳过 ${duplicateCount} 个已存在的用例）`)
			} else {
				this.$message.success(`成功添加 ${newCaseIds.length} 个用例`)
			}
		},
		
		setFuncCaseData(caseData) {
			if (this.SuiteSave.func_cases.includes(caseData.id)) {
				// 使用 Element Plus 的提示组件
				this.$message.warning('该用例已关联')
				return // 直接返回，不执行后面的添加操作
			}
			 this.SuiteSave.func_cases.push(caseData.id)
			 this.SuiteSave.func_cases_detail.push(caseData)
		},
		
		run(obj){
			this.runTimesVisible = true
			this.runSuiteForm.suite_id = obj.id
			this.$refs.runRef.resetFields();
		},
		caseRun(){
			this.runSuite()
		},
		headerRowStyle() {
		    return {
		      'font-weight': '600',
		      'color': '#1a1a1a',
		      'background-color': '#f8fafc',
		      'border-bottom': '1px solid #e2e8f0',
		      'height': '56px'
		    }
		},
		
		handleSortChange(column) {
		  const { prop, order } = column
		  if (order === 'ascending') {
		    this.sort_params.ordering = prop
		  } else if (order === 'descending') {
		    this.sort_params.ordering = `-${prop}`
		  } else {
		    // 如果取消排序，则清空排序参数
		    this.sort_params.ordering = ''
		  }
		  // 重置到第一页并获取数据
		  this.page_size_params.page = 1
		  this.getSuites()
		},
	
		
		getTagType(tagName) {
		  if (!tagName) return ''
		  const colors = ['', 'success', 'info', 'warning', 'danger']
		  const hash = tagName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
		  return colors[hash % colors.length]
		},
		
		getTypeTagType(typeName) {
		  const typeMap = {
		    '1': '',
		    '2': 'success',
		    '3': 'warning',
		    '4': 'info',
		    '5': 'danger'
		  }
		  const typeKey = this.automationTypes.find(t => t.label === typeName)?.value || 'API'
		  return typeMap[typeKey] || ''
		},
		
		async runSuite(){
			this.$refs['runRef'].validate(async (valid, fields)=>{
				if(valid){
					this.runTimesVisible = false
					const response = await this.$api.runSuite(this.runSuiteForm)
					ElMessage({message: response.data.result.message, type: 'success'})
					this.$router.push({ path: '/report/listView', query: { id: response.data.result.report_id } })
				}
			})
		},
		handleCurrentChange(){
			this.getSuites()
		},
		handleSizeChange(){
			this.page_size_params.page = 1
			this.getSuites()
		},
		search(){
			this.page_size_params.page = 1
			this.getSuites()
		},
		reset(){
			for(let key in this.suiteSearch){
				this.suiteSearch[key] = ''
			}
			this.page_size_params.page = 1
			this.getSuites()
		},
		editSuite(row_data){
			this.isAdd = false
			this.tagView = false
			this.title = '编辑测试套件'
			this.getSuite(row_data.id)
			this.editDialogVisible = true
			this.$refs.suiteRef.resetFields();
		},
		viewSuite(row_data){
			this.isAdd = false
			this.title = '查看测试套件'
			this.tagView = true
			this.getSuite(row_data.id)
			this.editDialogVisible = true
		},
		addSuite(){
			this.title = '新增测试套件'
			this.tagView = false
			this.editDialogVisible = true
			this.isAdd = true
			this.SuiteSave.id = 0
			this.$refs.suiteRef.resetFields();
		},
		change(){
			if (this.SuiteSave.type ===2){
				this.getWebExecutors()
			}else if(this.SuiteSave.type === 3){
				this.getAppExecutors(1)
			}else if(this.SuiteSave.type === 4){
				this.getAppExecutors(2)
			}
		},
		
		removeCase(scope) {
			ElMessageBox.confirm(
			  '确定移除该用例?',
			  '确认移除',
			  {
			    confirmButtonText: '确认移除',
			    cancelButtonText: '取消',
			    type: 'warning',
			    confirmButtonClass: 'el-button--danger',
			    customClass: 'confirm-dialog'
			  }
			).then(async() => {
			  const index = scope.$index
			  const id = scope.row.id
			  
			  // 根据索引从 case_detail 中移除
			  if (Array.isArray(this.SuiteSave.auto_cases_detail)) {
			    this.SuiteSave.auto_cases_detail.splice(index, 1)
			  }
			  
			  // 根据 id 从 case 中移除
			  if (Array.isArray(this.SuiteSave.auto_cases)) {
			    // const idIndex = this.SuiteSave.auto_cases.indexOf(id);
				this.SuiteSave.auto_cases.splice(index, 1);
				console.log(this.SuiteSave.auto_cases, 'auto_cases')
				// if (idIndex !== -1) {
				//   this.SuiteSave.auto_cases.splice(idIndex, 1);
				//   console.log(this.SuiteSave.auto_cases, 'auto_cases')
				// }
			  }
			}).catch(() => {})
		    
		},
		
		removeFuncCase(scope) {
			ElMessageBox.confirm(
			  '确定移除该用例?',
			  '确认移除',
			  {
			    confirmButtonText: '确认移除',
			    cancelButtonText: '取消',
			    type: 'warning',
			    confirmButtonClass: 'el-button--danger',
			    customClass: 'confirm-dialog'
			  }
			).then(async() => {
			  const index = scope.$index
			  const id = scope.row.id
			  
			  // 根据索引从 case_detail 中移除
			  if (Array.isArray(this.SuiteSave.func_cases_detail)) {
			    this.SuiteSave.func_cases_detail.splice(index, 1)
			  }
			  
			  // 根据 id 从 case 中移除
			  if (Array.isArray(this.SuiteSave.func_cases)) {
				this.SuiteSave.func_cases.splice(index, 1);
			 //    const idIndex = this.SuiteSave.func_cases.indexOf(id);
				// if (idIndex !== -1) {
				//   this.SuiteSave.func_cases.splice(idIndex, 1);
				// }
			  }
			}).catch(() => {})
		    
		},
		
		save(){
			if(common.hasEmptyValues(this.SuiteSave.conditions, ['value', 'method', 'andOr'])){
				ElMessage({message: "请完善测试套件条件表格数据，所有字段都必填", type: 'error'})
			}else if (this.isAdd){
				this.createSuite()
			}else{
				this.updateSuite()
			}
		},
		async createSuite(){
			this.$refs['suiteRef'].validate(async (valid, fields)=>{
				if(valid){
					this.SuiteSave.project = this.projectInfo.id
					const response = await this.$api.createSuite(this.SuiteSave)
					if(response.status === 201){
						this.editDialogVisible = false
						this.getSuites()
						ElMessage({message: "保存成功", type: 'success'})
					}
				}
			})
		},
		async updateSuite(){
			this.$refs['suiteRef'].validate(async (valid, fields)=>{
				if(valid){
					this.SuiteSave.project = this.projectInfo.id
					const response = await this.$api.updateSuite(this.SuiteSave.id, this.SuiteSave)
					if(response.status === 200){
						this.editDialogVisible = false
						this.getSuites()
						ElMessage({message: "保存成功", type: 'success'})
					}
				}
			})
		},
		async deleteSuite(id){
			ElMessageBox.confirm(
			    '确定删除此测试套件？删除后数据将无法恢复。',
			    '确认删除',
			    {
			      confirmButtonText: '确认删除',
			      cancelButtonText: '取消',
			      type: 'warning',
			      confirmButtonClass: 'el-button--danger',
			      customClass: 'confirm-dialog'
			    }
			  ).then(async() => {
				  const response = await this.$api.deleteSuite(id)
				  if (response.status === 204){
					  this.getSuites()
					  ElMessage({
					    type: 'success',
					    message: '删除成功',
					  })
				  }
				  
			    }).catch(() => {})
		},
		async getSuite(id){
			const response = await this.$api.getSuite(id)
			if (response.status === 200){
				this.SuiteSave = {...response.data.result}
			}
		},
		async getSuites(){
			this.suiteSearch.project = this.projectInfo.id
			this.SuiteSave.project = this.projectInfo.id
			const response = await this.$api.getSuites(Object.assign(this.suiteSearch, this.page_size_params, this.sort_params))
			if (response.status === 200){
				this.suite_list = {...response.data}
			}
		},
		async getWebExecutors(){
			const response = await this.$api.getWebExecutors({project: this.projectInfo.id, type: 2})
			if (response.status === 200){
				this.web_executor_list = [...response.data.results]
			}
		},
		async getAndroidExecutors(){
			const response = await this.$api.getAppExecutors({project: this.projectInfo.id, platform_name: 1})
			if (response.status === 200){
				this.android_executor_list = [...response.data.results]
			}
		},
		async getIosExecutors(){
			const response = await this.$api.getAppExecutors({project: this.projectInfo.id, platform_name: 1})
			if (response.status === 200){
				this.ios_executor_list = [...response.data.results]
			}
		},

		async check_permission(){
			const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission[this.$route.path]}
			const response = await this.$api.check_permission(params)
			if (response.status === 200){
				this.permission = { ...response.data.result }
			}
		},

		async getEnvs(){
			const response = await this.$api.getEnvs({project: this.projectInfo.id})
			if (response.status === 200){
				this.env_list = {...response.data}
			}
		},
	},
	created() {
		this.check_permission()
		this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
		this.getSuites()
		this.getWebExecutors()
		this.getAndroidExecutors()
		this.getIosExecutors()
		this.getEnvs()
	}
}
</script>

<style scoped>
.suite-management-container {
	width: 100%;
	background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
	padding: 20px 15px 15px 15px;
	box-sizing: border-box;
	display: flex;
	flex-direction: column;
	gap: 20px;
	min-height: calc(100vh - 75px);
	max-height: calc(100vh - 75px);
	height: calc(100vh - 75px);
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
	background: white;
	border: none;
	border-radius: 16px;
	overflow: hidden;
	flex-shrink: 0;
}

.filter-card :deep(.el-card__body) {
	padding: 20px 20px 0 20px;
}

.filter-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 15px 24px 10px 24px;
	border-bottom: 1px solid #f1f5f9;
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
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
	background: white;
	transform: rotate(45deg);
}

.filter-title {
	margin: 0;
	font-size: 18px;
	font-weight: 600;
	color: #1a1a1a;
	background: linear-gradient(135deg, #1a1a1a 0%, #4a5568 100%);
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
	border: 1px solid #e2e8f0;
	background: white;
	color: #64748b;
	font-weight: 500;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
}

.reset-btn:hover {
	background: #f8fafc;
	border-color: #cbd5e1;
	transform: translateY(-1px);
}

.reset-btn .el-icon {
	margin-right: 8px;
	font-size: 16px;
}

.search-btn {
	padding: 10px 24px;
	border-radius: 10px;
	background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
	border: none;
	font-weight: 500;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
}

.search-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.search-btn .el-icon {
	margin-right: 8px;
	font-size: 16px;
}

.filter-form-wrapper {
	padding: 25px 24px 0px 24px;
}

.inline-form {
	margin-bottom: 0;
}

/* 水平布局的表单项 */
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
  color: #475569;
  width: 90px;
  margin-right: 10px;
  flex-shrink: 0;
  white-space: nowrap;
}

.label-text {
  white-space: nowrap;
}

.icon-user,
.icon-role,
.icon-email,
.icon-creator,
.icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
}

/* 为图标添加背景颜色 */
.icon-user {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 4px;
}

.icon-role {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border-radius: 4px;
}

.icon-email {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 4px;
}

.icon-creator {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 4px;
}

.icon-updater {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border-radius: 4px;
}

.label-with-icon .icon-suite-name {
	width: 16px;
	height: 16px;
	display: inline-block;
	flex-shrink: 0;
	border-radius: 4px;
	background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
}

/* 输入框和下拉框样式 */
.input-elegant, .select-elegant {
	flex: 1;
	min-width: 0;
}

.input-elegant >>> .el-input__inner,
.select-elegant >>> .el-input__inner {
	border-radius: 10px;
	border: 1px solid #e2e8f0;
	background: #f8fafc;
	padding: 0 15px;
	box-shadow: none;
	transition: all 0.3s ease;
	height: 40px;
	line-height: 40px;
}

.input-elegant >>> .el-input__inner:hover,
.select-elegant >>> .el-input__inner:hover {
	border-color: #cbd5e1;
	background: white;
}

.input-elegant >>> .el-input__inner:focus,
.select-elegant >>> .el-input__inner:focus {
	border-color: #3b82f6;
	box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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
}

.content-header {
	padding: 20px 24px;
	border-bottom: 1px solid #f1f5f9;
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
	color: #1a1a1a;
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
	background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
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
	background: #f8fafc;
	border-radius: 8px;
	border: 1px solid #e2e8f0;
}

.stat-label {
	font-size: 12px;
	color: #64748b;
	font-weight: 500;
}

.stat-value {
	font-size: 14px;
	font-weight: 600;
	color: #1a1a1a;
}

.add-btn {
	padding: 10px 24px;
	border-radius: 10px;
	background: linear-gradient(135deg, #10b981 0%, #059669 100%);
	border: none;
	font-weight: 500;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
}

.add-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.add-btn .el-icon {
	margin-right: 8px;
	font-size: 16px;
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

.elegant-table >>> .el-table__header-wrapper th {
	background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
	font-weight: 600;
	color: #1a1a1a;
	border-bottom: 1px solid #e2e8f0;
	padding: 16px 0;
}

.elegant-table >>> .el-table__header-wrapper .cell {
	padding: 0 16px;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row {
	transition: all 0.3s ease;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row:nth-child(even) {
	background: #f8fafc;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row:hover {
	background: #f1f8ff;
	transform: translateX(4px);
}

.elegant-table >>> .el-table__body-wrapper .el-table__row.active-row {
	background: #ebf5ff;
	position: relative;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row.active-row::before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	width: 4px;
	background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%);
}

.elegant-table >>> .el-table__body-wrapper td {
	border-bottom: 1px solid #f1f5f9;
	padding: 16px 0;
	transition: all 0.3s ease;
}

.elegant-table >>> .el-table__body-wrapper .cell {
	padding: 0 16px;
}

/* 序号单元格 */
.index-cell {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 32px;
	height: 32px;
	background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
	border-radius: 8px;
	font-weight: 600;
	color: #475569;
	margin: 0 auto;
}

/* 测试套件名称单元格 */
.suite-name-cell {
	display: flex;
	align-items: center;
	justify-content: center;
}

.suite-name-text {
	font-weight: 500;
	color: #1a1a1a;
	line-height: 1.4;
}

/* 测试套件类型标签 */
.suite-type-tag {
	font-weight: 500;
	padding: 4px 10px;
	border-radius: 20px;
	border: none;
}

/* 重试单元格 */
.retry-cell {
	display: flex;
	align-items: center;
	justify-content: center;
}

/* 时间单元格 */
.time-cell {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	color: #64748b;
	font-size: 13px;
}

.icon-time {
	width: 14px;
	height: 14px;
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
	background-size: contain;
	background-repeat: no-repeat;
}

/* 操作按钮 */
.action-buttons {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
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

.action-btn.view-btn:hover {
	box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4);
}

.action-btn.run-btn:hover {
	box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.action-btn.edit-btn:hover {
	box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.action-btn.delete-btn:hover {
	box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.action-btn:active {
	transform: translateY(0) scale(0.95);
}

.action-btn.view-btn {
	background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.action-btn.run-btn {
	background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.action-btn.edit-btn {
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.action-btn.delete-btn {
	background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
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
	border-top: 1px solid #f1f5f9;
	flex-shrink: 0;
	display: block !important;
	min-height: 40px;
	background: white;
	float: right;
	z-index: 10;
	position: relative;
	opacity: 1 !important;
	visibility: visible !important;
}



/* 对话框样式 */
.elegant-dialog >>> .el-dialog {
	border-radius: 16px;
	overflow: hidden;
	box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.elegant-dialog >>> .el-dialog__header {
	padding: 24px;
	margin: 0;
	border-bottom: 1px solid #f1f5f9;
	background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
}

.elegant-dialog >>> .el-dialog__title {
	font-size: 20px;
	font-weight: 700;
	color: #1a1a1a;
	position: relative;
	padding-left: 16px;
}

.elegant-dialog >>> .el-dialog__title::before {
	content: '';
	position: absolute;
	left: 0;
	top: 50%;
	transform: translateY(-50%);
	width: 4px;
	height: 24px;
	background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
	border-radius: 2px;
}

.elegant-dialog >>> .el-dialog__body {
	padding: 24px;
}

.run-dialog-form {
	margin: 0;
}

.dialog-form {
	margin: 0;
}

.dialog-label {
	display: flex;
	align-items: center;
	gap: 8px;
	margin-bottom: 8px;
	font-size: 14px;
	font-weight: 600;
	color: #334155;
}

.icon-suite-name,
.icon-suite-type,
.icon-executor,
.icon-retry,
.icon-push,
.icon-condition {
	width: 16px;
	height: 16px;
	display: inline-block;
	background-size: contain;
	background-repeat: no-repeat;
}

.icon-suite-name {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M4 6h16v2H4zm0 4h16v2H4zm0 4h10v2H4z'/%3E%3C/svg%3E");
}

.icon-suite-type {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E");
}

.icon-executor {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
}

.icon-retry {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z'/%3E%3C/svg%3E");
}

.icon-push {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z'/%3E%3C/svg%3E");
}

.icon-condition {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h10v2H7zm0 4h7v2H7z'/%3E%3C/svg%3E");
}

.dialog-input >>> .el-input__inner {
	border-radius: 12px;
	border: 1px solid #e2e8f0;
	background: white;
	padding: 0 16px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
	transition: all 0.3s ease;
	height: 40px;
	line-height: 40px;
}

.dialog-input >>> .el-input__inner:hover {
	border-color: #cbd5e1;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-input >>> .el-input__inner:focus {
	border-color: #3b82f6;
	box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.dialog-select {
	width: 100%;
}

.dialog-select >>> .el-input__inner {
	border-radius: 12px;
	border: 1px solid #e2e8f0;
	background: white;
	padding: 0 16px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
	transition: all 0.3s ease;
	height: 40px;
	line-height: 40px;
}

.dialog-select >>> .el-input__inner:hover {
	border-color: #cbd5e1;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-select >>> .el-input__inner:focus {
	border-color: #3b82f6;
	box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.suite-condition-item {
	margin-top: 20px;
}

.suite-condition-wrapper {
	border: 1px solid #e2e8f0;
	border-radius: 12px;
	padding: 16px;
	width: 100%;
	background: #f8fafc;
}

.run-dialog-form .el-form-item {
	margin-bottom: 20px;
}

.run-dialog-form .el-form-item__label {
	font-weight: 600;
	color: #334155;
}

.env-select,
.async-select {
	width: 100%;
}

.elegant-dialog >>> .el-dialog__footer {
	padding: 16px 24px;
	border-top: 1px solid #f1f5f9;
	background: white;
}

.dialog-footer {
	display: flex;
	justify-content: flex-end;
	gap: 12px;
}

/* 合并列样式 */
.user-time-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
  padding: 8px 0;
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

.dialog-cancel-btn {
	padding: 10px 24px;
	border-radius: 10px;
	border: 1px solid #e2e8f0;
	background: white;
	color: #64748b;
	font-weight: 500;
	transition: all 0.3s ease;
}

.dialog-cancel-btn:hover {
	background: #f8fafc;
	border-color: #cbd5e1;
	transform: translateY(-1px);
}

.dialog-confirm-btn {
	padding: 10px 24px;
	border-radius: 10px;
	background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
	border: none;
	font-weight: 500;
	transition: all 0.3s ease;
}

.dialog-confirm-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
	.suite-management-container {
		padding: 16px;
	}
	
	.filter-card .filter-header,
	.filter-card .filter-form-wrapper,
	.content-card .content-header,
	.content-card .table-wrapper {
		padding: 16px 20px;
	}
}

@media screen and (max-width: 768px) {
	.suite-management-container {
		padding: 12px;
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
	
	/* 在移动端将水平布局改回垂直布局 */
	.form-item-horizontal {
		flex-direction: column;
		align-items: flex-start;
	}
	
	.horizontal-label {
		width: 100%;
		margin-right: 0;
		margin-bottom: 8px;
	}
	
	.input-elegant, .select-elegant {
		width: 100%;
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
	
	.add-btn {
		width: 100%;
	}
	
	.table-wrapper {
		overflow-x: auto;
	}
	
	.elegant-table {
		min-width: 800px;
	}
	
	.pagination-wrapper {
		padding: 15px 20px;
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
</style>