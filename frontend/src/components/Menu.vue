<template>
	<!-- 修改密码对话框 -->
	<el-dialog v-model="modifyPwdVisible" title="修改密码" width="500" append-to-body :show-close='true' class="password-dialog">
	    <el-form :model="userSave" label-position='top' :rules="passwordRules" ref="passwordFormRef">
			<el-form-item label="新密码" prop="password" label-width="80px">
				<el-input 
					v-model="userSave.password" 
					autocomplete="off" 
					placeholder="请输入新密码" 
					type="password" 
					show-password
					class="password-input"
				/>
			</el-form-item>
			<el-form-item label="确认密码" prop="password_confirm" label-width="80px">
				<el-input 
					v-model="userSave.password_confirm" 
					autocomplete="off" 
					placeholder="请再次输入新密码" 
					type="password" 
					show-password
					class="password-input"
				/>
			</el-form-item>
	    </el-form>
	    <template #footer>
	      <div class="dialog-footer">
	        <el-button @click="modifyPwdVisible = false">取消</el-button>
	        <el-button type="primary" @click="modify_pwd">确定</el-button>
	      </div>
	    </template>
	</el-dialog>

	<!-- 环境管理弹窗 -->
	<EnvManagement v-model="envManagementVisible" :menus="menus" />
	
	<!-- 主框架：左侧导航 + 顶栏（Q·M 重构版布局） -->
	<div class="qm-shell">
		<!-- 侧边导航 -->
		<aside class="qm-sidebar" :class="{ 'is-collapsed': isCollapse }">
			<div class="sidebar-logo" @click="toMyProject" title="回到我的项目">
				<div class="logo-circle">
					<svg class="logo-icon" viewBox="0 0 100 100">
						<path d="M50,10 L90,30 L90,70 L50,90 L10,70 L10,30 Z" class="logo-hexagon"></path>
						<circle cx="50" cy="50" r="20" class="logo-center"></circle>
						<path d="M35,35 L65,35 L65,65 L35,65 Z" class="logo-square"></path>
					</svg>
					<div class="logo-glow"></div>
				</div>
				<div class="sidebar-logo-text" v-show="!isCollapse">
					<h1 class="platform-name">Q·M 测试平台</h1>
					<p class="platform-slogan">智能测试解决方案</p>
				</div>
			</div>
			<el-scrollbar class="sidebar-scroll">
			<el-menu
			  ref="menu"
			  :default-active="defaultPath"
			  :collapse-transition='false'
			  class="sidebar-menu"
			  :default-openeds="openedMenus"
			  :collapse="isCollapse"
			  router
			>

		  <!-- 项目首页 -->
		  <el-menu-item index="/project/index" class="menu-item" @click='toProjectIndex' v-if='!showUser'>
			  <template #title>
			  	<el-icon class="menu-icon"><component is="House"></component></el-icon>
			  	<span class="menu-text">项目概览</span>
			  </template>
		  </el-menu-item>
		  
		  <!-- 动态菜单（过滤掉"环境管理"，已改为弹窗方式打开） -->
		  <template v-for="menu_obj in menus">
			  <el-sub-menu
				:index="menu_obj.id"
				:key='menu_obj.id'
				v-if="menu_obj.has_permission && !showUser && menu_obj.name !== '环境管理'"
				class="sub-menu"
				popper-class="custom-submenu-popup"
			  >
					<template #title>
						<el-icon class="menu-icon"><component :is="menu_obj.icon"></component></el-icon>
						<span class="menu-text">{{ menu_obj.name }}</span>
					</template>
					<template v-for="menu_child_obj in menu_obj.children" :key='menu_child_obj.path'>
						<el-menu-item 
							v-if='menu_child_obj.has_permission' 
							:index="menu_child_obj.path" 
							class="sub-menu-item"
						>
							<template #title>
								<el-icon class="sub-menu-icon"><component :is="menu_child_obj.icon"></component></el-icon>
								<span class="sub-menu-text">{{ menu_child_obj.name }}</span>
							</template>
						</el-menu-item>
					</template>
			  </el-sub-menu>
		  </template>

		 <!-- 系统管理菜单 -->
		<el-sub-menu index="/user/list" class="sub-menu" popper-class="custom-submenu-popup" v-if="showUser && userInfo.is_superuser">
			<template #title>
				<div class="menu-title">
					<el-icon class="menu-icon"><Setting /></el-icon>
					系统管理
				</div>
			</template>
			<el-menu-item index='/user/list'  class='menu-item'>
				<el-icon><User /></el-icon>
				用户列表
			</el-menu-item>
			<el-menu-item index='/user/role'  class='menu-item'>
				<el-icon><SwitchFilled /></el-icon>
				角色列表
			</el-menu-item>
			<el-menu-item index='/user/permission'  class='menu-item'>
			<el-icon><Burger /></el-icon>
			权限列表
		</el-menu-item>
		<el-menu-item index='/user/auditLog'  class='menu-item'>
			<el-icon><Document /></el-icon>
			审计日志
		</el-menu-item>
		</el-sub-menu>


		<!-- 项目管理菜单 -->
		<el-sub-menu index="/myProjects" class="sub-menu" popper-class="custom-submenu-popup" v-if="showUser">
			<template #title>
				<div class="menu-title">
					<el-icon class="menu-icon"><FolderOpened /></el-icon>
					项目管理
				</div>
			</template>
			<el-menu-item index='/myProjects' @click='toMyProject' class='menu-item'>
				<el-icon><Folder /></el-icon>
				我的项目
			</el-menu-item>
			<el-menu-item index='/project/list' @click='toProjectList' class='menu-item'>
				<el-icon><List /></el-icon>
				项目列表
			</el-menu-item>
			<el-menu-item index='/project/appeal' @click='toProjectAppeal' class='menu-item'>
				<el-icon><DocumentAdd /></el-icon>
				我的项目申请
			</el-menu-item>
			<el-menu-item index='/project/myAppeal' @click='toProjectMyAppeal' class='menu-item'>
				<el-icon><Document /></el-icon>
				我申请的项目
			</el-menu-item>
		</el-sub-menu>


		  <!-- 项目管理菜单 -->
		<el-sub-menu index="/user/tool" class="sub-menu" popper-class="custom-submenu-popup" v-if="showUser">
			<template #title>
				<div class="menu-title">
					<el-icon class="menu-icon"><FirstAidKit /></el-icon>
					常用工具
				</div>
			</template>
			 <!-- 导航页菜单 -->
			<el-menu-item :index="''" @click='toTestTool' class="menu-item " v-if="showUser">
				<el-icon><SuitcaseLine /></el-icon>
				测试工具
			</el-menu-item>
			<el-menu-item :index="''" @click='toNavagation' class="menu-item " v-if="showUser">
				<el-icon><Link /></el-icon>
				平台导航
			</el-menu-item>
		</el-sub-menu>
		  
		  <!-- 我的项目 -->
		  <el-menu-item index='/myProjects' class="menu-item my-project-item" @click='toMyProject' v-if='!showUser'>
				<template #title>
					<el-icon class="menu-icon"><component is="StarFilled"></component></el-icon>
					<span class="menu-text">我的项目</span>
				</template>
		  </el-menu-item>
		  
			</el-menu>
			</el-scrollbar>
			<div class="sidebar-footer" @click="toggleCollapse">
				<el-icon class="collapse-icon"><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
				<span class="collapse-text" v-show="!isCollapse">收起菜单</span>
			</div>
		</aside>

		<!-- 顶栏 -->
		<header class="qm-topbar">
			<div class="topbar-left">
				<span class="topbar-title">{{ pageTitle }}</span>
			</div>
			<div class="topbar-actions">
			 <!-- 主题切换 -->
			<div class="toolbar-item" @click="toggleTheme">
				 <el-tooltip :content="theme === 'dark' ? '切换浅色' : '切换深色'" placement="bottom">
				 	<el-icon class="toolbar-icon"><Sunny v-if="theme === 'dark'" /><Moon v-else /></el-icon>
				 </el-tooltip>
			 </div>

			 <!-- 帮助文档 -->
			<div class="toolbar-item" @click="openHelp">
				 <el-tooltip content="帮助文档" placement="bottom">
				 	<el-icon class="toolbar-icon"><QuestionFilled /></el-icon>
				 </el-tooltip>
			 </div>

			 <!-- 全屏按钮 -->
			 <div class="toolbar-item" @click='fullScreen'>
				 <el-tooltip content="全屏显示" placement="bottom">
				 	<el-icon class="toolbar-icon"><FullScreen /></el-icon>
				 </el-tooltip>
			 </div>

			  <!-- 项目设置 -->
			<div class="toolbar-item" @click="toProjectSetting" v-if="!showUser">
				 <el-tooltip content="项目设置" placement="bottom">
				 	<el-icon class="toolbar-icon"><Setting /></el-icon>
				 </el-tooltip>
			 </div>

			   <!-- 环境管理（仅项目视图，根据权限判断） -->
		<div class="toolbar-item" @click="openEnvManagement" v-if="!showUser && hasEnvManagementPermission">
			 <el-tooltip content="环境管理" placement="bottom">
			 	<el-icon class="toolbar-icon"><HelpFilled /></el-icon>
			 </el-tooltip>
		 </div>

			   <!-- 消息通知 -->
		 <div class="toolbar-item message-bell" @click="openMessageDialog" v-if="!showUser">
		 		<el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99" class="message-badge">
		 			<el-icon class="toolbar-icon"><Bell /></el-icon>
		 		</el-badge>
		 </div>

			 <!-- 用户菜单 -->
			 <el-dropdown @command="handleCommand" class="user-dropdown">
				  <div class="user-info">
					<el-avatar
						:size="32"
						class="user-avatar"
						:src="userAvatar"
					>
					  {{ userInfo.user_name ? userInfo.user_name.charAt(0).toUpperCase() : 'U' }}
					</el-avatar>
					<div class="user-details">
						<span class="user-name">{{ userInfo.user_name }}</span>
						<el-icon class="dropdown-arrow"><arrow-down /></el-icon>
					</div>
				  </div>
				  <template #dropdown>
					<el-dropdown-menu class="user-dropdown-menu">
					  <el-dropdown-item command="modifyPwd" class="dropdown-item">
					  	<el-icon><Key /></el-icon>
					  	<span>修改密码</span>
					  </el-dropdown-item>
					  <el-dropdown-item divided command="logout" class="dropdown-item logout">
					  	<el-icon><SwitchButton /></el-icon>
					  	<span>退出登录</span>
					  </el-dropdown-item>
					</el-dropdown-menu>
				  </template>
			 </el-dropdown>
		 </div>
		</header>

		 <!-- 消息通知弹窗 -->
		 <el-dialog v-model="messageDialogVisible" title="消息通知" width="1100" append-to-body class="message-dialog" @close="onMessageDialogClose">
		 		<template #header>
		 			<div class="message-dialog-header">
		 				<span class="message-dialog-title">消息通知</span>
		 				<el-button text type="primary" @click="markAllRead" v-if="unreadCount > 0" style="margin-right: 30px;">全部已读</el-button>
		 			</div>
		 		</template>
		 		<el-tabs v-model="activeMessageTab" @tab-change="onMessageTabChange">
		 			<!-- 系统通知 -->
		 			<el-tab-pane name="1">
		 				<template #label>
		 					<span class="tab-label-wrap">系统通知
		 						<span v-if="unreadByType['1'] > 0" class="tab-unread-badge">{{ unreadByType['1'] }}</span>
		 					</span>
		 				</template>
		 				<div class="message-tab-list" v-loading="messageLoading">
		 					<div v-if="messageList.length === 0" class="message-empty">
		 						<el-empty description="暂无消息" :image-size="80" />
		 					</div>
		 					<div
		 						v-for="msg in messageList"
		 						:key="msg.id"
		 						class="message-item"
		 						:class="{ unread: !msg.is_read }"
		 						@click="handleMessageClick(msg)"
		 					>
		 						<div class="message-dot" v-if="!msg.is_read"></div>
		 						<div class="message-content">
		 							<div class="message-title">
		 								<span class="message-title-text">{{ msg.title }}</span>
		 							</div>
		 							<div class="message-text">{{ msg.content }}</div>
		 							<div class="message-time">{{ msg.create_time }}</div>
		 						</div>
		 						<el-icon class="message-delete-icon" @click.stop="handleDeleteMessage(msg)"><Delete /></el-icon>
		 					</div>
		 				</div>
		 			</el-tab-pane>

		 			<!-- 告警消息（仅在项目视图中显示） -->
	 			<el-tab-pane name="3" v-if="!showUser">
	 				<template #label>
	 					<span class="tab-label-wrap">告警消息
	 						<span v-if="unreadByType['3'] > 0" class="tab-unread-badge">{{ unreadByType['3'] }}</span>
	 					</span>
	 				</template>
	 				<div class="message-tab-list" v-loading="messageLoading">
	 					<div v-if="messageList.length === 0" class="message-empty">
	 						<el-empty description="暂无消息" :image-size="80" />
	 					</div>
	 					<div
	 						v-for="msg in messageList"
	 						:key="msg.id"
	 						class="message-item"
	 						:class="{ unread: !msg.is_read }"
	 						@click="handleMessageClick(msg)"
	 					>
	 						<div class="message-dot" v-if="!msg.is_read"></div>
	 						<div class="message-content">
	 							<div class="message-title">
	 								<span class="message-title-text">{{ msg.title }}</span>
	 							</div>
	 							<div class="message-text">{{ msg.content }}</div>
	 							<div class="message-time">{{ msg.create_time }}</div>
	 						</div>
	 						<el-icon class="message-delete-icon" @click.stop="handleDeleteMessage(msg)"><Delete /></el-icon>
	 					</div>
	 				</div>
	 			</el-tab-pane>

	 			<!-- 任务消息（仅在项目视图中显示） -->
	 			<el-tab-pane name="2" v-if="!showUser">
	 				<template #label>
	 					<span class="tab-label-wrap">任务消息
	 						<span v-if="unreadByType['2'] > 0" class="tab-unread-badge">{{ unreadByType['2'] }}</span>
	 					</span>
	 				</template>
	 				<div class="message-tab-list" v-loading="messageLoading">
	 					<div v-if="messageList.length === 0" class="message-empty">
	 						<el-empty description="暂无消息" :image-size="80" />
	 					</div>
	 					<div
	 						v-for="msg in messageList"
	 						:key="msg.id"
	 						class="message-item task-message-item"
	 						:class="{ unread: !msg.is_read }"
	 						@click="handleMessageClick(msg)"
	 					>
	 						<div class="message-dot" v-if="!msg.is_read"></div>
	 						<div class="message-content">
	 							<div class="message-title">
	 								<span class="message-title-text">{{ msg.title }}</span>
	 								<el-tag v-if="msg.task_status === 1" type="warning" size="small" effect="light" class="task-status-tag">进行中</el-tag>
	 								<el-tag v-else-if="msg.task_status === 2" type="success" size="small" effect="light" class="task-status-tag">已完成</el-tag>
	 								<el-tag v-else-if="msg.task_status === 3" type="danger" size="small" effect="light" class="task-status-tag">失败</el-tag>
	 							</div>
	 							<div class="task-stats-row">
	 								<div class="task-stat-item stat-total">
									<span class="stat-label">总数</span>
									<span class="stat-value">{{ msg.total_count ?? 0 }}</span>
								</div>
	 								<div class="task-stat-item stat-success">
	 									<span class="stat-label">成功</span>
	 									<span class="stat-value">{{ msg.success_count ?? 0 }}</span>
	 								</div>
	 								<div class="task-stat-item stat-failed" v-if="msg.failed_count > 0">
	 									<el-tooltip
	 										:content="msg.fail_reason || '未知错误'"
	 										placement="top"
	 										effect="dark"
	 									>
	 										<span class="stat-label">失败</span>
	 										<span class="stat-value">{{ msg.failed_count }}</span>
	 									</el-tooltip>
	 								</div>
	 								<div class="task-stat-item stat-failed" v-else>
	 									<span class="stat-label">失败</span>
	 									<span class="stat-value">0</span>
	 								</div>
	 								<div class="task-stat-item stat-duration" v-if="msg.duration != null">
									<span class="stat-label">耗时</span>
									<span class="stat-value">{{ msg.duration % 1 === 0 ? msg.duration : msg.duration.toFixed(1) }}s</span>
								</div>
	 							</div>
	 							<div class="message-meta">
	 								<span class="message-time">{{ msg.create_time }}</span>
	 								<span class="message-creator" v-if="msg.create_by_name">创建人: {{ msg.create_by_name }}</span>
	 							</div>
	 						</div>
	 						<el-icon class="message-delete-icon" @click.stop="handleDeleteMessage(msg)"><Delete /></el-icon>
	 					</div>
	 				</div>
	 			</el-tab-pane>
		 		</el-tabs>

		 		<div class="message-pagination" v-if="messageTotal > 0">
		 			<el-pagination
		 				v-model:current-page="messagePage"
		 				v-model:page-size="messagePageSize"
		 				:page-sizes="[10, 20, 30, 50]"
		 				:total="messageTotal"
		 				layout="total, sizes, prev, pager, next, jumper"
		 				@size-change="onMessageSizeChange"
		 				@current-change="onMessagePageChange"
		 				:background="true"
		 				class="select input"
		 			/>
		 		</div>
		 </el-dialog>

	</div>
