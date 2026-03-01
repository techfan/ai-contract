<script setup>
import { ref, onMounted, watch, defineProps, computed } from 'vue'
import axios from 'axios'
import * as diff from 'diff'
import * as Diff2Html from 'diff2html'
import 'diff2html/bundles/css/diff2html.min.css'

// 定义props
const props = defineProps({
  selectedContract: {
    type: Object,
    default: null
  }
})

// 响应式数据
const contract = ref(null)
const selectedVersion = ref(null)
const versions = ref([])
const searchKeyword = ref('')
const searchResults = ref([])
const currentSearchIndex = ref(-1)
const showVersionCompare = ref(false)
const compareVersions = ref({ v1: null, v2: null })
const diffResult = ref(null)
const complianceIssues = ref([])
const onlineUsers = ref([])

// 编辑器引用
const editorRef = ref(null)

// 版本对比相关
const showCompareButton = ref(true)

// 编辑状态管理
const isEditing = ref(false)
const originalContent = ref('')
const editedContent = ref('')
const contractContent = ref('')



// 计算属性：带高亮的合同内容
const highlightedContent = computed(() => {
  if (!contractContent.value || !searchKeyword.value) {
    return contractContent.value
  }
  
  const keyword = searchKeyword.value
  const content = contractContent.value
  
  // 简单的替换，确保每个匹配项都被正确高亮
  const regex = new RegExp(`(${keyword})`, 'gi')
  return content.replace(regex, '<span class="search-highlight">$1</span>')
})

// 模拟合同数据，用于开发测试
const mockContract = {
  id: 1,
  title: '农副产品买卖合同',
  description: '关于农副产品的采购合同',
  status: '待审核',
  contract_type: '采购',
  created_at: '2026-01-20T08:00:00',
  updated_at: '2026-01-20T08:00:00',
  versions: [
    {
      id: 1,
      version: 1,
      created_at: '2026-01-20T08:00:00',
      file_type: 'pdf'
    }
  ]
}

// 模拟合同内容
const mockContractContent = `
第一章 总则

第一条 合同双方
甲方：XXX公司
乙方：XXX农场

第二条 合同目的
为明确甲乙双方权利义务，保障双方合法权益，根据《中华人民共和国合同法》等相关法律法规，经双方协商一致，就农副产品采购事宜订立本合同。

第二章 产品名称、数量、质量标准

第三条 产品名称
本合同所指农副产品为：新鲜蔬菜、水果等。

第四条 产品数量
甲方采购乙方农副产品的数量为：每月不少于1000公斤。

第五条 质量标准
乙方提供的农副产品应符合国家相关质量标准，新鲜、无病虫害、无腐烂变质。

第三章 价格与结算

第六条 产品价格
农副产品的价格由双方根据市场行情协商确定，每公斤不超过10元。

第七条 结算方式
甲方应在收到农副产品后3个工作日内支付货款，支付方式为银行转账。

第四章 交货与验收

第八条 交货地点
乙方应将农副产品运至甲方指定地点：XXX市XXX区XXX路XXX号。

第九条 交货时间
乙方应在每月1日至5日期间交货。

第十条 验收方式
甲方应在收到农副产品后当场验收，如发现质量问题应立即通知乙方。

第五章 违约责任

第十一条 甲方违约责任
甲方如未按合同约定支付货款，每逾期一日，应按未支付金额的0.1%向乙方支付违约金。

第十二条 乙方违约责任
乙方如未按合同约定提供农副产品，每逾期一日，应按合同总金额的0.1%向甲方支付违约金。

第六章 争议解决

第十三条 争议解决方式
本合同履行过程中如发生争议，双方应协商解决；协商不成的，可向有管辖权的人民法院提起诉讼。

第七章 其他条款

第十四条 合同生效
本合同自双方签字盖章之日起生效，有效期为一年。

第十五条 合同份数
本合同一式两份，甲乙双方各执一份，具有同等法律效力。

甲方（盖章）：__________________  
法定代表人（签字）：____________
日期：______年____月____日

乙方（盖章）：__________________  
法定代表人（签字）：____________
日期：______年____月____日
`

