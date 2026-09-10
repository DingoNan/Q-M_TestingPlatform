<template>
	<div class="defect-list">
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
						size="large"
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
						node-key="id"
						:indent="10"
						:expand-on-click-node="false"
						@node-click="moduleSelect"
						:current-node-key="selectNode"
						:filter-node-method="filterNode"
						:data="plant_module_list"
						:props="{label: 'name'}"
						class="elegant-tree"
					>
						<template #empty>
						<div class="empty-tree">
							<el-empty description="暂无产品数据" :image-size="100">
								<template #description>
									<div style="margin-bottom: 10px;">暂无产品数据</div>
									<el-button
										type="primary"
										@click="goToCreatePlant"
										class="add-btn"
									>
										<el-icon><Plus /></el-icon>去新建产品
									</el-button>
								</template>
							</el-empty>
						</div>
					</template>
					<template #default="{ node, data }">
							<div class="custom-tree-node">
								<div class="node-content">
									<i class="icon-folder-tree" :class="{ 'icon-folder-tree-root': data.id < 0 }"></i>
									<el-tooltip :content="node.label" :show-after="500">
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
						<el-button @click="expandAllNodes" class="tree-btn" type="success">
							<el-icon><Expand /></el-icon>全部展开
						</el-button>
						<el-button @click="collapseAllNodes" class="tree-btn">
							<el-icon><Fold /></el-icon>全部折叠
						</el-button>
					</div>
				</div>
			</div>
		</div>

		<!-- 右侧主要内容区域 -->
		<div class="main-content">
			<!-- 搜索筛选区域 -->
			<el-card class="filter-card elegant-shadow">
				<div class="filter-header">
					<div class="header-title-section">
						<i class="icon-search"></i>
						<h3 class="filter-title">缺陷筛选</h3>
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
					<el-form :model="defectSearch" class="filter-form inline-form">
						<el-row :gutter="24">
							<el-col :xs="24" :sm="12" :md="8" :lg="6">
								<el-form-item class="inline-form-item">
									<div class="inline-label-wrapper">
										<i class="icon-title"></i>
										<span class="inline-label-text">标题</span>
									</div>
									<el-input v-model="defectSearch.title" placeholder="请输入缺陷标题" clearable size='large' class="input" />
								</el-form-item>
							</el-col>

							<el-col :xs="24" :sm="12" :md="8" :lg="6">
								<el-form-item class="inline-form-item">
									<div class="inline-label-wrapper">
										<i class="icon-severity"></i>
										<span class="inline-label-text">严重程度</span>
									</div>
									<el-select v-model="defectSearch.severity" placeholder="请选择" clearable filterable size='large' class="select" popper-class='select-dropdown-rounded'>
										<el-option v-for="item in severityOptions" :key="item.value" :label="item.label" :value="item.value" />
									</el-select>
								</el-form-item>
							</el-col>

							<el-col :xs="24" :sm="12" :md="8" :lg="6">
								<el-form-item class="inline-form-item">
									<div class="inline-label-wrapper">
										<i class="icon-priority"></i>
										<span class="inline-label-text">优先级</span>
									</div>
									<el-select v-model="defectSearch.priority" placeholder="请选择" clearable filterable size='large' class="select" popper-class='select-dropdown-rounded'>
										<el-option v-for="item in priorityOptions" :key="item.value" :label="item.label" :value="item.value" />
									</el-select>
								</el-form-item>
							</el-col>

							<el-col :xs="24" :sm="12" :md="8" :lg="6">
								<el-form-item class="inline-form-item">
									<div class="inline-label-wrapper">
										<i class="icon-type"></i>
										<span class="inline-label-text">BUG类型</span>
									</div>
									<el-select v-model="defectSearch.defect_type" placeholder="请选择" clearable filterable size='large' class="select" popper-class='select-dropdown-rounded'>
										<el-option v-for="item in defectTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
									</el-select>
								</el-form-item>
							</el-col>

							<el-col :xs="24" :sm="12" :md="8" :lg="6">
								<el-form-item class="inline-form-item">
									<div class="inline-label-wrapper">
										<i class="icon-status"></i>
										<span class="inline-label-text">状态</span>
									</div>
									<el-select v-model="defectSearch.status" placeholder="请选择" clearable filterable size='large' class="select" popper-class='select-dropdown-rounded'>
										<el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
									</el-select>
								</el-form-item>
							</el-col>

							<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="inline-form-item">
								<div class="inline-label-wrapper">
									<i class="icon-user"></i>
									<span class="inline-label-text">处理人</span>
								</div>
								<el-select v-model="defectSearch.assignee" placeholder="请选择" clearable filterable size='large' class="select" popper-class='select-dropdown-rounded'>
									<el-option v-for="user_obj in user_list" :key="user_obj.id" :label="user_obj.username" :value="user_obj.id" />
								</el-select>
							</el-form-item>
						</el-col>

						<el-col :xs="24" :sm="12" :md="8" :lg="6">
							<el-form-item class="inline-form-item">
								<div class="inline-label-wrapper">
									<i class="icon-user"></i>
									<span class="inline-label-text">测试计划</span>
								</div>
								<el-select v-model="defectSearch.plan" placeholder="请选择" clearable filterable size='large' class="select" popper-class='select-dropdown-rounded'>
									<el-option v-for="plan in planList" :key="plan.id" :label="plan.name" :value="plan.id" />
								</el-select>
							</el-form-item>
						</el-col>
						</el-row>
					</el-form>
				</div>
			</el-card>

			<!-- 缺陷列表区域 -->
			<el-card class="content-card elegant-shadow">
				<div class="content-header">
					<div class="content-title-section">
						<div class="title-with-stats">
							<h3 class="content-title">缺陷列表</h3>
							<div class="stats-info">
								<div class="stat-item">
									<span class="stat-label">总计</span>
									<span class="stat-value">{{ defect_list.count || 0 }}</span>
								</div>
							</div>
						</div>
					</div>
					<div class="header-action-section">
					<el-button type="primary" v-if="permission.has_add_permission" @click="openCreateDialog" class="add-btn">
						<el-icon><Plus /></el-icon>新增缺陷
					</el-button>
					<el-button type="danger" v-if="permission.has_delete_permission" :disabled="multipleSelection.length === 0" @click="batchDeleteDefects" class="batch-delete-btn">
						<el-icon><Delete /></el-icon>批量删除
					</el-button>
				</div>
				</div>

				<!-- 数据表格 -->
				<div class="table-wrapper">
					<el-table
						:max-height="'calc(100vh - 580px)'"
						:data="defect_list.results"
						class="elegant-table"
						:show-overflow-tooltip='true'
						:default-sort="{ prop: 'create_time', order: 'descending' }"
						@selection-change="handleSelectionChange"
						@sort-change="handleSortChange"
					>
						<el-table-column v-if="permission.has_delete_permission" type="selection" width="55" align="center" />

						<el-table-column label="标题" prop="title" min-width="200" align="center">
							<template #default="scope">
								<el-link v-if="permission.has_read_permission" type="primary" @click="viewDefectDetail(scope.row)">{{ scope.row.title }}</el-link>
								<span v-else>{{ scope.row.title }}</span>
							</template>
						</el-table-column>

						<el-table-column label="所属测试计划" prop="plan_name" width="180" align="center">
							<template #default="scope">
								<el-dropdown
									v-if="permission.has_edit_permission"
									trigger="click"
									@command="(val) => updateSingleField(scope.row, 'plan', val)"
									class="status-dropdown"
									popper-class="assignee-dropdown-popper"
								>
									<span class="status-badge" :class="getPlanClass(scope.row.plan)">
										<span class="status-dot"></span>
										<span class="status-label">{{ scope.row.plan_name || '未关联' }}</span>
										<el-icon class="status-arrow"><ArrowDown /></el-icon>
									</span>
									<template #dropdown>
										<el-dropdown-menu>
											<el-dropdown-item v-for="plan in planList" :key="plan.id" :command="plan.id" class="status-dropdown-item">
												<span class="status-indicator" :class="getIndicatorClassByUserId(plan.id)"></span>
												<span class="status-text">{{ plan.name }}</span>
											</el-dropdown-item>
											<el-dropdown-item v-if="scope.row.plan" :command="null" divided class="status-dropdown-item">
												<span class="status-indicator info"></span>
												<span class="status-text">取消关联</span>
											</el-dropdown-item>
										</el-dropdown-menu>
									</template>
								</el-dropdown>
								<span v-else class="status-badge-static" :class="getPlanClass(scope.row.plan)">
									{{ scope.row.plan_name || '-' }}
								</span>
							</template>
						</el-table-column>

						<el-table-column label="严重程度" prop="severity" width="130" align="center" sortable="custom">
							<template #default="scope">
								<el-dropdown
									v-if="permission.has_edit_permission"
									trigger="click"
									@command="(val) => updateSingleField(scope.row, 'severity', val)"
									class="status-dropdown"
									popper-class="status-dropdown-popper"
								>
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
								<span v-else class="status-badge-static" :class="'severity-' + scope.row.severity">
									{{ scope.row.severity_name || '-' }}
								</span>
							</template>
						</el-table-column>

						<el-table-column label="优先级" prop="priority" width="120" align="center" sortable="custom">
							<template #default="scope">
								<el-dropdown
									v-if="permission.has_edit_permission"
									trigger="click"
									@command="(val) => updateSingleField(scope.row, 'priority', val)"
									class="status-dropdown"
									popper-class="status-dropdown-popper"
								>
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
								<span v-else class="status-badge-static" :class="'priority-' + scope.row.priority">
									{{ scope.row.priority_name || '-' }}
								</span>
							</template>
						</el-table-column>

						<el-table-column label="BUG类型" prop="defect_type" width="150" align="center" sortable="custom">
							<template #default="scope">
								<el-dropdown
									v-if="permission.has_edit_permission"
									trigger="click"
									@command="(val) => updateSingleField(scope.row, 'defect_type', val)"
									class="status-dropdown"
									popper-class="status-dropdown-popper"
								>
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
								<span v-else class="status-badge-static" :class="'defect-type-' + scope.row.defect_type">
									{{ scope.row.defect_type_name || '-' }}
								</span>
							</template>
						</el-table-column>

						<el-table-column label="状态" prop="status" width="120" align="center" sortable="custom">
							<template #default="scope">
								<el-dropdown
									v-if="permission.has_edit_permission"
									trigger="click"
									@command="(val) => updateSingleField(scope.row, 'status', val)"
									class="status-dropdown"
									popper-class="status-dropdown-popper"
								>
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
								<span v-else class="status-badge-static" :class="'defect-status-' + scope.row.status">
									{{ scope.row.status_name || '-' }}
								</span>
							</template>
						</el-table-column>

					<el-table-column label="负责人" prop="owner_name" width="180" align="center" sortable="custom">
						<template #default="scope">
							<el-dropdown
								v-if="permission.has_edit_permission"
								trigger="click"
								@command="(val) => updateSingleField(scope.row, 'owner', val)"
								class="status-dropdown"
								popper-class="assignee-dropdown-popper"
							>
								<span class="status-badge" :class="getAssigneeClass(scope.row.owner)">
									<span class="status-dot"></span>
									<span class="status-label">{{ scope.row.owner_name || '未分配' }}</span>
									<el-icon class="status-arrow"><ArrowDown /></el-icon>
								</span>
								<template #dropdown>
									<el-dropdown-menu>
										<el-dropdown-item v-for="user_obj in user_list" :key="user_obj.id" :command="user_obj.id" class="status-dropdown-item">
											<span class="status-indicator" :class="getIndicatorClassByUserId(user_obj.id)"></span>
											<span class="status-text">{{ user_obj.username }}</span>
										</el-dropdown-item>
									</el-dropdown-menu>
								</template>
							</el-dropdown>
							<span v-else class="status-badge-static" :class="getAssigneeClass(scope.row.owner)">
								{{ scope.row.owner_name || '-' }}
							</span>
						</template>
					</el-table-column>

					<el-table-column label="处理人" prop="assignee_name" width="180" align="center" sortable="custom">
							<template #default="scope">
								<el-dropdown
									v-if="permission.has_edit_permission"
									trigger="click"
									@command="(val) => updateSingleField(scope.row, 'assignee', val)"
									class="status-dropdown"
									popper-class="assignee-dropdown-popper"
								>
									<span class="status-badge" :class="getAssigneeClass(scope.row.assignee)">
										<span class="status-dot"></span>
										<span class="status-label">{{ scope.row.assignee_name || '未分配' }}</span>
										<el-icon class="status-arrow"><ArrowDown /></el-icon>
									</span>
									<template #dropdown>
										<el-dropdown-menu>
											<el-dropdown-item v-for="user_obj in user_list" :key="user_obj.id" :command="user_obj.id" class="status-dropdown-item">
												<span class="status-indicator" :class="getIndicatorClassByUserId(user_obj.id)"></span>
												<span class="status-text">{{ user_obj.username }}</span>
											</el-dropdown-item>
										</el-dropdown-menu>
									</template>
								</el-dropdown>
								<span v-else class="status-badge-static" :class="getAssigneeClass(scope.row.assignee)">
									{{ scope.row.assignee_name || '-' }}
								</span>
							</template>
						</el-table-column>

				<!-- 合并列：创建信息 -->
					<el-table-column
						label="创建信息"
						width="200"
						align="center"
						sortable="custom"
						prop="create_time"
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
						prop="update_time"
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

						<el-table-column label="操作" width="210" fixed="right" align="center">
							<template #default="scope">
								<div class="action-buttons">
									<el-tooltip content="查看详情" placement="top" effect="dark">
										<el-button type="success" v-if="permission.has_read_permission" circle @click="viewDefectDetail(scope.row)" class="action-btn view-btn">
											<el-icon><View /></el-icon>
										</el-button>
									</el-tooltip>
									<el-tooltip content="编辑" placement="top" effect="dark">
										<el-button type="warning" v-if="permission.has_edit_permission" circle @click="openEditDialog(scope.row)" class="action-btn edit-btn">
											<el-icon><EditPen /></el-icon>
										</el-button>
									</el-tooltip>
									<el-tooltip content="删除" placement="top" effect="dark">
										<el-button type="danger" v-if="permission.has_delete_permission" circle @click="deleteDefect(scope.row.id)" class="action-btn delete-btn">
											<el-icon><Delete /></el-icon>
										</el-button>
									</el-tooltip>
								</div>
							</template>
						</el-table-column>
					</el-table>
				</div>

				<!-- 分页 -->
				<div class="pagination-wrapper">
					<el-pagination
						v-model:current-page="page_size_params.page"
						v-model:page-size="page_size_params.size"
						:page-sizes="[10, 20, 30, 50]"
						layout="total, sizes, prev, pager, next, jumper"
						:total="defect_list.count"
						@size-change="handleSizeChange"
						@current-change="handleCurrentChange"
						class="select input"
				:background="true"
			/>
			</div>
		</el-card>
	</div>

		<!-- 新增/编辑 抽屉 -->
		<el-drawer class="defect-drawer" v-model="dialogVisible" @closed="onDrawerClosed" :with-header="false" direction="rtl" :show-close="false" :append-to-body="true" :close-on-click-modal="false" size="calc(100vw)" destroy-on-close>
			<el-card class="content-card elegant-shadow">
				<el-form :model="defectForm" :rules="formRules" ref="defectFormRef" label-position="top">
				<!-- 左右分栏 -->
				<div class="drawer-split-layout">
					<!-- 左侧：自适应宽度 - 上下分栏（上：标题+创建/更新信息，下：富文本编辑区域） -->
					<div class="drawer-left">
						<!-- 上部：标题 + 创建/更新信息 -->
						<div class="drawer-left-header">
							<div class="header-top">
								<div class="case-title-area">
									<el-form-item prop="title" class="title-form-item">
										<el-input v-model="defectForm.title" class="case-title-input" placeholder="请输入缺陷标题" maxlength="500" :disabled="readView" />
									</el-form-item>
								</div>
							</div>
							<!-- 创建/更新信息（右对齐） -->
							<div class="case-meta-section">
								<div class="case-meta">
									<div class="meta-item">
										<span class="meta-label">创建人</span>
										<span class="meta-value">{{ defectForm.create_by_name || '-' }}</span>
									</div>
									<div class="meta-divider"></div>
									<div class="meta-item">
										<span class="meta-label">创建时间</span>
										<span class="meta-value">{{ defectForm.create_time || '-' }}</span>
									</div>
									<div class="meta-divider"></div>
									<div class="meta-item">
										<span class="meta-label">更新人</span>
										<span class="meta-value">{{ defectForm.update_by_name || '-' }}</span>
									</div>
									<div class="meta-divider"></div>
									<div class="meta-item">
										<span class="meta-label">更新时间</span>
										<span class="meta-value">{{ defectForm.update_time || '-' }}</span>
									</div>
								</div>
							</div>
						</div>
						<!-- 下部：富文本编辑区域 -->
						<div class="drawer-left-content">
							<el-collapse v-model="activeNames" class="step-collapse-panel">
								<el-card class="step_item_card">
									<el-collapse-item name="1">
										<template #title>
											<div class="section-divider">
												<span class="section-title">缺陷描述</span>
											</div>
										</template>
										<FullText v-model="defectForm.description" placeholder="请输入缺陷描述" :height="400" :autoHeight="true" :disabled="readView" />
									</el-collapse-item>
								</el-card>
								<el-card class="step_item_card">
									<el-collapse-item name="2">
										<template #title>
											<div class="section-divider">
												<span class="section-title">实际结果</span>
											</div>
										</template>
										<FullText v-model="defectForm.actual_result" placeholder="请输入实际结果" :height="400" :autoHeight="true" :disabled="readView" />
									</el-collapse-item>
								</el-card>
								<el-card class="step_item_card">
									<el-collapse-item name="3">
										<template #title>
											<div class="section-divider">
												<span class="section-title">预期结果</span>
											</div>
										</template>
										<FullText v-model="defectForm.expected_result" placeholder="请输入预期结果" :height="400" :autoHeight="true" :disabled="readView" />
									</el-collapse-item>
								</el-card>
							</el-collapse>
							<!-- 评论动态 / 关联功能用例 Tab -->
							<el-card class="step_item_card comment-section-card" v-if="defectForm.id">
								<el-tabs v-model="commentActiveTab" class="dynamic-tabs">
									<el-tab-pane label="评论动态" name="comments">
										<div class="comments-container">
											<div class="comment-input-area" v-if="permission.has_add_permission">
											<FullText
												v-model="newCommentContent"
												:height="200"
												:autoHeight="true"
												placeholder="请输入评论内容...输入 @ 可提及项目用户"
												:disabled="readView"
												:enable-mention="true"
												:mention-users="user_list"
												:mention-excluded-ids="newCommentMentionExcludedIds"
											></FullText>
											<div class="comment-actions" v-if="!readView">
												<el-button type="primary" @click="submitDefectComment" :loading="submittingComment" class="add-btn">
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
																	v-if="canEditComment(comment)"
																	type="text"
																	size="small"
																	@click="editDefectComment(comment)"
																>编辑</el-button>
																<el-button
																	v-if="canDeleteComment(comment)"
																	type="text"
																	size="small"
																	class="delete-btn"
																	@click="deleteDefectCommentRow(comment)"
																>删除</el-button>
															</span>
														</div>
													</div>
													<div class="comment-content">
														<div v-if="editingCommentId === comment.id" class="edit-comment-area">
														<FullText
															v-model="editCommentContent"
															:height="150"
															:autoHeight="true"
															:enable-mention="true"
															:mention-users="user_list"
															:mention-excluded-ids="editCommentMentionExcludedIds"
														></FullText>
														<div class="edit-actions">
															<el-button size="small" @click="saveDefectCommentEdit(comment)" type="primary">保存</el-button>
															<el-button size="small" @click="cancelDefectCommentEdit">取消</el-button>
														</div>
													</div>
														<div class="rich-text-view" v-else v-html="comment.content"></div>
													</div>
												</div>
												<el-empty v-if="commentsList.length === 0" description="暂无评论" :image-size="100"></el-empty>
											</div>
										</div>
									</el-tab-pane>
									<el-tab-pane :label="`关联功能用例${linkedFuncCases.length ? ' (' + linkedFuncCases.length + ')' : ''}`" name="func_cases">
										<div class="func-cases-tab">
											<div class="func-cases-toolbar" v-if="!readView">
												<el-button type="primary" @click="chooseCaseVisible = true" class="add-btn">
													<el-icon><Plus /></el-icon>添加关联
												</el-button>
											</div>
											<el-table :data="linkedFuncCases" class="elegant-table" v-loading="loadingFuncCases" empty-text="暂无关联功能用例">
												<el-table-column label="序号" width="70" type="index" align="center">
													<template #default="scope">
														<div class="index-cell">{{ scope.$index + 1 }}</div>
													</template>
												</el-table-column>
												<el-table-column label="用例名称" min-width="220" show-overflow-tooltip>
													<template #default="scope">
														<span class="func-case-name" @click="openFuncCaseDetail(scope.row)">{{ scope.row.name }}</span>
													</template>
												</el-table-column>
												<el-table-column label="用例标签" min-width="160" align="center">
												<template #default="scope">
													<div class="tags-container">
														<el-tag
															v-for="tag in scope.row.tag_name"
															:key="tag.id"
															size="small"
															:type="getTagType(tag.name)"
															effect="light"
															class="case-tag"
														>{{ tag.name }}</el-tag>
														<span v-if="!scope.row.tag_name || scope.row.tag_name.length === 0">-</span>
													</div>
												</template>
											</el-table-column>
											<el-table-column label="自动化信息" width="150" align="center">
												<template #default="scope">
													<div class="auto-info-cell">
														<span class="auto-type-badge" :class="'auto-type-' + scope.row.can_autoed">{{ scope.row.can_autoed_name || '-' }}</span>
														<span class="auto-status-badge" :class="'auto-status-' + scope.row.auto_status">{{ scope.row.auto_status_name || '-' }}</span>
													</div>
												</template>
											</el-table-column>
											<el-table-column label="创建信息" width="180" align="center">
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
											<el-table-column label="更新信息" width="180" align="center">
												<template #default="scope">
													<div class="user-time-cell">
														<div class="user-info">
															<el-icon><User /></el-icon>
															<span>{{ scope.row.update_by_name || '-' }}</span>
														</div>
														<div class="time-info">
															<el-icon><Document /></el-icon>
															<span>{{ formatTime(scope.row.update_time) }}</span>
														</div>
													</div>
												</template>
											</el-table-column>
												<el-table-column label="操作" width="100" align="center" v-if="!readView">
												<template #default="scope">
													<el-tooltip content="取消关联" placement="top" effect="dark">
														<el-button type="danger" circle size="small" @click="unlinkFuncCase(scope.row)">
															<el-icon><Delete /></el-icon>
														</el-button>
													</el-tooltip>
												</template>
											</el-table-column>
										</el-table>
										</div>
									</el-tab-pane>
								</el-tabs>
							</el-card>
						</div>
					</div>
					<!-- 右侧：300px 固定宽度 - 基础信息 -->
					<div class="drawer-right">
						<div class="drawer-right-title">
							<span>基础信息</span>
						</div>
						<el-divider style="margin-top: 10px; margin-bottom: 30px"></el-divider>
						<div class="step-base-info">
				<el-form-item label="所属测试计划" prop="plan">
					<el-select v-model="defectForm.plan" placeholder="请选择测试计划" clearable filterable class="select" size="large" popper-class="select-dropdown-rounded" :disabled="readView" @change="onPlanChange">
						<el-option v-for="plan in planList" :key="plan.id" :label="plan.name" :value="plan.id" />
					</el-select>
				</el-form-item>
				<el-form-item label="所属模块" prop="module">
						<el-cascader
							v-model="defectForm.module"
							placeholder="请选择或输入模块名称"
							collapse-tags
							:options="plant_module_list"
							:props="moduleEditProps"
							filterable
							size="large"
							style="width: 100%;"
							class="cascader"
							:disabled="readView"
						/>
					</el-form-item>
					<el-form-item label="严重程度" prop="severity">
						<el-select v-model="defectForm.severity" placeholder="请选择" class="select" size="large" popper-class="select-dropdown-rounded" :disabled="readView">
							<el-option v-for="item in severityOptions" :key="item.value" :label="item.label" :value="item.value" />
						</el-select>
					</el-form-item>
					<el-form-item label="优先级" prop="priority">
						<el-select v-model="defectForm.priority" placeholder="请选择" class="select" size="large" popper-class="select-dropdown-rounded" :disabled="readView">
							<el-option v-for="item in priorityOptions" :key="item.value" :label="item.label" :value="item.value" />
						</el-select>
					</el-form-item>
					<el-form-item label="BUG类型" prop="defect_type">
						<el-select v-model="defectForm.defect_type" placeholder="请选择" class="select" size="large" popper-class="select-dropdown-rounded" :disabled="readView">
							<el-option v-for="item in defectTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
						</el-select>
					</el-form-item>
					<el-form-item label="状态" prop="status">
						<el-select v-model="defectForm.status" placeholder="请选择" class="select" size="large" popper-class="select-dropdown-rounded" :disabled="readView">
							<el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
						</el-select>
					</el-form-item>
					<el-form-item label="负责人" prop="owner">
					<el-select v-model="defectForm.owner" placeholder="请选择" clearable filterable class="select" size="large" popper-class="select-dropdown-rounded" :disabled="readView">
						<el-option v-for="user_obj in user_list" :key="user_obj.id" :label="user_obj.username" :value="user_obj.id" />
					</el-select>
				</el-form-item>
				<el-form-item label="处理人" prop="assignee">
					<el-select v-model="defectForm.assignee" placeholder="请选择" clearable filterable class="select" size="large" popper-class="select-dropdown-rounded" :disabled="readView">
						<el-option v-for="user_obj in user_list" :key="user_obj.id" :label="user_obj.username" :value="user_obj.id" />
					</el-select>
				</el-form-item>
			</div>
				</div>
			</div>
				</el-form>
			</el-card>
			<div class="drawer-footer">
			<el-button @click="dialogVisible = false" class="dialog-cancel-btn">{{ readView ? '返回' : '取消' }}</el-button>
			<el-button v-if="!readView" type="primary" @click="saveDefect(false)" class="dialog-confirm-btn">保存</el-button>
			<el-button v-if="!readView" type="success" @click="saveDefect(true)" class="dialog-confirm-btn">保存并关闭</el-button>
		</div>
		</el-drawer>

		<!-- 功能用例详情抽屉（样式与内容参考测试计划详情） -->
		<el-drawer
			v-model="funcCaseDetailVisible"
			direction="rtl"
			:size="'calc(100vw - 260px)'"
			:show-close="true"
			:with-header="false"
			:append-to-body="true"
			:z-index="3001"
			class="func-case-detail-drawer"
			destroy-on-close
		>
			<div class="detail-header">
				<div class="title-area">
					<h3 class="drawer-title">{{ currentFuncCaseDetail.name || '用例详情' }}</h3>
					<el-tooltip content="复制用例名称" placement="top" effect="dark">
						<el-button type="primary" class="copy-btn" @click="copyFuncCaseName" circle size="small">
							<el-icon><DocumentCopy /></el-icon>
						</el-button>
					</el-tooltip>
				</div>
			</div>

			<div class="detail-nav-wrapper" v-if="navItems.length">
				<div class="vertical-nav">
					<div
						v-for="(item, index) in navItems"
						:key="index"
						class="nav-item"
						:class="{ active: activeSection === item.id }"
						@click="scrollToSection(item.id)"
					>
						<span class="nav-text">{{ item.name }}</span>
					</div>
				</div>
			</div>

			<div class="case-detail-container" v-if="currentFuncCaseDetail.id">
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
										<div class="form-value">{{ currentFuncCaseDetail.module_name || '-' }}</div>
									</div>
								</el-col>
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">自动化类型</label>
										<div class="form-value">
											<span class="tag-item">{{ currentFuncCaseDetail.can_autoed_name || '-' }}</span>
										</div>
									</div>
								</el-col>
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">自动化状态</label>
										<div class="form-value">
											<span class="tag-item">{{ currentFuncCaseDetail.auto_status_name || '-' }}</span>
										</div>
									</div>
								</el-col>
								<el-col :span="4">
									<div class="form-item">
										<label class="form-label">用例标签</label>
										<div class="form-value">
											<span v-for="(tag, index) in currentFuncCaseDetail.tag_name" :key="index" class="tag-item">
												{{ tag.name }}
											</span>
											<span v-if="!currentFuncCaseDetail.tag_name || currentFuncCaseDetail.tag_name.length === 0">-</span>
										</div>
									</div>
								</el-col>
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">负责人</label>
										<div class="form-value">{{ currentFuncCaseDetail.owner_name || '-' }}</div>
									</div>
								</el-col>
							</el-row>
							<el-row :gutter="32">
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">创建人</label>
										<div class="form-value">{{ currentFuncCaseDetail.create_by_name || '-' }}</div>
									</div>
								</el-col>
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">创建时间</label>
										<div class="form-value">{{ formatTime(currentFuncCaseDetail.create_time) }}</div>
									</div>
								</el-col>
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">更新人</label>
										<div class="form-value">{{ currentFuncCaseDetail.update_by_name || '-' }}</div>
									</div>
								</el-col>
								<el-col :span="5">
									<div class="form-item">
										<label class="form-label">更新时间</label>
										<div class="form-value">{{ formatTime(currentFuncCaseDetail.update_time) }}</div>
									</div>
								</el-col>
								<el-col :span="4"></el-col>
							</el-row>
						</div>
					</el-card>

					<el-card class="section-card" id="section-precondition">
						<div class="section-divider">
							<span class="section-title">前置条件</span>
						</div>
						<el-divider style="margin-top: 0px"></el-divider>
						<div class="rich-content">
							<div class="rich-text-view" v-html="currentFuncCaseDetail.setup_condition || '暂无前置条件'"></div>
						</div>
					</el-card>

					<el-card class="section-card" id="section-steps">
						<div class="section-divider">
							<span class="section-title">测试步骤</span>
						</div>
						<el-divider style="margin-top: 0px"></el-divider>
						<div class="steps-content">
							<div v-if="currentFuncCaseDetail.step_type === 1" class="rich-content">
								<div class="rich-text-view" v-html="currentFuncCaseDetail.step_text || '暂无步骤信息'"></div>
							</div>
							<FunCaseTable
								v-if="currentFuncCaseDetail.step_type === 2"
								:tableData="currentFuncCaseDetail.step_table"
								:height="300"
								:readonly="true">
							</FunCaseTable>
						</div>
					</el-card>

					<el-card class="section-card" id="section-expected" v-if="currentFuncCaseDetail.step_type === 1">
						<div class="section-divider">
							<span class="section-title">预期结果</span>
						</div>
						<el-divider style="margin-top: 0px"></el-divider>
						<div class="rich-content">
							<div class="rich-text-view" v-html="currentFuncCaseDetail.exp_text || '暂无预期结果'"></div>
						</div>
					</el-card>

					<el-card class="section-card" id="section-remark">
						<div class="section-divider">
							<span class="section-title">备注信息</span>
						</div>
						<el-divider style="margin-top: 0px"></el-divider>
						<div class="rich-content">
							<div class="rich-text-view" v-html="currentFuncCaseDetail.case_mark || '暂无备注'"></div>
						</div>
					</el-card>

					<el-card class="section-card" id="section-script" v-if="currentFuncCaseDetail.can_autoed !== 3 && currentFuncCaseDetail.case_detail && currentFuncCaseDetail.case_detail.length > 0">
						<div class="section-divider">
							<span class="section-title">关联自动化脚本用例</span>
						</div>
						<el-divider style="margin-top: 0px"></el-divider>
						<el-table
							:data="currentFuncCaseDetail.case_detail"
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
						</el-table>
					</el-card>
				</div>
			</div>
		</el-drawer>

		<!-- 选择功能用例抽屉 -->
		<el-drawer
			v-model="chooseCaseVisible"
			:with-header="false"
			direction="ttb"
			show-close
			:z-index="3000"
			:append-to-body="true"
			size="'calc(100vh - 30px)'"
			destroy-on-close
		>
			<FunCaseList
				:isCanChoose="true"
				:parentPermission="permission"
				:existCaseIds="existCaseIds"
				v-model:chooseCaseVisible="chooseCaseVisible"
				@setFuncCaseData="addSingleFuncCase"
				@setFuncManyCaseData="addManyFuncCases"
			></FunCaseList>
		</el-drawer>
	</div>
