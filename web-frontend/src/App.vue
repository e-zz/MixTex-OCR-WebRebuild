<template>
  <div id="app">
    <!-- 全局加载状态 -->
    <GlobalLoading ref="globalLoadingRef" />
    
    <el-container class="main-container">
      <!-- 顶部标题栏 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="header-left">
            <h1>MixTeX OCR</h1>
          </div>
          <div class="header-right">
            <el-button 
              type="primary" 
              size="small" 
              @click="downloadAndSetupModel" 
              :loading="isDownloading"
            >
              <el-icon><Download /></el-icon>
              下载并设置模型
            </el-button>
            
            <!-- Add the close/restart dropdown here -->
            <el-button 
              type="danger" 
              size="small"
              @click="handleShutdown"
            >
              <el-icon><Close /></el-icon>
              关闭应用
            </el-button>
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="main-content">
        <el-row :gutter="20" class="content-row">
          <!-- 左侧功能区域 -->
          <el-col :span="12" class="left-panel">
            <el-card class="function-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon>
                    <Upload />
                  </el-icon>
                  <span>图片识别</span>
                </div>
              </template>

              <!-- 剪贴板粘贴 -->
              <div class="function-content">
                <ClipboardUpload ref="clipboardUploadRef" />
              </div>
            </el-card>
          </el-col>

          <!-- 右侧结果显示区域 -->
          <el-col :span="12" class="right-panel">
            <el-card class="result-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon>
                    <Document />
                  </el-icon>
                  <span>识别结果</span>

                </div>
              </template>

              <!-- 结果展示区域 -->
              <div class="result-content">
                <div v-if="!hasCurrentImage" class="empty-state">
                  <el-icon class="empty-icon">
                    <Document />
                  </el-icon>
                  <p>暂无识别结果</p>
                  <p class="empty-tip">请在左侧上传或粘贴图片进行识别</p>
                </div>

                <div v-else class="current-result">
                  <!-- 图片显示 -->
                  <div class="result-image-section">
                    <h4>识别图片</h4>
                    <img :src="currentResult.imageUrl" alt="识别图片" class="result-image" />
                  </div>

                  <!-- 结果显示 -->
                  <div class="result-latex-section">
                    <h4>识别结果</h4>
                    <el-input v-model="currentResult.latex" type="textarea" :rows="6" readonly class="latex-input" />
                    <div class="result-actions">
                      <el-button type="primary" size="small" @click="copyToClipboard(currentResult.latex)">
                        <el-icon>
                          <CopyDocument />
                        </el-icon>
                        复制结果
                      </el-button>
                      <el-button type="primary" size="small" @click="reRecognize" :disabled="!hasCurrentImage">
                        重新识别
                      </el-button>
                      <el-button type="success" size="small" @click="submitFeedback(currentResult, 'Perfect')">
                        👍 完美
                      </el-button>
                      <el-button type="warning" size="small" @click="submitFeedback(currentResult, 'Mistake')">
                        😕 失误
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>

      <!-- 底部状态栏 -->
      <el-footer class="app-footer">
        <div class="footer-content">
          <div class="footer-left">
            <span>基于 MixTeX 模型 | 支持数学公式识别</span>
          </div>
          <div class="footer-right">
            <el-button type="text" size="small" @click="showAbout">
              关于
            </el-button>
          </div>
        </div>
      </el-footer>
    </el-container>

    <!-- 关于弹窗 -->
    <AboutPopup ref="aboutPopupRef" />
  </div>
</template>

<script setup>
import { ref, computed, provide } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Upload, 
  Document, 
  CopyDocument, 
  Close, 
  Download 
  // Remove Refresh since we're not using it anymore
} from '@element-plus/icons-vue'
import ClipboardUpload from './components/ClipboardUpload.vue'
import GlobalLoading from './components/GlobalLoading.vue'
import AboutPopup from './components/AboutPopup.vue'

// 响应式数据
const currentResult = ref(null)
const clipboardUploadRef = ref(null)
const globalLoadingRef = ref(null)
const aboutPopupRef = ref(null)

// 计算属性
const hasCurrentImage = computed(() => currentResult.value !== null)

// Add new state for download button
const isDownloading = ref(false)

