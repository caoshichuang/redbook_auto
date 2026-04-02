<template>
  <div>
    <div class="page-header d-print-none">
      <div class="row align-items-center">
        <div class="col">
          <h2 class="page-title">{{ t('distribution.title') }}</h2>
          <p class="text-muted mt-1">{{ t('distribution.description') }}</p>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message.text" class="alert mb-3" :class="message.type === 'success' ? 'alert-success' : 'alert-danger'">
      {{ message.text }}
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table table-vcenter card-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Market</th>
              <th>Type</th>
              <th>Title</th>
              <th>Created</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="contents.length === 0">
              <td colspan="7" class="text-center text-muted py-4">暂无内容</td>
            </tr>
            <tr v-for="item in contents" :key="item.id">
              <td class="text-muted">{{ item.id }}</td>
              <td>
                <span class="badge bg-blue-lt">{{ item.market }}</span>
              </td>
              <td class="text-muted">{{ item.content_type }}</td>
              <td>
                <div class="text-truncate" style="max-width: 250px;" :title="item.title">{{ item.title }}</div>
              </td>
              <td class="text-muted"><small>{{ item.created_at }}</small></td>
              <td>
                <span class="badge" :class="getStatusBadge(item.status)">{{ item.status }}</span>
              </td>
              <td>
                <div class="btn-list flex-nowrap">
                  <button class="btn btn-sm btn-ghost-pink" @click="distributeToXiaohongshu(item)">
                    {{ t('distribution.xiaohongshu') }}
                  </button>
                  <button class="btn btn-sm btn-ghost-success" @click="distributeToWechat(item)">
                    {{ t('distribution.wechat') }}
                  </button>
                  <button class="btn btn-sm btn-ghost-warning" @click="distributeToToutiao(item)">
                    {{ t('distribution.toutiao') }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 小红书 Modal -->
    <div class="modal modal-blur fade" :class="{ show: xiaohongshuDialogVisible }" :style="{ display: xiaohongshuDialogVisible ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Xiaohongshu Distribution</h5>
            <button type="button" class="btn-close" @click="xiaohongshuDialogVisible = false"></button>
          </div>
          <div class="modal-body" v-if="xiaohongshuData">
            <div class="mb-3">
              <label class="form-label fw-bold">Title (max 20 chars)</label>
              <input type="text" class="form-control" :value="xiaohongshuData.formatted_content?.title" readonly />
            </div>
            <div class="mb-3">
              <label class="form-label fw-bold">Content</label>
              <textarea class="form-control" :value="xiaohongshuData.formatted_content?.full_content" rows="6" readonly></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label fw-bold">{{ t('distribution.instructions') }}</label>
              <textarea class="form-control" :value="xiaohongshuData.instructions" rows="10" readonly></textarea>
            </div>
            <div v-if="xiaohongshuData.warnings?.length > 0" class="mb-3">
              <label class="form-label fw-bold">{{ t('distribution.warnings') }}</label>
              <div v-for="(warning, index) in xiaohongshuData.warnings" :key="index" class="alert alert-warning py-2 mb-1">
                {{ warning }}
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary me-auto" @click="copyXiaohongshuContent">
              {{ t('distribution.copyContent') }}
            </button>
            <button type="button" class="btn btn-secondary" @click="xiaohongshuDialogVisible = false">Close</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="xiaohongshuDialogVisible" class="modal-backdrop fade show"></div>

    <!-- WeChat Modal -->
    <div class="modal modal-blur fade" :class="{ show: wechatDialogVisible }" :style="{ display: wechatDialogVisible ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">WeChat Distribution</h5>
            <button type="button" class="btn-close" @click="wechatDialogVisible = false"></button>
          </div>
          <div class="modal-body" v-if="wechatData">
            <div class="alert" :class="wechatData.success ? 'alert-success' : 'alert-danger'">
              {{ wechatData.message }}
            </div>
            <div v-if="wechatData.success && wechatData.data">
              <div class="mb-2">Status: <span class="badge bg-blue-lt">{{ wechatData.data.status }}</span></div>
              <div v-if="wechatData.data.status === 'draft'" class="text-muted small">
                Draft has been created. Please log in to publish manually.
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="wechatDialogVisible = false">Close</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="wechatDialogVisible" class="modal-backdrop fade show"></div>

    <!-- Toutiao Modal -->
    <div class="modal modal-blur fade" :class="{ show: toutiaoDialogVisible }" :style="{ display: toutiaoDialogVisible ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Toutiao Distribution</h5>
            <button type="button" class="btn-close" @click="toutiaoDialogVisible = false"></button>
          </div>
          <div class="modal-body" v-if="toutiaoData">
            <div class="alert" :class="toutiaoData.success ? 'alert-success' : 'alert-danger'">
              {{ toutiaoData.message }}
            </div>
            <div v-if="toutiaoData.success && toutiaoData.data">
              <div class="mb-2">Status: <span class="badge bg-blue-lt">{{ toutiaoData.data.status }}</span></div>
              <div v-if="toutiaoData.data.status === 'draft'" class="text-muted small">
                Article has been created. Please log in to publish manually.
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="toutiaoDialogVisible = false">Close</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="toutiaoDialogVisible" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../utils/api'

const { t } = useI18n()
const contents = ref([])
const xiaohongshuDialogVisible = ref(false)
const wechatDialogVisible = ref(false)
const toutiaoDialogVisible = ref(false)
const xiaohongshuData = ref(null)
const wechatData = ref(null)
const toutiaoData = ref(null)
const message = reactive({ text: '', type: 'success' })

const showMsg = (text, type = 'success') => {
  message.text = text
  message.type = type
  setTimeout(() => { message.text = '' }, 3000)
}

const getStatusBadge = (status) => {
  const map = {
    generated: 'bg-blue-lt',
    sent: 'bg-success-lt text-success',
    published: 'bg-success-lt text-success',
    failed: 'bg-danger-lt text-danger'
  }
  return map[status] || 'bg-secondary-lt'
}

const fetchContents = async () => {
  try {
    contents.value = await api.get('/content/')
  } catch (error) {
    showMsg('Failed to load contents', 'error')
  }
}

const distributeToXiaohongshu = async (content) => {
  try {
    const data = await api.post(`/distribution/xiaohongshu/${content.id}`)
    xiaohongshuData.value = data.data
    xiaohongshuDialogVisible.value = true
  } catch (error) {
    showMsg('Failed to distribute to Xiaohongshu', 'error')
  }
}

const distributeToWechat = async (content) => {
  try {
    wechatData.value = await api.post(`/distribution/wechat/${content.id}`)
    wechatDialogVisible.value = true
  } catch (error) {
    showMsg('Failed to distribute to WeChat', 'error')
  }
}

const distributeToToutiao = async (content) => {
  try {
    const response = await api.post(`/distribution/toutiao/${content.id}`)
    toutiaoData.value = response.data
    toutiaoDialogVisible.value = true
  } catch (error) {
    showMsg('Failed to distribute to Toutiao', 'error')
  }
}

const copyXiaohongshuContent = async () => {
  try {
    await navigator.clipboard.writeText(xiaohongshuData.value.formatted_content.full_content)
    showMsg('Content copied to clipboard!')
  } catch (error) {
    showMsg('Failed to copy content', 'error')
  }
}

onMounted(fetchContents)
</script>
