<template>
  <div class="strategy-container">
    <div class="strategy-header">
      <h2 class="page-title">AI 策略中心</h2>
      <el-button type="primary" size="large" class="create-btn" @click="openCreateDialog">
        <el-icon class="mr-2"><Plus /></el-icon>
        新建策略
      </el-button>
    </div>

    <el-skeleton :loading="plansLoading" animated :count="2">
      <template #template>
        <div class="skeleton-card"></div>
      </template>
      <template #default>
        <div v-if="plans.length" class="plans-grid">
          <el-card
            v-for="plan in plans"
            :key="plan.id"
            class="plan-card"
            shadow="hover"
          >
            <div class="plan-card-header">
              <div>
                <div class="plan-type">{{ formatPlanType(plan.planType) }}</div>
                <h3 class="plan-name">{{ plan.name }}</h3>
                <div class="plan-tags">
                  <el-tag size="small" effect="dark">{{ plan.exchange?.toUpperCase() }}</el-tag>
                  <el-tag v-if="plan.symbol" size="small" type="info" effect="dark">{{ plan.symbol }}</el-tag>
                </div>
              </div>
              <div class="plan-meta">
                <el-tag size="small" type="info">{{ plan.createdAt }}</el-tag>
              </div>
            </div>
            <div class="plan-card-body">
              <template v-if="plan.planType === 'ai_trader'">
                <div class="plan-row">
                  <span>AI 模型</span>
                  <strong>{{ formatAIModel(plan.aiModel) }}</strong>
                </div>
                <div class="plan-row" v-if="plan.promptName">
                  <span>Prompt</span>
                  <span>{{ plan.promptDisplayName || formatPromptName(plan.promptName) }}</span>
                </div>
                <div class="plan-row" v-if="plan.positionMode">
                  <span>仓位模式</span>
                  <span>{{ formatPositionMode(plan.positionMode) }} · {{ plan.leverage }}x</span>
                </div>
                <div class="plan-row" v-if="plan.amount">
                  <span>投入金额</span>
                  <span>{{ plan.amount }} USDT</span>
                </div>
              </template>
              <template v-else>
                <div class="plan-row">
                  <span>仓位模式</span>
                  <span>{{ formatPositionMode(plan.positionMode) }} · {{ plan.leverage }}x</span>
                </div>
                <div class="plan-row">
                  <span>方向</span>
                  <span>{{ formatDirection(plan.direction) }}</span>
                </div>
                <div class="plan-row">
                  <span>总资金</span>
                  <span>{{ plan.totalFunds }} USDT</span>
                </div>
                <div class="plan-row">
                  <span>单次投入</span>
                  <span>{{ plan.singleInvestment }} USDT</span>
                </div>
                <div class="plan-row">
                  <span>定投间隔</span>
                  <span>{{ plan.interval }}</span>
                </div>
              </template>
            </div>
            <div class="plan-card-footer">
              <el-tag size="small" type="warning">未运行</el-tag>
            </div>
          </el-card>
        </div>
        <el-empty v-else description="暂无策略计划">
          <el-button type="primary" @click="openCreateDialog">新建策略</el-button>
        </el-empty>
      </template>
    </el-skeleton>

    <el-dialog
      v-model="dialogVisible"
      title="新建策略计划"
      width="720px"
      class="strategy-dialog"
      align-center
    >
      <el-tabs v-model="dialogActiveTab" class="form-tabs">
        <el-tab-pane label="AI 交易员" name="ai">
          <el-form label-width="120px" class="strategy-form">
            <el-form-item label="策略名称">
              <el-input v-model="aiStrategyForm.name" placeholder="例如：BTC AI 马丁" clearable />
            </el-form-item>
            <el-form-item label="交易所">
              <el-select v-model="aiStrategyForm.exchange" class="w-full">
                <el-option label="Binance (币安)" value="binance" />
                <el-option label="OKX (欧易)" value="okx" />
              </el-select>
            </el-form-item>
            <el-form-item label="仓位模式">
              <el-radio-group v-model="aiStrategyForm.positionMode">
                <el-radio-button label="cross">全仓</el-radio-button>
                <el-radio-button label="isolated">逐仓</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="杠杆倍率">
              <el-input-number v-model="aiStrategyForm.leverage" :min="1" :max="125" :step="1" />
              <div class="form-hint">默认 10x，可根据策略需求调整</div>
            </el-form-item>
            <el-form-item label="交易对">
              <el-input
                v-model="aiStrategyForm.symbol"
                placeholder="例如：BTCUSDT"
                clearable
                style="text-transform: uppercase;"
              />
            </el-form-item>
            <el-form-item label="投入金额 (USDT)">
              <el-input-number v-model="aiStrategyForm.amount" :min="10" :step="10" />
            </el-form-item>
            <el-form-item label="AI 模型">
              <el-select v-model="aiStrategyForm.aiModel" class="w-full">
                <el-option label="DeepSeek V3" value="deepseek" />
                <el-option label="Qwen 3" value="qwen3" />
              </el-select>
            </el-form-item>
            <el-form-item label="提示词 Prompt">
              <el-select
                v-model="aiStrategyForm.promptName"
                class="w-full"
                :loading="promptsLoading"
                placeholder="选择策略提示词"
                filterable
                clearable
              >
                <el-option
                  v-for="prompt in promptOptions"
                  :key="prompt.name"
                  :label="formatPromptName(prompt.name)"
                  :value="prompt.name"
                />
              </el-select>
              <div class="form-hint">可在系统设置 > 自定义 Prompt 中新增或修改提示词</div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="合约定投" name="dca">
          <el-form label-width="120px" class="strategy-form">
            <el-form-item label="策略名称">
              <el-input v-model="dcaStrategyForm.name" placeholder="例如：ETH 周期定投" clearable />
            </el-form-item>
            <el-form-item label="交易所">
              <el-select v-model="dcaStrategyForm.exchange" class="w-full">
                <el-option label="Binance (币安)" value="binance" />
                <el-option label="OKX (欧易)" value="okx" />
              </el-select>
            </el-form-item>
            <el-form-item label="仓位模式">
              <el-radio-group v-model="dcaStrategyForm.positionMode">
                <el-radio-button label="cross">全仓</el-radio-button>
                <el-radio-button label="isolated">逐仓</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="杠杆倍率">
              <el-input-number v-model="dcaStrategyForm.leverage" :min="1" :max="50" />
              <div class="form-hint">默认 5x，建议根据风险偏好调整</div>
            </el-form-item>
            <el-form-item label="交易对">
              <el-input
                v-model="dcaStrategyForm.symbol"
                placeholder="例如：ETHUSDT"
                clearable
                style="text-transform: uppercase;"
              />
            </el-form-item>
            <el-form-item label="总资金 (USDT)">
              <el-input-number v-model="dcaStrategyForm.totalFunds" :min="100" :step="50" />
            </el-form-item>
            <el-form-item label="单次投入 (USDT)">
              <el-input-number v-model="dcaStrategyForm.singleInvestment" :min="10" :step="10" />
            </el-form-item>
            <el-form-item label="定投间隔">
              <el-input
                v-model="dcaStrategyForm.interval"
                placeholder="例如：每 6 小时 / 每天 10:00"
                clearable
              />
            </el-form-item>
            <el-form-item label="方向">
              <el-radio-group v-model="dcaStrategyForm.direction">
                <el-radio-button label="long">做多</el-radio-button>
                <el-radio-button label="short">做空</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="savingPlan" @click="createPlan">
            保存策略
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { Plus } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { api } from '../utils/api';

