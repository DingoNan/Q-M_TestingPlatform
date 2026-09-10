<template>
	<div class="system-setting-page">
		<!-- 页面头部 -->
		<div class="page-header">
			<div class="page-header-left">
				<div class="page-title-wrap">
					<h1 class="page-title">项目设置</h1>
					<p class="page-subtitle">统一管理当前项目的配置项</p>
				</div>
			</div>

			<div class="page-header-right">
				<el-button class="default-light-btn back-btn" @click="goBack">
					<el-icon><ArrowLeft /></el-icon>
					<span>返回</span>
				</el-button>
			</div>
		</div>

		<!-- 主体区域 -->
		<div class="system-setting-layout">
			<!-- 左侧tab导航 -->
			<div class="setting-sidebar">
				<div class="setting-sidebar-title">设置项</div>
				<div
							v-for="tab in dynamicSettingTabs"
							:key="tab.name"
							class="setting-tab-item"
							:class="{ active: activeTab === tab.name }"
							@click="switchTab(tab.name)"
						>
							<div class="setting-tab-label">{{ tab.label }}</div>
							<div class="setting-tab-desc">{{ tab.desc }}</div>
						</div>
			</div>

			<!-- 右侧内容 -->
			<div class="setting-content">
				<div class="setting-content-header">
					<div>
						<h3 class="setting-content-title">{{ currentTabConfig.label }}</h3>
						<p class="setting-content-subtitle">{{ currentTabConfig.desc }}</p>
					</div>
					<div class="setting-header-actions">
						<template v-if="activeTab === 'ai_config'">
							<el-button class="primary-gradient-btn" type="primary" @click="openAddAiProvider">
								添加AI供应商
							</el-button>
						</template>
						<el-button v-else-if="activeTab !== 'member_config'" class="primary-gradient-btn" type="primary" @click="saveCurrentTab">
							保存
						</el-button>
					</div>
				</div>

				<div class="setting-content-body">
					<!-- AI供应商 -->
					<template v-if="activeTab === 'ai_config'">
						<div class="ai-config-panel">
							<div class="ai-config-toolbar">
								<div class="ai-config-summary">
									共 <span>{{ aiConfigList.length }}</span> 个供应商配置
								</div>
							</div>

							<div class="ai-config-list" v-loading="aiConfigListLoading">
								<div
									v-for="(item, index) in aiConfigList"
									:key="item.id || `temp-${index}`"
									class="ai-config-card"
								>
									<div class="ai-config-card-left">
										<div class="ai-config-avatar-wrap">
											<img
												:src="getProviderAvatar(item.provider || item.provider_name)"
												:alt="item.provider_name || item.provider"
												class="ai-config-avatar"
											/>
										</div>
										<div class="ai-config-info">
											<div class="ai-config-provider">
												<span>{{ item.provider_name || item.provider }}</span>
												<el-tag v-if="item.is_default" class="default-tag" size="small" effect="light" round>默认</el-tag>
											</div>
											<div class="ai-config-model">{{ item.model_name }}</div>
											<div class="ai-config-url">{{ item.api_url }}</div>
										</div>
									</div>

									<div class="ai-config-card-right">
										<el-tooltip :content="item.is_default ? '当前为默认供应商' : '设为默认'" placement="top">
											<el-button
												class="icon-action-btn"
												:class="item.is_default ? 'default-star-btn-active' : 'default-star-btn'"
												circle
												:disabled="!!item.is_default"
												@click="setDefaultProvider(item)"
											>
												<el-icon><StarFilled /></el-icon>
											</el-button>
										</el-tooltip>

										<!-- 启用/禁用开关 -->
										<el-tooltip :content="item.is_active ? '点击禁用' : '点击启用'" placement="top">
											<el-switch
												v-model="item.is_active"
												:loading="item._switchLoading"
												@change="val => toggleActive(item, val)"
												inline-prompt
												active-text="启"
												inactive-text="禁"
												:active-color="'#f59e0b'"
												:inactive-color="'#a5b4cb'"
											/>
										</el-tooltip>

										<el-tooltip content="编辑" placement="top">
											<el-button class="icon-action-btn edit-icon-btn" circle @click="editAiProvider(item)">
												<el-icon><Edit /></el-icon>
											</el-button>
										</el-tooltip>

										<el-tooltip content="删除" placement="top">
											<el-button class="icon-action-btn delete-icon-btn" circle @click="deleteAiProvider(item)">
												<el-icon><Delete /></el-icon>
											</el-button>
										</el-tooltip>
									</div>
								</div>

								<el-empty
									v-if="!aiConfigListLoading && aiConfigList.length === 0"
									description="暂无AI供应商配置"
								/>
							</div>
						</div>
					</template>

					<!-- 其他tab占位 -->
					<template v-else-if="activeTab === 'general_config'">
						<div class="message-push-config">
							<div class="config-section">
								<div class="section-title">
									<el-icon><Notification /></el-icon>
									<span>消息推送渠道</span>
								</div>
								<div class="channel-list">
									<div
										v-for="channel in messageChannels"
										:key="channel.value"
										class="channel-item"
									>
										<div class="channel-info">
											<div class="channel-name">{{ channel.label }}</div>
											<div class="channel-desc">{{ channel.desc }}</div>
										</div>
										<el-switch
											v-model="channel.enabled"
											@change="handleChannelToggle(channel.value, $event)"
											:active-color="'#f59e0b'"
											:inactive-color="'var(--qm-line-strong)'"
										/>
									</div>
								</div>
							</div>

							<template v-if="messageChannels.find(c => c.value === 'dingtalk')?.enabled">
								<div class="config-section">
									<div class="section-title">
										<el-icon><Link /></el-icon>
										<span>钉钉配置</span>
									</div>
									<div class="form-row">
										<el-form-item label="Webhook URL">
											<el-input
												v-model="dingtalkConfig.webhook_url"
												placeholder="请输入钉钉Webhook URL"
												class="input"
												size="large"
											/>
										</el-form-item>
									</div>
									<div class="form-row">
										<el-form-item label="密钥">
											<el-input
												v-model="dingtalkConfig.secret"
												placeholder="请输入钉钉密钥（可选）"
												type="password"
												show-password
												class="form-input"
											/>
										</el-form-item>
									</div>
								</div>
							</template>

							<template v-if="messageChannels.find(c => c.value === 'feishu')?.enabled">
								<div class="config-section">
									<div class="section-title">
										<el-icon><Connection /></el-icon>
										<span>飞书配置</span>
									</div>
									<div class="form-row">
										<el-form-item label="Webhook URL">
											<el-input
												v-model="feishuConfig.webhook_url"
												placeholder="请输入飞书Webhook URL"
												class="input"
												size="large"
											/>
										</el-form-item>
									</div>
									<div class="form-row">
										<el-form-item label="密钥">
											<el-input
												v-model="feishuConfig.secret"
												placeholder="请输入飞书密钥（可选）"
												type="password"
												show-password
												class="input"
												size="large"
											/>
										</el-form-item>
									</div>
								</div>
							</template>

							<template v-if="messageChannels.find(c => c.value === 'email')?.enabled">
								<div class="config-section">
									<div class="section-title">
										<el-icon><Message /></el-icon>
										<span>邮箱配置</span>
									</div>
									<div class="form-row">
										<el-form-item label="SMTP服务器">
											<el-input
												v-model="emailConfig.smtp_host"
												placeholder="例如：smtp.gmail.com"
												class="input"
												size='larges'
											/>
										</el-form-item>
									</div>
									<div class="form-row">
										<el-form-item label="SMTP端口">
											<el-input
												v-model="emailConfig.smtp_port"
												placeholder="默认：587"
												class="input"
												size='large'
											/>
										</el-form-item>
									</div>
									<div class="form-row">
										<el-form-item label="发件人邮箱">
											<el-input
												v-model="emailConfig.from_email"
												placeholder="例如：sender@gmail.com"
												class="input"
												size='large'
											/>
										</el-form-item>
									</div>
									<div class="form-row">
										<el-form-item label="授权码">
											<el-input
												v-model="emailConfig.smtp_password"
												placeholder="请输入邮箱授权码"
												type="password"
												show-password
												class="input"
												size='large'
											/>
										</el-form-item>
									</div>
									<div class="form-row">
										<el-form-item label="收件人邮箱">
											<el-input
												v-model="emailConfig.to_emails"
												placeholder="多个邮箱用逗号分隔"
												class="input"
												size='large'
											/>
										</el-form-item>
									</div>
								</div>
							</template>

							<template v-if="messageChannels.find(c => c.value === 'message')?.enabled">
								<div class="config-section">
									<div class="section-title">
										<el-icon><Bell /></el-icon>
										<span>消息推送配置</span>
									</div>
									<div class="form-row">
										<el-form-item label="推送内容模板">
											<el-input
												v-model="messageConfig.template"
												type="textarea"
												placeholder="请输入消息推送模板"
												:rows="4"
												class="input"
												size='large'
											/>
										</el-form-item>
									</div>
									<div class="form-row">
										<el-form-item label="推送频率">
											<el-select
												v-model="messageConfig.frequency"
												placeholder="请选择推送频率"
												class="full-width-select"
											>
												<el-option label="实时推送" value="realtime" />
												<el-option label="每小时推送" value="hourly" />
												<el-option label="每天推送" value="daily" />
												<el-option label="每周推送" value="weekly" />
											</el-select>
										</el-form-item>
									</div>
									<div class="form-row">
										<el-form-item label="推送人群">
											<el-checkbox-group v-model="messageConfig.push_to">
												<el-checkbox label="admin" name="push_to">管理员</el-checkbox>
												<el-checkbox label="user" name="push_to">用户</el-checkbox>
												<el-checkbox label="guest" name="push_to">访客</el-checkbox>
											</el-checkbox-group>
										</el-form-item>
									</div>
								</div>
							</template>
						</div>
					</template>

					<!-- 通用设置 -->
					<template v-else-if="activeTab === 'common_config'">
						<div class="message-push-config">
							<div class="config-section">
								<div class="section-title">
									<el-icon><Timer /></el-icon>
									<span>回放文件清理</span>
								</div>
								<div class="form-row">
									<el-form-item label="保留天数">
										<el-input-number
											v-model="generalConfig.trace_retention_days"
											:min="1"
											:max="365"
											:step="1"
											step-strictly
											controls-position="right"
											class="retention-input"
										/>
										<span class="setting-hint">天</span>
									</el-form-item>
								</div>
								<div class="config-tip">
									执行用例产生的 Trace 回放文件、视频及用例执行日志（含 base64 截图），按其所属项目配置的保留天数由系统每天 03:30 自动删除（报告本身保留）；项目未配置时按默认 30 天清理，无法识别所属项目的文件按最长保留天数清理。取值范围 1~365 天。
								</div>
							</div>
						</div>
					</template>

					<!-- 成员管理配置 -->
					<template v-else-if="activeTab === 'member_config'">
						<div class="member-config-panel">
							<!-- 权限检查提示 -->
							<el-alert
								v-if="!isProjectCreator"
								:title="'权限不足'"
								:description="'只有项目创建者才能管理成员'"
								type="warning"
								show-icon
								class="permission-alert"
							/>

							<template v-if="isProjectCreator">
								<!-- 成员列表 -->
								<div class="config-section">
							<div class="section-title">
								<el-icon><User /></el-icon>
								<span>项目成员</span>
								<el-button class="primary-gradient-btn add-member-btn" type="primary" @click="openAddMember">
									<el-icon><Plus /></el-icon>
									添加成员
								</el-button>
							</div>
							<div class="member-list" v-loading="memberListLoading">
										<div
											v-for="member in memberList"
											:key="member.id"
											class="member-item"
										>
											<div class="member-info">
												<div class="member-avatar">
														<span class="avatar-text">{{ getAvatarText(member.user_name) }}</span>
													</div>
												<div class="member-details">
														<div class="member-name">{{ member.user_name }}</div>
														<div class="member-role">{{ member.role_name || getRoleLabel(member.role) }}</div>
														<div class="member-joined">{{ formatJoinTime(member.create_time) }}</div>
													</div>
											</div>
											<div class="member-actions">
												<el-tooltip content="编辑角色" placement="top">
													<el-button class="icon-action-btn edit-icon-btn" circle @click="editMemberRole(member)">
														<el-icon><Edit /></el-icon>
													</el-button>
												</el-tooltip>
												<el-tooltip content="移除成员" placement="top">
													<el-button class="icon-action-btn delete-icon-btn" circle @click="removeMember(member)">
														<el-icon><Delete /></el-icon>
													</el-button>
												</el-tooltip>
											</div>
										</div>

										<el-empty
											v-if="!memberListLoading && memberList.length === 0"
											description="暂无成员"
										/>
									</div>
								</div>
							</template>
						</div>
					</template>
				</div>
			</div>
		</div>

		<!-- 添加/编辑AI供应商 -->
		<!-- 编辑角色对话框 -->
		<el-dialog
			v-model="roleDialogVisible"
			title="编辑成员角色"
			width="400"
			append-to-body
			:show-close="true"
			class="role-dialog"
		>
			<el-form
				:model="roleForm"
				label-position="top"
				class="role-form"
			>
				<el-form-item label="选择角色">
					<el-select
						v-model="roleForm.role_id"
						placeholder="请选择角色"
						class="select"
						  size='large'
						  popper-class='select-dropdown-rounded'
						:loading="roleListLoading"
					>
						<el-option
							v-for="role in roleList"
							:key="role.id"
							:label="role.name || role.role_name"
							:value="role.id"
						/>
					</el-select>
				</el-form-item>
			</el-form>
			<template #footer>
				<div class="dialog-footer">
					<el-button class="default-light-btn" @click="roleDialogVisible = false">取消</el-button>
					<el-button class="primary-gradient-btn" type="primary" @click="saveMemberRole">保存</el-button>
				</div>
			</template>
		</el-dialog>

		<!-- 新增成员对话框 -->
		<el-dialog
			v-model="addMemberDialogVisible"
			title="添加成员"
			width="400"
			append-to-body
			:show-close="true"
			class="add-member-dialog"
		>
			<el-form
				:model="addMemberForm"
				:rules="addMemberRules"
				ref="addMemberFormRef"
				label-position="top"
				class="add-member-form"
			>
				<el-form-item label="用户" prop="user">
					<el-select
						v-model="addMemberForm.user"
						placeholder="请选择用户"
						class="select"
						  size='large'
						  popper-class='select-dropdown-rounded'
						filterable
						:loading="userListLoading"
					>
						<el-option
							v-for="user in userList"
							:key="user.id"
							:label="user.username || user.user_name"
							:value="user.id"
						/>
					</el-select>
				</el-form-item>
				<el-form-item label="角色" prop="role">
					<el-select
						v-model="addMemberForm.role"
						placeholder="请选择角色"
						class="select"
						  size='large'
						  popper-class='select-dropdown-rounded'
						:loading="roleListLoading"
					>
						<el-option
							v-for="role in roleList"
							:key="role.id"
							:label="role.name || role.role_name"
							:value="role.id"
						/>
					</el-select>
				</el-form-item>
			</el-form>
			<template #footer>
				<div class="dialog-footer">
					<el-button class="default-light-btn" @click="addMemberDialogVisible = false">取消</el-button>
					<el-button class="primary-gradient-btn" type="primary" @click="saveNewMember">保存</el-button>
				</div>
			</template>
		</el-dialog>

		<!-- 添加/编辑AI供应商 -->
		<el-dialog
			v-model="aiDialogVisible"
			:title="aiDialogMode === 'edit' ? '编辑AI供应商' : '添加AI供应商'"
			width="550"
			append-to-body
			:show-close="true"
			class="ai-provider-dialog"
		>
			<el-form
				:model="aiProviderForm"
				label-position="top"
				:rules="aiProviderRules"
				ref="aiProviderFormRef"
				class="ai-provider-form"
			>
				<el-form-item label="供应商" prop="provider">
					<div class="provider-list">
						<div
							v-for="item in providerOptions"
							:key="item.value"
							class="provider-card"
							:class="{ active: aiProviderForm.provider === item.value }"
							@click="selectAiProvider(item)"
						>
							<div class="provider-avatar-wrap">
								<img :src="item.avatar" :alt="item.label" class="provider-avatar" />
							</div>
							<div class="provider-name">{{ item.label }}</div>
						</div>
					</div>
				</el-form-item>

				<el-form-item label="API Key" prop="api_key">
					<el-input
						v-model="aiProviderForm.api_key"
						autocomplete="off"
						placeholder="请输入 API Key"
						type="password"
						show-password
						class="input"
						size='large'
					/>
				</el-form-item>

				<el-form-item label="API URL" prop="api_url">
					<el-input
						v-model="aiProviderForm.api_url"
						autocomplete="off"
						placeholder="请输入 API URL"
						class="input"
						size="large"
					/>
				</el-form-item>

				<el-form-item label="模型名称" prop="model_name">
					<el-select
						v-model="aiProviderForm.model_name"
						placeholder="请选择或直接输入模型名称"
						class="select"
						size='large'
						popper-class='select-dropdown-rounded'
						filterable
						allow-create
						default-first-option
						:reserve-keyword="false"
						clearable
					>
						<el-option
							v-for="model in currentModelOptions"
							:key="model"
							:label="model"
							:value="model"
						/>
					</el-select>
					<div v-if="isCustomModel" class="form-tip">
						当前为自定义模型，请确认该模型 ID 在所选供应商处可用
					</div>
				</el-form-item>
			</el-form>

			<template #footer>
				<div class="dialog-footer">
					<div class="dialog-footer-left">
						<el-button class="default-light-btn" @click="testAiConnection">
							测试连接
						</el-button>
					</div>
					<div class="dialog-footer-right">
						<el-button class="default-light-btn" @click="aiDialogVisible = false">取消</el-button>
						<el-button class="primary-gradient-btn" type="primary" @click="saveAiProvider">
							保存
						</el-button>
					</div>
				</div>
			</template>
		</el-dialog>
	</div>
