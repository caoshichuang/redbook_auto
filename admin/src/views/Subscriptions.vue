<template>
  <div>
    <div class="page-header d-print-none">
      <div class="row align-items-center">
        <div class="col">
          <h2 class="page-title">{{ t('subscriptions.title') }}</h2>
        </div>
        <div class="col-auto ms-auto">
          <button class="btn btn-primary" @click="showAddDialog">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon me-1" width="24" height="24" viewBox="0 0 24 24"
              stroke-width="2" stroke="currentColor" fill="none">
              <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            {{ t('subscriptions.addSubscription') }}
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
              <th>{{ t('subscriptions.stockCode') }}</th>
              <th>{{ t('subscriptions.stockName') }}</th>
              <th>{{ t('subscriptions.market') }}</th>
              <th>{{ t('subscriptions.rules') }}</th>
              <th>{{ t('common.status') }}</th>
              <th>{{ t('common.createdAt') }}</th>
              <th>{{ t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="subscriptions.length === 0">
              <td colspan="8" class="text-center text-muted py-4">暂无订阅</td>
            </tr>
            <tr v-for="sub in subscriptions" :key="sub.id">
              <td class="text-muted">{{ sub.id }}</td>
              <td><code>{{ sub.stock_code }}</code></td>
              <td>{{ sub.stock_name }}</td>
              <td>
                <span class="badge bg-blue-lt">{{ sub.market }}</span>
              </td>
              <td>
                <div class="d-flex flex-wrap gap-1">
                  <span
                    v-for="rule in parseRules(sub.rules)"
                    :key="rule.type"
                    class="badge bg-secondary-lt"
                  >
                    {{ rule.type }}: {{ rule.threshold }}
                  </span>
                </div>
              </td>
              <td>
                <span class="badge" :class="sub.is_active ? 'bg-success-lt text-success' : 'bg-secondary-lt'">
                  {{ sub.is_active ? t('subscriptions.active') : t('subscriptions.inactive') }}
                </span>
              </td>
              <td class="text-muted"><small>{{ sub.created_at }}</small></td>
              <td>
                <div class="btn-list flex-nowrap">
                  <button class="btn btn-sm btn-ghost-secondary" @click="editSubscription(sub)">{{ t('common.edit') }}</button>
                  <button class="btn btn-sm btn-ghost-danger" @click="deleteSubscription(sub)">{{ t('common.delete') }}</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 添加/编辑 Modal -->
    <div class="modal modal-blur fade" :class="{ show: dialogVisible }" :style="{ display: dialogVisible ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? t('subscriptions.editSubscription') : t('subscriptions.addSubscription') }}</h5>
            <button type="button" class="btn-close" @click="dialogVisible = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">{{ t('subscriptions.stockCode') }}</label>
              <input type="text" class="form-control" v-model="form.stock_code" placeholder="e.g., 600519" />
            </div>
            <div class="mb-3">
              <label class="form-label">{{ t('subscriptions.stockName') }}</label>
              <input type="text" class="form-control" v-model="form.stock_name" placeholder="e.g., 贵州茅台" />
            </div>
            <div class="mb-3">
              <label class="form-label">{{ t('subscriptions.market') }}</label>
              <select class="form-select" v-model="form.market">
                <option value="A股">A股</option>
                <option value="港股">港股</option>
                <option value="美股">美股</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">{{ t('subscriptions.alertRules') }}</label>
              <div v-for="(rule, index) in form.rules" :key="index" class="d-flex gap-2 mb-2">
                <select class="form-select" v-model="rule.type" style="flex: 1;">
                  <option value="change">Price Change %</option>
                  <option value="announce">Announcement</option>
                  <option value="earning">Earnings</option>
                  <option value="dividend">Dividend</option>
                </select>
                <input
                  type="text"
                  class="form-control"
                  v-model="rule.threshold"
                  placeholder="Threshold"
                  :disabled="rule.type !== 'change'"
                  style="flex: 1;"
                />
                <button class="btn btn-ghost-danger btn-sm" @click="removeRule(index)">✕</button>
              </div>
              <button class="btn btn-sm btn-secondary" @click="addRule">+ {{ t('subscriptions.addRule') }}</button>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-link link-secondary me-auto" @click="dialogVisible = false">{{ t('common.cancel') }}</button>
            <button type="button" class="btn btn-primary" @click="saveSubscription">{{ t('common.save') }}</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="dialogVisible" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../utils/api'

const { t } = useI18n()
const subscriptions = ref([])
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const message = reactive({ text: '', type: 'success' })

const form = ref({
  stock_code: '',
  stock_name: '',
  market: 'A股',
  rules: [{ type: 'change', threshold: '5' }]
})

const showMsg = (text, type = 'success') => {
  message.text = text
  message.type = type
  setTimeout(() => { message.text = '' }, 3000)
}

const parseRules = (rulesJson) => {
  if (!rulesJson) return []
  try {
    return typeof rulesJson === 'string' ? JSON.parse(rulesJson) : rulesJson
  } catch {
    return []
  }
}

const fetchSubscriptions = async () => {
  try {
    subscriptions.value = await api.get('/subscriptions/')
  } catch (error) {
    showMsg('Failed to load subscriptions', 'error')
  }
}

const showAddDialog = () => {
  isEditing.value = false
  editingId.value = null
  form.value = {
    stock_code: '',
    stock_name: '',
    market: 'A股',
    rules: [{ type: 'change', threshold: '5' }]
  }
  dialogVisible.value = true
}

const editSubscription = (row) => {
  isEditing.value = true
  editingId.value = row.id
  form.value = {
    stock_code: row.stock_code,
    stock_name: row.stock_name,
    market: row.market,
    rules: parseRules(row.rules)
  }
  if (form.value.rules.length === 0) {
    form.value.rules = [{ type: 'change', threshold: '5' }]
  }
  dialogVisible.value = true
}

const deleteSubscription = async (row) => {
  if (!confirm(`Are you sure you want to delete ${row.stock_name}?`)) return
  try {
    await api.delete(`/subscriptions/${row.id}`)
    showMsg('Subscription deleted')
    fetchSubscriptions()
  } catch (error) {
    showMsg('Failed to delete subscription', 'error')
  }
}

const addRule = () => {
  form.value.rules.push({ type: 'change', threshold: '5' })
}

const removeRule = (index) => {
  form.value.rules.splice(index, 1)
}

const saveSubscription = async () => {
  try {
    const data = {
      ...form.value,
      rules: JSON.stringify(form.value.rules)
    }
    if (isEditing.value) {
      await api.put(`/subscriptions/${editingId.value}`, data)
      showMsg('Subscription updated')
    } else {
      await api.post('/subscriptions/', data)
      showMsg('Subscription created')
    }
    dialogVisible.value = false
    fetchSubscriptions()
  } catch (error) {
    showMsg('Failed to save subscription', 'error')
  }
}

onMounted(fetchSubscriptions)
</script>
