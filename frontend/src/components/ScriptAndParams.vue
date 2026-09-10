<template>
  <!-- 查看函数体弹窗 -->
  <el-dialog v-model="viewFuncVisiable" title="查看函数体" width="1250px" z-index="99999999" :append-to-body="true">
    <BodyEdit :bind_case_data="[]" v-model="func_script" lang="python" height="600px"></BodyEdit>
  </el-dialog>

  <!-- depth >= 1时显示输入框 -->
  <div class="func-input-container" v-if="depth >= 1">
    <el-input
      v-model="localValue"
      @focus="handleFocus"
      @blur="handleBlur"
      size="large"
      class="input"
      placeholder="请输入参数值或选择引用"
    >
      <template #suffix>
        <div class="dropdown-wrapper">
          <el-dropdown @command="handleCommand" placement="bottom-end" trigger="click" class="custom-dropdown">
            <div class="dropdown-trigger">
              <el-icon :size="16" class="dropdown-icon">
                <Menu />
              </el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="custom-dropdown-menu">
                <el-dropdown-item :command="{ type: 'func_generate' }" v-if="depth === 0" class="dropdown-item">
                  <div class="dropdown-item-content">
                    <el-icon class="dropdown-item-icon"><MagicStick /></el-icon>
                    <span class="dropdown-item-text">参数构造器</span>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item :command="{ type: 'bind_enum' }" class="dropdown-item">
                  <div class="dropdown-item-content">
                    <el-icon class="dropdown-item-icon"><List /></el-icon>
                    <span class="dropdown-item-text">常量值引用</span>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item :command="{ type: 'bind_env_params' }" class="dropdown-item">
                  <div class="dropdown-item-content">
                    <el-icon class="dropdown-item-icon"><Setting /></el-icon>
                    <span class="dropdown-item-text">全局变量引用</span>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item :command="{ type: 'bind_step_params' }" v-if="!is_case_params" class="dropdown-item">
                  <div class="dropdown-item-content">
                    <el-icon class="dropdown-item-icon"><Connection /></el-icon>
                    <span class="dropdown-item-text">步骤变量引用</span>
                  </div>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </template>
    </el-input>
  </div>

  <!-- depth < 1时显示按钮下拉菜单 -->
  <div class="quick-action-container" v-if="depth < 1">
    <el-dropdown @command="handleCommand" class="quick-dropdown">
      <el-button type="success" class="dialog-confirm-btn">
        <!-- <el-icon><MagicStick /></el-icon> -->
		<span class="button-text">快捷变量引用</span>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu class="custom-dropdown-menu">
          <el-dropdown-item :command="{ type: 'func_generate' }" class="dropdown-item">
            <div class="dropdown-item-content">
              <el-icon class="dropdown-item-icon"><MagicStick /></el-icon>
              <span class="dropdown-item-text">参数构造器</span>
            </div>
          </el-dropdown-item>
          <el-dropdown-item :command="{ type: 'bind_enum' }" class="dropdown-item">
            <div class="dropdown-item-content">
              <el-icon class="dropdown-item-icon"><List /></el-icon>
              <span class="dropdown-item-text">常量值引用</span>
            </div>
          </el-dropdown-item>
          <el-dropdown-item :command="{ type: 'bind_env_params' }" class="dropdown-item">
            <div class="dropdown-item-content">
              <el-icon class="dropdown-item-icon"><Setting /></el-icon>
              <span class="dropdown-item-text">全局变量引用</span>
            </div>
          </el-dropdown-item>
          <el-dropdown-item :command="{ type: 'bind_step_params' }" v-if="!is_case_params" class="dropdown-item">
            <div class="dropdown-item-content">
              <el-icon class="dropdown-item-icon"><Connection /></el-icon>
              <span class="dropdown-item-text">步骤变量引用</span>
            </div>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>

  <!-- 环境变量引用弹窗 -->
  <el-dialog
    v-model="bindParamsVisible"
    title="全局变量引用"
    width="80%"
    :append-to-body="true"
    class="params-dialog"
    :close-on-click-modal="false"
  >
    <el-tabs v-model="bind_active_name"  class="drawer-sub-tabs">
      <el-tab-pane label="全局变量" name="case_global">
        <div class="table-container">
          <vxe-table
            :data="bind_global_params"
            height="500"
            show-overflow
            row-id="id"
            border
            :row-config="{ isHover: true }"
          >
            <vxe-column field="name" title="变量名称" min-width="250" align="center" />
            <vxe-column field="value" title="变量值" min-width="250" align="center" />
            <vxe-column field="remark" title="变量说明" min-width="200" align="center" />
            <vxe-column title="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
				<el-button type="success" class='dialog-confirm-btn' @click="bind_global(row.name)" :icon="Select">
					<span class="button-text">绑定</span>
				</el-button>
              </template>
            </vxe-column>
          </vxe-table>
        </div>
      </el-tab-pane>
      <el-tab-pane label="环境变量" name="env_bind">
        <div class="table-container">
          <vxe-table
            :data="bind_env_params"
            height="500"
            show-overflow
            row-id="id"
            border
            :row-config="{ isHover: true }"
          >
            <vxe-column field="name" title="变量名称" min-width="200" align="center" />
            <vxe-column field="value" title="变量值" min-width="250" align="center" />
            <vxe-column
              field="env_name"
              title="所属环境"
              min-width="200"
              align="center"
              :filters="envFilterOptions"
              :filter-multiple="false"
            />
            <vxe-column field="remark" title="变量说明" min-width="200" align="center" />
            <vxe-column title="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
				<el-button type="success" class='dialog-confirm-btn' @click="bind(row.name)" :icon="Select">
					<span class="button-text">绑定</span>
				</el-button>
              </template>
            </vxe-column>
          </vxe-table>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="用例变量" name="case_bind">
        <div class="table-container">
          <vxe-table
            :data="bind_case_params"
            height="500"
            show-overflow
            row-id="id"
            border
            :row-config="{ isHover: true }"
          >
            <vxe-column field="name" title="变量名称" min-width="250" align="center" />
            <vxe-column field="value" title="变量值" min-width="250" align="center" />
            <vxe-column field="remark" title="变量说明" min-width="200" align="center" />
            <vxe-column title="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
				<el-button type="success" class='dialog-confirm-btn' @click="bind_case(row.name)" :icon="Select">
					<span class="button-text">绑定</span>
				</el-button>
              </template>
            </vxe-column>
          </vxe-table>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="数据集" name="case_data">
        <div class="table-container">
          <vxe-table
            :data="_bind_case_data"
            height="500"
            show-overflow
            row-id="id"
            border
            :row-config="{ isHover: true }"
          >
            <vxe-column field="params_name" title="变量名称" min-width="300" align="center" />
            <vxe-column title="操作" width="150" align="center" fixed="right">
              <template #default="{ row }">
				  <el-button type="success" class='dialog-confirm-btn' @click="bind_case_data_func(row.params_name)" :icon="Select">
				  	<span class="button-text">绑定</span>
				  </el-button>
              </template>
            </vxe-column>
          </vxe-table>
        </div>
      </el-tab-pane>
    </el-tabs>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="bindParamsVisible = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 常量值引用弹窗 -->
  <el-dialog
    v-model="bindEnumVisible"
    title="常量值引用"
    width="80%"
    :append-to-body="true"
    class="enum-dialog"
    :close-on-click-modal="false"
  >
    <div class="enum-header">
      <el-select
        v-model="enum_name"
        placeholder="请选择常量类名"
        @change="enumChange"
        filterable
        size="large"
        style="width: 100%"
      >
        <el-option
          v-for="enum_obj in enum_list.results"
          :key="enum_obj.id"
          :label="`${enum_obj.name}${enum_obj.desc ? ' (' + enum_obj.desc + ')' : ''}`"
          :value="enum_obj.value"
        />
      </el-select>
    </div>
    
    <div class="table-container" v-if="enum_value_list && enum_value_list.length > 0">
      <vxe-table
        :data="enum_value_list"
        height="500"
        show-overflow
        row-id="id"
        border
        :row-config="{ isHover: true }"
      >
        <vxe-column field="name" title="变量名称" min-width="250" align="center" />
        <vxe-column field="value" title="变量值" min-width="250" align="center" />
        <vxe-column field="explain" title="变量说明" min-width="200" align="center" />
        <vxe-column title="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
			<el-button type="success" class='dialog-confirm-btn' @click="bind_enum(row.value)" :icon="Select">
				<span class="button-text">绑定</span>
			</el-button>
          </template>
        </vxe-column>
      </vxe-table>
    </div>
    
    <div v-else class="empty-state">
      <el-empty description="请选择常量类名查看详情" />
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="bindEnumVisible = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 步骤变量引用弹窗 -->
  <el-dialog
    v-model="StepParamsVisible"
    title="步骤变量引用"
    width="95%"
    :append-to-body="true"
    class="step-dialog"
    :close-on-click-modal="false"
    @closed="handleStepDialogClosed"
  >
    <div class="step-dialog-container">
      <!-- 左侧：步骤列表 -->
      <div class="step-sidebar">
        <div class="sidebar-section">
          <div class="section-title">步骤列表</div>
          <div class="step-list-container">
            <div class="step-list">
              <div
                v-for="(step, index) in sliceSteps"
                :key="index"
                :class="['step-item', { active: step_active_tab === index }]"
                @click="selectStepTab(index)"
              >
                <div class="step-index">{{ index + 1 }}</div>
                <div class="step-info">
                  <div class="step-type">{{ getStepTypeLabel(step) }}</div>
                  <el-tooltip :content="step.desc || '未命名步骤'" placement="right" effect="light">
                    <div class="step-desc">{{ step.desc || '未命名步骤' }}</div>
                  </el-tooltip>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 中间：变量类型选择 -->
      <div class="variable-type-sidebar">
        <div class="sidebar-section">
          <div class="section-title">变量类型</div>
          <div class="variable-type-container">
            <div class="variable-type-list">
              <!-- 步骤参数 - 所有步骤都显示 -->
              <div 
                :class="['variable-type-item', { active: selectedVariableType === 'stepParams' }]"
                @click="selectVariableType('stepParams')"
              >
                <el-icon><Collection /></el-icon>
                <span>步骤参数</span>
              </div>
              
              <!-- 运行次数 - 所有步骤都显示 -->
              <div 
                :class="['variable-type-item', { active: selectedVariableType === 'runTimes' }]"
                @click="selectVariableType('runTimes')"
              >
                <el-icon><Timer /></el-icon>
                <span>循环索引</span>
              </div>
			  <div
			    :class="['variable-type-item', { active: selectedVariableType === 'runElement' }]"
			    @click="selectVariableType('runElement')"
			  >
			    <el-icon><Timer /></el-icon>
			    <span>循环值</span>
			  </div>
              
              <!-- 函数参数 - 非接口请求步骤显示 -->
              <div 
                v-if="!isRequestType(currentStep)"
                :class="['variable-type-item', { active: selectedVariableType === 'funcParams' }]"
                @click="selectVariableType('funcParams')"
              >
                <el-icon><MagicStick /></el-icon>
                <span>函数参数</span>
              </div>
              
              <!-- 函数返回值 - 非接口请求步骤显示 -->
              <div 
                v-if="!isRequestType(currentStep)"
                :class="['variable-type-item', { active: selectedVariableType === 'funcReturn' }]"
                @click="selectVariableType('funcReturn')"
              >
                <el-icon><Refresh /></el-icon>
                <span>函数返回值</span>
              </div>
              
              <!-- 接口相关变量 - 只在接口请求步骤显示 -->
              <template v-if="isRequestType(currentStep)">
                <!-- URL相关变量 -->
                <div 
                  :class="['variable-type-item', { active: selectedVariableType === 'apiUri' }]"
                  @click="selectVariableType('apiUri')"
                >
                  <el-icon><Link /></el-icon>
                  <span>URI</span>
                </div>
                <div 
                  :class="['variable-type-item', { active: selectedVariableType === 'apiUrl' }]"
                  @click="selectVariableType('apiUrl')"
                >
                  <el-icon><Link /></el-icon>
                  <span>URL</span>
                </div>
                <div 
                  :class="['variable-type-item', { active: selectedVariableType === 'apiHost' }]"
                  @click="selectVariableType('apiHost')"
                >
                  <el-icon><House /></el-icon>
                  <span>请求域名</span>
                </div>
                <div 
                  :class="['variable-type-item', { active: selectedVariableType === 'apiMethod' }]"
                  @click="selectVariableType('apiMethod')"
                >
                  <el-icon><Operation /></el-icon>
                  <span>请求方法</span>
                </div>
                
                <!-- 请求相关变量 -->
                <div 
                  :class="['variable-type-item', { active: selectedVariableType === 'apiRequestHeaders' }]"
                  @click="selectVariableType('apiRequestHeaders')"
                >
                  <el-icon><Document /></el-icon>
                  <span>请求头</span>
                </div>
                <div 
                  :class="['variable-type-item', { active: selectedVariableType === 'apiRequestParams' }]"
                  @click="selectVariableType('apiRequestParams')"
                >
                  <el-icon><Search /></el-icon>
                  <span>查询参数</span>
                </div>
                <div 
                  :class="['variable-type-item', { active: selectedVariableType === 'apiRequestBody' }]"
                  @click="selectVariableType('apiRequestBody')"
                >
                  <el-icon><Document /></el-icon>
                  <span>请求体</span>
                </div>
                
                <!-- 响应相关变量 -->
                <div 
                  :class="['variable-type-item', { active: selectedVariableType === 'apiResponseBody' }]"
                  @click="selectVariableType('apiResponseBody')"
                >
                  <el-icon><Document /></el-icon>
                  <span>响应体</span>
                </div>
                <div 
                  :class="['variable-type-item', { active: selectedVariableType === 'apiStatusCode' }]"
                  @click="selectVariableType('apiStatusCode')"
                >
                  <el-icon><Check /></el-icon>
                  <span>状态码</span>
                </div>
                <div 
                  :class="['variable-type-item', { active: selectedVariableType === 'apiResponseHeaders' }]"
                  @click="selectVariableType('apiResponseHeaders')"
                >
                  <el-icon><Document /></el-icon>
                  <span>响应头</span>
                </div>
                <div 
                  :class="['variable-type-item', { active: selectedVariableType === 'apiResponseCookies' }]"
                  @click="selectVariableType('apiResponseCookies')"
                >
                  <el-icon><Document /></el-icon>
                  <span>Cookies</span>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧：具体变量内容 -->
      <div class="step-content">
        <div v-if="selectedVariableType" class="step-detail">
          <!-- 步骤标题 -->
          <div class="step-header">
            <div class="step-title">
              <span class="step-number">步骤 {{ parseInt(step_active_tab) + 1 }}</span>
              <span class="step-number">{{ currentStep.desc || '未命名步骤' }}</span>
			  <span class="step-number">{{ getStepTypeLabel(currentStep) }}</span>
			  <span class="step-number">{{ getVariableTypeLabel(selectedVariableType) }}</span>
            </div>
            <!-- <div class="step-subtitle">{{ getStepTypeLabel(currentStep) }}</div>
            <div class="variable-title">{{ getVariableTypeLabel(selectedVariableType) }}</div> -->
          </div>
          
          <!-- 变量内容 -->
          <div class="variable-content">
            <!-- 步骤参数 -->
            <div v-if="selectedVariableType === 'stepParams'" class="variable-section">
              <div v-if="currentStep.step_params && currentStep.step_params.length > 0" class="table-container">
                <vxe-table
                  :data="currentStep.step_params"
                  height="500"
                  show-overflow
                  row-id="id"
                  border
                  :row-config="{ isHover: true }"
                >
                  <vxe-column field="name" title="变量名称" min-width="250" align="center" />
                  <vxe-column field="value" title="变量值" min-width="250" align="center" />
                  <vxe-column field="explain" title="变量说明" min-width="200" align="center" />
                  <vxe-column title="操作" width="120" align="center" fixed="right">
                    <template #default="{ row }">
					  <el-button type="success" class='dialog-confirm-btn' @click="bind_step_params(row.name)" :icon="Select">
					  	<span class="button-text">绑定</span>
					  </el-button>
                    </template>
                  </vxe-column>
                </vxe-table>
              </div>
              <div v-else class="direct-bind-content">
                <div class="bind-info">
                  <div class="bind-title">直接绑定</div>
                  <div class="bind-desc">当前步骤的步骤参数为空，您可以直接绑定整个步骤参数对象</div>
                  <div class="bind-expression">
                    <div class="expression-label">绑定表达式：</div>
                    <div class="expression-value">case_params.stepResponse['{{ case_step_id }}']['stepParams']</div>
                  </div>
                  <div class="bind-action">
					<el-button type="success" class='dialog-confirm-btn' @click="handleDirectBind" :icon="Select" size='large'>
						<span class="button-text">确认绑定</span>
					</el-button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 函数参数 -->
            <div v-else-if="selectedVariableType === 'funcParams'" class="variable-section">
              <div v-if="one_step_obj.func_params && one_step_obj.func_params.length > 0" class="table-container">
                <vxe-table
                  ref="funcParamsTableRef"
                  height="500"
                  :row-config="{ keyField: 'id' }"
                  show-overflow
                  :tree-config="treeConfig"
                  :data="one_step_obj.func_params"
                >
                  <vxe-column field="name" title="参数名称" min-width="250" tree-node align="center" />
                  <vxe-column field="type" title="参数类型" width="120" />
                  <vxe-column field="value" title="参数值" min-width="250" align="center" />
                  <vxe-column field="explain" title="参数说明" min-width="200" align="center" />
                  <vxe-column title="操作" width="120" align="center" fixed="right">
                    <template #default="{ row }">
						<el-button type="success" class='dialog-confirm-btn' @click="bind_func_params(row)" :icon="Select">
							<span class="button-text">绑定</span>
						</el-button>
                    </template>
                  </vxe-column>
                </vxe-table>
              </div>
              <div v-else class="direct-bind-content">
                <div class="bind-info">
                  <div class="bind-title">直接绑定</div>
                  <div class="bind-desc">当前步骤的函数参数为空，您可以直接绑定整个函数参数对象</div>
                  <div class="bind-expression">
                    <div class="expression-label">绑定表达式：</div>
                    <div class="expression-value">case_params.stepResponse['{{ case_step_id }}']['funcParams']</div>
                  </div>
                  <div class="bind-action">
					<el-button type="success" class='dialog-confirm-btn' @click="handleDirectBind" :icon="Select" size='large'>
						<span class="button-text">确认绑定</span>
					</el-button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 运行次数 -->
            <div v-else-if="selectedVariableType === 'runTimes'" class="variable-section direct-bind-content">
              <div class="bind-info">
                <div class="bind-title">直接绑定</div>
                <div class="bind-desc">将绑定当前步骤的循环索引变量</div>
                <div class="bind-expression">
                  <div class="expression-label">绑定表达式：</div>
                  <div class="expression-value">case_params.stepResponse['{{ case_step_id }}']['runTimes']</div>
                </div>
                <div class="bind-action">
				  <el-button type="success" class='dialog-confirm-btn' @click="handleDirectBind" :icon="Select" size='large'>
				  	<span class="button-text">确认绑定</span>
				  </el-button>
                </div>
              </div>
            </div>
			
			<!-- 运行次数 -->
			<div v-else-if="selectedVariableType === 'runElement'" class="variable-section direct-bind-content">
			  <div class="bind-info">
			    <div class="bind-title">直接绑定</div>
			    <div class="bind-desc">将绑定当前步骤的循环值变量</div>
			    <div class="bind-expression">
			      <div class="expression-label">绑定表达式：</div>
			      <div class="expression-value">case_params.stepResponse['{{ case_step_id }}']['runElement']</div>
			    </div>
			    <div class="bind-action">
				  <el-button type="success" class='dialog-confirm-btn' @click="handleDirectBind" :icon="Select" size='large'>
				  	<span class="button-text">确认绑定</span>
				  </el-button>
			    </div>
			  </div>
			</div>
            
            <!-- 函数返回值 -->
            <div v-else-if="selectedVariableType === 'funcReturn'" class="variable-section direct-bind-content">
              <div class="bind-info">
                <div class="bind-title">直接绑定</div>
                <div class="bind-desc">将绑定当前步骤的函数返回值变量</div>
                <div class="bind-expression">
                  <div class="expression-label">绑定表达式：</div>
                  <div class="expression-value">case_params.stepResponse['{{ case_step_id }}']['funcReturn']</div>
                </div>
                <div class="bind-action">
					<el-button type="success" class='dialog-confirm-btn' @click="handleDirectBind" :icon="Select" size='large'>
						<span class="button-text">确认绑定</span>
					</el-button>
                  
                </div>
              </div>
            </div>
            
            <!-- 请求头 -->
            <div v-else-if="selectedVariableType === 'apiRequestHeaders'" class="variable-section">
              <div v-if="one_step_obj.api_headers && one_step_obj.api_headers.length > 0" class="table-container">
                <vxe-table
                  :data="one_step_obj.api_headers"
                  height="500"
                  show-overflow
                  row-id="id"
                  border
                  :row-config="{ isHover: true }"
                >
                  <vxe-column field="name" title="变量名称" min-width="250" align="center" />
                  <vxe-column field="value" title="变量值" min-width="250" align="center" />
                  <vxe-column field="explain" title="变量说明" min-width="200" align="center" />
                  <vxe-column title="操作" width="120" align="center" fixed="right">
                    <template #default="{ row }">
					  <el-button type="success" class='dialog-confirm-btn' @click="bind_step_headers(row.name)" :icon="Select">
					  		<span class="button-text">绑定</span>
					  </el-button>
                    </template>
                  </vxe-column>
                </vxe-table>
              </div>
              <div v-else class="direct-bind-content">
                <div class="bind-info">
                  <div class="bind-title">直接绑定</div>
                  <div class="bind-desc">当前步骤的请求头为空，您可以直接绑定整个请求头对象</div>
                  <div class="bind-expression">
                    <div class="expression-label">绑定表达式：</div>
                    <div class="expression-value">case_params.stepResponse['{{ case_step_id }}']['apiRequestHeaders']</div>
                  </div>
                  <div class="bind-action">
					  <el-button type="success" class='dialog-confirm-btn' @click="handleDirectBind" :icon="Select" size='large'>
					  	<span class="button-text">确认绑定</span>
					  </el-button>
                    
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 查询参数 -->
            <div v-else-if="selectedVariableType === 'apiRequestParams'" class="variable-section">
              <div v-if="one_step_obj.api_params && one_step_obj.api_params.length > 0" class="table-container">
                <vxe-table
                  :data="one_step_obj.api_params"
                  height="500"
                  show-overflow
                  row-id="id"
                  border
                  :row-config="{ isHover: true }"
                >
                  <vxe-column field="name" title="变量名称" min-width="250" align="center" />
                  <vxe-column field="value" title="变量值" min-width="250" align="center" />
                  <vxe-column field="explain" title="变量说明" min-width="200" align="center" />
                  <vxe-column title="操作" width="120" align="center" fixed="right">
                    <template #default="{ row }">
                      <el-button type="success" class='dialog-confirm-btn' @click="bind_api_params(row.name)" :icon="Select">
						  <span class="button-text">绑定</span>
					  </el-button>
                    </template>
                  </vxe-column>
                </vxe-table>
              </div>
              <div v-else class="direct-bind-content">
                <div class="bind-info">
                  <div class="bind-title">直接绑定</div>
                  <div class="bind-desc">当前步骤的查询参数为空，您可以直接绑定整个查询参数对象</div>
                  <div class="bind-expression">
                    <div class="expression-label">绑定表达式：</div>
                    <div class="expression-value">case_params.stepResponse['{{ case_step_id }}']['apiRequestParams']</div>
                  </div>
                  <div class="bind-action">
					<el-button type="success" class='dialog-confirm-btn' @click="handleDirectBind" :icon="Select" size='large'>
						<span class="button-text">确认绑定</span>
					</el-button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 请求体 -->
            <div v-else-if="selectedVariableType === 'apiRequestBody'" class="variable-section">
              <div v-if="one_step_obj.api_json && one_step_obj.api_json.length > 0" class="table-container">
                <vxe-table
                  ref="bodyTableRef"
                  height="500"
                  :row-config="{ keyField: 'id' }"
                  show-overflow
                  :tree-config="treeConfig"
                  :data="one_step_obj.api_json"
                >
                  <vxe-column field="name" title="参数名称" min-width="250" tree-node align="center" />
                  <vxe-column field="type" title="参数类型" width="120" />
                  <vxe-column field="value" title="参数值" min-width="250" align="center" />
                  <vxe-column field="explain" title="参数说明" min-width="200" align="center" />
                  <vxe-column title="操作" width="120" align="center" fixed="right">
                    <template #default="{ row }">
                      <el-button type="success" class="dialog-confirm-btn"  @click="bind_body_params(row)" :icon="Select">
						  <span class="button-text">绑定</span>
					  </el-button>
                    </template>
                  </vxe-column>
                </vxe-table>
              </div>
              <div v-else class="direct-bind-content">
                <div class="bind-info">
                  <div class="bind-title">直接绑定</div>
                  <div class="bind-desc">当前步骤的请求体为空，您可以直接绑定整个请求体对象</div>
                  <div class="bind-expression">
                    <div class="expression-label">绑定表达式：</div>
                    <div class="expression-value">case_params.stepResponse['{{ case_step_id }}']['apiRequestBody']</div>
                  </div>
                  <div class="bind-action">
                    <el-button type="success" class='dialog-confirm-btn' @click="handleDirectBind" :icon="Select" size='large'>
                    	<span class="button-text">确认绑定</span>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 响应体 -->
            <div v-else-if="selectedVariableType === 'apiResponseBody'" class="variable-section">
              <div v-if="one_step_obj.api_response && one_step_obj.api_response.length > 0" class="table-container">
                <vxe-table
                  ref="responseTableRef"
				  max-height='500'
                  :row-config="{ keyField: 'id' }"
                  show-overflow
                  :tree-config="treeConfig"
                  :data="one_step_obj.api_response"
                >
                  <vxe-column field="name" title="参数名称" min-width="250" tree-node align="center" />
                  <vxe-column field="type" title="参数类型" width="120" />
                  <vxe-column field="value" title="参数值" min-width="250" align="center" />
                  <vxe-column field="explain" title="参数说明" min-width="200" align="center" />
                  <vxe-column title="操作" width="120" align="center" fixed="right">
                    <template #default="{ row }">
                      <el-button type="success" class="dialog-confirm-btn" @click="bind_response_body(row)" :icon="Select">
						  <span class="button-text">绑定</span>
					  </el-button>
                    </template>
                  </vxe-column>
                </vxe-table>
              </div>
              <div v-else class="direct-bind-content">
                <div class="bind-info">
                  <div class="bind-title">直接绑定</div>
                  <div class="bind-desc">当前步骤的响应体为空，您可以直接绑定整个响应体对象</div>
                  <div class="bind-expression">
                    <div class="expression-label">绑定表达式：</div>
                    <div class="expression-value">case_params.stepResponse['{{ case_step_id }}']['apiResponseBody']</div>
                  </div>
                  <div class="bind-action">
                    <el-button type="success" class='dialog-confirm-btn' @click="handleDirectBind" :icon="Select" size='large'>
                    	<span class="button-text">确认绑定</span>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 其他直接绑定类型（无列表） -->
            <div v-else class="direct-bind-content">
              <div class="bind-info">
                <div class="bind-title">直接绑定</div>
                <div class="bind-desc">将绑定当前步骤的 {{ getVariableTypeLabel(selectedVariableType) }} 变量</div>
                <div class="bind-expression">
                  <div class="expression-label">绑定表达式：</div>
                  <div class="expression-value">case_params.stepResponse['{{ case_step_id }}']['{{ selectedVariableType }}']</div>
                </div>
                <div class="bind-action">
                  <el-button type="success" class='dialog-confirm-btn' @click="handleDirectBind" :icon="Select" size='large'>
                  	<span class="button-text">确认绑定</span>
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-step-content">
          <el-empty description="请从左侧选择步骤和变量类型" />
        </div>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="StepParamsVisible = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 参数构造器弹窗 -->
  <el-dialog
    v-model="funcVisible"
    title="参数构造器"
    width="90%"
    :append-to-body="true"
    class="func-dialog"
    :close-on-click-modal="false"
  >
    <div class="func-dialog-content">
      <div class="func-header">
        <el-row :gutter="20" align="middle">
          <el-col :span="18">
            <el-cascader
              ref="cascaderRef"
              :teleported="false"
              @change="actionChange"
              v-model="func_values"
              :options="func_list"
              :props="editProps"
              filterable
              placeholder="请选择函数生成数据"
              style="width: 100%"
              size="large"
            />
          </el-col>
          <el-col :span="6" class="func-actions">
            <el-button-group>
              <el-button type="primary" @click="singleRunFunction"  class="dialog-confirm-btn">
				  <span class="button-text">运行函数</span>
			  </el-button>

            </el-button-group>
          </el-col>
        </el-row>
      </div>

      <div class="func-content">
        <el-collapse v-model="activeNames" accordion class="func-collapse">
          <el-collapse-item title="函数体" name="1">
            <div class="code-editor-container">
              <v-ace-editor
                v-model:value="func_script"
                lang="python"
                theme="chrome"
                style="height: 200px"
                :options="editOption"
                readonly
              />
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="函数参数" name="2">
            <div class="table-container">
              <vxe-table
                ref="funcParamsTableRef"
                :data="func_params"
                height="300"
                empty-text="该函数无入参"
                row-id="id"
                border
                :row-config="{ isHover: true, keyField: 'id' }"
                :tree-config="treeConfig"
              >
                <vxe-column field="name" title="参数名称" min-width="250" tree-node align="left">
                  <template #default="{ row }">
                    <div class="tree-cell" :style="{ paddingLeft: (row._level - 1) * 20 + 'px' }">
                      {{ row.name }}
                    </div>
                  </template>
                </vxe-column>
                <vxe-column field="type" title="参数类型" min-width="120" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getTypeTagType(row.type)">{{ row.type }}</el-tag>
                  </template>
                </vxe-column>
                <vxe-column field="explain" title="参数说明" min-width="250" align="center" />
                <vxe-column field="value" title="参数值" min-width="300" align="left">
                  <template #default="{ row }">
                    <template v-if="depth < maxDepth">
                      <ScriptAndParams
                        :depth="depth + 1"
                        :value="row.value"
                        :row="row"
                        :bind_case_data="bind_case_data"
                        :step_index="step_index"
                        :steps="steps"
                        :bind_env_params="bind_env_params"
                        :case_table_data="case_table_data"
                        :func_list="func_list"
                        :is_case_params="is_case_params"
                        @update:value="handleUpdateValue(row, $event)"
                      />
                    </template>
                    <template v-else>
                      <el-input
                        v-model="row.value"
                        @change="handleUpdateValue(row, row.value)"
                        size="small"
                        placeholder="请输入参数值"
                      />
                    </template>
                  </template>
                </vxe-column>
              </vxe-table>
            </div>
          </el-collapse-item>
          
          <el-collapse-item v-if="func_values[0] === StepType.UserCustomizeFunction" title="导入模块" name="3">
            <div class="code-editor-container">
              <v-ace-editor
                v-model:value="func_package"
                lang="python"
                theme="chrome"
                style="height: 150px"
                :options="editOption"
              />
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="运行结果" name="4">
            <div class="result-container">
              <v-ace-editor
                v-model:value="func_run_result"
                lang="python"
                theme="chrome"
                style="height: 100px"
                :options="editOption"
              />
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="funcVisible = false">取消</el-button>
        <el-button type="primary" @click="insertDynamicResult" :disabled="func_values.length === 0">引用该函数</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { VAceEditor } from 'vue3-ace-editor';
