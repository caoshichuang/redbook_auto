<template>
  <div>
    <div class="page-header d-print-none">
      <div class="row align-items-center">
        <div class="col">
          <h2 class="page-title">{{ t('content.title') }}</h2>
        </div>
        <div class="col-auto ms-auto d-flex gap-2">
          <select class="form-select" v-model="filter.market" style="width: 140px;" @change="loadContent">
            <option value="">{{ t('content.allMarkets') }}</option>
            <option value="美股">美股</option>
            <option value="A股">A股</option>
            <option value="港股">港股</option>
          </select>
          <button class="btn btn-secondary" @click="loadContent">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon me-1" width="24" height="24" viewBox="0 0 24 24"
              stroke-width="2" stroke="currentColor" fill="none">
              <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
              <polyline points="1 4 1 10 7 10" />
              <path d="M3.51 15a9 9 0 1 0 .49-3.35" />
            </svg>
            {{ t('common.refresh') }}
          </button>
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
              <th>{{ t('content.market') }}</th>
              <th>{{ t('content.type') }}</th>
              <th>{{ t('content.contentTitle') }}</th>
              <th>{{ t('common.createdAt') }}</th>
              <th>{{ t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="text-center py-4">
                <div class="spinner-border spinner-border-sm text-primary"></div>
              </td>
            </tr>
            <tr v-else-if="contents.length === 0">
              <td colspan="6" class="text-center text-muted py-4">暂无内容</td>
            </tr>
            <tr v-for="item in contents" :key="item.id">
              <td class="text-muted">{{ item.id }}</td>
              <td>
                <span class="badge bg-blue-lt">{{ item.market }}</span>
              </td>
              <td class="text-muted">{{ item.content_type }}</td>
              <td>
                <div class="text-truncate" style="max-width: 300px;" :title="item.title">{{ item.title }}</div>
              </td>
              <td class="text-muted">
                <small>{{ item.created_at }}</small>
              </td>
              <td>
                <div class="btn-list flex-nowrap">
                  <button class="btn btn-sm btn-ghost-secondary" @click="showDetail(item)">
                    {{ t('content.viewDetail') }}
                  </button>
                  <button class="btn btn-sm btn-ghost-danger" @click="handleDelete(item)">
                    {{ t('common.delete') }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 内容详情 Modal -->
    <div class="modal modal-blur fade" :class="{ show: detailDialogVisible }" :style="{ display: detailDialogVisible ? 'block' : 'none' }" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ t('content.detail') }}</h5>
            <button type="button" class="btn-close" @click="detailDialogVisible = false"></button>
          </div>
          <div class="modal-body" v-if="currentContent">
            <div class="row g-3 mb-3">
              <div class="col-sm-6">
                <div class="datagrid-item">
                  <div class="datagrid-title">ID</div>
                  <div class="datagrid-content">{{ currentContent.id }}</div>
                </div>
              </div>
              <div class="col-sm-6">
                <div class="datagrid-item">
                  <div class="datagrid-title">{{ t('content.market') }}</div>
                  <div class="datagrid-content">{{ currentContent.market }}</div>
                </div>
              </div>
              <div class="col-sm-6">
                <div class="datagrid-item">
                  <div class="datagrid-title">{{ t('content.type') }}</div>
                  <div class="datagrid-content">{{ currentContent.content_type }}</div>
                </div>
              </div>
              <div class="col-sm-6">
                <div class="datagrid-item">
                  <div class="datagrid-title">{{ t('common.createdAt') }}</div>
                  <div class="datagrid-content">{{ currentContent.created_at }}</div>
                </div>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label fw-bold">{{ t('content.contentTitle') }}</label>
              <div class="form-control bg-light">{{ currentContent.title }}</div>
            </div>

            <div class="mb-3">
              <label class="form-label fw-bold">{{ t('content.contentText') }}</label>
              <textarea class="form-control" :value="currentContent.content" rows="12" readonly style="font-family: monospace; font-size: 0.85rem;"></textarea>
            </div>

            <div v-if="currentContent.tags" class="mb-3">
              <label class="form-label fw-bold">{{ t('content.tags') }}</label>
              <div class="form-control bg-light">{{ currentContent.tags }}</div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary me-auto" @click="copyContent">
              {{ t('content.copyContent') }}
            </button>
            <button type="button" class="btn btn-secondary" @click="detailDialogVisible = false">{{ t('common.close') }}</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="detailDialogVisible" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { contentApi } from '../utils/api'

const { t } = useI18n()
const contents = ref([])
const loading = ref(false)
const detailDialogVisible = ref(false)
const currentContent = ref(null)
const filter = reactive({ market: '' })
const message = reactive({ text: '', type: 'success' })

const showMsg = (text, type = 'success') => {
  message.text = text
  message.type = type
  setTimeout(() => { message.text = '' }, 3000)
}

const loadContent = async () => {
  loading.value = true
  try {
    const params = {}
    if (filter.market) params.market = filter.market
    contents.value = await contentApi.list(params)
  } catch (error) {
    showMsg('加载失败', 'error')
  } finally {
    loading.value = false
  }
}

const showDetail = (row) => {
  currentContent.value = { ...row }
  detailDialogVisible.value = true
}

const handleDelete = async (row) => {
  if (!confirm('确定删除此内容？')) return
  try {
    await contentApi.delete(row.id)
    showMsg(t('common.success'))
    loadContent()
  } catch (error) {
    showMsg(error.response?.data?.detail || t('common.error'), 'error')
  }
}

const copyContent = () => {
  navigator.clipboard.writeText(currentContent.value.content)
  showMsg(t('content.copied'))
}

onMounted(loadContent)
</script>
