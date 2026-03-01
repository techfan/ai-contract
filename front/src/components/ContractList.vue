<script setup>
import { ref, onMounted, defineEmits } from 'vue'
import axios from 'axios'

// 定义事件
const emit = defineEmits(['contract-select'])

// 响应式数据
const contracts = ref([])
const filteredContracts = ref([])
const selectedContract = ref(null)

// 筛选条件
const filters = ref({
  status: '',
  contractType: '',
  startDate: '',
  endDate: ''
})

// 合同状态选项
const statusOptions = [
  { value: '', label: '全部状态' },
  { value: '待审核', label: '待审核' },
  { value: '已审核', label: '已审核' },
  { value: '已修改', label: '已修改' }
]

// 合同类型选项
const typeOptions = [
  { value: '', label: '全部类型' },
  { value: '采购', label: '采购' },
  { value: '销售', label: '销售' },
  { value: '服务', label: '服务' },
  { value: '其他', label: '其他' }
]

// 获取合同列表
const fetchContracts = async () => {
  try {
    const params = {}
    
    // 构建查询参数
    if (filters.value.status) {
      params.status = filters.value.status
    }
    if (filters.value.contractType) {
      params.contract_type = filters.value.contractType
    }
    if (filters.value.startDate) {
      params.start_date = filters.value.startDate
    }
    if (filters.value.endDate) {
      params.end_date = filters.value.endDate
    }
    
    const response = await axios.get('http://localhost:8000/api/contracts', { params })
    contracts.value = response.data
    filteredContracts.value = response.data
  } catch (error) {
    console.error('获取合同列表失败:', error)
    // 模拟数据，用于开发测试
    contracts.value = [
      {
        id: 1,
        title: '农副产品买卖合同',
        description: '关于农副产品的采购合同',
        status: '待审核',
        contract_type: '采购',
        created_at: '2026-01-20T08:00:00',
        updated_at: '2026-01-20T08:00:00',
        latest_version: 1
      },
      {
        id: 2,
        title: '委托合同',
        description: '委托服务合同',
        status: '已审核',
        contract_type: '服务',
        created_at: '2026-01-21T09:00:00',
        updated_at: '2026-01-22T10:00:00',
        latest_version: 2
      },
      {
        id: 3,
        title: '建设工程施工合同',
        description: '建筑工程施工协议',
        status: '已修改',
        contract_type: '服务',
        created_at: '2026-01-22T11:00:00',
        updated_at: '2026-01-23T12:00:00',
        latest_version: 3
      },
      {
        id: 4,
        title: '数据融合开发合同',
        description: '数据融合技术开发协议',
        status: '待审核',
        contract_type: '服务',
        created_at: '2026-01-23T13:00:00',
        updated_at: '2026-01-23T13:00:00',
        latest_version: 1
      },
      {
        id: 5,
        title: '研学旅游合同',
        description: '研学旅游服务协议',
        status: '已审核',
        contract_type: '服务',
        created_at: '2026-01-24T14:00:00',
        updated_at: '2026-01-25T15:00:00',
        latest_version: 2
      }
    ]
    filteredContracts.value = contracts.value
  }
}

// 应用筛选
const applyFilters = () => {
  let result = [...contracts.value]
  
  // 状态筛选
  if (filters.value.status) {
    result = result.filter(contract => contract.status === filters.value.status)
  }
  
  // 类型筛选
  if (filters.value.contractType) {
    result = result.filter(contract => contract.contract_type === filters.value.contractType)
  }
  
  // 时间范围筛选
  if (filters.value.startDate) {
    const start = new Date(filters.value.startDate)
    result = result.filter(contract => new Date(contract.created_at) >= start)
  }
  
  if (filters.value.endDate) {
    const end = new Date(filters.value.endDate)
    end.setHours(23, 59, 59, 999)
    result = result.filter(contract => new Date(contract.created_at) <= end)
  }
  
  filteredContracts.value = result
}

