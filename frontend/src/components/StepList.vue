<template>
	<!-- 模块编辑对话框 -->
	<el-dialog v-model="editModuleVisible" :title="moduleTitle" width='450' class="elegant-dialog">
	  <div class="dialog-content">
	    <el-form :model="moduleSave" label-position='top' :rules="moduleRules" ref='moduleRef' class="dialog-form" :disabled="moduleView">
	      <el-form-item  prop='name' class="dialog-form-item">
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
	      <el-button type="primary" @click="save" class="dialog-confirm-btn">保存</el-button>
	    </span>
	  </template>
	</el-dialog>
	
	<!-- 主容器 -->
	<div class="case-management-container">
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
			<div class="step-container">
				<!-- 搜索筛选区域 -->
				<el-card class="filter-card elegant-shadow">
					<div class="filter-header">
						<div class="header-title-section">
							<i class="icon-search"></i>
							<h3 class="filter-title">步骤筛选</h3>
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
						<el-form :model="stepSearch" class="filter-form inline-form">
							<el-row :gutter="24">
								<el-col :xs="24" :sm="12" :md="8" :lg="6">
									<el-form-item class="form-item-horizontal">
										<div class="horizontal-label">
											<i class="icon-step-type"></i>
											<span>步骤类型</span>
										</div>
										<el-select 
											v-model="stepSearch.type" 
											clearable 
											placeholder="请选择步骤类型" 
											
											class="select"
											size='large'
											popper-class='select-dropdown-rounded'
										>
											<el-option 
												v-for="(value, key) in StepType" 
												:label="key" 
												:value="value"
												:key="value"
											></el-option>
										</el-select>
									</el-form-item>
								</el-col>
								<el-col :xs="24" :sm="12" :md="8" :lg="6">
									<el-form-item class="form-item-horizontal">
										<div class="horizontal-label">
											<i class="icon-case"></i>
											<span>用例名称</span>
										</div>
										<el-select 
											v-model="stepSearch.case" 
											clearable 
											placeholder="请选择用例" 
											class="select"
											filterable
											size='large'
											popper-class='select-dropdown-rounded'
										>
											<el-option 
												v-for="obj in case_list" 
												:label="obj.name" 
												:value="obj.id"
												:key="obj.id"
											></el-option>
										</el-select>
									</el-form-item>
								</el-col>
								<el-col :xs="24" :sm="12" :md="8" :lg="6">
									<el-form-item class="form-item-horizontal">
										<div class="horizontal-label">
											<i class="icon-step-name"></i>
											<span>步骤名称</span>
										</div>
										<el-input 
											v-model="stepSearch.desc" 
											placeholder="请输入步骤名称" 
											clearable
											class="input"
											size='large'
										/>
									</el-form-item>
								</el-col>
								<el-col :xs="24" :sm="12" :md="8" :lg="6">
								  <el-form-item class="inline-form-item">
								    <div class="inline-label-wrapper">
								      <i class="icon-creator"></i>
									<el-select
									  v-model="search_person" 
									  placeholder="请选择" 
									  filterable
									  class="select"
									  size='large'
									  style='width: 100px'
									  popper-class='select-dropdown-rounded'
									>
									  <el-option  label='创建人' :value="1" />
									  <el-option  label='更新人' :value="2" />
									</el-select>
								      <!-- <span class="inline-label-text">创建人</span> -->
								    </div>
								    <el-select 
									  v-if='search_person ===1'
								      v-model="stepSearch.create_by" 
								      placeholder="请选择" 
								      clearable
								      filterable
								      class="select"
									  size='large'
									  popper-class='select-dropdown-rounded'
								    >
								      <el-option v-for="user_obj in user_list" :label='user_obj.username' :value="user_obj.id" />
								    </el-select>
								  <el-select
									v-if='search_person ===2'
									v-model="stepSearch.update_by" 
									placeholder="请选择" 
									clearable
									filterable
									class="select"
									size='large'
									popper-class='select-dropdown-rounded'
								  >
									<el-option v-for="user_obj in user_list" :label='user_obj.username' :value="user_obj.id" />
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
								<h3 class="content-title">步骤列表</h3>
								<div class="stats-info">
									<div class="stat-item">
										<span class="stat-label">总计</span>
										<span class="stat-value">{{ step_list.count || 0 }}</span>
									</div>
									<div class="stat-item">
										<span class="stat-label">当前页</span>
										<span class="stat-value">{{ page_size_params.page }}</span>
									</div>
									<div class="stat-item" v-if="isCanChoose" >
										<span class="stat-label">已选中</span>
										<span class="stat-value">{{ multipleSelection.length }}</span>
									</div>
								</div>
							</div>
							<el-button
							  v-if="isCanChoose === true && is_com === true" 
							  @click="chooseManyComStepData"  
							  type="primary" 
							  class="add-btn"
							>
							  <el-icon><Pointer /></el-icon>批量选择
							</el-button>
							<el-button
							  v-if="isCanChoose === true && is_com === false" 
							  @click="chooseManyStepData"  
							  type="primary" 
							  class="add-btn"
							>
							  <el-icon><Pointer /></el-icon>批量选择
							</el-button>
						</div>
					</div>
			
					<!-- 数据表格 -->
					<div class="table-wrapper">
						<el-table 
							:data="step_list.results" 
							:max-height="'calc(100vh - 485px)'" 
							class="elegant-table"
							@selection-change="handleSelectionChange"
							@sort-change='handleSortChange'
							:header-row-style="headerRowStyle"
							
						>
							<el-table-column 
								label="序号" 
								width="70" 
								type="index" 
								align="center"
								class-name="index-column"
								v-if='!isCanChoose'
							>
								<template #default="scope">
									<div class="index-cell">
										{{ scope.$index + 1 + (page_size_params.page - 1) * page_size_params.size }}
									</div>
								</template>
							</el-table-column>
							<el-table-column type="selection" width="55" v-if='isCanChoose'></el-table-column>
			
							
							<el-table-column 
								label="步骤名称" 
								prop="desc" 
								min-width="300" 
								align="center"
								class-name="step-name-column"
							>
								<template #default='scope'>
									<div class="step-name-cell">
										<el-tooltip 
											effect="dark" 
											:content="scope.row.desc" 
											placement="top-start"
										>
											<div class="step-desc">
												{{ scope.row.desc.length <= 25 ? scope.row.desc : scope.row.desc.slice(0, 25) + '...' }}
											</div>
										</el-tooltip>
									</div>
								</template>
							</el-table-column>
							
							<el-table-column 
								label="步骤类型" 
								min-width="220" 
								align="center" 
								header-align="center"
								class-name="step-type-column"
							>
								<template #default="scope">
									<div class="step-type-tags">
										<!-- Request 类型 -->
										<template v-if='scope.row.type === 5 || scope.row.com_step_type === 5'>
											<el-tag 
												color='#3498DB' 
												effect='dark' 
												class="step-tag"
											>
												HTTP接口请求
											</el-tag>
											<el-tag 
												color='#3498DB' 
												effect='dark' 
												class="step-tag"
											>
												{{ scope.row.api_method }}
											</el-tag>
											<el-tag 
												effect='dark' 
												color='#3498DB' 
												@click='jumpApi(scope.row.keyword)' 
												class="step-tag clickable"
											>
												关联接口-{{ scope.row.keyword }}
											</el-tag>
										</template>
										
										<!-- Selenium 类型 -->
										<template v-if='scope.row.type === 2 || scope.row.com_step_type === 2'>
											<el-tag 
												color="#2ECC71" 
												effect='dark'
												class="step-tag"
											>
												WEB自动化
											</el-tag>
											<el-tag 
												color="#2ECC71" 
												effect='dark'
												class="step-tag"
											>
												{{ scope.row.keyword }}
											</el-tag>
										</template>

										<!-- Selenium 类型 -->
										<template v-if='scope.row.type === 10 || scope.row.com_step_type === 10'>
											<el-tag 
												color="#2ECC71" 
												effect='dark'
												class="step-tag"
											>
												WEB自动化
											</el-tag>
											<el-tag 
												color="#2ECC71" 
												effect='dark'
												class="step-tag"
											>
												{{ scope.row.keyword }}
											</el-tag>
										</template>
										
										<!-- PythonScript 类型 -->
										<el-tag 
											v-if='scope.row.type === 4 || scope.row.com_step_type === 4' 
											color="#9B59B6" 
											effect='dark'
											class="step-tag"
										>
											Python脚本
										</el-tag>
										
										<!-- Appium 类型 -->
										<template v-if='scope.row.type === 7 || scope.row.com_step_type === 7'>
											<el-tag 
												color="#009688" 
												effect='dark'
												class="step-tag"
											>
												APP自动化
											</el-tag>
											<el-tag 
												color="#009688" 
												effect='dark'
												class="step-tag"
											>
												{{ scope.row.keyword }}
											</el-tag>
										</template>
										
										<!-- SQL 类型 -->
										<template v-if='scope.row.type === 8 || scope.row.com_step_type === 8'>
											<el-tag 
												color="#F1C40F" 
												effect='dark'
												class="step-tag"
											>
												数据库操作
											</el-tag>
											<el-tag 
												color="#F1C40F" 
												effect='dark'
												class="step-tag"
											>
												{{ scope.row.keyword }}
											</el-tag>
										</template>
										
										<!-- Control 类型 -->
										<el-tag 
											v-if='(scope.row.type === 9 || scope.row.com_step_type === 9) && scope.row.keyword === "1"' 
											color="#1ABC9C" 
											effect='dark'
											class="step-tag"
										>
											IF条件控制器
										</el-tag>
										<el-tag 
											v-if='(scope.row.type === 9 || scope.row.com_step_type === 9) && scope.row.keyword === "2"' 
											color="#1ABC9C " 
											effect="dark"
											class="step-tag"
										>
											FOR循环控制器
										</el-tag>
										<el-tag
											v-if='scope.row.type === 9 && scope.row.keyword === "6"' 
											color="#1ABC9C " 
											effect="dark"
											class="step-tag"
										>
											FOREACH循环控制器
										</el-tag>
										<el-tag 
											v-if='(scope.row.type === 9 || scope.row.com_step_type === 9) && scope.row.keyword === "3"' 
											color="#1ABC9C " 
											effect="dark"
											class="step-tag"
										>
											WHILE控制器
										</el-tag>
										<el-tag 
											v-if='(scope.row.type === 9 || scope.row.com_step_type === 9) && scope.row.keyword === "4"' 
											color="#1ABC9C " 
											effect="dark"
											class="step-tag"
										>
											事务控制器
										</el-tag>
										<el-tag 
											v-if='(scope.row.type === 9 || scope.row.com_step_type === 9) && scope.row.keyword === "5"' 
											color="#1ABC9C " 
											effect="dark"
											class="step-tag"
										>
											等待时间控制器
										</el-tag>
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
											effect='light'
											:disabled="!scope.row.case_info || scope.row.case_info.length === 0"
										>
											<template #content>
												<div class="case-tooltip-content">
													<div 
														v-for='(case_obj, index) in scope.row.case_info'
														:key="case_obj.id"
														class="case-item"
													>
														<el-link 
															type="primary" 
															@click='jumpCase(case_obj.id)'
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
							
							<el-table-column 
								label="创建人" 
								prop="create_by_name" 
								min-width="100" 
								align="center"
								class-name="creator-column"
							/>
							
							<el-table-column 
								label="更新人" 
								prop="update_by_name" 
								min-width="100" 
								align="center"
								class-name="updater-column"
							/>
							
							<el-table-column 
								label="创建时间" 
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
								label="更新时间" 
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
								width="80" 
								v-if="isCanChoose === true" 
								label="操作" 
								fixed="right"
								class-name="action-column"
							>
								<template #default="scope">
									<div class="action-buttons">
										<el-tooltip 
											content="选择" 
											placement="top" 
											effect="dark"
										>
											<el-button 
												type='primary' 
												v-if="isCanChoose === true && is_com === false" 
												:icon="Pointer" 
												size="large" 
												circle
												@click="chooseStepData(scope.row)" 
												class="action-btn choose-btn"
											></el-button>
										</el-tooltip>
										<el-tooltip 
											content="选择" 
											placement="top" 
											effect="dark"
										>
											<el-button 
												type='primary' 
												v-if="isCanChoose === true && is_com === true" 
												:icon="Pointer" 
												size="large" 
												circle
												@click="chooseComStepData(scope.row)" 
												class="action-btn choose-btn"
											></el-button>
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
							:total="step_list.count"
							@size-change="handleSizeChange"
							@current-change="handleCurrentChange"
							class="select input"
							:background="true"
						/>
					</div>
				</el-card>
			</div>
	  </div>
	</div>
