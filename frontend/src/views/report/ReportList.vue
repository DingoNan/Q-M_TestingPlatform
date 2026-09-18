<template>
	<div class="report">
		<!-- 搜索筛选区域 -->
		<el-card class="filter-card elegant-shadow" >
			<div class="filter-header">
				<div class="header-title-section">
					<i class="icon-search"></i>
					<h3 class="filter-title">测试报告筛选</h3>
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
				<el-form :model="reportSearch" class="filter-form inline-form">
					<el-row :gutter="24">
						<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="form-item-enhanced">
								<div class="label-with-icon">
									<i class="icon-report"></i>
									<span>报告名称</span>
								</div>
								<el-input 
									v-model="reportSearch.name" 
									placeholder="请输入报告名称" 
									clearable
									size='large'
									class="input"
								/>
							</el-form-item>
						</el-col>
						
						<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="form-item-enhanced">
								<div class="label-with-icon">
									<i class="icon-suite"></i>
									<span>所属套件</span>
								</div>
								<el-select 
									v-model="reportSearch.suite" 
									placeholder="请选择所属套件" 
									clearable
									filterable
									class="select"
									size='large'
									popper-class='select-dropdown-rounded'
								>
									<el-option 
										v-for="suite_obj in suite_list.results" 
										:key="suite_obj.id"
										:label="suite_obj.name" 
										:value="suite_obj.id" 
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
									v-model="reportSearch.env" 
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
									v-model="reportSearch.create_by" 
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
		
		<!-- 主内容区域 -->
		<el-card class="content-card elegant-shadow">
			<div class="content-header">
				<div class="content-title-section">
					<div class="title-with-stats">
						<h3 class="content-title">测试报告列表</h3>
						<div class="stats-info">
							<div class="stat-item">
								<span class="stat-label">总计</span>
								<span class="stat-value">{{ report_list.count || 0 }}</span>
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
						@click="batchDeleteReports"
						class="batch-delete-btn"
					>
						<el-icon><Delete /></el-icon>批量删除
					</el-button>
				</div>
			</div>

			<!-- 数据表格 -->
			<div class="table-wrapper">
				<el-table
					:max-height="'calc(100vh - 475px)'"
					:data="report_list.results"
					class="elegant-table"
					:show-overflow-tooltip='true'
					:header-row-style="headerRowStyle"
					@selection-change="handleSelectionChange"
				>
					<el-table-column
						v-if="permission.has_delete_permission"
						type="selection"
						width="55"
						align="center"
					></el-table-column>

					<el-table-column
						label="报告名称"
						prop="name"
						min-width="100"
						align="center"
						class-name="name-column"
					>
						<!-- <template #default="scope">
							<el-link :href="`/#/report/listView?id=${scope.row.id}`" type='primary' class="report-link">{{ scope.row.name }}</el-link>
						</template> -->
					</el-table-column>
					
					<el-table-column 
						label="所属套件" 
						prop="suite_name" 
						min-width="100" 
						align="center"
						class-name="suite-column"
					/>
					
					<el-table-column 
						label="执行环境" 
						prop="env_name" 
						width="120"
						align="center"
						class-name="env-column"
					/>
					
					<el-table-column 
						label="用例总数" 
						prop="all_case_number" 
						width="100" 
						align="center"
						class-name="total-column"
					>
						<template #default="scope">
							<div class="total-cell">
								{{ scope.row.all_case_number }}
							</div>
						</template>
					</el-table-column>
					
					<el-table-column 
						label="成功数" 
						prop="success_case_number" 
						width="80" 
						align="center"
						class-name="success-column"
					>
						<template #default="scope">
							<el-tag type="success" effect="light" class="success-tag">
								{{ scope.row.success_case_number }}
							</el-tag>
						</template>
					</el-table-column>
					
					<el-table-column 
						label="成功率" 
						prop="success_percent" 
						width="80" 
						align="center"
						class-name="percent-column"
					>
						<template #default="scope">
							<div class="percent-cell" :class="getPercentClass(scope.row.success_percent)">
								{{ scope.row.success_percent }}%
							</div>
						</template>
					</el-table-column>
					
					<el-table-column 
						label="执行人" 
						prop="create_by_name"  
						width="120"
						align="center"
						class-name="creator-column"
					/>
					
					<el-table-column 
						label="用例开始时间" 
						prop="create_time" 
						sortable 
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
						label="用例结束时间" 
						prop="update_time" 
						sortable 
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
						label="执行进度"  
						width="120" 
						prop="status" 
						align="center"
						class-name="progress-column"
					>
						<template #default="scope">
							<div class="progress-cell">
								<el-tag 
									v-if="isCompleted(scope.row)" 
									type="success" 
									effect="dark"
									class="completed-tag"
								>
									已完成
								</el-tag>
								<el-progress 
									v-else 
									:percentage="getProgress(scope.row)"  
									:stroke-width="10" 
									striped 
									striped-flow
									class="progress-bar"
								/>
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
									content="查看功能报告" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type="success" 
										v-if="permission.has_read_permission" 
										class="action-btn view-btn"
										@click.stop="viewReportDetail(scope.row.id)"
										circle
									>
										<el-icon><View /></el-icon>
									</el-button>
								</el-tooltip>
								
								<el-tooltip 
									content="删除功能报告" 
									placement="top" 
									effect="dark"
								>
									<el-button 
										type="danger" 
										v-if="permission.has_delete_permission" 
										@click.stop="deleteReport(scope.row.id)" 
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
					:total="report_list.count"
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
import {mapState, mapActions} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
	Refresh,
	Search,
	View, 
	Delete, 
	Plus, 
	EditPen
} from '@element-plus/icons-vue'

