<template>
  <div class="plant-management-container">
	  
	<el-card class="drawer-card elegant-shadow">
	  <el-tabs v-model="activeName" class="drawer-tabs" @tab-click="handleClick">
	    <el-tab-pane label="产品列表" name="plant" lazy='true'>
			
			<!-- 产品列表搜索区域 -->
			<el-card class="filter-card elegant-shadow" >
			  <div class="filter-header">
			    <div class="header-title-section">
			      <i class="icon-search"></i>
			      <h3 class="filter-title">产品筛选</h3>
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
			    <el-form :model="plantSearch" class="filter-form inline-form">
			      <el-row :gutter="24">
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="inline-form-item">
			            <div class="inline-label-wrapper">
			              <i class="icon-product"></i>
			              <span class="inline-label-text">产品名称</span>
			            </div>
			            <el-input 
			              v-model="plantSearch.name" 
			              placeholder="请输入产品名称" 
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
			              v-model="plantSearch.create_by" 
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
			              v-model="plantSearch.update_by" 
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
			        <h3 class="content-title">产品列表</h3>
			        <div class="stats-info">
			          <div class="stat-item">
			            <span class="stat-label">总计</span>
			            <span class="stat-value">{{ plant_list.count || 0 }}</span>
			          </div>
			          <div class="stat-item">
			            <span class="stat-label">当前页</span>
			            <span class="stat-value">{{ page_size_params.page }}</span>
			          </div>
			        </div>
			      </div>
			      <el-button 
			        v-if="permission.has_add_permission" 
			        @click="addPlant()" 
			        type="primary" 
			        class="add-btn"
			      >
			        <el-icon><Plus /></el-icon>新增产品
			      </el-button>
			    </div>
			  </div>
			
			  <!-- 数据表格 -->
			  <div class="table-wrapper">
			    <!-- 产品列表表格 -->
			    <el-table 
			      :data="plant_list.results" 
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
			      >
			        <template #default="scope">
			          <div class="index-cell">
			            {{ scope.$index + 1 + (page_size_params.page - 1) * page_size_params.size }}
			          </div>
			        </template>
			      </el-table-column>
			      
			      <el-table-column 
			        label="产品名称" 
			        prop="name" 
			        min-width="150" 
			        align="center"
			        class-name="name-column"
			      >
			        <template #default="scope">
			          <div class="name-cell">
			            <el-tag 
			              :type="getProductTypeTag(scope.row.type)"
			              effect="light"
			              class="product-badge"
			            >
			              <span class="product-icon">
			                <i :class="getProductIcon(scope.row.type)"></i>
			              </span>
			              {{ scope.row.name }}
			            </el-tag>
			          </div>
			        </template>
			      </el-table-column>
			      
			      <el-table-column 
			        label="产品类型" 
			        prop="type_name" 
			        width="150" 
			        align="center"
			        class-name="type-column"
			      >
			        <template #default="scope">
			          <el-tag 
			            :type="getProductTypeTag(scope.row.type)"
			            effect="plain"
			            class="type-tag"
			          >
			            {{ scope.row.type_name }}
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
			              content="查看产品" 
			              placement="top" 
			              effect="dark"
			            >
			              <el-button 
			                type="success" 
			                v-if="permission.has_read_permission" 
			                class="action-btn view-btn"
			                @click.stop="viewPlant(scope.row)"
			                circle
			              >
			                <el-icon><View /></el-icon>
			              </el-button>
			            </el-tooltip>
			            
			            <el-tooltip 
			              content="编辑产品" 
			              placement="top" 
			              effect="dark"
			            >
			              <el-button 
			                type="warning" 
			                v-if="permission.has_edit_permission" 
			                class="action-btn edit-btn"
			                @click.stop="editPlant(scope.row)"
			                circle
			              >
			                <el-icon><EditPen /></el-icon>
			              </el-button>
			            </el-tooltip>
			            
			            <el-tooltip 
			              content="删除产品" 
			              placement="top" 
			              effect="dark"
			            >
			              <el-button 
			                type="danger" 
			                v-if="permission.has_delete_permission" 
			                @click.stop="deletePlant(scope.row.id)" 
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
			      :total="plant_list.count"
			      @size-change="handleSizeChange"
			      @current-change="handleCurrentChange"
			      class="select input"
			      :background="true"
			    />
			  </div>
			</el-card>
			
		</el-tab-pane>
		<el-tab-pane label="产品域名配置" name="plant_env" lazy='true'>
			
			<!-- 产品环境列表搜索区域 -->
			<el-card class="filter-card elegant-shadow" v-if='activeName !== "first"'>
			  <div class="filter-header">
			    <div class="header-title-section">
			      <i class="icon-search"></i>
			      <h3 class="filter-title">产品域名配置筛选</h3>
			      <el-tag size="small" type="info" effect="plain">精准查询</el-tag>
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
			    <el-form :model="envPlantSearch" class="filter-form inline-form">
			      <el-row :gutter="24">
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="inline-form-item">
			            <div class="inline-label-wrapper">
			              <i class="icon-plant"></i>
			              <span class="inline-label-text">产品名称</span>
			            </div>
			            <el-select 
			              v-model="envPlantSearch.plant" 
			              placeholder="请选择产品" 
			              clearable
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
			        </el-col>
			        
			        <el-col :xs="24" :sm="12" :md="8" :lg="6">
			          <el-form-item class="inline-form-item">
			            <div class="inline-label-wrapper">
			              <i class="icon-env"></i>
			              <span class="inline-label-text">环境名称</span>
			            </div>
			            <el-select 
			              v-model="envPlantSearch.env" 
			              placeholder="请选择环境" 
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
			          <el-form-item class="inline-form-item">
			            <div class="inline-label-wrapper">
			              <i class="icon-creator"></i>
			              <span class="inline-label-text">创建人</span>
			            </div>
			            <el-select 
			              v-model="envPlantSearch.create_by" 
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
			              v-model="envPlantSearch.update_by" 
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
			        <h3 class="content-title">产品域名配置</h3>
			        <div class="stats-info">
			          <div class="stat-item">
			            <span class="stat-label">总计</span>
			            <span class="stat-value">{{ envPlantList.count || 0 }}</span>
			          </div>
			          <div class="stat-item">
			            <span class="stat-label">当前页</span>
			            <span class="stat-value">{{ page_size_params.page }}</span>
			          </div>
			        </div>
			      </div>
			      <el-button 
			        v-if="permission.has_add_permission" 
			        @click="addEnvPlant()" 
			        type="primary" 
			        class="add-btn"
			      >
			        <el-icon><Plus /></el-icon>新增产品域名配置
			      </el-button>
			    </div>
			  </div>
			
			  <!-- 数据表格 -->
			  <div class="table-wrapper">
			   
			    <!-- 产品环境列表表格 -->
			    <el-table 
			      :data="envPlantList.results" 
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
			      >
			        <template #default="scope">
			          <div class="index-cell">
			            {{ scope.$index + 1 + (page_size_params.page - 1) * page_size_params.size }}
			          </div>
			        </template>
			      </el-table-column>
			      
			      <el-table-column
			        label="产品类型" 
			        prop="type_name" 
			        width="150" 
			        align="center"
			        class-name="type-column"
			      >
			        <template #default="scope">
			          <el-tag 
			            :type="getProductTypeTag(scope.row.type)"
			            effect="plain"
			            class="type-tag"
			          >
			            {{ scope.row.type_name }}
			          </el-tag>
			        </template>
			      </el-table-column>
			      
			     
			      
			      <el-table-column 
			        label="产品配置信息" 
			        min-width="250" 
			        align="center"
			        class-name="app-info-column"
			      >
			        <template #default="scope">
			          <div  class="app-info-cell">
						<div  class="empty-cell app-info-item">
						  <div class="app-info-label">域名：</div>
						  <el-link
							:href="scope.row.host.startsWith('http') ? scope.row.host : `http://${scope.row.host}`" 
							target="_blank" 
							type="primary"
							
						  >
							<i class="icon-link"></i>
							{{ scope.row.host }}
						  </el-link>
						</div>
			            <div class="app-info-item" v-if="scope.row.type === 2">
			              <div class="app-info-label">包名：</div>
			              <div class="app-info-value">{{ scope.row.package || '-' }}</div>
			            </div>
			            <div class="app-info-item" v-if="scope.row.type === 2">
			              <div class="app-info-label">Activity：</div>
			              <div class="app-info-value">{{ scope.row.activity || '-' }}</div>
			            </div>
			          </div>
			        </template>
			      </el-table-column>
			      
			      <el-table-column 
			        label="所属产品" 
			        prop="plant_name" 
			        min-width="120" 
			        align="center"
			        class-name="plant-column"
			      />
			      
			      <el-table-column 
			        label="所属环境" 
			        prop="env_name" 
			        min-width="140" 
			        align="center"
			        class-name="env-column"
			      >
			        <template #default="scope">
			          <el-tag 
			            :type="getEnvTypeTag(scope.row.env)"
			            effect="light"
			            class="env-tag"
			          >
			            {{ scope.row.env_name }}
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
			              content="查看产品环境" 
			              placement="top" 
			              effect="dark"
			            >
			              <el-button 
			                type="success" 
			                v-if="permission.has_read_permission" 
			                class="action-btn view-btn"
			                @click.stop="viewEnvPlant(scope.row)"
			                circle
			              >
			                <el-icon><View /></el-icon>
			              </el-button>
			            </el-tooltip>
			            
			            <el-tooltip 
			              content="编辑产品环境" 
			              placement="top" 
			              effect="dark"
			            >
			              <el-button 
			                type="warning" 
			                v-if="permission.has_edit_permission" 
			                class="action-btn edit-btn"
			                @click.stop="editEnvPlant(scope.row)"
			                circle
			              >
			                <el-icon><EditPen /></el-icon>
			              </el-button>
			            </el-tooltip>
			            
			            <el-tooltip 
			              content="删除产品环境" 
			              placement="top" 
			              effect="dark"
			            >
			              <el-button 
			                type="danger" 
			                v-if="permission.has_delete_permission" 
			                @click.stop="deleteEnvPlant(scope.row.id)" 
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
			      :total="envPlantList.count"
			      @size-change="handleEnvSizeChange"
			      @current-change="handleEnvCurrentChange"
			      class="select input"
			      :background="true"
			    />
			  </div>
			</el-card>
			
		</el-tab-pane>
	  </el-tabs>
	</el-card>
    
    <!-- 产品表单对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      :title="title" 
      width="600"
      class="elegant-dialog"
      :close-on-click-modal="false"
      @close="handleDialogClose('plant')"
    >
      <div class="dialog-content">
        <el-form 
          :model="plantSave" 
          :rules="plantRules" 
          ref="plantRef"
          label-position="top" 
          :disabled="plantView"
          class="dialog-form"
        >
          <!-- 改为每个字段一行 -->
          <el-form-item prop="name" class="dialog-form-item-full">
            <div class="dialog-label">
              <i class="icon-product-dialog"></i>
              产品名称
            </div>
            <el-input 
              v-model="plantSave.name" 
              autocomplete="off" 
              placeholder="请输入产品名称"
              class="input"
              size='large'
              :maxlength="20"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item prop="type" class="dialog-form-item-full">
            <div class="dialog-label">
              <i class="icon-type-dialog"></i>
              产品类型
            </div>
            <el-select 
              v-model="plantSave.type" 
              placeholder="请选择产品类型"
              class="select"
              size='large'
              popper-class='select-dropdown-rounded'
            >
              <el-option label="WEB" :value="1" />
              <el-option label="PHONE_APP" :value="2" />
              <el-option label="H5" :value="3" />
              <el-option label="MINI" :value="4" />
              <el-option label="DESKTOP_APP" :value="5" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
      	<span class="dialog-footer" v-if="!plantView">
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

    <!-- 产品环境表单对话框 -->
    <el-dialog 
      v-model="envEditDialogVisible" 
      :title="title" 
      width="600"
      class="elegant-dialog"
      :close-on-click-modal="false"
      @close="handleDialogClose('envPlant')"
    >
      <div class="dialog-content">
        <el-form 
          :model="envPlantSave" 
          :rules="plantEnvRules" 
          ref="plantEnvRef"
          label-position="top" 
          :disabled="envPlantView"
          class="dialog-form"
        > 
		
		  <el-form-item prop="plant" class="dialog-form-item-full">
		    <div class="dialog-label">
		      <i class="icon-plant-dialog"></i>
		      所属产品
		    </div>
		    <el-select 
		      v-model="envPlantSave.plant" 
		      placeholder="请选择所属产品"
		      class="select"
		      size='large'
		      popper-class='select-dropdown-rounded'
		      :disabled="!isEnvAdd"
			  @change="handleEnvTypeChange"
		    >
		      <el-option 
		        v-for="plant_obj in plant_list.results" 
		        :key="plant_obj.id"
		        :label="plant_obj.name" 
		        :value="plant_obj.id" 
		      />
		    </el-select>
		  </el-form-item>
		  
          <!-- 改为每个字段一行 -->
          <el-form-item  class="dialog-form-item-full">
            <div class="dialog-label">
              <i class="icon-type-dialog"></i>
              产品类型
            </div>
            <el-select 
              v-model="selectedPlantType" 
              placeholder="请选择产品类型"
              class="select"
              size='large'
              popper-class='select-dropdown-rounded'
			  disabled
            >
              <el-option label="WEB" :value="1" />
              <el-option label="PHONE_APP" :value="2" />
			  <el-option label="H5" :value="3" />
			  <el-option label="MINI" :value="4" />
			  <el-option label="DESKTOP_APP" :value="5" />
            </el-select>
          </el-form-item>
          
          <el-form-item prop="env" class="dialog-form-item-full">
            <div class="dialog-label">
              <i class="icon-env-dialog"></i>
              所属环境
            </div>
            <el-select 
              v-model="envPlantSave.env" 
              placeholder="请选择所属环境"
              class="select"
              size='large'
              popper-class='select-dropdown-rounded'
              :disabled="!isEnvAdd"
            >
              <el-option 
                v-for="env_obj in env_list.results" 
                :key="env_obj.id"
                :label="env_obj.name" 
                :value="env_obj.id" 
              />
            </el-select>
          </el-form-item>
          
          <div v-if="selectedPlantType === 1" class="web-config-section">
            <div class="section-title">
              <i class="icon-web"></i>
              <span>WEB配置</span>
            </div>
            <el-form-item prop="host" class="dialog-form-item-full">
              <div class="dialog-label">
                <i class="icon-host"></i>
                产品域名
              </div>
              <el-input 
                v-model="envPlantSave.host" 
                autocomplete="off" 
                placeholder="请输入WEB产品域名，如：example.com"
                class="input"
                size='large'
                :maxlength="200"
                show-word-limit
              />
            </el-form-item>
          </div>
          
          <div v-if="selectedPlantType === 2 || selectedPlantType === 3 || selectedPlantType === 4" class="app-config-section">
            <div class="section-title">
              <i class="icon-app"></i>
              <span>APP配置</span>
            </div>
			
			<el-form-item prop="host" class="dialog-form-item-full">
			  <div class="dialog-label">
			    <i class="icon-host"></i>
			    接口请求域名
			  </div>
			  <el-input 
			    v-model="envPlantSave.host" 
			    autocomplete="off" 
			    placeholder="请输入接口请求域名，如：example.com"
			    class="input"
			    size='large'
			    :maxlength="200"
			    show-word-limit
			  />
			</el-form-item>
			
            <el-form-item prop="package" class="dialog-form-item-full" v-if="selectedPlantType === 2">
              <div class="dialog-label">
                <i class="icon-package"></i>
                APP包名
              </div>
              <el-input 
                v-model="envPlantSave.package" 
                autocomplete="off" 
                placeholder="请输入APP产品包名，如：com.example.app"
                class="input"
                size='large'
                :maxlength="100"
                show-word-limit
              />
            </el-form-item>
            
            <el-form-item prop="activity" class="dialog-form-item-full" v-if="selectedPlantType === 2">
              <div class="dialog-label">
                <i class="icon-activity"></i>
                主入口Activity
              </div>
              <el-input 
                v-model="envPlantSave.activity" 
                autocomplete="off" 
                placeholder="请输入主入口activity名，如：com.example.app.MainActivity"
                class="input"
                size='large'
                :maxlength="100"
                show-word-limit
              />
            </el-form-item>
          </div>
        </el-form>
      </div>
      <template #footer>
      	<span class="dialog-footer" v-if="!envPlantView">
      		<el-button @click="envEditDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
      		<el-button 
      		  v-if="permission.has_add_permission || permission.has_edit_permission" 
      		  type="primary" 
      		  @click="saveEnvPlant" 
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
  EditPen
} from '@element-plus/icons-vue'

