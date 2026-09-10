<template>
  <div class="environment-management-container">
	  
	<el-card class="drawer-card elegant-shadow">
	  <el-tabs v-model="activeName" class="drawer-tabs" @tab-click="handleClick">
	    <el-tab-pane label="环境列表" name="env" lazy='true'>
			<el-card class="filter-card elegant-shadow">
			  <div class="filter-header">
			    <div class="header-title-section">
			      <i class="icon-search"></i>
			      <h3 class="filter-title">环境列表筛选</h3>
			      <el-tag size="small" type="info" effect="plain">模糊查询</el-tag>
			    </div>
			    <div class="header-action-section">
			      <el-button class="reset-btn" @click="reset">
			        <el-icon><Refresh /></el-icon>重置
			      </el-button>
			      <el-button type="primary" @click="searchEnv" class="search-btn">
			        <el-icon><Search /></el-icon>查询
			      </el-button>
			    </div>
			  </div>
			  
			  <!-- 动态筛选表单 -->
			  <div class="filter-form-wrapper">
			    <!-- 环境列表筛选 -->
			    <el-form  :model="envSearch" class="filter-form inline-form">
			      <el-row :gutter="24">
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-user"></i>
			              <span class='label-text'>环境名称</span>
			            </div>
						<el-input
						  v-model="envSearch.name" 
						  placeholder="请输入环境名称" 
						  clearable
						  class="input"
						  size='large'
						/>
			          </el-form-item>
			        </el-col>
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-creator"></i>
			              <span class='label-text'>创建人</span>
			            </div>
			            <el-select 
			              v-model="envSearch.create_by" 
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
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-updater"></i>
			              <span class='label-text'>更新人</span>
			            </div>
			            <el-select 
			              v-model="envSearch.update_by" 
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
			  <!-- 内容标题区域 -->
			  <div class="content-header">
			    <div class="content-title-section">
			      <div class="title-with-stats">
			        <h3 class="content-title">环境列表</h3>
			        <div class="stats-info">
			          <div class="stat-item">
			            <span class="stat-label">总计</span>
			            <span class="stat-value">{{ env_list.count }}</span>
			          </div>
			          <div class="stat-item">
			            <span class="stat-label">当前页</span>
			            <span class="stat-value">{{ page_size_params.page }}</span>
			          </div>
			        </div>
			      </div>
			      
			      <!-- 新增按钮区域 -->
			      <div class="action-buttons-section">
			        <el-button 
			          v-if="permission.has_add_permission" 
			          @click="addEnv" 
			          type="primary" 
			          class="add-btn"
			        >
			          <el-icon><Plus /></el-icon>新增环境
			        </el-button>
			      </div>
			    </div>
			  </div>
			  
			  <!-- 动态内容区域 -->
			  <div class="table-section">
			    <div class="table-wrapper">
			      <!-- 环境列表表格 -->
			      <div >
			        <el-table 
			          :data="env_list.results" 
			          :max-height="'calc(100vh - 550px)'" 
			          class="elegant-table"
			          :header-row-style="headerRowStyle"
			          :show-overflow-tooltip="true"
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
			            label="环境名称" 
			            prop="name" 
			            min-width="150" 
			            align="center"
			            class-name="env-column"
			          >
			            <template #default="scope">
			              <div class="env-cell">
			                <div class="env-icon">
			                  <el-icon>
			                    <Environment />
			                  </el-icon>
			                </div>
			                <div class="env-info">
			                  <span class="env-name">{{ scope.row.name }}</span>
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
			                  content="查看环境" 
			                  placement="top" 
			                  effect="dark"
			                >
			                  <el-button 
			                    type="success" 
			                    v-if="permission.has_read_permission" 
			                    class="action-btn view-btn"
			                    @click.stop="viewEnv(scope.row)"
			                    circle
			                  >
			                    <el-icon><View /></el-icon>
			                  </el-button>
			                </el-tooltip>
			                
			                <el-tooltip 
			                  content="编辑环境" 
			                  placement="top" 
			                  effect="dark"
			                >
			                  <el-button 
			                    type="warning" 
			                    v-if="permission.has_edit_permission" 
			                    class="action-btn edit-btn"
			                    @click.stop="editEnv(scope.row)"
			                    circle
			                  >
			                    <el-icon><EditPen /></el-icon>
			                  </el-button>
			                </el-tooltip>
			                
			                <el-tooltip 
			                  content="删除环境" 
			                  placement="top" 
			                  effect="dark"
			                >
			                  <el-button 
			                    type="danger" 
			                    v-if="permission.has_delete_permission" 
			                    @click.stop="deleteEnv(scope.row.id)" 
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
			        
			        <!-- 分页组件 -->
			        <div class="pagination-wrapper">
			          <el-pagination
			            v-model:current-page="page_size_params.page"
			            v-model:page-size="page_size_params.size"
			            :page-sizes="[10, 20, 30, 50]"
			            layout="total, sizes, prev, pager, next, jumper"
			            :total="env_list.count"
			            @size-change="handleSizeChange"
			            @current-change="handleCurrentChange"
			            class="select input"
			            :background="true"
			          />
			        </div>
			    </div>
			  </div>
			</div>
			</el-card>
		</el-tab-pane>
		<el-tab-pane label="全局变量配置" name="global_params" lazy='true'>
			<el-card class="filter-card elegant-shadow">
			  <div class="filter-header">
			    <div class="header-title-section">
			      <i class="icon-search"></i>
			      <h3 class="filter-title">全局变量筛选</h3>
			      <el-tag size="small" type="info" effect="plain">模糊查询</el-tag>
			    </div>
			    <div class="header-action-section">
			      <el-button class="reset-btn" @click="resetGlobalParams()">
			        <el-icon><Refresh /></el-icon>重置
			      </el-button>
			      <el-button type="primary" @click="searchGlobalParams" class="search-btn">
			        <el-icon><Search /></el-icon>查询
			      </el-button>
			    </div>
			  </div>
			  
			  <!-- 动态筛选表单 -->
			  <div class="filter-form-wrapper">
			    <!-- 环境变量筛选 -->
			    <el-form  :model="paramsSearch" class="filter-form">
			      <el-row :gutter="24">
					  
					<el-col :xs="24" :sm="12" :md="8" :lg="6">
					  <el-form-item class="form-item-enhanced">
					    <div class="label-with-icon">
					      <i class="icon-user"></i>
					      <span>变量名称</span>
					    </div>
					    <el-input 
					      v-model="paramsGlobalSearch.name"
					      placeholder="请输入变量名称" 
					      clearable
					      class="input"
					      size='large'
					    />
					  </el-form-item>
					</el-col>
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-creator"></i>
			              <span>创建人</span>
			            </div>
			            <el-select 
			              v-model="paramsGlobalSearch.create_by"
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
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-updater"></i>
			              <span>更新人</span>
			            </div>
			            <el-select 
			              v-model="paramsGlobalSearch.update_by"
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
			  <!-- 内容标题区域 -->
			  <div class="content-header">
			    <div class="content-title-section">
			      <div class="title-with-stats">
			        <h3 class="content-title">全局变量配置</h3>
			        <div class="stats-info">
			          <div class="stat-item">
			            <span class="stat-label">总计</span>
			            <span class="stat-value">{{ global_params_list.count }}</span>
			          </div>
			          <div class="stat-item">
			            <span class="stat-label">当前页</span>
			            <span class="stat-value">{{ page_size_params.page }}</span>
			          </div>
			        </div>
			      </div>
			      
			      <!-- 新增按钮区域 -->
			      <div class="action-buttons-section">
			        <el-button 
			          v-if="permission.has_add_permission" 
			          @click="addGlobalParams"
			          type="primary" 
			          class="add-btn"
			        >
			          <el-icon><Plus /></el-icon>新增全局变量
			        </el-button>
			      </div>
			    </div>
			  </div>
			  
			  <div class="table-section">
			    <div class="table-wrapper">
			      <!-- 环境变量表格 -->
			      <div>
			        <el-table 
			          :data="global_params_list.results"
			          :max-height="'calc(100vh - 550px)'" 
			          class="elegant-table"
			          :header-row-style="headerRowStyle"
			          :show-overflow-tooltip="true"
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
					    label="变量名称" 
					    prop="name" 
					    width="150" 
					    align="center"
					    class-name="variable-column"
					  >
					    <template #default="scope">
					      <el-tag size="small" type="primary" effect="light">
					        {{ scope.row.name }}
					      </el-tag>
					    </template>
					  </el-table-column>
			          
			          <el-table-column 
			            label="变量值" 
			            prop="value" 
			            width="200" 
			            align="center"
			            class-name="value-column"
			          >
			            <template #default="scope">
			              <div class="value-cell">
			                <i class="icon-value"></i>
			                <span class="value-text">{{ scope.row.value }}</span>
			              </div>
			            </template>
			          </el-table-column>
			          
			          <el-table-column 
			            label="变量备注" 
			            prop="remark" 
			            min-width="150" 
			            align="center"
			            class-name="remark-column"
			          />
			          
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
			                  content="查看环境变量" 
			                  placement="top" 
			                  effect="dark"
			                >
			                  <el-button 
			                    type="success" 
			                    v-if="permission.has_read_permission" 
			                    class="action-btn view-btn"
			                    @click.stop="viewGlobalParams(scope.row)"
			                    circle
			                  >
			                    <el-icon><View /></el-icon>
			                  </el-button>
			                </el-tooltip>
			                
			                <el-tooltip 
			                  content="编辑环境变量" 
			                  placement="top" 
			                  effect="dark"
			                >
			                  <el-button 
			                    type="warning" 
			                    v-if="permission.has_edit_permission" 
			                    class="action-btn edit-btn"
			                    @click.stop="editGlobalParams(scope.row)"
			                    circle
			                  >
			                    <el-icon><EditPen /></el-icon>
			                  </el-button>
			                </el-tooltip>
			                
			                <el-tooltip 
			                  content="删除环境变量" 
			                  placement="top" 
			                  effect="dark"
			                >
			                  <el-button 
			                    type="danger" 
			                    v-if="permission.has_delete_permission" 
			                    @click.stop="deleteGlobalParams(scope.row.id)"
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
			        
			        <!-- 分页组件 -->
			        <div class="pagination-wrapper">
			          <el-pagination
			            v-model:current-page="page_size_params.page"
			            v-model:page-size="page_size_params.size"
			            :page-sizes="[10, 20, 30, 50]"
			            layout="total, sizes, prev, pager, next, jumper"
			            :total="global_params_list.count"
			            @size-change="handleSizeGlobalParamsChange"
			            @current-change="handleCurrentGlobalParamsChange"
			            class="select input"
			            :background="true"
			          />
			        </div>
			      </div>
				</div>
				</div>
			</el-card>
		</el-tab-pane>
		<el-tab-pane label="环境变量配置" name="params" lazy='true'>
			<el-card class="filter-card elegant-shadow">
			  <div class="filter-header">
			    <div class="header-title-section">
			      <i class="icon-search"></i>
			      <h3 class="filter-title">环境变量筛选</h3>
			      <el-tag size="small" type="info" effect="plain">模糊查询</el-tag>
			    </div>
			    <div class="header-action-section">
			      <el-button class="reset-btn" @click="resetParams()">
			        <el-icon><Refresh /></el-icon>重置
			      </el-button>
			      <el-button type="primary" @click="searchParams" class="search-btn">
			        <el-icon><Search /></el-icon>查询
			      </el-button>
			    </div>
			  </div>

			  <!-- 动态筛选表单 -->
			  <div class="filter-form-wrapper">
			    <!-- 环境变量筛选 -->
			    <el-form  :model="paramsSearch" class="filter-form">
			      <el-row :gutter="24">

					<el-col :xs="24" :sm="12" :md="8" :lg="6">
					  <el-form-item class="form-item-enhanced">
					    <div class="label-with-icon">
					      <i class="icon-user"></i>
					      <span>变量名称</span>
					    </div>
					    <el-input
					      v-model="paramsSearch.name"
					      placeholder="请输入变量名称"
					      clearable
					      class="input"
					      size='large'
					    />
					  </el-form-item>
					</el-col>

			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-role"></i>
			              <span>环境名称</span>
			            </div>
			            <el-select
			              v-model="paramsSearch.env"
			              placeholder="请选择环境名称"
			              clearable
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

			       <!-- <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-remark"></i>
			              <span>变量备注</span>
			            </div>
			            <el-input
			              v-model="paramsSearch.remark"
			              placeholder="请输入变量备注"
			              clearable
			              class="input"
			              size='large'
			            />
			          </el-form-item>
			        </el-col>
			        -->
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-creator"></i>
			              <span>创建人</span>
			            </div>
			            <el-select
			              v-model="paramsSearch.create_by"
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

			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-updater"></i>
			              <span>更新人</span>
			            </div>
			            <el-select
			              v-model="paramsSearch.update_by"
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
			  <!-- 内容标题区域 -->
			  <div class="content-header">
			    <div class="content-title-section">
			      <div class="title-with-stats">
			        <h3 class="content-title">环境变量配置</h3>
			        <div class="stats-info">
			          <div class="stat-item">
			            <span class="stat-label">总计</span>
			            <span class="stat-value">{{ params_list.count }}</span>
			          </div>
			          <div class="stat-item">
			            <span class="stat-label">当前页</span>
			            <span class="stat-value">{{ page_size_params.page }}</span>
			          </div>
			        </div>
			      </div>

			      <!-- 新增按钮区域 -->
			      <div class="action-buttons-section">
			        <el-button
			          v-if="permission.has_add_permission"
			          @click="addParams"
			          type="primary"
			          class="add-btn"
			        >
			          <el-icon><Plus /></el-icon>新增环境变量
			        </el-button>
			      </div>
			    </div>
			  </div>

			  <div class="table-section">
			    <div class="table-wrapper">
			      <!-- 环境变量表格 -->
			      <div>
			        <el-table
			          :data="params_list.results"
			          :max-height="'calc(100vh - 550px)'"
			          class="elegant-table"
			          :header-row-style="headerRowStyle"
			          :show-overflow-tooltip="true"
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
					    label="变量名称"
					    prop="name"
					    width="150"
					    align="center"
					    class-name="variable-column"
					  >
					    <template #default="scope">
					      <el-tag size="small" type="primary" effect="light">
					        {{ scope.row.name }}
					      </el-tag>
					    </template>
					  </el-table-column>

			          <el-table-column
			            label="变量值"
			            prop="value"
			            width="200"
			            align="center"
			            class-name="value-column"
			          >
			            <template #default="scope">
			              <div class="value-cell">
			                <i class="icon-value"></i>
			                <span class="value-text">{{ scope.row.value }}</span>
			              </div>
			            </template>
			          </el-table-column>

			          <el-table-column
			            label="变量备注"
			            prop="remark"
			            min-width="150"
			            align="center"
			            class-name="remark-column"
			          />

					  <el-table-column
					    label="所属环境"
					    prop="env_name"
					    width="150"
					    align="center"
					    class-name="env-column"
					  >
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
			                  content="查看环境变量"
			                  placement="top"
			                  effect="dark"
			                >
			                  <el-button
			                    type="success"
			                    v-if="permission.has_read_permission"
			                    class="action-btn view-btn"
			                    @click.stop="viewParams(scope.row)"
			                    circle
			                  >
			                    <el-icon><View /></el-icon>
			                  </el-button>
			                </el-tooltip>

			                <el-tooltip
			                  content="编辑环境变量"
			                  placement="top"
			                  effect="dark"
			                >
			                  <el-button
			                    type="warning"
			                    v-if="permission.has_edit_permission"
			                    class="action-btn edit-btn"
			                    @click.stop="editParams(scope.row)"
			                    circle
			                  >
			                    <el-icon><EditPen /></el-icon>
			                  </el-button>
			                </el-tooltip>

			                <el-tooltip
			                  content="删除环境变量"
			                  placement="top"
			                  effect="dark"
			                >
			                  <el-button
			                    type="danger"
			                    v-if="permission.has_delete_permission"
			                    @click.stop="deleteParams(scope.row.id)"
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

			        <!-- 分页组件 -->
			        <div class="pagination-wrapper">
			          <el-pagination
			            v-model:current-page="page_size_params.page"
			            v-model:page-size="page_size_params.size"
			            :page-sizes="[10, 20, 30, 50]"
			            layout="total, sizes, prev, pager, next, jumper"
			            :total="params_list.count"
			            @size-change="handleSizeParamsChange"
			            @current-change="handleCurrentParamsChange"
			            class="select input"
			            :background="true"
			          />
			        </div>
			      </div>
				</div>
				</div>
			</el-card>
		</el-tab-pane>
		<el-tab-pane label="浏览器集群配置" name="web" lazy='true'>
			<el-card class="filter-card elegant-shadow">
			  <div class="filter-header">
			    <div class="header-title-section">
			      <i class="icon-search"></i>
			      <h3 class="filter-title">浏览器集群配置筛选</h3>
			      <el-tag size="small" type="info" effect="plain">模糊查询</el-tag>
			    </div>
			    <div class="header-action-section">
			      <el-button class="reset-btn" @click="resetExecutor()">
			        <el-icon><Refresh /></el-icon>重置
			      </el-button>
			      <el-button type="primary" @click="searchExecutor" class="search-btn">
			        <el-icon><Search /></el-icon>查询
			      </el-button>
			    </div>
			  </div>
			  <!-- 动态筛选表单 -->
			  <div class="filter-form-wrapper">
			  
			    <!-- Web执行机筛选 -->
			    <el-form  :model="webExecutorSearch" class="filter-form">
			      <el-row :gutter="24">
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-user"></i>
			              <span class='label-text'>集群名称</span>
			            </div>
			            <el-input 
			              v-model="webExecutorSearch.name" 
			              placeholder="请输入执行机名称" 
			              clearable
			              class="input"
			              size='large'
			            />
			          </el-form-item>
			        </el-col>
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-email"></i>
			              <span class='label-text'>集群类型</span>
			            </div>
			            <el-select 
			              v-model="webExecutorSearch.type" 
			              placeholder="请选择浏览器集群类型" 
			              clearable
			              class="select"
			              size='large'
			              popper-class='select-dropdown-rounded'
			            >
			              <el-option label="StandAlone" value="1" />
			              <el-option label="Hub" value="2" />
			              <el-option label="Node" value="3" />
			            </el-select>
			          </el-form-item>
			        </el-col>
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-role"></i>
			              <span class='label-text'>集群状态</span>
			            </div>
			            <el-select 
			              v-model="webExecutorSearch.status" 
			              placeholder="请选择浏览器集群状态" 
			              clearable
			              class="select"
			              size='large'
			              popper-class='select-dropdown-rounded'
			            >
			              <el-option label="启用" :value="1" />
			              <el-option label="禁用" :value="2" />
			            </el-select>
			          </el-form-item>
			        </el-col>
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-creator"></i>
			              <span class='label-text'>创建人</span>
			            </div>
			            <el-select 
			              v-model="webExecutorSearch.create_by" 
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
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-updater"></i>
			              <span class='label-text'>更新人</span>
			            </div>
			            <el-select 
			              v-model="webExecutorSearch.update_by" 
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
			  <!-- 内容标题区域 -->
			  <div class="content-header">
			    <div class="content-title-section">
			      <div class="title-with-stats">
			        <h3 class="content-title">浏览器集群配置</h3>
			        <div class="stats-info">
			          <div class="stat-item">
			            <span class="stat-label">总计</span>
			            <span class="stat-value">{{ web_executor_list.count }}</span>
			          </div>
			          <div class="stat-item">
			            <span class="stat-label">当前页</span>
			            <span class="stat-value">{{ page_size_params.page }}</span>
			          </div>
			        </div>
			      </div>
			      
			      <!-- 新增按钮区域 -->
			      <div class="action-buttons-section">			        
			        <el-button 
			          v-if="permission.has_add_permission" 
			          @click="addExecutor" 
			          type="primary" 
			          class="add-btn"
			        >
			          <el-icon><Plus /></el-icon>新增浏览器集群
			        </el-button>
			        
			      </div>
			    </div>
			  </div>
			  
			  <!-- 动态内容区域 -->
			  <div class="table-section">
			    <div class="table-wrapper">
			  
			      <!-- Web执行机表格 -->
			      <div >
			        <el-table 
			          :data="web_executor_list.results" 
			          :max-height="'calc(100vh - 605px)'" 
			          class="elegant-table"
			          :header-row-style="headerRowStyle"
			          :show-overflow-tooltip="true"
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
			            label="执行机名称" 
			            prop="name" 
			            width="200" 
			            align="center"
			            class-name="executor-column"
			          >
			            <template #default="scope">
			              <div class="executor-cell">
			                <div class="executor-icon">
			                  <el-icon>
			                    <Monitor />
			                  </el-icon>
			                </div>
			                <span class="executor-name">{{ scope.row.name }}</span>
			              </div>
			            </template>
			          </el-table-column>
			          
			          <el-table-column 
			            label="执行机类型" 
			            prop="type" 
			            width="150" 
			            align="center"
			            class-name="type-column"
			          >
			            <template #default="scope">
			              <el-tag 
			                :type="scope.row.type === 1 ? 'success' : scope.row.type === 2 ? 'primary' : 'info'"
			                effect="light"
			                class="type-tag"
			              >
			                {{ scope.row.type === 1 ? 'StandAlone' : scope.row.type === 2 ? 'Hub' : 'Node' }}
			              </el-tag>
			            </template>
			          </el-table-column>
			          
			          <el-table-column 
			            label="执行机地址" 
			            prop="url" 
			            min-width="200" 
			            align="center"
			            class-name="url-column"
			          >
			            <template #default="scope">
			              <div class="url-cell">
			                <el-link 
			                  :href="scope.row.url" 
			                  target="_blank"
			                  type="primary"
			                  class="url-link"
			                >
			                  <i class="icon-link"></i>
			                  {{ scope.row.url }}
			                </el-link>
			              </div>
			            </template>
			          </el-table-column>
			          
			          <el-table-column 
			            label="VNC地址" 
			            prop="vnc_url" 
			            min-width="200" 
			            align="center"
			            class-name="url-column"
			          >
			            <template #default="scope">
			              <div class="url-cell">
			                <el-link 
			                  :href="scope.row.vnc_url" 
			                  target="_blank"
			                  type="success"
			                  class="url-link"
			                >
			                  <i class="icon-vnc"></i>
			                  {{ scope.row.vnc_url }}
			                </el-link>
			              </div>
			            </template>
			          </el-table-column>
			          
			          <el-table-column 
			            label="状态" 
			            prop="status_name" 
			            width="100" 
			            align="center"
			            class-name="status-column"
			          >
			            <template #default="scope">
			              <el-tag 
			                :type="scope.row.status === 1 ? 'success' : 'danger'"
			                effect="light"
			                class="status-tag"
			              >
			                {{ scope.row.status === 1 ? '启用' : '禁用' }}
			              </el-tag>
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
			                  content="查看执行机" 
			                  placement="top" 
			                  effect="dark"
			                >
			                  <el-button 
			                    type="success" 
			                    v-if="permission.has_read_permission" 
			                    class="action-btn view-btn"
			                    @click.stop="viewExecutor(scope.row)"
			                    circle
			                  >
			                    <el-icon><View /></el-icon>
			                  </el-button>
			                </el-tooltip>
			                
			                <el-tooltip 
			                  content="编辑执行机" 
			                  placement="top" 
			                  effect="dark"
			                >
			                  <el-button 
			                    type="warning" 
			                    v-if="permission.has_edit_permission" 
			                    class="action-btn edit-btn"
			                    @click.stop="editExecutor(scope.row)"
			                    circle
			                  >
			                    <el-icon><EditPen /></el-icon>
			                  </el-button>
			                </el-tooltip>
			                
			                <el-tooltip 
			                  content="删除执行机" 
			                  placement="top" 
			                  effect="dark"
			                >
			                  <el-button 
			                    type="danger" 
			                    v-if="permission.has_delete_permission" 
			                    @click.stop="deleteWebExecutor(scope.row.id)" 
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
			        
			        <!-- 分页组件 -->
			        <div class="pagination-wrapper">
			          <el-pagination
			            v-model:current-page="page_size_params.page"
			            v-model:page-size="page_size_params.size"
			            :page-sizes="[10, 20, 30, 50]"
			            layout="total, sizes, prev, pager, next, jumper"
			            :total="web_executor_list.count"
			            @size-change="handleSizeWebChange"
			            @current-change="handleCurrentWebChange"
			            class="select input"
			            :background="true"
			          />
			        </div>
			      </div>
			  </div>
			  </div>
			</el-card>
		</el-tab-pane>
		<el-tab-pane label="手机设备配置" name="app" lazy='true'>
			<el-card class="filter-card elegant-shadow">
			  <div class="filter-header">
			    <div class="header-title-section">
			      <i class="icon-search"></i>
			      <h3 class="filter-title">手机设备筛选</h3>
			      <el-tag size="small" type="info" effect="plain">模糊查询</el-tag>
			    </div>
			    <div class="header-action-section">
			      <el-button class="reset-btn" @click="resetAppExecutor()">
			        <el-icon><Refresh /></el-icon>重置
			      </el-button>
			      <el-button type="primary" @click="searchAppExecutor" class="search-btn">
			        <el-icon><Search /></el-icon>查询
			      </el-button>
			    </div>
			  </div>
			  <!-- 动态筛选表单 -->
			  <div class="filter-form-wrapper">
			    <!-- App执行机筛选 -->
			    <el-form  :model="appExecutorSearch" class="filter-form">
			      <el-row :gutter="24">
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-user"></i>
			              <span>设备名称</span>
			            </div>
			            <el-input 
			              v-model="appExecutorSearch.device_name" 
			              placeholder="请输入设备名称" 
			              clearable
			              class="input"
						  size='large'
			            />
			          </el-form-item>
			        </el-col>
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-role"></i>
			              <span>设备类型</span>
			            </div>
			            <el-select 
			              v-model="appExecutorSearch.platform_name" 
			              placeholder="请选择设备类型" 
			              clearable
			              class="select"
			              size='large'
			              popper-class='select-dropdown-rounded'
			            >
			              <el-option label="Android" value="1" />
			              <el-option label="iOS" value="2" />
			            </el-select>
			          </el-form-item>
			        </el-col>
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-email"></i>
			              <span>设备状态</span>
			            </div>
			            <el-select 
			              v-model="appExecutorSearch.status" 
			              placeholder="请选择" 
			              clearable
			              class="select"
			              size='large'
			              popper-class='select-dropdown-rounded'
			            >
			              <el-option label="启用" :value="1" />
			              <el-option label="禁用" :value="2" />
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
			              v-model="appExecutorSearch.create_by" 
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
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-enhanced">
			            <div class="label-with-icon">
			              <i class="icon-updater"></i>
			              <span>更新人</span>
			            </div>
			            <el-select 
			              v-model="appExecutorSearch.update_by" 
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
			  <!-- 内容标题区域 -->
			  <div class="content-header">
			    <div class="content-title-section">
			      <div class="title-with-stats">
			        <h3 class="content-title">手机设备配置</h3>
			        <div class="stats-info">
			          <div class="stat-item">
			            <span class="stat-label">总计</span>
			            <span class="stat-value">{{ app_executor_list.count }}</span>
			          </div>
			          <div class="stat-item">
			            <span class="stat-label">当前页</span>
			            <span class="stat-value">{{ page_size_params.page }}</span>
			          </div>
			        </div>
			      </div>
			      
			      <!-- 新增按钮区域 -->
			      <div class="action-buttons-section">
			        <el-button 
			          v-if="permission.has_add_permission" 
			          @click="addAppExecutor" 
			          type="primary" 
			          class="add-btn"
			        >
			          <el-icon><Plus /></el-icon>新增手机设备
			        </el-button>
			      </div>
			    </div>
			  </div>
			  
			  <!-- 动态内容区域 -->
			  <div class="table-section">
			    <div class="table-wrapper">
			  
			      <!-- App执行机表格 -->
			      <div >
			        <el-table 
			          :data="app_executor_list.results" 
			          :max-height="'calc(100vh - 605px)'" 
			          class="elegant-table"
			          :header-row-style="headerRowStyle"
			          :show-overflow-tooltip="true"
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
			            label="设备名称" 
			            prop="device_name" 
			            width="150" 
			            align="center"
			            class-name="device-column"
			          >
			            <template #default="scope">
			              <div class="device-cell">
			                <div class="device-icon">
			                  <el-icon>
			                    <Phone />
			                  </el-icon>
			                </div>
			                <span class="device-name">{{ scope.row.device_name }}</span>
			              </div>
			            </template>
			          </el-table-column>
			          
			          <el-table-column 
			            label="设备类型" 
			            prop="platform_name" 
			            width="120" 
			            align="center"
			            class-name="platform-column"
			          >
			            <template #default="scope">
			              <el-tag 
			                :type="scope.row.platform_name === 1 ? 'success' : 'primary'"
			                effect="light"
			                class="platform-tag"
			              >
			                {{ scope.row.platform_name === 1 ? 'Android' : 'iOS' }}
			              </el-tag>
			            </template>
			          </el-table-column>
			          
			          <el-table-column 
			            label="设备版本号" 
			            prop="platform_version" 
			            width="120" 
			            align="center"
			            class-name="version-column"
			          />
			          
			          <el-table-column 
			            label="Hub地址" 
			            prop="hub_url" 
			            min-width="200" 
			            align="center"
			            class-name="url-column"
			          >
			            <template #default="scope">
			              <div class="url-cell">
			                <el-link 
			                  :href="scope.row.hub_url" 
			                  target="_blank"
			                  type="primary"
			                  class="url-link"
			                >
			                  <i class="icon-link"></i>
			                  {{ scope.row.hub_url }}
			                </el-link>
			              </div>
			            </template>
			          </el-table-column>
			          
			          <el-table-column 
			            label="Node地址" 
			            prop="node_url" 
			            min-width="200" 
			            align="center"
			            class-name="url-column"
			          >
			            <template #default="scope">
			              <div class="url-cell">
			                <el-link 
			                  :href="scope.row.node_url" 
			                  target="_blank"
			                  type="success"
			                  class="url-link"
			                >
			                  <i class="icon-node"></i>
			                  {{ scope.row.node_url }}
			                </el-link>
			              </div>
			            </template>
			          </el-table-column>
			          
			          <el-table-column 
			            label="状态" 
			            prop="status_name" 
			            width="100" 
			            align="center"
			            class-name="status-column"
			          >
			            <template #default="scope">
			              <el-tag 
			                :type="scope.row.status === 1 ? 'success' : 'danger'"
			                effect="light"
			                class="status-tag"
			              >
			                {{ scope.row.status === 1 ? '启用' : '禁用' }}
			              </el-tag>
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
			                  content="查看设备" 
			                  placement="top" 
			                  effect="dark"
			                >
			                  <el-button 
			                    type="success" 
			                    v-if="permission.has_read_permission" 
			                    class="action-btn view-btn"
			                    @click.stop="viewAppExecutor(scope.row)"
			                    circle
			                  >
			                    <el-icon><View /></el-icon>
			                  </el-button>
			                </el-tooltip>
			                
			                <el-tooltip 
			                  content="编辑设备" 
			                  placement="top" 
			                  effect="dark"
			                >
			                  <el-button 
			                    type="warning" 
			                    v-if="permission.has_read_permission" 
			                    class="action-btn edit-btn"
			                    @click.stop="editAppExecutor(scope.row)"
			                    circle
			                  >
			                    <el-icon><EditPen /></el-icon>
			                  </el-button>
			                </el-tooltip>
			                
			                <el-tooltip 
			                  content="删除设备" 
			                  placement="top" 
			                  effect="dark"
			                >
			                  <el-button 
			                    type="danger" 
			                    v-if="permission.has_read_permission" 
			                    @click.stop="deleteAppExecutor(scope.row.id)" 
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
			        
			        <!-- 分页组件 -->
			        <div class="pagination-wrapper">
			          <el-pagination
			            v-model:current-page="page_size_params.page"
			            v-model:page-size="page_size_params.size"
			            :page-sizes="[10, 20, 30, 50]"
			            layout="total, sizes, prev, pager, next, jumper"
			            :total="app_executor_list.count"
			            @size-change="handleSizeAppChange"
			            @current-change="handleCurrentAppChange"
			            class="select input"
			            :background="true"
			          />
			        </div>
			      </div>
			    </div>
			  </div>
			</el-card>
		</el-tab-pane>
	    <el-tab-pane label='全局请求头配置' name='header' lazy='true'>
			<Header></Header>
		</el-tab-pane>
		<el-tab-pane label='全局会话配置' name='cookie' lazy='true'>
			<Cookie></Cookie>
		</el-tab-pane>
	  </el-tabs>
	</el-card>

    <!-- 所有对话框 -->
    <!-- 环境表单对话框 -->
    <el-dialog 
      v-model="editEnvDialogVisible" 
      :title="title" 
      width="900"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form 
          :model="envSave" 
          :disabled="envView"
          :rules="envRules" 
          ref="envRef"
          class="dialog-form"
        >
          <el-form-item prop="name" class="form-item-enhanced">
            <div class="dialog-label-with-icon">
              <i class="icon-env-dialog"></i>
              <span class='label-text'>环境名称</span>
            </div>
            <el-input 
              v-model="envSave.name" 
              autocomplete="off" 
              placeholder="请输入环境名称"
              class="input"
              size='large'
			  maxlength="20"
			  show-word-limit
            />
          </el-form-item>
          
          <el-tabs v-model="active" class="drawer-tabs" style='margin-top: 20px;'>
            <el-tab-pane name="setup" lazy>
              <template #label>
                <span class="tab-label">
                  <i class="icon-setup"></i>
                  前置脚本
                </span>
                <el-tooltip placement="left" effect="light">
                  <template #content>
                    <ul class="tooltip-content">
                      <li>单个运行测试用例时不会执行</li>
                      <li>批量运行测试用例时会在所有用例执行前执行一次</li>
                    </ul>
                  </template>
                  <el-icon color="green" class="info-icon">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </template>
              <BodyEdit 
                :bind_case_data="[]" 
                v-model="envSave.setup" 
                lang="python" 
				:is-show-env="true"
                :is_function="false" 
                height="300px" 
                class="body-editor"
              />
            </el-tab-pane>
            
            <el-tab-pane name="teardown" lazy>
              <template #label>
                <span class="tab-label">
                  <i class="icon-teardown"></i>
                  后置脚本
                </span>
                <el-tooltip placement="left" effect="light">
                  <template #content>
                    <ul class="tooltip-content">
                      <li>单个运行测试用例时不会执行</li>
                      <li>批量运行测试用例时会在所有用例执行后执行一次</li>
                    </ul>
                  </template>
                  <el-icon color="green" class="info-icon">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </template>
              <BodyEdit 
                :bind_case_data="[]" 
                v-model="envSave.teardown" 
                lang="python" 
				:is-show-env="true"
                :is_function="false" 
                height="300px" 
                class="body-editor"
              />
            </el-tab-pane>
          </el-tabs>
        </el-form>
      </div>
      
      <div slot="footer" class="dialog-footer" v-if="!envView">
        <el-button @click="editEnvDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button 
          v-if="permission.has_edit_permission || permission.has_add_permission" 
          type="primary" 
          @click="save" 
          class="dialog-confirm-btn"
        >
          保存
        </el-button>
      </div>
    </el-dialog>

    <!-- 环境变量表单对话框 -->
    <el-dialog 
      v-model="editParamsDialogVisible" 
      :title="params_title" 
      width="600"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form 
          :model="paramsSave" 
          :disabled="envUrlView"
          :rules="envVarRules" 
          ref="envVarRef"
          class="dialog-form"
        >
          <el-form-item prop="env" class="dialog-form-item">
            <div class="label-with-icon">
              <i class="icon-email"></i>
              <span>环境名称</span>
            </div>
            <el-select 
              v-model="paramsSave.env" 
              placeholder="请选择环境"
              class="select"
              size='large'
              popper-class='select-dropdown-rounded'
            >
              <el-option 
                v-for="env_obj in env_list.results" 
                :key="env_obj.id"
                :label="env_obj.name" 
                :value="env_obj.id" 
                class="dialog-option"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item prop="name" class="dialog-form-item">
            <div class="label-with-icon">
              <i class="icon-user"></i>
              <span>变量名称</span>
            </div>
            <el-input 
              v-model="paramsSave.name" 
              autocomplete="off" 
              placeholder="请输入变量名称"
              class="input"
              size='large'
			  maxlength="30"
			  show-word-limit
            />
          </el-form-item>
          
          <el-form-item prop="value" class="dialog-form-item">
            <div class="dialog-label-with-icon">
              <i class="icon-user"></i>
              <span>变量值</span>
            </div>
            <el-input 
              v-model="paramsSave.value" 
              autocomplete="off" 
			  :autosize="{ minRows: 2, maxRows: 4 }"
			  type="textarea"
              placeholder="请输入变量值"
              class="text"
              size='large'
            />
          </el-form-item>
          
          <el-form-item prop="remark" class="dialog-form-item">
            <div class="label-with-icon">
              <i class="icon-creator"></i>
              <span>备注</span>
            </div>
            <el-input 
              v-model="paramsSave.remark" 
              autocomplete="off" 
              :autosize="{ minRows: 2, maxRows: 4 }"
              type="textarea" 
              placeholder="请输入备注说明"
              class="text"
              size='large'
			  maxlength="200"
			  show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      
      <div slot="footer" class="dialog-footer" v-if="!envUrlView">
        <el-button @click="editParamsDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button 
          v-if="permission.has_add_permission || permission.has_edit_permission" 
          type="primary" 
          @click="saveParams" 
          class="dialog-confirm-btn"
        >
          保存
        </el-button>
      </div>
    </el-dialog>

	<!-- 全局变量表单对话框 -->
    <el-dialog
      v-model="editGlobalParamsDialogVisible"
      :title="global_params_title"
      width="600"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form
          :model="paramsGlobalSave"
          :disabled="globalView"
          :rules="globalVarRules"
          ref="globalRef"
          class="dialog-form"
        >
          <el-form-item prop="name" class="dialog-form-item">
            <div class="label-with-icon">
              <i class="icon-user"></i>
              <span>变量名称</span>
            </div>
            <el-input
              v-model="paramsGlobalSave.name"
              autocomplete="off"
              placeholder="请输入变量名称"
              class="input"
              size='large'
			  maxlength="30"
			  show-word-limit
            />
          </el-form-item>

          <el-form-item prop="value" class="dialog-form-item">
            <div class="dialog-label-with-icon">
              <i class="icon-user"></i>
              <span>变量值</span>
            </div>
            <el-input
              v-model="paramsGlobalSave.value"
              autocomplete="off"
			  :autosize="{ minRows: 2, maxRows: 4 }"
			  type="textarea"
              placeholder="请输入变量值"
              class="text"
              size='large'
            />
          </el-form-item>

          <el-form-item prop="remark" class="dialog-form-item">
            <div class="label-with-icon">
              <i class="icon-creator"></i>
              <span>备注</span>
            </div>
            <el-input
              v-model="paramsGlobalSave.remark"
              autocomplete="off"
              :autosize="{ minRows: 2, maxRows: 4 }"
              type="textarea"
              placeholder="请输入备注说明"
              class="text"
              size='large'
			  maxlength="200"
			  show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>

      <div slot="footer" class="dialog-footer" v-if="!globalView">
        <el-button @click="editGlobalParamsDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button
          v-if="permission.has_add_permission || permission.has_edit_permission"
          type="primary"
          @click="saveGlobalParams"
          class="dialog-confirm-btn"
        >
          保存
        </el-button>
      </div>
    </el-dialog>

    <!-- Web执行机表单对话框 -->
    <el-dialog 
      v-model="editExecutorVisible" 
      :title="executorTitle" 
      width="600"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form 
          :model="executorSave" 
          :disabled="webExecuteView"
          :rules="webRules" 
          ref="webRef"
          class="dialog-form"
        >
          <el-form-item prop="type" class="dialog-form-item">
            <div class="label-with-icon">
              <i class="icon-updater"></i>
              <span>集群类型</span>
            </div>
            <el-select 
              v-model="executorSave.type" 
              placeholder="请选择浏览器集群类型"
              class="select"
              size='large'
              popper-class='select-dropdown-rounded'
            >
              <el-option label="StandAlone" :value="1" />
              <el-option label="Hub" :value="2" />
              <el-option label="Node" :value="3" />
            </el-select>
          </el-form-item>
          
          <el-form-item prop="status" class="dialog-form-item">
            <div class="label-with-icon">
              <i class="icon-role"></i>
              <span>集群状态</span>
            </div>
            <el-select 
              v-model="executorSave.status" 
              placeholder="请选择浏览器集群状态"
              class="select"
              size='large'
              popper-class='select-dropdown-rounded'
            >
              <el-option label="启用" :value="1" />
              <el-option label="禁用" :value="2" />
            </el-select>
          </el-form-item>
          
          <el-form-item prop="name" class="dialog-form-item">
            <div class="label-with-icon">
              <i class="icon-name"></i>
              <span>集群名称</span>
            </div>
            <el-input 
              v-model="executorSave.name" 
              autocomplete="off" 
              placeholder="请输入浏览器集群名称"
              class="input"
			  maxlength="30"
			  show-word-limit
              size='large'
            />
          </el-form-item>
          
          <el-form-item prop="url" class="dialog-form-item">
            <div class="label-with-icon">
              <i class="icon-creator"></i>
              <span>集群地址</span>
            </div>
            <el-input 
              v-model="executorSave.url" 
              autocomplete="off" 
              placeholder="请输入浏览器集群地址"
			  maxlength="100"
			  show-word-limit
              class="input"
              size='large'
            />
          </el-form-item>
          
          <el-form-item prop="vnc_url" class="dialog-form-item">
            <div class="label-with-icon">
              <i class="icon-user"></i>
              <span>集群VNC地址</span>
            </div>
            <el-input 
              v-model="executorSave.vnc_url" 
              autocomplete="off" 
              placeholder="请输入浏览器集群VNC地址"
			  maxlength="100"
			  show-word-limit
              class="input"
              size='large'
            />
          </el-form-item>
        </el-form>
      </div>
      
      <div slot="footer" class="dialog-footer" v-if="!webExecuteView">
        <el-button @click="editExecutorVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button 
          v-if="permission.has_add_permission || permission.has_edit_permission" 
          type="primary" 
          @click="saveExecutor" 
          class="dialog-confirm-btn"
        >
          保存
        </el-button>
      </div>
    </el-dialog>

    <!-- App执行机表单对话框 -->
    <el-dialog 
      v-model="editAppExecutorVisible" 
      :title="appExecutorTitle" 
      width="700"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form 
          :model="appExecutorSave" 
          :disabled="appExecuteView"
          :rules="appRules" 
          ref="appRef"
          class="dialog-form"
        >
          <el-form-item prop="platform_name"  class="form-item-inline">
            <div class="label-with-icon">
              <i class="icon-user"></i>
              <span>设备类型</span>
            </div>
            <el-select 
              v-model="appExecutorSave.platform_name" 
              placeholder="请选择APP设备类型"
              class="select"
              size='large'
              popper-class='select-dropdown-rounded'
            >
              <el-option label="Android" :value="1" />
              <el-option label="iOS" :value="2" />
            </el-select>
          </el-form-item>
          
          <el-form-item prop="status" class="form-item-inline">
            <div class="label-with-icon">
              <i class="icon-email"></i>
              <span>状态</span>
            </div>
            <el-select 
              v-model="appExecutorSave.status" 
              placeholder="请选择"
              class="select"
              size='large'
              popper-class='select-dropdown-rounded'
            >
              <el-option label="启用" :value="1" />
              <el-option label="禁用" :value="2" />
            </el-select>
          </el-form-item>
          
          <el-form-item prop="device_name" class="form-item-inline">
            <div class="label-with-icon">
              <i class="icon-role"></i>
              <span>设备名称</span>
            </div>
            <el-input 
              v-model="appExecutorSave.device_name" 
              autocomplete="off" 
              placeholder="请输入设备名称"
              class="input"
			  maxlength="50"
			  show-word-limit
              size='large'
            />
          </el-form-item>
          
          <el-form-item prop="platform_version" class="form-item-inline">
            <div class="label-with-icon">
              <i class="icon-user"></i>
              <span>版本号</span>
            </div>
            <el-input-number 
              v-model="appExecutorSave.platform_version" 
              autocomplete="off" 
              placeholder="请输入设备系统版本号"
              class="input"
			  style='width: 100%'
			  maxlength="2"
			  show-word-limit
              size='large'
            />
          </el-form-item>
          
          <el-form-item prop="hub_url" class="form-item-inline">
            <div class="label-with-icon">
              <i class="icon-creator"></i>
              <span>Hub地址</span>
            </div>
            <el-input 
              v-model="appExecutorSave.hub_url" 
              autocomplete="off" 
              placeholder="请输入所属Hub地址"
              class="input"
			  maxlength="100"
			  show-word-limit
              size='large'
            />
          </el-form-item>
          
          <el-form-item prop="node_url" class="form-item-inline">
            <div class="label-with-icon">
              <i class="icon-updater"></i>
              <span>Node地址</span>
            </div>
            <el-input 
              v-model="appExecutorSave.node_url" 
              autocomplete="off" 
              placeholder="请输入所属Node地址"
			  maxlength="100"
			  show-word-limit
              class="input"
              size='large'
            />
          </el-form-item>
		  
		  <el-form-item prop="device_desc" class="form-item-inline-two">
		    <div class="label-with-icon">
		      <i class="icon-desc"></i>
		      <span>设备描述</span>
		    </div>
		    <el-input
		      v-model="appExecutorSave.device_desc" 
		      autocomplete="off" 
		      :autosize="{ minRows: 2, maxRows: 4 }"
		      type="textarea" 
		      placeholder="请输入设备描述"
			  maxlength="200"
			  show-word-limit
		      class="text"
		      size='large'
		    />
		  </el-form-item>
        </el-form>
      </div>
      
      <div slot="footer" class="dialog-footer" v-if="!appExecuteView">
        <el-button @click="editAppExecutorVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button 
          v-if="permission.has_add_permission || permission.has_edit_permission" 
          type="primary" 
          @click="saveAppExecutor" 
          class="dialog-confirm-btn"
        >
          保存
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import BodyEdit from '../../components/BodyEdit.vue'
import Header from './Header.vue'
import Cookie from './Cookie.vue'
import {
  Refresh,
  Search,
  Plus,
  View,
  Delete,
  EditPen,
  Environment,
  Monitor,
  Phone,
  InfoFilled
} from '@element-plus/icons-vue'

