<template>
  <el-dialog v-model="viewFuncVisiable" title="查看函数体" width="1250px" z-index="99999999" :append-to-body="true">
    <BodyEdit :bind_case_data="[]" v-model="func_script" lang="python" height="600px"></BodyEdit>
  </el-dialog>

  <div class="func-input-container">
    <el-input
      v-model="localValue"
      @focus="handleFocus"
      @blur="handleBlur"
      :disabled="disabled"
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
                    <span class="dropdown-item-text">常量引用</span>
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

  <!-- 环境变量引用弹窗 -->
  <el-dialog
    v-model="bindParamsVisible"
    title="全局变量引用"
    width="80%"
    :append-to-body="true"
    class="params-dialog"
    :close-on-click-modal="false"
  >
    <el-tabs v-model="bind_active_name"  class="tabs-container">
       <el-tab-pane label="全局变量" name="global_bind">
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
				  <el-button type="primary" @click="bind_global(row.name)"  class="dialog-confirm-btn" :icon="Select">
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
				  <el-button type="primary" @click="bind(row.name)"  class="dialog-confirm-btn" :icon="Select">
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
				  <el-button type="primary" @click="bind_case(row.name)"  class="dialog-confirm-btn" :icon="Select">
				  	<span class="button-text">绑定</span>
				  </el-button>
              </template>
            </vxe-column>
          </vxe-table>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="数据集" name="case_data" v-if="!is_case_data">
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
            <vxe-column title="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
				  <el-button type="primary" @click="bind_case_data_func(row.params_name)"  class="dialog-confirm-btn" :icon="Select">
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

  <!-- 枚举值引用弹窗 -->
  <el-dialog
    v-model="bindEnumVisible"
    title="枚举值引用"
    width="80%"
    :append-to-body="true"
    class="enum-dialog"
    :close-on-click-modal="false"
  >
    <div class="enum-header">
      <el-select
        v-model="enum_name"
        placeholder="请选择枚举类型"
        @change="enumChange"
        filterable
        size="large"
        style="width: 100%"
      >
        <el-option
          v-for="enum_obj in enum_list.results"
          :key="enum_obj.id"
          :label="`${enum_obj.name}${enum_obj.desc ? ' (' + enum_obj.desc + ')' : ''}`"
          :value="enum_obj"
        />
      </el-select>
    </div>
    
    <div class="table-container" v-if="enum_obj.value">
      <vxe-table
        :data="enum_obj.value"
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
			  <el-button type="primary" @click="bind_enum(row)"  class="dialog-confirm-btn" :icon="Select">
			  	<span class="button-text">绑定</span>
			  </el-button>
          </template>
        </vxe-column>
      </vxe-table>
    </div>
    
    <div v-else class="empty-state">
      <el-empty description="请选择枚举类型查看详情" />
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
    width="90%"
    :append-to-body="true"
    class="step-dialog"
    :close-on-click-modal="false"
    @closed="handleStepDialogClosed"
  >
    <div class="step-dialog-content">
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
                  <el-tooltip :content="step.desc" placement="right" effect="light">
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
              <!-- 步骤参数 -->
              <div 
                :class="['variable-type-item', { active: selectedVariableType === 'stepParams' }]" 
                @click="selectVariableType('stepParams')"
              >
                <el-icon><Collection /></el-icon>
                <span>步骤参数</span>
              </div>
              
              <!-- 函数参数 - 只显示在非请求类型步骤中 -->
              <div 
                :class="['variable-type-item', { active: selectedVariableType === 'funcParams' }]" 
                v-if="!isRequestType(currentStep)" 
                @click="selectVariableType('funcParams')"
              >
                <el-icon><MagicStick /></el-icon>
                <span>函数参数</span>
              </div>
              
              <!-- 公共项 -->
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
              <div 
                :class="['variable-type-item', { active: selectedVariableType === 'funcReturn' }]" 
                v-if="!isRequestType(currentStep)" 
                @click="selectVariableType('funcReturn')"
              >
                <el-icon><Refresh /></el-icon>
                <span>函数返回值</span>
              </div>
              
              <!-- 请求相关变量 - 只显示在请求类型步骤中 -->
              <template v-if="isRequestType(currentStep)">
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
        <div v-if="!selectedVariableType" class="empty-content">
          <el-empty description="请从左侧选择步骤和变量类型" />
        </div>
        
        <div v-else class="step-detail-content">
          <div class="content-header">
			<div class="step-title">
			  <span class="step-number">步骤 {{ parseInt(step_active_tab) + 1 }}</span>
			  <span class="step-number">{{ currentStep.desc || '未命名步骤' }}</span>
			  <span class="step-number">{{ getStepTypeLabel(currentStep) }}</span>
			  <span class="step-number">{{ getVariableTypeLabel(selectedVariableType) }}</span>
			</div>
