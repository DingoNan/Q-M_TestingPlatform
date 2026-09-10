<template>
  <div class="no-permission-container">
    <!-- 背景效果 -->
    <div class="background-effects">
      <div class="effect effect-1"></div>
      <div class="effect effect-2"></div>
      <div class="effect effect-3"></div>
    </div>
    
    <div class="no-permission-card">
      <!-- 锁定图标区域 -->
      <div class="icon-section">
        <div class="lock-container">
          <el-icon class="no-permission-icon"><Lock /></el-icon>
          <div class="lock-shine"></div>
        </div>
      </div>
      
      <!-- 标题和描述 -->
      <h2 class="no-permission-title">
        <span class="title-word" v-for="(word, index) in titleWords" :key="index" :style="{ animationDelay: index * 0.1 + 's' }">
          {{ word }}
        </span>
      </h2>
      <p class="no-permission-description">
        您没有权限访问当前页面，请联系管理员获取权限。
      </p>
      
      <!-- 按钮组 -->
      <div class="button-group">
        <el-button type="primary" @click="goBack" class="back-button">
          <el-icon><ArrowLeft /></el-icon>
          返回上一页
        </el-button>
      </div>
      
      <!-- 装饰元素 -->
      <div class="decorations">
        <div class="decoration decoration-1"></div>
        <div class="decoration decoration-2"></div>
        <div class="decoration decoration-3"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { Lock, ArrowLeft, House } from '@element-plus/icons-vue'

export default {
  setup() {
    return {
      Lock,
      ArrowLeft,
      House
    }
  },
  data() {
    return {
      titleWords: ['暂', '无', '权', '限']
    }
  },
  methods: {
    goBack() {
      // 尝试返回上一页，跳过当前页面和可能的权限页面
      window.history.go(-2) || this.$router.push('/project/index')
    }
  }
}
</script>

<style scoped>
.no-permission-container {
  width: 100%;
  height: calc(100vh - 75px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 背景效果 */
.background-effects {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.effect {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.3;
  animation: float 10s infinite ease-in-out;
}

.effect-1 {
  width: 500px;
  height: 500px;
  background: #f59e0b;
  top: -150px;
  left: -150px;
  animation-delay: 0s;
}

.effect-2 {
  width: 400px;
  height: 400px;
  background: #ef4444;
  bottom: -150px;
  right: -150px;
  animation-delay: 3s;
}

.effect-3 {
  width: 300px;
  height: 300px;
  background: #10b981;
  top: 50%;
  right: 10%;
  animation-delay: 6s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  25% {
    transform: translateY(-25px) rotate(5deg);
  }
  50% {
    transform: translateY(15px) rotate(0deg);
  }
  75% {
    transform: translateY(-15px) rotate(-5deg);
  }
}

.no-permission-card {
  background: var(--qm-bg-2);
  border-radius: 32px;
  box-shadow: 0 16px 60px rgba(0, 0, 0, 0.15);
  padding: 80px 50px;
  text-align: center;
  max-width: 580px;
  width: 100%;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 1;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(16px);
}

.no-permission-card:hover {
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.2);
  transform: translateY(-12px) scale(1.03);
}

/* 锁定图标 */
.icon-section {
  margin-bottom: 40px;
  position: relative;
}

.lock-container {
  position: relative;
  display: inline-block;
}

.no-permission-icon {
  font-size: 120px;
  color: #ef4444;
  animation: pulse 2.5s infinite;
  position: relative;
  z-index: 2;
}

.lock-shine {
  position: absolute;
  top: -30px;
  left: -30px;
  right: -30px;
  bottom: -30px;
  background: radial-gradient(circle, rgba(239, 68, 68, 0.25) 0%, transparent 70%);
  border-radius: 50%;
  animation: shine 4s infinite;
  z-index: 1;
}

@keyframes shine {
  0% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 0.5;
  }
}

/* 标题 */
.no-permission-title {
  font-size: 36px;
  font-weight: 800;
  color: var(--qm-text-1);
  margin: 0 0 20px 0;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.title-word {
  display: inline-block;
  opacity: 0;
  transform: translateY(25px);
  animation: slideIn 0.8s forwards ease-out;
}

@keyframes slideIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 描述 */
.no-permission-description {
  font-size: 20px;
  color: var(--qm-text-2);
  margin: 0 0 50px 0;
  line-height: 1.7;
  opacity: 0;
  animation: fadeIn 1s forwards ease-out;
  animation-delay: 0.6s;
  max-width: 450px;
  margin-left: auto;
  margin-right: auto;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

/* 按钮组 */
.button-group {
  display: flex;
  justify-content: center;
  opacity: 0;
  animation: fadeIn 1s forwards ease-out;
  animation-delay: 0.9s;
}

.back-button {
  padding: 16px 40px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 16px;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border: none;
  color: white;
  min-width: 180px;
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.3);
}

.back-button:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(245, 158, 11, 0.5);
}

.back-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s;
}

.back-button:hover::before {
  left: 100%;
}

.back-button:active {
  transform: translateY(-2px);
}

/* 装饰元素 */
.decorations {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.decoration {
  position: absolute;
  border-radius: 50%;
  background: rgba(245, 158, 11, 0.1);
  animation: float 8s infinite ease-in-out;
}

.decoration-1 {
  width: 100px;
  height: 100px;
  top: 30px;
  right: 30px;
  animation-delay: 0s;
}

.decoration-2 {
  width: 80px;
  height: 80px;
  bottom: 30px;
  left: 30px;
  animation-delay: 3s;
}

.decoration-3 {
  width: 60px;
  height: 60px;
  top: 50%;
  left: 15px;
  animation-delay: 6s;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .no-permission-card {
    padding: 60px 30px;
  }
  
  .no-permission-icon {
    font-size: 100px;
  }
  
  .no-permission-title {
    font-size: 28px;
  }
  
  .no-permission-description {
    font-size: 18px;
  }
  
  .back-button {
    padding: 14px 36px;
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .no-permission-card {
    padding: 40px 24px;
  }
  
  .no-permission-icon {
    font-size: 80px;
  }
  
  .no-permission-title {
    font-size: 24px;
  }
  
  .no-permission-description {
    font-size: 16px;
  }
  
  .back-button {
    padding: 12px 32px;
    font-size: 15px;
  }
}
</style>