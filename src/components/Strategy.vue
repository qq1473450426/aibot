<template>
  <div class="strategy-container">
    <!-- 头部 -->
    <div class="strategy-header">
      <h2 class="page-title">AI 策略中心</h2>
      <el-button type="primary" size="large" @click="dialogVisible = true" class="create-btn">
        <el-icon class="mr-2"><Plus /></el-icon>
        新建策略
      </el-button>
    </div>

    <!-- 策略卡片网格 -->
    <div class="strategies-grid">
      <el-card 
        v-for="strategy in strategies" 
        :key="strategy.id" 
        class="strategy-card"
        shadow="hover"
        :class="{ active: strategy.active }"
      >
        <div class="strategy-card-header">
          <div class="strategy-info">
            <h3 class="strategy-name">{{ strategy.name }}</h3>
            <div class="strategy-tags">
              <el-tag size="small" effect="dark">{{ strategy.symbol }}</el-tag>
              <el-tag size="small" type="info" effect="dark" class="ml-2">
                {{ strategy.aiModel }}
              </el-tag>
            </div>
          </div>
          <el-switch 
            v-model="strategy.active" 
            active-text="运行" 
            inactive-text="停止"
            active-color="#10b981"
          />
        </div>

        <div class="strategy-stats">
          <div class="stat-item">
            <span class="stat-label">类型:</span>
            <span class="stat-value">{{ strategy.type }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">当前 ROI:</span>
            <span :class="strategy.roi > 0 ? 'roi-positive' : 'roi-negative'">
              {{ strategy.roi > 0 ? '+' : '' }}{{ strategy.roi }}%
            </span>
          </div>
          <div class="stat-item">
            <span class="stat-label">运行时间:</span>
            <span class="stat-value">{{ strategy.runtime }}</span>
          </div>
        </div>

        <div class="strategy-actions">
          <el-button size="small" plain>日志</el-button>
          <el-button size="small" plain>配置</el-button>
          <el-button size="small" type="danger" plain icon="Delete" circle />
        </div>
      </el-card>
    </div>

    <!-- 创建策略对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      title="创建新 AI 策略" 
      width="680px"
      class="strategy-dialog"
      align-center
    >
      <el-form :model="form" label-width="120px" class="strategy-form">
        <el-tabs v-model="activeTab" class="form-tabs">
          <el-tab-pane label="基础信息" name="base">
            <el-form-item label="策略名称">
              <el-input 
                v-model="form.name" 
                placeholder="例如: BTC 稳健定投"
                clearable
              />
            </el-form-item>
            <el-form-item label="交易对">
              <el-input 
                v-model="form.symbol" 
                placeholder="BTCUSDT"
                clearable
                style="text-transform: uppercase;"
              />
            </el-form-item>
            <el-form-item label="AI 模型">
              <el-select v-model="form.aiModel" class="w-full" placeholder="选择 AI 模型">
                <el-option label="DeepSeek V3 (推荐)" value="deepseek" />
                <el-option label="Qwen 3 (通义千问)" value="qwen3" />
              </el-select>
            </el-form-item>
            <el-form-item label="策略类型">
              <el-radio-group v-model="form.type">
                <el-radio-button label="DCA">合约定投 (DCA)</el-radio-button>
                <el-radio-button label="TREND">趋势跟踪</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="定投/马丁参数" name="params" v-if="form.type === 'DCA'">
            <el-alert 
              title="风险提示：马丁策略在极端行情下风险较高" 
              type="warning" 
              show-icon 
              class="mb-4" 
              :closable="false"
            />
            <el-form-item label="首单金额 (U)">
              <el-input-number 
                v-model="form.dca.baseOrder" 
                :min="10" 
                :step="10"
                controls-position="right"
              />
            </el-form-item>
            <el-form-item label="补仓倍数">
              <el-input-number 
                v-model="form.dca.multiplier" 
                :step="0.1" 
                :min="1.0"
                :precision="1"
                controls-position="right"
              />
              <div class="form-hint">例如 1.2 表示下一单金额是上一单的 1.2 倍</div>
            </el-form-item>
            <el-form-item label="补单间隔 (%)">
              <el-input-number 
                v-model="form.dca.stepScale" 
                :step="0.1"
                :precision="1"
                controls-position="right"
              />
              <div class="form-hint">下跌多少百分比补仓</div>
            </el-form-item>
            <el-form-item label="最大补单次数">
              <el-input-number 
                v-model="form.dca.maxOrders" 
                :max="10"
                :min="1"
                controls-position="right"
              />
            </el-form-item>
            <el-form-item label="止盈目标 (%)">
              <el-input-number 
                v-model="form.dca.takeProfit" 
                :step="0.1"
                :precision="1"
                controls-position="right"
              />
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createStrategy" :loading="creating">
            创建并运行
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { Plus, Delete } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { api } from '../utils/api';

const dialogVisible = ref(false);
const activeTab = ref('base');
const creating = ref(false);

// Strategies Data
const strategies = ref([]);

// Form Data
const form = reactive({
  name: '',
  symbol: '',
  aiModel: 'deepseek',
  type: 'DCA',
  dca: {
    baseOrder: 20,
    multiplier: 1.5,
    stepScale: 2.0,
    maxOrders: 5,
    takeProfit: 1.5
  }
});

// 加载策略列表
const loadStrategies = async () => {
  try {
    const data = await api.getStrategies();
    strategies.value = data.strategies || [];
  } catch (error) {
    console.error('加载策略失败:', error);
    ElMessage.error('加载策略列表失败');
  }
};

// 创建策略
const createStrategy = async () => {
  if (!form.name || !form.symbol) {
    ElMessage.warning('请填写策略名称和交易对');
    return;
  }

  creating.value = true;
  try {
    const strategyData = {
      id: Date.now(),
      name: form.name || '未命名策略',
      symbol: form.symbol.toUpperCase(),
      type: form.type === 'DCA' ? 'Contract DCA' : 'AI Trend',
      aiModel: form.aiModel === 'deepseek' ? 'DeepSeek' : 'Qwen3',
      roi: 0,
      runtime: '刚刚',
      active: true,
      ...form
    };
    
    const response = await api.createStrategy(strategyData);
    
    if (response.success) {
      strategies.value.push({
        id: strategyData.id,
        name: strategyData.name,
        symbol: strategyData.symbol,
        type: strategyData.type,
        aiModel: strategyData.aiModel,
        roi: 0,
        runtime: '刚刚',
        active: true
      });
      dialogVisible.value = false;
      
      // 重置表单
      form.name = '';
      form.symbol = '';
      form.aiModel = 'deepseek';
      form.type = 'DCA';
      activeTab.value = 'base';
      
      ElMessage.success(response.message || '策略创建成功，AI 开始接管交易');
    }
  } catch (error) {
    console.error('创建策略失败:', error);
    ElMessage.error('创建策略失败: ' + (error.message || '网络错误'));
  } finally {
    creating.value = false;
  }
};

// 组件挂载时加载数据
onMounted(() => {
  loadStrategies();
});
</script>

<style scoped>
.strategy-container {
  max-width: 1600px;
  margin: 0 auto;
}

.strategy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.create-btn {
  height: 40px;
  padding: 0 24px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
}

.strategies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.strategy-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  background: white;
}

