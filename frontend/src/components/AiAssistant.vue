<template>
  <!-- AI助手浮动按钮（可拖动） -->
  <div
    v-if="projectInfo && projectInfo.id"
    class="ai-assistant-fab"
    :class="{ dragging: isDragging }"
    :style="fabStyle"
    @mousedown="onFabMouseDown"
    @click="onFabClick"
  >
    <el-icon class="ai-fab-icon"><MagicStick /></el-icon>
    <span class="ai-fab-pulse"></span>
  </div>

  <!-- AI全屏对话弹窗 -->
  <el-dialog v-model="aiChatVisible" :close-on-click-modal="false" fullscreen class="ai-chat-dialog" destroy-on-close @open="adjustChatHeight" append-to-body>
    <template #header>
      <div class="ai-dialog-header">
        <span class="ai-header-title">AI助手</span>
        <el-popover
          v-model:visible="aiModelPopoverVisible"
          trigger="click"
          placement="right-start"
          :width="280"
          popper-class="ai-model-popover"
          :popper-options="{ modifiers: [{ name: 'flip', enabled: false }] }"
        >
          <template #reference>
            <span class="ai-model-name">
              {{ currentModelName || '选择模型' }}
              <el-icon class="ai-model-arrow" :class="{ open: aiModelPopoverVisible }"><ArrowDown /></el-icon>
            </span>
          </template>
          <template #default>
            <div class="ai-model-list">
              <div
                v-for="c in ai_config_list"
                :key="c.id"
                class="ai-model-list-item"
                :class="{ active: c.id === aiChatConfigId }"
                @click="selectModel(c.id)"
              >
                <div class="ai-model-list-name">{{ c.name }}</div>
                <div class="ai-model-list-desc">{{ c.model_name }}</div>
                <el-icon v-if="c.id === aiChatConfigId" class="ai-model-check"><Select /></el-icon>
              </div>
              <div v-if="!ai_config_list.length" class="ai-model-list-empty">暂无可用模型</div>
            </div>
          </template>
        </el-popover>
      </div>
    </template>
    <div class="ai-chat-layout" ref="aiChatLayoutRef">
      <!-- 左侧会话列表 -->
      <div class="ai-chat-sidebar">
        <div class="ai-sidebar-header">
          <div class="ai-new-chat-btn" @click="newConversation">
            <el-icon class="ai-new-chat-icon"><Plus /></el-icon>
            <span>开启新对话</span>
          </div>
        </div>
        <div class="ai-conversation-list" @scroll="onConversationScroll">
          <div
            v-for="conv in conversation_list"
            :key="conv.id"
            class="ai-conversation-item"
            :class="{ active: conv.id === currentConversationId }"
            @click="selectConversation(conv.id)"
          >
            <div class="ai-conv-item-main">
              <div class="ai-conv-title" @dblclick.stop="renameConversation(conv)">{{ conv.title }}</div>
              <div class="ai-conv-meta">{{ conv.update_time }}</div>
            </div>
            <el-icon class="ai-conv-action" @click.stop="renameConversation(conv)"><Edit /></el-icon>
            <el-icon class="ai-conv-delete" @click.stop="deleteConversation(conv.id)"><Delete /></el-icon>
          </div>
          <div v-if="!conversation_list.length" class="ai-empty-conversation">
            暂无对话记录
          </div>
          <div v-else-if="conv_loading" class="ai-conv-loadmore">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
          <div v-else-if="!conv_has_more && conversation_list.length >= conv_size" class="ai-conv-loadmore end">
            —— 已经到底啦 ——
          </div>
        </div>
      </div>

      <!-- 右侧对话区 -->
      <div class="ai-chat-main" :class="{ 'no-messages': !chatMessages.length && !aiStreaming }">
        <div class="ai-chat-messages" ref="chatMessagesRef">
          <div v-if="!chatMessages.length" class="ai-chat-welcome">
            <el-icon :size="48" color="#8b5cf6"><MagicStick /></el-icon>
            <h3>AI助手</h3>
            <div class="ai-welcome-options">
              <div class="ai-welcome-option" :class="{ active: chatMode === 'generate' }" @click="selectMode('generate')">
                <el-icon class="ai-welcome-option-icon"><Document /></el-icon>
                <span class="ai-welcome-option-text">AI生成功能测试用例</span>
              </div>
              <div class="ai-welcome-option" :class="{ active: chatMode === 'assistant' }" @click="selectMode('assistant')">
                <el-icon class="ai-welcome-option-icon"><ChatDotRound /></el-icon>
                <span class="ai-welcome-option-text">AI助手</span>
              </div>
            </div>
          </div>

          <div v-for="msg in chatMessages" :key="msg.id" class="ai-message" :class="msg.role">
            <div class="ai-message-header">
              <div class="ai-message-avatar">
                <el-avatar v-if="msg.role === 'user'" :size="32" :style="{background: 'linear-gradient(135deg, #0ea5e9, #0284c7)', color: '#fff', fontWeight: 600, fontSize: 14}">
                  {{ (userInfo.user_name || 'U').toString().charAt(0).toUpperCase() }}
                </el-avatar>
                <el-icon v-else-if="msg.is_task && (msg.task_status === 'pending' || msg.task_status === 'running')" :size="20" color="#8b5cf6" class="is-loading"><Loading /></el-icon>
                <el-icon v-else :size="20" color="#8b5cf6"><MagicStick /></el-icon>
              </div>
              <span class="ai-message-name">
                {{ msg.role === 'user' ? (userInfo.user_name || '用户') : 'AI助手' }}
              </span>
            </div>
            <div class="ai-message-body">
              <div class="ai-message-content" :class="{ 'ai-task-success': msg.is_task && msg.task_status === 'success', 'ai-task-failed': msg.is_task && msg.task_status === 'failed' }" v-html="renderMarkdown(msg.content)"></div>
              <div class="ai-message-actions">
                <el-tooltip :content="msg.copied ? '已复制' : '复制'" placement="top" effect="dark">
                  <el-button link type="primary" size="small" class="ai-copy-btn" @click="copyMsgContent(msg)">
                    <el-icon :size="14"><Check v-if="msg.copied" /><CopyDocument v-else /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
              <div v-if="msg.cases_data && msg.cases_data.length" class="ai-message-cases">
                <div class="ai-cases-header">
                  <span>{{ msg.is_task ? `已生成 ${msg.cases_data.length} 条用例（已自动保存）` : `AI生成了 ${msg.cases_data.length} 条用例` }}</span>
                  <el-button v-if="!msg.is_task" type="primary" size="small" @click="saveCases(msg)" :loading="msg.saving">
                    保存用例
                  </el-button>
                </div>
                <div class="ai-cases-preview">
                  <div v-for="(c, i) in msg.cases_data" :key="i" class="ai-case-preview-item">
                    <span class="ai-case-num">{{ i + 1 }}</span>
                    <span class="ai-case-preview-name">{{ c.name }}</span>
                    <span class="ai-case-steps">{{ c.step_table?.length || 0 }} 步</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="aiStreaming" class="ai-message assistant">
            <div class="ai-message-header">
              <div class="ai-message-avatar">
                <el-icon :size="20" color="#8b5cf6" class="is-loading"><Loading /></el-icon>
              </div>
              <span class="ai-message-name">AI助手</span>
            </div>
            <div class="ai-message-body">
              <div v-if="streamingStatus && !streamingContent" class="ai-streaming-status">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>{{ streamingStatus }}</span>
              </div>
              <div class="ai-message-content ai-streaming" v-html="renderMarkdown(streamingContent)"></div>
            </div>
          </div>
        </div>

        <div class="ai-chat-input-area">
          <div class="ai-chat-input-wrapper" :class="{ 'is-dragging': isDraggingFile }">
            <div class="ai-input-box" :class="{ 'has-images': pastedImages.length || pastedDocs.length }">
              <!-- 图片预览：嵌在输入框顶部 -->
              <div v-if="pastedImages.length || pastedDocs.length" class="ai-attachment-list">
                <template v-for="(img, idx) in pastedImages" :key="'img-' + idx">
                  <div class="ai-attachment-item image-item">
                    <img :src="img.url" class="ai-attachment-thumb" />
                    <span class="ai-attachment-name" :title="img.name">{{ img.name }}</span>
                    <el-icon class="ai-attachment-remove" @click="removeImage(idx)"><Close /></el-icon>
                  </div>
                </template>
                <template v-for="(doc, idx) in pastedDocs" :key="'doc-' + idx">
                  <div class="ai-attachment-item doc-item">
                    <el-icon class="ai-doc-icon" :class="doc.ext"><Document /></el-icon>
                    <span class="ai-attachment-name" :title="doc.name">{{ doc.name }}</span>
                    <span class="ai-doc-size">{{ doc.sizeText }}</span>
                    <el-icon class="ai-attachment-remove" @click="removeDoc(idx)"><Close /></el-icon>
                  </div>
                </template>
              </div>
              <textarea
                v-model="chatInput"
                class="ai-chat-textarea"
                :placeholder="chatPlaceholder"
                @keydown.enter.exact.prevent="sendMessage"
                @input="autoResizeTextarea"
                @paste.native="onPaste"
                @dragover.prevent="onDragOver"
                @dragleave.prevent="onDragLeave"
                @drop.prevent="onDrop"
                rows="3"
                ref="chatTextareaRef"
              ></textarea>
              <!-- 附件按钮 -->
              <el-tooltip content="上传文档 (PDF/Word/Excel/Markdown/TXT)" placement="top" effect="dark">
                <el-button
                  circle
                  size="small"
                  class="ai-attach-btn"
                  @click="triggerFileInput"
                  :disabled="aiStreaming || aiTaskRunning"
                >
                  <el-icon><Paperclip /></el-icon>
                </el-button>
              </el-tooltip>
              <input
                type="file"
                ref="fileInputRef"
                class="ai-file-input"
                multiple
                accept=".pdf,.doc,.docx,.xls,.xlsx,.md,.txt,.csv"
                @change="onFileSelect"
              />
              <el-button
                type="primary"
                @click="sendMessage"
                :disabled="(!chatInput.trim() && !pastedImages.length && !pastedDocs.length) || aiStreaming || aiTaskRunning"
                :loading="aiStreaming || aiTaskRunning"
                class="ai-send-btn"
              >
                <el-icon v-if="!aiStreaming"><Promotion /></el-icon>
              </el-button>
            </div>
            <!-- 拖拽提示 -->
            <div v-if="isDraggingFile" class="ai-drag-overlay">
              <el-icon :size="48" color="#8b5cf6"><UploadFilled /></el-icon>
              <span>松开上传文件</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </el-dialog>

  <!-- 重命名对话弹窗 -->
  <el-dialog v-model="renameConvVisible" title="重命名对话" width="450" class="elegant-dialog" :close-on-click-modal="false" append-to-body>
    <div class="dialog-content">
      <el-form label-position="top" class="dialog-form">
        <el-form-item class="dialog-form-item">
          <el-input v-model="renameConvTitle" placeholder="请输入对话名称" class="input" size="large" maxlength="50" show-word-limit @keydown.enter="confirmRename"/>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="renameConvVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button type="primary" @click="confirmRename" class="dialog-confirm-btn">保存</el-button>
      </span>
    </template>
  </el-dialog>

  <!-- 删除对话确认弹窗 -->
  <el-dialog v-model="deleteConvVisible" title="删除对话" width="450" class="elegant-dialog" :close-on-click-modal="false" append-to-body>
    <div class="dialog-content">
      <div class="delete-conv-tip">
        <el-icon :size="24" color="#f59e0b"><WarningFilled /></el-icon>
        <span>确定删除该对话？删除后不可恢复。</span>
      </div>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="deleteConvVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button type="danger" @click="confirmDeleteConv" class="dialog-confirm-btn">删除</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { mapState } from 'vuex'