</template>

<script>
import {mapState, mapActions, mapGetters} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, Pointer, Plus, EditPen, Refresh, Search } from '@element-plus/icons-vue'

export default{
	watch: {
	  filterText(val) {
	    if (this.$refs.treeRef) {
	      this.$refs.treeRef.filter(val)
	    }
	  }
	},
	computed:{
		...mapState(['pathPermission', 'projectInfo', 'userInfo']),
		chooseStepVisible: {
			get(){
				return this.chooseStepVisible
			},
			set(value){
				this.$emit('update:chooseStepVisible', value)
			}
		},
		chooseComStepVisible: {
			get(){
				return this.chooseComStepVisible
			},
			set(value){
				this.$emit('update:chooseComStepVisible', value)
			}
		},
	},
	emits: ['update:chooseStepVisible', 'setStepData', 'update:chooseComStepVisible', 'setComStepData'],
	props: {
		'isCanChoose': {
			type: Boolean,
			default: false,
		},
		'parentPermission': {
              type: Object,
              default: null,
        },
		'is_com': {
			type: Boolean,
			default: false,
		}
	},
	data() {
		return {
			editModuleVisible: false,
			plant_module_list: [],
			filterText: '',
			multipleSelection: [], // 存储选中的行
			permission: {},
			search_person: 1,
			stepSearch:{
				desc: '',
				type: '',
				case: '',
				module: '',
				// 必须初始化：getSteps() 会直接 join，未点模块树时为 undefined 会抛 TypeError
				module_list: [],
				create_by: '',
				update_by: '',
			},
			moduleTitle: '',
			user_list: [],
			moduleSave:{
			  project: '',
			  name: '',
			  plant: '',
			  parent: 0,
			},
			caseSearch:{
			  module: '',
			  project: '',
			  module_list: [],
			},
			selectNode: 0,
			includeChildren: true,
			StepType:{
				'HTTP接口请求': 5,                  
				'WEB自动化': 2,                  
				'Python脚本': 4,
				'APP自动化': 7,
				"数据库操作": 8,
				"逻辑控制器": 9
			},
			case_list: [],
			page_size_params: {
				page: 1,
				size: 10,
			},
			sort_params: {
			  ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
			},
			count: 1,
			step_list: [],
			role_names: [],
		}
	},
	setup() {
		return {
			Pointer,
			Delete,
			Plus,
			View,
			EditPen,
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
		jumpCase(case_id){
			this.$router.push({path: '/resource/scriptCaseEdit', query: {id: case_id}})
		},
		handleSelectionChange(val) {
		    this.multipleSelection = val
		},
		jumpApi(api_id){
			this.$router.push({path: '/resource/apiEdit', query: {id: api_id, mode: 'view'}})
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
		
		controlCommand(command){
		  this.module_node = command
		  if(command.action === 'add'){
		    this.editModuleVisible = true
		    this.moduleTitle = '新增模块'
		  }else if(command.action === 'edit'){
		    this.moduleSave = {...this.module_node.node.data}
		    this.editModuleVisible = true
		    this.moduleTitle = '编辑模块'
		  }else if(command.action === 'delete'){
		    this.deleteModule(this.module_node.node.data.id)
		  }
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
		
		async getCases(){
		  this.caseSearch.project = this.projectInfo.id
		  this.caseSearch.module = (this.stepSearch.module_list || []).join(',')
		  const response = await this.$api.getCases(this.caseSearch)
		  if (response.status === 200){
		    this.case_list = {...response.data.results}
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
		        this.moduleSave.plant = -this.module_node.node.data.id
		        this.moduleSave.parent = null
		      }else{
		        this.moduleSave.plant = this.module_node.node.data.plant_id
		        this.moduleSave.parent = this.module_node.node.data.id
		      }
		      this.moduleSave.project = this.projectInfo.id
		      const response = await this.$api.createModule(this.moduleSave)
		      if(response.status === 201){
		        this.editModuleVisible = false
		        this.getPlantModule()
		        ElMessage({message: "保存成功", type: 'success'})
		      }
		    }
		  })
		},
		
		async updateModule(){
		  this.$refs['moduleRef'].validate(async (valid, fields)=>{
		    if (valid){
		      this.moduleSave.project = this.module_node.node.data.project_id
		      this.moduleSave.plant = this.module_node.node.data.plant_id
		      const response = await this.$api.updateModule(this.moduleSave.id, this.moduleSave)
		      if(response.status === 200){
		        this.editModuleVisible = false
		        this.getPlantModule()
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
		
		async getPlantModule(){
		  const response = await this.$api.getAllPlantModule({project: this.projectInfo.id})
		  if (response.status === 200){
		    this.plant_module_list = response.data.results
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
		  this.getSteps()
		},
		
		filterNode(value, data) {
		  if (!value) return true
		  return data?.name?.includes(value) || false
		},
	
		handleCurrentChange(){
			this.getSteps()
		},
		handleSizeChange(){
			this.page_size_params.page = 1
			this.getSteps()
		},
		search(){
			this.page_size_params.page = 1
			this.getSteps()
		},
		reset(){
			for(let key in this.stepSearch){
				if(key === 'module_list'){
				  continue
				}
				this.stepSearch[key] = ''
			}
			this.page_size_params.page = 1
			this.getSteps()
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
		
		moduleSelect(node){
		  if (!node) {
		    this.selectNode = null
		    this.stepSearch.module_list = []
		    this.getCases()
		    this.getSteps()
		    return
		  }
		  // 如果点击的是已选中的节点，取消选中
		  if (this.selectNode === node.id) {
		    this.$refs.treeRef?.setCurrentKey(null)
		    this.selectNode = null
		    this.stepSearch.module_list = []
		    localStorage.removeItem('case_node')
		    this.getCases()
		    this.getSteps()
		    return
		  }
		  localStorage.setItem('case_node', JSON.stringify(node))
		  this.selectNode = node.id
		  if (this.includeChildren) {
		    this.stepSearch.module_list = this.getAllIds(node)
		  } else {
		    this.stepSearch.module_list = [node.id]
		  }
		  this.getCases()
		  this.getSteps()
		},
		
		onIncludeChildrenChange() {
		  const node = this.$refs.treeRef?.getCurrentNode()
		  if (node) {
		    if (this.includeChildren) {
		      this.stepSearch.module_list = this.getAllIds(node)
		    } else {
		      this.stepSearch.module_list = [node.id]
		    }
		    this.getCases()
		    this.getSteps()
		  }
		},
		
		editStep(row_data){
			this.$router.push({path: '/test/stepEdit', query: {id: row_data.id}})
		},
		chooseStepData(data){
			this.$emit('update:chooseStepVisible', false)
			this.$emit('setStepData', data)
		},
		chooseComStepData(data){
			this.$emit('update:chooseComStepVisible', false)
			this.$emit('setComStepData', data)
		},
		chooseManyComStepData(){
			this.$emit('update:chooseComStepVisible', false)
			this.$emit('setManyComStepData', this.multipleSelection)
		},
		chooseManyStepData(){
			this.$emit('update:chooseStepVisible', false)
			this.$emit('setManyStepData', this.multipleSelection)
		},
		async  check_permission(){
		     if (this.parentPermission){
              this.permission = this.parentPermission
            }else{
              const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission['/common/step']}
              const response = await this.$api.check_permission(params)
              if (response.status === 200){
                    this.permission = { ...response.data.result }
              }
            }
	 	},
		async getSteps(){
			this.stepSearch.project = this.projectInfo.id
			const data = Object.assign(this.stepSearch, this.page_size_params, this.sort_params)
			this.stepSearch.module = (this.stepSearch.module_list || []).join(',')
			const response = await this.$api.getSteps(data)
			if (response.status === 200){
				this.step_list = {...response.data}
			}
		},
	},
	created() {
		this.check_permission()
		const node = JSON.parse(localStorage.getItem('case_node'))
		if (node) {
		  this.$nextTick(() => {
		    if (this.$refs.treeRef) {
		      this.$refs.treeRef.setCurrentKey(node.id)
		    }
		  })
		  this.stepSearch.module_list = this.getAllIds(node)
		}
		this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
		this.getCases()
		this.getSteps()
		this.getPlantModule()
	}
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

/* 修复：节点名称过长时设置按钮被隐藏的问题 */
.custom-tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
  min-width: 0; /* 添加最小宽度为0，允许flex子元素收缩 */
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

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  color: var(--qm-text-2);
  min-width: 0; /* 允许文本区域收缩 */
}

.node-actions {
  flex-shrink: 0; /* 防止操作按钮被挤压 */
  opacity: 0;
  transition: opacity 0.3s ease;
  margin-left: 8px; /* 添加左边距，确保与文本有间隔 */
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

.inline-form-item {
  margin-bottom: 0;
    display: flex;
    flex-direction: row;
    align-items: center;
    height: 40px;
}

.inline-label-wrapper {
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

.inline-form-item :deep(.el-form-item__content) {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  flex-wrap: nowrap !important;
  margin-left: 0 !important;
  width: 100%;
}

.step-container {
	width: 100%;
	background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
	
	box-sizing: border-box;
	display: flex;
	flex-direction: column;
	gap: 20px;
	min-height: calc(100vh - 110px);
	max-height: calc(100vh - 110px);
	height: calc(100vh - 110px);
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

.inline-form {
	margin-bottom: 0;
}

/* 水平布局的表单项 */
.form-item-horizontal {
	margin-bottom: 25px;
	  display: flex;
	  flex-direction: row;
	  align-items: center;
	  height: 40px;
	}
	
.form-item-horizontal :deep(.el-form-item__content) {
	  display: flex !important;
	  flex-direction: row !important;
	  align-items: center !important;
	  flex-wrap: nowrap !important;
	  margin-left: 0 !important;
	  width: 100%;
}

.horizontal-label {
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

.horizontal-label .icon-step-type,
.inline-label-wrapper .icon-step-type,
.horizontal-label .icon-step-name,
.inline-label-wrapper .icon-step-name,
.horizontal-label .icon-case,
.inline-label-wrapper .icon-case,
.horizontal-label .icon-creator,
.inline-label-wrapper .icon-creator,
.horizontal-label .icon-updater,
.inline-label-wrapper .icon-updater {
	width: 16px;
	height: 16px;
	display: inline-block;
	flex-shrink: 0;
	border-radius: 4px;
}

.horizontal-label .icon-step-type,
.inline-label-wrapper .icon-step-type { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); }

.horizontal-label .icon-step-name,
.inline-label-wrapper .icon-step-name { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }

.horizontal-label .icon-case,
.inline-label-wrapper .icon-case { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }

.horizontal-label .icon-creator,
.inline-label-wrapper .icon-creator { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }

.horizontal-label .icon-updater,
.inline-label-wrapper .icon-updater { background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); }

/* 输入框和下拉框样式 */
.input-elegant, .select-elegant {
	flex: 1;
	min-width: 0;
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

/* 序号单元格 */
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

/* 步骤名称单元格 */
.step-name-cell {
	display: flex;
	align-items: center;
	justify-content: center;
}

.step-desc {
	font-weight: 500;
	color: var(--qm-text-1);
	line-height: 1.4;
}

/* 步骤类型标签 */
.step-type-tags {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
	align-items: center;
}

.step-tag {
	border: none;
	font-weight: 500;
	padding: 4px 10px;
	border-radius: 20px;
	cursor: default;
	user-select: none;
}

.step-tag.clickable {
	cursor: pointer;
	transition: all 0.3s ease;
}

.step-tag.clickable:hover {
	opacity: 0.9;
	transform: translateY(-1px);
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

/* 时间单元格 */
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


/* 操作按钮 */
.action-buttons {
	display: flex;
	align-items: center;
	justify-content: center;
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

.action-btn.choose-btn {
	background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.action-btn.choose-btn:hover {
	box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.action-btn:active {
	transform: translateY(0) scale(0.95);
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

/* 响应式设计 */
@media screen and (max-width: 1200px) {
	.step-container {
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
	.step-container {
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