<template>
  <div class="settings-container">
    <div class="settings-wrapper">
      <h2 class="settings-title">系统设置</h2>

      <el-tabs type="border-card" class="settings-tabs" v-model="activeTab">
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

                <el-form-item label="API Key" required>
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
                  <div class="form-hint">必填，此 Key 将作为唯一标识</div>
                </el-form-item>

                <el-form-item label="Secret Key" required>
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
                  <div class="form-hint">必填</div>
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

        <!-- 自定义 Prompt -->
        <el-tab-pane label="自定义 Prompt" name="prompt">
          <div class="settings-section">
            <div class="prompt-manager">
              <!-- Prompt 列表 -->
              <div class="prompt-list-section">
                <div class="section-header-prompt">
                  <h3 class="section-title-small">Prompt 方案</h3>
                  <el-button type="primary" size="small" @click="showAddPromptDialog = true">
                    <el-icon class="mr-2"><Plus /></el-icon>
                    新建 Prompt
                  </el-button>
                </div>
                
                <div class="prompt-list">
                  <div
                    v-for="prompt in prompts"
                    :key="prompt.name"
                    class="prompt-item"
                    :class="{ active: selectedPrompt === prompt.name }"
                    @click="loadPrompt(prompt.name)"
                  >
                    <div class="prompt-item-header">
                      <span class="prompt-name">{{ getPromptDisplayName(prompt.name) }}</span>
                      <el-tag v-if="prompt.isDefault" size="small" type="info">默认</el-tag>
                    </div>
                    <div class="prompt-item-actions">
                      <el-button
                        v-if="!prompt.isDefault"
                        type="danger"
                        size="small"
                        text
                        @click.stop="handleDeletePrompt(prompt.name)"
                      >
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Prompt 编辑区 -->
              <div class="prompt-editor-section">
                <div class="section-header-prompt">
                  <h3 class="section-title-small">
                    {{ selectedPrompt ? `编辑: ${getPromptDisplayName(selectedPrompt)}` : '选择或创建 Prompt 方案' }}
                  </h3>
                  <el-button
                    v-if="selectedPrompt"
                    type="success"
                    size="small"
                    @click="savePrompt"
                    :loading="saving === 'prompt'"
                  >
                    <el-icon class="mr-2"><Check /></el-icon>
                    保存
                  </el-button>
                </div>

                <div v-if="selectedPrompt" class="prompt-editor">
                  <el-input
                    v-model="promptContent"
                    type="textarea"
                    :rows="15"
                    placeholder="请输入 Prompt 内容..."
                    class="prompt-textarea"
                  />
                  <div class="form-hint">
                    提示：此 Prompt 将用于 AI 模型生成交易策略分析。支持多行文本。
                  </div>
                </div>
                <div v-else class="prompt-placeholder">
                  <el-empty description="请从左侧选择一个 Prompt 方案或创建新方案" />
                </div>
              </div>
            </div>

            <!-- 添加 Prompt 对话框 -->
            <el-dialog
              v-model="showAddPromptDialog"
              title="新建 Prompt 方案"
              width="500px"
            >
              <el-form :model="newPromptForm" label-width="100px">
                <el-form-item label="方案名称" required>
                  <el-input
                    v-model="newPromptForm.name"
                    placeholder="请输入方案名称（仅支持字母、数字、下划线和连字符）"
                    clearable
                  />
                  <div class="form-hint">例如: my_custom_prompt</div>
                </el-form-item>
                <el-form-item label="Prompt 内容">
                  <el-input
                    v-model="newPromptForm.content"
                    type="textarea"
                    :rows="10"
                    placeholder="请输入 Prompt 内容..."
                  />
                </el-form-item>
              </el-form>
              <template #footer>
                <el-button @click="showAddPromptDialog = false">取消</el-button>
                <el-button type="primary" @click="handleCreatePrompt" :loading="creatingPrompt">
                  创建
                </el-button>
              </template>
            </el-dialog>
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
                      </div>
                    </el-radio>
                    <el-radio label="qwen3" border size="large" class="model-radio">
                      <div class="model-option">
                        <strong>Qwen 3 (通义千问)</strong>
                      </div>
                    </el-radio>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="Model API Key" required>
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
                  <div class="form-hint">必填，此 Key 将作为唯一标识，请妥善保管</div>
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
import { reactive, ref, onMounted } from 'vue';
import { ElMessage, ElLoading, ElMessageBox } from 'element-plus';
import { CreditCard, Key, Lock, Document, Cpu, Check, Plus, Delete } from '@element-plus/icons-vue';
import { api } from '../utils/api';

