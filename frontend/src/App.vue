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
          <div class="grid">
            <div class="card" v-for="n in 4" :key="n">指标卡 {{ n }}</div>
          </div>
        </main>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
const view = ref<'login' | 'dashboard'>('login')
const active = ref('dashboard')
const bannerTitle = computed(() => ({
  dashboard: '欢迎，admin',
  network: '网络配置',
  upgrade: '固件升级',
  diagnostics: '运行诊断',
  artifacts: '固件制品管理',
  jobs: '升级任务'
}[active.value] ?? '控制台'))
</script>
