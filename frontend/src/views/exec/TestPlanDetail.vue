<template>
	<el-dialog v-model="lookLogVisible" direction="rtl" :show-close="true" destroy-on-close fullscreen>
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
											<BodyEdit :bind_case_data="bind_case_data" v-model="one_case_log.logs[step_index].logs[log_index].value"></BodyEdit>
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

	<div class="plan-detail-container">
		<!-- 左侧模块树 -->
		<div class="sidebar-card elegant-shadow">
			<div class="sidebar-header">
				<div class="sidebar-title-wrapper">
					<i class="icon-tree"></i>
					<h3 class="sidebar-title">模块管理</h3>
				</div>
				<el-radio-group v-model="includeChildren" @change="onIncludeChildrenChange" size="small" class="include-children-radio">
					<el-radio-button :label="true">含子节点</el-radio-button>
					<el-radio-button :label="false">仅当前</el-radio-button>
				</el-radio-group>
			</div>
			
			<div class="sidebar-content">
				<div class="search-wrapper">
					<el-input 
						v-model="filterText" 
						placeholder="请输入模块名称" 
						clearable
						class="input"
						size='large'
					>
					<template #prefix>
						<el-icon><Search /></el-icon>
					</template>
					</el-input>
					<el-divider class="tree-divider" />
				</div>
				
				<div class="tree-wrapper">
					<el-tree 
						ref="treeRef"
						highlight-current
						node-key='id'
						:expand-on-click-node='false'
					    :indent='10'
						@node-click='moduleSelect'
						:current-node-key='selectNode'
						:filter-node-method="filterNode"
						:data='plant_module_list' 
						:props="{label: 'name'}" 
						class="elegant-tree"
					> 
						<template #default="{ node, data }">
							<div class="custom-tree-node">
								<div class="node-content">
									<i class="icon-folder-tree" :class="{ 'icon-folder-tree-root': data.id < 0 }"></i>
									<el-tooltip :content="node.label" placement="top">
										<span class="node-label">{{ node.label }}</span>
									</el-tooltip>
								</div>
							</div>
						</template>
					</el-tree>
				</div>
				
				<div class="tree-actions">
					<el-divider class="tree-divider" />
					<div class="tree-buttons">
						<el-button @click="expandAllNodes" class="tree-btn"  type='success'>
							<el-icon><Expand /></el-icon>全部展开
						</el-button>
						<el-button @click="collapseAllNodes" class="tree-btn" >
							<el-icon><Fold /></el-icon>全部折叠
						</el-button>
					</div>
				</div>
			</div>
		</div>

		<!-- 右侧主要内容区域 -->
		<div class="main-content">
			<el-card class="filter-card elegant-shadow">
				<div class="filter-header">
					<div class="header-title-section">
						<i class="icon-search"></i>
						<h3 class="filter-title">关联用例筛选</h3>
						<el-tag size="small" type="info" effect="plain">精准查询</el-tag>
					</div>
					<div class="header-action-section">
						<el-button @click="handleReset" class="reset-btn" size="large">
							<el-icon><RefreshLeft /></el-icon>重置
						</el-button>
						<el-button @click="handleSearch" type="primary" class="search-btn" size="large">
							<el-icon><Search /></el-icon>查询
						</el-button>
					</div>
				</div>
				
				<div class="filter-form-wrapper">
					<el-form :model="filterParams" class="filter-form inline-form">
						<el-row :gutter="24">
							<el-col :xs="24" :sm="12" :md="8" :lg="6">
								<el-form-item class="form-item-inline">
									<div class="label-with-icon">
										<i class="icon-case-name"></i>
										<span class="label-text">用例名称</span>
									</div>
									<el-input 
										v-model="filterParams.name" 
										placeholder="请输入用例名称" 
										clearable
										size="large"
										class="input"
										@keyup.enter="loadCaseList"
									/>
								</el-form-item>
							</el-col>
							<el-col :xs="24" :sm="12" :md="8" :lg="6">
								<el-form-item class="form-item-inline">
									<div class="label-with-icon">
										<i class="icon-status"></i>
										<span class="label-text">执行状态</span>
									</div>
									<el-select 
										v-model="filterParams.exec_status" 
										placeholder="全部状态" 
										clearable
										filterable
										size="large"
										popper-class="select-dropdown-rounded"
										class="select"
									>
										<el-option label="未执行" :value="1"></el-option>
										<el-option label="暂缓" :value="2"></el-option>
										<el-option label="已通过" :value="3"></el-option>
										<el-option label="未通过" :value="4"></el-option>
									</el-select>
								</el-form-item>
							</el-col>
							<el-col :xs="24" :sm="12" :md="8" :lg="6">
								<el-form-item class="form-item-inline">
									<div class="label-with-icon">
										<i class="icon-executor"></i>
										<span class="label-text">执行人</span>
									</div>
									<el-select 
									v-model="filterParams.executed_by" 
									placeholder="全部执行人" 
									clearable
									filterable
									size="large"
									popper-class="select-dropdown-rounded"
									class="select"
								>
									<el-option 
										v-for="user in userList" 
										:key="user.id" 
										:label="user.username" 
										:value="user.id"
									></el-option>
								</el-select>
							</el-form-item>
						</el-col>
						<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="form-item-inline">
								<div class="label-with-icon">
									<i class="icon-creator"></i>
									<span class="label-text">添加人</span>
								</div>
								<el-select 
									v-model="filterParams.added_by" 
									placeholder="全部添加人" 
									clearable
									filterable
									size="large"
									popper-class="select-dropdown-rounded"
									class="select"
								>
									<el-option 
										v-for="user in userList" 
										:key="user.id" 
										:label="user.username" 
										:value="user.id"
									></el-option>
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
							<h3 class="content-title">关联用例列表</h3>
							<el-tooltip 
								placement="top"
								:show-arrow="false"
								effect="dark"
								class="rate-tooltip-wrapper"
							>
								<template #content>
									<div class="rate-tooltip">
										<div class="tooltip-item">
											<span class="tooltip-label">总用例数:</span>
											<span class="tooltip-value">{{ total || 0 }}</span>
										</div>
										<div class="tooltip-item">
											<span class="tooltip-label">通过:</span>
											<span class="tooltip-value success">{{ passedCount }}</span>
										</div>
										<div class="tooltip-item">
											<span class="tooltip-label">失败:</span>
											<span class="tooltip-value danger">{{ failedCount }}</span>
										</div>
										<div class="tooltip-item">
											<span class="tooltip-label">进行中:</span>
											<span class="tooltip-value primary">{{ inProgressCount }}</span>
										</div>
										<div class="tooltip-item">
											<span class="tooltip-label">未执行:</span>
											<span class="tooltip-value warning">{{ notExecutedCount }}</span>
										</div>
										<div class="tooltip-item">
											<span class="tooltip-label">暂缓:</span>
											<span class="tooltip-value info">{{ postponedCount }}</span>
										</div>
									</div>
								</template>
								<div class="pass-rate-display">
									<div class="pass-rate-bar">
										<div 
											v-if="total > 0"
											class="rate-segment passed"
											:style="{ width: getSegmentWidth(passedCount, total) }"
										></div>
										<div 
											v-if="total > 0"
											class="rate-segment failed"
											:style="{ width: getSegmentWidth(failedCount, total) }"
										></div>
										<div 
											v-if="total > 0"
											class="rate-segment postponed"
											:style="{ width: getSegmentWidth(postponedCount, total) }"
										></div>
										<div 
											v-if="total > 0"
											class="rate-segment not-executed"
											:style="{ width: getSegmentWidth(notExecutedCount, total) }"
										></div>
									</div>
									<span class="pass-rate-text">通过率 {{ calculatePassRate() }}%</span>
								</div>
							</el-tooltip>
						</div>
					</div>
					<div class="header-action-section">
						<div class="selected-count-badge" v-if="selectedCases.length > 0">
							<el-icon><SuccessFilled /></el-icon>
							<span>已选 {{ selectedCases.length }}</span>
						</div>
						<el-dropdown 
							v-if="permission.has_edit_permission"
							@command="handleBatchCommand" 
							:disabled="selectedCases.length === 0"
							class="batch-dropdown"
							popper-class="batch-dropdown-popper"
						>
							<el-button class="toolbar-btn" :disabled="selectedCases.length === 0">
								<el-icon><Setting /></el-icon>批量操作
							</el-button>
							<template #dropdown>
								<el-dropdown-menu>
									<el-dropdown-item command="executor" class="batch-dropdown-item" v-if="permission.has_edit_permission">
										<span class="item-text">修改执行人</span>
									</el-dropdown-item>
									<el-dropdown-item command="result" class="batch-dropdown-item" v-if="permission.has_edit_permission">
										<span class="item-text">修改执行状态</span>
									</el-dropdown-item>
									<el-dropdown-item command="run" class="batch-dropdown-item" v-if="permission.has_edit_permission">
										<span class="item-text">执行脚本用例</span>
									</el-dropdown-item>
									<el-dropdown-item command="remove" class="batch-dropdown-item" v-if="permission.has_delete_permission">
										<span class="item-text">移除用例</span>
									</el-dropdown-item>
								</el-dropdown-menu>
							</template>
						</el-dropdown>
						<el-button
							v-if="permission.has_add_permission"
							@click="openChooseCase"
							type="primary"
							class="add-btn"
						>
							<el-icon><Plus /></el-icon>关联功能用例
						</el-button>
					</div>
				</div>

				<div class="table-wrapper">
					<el-table
						ref="tableRef"
						:data="tableData" 
						:max-height="'calc(100vh - 490px)'"
						class="elegant-table"
						:header-row-style="headerRowStyle"
						v-loading="loading"
						@selection-change="handleSelectionChange"
					>
						<el-table-column 
							type="selection"
							width="55"
							align="center"
						/>

						<el-table-column 
							label="用例名称" 
							min-width="150" 
							align="left"
							class-name="name-column"
						>
							<template #default="scope">
								<el-link type="primary" class="case-link" @click="openCaseDetail(scope.row)">
									{{ scope.row.func_case_name || '-' }}
								</el-link>
							</template>
						</el-table-column>

						<el-table-column 
							label="用例标签" 
							width="150" 
							align="center"
							class-name="tag-column"
						>
							<template #default="scope">
								<div class="case-tag-list">
									<span 
										v-for="(tag, index) in (scope.row.func_case_tag_names || [])"
										:key="index"
										class="case-tag-badge"
									>
										{{ tag }}
									</span>
								</div>
							</template>
						</el-table-column>

						<el-table-column 
							label="执行状态" 
							width="150" 
							align="center"
							class-name="status-column"
						>
							<template #default="scope">
								<el-dropdown v-if="permission.has_edit_permission" trigger="click" @command="(val) => updateExecStatus(scope.row, val)" class="status-dropdown" popper-class="status-dropdown-popper">
									<span class="status-badge" :class="'status-' + scope.row.exec_status">
										<span class="status-dot"></span>
										<span class="status-label">{{ scope.row.exec_status_name || getExecStatusName(scope.row.exec_status) }}</span>
										<el-icon class="status-arrow"><ArrowDown /></el-icon>
									</span>
									<template #dropdown>
										<el-dropdown-menu>
									<el-dropdown-item :command="5" class="status-dropdown-item">
										<span class="status-indicator primary"></span>
										<span class="status-text">进行中</span>
									</el-dropdown-item>
									<el-dropdown-item :command="2" class="status-dropdown-item">
										<span class="status-indicator warning"></span>
										<span class="status-text">暂缓</span>
									</el-dropdown-item>
									<el-dropdown-item :command="3" class="status-dropdown-item">
										<span class="status-indicator success"></span>
										<span class="status-text">已通过</span>
									</el-dropdown-item>
									<el-dropdown-item :command="4" class="status-dropdown-item">
										<span class="status-indicator danger"></span>
										<span class="status-text">未通过</span>
									</el-dropdown-item>
								</el-dropdown-menu>
									</template>
								</el-dropdown>
							</template>
						</el-table-column>

						<el-table-column
							label="自动化信息"
							width="150"
							align="center"
							class-name="auto-info-column"
						>
							<template #default="scope">
								<div class="auto-info-cell">
									<span class="auto-type-tag" v-if="scope.row.func_case_detail?.can_autoed_name">
										{{ scope.row.func_case_detail.can_autoed_name }}
									</span>
									<span class="auto-status-tag" v-if="scope.row.func_case_detail?.auto_status_name">
										{{ scope.row.func_case_detail.auto_status_name }}
									</span>
								</div>
							</template>
						</el-table-column>

						<el-table-column
							label="执行信息"
							width="180"
							align="center"
							class-name="info-column"
						>
							<template #default="scope">
								<div class="user-time-cell">
									<div class="user-info">
										<i class="icon-user"></i>
										<span class="user-name">{{ scope.row.executed_by_name || '-' }}</span>
									</div>
									<div class="time-info">
										<i class="icon-time-small"></i>
										<span class="time-text">{{ scope.row.executed_time ? formatTime(scope.row.executed_time) : '-' }}</span>
									</div>
								</div>
							</template>
						</el-table-column>

						<el-table-column 
							label="更新信息" 
							width="180" 
							align="center"
							class-name="info-column"
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
							label="创建信息" 
							width="180" 
							align="center"
							class-name="info-column"
						>
							<template #default="scope">
								<div class="user-time-cell">
									<div class="user-info">
										<i class="icon-user"></i>
										<span class="user-name">{{ scope.row.added_by_name || '-' }}</span>
									</div>
									<div class="time-info">
										<i class="icon-time-small"></i>
										<span class="time-text">{{ formatTime(scope.row.create_time) }}</span>
									</div>
								</div>
						</template>
					</el-table-column>

					<el-table-column 
						label="操作" 
						width="100" 
						align="center"
						class-name="action-column"
					>
						<template #default="scope">
							<el-tooltip 
								content="执行关联脚本用例" 
								placement="top" 
								effect="dark"
							>
								<el-button 
									circle 
									type="primary" 
									@click="run(scope.row)"
									class="action-btn run-btn"
								>
									<el-icon><VideoPlay /></el-icon>
								</el-button>
							</el-tooltip>
						</template>
					</el-table-column>
				</el-table>
				</div>

				<div class="pagination-wrapper">
					<el-pagination
						v-model:current-page="page"
						v-model:page-size="size"
						:page-sizes="[10, 20, 30, 50]"
						layout="total, sizes, prev, pager, next, jumper"
						:total="total"
						@size-change="handleSizeChange"
						@current-change="handleCurrentChange"
						class="select input"
						:background="true"
					/>
				</div>
			</el-card>
		</div>

		<!-- 执行测试用例对话框 -->
		<el-dialog v-model="runTimesVisible" title="执行关联脚本用例" width="600" class="elegant-dialog">
		    <el-form :model="runCaseForm" label-width="120px" class="run-dialog-form" :rules="runRules" ref='runRef' label-position='top'>
				<el-form-item label="执行环境" prop="env_id">
					<el-select v-model="runCaseForm.env_id" class="select" placeholder="请选择执行环境" popper-class='select-dropdown-rounded' size='large'>
						<el-option
						  v-for="item in env_list.results"
						  :key="item.id"
						  :label="item.name"
						  :value="item.id"
						/>
					</el-select>
				</el-form-item>
		    </el-form>
		    <template #footer>
				<span class="dialog-footer">
					<el-button @click="runTimesVisible = false" class="dialog-cancel-btn">取消</el-button>
					<el-button type="primary" @click="caseRun" class="dialog-confirm-btn">执行</el-button>
				</span>
		    </template>
		</el-dialog>

		<el-drawer 
		v-model="chooseCaseVisible" 
		:with-header="false" 
		direction="ttb" 
		show-close 
		:z-index="1001" 
		size="'calc(100vh - 30px)'"
		destroy-on-close
	>
			<FunCaseList 
				:isCanChoose="true"
				:parentPermission="permission"
				:existCaseIds="existCaseIds"
				v-model:chooseCaseVisible="chooseCaseVisible" 
				@setFuncCaseData="addSingleCase"
				@setFuncManyCaseData="addCasesToPlan"
			></FunCaseList>
		</el-drawer>



		<el-dialog v-model="executorDialogVisible" title="批量修改执行人" width="500px" class="elegant-dialog">
			<el-form :model="batchForm" label-position="top" class="batch-form">
				<el-form-item label="选择执行人">
					<el-select v-model="batchForm.executed_by" 
					placeholder="请选择执行人" 
					style="width: 100%"
					size='large'
					popper-class="select-dropdown-rounded"
					class="select">
						<el-option 
							v-for="user in userList" 
							:key="user.id" 
							:label="user.username" 
							:value="user.id"
						></el-option>
					</el-select>
				</el-form-item>
			</el-form>
			<template #footer>
				<el-button @click="executorDialogVisible = false">取消</el-button>
				<el-button type="primary" @click="confirmModifyExecutor">确定修改</el-button>
			</template>
		</el-dialog>

		<el-dialog v-model="resultDialogVisible" title="批量修改执行状态" width="500px" class="elegant-dialog">
			<el-form :model="batchForm" label-position="top" class="batch-form">
				<el-form-item label="选择执行状态">
					<el-radio-group v-model="batchForm.exec_status">
						<el-radio :label="5" class="result-radio">
							<span class="radio-dot primary"></span>
							<span class="radio-label">进行中</span>
						</el-radio>
						<el-radio :label="2" class="result-radio">
							<span class="radio-dot warning"></span>
							<span class="radio-label">暂缓</span>
						</el-radio>
						<el-radio :label="3" class="result-radio">
							<span class="radio-dot success"></span>
							<span class="radio-label">已通过</span>
						</el-radio>
						<el-radio :label="4" class="result-radio">
							<span class="radio-dot danger"></span>
							<span class="radio-label">未通过</span>
						</el-radio>
					</el-radio-group>
				</el-form-item>
			</el-form>
			<template #footer>
				<el-button @click="resultDialogVisible = false">取消</el-button>
				<el-button type="primary" @click="confirmModifyResult">确定修改</el-button>
			</template>
		</el-dialog>

		<el-drawer
			v-model="caseDetailVisible"
			direction="rtl"
			:size="'85vw'"
			:show-close="true"
			:with-header="false"
			class="case-detail-drawer"
			@closed="onCaseDetailClosed"
		>
			<div class="detail-header">
				<div class="title-area">
					<h3 class="drawer-title">{{ currentCase.func_case_name || '用例详情' }}</h3>
					<el-tooltip content="复制用例" placement="top" effect="dark">
						<el-button type="primary" class="copy-btn" @click="copyCase" circle size="small">
							<el-icon><DocumentCopy /></el-icon>
						</el-button>
					</el-tooltip>
				</div>
			</div>
			
			<div class="detail-nav-wrapper">
				<div class="vertical-nav">
					<div 
						v-for="(item, index) in navItems" 
						:key="index"
						class="nav-item"
						:class="{ active: activeSection === item.id }"
						@click="scrollToSection(item.id)"
					>
						<el-icon class="nav-icon" v-if="item.icon">{{ item.icon }}</el-icon>
						<span class="nav-text">{{ item.name }}</span>
					</div>
				</div>
			</div>

			<div class="case-detail-container" v-if="currentCase.func_case_detail">
				<div class="case-detail-main">
					<el-card class="section-card" id="section-basic">
						<div class="section-divider">
							<span class="section-title">基础信息</span>
						</div>
						<el-divider style="margin-top: 0px"></el-divider>
						<div class="section-content">
							<el-row :gutter="32">
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">所属模块</label>
										<div class="form-value">{{ currentCase.func_case_detail.module_name || '-' }}</div>
									</div>
								</el-col>
								<el-col :span="8">
								<div class="form-item exec-status-item" :class="'exec-status-' + currentCase.exec_status">
									<label class="form-label">执行状态</label>
									<el-dropdown v-if="permission.has_edit_permission" trigger="click" @command="updateExecStatusDetail" class="status-dropdown" popper-class="status-dropdown-popper">
										<span class="status-badge" :class="'status-' + currentCase.exec_status">
											<span class="status-dot"></span>
											<span class="status-label">{{ currentCase.exec_status_name || getExecStatusName(currentCase.exec_status) }}</span>
											<el-icon class="status-arrow"><ArrowDown /></el-icon>
										</span>
										<template #dropdown>
											<el-dropdown-menu>
												<el-dropdown-item :command="5" class="status-dropdown-item">
													<span class="status-indicator primary"></span>
													<span class="status-text">进行中</span>
												</el-dropdown-item>
												<el-dropdown-item :command="2" class="status-dropdown-item">
													<span class="status-indicator warning"></span>
													<span class="status-text">暂缓</span>
												</el-dropdown-item>
												<el-dropdown-item :command="3" class="status-dropdown-item">
													<span class="status-indicator success"></span>
													<span class="status-text">已通过</span>
												</el-dropdown-item>
												<el-dropdown-item :command="4" class="status-dropdown-item">
													<span class="status-indicator danger"></span>
													<span class="status-text">未通过</span>
												</el-dropdown-item>
											</el-dropdown-menu>
										</template>
									</el-dropdown>
									<span v-else class="status-badge" :class="'status-' + currentCase.exec_status">
										<span class="status-dot"></span>
										<span class="status-label">{{ currentCase.exec_status_name || getExecStatusName(currentCase.exec_status) || '-' }}</span>
									</span>
								</div>
							</el-col>
								<el-col :span="8">
								<div class="form-item executor-item">
									<label class="form-label">执行人</label>
									<el-dropdown v-if="permission.has_edit_permission" trigger="click" @command="updateExecutorDetail" class="status-dropdown" popper-class="assignee-dropdown-popper">
										<span class="status-badge" :class="getAssigneeClass(currentCase.executed_by)">
											<span class="status-dot"></span>
											<span class="status-label">{{ currentCase.executed_by_name || '未分配' }}</span>
											<el-icon class="status-arrow"><ArrowDown /></el-icon>
										</span>
										<template #dropdown>
											<el-dropdown-menu>
												<el-dropdown-item v-for="user in userList" :key="user.id" :command="user.id" class="status-dropdown-item">
													<span class="status-indicator" :class="getIndicatorClassByUserId(user.id)"></span>
													<span class="status-text">{{ user.username }}</span>
												</el-dropdown-item>
											</el-dropdown-menu>
										</template>
									</el-dropdown>
									<span v-else class="status-badge" :class="getAssigneeClass(currentCase.executed_by)">
										<span class="status-dot"></span>
										<span class="status-label">{{ currentCase.executed_by_name || '未分配' }}</span>
									</span>
								</div>
							</el-col>
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">自动化类型</label>
										<div class="form-value">
											<span class="tag-item" :class="getAutoTypeTagClass(currentCase.func_case_detail.can_autoed)">
												{{ currentCase.func_case_detail.can_autoed_name || '-' }}
											</span>
										</div>
									</div>
								</el-col>
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">自动化状态</label>
										<div class="form-value">
											<span class="tag-item" :class="getAutoStatusTagClass(currentCase.func_case_detail.auto_status)">
												{{ currentCase.func_case_detail.auto_status_name || '-' }}
											</span>
										</div>
									</div>
								</el-col>
								<el-col :span="4">
									<div class="form-item">
										<label class="form-label">用例标签</label>
										<div class="form-value">
											<span v-for="(tag, index) in currentCase.func_case_detail.tag_name" :key="index" class="tag-item">
												{{ tag.name }}
											</span>
											<span v-if="!currentCase.func_case_detail.tag_name || currentCase.func_case_detail.tag_name.length === 0">-</span>
										</div>
									</div>
								</el-col>
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">用例负责人</label>
										<div class="form-value">{{ currentCase.func_case_detail.owner_name || '-' }}</div>
									</div>
								</el-col>
							</el-row>
							<el-row :gutter="32">
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">创建人</label>
										<div class="form-value">{{ currentCase.func_case_detail.create_by_name || '-' }}</div>
									</div>
								</el-col>
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">创建时间</label>
										<div class="form-value">{{ formatTime(currentCase.func_case_detail.create_time) }}</div>
									</div>
								</el-col>
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">更新人</label>
										<div class="form-value">{{ currentCase.func_case_detail.update_by_name || '-' }}</div>
									</div>
								</el-col>
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">更新时间</label>
										<div class="form-value">{{ formatTime(currentCase.func_case_detail.update_time) }}</div>
									</div>
								</el-col>
							</el-row>
							<el-row :gutter="32">
								<el-col :span="8">
									<div class="form-item">
										<label class="form-label">执行时间</label>
										<div class="form-value">{{ currentCase.executed_time ? formatTime(currentCase.executed_time) : '-' }}</div>
									</div>
								</el-col>
							</el-row>
						</div>
					</el-card>

					<el-card class="section-card" id="section-precondition">
						<div class="section-divider">
							<span class="section-title">前置条件</span>
						</div>
						<el-divider style="margin-top: 0px"></el-divider>
						<div class="rich-content">
							<div class="rich-text-view" v-html="currentCase.func_case_detail.setup_condition || '暂无前置条件'"></div>
						</div>
					</el-card>

					<el-card class="section-card" id="section-steps">
						<div class="section-divider">
							<span class="section-title">测试步骤</span>
						</div>
						<el-divider style="margin-top: 0px"></el-divider>
						<div class="steps-content">
							<div v-if="currentCase.func_case_detail.step_type === 1" class="rich-content">
								<div class="rich-text-view" v-html="currentCase.func_case_detail.step_text || '暂无步骤信息'"></div>
							</div>
							<FunCaseTable 
								v-if="currentCase.func_case_detail.step_type === 2" 
								:tableData="currentCase.func_case_detail.step_table"
								:height="300"
								:readonly="true">
							</FunCaseTable>
						</div>
					</el-card>

					<el-card class="section-card" id="section-expected" v-if="currentCase.func_case_detail.step_type === 1">
						<div class="section-divider">
							<span class="section-title">预期结果</span>
						</div>
						<el-divider style="margin-top: 0px"></el-divider>
						<div class="rich-content">
							<div class="rich-text-view" v-html="currentCase.func_case_detail.exp_text || '暂无预期结果'"></div>
						</div>
					</el-card>

					<el-card class="section-card" id="section-remark">
						<div class="section-divider">
							<span class="section-title">备注信息</span>
						</div>
						<el-divider style="margin-top: 0px"></el-divider>
						<div class="rich-content">
							<div class="rich-text-view" v-html="currentCase.func_case_detail.case_mark || '暂无备注'"></div>
						</div>
					</el-card>

					<el-card class="section-card" id="section-script" v-if="currentCase.func_case_detail.can_autoed !== 3 && currentCase.func_case_detail.case_detail && currentCase.func_case_detail.case_detail.length > 0">
						<div class="section-divider">
							<span class="section-title">关联自动化脚本用例</span>
						</div>
						<el-divider style="margin-top: 0px"></el-divider>
						<el-table
							:data="currentCase.func_case_detail.case_detail"
							class="elegant-table"
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
								min-width="220"
								align="center"
								class-name="case-info-column"
							>
								<template #default="scope">
									<div class="case-info-cell">
										<div class="case-type-badge">
											<el-tag
												size="small"
												:type="getScriptCaseTagType(scope.row.type_name)"
												effect="light"
												class="type-tag"
											>
												{{ scope.row.type_name }}
											</el-tag>
										</div>
										<span class="case-name">{{ scope.row.name }}</span>
									</div>
								</template>
							</el-table-column>

							<el-table-column
								label="自动化测试结果"
								min-width="140"
								align="center"
								class-name="tag-column"
							>
								<template #default="scope">
									<div class="tags-container">
										<el-tag
											:type="getTestResultType(scope.row.recent_plan_test_result)"
											effect="light"
											class="case-tag"
										>
											{{ getTestResultName(scope.row.recent_plan_test_result) }}
										</el-tag>
									</div>
								</template>
							</el-table-column>

							<el-table-column
								label="用例标签"
								min-width="140"
								align="center"
								class-name="tag-column"
							>
								<template #default="scope">
									<div class="tags-container">
										<el-tag
											v-for="tag in scope.row.tag_name"
											:key="tag.id"
											size="small"
											:type="getTagType(tag.name)"
											effect="light"
											class="case-tag"
										>
											{{ tag.name }}
										</el-tag>
										<span v-if="!scope.row.tag_name || scope.row.tag_name.length === 0">-</span>
									</div>
								</template>
							</el-table-column>

							<el-table-column
								label="创建信息"
								width="180"
								align="center"
								class-name="creator-column"
							>
								<template #default="scope">
									<div class="user-time-cell">
										<div class="user-info">
											<el-icon><User /></el-icon>
											<span>{{ scope.row.create_by_name || '-' }}</span>
										</div>
										<div class="time-info">
											<el-icon><Document /></el-icon>
											<span>{{ formatTime(scope.row.create_time) }}</span>
										</div>
									</div>
								</template>
							</el-table-column>

							<el-table-column
								label="操作"
								width="100"
								align="center"
								class-name="action-column"
							>
								<template #default="scope">
									<el-tooltip
										v-if="scope.row.recent_plan_test_result"
										content="查看执行日志"
										placement="top"
										effect="dark"
									>
										<el-button
											type="success"
											circle
											@click="viewScriptCase(scope.row)"
										>
											<el-icon><View /></el-icon>
										</el-button>
									</el-tooltip>
									<span v-else>-</span>
								</template>
							</el-table-column>
						</el-table>
					</el-card>

					<el-card class="section-card" id="section-comment" shadow="never">
						<el-tabs v-model="activeTab" class="dynamic-tabs" @tab-change="handleTabChange">
							<el-tab-pane label="执行动态" name="comments">
								<div class="comments-container">
									<div class="comment-input-area" v-if="permission.has_add_permission">
									<FullText
										v-model="newCommentContent"
										:height="250"
										:auto-height="true"
										placeholder="请输入评论内容...输入 @ 可提及项目用户"
										:enable-mention="true"
										:mention-users="userList"
										:mention-excluded-ids="newCommentMentionExcludedIds"
									></FullText>
									<div class="comment-actions">
									<el-button type="primary" @click="submitComment" :loading="submittingComment" class="publish-comment-btn">
										<el-icon><Plus /></el-icon>发布评论
									</el-button>
									</div>
								</div>
									<div class="comments-list">
										<div class="comment-item" v-for="comment in commentsList" :key="comment.id">
											<div class="comment-header">
												<div class="comment-user">
													<el-avatar :size="32" class="user-avatar">
														{{ comment.comment_by_name?.charAt(0) || 'U' }}
													</el-avatar>
													<span class="user-name">{{ comment.comment_by_name || '未知用户' }}</span>
												</div>
												<div class="comment-actions-right">
													<span class="comment-time">{{ formatTime(comment.create_time) }}</span>
													<span class="comment-actions-btns">
														<el-button
															v-if="permission.has_edit_permission"
															type="text"
															size="small"
															@click="editComment(comment)"
														>编辑</el-button>
														<el-button
															v-if="canDeleteComment(comment)"
															type="text"
															size="small"
															class="delete-btn"
															@click="deleteComment(comment)"
														>删除</el-button>
													</span>
												</div>
											</div>
											<div class="comment-content">
											<div v-if="editingCommentId === comment.id" class="edit-comment-area">
												<FullText
													v-model="editCommentContent"
													:height="150"
													:auto-height="true"
													:enable-mention="true"
													:mention-users="userList"
													:mention-excluded-ids="editCommentMentionExcludedIds"
												></FullText>
												<div class="edit-actions" v-if="permission.has_edit_permission">
													<el-button size="small" @click="saveCommentEdit(comment)" type="primary">保存</el-button>
													<el-button size="small" @click="cancelCommentEdit">取消</el-button>
												</div>
											</div>
											<div class="rich-text-view" v-else v-html="comment.content"></div>
										</div>
										</div>
										<el-empty v-if="commentsList.length === 0" description="暂无评论" :image-size="100"></el-empty>
									</div>
								</div>
							</el-tab-pane>
							<el-tab-pane label="关联缺陷" name="defects">
								<div class="defects-container">
									<el-table
										:data="defectsList"
										v-loading="defectsLoading"
										max-height="420"
										class="defects-table"
										:show-overflow-tooltip="true"
										empty-text="暂无关联缺陷"
									>
										<el-table-column type="index" label="序号" width="70" align="center" :index="defectIndexMethod" />
										<el-table-column label="标题" prop="title" min-width="200" align="center">
											<template #default="scope">
												<el-link type="primary" @click="goToDefectDetail(scope.row)">{{ scope.row.title }}</el-link>
											</template>
										</el-table-column>
										<el-table-column label="严重程度" prop="severity" width="130" align="center">
											<template #default="scope">
												<span class="status-badge" :class="'severity-' + scope.row.severity">
													<span class="status-dot"></span>
													<span class="status-label">{{ scope.row.severity_name || '-' }}</span>
												</span>
											</template>
										</el-table-column>
										<el-table-column label="优先级" prop="priority" width="120" align="center">
											<template #default="scope">
												<span class="status-badge" :class="'priority-' + scope.row.priority">
													<span class="status-dot"></span>
													<span class="status-label">{{ scope.row.priority_name || '-' }}</span>
												</span>
											</template>
										</el-table-column>
										<el-table-column label="BUG类型" prop="defect_type" width="150" align="center">
											<template #default="scope">
												<span class="status-badge" :class="'defect-type-' + scope.row.defect_type">
													<span class="status-dot"></span>
													<span class="status-label">{{ scope.row.defect_type_name || '-' }}</span>
												</span>
											</template>
										</el-table-column>
										<el-table-column label="状态" prop="status" width="120" align="center">
											<template #default="scope">
												<span class="status-badge" :class="'defect-status-' + scope.row.status">
													<span class="status-dot"></span>
													<span class="status-label">{{ scope.row.status_name || '-' }}</span>
												</span>
											</template>
										</el-table-column>
										<el-table-column label="负责人" prop="owner_name" width="180" align="center">
										<template #default="scope">
											<span class="status-badge" :class="getAssigneeClass(scope.row.owner)">
												<span class="status-dot"></span>
												<span class="status-label">{{ scope.row.owner_name || '未分配' }}</span>
											</span>
										</template>
									</el-table-column>
									<el-table-column label="处理人" prop="assignee_name" width="180" align="center">
											<template #default="scope">
												<span class="status-badge" :class="getAssigneeClass(scope.row.assignee)">
													<span class="status-dot"></span>
													<span class="status-label">{{ scope.row.assignee_name || '未分配' }}</span>
												</span>
											</template>
										</el-table-column>
										<el-table-column label="创建信息" width="200" align="center" prop="create_time" class-name="creator-column">
											<template #default="scope">
												<div class="user-time-cell">
													<div class="user-info">
														<el-icon><User /></el-icon>
														<span class="user-name">{{ scope.row.create_by_name || '-' }}</span>
													</div>
													<div class="time-info">
														<el-icon><Document /></el-icon>
														<span class="time-text">{{ formatTime(scope.row.create_time) }}</span>
													</div>
												</div>
											</template>
										</el-table-column>
										<el-table-column label="更新信息" width="200" align="center" prop="update_time" class-name="updater-column">
											<template #default="scope">
												<div class="user-time-cell">
													<div class="user-info">
														<el-icon><User /></el-icon>
														<span class="user-name">{{ scope.row.update_by_name || '-' }}</span>
													</div>
													<div class="time-info">
														<el-icon><Document /></el-icon>
														<span class="time-text">{{ formatTime(scope.row.update_time) }}</span>
													</div>
												</div>
											</template>
										</el-table-column>
									</el-table>
								</div>
							</el-tab-pane>
						</el-tabs>
					</el-card>
				</div>

				<div class="case-detail-sidebar">
					<el-card class="sidebar-card">
						<div class="section-divider">
							<span class="section-title">执行信息</span>
						</div>
						<el-divider style="margin-top: 0px"></el-divider>
						<div class="sidebar-content">
							<div class="sidebar-item" v-if="permission.has_edit_permission">
								<label class="sidebar-label">执行状态</label>
								<el-select v-model="currentCase.exec_status" size="large" style="width: 100%" @change="updateExecStatusDetail" class="select" popper-class="select-dropdown-rounded">
						<el-option v-if="currentCase.exec_status === 1" label="未执行" :value="1" :disabled="true"></el-option>
						<el-option label="进行中" :value="5"></el-option>
						<el-option label="暂缓" :value="2"></el-option>
						<el-option label="已通过" :value="3"></el-option>
						<el-option label="未通过" :value="4"></el-option>
					</el-select>
							</div>
							<div class="sidebar-item" v-else>
								<label class="sidebar-label">执行状态</label>
								<div class="sidebar-value">{{ getExecStatusName(currentCase.exec_status) || '-' }}</div>
							</div>
							<div class="sidebar-item" v-if="permission.has_edit_permission">
								<label class="sidebar-label">执行人</label>
								<el-select v-model="currentCase.executed_by" size="large" style="width: 100%" @change="updateExecutorDetail" class="select" popper-class="select-dropdown-rounded">
									<el-option 
										v-for="user in userList" 
										:key="user.id" 
										:label="user.username" 
										:value="user.id"
									></el-option>
								</el-select>
							</div>
							<div class="sidebar-item" v-else>
								<label class="sidebar-label">执行人</label>
								<div class="sidebar-value">{{ currentCase.executed_by_name || '-' }}</div>
							</div>
							<div class="sidebar-item">
								<label class="sidebar-label">执行时间</label>
								<div class="sidebar-value">{{ currentCase.executed_time ? formatTime(currentCase.executed_time) : '-' }}</div>
							</div>
							<div class="sidebar-item">
								<label class="sidebar-label">创建人</label>
								<div class="sidebar-value">{{ currentCase.added_by_name || '-' }}</div>
							</div>
							<div class="sidebar-item">
								<label class="sidebar-label">创建时间</label>
								<div class="sidebar-value">{{ formatTime(currentCase.create_time) }}</div>
							</div>
							<div class="sidebar-item">
								<label class="sidebar-label">更新人</label>
								<div class="sidebar-value">{{ currentCase.update_by_name || '-' }}</div>
							</div>
							<div class="sidebar-item">
								<label class="sidebar-label">更新时间</label>
								<div class="sidebar-value">{{ formatTime(currentCase.update_time) }}</div>
							</div>
						</div>
					</el-card>
				</div>
			</div>
		</el-drawer>
	</div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowDown, Delete, Search, Expand, Fold, User, CircleCheck, Document, UserFilled, RefreshLeft, Setting, SuccessFilled, Edit, DocumentCopy } from '@element-plus/icons-vue'
