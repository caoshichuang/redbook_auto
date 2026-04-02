<template>
  <div>
    <div class="page-header d-print-none">
      <div class="row align-items-center">
        <div class="col">
          <h2 class="page-title">{{ t('config.title') }}</h2>
        </div>
        <div class="col-auto d-flex gap-2">
          <button class="btn btn-primary" @click="saveAll" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
            {{ t('config.saveAll') }}
          </button>
          <button class="btn btn-secondary" @click="backupConfig">{{ t('config.backup') }}</button>
          <button class="btn btn-warning" @click="showRestoreDialog">{{ t('config.restore') }}</button>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message.text" class="alert mb-3" :class="message.type === 'success' ? 'alert-success' : 'alert-danger'">
      {{ message.text }}
    </div>

    <div class="row">
      <!-- 左侧分类导航 -->
      <div class="col-lg-3">
        <div class="card">
          <div class="list-group list-group-flush">
            <a
              v-for="cat in categories"
              :key="cat.id"
              href="#"
              class="list-group-item list-group-item-action d-flex align-items-center gap-2"
              :class="{ active: activeCategory === cat.id }"
              @click.prevent="handleCategoryChange(cat.id)"
            >
              <span>{{ cat.icon }}</span>
              <span>{{ cat.name }}</span>
            </a>
          </div>
        </div>
      </div>

      <!-- 右侧配置表单 -->
      <div class="col-lg-9">
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">{{ currentCategoryLabel }}</h3>
          </div>
          <div class="card-body">

            <!-- AI 配置 -->
            <div v-if="activeCategory === 'ai'">
              <div class="mb-3">
                <label class="form-label">DeepSeek API Key</label>
                <input type="password" class="form-control" v-model="aiConfig.DEEPSEEK_API_KEY" placeholder="sk-xxxxxxxx" />
                <small class="text-muted">Your DeepSeek API key</small>
              </div>
              <div class="mb-3">
                <label class="form-label">DeepSeek Base URL</label>
                <input type="text" class="form-control" v-model="aiConfig.DEEPSEEK_BASE_URL" placeholder="https://api.deepseek.com" />
                <small class="text-muted">DeepSeek API base URL</small>
              </div>
              <div class="mb-3">
                <label class="form-label">DeepSeek Model</label>
                <select class="form-select" v-model="aiConfig.DEEPSEEK_MODEL">
                  <option value="deepseek-chat">deepseek-chat</option>
                  <option value="deepseek-coder">deepseek-coder</option>
                </select>
                <small class="text-muted">Model to use for content generation</small>
              </div>
            </div>

            <!-- 数据源配置 -->
            <div v-if="activeCategory === 'datasource'">
              <div class="mb-3">
                <label class="form-label">Tushare Token</label>
                <input type="password" class="form-control" v-model="datasourceConfig.TUSHARE_TOKEN" placeholder="Your Tushare token" />
                <small class="text-muted">Tushare API token for data access</small>
              </div>
            </div>

            <!-- 邮件配置 -->
            <div v-if="activeCategory === 'email'">
              <div class="mb-3">
                <label class="form-label">Sender Email</label>
                <input type="email" class="form-control" v-model="emailConfig.QQ_EMAIL" placeholder="your_email@qq.com" />
                <small class="text-muted">QQ email address for sending</small>
              </div>
              <div class="mb-3">
                <label class="form-label">Auth Code</label>
                <input type="password" class="form-control" v-model="emailConfig.QQ_EMAIL_AUTH_CODE" placeholder="16-char auth code" />
                <small class="text-muted">QQ email authorization code</small>
              </div>
              <div class="mb-3">
                <label class="form-label">Receiver Email</label>
                <input type="email" class="form-control" v-model="emailConfig.RECEIVER_EMAIL" placeholder="receiver@example.com" />
                <small class="text-muted">Email address to receive notifications</small>
              </div>
              <div class="mb-3">
                <label class="form-label">SMTP Server</label>
                <input type="text" class="form-control" v-model="emailConfig.SMTP_SERVER" placeholder="smtp.qq.com" />
                <small class="text-muted">SMTP server address</small>
              </div>
              <div class="mb-3">
                <label class="form-label">SMTP Port</label>
                <input type="number" class="form-control" v-model.number="emailConfig.SMTP_PORT" min="1" max="65535" />
                <small class="text-muted">SMTP port (usually 465 for SSL)</small>
              </div>
              <button class="btn btn-secondary" @click="testEmail">{{ t('config.testEmail') }}</button>
            </div>

            <!-- 应用配置 -->
            <div v-if="activeCategory === 'app'">
              <div class="mb-3">
                <label class="form-label">Base URL</label>
                <input type="text" class="form-control" v-model="appConfig.BASE_URL" placeholder="http://your-server:8080" />
                <small class="text-muted">Application access URL</small>
              </div>
              <div class="mb-3">
                <label class="form-label">Log Level</label>
                <select class="form-select" v-model="appConfig.LOG_LEVEL">
                  <option value="DEBUG">DEBUG</option>
                  <option value="INFO">INFO</option>
                  <option value="WARNING">WARNING</option>
                  <option value="ERROR">ERROR</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Log Rotation</label>
                <input type="text" class="form-control" v-model="appConfig.LOG_ROTATION" placeholder="10 MB" />
                <small class="text-muted">Log file rotation size (e.g., 10 MB)</small>
              </div>
              <div class="mb-3">
                <label class="form-label">Log Retention</label>
                <input type="text" class="form-control" v-model="appConfig.LOG_RETENTION" placeholder="30 days" />
                <small class="text-muted">Log file retention period</small>
              </div>
            </div>

            <!-- 明星股票配置 -->
            <div v-if="activeCategory === 'star_stocks'">
              <ul class="nav nav-tabs mb-3">
                <li class="nav-item" v-for="market in ['A股', '港股', '美股']" :key="market">
                  <a class="nav-link" :class="{ active: starTab === market }" href="#" @click.prevent="starTab = market">
                    {{ market }}
                  </a>
                </li>
              </ul>
              <div v-for="market in ['A股', '港股', '美股']" :key="market" v-show="starTab === market">
                <div v-for="(stock, index) in (starStocksConfig[market] || [])" :key="index" class="d-flex gap-2 mb-2">
                  <input type="text" class="form-control" v-model="stock.code" placeholder="Code" />
                  <input type="text" class="form-control" v-model="stock.name" placeholder="Name" />
                  <button class="btn btn-ghost-danger btn-sm" @click="removeStock(market, index)">✕</button>
                </div>
                <button class="btn btn-primary btn-sm mt-2" @click="addStock(market)">+ Add {{ market }} Stock</button>
              </div>
            </div>

            <!-- 业务阈值配置 -->
            <div v-if="activeCategory === 'thresholds'">
              <div class="mb-3">
                <label class="form-label">Hot Stock Threshold (%)</label>
                <input type="number" class="form-control" v-model.number="thresholdsConfig.hot_stock_threshold" min="0" max="100" step="0.1" />
                <small class="text-muted">Price change threshold for hot stock alerts</small>
              </div>
              <div class="mb-3">
                <label class="form-label">Limit Up/Down Threshold (%)</label>
                <input type="number" class="form-control" v-model.number="thresholdsConfig.limit_up_down_threshold" min="0" max="100" step="0.1" />
                <small class="text-muted">Threshold for limit up/down detection</small>
              </div>
            </div>

            <!-- 定时任务配置 -->
            <div v-if="activeCategory === 'scheduler'">
              <div class="mb-3">
                <label class="form-label">US Stock Summary Time</label>
                <input type="time" class="form-control" v-model="schedulerConfig.us_stock_time" />
                <small class="text-muted">Daily US stock market summary time</small>
              </div>
              <div class="mb-3">
                <label class="form-label">A-Share Summary Time</label>
                <input type="time" class="form-control" v-model="schedulerConfig.a_share_time" />
                <small class="text-muted">Daily A-share and HK stock summary time</small>
              </div>
              <div class="mb-3">
                <label class="form-label">Hot Stocks Time</label>
                <input type="time" class="form-control" v-model="schedulerConfig.hot_stock_time" />
                <small class="text-muted">Daily hot stock analysis time</small>
              </div>
              <div class="mb-3">
                <label class="form-label">IPO Analysis Time</label>
                <input type="time" class="form-control" v-model="schedulerConfig.ipo_time" />
                <small class="text-muted">Daily IPO analysis time</small>
              </div>
            </div>

            <!-- 项目信息配置 -->
            <div v-if="activeCategory === 'project'">
              <div class="mb-3">
                <label class="form-label">Project Name</label>
                <input type="text" class="form-control" v-model="projectConfig.project_name" placeholder="FinanceSail" />
              </div>
              <div class="mb-3">
                <label class="form-label">Project Name (EN)</label>
                <input type="text" class="form-control" v-model="projectConfig.project_name_en" placeholder="FinanceSail" />
              </div>
              <div class="mb-3">
                <label class="form-label">Version</label>
                <input type="text" class="form-control" v-model="projectConfig.project_version" placeholder="1.0.0" />
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea class="form-control" v-model="projectConfig.project_description" rows="3" placeholder="Automated Financial Content Distribution System"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Logo</label>
                <input type="text" class="form-control" v-model="projectConfig.project_logo" placeholder="⛵" />
              </div>
              <div class="mb-3">
                <label class="form-label">Slogan</label>
                <input type="text" class="form-control" v-model="projectConfig.project_slogan" placeholder="Empowering Financial Content Distribution" />
              </div>
            </div>

            <!-- 节假日配置 -->
            <div v-if="activeCategory === 'holidays'">
              <ul class="nav nav-tabs mb-3">
                <li class="nav-item" v-for="year in Object.keys(holidaysConfig)" :key="year">
                  <a class="nav-link" :class="{ active: holidayTab === year }" href="#" @click.prevent="holidayTab = year">
                    {{ year }}
                  </a>
                </li>
              </ul>
              <div v-for="year in Object.keys(holidaysConfig)" :key="year" v-show="holidayTab === year">
                <div class="d-flex flex-wrap gap-2 mb-3">
                  <span
                    v-for="(date, index) in holidaysConfig[year]"
                    :key="index"
                    class="badge bg-azure-lt text-azure d-flex align-items-center gap-1"
                    style="font-size: 0.85rem; padding: 6px 10px;"
                  >
                    {{ date }}
                    <button type="button" class="btn-close btn-close-sm" style="font-size: 0.6rem;" @click="removeHoliday(year, index)"></button>
                  </span>
                </div>
                <div class="d-flex gap-2 mt-2">
                  <input type="date" class="form-control" v-model="newHoliday[year]" style="width: 200px;" />
                  <button class="btn btn-primary btn-sm" @click="addHoliday(year)">Add</button>
                </div>
              </div>
              <button class="btn btn-secondary btn-sm mt-3" @click="addYear">{{ t('config.addYear') }}</button>
            </div>

            <!-- 分发平台配置 -->
            <div v-if="activeCategory === 'distribution'">
              <div class="mb-3">
                <label class="form-label">WeChat App ID</label>
                <input type="text" class="form-control" v-model="distributionConfig.wechat_app_id" placeholder="Your WeChat App ID" />
                <small class="text-muted">WeChat Official Account App ID</small>
              </div>
              <div class="mb-3">
                <label class="form-label">WeChat App Secret</label>
                <input type="password" class="form-control" v-model="distributionConfig.wechat_app_secret" placeholder="Your WeChat App Secret" />
                <small class="text-muted">WeChat Official Account App Secret</small>
              </div>
              <div class="mb-3">
                <label class="form-label">Toutiao Access Token</label>
                <input type="password" class="form-control" v-model="distributionConfig.toutiao_access_token" placeholder="Your Toutiao Access Token" />
                <small class="text-muted">Toutiao (ByteDance) API access token</small>
              </div>
              <div class="mb-3">
                <label class="form-label">WxPusher App Token</label>
                <input type="password" class="form-control" v-model="distributionConfig.wxpusher_app_token" placeholder="Your WxPusher App Token" />
                <small class="text-muted">WxPusher application token</small>
              </div>
            </div>

            <!-- 分析策略配置 -->
            <div v-if="activeCategory === 'strategies'">
              <div v-if="strategiesLoading" class="text-center py-4">
                <div class="spinner-border text-primary"></div>
              </div>
              <div v-else>
                <div v-for="market in strategyMarkets" :key="market" class="mb-4">
                  <div class="card">
                    <div class="card-header">
                      <h4 class="card-title mb-0">{{ market }}</h4>
                    </div>
                    <div class="card-body">
                      <div class="row g-2">
                        <div
                          v-for="strategy in allStrategies.filter(s => s.markets.includes(market))"
                          :key="strategy.id"
                          class="col-sm-6"
                        >
                          <label class="form-check">
                            <input
                              type="checkbox"
                              class="form-check-input"
                              :value="strategy.id"
                              v-model="enabledStrategies[market]"
                            />
                            <span class="form-check-label">
                              <strong>{{ strategy.display_name }}</strong>
                              <br />
                              <small class="text-muted">{{ strategy.description }}</small>
                            </span>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <button class="btn btn-primary" @click="saveStrategies" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                  {{ t('config.saveStrategies') }}
                </button>
              </div>
            </div>

            <!-- 保存按钮（策略页除外，策略有独立按钮） -->
            <div v-if="activeCategory !== 'strategies'" class="mt-4 pt-3 border-top d-flex gap-2">
              <button class="btn btn-primary" @click="saveCategory" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                {{ t('config.saveCategory') }}
              </button>
              <button class="btn btn-secondary" @click="resetCategory">{{ t('common.reset') }}</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 恢复配置 Modal -->
    <div class="modal modal-blur fade" :class="{ show: restoreDialogVisible }" :style="{ display: restoreDialogVisible ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog modal-sm modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Restore Configuration</h5>
            <button type="button" class="btn-close" @click="restoreDialogVisible = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Select backup file (.json)</label>
              <input type="file" class="form-control" accept=".json" @change="handleRestoreFile" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="restoreDialogVisible = false">Cancel</button>
            <button type="button" class="btn btn-primary" @click="restoreConfig" :disabled="!restoreFile">Restore</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="restoreDialogVisible" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import api, { strategyApi } from '../utils/api'

