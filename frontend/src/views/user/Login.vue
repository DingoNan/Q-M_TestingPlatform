<template>
	<div class="login-page">
		<!-- 纯 CSS 几何背景装饰 -->
		<div class="bg-deco deco-1"></div>
		<div class="bg-deco deco-2"></div>
		<div class="bg-deco deco-3"></div>

		<div class="login-center">
			<div class="login-card">
				<!-- 品牌区 -->
				<div class="brand">
					<div class="brand-logo">
						<svg viewBox="0 0 100 100">
							<path d="M50,10 L90,30 L90,70 L50,90 L10,70 L10,30 Z" class="logo-hexagon"></path>
							<circle cx="50" cy="50" r="20" class="logo-center"></circle>
							<path d="M35,35 L65,35 L65,65 L35,65 Z" class="logo-square"></path>
						</svg>
					</div>
					<h1 class="brand-name">Q·M 测试平台</h1>
					<p class="brand-slogan">智能测试解决方案</p>
				</div>

				<!-- 错误提示 -->
				<div class="error-alert" v-if="loginError.show" :class="{shake: loginError.shake}">
					<div class="error-content">
						<el-icon class="error-icon"><Warning /></el-icon>
						<div class="error-text">
							<h4>{{ loginError.title }}</h4>
							<p>{{ loginError.message }}</p>
						</div>
						<el-icon class="close-icon" @click="dismissError"><Close /></el-icon>
					</div>
					<div class="error-progress" :style="{width: loginError.progress + '%'}"></div>
				</div>

				<!-- 登录表单 -->
				<el-form :model="loginForm" :rules="loginRules" ref='loginRef' class="login-form">
					<el-form-item prop="username">
						<div class="form-input" :class="{focused: focusedField === 'username', 'has-error': loginError.show}">
							<div class="input-icon">
								<el-icon><User /></el-icon>
							</div>
							<el-input
								v-model="loginForm.username"
								placeholder="请输入用户名"
								@focus="handleInputFocus('username')"
								@blur="focusedField = ''"
								@input="clearError">
							</el-input>
						</div>
					</el-form-item>

					<el-form-item prop="password">
						<div class="form-input" :class="{focused: focusedField === 'password', 'has-error': loginError.show}">
							<div class="input-icon">
								<el-icon><Lock /></el-icon>
							</div>
							<el-input
								v-model="loginForm.password"
								placeholder="请输入密码"
								type="password"
								show-password
								@focus="handleInputFocus('password')"
								@blur="focusedField = ''"
								@input="clearError">
							</el-input>
						</div>
					</el-form-item>

					<div class="form-options">
						<div class="remember-me">
							<el-switch
								v-model="loginForm.status"
								:active-color="switchColor"
								class="custom-switch">
							</el-switch>
							<span>记住登录状态</span>
						</div>

						<div class="forgot-password">
							<router-link class="forgot-link">忘记密码?</router-link>
						</div>
					</div>

					<el-form-item>
						<el-button
							type="primary"
							@click="login"
							class="login-btn"
							:loading="loading">
							<span v-if="!loading">立即登录</span>
							<span v-else>登录中...</span>
						</el-button>
					</el-form-item>

					<div class="login-footer">
						<p>还没有账号？</p>
						<router-link :to="{ name: 'register' }" class="nav-link">
							去注册
							<el-icon><ArrowRight /></el-icon>
						</router-link>
					</div>
				</el-form>
			</div>

			<!-- 页脚状态 -->
			<div class="page-foot">
				<span class="status-dot"></span>
				<span>平台运行中 · 在线 {{ onlineUsers }} 人</span>
				<span class="foot-sep">|</span>
				<span>© 2025 Q·M 测试平台</span>
			</div>
		</div>
	</div>
</template>

<script type='text/javascript'>
import api from '../../api/index.js'
import {mapMutations} from 'vuex'
import { ElMessage } from 'element-plus'
import { User, Lock, ArrowRight, Warning, Close } from '@element-plus/icons-vue'

