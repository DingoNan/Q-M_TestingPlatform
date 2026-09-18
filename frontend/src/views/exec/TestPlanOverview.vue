<template>
	<div class="overview-page-container">
		<div class="page-header">
			<div class="header-info">
				<i class="icon-report-header"></i>
				<h2 class="page-title">测试计划概览 - {{ overviewPlan.name || '-' }}</h2>
				<span v-if="overviewPlan.status_name" class="status-badge">{{ overviewPlan.status_name }}</span>
			</div>
			<el-button @click="goBack" class="back-btn">
				<el-icon><ArrowLeft /></el-icon>返回
			</el-button>
		</div>

		<div v-loading="loading" class="overview-content">
			<div class="overview-top">
				<div class="overview-left">
					<div class="section-title">基础信息</div>
					<div class="info-grid">
						<div class="info-item">
							<span class="info-label">计划名称</span>
							<span class="info-value">{{ overviewPlan.name || '-' }}</span>
						</div>
						<div class="info-item">
							<span class="info-label">所属项目</span>
							<span class="info-value">{{ overviewPlan.project_name || '-' }}</span>
						</div>
						<div class="info-item">
							<span class="info-label">计划描述</span>
							<span class="info-value">{{ overviewPlan.desc || '-' }}</span>
						</div>
						<div class="info-item">
							<span class="info-label">执行时间</span>
							<span class="info-value">{{ overviewPlan.start_end_time || '-' }}</span>
						</div>
						<div class="info-item">
							<span class="info-label">创建人</span>
							<span class="info-value">{{ overviewPlan.create_by_name || '-' }}</span>
						</div>
						<div class="info-item">
							<span class="info-label">创建时间</span>
							<span class="info-value">{{ overviewPlan.create_time || '-' }}</span>
						</div>
					</div>
				</div>
				<div class="overview-right">
					<div class="section-title">执行概览</div>
					<div class="icons-container">
						<div class="rate-card">
							<div class="rate-circle">
								<div class="rate-value">{{ calculateExecutionRate() }}%</div>
								<div class="rate-label">执行率</div>
							</div>
						</div>
						<div class="rate-card">
							<div class="rate-circle">
								<div class="rate-value">{{ calculatePassRate() }}%</div>
								<div class="rate-label">总通过率</div>
							</div>
						</div>
						<div class="rate-card">
							<div class="rate-circle">
								<div class="rate-value">{{ calculateExecutionPassRate() }}%</div>
								<div class="rate-label">执行通过率</div>
							</div>
						</div>
					</div>
					<div class="status-mini-cards">
						<div class="mini-card total">
							<span class="mini-label">总计</span>
							<span class="mini-value">{{ overviewPlan.total_count || 0 }}</span>
						</div>
						<div class="mini-card passed">
							<span class="mini-label">已通过</span>
							<span class="mini-value">{{ overviewPlan.passed_count || 0 }}</span>
						</div>
						<div class="mini-card failed">
							<span class="mini-label">未通过</span>
							<span class="mini-value">{{ overviewPlan.failed_count || 0 }}</span>
						</div>
						<div class="mini-card in-progress">
							<span class="mini-label">进行中</span>
							<span class="mini-value">{{ overviewPlan.in_progress_count || 0 }}</span>
						</div>
						<div class="mini-card blocked">
							<span class="mini-label">暂缓</span>
							<span class="mini-value">{{ overviewPlan.blocked_count || 0 }}</span>
						</div>
						<div class="mini-card not-executed">
							<span class="mini-label">未执行</span>
							<span class="mini-value">{{ overviewPlan.not_executed_count || 0 }}</span>
						</div>
					</div>
				</div>
			</div>

			<div class="overview-bottom">
				<div class="section-title">执行人统计</div>
				<div class="executor-cards">
					<div class="executor-card" v-for="(item, index) in executorStats" :key="index">
						<div class="executor-header">
							<div class="executor-avatar">{{ item.executor_name === '未分配' ? '?' : item.executor_name.charAt(0) }}</div>
							<div class="executor-info">
								<div class="executor-name">{{ item.executor_name }}</div>
								<div class="executor-status" :class="getExecutorStatusClass(item)">{{ getExecutorStatus(item) }}</div>
							</div>
						</div>
						<div class="executor-stats">
							<div class="executor-stat-item">
								<span class="stat-label">分配</span>
								<span class="stat-value total">{{ item.total }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">通过</span>
								<span class="stat-value passed">{{ item.passed }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">失败</span>
								<span class="stat-value failed">{{ item.failed }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">进行中</span>
								<span class="stat-value in-progress">{{ item.in_progress }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">暂缓</span>
								<span class="stat-value blocked">{{ item.blocked }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">未执行</span>
								<span class="stat-value idle">{{ item.not_executed }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">缺陷</span>
								<span class="stat-value defect">{{ item.defect_count }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">通过率</span>
								<span class="stat-value" :class="(item.total > 0 ? Math.round((item.passed / item.total) * 100) : 0) > 60 ? 'passed' : 'failed'">{{ item.total > 0 ? Math.round((item.passed / item.total) * 100) : 0 }}%</span>
							</div>
						</div>
					</div>
				</div>
			</div>

			<div class="overview-bottom">
				<div class="section-title">标签统计</div>
				<div class="executor-cards">
					<div class="executor-card" v-for="(item, index) in tagStats" :key="index">
						<div class="executor-header">
							<div class="executor-avatar tag-avatar">
								{{ item.name.charAt(0) }}
							</div>
							<div class="executor-info">
								<div class="executor-name">{{ item.name }}</div>
								<div class="executor-status" :class="getTagStatusClass(item)">
									{{ getTagStatus(item) }}
								</div>
							</div>
						</div>
						<div class="executor-stats">
							<div class="executor-stat-item">
								<span class="stat-label">总数</span>
								<span class="stat-value total">{{ item.all_case_number }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">通过</span>
								<span class="stat-value passed">{{ item.success_number }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">失败</span>
								<span class="stat-value failed">{{ item.fail_number }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">进行中</span>
								<span class="stat-value in-progress">{{ item.error_number }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">未执行</span>
								<span class="stat-value idle">{{ item.not_executed_number }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">暂缓</span>
								<span class="stat-value blocked">{{ item.postponed_number }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">缺陷</span>
								<span class="stat-value defect">{{ item.defect_count }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">通过率</span>
								<span class="stat-value" :class="(item.all_case_number > 0 ? Math.round((item.success_number / item.all_case_number) * 100) : 0) > 60 ? 'passed' : 'failed'">{{ item.all_case_number > 0 ? Math.round((item.success_number / item.all_case_number) * 100) : 0 }}%</span>
							</div>
						</div>
					</div>
					<div v-if="tagStats.length === 0" class="empty-tip">暂无标签统计数据</div>
				</div>
			</div>

			<div class="overview-bottom">
				<div class="section-title">模块统计</div>
				<div class="module-filter-bar">
					<el-input 
						v-model="moduleSearchKeyword" 
						placeholder="搜索模块名称" 
						clearable 
						prefix-icon="Search"
						class="input"
						style="width: 300px;"
						@input="onModuleSearchChange"
					/>
				</div>
				<div class="module-cards">
					<div class="executor-card" v-for="(item, index) in displayModuleStats" :key="index">
						<div class="executor-header">
							<div class="executor-avatar module-avatar">
								{{ item.module_name.charAt(0) }}
							</div>
							<div class="executor-info">
								<div class="executor-name">{{ item.plant_name }}_{{ item.module_name }}</div>
								<div class="executor-status" :class="getModuleStatusClass(item)">
									{{ getModuleStatus(item) }}
								</div>
							</div>
						</div>
						<div class="executor-stats">
							<div class="executor-stat-item">
								<span class="stat-label">总数</span>
								<span class="stat-value total">{{ item.all_case_number }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">通过</span>
								<span class="stat-value passed">{{ item.success_number }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">失败</span>
								<span class="stat-value failed">{{ item.fail_number }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">进行中</span>
								<span class="stat-value in-progress">{{ item.error_number }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">未执行</span>
								<span class="stat-value idle">{{ item.not_executed_number }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">暂缓</span>
								<span class="stat-value blocked">{{ item.postponed_number }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">缺陷</span>
								<span class="stat-value defect">{{ item.defect_count }}</span>
							</div>
							<div class="executor-stat-item">
								<span class="stat-label">通过率</span>
								<span class="stat-value" :class="(item.all_case_number > 0 ? Math.round((item.success_number / item.all_case_number) * 100) : 0) > 60 ? 'passed' : 'failed'">{{ item.all_case_number > 0 ? Math.round((item.success_number / item.all_case_number) * 100) : 0 }}%</span>
							</div>
						</div>
					</div>
					<div v-if="filteredModuleStats.length === 0" class="empty-tip">暂无模块统计数据</div>
				</div>
				<div v-if="filteredModuleStats.length > 9" class="view-more-container">
					<el-button 
						@click="toggleModuleExpand" 
						type="primary" 
						plain
						class="view-more-btn"
					>
						{{ moduleExpanded ? '收起' : '查看更多' }}
						<el-icon :class="{ 'rotate-icon': moduleExpanded }"><ArrowDown /></el-icon>
					</el-button>
				</div>
			</div>

			<div class="overview-bottom">
				<div class="section-title">缺陷统计</div>
				<el-table
					:data="pagedDefectList"
					style="width: 100%"
					:max-height="'400px'"
					class="elegant-table"
					:show-overflow-tooltip="true"
					:default-sort="{ prop: 'create_time', order: 'descending' }"
					@sort-change="handleDefectSortChange"
				>
					<el-table-column type="index" label="序号" width="70" align="center" :index="defectIndexMethod" />
					<el-table-column label="标题" prop="title" min-width="200" align="center">
						<template #default="scope">
							<el-link type="primary" @click="goToDefectDetail(scope.row)">{{ scope.row.title }}</el-link>
						</template>
					</el-table-column>

					<el-table-column label="严重程度" prop="severity" width="130" align="center" sortable="custom">
						<template #default="scope">
							<el-dropdown trigger="click" @command="(val) => updateDefectField(scope.row, 'severity', val)" class="status-dropdown" popper-class="status-dropdown-popper">
								<span class="status-badge" :class="'severity-' + scope.row.severity">
									<span class="status-dot"></span>
									<span class="status-label">{{ scope.row.severity_name || '-' }}</span>
									<el-icon class="status-arrow"><ArrowDown /></el-icon>
								</span>
								<template #dropdown>
									<el-dropdown-menu>
										<el-dropdown-item v-for="item in severityOptions" :key="item.value" :command="item.value" class="status-dropdown-item">
											<span class="status-indicator" :class="getIndicatorClass('severity', item.value)"></span>
											<span class="status-text">{{ item.label }}</span>
										</el-dropdown-item>
									</el-dropdown-menu>
								</template>
							</el-dropdown>
						</template>
					</el-table-column>

					<el-table-column label="优先级" prop="priority" width="120" align="center" sortable="custom">
						<template #default="scope">
							<el-dropdown trigger="click" @command="(val) => updateDefectField(scope.row, 'priority', val)" class="status-dropdown" popper-class="status-dropdown-popper">
								<span class="status-badge" :class="'priority-' + scope.row.priority">
									<span class="status-dot"></span>
									<span class="status-label">{{ scope.row.priority_name || '-' }}</span>
									<el-icon class="status-arrow"><ArrowDown /></el-icon>
								</span>
								<template #dropdown>
									<el-dropdown-menu>
										<el-dropdown-item v-for="item in priorityOptions" :key="item.value" :command="item.value" class="status-dropdown-item">
											<span class="status-indicator" :class="getIndicatorClass('priority', item.value)"></span>
											<span class="status-text">{{ item.label }}</span>
										</el-dropdown-item>
									</el-dropdown-menu>
								</template>
							</el-dropdown>
						</template>
					</el-table-column>

					<el-table-column label="BUG类型" prop="defect_type" width="150" align="center" sortable="custom">
						<template #default="scope">
							<el-dropdown trigger="click" @command="(val) => updateDefectField(scope.row, 'defect_type', val)" class="status-dropdown" popper-class="status-dropdown-popper">
								<span class="status-badge" :class="'defect-type-' + scope.row.defect_type">
									<span class="status-dot"></span>
									<span class="status-label">{{ scope.row.defect_type_name || '-' }}</span>
									<el-icon class="status-arrow"><ArrowDown /></el-icon>
								</span>
								<template #dropdown>
									<el-dropdown-menu>
										<el-dropdown-item v-for="item in defectTypeOptions" :key="item.value" :command="item.value" class="status-dropdown-item">
											<span class="status-indicator" :class="getIndicatorClass('defect_type', item.value)"></span>
											<span class="status-text">{{ item.label }}</span>
										</el-dropdown-item>
									</el-dropdown-menu>
								</template>
							</el-dropdown>
						</template>
					</el-table-column>

					<el-table-column label="状态" prop="status" width="120" align="center" sortable="custom">
						<template #default="scope">
							<el-dropdown trigger="click" @command="(val) => updateDefectField(scope.row, 'status', val)" class="status-dropdown" popper-class="status-dropdown-popper">
								<span class="status-badge" :class="'defect-status-' + scope.row.status">
									<span class="status-dot"></span>
									<span class="status-label">{{ scope.row.status_name || '-' }}</span>
									<el-icon class="status-arrow"><ArrowDown /></el-icon>
								</span>
								<template #dropdown>
									<el-dropdown-menu>
										<el-dropdown-item v-for="item in statusOptions" :key="item.value" :command="item.value" class="status-dropdown-item">
											<span class="status-indicator" :class="getIndicatorClass('status', item.value)"></span>
											<span class="status-text">{{ item.label }}</span>
										</el-dropdown-item>
									</el-dropdown-menu>
								</template>
							</el-dropdown>
						</template>
					</el-table-column>

					<el-table-column label="负责人" prop="owner_name" width="180" align="center" sortable="custom">
					<template #default="scope">
						<el-dropdown trigger="click" @command="(val) => updateDefectField(scope.row, 'owner', val)" class="status-dropdown" popper-class="assignee-dropdown-popper">
							<span class="status-badge" :class="getAssigneeClass(scope.row.owner)">
								<span class="status-dot"></span>
								<span class="status-label">{{ scope.row.owner_name || '未分配' }}</span>
								<el-icon class="status-arrow"><ArrowDown /></el-icon>
							</span>
							<template #dropdown>
								<el-dropdown-menu>
									<el-dropdown-item v-for="user_obj in userList" :key="user_obj.id" :command="user_obj.id" class="status-dropdown-item">
										<span class="status-indicator" :class="getIndicatorClassByUserId(user_obj.id)"></span>
										<span class="status-text">{{ user_obj.username }}</span>
									</el-dropdown-item>
								</el-dropdown-menu>
							</template>
						</el-dropdown>
					</template>
				</el-table-column>

				<el-table-column label="处理人" prop="assignee_name" width="180" align="center" sortable="custom">
						<template #default="scope">
							<el-dropdown trigger="click" @command="(val) => updateDefectField(scope.row, 'assignee', val)" class="status-dropdown" popper-class="assignee-dropdown-popper">
								<span class="status-badge" :class="getAssigneeClass(scope.row.assignee)">
									<span class="status-dot"></span>
									<span class="status-label">{{ scope.row.assignee_name || '未分配' }}</span>
									<el-icon class="status-arrow"><ArrowDown /></el-icon>
								</span>
								<template #dropdown>
									<el-dropdown-menu>
										<el-dropdown-item v-for="user_obj in userList" :key="user_obj.id" :command="user_obj.id" class="status-dropdown-item">
											<span class="status-indicator" :class="getIndicatorClassByUserId(user_obj.id)"></span>
											<span class="status-text">{{ user_obj.username }}</span>
										</el-dropdown-item>
									</el-dropdown-menu>
								</template>
							</el-dropdown>
						</template>
					</el-table-column>

					<el-table-column label="创建信息" width="200" align="center" sortable="custom" prop="create_time" class-name="creator-column">
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

					<el-table-column label="更新信息" width="200" align="center" sortable="custom" prop="update_time" class-name="updater-column">
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
				</el-table>
				<div class="pagination-wrapper">
					<el-pagination
						v-model:current-page="defectCurrentPage"
						v-model:page-size="defectPageSize"
						:page-sizes="[10, 20, 30, 50]"
						layout="total, sizes, prev, pager, next, jumper"
						:total="defectList.length"
						@size-change="handleDefectSizeChange"
						@current-change="handleDefectPageChange"
						class="select input"
						:background="true"
					/>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { mapState } from 'vuex'
import { ArrowLeft, ArrowDown, View, EditPen, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
	name: 'TestPlanOverview',
	components: {
		ArrowLeft,
		ArrowDown,
		View,
		EditPen,
		Delete
	},
	computed: {
		...mapState(['userInfo', 'pathPermission', 'projectInfo']),
		displayModuleStats() {
			if (this.moduleExpanded) {
				return this.filteredModuleStats;
			}
			return this.filteredModuleStats.slice(0, 9);
		},
		pagedDefectList() {
			const { prop, order } = this.defectSort
			let list = this.defectList
			if (prop && order) {
				list = [...this.defectList].sort((a, b) => {
					let cmp = 0
					if (prop === 'owner_name' || prop === 'assignee_name') {
					cmp = (a[prop] || '').localeCompare(b[prop] || '')
				} else if (prop === 'create_time' || prop === 'update_time') {
						cmp = new Date(a[prop]) - new Date(b[prop])
					} else {
						cmp = (a[prop] ?? 0) - (b[prop] ?? 0)
					}
					return order === 'ascending' ? cmp : -cmp
				})
			}
			const start = (this.defectCurrentPage - 1) * this.defectPageSize;
			return list.slice(start, start + this.defectPageSize);
		}
	},
	data() {
		return {
			loading: false,
			permission: {},
			overviewPlan: {},
			executorStats: [],
			moduleStats: [],
			tagStats: [],
			filteredModuleStats: [],
			moduleSearchKeyword: '',
			moduleExpanded: false,
			defectList: [],
			defectCurrentPage: 1,
			defectPageSize: 10,
			// 缺陷列表前端排序状态（数据为全量加载，前端排序+分页）
			defectSort: { prop: 'create_time', order: 'descending' },
			userList: [],
			severityOptions: [
				{value: 1, label: '致命'},
				{value: 2, label: '严重'},
				{value: 3, label: '一般'},
				{value: 4, label: '轻微'},
			],
			priorityOptions: [
				{value: 1, label: '紧急'},
				{value: 2, label: '高'},
				{value: 3, label: '中'},
				{value: 4, label: '低'},
			],
			defectTypeOptions: [
				{value: 1, label: '代码问题-前端'},
				{value: 2, label: '代码问题-后端'},
				{value: 3, label: '设计如此'},
				{value: 4, label: '重复BUG'},
				{value: 5, label: '需求变动'},
				{value: 6, label: 'UI样式'},
				{value: 7, label: '设计缺陷'},
			],
			statusOptions: [
				{value: 1, label: '待处理'},
				{value: 2, label: '处理中'},
				{value: 3, label: '已解决'},
				{value: 4, label: '已关闭'},
			]
		}
	},
	methods: {
		goBack() {
			this.$router.back()
		},
		async check_permission(){
			const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission['/exec/plan']}
			const response = await this.$api.check_permission(params)
			if (response.status === 200){
				this.permission = { ...response.data.result }
			}
		},
		getExecutorStatus(item) {
			if (!item.total || item.total === 0) return '未开始'
			if (item.total === item.not_executed) return '未开始'
			if (item.total === (item.passed + item.failed + item.blocked)) return '已完成'
			return '进行中'
		},
		getExecutorStatusClass(item) {
			const status = this.getExecutorStatus(item)
			switch(status) {
				case '未开始': return 'status-idle'
				case '进行中': return 'status-processing'
				case '已完成': return 'status-completed'
				default: return ''
			}
		},
		getTagStatus(item) {
			if (!item.all_case_number || item.all_case_number === 0) return '未开始'
			if (item.not_executed_number === item.all_case_number) return '未开始'
			if ((item.success_number + item.fail_number) === item.all_case_number) return '已完成'
			return '进行中'
		},
		getTagStatusClass(item) {
			const status = this.getTagStatus(item)
			switch(status) {
				case '未开始': return 'status-idle'
				case '进行中': return 'status-processing'
				case '已完成': return 'status-completed'
				default: return ''
			}
		},
		getModuleStatus(item) {
			if (!item.all_case_number || item.all_case_number === 0) return '未开始'
			if (item.not_executed_number === item.all_case_number) return '未开始'
			if ((item.success_number + item.fail_number) === item.all_case_number) return '已完成'
			return '进行中'
		},
		getModuleStatusClass(item) {
			const status = this.getModuleStatus(item)
			switch(status) {
				case '未开始': return 'status-idle'
				case '进行中': return 'status-processing'
				case '已完成': return 'status-completed'
				default: return ''
			}
		},
		onModuleSearchChange() {
			this.moduleExpanded = false;
			if (!this.moduleSearchKeyword) {
				this.filteredModuleStats = [...this.moduleStats]
			} else {
				const keyword = this.moduleSearchKeyword.toLowerCase()
				this.filteredModuleStats = this.moduleStats.filter(item => 
					item.module_name.toLowerCase().includes(keyword) || 
					item.plant_name.toLowerCase().includes(keyword)
				)
			}
		},
		toggleModuleExpand() {
			this.moduleExpanded = !this.moduleExpanded;
		},
		handleDefectPageChange(page) {
			this.defectCurrentPage = page;
		},
		handleDefectSizeChange(size) {
			this.defectPageSize = size;
			this.defectCurrentPage = 1;
		},
		handleDefectSortChange({ column, prop, order }) {
			// 前端排序：更新排序状态，由 pagedDefectList 计算属性统一排序+分页
			this.defectSort = { prop: prop || '', order: order || '' }
			this.defectCurrentPage = 1
		},
		goToDefectDetail(row) {
			const routeData = this.$router.resolve({ path: '/defect/list', query: { action: 'view', id: row.id } });
			window.open(routeData.href, '_blank');
		},
		defectIndexMethod(index) {
			return (this.defectCurrentPage - 1) * this.defectPageSize + index + 1;
		},
		async updateDefectField(row, field, value) {
			const response = await this.$api.patchDefect(row.id, {[field]: value})
			if (response.status === 200) {
				ElMessage.success('修改成功')
				await this.loadPlanOverview()
			}
		},
		async deleteDefect(id) {
			ElMessageBox.confirm('确定删除此缺陷？删除后数据将无法恢复。', '确认删除', {
				confirmButtonText: '确认删除',
				cancelButtonText: '取消',
				type: 'warning',
			}).then(async () => {
				const response = await this.$api.deleteDefect(id)
				if (response.status === 204) {
					ElMessage.success('删除成功')
					await this.loadPlanOverview()
				}
			}).catch(() => {})
		},
		getIndicatorClass(field, value) {
			const maps = {
				severity: {1: 'danger', 2: 'warning', 3: 'primary', 4: 'info'},
				priority: {1: 'danger', 2: 'warning', 3: 'primary', 4: 'info'},
				defect_type: {1: 'purple', 2: 'cyan', 3: 'info', 4: 'warning', 5: 'primary', 6: 'pink', 7: 'success'},
				status: {1: 'info', 2: 'warning', 3: 'success', 4: 'primary'},
			}
			return (maps[field] && maps[field][value]) || 'info'
		},
		getAssigneeClass(userId) {
			if (!userId) return 'assignee-none'
			const palette = ['assignee-1', 'assignee-2', 'assignee-3', 'assignee-4', 'assignee-5', 'assignee-6', 'assignee-7', 'assignee-8']
			const idx = (Number(userId) % palette.length + palette.length) % palette.length
			return palette[idx]
		},
		getIndicatorClassByUserId(userId) {
			if (!userId) return 'info'
			const palette = ['primary', 'purple', 'danger', 'success', 'cyan', 'warning', 'info', 'orange']
			const idx = (Number(userId) % palette.length + palette.length) % palette.length
			return palette[idx]
		},
		formatTime(time) {
			if (!time) return '-'
			return new Date(time).toLocaleString('zh-CN', {
				year: 'numeric', month: '2-digit', day: '2-digit',
				hour: '2-digit', minute: '2-digit',
			}).replace(/\//g, '-')
		},
		calculatePassRate() {
			if (this.overviewPlan.pass_rate !== undefined && this.overviewPlan.pass_rate !== null) {
				return this.overviewPlan.pass_rate
			}
			if (!this.overviewPlan.total_count || this.overviewPlan.total_count === 0) return 0
			return Math.round((this.overviewPlan.passed_count || 0) / this.overviewPlan.total_count * 100)
		},
		calculateExecutionRate() {
			if (!this.overviewPlan.total_count || this.overviewPlan.total_count === 0) return 0
			const executed = this.overviewPlan.total_count - (this.overviewPlan.not_executed_count || 0)
			return Math.round(executed / this.overviewPlan.total_count * 100)
		},
		calculateExecutionPassRate() {
			const executed = this.overviewPlan.total_count - (this.overviewPlan.not_executed_count || 0)
			if (!executed || executed === 0) return 0
			return Math.round((this.overviewPlan.passed_count || 0) / executed * 100)
		},
		async loadPlanOverview() {
			const planId = this.$route.params.id
			if (!planId) return
			
			this.loading = true
			try {
				const response = await this.$api.getPlanOverview(planId)
				if (response.status === 200) {
					const data = response.data.result
					const basicInfo = { ...data.basic_info }
					if (Array.isArray(basicInfo.start_end_time) && basicInfo.start_end_time.length === 2) {
						const start = basicInfo.start_end_time[0].split('T')[0]
						const end = basicInfo.start_end_time[1].split('T')[0]
						basicInfo.start_end_time = `${start} ~ ${end}`
					}
					this.overviewPlan = {
						name: basicInfo.name || '',
						project_name: basicInfo.project_name || '',
						desc: basicInfo.desc || '',
						start_end_time: basicInfo.start_end_time || '',
						create_by_name: basicInfo.create_by_name || '',
						create_time: basicInfo.create_time || '',
						status: basicInfo.status || '',
						status_name: basicInfo.status_name || '',
						passed_count: data.status_info.passed_count || 0,
						failed_count: data.status_info.failed_count || 0,
						in_progress_count: data.status_info.in_progress_count || 0,
						blocked_count: data.status_info.postponed_count || 0,
						not_executed_count: data.status_info.not_executed_count || 0,
						total_count: data.status_info.total_count || 0,
						pass_rate: data.status_info.pass_rate || 0
					}
					this.executorStats = data.executor_stats.map(item => ({
						executor_name: item.executed_by_name || '未分配',
						total: item.assigned_count || 0,
						passed: item.passed || 0,
						failed: item.failed || 0,
						in_progress: item.in_progress || 0,
						blocked: item.postponed || 0,
						not_executed: item.not_executed || 0,
						defect_count: item.defect_count || 0
					}))
					this.moduleStats = data.module_stats || []
					this.tagStats = data.tag_stats || []
					this.filteredModuleStats = [...this.moduleStats]
					this.defectList = data.defect_list || []
					this.defectCurrentPage = 1
				}
			} catch (error) {
				console.error('加载计划概览失败:', error)
			} finally {
				this.loading = false
			}
		}
	},
	created() {
		this.check_permission()
		this.loadPlanOverview()
		this.userList = JSON.parse(localStorage.getItem('user_list') || '[]')
	}
}
</script>

<style scoped>
.overview-page-container {
	width: 100%;
	background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
	padding: 20px 5px;
	box-sizing: border-box;
	min-height: calc(100vh - 75px);
}

.page-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 20px;
	margin-bottom: 24px;
	padding: 20px 24px;
	background: var(--qm-bg-2);
	border-radius: 16px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
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
}

.back-btn:hover {
	background: var(--qm-bg-1);
	border-color: var(--qm-line-strong);
	transform: translateY(-1px);
}

.header-info {
	display: flex;
	align-items: center;
	gap: 12px;
	flex: 1;
}

.page-title {
	margin: 0;
	font-size: 20px;
	font-weight: 700;
	color: var(--qm-text-1);
}

.icon-report-header {
	display: inline-block;
	width: 32px;
	height: 32px;
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
	border-radius: 10px;
	position: relative;
	flex-shrink: 0;
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

.status-badge {
	font-size: 12px;
	padding: 2px 8px;
	border-radius: 10px;
	font-weight: 500;
	background: rgba(16, 185, 129, 0.1);
	color: #10b981;
	white-space: nowrap;
}

.overview-content {
	padding: 0;
}

.overview-top {
	display: flex;
	gap: 24px;
	margin-bottom: 24px;
}

.overview-left {
	flex: 1;
	background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-2) 100%);
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
	background: linear-gradient(135deg, #f0f9ff 0%, var(--qm-bg-2) 100%);
	border-radius: 20px;
	padding: 28px;
	box-shadow: 0 4px 20px rgba(245, 158, 11, 0.1), 0 1px 3px rgba(0, 0, 0, 0.05);
	border: 1px solid rgba(245, 158, 11, 0.15);
	transition: all 0.3s ease;
}

.overview-right:hover {
	box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15), 0 2px 8px rgba(0, 0, 0, 0.08);
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
	display: flex;
	justify-content: center;
	margin-bottom: 20px;
}

.rate-circle {
	width: 120px;
	height: 120px;
	border-radius: 50%;
	background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8px 24px rgba(245, 158, 11, 0.3);
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
	background: linear-gradient(135deg, var(--qm-warning-soft) 0%, var(--qm-warning-soft-2) 100%);
}

.mini-card.blocked .mini-label {
	color: #d97706;
}

.mini-card.blocked .mini-value {
	color: #b45309;
}

.mini-card.in-progress {
	background: linear-gradient(135deg, var(--qm-warning-soft) 0%, var(--qm-warning-soft-2) 100%);
}

.mini-card.in-progress .mini-label {
	color: #f59e0b;
}

.mini-card.in-progress .mini-value {
	color: #ea580c;
}

.mini-card.not-executed {
	background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
}

.mini-card.not-executed .mini-label {
	color: var(--qm-text-2);
}

.mini-card.not-executed .mini-value {
	color: var(--qm-text-2);
}

.mini-card.total {
	background: linear-gradient(135deg, var(--qm-accent-soft) 0%, #e0e7ff 100%);
}

.mini-card.total .mini-label {
	color: #d97706;
}

.mini-card.total .mini-value {
	color: #c2410c;
}

.overview-bottom {
	background: linear-gradient(135deg, #faf5ff 0%, var(--qm-bg-2) 100%);
	border-radius: 20px;
	padding: 28px;
	margin-bottom: 24px;
	box-shadow: 0 4px 20px rgba(249, 115, 22, 0.1), 0 1px 3px rgba(0, 0, 0, 0.05);
	border: 1px solid rgba(249, 115, 22, 0.15);
	transition: all 0.3s ease;
}

.overview-bottom:last-child {
	margin-bottom: 0;
}

.overview-bottom:hover {
	box-shadow: 0 8px 30px rgba(249, 115, 22, 0.15), 0 2px 8px rgba(0, 0, 0, 0.08);
	transform: translateY(-2px);
}

.section-title {
	font-size: 18px;
	font-weight: 800;
	color: var(--qm-text-1);
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
	background: linear-gradient(180deg, #f59e0b, #f97316);
	border-radius: 3px;
	box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
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
	background: linear-gradient(135deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
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
	color: var(--qm-text-2);
	text-transform: uppercase;
	letter-spacing: 0.5px;
}

.info-value {
	font-size: 14px;
	font-weight: 600;
	color: var(--qm-text-1);
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.overview-content {
	padding: 0;
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
	background: linear-gradient(135deg, var(--qm-bg-2) 0%, #fefefe 100%);
	border-radius: 16px;
	padding: 20px;
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
	border: 1px solid rgba(249, 115, 22, 0.08);
	transition: all 0.3s ease;
}

.executor-card:hover {
	transform: translateY(-4px);
	box-shadow: 0 8px 24px rgba(249, 115, 22, 0.15);
	border-color: rgba(249, 115, 22, 0.2);
	background: var(--qm-bg-2);
}

.executor-header {
	display: flex;
	align-items: center;
	gap: 12px;
	padding-bottom: 16px;
	border-bottom: 1px solid var(--qm-bg-3);
}

.executor-avatar {
	width: 40px;
	height: 40px;
	border-radius: 50%;
	background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
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

.module-filter-bar {
	margin-bottom: 20px;
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
	color: var(--qm-text-2);
}

.status-processing {
	background: rgba(245, 158, 11, 0.1);
	color: #f59e0b;
}

.status-completed {
	background: rgba(16, 185, 129, 0.1);
	color: #10b981;
}

.executor-name {
	font-weight: 600;
	color: var(--qm-text-1);
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
	grid-template-columns: repeat(8, 1fr);
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
	color: var(--qm-text-2);
}

.executor-stat-item .stat-value {
	font-size: 16px;
	font-weight: 700;
	font-family: 'SF Mono', 'Consolas', monospace;
}

.executor-stat-item .stat-value.total {
	color: #d97706;
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
	color: #f59e0b;
}

.executor-stat-item .stat-value.idle {
	color: var(--qm-text-2);
}

.executor-stat-item .stat-value.defect {
	color: #f97316;
}

.empty-tip {
	text-align: center;
	color: var(--qm-text-3);
	padding: 32px 0;
	font-size: 14px;
}

.pagination-wrapper {
	display: flex;
	justify-content: flex-end;
	padding: 16px 0 0 0;
	margin-top: 8px;
	border-top: 1px solid var(--qm-bg-3);
}

/* 表格样式（参考 DefectList） */
.elegant-table {
	width: 100%;
	border-collapse: separate;
	border-spacing: 0;
}

.elegant-table :deep(th.el-table__cell) {
	background: linear-gradient(180deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
	font-weight: 600;
	color: var(--qm-text-1);
	border-bottom: 1px solid var(--qm-line-strong);
}

/* 排序图标：显示上下箭头并高亮当前排序方向 */
.elegant-table :deep(.caret-wrapper) {
	width: 16px;
	height: 16px;
	display: inline-flex;
	align-items: center;
	justify-content: center;
}

.elegant-table :deep(.sort-caret) {
	width: 0;
	height: 0;
	border-left: 4px solid transparent;
	border-right: 4px solid transparent;
}

.elegant-table :deep(.sort-caret.ascending) {
	border-bottom-color: #c0c4cc;
	margin-bottom: 2px;
}

.elegant-table :deep(.sort-caret.descending) {
	border-top-color: #c0c4cc;
	margin-top: 2px;
}

/* 当前排序方向高亮 */
.elegant-table :deep(.ascending .sort-caret.ascending) {
	border-bottom-color: #f59e0b;
}

.elegant-table :deep(.descending .sort-caret.descending) {
	border-top-color: #f59e0b;
}

.elegant-table :deep(tr:nth-child(even)) {
	background: var(--qm-bg-1);
}

.elegant-table :deep(tr:hover) {
	background: var(--qm-warning-soft);
}

/* 列内下拉编辑徽章 */
.status-dropdown {
	display: inline-flex;
	align-items: center;
}

.status-badge {
	display: inline-flex;
	align-items: center;
	gap: 6px;
	padding: 7px 14px;
	border-radius: 20px;
	font-size: 12px;
	font-weight: 500;
	cursor: pointer;
	transition: all 0.2s ease;
	user-select: none;
	line-height: 1.2;
}

.status-badge:hover {
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.status-dot {
	width: 6px;
	height: 6px;
	border-radius: 50%;
	background: var(--qm-bg-2);
	opacity: 0.9;
}

.status-label {
	color: white;
	line-height: 1;
}

.status-arrow {
	font-size: 11px;
	color: white;
	opacity: 0.8;
}

.status-badge-static {
	display: inline-block;
	padding: 5px 12px;
	border-radius: 12px;
	font-size: 12px;
	font-weight: 500;
	line-height: 1.2;
	color: #fff;
}

/* 严重程度颜色 */
.severity-1 { background: linear-gradient(135deg, #f87171 0%, #ef4444 100%); }
.severity-2 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.severity-3 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.severity-4 { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }

/* 优先级颜色 */
.priority-1 { background: linear-gradient(135deg, #f87171 0%, #ef4444 100%); }
.priority-2 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.priority-3 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.priority-4 { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }

/* BUG类型颜色 */
.defect-type-1 { background: linear-gradient(135deg, #a78bfa 0%, #f97316 100%); }
.defect-type-2 { background: linear-gradient(135deg, #22d3ee 0%, #d97706 100%); }
.defect-type-3 { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }
.defect-type-4 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.defect-type-5 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.defect-type-6 { background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%); }
.defect-type-7 { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); }

/* 状态颜色 */
.defect-status-1 { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }
.defect-status-2 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.defect-status-3 { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); }
.defect-status-4 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }

/* 处理人颜色 */
.assignee-none { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }
.assignee-1 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.assignee-2 { background: linear-gradient(135deg, #a78bfa 0%, #f97316 100%); }
.assignee-3 { background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%); }
.assignee-4 { background: linear-gradient(135deg, #fb7185 0%, #e11d48 100%); }
.assignee-5 { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); }
.assignee-6 { background: linear-gradient(135deg, #22d3ee 0%, #d97706 100%); }
.assignee-7 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.assignee-8 { background: linear-gradient(135deg, #fb923c 0%, #ea580c 100%); }

/* 操作按钮 */
.action-buttons {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
}

.action-btn {
	position: relative;
	overflow: hidden;
	border: none !important;
	width: 32px !important;
	height: 32px !important;
	padding: 0 !important;
	transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.action-btn:hover {
	transform: translateY(-2px) scale(1.1);
}

.action-btn.view-btn {
	background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}
.action-btn.view-btn:hover {
	box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4);
}

.action-btn.edit-btn {
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}
.action-btn.edit-btn:hover {
	box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.action-btn.delete-btn {
	background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
}
.action-btn.delete-btn:hover {
	box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
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

/* 创建/更新信息列样式 */
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

.user-time-cell .icon-user {
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
	color: var(--qm-text-2);
	font-weight: 500;
	flex: 1;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.time-text {
	font-size: 12px;
	color: var(--qm-text-2);
	flex: 1;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

@media screen and (max-width: 1200px) {
	.overview-page-container {
		padding: 16px;
	}
	
	.overview-top {
		flex-direction: column;
	}
	
	.status-mini-cards {
		grid-template-columns: repeat(3, 1fr);
	}
}

@media screen and (max-width: 768px) {
	.overview-page-container {
		padding: 12px;
	}
	
	.page-header {
		flex-direction: column;
		gap: 16px;
		align-items: stretch;
	}
	
	.back-btn {
		align-self: flex-end;
	}
	
	.info-grid {
		grid-template-columns: 1fr;
	}
	
	.status-mini-cards {
		grid-template-columns: repeat(2, 1fr);
	}
}
</style>

<style>
/* 下拉弹出菜单样式（非 scoped，参考 DefectList） */
.status-dropdown-popper.el-popper {
	padding: 8px !important;
	border-radius: 12px !important;
	border: none !important;
	box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12) !important;
}

.status-dropdown-popper .el-dropdown-menu {
	border: none !important;
	box-shadow: none !important;
	padding: 0 !important;
}

.status-dropdown-popper .el-dropdown-menu__item {
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 10px 16px;
	margin: 2px 0;
	border-radius: 8px;
	transition: all 0.2s ease;
}

.status-dropdown-popper .el-dropdown-menu__item:hover {
	background: var(--qm-bg-3);
}

.status-dropdown-popper .status-indicator {
	width: 10px;
	height: 10px;
	border-radius: 50%;
	flex-shrink: 0;
}

.status-dropdown-popper .status-indicator.danger { background: #ef4444; }
.status-dropdown-popper .status-indicator.warning { background: #f59e0b; }
.status-dropdown-popper .status-indicator.primary { background: #f59e0b; }
.status-dropdown-popper .status-indicator.success { background: #10b981; }
.status-dropdown-popper .status-indicator.info { background: var(--qm-text-3); }
.status-dropdown-popper .status-indicator.purple { background: #f97316; }
.status-dropdown-popper .status-indicator.cyan { background: #d97706; }
.status-dropdown-popper .status-indicator.pink { background: #ec4899; }
.status-dropdown-popper .status-indicator.orange { background: #ea580c; }

.status-dropdown-popper .status-text {
	font-size: 14px;
	font-weight: 500;
	color: var(--qm-text-2);
}

/* 处理人下拉菜单 */
.assignee-dropdown-popper.el-popper {
	padding: 8px !important;
	border-radius: 12px !important;
	border: none !important;
	box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12) !important;
	max-height: 320px;
	overflow-y: auto;
}

.assignee-dropdown-popper .el-dropdown-menu {
	border: none !important;
	box-shadow: none !important;
	padding: 0 !important;
	max-height: 300px;
	overflow-y: auto;
}

.assignee-dropdown-popper .el-dropdown-menu__item {
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 10px 16px;
	margin: 2px 0;
	border-radius: 8px;
	transition: all 0.2s ease;
}

.assignee-dropdown-popper .el-dropdown-menu__item:hover {
	background: var(--qm-bg-3);
}

.assignee-dropdown-popper .status-indicator {
	width: 10px;
	height: 10px;
	border-radius: 50%;
	flex-shrink: 0;
}

.assignee-dropdown-popper .status-indicator.danger { background: #ef4444; }
.assignee-dropdown-popper .status-indicator.warning { background: #f59e0b; }
.assignee-dropdown-popper .status-indicator.primary { background: #f59e0b; }
.assignee-dropdown-popper .status-indicator.success { background: #10b981; }
.assignee-dropdown-popper .status-indicator.info { background: var(--qm-text-3); }
.assignee-dropdown-popper .status-indicator.purple { background: #f97316; }
.assignee-dropdown-popper .status-indicator.cyan { background: #d97706; }
.assignee-dropdown-popper .status-indicator.pink { background: #ec4899; }
.assignee-dropdown-popper .status-indicator.orange { background: #ea580c; }

.assignee-dropdown-popper .status-text {
	font-size: 14px;
	font-weight: 500;
	color: var(--qm-text-2);
}
</style>