import FunCaseList from '../case/FunCaseList.vue'
import FunCaseTable from '../../components/FunCaseTable.vue'
import BodyEdit from '../../components/BodyEdit.vue'
import FullText from '../../components/FullText.vue'
import api from '../../api/index.js'

import { VideoPlay, View } from '@element-plus/icons-vue'

export default {
	name: 'TestPlanDetail',
	components: { FunCaseList, FunCaseTable, FullText, VideoPlay, View, BodyEdit },
	data() {
		return {
			planId: this.$route.params.id,
			planInfo: {},
			tableData: [],
			existCaseIds: [],
			loading: false,
			page: 1,
			size: 20,
			total: 0,
			chooseCaseVisible: false,
			executorDialogVisible: false,
			resultDialogVisible: false,
			caseDetailVisible: false,
		currentCase: {},
		pendingCaseId: this.$route.query.case_id || null,
		autoCaseOpened: false,
		userList: [],
			batchForm: {
				executed_by: null,
				exec_status: null
			},
			selectedCases: [],
			filterText: '',
			selectNode: null,
			includeChildren: true,
			plant_module_list: [],
			currentModuleId: null,
			filterParams: {
				name: '',
				exec_status: null,
				executed_by: null,
				added_by: null
			},
			activeTab: 'comments',
			newCommentContent: '',
			commentsList: [],
			// 关联缺陷（只读）
			defectsList: [],
			defectsLoading: false,
			defectsLoaded: false,
			submittingComment: false,
		editingCommentId: null,
		editCommentContent: '',
		activeSection: 'section-basic',
			navItems: [],
			permission: {},
			// 执行相关
			runTimesVisible: false,
			runCaseForm: {
				case_id: '',
				env_id: ''
			},
			env_list: {
				results: []
			},
			runRules: {
				env_id: [
					{ required: true, message: '请选择执行环境', trigger: 'change' }
				]
			},
			// 日志查看相关
			lookLogVisible: false,
			one_case_log: {},
			caseActive: '',
			stepActive: '',
			logActive: '',
			bind_case_data: [],
			case_index: 1,
			currentFuncCaseId: null
		}
	},
	computed: {
		...mapState(['pathPermission', 'userInfo', 'projectInfo']),
		// 新评论编辑器中已提及的用户ID（避免重复@）
		newCommentMentionExcludedIds() {
			return this.extractMentionedIds(this.newCommentContent)
		},
		// 编辑评论时已提及的用户ID
		editCommentMentionExcludedIds() {
			return this.extractMentionedIds(this.editCommentContent)
		},
		headerRowStyle() {
			return {
				background: 'var(--qm-bg-1)',
				color: 'var(--qm-text-2)',
				fontWeight: '600'
			}
		},
		passedCount() {
			return this.tableData.filter(item => item.exec_status === 3).length
		},
		failedCount() {
			return this.tableData.filter(item => item.exec_status === 4).length
		},
		notExecutedCount() {
			return this.tableData.filter(item => item.exec_status === 1).length
		},
		postponedCount() {
			return this.tableData.filter(item => item.exec_status === 2).length
		},
		inProgressCount() {
			return this.tableData.filter(item => item.exec_status === 5).length
		}
	},
	watch: {
		filterText(val) {
			this.$refs.treeRef.filter(val)
		},
		// 已在测试计划详情页时，点击@提及消息跳转携带 case_id 自动打开用例抽屉
		'$route.query'(val) {
			const caseId = val && val.case_id
			if (!caseId) return
			if (this.caseDetailVisible && String(this.currentCase.id) === String(caseId)) return
			// 用例列表已加载则直接打开，否则等 loadCaseList 完成后自动打开
			const target = this.tableData.find(item => String(item.id) === String(caseId))
			if (target) {
				this.autoCaseOpened = true
				this.openCaseDetail(target)
			} else {
				this.pendingCaseId = caseId
				this.autoCaseOpened = false
				this.loadCaseList()
			}
		}
	},
	mounted() {
		this.check_permission()
		this.loadPlanDetail()
		this.loadCaseList()
		this.loadModuleList()
		this.loadUserList()
		this.loadEnvList()
	},
	methods: {
		// 加载执行环境列表
		async loadEnvList() {
			const response = await this.$api.getEnvs({project: this.projectInfo.id})
			if (response.status === 200) {
				this.env_list = {...response.data}
			}
		},
		// 打开执行对话框
		run(obj) {
			// 检查是否有关联脚本用例
			const hasCaseDetail = obj.func_case_detail &&
				obj.func_case_detail.can_autoed !== 3 &&
				obj.func_case_detail.case_detail &&
				obj.func_case_detail.case_detail.length > 0

			if (!hasCaseDetail) {
				ElMessage.warning('该用例无关联脚本用例')
				return
			}

			this.runTimesVisible = true
			this.runCaseForm.case_id = obj.id
			this.$refs.runRef.resetFields()
		},
		// 执行测试用例
		caseRun() {
			this.$refs.runRef.validate((valid) => {
				if (valid) {
					const caseIds = this.selectedCases.length > 0 
						? this.selectedCases.map(item => item.func_case)
						: [this.runCaseForm.case_id]
					
					const params = {
						plan_id: this.$route.params.id,
						func_case_ids: caseIds,
						env_id: this.runCaseForm.env_id
					}
					this.$api.runPlanCaseAutomation(params).then(res => {
						if (res.status === 200) {
							this.runTimesVisible = false
							this.$message({
								message: res.data.message || '执行完成后自动更新该功能用例的执行结果',
								type: 'success'
							})
							this.loadCaseList()
						}
					}).catch(err => {
						this.$message({
							message: err.response?.data?.error || '执行失败',
							type: 'error'
						})
					})
				}
			})
		},
		async check_permission(){
			const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission['/exec/plan']}
			const response = await this.$api.check_permission(params)
			if (response.status === 200){
				this.permission = { ...response.data.result }
			}
		},
		...mapActions(['getRolePermission']),
		
		calculatePassRate() {
			if (this.total === 0) return 0
			return Math.round((this.passedCount / this.total) * 100)
		},

		getSegmentWidth(count, total) {
			if (total === 0) return '0%'
			return `${(count / total) * 100}%`
		},
		
		loadUserList() {
			api.getUsers().then(res => {
				if (res.status === 200) {
					this.userList = res.data.results || res.data || []
				}
			})
		},

		confirmModifyExecutor() {
			if (!this.batchForm.executed_by) {
				ElMessage.warning('请选择执行人')
				return
			}
			const user = this.userList.find(u => u.id === this.batchForm.executed_by)
			const planCaseIds = this.selectedCases.map(item => item.id)
			api.modifyExecutedBy(planCaseIds, {
				executed_by: this.batchForm.executed_by
			}).then(res => {
				if (res.status === 200) {
					ElMessage.success(`成功修改 ${this.selectedCases.length} 个用例的执行人`)
					this.selectedCases.forEach(item => {
						item.executed_by_name = user ? user.username : this.userInfo.name
					})
					this.executorDialogVisible = false
					this.loadCaseList()
				}
			})
		},

		confirmModifyResult() {
			if (!this.batchForm.exec_status) {
				ElMessage.warning('请选择测试结果')
				return
			}
			const statusName = this.getExecStatusName(this.batchForm.exec_status)
			const planCaseIds = this.selectedCases.map(item => item.id)
			api.modifyExecStatus(planCaseIds, {
				exec_status: this.batchForm.exec_status,
				executed_by: this.userInfo.id,
			}).then(res => {
				if (res.status === 200) {
					ElMessage.success(`成功将 ${this.selectedCases.length} 个用例标记为「${statusName}」`)
					this.resultDialogVisible = false
					this.loadPlanDetail()
					this.loadCaseList()
				}
			})
		},
		
		async loadModuleList() {
			const response = await api.getAllPlantModule({project: this.projectInfo.id})
			if (response.status === 200) {
				this.plant_module_list = response.data.results
			}
		},

		filterNode(value, data) {
			if (!value) return true
			return data.name.indexOf(value) !== -1
		},

		moduleSelect(node) {
			if (!node) {
				this.selectNode = null
				this.currentModuleId = null
				this.page = 1
				this.loadCaseList()
				return
			}
			// 如果点击的是已选中的节点，取消选中
			if (this.selectNode === node.id) {
				this.$refs.treeRef?.setCurrentKey(null)
				this.selectNode = null
				this.currentModuleId = null
				this.page = 1
				this.loadCaseList()
				return
			}
			this.selectNode = node.id
			if (this.includeChildren) {
				this.currentModuleId = this.getAllIds(node)
			} else {
				this.currentModuleId = node.id
			}
			this.page = 1
			this.loadCaseList()
		},
		
		getAllIds(node) {
			let ids = [node.id]
			if (node.children && node.children.length > 0) {
				node.children.forEach(child => {
					ids = ids.concat(this.getAllIds(child))
				})
			}
			return ids
		},
		
		onIncludeChildrenChange() {
			if (this.selectNode) {
				const node = this.$refs.treeRef?.getNode(this.selectNode)
				if (node && node.data) {
					if (this.includeChildren) {
						this.currentModuleId = this.getAllIds(node.data)
					} else {
						this.currentModuleId = node.data.id
					}
					this.page = 1
					this.loadCaseList()
				}
			}
		},

		expandAllNodes() {
			for (let x in this.$refs.treeRef.store._getAllNodes()) {
				this.$refs.treeRef.store._getAllNodes()[x].expanded = true
			}
		},

		collapseAllNodes() {
			for (let x in this.$refs.treeRef.store._getAllNodes()) {
				this.$refs.treeRef.store._getAllNodes()[x].expanded = false
			}
		},

		loadPlanDetail() {
			api.getPlan(this.planId).then(res => {
				if (res.status === 200) {
					this.planInfo = res.data
				}
			})
		},

		handleSearch() {
			this.page = 1
			this.loadCaseList()
		},

		handleReset() {
			this.filterParams = {
				name: '',
				exec_status: null,
				executed_by: null,
				added_by: null
			}
			this.page = 1
			this.loadCaseList()
		},

		handleBatchCommand(command) {
			switch(command) {
				case 'executor':
					this.openExecutorDialog()
					break
				case 'result':
					this.openResultDialog()
					break
				case 'run':
					this.openBatchRunDialog()
					break
				case 'remove':
					this.batchRemoveCases()
					break
			}
		},

		openExecutorDialog() {
			this.batchForm.executed_by = null
			this.executorDialogVisible = true
		},

		openResultDialog() {
			this.batchForm.exec_status = null
			this.resultDialogVisible = true
		},

		openBatchRunDialog() {
			this.runCaseForm.env_id = null
			this.runTimesVisible = true
		},

		loadCaseList() {
			this.loading = true
			const params = {
				page: this.page,
				size: this.size,
				test_plan: this.planId
			}
			if (this.currentModuleId) {
				if (Array.isArray(this.currentModuleId)) {
					params.module = this.currentModuleId.join(',')
				} else {
					params.module = this.currentModuleId
				}
			}
			if (this.filterParams.name) {
				params.func_case_name__icontains = this.filterParams.name
			}
			if (this.filterParams.exec_status) {
				params.exec_status = this.filterParams.exec_status
			}
			if (this.filterParams.executed_by) {
				params.executed_by = this.filterParams.executed_by
			}
			if (this.filterParams.added_by) {
				params.added_by = this.filterParams.added_by
			}
			api.getPlanCases(params).then(res => {
			if (res.status === 200) {
				this.tableData = res.data.results
				this.total = res.data.count
				this.existCaseIds = res.data.results.map(item => item.func_case)
				// @提及消息跳转携带 case_id 时自动打开用例详情抽屉
				if (this.pendingCaseId && !this.autoCaseOpened) {
					const target = this.tableData.find(item => String(item.id) === String(this.pendingCaseId))
					if (target) {
						this.autoCaseOpened = true
						this.pendingCaseId = null
						this.openCaseDetail(target)
					}
				}
			}
			this.loading = false
		}).catch(() => {
			this.loading = false
		})
	},

		handleSelectionChange(selection) {
			this.selectedCases = selection
		},

		openChooseCase() {
			this.chooseCaseVisible = true
		},

		addCasesToPlan(caseList) {
			const allCaseIds = caseList.map(item => item.id)
			const newCaseIds = allCaseIds.filter(id => !this.existCaseIds.includes(id))
			const duplicateCount = allCaseIds.length - newCaseIds.length
			
			if (newCaseIds.length === 0) {
				ElMessage.warning(`选中的 ${allCaseIds.length} 个用例已全部在计划中，无需重复添加`)
				this.chooseCaseVisible = false
				return
			}
			
			api.addFuncCasesToPlan(this.planId, { 
				func_case_ids: newCaseIds,
				executed_by: this.userInfo.user_id
			}).then(res => {
				if (res.status === 200) {
					if (duplicateCount > 0) {
						ElMessage.success(`成功添加 ${newCaseIds.length} 个用例（跳过 ${duplicateCount} 个已存在的用例）`)
					} else {
						ElMessage.success(`成功添加 ${newCaseIds.length} 个用例`)
					}
					this.chooseCaseVisible = false
					this.existCaseIds = [...this.existCaseIds, ...newCaseIds]
					this.loadPlanDetail()
					this.loadCaseList()
				}
			})
		},

		addSingleCase(caseItem) {
			if (this.existCaseIds.includes(caseItem.id)) {
				ElMessage.warning('该用例已在计划中，无需重复添加')
				this.chooseCaseVisible = false
				return
			}
			
			api.addFuncCasesToPlan(this.planId, { 
				func_case_ids: [caseItem.id],
				executed_by: this.userInfo.user_id 
			}).then(res => {
				if (res.status === 200) {
					ElMessage.success('成功添加 1 个用例')
					this.chooseCaseVisible = false
					this.existCaseIds = [...this.existCaseIds, caseItem.id]
					this.loadPlanDetail()
					this.loadCaseList()
				}
			})
		},

		batchRemoveCases() {
			ElMessageBox.confirm(
				`确定要移除选中的 ${this.selectedCases.length} 个用例吗？`,
				'提示',
				{
					confirmButtonText: '确定',
					cancelButtonText: '取消',
					type: 'warning'
				}
			).then(() => {
				const caseIds = this.selectedCases.map(item => item.func_case)
				api.removeFuncCasesFromPlan(this.planId, { func_case_ids: caseIds }).then(res => {
					if (res.status === 200) {
						ElMessage.success('批量移除成功')
						this.existCaseIds = this.existCaseIds.filter(id => !caseIds.includes(id))
						this.selectedCases = []
						this.loadPlanDetail()
						this.loadCaseList()
					}
				})
			}).catch(() => {})
		},





		updateExecStatus(row, status) {
			const params = {
				exec_status: status,
				executed_by: this.userInfo.id,
				executed_time: new Date().toISOString().replace('T', ' ').substring(0, 19),
				test_plan: row.test_plan,
				func_case: row.func_case
			}
			api.updatePlanCase(row.id, params).then(res => {
				if (res.status === 200) {
					ElMessage.success('状态更新成功')
					this.loadPlanDetail()
					this.loadCaseList()
				}
			})
		},

		openCaseDetail(row) {
		this.currentCase = { ...row }
		this.currentFuncCaseId = row.func_case
		this.caseDetailVisible = true
		// 同步 URL 的 case_id，便于刷新/分享/消息跳转定位
		if (String(this.$route.query.case_id) !== String(row.id)) {
			this.$router.replace({ query: { ...this.$route.query, case_id: row.id } }).catch(() => {})
		}
		// 切换用例时重置 Tab 与关联缺陷状态
		this.activeTab = 'comments'
		this.defectsList = []
		this.defectsLoaded = false
		this.loadCaseComments(row.id)
		this.$nextTick(() => {
			this.buildNavItems()
		})
	},
	onCaseDetailClosed() {
		// 关闭抽屉时清除 URL 中的 case_id
		const query = { ...this.$route.query }
		if (query.case_id) {
			delete query.case_id
			this.$router.replace({ query }).catch(() => {})
		}
	},

		buildNavItems() {
			const items = [
				{ id: 'section-basic', name: '基础信息' },
				{ id: 'section-precondition', name: '前置条件' },
				{ id: 'section-steps', name: '测试步骤' }
			]
			if (this.currentCase.func_case_detail && this.currentCase.func_case_detail.step_type === 1) {
				items.push({ id: 'section-expected', name: '预期结果' })
			}
			items.push({ id: 'section-remark', name: '备注信息' })
			if (this.currentCase.func_case_detail && 
				this.currentCase.func_case_detail.can_autoed !== 3 && 
				this.currentCase.func_case_detail.case_detail && 
				this.currentCase.func_case_detail.case_detail.length > 0) {
				items.push({ id: 'section-script', name: '关联用例' })
			}
			items.push({ id: 'section-comment', name: '执行动态' })
			this.navItems = items
		},

		loadCaseComments(testPlanFuncCaseId) {
			api.getPlanCaseComments({ test_plan_func_case: testPlanFuncCaseId }).then(res => {
				if (res.status === 200) {
					this.commentsList = res.data.results || []
				}
			})
		},

		// 切换 Tab：首次进入“关联缺陷”时懒加载
		handleTabChange(paneName) {
			if (paneName === 'defects' && !this.defectsLoaded && this.currentFuncCaseId) {
				this.loadAssociatedDefects()
			}
		},
		// 加载当前功能用例关联的缺陷（只读）
		loadAssociatedDefects() {
			this.defectsLoading = true
			this.defectsLoaded = true
			this.$api.getDefects({ func_case: this.currentFuncCaseId, size: 1000 }).then(res => {
				if (res.status === 200) {
					this.defectsList = res.data.results || []
				}
			}).finally(() => {
				this.defectsLoading = false
			})
		},
		// 新标签页打开缺陷详情
		goToDefectDetail(row) {
			const routeData = this.$router.resolve({ path: '/defect/list', query: { action: 'view', id: row.id } })
			window.open(routeData.href, '_blank')
		},
		// 缺陷序号
		defectIndexMethod(index) {
			return index + 1
		},
		// 处理人徽章颜色（与测试计划概览一致）
		getAssigneeClass(userId) {
			if (!userId) return 'assignee-none'
			const palette = ['assignee-1', 'assignee-2', 'assignee-3', 'assignee-4', 'assignee-5', 'assignee-6', 'assignee-7', 'assignee-8']
			const idx = (Number(userId) % palette.length + palette.length) % palette.length
			return palette[idx]
		},
		// 处理人下拉项指示点颜色（与 DefectList 一致）
		getIndicatorClassByUserId(userId) {
			if (!userId) return 'info'
			const palette = ['primary', 'purple', 'danger', 'success', 'cyan', 'warning', 'info', 'orange']
			const idx = (Number(userId) % palette.length + palette.length) % palette.length
			return palette[idx]
		},

		submitComment() {
		if (!this.newCommentContent.trim()) {
			ElMessage.warning('请输入评论内容')
			return
		}
		this.submittingComment = true
		const params = {
			test_plan_func_case: this.currentCase.id,
			content: this.newCommentContent,
			mentioned_users: this.extractMentionedIds(this.newCommentContent)
		}
		api.addPlanCaseComment(params).then(res => {
		if (res.status === 201) {
			ElMessage.success('评论发布成功')
			this.newCommentContent = ''
			this.loadCaseComments(this.currentCase.id)
		}
		this.submittingComment = false
	}).catch(() => {
		this.submittingComment = false
	})
},
	// 从评论HTML中解析被@提及的用户ID列表
	extractMentionedIds(html) {
		if (!html) return []
		const ids = new Set()
		try {
			const doc = new DOMParser().parseFromString(html, 'text/html')
			doc.querySelectorAll('.at-mention[data-user-id]').forEach(el => {
				const id = el.getAttribute('data-user-id')
				if (id) ids.add(Number(id))
			})
		} catch (e) {
			const re = /data-user-id="(\d+)"/g
			let m
			while ((m = re.exec(html)) !== null) ids.add(Number(m[1]))
		}
		return [...ids]
	},

		editComment(comment) {
			this.editingCommentId = comment.id
			this.editCommentContent = comment.content
		},

		saveCommentEdit(comment) {
			if (!this.editCommentContent.trim()) {
				ElMessage.warning('请输入评论内容')
				return
			}
			api.updatePlanCaseComment(comment.id, { content: this.editCommentContent }).then(res => {
				if (res.status === 200) {
					ElMessage.success('评论更新成功')
					this.editingCommentId = null
					this.editCommentContent = ''
					this.loadCaseComments(this.currentCase.id)
				}
			})
		},

		cancelCommentEdit() {
			this.editingCommentId = null
			this.editCommentContent = ''
		},

		canDeleteComment(comment) {
			const isPlanCreator = this.planInfo && this.planInfo.create_by === this.userInfo.user_id
			const isCommentAuthor = comment && comment.comment_by === this.userInfo.user_id
			return isPlanCreator || isCommentAuthor
		},

		async viewScriptCase(row) {
			console.log('查看脚本用例:', row)
			// 获取该脚本用例在当前计划中的最新执行日志
			const response = await this.$api.getCaseLogs({
				case: row.id,
				func_case: this.currentFuncCaseId,
				plan: this.planId,
				page: 1,
				size: 1
			})
			if (response.status === 200 && response.data.results && response.data.results.length > 0) {
				this.lookLogVisible = true
				this.one_case_log = { ...response.data.results[0] }
			} else {
				ElMessage.warning('暂无执行日志')
			}
		},

		deleteComment(comment) {
			ElMessageBox.confirm('确定要删除这条评论吗？', '提示', {
				confirmButtonText: '确定',
				cancelButtonText: '取消',
				type: 'warning'
			}).then(() => {
				api.deletePlanCaseComment(comment.id).then(res => {
					if (res.status === 204) {
						ElMessage.success('评论删除成功')
						this.loadCaseComments(this.currentCase.id)
					}
				})
			}).catch(() => {})
		},

		scrollToSection(sectionId) {
			this.activeSection = sectionId
			const element = document.getElementById(sectionId)
			if (element) {
				element.scrollIntoView({ behavior: 'smooth', block: 'start' })
			}
		},

		updateExecStatusDetail(status) {
			const params = {
				exec_status: status,
				executed_by: this.currentCase.executed_by || this.userInfo.id,
				executed_time: new Date().toISOString().replace('T', ' ').substring(0, 19)
			}
			api.updatePlanCase(this.currentCase.id, params).then(res => {
			if (res.status === 200) {
				ElMessage.success('执行状态更新成功')
				this.currentCase.exec_status = status
				this.currentCase.exec_status_name = this.getExecStatusName(status)
				this.currentCase.executed_time = params.executed_time
				this.loadCaseList()
			}
		})
		},

		updateExecutorDetail(userId) {
		const params = {
			executed_by: userId
		}
		api.updatePlanCase(this.currentCase.id, params).then(res => {
			if (res.status === 200) {
				ElMessage.success('执行人更新成功')
				this.currentCase.executed_by = userId
				const user = this.userList.find(u => u.id === userId)
				if (user) {
					this.currentCase.executed_by_name = user.username
				}
				this.loadCaseList()
			}
		})
	},

		copyCase() {
			navigator.clipboard.writeText(this.currentCase.func_case_name)
			ElMessage({message: '复制成功', type: 'success'})
		},

		getTagType(name) {
			const tagMap = {
				'P0': 'danger',
				'P1': 'warning',
				'P2': 'success',
				'P3': 'info'
			}
			return tagMap[name] || 'info'
		},

		getScriptCaseTagType(typeName) {
			const typeMap = {
				'API Case': 'primary',
				'Web Case': 'success',
				'App Case': 'warning'
			}
			return typeMap[typeName] || 'info'
		},

		getAutoTypeTagType(type) {
			const typeMap = {
				1: 'success',
				2: 'warning',
				3: 'info'
			}
			return typeMap[type] || 'info'
		},

		getAutoStatusTagType(status) {
			const statusMap = {
				0: 'info',
				1: 'primary',
				2: 'warning',
				3: 'success'
			}
			return statusMap[status] || 'info'
		},

		getAutoTypeTagClass(type) {
			return ''
		},

		getAutoStatusTagClass(status) {
			return ''
		},

		removeCase(row) {
			ElMessageBox.confirm(
				'确定要移除此用例吗？',
				'提示',
				{
					confirmButtonText: '确定',
					cancelButtonText: '取消',
					type: 'warning'
				}
			).then(() => {
				api.removeFuncCasesFromPlan(this.planId, { func_case_ids: [row.func_case] }).then(res => {
					if (res.status === 200) {
						ElMessage.success('用例移除成功')
						this.existCaseIds = this.existCaseIds.filter(id => id !== row.func_case)
						this.loadPlanDetail()
						this.loadCaseList()
					}
				})
			}).catch(() => {})
		},

		getStatusType(status) {
			switch(status) {
				case 1: return 'info'
				case 2: return 'warning'
				case 3: return 'success'
				case 4: return 'danger'
				default: return 'info'
			}
		},

		formatTime(time) {
			if (!time) return '-'
			return new Date(time).toLocaleString('zh-CN', {
				year: 'numeric',
				month: '2-digit',
				day: '2-digit',
				hour: '2-digit',
				minute: '2-digit',
				second: '2-digit'
			}).replace(/\//g, '-')
		},

		getPriorityType(level) {
			switch(level) {
				case 1: return 'danger'
				case 2: return 'warning'
				case 3: return 'primary'
				case 4: return 'info'
				default: return 'info'
			}
		},

		getExecStatusType(status) {
			switch(status) {
				case 1: return 'info'
				case 2: return 'warning'
				case 3: return 'success'
				case 4: return 'danger'
				case 5: return 'primary'
				default: return 'info'
			}
		},

		getTestResultType(result) {
			switch(result) {
				case 1: return 'success'
				case 2: return 'danger'
				case 3: return 'warning'
				default: return 'info'
			}
		},

		getTestResultName(result) {
			switch(result) {
				case 1: return '成功'
				case 2: return '失败'
				case 3: return '错误'
				default: return '未执行'
			}
		},

		getExecStatusName(status) {
				console.log('getExecStatusName called with status:', status)
				switch(status) {
					case 1: return '未执行'
					case 2: return '暂缓'
					case 3: return '已通过'
					case 4: return '未通过'
					case 5: return '进行中'
					default: return '未知'
				}
			},

		handleSizeChange(val) {
			this.size = val
			this.loadCaseList()
		},

		handleCurrentChange(val) {
			this.page = val
			this.loadCaseList()
		}
	},
	setup() {
		return {
			Plus,
		ArrowDown,
		Delete,
		Search,
		Expand,
		Fold,
		User,
		CircleCheck,
		Document,
		UserFilled,
		RefreshLeft,
		Setting,
		SuccessFilled,
		DocumentCopy
		}
	}
}
</script>

