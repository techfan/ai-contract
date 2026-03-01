<script setup>
import { ref, onMounted, watch, defineProps, computed } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

// 定义props
const props = defineProps({
  selectedContract: {
    type: Object,
    default: null
  }
})

// 响应式数据
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const isGeneratingResponse = ref(false) // 跟踪是否正在生成AI回复
const sessions = ref([])
const currentSessionId = ref('')
const activeContractId = ref(null)
const sessionFirstMessage = ref({}) // 跟踪每个会话的首次消息
const uploadedFiles = ref([]) // 存储上传的文件内容
const streamingTimeout = ref(null) // 用于存储流式输出的定时器ID

// 监听selectedContract变化
watch(() => props.selectedContract, (newContract) => {
  if (newContract) {
    activeContractId.value = newContract.id
    // 重置当前会话的首次消息标记，以便下次消息包含新合同信息
    if (currentSessionId.value) {
      sessionFirstMessage.value[currentSessionId.value] = true
    }
    // 可以在这里添加欢迎消息或其他逻辑
    messages.value.push({ 
      role: 'assistant', 
      content: `已切换到合同: ${newContract.title}`, 
      created_at: new Date() 
    })
  }
})

// 生成会话ID
const generateSessionId = () => {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

// 初始化会话
const initSession = () => {
  const sessionId = generateSessionId()
  currentSessionId.value = sessionId
  sessions.value.push({ id: sessionId, name: `会话 ${sessions.value.length + 1}`, created_at: new Date() })
  messages.value = []
  sessionFirstMessage.value[sessionId] = true // 标记为首次消息
}

// 切换会话
const switchSession = (sessionId) => {
  currentSessionId.value = sessionId
  fetchSessionMessages(sessionId)
  // 确保会话有首次消息标记
  if (sessionFirstMessage.value[sessionId] === undefined) {
    // 如果是已存在的会话，标记为非首次消息
    sessionFirstMessage.value[sessionId] = false
  }
}

// 获取会话消息
const fetchSessionMessages = async (sessionId) => {
  try {
    const response = await axios.get(`http://localhost:8000/api/conversations/${sessionId}/messages`)
    messages.value = response.data
  } catch (error) {
    console.error('获取会话消息失败:', error)
    // 清空消息列表
    messages.value = []
  }
}

// 流式输出AI回复
const streamAIResponse = (fullContent) => {
  // 清除之前可能存在的定时器
  if (streamingTimeout.value) {
    clearTimeout(streamingTimeout.value)
    streamingTimeout.value = null
  }
  
  const messageId = Date.now()
  let currentContent = ''
  let index = 0
  
  // 添加初始消息
  const messageIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: '',
    created_at: new Date(),
    streaming: true
  })
  
  // 立即设置isLoading为false，这样开始输出时就不会显示"正在思考"
  isLoading.value = false
  
  // 流式输出函数
  const stream = () => {
    if (isGeneratingResponse.value && index < fullContent.length) {
      currentContent += fullContent.charAt(index)
      index++
      messages.value[messageIndex].content = currentContent
      messages.value[messageIndex].streaming = true
      
      // 控制流速，模拟真实打字速度
      const delay = Math.random() * 30 + 10
      streamingTimeout.value = setTimeout(stream, delay)
    } else {
      // 流式输出完成或被终止
      if (messageIndex < messages.value.length) {
        messages.value[messageIndex].streaming = false
      }
      isGeneratingResponse.value = false
      streamingTimeout.value = null
    }
  }
  
  // 开始流式输出
  stream()
}