export default {
  name: 'PlantManagement',
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
      plantView: false,
      envPlantView: false,
      permission: {},
      plantSearch: {
        name: '',
        project: '',
        create_by: '',
        update_by: ''
      },
      envPlantSearch: {
        project: '',
        env: '',
        plant: '',
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
      activeName: 'plant',
      title: '新增产品',
	  selectedPlantType: '',
      envTitle: '新增产品环境',
      isAdd: true,
      isEnvAdd: true,
      editDialogVisible: false,
      envEditDialogVisible: false,
      plant_list: {
        count: 0,
        results: []
      },
      env_list: {
        count: 0,
        results: []
      },
      envPlantList: {
        count: 0,
        results: []
      },
      plantSave: {
        id: '',
        project: '',
        name: '',
        type: '',
      },
      plantRules: {
        name: [{
          required: true,
          message: '产品名称不能为空',
          trigger: 'blur',
        }],
        type: [{
          required: true,
          message: '请选择产品类型',
          trigger: 'change',
        }],
      },
      envPlantSave: {
        id: '',
        host: '',
        package: '',
        env: '',
        plant: '',
        activity: '',
      },
      plantEnvRules: {
        host: [{
          required: true,
          message: '域名不能为空',
          trigger: 'blur',
        }],
        package: [{
          required: true,
          message: 'APP产品包名不能为空',
          trigger: 'blur',
        }],
        env: [{
          required: true,
          message: '请选择所属环境',
          trigger: 'change',
        }],
        plant: [{
          required: true,
          message: '请选择所属产品',
          trigger: 'change',
        }],
        activity: [{
          required: true,
          message: 'APP产品主入口activity不能为空',
          trigger: 'blur',
        }],
      },
      user_list: [],
    }
  },
  components: {
    Refresh,
    Search,
    Plus,
    View,
    Delete,
    EditPen
  },
  methods: {
    ...mapActions(['getRolePermission', 'projectInfo', 'userInfo']),
    
    handleCurrentChange() {
      this.getPlants()
    },
    
    handleSizeChange() {
      this.getPlants()
    },
	
	handleEnvCurrentChange() {
	  this.getEnvPlants()
	},
	
	handleEnvSizeChange() {
	  this.getEnvPlants()
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
	  if (this.activeName ==='plant'){
		  this.getPlants()
	  }else if(this.activeName ==='plant_env'){
		  this.getEnvPlants()
	  }
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
    
    getProductTypeTag(type) {
      const typeMap = {
        1: 'primary',   // WEB
        2: 'success',   // PHONE_APP
        3: 'info',      // H5
        4: 'warning',   // MINI
        5: 'danger'     // DESKTOP_APP
      }
      return typeMap[type] || 'info'
    },
    
    getProductIcon(type) {
      const iconMap = {
        1: 'icon-web',
        2: 'icon-app',
        3: 'icon-h5',
        4: 'icon-mini',
        5: 'icon-desktop'
      }
      return iconMap[type] || 'icon-default'
    },
    
    getEnvTypeTag(envId) {
      if (!envId) return 'info'
      const hash = envId.toString().split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
      const colors = ['', 'success', 'warning', 'danger', 'info']
      return colors[hash % colors.length]
    },
    
	handleClick(tab) {
	    // 切换标签页时重置分页参数
	    this.page_size_params.page = 1
	    this.page_size_params.size = 10
	    
	    // 根据标签页加载对应的数据
	    switch (tab.props.name) {
	      case 'plant':
	        this.getPlants()
	        break
	      case 'plant_env':
	        this.getEnvPlants()
	        break
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
    
    search() {
      this.getPlants()
    },
    
    reset() {
      for (let key in this.plantSearch) {
        this.plantSearch[key] = ''
      }
    },
    
    searchEnv() {
      this.getEnvPlants()
    },
    
    resetEnv() {
      for (let key in this.envPlantSearch) {
        this.envPlantSearch[key] = ''
      }
    },
    
    handleEnvTypeChange(value) {
	  const selectedObj = this.plant_list.results.find(
	        item => item.id === value
	  );
	  console.log(selectedObj, 'obj')
	  this.selectedPlantType = selectedObj.type
      if (value === 0) {
        this.envPlantSave.package = ''
        this.envPlantSave.activity = ''
      } else if (value === 1) {
        this.envPlantSave.host = ''
      }
    },
    
    handleDialogClose(type) {
      if (type === 'envPlant') {
        this.$refs.plantEnvRef?.clearValidate()
      } else {
        this.$refs.plantRef?.clearValidate()
      }
    },
    
    editPlant(row_data) {
      this.editDialogVisible = true
      this.plantView = false
      this.isAdd = false
      this.title = '编辑产品'
      this.getPlant(row_data.id)
      this.$nextTick(() => {
        this.$refs.plantRef?.clearValidate()
      })
    },
    
    viewPlant(row_data) {
      this.editDialogVisible = true
      this.isAdd = false
      this.plantView = true
      this.title = '查看产品'
      this.getPlant(row_data.id)
    },
    
    addPlant() {
      this.plantSave = {
        project: this.projectInfo.id,
        name: '',
        type: ''
      }
      this.title = '新增产品'
      this.plantView = false
      this.editDialogVisible = true
      this.isAdd = true
      this.$nextTick(() => {
        this.$refs.plantRef?.resetFields()
      })
    },
    
    editEnvPlant(row_data) {
      this.isEnvAdd = false
      this.title = '编辑产品环境'
      this.envPlantView = false
      this.envEditDialogVisible = true
      this.getEnvPlant(row_data.id)
      this.$nextTick(() => {
        this.$refs.plantEnvRef?.clearValidate()
      })
    },
    
    viewEnvPlant(row_data) {
      this.isEnvAdd = false
      this.title = '查看产品环境'
      this.envPlantView = true
      this.envEditDialogVisible = true
      this.getEnvPlant(row_data.id)
    },
    
    addEnvPlant() {
      this.envEditDialogVisible = true
      this.envPlantSave = {
        project: this.projectInfo.id,
        host: '',
        type: null,
        package: '',
        env: '',
        plant: '',
        activity: '',
      }
      this.title = '新增产品环境'
      this.envPlantView = false
      this.isEnvAdd = true
      this.$nextTick(() => {
        this.$refs.plantEnvRef?.resetFields()
      })
    },
    
    save() {
      if (this.isAdd) {
        this.createPlant()
      } else {
        this.updatePlant()
      }
    },
    
    saveEnvPlant() {
      if (this.isEnvAdd) {
        this.createEnvPlant()
      } else {
        this.updateEnvPlant()
      }
    },
    
    async createPlant() {
      this.$refs['plantRef'].validate(async (valid) => {
        if (valid) {
          try {
            this.plantSave.project = this.projectInfo.id
            const response = await this.$api.createPlant(this.plantSave)
            if (response.status === 201) {
              this.editDialogVisible = false
              this.getPlants()
              ElMessage({
                message: "保存成功",
                type: 'success'
              })
            }
          } catch (error) {
            console.error('创建产品失败:', error)
          }
        }
      })
    },
    
    async createEnvPlant() {
      this.$refs['plantEnvRef'].validate(async (valid) => {
        if (valid) {
          try {
            const response = await this.$api.createEnvPlant(this.envPlantSave)
            if (response.status === 201) {
              this.envEditDialogVisible = false
              this.getEnvPlants()
              ElMessage({
                message: "保存成功",
                type: 'success'
              })
            }
          } catch (error) {
            console.error('创建产品环境失败:', error)
          }
        }
      })
    },
    
    async updatePlant() {
      this.$refs['plantRef'].validate(async (valid) => {
        if (valid) {
          try {
            const response = await this.$api.updatePlant(this.plantSave.id, this.plantSave)
            if (response.status === 200) {
              this.editDialogVisible = false
              this.getPlants()
              ElMessage({
                message: "保存成功",
                type: 'success'
              })
            }
          } catch (error) {
            console.error('更新产品失败:', error)
          }
        }
      })
    },
    
    async updateEnvPlant() {
      this.$refs['plantEnvRef'].validate(async (valid) => {
        if (valid) {
          try {
            const response = await this.$api.updateEnvPlant(this.envPlantSave.id, this.envPlantSave)
            if (response.status === 200) {
              this.envEditDialogVisible = false
              this.getEnvPlants()
              ElMessage({
                message: "保存成功",
                type: 'success'
              })
            }
          } catch (error) {
            console.error('更新产品环境失败:', error)
          }
        }
      })
    },
    
    async deletePlant(id) {
      try {
        await ElMessageBox.confirm(
          '确定删除此产品？删除后数据将无法恢复。',
          '确认删除',
          {
            confirmButtonText: '确认删除',
            cancelButtonText: '取消',
            type: 'warning',
            confirmButtonClass: 'el-button--danger',
            customClass: 'confirm-dialog'
          }
        )
        const response = await this.$api.deletePlant(id)
        if (response.status === 204) {
          this.getPlants()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }
      } catch (error) {
        // 用户取消删除
      }
    },
    
    async deleteEnvPlant(id) {
      try {
        await ElMessageBox.confirm(
          '确定删除此产品环境？删除后数据将无法恢复。',
          '确认删除',
          {
            confirmButtonText: '确认删除',
            cancelButtonText: '取消',
            type: 'warning',
            confirmButtonClass: 'el-button--danger',
            customClass: 'confirm-dialog'
          }
        )
        const response = await this.$api.deleteEnvPlant(id)
        if (response.status === 204) {
          this.getEnvPlants()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }
      } catch (error) {
        // 用户取消删除
      }
    },
    
    async getPlants() {
      try {
        const par = {
          ...this.plantSearch,
          ...this.page_size_params,
          project: this.projectInfo.id
        }
		const params = Object.assign(par, this.sort_params)
        const response = await this.$api.getPlants(params)
        if (response.status === 200) {
          this.plant_list = { ...response.data }
        }
      } catch (error) {
        console.error('获取产品列表失败:', error)
      }
    },
    
    async getEnvPlants() {
      try {
        const par = {
          ...this.envPlantSearch,
          ...this.page_size_params,
          project: this.projectInfo.id
        }
		const params = Object.assign(par, this.sort_params)
        const response = await this.$api.getEnvPlants(params)
        if (response.status === 200) {
          this.envPlantList = { ...response.data }
        }
      } catch (error) {
        console.error('获取产品环境列表失败:', error)
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
    
    async getPlant(id) {
      try {
        const response = await this.$api.getPlant(id)
        if (response.status === 200) {
          this.plantSave = { ...response.data.result }
        }
      } catch (error) {
        console.error('获取产品详情失败:', error)
      }
    },

    async  check_permission(){
        const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission[this.$route.path]}
		const response = await this.$api.check_permission(params)
		if (response.status === 200){
			 this.permission = { ...response.data.result }
		}
	 },
    
    async getEnvPlant(id) {
      try {
        const response = await this.$api.getEnvPlant(id)
        if (response.status === 200) {
          this.envPlantSave = { ...response.data.result }
		  this.selectedPlantType = this.envPlantSave.type
        }
      } catch (error) {
        console.error('获取产品环境详情失败:', error)
      }
    },

  },
  created() {
    this.check_permission()
    this.user_list = JSON.parse(localStorage.getItem('user_list') || '[]')
    this.getPlants()
    this.getEnvs()
    this.getEnvPlants()
  },
  watch: {
    activeName(val) {
      if (val === 'first') {
        this.getPlants()
      } else if (val === 'second') {
        this.getEnvPlants()
      }
    }
  }
}
</script>

<style scoped>
.plant-management-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
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
  border: none;
  margin-bottom: 20px;
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

.filter-card :deep(.el-card__body) {
  padding: 20px 20px 0 20px;
}

.filter-form-wrapper {
  padding: 25px 5px 0px 5px;
}

/* 内联表单样式 */
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
    color: #475569;
    width: 90px;
    margin-right: 10px;
    flex-shrink: 0;
    white-space: nowrap;
}

.inline-label-text {
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  white-space: nowrap;
}

.icon-product,
.icon-plant,
.icon-env,
.icon-creator,
.icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
}

.icon-product { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-plant { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.icon-env { background: linear-gradient(135deg, #06b6d4 0%, #0e7490 100%); }
.icon-creator { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-updater { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }

/* 内联输入框样式 */
.input-inline >>> .el-input__inner,
.select-inline >>> .el-input__inner {
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  padding: 0 15px;
  box-shadow: none;
  transition: all 0.3s ease;
  flex: 1;
  margin-left: 12px;
}

.input-inline >>> .el-input__inner:hover,
.select-inline >>> .el-input__inner:hover {
  border-color: #cbd5e1;
  background: white;
}

.input-inline >>> .el-input__inner:focus,
.select-inline >>> .el-input__inner:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.select-inline {
  flex: 1;
  margin-left: 12px;
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
}
::v-deep .content-card .el-card__body {
  padding: 0px;
}

.content-header {
  padding: 20px 24px 0 24px;
  margin-top: 20px;
  flex-shrink: 0;
}

.content-title-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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

.add-btn .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

/* Tabs样式 */
.tabs-wrapper {
  margin-top: 10px;
}

.elegant-tabs {
  background: transparent;
}

.elegant-tabs >>> .el-tabs__header {
  margin: 0;
  border-bottom: 2px solid #f1f5f9;
}

.elegant-tabs >>> .el-tabs__nav-wrap::after {
  display: none;
}

.elegant-tabs >>> .el-tabs__item {
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
  color: #64748b;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
}

.elegant-tabs >>> .el-tabs__item:hover {
  color: #3b82f6;
}

.elegant-tabs >>> .el-tabs__item.is-active {
  color: #3b82f6;
  font-weight: 600;
}

.elegant-tabs >>> .el-tabs__item.is-active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 3px 3px 0 0;
}

.elegant-tabs >>> .el-tabs__active-bar {
  display: none;
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

.elegant-table >>> .el-table__body-wrapper .el-table__row.active-row {
  background: #ebf5ff;
  position: relative;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row.active-row::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%);
}

.elegant-table >>> .el-table__body-wrapper td {
  border-bottom: 1px solid #f1f5f9;
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
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-radius: 8px;
  font-weight: 600;
  color: #475569;
  margin: 0 auto;
}

.name-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 500;
  font-size: 13px;
  transition: all 0.3s ease;
  border-width: 2px;
}

.product-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.product-icon {
  font-weight: bold;
  margin-right: 4px;
}

.icon-web,
.icon-app,
.icon-h5,
.icon-mini,
.icon-desktop,
.icon-default {
  display: inline-block;
  width: 12px;
  height: 12px;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-web {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z'/%3E%3C/svg%3E");
}

.icon-app {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M16 1H8C6.34 1 5 2.34 5 4v16c0 1.66 1.34 3 3 3h8c1.66 0 3-1.34 3-3V4c0-1.66-1.34-3-3-3zm-2 20h-4v-1h4v1zm3.25-3H6.75V4h10.5v14z'/%3E%3C/svg%3E");
}

.icon-h5 {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2306b6d4' d='M14.4 6L14 4H5v17h2v-7h5.6l.4 2h7V6h-5.6zM7 14v-3.5h2.5c.8 0 1.5.7 1.5 1.5s-.7 1.5-1.5 1.5H7zm5.5-4c-.8 0-1.5-.7-1.5-1.5s.7-1.5 1.5-1.5 1.5.7 1.5 1.5-.7 1.5-1.5 1.5z'/%3E%3C/svg%3E");
}

.icon-mini {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M16 1H8C6.34 1 5 2.34 5 4v16c0 1.66 1.34 3 3 3h8c1.66 0 3-1.34 3-3V4c0-1.66-1.34-3-3-3zm-2 20h-4v-1h4v1zm3.25-3H6.75V4h10.5v14z'/%3E%3C/svg%3E");
}

.icon-desktop {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ef4444' d='M21 2H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h7v2H8v2h8v-2h-2v-2h7c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H3V4h18v12z'/%3E%3C/svg%3E");
}

.type-tag,
.env-type-tag,
.env-tag {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.host-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.host-link {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #3b82f6;
  text-decoration: none;
  transition: all 0.3s ease;
}

.host-link:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

.icon-link {
  display: inline-block;
  width: 12px;
  height: 12px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

/* APP信息显示样式 */
.app-info-cell {
  text-align: left;
  padding: 4px 0;
}

.app-info-item {
  display: flex;
  margin-bottom: 6px;
  font-size: 12px;
  line-height: 1.4;
}

.app-info-item:last-child {
  margin-bottom: 0;
}

.app-info-label {
  min-width: 70px;
  color: #64748b;
  font-weight: 500;
  flex-shrink: 0;
}

.app-info-value {
  flex: 1;
  color: #334155;
  font-family: 'Courier New', monospace;
  word-break: break-all;
  background: #f8fafc;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

.empty-cell {
  color: #94a3b8;
  font-style: italic;
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
  border-top: 1px solid #f1f5f9;
  flex-shrink: 0;
  display: block !important;
  float: right;
  min-height: 40px;
  background: white;
  z-index: 10;
  position: relative;
  opacity: 1 !important;
  visibility: visible !important;
}


/* 对话框样式 */
.elegant-dialog >>> .el-dialog {
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.elegant-dialog >>> .el-dialog__header {
  padding: 24px 24px 0;
  margin: 0;
}

.elegant-dialog >>> .el-dialog__title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 12px;
}

.elegant-dialog >>> .el-dialog__title::before {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
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
}

/* 修改为每个字段一行 */
.dialog-form-item-full {
  margin-bottom: 20px;
  width: 100%;
}

.dialog-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.icon-product-dialog,
.icon-type-dialog,
.icon-env-dialog,
.icon-plant-dialog,
.icon-web,
.icon-app,
.icon-host,
.icon-package,
.icon-activity {
  width: 16px;
  height: 16px;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-product-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/%3E%3C/svg%3E");
}

.icon-type-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M12 3L1 9l11 6 9-4.91V17h2V9L12 3zM5 13.38v3.79l7 3.11 7-3.11v-3.79l-7 3.11-7-3.11z'/%3E%3C/svg%3E");
}

.icon-env-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M12 3L4 9v12h16V9l-8-6zm0 2.5L18 9v3h-2v4h-2v-4h-2v4h-2v-4H6V9l6-3.5zM6 19v-5h12v5H6z'/%3E%3C/svg%3E");
}

.icon-plant-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M17 12h-5v5h5v-5zM16 1v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-1V1h-2zm3 18H5V8h14v11z'/%3E%3C/svg%3E");
}

.icon-web {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z'/%3E%3C/svg%3E");
}

.icon-app {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M16 1H8C6.34 1 5 2.34 5 4v16c0 1.66 1.34 3 3 3h8c1.66 0 3-1.34 3-3V4c0-1.66-1.34-3-3-3zm-2 20h-4v-1h4v1zm3.25-3H6.75V4h10.5v14z'/%3E%3C/svg%3E");
}

.icon-host {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z'/%3E%3C/svg%3E");
}

.icon-package {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z'/%3E%3C/svg%3E");
}

.icon-activity {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M13 3h-2v10h2V3zm4.83 2.17l-1.42 1.42C17.99 7.86 19 9.81 19 12c0 3.87-3.13 7-7 7s-7-3.13-7-7c0-2.19 1.01-4.14 2.58-5.42L6.17 5.17C4.23 6.82 3 9.26 3 12c0 4.97 4.03 9 9 9s9-4.03 9-9c0-2.74-1.23-5.18-3.17-6.83z'/%3E%3C/svg%3E");
}

.dialog-input-full >>> .el-input__inner,
.dialog-select-full >>> .el-input__inner {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: white;
  padding: 0 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  width: 100%;
  height: 40px;
  line-height: 40px;
}

.dialog-input-full >>> .el-input__inner:hover,
.dialog-select-full >>> .el-input__inner:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-input-full >>> .el-input__inner:focus,
.dialog-select-full >>> .el-input__inner:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.dialog-input-full >>> .el-input__count {
  color: #94a3b8;
}

.web-config-section,
.app-config-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f1f5f9;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.elegant-dialog >>> .el-dialog__footer {
  padding: 16px 24px 24px;
  border-top: 1px solid #f1f5f9;
}

.dialog-footer {
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
  .plant-management-container {
    padding: 16px;
  }
  
  .filter-card .filter-header,
  .filter-card .filter-form-wrapper,
  .content-card .content-header{
    padding: 16px 20px;
  }
}

@media screen and (max-width: 768px) {
  .plant-management-container {
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
  
  .elegant-table {
    min-width: 800px;
  }
  
  .pagination-wrapper {
    padding: 15px 20px;
  }
  
  /* 响应式调整内联表单 */
  .inline-form-item {
    height: auto;
    flex-wrap: wrap;
    margin-bottom: 16px;
  }
  
  .inline-label-wrapper {
    min-width: 80px;
    margin-bottom: 8px;
  }
  
  .input-inline >>> .el-input__inner,
  .select-inline >>> .el-input__inner {
    margin-left: 0;
    margin-top: 4px;
  }
  
  .select-inline {
    margin-left: 0;
    margin-top: 4px;
  }
  
  /* 对话框响应式 */
  .dialog-form-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .dialog-form-item-full {
    min-width: 100%;
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