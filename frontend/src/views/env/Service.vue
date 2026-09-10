<template>
  <div class="service-management-container">
	  
	<el-card class="drawer-card elegant-shadow">
	  <el-tabs v-model="activeName" class="drawer-tabs" @tab-click="handleClick">
	    <el-tab-pane label="服务列表" name="service" lazy='true'>
			
			<!-- 服务搜索区域 -->
			<el-card class="filter-card elegant-shadow" >
			  <div class="filter-header">
			    <div class="header-title-section">
			      <i class="icon-search"></i>
			      <h3 class="filter-title">服务筛选</h3>
			      <el-tag size="small" type="info" effect="plain">精确查询</el-tag>
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
			    <el-form :model="serviceSearch" class="filter-form inline-form">
			      <el-row :gutter="24">
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="inline-form-item">
			            <div class="inline-label-wrapper">
			              <i class="icon-service"></i>
			              <span class="inline-label-text">服务名称</span>
			            </div>
			            <el-input 
			              v-model="serviceSearch.name" 
			              placeholder="请输入服务名称" 
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
			              <span class="inline-label-text">创建人</span>
			            </div>
			            <el-select 
			              v-model="serviceSearch.create_by" 
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
			          <el-form-item class="inline-form-item">
			            <div class="inline-label-wrapper">
			              <i class="icon-updater"></i>
			              <span class="inline-label-text">更新人</span>
			            </div>
			            <el-select 
			              v-model="serviceSearch.update_by" 
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
			        <h3 class="content-title">服务列表</h3>
			        <div class="stats-info">
			          <div class="stat-item">
			            <span class="stat-label">总计</span>
			            <span class="stat-value">
			              {{ service_list.count || 0 }}
			            </span>
			          </div>
			          <div class="stat-item">
			            <span class="stat-label">当前页</span>
			            <span class="stat-value">
			              {{ page_size_params.page }}
			            </span>
			          </div>
			        </div>
			      </div>
			      <el-button 
			        v-if="permission.has_add_permission" 
			        @click="addService()" 
			        type="primary" 
			        class="add-btn"
			      >
			        <el-icon><Plus /></el-icon>
			        新增服务
			      </el-button>
			    </div>
			  </div>
			
			  <!-- Tab标签页 - 修复位置 -->
			  <div class="tab-container">
				<div class="table-container">
				  <div class="table-wrapper">
				    <el-table 
				      :data="service_list.results" 
				      :max-height="'calc(100vh - 535px)'" 
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
				      >
				        <template #default="scope">
				          <div class="index-cell">
				            {{ scope.$index + 1 + (page_size_params.page - 1) * page_size_params.size }}
				          </div>
				        </template>
				      </el-table-column>
				      
				      <el-table-column 
				        label="服务名称" 
				        prop="name" 
				        min-width="150" 
				        align="center"
				        class-name="service-column"
				      >
				        <template #default="scope">
				          <div class="service-cell">
				            <el-tag 
				              :type="getServiceType(scope.row.name)"
				              effect="light"
				              class="service-badge"
				            >
				              <i class="icon-service-cell"></i>
				              {{ scope.row.name }}
				            </el-tag>
				          </div>
				        </template>
				      </el-table-column>
					  
					  <el-table-column
					    label="接口请求域名配置" 
					    prop="name" 
					    min-width="150" 
					    align="center"
					    class-name="service-column"
					  >
					    <template #default="scope">
					      <div class="service-cell">
					        <el-tag v-if='!scope.row.is_server_host'
					          :type="getServiceType(scope.row.name)"
					          effect="light"
					          class="service-badge"
					        >
					          <i class="icon-service-cell"></i>
					          接口请求域名跟随产品域名配置
					        </el-tag>
							<el-tag v-else
							  :type="getServiceType(scope.row.name)"
							  effect="light"
							  class="service-badge"
							>
							  <i class="icon-service-cell"></i>
							  接口请求域名跟随服务域名配置
							</el-tag>
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
				              content="查看服务" 
				              placement="top" 
				              effect="dark"
				            >
				              <el-button 
				                type="success" 
				                v-if="permission.has_read_permission" 
				                class="action-btn view-btn"
				                @click.stop="viewService(scope.row)"
				                circle
				              >
				                <el-icon><View /></el-icon>
				              </el-button>
				            </el-tooltip>
				            
				            <el-tooltip 
				              content="编辑服务" 
				              placement="top" 
				              effect="dark"
				            >
				              <el-button 
				                type="warning" 
				                v-if="permission.has_edit_permission" 
				                class="action-btn edit-btn"
				                @click.stop="editService(scope.row)"
				                circle
				              >
				                <el-icon><EditPen /></el-icon>
				              </el-button>
				            </el-tooltip>
				            
				            <el-tooltip 
				              content="删除服务" 
				              placement="top" 
				              effect="dark"
				            >
				              <el-button 
				                type="danger" 
				                v-if="permission.has_delete_permission" 
				                @click.stop="deleteService(scope.row.id)" 
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
				      :total="service_list.count"
				      @size-change="handleSizeChange"
				      @current-change="handleCurrentChange"
				      class="select input"
					  style='float: right;'
				      :background="true"
				    />
				  </div>
				</div>
			  </div>
			</el-card>
		</el-tab-pane>
		<el-tab-pane label='服务域名配置' name='service_config' lazy='true'>
			<!-- 接口域名配置搜索区域 -->
			<el-card class="filter-card elegant-shadow" >
			  <div class="filter-header">
				<div class="header-title-section">
				  <i class="icon-search"></i>
				  <h3 class="filter-title">服务域名配置筛选</h3>
				  <el-tag size="small" type="info" effect="plain">关联查询</el-tag>
				</div>
				<div class="header-action-section">
				  <el-button class="reset-btn" @click="resetEnv">
					<el-icon><Refresh /></el-icon>重置
				  </el-button>
				  <el-button type="primary" @click="searchEnv" class="search-btn">
					<el-icon><Search /></el-icon>查询
				  </el-button>
				</div>
			  </div>
			  
			  <div class="filter-form-wrapper">
				<el-form :model="envServiceSearch" class="filter-form inline-form">
				  <el-row :gutter="24">
					<el-col :xs="24" :sm="12" :md="8" :lg="6">
					  <el-form-item class="inline-form-item">
						<div class="inline-label-wrapper">
						  <i class="icon-environment"></i>
						  <span class="inline-label-text">所属环境</span>
						</div>
						<el-select 
						  v-model="envServiceSearch.env" 
						  placeholder="请选择所属环境" 
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
					  <el-form-item class="inline-form-item">
						<div class="inline-label-wrapper">
						  <i class="icon-service"></i>
						  <span class="inline-label-text">所属服务</span>
						</div>
						<el-select 
						  v-model="envServiceSearch.service" 
						  placeholder="请选择所属服务" 
						  clearable
						  filterable
						  class="select"
						  size='large'
						  popper-class='select-dropdown-rounded'
						>
						  <el-option 
							v-for="service_obj in service_list_no_limit.results" 
							:key="service_obj.id"
							:label="service_obj.name" 
							:value="service_obj.id" 
						  />
						</el-select>
					  </el-form-item>
					</el-col>
					
					<!-- <el-col :xs="24" :sm="12" :md="8" :lg="6">
					  <el-form-item class="inline-form-item">
						<div class="inline-label-wrapper">
						  <i class="icon-product"></i>
						  <span class="inline-label-text">所属产品</span>
						</div>
						<el-select 
						  v-model="envServiceSearch.plant" 
						  placeholder="请选择所属产品" 
						  clearable
						  filterable
						  class="select"
						  size='large'
						  popper-class='select-dropdown-rounded'
						>
						  <el-option 
							v-for="plant_obj in plant_list.results" 
							:key="plant_obj.id"
							:label="plant_obj.name" 
							:value="plant_obj.id" 
						  />
						</el-select>
					  </el-form-item>
					</el-col> -->
					
					<el-col :xs="24" :sm="12" :md="8" :lg="6">
					  <el-form-item class="inline-form-item">
						<div class="inline-label-wrapper">
						  <i class="icon-creator"></i>
						  <span class="inline-label-text">创建人</span>
						</div>
						<el-select 
						  v-model="envServiceSearch.create_by" 
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
					  <el-form-item class="inline-form-item">
						<div class="inline-label-wrapper">
						  <i class="icon-updater"></i>
						  <span class="inline-label-text">更新人</span>
						</div>
						<el-select 
						  v-model="envServiceSearch.update_by" 
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
			        <h3 class="content-title">服务域名配置列表</h3>
			        <div class="stats-info">
			          <div class="stat-item">
			            <span class="stat-label">总计</span>
			            <span class="stat-value">
			              {{ envServiceList.count || 0 }}
			            </span>
			          </div>
			          <div class="stat-item">
			            <span class="stat-label">当前页</span>
			            <span class="stat-value">
			              {{ page_size_params.page }}
			            </span>
			          </div>
			        </div>
			      </div>
			      <el-button 
			        v-if="permission.has_add_permission" 
			        @click="addEnvService()" 
			        type="primary" 
			        class="add-btn"
			      >
			        <el-icon><Plus /></el-icon>
			       新增服务域名配置
			      </el-button>
			    </div>
			  </div>
			
			  <!-- Tab标签页 - 修复位置 -->
			  <div class="tab-container">
				<div class="table-container">
				  <div class="table-wrapper">
					<el-table 
					  :data="envServiceList.results" 
					  :max-height="'calc(100vh - 540px)'" 
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
					  >
						<template #default="scope">
						  <div class="index-cell">
							{{ scope.$index + 1 + (page_size_params.page - 1) * page_size_params.size }}
						  </div>
						</template>
					  </el-table-column>
					  
					  <el-table-column 
						label="配置信息" 
						min-width="300" 
						align="center"
						class-name="config-column"
					  >
						<template #default="scope">
						  <div class="config-cell">
							<div class="config-row">
							  <div class="config-label">
								<i class="icon-environment-cell"></i>
								<span>环境</span>
							  </div>
							  <div class="config-value">
								<el-tag 
								  :type="getEnvType(scope.row.env_name)"
								  effect="light"
								  size="small"
								>
								  {{ scope.row.env_name }}
								</el-tag>
							  </div>
							</div>
							<div class="config-row">
							  <div class="config-label">
								<i class="icon-service-cell"></i>
								<span>服务</span>
							  </div>
							  <div class="config-value">
								<el-tag type="primary" effect="light" size="small">
								  {{ scope.row.service_name }}
								</el-tag>
							  </div>
							</div>
							<div class="config-row">
							  <div class="config-label">
								<i class="icon-product-cell"></i>
								<span>域名</span>
							  </div>
							  <div class="config-value">
								<el-tag type="success" effect="light" size="small">
								  {{ scope.row.host }}
								</el-tag>
							  </div>
							</div>
							<!-- <div class="config-row">
							  <div class="config-label">
								<i class="icon-rule-cell"></i>
								<span>规则数</span>
							  </div>
							  <div class="config-value">
								<span class="rule-count">{{ scope.row.host_rules?.length || 0 }} 条</span>
							  </div>
							</div> -->
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
							  content="查看配置" 
							  placement="top" 
							  effect="dark"
							>
							  <el-button 
								type="success" 
								v-if="permission.has_read_permission" 
								class="action-btn view-btn"
								@click.stop="viewEnvService(scope.row)"
								circle
							  >
								<el-icon><View /></el-icon>
							  </el-button>
							</el-tooltip>
							
							<el-tooltip 
							  content="编辑配置" 
							  placement="top" 
							  effect="dark"
							>
							  <el-button 
								type="warning" 
								v-if="permission.has_edit_permission" 
								class="action-btn edit-btn"
								@click.stop="editEnvService(scope.row)"
								circle
							  >
								<el-icon><EditPen /></el-icon>
							  </el-button>
							</el-tooltip>
							
							<el-tooltip 
							  content="删除配置" 
							  placement="top" 
							  effect="dark"
							>
							  <el-button 
								type="danger" 
								v-if="permission.has_delete_permission" 
								@click.stop="deleteEnvService(scope.row.id)" 
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
					  :total="envServiceList.count"
					  @size-change="handleSizeEnvChange"
					  @current-change="handleCurrentEnvChange"
					  class="select input"
					  style='float: right;'
					  :background="true"
					/>
				  </div>
				</div>
			  </div>
			</el-card>
			
		</el-tab-pane>
	  </el-tabs>
	</el-card>

    <!-- 服务表单对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      :title="title" 
      width="500"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form 
          :model="serviceSave" 
          :rules="serviceRules" 
          ref="serviceRef"
          label-position="top" 
          :disabled="serviceView"
          class="dialog-form"
        >
          <el-form-item prop="name" class="dialog-form-item">
            <label class="dialog-label">
              <i class="icon-service-dialog"></i>
              服务名称
            </label>
            <el-input 
              v-model="serviceSave.name" 
              autocomplete="off" 
              placeholder="请输入服务名称"
              class="input"
			  size='large'
              :maxlength="50"
              show-word-limit
            />
          </el-form-item>
		  <el-form-item prop="is_server_host" class="dialog-form-item">
		    <label class="dialog-label">
		      <i class="icon-service-dialog"></i>
		      接口域名配置
		    </label>
		    <el-select
		      v-model="serviceSave.is_server_host" 
		      placeholder="请选择接口请求域名配置" 
		      class="select"
		      size='large'
		      popper-class='select-dropdown-rounded'
		    >
		      <el-option label="接口请求跟随服务域名配置" :value="true" />
			  <el-option label="接口请求跟随产品域名配置" :value="false" />
		    </el-select>
		  </el-form-item>
        </el-form>
      </div>
      
	  <template #footer>
	  	<span class="dialog-footer" v-if="!serviceView">
	  		<el-button @click="editDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
	  		<el-button 
	  		  v-if="permission.has_add_permission || permission.has_edit_permission" 
	  		  type="primary" 
	  		  @click="save" 
	  		  class="dialog-confirm-btn"
	  		>
	  		  保存
	  		</el-button>
	  	</span>
	  </template>
    </el-dialog>

    <!-- 接口域名配置表单对话框 -->
    <el-dialog 
      v-model="envEditDialogVisible" 
      :title="title" 
      width="600"
      class="elegant-dialog wide-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form 
          :model="envServiceSave" 
          :rules="envServiceRules" 
          ref="envServiceRef"
          label-position="top" 
          :disabled="envServiceView"
          class="dialog-form"
        >
          <el-form-item prop="env" class="dialog-form-item">
            <label class="dialog-label">
              <i class="icon-environment-dialog"></i>
              环境名称
            </label>
            <el-select 
              v-model="envServiceSave.env" 
              placeholder="请选择所属环境" 
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
          
          <el-form-item prop="service" class="dialog-form-item">
            <label class="dialog-label">
              <i class="icon-service-dialog"></i>
              服务名称
            </label>
            <el-select 
              v-model="envServiceSave.service" 
              placeholder="请选择所属服务" 
              clearable
              class="select"
              size='large'
              popper-class='select-dropdown-rounded'
            >
              <el-option 
                v-for="service_obj in service_list_no_limit.results" 
                :key="service_obj.id"
                :label="service_obj.name" 
                :value="service_obj.id" 
              />
            </el-select>
          </el-form-item>
          
          <el-form-item prop="host" class="dialog-form-item">
            <label class="dialog-label">
              <i class="icon-host"></i>
              请求域名
            </label>
            <el-input
              v-model="envServiceSave.host" 
              autocomplete="off" 
              placeholder="请输入接口请求域名，如：example.com"
              class="input"
              size='large'
              :maxlength="200"
              show-word-limit
            />
          </el-form-item>
          
         <!-- <div class="rules-section">
            <div class="rules-header">
              <h4 class="rules-title">
                <i class="icon-rules-dialog"></i>
                服务域名匹配规则
              </h4>
              <el-tooltip 
                placement="right" 
                effect="light"
                raw-content
              >
                <template #content>
                  <div class="rules-tooltip-content">
                    <h4>匹配规则说明</h4>
                    <ul>
                      <li><strong>匹配机制</strong>：用例执行时，根据选择的环境、步骤所属产品、接口所属服务，匹配对应的域名配置，再通过接口路径匹配具体域名地址。</li>
                      <li><strong>规则优先级</strong>：默认第一行优先级最低，最后一行最高。**为默认全局匹配规则。</li>
                      <li><strong>前缀匹配</strong>：如 <code>/api/user/</code> 匹配所有以该路径开头的接口。</li>
                      <li><strong>精准匹配</strong>：如 <code>/api/user/login</code> 仅匹配该路径接口。</li>
                    </ul>
                  </div>
                </template>
                <el-icon class="rules-info-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </div> -->
            
          <!--  <el-form-item prop="host_rules" class="rules-form-item">
              <HostRules :tableData='envServiceSave.host_rules'></HostRules>
            </el-form-item> -->
          <!-- </div> -->
        </el-form>
      </div>
      <template #footer>
      	<span class="dialog-footer" v-if="!envServiceView">
      		<el-button @click="envEditDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
      		<el-button 
      		  v-if="permission.has_add_permission || permission.has_edit_permission" 
      		  type="primary" 
      		  @click="saveEnvService" 
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
import { mapState, mapActions } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Search,
  Plus,
  View,
  Delete,
  EditPen,
  InfoFilled
} from '@element-plus/icons-vue'
import HostRules from '../../components/HostRules.vue'
import * as common from '../../utils/common.js'