</template>

<script>
import { mapState } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, Delete, Notification, Link, Connection, Message, Bell, User, UserFilled, Plus, Timer, StarFilled } from '@element-plus/icons-vue'
import api from '@/api/index.js'

export default {
	name: 'SystemSetting',
	components: {
		ArrowLeft,
		Edit,
		Delete,
		Notification,
		Link,
		Connection,
		Message,
		Bell,
		User,
		UserFilled,
		Plus,
		Timer,
		StarFilled
	},
	data() {
		const validateAiProvider = (rule, value, callback) => {
			if (!value) {
				callback(new Error('请选择供应商'))
			} else {
				callback()
			}
		}

		return {
			activeTab: 'ai_config',
			settingTabs: [
				{
					name: 'ai_config',
					label: 'AI供应商',
					desc: '管理项目使用的AI供应商配置'
				},
				{
					name: 'general_config',
					label: '消息设置',
					desc: '消息推送配置'
				}
			],

			providerOptions: [
				{
					label: 'DeepSeek',
					value: 'DeepSeek',
					avatar: 'https://cdn.apifox.com/app/llm-provider-icon/builtin/deepseek.png',
					api_url: 'https://api.deepseek.com',
					// 官方最新模型（deepseek-chat / deepseek-reasoner 已于 2026-07-24 下线）
					models: [
						'deepseek-v4-pro',
						'deepseek-v4-flash',
						'deepseek-flash',
						'deepseek-v4-flash-vision-exp'
					]
				},
				{
					label: '腾讯混元',
					value: '腾讯混元',
					avatar: 'https://cdn.apifox.com/app/llm-provider-icon/builtin/hunyuan.png',
					api_url: 'https://api.hunyuan.cloud.tencent.com/v1',
					models: ['hunyuan-turbo', 'hunyuan-standard']
				},
				{
					label: '腾讯云',
					value: '腾讯云',
					avatar: 'https://cdn.apifox.com/app/llm-provider-icon/builtin/tencent-cloud.png',
					api_url: 'https://api.lkeap.cloud.tencent.com/v1',
					models: ['hunyuan-turbo', 'hunyuan-standard']
				},
				{
					label: '阿里云百炼',
					value: '阿里云百炼',
					avatar: 'https://cdn.apifox.com/app/llm-provider-icon/builtin/aliyun.png',
					api_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
					models: ['qwen-turbo', 'qwen-plus', 'qwen-max']
				},
				{
					label: '智谱',
					value: '智谱',
					avatar: 'https://cdn.apifox.com/app/llm-provider-icon/builtin/bigmodel.png',
					api_url: 'https://open.bigmodel.cn/api/paas/v4',
					models: ['glm-4', 'glm-4-plus', 'glm-4v']
				},
				{
					label: '火山引擎',
					value: '火山引擎',
					avatar: 'https://cdn.apifox.com/app/llm-provider-icon/builtin/volcengine.png',
					api_url: 'https://ark.cn-beijing.volces.com/api/v3',
					models: ['doubao-pro-32k', 'doubao-lite-32k']
				},
				{
					label: 'MiniMax',
					value: 'MiniMax',
					avatar: 'https://cdn.apifox.com/app/llm-provider-icon/builtin/minimax.png',
					api_url: 'https://api.minimaxi.com',
					models: ['abab6-chat', 'abab5.5-chat']
				},
				{
					label: '月之暗面',
					value: '月之暗面',
					avatar: 'https://cdn.apifox.com/app/llm-provider-icon/builtin/moonshot.png',
					api_url: 'https://api.moonshot.cn/v1',
					models: ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k']
				},
				{
					label: '硅基流动',
					value: '硅基流动',
					avatar: 'https://cdn.apifox.com/app/llm-provider-icon/builtin/siliconflow.png',
					api_url: 'https://api.siliconflow.cn/v1',
					// 模型广场持续上新，以下为常用清单；下拉支持直接输入任意 model id
					models: [
						'deepseek-ai/DeepSeek-V3.2',
						'deepseek-ai/DeepSeek-V4-Pro',
						'deepseek-ai/DeepSeek-V4-Flash',
						'deepseek-ai/DeepSeek-R1',
						'deepseek-ai/DeepSeek-V3',
						'Qwen/Qwen3-8B',
						'Qwen/Qwen2.5-7B-Instruct',
						'Qwen/Qwen2.5-72B-Instruct',
						'zai-org/GLM-5.2',
						'moonshotai/Kimi-K2.7-Code',
						'MiniMaxAI/MiniMax-M3',
						'THUDM/glm-4-9b-chat'
					]
				},
				{
					label: '自定义',
					value: '自定义',
					avatar: 'https://cdn.apifox.com/app/llm-provider-icon/builtin/openai.png',
					api_url: '',
					models: []
				}
			],

			aiConfigList: [],
			aiConfigListLoading: false,
			aiDialogVisible: false,
			aiDialogMode: 'add',
			currentEditId: '',

			aiProviderForm: {
				id: '',
				provider: '',
				provider_name: '',
				api_key: '',
				api_url: '',
				model_name: '',
				is_default: false
			},

			aiProviderRules: {
				provider: [
					{ required: true, validator: validateAiProvider, trigger: 'change' }
				],
				api_key: [
					{ required: true, message: '请输入API Key', trigger: 'blur' }
				],
				api_url: [
					{ required: true, message: '请输入API URL', trigger: 'blur' }
				],
				model_name: [
					{ required: true, message: '请选择模型名称', trigger: 'change' }
				]
			},

			messageChannels: [
				{
					value: 'dingtalk',
					label: '钉钉',
					desc: '钉钉机器人推送',
					enabled: false
				},
				{
					value: 'feishu',
					label: '飞书',
					desc: '飞书机器人推送',
					enabled: false
				},
				{
					value: 'email',
					label: '邮箱',
					desc: '邮箱SMTP推送',
					enabled: false
				},
				{
					value: 'message',
					label: '消息推送',
					desc: '系统消息推送',
					enabled: false
				}
			],

			dingtalkConfig: {
				webhook_url: '',
				secret: '',
				at_users: '',
				at_all: false
			},

			feishuConfig: {
				webhook_url: '',
				secret: '',
				at_all: false
			},

			emailConfig: {
				smtp_host: '',
				smtp_port: '587',
				from_email: '',
				smtp_password: '',
				to_emails: ''
			},

			messageConfig: {
				template: '',
				frequency: 'realtime',
				push_to: []
			},

			// 通用设置
			generalConfig: {
				id: null,
				trace_retention_days: 30
			},

			// 成员管理配置
			memberConfig: {
				invite_setting: 'creator_only',
				role_management: 'creator_only',
				member_deletion: 'creator_only',
				default_role: 'member',
				require_approval: false,
				approvers: ['creator'],
				activity_reminder: false,
				inactive_days: 30
			},

			// 成员列表
			memberList: [],
			memberListLoading: false,

			// 编辑角色对话框
		roleDialogVisible: false,
		selectedMember: null,
		roleForm: {
			role_id: ''
		},

		// 新增成员对话框
		addMemberDialogVisible: false,
		addMemberForm: {
			user: null,
			role: null
		},
		addMemberRules: {
			user: [
				{ required: true, message: '请选择用户', trigger: ['change', 'blur'] }
			],
			role: [
				{ required: true, message: '请选择角色', trigger: ['change', 'blur'] }
			]
		},
		// 用户列表
		userList: [],
		userListLoading: false,
		// 角色列表
		roleList: [],
		roleListLoading: false
		}
	},
	computed: {
		...mapState(['role_id', 'pathPermission', 'userInfo', 'projectInfo']),
		projectId() {
			return this.projectInfo?.id || ''
		},
		currentTabConfig() {
			return this.dynamicSettingTabs.find(tab => tab.name === this.activeTab) || this.dynamicSettingTabs[0]
		},
		currentModelOptions() {
			const provider = this.providerOptions.find(item => item.value === this.aiProviderForm.provider)
			const list = provider ? [...(provider.models || [])] : []
			// 已保存的自定义模型不在预置清单时也要能正常回显
			const current = (this.aiProviderForm.model_name || '').trim()
			if (current && !list.includes(current)) {
				list.unshift(current)
			}
			return list
		},
		// 是否为预置清单外的自定义模型
		isCustomModel() {
			const provider = this.providerOptions.find(item => item.value === this.aiProviderForm.provider)
			const current = (this.aiProviderForm.model_name || '').trim()
			if (!current) return false
			return !(provider?.models || []).includes(current)
		},

		// 判断当前用户是否为项目创建者
		isProjectCreator() {
			return this.projectInfo.create_by === this.userInfo.user_id || this.userInfo.is_superuser
		},

		// 动态生成设置标签页
		dynamicSettingTabs() {
			const tabs = [
				{
					name: 'ai_config',
					label: 'AI供应商',
					desc: '管理项目使用的AI供应商配置'
				},
				{
					name: 'general_config',
					label: '消息设置',
					desc: '消息推送配置'
				},
				{
					name: 'common_config',
					label: '通用设置',
					desc: '回放文件清理等通用配置'
				}
			]
			
			// 只有项目创建者才显示成员管理标签
			if (this.isProjectCreator) {
				tabs.push({
					name: 'member_config',
					label: '成员管理',
					desc: '管理项目成员权限配置'
				})
			}
			
			return tabs
		}
	},
	watch: {
		projectId: {
			immediate: true,
			handler(newVal) {
				if (newVal) {
					this.loadCurrentTabData()
				} else {
					this.aiConfigList = []
					// 重置消息推送配置
					if (this.activeTab === 'general_config') {
						this.resetMessagePushConfigs()
					}
				}
			}
		}
	},
	methods: {
		goBack() {
			this.$router.back()
		},

		switchTab(tabName) {
			this.activeTab = tabName
			this.loadCurrentTabData()
		},

		loadCurrentTabData() {
			if (this.activeTab === 'ai_config') {
				this.getAiConfigs()
			} else if (this.activeTab === 'general_config') {
				this.getMessagePushConfigs()
			} else if (this.activeTab === 'common_config') {
				this.getGeneralSetting()
			} else if (this.activeTab === 'member_config') {
				this.getMemberList()
			}
		},

		saveCurrentTab() {
			if (this.activeTab === 'general_config') {
				this.saveMessagePushConfigs()
			} else if (this.activeTab === 'common_config') {
				this.saveGeneralSetting()
			} else if (this.activeTab === 'member_config') {
				ElMessage.success('保存成功')
			} else {
				ElMessage.success('保存成功')
			}
		},

		handleChannelToggle(channelValue, isEnabled) {
			if (isEnabled) {
				ElMessage.info(`${this.getMessageChannelLabel(channelValue)}已启用`)
			} else {
				ElMessage.info(`${this.getMessageChannelLabel(channelValue)}已禁用`)
			}
		},

		getMessageChannelLabel(value) {
			const channel = this.messageChannels.find(c => c.value === value)
			return channel ? channel.label : ''
		},

		resetMessagePushConfigs() {
			// 重置各渠道配置
			this.dingtalkConfig = {
				webhook_url: '',
				secret: '',
				at_users: '',
				at_all: false
			}
			this.feishuConfig = {
				webhook_url: '',
				secret: '',
				at_all: false
			}
			this.emailConfig = {
				smtp_host: '',
				smtp_port: '587',
				from_email: '',
				smtp_password: '',
				to_emails: ''
			}
			this.messageConfig = {
				template: '',
				frequency: 'realtime',
				push_to: []
			}
			// 重置渠道启用状态
			this.messageChannels = this.messageChannels.map(channel => ({
				...channel,
				enabled: false
			}))
		},

		getProviderAvatar(provider) {
			const target = this.providerOptions.find(
				item => item.value === provider || item.label === provider
			)
			return target ? target.avatar : 'https://cdn.apifox.com/app/llm-provider-icon/builtin/openai.png'
		},

		resetAiProviderForm() {
			this.currentEditId = ''
			this.aiProviderForm = {
				id: '',
				provider: '',
				provider_name: '',
				api_key: '',
				api_url: '',
				model_name: ''
			}
		},

		selectAiProvider(item) {
			this.aiProviderForm.provider = item.value
			this.aiProviderForm.provider_name = item.label
			// 自定义供应商无预置 URL，保留用户已填写的内容
			this.aiProviderForm.api_url = item.api_url || this.aiProviderForm.api_url || ''
			// 自定义供应商（预置清单为空）不覆盖用户已填/自定义的模型名
			if (item.models && item.models.length > 0 && !item.models.includes(this.aiProviderForm.model_name)) {
				this.aiProviderForm.model_name = item.models[0] || ''
			}
		},

		openAddAiProvider() {
			this.aiDialogMode = 'add'
			this.resetAiProviderForm()
			this.aiDialogVisible = true
			this.$nextTick(() => {
				this.$refs.aiProviderFormRef?.clearValidate()
			})
		},

		async editAiProvider(row) {
			try {
				this.aiDialogMode = 'edit'
				this.currentEditId = row.id
				this.aiDialogVisible = true

				let detail = row
				if (row.id && this.$api.getAiConfig) {
					const response = await this.$api.getAiConfig(row.id)
					if (response.status === 200) {
						detail = response.data?.result || response.data?.data || row
					}
				}

				this.aiProviderForm = {
					id: detail.id || '',
					provider: detail.provider || detail.provider_name || '',
					provider_name: detail.provider_name || detail.provider || '',
					api_key: detail.api_key || '',
					api_url: detail.api_url || '',
					model_name: detail.model_name || ''
				}

				const matchedOption = this.providerOptions.find(
					opt => opt.value === this.aiProviderForm.provider || opt.label === this.aiProviderForm.provider_name
				)
				if (matchedOption) {
					this.aiProviderForm.provider = matchedOption.value
					this.aiProviderForm.provider_name = matchedOption.label
					if (!this.aiProviderForm.api_url && matchedOption.api_url) {
						this.aiProviderForm.api_url = matchedOption.api_url
					}
				}

				this.$nextTick(() => {
					this.$refs.aiProviderFormRef?.clearValidate()
				})
			} catch (error) {
				console.error('获取AI供应商详情失败:', error)
				ElMessage.error('获取详情失败')
				this.aiDialogVisible = false
			}
		},

		async deleteAiProvider(row) {
			try {
				await ElMessageBox.confirm(
					`确定删除供应商“${row.provider_name || row.provider}”吗？`,
					'删除确认',
					{
						confirmButtonText: '确定',
						cancelButtonText: '取消',
						type: 'warning'
					}
				)

				const response = await this.$api.deleteAiConfig(row.id)
				if (response.status === 204) {
					ElMessage.success('删除成功')
					this.getAiConfigs()
				}
			} catch (error) {
				if (error !== 'cancel' && error !== 'close') {
					console.error('删除AI供应商失败:', error)
					ElMessage.error('删除失败')
				}
			}
		},

		async getAiConfigs() {
			if (!this.projectId) {
				this.aiConfigList = []
				return
			}

			this.aiConfigListLoading = true
			try {
				const response = await this.$api.getAiConfigs({
					project: this.projectId
				})
				if (response.status === 200) {
					const result =
						response.data?.result ||
						response.data?.data ||
						response.data?.results ||
						[]
					this.aiConfigList = (Array.isArray(result) ? result : []).map(item => ({
						...item,
						_switchLoading: false
					}))
				}
			} catch (error) {
				console.error('获取AI供应商列表失败:', error)
				this.aiConfigList = []
				ElMessage.error('获取列表失败')
			} finally {
				this.aiConfigListLoading = false
			}
		},

		// 切换启用/禁用状态（全量更新）
		async toggleActive(item, newVal) {
			item._switchLoading = true
			const originalVal = !newVal

			try {
				// 构造完整的更新数据（剔除前端临时属性）
				const updateData = {
					project: this.projectInfo.id,
					provider: item.provider,
					provider_name: item.provider_name,
					api_key: item.api_key,
					api_url: item.api_url,
					model_name: item.model_name,
					is_active: newVal,
					is_default: !!item.is_default
				}
				// 注意：如果 api_key 是脱敏值（如 "********"），后端需要特殊处理（例如忽略该字段或保持原值）
				// 这里按用户要求传递所有字段
				const response = await this.$api.updateAiConfig(item.id, updateData)

				const isSuccess = (response.status >= 200 && response.status < 300) || response.data?.code === 200
				if (isSuccess) {
					ElMessage.success(`已${newVal ? '启用' : '禁用'}`)
					await this.getAiConfigs() // 刷新列表
				} else {
					item.is_active = originalVal
					ElMessage.error(response.data?.msg || '操作失败')
				}
			} catch (error) {
				console.error('更新状态失败:', error)
				item.is_active = originalVal
				ElMessage.error(error.response?.data?.msg || '操作失败')
			} finally {
				item._switchLoading = false
			}
		},

		async testAiConnection() {
			try {
				await this.$refs.aiProviderFormRef.validateField('provider')
				await this.$refs.aiProviderFormRef.validateField('api_key')
				await this.$refs.aiProviderFormRef.validateField('api_url')
				await this.$refs.aiProviderFormRef.validateField('model_name')

				const params = {
					project: this.projectId,
					provider: this.aiProviderForm.provider,
					provider_name: this.aiProviderForm.provider_name || this.aiProviderForm.provider,
					api_key: this.aiProviderForm.api_key,
					api_url: this.aiProviderForm.api_url,
					model_name: this.aiProviderForm.model_name
				}

				if (this.$api.testAiConfig) {
					const response = await this.$api.testAiConfig(params)
					if (response.status === 200) {
						ElMessage.success('测试连接成功')
					} else {
						ElMessage.error('测试连接失败')
					}
				} else {
					ElMessage.success('测试连接成功（模拟）')
				}
			} catch (error) {
				if (error?.message) {
					return
				}
				console.error('测试连接失败:', error)
				ElMessage.error('测试连接失败')
			}
		},

		async saveAiProvider() {
			try {
				await this.$refs.aiProviderFormRef.validate()

				const params = {
					project: this.projectId,
					provider: this.aiProviderForm.provider,
					provider_name: this.aiProviderForm.provider_name || this.aiProviderForm.provider,
					api_key: this.aiProviderForm.api_key,
					api_url: this.aiProviderForm.api_url,
					model_name: this.aiProviderForm.model_name
				}

				let response
				if (this.aiDialogMode === 'edit') {
					response = await this.$api.updateAiConfig(this.aiProviderForm.id || this.currentEditId, params)
				} else {
					response = await this.$api.createAiConfig(params)
				}

				const isSuccess = (response.status >= 200 && response.status < 300) || response.data?.code === 200
				if (isSuccess) {
					ElMessage.success(this.aiDialogMode === 'edit' ? '修改成功' : '添加成功')
					this.aiDialogVisible = false
					await this.getAiConfigs()
				} else {
					const errorMsg = response.data?.msg || response.data?.message || '操作失败'
					ElMessage.error(errorMsg)
				}
			} catch (error) {
				if (error?.errors) return
				console.error('保存AI供应商失败:', error)
				const errorMsg = error.response?.data?.msg || error.response?.data?.message || '保存失败'
				ElMessage.error(errorMsg)
			}
		},

		// 设为默认AI供应商
		async setDefaultProvider(item) {
			try {
				const response = await this.$api.setDefaultAiConfig(item.id)
				const isSuccess = (response.status >= 200 && response.status < 300) || response.data?.code === 200
				if (isSuccess) {
					ElMessage.success('已设为默认')
					this.getAiConfigs()
				} else {
					ElMessage.error(response.data?.msg || '设置失败')
				}
			} catch (error) {
				console.error('设置默认供应商失败:', error)
				ElMessage.error(error.response?.data?.msg || '设置失败')
			}
		},

		// 消息推送配置相关方法
		async getMessagePushConfigs() {
			if (!this.projectId) {
				return
			}

			try {
				const response = await api.getProjectMsgPush({
					project: this.projectId
				})
				if (response.status === 200) {
					const result = response.data?.result || response.data?.data || response.data?.results || []
					const configs = Array.isArray(result) ? result : []
					
					// 定义渠道值映射
					const channelValueMap = {
						'dingtalk': 2,
						'feishu': 1,
						'email': 3,
						'message': 4
					}
					
					// 更新渠道启用状态和ID
					this.messageChannels = this.messageChannels.map(channel => {
						const pushType = channelValueMap[channel.value]
						const config = configs.find(c => c.push_type === pushType)
						return {
							...channel,
							enabled: !!config && (config.is_active !== false),
							id: config?.id || null
						}
					})
					
					// 更新配置数据 - 总是回显配置数据
					const dingtalkConfig = configs.find(c => c.push_type === 2)
					if (dingtalkConfig) {
						this.dingtalkConfig = {
							webhook_url: dingtalkConfig.webhook_url || '',
							secret: dingtalkConfig.email_password || '',
							id: dingtalkConfig.id || null
						}
					}
					
					const feishuConfig = configs.find(c => c.push_type === 1)
					if (feishuConfig) {
						this.feishuConfig = {
							webhook_url: feishuConfig.webhook_url || '',
							secret: feishuConfig.email_password || '',
							id: feishuConfig.id || null
						}
					}
					
					const emailConfig = configs.find(c => c.push_type === 3)
					if (emailConfig) {
						this.emailConfig = {
							smtp_host: emailConfig.email_host || '',
							smtp_port: emailConfig.email_port || '587',
							from_email: emailConfig.email_user || '',
							smtp_password: emailConfig.email_password || '',
							to_emails: emailConfig.email_to || '',
							id: emailConfig.id || null
						}
					}
				}
			} catch (error) {
				console.error('获取消息推送配置失败:', error)
			}
		},

		async saveMessagePushConfigs() {
			if (!this.projectId) {
				ElMessage.error('项目ID不存在')
				return
			}

			try {
				// 校验钉钉配置
				if (this.messageChannels.find(c => c.value === 'dingtalk')?.enabled) {
					if (!this.dingtalkConfig.webhook_url) {
						ElMessage.warning('钉钉Webhook URL不能为空')
						return
					}
				}

				// 校验飞书配置
				if (this.messageChannels.find(c => c.value === 'feishu')?.enabled) {
					if (!this.feishuConfig.webhook_url) {
						ElMessage.warning('飞书Webhook URL不能为空')
						return
					}
				}

				// 校验邮箱配置
				if (this.messageChannels.find(c => c.value === 'email')?.enabled) {
					if (!this.emailConfig.smtp_host) {
						ElMessage.warning('邮箱SMTP服务器不能为空')
						return
					}
					if (!this.emailConfig.from_email) {
						ElMessage.warning('邮箱账号不能为空')
						return
					}
					if (!this.emailConfig.to_emails) {
						ElMessage.warning('收件人邮箱不能为空')
						return
					}
					if (!this.emailConfig.smtp_port) {
						ElMessage.warning('邮箱SMTP端口不能为空')
						return
					}
				}

				// 保存钉钉配置
				const dingtalkEnabled = this.messageChannels.find(c => c.value === 'dingtalk')?.enabled
				const params = {
					project: this.projectId,
					push_type: 2,
					webhook_url: this.dingtalkConfig.webhook_url,
					email_password: this.dingtalkConfig.secret,
					is_active: dingtalkEnabled
				}
				
				if (this.dingtalkConfig.id) {
					await api.updateProjectMsgPush(this.dingtalkConfig.id, params)
				} else {
					await api.createProjectMsgPush(params)
				}

				// 保存飞书配置
				const feishuEnabled = this.messageChannels.find(c => c.value === 'feishu')?.enabled
				const params2 = {
					project: this.projectId,
					push_type: 1,
					webhook_url: this.feishuConfig.webhook_url,
					email_password: this.feishuConfig.secret,
					is_active: feishuEnabled
				}
				
				if (this.feishuConfig.id) {
					await api.updateProjectMsgPush(this.feishuConfig.id, params2)
				} else {
					await api.createProjectMsgPush(params2)
				}

				// 保存邮箱配置
				const emailEnabled = this.messageChannels.find(c => c.value === 'email')?.enabled
				const params3 = {
					project: this.projectId,
					push_type: 3,
					email_host: this.emailConfig.smtp_host,
					email_user: this.emailConfig.from_email,
					email_password: this.emailConfig.smtp_password,
					email_to: this.emailConfig.to_emails,
					is_active: emailEnabled
				}
				
				if (this.emailConfig.smtp_port) {
					params3.email_port = this.emailConfig.smtp_port
				}
				
				if (this.emailConfig.id) {
					await api.updateProjectMsgPush(this.emailConfig.id, params3)
				} else {
					await api.createProjectMsgPush(params3)
				}

				ElMessage.success('消息推送配置保存成功')
			} catch (error) {
				console.error('保存消息推送配置失败:', error)
				ElMessage.error('保存失败')
			}
		},

		// 通用设置相关方法
		async getGeneralSetting() {
			if (!this.projectId) {
				return
			}

			try {
				const response = await api.getProjectGeneralSetting({
					project: this.projectId
				})
				if (response.status === 200) {
					const result = response.data?.result || response.data?.data || response.data?.results || []
					const configs = Array.isArray(result) ? result : (result ? [result] : [])
					const config = configs[0]
					if (config) {
						this.generalConfig = {
							id: config.id,
							trace_retention_days: config.trace_retention_days || 30
						}
					} else {
						this.generalConfig = { id: null, trace_retention_days: 30 }
					}
				}
			} catch (error) {
				console.error('获取通用设置失败:', error)
			}
		},

		async saveGeneralSetting() {
			if (!this.projectId) {
				ElMessage.error('项目ID不存在')
				return
			}

			const days = Number(this.generalConfig.trace_retention_days)
			if (!days || days < 1 || days > 365) {
				ElMessage.warning('保留天数需在 1~365 之间')
				return
			}

			try {
				const params = {
					project: this.projectId,
					trace_retention_days: days
				}
				if (this.generalConfig.id) {
					await api.updateProjectGeneralSetting(this.generalConfig.id, params)
				} else {
					await api.createProjectGeneralSetting(params)
				}
				ElMessage.success('通用设置保存成功')
				this.getGeneralSetting()
			} catch (error) {
				console.error('保存通用设置失败:', error)
				ElMessage.error(error.response?.data?.msg || '保存失败')
			}
		},

		// 成员管理相关方法
		async getMemberList() {
			if (!this.projectId) {
				this.memberList = []
				return
			}

			this.memberListLoading = true
			try {
				// 调用API获取成员列表
				const response = await this.$api.getProjectMembers({
					project: this.projectId
				})
				if (response.status === 200) {
					const result = response.data?.result || response.data?.data || response.data?.results || []
					this.memberList = Array.isArray(result) ? result : []
				} else {
					this.memberList = []
					ElMessage.error('获取成员列表失败')
				}
			} catch (error) {
				console.error('获取成员列表失败:', error)
				this.memberList = []
				ElMessage.error('获取成员列表失败')
			} finally {
				this.memberListLoading = false
			}
		},

		getAvatarText(user_name) {
			return user_name ? user_name.charAt(0).toUpperCase() : '?'
		},

		getRoleLabel(role) {
			const roleMap = {
				creator: '创建者',
				admin: '管理员',
				member: '普通成员',
				guest: '访客'
			}
			return roleMap[role] || role
		},

		formatJoinTime(time) {
			if (!time) return ''
			const date = new Date(time)
			return date.toLocaleString()
		},

		async editMemberRole(member) {
			this.selectedMember = member
			this.roleForm.role_id = member.role
			// 加载角色列表
			await this.getRoleList()
			this.roleDialogVisible = true
		},

		async removeMember(member) {
			try {
				await ElMessageBox.confirm(
					`确定移除成员“${member.user_name}”吗？`,
					'移除确认',
					{
						confirmButtonText: '确定',
						cancelButtonText: '取消',
						type: 'warning'
					}
				)

				// 调用API移除成员
				const response = await this.$api.deleteProjectMember(member.id)
				if (response.status === 204 || response.status === 200) {
					this.memberList = this.memberList.filter(m => m.id !== member.id)
					ElMessage.success('成员移除成功')
				} else {
					ElMessage.error('移除失败')
				}
			} catch (error) {
				if (error !== 'cancel' && error !== 'close') {
					console.error('移除成员失败:', error)
					ElMessage.error('移除失败')
				}
			}
		},

		async saveMemberRole() {
			if (!this.selectedMember) {
				ElMessage.error('请选择要编辑的成员')
				return
			}

			try {
				// 调用API更新成员角色
				const response = await this.$api.updateProjectMember(this.selectedMember.id, {
					project: this.selectedMember.project,
					user: this.selectedMember.user,
					role: this.roleForm.role_id
				})
				if (response.status === 200) {
					const memberIndex = this.memberList.findIndex(m => m.id === this.selectedMember.id)
					if (memberIndex !== -1) {
						this.memberList[memberIndex].role = this.roleForm.role_id
					}
					this.roleDialogVisible = false
					this.getMemberList()
					ElMessage.success('角色更新成功')
				} else {
					ElMessage.error('更新失败')
				}
			} catch (error) {
				console.error('更新角色失败:', error)
				ElMessage.error('更新失败')
			}
		},

		// 获取用户列表
		async getUserList() {
			this.userListLoading = true
			try {
				const response = await this.$api.getUsers()
				if (response.status === 200) {
					const result = response.data?.result || response.data?.data || response.data?.results || []
					// 排除已经是项目成员的用户
					const memberUserIds = this.memberList.map(m => m.user)
					this.userList = Array.isArray(result) ? result.filter(user => !memberUserIds.includes(user.id)) : []
				}
			} catch (error) {
				console.error('获取用户列表失败:', error)
				this.userList = []
			} finally {
				this.userListLoading = false
			}
		},

		// 获取角色列表
		async getRoleList() {
			this.roleListLoading = true
			try {
				const response = await this.$api.getRoles()
				if (response.status === 200) {
					const result = response.data?.result || response.data?.data || response.data?.results || []
					this.roleList = Array.isArray(result) ? result : []
				}
			} catch (error) {
				console.error('获取角色列表失败:', error)
				this.roleList = []
			} finally {
				this.roleListLoading = false
			}
		},

		// 打开新增成员对话框
		async openAddMember() {
			this.addMemberForm = {
				user: null,
				role: null
			}
			// 加载用户列表和角色列表
			await Promise.all([
				this.getUserList(),
				this.getRoleList()
			])
			this.addMemberDialogVisible = true
			this.$nextTick(() => {
				this.$refs.addMemberFormRef?.clearValidate()
			})
		},

		// 保存新成员
		async saveNewMember() {
			try {
				// 使用Element Plus的表单验证
				await this.$refs.addMemberFormRef.validate()

				// 调用API创建新成员
				const response = await this.$api.createProjectMember({
					project: this.projectId,
					user: this.addMemberForm.user,
					role: this.addMemberForm.role
				})
				if (response.status === 201 || response.status === 200) {
					const newMember = response.data?.result || response.data?.data || {}
					this.memberList.push(newMember)
					this.addMemberDialogVisible = false
					ElMessage.success('成员添加成功')
				} else {
					ElMessage.error('添加失败')
				}
			} catch (error) {
				// 表单验证失败时，Element Plus会自动显示错误提示
				// 只有当error不是表单验证错误时，才显示添加失败提示
				console.log(error)
				// 检查error是否是表单验证错误（包含user或role字段）
				if (!error || (!error.user && !error.role)) {
					ElMessage.error('添加失败')
				}
			}
		}
	}
}
</script>