const dialogVisible = ref(false);
const dialogActiveTab = ref('ai');
const savingPlan = ref(false);

const plans = ref([]);
const plansLoading = ref(false);

const promptOptions = ref([]);
const promptsLoading = ref(false);

const aiStrategyForm = reactive({
  name: '',
  exchange: 'binance',
  positionMode: 'cross',
  leverage: 10,
  symbol: '',
  amount: 100,
  aiModel: 'deepseek',
  promptName: ''
});

const dcaStrategyForm = reactive({
  name: '',
  exchange: 'binance',
  positionMode: 'cross',
  leverage: 5,
  symbol: '',
  totalFunds: 500,
  singleInvestment: 50,
  interval: '每天 10:00',
  direction: 'long'
});

const loadPlans = async () => {
  plansLoading.value = true;
  try {
    const response = await api.getPlans();
    plans.value = response.success ? (response.plans || []) : [];
  } catch (error) {
    ElMessage.error('加载策略计划失败');
  } finally {
    plansLoading.value = false;
  }
};

const loadPrompts = async () => {
  promptsLoading.value = true;
  try {
    const response = await api.getPromptsList();
    if (response.success) {
      promptOptions.value = response.prompts || [];
      if (!aiStrategyForm.promptName && promptOptions.value.length) {
        aiStrategyForm.promptName = promptOptions.value[0].name;
      }
    }
  } catch (error) {
    ElMessage.error('加载 Prompt 列表失败');
  } finally {
    promptsLoading.value = false;
  }
};

const resetForms = () => {
  dialogActiveTab.value = 'ai';
  Object.assign(aiStrategyForm, {
    name: '',
    exchange: 'binance',
    positionMode: 'cross',
    leverage: 10,
    symbol: '',
    amount: 100,
    aiModel: 'deepseek',
    promptName: promptOptions.value[0]?.name || ''
  });
  Object.assign(dcaStrategyForm, {
    name: '',
    exchange: 'binance',
    positionMode: 'cross',
    leverage: 5,
    symbol: '',
    totalFunds: 500,
    singleInvestment: 50,
    interval: '每天 10:00',
    direction: 'long'
  });
};

