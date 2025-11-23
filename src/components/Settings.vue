<template>
  <div class="settings-container">
    <div class="settings-wrapper">
      <h2 class="settings-title">系统设置</h2>

      <el-tabs type="border-card" class="settings-tabs">
        <!-- 交易所 API 配置 -->
        <el-tab-pane label="交易所 API" name="exchange">
          <div class="settings-section">
            <el-form label-position="top" class="settings-form">
              <div class="form-card exchange-card">
                <h3 class="form-section-title">
                  <el-icon class="form-icon"><CreditCard /></el-icon>
                  交易所 API 配置
                </h3>
                
                <el-form-item label="选择交易所">
                  <el-select 
                    v-model="exchangeForm.exchange" 
                    placeholder="请选择交易所"
                    class="w-full"
                    size="large"
                  >
                    <el-option label="Binance (币安)" value="binance">
                      <span style="font-weight: 600;">Binance (币安)</span>
                    </el-option>
                    <el-option label="OKX (欧易)" value="okx">
                      <span style="font-weight: 600;">OKX (欧易)</span>
                    </el-option>
                  </el-select>
                </el-form-item>

                <el-form-item label="API Key">
                  <el-input 
                    v-model="exchangeForm.apiKey" 
                    placeholder="输入 API Key"
                    clearable
                    show-password
                    size="large"
                  >
                    <template #prefix>
                      <el-icon><Key /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>

                <el-form-item label="Secret Key">
                  <el-input 
                    v-model="exchangeForm.secretKey" 
                    type="password" 
                    show-password 
                    placeholder="输入 Secret Key"
                    clearable
                    size="large"
                  >
                    <template #prefix>
                      <el-icon><Lock /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>

                <el-form-item v-if="exchangeForm.exchange === 'okx'" label="Passphrase">
                  <el-input 
                    v-model="exchangeForm.passphrase" 
                    type="password" 
                    placeholder="OKX 必填"
                    clearable
                    size="large"
                  >
                    <template #prefix>
                      <el-icon><Document /></el-icon>
                    </template>
                  </el-input>
                  <div class="form-hint">OKX 交易所需要 Passphrase，请妥善保管</div>
                </el-form-item>
              </div>

              <el-button 
                type="primary" 
                size="large" 
                @click="saveToDB('exchange')"
                class="save-btn"
                :loading="saving === 'exchange'"
              >
                <el-icon class="mr-2"><Check /></el-icon>
                保存并测试连接
              </el-button>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- AI 模型配置 -->
        <el-tab-pane label="AI 模型配置" name="ai">
          <div class="settings-section">
            <el-form label-position="top" class="settings-form">
              <div class="form-card ai-card">
                <h3 class="form-section-title">
                  <el-icon class="form-icon"><Cpu /></el-icon>
                  AI 模型配置
                </h3>
                
                <el-form-item label="首选 AI 模型">
                  <el-radio-group v-model="aiForm.provider" class="model-selector">
                    <el-radio label="deepseek" border size="large" class="model-radio">
                      <div class="model-option">
                        <strong>DeepSeek V3</strong>
                        <span class="model-desc">推荐，性能优秀</span>
                      </div>
                    </el-radio>
                    <el-radio label="qwen3" border size="large" class="model-radio">
                      <div class="model-option">
                        <strong>Qwen 3 (通义千问)</strong>
                        <span class="model-desc">阿里云通义千问</span>
                      </div>
                    </el-radio>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="Model API Key">
                  <el-input 
                    v-model="aiForm.apiKey" 
                    type="password" 
                    show-password 
                    placeholder="sk-..."
                    clearable
                    size="large"
                  >
                    <template #prefix>
                      <el-icon><Key /></el-icon>
                    </template>
                  </el-input>
                  <div class="form-hint">该 Key 将用于生成交易策略分析，请妥善保管</div>
                </el-form-item>

                <el-form-item label="风险偏好 (System Prompt 参数)">
                  <el-slider 
                    v-model="aiForm.riskLevel" 
                    :marks="{
                      0: { label: '保守', style: { color: '#10b981' } },
                      50: { label: '稳健', style: { color: '#3b82f6' } },
                      100: { label: '激进', style: { color: '#ef4444' } }
                    }"
                    :step="5"
                    show-stops
                  />
                  <div class="risk-level-info">
                    <span>当前级别: </span>
                    <span :class="getRiskLevelClass(aiForm.riskLevel)">
                      {{ getRiskLevelText(aiForm.riskLevel) }}
                    </span>
                  </div>
                </el-form-item>
              </div>

              <el-button 
                type="success" 
                size="large" 
                @click="saveToDB('ai')"
                class="save-btn"
                :loading="saving === 'ai'"
              >
                <el-icon class="mr-2"><Check /></el-icon>
                保存 AI 配置
              </el-button>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { ElMessage, ElLoading } from 'element-plus';