<style scoped>
.plan-detail-container {
	width: 100%;
	background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
	padding: 20px 15px 15px 15px;
	box-sizing: border-box;
	display: flex;
	gap: 20px;
	min-height: calc(100vh - 75px);
	height: calc(100vh - 75px);
	max-height: calc(100vh - 75px);
}

.elegant-shadow {
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06),
				0 1px 4px rgba(0, 0, 0, 0.08);
	transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.elegant-shadow:hover {
	box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1),
				0 2px 8px rgba(0, 0, 0, 0.12);
}

/* 侧边栏样式 - 与功能用例保持完全一致 */
.sidebar-card {
	width: 320px;
	flex-shrink: 0;
	background: var(--qm-bg-2);
	border: none;
	border-radius: 16px;
	overflow: hidden;
	display: flex;
	flex-direction: column;
}

.sidebar-header {
	padding: 20px 24px;
	border-bottom: 1px solid var(--qm-bg-3);
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.sidebar-title-wrapper {
	display: flex;
	align-items: center;
	gap: 12px;
}

.icon-tree {
	display: inline-block;
	width: 24px;
	height: 24px;
	background: linear-gradient(135deg, #10b981 0%, #059669 100%);
	border-radius: 8px;
	position: relative;
}

.icon-tree::before {
	content: '';
	position: absolute;
	top: 6px;
	left: 8px;
	width: 8px;
	height: 8px;
	background: var(--qm-bg-2);
	border-radius: 50%;
}

.icon-tree::after {
	content: '';
	position: absolute;
	top: 15px;
	left: 7px;
	width: 10px;
	height: 6px;
	background: var(--qm-bg-2);
	clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
}

.sidebar-title {
	margin: 0;
	font-size: 18px;
	font-weight: 600;
	color: var(--qm-text-1);
	flex: 1;
}

.sidebar-tag {
	font-weight: 500;
}

.sidebar-content {
	flex: 1;
	display: flex;
	flex-direction: column;
	min-height: 0;
}

.search-wrapper {
	padding: 16px 24px 0;
}

.tree-divider {
	margin: 16px 0;
	border-color: var(--qm-bg-3);
}

.tree-wrapper {
	flex: 1;
	padding: 0 20px;
	min-height: 0;
	overflow-y: auto;
}

.elegant-tree >>> .el-tree {
	background: transparent;
}

.elegant-tree >>> .el-tree-node__content {
	height: 40px;
	border-radius: 8px;
	margin-bottom: 4px;
	transition: all 0.3s ease;
}

.elegant-tree >>> .el-tree-node__content:hover {
	background: var(--qm-warning-soft);
}

.elegant-tree >>> .el-tree-node.is-current > .el-tree-node__content {
	background: var(--qm-warning-soft);
	position: relative;
}

.elegant-tree >>> .el-tree-node.is-current > .el-tree-node__content::before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	width: 4px;
	background: linear-gradient(180deg, #f59e0b 0%, #d97706 100%);
	border-radius: 0 2px 2px 0;
}

.custom-tree-node {
	display: flex;
	align-items: center;
	justify-content: space-between;
	width: 100%;
	padding-right: 8px;
	min-width: 0;
}

.node-content {
	display: flex;
	align-items: center;
	gap: 8px;
	flex: 1;
	overflow: hidden;
	min-width: 0;
	max-width: calc(100% - 40px);
}

.icon-folder-tree {
	width: 16px;
	height: 16px;
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z'/%3E%3C/svg%3E");
	background-size: contain;
	background-repeat: no-repeat;
	flex-shrink: 0;
}

.icon-folder-tree-root {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z'/%3E%3C/svg%3E");
}

.node-label {
	flex: 1;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	font-size: 14px;
	color: var(--qm-text-2);
	min-width: 0;
}

.tree-actions {
	padding: 0 24px 20px;
}

.tree-buttons {
	display: flex;
	gap: 12px;
}

.tree-btn {
	flex: 1;
	border-radius: 10px;
	border: 1px solid var(--qm-line-strong);
	background: var(--qm-bg-2);
	color: var(--qm-text-2);
	font-weight: 500;
	transition: all 0.3s ease;
}

.tree-btn:hover {
	background: var(--qm-bg-1);
	border-color: var(--qm-line-strong);
	transform: translateY(-1px);
}

.tree-btn .el-icon {
	margin-right: 6px;
	font-size: 14px;
}

/* 主内容区域 */
.main-content {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 20px;
	min-width: 0;
	overflow-y: auto;
}

.content-card {
	background: var(--qm-bg-2);
	border: none;
	border-radius: 8px;
	flex: 1;
	display: flex;
	flex-direction: column;
	overflow: hidden;
	box-shadow: 0 1px 10px rgba(0, 0, 0, 0.05);
	transition: all 0.2s ease;
}

.content-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20px 24px;
	border-bottom: 1px solid var(--qm-bg-3);
	flex-shrink: 0;
}

.header-left {
	display: flex;
	align-items: center;
	gap: 16px;
}

.content-title {
	font-size: 18px;
	font-weight: 600;
	color: var(--qm-text-1);
	margin: 0;
}

.selected-count {
	padding: 4px 12px;
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
	color: white;
	border-radius: 20px;
	font-size: 13px;
	font-weight: 500;
}

.header-right {
	display: flex;
	gap: 12px;
}

.add-btn {
	display: flex;
	align-items: center;
	gap: 6px;
	padding: 10px 20px;
	border-radius: 10px;
	font-weight: 500;
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
	border: none;
	box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
	transition: all 0.3s ease;
}

.add-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.add-btn .el-icon {
	transition: transform 0.3s ease;
}

.add-btn:hover .el-icon {
	transform: rotate(90deg);
}

.batch-remove-btn {
	display: flex;
	align-items: center;
	gap: 6px;
	padding: 10px 20px;
	border-radius: 10px;
	font-weight: 500;
	background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
	border: none;
}

.table-wrapper {
	flex: 1;
	padding: 0 0px;
	overflow-y: auto;
}

.elegant-table {
	width: 100%;
}

.elegant-table :deep(.el-table__header-wrapper) {
	border-radius: 8px 8px 0 0;
	overflow: hidden;
}

.elegant-table :deep(.el-table__header th) {
	background: var(--qm-bg-1);
	color: var(--qm-text-2);
	font-weight: 600;
	border-bottom: none;
	padding: 12px 0;
}

.elegant-table :deep(.el-table__body tr:hover > td) {
	background: var(--qm-bg-1);
}

.elegant-table :deep(.el-table__body td) {
	padding: 14px 0;
	border-bottom: 1px solid var(--qm-bg-3);
}

.index-cell {
	width: 32px;
	height: 32px;
	line-height: 32px;
	text-align: center;
	background: var(--qm-bg-3);
	border-radius: 6px;
	font-weight: 600;
	color: var(--qm-text-2);
	font-size: 13px;
	margin: 0 auto;
}

.case-link {
	font-weight: 500;
	font-size: 14px;
}

.pagination-wrapper {
	padding: 20px 24px 0px 24px;
	border-top: 1px solid var(--qm-bg-3);
	flex-shrink: 0;
	display: block !important;
	min-height: 40px;
	background: var(--qm-bg-2);
	float: right;
	z-index: 10;
	position: relative;
	opacity: 1 !important;
	visibility: visible !important;
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

.filter-card :deep(.el-card__body) {
	padding: 20px 20px 0 20px;
}

.filter-form-wrapper {
	padding: 25px 24px 0px 24px;
}

.filter-form {
	margin-bottom: 0;
}

.content-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20px 24px;
	border-bottom: 1px solid var(--qm-bg-3);
	flex-shrink: 0;
}

.content-title-section {
	display: flex;
	align-items: center;
	flex: 1;
}

.title-with-stats {
	display: flex;
	align-items: center;
	gap: 20px;
}

.selected-count-badge {
	display: flex;
	align-items: center;
	gap: 6px;
	padding: 6px 14px;
	background: linear-gradient(135deg, #10b981 0%, #059669 100%);
	color: white;
	border-radius: 20px;
	font-size: 13px;
	font-weight: 500;
	margin-right: 8px;
}

.selected-count-badge .el-icon {
	font-size: 14px;
}

.pass-rate-display {
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 0 8px;
}

.pass-rate-bar {
	flex: 1;
	min-width: 120px;
	height: 8px;
	background: var(--qm-bg-3);
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
	background: linear-gradient(90deg, var(--qm-text-3), var(--qm-text-2));
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

.pass-rate-text {
	font-size: 14px;
	font-weight: 600;
	color: var(--qm-text-1);
	min-width: 60px;
	text-align: right;
}

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
	color: var(--qm-text-3);
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
	color: #fbbf24;
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
}

.stat-label {
	font-size: 13px;
	color: var(--qm-text-2);
}

.stat-value {
	font-size: 18px;
	font-weight: 700;
	color: #f59e0b;
}

.stat-value.selected {
	color: #10b981;
}

.batch-dropdown {
	margin-right: 12px;
}

.batch-dropdown .toolbar-btn {
	display: flex;
	align-items: center;
	gap: 6px;
	padding: 10px 20px;
	border-radius: 10px !important;
	font-weight: 500 !important;
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
	border: none !important;
	color: white !important;
	box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3) !important;
	transition: all 0.3s ease !important;
}

.batch-dropdown .toolbar-btn:disabled {
	opacity: 0.5 !important;
	cursor: not-allowed;
	background: var(--qm-text-3) !important;
	box-shadow: none !important;
}

.batch-dropdown .toolbar-btn:hover:not(:disabled) {
	transform: translateY(-2px) !important;
	box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4) !important;
}

