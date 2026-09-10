<template>
  <div class="api-edit-page">
      <el-card class="drawer-card elegant-shadow">
        <el-tabs v-model="active_api_tab" class="drawer-tabs"  @tab-click="handleClick">
          <el-tab-pane :label="apiTitle" name="doc" lazy='true'>
            <div class="drawer-form-container">
              <el-form :model="apiForm" :disabled='readView'  :rules="saveRules" ref='saveRef'>
                <!-- 基本信息 -->
                <div class="form-section-card elegant-shadow">
                  <div class="form-section-header">
                    <h3 class="section-title">基本信息</h3>
                  </div>
                  <el-row :gutter="20" class="form-row">
                    <el-col :span="12">
                      <el-form-item  prop="name" class="drawer-form-item">
						<template #label>
							<div class="drawer-label-wrapper">
							  <i class="icon-name"></i>
							  <span class="drawer-label-text">接口名称</span>
							</div>
						</template>
						<el-input v-model="apiForm.name"  placeholder="请输入接口名称" size='large' class='input' style='width:"calc(100vw)"'></el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item  prop="module"  class="drawer-form-item">
						<template #label>
							<div class="drawer-label-wrapper">
							  <i class="icon-module"></i>
							  <span class="drawer-label-text" style='width: 100px'>所属服务/模块</span>
							</div>
						</template>
                       
                        <el-cascader
                          collapse-tags 
                          v-model='apiForm.module' 
                          :options="service_module_list" 
                          :props="moduleProps" 

                          size='large'
						  style='width: 100%'
                          class="drawer-select drawer-cascader"
                          placeholder="请选择所属模块"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  
                  <el-row :gutter="20" class="form-row">
					  
					<el-col :span="12">
					  <el-form-item  prop="status"  class="drawer-form-item">
						<template #label>
							<div class="drawer-label-wrapper">
							  <i class="icon-status"></i>
							  <span class="drawer-label-text">接口状态</span>
							</div>
						</template>
					    <el-radio-group v-model="apiForm.status" class="drawer-radio-group" size='large'>
					      <el-radio-button v-for='(value, label) in api_status' :value="value">{{ label }}</el-radio-button>
					    </el-radio-group>
					  </el-form-item>
					</el-col>
					
                    <el-col :span="12">
                      <el-form-item  prop="url"  class="drawer-form-item">
						<template #label>
							<div class="drawer-label-wrapper">
							  <i class="icon-method"></i>
							  <span class="drawer-label-text" style='width: 100px'>请求方法/地址</span>
							</div>
						</template>
                       <el-input v-model="apiForm.url" placeholder="/user/login" size='large' class='input'>
                       	<template #prepend>
                       	    <el-select
							 v-model="apiForm.method"
								size='large'
								popper-class='select-dropdown-rounded'
								 placeholder="请选择请求方法"
								  style='width: 150px'>
                       	      <el-option v-for="http_method in methods" :label='http_method' :value="http_method" />
                       	    </el-select>    
                       	</template>
                       </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
                
                <!-- 请求信息 -->
                <div class="form-section-card elegant-shadow">
                  <div class="form-section-header">
                    <h3 class="section-title">请求信息</h3>
                  </div>
                  <div class='api_request_info'>
                    <el-tabs v-model="active_request_tab"  class="drawer-sub-tabs" >
                      <el-tab-pane label="请求头" name="headers" lazy='true'>
                        <Header :bind_case_data='[]' :tableData='apiForm.headers' :func_list='func_list' :bind_env_params='[]' :bind_global_params='[]'></Header>
                      </el-tab-pane>
                      <el-tab-pane label="Query参数" name="params" lazy='true'>
                        <Params :bind_case_data='[]' :tableData='apiForm.params' :func_list='func_list'></Params>
                      </el-tab-pane>
                      <el-tab-pane label="请求体" name="body">
                        <div class="body-type-wrapper">
                          <el-row class="body-type-header">
                            <el-radio-group v-model="apiForm.body_type" class="drawer-radio-group" fill="#6c6cff">
                              <el-radio-button :value="1" size="large">Json</el-radio-button>
                              <el-radio-button :value="2" size="large">Form</el-radio-button>
                            </el-radio-group>
                            <el-form-item  v-if='apiForm.body_type === 1' style="margin-bottom: 0px; margin-left: 20px;">
							  <el-tooltip content='Json根类型'>
								  <el-select v-model="apiForm.api_json_type"  style='width: 100px;' class="select"
            size='large'
            popper-class='select-dropdown-rounded' >
								    <el-option v-for="value in json_root_type" :label="value" :value="value" ></el-option>
								  </el-select>
							  </el-tooltip>
                            </el-form-item>
                          </el-row>
                          <div class="body-content">
                            <Data :bind_case_data='[]' :bind_env_params='[]' :bind_global_params='[]' :tableData='apiForm.data' :func_list='func_list' v-if='apiForm.body_type === 2'></Data>
                            <Json :bind_case_data='[]' :tableData='apiForm.json' :bind_env_params='[]' :bind_global_params='[]' :func_list='func_list' v-if='apiForm.body_type === 1'></Json>
                          </div>
                        </div>
                      </el-tab-pane>
                    </el-tabs>
                  </div>
                </div>
                
                <!-- 响应信息 -->
                <div class="form-section-card elegant-shadow">
                  <div class="form-section-header">
                    <h3 class="section-title">响应信息</h3>
                  </div>
                  <div class='api_response_info'>
                    <el-tabs v-model="response_tab_active"  editable @edit="addResponseTab" class="drawer-sub-tabs response-tabs">
                      <el-tab-pane v-for="(item, index) in apiForm.response" :key="index" :label="`Response[${item.response_status}]`" :name="index">
                        <Response :bind_case_data='[]' :tableData='item.response_data' :func_list='func_list' :bind_env_params='[]' :bind_global_params='[]'></Response>
                      </el-tab-pane>
                    </el-tabs>
                  </div>
                </div>
              </el-form>
            </div>
          </el-tab-pane>
          
          <!-- 接口测试标签页 -->
          <el-tab-pane label="接口测试" name="test" lazy='true' >
            <div class="drawer-form-container" ref="testScrollContainer">
              <el-form :model="testApiForm" :disabled='readView' class='drawer-form' :rules="runRules" ref='runRef'>
                <div class="form-section-card elegant-shadow">
                  <div class="form-section-header">
                    <h3 class="section-title">测试配置
					</h3>
                  </div>
                  <el-row :gutter="20" class="form-row">
                    <el-col :span="12">
                      <el-form-item  prop="name"  class="drawer-form-item">
						<template #label>
							<div class="drawer-label-wrapper">
							  <i class="icon-name" style="margin-left: 10px"></i>
							  <span class="drawer-label-text" style='width: 70px'>接口名称</span>
							</div>
						</template>
                        <el-input v-model="testApiForm.name"  size='large' class='input' placeholder="请输入接口名称"></el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12" >
                      <el-form-item  prop="module"  class="drawer-form-item">
						<template #label>
							<div class="drawer-label-wrapper">
							  <i class="icon-module"></i>
							  <span class="drawer-label-text"  style='width: 100px'>所属服务/模块</span>
							</div>
						</template>
                        <el-cascader 
                          collapse-tags 
						  size='large'
                          v-model='testApiForm.module' 
                          :options="service_module_list" 
                          :props="moduleProps"
						  style='width: 100%'
                          class="drawer-select drawer-cascader"
                          placeholder="请选择所属模块"
                          @change="handleModuleChange"
                        />
                      </el-form-item>
                    </el-col>

                  </el-row>
                  
                  <el-row :gutter="20" class="form-row">
					<el-col :span="12" style="padding-right: 0px;">
					  <el-form-item class="dialog-form-item" prop="host">
						<template #label>
						  <div class="drawer-label-wrapper">
						    <i class="icon-url"></i>
                             <el-tooltip placement="top" effect="light">
							<template #content>
							  <ul>
								<li>当前的请求域名仅用来查看该接口在当前配置下在不同环境下对应的请求域名</li>
								<li>当前接口所属服务中的接口域名配置为 -> {{ envServiceList.is_server_host ? '跟随服务域名配置': '跟随产品域名配置'}}</li>
								<li>当接口所属服务的接口域名配置为跟随产品域名配置时, 根据当前接口所属产品取[环境管理-产品配置-产品域名配置下对应环境和产品的产品域名]</li>
								<li>当接口所属服务的接口域名配置为跟随服务域名配置时, 根据当前接口所属服务取[环境管理-服务配置-服务域名配置下对应环境和服务的服务域名]</li>
								<li v-if='envServiceList.is_server_host' style="color: red;">
								  <el-link type="danger" underline @click="() => this.$router.push({ name: 'service' })">如果下拉框没有显示对应的环境, 则需要去配置,点击去添加</el-link>
								</li>
								<li v-if='!envServiceList.is_server_host' style="color: red;">
								  <el-link type="danger" underline @click="() => this.$router.push({ name: 'plant' })">如果下拉框没有显示对应的环境, 则需要去配置,点击去添加</el-link>
								</li>
							  </ul>
							</template>
							<el-icon color="green" class="info-icon"><InfoFilled /></el-icon>
						  </el-tooltip>
						    <span class="drawer-label-text" style="margin-left: -15px">请求域名</span>
						  </div>
						</template>
						<el-input v-model="testApiForm.host"  class="input" size='large' placeholder="选择环境后显示对应的请求域名" disabled>
						  <template #prepend>
							<el-select v-model="testApiForm.plant" style='width: 180px; margin-right:20px' @change="getRequestHosts"  class='input' size='large' popper-class='select-dropdown-rounded' v-if='!envServiceList.is_server_host' placeholder="请选择所属产品">
                               <el-option v-for="plant in plant_list.results" :label="plant.name" :value="plant.id" />
                            </el-select>
                            <el-select v-model='testApiForm.host' style='width: 180px;' size='large'  popper-class='select-dropdown-rounded' class='input' placeholder="请选择环境">
								<el-option v-for="obj in envServiceList.env_hosts"  color="#50E3C2" size="large"  :label='obj.env_name' :value="obj.host"></el-option>
							</el-select>
						  </template>
						</el-input>
					  </el-form-item>
					</el-col>
                    <el-col :span="12">
                      <el-form-item prop="method" class="drawer-form-item">
						<template #label>
							<div class="drawer-label-wrapper">
							  <i class="icon-method"></i>
							  <span class="drawer-label-text" style='width: 100px'>请求方法/地址</span>
							</div>
						</template>
                       <el-input v-model="testApiForm.url" placeholder="/user/login" size='large' class='input'>
						   <template #prepend>
						       <el-select v-model="testApiForm.method"   placeholder="请选择请求方法"
								size='large'
								popper-class='select-dropdown-rounded'
								style='width: 150px'>
						         <el-option v-for="http_method in methods" :label='http_method' :value="http_method" />
						       </el-select>  
						   </template>
					   </el-input>
                       
                      </el-form-item>
                    </el-col>
                    <!-- <el-col :span="2">
                     
                    </el-col> -->
                  </el-row>
                </div>
                
                <!-- 请求信息 -->
                <div class="form-section-card elegant-shadow">
                  <div class="form-section-header">
                    <h3 class="section-title">请求信息</h3>
                  </div>
                  <div class='api_request_info'>
                    <el-tabs v-model="test_active_request_tab"  class="drawer-sub-tabs" >
                      <el-tab-pane label="请求头" name="headers" lazy='true'>
                        <Header :isTest='true' :bind_case_data='[]' :tableData='testApiForm.headers' :bind_env_params='[]' :bind_global_params='[]' :func_list='func_list'></Header>
                      </el-tab-pane>
                      <el-tab-pane label="Query参数" name="params" lazy='true'>
                        <Params :isTest='true' :bind_case_data='[]' :tableData='testApiForm.params' :func_list='func_list'></Params>
                      </el-tab-pane>
                      <el-tab-pane label="请求体" name="body">
                        <div class="body-type-wrapper">
                          <el-row class="body-type-header">
                            <el-radio-group v-model="testApiForm.body_type" class="drawer-radio-group" fill="#6c6cff">
                              <el-radio-button :value="1" size="large">Json</el-radio-button>
                              <el-radio-button :value="2" size="large">Form</el-radio-button>
                            </el-radio-group>
                            <el-form-item v-if='testApiForm.body_type === 1' style="margin-bottom: 0px; margin-left: 20px;">
							  <el-tooltip content='Json根类型'>
								  <el-select v-model="testApiForm.api_json_type" style='width: 100px;' class="drawer-select drawer-sub-select" size='large'>
								    <el-option v-for="value in json_root_type" :label="value" :value="value" ></el-option>
								  </el-select>
							  </el-tooltip>
                            </el-form-item>
                          </el-row>
                          <div class="body-content">
                            <Data :isTest='true' :bind_env_params='[]' :bind_global_params='[]' :bind_case_data='[]' :tableData='testApiForm.data' :func_list='func_list' v-if='testApiForm.body_type === 2'></Data>
                            <Json :isTest='true' :bind_env_params='[]' :bind_global_params='[]' :bind_case_data='[]' :tableData='testApiForm.json' :func_list='func_list' v-if='testApiForm.body_type === 1'></Json>
                          </div>
                        </div>
                      </el-tab-pane>
                    </el-tabs>
                  </div>
                </div>

                <!-- 响应信息 -->
                <div class="form-section-card elegant-shadow" v-if='api_test_result' ref="testResponseSection">
                  <div class="form-section-header">
                    <h3 class="section-title">响应信息</h3>
                  </div>
                  <div class='api_request_info'>
                    <el-tabs v-model="test_active_response_tab"  class="drawer-sub-tabs" >
                       <el-tab-pane label="响应状态码" name="ResponseStatus"  lazy='true'>
                        <BodyEdit :bind_case_data='[]' v-model='this.api_test_result.response_status'></BodyEdit>
                      </el-tab-pane>
                      <el-tab-pane label="响应体" name="ResponseBody"  lazy='true'>
                        <BodyEdit :bind_case_data='[]' v-model='this.api_test_result.response_body'></BodyEdit>
                      </el-tab-pane>
                      <el-tab-pane label="响应头" name="ResponseHeader"  lazy='true'>
                        <BodyEdit :bind_case_data='[]' v-model='this.api_test_result.response_header'></BodyEdit>
                      </el-tab-pane>
                      <el-tab-pane label="请求头" name="RequestHeader"  lazy='true'>
                        <BodyEdit :bind_case_data='[]' v-model='this.api_test_result.request_header'></BodyEdit>
                      </el-tab-pane>
                      <el-tab-pane label="请求URL" name="RequestUrl"  lazy='true'>
                        <BodyEdit :bind_case_data='[]' v-model='this.api_test_result.request_url'></BodyEdit>
                      </el-tab-pane>
                      <el-tab-pane label="请求体" name="RequestBody"  lazy='true'>
                        <BodyEdit :bind_case_data='[]' v-model='this.api_test_result.request_body'></BodyEdit>
                      </el-tab-pane>
                    </el-tabs>
                  </div>
                </div>
              </el-form>
            </div>
          </el-tab-pane>

          <!-- 关联脚本用例标签页 -->
          <el-tab-pane label="关联脚本用例" name="case" v-if='!isAdd' lazy='true'>
            <div class="case-management">
              <div class="case-header">
                <div class="case-stat">
                  <i class="icon-case"></i>
                  <span class="case-stat-label">关联脚本用例个数：</span>
                  <span class="case-stat-number">{{ apiForm.case_num || 0 }}</span>
                </div>
                <div class="case-tip">
                  <el-icon color="var(--qm-text-3)"><InfoFilled /></el-icon>
                  <span>点击用例名称或查看按钮可跳转至脚本用例详情，底部「执行」按钮可批量运行勾选用例</span>
                </div>
              </div>

              <div class="table-wrapper" style="margin-top: 20px;">
                <el-table
                  v-if='apiForm.case_info && apiForm.case_info.length > 0'
                  :max-height='500'
                  :data="apiForm.case_info"
                  class='elegant-table'
                  :show-overflow-tooltip='true'
                  :header-row-style="headerRowStyle"
                  @selection-change="handleRunSelectionChange"
                >
                  <el-table-column type="selection" width="55" align="center" class-name="selection-column" />
                  <el-table-column label="用例信息" min-width="250" align="center" class-name="case-info-column">
                    <template #default="scope">
                      <div class="case-info-cell">
                        <div class="case-type-badge">
                          <el-tag size="small" :type="getTypeTagType(scope.row.type_name)" effect="light" class="type-tag">
                            {{ scope.row.type_name }}
                          </el-tag>
                        </div>
                        <el-link type="primary" :underline="false" @click="jumpCase(scope.row.id)" class="case-link">
                          {{ scope.row.name }}
                        </el-link>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column label="最近测试结果" prop="recent_test_result_name" width="120" align="center" class-name="result-column">
                    <template #default="scope">
                      <el-tag v-if='scope.row.recent_test_result_name ==="成功"' effect="dark" type="success" class="result-tag">{{ scope.row.recent_test_result_name }}</el-tag>
                      <el-tag v-else-if='scope.row.recent_test_result_name ==="失败"' effect="dark" type="danger" class="result-tag">{{ scope.row.recent_test_result_name }}</el-tag>
                      <el-tag v-else-if='scope.row.recent_test_result_name ==="错误"' effect="dark" type="danger" class="result-tag">{{ scope.row.recent_test_result_name }}</el-tag>
                      <el-tag v-else effect="dark" type="info" class="result-tag">{{ scope.row.recent_test_result_name || '未执行' }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="用例标签" prop="tag_name" min-width="160" align="center" class-name="tag-column">
                    <template #default="scope">
                      <div class="tags-container">
                        <el-tag v-for='obj in scope.row.tag_name' :key="obj.id" size="small" :type="getTagType(obj.name)" effect="light" class="case-tag">
                          {{ obj.name }}
                        </el-tag>
                        <span v-if="!scope.row.tag_name || scope.row.tag_name.length === 0" class="no-tag">-</span>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column label="创建信息" width="200" align="center" class-name="creator-column">
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
                  <el-table-column label="更新信息" width="200" align="center" class-name="updater-column">
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
                  <el-table-column align="center" :width="70" label="操作" class-name="action-column" fixed="right">
                    <template #default="scope">
                      <div class="action-buttons">
                        <el-tooltip content="查看用例" placement="top" effect="dark">
                          <el-button type="success" class="action-btn view-btn" @click="jumpCase(scope.row.id)" circle>
                            <el-icon><View /></el-icon>
                          </el-button>
                        </el-tooltip>
                      </div>
                    </template>
                  </el-table-column>
                </el-table>
                <el-empty v-else description="暂无关联脚本用例" />
              </div>

              <!-- AI自动生成用例：内联展开面板（点击底部按钮展开/收起） -->
              <el-collapse-transition>
                <div v-show="aiGenInlineOpen" class="ai-inline-panel">
                  <div class="ai-inline-header">
                    <div class="ai-inline-title">
                      <span class="ai-header-title">AI生成配置</span>
                      <el-tag v-if="aiGenTaskRunning" type="warning" size="small" effect="light" class="ai-task-tag">AI生成中…</el-tag>
                    </div>
                    <div class="ai-inline-header-right">
                      <el-popover
                        v-model:visible="aiModelPopoverVisible"
                        trigger="click"
                        placement="bottom-start"
                        :width="280"
                        popper-class="ai-model-popover"
                        :popper-options="{ modifiers: [{ name: 'flip', enabled: false }] }"
                      >
                        <template #reference>
                          <span class="ai-model-name">
                            {{ aiGenCurrentModelName || '选择模型' }}
                            <el-icon class="ai-model-arrow" :class="{ open: aiModelPopoverVisible }"><ArrowDown /></el-icon>
                          </span>
                        </template>
                        <template #default>
                          <div class="ai-model-list">
                            <div
                              v-for="c in aiConfigList.results"
                              :key="c.id"
                              class="ai-model-list-item"
                              :class="{ active: c.id === aiGenForm.ai_config_id }"
                              @click="aiGenSelectModel(c.id)"
                            >
                              <div class="ai-model-list-name">{{ c.name }}</div>
                              <div class="ai-model-list-desc">{{ c.model || c.model_name || '-' }}</div>
                              <el-icon v-if="c.id === aiGenForm.ai_config_id" class="ai-model-check"><SelectIcon /></el-icon>
                            </div>
                            <div v-if="!(aiConfigList.results && aiConfigList.results.length)" class="ai-model-list-empty">暂无可用模型</div>
                          </div>
                        </template>
                      </el-popover>
                      <el-button type="text" @click="closeAiGenInline" class="ai-inline-close" :disabled="aiGenSubmitting">
                        收起
                      </el-button>
                    </div>
                  </div>

                  <div class="ai-scroll-area">
                    <!-- 模块选择：Case模型模块树，label 与 input 中线对齐，宽度控制 -->
                    <el-form :model="aiGenForm" :rules="aiGenRules" ref="aiGenRef" label-width="86px" label-position="right" class="ai-module-form">
                      <el-form-item label="用例模块" prop="module_id">
                        <el-cascader
                          v-model="aiGenForm.module_id"
                          :options="aiGenCaseModuleList"
                          :props="aiGenModuleProps"
                          size='default'
                          style='max-width: 520px; width: 100%'
                          class="drawer-cascader"
                          placeholder="请选择用例所属模块"
                          filterable
                        />
                      </el-form-item>
                    </el-form>

                    <!-- 独立大标题：选择生成的用例类型 -->
                    <div class="ai-block-title">
                      <span class="ai-block-title-text">选择生成的用例类型</span>
                    </div>

                    <!-- 场景分组区：每张卡片头部统一为「左：正向/负向/边界值/安全性 小标题 + 右：全选checkbox」 -->
                    <div class="scenario-group" v-for="group in aiScenarioGroups" :key="group.key">
                      <div class="scenario-group-header">
                        <div class="scenario-group-title">{{ group.title }}</div>
                        <el-checkbox
                          v-model="group._allSelected"
                          :indeterminate="group._indeterminate"
                          @change="(val) => onScenarioGroupToggle(group, val)"
                          class="ai-scenario-checkbox"
                        >
                          全选
                        </el-checkbox>
                      </div>
                      <div class="scenario-group-items">
                        <el-checkbox
                          v-for="item in group.items"
                          :key="item.key"
                          v-model="item._selected"
                          @change="onScenarioItemToggle(group)"
                          class="ai-scenario-checkbox"
                        >
                          {{ item.label }}
                        </el-checkbox>
                      </div>
                    </div>

                    <!-- 补充需求：内联 style + 全局样式双重强制 200px 高度 -->
                    <el-input
                      v-model="aiGenForm.extra_requirement"
                      type="textarea"
                      :autosize="{ minRows: 9, maxRows: 20 }"
                      maxlength="800"
                      show-word-limit
                      size='default'
                      class="text ai-extra-input"
                      style="height:200px !important; min-height:200px !important;"
                      placeholder="请输入更多要求"
                    />
                  </div>

                  <div class="ai-inline-footer">
                    <el-button @click="closeAiGenInline" :disabled="aiGenSubmitting" class="dialog-cancel-btn">取消</el-button>
                    <el-button
                      type="primary"
                      class="ai-submit-btn"
                      :loading="aiGenSubmitting"
                      @click="submitAiGenerate"
                    >
                      生成
                    </el-button>
                  </div>
                </div>
              </el-collapse-transition>
            </div>
          </el-tab-pane>

          <!-- 高级Mock标签页 -->
          <el-tab-pane label="高级Mock" name="mock" v-if='!isAdd' lazy='true'>
            <div class="mock-management">
              <div class="mock-header">
                <el-button v-if='permission.has_add_permission && !readView' @click="addMockApi" type='primary' class="drawer-add-btn">新增Mock</el-button>
                <div class="mock-actions">
                  <el-tooltip content="快速测试"> 
                    <el-icon :size="size" :color="color" style="margin-right: 15px;" @click="mockTestChange" v-if="(permission.has_add_permission || permission.has_edit_permission) && !readView && api_mock_list.results.length !=0">
                      <Position />
                    </el-icon>
                  </el-tooltip>
                  <el-tooltip content="复制Mock地址">
                    <el-icon :size="size" :color="color" style="margin-right: 15px;" @click="copy">
                      <CopyDocument />
                    </el-icon>
                  </el-tooltip>
                  <el-link type="primary" :underline="false" class="mock-link">示例调用地址: {{ $api.base_url }}/api_mock/{{ apiForm.id }}{{ apiForm.url }}</el-link>
                </div>
              </div>
              
              <div class="table-wrapper" style="margin-top: 20px;">
                <el-table :max-height='500' :data="api_mock_list.results" class='elegant-table' :show-overflow-tooltip='true' :header-row-style="headerRowStyle">
                  <el-table-column label="序号" width="70" type="index" align="center" class-name="index-column">
                    <template #default="scope">
                      <div class="index-cell">
                        {{ scope.$index + 1 }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column label="Mock名称" prop="name" min-width="200" align="center" class-name="name-column"/>
                  <el-table-column label="Mock描述" prop="desc" min-width="400" align="center" class-name="desc-column"/>
                  <el-table-column label="启用" prop="is_enable" width="80" align="center" class-name="enable-column">
                    <template #default="scope">
                      <el-switch v-model="scope.row.is_enable" @change='isEnableChange(scope.row)' :disabled="!permission.has_edit_permission || readView" class="enable-switch"/>
                    </template>
                  </el-table-column>
                  <el-table-column label="创建信息" width="180" align="center" class-name="create-info-column">
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
                  <el-table-column label="更新信息" width="180" align="center" class-name="update-info-column">
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
                  <el-table-column align="center" :width='calcMockWidth' label="操作" class-name="action-column">
                    <template #default="scope">
                      <div class="action-buttons">
                        <el-tooltip content="查看MockApi">
                          <el-button type="success" v-if="permission.has_read_permission" class="action-btn view-btn" @click="ViewMock(scope.row)" circle>
                            <el-icon><View /></el-icon>
                          </el-button>
                        </el-tooltip>
                        <el-tooltip content="编辑MockApi">
                          <el-button type='warning' v-if="permission.has_edit_permission && !readView" class="action-btn edit-btn" @click="editMock(scope.row)" circle>
                            <el-icon><EditPen /></el-icon>
                          </el-button>
                        </el-tooltip>
                        <el-tooltip content="删除MockApi">
                          <el-button type="danger" v-if="permission.has_delete_permission && !readView" @click="deleteMock(scope.row.id)" class="action-btn delete-btn" circle>
                            <el-icon><Delete /></el-icon>
                          </el-button>
                        </el-tooltip>
                      </div>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </el-tab-pane>
          
          <!-- Mock测试标签页 -->
          <el-tab-pane label="Mock测试" name="mock_test" lazy='true' v-if='mockTestVisible && !isAdd'>
            <div class="drawer-form-container">
              <el-form :model="mockTestForm" :disabled='readView' class='drawer-form'>
                <div class="form-section-card elegant-shadow">
                  <div class="form-section-header">
                    <h3 class="section-title">Mock测试配置</h3>
                  </div>
                  <el-row :gutter="20" class="form-row">
                    <el-col :span="12">
                      <el-form-item   class="drawer-form-item">
						<template #label>
							<div class="drawer-label-wrapper">
							  <i class="icon-method"></i>
							  <span class="drawer-label-text" style='width: 100px'>请求方法/地址</span>
							</div>
						</template>
						<el-input v-model="mockTestForm.url" placeholder="/user/login" disabled size='large' class='input'>
							<template #prepend>
								<el-select v-model="mockTestForm.method"  placeholder="请选择请求方法"  style='width: 120px' class="select"
            size='large'
            popper-class='select-dropdown-rounded' >
								  <el-option v-for="http_method in methods" :label='http_method' :value="http_method" />
								</el-select>
							</template>
						</el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label-width="0" class="drawer-form-item">
                        <el-button type="primary" size='large' @click='testMockApi' v-if='(permission.has_add_permission || permission.has_edit_permission) && !isRunApi' class="drawer-confirm-btn drawer-send-btn">发送</el-button>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
                
                <!-- 请求信息 -->
                <div class="form-section-card elegant-shadow">
                  <div class="form-section-header">
                    <h3 class="section-title">请求信息</h3>
                  </div>
                  <div class='api_request_info'>
                    <el-tabs v-model="mock_test_active_request_tab"  class="drawer-sub-tabs" >
                      <el-tab-pane label="请求头" name="headers" lazy='true'>
                        <Header :bind_case_data='[]' :tableData='mockTestForm.headers' :func_list='func_list' :bind_env_params='[]' :bind_global_params='[]'></Header>
                      </el-tab-pane>
                      <el-tab-pane label="Query参数" name="params" lazy='true'>
                        <Params :bind_case_data='[]' :tableData='mockTestForm.params' :bind_env_params='[]' :bind_global_params='[]' :func_list='func_list'></Params>
                      </el-tab-pane>
                      <el-tab-pane label="请求体" name="body">
                        <div class="body-type-wrapper">
                          <el-row class="body-type-header">
                            <el-radio-group v-model="mockTestForm.body_type" class="drawer-radio-group" fill="#6c6cff">
                              <el-radio-button :value="1" size="large">Json</el-radio-button>
                              <el-radio-button :value="2" size="large">Form</el-radio-button>
                            </el-radio-group>
                            <el-form-item    style='margin-bottom: 0px; margin-left: 20px;' v-if='mockTestForm.body_type === 1' >
								<el-tooltip content="Json根类型">
									<el-select v-model="apiMockForm.api_json_type" style='width: 100px;' class="select"
            size='large'
            popper-class='select-dropdown-rounded' >
									  <el-option v-for="value in json_root_type" :label="value" :value="value" ></el-option>
									</el-select>
								</el-tooltip>
                            </el-form-item>
                          </el-row>
                          <div class="body-content">
                            <Data :bind_case_data='[]' :bind_env_params='[]' :bind_global_params='[]' :tableData='mockTestForm.data' :func_list='func_list' v-if='mockTestForm.body_type === 2'></Data>
                            <Json :bind_case_data='[]' :bind_env_params='[]' :bind_global_params='[]' :tableData='mockTestForm.json' :func_list='func_list' v-if='mockTestForm.body_type === 1'></Json>
                          </div>
                        </div>
                      </el-tab-pane>
                    </el-tabs>
                  </div>
                </div>
				
				<!-- 响应信息 -->
				    <div class="form-section-card elegant-shadow" v-if='typeof mock_api_test_result === "object"'>
				      <div class="form-section-header">
				        <h3 class="section-title">响应信息</h3>
				      </div>
				      <div class='api_request_info'>
				        <el-tabs v-model="mock_test_active_response_tab"  class="drawer-sub-tabs" >
				          <el-tab-pane label="响应状态码" name="response_status"  lazy='true'>
				            <BodyEdit :bind_case_data='[]' v-model='this.mock_api_test_result.response_status'></BodyEdit>
				          </el-tab-pane>
						  <el-tab-pane label="响应体" name="response_body"  lazy='true'>
						    <BodyEdit :bind_case_data='[]' v-model='this.mock_api_test_result.response_body'></BodyEdit>
						  </el-tab-pane>
						  <el-tab-pane label="响应头" name="response_header"  lazy='true'>
						    <BodyEdit :bind_case_data='[]' v-model='this.mock_api_test_result.response_header'></BodyEdit>
						  </el-tab-pane>
						  <el-tab-pane label="请求头" name="request_header"  lazy='true'>
						    <BodyEdit :bind_case_data='[]' v-model='this.mock_api_test_result.request_header'></BodyEdit>
						  </el-tab-pane>
						  <el-tab-pane label="请求Query参数" name="request_params"  lazy='true'>
						    <BodyEdit :bind_case_data='[]' v-model='this.mock_api_test_result.request_params'></BodyEdit>
						  </el-tab-pane>
						  <el-tab-pane label="请求体" name="request_body"  lazy='true'>
						    <BodyEdit :bind_case_data='[]' v-model='this.mock_api_test_result.request_body'></BodyEdit>
						  </el-tab-pane>
				        </el-tabs>
				      </div>
				    </div>
              </el-form>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
        <div class="drawer-footer">
          <div class="footer-right">
			<el-button type="primary" @click="goBack" class="drawer-cancel-btn">返回</el-button>
            <el-button type="primary" @click="viewLatestReport" v-if='!isAdd && active_api_tab === "case" && latestApiReport' class="drawer-confirm-btn">查看报告</el-button>
            <el-button type="primary" class="drawer-confirm-btn" :loading="aiGenSubmitting" @click="toggleAiGenInline" v-if='permission.has_add_permission && !isAdd && !readView && active_api_tab === "case"'>
              AI自动生成用例
            </el-button>
            <el-button type="primary" @click="openRunDialog" v-if='!isAdd && !readView && active_api_tab === "case"' class="drawer-confirm-btn">执行</el-button>
			<el-button type="primary" @click='testApi' v-if='(permission.has_add_permission || permission.has_edit_permission) && !isRunApi && !readView && this.active_api_tab==="test"' class="drawer-confirm-btn drawer-send-btn">发送</el-button>
            <el-button v-if='(permission.has_add_permission || permission.has_edit_permission) && !isRunApi && !readView && active_api_tab ==="doc"' type="primary" @click='saveApi(false)' class="drawer-confirm-btn">保存</el-button>
            <el-button v-if='(permission.has_add_permission || permission.has_edit_permission) && !isRunApi && !readView && active_api_tab ==="doc"' type="primary" @click='saveApi(true)' class="drawer-confirm-btn">保存并关闭</el-button>

          </div>
        </div>
    <el-drawer v-model="mockVisible" :with-header='false'  class="api-drawer" :show-close='false' direction='rtl' size='100%'>
      <el-card class="drawer-card elegant-shadow">
        <el-tabs v-model="active_mock_tab" class="drawer-tabs" >
          <el-tab-pane :label="mockTitle" name="mock" lazy='true'>
            <div class="drawer-form-container">
				<el-form :model="apiMockForm" label-position='right' class="drawer-tabs" :rules="mockRules" ref='mockRef' :disabled='readMockView'>
						<div class="form-section-card elegant-shadow">
						  <div class="form-section-header">
						    <h3 class="section-title">基本信息</h3>
						  </div>
						  <div class="mock-form-wrapper">
						    <el-row :gutter="20">
						      <el-col :span="12">
						        <el-form-item label="MockApi名称" prop='name'>
						          <el-input v-model="apiMockForm.name" placeholder="请输入MockApi名称" type='textarea' :rows="3" maxlength='50' show-word-limit class="text" size='large'></el-input>
						        </el-form-item>
						      </el-col>
						      <el-col :span="12">
						        <el-form-item label="MockApi描述" prop='desc'>
						          <el-input v-model="apiMockForm.desc" placeholder="请输入MockApi描述" type='textarea' :rows="3" maxlength='200' show-word-limit class="text" size='large'></el-input>
						        </el-form-item>
						      </el-col>
						    </el-row>
						  </div>
						</div>
				
						<div class="mock-tabs-wrapper form-section-card elegant-shadow">
						  <div class="form-section-header">
							<h3 class="section-title">请求触发条件</h3>
						  </div>
						  <div class='api_request_info'>
							<el-tabs v-model="mock_active_request_tab"   class="drawer-sub-tabs">
							  <el-tab-pane label="请求头" name="headers" lazy='true'>
								<MockHeader :bind_case_data='[]' :tableData='apiMockForm.headers' :func_list='func_list' :height="250" :check_methods="check_methods"></MockHeader>
							  </el-tab-pane>
							  <el-tab-pane label="Query参数" name="params" lazy='true'>
								<MockParams :bind_case_data='[]' :tableData='apiMockForm.params' :func_list='func_list' :height='250' :check_methods='check_methods'></MockParams>
							  </el-tab-pane>
							  <el-tab-pane label="请求体" name="Body">
								<div class="body-type-wrapper">
								  <el-row class="body-type-header">
									<el-radio-group v-model="apiMockForm.body_type" fill="#6c6cff">
									  <el-radio-button :value="1" size="large">Json</el-radio-button>
									  <el-radio-button :value="2" size="large">Form</el-radio-button>
									</el-radio-group>
									<el-form-item v-if='apiMockForm.body_type === 1'  style="margin-bottom: 0px; margin-left: 20px;"  label-position="right">
										<el-tooltip content="Json根类型">
											<el-select v-model="apiMockForm.api_json_type" style='width: 100px;' class="select" size='large'
            popper-class='select-dropdown-rounded' >
												<el-option v-for="value in json_root_type" :label="value" :value="value" ></el-option>
											</el-select>
										</el-tooltip>
									</el-form-item>
								  </el-row>
								  <MockJson :bind_case_data='[]' :tableData='apiMockForm.json' :func_list='func_list' :height='250' :check_methods='check_methods' v-if='apiMockForm.body_type === 1'></MockJson>
								  <MockData :bind_case_data='[]' :tableData='apiMockForm.data' :func_list='func_list' :height='250' :check_methods='check_methods' v-if='apiMockForm.body_type === 2'></MockData>
								</div>
							  </el-tab-pane>
							</el-tabs>
						  </div>
						</div>
						<div class="form-section-card elegant-shadow">
						  <div class="form-section-header">
						    <h3 class="section-title">Mock响应信息</h3>
						  </div>
						  <el-tabs v-model="mock_active_response_tab"   class="drawer-sub-tabs">
						    <el-tab-pane label="响应头" name="headers" lazy='true'>
								<Header :bind_case_data='[]' :bind_env_params='[]' :bind_global_params='[]' :tableData='apiMockForm.response_headers' :func_list='func_list'></Header>
						    </el-tab-pane>
							<el-tab-pane label="响应体" name="body" lazy='true'>
								<div class="response-type-wrapper">
									<el-row class="body-type-header" type="flex" align="middle" style="padding: 8px 0;">
									  <!-- 左侧 Radio 组 -->
									  <el-col :span="6">
										<el-radio-group v-model="apiMockForm.response_type" fill="#6c6cff" size="large" style='margin-left: 20px'>
										  <el-radio-button :value="2">跟随 API 文档</el-radio-button>
										  <el-radio-button :value="1">自定义响应体</el-radio-button>	  
										</el-radio-group>
									  </el-col>
									  
									  <!-- 右侧三个设置项 -->
									  <el-col :span="18">
										<div style="display: flex; justify-content: flex-end; align-items: center; gap: 32px; margin-right: 30px">
										  <!-- JSON根类型 -->
										  <div style="display: flex; align-items: center;">
											<span style="
											  font-size: 14px; 
											  font-weight: 500;
											  color: var(--qm-text-1); 
											  margin-right: 10px; 
											  white-space: nowrap;
											  letter-spacing: 0.2px;
											">JSON根类型</span>
											<el-select 
											  v-model="apiMockForm.api_response_type" 
											  style="width: 110px;" 
											  class="select"
											  size='large'
											  popper-class='select-dropdown-rounded'
											  placeholder="选择类型"
											>
											  <el-option v-for="value in json_root_type" :label="value" :value="value"></el-option>
											</el-select>
										  </div>
										</div>
									  </el-col>
									</el-row>
								  <div v-if='apiMockForm.response_type === 1'>
									<MockResponse :bind_case_data='[]' :tableData='apiMockForm.response' :func_list='func_list' :height='250' :check_method='check_methods'></MockResponse>
								  </div>
								  
								  <div v-if='apiMockForm.response_type === 2' class="follow-api-info">
									<el-alert 
									  type="info" 
									  show-icon 
									  :closable="false"
									  style="margin-top: 10px;"
									>
									  <template #title>
										<span>系统会根据 API 文档返回参数自动生成返回内容，当 API 文档变更时，返回结果也会实时变更，每次返回必定是不同的随机数据。</span>
									  </template>
									</el-alert>
								  </div>
								</div>
							</el-tab-pane>
							<el-tab-pane label="高级设置" name="setting" lazy='true'>
								<el-form-item label-width="100px" label="响应状态码">
									<el-select
									  v-model="apiMockForm.status_code"
									  filterable
									  allow-create
									  default-first-option
									  :reserve-keyword="false"
									  placeholder="选择或输入"
									  class="select"
									  size='large'
									  popper-class='select-dropdown-rounded'
									  style="width: 200px;" 
									  
									>
									  <el-option
										v-for="item in http_status"
										:key="item"
										:label="item"
										:value="item"
									  />
									</el-select>
								</el-form-item>
								<el-form-item label-width="100px" label="响应延迟(ms)">
									<el-input-number 
									  v-model="apiMockForm.timeout" 
									  :min="0" 
									  :max="5000" 
									  :step="100"
									  class="input" 
									  style="width: 200px;" 
									  size="large"
									  controls-position="right"
									  placeholder="输入延迟时间"
									/>
									<el-alert
									  type="info" 
									  show-icon 
									  :closable="false"
									  style='width: 230px; margin-left: 20px'
									>
									  <template #title>
										<span> 最大延迟时间为：3000 ms</span>
									  </template>
									</el-alert>
								</el-form-item>
							</el-tab-pane>
						  </el-tabs>
						</div>
				</el-form>
			</div>
		  </el-tab-pane>
		</el-tabs>
	  </el-card>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="()=>{mockVisible = false}" class="dialog-cancel-btn">取消</el-button>
          <el-button type="primary" @click="saveMock" class="dialog-confirm-btn" v-if='!readMockView'>确定</el-button>
        </div>
      </template>
    </el-drawer>
    <el-dialog v-model="responseStatusVisible" title="新增响应返回体" width="300" append-to-body='append_to_body' :show-close='show_close' class="elegant-dialog">
      <el-select
        :disabled='disabled'
        v-model="response_status"
        filterable
        allow-create
        default-first-option
        :reserve-keyword="false"
        placeholder="请选择或输入响应状态码"
        class="select"
        size='large'
        popper-class='select-dropdown-rounded'
      >
        <el-option
          v-for="item in http_status"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="responseStatusVisible = false" class="dialog-cancel-btn">取消</el-button>
          <el-button @click="saveResponse" class="dialog-confirm-btn">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 执行脚本用例对话框 -->
    <el-dialog v-model="runCaseVisible" title="执行脚本用例" width="500" class="elegant-dialog">
      <el-form :model="runCaseForm" label-width="100px" class="run-dialog-form" :rules="runCaseRules" ref='runCaseRef' label-position='top'>
        <el-form-item label="执行环境" prop="env_id">
          <el-select v-model="runCaseForm.env_id" placeholder="请选择执行环境" class="select" size='large' popper-class='select-dropdown-rounded' style="width: 100%;">
            <el-option
              v-for="item in env_list.results"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="测试报告名称" prop="title">
          <el-input v-model='runCaseForm.title' placeholder="请输入测试报告名称" class='input' size='large'></el-input>
        </el-form-item>
        <el-form-item label="失败重试次数" prop="rerun_times">
          <el-input-number v-model="runCaseForm.rerun_times" :precision="0" :step="1" :min='0' :max="3" style='width: 100%;' class="input" size='large' />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="runCaseVisible = false" class="dialog-cancel-btn">取消</el-button>
          <el-button type="primary" @click="confirmRunCase" class="dialog-confirm-btn">确认</el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script>
import api from '../../api/index.js'
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
  VideoPlay,
  ArrowDown,
  Select as SelectIcon
} from '@element-plus/icons-vue'
import Params from '../../components/Params.vue'
import MockParams from '../../components/MockParams.vue'
import Header from '../../components/Header.vue'
import MockHeader from '../../components/MockHeader.vue'
import Json from '../../components/Json.vue'
import MockJson from '../../components/MockJson.vue'
import Response from '../../components/Response.vue'
import MockResponse from '../../components/MockResponse.vue'
import MockData from '../../components/MockData.vue'
import Data from '../../components/Data.vue'
import BodyEdit from '../../components/BodyEdit.vue'

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
    },

    // AI生成用例：当前选中的模型显示名
    aiGenCurrentModelName() {
      const list = this.aiConfigList.results || []
      const cfg = list.find(c => c.id === this.aiGenForm.ai_config_id)
      if (!cfg) return ''
      return cfg.model || cfg.model_name || cfg.name || ''
    },

    // AI生成用例：场景分组动态数据源（带全选/半选状态）
    aiScenarioGroups() {
      const buildGroup = (title, key, items) => {
        const selectedCount = items.filter(i => i._selected).length
        const _allSelected = selectedCount === items.length
        const _indeterminate = selectedCount > 0 && selectedCount < items.length
        return { title, key, items, _allSelected, _indeterminate }
      }
      const f = this.aiGenForm
      return [
        buildGroup('正向', 'positive', [
          { key: 'positive_required_only',    label: '仅传必要字段', _selected: !!f.positive_required_only },
          { key: 'positive_semantic_valid',   label: '语义合法',     _selected: !!f.positive_semantic_valid },
          { key: 'positive_enum_combo',       label: '覆盖枚举组合', _selected: !!f.positive_enum_combo },
          { key: 'positive_other',            label: '其他正向',     _selected: !!f.positive_other },
        ]),
        buildGroup('负向', 'negative', [
          { key: 'negative_invalid_value',       label: '无效值',         _selected: !!f.negative_invalid_value },
          { key: 'negative_missing_required',    label: '缺失必填字段',   _selected: !!f.negative_missing_required },
          { key: 'negative_format_error',        label: '格式错误',       _selected: !!f.negative_format_error },
          { key: 'negative_type_error',          label: '类型错误',       _selected: !!f.negative_type_error },
          { key: 'negative_semantic_invalid',    label: '语义非法',       _selected: !!f.negative_semantic_invalid },
          { key: 'negative_other',               label: '其他负向',       _selected: !!f.negative_other },
        ]),
        buildGroup('边界值', 'boundary', [
          { key: 'boundary_max_min',             label: '极大值/极小值',           _selected: !!f.boundary_max_min },
          { key: 'boundary_out_of_range',        label: '超出最大、最小边界值',     _selected: !!f.boundary_out_of_range },
          { key: 'boundary_null_zero_empty',     label: 'Null/零值/空值',          _selected: !!f.boundary_null_zero_empty },
          { key: 'boundary_string_length',       label: '字符串过长、过短',         _selected: !!f.boundary_string_length },
        ]),
        buildGroup('安全性', 'security', [
          { key: 'security_auth_control',    label: '鉴权控制',   _selected: !!f.security_auth_control },
          { key: 'security_sql_inject',      label: 'SQL注入',    _selected: !!f.security_sql_inject },
          { key: 'security_fuzzy_input',     label: '模糊输入',   _selected: !!f.security_fuzzy_input },
          { key: 'security_xss_inject',      label: 'XSS注入',    _selected: !!f.security_xss_inject },
          { key: 'security_command_inject',  label: '命令行注入', _selected: !!f.security_command_inject },
          { key: 'security_json_inject',     label: 'JSON注入',   _selected: !!f.security_json_inject },
          { key: 'security_nosql_inject',    label: 'NoSQL注入',  _selected: !!f.security_nosql_inject },
        ]),
      ]
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
      runCaseVisible: false,
      selectedRunCases: [],
      runCaseForm: {
        env_id: '',
        title: '',
        rerun_times: 0
      },
      runCaseRules: {
        env_id: [{ required: true, message: '请选择执行环境', trigger: 'change' }],
        title: [{ required: true, message: '请输入测试报告名称', trigger: 'blur' }],
        rerun_times: [{ required: true, message: '失败重试次数不能为空', trigger: 'blur' }]
      },
      latestApiReport: null,
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
      automationTypes: [
        { label: '接口自动化', value: '1' },
        { label: 'Web自动化', value: '2' },
        { label: 'App自动化', value: '3' },
        { label: '造数脚本', value: '4' },
        { label: '性能测试', value: '5' },
      ],
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
      service_module_list: [],
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
      append_to_body: true,
      // AI生成用例
      aiGenInlineOpen: false,
      aiGenTaskRunning: false,
      aiGenSubmitting: false,
      aiGenPollTimer: null,
      aiModelPopoverVisible: false,
      aiConfigList: { results: [] },
      aiGenTagList: { results: [] },
      aiGenCaseModuleList: [],
      aiGenModuleProps: {
        emitPath: false,
        value: 'id',
        label: 'name',
        checkStrictly: true,
      },
      aiGenForm: {
        ai_config_id: null,
        module_id: null,
        generate_count: 5,
        extra_requirement: '',
        // 细粒度场景选项 (后端接口是4个粗粒度开关 + extra_requirement)
        // 正向
        positive_required_only: true,
        positive_semantic_valid: true,
        positive_enum_combo: true,
        positive_other: false,
        // 负向 (会映射到 include_missing_required / include_type_error / include_exception_status)
        negative_invalid_value: false,
        negative_missing_required: false,
        negative_format_error: false,
        negative_type_error: false,
        negative_semantic_invalid: false,
        negative_other: false,
        // 边界值 (映射到 include_boundary)
        boundary_max_min: false,
        boundary_out_of_range: false,
        boundary_null_zero_empty: false,
        boundary_string_length: false,
        // 安全性 (映射到 include_security)
        security_auth_control: false,
        security_sql_inject: false,
        security_fuzzy_input: false,
        security_xss_inject: false,
        security_command_inject: false,
        security_json_inject: false,
        security_nosql_inject: false,
      },
      aiGenRules: {
        module_id: [{ required: true, message: '请选择用例模块', trigger: 'change' }],
      }
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
    Fold,
    VideoPlay,
    ArrowDown,
    SelectIcon
  },
  watch: {
    filterServiceText(val) {
      if (this.$refs.treeRef) {
        this.$refs.treeRef.filter(val)
      }
    }
  },
  beforeDestroy() {
    this.stopAiTaskPolling()
  },
  methods:{
    handleRunSelectionChange(selection) {
      this.selectedRunCases = selection
    },
    openRunDialog() {
      if (!this.selectedRunCases || this.selectedRunCases.length === 0) {
        ElMessage({ message: '请选择脚本用例', type: 'warning' })
        return
      }
      // 组装报告名默认值：接口名称 + 固定文案：关联脚本用例
      const apiName = this.apiForm.name || ''
      this.runCaseForm = {
        env_id: '',
        title: `${apiName}${apiName ? '-' : ''}关联脚本用例`,
        rerun_times: 0
      }
      this.runCaseVisible = true
      this.$nextTick(() => {
        if (this.$refs.runCaseRef) {
          this.$refs.runCaseRef.clearValidate()
        }
      })
    },
    confirmRunCase() {
      this.$refs['runCaseRef'].validate(async (valid, fields) => {
        if (valid) {
          this.runCaseVisible = false
          const scriptCaseIds = this.selectedRunCases.map(c => c.id)
          const params = {
            env_id: this.runCaseForm.env_id,
            title: this.runCaseForm.title,
            rerun_times: this.runCaseForm.rerun_times,
            script_cases: scriptCaseIds,
            api_id: this.apiForm.id
          }
          const response = await this.$api.runSuite(params)
          ElMessage({ message: response.data.result.message, type: 'success' })
          this.$router.push({ path: '/report/listView', query: { id: response.data.result.report_id } })
        }
      })
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
    getTagType(tagName) {
      if (!tagName) return ''
      const colors = ['', 'success', 'info', 'warning', 'danger']
      const hash = tagName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
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

     handleClick(tab, event) {
      if (tab.props.name === 'doc' && !this.apiForm.id) {
        this.apiForm = JSON.parse(JSON.stringify(this.testApiForm))
      } else if (tab.props.name === 'test' && !this.apiForm.id) {
        this.testApiForm = JSON.parse(JSON.stringify(this.apiForm))
        this.getRequestHosts()
      } else if (tab.props.name === 'case' && this.apiForm.id) {
        this.fetchLatestApiReport()
      }
     },
    async fetchLatestApiReport() {
      this.latestApiReport = null
      if (!this.apiForm.id) return
      try {
        const res = await this.$api.getReports({ api: this.apiForm.id, page: 1, size: 1 })
        const list = (res.data.result || res.data)?.results || []
        if (list.length > 0) {
          this.latestApiReport = list[0]
        }
      } catch (e) {
        console.error('获取最新测试报告失败:', e)
      }
    },
    viewLatestReport() {
      if (this.latestApiReport) {
        // 跳转到报告详情页前，记录当前接口 id 与激活的 Tab，便于返回时恢复定位
        sessionStorage.setItem('apiEdit_restore_tab', JSON.stringify({apiId: this.apiForm.id, tab: this.active_api_tab}))
        this.$router.push({ path: '/report/listView', query: { id: this.latestApiReport.id } })
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
				this.getServiceModule()
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
      // 跳转到用例编辑页前，记录当前接口 id 与激活的 Tab，便于返回时恢复定位
      sessionStorage.setItem('apiEdit_restore_tab', JSON.stringify({apiId: this.apiForm.id, tab: this.active_api_tab}))
      this.$router.push({path: '/resource/scriptCaseEdit', query: {id: case_id}})
    },

    // ===== AI自动生成接口脚本用例 =====
    async loadAiConfigsForGen() {
      try {
        const res = await api.getAiConfigs({ project: this.projectInfo.id, page: 1, size: 100, is_active: true })
        if (res && res.data) {
          this.aiConfigList = res.data
          const list = this.aiConfigList.results || []
          if (list.length > 0 && !this.aiGenForm.ai_config_id) {
            // 优先：localStorage 保存的用户上次选择 → 项目默认 → 列表第一个
            const cachedId = localStorage.getItem(`ai_model_${this.projectInfo.id}`)
            let defaultCfg = null
            if (cachedId) {
              const cid = Number(cachedId)
              defaultCfg = list.find(c => c.id === cid || String(c.id) === cachedId)
            }
            if (!defaultCfg) defaultCfg = list.find(c => c.is_default) || list[0]
            if (defaultCfg) this.aiGenForm.ai_config_id = defaultCfg.id
          }
        }
      } catch (e) {
        // 静默失败，用户手动选时会发现没有选项
      }
    },

    // 加载Case模型模块树（脚本用例所属模块）
    async loadAiCaseModules() {
      try {
        const res = await this.$api.getAllPlantModule({ project: this.projectInfo.id })
        if (res && res.status === 200) {
          this.aiGenCaseModuleList = res.data.results || []
        }
      } catch (e) {
        // 静默失败
      }
    },

    async loadTagsForAiGen() {
      try {
        const res = await api.getTags({ project: this.projectInfo.id, page: 1, size: 200 })
        if (res && res.data) {
          this.aiGenTagList = res.data
        }
      } catch (e) {
        // 静默失败
      }
    },

    toggleAiGenInline() {
      // 再次点击时：AI生成中不允许关闭（防止误操作中断用户的进度感），其它情况切换显隐
      if (this.aiGenSubmitting) return
      if (this.aiGenInlineOpen) {
        this.closeAiGenInline()
        return
      }
      if (!this.apiForm.id) {
        ElMessage({ message: '请先保存接口文档，再使用AI生成用例', type: 'warning' })
        return
      }
      // 若还未加载Case模块树，立即加载
      if (!this.aiGenCaseModuleList || this.aiGenCaseModuleList.length === 0) {
        this.loadAiCaseModules()
      }
      this.aiGenInlineOpen = true
    },

    closeAiGenInline() {
      if (this.aiGenSubmitting) return
      this.aiGenInlineOpen = false
      this.aiModelPopoverVisible = false
    },

    // 选择AI模型（面板头部popover）
    aiGenSelectModel(configId) {
      this.aiGenForm.ai_config_id = configId
      this.aiModelPopoverVisible = false
      if (this.projectInfo && this.projectInfo.id) {
        localStorage.setItem(`ai_model_${this.projectInfo.id}`, String(configId))
      }
    },

    // AI场景：全选组
    onScenarioGroupToggle(group, val) {
      const form = this.aiGenForm
      group.items.forEach(it => {
        if (Object.prototype.hasOwnProperty.call(form, it.key)) {
          form[it.key] = !!val
        }
      })
    },

    // AI场景：子项切换(computed aiScenarioGroups 会自动重算全选/半选状态)
    onScenarioItemToggle(group) {
      const form = this.aiGenForm
      group.items.forEach(it => {
        if (Object.prototype.hasOwnProperty.call(form, it.key)) {
          form[it.key] = !!it._selected
        }
      })
    },

    submitAiGenerate() {
      const f = this.aiGenForm
      // 先做自定义校验（已不再走 aiGenRules 中 ai_config_id 校验）
      if (!f.ai_config_id) {
        // 自动打开模型 popover 提示用户选
        this.aiModelPopoverVisible = true
        ElMessage({ message: '请先选择AI模型', type: 'warning' })
        return
      }

      // 表单校验 (目前只校验 module_id)
      this.$refs.aiGenRef.validate(async (valid) => {
        if (!valid) return

        // ===== 1. 细粒度子场景 -> 后端粗粒度开关 映射 =====
        const hasBoundary = f.boundary_max_min || f.boundary_out_of_range || f.boundary_null_zero_empty || f.boundary_string_length
        const hasMissingRequired = f.negative_missing_required
        const hasTypeError = f.negative_type_error || f.negative_format_error
        const hasExceptionStatus = f.negative_invalid_value || f.negative_semantic_invalid || f.negative_other
        const hasSecurity = f.security_auth_control || f.security_sql_inject || f.security_fuzzy_input || f.security_xss_inject || f.security_command_inject || f.security_json_inject || f.security_nosql_inject

        // ===== 2. 正向/负向/安全性的细粒度要求 -> 拼到 extra_requirement，让 LLM 参考 =====
        const tips = []
        const positiveSelected = [
          f.positive_required_only && '仅传必要字段',
          f.positive_semantic_valid && '语义合法',
          f.positive_enum_combo && '覆盖枚举组合',
          f.positive_other && '其他正向用例',
        ].filter(Boolean)
        if (positiveSelected.length) tips.push('正向场景细化：' + positiveSelected.join('、'))

        const negativeSelected = [
          f.negative_invalid_value && '无效值',
          f.negative_missing_required && '缺失必填字段',
          f.negative_format_error && '格式错误',
          f.negative_type_error && '类型错误',
          f.negative_semantic_invalid && '语义非法',
          f.negative_other && '其他负向用例',
        ].filter(Boolean)
        if (negativeSelected.length) tips.push('负向场景细化：' + negativeSelected.join('、'))

        const boundarySelected = [
          f.boundary_max_min && '极大值/极小值',
          f.boundary_out_of_range && '超出边界值',
          f.boundary_null_zero_empty && 'Null/零值/空值',
          f.boundary_string_length && '字符串长度边界',
        ].filter(Boolean)
        if (boundarySelected.length) tips.push('边界值场景细化：' + boundarySelected.join('、'))

        const securitySelected = [
          f.security_auth_control && '鉴权控制',
          f.security_sql_inject && 'SQL注入',
          f.security_fuzzy_input && '模糊输入',
          f.security_xss_inject && 'XSS注入',
          f.security_command_inject && '命令行注入',
          f.security_json_inject && 'JSON注入',
          f.security_nosql_inject && 'NoSQL注入',
        ].filter(Boolean)
        if (securitySelected.length) {
          tips.push('安全性场景(额外生成)：' + securitySelected.join('、'))
        }

        // 合并用户手写补充需求
        let mergedExtra = tips.join('\n')
        if (f.extra_requirement && f.extra_requirement.trim()) {
          mergedExtra = (mergedExtra ? mergedExtra + '\n\n' : '') + '用户补充要求：\n' + f.extra_requirement.trim()
        }

        this.aiGenSubmitting = true
        try {
          const res = await api.aiGenerateApiCase({
            api_id: this.apiForm.id,
            project_id: this.projectInfo.id,
            ai_config_id: f.ai_config_id,
            module_id: f.module_id,
            tag_ids: [],
            generate_count: Number(f.generate_count) || 5,
            include_boundary: hasBoundary,
            include_missing_required: hasMissingRequired,
            include_type_error: hasTypeError,
            include_exception_status: hasExceptionStatus,
            include_security: hasSecurity,
            extra_requirement: mergedExtra,
          })
          if (res && res.status >= 200 && res.status < 300 && res.data) {
            const result = res.data.result || res.data
            if (result && result.task_id) {
              ElMessage({ message: result.message || 'AI生成任务已提交，生成中请稍候…', type: 'success' })
              this.startAiTaskPolling(result.task_id)
            } else {
              ElMessage({ message: '任务提交失败，请稍后重试', type: 'error' })
            }
          } else {
            const detail = (res && res.data && (res.data.detail || res.data.msg)) || '任务提交失败，请稍后重试'
            ElMessage({ message: detail, type: 'error' })
          }
        } catch (e) {
          const msg = (e && e.response && e.response.data && e.response.data.detail) || '任务提交失败，请稍后重试'
          ElMessage({ message: msg, type: 'error' })
        } finally {
          this.aiGenSubmitting = false
        }
      })
    },

    startAiTaskPolling(taskId) {
      this.stopAiTaskPolling()
      this.aiGenTaskRunning = true
      let ticks = 0
      const maxTicks = 120 // 最多轮询 10 分钟 (5s * 120)
      this.aiGenPollTimer = setInterval(async () => {
        ticks += 1
        try {
          const res = await api.aiTaskStatus({ task_id: taskId })
          const data = (res && res.data && (res.data.result || res.data)) || {}
          if (data.status === 'success' || data.status === 'done') {
            this.stopAiTaskPolling()
            this.aiGenTaskRunning = false
            ElMessage({ message: 'AI生成完成，正在刷新用例列表…', type: 'success' })
            // 任务成功，刷新当前接口的关联用例列表
            await this.refreshApiCaseList()
            // 同步刷新最新报告
            this.fetchLatestApiReport()
          } else if (data.status === 'failed' || data.status === 'error') {
            this.stopAiTaskPolling()
            this.aiGenTaskRunning = false
            ElMessage({ message: data.message || 'AI生成任务失败', type: 'error' })
          } else if (data.status === 'running' || data.status === 'pending') {
            // 继续等待
          } else if (data.status === 'not_found') {
            // 任务不存在或已过期，结束轮询
            this.stopAiTaskPolling()
            this.aiGenTaskRunning = false
          }
        } catch (e) {
          // 网络错误不终止轮询，直到达到 maxTicks
        }
        if (ticks >= maxTicks) {
          this.stopAiTaskPolling()
          this.aiGenTaskRunning = false
          ElMessage({ message: 'AI生成任务仍在后台执行，完成后会发送站内信通知', type: 'info' })
        }
      }, 5000)
    },

    stopAiTaskPolling() {
      if (this.aiGenPollTimer) {
        clearInterval(this.aiGenPollTimer)
        this.aiGenPollTimer = null
      }
    },

    async refreshApiCaseList() {
      try {
        if (!this.apiForm.id) return
        const res = await api.getApi(this.apiForm.id)
        if (res && res.data) {
          const data = res.data
          this.apiForm.case_num = data.case_num || 0
          this.apiForm.case_info = data.case_info || []
        }
      } catch (e) {
        // 刷新失败不阻塞
      }
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
           this.goBack()
        }else{
          this.apiForm = {...response.data.result}
          this.testApiForm = JSON.parse(JSON.stringify(this.apiForm))
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
           this.goBack()
        }
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
              this.test_active_response_tab = 'ResponseStatus'
              ElMessage({message: "执行完成", type: 'success'})
              this.$nextTick(() => {
                this.scrollToTestResponse()
              })
            }
          }
        }
      })
    },
    scrollToTestResponse() {
      const container = this.$refs.testScrollContainer
      const target = this.$refs.testResponseSection
      if (container && target) {
        const targetEl = Array.isArray(target) ? target[0].$el || target[0] : (target.$el || target)
        const containerEl = Array.isArray(container) ? container[0].$el || container[0] : (container.$el || container)
        if (containerEl.scrollIntoView !== undefined && targetEl.offsetTop !== undefined) {
          containerEl.scrollTo({
            top: targetEl.offsetTop - 12,
            behavior: 'smooth'
          })
        }
      }
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
      this.$emit('update:chooseApiVisible', false)
      this.$emit('setApiData', apiData)
    },
    editApi(row_data){
      this.apiTitle = '编辑接口文档'
      this.isAdd = false
      this.readView = false
      this.apiForm = {...row_data}
      this.testApiForm = JSON.parse(JSON.stringify(this.apiForm))
      this.getMocks()
	    this.getRequestHosts()
	    this.getPlants()
    },
    editMock(row_data){
      this.mockTitle = '编辑MockApi'
      this.isMockAdd = false
      this.readMockView = false
      this.apiMockForm = {...row_data}
      this.mockVisible = true
    },
    runApi(row_data){
      this.apiTitle = '接口测试'
      this.isRunApi = true
      this.readView = false
      this.apiForm = {...row_data}
      this.getEnvs()
    },
    ViewApi(row_data){
      this.apiTitle = '查看接口文档'
      this.isAdd = false
      this.readView = true
      this.apiForm = {...row_data}
      this.getMocks()
    },
    ViewMock(row_data){
      this.mockTitle = '查看MockApi'
      this.isMockAdd = false
      this.readMockView = true
      this.apiMockForm = {...row_data}
      this.mockVisible = true
    },
    addApi(){
      this.apiTitle = '新增接口文档'
      this.active_api_tab = 'doc'
      this.isAdd = true
      this.readView = false
      this.apiForm = {...this.tmpApiForm}
      const moduleId = this.$route.query.module
      const serviceId = this.$route.query.service
      if (moduleId) {
        this.apiForm.module = Number(moduleId)
      }
      if (serviceId) {
        this.apiForm.service = Number(serviceId)
      }
      this.getPlants()
      if (this.$refs.runRef) {
        this.$refs.runRef.resetFields();
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
    async getServiceModule(){
      const response = await this.$api.getAllServiceModule({project: this.projectInfo.id})
      if (response.status === 200){
        this.service_module_list = response.data.results
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
        // 确保DOM已更新
        
        // 等待异步获取数据
        const row = await this.getApi(this.$route.query.apiId)
        
        // 调用查看方法
        this.ViewApi(row)
        
        // 清除查询参数
        this.$router.replace({
          path: this.$route.path,
          query: {}
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
          const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission['/resource/api']}
          const response = await this.$api.check_permission(params)
          if (response.status === 200){
               this.permission = { ...response.data.result }
          }
	 },
	goBack(){
	  this.$router.push('/resource/api')
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
  async created() {
    this.check_permission()
	this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
    this.tmpApiForm = {...this.apiForm}
    this.tmpApiMockForm = {...this.apiMockForm}
    this.getCheck()
    this.getfuncs()
    this.getServiceModule()
    this.getServices()
    this.getEnvs()
    // 异步加载 AI 模型配置与标签列表，用于 AI 生成用例弹窗
    this.loadAiConfigsForGen()
    this.loadAiCaseModules()
    this.loadTagsForAiGen()
    const mode = this.$route.query.mode || 'create'
    const id = this.$route.query.id
    if ((mode === 'edit' || mode === 'view') && id) {
      const row = await this.getApi(id)
      if (mode === 'edit') {
        this.editApi(row)
      } else {
        this.ViewApi(row)
      }
    } else {
      this.addApi()
    }
    // 从 URL query 读取指定 Tab（如从消息通知跳转时 tab=case）
    const queryTab = this.$route.query.tab
    if (queryTab && ['doc', 'test', 'case', 'mock_test'].includes(queryTab)) {
      this.active_api_tab = queryTab
      if (queryTab === 'case') {
        this.$nextTick(() => this.fetchLatestApiReport())
      }
    }
    // 从用例编辑页返回时，恢复上一次激活的 Tab（如"关联脚本用例"）
    const restoreInfo = sessionStorage.getItem('apiEdit_restore_tab')
    if (restoreInfo) {
      try {
        const { apiId, tab } = JSON.parse(restoreInfo)
        if (String(apiId) === String(id) && tab) {
          this.active_api_tab = tab
          if (tab === 'case') {
            this.$nextTick(() => this.fetchLatestApiReport())
          }
        }
      } catch (e) {}
      sessionStorage.removeItem('apiEdit_restore_tab')
    }
  }
}
</script>

<style scoped>
.api-edit-page {
  width: 100%;
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  padding: 20px 15px 0 15px;
  box-sizing: border-box;
  height: calc(100vh - 75px);
  max-height: calc(100vh - 75px);
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;
}
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
  /* 防止子元素（如 case-management + 内联面板）把卡片宽度撑出视口 */
  min-width: 0;
  max-width: 100%;
  width: 100%;
  box-sizing: border-box;
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

.dialog-select >>> .el-input__inner,
.dialog-input >>> .el-input__inner,
.dialog-textarea >>> .el-textarea__inner {
  border-radius: 12px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  padding: 0 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.dialog-select >>> .el-input__inner:hover,
.dialog-input >>> .el-input__inner:hover,
.dialog-textarea >>> .el-textarea__inner:hover {
  border-color: var(--qm-line-strong);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-select >>> .el-input__inner:focus,
.dialog-input >>> .el-input__inner:focus,
.dialog-textarea >>> .el-textarea__inner:focus {
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

/* 页面主卡片只保留顶部圆角，与底部 footer 融为一体 */
.api-edit-page > .drawer-card {
  border-radius: 16px 16px 0 0;
}

/* drawer-tabs 整体容器 - 需填充剩余高度并让内部内容滚动 */
.drawer-tabs {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
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

.drawer-tabs >>> .el-tabs__content .el-tab-pane {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.drawer-form-container {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  min-height: 0;
}

/* 抽屉内部内容区滚动条样式 */
.drawer-form-container::-webkit-scrollbar {
  width: 6px;
}
.drawer-form-container::-webkit-scrollbar-track {
  background: var(--qm-bg-1);
  border-radius: 4px;
}
.drawer-form-container::-webkit-scrollbar-thumb {
  background: var(--qm-line-strong);
  border-radius: 4px;
}
.drawer-form-container::-webkit-scrollbar-thumb:hover {
  background: var(--qm-line-strong);
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

/* 抽屉页脚样式 - 与主卡片融为一体，固定在底部 */
.drawer-footer {
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
  overflow-x: hidden;
  overflow-y: auto;
  /* 防止 case-header + el-table + AI面板把宽度顶出父容器 */
  min-width: 0;
  max-width: 100%;
  width: 100%;
  box-sizing: border-box;
}

.case-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: var(--qm-bg-1);
  border-radius: 12px;
  border: 1px solid var(--qm-line-strong);
  box-sizing: border-box;
  width: 100%;
  max-width: 100%;
  min-width: 0;
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

.run-case-footer-btn {
  padding: 10px 24px !important;
  border-radius: 10px !important;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%) !important;
  border: none !important;
  font-weight: 500;
  transition: all 0.3s ease;
}

.run-case-footer-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.icon-case {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 4px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

/* 关联脚本用例表格样式 */
.case-info-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.case-type-badge {
  display: flex;
  justify-content: center;
}

.type-tag {
  font-size: 12px;
  border-radius: 4px;
}

.result-tag {
  min-width: 60px;
  text-align: center;
  border-radius: 6px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 4px;
}

.case-tag {
  border-radius: 4px;
}

.no-tag {
  color: var(--qm-line-strong);
  font-size: 14px;
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
  flex: 1;
  min-height: 0;
  box-sizing: border-box;
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
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
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
	color: var(--qm-text-2);
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

/* AI生成配置内联面板 - 局部样式（scoped，直接作用于面板节点） */
/* 三段式 flex：header + 可滚动内容 + footer，始终能看到头尾，滚动只在中段 */
.ai-inline-panel {
  margin-top: 20px;
  border: 1px solid #e0e7ff;
  border-radius: 12px;
  background: linear-gradient(180deg, #fafaff 0%, var(--qm-bg-2) 60%);
  box-shadow: 0 2px 12px rgba(249, 115, 22, 0.06);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 280px);
  /* 宽度约束：严格不超过父容器（case-management），子节点再宽也不会撑破面板 */
  width: 100%;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

/* 头部：标题 + 模型选择 popover + 收起按钮 */
.ai-inline-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 20px;
  background: var(--qm-bg-2);
  border-bottom: 1px solid #eef2f7;
  flex: 0 0 auto;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

.ai-inline-title {
  display: flex;
  align-items: center;
  gap: 10px;
  /* 标题侧：允许缩到最小，把横向空间让给右侧模型按钮（必要时自动换行） */
  min-width: 0;
  flex-shrink: 1;
  overflow: hidden;
}

.ai-inline-title .ai-header-title {
  font-size: 16px;
  font-weight: 700;
  color: #d97706;
  position: relative;
  padding-left: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ai-inline-title .ai-header-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: linear-gradient(180deg, #f97316 0%, #ea580c 100%);
  border-radius: 2px;
}

.ai-inline-title .ai-task-tag {
  border-radius: 6px;
  font-weight: 500;
  flex-shrink: 0;
}

.ai-inline-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  /* 右侧（模型名 + 收起按钮）：需要时自动折行到下一行，绝对不会撑破头部 */
  min-width: 0;
  flex-shrink: 0;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.ai-inline-header-right .ai-model-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #d97706;
  cursor: pointer;
  padding: 5px 12px;
  border-radius: 8px;
  background: var(--qm-accent-soft);
  transition: all 0.2s;
  user-select: none;
}

.ai-inline-header-right .ai-model-name:hover {
  background: #ede9fe;
  color: #5b21b6;
}

.ai-inline-header-right .ai-model-arrow {
  font-size: 12px;
  color: #f97316;
  transition: transform 0.2s;
}

.ai-inline-header-right .ai-model-arrow.open {
  transform: rotate(180deg);
}

.ai-inline-close {
  font-size: 13px;
  color: var(--qm-text-2);
}

.ai-inline-close:hover {
  color: var(--qm-text-2);
}

/* 模型选择 popover 列表（独立 popper-class，跨容器通用；注意：popover append-to-body，必须使用全局穿透 html body 前缀） */
html body .ai-model-popover .ai-model-list {
  max-height: 320px;
  overflow-y: auto;
  background: var(--qm-accent-soft);
  border-radius: 8px;
  padding: 4px;
}

html body .ai-model-popover .ai-model-list-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

html body .ai-model-popover .ai-model-list-item:hover {
  background: #ede9fe;
}

html body .ai-model-popover .ai-model-list-item.active {
  background: linear-gradient(135deg, #ddd6fe 0%, #c4b5fd 100%);
}

html body .ai-model-popover .ai-model-list-name {
  font-size: 14px;
  font-weight: 600;
  color: #d97706;
}

html body .ai-model-popover .ai-model-list-desc {
  font-size: 12px;
  color: #f97316;
}

html body .ai-model-popover .ai-model-check {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #d97706;
  font-size: 16px;
}

html body .ai-model-popover .ai-model-list-empty {
  text-align: center;
  color: #f97316;
  font-size: 13px;
  padding: 20px 0;
}

/* ========== AI 生成面板：场景复选框统一紫色系（与「生成」按钮渐变背景一致） ========== */
/* 全局前缀（不依赖 scoped :deep），因为 el-checkbox 是第三方组件，内部 __label/__inner 是 scoped 穿透不稳定的目标 */
html body .ai-inline-panel .ai-scenario-checkbox .el-checkbox__label {
  color: #d97706 !important;
  font-weight: 500 !important;
  font-size: 13.5px !important;
  line-height: 20px;
}

html body .ai-inline-panel .ai-scenario-checkbox:hover .el-checkbox__label {
  color: #5b21b6 !important;
}

html body .ai-inline-panel .ai-scenario-checkbox .el-checkbox__inner {
  border-color: #a78bfa !important;
  border-radius: 4px !important;
  transition: all 0.2s !important;
}

html body .ai-inline-panel .ai-scenario-checkbox:hover .el-checkbox__inner {
  border-color: #f97316 !important;
}

html body .ai-inline-panel .ai-scenario-checkbox .el-checkbox__input.is-checked .el-checkbox__inner {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
  border-color: transparent !important;
}

html body .ai-inline-panel .ai-scenario-checkbox .el-checkbox__input.is-checked + .el-checkbox__label {
  color: #5b21b6 !important;
  font-weight: 600 !important;
}

html body .ai-inline-panel .ai-scenario-checkbox .el-checkbox__input.is-indeterminate .el-checkbox__inner {
  background: linear-gradient(135deg, #a78bfa 0%, #f97316 100%) !important;
  border-color: transparent !important;
}

/* ========== AI 生成面板：请输入更多要求 textarea 固定高度 200px（三层全兜 + !important） ========== */
/* 外层（el-input 根） */
html body .ai-inline-panel .ai-extra-input.el-input,
html body .ai-inline-panel .ai-extra-input.el-textarea,
html body .ai-inline-panel .ai-extra-input {
  height: 200px !important;
  min-height: 200px !important;
  max-height: 500px;
  display: flex !important;
  flex-direction: column;
}

/* Inner textarea 盒子，实际显示文本的那个节点 */
html body .ai-inline-panel .ai-extra-input.el-textarea .el-textarea__inner,
html body .ai-inline-panel .ai-extra-input .el-textarea .el-textarea__inner,
html body .ai-inline-panel .ai-extra-input .el-textarea__inner {
  height: 200px !important;
  min-height: 200px !important;
  max-height: 480px !important;
  line-height: 1.6 !important;
  padding: 10px 12px !important;
  border-radius: 8px !important;
  resize: vertical;
}

/* 当 autosize 计算的高度超过 200 时，允许 textarea 更高（但有上限 480px） */
html body .ai-inline-panel .ai-extra-input.el-textarea[data-expand='true'] .el-textarea__inner,
html body .ai-inline-panel .ai-extra-input .el-textarea[data-expand='true'] .el-textarea__inner {
  height: auto !important;
  min-height: 200px !important;
}

html body .ai-inline-panel .ai-extra-input .el-input__count {
  color: #f97316;
  background: var(--qm-accent-soft);
}

/* ========== AI 生成面板：模块表单 label 颜色紫色系 ========== */
html body .ai-inline-panel .ai-module-form .el-form-item__label {
  color: #d97706 !important;
  font-weight: 600 !important;
  font-size: 13.5px !important;
}

/* ========== 内容区（唯一滚动容器） ========== */
.ai-inline-panel .ai-scroll-area {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 18px 20px 20px 20px;
  overflow-y: auto;
  overflow-x: hidden;
  /* 宽度约束：保证内容不会把父面板横向撑出屏幕 */
  width: 100%;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

/* 模块表单、场景分组卡片、补充需求：全部 max-width=100% 防止撑破滚动区 */
.ai-inline-panel .ai-module-form,
.ai-inline-panel .ai-block-title,
.ai-inline-panel .scenario-group,
.ai-inline-panel .ai-extra-input {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

.ai-inline-panel .ai-module-form :deep(.el-form-item) {
  align-items: center;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
  margin-bottom: 4px;
}

.ai-inline-panel .ai-module-form :deep(.el-form-item__content),
.ai-inline-panel .ai-module-form :deep(.el-cascader) {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
  align-items: center;
}

/* 模块表单：label 与 input 中线对齐（上面已补宽度约束，此处只保留对齐/行高） */
.ai-inline-panel .ai-module-form .el-form-item {
  margin-bottom: 4px;
}

/* Element Plus 默认 .el-form-item 使用 flex; label 顶部对齐
 * 此处强制居中对齐，label 与 input 盒子中线对齐。
 * label 行高与 input 默认 32px 高度基本一致，配合 form label-width 避免换行问题。 */
.ai-inline-panel .ai-module-form :deep(.el-form-item) {
  align-items: center;
}

.ai-inline-panel .ai-module-form :deep(.el-form-item__label) {
  line-height: 1;
  padding-top: 0;
  padding-bottom: 0;
}

.ai-inline-panel .ai-module-form :deep(.el-form-item__content) {
  line-height: 1;
  align-items: center;
}

/* 模型名胶囊按钮：限制最长 320px（防止长模型名撑破 header） */
.ai-inline-header-right .ai-model-name {
  max-width: 320px;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ai-inline-header-right .ai-model-name .ai-model-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
  flex-shrink: 1;
}

/* 底部按钮栏：限制宽度不超过父容器，按钮多时自动换行 */
.ai-inline-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  border-top: 1px solid #eef2f7;
  background: var(--qm-bg-2);
  flex: 0 0 auto;
  flex-wrap: wrap;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

/* 独立大标题：选择生成的用例类型 —— 紫色字体与生成按钮背景色保持一致 */
.ai-inline-panel .ai-block-title {
  margin: 2px 0 8px 0;
}

.ai-inline-panel .ai-block-title-text {
  display: inline-block;
  position: relative;
  font-size: 15px;
  font-weight: 700;
  color: #d97706;
  padding-left: 10px;
  line-height: 1.2;
}

.ai-inline-panel .ai-block-title-text::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 14px;
  background: linear-gradient(180deg, #f97316 0%, #ea580c 100%);
  border-radius: 2px;
}

.ai-inline-panel .scenario-group {
  border: 1px solid var(--qm-line-strong);
  border-radius: 10px;
  padding: 12px 16px 6px 16px;
  background: #fafbfc;
}

.ai-inline-panel .scenario-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

/* 有标题版（正向卡）/无标题版：废弃统一删除 */
.ai-inline-panel .scenario-group-header.scenario-group-header-with-title {
  display: none;
}
.ai-inline-panel .scenario-group-header.scenario-group-header-right {
  display: none;
}

.ai-inline-panel .scenario-group-title {
  font-weight: 700;
  font-size: 14px;
  color: #d97706;
  position: relative;
  padding-left: 10px;
  line-height: 1.2;
}

.ai-inline-panel .scenario-group-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 14px;
  background: linear-gradient(180deg, #f97316 0%, #ea580c 100%);
  border-radius: 2px;
}

/* 正向卡片大标题（已移到独立块，隐藏） */
.ai-inline-panel .scenario-group-title.scenario-group-title-main {
  display: none;
}

.ai-inline-panel .scenario-group-items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 20px;
}

/* 注：复选框颜色、textarea 高度已搬到全局样式（html body .ai-inline-panel .ai-scenario-checkbox ... / .ai-extra-input ...）
   因为 Element Plus 内部类名在 scoped :deep 下部分 Vue 编译版本穿透不稳定，统一用全局前缀保证命中 */

/* ========== 底部按钮（样式在前面定义，这里只写按钮本身的细节） ========== */

.ai-inline-footer .ai-submit-btn {
  min-width: 120px;
  height: 36px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-color: transparent;
  box-shadow: 0 4px 14px rgba(245, 158, 11, 0.25);
}

.ai-inline-footer .ai-submit-btn:hover,
.ai-inline-footer .ai-submit-btn:focus {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  border-color: transparent;
}
</style>