<!--            <div class="title">{{ getVariableTypeLabel(selectedVariableType) }} 步骤 {{ {{ parseInt(step_active_tab) + 1 }} }}. {{ currentStep.desc || '未命名步骤' }}</div> -->
            <!-- <div class="subtitle">当前步骤: {{ step_active_tab + 1 }}. {{ currentStep.desc || '未命名步骤' }}</div> -->
          </div>
          
          <!-- 步骤参数 -->
          <div v-if="selectedVariableType === 'stepParams'" class="table-container">
            <div v-if="currentStep.step_params && currentStep.step_params.length > 0">
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
					  <el-button type="primary" @click="bind_step_params(row.name)"  class="dialog-confirm-btn" :icon="Select">
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
                  <div class="expression-value">${stepResponse.{{ case_step_id }}.stepParams}</div>
                </div>
                <div class="bind-action">
				  <el-button type="primary" @click="handleDirectBind('stepParams')"  class="dialog-confirm-btn" :icon="Select" size="large">
				  	<span class="button-text">确认绑定</span>
				  </el-button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 函数参数 -->
          <div v-else-if="selectedVariableType === 'funcParams'" class="table-container">
            <div v-if="one_step_obj.func_params && one_step_obj.func_params.length > 0">
              <vxe-table
                ref="funcTableRef"
                :data="one_step_obj.func_params"
                height="500"
                show-overflow
                row-id="id"
                border
                :row-config="{ isHover: true, keyField: 'id' }"
                :tree-config="treeConfig"
              >
                <vxe-column field="name" title="参数名称" min-width="250" tree-node align="center">
                  <template #default="{ row }">
                    <div class="tree-cell" :style="{ paddingLeft: (row._level - 1) * 20 + 'px' }">
                      {{ row.name }}
                    </div>
                  </template>
                </vxe-column>
                <vxe-column field="type" title="类型" min-width="120" align="center" />
                <vxe-column field="value" title="参数值" min-width="200" align="center" />
                <vxe-column field="explain" title="参数说明" min-width="200" align="center" />
                <vxe-column title="操作" width="120" align="center" fixed="right">
                  <template #default="{ row }">
					  <el-button type="primary" @click="bind_func_params(row)"  class="dialog-confirm-btn" :icon="Select">
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
                  <div class="expression-value">${stepResponse.{{ case_step_id }}.funcParams}</div>
                </div>
                <div class="bind-action">
					<el-button type="primary" @click="handleDirectBind('funcParams')"  class="dialog-confirm-btn" :icon="Select" size="large">
						<span class="button-text">确认绑定</span>
					</el-button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 请求头 -->
          <div v-else-if="selectedVariableType === 'apiRequestHeaders'" class="table-container">
            <div v-if="one_step_obj.api_headers && one_step_obj.api_headers.length > 0">
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
					<el-button type="primary" @click="bind_step_headers(row.name)"  class="dialog-confirm-btn" :icon="Select">
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
                  <div class="expression-value">${stepResponse.{{ case_step_id }}.apiRequestHeaders}</div>
                </div>
                <div class="bind-action">
					<el-button type="primary" @click="handleDirectBind('apiRequestHeaders')"  class="dialog-confirm-btn" :icon="Select" size="large">
						<span class="button-text">确认绑定</span>
					</el-button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 查询参数 -->
          <div v-else-if="selectedVariableType === 'apiRequestParams'" class="table-container">
            <div v-if="one_step_obj.api_params && one_step_obj.api_params.length > 0">
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
					  <el-button type="primary" @click="bind_api_params(row.name)"  class="dialog-confirm-btn" :icon="Select">
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
                  <div class="expression-value">${stepResponse.{{ case_step_id }}.apiRequestParams}</div>
                </div>
                <div class="bind-action">
					<el-button type="primary" @click="handleDirectBind('apiRequestParams')"  class="dialog-confirm-btn" :icon="Select" size="large">
						<span class="button-text">确认绑定</span>
					</el-button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 请求体 -->
          <div v-else-if="selectedVariableType === 'apiRequestBody'" class="table-container">
            <div v-if="one_step_obj.api_json && one_step_obj.api_json.length > 0">
              <vxe-table
                ref="bodyTableRef"
                :data="one_step_obj.api_json"
                height="500"
                show-overflow
                row-id="id"
                border
                :row-config="{ isHover: true, keyField: 'id' }"
                :tree-config="treeConfig"
              >
                <vxe-column field="name" title="参数名称" min-width="250" tree-node align="center">
                  <template #default="{ row }">
                    <div class="tree-cell" :style="{ paddingLeft: (row._level - 1) * 20 + 'px' }">
                      {{ row.name }}
                    </div>
                  </template>
                </vxe-column>
                <vxe-column field="type" title="类型" min-width="120" align="center" />
                <vxe-column field="value" title="参数值" min-width="200" align="center" />
                <vxe-column field="explain" title="参数说明" min-width="200" align="center" />
                <vxe-column title="操作" width="120" align="center" fixed="right">
                  <template #default="{ row }">
					  <el-button type="primary" @click="bind_body_params(row)"  class="dialog-confirm-btn" :icon="Select">
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
                  <div class="expression-value">${stepResponse.{{ case_step_id }}.apiRequestBody}</div>
                </div>
                <div class="bind-action">
					<el-button type="primary" @click="handleDirectBind('apiRequestBody')"  class="dialog-confirm-btn" :icon="Select" size="large">
						<span class="button-text">确认绑定</span>
					</el-button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 响应体 -->
          <div v-else-if="selectedVariableType === 'apiResponseBody'" class="table-container">
            <div v-if="one_step_obj.api_response && one_step_obj.api_response.length > 0">
              <vxe-table
                ref="responseTableRef"
                :data="one_step_obj.api_response"
                height="500"
                show-overflow
                row-id="id"
                border
                :row-config="{ isHover: true, keyField: 'id' }"
                :tree-config="treeConfig"
              >
                <vxe-column field="name" title="参数名称" min-width="250" tree-node align="center">
                  <template #default="{ row }">
                    <div class="tree-cell" :style="{ paddingLeft: (row._level - 1) * 20 + 'px' }">
                      {{ row.name }}
                    </div>
                  </template>
                </vxe-column>
                <vxe-column field="type" title="类型" min-width="120" align="center" />
                <vxe-column field="value" title="参数值" min-width="200" align="center" />
                <vxe-column field="explain" title="参数说明" min-width="200" align="center" />
                <vxe-column title="操作" width="120" align="center" fixed="right">
                  <template #default="{ row }">
					  <el-button type="primary" @click="bind_response_body(row)"  class="dialog-confirm-btn" :icon="Select">
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
                  <div class="expression-value">${stepResponse.{{ case_step_id }}.apiResponseBody}</div>
                </div>
                <div class="bind-action">
					<el-button type="primary" @click="handleDirectBind('apiResponseBody')"  class="dialog-confirm-btn" :icon="Select" size="large">
						<span class="button-text">确认绑定</span>
					</el-button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 直接绑定类型（无列表） -->
          <div v-else class="direct-bind-content">
            <div class="bind-info">
              <div class="bind-title">直接绑定</div>
              <div class="bind-desc">将绑定当前步骤的 {{ getVariableTypeLabel(selectedVariableType) }} 变量</div>
              <div class="bind-expression">
                <div class="expression-label">绑定表达式：</div>
                <div class="expression-value">${stepResponse.{{ case_step_id }}.{{ selectedVariableType }}}</div>
              </div>
              <div class="bind-action">
				  <el-button type="primary" @click="handleDirectBind(selectedVariableType)"  class="dialog-confirm-btn" :icon="Select" size="large">
				  	<span class="button-text">确认绑定</span>
				  </el-button>
              </div>
            </div>
          </div>
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
              <el-button type="primary" @click="singleRunFunction" :icon="VideoPlay">运行函数</el-button>
              <!-- <el-button v-if="func_script" type="primary" @click="viewFuncBody" :icon="View">查看函数体</el-button> -->
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
                      <FuncAndParams
                        :depth="depth + 1"
                        :value="row.value"
                        :row="row"
                        :bind_case_data="bind_case_data"
                        :step_index="step_index"
                        :steps="steps"
                        :bind_env_params="bind_env_params"
                        :bind_gloabl_params="bind_gloabl_params"
                        :case_table_data="processedCaseTableData"
                        :func_list="func_list"
                        :close-dialog="closeDialog"
                        @update:value="handleUpdateValue(row, $event)"
                        @closeDialog="handleCloseDialog"
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
                lang="text"
                theme="chrome"
                style="height: 100px"
                :options="editOption"
                readonly
              />
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="funcVisible = false">关闭</el-button>
        <el-button type="success" @click="insertStaticResult" :disabled="!func_run_result" :icon="DocumentAdd">
          插入静态结果
        </el-button>
        <el-button type="warning" @click="insertDynamicResult" :disabled="func_values.length === 0" :icon="Refresh">
          插入动态结果
        </el-button>
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
  DocumentAdd,
  Refresh,
  Timer,
  Check,
  Document,
  Cookie,
  Link,
  House,
  Operation,
  Collection,
  Search
} from '@element-plus/icons-vue';
import { mapState } from 'vuex';
import BodyEdit from './BodyEdit.vue';
import FuncAndParams from './FuncAndParams.vue';