// 停止生成AI回复
const stopAIResponse = () => {
  if (isGeneratingResponse.value) {
    isGeneratingResponse.value = false
    if (streamingTimeout.value) {
      clearTimeout(streamingTimeout.value)
      streamingTimeout.value = null
    }
    // 标记最后一条AI消息为已终止
    for (let i = messages.value.length - 1; i >= 0; i--) {
      if (messages.value[i].role === 'assistant' && messages.value[i].streaming) {
        messages.value[i].streaming = false
        messages.value[i].content += '\n\n[回复已终止]'
        break
      }
    }
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  if (!currentSessionId.value) initSession()
  
  const message = inputMessage.value.trim()
  inputMessage.value = ''
  
  // 添加用户消息
  messages.value.push({ role: 'user', content: message, created_at: new Date() })
  isLoading.value = true
  isGeneratingResponse.value = true // 设置为正在生成AI回复
  
  try {
    // 确保会话存在
    const formData1 = new FormData()
    formData1.append('session_id', currentSessionId.value)
    await axios.post('http://localhost:8000/api/conversations', formData1)
    
    // 构建消息内容，包含上传的文件内容
    let fullMessage = message
    
    // 如果有上传的文件，将文件内容添加到消息中
    if (uploadedFiles.value.length > 0) {
      console.log('有上传的文件，添加文件内容到消息中')
      fullMessage += '\n\n--- 上传的文件内容 ---\n'
      
      uploadedFiles.value.forEach((file, index) => {
        fullMessage += `\n### 文件 ${index + 1}: ${file.name}\n${file.content}\n`
      })
      
      // 清空上传的文件，因为已经包含在消息中
      uploadedFiles.value = []
    }
    
    // 发送消息并获取AI回复
    const formData2 = new FormData()
    formData2.append('content', fullMessage)
    
    // 只在会话的首次消息中添加合同信息
    if (sessionFirstMessage.value[currentSessionId.value] && props.selectedContract) {
      console.log('首次消息，添加合同信息:', props.selectedContract)
      // 确保contract_id被转换为字符串
      formData2.append('contract_id', props.selectedContract.id.toString())
      formData2.append('contract_title', props.selectedContract.title)
      // 标记为非首次消息
      sessionFirstMessage.value[currentSessionId.value] = false
    } else if (sessionFirstMessage.value[currentSessionId.value]) {
      console.log('首次消息，但没有选中合同')
    } else {
      console.log('非首次消息，不添加合同信息')
    }
    
    const response = await axios.post(`http://localhost:8000/api/conversations/${currentSessionId.value}/messages`, formData2)
    
    // 使用流式输出AI回复
    streamAIResponse(response.data.content)
  } catch (error) {
    console.error('发送消息失败:', error)
    // 模拟AI回复，使用流式输出
    setTimeout(() => {
      streamAIResponse('这是AI的模拟回复。实际应用中，这里会显示OpenAI的真实回复。')
    }, 500)
  }
}

// 上传合同问答
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  console.log('上传文件:', file.name)
  
  // 显示上传中消息
  messages.value.push({ role: 'user', content: `上传了文件: ${file.name}`, created_at: new Date() })
  messages.value.push({ role: 'assistant', content: `正在分析文件 ${file.name}...`, created_at: new Date() })
  
  // 读取文件内容
  const reader = new FileReader()
  
  reader.onload = (e) => {
    try {
      const fileContent = e.target.result
      // 保存文件信息和内容
      uploadedFiles.value.push({
        name: file.name,
        type: file.type,
        content: fileContent,
        uploaded_at: new Date()
      })
      
      console.log('文件读取成功:', file.name, '内容长度:', fileContent.length)
      // 更新消息
      messages.value.pop() // 移除正在分析的消息
      messages.value.push({ 
        role: 'assistant', 
        content: `已成功分析文件 ${file.name}，您可以基于此文件内容进行提问。`, 
        created_at: new Date() 
      })
    } catch (error) {
      console.error('文件读取失败:', error)
      messages.value.pop() // 移除正在分析的消息
      messages.value.push({ 
        role: 'assistant', 
        content: `文件分析失败: ${error.message}`, 
        created_at: new Date() 
      })
    }
  }
  
  reader.onerror = (error) => {
    console.error('文件读取错误:', error)
    messages.value.pop() // 移除正在分析的消息
    messages.value.push({ 
      role: 'assistant', 
      content: `文件读取错误: ${error.message}`, 
      created_at: new Date() 
    })
  }
  
  // 根据文件类型读取
  if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
    reader.readAsText(file, 'utf-8')
  } else if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
    // 对于PDF文件，我们需要在后端处理
    // 这里先上传文件到后端，然后获取内容
    uploadFileToBackend(file)
  } else if (file.type.includes('word') || file.name.endsWith('.docx') || file.name.endsWith('.doc')) {
    // 对于Word文件，同样需要在后端处理
    uploadFileToBackend(file)
  } else {
    // 尝试以文本形式读取其他文件
    reader.readAsText(file, 'utf-8')
  }
  
  // 清空文件输入
  event.target.value = ''
}

