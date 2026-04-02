<template>
  <div>
    <div class="page-header d-print-none">
      <div class="row align-items-center">
        <div class="col">
          <h2 class="page-title">{{ t('users.title') }}</h2>
        </div>
        <div class="col-auto ms-auto">
          <button class="btn btn-primary" @click="showAddDialog">
            <svg xmlns="http://www.w3.org/2000/svg" class="icon me-1" width="24" height="24" viewBox="0 0 24 24"
              stroke-width="2" stroke="currentColor" fill="none">
              <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            {{ t('users.addUser') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message.text" class="alert mb-3" :class="message.type === 'success' ? 'alert-success' : 'alert-danger'" role="alert">
      {{ message.text }}
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table table-vcenter card-table">
          <thead>
            <tr>
              <th>{{ t('users.email') }}</th>
              <th>{{ t('users.nickname') }}</th>
              <th>{{ t('users.expireDate') }}</th>
              <th>{{ t('common.status') }}</th>
              <th>{{ t('users.subscriptions') }}</th>
              <th>{{ t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="text-center py-4">
                <div class="spinner-border spinner-border-sm text-primary"></div>
              </td>
            </tr>
            <tr v-else-if="users.length === 0">
              <td colspan="6" class="text-center text-muted py-4">暂无用户</td>
            </tr>
            <tr v-for="user in users" :key="user.email">
              <td>
                <div class="d-flex align-items-center">
                  <span class="avatar avatar-sm me-2 bg-primary-lt">{{ user.email?.charAt(0).toUpperCase() }}</span>
                  {{ user.email }}
                </div>
              </td>
              <td class="text-muted">{{ user.name || '-' }}</td>
              <td class="text-muted">{{ user.expire_date }}</td>
              <td>
                <span class="badge" :class="user.is_expired ? 'bg-danger-lt text-danger' : 'bg-success-lt text-success'">
                  {{ user.is_expired ? t('users.expired') : t('users.active') }}
                </span>
              </td>
              <td class="text-muted">{{ user.stocks?.length || 0 }}</td>
              <td>
                <div class="btn-list flex-nowrap">
                  <button class="btn btn-sm btn-ghost-secondary" @click="showSubscriptions(user)">
                    {{ t('users.manageSubscriptions') }}
                  </button>
                  <button class="btn btn-sm btn-ghost-success" @click="showRenewDialog(user)">
                    {{ t('users.renew') }}
                  </button>
                  <button class="btn btn-sm btn-ghost-danger" @click="handleDelete(user)">
                    {{ t('common.delete') }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 添加用户 Modal -->
    <div class="modal modal-blur fade" :class="{ show: addDialogVisible }" :style="{ display: addDialogVisible ? 'block' : 'none' }" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-sm modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ t('users.addUser') }}</h5>
            <button type="button" class="btn-close" @click="addDialogVisible = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label required">{{ t('users.email') }}</label>
              <input type="email" class="form-control" v-model="addForm.email" placeholder="user@example.com" />
            </div>
            <div class="mb-3">
              <label class="form-label">{{ t('users.nickname') }}</label>
              <input type="text" class="form-control" v-model="addForm.name" placeholder="昵称" />
            </div>
            <div class="mb-3">
              <label class="form-label">{{ t('users.expireDays') }}</label>
              <input type="number" class="form-control" v-model.number="addForm.expire_days" min="1" max="365" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-link link-secondary me-auto" @click="addDialogVisible = false">{{ t('common.cancel') }}</button>
            <button type="button" class="btn btn-primary" @click="handleAdd">{{ t('common.confirm') }}</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="addDialogVisible" class="modal-backdrop fade show"></div>

    <!-- 续费 Modal -->
    <div class="modal modal-blur fade" :class="{ show: renewDialogVisible }" :style="{ display: renewDialogVisible ? 'block' : 'none' }" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-sm modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ t('users.renew') }}</h5>
            <button type="button" class="btn-close" @click="renewDialogVisible = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">{{ t('common.email') }}</label>
              <div class="form-control bg-light">{{ currentUser?.email }}</div>
            </div>
            <div class="mb-3">
              <label class="form-label">{{ t('users.renewDays') }}</label>
              <input type="number" class="form-control" v-model.number="renewDays" min="1" max="365" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-link link-secondary me-auto" @click="renewDialogVisible = false">{{ t('common.cancel') }}</button>
            <button type="button" class="btn btn-primary" @click="handleRenew">{{ t('common.confirm') }}</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="renewDialogVisible" class="modal-backdrop fade show"></div>

    <!-- 订阅管理 Modal -->
    <div class="modal modal-blur fade" :class="{ show: subDialogVisible }" :style="{ display: subDialogVisible ? 'block' : 'none' }" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ t('users.manageSubscriptions') }} - {{ currentUser?.email }}</h5>
            <button type="button" class="btn-close" @click="subDialogVisible = false"></button>
          </div>
          <div class="modal-body">
            <div class="d-flex gap-2 mb-3">
              <input
                type="text"
                class="form-control"
                v-model="newStock"
                :placeholder="t('users.inputStock')"
                @keyup.enter="handleAddSubscription"
              />
              <button class="btn btn-primary" @click="handleAddSubscription">{{ t('users.addSubscription') }}</button>
            </div>
            <table class="table table-vcenter">
              <thead>
                <tr>
                  <th>{{ t('users.stockCode') }}</th>
                  <th>{{ t('users.stockName') }}</th>
                  <th>{{ t('common.actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!currentUser?.stocks?.length">
                  <td colspan="3" class="text-center text-muted py-3">暂无订阅</td>
                </tr>
                <tr v-for="stock in (currentUser?.stocks || [])" :key="stock.code">
                  <td>{{ stock.code }}</td>
                  <td>{{ stock.name }}</td>
                  <td>
                    <button class="btn btn-sm btn-ghost-danger" @click="handleDeleteSubscription(stock)">
                      {{ t('common.delete') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="subDialogVisible = false">{{ t('common.close') }}</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="subDialogVisible" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { usersApi } from '../utils/api'

const { t } = useI18n()
const users = ref([])
const loading = ref(false)
const addDialogVisible = ref(false)
const renewDialogVisible = ref(false)
const subDialogVisible = ref(false)
const currentUser = ref(null)
const newStock = ref('')
const renewDays = ref(30)
const message = reactive({ text: '', type: 'success' })

const addForm = reactive({
  email: '',
  name: '',
  expire_days: 30
})

const showMsg = (text, type = 'success') => {
  message.text = text
  message.type = type
  setTimeout(() => { message.text = '' }, 3000)
}

const loadUsers = async () => {
  loading.value = true
  try {
    users.value = await usersApi.list()
  } catch (error) {
    showMsg('加载失败', 'error')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  addForm.email = ''
  addForm.name = ''
  addForm.expire_days = 30
  addDialogVisible.value = true
}

const handleAdd = async () => {
  try {
    await usersApi.create(addForm)
    showMsg(t('common.success'))
    addDialogVisible.value = false
    loadUsers()
  } catch (error) {
    showMsg(error.response?.data?.detail || t('common.error'), 'error')
  }
}

const showRenewDialog = (user) => {
  currentUser.value = user
  renewDays.value = 30
  renewDialogVisible.value = true
}

const handleRenew = async () => {
  try {
    await usersApi.renew(currentUser.value.email, renewDays.value)
    showMsg(t('common.success'))
    renewDialogVisible.value = false
    loadUsers()
  } catch (error) {
    showMsg(error.response?.data?.detail || t('common.error'), 'error')
  }
}

const handleDelete = async (user) => {
  if (!confirm(`确定删除用户 ${user.email}？`)) return
  try {
    await usersApi.delete(user.email)
    showMsg(t('common.success'))
    loadUsers()
  } catch (error) {
    showMsg(error.response?.data?.detail || t('common.error'), 'error')
  }
}

const showSubscriptions = (user) => {
  currentUser.value = user
  newStock.value = ''
  subDialogVisible.value = true
}

const handleAddSubscription = async () => {
  if (!newStock.value) return
  try {
    await usersApi.addSubscription(currentUser.value.email, { stock_code_or_name: newStock.value })
    showMsg(t('common.success'))
    newStock.value = ''
    const updatedUsers = await usersApi.list()
    users.value = updatedUsers
    currentUser.value = updatedUsers.find(u => u.email === currentUser.value.email)
  } catch (error) {
    showMsg(error.response?.data?.detail || t('common.error'), 'error')
  }
}

const handleDeleteSubscription = async (stock) => {
  try {
    await usersApi.deleteSubscription(currentUser.value.email, stock.code || stock.name)
    showMsg(t('common.success'))
    const updatedUsers = await usersApi.list()
    users.value = updatedUsers
    currentUser.value = updatedUsers.find(u => u.email === currentUser.value.email)
  } catch (error) {
    showMsg(error.response?.data?.detail || t('common.error'), 'error')
  }
}

onMounted(loadUsers)
</script>
