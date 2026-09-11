<template>
  <!-- 关联脚本用例弹窗 -->
  <el-drawer v-model="chooseCaseVisible" :with-header="false" direction="ttb" show-close :z-index="1001" fullscreen="true" destroy-on-close :size="'calc(100vh - 30px)'">
    <CaseList :isCanChoose="true" v-model:chooseCaseVisible="chooseCaseVisible" :existCaseIds="caseForm.case" @setCaseData="setCaseData" @setManyCaseData="setManyCaseData"></CaseList>
  </el-drawer>
  
  
  <!-- 模块编辑对话框 -->
  <el-dialog v-model="editModuleVisible" :title="moduleTitle" width='450' class="elegant-dialog">
    <div class="dialog-content">
      <el-form :model="moduleSave" label-position='top' :rules="moduleRules" ref='moduleRef' class="dialog-form" :disabled="moduleView">
        <el-form-item  prop='name' class="dialog-form-item">
          <label class="dialog-label">
            <i class="icon-module"></i>
            模块名称
          </label>
          <el-input v-model="moduleSave.name" autocomplete="off" placeholder="请输入模块名称" class="input" size='large'/>
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

  <!-- 批量删除确认弹窗 -->
  <el-dialog v-model="batchDeleteDialogVisible" title="批量删除用例" width="500px" class="elegant-dialog" append-to-body>
    <div class="batch-delete-content">
      <el-icon class="batch-delete-icon"><Delete /></el-icon>
      <div class="batch-delete-text">
        <p>确定删除选中的 <span class="batch-delete-count">{{ multipleSelection.length }}</span> 条用例？</p>
        <p class="batch-delete-tip">删除后数据将无法恢复</p>
      </div>
    </div>
    <template #footer>
      <el-button @click="batchDeleteDialogVisible = false">取消</el-button>
      <el-button type="danger" @click="confirmBatchDelete" :loading="batchDeleting">确认删除</el-button>
    </template>
  </el-dialog>

  <!-- 批量修改弹窗 -->
  <el-dialog v-model="batchDialogVisible" :title="batchDialogTitle" width="500px" class="elegant-dialog" append-to-body>
    <el-form :model="batchForm" label-position="top" class="batch-form">
      <el-form-item  v-if="batchDialogType === 'owner'">
        <el-select v-model="batchForm.owner" placeholder="请选择负责人" style="width: 100%" size="large" popper-class="select-dropdown-rounded" filterable clearable class="select">
          <el-option v-for="user_obj in user_list" :key="user_obj.id" :label="user_obj.username" :value="user_obj.id" />
        </el-select>
      </el-form-item>
      <el-form-item  v-if="batchDialogType === 'auto_status'">
        <el-select v-model="batchForm.auto_status" class='select' placeholder="请选择自动化状态" style="width: 100%" size="large" popper-class="select-dropdown-rounded" clearable>
          <el-option label="已完成" :value="1" />
          <el-option label="进行中" :value="2" />
          <el-option label="待开始" :value="3" />
          <el-option label="手工测试" :value="4" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="batchDialogType === 'module'">
        <el-cascader
          v-model="batchForm.module"
          :options="plant_module_list"
          :props="moduleEditProps"
          placeholder="请选择模块"
          style="width: 100%"
          size="large"
          clearable
          filterable
          class="cascader"
        />
      </el-form-item>
      <el-form-item  v-if="batchDialogType === 'tag'">
        <el-select v-model="batchForm.tag" class='select' placeholder="请选择标签" style="width: 100%" size="large" popper-class="select-dropdown-rounded" multiple clearable>
          <el-option v-for="tag in tag_list" :key="tag.id" :label="tag.name" :value="tag.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="batchDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="confirmBatchUpdate">确定修改</el-button>
    </template>
  </el-dialog>

  <!-- AI生成场景脚本弹窗 -->
  <el-dialog v-model="scenarioGenVisible" title="AI生成场景脚本" width="520" draggable class="elegant-dialog">
    <el-form class="dialog-form" label-position="top" @submit.prevent>
      <el-alert
        title="AI将根据当前功能用例自动编排接口/WebUI场景脚本，并附带断言与变量传递（进行中的任务可在站内信查看）。"
        type="info"
        :closable="false"
        show-icon
        class="tip-alert ai-alert"
      />
      <el-form-item class="dialog-form-item">
        <label class="dialog-label">生成模式<span class="ai-required">*</span></label>
        <el-checkbox-group v-model="scenarioGenForm.modes">
          <el-checkbox-button label="api">接口自动化</el-checkbox-button>
          <el-checkbox-button label="web_ui">WebUI自动化</el-checkbox-button>
        </el-checkbox-group>
        <div class="scenario-mode-tip">WebUI模式会在前置步骤自动插入接口调用造数据，并传递变量参数</div>
      </el-form-item>
      <el-form-item class="dialog-form-item">
        <label class="dialog-label">AI模型<span class="ai-required">*</span></label>
        <el-select v-model="scenarioAiConfigId" placeholder="请选择AI模型" class="select" size="large" popper-class="select-dropdown-rounded" style="width:100%">
          <el-option v-for="cfg in scenarioAiConfigs" :key="cfg.id" :label="cfg.provider_name + ' / ' + cfg.model_name" :value="cfg.id" />
        </el-select>
      </el-form-item>
      <el-form-item class="dialog-form-item">
        <label class="dialog-label">补充需求(可选)</label>
        <el-input v-model="scenarioGenForm.extra_requirement" type="textarea" :rows="3" placeholder="例如：覆盖正向+边界+异常场景、生成后清理测试数据" class='text' />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="scenarioGenVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button type="primary" :loading="scenarioGenerating" class="dialog-confirm-btn" @click="submitScenarioGen">开始生成</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 步骤详情抽屉 -->
  <el-drawer class="step fun-case-drawer" :z-index="1000" v-model="editCaseVisible" @closed="onDrawerClosed" :with-header="false" direction="rtl" :show-close="false" :append-to-body="true" :close-on-click-modal="false" size="calc(100vw)" >
    <el-card class="content-card elegant-shadow">
  	  <el-form :disabled="caseView" :rules="caseRules" ref="caseRef" :model="caseForm" label-position="top">
		<div class="drawer-split-layout">
		  <!-- 左侧：步骤信息 -->
		  <div class="drawer-left">
		  <div class="content-header">
  			<div class="header-top">
  			  <div class="case-title-area">
  				<el-form-item prop="name" class="title-form-item">
  					<el-input
  					  v-model="caseForm.name"
  					  class="case-title-input"
  					  placeholder="请输入用例名称"
  					  maxlength="50"
  					  :disabled="caseView"
  					/>
  				</el-form-item>
  			  </div>
  			</div>
			<!-- 创建/更新信息（右对齐） -->
			<div class="case-meta-section">
				<div class="case-meta">
					<div class="meta-item">
						<span class="meta-label">创建人</span>
						<span class="meta-value">{{ caseForm.create_by_name || '-' }}</span>
					</div>
					<div class="meta-divider"></div>
					<div class="meta-item">
						<span class="meta-label">创建时间</span>
						<span class="meta-value">{{ caseForm.create_time || '-' }}</span>
					</div>
					<div class="meta-divider"></div>
					<div class="meta-item">
						<span class="meta-label">更新人</span>
						<span class="meta-value">{{ caseForm.update_by_name || '-' }}</span>
					</div>
					<div class="meta-divider"></div>
					<div class="meta-item">
						<span class="meta-label">更新时间</span>
						<span class="meta-value">{{ caseForm.update_time || '-' }}</span>
					</div>
				</div>
			</div>
  	  </div>
	  <div class="drawer-left-content">
      <el-collapse v-model="activeNames" class="step-collapse-panel" ref="collapse">
  		  <!-- 关联脚本用例 -->
		  <el-card class='step_item_card' v-if='caseForm.can_autoed !=3 '>
			  <el-collapse-item  name="0" >
					<template #title="{ isActive }">
					  <div class="section-divider">
						<span class="section-title">关联脚本用例</span>
					  </div>
					</template>
					<el-button
					  v-if="caseForm.id && !caseView" 
					  @click="openScenarioGen" 
					  type="success" 
					  class="add-btn"
					  style='float: right; margin-bottom: 20px; margin-right: 10px;'
					>
					  <el-icon><MagicStick /></el-icon>AI生成脚本
					</el-button>
					<el-button
					  v-if="permission.has_edit_permission || permission.has_add_permission" 
					  @click="()=>{this.chooseCaseVisible=true}" 
					  type="primary" 
					  class="add-btn"
					  style='float: right; margin-bottom: 20px; margin-right: 10px;'
					>
					  <el-icon><Plus /></el-icon>关联脚本用例
					</el-button>
					<el-table
					    :data="caseForm.case_detail" 
					    :max-height="'calc(100vh - 580px)'" 
					    class="elegant-table"
					    :header-row-style="headerRowStyle"
					    @row-dblclick="editStep"
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
					      min-width="250" 
					      align="center"
					      class-name="case-info-column"
					    >
					      <template #default='scope'>
					        <div class="case-info-cell">
					          <div class="case-type-badge">
					            <el-tag 
					              size="small" 
					              :type="getTypeTagType(scope.row.type_name)"
					              effect="light"
					              class="type-tag"
					            >
					              <i :class="`type-icon-cell type-icon-${scope.row.type}`"></i>
					              {{ scope.row.type_name }}
					            </el-tag>
					          </div>
					          <el-link type="primary" @click='editStep(scope.row)' class="case-link">
					            {{ scope.row.name }}
					          </el-link>
					        </div>
					      </template>
					    </el-table-column>
					    
					    <el-table-column 
					      label="最近测试结果" 
					      prop="recent_test_result_name" 
					      width="120" 
					      align="center"
					      class-name="result-column"
					    >
					      <template #default="scope">
					        <el-tag 
					          v-if='scope.row.recent_test_result_name ==="成功"' 
					          effect="dark" 
					          type="success"
					          class="result-tag"
					        >{{ scope.row.recent_test_result_name }}</el-tag>
					        <el-tag 
					          v-if='scope.row.recent_test_result_name ==="失败"' 
					          effect="dark" 
					          type="danger"
					          class="result-tag"
					        >{{ scope.row.recent_test_result_name }}</el-tag>
					        <el-tag 
					          v-if='scope.row.recent_test_result_name ==="错误"' 
					          effect="dark" 
					          type="danger"
					          class="result-tag"
					        >{{ scope.row.recent_test_result_name }}</el-tag>
					        <el-tag 
					          v-if='scope.row.recent_test_result_name ==="未执行"' 
					          effect="dark" 
					          type="info"
					          class="result-tag"
					        >{{ scope.row.recent_test_result_name }}</el-tag>
					      </template>
					    </el-table-column>
					    
					    <el-table-column 
					      label="用例标签" 
					      prop="tag_name" 
					      min-width="160" 
					      align="center"
					      class-name="tag-column"
					    >
					      <template #default="scope">
					        <div class="tags-container">
					          <el-tag 
					            v-for='obj in scope.row.tag_name' 
					            :key="obj.id"
					            size="small"
					            :type="getTagType(obj.name)"
					            effect="light"
					            class="case-tag"
					          >
					            {{ obj.name }}
					          </el-tag>
					          <span v-if="!scope.row.tag_name || scope.row.tag_name.length === 0" class="no-tag">-</span>
					        </div>
					      </template>
					    </el-table-column>
					    
					    <!-- 合并列：创建信息 -->
					    <el-table-column 
					      label="创建信息" 
					      width="200" 
					      align="center"
						  sortable 
						  prop='create_time'
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
						  sortable
						   prop='update_time'
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
					      width="80" 
					      label="操作"
					      class-name="action-column"
					      fixed="right"
					    >
					      <template #default="scope">
					        <div class="action-buttons">
					          
					          <el-tooltip 
					            content="移除用例" 
					            placement="top" 
					            effect="dark"
					          >
					            <el-button 
					              type="danger" 
					              v-if="permission.has_edit_permission || permission.has_add_permission" 
					              @click.stop="removeCase(scope)" 
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
			  </el-collapse-item>
		  </el-card>
  		  
  		  <el-card class='step_item_card' >
  			  <el-collapse-item  name="1" >
  					<template #title="{ isActive }">
  						  <div class="section-divider">
  							<span class="section-title">前置条件</span>
  						  </div>
  					</template>
					<FullText 
					     v-model="caseForm.setup_condition"
					     placeholder="请输入前置条件"
						 :height="450"
					     :autoHeight="true"
					    />
  			  </el-collapse-item>
  		  </el-card>
          
  		  <el-card class='step_item_card' >
  			  <el-collapse-item  name="2" >
  				<template #title="{ isActive }">
  					  <div class="section-divider">
						<el-form-item  prop="step_type" style='margin-top: 15px;'>
						  <span class="section-title">步骤描述</span>
						  <el-radio-group v-model="caseForm.step_type"  size='small' style='margin-left:15px'>
							<el-radio-button :value="1">文本模式</el-radio-button>
							<el-radio-button :value="2">表格模式</el-radio-button>
						  </el-radio-group>
						</el-form-item>
  					  </div>
  				</template>
  			    <FullText
					v-if='caseForm.step_type ===1'
  			         v-model="caseForm.step_text"
  			         placeholder="请输入步骤描述"
  			    	 :height="450"
  			         :autoHeight="true"
  			        />
				<FunCaseTable
					v-if='caseForm.step_type ===2'
				    :tableData="caseForm.step_table"
				    />
  			  </el-collapse-item>
  		  </el-card>
        
  		  <el-card class='step_item_card' v-if='caseForm.step_type ===1'>
  			  <el-collapse-item  name="3" >
  			    <template #title="{ isActive }">
  			    	  <div class="section-divider">
  			    		<span class="section-title">预期结果</span>
  			    	  </div>
  			    </template>
				<FullText
				     v-model="caseForm.exp_text"
				     placeholder="请输入预期结果"
					 :height="450"
				     :autoHeight="true"
				    />
  			  </el-collapse-item>
  		  </el-card>
		  
		  <el-card class='step_item_card' >
			  <el-collapse-item  name="4">
				<template #title="{ isActive }">
					  <div class="section-divider">
						<span class="section-title">用例备注</span>
					  </div>
				</template>
				<FullText
					 v-model="caseForm.case_mark"
					 placeholder="请输入用例备注"
					 :height="450"
					 :autoHeight="true"
					/>
			  </el-collapse-item>
		  </el-card>
  	
      </el-collapse>
	  </div>
	  </div>
		  <!-- 右侧：基础信息 -->
		  <div class="drawer-right">
		    <div class="drawer-right-title">
		      <span>基础信息</span>
		    </div>
		    <el-divider style="margin-top: 10px; margin-bottom: 30px"></el-divider>
		    <div class="step-base-info">
		      <el-form-item prop="module" label="所属模块">
		        <el-cascader
		          placeholder="请选择或输入模块名称"
		          collapse-tags
		          v-model="caseForm.module"
		          :options="plant_module_list"
		          :props="moduleEditProps"
		          filterable
		          size="large"
		          style="width: 100%;"
		          class="cascader"
		        />
		      </el-form-item>
		      <el-form-item prop="can_autoed" label="用例类型">
		        <el-select v-model="caseForm.can_autoed" placeholder="请选择"  class="select" size="large" popper-class="select-dropdown-rounded" @change="caseTypeChange">
		          <el-option label="全自动化" :value="1"></el-option>
		          <el-option label="半自动化" :value="2"></el-option>
		          <el-option label="手工测试" :value="3"></el-option>
		        </el-select>
		      </el-form-item>
		      <el-form-item prop="auto_status" label="自动化状态">
		        <el-select v-model="caseForm.auto_status" placeholder="请选择"  class="select" size="large" popper-class="select-dropdown-rounded">
		          <el-option v-if="caseForm.can_autoed !=3 " label="已完成" :value="1"></el-option>
		          <el-option v-if="caseForm.can_autoed !=3 " label="进行中" :value="2"></el-option>
		          <el-option v-if="caseForm.can_autoed !=3 " label="待开始" :value="3"></el-option>
		          <el-option v-if="caseForm.can_autoed ===3 " label="手工测试" :value="4"></el-option>
		        </el-select>
		      </el-form-item>
		      <el-form-item label="用例负责人" prop="owner">
		        <el-select v-model="caseForm.owner" placeholder="请选择用例负责人"  class="select" size="large" popper-class="select-dropdown-rounded">
		          <el-option v-for="user_obj in user_list" :label="user_obj.username" :value="user_obj.id" />
		        </el-select>
		      </el-form-item>
		      <el-form-item label="用例标签" prop="tag">
		        <el-select v-model="caseForm.tag" placeholder="请选择用例标签"  multiple class="select" size="large" popper-class="select-dropdown-rounded">
		          <el-option v-for="tag in tag_list" :label="tag.name" :value="tag.id" />
		        </el-select>
		      </el-form-item>
		      <el-form-item label="用例状态">
		        <el-input :model-value="getCaseStatusName(caseForm.case_status)" disabled size="large" />
		      </el-form-item>
		     
		    </div>
		  </div>
		</div>
  	  </el-form>
    </el-card>
    <div class="drawer-footer">
      <el-button type="primary" @click="() => { this.editCaseVisible = false; this.getCase() }" class="dialog-cancel-btn">
        <span class="button-text">取消</span>
      </el-button>
      <el-button v-if="!caseView && !stepView && permission.has_edit_permission && caseForm.case_status === 1" type="warning" @click="approveCase" :loading="loading" class="dialog-confirm-btn">
        <span class="button-text">审核通过</span>
      </el-button>
      <el-button v-if="!caseView && !stepView && permission.has_edit_permission && caseForm.case_status === 2" type="success" @click="reviewCase" :loading="loading" class="dialog-confirm-btn">
        <span class="button-text">评审通过</span>
      </el-button>
      <el-button v-if="!caseView && !stepView" type="primary" @click="saveFCase(false)" :loading="loading" class="dialog-confirm-btn">
        <span class="button-text">保存</span>
      </el-button>
      <el-button v-if="!caseView && !stepView" type="primary" @click="saveFCase(true)" :loading="loading" class="dialog-confirm-btn">
        <span class="button-text">保存并关闭</span>
      </el-button>
    </div>
  </el-drawer>

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
            :indent='10'
            :expand-on-click-node='false'
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
      <!-- 筛选区域 -->
      <el-card class="filter-card elegant-shadow">
        <div class="filter-header">
          <div class="header-title-section">
            <i class="icon-search"></i>
            <h3 class="filter-title">功能用例筛选</h3>
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
          <el-form :model="caseSearch" class="filter-form inline-form">
            <el-row :gutter="24">
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="inline-form-item">
                  <div class="inline-label-wrapper">
                    <i class="icon-case"></i>
                    <span class="inline-label-text">用例名称</span>
                  </div>
                  <el-input 
                    v-model="caseSearch.name" 
                    placeholder="请输入用例名称" 
                    clearable
					size='large'
                    class="input"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="inline-form-item">
                  <div class="inline-label-wrapper">
                    <i class="icon-tag"></i>
                    <span class="inline-label-text">用例标签</span>
                  </div>
                  <el-select 
                    v-model="caseSearch.tag" 
                    placeholder="请选择用例标签" 
                    clearable
					size='large'
                    class="select"
					popper-class='select-dropdown-rounded'
                  >
                    <el-option v-for="tag in tag_list" :label='tag.name' :value="tag.id" />
                  </el-select>
                </el-form-item>
              </el-col>
			  
			  <el-col :xs="24" :sm="12" :md="8" :lg="6">
			    <el-form-item class="inline-form-item">
			      <div class="inline-label-wrapper">
			        <i class="icon-result"></i>
			        <span class="inline-label-text">用例状态</span>
			      </div>
				  <el-select v-model="caseSearch.case_status" placeholder="请选择" clearable class="select" size='large' popper-class='select-dropdown-rounded'>
				    <el-option label='待修改' :value="1"></el-option>
				    <el-option label='待评审' :value="2"></el-option>
				    <el-option label='已评审' :value="3"></el-option>
				  </el-select>
			    </el-form-item>
			  </el-col>

			  <el-col :xs="24" :sm="12" :md="8" :lg="6">
			    <el-form-item class="inline-form-item">
			      <div class="inline-label-wrapper">
			        <i class="icon-result"></i>
			        <span class="inline-label-text">自动化状态</span>
			      </div>
				  <el-select v-model="caseSearch.auto_status" placeholder="请选择" clearable class="select" size='large' popper-class='select-dropdown-rounded'>
				    <el-option label='已完成' :value="1"></el-option>
				    <el-option label='进行中' :value="2"></el-option>
				    <el-option label='待开始' :value="3"></el-option>
				    <el-option label='手工测试' :value="4"></el-option>
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
                    v-model="caseSearch.create_by"
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

              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="inline-form-item">
                  <div class="inline-label-wrapper">
                    <i class="icon-creator"></i>
                    <span class="inline-label-text">更新人</span>
                  </div>
                  <el-select
                    v-model="caseSearch.update_by"
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

              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="inline-form-item">
                  <div class="inline-label-wrapper">
                    <i class="icon-creator"></i>
                    <span class="inline-label-text">负责人</span>
                  </div>
                  <el-select
                    v-model="caseSearch.owner"
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

      <!-- 用例列表区域 -->
      <el-card class="content-card elegant-shadow" :body-style="{ paddingBottom: '0px' }">
        <div class="content-header">
          <div class="content-title-section">
            <div class="title-with-stats">
              <h3 class="content-title">功能用例列表</h3>
              <div class="stats-info">
                <div class="stat-item">
                  <span class="stat-label">总计</span>
                  <span class="stat-value">{{ case_list.count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">当前页</span>
                  <span class="stat-value">{{ page_size_params.page }}</span>
                </div>
				<div class="stat-item" v-if='isCanChoose'>
					<span class="stat-label">已选中</span>
					<span class="stat-value">{{ multipleSelection.length }}</span>
				</div>
              </div>
            </div>
            <div class="header-action-section">
              <div class="selected-count-badge" v-if="!isCanChoose && multipleSelection.length > 0">
                <el-icon><SuccessFilled /></el-icon>
                <span>已选 {{ multipleSelection.length }}</span>
              </div>
              <el-dropdown
                v-if="permission.has_edit_permission && !isCanChoose"
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
                    <el-dropdown-item command="owner" class="batch-dropdown-item">
                      <span class="item-text">修改负责人</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="auto_status" class="batch-dropdown-item">
                      <span class="item-text">修改自动化状态</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="module" class="batch-dropdown-item">
                      <span class="item-text">修改模块</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="tag" class="batch-dropdown-item">
                      <span class="item-text">添加标签</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" class="batch-dropdown-item">
                      <span class="item-text">批量删除</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button
                v-if="permission.has_add_permission && !isCanChoose"
                @click="addCase"
                type="primary"
                class="add-btn"
              >
                <el-icon><Plus /></el-icon>新增用例
              </el-button>
            </div>
			<el-button
			  v-if="permission.has_add_permission && isCanChoose" 
			  @click="chooseFuncManyCase" 
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
            :data="case_list.results" 
            :max-height="'calc(100vh - 540px)'"
            class="elegant-table"
			@selection-change="handleSelectionChange"
            :header-row-style="headerRowStyle"
			@sort-change='handleSortChange'
          >
            <el-table-column type="selection" width="55" align="center"></el-table-column>

            <el-table-column
              label="用例名称"
              min-width="250"
              align="center"
			  prop="name"
              class-name="case-info-column"
             :show-overflow-tooltip="true">
              <template #default="scope">
                <el-link type="primary" @click="editStepTwo(scope.row)" class="case-link">
                  {{ scope.row.name }}
                </el-link>
              </template>
            </el-table-column>
			
			<!-- <el-table-column
			  label="用例类型" 
			  width="100" 
			  align="center"
			  prop="can_autoed_name" 
			  class-name="case-info-column"
			>
			 
			</el-table-column> -->
			
			<el-table-column
			  label="自动化状态"
			  width="150"
			  align="center"
			  prop="auto_status_name"
			  class-name="case-info-column"
			>
			  <template #default="scope">
			    <el-dropdown
			      v-if="!isCanChoose && permission.has_edit_permission"
			      trigger="click"
			      @command="(val) => updateSingleField(scope.row, 'auto_status', val)"
			      class="status-dropdown"
			      popper-class="status-dropdown-popper"
			    >
			      <span class="status-badge" :class="'auto-status-' + scope.row.auto_status">
			        <span class="status-dot"></span>
			        <span class="status-label">{{ scope.row.auto_status_name || '-' }}</span>
			        <el-icon class="status-arrow"><ArrowDown /></el-icon>
			      </span>
			      <template #dropdown>
			        <el-dropdown-menu>
			          <el-dropdown-item :command="1" class="status-dropdown-item">
			            <span class="status-indicator success"></span>
			            <span class="status-text">已完成</span>
			          </el-dropdown-item>
			          <el-dropdown-item :command="2" class="status-dropdown-item">
			            <span class="status-indicator primary"></span>
			            <span class="status-text">进行中</span>
			          </el-dropdown-item>
			          <el-dropdown-item :command="3" class="status-dropdown-item">
			            <span class="status-indicator warning"></span>
			            <span class="status-text">待开始</span>
			          </el-dropdown-item>
			          <el-dropdown-item :command="4" class="status-dropdown-item">
			            <span class="status-indicator info"></span>
			            <span class="status-text">手工测试</span>
			          </el-dropdown-item>
			        </el-dropdown-menu>
			      </template>
			    </el-dropdown>
			    <span v-else class="status-badge-static" :class="'auto-status-' + scope.row.auto_status">
			      {{ scope.row.auto_status_name || '-' }}
			    </span>
			  </template>
			</el-table-column>

            <!-- <el-table-column
              label="测试结果"
              prop="recent_test_result_name"
              width="120"
              align="center"
              class-name="result-column"
            >
              <template #default="scope">
                <el-tag 
                  v-if='scope.row.recent_test_result_name ==="成功"' 
                  effect="dark" 
                  type="success"
                  class="result-tag"
                >{{ scope.row.recent_test_result_name }}</el-tag>
                <el-tag 
                  v-if='scope.row.recent_test_result_name ==="失败"' 
                  effect="dark" 
                  type="danger"
                  class="result-tag"
                >{{ scope.row.recent_test_result_name }}</el-tag>
                <el-tag 
                  v-if='scope.row.recent_test_result_name ==="错误"' 
                  effect="dark" 
                  type="danger"
                  class="result-tag"
                >{{ scope.row.recent_test_result_name }}</el-tag>
                <el-tag 
                  v-if='scope.row.recent_test_result_name ==="未执行"' 
                  effect="dark" 
                  type="info"
                  class="result-tag"
                >{{ scope.row.recent_test_result_name }}</el-tag>
              </template>
            </el-table-column> -->
            
            <el-table-column
              label="用例标签"
              prop="tag_name"
              min-width="180"
              align="center"
              class-name="tag-column"
            >
              <template #default="scope">
                <div class="tags-container">
                  <el-tag
                    v-for='obj in scope.row.tag_name'
                    :key="obj.id"
                    size="small"
                    :type="getTagType(obj.name)"
                    effect="light"
                    class="case-tag"
                  >
                    {{ obj.name }}
                  </el-tag>
                  <span v-if="!scope.row.tag_name || scope.row.tag_name.length === 0" class="no-tag">-</span>
                  <el-dropdown
                    v-if="!isCanChoose && permission.has_edit_permission"
                    trigger="click"
                    @command="(val) => updateSingleField(scope.row, 'tag', [val])"
                    class="tag-add-dropdown"
                    popper-class="tag-add-dropdown-popper"
                  >
                    <span class="tag-add-badge">
                      <el-icon><Plus /></el-icon>
                    </span>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item
                          v-for="tag in tag_list"
                          :key="tag.id"
                          :command="tag.id"
                          class="tag-dropdown-item"
                        >
                          <span class="status-indicator" :class="getTagColorClass(tag.name)"></span>
                          <span class="status-text">{{ tag.name }}</span>
                        </el-dropdown-item>
                        <div v-if="!tag_list || tag_list.length === 0" class="tag-empty">暂无标签</div>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </template>
            </el-table-column>

			<el-table-column
			  label="用例状态"
			  width="120"
			  align="center"
			  prop="case_status_name"
			  class-name="case-info-column"
			>
			  <template #default="scope">
			    <span class="status-badge-static" :class="'case-status-' + scope.row.case_status">
			      {{ getCaseStatusName(scope.row.case_status) }}
			    </span>
			  </template>
			</el-table-column>

			<el-table-column
			  label="负责人"
			  width="160"
			  align="center"
			  prop="owner_name"
			  class-name="case-info-column"
			>
			  <template #default="scope">
			    <el-dropdown
			      v-if="!isCanChoose && permission.has_edit_permission"
			      trigger="click"
			      @command="(val) => updateSingleField(scope.row, 'owner', val)"
			      class="status-dropdown"
			      popper-class="owner-dropdown-popper"
			    >
			      <span class="status-badge" :class="getOwnerClass(scope.row.owner)">
			        <span class="status-dot"></span>
			        <span class="status-label">{{ scope.row.owner_name || '未分配' }}</span>
			        <el-icon class="status-arrow"><ArrowDown /></el-icon>
			      </span>
			      <template #dropdown>
			        <el-dropdown-menu>
			          <el-dropdown-item v-for="user_obj in user_list" :key="user_obj.id" :command="user_obj.id" class="status-dropdown-item">
			            <span class="status-indicator" :class="getOwnerIndicatorClass(user_obj.id)"></span>
			            <span class="status-text">{{ user_obj.username }}</span>
			          </el-dropdown-item>
			        </el-dropdown-menu>
			      </template>
			    </el-dropdown>
			    <span v-else class="status-badge-static" :class="getOwnerClass(scope.row.owner)">
			      {{ scope.row.owner_name || '-' }}
			    </span>
			  </template>
			</el-table-column>

            <!-- 合并列：创建信息 -->
            <el-table-column 
              label="创建信息" 
              width="200" 
              align="center"
			  prop='create_time'
			  sortable="customer"
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
			  prop='update_time'
			  sortable='customer'
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
                    content="查看用例" 
                    placement="top" 
                    effect="dark"
                  >
                    <el-button 
                      type="success" 
                      v-if="permission.has_read_permission && !isCanChoose" 
                      class="action-btn view-btn"
                      @click.stop="viewCase(scope.row)"
                      circle
                    >
                      <el-icon><View /></el-icon>
                    </el-button>
                  </el-tooltip>
                  
                  <el-tooltip 
                    content="编辑用例" 
                    placement="top" 
                    effect="dark"
                  >
                    <el-button 
                      type="warning" 
                      v-if="permission.has_edit_permission && !isCanChoose" 
                      class="action-btn edit-btn"
                      @click.stop="editCase(scope.row)"
                      circle
                    >
                      <el-icon><EditPen /></el-icon>
                    </el-button>
                  </el-tooltip>
                  
                  <el-tooltip 
                    content="复制用例" 
                    placement="top" 
                    effect="dark"
                  >
                    <el-button 
                      type="primary" 
                      v-if="permission.has_add_permission && !isCanChoose" 
                      class="action-btn copy-btn"
                      @click.stop="copy(scope.row)"
                      circle
                    >
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </el-tooltip>
                  
                  <el-tooltip 
                    content="删除用例" 
                    placement="top" 
                    effect="dark"
                  >
                    <el-button 
                      type="danger" 
                      v-if="permission.has_delete_permission && !isCanChoose" 
                      @click.stop="deleteCase(scope.row.id)" 
                      class="action-btn delete-btn"
                      circle
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
				  
				  <el-tooltip
				    content="选择用例" 
				    placement="top" 
				    effect="dark"
				  >
				    <el-button 
				      type="primary" 
					   v-if="isCanChoose && !existCaseIds.includes(scope.row.id)"
				      class="action-btn choose-btn"
				      @click.stop="chooseCaseId(scope.row)"
				      circle
				    >
				      <el-icon><Pointer /></el-icon>
				    </el-button>
				  </el-tooltip>
				  <el-tag v-if="isCanChoose && existCaseIds.includes(scope.row.id)">已选</el-tag>
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
            :total="case_list.count"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            class="select input"
            :background="true"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import FullText from '../../components/FullText.vue'
import CaseList from './CaseList.vue'
import FunCaseTable from '../../components/FunCaseTable.vue'

import {
  Refresh,
  Search,
  Plus,
  View,
  Delete,
  EditPen,
  CopyDocument,
  Setting,
  Expand,
  Fold,
  SuccessFilled,
  ArrowDown,
  MagicStick
} from '@element-plus/icons-vue'

export default{
  watch: {
    filterText(val) {
      if (this.$refs.treeRef) {
        this.$refs.treeRef.filter(val)
      }
    },
    // 【AI 用例可见性修复】同组件内 query 变化不会重新触发 mounted，
    // 因此 AI 生成完成通知链接（#/resource/funcCase?filter=ai）需要在
    // query 变化时手动重新应用筛选条件并刷新列表。
    '$route.query.filter'(val) {
      if (val === 'ai') {
        this.applyAiFilter()
        this.getFCases()
      }
    },
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
    'caseId':{
      type: Infinity,
    },
	'existCaseIds': {
	  type: Array,
	  default:  () => [],
	},
  },
  computed:{
    ...mapState(['pathPermission', 'projectInfo', 'userInfo']),

    calcMinWidth() {
      let visibleButtons = 0
      if (this.permission.has_read_permission && !this.isCanChoose) visibleButtons += 1
      if (this.permission.has_edit_permission && !this.isCanChoose) visibleButtons += 1
      if (this.permission.has_add_permission && !this.isCanChoose) visibleButtons += 1
      if (this.permission.has_delete_permission && !this.isCanChoose) visibleButtons += 1
      if (this.isCanChoose) visibleButtons += 1;
      return Math.max(10, visibleButtons * 60)
    }
  },
  data() {
    return {
      module_node: {},
	  chooseCaseVisible: false,
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
        plant: '',
        parent: 0,
      },
      editModuleVisible: false,
      selectNode: 0,
      filterText: '',
      includeChildren: true,
      caseView: false,
      activeNames: '2',
      result_list: [
        {label: '成功', value: 1},
        {label: '失败', value: 2},
        {label: '错误', value: 3},
        {label: '未执行', value: 4},
      ],
      tag_list: '',
      caseForm:{
        project: '',
        id: '',
        module: '',
        name: '',
        tag: '',
        owner: '',
		setup_condition: '',
		case_mark: '',
		step_text: '',
		step_table: [],
		can_autoed: 3,
		auto_status: 4,
		case_status: 2,
		case: [],
		case_detail: [],
		step_type: 2
      },
	  search_person: 1,
      caseRules: {
        name: [{
          required: true,
          message: '用例名称不能为空',
          trigger: 'blur',
        }],
        module: [{
          required: true,
          message: '请选择所属模块',
          trigger: 'change',
        }],
		can_autoed: [{
		  required: true,
		  message: '请选择用例类型',
		  trigger: 'change',
		}],
		auto_status: [{
		  required: true,
		  message: '请选择自动化状态',
		  trigger: 'change',
		}],
		case_status: [{
		  required: true,
		  message: '请选择用例状态',
		  trigger: 'change',
		}],
        tag: [{
          required: true,
          message: '请选择用例标签',
          trigger: 'change',
        }],
		owner: [{
		  required: true,
		  message: '请选择用例负责人',
		  trigger: 'change',
		}],
      },
      caseFormTmp:{
        project: '',
        id: '',
        module: '',
        name: '',
        tag: '',
        owner: '',
        setup_condition: '',
        case_mark: '',
        step_text: '',
        step_table: [],
        can_autoed: 3,
        auto_status: 4,
        case: [],
        step_type: 2
      },
      editCaseVisible: false,
      moduleEditProps:{
        emitPath: false,
        value: 'id',
        label: 'name',
        checkStrictly: true,
      },
	  automationTypes: [
	    { label: '接口自动化', value: '1' },
	    { label: 'Web自动化', value: '2' },
	    { label: 'App自动化', value: '3' },
	    { label: '造数脚本', value: '4' },
	    { label: '性能测试', value: '5' },
	  ],
      permission: {},
      caseSearch:{
        name: '',
        service: '',
        method: '',
        url: '',
        project: '',
        module_list: [],
        module: '',
		    auto_status: '',
        case_status: '',
        recent_test_result: '',
		    owner: '',
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
	  multipleSelection: [],
      caseTitle: '新增功能用例',
      moduleTitle: '',
      case_list: [],
      user_list: [],
      service_list: [],
      plant_module_list: [],
      role_names: [],
	  auto_case_list: [],
	  batchDialogVisible: false,
	  batchDialogType: '',
	  batchDialogTitle: '',
	  batchDeleteDialogVisible: false,
	  batchDeleting: false,
	  batchForm: {
	    owner: null,
	    auto_status: null,
	    module: null,
	    tag: [],
	  },
	  scenarioGenVisible: false,
	  scenarioGenForm: {
	    modes: ['api'],
	    extra_requirement: '',
	  },
	  scenarioAiConfigs: [],
	  scenarioAiConfigId: '',
	  scenarioGenerating: false,
	}
  },
  components: {
    Refresh,
    Search,
    Plus,
    View,
    Delete,
    EditPen,
    CopyDocument,
    Setting,
    Expand,
    Fold,
	FullText,
	FunCaseTable,
	CaseList,
    SuccessFilled,
    ArrowDown
  },
  methods:{
    ...mapActions(['getRolePermission']),

    handleTypeChange() {
      this.page_size_params.page = 1
      this.getFCases()
    },
	
	handleSelectionChange(val) {
	    this.multipleSelection = val
	},

	handleBatchCommand(command) {
	  if (command === 'delete') {
	    this.batchDeleteDialogVisible = true
	    return
	  }
	  this.batchDialogType = command
	  const titleMap = {
	    owner: '批量修改负责人',
	    auto_status: '批量修改自动化状态',
	    module: '批量修改模块',
	    tag: '批量添加标签',
	  }
	  this.batchDialogTitle = titleMap[command] || '批量操作'
	  this.batchForm = { owner: null, auto_status: null, module: null, tag: [] }
	  this.batchDialogVisible = true
	},

	async confirmBatchDelete() {
	  this.batchDeleting = true
	  const ids = this.multipleSelection.map(c => c.id)
	  console.log('[批量删除] 开始, ids=', ids, '数量=', ids.length)
	  let successCount = 0
	  let failCount = 0
	  for (const id of ids) {
	    try {
	      console.log(`[批量删除] 删除 id=${id} ...`)
	      const response = await this.$api.deleteFCase(id)
	      console.log(`[批量删除] id=${id} 响应:`, response.status, response.data)
	      if (response.status === 204) {
	        successCount++
	      } else {
	        failCount++
	      }
	    } catch (err) {
	      console.error(`[批量删除] id=${id} 失败:`, err)
	      failCount++
	    }
	  }
	  console.log(`[批量删除] 完成, 成功=${successCount}, 失败=${failCount}`)
	  this.batchDeleteDialogVisible = false
	  this.batchDeleting = false
	  this.getFCases()
	  if (failCount === 0) {
	    ElMessage({ type: 'success', message: `成功删除 ${successCount} 条用例` })
	  } else {
	    ElMessage({ type: 'warning', message: `删除完成：成功 ${successCount} 条，失败 ${failCount} 条` })
	  }
	},

	async confirmBatchUpdate() {
	  const ids = this.multipleSelection.map(item => item.id)
	  const params = { ids }
	  let fieldLabel = ''
	  if (this.batchDialogType === 'owner') {
	    if (!this.batchForm.owner) {
	      ElMessage.warning('请选择负责人')
	      return
	    }
	    params.owner = this.batchForm.owner
	    fieldLabel = '负责人'
	  } else if (this.batchDialogType === 'auto_status') {
	    if (this.batchForm.auto_status === null) {
	      ElMessage.warning('请选择自动化状态')
	      return
	    }
	    params.auto_status = this.batchForm.auto_status
	    fieldLabel = '自动化状态'
	  } else if (this.batchDialogType === 'module') {
	    if (this.batchForm.module === null) {
	      ElMessage.warning('请选择模块')
	      return
	    }
	    if (this.batchForm.module < 0) {
	      ElMessage.error('所属模块不能选择根节点')
	      return
	    }
	    params.module = this.batchForm.module
	    fieldLabel = '模块'
	  } else if (this.batchDialogType === 'tag') {
	    if (!this.batchForm.tag || this.batchForm.tag.length === 0) {
	      ElMessage.warning('请选择标签')
	      return
	    }
	    params.tag = this.batchForm.tag
	    fieldLabel = '标签'
	  }
	  const response = await this.$api.batchUpdateFuncCases(params)
	  if (response.status === 200) {
	    ElMessage.success(`成功修改 ${ids.length} 个用例的${fieldLabel}`)
	    this.batchDialogVisible = false
	    this.getFCases()
	  }
	},

	async updateSingleField(row, field, value) {
	  const params = { ids: [row.id] }
	  params[field] = value
	  const response = await this.$api.batchUpdateFuncCases(params)
	  if (response.status === 200) {
	    ElMessage.success('修改成功')
	    this.getFCases()
	  }
	},
	getOwnerClass(userId) {
	  if (!userId) return 'owner-none'
	  const palette = [
	    'owner-1', 'owner-2', 'owner-3', 'owner-4',
	    'owner-5', 'owner-6', 'owner-7', 'owner-8',
	  ]
	  const idx = (Number(userId) % palette.length + palette.length) % palette.length
	  return palette[idx]
	},
	getOwnerIndicatorClass(userId) {
	  if (!userId) return 'info'
	  const palette = ['primary', 'purple', 'danger', 'success', 'cyan', 'warning', 'info', 'orange']
	  const idx = (Number(userId) % palette.length + palette.length) % palette.length
	  return palette[idx]
	},
	
	chooseFuncManyCase(){
		// this.$emit('update:chooseCaseVisible', false)
		this.$emit('setFuncManyCaseData', this.multipleSelection)
	},
	
	setCaseData(caseData) {
    if (this.caseForm.case.includes(caseData.id)) {
        // 使用 Element Plus 的提示组件
        this.$message.warning('该用例已关联')
        return // 直接返回，不执行后面的添加操作
      }
    this.caseForm.case.push(caseData.id)
    this.caseForm.case_detail.push(caseData)
	},

  setManyCaseData(manyCaseData){
			let duplicateCount = 0
			let newCaseIds = []
			for (const caseData of manyCaseData) {
				if (this.caseForm.case.includes(caseData.id)) {
					duplicateCount++
					continue
				}
				this.caseForm.case.push(caseData.id)
				this.caseForm.case_detail.push(caseData)
				newCaseIds.push(caseData.id)
			}
			if (newCaseIds.length === 0) {
				this.$message.warning('所选用例已全部存在，无需重复添加')
			} else if (duplicateCount > 0) {
				this.$message.success(`成功添加 ${newCaseIds.length} 个用例（跳过 ${duplicateCount} 个已存在的用例）`)
			} else {
				this.$message.success(`成功添加 ${newCaseIds.length} 个用例`)
			}
	},
	
	chooseCaseId(caseData){
	  // this.$emit('update:chooseFuncCaseVisible', false)
	  this.$emit('setFuncCaseData', caseData)
	},
	
	removeCase(scope) {
		ElMessageBox.confirm(
		  '确定移除该用例?',
		  '确认移除',
		  {
		    confirmButtonText: '确认移除',
		    cancelButtonText: '取消',
		    type: 'warning',
		    confirmButtonClass: 'el-button--danger',
		    customClass: 'confirm-dialog'
		  }
		).then(async() => {
		  const index = scope.$index
		  const id = scope.row.id
		  
		  // 根据索引从 case_detail 中移除
		  if (Array.isArray(this.caseForm.case_detail)) {
		    this.caseForm.case_detail.splice(index, 1)
		  }
		  
		  // 根据 id 从 case 中移除
		  if (Array.isArray(this.caseForm.case)) {
		    const idIndex = this.caseForm.case.indexOf(id);
			if (idIndex !== -1) {
			  this.caseForm.case.splice(idIndex, 1);
			}
		  }
		}).catch(() => {})
	    
	},
	
	caseTypeChange(value){
		if(value ===3){
			this.caseForm.auto_status = 4
		}else{
			console.log(value, '1111', this.caseForm.auto_status)
			if (this.caseForm.auto_status === 4){
				this.caseForm.auto_status = 3
			}
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
	  this.getFCases()
	},
    
    getTypeLabel(type) {
      const typeObj = this.automationTypes.find(t => t.value === type)
      return typeObj ? typeObj.label : ''
    },
    
    getTypeTagType(typeName) {
      const typeMap = {
        '1': '',
        '2': 'success',
        '3': 'warning',
        '4': 'info',
        '5': 'danger'
      }
      const typeKey = this.automationTypes.find(t => t.label === typeName)?.value || 'API'
      return typeMap[typeKey] || ''
    },
    
    handleCurrentChange(page) {
      this.page_size_params.page = page
      this.getFCases()
    },
    
	handleChange(newValue) {
		  console.log('前置条件已更新:', newValue)
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
      this.getCases()
    },
    
    getTagType(tagName) {
      if (!tagName) return ''
      const colors = ['', 'success', 'info', 'warning', 'danger']
      const hash = tagName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
      return colors[hash % colors.length]
    },

	getCaseStatusName(status) {
	  const map = { 1: '待修改', 2: '待评审', 3: '已评审' }
	  return map[status] || '-'
	},

	getTagColorClass(tagName) {
	  if (!tagName) return 'info'
	  const colors = ['primary', 'success', 'warning', 'info', 'danger']
	  const hash = tagName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
	  return colors[hash % colors.length]
	},
	
	goToCreatePlant(){
		this.$router.push({name: 'plant'})
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
    
    save(){
      if (this.module_node.action === 'add'){
        this.createModule()
      }else if(this.module_node.action === 'edit'){
        this.updateModule()
      }
    },
	
	saveFCase(){
	  if (this.caseForm.id === ''){
	    this.createFCase()
	  }else{
	    this.updateFCase()
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
    
    filterNode(value, data) {
      if (!value) return true
      return data?.name?.includes(value) || false
    },
    
    moduleSelect(node){
      if (!node) {
        this.selectNode = null
        this.caseSearch.module_list = []
        this.getCases(false)
        return
      }
      // 如果点击的是已选中的节点，取消选中
      if (this.selectNode === node.id) {
        this.$refs.treeRef?.setCurrentKey(null)
        this.selectNode = null
        this.caseSearch.module_list = []
        localStorage.removeItem('case_node')
        this.getCases(false)
        return
      }
      localStorage.setItem('case_node', JSON.stringify(node))
      this.selectNode = node.id
      if (this.includeChildren) {
        this.caseSearch.module_list = this.getAllIds(node)
      } else {
        this.caseSearch.module_list = [node.id]
      }
      this.getCases(false)
    },
    
    onIncludeChildrenChange() {
      const node = this.$refs.treeRef?.getCurrentNode()
      if (node) {
        if (this.includeChildren) {
          this.caseSearch.module_list = this.getAllIds(node)
        } else {
          this.caseSearch.module_list = [node.id]
        }
        this.getCases(false)
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
    
    search(){
      this.getFCases()
    },
    
    async copy(row_data){
      this.caseForm = {...row_data}
      this.caseForm.name = this.caseForm.name + '副本'
	  this.caseForm.project = this.projectInfo.id
	  const response = await this.$api.createFCase(this.caseForm)
	  if (response.status === 201){
	    this.getFCases()
	    ElMessage({message: "复制成功", type: 'success'})
	  }
    },
    
    reset(){
      for(let key in this.caseSearch){
        if(key === 'module_list'){
          continue
        }else if(key === 'tag'){
          this.caseSearch.tag = []
        }else{
          this.caseSearch[key] = ''
        }
      }
    },
    
    editCase(row_data){
      this.editCaseVisible = true
      this.caseView = false
      this.caseTitle = '编辑功能用例'
      this.activeNames = '2'
      this.caseForm = {...row_data}
      this.$router.replace({ query: { ...this.$route.query, action: 'edit', id: row_data.id } })
      this.$nextTick(() => {
        if (this.$refs.caseRef) {
          this.$refs.caseRef.clearValidate()
        }
      })
    },
    
    viewCase(row_data){
      this.editCaseVisible = true
      this.caseTitle = '查看功能用例'
      this.caseView = true
      this.activeNames = '2'
      this.caseForm = {...row_data}
      this.$router.replace({ query: { ...this.$route.query, action: 'view', id: row_data.id } })
    },

	onDrawerClosed() {
		const query = { ...this.$route.query }
		delete query.action
		delete query.id
		this.$router.replace({ query })
	},

    // ===== AI生成场景脚本 =====
    async openScenarioGen() {
      if (!this.caseForm.id) return
      this.scenarioGenVisible = true
      this.scenarioGenForm = {
        modes: ['api'],
        extra_requirement: '',
      }
      // 加载AI配置，默认选中默认配置
      if (!this.scenarioAiConfigs.length) {
        const res = await this.$api.getAiConfigs({ is_active: true, project: this.projectInfo.id })
        if (res.status === 200) {
          this.scenarioAiConfigs = res.data.results || res.data.result || []
        }
      }
      const def = this.scenarioAiConfigs.find(c => c.is_default)
      this.scenarioAiConfigId = def ? def.id : (this.scenarioAiConfigs[0] ? this.scenarioAiConfigs[0].id : '')
    },

    async submitScenarioGen() {
      if (!this.scenarioGenForm.modes.length) {
        ElMessage({ message: '请至少选择一种生成模式', type: 'warning' })
        return
      }
      if (!this.scenarioAiConfigId) {
        ElMessage({ message: '请选择AI模型', type: 'warning' })
        return
      }
      this.scenarioGenerating = true
      try {
        const res = await this.$api.aiGenerateScenarioCase({
          project_id: this.projectInfo.id,
          func_case_id: this.caseForm.id,
          ai_config_id: this.scenarioAiConfigId,
          module_id: this.caseForm.module,
          mode: this.scenarioGenForm.modes,
          extra_requirement: this.scenarioGenForm.extra_requirement,
        })
        if (res.status === 200) {
          ElMessage({ message: 'AI场景脚本生成任务已提交，生成完成后可在消息中心查看', type: 'success' })
          this.scenarioGenVisible = false
        } else {
          const detail = res.data && res.data.detail
          ElMessage({ message: detail || '提交失败，请稍后重试', type: 'error' })
        }
      } catch (e) {
        ElMessage({ message: '提交失败，请稍后重试', type: 'error' })
      } finally {
        this.scenarioGenerating = false
      }
    },
    
    addCase(){
      const node = this.$refs.treeRef.getCurrentNode()
      this.editCaseVisible = true
      this.caseView = false
      this.caseTitle = '新增功能用例'
      this.activeNames = '2'
      this.caseForm = {
        project: this.projectInfo.id,
        id: '',
        module: node ? node.id : '',
        name: '',
        tag: [],
        owner: this.userInfo.user_id,
        setup_condition: '',
        case_mark: '',
        step_text: '',
        step_table: [],
        can_autoed: 3,
        auto_status: 4,
        case_status: 2,
        case: [],
        case_detail: [],
        step_type: 2,
      }
      this.$nextTick(() => {
        if (this.$refs.caseRef) {
          this.$refs.caseRef.clearValidate()
        }
      })
    },
    
    async createFCase(){
      if(this.caseForm.module < 0){
        ElMessage({message: "所属模块不能选择根节点", type: 'error'})
        return 
      }
      this.$refs['caseRef'].validate(async (valid, fields)=>{
        if(valid){
          this.caseForm.project = this.projectInfo.id
          const response = await this.$api.createFCase(this.caseForm)
          if (response.status === 201){
            this.editCaseVisible = false
            this.getFCases()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
    },
    
    async updateFCase(){
      if(this.caseForm.module < 0){
        ElMessage({message: "所属模块不能选择根节点", type: 'error'})
        return 
      }
      this.$refs['caseRef'].validate(async (valid, fields)=>{
        if(valid){
          const response = await this.$api.updateFCase(this.caseForm.id, this.caseForm)
          if (response.status === 200){
            this.editCaseVisible = false
            this.getFCases()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
    },

    async approveCase(){
      this.$refs['caseRef'].validate(async (valid) => {
        if (!valid) return
        this.loading = true
        this.caseForm.case_status = 2
        try {
          const response = await this.$api.updateFCase(this.caseForm.id, this.caseForm)
          if (response.status === 200){
            ElMessage({message: '审核通过，状态已更新为待评审', type: 'success'})
            await this.getFCases()
            this.openNextPendingCase(1, '全部用例审核完成')
          }
        } catch (e) {
          ElMessage({message: '操作失败', type: 'error'})
        } finally {
          this.loading = false
        }
      })
    },

    async reviewCase(){
      this.$refs['caseRef'].validate(async (valid) => {
        if (!valid) return
        this.loading = true
        this.caseForm.case_status = 3
        try {
          const response = await this.$api.updateFCase(this.caseForm.id, this.caseForm)
          if (response.status === 200){
            ElMessage({message: '评审通过，状态已更新为已评审', type: 'success'})
            await this.getFCases()
            this.openNextPendingCase(2, '全部用例评审完成')
          }
        } catch (e) {
          ElMessage({message: '操作失败', type: 'error'})
        } finally {
          this.loading = false
        }
      })
    },

    openNextPendingCase(targetStatus, doneMessage){
      const currentId = this.caseForm.id
      const userId = this.userInfo.user_id
      const nextCase = this.case_list.results.find(c =>
        c.create_by === userId &&
        c.id !== currentId &&
        c.case_status === targetStatus
      )
      if (nextCase){
        this.editCase(nextCase)
      } else {
        this.editCaseVisible = false
        ElMessage({message: doneMessage, type: 'success'})
      }
    },
    
    async deleteCase(id){
      ElMessageBox.confirm(
        '确定删除此用例？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async() => {
        const response = await this.$api.deleteFCase(id)
        if (response.status === 204){
          this.getFCases()
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
    
    async getFCases(){
      this.caseSearch.project = this.projectInfo.id
      const data = Object.assign(this.caseSearch, this.page_size_params, this.sort_params)
      this.caseSearch.module = (this.caseSearch.module_list || []).join(',')
      const response = await this.$api.getFCases(data)
      if (response.status === 200){
        this.case_list = {...response.data}
      }
    },
    
    async getTags(){
      const response = await this.$api.getTags({project: this.projectInfo.id})
      if (response.status === 200){
        this.tag_list = response.data.results
      }
    },
    
    editStep(row, column, event){
      localStorage.setItem('case_model', 'tree')
      this.$router.push({name: 'caseStepEdit', query: {id: row.id}})
    },
    
    editStepTwo(row){
      this.editCase(row)
    },

    async check_permission(path){
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
	
	async getCases(){
    this.caseSearch.module = (this.caseSearch.module_list || []).join(',')
    const data = Object.assign(this.caseSearch, this.page_size_params, this.sort_params)
	  const response = await this.$api.getCases(data)
	  if (response.status === 200){
	    this.case_list = {...response.data.results}
	  }
	},

  // 【AI 用例可见性修复】统一的 AI 用例定位逻辑：
  // 清空模块树记忆（localStorage['case_node']）与模块筛选，并只筛"待修改"(case_status=1)。
  // 原因：AI 生成用例固定落在 case_status=1(待修改) 且可能位于用户当前未选中的模块，
  // 沿用上次记忆的模块节点会导致新生成的用例在列表里"看不见"。
  applyAiFilter() {
    localStorage.removeItem('case_node')
    this.selectNode = null
    this.caseSearch.module_list = []
    this.caseSearch.case_status = 1
    this.$nextTick(() => {
      this.$refs.treeRef?.setCurrentKey(null)
    })
  },

  // 应用模块树记忆：非 AI 场景下的默认行为（保持原有语义）
  applyRememberedModule() {
    const node = JSON.parse(localStorage.getItem('case_node'))
    if (node) {
      this.selectNode = node.id
      this.$nextTick(() => {
        if (this.$refs.treeRef) {
          this.$refs.treeRef.setCurrentKey(node.id)
        }
      })
      this.caseSearch.module_list = this.getAllIds(node)
    }
  },

  // URL query 路由分发（mounted 与 query 变化时共用，保证幂等）
  async applyRouteQuery() {
    const { filter, action, id } = this.$route.query
    if (filter === 'ai') {
      this.applyAiFilter()
      await this.getFCases()
      return
    }
    await this.getFCases()
    // URL 参数打开编辑/查看弹窗
    if (action && id) {
      const res = await this.$api.getFCase(id)
      if (res.status === 200) {
        const data = { ...res.data.result, id: id }
        if (action === 'view') {
          this.viewCase(data)
        } else if (action === 'edit') {
          this.editCase(data)
        }
      }
    }
  },
  },
  async mounted() {
    // 【AI 用例可见性修复 - 兜底】生成完成通知若以"整页跳转"打开链接，
    // RouterLink/href 的 hash 变化可能在组件挂载前就被 hashchange 消费掉，
    // 导致 mounted 里读到的 $route.query 不含 filter。
    // 这里在 window 层监听 hashchange（capture 阶段），一旦 URL 里出现
    // filter=ai 就直接应用筛选，不依赖路由时序。
    this._onHashChange = () => {
      if (window.location.hash.indexOf('filter=ai') !== -1) {
        this.applyAiFilter()
        this.getFCases()
      }
    }
    window.addEventListener('hashchange', this._onHashChange, true)

    this.check_permission()
    this.getPlantModule()
    this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
    // 【AI 用例可见性修复】支持通过 URL 参数强制清空模块/状态筛选。
    // 场景：AI 助手生成用例后跳转过来，用 case_mark='AI生成' 或 case_status=1 筛选，
    // 若沿用 localStorage 记忆的模块节点，新用例会因模块不同而"看不见"。
    const { filter } = this.$route.query
    if (filter === 'ai') {
      this.applyAiFilter()
    } else {
      this.applyRememberedModule()
    }
    await this.getFCases()
    this.getTags()
    // URL 参数打开编辑/查看弹窗
    const { action, id } = this.$route.query
    if (action && id) {
      const res = await this.$api.getFCase(id)
      if (res.status === 200) {
        const data = { ...res.data.result, id: id }
        if (action === 'view') {
          this.viewCase(data)
        } else if (action === 'edit') {
          this.editCase(data)
        }
      }
    }
  },
  beforeUnmount() {
    window.removeEventListener('hashchange', this._onHashChange, true)
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

.tree-search-input :deep(.el-input__inner) {
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

.tree-search-input :deep(.el-input__inner:focus) {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
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

.elegant-tree :deep(.el-tree-node.is-current > .el-tree-node__content::before) {
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
  min-width: 0; /* 允许内容区域收缩 */
  max-width: calc(100% - 40px); /* 限制最大宽度，为操作按钮留出空间 */
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
  max-width: calc(100% - 32px); /* 留出右侧按钮空间 */
}

.node-actions {
  flex-shrink: 0; /* 防止操作按钮被挤压 */
  opacity: 0;
  transition: opacity 0.3s ease;
  margin-left: 8px; /* 添加左边距，确保与文本有间隔 */
}

.elegant-tree :deep(.el-tree-node__content:hover .node-actions) {
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

/* drawer 左右分栏布局 */
.drawer-split-layout {
  display: flex;
  gap: 16px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.drawer-left {
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
}

.drawer-left-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
  padding-right: 4px;
}

.drawer-left-content::-webkit-scrollbar {
  width: 8px;
}

.drawer-left-content::-webkit-scrollbar-track {
  background: var(--qm-bg-3);
  border-radius: 4px;
}

.drawer-left-content::-webkit-scrollbar-thumb {
  background: var(--qm-line-strong);
  border-radius: 4px;
}

.drawer-left-content::-webkit-scrollbar-thumb:hover {
  background: var(--qm-text-3);
}

.drawer-right::-webkit-scrollbar {
  width: 6px;
}

.drawer-right::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 4px;
}

.drawer-right::-webkit-scrollbar-thumb {
  background: var(--qm-line-strong);
  border-radius: 4px;
}

.drawer-right::-webkit-scrollbar-thumb:hover {
  background: var(--qm-line-strong);
}

.drawer-right {
  width: 320px;
  flex-shrink: 0;
  background: var(--qm-bg-2);
  padding: 20px 20px 40px 20px;
  border: 1px solid var(--qm-bg-3);
  border-radius: 12px;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.drawer-right-title span {
  font-size: 18px;
  font-weight: 700;
  color: var(--qm-text-1);
  padding-left: 14px;
  padding-bottom: 5px;
  position: relative;
  display: inline-block;
  line-height: 1.5;
}

.drawer-right-title span::before {
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

.drawer-right .step-base-info {
  background: transparent;
  padding: 0;
  border-radius: 0;
  border: none;
  margin-bottom: 0;
}

.drawer-right .step-base-info .el-form-item {
  margin-bottom: 16px;
}

.drawer-right .step-base-info :deep(.el-form-item__label) {
  font-weight: 400;
  color: var(--qm-text-2);
  font-size: 13px;
  padding-bottom: 4px;
}

.drawer-right .step-base-info .meta-form-item :deep(.el-input__wrapper) {
  background: var(--qm-bg-1);
  box-shadow: none;
}

.drawer-right .step-base-info .meta-form-item :deep(.el-input__inner) {
  color: var(--qm-text-2);
  -webkit-text-fill-color: var(--qm-text-2);
}

.drawer-right .meta-divider-line {
  margin: 8px 0 20px 0;
}

.drawer-right .el-select,
.drawer-right .el-cascader,
.drawer-right .el-input {
  width: 100%;
}

.step-detail-card {
  border: none;
  border-radius: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.step-detail-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--qm-bg-3);
  background: var(--qm-bg-2);
}

.step-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--qm-text-1);
}

.step-collapse-panel {
  padding: 24px 0px;
  background: var(--qm-bg-2);
}

.step-collapse-panel :deep(.el-collapse-item__header) {
  font-weight: 600;
  background: var(--qm-bg-2);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 8px;
  border: 1px solid var(--qm-line-strong);
}

.step-collapse-panel :deep(.el-collapse-item__content) {
  padding: 20px;
  background: var(--qm-bg-2);
  border-radius: 8px;
  border: 1px solid var(--qm-line-strong);
  border-top: none;
  margin-bottom: 16px;
}

/* 1. 确保el-collapse-item__header固定高度，但保留原有布局 */
.step-collapse-panel :deep(.el-collapse-item__header) {
  /* 固定高度属性 */
  height: 60px !important; /* 稍微调高一点，给内边距留空间 */
  min-height: 60px !important;
  max-height: 60px !important;
  
  /* 恢复原有的内边距和布局 */
  padding: 0 20px !important; /* 保持原有的左右内边距 */
  margin: 0 !important;
  box-sizing: border-box !important;
  
  /* 使用flex确保内容垂直居中 */
  display: flex !important;
  align-items: center !important;
  flex-wrap: nowrap !important;
  
  /* 防止内容溢出 */
  overflow: hidden !important;
  
  /* 固定字体，防止缩放 */
  font-size: 15px !important;
  font-weight: 600 !important;
  color: var(--qm-text-1) !important;
  
  /* 恢复原有的背景色和边框 */
  background: var(--qm-bg-1) !important;
  border-radius: 8px !important;
  border: 1px solid var(--qm-line-strong) !important;
  margin-bottom: 8px !important;
  
  /* 保持原有的过渡效果 */
  transition: all 0.3s ease !important;
}

/* 抽屉主体样式 - 已移至全局样式块（因 append-to-body 导致 scoped 深度选择器失效） */

/* 内容卡片、el-card__body、el-form、左侧滚动区、底部按钮样式 */
/* 已移至全局样式块（因 append-to-body 导致 scoped :deep() 深度选择器对 Element Plus 内部元素失效） */

.step_item_card {
  background: var(--qm-bg-2);
  margin: 0px 10px 20px 10px;
  border: none;
  border-radius: 16px;
  overflow: hidden;
}

/* 整体样式 */
.step .content-header {

  border-bottom: 1px solid var(--qm-bg-3);
  background: var(--qm-bg-2);
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex-shrink: 0;
}

/* 第一行：标题 + 按钮 */
.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: nowrap;
  min-height: 40px;
}

/* 标题表单项（去除默认 margin） */
.title-form-item {
	margin-bottom: 0;
}

.title-form-item :deep(.el-form-item__content) {
	line-height: normal;
}

/* 创建/更新信息区域（标题下方右对齐） */
.case-meta-section {
	display: flex;
	justify-content: flex-end;
	margin-top: 8px;
}

/* 第二行：用例信息 */
.header-bottom {
  display: flex;
  align-items: center;
  gap: 8px;
}

.case-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 13px;
  color: var(--qm-text-2);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-label {
  color: var(--qm-text-3);
  font-weight: 500;
}

.meta-value {
  color: var(--qm-text-2);
  font-weight: 600;
}

.meta-time {
  color: var(--qm-line-strong);
  font-size: 12px;
}

.meta-divider {
  width: 1px;
  height: 14px;
  background: var(--qm-line-strong);
}

.section-divider {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 12px 0 12px 0;
  padding: 0 8px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--qm-text-2);
}

.section-icon {
  color: var(--qm-text-3);
  width: 16px;
  height: 16px;
}

.step-base-info {
  background: var(--qm-bg-2);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid var(--qm-line-strong);
  margin-bottom: 20px;
}

/* 2. 修复section-divider的布局 */
.step-collapse-panel :deep(.el-collapse-item__header .section-divider) {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  width: 100% !important;
  height: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
  
  /* 确保内部元素不会撑开高度 */
  line-height: 1 !important;
}

/* 3. 修复section-title的样式，确保左边框伪元素正确显示 */
.step-collapse-panel :deep(.section-title) {
  margin: 0 !important;
  padding: 0 !important;
  padding-left: 20px !important; /* 为左边蓝色竖条留出空间 */
  font-size: 16px !important;
  font-weight: 600 !important;
  color: var(--qm-text-2) !important;
  line-height: 1.5 !important;
  
  /* 确保垂直居中 */
  display: flex !important;
  align-items: center !important;
  position: relative !important;
  height: 100% !important;
}

/* 4. 修复section-title::before左边蓝色竖条的位置和大小 */
.step-collapse-panel :deep(.section-title::before) {
  content: '';
  position: absolute;
  left: 0; /* 紧贴父元素左侧 */
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px; /* 固定高度，不随内容变化 */
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 2px;
  margin: 0 !important;
}

.type-radio-group :deep(.el-radio-button__inner) {
  width: 100%;
  padding: 16px 12px;
  border-radius: 12px !important;
  border: 2px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  color: var(--qm-text-2);
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.type-radio-group >>> .el-radio-button__original-radio:checked + .el-radio-button__inner {
  border-color: #f59e0b;
  background: linear-gradient(135deg, var(--qm-warning-soft) 0%, var(--qm-warning-soft-2) 100%);
  color: #b45309;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
  transform: translateY(-2px);
}

.type-item-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.type-icon {
  width: 24px;
  height: 24px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.type-icon-1 {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M21 10c-1.1 0-2 .9-2 2v3H5v-3c0-1.1-.9-2-2-2s-2 .9-2 2v5c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2v-5c0-1.1-.9-2-2-2zm-3-5H6c-1.1 0-2 .9-2 2v2.15c1.16.41 2 1.51 2 2.82V14h12v-2.03c0-1.3.84-2.4 2-2.82V7c0-1.1-.9-2-2-2z'/%3E%3C/svg%3E");
}

.type-icon-2 {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm-5 14H4v-4h11v4zm0-5H4V9h11v4zm5 5h-4V9h4v9z'/%3E%3C/svg%3E");
}

.type-icon-3 {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z'/%3E%3C/svg%3E");
}

.type-icon-4 {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%236b7280' d='M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z'/%3E%3C/svg%3E");
}

.type-icon-5 {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ef4444' d='M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z'/%3E%3C/svg%3E");
}

.type-text {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}

/* 不同类型按钮的样式 */
.type-radio-group :deep(.type-1 .el-radio-button__inner) {
  border-color: var(--qm-warning-line);
  background: var(--qm-warning-soft);
  color: #b45309;
}

.type-radio-group >>> .type-2 .el-radio-button__inner {
  border-color: #d1fae5;
  background: #ecfdf5;
  color: #065f46;
}

.type-radio-group :deep(.type-3 .el-radio-button__inner) {
  border-color: var(--qm-warning-line);
  background: var(--qm-warning-soft);
  color: #92400e;
}

.type-radio-group :deep(.type-4 .el-radio-button__inner) {
  border-color: var(--qm-bg-3);
  background: var(--qm-bg-1);
  color: #374151;
}

.type-radio-group :deep(.type-5 .el-radio-button__inner) {
  border-color: #fee2e2;
  background: var(--qm-red-soft);
  color: #991b1b;
}

.type-radio-group :deep(.type-1 .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  border-color: #f59e0b;
  background: linear-gradient(135deg, var(--qm-warning-soft) 0%, var(--qm-warning-soft-2) 100%);
  color: #b45309;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
}

.type-radio-group :deep(.type-2 .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  border-color: #10b981;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  color: #065f46;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.type-radio-group :deep(.type-3 .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  border-color: #f59e0b;
  background: linear-gradient(135deg, var(--qm-warning-soft) 0%, var(--qm-warning-soft-2) 100%);
  color: #92400e;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
}

.type-radio-group :deep(.type-4 .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  border-color: var(--qm-text-2);
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  color: #374151;
  box-shadow: 0 4px 12px rgba(107, 114, 128, 0.2);
}

.type-radio-group :deep(.type-5 .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: #991b1b;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

/* 筛选卡片 */
.filter-card {
  background: var(--qm-bg-2);
  border: none;
  border-radius: 16px;
  overflow: hidden;
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

.icon-case,
.icon-result,
.icon-folder {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-case {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
}

.icon-result {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z'/%3E%3C/svg%3E");
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

.inline-form-item {
  margin-bottom: 25px;
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
  min-width: 100px;
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

.inline-label-text {
    white-space: nowrap;

}

.icon-tag,
.icon-creator,
.icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-tag {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z'/%3E%3C/svg%3E");
}

.icon-creator {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
}

.icon-updater {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E");
}

.inline-label-wrapper .icon-case {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.inline-label-wrapper .icon-tag {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
}

.inline-label-wrapper .icon-result {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.inline-label-wrapper .icon-creator {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.input-inline >>> .el-input__inner,
.select-inline >>> .el-input__inner {
  border-radius: 10px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-1);
  padding: 0 15px;
  box-shadow: none;
  transition: all 0.3s ease;
  flex: 1;
  margin-left: 12px;
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

.select-inline {
  flex: 1;
  margin-left: 12px;
}

/* 内容卡片 - 已在上方定义 */

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

/* 第一行：标题 + 按钮 */
.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: nowrap;
  min-height: 40px;
}

.case-title-area {
  flex: 1;
  min-width: 0;
  position: relative;
  padding-left: 12px;
}

/* 标题左侧蓝色竖线 */
.case-title-area::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(to bottom, #f59e0b, #d97706);
  border-radius: 2px;
}

/* 用例名称 - 保留左侧蓝色竖杠 */
.content-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--qm-text-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
  position: relative;
  padding-left: 16px;
}

/* 可编辑用例名称标题输入框 */
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
}

.case-title-input :deep(.el-input__wrapper):hover {
  background: var(--qm-bg-3);
}

.case-title-input :deep(.el-input__wrapper.is-focus) {
  background: var(--qm-bg-1);
  box-shadow: 0 0 0 2px #f59e0b inset;
}

.case-title-input :deep(.el-input__inner) {
  font-size: 18px;
  font-weight: 700;
  color: var(--qm-text-1);
  height: 40px;
  line-height: 40px;
}

.case-title-input :deep(.el-input__inner)::placeholder {
  font-size: 16px;
  font-weight: 400;
  color: var(--qm-text-3);
}

.case-title-input :deep(.is-disabled .el-input__wrapper) {
  background: transparent;
  box-shadow: none;
}

.case-title-input :deep(.is-disabled .el-input__inner) {
  color: var(--qm-text-1);
  cursor: default;
  -webkit-text-fill-color: var(--qm-text-1);
}

.content-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
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

.type-badge {
  background: linear-gradient(135deg, var(--qm-warning-soft) 0%, var(--qm-warning-soft-2) 100%);
  border: 1px solid #fde68a;
}

.type-badge .stat-value {
  color: #b45309;
  font-weight: 600;
}

.type-icon-small {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
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

.elegant-table :deep(.el-table__header-wrapper th) {
  background: linear-gradient(180deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  font-weight: 600;
  color: var(--qm-text-1);
  border-bottom: 1px solid var(--qm-line-strong);
  padding: 16px 0;
}

.elegant-table >>> .el-table__header-wrapper .cell {
  padding: 0 16px;
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row) {
  transition: all 0.3s ease;
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row:nth-child(even)) {
  background: var(--qm-bg-1);
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row:hover) {
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

.elegant-table :deep(.el-table__body-wrapper td) {
  border-bottom: 1px solid var(--qm-bg-3);
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

.type-icon-cell {
  width: 14px;
  height: 14px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  margin-right: 4px;
  vertical-align: -2px;
}

.case-link {
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
}

.case-link:hover {
  color: #f59e0b;
  text-decoration: underline;
}

.result-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 12px;
  border: none;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
  align-items: center;
  min-height: 32px;
}

.case-tag {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  border-width: 1px;
}

.no-tag {
  color: var(--qm-text-3);
  font-size: 13px;
}

/* 合并列样式 */
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

.action-btn.copy-btn:hover {
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

.action-btn.copy-btn {
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
  padding: 20px 24px 10px 10px;
  float: right;
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
  margin-bottom: 0px;
  min-height: 40px;
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

.elegant-pagination :deep(.el-pagination) {
  display: flex;
  align-items: center;
}

.elegant-pagination >>> .el-pagination__total {
  color: var(--qm-text-2);
  font-weight: 500;
  margin-right: 20px;
}

.elegant-pagination :deep(.el-pagination__sizes) {
  margin-right: 20px;
}

.elegant-pagination :deep(.el-pagination__sizes .el-input .el-input__inner) {
  border-radius: 8px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  box-shadow: none;
  height: 32px;
  line-height: 32px;
}

.elegant-pagination :deep(.el-pagination__sizes .el-input .el-input__inner:hover) {
  border-color: var(--qm-line-strong);
}

.elegant-pagination :deep(.el-pager li) {
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

.elegant-pagination :deep(.el-pagination__jump) {
  margin-left: 20px;
}

.elegant-pagination :deep(.el-pagination__jump .el-input .el-input__inner) {
  border-radius: 8px;
  border: 1px solid var(--qm-line-strong);
  box-shadow: none;
  height: 32px;
  line-height: 32px;
}

.elegant-pagination :deep(.el-pagination__jump .el-input .el-input__inner:hover) {
  border-color: var(--qm-line-strong);
}

/* 对话框样式 */
.elegant-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.elegant-dialog >>> .el-dialog__header {
  padding: 24px 24px 0;
  margin: 0;
}

.elegant-dialog :deep(.el-dialog__title) {
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
  padding: 0;
}

.dialog-form {
  margin: 0;
}


.dialog-form-item {
  margin-bottom: 22px;
}

.dialog-form-item :deep(.el-form-item__error) {
  position: relative;
  padding-top: 4px;
}

.dialog-form-item :deep(.el-form-item__label) {
  font-weight: 600;
  color: var(--qm-text-2);
  font-size: 14px;
}

.dialog-form-item:last-child {
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

.ai-alert {
  margin-bottom: 16px;
}

.ai-required {
  color: #ef4444;
  margin-left: 2px;
  font-weight: 600;
}

.icon-module,
.icon-tag-dialog {
  width: 16px;
  height: 16px;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-module {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z'/%3E%3C/svg%3E");
}

.icon-tag-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z'/%3E%3C/svg%3E");
}

.dialog-input >>> .el-input__inner,
.dialog-cascader >>> .el-input__inner,
.dialog-select >>> .el-input__inner {
  border-radius: 12px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  padding: 0 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.dialog-input >>> .el-input__inner:hover,
.dialog-cascader >>> .el-input__inner:hover,
.dialog-select >>> .el-input__inner:hover {
  border-color: var(--qm-line-strong);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-input >>> .el-input__inner:focus,
.dialog-cascader >>> .el-input__inner:focus,
.dialog-select >>> .el-input__inner:focus {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
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
  
  .type-radio-group >>> .el-radio-button {
    min-width: 120px;
  }
}

@media screen and (max-width: 768px) {
  .case-management-container {
    padding: 12px;
  }
  
  .type-radio-group {
    flex-direction: column;
  }
  
  .type-radio-group >>> .el-radio-button {
    width: 100%;
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
  }
  
  .inline-form-item {
    height: auto;
    flex-wrap: wrap;
    margin-bottom: 20px;
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
    flex-wrap: wrap;
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

/* ===== 批量删除弹窗内容 ===== */
.batch-delete-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 8px 0;
}

.batch-delete-icon {
  font-size: 48px;
  color: #ef4444;
  flex-shrink: 0;
  margin-top: 4px;
}

.batch-delete-text p {
  margin: 0;
  line-height: 1.6;
}

.batch-delete-count {
  font-size: 20px;
  font-weight: 700;
  color: #ef4444;
}

.batch-delete-tip {
  color: var(--qm-text-3);
  font-size: 14px;
  margin-top: 4px !important;
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

.type-filter-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
}

.filter-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both;
}

.content-card {
  flex: 1;
  background: var(--qm-bg-2);
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding-bottom: 0px;
  animation: slideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.3s both;
}

/* 列表页 content-card 的 el-card__body 调整底部 padding，让分页组件贴近卡片底部边框 */
.case-management-container .content-card :deep(.el-card__body) {
  padding-bottom: 0px;
}

/* 批量操作相关样式 */
.selected-count-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  font-size: 13px;
  font-weight: 600;
  margin-right: 12px;
}

.selected-count-badge .el-icon {
  font-size: 14px;
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

/* 行内编辑样式 */
.inline-edit-cell {
  cursor: pointer;
  display: inline-block;
  padding: 2px 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
  min-width: 40px;
  text-align: center;
}

.inline-edit-cell:hover {
  background: var(--qm-warning-soft);
  color: #f59e0b;
}

.inline-edit-wrapper {
  padding: 4px 0;
}

.inline-edit-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--qm-text-2);
  margin-bottom: 8px;
}

.add-tag-btn {
  padding: 2px 6px !important;
  color: #f59e0b !important;
  border: 1px dashed #fcd34d !important;
  border-radius: 4px !important;
  height: auto !important;
}

.add-tag-btn:hover {
  background: var(--qm-warning-soft) !important;
  border-color: #f59e0b !important;
}

.batch-form .el-form-item {
  margin-bottom: 0;
}

.scenario-mode-tip {
  width: 100%;
  font-size: 12px;
  color: var(--qm-text-3);
  line-height: 1.5;
  margin-top: 6px;
}

/* 状态徽章样式(参考 TestPlanDetail) */
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

/* 自动化状态颜色 */
.auto-status-1 {
  background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
}
.auto-status-2 {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}
.auto-status-3 {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}
.auto-status-4 {
  background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%);
}

/* 用例状态颜色 */
.case-status-1 {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}
.case-status-2 {
  background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%);
}
.case-status-3 {
  background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
}

/* 负责人颜色（参考自动化状态，按 user id 取模 8 套渐变） */
.owner-none { background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%); }
.owner-1 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.owner-2 { background: linear-gradient(135deg, #a78bfa 0%, #f97316 100%); }
.owner-3 { background: linear-gradient(135deg, #f472b6 0%, #ec4899 100%); }
.owner-4 { background: linear-gradient(135deg, #fb7185 0%, #e11d48 100%); }
.owner-5 { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); }
.owner-6 { background: linear-gradient(135deg, #22d3ee 0%, #d97706 100%); }
.owner-7 { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); }
.owner-8 { background: linear-gradient(135deg, #fb923c 0%, #ea580c 100%); }

/* 标签添加徽章 */
.tag-add-dropdown {
  display: inline-flex !important;
  align-items: center;
  position: relative;
  z-index: 10;
}

.tag-add-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 4px;
  font-size: 12px;
  outline: none;
}

.tag-add-badge .el-icon {
  pointer-events: none;
}

.tag-add-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

.tag-empty {
  padding: 16px;
  text-align: center;
  color: var(--qm-text-3);
  font-size: 13px;
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

/* 批量操作下拉菜单 popper 样式 */
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

.item-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--qm-text-2);
  transition: all 0.2s ease;
}

.batch-dropdown-item:hover .item-text {
  color: #f59e0b;
}

/* 行内编辑 popover 样式 */
.inline-edit-popper.el-popper {
  padding: 12px !important;
  border-radius: 10px !important;
  border: 1px solid var(--qm-bg-3) !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1) !important;
}

/* 状态下拉菜单 popper 样式(参考 TestPlanDetail) */
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

.status-dropdown-popper .status-indicator.danger {
  background: #ef4444;
}

.status-dropdown-popper .status-indicator.orange {
  background: #ea580c;
}

.status-dropdown-popper .status-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--qm-text-2);
}

/* 负责人下拉菜单 popper 样式（用户多时支持滚动） */
.owner-dropdown-popper.el-popper {
  padding: 8px !important;
  border-radius: 12px !important;
  border: none !important;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12) !important;
  max-height: 320px;
  overflow-y: auto;
}

.owner-dropdown-popper .el-dropdown-menu {
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  max-height: 300px;
  overflow-y: auto;
}

.owner-dropdown-popper .el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  margin: 2px 0;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.owner-dropdown-popper .el-dropdown-menu__item:hover {
  background: var(--qm-bg-3);
}

.owner-dropdown-popper .status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.owner-dropdown-popper .status-indicator.danger { background: #ef4444; }
.owner-dropdown-popper .status-indicator.warning { background: #f59e0b; }
.owner-dropdown-popper .status-indicator.primary { background: #f59e0b; }
.owner-dropdown-popper .status-indicator.success { background: #10b981; }
.owner-dropdown-popper .status-indicator.info { background: var(--qm-text-3); }
.owner-dropdown-popper .status-indicator.purple { background: #f97316; }
.owner-dropdown-popper .status-indicator.cyan { background: #d97706; }
.owner-dropdown-popper .status-indicator.orange { background: #ea580c; }

.owner-dropdown-popper .status-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--qm-text-2);
}

/* 标签添加下拉菜单 popper 样式 */
.tag-add-dropdown-popper.el-popper {
  padding: 8px !important;
  border-radius: 12px !important;
  border: none !important;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12) !important;
  max-height: 280px;
  overflow-y: auto;
}

.tag-add-dropdown-popper .el-dropdown-menu {
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}

.tag-add-dropdown-popper .el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  margin: 2px 0;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.tag-add-dropdown-popper .el-dropdown-menu__item:hover {
  background: var(--qm-bg-3);
}

.tag-add-dropdown-popper .status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-add-dropdown-popper .status-indicator.primary {
  background: #f59e0b;
}

.tag-add-dropdown-popper .status-indicator.success {
  background: #10b981;
}

.tag-add-dropdown-popper .status-indicator.warning {
  background: #f59e0b;
}

.tag-add-dropdown-popper .status-indicator.info {
  background: var(--qm-text-3);
}

.tag-add-dropdown-popper .status-indicator.danger {
  background: #ef4444;
}

.tag-add-dropdown-popper .status-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--qm-text-2);
}

/* ============================================
   抽屉样式 - 全局样式（因 append-to-body 导致 scoped 失效）
   参考 ApiEdit.vue 的 .api-drawer 布局
   ============================================ */

/* 抽屉主体 - 外层不滚动，使用 flex 布局 */
html body .el-drawer.fun-case-drawer .el-drawer__body,
html body .el-overlay.fun-case-drawer .el-drawer__body,
html body .el-overlay .fun-case-drawer .el-drawer__body {
  padding: 20px !important;
  overflow: hidden !important;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
}

/* 内容卡片 - flex 链第 1 层 */
html body .fun-case-drawer .content-card {
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
html body .fun-case-drawer .content-card .el-card__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 0;
  overflow: hidden;
}

/* el-form - flex 链第 3 层，传递 flex 高度 */
html body .fun-case-drawer .content-card .el-card__body > .el-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

/* drawer 左右分栏布局 - flex 链第 4 层 */
html body .fun-case-drawer .drawer-split-layout {
  display: flex;
  gap: 16px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: 20px 20px 0px 20px;
  box-sizing: border-box;
}

/* 左侧容器 - flex 链第 5 层 */
html body .fun-case-drawer .drawer-left {
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
}

/* 内容头部 - 固定高度，不参与 flex 收缩 */
html body .fun-case-drawer .content-header {
  padding: 20px 24px 20px 24px;
  background: var(--qm-bg-2);
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex-shrink: 0;
  border-bottom: 1px solid var(--qm-bg-3);
}

/* 左侧内容区 - flex 链第 6 层，唯一的滚动容器 */
html body .fun-case-drawer .drawer-left-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
  padding-right: 4px;
}

/* 左侧内容区滚动条样式 */
html body .fun-case-drawer .drawer-left-content::-webkit-scrollbar {
  width: 8px;
}

html body .fun-case-drawer .drawer-left-content::-webkit-scrollbar-track {
  background: var(--qm-bg-3);
  border-radius: 4px;
}

html body .fun-case-drawer .drawer-left-content::-webkit-scrollbar-thumb {
  background: var(--qm-line-strong);
  border-radius: 4px;
}

html body .fun-case-drawer .drawer-left-content::-webkit-scrollbar-thumb:hover {
  background: var(--qm-text-3);
}

/* 抽屉底部按钮 - 固定在底部，与卡片融为一体 */
html body .fun-case-drawer .drawer-footer {
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
</style>