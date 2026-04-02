<template>
  <div class="preview-container">
    <div class="header">
      <div class="logo">⛵ FinanceSail</div>
    </div>

    <!-- Toast 提示 -->
    <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.message }}</div>

    <div class="content-wrapper">
      <div class="title-section">
        <h1 class="title">{{ content.title }}</h1>
        <div class="meta">
          <span class="market">{{ content.market }}</span>
          <span class="date">{{ content.created_at }}</span>
        </div>
      </div>

      <div class="images-section" v-if="content.image_urls && content.image_urls.length > 0">
        <h2>📊 Images</h2>
        <div class="images-grid">
          <div
            v-for="(url, index) in content.image_urls"
            :key="index"
            class="image-item"
            @click="viewImage(index)"
          >
            <img :src="url" :alt="`Image ${index + 1}`" />
            <div class="image-overlay">
              <button
                class="btn-download"
                @click.stop="downloadImage(url, index)"
                title="下载图片"
              >⬇</button>
            </div>
          </div>
        </div>
      </div>

      <div class="content-section">
        <h2>📝 Content</h2>
        <div class="content-box">
          <pre>{{ content.content }}</pre>
        </div>
      </div>

      <div class="tags-section" v-if="content.tags">
        <h2>🏷️ Tags</h2>
        <div class="tags">
          <span v-for="tag in parseTags(content.tags)" :key="tag" class="tag">
            {{ tag }}
          </span>
        </div>
      </div>

      <div class="actions">
        <button class="btn btn-primary" @click="copyTitle">📄 Copy Title</button>
        <button class="btn btn-success" @click="copyContent">📋 Copy Content</button>
        <button class="btn btn-warning" @click="copyTags">🏷️ Copy Tags</button>
        <button class="btn btn-info" @click="copyAll">📑 Copy All</button>
      </div>
    </div>

    <!-- 图片预览弹窗 -->
    <div v-if="showViewer" class="viewer-overlay" @click="showViewer = false">
      <div class="viewer-content" @click.stop>
        <button class="viewer-close" @click="showViewer = false">✕</button>
        <button class="viewer-prev" @click="prevImage" v-if="content.image_urls && content.image_urls.length > 1">‹</button>
        <img :src="content.image_urls && content.image_urls[viewerIndex]" class="viewer-img" />
        <button class="viewer-next" @click="nextImage" v-if="content.image_urls && content.image_urls.length > 1">›</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const content = ref({
  id: 0,
  market: '',
  content_type: '',
  title: '',
  content: '',
  tags: '',
  image_urls: [],
  created_at: ''
})
const showViewer = ref(false)
const viewerIndex = ref(0)
const toast = ref({ show: false, message: '', type: 'success' })

// 显示 toast 提示
const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 2500)
}

const parseTags = (tags) => {
  if (!tags) return []
  return tags.split(' ').filter(tag => tag.trim())
}

const viewImage = (index) => {
  viewerIndex.value = index
  showViewer.value = true
}

const prevImage = () => {
  if (viewerIndex.value > 0) viewerIndex.value--
}

const nextImage = () => {
  if (content.value.image_urls && viewerIndex.value < content.value.image_urls.length - 1) {
    viewerIndex.value++
  }
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    showToast('Copied to clipboard!')
  } catch {
    showToast('Failed to copy', 'error')
  }
}

const copyTitle = () => copyToClipboard(content.value.title)
const copyContent = () => copyToClipboard(content.value.content)
const copyTags = () => copyToClipboard(content.value.tags)

const copyAll = () => {
  const all = `${content.value.title}\n\n${content.value.content}\n\n${content.value.tags}`
  copyToClipboard(all)
}

const downloadImage = (url, index) => {
  const link = document.createElement('a')
  link.href = url
  link.download = `image_${index + 1}.png`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showToast('Download started!')
}

const fetchContent = async () => {
  try {
    const response = await axios.get(`/api/preview/${route.params.id}`)
    content.value = response.data
  } catch (error) {
    console.error('Failed to fetch content:', error)
    showToast('Failed to load content', 'error')
  }
}

onMounted(() => {
  fetchContent()
})
</script>

<style scoped>
.preview-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  position: relative;
}

/* Toast 提示 */
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 24px;
  border-radius: 6px;
  font-size: 14px;
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.toast.success { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
.toast.error   { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }

.header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: #0d6efd;
}

.content-wrapper {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.title-section {
  margin-bottom: 24px;
  text-align: center;
}

.title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.meta {
  display: flex;
  justify-content: center;
  gap: 12px;
  color: #909399;
  font-size: 14px;
}

.market {
  background: #0d6efd;
  color: #fff;
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: 500;
}

.images-section,
.content-section,
.tags-section {
  margin-bottom: 24px;
}

h2 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.image-item {
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
  position: relative;
}

.image-item:hover {
  transform: scale(1.02);
}

.image-overlay {
  position: absolute;
  bottom: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-item:hover .image-overlay {
  opacity: 1;
}

.btn-download {
  background: rgba(0,0,0,0.6);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-download:hover { background: rgba(0,0,0,0.8); }

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.content-box {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
}

.content-box pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'SF Mono', Monaco, 'Inconsolata', 'Roboto Mono', 'Source Code Pro', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: #dbeafe;
  color: #1d4ed8;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
}

/* 操作按钮 */
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: opacity 0.15s;
}
.btn:hover { opacity: 0.85; }
.btn-primary { background: #0d6efd; color: #fff; }
.btn-success { background: #198754; color: #fff; }
.btn-warning { background: #ffc107; color: #212529; }
.btn-info    { background: #0dcaf0; color: #212529; }

/* 图片预览弹窗 */
.viewer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  z-index: 9998;
  display: flex;
  align-items: center;
  justify-content: center;
}

.viewer-content {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  max-width: 90vw;
  max-height: 90vh;
}

.viewer-img {
  max-width: 80vw;
  max-height: 85vh;
  border-radius: 8px;
  object-fit: contain;
}

.viewer-close {
  position: absolute;
  top: -40px;
  right: 0;
  background: rgba(255,255,255,0.2);
  border: none;
  color: #fff;
  font-size: 20px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
}

.viewer-prev,
.viewer-next {
  background: rgba(255,255,255,0.2);
  border: none;
  color: #fff;
  font-size: 32px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.viewer-prev:hover,
.viewer-next:hover { background: rgba(255,255,255,0.35); }

/* 手机端适配 */
@media (max-width: 768px) {
  .preview-container {
    padding: 12px;
  }

  .content-wrapper {
    padding: 16px;
    border-radius: 8px;
  }

  .title {
    font-size: 22px;
  }

  .meta {
    flex-direction: column;
    gap: 8px;
  }

  .images-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .actions {
    flex-direction: column;
  }

  .actions .btn {
    width: 100%;
  }
}
</style>