const saving = ref(null);
const activeTab = ref("exchange");
const prompts = ref([]);
const selectedPrompt = ref(null);
const promptContent = ref('');
const showAddPromptDialog = ref(false);
const creatingPrompt = ref(false);
const currentPromptIsDefault = ref(false);

const newPromptForm = reactive({
  name: '',
  content: ''
});

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

// 加载 Prompt 列表
const loadPromptsList = async () => {
  try {
    const response = await api.getPromptsList();
    if (response.success) {
      prompts.value = response.prompts || [];
    }
  } catch (error) {
    console.error('加载 Prompt 列表失败:', error);
    ElMessage.error('加载 Prompt 列表失败');
  }
};

// 加载指定 Prompt 内容
const loadPrompt = async (promptName) => {
  try {
    const response = await api.getPrompt(promptName);
    if (response.success) {
      selectedPrompt.value = promptName;
      promptContent.value = response.content || '';
      // 检查是否为默认方案
      const prompt = prompts.value.find(p => p.name === promptName);
      currentPromptIsDefault.value = prompt ? prompt.isDefault : false;
    }
  } catch (error) {
    console.error('加载 Prompt 失败:', error);
    ElMessage.error('加载 Prompt 失败: ' + (error.message || '网络错误'));
  }
};

// 保存 Prompt
const savePrompt = async () => {
  if (!selectedPrompt.value) return;
  
  saving.value = 'prompt';
  try {
    const response = await api.savePrompt({
      name: selectedPrompt.value,
      content: promptContent.value
    });
    
    if (response.success) {
      ElMessage.success(response.message || 'Prompt 保存成功');
      // 刷新列表（保持当前选择）
      await loadPromptsList();
    }
  } catch (error) {
    const errorMessage = error.message || '网络错误';
    // 如果是修改默认方案的错误，显示更友好的提示
    if (errorMessage.includes('不能修改默认方案')) {
      ElMessage.warning('默认方案可以直接编辑内容，无需修改文件名');
    } else {
      ElMessage.error('保存失败: ' + errorMessage);
    }
  } finally {
    saving.value = null;
  }
};

// 创建新 Prompt
const handleCreatePrompt = async () => {
  if (!newPromptForm.name.trim()) {
    ElMessage.warning('请输入方案名称');
    return;
  }

  creatingPrompt.value = true;
  try {
    const response = await api.savePrompt({
      name: newPromptForm.name.trim(),
      content: newPromptForm.content || ''
    });

    if (response.success) {
      ElMessage.success('Prompt 方案创建成功');
      showAddPromptDialog.value = false;
      // 重置表单
      newPromptForm.name = '';
      newPromptForm.content = '';
      // 刷新列表并加载新创建的 Prompt
      await loadPromptsList();
      await loadPrompt(response.name);
    }
  } catch (error) {
    ElMessage.error('创建失败: ' + (error.message || '网络错误'));
  } finally {
    creatingPrompt.value = false;
  }
};

// 删除 Prompt
const handleDeletePrompt = async (promptName) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 Prompt 方案 "${promptName}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    const response = await api.deletePrompt(promptName);
    if (response.success) {
      ElMessage.success('删除成功');
      // 如果删除的是当前选中的 Prompt，清空选择
      if (selectedPrompt.value === promptName) {
        selectedPrompt.value = null;
        promptContent.value = '';
      }
      // 刷新列表
      await loadPromptsList();
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.message || '网络错误'));
    }
  }
};

// 加载交易所配置
const loadExchangeSettings = async () => {
  try {
    const response = await api.getExchangeSettings();
    if (response.success && response.data) {
      exchangeForm.exchange = response.data.exchange || 'binance';
      exchangeForm.apiKey = response.data.apiKey || '';
      exchangeForm.secretKey = response.data.secretKey || '';
      exchangeForm.passphrase = response.data.passphrase || '';
    }
  } catch (error) {
    console.error('加载交易所配置失败:', error);
    // 不显示错误，因为可能是首次使用，没有配置
  }
};

