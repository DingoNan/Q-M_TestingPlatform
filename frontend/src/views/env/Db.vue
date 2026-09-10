<template>
  <div class="database-management-container">
    <!-- 筛选卡片 -->
	<el-card class="drawer-card elegant-shadow">
	  <el-tabs v-model="activeName" class="drawer-tabs" @tab-click="handleClick">
	    <el-tab-pane label="数据库列表" name="db" lazy='true'>
			<el-card class="filter-card elegant-shadow">
			  
			  <div class="filter-header">
			    <div class="header-title-section">
			      <i class="icon-search"></i>
			      <h3 class="filter-title">数据库筛选</h3>
			      <el-tag size="small" type="info" effect="plain">模糊查询</el-tag>
			    </div>
			    <div class="header-action-section">
			      <el-button class="reset-btn" @click="activeName === 'first' ? reset() : resetEnv()">
			        <el-icon><Refresh /></el-icon>重置
			      </el-button>
			      <el-button type="primary" @click="activeName === 'first' ? search() : searchEnv()" class="search-btn">
			        <el-icon><Search /></el-icon>查询
			      </el-button>
			    </div>
			  </div>
			  
			  <div class="filter-form-wrapper" >
			    <el-form :model="dbSearch" class="filter-form inline-form">
			      <el-row :gutter="24">
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-inline">
			            <div class="label-with-icon">
			              <i class="icon-database"></i>
			              <span class="label-text">数据库名称</span>
			            </div>
			            <el-input 
			              v-model="dbSearch.name" 
			              placeholder="请输入数据库名称" 
			              clearable
			              class="input"
						  size='large'
			            />
			          </el-form-item>
			        </el-col>
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-inline">
			            <div class="label-with-icon">
			              <i class="icon-creator"></i>
			              <span class="label-text">创建人</span>
			            </div>
			            <el-select 
			              v-model="dbSearch.create_by" 
			              placeholder="请选择创建人" 
			              clearable
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
			          <el-form-item class="form-item-inline">
			            <div class="label-with-icon">
			              <i class="icon-updater"></i>
			              <span class="label-text">更新人</span>
			            </div>
			            <el-select 
			              v-model="dbSearch.update_by" 
			              placeholder="请选择更新人" 
			              clearable
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
			
			<!-- 内容区域 -->
			<el-card class="content-card elegant-shadow">
			  <div class="tabs-wrapper">
				<div class="tab-content">
				  <div class="content-header">
				    <div class="content-title-section">
				      <div class="title-with-stats">
				        <h3 class="content-title">数据库列表</h3>
				        <div class="stats-info">
				          <div class="stat-item">
				            <span class="stat-label">总计</span>
				            <span class="stat-value">{{ db_list.count || 0 }}</span>
				          </div>
				          <div class="stat-item">
				            <span class="stat-label">当前页</span>
				            <span class="stat-value">{{ page_size_params.page }}</span>
				          </div>
				        </div>
				      </div>
				      <el-button 
				        v-if="permission.has_add_permission" 
				        @click="addDb" 
				        type="primary" 
				        class="add-btn"
				      >
				        新增数据库
				      </el-button>
				    </div>
				  </div>
							
				  <!-- 数据库列表表格 -->
				  <div class="table-wrapper">
				    <el-table 
				      :data="db_list.results" 
				      :max-height="'calc(100vh - 550px)'" 
				      class="elegant-table"
				      :header-row-style="headerRowStyle"
				      :show-overflow-tooltip='true'
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
				        label="数据库名称" 
				        prop="name" 
				        min-width="120" 
				        align="center"
				        class-name="db-column"
				      >
				        <template #default="scope">
				          <div class="db-cell">
				            <div class="db-icon">
				              <i class="icon-database-small"></i>
				            </div>
				            <div class="">
				              <span class="dbname">{{ scope.row.name }}</span>
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
				              content="查看数据库" 
				              placement="top" 
				              effect="dark"
				            >
				              <el-button 
				                type="success" 
				                v-if="permission.has_read_permission" 
				                class="action-btn view-btn"
				                @click.stop="viewDb(scope.row)"
								
				                circle
				              >
				                <el-icon><View /></el-icon>
				              </el-button>
				            </el-tooltip>
				            
				            <el-tooltip 
				              content="编辑数据库" 
				              placement="top" 
				              effect="dark"
				            >
				              <el-button 
				                type="warning" 
				                v-if="permission.has_edit_permission" 
				                class="action-btn edit-btn"
				                @click.stop="editDb(scope.row)"
				                circle
				              >
				                <el-icon><EditPen /></el-icon>
				              </el-button>
				            </el-tooltip>
				            
				            <el-tooltip 
				              content="删除数据库" 
				              placement="top" 
				              effect="dark"
				            >
				              <el-button 
				                type="danger" 
				                v-if="permission.has_delete_permission" 
				                @click.stop="deleteDb(scope.row.id)" 
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
				</div>
			  </div>
			  
			  <!-- 分页组件移到标签页外部 -->
			  <div class="pagination-wrapper">
			    <el-pagination
			      v-model:current-page="page_size_params.page"
			      v-model:page-size="page_size_params.size"
			      :page-sizes="[10, 20, 30, 50]"
			      :hide-on-single-page="false"
			      layout="total, sizes, prev, pager, next, jumper"
			      :total="db_list.count"
			      @size-change="handleSizeChange"
			      @current-change="handleCurrentChange"
			      class="input select"
			      :background="true"
			    />
			    
			  </div>
			</el-card>
			
		</el-tab-pane>
		<el-tab-pane label="数据库环境配置" name="env_db" lazy='true'>
			<el-card class="filter-card elegant-shadow">
			  
			  <div class="filter-header">
			    <div class="header-title-section">
			      <i class="icon-search"></i>
			      <h3 class="filter-title">数据库环境配置</h3>
			      <el-tag size="small" type="info" effect="plain">精确查询</el-tag>
			    </div>
			    <div class="header-action-section">
			      <el-button class="reset-btn" @click="resetEnv()">
			        <el-icon><Refresh /></el-icon>重置
			      </el-button>
			      <el-button type="primary" @click="searchEnv()" class="search-btn">
			        <el-icon><Search /></el-icon>查询
			      </el-button>
			    </div>
			  </div>
			  
			  <div class="filter-form-wrapper" >
			    <el-form :model="envdbSearch" class="filter-form inline-form">
			      <el-row :gutter="24">
			       <!-- <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-inline">
			            <div class="label-with-icon">
			              <i class="icon-db-type"></i>
			              <span class="label-text">数据库类型</span>
			            </div>
			            <el-select 
			              v-model="envdbSearch.type" 
			              placeholder="请选择数据库类型" 
			              clearable
			             class="select"
			             size='large'
			             popper-class='select-dropdown-rounded'
			            >
			              <el-option label='MySQL' :value="1" />
			              <el-option label='PostgreSQL' :value="2" />
			            </el-select>
			          </el-form-item>
			        </el-col> -->
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-inline">
			            <div class="label-with-icon">
			              <i class="icon-database"></i>
			              <span class="label-text">数据库名称</span>
			            </div>
			            <el-select 
			              v-model="envdbSearch.db" 
			              placeholder="请选择数据库名称" 
			              clearable
			              class="select"
			              size='large'
			              popper-class='select-dropdown-rounded'
			            >
			              <el-option 
			                v-for="db_obj in db_list.results" 
			                :key="db_obj.id"
			                :label="db_obj.name" 
			                :value="db_obj.id" 
			              />
			            </el-select>
			          </el-form-item>
			        </el-col>
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-inline">
			            <div class="label-with-icon">
			              <i class="icon-environment"></i>
			              <span class="label-text">环境名称</span>
			            </div>
			            <el-select 
			              v-model="envdbSearch.env" 
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
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="form-item-inline">
			            <div class="label-with-icon">
			              <i class="icon-creator"></i>
			              <span class="label-text">创建人</span>
			            </div>
			            <el-select 
			              v-model="envdbSearch.create_by" 
			              placeholder="请选择创建人" 
			              clearable
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
			          <el-form-item class="form-item-inline">
			            <div class="label-with-icon">
			              <i class="icon-updater"></i>
			              <span class="label-text">更新人</span>
			            </div>
			            <el-select 
			              v-model="envdbSearch.update_by" 
			              placeholder="请选择更新人" 
			              clearable
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
			
			<!-- 内容区域 -->
			<el-card class="content-card elegant-shadow">
			  <div class="tab-content">
			    <div class="content-header">
			      <div class="content-title-section">
			        <div class="title-with-stats">
			          <h3 class="content-title">数据库环境配置</h3>
			          <div class="stats-info">
			            <div class="stat-item">
			              <span class="stat-label">总计</span>
			              <span class="stat-value">{{ envDbList.count || 0 }}</span>
			            </div>
			            <div class="stat-item">
			              <span class="stat-label">当前页</span>
			              <span class="stat-value">{{ page_size_params.page }}</span>
			            </div>
			          </div>
			        </div>
			        <el-button 
			          v-if="permission.has_add_permission" 
			          @click="addEnvDb" 
			          type="primary" 
			          class="add-btn"
			        >
			          新增数据库环境
			        </el-button>
			      </div>
			    </div>
			  			
			    <!-- 数据库环境列表表格 -->
			    <div class="table-wrapper">
			      <el-table 
			        :data="envDbList.results" 
			        :max-height="'calc(100vh - 550px)'" 
			        class="elegant-table"
			        :header-row-style="headerRowStyle"
			        :show-overflow-tooltip='true'
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
			          label="数据库类型" 
			          prop="type_name" 
			          min-width="100" 
			          align="center"
			          class-name="type-column"
			        >
			          <template #default="scope">
			            <el-tag 
			              :type="getDbTypeTagType(scope.row.type_name)"
			              effect="plain"
			              class="type-tag"
			            >
			              {{ scope.row.type_name }}
			            </el-tag>
			          </template>
			        </el-table-column>
			        
			        <el-table-column 
			          label="数据库名称" 
			          prop="db_name" 
			          min-width="120" 
			          align="center"
			          class-name="db-column"
			        />
			        
			        <el-table-column 
			          label="所属环境" 
			          prop="env_name" 
			          min-width="120" 
			          align="center"
			          class-name="env-column"
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
			                content="查看数据库环境" 
			                placement="top" 
			                effect="dark"
			              >
			                <el-button 
			                  type="success" 
			                  v-if="permission.has_read_permission" 
			                  class="action-btn view-btn"
			                  @click.stop="viewEnvDb(scope.row)"
			                  circle
			                >
			                  <el-icon><View /></el-icon>
			                </el-button>
			              </el-tooltip>
			              
			              <el-tooltip 
			                content="编辑数据库环境" 
			                placement="top" 
			                effect="dark"
			              >
			                <el-button 
			                  type="warning" 
			                  v-if="permission.has_edit_permission" 
			                  class="action-btn edit-btn"
			                  @click.stop="editEnvDb(scope.row)"
			                  circle
			                >
			                  <el-icon><EditPen /></el-icon>
			                </el-button>
			              </el-tooltip>
			              
			              <el-tooltip 
			                content="删除数据库环境" 
			                placement="top" 
			                effect="dark"
			              >
			                <el-button 
			                  type="danger" 
			                  v-if="permission.has_delete_permission" 
			                  @click.stop="deleteEnvDb(scope.row.id)" 
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
			  </div>
			  
			  <!-- 分页组件移到标签页外部 -->
			  <div class="pagination-wrapper">
			    <el-pagination
			      v-model:current-page="page_size_params.page"
			      v-model:page-size="page_size_params.size"
			      :page-sizes="[10, 20, 30, 50]"
			      :hide-on-single-page="false"
			      layout="total, sizes, prev, pager, next, jumper"
			      :total="envDbList.count"
			      @size-change="handleEnvSizeChange"
			      @current-change="handleEnvCurrentChange"
			      class="input select"
			      :background="true"
			    />
			  </div>
			</el-card>
		</el-tab-pane>
	  </el-tabs>
	</el-card>
   

    <!-- 数据库对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      :title="title" 
      width="600"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form 
          :model="dbSave" 
          :disabled='dbView' 
          :rules="dbRules" 
          ref='dbRef'
          label-position='top'
          class="dialog-form"
        >
          <el-form-item class="dialog-form-item" prop='name'>
            <label class="dialog-label">
              <i class="icon-database-dialog"></i>
              数据库名称
            </label>
            <el-input 
              v-model="dbSave.name" 
              autocomplete="off" 
              placeholder="请输入数据库名称"
              class="input"
			  :maxlength="50"
			  show-word-limit
			  size='large'
            />
          </el-form-item>
        </el-form>
      </div>
      
	  <template #footer>
	  	<span class="dialog-footer" v-if='!dbView'>
	  		<el-button @click="editDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
	  		<el-button 
	  		  type="primary" 
	  		  @click="save" 
	  		  v-if='permission.has_add_permission || has_edit_permission'
	  		  class="dialog-confirm-btn"
	  		>
	  		  保存
	  		</el-button>
	  	</span>
	  </template>
     
    </el-dialog>

    <!-- 数据库环境对话框 -->
    <el-dialog 
      v-model="envEditDialogVisible" 
      :title="title" 
      width="600"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form 
          :model="envDbSave" 
          :disabled='dbEnvView' 
          :rules="envDbRules" 
          ref='envDbRef'
          label-position='top'
          class="dialog-form"
        >
          <el-form-item class="dialog-form-item" prop='env' >
            <label class="dialog-label">
              <i class="icon-environment-dialog"></i>
              所属环境
            </label>
            <el-select 
              v-model="envDbSave.env" 
              placeholder="请选择" 
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
          
          <el-form-item class="dialog-form-item" prop='db'>
            <label class="dialog-label">
              <i class="icon-database-dialog"></i>
              所属数据库
            </label>
            <el-select 
              v-model="envDbSave.db" 
              placeholder="请选择" 
              clearable
              class="select"
              size='large'
              popper-class='select-dropdown-rounded'
            >
              <el-option 
                v-for="db_obj in db_list_no_limit.results" 
                :key="db_obj.id"
                :label="db_obj.name" 
                :value="db_obj.id" 
              />
            </el-select>
          </el-form-item>
          
          <el-form-item class="dialog-form-item" prop='type'>
            <label class="dialog-label">
              <i class="icon-db-type-dialog"></i>
              数据库类型
            </label>
            <el-select 
              v-model="envDbSave.type" 
              placeholder="请选择数据库类型" 
              clearable
              class="select"
              size='large'
              popper-class='select-dropdown-rounded'
            >
              <el-option label='MySQL' :value="1" />
              <el-option label='PostgreSQL' :value="2" />
              <el-option label='Redis' :value="3" />
            </el-select>
          </el-form-item>
          
          <el-form-item class="dialog-form-item" prop='name'>
            <label class="dialog-label">
              <i class="icon-connection"></i>
              连接名称
            </label>
            <el-input 
              v-model="envDbSave.name" 
              autocomplete="off" 
              placeholder="请输入数据库连接名称"
              class="input"
              size='large'
            />
          </el-form-item>
          
          <el-form-item class="dialog-form-item" prop='host'>
            <label class="dialog-label">
              <i class="icon-host"></i>
              连接地址
            </label>
            <el-input 
              v-model="envDbSave.host" 
              autocomplete="off" 
              placeholder="请输入数据库地址"
             class="input"
             size='large'
            />
          </el-form-item>
          
          <el-form-item class="dialog-form-item" prop='port'>
            <label class="dialog-label">
              <i class="icon-port"></i>
              连接端口号
            </label>
            <el-input-number 
              v-model="envDbSave.port" 
              :step="2" 
              style="width: 100%;"
              controls-position="right"
			  class="input"
			  size='large'
              :min="1"
              :max="65535"
            />
          </el-form-item>
          
          <el-form-item class="dialog-form-item" prop='username'>
            <label class="dialog-label">
              <i class="icon-user-dialog"></i>
              连接用户名
            </label>
            <el-input 
              v-model="envDbSave.username" 
              autocomplete="off" 
              placeholder="请输入数据库用户名"
              class="input"
              size='large'
            />
          </el-form-item>
          
          <el-form-item class="dialog-form-item" prop='password'>
            <label class="dialog-label">
              <i class="icon-password"></i>
              密码
            </label>
            <el-input 
              v-model="envDbSave.password" 
              autocomplete="off" 
              placeholder="请输入数据库密码"
              type="password"
              class="input"
              size='large'
            />
          </el-form-item>
        </el-form>
      </div>
      
	  <template #footer>
	  	<span class="dialog-footer" v-if='!dbEnvView'>
	  		<el-button @click="envEditDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
	  		<el-button 
	  		  type="primary" 
	  		  @click="saveEnvDb" 
	  		  v-if='permission.has_add_permission || permission.has_edit_permission'
	  		  class="dialog-confirm-btn"
	  		>
	  		  保存
	  		</el-button>
	  	</span>
	  </template>
    </el-dialog>
  </div>
