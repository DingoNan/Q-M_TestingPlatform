<template>
	<div class="register-page">
		<!-- 动态背景 -->
		<div class="dynamic-bg">
			<div class="bg-layer layer-1"></div>
			<div class="bg-layer layer-2"></div>
			<div class="bg-layer layer-3"></div>
			
			<!-- 数据流动线 -->
			<canvas ref="flowCanvas" class="flow-canvas"></canvas>
		</div>
		
		<!-- 浮动元素 -->
		<div class="float-elements-container">
			<div class="float-element api">
				<div class="float-content">
					<svg viewBox="0 0 24 24">
						<path d="M4.5,19.5l15-15M9,6l6,6M6,9l6,6M3,21h18"></path>
					</svg>
					<span>API</span>
				</div>
				<div class="float-tooltip">接口测试</div>
			</div>
			<div class="float-element ui">
				<div class="float-content">
					<svg viewBox="0 0 24 24">
						<rect x="3" y="3" width="18" height="18" rx="2"></rect>
						<line x1="3" y1="9" x2="21" y2="9"></line>
						<line x1="9" y1="21" x2="9" y2="9"></line>
					</svg>
					<span>UI</span>
				</div>
				<div class="float-tooltip">UI测试</div>
			</div>
			<div class="float-element performance">
				<div class="float-content">
					<svg viewBox="0 0 24 24">
						<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
						<polyline points="17 6 23 6 23 12"></polyline>
					</svg>
					<span>Perf</span>
				</div>
				<div class="float-tooltip">性能测试</div>
			</div>
			<div class="float-element mock">
				<div class="float-content">
					<svg viewBox="0 0 24 24">
						<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
						<polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
						<line x1="12" y1="22.08" x2="12" y2="12"></line>
					</svg>
					<span>Mock</span>
				</div>
				<div class="float-tooltip">Mock服务</div>
			</div>
		</div>
		
		<!-- 主内容 -->
		<div class="main-container">
			<!-- 左侧介绍区域 -->
			<div class="intro-section">
				<div class="intro-content">
					<!-- Logo和标题 -->
					<div class="logo-header">
						<div class="logo-wrapper">
							<div class="logo-circle">
								<svg class="logo-icon" viewBox="0 0 100 100">
									<path d="M50,10 L90,30 L90,70 L50,90 L10,70 L10,30 Z" class="logo-hexagon"></path>
									<circle cx="50" cy="50" r="20" class="logo-center"></circle>
									<path d="M35,35 L65,35 L65,65 L35,65 Z" class="logo-square"></path>
								</svg>
								<div class="logo-glow"></div>
							</div>
							<div class="logo-text">
								<h1 class="platform-name">BlackBagTest</h1>
								<p class="platform-slogan">智能测试解决方案</p>
							</div>
						</div>
					</div>
					
					<!-- 功能特性展示 -->
					<div class="features-showcase">
						<div class="features-title">
							<h2>一体化测试平台</h2>
							<p>为您的产品质量保驾护航</p>
						</div>
						
						<div class="feature-cards">
							<div class="feature-card" @mouseenter="activeFeature = 'api'" @mouseleave="activeFeature = ''">
								<div class="feature-icon api">
									<svg viewBox="0 0 24 24">
										<path d="M4.5,19.5l15-15M9,6l6,6M6,9l6,6M3,21h18"></path>
									</svg>
								</div>
								<h3>接口测试</h3>
								<p>全面支持REST、GraphQL、SOAP等多种接口协议，自动化测试用例管理</p>
								<div class="feature-wave" :class="{active: activeFeature === 'api'}"></div>
							</div>
							
							<div class="feature-card" @mouseenter="activeFeature = 'ui'" @mouseleave="activeFeature = ''">
								<div class="feature-icon ui">
									<svg viewBox="0 0 24 24">
										<rect x="3" y="3" width="18" height="18" rx="2"></rect>
										<line x1="3" y1="9" x2="21" y2="9"></line>
										<line x1="9" y1="21" x2="9" y2="9"></line>
									</svg>
								</div>
								<h3>UI测试</h3>
								<p>可视化UI测试，支持Web、移动端自动化测试，智能元素识别</p>
								<div class="feature-wave" :class="{active: activeFeature === 'ui'}"></div>
							</div>
							
							<div class="feature-card" @mouseenter="activeFeature = 'performance'" @mouseleave="activeFeature = ''">
								<div class="feature-icon performance">
									<svg viewBox="0 0 24 24">
										<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
										<polyline points="17 6 23 6 23 12"></polyline>
									</svg>
								</div>
								<h3>性能测试</h3>
								<p>高并发压力测试，性能监控与分析，瓶颈定位与优化建议</p>
								<div class="feature-wave" :class="{active: activeFeature === 'performance'}"></div>
							</div>
							
							<div class="feature-card" @mouseenter="activeFeature = 'mock'" @mouseleave="activeFeature = ''">
								<div class="feature-icon mock">
									<svg viewBox="0 0 24 24">
										<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
										<polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
										<line x1="12" y1="22.08" x2="12" y2="12"></line>
									</svg>
								</div>
								<h3>Mock服务</h3>
								<p>灵活的数据模拟服务，支持动态响应、场景化配置，提升测试效率</p>
								<div class="feature-wave" :class="{active: activeFeature === 'mock'}"></div>
							</div>
						</div>
					</div>
				</div>
			</div>
			
			<!-- 右侧注册区域 -->
			<div class="login-section">
				<div class="login-card">
					<!-- 注册表单标题 -->
					<div class="login-header">
						<h2>用户注册</h2>
						<p>请填写您的账号信息</p>
					</div>
					
					<!-- 错误提示区域 -->
					<div class="error-alert" v-if="registerError.show" :class="{shake: registerError.shake}">
						<div class="error-content">
							<el-icon class="error-icon"><Warning /></el-icon>
							<div class="error-text">
								<h4>{{ registerError.title }}</h4>
								<p>{{ registerError.message }}</p>
							</div>
							<el-icon class="close-icon" @click="dismissError"><Close /></el-icon>
						</div>
						<div class="error-progress" :style="{width: registerError.progress + '%'}"></div>
					</div>
					
					<!-- 表单区域 -->
					<el-form :model="registerForm" :rules="registerRules" ref='registerRef' class="login-form">
						<el-form-item prop="username">
							<div class="form-input" :class="{focused: focusedField === 'username', 'has-error': registerError.show}">
								<div class="input-icon">
									<el-icon><User /></el-icon>
								</div>
								<el-input 
									v-model="registerForm.username" 
									placeholder="请输入用户名"
									@focus="handleInputFocus('username')"
									@blur="focusedField = ''"
									@input="clearError">
								</el-input>
								<div class="input-underline">
									<div class="underline-active" :class="{active: focusedField === 'username'}"></div>
								</div>
							</div>
						</el-form-item>
						
						<el-form-item prop="password">
							<div class="form-input" :class="{focused: focusedField === 'password', 'has-error': registerError.show}">
								<div class="input-icon">
									<el-icon><Lock /></el-icon>
								</div>
								<el-input 
									v-model="registerForm.password" 
									placeholder="请输入密码"
									type="password"
									show-password
									@focus="handleInputFocus('password')"
									@blur="focusedField = ''"
									@input="clearError">
								</el-input>
								<div class="input-underline">
									<div class="underline-active" :class="{active: focusedField === 'password'}"></div>
								</div>
							</div>
						</el-form-item>
						
						<el-form-item prop="password_confirm">
				<div class="form-input" :class="{focused: focusedField === 'password_confirm', 'has-error': registerError.show}">
					<div class="input-icon">
						<el-icon><Lock /></el-icon>
					</div>
					<el-input 
						v-model="registerForm.password_confirm" 
						placeholder="请确认密码"
						type="password"
						show-password
						@focus="handleInputFocus('password_confirm')"
						@blur="focusedField = ''"
						@input="clearError">
					</el-input>
					<div class="input-underline">
						<div class="underline-active" :class="{active: focusedField === 'password_confirm'}"></div>
					</div>
				</div>
			</el-form-item>
						
						<el-form-item>
							<el-button 
								type="primary" 
								@click="register" 
								class="login-btn"
								:loading="loading"
								@mouseenter="hoverBtn = true"
								@mouseleave="hoverBtn = false">
								<span v-if="!loading">立即注册</span>
								<span v-else>注册中...</span>
								<div class="btn-ripple"></div>
								<div class="btn-shine" :class="{active: hoverBtn}"></div>
							</el-button>
						</el-form-item>
						
						<div class="login-footer">
							<p>已有账号？</p>
							<router-link 
								:to="{ name: 'login' }"
								class="nav-link">
								立即登录
								<el-icon><ArrowRight /></el-icon>
							</router-link>
						</div>
					</el-form>
					
					<!-- 平台状态 -->
					<div class="platform-status">
						<div class="status-item">
							<div class="status-dot online"></div>
							<span>平台状态: 运行中</span>
						</div>
						<div class="status-item">
							<div class="status-dot active"></div>
							<span>在线用户: {{ onlineUsers }}</span>
						</div>
					</div>
				</div>
			</div>
		</div>
		
		<!-- 粒子效果 -->
		<canvas ref="particleCanvas" class="particle-canvas"></canvas>
		
		<!-- 底部信息 -->
		<div class="footer">
			<div class="footer-content">
				<p>© 2025 BlackBagTest 智能测试平台 | 版本 3.0.0</p>
				<div class="footer-links">
					<a href="#" @click="openHelp">帮助文档</a>
					<a href="#">API文档</a>
					<a href="#">服务状态</a>
					<a href="#">联系我们</a>
					<router-link :to="{ name: 'navigation' }">平台导航</router-link>
				</div>
			</div>
		</div>
	</div>
