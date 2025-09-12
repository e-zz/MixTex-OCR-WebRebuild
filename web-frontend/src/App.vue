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
              style="margin-right: 40px;"
            >
              <el-icon><Download /></el-icon>
              {{ $t('header.downloadModel') }}
            </el-button>
            
            <div class="lang-toggle-wrapper">
              <!-- <span class="lang-label">EN</span> -->
              <el-switch
                v-model="languageSwitch"
                @change="onLanguageSwitchChange"
                class="lang-switch"
                inline-prompt
                active-text="中文"
                inactive-text="EN"
              />
              <span class="lang-label">{{ $t("header.alternativeLanguage") }}</span>
            </div>
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="main-content">
        <el-row :gutter="20" class="content-row">
          <!-- 左侧功能区域 -->
          <el-col :xs="24" :sm="24" :md="24" :lg="12" :xl="12" class="left-panel">
            <el-card class="function-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon>
                    <Upload />
                  </el-icon>
                  <span>{{ $t('clipboard.title') }}</span>
                </div>
              </template>

              <!-- 剪贴板粘贴 -->
              <div class="function-content">
                <ClipboardUpload ref="clipboardUploadRef" />
              </div>
            </el-card>
          </el-col>

          <!-- 右侧结果显示区域 -->
          <el-col :xs="24" :sm="24" :md="24" :lg="12" :xl="12" class="right-panel">
            <el-card class="result-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon>
                    <Document />
                  </el-icon>
                  <span>{{ $t('messages.recognitionResult') }}</span>

                </div>
              </template>

              <!-- 结果展示区域 -->
              <div class="result-content">
                <div v-if="!hasCurrentImage" class="empty-state">
                  <el-icon class="empty-icon">
                    <Document />
                  </el-icon>
                  <p>{{ $t('messages.recognitionNoResult') }}</p>
                  <p class="empty-tip">{{ $t('messages.uploadReminder') }}</p>
                </div>

                <div v-else class="current-result">
                  <!-- 图片显示 -->
                  <div class="result-image-section">
                    <h4>{{ $t('messages.recognizeImage') }}</h4>
                    <img :src="currentResult.imageUrl" alt="{{ $t('messages.recognizeImage') }}" class="result-image" />
                  </div>

                  <!-- 结果显示 -->
                  <div class="result-latex-section">
                    <h4>{{ $t('messages.recognitionNoResult') }}</h4>
                    <el-input v-model="currentResult.latex" type="textarea" :rows="6" readonly class="latex-input" />
                    <div class="result-actions">
                      <el-button type="primary" size="small" @click="copyToClipboard(currentResult.latex)">
                        <el-icon>
                          <CopyDocument />
                        </el-icon>
                        {{ $t('buttons.copyResult') }}
                      </el-button>
                      <el-button type="primary" size="small" @click="reRecognize" :disabled="!hasCurrentImage">
                        {{ $t('buttons.reRecognize') }}
                      </el-button>
                      <el-button type="success" size="small" @click="submitFeedback(currentResult, 'Perfect')">
                        👍 {{ $t('buttons.perfect') }}
                      </el-button>
                      <el-button type="warning" size="small" @click="submitFeedback(currentResult, 'Mistake')">
                        😕 {{ $t('buttons.mistake') }}
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
            <span>{{ $t('footer.poweredBy') }} </span>
            <a href="https://github.com/RQLuo/MixTeX-Latex-OCR" target="_blank" class="footer-link">
              <el-icon><Link /></el-icon>
            </a>
          </div>
          <div class="footer-right">
            <el-button type="text" size="small" > 
            <a href="https://github.com/e-zz/MixTex-OCR-WebRebuild" target="_blank" >
              {{ $t('footer.projectLink') }}
            </a>
            </el-button>
            <el-button type="text" size="small" @click="showAbout">
              {{ $t('footer.about') }} 
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
import { useI18n } from 'vue-i18n'
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
      t('download.confirmMessage'),
      t('download.title'),
      {
        confirmButtonText: t('download.confirmButton'),
        cancelButtonText: t('download.cancelButton'),
        type: 'info'
      }
    )

    isDownloading.value = true
    showGlobalLoading(t('download.downloading'))

    // Call backend endpoint to handle download, unzip and setup
    const response = await fetch('http://localhost:8000/download_model', {
      method: 'POST'
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || t('download.downloadFailed'))
    }

    const result = await response.json()
    hideGlobalLoading()
    isDownloading.value = false

    ElMessage.success(t('download.downloadSuccess'))
  } catch (error) {
    hideGlobalLoading()
    isDownloading.value = false

    // Don't show error if user cancelled
    if (error.toString().includes('cancel')) return

    ElMessage.error(`${t('download.downloadError')}: ${error.message || error}`)
  }
}

// Add i18n
const { t, locale } = useI18n()
const currentLanguage = ref(locale.value)

const languageSwitch = ref(currentLanguage.value === 'zh')

// Language change handler
const changeLanguage = (lang) => {
  locale.value = lang
  currentLanguage.value = lang
  localStorage.setItem('language', lang)
  ElMessage.success(t('messages.languageChanged'))
}

// Handle switch change
const onLanguageSwitchChange = (value) => {
  const lang = value ? 'zh' : 'en'
  changeLanguage(lang)
}


// // Add missing setLanguage function for backwards compatibility
// const setLanguage = (lang) => {
//   if (currentLanguage.value !== lang) {
//     changeLanguage(lang)
//     languageSwitch.value = lang === 'zh'
//   }
// }

// 方法
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success(t('messages.copiedToClipboard'))
  } catch (error) {
    // 降级方案
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    ElMessage.success(t('messages.copiedToClipboard'))
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
      ElMessage.success(t('messages.feedbackSubmitted'))
    } else {
      ElMessage.error(t('messages.feedbackFailed'))
    }
  } catch (error) {
    ElMessage.error(t('messages.feedbackFailed'))
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
const showGlobalLoading = (message = null) => {
  if (globalLoadingRef.value) {
    globalLoadingRef.value.show(message || t('messages.recognizing'))
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
  margin-bottom: 20px;
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
/* Language switch styles */
.lang-toggle-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 120px; /* Fixed minimum width */
}

.lang-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  min-width: 40px; /* Fixed width to prevent stretching */
  text-align: left;
  white-space: nowrap; /* Prevent text wrapping */
}

.lang-switch {
  --el-switch-on-color: #409eff;
  --el-switch-off-color: #dcdfe6;
  width: 60px !important; /* Fixed width for the switch */
  flex-shrink: 0; /* Prevent shrinking */
}

/* Ensure the switch button text doesn't cause stretching */
.lang-switch .el-switch__core {
  min-width: 60px;
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

.el-select .el-input {
  width: 80px;
}

.el-select .el-input__inner {
  text-align: center;
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

.footer-left {
  display: flex;
  align-items: center;
}

/* Override webkit default link styles with higher specificity */
a.footer-link,
a.footer-link:link,
a.footer-link:visited,
a.footer-link:hover,
a.footer-link:active,
a.footer-link:-webkit-any-link {
  color: #409eff !important;
  text-decoration: none !important;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
  transition: color 0.3s;
}

a.footer-link:hover {
  color: #66b1ff !important;
}

.footer-right a,
.footer-right a:link,
.footer-right a:visited,
.footer-right a:hover,
.footer-right a:active,
.footer-right a:-webkit-any-link {
  color: inherit !important;
  text-decoration: none !important;
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