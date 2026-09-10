<template>
  
  <!-- AI生成元素对话框 -->
  <el-dialog v-model="aiGenerateVisible" title="AI生成元素" width="520" draggable class="elegant-dialog">
    <el-form class="dialog-form" label-position="top" @submit.prevent>
      <el-alert
        title="AI将访问所选范围(模块或平台下所有模块)的页面，自动识别交互元素并生成/更新元素库记录（进行中的任务可在站内信查看）。"
        type="info"
        :closable="false"
        show-icon
        class="tip-alert ai-alert"
      />
      <el-form-item class="dialog-form-item">
        <label class="dialog-label">环境<span class="ai-required">*</span></label>
        <el-select v-model="aiEnvId" placeholder="请选择环境" class="select" size="large" popper-class="select-dropdown-rounded" style="width:100%">
          <el-option v-for="env in aiEnvs" :key="env.id" :label="env.name" :value="env.id" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="aiShowPagePath" class="dialog-form-item">
        <label class="dialog-label">页面路径<span class="ai-required">*</span></label>
        <el-input
          v-model.trim="aiPagePath"
          placeholder="请输入页面路径，如 /login"
          class="select"
          size="large"
          clearable
          @blur="aiPagePath = (aiPagePath || '').trim()"
        />
        <div class="ai-pagepath-tip">将拼接到所选环境平台域名后访问（如 {域名}{页面路径}）</div>
      </el-form-item>
      <el-form-item class="dialog-form-item">
        <label class="dialog-label">AI模型<span class="ai-required">*</span></label>
        <el-select v-model="aiConfigId" placeholder="请选择AI模型" class="select" size="large" popper-class="select-dropdown-rounded" style="width:100%">
          <el-option v-for="c in aiConfigs" :key="c.id" :label="c.provider_name + ' / ' + c.model_name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item class="dialog-form-item">
        <label class="dialog-label">识别阈值<span class="ai-tip">（向量去重相似度，越大越严格）</span></label>
        <div class="ai-threshold-row">
          <el-slider
            v-model="aiVectorThreshold"
            :min="0.5"
            :max="0.9"
            :step="0.05"
            :show-tooltip="false"
            class="ai-threshold-slider"
          />
          <span class="ai-threshold-value">{{ aiVectorThreshold.toFixed(2) }}</span>
        </div>
      </el-form-item>
      <el-form-item class="dialog-form-item">
        <div class="ai-login-row">
          <label class="ai-login-label">页面需登录</label>
          <el-switch v-model="aiNeedLogin" />
          <span class="ai-login-tip">开启后使用所选环境的登录态(Cookie)访问</span>
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="aiGenerateVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button type="primary" :loading="aiSubmitting" :disabled="!aiEnvId || !aiConfigId" class="dialog-confirm-btn" @click="submitAiGenerate">开始生成</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 批量修改状态弹窗 -->
  <el-dialog v-model="batchStatusDialogVisible" title="批量修改元素状态" width="420px" class="elegant-dialog" append-to-body>
    <el-form label-position="top" class="dialog-form">
      <el-form-item class="dialog-form-item">
        <label class="dialog-label">目标状态</label>
        <el-select v-model="batchStatusValue" placeholder="请选择状态" class="select" size="large" popper-class="select-dropdown-rounded">
          <el-option label="待修改" :value="0" />
          <el-option label="已发布" :value="1" />
          <el-option label="待废弃" :value="2" />
        </el-select>
      </el-form-item>
      <div class="batch-tip">将对已选 {{ multipleSelection.length }} 个元素修改状态</div>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="batchStatusDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button type="primary" :loading="batchSubmitting" class="dialog-confirm-btn" @click="confirmBatchStatus">确定</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 批量删除确认弹窗 -->
  <el-dialog v-model="batchDeleteDialogVisible" title="批量删除元素" width="500px" class="elegant-dialog" append-to-body>
    <div class="batch-tip">
      确定要删除已选 {{ multipleSelection.length }} 个元素吗？删除后不可恢复。
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="batchDeleteDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button type="danger" :loading="batchSubmitting" class="dialog-confirm-btn" @click="confirmBatchDelete">确定删除</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 导入接口对话框 -->
  <el-dialog v-model="elementExportVisible" title="导入元素" width="800" draggable class="elegant-dialog">
	 <!-- 提示文案 -->
	  <el-alert
		title="把需导入的页面Html和下面Json格式给AI,让AI自动生成页面的所有元素数据的Json"
		type="info"
		:closable="false"
		show-icon
		class="tip-alert"
	  />
	<v-ace-editor v-model:value='elementExportValue' lang='json' theme='chrome' style="height: 400px" :options='editOption'/>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="()=>{elementExportVisible = false}" class="dialog-cancel-btn">取消</el-button>
        <el-button type="primary" @click="exportElement" class="dialog-confirm-btn">确定</el-button>
      </div>
    </template>
  </el-dialog>
  
  <div class="case-management-container">
    <!-- 左侧模块树 -->
    <div class="sidebar-card elegant-shadow">
      <div class="sidebar-header">
        <div class="sidebar-title-wrapper">
          <i class="icon-tree"></i>
          <h3 class="sidebar-title">模块树</h3>
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
            :data='module_tree' 
            :props="{label: 'name', children: 'children'}" 
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
                  <i class="icon-folder-tree" :class="{ 
                    'icon-folder-tree-root': data.id < 0,
                    'icon-page-node': data.node_type === 'page',
                    'icon-module-node': data.node_type === 'module'
                  }"></i>
                  <el-tooltip :content="node.label" :show-after="500">
                    <span class="node-label">{{ node.label }}</span>
                  </el-tooltip>
                </div>
                <div class="node-actions">
                  <el-dropdown @command="controlCommand" trigger="click">
                    <el-button class="node-dropdown-btn" circle size="small">
                      <el-icon><Setting /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item v-if='permission.has_add_permission' :command="{ action: 'add', node: node }">
                          <el-icon><Plus /></el-icon>新增
                        </el-dropdown-item>
                        <el-dropdown-item v-if='permission.has_edit_permission && node.data.id > 0' divided :command="{ action: 'edit', node: node }">
                          <el-icon><EditPen /></el-icon>编辑
                        </el-dropdown-item>
                        <el-dropdown-item v-if='permission.has_delete_permission && node.data.id > 0' divided :command="{ action: 'delete', node: node }" class="danger-item">
                          <el-icon><Delete /></el-icon>删除
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
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
      <!-- 搜索筛选区域 -->
      <el-card class="filter-card elegant-shadow" >
        <div class="filter-header">
          <div class="header-title-section">
            <i class="icon-search"></i>
            <h3 class="filter-title">元素筛选</h3>
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
          <el-form :model="elementSearch" class="filter-form inline-form">
            <el-row :gutter="24">
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="form-item-enhanced">
                  <div class="label-with-icon">
                    <i class="icon-id"></i>
                    <span class='label-text'>元素ID</span>
                  </div>
				  <el-input
				    v-model="elementSearch.id" 
				    placeholder="请输入元素ID" 
				    clearable
				    size='large'
				    class="input"
				  />
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="form-item-enhanced">
                  <div class="label-with-icon">
                    <i class="icon-name"></i>
                    <span>元素名称</span>
                  </div>
                  <el-input
                    v-model="elementSearch.name" 
                    placeholder="请输入元素名称" 
                    clearable
                    size='large'
                    class="input"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="form-item-enhanced">
                  <div class="label-with-icon">
                    <i class="icon-type"></i>
                    <span>元素类型</span>
                  </div>
                  <el-select
                    v-model="elementSearch.type" 
                    placeholder="请选择元素类型" 
                    clearable
                    size='large'
                    class="select"
                    popper-class='select-dropdown-rounded'
                  >
                    <el-option label="web" value="web" />
                    <el-option label="app" value="app" />
                  </el-select>
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="form-item-enhanced">
                  <div class="label-with-icon">
                    <i class="icon-status"></i>
                    <span>元素状态</span>
                  </div>
                  <el-select
                    v-model="elementSearch.status" 
                    placeholder="请选择元素状态" 
                    clearable
                    size='large'
                    class="select"
                    popper-class='select-dropdown-rounded'
                  >
                    <el-option label="待修改" :value="0" />
                    <el-option label="已发布" :value="1" />
                    <el-option label="待废弃" :value="2" />
                  </el-select>
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="form-item-enhanced">
                  <div class="label-with-icon">
                    <i class="icon-creator"></i>
                    <span>创建人</span>
					
                  </div>
                  <el-select
                    v-model="elementSearch.create_by" 
                    placeholder="请选择创建人" 
                    clearable 
                    filterable
                    size='large'
                    class="select"
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
              
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="form-item-enhanced">
                  <div class="label-with-icon">
                    <i class="icon-updater"></i>
                    <span>更新人</span>
                  </div>
                  <el-select
                    v-model="elementSearch.update_by" 
                    placeholder="请选择更新人" 
                    clearable 
                    filterable
                    size='large'
                    class="select"
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
              <h3 class="content-title">元素列表</h3>
              <div class="stats-info">
                <div class="stat-item">
                  <span class="stat-label">总计</span>
                  <span class="stat-value">{{ module_list.count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">当前页</span>
                  <span class="stat-value">{{ page_size_params.page }}</span>
                </div>
              </div>
            </div>
			<div class="content-actions">
				<el-dropdown
				  v-if="permission.has_edit_permission || permission.has_delete_permission"
				  @command="handleBatchCommand"
				  :disabled="multipleSelection.length === 0"
				  class="batch-dropdown"
				  popper-class="batch-dropdown-popper"
				>
				  <el-button class="toolbar-btn" :disabled="multipleSelection.length === 0">
				    <el-icon><Setting /></el-icon>批量操作
				  </el-button>
				  <template #dropdown>
				    <el-dropdown-menu>
				      <el-dropdown-item command="status" class="batch-dropdown-item">
				        <span class="item-text">批量修改状态</span>
				      </el-dropdown-item>
				      <el-dropdown-item command="delete" class="batch-dropdown-item">
				        <span class="item-text">批量删除</span>
				      </el-dropdown-item>
				    </el-dropdown-menu>
				  </template>
				</el-dropdown>
				<el-button
				  v-if='permission.has_add_permission && canAiGenerate'
				  @click="openAiGenerate"
				  type='primary'
				  class="search-btn"
				>
				  <el-icon><MagicStick /></el-icon>AI生成
				</el-button>
				<el-button
				  v-if='permission.has_add_permission' 
				  @click="addElement"  
				  type='primary'
				  class="add-btn"
				>
				  <el-icon><Plus /></el-icon>新增元素
				</el-button>
			</div>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="table-wrapper">
          <el-table 
            :max-height="'calc(100vh - 540px)'" 
            :data="module_list.results" 
            class="elegant-table" 
            :show-overflow-tooltip='true'
			 @sort-change='handleSortChange'
            @selection-change="handleSelectionChange"
            :header-row-style="headerRowStyle"
          > 
			
            <el-table-column type="selection" width="55" align="center"></el-table-column>
            
            <el-table-column 
              label="ID" 
              width="70" 
              prop="id"
              align="center"
              class-name="id-column"
            >
              <template #default="scope">
                <div class="id-cell">
                  {{ scope.row.id }}
                </div>
              </template>
            </el-table-column>
            
            <el-table-column 
              label="元素名称" 
              prop="name" 
              min-width="120" 
              align="center"
              class-name="name-column"
            />
            
			<el-table-column
			  label="元素类型" 
			  prop="type" 
			  width="100" 
			  align="center"
			  class-name="type-column"
			>
			  <template #default="scope">
			    <el-tag 
			      :type="scope.row.type === 'web' ? 'primary' : 'success'" 
			      effect="light"
			      class="type-tag"
			    >
			      {{ scope.row.type }}
			    </el-tag>
			  </template>
			</el-table-column>
            
			<el-table-column
			  label="元素状态" 
			  prop="status" 
			  width="130" 
			  align="center"
			  class-name="status-column"
			>
			  <template #default="scope">
			    <el-dropdown
			      v-if="permission.has_edit_permission"
			      trigger="click"
			      @command="(val) => updateStatus(scope.row, val)"
			      class="status-dropdown"
			      popper-class="status-dropdown-popper"
			    >
			      <span class="status-badge" :class="'element-status-' + scope.row.status">
			        <span class="status-dot"></span>
			        <span class="status-label">{{ scope.row.status_display || '-' }}</span>
			        <el-icon class="status-arrow"><ArrowDown /></el-icon>
			      </span>
			      <template #dropdown>
			        <el-dropdown-menu>
			          <el-dropdown-item :command="0" class="status-dropdown-item">
			            <span class="status-indicator info"></span>
			            <span class="status-text">待修改</span>
			          </el-dropdown-item>
			          <el-dropdown-item :command="1" class="status-dropdown-item">
			            <span class="status-indicator success"></span>
			            <span class="status-text">已发布</span>
			          </el-dropdown-item>
			          <el-dropdown-item :command="2" class="status-dropdown-item">
			            <span class="status-indicator warning"></span>
			            <span class="status-text">待废弃</span>
			          </el-dropdown-item>
			        </el-dropdown-menu>
			      </template>
			    </el-dropdown>
			    <span v-else class="status-badge-static" :class="'element-status-' + scope.row.status">
			      {{ scope.row.status_display || '-' }}
			    </span>
			  </template>
			</el-table-column>
            
            
           
            <el-table-column 
              label="所属模块" 
              prop="module_name" 
              width="200" 
              align="center"
              class-name="module-column"
            />
            
            <el-table-column 
              label="创建信息" 
              width="200" 
              align="center"
			  prop="create_time"
			  sortable="custom" 
              class-name="create-info-column"
            >
              <template #default="scope">
                <div class="create-info-cell">
                  <div class="user-info">
                    <i class="icon-user"></i>
                    <span class="user-name">{{ scope.row.create_by_name || '-' }}</span>
                  </div>
                  <div class="time-info">
                    <i class="icon-time"></i>
                    <span class="time">{{ formatTime(scope.row.create_time) }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column 
              label="更新信息" 
              width="200" 
              align="center"
			  prop="update_time"
			  sortable="custom" 
              class-name="update-info-column"
            >
              <template #default="scope">
                <div class="update-info-cell">
                  <div class="user-info">
                    <i class="icon-user"></i>
                    <span class="user-name">{{ scope.row.update_by_name || '-' }}</span>
                  </div>
                  <div class="time-info">
                    <i class="icon-time"></i>
                    <span class="time">{{ formatTime(scope.row.update_time) }}</span>
                  </div>
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
                    content="查看元素" 
                    placement="top" 
                    effect="dark"
                  >
                    <el-button 
                      type="success" 
                      v-if="permission.has_read_permission" 
                      class="action-btn view-btn"
                      @click.stop="viewElement(scope.row)"
                      circle
                    >
                      <el-icon><View /></el-icon>
                    </el-button>
                  </el-tooltip>
                  
                  <el-tooltip 
                    content="编辑元素" 
                    placement="top" 
                    effect="dark"
                  >
                    <el-button 
                      type="warning" 
                      v-if="permission.has_edit_permission" 
                      class="action-btn edit-btn"
                      @click.stop="editElement(scope.row)"
                      circle
                    >
                      <el-icon><EditPen /></el-icon>
                    </el-button>
                  </el-tooltip>
                  
                  <el-tooltip 
                    content="删除元素" 
                    placement="top" 
                    effect="dark"
                  >
                    <el-button 
                      type="danger" 
                      v-if="permission.has_delete_permission" 
                      @click.stop="deleteElement(scope.row.id)" 
                      class="action-btn delete-btn"
                      circle
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                  
                  <el-tooltip 
                    content="选择元素" 
                    placement="top" 
                    effect="dark"
                  >
                    <el-button 
                      type="primary" 
                      v-if="isCanChoose === true" 
                      class="action-btn choose-btn"
                      @click.stop="chooseElementId(scope.row)"
                      circle
                    >
                      <el-icon><Pointer /></el-icon>
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
            :teleported='false'
            v-model:current-page="page_size_params.page"
            v-model:page-size="page_size_params.size"
            :page-sizes="[10, 20, 30, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="module_list.count"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            class="select input"
            :background="true"
          />
        </div>
      </el-card>
    </div>
    
    <!-- 元素表单对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      :title="title" 
      width="700"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
      <el-form 
        :model="elementSave" 
        label-position='top' 
        label-width="70px" 
        :disabled='elementView' 
        :rules="locRules" 
        ref='locRef'
        class="dialog-form"
      >
        <el-row :gutter="16">
          <el-col :span="24">
            <el-form-item  prop='name' class="dialog-form-item">
              <label class="dialog-label">
                <i class="icon-name-dialog"></i>
                元素名称
              </label>
              <el-input 
                v-model="elementSave.name" 
                autocomplete="off" 
                placeholder="请输入元素名称"
                class="input"
                maxlength="50"
                show-word-limit
                size='large'
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item prop='type' class="dialog-form-item">
              <label class="dialog-label">
                <i class="icon-type-dialog"></i>
                元素类型
              </label>
              <el-select 
                v-model="elementSave.type" 
                placeholder="请选择元素类型"
                class="select"
                size='large'
                popper-class='select-dropdown-rounded'
              >
                <el-option label="web" value="web"></el-option>
                <el-option label="app" value="app"></el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item prop='module' class="dialog-form-item" >
              <label class="dialog-label" >
                <i class="icon-page-dialog" style="margin-right: 6px;"></i>
                所属模块
              </label>
              <el-cascader 
                placeholder="请选择所属模块" 
                collapse-tags 
                v-model='elementSave.module' 
                :options="module_tree" 
                :props="editProps" 
                clearable
                class='cascader'
                size='large'
                :style="{ width: '100%' }"
              /> 
            </el-form-item>
          </el-col>
        </el-row>

		<el-form-item  prop='web' class="dialog-form-item" v-if="elementSave.type === 'web'">
		  <label class="dialog-label">
		    <i class="icon-web-dialog"></i>
		    Web元素
		  </label>
		  <el-row :gutter="16" class="loc-form">
		    <el-col :span="12">
		      <el-form-item prop="by" class="dialog-form-item">
		        <label class="dialog-label">定位方式</label>
		        <el-select v-model="elementSave.web.by" filterable default-first-option :reserve-keyword="false" size="large" class="select loc-by" popper-class="select-dropdown-rounded" placeholder="请选择定位方式" @change="ensureOpts(elementSave.web)">
		          <el-option v-for="item in web_by_list" :key="item" :label="item" :value="item" />
		        </el-select>
		      </el-form-item>
		    </el-col>
		    <el-col :span="12">
		      <el-form-item prop="web.value" class="dialog-form-item">
		        <label class="dialog-label">定位表达式</label>
		        <el-input v-model="elementSave.web.value" placeholder="请输入定位表达式" size="large" class="input loc-value" />
		      </el-form-item>
		    </el-col>
		    <el-col v-if="elementSave.web.by === 'role'" :span="12">
		      <el-form-item class="dialog-form-item loc-visible-item">
		        <label class="dialog-label">可见文本(可选)</label>
		        <el-input v-model="elementSave.web.opts.name" placeholder="role 可见文本" size="large" class="input loc-opts-name" />
		      </el-form-item>
		    </el-col>
		    <el-col v-if="elementSave.web.by === 'role' || elementSave.web.by === 'text' || elementSave.web.by === 'label'" :span="12">
		      <el-form-item class="dialog-form-item loc-exact-item">
		        <label class="dialog-label">精确匹配</label>
		        <el-switch v-model="elementSave.web.opts.exact" size="large" class="loc-exact-switch" />
		      </el-form-item>
		    </el-col>
		  </el-row>
		</el-form-item>
        
		<el-form-item  prop='android' class="dialog-form-item" v-if="elementSave.type === 'app'">
		  <label class="dialog-label">
		    <i class="icon-android-dialog"></i>
		    Android元素
		  </label>
		  <el-row :gutter="16" class="loc-form">
		    <el-col :span="12">
		      <el-form-item prop="by" class="dialog-form-item">
		        <label class="dialog-label">定位方式</label>
		        <el-select v-model="elementSave.android.by" filterable default-first-option :reserve-keyword="false" size="large" class="select loc-by" popper-class="select-dropdown-rounded" placeholder="请选择定位方式" @change="ensureOpts(elementSave.android)">
		          <el-option v-for="item in android_by_list" :key="item" :label="item" :value="item" />
		        </el-select>
		      </el-form-item>
		    </el-col>
		    <el-col :span="12">
		      <el-form-item prop="android.value" class="dialog-form-item">
		        <label class="dialog-label">定位表达式</label>
		        <el-input v-model="elementSave.android.value" placeholder="请输入定位表达式" size="large" class="input loc-value" />
		      </el-form-item>
		    </el-col>
		  </el-row>
		</el-form-item>
		
		
		<el-form-item  prop='ios' class="dialog-form-item"  v-if="elementSave.type === 'app'">
		  <label class="dialog-label">
		    <i class="icon-ios-dialog"></i>
		    Ios元素
		  </label>
		  <el-row :gutter="16" class="loc-form">
		    <el-col :span="12">
		      <el-form-item prop="by" class="dialog-form-item">
		        <label class="dialog-label">定位方式</label>
		        <el-select v-model="elementSave.ios.by" filterable default-first-option :reserve-keyword="false" size="large" class="select loc-by" popper-class="select-dropdown-rounded" placeholder="请选择定位方式" @change="ensureOpts(elementSave.ios)">
		          <el-option v-for="item in ios_by_list" :key="item" :label="item" :value="item" />
		        </el-select>
		      </el-form-item>
		    </el-col>
		    <el-col :span="12">
		      <el-form-item prop="ios.value" class="dialog-form-item">
		        <label class="dialog-label">定位表达式</label>
		        <el-input v-model="elementSave.ios.value" placeholder="请输入定位表达式" size="large" class="input loc-value" />
		      </el-form-item>
		    </el-col>
		  </el-row>
		</el-form-item>	 
		
      </el-form>
      
      <template #footer>
        <div class="dialog-footer" v-if='!elementView'>
          <el-button @click="editDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
          <el-button 
            type="primary" 
            @click="save" 
            v-if='permission.has_add_permission || permission.has_edit_permission'
            class="dialog-confirm-btn"
          >
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 页面/模块编辑对话框 -->
    <el-dialog v-model="editNodeVisible" :title="nodeTitle" width='450' class="elegant-dialog" style='border-radius: 12px !important;'>
      <div class="dialog-content">
        <el-form :model="nodeSave" label-position='top' :rules="nodeRules" ref='nodeRef' class="dialog-form" :disabled="nodeView">
          <el-form-item  prop='name' class="dialog-form-item">
            <label class="dialog-label">
              <i class="icon-module"></i>
              模块名称
            </label>
            <el-input v-model="nodeSave.name" autocomplete="off" placeholder="请输入模块名称" maxlength="20"
			  show-word-limit class="input" size='large'/>
          </el-form-item>
          <el-form-item prop='url' class="dialog-form-item">
            <label class="dialog-label">
              <i class="icon-page-dialog"></i>
              页面路径
            </label>
            <el-input v-model="nodeSave.url" autocomplete="off" placeholder="请输入页面路径（非必填）" maxlength="200"
			  show-word-limit class="input" size='large'/>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer" v-if='!nodeView'>
          <el-button @click="editNodeVisible = false" class="dialog-cancel-btn">取消</el-button>
          <el-button type="primary" @click="saveNode" class="dialog-confirm-btn">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from '../api/index.js'
import {VAceEditor} from 'vue3-ace-editor';
import { VxeUI } from 'vxe-pc-ui';
import 'ace-builds/src-noconflict/snippets/json';
import 'ace-builds/src-noconflict/mode-json';
import 'ace-builds/src-noconflict/snippets/python';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/theme-chrome';
import 'ace-builds/src-noconflict/theme-monokai';
import 'ace-builds/src-noconflict/ext-language_tools';
import ace from 'ace-builds';
import {mapState, mapActions} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Search,
  View, 
  Delete, 
  Plus, 
  EditPen, 
  Pointer,
  Setting,
  Expand,
  Fold,
  MagicStick,
  ArrowDown
} from '@element-plus/icons-vue'
import * as common from '../utils/common.js'

export default{
  name: 'ElementManagement',
  computed:{
    ...mapState(['pathPermission', 'projectInfo', 'userInfo']),
    canAiGenerate() {
      return !!(this.permission.has_add_permission && this.selectNode)
    },
    calcMinWidth() {
      let visibleButtons = 0;
      if (this.permission.has_read_permission) visibleButtons += 1;
      if (this.permission.has_edit_permission) visibleButtons += 1;
      if (this.permission.has_delete_permission) visibleButtons += 1;
      if (this.isCanChoose) visibleButtons += 1;
      return Math.max(10, visibleButtons * 60);
    }
  },
  components: {
	VAceEditor,
  },
  emits: ['update:chooseElementVisible', 'setElementData'],
  data() {
    return {
      user_list: [],
	  elementExportVisible: false,
	  aiGenerateVisible: false,
	  aiEnvs: [],
	  aiEnvId: '',
	  aiConfigs: [],
	  aiConfigId: '',
	  aiNeedLogin: false,
	  aiVectorThreshold: 0.6,
	  aiShowPagePath: false,
	  aiPagePath: '',
	  aiSubmitting: false,
	  multipleSelection: [],
	  batchStatusDialogVisible: false,
	  batchStatusValue: 1,
	  batchDeleteDialogVisible: false,
	  batchSubmitting: false,
	  elementExportValue: `[
	{
        "project":1,
        "name":"登录按钮",
        "module":1,
        "type":"web",
        "web":[{
	        "id":"eb6e3789-b286-43bd-a2f5-b514d3d19326",
	        "value":"//button[text()='登录']",
	        "by":"xpath",
	        "parentId":null,
	        "children":[]
        }],
        "android":[],
        "ios":[]
	}
]`,
	  activeName: 'first',
      elementView: false,
      props: {
        multiple: true,
        emitPath: false,
        value: 'id',
        label: 'name',
      },
      editProps:{
        emitPath: false,
        value: 'id',
        label: 'name',
		checkStrictly: true,
      },
	 
      permission: {},
      elementSearch:{
        id: '',
        name: '',
        project: '',
        module: '',
        module_list: [],
        create_by: '',
        update_by: '',
        type: '',
        status: '',
      },
      page_size_params: {
        page: 1,
        size: 10,
      },
	  sort_params: {
	    ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
	  },
      count: 1,
      title: '新增元素',
      isAdd: true,
      editDialogVisible: false,
      module_list: [],
      module_page_list: [],
      ViewVisible: false,
      tmpElementSave: {},
      elementSave:{
        project: '',
        name: '',
        module: '',
        type: 'web',
        web: { by: 'role', value: '', opts: { name: '', exact: false } },
        android: { by: '-android uiautomator', value: '', opts: { name: '', exact: false } },
        ios: { by: '-ios predicate string', value: '', opts: { name: '', exact: false } },
      },
      locRules: {
        name: [{
          required: true,
          message: '元素名称不能为空',
          trigger: 'blur',
        }],
        module: [{
          required: true,
          message: '请选择所属模块',
          trigger: 'change',
        }],
        type: [{
          required: true,
          message: '请选择元素类型',
          trigger: 'change',
        }],
        'web.value': [{
          validator: (rule, value, callback) => {
            if (this.elementSave.type === 'web' && !value) {
              callback(new Error('请输入定位表达式'))
            } else {
              callback()
            }
          },
          trigger: 'blur',
        }],
        'android.value': [{
          validator: (rule, value, callback) => {
            if (this.elementSave.type === 'app' && !value) {
              callback(new Error('请输入定位表达式'))
            } else {
              callback()
            }
          },
          trigger: 'blur',
        }],
        'ios.value': [{
          validator: (rule, value, callback) => {
            if (this.elementSave.type === 'app' && !value) {
              callback(new Error('请输入定位表达式'))
            } else {
              callback()
            }
          },
          trigger: 'blur',
        }],
      },
      web_by_list: ['role', 'label', 'placeholder', 'text', 'alt text', 'css', 'xpath', 'id'],
      android_by_list: [
        '-android uiautomator',
        '-android viewtag',
        '-android datamatcher',
        '-android viewmatcher',
        'accessibility id',
        '-image',
        '-custom',
        '-flutter semantics label',
        '-flutter type',
        '-flutter key',
        '-flutter text',
        '-flutter text containing',
      ],
      ios_by_list: [
        '-ios predicate string',
        '-ios class chain',
        'accessibility id',
        '-image',
        '-custom',
        '-flutter semantics label',
        '-flutter type',
        '-flutter key',
        '-flutter text',
        '-flutter text containing',
      ],
      // 树结构相关数据
      filterText: '',
      selectNode: 0,
      includeChildren: true,
      module_tree: [],
      nodeRules: {
        name: [{
          required: true,
          message: '模块名称不能为空',
          trigger: 'blur',
        }],
      },
      nodeSave:{
        project: '',
        name: '',
        plant: '',
        parent: 0,
        node_type: 'module', // 'module' 或 'page'
      },
      editNodeVisible: false,
      nodeTitle: '',
      nodeView: false,
      currentNode: {},
    }
  },
  props: {
    'isCanChoose': {
      type: Boolean,
      default: false,
    },
    'parentPermission': {
      type: Object,
      default: null,
    },
    'obj':{
      type: Object,
      defalut: {
        value: null
      }
    }
  },
  watch: {
    filterText(val) {
      if (this.$refs.treeRef) {
        this.$refs.treeRef.filter(val)
      }
    }
  },
  methods:{
    ...mapActions(['getRolePermission']),
    chooseElementId(data){
      this.$emit('setElementData', data)
    },
    
	goToCreatePlant(){
		this.$router.push({name: 'plant'})
	},
	
	async exportElement(){
		const response = await this.$api.import_element({value: this.elementExportValue})
		if(response.status === 200){
		  this.elementExportVisible = false
		  this.getElements()
		  ElMessage({message: "导入成功", type: 'success'})
		}
	},

	handleSelectionChange(selection){
	  this.multipleSelection = selection
	},

	handleBatchCommand(command){
	  if (command === 'status') {
	    this.batchStatusValue = 1
	    this.batchStatusDialogVisible = true
	  } else if (command === 'delete') {
	    this.batchDeleteDialogVisible = true
	  }
	},

	async confirmBatchStatus(){
	  if (this.multipleSelection.length === 0) {
	    ElMessage({message: "请先选择元素", type: 'warning'})
	    return
	  }
	  this.batchSubmitting = true
	  try {
	    const ids = this.multipleSelection.map(row => row.id)
	    const response = await this.$api.batchUpdateElements({ ids, status: this.batchStatusValue })
	    if (response.status === 200) {
	      this.batchStatusDialogVisible = false
	      ElMessage({message: "状态修改成功", type: 'success'})
	      this.getElements()
	    }
	  } catch (e) {
	    ElMessage({message: e?.detail || e?.msg || e?.message || "状态修改失败", type: 'error'})
	  } finally {
	    this.batchSubmitting = false
	  }
	},

	async confirmBatchDelete(){
	  if (this.multipleSelection.length === 0) {
	    ElMessage({message: "请先选择元素", type: 'warning'})
	    return
	  }
	  this.batchSubmitting = true
	  try {
	    const ids = this.multipleSelection.map(row => row.id)
	    const response = await this.$api.batchDeleteElements({ ids })
	    if (response.status === 200) {
	      this.batchDeleteDialogVisible = false
	      ElMessage({message: "删除成功", type: 'success'})
	      this.getElements()
	    }
	  } catch (e) {
	    ElMessage({message: e?.detail || e?.msg || e?.message || "删除失败", type: 'error'})
	  } finally {
	    this.batchSubmitting = false
	  }
	},

	async updateStatus(row, val){
	  if (row.status === val) return
	  try {
	    const response = await this.$api.batchUpdateElements({ ids: [row.id], status: val })
	    if (response.status === 200) {
	      const labelMap = { 0: '待修改', 1: '已发布', 2: '待废弃' }
	      row.status = val
	      row.status_display = labelMap[val] || row.status_display
	      ElMessage({message: "状态修改成功", type: 'success'})
	    }
	  } catch (e) {
	    ElMessage({message: e?.detail || e?.msg || e?.message || "状态修改失败", type: 'error'})
	  }
	},

	async openAiGenerate(){
	  this.aiGenerateVisible = true
	  this.aiEnvId = ''
	  this.aiConfigId = ''
	  this.aiNeedLogin = false
	  this.aiVectorThreshold = 0.6
	  // 模块维度：回显模块自带页面地址（可编辑，必填）；根节点：不显示页面路径
	  const isModule = this.selectNode && this.selectNode > 0
	  this.aiShowPagePath = !!isModule
	  if (isModule) {
	    const tree = this.$refs.treeRef
	    const node = tree ? tree.getCurrentNode() : null
	    let url = node && node.url ? node.url : ''
	    if (!url) {
	      const saved = JSON.parse(localStorage.getItem('element_node') || 'null')
	      if (saved && saved.id === this.selectNode) url = saved.url || ''
	    }
	    this.aiPagePath = url || ''
	  } else {
	    this.aiPagePath = ''
	  }
	  this.loadAiEnvs()
	  this.loadAiConfigs()
	},

	async loadAiEnvs(){
	  try {
	    const res = await this.$api.getEnvs({project: this.projectInfo.id})
	    this.aiEnvs = res.data.results || res.data.result || []
	  } catch (e) {
	    this.aiEnvs = []
	  }
	},

	async loadAiConfigs(){
	  try {
	    const res = await this.$api.getAiConfigs({is_active: true, project: this.projectInfo.id})
	    this.aiConfigs = res.data.results || res.data.result || []
	    // 未选择时默认选中默认AI配置
	    if (!this.aiConfigId) {
	      const def = this.aiConfigs.find(c => c.is_default)
	      if (def) this.aiConfigId = def.id
	    }
	  } catch (e) {
	    this.aiConfigs = []
	  }
	},

	async submitAiGenerate(){
	  if (!this.aiEnvId){
	    ElMessage({message: "请选择环境", type: 'warning'})
	    return
	  }
	  if (!this.aiConfigId){
		  ElMessage({message: "请选择AI模型", type: 'warning'})
		  return
		}
	  // 模块维度：页面路径必填，前端校验阻断
	  if (this.selectNode > 0 && !(this.aiPagePath || '').trim()){
		  ElMessage({message: "请填写页面路径", type: 'warning'})
		  return
		}
	  this.aiSubmitting = true
	  try {
	    const payload = {
	      project: this.projectInfo.id,
	      env_id: this.aiEnvId,
	      ai_config_id: this.aiConfigId,
	      need_login: this.aiNeedLogin,
	      vector_threshold: this.aiVectorThreshold,
	    }
	    if (this.selectNode < 0) {
	      payload.plant = -this.selectNode
	    } else {
	      payload.module = this.selectNode
	      payload.page_path = (this.aiPagePath || '').trim()
	    }
	    await this.$api.aiGenerateElements(payload)
	    this.aiGenerateVisible = false
	    ElMessage({message: "任务已提交，AI正在生成元素中", type: 'success'})
	  } catch (e) {
	    ElMessage({message: e?.detail || e?.msg || e?.message || "提交失败", type: 'error'})
	  } finally {
	    this.aiSubmitting = false
	  }
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
	  this.getElements()
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
      this.getElements()
    },
    
    handleSizeChange(){
      this.page_size_params.page = 1
      this.getElements()
    },
    
    search(){
      this.page_size_params.page = 1
      this.getElements()
    },
    
    reset(){
      for(let key in this.elementSearch){
        if(key === 'module_list'){
          continue
        }else{
          this.elementSearch[key] = ''
        }
      }
    },
    
    editElement(row_data){
      this.isAdd = false
      this.title = '编辑元素'
      this.elementView = false
      this.getElement(row_data.id)
      this.editDialogVisible = true
      this.$refs.locRef.resetFields();
    },
    
    viewElement(row_data){
      this.isAdd = false
      this.title = '查看元素'
      this.elementView = true
      this.getElement(row_data.id)
      this.editDialogVisible = true
    },
    
    addElement(){
      this.elementSave = {...this.tmpElementSave}
      this.elementSave.type = 'web'
      this.title = '新增元素'
      this.elementView = false
      this.editDialogVisible = true
      this.isAdd = true
	  const node = this.$refs.treeRef.getCurrentNode()
	  if ( node && node.id > 0){
	    this.elementSave.module = node.id
	  }
      this.$refs.locRef.resetFields();
    },
    
    ensureOpts(loc){
      if (loc && typeof loc === 'object' && !loc.opts) {
        this.$set(loc, 'opts', { name: '', exact: false })
      }
    },

    save(){
  	  if (this.elementSave.module < 0){
  		ElMessage({message: "所属模块不能选择根节点", type: 'error'})
  	  }else if (this.isAdd){
  	        this.createElement()
  	      }else{
  	        this.updateElement()
  	      }
  	},
    
    async createElement(){
      this.$refs['locRef'].validate(async (valid, fields)=>{
        if(valid){
          this.elementSave.project = this.projectInfo.id
          const response = await this.$api.createElement(this.elementSave)
          if(response.status === 201){
            this.editDialogVisible = false
            this.getElements()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
    },
    
    async updateElement(){
      this.$refs['locRef'].validate(async (valid, fields)=>{
        if(valid){
          this.elementSave.project = this.projectInfo.id
          const response = await this.$api.updateElement(this.elementSave.id, this.elementSave)
          if(response.status === 200){
            this.editDialogVisible = false
            this.getElements()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
    },
    
    async deleteElement(id){
      ElMessageBox.confirm(
        '确定删除此元素？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async() => {
        const response = await this.$api.deleteElement(id)
        if (response.status === 204){
          this.getElements()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }
      }).catch(() => {})
    },
    
    async getElement(id){
      const response = await this.$api.getElement(id)
      if (response.status === 200){
        this.elementSave = {...response.data.result}
        this.ensureOpts(this.elementSave.web)
        this.ensureOpts(this.elementSave.android)
        this.ensureOpts(this.elementSave.ios)
      }
    },
    
    async getElements(){
      this.elementSearch.project = this.projectInfo.id
      this.elementSave.project = this.projectInfo.id
      this.elementSearch.module = (this.elementSearch.module_list || []).join(',')
      const response = await this.$api.getElements(Object.assign(this.elementSearch, this.page_size_params, this.sort_params))
      if (response.status === 200){
        this.module_list = {...response.data}
      }
    },
    
    // 树结构相关方法
    filterNode(value, data) {
      if (!value) return true
      return data?.name?.includes(value) || false
    },
    
    moduleSelect(node){
      if (!node) {
        this.selectNode = null
        this.elementSearch.module_list = []
        this.getElements()
        return
      }
      // 如果点击的是已选中的节点，取消选中
      if (this.selectNode === node.id) {
        this.$refs.treeRef?.setCurrentKey(null)
        this.selectNode = null
        this.elementSearch.module_list = []
        localStorage.removeItem('element_node')
        this.getElements()
        return
      }
      localStorage.setItem('element_node', JSON.stringify(node))
      this.selectNode = node.id
      if (this.includeChildren) {
        this.elementSearch.module_list = this.getAllIds(node)
      } else {
        this.elementSearch.module_list = [node.id]
      }
      this.getElements()
    },
    
    onIncludeChildrenChange() {
      const node = this.$refs.treeRef?.getCurrentNode()
      if (node) {
        if (this.includeChildren) {
          this.elementSearch.module_list = this.getAllIds(node)
        } else {
          this.elementSearch.module_list = [node.id]
        }
        this.getElements()
      }
    },
    
    getAllPageIds(node) {
      const pageIds = []
      
      const traverse = (currentNode) => {
        if (currentNode.node_type === 'page') {
          pageIds.push(currentNode.id)
        } else if (currentNode.children) {
          currentNode.children.forEach(child => traverse(child))
        }
      }
      
      traverse(node)
      return pageIds
    },
    
    controlCommand(command){
      this.currentNode = command
      if(command.action === 'add'){
        this.editNodeVisible = true
        this.nodeView = false
        this.nodeTitle = '新增模块'
        this.nodeSave = {
          project: '',
          name: '',
          url: '',
          plant: '',
          parent: 0,
          node_type: 'module'
        }
      }else if(command.action === 'edit'){
        this.nodeSave = {...this.currentNode.node.data}
        this.nodeSave.url = this.nodeSave.url || ''
        this.editNodeVisible = true
        this.nodeView = false
        this.nodeTitle = '编辑模块'
      }else if(command.action === 'delete'){
        this.deleteModule(this.currentNode.node.data.id)
      }
    },
    
    async saveNode(){
      this.$refs['nodeRef'].validate(async (valid, fields)=>{
        if (valid){
          if (this.currentNode.action === 'add'){
            await this.createModule()
          }else if(this.currentNode.action === 'edit'){
            await this.updateModule()
          }
        }
      })
    },
    
   async createModule(){
     const saveData = {...this.nodeSave}
     saveData.project = this.projectInfo.id
     
     if (this.currentNode.node.data.id < 0){
       saveData.plant = -this.currentNode.node.data.id
       saveData.parent = null
     }else{
       saveData.plant = this.currentNode.node.data.plant_id || this.projectInfo.id
       saveData.parent = this.currentNode.node.data.id
     }
     
     const response = await this.$api.createModule(saveData)
     if(response.status === 201){
       this.editNodeVisible = false
       this.getPlantModule()
       ElMessage({message: "保存成功", type: 'success'})
     }
   },
   
   async updateModule(){
     const saveData = {...this.nodeSave}
     saveData.project = this.currentNode.node.data.project_id || this.projectInfo.id
     saveData.plant = this.currentNode.node.data.plant_id || this.projectInfo.id
     
     const response = await this.$api.updateModule(saveData.id, saveData)
     if(response.status === 200){
       this.editNodeVisible = false
       this.getPlantModule()
       ElMessage({message: "保存成功", type: 'success'})
     }
   },
   
   async deleteModule(id){
     ElMessageBox.confirm(
       '确定删除此模块？删除后数据将无法恢复。',
       '确认删除',
       {
         confirmButtonText: '确认删除',
         cancelButtonText: '取消',
         type: 'warning',
         confirmButtonClass: 'el-button--danger',
         customClass: 'confirm-dialog'
       }
     ).then(async() => {
       const response = await this.$api.deleteModule(id)
       if (response.status === 204){
         this.getPlantModule()
         ElMessage({
           type: 'success',
           message: '删除成功',
         })
       }
     }).catch(() => {})
   },
   
    
    expandAllNodes() {
      const allNodes = this.$refs.treeRef.store._getAllNodes()
      allNodes.forEach(node => {
        node.expanded = true
      })
    },
    
    collapseAllNodes() {
      const allNodes = this.$refs.treeRef.store._getAllNodes()
      allNodes.forEach(node => {
        node.expanded = false
      })
    },
	
	getAllIds(node) {
	  if (!node) return []
	  const ids = [node.id]
	  if (node.children && Array.isArray(node.children)) {
	    node.children.forEach(child => {
	      ids.push(...this.getAllIds(child))
	    })
	  }
	  return ids
	},

  async  check_permission(){
    console.log(this.parentPermission, '1123')
    if (this.parentPermission){
      this.permission = this.parentPermission
    }else{
       const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission['/common/element']}
       const response = await this.$api.check_permission(params)
       if (response.status === 200){
          this.permission = { ...response.data.result }
       }
    }

  },

	async getPlantModule(){
	  const response = await this.$api.getAllPlantModule({project: this.projectInfo.id})
	  if (response.status === 200){
	    this.module_tree = response.data.results
	  }
	},
  },
  created() {
    this.check_permission()
    this.user_list = JSON.parse(localStorage.getItem('user_list'))
    if(this.obj){
      this.elementSearch.id = this.obj['value']
    }
    const node = JSON.parse(localStorage.getItem('element_node'))
    if (node) {
      this.selectNode = node.id
      this.$nextTick(() => {
        if (this.$refs.treeRef) {
          this.$refs.treeRef.setCurrentKey(node.id)
        }
      })
      this.elementSearch.module_list = this.getAllIds(node)
    }
    this.getPlantModule()
    this.getElements()
    this.tmpElementSave = {...this.elementSave}
  },
}
</script>

<style scoped>
.case-management-container {
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

/* 侧边栏样式 */
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

.tree-search-input >>> .el-input__inner {
  border-radius: 10px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-1);
  padding: 0 15px;
  box-shadow: none;
  transition: all 0.3s ease;
}

.tree-search-input >>> .el-input__inner:hover {
  border-color: var(--qm-line-strong);
  background: var(--qm-bg-2);
}

.tree-search-input >>> .el-input__inner:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.tree-divider {
  margin: 16px 0;
  border-color: var(--qm-bg-3);
}

.tree-wrapper {
  flex: 1;
  padding: 0 24px;
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

.content-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 修复：节点名称过长时设置按钮被隐藏的问题 */
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
  max-width: calc(100% - 32px);
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

.icon-page-node {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
}

.icon-module-node {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z'/%3E%3C/svg%3E");
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

.node-actions {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.3s ease;
  margin-left: 8px;
}

.elegant-tree >>> .el-tree-node__content:hover .node-actions {
  opacity: 1;
}

.node-dropdown-btn {
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--qm-text-3);
  transition: all 0.3s ease;
}

.node-dropdown-btn:hover {
  background: var(--qm-bg-3);
  color: var(--qm-text-2);
}

.danger-item {
  color: #ef4444;
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
}

/* 筛选卡片 */
.filter-card {
  background: var(--qm-bg-2);
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

.batch-tip {
  color: var(--qm-text-2);
  font-size: 13px;
  line-height: 1.6;
  padding: 8px 4px;
}

/* 修改筛选区域的表单样式 */
.filter-form-wrapper {
  padding: 25px 24px 0px 24px;
  
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
    font-size: 14px;
    font-weight: 500;
    color: var(--qm-text-2);
    width: 90px;
    margin-right: 10px;
    flex-shrink: 0;
    white-space: nowrap;
}

.label-text {
  white-space: nowrap;
}

.icon-id,
.icon-name,
.icon-creator,
.icon-module,
.icon-updater,
.icon-type,
.icon-status {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-id {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4-4h2v14h-2z'/%3E%3C/svg%3E");
}

.icon-name {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
}

.icon-creator {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
}

.icon-updater {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E");
}

/* 查询区渐变图标 */
.label-with-icon .icon-id,
.label-with-icon .icon-name,
.label-with-icon .icon-creator,
.label-with-icon .icon-updater,
.label-with-icon .icon-type,
.label-with-icon .icon-status {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
}

.label-with-icon .icon-id { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.label-with-icon .icon-name { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.label-with-icon .icon-creator { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.label-with-icon .icon-updater { background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); }
.label-with-icon .icon-type { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); }
.label-with-icon .icon-status { background: linear-gradient(135deg, #10b981 0%, #047857 100%); }

.icon-module {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z'/%3E%3C/svg%3E");
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

.id-cell {
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

.type-tag {
  font-weight: 500;
}

/* 创建信息单元格 */
.create-info-cell,
.update-info-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
  justify-content: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--qm-text-2);
  font-size: 14px;
}

.icon-user {
  width: 14px;
  height: 14px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.user-name {
  font-weight: 500;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.time-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--qm-text-2);
  font-size: 12px;
}

.time {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.action-btn.edit-btn:hover {
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.action-btn.delete-btn:hover {
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.action-btn.choose-btn:hover {
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
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

.action-btn.choose-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
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
  float: right;
  min-height: 40px;
  background: var(--qm-bg-2);
  z-index: 10;
  position: relative;
  opacity: 1 !important;
  visibility: visible !important;
}


/* 对话框样式 */


/* 使用深度选择器来覆盖element-plus样式 */

.elegant-dialog >>> .el-dialog__header {
  padding: 24px 24px 0;
  margin: 0;
}

.elegant-dialog >>> .el-dialog__title {
  font-size: 20px;
  font-weight: 700;
  color: var(--qm-text-1);
  display: flex;
  align-items: center;
  gap: 12px;
}

.elegant-dialog >>> .el-dialog__title::before {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 2px;
}

.elegant-dialog >>> .el-dialog__body {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

 .elegant-dialog.el-dialog {
   border-radius: 12px !important;
 }

.dialog-form {
  margin: 0;
}

.dialog-form-item {
  margin-bottom: 20px;
}

.dialog-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--qm-text-2);
}

.ai-alert {
  margin-bottom: 16px;
}

.ai-required {
  color: #ef4444;
  margin-left: 2px;
  font-weight: 600;
}

.ai-login-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0 4px;
}

.ai-login-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--qm-text-2);
  flex-shrink: 0;
}

.ai-login-tip {
  color: var(--qm-text-3);
  font-size: 12px;
  line-height: 1.4;
}

.ai-tip {
  color: var(--qm-text-3);
  font-size: 12px;
  font-weight: 400;
  margin-left: 4px;
}

.ai-pagepath-tip {
  color: var(--qm-text-3);
  font-size: 12px;
  line-height: 1.4;
  margin-top: 4px;
}

.ai-threshold-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 4px 0;
  width: 100%;
}

.ai-threshold-slider {
  flex: 1;
}

.ai-threshold-value {
  flex-shrink: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--qm-text-2);
  min-width: 40px;
  text-align: right;
}

/* 对话框图标样式 */
.icon-name-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-page-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-type-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-web-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM4 12c0-4.42 3.58-8 8-8 1.85 0 3.55.63 4.9 1.69L5.69 16.9C4.63 15.55 4 13.85 4 12zm8 8c-1.85 0-3.55-.63-4.9-1.69L18.31 7.1C19.37 8.45 20 10.15 20 12c0 4.42-3.58 8-8 8z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-android-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M17.6 9.48l1.84-3.18c.16-.31.04-.69-.26-.85-.29-.15-.65-.06-.83.22l-1.88 3.24c-2.86-1.21-6.08-1.21-8.94 0L5.65 5.67c-.19-.28-.55-.37-.84-.22-.3.16-.42.54-.26.85L6.4 9.48C3.3 11.25 1.28 14.44 1 18h22c-.28-3.56-2.3-6.75-5.4-8.52zM7 15.25c-.69 0-1.25-.56-1.25-1.25s.56-1.25 1.25-1.25 1.25.56 1.25 1.25-.56 1.25-1.25 1.25zm10 0c-.69 0-1.25-.56-1.25-1.25s.56-1.25 1.25-1.25 1.25.56 1.25 1.25-.56 1.25-1.25 1.25z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-ios-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.17 3.51 7.08 9.08 6.74c1.79.04 3.07 1.2 4.08 1.2 1.01 0 2.62-1.48 4.52-1.26 2.49.38 4.28 2.41 4.28 2.41-3.64 2.07-3.1 6.16.89 8.19-.03.05-.05.1-.08.15-1.01 1.5-1.58 2.23-2.72 3.59zM12.03 6.54c-.14-1.4.4-2.79 1.52-3.77 1.12-1 2.63-1.55 4-1.33.15 1.1-.34 2.22-1.28 3.1-1.08 1-2.39 1.53-3.71 1.36-.09-.04-.18-.08-.27-.13-.03-.01-.06-.02-.1-.03-.05-.02-.1-.03-.15-.04-.02 0-.04-.01-.06-.01-.09-.02-.18-.04-.27-.06-.1-.02-.19-.04-.29-.06-.01 0-.01 0-.02-.01-.05-.01-.1-.02-.15-.03z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.loc-component {
  width: 100%;
}

.loc-form {
  width: 100%;
}
.loc-by,
.loc-value,
.loc-opts-name {
  width: 100% !important;
}
.loc-form >>> .el-form-item {
  width: 100%;
}
.loc-exact-item >>> .el-form-item__content,
.loc-visible-item >>> .el-form-item__content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: normal;
}
.loc-exact-item .loc-exact-switch {
  margin-top: 2px;
}
.loc-visible-item .loc-opts-name {
  height: 40px;
}

.elegant-dialog >>> .el-dialog__footer {
  padding: 16px 24px 24px;
  border-top: 1px solid var(--qm-bg-3);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .case-management-container {
    padding: 16px;
    flex-direction: column;
  }
  
  .sidebar-card {
    width: 100%;
    margin-bottom: 20px;
  }
  
  .sidebar-content {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .search-wrapper {
    width: 100%;
  }
  
  .tree-wrapper {
    flex: 1;
    min-height: 300px;
  }
  
  .tree-actions {
    width: 100%;
    margin-top: 20px;
  }
}

@media screen and (max-width: 768px) {
  .case-management-container {
    padding: 12px;
  }
  
  .filter-header {
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
  
  .elegant-dialog >>> .el-dialog {
    width: 90% !important;
    max-width: 500px;
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

.sidebar-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.filter-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
}

.content-card {
  animation: slideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both;
}
</style>

<style>
html body .el-radio-group.include-children-radio .el-radio-button.is-active .el-radio-button__inner {
  background: #10b981 !important;
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

/* ===== 批量操作按钮（参考 FunCaseList） ===== */
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

.batch-dropdown-popper.el-popper {
  padding: 12px !important;
  border-radius: 12px !important;
  border: none !important;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12) !important;
  background: var(--qm-bg-2) !important;
  width: auto !important;
  min-width: 100px !important;
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

.batch-dropdown-popper .el-dropdown-menu__item:hover {
  background: transparent !important;
}

.batch-dropdown-popper .el-dropdown-menu__item:last-child {
  padding-bottom: 0 !important;
  margin-bottom: 0 !important;
  border-bottom: none !important;
}

.batch-dropdown-item {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
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

.batch-dropdown-item .item-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--qm-text-2);
  transition: all 0.2s ease;
}

.batch-dropdown-item:hover .item-text {
  color: #f59e0b;
}

/* ===== 状态徽章与行内编辑下拉（参考 FunCaseList） ===== */
.status-dropdown {
  display: inline-flex;
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

.element-status-0 {
  background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%);
}
.element-status-1 {
  background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
}
.element-status-2 {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

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

.status-dropdown-popper .status-indicator.info { background: var(--qm-text-3); }
.status-dropdown-popper .status-indicator.success { background: #10b981; }
.status-dropdown-popper .status-indicator.warning { background: #f59e0b; }

.status-dropdown-popper .status-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--qm-text-2);
}

</style>