</template>

<script type='text/javascript'>
import api from '../../api/index.js'
import { ElMessage } from 'element-plus'
import { User, Lock, ArrowRight, Warning, Close } from '@element-plus/icons-vue'

export default {
	name: 'RegisterPage',
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
			switchColor: '#6366f1',
			registerError: {
				show: false,
				title: '',
				message: '',
				shake: false,
				progress: 100,
				timer: null
			},
			registerForm: {
				username: '',
				password: '',
				password_confirm: ''
			},
			registerRules: {
				username: [{
					required: true,
					message: '请输入用户名',
					trigger: 'blur',
				}],
				password: [{
					required: true,
					message: '请输入密码',
					trigger: 'blur',
				}],
				password_confirm: [{
				required: true,
				message: '请确认密码',
				trigger: 'blur',
				validator: (rule, value, callback) => {
					if (value !== this.registerForm.password) {
						callback(new Error('两次输入密码不一致'))
					} else {
						callback()
					}
				}
			}]
		},
			flowLines: [],
			particles: [],
			floatElements: []
		}
	},
	mounted() {
		this.initCanvasEffects();
		this.startAnimations();
		this.updateOnlineUsers();
		this.initFloatElements();
	},
	methods: {
		openHelp(){
			window.open('https://gitee.com/zengqicheng/black-bag-test/wikis/pages', '_blank');
		},
		async register(){
			// 清除之前的错误提示
			this.clearError();
			
			this.$refs['registerRef'].validate(async (valid, fields)=>{
				if(valid){
					this.loading = true
					try {
						// 构建注册参数，默认设置为非超级管理员
					const registerData = {
						username: this.registerForm.username,
						password: this.registerForm.password,
						password_confirm: this.registerForm.password_confirm,
						is_superuser: false // 默认非超级管理员
					}
						
						const response = await api.register(registerData)
						if (response.status === 201){
							// 注册成功
							ElMessage({
								message: '注册成功,请登录后使用',
								type: 'success',
								duration: 2000
							})
							
							// 跳转到登录页面
							this.$router.push({name: 'login'})
						}else{
							// 注册失败
							this.showErrorMessage(
								'注册失败', 
								response.data?.message || '注册失败，请重试'
							);
						}
					} catch (error) {
						// 网络错误或其他异常
						this.showErrorMessage(
							'注册失败', 
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
				} else if (firstError === 'password_confirm') {
					message = '两次输入密码不一致';
				}
					
					this.showErrorMessage('表单验证失败', message);
					this.loading = false;
				}
			})
		},
		// 显示错误消息
		showErrorMessage(title, message) {
			// 清除之前的定时器
			if (this.registerError.timer) {
				clearInterval(this.registerError.timer);
			}
			
			this.registerError = {
				show: true,
				title: title,
				message: message,
				shake: true,
				progress: 100,
				timer: null
			};
			
			// 移除抖动效果
			setTimeout(() => {
				this.registerError.shake = false;
			}, 500);
			
			// 设置进度条递减
			this.registerError.timer = setInterval(() => {
				if (this.registerError.progress > 0) {
					this.registerError.progress -= 0.5;
				} else {
					clearInterval(this.registerError.timer);
					this.registerError.show = false;
				}
			}, 50);
			
			// 5秒后自动关闭
			setTimeout(() => {
				if (this.registerError.show) {
					this.clearError();
				}
			}, 5000);
		},
		// 清除错误提示
		clearError() {
			if (this.registerError.timer) {
				clearInterval(this.registerError.timer);
			}
			this.registerError = {
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
			if (this.registerError.show) {
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
					color: `rgba(99, 102, 241, ${Math.random() * 0.3 + 0.1})`,
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
			// 每5秒获取一次在线用户数
			setInterval(() => {
				this.fetchOnlineUsersCount();
			}, 5000);
		},
		async fetchOnlineUsersCount() {
			try {
				const response = await api.getOnlineUsersCount();
				console.log('获取在线用户数响应:', response);
				if (response.status === 200) {
					console.log('响应数据:', response.data);
					this.onlineUsers = response.data.result?.count || 0;
				}
			} catch (error) {
				console.error('获取在线用户数失败:', error);
			}
		}
	},
	beforeUnmount() {
		this.flowLines = [];
		this.particles = [];
		this.floatElements = [];
		if (this.registerError.timer) {
			clearInterval(this.registerError.timer);
		}
	}
}
</script>

<style scoped>
.register-page {
	min-height: 100vh;
	background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
	display: flex;
	flex-direction: column;
	position: relative;
	overflow: hidden;
	font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
}

/* 动态背景 */
.dynamic-bg {
	position: absolute;
	width: 100%;
	height: 100%;
	z-index: 1;
}

.bg-layer {
	position: absolute;
	width: 100%;
	height: 100%;
}

.layer-1 {
	background: radial-gradient(circle at 20% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 50%);
	animation: pulse-1 8s ease-in-out infinite;
}

.layer-2 {
	background: radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
	animation: pulse-2 10s ease-in-out infinite;
}

.layer-3 {
	background: radial-gradient(circle at 50% 80%, rgba(14, 165, 233, 0.08) 0%, transparent 50%);
	animation: pulse-3 12s ease-in-out infinite;
}

@keyframes pulse-1 {
	0%, 100% { opacity: 0.8; }
	50% { opacity: 0.4; }
}

@keyframes pulse-2 {
	0%, 100% { opacity: 0.6; }
	50% { opacity: 0.2; }
}

@keyframes pulse-3 {
	0%, 100% { opacity: 0.7; }
	50% { opacity: 0.3; }
}

/* 数据流动画 */
.flow-canvas {
	position: absolute;
	width: 100%;
	height: 100%;
	z-index: 1;
}

/* 浮动元素容器 */
.float-elements-container {
	position: absolute;
	width: 100%;
	height: 100%;
	z-index: 3; /* 调整z-index，位于背景之上，主内容之下 */
	pointer-events: none; /* 确保不干扰交互 */
}

/* 浮动元素 */
.float-element {
	position: absolute;
	width: 70px;
	height: 70px;
	border-radius: 18px;
	background: rgba(255, 255, 255, 0.08);
	backdrop-filter: blur(15px);
	border: 1px solid rgba(255, 255, 255, 0.15);
	box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
	transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
	display: flex;
	align-items: center;
	justify-content: center;
	font-weight: 600;
	color: white;
	font-size: 14px;
	z-index: 3;
	pointer-events: auto;
	cursor: pointer;
	animation: float-element 6s ease-in-out infinite;
	overflow: hidden;
}

.float-element::before {
	content: '';
	position: absolute;
	width: 100%;
	height: 100%;
	border-radius: inherit;
	background: conic-gradient(from 0deg, transparent, rgba(99, 102, 241, 0.3), transparent);
	animation: rotate 4s linear infinite;
	z-index: -1;
	opacity: 0.5;
}

.float-element::after {
	content: '';
	position: absolute;
	top: 0;
	left: -100%;
	width: 100%;
	height: 100%;
	background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
	transition: left 0.7s ease;
}

.float-element:hover::after {
	left: 100%;
}

.float-element:hover {
	transform: translateY(-10px) scale(1.1);
	box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
	background: rgba(255, 255, 255, 0.12);
	border-color: rgba(99, 102, 241, 0.4);
}

.float-content {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 6px;
	z-index: 2;
}

.float-element svg {
	width: 24px;
	height: 24px;
	stroke: white;
	stroke-width: 2;
	stroke-linecap: round;
	stroke-linejoin: round;
	fill: none;
	transition: all 0.3s ease;
}

.float-element:hover svg {
	transform: scale(1.2);
}

.float-tooltip {
	position: absolute;
	bottom: -35px;
	left: 50%;
	transform: translateX(-50%);
	background: rgba(0, 0, 0, 0.8);
	color: white;
	padding: 6px 12px;
	border-radius: 6px;
	font-size: 12px;
	white-space: nowrap;
	opacity: 0;
	visibility: hidden;
	transition: all 0.3s ease;
	backdrop-filter: blur(10px);
	z-index: 100;
}

.float-element:hover .float-tooltip {
	opacity: 1;
	visibility: visible;
	bottom: -40px;
}

/* 浮动元素位置 */
.float-element.api { 
	top: 20%; 
	left: 5%; 
	animation-delay: 0s;
}

.float-element.ui { 
	top: 65%; 
	left: 8%; 
	animation-delay: 0.5s;
}

.float-element.performance { 
	top: 25%; 
	right: 5%; 
	animation-delay: 1s;
}

.float-element.mock { 
	top: 70%; 
	right: 8%; 
	animation-delay: 1.5s;
}

/* 浮动动画 */
@keyframes float-element {
	0%, 100% { 
		transform: translateY(0) rotate(0deg); 
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
	}
	25% { 
		transform: translateY(-15px) rotate(3deg);
		box-shadow: 0 15px 40px rgba(0, 0, 0, 0.25);
	}
	75% { 
		transform: translateY(10px) rotate(-3deg);
		box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
	}
}

@keyframes rotate {
	from { transform: rotate(0deg); }
	to { transform: rotate(360deg); }
}

/* 主容器 */
.main-container {
	display: flex;
	flex: 1;
	position: relative;
	z-index: 4; /* 主内容位于浮动元素之上 */
	padding: 20px;
	max-width: 1400px;
	margin: 0 auto;
	width: 100%;
}

/* 左侧介绍区域 */
.intro-section {
	flex: 1;
	display: flex;
	align-items: center;
	padding-right: 40px;
	position: relative;
	z-index: 5; /* 确保介绍区域内容在浮动元素之上 */
}

.intro-content {
	width: 100%;
	animation: slideInLeft 0.8s ease-out;
}

.logo-header {
	margin-bottom: 60px;
}

.logo-wrapper {
	display: flex;
	align-items: center;
	gap: 20px;
	margin-bottom: 30px;
}

.logo-circle {
	position: relative;
	width: 80px;
	height: 80px;
}

.logo-icon {
	width: 100%;
	height: 100%;
	filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.5));
	animation: logoFloat 6s ease-in-out infinite;
}

