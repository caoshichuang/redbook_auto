<template>
  <div>
    <!-- 页面标题 -->
    <div class="page-header d-print-none">
      <div class="row align-items-center">
        <div class="col">
          <h2 class="page-title">{{ t('dashboard.title') }}</h2>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="row row-deck row-cards mb-4">
      <div class="col-sm-6 col-lg-3">
        <div class="card">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="subheader">{{ t('dashboard.todayGenerated') }}</div>
            </div>
            <div class="h1 mb-3" style="color: #206bc4;">{{ stats.today_count || 0 }}</div>
            <div class="d-flex mb-2">
              <div>
                <span class="badge bg-green-lt me-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-inline" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none">
                    <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                    <polyline points="3 17 9 11 13 15 21 7" />
                    <polyline points="14 7 21 7 21 14" />
                  </svg>
                  今日内容
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3">
        <div class="card">
          <div class="card-body">
            <div class="subheader">{{ t('dashboard.totalContent') }}</div>
            <div class="h1 mb-3" style="color: #206bc4;">{{ stats.total_count || 0 }}</div>
            <div class="d-flex mb-2">
              <span class="badge bg-blue-lt">累计生成</span>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3">
        <div class="card">
          <div class="card-body">
            <div class="subheader">{{ t('dashboard.activeUsers') }}</div>
            <div class="h1 mb-3" style="color: #206bc4;">{{ users.length }}</div>
            <div class="d-flex mb-2">
              <span class="badge bg-purple-lt">活跃订阅</span>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3">
        <div class="card">
          <div class="card-body">
            <div class="subheader">{{ t('dashboard.systemStatus') }}</div>
            <div class="h1 mb-3 text-success">{{ t('dashboard.systemOk') }}</div>
            <div class="d-flex mb-2">
              <span class="badge bg-green-lt">
                <span class="status-indicator status-green status-indicator-animated me-1"></span>
                在线
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row row-cards">
      <!-- 快捷操作 -->
      <div class="col-lg-7">
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">{{ t('dashboard.quickActions') }}</h3>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <!-- 美股总结 -->
              <div class="col-sm-6">
                <button
                  class="btn btn-primary w-100"
                  :disabled="tasks.us.loading"
                  @click="triggerTask('us')"
                >
                  <span v-if="tasks.us.loading" class="spinner-border spinner-border-sm me-2"></span>
                  🇺🇸 {{ t('dashboard.triggerUS') }}
                </button>
                <div v-if="tasks.us.showProgress" class="mt-2">
                  <div class="progress" style="height: 6px;">
                    <div
                      class="progress-bar"
                      :class="tasks.us.failed ? 'bg-danger' : 'progress-bar-animated'"
                      :style="{ width: tasks.us.progress + '%' }"
                    ></div>
                  </div>
                  <small class="text-muted mt-1 d-block">{{ tasks.us.message }}</small>
                </div>
              </div>

              <!-- A股总结 -->
              <div class="col-sm-6">
                <button
                  class="btn btn-primary w-100"
                  :disabled="tasks.aShare.loading"
                  @click="triggerTask('aShare')"
                >
                  <span v-if="tasks.aShare.loading" class="spinner-border spinner-border-sm me-2"></span>
                  🇨🇳 {{ t('dashboard.triggerAShare') }}
                </button>
                <div v-if="tasks.aShare.showProgress" class="mt-2">
                  <div class="progress" style="height: 6px;">
                    <div
                      class="progress-bar"
                      :class="tasks.aShare.failed ? 'bg-danger' : 'progress-bar-animated'"
                      :style="{ width: tasks.aShare.progress + '%' }"
                    ></div>
                  </div>
                  <small class="text-muted mt-1 d-block">{{ tasks.aShare.message }}</small>
                </div>
              </div>

              <!-- IPO分析 -->
              <div class="col-sm-6">
                <button
                  class="btn btn-success w-100"
                  :disabled="tasks.ipo.loading"
                  @click="triggerTask('ipo')"
                >
                  <span v-if="tasks.ipo.loading" class="spinner-border spinner-border-sm me-2"></span>
                  📋 {{ t('dashboard.triggerIPO') }}
                </button>
                <div v-if="tasks.ipo.showProgress" class="mt-2">
                  <div class="progress" style="height: 6px;">
                    <div
                      class="progress-bar bg-success"
                      :class="tasks.ipo.failed ? 'bg-danger' : 'progress-bar-animated'"
                      :style="{ width: tasks.ipo.progress + '%' }"
                    ></div>
                  </div>
                  <small class="text-muted mt-1 d-block">{{ tasks.ipo.message }}</small>
                </div>
              </div>

              <!-- 热点个股 -->
              <div class="col-sm-6">
                <button
                  class="btn btn-warning w-100"
                  :disabled="tasks.hot.loading"
                  @click="triggerTask('hot')"
                >
                  <span v-if="tasks.hot.loading" class="spinner-border spinner-border-sm me-2"></span>
                  🔥 {{ t('dashboard.triggerHot') }}
                </button>
                <div v-if="tasks.hot.showProgress" class="mt-2">
                  <div class="progress" style="height: 6px;">
                    <div
                      class="progress-bar bg-warning"
                      :class="tasks.hot.failed ? 'bg-danger' : 'progress-bar-animated'"
                      :style="{ width: tasks.hot.progress + '%' }"
                    ></div>
                  </div>
                  <small class="text-muted mt-1 d-block">{{ tasks.hot.message }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 定时任务 -->
      <div class="col-lg-5">
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">{{ t('dashboard.scheduledJobs') }}</h3>
          </div>
          <div class="table-responsive">
            <table class="table table-vcenter card-table">
              <thead>
                <tr>
                  <th>{{ t('dashboard.jobName') }}</th>
                  <th>{{ t('dashboard.nextRun') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="jobs.length === 0">
                  <td colspan="2" class="text-center text-muted py-3">暂无数据</td>
                </tr>
                <tr v-for="job in jobs" :key="job.id">
                  <td>
                    <span class="text-reset">{{ job.name }}</span>
                  </td>
                  <td class="text-muted">
                    <small>{{ job.next_run }}</small>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { contentApi, usersApi, logsApi } from '../utils/api'

const { t } = useI18n()
const stats = ref({})
const users = ref([])
const jobs = ref([])

// 每个任务的状态
const createTaskState = () => ({
  loading: false,
  showProgress: false,
  progress: 0,
  message: '',
  failed: false,
  pollingTimer: null
})

const tasks = reactive({
  us: createTaskState(),
  aShare: createTaskState(),
  ipo: createTaskState(),
  hot: createTaskState()
})

const triggerApis = {
  us: () => contentApi.triggerUS(),
  aShare: () => contentApi.triggerAShare(),
  ipo: () => contentApi.triggerIPO(),
  hot: () => contentApi.triggerHot()
}

const loadData = async () => {
  try {
    const [statsRes, usersRes, jobsRes] = await Promise.all([
      contentApi.stats(),
      usersApi.list(),
      logsApi.getJobs()
    ])
    stats.value = statsRes
    users.value = usersRes
    jobs.value = jobsRes
  } catch (error) {
    console.error(error)
  }
}

const triggerTask = async (taskKey) => {
  const task = tasks[taskKey]
  task.loading = true
  task.showProgress = true
  task.progress = 5
  task.failed = false
  task.message = t('dashboard.taskTriggered')

  try {
    const res = await triggerApis[taskKey]()
    const taskId = res.task_id

    if (!taskId) {
      // 旧接口直接完成
      task.progress = 100
      task.message = t('dashboard.taskCompleted')
      setTimeout(() => {
        task.showProgress = false
        task.loading = false
        loadData()
      }, 2000)
      return
    }

    // 轮询进度
    task.pollingTimer = setInterval(async () => {
      try {
        const progress = await contentApi.getProgress(taskId)
        task.progress = progress.progress || 0
        task.message = progress.message || ''

        if (progress.status === 'completed') {
          clearInterval(task.pollingTimer)
          task.progress = 100
          task.message = t('dashboard.taskCompleted')
          task.loading = false
          setTimeout(() => {
            task.showProgress = false
            loadData()
          }, 2000)
        } else if (progress.status === 'failed') {
          clearInterval(task.pollingTimer)
          task.failed = true
          task.message = progress.message || t('dashboard.taskFailed')
          task.loading = false
          setTimeout(() => {
            task.showProgress = false
          }, 3000)
        }
      } catch (err) {
        console.error('进度查询失败', err)
      }
    }, 2000)
  } catch (error) {
    task.failed = true
    task.message = error.response?.data?.detail || t('dashboard.taskFailed')
    task.loading = false
    setTimeout(() => {
      task.showProgress = false
    }, 3000)
  }
}

onMounted(loadData)
</script>