const { t } = useI18n()
const categories = ref([])
const activeCategory = ref('ai')
const saving = ref(false)
const restoreDialogVisible = ref(false)
const restoreFile = ref(null)
const starTab = ref('A股')
const holidayTab = ref('')
const message = reactive({ text: '', type: 'success' })

// 策略配置相关
const allStrategies = ref([])
const enabledStrategies = ref({
  US_STOCK: [],
  A_SHARE: [],
  IPO: [],
  HOT: []
})
const strategyMarkets = ['US_STOCK', 'A_SHARE', 'IPO', 'HOT']
const strategiesLoading = ref(false)

const showMsg = (text, type = 'success') => {
  message.text = text
  message.type = type
  setTimeout(() => { message.text = '' }, 3000)
}

// 配置数据
const aiConfig = ref({
  DEEPSEEK_API_KEY: '',
  DEEPSEEK_BASE_URL: 'https://api.deepseek.com',
  DEEPSEEK_MODEL: 'deepseek-chat'
})

const datasourceConfig = ref({
  TUSHARE_TOKEN: ''
})

const emailConfig = ref({
  QQ_EMAIL: '',
  QQ_EMAIL_AUTH_CODE: '',
  RECEIVER_EMAIL: '',
  SMTP_SERVER: 'smtp.qq.com',
  SMTP_PORT: 465
})