.logo-hexagon {
	fill: none;
	stroke: #6366f1;
	stroke-width: 4;
	stroke-linecap: round;
	stroke-linejoin: round;
	animation: hexagonPulse 3s ease-in-out infinite;
}

.logo-center {
	fill: #6366f1;
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
	background: radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, transparent 70%);
	animation: glowPulse 4s ease-in-out infinite;
}

.logo-text {
	text-align: left;
}

.platform-name {
	font-size: 42px;
	font-weight: 800;
	background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
	-webkit-background-clip: text;
	-webkit-text-fill-color: transparent;
	background-clip: text;
	margin: 0 0 8px 0;
	letter-spacing: -0.5px;
}

.platform-slogan {
	color: rgba(255, 255, 255, 0.7);
	font-size: 18px;
	margin: 0;
}

.features-showcase {
	margin-top: 40px;
	position: relative;
	z-index: 5;
}

.features-title h2 {
	font-size: 32px;
	color: white;
	margin: 0 0 10px 0;
	font-weight: 700;
}

.features-title p {
	color: rgba(255, 255, 255, 0.6);
	font-size: 16px;
	margin: 0 0 40px 0;
}

.feature-cards {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 25px;
}

.feature-card {
	background: rgba(255, 255, 255, 0.05);
	backdrop-filter: blur(10px);
	border-radius: 20px;
	padding: 25px;
	border: 1px solid rgba(255, 255, 255, 0.1);
	transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
	position: relative;
	overflow: hidden;
	cursor: pointer;
}