export default {
	name: 'LoginPage',
	components: {
		User,
		Lock,
		ArrowRight,
		Warning,
		Close
	},
	data() {
		return {
			loading: false,
			hoverBtn: false,
			focusedField: '',
			activeFeature: '',
			onlineUsers: 124,
			switchColor: '#f59e0b',
			role_permissions: '',
			loginError: {
				show: false,
				title: '',
				message: '',
				shake: false,
				progress: 100,
				timer: null
			},
			loginForm: {
				username: '',
				password: '',
				status: false
			},
			loginRules: {
				username: [{
					required: true,
					message: '请输入用户名',
					trigger: 'blur',
				}],
				password: [{
					required: true,
					message: '',
					trigger: 'blur',
				}],
			},
			flowLines: [],
			particles: [],
			floatElements: []
		}
	},
	mounted() {
		// 聚焦单栏新版登录页：仅保留在线人数获取（canvas/浮动动画已随旧布局移除）
		this.updateOnlineUsers();
	},
	methods: {
		async getUser(id){
			const response = await this.$api.getUser(id)
			if(response.status === 200){
				this.role_permissions = response.data.result.role_info.role_permissions
			}
		},
		toNavagation(){
			this.$router.push({name: 'navigation'})
		},
		openHelp(){
			// window.open('/#/user/help', '_blank');
			const routeData = this.$router.resolve({ name: 'help' });
			window.open(routeData.href, '_blank');
		},
		async login(){
			// 清除之前的错误提示
			this.clearError();
			
			this.$refs['loginRef'].validate(async (valid, fields)=>{
				if(valid){
					this.loading = true
					try {
						const response = await api.loginApi(this.loginForm)
						if (response.status === 200){
							window.localStorage.setItem('token', JSON.stringify(response.data.result.token_access))
							this.$store.commit('saveUserInfo', response.data.result)
							// 登录成功 - 使用Toast提示
							ElMessage({
								message: '登录成功，欢迎使用 Q·M 测试平台',
								type: 'success',
								duration: 2000
							})
							
							// 立即跳转，不使用延时
							this.$router.push({name: 'myProject'})
						}else{
							// 登录失败 - 显示页面内错误提示
							this.showErrorMessage(
								'登录失败', 
								response.data?.message || '账号或密码错误，请重试'
							);
						}
					} catch (error) {
						// 网络错误或其他异常
						this.showErrorMessage(
							'登录失败', 
							error.response?.data?.message || '网络连接异常，请检查网络后重试'
						);
					} finally {
						this.loading = false
					}
				} else {
					// 表单验证失败
					const firstError = Object.keys(fields)[0];
					let message = '请正确填写表单信息';
					
					if (firstError === 'username') {
						message = '请输入有效的用户名';
					} else if (firstError === 'password') {
						message = '请输入有效的密码';
					}
					
					this.showErrorMessage('表单验证失败', message);
					this.loading = false;
				}
			})
		},
		// 显示错误消息
		showErrorMessage(title, message) {
			// 清除之前的定时器
			if (this.loginError.timer) {
				clearInterval(this.loginError.timer);
			}
			
			this.loginError = {
				show: true,
				title: title,
				message: message,
				shake: true,
				progress: 100,
				timer: null
			};
			
			// 移除抖动效果
			setTimeout(() => {
				this.loginError.shake = false;
			}, 500);
			
			// 设置进度条递减
			this.loginError.timer = setInterval(() => {
				if (this.loginError.progress > 0) {
					this.loginError.progress -= 0.5;
				} else {
					clearInterval(this.loginError.timer);
					this.loginError.show = false;
				}
			}, 50);
			
			// 5秒后自动关闭
			setTimeout(() => {
				if (this.loginError.show) {
					this.clearError();
				}
			}, 5000);
		},
		// 清除错误提示
		clearError() {
			if (this.loginError.timer) {
				clearInterval(this.loginError.timer);
			}
			this.loginError = {
				show: false,
				title: '',
				message: '',
				shake: false,
				progress: 100,
				timer: null
			};
		},
		// 手动关闭错误提示
		dismissError() {
			this.clearError();
		},
		// 输入框获取焦点
		handleInputFocus(field) {
			this.focusedField = field;
			// 如果当前有错误提示，清除它
			if (this.loginError.show) {
				this.clearError();
			}
		},
		// 初始化浮动元素
		initFloatElements() {
			this.floatElements = [
				{ type: 'api', x: 10, y: 20, dx: 0.3, dy: 0.2 },
				{ type: 'ui', x: 15, y: 60, dx: -0.2, dy: 0.3 },
				{ type: 'performance', x: 85, y: 30, dx: -0.3, dy: -0.1 },
				{ type: 'mock', x: 90, y: 70, dx: 0.1, dy: -0.2 }
			];
		},
		initCanvasEffects() {
			this.initFlowLines();
			this.initParticles();
			this.animate();
		},
		initFlowLines() {
			const canvas = this.$refs.flowCanvas;
			if (!canvas) return;
			
			canvas.width = canvas.parentElement.offsetWidth;
			canvas.height = canvas.parentElement.offsetHeight;
			
			for (let i = 0; i < 15; i++) {
				this.flowLines.push({
					x: Math.random() * canvas.width,
					y: Math.random() * canvas.height,
					length: Math.random() * 200 + 100,
					speed: Math.random() * 2 + 1,
					width: Math.random() * 2 + 0.5,
					color: `rgba(245, 158, 11, ${Math.random() * 0.3 + 0.1})`,
					direction: Math.random() > 0.5 ? 1 : -1
				});
			}
		},
		initParticles() {
			const canvas = this.$refs.particleCanvas;
			if (!canvas) return;
			
			canvas.width = window.innerWidth;
			canvas.height = window.innerHeight;
			
			for (let i = 0; i < 80; i++) {
				this.particles.push({
					x: Math.random() * canvas.width,
					y: Math.random() * canvas.height,
					size: Math.random() * 3 + 1,
					speedX: Math.random() * 0.5 - 0.25,
					speedY: Math.random() * 0.5 - 0.25,
					color: `rgba(255, 255, 255, ${Math.random() * 0.3 + 0.1})`,
					opacity: Math.random() * 0.5 + 0.2
				});
			}
		},
		animate() {
			this.drawFlowLines();
			this.drawParticles();
			requestAnimationFrame(this.animate);
		},
		drawFlowLines() {
			const canvas = this.$refs.flowCanvas;
			if (!canvas) return;
			
			const ctx = canvas.getContext('2d');
			ctx.clearRect(0, 0, canvas.width, canvas.height);
			
			this.flowLines.forEach(line => {
				ctx.beginPath();
				ctx.moveTo(line.x, line.y);
				ctx.lineTo(line.x + line.length * line.direction, line.y);
				ctx.strokeStyle = line.color;
				ctx.lineWidth = line.width;
				ctx.stroke();
				
				line.x += line.speed * line.direction;
				
				if (line.direction > 0 && line.x > canvas.width + line.length) {
					line.x = -line.length;
				} else if (line.direction < 0 && line.x < -line.length) {
					line.x = canvas.width + line.length;
				}
			});
		},
		drawParticles() {
			const canvas = this.$refs.particleCanvas;
			if (!canvas) return;
			
			const ctx = canvas.getContext('2d');
			ctx.clearRect(0, 0, canvas.width, canvas.height);
			
			this.particles.forEach(particle => {
				ctx.beginPath();
				ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
				ctx.fillStyle = particle.color;
				ctx.globalAlpha = particle.opacity;
				ctx.fill();
				
				particle.x += particle.speedX;
				particle.y += particle.speedY;
				
				if (particle.x < 0 || particle.x > canvas.width) particle.speedX *= -1;
				if (particle.y < 0 || particle.y > canvas.height) particle.speedY *= -1;
			});
		},
		startAnimations() {
			// 浮动元素动画
			this.floatAnimation();
			
			// 随机移动动画
			setInterval(() => {
				document.querySelectorAll('.float-element').forEach(el => {
					const randomX = Math.random() * 10 - 5;
					const randomY = Math.random() * 10 - 5;
					el.style.transform = `translate(${randomX}px, ${randomY}px) scale(1.05)`;
				});
			}, 4000);
		},
		floatAnimation() {
			const elements = document.querySelectorAll('.float-element');
			elements.forEach((el, index) => {
				el.style.animationDelay = `${index * 0.5}s`;
			});
		},
		updateOnlineUsers() {
			// 立即获取一次在线用户数
			this.fetchOnlineUsersCount();
		},
		async fetchOnlineUsersCount() {
			try {
				const response = await this.$api.getOnlineUsersCount();
				console.log('获取在线用户数响应:', response);
				if (response.status === 200) {
					console.log('响应数据:', response.data);
					this.onlineUsers = response.data.result?.count || 0;
				}
			} catch (error) {
				console.error('获取在线用户数失败:', error);
			}
		},
		jumpRegister(){
			// 如果有注册功能可以启用
			// this.$router.push({name: 'register'})
		}
	},
	created() {
		const userinfo = window.localStorage.getItem('userinfo')
		if (userinfo){
			this.loginForm = JSON.parse(userinfo)
		}
	},
	beforeUnmount() {
		this.flowLines = [];
		this.particles = [];
		this.floatElements = [];
		if (this.loginError.timer) {
			clearInterval(this.loginError.timer);
		}
	}
}
</script>

