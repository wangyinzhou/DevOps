<template>
  <div class="shell">
    <section class="login-page" v-if="view==='login'">
      <div class="login-card">
        <h1 style="text-align:center;font-size:44px;margin:0 0 8px;">Mock CPE 智能网关 Web 管理平台</h1>
        <p style="text-align:center;color:#6b7fa8;margin:0 0 20px;">管理员登录</p>
        <el-form label-position="top">
          <el-form-item label="用户名"><el-input model-value="admin" /></el-form-item>
          <el-form-item label="密码"><el-input type="password" model-value="admin123" show-password /></el-form-item>
          <el-button type="primary" style="width:100%;height:50px;font-size:28px;" @click="view='dashboard'">登 录</el-button>
        </el-form>
      </div>
    </section>

    <section v-else class="layout">
      <aside class="sidebar">
        <h3 style="margin:0 0 18px;">Mock CPE 智能网关 Web 管理平台</h3>
        <el-menu :default-active="active" @select="active = $event">
          <el-menu-item index="dashboard">控制台</el-menu-item>
          <el-menu-item index="network">网络配置</el-menu-item>
          <el-menu-item index="upgrade">固件升级</el-menu-item>
          <el-menu-item index="diagnostics">运行诊断</el-menu-item>
          <el-menu-item index="artifacts">固件制品</el-menu-item>
          <el-menu-item index="jobs">升级任务</el-menu-item>
        </el-menu>
      </aside>
      <div>
        <div class="topbar"><div>admin</div><el-button link @click="view='login'">退出</el-button></div>
        <main class="content">
          <div class="banner">
            <h2 style="margin:0 0 6px;font-size:48px;">{{ bannerTitle }}</h2>
            <div style="color:#4d6591;">页面采用蓝白运营商风格卡片式布局，作为论文演示基线界面。</div>
          </div>
          <template v-if="active==='dashboard'">
            <div class="grid">
              <div class="card">设备型号：{{ dashboard.model }}</div>
              <div class="card">固件版本：{{ dashboard.fw }}</div>
              <div class="card">运行时间：{{ dashboard.uptime }}</div>
              <div class="card">WAN 状态：{{ dashboard.wan }}</div>
            </div>
          </template>

          <template v-else-if="active==='network'">
            <section class="dual">
              <div class="card">
                <h3>无线网络设置</h3>
                <el-form label-position="top" class="form-grid">
                  <el-row :gutter="12">
                    <el-col :span="12"><el-form-item label="SSID"><el-input model-value="CPE-X1000_Home" /></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="无线密码"><el-input type="password" model-value="12345678" show-password /></el-form-item></el-col>
                  </el-row>
                  <el-row :gutter="12">
                    <el-col :span="12"><el-form-item label="联网模式"><el-select model-value="PPPoE"><el-option label="PPPoE" value="PPPoE" /></el-select></el-form-item></el-col>
                    <el-col :span="12"><el-form-item label="Wi‑Fi 信道"><el-select model-value="自动"><el-option label="自动" value="自动" /></el-select></el-form-item></el-col>
                  </el-row>
                  <el-button type="primary">保存配置</el-button>
                </el-form>
              </div>
              <div class="card">
                <h3>当前配置摘要</h3>
                <ul class="meta-list">
                  <li><span>SSID</span><strong>{{ networkSummary.ssid }}</strong></li>
                  <li><span>联网模式</span><strong>{{ networkSummary.mode }}</strong></li>
                  <li><span>访客 Wi‑Fi</span><strong>{{ networkSummary.guest }}</strong></li>
                  <li><span>信道</span><strong>{{ networkSummary.channel }}</strong></li>
                </ul>
              </div>
            </section>
          </template>

          <template v-else-if="active==='upgrade'">
            <section class="dual">
              <div class="card">
                <h3>固件文件校验</h3>
                <el-form label-position="top">
                  <el-form-item label="固件文件名"><el-input model-value="cpe_gateway_v1.2.3.bin" /></el-form-item>
                  <el-form-item label="命名规范"><el-input model-value="仅允许 .bin 后缀，格式：cpe_gateway_vX.Y.Z.bin" /></el-form-item>
                  <el-button type="primary">开始校验</el-button>
                </el-form>
              </div>
              <div class="card">
                <h3>当前升级信息</h3>
                <ul class="meta-list">
                  <li><span>当前固件版本</span><strong>{{ upgradeSummary.current }}</strong></li>
                  <li><span>目标固件版本</span><strong>{{ upgradeSummary.target }}</strong></li>
                  <li><span>校验状态</span><strong style="color:#16a34a">{{ upgradeSummary.status }}</strong></li>
                </ul>
              </div>
            </section>
          </template>

          <template v-else-if="active==='artifacts'">
            <section class="dual">
              <div class="card">
                <h3>制品登记</h3>
                <el-form label-position="top">
                  <el-form-item label="固件文件名"><el-input model-value="cpe_gateway_v1.2.3.bin" /></el-form-item>
                  <el-form-item label="来源类型"><el-select model-value="Jenkins 构建"><el-option label="Jenkins 构建" value="Jenkins 构建" /></el-select></el-form-item>
                  <el-button type="primary">登记制品</el-button>
                </el-form>
              </div>
              <div class="card">
                <h3>当前制品摘要</h3>
                <ul class="meta-list">
                  <li><span>当前制品版本</span><strong>{{ artifactsSummary.version }}</strong></li>
                  <li><span>来源类型</span><strong>{{ artifactsSummary.source }}</strong></li>
                  <li><span>MD5 状态</span><strong style="color:#16a34a">{{ artifactsSummary.md5 }}</strong></li>
                </ul>
              </div>
            </section>
            <div class="card" style="margin-top:14px;">
              <h3>制品列表</h3>
              <el-table :data="liveArtifactRows">
                <el-table-column prop="name" label="文件名" />
                <el-table-column prop="version" label="版本" />
                <el-table-column prop="source" label="来源" />
              </el-table>
            </div>
          </template>

          <template v-else-if="active==='jobs'">
            <section class="dual">
              <div class="card">
                <h3>创建升级任务</h3>
                <el-form label-position="top">
                  <el-form-item label="选择固件制品"><el-select model-value="cpe_gateway_v1.2.3.bin"><el-option label="cpe_gateway_v1.2.3.bin" value="cpe_gateway_v1.2.3.bin" /></el-select></el-form-item>
                  <el-form-item label="设备协议"><el-select model-value="mock"><el-option label="mock" value="mock" /></el-select></el-form-item>
                  <el-button type="primary">创建并执行任务</el-button>
                </el-form>
              </div>
              <div class="card">
                <h3>当前任务摘要</h3>
                <ul class="meta-list">
                  <li><span>当前任务状态</span><strong style="color:#16a34a">{{ jobsSummary.status }}</strong></li>
                  <li><span>目标固件版本</span><strong>{{ jobsSummary.target }}</strong></li>
                  <li><span>API 检查</span><strong style="color:#16a34a">{{ jobsSummary.api }}</strong></li>
                </ul>
              </div>
            </section>
          </template>
        </main>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