// 重置筛选
const resetFilters = () => {
  filters.value = {
    status: '',
    contractType: '',
    startDate: '',
    endDate: ''
  }
  filteredContracts.value = contracts.value
}

// 选择合同
const selectContract = (contract) => {
  selectedContract.value = contract
  // 发送事件通知父组件
  emit('contract-select', contract)
  console.log('选择了合同:', contract)
}

// 获取状态对应的CSS类名
const getStatusClass = (status) => {
  switch (status) {
    case '待审核':
      return 'status-pending'
    case '已审核':
      return 'status-approved'
    case '已修改':
      return 'status-modified'
    default:
      return ''
  }
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 组件挂载时获取合同列表
onMounted(() => {
  fetchContracts()
})
</script>

<template>
  <div class="contract-list">
    <!-- 面板标题 -->
    <div class="panel-title">
      合同清单
    </div>
    
    <!-- 筛选区域 -->
    <div class="filter-section">
      <h3>高级筛选</h3>
      
      <!-- 合同状态筛选 -->
      <div class="filter-group">
        <label for="status">合同状态</label>
        <select 
          id="status" 
          v-model="filters.status"
          @change="applyFilters"
        >
          <option 
            v-for="option in statusOptions" 
            :key="option.value" 
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
      
      <!-- 合同类型筛选 -->
      <div class="filter-group">
        <label for="contractType">合同类型</label>
        <select 
          id="contractType" 
          v-model="filters.contractType"
          @change="applyFilters"
        >
          <option 
            v-for="option in typeOptions" 
            :key="option.value" 
            :value="option.value"
          >
            {{ option.label }}
          </option>
        </select>
      </div>
      
      <!-- 时间范围筛选 -->
      <div class="filter-group">
        <label for="startDate">开始日期</label>
        <input 
          type="date" 
          id="startDate" 
          v-model="filters.startDate"
          @change="applyFilters"
        />
      </div>
      
      <div class="filter-group">
        <label for="endDate">结束日期</label>
        <input 
          type="date" 
          id="endDate" 
          v-model="filters.endDate"
          @change="applyFilters"
        />
      </div>
      
      <!-- 操作按钮 -->
      <div class="filter-actions">
        <button class="btn btn-reset" @click="resetFilters">重置</button>
        <button class="btn btn-refresh" @click="fetchContracts">刷新</button>
      </div>
    </div>
    
    <!-- 合同列表 -->
    <div class="contract-list-content">
      <div 
        v-for="contract in filteredContracts" 
        :key="contract.id"
        class="contract-item"
        :class="{ active: selectedContract && selectedContract.id === contract.id }"
        @click="selectContract(contract)"
      >
        <div class="contract-title">{{ contract.title }}</div>
        <div class="contract-meta">
          <span>{{ contract.contract_type }}</span>
          <span>{{ formatDate(contract.created_at) }}</span>
        </div>
        <div class="contract-footer">
          <span class="status-badge" :class="getStatusClass(contract.status)">
            {{ contract.status }}
          </span>
          <span class="version-info">v{{ contract.latest_version }}</span>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="filteredContracts.length === 0" class="empty-state">
        暂无合同数据
      </div>
    </div>
  </div>
</template>

<style scoped>
.contract-list {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.contract-list-content {
  flex: 1;
  overflow-y: auto;
}

.filter-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f5f5f5;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn:hover {
  background-color: #e0e0e0;
}

.btn-reset {
  flex: 1;
  color: #000;
}

.btn-refresh {
  flex: 1;
  background-color: #2196f3;
  color: white;
  border-color: #2196f3;
}

.btn-refresh:hover {
  background-color: #1976d2;
}

.contract-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
  font-size: 12px;
}

.version-info {
  color: #666;
  background-color: #f0f0f0;
  padding: 2px 6px;
  border-radius: 10px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
}
</style>