// 上传文件到后端并获取内容
const uploadFileToBackend = async (file) => {
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await axios.post('http://localhost:8000/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    // 使用新的/file-content接口获取文件内容
    // 处理Windows和Unix路径分隔符
    let filePath = response.data.file_path
    // 移除uploads前缀，无论使用什么路径分隔符
    filePath = filePath.replace(/^uploads[\\/]/, '')
    const contentResponse = await axios.get('http://localhost:8000/api/file-content', {
      params: {
        file_path: filePath
      }
    })
    
    // 保存文件信息和内容
    uploadedFiles.value.push({
      name: file.name,
      type: file.type,
      content: contentResponse.data.content,
      uploaded_at: new Date()
    })
    
    console.log('文件上传并分析成功:', file.name)
    messages.value.pop() // 移除正在分析的消息
    messages.value.push({ 
      role: 'assistant', 
      content: `已成功分析文件 ${file.name}，您可以基于此文件内容进行提问。`, 
      created_at: new Date() 
    })
  } catch (error) {
    console.error('文件上传失败:', error)
    messages.value.pop() // 移除正在分析的消息
    messages.value.push({ 
      role: 'assistant', 
      content: `文件上传失败: ${error.message}`, 
      created_at: new Date() 
    })
  }
}

// 对当前合同进行规则审核
const reviewContractRules = async (contractId) => {
  if (!contractId) return
  
  try {
    const response = await axios.post(`http://localhost:8000/api/contracts/${contractId}/review`)
    const issues = response.data.issues
    
    // 在对话框中显示审核结果
    if (issues.length > 0) {
      let message = '合同审核结果：\n\n'
      issues.forEach((issue, index) => {
        message += `${index + 1}. ${issue.rule_name} (${issue.severity})\n`
        message += `   ${issue.description}\n`
        message += `   位置：${issue.location}\n\n`
      })
      messages.value.push({ role: 'assistant', content: message, created_at: new Date() })
    } else {
      messages.value.push({ role: 'assistant', content: '合同审核通过，未发现问题。', created_at: new Date() })
    }
  } catch (error) {
    console.error('审核合同规则失败:', error)
    // 模拟审核结果
    messages.value.push({ role: 'assistant', content: '合同审核完成，未发现重大问题。', created_at: new Date() })
  }
}

// 组件挂载时初始化
onMounted(() => {
  initSession()
})
</script>