<style scoped>
/* ===== 全局重置 ===== */
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
}

/* 模型名称自定义提示 */
.form-tip {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.5;
  color: var(--el-color-warning, #e6a23c);
}

/* ===== 页面容器 ===== */
.system-setting-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 20px;
  background: linear-gradient(180deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  box-sizing: border-box;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 24px 28px;
  border-radius: 20px;
  background: linear-gradient(135deg, var(--qm-bg-2) 0%, #f8fbff 100%);
  border: 1px solid var(--qm-line-strong);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.05);
  flex-shrink: 0;
}

.page-header-left,
.page-header-right {
  display: flex;
  align-items: center;
}

.page-title-wrap {
  min-width: 0;
}

.page-title {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.page-subtitle {
  margin: 10px 0 0;
  font-size: 14px;
  color: var(--qm-text-2);
  line-height: 1.6;
}

/* ===== 主布局 ===== */
.system-setting-layout {
  display: flex;
  flex: 1;
  min-height: 0;
  border-radius: 22px;
  overflow: hidden;
  background: var(--qm-bg-2);
  border: 1px solid var(--qm-line-strong);
  box-shadow: 0 20px 48px rgba(15, 23, 42, 0.06);
}

.setting-sidebar {
  width: 260px;
  background: linear-gradient(180deg, #fbfcfe 0%, var(--qm-bg-1) 100%);
  border-right: 1px solid var(--qm-line-strong);
  padding: 24px 16px;
  box-sizing: border-box;
  overflow-y: auto;
}

.setting-sidebar-title {
  font-size: 13px;
  color: var(--qm-text-2);
  font-weight: 700;
  margin-bottom: 14px;
  padding: 0 10px;
  letter-spacing: 0.5px;
}

.setting-tab-item {
  padding: 16px 14px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.25s ease;
  margin-bottom: 12px;
  border: 1px solid transparent;
  background: transparent;
}

.setting-tab-item:hover {
  background: var(--qm-bg-2);
  border-color: var(--qm-warning-line);
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(245, 158, 11, 0.08);
}

.setting-tab-item.active {
  background: linear-gradient(135deg, var(--qm-accent-soft) 0%, #fffbeb 100%);
  border-color: #c7d2fe;
  box-shadow: 0 10px 22px rgba(245, 158, 11, 0.12);
}

.setting-tab-label {
  font-size: 15px;
  font-weight: 700;
  color: var(--qm-text-1);
  line-height: 1.4;
}

.setting-tab-desc {
  font-size: 12px;
  color: var(--qm-text-2);
  margin-top: 4px;
  line-height: 1.6;
}

/* ===== 右侧内容区 ===== */
.setting-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--qm-bg-1);
}

.setting-content-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 28px 30px 20px;
  border-bottom: 1px solid var(--qm-line-strong);
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(8px);
  flex-shrink: 0;
}

.setting-content-title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  line-height: 1.2;
}