// 获取合同详情
const fetchContractDetails = async (contractId) => {
  try {
    const response = await axios.get(`http://localhost:8000/api/contracts/${contractId}`)
    contract.value = response.data
    versions.value = response.data.versions
    if (versions.value.length > 0) {
      selectedVersion.value = versions.value[0]
      fetchVersionContent(contractId, selectedVersion.value.id)
    }
    // 获取合同详情后检查合规性
    checkCompliance()
  } catch (error) {
    console.error('获取合同详情失败:', error)
    // 使用模拟数据
    contract.value = mockContract
    versions.value = mockContract.versions
    selectedVersion.value = mockContract.versions[0]
    // 使用模拟数据后检查合规性
    checkCompliance()
    // 使用模拟合同内容
    contractContent.value = mockContractContent
  }
}

// 获取版本内容（文本形式）
const fetchVersionContent = async (contractId, versionId) => {
  try {
    const response = await axios.get(`http://localhost:8000/api/contracts/${contractId}/versions/${versionId}/content`)
    // 存储版本内容
    contractContent.value = response.data.content
  } catch (error) {
    console.error('获取版本内容失败:', error)
    // 使用模拟数据
    contractContent.value = mockContractContent
  }
}



// 搜索关键字
const searchKeywordInDocument = () => {
  if (!searchKeyword.value) {
    searchResults.value = []
    currentSearchIndex.value = -1
    return
  }
  
  // 实际搜索合同内容
  const results = []
  const content = contractContent.value || ''
  const keyword = searchKeyword.value
  const regex = new RegExp(keyword, 'gi')
  let match
  let position = 1
  
  while ((match = regex.exec(content)) !== null) {
    // 获取匹配上下文
    const start = Math.max(0, match.index - 20)
    const end = Math.min(content.length, match.index + keyword.length + 20)
    const context = content.substring(start, end).replace(/\n/g, ' ')
    
    results.push({
      position: position++,
      text: match[0],
      context: context,
      startIndex: match.index,
      endIndex: match.index + keyword.length
    })
  }
  
  searchResults.value = results
  currentSearchIndex.value = results.length > 0 ? 0 : -1
  
  // 搜索完成，不需要自动滚动到第一个结果
  // 只显示结果数量
}

// 搜索结果不需要导航功能，已移除上一个、下一个按钮

// 章节跳转
const jumpToSection = (section) => {
  console.log('跳转到章节:', section)
  // 实际应用中需要实现章节定位逻辑
}

// 打开版本对比
const openVersionCompare = () => {
  showVersionCompare.value = true
}

// 关闭版本对比
const closeVersionCompare = () => {
  showVersionCompare.value = false
  compareVersions.value = { v1: null, v2: null }
  diffResult.value = null
  // 重置对比按钮显示状态
  showCompareButton.value = true
}

// 字符串差异高亮（突出显示具体差异部分）
const highlightInlineDifferences = (text1, text2, isRemoved) => {
  // 如果文本相同，直接返回
  if (text1 === text2) {
    return text1
  }
  
  // 找出公共前缀
  let prefixLength = 0
  while (prefixLength < text1.length && prefixLength < text2.length && text1[prefixLength] === text2[prefixLength]) {
    prefixLength++
  }
  
  // 找出公共后缀
  let suffixLength = 0
  while (suffixLength < text1.length - prefixLength && suffixLength < text2.length - prefixLength && 
         text1[text1.length - suffixLength - 1] === text2[text2.length - suffixLength - 1]) {
    suffixLength++
  }
  
  const prefix = text1.substring(0, prefixLength)
  const suffix = text1.substring(text1.length - suffixLength)
  
  // 构建结果
  if (isRemoved) {
    // 第一个版本（被删除的内容）
    const removedPart = text1.substring(prefixLength, text1.length - suffixLength)
    return prefix + `<span class="diff-removed">${removedPart}</span>` + suffix
  } else {
    // 第二个版本（新增的内容）
    const addedPart = text2.substring(prefixLength, text2.length - suffixLength)
    return prefix + `<span class="diff-added">${addedPart}</span>` + suffix
  }
}