import 'ace-builds/src-noconflict/snippets/json';
import 'ace-builds/src-noconflict/mode-json';
import 'ace-builds/src-noconflict/snippets/python';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/theme-chrome';
import 'ace-builds/src-noconflict/theme-monokai';
import 'ace-builds/src-noconflict/ext-language_tools';
import ace from 'ace-builds';
import { ElMessage } from 'element-plus';
import {
  Menu,
  MagicStick,
  List,
  Setting,
  Connection,
  Select,
  VideoPlay,
  View,
  InfoFilled,
  Collection,
  Timer,
  Refresh,
  Link,
  House,
  Operation,
  Document,
  Search,
  Check,
  Cookie
} from '@element-plus/icons-vue';
import { mapState } from 'vuex';
import BodyEdit from './BodyEdit.vue';
import ScriptAndParams from './ScriptAndParams.vue';

export default {
  name: 'ScriptAndParams',
  computed: {
    ...mapState(['projectInfo']),
    editOption() {
      return {
        enablesBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true,
        tabSize: 4,
        fontSize: 14,
        useworker: true,
        ShowPrintMargin: false,
        enableMultiselect: true,
        showFoldwidgets: true,
        fadeFoldwidgets: true,
        wrap: true,
      };
    },
    sliceSteps() {
      return [...this.steps.slice(0, this.step_index + 1)];
    },
    envFilterOptions() {
      const seen = new Set();
      const uniqueItems = this.bind_env_params.filter(item => {
        if (seen.has(item.env_name)) {
          return false;
        }
        seen.add(item.env_name);
        return true;
      });

      return uniqueItems.map(item => ({
        label: item.env_name,
        value: item.env_name,
      }));
    },
    currentStep() {
      const index = parseInt(this.step_active_tab);
      return this.sliceSteps[index] || {};
    }
  },
  components: {
    BodyEdit,
    VAceEditor,
    ScriptAndParams,
  },
  emits: ['update:value'],
  props: {
    row: {
      type: Object,
    },
    value: {
      type: String,
    },
    func_list: {
      type: Array
    },
    bind_env_params: {
      type: Array
    },
    bind_global_params: {
      type: Array
    },
    case_table_data: {
      type: Array
    },
    bind_case_data: {
      type: Array
    },
    index: {
      type: Number
    },
    step_index: {
      type: Number
    },
    is_case_params: {
      type: Boolean,
      default: false
    },
    steps: {
      type: Array,
      default: [],
    },
    depth: {
      type: Number,
      default: 0
    },
    zIndex: {
      type: Number,
      default: 2000
    }
  },
  setup() {
    return {
      Menu,
      MagicStick,
      List,
      Setting,
      Connection,
      Select,
      VideoPlay,
      View,
      InfoFilled,
      Collection,
      Timer,
      Refresh,
      Link,
      House,
      Operation,
      Document,
      Search,
      Check,
      Cookie
    };
  },
  data() {
    return {
      viewFuncVisiable: false,
      maxDepth: 3,
      _bind_case_data: [],
      step_active_tab: 0,
      step_id: '',
      case_step_id: '',
      selectedVariableType: null,
      one_step_obj: {},
      localValue: this.value,
      activeNames: ['1'],
      bind_active_name: 'case_global',
      bind_case_params: [],
      StepParamsVisible: false,
      bindEnumVisible: false,
      enum_name: [],
      enum_value_list: [],
      StepType: {
        PlatformSystemFunction: -1,
        UserCustomizeFunction: 1,
        Request: 5,
        SQL: 8,
        Selenium: 2,
        Appium: 7,
        ComStep: 3,
        UserCustomizeScript: 4,
        Control: 9,
      },
      editProps: {
        emitPath: true,
        value: 'id',
        label: 'name',
      },
      treeConfig: {
        transform: true,
        accordion: true,
        rowField: 'id',
        parentField: 'parentId',
        iconOpen: 'vxe-icon-square-minus',
        iconClose: 'vxe-icon-square-plus',
      },
      show_close: false,
      append_to_body: true,
      funcVisible: false,
      bindParamsVisible: false,
      func_values: [],
      func_script: "",
      func_desc: "",
      func_package: '',
      func_params: [],
      enum_list: [],
      func_name: '',
      func_run_result: '',
      type_list: ['Str', 'Int', 'Float', "Dict", "List", 'Bool'],
      // 变量类型标签映射
      variableTypeLabels: {
        stepParams: '步骤参数',
        funcParams: '函数参数',
        runTimes: '循环索引',
		runElement: '循环值',
        apiUri: 'URI',
        apiUrl: 'URL',
        apiHost: 'Host',
        apiMethod: 'Method',
        apiRequestHeaders: '请求头',
        apiRequestParams: '查询参数',
        apiRequestBody: '请求体',
        apiResponseBody: '响应体',
        apiStatusCode: '状态码',
        apiResponseHeaders: '响应头',
        apiResponseCookies: 'Cookies',
        funcReturn: '函数返回值'
      }
    };
  },
  watch: {
    value(value) {
      this.localValue = value;
    },
    StepParamsVisible(val) {
      if (val && this.sliceSteps.length > 0) {
        this.step_active_tab = 0;
        this.step_id = this.sliceSteps[0].id;
        this.case_step_id = this.sliceSteps[0].case_step_id;
        this.getStep(this.step_id, this.case_step_id);
        this.selectedVariableType = null;
      }
    },
    step_active_tab(val) {
      if (val !== null && this.sliceSteps[val]) {
        this.step_id = this.sliceSteps[val].id;
        this.case_step_id = this.sliceSteps[val].case_step_id;
        this.getStep(this.step_id, this.case_step_id);
        this.selectedVariableType = null;
      }
    }
  },
  methods: {
    viewFuncBody() {
      this.viewFuncVisiable = true;
    },
    handleUpdateValue(row, newValue) {
      row.value = newValue;
    },
    handleUpdateName(row, newValue) {
      row.name = newValue;
    },
    handleFocus() {
      this.localValue = this.value;
    },
    enumChange(value) {
      this.enum_value_list = value;
    },
    handleBlur() {
      this.$emit('update:value', this.localValue);
    },
    handleCommand(command) {
      if (command.type === 'func_generate') {
        this.funcVisible = true;
      } else if (command.type === 'bind_env_params') {
        this.bindParamsVisible = true;
      } else if (command.type === 'bind_enum') {
        this.bindEnumVisible = true;
      } else {
        this.StepParamsVisible = true;
        this.step_active_tab = 0;
        if (this.sliceSteps.length > 0) {
          this.step_id = this.sliceSteps[0].id;
          this.case_step_id = this.sliceSteps[0].case_step_id;
          this.getStep(this.step_id, this.case_step_id);
        }
        this.selectedVariableType = null;
      }
    },
    // 检查是否为接口请求类型
    isRequestType(step) {
      if (!step) return false;
      // 判断是否为接口请求步骤：type=5 或 com_step_type=5
      return step.type === this.StepType.Request || step.com_step_type === this.StepType.Request;
    },
    // 获取步骤类型标签
    getStepTypeLabel(step) {
      const types = {
        [this.StepType.Request]: 'HTTP接口请求',
        [this.StepType.Selenium]: 'Selenium',
        [this.StepType.Appium]: 'Appium',
        [this.StepType.SQL]: '数据库操作',
        [this.StepType.ComStep]: '公共步骤',
        [this.StepType.Control]: '逻辑控制器',
        [this.StepType.UserCustomizeScript]: '自定义脚本',
        [this.StepType.UserCustomizeFunction]: '自定义函数',
        [this.StepType.PlatformSystemFunction]: '系统函数',
      };
      return types[step.type] || types[step.com_step_type] || '未知';
    },
    // 获取变量类型标签
    getVariableTypeLabel(type) {
      return this.variableTypeLabels[type] || type;
    },
    // 选择步骤标签
    selectStepTab(index) {
      this.step_active_tab = index;
      this.step_id = this.sliceSteps[index].id;
      this.case_step_id = this.sliceSteps[index].case_step_id;
      this.getStep(this.step_id, this.case_step_id);
      this.selectedVariableType = null;
    },
    // 选择变量类型
    selectVariableType(type) {
      this.selectedVariableType = type;
    },
    // 获取类型标签样式
    getTypeTagType(type) {
      const map = {
        Str: 'success',
        Int: 'primary',
        Float: 'info',
        Dict: 'warning',
        List: 'danger',
        Bool: 'success',
      };
      return map[type] || 'info';
    },
    bind(name) {
      const value = "case_params." + `envParams['${name}']`;
      this.localValue = value;
      this.$emit('update:value', value);
      this.bindParamsVisible = false;
      ElMessage.success('环境变量绑定成功！');
    },
    bind_enum(value) {
      this.localValue = value;
      this.$emit('update:value', value);
      this.bindEnumVisible = false;
      ElMessage.success('常量值绑定成功！');
    },
    bind_case(name) {
      const value = "case_params." + `caseParams['${name}']`;
      this.localValue = value;
      this.$emit('update:value', value);
      this.bindParamsVisible = false;
      ElMessage.success('用例变量绑定成功！');
    },
    bind_global(name) {
      const value = "case_params." + `globalParams['${name}']`;
      this.localValue = value;
      this.$emit('update:value', value);
      this.bindParamsVisible = false;
      ElMessage.success('全局变量绑定成功！');
    },
    bind_case_data_func(name) {
      const value = "case_params." + `caseData['${name}']`;
      this.localValue = value;
      this.$emit('update:value', value);
      this.bindParamsVisible = false;
      ElMessage.success('数据集变量绑定成功！');
    },
    bind_step_params(name) {
      const value = "case_params." + `stepResponse['${this.case_step_id}']['stepParams']['${name}']`;
      this.localValue = value;
      this.$emit('update:value', value);
      this.StepParamsVisible = false;
      ElMessage.success('步骤参数绑定成功！');
    },
    bind_api_params(name) {
      const value = "case_params." + `stepResponse['${this.case_step_id}']['apiRequestParams']['${name}']`;
      this.localValue = value;
      this.$emit('update:value', value);
      this.StepParamsVisible = false;
      ElMessage.success('查询参数绑定成功！');
    },
    bind_step_headers(name) {
      const value = "case_params." + `stepResponse['${this.case_step_id}']['apiRequestHeaders']['${name}']`;
      this.localValue = value;
      this.$emit('update:value', value);
      this.StepParamsVisible = false;
      ElMessage.success('请求头绑定成功！');
    },
    bind_body_params(row) {
      if (row.parentId === null) {
        const value = "case_params." + `stepResponse['${this.case_step_id}']['apiRequestBody']['${row.name}']`;
        this.localValue = value;
        this.$emit('update:value', value);
        this.StepParamsVisible = false;
        ElMessage.success('请求体参数绑定成功！');
      } else {
        let json_path;
        json_path = this.loop_find_name_by_parent_id(row.parentId, this.one_step_obj.api_json, `['${row.name}']`);
        const value = "case_params." + `stepResponse['${this.case_step_id}']['apiRequestBody']${json_path}`;
        this.localValue = value;
        this.$emit('update:value', value);
        this.StepParamsVisible = false;
        ElMessage.success('请求体参数绑定成功！');
      }
    },
    bind_func_params(row) {
      if (row.parentId === undefined) {
        const value = "case_params." + `stepResponse['${this.case_step_id}']['funcParams']['${row.name}']`;
        this.localValue = value;
        this.$emit('update:value', value);
        this.StepParamsVisible = false;
        ElMessage.success('函数参数绑定成功！');
      } else {
        let json_path;
        json_path = this.loop_find_name_by_parent_id(row.parentId, this.one_step_obj.func_params, `['${row.name}']`);
        const value = "case_params." + `stepResponse['${this.case_step_id}']['funcParams']${json_path}`;
        this.localValue = value;
        this.$emit('update:value', value);
        this.StepParamsVisible = false;
        ElMessage.success('函数参数绑定成功！');
      }
    },
    bind_response_body(row) {
      if (row.parentId === null) {
        const value = "case_params." + `stepResponse['${this.case_step_id}']['apiResponseBody']['${row.name}']`;
        this.localValue = value;
        this.$emit('update:value', value);
        this.StepParamsVisible = false;
        ElMessage.success('响应体参数绑定成功！');
      } else {
        let json_path;
        json_path = this.loop_find_name_by_parent_id(row.parentId, this.one_step_obj.api_response, `['${row.name}']`);
        const value = "case_params." + `stepResponse['${this.case_step_id}']['apiResponseBody']${json_path}`;
        this.localValue = value;
        this.$emit('update:value', value);
        this.StepParamsVisible = false;
        ElMessage.success('响应体参数绑定成功！');
      }
    },
    loop_find_name_by_parent_id(parentId, data, json_path) {
      for (const item of data) {
        if (item.id === parentId) {
          if (item.type === 'array') {
            const value = json_path.split('][');
            if (value.length > 1) {
              json_path = `['${item.name}']` + '[' + json_path.split('][')[0].slice(2, -1) + ']' + '[' + json_path.split('][').slice(1).join('][');
            } else {
              json_path = `['${item.name}']` + '[' + json_path.slice(2, -2) + ']';
            }
          } else {
            json_path = `['${item.name}']` + json_path;
          }
          if (item.parentId !== null) {
            return this.loop_find_name_by_parent_id(item.parentId, data, json_path);
          } else {
            return json_path;
          }
        }
      }
    },
    handleStepDialogClosed() {
      this.step_active_tab = 0;
      this.selectedVariableType = null;
    },
    // 直接绑定处理
    handleDirectBind() {
      const templates = {
        apiStatusCode: "case_params.stepResponse['${case_step_id}']['apiStatusCode']",
        apiRequestBody: "case_params.stepResponse['${case_step_id}']['apiRequestBody']",
        apiResponseBody: "case_params.stepResponse['${case_step_id}']['apiResponseBody']",
        apiRequestParams: "case_params.stepResponse['${case_step_id}']['apiRequestParams']",
        apiRequestHeaders: "case_params.stepResponse['${case_step_id}']['apiRequestHeaders']",
        runTimes: "case_params.stepResponse['${case_step_id}']['runTimes']",
		runElement: "case_params.stepResponse['${case_step_id}']['runElement']",
        apiUrl: "case_params.stepResponse['${case_step_id}']['apiUrl']",
        apiHost: "case_params.stepResponse['${case_step_id}']['apiHost']",
        apiUri: "case_params.stepResponse['${case_step_id}']['apiUri']",
        apiResponseHeaders: "case_params.stepResponse['${case_step_id}']['apiResponseHeaders']",
        apiResponseCookies: "case_params.stepResponse['${case_step_id}']['apiResponseCookies']",
        apiMethod: "case_params.stepResponse['${case_step_id}']['apiMethod']",
        funcReturn: "case_params.stepResponse['${case_step_id}']['funcReturn']",
        funcParams: "case_params.stepResponse['${case_step_id}']['funcParams']",
        stepParams: "case_params.stepResponse['${case_step_id}']['stepParams']",
      };

      if (templates[this.selectedVariableType]) {
        const value = templates[this.selectedVariableType].replace('${case_step_id}', this.case_step_id);
        this.localValue = value;
        this.$emit('update:value', value);
        this.StepParamsVisible = false;
        ElMessage.success('绑定成功！');
      }
    },
    insertStaticResult() {
      if (!this.func_run_result) {
        ElMessage.error('请先执行函数获取执行结果');
        return;
      }
      this.localValue = this.func_run_result;
      this.$emit('update:value', this.func_run_result);
      this.funcVisible = false;
      ElMessage.success('静态结果插入成功！');
    },
    insertDynamicResult() {
      if (this.func_values.length === 0) {
        ElMessage.error('请先选择函数');
        return;
      }

      for (const param of this.func_params) {
        if (param.value === null) {
          ElMessage.error('请先填写函数入参值');
          return;
        }
      }

      let paramsKeyParts = [];
      for (let param of this.func_params) {
        let formattedParam;
        switch (param.type) {
          case "Str":
            formattedParam = `'${param.value}'`;
            break;
          case "Int":
            formattedParam = `${param.value}`;
            break;
          case "Float":
            formattedParam = `${param.value}`;
            break;
          case "Tuple":
            formattedParam = `${param.value}`;
            break;
          case "Dict":
            formattedParam = `${param.value}`;
            break;
          case "List":
            formattedParam = `${param.value}`;
            break;
          default:
            formattedParam = `${param.value}`;
            break;
        }
        paramsKeyParts.push(formattedParam);
      }
      const params_key = paramsKeyParts.join(',');
      let function_name;
      if (this.func_values[0] === this.StepType.PlatformSystemFunction) {
        function_name = 'sys_function.' + this.func_values[this.func_values.length - 1];
      } else {
        function_name = 'user_function.' + this.func_name;
      }

      if (params_key === '') {
        this.localValue = `${function_name}()`;
        this.$emit('update:value', `${function_name}()`);
      } else {
        this.localValue = `${function_name}(${params_key})`;
        this.$emit('update:value', `${function_name}(${params_key})`);
      }
      this.funcVisible = false;
      ElMessage.success('函数引用插入成功！');
    },
    actionChange() {
      this.func_run_result = '';
      const step_type = this.func_values[0];
      const keyword = this.func_values[this.func_values.length - 1];
      const node = this.$refs.cascaderRef?.getCheckedNodes()[0];
      if (!node) return;

      if (step_type === this.StepType.PlatformSystemFunction) {
		console.log(node, 'data')
        this.func_script = node.data.script || '';
		console.log(this.func_script, 'data1')
        this.func_desc = Array.isArray(node.data.desc) ? node.data.desc.join('\n') : node.data.desc || '';
        this.func_params = node.data.params || [];
      } else {
        this.getPython(keyword);
      }
    },
    async getStep(id, case_step_id) {
      try {
        const response = await this.$api.getStep(`${this.$route.query.id}_${id}_${case_step_id}`);
        if (response.status === 200) {
          this.one_step_obj = { ...response.data.result };
          // 确保所有参数数据都存在
          if (this.one_step_obj.api_data && this.one_step_obj.api_data.length > 0) {
            this.one_step_obj.api_json = [...this.one_step_obj.api_data];
          }
          // 确保其他参数数据都存在
          if (!this.one_step_obj.api_headers) {
            this.one_step_obj.api_headers = [];
          }
          if (!this.one_step_obj.api_params) {
            this.one_step_obj.api_params = [];
          }
          if (!this.one_step_obj.api_response) {
            this.one_step_obj.api_response = [];
          }
          if (!this.one_step_obj.func_params) {
            this.one_step_obj.func_params = [];
          }
          // 确保 URL 相关数据存在
          if (!this.one_step_obj.api_uri) {
            this.one_step_obj.api_uri = '';
          }
          if (!this.one_step_obj.api_url) {
            this.one_step_obj.api_url = '';
          }
          if (!this.one_step_obj.api_host) {
            this.one_step_obj.api_host = '';
          }
          if (!this.one_step_obj.api_method) {
            this.one_step_obj.api_method = '';
          }
          if (!this.one_step_obj.api_status_code) {
            this.one_step_obj.api_status_code = '';
          }
          if (!this.one_step_obj.run_times) {
            this.one_step_obj.run_times = 0;
          }
          if (!this.one_step_obj.func_return) {
            this.one_step_obj.func_return = '';
          }
        }
      } catch (error) {
        console.error('获取步骤信息失败:', error);
      }
    },
    async getPython(id) {
      try {
        const response = await this.$api.getPython(id);
        if (response.status === 200) {
          const result = response.data.result;
          this.func_script = result.script || '';
          this.func_desc = result.desc || '';
          this.func_package = result.package || '';
          this.func_name = result.name || '';
          this.func_params = result.params || [];
        }
      } catch (error) {
        console.error('获取Python函数失败:', error);
      }
    },
    async getEnums() {
      try {
        const response = await this.$api.getEnums({ project: this.projectInfo.id });
        if (response.status === 200) {
          this.enum_list = { ...response.data };
        }
      } catch (error) {
        console.error('获取常量列表失败:', error);
      }
    },
    async singleRunFunction() {
      if (this.func_values.length === 0) {
        ElMessage.error('请先选择函数');
        return;
      }

      const func_type = this.func_values[0];
      const keyword = this.func_values[this.func_values.length - 1];

      if (func_type === this.StepType.PlatformSystemFunction) {
        const response = await this.$api.singleRunFunction({ name: keyword, params: this.func_params });
        if (response.status === 200) {
          this.func_run_result = response.data.result.result.toString();
          this.activeNames = ['4'];
          ElMessage.success('函数执行成功！');
        } else if (response.status === 400) {
          this.func_run_result = '函数执行报错, 请检查入参';
          ElMessage.error('函数执行报错，请检查入参');
        }
      } else {
        for (const param of this.func_params) {
          if (param.value === null) {
            ElMessage.error('请先填写函数入参值');
            return;
          }
        }
        const python_func_data = { name: this.func_name, script: this.func_script, package: this.func_package, params: this.func_params };
        const response = await this.$api.singleRunUserFunction({ python_func_obj: python_func_data });
        if (response.status === 200) {
          this.func_run_result = response.data.result.result.toString();
          this.activeNames = ['4'];
          ElMessage.success('函数执行成功！');
        } else if (response.status === 400) {
          this.func_run_result = '函数执行报错, 请检查入参';
          ElMessage.error('函数执行报错，请检查入参');
        }
      }
    },
    deal_params_name() {
      if (this.bind_case_data && this.bind_case_data.length !== 0) {
        this._bind_case_data = this.bind_case_data.map((value, index) => ({
          id: index,
          params_name: value
        }));
      }
    }
  },
  created() {
    this.getEnums();
    this.deal_params_name();
    // 判断是否是用例参数，如果不是用例参数，就可以引用上一个步骤的所有用例参数
    if (this.is_case_params) {
      this.bind_case_params = [...(this.case_table_data || []).slice(0, this.index)];
    } else {
      this.bind_case_params = [...(this.case_table_data || [])];
    }
  }
};
</script>