export default {
  name: 'ServiceManagement',
  components: {
    HostRules,
    Refresh,
    Search,
    Plus,
    View,
    Delete,
    EditPen,
    InfoFilled
  },
  computed: {
    ...mapState(['pathPermission', 'projectInfo', 'userInfo']),
    calcMinWidth() {
      let visibleButtons = 0
      if (this.permission.has_read_permission) visibleButtons += 1
      if (this.permission.has_edit_permission) visibleButtons += 1
      if (this.permission.has_delete_permission) visibleButtons += 1
      return Math.max(10, visibleButtons * 48)
    }
  },
  data() {
    return {
      serviceView: false,
      envServiceView: false,
      permission: {},
      serviceSearch: {
        name: '',
        project: '',
        create_by: '',
        update_by: ''
      },
      envServiceSearch: {
        project: '',
        plant: '',
        env: '',
        service: '',
        create_by: '',
        update_by: ''
      },
      page_size_params: {
        page: 1,
        size: 10
      },
	  sort_params: {
	    ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
	  },
      activeName: 'service',
      title: '新增服务',
      isAdd: true,
      editDialogVisible: false,
      envEditDialogVisible: false,
      service_list: {
        count: 0,
        results: []
      },
      service_list_no_limit: {
        count: 0,
        results: []
      },
      env_list: {
        count: 0,
        results: []
      },
      plant_list: {
        count: 0,
        results: []
      },
      envServiceList: {
        count: 0,
        results: []
      },
      user_list: [],
      serviceSave: {
        id: '',
        project: '',
		is_server_host: false,
        name: ''
      },
      serviceRules: {
        name: [{
          required: true,
          message: '服务名称不能为空',
          trigger: 'blur'
        }, {
          min: 1,
          max: 50,
          message: '服务名称长度在 1 到 50 个字符',
          trigger: 'blur'
        }]
      },
      envServiceSave: {
        id: '',
        host_rules: [],
        env: '',
        service: '',
        plant: ''
      },
      envServiceRules: {
        host_rules: [{
          validator: (rule, value, callback) => {
            if (!value || value.length === 0) {
              callback(new Error('服务域名匹配规则不能为空'))
            } else if (common.hasEmptyValues(value, ['host', 'rule', 'method'])) {
              callback(new Error('请完善服务域名匹配规则表格，所有字段都必填'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }],
        env: [{
          required: true,
          message: '请选择所属环境',
          trigger: 'change'
        }],
        service: [{
          required: true,
          message: '请选择所属服务',
          trigger: 'change'
        }],
        host: [{
          required: true,
          message: '请输入请求域名',
          trigger: 'blur'
        }]
      }
    }
  },
  methods: {
    ...mapActions(['check_permission']),
    
    handleCurrentChange(page) {
      this.page_size_params.page = page
      this.getServices()
    },
    
    handleCurrentEnvChange(page) {
      this.page_size_params.page = page
      this.getEnvServices()
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
    
    handleSizeChange(size) {
      this.page_size_params.size = size
      this.page_size_params.page = 1
      this.getServices()
    },
    
    handleSizeEnvChange(size) {
      this.page_size_params.size = size
      this.page_size_params.page = 1
      this.getEnvServices()
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
	  if (this.activeName ==='service'){
		  this.getServices()
	  }else{
		  this.getEnvServices()
	  }
	},
    
    handleClick(tab) {
      this.page_size_params.page = 1
      if (tab.paneName === 'first') {
        this.getServices()
      } else {
        this.getEnvServices()
      }
    },
    
    getServiceType(serviceName) {
      if (!serviceName) return 'info'
      const colors = ['primary', 'success', 'warning', 'danger', 'info']
      const hash = serviceName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
      return colors[hash % colors.length]
    },
    
    getEnvType(envName) {
      if (!envName) return ''
      const colors = ['', 'success', 'info', 'warning', 'danger']
      const hash = envName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
      return colors[hash % colors.length]
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
    
    search() {
      this.page_size_params.page = 1
      this.getServices()
    },
    
    reset() {
      for (let key in this.serviceSearch) {
        this.serviceSearch[key] = ''
      }
    },
    
    searchEnv() {
      this.page_size_params.page = 1
      this.getEnvServices()
    },
    
    resetEnv() {
      for (let key in this.envServiceSearch) {
        this.envServiceSearch[key] = ''
      }
    },
    
    editService(row_data) {
      this.isAdd = false
      this.title = '编辑服务'
      this.serviceView = false
      this.getService(row_data.id)
      this.editDialogVisible = true
      this.$nextTick(() => {
        if (this.$refs.serviceRef) {
          this.$refs.serviceRef.clearValidate()
        }
      })
    },
    
    viewService(row_data) {
      this.isAdd = false
      this.title = '查看服务'
      this.serviceView = true
      this.getService(row_data.id)
      this.editDialogVisible = true
    },
    
    addService() {
      this.serviceSave = {
        project: this.projectInfo.id,
		is_server_host: false,
        name: ''
      }
      this.title = '新增服务'
      this.serviceView = false
      this.editDialogVisible = true
      this.isAdd = true
      this.$nextTick(() => {
        if (this.$refs.serviceRef) {
          this.$refs.serviceRef.resetFields()
        }
      })
    },
    
    editEnvService(row_data) {
      this.isAdd = false
      this.title = '编辑服务域名配置'
      this.envServiceView = false
      this.envServiceSave = { ...row_data }
      this.envEditDialogVisible = true
      this.$nextTick(() => {
        if (this.$refs.envServiceRef) {
          this.$refs.envServiceRef.clearValidate()
        }
      })
    },
    
    viewEnvService(row_data) {
      this.isAdd = false
      this.title = '查看服务域名配置'
      this.envServiceView = true
      this.envServiceSave = { ...row_data }
      this.envEditDialogVisible = true
    },
    
    addEnvService() {
      this.envServiceSave = {
        project: this.projectInfo.id,
        host_rules: [],
        env: '',
        service: '',
        plant: ''
      }
      this.title = '新增服务域名配置'
      this.envServiceView = false
      this.envEditDialogVisible = true
      this.isAdd = true
      this.$nextTick(() => {
        if (this.$refs.envServiceRef) {
          this.$refs.envServiceRef.resetFields()
        }
      })
    },
    
    save() {
      this.$refs.serviceRef.validate(async (valid) => {
        if (valid) {
          if (this.isAdd) {
            await this.createService()
          } else {
            await this.updateService()
          }
        }
      })
    },
    
    saveEnvService() {
      this.$refs.envServiceRef.validate(async (valid) => {
        if (valid) {
          if (this.isAdd) {
            await this.createEnvService()
          } else {
            await this.updateEnvService()
          }
        }
      })
    },
    
    async createService() {
      try {
        const response = await this.$api.createService(this.serviceSave)
        if (response.status === 201) {
          this.editDialogVisible = false
          this.getServices()
          this.getServicesNoLimit()
          ElMessage({
            message: "保存成功",
            type: 'success'
          })
        }
      } catch (error) {
        console.error('创建服务失败:', error)
      }
    },
    
    async createEnvService() {
      try {
        const response = await this.$api.createEnvService(this.envServiceSave)
        if (response.status === 201) {
          this.envEditDialogVisible = false
          this.getEnvServices()
          ElMessage({
            message: "保存成功",
            type: 'success'
          })
        }
      } catch (error) {
        console.error('创建服务域名配置失败:', error)
      }
    },
    
    async updateService() {
      try {
        const response = await this.$api.updateService(this.serviceSave.id, this.serviceSave)
        if (response.status === 200) {
          this.editDialogVisible = false
          this.getServices()
          this.getServicesNoLimit()
          ElMessage({
            message: "保存成功",
            type: 'success'
          })
        }
      } catch (error) {
        console.error('更新服务失败:', error)
      }
    },
    
    async updateEnvService() {
      try {
        const response = await this.$api.updateEnvService(this.envServiceSave.id, this.envServiceSave)
        if (response.status === 200) {
          this.envEditDialogVisible = false
          this.getEnvServices()
          ElMessage({
            message: "保存成功",
            type: 'success'
          })
        }
      } catch (error) {
        console.error('更新服务域名配置失败:', error)
      }
    },
    
    async deleteService(id) {
      ElMessageBox.confirm(
        '确定删除此服务？将级联删除其下的服务模块、接口文档与服务域名配置，删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deleteService(id)
        if (response.status === 204 || response.status === 200) {
          this.getServices()
          this.getServicesNoLimit()
          ElMessage({
            type: 'success',
            message: response.data?.msg || '删除成功'
          })
        }
      }).catch(() => {})
    },
    
    async deleteEnvService(id) {
      ElMessageBox.confirm(
        '确定删除此服务域名配置？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deleteEnvService(id)
        if (response.status === 204) {
          this.getEnvServices()
          ElMessage({
            type: 'success',
            message: '删除成功'
          })
        }
      }).catch(() => {})
    },
    
    async getService(id) {
      try {
        const response = await this.$api.getService(id)
        if (response.status === 200) {
          this.serviceSave = { ...response.data.result }
        }
      } catch (error) {
        console.error('获取服务详情失败:', error)
      }
    },
    
    async getServices() {
      const par = {
        page: this.page_size_params.page,
        size: this.page_size_params.size,
        project: this.projectInfo.id
      }
      const params = Object.assign(par, this.sort_params)
      if (this.serviceSearch.name) params.name = this.serviceSearch.name
      if (this.serviceSearch.create_by) params.create_by = this.serviceSearch.create_by
      if (this.serviceSearch.update_by) params.update_by = this.serviceSearch.update_by
      
      try {
        const response = await this.$api.getServices(params)
        if (response.status === 200) {
          this.service_list = { ...response.data }
        }
      } catch (error) {
        console.error('获取服务列表失败:', error)
      }
    },
    
    async getServicesNoLimit() {
      try {
        const response = await this.$api.getServices({ project: this.projectInfo.id })
        if (response.status === 200) {
          this.service_list_no_limit = { ...response.data }
        }
      } catch (error) {
        console.error('获取服务列表(无限制)失败:', error)
      }
    },
    
    async getEnvServices() {
      const par = {
        page: this.page_size_params.page,
        size: this.page_size_params.size,
        project: this.projectInfo.id
      }
      const params = Object.assign(par, this.sort_params)
      if (this.envServiceSearch.env) params.env = this.envServiceSearch.env
      if (this.envServiceSearch.service) params.service = this.envServiceSearch.service
      if (this.envServiceSearch.plant) params.plant = this.envServiceSearch.plant
      if (this.envServiceSearch.create_by) params.create_by = this.envServiceSearch.create_by
      if (this.envServiceSearch.update_by) params.update_by = this.envServiceSearch.update_by
      
      try {
        const response = await this.$api.getEnvServices(params)
        if (response.status === 200) {
          this.envServiceList = { ...response.data }
        }
      } catch (error) {
        console.error('获取服务域名配置列表失败:', error)
      }
    },

    async  check_permission(){
        const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission['/env/service']}
		const response = await this.$api.check_permission(params)
		if (response.status === 200){
			 this.permission = { ...response.data.result }
		}
	 },
    
    async getEnvs() {
      try {
        const response = await this.$api.getEnvs({ project: this.projectInfo.id })
        if (response.status === 200) {
          this.env_list = { ...response.data }
        }
      } catch (error) {
        console.error('获取环境列表失败:', error)
      }
    },
    
    async getPlants() {
      try {
        const response = await this.$api.getPlants({ project: this.projectInfo.id })
        if (response.status === 200) {
          this.plant_list = { ...response.data }
        }
      } catch (error) {
        console.error('获取产品列表失败:', error)
      }
    }
  },
  created() {
    this.check_permission()
    this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
    this.getServices()
    this.getServicesNoLimit()
    this.getPlants()
    this.getEnvServices()
    this.getEnvs()
  }
}
</script>

<style scoped>
.service-management-container {
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
}

.drawer-tabs >>> .el-tabs__header {
  margin: 0;
  padding: 0px 24px 0;
  background: var(--qm-bg-2);
  border-bottom: 1px solid var(--qm-bg-3);
}

.drawer-tabs >>> .el-tabs__nav-wrap::after {
  background-color: var(--qm-bg-3);
}

.drawer-tabs >>> .el-tabs__item {
  font-size: 16px;
  font-weight: 600;
  color: var(--qm-text-2);
  padding: 0 24px;
  height: 48px;
  line-height: 48px;
  transition: all 0.3s ease;
}

.drawer-tabs >>> .el-tabs__item:hover {
  color: #f59e0b;
}

.drawer-tabs >>> .el-tabs__item.is-active {
  color: var(--qm-text-1);
  position: relative;
}

.drawer-tabs >>> .el-tabs__item.is-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
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
  margin-bottom: 20px;
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
  padding: 15px 5px 10px 5px;
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
  padding: 25px 5px 0px 5px;
}

/* 内联表单样式 - 修复label和input不在一行的问题 */
.inline-form {
  margin-bottom: 0;
}

.inline-form-item {
   margin-bottom: 25px;
   gap: 10px;
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
   min-width: 80px;
   margin-right: 10px;
   flex-shrink: 0;
   white-space: nowrap;
}

.inline-label-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--qm-text-2);
  white-space: nowrap;
}

