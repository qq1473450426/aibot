<template>
  <div class="dashboard-container">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card balance-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">总权益 (USDT)</span>
          </div>
        </template>
        <div class="stat-value balance-value">$ {{ mockData.balance.toLocaleString() }}</div>
        <div class="stat-desc">可用: ${{ mockData.available.toLocaleString() }}</div>
      </el-card>

      <el-card class="stat-card pnl-card" shadow="hover" :class="mockData.todayPnl >= 0 ? 'positive' : 'negative'">
        <template #header>
          <div class="card-header">
            <span class="card-title">今日盈亏</span>
          </div>
        </template>
        <div class="stat-value" :class="mockData.todayPnl >= 0 ? 'text-green' : 'text-red'">
          {{ mockData.todayPnl >= 0 ? '+' : '' }}${{ mockData.todayPnl.toLocaleString() }}
        </div>
        <div class="stat-desc">{{ mockData.todayPnlPercent }}%</div>
      </el-card>

      <el-card class="stat-card risk-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">盈亏比 (Risk/Reward)</span>
          </div>
        </template>
        <div class="stat-value">1 : 2.5</div>
        <div class="progress-wrapper">
          <el-progress 
            :percentage="mockData.winRate" 
            status="success" 
            :format="(percentage) => `胜率 ${percentage}%`"
            :stroke-width="8"
          />
        </div>
      </el-card>

      <el-card class="stat-card ai-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon class="card-icon"><Cpu /></el-icon>
            <span class="card-title">AI 实时决策</span>
          </div>
        </template>
        <div class="ai-logs">
          <div 
            v-for="(log, i) in mockData.aiLogs.length > 0 ? mockData.aiLogs : [
              { time: '14:30:01', msg: 'DeepSeek: BTC 15m级别出现底背离，建议建立观察仓。' },
              { time: '14:28:45', msg: 'Monitor: ETH 波动率指数飙升，暂停趋势策略。' },
              { time: '14:25:12', msg: 'System: 策略 [Alpha-1] 止盈触发，收益 +1.5%。' }
            ]" 
            :key="i" 
            class="ai-log-item"
          >
            <span class="log-time">[{{ log.time }}]</span>
            <span class="log-msg">{{ log.msg }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 主要内容区 -->
    <div class="content-grid">
      <div class="main-section">
        <!-- 净值曲线图 -->
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="section-header">
              <h3 class="section-title">近30日账户净值曲线</h3>
            </div>
          </template>
          <div ref="chartRef" class="chart-container"></div>
        </el-card>

        <!-- 当前持仓 -->
        <el-card class="table-card" shadow="never">
          <template #header>
            <div class="section-header">
              <h3 class="section-title">当前持仓</h3>
            </div>
          </template>
          <el-table :data="mockData.positions.length > 0 ? mockData.positions : [
            { symbol: 'BTCUSDT', side: 'LONG', size: '0.5', entryPrice: '64200.5', pnl: 1205.4 },
            { symbol: 'ETHUSDT', side: 'SHORT', size: '10.0', entryPrice: '3450.0', pnl: -150.2 }
          ]" stripe>
            <el-table-column prop="symbol" label="币种" width="140" />
            <el-table-column prop="side" label="方向" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.side === 'LONG' ? 'success' : 'danger'" effect="dark">
                  {{ scope.row.side }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="size" label="持仓量" width="120" />
            <el-table-column prop="entryPrice" label="开仓均价" width="140" />
            <el-table-column prop="pnl" label="未结盈亏">
              <template #default="scope">
                <span :class="scope.row.pnl > 0 ? 'pnl-positive' : 'pnl-negative'">
                  {{ scope.row.pnl > 0 ? '+' : '' }}{{ scope.row.pnl }} USDT
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 历史交易 -->
        <el-card class="table-card" shadow="never">
          <template #header>
            <div class="section-header">
              <h3 class="section-title">历史交易 (最近5笔)</h3>
            </div>
          </template>
          <el-table :data="mockData.history.length > 0 ? mockData.history : [
            { time: '11-23 10:00', symbol: 'SOLUSDT', action: 'SELL', realizedPnl: '+450.0' },
            { time: '11-23 09:15', symbol: 'DOGEUSDT', action: 'BUY', realizedPnl: '-20.5' }
          ]" size="small" stripe>
            <el-table-column prop="time" label="时间" width="140" />
            <el-table-column prop="symbol" label="币种" width="120" />
            <el-table-column prop="action" label="操作" width="100" />
            <el-table-column prop="realizedPnl" label="已结盈亏">
              <template #default="scope">
                <span :class="scope.row.realizedPnl.startsWith('+') ? 'pnl-positive' : 'pnl-negative'">
                  {{ scope.row.realizedPnl }} USDT
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <!-- 侧边栏 -->
      <div class="sidebar-section">
        <el-card class="whale-card" shadow="never">
          <template #header>
            <div class="section-header">
              <span class="whale-icon">🦈</span>
              <h3 class="section-title">链上巨鲸监控</h3>
              <el-tag size="small" type="warning" effect="dark">Live</el-tag>
            </div>
          </template>
          <div class="whale-list">
            <div 
              v-for="(whale, i) in mockData.whales.length > 0 ? mockData.whales : [
                { coin: 'BTC', amount: '2,500', time: '2m ago', from: '0x3f...a1b2', to: 'Binance Hot Wallet', alert: '大额充值预警' },
                { coin: 'USDT', amount: '50,000,000', time: '15m ago', from: 'Tether Treasury', to: '0x88...99aa', alert: '大额增发' }
              ]" 
              :key="i" 
              class="whale-item"
            >
              <div class="whale-header">
                <span class="whale-amount">{{ whale.amount }} {{ whale.coin }}</span>
                <span class="whale-time">{{ whale.time }}</span>
              </div>
              <div class="whale-details">
                <div class="whale-detail-item">From: {{ whale.from }}</div>
                <div class="whale-detail-item">To: {{ whale.to }}</div>
              </div>
              <div class="whale-alert">{{ whale.alert }}</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import * as echarts from 'echarts';