<style scoped>
.func-input-container {
  position: relative;
  width: 100%;
  margin-bottom: 10px;
}

.func-input-container .input {
  width: 100%;
}

.func-input-container :deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
  padding-right: 50px !important;
}

.func-input-container :deep(.el-input__wrapper:hover) {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 1px var(--el-color-primary-light-7);
}

.func-input-container :deep(.el-input__wrapper.is-focus) {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px var(--el-color-primary-light-8);
}

.dropdown-wrapper {
  position: absolute;
  right: 10px !important;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

/* 按钮文字容器 */
.button-text {
  position: relative;
  display: inline-block;
  padding-bottom: 3px; /* 为下划线留出空间 */
}

/* 下划线效果 */
.button-text::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: currentColor;
  transform: scaleX(0);
  transform-origin: bottom right;
  transition: transform 0.3s ease;
}

.dialog-confirm-btn {
  position: relative;
  padding: 10px 24px !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: 15px !important;
  transition: all 0.3s ease !important;
  overflow: hidden;
}

.dialog-confirm-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
  border: none !important;
  color: white !important;
}

.dialog-confirm-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4) !important;
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
}

/* 确认按钮下划线颜色 */
.button-text::after {
  background: var(--qm-bg-2); /* 白色下划线 */
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: linear-gradient(135deg, #f59e0b, #79bbff);
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;
}

.dropdown-trigger:hover {
  background: linear-gradient(135deg, #79bbff, #f59e0b);
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.dropdown-icon {
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-dropdown-menu {
  border-radius: 8px;
  padding: 8px 0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--qm-line);
  min-width: 160px;
}

.custom-dropdown-menu :deep(.el-dropdown-menu__item) {
  padding: 10px 16px;
  transition: all 0.2s ease;
}

.custom-dropdown-menu :deep(.el-dropdown-menu__item:hover) {
  background-color: #f0f7ff;
  color: #f59e0b;
}

.dropdown-item-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dropdown-item-icon {
  font-size: 16px;
  color: #f59e0b;
  width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dropdown-item-text {
  font-size: 14px;
  font-weight: 500;
}

.quick-action-container {
  margin-top: 0px;
  margin-left: 10px;
}

.quick-dropdown {
  width: 100%;
}

.quick-action-btn {
  width: 100%;
  justify-content: center;
  /* border-radius: 8px; */
  font-weight: 500;
  /* padding: 12px 0; */
  background: linear-gradient(135deg, #67c23a, #85ce61);
  border: none;
  transition: all 0.3s ease;
}

.quick-action-btn:hover {
  background: linear-gradient(135deg, #85ce61, #67c23a);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

/* 对话框样式 */
:deep(.params-dialog .el-dialog__body),
:deep(.enum-dialog .el-dialog__body),
:deep(.step-dialog .el-dialog__body),
:deep(.func-dialog .el-dialog__body) {
  padding: 20px;
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


.table-container {
  margin-top: 16px;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.table-container :deep(.vxe-table) {
  flex: 1;
}

.table-container :deep(.vxe-table--main-wrapper) {
  height: 100% !important;
}

.table-container :deep(.vxe-table--body-wrapper) {
  height: calc(100% - 45px) !important;
}

.table-container :deep(.vxe-table--header) {
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
}

.table-container :deep(.vxe-table--header .vxe-header--row) {
  color: white;
  font-weight: bold;
}

.table-container :deep(.vxe-table--header .vxe-header--column) {
  background: transparent !important;
}

.table-container :deep(.vxe-table--body .vxe-body--column) {
  background: transparent !important;
}

.tree-cell {
  display: flex;
  align-items: center;
  min-height: 28px;
  width: 100%;
}

:deep(.vxe-table--body .vxe-body--row) {
  transition: background-color 0.2s ease;
}

:deep(.vxe-table--body .vxe-body--row:hover) {
  background-color: #f0f7ff !important;
}

.enum-header {
  margin-bottom: 20px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  border-radius: 8px;
  background: var(--qm-bg-1);
  border: 1px dashed #dcdfe6;
}

/* 步骤对话框样式 - 三栏垂直布局 */
.step-dialog-container {
  display: flex;
  gap: 20px;
  min-height: 600px;
  height: 600px;
}

/* 左侧：步骤列表 */
.step-sidebar {
  width: 280px;
  flex-shrink: 0;
  background: var(--qm-bg-1);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-section {
  background: var(--qm-bg-2);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--qm-text-1);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--qm-line);
  flex-shrink: 0;
}

.step-list-container {
  flex: 1;
  overflow: hidden;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
  overflow-y: auto;
  padding-right: 5px;
}

.step-list::-webkit-scrollbar {
  width: 6px;
}

.step-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.step-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.step-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--qm-bg-2);
  border: 1px solid var(--qm-line);
  flex-shrink: 0;
}

.step-item:hover {
  background: var(--qm-info-soft);
  border-color: #f59e0b;
  transform: translateX(4px);
}

.step-item.active {
  background: linear-gradient(135deg, #f59e0b, #79bbff);
  border-color: #f59e0b;
  color: white;
}

.step-index {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--qm-info-soft);
  color: #f59e0b;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.step-item.active .step-index {
  background: var(--qm-bg-2);
  color: #f59e0b;
}

.step-info {
  flex: 1;
  min-width: 0;
}

.step-type {
  font-size: 12px;
  color: var(--qm-text-3);
  margin-bottom: 4px;
}

.step-item.active .step-type {
  color: rgba(255, 255, 255, 0.8);
}

.step-desc {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 中间：变量类型选择 */
.variable-type-sidebar {
  width: 200px;
  flex-shrink: 0;
  background: var(--qm-bg-1);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.variable-type-container {
  flex: 1;
  overflow: hidden;
}

.variable-type-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
  overflow-y: auto;
  padding-right: 5px;
}

.variable-type-list::-webkit-scrollbar {
  width: 6px;
}

.variable-type-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.variable-type-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.variable-type-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.variable-type-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--qm-bg-2);
  border: 1px solid var(--qm-line);
  flex-shrink: 0;
}

.variable-type-item:hover {
  border-color: #f59e0b;
  background: var(--qm-info-soft);
  transform: translateX(4px);
}

.variable-type-item.active {
  background: linear-gradient(135deg, #f59e0b, #79bbff);
  border-color: #f59e0b;
  color: white;
}

.variable-type-item .el-icon {
  font-size: 18px;
  color: #f59e0b;
  width: 24px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.variable-type-item.active .el-icon {
  color: white;
}

.variable-type-item span {
  font-size: 14px;
  font-weight: 500;
  color: var(--qm-text-2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.variable-type-item.active span {
  color: white;
}

/* 右侧：步骤详情 */
.step-content {
  flex: 1;
  min-width: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.empty-step-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background: var(--qm-bg-2);
  border-radius: 8px;
  border: 1px dashed #dcdfe6;
}

.step-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--qm-bg-2);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--qm-line);
}

.step-header {
  padding: 20px;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 20%, var(--qm-bg-1) 100%);
  border-bottom: 1px solid var(--qm-line);
  flex-shrink: 0;
}

.step-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.step-number {
  font-size: 18px;
  font-weight: 600;
  color: var(--qm-text-1);
}

.step-name {
  font-size: 18px;
  font-weight: 600;
  color: #f59e0b;
}

.step-subtitle {
  font-size: 14px;
  color: var(--qm-text-2);
  margin-bottom: 4px;
}

.variable-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--qm-text-1);
}

.variable-content {
  flex: 1;
  min-height: 600px;
  padding: 0px 20px;
}

.variable-section {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 直接绑定内容 */
.direct-bind-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80%;
  padding: 20px;
}

.bind-info {
  background: var(--qm-bg-1);
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  max-width: 600px;
  width: 100%;
  border: 2px solid var(--qm-line);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.bind-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--qm-text-1);
  margin-bottom: 12px;
}

.bind-desc {
  font-size: 16px;
  color: var(--qm-text-2);
  margin-bottom: 24px;
  line-height: 1.5;
}

.bind-expression {
  background: var(--qm-bg-2);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 32px;
  border: 2px dashed #f59e0b;
}

.expression-label {
  font-size: 14px;
  color: var(--qm-text-2);
  margin-bottom: 8px;
  text-align: left;
}

.expression-value {
  font-size: 16px;
  font-weight: 600;
  color: #f59e0b;
  font-family: 'Courier New', monospace;
  word-break: break-all;
  text-align: left;
  padding: 8px;
  background: var(--qm-bg-1);
  border-radius: 4px;
}

.bind-action {
  display: flex;
  justify-content: center;
}

/* 函数对话框样式 */
.func-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.func-header {
  margin-bottom: 10px;
}

.func-actions {
  display: flex;
  justify-content: flex-end;
}

.func-content {
  flex: 1;
}

.func-collapse {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.func-collapse :deep(.el-collapse-item__header) {
  background: var(--qm-bg-1);
  padding: 0 20px;
  font-weight: 600;
  border-bottom: 1px solid var(--qm-line);
}

.func-collapse :deep(.el-collapse-item__content) {
  padding: 20px;
  background: var(--qm-bg-2);
}

.code-editor-container {
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--qm-line-strong);
}

.result-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0px;
  /* border-top: 1px solid var(--qm-line); */
  background: var(--qm-bg-1);
}

/* 全局对话框样式 */
:deep(.el-dialog) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  margin: 0;
  padding: 20px;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

:deep(.el-dialog__headerbtn) {
  top: 20px;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

:deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: #f0f0f0;
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: var(--qm-bg-4);
}

:deep(.el-tabs__item) {
  transition: all 0.3s ease;
}

:deep(.el-tabs__item:hover) {
  color: #f59e0b;
}

:deep(.el-tabs__item.is-active) {
  color: #f59e0b;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .step-dialog-container {
    flex-wrap: wrap;
    height: auto;
  }
  
  .step-sidebar {
    width: 100%;
    max-height: 200px;
    margin-bottom: 20px;
  }
  
  .variable-type-sidebar {
    width: 100%;
    max-height: 300px;
    margin-bottom: 20px;
  }
}

@media (max-width: 768px) {
  :deep(.params-dialog),
  :deep(.enum-dialog),
  :deep(.step-dialog),
  :deep(.func-dialog) {
    width: 95% !important;
  }
  
  .func-actions {
    margin-top: 16px;
    justify-content: flex-start;
  }
  
  .bind-info {
    padding: 20px;
  }
  
  .step-dialog-container {
    flex-direction: column;
  }
  
  .step-sidebar {
    width: 100%;
    max-height: 300px;
  }
  
  .variable-type-sidebar {
    width: 100%;
    max-height: 300px;
  }
  
  .step-list {
    flex-direction: row;
    overflow-x: auto;
  }
  
  .step-item {
    min-width: 200px;
    margin-bottom: 0;
    margin-right: 8px;
  }
  
  .variable-type-list {
    flex-direction: row;
    overflow-x: auto;
  }
  
  .variable-type-item {
    min-width: 120px;
    margin-bottom: 0;
    margin-right: 4px;
  }
}
</style>