export default{
	name: 'ReportList',
	computed:{
		...mapState(['pathPermission', 'projectInfo', 'userInfo']),
		calcMinWidth() {
		  let visibleButtons = 0;
		  if (this.permission.has_read_permission) visibleButtons += 1;
		  if (this.permission.has_delete_permission) visibleButtons += 1;
		  return Math.max(10, visibleButtons * 60);
		}
	},
	data() {
		return {
			permission: {},
			multipleSelection: [],
			env_list: [],
			user_list: [],
			suite_list: [],
			reportSearch:{
				name: '',
				create_by: '',
				env: '',
				suite: '',
				project: '',
			},
			page_size_params: {
				page: 1,
				size: 10,
			},
			count: 1,
			isAdd: true,
			editDialogVisible: false,
			report_list: [],
			plant_module_list: [],
			module_list: [],
			ViewVisible: false,
			SuiteSave:{
				project: '',
				name: '',
				conditions: [],
			},
			role_names: [],
		}
	},
	methods:{
		...mapActions(['getRolePermission']),
		
		isCompleted(row) {
			return (row.success_case_number + row.fail_case_number + row.error_case_number) / row.all_case_number === 1
		},
		
		getProgress(row) {
			const total = row.all_case_number || 1
			const completed = row.success_case_number + row.fail_case_number + row.error_case_number
			return Number(((completed / total) * 100).toFixed(2))
		},
		
		getPercentClass(percent) {
			if (percent >= 90) return 'high-percent'
			if (percent >= 70) return 'medium-percent'
			return 'low-percent'
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
		
		handleCurrentChange(){
			this.getReports()
		},
		
		handleSizeChange(){
			this.page_size_params.page = 1
			this.getReports()
		},
		
		search(){
			this.page_size_params.page = 1
			this.getReports()
		},
		
		reset(){
			for(let key in this.reportSearch){
				this.reportSearch[key] = ''
			}
		},
		
		viewReportDetail(id){
			this.$router.push({name: 'reportViewDetail', query: {id: id}})
		},
		
		async deleteReport(id){
			ElMessageBox.confirm(
				'确定删除此测试报告？删除后数据将无法恢复。',
				'确认删除',
				{
					confirmButtonText: '确认删除',
					cancelButtonText: '取消',
					type: 'warning',
					confirmButtonClass: 'el-button--danger',
					customClass: 'confirm-dialog'
				}
			).then(async() => {
				const response = await this.$api.deleteReport(id)
				if (response.status === 204){
					this.getReports()
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
		async batchDeleteReports(){
			if (this.multipleSelection.length === 0) {
				ElMessage.warning('请选择要删除的报告')
				return
			}
			ElMessageBox.confirm(
			    `确定删除选中的 ${this.multipleSelection.length} 条测试报告？删除后数据将无法恢复。`,
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
					await Promise.all(ids.map(id => this.$api.deleteReport(id)))
					this.multipleSelection = []
					this.getReports()
					ElMessage({
					    type: 'success',
					    message: `成功删除 ${ids.length} 条报告`,
					})
				} catch (error) {
					ElMessage.error('部分报告删除失败，请刷新列表查看')
					this.getReports()
				}
			}).catch(() => {})
		},

		async getReports(){
			this.reportSearch.project = this.projectInfo.id
			const response = await this.$api.getReports(Object.assign(this.reportSearch, this.page_size_params))
			if (response.status === 200){
				this.report_list = {...response.data}
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
				localStorage.setItem('reportListPermission', JSON.stringify(this.permission))
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
		this.user_list = JSON.parse(localStorage.getItem('user_list'))
		this.getReports()
		this.getEnvs()
		this.getSuites()
	}
}
</script>

<style scoped>
.report{
	width: 100%;
	background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
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

.inline-form {
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
	color: var(--qm-text-2);
	width: 90px;
	flex-shrink: 0;
	white-space: nowrap;
}

.icon-report {
	width: 16px;
	height: 16px;
	display: inline-block;
	flex-shrink: 0;
	border-radius: 4px;
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.icon-suite,
.icon-env,
.icon-user {
	width: 16px;
	height: 16px;
	display: inline-block;
	flex-shrink: 0;
	border-radius: 4px;
}

.icon-suite { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-env { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-user { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }

/* 调整输入框和选择框样式 */
.input-elegant,
.select-elegant {
	flex: 1;
}

.input-elegant >>> .el-input__inner,
.select-elegant >>> .el-input__inner {
	border-radius: 10px;
	border: 1px solid var(--qm-line-strong);
	background: var(--qm-bg-1);
	padding: 0 15px;
	box-shadow: none;
	transition: all 0.3s ease;
	height: 40px;
	line-height: 40px;
}

.input-elegant >>> .el-input__inner:hover,
.select-elegant >>> .el-input__inner:hover {
	border-color: var(--qm-line-strong);
	background: var(--qm-bg-2);
}

.input-elegant >>> .el-input__inner:focus,
.select-elegant >>> .el-input__inner:focus {
	border-color: #f59e0b;
	box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
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
	background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
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

.elegant-table >>> .el-table__header-wrapper th {
	background: linear-gradient(180deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
	font-weight: 600;
	color: var(--qm-text-1);
	border-bottom: 1px solid var(--qm-line-strong);
	padding: 16px 0;
}

.elegant-table >>> .el-table__header-wrapper .cell {
	padding: 0 16px;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row {
	transition: all 0.3s ease;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row:nth-child(even) {
	background: var(--qm-bg-1);
}

.elegant-table >>> .el-table__body-wrapper .el-table__row:hover {
	background: var(--qm-warning-soft);
	transform: translateX(4px);
}

.elegant-table >>> .el-table__body-wrapper .el-table__row.active-row {
	background: var(--qm-warning-soft);
	position: relative;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row.active-row::before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	width: 4px;
	background: linear-gradient(180deg, #f59e0b 0%, #d97706 100%);
}

.elegant-table >>> .el-table__body-wrapper td {
	border-bottom: 1px solid var(--qm-bg-3);
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
	background: linear-gradient(135deg, var(--qm-bg-3) 0%, var(--qm-line-strong) 100%);
	border-radius: 8px;
	font-weight: 600;
	color: var(--qm-text-2);
	margin: 0 auto;
}

.total-cell {
	display: flex;
	align-items: center;
	justify-content: center;
	font-weight: 600;
	color: var(--qm-text-1);
}

.success-tag {
	font-weight: 500;
	background: linear-gradient(135deg, #10b981 0%, #059669 100%);
	color: white;
	border: none;
}

.percent-cell {
	display: flex;
	align-items: center;
	justify-content: center;
	font-weight: 600;
	border-radius: 6px;
	padding: 2px 8px;
}

.high-percent {
	color: #10b981;
	background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
}

.medium-percent {
	color: #f59e0b;
	background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
}

.low-percent {
	color: #ef4444;
	background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
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

.progress-cell {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 100%;
}

.completed-tag {
	font-weight: 500;
	background: linear-gradient(135deg, #10b981 0%, #059669 100%);
	color: white;
	border: none;
}

.progress-bar >>> .el-progress-bar__inner {
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.progress-bar >>> .el-progress-bar__outer {
	background-color: var(--qm-line-strong);
	border-radius: 10px;
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
	background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
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
	border-top: 1px solid var(--qm-bg-3);
	flex-shrink: 0;
	display: block !important;
	min-height: 40px;
	float: right;
	background: var(--qm-bg-2);
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
	color: var(--qm-text-2);
	font-weight: 500;
	margin-right: 20px;
}

.elegant-pagination >>> .el-pagination__sizes {
	margin-right: 20px;
}

.elegant-pagination >>> .el-pagination__sizes .el-input .el-input__inner {
	border-radius: 8px;
	border: 1px solid var(--qm-line-strong);
	background: var(--qm-bg-2);
	box-shadow: none;
	height: 32px;
	line-height: 32px;
}

.elegant-pagination >>> .el-pagination__sizes .el-input .el-input__inner:hover {
	border-color: var(--qm-line-strong);
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
	color: #f59e0b;
	border-color: #f59e0b;
	background: var(--qm-bg-2);
}

.elegant-pagination >>> .el-pager li.active {
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
	color: white;
	border-color: transparent;
}

.elegant-pagination >>> .btn-prev,
.elegant-pagination >>> .btn-next {
	border-radius: 8px;
	border: 1px solid var(--qm-line-strong);
	background: var(--qm-bg-2);
	transition: all 0.3s ease;
	min-width: 36px;
	height: 36px;
	line-height: 36px;
}

.elegant-pagination >>> .btn-prev:hover:not(.disabled),
.elegant-pagination >>> .btn-next:hover:not(.disabled) {
	border-color: #f59e0b;
	color: #f59e0b;
}

.elegant-pagination >>> .el-pagination__jump {
	margin-left: 20px;
}

.elegant-pagination >>> .el-pagination__jump .el-input .el-input__inner {
	border-radius: 8px;
	border: 1px solid var(--qm-line-strong);
	box-shadow: none;
	height: 32px;
	line-height: 32px;
}

.elegant-pagination >>> .el-pagination__jump .el-input .el-input__inner:hover {
	border-color: var(--qm-line-strong);
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
</style>