import { Cpu } from '@element-plus/icons-vue';
import { api } from '../utils/api';

// --- Dashboard Data ---
const mockData = reactive({
  balance: 125400.50,
  available: 45000.00,
  todayPnl: 1240.50,
  todayPnlPercent: 3.2,
  winRate: 72,
  aiLogs: [],
  positions: [],
  history: [],
  whales: []
});

// --- Chart Logic ---
const chartRef = ref(null);
let myChart = null;

// 加载仪表盘数据
const loadDashboardData = async () => {
  try {
    const data = await api.getDashboard();
    
    // 更新数据
    if (data.balance !== undefined) mockData.balance = data.balance;
    if (data.available !== undefined) mockData.available = data.available;
    if (data.todayPnl !== undefined) mockData.todayPnl = data.todayPnl;
    if (data.todayPnlPercent !== undefined) mockData.todayPnlPercent = data.todayPnlPercent;
    if (data.winRate !== undefined) mockData.winRate = data.winRate;
    if (data.aiLogs) mockData.aiLogs = data.aiLogs;
    if (data.positions) mockData.positions = data.positions;
    if (data.history) mockData.history = data.history;
    if (data.whales) mockData.whales = data.whales;
    
    // 更新图表
    if (myChart && data.balance !== undefined) {
      // 这里可以添加基于实际数据的图表更新逻辑
    }
  } catch (error) {
    console.error('加载仪表盘数据失败:', error);
    // 使用默认数据，不显示错误消息，避免干扰用户
  }
};

