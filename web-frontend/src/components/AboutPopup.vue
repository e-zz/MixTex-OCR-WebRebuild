<template>
  <transition name="fade">
    <div v-if="visible" class="about-popup-overlay" @click.self="close">
      <div class="about-popup-container">
        <div class="about-popup-header">
          <div class="header-content">
            <div class="app-icon">
              <el-icon size="32">
                <Document />
              </el-icon>
            </div>
            <div class="header-text">
              <h2>{{ $t('about.title') }}</h2>
              <p class="subtitle">{{ $t('about.webVersion') }}</p>
            </div>
          </div>
          <button class="close-button" @click="close">
            <el-icon>
              <Close />
            </el-icon>
          </button>
        </div>

        <div class="about-popup-content">
          <div class="section">
            <h3>{{ $t('about.techStack') }}</h3>
            <div class="tech-stack">
              <div class="tech-item">
                <el-icon class="tech-icon frontend">
                  <View />
                </el-icon>
                <div class="tech-details">
                  <strong>{{ $t('about.frontend') }}</strong>
                  <span>Vue 3 + Element Plus</span>
                </div>
              </div>

              <div class="tech-item">
                <el-icon class="tech-icon backend">
                  <Service />
                </el-icon>
                <div class="tech-details">
                  <strong>{{ $t('about.backend') }}</strong>
                  <span>FastAPI</span>
                </div>
              </div>

              <div class="tech-item">
                <el-icon class="tech-icon model">
                  <Cpu />
                </el-icon>
                <div class="tech-details">
                  <strong>{{ $t('about.model') }}</strong>
                  <span>
                    MixTeX {{ $t('about.modelText') }}
                    <a href="https://github.com/RQLuo/MixTeX-Latex-OCR" target="_blank" class="external-link">
                      <el-icon>
                        <Link />
                      </el-icon>
                    </a>
                  </span>
                </div>
              </div>

              <div class="tech-item">
                <el-icon class="tech-icon typst">
                  <EditPen />
                </el-icon>
                <div class="tech-details">
                  <strong>{{ $t('about.typst') }}</strong>
                  <span>
                    <a href="https://pandoc.org/" target="_blank" class="external-link">
                      Pandoc <el-icon>
                        <Link />
                      </el-icon>
                    </a>
                    {{ $t('about.and') }}
                    <a href="https://github.com/JessicaTegner/pypandoc" target="_blank" class="external-link">
                      pypandoc <el-icon>
                        <Link />
                      </el-icon>
                    </a>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="section">
            <h3>{{ $t('about.credits') }}</h3>
            <div class="credits">
              <div class="credit-item">
                <el-icon class="credit-icon">
                  <User />
                </el-icon>
                <div class="credit-text">
                  <strong>{{ $t('about.rebuilders') }}</strong>
                  <span>Hipeace, e-zz</span>
                </div>
              </div>

              <div class="credit-item">
                <el-icon class="credit-icon">
                  <Star />
                </el-icon>
                <div class="credit-text">
                  <strong>{{ $t('about.originalAuthor') }}</strong>
                  <span>
                    <a href="https://github.com/RQLuo/MixTeX-Latex-OCR" target="_blank" class="external-link">
                      RQLuo <el-icon>
                        <Link />
                      </el-icon>
                    </a>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="footer">
            <!-- <p class="footer-text">{{ $t('about.thanksMessage') }}</p> -->
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Document,
  Close,
  View,
  Service,
  Cpu,
  EditPen,
  Link,
  User,
  Star
} from '@element-plus/icons-vue'

// Add i18n
const { t } = useI18n()

// 响应式状态
const visible = ref(false)

// 显示弹窗
const show = () => {
  visible.value = true
}

// 关闭弹窗
const close = () => {
  visible.value = false
}

// 暴露方法给外部使用
defineExpose({
  show,
  close
})
</script>

<style scoped>
.about-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.about-popup-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  width: 600px;
  max-width: 90%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.about-popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  background: #409eff;
  color: white;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-text h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.close-button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 6px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.about-popup-content {
  padding: 24px 32px;
  overflow-y: auto;
}

.section {
  margin-bottom: 24px;
}

.section:last-child {
  margin-bottom: 0;
}

.section h3 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  border-left: 3px solid #409eff;
  padding-left: 8px;
}

.tech-stack,
.credits {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tech-item,
.credit-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.tech-icon,
.credit-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  flex-shrink: 0;
}

.tech-icon.frontend {
  background: #4CAF50;
}

.tech-icon.backend {
  background: #FF9800;
}

.tech-icon.model {
  background: #9C27B0;
}

.tech-icon.typst {
  background: #F44336;
}

.credit-icon {
  background: #409eff;
}

.tech-details,
.credit-text {
  flex: 1;
  min-width: 0;
}

.tech-details strong,
.credit-text strong {
  color: #303133;
  font-size: 14px;
  font-weight: 600;
  display: block;
  margin-bottom: 2px;
}

.tech-details span,
.credit-text span {
  color: #606266;
  font-size: 13px;
  line-height: 1.4;
}

.external-link {
  color: #409eff;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.external-link:hover {
  color: #66b1ff;
}

.external-link .el-icon {
  font-size: 12px;
}

.footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  text-align: center;
}

.footer-text {
  margin: 0;
  color: #909399;
  font-size: 13px;
  font-style: italic;
}

/* Simplified transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .about-popup-container {
    width: 95%;
    margin: 20px;
  }

  .about-popup-header,
  .about-popup-content {
    padding: 16px 20px;
  }

  .tech-icon,
  .credit-icon {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }
}
</style>