.setting-content-subtitle {
  margin: 10px 0 0;
  font-size: 13px;
  color: var(--qm-text-2);
  line-height: 1.6;
}

.setting-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-content-body {
  padding: 24px 30px 24px;   /* 底部与顶部一致 */
  flex: 1;
  overflow: auto;
}

/* AI 配置面板 */
.ai-config-panel {
  min-height: 300px;
}

.ai-config-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.ai-config-summary {
  font-size: 13px;
  color: var(--qm-text-2);
}

.ai-config-summary span {
  font-weight: 700;
  color: #0f172a;
}

/* 卡片列表区域 */
.ai-config-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-config-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid var(--qm-line-strong);
  background: linear-gradient(180deg, var(--qm-bg-2) 0%, #fbfdff 100%);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.035);
  transition: all 0.25s ease;
}

.ai-config-card:hover {
  transform: translateY(-2px);
  border-color: #c7d2fe;
  box-shadow: 0 14px 28px rgba(245, 158, 11, 0.08);
}

.ai-config-card-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.ai-config-avatar-wrap {
  width: 50px;
  height: 50px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--qm-accent-soft) 0%, var(--qm-bg-1) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid var(--qm-line-strong);
}

.ai-config-avatar {
  width: 28px;
  height: 28px;
  object-fit: contain;
}