</template>

<script>
import {mapState, mapActions, mapGetters} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, Edit, Plus, EditPen, Refresh, Search } from '@element-plus/icons-vue'

export default{
  name: 'DatabaseManagement',
  components: {
    View,
    Delete,
    Edit,
    Plus,
    EditPen,
    Refresh,
    Search
  },
	computed:{
		...mapState(['pathPermission', 'projectInfo', 'userInfo']),
		calcMinWidth() {
		  let visibleButtons = 0;
		  if (this.permission.has_read_permission) visibleButtons += 1;
		  if (this.permission.has_edit_permission) visibleButtons += 1;
		  if (this.permission.has_delete_permission) visibleButtons += 1;
		  return Math.max(10, visibleButtons * 60);
		}
	},
	data() {
		return {
			userColor: {},
			dbView: false,
			dbEnvView: false,
			permission: {},
			activeName: 'db',
			user_list: [],
			db_list_no_limit: [],
			dbSearch:{
				name: '',
				project: '',
				create_by: '',
				update_by: ''
			},
			envdbSearch:{
				project: '',
				type: '',
				env: '',
				db: '',
				create_by: '',
				update_by: ''
			},
			page_size_params: {
				page: 1,
				size: 10,
			},
			sort_params: {
			  ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
			},
			count: 1,
			title: '新增数据库',
			envTitle: '新增数据库环境',
			isAdd: true,
			isEnvAdd: true,
			editDialogVisible: false,
			envEditDialogVisible: false,
			headerDialogVisible: false,
			db_list: [],
			env_list: [],
			envDbList: [],
			ViewVisible: false,
			dbSave:{
				id: '',
				project: '',
				name: ''
			},
			dbRules: {
				name: [{
					required: true,
					message: '数据库名称不能为空',
					trigger: 'blur',
				}],
			},
			envDbRules: {
				username: [{
					required: true,
					message: '用户名不能为空',
					trigger: 'blur',
				}],
				password: [{
					required: true,
					message: '密码不能为空',
					trigger: 'blur',
				}],
				port: [{
					required: true,
					message: '端口号不能为空',
					trigger: 'blur',
				}],
				name: [{
					required: true,
					message: '数据库连接名称不能为空',
					trigger: 'blur',
				}],
				host: [{
					required: true,
					message: '数据库地址不能为空',
					trigger: 'blur',
				}],
				env: [{
					required: true,
					message: '请选择所属环境',
					trigger: 'change',
				}],
				type: [{
					required: true,
					message: '请选择数据库类型',
					trigger: 'change',
				}],
				db: [{
					required: true,
					message: '请选择所属数据库',
					trigger: 'change',
				}],
			},
			envDbSave:{
				id: '',
				username: '',
				password: '',
				port: 3306,
				name: '',
				host: '',
				env: '',
				type: 1,
				db: '',
			},
			role_names: [],
		}
	},
	setup() {
		return {
			Edit,
			Delete,
			Plus,
			View,
			EditPen,
      Refresh,
      Search
		}
	},
	methods:{
		...mapActions(['check_permission']),
    
    getDbTypeTagType(typeName) {
      const typeMap = {
        'MySQL': 'success',
        'PostgreSQL': 'primary',
        'Redis': 'danger'
      }
      return typeMap[typeName] || 'info'
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
	  if (this.activeName ==='db'){
		  this.getDbs()
	  }else{
		  this.getEnvDbs()
	  }
	},
		
	handleCurrentChange(){
		this.getDbs()
	},
	
	handleSizeChange(){
		this.getDbs()
	},
	
	handleEnvCurrentChange(){
		this.getEnvDbs()
	},
	
	handleEnvSizeChange(){
		this.getEnvDbs()
	},
	
	search(){
		this.getDbs()
	},
	
	reset(){
		for(let key in this.dbSearch){
			this.dbSearch[key] = ''
		}
	},
	
	searchEnv(){
		this.getEnvDbs()
	},
	
	resetEnv(){
		for(let key in this.envdbSearch){
			this.envdbSearch[key] = ''
		}
	},
	
	handleClick(tab) {
      this.activeName = tab.paneName
      if (tab.paneName === 'second') {
        this.getEnvDbs()
        this.getEnvs()
      } else {
        this.getDbs()
      }
    },
		
		editDb(row_data){
			this.isAdd = false
			this.title = '编辑数据库'
			this.dbView = false
			this.getDb(row_data.id)
			this.editDialogVisible = true
			this.$refs.dbRef.resetFields();
		},
		
		viewDb(row_data){
			this.isAdd = false
			this.title = '查看数据库'
			this.dbView = true
			this.getDb(row_data.id)
			this.editDialogVisible = true
		},
		
		addDb(){
			this.dbSave = {}
			this.dbEnvView = false
			this.title = '新增数据库'
			this.editDialogVisible = true
			this.isAdd = true
			this.$refs.dbRef.resetFields();
		},
		
		viewEnvDb(row_data){
			this.isAdd = false
			this.dbEnvView = true
			this.title = '查看数据库环境'
			this.envDbSave = {...row_data}
			this.envEditDialogVisible = true
		},
		
		editEnvDb(row_data){
			this.isAdd = false
			this.dbEnvView = false
			this.title = '编辑数据库环境'
			this.envDbSave = {...row_data}
			this.envEditDialogVisible = true
			this.$refs.envDbRef.resetFields()
		},
		
		addEnvDb(){
			this.envDbSave = {}
			this.dbEnvView = false
			this.title = '新增数据库环境'
			this.envEditDialogVisible = true
			this.isAdd = true
			this.$refs.envDbRef.resetFields()
		},
		
		save(){
			if (this.isAdd){
				this.createDb()
			}else{
				this.updateDb()
			}
		},
		
		saveEnvDb(){
			if (this.isAdd){
				this.createEnvDb()
			}else{
				this.updateEnvDb()
			}
		},
		
		async createDb(){
			this.$refs['dbRef'].validate(async (valid, fields)=>{
				if(valid){
					this.dbSave.project = this.projectInfo.id
					const response = await this.$api.createDb(this.dbSave)
					if(response.status === 201){
						this.editDialogVisible = false
						this.getDbs()
						ElMessage({message: "保存成功", type: 'success'})
					}
				}
			})
		},
		
		async createEnvDb(){
			this.$refs['envDbRef'].validate(async (valid, fields)=>{
				if(valid){
					const response = await this.$api.createEnvDb(this.envDbSave)
					if(response.status === 201){
						this.envEditDialogVisible = false
						this.getEnvDbs()
						ElMessage({message: "保存成功", type: 'success'})
					}
				}
			})
		},
		
		async updateDb(){
			this.$refs['dbRef'].validate(async (valid, fields)=>{
				if(valid){
					const response = await this.$api.updateDb(this.dbSave.id, this.dbSave)
					if(response.status === 200){
						this.editDialogVisible = false
						this.getDbs()
						ElMessage({message: "保存成功", type: 'success'})
					}
				}
			})
		},
		
		async updateEnvDb(){
			this.$refs['envDbRef'].validate(async (valid, fields)=>{
				if(valid){
					const response = await this.$api.updateEnvDb(this.envDbSave.id, this.envDbSave)
					if(response.status === 200){
						this.envEditDialogVisible = false
						this.getEnvDbs()
						ElMessage({message: "保存成功", type: 'success'})
					}
				}
			})
		},
		
		async deleteDb(id){
			ElMessageBox.confirm(
			    '确定删除此数据库？删除后数据将无法恢复。',
			    '确认删除',
			    {
			      confirmButtonText: '确认删除',
			      cancelButtonText: '取消',
			      type: 'warning',
			      confirmButtonClass: 'el-button--danger',
			      customClass: 'confirm-dialog'
			    }
			  ).then(async() => {
				  const response = await this.$api.deleteDb(id)
				  if (response.status === 204){
					  this.getDbs()
					  ElMessage({
					    type: 'success',
					    message: '删除成功',
					  })
				  }
				  
			    }).catch(() => {})
		},
		
		async deleteEnvDb(id){
			ElMessageBox.confirm(
			    '确定删除此数据库环境？删除后数据将无法恢复。',
			    '确认删除',
			    {
			      confirmButtonText: '确认删除',
			      cancelButtonText: '取消',
			      type: 'warning',
			      confirmButtonClass: 'el-button--danger',
			      customClass: 'confirm-dialog'
			    }
			  ).then(async() => {
				  const response = await this.$api.deleteEnvDb(id)
				  if (response.status === 204){
					  this.getEnvDbs()
					  ElMessage({
					    type: 'success',
					    message: '删除成功',
					  })
				  }
				  
			    }).catch(() => {})
		},
		
		async getDb(id){
			const response = await this.$api.getDb(id)
			if (response.status === 200){
				this.dbSave = {...response.data.result}
			}
		},
		
		async getDbs(){
			this.dbSearch.project = this.projectInfo.id
			const response = await this.$api.getDbs(Object.assign(this.dbSearch, this.page_size_params, this.sort_params))
			if (response.status === 200){
				this.db_list = {...response.data}
			}
		},
		
		async getEnvDbs(){
			this.envdbSearch.project = this.projectInfo.id
			const response = await this.$api.getEnvDbs(Object.assign(this.envdbSearch, this.page_size_params, this.sort_params))
			if (response.status === 200){
				this.envDbList = {...response.data}
			}
		},
		
		async getRoles(params){
			const response = await this.$api.getRoles(params)
			if (response.status === 200){
				this.role_names = response.data.results
			}
		},
		
		async getEnvs(params){
			const response = await this.$api.getEnvs({project: this.projectInfo.id})
			if (response.status === 200){
				this.env_list = {...response.data}
			}
		},

		 async  check_permission(){
			const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission['/env/db']}
			const response = await this.$api.check_permission(params)
			if (response.status === 200){
				this.permission = { ...response.data.result }
			}
	 	},
		
		async getDbNoLimit() {
		  try {
		    const response = await this.$api.getDbs({ project: this.projectInfo.id })
		    if (response.status === 200) {
		      this.db_list_no_limit = { ...response.data }
		    }
		  } catch (error) {
		    console.error('获取服务列表(无限制)失败:', error)
		  }
		},
	},
	created() {
	    this.check_permission()
		this.user_list =  JSON.parse(localStorage.getItem('user_list'))
		this.getDbs()
		this.getDbNoLimit()
		this.getEnvDbs()
		this.getEnvs()
	}
}
</script>