// Model download and setup function
const downloadAndSetupModel = async () => {
  try {
    // Confirm with user before proceeding
    await ElMessageBox.confirm(
      '将自动从GitHub下载MixTeX模型文件并设置。此过程可能需要几分钟时间，取决于您的网络速度。',
      '下载模型',
      {
        confirmButtonText: '确认下载',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    isDownloading.value = true
    showGlobalLoading('正在下载模型文件...')
    
    // Call backend endpoint to handle download, unzip and setup
    const response = await fetch('http://localhost:8000/download_model', {
      method: 'POST'
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '下载模型失败')
    }
    
    const result = await response.json()
    hideGlobalLoading()
    isDownloading.value = false
    
    ElMessage.success('模型下载并设置成功！')
  } catch (error) {
    hideGlobalLoading()
    isDownloading.value = false
    
    // Don't show error if user cancelled
    if (error.toString().includes('cancel')) return
    
    ElMessage.error(`模型下载失败: ${error.message || error}`)
  }
}

const handleShutdown = async () => {
  try {
    // Confirm before shutting down
    await ElMessageBox.confirm(
      '确定要关闭应用吗？',
      '关闭应用',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    showGlobalLoading('正在关闭应用...')
    
    // Call shutdown API
    await fetch('http://localhost:8000/shutdown', {
      method: 'POST'
    })
    
    // The application should close itself, but just in case:
    ElMessage.success('应用已关闭')
    setTimeout(() => {
      window.close()
    }, 1000)
    
  } catch (error) {
    hideGlobalLoading()
    
    // Don't show error if user cancelled
    if (error.toString().includes('cancel')) return
    
    ElMessage.error(`操作失败: ${error.message || error}`)
  }
}

// 方法
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    // 降级方案
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    ElMessage.success('已复制到剪贴板')
  }
}

const submitFeedback = async (result, feedback) => {
  try {
    const formData = new FormData()
    formData.append('latex_text', result.latex)
    formData.append('feedback', feedback)
    if (result.imageUrl) {
      formData.append('image_data', result.imageUrl)
    }

    const response = await fetch('http://localhost:8000/feedback', {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      ElMessage.success('反馈已提交,虽然没什么用')
    } else {
      ElMessage.error('反馈提交失败')
    }
  } catch (error) {
    ElMessage.error('反馈提交失败')
  }
}

const showAbout = () => {
  if (aboutPopupRef.value) {
    aboutPopupRef.value.show()
  }
}


// 重新识别
const reRecognize = async () => {
  if (clipboardUploadRef.value) {
    await clipboardUploadRef.value.reRecognize()
  }
}

// 添加结果到列表（只保存最新的）
const addResult = (imageUrl, latex) => {
  const now = new Date()
  const timeStr = now.toLocaleTimeString()

  currentResult.value = {
    imageUrl,
    latex,
    time: timeStr
  }
}

// 显示全局加载状态
const showGlobalLoading = (message = '正在识别...') => {
  if (globalLoadingRef.value) {
    globalLoadingRef.value.show(message)
  }
}

// 隐藏全局加载状态
const hideGlobalLoading = () => {
  if (globalLoadingRef.value) {
    globalLoadingRef.value.hide()
  }
}

// 提供给子组件
provide('addResult', addResult)
provide('showGlobalLoading', showGlobalLoading)
provide('hideGlobalLoading', hideGlobalLoading)
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 0;
  padding: 0;
  height: 100vh;
  background: #ffffff;
}

.main-container {
  height: 100vh;
  background: transparent;
}

.app-header {
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  height: auto;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
}

.header-right {
  display: flex;
  gap: 10px;
  /* Ensure buttons in header align properly */
  align-items: center;
}

.header-left h1 {
  margin: 0 0 5px 0;
  font-size: 2.2em;
  font-weight: 300;
  color: #333;
}

.header-left p {
  margin: 0;
  font-size: 1em;
  color: #666;
  opacity: 0.8;
}

.main-content {
  padding: 20px;
  background: transparent;
}

.content-row {
  height: calc(100vh - 200px);
}

.left-panel,
.right-panel {
  height: 100%;
}

.function-card,
.result-card {
  height: 100%;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  background: #ffffff;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.function-content {
  height: calc(100% - 60px);
  overflow: hidden;
}

.result-content {
  height: calc(100% - 60px);
  overflow-y: auto;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-tip {
  font-size: 14px;
  opacity: 0.7;
}

.current-result {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.result-image-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 5px;
}

.result-image-section h4 {
  margin: 0;
  color: #333;
  font-size: 14px;
  font-weight: 600;
}

.result-image {
  max-width: 100%;
  max-height: 250px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  object-fit: contain;
  align-self: center;
}

.result-latex-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.result-latex-section h4 {
  margin: 0;
  color: #333;
  font-size: 14px;
  font-weight: 600;
}

.latex-input {
  font-family: 'Courier New', monospace;
}

.result-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.app-footer {
  background: #ffffff;
  border-top: 1px solid #e4e7ed;
  padding: 0;
  height: auto;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  color: #666;
  font-size: 14px;
}

.about-content,
.help-content {
  line-height: 1.6;
}

.about-content h3,
.help-content h3 {
  color: #333;
  margin-bottom: 16px;
}

.about-content ul,
.help-content ul {
  padding-left: 20px;
}

.about-content li,
.help-content li {
  margin-bottom: 8px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .content-row {
    flex-direction: column;
  }

  .left-panel,
  .right-panel {
    width: 100%;
    margin-bottom: 20px;
  }

  .content-row {
    height: auto;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }

  .header-left h1 {
    font-size: 1.8em;
  }

  .main-content {
    padding: 10px;
  }

  .footer-content {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
}

/* 滚动条样式 */
.result-content::-webkit-scrollbar {
  width: 6px;
}

.result-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.result-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.result-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>