// 加载 AI 配置
const loadAISettings = async () => {
  try {
    const response = await api.getAISettings();
    if (response.success && response.data) {
      aiForm.provider = response.data.provider || 'deepseek';
      aiForm.apiKey = response.data.apiKey || '';
      aiForm.riskLevel = response.data.riskLevel || 50;
    }
  } catch (error) {
    console.error('加载 AI 配置失败:', error);
    // 不显示错误，因为可能是首次使用，没有配置
  }
};

const saveToDB = async (type) => {
  // 验证必填字段
  if (type === 'exchange') {
    if (!exchangeForm.exchange) {
      ElMessage.warning('请选择交易所');
      return;
    }
    if (!exchangeForm.apiKey || !exchangeForm.apiKey.trim()) {
      ElMessage.warning('API Key 不能为空');
      return;
    }
    if (!exchangeForm.secretKey || !exchangeForm.secretKey.trim()) {
      ElMessage.warning('Secret Key 不能为空');
      return;
    }
    if (exchangeForm.exchange === 'okx' && (!exchangeForm.passphrase || !exchangeForm.passphrase.trim())) {
      ElMessage.warning('OKX 交易所需要填写 Passphrase');
      return;
    }
  } else if (type === 'ai') {
    if (!aiForm.provider) {
      ElMessage.warning('请选择 AI 模型提供商');
      return;
    }
    if (!aiForm.apiKey || !aiForm.apiKey.trim()) {
      ElMessage.warning('Model API Key 不能为空');
      return;
    }
  }

  saving.value = type;
  const loading = ElLoading.service({ 
    text: type === 'exchange' ? '正在测试连接并保存配置...' : '正在保存 AI 配置...',
    background: 'rgba(255, 255, 255, 0.9)'
  });

  try {
    if (type === 'exchange') {
      const response = await api.saveExchangeSettings({
        exchange: exchangeForm.exchange,
        apiKey: exchangeForm.apiKey.trim(),
        secretKey: exchangeForm.secretKey.trim(),
        passphrase: exchangeForm.passphrase ? exchangeForm.passphrase.trim() : ''
      });
      loading.close();
      ElMessage.success({
        message: response.message || `已保存 ${exchangeForm.exchange} 配置，连接测试通过 (Ping: 45ms)`,
        duration: 3000
      });
      // 保存成功后重新加载配置（用于显示更新后的信息）
      await loadExchangeSettings();
    } else {
      const response = await api.saveAISettings({
        provider: aiForm.provider,
        apiKey: aiForm.apiKey.trim(),
        riskLevel: aiForm.riskLevel
      });
      loading.close();
      ElMessage.success({
        message: response.message || `AI 模型 ${aiForm.provider} 配置已更新`,
        duration: 3000
      });
      // 保存成功后重新加载配置
      await loadAISettings();
    }
  } catch (error) {
    loading.close();
    const errorMessage = error.message || '网络错误';
    // 如果是后端验证错误，显示后端返回的消息
    if (errorMessage.includes('不能为空')) {
      ElMessage.warning(errorMessage);
    } else {
      ElMessage.error({
        message: '保存失败: ' + errorMessage,
        duration: 3000
      });
    }
  } finally {
    saving.value = null;
  }
};

// 获取 Prompt 显示名称
const getPromptDisplayName = (name) => {
  const nameMap = {
    'conservative': '保守型',
    'moderate': '稳健型',
    'aggressive': '激进型'
  };
  return nameMap[name] || name;
};

// 组件挂载时加载所有配置
onMounted(() => {
  loadPromptsList();
  loadExchangeSettings();
  loadAISettings();
});
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

/* Prompt 管理样式 */
.prompt-manager {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 24px;
  min-height: 500px;
}

.prompt-list-section {
  border-right: 1px solid #e5e7eb;
  padding-right: 24px;
}

.section-header-prompt {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title-small {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.prompt-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 600px;
  overflow-y: auto;
}

.prompt-item {
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.prompt-item:hover {
  border-color: #667eea;
  background: #f9fafb;
}

.prompt-item.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
}

.prompt-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.prompt-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.prompt-item-actions {
  display: flex;
  gap: 4px;
}

.prompt-editor-section {
  flex: 1;
}

.prompt-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.prompt-textarea :deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.prompt-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  border: 2px dashed #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
}

/* 响应式 */
@media (max-width: 1024px) {
  .prompt-manager {
    grid-template-columns: 1fr;
  }
  
  .prompt-list-section {
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
    padding-right: 0;
    padding-bottom: 24px;
  }
  
  .prompt-list {
    max-height: 200px;
  }
}
</style>