// 高亮显示差异
const highlightDifferences = (content1, content2) => {
  const lines1 = content1.split('\n')
  const lines2 = content2.split('\n')
  
  let highlighted1 = ''
  let highlighted2 = ''
  
  // 找出最长的行数
  const maxLines = Math.max(lines1.length, lines2.length)
  
  for (let i = 0; i < maxLines; i++) {
    const line1 = lines1[i] || ''
    const line2 = lines2[i] || ''
    
    // 处理第一个版本
    if (i < lines1.length) {
      if (i >= lines2.length || line1 !== line2) {
        highlighted1 += `<div class="diff-line diff-removed">${highlightInlineDifferences(line1, line2, true)}</div>`
      } else {
        highlighted1 += `<div class="diff-line">${line1}</div>`
      }
    }
    
    // 处理第二个版本
    if (i < lines2.length) {
      if (i >= lines1.length || line2 !== line1) {
        highlighted2 += `<div class="diff-line diff-added">${highlightInlineDifferences(line1, line2, false)}</div>`
      } else {
        highlighted2 += `<div class="diff-line">${line2}</div>`
      }
    }
  }
  
  return { highlighted1, highlighted2 }
}

// 生成差异数据
const generateDiffData = (content1, content2) => {
  // 使用jsdiff生成行级差异
  const diffResult = diff.createTwoFilesPatch('version1', 'version2', content1, content2)
  return diffResult
}

// 渲染差异为HTML
const renderDiffHtml = (diffData) => {
  // 使用diff2html将diff数据转换为HTML
  const html = Diff2Html.html(diffData, {
    drawFileList: false,
    matching: 'lines',
    outputFormat: 'side-by-side',
    renderNothingWhenEmpty: true,
    showLineNumbers: false,
    highlight: true,
    fileListToggle: false,
    fileListStartVisible: false,
    fileContentToggle: false,
    // 确保行号完全不生成
    lineNumbers: false,
    // 调整渲染选项以避免滚动问题
    synchronisedScroll: true
  })
  return html
}

// 处理滚动同步
const handleScrollSync = () => {
  // 获取所有差异容器
  const diffWrappers = document.querySelectorAll('.d2h-wrapper')
  
  diffWrappers.forEach(wrapper => {
    // 确保只有一个滚动容器
    const contentContainer = wrapper.querySelector('.d2h-diff-tbody')
    if (contentContainer) {
      // 移除其他可能的滚动容器
      const otherContainers = wrapper.querySelectorAll(':scope > div:not(.d2h-diff-tbody)')
      otherContainers.forEach(container => {
        container.style.overflow = 'visible'
      })
    }
  })
}

// 开始版本对比
const startVersionCompare = async () => {
  if (!compareVersions.value.v1 || !compareVersions.value.v2) {
    alert('请选择两个版本进行对比')
    return
  }
  
  try {
    const response = await axios.get(`http://localhost:8000/api/contracts/${contract.value.id}/compare`, {
      params: {
        version1: compareVersions.value.v1,
        version2: compareVersions.value.v2
      }
    })
    // 生成差异数据
    const diffData = generateDiffData(response.data.content1, response.data.content2)
    // 渲染差异为HTML
    const diffHtml = renderDiffHtml(diffData)
    // 更新对比结果
    diffResult.value = {
      ...response.data,
      diffHtml: diffHtml
    }
  } catch (error) {
    console.error('版本对比失败:', error)
    // 模拟对比结果
    const content1 = mockContractContent
    const content2 = mockContractContent.replace('每月不少于1000公斤', '每月不少于1200公斤')
    // 生成差异数据
    const diffData = generateDiffData(content1, content2)
    // 渲染差异为HTML
    const diffHtml = renderDiffHtml(diffData)
    // 更新对比结果
    diffResult.value = {
      version1: compareVersions.value.v1,
      version2: compareVersions.value.v2,
      content1: content1,
      content2: content2,
      differences: '发现1处差异：\n- 产品数量从"每月不少于1000公斤"修改为"每月不少于1200公斤"',
      diffHtml: diffHtml
    }
  }
  // 隐藏对比按钮
  showCompareButton.value = false
  
  // 延迟处理滚动同步，确保DOM已更新
  setTimeout(() => {
    handleScrollSync()
  }, 100)
}