.feature-card:hover {
	transform: translateY(-8px);
	background: rgba(255, 255, 255, 0.08);
	border-color: rgba(99, 102, 241, 0.3);
	box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.feature-icon {
	width: 60px;
	height: 60px;
	border-radius: 16px;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 20px;
	position: relative;
	overflow: hidden;
}

.feature-icon svg {
	width: 30px;
	height: 30px;
	stroke: white;
	stroke-width: 2;
	stroke-linecap: round;
	stroke-linejoin: round;
	fill: none;
}

.feature-icon.api {
	background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.1) 100%);
	border: 1px solid rgba(99, 102, 241, 0.3);
}

.feature-icon.ui {
	background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
	border: 1px solid rgba(139, 92, 246, 0.3);
}

.feature-icon.performance {
	background: linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(14, 165, 233, 0.1) 100%);
	border: 1px solid rgba(14, 165, 233, 0.3);
}

.feature-icon.mock {
	background: linear-gradient(135deg, rgba(236, 72, 153, 0.2) 0%, rgba(236, 72, 153, 0.1) 100%);
	border: 1px solid rgba(236, 72, 153, 0.3);
}

.feature-card h3 {
	color: white;
	font-size: 20px;
	font-weight: 600;
	margin: 0 0 12px 0;
}