const appConfig = ref({
  BASE_URL: 'http://localhost:8080',
  LOG_LEVEL: 'INFO',
  LOG_ROTATION: '10 MB',
  LOG_RETENTION: '30 days'
})

const starStocksConfig = ref({
  'A股': [],
  '港股': [],
  '美股': []
})

const thresholdsConfig = ref({
  hot_stock_threshold: 3.0,
  limit_up_down_threshold: 9.9
})

const schedulerConfig = ref({
  us_stock_time: '09:00',
  a_share_time: '17:00',
  hot_stock_time: '17:30',
  ipo_time: '20:00'
})

const projectConfig = ref({
  project_name: 'FinanceSail',
  project_name_en: 'FinanceSail',
  project_version: '1.0.0',
  project_description: 'Automated Financial Content Distribution System',
  project_logo: '⛵',
  project_slogan: 'Empowering Financial Content Distribution'
})

const holidaysConfig = ref({})
const newHoliday = ref({})

const distributionConfig = ref({
  wechat_app_id: '',
  wechat_app_secret: '',
  toutiao_access_token: '',
  wxpusher_app_token: ''
})

const currentCategoryLabel = computed(() => {
  const cat = categories.value.find(c => c.id === activeCategory.value)
  return cat?.name || t('config.title')
})