// 检查合规性
const checkCompliance = async () => {
  try {
    const response = await axios.post(`http://localhost:8000/api/contracts/${contract.value.id}/review`)
    complianceIssues.value = response.data.issues
  } catch (error) {
    console.error('合规性检查失败:', error)
    // 模拟合规性检查结果
    complianceIssues.value = [
      {
        rule_id: 1,
        rule_name: '付款期限检查',
        description: '付款期限应在收到货物后7个工作日内',
        severity: 'warning',
        location: '第三章 价格与结算 第七条'
      },
      {
        rule_id: 2,
        rule_name: '违约金比例检查',
        description: '违约金比例不应超过每日0.05%',
        severity: 'error',
        location: '第五章 违约责任 第十一条'
      }
    ]
  }
}

// 初始化WebSocket连接
const initWebSocket = () => {
  // 实际应用中需要实现WebSocket连接
  console.log('初始化WebSocket连接')
  // 模拟在线用户
  onlineUsers.value = [
    { id: 1, name: '张三', cursorPosition: { line: 10, column: 5 } },
    { id: 2, name: '李四', cursorPosition: { line: 20, column: 10 } }
  ]
}

// 编辑功能
const startEditing = () => {
  isEditing.value = true
  // 确保即使contractContent为空，也有默认值
  const contentToEdit = contractContent.value || mockContractContent
  originalContent.value = contentToEdit
  editedContent.value = contentToEdit
  // 确保contractContent不为空，这样在取消编辑时内容仍然显示
  if (!contractContent.value) {
    contractContent.value = contentToEdit
  }
  // 将内容设置到编辑器中，避免响应式渲染导致的光标问题
  setTimeout(() => {
    if (editorRef.value) {
      editorRef.value.innerHTML = contentToEdit
    }
  }, 0)
}

const saveChanges = async () => {
  try {
    if (contract.value && selectedVersion.value) {
      console.log('保存内容:', editedContent.value)
      // 创建FormData对象
      const formData = new FormData()
      formData.append('content', editedContent.value)
      
      // 调用API保存版本内容到文件
      const response = await axios.post(`http://localhost:8000/api/contracts/${contract.value.id}/versions/${selectedVersion.value.id}/save`, formData)
      console.log('保存成功:', response.data)
      // 更新本地内容
      contractContent.value = editedContent.value
      // 退出编辑状态
      isEditing.value = false
    }
  } catch (error) {
    console.error('保存失败:', error)
    if (error.response) {
      console.error('响应数据:', error.response.data)
      console.error('响应状态:', error.response.status)
      alert(`保存失败: ${error.response.data.detail || '未知错误'}`)
    } else {
      alert('保存失败，请重试')
    }
  }
}

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false
  editedContent.value = originalContent.value
  // 确保contractContent不为空，这样在取消编辑时内容仍然显示
  if (!contractContent.value) {
    contractContent.value = originalContent.value
  }
}



// 处理内容编辑
const handleContentEdit = (event) => {
  // 直接从编辑器中获取内容，避免响应式渲染导致的光标问题
  if (editorRef.value) {
    // 只更新数据，不触发重新渲染
    editedContent.value = editorRef.value.innerText
  }
}

// 重置对比状态
const resetVersionCompare = () => {
  compareVersions.value = { v1: null, v2: null }
  diffResult.value = null
}

// 监听selectedContract变化
watch(() => props.selectedContract, (newContract) => {
  console.log('selectedContract变化:', newContract)
  // 重置搜索状态
  searchKeyword.value = ''
  searchResults.value = []
  currentSearchIndex.value = -1
  
  if (newContract) {
    fetchContractDetails(newContract.id)
  }
}, { immediate: true })

// 组件挂载时初始化
onMounted(() => {
  // 初始化WebSocket
  initWebSocket()
  // 检查合规性将在fetchContractDetails完成后调用
})
</script>

