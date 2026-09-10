<template>
	<el-drawer v-model="lookLogVisible"  direction="rtl" :show-close='true' size="calc(100vw)" destroy-on-close>
		<template #header="{ close, titleId, titleClass }">
			  <h4>{{ this.one_case_log.case_name}}</h4>
		</template>
		<div>
			<el-collapse v-model="caseActive" accordion class='elegant-collapse'>
			   <el-collapse-item :name='case_index'>
				   <template #title>
				       <el-text v-if="one_case_log.result_value === '成功'" type="success">【用例执行人: {{ one_case_log.create_by_name }}】【用例执行环境: {{ one_case_log.env_name }}】【用例花费时间: {{one_case_log.time.toFixed(2)}}秒】【用例执行结果: {{one_case_log.result_value}}】</el-text>
				       <el-text v-if="one_case_log.result_value === '失败'" type="danger">【用例执行人: {{ one_case_log.create_by_name }}】 【用例执行环境: {{ one_case_log.env_name }}】【用例花费时间: {{one_case_log.time.toFixed(2)}}秒】【用例执行结果: {{one_case_log.result_value}}】</el-text>
				       <el-text v-if="one_case_log.result_value === '错误'" type="danger">【用例执行人: {{ one_case_log.create_by_name }}】 【用例执行环境: {{ one_case_log.env_name }}】【用例花费时间: {{one_case_log.time.toFixed(2)}}秒】【用例执行结果: {{one_case_log.result_value}}】</el-text>
				   </template>
				   <template v-for="(step_log, step_index) in one_case_log.logs" :key='step_index'>
					   <el-collapse v-model="stepActive" accordion>
					        <el-collapse-item :name='step_index'>
							   <template #title>
								   <el-text
								     type="danger" 
								     v-if="step_log.logs && step_log.logs.some(log => log.title && log.title.includes('【ERROR】'))">
								     【{{ step_log.step_desc }}】
								   </el-text>
								   <el-text type="success" v-else>【{{ step_log.step_desc }}】</el-text>
							   </template>
							   <template v-for="(log_info, log_index) in step_log.logs" :key='log_index'>
								   <el-collapse v-model="logActive" accordion>
									  <el-collapse-item :title="log_info.title" :name='log_info.title'>
										  <template #title>
											   <el-text v-if="log_info.title.includes('【INFO】')" type="success">{{ log_info.title }}</el-text>
											   <el-text v-if="log_info.title.includes('【ERROR】')" type="danger">{{ log_info.title }}</el-text>
											   <el-image v-if='log_info.hasOwnProperty("uri")'
											        style="width: 30px; height: 30px; f"
											        :src="log_info.uri"
											        :zoom-rate="1.2"
											        :max-scale="7"
											        :min-scale="0.2"
											        :preview-src-list="[log_info.uri]"
											        :initial-index="4"
											        fit="cover"
											      />
										  </template>
										  <TraceReplay v-if="log_info.trace_url || log_info.video_url" :log-info="log_info" />
										  <BodyEdit v-else :bind_case_data='bind_case_data' v-model='one_case_log.logs[step_index].logs[log_index].value'></BodyEdit>
									  </el-collapse-item>
								   </el-collapse>
							   </template>
							</el-collapse-item>
						</el-collapse>
					</template>
			   </el-collapse-item>
			</el-collapse>
		</div>
	</el-drawer>
	<div class="report">
		<el-card class="filter-card elegant-shadow" >
			<div class="filter-header">
				<div class="header-title-section">
					<i class="icon-search"></i>
					<h3 class="filter-title">测试日志筛选</h3>
					<el-tag size="small" type="info" effect="plain">模糊查询</el-tag>
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
				<el-form :model="logSearch" class="filter-form">
					<el-row :gutter="24">
						<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="form-item-enhanced">
								<div class="label-with-icon">
									<i class="icon-case"></i>
									<span>用例名称</span>
								</div>
								<el-input 
									v-model="logSearch.case_name" 
									placeholder="请输入用例名称" 
									clearable
									class='input'
									size='large'
								/>
							</el-form-item>
						</el-col>
						
						<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="form-item-enhanced">
								<div class="label-with-icon">
									<i class="icon-result"></i>
									<span>执行结果</span>
								</div>
								<el-select 
									v-model="logSearch.result" 
									placeholder="请选择执行结果" 
									clearable
									class="select"
									size='large'
									popper-class='select-dropdown-rounded'
								>
									<el-option 
										v-for="test_result in test_results" 
										:key="test_result.value"
										:label="test_result.name" 
										:value="test_result.value" 
									/>
								</el-select>
							</el-form-item>
						</el-col>
						
						<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="form-item-enhanced">
								<div class="label-with-icon">
									<i class="icon-env"></i>
									<span>执行环境</span>
								</div>
								<el-select 
									v-model="logSearch.env" 
									placeholder="请选择执行环境" 
									clearable
									filterable
									class="select"
									size='large'
									popper-class='select-dropdown-rounded'
									
								>
									<el-option 
										v-for="env_obj in env_list.results" 
										:key="env_obj.id"
										:label="env_obj.name" 
										:value="env_obj.id" 
									/>
								</el-select>
							</el-form-item>
						</el-col>
						
						<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="form-item-enhanced">
								<div class="label-with-icon">
									<i class="icon-user"></i>
									<span>执行人</span>
								</div>
								<el-select 
									v-model="logSearch.create_by" 
									placeholder="请选择执行人" 
									clearable
									filterable
									class="select"
									size='large'
									popper-class='select-dropdown-rounded'
								>
									<el-option 
										v-for="user_obj in user_list" 
										:key="user_obj.id"
										:label="user_obj.username" 
										:value="user_obj.id" 
									/>
								</el-select>
							</el-form-item>
						</el-col>
					</el-row>
				</el-form>
			</div>
		</el-card>
		<el-card class="content-card elegant-shadow">
			<div class="content-header">
				<div class="content-title-section">
					<div class="title-with-stats">
						<h3 class="content-title">测试日志列表</h3>
						<div class="stats-info">
							<div class="stat-item">
								<span class="stat-label">总计</span>
								<span class="stat-value">{{ log_list.count || 0 }}</span>
							</div>
							<div class="stat-item">
								<span class="stat-label">当前页</span>
								<span class="stat-value">{{ page_size_params.page }}</span>
							</div>
							<div class="stat-item" v-if="permission.has_delete_permission">
								<span class="stat-label">已选中</span>
								<span class="stat-value">{{ multipleSelection.length }}</span>
							</div>
						</div>
					</div>
				</div>
				<div class="header-action-section" v-if="permission.has_delete_permission">
					<el-button
						type="danger"
						:disabled="multipleSelection.length === 0"
						@click="batchDeleteCaseLogs"
						class="batch-delete-btn"
					>
						<el-icon><Delete /></el-icon>批量删除
					</el-button>
				</div>
			</div>

			<!-- 数据表格 -->
			<div class="table-wrapper">
				<el-table
				:data="log_list.results"
				:max-height="'calc(100vh - 475px)'"
				class="elegant-table"
				:header-row-style="headerRowStyle"
				:show-overflow-tooltip="true"
				@sort-change='handleSortChange'
				@selection-change="handleSelectionChange"
			>
				<el-table-column
					v-if="permission.has_delete_permission"
					type="selection"
					width="55"
					align="center"
				></el-table-column>

					<el-table-column
						label="用例名称"
						prop="case_name"
						align="center"
						min-width="100"
						class-name="case-column"
					>
						<template #default="scope">
							<el-link 
								:href="`/#/test/caseEdit?id=${scope.row.case}`" 
								type="primary" 
								target="_blank"
								class="case-link"
							>
								{{ scope.row.case_name }}
							</el-link>
						</template>
					</el-table-column>
					
					<el-table-column 
						label="关联报告" 
						prop="report_name" 
						min-width="100"  
						align="center"
						class-name="report-column"
					>
						<template #default="scope">
							<el-link 
								v-if="scope.row.report !== null" 
								:href="`/#/test/listView?id=${scope.row.report}`" 
								type="primary" 
								target="_blank"
								class="report-link"
							>
								{{ scope.row.report_name }}
							</el-link>
							<span v-else class="no-report">-</span>
						</template>
					</el-table-column>
					
					<el-table-column 
						label="测试耗时" 
						align="center" 
						width="100"
						class-name="time-column"
					>
						<template #default="scope">
							<div class="time-cell">
								<i class="icon-clock"></i>
								<span>{{ scope.row.time.toFixed(2) }} 秒</span>
							</div>
						</template>
					</el-table-column>
					
					<el-table-column 
						label="执行结果" 
						width="100" 
						align="center"
						class-name="result-column"
					>
						<template #default="scope">
							<el-tag 
								v-if="scope.row.result_value === '成功'" 
								type="success" 
								effect="light"
								class="result-tag success-tag"
							>
								{{ scope.row.result_value }}
							</el-tag>
							<el-tag 
								v-if="scope.row.result_value === '失败'" 
								type="danger" 
								effect="light"
								class="result-tag fail-tag"
							>
								{{ scope.row.result_value }}
							</el-tag>
							<el-tag 
								v-if="scope.row.result_value === '错误'" 
								type="danger" 
								effect="light"
								class="result-tag error-tag"
							>
								{{ scope.row.result_value }}
							</el-tag>
						</template>
					</el-table-column>
					
					<el-table-column 
						label="所属平台" 
						prop="case_plant" 
						width="150"  
						align="center"
						class-name="plant-column"
					/>
					
					<el-table-column 
						label="所属模块" 
						prop="case_module" 
						width="150" 
						align="center"
						class-name="module-column"
					/>
					
					<el-table-column 
						label="执行人" 
						prop="create_by_name" 
						width="120"
						align="center"
						class-name="creator-column"
					/>
					
					<el-table-column 
						label="执行环境" 
						prop="env_name" 
						width="100" 
						align="center"
						class-name="env-column"
					/>
					
					<el-table-column 
						label="测试开始时间" 
						prop="create_time" 
						sortable="custom"   
						width="180" 
						align="center"
						class-name="time-column"
					>
						<template #default="scope">
							<div class="time-cell">
								<i class="icon-time"></i>
								<span>{{ formatTime(scope.row.create_time) }}</span>
							</div>
						</template>
					</el-table-column>
					
					<el-table-column 
						label="测试结束时间" 
						prop="update_time" 
						sortable="custom"   
						width="180" 
						align="center"
						class-name="time-column"
					>
						<template #default="scope">
							<div class="time-cell">
								<i class="icon-time"></i>
								<span>{{ formatTime(scope.row.update_time) }}</span>
							</div>
						</template>
					</el-table-column>
					
					<el-table-column 
						align="center" 
						:width="calcMinWidth" 
						label="操作"
						class-name="action-column"
						fixed="right"
					>
						<template #default="scope">
							<div class="action-buttons">
								<el-tooltip 
									content="查看日志" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type="success" 
										v-if="permission.has_read_permission" 
										class="action-btn view-btn"
										@click.stop="view(scope.row)"
										circle
									>
										<el-icon><View /></el-icon>
									</el-button>
								</el-tooltip>
								
								<el-tooltip 
									content="删除日志" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type="danger" 
										v-if="permission.has_delete_permission" 
										@click.stop="deleteCaseLog(scope.row.id)" 
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
					:total="log_list.count"
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
import { ElMessage, ElMessageBox } from 'element-plus'
import BodyEdit from '../../components/BodyEdit.vue'
import TraceReplay from '../../components/TraceReplay.vue'
import {
	Refresh,
	Search,
	View,
	Delete,
	EditPen,
	Menu
} from '@element-plus/icons-vue'