export default {
  name: 'EnvironmentManagement',
  computed: {
    ...mapState(['pathPermission', 'projectInfo', 'env_id', 'env_name', 'userInfo']),
    calcMinWidth() {
      let visibleButtons = 0
      if (this.permission.has_read_permission) visibleButtons += 1
      if (this.permission.has_edit_permission) visibleButtons += 1
      if (this.permission.has_delete_permission) visibleButtons += 1
      return Math.max(10, visibleButtons * 60)
    }
  },
  data() {
    return {
      userColor: {},
      envRules: {
        name: [{
          required: true,
          message: '环境名称不能为空',
          trigger: 'blur',
        }],
      },
      envVarRules: {
        name: [{
          required: true,
          message: '变量名称不能为空',
          trigger: 'blur',
        }],
        env: [{
          required: true,
          message: '请选择所属环境',
          trigger: 'change',
        }],
        value: [{
          required: true,
          message: '变量值不能为空',
          trigger: 'blur',
        }],
        remark: [{
          required: true,
          message: '备注不能为空',
          trigger: 'blur',
        }],
      },
      globalVarRules: {
        name: [{
          required: true,
          message: '变量名称不能为空',
          trigger: 'blur',
        }],
        value: [{
          required: true,
          message: '变量值不能为空',
          trigger: 'blur',
        }],
        remark: [{
          required: true,
          message: '备注不能为空',
          trigger: 'blur',
        }],
      },
      webRules: {
        name: [{
          required: true,
          message: '执行机名称不能为空',
          trigger: 'blur',
        }],
        status: [{
          required: true,
          message: '请选择执行机状态',
          trigger: 'change',
        }],
        type: [{
          required: true,
          message: '请选择执行机类型',
          trigger: 'change',
        }],
        url: [{
          required: true,
          message: '执行机地址不能为空',
          trigger: 'blur',
        }],
        vnc_url: [{
          required: true,
          message: '执行机VNC地址不能为空',
          trigger: 'blur',
        }],
      },
      appRules: {
        device_name: [{
          required: true,
          message: '设备名称不能为空',
          trigger: 'blur',
        }],
        device_desc: [{
          required: true,
          message: '设备描述不能为空',
          trigger: 'blur',
        }],
        hub_url: [{
          required: true,
          message: 'Hub地址不能为空',
          trigger: 'blur',
        }],
        platform_name: [{
          required: true,
          message: '请选择设备类型',
          trigger: 'change',
        }],
        platform_version: [{
          required: true,
          message: '设备版本号不能为空',
          trigger: 'blur',
        }],
        node_url: [{
          required: true,
          message: 'Node地址不能为空',
          trigger: 'blur',
        }],
        status: [{
          required: true,
          message: '请选择设备状态',
          trigger: 'change',
        }],
      },
      envView: false,
      envUrlView: false,
      webExecuteView: false,
      appExecuteView: false,
      active: 'setup',
      activeName: 'env',
      permission: {},
      user_list: [],
      envSearch: {
        name: '',
        project: '',
        create_by: '',
        update_by: '',
      },
      paramsSearch: {
        env: '',
        name: '',
        remark: '',
        project: '',
        create_by: '',
        update_by: '',
      },
      paramsGlobalSearch: {
        name: '',
        remark: '',
        project: '',
        create_by: '',
        update_by: '',
      },
      page_size_params: {
        page: 1,
        size: 10,
      },
	  sort_params: {
	    ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
	  },
      count: 1,
      env_name: '',
      title: '新增环境',
      params_title: '新增环境变量',
      global_params_title: '新增全局变量',
      isAdd: true,
      default_env_id: '',
      // 修复：使用独立的对话框控制变量
      editEnvDialogVisible: false,
      editParamsDialogVisible: false,
      editGlobalParamsDialogVisible: false,
      editExecutorVisible: false,
      editAppExecutorVisible: false,
      env_list: [],
      params_list: [],
      global_params_list: [],
      ViewVisible: false,
      envSave: {
        project: '',
        name: '',
        setup: '',
        teardown: '',
      },
      paramsSave: {
        project: '',
        name: '',
        env: '',
        value: '',
        remark: ''
      },
      paramsGlobalSave: {
        project: '',
        name: '',
        value: '',
        remark: ''
      },
      webExecutorSearch: {
        name: '',
        type: '',
        project: '',
        status: 1,
        create_by: '',
        update_by: '',
      },
      appExecutorSearch: {
        device_name: '',
        type: '',
        project: '',
        status: 1,
        create_by: '',
        update_by: '',
      },
      executorSave: {
        project: '',
        name: '',
        url: '',
        type: '',
        vnc_url: '',
        status: 1
      },
      appExecutorSave: {
        project: '',
        device_name: '',
        hub_url: '',
        platform_name: '',
        platform_version: '',
        node_url: '',
        vnc_url: '',
        status: 1
      },
      executorTitle: '',
      appExecutorTitle: '',
      web_executor_list: [],
      app_executor_list: [],
      role_names: [],
    }
  },
  components: {
    BodyEdit,
    Refresh,
    Search,
    Plus,
    View,
    Delete,
    EditPen,
    Environment,
    Monitor,
    Phone,
    InfoFilled,
	Header,
	Cookie
  },
  methods: {
    ...mapActions(['check_permission']),
    
    handleCurrentChange() {
      this.getEnvs()
    },
    
    handleCurrentParamsChange() {
      this.getPars()
    },
    
    handleCurrentWebChange() {
      this.getWebExecutors()
    },
    
    handleCurrentAppChange() {
      this.getAppExecutors()
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
    
    handleSizeChange() {
      this.getEnvs()
    },
    
    handleSizeParamsChange() {
      this.getPars()
    },

    handleSizeGlobalParamsChange() {
      this.getGlobalPars()
    },
    
    handleSizeWebChange() {
      this.getWebExecutors()
    },
    
    handleSizeAppChange() {
      this.getAppExecutors()
    },
    
    changeEnv(value) {
      this.paramsSearch.env = value
      this.getPars()
    },
    
    searchEnv() {
      this.getEnvs()
    },
    
    searchParams() {
      this.getPars()
    },

    searchGlobalParams() {
      this.getGlobalPars()
    },

    
    searchExecutor() {
      this.getWebExecutors()
    },
    
    searchAppExecutor() {
      this.getAppExecutors()
    },
    
    reset() {
      for (let key in this.envSearch) {
        this.envSearch[key] = ''
      }
    },
    
    resetParams() {
      for (let key in this.paramsSearch) {
        this.paramsSearch[key] = ''
      }
    },

    resetGlobalParams() {
      for (let key in this.paramsGlobalSearch) {
        this.paramsGlobalSearch[key] = ''
      }
    },
    
    resetExecutor() {
      for (let key in this.webExecutorSearch) {
        if (key != 'env') {
          this.webExecutorSearch[key] = ''
        }
      }
    },
    
    resetAppExecutor() {
      for (let key in this.appExecutorSearch) {
        if (key != 'env') {
          this.appExecutorSearch[key] = ''
        }
      }
    },
    
    // 新的重置方法
    resetCurrentFilter() {
      switch (this.activeName) {
        case 'first':
          this.reset()
          break
        case 'second':
          this.resetParams()
          break
        case 'thrid':
          this.resetExecutor()
          break
        case 'four':
          this.resetAppExecutor()
          break
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
	  if (this.activeName ==='env'){
		  this.getEnvs()
	  }else if(this.activeName ==='params'){
		  this.getPars()
	  }else if(this.activeName ==='web'){
		  this.getWebExecutors()
	  }else if(this.activeName ==='app'){
		  this.getAppExecutors()
	  }
	},
    
    editEnv(row_data) {
      this.isAdd = false
      this.title = '编辑环境'
      this.envView = false
      this.envSave = row_data
      this.editEnvDialogVisible = true
      if (this.$refs.envRef) {
        this.$refs.envRef.clearValidate()
      }
    },
    
    addEnv() {
      this.title = '新增环境'
      this.envView = false
      this.editEnvDialogVisible = true
      this.isAdd = true
      if (this.$refs.envRef) {
        this.$refs.envRef.resetFields()
      }
    },
    
    viewEnv(row_data) {
      this.isAdd = false
      this.title = '查看环境'
      this.envView = true
      this.envSave = row_data
      this.editEnvDialogVisible = true
    },
    
    addParams() {
      this.isAdd = true
      this.params_title = '新增环境变量'
      this.envUrlView = false
      this.editParamsDialogVisible = true
      this.paramsSave = {}
      this.isAdd = true
      if (this.$refs.envVarRef) {
        this.$refs.envVarRef.resetFields()
      }
    },

     addGlobalParams() {
      this.isAdd = true
      this.global_params_title = '新增全局变量'
      this.globalView = false
      this.editGlobalParamsDialogVisible = true
      this.paramsGlobalSave = {}
      this.isAdd = true
      if (this.$refs.globalRef) {
        this.$refs.globalRef.resetFields()
      }
    },
    
    editParams(row_data) {
      this.isAdd = false
      this.params_title = '编辑环境变量'
      this.envUrlView = false
      this.paramsSave = { ...row_data }
      this.editParamsDialogVisible = true
      if (this.$refs.envVarRef) {
        this.$refs.envVarRef.clearValidate()
      }
    },

    editGlobalParams(row_data) {
      this.isAdd = false
      this.global_params_title = '编辑全局变量'
      this.globalView = false
      this.paramsGlobalSave = { ...row_data }
      this.editGlobalParamsDialogVisible = true
      if (this.$refs.globalRef) {
        this.$refs.globalRef.clearValidate()
      }
    },
    
    viewParams(row_data) {
      this.isAdd = false
      this.params_title = '查看环境变量'
      this.envUrlView = true
      this.paramsSave = { ...row_data }
      this.editParamsDialogVisible = true
    },

    viewGlobalParams(row_data) {
      this.isAdd = false
      this.global_params_title = '查看环境变量'
      this.globalView = true
      this.paramsGlobalSave = { ...row_data }
      this.editGlobalParamsDialogVisible = true
    },
    
    viewExecutor(row_data) {
      this.isAdd = false
      this.webExecuteView = true
      this.executorTitle = '查看执行机'
      this.executorSave = { ...row_data }
      this.editExecutorVisible = true
    },
    
    editExecutor(row_data) {
      this.isAdd = false
      this.webExecuteView = false
      this.executorTitle = '编辑执行机'
      this.executorSave = { ...row_data }
      this.editExecutorVisible = true
      if (this.$refs.webRef) {
        this.$refs.webRef.clearValidate()
      }
    },
    
    editAppExecutor(row_data) {
      this.isAdd = false
      this.appExecuteView = false
      this.appExecutorTitle = '编辑设备'
      this.appExecutorSave = { ...row_data }
      this.editAppExecutorVisible = true
      if (this.$refs.appRef) {
        this.$refs.appRef.clearValidate()
      }
    },
    
    viewAppExecutor(row_data) {
      this.isAdd = false
      this.appExecuteView = true
      this.appExecutorTitle = '查看设备'
      this.appExecutorSave = { ...row_data }
      this.editAppExecutorVisible = true
    },
    
    addExecutor() {
      this.editExecutorVisible = true
      this.webExecuteView = false
      this.executorSave = {}
	  this.executorSave.status = 1
	  this.executorSave.type = 1
      this.isAdd = true
      this.executorTitle = '新增执行机'
      if (this.$refs.webRef) {
        this.$refs.webRef.resetFields()
      }
    },
    
    addAppExecutor() {
      this.editAppExecutorVisible = true
      this.appExecutorSave = {}
	  this.appExecutorSave.status = 1
	  this.appExecutorSave.platform_name = 1
      this.appExecuteView = false
      this.isAdd = true
      this.appExecutorTitle = '新增设备'
      if (this.$refs.appRef) {
        this.$refs.appRef.resetFields()
      }
    },
    
    save() {
      if (this.isAdd) {
        this.createEnv()
      } else {
        this.updateEnv()
      }
    },
    
    saveParams() {
      if (this.isAdd) {
        this.createPar()
      } else {
        this.updatePar()
      }
    },

    saveGlobalParams() {
      if (this.isAdd) {
        this.createGlobalPar()
      } else {
        this.updateGlobalPar()
      }
    },
    
    saveExecutor() {
      if (this.isAdd) {
        this.createWebExecutor()
      } else {
        this.updateWebExecutor()
      }
    },
    
    saveAppExecutor() {
      if (this.isAdd) {
        this.createAppExecutor()
      } else {
        this.updateAppExecutor()
      }
    },
    
    async createEnv() {
      this.$refs['envRef'].validate(async (valid, fields) => {
        if (valid) {
          this.envSave.project = this.projectInfo.id
          const response = await this.$api.createEnv(this.envSave)
          if (response.status === 201) {
            this.editEnvDialogVisible = false
            this.getEnvs()
            ElMessage({ message: "保存成功", type: 'success' })
          }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
        }
      })
    },
    
    async createPar() {
      this.$refs['envVarRef'].validate(async (valid, fields) => {
        if (valid) {
          this.paramsSave.project = this.projectInfo.id
          const response = await this.$api.createPar(this.paramsSave)
          if (response.status === 201) {
            this.editParamsDialogVisible = false
            this.getPars()
            ElMessage({ message: "保存成功", type: 'success' })
          }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
        }
      })
    },

    async createGlobalPar() {
      this.$refs['globalRef'].validate(async (valid, fields) => {
        if (valid) {
          this.paramsGlobalSave.project = this.projectInfo.id
          const response = await this.$api.createGlobalPar(this.paramsGlobalSave)
          if (response.status === 201) {
            this.editGlobalParamsDialogVisible = false
            this.getGlobalPars()
            ElMessage({ message: "保存成功", type: 'success' })
          }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
        }
      })
    },
    
    async createWebExecutor() {
      this.$refs['webRef'].validate(async (valid, fields) => {
        if (valid) {
          this.executorSave.project = this.projectInfo.id
          const response = await this.$api.createWebExecutor(this.executorSave)
          if (response.status === 201) {
            this.editExecutorVisible = false
            this.getWebExecutors()
            ElMessage({ message: "保存成功", type: 'success' })
          }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
        }
      })
    },
    
    async createAppExecutor() {
      this.$refs['appRef'].validate(async (valid, fields) => {
        if (valid) {
          this.appExecutorSave.project = this.projectInfo.id
          const response = await this.$api.createAppExecutor(this.appExecutorSave)
          if (response.status === 201) {
            this.editAppExecutorVisible = false
            this.getAppExecutors()
            ElMessage({ message: "保存成功", type: 'success' })
          }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
        }
      })
    },
    
    async updateEnv() {
      this.$refs['envRef'].validate(async (valid, fields) => {
        if (valid) {
          this.envSave.project = this.projectInfo.id
          const response = await this.$api.updateEnv(this.envSave.id, this.envSave)
          if (response.status === 200) {
            this.editEnvDialogVisible = false
            this.getEnvs()
            ElMessage({ message: "保存成功", type: 'success' })
          }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
        } else {
          return false
        }
      })
    },
    
    async updatePar() {
      this.$refs['envVarRef'].validate(async (valid, fields) => {
        if (valid) {
          this.paramsSave.project = this.projectInfo.id
          const response = await this.$api.updatePar(this.paramsSave.id, this.paramsSave)
          if (response.status === 200) {
            this.editParamsDialogVisible = false
            this.getPars()
            ElMessage({ message: "保存成功", type: 'success' })
          }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
        }
      })
    },

    async updateGlobalPar() {
      this.$refs['globalRef'].validate(async (valid, fields) => {
        if (valid) {
          this.paramsGlobalSave.project = this.projectInfo.id
          const response = await this.$api.updateGlobalPar(this.paramsGlobalSave.id, this.paramsGlobalSave)
          if (response.status === 200) {
            this.editGlobalParamsDialogVisible = false
            this.getGlobalPars()
            ElMessage({ message: "保存成功", type: 'success' })
          }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
        }
      })
    },
    
    async updateWebExecutor() {
      this.$refs['webRef'].validate(async (valid, fields) => {
        if (valid) {
          this.executorSave.project = this.projectInfo.id
          const response = await this.$api.updateWebExecutor(this.executorSave.id, this.executorSave)
          if (response.status === 200) {
            this.editExecutorVisible = false
            this.getWebExecutors()
            ElMessage({ message: "保存成功", type: 'success' })
          }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
        }
      })
    },
    
    async updateAppExecutor() {
      this.$refs['appRef'].validate(async (valid, fields) => {
        if (valid) {
          this.appExecutorSave.project = this.projectInfo.id
          const response = await this.$api.updateAppExecutor(this.appExecutorSave.id, this.appExecutorSave)
          if (response.status === 200) {
            this.editAppExecutorVisible = false
            this.getAppExecutors()
            ElMessage({ message: "保存成功", type: 'success' })
          }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
        }
      })
    },
    
    async deleteEnv(id) {
      ElMessageBox.confirm(
        '确定删除此环境？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deleteEnv(id)
        if (response.status === 204) {
          this.getEnvs()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
      }).catch(() => {})
    },
    
    async deleteParams(id) {
      ElMessageBox.confirm(
        '确定删除此环境变量？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deletePar(id)
        if (response.status === 204) {
          this.getPars()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
      }).catch(() => {})
    },

     async deleteGlobalParams(id) {
      ElMessageBox.confirm(
        '确定删除此全局变量？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deleteGlobalPar(id)
        if (response.status === 204) {
          this.getGlobalPars()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
      }).catch(() => {})
    },
    
    async deleteWebExecutor(id) {
      ElMessageBox.confirm(
        '确定删除此执行机？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deleteWebExecutor(id)
        if (response.status === 204) {
          this.getWebExecutors()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
      }).catch(() => {})
    },
    
    async deleteAppExecutor(id) {
      ElMessageBox.confirm(
        '确定删除此设备？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deleteAppExecutor(id)
        if (response.status === 204) {
          this.getAppExecutors()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }
      }).catch(() => {})
    },
    
    async getEnvs() {
      this.envSearch.project = this.projectInfo.id
      this.envSave.project = this.projectInfo.id
      const response = await this.$api.getEnvs(Object.assign(this.envSearch, this.page_size_params, this.sort_params))
      if (response.status === 200) {
        this.env_list = { ...response.data }
      }
    },
    
    async getPars() {
      this.paramsSearch.project = this.projectInfo.id
      this.paramsSave.project = this.projectInfo.id
      const response = await this.$api.getPars(Object.assign(this.paramsSearch, this.page_size_params, this.sort_params))
      if (response.status === 200) {
        this.params_list = { ...response.data }
      }
    },

    async getGlobalPars() {
      this.paramsGlobalSearch.project = this.projectInfo.id
      this.paramsGlobalSave.project = this.projectInfo.id
      const response = await this.$api.getGlobalPars(Object.assign(this.paramsGlobalSearch, this.page_size_params, this.sort_params))
      if (response.status === 200) {
        this.global_params_list = { ...response.data }
      }
    },
    
    async getWebExecutors() {
      this.webExecutorSearch.project = this.projectInfo.id
      this.executorSave.project = this.projectInfo.id
      const response = await this.$api.getWebExecutors(Object.assign(this.webExecutorSearch, this.page_size_params, this.sort_params))
      if (response.status === 200) {
        this.web_executor_list = { ...response.data }
      }
    },
    
    async getAppExecutors() {
      this.appExecutorSearch.project = this.projectInfo.id
      this.appExecutorSave.project = this.projectInfo.id
      const response = await this.$api.getAppExecutors(Object.assign(this.appExecutorSearch, this.page_size_params, this.sort_params))
      if (response.status === 200) {
        this.app_executor_list = { ...response.data }
      }
    },

    async  check_permission(){
        const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission['/env/env']}
        const response = await this.$api.check_permission(params)
        if (response.status === 200){
          this.permission = { ...response.data.result }
        }
	 },
    
    handleClick(tab) {
      // 切换标签页时重置分页参数
      this.page_size_params.page = 1
      this.page_size_params.size = 10
      
      // 根据标签页加载对应的数据
      switch (tab.props.name) {
        case 'first':
          this.getEnvs()
          break
        case 'second':
          this.getGlobalPars()
          break
        case 'thrid':
          this.getPars()
          break
        case 'four':
          this.getWebExecutors()
          break
        case 'five':
          this.getAppExecutors()
          break
      }
    }
  },
  created() {
    this.check_permission()
    this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
    this.getEnvs()
    this.getPars()
    this.getGlobalPars()
    this.getWebExecutors()
    this.getAppExecutors()
  }
}
</script>