const fetchCategories = async () => {
  try {
    const data = await api.get('/config/categories')
    categories.value = data.categories
    // 添加策略分类
    if (!categories.value.find(c => c.id === 'strategies')) {
      categories.value.push({ id: 'strategies', name: t('config.strategies'), icon: '🎯' })
    }
  } catch (error) {
    // 静默失败，使用默认分类
    categories.value = [
      { id: 'ai', name: t('config.ai'), icon: '🤖' },
      { id: 'datasource', name: t('config.datasource'), icon: '📊' },
      { id: 'email', name: t('config.email'), icon: '📧' },
      { id: 'app', name: t('config.app'), icon: '⚙️' },
      { id: 'star_stocks', name: t('config.star_stocks'), icon: '⭐' },
      { id: 'thresholds', name: t('config.thresholds'), icon: '📏' },
      { id: 'scheduler', name: t('config.scheduler'), icon: '⏰' },
      { id: 'project', name: t('config.project'), icon: '🚀' },
      { id: 'holidays', name: t('config.holidays'), icon: '📅' },
      { id: 'distribution', name: t('config.distribution'), icon: '📤' },
      { id: 'strategies', name: t('config.strategies'), icon: '🎯' }
    ]
  }
}

const fetchCategoryConfig = async (category) => {
  if (category === 'strategies') {
    await fetchStrategies()
    return
  }
  try {
    const data = await api.get(`/config/category/${category}`)
    switch (category) {
      case 'ai': aiConfig.value = data; break
      case 'datasource': datasourceConfig.value = data; break
      case 'email': emailConfig.value = data; break
      case 'app': appConfig.value = data; break
      case 'star_stocks': starStocksConfig.value = data; break
      case 'thresholds': thresholdsConfig.value = data; break
      case 'scheduler': schedulerConfig.value = data; break
      case 'project': projectConfig.value = data; break
      case 'holidays':
        holidaysConfig.value = data
        Object.keys(data).forEach(year => {
          newHoliday.value[year] = ''
        })
        if (Object.keys(data).length > 0) {
          holidayTab.value = Object.keys(data)[0]
        }
        break
      case 'distribution': distributionConfig.value = data; break
    }
  } catch (error) {
    console.error(`Failed to fetch ${category} config:`, error)
  }
}