<template>
  <div class="contract-viewer">
    <!-- 面板标题 -->
    <div class="panel-title">
      <h2>{{ contract?.title || '合同查看器' }}</h2>
      <div class="viewer-actions">
        <!-- 非编辑状态显示的按钮 -->
        <button v-if="!isEditing" class="btn btn-primary" @click="startEditing">编辑</button>
        <button class="btn btn-secondary" @click="openVersionCompare">版本对比</button>
        <button class="btn btn-secondary" @click="checkCompliance">合规检查</button>
        
        <!-- 编辑状态显示的按钮 -->
        <button v-if="isEditing" class="btn btn-success" @click="saveChanges">保存</button>
        <button v-if="isEditing" class="btn btn-danger" @click="cancelEditing">取消</button>
      </div>
    </div>
    
    <!-- 搜索和版本选择功能 -->
    <div class="search-section">
      <div class="search-input-group">
        <input 
          type="text" 
          v-model="searchKeyword" 
          placeholder="搜索关键字..."
          class="search-input"
          @input="searchKeywordInDocument"
        />
        <select 
          v-if="versions.length > 0" 
          v-model="selectedVersion" 
          @change="fetchVersionContent(contract.id, selectedVersion.id)"
          class="version-select"
        >
          <option 
            v-for="version in versions" 
            :key="version.id" 
            :value="version"
          >
            v{{ version.version }} ({{ new Date(version.created_at).toLocaleDateString() }})
          </option>
        </select>
      </div>
      <div class="search-results" v-if="searchResults.length > 0">
        <span>找到 {{ searchResults.length }} 个结果</span>
      </div>
    </div>
    
    <!-- 文档内容 -->
    <div class="document-content">
      <!-- 编辑状态 -->
      <div v-if="isEditing" class="edit-mode">
        <div 
          contenteditable="true"
          class="content-editor"
          ref="editorRef"
          @input="handleContentEdit"
        ></div>
      </div>
      
      <!-- 查看状态 -->
      <div v-else class="view-mode">
        <div class="content-display" v-html="highlightedContent || '请选择一个合同查看内容'"> </div>
      </div>
    </div>
    
    <!-- 版本对比弹窗 -->
    <div v-if="showVersionCompare" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <button class="btn btn-close" @click="closeVersionCompare">×</button>
        </div>
        <div class="modal-body">
          <div class="version-selector-group">
            <div>
              <label for="version1">版本 1：</label>
              <select id="version1" v-model="compareVersions.v1">
                <option 
                  v-for="version in versions" 
                  :key="version.version" 
                  :value="version.version"
                >
                  v{{ version.version }}
                </option>
              </select>
            </div>
            <div>
              <label for="version2">版本 2：</label>
              <select id="version2" v-model="compareVersions.v2">
                <option 
                  v-for="version in versions" 
                  :key="version.version" 
                  :value="version.version"
                >
                  v{{ version.version }}
                </option>
              </select>
            </div>
          </div>
          <button 
            v-if="showCompareButton" 
            class="btn btn-primary" 
            @click="startVersionCompare"
            :disabled="!compareVersions.v1 || !compareVersions.v2"
          >
            开始对比
          </button>
          
          <!-- 对比结果 -->
          <div v-if="diffResult" class="diff-result">
            <h4>对比结果</h4>
            <div class="diff-content">
              <div class="diff2html-container" v-html="diffResult.diffHtml"></div>
            </div>
            
          </div>
        </div>
      </div>
    </div>
    
    <!-- 文件预览弹窗 -->
    <div v-if="isFilePreview" class="modal-overlay">
      <div class="modal-content modal-content-large">
        <div class="modal-header">
          <h3>文件预览</h3>
          <button class="btn btn-close" @click="closeFilePreview">×</button>
        </div>
        <div class="modal-body">
          <!-- PDF预览 -->
          <div v-if="currentFileType.includes('pdf')" class="file-preview">
            <iframe :src="currentFileUrl" class="pdf-preview" title="PDF Preview"></iframe>
          </div>
          <!-- Word预览 -->
          <div v-else-if="currentFileType.includes('word') || currentFileType.includes('doc')" class="file-preview">
            <div class="word-preview">
              <p>Word文件预览</p>
              <a :href="currentFileUrl" target="_blank" class="btn btn-primary">在新窗口打开</a>
            </div>
          </div>
          <!-- 其他文件类型 -->
          <div v-else class="file-preview">
            <div class="other-preview">
              <p>不支持的文件类型</p>
              <a :href="currentFileUrl" target="_blank" class="btn btn-primary">下载文件</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.contract-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fafafa;
  min-height: 56px;
  box-sizing: border-box;
}

.panel-title h2 {
  font-size: 18px;
  font-weight: bold;
  margin: 0;
}

.viewer-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
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