const openCreateDialog = async () => {
  resetForms();
  dialogVisible.value = true;
  if (!promptOptions.value.length) {
    await loadPrompts();
  }
};

const validateAiStrategy = () => {
  if (!aiStrategyForm.name.trim()) {
    ElMessage.warning('请输入策略名称');
    return false;
  }
  if (!aiStrategyForm.symbol.trim()) {
    ElMessage.warning('请输入交易对');
    return false;
  }
  if (!aiStrategyForm.promptName) {
    ElMessage.warning('请选择 Prompt');
    return false;
  }
  return true;
};

const validateDcaStrategy = () => {
  if (!dcaStrategyForm.name.trim()) {
    ElMessage.warning('请输入策略名称');
    return false;
  }
  if (!dcaStrategyForm.symbol.trim()) {
    ElMessage.warning('请输入交易对');
    return false;
  }
  if (!dcaStrategyForm.interval.trim()) {
    ElMessage.warning('请输入定投间隔');
    return false;
  }
  return true;
};

const createPlan = async () => {
  let payload = null;
  if (dialogActiveTab.value === 'ai') {
    if (!validateAiStrategy()) return;
    payload = {
      planType: 'ai_trader',
      name: aiStrategyForm.name.trim(),
      exchange: aiStrategyForm.exchange,
      positionMode: aiStrategyForm.positionMode,
      leverage: aiStrategyForm.leverage,
      symbol: aiStrategyForm.symbol.trim().toUpperCase(),
      amount: Number(aiStrategyForm.amount),
      aiModel: aiStrategyForm.aiModel,
      promptName: aiStrategyForm.promptName,
      promptDisplayName: formatPromptName(aiStrategyForm.promptName)
    };
  } else {
    if (!validateDcaStrategy()) return;
    payload = {
      planType: 'contract_dca',
      name: dcaStrategyForm.name.trim(),
      exchange: dcaStrategyForm.exchange,
      positionMode: dcaStrategyForm.positionMode,
      leverage: dcaStrategyForm.leverage,
      symbol: dcaStrategyForm.symbol.trim().toUpperCase(),
      totalFunds: Number(dcaStrategyForm.totalFunds),
      singleInvestment: Number(dcaStrategyForm.singleInvestment),
      interval: dcaStrategyForm.interval.trim(),
      direction: dcaStrategyForm.direction
    };
  }

  savingPlan.value = true;
  try {
    const response = await api.createPlan(payload);
    if (response.success) {
      ElMessage.success(response.message || '策略保存成功');
      dialogVisible.value = false;
      await loadPlans();
    }
  } catch (error) {
    ElMessage.error('保存策略失败: ' + (error.message || '网络错误'));
  } finally {
    savingPlan.value = false;
  }
};

const formatPlanType = (type) =>
  type === 'ai_trader' ? 'AI 交易员' : '合约定投';

const formatPositionMode = (mode) =>
  mode === 'cross' ? '全仓' : '逐仓';

const formatDirection = (dir) =>
  dir === 'long' ? '做多' : '做空';

const formatAIModel = (model) =>
  model === 'deepseek' ? 'DeepSeek' : 'Qwen3';

const formatPromptName = (name) => {
  const map = {
    conservative: '保守型 Prompt',
    moderate: '稳健型 Prompt',
    aggressive: '激进型 Prompt'
  };
  return map[name] || name;
};

onMounted(async () => {
  await Promise.all([loadPlans(), loadPrompts()]);
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

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.plan-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.plan-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.plan-card :deep(.el-card__body) {
  padding: 20px;
}

.plan-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.plan-type {
  font-size: 13px;
  color: #6366f1;
  font-weight: 600;
}

.plan-name {
  margin: 4px 0;
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

.plan-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.plan-card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 14px;
}

.plan-row {
  display: flex;
  justify-content: space-between;
  color: #374151;
}

.plan-row span:first-child {
  color: #6b7280;
}

.plan-card-footer {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.strategy-dialog :deep(.el-dialog) {
  border-radius: 12px;
}

.strategy-dialog :deep(.el-dialog__body) {
  padding: 0 24px 24px;
}

.strategy-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.form-hint {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.skeleton-card {
  height: 200px;
  border-radius: 12px;
  background: linear-gradient(90deg, #f4f4f5 25%, #e5e7eb 37%, #f4f4f5 63%);
  margin-bottom: 16px;
}

.form-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .strategy-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .create-btn {
    width: 100%;
  }

  .plans-grid {
    grid-template-columns: 1fr;
  }
}

.mr-2 {
  margin-right: 8px;
}

.w-full {
  width: 100%;
}
</style>








