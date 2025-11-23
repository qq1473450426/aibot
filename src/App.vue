<template>
  <div class="app-container">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-icon">AI</span>
          <span class="logo-text">Quant Pro</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <a
          v-for="item in menuItems"
          :key="item.key"
          @click="currentPage = item.key"
          class="nav-item"
          :class="{ active: currentPage === item.key }"
        >
          <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
          <span class="nav-text">{{ item.label }}</span>
        </a>
      </nav>

      <div class="sidebar-footer">
        <div class="version-info">v3.0.0 Stable</div>
        <div class="connection-status">
          <span class="status-dot"></span>
          <span>Connected: DeepSeek</span>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部导航栏 -->
      <header class="top-header">
        <h1 class="page-title">{{ currentTitle }}</h1>
        <div class="header-actions">
          <el-tag type="success" effect="dark" size="large">
            <el-icon class="mr-2"><CircleCheck /></el-icon>
            API Connected
          </el-tag>
          <div class="user-avatar">
            <span>A</span>
          </div>
        </div>
      </header>

      <!-- 内容区域 -->
      <div class="content-area">
        <component :is="currentComponent" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Odometer, Coin, Setting, CircleCheck } from '@element-plus/icons-vue';
import Dashboard from './components/Dashboard.vue';
import Strategy from './components/Strategy.vue';
import Settings from './components/Settings.vue';

const currentPage = ref('dashboard');

const menuItems = [
  { key: 'dashboard', label: '仪表盘监控', icon: Odometer },
  { key: 'strategy', label: 'AI 策略中心', icon: Coin },
  { key: 'settings', label: '系统配置', icon: Setting },
];

const currentComponent = computed(() => {
  switch (currentPage.value) {
    case 'dashboard': return Dashboard;
    case 'strategy': return Strategy;
    case 'settings': return Settings;
    default: return Dashboard;
  }
});

const currentTitle = computed(() => {
  return menuItems.find(i => i.key === currentPage.value)?.label;
});
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #f5f7fa;
}

/* 侧边栏样式 */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 700;
}

.logo-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 900;
}

.logo-text {
  color: #e2e8f0;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 12px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  margin-bottom: 6px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #cbd5e1;
  font-size: 14px;
  font-weight: 500;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  transform: translateX(4px);
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.nav-icon {
  margin-right: 12px;
  font-size: 18px;
}

.nav-text {
  flex: 1;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 11px;
  text-align: center;
  color: #94a3b8;
}

.version-info {
  margin-bottom: 8px;
  font-weight: 600;
}

.connection-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 11px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 主内容区样式 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-header {
  height: 70px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 10;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.user-avatar:hover {
  transform: scale(1.1);
}

.content-area {
  flex: 1;
  overflow: auto;
  padding: 24px;
  background: #f5f7fa;
}
</style>