<template>
  <div class="clipboard-upload-container">
    <!-- 剪贴板区域 -->
    <div 
      class="clipboard-area"
      @paste="handlePaste"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
      :class="{ 'dragover': isDragOver }"
    >
      <div class="clipboard-content">
        <el-icon class="clipboard-icon"><DocumentCopy /></el-icon>
        <div class="clipboard-text">
          <h3>{{ $t('clipboard.title') }}</h3>
          <p>{{ $t('clipboard.pasteHint') }}</p>
          <p>{{ $t('clipboard.dragHint') }}</p>
        </div>
      </div>
    </div>

    <!-- 格式设置 -->
    <div class="format-settings">
      <el-divider>{{ $t('clipboard.formatSettings') }}</el-divider>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-checkbox v-model="useDollars">{{ $t('clipboard.useDollars') }}</el-checkbox>
        </el-col>
        <el-col :span="12">
          <el-checkbox v-model="convertAlign">{{ $t('clipboard.convertAlign') }}</el-checkbox>
        </el-col>
        <el-col :span="12">
          <el-checkbox v-model="useTypst">{{ $t('clipboard.useTypst') }}</el-checkbox>
        </el-col>
      </el-row>
    </div>

    <!-- 隐藏的加载指示器 -->
    <div v-if="isProcessing" style="display: none;">
      <el-progress 
        :percentage="loadingProgress" 
        :stroke-width="8"
        color="#409eff"
        :show-text="false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentCopy } from '@element-plus/icons-vue'
import axios from 'axios'

// 响应式数据
const imageUrl = ref('')
const isProcessing = ref(false)
const isDragOver = ref(false)
const loadingProgress = ref(0)
const useDollars = ref(false)
const useTypst = ref(true)
const convertAlign = ref(false)
const currentFile = ref(null)

// API配置
const API_BASE = 'http://localhost:8000'

// 获取父组件的方法
const addResult = inject('addResult', null)
const showGlobalLoading = inject('showGlobalLoading', null)
const hideGlobalLoading = inject('hideGlobalLoading', null)

// 处理粘贴事件
const handlePaste = async (event) => {
  event.preventDefault()
  const items = event.clipboardData.items
  
  for (let item of items) {
    if (item.type.indexOf('image') !== -1) {
      const file = item.getAsFile()
      if (file) {
        await processImage(file)
      }
    }
  }
}

// 处理拖拽事件
const handleDragOver = (event) => {
  event.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (event) => {
  event.preventDefault()
  isDragOver.value = false
}

const handleDrop = async (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  const files = event.dataTransfer.files
  if (files.length > 0) {
    await processImage(files[0])
  }
}

const { t } = useI18n()

// 处理图片
const processImage = async (file) => {
  try {
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      ElMessage.error(t('messages.invalidImageFile'))
      return
    }

    // 保存文件引用
    currentFile.value = file

    // 显示预览
    const reader = new FileReader()
    reader.onload = (e) => {
      imageUrl.value = e.target.result
    }
    reader.readAsDataURL(file)

    // 自动开始识别
    await recognizeImage(file)
    
  } catch (error) {
    ElMessage.error(t('messages.processingError') + error.message)
  }
}

// 文件转base64
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = error => reject(error)
  })
}

// 识别图片
const recognizeImage = async (file) => {
  if (!file) {
    ElMessage.error(t('messages.pleaseSelectImage'))
    return
  }

  isProcessing.value = true
  loadingProgress.value = 0
  
  // 显示全局加载状态
  if (showGlobalLoading) {
    showGlobalLoading(t('messages.recognizing'))
  }

  try {
    // 模拟进度
    const progressInterval = setInterval(() => {
      if (loadingProgress.value < 90) {
        loadingProgress.value += 10
      }
    }, 200)

    // 转换为base64
    const base64Data = await fileToBase64(file)
    
    // 发送到API
    const formData = new FormData()
    formData.append('image_data', base64Data)
    formData.append('use_dollars', useDollars.value)
    formData.append('convert_align', convertAlign.value)
    formData.append('use_typst', useTypst.value)

    const response = await axios.post(`${API_BASE}/predict_clipboard`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    clearInterval(progressInterval)
    loadingProgress.value = 100

    if (response.data.success) {
      const result = response.data.latex
      ElMessage.success('识别成功')
      
      // 添加到父组件的结果列表
      if (addResult) {
        addResult(imageUrl.value, result)
      }
    } else {
      ElMessage.error(response.data.message || '识别失败')
    }
    
  } catch (error) {
    ElMessage.error('请求失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    isProcessing.value = false
    loadingProgress.value = 0
    
    // 隐藏全局加载状态
    if (hideGlobalLoading) {
      hideGlobalLoading()
    }
  }
}

// 重新识别
const reRecognize = async () => {
  if (currentFile.value) {
    await recognizeImage(currentFile.value)
  } else {
    ElMessage.warning(t('messages.noImageToReRecognize'))
  }
}

// 清除图片函数已删除

// 全局粘贴监听
const handleGlobalPaste = async (event) => {
  // 检查是否在剪贴板区域内
  const clipboardArea = document.querySelector('.clipboard-area')
  if (clipboardArea && clipboardArea.contains(event.target)) {
    return // 让局部处理函数处理
  }
  
  // 全局粘贴处理
  const items = event.clipboardData.items
  for (let item of items) {
    if (item.type.indexOf('image') !== -1) {
      const file = item.getAsFile()
      if (file) {
        await processImage(file)
      }
    }
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('paste', handleGlobalPaste)
})

onUnmounted(() => {
  document.removeEventListener('paste', handleGlobalPaste)
})

// 暴露重新识别方法给父组件
defineExpose({
  reRecognize
})
</script>

<style scoped>
.clipboard-upload-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.format-settings {
  margin-top: 15px;
  margin-bottom: 5px;
}

.clipboard-area {
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  background-color: #fafafa;
  transition: all 0.3s ease;
  cursor: pointer;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clipboard-area:hover {
  border-color: #409eff;
  background-color: #f0f8ff;
}

.clipboard-area.dragover {
  border-color: #409eff;
  background-color: #e3f2fd;
  transform: scale(1.02);
}

.clipboard-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  max-width: 400px;
}

.clipboard-icon {
  font-size: 36px;
  color: #409eff;
}

.clipboard-text h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 18px;
}

.clipboard-text p {
  margin: 3px 0;
  color: #666;
  font-size: 13px;
}

/* 图片预览和加载状态相关样式已删除 */

/* 响应式设计 */
@media (max-width: 768px) {
  .clipboard-area {
    padding: 20px;
  }
  
  .clipboard-text h3 {
    font-size: 16px;
  }
  
  .clipboard-text p {
    font-size: 12px;
  }
}
</style>