.batch-dropdown .toolbar-btn .el-icon {
	transition: transform 0.3s ease;
}

.batch-dropdown .toolbar-btn:hover:not(:disabled) .el-icon {
	transform: rotate(15deg);
}

.header-action-section {
	display: flex;
	align-items: center;
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
}

.dialog-confirm-btn {
	padding: 10px 24px;
	border-radius: 10px;
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
	border: none;
	font-weight: 500;
	transition: all 0.3s ease;
}

.dialog-confirm-btn:hover {
	box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.status-form {
	padding: 10px 0;
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
	.plan-detail-container {
		padding: 16px;
		flex-direction: column;
		height: auto;
		max-height: none;
		min-height: calc(100vh - 75px);
	}
	
	.sidebar-card {
		width: 100%;
		margin-bottom: 20px;
	}
	
	.plan-header {
		flex-direction: column;
		gap: 24px;
	}
	
	.plan-stats {
		width: 100%;
		justify-content: center;
	}
}

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

.user-name,
.time-text {
	font-size: 13px;
	color: var(--qm-text-2);
	font-weight: 400;
}

.status-tag {
	cursor: pointer;
	display: inline-flex;
	align-items: center;
	gap: 4px;
	padding-right: 6px;
}

.status-tag:hover {
	opacity: 0.85;
}

.status-tag .el-icon {
	font-size: 12px;
}

.case-tag-list {
	display: flex;
	flex-wrap: wrap;
	gap: 4px;
	justify-content: center;
}

.case-tag-badge {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	padding: 4px 10px;
	border-radius: 12px;
	font-size: 12px;
	font-weight: 500;
	background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
	color: white;
	line-height: 1.2;
	transition: all 0.2s ease;
}

.case-tag-badge:hover {
	transform: translateY(-1px);
	box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3);
}