// 初始化图表
const initChart = () => {
  if (chartRef.value) {
    myChart = echarts.init(chartRef.value);
    myChart.setOption({
      title: { text: '', left: 'center' },
      tooltip: { 
        trigger: 'axis',
        backgroundColor: 'rgba(50, 50, 50, 0.9)',
        borderColor: '#667eea',
        borderWidth: 1,
        textStyle: { color: '#fff' }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: { 
        type: 'category', 
        data: ['11-01', '11-05', '11-10', '11-15', '11-20', '11-23'],
        axisLine: { lineStyle: { color: '#e5e7eb' } },
        axisLabel: { color: '#6b7280' }
      },
      yAxis: { 
        type: 'value', 
        scale: true,
        axisLine: { lineStyle: { color: '#e5e7eb' } },
        axisLabel: { color: '#6b7280' },
        splitLine: { lineStyle: { color: '#f3f4f6', type: 'dashed' } }
      },
      series: [{
        data: [100000, 105000, 103000, 115000, 120000, 125400],
        type: 'line',
        smooth: true,
        areaStyle: { 
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
            ]
          }
        },
        itemStyle: { color: '#667eea' },
        lineStyle: { width: 3, color: '#667eea' },
        symbol: 'circle',
        symbolSize: 6
      }]
    });
    window.addEventListener('resize', () => {
      if (myChart) myChart.resize();
    });
  }
};

onMounted(async () => {
  initChart();
  await loadDashboardData();
});
</script>

<style scoped>
.dashboard-container {
  max-width: 1600px;
  margin: 0 auto;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  border: none;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.balance-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.balance-card :deep(.el-card__header) {
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 16px 20px;
}

.balance-card :deep(.el-card__body) {
  padding: 20px;
}

.pnl-card.positive {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.pnl-card.negative {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.risk-card {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.ai-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  color: white;
}

.ai-card :deep(.el-card__header) {
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.ai-card :deep(.el-card__body) {
  padding: 16px 20px;
  max-height: 120px;
  overflow-y: auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  opacity: 0.9;
}

.card-icon {
  font-size: 16px;
  color: #a78bfa;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.balance-value {
  font-size: 32px;
  font-weight: 900;
}

.stat-desc {
  font-size: 13px;
  opacity: 0.8;
}

.progress-wrapper {
  margin-top: 12px;
}

.text-green {
  color: #10ff88;
}

.text-red {
  color: #ff6b6b;
}

.ai-logs {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ai-log-item {
  display: flex;
  gap: 8px;
  padding: 6px 0;
  border-left: 2px solid #a78bfa;
  padding-left: 10px;
  font-size: 12px;
  line-height: 1.5;
}

.log-time {
  color: #94a3b8;
  white-space: nowrap;
}

.log-msg {
  color: #e2e8f0;
  flex: 1;
}

/* 内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
}

.main-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-section {
  display: flex;
  flex-direction: column;
}

/* 卡片样式 */
.chart-card,
.table-card,
.whale-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: white;
}

.chart-card :deep(.el-card__header),
.table-card :deep(.el-card__header),
.whale-card :deep(.el-card__header) {
  background: #fafbfc;
  border-bottom: 1px solid #e5e7eb;
  padding: 16px 20px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.whale-icon {
  font-size: 20px;
}

.chart-container {
  width: 100%;
  height: 380px;
}

.pnl-positive {
  color: #10b981;
  font-weight: 600;
}

.pnl-negative {
  color: #ef4444;
  font-weight: 600;
}

/* 巨鲸监控 */
.whale-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.whale-item {
  padding: 14px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.whale-item:hover {
  background: #f3f4f6;
  border-color: #667eea;
  transform: translateX(4px);
}

.whale-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.whale-amount {
  font-weight: 700;
  color: #ea580c;
  font-size: 15px;
}

.whale-time {
  color: #9ca3af;
  font-size: 12px;
}

.whale-details {
  margin-bottom: 8px;
}

.whale-detail-item {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.whale-alert {
  display: inline-block;
  padding: 4px 8px;
  background: #eff6ff;
  color: #3b82f6;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 1400px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .sidebar-section {
    order: -1;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