export default{
	name: 'TestLog',
	computed:{
		...mapState(['pathPermission', 'projectInfo', 'userInfo']),
		calcMinWidth() {
		  let visibleButtons = 0;
		  if (this.permission.has_read_permission) visibleButtons += 1;
		  if (this.permission.has_delete_permission) visibleButtons += 1;
		  return Math.max(10, visibleButtons * 60);
		}
	},
	components: {
		BodyEdit,
		TraceReplay
	},
	data() {
		return {
			lookLogVisible: false,
			permission: {},
			multipleSelection: [],
			test_results: [
				{name: '成功', value: 1},
				{name: '失败', value: 2},
				{name: '错误', value: 3},
			],
			env_list: [],
			user_list: [],
			suite_list: [],
			logSearch:{
				case_name: '',
				result: '',
				create_by: '',
				env: '',
			},
			page_size_params: {
				page: 1,
				size: 10,
			},
			sort_params: {
			  ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
			},
			count: 1,
			isAdd: true,
			editDialogVisible: false,
			log_list: [],
			plant_module_list: [],
			module_list: [],
			ViewVisible: false,
			one_case_log: {},
			role_names: [],
			caseActive: '',
			stepActive: '',
			logActive: '',
			case_index: 0,
			bind_case_data: {}
		}
	},
	methods:{
		...mapActions(['getRolePermission']),
		handleCurrentChange(){
			this.getCaseLogs()
		},
		viewReportDetail(id){
			this.$router.push({name: 'reportViewDetail', query: {id: id}})
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
		  this.getCaseLogs()
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
		
		handleSizeChange(){
			this.page_size_params.page = 1
			this.getCaseLogs()
		},
		search(){
			this.page_size_params.page = 1
			this.getCaseLogs()
		},
		reset(){
			for(let key in this.logSearch){
				this.logSearch[key] = ''
			}
		},
		async deleteCaseLog(id){
			ElMessageBox.confirm(
			    '确定删除此测试日志？删除后数据将无法恢复。',
			    '确认删除',
			    {
			      confirmButtonText: '确认删除',
			      cancelButtonText: '取消',
			      type: 'warning',
			      confirmButtonClass: 'el-button--danger',
			      customClass: 'confirm-dialog'
			    }
			  ).then(async() => {
				  const response = await this.$api.deleteCaseLog(id)
				  if (response.status === 204){
					 this.getCaseLogs()
					  ElMessage({
					    type: 'success',
					    message: '删除成功',
					  })
				  }
				  
			    }).catch(() => {})
		},
		handleSelectionChange(val) {
			this.multipleSelection = val
		},
		async batchDeleteCaseLogs(){
			if (this.multipleSelection.length === 0) {
				ElMessage.warning('请选择要删除的日志')
				return
			}
			ElMessageBox.confirm(
			    `确定删除选中的 ${this.multipleSelection.length} 条测试日志？删除后数据将无法恢复。`,
			    '确认批量删除',
			    {
			      confirmButtonText: '确认删除',
			      cancelButtonText: '取消',
			      type: 'warning',
			      confirmButtonClass: 'el-button--danger',
			      customClass: 'confirm-dialog'
			    }
			  ).then(async() => {
				  const ids = this.multipleSelection.map(item => item.id)
				  try {
					  await Promise.all(ids.map(id => this.$api.deleteCaseLog(id)))
					  this.multipleSelection = []
					  this.getCaseLogs()
					  ElMessage({
					    type: 'success',
					    message: `成功删除 ${ids.length} 条日志`,
					  })
				  } catch (error) {
					  ElMessage.error('部分日志删除失败，请刷新列表查看')
					  this.getCaseLogs()
				  }
			    }).catch(() => {})
		},
		view(row){
			this.lookLogVisible = true
			this.one_case_log = {...row}
		},
		async deleteSuite(id){
			const response = await this.$api.deleteSuite(id)
			if (response.status === 204){
				this.getSuites()
			}
		},
		async getSuite(id){
			const response = await this.$api.getSuite(id)
			if (response.status === 200){
				this.SuiteSave = {...response.data.result}
			}
		},
		async getCaseLogs(){
			this.logSearch.project = this.projectInfo.id
			const response = await this.$api.getCaseLogs(Object.assign(this.logSearch, this.page_size_params, this.sort_params))
			if (response.status === 200){
				this.log_list = {...response.data}
			}
		},
		async getEnvs(params){
			const response = await this.$api.getEnvs({project: this.projectInfo.id})
			if (response.status === 200){
				this.env_list = {...response.data}
			}
		},

		async check_permission(){
			const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission[this.$route.path]}
			const response = await this.$api.check_permission(params)
			if (response.status === 200){
				this.permission = { ...response.data.result }
			}
		},
		async getSuites(params){
			const response = await this.$api.getSuites({project: this.projectInfo.id})
			if (response.status === 200){
				this.suite_list = {...response.data}
			}
		}
	},
	created() {
		this.check_permission()
		this.user_list =  JSON.parse(localStorage.getItem('user_list'))
		this.getCaseLogs()
		this.getEnvs()
		
	}
}
</script>