.feature-card p {
	color: rgba(255, 255, 255, 0.6);
	font-size: 14px;
	line-height: 1.6;
	margin: 0;
}

.feature-wave {
	position: absolute;
	bottom: 0;
	left: 0;
	width: 100%;
	height: 3px;
	background: linear-gradient(90deg, transparent, #6366f1, transparent);
	transform: translateX(-100%);
	transition: transform 0.6s ease;
}

.feature-wave.active {
	transform: translateX(100%);
}

/* 右侧注册区域 */
.login-section {
	width: 420px;
	display: flex;
	align-items: center;
	position: relative;
	z-index: 5; /* 确保登录区域在浮动元素之上 */
}

.login-card {
	background: rgba(255, 255, 255, 0.97);
	backdrop-filter: blur(20px);
	border-radius: 24px;
	padding: 40px;
	width: 100%;
	box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
	border: 1px solid rgba(255, 255, 255, 0.25);
	animation: slideInRight 0.8s ease-out;
	position: relative;
	overflow: hidden;
}

.login-card::before {
	content: '';
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 6px;
	background: linear-gradient(90deg, #6366f1, #8b5cf6, #0ea5e9, #ec4899);
	background-size: 300% 100%;
	animation: gradientShift 3s ease infinite;
}

.login-header {
	text-align: center;
	margin-bottom: 30px;
}

.login-header h2 {
	font-size: 28px;
	color: #1e293b;
	margin: 0 0 10px 0;
	font-weight: 700;
}

.login-header p {
	color: #64748b;
	font-size: 15px;
	margin: 0;
}

/* 错误提示样式 */
.error-alert {
	background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
	border: 1px solid #f87171;
	border-radius: 12px;
	padding: 16px;
	margin-bottom: 24px;
	position: relative;
	overflow: hidden;
	transform: translateY(0);
	opacity: 1;
	transition: all 0.3s ease;
}

.error-alert.shake {
	animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

.error-alert.hide {
	transform: translateY(-10px);
	opacity: 0;
	height: 0;
	padding: 0;
	margin: 0;
	border: none;
}

.error-content {
	display: flex;
	align-items: flex-start;
	gap: 12px;
}

.error-icon {
	color: #dc2626;
	font-size: 20px;
	flex-shrink: 0;
	margin-top: 2px;
}

.error-text {
	flex: 1;
}

.error-text h4 {
	color: #dc2626;
	font-size: 16px;
	font-weight: 600;
	margin: 0 0 4px 0;
}

.error-text p {
	color: #7f1d1d;
	font-size: 14px;
	margin: 0;
	line-height: 1.4;
}

.close-icon {
	color: #dc2626;
	font-size: 16px;
	cursor: pointer;
	transition: all 0.2s ease;
	flex-shrink: 0;
}

.close-icon:hover {
	transform: scale(1.1);
}

.error-progress {
	position: absolute;
	bottom: 0;
	left: 0;
	height: 3px;
	background: linear-gradient(90deg, #dc2626, #ef4444);
	transition: width 0.05s linear;
}

/* 抖动动画 */
@keyframes shake {
	10%, 90% { transform: translateX(-1px); }
	20%, 80% { transform: translateX(2px); }
	30%, 50%, 70% { transform: translateX(-3px); }
	40%, 60% { transform: translateX(3px); }
}

/* 表单区域 */
.login-form {
	margin-bottom: 30px;
}

.form-input {
	position: relative;
	margin-bottom: 24px;
	width: 100%;
}

/* 修复输入框宽度问题 */
:deep(.el-form-item) {
	margin-bottom: 0;
}

:deep(.el-form-item__content) {
	width: 100%;
	line-height: normal;
}

.input-icon {
	position: absolute;
	left: 16px;
	top: 50%;
	transform: translateY(-50%);
	color: #6366f1;
	z-index: 2;
	transition: all 0.3s ease;
}

.form-input.focused .input-icon {
	color: #8b5cf6;
	margin-bottom: 10px;
	transform: translateY(-50%) scale(1.2);
}

.form-input.has-error .input-icon {
	color: #dc2626;
}

/* 统一输入框样式 */
:deep(.el-input) {
	width: 100%;
}

:deep(.el-input__wrapper) {
	width: 100%;
	background: rgba(255, 255, 255, 0.95);
	border: 2px solid #e2e8f0;
	border-radius: 12px;
	padding: 16px 16px 16px 48px;
	height: 56px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	transition: all 0.3s ease;
	box-sizing: border-box;
}

.form-input.has-error :deep(.el-input__wrapper) {
	border-color: #dc2626;
	background: #fef2f2;
}

:deep(.el-input__wrapper:hover),
:deep(.el-input__wrapper.is-focus) {
	border-color: #6366f1;
	box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
	background: white;
}

.form-input.has-error :deep(.el-input__wrapper:hover),
.form-input.has-error :deep(.el-input__wrapper.is-focus) {
	border-color: #dc2626;
	box-shadow: 0 4px 12px rgba(220, 38, 38, 0.15);
}

.input-underline {
	position: absolute;
	bottom: -2px;
	left: 16px;
	right: 16px;
	height: 2px;
	background: #e2e8f0;
	overflow: hidden;
}

.form-input.has-error .input-underline {
	background: #fecaca;
}

.underline-active {
	height: 100%;
	width: 100%;
	background: linear-gradient(90deg, #6366f1, #8b5cf6);
	transform: translateX(-100%);
	transition: transform 0.3s ease;
}

.form-input.has-error .underline-active {
	background: linear-gradient(90deg, #dc2626, #ef4444);
}

.underline-active.active {
	transform: translateX(0);
}

.login-btn {
	position: relative;
	width: 100%;
	height: 56px;
	border: none;
	border-radius: 12px;
	font-size: 16px;
	font-weight: 600;
	letter-spacing: 0.5px;
	background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
	overflow: hidden;
	transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
	margin-bottom: 20px;
}

.login-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 10px 25px rgba(99, 102, 241, 0.4);
}

.login-btn:active {
	transform: translateY(0);
}

.btn-ripple {
	position: absolute;
	top: 50%;
	left: 50%;
	width: 0;
	height: 0;
	border-radius: 50%;
	background: rgba(255, 255, 255, 0.5);
	transform: translate(-50%, -50%);
	transition: width 0.6s ease, height 0.6s ease, opacity 0.6s ease;
}

.login-btn:hover .btn-ripple {
	width: 200%;
	height: 200%;
	opacity: 0;
}

.btn-shine {
	position: absolute;
	top: -100%;
	left: -100%;
	width: 50%;
	height: 300%;
	background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
	transform: rotate(30deg);
	transition: left 0.8s ease;
}

.btn-shine.active {
	left: 150%;
}

.login-footer {
	text-align: center;
	border-top: 1px solid #e2e8f0;
	padding-top: 20px;
}

.login-footer p {
	color: #64748b;
	font-size: 14px;
	margin: 0 0 15px 0;
}

.nav-link {
	display: inline-flex;
	align-items: center;
	gap: 8px;
	color: #6366f1;
	text-decoration: none;
	font-weight: 600;
	font-size: 14px;
	transition: all 0.3s ease;
	padding: 8px 16px;
	border-radius: 8px;
	background: rgba(99, 102, 241, 0.1);
}

.nav-link:hover {
	color: white;
	background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
	transform: translateY(-2px);
	box-shadow: 0 5px 15px rgba(99, 102, 241, 0.3);
}

.platform-status {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-top: 25px;
	padding-top: 25px;
	border-top: 1px solid #e2e8f0;
}

.status-item {
	display: flex;
	align-items: center;
	gap: 8px;
	color: #64748b;
	font-size: 14px;
}

.status-dot {
	width: 10px;
	height: 10px;
	border-radius: 50%;
}

.status-dot.online {
	background: #10b981;
	animation: pulse-dot 2s ease-in-out infinite;
}

.status-dot.active {
	background: #f59e0b;
}

@keyframes pulse-dot {
	0%, 100% { opacity: 1; }
	50% { opacity: 0.5; }
}

/* 粒子画布 */
.particle-canvas {
	position: absolute;
	width: 100%;
	height: 100%;
	z-index: 2;
}

/* 底部信息 */
.footer {
	position: relative;
	z-index: 4;
	background: rgba(15, 23, 42, 0.8);
	backdrop-filter: blur(10px);
	border-top: 1px solid rgba(255, 255, 255, 0.1);
	padding: 30px 0;
	margin-top: 40px;
}

.footer-content {
	max-width: 1200px;
	margin: 0 auto;
	padding: 0 20px;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.footer p {
	color: rgba(255, 255, 255, 0.6);
	font-size: 14px;
	margin: 0;
}

.footer-links {
	display: flex;
	gap: 20px;
}

.footer-links a {
	color: rgba(255, 255, 255, 0.6);
	text-decoration: none;
	font-size: 14px;
	transition: all 0.3s ease;
	position: relative;
	padding: 5px 0;
}

.footer-links a:hover {
	color: #6366f1;
}

.footer-links a::after {
	content: '';
	position: absolute;
	bottom: 0;
	left: 0;
	width: 0;
	height: 2px;
	background: #6366f1;
	transition: width 0.3s ease;
}

.footer-links a:hover::after {
	width: 100%;
}

/* 动画效果 */
@keyframes slideInLeft {
	from {
		opacity: 0;
		transform: translateX(-50px);
	}
	to {
		opacity: 1;
		transform: translateX(0);
	}
}

@keyframes slideInRight {
	from {
		opacity: 0;
		transform: translateX(50px);
	}
	to {
		opacity: 1;
		transform: translateX(0);
	}
}

@keyframes gradientShift {
	0% { background-position: 0% 50%; }
	50% { background-position: 100% 50%; }
	100% { background-position: 0% 50%; }
}

@keyframes logoFloat {
	0%, 100% { transform: translateY(0) rotate(0deg); }
	25% { transform: translateY(-10px) rotate(2deg); }
	75% { transform: translateY(10px) rotate(-2deg); }
}

@keyframes hexagonPulse {
	0%, 100% { stroke-width: 4; opacity: 1; }
	50% { stroke-width: 6; opacity: 0.8; }
}

@keyframes centerPulse {
	0%, 100% { r: 20; opacity: 0.8; }
	50% { r: 22; opacity: 1; }
}

@keyframes glowPulse {
	0%, 100% { opacity: 0.6; }
	50% { opacity: 0.9; }
}

/* 响应式设计 */
@media (max-width: 1024px) {
	.main-container {
		flex-direction: column;
		align-items: center;
		padding: 40px 20px;
	}
	
	.intro-section {
		padding-right: 0;
		margin-bottom: 40px;
		text-align: center;
	}
	
	.login-section {
		width: 100%;
		max-width: 420px;
	}
	
	.feature-cards {
		grid-template-columns: 1fr;
		gap: 20px;
	}
	
	.logo-wrapper {
		justify-content: center;
	}
}

@media (max-width: 768px) {
	.intro-section {
		display: none;
	}
	
	.login-card {
		padding: 30px 24px;
	}
	
	.float-elements-container {
		display: none;
	}
	
	.footer-content {
		flex-direction: column;
		gap: 20px;
		text-align: center;
	}
	
	.footer-links {
		flex-wrap: wrap;
		justify-content: center;
	}
}

/* 加载动画 */
:deep(.el-loading-spinner) {
	color: #6366f1;
}

:deep(.el-loading-spinner .path) {
	stroke: #6366f1;
}

/* 表单验证样式 */
:deep(.el-form-item__error) {
	font-size: 12px;
	color: #dc2626;
	margin-top: 4px;
}

/* 按钮加载状态 */
:deep(.el-button--loading) {
	background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
}

/* 确保所有元素都有合适的z-index */
* {
	z-index: inherit;
}
</style>