const fetchStrategies = async () => {
  strategiesLoading.value = true
  try {
    const res = await strategyApi.list()
    allStrategies.value = res.strategies || []

    // 获取各市场已启用的策略
    for (const market of strategyMarkets) {
      try {
        const enabled = await strategyApi.getEnabled(market)
        enabledStrategies.value[market] = enabled.enabled_strategy_ids || []
      } catch {
        enabledStrategies.value[market] = []
      }
    }
  } catch (error) {
    console.error('Failed to fetch strategies:', error)
  } finally {
    strategiesLoading.value = false
  }
}

const saveStrategies = async () => {
  saving.value = true
  try {
    for (const market of strategyMarkets) {
      await strategyApi.setEnabled(market, enabledStrategies.value[market])
    }
    showMsg(t('config.strategiesSaved'))
  } catch (error) {
    showMsg('Failed to save strategies', 'error')
  } finally {
    saving.value = false
  }
}

const handleCategoryChange = (categoryId) => {
  activeCategory.value = categoryId
  fetchCategoryConfig(categoryId)
}

const saveCategory = async () => {
  saving.value = true
  try {
    let configData
    switch (activeCategory.value) {
      case 'ai': configData = aiConfig.value; break
      case 'datasource': configData = datasourceConfig.value; break
      case 'email': configData = emailConfig.value; break
      case 'app': configData = appConfig.value; break
      case 'star_stocks': configData = starStocksConfig.value; break
      case 'thresholds': configData = thresholdsConfig.value; break
      case 'scheduler': configData = schedulerConfig.value; break
      case 'project': configData = projectConfig.value; break
      case 'holidays': configData = holidaysConfig.value; break
      case 'distribution': configData = distributionConfig.value; break
    }
    await api.put(`/config/category/${activeCategory.value}`, configData)
    showMsg('Configuration saved successfully')
  } catch (error) {
    showMsg('Failed to save configuration', 'error')
  } finally {
    saving.value = false
  }
}