</template>

<script>
import {mapState} from 'vuex'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Refresh, Search, View, Delete, Plus, EditPen, Expand, Fold, ArrowDown, User, Document, DocumentCopy} from '@element-plus/icons-vue'
import FullText from '../../components/FullText.vue'
import FunCaseList from '../case/FunCaseList.vue'
import FunCaseTable from '../../components/FunCaseTable.vue'

export default {
	name: 'DefectList',
	components: {
		FullText,
		FunCaseList,
		FunCaseTable,
	},
	computed: {
		...mapState(['pathPermission', 'projectInfo', 'userInfo']),
		// 新评论编辑器中已提及的用户ID（避免重复@）
		newCommentMentionExcludedIds() {
			return this.extractMentionedIds(this.newCommentContent)
		},
		// 编辑评论时已提及的用户ID
		editCommentMentionExcludedIds() {
			return this.extractMentionedIds(this.editCommentContent)
		}
	},
	data() {
		return {
			permission: {},
			multipleSelection: [],
			user_list: [],
			plant_module_list: [],
			moduleEditProps: {
				emitPath: false,
				value: 'id',
				label: 'name',
				checkStrictly: true,
			},
			filterText: '',
			selectNode: null,
			includeChildren: true,
			defectSearch: {
				title: '',
				severity: '',
				priority: '',
				defect_type: '',
				status: '',
				assignee: '',
				module_list: [],
				plan: '',
			},
			page_size_params: {
			page: 1,
			size: 10,
		},
		// 后端排序：DRF OrderingFilter 的 ordering 参数，前缀 '-' 表示降序
		ordering: '-create_time',
		defect_list: {count: 0, results: []},
			dialogVisible: false,
			isEdit: false,
			readView: false,
			activeNames: ['1', '2', '3'],
			defectForm: this.getEmptyDefectForm(),
			formRules: {
				title: [{required: true, message: '请输入缺陷标题', trigger: 'blur'}],
				severity: [{required: true, message: '请选择严重程度', trigger: 'change'}],
				priority: [{required: true, message: '请选择优先级', trigger: 'change'}],
				defect_type: [{required: true, message: '请选择BUG类型', trigger: 'change'}],
				status: [{required: true, message: '请选择状态', trigger: 'change'}],
				assignee: [{required: true, message: '请选择处理人', trigger: 'change'}],
				module: [{required: true, message: '请选择所属模块', trigger: 'change'}],
			},
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
			],
			// 评论动态相关
		newCommentContent: '',
		commentsList: [],
		submittingComment: false,
		editingCommentId: null,
		editCommentContent: '',
			// 测试计划列表
		planList: [],
		// 关联功能用例 Tab
			commentActiveTab: 'comments',
			linkedFuncCases: [],
			loadingFuncCases: false,
			funcCaseDetailVisible: false,
		currentFuncCaseDetail: {},
		activeSection: 'section-basic',
		navItems: [],
			// 选择功能用例抽屉
			chooseCaseVisible: false,
			existCaseIds: [],
		}
	},
	watch: {
		filterText(val) {
			this.$refs.treeRef?.filter(val)
		},
		// 已在缺陷列表页时，点击@提及消息跳转携带 action&id 自动打开弹窗
		'$route.query'(val) {
			const { action, id } = val || {}
			if (action && id) {
				if (this.dialogVisible && String(this.defectForm.id) === String(id)) return
				this.openDefectFromUrl(action, id)
			}
		},
	},
	methods: {
		goToCreatePlant() {
			this.$router.push({ name: 'plant' })
		},
		getEmptyDefectForm() {
			return {
				id: null,
				title: '',
				description: '',
				actual_result: '',
				expected_result: '',
				severity: 3,
				priority: 3,
				defect_type: 1,
				status: 1,
			owner: null,
			assignee: null,
				module: null,
				plan: null,
				func_cases: [],
				create_by_name: '',
				create_time: '',
				update_by_name: '',
				update_time: '',
			}
		},
		getSeverityTagType(severity) {
			const map = {1: 'danger', 2: 'warning', 3: '', 4: 'info'}
			return map[severity] || ''
		},
		getPriorityTagType(priority) {
			const map = {1: 'danger', 2: 'warning', 3: '', 4: 'info'}
			return map[priority] || ''
		},
		getStatusTagType(status) {
		const map = {1: 'info', 2: 'warning', 3: 'success', 4: 'danger'}
		return map[status] || ''
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
	async updateSingleField(row, field, value) {
		const response = await this.$api.patchDefect(row.id, {[field]: value})
		if (response.status === 200) {
			ElMessage.success('修改成功')
			this.getDefects()
		}
	},
	getAssigneeClass(userId) {
		if (!userId) return 'assignee-none'
		const palette = [
			'assignee-1', 'assignee-2', 'assignee-3', 'assignee-4',
			'assignee-5', 'assignee-6', 'assignee-7', 'assignee-8',
		]
		// 按 user id 哈希选色，保证同一用户始终显示同一颜色
		const idx = (Number(userId) % palette.length + palette.length) % palette.length
		return palette[idx]
	},
	getPlanClass(planId) {
		if (!planId) return 'assignee-none'
		const palette = [
			'assignee-1', 'assignee-2', 'assignee-3', 'assignee-4',
			'assignee-5', 'assignee-6', 'assignee-7', 'assignee-8',
		]
		const idx = (Number(planId) % palette.length + palette.length) % palette.length
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
			year: 'numeric',
			month: '2-digit',
			day: '2-digit',
			hour: '2-digit',
			minute: '2-digit',
		}).replace(/\//g, '-')
	},
	getTagType(tagName) {
		if (!tagName) return ''
		const colors = ['', 'success', 'info', 'warning', 'danger']
		const hash = tagName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
		return colors[hash % colors.length]
	},
		search() {
		this.page_size_params.page = 1
		this.getDefects()
	},
	reset() {
		for (let key in this.defectSearch) {
			if (Array.isArray(this.defectSearch[key])) {
				this.defectSearch[key] = []
			} else {
				this.defectSearch[key] = ''
			}
		}
		// 重置树选中状态
		this.selectNode = null
		this.$refs.treeRef?.setCurrentKey(null)
		this.getDefects()
	},
	handleCurrentChange() {
		this.getDefects()
	},
	handleSizeChange() {
		this.page_size_params.page = 1
		this.getDefects()
	},
	handleSelectionChange(val) {
		this.multipleSelection = val
	},
	handleSortChange({ column, prop, order }) {
		// 后端排序：将 Element Plus 的排序状态转为 DRF ordering 参数
		// prop -> 实际排序字段（处理人需跨表用 assignee__username）
		const orderingFieldMap = {
			severity: 'severity',
			priority: 'priority',
			defect_type: 'defect_type',
			status: 'status',
			owner_name: 'owner__username',
			assignee_name: 'assignee__username',
			create_time: 'create_time',
			update_time: 'update_time',
		}
		const field = orderingFieldMap[prop]
		if (!prop || !order || !field) {
			this.ordering = ''
		} else if (order === 'ascending') {
			this.ordering = field
		} else {
			this.ordering = '-' + field
		}
		this.page_size_params.page = 1
		this.getDefects()
	},
	async getDefects() {
		this.defectSearch.project = this.projectInfo.id
		const params = {}
		for (let key in this.defectSearch) {
			const val = this.defectSearch[key]
			if (val === '' || val === null || val === undefined) continue
			if (Array.isArray(val)) {
				if (val.length === 0) continue
				// module_list 数组映射为后端字段名 module（参考 FunCaseList）
				const paramKey = key === 'module_list' ? 'module' : key
				params[paramKey] = val.join(',')
			} else {
				params[key] = val
			}
		}
		// 后端排序参数（DRF OrderingFilter）
		if (this.ordering) {
			params.ordering = this.ordering
		}
		const response = await this.$api.getDefects(Object.assign(params, this.page_size_params))
		if (response.status === 200) {
			this.defect_list = {...response.data}
		}
	},
	// 模块树相关方法（参考 FunCaseList）
	expandAllNodes() {
		const allNodes = this.$refs.treeRef?.store._getAllNodes() || []
		allNodes.forEach(node => { node.expanded = true })
	},
	collapseAllNodes() {
		const allNodes = this.$refs.treeRef?.store._getAllNodes() || []
		allNodes.forEach(node => { node.expanded = false })
	},
	filterNode(value, data) {
		if (!value) return true
		return data?.name?.includes(value) || false
	},
	moduleSelect(node) {
		if (!node) {
			this.selectNode = null
			this.defectSearch.module_list = []
			localStorage.removeItem('defect_node')
			this.getDefects()
			return
		}
		// 再次点击已选中节点，取消选中
		if (this.selectNode === node.id) {
			this.$refs.treeRef?.setCurrentKey(null)
			this.selectNode = null
			this.defectSearch.module_list = []
			localStorage.removeItem('defect_node')
			this.getDefects()
			return
		}
		localStorage.setItem('defect_node', JSON.stringify(node))
		this.selectNode = node.id
		this.defectSearch.module_list = this.includeChildren ? this.getAllIds(node) : [node.id]
		this.getDefects()
	},
	onIncludeChildrenChange() {
		if (this.selectNode) {
			const node = this.$refs.treeRef?.getCurrentNode()
			if (node) {
				this.defectSearch.module_list = this.includeChildren ? this.getAllIds(node) : [node.id]
				this.getDefects()
			}
		}
	},
	getAllIds(node) {
		if (!node) return []
		const ids = [node.id]
		if (node.children && Array.isArray(node.children)) {
			node.children.forEach(child => { ids.push(...this.getAllIds(child)) })
		}
		return ids
	},
		async check_permission() {
			const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission[this.$route.path]}
			const response = await this.$api.check_permission(params)
			if (response.status === 200) {
				this.permission = {...response.data.result}
			}
		},
		openCreateDialog() {
		this.isEdit = false
		this.readView = false
		const node = this.$refs.treeRef?.getCurrentNode()
		this.defectForm = this.getEmptyDefectForm()
		// 选中模块时自动回填（根节点 id<0 不回填）
		if (node && node.id > 0) {
			this.defectForm.module = node.id
		}
		this.dialogVisible = true
		// 新建时清空评论与关联用例
		this.commentsList = []
		this.newCommentContent = ''
		this.editingCommentId = null
		this.editCommentContent = ''
		this.linkedFuncCases = []
		this.existCaseIds = []
		this.commentActiveTab = 'comments'
		this.$nextTick(() => {
			this.$refs.defectFormRef && this.$refs.defectFormRef.clearValidate()
		})
	},
		openEditDialog(row) {
		this.isEdit = true
		this.readView = false
		this.defectForm = {
			id: row.id,
			title: row.title,
			description: row.description,
			actual_result: row.actual_result || '',
			expected_result: row.expected_result || '',
			severity: row.severity,
			priority: row.priority,
			defect_type: row.defect_type,
			status: row.status,
		owner: row.owner,
		assignee: row.assignee,
			module: row.module,
			plan: row.plan,
			func_cases: (row.func_cases || []).map(fc => typeof fc === 'object' ? fc.id : fc),
			create_by: row.create_by,
			create_by_name: row.create_by_name || '',
			create_time: row.create_time || '',
			update_by_name: row.update_by_name || '',
			update_time: row.update_time || '',
		}
		this.dialogVisible = true
		this.loadLinkedFuncCases(row)
		this.loadDefectComments(row.id)
		this.$router.replace({ query: { ...this.$route.query, action: 'edit', id: row.id } })
		this.$nextTick(() => {
			this.$refs.defectFormRef && this.$refs.defectFormRef.clearValidate()
		})
	},
	async saveDefect(closeAfter = false) {
		this.$refs.defectFormRef.validate(async (valid) => {
			if (valid) {
				// 校验模块不能选根节点
				if (this.defectForm.module && this.defectForm.module < 0) {
					ElMessage.error('所属模块不能选择根节点')
					return
				}
				const submitData = {...this.defectForm, project: this.projectInfo.id}
				// 空值清理，避免外键字段 400
				if (!submitData.assignee) submitData.assignee = null
				if (!submitData.module) submitData.module = null
				if (!submitData.plan) submitData.plan = null
				if (this.isEdit) {
						const response = await this.$api.updateDefect(this.defectForm.id, submitData)
						if (response.status === 200) {
							if (closeAfter) {
								this.dialogVisible = false
							} else {
								// 保留弹窗，刷新当前缺陷数据并重新加载评论
								this.loadDefectComments(this.defectForm.id)
							}
							this.getDefects()
							ElMessage.success('更新成功')
						}
					} else {
						const response = await this.$api.createDefect(submitData)
						if (response.status === 201) {
							if (closeAfter) {
								this.dialogVisible = false
							} else {
								// 新建成功后转为编辑模式，便于继续编辑
								this.isEdit = true
								this.defectForm.id = response.data.result.id
								// 回填新建后的 id 到 func_cases（保持已选项）
								if (Array.isArray(this.defectForm.func_cases)) {
									this.defectForm.func_cases = [...this.defectForm.func_cases]
								}
								this.loadDefectComments(response.data.result.id)
							}
							this.getDefects()
							ElMessage.success('创建成功')
						}
					}
				}
			})
	},
		viewDefectDetail(row) {
		this.isEdit = false
		this.readView = true
		this.defectForm = {
			id: row.id,
			title: row.title,
			description: row.description,
			actual_result: row.actual_result || '',
			expected_result: row.expected_result || '',
			severity: row.severity,
			priority: row.priority,
			defect_type: row.defect_type,
			status: row.status,
		owner: row.owner,
		assignee: row.assignee,
			module: row.module,
			plan: row.plan,
			func_cases: (row.func_cases || []).map(fc => typeof fc === 'object' ? fc.id : fc),
			create_by: row.create_by,
			create_by_name: row.create_by_name || '',
			create_time: row.create_time || '',
			update_by_name: row.update_by_name || '',
			update_time: row.update_time || '',
		}
		this.dialogVisible = true
		this.loadLinkedFuncCases(row)
		this.loadDefectComments(row.id)
		this.$router.replace({ query: { ...this.$route.query, action: 'view', id: row.id } })
		this.$nextTick(() => {
			this.$refs.defectFormRef && this.$refs.defectFormRef.clearValidate()
		})
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
					this.getDefects()
				}
			}).catch(() => {})
		},
		async batchDeleteDefects() {
			if (this.multipleSelection.length === 0) {
				ElMessage.warning('请选择要删除的缺陷')
				return
			}
			ElMessageBox.confirm(`确定删除选中的 ${this.multipleSelection.length} 条缺陷？删除后数据将无法恢复。`, '确认批量删除', {
				confirmButtonText: '确认删除',
				cancelButtonText: '取消',
				type: 'warning',
			}).then(async () => {
				const ids = this.multipleSelection.map(item => item.id)
				try {
					await Promise.all(ids.map(id => this.$api.deleteDefect(id)))
					this.multipleSelection = []
					this.getDefects()
					ElMessage.success(`成功删除 ${ids.length} 条缺陷`)
				} catch (error) {
					ElMessage.error('部分删除失败')
					this.getDefects()
				}
			}).catch(() => {})
		},
		async getPlantModule() {
			const response = await this.$api.getAllPlantModule({project: this.projectInfo.id})
			if (response.status === 200) {
				this.plant_module_list = response.data.results
			}
		},
	async openDefectFromUrl(action, id) {
		const res = await this.$api.getDefect(id)
		if (res.status === 200) {
			const data = { ...res.data.result, id: id }
			if (action === 'view') {
				this.viewDefectDetail(data)
			} else if (action === 'edit') {
				this.openEditDialog(data)
			}
		}
	},
	onDrawerClosed() {
		const query = { ...this.$route.query }
		delete query.action
		delete query.id
		this.$router.replace({ query })
		// 重置评论相关状态
		this.newCommentContent = ''
		this.commentsList = []
		this.editingCommentId = null
		this.editCommentContent = ''
		this.submittingComment = false
		// 重置关联用例相关状态
		this.linkedFuncCases = []
		this.existCaseIds = []
		this.currentFuncCaseDetail = {}
		this.funcCaseDetailVisible = false
		this.activeSection = 'section-basic'
		this.navItems = []
		this.chooseCaseVisible = false
		this.commentActiveTab = 'comments'
	},
	// ===== 评论动态相关方法 =====
	loadDefectComments(defectId) {
		if (!defectId) {
			this.commentsList = []
			return
		}
		this.$api.getDefectComments({ defect: defectId }).then(res => {
			if (res.status === 200) {
				this.commentsList = res.data.results || res.data || []
			}
		}).catch(() => {
			this.commentsList = []
		})
	},
	submitDefectComment() {
	if (!this.newCommentContent.trim()) {
		ElMessage.warning('请输入评论内容')
		return
	}
	this.submittingComment = true
	const params = {
		defect: this.defectForm.id,
		content: this.newCommentContent,
		mentioned_users: this.extractMentionedIds(this.newCommentContent)
	}
	this.$api.createDefectComment(params).then(res => {
		if (res.status === 201) {
			ElMessage.success('评论发布成功')
			this.newCommentContent = ''
			this.loadDefectComments(this.defectForm.id)
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
	editDefectComment(comment) {
		this.editingCommentId = comment.id
		this.editCommentContent = comment.content
	},
	saveDefectCommentEdit(comment) {
		if (!this.editCommentContent.trim()) {
			ElMessage.warning('请输入评论内容')
			return
		}
		this.$api.updateDefectComment(comment.id, { content: this.editCommentContent }).then(res => {
			if (res.status === 200) {
				ElMessage.success('评论更新成功')
				this.editingCommentId = null
				this.editCommentContent = ''
				this.loadDefectComments(this.defectForm.id)
			}
		})
	},
	cancelDefectCommentEdit() {
		this.editingCommentId = null
		this.editCommentContent = ''
	},
	canEditComment(comment) {
		return comment && comment.comment_by === this.userInfo.user_id
	},
	canDeleteComment(comment) {
		return comment && comment.comment_by === this.userInfo.user_id
	},
	deleteDefectCommentRow(comment) {
		ElMessageBox.confirm('确定要删除这条评论吗？', '提示', {
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning'
		}).then(() => {
			this.$api.deleteDefectComment(comment.id).then(res => {
				if (res.status === 204) {
					ElMessage.success('评论删除成功')
					this.loadDefectComments(this.defectForm.id)
				}
			})
		}).catch(() => {})
	},
	// ===== 测试计划与功能用例 =====
	async loadPlanList() {
		const params = { project: this.projectInfo.id, size: 999 }
		const response = await this.$api.getPlans(params)
		if (response.status === 200) {
			this.planList = response.data.results || []
		}
	},
	onPlanChange(planId) {
		// 选择测试计划后，可按需联动加载该计划下的功能用例（这里简单加载全部项目的功能用例）
		// 如需按计划过滤，可调用 getPlanCases(planId)
	},
	// ===== 关联功能用例相关方法 =====
	loadLinkedFuncCases(row) {
		this.linkedFuncCases = (row && row.func_cases_info) ? [...row.func_cases_info] : []
		this.defectForm.func_cases = this.linkedFuncCases.map(c => c.id)
		this.existCaseIds = [...this.defectForm.func_cases]
	},
	async openFuncCaseDetail(row) {
		// func_cases_info 已通过序列化器返回完整信息，直接使用
		this.currentFuncCaseDetail = { ...row }
		this.activeSection = 'section-basic'
		this.navItems = []
		this.funcCaseDetailVisible = true
		this.$nextTick(() => {
			this.buildFuncCaseNavItems()
		})
	},

	buildFuncCaseNavItems() {
		const items = [
			{ id: 'section-basic', name: '基础信息' },
			{ id: 'section-precondition', name: '前置条件' },
			{ id: 'section-steps', name: '测试步骤' }
		]
		if (this.currentFuncCaseDetail.step_type === 1) {
			items.push({ id: 'section-expected', name: '预期结果' })
		}
		items.push({ id: 'section-remark', name: '备注信息' })
		if (this.currentFuncCaseDetail.can_autoed !== 3 &&
			this.currentFuncCaseDetail.case_detail &&
			this.currentFuncCaseDetail.case_detail.length > 0) {
			items.push({ id: 'section-script', name: '关联用例' })
		}
		this.navItems = items
	},

	scrollToSection(sectionId) {
		this.activeSection = sectionId
		const element = document.getElementById(sectionId)
		if (element) {
			element.scrollIntoView({ behavior: 'smooth', block: 'start' })
		}
	},

	copyFuncCaseName() {
		navigator.clipboard.writeText(this.currentFuncCaseDetail.name || '')
		ElMessage({ message: '复制成功', type: 'success' })
	},

	getScriptCaseTagType(typeName) {
		const typeMap = {
			'API Case': 'primary',
			'Web Case': 'success',
			'App Case': 'warning'
		}
		return typeMap[typeName] || 'info'
	},
	async unlinkFuncCase(row) {
		ElMessageBox.confirm(`确定取消关联功能用例「${row.name}」？`, '提示', {
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning'
		}).then(async () => {
			this.loadingFuncCases = true
			const remainIds = this.linkedFuncCases.filter(c => c.id !== row.id).map(c => c.id)
			const response = await this.$api.patchDefect(this.defectForm.id, { func_cases: remainIds })
			if (response.status === 200) {
				ElMessage.success('已取消关联')
				this.linkedFuncCases = this.linkedFuncCases.filter(c => c.id !== row.id)
				this.defectForm.func_cases = remainIds
				this.existCaseIds = remainIds
				this.getDefects()
			}
			this.loadingFuncCases = false
		}).catch(() => {})
	},
	// 单个添加功能用例
	async addSingleFuncCase(caseItem) {
		if (this.existCaseIds.includes(caseItem.id)) {
			ElMessage.warning('该用例已关联，无需重复添加')
			this.chooseCaseVisible = false
			return
		}
		const allIds = [...this.linkedFuncCases.map(c => c.id), caseItem.id]
		const response = await this.$api.patchDefect(this.defectForm.id, { func_cases: allIds })
		if (response.status === 200) {
			ElMessage.success('关联成功')
			this.linkedFuncCases = [...this.linkedFuncCases, caseItem]
			this.defectForm.func_cases = allIds
			this.existCaseIds = allIds
			this.chooseCaseVisible = false
			this.getDefects()
		}
	},
	// 批量添加功能用例
	async addManyFuncCases(caseList) {
		const allCaseIds = caseList.map(item => item.id)
		const newCaseIds = allCaseIds.filter(id => !this.existCaseIds.includes(id))
		const duplicateCount = allCaseIds.length - newCaseIds.length
		if (newCaseIds.length === 0) {
			ElMessage.warning(`选中的 ${allCaseIds.length} 个用例已全部关联，无需重复添加`)
			this.chooseCaseVisible = false
			return
		}
		const allIds = [...new Set([...this.linkedFuncCases.map(c => c.id), ...newCaseIds])]
		const response = await this.$api.patchDefect(this.defectForm.id, { func_cases: allIds })
		if (response.status === 200) {
			if (duplicateCount > 0) {
				ElMessage.success(`成功关联 ${newCaseIds.length} 个用例（跳过 ${duplicateCount} 个已关联的用例）`)
			} else {
				ElMessage.success(`成功关联 ${newCaseIds.length} 个用例`)
			}
			const newCases = caseList.filter(c => newCaseIds.includes(c.id))
			this.linkedFuncCases = [...this.linkedFuncCases, ...newCases]
			this.defectForm.func_cases = allIds
			this.existCaseIds = allIds
			this.chooseCaseVisible = false
			this.getDefects()
		}
	},
},
mounted() {
	this.check_permission()
	this.user_list = JSON.parse(localStorage.getItem('user_list') || '[]')
	this.getPlantModule()
	this.loadPlanList()
	// 恢复上次选中的模块节点（参考 FunCaseList）
	const node = JSON.parse(localStorage.getItem('defect_node'))
	if (node) {
		this.selectNode = node.id
		this.$nextTick(() => {
			if (this.$refs.treeRef) {
				this.$refs.treeRef.setCurrentKey(node.id)
			}
		})
		this.defectSearch.module_list = this.getAllIds(node)
	}
	this.getDefects()
	// URL 参数打开编辑/查看弹窗
	const { action, id } = this.$route.query
	if (action && id) {
		this.openDefectFromUrl(action, id)
	}
},
}
</script>

<style scoped>
.defect-list {
	width: 100%;
	background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
	padding: 20px 15px 15px 15px;
	box-sizing: border-box;
	display: flex;
	gap: 20px;
	min-height: calc(100vh - 75px);
	height: calc(100vh - 75px);
	max-height: calc(100vh - 75px);
	overflow: hidden;
}

.elegant-shadow {
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.08);
	transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.elegant-shadow:hover {
	box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.12);
}

.filter-card {
	background: var(--qm-bg-2);
	border: none;
	border-radius: 16px;
	overflow: hidden;
	flex-shrink: 0;
	min-width: 0;
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

.filter-card :deep(.el-card__body) {
	padding: 20px 20px 0 20px;
}

.filter-form-wrapper {
	padding: 25px 24px 0px 24px;
}

.inline-form {
	margin-bottom: 0;
}

.inline-form-item {
	margin-bottom: 25px;
	display: flex;
	flex-direction: row;
	align-items: center;
	height: 40px;
}

.inline-form-item :deep(.el-form-item__content) {
	display: flex !important;
	flex-direction: row !important;
	align-items: center !important;
	flex-wrap: nowrap !important;
	margin-left: 0 !important;
	width: 100%;
}

.inline-label-wrapper {
	display: flex;
	align-items: center;
	gap: 6px;
	font-size: 14px;
	font-weight: 500;
	color: var(--qm-text-2);
	min-width: 100px;
	flex-shrink: 0;
	white-space: nowrap;
}

.inline-label-text {
	white-space: nowrap;
}

.inline-label-wrapper .icon-title,
.inline-label-wrapper .icon-severity,
.inline-label-wrapper .icon-priority,
.inline-label-wrapper .icon-type,
.inline-label-wrapper .icon-status,
.inline-label-wrapper .icon-user {
	width: 16px;
	height: 16px;
	display: inline-block;
	flex-shrink: 0;
	border-radius: 4px;
	background-size: contain;
	background-repeat: no-repeat;
}

.inline-label-wrapper .icon-title {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
	background-color: transparent;
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.inline-label-wrapper .icon-severity {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' d='M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z'/%3E%3C/svg%3E");
	background-color: transparent;
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.inline-label-wrapper .icon-priority {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' d='M14.5 17.5L13 16l4-4-4-4 1.5-1.5 4 4zM11 16.5L2.5 8l1.5-1.5L11 13.5l1.5-1.5 5.5 5.5L15 19l-4-4v2.5z'/%3E%3C/svg%3E");
	background-color: transparent;
	background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
}

.inline-label-wrapper .icon-type {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' d='M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10zM6 12h8v2H6zm0-3h12v2H6zm0 6h8v2H6z'/%3E%3C/svg%3E");
	background-color: transparent;
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.inline-label-wrapper .icon-status {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z'/%3E%3C/svg%3E");
	background-color: transparent;
	background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.inline-label-wrapper .icon-user {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
	background-color: transparent;
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.content-card {
	flex: 1;
	background: var(--qm-bg-2);
	border: none;
	border-radius: 16px;
	display: flex;
	flex-direction: column;
	min-height: 0;
	min-width: 0;
	overflow: hidden;
	padding-bottom: 0px;
}

/* 右侧主要内容区域：上筛选 + 下列表 */
.main-content {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 20px;
	min-width: 0;
}

/* 左侧模块树侧边栏 */
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
	gap: 12px;
}

.sidebar-title-wrapper {
	display: flex;
	align-items: center;
	gap: 12px;
}

.include-children-radio {
	flex-shrink: 0;
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

/* 模块树滚动条样式 */
.tree-wrapper::-webkit-scrollbar {
	width: 6px;
}

.tree-wrapper::-webkit-scrollbar-track {
	background: transparent;
}

.tree-wrapper::-webkit-scrollbar-thumb {
	background: var(--qm-line-strong);
	border-radius: 3px;
}

.tree-wrapper::-webkit-scrollbar-thumb:hover {
	background: var(--qm-text-3);
}

/* el-tree 节点样式 */
.elegant-tree :deep(.el-tree) {
	background: transparent;
}

.elegant-tree :deep(.el-tree-node__content) {
	height: 40px;
	border-radius: 8px;
	margin-bottom: 4px;
	transition: all 0.3s ease;
}

.elegant-tree :deep(.el-tree-node__content:hover) {
	background: var(--qm-warning-soft);
}

.elegant-tree :deep(.el-tree-node.is-current > .el-tree-node__content) {
	background: var(--qm-warning-soft);
	position: relative;
}

.elegant-tree :deep(.el-tree-node.is-current > .el-tree-node__content)::before {
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

.header-action-section {
	display: flex;
	align-items: center;
	gap: 12px;
}

.table-wrapper {
	flex: 1;
	padding: 0;
	min-height: 0;
	min-width: 0;
	overflow: hidden;
}

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

/* 排序图标：恢复默认上下箭头并高亮当前排序方向 */
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

.pagination-wrapper {
	padding: 20px 24px 0px 24px;
	border-top: 1px solid var(--qm-bg-3);
	float: right;
	display: flex;
	justify-content: flex-end;
	margin-bottom: 10px;
	padding-right: 10px;
}

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

.action-btn.edit-btn {
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
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

/* 列内下拉编辑 - 彩色徽章（参考 FunCaseList 自动化状态） */
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

.inline-edit-wrapper {
	padding: 4px;
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

/* 处理人/负责人颜色（按 user id 取模，8 套彩色渐变） */
.assignee-none { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }
.assignee-1 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.assignee-2 { background: linear-gradient(135deg, #a78bfa 0%, #f97316 100%); }
.assignee-3 { background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%); }
.assignee-4 { background: linear-gradient(135deg, #fb7185 0%, #e11d48 100%); }
.assignee-5 { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); }
.assignee-6 { background: linear-gradient(135deg, #22d3ee 0%, #d97706 100%); }
.assignee-7 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.assignee-8 { background: linear-gradient(135deg, #fb923c 0%, #ea580c 100%); }

/* 下拉弹出菜单样式（非 scoped） */

/* 新增缺陷按钮 - 绿色渐变（参考 FunCaseList .add-btn） */
.add-btn {
	padding: 5px 24px;
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

/* 批量删除按钮 - 红色渐变 */
.batch-delete-btn {
	padding: 10px 24px;
	border-radius: 10px;
	background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
	border: none;
	font-weight: 500;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
}

.batch-delete-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.batch-delete-btn .el-icon {
	margin-right: 8px;
	font-size: 16px;
}

/* 抽屉底部按钮样式（参考 FunCaseList） */
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
	transform: translateY(-1px);
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
	transform: translateY(-2px);
	box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
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

/* 可编辑缺陷标题输入框（参考 FunCaseList，使用 scoped :deep 穿透） */
.title-form-item {
	margin-bottom: 0;
}

.title-form-item :deep(.el-form-item__content) {
	line-height: normal;
}

.case-title-input {
	width: 100%;
}

.case-title-input :deep(.el-input__wrapper) {
	border: none;
	box-shadow: none;
	background: transparent;
	padding: 0 8px;
	border-radius: 8px;
	transition: all 0.2s ease;
	min-height: 36px;
	height: 36px;
}

.case-title-input :deep(.el-input__wrapper:hover) {
	background: var(--qm-bg-3);
}

.case-title-input :deep(.el-input__wrapper.is-focus) {
	background: var(--qm-bg-1);
	box-shadow: 0 0 0 2px #f59e0b inset;
}

.case-title-input :deep(.el-input__inner) {
	font-size: 16px;
	font-weight: 700;
	color: var(--qm-text-1);
	height: 36px;
	line-height: 36px;
	text-align: left;
}

.case-title-input :deep(.el-input__inner::placeholder) {
	font-size: 14px;
	font-weight: 400;
	color: var(--qm-text-3);
	text-align: left;
}

/* 创建信息/更新信息合并列样式（参考 FunCaseList） */
.user-time-cell {
	display: flex;
	flex-direction: column;
	gap: 4px;
	align-items: center;
	padding: 8px 0;
}

.user-info,
.time-info {
	display: flex;
	align-items: center;
	gap: 6px;
	justify-content: center;
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

.func-cases-tab {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.func-cases-toolbar {
	display: flex;
	justify-content: flex-end;
	padding: 10px 4px 4px 4px;
}

/* Tab 下划线样式（参考 ApiEdit .drawer-tabs） */
.dynamic-tabs :deep(.el-tabs__header) {
	margin: 0 0 0 -5px;
	padding: 0;
	background: var(--qm-bg-2);
	border-bottom: 1px solid var(--qm-line-strong);
	overflow: visible !important;
}
.dynamic-tabs :deep(.el-tabs__nav-wrap) {
	overflow: visible !important;
}
.dynamic-tabs :deep(.el-tabs__nav-scroll) {
	overflow: visible !important;
}
.dynamic-tabs :deep(.el-tabs__nav-wrap::after) {
	display: none;
}
.dynamic-tabs :deep(.el-tabs__active-bar) {
	display: none;
}
.dynamic-tabs :deep(.el-tabs__item) {
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
.dynamic-tabs :deep(.el-tabs__item:first-child) {
	margin-left: 0;
}
.dynamic-tabs :deep(.el-tabs__item::after) {
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
.dynamic-tabs :deep(.el-tabs__item:hover) {
	color: #f59e0b;
}
.dynamic-tabs :deep(.el-tabs__item:hover::after) {
	width: 100%;
	background: rgba(245, 158, 11, 0.5);
}
.dynamic-tabs :deep(.el-tabs__item.is-active) {
	color: #f59e0b;
	font-weight: 600;
}
.dynamic-tabs :deep(.el-tabs__item.is-active::after) {
	width: 100%;
	background: #f59e0b;
}
.dynamic-tabs :deep(.el-tabs__content) {
	flex: 1;
	padding: 0;
	display: flex;
	flex-direction: column;
	min-height: 0;
}

.func-case-name {
	color: #f59e0b;
	cursor: pointer;
	transition: color 0.2s;
}
.func-case-name:hover {
	color: #66b1ff;
	text-decoration: underline;
}

.tags-container {
	display: flex;
	flex-wrap: wrap;
	gap: 4px;
	justify-content: center;
}
.case-tag {
	margin: 0;
}

.auto-info-cell {
	display: flex;
	flex-direction: column;
	gap: 4px;
	align-items: center;
}
.auto-type-badge {
	display: inline-block;
	padding: 2px 8px;
	border-radius: 4px;
	font-size: 12px;
	line-height: 18px;
}
.auto-type-1 {
	background: #e1f3d8;
	color: #67c23a;
}
.auto-type-2 {
	background: #fdf6ec;
	color: #e6a23c;
}
.auto-type-3 {
	background: #f4f4f5;
	color: var(--qm-text-3);
}
.auto-status-badge {
	display: inline-block;
	padding: 2px 8px;
	border-radius: 4px;
	font-size: 12px;
	line-height: 18px;
}
.auto-status-1 {
	background: #e1f3d8;
	color: #67c23a;
}
.auto-status-2 {
	background: #ecf5ff;
	color: #f59e0b;
}
.auto-status-3 {
	background: #fdf6ec;
	color: #e6a23c;
}

.user-time-cell {
	display: flex;
	flex-direction: column;
	gap: 4px;
	font-size: 12px;
}
.user-time-cell .user-info,
.user-time-cell .time-info {
	display: flex;
	align-items: center;
	gap: 4px;
	justify-content: center;
}
.user-time-cell .el-icon {
	font-size: 12px;
	color: var(--qm-text-3);
}
</style>

<style>
/* ============================================
   列内下拉编辑 popper 样式（参考 FunCaseList status-dropdown-popper）
   ============================================ */
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

.status-dropdown-popper .status-indicator.danger {
	background: #ef4444;
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

.status-dropdown-popper .status-indicator.info {
	background: var(--qm-text-3);
}

.status-dropdown-popper .status-indicator.purple {
	background: #f97316;
}

.status-dropdown-popper .status-indicator.cyan {
	background: #d97706;
}

.status-dropdown-popper .status-indicator.pink {
	background: #ec4899;
}

.status-dropdown-popper .status-indicator.orange {
	background: #ea580c;
}

.status-dropdown-popper .status-text {
	font-size: 14px;
	font-weight: 500;
	color: var(--qm-text-2);
}

/* 处理人下拉菜单（用户多时支持滚动） */
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

/* ============================================
   抽屉样式 - 全局样式（因 append-to-body 导致 scoped 失效）
   参考 FunCaseList.vue 的 .step 抽屉布局
   ============================================ */

/* 抽屉主体 - 外层不滚动，使用 flex 布局 */
html body .el-drawer.defect-drawer .el-drawer__body,
html body .el-overlay.defect-drawer .el-drawer__body,
html body .el-overlay .defect-drawer .el-drawer__body {
	padding: 20px !important;
	overflow: hidden !important;
	height: 100%;
	display: flex;
	flex-direction: column;
	background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
}

/* 内容卡片 - flex 链第 1 层 */
html body .defect-drawer .content-card {
	flex: 1;
	background: var(--qm-bg-2);
	border: none;
	border-radius: 16px 16px 0 0;
	display: flex;
	flex-direction: column;
	min-height: 0;
	overflow: hidden;
}

/* el-card body - flex 链第 2 层，去掉默认 padding，传递 flex 高度 */
html body .defect-drawer .content-card .el-card__body {
	flex: 1;
	display: flex;
	flex-direction: column;
	min-height: 0;
	padding: 0;
	overflow: hidden;
}

/* el-form - flex 链第 3 层，传递 flex 高度 */
html body .defect-drawer .content-card .el-card__body > .el-form {
	flex: 1;
	display: flex;
	flex-direction: column;
	min-height: 0;
	overflow: hidden;
	padding: 0;
	box-sizing: border-box;
}

/* 左侧上部 - 标题 + 创建/更新信息，固定高度不参与 flex 收缩 */
html body .defect-drawer .drawer-left-header {
	padding: 16px 20px 12px 20px;
	background: var(--qm-bg-2);
	display: flex;
	flex-direction: column;
	gap: 8px;
	flex-shrink: 0;
	border-bottom: 1px solid var(--qm-bg-3);
	border-radius: 12px 12px 0 0;
}

/* 第一行：标题输入 */
html body .defect-drawer .header-top {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 20px;
	flex-wrap: nowrap;
	min-height: 36px;
}

/* 创建/更新信息区域（标题下方右对齐） */
html body .defect-drawer .case-meta-section {
	display: flex;
	justify-content: flex-end;
	margin-top: 8px;
}

html body .defect-drawer .case-meta {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: 12px;
	font-size: 13px;
	color: var(--qm-text-2);
}

html body .defect-drawer .meta-item {
	display: flex;
	align-items: center;
	gap: 8px;
}

html body .defect-drawer .meta-label {
	color: var(--qm-text-3);
	font-weight: 500;
}

html body .defect-drawer .meta-value {
	color: var(--qm-text-2);
	font-weight: 600;
}

html body .defect-drawer .meta-divider {
	width: 1px;
	height: 14px;
	background: var(--qm-line-strong);
}

/* drawer 左右分栏布局 - flex 链第 4 层 */
html body .defect-drawer .drawer-split-layout {
	display: flex;
	gap: 16px;
	flex: 1;
	min-height: 0;
	overflow: hidden;
	padding: 20px 20px 0px 20px;
	box-sizing: border-box;
}

/* 左侧容器 - 上下分栏（上：header，下：富文本），自适应宽度 */
html body .defect-drawer .drawer-left {
	flex: 1;
	min-width: 0;
	min-height: 0;
	display: flex;
	flex-direction: column;
	background: var(--qm-bg-2);
	border: 1px solid var(--qm-bg-3);
	border-radius: 12px;
	overflow: hidden;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
	padding: 0;
}

/* 左侧下部 - 富文本编辑区域，内部滚动 */
html body .defect-drawer .drawer-left .drawer-left-content {
	flex: 1;
	overflow-y: auto;
	overflow-x: hidden;
	min-height: 0;
	padding: 20px 20px 40px 20px;
}

/* 滚动条样式，作用于富文本滚动容器 */
html body .defect-drawer .drawer-left-content::-webkit-scrollbar {
	width: 8px;
}

html body .defect-drawer .drawer-left-content::-webkit-scrollbar-track {
	background: var(--qm-bg-3);
	border-radius: 4px;
}

html body .defect-drawer .drawer-left-content::-webkit-scrollbar-thumb {
	background: var(--qm-line-strong);
	border-radius: 4px;
}

html body .defect-drawer .drawer-left-content::-webkit-scrollbar-thumb:hover {
	background: var(--qm-text-3);
}

/* 右侧容器 - 基础信息，300px 固定宽度，内部可滚动 */
html body .defect-drawer .drawer-right {
	width: 300px;
	flex-shrink: 0;
	min-height: 0;
	display: flex;
	flex-direction: column;
	background: var(--qm-bg-2);
	border: 1px solid var(--qm-bg-3);
	border-radius: 12px;
	overflow: hidden;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
	padding: 20px 20px 40px 20px;
	overflow-y: auto;
}

/* 右侧滚动条样式 */
html body .defect-drawer .drawer-right::-webkit-scrollbar {
	width: 8px;
}

html body .defect-drawer .drawer-right::-webkit-scrollbar-track {
	background: var(--qm-bg-3);
	border-radius: 4px;
}

html body .defect-drawer .drawer-right::-webkit-scrollbar-thumb {
	background: var(--qm-line-strong);
	border-radius: 4px;
}

html body .defect-drawer .drawer-right::-webkit-scrollbar-thumb:hover {
	background: var(--qm-text-3);
}

/* 右侧标题样式 */
html body .defect-drawer .drawer-right-title span {
	font-size: 18px;
	font-weight: 700;
	color: var(--qm-text-1);
	padding-left: 14px;
	padding-bottom: 5px;
	position: relative;
	display: inline-block;
	line-height: 1.5;
}

html body .defect-drawer .drawer-right-title span::before {
	content: '';
	position: absolute;
	left: 0;
	top: 50%;
	transform: translateY(-50%);
	width: 4px;
	height: 18px;
	background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
	border-radius: 2px;
}

/* 左侧基础信息表单 */
html body .defect-drawer .step-base-info {
	background: transparent;
	padding: 0;
	border-radius: 0;
	border: none;
	margin-bottom: 0;
}

html body .defect-drawer .step-base-info .el-form-item {
	margin-bottom: 16px;
}

html body .defect-drawer .step-base-info .el-form-item__label {
	font-weight: 400;
	color: var(--qm-text-2);
	font-size: 13px;
	padding-bottom: 4px;
}

html body .defect-drawer .step-base-info .meta-form-item .el-input__wrapper {
	background: var(--qm-bg-1);
	box-shadow: none;
}

html body .defect-drawer .step-base-info .meta-form-item .el-input__inner {
	color: var(--qm-text-2);
	-webkit-text-fill-color: var(--qm-text-2);
}

html body .defect-drawer .meta-divider-line {
	margin: 8px 0 20px 0;
}

html body .defect-drawer .step-base-info .el-select,
html body .defect-drawer .step-base-info .el-cascader,
html body .defect-drawer .step-base-info .el-input,
html body .defect-drawer .step-base-info .el-date-editor {
	width: 100%;
}

/* 折叠面板样式（应用于右侧富文本区，全局穿透） */
html body .defect-drawer .step-collapse-panel {
	padding: 0px 0px;
	background: var(--qm-bg-2);
	border: none;
}

html body .defect-drawer .step-collapse-panel .el-collapse-item__header {
	font-weight: 600;
	background: var(--qm-bg-1);
	padding: 0 20px !important;
	border-radius: 8px !important;
	margin-bottom: 8px !important;
	border: 1px solid var(--qm-line-strong) !important;
	height: 60px !important;
	min-height: 60px !important;
	max-height: 60px !important;
	display: flex !important;
	align-items: center !important;
	flex-wrap: nowrap !important;
	overflow: hidden !important;
	font-size: 15px !important;
	color: var(--qm-text-1) !important;
	transition: all 0.3s ease !important;
}

html body .defect-drawer .step-collapse-panel .el-collapse-item__content {
	padding: 20px;
	background: var(--qm-bg-2);
	border-radius: 8px;
	border: 1px solid var(--qm-line-strong);
	border-top: none;
	margin-bottom: 16px;
}

html body .defect-drawer .step_item_card {
	background: transparent;
	margin: 0 10px 8px 10px;
	border: none;
	border-radius: 0;
	overflow: visible;
	box-shadow: none;
}

html body .defect-drawer .step_item_card .el-card__body {
	padding: 0 !important;
}

html body .defect-drawer .section-divider {
	display: flex !important;
	align-items: center !important;
	justify-content: space-between !important;
	width: 100% !important;
	height: 100% !important;
	margin: 0 !important;
	padding: 0 !important;
	line-height: 1 !important;
}

html body .defect-drawer .section-title {
	margin: 0 !important;
	padding: 0 !important;
	padding-left: 20px !important;
	font-size: 16px !important;
	font-weight: 600 !important;
	color: var(--qm-text-2) !important;
	line-height: 1.5 !important;
	display: flex !important;
	align-items: center !important;
	position: relative !important;
	height: 100% !important;
}

html body .defect-drawer .section-title::before {
	content: '';
	position: absolute;
	left: 0;
	top: 50%;
	transform: translateY(-50%);
	width: 4px;
	height: 20px;
	background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
	border-radius: 2px;
	margin: 0 !important;
}

/* 评论动态区域 */
html body .defect-drawer .comment-section-card {
	margin-top: 8px;
}

html body .defect-drawer .comment-section-title {
	padding: 12px 0;
	margin-bottom: 8px;
}

html body .defect-drawer .comments-container {
	padding: 4px 0;
}

html body .defect-drawer .comment-input-area {
	margin-bottom: 20px;
	padding: 16px;
	background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
	border-radius: 10px;
	border: 1px solid var(--qm-line-strong);
}

html body .defect-drawer .comment-actions {
	display: flex;
	justify-content: flex-end;
	margin-top: 10px;
	gap: 8px;
}

/* 评论中@提及用户的渲染样式 */
html body .defect-drawer .rich-text-view .at-mention,
html body .defect-drawer .edit-comment-area .at-mention {
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

html body .defect-drawer .comments-list {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

html body .defect-drawer .comment-item {
	padding: 14px 16px;
	background: var(--qm-bg-2);
	border-radius: 10px;
	border: 1px solid var(--qm-bg-3);
	transition: all 0.2s ease;
}

html body .defect-drawer .comment-item:hover {
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
	border-color: var(--qm-line-strong);
}

html body .defect-drawer .comment-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 10px;
}

html body .defect-drawer .comment-user {
	display: flex;
	align-items: center;
	gap: 10px;
}

html body .defect-drawer .comment-user .user-avatar {
	background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
	color: white;
	font-weight: 600;
	border: 2px solid white;
	box-shadow: 0 2px 8px rgba(245, 158, 11, 0.2);
}

html body .defect-drawer .comment-user .user-name {
	font-size: 14px;
	font-weight: 600;
	color: var(--qm-text-2);
}

html body .defect-drawer .comment-time {
	font-size: 12px;
	color: var(--qm-text-3);
}

html body .defect-drawer .comment-content {
	padding-left: 42px;
	line-height: 1.6;
	color: var(--qm-text-2);
}

html body .defect-drawer .comment-actions-right {
	display: flex;
	align-items: center;
	gap: 12px;
}

html body .defect-drawer .comment-actions-btns {
	display: flex;
	align-items: center;
	gap: 4px;
}

html body .defect-drawer .comment-actions-btns .el-button {
	padding: 0;
	min-width: auto;
}

html body .defect-drawer .delete-btn {
	color: #ef4444 !important;
}

html body .defect-drawer .delete-btn:hover {
	color: #dc2626 !important;
}

html body .defect-drawer .edit-comment-area {
	margin-top: 8px;
}

html body .defect-drawer .edit-actions {
	display: flex;
	justify-content: flex-end;
	gap: 8px;
	margin-top: 10px;
}

html body .defect-drawer .rich-text-view {
	word-break: break-word;
}

html body .defect-drawer .rich-text-view p {
	margin: 0 0 8px 0;
}

html body .defect-drawer .rich-text-view p:last-child {
	margin-bottom: 0;
}

/* 抽屉底部按钮 - 固定在底部，与卡片融为一体 */
html body .defect-drawer .drawer-footer {
	padding: 16px 24px;
	border-top: 1px solid var(--qm-bg-3);
	background: var(--qm-bg-2);
	border-radius: 0 0 16px 16px;
	z-index: 10;
	display: flex;
	justify-content: flex-end;
	align-items: center;
	gap: 12px;
	flex-shrink: 0;
}

/* 标题区域样式（全局穿透，因 append-to-body） */
html body .defect-drawer .case-title-area {
	flex: 1 !important;
	min-width: 0 !important;
	position: relative;
	padding-left: 12px;
}

html body .defect-drawer .case-title-area::before {
	content: '';
	position: absolute;
	left: 0;
	top: 50%;
	transform: translateY(-50%);
	width: 4px;
	height: 16px;
	background: linear-gradient(to bottom, #f59e0b, #d97706);
	border-radius: 2px;
}

/* ============================================
   功能用例详情抽屉（teleported via append-to-body，需全局样式）
   样式参考 TestPlanDetail 的 case-detail-drawer
   ============================================ */
html body .func-case-detail-drawer.el-drawer.rtl {
	margin: 0;
	height: 100vh;
	width: calc(100vw - 260px) !important;
	border-radius: 16px 0 0 16px;
	box-shadow: -8px 0 40px rgba(0, 0, 0, 0.15);
	border-left: 1px solid rgba(255, 255, 255, 0.8);
	background: linear-gradient(135deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
}
html body .el-overlay .func-case-detail-drawer .el-drawer__body {
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

/* 顶部标题栏 */
html body .func-case-detail-drawer .detail-header {
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
html body .func-case-detail-drawer .title-area {
	display: flex;
	align-items: center;
	gap: 12px;
}
html body .func-case-detail-drawer .drawer-title {
	margin: 0;
	font-size: 20px;
	font-weight: 700;
	color: var(--qm-text-1);
	position: relative;
	padding-left: 16px;
}
html body .func-case-detail-drawer .drawer-title::before {
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
html body .func-case-detail-drawer .copy-btn {
	padding: 6px;
}

/* 左侧垂直导航 - 导航右边框紧贴弹窗左边框，顶部对齐 */
html body .func-case-detail-drawer .detail-nav-wrapper {
	position: fixed;
	left: calc(260px - 72px);
	top: 0;
	width: 72px;
	z-index: 1000;
}
html body .func-case-detail-drawer .vertical-nav {
	background: var(--qm-bg-2);
	border-radius: 12px;
	padding: 4px 0;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
	border: 1px solid var(--qm-bg-3);
	overflow: hidden;
	width: 72px;
}
html body .func-case-detail-drawer .nav-item {
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
}
html body .func-case-detail-drawer .nav-item:hover {
	color: #f59e0b;
	background: rgba(245, 158, 11, 0.05);
}
html body .func-case-detail-drawer .nav-item.active {
	color: #f59e0b;
	font-weight: 600;
	background: linear-gradient(90deg, rgba(245, 158, 11, 0.08) 0%, transparent 100%);
}
html body .func-case-detail-drawer .nav-item.active::before {
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
html body .func-case-detail-drawer .nav-text {
	line-height: 1.4;
}

/* 内容容器 */
html body .func-case-detail-drawer .case-detail-container {
	display: flex;
	gap: 24px;
	padding: 24px;
	flex: 1;
	overflow-y: auto;
	overflow-x: hidden;
	background: var(--qm-bg-1);
	scrollbar-width: none;
	-ms-overflow-style: none;
}
html body .func-case-detail-drawer .case-detail-container::-webkit-scrollbar {
	display: none;
}
html body .func-case-detail-drawer .case-detail-main {
	flex: 1;
	min-width: 0;
}

/* 分区卡片 */
html body .func-case-detail-drawer .section-card {
	margin-bottom: 20px;
	border: none;
	border-radius: 8px;
	box-shadow: 0 1px 10px rgba(0, 0, 0, 0.05);
	transition: all 0.2s ease;
	scroll-margin-top: 20px;
}
html body .func-case-detail-drawer .section-card:hover {
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}
html body .func-case-detail-drawer .section-card .el-card__body {
	padding: 24px 28px;
}
html body .func-case-detail-drawer .section-divider {
	display: flex;
	align-items: center;
	margin-bottom: 12px;
}
html body .func-case-detail-drawer .section-title {
	font-size: 15px;
	font-weight: 600;
	color: var(--qm-text-1);
	position: relative;
	padding-left: 12px;
}
html body .func-case-detail-drawer .section-title::before {
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
html body .func-case-detail-drawer .section-content {
	padding: 12px 0;
}

/* 基础信息表单项 */
html body .func-case-detail-drawer .form-item {
	margin-bottom: 22px;
}
html body .func-case-detail-drawer .form-label {
	display: block;
	font-size: 13px;
	font-weight: 600;
	color: var(--qm-text-1);
	margin-bottom: 6px;
}
html body .func-case-detail-drawer .form-value {
	font-size: 14px;
	font-weight: 400;
	color: var(--qm-text-2);
	line-height: 1.5;
}
html body .func-case-detail-drawer .tag-item {
	display: inline-flex;
	align-items: center;
	padding: 2px 10px;
	background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
	color: white;
	border-radius: 12px;
	font-size: 12px;
	margin-right: 6px;
}

/* 富文本内容 */
html body .func-case-detail-drawer .rich-content {
	padding: 12px 0;
}
html body .func-case-detail-drawer .steps-content {
	padding: 12px 0;
}
html body .func-case-detail-drawer .rich-text-view {
	min-height: 30px;
	line-height: 1.6;
	color: var(--qm-text-1);
	word-break: break-word;
	font-size: 13px;
}
html body .func-case-detail-drawer .rich-text-view p {
	margin: 8px 0;
}
html body .func-case-detail-drawer .rich-text-view ul,
html body .func-case-detail-drawer .rich-text-view ol {
	padding-left: 20px;
	margin: 8px 0;
}

/* 关联脚本用例表格 */
html body .func-case-detail-drawer .elegant-table {
	border-radius: 8px;
	overflow: hidden;
}
html body .func-case-detail-drawer .index-cell {
	font-weight: 600;
	color: var(--qm-text-2);
}
html body .func-case-detail-drawer .case-info-cell {
	display: flex;
	flex-direction: column;
	gap: 6px;
	align-items: center;
}
html body .func-case-detail-drawer .case-type-badge {
	display: flex;
	justify-content: center;
}
html body .func-case-detail-drawer .case-name {
	font-size: 13px;
	color: var(--qm-text-1);
	font-weight: 500;
}
html body .func-case-detail-drawer .tags-container {
	display: flex;
	flex-wrap: wrap;
	gap: 4px;
	justify-content: center;
}
html body .func-case-detail-drawer .case-tag {
	margin: 0;
}
html body .func-case-detail-drawer .user-time-cell {
	display: flex;
	flex-direction: column;
	gap: 4px;
	font-size: 12px;
}
html body .func-case-detail-drawer .user-time-cell .user-info,
html body .func-case-detail-drawer .user-time-cell .time-info {
	display: flex;
	align-items: center;
	gap: 4px;
	justify-content: center;
}
html body .func-case-detail-drawer .user-time-cell .el-icon {
	font-size: 12px;
	color: var(--qm-text-3);
}
</style>