/* 自定义图标 */
.icon-service {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.icon-environment,
.icon-product,
.icon-creator,
.icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
}

.icon-environment { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-product { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-creator { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-updater { background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); }

/* 内联输入框样式 - 修复布局问题 */
.input-inline,
.select-inline {
  flex: 1;
  margin-left: 12px;
}

.input-inline >>> .el-input__inner,
.select-inline >>> .el-input__inner {
  border-radius: 10px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-1);
  padding: 0 15px;
  box-shadow: none;
  transition: all 0.3s ease;
  width: 100%;
  height: 40px;
  line-height: 40px;
}

.input-inline >>> .el-input__inner:hover,
.select-inline >>> .el-input__inner:hover {
  border-color: var(--qm-line-strong);
  background: var(--qm-bg-2);
}

.input-inline >>> .el-input__inner:focus,
.select-inline >>> .el-input__inner:focus {
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
  padding: 0;
  overflow: hidden;
}

::v-deep .content-card .el-card__body {
  padding: 0px;
}

.content-header {
  padding: 20px 24px;
  margin-top:20px;
  border-bottom: 1px solid var(--qm-bg-3);
  flex-shrink: 0;
}

::v-deep .filter-card .el-card__body {
  padding-bottom: 5px;
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

/* Tab容器 - 修复位置 */
.tab-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.content-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.content-tabs >>> .el-tabs__header {
  margin: 0 24px;
  padding-top: 10px;
  border-bottom: 1px solid var(--qm-bg-3);
  flex-shrink: 0;
}

.content-tabs >>> .el-tabs__nav-wrap::after {
  background-color: var(--qm-line-strong);
}

.content-tabs >>> .el-tabs__item {
  padding: 0 20px;
  height: 48px;
  line-height: 48px;
  font-weight: 500;
  color: var(--qm-text-2);
  transition: all 0.3s ease;
}

.content-tabs >>> .el-tabs__item:hover {
  color: #f59e0b;
}

.content-tabs >>> .el-tabs__item.is-active {
  color: #f59e0b;
  font-weight: 600;
  border-bottom: 2px solid #f59e0b;
}

.content-tabs >>> .el-tabs__content {
  flex: 1;
  padding: 0;
  min-height: 0;
  overflow: hidden;
}

.content-tabs >>> .el-tab-pane {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 表格容器 */
.table-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.table-wrapper {
  flex: 1;
  padding: 0 0px;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 优雅表格样式 */
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

/* 自定义单元格样式 */
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

.service-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.service-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 500;
  font-size: 13px;
  transition: all 0.3s ease;
  border-width: 2px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.service-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.icon-service-cell {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9h-4v4h-2v-4H9V9h4V5h2v4h4v2z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
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

/* 接口域名配置单元格 */
.config-cell {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px 0;
}

.config-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 4px 0;
}

.config-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--qm-text-2);
  min-width: 40px;
}

.config-value {
  font-size: 13px;
  color: var(--qm-text-1);
}

.rule-count {
  font-weight: 600;
  color: #f59e0b;
}

.icon-environment-cell,
.icon-service-cell,
.icon-product-cell,
.icon-host,
.icon-rule-cell {
  width: 12px;
  height: 12px;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-environment-cell {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM4 12c0-4.42 3.58-8 8-8 1.85 0 3.55.63 4.9 1.69L5.69 16.9C4.63 15.55 4 13.85 4 12zm8 8c-1.85 0-3.55-.63-4.9-1.69L18.31 7.1C19.37 8.45 20 10.15 20 12c0 4.42-3.58 8-8 8z'/%3E%3C/svg%3E");
}

.icon-product-cell {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z'/%3E%3C/svg%3E");
}

.icon-rule-cell {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z'/%3E%3C/svg%3E");
}

.icon-host {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z'/%3E%3C/svg%3E");
}


/* 操作按钮 */
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

/* 分页组件样式 */
.pagination-wrapper {
  padding: 20px 24px 0px 20px;
  border-top: 1px solid var(--qm-bg-3);
  flex-shrink: 0;
  display: block !important;
  min-height: 40px;
  background: var(--qm-bg-2);
  z-index: 10;
  position: relative;
  opacity: 1 !important;
  visibility: visible !important;
}

/* 对话框样式 */
.elegant-dialog >>> .el-dialog {
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.elegant-dialog.wide-dialog >>> .el-dialog {
  width: 1000px;
  max-width: 90vw;
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

.dialog-content {
  padding: 24px 0 24px 0;
}

.dialog-form {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dialog-form-grid {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-row .dialog-form-item {
  flex: 1;
}

.dialog-form-item {
  margin-bottom: 0;
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

/* 对话框图标 */
.icon-service-dialog,
.icon-environment-dialog,
.icon-product-dialog,
.icon-rules-dialog {
  width: 16px;
  height: 16px;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-service-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9h-4v4h-2v-4H9V9h4V5h2v4h4v2z'/%3E%3C/svg%3E");
}

.icon-environment-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM4 12c0-4.42 3.58-8 8-8 1.85 0 3.55.63 4.9 1.69L5.69 16.9C4.63 15.55 4 13.85 4 12zm8 8c-1.85 0-3.55-.63-4.9-1.69L18.31 7.1C19.37 8.45 20 10.15 20 12c0 4.42-3.58 8-8 8z'/%3E%3C/svg%3E");
}

.icon-product-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z'/%3E%3C/svg%3E");
}

.icon-rules-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z'/%3E%3C/svg%3E");
}

.dialog-input >>> .el-input__inner,
.dialog-select >>> .el-input__inner {
  border-radius: 12px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  padding: 0 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  width: 100%;
}

.dialog-input >>> .el-input__inner:hover,
.dialog-select >>> .el-input__inner:hover {
  border-color: var(--qm-line-strong);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-input >>> .el-input__inner:focus,
.dialog-select >>> .el-input__inner:focus {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.dialog-input >>> .el-input__count {
  color: var(--qm-text-3);
}

/* 规则区域样式 */
.rules-section {
  border: 1px solid var(--qm-line-strong);
  border-radius: 12px;
  padding: 20px;
  background: var(--qm-bg-1);
}

.rules-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.rules-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--qm-text-1);
  display: flex;
  align-items: center;
  gap: 8px;
}

.rules-info-icon {
  color: #10b981;
  cursor: help;
  font-size: 18px;
  transition: all 0.3s ease;
}

.rules-info-icon:hover {
  color: #059669;
  transform: scale(1.1);
}

.rules-tooltip-content {
  max-width: 400px;
  padding: 8px;
}

.rules-tooltip-content h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--qm-text-1);
}

.rules-tooltip-content ul {
  margin: 0;
  padding-left: 20px;
}

.rules-tooltip-content li {
  font-size: 12px;
  color: var(--qm-text-2);
  line-height: 1.5;
  margin-bottom: 4px;
}

.rules-tooltip-content li strong {
  color: var(--qm-text-2);
}

.rules-tooltip-content li code {
  background: var(--qm-line-strong);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 11px;
}

.rules-form-item {
  margin-bottom: 0;
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
  .service-management-container {
    padding: 16px;
  }
  
  .filter-card .filter-header,
  .filter-card .filter-form-wrapper,
  .content-card .content-header {
    padding: 16px 20px;
  }
  
  .table-wrapper {
    padding: 0 20px;
  }
}

@media screen and (max-width: 992px) {
  .elegant-dialog.wide-dialog >>> .el-dialog {
    width: 90vw;
    max-width: 90vw;
  }
  
  .form-row {
    flex-direction: column;
  }
}

@media screen and (max-width: 768px) {
  .service-management-container {
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
  
  /* 移动端内联表单样式 */
  .inline-form-item {
    height: auto;
    flex-wrap: wrap;
    margin-bottom: 16px;
  }
  
  .inline-label-wrapper {
    min-width: 80px;
    margin-bottom: 8px;
    width: 100%;
  }
  
  .input-inline,
  .select-inline {
    margin-left: 0;
    margin-top: 4px;
    width: 100%;
  }
  
  .input-inline >>> .el-input__inner,
  .select-inline >>> .el-input__inner {
    margin-left: 0;
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