.drawer-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: 100%;
	}

	:deep(.case-detail-drawer) {
		&.el-drawer.rtl {
			margin: 0;
			height: 100vh;
			width: 85vw !important;
			border-radius: 16px 0 0 16px;
			box-shadow: -8px 0 40px rgba(0, 0, 0, 0.15);
			border-left: 1px solid rgba(255, 255, 255, 0.8);
			background: linear-gradient(135deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
		}
		
		.el-drawer__body {
			padding: 0 !important;
			display: flex;
			flex-direction: column;
			height: 100%;
			overflow: hidden;
			position: relative;
			overflow-x: hidden;
			box-sizing: border-box;
			border-radius: 16px 0 0 16px;
		}
	}

	.detail-header {
		position: sticky;
		top: 0;
		z-index: 100;
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		padding: 24px 60px 24px 24px;
		box-sizing: border-box;
		background: linear-gradient(135deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
		border-bottom: 1px solid var(--qm-bg-3);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
		flex-shrink: 0;
	}

	.title-area {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.drawer-title {
		margin: 0;
		font-size: 20px;
		font-weight: 700;
		color: var(--qm-text-1);
		position: relative;
		padding-left: 16px;
	}
	
	.drawer-title::before {
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

	.copy-btn {
		padding: 6px;
	}

	.case-detail-container {
		display: flex;
		gap: 24px;
		padding: 24px;
		flex: 1;
		overflow-y: auto;
		overflow-x: hidden;
		background: var(--qm-bg-1);
		scrollbar-width: none;
		-ms-overflow-style: none;
		
		&::-webkit-scrollbar {
			display: none;
		}
	}

	.case-detail-main {
		flex: 1;
		min-width: 0;
	}

	.case-detail-sidebar {
		display: none;
		flex: 0 0 320px;
		max-width: 320px;
		box-sizing: border-box;
		padding-right: 40px;
	}

	.section-card {
		margin-bottom: 20px;
		border: none;
		border-radius: 8px;
		box-shadow: 0 1px 10px rgba(0, 0, 0, 0.05);
		transition: all 0.2s ease;
		
		&:hover {
			box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
		}
		
		:deep(.el-card__body) {
			padding: 24px 28px;
		}
	}

	.section-divider {
		display: flex;
		align-items: center;
		margin-bottom: 12px;
	}

	.section-title {
		font-size: 15px;
		font-weight: 600;
		color: var(--qm-text-1);
		position: relative;
		padding-left: 12px;
		
		&::before {
			content: '';
			position: absolute;
			left: 0;
			top: 50%;
			transform: translateY(-50%);
			width: 4px;
			height: 16px;
			background: linear-gradient(180deg, #f59e0b 0%, #66b1ff 100%);
			border-radius: 2px;
		}
	}

	.section-content {
		padding: 12px 0;
	}

	#section-basic .section-content {
		display: grid;
		grid-template-columns: repeat(6, 1fr);
		gap: 22px 16px;
	}
	#section-basic .section-content .el-row {
		display: contents;
	}
	#section-basic .section-content .el-col {
		max-width: none !important;
		flex: none !important;
		width: auto !important;
		padding-left: 0 !important;
		padding-right: 0 !important;
	}

	#section-basic .form-item {
		margin-bottom: 0;
		display: flex;
		flex-direction: column;
		justify-content: center;
		height: 100%;
		box-sizing: border-box;
		padding: 12px 10px;
		background: linear-gradient(180deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
		border: 1px solid var(--qm-line-strong);
		border-radius: 10px;
		transition: all 0.2s ease;
	}
	#section-basic .form-item:hover {
		border-color: #a5b4fc;
		box-shadow: 0 2px 10px rgba(245, 158, 11, 0.1);
		transform: translateY(-1px);
	}
	#section-basic .form-label {
		text-align: center;
		font-size: 12px;
		font-weight: 600;
		color: var(--qm-text-2);
		margin-bottom: 8px;
		letter-spacing: 0.5px;
	}
	#section-basic .form-value {
		text-align: center;
		font-size: 14px;
		font-weight: 600;
		color: #1f2937;
		line-height: 1.5;
		word-break: break-word;
	}

	/* 执行状态徽章：标题与卡片样式保持默认，仅居中显示带颜色的状态徽章 */
	#section-basic .exec-status-item {
		align-items: center;
	}
	#section-basic .exec-status-item .status-dropdown {
		justify-self: center;
	}
	#section-basic .exec-status-item .status-badge {
		justify-content: center;
	}

	/* 执行人徽章：同上，居中显示带颜色的处理人徽章 */
	#section-basic .executor-item {
		align-items: center;
	}
	#section-basic .executor-item .status-dropdown {
		justify-self: center;
	}
	#section-basic .executor-item .status-badge {
		justify-content: center;
	}

	.form-item {
		margin-bottom: 22px;
	}

	.form-label {
		display: block;
		font-size: 13px;
		font-weight: 600;
		color: var(--qm-text-1);
		margin-bottom: 6px;
	}

	.form-value {
		font-size: 14px;
		font-weight: 400;
		color: var(--qm-text-2);
		line-height: 1.5;
	}

	.tag-item {
		display: inline-flex;
		align-items: center;
		padding: 2px 10px;
		background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
		color: white;
		border-radius: 12px;
		font-size: 12px;
		margin-right: 6px;
	}

	.rich-content {
		padding: 12px 0;
	}

	.rich-text-view {
		min-height: 30px;
		line-height: 1.6;
		color: var(--qm-text-1);
		word-break: break-word;

		&:empty::before {
			content: attr(data-placeholder);
			color: var(--qm-text-3);
		}

		p {
			margin: 8px 0;
		}

		ul, ol {
			padding-left: 20px;
			margin: 8px 0;
		}

		li {
			margin: 4px 0;
		}

		strong {
			font-weight: 600;
		}

		em {
			font-style: italic;
		}

		u {
			text-decoration: underline;
		}

		s {
			text-decoration: line-through;
		}

		code {
			background: var(--qm-bg-1);
			padding: 2px 8px;
			border-radius: 4px;
			font-family: monospace;
			font-size: 14px;
		}

		pre {
			background: #1e1e1e;
			color: #d4d4d4;
			padding: 12px;
			border-radius: 6px;
			overflow-x: auto;
			margin: 8px 0;

			code {
				background: transparent;
				padding: 0;
				color: inherit;
			}
		}

		blockquote {
			border-left: 4px solid #e4e7ed;
			padding-left: 12px;
			margin: 8px 0;
			color: var(--qm-text-2);
			background: var(--qm-bg-1);
			padding: 8px 12px;
			border-radius: 0 4px 4px 0;
		}

		table {
			border-collapse: collapse;
			width: 100%;
			margin: 8px 0;

			td, th {
				border: 1px solid var(--qm-line-strong);
				padding: 8px 12px;
			}

			th {
				background: var(--qm-bg-1);
				font-weight: 600;
			}
		}

		a {
			color: #f59e0b;
			text-decoration: none;

			&:hover {
				text-decoration: underline;
			}
		}

		img {
			max-width: 100%;
			height: auto;
			border-radius: 4px;
			margin: 8px 0;
		}

		h1, h2, h3, h4, h5, h6 {
			margin: 16px 0 8px;
			font-weight: 600;
			line-height: 1.3;
		}

		h1 {
			font-size: 24px;
		}

		h2 {
			font-size: 20px;
		}

		h3 {
			font-size: 18px;
		}

		h4 {
			font-size: 16px;
		}

		h5, h6 {
			font-size: 14px;
		}
	}

	.steps-content {
		padding: 8px 0;
	}

	.elegant-table {
		width: 100%;
		border-collapse: separate;
		border-spacing: 0;
		background: transparent;
		border-radius: 8px;
		overflow: hidden;
		
		:deep(.el-table__header-wrapper th) {
			background: linear-gradient(180deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
			font-weight: 600;
			color: var(--qm-text-1);
			border-bottom: 1px solid var(--qm-line-strong);
			padding: 14px 0;
		}
		
		:deep(.el-table__header-wrapper .cell) {
			padding: 0 16px;
		}
		
		:deep(.el-table__body-wrapper .el-table__row) {
			transition: all 0.3s ease;
		}
		
		:deep(.el-table__body-wrapper .el-table__row:nth-child(even)) {
			background: var(--qm-bg-1);
		}
		
		:deep(.el-table__body-wrapper .el-table__row:hover) {
			background: var(--qm-warning-soft);
			transform: translateX(4px);
		}
		
		:deep(.el-table__body-wrapper td) {
			border-bottom: 1px solid var(--qm-bg-3);
			padding: 18px 0;
			transition: all 0.3s ease;
		}
		
		:deep(.el-table__body-wrapper .cell) {
			padding: 0 16px;
		}
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

	.case-info-cell {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
	}

	.case-type-badge {
		width: 100%;
		display: flex;
		justify-content: center;
	}

	.type-tag {
		padding: 4px 10px;
		border-radius: 12px;
		font-size: 12px;
		font-weight: 500;
		border-width: 1px;
	}

	.case-name {
		font-size: 14px;
		color: var(--qm-text-1);
		font-weight: 500;
	}

	.result-tag {
		padding: 4px 10px;
		border-radius: 10px;
		font-size: 12px;
		font-weight: 500;
	}

	.tags-container {
		display: flex;
		justify-content: center;
		flex-wrap: wrap;
		gap: 4px;
	}

	.case-tag {
		padding: 2px 8px;
		border-radius: 8px;
		font-size: 12px;
	}

	.user-time-cell {
		.user-info,
		.time-info {
			display: flex;
			align-items: center;
			justify-content: center;
			gap: 4px;
			font-size: 13px;
			color: var(--qm-text-2);
			margin-bottom: 4px;
			
			&:last-child {
				margin-bottom: 0;
			}
			
			.el-icon {
				font-size: 12px;
			}
		}
	}

	.run-stats-cell {
		.stats-row {
			display: flex;
			justify-content: center;
			gap: 12px;
			font-size: 12px;
			margin-bottom: 4px;
			
			&:last-child {
				margin-bottom: 0;
			}
		}
		
		.stat-item {
			&.success {
				color: #67c23a;
				font-weight: 500;
			}
			&.fail {
				color: #f56c6c;
				font-weight: 500;
			}
			&.error {
				color: #e6a23c;
				font-weight: 500;
			}
			&.total {
				color: #f59e0b;
				font-weight: 500;
			}
		}
	}

	.sidebar-card {
		border: none;
		border-radius: 8px;
		box-shadow: 0 1px 10px rgba(0, 0, 0, 0.05);
		transition: all 0.2s ease;
		
		&:hover {
			box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
		}
		
		:deep(.el-card__body) {
			padding: 20px 20px;
		}
	}

	.sidebar-content {
		padding: 8px 0;
	}

	.sidebar-item {
		margin-bottom: 24px;
	}

	.sidebar-label {
		display: block;
		font-size: 14px;
		font-weight: 500;
		color: var(--qm-text-2);
		margin-bottom: 8px;
	}

	.sidebar-value {
		font-size: 14px;
		color: var(--qm-text-1);
		line-height: 1.5;
	}



	.status-badge {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		padding: 6px 12px;
		border-radius: 20px;
		font-size: 13px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
		user-select: none;
	}

.status-badge:hover {
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.status-dot {
	width: 8px;
	height: 8px;
	border-radius: 50%;
	background: var(--qm-bg-2);
	opacity: 0.9;
}

.status-label {
	color: white;
	line-height: 1;
}

.auto-info-cell {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 4px;
}

.auto-type-tag,
.auto-status-tag {
	font-size: 12px;
	padding: 2px 8px;
	border-radius: 10px;
	font-weight: 500;
	white-space: nowrap;
}

.auto-type-tag {
	background: rgba(245, 158, 11, 0.1);
	color: #f59e0b;
}

.auto-status-tag {
	background: rgba(16, 185, 129, 0.1);
	color: #10b981;
}

.status-arrow {
	font-size: 12px;
	color: white;
	opacity: 0.8;
}

.status-1 {
	background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%);
}

.status-2 {
	background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

.status-3 {
	background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
}

.status-4 {
	background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
}

.status-5 {
	background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

.batch-dropdown {
	margin-left: 12px;
}

.batch-btn {
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
	color: white;
	border: none;
	padding: 8px 16px;
	border-radius: 8px;
	font-weight: 500;
	transition: all 0.2s ease;
}

.batch-btn:hover:not(:disabled) {
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.batch-btn:disabled {
	opacity: 0.5;
	cursor: not-allowed;
}

.filter-card {
	border-radius: 8px;
	border: none;
	margin-bottom: 0px;
	box-shadow: 0 1px 10px rgba(0, 0, 0, 0.05);
}

.inline-form {
	margin-bottom: 0;
}

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
	color: var(--qm-text-2);
	width: 90px;
	margin-right: 10px;
	flex-shrink: 0;
	white-space: nowrap;
}

.label-with-icon .el-icon {
	color: #f59e0b;
	font-size: 16px;
}

/* 筛选区小图标 */
.label-with-icon .icon-case-name,
.label-with-icon .icon-status,
.label-with-icon .icon-executor,
.label-with-icon .icon-creator {
	width: 16px;
	height: 16px;
	display: inline-block;
	flex-shrink: 0;
	border-radius: 4px;
}

.label-with-icon .icon-case-name { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.label-with-icon .icon-status { background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); }
.label-with-icon .icon-executor { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.label-with-icon .icon-creator { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }

.label-text {
	white-space: nowrap;
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

.batch-dropdown :deep(.el-dropdown) {
	display: inline-flex;
}

.batch-dropdown :deep(.el-dropdown-menu) {
	padding: 8px;
	border-radius: 12px;
	box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
	border: 1px solid var(--qm-bg-3);
}

.batch-dropdown :deep(.el-dropdown-menu__item) {
	padding: 10px 16px;
	margin: 2px 0;
	border-radius: 8px;
	font-size: 14px;
	font-weight: 500;
	color: var(--qm-text-2);
	display: flex;
	align-items: center;
	gap: 10px;
	transition: all 0.2s ease;
}

.batch-dropdown :deep(.el-dropdown-menu__item:hover) {
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
	color: white;
	transform: translateX(2px);
}

.batch-dropdown :deep(.el-dropdown-menu__item .el-icon) {
	font-size: 16px;
}

.batch-dropdown :deep(.el-dropdown-menu__item--divided) {
	border-top: 1px solid var(--qm-line-strong);
	margin-top: 6px;
	padding-top: 12px;
}

.batch-dropdown :deep(.el-dropdown-menu__item--divided:hover) {
	border-color: transparent;
}

.batch-dropdown .toolbar-btn {
	display: flex;
	align-items: center;
	gap: 6px;
}

.batch-form .el-form-item {
	margin-bottom: 24px;
}

.result-radio {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 10px 16px;
	margin-right: 16px;
	border-radius: 8px;
	border: 2px solid var(--qm-line-strong);
	transition: all 0.2s ease;
}

.result-radio.is-active {
	border-color: #f59e0b;
	background: rgba(245, 158, 11, 0.05);
}

.radio-dot {
	width: 12px;
	height: 12px;
	border-radius: 50%;
}

.radio-dot.warning {
	background: #f59e0b;
}

.radio-dot.primary {
	background: #f59e0b;
}

.radio-dot.success {
	background: #10b981;
}

.radio-dot.danger {
	background: #ef4444;
}

.radio-label {
	font-size: 14px;
	font-weight: 500;
	color: var(--qm-text-2);
}

.tree-wrapper::-webkit-scrollbar {
  width: 6px;
}

.tree-wrapper::-webkit-scrollbar-track {
  background: var(--qm-bg-1);
  border-radius: 4px;
}

.tree-wrapper::-webkit-scrollbar-thumb {
  background: var(--qm-line-strong);
  border-radius: 4px;
}

.tree-wrapper::-webkit-scrollbar-thumb:hover {
  background: var(--qm-line-strong);
}

html body .el-radio-group.include-children-radio .el-radio-button.is-active .el-radio-button__inner {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
  color: #ffffff !important;
  border-color: #10b981 !important;
  box-shadow: -1px 0 0 0 #10b981 !important;
}

html body .el-radio-group.include-children-radio .el-radio-button:first-child .el-radio-button__inner {
  border-radius: 6px 0 0 6px !important;
}

html body .el-radio-group.include-children-radio .el-radio-button:last-child .el-radio-button__inner {
  border-radius: 0 6px 6px 0 !important;
}

html body .el-radio-group.include-children-radio .el-radio-button__inner {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 0 !important;
  border: 1px solid var(--qm-line-strong) !important;
  background: var(--qm-bg-2);
  color: var(--qm-text-2);
  transition: all 0.3s ease;
}
</style>

<style>
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
	width: 12px;
	height: 12px;
	border-radius: 50%;
	flex-shrink: 0;
}

.status-dropdown-popper .status-indicator.warning {
	background: #f59e0b;
}

.status-dropdown-popper .status-indicator.primary {
	background: #f59e0b;
}

.status-dropdown-popper .status-indicator.success {
	background: #10b981;
}

.status-dropdown-popper .status-indicator.danger {
	background: #ef4444;
}

.status-dropdown-popper .status-text {
	font-size: 14px;
	font-weight: 500;
	color: var(--qm-text-2);
}

/* 执行人下拉菜单（用户多时支持滚动） */
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

/* 基础信息中执行人徽章颜色（与缺陷表一致，全局生效） */
#section-basic .assignee-none { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }
#section-basic .assignee-1 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
#section-basic .assignee-2 { background: linear-gradient(135deg, #a78bfa 0%, #f97316 100%); }
#section-basic .assignee-3 { background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%); }
#section-basic .assignee-4 { background: linear-gradient(135deg, #fb7185 0%, #e11d48 100%); }
#section-basic .assignee-5 { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); }
#section-basic .assignee-6 { background: linear-gradient(135deg, #22d3ee 0%, #d97706 100%); }
#section-basic .assignee-7 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
#section-basic .assignee-8 { background: linear-gradient(135deg, #fb923c 0%, #ea580c 100%); }

.batch-dropdown-popper.el-popper {
	padding: 12px !important;
	border-radius: 12px !important;
	border: none !important;
	box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12) !important;
	background: var(--qm-bg-2) !important;
	width: auto !important;
}

.batch-dropdown-popper .el-dropdown-menu {
	border: none !important;
	box-shadow: none !important;
	padding: 0 !important;
	background: transparent !important;
	width: 100% !important;
}

.batch-dropdown-popper .el-dropdown-menu__item {
	padding: 0 !important;
	margin: 0 !important;
	border-radius: 8px !important;
	overflow: hidden;
	padding-bottom: 12px !important;
	margin-bottom: 12px !important;
	border-bottom: 1px solid var(--qm-bg-3) !important;
}

.batch-dropdown-popper .el-dropdown-menu__item:last-child {
	padding-bottom: 0 !important;
	margin-bottom: 0 !important;
	border-bottom: none !important;
}

.batch-dropdown-popper .el-dropdown-menu__item--divided {
	border-top: 1px solid var(--qm-bg-3) !important;
	margin: 8px 0 4px 0 !important;
	padding-top: 8px !important;
}

.batch-dropdown-item {
	display: block !important;
	width: 100% !important;
	padding: 14px 20px !important;
	transition: all 0.2s ease !important;
	border-radius: 8px !important;
	white-space: nowrap;
	line-height: 1.5;
}

.batch-dropdown-item:hover {
	background: var(--qm-warning-soft) !important;
}

.item-text {
	font-size: 14px;
	font-weight: 500;
	color: var(--qm-text-2);
	transition: all 0.2s ease;
}

.batch-dropdown-item:hover .item-text {
	color: #f59e0b;
}

.dynamic-tabs .el-tabs__header {
	margin: 0 0 0 -10px;
	padding: 0;
	background: var(--qm-bg-2);
	border-bottom: 1px solid var(--qm-line-strong);
	overflow: visible !important;
}

.dynamic-tabs .el-tabs__nav-wrap {
	overflow: visible !important;
}

.dynamic-tabs .el-tabs__nav-scroll {
	overflow: visible !important;
}

.dynamic-tabs .el-tabs__nav-wrap::after {
	display: none;
}

.dynamic-tabs .el-tabs__active-bar {
	display: none;
}

.dynamic-tabs .el-tabs__item {
	position: relative;
	font-size: 16px;
	font-weight: 600;
	color: var(--qm-text-2);
	padding: 0;
	margin: 0 16px;
	height: 48px;
	line-height: 48px;
	transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.dynamic-tabs .el-tabs__item:first-child {
	margin-left: 0;
}

.dynamic-tabs .el-tabs__item::after {
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

.dynamic-tabs .el-tabs__item:hover {
	color: #f59e0b;
}

.dynamic-tabs .el-tabs__item:hover::after {
	width: 100%;
	background: rgba(245, 158, 11, 0.5);
}

.dynamic-tabs .el-tabs__item.is-active {
	color: #f59e0b;
	font-weight: 600;
}

.dynamic-tabs .el-tabs__item.is-active::after {
	width: 100%;
	background: #f59e0b;
}

.dynamic-tabs .el-tabs__content {
	flex: 1;
	padding: 0;
	display: flex;
	flex-direction: column;
	min-height: 0;
}

.comments-container {
	padding: 4px 0;
}

.defects-container {
	padding: 4px 0;
}

.defects-table {
	width: 100%;
	border-collapse: separate;
	border-spacing: 0;
}

.defects-table :deep(th.el-table__cell) {
	background: linear-gradient(180deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
	font-weight: 600;
	color: var(--qm-text-1);
	border-bottom: 1px solid var(--qm-line-strong);
}

.defects-table :deep(tr:nth-child(even)) {
	background: var(--qm-bg-1);
}

.defects-table :deep(tr:hover > td.el-table__cell) {
	background: var(--qm-warning-soft);
}

.defects-table :deep(.el-link) {
	font-weight: 500;
}

/* 只读徽章：去除下拉交互态 */
.defects-table .status-badge {
	cursor: default;
}

.defects-table .status-badge:hover {
	transform: none;
	box-shadow: none;
}

/* 严重程度颜色 */
.defects-table .severity-1 { background: linear-gradient(135deg, #f87171 0%, #ef4444 100%); }
.defects-table .severity-2 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.defects-table .severity-3 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.defects-table .severity-4 { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }

/* 优先级颜色 */
.defects-table .priority-1 { background: linear-gradient(135deg, #f87171 0%, #ef4444 100%); }
.defects-table .priority-2 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.defects-table .priority-3 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.defects-table .priority-4 { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }

/* BUG类型颜色 */
.defects-table .defect-type-1 { background: linear-gradient(135deg, #a78bfa 0%, #f97316 100%); }
.defects-table .defect-type-2 { background: linear-gradient(135deg, #22d3ee 0%, #d97706 100%); }
.defects-table .defect-type-3 { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }
.defects-table .defect-type-4 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.defects-table .defect-type-5 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.defects-table .defect-type-6 { background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%); }
.defects-table .defect-type-7 { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); }

/* 状态颜色 */
.defects-table .defect-status-1 { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }
.defects-table .defect-status-2 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.defects-table .defect-status-3 { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); }
.defects-table .defect-status-4 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }

/* 处理人颜色 */
.defects-table .assignee-none { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }
.defects-table .assignee-1 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.defects-table .assignee-2 { background: linear-gradient(135deg, #a78bfa 0%, #f97316 100%); }
.defects-table .assignee-3 { background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%); }
.defects-table .assignee-4 { background: linear-gradient(135deg, #fb7185 0%, #e11d48 100%); }
.defects-table .assignee-5 { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); }
.defects-table .assignee-6 { background: linear-gradient(135deg, #22d3ee 0%, #d97706 100%); }
.defects-table .assignee-7 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.defects-table .assignee-8 { background: linear-gradient(135deg, #fb923c 0%, #ea580c 100%); }

.comment-input-area {
	margin-bottom: 24px;
	padding: 20px;
	background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
	border-radius: 12px;
	border: 1px solid var(--qm-line-strong);
}

.comment-actions {
	display: flex;
	justify-content: flex-end;
	gap: 8px;
	margin-top: 12px;
}

/* 发布评论按钮 - 绿色渐变（与 DefectList 保持一致） */
.publish-comment-btn {
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
.publish-comment-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}
.publish-comment-btn .el-icon {
	margin-right: 8px;
	font-size: 16px;
}

/* 评论中@提及用户的渲染样式 */
.rich-text-view .at-mention,
.edit-comment-area .at-mention {
	display: inline-flex;
	align-items: center;
	padding: 1px 8px;
	margin: 0 2px;
	background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
	color: #fff;
	border-radius: 10px;
	font-size: 13px;
	font-weight: 600;
	line-height: 1.6;
	user-select: none;
}

.comments-list {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.comment-item {
	padding: 16px 20px;
	background: var(--qm-bg-2);
	border-radius: 12px;
	border: 1px solid var(--qm-bg-3);
	transition: all 0.2s ease;

	&:hover {
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
		border-color: var(--qm-line-strong);
	}
}

.comment-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 12px;
}

.comment-user {
	display: flex;
	align-items: center;
	gap: 10px;
}

.user-avatar {
	background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
	color: white;
	font-weight: 600;
	border: 2px solid white;
	box-shadow: 0 2px 8px rgba(245, 158, 11, 0.2);
}

.user-name {
	font-size: 14px;
	font-weight: 600;
	color: var(--qm-text-2);
}

.comment-time {
	font-size: 12px;
	color: var(--qm-text-3);
}

.comment-content {
	padding-left: 42px;
	line-height: 1.6;
	color: var(--qm-text-2);
}

.comment-actions-right {
	display: flex;
	align-items: center;
	gap: 12px;
}

.comment-actions-btns {
	display: flex;
	align-items: center;
	gap: 4px;
}

.comment-actions-btns .el-button {
	padding: 0;
	min-width: auto;
}

.delete-btn {
	color: #ef4444 !important;
}

.delete-btn:hover {
	color: #dc2626 !important;
}

.edit-comment-area {
	margin-top: 8px;
}

.edit-actions {
	display: flex;
	justify-content: flex-end;
	gap: 8px;
	margin-top: 12px;
}

.detail-nav-wrapper {
	position: fixed;
	left: calc(15vw - 70px);
	top: 0;
	width: 70px;
	z-index: 1000;
}

.vertical-nav {
	background: var(--qm-bg-2);
	border-radius: 12px;
	padding: 4px 0;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
	border: 1px solid var(--qm-bg-3);
	overflow: hidden;
}

.nav-item {
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 7px 8px;
	font-size: 11px;
	font-weight: 500;
	color: var(--qm-text-2);
	cursor: pointer;
	transition: all 0.2s ease;
	position: relative;
	text-align: center;
	line-height: 1.3;

	&:hover {
		color: #f59e0b;
		background: rgba(245, 158, 11, 0.05);
	}

	&.active {
		color: #f59e0b;
		font-weight: 600;
		background: linear-gradient(90deg, rgba(245, 158, 11, 0.08) 0%, transparent 100%);

		&::before {
			content: '';
			position: absolute;
			left: 0;
			top: 50%;
			transform: translateY(-50%);
			width: 3px;
			height: 60%;
			background: linear-gradient(180deg, #f59e0b 0%, #f97316 100%);
			border-radius: 0 2px 2px 0;
		}
	}
}

.nav-text {
	line-height: 1.4;
}

.icon-exec {
	width: 16px;
	height: 16px;
	display: inline-block;
	background-size: contain;
	background-repeat: no-repeat;
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' d='M8 5v14l11-7z'/%3E%3C/svg%3E");
}

.exec-btn {
	width: 36px;
	height: 36px;
	display: flex;
	align-items: center;
	justify-content: center;
}

/* 操作按钮 */
.action-buttons {
	display: flex;
	align-items: center;
	gap: 8px;
}

.action-btn {
	width: 36px;
	height: 36px;
	transition: all 0.2s ease;
}

.action-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.run-btn {
	background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
	border-color: #f59e0b;
}

.run-btn:hover {
	background: linear-gradient(135deg, #ea580c 0%, #f59e0b 100%);
	border-color: #ea580c;
}
</style>