<style scoped>
/* ============================================================
   Q·M 登录页 · 聚焦单栏设计（浅色默认 / 深色自适应）
   ============================================================ */
.login-page {
	min-height: 100vh;
	background: var(--qm-bg-1, #f5f7fa);
	display: flex;
	align-items: center;
	justify-content: center;
	position: relative;
	overflow: hidden;
}

/* 几何装饰 */
.bg-deco {
	position: absolute;
	border-radius: 50%;
	pointer-events: none;
}
.deco-1 {
	width: 440px;
	height: 440px;
	background: var(--qm-accent-soft, rgba(245,158,11,.12));
	top: -160px;
	right: -120px;
}
.deco-2 {
	width: 280px;
	height: 280px;
	background: var(--qm-accent-soft, rgba(245,158,11,.12));
	bottom: -100px;
	left: -80px;
}
.deco-3 {
	width: 110px;
	height: 110px;
	background: transparent;
	border: 2px solid var(--qm-accent-line, rgba(245,158,11,.35));
	top: 16%;
	left: 10%;
	border-radius: 24px;
	transform: rotate(18deg);
}

.login-center {
	position: relative;
	z-index: 1;
	width: 100%;
	max-width: 400px;
	padding: 24px;
}

/* 登录卡片 */
.login-card {
	background: var(--qm-bg-2, #ffffff);
	border: 1px solid var(--qm-line, rgba(15,23,42,.08));
	border-radius: 16px;
	padding: 36px 32px 26px;
	box-shadow: var(--qm-shadow, 0 4px 20px rgba(15,23,42,.06));
}

/* 品牌区 */
.brand {
	text-align: center;
	margin-bottom: 26px;
}
.brand-logo {
	width: 52px;
	height: 52px;
	border-radius: 14px;
	background: var(--qm-accent, #f59e0b);
	display: flex;
	align-items: center;
	justify-content: center;
	margin: 0 auto 12px;
}
.brand-logo svg {
	width: 30px;
	height: 30px;
}
.logo-hexagon { fill: none; stroke: rgba(255,255,255,.92); stroke-width: 6; }
.logo-center { fill: rgba(255,255,255,.92); }
.logo-square { fill: var(--qm-accent, #f59e0b); }
.brand-name {
	font-size: 20px;
	font-weight: 500;
	color: var(--qm-text-1, #1f2937);
	margin: 0 0 4px;
}
.brand-slogan {
	font-size: 13px;
	color: var(--qm-text-3, #9ca3af);
	margin: 0;
}

/* 错误提示 */
.error-alert {
	border: 1px solid var(--qm-red, #ef4444);
	border-radius: 10px;
	margin-bottom: 16px;
	overflow: hidden;
	background: var(--qm-red-soft, #fef2f2);
}
.error-content {
	display: flex;
	align-items: flex-start;
	gap: 10px;
	padding: 10px 12px;
}
.error-icon {
	color: var(--qm-red, #ef4444);
	font-size: 16px;
	margin-top: 2px;
}
.error-text h4 {
	font-size: 13px;
	color: var(--qm-text-1, #1f2937);
	margin: 0 0 2px;
}
.error-text p {
	font-size: 12px;
	color: var(--qm-text-2, #4b5563);
	margin: 0;
	line-height: 1.5;
}
.close-icon {
	margin-left: auto;
	cursor: pointer;
	color: var(--qm-text-3, #9ca3af);
	font-size: 14px;
}
.error-progress {
	height: 2px;
	background: var(--qm-red, #ef4444);
	transition: width .3s linear;
}
.shake {
	animation: shakeX .4s ease;
}
@keyframes shakeX {
	0%, 100% { transform: translateX(0); }
	25% { transform: translateX(-5px); }
	75% { transform: translateX(5px); }
}

/* 表单 */
.login-form :deep(.el-form-item) {
	margin-bottom: 16px;
}
.form-input {
	display: flex;
	align-items: center;
	gap: 10px;
	width: 100%;
	height: 44px;
	padding: 0 14px;
	border: 1px solid var(--qm-line-strong, rgba(15,23,42,.14));
	border-radius: 10px;
	background: var(--qm-bg-2, #fff);
	box-sizing: border-box;
	transition: border-color .2s ease, box-shadow .2s ease;
}
.form-input.focused {
	border-color: var(--qm-accent, #f59e0b);
	box-shadow: 0 0 0 3px var(--qm-accent-soft, rgba(245,158,11,.12));
}
.form-input.has-error {
	border-color: var(--qm-red, #ef4444);
}
.input-icon {
	display: flex;
	align-items: center;
	color: var(--qm-text-3, #9ca3af);
	font-size: 16px;
}
.form-input.focused .input-icon {
	color: var(--qm-accent, #f59e0b);
}
.login-form :deep(.el-input__wrapper) {
	box-shadow: none !important;
	background: transparent;
	padding: 0;
}
.login-form :deep(.el-input__inner) {
	color: var(--qm-text-1, #1f2937);
	height: 42px;
}
.login-form :deep(.el-input__inner::placeholder) {
	color: var(--qm-text-3, #9ca3af);
}

/* 选项行 */
.form-options {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin: 2px 0 18px;
}
.remember-me {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 13px;
	color: var(--qm-text-2, #4b5563);
}
.forgot-link {
	font-size: 13px;
	color: var(--qm-text-3, #9ca3af);
	text-decoration: none;
}
.forgot-link:hover {
	color: var(--qm-accent, #f59e0b);
}

/* 登录按钮 */
.login-btn {
	width: 100%;
	height: 44px;
	font-size: 15px;
	font-weight: 500;
	border-radius: 10px;
	border: none;
	background: var(--qm-accent, #f59e0b);
}
.login-btn:hover {
	background: var(--qm-accent-2, #f97316);
}

/* 注册 */
.login-footer {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 6px;
	margin-top: 4px;
}
.login-footer p {
	font-size: 13px;
	color: var(--qm-text-3, #9ca3af);
	margin: 0;
}
.nav-link {
	display: flex;
	align-items: center;
	gap: 2px;
	font-size: 13px;
	color: var(--qm-accent, #f59e0b);
	text-decoration: none;
	font-weight: 500;
}

/* 页脚 */
.page-foot {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	margin-top: 18px;
	font-size: 12px;
	color: var(--qm-text-3, #9ca3af);
}
.status-dot {
	width: 7px;
	height: 7px;
	border-radius: 50%;
	background: var(--qm-green, #10b981);
	display: inline-block;
}
.foot-sep {
	color: var(--qm-line-strong, rgba(15,23,42,.14));
}
</style>