.btn-primary {
  background-color: #2196f3;
  color: white;
  border-color: #2196f3;
}

.btn-primary:hover {
  background-color: #1976d2;
}

.btn-secondary {
  background-color: #4caf50;
  color: white;
  border-color: #4caf50;
}

.btn-secondary:hover {
  background-color: #388e3c;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.btn-close:hover {
  color: #333;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}



.btn-nav {
  background-color: #2196f3;
  color: white;
  border-color: #2196f3;
}

.btn-nav:hover {
  background-color: #1976d2;
}

.btn-search {
  background-color: #2196f3;
  color: white;
  border-color: #2196f3;
}



.search-section {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f9f9f9;
}

.search-input-group {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.search-input {
  width: 50%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 200px;
}

.version-select {
  padding: 8px 12px;
  border: 1px solid #333;
  border-radius: 4px;
  font-size: 14px;
  background-color: #000;
  color: #fff;
  cursor: pointer;
  min-width: 150px;
  text-align: right;
}

.version-select:hover {
  border-color: #2196f3;
  background-color: #333;
}

.version-select:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.3);
}

.search-results {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #666;
}

.document-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  position: relative;
}

.document-content .content-display {
  white-space: pre-wrap;
  font-family: Arial, sans-serif;
  line-height: 1.6;
  font-size: 14px;
}

/* Global style for search highlighting */
:global(.search-highlight) {
  background-color: #ffff00;
  color: #000000;
  padding: 0 2px;
  border-radius: 2px;
  font-weight: bold;
}

.compliance-issues {
  margin-top: 20px;
  padding: 16px;
  background-color: #fff3e0;
  border-radius: 4px;
}

.compliance-issues h3 {
  margin-bottom: 12px;
  color: #ff9800;
}

.compliance-issues ul {
  list-style: none;
  padding: 0;
}

.compliance-issues li {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 4px;
  background-color: white;
  border-left: 4px solid #ff9800;
}

.issue-error {
  border-left-color: #f44336 !important;
}

.issue-warning {
  border-left-color: #ff9800 !important;
}

.issue-info {
  border-left-color: #2196f3 !important;
}

.issue-location {
  font-size: 12px;
  color: #666;
  background-color: #f0f0f0;
  padding: 2px 6px;
  border-radius: 10px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 4px;
  width: 80%;
  max-width: 1000px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 8px 16px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fafafa;
  min-height: 32px;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
}

.modal-body {
  padding: 20px;
}

.version-selector-group {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.version-selector-group div {
  flex: 1;
}

.version-selector-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
}

.version-selector-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.diff-result {
  margin-top: 20px;
  border-top: 1px solid #e0e0e0;
  padding-top: 20px;
}

.diff-content {
  margin-bottom: 20px;
  overflow: auto;
  max-height: 500px;
  /* 允许水平和垂直滚动 */
  /* 确保是唯一的滚动容器 */
  position: relative;
  width: 100%;
  /* 确保水平滚动条始终可见 */
  overflow-x: auto;
  overflow-y: auto;
}

/* 确保diff2html容器可以根据内容宽度调整 */
:deep(.diff2html-container) {
  width: auto;
  min-width: 100%;
  height: 100%;
  overflow: visible;
}

/* 确保差异表格有正确的滚动行为 */
:deep(.d2h-files-diff) {
  overflow: visible;
}

:deep(.d2h-wrapper) {
  font-family: Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  border: none;
}

:deep(.d2h-diff-tbody) {
  font-family: Arial, sans-serif;
}

