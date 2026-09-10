<template>
	<!-- 执行测试套件对话框 -->
	<el-dialog v-model="runTimesVisible" title="执行所有关联脚本用例" width="600" class="elegant-dialog">
	    <el-form :model="runPlanForm" label-width="120px" class="run-dialog-form" :rules="runRules" ref='runRef' label-position='top'>
			<el-form-item label="执行环境" prop="env_id">
				<el-select v-model="runPlanForm.env_id" class="select" placeholder="请选择执行环境" popper-class='select-dropdown-rounded' size='large'>
					<el-option
					  v-for="item in env_list.results"
					  :key="item.id"
					  :label="item.name"
					  :value="item.id"
					/>
				</el-select>
			</el-form-item>
			<!-- <el-form-item label="是否并发执行" prop="is_async">
				<el-select v-model="runPlanForm.is_async" class="select" popper-class='select-dropdown-rounded' size='large'>
					<el-option label='是' :value='true'/>
					<el-option  label='否' :value='false' />
				</el-select>
			</el-form-item> -->
			<!-- <el-form-item label="并发数" prop="count" v-if='runPlanForm.is_async'>
				<el-input-number v-model="runPlanForm.count" :min="1" :max="4" style="width: 100%;" size='large' class='input'/>
			</el-form-item> -->
	    </el-form>
	    <template #footer>
			<span class="dialog-footer">
				<el-button @click="runTimesVisible = false" class="dialog-cancel-btn">取消</el-button>
				<el-button type="primary" @click="runPlan" class="dialog-confirm-btn">执行</el-button>
			</span>
	    </template>
	</el-dialog>
	
	<!-- 测试计划编辑对话框 -->
	<el-dialog
		v-model="editDialogVisible" 
		:show-close="true" 
		:title="title"
		width="500px"
		class="elegant-dialog"
	>
		<el-form :model="PlanSave" :disabled="tagView" :rules="planRules" ref='planRef' class="dialog-form" position="top">
			<el-row :gutter="20">
				<el-col :span='24'>
					<el-form-item  prop='name'>
						<label class="dialog-label">
							<i class="icon-plan-name"></i>
							测试计划名称
						</label>
						<el-input v-model="PlanSave.name" autocomplete="off" placeholder="请输入测试计划名称" class="input" size='large' show-word-limit maxlength="50"/>
					</el-form-item>
				</el-col>
				<el-col :span='24' >
					<el-form-item  prop='start_end_time'>
						<label class="dialog-label">
							<i class="icon-executor"></i>
							测试计划起止时间
						</label>
						 <el-date-picker
							v-model="PlanSave.start_end_time"
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
							测试计划描述
						</label>
						 <el-input
						   v-model="PlanSave.desc" 
						   autocomplete="off" 
						   placeholder="请输入测试计划描述"
						   maxlength="200"
						   show-word-limit
						   type="textarea"
						   size='large'
						   class="text"
						 />
					</el-form-item>
				</el-col>
			</el-row>
		</el-form>
		<template #footer>
			<span class="dialog-footer" v-if='!tagView'>
				<el-button @click="editDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
				<el-button type="primary" @click="save" v-if='permission.has_add_permission || permission.has_edit_permission' class="dialog-confirm-btn">保存</el-button>
			</span>
		</template>
	</el-dialog>

	<!-- 主页面 -->
	<div class="plan-management-container">
		<!-- 搜索筛选区域 -->
		<el-card class="filter-card elegant-shadow">
			<div class="filter-header">
				<div class="header-title-section">
					<i class="icon-search"></i>
					<h3 class="filter-title">测试计划筛选</h3>
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
				<el-form :model="planSearch" class="filter-form inline-form">
					<el-row :gutter="24">
						<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="form-item-inline">
								<div class="label-with-icon">
									<i class="icon-plan-name"></i>
									<span class='label-text'>计划名称</span>
								</div>
								<el-input 
									v-model="planSearch.name" 
									placeholder="请输入测试计划名称" 
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
									v-model="planSearch.create_by" 
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
									v-model="planSearch.update_by" 
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
						<h3 class="content-title">测试计划列表</h3>
						<div class="stats-info">
							<div class="stat-item">
								<span class="stat-label">总计</span>
								<span class="stat-value">{{ plan_list.count || 0 }}</span>
							</div>
							<div class="stat-item">
								<span class="stat-label">当前页</span>
								<span class="stat-value">{{ page_size_params.page }}</span>
							</div>
						</div>
					</div>
					<el-button 
						v-if='permission.has_add_permission' 
						@click="addPlan" 
						type="primary" 
						class="add-btn"
					>
						<el-icon><Plus /></el-icon>新增测试计划
					</el-button>
				</div>
			</div>

			<!-- 数据表格 -->
			<div class="table-wrapper">
				<el-table 
					:data="plan_list.results" 
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
						label="测试计划名称" 
						prop="name" 
						min-width="150" 
						align="center"
						class-name="plan-name-column"
					>
						<template #default="scope">
							<div class="plan-name-cell">
								<el-tooltip 
									effect="dark" 
									:content="scope.row.name" 
									placement="top-start"
								>
									<div class="plan-name-text">
										{{ scope.row.name && scope.row.name.length > 20 ? scope.row.name.slice(0, 20) + '...' : scope.row.name }}
									</div>
								</el-tooltip>
							</div>
						</template>
					</el-table-column>
					
					<el-table-column 
						label="状态" 
						width="180" 
						align="center"
						class-name="status-column"
					>
						<template #default="scope">
							<div class="status-container">
								<el-tag 
									:type="getStatusType(scope.row.status)" 
									effect="light"
									size="small"
									class="status-tag"
								>
									{{ scope.row.status_name }}
								</el-tag>
								<span class="progress-count" v-if="scope.row.total_count > 0">
									({{ (scope.row.passed_count || 0 + scope.row.failed_count || 0) }}/{{ scope.row.total_count || 0 }})
								</span>
							</div>
						</template>
					</el-table-column>
					
					<el-table-column 
						label="通过率" 
						width="180" 
						align="center"
						class-name="pass-rate-column"
					>
						<template #default="scope">
							<el-tooltip 
								placement="top"
								:show-arrow="false"
								effect="dark"
							>
								<template #content>
									<div class="rate-tooltip">
										<div class="tooltip-item">
											<span class="tooltip-label">总用例数:</span>
											<span class="tooltip-value">{{ scope.row.total_count || 0 }}</span>
										</div>
										<div class="tooltip-item">
											<span class="tooltip-label">通过:</span>
											<span class="tooltip-value success">{{ scope.row.passed_count || 0 }}</span>
										</div>
										<div class="tooltip-item">
											<span class="tooltip-label">失败:</span>
											<span class="tooltip-value danger">{{ scope.row.failed_count || 0 }}</span>
										</div>
										<div class="tooltip-item">
											<span class="tooltip-label">进行中:</span>
											<span class="tooltip-value primary">{{ scope.row.in_progress_count || 0 }}</span>
										</div>
										<div class="tooltip-item">
											<span class="tooltip-label">未执行:</span>
											<span class="tooltip-value warning">{{ scope.row.not_executed_count || 0 }}</span>
										</div>
										<div class="tooltip-item">
											<span class="tooltip-label">阻塞:</span>
											<span class="tooltip-value info">{{ scope.row.postponed_count || 0 }}</span>
										</div>
									</div>
								</template>
								<div class="pass-rate-container">
									<div class="pass-rate-bar">
										<div 
											v-if="scope.row.total_count > 0"
											class="rate-segment passed"
											:style="{ width: getSegmentWidth(scope.row.passed_count, scope.row.total_count) }"
										></div>
										<div 
											v-if="scope.row.total_count > 0"
											class="rate-segment failed"
											:style="{ width: getSegmentWidth(scope.row.failed_count, scope.row.total_count) }"
										></div>
										<div 
											v-if="scope.row.total_count > 0"
											class="rate-segment in-progress"
											:style="{ width: getSegmentWidth(scope.row.in_progress_count, scope.row.total_count) }"
										></div>
										<div 
											v-if="scope.row.total_count > 0"
											class="rate-segment postponed"
											:style="{ width: getSegmentWidth(scope.row.postponed_count, scope.row.total_count) }"
										></div>
										<div 
											v-if="scope.row.total_count > 0"
											class="rate-segment not-executed"
											:style="{ width: getSegmentWidth(scope.row.not_executed_count, scope.row.total_count) }"
										></div>
									</div>
									<span class="pass-rate-text">{{ scope.row.pass_rate || 0 }}%</span>
								</div>
							</el-tooltip>
						</template>
					</el-table-column>
					
					<!-- 合并列：计划起止时间 -->
					<el-table-column 
					  label="计划起止时间" 
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
									content="计划概览" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type="info"
										v-if="permission.has_read_permission" 
										:icon="DataLine" 
										@click="openPlanOverview(scope.row)" 
										class="action-btn overview-btn"
										circle
									></el-button>
								</el-tooltip>

								<el-tooltip 
									content="查看关联最新的自动化测试报告" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type="success" 
										v-if="permission.has_read_permission" 
										:icon="View" 
										@click="viewPlanReport(scope.row)" 
										class="action-btn view-btn"
										circle
									></el-button>
								</el-tooltip>
								
								<el-tooltip 
									content="进入详情" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type='primary' 
										v-if="permission.has_read_permission" 
										:icon="Pointer" 
										@click="run(scope.row)" 
										class="action-btn run-btn"
										circle
									></el-button>
								</el-tooltip>

								<el-tooltip
									content="执行关联所有关联脚本用例"
									placement="top"
									effect="dark"
								>
									<el-button
										type='primary'
										v-if="permission.has_eidt_permission || permission.has_add_permission"
										:icon="VideoPlay"
										@click="openPlanDialog(scope.row)"
										class="action-btn run-btn"
										circle
									></el-button>
								</el-tooltip>
								
								<el-tooltip 
									content="编辑测试计划" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type='warning' 
										v-if="permission.has_edit_permission" 
										:icon="EditPen" 
										@click="editPlan(scope.row)" 
										class="action-btn edit-btn"
										circle
									></el-button>
								</el-tooltip>
								
								<el-tooltip 
									content="删除测试计划" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type="danger" 
										v-if="permission.has_delete_permission" 
										@click="deletePlan(scope.row.id)" 
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
					:total="plan_list.count"
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
import { View, Delete, VideoPlay, Plus, EditPen, Cpu, Refresh, Search, Pointer, DataLine, CircleCheck, CircleClose, Warning, Clock, Collection } from '@element-plus/icons-vue'
import CaseList from '../case/CaseList.vue'
import FunCaseList from '../case/FunCaseList.vue'
import * as common from '../../utils/common.js'
export default{
	computed:{
		...mapState(['pathPermission', 'projectInfo', 'env_id', 'userInfo']),
		calcMinWidth() {
	  let visibleButtons = 0;
	  if (this.permission.has_read_permission) visibleButtons += 2;
	  if (this.permission.has_edit_permission && this.permission.has_add_permission){
		  visibleButtons += 2
	  }else if(this.permission.has_edit_permission){
		  visibleButtons += 2
	  }else{
		   visibleButtons += 1
	  }
	  if (this.permission.has_delete_permission) visibleButtons += 1;
	  return Math.max(10, visibleButtons * 60);
	},
	},
	components: {
		CaseList,
		FunCaseList
	},
	data() {
		return {
			tagView: false,
			permission: {},
			chooseCaseVisible: false,
			chooseFuncCaseVisible: false,
			planSearch:{
				name: '',
				project: '',
				create_by: '',
				update_by: '',
			},
			page_size_params: {
				page: 1,
				size: 10,
			},
			count: 1,
			runTimesVisible: false,
			title: '新增测试计划',
			isAdd: true,
			editDialogVisible: false,
			plan_list: [],
			plant_module_list: [],
			module_list: [],
			ViewVisible: false,
			caseType:{'API': 1,'WEB_UI': 2, 'APP_UI': 3},
			runPlanForm: {
				env_id: '',
				plan_id: ''
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
			PlanSave:{
				project: '',
				name: '',
				desc: '',
				start_end_time: [],
			},
			sort_params: {
			  ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
			},
			planRules: {
				name: [{
					required: true,
					message: '测试计划名称不能为空',
					trigger: 'blur',
				}],
				desc: [{
					required: true,
					message: '测试计划描述不能为空',
					trigger: 'blur',
				}],
				start_end_time: [{
					required: true,
					message: '请选择测试计划起止时间',
					trigger: 'change',
				}],
			},

		}
	},
	setup() {
		return {
			VideoPlay,
			Delete,
			Plus,
			View,
			EditPen,
			Pointer,
			Cpu,
			Refresh,
			Search,
			DataLine,
			CircleCheck,
			CircleClose,
			Warning,
			Clock,
			Collection
		}
	},
	methods:{
		...mapActions(['getRolePermission']),
		getStatusType(status) {
			switch(status) {
				case 1:
					return 'info'
				case 2:
					return 'warning'
				case 3:
					return 'success'
				case 4:
					return 'danger'
				default:
					return 'info'
			}
		},
		calculatePassRate(row) {
			console.log('calculatePassRate called with row:', row)
			// 处理 Proxy 对象，确保能正确访问属性
			const passRate = row.pass_rate
			console.log('pass_rate value:', passRate)
			if (passRate !== undefined && passRate !== null) {
				console.log('Using pass_rate from backend:', passRate)
				return passRate
			}
			console.log('pass_rate not found, calculating manually')
			const totalCount = row.total_count
			const passedCount = row.passed_count
			if (!totalCount || totalCount === 0) return 0
			const calculatedRate = Math.round((passedCount || 0) / totalCount * 100)
			console.log('Calculated rate:', calculatedRate)
			return calculatedRate
		},
		getSegmentWidth(count, total) {
			if (!total || total === 0) return '0%'
			return `${Math.round((count || 0) / total * 100)}%`
		},
		getRateWidth(rate) {
			const width = Math.min(100, Math.max(0, rate || 0))
			return `${width}%`
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
		  this.getPlans()
		},
		
		async runPlan(){
			this.$refs['runRef'].validate(async (valid, fields)=>{
				if(valid){
					this.runTimesVisible = false
					const response = await this.$api.runPlanCaseAutomation(this.runPlanForm)
					ElMessage({message: '已开始执行整个测试计划功能用例关联的脚本用例', type: 'success'})
					this.$router.push({ path: `/exec/plan/detail/${this.runPlanForm.plan_id}`})
				}
			})
		},
		handleCurrentChange(){
			this.getPlans()
		},
		handleSizeChange(){
			this.page_size_params.page = 1
			this.getPlans()
		},
		search(){
			this.page_size_params.page = 1
			this.getPlans()
		},
		reset(){
			for(let key in this.planSearch){
				this.planSearch[key] = ''
			}
			this.page_size_params.page = 1
			this.getPlans()
		},
		editPlan(row_data){
			this.isAdd = false
			this.tagView = false
			this.title = '编辑测试计划'
			this.getPlan(row_data.id)
			this.editDialogVisible = true
			this.$refs.planRef.resetFields();
		},
		openPlanDialog(obj){
			this.runTimesVisible = true
			this.runPlanForm.plan_id = obj.id
			this.$refs.runRef.resetFields();
		},
		viewPlanReport(row_data){
			if (!row_data.report_id) {
				ElMessage({message: '该测试计划未关联自动化测试报告', type: 'warning'})
				return
			}
			this.$router.push({ path: '/report/listView', query: { id: row_data.report_id } })
			// this.isAdd = false
			// this.title = '查看测试计划'
			// this.tagView = true
			// this.getPlan(row_data.id)
			// this.editDialogVisible = true
		},
		async openPlanOverview(row_data) {
			this.$router.push({
				name: 'TestPlanOverview',
				params: { id: row_data.id }
			})
		},
		addPlan(){
			this.title = '新增测试计划'
			this.tagView = false
			this.editDialogVisible = true
			this.isAdd = true
			this.PlanSave.id = 0
			this.$refs.planRef.resetFields();
		},
		
		save(){
			if (this.isAdd){
				this.createPlan()
			}else{
				this.updatePlan()
			}
		},
		async createPlan(){
			this.$refs['planRef'].validate(async (valid, fields)=>{
				if(valid){
					this.PlanSave.project = this.projectInfo.id
					const response = await this.$api.createPlan(this.PlanSave)
					if(response.status === 201){
						this.editDialogVisible = false
						this.getPlans()
						ElMessage({message: "保存成功", type: 'success'})
					}
				}
			})
		},
		async updatePlan(){
			this.$refs['planRef'].validate(async (valid, fields)=>{
				if(valid){
					this.PlanSave.project = this.projectInfo.id
					const response = await this.$api.updatePlan(this.PlanSave.id, this.PlanSave)
					if(response.status === 200){
						this.editDialogVisible = false
						this.getPlans()
						ElMessage({message: "保存成功", type: 'success'})
					}
				}
			})
		},
		async deletePlan(id){
			ElMessageBox.confirm(
			    '确定删除此测试计划？删除后数据将无法恢复。',
			    '确认删除',
			    {
			      confirmButtonText: '确认删除',
			      cancelButtonText: '取消',
			      type: 'warning',
			      confirmButtonClass: 'el-button--danger',
			      customClass: 'confirm-dialog'
			    }
			  ).then(async() => {
				  const response = await this.$api.deletePlan(id)
				  if (response.status === 204){
					  this.getPlans()
					  ElMessage({
					    type: 'success',
					    message: '删除成功',
					  })
				  }
				  
			    }).catch(() => {})
		},
		async getPlan(id){
			const response = await this.$api.getPlan(id)
			if (response.status === 200){
				this.PlanSave = {...response.data.result}
			}
		},
		async getPlans(){
			this.planSearch.project = this.projectInfo.id
			this.PlanSave.project = this.projectInfo.id
			const response = await this.$api.getPlans(Object.assign(this.planSearch, this.page_size_params, this.sort_params))
			if (response.status === 200){
				this.plan_list = {...response.data}
				console.log('getPlans response data:', response.data)
				console.log('plan_list results:', this.plan_list.results)
				if (this.plan_list.results && this.plan_list.results.length > 0) {
					console.log('First plan data:', this.plan_list.results[0])
					console.log('First plan pass_rate:', this.plan_list.results[0].pass_rate)
				}
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
		run(row) {
			this.$router.push({
				name: 'TestPlanDetail',
				params: { id: row.id }
			})
		}
	},
	created() {
		this.check_permission()
		this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
		this.getPlans()
		this.getEnvs()
	}
}
</script>

<style scoped>
.plan-management-container {
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

.label-with-icon .icon-plan-name {
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

/* 测试计划名称单元格 */
.plan-name-cell {
	display: flex;
	align-items: center;
	justify-content: center;
}

.plan-name-text {
	font-weight: 500;
	color: #1a1a1a;
	line-height: 1.4;
}

/* 测试计划类型标签 */
.plan-type-tag {
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

.action-btn.overview-btn {
	background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}

.action-btn.overview-btn:hover {
	box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
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

.icon-plan-name,
.icon-plan-type,
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

.icon-plan-name {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M4 6h16v2H4zm0 4h16v2H4zm0 4h10v2H4z'/%3E%3C/svg%3E");
}

.icon-plan-type {
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

.plan-condition-item {
	margin-top: 20px;
}

.plan-condition-wrapper {
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

/* 计划概览弹窗样式 */
.overview-content {
	padding: 10px 0;
}

.overview-top {
	display: flex;
	gap: 24px;
	margin-bottom: 24px;
}

.overview-left {
	flex: 1;
	background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
	border-radius: 20px;
	padding: 28px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
	border: 1px solid rgba(148, 163, 184, 0.15);
	transition: all 0.3s ease;
}

.overview-left:hover {
	box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
	transform: translateY(-2px);
}

.overview-right {
	flex: 1;
	background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
	border-radius: 20px;
	padding: 28px;
	box-shadow: 0 4px 20px rgba(59, 130, 246, 0.1), 0 1px 3px rgba(0, 0, 0, 0.05);
	border: 1px solid rgba(59, 130, 246, 0.15);
	transition: all 0.3s ease;
}

.overview-right:hover {
	box-shadow: 0 8px 30px rgba(59, 130, 246, 0.15), 0 2px 8px rgba(0, 0, 0, 0.08);
	transform: translateY(-2px);
}

.icons-container {
	display: flex;
	gap: 16px;
	margin-bottom: 24px;
	flex-wrap: wrap;
	justify-content: space-between;
}

.rate-card {
	flex: 1;
	min-width: 180px;
	max-width: 300px;
}

.progress-card {
	flex: 1;
	min-width: 150px;
	background: rgba(255, 255, 255, 0.8);
	border-radius: 12px;
	padding: 20px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(148, 163, 184, 0.1);
}

.progress-label {
	font-size: 14px;
	font-weight: 500;
	margin-bottom: 12px;
	color: #334155;
}

.progress-text {
	font-size: 14px;
	color: #94a3b8;
	text-align: center;
	padding: 20px 0;
}

.overview-bottom {
	background: linear-gradient(135deg, #faf5ff 0%, #ffffff 100%);
	border-radius: 20px;
	padding: 28px;
	margin-bottom: 24px;
	box-shadow: 0 4px 20px rgba(139, 92, 246, 0.1), 0 1px 3px rgba(0, 0, 0, 0.05);
	border: 1px solid rgba(139, 92, 246, 0.15);
	transition: all 0.3s ease;
}

.overview-bottom:last-child {
	margin-bottom: 0;
}

.overview-bottom:hover {
	box-shadow: 0 8px 30px rgba(139, 92, 246, 0.15), 0 2px 8px rgba(0, 0, 0, 0.08);
	transform: translateY(-2px);
}

.section-title {
	font-size: 18px;
	font-weight: 800;
	color: #1e293b;
	margin-bottom: 24px;
	padding-bottom: 12px;
	display: flex;
	align-items: center;
	gap: 12px;
}

.section-title::before {
	content: '';
	width: 5px;
	height: 24px;
	background: linear-gradient(180deg, #6366f1, #8b5cf6);
	border-radius: 3px;
	box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
}

.info-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 16px;
}

.info-item {
	display: flex;
	flex-direction: column;
	gap: 6px;
	padding: 14px 18px;
	background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
	border-radius: 12px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
	border: 1px solid rgba(148, 163, 184, 0.15);
	transition: all 0.2s ease;
}

.info-item:hover {
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
	transform: translateY(-1px);
}

.info-label {
	font-size: 12px;
	font-weight: 600;
	color: #64748b;
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.info-value {
	font-size: 14px;
	font-weight: 600;
	color: #1e293b;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}



.rate-card {
	display: flex;
	justify-content: center;
	margin-bottom: 20px;
}

.rate-circle {
	width: 120px;
	height: 120px;
	border-radius: 50%;
	background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
}

.rate-value {
	font-size: 32px;
	font-weight: 800;
	color: white;
	line-height: 1;
	font-family: 'SF Mono', 'Consolas', monospace;
}

.rate-label {
	font-size: 12px;
	font-weight: 600;
	color: rgba(255, 255, 255, 0.9);
	margin-top: 4px;
}

.status-mini-cards {
	display: grid;
	grid-template-columns: repeat(6, 1fr);
	gap: 10px;
}

.mini-card {
	padding: 12px 8px;
	border-radius: 10px;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 4px;
}

.mini-label {
	font-size: 11px;
	font-weight: 600;
}

.mini-value {
	font-size: 20px;
	font-weight: 800;
	font-family: 'SF Mono', 'Consolas', monospace;
}

.mini-card.passed {
	background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
}

.mini-card.passed .mini-label {
	color: #059669;
}

.mini-card.passed .mini-value {
	color: #047857;
}

.mini-card.failed {
	background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
}

.mini-card.failed .mini-label {
	color: #dc2626;
}

.mini-card.failed .mini-value {
	color: #b91c1c;
}

.mini-card.blocked {
	background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
}

.mini-card.blocked .mini-label {
	color: #d97706;
}

.mini-card.blocked .mini-value {
	color: #b45309;
}

.mini-card.in-progress {
	background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
}

.mini-card.in-progress .mini-label {
	color: #3b82f6;
}

.mini-card.in-progress .mini-value {
	color: #2563eb;
}

.mini-card.not-executed {
	background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.mini-card.not-executed .mini-label {
	color: #475569;
}

.mini-card.not-executed .mini-value {
	color: #334155;
}

.mini-card.total {
	background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
}

.mini-card.total .mini-label {
	color: #4f46e5;
}

.mini-card.total .mini-value {
	color: #4338ca;
}

.overview-content {
	padding: 12px;
	background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
	border-radius: 12px;
}

.executor-cards {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 20px;
}

@media (max-width: 1200px) {
	.executor-cards {
		grid-template-columns: repeat(2, 1fr);
	}
}

@media (max-width: 768px) {
	.executor-cards {
		grid-template-columns: 1fr;
	}
}

.executor-card {
	background: linear-gradient(135deg, #ffffff 0%, #fefefe 100%);
	border-radius: 16px;
	padding: 20px;
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
	border: 1px solid rgba(139, 92, 246, 0.08);
	transition: all 0.3s ease;
}

.executor-card:hover {
	transform: translateY(-4px);
	box-shadow: 0 8px 24px rgba(139, 92, 246, 0.15);
	border-color: rgba(139, 92, 246, 0.2);
	background: white;
}



.executor-header {
	display: flex;
	align-items: center;
	gap: 12px;
	padding-bottom: 16px;
	border-bottom: 1px solid #f1f5f9;
}

.executor-avatar {
	width: 40px;
	height: 40px;
	border-radius: 50%;
	background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
	display: flex;
	align-items: center;
	justify-content: center;
	color: white;
	font-weight: 700;
	font-size: 16px;
}

.module-avatar {
	background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
}

.tag-avatar {
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
}

.module-avatar {
	background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
}

.module-filter-bar {
	margin-bottom: 20px;
}

.module-search-input {
	width: 300px;
}

.module-cards {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 16px;
}

@media (max-width: 1200px) {
	.module-cards {
		grid-template-columns: repeat(2, 1fr);
	}
}

@media (max-width: 768px) {
	.module-cards {
		grid-template-columns: 1fr;
	}
}

.view-more-container {
	display: flex;
	justify-content: center;
	margin-top: 20px;
	padding-top: 16px;
	border-top: 1px solid #f0f0f0;
}

.view-more-btn {
	min-width: 120px;
}

.rotate-icon {
	transform: rotate(180deg);
	transition: transform 0.3s ease;
}

.executor-info {
	flex: 1;
	min-width: 0;
	margin-left: 12px;
	display: flex;
	align-items: center;
	gap: 8px;
}

.executor-status {
	font-size: 12px;
	padding: 2px 8px;
	border-radius: 10px;
	font-weight: 500;
	display: inline-block;
	white-space: nowrap;
}

.status-idle {
	background: rgba(148, 163, 184, 0.1);
	color: #64748b;
}

.status-processing {
	background: rgba(59, 130, 246, 0.1);
	color: #3b82f6;
}

.status-completed {
	background: rgba(16, 185, 129, 0.1);
	color: #10b981;
}

.executor-name {
	font-weight: 600;
	color: #1e293b;
	font-size: 14px;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.executor-rate {
	font-size: 20px;
	font-weight: 800;
	color: #10b981;
	font-family: 'SF Mono', 'Consolas', monospace;
}

.executor-stats {
	display: grid;
	grid-template-columns: repeat(6, 1fr);
	gap: 8px;
	padding: 16px 0;
	margin: 8px 0;
}

.executor-stat-item {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 4px;
}



.executor-stat-item .stat-label {
	font-size: 11px;
	font-weight: 600;
	color: #64748b;
}

.executor-stat-item .stat-value {
	font-size: 16px;
	font-weight: 700;
	font-family: 'SF Mono', 'Consolas', monospace;
}

.executor-stat-item .stat-value.total {
	color: #4f46e5;
}

.executor-stat-item .stat-value.passed {
	color: #10b981;
}

.executor-stat-item .stat-value.failed {
	color: #ef4444;
}

.executor-stat-item .stat-value.blocked {
	color: #f59e0b;
}

.executor-stat-item .stat-value.in-progress {
	color: #3b82f6;
}

.executor-stat-item .stat-value.idle {
	color: #64748b;
}

.stats-card {
	background: #ffffff;
	border-radius: 16px;
	padding: 20px;
	border: 1px solid #e2e8f0;
	margin-bottom: 24px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stats-card-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 16px;
	padding-bottom: 12px;
	border-bottom: 1px solid #f1f5f9;
}

.stats-card-title {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 15px;
	font-weight: 600;
	color: #1e293b;
}

.stats-card-title i {
	font-size: 18px;
}

.stats-card-title .icon-module {
	color: #4f46e5;
}

.stats-card-title .icon-tag {
	color: #ec4899;
}

.stats-table-container {
	position: relative;
}

.stats-table-container .data-table {
	border-radius: 12px;
	overflow: hidden;
}

.stats-table-container .module-name {
	font-weight: 600;
	color: #1e293b;
}

.stats-table-container .tag-name {
	font-weight: 600;
	color: #1e293b;
}

.stats-table-container .number-value {
	font-weight: 700;
	color: #4f46e5;
	font-family: 'SF Mono', 'Consolas', monospace;
}

.stats-table-container .success-value {
	font-weight: 700;
	color: #10b981;
	font-family: 'SF Mono', 'Consolas', monospace;
}

.stats-table-container .error-value {
	font-weight: 700;
	color: #ef4444;
	font-family: 'SF Mono', 'Consolas', monospace;
}

.stats-table-container .warning-value {
	font-weight: 700;
	color: #f59e0b;
	font-family: 'SF Mono', 'Consolas', monospace;
}

.stats-table-container .percent-value {
	font-weight: 700;
	font-family: 'SF Mono', 'Consolas', monospace;
}

.stats-table-container .percent-good {
	color: #10b981;
}

.stats-table-container .percent-warning {
	color: #f59e0b;
}

.stats-table-container .percent-danger {
	color: #ef4444;
}

.empty-tip {
	text-align: center;
	color: #94a3b8;
	padding: 32px 0;
	font-size: 14px;
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
	.plan-management-container {
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
	.plan-management-container {
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

/* 状态标签样式 */
.status-container {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
}

.status-tag {
	font-weight: 500;
	padding: 4px 12px;
	border-radius: 20px;
}

.progress-count {
	font-size: 13px;
	font-weight: 600;
	color: #475569;
}

/* 通过率容器 */
.pass-rate-container {
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 0 8px;
}

.pass-rate-bar {
	flex: 1;
	height: 8px;
	background: #f1f5f9;
	border-radius: 4px;
	overflow: hidden;
	display: flex;
}

.rate-segment {
	height: 100%;
	transition: all 0.3s ease;
}

.rate-segment:first-child {
	border-radius: 4px 0 0 4px;
}

.rate-segment:last-child {
	border-radius: 0 4px 4px 0;
}

.rate-segment:only-child {
	border-radius: 4px;
}

.rate-segment.not-executed {
	background: linear-gradient(90deg, #94a3b8, #64748b);
}

.rate-segment.postponed {
	background: linear-gradient(90deg, #f59e0b, #d97706);
}

.rate-segment.failed {
	background: linear-gradient(90deg, #ef4444, #dc2626);
}

.rate-segment.passed {
	background: linear-gradient(90deg, #10b981, #059669);
}

.rate-segment.in-progress {
	background: linear-gradient(90deg, #3b82f6, #2563eb);
}

.pass-rate-text {
	font-size: 14px;
	font-weight: 600;
	color: #1a1a1a;
	min-width: 45px;
	text-align: right;
}

/* 悬浮提示样式 */
.rate-tooltip {
	padding: 8px 4px;
}

.tooltip-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 4px 0;
	min-width: 160px;
	gap: 20px;
}

.tooltip-label {
	font-size: 12px;
	color: #94a3b8;
}

.tooltip-value {
	font-size: 12px;
	font-weight: 600;
	color: white;
}

.tooltip-value.success {
	color: #4ade80;
}

.tooltip-value.danger {
	color: #f87171;
}

.tooltip-value.warning {
	color: #fbbf24;
}

.tooltip-value.info {
	color: #60a5fa;
}

.tooltip-value.primary {
	color: #3b82f6;
}

/* 对话框标题样式 */
.dialog-title {
	display: flex;
	align-items: center;
	gap: 12px;
}

.status-badge {
	font-size: 12px;
	padding: 2px 8px;
	border-radius: 10px;
	font-weight: 500;
	background: rgba(16, 185, 129, 0.1);
	color: #10b981;
	white-space: nowrap;
}
</style>