</template>

<script>
import {mapState, mapActions, mapMutations} from 'vuex'
import { h } from 'vue'
import { Menu, Fold, Expand, ArrowDown, ArrowUp, Key, Document, SwitchButton, QuestionFilled, FullScreen, StarFilled, House, Bell, Delete, Right, Check, HelpFilled, View, Moon, Sunny } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import api, { base_url } from '../api/index.js'
import EnvManagement from './EnvManagement.vue'

export default {
  name: 'TopMenu',
  components: { EnvManagement },
  setup() {
  	return {
  		Fold,
		Menu,
		Expand,
		ArrowDown,
		ArrowUp,
		Key,
		Document,
		SwitchButton,
		QuestionFilled,
		FullScreen,
		StarFilled,
		House,
		Bell,
		Delete,
		Right,
		Check,
		HelpFilled,
		View,
		Moon,
		Sunny
  	}
  },
  data() {
	const validatePassword = (rule, value, callback) => {
		if (value === '') {
			callback(new Error('请输入密码'));
		} else if (value.length < 6) {
			callback(new Error('密码长度不能少于6位'));
		} else {
			if (this.userSave.password_confirm !== '') {
				this.$refs.passwordFormRef.validateField('password_confirm');
			}
			callback();
		}
	};
	
	const validatePasswordConfirm = (rule, value, callback) => {
		if (value === '') {
			callback(new Error('请再次输入密码'));
		} else if (value !== this.userSave.password) {
			callback(new Error('两次输入密码不一致'));
		} else {
			callback();
		}
	};
	
  	return {
		menus: '',
		loading: true,
		defaultPath: '',
		first_menu_name: '项目首页',
		second_menu_name: '',
		isCollapse: false,
		isExpand: false,
		openedMenus: [],
		envManagementVisible: false,
		modifyPwdVisible: false,
		userSave: {
			id: '',
			password: '',
			password_confirm: ''
		},
		passwordRules: {
			password: [
				{ required: true, validator: validatePassword, trigger: 'blur' }
			],
			password_confirm: [
				{ required: true, validator: validatePasswordConfirm, trigger: 'blur' }
			]
		},
		// 用户头像URL（如果有的话）
		userAvatar: '',
		// 消息通知
		unreadCount: 0,
		unreadByType: { '1': 0, '2': 0, '3': 0 },
		messageList: [],
		messageLoading: false,
		messageDialogVisible: false,
		activeMessageTab: '1',
		messagePage: 1,
		messagePageSize: 10,
		messageTotal: 0,
		messageRefreshTimer: null,
		// WebSocket 实时推送
		ws: null,
		wsReconnectTimer: null,
		wsRetryCount: 0
  	}
  },
  props: {
	'width':{
		type: String,
	},
	'showUser':{
		type: Boolean,
		default: false,
	}
  },
  computed: {
  	...mapState(['role_id', 'pathPermission', 'userInfo', 'projectInfo', 'theme']),
  	// 环境管理权限：从动态菜单中查找"环境管理"的 has_permission
  	hasEnvManagementPermission() {
  		if (!this.menus || !Array.isArray(this.menus)) return false
  		const envMenu = this.menus.find(m => m.name === '环境管理')
  		return envMenu ? envMenu.has_permission : false
  	},
  	// 顶栏标题：项目空间显示项目名，系统层显示控制台
  	pageTitle() {
  		if (!this.showUser && this.projectInfo && this.projectInfo.name) return this.projectInfo.name
  		return '控制台'
  	}
  },
  methods: {
	  ...mapMutations(['setPathPermission', 'toggleTheme']),
	  openEnvManagement() {
	  	this.envManagementVisible = true
	  },
	  toMyProject(){
	  	this.$router.push({name: 'myProject'})
	  	this.defaultPath = '/myProjects'
	  },
	  toggleCollapse(){
	  	this.isCollapse = !this.isCollapse
	  	// 同步到 html 属性，让内容区(.qm-content-area)的 margin 联动收窄
	  	document.documentElement.setAttribute('data-sidebar', this.isCollapse ? 'collapsed' : 'expanded')
	  	try { localStorage.setItem('qm-sidebar-collapsed', this.isCollapse ? '1' : '0') } catch(e) {}
	  	this.$emit('collapse-change', this.isCollapse)
	  },
		toProjectSetting(){
			this.$router.push({name: 'systemSetting'})
			this.defaultPath = '/project/setting'
		},
		toProjectList(){
			this.$router.push({name: 'projectList'})
			this.defaultPath = '/project/list'
		},
		toProjectAppeal(){
			this.$router.push({name: 'projectAppeal'})
			this.defaultPath = '/project/appeal'
		},
		toProjectMyAppeal(){
			this.$router.push({name: 'myAppeal'})
			this.defaultPath = '/project/myAppeal'
		},
		toTestTool(){
			const routeData = this.$router.resolve({ name: 'Tools' });
			window.open(routeData.href, '_blank');
		},
		toNavagation(){
			const routeData = this.$router.resolve({ name: 'navigation' });
			window.open(routeData.href, '_blank');
			// this.$router.push({name: 'navigation'})
			// this.defaultPath = '/user/navigation'
		},
	  play_menu(){
	  	document.getElementById('home_menu').style='display:block;'
	  },
	  toProjects(){
	  	this.$router.push({name: 'myProject'})
	  },
	  async exitLogin(){  
		ElMessageBox.confirm(
	      '确定要退出登录吗？',
	      '退出确认',
	      {
	        confirmButtonText: '确定',
	        cancelButtonText: '取消',
	        type: 'warning',
	        customClass: 'logout-confirm'
	      }
	    ).then(async () => {
	      try {
	        // 调用登出接口
	        const response = await api.logout();
	        
	        // 清除本地存储的token和用户信息
	        window.localStorage.removeItem('token');
	        window.localStorage.removeItem('userinfo');
	        
	        // 清除Vuex中的用户信息
	        this.$store.commit('clearUserInfo');
	        
	        // 跳转到登录页面
	        this.$router.push({name: 'login'});
	        
	        // 显示退出成功的提示
	        ElMessage({
	          type: 'success',
	          message: '已退出登录',
	        });
	      } catch (error) {
	        console.error('退出登录失败:', error);
	        
	        // 即使接口调用失败，也清除本地存储并跳转到登录页面
	        window.localStorage.removeItem('token');
	        window.localStorage.removeItem('userinfo');
	        this.$store.commit('clearUserInfo');
	        this.$router.push({name: 'login'});
	        
	        ElMessage({
	          type: 'success',
	          message: '已退出登录',
	        });
	      }
	    }).catch(() => {
	      // 取消退出
	    })
	  },
	  fullScreen(){
	  	let full = document.fullscreenElement  
		   if(!full){
				document.documentElement.requestFullscreen()
			}else{
				document.exitFullscreen()        
			}
	  },
	  openHelp(){
		// const help = this.$router.push({name: 'help'})
	  	const routeData = this.$router.resolve({ name: 'help' });
	  	window.open(routeData.href, '_blank');
	  },
	  handleCommand(command){
	  	if (command === 'modifyPwd'){
	  		this.modifyPwdVisible = true
			// 重置表单
			this.$nextTick(() => {
				if (this.$refs.passwordFormRef) {
					this.$refs.passwordFormRef.resetFields();
				}
			});
	  	}else if(command === 'help'){
	  		this.openHelp()
	  	}else if(command === 'logout'){
	  		this.exitLogin()
	  	}
	  },
	  async modify_pwd(){
		try {
			await this.$refs.passwordFormRef.validate();
			this.userSave.id = this.userInfo.user_id;
			const response = await this.$api.modify_pwd(this.userSave);
			if(response.status === 200){
				ElMessage({
					message: '密码修改成功',
					type: 'success'
				});
				this.modifyPwdVisible = false;
				// 清空密码字段
				this.userSave.password = '';
				this.userSave.password_confirm = '';
			}
		} catch (error) {
			if (error.errors) {
				console.error('请正确填写密码信息:', error);
			} else {
				console.error('修改密码失败:', error);
			}
		}
	  },
	  
	  // 消息通知相关方法
  openMessageDialog() {
  	this.messageDialogVisible = true
  	this.messagePage = 1
  	// 在系统管理等非项目视图下（showUser=true），只允许系统通知Tab，强制重置避免Tab消失后activeTab残留
  	if (this.showUser) {
  		this.activeMessageTab = '1'
  	}
  	this.fetchMessages()
  	this.fetchUnreadCount()
  },
	  onMessageTabChange() {
	  	this.messagePage = 1
	  	this.stopMessageRefresh()
	  	this.fetchMessages()
	  },
	  onMessagePageChange() {
	  	this.fetchMessages()
	  },
	  onMessageSizeChange() {
	  	this.messagePage = 1
	  	this.fetchMessages()
	  },
	  async fetchMessages() {
	  	this.messageLoading = true
	  	try {
	  		const params = {
	  			size: this.messagePageSize,
	  			page: this.messagePage,
	  			message_type: this.activeMessageTab,
	  		}
	  		if (!this.showUser && this.projectInfo?.id) {
	  			params.project = this.projectInfo.id
	  		}
	  		const res = await api.getMessages(params)
	  		if (res.status === 200) {
	  			this.messageList = res.data.results || []
	  			this.messageTotal = res.data.count || 0
	  			// 任务消息tab: 检查是否有进行中的任务，自动刷新
	  			if (this.activeMessageTab === '2' && this.messageDialogVisible) {
	  				this.checkAndStartRefresh()
	  			}
	  		}
	  	} catch (e) {
	  		console.error('获取消息失败:', e)
	  	} finally {
	  		this.messageLoading = false
	  	}
	  },
	  checkAndStartRefresh() {
	  	const hasRunning = this.messageList.some(msg => msg.task_status === 1)
	  	if (hasRunning && !this.messageRefreshTimer) {
	  		this.messageRefreshTimer = setInterval(() => {
	  			this.fetchMessages()
	  			this.fetchUnreadCount()
	  		}, 5000)
	  	} else if (!hasRunning && this.messageRefreshTimer) {
	  		this.stopMessageRefresh()
	  		this.fetchUnreadCount()
	  	}
	  },
	  stopMessageRefresh() {
	  	if (this.messageRefreshTimer) {
	  		clearInterval(this.messageRefreshTimer)
	  		this.messageRefreshTimer = null
	  	}
	  },
	  onMessageDialogClose() {
	  	this.stopMessageRefresh()
	  },
	  // ===== WebSocket 实时推送 =====
	  connectWebSocket() {
	  	if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
	  		return
	  	}
	  	try {
	  		const token = JSON.parse(window.localStorage.getItem('token'))
	  		if (!token) {
	  			return
	  		}
	  		// base_url 形如 http://host:8000，转换为 ws://host:8000
	  		const wsProtocol = base_url.startsWith('https') ? 'wss' : 'ws'
	  		const wsBase = base_url.replace(/^https?:\/\//, '')
	  		const wsUrl = `${wsProtocol}://${wsBase}/ws/message/?token=${encodeURIComponent(token)}`
	  		const ws = new WebSocket(wsUrl)
	  		this.ws = ws

	  		ws.onopen = () => {
	  			this.wsRetryCount = 0
	  		}
	  		ws.onmessage = (event) => {
	  			try {
	  				const data = JSON.parse(event.data)
	  				if (data && data.type === 'message.push' && data.message) {
	  					this.handleWsPush(data.message)
	  				}
	  			} catch (e) {
	  				console.error('WS 消息解析失败:', e)
	  			}
	  		}
	  		ws.onerror = () => {
	  			console.warn('WebSocket 连接错误')
	  		}
	  		ws.onclose = () => {
	  			// 断线自动重连(指数退避)
	  			const delay = Math.min(30000, 1000 * Math.pow(2, this.wsRetryCount))
	  			this.wsRetryCount++
	  			this.ws = null
	  			this.wsReconnectTimer = setTimeout(() => {
	  				this.connectWebSocket()
	  			}, delay)
	  		}
	  	} catch (e) {
	  		console.error('建立 WebSocket 失败:', e)
	  	}
	  },
	  disconnectWebSocket() {
	  	if (this.wsReconnectTimer) {
	  		clearTimeout(this.wsReconnectTimer)
	  		this.wsReconnectTimer = null
	  	}
	  	if (this.ws) {
	  		this.ws.onclose = null
	  		this.ws.close()
	  		this.ws = null
	  	}
	  },
	  handleWsPush(msg) {
			  	// 有新消息：刷新未读数与列表
			  	this.fetchUnreadCount()
			  	this.fetchMessages()
			  	// 任务进行中状态只刷新列表，不弹右上角通知窗
			  	if (msg.message_type === '2' && String(msg.task_status) === '1') {
			  		return
			  	}
			  	// 右上角弹窗提示，点击跳转关联链接
			  	const messageTypeMap = { '1': '系统通知', '2': '任务通知', '3': '告警通知' }
			  	const title = msg.title || '新消息'
			  	const relatedUrl = msg.related_url
			  	// 构建消息内容 VNode
			  	const contentNodes = []
			  	if (msg.message_type === '2' && msg.task_status) {
			  		const statBase = 'display:inline-flex;align-items:center;gap:3px;padding:2px 8px;border-radius:5px;font-size:11px;font-weight:500;'
			  		contentNodes.push(
			  			h('div', { style: 'display:flex;align-items:center;gap:6px;flex-wrap:wrap;' }, [
			  				msg.total_count != null ? h('span', { style: statBase + 'background:#fffbeb;color:#d97706;' }, [
			  					h('span', { style: 'color:#d97706;' }, '总数'),
			  					h('span', { style: 'color:#b45309;font-weight:600;' }, String(msg.total_count))
			  				]) : null,
			  				msg.success_count != null ? h('span', { style: statBase + 'background:#ecfdf5;color:#047857;' }, [
			  					h('span', { style: 'color:#047857;' }, '成功'),
			  					h('span', { style: 'color:#065f46;font-weight:600;' }, String(msg.success_count))
			  				]) : null,
			  				h('span', { style: statBase + 'background:#fef2f2;color:#b91c1c;' }, [
			  					h('span', { style: 'color:#b91c1c;' }, '失败'),
			  					h('span', { style: 'color:#991b1b;font-weight:600;' }, String(msg.failed_count ?? 0))
			  				]),
			  				msg.duration != null ? h('span', { style: statBase + 'background:#fefce8;color:#a16207;' }, [
			  					h('span', { style: 'color:#a16207;' }, '耗时'),
			  					h('span', { style: 'color:#854d0e;font-weight:600;' }, (msg.duration % 1 === 0 ? String(msg.duration) : msg.duration.toFixed(1)) + 's')
			  				]) : null,
			  			])
			  		)
			  	} else {
			  		contentNodes.push(
			  			h('div', { style: 'font-size:12px;color:var(--qm-text-2);line-height:1.7;margin-bottom:10px;white-space:pre-wrap;' }, msg.content || messageTypeMap[msg.message_type] || '')
			  		)
			  	}
			  	// 操作按钮（先构建 VNode，再创建通知以使 notification 变量被闭包捕获）
			  	const btnNodes = []
			  	const btnBase = 'display:inline-flex;align-items:center;justify-content:center;height:28px;padding:0 14px;border-radius:6px;font-size:12px;cursor:pointer;border:none;outline:none;transition:all .2s;'
			  	btnNodes.push(
			  		h('button', {
			  			style: btnBase + 'background:var(--qm-bg-3);color:var(--qm-text-2);',
			  			onClick: (e) => {
			  				e.stopPropagation()
			  				notification.close()
			  			}
			  		}, '知道了')
			  	)
			  	if (relatedUrl) {
			  		btnNodes.push(
			  			h('button', {
			  				style: btnBase + 'background:#f59e0b;color:#fff;',
			  				onClick: (e) => {
			  					e.stopPropagation()
			  					notification.close()
			  					this.$router.push(relatedUrl)
			  				}
			  			}, '去处理')
			  		)
			  	}
			  	contentNodes.push(
			  		h('div', { style: 'display:flex;gap:8px;justify-content:flex-end;' }, btnNodes)
			  	)
			  	// 根据任务结果选择通知类型（成功=绿色，有失败=红色，其他=蓝色）
			  	let notifyType = 'info'
			  	if (msg.message_type === '2' && msg.task_status) {
			  		if (String(msg.task_status) === '3') {
			  			notifyType = 'error'
			  		} else if ((msg.failed_count ?? 0) > 0) {
			  			notifyType = 'warning'
			  		} else {
			  			notifyType = 'success'
			  		}
			  	}
			  	const notification = ElNotification({
			  		title,
			  		message: h('div', { style: 'font-size:13px;color:#334155;line-height:1.6;display:flex;flex-direction:column;gap:20px;padding-top:20px;' }, contentNodes),
			  		type: notifyType,
			  		duration: 0,
			  		showClose: false,
			  		width: 360,
			  		onClick: () => {
			  			if (relatedUrl) {
			  				this.$router.push(relatedUrl)
			  			}
			  		}
			  	})
			  },
	  async fetchUnreadCount() {
	  	try {
	  		const params = {}
	  		if (!this.showUser && this.projectInfo?.id) {
	  			params.project_id = this.projectInfo.id
	  		}
	  		const res = await api.getUnreadMessageCount(params)
	  		if (res.status === 200) {
	  			const data = res.data
	  			this.unreadCount = data.result?.count || data.count || 0
	  			const bt = data.result?.by_type || data.by_type || {}
	  			Object.assign(this.unreadByType, {
	  				'1': Number(bt['1']) || 0,
	  				'2': Number(bt['2']) || 0,
	  				'3': Number(bt['3']) || 0,
	  			})
	  		}
	  	} catch (e) {
	  		console.error('获取未读消息数失败:', e)
	  		this.unreadCount = 0
	  		Object.assign(this.unreadByType, { '1': 0, '2': 0, '3': 0 })
	  	}
	  },
	  async markAllRead() {
	  	if (this.unreadCount === 0) return
	  	try {
	  		await api.markAllMessageRead()
	  		this.unreadCount = 0
	  		Object.assign(this.unreadByType, { '1': 0, '2': 0, '3': 0 })
	  		this.messageList.forEach(msg => {
	  			msg.is_read = true
	  		})
	  		ElMessage.success('全部已读')
	  	} catch (e) {
	  		console.error('标记已读失败:', e)
	  	}
	  },
	  async markSingleRead(msg) {
	  	if (!msg.is_read) {
	  		try {
	  			await api.markMessageRead({ message_ids: [msg.id] })
	  			msg.is_read = true
	  			await this.fetchUnreadCount()
	  			ElMessage.success('已标记为已读')
	  		} catch (e) {
	  			console.error('标记已读失败:', e)
	  			ElMessage.error('标记已读失败')
	  		}
	  	}
	  },
	  async handleDeleteMessage(msg) {
	  	try {
	  		await ElMessageBox.confirm('确定删除该消息吗？', '提示', {
	  			confirmButtonText: '确定',
	  			cancelButtonText: '取消',
	  			type: 'warning',
	  		})
	  		await api.deleteMessage(msg.id)
	  		ElMessage.success('删除成功')
	  		this.fetchMessages()
	  		this.fetchUnreadCount()
	  	} catch (e) {
	  		if (e !== 'cancel') {
	  			console.error('删除消息失败:', e)
	  		}
	  	}
	  },
	  async handleMessageClick(msg) {
	  	if (!msg.is_read) {
	  		try {
	  			await api.markMessageRead({ message_ids: [msg.id] })
	  			msg.is_read = true
	  			await this.fetchUnreadCount()
	  		} catch (e) {
		  		console.error('标记已读失败:', e)
		  	}
	  	}
	  	if (msg.related_url) {
	  		this.messageDialogVisible = false
	  		this.$router.push(msg.related_url)
	  	}
	  },
	  async jumpToRelated(row) {
		  if (row.related_url) {
			  if (!row.is_read) {
				  try {
					  await api.markMessageRead({ message_ids: [row.id] })
					  row.is_read = true
					  await this.fetchUnreadCount()
				  } catch (e) {
					  console.error('标记已读失败:', e)
				  }
			  }
			  this.messageDialogVisible = false
			  this.$router.push(row.related_url)
		  }
	  },
	  updateDefaultPath() {
	    const path = this.$route.path
	    // 遍历菜单项做前缀匹配：详情/编辑页路径以列表页路径开头时自动高亮
	    // 取最长匹配，避免短路径误匹配
	    let matchedPath = ''
	    for (const menu of this.menus) {
	      if (menu.children) {
	        for (const child of menu.children) {
	          if (child.has_permission && path.startsWith(child.path) && child.path.length > matchedPath.length) {
	            matchedPath = child.path
	          }
	        }
	      }
	    }
	    this.defaultPath = matchedPath || path
	  },
	  
	  async getRole(){
		  let requeset_role_id = this.role_id
		  if (requeset_role_id === null){
		  	 return
		  }
		  if(this.userInfo.is_superuser || this.userInfo.user_id === this.projectInfo.create_by){
				console.log('是超级用户或项目创建人')
				requeset_role_id = 0
		  }
		  const response = await this.$api.getRole(requeset_role_id, {is_add: false, project_id: this.projectInfo.id})
		  if (response.status === 200){
			  this.menus = [...response.data.result.role_permissions]
			  this.setPathPermission(response.data.result.pathPermissions)
			  // 菜单数据加载完成后，用前缀匹配重新计算高亮路径
			  this.updateDefaultPath()
		  }
	  },
	  // 生成用户头像背景色
	  generateAvatarColor(name) {
	    if (!name) return '#f59e0b'
	    
	    const colors = [
	      '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
	      '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
	    ]
	    
	    // 根据用户名首字母生成颜色
	    const charCode = name.charCodeAt(0)
	    return colors[charCode % colors.length]
	  }
  },
  watch: {
      isCollapse(newVal) {
        // 触发事件，通知父组件
        this.$emit('collapse-change', newVal);
      },
      // 监听 showUser 变化，重新获取消息
      showUser: {
        handler() {
          this.fetchUnreadCount()
          this.fetchMessages()
        },
        immediate: false
      },
      // 监听 projectInfo 变化，重新获取消息（项目视图）
      projectInfo: {
        handler(newVal) {
          if (!this.showUser && newVal?.id) {
            this.fetchUnreadCount()
            this.fetchMessages()
          }
        },
        deep: true,
        immediate: false
      },
      // 监听路由变化，重新获取消息
      '$route': {
        handler() {
          console.log('路由变化，重新获取未读消息数')
          this.fetchUnreadCount()
          this.fetchMessages()
        },
        immediate: false
      }
    },
  created() {
		  if(!this.showUser){
			  this.getRole()
		  }
		  const topic_info = window.localStorage.getItem('topic_info')
		  this.$watch('$route', this.updateDefaultPath, { immediate: true })

		  if (topic_info){
		  	this.topicValue = JSON.parse(topic_info).name
		  }
		  this.fetchUnreadCount()
		  this.connectWebSocket()
		  // 恢复侧栏折叠状态并同步 html 属性
		  try {
		  	if (localStorage.getItem('qm-sidebar-collapsed') === '1') this.isCollapse = true
		  } catch(e) {}
		  document.documentElement.setAttribute('data-sidebar', this.isCollapse ? 'collapsed' : 'expanded')
	  },
	  beforeUnmount() {
		  this.stopMessageRefresh()
		  this.disconnectWebSocket()
	  }
}
</script>