/* 隐藏行号 */
:deep(.d2h-linenumber) {
  display: none !important;
  width: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* 确保所有行号相关元素都隐藏 */
:deep(.d2h-left-linenumber),
:deep(.d2h-right-linenumber),
:deep(.d2h-code-linenumber),
:deep(.d2h-linenumber-wrapper) {
  display: none !important;
  width: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* 确保差异容器有统一的滚动行为 */
:deep(.d2h-wrapper) {
  overflow: visible !important;
  position: relative;
  width: auto !important;
  min-width: 100% !important;
  /* 确保内容可以自由扩展 */
  display: block;
}

:deep(.d2h-diff-container) {
  overflow: visible !important;
}

:deep(.d2h-diff-content) {
  overflow: visible !important;
}

/* 确保差异表格可以根据内容宽度调整 */
:deep(.d2h-diff-table) {
  width: auto !important;
  min-width: 100% !important;
  table-layout: auto !important;
}

/* 调整列宽，确保内容区域合理分配 */
:deep(.d2h-diff-col) {
  width: auto !important;
  min-width: 300px !important;
  max-width: none !important;
}

/* 确保内容单元格可以根据内容宽度调整 */
:deep(.d2h-code-wrapper) {
  width: auto !important;
  min-width: 100% !important;
  overflow: visible !important;
  white-space: nowrap;
}

/* 确保代码行可以根据内容宽度调整 */
:deep(.d2h-code-line) {
  width: auto !important;
  min-width: 100% !important;
  white-space: pre !important;
  word-wrap: normal !important;
  overflow: visible !important;
}

/* 调整差异块样式 */
:deep(.d2h-diff-table) {
  width: 100%;
  border-collapse: collapse;
  font-family: Arial, sans-serif;
}

:deep(.d2h-files-diff) {
  border: none;
}

:deep(.d2h-file-header) {
  display: none;
}

:deep(.d2h-diff-tbody tr) {
  border-bottom: 1px solid #f0f0f0;
}

:deep(.d2h-diff-tbody td) {
  padding: 8px 12px;
  vertical-align: top;
}

/* 调整差异内容样式 */
:deep(.d2h-code-line) {
  font-family: Arial, sans-serif;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 调整新增和删除行的样式 */
:deep(.d2h-ins) {
  background-color: #e6ffed;
  color: #22863a;
  border-left: 3px solid #28a745;
}

:deep(.d2h-del) {
  background-color: #ffeef0;
  color: #cb2431;
  border-left: 3px solid #dc3545;
}

/* 调整并排显示的列宽 */
:deep(.d2h-diff-col) {
  width: 50%;
}

:deep(.d2h-diff-col:nth-child(1)) {
  border-right: 1px solid #f0f0f0;
}

/* 确保内容正确换行 */
:deep(.d2h-content-wrapper) {
  width: 100%;
  overflow: hidden;
}

.diff-side {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
  max-height: 400px;
  overflow-y: auto;
}

.diff-side h5 {
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: bold;
  color: #666;
}

.diff-side {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
  max-height: 400px;
  overflow-y: auto;
}

.diff-side h5 {
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: bold;
  color: #666;
}

.diff-display {
  white-space: pre-wrap;
  font-family: Arial, sans-serif;
  line-height: 1.4;
  font-size: 13px;
}

.diff-removed {
  background-color: #ffebee;
  color: #c62828;
  padding: 4px 6px;
  border-radius: 3px;
  margin: 2px 0;
  border-left: 3px solid #f44336;
  display: block;
}

.diff-added {
  background-color: #e8f5e8;
  color: #2e7d32;
  padding: 4px 6px;
  border-radius: 3px;
  margin: 2px 0;
  border-left: 3px solid #4caf50;
  display: block;
}

/* 行内差异样式 */
.diff-removed {
  background-color: #ffcdd2;
  color: #c62828;
  padding: 1px 3px;
  border-radius: 2px;
  margin: 0 1px;
}

.diff-added {
  background-color: #c8e6c9;
  color: #2e7d32;
  padding: 1px 3px;
  border-radius: 2px;
  margin: 0 1px;
}

.diff-summary {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.diff-summary h5 {
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: bold;
  color: #666;
}

  /* 编辑模式样式 */
  .edit-mode {
    height: 100%;
  }

  .content-editor {
    width: 100%;
    min-height: 400px;
    padding: 16px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: Arial, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    white-space: pre-wrap;
    word-wrap: break-word;
    background-color: #fff;
  }

  .content-editor:focus {
    outline: none;
    border-color: #2196f3;
    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
  }

  /* 查看模式样式 */
  .view-mode {
    height: 100%;
  }

  .btn-success {
    background-color: #4caf50;
    color: white;
    border-color: #4caf50;
  }

  .btn-success:hover {
    background-color: #388e3c;
  }

  .btn-danger {
    background-color: #f44336;
    color: white;
    border-color: #f44336;
  }

  .btn-danger:hover {
    background-color: #d32f2f;
  }
</style>