.strategy-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.strategy-card.active {
  border-color: #10b981;
  background: linear-gradient(to bottom, #ffffff 0%, #f0fdf4 100%);
}

.strategy-card :deep(.el-card__body) {
  padding: 20px;
}

.strategy-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.strategy-info {
  flex: 1;
}

.strategy-name {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 10px 0;
}

.strategy-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.strategy-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.stat-label {
  color: #6b7280;
}

.stat-value {
  color: #1f2937;
  font-weight: 600;
}

.roi-positive {
  color: #10b981;
  font-weight: 700;
  font-size: 15px;
}

.roi-negative {
  color: #ef4444;
  font-weight: 700;
  font-size: 15px;
}

.strategy-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

/* 对话框样式 */
.strategy-dialog :deep(.el-dialog) {
  border-radius: 12px;
}

.strategy-dialog :deep(.el-dialog__header) {
  padding: 24px 24px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.strategy-dialog :deep(.el-dialog__title) {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

.strategy-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.strategy-form {
  padding: 0;
}

.form-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
}

.form-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 600;
  padding: 0 24px;
}

.form-hint {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .strategies-grid {
    grid-template-columns: 1fr;
  }
  
  .strategy-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .create-btn {
    width: 100%;
  }
}

.mr-2 {
  margin-right: 8px;
}

.ml-2 {
  margin-left: 8px;
}

.w-full {
  width: 100%;
}

.mb-4 {
  margin-bottom: 16px;
}
</style>