<style scoped>
	/* 主容器 */
	.menu-container {
		position: relative;
		width: 100%;
		height: 69px;
		background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		z-index: 1000;
	}
	
	/* 主菜单 */
	.main-menu {
		height: 69px;
		display: flex;
		align-items: center;
		padding: 0 20px;
		border-bottom: none;
		background: transparent !important;
	}
	
	/* Logo区域 - 更新为新Logo样式 */
	.logo-area {
		width: 190px;
		height: 64px;
		padding: 0 !important;
		margin-right: 0px;
		background: transparent !important;
	}
	
	.logo-area:hover {
		background: transparent !important;
	}
	
	.logo-container {
		display: flex;
		align-items: center;
		width: 100%;
		height: 100%;
		padding: 0;
		gap: 12px;
	}
	
	/* 新的Logo样式 */
	.logo-circle {
		position: relative;
		width: 40px;
		height: 40px;
		flex-shrink: 0;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	
	.logo-icon {
		width: 100%;
		height: 100%;
		filter: drop-shadow(0 0 15px rgba(245, 158, 11, 0.5));
		animation: logoFloat 6s ease-in-out infinite;
	}
	
	.logo-hexagon {
		fill: none;
		stroke: #f59e0b;
		stroke-width: 4;
		stroke-linecap: round;
		stroke-linejoin: round;
		animation: hexagonPulse 3s ease-in-out infinite;
	}
	
	.logo-center {
		fill: #f59e0b;
		opacity: 0.8;
		animation: centerPulse 2s ease-in-out infinite;
	}
	
	.logo-square {
		fill: rgba(255, 255, 255, 0.9);
	}
	
	.logo-glow {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		border-radius: 50%;
		background: radial-gradient(circle, rgba(245, 158, 11, 0.3) 0%, transparent 70%);
		animation: glowPulse 4s ease-in-out infinite;
		z-index: -1;
	}
	
	/* 平台信息 - 优化垂直布局 */
	.platform-info {
		display: flex;
		flex-direction: column;
		justify-content: center;
		gap: 2px;
		max-width: 120px;
		height: 100%;
	}
	
	.platform-name {
		font-size: 15px;
		font-weight: 500;
		color: var(--qm-text-1, #1f2937);
		margin: 0;
		letter-spacing: 0;
		line-height: 1.3;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 150px;
		text-align: left;
		padding-bottom: 0;
	}
	
	.platform-slogan-container {
		display: flex;
		align-items: flex-start;
		height: 16px;
	}
	
	.platform-slogan {
		color: var(--qm-text-3, #9ca3af);
		font-size: 11px;
		margin: 0;
		font-weight: 400;
		letter-spacing: 0.5px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 140px;
		text-align: left;
		line-height: 1;
	}
	
	/* Logo动画 */
	@keyframes logoFloat {
		0%, 100% { transform: translateY(0) rotate(0deg); }
		25% { transform: translateY(-3px) rotate(2deg); }
		75% { transform: translateY(2px) rotate(-2deg); }
	}
	
	@keyframes hexagonPulse {
		0%, 100% { stroke-width: 4; }
		50% { stroke-width: 5; }
	}
	
	@keyframes centerPulse {
		0%, 100% { opacity: 0.8; r: 20; }
		50% { opacity: 1; r: 21; }
	}
	
	@keyframes glowPulse {
		0%, 100% { opacity: 0.3; transform: scale(1); }
		50% { opacity: 0.5; transform: scale(1.05); }
	}
	
	/* 菜单项（垂直侧栏适配） */
	.menu-item {
		height: 42px;
		display: flex;
		align-items: center;
		padding: 0 14px;
		margin: 2px 8px;
		border-radius: 8px;
		transition: all 0.2s ease;
		border-bottom: none;
		background: transparent !important;
	}

	.menu-item:hover {
		background: var(--qm-bg-3, #f1f5f9) !important;
		border-bottom-color: transparent;
		transform: none;
	}

	.menu-item.is-active {
		border-bottom-color: transparent;
		background: var(--qm-accent-soft, rgba(245, 158, 11, 0.12)) !important;
	}

	.menu-icon {
		margin-right: 10px;
		font-size: 17px;
		color: var(--qm-text-3, #9ca3af);
	}

	.menu-text {
		font-size: 14px;
		font-weight: 400;
		letter-spacing: 0;
		color: var(--qm-text-2, #4b5563);
	}

	.menu-item.is-active .menu-text,
	.menu-item.is-active .menu-icon {
		color: var(--qm-accent-strong, #b45309);
		font-weight: 500;
	}
	
	/* 我的项目特殊样式 */
	.my-project-item {
		position: relative;
		overflow: hidden;
	}
	
	.my-project-item::before {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.15), transparent);
		transition: left 0.6s;
	}
	
	.my-project-item:hover::before {
		left: 100%;
	}
	
	.my-project-item .menu-icon {
		color: var(--qm-accent, #f59e0b);
	}

	/* 子菜单（垂直侧栏适配）
	   注意：el-sub-menu 的 li 绝不能设 display:flex —— 会把标题和
	   子菜单 ul 排成一行，子菜单被挤出侧栏外（表现为"展不开/被遮挡"） */
	.sub-menu {
		background: transparent !important;
	}

	:deep(.el-sub-menu__title) {
		height: 42px !important;
		line-height: 42px;
		margin: 2px 8px;
		border-radius: 8px;
		background: transparent !important;
		color: var(--qm-text-2, #4b5563) !important;
	}

	:deep(.el-sub-menu__title:hover) {
		background: var(--qm-bg-3, #f1f5f9) !important;
		color: var(--qm-text-1, #1f2937) !important;
	}
	
	/* 子菜单项 */
	.sub-menu-item {
		max-width: 180px;
		transition: all 0.3s ease;
	}
	
	.sub-menu-icon {
		margin-right: 10px;
		font-size: 16px;
	}
	
	.sub-menu-text {
		font-size: 14px;
	}
	
	/* 右侧工具栏 */
	.right-toolbar {
		position: absolute;
		right: 24px;
		top: 0;
		height: 64px;
		display: flex;
		align-items: center;
		gap: 18px;
	}
	
	.toolbar-item {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 34px;
		height: 34px;
		border-radius: 8px;
		background: transparent;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.toolbar-item:hover {
		background: var(--qm-bg-3, #f1f5f9);
		transform: none;
		box-shadow: none;
	}

	.toolbar-icon {
		font-size: 17px;
		color: var(--qm-text-2, #4b5563);
	}
	
	/* 用户下拉菜单 */
	.user-dropdown {
		cursor: pointer;
	}
	
	.user-info {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 5px 10px;
		border-radius: 8px;
		transition: all 0.2s ease;
		border: 1px solid transparent;
		background: transparent;
	}

	.user-info:hover {
		background: var(--qm-bg-3, #f1f5f9);
		border-color: var(--qm-line, rgba(15,23,42,.08));
		box-shadow: none;
	}

	.user-avatar {
		flex-shrink: 0;
		font-weight: 500;
		color: #fff;
		background: var(--qm-accent, #f59e0b);
		box-shadow: none;
		transition: transform 0.2s ease;
	}

	.user-info:hover .user-avatar {
		transform: none;
	}

	.user-details {
		display: flex;
		align-items: center;
		gap: 6px;
	}

	.user-name {
		font-size: 13px;
		font-weight: 400;
		max-width: 96px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		color: var(--qm-text-1, #1f2937);
	}

	.dropdown-arrow {
		font-size: 12px;
		color: var(--qm-text-3, #9ca3af);
		transition: transform 0.2s ease;
	}

	.user-dropdown:hover .dropdown-arrow {
		transform: rotate(180deg);
		color: var(--qm-accent, #f59e0b);
	}
	
	/* 下拉菜单 */
	.user-dropdown-menu {
		margin-top: 0px;
		min-width: 160px;
		border-radius: 12px;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
		border: 1px solid rgba(255, 255, 255, 0.1);
		background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
		overflow: hidden;
	}
	
	.user-dropdown-menu span {
		color: rgba(255, 255, 255, 0.9);
	}
	
	.dropdown-item {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 10px 20px;
		font-size: 14px;
		color: rgba(255, 255, 255, 0.9);
		transition: all 0.3s ease;
		border-radius: 4px;
		margin: 4px 8px;
		width: auto;
	}
	
	/* 修复下拉项悬浮颜色问题 */
	:deep(.el-dropdown-menu__item):hover {
		background-color: rgba(245, 158, 11, 0.2) !important;
		color: white !important;
	}
	
	:deep(.el-dropdown-menu__item) .el-icon {
		color: rgba(255, 255, 255, 0.8);
	}
	
	:deep(.el-dropdown-menu__item):hover .el-icon {
		color: white !important;
	}
	
	:deep(.el-dropdown-menu__item).logout:hover {
		background-color: rgba(245, 108, 108, 0.2) !important;
		color: #f56c6c !important;
	}
	
	:deep(.el-dropdown-menu__item).logout:hover .el-icon {
		color: #f56c6c !important;
	}
	
	.dropdown-item.logout:hover {
		background: rgba(245, 108, 108, 0.1) !important;
		color: #f56c6c !important;
	}
	
	.dropdown-item .el-icon {
		font-size: 16px;
	}
	
	/* 对话框样式优化 */
	.password-dialog :deep(.el-dialog) {
		border-radius: 16px;
		overflow: hidden;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		background: linear-gradient(135deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
		border: 1px solid rgba(255, 255, 255, 0.2);
	}
	
	.password-dialog :deep(.el-dialog__header) {
		padding: 20px 20px 10px;
		border-bottom: 1px solid var(--qm-line);
		background: linear-gradient(180deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
	}
	
	.password-dialog :deep(.el-dialog__title) {
		font-size: 18px;
		font-weight: 700;
		color: var(--qm-text-1);
	}
	
	.password-dialog :deep(.el-dialog__body) {
		padding: 20px;
	}
	
	.password-dialog :deep(.el-form-item__label) {
		font-size: 14px;
		font-weight: 600;
		color: var(--qm-text-2);
		margin-bottom: 8px;
	}
	
	.password-input :deep(.el-input__wrapper) {
		border-radius: 10px;
		border: 2px solid var(--qm-line-strong);
		background: var(--qm-bg-2);
		padding: 0 16px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
		transition: all 0.3s ease;
	}
	
	.password-input :deep(.el-input__wrapper:hover) {
		border-color: var(--qm-line-strong);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
	}
	
	.password-input :deep(.el-input__wrapper.is-focus) {
		border-color: #f59e0b;
		box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
	}
	
	.dialog-footer {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 12px;
		padding-top: 20px;
	}
	
	.password-dialog .dialog-footer .el-button {
		padding: 10px 24px;
		border-radius: 10px;
		font-weight: 500;
	}
	
	.password-dialog .dialog-footer .el-button--primary {
		background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
		border: none;
		transition: all 0.3s ease;
	}
	
	.password-dialog .dialog-footer .el-button--primary:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 20px rgba(245, 158, 11, 0.4);
	}
	
	/* 响应式调整 */
	@media (max-width: 1200px) {
		.user-name {
			max-width: 100px;
		}
		
		.logo-area {
			width: 170px;
			margin-right: 20px;
		}
		
		.platform-name {
			font-size: 16px;
			max-width: 120px;
		}
		
		.platform-slogan {
			font-size: 10px;
			max-width: 120px;
		}
	}
	
	@media (max-width: 992px) {
		.menu-item {
			padding: 0 16px;
		}
		
		.logo-area {
			width: 150px;
		}
		
		.platform-name {
			font-size: 15px;
			max-width: 100px;
		}
		
		.platform-slogan {
			display: none;
		}
		
		.platform-slogan-container {
			display: none;
		}
		
		.logo-circle {
			width: 35px;
			height: 35px;
		}
		
		.right-toolbar {
			right: 15px;
			gap: 12px;
		}
		
		.user-info {
			padding: 6px 10px;
		}
		
		.user-name {
			max-width: 80px;
		}
	}
	
	@media (max-width: 768px) {
		.menu-container {
			height: 60px;
		}
		
		.main-menu {
			height: 60px;
			padding: 0 10px;
		}
		
		.menu-item {
			height: 60px;
			padding: 0 12px;
		}
		
		.logo-area {
			width: 130px;
			margin-right: 10px;
		}
		
		.platform-info {
			display: none;
		}
		
		.menu-text {
			font-size: 14px;
		}
		
		.user-name {
			display: none;
		}
		
		.user-info {
			padding: 5px;
		}
		
		.toolbar-item {
			width: 36px;
			height: 36px;
		}
	}
	
	/* 深色模式适配 */
	:deep(.el-menu--horizontal) .el-sub-menu .el-sub-menu__title:hover {
		background: rgba(255, 255, 255, 0.08) !important;
	}
	
	:deep(.el-menu--horizontal) .el-menu-item:not(.is-disabled):hover {
		background: rgba(255, 255, 255, 0.08) !important;
	}
	
	:deep(.el-dropdown-menu__item) {
		padding: 10px 20px;
		color: rgba(255, 255, 255, 0.9);
	}
	
	:deep(.el-dialog__header) {
		padding: 20px 20px 10px;
		border-bottom: 1px solid var(--qm-line);
	}
	
	:deep(.el-dialog__body) {
		padding: 20px;
	}

	/* ============================================================
	   Q·M 重构布局：左侧导航 + 顶栏
	   ============================================================ */
	.qm-shell {
		--qm-sidebar-w: 220px;
	}

	/* ---- 侧边栏 ---- */
	.qm-sidebar {
		position: fixed;
		left: 0;
		top: 0;
		bottom: 0;
		width: var(--qm-sidebar-w);
		display: flex;
		flex-direction: column;
		background: var(--qm-bg-2, #fff);
		border-right: 1px solid var(--qm-line, rgba(15,23,42,.08));
		z-index: 1001;
		transition: width .25s ease;
	}
	.qm-sidebar.is-collapsed {
		--qm-sidebar-w: 64px;
		width: 64px;
	}

	.sidebar-logo {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 14px 16px;
		cursor: pointer;
		border-bottom: 1px solid var(--qm-line, rgba(15,23,42,.08));
		min-height: 64px;
		box-sizing: border-box;
		overflow: hidden;
	}
	.sidebar-logo .logo-circle {
		position: relative;
		width: 34px;
		height: 34px;
		flex-shrink: 0;
		border-radius: 9px;
		background: var(--qm-accent, #f59e0b);
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.sidebar-logo .logo-icon {
		width: 20px;
		height: 20px;
	}
	.sidebar-logo .logo-hexagon { fill: none; stroke: rgba(255,255,255,.9); stroke-width: 6; }
	.sidebar-logo .logo-center { fill: rgba(255,255,255,.9); }
	.sidebar-logo .logo-square { fill: var(--qm-accent, #f59e0b); }
	.sidebar-logo .logo-glow { display: none; }
	.sidebar-logo-text { min-width: 0; }
	.sidebar-logo-text .platform-name {
		font-size: 15px;
		font-weight: 500;
		color: var(--qm-text-1, #1f2937);
		margin: 0;
		white-space: nowrap;
		line-height: 1.3;
	}
	.sidebar-logo-text .platform-slogan {
		font-size: 11px;
		color: var(--qm-text-3, #9ca3af);
		margin: 0;
		white-space: nowrap;
		line-height: 1.4;
	}

	.sidebar-scroll {
		flex: 1;
		overflow: hidden;
	}

	/* 垂直菜单 */
	.sidebar-menu {
		border-right: none !important;
		background: transparent !important;
		width: 100% !important;
	}
	.qm-sidebar.is-collapsed .sidebar-menu {
		width: 64px !important;
	}
	.sidebar-menu :deep(.el-menu-item) {
		height: 42px;
		line-height: 42px;
		margin: 2px 8px;
		border-radius: 8px;
		color: var(--qm-text-2, #4b5563);
		background: transparent !important;
	}
	.sidebar-menu :deep(.el-menu-item:hover) {
		background: var(--qm-bg-3, #f1f5f9) !important;
		color: var(--qm-text-1, #1f2937);
	}
	.sidebar-menu :deep(.el-menu-item.is-active) {
		background: var(--qm-accent-soft, rgba(245,158,11,.12)) !important;
		color: var(--qm-accent-strong, #b45309) !important;
		font-weight: 500;
	}
	.sidebar-menu :deep(.el-sub-menu__title) {
		height: 42px;
		line-height: 42px;
		margin: 2px 8px;
		border-radius: 8px;
		color: var(--qm-text-2, #4b5563);
		background: transparent !important;
	}
	.sidebar-menu :deep(.el-sub-menu__title:hover) {
		background: var(--qm-bg-3, #f1f5f9) !important;
		color: var(--qm-text-1, #1f2937);
	}
	.sidebar-menu :deep(.el-sub-menu .el-menu-item) {
		padding-left: 44px !important;
	}
	.sidebar-menu :deep(.el-menu-item .el-icon),
	.sidebar-menu :deep(.el-sub-menu__title .el-icon) {
		color: inherit;
	}

	/* 折叠按钮 */
	.sidebar-footer {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 12px 18px;
		border-top: 1px solid var(--qm-line, rgba(15,23,42,.08));
		cursor: pointer;
		color: var(--qm-text-3, #9ca3af);
		user-select: none;
	}
	.sidebar-footer:hover {
		color: var(--qm-accent, #f59e0b);
	}
	.qm-sidebar.is-collapsed .sidebar-footer {
		justify-content: center;
		padding: 12px 0;
	}
	.collapse-text { font-size: 12px; white-space: nowrap; }

	/* ---- 顶栏 ---- */
	.qm-topbar {
		position: fixed;
		left: var(--qm-sidebar-w, 220px);
		right: 0;
		top: 0;
		height: 56px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0 20px;
		background: var(--qm-bg-2, #fff);
		border-bottom: 1px solid var(--qm-line, rgba(15,23,42,.08));
		z-index: 1000;
		transition: left .25s ease;
	}
	.qm-sidebar.is-collapsed ~ .qm-topbar {
		left: 64px;
	}

	.topbar-title {
		font-size: 15px;
		font-weight: 500;
		color: var(--qm-text-1, #1f2937);
	}

	.topbar-actions {
		display: flex;
		align-items: center;
		gap: 4px;
	}
	.toolbar-item {
		width: 34px;
		height: 34px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 8px;
		cursor: pointer;
		color: var(--qm-text-2, #4b5563);
	}
	.toolbar-item:hover {
		background: var(--qm-bg-3, #f1f5f9);
		color: var(--qm-accent, #f59e0b);
	}
	.toolbar-icon { font-size: 17px; }

	/* 用户信息 */
	.user-dropdown { cursor: pointer; }
	.user-info {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 4px 8px;
		border-radius: 8px;
	}
	.user-info:hover { background: var(--qm-bg-3, #f1f5f9); }
	.user-avatar { background: var(--qm-accent, #f59e0b); color: #fff; font-weight: 500; }
	.user-details { display: flex; align-items: center; gap: 4px; }
	.user-name {
		font-size: 13px;
		color: var(--qm-text-1, #1f2937);
		max-width: 96px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.dropdown-arrow { font-size: 12px; color: var(--qm-text-3, #9ca3af); }

</style>

<style>
	/* 自定义子菜单弹出框样式 - 与用户下拉菜单保持一致 */
	.custom-submenu-popup {
		border-radius: 12px !important;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
		border: 1px solid rgba(255, 255, 255, 0.1) !important;
		background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
		overflow: hidden !important;
		padding: 0 !important;
		margin-top: 0px !important;
	}
	
	.custom-submenu-popup .el-menu {
		background: transparent !important;
		border: none !important;
		padding: 0 !important;
	}
	
	.custom-submenu-popup .el-menu-item {
		display: flex !important;
		align-items: center !important;
		gap: 12px !important;
		padding: 12px 20px !important;
		font-size: 14px !important;
		color: rgba(255, 255, 255, 0.9) !important;
		transition: all 0.3s ease !important;
		margin: 0 !important;
		width: 100% !important;
		height: auto !important;
		min-height: 44px !important;
		line-height: normal !important;
		box-sizing: border-box !important;
		position: relative !important;
		/* 添加明显的底部边框 */
		border-bottom: 1px solid rgba(255, 255, 255, 0.15) !important;
	}
	
	/* 最后一个菜单项去掉底部边框 */
	.custom-submenu-popup .el-menu-item:last-child {
		border-bottom: none !important;
	}
	
	/* 鼠标悬停时的底部边框颜色变化 */
	.custom-submenu-popup .el-menu-item:hover {
		border-bottom-color: rgba(245, 158, 11, 0.5) !important;
	}
	
	/* 激活状态的底部边框 */
	.custom-submenu-popup .el-menu-item.is-active {
		border-bottom-color: #f59e0b !important;
	}
	
	.custom-submenu-popup .el-menu-item .el-icon {
		font-size: 16px !important;
		color: rgba(255, 255, 255, 0.8) !important;
		margin-right: 10px !important;
		width: 20px !important;
		height: 20px !important;
	}
	
	.custom-submenu-popup .el-menu-item:hover {
		background-color: rgba(245, 158, 11, 0.2) !important;
		color: white !important;
	}
	
	.custom-submenu-popup .el-menu-item:hover .el-icon {
		color: white !important;
	}
	
	.custom-submenu-popup .el-menu-item.is-active {
		background-color: rgba(245, 158, 11, 0.3) !important;
		color: white !important;
	}
	
	.custom-submenu-popup .el-menu-item.is-active .el-icon {
		color: white !important;
	}
	
	/* 菜单项之间的间隔效果 - 通过边框实现 */
	.custom-submenu-popup .el-menu-item:not(:last-child)::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 20px;
		right: 20px;
		height: 1px;
		background: linear-gradient(90deg, 
			rgba(255, 255, 255, 0) 0%, 
			rgba(255, 255, 255, 0.2) 20%, 
			rgba(255, 255, 255, 0.2) 80%, 
			rgba(255, 255, 255, 0) 100%) !important;
	}
	
	/* 确保箭头图标正确显示 */
	.custom-submenu-popup .el-sub-menu__icon-arrow {
		color: rgba(255, 255, 255, 0.7) !important;
		margin-top: -8px !important;
	}
	
	/* 修复子菜单的下拉菜单样式 */
	.custom-submenu-popup .el-menu--popup {
		min-width: 160px !important;
	}
	
	/* 二级子菜单样式 */
	.custom-submenu-popup .el-menu--popup .custom-submenu-popup {
		margin-left: 4px !important;
		margin-top: -8px !important;
	}
	
	/* 增强用户下拉菜单项的底部边框 */
	.user-dropdown-menu .el-dropdown-menu__item {
		position: relative;
		border-bottom: 1px solid rgba(255, 255, 255, 0.15) !important;
	}
	
	.user-dropdown-menu .el-dropdown-menu__item:last-child {
		border-bottom: none !important;
	}
	
	.user-dropdown-menu .el-dropdown-menu__item:hover {
		border-bottom-color: rgba(245, 158, 11, 0.5) !important;
	}
	
	.user-dropdown-menu .el-dropdown-menu__item.logout:hover {
		border-bottom-color: rgba(245, 108, 108, 0.5) !important;
	}
	
	/* 修改用户头像下拉菜单文字居中显示 */
	.user-dropdown-menu .el-dropdown-menu__item {
		display: flex !important;
		justify-content: center !important; /* 水平居中 */
		align-items: center !important; /* 垂直居中 */
		text-align: center !important; /* 文本居中 */
	}
	
	.user-dropdown-menu .el-dropdown-menu__item .el-icon {
		position: absolute !important; /* 图标绝对定位 */
		left: 20px !important; /* 图标距离左边20px */
		top: 50% !important;
		transform: translateY(-50%) !important; /* 垂直居中 */
		margin-right: 0 !important; /* 移除原来的右边距 */
	}
	
	.user-dropdown-menu .el-dropdown-menu__item span {
		display: block !important;
		width: 100% !important;
		text-align: center !important;
		padding-left: 24px !important; /* 为图标留出空间 */
		padding-right: 24px !important; /* 对称 */
	}
	
	/* 确保退出登录项也居中 */
	.user-dropdown-menu .el-dropdown-menu__item.logout {
		display: flex !important;
		justify-content: center !important;
		align-items: center !important;
		text-align: center !important;
	}
	
	.user-dropdown-menu .el-dropdown-menu__item.logout .el-icon {
		position: absolute !important;
		left: 20px !important;
		top: 50% !important;
		transform: translateY(-50%) !important;
		margin-right: 0 !important;
	}
	
	.user-dropdown-menu .el-dropdown-menu__item.logout span {
		display: block !important;
		width: 100% !important;
		text-align: center !important;
		padding-left: 24px !important;
		padding-right: 24px !important;
	}
	
	/* 使用深度选择器来覆盖element-plus样式 */
	 .password-dialog.el-dialog {
	   border-radius: 12px !important;
	 }
	 
	/* 消息通知弹窗样式 */
	.message-dialog .el-dialog__body {
		padding: 0 20px 20px;
	}

	.message-dialog-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: 100%;
	}

	.message-dialog-title {
		font-size: 18px;
		font-weight: 700;
		color: var(--qm-text-1);
		padding-left: 12px;
		position: relative;
	}

	.message-dialog-title::before {
		content: '';
		position: absolute;
		left: 0;
		top: 50%;
		transform: translateY(-50%);
		width: 4px;
		height: 20px;
		background: linear-gradient(180deg, #f59e0b 0%, #f97316 100%);
		border-radius: 2px;
	}

	.message-tab-list {
		max-height: 450px;
		overflow-y: auto;
	}

	.message-tab-list::-webkit-scrollbar {
		width: 6px;
	}

	.message-tab-list::-webkit-scrollbar-track {
		background: transparent;
	}

	.message-tab-list::-webkit-scrollbar-thumb {
		background: var(--qm-line-strong);
		border-radius: 3px;
	}

	.message-tab-list::-webkit-scrollbar-thumb:hover {
		background: var(--qm-text-3);
	}

	.message-empty {
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 40px 0;
	}

	.message-item {
		display: flex;
		align-items: flex-start;
		padding: 14px 16px;
		border-bottom: 1px solid #f0f0f0;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.message-item:hover {
		background-color: var(--qm-bg-1);
	}

	.message-item.unread {
		background-color: #f0f4ff;
	}

	.message-item.unread:hover {
		background-color: #e6edff;
	}

	.message-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background-color: #f59e0b;
		margin-top: 6px;
		margin-right: 12px;
		flex-shrink: 0;
	}

	.message-content {
		flex: 1;
		min-width: 0;
	}

	.message-title {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-bottom: 4px;
	}

	.message-title-text {
		font-size: 14px;
		font-weight: 500;
		color: #333;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.message-text {
		font-size: 13px;
		color: #666;
		line-height: 1.5;
		margin-bottom: 4px;
	}

	.message-time {
		font-size: 12px;
		color: #999;
	}

	.message-delete-icon {
		flex-shrink: 0;
		margin-left: 8px;
		color: #c0c4cc;
		cursor: pointer;
		font-size: 16px;
		transition: color 0.2s;
	}

	.message-delete-icon:hover {
		color: #f56c6c;
	}

	/* 任务消息卡片样式 */
	.task-message-item {
		flex-direction: column;
		align-items: stretch;
		padding: 14px 16px;
		gap: 0;
	}

	.task-message-item > .message-dot {
		position: absolute;
		top: 14px;
		left: 16px;
	}

	.task-message-item {
		position: relative;
		padding-left: 28px;
		padding-right: 36px;
	}

	.task-message-item > .message-delete-icon {
		position: absolute;
		top: 14px;
		right: 16px;
		margin-left: 0;
	}

	.task-status-tag {
		margin-left: 8px;
		flex-shrink: 0;
		width: fit-content;
		align-self: center;
	}

	.task-stats-row {
		display: flex;
		align-items: center;
		gap: 6px;
		margin-top: 10px;
		margin-bottom: 8px;
		flex-wrap: wrap;
	}

	.task-stat-item {
		display: inline-flex;
		align-items: center;
		gap: 3px;
		padding: 2px 8px;
		border-radius: 5px;
		font-size: 11px;
		font-weight: 500;
	}

	.task-stat-item .stat-label {
		font-weight: 500;
	}

	.task-stat-item .stat-value {
		font-weight: 600;
	}

	.task-stat-item.stat-total {
		background: var(--qm-warning-soft);
		color: #d97706;
	}

	.task-stat-item.stat-total .stat-label {
		color: #d97706;
	}

	.task-stat-item.stat-total .stat-value {
		color: #b45309;
	}

	.task-stat-item.stat-success {
		background: #ecfdf5;
		color: #047857;
	}

	.task-stat-item.stat-success .stat-label {
		color: #047857;
	}

	.task-stat-item.stat-success .stat-value {
		color: #065f46;
	}

	.task-stat-item.stat-failed {
		background: var(--qm-red-soft);
		color: #b91c1c;
	}

	.task-stat-item.stat-failed .stat-label {
		color: #b91c1c;
	}

	.task-stat-item.stat-failed .stat-value {
		color: #991b1b;
	}

	.task-stat-item.stat-duration {
		background: #fefce8;
		color: #a16207;
	}

	.task-stat-item.stat-duration .stat-label {
		color: #a16207;
	}

	.task-stat-item.stat-duration .stat-value {
		color: #854d0e;
	}

	.message-meta {
		display: flex;
		align-items: center;
		gap: 12px;
		font-size: 12px;
		color: var(--qm-text-3);
	}

	.message-creator {
		color: var(--qm-text-3);
	}

	.message-pagination {
		display: flex;
		justify-content: flex-end;
		padding-top: 16px;
	}

	/* tab 未读数量徽章 */
	.tab-label-wrap {
		position: relative;
		display: inline-block;
	}

	.tab-unread-badge {
		position: absolute;
		top: 10px;
		right: -16px;
		transform: translateY(-50%);
		min-width: 18px;
		height: 18px;
		padding: 0 5px;
		font-size: 12px;
		color: #fff;
		background-color: #f56c6c;
		border: 1px solid var(--el-bg-color, #fff);
		border-radius: 10px;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		line-height: 1;
		box-sizing: border-box;
	}

	/* 消息弹窗 tabs 下划线 - 参考菜单 menu-item 样式 */
	.message-dialog .el-tabs__header {
		margin-bottom: 16px;
		border-bottom: 1px solid var(--qm-line-strong);
		overflow: visible !important;
	}

	.message-dialog .el-tabs__nav-wrap {
		overflow: visible !important;
	}

	.message-dialog .el-tabs__nav-scroll {
		overflow: visible !important;
	}

	.message-dialog .el-tabs__nav-wrap::after {
		display: none;
	}

	.message-dialog .el-tabs__item {
		position: relative;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		padding: 0;
		margin: 0 16px;
		height: 48px;
		line-height: 48px;
		font-size: 14px;
		color: var(--qm-text-2);
	}

	.message-dialog .el-tabs__item::after {
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

	.message-dialog .el-tabs__item:hover::after {
		width: 100%;
		background: rgba(245, 158, 11, 0.5);
	}

	.message-dialog .el-tabs__item.is-active::after {
		width: 100%;
		background: #f59e0b;
	}

	.message-dialog .el-tabs__item:hover {
		color: #f59e0b;
	}

	.message-dialog .el-tabs__item.is-active {
		color: #f59e0b;
		font-weight: 600;
	}

	.message-dialog .el-tabs__active-bar {
		display: none;
	}

	/* 分页样式 - 参考列表分页组件 */
	.elegant-pagination :deep(.el-pagination) {
		display: flex;
		align-items: center;
	}

	.elegant-pagination :deep(.el-pagination__total) {
		color: var(--qm-text-2);
		font-weight: 500;
		margin-right: 20px;
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

	.elegant-pagination :deep(.el-pager li:not(.disabled):hover) {
		color: #f59e0b;
		border-color: #f59e0b;
		background: var(--qm-bg-2);
	}

	.elegant-pagination :deep(.el-pager li.is-active) {
		background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
		color: white;
		border-color: transparent;
	}

	.elegant-pagination :deep(.btn-prev),
	.elegant-pagination :deep(.btn-next) {
		border-radius: 8px;
		border: 1px solid var(--qm-line-strong);
		background: var(--qm-bg-2);
		transition: all 0.3s ease;
		min-width: 36px;
		height: 36px;
		line-height: 36px;
	}

	.elegant-pagination :deep(.btn-prev:hover:not(.disabled)),
	.elegant-pagination :deep(.btn-next:hover:not(.disabled)) {
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
	
	.message-bell {
		position: relative;
	}
	
	.message-badge {
		display: flex;
		align-items: center;
	}

</style>