import { ElMessage } from 'element-plus'
import { base_url } from '../api/index.js'
import {
  Plus,
  Delete,
  CopyDocument,
  MagicStick,
  Loading,
  WarningFilled,
  Promotion,
  ArrowDown,
  Select,
  Edit,
  Check,
  Document,
  ChatDotRound,
  Close,
  Paperclip,
  UploadFilled
} from '@element-plus/icons-vue'

export default {
  name: 'AiAssistant',
  emits: ['cases-saved'],
  watch: {
    aiChatVisible(val) {
      if (!val) {
        this.currentConversationId = null
        this.currentConversationTitle = ''
        this.chatMessages = []
        this.chatInput = ''
        this.aiStreaming = false
        this.aiTaskRunning = false
        this.streamingContent = ''
        this.conversation_list = []
        this.conv_page = 1
        this.conv_has_more = false
        this.chatMode = ''
        this.pastedImages = []
        this.pastedDocs = []
      }
    }
  },
  computed: {
    ...mapState(['projectInfo', 'userInfo']),
    currentModelName() {
      const config = this.ai_config_list.find(c => c.id === this.aiChatConfigId)
      return config ? config.model_name : ''
    },
    chatPlaceholder() {
      if (this.chatMode === 'generate') {
        return '描述你的测试需求，AI将为你生成功能测试用例...'
      }
      if (this.chatMode === 'assistant') {
        return '输入你的问题，按 Enter 发送，Shift+Enter 换行...'
      }
      return '请先选择上方功能模式...'
    },
    fabStyle() {
      if (this.fabPos) {
        return { left: this.fabPos.x + 'px', top: this.fabPos.y + 'px', right: 'auto', bottom: 'auto' }
      }
      return {}
    }
  },
  data() {
    return {
      // AI对话相关
      aiChatVisible: false,
      aiChatConfigId: '',
      ai_config_list: [],
      conversation_list: [],
      conv_page: 1,
      conv_size: 20,
      conv_has_more: false,
      conv_loading: false,
      currentConversationId: null,
      currentConversationTitle: '',
      chatMessages: [],
      chatInput: '',
      aiStreaming: false,
      streamingContent: '',
      streamingStatus: '',
      aiModelPopoverVisible: false,
      renameConvVisible: false,
      renameConvTitle: '',
      renameConvId: null,
      deleteConvVisible: false,
      deleteConvId: null,
      chatMode: '', // 'generate' | 'assistant'
      // 异步任务相关
      aiTaskRunning: false,
      // 拖动相关
      isDragging: false,
      fabPos: null, // {x, y} 拖动后的位置
      dragStart: { x: 0, y: 0, fabX: 0, fabY: 0 },
      dragMoved: false,
      // 粘贴图片
      pastedImages: [], // [{ url: 'data:image/...', base64: '...', name: 'image.png' }]
      // 上传文档
      pastedDocs: [], // [{ name, ext, size, sizeText, base64, type }]
      isDraggingFile: false,
      maxFileSize: 20 * 1024 * 1024, // 20MB
      docAllowedExts: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'md', 'txt', 'csv'],
    }
  },
  components: {
    Plus,
    Delete,
    CopyDocument,
    MagicStick,
    Loading,
    WarningFilled,
    Promotion,
    ArrowDown,
    Select,
    Edit,
    Check,
    Document,
    ChatDotRound,
    Close,
    Paperclip,
    UploadFilled
  },
  methods: {
    // ===== AI对话式生成 =====
    async openAiChat() {
      this.aiChatVisible = true
      if (!this.ai_config_list.length) {
        const res = await this.$api.getAiConfigs({ is_active: true, project: this.projectInfo.id })
        if (res.status === 200) {
          this.ai_config_list = res.data.results || res.data.result || []
          // 恢复缓存的模型选择，无缓存时选中默认AI配置
          if (!this.aiChatConfigId) {
            const cachedId = localStorage.getItem(`ai_model_${this.projectInfo.id}`)
            if (cachedId && this.ai_config_list.some(c => c.id == cachedId)) {
              this.aiChatConfigId = Number(cachedId)
            } else {
              const def = this.ai_config_list.find(c => c.is_default)
              if (def) this.aiChatConfigId = def.id
            }
          }
        }
      }
      await this.loadConversations(true)
      // 自动选中最近的会话
      if (this.conversation_list.length && !this.currentConversationId) {
        await this.selectConversation(this.conversation_list[0].id)
      }
      this.adjustChatHeight()
    },

    // ===== 浮动按钮拖动 =====
    onFabMouseDown(e) {
      const fab = e.currentTarget
      const rect = fab.getBoundingClientRect()
      this.dragStart = {
        x: e.clientX,
        y: e.clientY,
        fabX: rect.left,
        fabY: rect.top,
      }
      this.dragMoved = false
      this.isDragging = true
      document.addEventListener('mousemove', this.onFabMouseMove)
      document.addEventListener('mouseup', this.onFabMouseUp)
    },

    onFabMouseMove(e) {
      const dx = e.clientX - this.dragStart.x
      const dy = e.clientY - this.dragStart.y
      if (Math.abs(dx) > 4 || Math.abs(dy) > 4) {
        this.dragMoved = true
      }
      let newX = this.dragStart.fabX + dx
      let newY = this.dragStart.fabY + dy
      // 边界限制（Y轴下限需考虑顶部菜单栏高度，避免被遮挡）
      const fabSize = 52
      const headerH = document.querySelector('.main-menu')?.offsetHeight || 54
      newX = Math.max(8, Math.min(newX, window.innerWidth - fabSize - 8))
      newY = Math.max(headerH + 8, Math.min(newY, window.innerHeight - fabSize - 8))
      this.fabPos = { x: newX, y: newY }
    },

    onFabMouseUp() {
      this.isDragging = false
      document.removeEventListener('mousemove', this.onFabMouseMove)
      document.removeEventListener('mouseup', this.onFabMouseUp)
      if (this.dragMoved && this.fabPos) {
        localStorage.setItem('ai_fab_pos', JSON.stringify(this.fabPos))
      }
    },

    onFabClick() {
      if (this.dragMoved) return
      this.openAiChat()
    },

    // 窗口尺寸变化时检查 FAB 是否还在视口内，超出则重置到默认位置
    checkFabPosition() {
      if (this.fabPos) {
        const fabSize = 52
        const headerH = document.querySelector('.main-menu')?.offsetHeight || 54
        if (this.fabPos.x < 8 || this.fabPos.x > window.innerWidth - fabSize - 8 ||
            this.fabPos.y < headerH + 8 || this.fabPos.y > window.innerHeight - fabSize - 8) {
          this.fabPos = null
          localStorage.removeItem('ai_fab_pos')
        }
      }
    },

    adjustChatHeight() {
      setTimeout(() => {
        const header = document.querySelector('.ai-chat-dialog .el-dialog__header')
        const headerH = header ? header.offsetHeight : 60
        const sidebar = document.querySelector('.ai-chat-sidebar')
        const main = document.querySelector('.ai-chat-main')
        if (sidebar) sidebar.style.top = headerH + 'px'
        if (main) main.style.top = headerH + 'px'
      }, 100)
    },

    selectModel(configId) {
      this.aiChatConfigId = configId
      this.aiModelPopoverVisible = false
      if (this.projectInfo && this.projectInfo.id) {
        localStorage.setItem(`ai_model_${this.projectInfo.id}`, configId)
      }
    },

    async loadConversations(reset = true) {
      if (this.conv_loading) return
      if (!reset && !this.conv_has_more) return
      this.conv_loading = true
      try {
        const page = reset ? 1 : this.conv_page
        const res = await this.$api.aiConversations({
          project: this.projectInfo.id,
          page,
          size: this.conv_size,
        })
        if (res.status === 200) {
          const list = res.data.results || res.data.result || []
          if (reset) {
            this.conversation_list = list
          } else {
            this.conversation_list.push(...list)
          }
          this.conv_page = page + 1
          this.conv_has_more = !!res.data.next
        }
      } finally {
        this.conv_loading = false
      }
    },

    onConversationScroll(e) {
      const el = e.target
      if (!el) return
      if (el.scrollTop + el.clientHeight >= el.scrollHeight - 50) {
        this.loadConversations(false)
      }
    },

    async newConversation() {
      if (!this.aiChatConfigId) return
      const res = await this.$api.aiCreateConversation({
        project_id: this.projectInfo.id,
        ai_config_id: this.aiChatConfigId,
        module_id: null,
        title: '新对话',
      })
      if (res.status === 200 || res.status === 201) {
        const newConvId = res.data.result?.id || res.data.id
        await this.loadConversations(true)
        if (newConvId) {
          await this.selectConversation(newConvId)
        }
      }
    },

    renameConversation(conv) {
      this.renameConvId = conv.id
      this.renameConvTitle = conv.title
      this.renameConvVisible = true
    },

    async confirmRename() {
      const title = this.renameConvTitle.trim()
      if (!title) {
        ElMessage({ message: '名称不能为空', type: 'warning' })
        return
      }
      const res = await this.$api.aiRenameConversation(this.renameConvId, { title })
      if (res.status === 200) {
        const conv = this.conversation_list.find(c => c.id === this.renameConvId)
        if (conv) conv.title = title
        this.renameConvVisible = false
        ElMessage({ message: '重命名成功', type: 'success' })
      }
    },

    async selectConversation(convId) {
      this.currentConversationId = convId
      const conv = this.conversation_list.find(c => c.id === convId)
      this.currentConversationTitle = conv ? conv.title : ''
      if (conv && conv.ai_config_id) {
        this.aiChatConfigId = conv.ai_config_id
      }
      // 切换会话时默认设为助手模式
      if (!this.chatMode) this.chatMode = 'assistant'
      // 加载消息
      const res = await this.$api.aiConversationMessages(convId)
      if (res.status === 200) {
        const msgData = res.data.results || res.data.result || []
        this.chatMessages = msgData.map(m => ({ ...m, saving: false, copied: false }))
        this.$nextTick(() => this.scrollToBottom())
      }
    },

    deleteConversation(convId) {
      this.deleteConvId = convId
      this.deleteConvVisible = true
    },

    async confirmDeleteConv() {
      const res = await this.$api.aiDeleteConversation(this.deleteConvId)
      if (res.status === 204) {
        if (this.currentConversationId === this.deleteConvId) {
          this.currentConversationId = null
          this.currentConversationTitle = ''
          this.chatMessages = []
        }
        await this.loadConversations(true)
        this.deleteConvVisible = false
        ElMessage({ message: '删除成功', type: 'success' })
      }
    },

    selectMode(mode) {
      this.chatMode = mode
      this.$nextTick(() => {
        if (this.$refs.chatTextareaRef) this.$refs.chatTextareaRef.focus()
      })
    },

    async sendMessage() {
      const msg = this.chatInput.trim()
      if ((!msg && !this.pastedImages.length && !this.pastedDocs.length) || this.aiStreaming || this.aiTaskRunning) return
      if (!this.aiChatConfigId) {
        ElMessage({ message: '请先选择AI模型', type: 'warning' })
        return
      }
      // 有图片或文档时自动切到生成用例模式
      if ((this.pastedImages.length || this.pastedDocs.length) && this.chatMode !== 'generate') {
        this.chatMode = 'generate'
      }
      // 生成用例模式：走异步任务，不创建会话
      if (this.chatMode === 'generate') {
        this.chatInput = ''
        this.autoResizeTextarea()
        await this.generateFuncCaseTask(msg)
        return
      }
      if (!this.currentConversationId) {
        await this.newConversation()
        if (!this.currentConversationId) return
      }
      // 首次发送消息时，用消息内容前15个字作为对话名称
      const conv = this.conversation_list.find(c => c.id === this.currentConversationId)
      if (conv && conv.title === '新对话') {
        const newTitle = msg.slice(0, 15) || '新对话'
        try {
          const res = await this.$api.aiRenameConversation(this.currentConversationId, { title: newTitle })
          if (res.status === 200) {
            conv.title = newTitle
          }
        } catch (e) { /* ignore */ }
      }
      this.chatInput = ''
      this.autoResizeTextarea()

      // 立即把用户消息插入列表（乐观展示）
      this.chatMessages.push({
        id: 'local_' + Date.now(),
        role: 'user',
        content: msg,
        cases_data: [],
        saving: false,
        copied: false,
      })
      this.$nextTick(() => this.scrollToBottom())

      this.aiStreaming = true
      this.streamingContent = ''
      this.streamingStatus = ''

      // 调用SSE流式接口
      const url = `${base_url}/ai/conversations/${this.currentConversationId}/chat_stream/`
      const token = JSON.parse(localStorage.getItem('token') || '""') || ''
      const body = JSON.stringify({
        message: msg,
        ai_config_id: this.aiChatConfigId,
        mode: this.chatMode || 'assistant',
      })

      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: body,
      }).then(response => {
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        const read = () => {
          reader.read().then(({ done, value }) => {
            if (done) {
              this.aiStreaming = false
              this.streamingContent = ''
              return
            }
            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            buffer = lines.pop() || ''
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6))
                  if (data.tool_status) {
                    this.streamingStatus = data.tool_status
                    this.scrollToBottom()
                  }
                  if (data.content) {
                    this.streamingStatus = ''
                    this.streamingContent += data.content
                    this.scrollToBottom()
                  }
                  if (data.done) {
                    this.aiStreaming = false
                    this.streamingStatus = ''
                    this.chatMessages.push({
                      id: data.message_id,
                      role: 'assistant',
                      content: this.streamingContent,
                      cases_data: data.cases || [],
                      saving: false,
                    })
                    this.streamingContent = ''
                    this.scrollToBottom()
                  }
                  if (data.error) {
                    this.aiStreaming = false
                    this.streamingContent = ''
                    this.streamingStatus = ''
                    ElMessage({ message: data.error, type: 'error' })
                  }
                } catch (e) {
                  // ignore parse errors
                }
              }
            }
            read()
          }).catch(err => {
            this.aiStreaming = false
            console.error('SSE error:', err)
          })
        }
        read()
      }).catch(err => {
        this.aiStreaming = false
        ElMessage({ message: '请求失败', type: 'error' })
        console.error('fetch error:', err)
      })
    },

    // ===== 异步任务：AI生成功能用例 =====
    async generateFuncCaseTask(requirement) {
      this.aiTaskRunning = true
      // 收集图片base64
      const images = this.pastedImages.map(img => ({
        base64: img.base64,
        type: img.type,
      }))
      // 收集文档base64
      const documents = this.pastedDocs.map(doc => ({
        base64: doc.base64,
        name: doc.name,
        ext: doc.ext,
        type: doc.type,
        size: doc.size,
      }))
      // 立即提示并关闭弹窗，不等接口返回
      ElMessage({ message: '任务已提交，AI正在生成用例中', type: 'success' })
      this.aiChatVisible = false
      this.pastedImages = []
      this.pastedDocs = []
      try {
        await this.$api.aiGenerateFuncCase({
          requirement,
          ai_config_id: this.aiChatConfigId,
          project_id: this.projectInfo.id,
          images,
          documents,
        })
      } catch (e) {
        ElMessage({ message: '任务提交失败，请稍后重试', type: 'error' })
      } finally {
        this.aiTaskRunning = false
      }
    },

    // ===== 粘贴处理（图片+文档） =====
    onPaste(e) {
      const items = e.clipboardData?.items
      if (!items) return
      const imageItems = []
      const docItems = []
      for (let i = 0; i < items.length; i++) {
        const item = items[i]
        if (item.type.startsWith('image/')) {
          imageItems.push(item)
        } else if (item.kind === 'file' && item.type && !item.type.startsWith('text/')) {
          // 非图片的文件类型
          docItems.push(item)
        }
      }
      if (imageItems.length === 0 && docItems.length === 0) return
      // 阻止默认粘贴行为
      e.preventDefault()
      imageItems.forEach((item) => {
        const file = item.getAsFile()
        if (!file) return
        this._compressImage(file).then(({ dataUrl, base64, name, type }) => {
          this.pastedImages.push({ url: dataUrl, base64, name, type })
        })
      })
      docItems.forEach((item) => {
        const file = item.getAsFile()
        if (!file) return
        this._processDocFile(file)
      })
    },

    // ===== 文件选择处理 =====
    triggerFileInput() {
      this.$refs.fileInputRef?.click()
    },
    onFileSelect(e) {
      const files = e.target.files
      if (!files || files.length === 0) return
      this._handleFiles(files)
      // 重置input，允许选择相同文件
      e.target.value = ''
    },

    // ===== 拖拽处理 =====
    onDragOver(e) {
      if (this.aiStreaming || this.aiTaskRunning) return
      const files = e.dataTransfer?.files
      if (files && files.length > 0) {
        this.isDraggingFile = true
      }
    },
    onDragLeave() {
      this.isDraggingFile = false
    },
    onDrop(e) {
      this.isDraggingFile = false
      if (this.aiStreaming || this.aiTaskRunning) return
      const files = e.dataTransfer?.files
      if (!files || files.length === 0) return
      this._handleFiles(files)
    },

    // 处理文件列表（图片→pastedImages，文档→pastedDocs）
    _handleFiles(files) {
      Array.from(files).forEach(file => {
        if (file.type.startsWith('image/')) {
          this._compressImage(file).then(({ dataUrl, base64, name, type }) => {
            this.pastedImages.push({ url: dataUrl, base64, name, type })
          })
        } else {
          this._processDocFile(file)
        }
      })
    },

    // 处理文档文件
    _processDocFile(file) {
      const ext = (file.name?.split('.').pop() || '').toLowerCase()
      if (!this.docAllowedExts.includes(ext)) {
        ElMessage({ message: `不支持的文件类型: .${ext}`, type: 'warning' })
        return
      }
      if (file.size > this.maxFileSize) {
        ElMessage({ message: `文件 ${file.name} 超过20MB限制`, type: 'warning' })
        return
      }
      const reader = new FileReader()
      reader.onload = (ev) => {
        const base64 = ev.target.result.split(',')[1] || ''
        this.pastedDocs.push({
          name: file.name,
          ext,
          size: file.size,
          sizeText: this._formatFileSize(file.size),
          base64,
          type: file.type || `application/${ext}`,
        })
      }
      reader.readAsDataURL(file)
    },

    // 格式化文件大小
    _formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / 1024 / 1024).toFixed(1) + ' MB'
    },

    // 删除文档
    removeDoc(idx) {
      this.pastedDocs.splice(idx, 1)
    },

    // 压缩图片：限制最大尺寸和质量，减小传输体积
    _compressImage(file) {
      return new Promise((resolve) => {
        const reader = new FileReader()
        reader.onload = (ev) => {
          const img = new Image()
          img.onload = () => {
            const MAX_DIM = 1920
            let { width, height } = img
            if (width > MAX_DIM || height > MAX_DIM) {
              const ratio = Math.min(MAX_DIM / width, MAX_DIM / height)
              width = Math.round(width * ratio)
              height = Math.round(height * ratio)
            }
            const canvas = document.createElement('canvas')
            canvas.width = width
            canvas.height = height
            const ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0, width, height)
            // 转为JPEG压缩（PNG截图有大量透明区域时，JPEG体积更小）
            const dataUrl = canvas.toDataURL('image/jpeg', 0.85)
            const base64 = dataUrl.split(',')[1] || ''
            const ext = file.name?.split('.').pop() || 'png'
            resolve({
              dataUrl,
              base64,
              name: file.name || `image_${Date.now()}.${ext}`,
              type: 'image/jpeg',
            })
          }
          img.onerror = () => {
            // 图片加载失败，使用原始数据
            const dataUrl = ev.target.result
            resolve({
              dataUrl,
              base64: dataUrl.split(',')[1] || '',
              name: file.name || `image_${Date.now()}.png`,
              type: file.type || 'image/png',
            })
          }
          img.src = ev.target.result
        }
        reader.readAsDataURL(file)
      })
    },

    removeImage(idx) {
      this.pastedImages.splice(idx, 1)
    },

    autoResizeTextarea() {
      this.$nextTick(() => {
        const el = this.$refs.chatTextareaRef
        if (!el) return
        el.style.height = 'auto'
        el.style.height = Math.min(el.scrollHeight, 800) + 'px'
      })
    },

    async saveCases(msg) {
      msg.saving = true
      try {
        const res = await this.$api.aiSaveChatCases({
          message_id: msg.id,
          cases: msg.cases_data,
          project_id: this.projectInfo.id,
          module_id: null,
        })
        if (res.status === 200) {
          const savedCount = res.data.result?.saved_count ?? res.data.saved_count ?? 0
          ElMessage({ message: `成功保存 ${savedCount} 条用例`, type: 'success' })
          this.$emit('cases-saved', { count: savedCount })
        }
      } catch (e) {
        ElMessage({ message: '保存失败', type: 'error' })
      } finally {
        msg.saving = false
      }
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const el = this.$refs.chatMessagesRef
        if (el) el.scrollTop = el.scrollHeight
      })
    },

    renderMarkdown(text) {
      if (!text) return ''
      let html = text

      // ===== 1. 代码块（先处理，避免内部内容被替换破坏） =====
      html = html.replace(/```json\s*([\s\S]*?)```/g, (_m, code) => {
        return '<pre class="md-code-block"><code>' + this._escapeHtml(code.trim()) + '</code></pre>'
      })
      html = html.replace(/```\s*([\s\S]*?)```/g, (_m, code) => {
        return '<pre class="md-code-block"><code>' + this._escapeHtml(code.trim()) + '</code></pre>'
      })

      // ===== 2. Markdown表格渲染 =====
      html = html.replace(/((?:^\|.*\|\n)+)/gm, (tableBlock) => {
        const lines = tableBlock.trim().split('\n').filter(l => l.includes('|'))
        if (lines.length < 2) return tableBlock
        const headerLine = lines[0]
        const separatorLine = lines[1]
        if (!separatorLine.match(/^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/)) return tableBlock
        const bodyLines = lines.slice(2)

        const parseRow = (line) => line
          .replace(/^\|/, '').replace(/\|$/, '')
          .split('|')
          .map(cell => cell.trim())

        const headers = parseRow(headerLine)
        const rows = bodyLines.map(parseRow)

        let tableHtml = '<table class="md-table"><thead><tr>'
        headers.forEach(h => { tableHtml += `<th>${this._inlineMarkdown(h)}</th>` })
        tableHtml += '</tr></thead><tbody>'
        rows.forEach(row => {
          tableHtml += '<tr>'
          row.forEach(cell => { tableHtml += `<td>${this._inlineMarkdown(cell)}</td>` })
          tableHtml += '</tr>'
        })
        tableHtml += '</tbody></table>'
        return tableHtml
      })

      // ===== 3. 标题 =====
      html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>')
      html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>')
      html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>')

      // ===== 4. 分割线 =====
      html = html.replace(/^---+$/gm, '<hr class="md-hr">')

      // ===== 5. 有序列表（包裹成 <ol>） =====
      html = html.replace(/((?:^\d+\. .+\n?)+)/gm, (_m, block) => {
        const items = block.trim().split('\n').map(line =>
          line.replace(/^\d+\. (.+)$/, '$1')
        )
        return '<ol class="md-ol">' + items.map(i => `<li>${this._inlineMarkdown(i)}</li>`).join('') + '</ol>'
      })

      // ===== 6. 无序列表（包裹成 <ul>） =====
      html = html.replace(/((?:^[-*] .+\n?)+)/gm, (_m, block) => {
        const items = block.trim().split('\n').map(line =>
          line.replace(/^[-*] (.+)$/, '$1')
        )
        return '<ul class="md-ul">' + items.map(i => `<li>${this._inlineMarkdown(i)}</li>`).join('') + '</ul>'
      })

      // ===== 7. 行内元素 =====
      html = this._inlineMarkdown(html, true)

      // ===== 8. 换行（非表格/列表内部） =====
      html = html.replace(/\n/g, '<br>')

      return html
    },

    // 行内Markdown处理（加粗、行内代码等）
    _inlineMarkdown(text, skipCode = false) {
      let s = text
      if (!skipCode) {
        s = s.replace(/`([^`]+)`/g, '<code class="md-inline-code">$1</code>')
      }
      s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      // emoji格式 💡 **标题** 已处理加粗
      return s
    },

    _escapeHtml(text) {
      const div = document.createElement('div')
      div.textContent = text
      return div.innerHTML
    },

    async copyMsgContent(msg) {
      if (!msg || !msg.content) return
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(msg.content)
        } else {
          const ta = document.createElement('textarea')
          ta.value = msg.content
          ta.style.position = 'fixed'
          ta.style.left = '-9999px'
          document.body.appendChild(ta)
          ta.select()
          document.execCommand('copy')
          document.body.removeChild(ta)
        }
        msg.copied = true
        setTimeout(() => { msg.copied = false }, 1800)
        ElMessage({ message: '已复制到剪贴板', type: 'success', duration: 1500 })
      } catch (e) {
        ElMessage({ message: '复制失败', type: 'error' })
      }
    },
  },
  mounted() {
    window.addEventListener('resize', this.adjustChatHeight)
    window.addEventListener('resize', this.checkFabPosition)
    // 恢复缓存的浮动按钮位置
    const cachedPos = localStorage.getItem('ai_fab_pos')
    if (cachedPos) {
      try {
        const pos = JSON.parse(cachedPos)
        if (pos && typeof pos.x === 'number' && typeof pos.y === 'number') {
          const fabSize = 52
          const headerH = document.querySelector('.main-menu')?.offsetHeight || 54
          // 边界检查：确保 FAB 在当前视口内可见且不被菜单栏遮挡
          if (pos.x >= 8 && pos.x <= window.innerWidth - fabSize - 8 &&
              pos.y >= headerH + 8 && pos.y <= window.innerHeight - fabSize - 8) {
            this.fabPos = pos
          } else {
            // 超出视口，清除缓存，回到默认位置
            localStorage.removeItem('ai_fab_pos')
          }
        }
      } catch (e) { /* ignore */ }
    }
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.adjustChatHeight)
    window.removeEventListener('resize', this.checkFabPosition)
  }
}
</script>

<style scoped>
/* ===== AI助手浮动按钮 ===== */
.ai-assistant-fab {
  position: fixed;
  right: 28px;
  bottom: 28px;
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  color: #fff;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.45);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
}

.ai-assistant-fab:hover {
  transform: translateY(-3px) scale(1.03);
  box-shadow: 0 12px 32px rgba(139, 92, 246, 0.55);
  background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
}

.ai-assistant-fab:active {
  transform: translateY(-1px) scale(1.01);
}

.ai-assistant-fab.dragging,
.ai-assistant-fab.dragging:hover,
.ai-assistant-fab.dragging:active {
  transform: none;
  cursor: grabbing;
  transition: none;
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.45);
  opacity: 0.9;
}

.ai-fab-icon {
  font-size: 22px;
}

.ai-fab-pulse {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #10b981;
  border: 2px solid #fff;
  animation: aiPulse 2s ease-in-out infinite;
}

@keyframes aiPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.15); }
}

/* ===== AI全屏对话弹窗 ===== */
:deep(.el-dialog.ai-chat-dialog) {
  margin: 0 !important;
  padding: 0 !important;
  border-radius: 0 !important;
  background: #fff;
  display: flex !important;
  flex-direction: column !important;
  height: 100vh !important;
  overflow: hidden !important;
}

:deep(.el-dialog__body) {
  padding: 0 !important;
  flex: 1 !important;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
  min-height: 0 !important;
}

/* 顶部标题 + 模型选择 */
.ai-dialog-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ai-header-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  position: relative;
  padding-left: 16px;
}

.ai-header-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 24px;
  background: linear-gradient(180deg, #8b5cf6 0%, #6d28d9 100%);
  border-radius: 2px;
}

/* 模型名称按钮 */
.ai-model-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 600;
  color: #6d28d9;
  cursor: pointer;
  padding: 5px 12px;
  border-radius: 8px;
  background: #f5f3ff;
  transition: all 0.2s;
  user-select: none;
}

.ai-model-name:hover {
  background: #ede9fe;
  color: #5b21b6;
}

.ai-model-arrow {
  font-size: 13px;
  color: #8b5cf6;
  transition: transform 0.2s;
}

.ai-model-arrow.open {
  transform: rotate(180deg);
}

/* 模型选择弹窗列表 */
.ai-model-list {
  max-height: 320px;
  overflow-y: auto;
  background: #f5f3ff;
  border-radius: 8px;
  padding: 4px;
}

.ai-model-list-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.ai-model-list-item:hover {
  background: #ede9fe;
}

.ai-model-list-item.active {
  background: linear-gradient(135deg, #ddd6fe 0%, #c4b5fd 100%);
}

.ai-model-list-name {
  font-size: 14px;
  font-weight: 600;
  color: #6d28d9;
}

.ai-model-list-desc {
  font-size: 12px;
  color: #8b5cf6;
}

.ai-model-check {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6d28d9;
  font-size: 16px;
}

.ai-model-list-empty {
  text-align: center;
  color: #8b5cf6;
  font-size: 13px;
  padding: 20px 0;
}

.ai-chat-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

/* 左侧会话列表 */
.ai-chat-sidebar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 280px;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}

.ai-sidebar-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px 25px 12px 10px;
  border-bottom: 1px solid #f1f5f9;
}

.ai-new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  height: 42px;
  border-radius: 10px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
  user-select: none;
}

.ai-new-chat-btn:hover {
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
  box-shadow: 0 4px 14px rgba(139, 92, 246, 0.45);
  transform: translateY(-1px);
}

.ai-new-chat-btn:active {
  transform: translateY(0);
}

.ai-new-chat-icon {
  font-size: 16px;
}

.ai-conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.ai-conversation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.ai-conversation-item:hover {
  background: #f1f5f9;
}

.ai-conversation-item.active {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
}

.ai-conv-item-main {
  flex: 1;
  overflow: hidden;
}

.ai-conv-title {
  font-size: 13px;
  font-weight: 500;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ai-conv-meta {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.ai-conv-action,
.ai-conv-delete {
  color: #cbd5e1;
  cursor: pointer;
  flex-shrink: 0;
  margin-left: 8px;
  opacity: 0;
  transition: all 0.2s;
}

.ai-conversation-item:hover .ai-conv-action,
.ai-conversation-item:hover .ai-conv-delete,
.ai-conversation-item.active .ai-conv-action,
.ai-conversation-item.active .ai-conv-delete {
  opacity: 1;
}

.ai-conv-action:hover {
  color: #6d28d9;
}

.ai-conv-delete:hover {
  color: #ef4444;
}

.ai-empty-conversation {
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
  padding: 40px 0;
}

.ai-conv-loadmore {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 16px 0;
  color: #94a3b8;
  font-size: 12px;
}

.ai-conv-loadmore.end {
  color: #cbd5e1;
}

/* 删除对话确认提示 */
.delete-conv-tip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  font-size: 14px;
  color: #475569;
}

/* 右侧对话区 */
.ai-chat-main {
  position: fixed;
  bottom: 0;
  left: 280px;
  right: 0;
  background: #fff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ai-chat-main.no-messages {
  justify-content: center;
}

.ai-chat-main.no-messages .ai-chat-messages {
  flex: 0 0 auto;
}

.ai-chat-messages {
  flex: 1;
  overflow-y: scroll;
  padding: 20px 20px;
  scroll-behavior: smooth;
}

/* AI聊天区细滚动条 */
.ai-chat-messages::-webkit-scrollbar,
.ai-conversation-list::-webkit-scrollbar,
.ai-chat-textarea::-webkit-scrollbar {
  width: 6px;
}

.ai-chat-messages::-webkit-scrollbar-track,
.ai-conversation-list::-webkit-scrollbar-track,
.ai-chat-textarea::-webkit-scrollbar-track {
  background: transparent;
}

.ai-chat-messages::-webkit-scrollbar-thumb,
.ai-conversation-list::-webkit-scrollbar-thumb,
.ai-chat-textarea::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.ai-chat-messages::-webkit-scrollbar-thumb:hover,
.ai-conversation-list::-webkit-scrollbar-thumb:hover,
.ai-chat-textarea::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 欢迎页 */
.ai-chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 12px;
}

.ai-chat-welcome h3 {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 8px 0 4px;
}

.ai-welcome-options {
  display: flex;
  gap: 16px;
  margin-top: 12px;
}

.ai-welcome-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  transition: all 0.25s;
  user-select: none;
}

.ai-welcome-option:hover {
  border-color: #c4b5fd;
  background: #f5f3ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.12);
}

.ai-welcome-option.active {
  border-color: #8b5cf6;
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
}

.ai-welcome-option.active .ai-welcome-option-icon {
  color: #6d28d9;
}

.ai-welcome-option.active .ai-welcome-option-text {
  color: #6d28d9;
  font-weight: 600;
}

.ai-welcome-option-icon {
  font-size: 20px;
  color: #8b5cf6;
}

.ai-welcome-option-text {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

/* 消息样式 */
.ai-message {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
  max-width: 1100px;
  margin-left: auto;
  margin-right: auto;
}

.ai-message.assistant .ai-message-body {
  max-width: calc(100% - 150px);
  margin-right: auto;
}

.ai-message.user .ai-message-body {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  max-width: calc(100% - 150px);
  margin-left: auto;
}

.ai-message-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-message.user .ai-message-header {
  flex-direction: row-reverse;
}

.ai-message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-message.user .ai-message-avatar {
  background: transparent;
  padding: 0;
  width: auto;
  height: auto;
}

.ai-message-name {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  line-height: 1;
}

.ai-copy-btn {
  padding: 0 !important;
  width: 28px !important;
  height: 28px !important;
  min-width: 28px !important;
  min-height: 28px !important;
  color: #94a3b8 !important;
  background: #f1f5f9 !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 6px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-decoration: none !important;
  box-shadow: none !important;
}

.ai-copy-btn:hover {
  color: #8b5cf6 !important;
  background: #f5f3ff !important;
  border-color: #c4b5fd !important;
}

.ai-copy-btn :deep(.el-icon) {
  width: 14px !important;
  height: 14px !important;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
}

.ai-copy-btn :deep(.el-button__inner) {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 0 !important;
}

.ai-message-actions {
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.ai-message.user .ai-message-actions {
  justify-content: flex-end;
}

.ai-message-body {
  flex: 1;
  min-width: 0;
}

.ai-message-content {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  color: #334155;
  word-break: break-word;
  display: inline-block;
  max-width: 100%;
}

.ai-message.assistant .ai-message-content {
  background: #fff;
  border: 1px solid #e2e8f0;
}

.ai-message-content.ai-task-success {
  border-color: #86efac !important;
  background: #f0fdf4 !important;
}

.ai-message-content.ai-task-failed {
  border-color: #fca5a5 !important;
  background: #fef2f2 !important;
  color: #b91c1c !important;
}

.ai-message.user .ai-message-cases {
  width: 100%;
}

.ai-streaming {
  position: relative;
}

.ai-streaming-status {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #94a3b8;
  font-size: 13px;
  padding: 4px 0;
}

.ai-streaming::after {
  content: '▋';
  animation: blink 1s infinite;
  color: #8b5cf6;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Markdown渲染 */
.ai-message-content :deep(.md-code-block) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
  margin: 8px 0;
  line-height: 1.6;
}

.ai-message-content :deep(.md-code-block code) {
  white-space: pre-wrap;
  word-break: break-all;
}

.ai-message-content :deep(.md-inline-code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  color: #db2777;
  font-family: Consolas, Monaco, monospace;
}

.ai-message-content :deep(h2) {
  margin: 16px 0 10px;
  font-weight: 600;
  font-size: 18px;
  color: #0f172a;
  padding-bottom: 6px;
  border-bottom: 1px solid #e2e8f0;
}

.ai-message-content :deep(h3) {
  margin: 14px 0 8px;
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.ai-message-content :deep(h4) {
  margin: 12px 0 6px;
  font-weight: 600;
  font-size: 15px;
  color: #334155;
}

/* 分割线 */
.ai-message-content :deep(.md-hr) {
  border: none;
  border-top: 1px dashed #cbd5e1;
  margin: 14px 0;
}

/* 有序/无序列表 */
.ai-message-content :deep(.md-ol),
.ai-message-content :deep(.md-ul) {
  margin: 8px 0;
  padding-left: 4px;
}

.ai-message-content :deep(.md-ul li) {
  list-style: disc;
  margin-left: 22px;
  line-height: 1.8;
  padding-left: 4px;
  color: #334155;
}

.ai-message-content :deep(.md-ol li) {
  list-style: decimal;
  margin-left: 22px;
  line-height: 1.8;
  padding-left: 4px;
  color: #334155;
}

/* Markdown表格 */
.ai-message-content :deep(.md-table) {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
  font-size: 13px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.ai-message-content :deep(.md-table th) {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #fff;
  font-weight: 600;
  text-align: left;
  padding: 10px 12px;
  border: 1px solid #7c3aed;
  white-space: nowrap;
}

.ai-message-content :deep(.md-table td) {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  color: #334155;
  background: #fff;
  line-height: 1.6;
}

.ai-message-content :deep(.md-table tbody tr:nth-child(even) td) {
  background: #f8fafc;
}

.ai-message-content :deep(.md-table tbody tr:hover td) {
  background: #eef2ff;
}

.ai-message-content :deep(strong) {
  color: #0f172a;
  font-weight: 600;
}

/* 用例预览 */
.ai-message-cases {
  margin-top: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.ai-cases-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  font-size: 13px;
  font-weight: 500;
  color: #6d28d9;
}

.ai-cases-preview {
  padding: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.ai-case-preview-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-bottom: 1px solid #f1f5f9;
}

.ai-case-preview-item:last-child {
  border-bottom: none;
}

.ai-case-num {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #8b5cf6;
  color: #fff;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.ai-case-preview-name {
  flex: 1;
  font-size: 13px;
  color: #334155;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ai-case-steps {
  font-size: 11px;
  color: #94a3b8;
  flex-shrink: 0;
}

/* 输入区 */
.ai-chat-input-area {
  padding: 0 26px 16px 20px;
  background: transparent;
}

.ai-chat-input-wrapper {
  max-width: 1100px;
  margin: 0 auto;
}

.ai-input-box {
  position: relative;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
  overflow: hidden;
}

.ai-input-box:focus-within {
  border-color: #8b5cf6;
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
}

.ai-input-box.has-images {
  padding-top: 8px;
}

.ai-chat-textarea {
  width: 100%;
  border: none;
  border-radius: 0;
  padding: 12px 88px 50px 14px;
  font-size: 14px;
  font-family: inherit;
  line-height: 1.5;
  resize: none;
  outline: none;
  overflow-y: auto;
  background: transparent;
  box-sizing: border-box;
  max-height: 800px;
}

.ai-chat-textarea::placeholder {
  color: #94a3b8;
}

.ai-attach-btn {
  position: absolute;
  right: 54px;
  bottom: 16px;
  background: #f8fafc !important;
  border: 1px solid #e2e8f0 !important;
  color: #64748b !important;
  width: 32px !important;
  height: 32px !important;
  min-height: 32px !important;
  z-index: 2;
}

.ai-attach-btn:hover:not(.is-disabled) {
  background: #f1f5f9 !important;
  color: #6d28d9 !important;
  border-color: #c4b5fd !important;
}

.ai-file-input {
  display: none;
}

.ai-send-btn {
  position: absolute;
  right: 12px;
  bottom: 16px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  border: none;
  border-radius: 8px;
  padding: 0 !important;
  width: 36px;
  height: 36px;
  min-height: 36px !important;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 2;
}

.ai-send-btn:hover {
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.ai-send-btn.is-disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background: #cbd5e1;
  box-shadow: none;
}

/* 附件预览列表（图片+文档通用） */
.ai-attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 0 14px 8px 14px;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 4px;
}

.ai-attachment-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 28px 6px 6px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  max-width: 240px;
}

.ai-attachment-item.image-item {
  /* 图片缩略图样式 */
}

.ai-attachment-item.doc-item {
  gap: 6px;
  padding: 6px 28px 6px 8px;
}

.ai-attachment-thumb {
  width: 32px;
  height: 32px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
}

.ai-doc-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.ai-doc-icon.pdf {
  color: #ef4444;
}
.ai-doc-icon.doc,
.ai-doc-icon.docx {
  color: #3b82f6;
}
.ai-doc-icon.xls,
.ai-doc-icon.xlsx {
  color: #22c55e;
}
.ai-doc-icon.md {
  color: #8b5cf6;
}
.ai-doc-icon.txt,
.ai-doc-icon.csv {
  color: #64748b;
}

.ai-attachment-name {
  font-size: 12px;
  color: #475569;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.ai-doc-size {
  font-size: 11px;
  color: #94a3b8;
  flex-shrink: 0;
}

.ai-attachment-remove {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 16px;
  height: 16px;
  background: #ef4444;
  color: #fff;
  border-radius: 50%;
  font-size: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.4);
  transition: transform 0.2s;
}

.ai-attachment-remove:hover {
  transform: scale(1.15);
}

/* 拖拽覆盖层 */
.ai-drag-overlay {
  position: absolute;
  inset: 0;
  background: rgba(139, 92, 246, 0.08);
  border: 2px dashed #8b5cf6;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  z-index: 10;
  pointer-events: none;
}

.ai-chat-input-wrapper.is-dragging .ai-input-box {
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}
</style>

<style>
/* AI全屏对话弹窗 - dialog overrides (non-scoped for Element Plus internals) */
html body .el-dialog.ai-chat-dialog {
  margin: 0 !important;
  padding: 0 !important;
  border-radius: 0 !important;
  background: #fff;
  display: flex !important;
  flex-direction: column !important;
  height: 100vh !important;
  overflow: hidden !important;
  --el-dialog-padding-primary: 0;
}

html body .el-dialog.ai-chat-dialog .el-dialog__header {
  padding: 16px 24px !important;
  margin: 0 !important;
  border-bottom: 1px solid #e2e8f0;
}

html body .el-dialog.ai-chat-dialog .el-dialog__body {
  padding: 0 !important;
  flex: 1 !important;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
  min-height: 0 !important;
}

/* AI模型选择弹窗容器 */
.ai-model-popover.el-popover.el-popper {
  background: #f5f3ff !important;
  border: 1px solid #ddd6fe !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.15) !important;
}

.ai-model-popover .el-popover__title {
  color: #6d28d9;
}

html body .ai-copy-btn.el-button {
  padding: 0 !important;
  width: 28px !important;
  height: 28px !important;
  min-width: 28px !important;
  min-height: 28px !important;
  color: #94a3b8 !important;
  background: #f1f5f9 !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 6px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-shadow: none !important;
}

html body .ai-copy-btn.el-button:hover {
  color: #8b5cf6 !important;
  background: #f5f3ff !important;
  border-color: #c4b5fd !important;
}

html body .ai-copy-btn.el-button .el-icon {
  width: 14px !important;
  height: 14px !important;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
}

html body .ai-copy-btn.el-button .el-button__inner {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 0 !important;
  flex: 0 0 auto;
}
</style>
