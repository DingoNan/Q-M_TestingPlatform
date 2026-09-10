<template>
  <!-- 模块编辑对话框 -->
  <el-dialog v-model="editModuleVisible" :title="moduleTitle" width='450' class="elegant-dialog">
    <div class="dialog-content">
      <el-form :model="moduleSave" label-position='top' :rules="moduleRules" ref='moduleRef' class="dialog-form" :disabled="moduleView">
        <el-form-item prop='name' class="dialog-form-item">
          <label class="dialog-label">
            <i class="icon-module"></i>
            模块名称
          </label>
          <el-input v-model="moduleSave.name" autocomplete="off" placeholder="请输入模块名称" class="input" size='large' maxlength="20" show-word-limit/>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <span class="dialog-footer" v-if='!moduleView'>
        <el-button @click="editModuleVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button type="primary" @click="save()" class="dialog-confirm-btn">保存</el-button>
      </span>
    </template>
  </el-dialog>

  <!-- 用例编辑对话框 -->
  <el-dialog v-model="editCaseVisible" :title="title" width="450" :close-on-click-modal='false' class="elegant-dialog">
    <div class="dialog-content">
      <el-form :model="caseForm" label-position='top' :disabled='caseView' :rules="caseRules" ref='caseRef' class="dialog-form">
        <el-form-item label="用例名称" prop="name" class="dialog-form-item">
          <label class="dialog-label">
            <i class="icon-case"></i>
            用例名称
          </label>
          <el-input v-model="caseForm.name" autocomplete="off" placeholder="请输入用例名称" class="input" size='large'/>
        </el-form-item>
        
        <el-form-item label="所属模块" prop='module' class="dialog-form-item">
          <label class="dialog-label">
            <i class="icon-folder"></i>
            所属模块
          </label>
          <el-cascader 
            placeholder='请选择或输入模块名称' 
            collapse-tags 
            v-model="caseForm.module" 
            :options="plant_module_list" 
            :props="moduleEditProps" 
            clearable
            filterable
            class="dialog-cascader"
          />
        </el-form-item>
        
        <el-form-item label="用例标签" prop="tag" class="dialog-form-item">
          <label class="dialog-label">
            <i class="icon-tag-dialog"></i>
            用例标签
          </label>
          <el-select v-model="caseForm.tag" placeholder="请选择用例标签" clearable multiple class="select"
            size='large'
            popper-class='select-dropdown-rounded'>
            <el-option v-for="tag in tag_list" :label='tag.name' :value="tag.id" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>
    
    <template #footer>
      <span class="dialog-footer" v-if='!caseView'>
        <el-button @click="editCaseVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button type="primary" v-if='title === "新增用例"' @click="createCase" class="dialog-confirm-btn">确认</el-button>
        <el-button type="primary" v-if='title === "编辑用例"' @click="updateCase" class="dialog-confirm-btn">确认</el-button>
      </span>
    </template>
  </el-dialog>

  <!-- 主容器 -->
  <div class="api-management-container">
    <div class="tab-content-wrapper">
      <el-container class="tab-container">
        <!-- 左侧树形结构 -->
        <el-aside width="320px" class="tree-aside">
          <el-card class="tree-card elegant-shadow">
            <div class="tree-card-content">
              <div class="tree-header">
                <div class="tree-title-wrapper">
                  <h3 class="tree-title">服务模块树</h3>
                </div>
                <el-radio-group v-model="includeChildren" @change="onIncludeChildrenChange" size="small" class="include-children-radio">
                  <el-radio-button :label="true">含子节点</el-radio-button>
                  <el-radio-button :label="false">仅当前</el-radio-button>
                </el-radio-group>
              </div>
              <el-input 
                v-model="filterServiceText" 
                placeholder="请输入模块名称" 
                class="input" size='large'
                clearable
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-divider style='margin-bottom: 10px; margin-top: 10px'></el-divider>
              <div class="tree-wrapper">
                <el-tree 
                  ref="treeRef"
                  highlight-current
                  node-key='id'
                  :expand-on-click-node='false'
                  :indent='10'
                  @node-click='moduleServiceSelect'
                  :current-node-key='selectServiceNode'
                  :filter-node-method="filterServiceNode"
                  :data='serviceModuleTree' 
                  :props="{label: 'name'}" 
                  class="custom-tree"
                > 
				  <template #empty>
					  <div class="empty-tree">
						<el-empty description="暂无服务数据" :image-size="100">
						  <template #description>
							<div style="margin-bottom: 10px;">暂无接口服务数据</div>
								<el-button
							  type="primary"
							  @click="goToCreateService"
							  class="add-btn"
							>
							  <el-icon><Plus /></el-icon>去新建服务
							</el-button>
						  </template>
						</el-empty>
					  </div>
				  </template>
                  <template #default="{ node, data }">
                    <div class="custom-tree-node">
                      <div class="node-content">
                        <i :class="getNodeIcon(data)" class="node-icon"></i>
                        <el-tooltip 
                          :content="node.label" 
                          placement="bottom" 
                          effect="dark"
                          :show-after="500"
                        >
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
                                <el-icon><Plus /></el-icon>新增模块
                              </el-dropdown-item>
                              <el-dropdown-item v-if='permission.has_edit_permission && node.data.id > 0' divided :command="{ action: 'edit', node: node }">
                                <el-icon><EditPen /></el-icon>编辑模块
                              </el-dropdown-item>
                              <el-dropdown-item v-if='permission.has_delete_permission && node.data.id > 0' divided :command="{ action: 'delete', node: node }" class="danger-item">
                                <el-icon><Delete /></el-icon>删除模块
                              </el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                    </div>
                  </template>
                </el-tree>
              </div>
            </div>
            <el-divider style='margin: 0px'></el-divider>
            <div class="tree-footer">
              <div class="tree-actions">
                <el-button 
                  @click="expandServiceAllNodes" 
                  plain
                  class="tree-action-btn"
                >
                  <el-icon><Expand /></el-icon>全部展开
                </el-button>
                <el-button 
                  @click="collapseServiceAllNodes" 
                  plain
                  class="tree-action-btn"
                >
                  <el-icon><Fold /></el-icon>全部折叠
                </el-button>
              </div>
            </div>
          </el-card>
        </el-aside>
        
        <!-- 右侧内容区域 -->
        <el-main class="content-main">
          
          <!-- 搜索筛选区域 -->
          <el-card class="filter-card elegant-shadow">
            <div class="filter-header">
              <div class="header-title-section">
                <i class="icon-search"></i>
                <h3 class="filter-title">接口筛选</h3>
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
              <el-form :model="apiSearch" class="filter-form inline-form">
                <el-row :gutter="24">
                  <!-- 第一行 -->
                  <el-col :xs="24" :sm="12" :md="8" :lg="6">
                    <el-form-item class="inline-form-item">
                      <div class="inline-label-wrapper">
                        <i class="icon-name"></i>
                        <span class="inline-label-text">接口名称</span>
                      </div>
                      <el-input 
                        v-model="apiSearch.name" 
                        placeholder="请输入接口名称" 
                        clearable
                        class="input" size='large'
                      />
                    </el-form-item>
                  </el-col>
                  
                  <el-col :xs="24" :sm="12" :md="8" :lg="6">
                    <el-form-item class="inline-form-item">
                      <div class="inline-label-wrapper">
                        <i class="icon-url"></i>
                        <span class="inline-label-text">接口地址</span>
                      </div>
                      <el-input 
                        v-model="apiSearch.url" 
                        placeholder="请输入接口地址" 
                        clearable
                       class="input" size='large'
                      />
                    </el-form-item>
                  </el-col>
                  
                  <!-- 第二行 -->
                  <el-col :xs="24" :sm="12" :md="8" :lg="6">
                    <el-form-item class="inline-form-item">
                      <div class="inline-label-wrapper">
                        <i class="icon-method"></i>
                        <span class="inline-label-text">请求方法</span>
                      </div>
                      <el-select 
                        v-model="apiSearch.method" 
                        placeholder="请选择请求方法" 
                        clearable
                        class="select"
                        size='large'
                        popper-class='select-dropdown-rounded'
                        
                      >
                        <el-option 
                          v-for="http_method in methods" 
                          :key="http_method"
                          :label="http_method" 
                          :value="http_method" 
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :xs="24" :sm="12" :md="8" :lg="6">
                    <el-form-item class="inline-form-item">
                      <div class="inline-label-wrapper">
                        <i class="icon-case"></i>
                        <span class="inline-label-text">关联用例</span>
                      </div>
                      <el-select 
                        v-model="apiSearch.is_autoed" 
                        placeholder="请选择" 
                        clearable
                       class="select"
                       size='large'
                       popper-class='select-dropdown-rounded'
                       
                        
                      >
                        <el-option label="是" :value="true" />
                        <el-option label="否" :value="false" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :xs="24" :sm="12" :md="8" :lg="6">
                    <el-form-item class="inline-form-item">
                      <div class="inline-label-wrapper">
                        <i class="icon-status"></i>
                        <span class="inline-label-text">接口状态</span>
                      </div>
                      <el-select 
                        v-model="apiSearch.status" 
                        placeholder="请选择接口状态" 
                        clearable
                        filterable
                        class="select"
                        size='large'
                        popper-class='select-dropdown-rounded'
                        
                      >
                        <el-option 
                          v-for="(value, label) in api_status" 
                          :key="value"
                          :label="label" 
                          :value="value" 
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :xs="24" :sm="12" :md="8" :lg="6">
                    <el-form-item class="inline-form-item">
                      <div class="inline-label-wrapper">
                        <i class="icon-creator"></i>
                        <span class="inline-label-text">创建人</span>
                      </div>
                      <el-select 
                        v-model="apiSearch.create_by" 
                        placeholder="请选择创建人" 
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
                  
                  <!-- 第三行 -->
                  <el-col :xs="24" :sm="12" :md="8" :lg="6">
                    <el-form-item class="inline-form-item">
                      <div class="inline-label-wrapper">
                        <i class="icon-updater"></i>
                        <span class="inline-label-text">更新人</span>
                      </div>
                      <el-select 
                        v-model="apiSearch.update_by" 
                        placeholder="请选择更新人" 
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
                  <h3 class="content-title">接口列表</h3>
                  <div class="stats-info">
                    <div class="stat-item">
                      <span class="stat-label">总计</span>
                      <span class="stat-value">{{ api_list.count || 0 }}</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">当前页</span>
                      <span class="stat-value">{{ page_size_params.page }}</span>
                    </div>
                  </div>
                </div>
                <div class="content-actions">
                  <el-button 
                    v-if='permission.has_add_permission' 
                    @click="addApi" 
                    type='primary'
                    class="add-btn"
                  >
                    <el-icon><Plus /></el-icon>新增
                  </el-button>
                  <el-button
                    v-if='permission.has_add_permission'
                    @click="openImportDialog"
                    type='primary'
                    class="import-btn"
                  >
                    <el-icon><UploadFilled /></el-icon>导入
                  </el-button>
                </div>
              </div>
            </div>
          
            <!-- 数据表格 -->
            <div class="table-wrapper">
              <el-table 
                :data="api_list.results" 
                :max-height="'calc(100vh - 530px)'" 
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
                 :show-overflow-tooltip="true">
                  <template #default="scope">
                    <div class="index-cell">
                      {{ scope.$index + 1 + (page_size_params.page - 1) * page_size_params.size }}
                    </div>
                  </template>
                </el-table-column>
                
                <el-table-column 
                  label="接口名称" 
                  prop="name" 
                  min-width="200" 
                  align="center"
                  class-name="name-column"
                />
                
                <el-table-column 
                  label="接口状态" 
                  prop="status_name" 
                  width="110" 
                  align="center"
                  class-name="status-column"
                >
                  <template #default="scope">
                    <el-tag 
                      v-if='scope.row.status ===1' 
                      color='#67C23A' 
                      effect='dark'
                      class="status-tag"
                    >
                      {{ scope.row.status_name }}
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.status ===2' 
                      color="#f59e0b" 
                      effect='dark'
                      class="status-tag"
                    >
                      {{ scope.row.status_name }}
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.status ===3' 
                      color="#909399" 
                      effect='dark'
                      class="status-tag"
                    >
                      {{ scope.row.status_name }}
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.status ===4' 
                      color="#f59e0b" 
                      effect='dark'
                      class="status-tag"
                    >
                      {{ scope.row.status_name }}
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.status ===5' 
                      color="#f59e0b" 
                      effect='dark'
                      class="status-tag"
                    >
                      {{ scope.row.status_name }}
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.status ===6' 
                      color="#E6A23C" 
                      effect='dark'
                      class="status-tag"
                    >
                      {{ scope.row.status_name }}
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.status ===7' 
                      color="#67C23A" 
                      effect='dark'
                      class="status-tag"
                    >
                      {{ scope.row.status_name }}
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.status ===8' 
                      color="#F93E3E" 
                      effect='dark'
                      class="status-tag"
                    >
                      {{ scope.row.status_name }}
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.status ===9' 
                      color="#E6A23C" 
                      effect='dark'
                      class="status-tag"
                    >
                      {{ scope.row.status_name }}
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.status ===10' 
                      color="#909399" 
                      effect='dark'
                      class="status-tag"
                    >
                      {{ scope.row.status_name }}
                    </el-tag>
                  </template>
                </el-table-column>
                
                <el-table-column 
                  label="请求方法" 
                  prop="method" 
                  width="130" 
                  align="center"
                  class-name="method-column"
                >
                  <template #default="scope">
                    <el-tag 
                      v-if='scope.row.method ==="GET"' 
                      color='#f59e0b' 
                      effect='dark'
                      class="method-tag"
                    >
                      GET
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.method ==="POST"' 
                      color="#49CC90" 
                      effect='dark'
                      class="method-tag"
                    >
                      POST
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.method ==="DELETE"' 
                      color="#F93E3E" 
                      effect='dark'
                      class="method-tag"
                    >
                      DELETE
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.method ==="PUT"' 
                      color="#FCA130" 
                      effect='dark'
                      class="method-tag"
                    >
                      PUT
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.method ==="PATCH"' 
                      color="#50E3C2" 
                      effect='dark'
                      class="method-tag"
                    >
                      PATCH
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.method ==="HEAD"' 
                      color="#9012FE" 
                      effect='dark'
                      class="method-tag"
                    >
                      HEAD
                    </el-tag>
                    <el-tag 
                      v-if='scope.row.method ==="OPTIONS"' 
                      color="#2B6CB0" 
                      effect='dark'
                      class="method-tag"
                    >
                      OPTIONS
                    </el-tag>
                  </template>
                </el-table-column>
                
                <el-table-column 
                  label="接口地址" 
                  prop="url" 
                  min-width="200" 
                  align="center"
                  class-name="url-column"
                >
                  <template #default="scope">
                    <div class="url-cell">
                      <!-- 复制按钮在上 -->
                      <div class="copy-action-row">
                        <el-link 
                          type="primary" 
                          @click="copyUrl(scope.row.url)" 
                          class="copy-link"
                          :underline="false"
                        >
                          <el-icon class="copy-icon">
                            <CopyDocument />
                          </el-icon>
                        </el-link>
                      </div>
                      <!-- URL地址在下 -->
                      <div class="url-text-row">
                        <span class="url-text">{{ scope.row.url }}</span>
                      </div>
                    </div>
                  </template>
                </el-table-column>
                
                <el-table-column
                  label="关联用例个数"
                  prop="case_num"
                  width="120"
                  align="center"
                  class-name="case-count-column"
                >
                  <template #default="scope">
                    <div class="case-count-cell">
                      <el-tooltip
                        placement="bottom"
                        effect="light"
                        :disabled="!scope.row.case_info || scope.row.case_info.length === 0"
                      >
                        <template #content>
                          <div class="case-tooltip-content">
                            <div
                              v-for="(case_obj, index) in scope.row.case_info"
                              :key="case_obj.id"
                              class="case-item"
                            >
                              <el-link
                                type="primary"
                                @click="jumpCase(case_obj.id)"
                                class="case-link"
                              >
                                {{ index + 1 }}. &nbsp; {{ case_obj.name }}
                              </el-link>
                            </div>
                          </div>
                        </template>
                        <div class="case-count">
                          <span class="case-count-number">{{ scope.row.case_num || 0 }}</span>
                        </div>
                      </el-tooltip>
                    </div>
                  </template>
                </el-table-column>
                
                <!-- 创建信息列 -->
                <el-table-column 
                  label="创建信息" 
                  width="180" 
                  align="center"
				  sortable="custom"
				  prop='create_time'
                  class-name="create-info-column"
                >
                  <template #default="scope">
                    <div class="info-cell">
                      <div class="info-user">
                        <i class="icon-user"></i>
                        <span class="user-name">{{ scope.row.create_by_name || '-' }}</span>
                      </div>
                      <div class="info-time">
                        <i class="icon-time-small"></i>
                        <span class="time-text">{{ formatTime(scope.row.create_time) }}</span>
                      </div>
                    </div>
                  </template>
                </el-table-column>
                
                <!-- 更新信息列 -->
                <el-table-column 
                  label="更新信息" 
                  width="180" 
                  align="center"
				  sortable="custom"
				   prop='update_time'
                  class-name="update-info-column"
                >
                  <template #default="scope">
                    <div class="info-cell">
                      <div class="info-user">
                        <i class="icon-user"></i>
                        <span class="user-name">{{ scope.row.update_by_name || '-' }}</span>
                      </div>
                      <div class="info-time">
                        <i class="icon-time-small"></i>
                        <span class="time-text">{{ formatTime(scope.row.update_time) }}</span>
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
                        content="查看接口文档" 
                        placement="top" 
                        effect="dark"
                        v-if="permission.has_read_permission"
                      >
                        <el-button 
                          type="success" 
                          class="action-btn view-btn"
                          @click.stop="ViewApi(scope.row)"
                          circle
                        >
                          <el-icon><View /></el-icon>
                        </el-button>
                      </el-tooltip>
                      
                      <el-tooltip 
                        content="编辑接口文档" 
                        placement="top" 
                        effect="dark"
                        v-if="permission.has_edit_permission"
                      >
                        <el-button 
                          type="warning" 
                          class="action-btn edit-btn"
                          @click.stop="editApi(scope.row)"
                          circle
                        >
                          <el-icon><EditPen /></el-icon>
                        </el-button>
                      </el-tooltip>
                      
                      <el-tooltip 
                        content="删除接口文档" 
                        placement="top" 
                        effect="dark"
                        v-if="permission.has_delete_permission"
                      >
                        <el-button 
                          type="danger" 
                          @click.stop="deleteApi(scope.row.id)" 
                          class="action-btn delete-btn"
                          circle
                        >
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </el-tooltip>
                      
                      <el-tooltip 
                        content="选择接口" 
                        placement="top" 
                        effect="dark"
                        v-if="isCanChoose"
                      >
                        <el-button 
                          type="primary" 
                          class="action-btn choose-btn"
                          @click.stop="chooseApiId(scope.row)"
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
                v-model:current-page="page_size_params.page"
                v-model:page-size="page_size_params.size"
                :page-sizes="[10, 20, 30, 50]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="api_list.count"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
                class="select input"
                :background="true"
                
              />
            </div>
          </el-card>
        
        </el-main>
      </el-container>
    </div>

    <!-- 导入接口对话框（Apifox 风格 / V2） -->
    <el-dialog v-model="apiImportVisible" title="导入接口" width="900" draggable
               :close-on-click-modal="false" class="import-dialog elegant-dialog">
      <el-steps :active="importStep" finish-status="success" align-center class="import-steps">
        <el-step title="选择格式" />
        <el-step title="数据来源" />
        <el-step title="配置选项" />
        <el-step title="导入结果" />
      </el-steps>

      <!-- Step 0：选择格式 -->
      <div v-show="importStep === 0" class="step-content">
        <div class="format-grid">
          <div v-for="opt in importFormats" :key="opt.value"
               class="format-card"
               :class="{ active: apiImportSet.format === opt.value }"
               @click="apiImportSet.format = opt.value">
            <img :src="opt.iconSvg" class="format-icon" alt="" />
            <div class="format-info">
              <div class="format-name">{{ opt.label }}</div>
              <div class="format-desc">{{ opt.desc }}</div>
            </div>
            <el-icon v-if="apiImportSet.format === opt.value" class="format-check"><CircleCheck /></el-icon>
          </div>
        </div>
      </div>

      <!-- Step 1：数据来源 -->
      <div v-show="importStep === 1" class="step-content">
        <!-- cURL 格式：直接粘贴命令 -->
        <div v-if="apiImportSet.format === 'curl'">
          <el-input v-model="apiImportSet.curlText" type="textarea" :autosize="{ minRows: 8, maxRows: 14 }"
                      placeholder="请粘贴 cURL 命令，例如：&#10;curl -X POST https://api.example.com/users&#10;  -H 'Content-Type: application/json'&#10;  -d '{&quot;name&quot;: &quot;test&quot;}'"
                      class="text"/>
          <div class="source-tip">支持从浏览器开发者工具复制的 cURL 命令（-H/-d/-F/-X/-G 等常用参数），可一次粘贴多条</div>
        </div>
        <!-- 其他格式：文件 / URL -->
        <el-tabs v-else v-model="apiImportSet.source" class="source-tabs">
          <el-tab-pane label="文件导入" name="file">
            <el-upload drag :auto-upload="false" :on-change="onImportFileChange" :on-remove="onImportFileRemove"
                       :file-list="importFileList" :limit="1" accept=".json,.yaml,.yml,.jmx,.xml"
                       class="import-uploader">
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
              <template #tip>
                <div class="el-upload__tip">支持 .json / .yaml / .yml / .jmx / .xml 文件，仅支持单个文件</div>
              </template>
            </el-upload>
          </el-tab-pane>
          <el-tab-pane label="URL 导入" name="url">
            <el-input v-model="apiImportSet.url" placeholder="请输入 OpenAPI / Swagger / Postman 数据文件的直链 URL"
                      size="large" clearable class="input">
              <template #prefix><el-icon><Link /></el-icon></template>
            </el-input>
            <div class="source-tip">注意：URL 应指向 json/yaml 数据文件，而非文档展示页面地址</div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- Step 2：配置选项 -->
      <div v-show="importStep === 2" class="step-content">
        <el-form :model="apiImportSet" label-position="top" :rules="importRules" ref="importRef">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="所属服务" prop="service">
                <el-select v-model="apiImportSet.service" placeholder="请选择目标服务" clearable size="large"
                           popper-class="select-dropdown-rounded" class="select full-width">
                  <el-option v-for="service_obj in service_list.results" :key="service_obj.id"
                             :label="service_obj.name" :value="service_obj.id" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="目标模块（可选）">
                <el-tree-select v-model="apiImportSet.module" :data="importModuleTree" :props="importTreeProps"
                                clearable check-strictly :render-after-expand="false" node-key="id"
                                placeholder="不选则按 tag 自动创建" size="large" class="select full-width"
                                popper-class="select-tree-dropdown-rounded"/>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="URI 前缀">
            <el-input v-model="apiImportSet.uriPrefix" placeholder="如 /api/v1，留空则使用文档原路径" size="large"
                      class="input"/>
          </el-form-item>
          <el-form-item label="重复接口处理">
            <el-radio-group v-model="apiImportSet.matchMode" class="match-mode-group">
              <el-radio-button label="overwrite">覆盖所有字段</el-radio-button>
              <el-radio-button label="skip">不导入</el-radio-button>
              <el-radio-button label="keep_both">保留两者</el-radio-button>
            </el-radio-group>
            <div class="form-tip">当 “服务 + 请求方法 + URL” 相同时触发：覆盖原接口 / 跳过 / 保留为新接口</div>
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 3：导入结果 -->
      <div v-show="importStep === 3" class="step-content">
        <div class="result-summary">
          <div class="result-icon" :class="importStats.failed > 0 ? 'partial' : 'success'">
            <el-icon><Warning v-if="importStats.failed > 0"/><CircleCheck v-else/></el-icon>
          </div>
          <div class="result-text">
            <div class="result-title">导入{{ importStats.failed > 0 ? '完成（部分失败）' : '成功' }}</div>
            <div class="result-sub">共处理 {{ importStats.total }} 个接口</div>
          </div>
        </div>
        <div class="stats-grid">
          <div class="stat-cell success"><div class="num">{{ importStats.success }}</div><div class="lbl">新增</div></div>
          <div class="stat-cell updated"><div class="num">{{ importStats.updated }}</div><div class="lbl">更新</div></div>
          <div class="stat-cell skipped"><div class="num">{{ importStats.skipped }}</div><div class="lbl">跳过</div></div>
          <div class="stat-cell failed"><div class="num">{{ importStats.failed }}</div><div class="lbl">失败</div></div>
        </div>
        <div v-if="importStats.errors && importStats.errors.length" class="error-list">
          <div class="error-title">失败详情：</div>
          <div v-for="(err, i) in importStats.errors.slice(0, 20)" :key="i" class="error-item">{{ err }}</div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="apiImportVisible = false" class="dialog-cancel-btn">关闭</el-button>
          <el-button v-if="importStep > 0 && importStep < 3" @click="prevImportStep" class="dialog-cancel-btn">上一步</el-button>
          <el-button v-if="importStep < 2" type="primary" @click="nextImportStep" class="dialog-confirm-btn"
                     :disabled="!canNextImportStep">下一步</el-button>
          <el-button v-if="importStep === 2" type="primary" @click="submitImportV2" class="dialog-confirm-btn"
                     :loading="importLoading">开始导入</el-button>
          <el-button v-if="importStep === 3" type="primary" @click="resetImportDialog" class="dialog-confirm-btn">再次导入</el-button>
        </div>
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
import {mapState, mapActions, mapGetters} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  View,
  Delete,
  Edit,
  Plus,
  EditPen,
  UploadFilled,
  Pointer,
  Position,
  CopyDocument,
  Refresh,
  Search,
  Setting,
  Expand,
  Fold,
  CircleCheck,
  Warning,
  Link
} from '@element-plus/icons-vue'
import Params from './Params.vue'
import MockParams from './MockParams.vue'
import Header from './Header.vue'
import MockHeader from './MockHeader.vue'
import Json from './Json.vue'
import MockJson from './MockJson.vue'
import Response from './Response.vue'
import MockResponse from './MockResponse.vue'
import MockData from './MockData.vue'
import Data from './Data.vue'
import BodyEdit from './BodyEdit.vue'