<style scoped>
.database-management-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px 15px 15px 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: calc(100vh - 75px);
  min-height: calc(100vh - 75px);
  max-height: calc(100vh - 75px);
  overflow: hidden;
}

.drawer-card {
  flex: 1;
  background: white;
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
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
  margin-bottom: 20px;
  border: none;
  border-radius: 16px;
  overflow: hidden;
  flex-shrink: 0;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 5px 10px 5px;
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

.reset-btn i {
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

.search-btn i {
  margin-right: 8px;
  font-size: 16px;
}

.filter-card :deep(.el-card__body) {
  padding: 20px 20px 0 20px;
}

.filter-form-wrapper {
  padding: 25px 5px 0px 5px;
}

.inline-form {
  margin-bottom: 0;
}

/* 标签和输入框在一行显示 */
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
  margin-right: 10px;
}

.icon-database,
.icon-db-type,
.icon-environment,
.icon-creator,
.icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
}

/* 为图标添加背景颜色 */
.icon-database {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 4px;
}

.icon-db-type {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border-radius: 4px;
}

.icon-environment {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 4px;
}

.icon-creator {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 4px;
}

.icon-updater {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border-radius: 4px;
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
  max-height: 100%;
  overflow: hidden;
}

.tabs-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tabs-wrapper :deep(.el-tabs) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tabs-wrapper :deep(.el-tabs__content) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tabs-wrapper :deep(.el-tab-pane) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tab-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.content-header {
  padding: 20px 24px;
  margin-top: 20px;
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

.elegant-table :deep(.el-table__header-wrapper th) {
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  font-weight: 600;
  color: #1a1a1a;
  border-bottom: 1px solid #e2e8f0;
  padding: 16px 0;
}

.elegant-table :deep(.el-table__header-wrapper .cell) {
  padding: 0 16px;
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row) {
  transition: all 0.3s ease;
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row:nth-child(even)) {
  background: #f8fafc;
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row:hover) {
  background: #f1f8ff;
  transform: translateX(4px);
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row.active-row) {
  background: #ebf5ff;
  position: relative;
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row.active-row::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%);
}