export default {
  name: 'FuncAndParams',
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
      return this.sliceSteps[this.step_active_tab] || {};
    },
    // 处理用例变量数据，确保有value字段
    processedCaseTableData() {
      if (!this.case_table_data || !Array.isArray(this.case_table_data)) {
        return [];
      }
      return this.case_table_data.map(item => {
        // 如果item是字符串，转换为对象格式
        if (typeof item === 'string') {
          return {
            name: item,
            value: '',
            remark: ''
          };
        }
        // 如果item是对象，确保有value字段
        return {
          ...item,
          value: item.value || item.default_value || ''
        };
      });
    }
  },
  components: {
    BodyEdit,
    VAceEditor,
    FuncAndParams,
  },
  emits: ['update:value', 'closeDialog'],
  props: {
    row: {
      type: Object,
    },
    value: {
      type: String,
    },
    func_list: {
      type: Array,
    },
    bind_env_params: {
      type: Array,
    },
    bind_global_params: {
      type: Array,
    },
    bind_case_data: {
      type: Array,
    },
    case_table_data: {
      type: Array,
    },
    index: {
      type: Number,
    },
    step_index: {
      type: Number,
    },
    is_case_params: {
      type: Boolean,
      default: false,
    },
    is_case_data: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    steps: {
      type: Array,
      default: [],
    },
    depth: {
      type: Number,
      default: 0,
    },
    zIndex: {
      type: Number,
      default: 2000,
    },
    closeDialog: {
      type: Function,
      default: null
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
      DocumentAdd,
      Refresh,
      Timer,
      Check,
      Document,
      Cookie,
      Link,
      House,
      Operation,
      Collection,
      Search,
    };
  },
  data() {
    return {
      script: '',
      viewFuncVisiable: false,
      maxDepth: 3,
      step_active_tab: 0,
      step_id: '',
      case_step_id: '',
      selectedVariableType: '',
      _bind_case_data: [],
      one_step_obj: {},
      localValue: this.value,
      activeNames: ['1'],
      bind_active_name: 'global_bind',
      bind_case_params: [],
      StepParamsVisible: false,
      bindEnumVisible: false,
      enum_name: null,
      enum_obj: {},
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
      funcVisible: false,
      bindParamsVisible: false,
      func_values: [],
      func_script: '',
      func_desc: '',
      func_package: '',
      func_params: [],
      enum_list: [],
      func_name: '',
      func_run_result: '',
      type_list: ['Str', 'Int', 'Float', 'Dict', 'List', 'Bool'],
      variableTypeLabels: {
        stepParams: '步骤参数',
        funcParams: '函数参数',
        runTimes: '循环索引',
		runElement: '循环值',
        funcReturn: '函数返回值',
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
        this.selectedVariableType = '';
      }
    },
    step_active_tab(val) {
      if (val !== null && this.sliceSteps[val]) {
        this.step_id = this.sliceSteps[val].id;
        this.case_step_id = this.sliceSteps[val].case_step_id;
        this.getStep(this.step_id, this.case_step_id);
        // 切换步骤时清空选中的变量类型
        this.selectedVariableType = '';
      }
    },
    // 监听case_table_data变化，重新处理bind_case_params
    case_table_data: {
      handler() {
        this.initBindCaseParams();
      },
      deep: true
    }
  },
  methods: {
    // 处理关闭弹窗事件
    handleCloseDialog(dialogType) {
      this.$emit('closeDialog', dialogType);
    },
    
    // 关闭指定弹窗
    closeDialog(dialogType) {
      switch(dialogType) {
        case 'env':
          this.bindParamsVisible = false;
          break;
        case 'enum':
          this.bindEnumVisible = false;
          break;
        case 'step':
          this.StepParamsVisible = false;
          break;
        case 'func':
          this.funcVisible = false;
          break;
      }
    },
    
    // 初始化用例变量数据
    initBindCaseParams() {
      if (this.is_case_params) {
        // 如果是用例参数，只取当前索引之前的
        this.bind_case_params = [...(this.processedCaseTableData || []).slice(0, this.index)];
      } else {
        // 否则取全部
        this.bind_case_params = [...(this.processedCaseTableData || [])];
      }
    },
    
    // 检查步骤是否为请求类型
    isRequestType(step) {
      if (!step) return false;
      return step.type === this.StepType.Request || step.com_step_type === this.StepType.Request;
    },
    
    viewFuncBody() {
      this.viewFuncVisiable = true;
    },
    handleUpdateValue(row, newValue) {
      row.value = newValue;
      // 使用Vue.set确保响应式更新
      if (this.$set) {
        this.$set(row, 'value', newValue);
      } else {
        // 如果this.$set不可用，直接赋值
        row.value = newValue;
      }
    },
    handleUpdateName(row, newValue) {
      row.name = newValue;
    },
    handleFocus() {
      this.localValue = this.value;
    },
    enumChange(value) {
      this.enum_obj = { ...value };
    },
    handleBlur() {
      this.$emit('update:value', this.localValue);
    },
    handleCommand(command) {
      switch (command.type) {
        case 'func_generate':
          this.funcVisible = true;
          break;
        case 'bind_env_params':
          this.bindParamsVisible = true;
          break;
        case 'bind_enum':
          this.bindEnumVisible = true;
          break;
        case 'bind_step_params':
          this.StepParamsVisible = true;
          break;
      }
    },
    selectStepTab(index) {
      this.step_active_tab = index;
    },
    selectVariableType(type) {
      this.selectedVariableType = type;
    },
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
    getVariableTypeLabel(type) {
      return this.variableTypeLabels[type] || type;
    },
    handleDirectBind(type) {
      const templates = {
        apiStatusCode: 'stepResponse.${case_step_id}.apiStatusCode',
        apiRequestBody: 'stepResponse.${case_step_id}.apiRequestBody',
        apiResponseBody: 'stepResponse.${case_step_id}.apiResponseBody',
        apiRequestParams: 'stepResponse.${case_step_id}.apiRequestParams',
        apiRequestHeaders: 'stepResponse.${case_step_id}.apiRequestHeaders',
        runTimes: 'stepResponse.${case_step_id}.runTimes',
        apiUrl: 'stepResponse.${case_step_id}.apiUrl',
        apiHost: 'stepResponse.${case_step_id}.apiHost',
        apiUri: 'stepResponse.${case_step_id}.apiUri',
        apiResponseHeaders: 'stepResponse.${case_step_id}.apiResponseHeaders',
        apiResponseCookies: 'stepResponse.${case_step_id}.apiResponseCookies',
        apiMethod: 'stepResponse.${case_step_id}.apiMethod',
        funcReturn: 'stepResponse.${case_step_id}.funcReturn',
        funcParams: 'stepResponse.${case_step_id}.funcParams',
        stepParams: 'stepResponse.${case_step_id}.stepParams',
      };

      const variableType = type || this.selectedVariableType;
      if (templates[variableType]) {
        const value = '${' + templates[variableType].replace('${case_step_id}', this.case_step_id) + '}';
        this.localValue = this.localValue + value;
        this.$emit('update:value', this.localValue);
        this.StepParamsVisible = false;
        ElMessage.success('绑定成功！');
      }
    },
    handleStepDialogClosed() {
      this.step_active_tab = 0;
      this.selectedVariableType = '';
    },
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
      const value = '${envParams.' + name + '}';
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.bindParamsVisible = false;
      ElMessage.success('环境变量绑定成功！');
      
      // 如果有关闭弹窗函数，调用它
      if (this.closeDialog) {
        this.closeDialog('env');
      }
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'env');
    },
    bind_enum(row) {
      if (!this.enum_name) {
        ElMessage.warning('请先选择枚举类型');
        return;
      }
      const value = '${' + this.enum_name.name + '.' + row.name + '}';
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.bindEnumVisible = false;
      ElMessage.success('枚举值绑定成功！');
      
      // 如果有关闭弹窗函数，调用它
      if (this.closeDialog) {
        this.closeDialog('enum');
      }
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'enum');
    },
    bind_global(name) {
      const value = '${globalParams.' + name + '}';
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.bindParamsVisible = false;
      ElMessage.success('全局变量绑定成功！');

      // 如果有关闭弹窗函数，调用它
      if (this.closeDialog) {
        this.closeDialog('env');
      }
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'env');
    },
    bind_case(name) {
      const value = '${caseParams.' + name + '}';
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.bindParamsVisible = false;
      ElMessage.success('用例变量绑定成功！');
      
      // 如果有关闭弹窗函数，调用它
      if (this.closeDialog) {
        this.closeDialog('env');
      }
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'env');
    },
    bind_case_data_func(name) {
      const value = '${caseData.' + name + '}';
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.bindParamsVisible = false;
      ElMessage.success('数据集变量绑定成功！');
      
      // 如果有关闭弹窗函数，调用它
      if (this.closeDialog) {
        this.closeDialog('env');
      }
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'env');
    },
    bind_step_params(name) {
      const value = '${stepResponse.' + this.case_step_id + '.stepParams.' + name + '}';
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.StepParamsVisible = false;
      ElMessage.success('步骤参数绑定成功！');
      
      // 如果有关闭弹窗函数，调用它
      if (this.closeDialog) {
        this.closeDialog('step');
      }
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'step');
    },
    bind_api_params(name) {
      const value = '${stepResponse.' + this.case_step_id + '.apiRequestParams.' + name + '}';
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.StepParamsVisible = false;
      ElMessage.success('查询参数绑定成功！');
      
      // 如果有关闭弹窗函数，调用它
      if (this.closeDialog) {
        this.closeDialog('step');
      }
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'step');
    },
    bind_step_headers(name) {
      const value = '${stepResponse.' + this.case_step_id + '.apiRequestHeaders.' + name + '}';
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.StepParamsVisible = false;
      ElMessage.success('请求头绑定成功！');
      
      // 如果有关闭弹窗函数，调用它
      if (this.closeDialog) {
        this.closeDialog('step');
      }
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'step');
    },
    bind_body_params(row) {
      let path;
      if (row.parentId === null) {
        path = row.name;
      } else {
        path = this.loop_find_name_by_parent_id(row.parentId, this.one_step_obj.api_json, row.name);
        if (path.endsWith('.')) {
          path = path.slice(0, -1);
        }
      }
      const value = '${stepResponse.' + this.case_step_id + '.apiRequestBody.' + path + '}';
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.StepParamsVisible = false;
      ElMessage.success('请求体参数绑定成功！');
      
      // 如果有关闭弹窗函数，调用它
      if (this.closeDialog) {
        this.closeDialog('step');
      }
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'step');
    },
    bind_func_params(row) {
      let path;
      if (!row.parentId) {
        path = row.name;
      } else {
        path = this.loop_find_name_by_parent_id(row.parentId, this.one_step_obj.func_params, row.name);
        if (path.endsWith('.')) {
          path = path.slice(0, -1);
        }
      }
      const value = '${stepResponse.' + this.case_step_id + '.funcParams.' + path + '}';
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.StepParamsVisible = false;
      ElMessage.success('函数参数绑定成功！');
      
      // 如果有关闭弹窗函数，调用它
      if (this.closeDialog) {
        this.closeDialog('step');
      }
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'step');
    },
    bind_response_body(row) {
      let path;
      if (row.parentId === null) {
        path = row.name;
      } else {
        path = this.loop_find_name_by_parent_id(row.parentId, this.one_step_obj.api_response, row.name);
        if (path.endsWith('.')) {
          path = path.slice(0, -1);
        }
      }
      const value = '${stepResponse.' + this.case_step_id + '.apiResponseBody.' + path + '}';
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.StepParamsVisible = false;
      ElMessage.success('响应体参数绑定成功！');
      
      // 如果有关闭弹窗函数，调用它
      if (this.closeDialog) {
        this.closeDialog('step');
      }
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'step');
    },
    loop_find_name_by_parent_id(parentId, data, json_path) {
      for (const item of data) {
        if (item.id === parentId) {
          if (item.type === 'array') {
            json_path = item.name + '[' + json_path.split('.')[0] + ']' + '.' + json_path.split('.').slice(1).join('.');
          } else {
            json_path = item.name + '.' + json_path;
          }
          if (item.parentId !== null) {
            return this.loop_find_name_by_parent_id(item.parentId, data, json_path);
          } else {
            return json_path;
          }
        }
      }
      return json_path;
    },
    insertStaticResult() {
      if (!this.func_run_result) {
        ElMessage.error('请先执行函数获取执行结果');
        return;
      }
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.funcVisible = false;
      ElMessage.success('静态结果插入成功！');
      
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'func');
    },
    insertDynamicResult() {
      if (this.func_values.length === 0) {
        ElMessage.error('请先选择函数');
        return;
      }

      for (const param of this.func_params) {
        if (param.value === null || param.value === '') {
          ElMessage.error('请先填写函数入参值');
          return;
        }
      }

      let paramsKeyParts = [];
      for (let param of this.func_params) {
        let formattedParam = param.value;
        if (param.type === 'Str') {
          formattedParam = `'${param.value}'`;
        }
        paramsKeyParts.push(formattedParam);
      }

      const params_key = paramsKeyParts.join(', ');
      let function_name;
      if (this.func_values[0] === this.StepType.PlatformSystemFunction) {
        function_name = this.func_values[this.func_values.length - 1];
      } else {
        function_name = this.func_name;
      }

      const value = params_key ? `f{${function_name}(${params_key})}` : `f{${function_name}()}`;
      this.localValue = this.localValue + value;
      this.$emit('update:value', this.localValue);
      this.funcVisible = false;
      ElMessage.success('动态函数插入成功！');
      
      // 向上传递关闭弹窗事件
      this.$emit('closeDialog', 'func');
    },
    actionChange() {
      this.func_run_result = '';
      const step_type = this.func_values[0];
      const keyword = this.func_values[this.func_values.length - 1];
      const node = this.$refs.cascaderRef?.getCheckedNodes()[0];
      if (!node) return;

      if (step_type === this.StepType.PlatformSystemFunction) {
        this.func_script = node.data.script || '';
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
          if (this.one_step_obj.api_data && this.one_step_obj.api_data.length > 0) {
            this.one_step_obj.api_json = [...this.one_step_obj.api_data];
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
        console.error('获取枚举列表失败:', error);
      }
    },
    async singleRunFunction() {
      if (this.func_values.length === 0) {
        ElMessage.error('请先选择函数');
        return;
      }

      for (const param of this.func_params) {
        if (param.value === null || param.value === '') {
          ElMessage.error('请先填写函数入参值');
          return;
        }
      }

      try {
        let response;
        const func_type = this.func_values[0];
        const keyword = this.func_values[this.func_values.length - 1];

        if (func_type === this.StepType.PlatformSystemFunction) {
          response = await this.$api.singleRunFunction({ name: keyword, params: this.func_params });
        } else {
          const python_func_data = {
            name: this.func_name,
            script: this.func_script,
            package: this.func_package,
            params: this.func_params,
          };
          response = await this.$api.singleRunUserFunction({ python_func_obj: python_func_data });
        }

        if (response.status === 200) {
          this.func_run_result = String(response.data.result.result || '');
          this.activeNames = ['4'];
          ElMessage.success('函数执行成功！');
        } else if (response.status === 400) {
          this.func_run_result = '函数执行报错，请检查入参';
          ElMessage.error('函数执行报错，请检查入参');
        }
      } catch (error) {
        console.error('函数执行失败:', error);
        this.func_run_result = '函数执行失败，请检查网络或配置';
        ElMessage.error('函数执行失败，请检查网络或配置');
      }
    },
    deal_params_name() {
      this._bind_case_data = this.bind_case_data.map((value, index) => ({
        id: index,
        params_name: value,
      }));
    },
  },
  created() {
    this.getEnums();
    this.deal_params_name();
    this.initBindCaseParams();
  },
};
</script>