<style scoped>
	.report{
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

	/* 修改筛选区域的表单样式 */
	.filter-card :deep(.el-card__body) {
		padding: 20px 20px 0 20px;
	}

	.filter-form-wrapper {
		padding: 25px 24px 0px 24px;
	}

	.filter-form {
		margin-bottom: 0;
	}

	.form-item-enhanced {
		margin-bottom: 25px;
		  display: flex;
		  flex-direction: row;
		  align-items: center;
		  height: 40px;
		}
		
	.form-item-enhanced :deep(.el-form-item__content) {
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
		margin-right: 12px;
		font-size: 14px;
		font-weight: 500;
		color: #475569;
		width: 90px;
		flex-shrink: 0;
		white-space: nowrap;
	}

	.icon-case {
		width: 16px;
		height: 16px;
		display: inline-block;
		flex-shrink: 0;
		border-radius: 4px;
		background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
	}

	.icon-result {
		width: 16px;
		height: 16px;
		display: inline-block;
		flex-shrink: 0;
		border-radius: 4px;
		background: linear-gradient(135deg, #10b981 0%, #059669 100%);
	}

	.icon-env,
	.icon-user {
		width: 16px;
		height: 16px;
		display: inline-block;
		flex-shrink: 0;
		border-radius: 4px;
	}

	.icon-env { background: linear-gradient(135deg, #06b6d4 0%, #0e7490 100%); }
	.icon-user { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); }

	/* 调整输入框和选择框样式 */
	.input-elegant,
	.select-elegant {
		flex: 1;
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

	/* 调整 el-form-item 的内部布局 */
	.filter-form >>> .el-form-item__content {
		display: flex;
		align-items: center;
		flex: 1;
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
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.content-title-section {
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex: 1;
	}

	.content-header .header-action-section {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-shrink: 0;
		margin-left: 16px;
	}

	.batch-delete-btn {
		padding: 10px 20px;
		border-radius: 10px;
		background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
		border: none;
		font-weight: 500;
		transition: all 0.3s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.batch-delete-btn:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
	}

	.batch-delete-btn .el-icon {
		margin-right: 8px;
		font-size: 16px;
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

	.case-link {
		font-weight: 500;
	}

	.report-link {
		font-weight: 500;
	}

	.no-report {
		color: #94a3b8;
	}

	.time-cell {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		color: #64748b;
		font-size: 13px;
	}

	.icon-clock {
		width: 14px;
		height: 14px;
		background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
		background-size: contain;
		background-repeat: no-repeat;
	}

	.icon-time {
		width: 14px;
		height: 14px;
		background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
		background-size: contain;
		background-repeat: no-repeat;
	}

	.result-tag {
		font-weight: 500;
	}

	.success-tag {
		background: linear-gradient(135deg, #10b981 0%, #059669 100%);
		color: white;
		border: none;
	}

	.fail-tag,
	.error-tag {
		background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
		color: white;
		border: none;
	}

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

	.action-btn.delete-btn:hover {
		box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
	}

	.action-btn:active {
		transform: translateY(0) scale(0.95);
	}

	.action-btn.view-btn {
		background: linear-gradient(135deg, #10b981 0%, #059669 100%);
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
		float: right;
		background: white;
		z-index: 10;
		position: relative;
		opacity: 1 !important;
		visibility: visible !important;
	}

	.elegant-pagination {
		display: flex;
		justify-content: flex-end;
		visibility: visible !important;
		opacity: 1 !important;
	}

	.elegant-pagination >>> .el-pagination {
		display: flex;
		align-items: center;
	}

	.elegant-pagination >>> .el-pagination__total {
		color: #64748b;
		font-weight: 500;
		margin-right: 20px;
	}

	.elegant-pagination >>> .el-pagination__sizes {
		margin-right: 20px;
	}

	.elegant-pagination >>> .el-pagination__sizes .el-input .el-input__inner {
		border-radius: 8px;
		border: 1px solid #e2e8f0;
		background: white;
		box-shadow: none;
		height: 32px;
		line-height: 32px;
	}

	.elegant-pagination >>> .el-pagination__sizes .el-input .el-input__inner:hover {
		border-color: #cbd5e1;
	}

	.elegant-pagination >>> .el-pager li {
		border-radius: 8px;
		margin: 0 4px;
		border: 1px solid transparent;
		transition: all 0.3s ease;
		font-weight: 500;
		min-width: 36px;
		height: 36px;
		line-height: 36px;
	}

	.elegant-pagination >>> .el-pager li:not(.disabled):hover {
		color: #3b82f6;
		border-color: #3b82f6;
		background: white;
	}

	.elegant-pagination >>> .el-pager li.active {
		background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
		color: white;
		border-color: transparent;
	}

	.elegant-pagination >>> .btn-prev,
	.elegant-pagination >>> .btn-next {
		border-radius: 8px;
		border: 1px solid #e2e8f0;
		background: white;
		transition: all 0.3s ease;
		min-width: 36px;
		height: 36px;
		line-height: 36px;
	}

	.elegant-pagination >>> .btn-prev:hover:not(.disabled),
	.elegant-pagination >>> .btn-next:hover:not(.disabled) {
		border-color: #3b82f6;
		color: #3b82f6;
	}

	.elegant-pagination >>> .el-pagination__jump {
		margin-left: 20px;
	}

	.elegant-pagination >>> .el-pagination__jump .el-input .el-input__inner {
		border-radius: 8px;
		border: 1px solid #e2e8f0;
		box-shadow: none;
		height: 32px;
		line-height: 32px;
	}

	.elegant-pagination >>> .el-pagination__jump .el-input .el-input__inner:hover {
		border-color: #cbd5e1;
	}

	/* 响应式设计 */
	@media screen and (max-width: 1200px) {
		.report {
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
		.report {
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
		
		.form-item-enhanced {
			flex-direction: column;
			align-items: flex-start;
			margin-bottom: 16px;
			min-height: auto;
		}
		
		.label-with-icon {
			margin-right: 0;
			margin-bottom: 8px;
			min-width: auto;
			width: 100%;
		}
		
		.input-elegant,
		.select-elegant {
			width: 100%;
		}
		
		.filter-form >>> .el-form-item__content {
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
	/* ====== 修复测试历史抽屉中的折叠面板标题高度 ====== */
	
	/* 1. 最外层：用例级别的折叠面板标题 */
	.elegant-collapse :deep(.el-collapse-item__header) {
	  /* 固定高度为60px */
	  height: 60px !important;
	  min-height: 60px !important;
	  max-height: 60px !important;
	  line-height: 60px !important;
	  
	  /* 内边距确保内容居中显示 */
	  padding: 0 20px !important;
	  margin-bottom: 8px !important;
	  
	  /* Flex布局确保内容垂直居中 */
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
	
	/* 2. 第二层：步骤级别的折叠面板标题 */
	.elegant-collapse :deep(.step-collapse .el-collapse-item__header) {
	  height: 60px !important;
	  min-height: 60px !important;
	  max-height: 60px !important;
	  line-height: 60px !important;
	  padding: 0 20px !important;
	  
	  display: flex !important;
	  align-items: center !important;
	  box-sizing: border-box !important;
	  
	  background: white !important;
	  border: 1px solid #e4e7ed !important;
	  border-radius: 6px !important;
	  margin-bottom: 6px !important;
	  font-size: 14px !important;
	  font-weight: 500 !important;
	}
	
	/* 3. 第三层：日志详情级别的折叠面板标题 */
	.elegant-collapse :deep(.el-collapse .el-collapse-item__header) {
	  height: 60px !important;
	  min-height: 60px !important;
	  max-height: 60px !important;
	  line-height: 60px !important;
	  padding: 0 20px !important;
	  
	  display: flex !important;
	  align-items: center !important;
	  box-sizing: border-box !important;
	  
	  background: #f9fafb !important;
	  border: 1px solid #e5e7eb !important;
	  border-radius: 4px !important;
	  margin-bottom: 4px !important;
	  font-size: 13px !important;
	}
	
	/* 4. 修复折叠面板内容区域的高度自适应 */
	.elegant-collapse :deep(.el-collapse-item__content) {
	  padding: 16px !important;
	  background: white !important;
	  border: 1px solid #e2e8f0 !important;
	  border-top: none !important;
	  border-radius: 0 0 8px 8px !important;
	}
	
	/* 5. 确保el-text元素正确显示 */
	.elegant-collapse .el-text {
	  line-height: 1.4 !important;
	  font-size: inherit !important;
	  display: inline-flex !important;
	  align-items: center !important;
	  white-space: nowrap !important;
	  overflow: hidden !important;
	  text-overflow: ellipsis !important;
	}
	
	.elegant-collapse .el-text--success {
	  color: #10b981 !important;
	}
	
	.elegant-collapse .el-text--danger {
	  color: #ef4444 !important;
	}
	
	/* 6. 修复el-image在标题中的显示 */
	.elegant-collapse :deep(.el-collapse-item__header .el-image) {
	  margin-left: 12px !important;
	  width: 30px !important;
	  height: 30px !important;
	  border-radius: 4px !important;
	  border: 1px solid #e4e7ed !important;
	  flex-shrink: 0 !important;
	}
	
	/* 7. 激活状态样式保持 */
	.elegant-collapse :deep(.el-collapse-item.is-active .el-collapse-item__header) {
	  border-bottom-left-radius: 0 !important;
	  border-bottom-right-radius: 0 !important;
	  border-bottom: none !important;
	  background: #f1f8ff !important;
	}
	
	/* 8. 确保抽屉容器正确显示 */
	.el-drawer {
	  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
	  -webkit-font-smoothing: antialiased;
	  -moz-osx-font-smoothing: grayscale;
	}
	
	/* 9. 修复抽屉标题样式 */
	.el-drawer :deep(.el-drawer__header) {
	  margin-bottom: 0 !important;
	  padding: 24px 24px 16px 24px !important;
	  border-bottom: 1px solid #f1f5f9 !important;
	}
	
	.el-drawer :deep(.el-drawer__header h4) {
	  margin: 0 !important;
	  font-size: 20px !important;
	  font-weight: 600 !important;
	  color: #1a1a1a !important;
	}
	
	/* 10. 抽屉内容区域滚动优化 */
	.el-drawer :deep(.el-drawer__body) {
	  padding: 0 !important;
	  overflow: hidden !important;
	}
	
	.el-drawer > div {
	  height: 100% !important;
	  padding: 24px !important;
	  overflow-y: auto !important;
	  box-sizing: border-box !important;
	}
</style>