.elegant-table :deep(.el-table__body-wrapper td) {
  border-bottom: 1px solid #f1f5f9;
  padding: 16px 0;
  transition: all 0.3s ease;
}

.elegant-table :deep(.el-table__body-wrapper .cell) {
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

.db-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.db-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0;
}

.icon-database-small {
  width: 20px;
  height: 20px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M12 3C7.58 3 4 4.79 4 7v10c0 2.21 3.59 4 8 4s8-1.79 8-4V7c0-2.21-3.59-4-8-4zm0 2c3.87 0 6 1.5 6 2s-2.13 2-6 2-6-1.5-6-2 2.13-2 6-2zm6 4v3c0 .43-2.28 2-6 2s-6-1.57-6-2v-3c0 .43 2.28 2 6 2s6-1.57 6-2zm0 5v3c0 .43-2.28 2-6 2s-6-1.57-6-2v-3c0 .43 2.28 2 6 2s6-1.57 6-2z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

. {
	width: 100%
  /* align: center; */
}

.dbname {
  font-weight: 500;
  text-align: center;
  color: #1a1a1a;
}

.type-tag {
  border-radius: 12px;
  padding: 4px 12px;
  font-weight: 500;
}

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

/* 合并列：用户+时间 */
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

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  padding: 0;
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

/* 分页组件样式 */
.pagination-wrapper {
  padding: 20px 24px 0px 20px;
  float: right;
  border-top: 1px solid #f1f5f9;
  flex-shrink: 0;
  display: block !important;
  min-height: 40px;
  background: white;
  z-index: 10;
}

::v-deep .content-card .el-card__body {
  padding: 0px;
}


/* 对话框样式 */
.elegant-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.elegant-dialog :deep(.el-dialog__header) {
  padding: 24px 24px 0;
  margin: 0;
}

.elegant-dialog :deep(.el-dialog__title) {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 12px;
}

.elegant-dialog :deep(.el-dialog__title::before) {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 2px;
}

.elegant-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.dialog-content {
  padding: 24px 0 24px 0;
}

.dialog-form {
  margin: 0;
}

.dialog-form-item {
  margin-bottom: 20px;
    display: flex;
    flex-direction: row;
    align-items: center;
    height: 40px;
  }
  
.dialog-form-item :deep(.el-form-item__content) {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    flex-wrap: nowrap !important;
    margin-left: 0 !important;
    width: 100%;
}

.dialog-label {
  display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
    font-weight: 500;
    color: #475569;
    min-width: 100px;
    margin-right: 10px;
    flex-shrink: 0;
    white-space: nowrap;
}

.icon-database-dialog,
.icon-db-type-dialog,
.icon-environment-dialog,
.icon-connection,
.icon-host,
.icon-port,
.icon-user-dialog,
.icon-password {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
}

.icon-database-dialog {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 4px;
}

.icon-db-type-dialog {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border-radius: 4px;
}

.icon-environment-dialog {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 4px;
}

.icon-connection {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 4px;
}

.icon-host {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border-radius: 4px;
}

.icon-port {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border-radius: 4px;
}

.icon-user-dialog {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 4px;
}

.icon-password {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 4px;
}

.elegant-dialog :deep(.el-input-number) {
  width: 100%;
}

.elegant-dialog :deep(.el-input-number .el-input__inner) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: white;
  padding: 0 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  height: 40px;
  line-height: 40px;
}

.elegant-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px 24px;
  border-top: 1px solid #f1f5f9;
}

.dialog-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .database-management-container {
    padding: 16px;
    height: calc(100vh - 60px);
    min-height: calc(100vh - 60px);
    max-height: calc(100vh - 60px);
  }
  
  .filter-card .filter-header,
  .filter-card .filter-form-wrapper,
  .content-card .content-header,
  .content-card .table-wrapper {
    padding: 16px 20px;
  }
  
  .label-with-icon {
    min-width: 70px;
    font-size: 13px;
  }
}

@media screen and (max-width: 768px) {
  .database-management-container {
    padding: 12px;
    height: auto;
    min-height: calc(100vh - 60px);
    max-height: none;
    overflow-y: auto;
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
  
  .form-item-inline {
    flex-direction: column;
    align-items: flex-start;
    height: auto;
  }
  
  .form-item-inline :deep(.el-form-item__content) {
    flex-direction: column !important;
    align-items: flex-start !important;
  }
  
  .label-with-icon {
    margin-bottom: 8px;
    margin-right: 0;
    min-width: auto;
  }
  
  .input-elegant,
  .select-elegant {
    margin-left: 0;
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
</style>