<style scoped>
.func-input-container {
  position: relative;
  width: 100%;
}

.func-input {
  width: 100%;
}

.func-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
  padding-right: 50px !important; /* 为下拉按钮留出空间 */
}

.func-input :deep(.el-input__wrapper:hover) {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 1px var(--el-color-primary-light-7);
}

.func-input :deep(.el-input__wrapper.is-focus) {
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

:deep(.params-dialog .el-dialog__body),
:deep(.enum-dialog .el-dialog__body),
:deep(.step-dialog .el-dialog__body),
:deep(.func-dialog .el-dialog__body) {
  padding: 20px;
}

.tabs-container {
  border-radius: 8px;
  overflow: hidden;
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

.step-dialog-content {
  display: flex;
  gap: 20px;
  min-height: 600px;
  height: 600px;
}

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

/* 中间：变量类型选择 */
.variable-type-sidebar {
  width: 220px;
  flex-shrink: 0;
  background: var(--qm-bg-1);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 右侧：具体变量内容 */
.step-content {
  flex: 1;
  min-width: 0;
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

.variable-type-item.active .el-icon {
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

.empty-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background: var(--qm-bg-2);
  border-radius: 8px;
  border: 1px dashed #dcdfe6;
}

.step-detail-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--qm-bg-2);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--qm-line);
}

.content-header {
  padding: 20px;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 20%, var(--qm-bg-1) 100%);
  border-bottom: 1px solid var(--qm-line);
  flex-shrink: 0;
}

.content-header .step-number {
  font-size: 18px;
  font-weight: 600;
  color: var(--qm-text-1);
}

.step-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.content-header .subtitle {
  font-size: 14px;
  color: var(--qm-text-1);
}

.direct-bind-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 20px;
  flex: 1;
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
  font-size: 18px;
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

@media (max-width: 1400px) {
  .step-dialog-content {
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
}
</style>