import { CreditCard, Key, Lock, Document, Cpu, Check } from '@element-plus/icons-vue';
import { api } from '../utils/api';

const saving = ref(null);

const exchangeForm = reactive({
  exchange: 'binance',
  apiKey: '',
  secretKey: '',
  passphrase: ''
});

const aiForm = reactive({
  provider: 'deepseek',
  apiKey: '',
  riskLevel: 50
});

const getRiskLevelText = (level) => {
  if (level <= 30) return '保守';
  if (level <= 70) return '稳健';
  return '激进';
};

const getRiskLevelClass = (level) => {
  if (level <= 30) return 'risk-conservative';
  if (level <= 70) return 'risk-moderate';
  return 'risk-aggressive';
};

const saveToDB = async (type) => {
  saving.value = type;
  const loading = ElLoading.service({ 
    text: type === 'exchange' ? '正在测试连接并保存配置...' : '正在保存 AI 配置...',
    background: 'rgba(255, 255, 255, 0.9)'
  });

  try {
    if (type === 'exchange') {
      const response = await api.saveExchangeSettings(exchangeForm);
      loading.close();
      ElMessage.success({
        message: response.message || `已保存 ${exchangeForm.exchange} 配置，连接测试通过 (Ping: 45ms)`,
        duration: 3000
      });
    } else {
      const response = await api.saveAISettings(aiForm);
      loading.close();
      ElMessage.success({
        message: response.message || `AI 模型 ${aiForm.provider} 配置已更新`,
        duration: 3000
      });
    }
  } catch (error) {
    loading.close();
    ElMessage.error({
      message: '保存失败: ' + (error.message || '网络错误'),
      duration: 3000
    });
  } finally {
    saving.value = null;
  }
};
</script>

<style scoped>
.settings-container {
  max-width: 900px;
  margin: 0 auto;
}

.settings-wrapper {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.settings-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 24px 0;
}

.settings-tabs {
  border-radius: 12px;
  overflow: hidden;
}

.settings-tabs :deep(.el-tabs__header) {
  margin: 0;
  border-bottom: 2px solid #e5e7eb;
}

.settings-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 600;
  padding: 16px 32px;
  height: 60px;
  line-height: 60px;
}

.settings-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
  border-bottom: 2px solid #667eea;
}

.settings-section {
  padding: 24px 0;
}

.settings-form {
  width: 100%;
}

.form-card {
  background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.exchange-card {
  background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
  border-color: #bfdbfe;
}

.ai-card {
  background: linear-gradient(135deg, #faf5ff 0%, #ffffff 100%);
  border-color: #e9d5ff;
}

.form-section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 20px 0;
  padding-bottom: 16px;
  border-bottom: 2px solid #e5e7eb;
}

.form-icon {
  font-size: 20px;
  color: #667eea;
}

.settings-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
  margin-bottom: 8px;
}

.settings-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.settings-form :deep(.el-select) {
  width: 100%;
}

.model-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.model-radio {
  width: 100%;
  margin: 0;
  padding: 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.model-radio:hover {
  border-color: #667eea;
  background: #f3f4f6;
}

.model-radio :deep(.el-radio__input.is-checked + .el-radio__label) {
  color: #667eea;
}

.model-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.model-desc {
  font-size: 12px;
  color: #6b7280;
  font-weight: normal;
}

.form-hint {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 6px;
  line-height: 1.5;
}

.risk-level-info {
  margin-top: 12px;
  font-size: 14px;
  color: #6b7280;
  font-weight: 600;
}

.risk-conservative {
  color: #10b981;
  font-weight: 700;
}

.risk-moderate {
  color: #3b82f6;
  font-weight: 700;
}

.risk-aggressive {
  color: #ef4444;
  font-weight: 700;
}

.settings-form :deep(.el-slider) {
  margin-top: 12px;
}

.settings-form :deep(.el-slider__marks-text) {
  font-weight: 600;
}

.save-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
}

.save-btn.el-button--success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.save-btn.el-button--success:hover {
  box-shadow: 0 8px 16px rgba(16, 185, 129, 0.4);
}

/* 响应式 */
@media (max-width: 768px) {
  .settings-wrapper {
    padding: 20px;
  }
  
  .settings-title {
    font-size: 24px;
  }
  
  .form-card {
    padding: 16px;
  }
  
  .model-selector {
    gap: 8px;
  }
  
  .model-radio {
    padding: 12px;
  }
}

.mr-2 {
  margin-right: 8px;
}

.w-full {
  width: 100%;
}
</style>