const view = ref<'login' | 'dashboard'>('login')
const active = ref('dashboard')
const apiBase = (import.meta.env.VITE_API_BASE as string | undefined) ?? 'http://127.0.0.1:5000/api/v1'

const dashboard = ref({ model: 'CPE-X1000', fw: 'v1.2.3', uptime: '-', wan: '在线' })
const networkSummary = ref({ ssid: 'CPE-X1000_Home', mode: 'PPPoE', guest: '已启用', channel: '自动' })
const upgradeSummary = ref({ current: 'v1.2.2', target: 'v1.2.3', status: '已通过' })
const artifactsSummary = ref({ version: 'v1.2.3', source: 'Jenkins 构建', md5: '已生成' })
const jobsSummary = ref({ status: 'passed', target: 'v1.2.3', api: '通过' })
const bannerTitle = computed(() => ({
  dashboard: '欢迎，admin',
  network: '网络配置',
  upgrade: '固件升级',
  diagnostics: '运行诊断',
  artifacts: '固件制品管理',
  jobs: '升级任务'
}[active.value] ?? '控制台'))

const artifactRows = [
  { name: 'cpe_gateway_v1.2.3.bin', version: 'v1.2.3', source: 'Jenkins 构建' },
  { name: 'cpe_gateway_v1.2.2.bin', version: 'v1.2.2', source: 'Jenkins 构建' }
]

const liveArtifactRows = ref(artifactRows)

async function fetchJson(path: string) {
  const resp = await fetch(`${apiBase}${path}`)
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
  return await resp.json()
}

async function loadDashboard() {
  try {
    const data = await fetchJson('/dashboard')
    dashboard.value = {
      model: data.system?.device_model ?? dashboard.value.model,
      fw: data.system?.firmware_version ?? dashboard.value.fw,
      uptime: data.system?.uptime ?? '-',
      wan: data.system?.wan_status ?? '在线'
    }
  } catch (_e) {
    // keep demo fallback
  }
}

async function loadNetworkSummary() {
  try {
    const data = await fetchJson('/network')
    networkSummary.value = {
      ssid: data.network?.ssid ?? networkSummary.value.ssid,
      mode: String(data.network?.mode ?? networkSummary.value.mode).toUpperCase(),
      guest: data.network?.guest_wifi === 'enabled' ? '已启用' : '已禁用',
      channel: data.network?.channel ?? networkSummary.value.channel
    }
  } catch (_e) {}
}

async function loadUpgradeSummary() {
  try {
    const data = await fetchJson('/upgrade')
    upgradeSummary.value = {
      current: data.current_version ?? upgradeSummary.value.current,
      target: data.target_version ?? upgradeSummary.value.target,
      status: data.status ?? upgradeSummary.value.status
    }
  } catch (_e) {}
}

async function loadArtifacts() {
  try {
    const data = await fetchJson('/artifacts')
    if (Array.isArray(data.artifacts)) {
      liveArtifactRows.value = data.artifacts.map((item: any) => ({
        name: item.filename,
        version: `v${item.version}`,
        source: item.source_type
      }))
      const first = data.artifacts[0]
      if (first) {
        artifactsSummary.value = {
          version: `v${first.version}`,
          source: first.source_type,
          md5: first.md5 ? '已生成' : '未生成'
        }
      }
    }
  } catch (_e) {}
}

async function loadJobs() {
  try {
    const data = await fetchJson('/upgrade-jobs')
    if (Array.isArray(data.jobs) && data.jobs[0]) {
      jobsSummary.value = {
        status: data.jobs[0].status,
        target: `v${data.jobs[0].target_version}`,
        api: data.jobs[0].api_check ? '通过' : '失败'
      }
    }
  } catch (_e) {}
}

watch(active, async (val) => {
  if (val === 'dashboard') await loadDashboard()
  if (val === 'network') await loadNetworkSummary()
  if (val === 'upgrade') await loadUpgradeSummary()
  if (val === 'artifacts') await loadArtifacts()
  if (val === 'jobs') await loadJobs()
})

onMounted(async () => {
  await loadDashboard()
})
</script>
