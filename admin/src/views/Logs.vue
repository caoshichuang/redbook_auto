<template>
  <div>
    <div class="page-header d-print-none">
      <div class="row align-items-center">
        <div class="col">
          <h2 class="page-title">{{ t('logs.title') }}</h2>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="card">
      <div class="card-header">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'status' }" href="#" @click.prevent="activeTab = 'status'">
              {{ t('logs.systemStatus') }}
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'app' }" href="#" @click.prevent="switchTab('app')">
              {{ t('logs.appLog') }}
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'error' }" href="#" @click.prevent="switchTab('error')">
              {{ t('logs.errorLog') }}
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'jobs' }" href="#" @click.prevent="switchTab('jobs')">
              {{ t('logs.scheduledJobs') }}
            </a>
          </li>
        </ul>
      </div>

      <div class="card-body">
        <!-- 系统状态 -->
        <div v-if="activeTab === 'status'">
          <div v-if="loadingStatus" class="text-center py-4">
            <div class="spinner-border text-primary"></div>
          </div>
          <div v-else class="row g-3">
            <div class="col-sm-6 col-lg-3">
              <div class="card">
                <div class="card-body p-3 text-center">
                  <div class="text-muted mb-1">{{ t('logs.cpu') }}</div>
                  <div class="h2 mb-0">{{ systemStatus.cpu_percent || 0 }}%</div>
                  <div class="progress mt-2" style="height: 4px;">
                    <div class="progress-bar" :class="cpuClass" :style="{ width: (systemStatus.cpu_percent || 0) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="card">
                <div class="card-body p-3 text-center">
                  <div class="text-muted mb-1">{{ t('logs.memory') }}</div>
                  <div class="h2 mb-0">{{ systemStatus.memory?.percent || 0 }}%</div>
                  <div class="progress mt-2" style="height: 4px;">
                    <div class="progress-bar bg-blue" :style="{ width: (systemStatus.memory?.percent || 0) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="card">
                <div class="card-body p-3 text-center">
                  <div class="text-muted mb-1">{{ t('logs.disk') }}</div>
                  <div class="h2 mb-0">{{ systemStatus.disk?.percent || 0 }}%</div>
                  <div class="progress mt-2" style="height: 4px;">
                    <div class="progress-bar bg-green" :style="{ width: (systemStatus.disk?.percent || 0) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="card">
                <div class="card-body p-3 text-center">
                  <div class="text-muted mb-1">{{ t('logs.pythonVersion') }}</div>
                  <div class="h4 mb-0">{{ systemStatus.python_version || '-' }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 应用日志 -->
        <div v-if="activeTab === 'app'">
          <div class="d-flex justify-content-end mb-2">
            <button class="btn btn-sm btn-secondary" @click="loadAppLog" :disabled="loadingApp">
              <span v-if="loadingApp" class="spinner-border spinner-border-sm me-1"></span>
              {{ t('common.refresh') }}
            </button>
          </div>
          <pre class="bg-dark text-success p-3 rounded" style="height: 500px; overflow-y: auto; font-size: 0.8rem; line-height: 1.5;">{{ appLog }}</pre>
        </div>

        <!-- 错误日志 -->
        <div v-if="activeTab === 'error'">
          <div class="d-flex justify-content-end mb-2">
            <button class="btn btn-sm btn-secondary" @click="loadErrorLog" :disabled="loadingError">
              <span v-if="loadingError" class="spinner-border spinner-border-sm me-1"></span>
              {{ t('common.refresh') }}
            </button>
          </div>
          <pre class="bg-dark text-danger p-3 rounded" style="height: 500px; overflow-y: auto; font-size: 0.8rem; line-height: 1.5;">{{ errorLog }}</pre>
        </div>

        <!-- 定时任务 -->
        <div v-if="activeTab === 'jobs'">
          <div v-if="loadingJobs" class="text-center py-4">
            <div class="spinner-border text-primary"></div>
          </div>
          <table v-else class="table table-vcenter card-table">
            <thead>
              <tr>
                <th>{{ t('logs.jobId') }}</th>
                <th>{{ t('logs.jobName') }}</th>
                <th>{{ t('logs.trigger') }}</th>
                <th>{{ t('logs.nextRun') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="jobs.length === 0">
                <td colspan="4" class="text-center text-muted py-3">暂无任务</td>
              </tr>
              <tr v-for="job in jobs" :key="job.id">
                <td><small class="text-muted font-monospace">{{ job.id }}</small></td>
                <td>{{ job.name }}</td>
                <td class="text-muted">{{ job.trigger }}</td>
                <td class="text-muted">{{ job.next_run }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { logsApi } from '../utils/api'

const { t } = useI18n()
const activeTab = ref('status')
const loadingStatus = ref(false)
const loadingApp = ref(false)
const loadingError = ref(false)
const loadingJobs = ref(false)

const systemStatus = ref({})
const appLogLines = ref([])
const errorLogLines = ref([])
const jobs = ref([])

const appLog = computed(() => appLogLines.value.join('\n'))
const errorLog = computed(() => errorLogLines.value.join('\n'))

const cpuClass = computed(() => {
  const cpu = systemStatus.value.cpu_percent || 0
  if (cpu > 80) return 'bg-danger'
  if (cpu > 60) return 'bg-warning'
  return 'bg-success'
})

const switchTab = (tab) => {
  activeTab.value = tab
  if (tab === 'app' && appLogLines.value.length === 0) loadAppLog()
  if (tab === 'error' && errorLogLines.value.length === 0) loadErrorLog()
  if (tab === 'jobs' && jobs.value.length === 0) loadJobs()
}

const loadSystemStatus = async () => {
  loadingStatus.value = true
  try {
    systemStatus.value = await logsApi.getSystemStatus()
  } catch (error) {
    console.error('加载系统状态失败', error)
  } finally {
    loadingStatus.value = false
  }
}

const loadAppLog = async () => {
  loadingApp.value = true
  try {
    const res = await logsApi.getAppLog(200)
    appLogLines.value = res.lines
  } catch (error) {
    console.error('加载日志失败', error)
  } finally {
    loadingApp.value = false
  }
}

const loadErrorLog = async () => {
  loadingError.value = true
  try {
    const res = await logsApi.getErrorLog(200)
    errorLogLines.value = res.lines
  } catch (error) {
    console.error('加载日志失败', error)
  } finally {
    loadingError.value = false
  }
}

const loadJobs = async () => {
  loadingJobs.value = true
  try {
    jobs.value = await logsApi.getJobs()
  } catch (error) {
    console.error('加载任务状态失败', error)
  } finally {
    loadingJobs.value = false
  }
}

onMounted(() => {
  loadSystemStatus()
  loadAppLog()
})
</script>
