<script setup>
import { ref } from 'vue'
import ContractList from './components/ContractList.vue'
import ContractViewer from './components/ContractViewer.vue'
import AIInteraction from './components/AIInteraction.vue'

// 响应式数据
const selectedContract = ref(null)

// 处理合同选择
const handleContractSelect = (contract) => {
  selectedContract.value = contract
}
</script>

<template>
  <div class="app-container">
    <!-- 左侧合同清单区域 -->
    <div class="left-panel">
      <ContractList @contract-select="handleContractSelect" />
    </div>
    
    <!-- 中间合同展示区域 -->
    <div class="center-panel">
      <ContractViewer :selected-contract="selectedContract" />
    </div>
    
    <!-- 右侧AI交互区域 -->
    <div class="right-panel">
      <AIInteraction :selected-contract="selectedContract" />
    </div>
  </div>
</template>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
  color: #333;
  margin: 0;
  padding: 0;
}

/* 应用容器 */
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
  width: 100vw;
  max-width: 100%;
  margin: 0;
  padding: 0;
}

/* 左侧面板 */
.left-panel {
  width: 280px;
  background-color: #fff;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  flex-shrink: 0;
}

/* 中间面板 */
.center-panel {
  flex: 1;
  background-color: #fff;
  overflow-y: auto;
  min-width: 0;
}

/* 右侧面板 */
.right-panel {
  width: 380px;
  background-color: #fff;
  border-left: 1px solid #e0e0e0;
  overflow-y: auto;
  flex-shrink: 0;
}

/* 状态颜色 */
.status-pending {
  color: #ff9800;
  background-color: #fff3e0;
}

.status-approved {
  color: #4caf50;
  background-color: #e8f5e8;
}

.status-modified {
  color: #2196f3;
  background-color: #e3f2fd;
}

/* 通用样式 */
.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fafafa;
  min-height: 56px;
  box-sizing: border-box;
}

.filter-section {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.filter-group {
  margin-bottom: 12px;
}

.filter-group label {
  display: block;
  margin-bottom: 4px;
  font-size: 14px;
  font-weight: 500;
}

.filter-group select,
.filter-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.contract-item {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.contract-item:hover {
  background-color: #f5f5f5;
}

.contract-item.active {
  background-color: #e3f2fd;
  border-left: 3px solid #2196f3;
}

.contract-item .contract-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.contract-item .contract-meta {
  font-size: 12px;
  color: #666;
  display: flex;
  justify-content: space-between;
}

.contract-item .status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}
</style>