.ai-config-info {
  min-width: 0;
}

.ai-config-provider {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.4;
}

.ai-config-model {
  font-size: 13px;
  color: var(--qm-text-2);
  margin-top: 4px;
  word-break: break-all;
}

.ai-config-url {
  font-size: 12px;
  color: var(--qm-text-3);
  margin-top: 5px;
  word-break: break-all;
}

.ai-config-card-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

/* 默认供应商 */
.ai-config-provider {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.ai-config-provider span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.default-tag {
  flex-shrink: 0;
  border: none;
  color: #f59e0b;
  background: linear-gradient(135deg, var(--qm-accent-soft) 0%, #f5f3ff 100%);
}

.default-star-btn {
  color: var(--qm-line-strong) !important;
  background: var(--qm-bg-1) !important;
}

.default-star-btn:hover:not(:disabled) {
  color: #f59e0b !important;
  background: var(--qm-warning-soft-2) !important;
  transform: scale(1.05);
}

.default-star-btn-active {
  color: #f59e0b !important;
  background: var(--qm-warning-soft-2) !important;
  cursor: default !important;
}

/* 图标按钮 */
.icon-action-btn {
		border: none !important;
		font-size: 16px;
		transition: all 0.2s ease;
	}

	.edit-icon-btn {
		color: #f59e0b !important;
		background: var(--qm-accent-soft) !important;
	}

	.edit-icon-btn:hover {
		background: var(--qm-warning-soft-2) !important;
		color: #d97706 !important;
		transform: scale(1.05);
	}

	.delete-icon-btn {
		color: #ef4444 !important;
		background: var(--qm-red-soft-2) !important;
	}

	.delete-icon-btn:hover {
		background: var(--qm-red-soft-2) !important;
		color: #dc2626 !important;
		transform: scale(1.05);
	}

	/* 成员管理配置样式 */
	.member-config-panel {
		min-height: 300px;
	}

	.permission-alert {
		margin-bottom: 20px;
		border-radius: 12px;
	}

	.config-desc {
		font-size: 14px;
		color: var(--qm-text-2);
		margin-bottom: 20px;
		line-height: 1.6;
	}

	.switch-desc {
		margin-left: 8px;
		font-size: 14px;
		color: var(--qm-text-2);
	}

	.input-desc {
		margin-left: 8px;
		font-size: 14px;
		color: var(--qm-text-2);
	}

	/* 成员列表样式 */
	.member-list {
		margin-top: 16px;
	}

	.member-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 16px;
		border-radius: 16px;
		border: 1px solid var(--qm-line-strong);
		background: linear-gradient(180deg, var(--qm-bg-2) 0%, #fbfdff 100%);
		box-shadow: 0 8px 18px rgba(15, 23, 42, 0.035);
		transition: all 0.25s ease;
		margin-bottom: 12px;
	}

	.member-item:hover {
		transform: translateY(-2px);
		border-color: #c7d2fe;
		box-shadow: 0 14px 28px rgba(245, 158, 11, 0.08);
	}

	.member-info {
		display: flex;
		align-items: center;
		gap: 16px;
		min-width: 0;
	}

	.member-avatar {
		width: 48px;
		height: 48px;
		border-radius: 50%;
		background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.avatar-text {
		color: white;
		font-size: 18px;
		font-weight: 700;
		line-height: 1;
	}

	.member-details {
		min-width: 0;
	}

	.member-name {
		font-size: 16px;
		font-weight: 700;
		color: #0f172a;
		line-height: 1.4;
		margin-bottom: 4px;
	}

	.member-role {
		font-size: 14px;
		color: #f59e0b;
		margin-bottom: 4px;
	}

	.member-joined {
		font-size: 12px;
		color: var(--qm-text-3);
	}

	.member-actions {
		display: flex;
		align-items: center;
		gap: 8px;
		flex-shrink: 0;
	}

/* 占位卡片 */
.setting-placeholder-card {
  padding: 40px;
  border-radius: 18px;
  background: var(--qm-bg-2);
  border: 1px solid var(--qm-line-strong);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
}

.setting-placeholder-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.setting-placeholder-text {
  margin-top: 10px;
  font-size: 14px;
  color: var(--qm-text-2);
  line-height: 1.6;
}

.setting-placeholder-action {
  margin-top: 20px;
}

/* 对话框样式 */
.ai-provider-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.18);
}

.ai-provider-dialog :deep(.el-dialog__header) {
  padding: 20px 22px 12px;
  border-bottom: 1px solid #eef2f7;
  background: linear-gradient(180deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
}

.ai-provider-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.ai-provider-dialog :deep(.el-dialog__body) {
  padding: 22px;
}

.ai-provider-form {
  width: 100%;
}

.provider-list {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.provider-card {
  padding: 12px 8px;
  border: 1px solid #dbe2ea;
  border-radius: 14px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  background: var(--qm-bg-2);
}

.provider-card:hover {
  border-color: #fcd34d;
  box-shadow: 0 8px 20px rgba(245, 158, 11, 0.12);
  transform: translateY(-1px);
}

.provider-card.active {
  border-color: #f59e0b;
  background: linear-gradient(135deg, var(--qm-accent-soft) 0%, #f5f3ff 100%);
  box-shadow: 0 8px 20px rgba(245, 158, 11, 0.14);
}

.provider-avatar-wrap {
  width: 50px;
  height: 50px;
  margin: 0 auto 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, #eef2f7 100%);
  border: 1px solid var(--qm-line-strong);
}

.provider-avatar {
  width: 30px;
  height: 30px;
  object-fit: contain;
}

.provider-name {
  font-size: 12px;
  color: #1f2937;
  font-weight: 600;
  line-height: 1.4;
}

.setting-input :deep(.el-input__wrapper),
.full-width-select :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid #dbe2ea;
  background: var(--qm-bg-2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  padding: 0 14px;
  transition: all 0.25s ease;
}

.setting-input :deep(.el-input__wrapper:hover),
.full-width-select :deep(.el-input__wrapper:hover) {
  border-color: var(--qm-line-strong);
}

.setting-input :deep(.el-input__wrapper.is-focus),
.full-width-select :deep(.el-input__wrapper.is-focus) {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.10);
}

.full-width-select {
  width: 100%;
}

.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.dialog-footer-left,
.dialog-footer-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 主按钮 */
.primary-gradient-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%) !important;
  border: none !important;
  color: #fff !important;
  border-radius: 10px !important;
  padding: 10px 24px !important;
  font-weight: 500 !important;
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.22);
  transition: all 0.3s ease !important;
}