<style scoped>
.environment-management-container {
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

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 10px 10px 0px;
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

/* 筛选表单样式 */
.filter-form-wrapper {
  padding: 25px 5px 0px 5px;
}

.filter-form .el-row .el-col {
    width: 100%;
    margin-bottom: 16px;
  }

.form-item-enhanced {
  margin-bottom: 0;
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

.form-item-inline {
  margin-bottom: 20px;
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

.form-item-inline-two {
  margin-top: 40px;
  display: flex;
  flex-direction: row;
  align-items: center;
  height: 40px;
}

.form-item-inline-two :deep(.el-form-item__content) {
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
.icon-name,
.icon-desc,
.icon-role,
.icon-email,
.icon-creator,
.icon-updater,
.icon-remark {
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

.icon-desc {
  background: linear-gradient(135deg, #5500ff 0%, #aa007f 100%);
  border-radius: 4px;
}
.icon-name {
  background: linear-gradient(135deg, #00ff00 0%, #5555ff 100%);
  
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

.icon-remark {
  background: linear-gradient(135deg, #06b6d4 0%, #0e7490 100%);
  border-radius: 4px;
}

/* 内容卡片 */
.content-card {
  flex: 1;
  background: white;
  border: none;
  border-radius: 16px;
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

/* 内容标题区域 */
.content-header {
  padding: 20px 24px 10px 24px;
  margin-top: 20px;
  border-bottom: 1px solid #f1f5f9;
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
  flex: 1;
}

.content-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  position: relative;
  padding-left: 16px;
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

/* 调整统计信息位置 */
.stats-info {
  display: flex;
  gap: 16px;
  margin-left: 30px;
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

/* 新增按钮区域 */
.action-buttons-section {
  display: flex;
  gap: 12px;
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

/* Tabs样式 */
.elegant-tabs {
  flex-shrink: 0;
  padding: 0 24px;
}

.elegant-tabs >>> .el-tabs__header {
  background: white;
  border-bottom: 1px solid #f1f5f9;
  margin: 0;
}

.elegant-tabs >>> .el-tabs__nav-wrap::after {
  background-color: #f1f5f9;
}

.elegant-tabs >>> .el-tabs__item {
  font-weight: 500;
  color: #64748b;
  padding: 0 20px;
  height: 48px;
  line-height: 48px;
  transition: all 0.3s ease;
}

.elegant-tabs >>> .el-tabs__item:hover {
  color: #3b82f6;
}

.elegant-tabs >>> .el-tabs__item.is-active {
  color: #3b82f6;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.1) 100%);
  border-radius: 8px 8px 0 0;
}

/* 表格区域 */
.table-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 0;
}

.table-wrapper {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 0px;
}

.elegant-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: transparent;
  border-radius: 12px;
  overflow: hidden;
  margin-top: 20px;
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

.elegant-table >>> .el-table__body-wrapper td {
  border-bottom: 1px solid #f1f5f9;
  padding: 16px 0;
  transition: all 0.3s ease;
}

.elegant-table >>> .el-table__body-wrapper .cell {
  padding: 0 16px;
}

/* 分页组件样式 */
.pagination-wrapper {
  padding: 20px 0 0px 0px;
  border-top: 1px solid #f1f5f9;
  float: right;
  flex-shrink: 0;
  display: block !important;
  min-height: 40px;
  background: white;
  z-index: 10;
  position: relative;
  opacity: 1 !important;
  visibility: visible !important;
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
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.action-btn i {
  color: white;
  font-size: 16px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 对话框样式优化 */
.elegant-dialog >>> .el-dialog {
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.elegant-dialog >>> .el-dialog__header {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
  padding: 20px 24px;
  margin: 0;
}

.elegant-dialog >>> .el-dialog__title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  background: linear-gradient(135deg, #1a1a1a 0%, #4a5568 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.dialog-content {
  padding: 24px;
}

.dialog-form {
  margin-bottom: 0;
}

/* 对话框表单项样式 - 与列表保持一致 */
.dialog-form-item {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  min-height: 56px;
}

.dialog-label-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  min-width: 120px;
  flex-shrink: 0;
  white-space: nowrap;
}

.dialog-label-with-icon i {
  display: inline-block;
  width: 16px;
  height: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  position: relative;
}

/* 对话框tabs样式 */
.drawer-card {
  flex: 1;
  background: white;
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  overflow-y: hidden;
}

::v-deep .content-card .el-card__body {
  padding: 0px;
}

::v-deep .filter-card .el-card__body {
  padding-bottom: 10px;
}

.drawer-tabs >>> .el-tabs__header {
  margin: 0;
  padding: 0px 24px 0;
  background: white;
  border-bottom: 1px solid #f1f5f9;
}

.drawer-tabs >>> .el-tabs__nav-wrap::after {
  background-color: #f1f5f9;
}

.drawer-tabs >>> .el-tabs__item {
  font-size: 16px;
  font-weight: 600;
  color: #64748b;
  padding: 0 24px;
  height: 48px;
  line-height: 48px;
  transition: all 0.3s ease;
}

.drawer-tabs >>> .el-tabs__item:hover {
  color: #3b82f6;
}

.drawer-tabs >>> .el-tabs__item.is-active {
  color: #1a1a1a;
  position: relative;
}

.drawer-tabs >>> .el-tabs__item.is-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 2px 2px 0 0;
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
  overflow-y: auto;
  min-height: 0;
}

.drawer-form {
  width: 100%;
}

/* 对话框底部按钮 */
.dialog-footer {
  padding: 20px 24px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.dialog-cancel-btn {
  padding: 10px 20px;
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
  .environment-management-container {
    padding: 16px;
  }
  
  .filter-card .filter-header,
  .filter-card .filter-form-wrapper,
  .content-header,
  .elegant-tabs {
    padding: 16px 20px;
  }
  
  .stats-info {
    margin-left: 20px;
  }
  
  .dialog-content {
    padding: 20px;
  }
}

@media screen and (max-width: 992px) {
  .title-with-stats {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .stats-info {
    margin-left: 0;
  }
  
  .dialog-form-item {
    flex-direction: column;
    align-items: flex-start;
    min-height: auto;
  }
  
  .dialog-label-with-icon {
    margin-right: 0;
    margin-bottom: 8px;
    min-width: auto;
    width: 100%;
  }
}

@media screen and (max-width: 768px) {
  .environment-management-container {
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
  
  
  
  .form-item-enhanced {
      margin-bottom: 0;
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
     color: #475569;
     min-width: 50px;
     margin-right: 10px;
     flex-shrink: 0;
     white-space: nowrap;
  }
  
  .label-text {
    white-space: nowrap;
  }
  
  .content-title-section {
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
    justify-content: flex-start;
    flex-wrap: wrap;
  }
  
  .action-buttons-section {
    width: 100%;
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
    padding: 15px 0;
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

.filter-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.content-card {
  animation: slideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
}

/* 合并列：创建/更新信息样式 */
.user-time-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
  padding: 8px 0;
}
.user-time-cell .user-info,
.user-time-cell .time-info {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
}
.user-time-cell .icon-user {
  width: 12px !important;
  height: 12px !important;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E") !important;
  background-size: contain !important;
  background-position: center !important;
  background-repeat: no-repeat !important;
  flex-shrink: 0 !important;
  border-radius: 0 !important;
  display: inline-block !important;
}
.user-time-cell .icon-time-small {
  width: 12px;
  height: 12px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  flex-shrink: 0;
  display: inline-block;
}
.user-time-cell .user-name {
  font-size: 13px;
  color: #334155;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-time-cell .time-text {
  font-size: 12px;
  color: #64748b;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>