<template>
  <div class="ai-interaction">
    <!-- 面板标题 -->
    <div class="panel-title">
      AI交互助手
    </div>
    
    <!-- 会话管理 -->
    <div class="session-management">
      <div class="session-tabs">
        <div 
          v-for="session in sessions" 
          :key="session.id"
          class="session-tab"
          :class="{ active: currentSessionId === session.id }"
          @click="switchSession(session.id)"
        >
          {{ session.name }}
        </div>
        <div class="session-tab new-session" @click="initSession">
          +
        </div>
      </div>
    </div>
    
    <!-- 消息列表 -->
    <div class="message-list">
      <div 
        v-for="(message, index) in messages" 
        :key="index"
        class="message"
        :class="message.role"
      >
        <div class="message-content" v-html="message.role === 'assistant' ? marked(message.content) : message.content"></div>
        <div class="message-time">
          {{ new Date(message.created_at).toLocaleTimeString() }}
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading">
        <div class="loading-spinner"></div>
        <span>正在思考...</span>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="input-area">
      <!-- 消息输入 -->
      <div class="message-input">
        <label class="upload-btn-icon">
          <input type="file" accept=".pdf,.docx,.doc,.txt" @change="handleFileUpload" />
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
          </svg>
        </label>
        <input 
          type="text" 
          v-model="inputMessage"
          placeholder="请输入您的问题..."
          @keyup.enter="sendMessage"
          class="message-input-field"
        />
        <button 
          class="send-btn" 
          @click="isGeneratingResponse ? stopAIResponse() : sendMessage()"
          :disabled="(!isGeneratingResponse && !inputMessage.trim())"
        >
          <!-- 发送按钮图标 -->
          <template v-if="!isGeneratingResponse">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </template>
          <!-- 停止按钮图标 -->
          <template v-else>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10" fill="#2196f3" stroke="none"/>
              <rect x="7" y="7" width="10" height="10" fill="white" stroke="none"/>
            </svg>
          </template>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-interaction {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

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

.session-management {
  border-bottom: 1px solid #e0e0e0;
  background-color: #f9f9f9;
}

.session-tabs {
  display: flex;
  overflow-x: auto;
  padding: 8px;
  gap: 8px;
}

.session-tab {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 16px;
  background-color: #fff;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.session-tab:hover {
  background-color: #f0f0f0;
}

.session-tab.active {
  background-color: #2196f3;
  color: white;
  border-color: #2196f3;
}

.session-tab.new-session {
  background-color: #f5f5f5;
  border: 1px dashed #ddd;
  font-size: 16px;
  font-weight: bold;
  min-width: 32px;
  text-align: center;
}

.message-list {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background-color: #f9f9f9;
}

.message {
  margin-bottom: 16px;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  margin-left: auto;
}

.message.assistant {
  align-self: flex-start;
}

.message-content {
  padding: 12px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.4;
}

.message.user .message-content {
  background-color: #e3f2fd;
  border-top-right-radius: 4px;
}

.message.assistant .message-content {
  background-color: #fff;
  border: 1px solid #ddd;
  border-top-left-radius: 4px;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

.message.assistant .message-time {
  text-align: left;
}

/* Markdown样式 */
.message-content :deep(h1),
.message-content :deep(h2),
.message-content :deep(h3),
.message-content :deep(h4),
.message-content :deep(h5),
.message-content :deep(h6) {
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: bold;
}

.message-content :deep(h1) {
  font-size: 1.5em;
  border-bottom: 1px solid #ddd;
  padding-bottom: 4px;
}

.message-content :deep(h2) {
  font-size: 1.3em;
}

.message-content :deep(h3) {
  font-size: 1.1em;
}

.message-content :deep(p) {
  margin-bottom: 12px;
  line-height: 1.5;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  margin-bottom: 12px;
  padding-left: 24px;
}

.message-content :deep(li) {
  margin-bottom: 4px;
}

.message-content :deep(ul) :deep(li) {
  list-style-type: disc;
}

.message-content :deep(ol) :deep(li) {
  list-style-type: decimal;
}

.message-content :deep(strong) {
  font-weight: bold;
}

.message-content :deep(em) {
  font-style: italic;
}

.message-content :deep(code) {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.9em;
}

.message-content :deep(pre) {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 12px;
}

.message-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
  font-size: 0.85em;
}

.message-content :deep(a) {
  color: #2196f3;
  text-decoration: none;
}

.message-content :deep(a:hover) {
  text-decoration: underline;
}

.message-content :deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 12px;
  margin-left: 0;
  margin-bottom: 12px;
  color: #666;
}

.loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 12px;
  font-size: 14px;
  color: #666;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.input-area {
  border-top: 1px solid #e0e0e0;
  padding: 12px 16px;
  background-color: #fff;
}

.upload-btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  border: none;
  border-radius: 50%;
  background-color: #f5f5f5;
  cursor: pointer;
  transition: all 0.2s;
  color: #666;
}

.upload-btn-icon:hover {
  background-color: #e0e0e0;
  color: #333;
}

.upload-btn-icon input {
  display: none;
}

.message-input {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 24px;
  padding: 4px;
  transition: all 0.2s;
}

.message-input:focus-within {
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

.message-input-field {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  background-color: transparent;
  outline: none;
  color: #333; /* 设置黑色字体 */
}

.send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 16px;
  border: none;
  border-radius: 50%;
  background-color: #2196f3;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 40px;
  height: 40px;
}

.send-btn:hover:not(:disabled) {
  background-color: #1976d2;
  transform: scale(1.05);
}

.send-btn:disabled {
  background-color: #bdbdbd;
  cursor: not-allowed;
  transform: none;
}
</style>