const resetCategory = () => {
  fetchCategoryConfig(activeCategory.value)
}

const saveAll = async () => {
  saving.value = true
  try {
    const allConfig = {
      ai: aiConfig.value,
      datasource: datasourceConfig.value,
      email: emailConfig.value,
      app: appConfig.value,
      star_stocks: starStocksConfig.value,
      thresholds: thresholdsConfig.value,
      scheduler: schedulerConfig.value,
      project: projectConfig.value,
      holidays: holidaysConfig.value,
      distribution: distributionConfig.value
    }
    await api.put('/config/batch', { configs: allConfig })
    showMsg('All configurations saved successfully')
  } catch (error) {
    showMsg('Failed to save all configurations', 'error')
  } finally {
    saving.value = false
  }
}

const backupConfig = async () => {
  try {
    const response = await api.get('/config/backup')
    const { backup_data } = response
    const blob = new Blob([JSON.stringify(backup_data, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `config_backup_${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    window.URL.revokeObjectURL(url)
    showMsg('Configuration backup downloaded')
  } catch (error) {
    showMsg('Failed to backup configuration', 'error')
  }
}

const showRestoreDialog = () => {
  restoreDialogVisible.value = true
}

const handleRestoreFile = (e) => {
  restoreFile.value = e.target.files[0] || null
}

const restoreConfig = async () => {
  if (!restoreFile.value) return
  try {
    const reader = new FileReader()
    reader.onload = async (e) => {
      try {
        const backupData = JSON.parse(e.target.result)
        await api.post('/config/restore', backupData)
        showMsg('Configuration restored successfully')
        restoreDialogVisible.value = false
        Object.keys(backupData).forEach(category => {
          fetchCategoryConfig(category)
        })
      } catch (error) {
        showMsg('Failed to restore configuration', 'error')
      }
    }
    reader.readAsText(restoreFile.value)
  } catch (error) {
    showMsg('Failed to read backup file', 'error')
  }
}

const testEmail = async () => {
  try {
    const response = await api.post('/config/test/email')
    if (response.success) {
      showMsg('Test email sent successfully')
    } else {
      showMsg(response.message, 'error')
    }
  } catch (error) {
    showMsg('Failed to test email configuration', 'error')
  }
}

// 明星股操作
const addStock = (market) => {
  if (!starStocksConfig.value[market]) {
    starStocksConfig.value[market] = []
  }
  starStocksConfig.value[market].push({ code: '', name: '' })
}

const removeStock = (market, index) => {
  starStocksConfig.value[market].splice(index, 1)
}

// 节假日操作
const addHoliday = (year) => {
  if (newHoliday.value[year]) {
    holidaysConfig.value[year].push(newHoliday.value[year])
    newHoliday.value[year] = ''
  }
}

const removeHoliday = (year, index) => {
  holidaysConfig.value[year].splice(index, 1)
}

const addYear = () => {
  const year = String(new Date().getFullYear() + 1)
  if (!holidaysConfig.value[year]) {
    holidaysConfig.value[year] = []
    newHoliday.value[year] = ''
    holidayTab.value = year
  }
}

onMounted(() => {
  fetchCategories()
  fetchCategoryConfig('ai')
})
</script>