export default{
  name: 'ApiManagement',
  computed:{
    ...mapState(['pathPermission', 'projectInfo', 'userInfo']),
    chooseApiVisible: {
      get(){
        return this.chooseApiVisible
      },
      set(value){
        this.$emit('update:chooseApiVisible', value)
      }
    },
    editOption(){
      return {
        enablesBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true,
        tabSize: 4,
        fontSize: 18,
        useworker: true,
        ShowPrintMargin: false,
        enableMultiselect: true,
        showFoldwidgets: true,
        fadeFoldwidgets: true,
        wrap:true,
      }
    },
    canNextImportStep(){
      if(this.importStep === 0){
        return !!this.apiImportSet.format
      }
      if(this.importStep === 1){
        // cURL 格式：校验粘贴的命令
        if(this.apiImportSet.format === 'curl'){
          return !!(this.apiImportSet.curlText && this.apiImportSet.curlText.trim())
        }
        if(this.apiImportSet.source === 'file'){
          return !!this.apiImportSet.file
        }
        if(this.apiImportSet.source === 'url'){
          return !!this.apiImportSet.url && /^https?:\/\//i.test(this.apiImportSet.url)
        }
        return true
      }
      return true
    },
    calcMinWidth() {
      let visibleButtons = 0;
      if (this.permission.has_read_permission) visibleButtons += 1;
      if (this.permission.has_edit_permission) visibleButtons += 1;
      if (this.permission.has_delete_permission) visibleButtons += 1;
      if (this.isCanChoose) visibleButtons += 1;
      return Math.max(10, visibleButtons * 60);
    },
    calcMockWidth() {
      let visibleButtons = 0;
      if (this.permission.has_read_permission && !this.isCanChoose) visibleButtons += 1;
      if (this.permission.has_edit_permission && !this.readView) visibleButtons += 1;
      if (this.permission.has_delete_permission && !this.readView) visibleButtons += 1;
      return Math.max(10, visibleButtons * 60);
    }
  },
  emits: ['update:chooseApiVisible', 'setApiData'],
  props: {
    'isCanChoose': {
      type: Boolean,
      default: false,
    },
    'parentPermission': {
      type: Object,
      default: null,
    },
    'apiId':{
      type: Infinity,
    }
  },
  data() {
    return{
      api_status: {
        "已发布": 1,
        "设计中": 2,
        "待确定": 3,
        "开发": 4,
        "对接": 5,
        "测试": 6,
        "完成": 7,
        "异常": 8,
        "维护": 9,
        "废弃": 10,
      },
      env_id: '',
	  treeProps: {
	  	label: 'name',
	  	children: 'children'
	  },
      env_list: '',
	  active_mock_tab: 'mock',
      api_test_result: '',
	  filterServiceText: '',
      mock_api_test_result: '',
	  serviceModuleTree: [],
      func_list: [],
      active_request_collapse: 'request',
      mock_active_request_tab: 'Body',
	  mock_active_response_tab: 'body',
	  mock_test_active_request_tab: 'body',
	  mock_test_active_response_tab: 'response_status',
      json_root_type: ['object', 'array'],
      active_request_tab: 'body',
	  test_active_request_tab: 'body',
    test_active_response_tab: 'ResponseStatus',
      active_api_tab: 'doc',
      readView: false,
      readMockView: false,
      isRunApi: false,
      responseStatusVisible: false,
      CreateApiVisible: false,
      mockTestVisible: false,
      apiTitle: '新增接口文档',
      exportRules: {
        exportType: [{
          required: true,
          message: '请选择导入类型',
          trigger: 'change',
        }],
        service: [{
          required: true,
          message: '请选择所属服务',
          trigger: 'change',
        }],
        value: [{
          required: true,
          message: '导入json数据不能为空',
          trigger: 'blur',
        }],
      },
      apiExportSet:{
        service: '',
        exportType: 'open-api-json',
        uri: '',
        value: '',
        module: ''
      },
      runRules: {
		module: [{
		  required: true,
		  message: '请选择所属服务/模块',
		  trigger: 'change',
		}],
		plant: [{
		  required: true,
		  message: '请选择所属产品',
		  trigger: 'change',
		}],
		host: [{
		  required: true,
		  message: '请求域名不能为空',
		  trigger: 'blur',
		}],
        service: [{
          required: true,
          message: '请选择所属服务',
          trigger: 'change',
        }],
        method: [{
          required: true,
          message: '请选择请求方法',
          trigger: 'change',
        }],
        url: [{
          required: true,
          message: '请求地址不能为空',
          trigger: 'blur',
        }],
      },
      saveRules: {
        name: [{
          required: true,
          message: '接口名称不能为空',
          trigger: 'blur',
        }],
		status: [{
		  required: true,
		  message: '请选择接口状态',
		  trigger: 'blur',
		}],
        module: [{
          required: true,
          message: '请选择所属模块',
          trigger: 'change',
        }],
        service: [{
          required: true,
          message: '请选择所属服务',
          trigger: 'change',
        }],
        method: [{
          required: true,
          message: '请选择请求方法',
          trigger: 'change',
        }],
        url: [{
          required: true,
          message: '请求地址不能为空',
          trigger: 'blur',
        }],
      },
      moduleProps:{
        emitPath: false,
        value: 'id',
        label: 'name',
        checkStrictly: true,
      },
      apiExportVisible: false,
      // 新版导入（V2 - Apifox 风格）
      apiImportVisible: false,
      importStep: 0,
      importLoading: false,
      importFileList: [],
      importModuleTree: [],
      importTreeProps: { value: 'id', label: 'name', children: 'children', disabled: 'disabled' },
      importFormats: [
        {
          value: 'openapi-swagger',
          label: 'OpenAPI / Swagger',
          desc: '自动识别 2.0 / 3.x，支持 JSON & YAML',
          iconSvg: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"%3E%3Crect width="64" height="64" rx="12" fill="%230ea5e9"/%3E%3Cpath fill="white" d="M20 16h24v4H28v8h12v4H28v8h16v4H20V16z"/%3E%3C/svg%3E'
        },
        {
          value: 'postman-v2.1',
          label: 'Postman',
          desc: 'Collection v2.1',
          iconSvg: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"%3E%3Crect width="64" height="64" rx="12" fill="%23ff6c37"/%3E%3Cpath fill="white" d="M22 20c-2 0-3 1.5-3 4s1 4 3 4c1 0 2-.5 2.5-1.2l8.5 4.7c-.5 2-2.5 3.5-5 3.5-1.5 0-3-.5-4-1.3l-3 5.2c1.8 1.2 4 1.8 6.5 1.8 5 0 9-3.5 9-8.5 0-4-3-7.5-7-8.5l-7-3.8c-.3-.2-.5-.4-.5-.7 0-.5.5-.8 1-.8s1 .3 1 .8c0 .3-.2.5-.5.7l-5.5 3z"/%3E%3C/svg%3E'
        },
        {
          value: 'apifox',
          label: 'Apifox',
          desc: '智能接口文档',
          iconSvg: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"%3E%3Crect width="64" height="64" rx="12" fill="%23fb7c42"/%3E%3Cpath fill="white" d="M18 44l6-24h4l3 14 3-14h4l5 24h-5l-2.5-13-2.5 13h-4l-3-13-2.5 13H18z"/%3E%3C/svg%3E'
        },
        {
          value: 'yapi',
          label: 'YApi',
          desc: '接口管理平台',
          iconSvg: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"%3E%3Crect width="64" height="64" rx="12" fill="%232d8cf0"/%3E%3Cpath fill="white" d="M22 20h6l4 10 4-10h6L34 38v6h-6v-6L22 20z"/%3E%3C/svg%3E'
        },
        {
          value: 'apipost',
          label: 'ApiPost',
          desc: '接口调试工具',
          iconSvg: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"%3E%3Crect width="64" height="64" rx="12" fill="%234f46e5"/%3E%3Cpath fill="white" d="M20 20h8c3.3 0 6 2.7 6 6 0 2-1 3.5-2.5 4.5L33 44h-6l-1-11h-2v11h-4V20zm4 4v4h4c1.1 0 2-.9 2-2s-.9-2-2-2h-4z"/%3E%3C/svg%3E'
        },
        {
          value: 'jmeter',
          label: 'JMeter',
          desc: '性能测试脚本',
          iconSvg: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"%3E%3Crect width="64" height="64" rx="12" fill="%233c8e3e"/%3E%3Cpath fill="white" d="M32 14l14 24H18L32 14zm0 8l-8 14h16L32 22zm-2 18h4v10h-4V44z"/%3E%3C/svg%3E'
        },
        {
          value: 'eolink',
          label: 'Eolink',
          desc: '接口管理云平台',
          iconSvg: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"%3E%3Crect width="64" height="64" rx="12" fill="%2312b5cb"/%3E%3Cpath fill="white" d="M18 32c0-7.7 6.3-14 14-14 3.5 0 6.8 1.3 9.3 3.5l-3 3C36.2 22.7 34.2 22 32 22c-5.5 0-10 4.5-10 10s4.5 10 10 10c2.2 0 4.2-.7 5.7-1.5l3 3C37.8 45.7 34.5 47 32 47c-7.7 0-14-6.3-14-14zm7-10v2h10v-2H25zm0 4h7v2h-7v-2zm0 4h10v2H25v-2z"/%3E%3C/svg%3E'
        },
        {
          value: 'curl',
          label: 'cURL',
          desc: '命令行导入',
          iconSvg: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"%3E%3Crect width="64" height="64" rx="12" fill="%231e293b"/%3E%3Cpath fill="%234ade80" d="M18 24h28v4H22v8h22v4H18V24zm22 20l6-4-6-4v3h-6v2h6v3z"/%3E%3C/svg%3E'
        },
      ],
      importStats: { success: 0, skipped: 0, updated: 0, failed: 0, total: 0, errors: [] },
      apiImportSet: {
        format: 'openapi-swagger',
        source: 'file',
        url: '',
        curlText: '',
        file: null,
        service: '',
        module: '',
        uriPrefix: '',
        matchMode: 'overwrite',
      },
      importRules: {
        service: [{ required: true, message: '请选择所属服务', trigger: 'change' }],
      },
      mockVisible: false,
      props: {
        multiple: true,
        emitPath: false,
        value: 'id',
        label: 'name',
      },
      methods: [
        'GET',
        'POST',
        'PUT',
        'DELETE',
        'HEAD',
        'OPTIONS',
        'PATCH'
      ],
      response_status: '',
      tmpApiForm: {},
      apiForm:{
        id: '',
        module: '',
        status: 1,
        name: '',
        url: '',
        method: 'GET',
        service: '',
        host: '',
        headers: [],
        api_json_type: 'object',
        api_response_type: 'object',
        json: [],
        response_tree: [],
        data: [],
        body_type: 1,
        params: [],
        response: [{
          'response_status': 200,
          'response_data': [],
        },]
      },
      testApiForm:{
        id: '',
        module: '',
        name: '',
        url: '',
        method: '',
        service: '',
        plant: '',
        host: '',
        headers: [],
        api_json_type: 'object',
        api_response_type: 'object',
        json: [],
        json_tree: [],
        data: [],
        body_type: 1,
        params: [],
        response: [{
          'response_status': 200,
          'response_data': [],
        },]
      },
      mockTestForm:{
        url: '',
        method: '',
        headers: [],
        api_json_type: 'object',
        body_type: 1,
        json: [],
        json_tree: [],
        data: [],
        params: [],
      },
	  envServiceList: [],
      tmpApiMockForm: {},
      apiMockForm:{
        id: '',
        name: '',
        headers: [],
        api_json_type: 'object',
        status_code: 200,
        timeout: 0,
        body_type: 1,
        response_type: 2,
        body_type_name: '',
        response_type_name: '',
        json: [],
        json_tree: [],
        data: [],
        body: '',
        params: [],
        response:[],
		response_headers: [],
        api_response_type: 'object',
      },
      mockRules: {
        name: [{
          required: true,
          message: 'Mock API 名称不能为空',
          trigger: 'blur',
        }],
        desc: [{
          required: true,
          message: 'Mock API 描述不能为空',
          trigger: 'blur',
        }],
      },
      http_status: [200, 403, 404, 410, 422, 500, 502, 503, 504],
      permission: {},
      apiSearch:{
        name: '',
        service: '',
        status: '',
        method: '',
        url: '',
        project: '',
        module_list: [],
        create_by: [],
        update_by: [],
        is_autoed: '',
      },
      user_list: [],
      plant_list: [],
      page_size_params: {
        page: 1,
        size: 10,
      },
	  sort_params: {
	    ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
	  },
      count: 1,
      title: '新增模块',
      mockTitle: '',
      isAdd: true,
      isMockAdd: true,
      editDialogVisible: false,
      api_list: [],
      api_mock_list: [],
      service_list: [],
      ViewVisible: false,
      plant_module_list: [],
      // 模块编辑相关
      module_node: {},
      moduleRules: {
        name: [{
          required: true,
          message: '模块名称不能为空',
          trigger: 'blur',
        }],
      },
      moduleSave:{
        project: '',
        name: '',
        service: '',
        parent: 0,
      },
      editModuleVisible: false,
      selectNode: 0,
      moduleView: false,
      moduleTitle: '',
      selectServiceNode: 0,
      includeChildren: true,
      role_names: [],
      size: '20px',
      color: '#f59e0b',
      check_methods: [],
      response_tab_active: 0,
      disabled: false,
      show_close: true,
      append_to_body: true
    }
  },
  components: {
    VAceEditor,
    Json,
    MockJson,
    Header,
    MockHeader,
    Response,
    MockResponse,
    Params,
    MockParams,
    BodyEdit,
    MockData,
    Data,
    Refresh,
    Search,
    CopyDocument,
    Setting,
    Expand,
    Fold
  },
  watch: {
    filterServiceText(val) {
      if (this.$refs.treeRef) {
        this.$refs.treeRef.filter(val)
      }
    }
  },
  methods:{
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

     handleClick(tab, event) {
      if (tab.props.name === 'doc' && !this.apiForm.id) {
        this.apiForm = JSON.parse(JSON.stringify(this.testApiForm))
      } else if (tab.props.name === 'test' && !this.apiForm.id) {
        this.testApiForm = JSON.parse(JSON.stringify(this.apiForm))
        this.getRequestHosts()
      }
     },

     handleModuleChange(value) {
      this.getRequestHosts()
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
	
	goToCreateService(){
		this.$router.push({name: 'service'})
	},
    
    // 模块操作相关方法
    controlCommand(command){
      this.module_node = command
      if(command.action === 'add'){
        this.editModuleVisible = true
        this.moduleTitle = '新增模块'
        this.moduleView = false
        this.moduleSave = {
          project: this.projectInfo.id,
          name: '',
          service: '',
          parent: 0,
        }
      }else if(command.action === 'edit'){
        this.moduleSave = {...this.module_node.node.data}
        this.editModuleVisible = true
        this.moduleTitle = '编辑模块'
        this.moduleView = false
      }else if(command.action === 'delete'){
        this.deleteModule(this.module_node.node.data.id)
      }
    },
    
    save(){
      if (this.module_node.action === 'add'){
        this.createModule()
      }else if(this.module_node.action === 'edit'){
        this.updateModule()
      }
    },
    
    async createModule(){
      this.$refs['moduleRef'].validate(async (valid, fields)=>{
        if (valid){
          if (this.module_node.node.data.id < 0){
            // 根节点，创建新的服务
            this.moduleSave.service = -this.module_node.node.data.id
            this.moduleSave.parent = null
          }else{
            // 子模块
            this.moduleSave.service = this.module_node.node.data.service_id
            this.moduleSave.parent = this.module_node.node.data.id
          }
          this.moduleSave.project = this.projectInfo.id
          const response = await this.$api.createServiceModule(this.moduleSave)
          if(response.status === 201){
            this.editModuleVisible = false
            this.getAllServiceModule()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
    },
    
    async updateModule(){
      this.$refs['moduleRef'].validate(async (valid, fields)=>{
        if (valid){
          this.moduleSave.project = this.module_node.node.data.project_id
          this.moduleSave.service = this.module_node.node.data.service_id
          const response = await this.$api.updateServiceModule(this.moduleSave.id, this.moduleSave)
          if(response.status === 200){
            this.editModuleVisible = false
            this.getAllServiceModule()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
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
        const response = await this.$api.deleteServiceModule(id)
        if (response.status === 204){
          this.getAllServiceModule()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }
      }).catch(() => {})
    },
    
	async getAllServiceModule(){
		try {
			const response = await this.$api.getAllServiceModule({project: this.projectInfo.id})
			if (response.status === 200){
				this.serviceModuleTree = response.data.results
			}
		} catch (error) {
			console.error('获取服务模块树失败:', error)
		}
	},
	
	filterServiceNode(value, data) {
	  if (!value) return true
	  return data?.name?.includes(value) || false
	},
	
	expandServiceAllNodes() {
		if (this.$refs.treeRef) {
			const allNodes = this.$refs.treeRef.store._getAllNodes();
			allNodes.forEach(node => {
				node.expanded = true;
			});
		}
	},
	collapseServiceAllNodes() {
		if (this.$refs.treeRef) {
			const allNodes = this.$refs.treeRef.store._getAllNodes();
			allNodes.forEach(node => {
				node.expanded = false;
			});
		}
	},
	
	getNodeIcon(data) {
		// 根据节点类型返回不同的图标
		if (data.id < 0) {
			return 'icon-folder-tree icon-folder-tree-root'
		}
		return 'icon-folder-tree'
	},
    
    copy() {
      if (VxeUI.clipboard.copy(this.$api.base_url + '/api_mock/' + this.apiForm.id + this.apiForm.url)) {
        ElMessage({type: 'success', message: '复制成功'})
      }
    },
    copyUrl(data) {
      if (VxeUI.clipboard.copy(data)) {
        ElMessage({type: 'success', message: '复制成功'})
      }
    },
    jumpCase(case_id){
      this.$router.push({path: '/resource/scriptCaseEdit', query: {id: case_id}})
    },
    ...mapActions(['getRolePermission']),
    handleCurrentChange(page){
      this.page_size_params.page = page
      this.getApis()
    },
    mockTestChange(){
      if(!this.mockTestVisible){
        this.active_api_tab = 'mock_test'
        this.mockTestForm.method = this.apiForm.method
        this.mockTestForm.url = this.$api.base_url + '/api_mock/' + this.apiForm.id + this.apiForm.url
      }else{
        this.active_api_tab = 'mock'
      }
      this.mockTestVisible = !this.mockTestVisible
    },
    async isEnableChange(data){
      const response = await this.$api.updateMock(data.id, data)
      if (response.status === 200){
        this.mockVisible = false
        this.getMocks()
        ElMessage({message: "保存成功", type: 'success'})
      }
    },
    remove_vxe_table_info(){
      this.testApiForm.json_tree = JSON.parse(JSON.stringify(this.testApiForm.json))
      for (let index = this.testApiForm.json.length - 1; index >= 0; index--) {
        if(this.testApiForm.json_tree[index].parentId !== null){
          this.testApiForm.json_tree.splice(index, 1)
        }
      }
      this.delExtraInfo(this.testApiForm.json_tree)
    },
	remove_vxe_table_api_form_response_info(){
	  this.apiForm.response_tree = JSON.parse(JSON.stringify(this.apiForm.response))
	  for(let _index = this.apiForm.response.length - 1; _index >=0; _index --){
		for (let index = this.apiForm.response[_index].response_data.length - 1; index >= 0; index--) {
		  if(this.apiForm.response_tree[_index].response_data[index].parentId !== null){
		    this.apiForm.response_tree[_index].response_data.splice(index, 1)
		  }
		}
		this.delExtraInfo(this.apiForm.response_tree[_index].response_data)
	  }
	},
    remove_vxe_table_mock_test_info(){
      this.mockTestForm.json_tree = JSON.parse(JSON.stringify(this.mockTestForm.json))
      for (let index = this.mockTestForm.json.length - 1; index >= 0; index--) {
        if(this.mockTestForm.json_tree[index].parentId !== null){
          this.mockTestForm.json_tree.splice(index, 1)
        }
      }
      this.delExtraInfo(this.mockTestForm.json_tree)
    },
    remove_vxe_table_mock_info(){
      this.apiMockForm.json_tree = JSON.parse(JSON.stringify(this.apiMockForm.json))
      this.apiMockForm.response_tree = JSON.parse(JSON.stringify(this.apiMockForm.response))
      for (let index = this.apiMockForm.json.length - 1; index >= 0; index--) {
        if(this.apiMockForm.json_tree[index].parentId !== null){
          this.apiMockForm.json_tree.splice(index, 1)
        }
      }
      this.delExtraInfo(this.apiMockForm.json_tree)
      for (let index = this.apiMockForm.response.length - 1; index >= 0; index--) {
        if(this.apiMockForm.response_tree[index].parentId !== null){
          this.apiMockForm.response_tree.splice(index, 1)
        }
      }
      this.delExtraInfo(this.apiMockForm.response_tree)
    },
    delExtraInfo(data){
      for (let index = 0; index < data.length; index++) {
        delete data[index]._X_ROW_CHILD
        delete data[index]._X_ROW_KEY
        if (data[index].hasOwnProperty('children')) {
          this.delExtraInfo(data[index].children);
        }else{
          delete data[index].children
        }
      }
    },
    saveResponse(){
      this.apiForm.response.push({
        'response_status': this.response_status,
        'response_data': [],
      },)
      this.responseStatusVisible = false
    },
    async createApi(is_close){
      if(this.apiForm.module < 0){
        ElMessage({message: "所属模块不能选择根节点", type: 'error'})
        return 
      }
      const response = await this.$api.createApi(this.apiForm)
      if (response.status === 201){
        if(is_close){
           this.CreateApiVisible = false
        }else{
          this.editApi({...response.data.result})
        }
        ElMessage({message: "保存成功", type: 'success'})
      }
    },
    async createMock(){
      this.$refs['mockRef'].validate(async (valid, fields)=>{
        if(valid){
          this.apiMockForm.api =  this.apiForm.id
          const response = await this.$api.createMock(this.apiMockForm)
          if (response.status === 201){
            this.mockVisible = false
            this.getMocks()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
    },
    async updateApi(is_close){
      if(this.apiForm.module < 0){
        ElMessage({message: "所属模块不能选择根节点", type: 'error'})
        return 
      }
      const response = await this.$api.updateApi(this.apiForm.id, this.apiForm)
      if (response.status === 200){
        if(is_close){
           this.CreateApiVisible = false
        }
        this.getApis()
        ElMessage({message: "保存成功", type: 'success'})
      }
    },
    async updateMock(){
      this.$refs['mockRef'].validate(async (valid, fields)=>{
        if(valid){
          const response = await this.$api.updateMock(this.apiMockForm.id, this.apiMockForm)
          if (response.status === 200){
            this.mockVisible = false
            this.getMocks()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
    },
    ensureString(value) {
      // 注意：typeof null === 'object'，所以要排除 null
      if (typeof value === 'object' ) {
        return JSON.stringify(value, null, 4);
      }
      return value;
    },
	
	filterRequiredItems(list) {
	  if (!Array.isArray(list)) return [];
	
	  // 递归处理单个节点，返回新节点或 null（表示应移除）
	  const filterNode = (node) => {
	    if (!node || typeof node !== 'object') return null;
	
	    // 1. 先处理 children
	    let filteredChildren = [];
	    if (Array.isArray(node.children)) {
	      filteredChildren = node.children
	        .map(child => filterNode(child))
	        .filter(child => child !== null);
	    }
	
	    // 2. 判断当前节点是否保留
	    const isRequired = node.is_required !== false; // true 或 undefined 都视为需要保留
	    if (isRequired) {
	      // 自身需要保留：返回新对象（包含过滤后的 children）
	      return { ...node, children: filteredChildren };
	    } else {
	      // 自身 is_required === false：只有当有子节点被保留时才保留自己
	      if (filteredChildren.length > 0) {
	        return { ...node, children: filteredChildren };
	      } else {
	        return null; // 移除
	      }
	    }
	  };
	
	  return list.map(item => filterNode(item)).filter(item => item !== null);
	},

    testApi(){
      this.$refs['runRef'].validate(async (valid, fields)=>{
        if(valid){
          if(!this.testApiForm.host){
			  ElMessage({message: "请输入请求域名", type: 'warning'})
		  }else{
            this.remove_vxe_table_info()
			const tmpApiForm = {
			    ...this.testApiForm,  // 浅拷贝其他字段（如 id, name 等）
			    headers: this.filterRequiredItems(this.testApiForm.headers),
			    params: this.filterRequiredItems(this.testApiForm.params),
			    json_tree: this.filterRequiredItems(this.testApiForm.json_tree),
			    data: this.filterRequiredItems(this.testApiForm.data)
			};
            const response = await this.$api.api_run(tmpApiForm)
            if(response.status === 200){
              this.api_test_result = response.data.result
              this.api_test_result.response_header = this.ensureString(this.api_test_result.response_header)
              this.api_test_result.request_header = this.ensureString(this.api_test_result.request_header)
              this.api_test_result.response_body = this.ensureString(this.api_test_result.response_body)
              this.api_test_result.request_body = this.ensureString(this.api_test_result.request_body)  
              ElMessage({message: "执行完成", type: 'success'})
            }  
          }
        }
      })
    },
    async testMockApi(){
      this.remove_vxe_table_mock_test_info()
      const response = await this.$api.mock_api_run(this.mockTestForm)
	  this.mock_api_test_result = response.data.result
	  if (typeof this.mock_api_test_result === 'object'){
		  this.mock_api_test_result.response_header = this.ensureString(this.mock_api_test_result.response_header)
		  this.mock_api_test_result.response_body = this.ensureString(this.mock_api_test_result.response_body)
		  this.mock_api_test_result.request_body = this.ensureString(this.mock_api_test_result.request_body)
		  this.mock_api_test_result.request_header = this.ensureString(this.mock_api_test_result.request_header)
		  this.mock_api_test_result.request_params = this.ensureString(this.mock_api_test_result.request_params)
		  ElMessage({message: "执行完成", type: 'success'}) 
	  }else{
		  ElMessage({message: this.mock_api_test_result, type: 'warning'}) 
	  }
    },
    async saveApi(is_close){
      this.$refs['saveRef'].validate(async (valid, fields)=>{
        if(valid){
		  this.remove_vxe_table_api_form_response_info()
          for (const index in this.apiForm.json){
            delete this.apiForm.json[index].children
            delete this.apiForm.json[index]._X_ROW_CHILD
            delete this.apiForm.json[index]._X_ROW_KEY
          }
          for (const index in this.apiForm.data){
            delete this.apiForm.data[index].children
            delete this.apiForm.data[index]._X_ROW_CHILD
            delete this.apiForm.data[index]._X_ROW_KEY
          }
          for (const index in this.apiForm.headers){
            delete this.apiForm.headers[index].children
            delete this.apiForm.headers[index]._X_ROW_CHILD
            delete this.apiForm.headers[index]._X_ROW_KEY
          }
          for (const index in this.apiForm.params){
            delete this.apiForm.params[index].children
            delete this.apiForm.params[index]._X_ROW_CHILD
            delete this.apiForm.params[index]._X_ROW_KEY
          }
          for (const key in this.apiForm.response) {
            for (const index in this.apiForm.response[key].response_data){
              delete this.apiForm.response[key].response_data[index].children
              delete this.apiForm.response[key].response_data[index]._X_ROW_CHILD
              delete this.apiForm.response[key].response_data[index]._X_ROW_KEY
            }
          }
          if(this.apiForm.id){
            this.updateApi(is_close)
          }else{
            this.createApi(is_close)
          }
        }
      })
    },
    saveMock(){
      this.remove_vxe_table_mock_info()
      for (const index in this.apiMockForm.json){
        delete this.apiMockForm.json[index].children
        delete this.apiMockForm.json[index]._X_ROW_CHILD
        delete this.apiMockForm.json[index]._X_ROW_KEY
      }
      for (const index in this.apiMockForm.data){
        delete this.apiMockForm.data[index].children
        delete this.apiMockForm.data[index]._X_ROW_CHILD
        delete this.apiMockForm.data[index]._X_ROW_KEY
      }
      for (const index in this.apiMockForm.headers){
        delete this.apiMockForm.headers[index].children
        delete this.apiMockForm.headers[index]._X_ROW_CHILD
        delete this.apiMockForm.headers[index]._X_ROW_KEY
      }
      for (const index in this.apiMockForm.params){
        delete this.apiMockForm.params[index].children
        delete this.apiMockForm.params[index]._X_ROW_CHILD
        delete this.apiMockForm.params[index]._X_ROW_KEY
      }
      for (const key in this.apiMockForm.response) {
        for (const index in this.apiMockForm.response[key].response_data){
          delete this.apiMockForm.response[key].response_data[index].children
          delete this.apiMockForm.response[key].response_data[index]._X_ROW_CHILD
          delete this.apiMockForm.response[key].response_data[index]._X_ROW_KEY
        }
      }
      if(this.apiMockForm.id){
        this.updateMock()
      }else{
        this.createMock()
      }
    },
    handleSizeChange(size){
      this.page_size_params.size = size
      this.page_size_params.page = 1
      this.getApis()
    },
    exportApi(){
      this.import_api()
    },
    search(){
      this.page_size_params.page = 1
      this.getApis()
    },
    reset(){
      for(let key in this.apiSearch){
        if(key === 'module_list'){
          continue
        }else{
          this.apiSearch[key] = ''
        }
      }
    },
    addResponseTab(index, action){
      if (action==='remove'){
        this.apiForm.response.splice(index, 1)
      }else{
        this.responseStatusVisible = true
        
      }
    },
    chooseApiId(apiData){
      // 接口状态守卫：废弃接口不允许被用例引用
      if (Number(apiData.status) === 10) {
        this.$message.error(
          `接口「${apiData.name}」已废弃，不允许被用例引用，请更换为有效接口`
        )
        return
      }
      this.$emit('update:chooseApiVisible', false)
      this.$emit('setApiData', apiData)
    },
    editApi(row_data){
      this.$router.push({path:'/resource/apiEdit', query:{id:row_data.id, mode:'edit'}})
    },
    editMock(row_data){
      this.mockTitle = '编辑MockApi'
      this.isMockAdd = false
      this.readMockView = false
      this.apiMockForm = {...row_data}
      this.mockVisible = true
    },
    runApi(row_data){
      this.$router.push({path:'/resource/apiEdit', query:{id:row_data.id, mode:'edit'}})
    },
    ViewApi(row_data){
      this.$router.push({path:'/resource/apiEdit', query:{id:row_data.id, mode:'view'}})
    },
    ViewMock(row_data){
      this.mockTitle = '查看MockApi'
      this.isMockAdd = false
      this.readMockView = true
      this.apiMockForm = {...row_data}
      this.mockVisible = true
    },
    addApi(){
      const query = {mode:'create'}
      const node = this.$refs.treeRef && this.$refs.treeRef.getCurrentNode()
      if (node){
        if (node.id > 0){
          query.module = node.id
          query.service = node.service_id
        } else {
          query.service = -node.id
        }
      }
      this.$router.push({path:'/resource/apiEdit', query:query})
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
	  this.getApis()
	},
	
    addMockApi(){
      this.mockTitle = '新增MockApi'
      this.isMockAdd = true
      this.readView = false
      this.mockVisible = true
      this.apiMockForm = {...this.tmpApiMockForm}
      if (this.$refs.runRef) {
        this.$refs.runRef.resetFields();
      }
    },
    async import_api(){
      this.$refs['exportRef'].validate(async (valid, fields)=>{
        if(valid){
          this.apiExportSet.project = this.projectInfo.id
          const response = await this.$api.import_api(this.apiExportSet)
          if(response.status === 200){
            this.getApis()
            this.apiExportVisible = false
            ElMessage({
              type: 'success',
              message: '导入成功',
            })
          }
        }
      })
    },
    // ========== 新版导入（V2 - Apifox 风格） ==========
    openImportDialog(){
      this.resetImportDialog(false)
      this.apiImportVisible = true
      this.buildImportModuleTree()
    },
    buildImportModuleTree(){
      // 基于 serviceModuleTree 构建“服务 → 模块”树：
      // - 保留原始 id（services 节点 id 为负数，模块 id 为正数，避免 id 冲突）
      // - 服务节点标记为 disabled，仅允许选择具体模块
      const clone = (nodes) => {
        return (nodes || []).map(n => {
          const isService = n.id < 0
          return {
            id: n.id,
            name: n.name,
            disabled: isService,
            children: clone(n.children),
          }
        })
      }
      this.importModuleTree = clone(this.serviceModuleTree || [])
    },
    onImportFileChange(file, fileList){
      this.importFileList = fileList.slice(-1)
      this.apiImportSet.file = file && file.raw ? file.raw : null
    },
    onImportFileRemove(file, fileList){
      this.importFileList = fileList
      this.apiImportSet.file = null
    },
    nextImportStep(){
      if(!this.canNextImportStep){
        ElMessage({ type: 'warning', message: '请先完善当前步骤必填项' })
        return
      }
      if(this.importStep < 3) this.importStep += 1
    },
    prevImportStep(){
      if(this.importStep > 0) this.importStep -= 1
    },
    resetImportDialog(closeDialog = true){
      this.importStep = 0
      this.importLoading = false
      this.importFileList = []
      this.apiImportSet = {
        format: 'openapi-swagger',
        source: 'file',
        url: '',
        curlText: '',
        file: null,
        service: '',
        module: '',
        uriPrefix: '',
        matchMode: 'overwrite',
      }
      this.importStats = { success: 0, skipped: 0, updated: 0, failed: 0, total: 0, errors: [] }
      if(closeDialog) this.apiImportVisible = false
    },
    async submitImportV2(){
      if(!this.apiImportSet.service){
        ElMessage({ type: 'warning', message: '请选择所属服务' })
        return
      }
      this.importLoading = true
      try {
        let payload
        if(this.apiImportSet.format === 'curl'){
          // cURL 格式：直接传 curl 文本
          payload = {
            format: 'curl',
            source: 'curl',
            service: this.apiImportSet.service,
            module: this.apiImportSet.module || '',
            uriPrefix: this.apiImportSet.uriPrefix || '',
            matchMode: this.apiImportSet.matchMode,
            curlText: this.apiImportSet.curlText,
          }
        } else if(this.apiImportSet.source === 'file'){
          if(!this.apiImportSet.file){
            ElMessage({ type: 'warning', message: '请上传文件' })
            this.importLoading = false
            return
          }
          payload = new FormData()
          payload.append('file', this.apiImportSet.file)
          payload.append('format', this.apiImportSet.format)
          payload.append('source', 'file')
          payload.append('service', this.apiImportSet.service)
          if(this.apiImportSet.module) payload.append('module', this.apiImportSet.module)
          if(this.apiImportSet.uriPrefix) payload.append('uriPrefix', this.apiImportSet.uriPrefix)
          payload.append('matchMode', this.apiImportSet.matchMode)
        } else {
          // url source
          payload = {
            format: this.apiImportSet.format,
            source: 'url',
            service: this.apiImportSet.service,
            module: this.apiImportSet.module || '',
            uriPrefix: this.apiImportSet.uriPrefix || '',
            matchMode: this.apiImportSet.matchMode,
            url: this.apiImportSet.url,
          }
        }
        const response = await this.$api.import_api_v2(payload)
        // CustomRender 会把响应包成 {code, msg, result}，因此实际数据在 response.data.result
        const respBody = response.data || {}
        const innerData = respBody.result || respBody
        if(response.status === 200 && innerData && innerData.task_id){
          // 异步导入：任务已在后台执行，完成后通过站内信通知
          ElMessage({ type: 'success', message: innerData.message || '导入任务已提交，完成后将发送站内信通知' })
          this.resetImportDialog()
        } else {
          ElMessage({ type: 'error', message: innerData.detail || respBody.detail || respBody.msg || '导入失败' })
        }
      } catch (e) {
        ElMessage({ type: 'error', message: '导入异常：' + (e && e.message ? e.message : e) })
      } finally {
        this.importLoading = false
      }
    },
    async deleteApi(id){
      ElMessageBox.confirm(
          '确定删除此接口文档？删除后数据将无法恢复。',
          '确认删除',
          {
            confirmButtonText: '确认删除',
            cancelButtonText: '取消',
            type: 'warning',
            confirmButtonClass: 'el-button--danger',
            customClass: 'confirm-dialog'
          }
        ).then(async() => {
          const response = await this.$api.deleteApi(id)
          if (response.status === 204){
            this.getApis()
            ElMessage({
              type: 'success',
              message: '删除成功',
            })
          }
          
          }).catch(() => {})
    },
    async deleteMock(id){
      ElMessageBox.confirm(
          '确定删除此Mock接口？删除后数据将无法恢复。',
          '确认删除',
          {
            confirmButtonText: '确认删除',
            cancelButtonText: '取消',
            type: 'warning',
            confirmButtonClass: 'el-button--danger',
            customClass: 'confirm-dialog'
          }
        ).then(async() => {
          const response = await this.$api.deleteMock(id)
          if (response.status === 204){
            this.getMocks()
            ElMessage({
              type: 'success',
              message: '删除成功',
            })
          }
          
          }).catch(() => {})
    },
    async getServices(){
      const response = await this.$api.getServices({project: this.projectInfo.id})
      if (response.status === 200){
        this.service_list = {...response.data}
      }
    },
    async getPlantModule(){
      const response = await this.$api.getAllPlantModule({project: this.projectInfo.id})
      if (response.status === 200){
        this.plant_module_list = response.data.results
      }
    },
    async getApis(){
      this.apiSearch.project = this.projectInfo.id
      const data = Object.assign(this.apiSearch, this.page_size_params, this.sort_params)
      this.apiSearch.module = (this.apiSearch.module_list || []).join(',')
      const response = await this.$api.getApis(data)
      if (response.status === 200){
        this.api_list = {...response.data}
      }
    },
    async getApi(id){
      const response = await this.$api.getApi(id)
      if (response.status === 200){
        return {...response.data.result}
      }
    },
   async handleAutoView() {
      if (this.$route.query.autoView === 'true') {
        const apiId = this.$route.query.apiId
        // 清除查询参数并跳转到接口编辑页面查看
        this.$router.replace({
          path: '/resource/apiEdit',
          query: {id: apiId, mode: 'view'}
        })
      }
    },
    async getMocks(){
      const response = await this.$api.getMocks({api: this.apiForm.id})
      if (response.status === 200){
        this.api_mock_list = {...response.data}
      }
    },
    async getEnvs(){
      const response = await this.$api.getEnvs({project: this.projectInfo.id})
      if (response.status === 200){
        this.env_list = {...response.data}
      }
    },
    async getCheck(){
      const response = await this.$api.getCheck()
      if (response.status === 200){
        this.check_methods = response.data.results
      }
    },
    async getfuncs(){
      const response = await this.$api.getFuncs({project: this.projectInfo.id})
      if (response.status === 200){
        this.func_list = [...response.data.results]
      }
    },
    moduleServiceSelect(node){
      if (!node) {
        this.selectServiceNode = null
        this.apiSearch.module_list = []
        this.getApis(false)
        return
      }
      // 如果点击的是已选中的节点，取消选中
      if (this.selectServiceNode === node.id) {
        this.$refs.treeRef?.setCurrentKey(null)
        this.selectServiceNode = null
        this.apiSearch.module_list = []
        localStorage.removeItem('api_node')
        this.getApis(false)
        return
      }
      localStorage.setItem('api_node', JSON.stringify(node))
      this.selectServiceNode = node.id
      if (this.includeChildren) {
        this.apiSearch.module_list = this.getAllIds(node)
      } else {
        this.apiSearch.module_list = [node.id]
      }
      this.getApis(false)
    },
    
    onIncludeChildrenChange() {
      const node = this.$refs.treeRef?.getCurrentNode()
      if (node) {
        if (this.includeChildren) {
          this.apiSearch.module_list = this.getAllIds(node)
        } else {
          this.apiSearch.module_list = [node.id]
        }
        this.getApis(false)
      }
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

    async getPlants() {
      const response = await this.$api.getPlants({ project: this.projectInfo.id })
      if (response.status === 200) {
        this.plant_list = { ...response.data }
      }
    },

    async  check_permission(){
        if (this.parentPermission){
      	  this.permission = this.parentPermission
        }else{
          const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission[this.$route.path]}
          const response = await this.$api.check_permission(params)
          if (response.status === 200){
               this.permission = { ...response.data.result }
          }
        }
	 },
	
	async getRequestHosts() {
	  const response = await this.$api.getRequestHost({ module: this.testApiForm.module, service: this.testApiForm.service, plant: this.testApiForm.plant })
	  if (response.status === 200) {
	    this.envServiceList = { ...response.data.result }
	    if (this.envServiceList.env_hosts.length === 0 && this.testApiForm.plant) {
		  const msg = this.envServiceList.is_server_host ? '该接口所属服务还没添加服务域名配置,': '该接口所属产品还没添加产品域名配置,'
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
  },
  created() {
    this.check_permission()
    this.getAllServiceModule()
	this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
	const node = JSON.parse(localStorage.getItem('api_node'))
	if (node) {
	  this.$nextTick(() => {
	    if (this.$refs.treeRef) {
	      this.$refs.treeRef.setCurrentKey(node.id)
	    }
	  })
	  this.apiSearch.module_list = this.getAllIds(node)
	}
    this.getApis()
    this.user_list =  JSON.parse(localStorage.getItem('user_list'))
    this.tmpApiForm = {...this.apiForm}
    this.tmpApiMockForm = {...this.apiMockForm}
    this.getCheck()
    this.getfuncs()
    this.getServices()
    this.getEnvs()
    this.handleAutoView()
  }
}
</script>

<style scoped>
.api-management-container {
  width: 100%;
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  padding: 20px 15px 15px 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: calc(100vh - 75px);
  height: calc(100vh - 75px);
  max-height: calc(100vh - 75px);
  overflow: hidden;
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

.filter-form-wrapper {
  padding: 25px 24px 0px 24px;
}

/* 内联表单样式 */
.inline-form {
  margin-bottom: 0;
}

.inline-form-item {
    margin-bottom: 20px;
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
    width: 90px;
    
    flex-shrink: 0;
    white-space: nowrap;
}

.inline-label-text {
  white-space: nowrap;
}

/* 图标样式 */
.icon-service,
.icon-module,
.icon-name,
.icon-url,
.icon-method,
.icon-case,
.icon-status,
.icon-creator,
.icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-service {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M4 6h16v2H4zm0 4h16v2H4zm0 4h10v2H4z'/%3E%3C/svg%3E");
}

.icon-module {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z'/%3E%3C/svg%3E");
}

.icon-name {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V6h16v12z'/%3E%3C/svg%3E");
}

.icon-url {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M19 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 14H5V8h14v10z'/%3E%3C/svg%3E");
}

.icon-method {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M10 9h4V6h3l-5-5-5 5h3v3zm-1 1H6V7l-5 5 5 5v-3h3v-4zm14 2l-5-5v3h-3v4h3v3l5-5zm-9 3h-4v3H7l5 5 5-5h-3v-3z'/%3E%3C/svg%3E");
}

.icon-case {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/%3E%3C/svg%3E");
}

.icon-status {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm4.59-12.42L10 14.17l-2.59-2.58L6 13l4 4 8-8z'/%3E%3C/svg%3E");
}

.icon-creator {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
}

.icon-updater {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E");
}

/* 查询区渐变图标 */
.inline-label-wrapper .icon-name,
.inline-label-wrapper .icon-url,
.inline-label-wrapper .icon-method,
.inline-label-wrapper .icon-case,
.inline-label-wrapper .icon-status,
.inline-label-wrapper .icon-creator,
.inline-label-wrapper .icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
}

.inline-label-wrapper .icon-name { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.inline-label-wrapper .icon-url { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.inline-label-wrapper .icon-method { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.inline-label-wrapper .icon-case { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.inline-label-wrapper .icon-status { background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); }
.inline-label-wrapper .icon-creator { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.inline-label-wrapper .icon-updater { background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); }

/* 内联输入框样式 */
.input-inline >>> .el-input__inner,
.select-inline >>> .el-input__inner,
.cascader-inline >>> .el-input__inner {
 /* border-radius: 10px;
  border: 1px solid var(--qm-line-strong); */
  /* background: var(--qm-bg-1); */
  padding: 0 15px;
  box-shadow: none;
  transition: all 0.3s ease;
  flex: 1; /* 占据剩余空间 */
  margin-left: 0px; /* 标签和输入框之间的间距 */
  
}

.input-inline >>> .el-input__inner:hover,
.select-inline >>> .el-input__inner:hover,
.cascader-inline >>> .el-input__inner:hover {
  border-color: var(--qm-line-strong);
  background: var(--qm-bg-2);
}

.input-inline >>> .el-input__inner:focus,
.select-inline >>> .el-input__inner:focus,
.cascader-inline >>> .el-input__inner:focus {
  border-color: #f59e0b;
  /* box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1); */
}

/* 确保el-select也正确显示 */
.select-inline,
.cascader-inline {
  flex: 1;
  margin-left: 12px;
}

/* 内容卡片 */
.content-card {
  flex: 1;
  background: var(--qm-bg-2);
  margin-top: 15px;
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 300px
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

.content-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.add-btn,
.import-btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.import-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border: none;
}

.import-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.add-btn .el-icon,
.import-btn .el-icon {
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

.custom-tree >>> .el-tree-node.is-current > .el-tree-node__content::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  boder: 0px;
  background: linear-gradient(180deg, #f59e0b 0%, #d97706 100%);
  border-radius: 0 2px 2px 0;
}

.custom-tree >>> .el-tree {
  background: transparent;
}

.custom-tree >>> .el-tree-node__content {
  height: 40px;
  border-radius: 8px;
  margin-bottom: 4px;
  transition: all 0.3s ease;
}

.custom-tree >>> .el-tree-node__content:hover {
  background: var(--qm-warning-soft);
}

.custom-tree >>> .el-tree-node.is-current > .el-tree-node__content {
  background: var(--qm-warning-soft);
  position: relative;
}


.custom-tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
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

/* 标签样式 */
.status-tag,
.method-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 12px;
  border: none;
}

/* URL单元格样式 - 修改为两行显示 */
.url-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 0;
}

.copy-action-row {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.copy-link {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #f59e0b;
  cursor: pointer;
  transition: all 0.3s ease;
}

.copy-link:hover {
  color: #d97706;
}

.copy-icon {
  cursor: pointer;
  transition: all 0.3s ease;
}

.copy-link:hover .copy-icon {
  transform: scale(1.1);
}

.url-text-row {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  word-break: break-all;
}

.url-text {
  font-size: 12px;
  color: var(--qm-text-2);
  text-align: center;
  line-height: 1.4;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 信息单元格样式 */
.info-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 0;
}

.info-user,
.info-time {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  justify-content: center;
}

.icon-user {
  width: 12px;
  height: 12px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
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
  font-size: 12px;
  color: var(--qm-text-2);
  line-height: 1.4;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 关联用例个数单元格 */
.case-count-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.case-count {
  display: flex;
  align-items: center;
  justify-content: center;
}

.case-count-number {
  font-weight: 600;
  color: #f59e0b;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 4px 8px;
  border-radius: 6px;
  background: rgba(245, 158, 11, 0.1);
}

.case-count-number:hover {
  background: rgba(245, 158, 11, 0.2);
  transform: scale(1.05);
}

.case-tooltip-content {
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
}

.case-item {
  margin-bottom: 8px;
  padding: 4px 0;
  border-bottom: 1px solid var(--qm-bg-3);
}

.case-item:last-child {
  margin-bottom: 0;
  border-bottom: none;
}

.case-link {
  font-size: 13px;
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

/* 对话框样式 */
.elegant-dialog >>> .el-dialog {
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

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

/* ========== 导入对话框（Apifox 风格） ========== */
.import-dialog >>> .el-dialog__body {
  padding: 16px 24px 8px;
}

.import-steps {
  margin-bottom: 24px;
}

.import-steps >>> .el-step__icon.is-process {
  border-color: #f59e0b;
  color: #f59e0b;
}

.import-steps >>> .el-step__title.is-process,
.import-steps >>> .el-step__title.is-finish {
  color: #d97706;
  font-weight: 600;
}

.step-content {
  min-height: 320px;
  padding: 8px 4px;
  overflow-x: hidden;
}

/* Step 0：格式卡片网格 */
.format-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 14px;
}

.format-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 16px;
  border-radius: 14px;
  border: 2px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  cursor: pointer;
  transition: all 0.25s ease;
}

.format-card:hover {
  border-color: var(--qm-line-strong);
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
}

.format-card.active {
  border-color: #f59e0b;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(217, 119, 6, 0.04) 100%);
  box-shadow: 0 6px 18px rgba(245, 158, 11, 0.18);
}

.format-card .format-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  object-fit: contain;
  background: transparent;
  padding: 2px;
  box-sizing: border-box;
}

.format-card.active .format-icon {
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.35);
}

.format-info {
  flex: 1;
  min-width: 0;
}

.format-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--qm-text-1);
  margin-bottom: 4px;
}

.format-desc {
  font-size: 12px;
  color: var(--qm-text-2);
}

.format-check {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 18px;
  color: #f59e0b;
}

/* Step 1：数据来源 Tabs */
.source-tabs >>> .el-tabs__header {
  margin: 0 0 16px;
  padding: 0;
}

.source-tabs >>> .el-tabs__nav-wrap::after {
  background: var(--qm-bg-3);
}

.source-tabs >>> .el-tabs__item.is-active {
  color: #d97706;
  font-weight: 600;
}

.source-tabs >>> .el-tabs__active-bar {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  height: 3px;
  border-radius: 2px;
}

.import-uploader >>> .el-upload-dragger {
  width: 100%;
  height: 220px;
  border-radius: 14px;
  border: 2px dashed var(--qm-line-strong);
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease;
}

.import-uploader >>> .el-upload-dragger:hover {
  border-color: #f59e0b;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.04) 0%, rgba(217, 119, 6, 0.02) 100%);
}

.import-uploader >>> .el-upload__text {
  color: var(--qm-text-2);
  font-size: 14px;
  margin-top: 8px;
}

.import-uploader >>> .el-upload__text em {
  color: #f59e0b;
  font-style: normal;
  font-weight: 600;
}

.import-uploader >>> .el-icon--upload {
  font-size: 56px;
  color: #f59e0b;
  margin-bottom: 8px;
}

.import-uploader >>> .el-upload__tip {
  text-align: center;
  color: var(--qm-text-3);
  font-size: 12px;
  margin-top: 12px;
}

.source-tip {
  margin-top: 10px;
  font-size: 12px;
  color: var(--qm-text-3);
}

.curl-textarea >>> .el-textarea__inner {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  min-height: 180px;
}

.import-dialog .text.el-textarea >>> .el-textarea__inner {
  overflow-x: hidden !important;
  overflow-y: auto !important;
  white-space: pre-wrap !important;
  word-break: break-all !important;
}

.import-dialog .text.el-textarea {
  overflow: hidden !important;
  box-sizing: border-box !important;
  width: 100% !important;
}

/* Step 2：配置选项 */
.full-width {
  width: 100%;
}

.match-mode-group >>> .el-radio-button__inner {
  padding: 10px 18px;
  border-radius: 0 !important;
  border: 1px solid var(--qm-line-strong) !important;
  background: var(--qm-bg-2);
  color: var(--qm-text-2);
  font-weight: 500;
  transition: all 0.25s ease;
}

.match-mode-group >>> .el-radio-button:first-child .el-radio-button__inner {
  border-radius: 10px 0 0 10px !important;
}

.match-mode-group >>> .el-radio-button:last-child .el-radio-button__inner {
  border-radius: 0 10px 10px 0 !important;
}

.match-mode-group >>> .el-radio-button.is-active .el-radio-button__inner {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
  color: #ffffff !important;
  border-color: #d97706 !important;
  box-shadow: -1px 0 0 0 #d97706 !important;
}

.form-tip {
  margin-top: 6px;
  font-size: 12px;
  color: var(--qm-text-3);
}

/* Step 3：导入结果 */
.result-summary {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 20px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  margin-bottom: 18px;
}

.result-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  flex-shrink: 0;
}

.result-icon.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #ffffff;
}

.result-icon.partial {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #ffffff;
}

.result-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--qm-text-1);
}

.result-sub {
  font-size: 13px;
  color: var(--qm-text-2);
  margin-top: 4px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat-cell {
  padding: 16px;
  border-radius: 12px;
  text-align: center;
  background: var(--qm-bg-1);
  border: 1px solid var(--qm-line-strong);
}

.stat-cell .num {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-cell .lbl {
  font-size: 12px;
  color: var(--qm-text-2);
  margin-top: 4px;
}

.stat-cell.success .num { color: #10b981; }
.stat-cell.updated .num { color: #f59e0b; }
.stat-cell.skipped .num { color: var(--qm-text-3); }
.stat-cell.failed .num  { color: #ef4444; }

.error-list {
  background: var(--qm-red-soft);
  border: 1px solid #fecaca;
  border-radius: 10px;
  padding: 12px 14px;
  max-height: 160px;
  overflow-y: auto;
}

.error-title {
  font-size: 13px;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 8px;
}

.error-item {
  font-size: 12px;
  color: #991b1b;
  line-height: 1.6;
  padding: 2px 0;
  border-bottom: 1px dashed #fecaca;
}

.error-item:last-child {
  border-bottom: none;
}

/* Mock对话框特殊样式 */
.mock-form-wrapper {
  padding: 0;
}

.mock-tabs-wrapper {
  margin-top: 10px;
}

.body-type-wrapper {
  padding: 10px 0;
}

.response-type-wrapper {
  padding: 10px 0;
}

.response-header {
  margin-bottom: 15px;
}

.response-settings {
  margin-bottom: 15px;
}

.follow-api-info {
  margin-top: 15px;
}

/* ============================================
   抽屉样式优化 - 与列表样式保持一致
   ============================================ */
.api-drawer >>> .el-drawer {
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
}

.api-drawer >>> .el-drawer__body {
  padding: 20px !important;
  overflow: hidden !important;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
}

.drawer-card {
  flex: 1;
  background: var(--qm-bg-2);
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  
  overflow: hidden;
  overflow-y: hidden;
}

/* drawer-tabs 下划线 - 参考消息弹窗 tab 样式 */
.drawer-tabs >>> .el-tabs__header {
  margin: 0;
  padding: 0px 24px 0;
  background: var(--qm-bg-2);
  border-bottom: 1px solid var(--qm-line-strong);
  overflow: visible !important;
}

.drawer-tabs >>> .el-tabs__nav-wrap {
  overflow: visible !important;
}

.drawer-tabs >>> .el-tabs__nav-scroll {
  overflow: visible !important;
}

.drawer-tabs >>> .el-tabs__nav-wrap::after {
  display: none;
}

.drawer-tabs >>> .el-tabs__active-bar {
  display: none;
}

.drawer-tabs >>> .el-tabs__item {
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

.drawer-tabs >>> .el-tabs__item::after {
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

.drawer-tabs >>> .el-tabs__item:hover {
  color: #f59e0b;
}

.drawer-tabs >>> .el-tabs__item:hover::after {
  width: 100%;
  background: rgba(245, 158, 11, 0.5);
}

.drawer-tabs >>> .el-tabs__item.is-active {
  color: #f59e0b;
  font-weight: 600;
}

.drawer-tabs >>> .el-tabs__item.is-active::after {
  width: 100%;
  background: #f59e0b;
}

.drawer-tabs >>> .el-tabs__content {
  flex: 1;
  padding: 0;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.drawer-form-container {
  flex: 1;
  padding: 24px;
  overflow-y: hidden;
  min-height: 0;
}

.drawer-form {
  width: 100%;
}

/* 表单卡片样式 */
.form-section-card {
  background: var(--qm-bg-2);
  border-radius: 12px;
  margin-bottom: 24px;
  padding: 20px;
  border: 1px solid var(--qm-line-strong);
}

.form-section-header {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--qm-bg-3);
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--qm-text-1);
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

.form-row {
  margin-bottom: 16px;
}

.form-row:last-child {
  margin-bottom: 0;
}

/* 抽屉表单项目样式 */
.drawer-form-item {
  margin-bottom: 16px;
}

.drawer-form-item:last-child {
  margin-bottom: 0;
}

.drawer-label-wrapper {
  display: flex;
  align-items: center;
  
  margin-bottom: 8px;
}

.drawer-label-text {
  line-height: 40px;
  margin-left: 10px;
  font-size: 14px;
  width:80px;
  font-weight: 500;
  color: var(--qm-text-2);
}

/* 抽屉输入框样式 */
.drawer-input >>> .el-input__inner,
.drawer-select >>> .el-input__inner,
.drawer-cascader >>> .el-input__inner {
  height: 40px;
  line-height: 40px;
  width: 100%
}


.drawer-method-url >>> .el-input-group__prepend {
  background: transparent;
  border: none;
  padding: 0;
}

.drawer-method-select {
  width: 120px;
}

.drawer-method-select >>> .el-input__inner {
  border-radius: 10px 0 0 10px;
  border-right: 1px solid var(--qm-line-strong);
}

.drawer-method-url >>> .el-input__inner {
  border-radius: 0 10px 10px 0;
}

/* 抽屉单选按钮组样式 */
.drawer-radio-group >>> .el-radio-button__inner {
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  color: var(--qm-text-2);
  font-weight: 500;
  transition: all 0.3s ease;
}

.drawer-radio-group >>> .el-radio-button:first-child .el-radio-button__inner {
  border-radius: 10px 0 0 10px;
}

.drawer-radio-group >>> .el-radio-button:last-child .el-radio-button__inner {
  border-radius: 0 10px 10px 0;
}

.drawer-radio-group >>> .el-radio-button__orig-radio:checked + .el-radio-button__inner {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-color: transparent;
  color: white;
  box-shadow: none;
}

/* 抽屉子标签页样式 */
.drawer-sub-tabs >>> .el-tabs__header {
  margin: 0 0 16px 0;
  padding: 0;
}

.drawer-sub-tabs >>> .el-tabs__nav-wrap::after {
  background-color: var(--qm-line-strong);
}

.drawer-sub-tabs >>> .el-tabs__content {
  flex: 1;
}

/* 请求体类型头部 */
.body-type-header {
  margin-bottom: 16px;
  padding: 12px 16px;
  background: var(--qm-bg-1);
  border-radius: 8px;
  border: 1px solid var(--qm-line-strong);
}

.drawer-sub-select {
  width: 150px;
}

/* 抽屉按钮样式 */
.drawer-confirm-btn {
  padding: 10px 24px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.drawer-confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.drawer-cancel-btn {
  padding: 10px 24px;
  border-radius: 10px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  color: var(--qm-text-2);
  font-weight: 500;
  transition: all 0.3s ease;
}

.drawer-cancel-btn:hover {
  background: var(--qm-bg-1);
  border-color: var(--qm-line-strong);
  transform: translateY(-1px);
}

.drawer-send-btn {
  /* width: 100%; */
  float: right;
}

/* 抽屉页脚样式 */
.drawer-footer {
  padding: 20px 20px 0px 20px;
  border-top: 1px solid var(--qm-bg-3);
  background: var(--qm-bg-2);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 关联脚本用例管理样式 */
.case-management {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: var(--qm-bg-1);
  border-radius: 12px;
  border: 1px solid var(--qm-line-strong);
}

.case-stat {
  display: flex;
  align-items: center;
  gap: 8px;
}

.case-stat-label {
  font-size: 14px;
  color: var(--qm-text-2);
  font-weight: 500;
}

.case-stat-number {
  font-size: 16px;
  font-weight: 600;
  color: #f59e0b;
  padding: 4px 12px;
  border-radius: 6px;
  background: rgba(245, 158, 11, 0.1);
}

.case-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--qm-text-3);
}

.icon-case {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 4px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

/* 高级Mock管理样式 */
.mock-management {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.mock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: var(--qm-bg-1);
  border-radius: 12px;
  border: 1px solid var(--qm-line-strong);
}

.drawer-add-btn {
  padding: 10px 20px;
  border-radius: 10px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drawer-add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.drawer-add-btn .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

.mock-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.mock-link {
  font-size: 14px;
  color: #f59e0b;
}

/* 响应标签页样式 */
.response-tabs >>> .el-tabs__new-tab {
  margin-left: 8px;
  border-radius: 8px;
  background: var(--qm-bg-3);
  border: 1px solid var(--qm-line-strong);
  color: var(--qm-text-2);
}

.response-tabs >>> .el-tabs__new-tab:hover {
  background: var(--qm-line-strong);
  color: #f59e0b;
}

/* 隐藏滚动条但保留功能 */
.api-management-container ::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.api-management-container ::-webkit-scrollbar-track {
  background: var(--qm-bg-3);
  border-radius: 3px;
}

.api-management-container ::-webkit-scrollbar-thumb {
  background: var(--qm-line-strong);
  border-radius: 3px;
}

.api-management-container ::-webkit-scrollbar-thumb:hover {
  background: var(--qm-text-3);
}

/* 修复 el-drawer 滚动条问题 */
/* :deep(.api-drawer .el-drawer__body) {
  overflow: auto !important;
} */

:deep(.drawer-form-container) {
  overflow-y: auto;
  max-height: calc(100vh - 220px);
}

/* 右侧内容区域 */
.content-main {
	padding: 0px;
	display: flex;
	flex-direction: column;
	min-height: 0;
	flex: 1;
	width: calc(100% - 320px);
	box-sizing: border-box;
	min-height: calc(100vh - 105px);
	height: calc(100vh - 105px);
	max-height: calc(100vh - 105px);
}

.tab-content-wrapper {
	flex: 1;
	display: flex;
	flex-direction: column;
	min-height: 0;
	padding: 0;
	width: 100%;
	height: 100%;
	background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
}

.tab-container {
	flex: 1;
	display: flex;
	min-height: 0;
	width: 100%;
	height: 100%;
	
	box-sizing: border-box;
	align-items: stretch;
}

/* 左侧树形结构 */
.tree-aside {
	display: flex;
	flex-direction: column;
	width: 320px;
	flex-shrink: 0;
	padding-right: 16px;
	box-sizing: border-box;
	min-height: calc(100vh - 100px);
	height: calc(100vh - 100px);
	max-height: calc(100vh - 100px);
	overflow-y: hidden;
}

.tree-card {
	background: var(--qm-bg-2);
	border: none;
	border-radius: 16px;
	display: flex;
	flex-direction: column;
	width: 100%;
	/* min-height: calc(100vh - 105px);
	overflow-y: hidden; */
	box-sizing: border-box;
	position: relative;
}

::v-deep .tree-card .el-card__body {
  padding-top: 15px;
  padding-right: 10px;
}

::v-deep .filter-card .el-card__body {
  padding-bottom: 10px;
}

::v-deep .drawer-card .el-card__body {
  padding: 0px 5px;
  
}

.tree-card-content {
	flex: 1;
	display: flex;
	flex-direction: column;
	/* overflow-x: hidden;
	overflow-y: hidden;
	min-height: calc(100vh - 180px);
	max-height: calc(100vh - 180px);
	height: calc(100vh - 180px); */
}

.tree-header {
	padding: 16px 12px 12px 8px;
	margin-bottom:10px;
	border-bottom: 1px solid var(--qm-bg-3);
	display: flex;
	justify-content: space-between;
	align-items: center;
	flex-shrink: 0;
	gap: 12px;
}

.tree-title-wrapper {
  display: flex;
  align-items: center;
}

.include-children-radio {
  flex-shrink: 0;
}

.tree-title {
	margin: 0;
	font-size: 16px;
	font-weight: 600;
	color: var(--qm-text-1);
	display: flex;
	align-items: center;
	gap: 8px;
	white-space: nowrap;
}

.tree-title::before {
	content: '';
	width: 4px;
	height: 20px;
	background: linear-gradient(135deg, #10b981 0%, #059669 100%);
	border-radius: 2px;
}

.tree-search-input {
	margin: 16px 20px;
	flex-shrink: 0;
}

:deep(.tree-search-input .el-input__inner) {
	border-radius: 10px;
	border: 1px solid var(--qm-line-strong);
	background: var(--qm-bg-1);
	padding: 0 16px 0 40px;
	height: 36px;
	line-height: 36px;
	transition: all 0.3s ease;
}

:deep(.tree-search-input .el-input__inner:hover) {
	border-color: var(--qm-line-strong);
	background: var(--qm-bg-2);
}

:deep(.tree-search-input .el-input__inner:focus) {
	border-color: #10b981;
	box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

:deep(.tree-search-input .el-input__prefix) {
	display: flex;
	align-items: center;
	justify-content: center;
	left: 12px;
	color: var(--qm-text-3);
}

.tree-wrapper {
	flex: 1;
	padding: 0 12px 16px 10px;
	overflow-y: auto;
	overflow-x: hidden;
	box-sizing: border-box;
}

.custom-tree {
	background: transparent;
	height: calc(100vh - 340px);
	width: 100%;
	max-width: 100%;
}

:deep(.custom-tree .el-tree-node__content) {
	height: 40px;
	border-radius: 8px;
	margin-bottom: 4px;
	transition: all 0.3s ease;
	overflow: hidden;
}

:deep(.custom-tree .el-tree-node__content:hover) {
	background-color: var(--qm-warning-soft);
}

:deep(.custom-tree .el-tree-node:focus > .el-tree-node__content) {
	background-color: var(--qm-warning-soft);
}

:deep(.custom-tree .el-tree-node.is-current > .el-tree-node__content) {
	background: linear-gradient(135deg, var(--qm-warning-soft) 0%, var(--qm-warning-soft-2) 100%);
	/* border: 1px solid #f59e0b; */
}

.custom-tree-node {
	display: flex;
	align-items: center;
	width: 100%;
	padding-right: 8px;
	box-sizing: border-box;
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

.node-label {
	display: block;
	font-size: 14px;
	font-weight: 500;
	color: var(--qm-text-1);
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
	flex: 1;
	min-width: 0;
}



.icon-folder-tree {
	width: 16px;
	height: 16px;
	display: inline-block;
	background-size: contain;
	background-repeat: no-repeat;
	flex-shrink: 0;
}

.icon-folder-tree {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z'/%3E%3C/svg%3E");
}

.icon-folder-tree-root {
	background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z'/%3E%3C/svg%3E");
}

.node-actions {
	opacity: 0;
	transition: opacity 0.3s ease;
}

:deep(.custom-tree .el-tree-node__content:hover .node-actions) {
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

.tree-footer {
	padding: 0px;
	margin-top: 15px;
	/* border-top: 1px solid var(--qm-bg-3); */
	flex-shrink: 0;
	background: var(--qm-bg-2);
	position: relative;
	z-index: 2;
}

.tree-divider {
	margin: 0;
}

.tree-actions {
	display: flex;
	justify-content: space-between;
	gap: 12px;
}

.tree-action-btn {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 6px;
	border-radius: 8px;
	font-weight: 500;
}

.tree-action-btn .el-icon {
	font-size: 14px;
}

:deep(.el-drawer__body) {
  padding: 20 !important;
  overflow: hidden !important;
  height: 100%;
  display: flex;
  flex-direction: column;
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
</style>