.primary-gradient-btn:hover,
.primary-gradient-btn:focus {
  background: linear-gradient(135deg, #5b5ff0 0%, #ea580c 100%) !important;
  color: #fff !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(245, 158, 11, 0.4) !important;
}

.primary-gradient-btn:active {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.28) !important;
}

/* 取消按钮 */
.default-light-btn {
  padding: 10px 20px !important;
  border-radius: 10px !important;
  font-weight: 500 !important;
  color: var(--qm-text-2) !important;
  background: var(--qm-bg-2) !important;
  border: 1px solid #dbe2ea !important;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  transition: all 0.25s ease !important;
}

.default-light-btn:hover,
.default-light-btn:focus {
  color: #1f2937 !important;
  border-color: #a5b4cb !important;
  background: var(--qm-bg-1) !important;
  transform: translateY(-1px);
}

/* 通用设置 - 消息推送配置 */
.message-push-config {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.config-section {
  padding: 24px;
  border-radius: 16px;
  background: var(--qm-bg-2);
  border: 1px solid var(--qm-line-strong);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
  transition: all 0.25s ease;
}

.config-section:hover {
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--qm-bg-3);
}

.section-title .el-icon {
  font-size: 20px;
  color: #f59e0b;
}

.section-title span {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.channel-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.channel-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-radius: 12px;
  background: linear-gradient(180deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  border: 1px solid var(--qm-line-strong);
  transition: all 0.25s ease;
}

.channel-item:hover {
  border-color: #c7d2fe;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.08);
}

.channel-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.channel-name {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.channel-desc {
  font-size: 13px;
  color: var(--qm-text-2);
}

/* 通用设置 */
.retention-input {
  width: 160px;
}

.setting-hint {
  margin-left: 8px;
  font-size: 14px;
  color: var(--qm-text-2);
}

.config-tip {
  font-size: 13px;
  color: var(--qm-text-3);
  line-height: 1.7;
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--qm-bg-1);
  border: 1px dashed var(--qm-line-strong);
}

.form-row {
  margin-bottom: 24px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-row :deep(.el-form-item) {
  margin-bottom: 0;
}

.form-row :deep(.el-form-item__label) {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  padding: 0 12px 8px 0;
  width: 120px;
  text-align: right;
  vertical-align: middle;
}

.form-row :deep(.el-form-item__content) {
  margin-left: 0 !important;
  display: flex;
  align-items: center;
  min-width: 0;
}

.form-row :deep(.el-input__wrapper),
.form-row :deep(.el-select__wrapper) {
  border-radius: 10px;
  border: 1px solid #dbe2ea;
  background: var(--qm-bg-2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  transition: all 0.25s ease;
}

.form-row :deep(.el-input__wrapper:hover),
.form-row :deep(.el-select__wrapper:hover) {
  border-color: var(--qm-line-strong);
}

.form-row :deep(.el-input__wrapper.is-focus),
.form-row :deep(.el-select__wrapper.is-focus) {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.10);
}

.form-row :deep(.el-textarea__inner) {
  border-radius: 10px;
  border: 1px solid #dbe2ea;
  background: var(--qm-bg-2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  transition: all 0.25s ease;
  resize: vertical;
  min-height: 80px;
}

.form-row :deep(.el-textarea__inner:hover) {
  border-color: var(--qm-line-strong);
}

.form-row :deep(.el-textarea__inner:focus) {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.10);
}

.form-row :deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.form-row :deep(.el-checkbox) {
  padding: 8px 16px;
  border-radius: 8px;
  background: var(--qm-bg-1);
  border: 1px solid var(--qm-line-strong);
  transition: all 0.25s ease;
}

.form-row :deep(.el-checkbox:hover) {
  background: var(--qm-bg-3);
  border-color: var(--qm-line-strong);
}

.form-row :deep(.el-checkbox.is-checked) {
  background: linear-gradient(135deg, var(--qm-accent-soft) 0%, #f5f3ff 100%);
  border-color: #f59e0b;
  color: #f59e0b;
}

.form-row :deep(.el-checkbox.is-checked:hover) {
  background: linear-gradient(135deg, #fef3c7 0%, #ede9fe 100%);
}
</style>