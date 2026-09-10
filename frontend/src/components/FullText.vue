<template>
  <div class="full-text-editor" :style="{ height: containerHeight }">
    <div id="editor-toolbar" ref="toolbarRef"></div>
    <div id="editor-content" ref="editorRef"></div>
    <Teleport to="body">
      <div
        v-if="mentionVisible && enableMention"
        class="ft-mention-panel"
        :style="panelStyle"
        @mousedown.prevent
      >
        <div v-if="filteredMentionUsers.length === 0" class="ft-mention-empty">无匹配用户</div>
        <div
          v-for="(u, i) in filteredMentionUsers"
          :key="u.id"
          class="ft-mention-item"
          :class="{ active: i === mentionActiveIndex }"
          @mousedown.prevent="selectMention(u)"
          @mouseenter="mentionActiveIndex = i"
        >
          <span class="ft-mention-avatar">{{ (u.username || 'U').charAt(0) }}</span>
          <span class="ft-mention-name">{{ u.username }}</span>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { onMounted, ref, onBeforeUnmount, watch, nextTick, computed } from 'vue'
import { createEditor, createToolbar, Boot, SlateTransforms } from '@wangeditor/editor'

// ============ 注册自定义 @ 提及元素（保证 data-user-id 在 getHtml/setHtml 中不丢失） ============
const MENTION_TYPE = 'mention'
let mentionRegistered = false
function registerMentionElement() {
  if (mentionRegistered) return
  mentionRegistered = true
  // 渲染：slate node -> snabbdom VNode（手动构造，避免直接依赖 snabbdom）
  const renderMention = (elem, children, editor) => {
    const username = elem.username || ''
    return {
      sel: 'span',
      data: {
        props: { contentEditable: false },
        attrs: { 'data-user-id': String(elem.userId || ''), 'data-w-e-type': MENTION_TYPE },
        class: { 'at-mention': true },
        style: {
          display: 'inline-flex',
          alignItems: 'center',
          padding: '1px 8px',
          margin: '0 2px',
          background: 'linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)',
          color: '#fff',
          borderRadius: '10px',
          fontSize: '13px',
          fontWeight: '600',
          lineHeight: '1.6',
          userSelect: 'none'
        }
      },
      children: undefined,
      text: '@' + username,
      elm: undefined,
      key: undefined
    }
  }
  // 序列化为 HTML（getHtml 时调用，保留 data-user-id）
  const mentionToHtml = (elem, childrenHtml) => {
    return `<span class="at-mention" data-w-e-type="${MENTION_TYPE}" data-user-id="${elem.userId || ''}" contenteditable="false">@${elem.username || ''}</span>`
  }
  // 由 HTML 解析为 slate node（setHtml/paste 时，匹配 span[data-w-e-type="mention"]）
  const parseMention = (elem, children, editor) => {
    return {
      type: MENTION_TYPE,
      userId: elem.getAttribute('data-user-id') || '',
      username: (elem.textContent || '').replace(/^@/, ''),
      children: [{ text: '' }]
    }
  }
  // editor 插件：声明为 inline + void 元素
  const withMention = (editor) => {
    const { isInline, isVoid } = editor
    const newEditor = editor
    newEditor.isInline = (elem) => {
      if (elem.type === MENTION_TYPE) return true
      return isInline(elem)
    }
    newEditor.isVoid = (elem) => {
      if (elem.type === MENTION_TYPE) return true
      return isVoid(elem)
    }
    return newEditor
  }
  try {
    Boot.registerModule({
      renderElems: [{ type: MENTION_TYPE, renderElem: renderMention }],
      elemsToHtml: [{ type: MENTION_TYPE, elemToHtml: mentionToHtml }],
      parseElemsHtml: [{ selector: `span[data-w-e-type="${MENTION_TYPE}"]`, parseElemHtml: parseMention }],
      editorPlugin: withMention
    })
  } catch (e) {
    mentionRegistered = false
  }
}
registerMentionElement()

export default {
  name: 'FullText',
  
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: '请输入内容...'
    },
    height: {
      type: [Number, String],
      default: 400
    },
    minHeight: {
      type: [Number, String],
      default: 200
    },
    maxHeight: {
      type: [Number, String],
      default: 800
    },
    disabled: {
      type: Boolean,
      default: false
    },
    // 内联 @ 提及功能开关
    enableMention: {
      type: Boolean,
      default: false
    },
    // 可被提及的用户列表 [{id, username}]
    mentionUsers: {
      type: Array,
      default: () => []
    },
    // 已被提及的用户ID（在浮层中隐藏，避免重复@）
    mentionExcludedIds: {
      type: Array,
      default: () => []
    }
  },

  emits: ['update:modelValue', 'change', 'mention-select'],
  
  setup(props, { emit }) {
    const editorRef = ref(null)
    const toolbarRef = ref(null)
    let editor = null
    let toolbar = null
    let ignoreNextChange = false // 标记是否忽略下一次change事件
    let lastHtml = '' // 记录上一次的HTML内容

    // ============ 内联 @ 提及 ============
    const mentionVisible = ref(false)
    const mentionKeyword = ref('')
    const mentionActiveIndex = ref(0)
    const mentionPos = ref({ left: 0, top: 0 })
    let mentionStartRange = null // '@' 后紧邻的折叠选区
    let mentionEndRange = null   // 当前光标选区（随键入更新）

    const filteredMentionUsers = computed(() => {
      if (!props.enableMention) return []
      const kw = mentionKeyword.value.trim().toLowerCase()
      return props.mentionUsers.filter(u => {
        if (props.mentionExcludedIds.includes(u.id)) return false
        if (!kw) return true
        return (u.username || '').toLowerCase().includes(kw)
      })
    })
    const panelStyle = computed(() => ({
      left: mentionPos.value.left + 'px',
      top: mentionPos.value.top + 'px'
    }))

    const updateMentionPos = () => {
      const sel = window.getSelection()
      if (!sel || sel.rangeCount === 0) return
      const rect = sel.getRangeAt(0).getBoundingClientRect()
      mentionPos.value = { left: rect.left, top: rect.bottom + 4 }
    }
    const openMention = () => {
      const sel = window.getSelection()
      if (!sel || sel.rangeCount === 0) return
      const r = sel.getRangeAt(0).cloneRange()
      mentionStartRange = r.cloneRange()
      mentionEndRange = r.cloneRange()
      mentionKeyword.value = ''
      mentionActiveIndex.value = 0
      updateMentionPos()
      mentionVisible.value = true
    }
    const closeMention = () => {
      mentionVisible.value = false
      mentionKeyword.value = ''
      mentionStartRange = null
      mentionEndRange = null
    }
    const selectMention = (user) => {
      if (!editor) { closeMention(); return }
      // 当前选区位于 "@关键词" 之后，用 wangEditor 自身 API 删除 (关键词长度 + 1 个 '@') 个字符以保持选区同步
      const count = mentionKeyword.value.length + 1
      for (let i = 0; i < count; i++) {
        try { editor.deleteBackward('character') } catch (e) { break }
      }
      try {
        // 插入自定义 mention slate 节点（inline + void），渲染为蓝色徽章且 data-user-id 会被序列化保留
        SlateTransforms.insertNodes(editor, {
          type: MENTION_TYPE,
          userId: String(user.id),
          username: user.username || '',
          children: [{ text: '' }]
        })
        // 提及后插入一个空格，方便继续输入
        SlateTransforms.insertText(editor, ' ')
      } catch (e) {
        // 兜底：插入纯文本
        try { editor.insertText(`@${user.username} `) } catch (e2) {}
      }
      closeMention()
      emit('mention-select', user)
    }
    // keydown（capture 阶段）：处理会触发默认行为的键（Enter 换行 / 方向键移动光标 / Esc），必须 preventDefault 阻止 wangEditor 先行处理
    const handleEditorKeydown = (e) => {
      if (!props.enableMention) return
      if (!mentionVisible.value) return
      const key = e.key
      if (key === 'Enter' || key === 'NumpadEnter') {
        e.preventDefault()
        const u = filteredMentionUsers.value[mentionActiveIndex.value]
        if (u) selectMention(u); else closeMention()
        return
      }
      if (key === 'ArrowDown') {
        e.preventDefault()
        mentionActiveIndex.value = Math.min(Math.max(filteredMentionUsers.value.length - 1, 0), mentionActiveIndex.value + 1)
        return
      }
      if (key === 'ArrowUp') {
        e.preventDefault()
        mentionActiveIndex.value = Math.max(0, mentionActiveIndex.value - 1)
        return
      }
      if (key === 'Escape') {
        e.preventDefault()
        closeMention()
        return
      }
    }

    const handleEditorKeyup = (e) => {
      if (!props.enableMention) return
      const key = e.key
      if (mentionVisible.value) {
        if (key === 'Backspace') {
          mentionKeyword.value = mentionKeyword.value.slice(0, -1)
          const sel1 = window.getSelection()
          if (sel1 && sel1.rangeCount) mentionEndRange = sel1.getRangeAt(0).cloneRange()
          if (!mentionKeyword.value) { closeMention(); return }
          mentionActiveIndex.value = 0
          updateMentionPos()
          return
        }
        // 可用于过滤的可打印字符
        if (key.length === 1 && /[a-zA-Z0-9_\u4e00-\u9fa5.\-@ ]/.test(key)) {
          if (key === ' ') { closeMention(); return }
          mentionKeyword.value += key
          mentionActiveIndex.value = 0
          const sel2 = window.getSelection()
          if (sel2 && sel2.rangeCount) mentionEndRange = sel2.getRangeAt(0).cloneRange()
          updateMentionPos()
          return
        }
        // 其他单字符（标点等）关闭浮层；多字符键名（Shift/Ctrl 等）忽略
        if (key.length === 1) closeMention()
        return
      }
      if (key === '@') openMention()
    }
    
    // 计算容器高度
    const containerHeight = computed(() => {
      if (typeof props.height === 'number') {
        return `${props.height}px`
      }
      return props.height
    })
    
    // 初始化编辑器
    const initEditor = () => {
      if (!editorRef.value || !toolbarRef.value) return
      
      // 清理旧实例
      if (editor) {
        editor.destroy()
        editor = null
      }
      if (toolbar) {
        toolbar.destroy()
        toolbar = null
      }
      
      // 编辑器配置
      const editorConfig = {
        placeholder: props.placeholder,
        scroll: true,
        autoFocus: false,
        readOnly: props.disabled,
        hoverbarKeys: {
          'link': {
            menuKeys: ['editLink', 'unLink', 'viewLink']
          },
          'image': {
            menuKeys: ['editImage', 'width50', 'width100', 'deleteImage']
          },
          'pre': {
            menuKeys: ['codeBlock', 'codeSelectLang']
          },
          'table': {
            menuKeys: ['tableHeader', 'tableFullWidth', 'insertTableRow', 'deleteTableRow', 
                      'insertTableCol', 'deleteTableCol', 'deleteTable']
          }
        },
        MENU_CONF: {
          // 图片上传配置
          uploadImage: {
            // 自定义上传 - 将图片转为base64并直接插入
            async customUpload(file, insertFn) {
              return new Promise((resolve, reject) => {
                try {
                  // 转为base64
                  const reader = new FileReader()
                  reader.readAsDataURL(file)
                  reader.onload = () => {
                    // 插入图片到编辑器
                    insertFn(reader.result, file.name, reader.result)
                    resolve({
                      data: {
                        url: reader.result,
                        alt: file.name,
                        href: reader.result
                      }
                    })
                  }
                  reader.onerror = () => {
                    reject(new Error('图片读取失败'))
                  }
                } catch (error) {
                  reject(error)
                }
              })
            },
            maxFileSize: 10 * 1024 * 1024, // 10M
            allowedFileTypes: ['image/*', 'image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            // 启用base64
            base64LimitSize: 5 * 1024 * 1024, // 5M以下的图片转base64
            customInsert(res, insertFn) {
              // 自定义插入
              const url = res.data?.url || res
              const alt = res.data?.alt || 'image'
              const href = res.data?.href || url
              insertFn(url, alt, href)
            }
          },
          // 插入图片配置 - 允许base64图片
          insertImage: {
            checkImage(image, src, alt, href) {
              // 允许所有图片，包括base64
              return true
            }
          },
          // 代码语言选择
          codeSelectLang: {
            codeLangs: [
              { text: 'HTML', value: 'html' },
              { text: 'XML', value: 'xml' },
              { text: 'CSS', value: 'css' },
              { text: 'JavaScript', value: 'javascript' },
              { text: 'TypeScript', value: 'typescript' },
              { text: 'Vue', value: 'vue' },
              { text: 'JSON', value: 'json' },
              { text: 'Java', value: 'java' },
              { text: 'Python', value: 'python' },
              { text: 'SQL', value: 'sql' },
              { text: 'Bash', value: 'bash' },
              { text: 'Plain text', value: 'text' }
            ]
          }
        },
        // 使用防抖的onChange
        onChange: (editor) => {
          if (ignoreNextChange) return
          
          const html = editor.getHtml()
          // 只有当内容确实发生变化时才emit
          if (html !== lastHtml) {
            lastHtml = html
            emit('update:modelValue', html)
            emit('change', html)
          }
        },
        onCreated: () => {
          // 初始设置内容
          lastHtml = props.modelValue || ''
          ignoreNextChange = true
          editor.setHtml(lastHtml)
          
          // 添加点击事件监听
          editorRef.value.addEventListener('click', handleEditorClick)
          editorRef.value.addEventListener('mousedown', handleEditorMouseDown)
          editorRef.value.addEventListener('keyup', handleEditorKeyup)
          editorRef.value.addEventListener('keydown', handleEditorKeydown, true)

          // 短暂延迟后重置标志
          setTimeout(() => {
            ignoreNextChange = false
          }, 100)
        },
        onDestroyed: () => {
          console.log('编辑器已销毁')
          // 清理事件监听
          editorRef.value.removeEventListener('click', handleEditorClick)
          editorRef.value.removeEventListener('mousedown', handleEditorMouseDown)
          editorRef.value.removeEventListener('keyup', handleEditorKeyup)
          editorRef.value.removeEventListener('keydown', handleEditorKeydown, true)
          closeMention()
        }
      }
      
      // 创建编辑器
      editor = createEditor({
        selector: editorRef.value,
        config: editorConfig,
        mode: 'default'
      })
      
      // 完整工具栏配置
      const toolbarConfig = {
        excludeKeys: [], // 不排除任何按键
        toolbarKeys: [
          // 字体样式
          'headerSelect',
          '|',
          'bold',
          'underline',
          'italic',
          'through',
          'code',
          'sup',
          'sub',
          'clearStyle',
          '|',
          'color',
          'bgColor',
          '|',
          
          // 字体设置
          'fontSize',
          'fontFamily',
          'lineHeight',
          '|',
          
          // 段落和列表
          'bulletedList',
          'numberedList',
          'todo',
          'justifyLeft',
          'justifyRight',
          'justifyCenter',
          'justifyJustify',
          'indent',
          'delIndent',
          '|',
          
          // 插入元素
          'emotion',
          'insertLink',
          {
            key: 'group-image',
            title: '图片',
            iconSvg: '<svg viewBox="0 0 1024 1024"><path d="M959.877 128l0.123 0.123v767.775l-0.123 0.122H64.102l-0.122-0.122V128.123l0.122-0.123h895.775zM960 64H64C28.795 64 0 92.795 0 128v768c0 35.205 28.795 64 64 64h896c35.205 0 64-28.795 64-64V128c0-35.205-28.795-64-64-64zM832 288.01c0 53.023-42.988 96.01-96.01 96.01s-96.01-42.987-96.01-96.01S682.967 192 735.99 192 832 234.988 832 288.01zM896 832H128V704l224-384 256 320h64l224-192z"></path></svg>',
            menuKeys: ['uploadImage', 'insertImage']
          },
          'insertVideo',
          'insertTable',
          'codeBlock',
          'divider',
          '|',
          
          // 其他功能
          'undo',
          'redo',
          'fullScreen'
        ]
      }
      
      // 创建工具栏
      toolbar = createToolbar({
        editor,
        selector: toolbarRef.value,
        config: toolbarConfig,
        mode: 'default'
      })
    }
    
    // 处理编辑器点击事件
    const handleEditorClick = (e) => {
      // 点击编辑器内容时，若@提及浮层处于打开状态则关闭（选择已改变）
      if (mentionVisible.value) closeMention()
      if (editor && !editor.isFocused()) {
        // 延迟设置焦点，确保点击事件完成
        setTimeout(() => {
          if (editor) {
            editor.focus(true) // 强制聚焦
          }
        }, 0)
      }
    }
    
    // 处理编辑器鼠标按下事件
    const handleEditorMouseDown = (e) => {
      // 阻止默认行为可能有助于保持焦点
      e.stopPropagation()
    }
    
    // 监听值变化 - 简化逻辑
    watch(() => props.modelValue, (newVal) => {
      if (!editor) return
      
      const currentHtml = editor.getHtml()
      // 只有当新值确实不同时才更新
      if (newVal !== currentHtml && newVal !== lastHtml) {
        // 保存当前是否有焦点
        const hasFocus = editor.isFocused()
        
        // 设置标志，避免触发change事件
        ignoreNextChange = true
        
        // 立即设置内容
        editor.setHtml(newVal)
        lastHtml = newVal
        
        // 如果之前有焦点，恢复焦点
        if (hasFocus) {
          // 使用setTimeout确保DOM更新完成
          setTimeout(() => {
            if (editor) {
              editor.focus(true)
            }
          }, 10)
        }
        
        // 短暂延迟后重置标志
        setTimeout(() => {
          ignoreNextChange = false
        }, 50)
      }
    }, { deep: true })
    
    // 监听高度变化
    watch(() => props.height, () => {
      nextTick(() => {
        if (editor) {
          editor.restoreSelection()
        }
      })
    })
    
    // 监听disabled状态变化
    watch(() => props.disabled, (newVal) => {
      if (editor) {
        if (newVal) {
          editor.disable()
        } else {
          editor.enable()
        }
      }
    })
    
    // 初始化
    onMounted(() => {
      nextTick(() => {
        initEditor()
      })
    })
    
    // 清理
    onBeforeUnmount(() => {
      // 清理事件监听
      if (editorRef.value) {
        editorRef.value.removeEventListener('click', handleEditorClick)
        editorRef.value.removeEventListener('mousedown', handleEditorMouseDown)
        editorRef.value.removeEventListener('keyup', handleEditorKeyup)
        editorRef.value.removeEventListener('keydown', handleEditorKeydown, true)
      }
      closeMention()
      
      if (toolbar) {
        toolbar.destroy()
        toolbar = null
      }
      if (editor) {
        editor.destroy()
        editor = null
      }
    })
    
    // 暴露方法
    const getContent = () => {
      return editor ? editor.getHtml() : ''
    }
    
    const getTextContent = () => {
      return editor ? editor.getText() : ''
    }
    
    const setContent = (content) => {
      if (editor) {
        ignoreNextChange = true
        editor.setHtml(content)
        lastHtml = content
        // 短暂延迟后重置标志
        setTimeout(() => {
          ignoreNextChange = false
        }, 50)
      }
    }
    
    const clearContent = () => {
      if (editor) {
        ignoreNextChange = true
        editor.clear()
        lastHtml = ''
        // 短暂延迟后重置标志
        setTimeout(() => {
          ignoreNextChange = false
        }, 50)
      }
    }
    
    const getEditorInstance = () => {
      return editor
    }
    
    const insertHtml = (html) => {
      if (editor) {
        editor.insertHtml(html)
      }
    }
    
    const insertText = (text) => {
      if (editor) {
        editor.insertText(text)
      }
    }
    
    const insertImage = (src, alt = '', href = '') => {
      if (editor) {
        editor.insertImage({
          src,
          alt,
          href,
          style: { maxWidth: '100%' }
        })
      }
    }
    
    const disable = () => {
      if (editor) {
        editor.disable()
      }
    }
    
    const enable = () => {
      if (editor) {
        editor.enable()
        // 尝试恢复焦点
        setTimeout(() => {
          if (editor) {
            editor.focus(true)
          }
        }, 10)
      }
    }
    
    const isDisabled = () => {
      return editor ? editor.isDisabled() : true
    }
    
    // 专门处理图片上传的方法
    const uploadImage = (file) => {
      return new Promise((resolve, reject) => {
        if (!editor) {
          reject(new Error('编辑器未初始化'))
          return
        }
        
        const reader = new FileReader()
        reader.onload = (e) => {
          const base64Data = e.target.result
          editor.insertImage({
            src: base64Data,
            alt: file.name,
            style: { maxWidth: '100%' }
          })
          resolve(base64Data)
        }
        reader.onerror = () => {
          reject(new Error('图片读取失败'))
        }
        reader.readAsDataURL(file)
      })
    }
    
    // 手动触发焦点
    const focus = () => {
      if (editor) {
        editor.focus(true)
      }
    }
    
    // 手动触发失焦
    const blur = () => {
      if (editor) {
        editor.blur()
      }
    }
    
    return {
      editorRef,
      toolbarRef,
      containerHeight,
      getContent,
      getTextContent,
      setContent,
      clearContent,
      getEditorInstance,
      insertHtml,
      insertText,
      insertImage,
      disable,
      enable,
      isDisabled,
      uploadImage,
      focus,
      blur,
      // 内联 @ 提及
      mentionVisible,
      mentionActiveIndex,
      filteredMentionUsers,
      panelStyle,
      selectMention
    }
  },
  
  // 选项式API兼容
  methods: {
    getContent() {
      return this.getContent?.() || ''
    },
    
    getTextContent() {
      return this.getTextContent?.() || ''
    },
    
    setContent(content) {
      this.setContent?.(content)
    },
    
    clearContent() {
      this.clearContent?.()
    },
    
    getEditorInstance() {
      return this.getEditorInstance?.() || null
    },
    
    insertHtml(html) {
      this.insertHtml?.(html)
    },
    
    insertText(text) {
      this.insertText?.(text)
    },
    
    insertImage(src, alt, href) {
      this.insertImage?.(src, alt, href)
    },
    
    disable() {
      this.disable?.()
    },
    
    enable() {
      this.enable?.()
    },
    
    isDisabled() {
      return this.isDisabled?.() || true
    },
    
    uploadImage(file) {
      return this.uploadImage?.(file)
    },
    
    focus() {
      this.focus?.()
    },
    
    blur() {
      this.blur?.()
    }
  }
}
</script>

<style scoped>
.full-text-editor {
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  background: white;
  display: flex;
  flex-direction: column;
}

#editor-toolbar {
  border-bottom: 1px solid #e8e8e8;
  background: #fafafa;
  padding: 5px 10px;
  min-height: 46px;
  flex-shrink: 0;
  z-index: 10;
}

#editor-content {
  flex: 1;
  min-height: v-bind('minHeight + "px"');
  max-height: v-bind('maxHeight + "px"');
  overflow-y: auto;
  padding: 10px 15px;
  position: relative;
  cursor: text;
}

/* 工具栏样式优化 */
:deep(.w-e-bar) {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: center !important;
  gap: 2px !important;
  background: transparent !important;
}

:deep(.w-e-bar-item) {
  margin: 0 !important;
  border-radius: 3px !important;
}

:deep(.w-e-bar-item:hover) {
  background-color: #f0f0f0 !important;
}

:deep(.w-e-bar-item button) {
  padding: 6px 8px !important;
}

:deep(.w-e-bar-divider) {
  margin: 0 4px !important;
}

/* 编辑器内容区域样式 - 确保编辑器区域可以正确获取焦点 */
:deep(.w-e-text-container) {
  min-height: calc(v-bind('minHeight') - 60px) !important;
  max-height: calc(v-bind('maxHeight') - 60px) !important;
  outline: none !important;
  position: relative !important;
  z-index: 1 !important;
  cursor: text !important;
}

:deep(.w-e-text) {
  min-height: calc(v-bind('minHeight') - 80px) !important;
  padding: 8px 0 !important;
  outline: none !important;
  cursor: text !important;
}

:deep(.w-e-text-container:focus) {
  outline: none !important;
}

:deep(.w-e-text:focus) {
  outline: none !important;
}

/* 确保编辑器内容区域可以点击获取焦点 */
:deep([data-w-e-textarea="true"]) {
  outline: none !important;
  min-height: calc(v-bind('minHeight') - 100px) !important;
  cursor: text !important;
  user-select: text !important;
  -webkit-user-select: text !important;
}

/* 图片样式 */
:deep(.w-e-text img) {
  max-width: 100% !important;
  height: auto !important;
  cursor: pointer !important;
  display: block !important;
  margin: 8px 0 !important;
}

/* 表格样式 */
:deep(.w-e-text table) {
  border-collapse: collapse;
  width: 100%;
}

:deep(.w-e-text table td),
:deep(.w-e-text table th) {
  border: 1px solid #ddd;
  padding: 8px;
}

/* 代码块样式 */
:deep(.w-e-text pre) {
  background-color: #f5f5f5;
  border-radius: 4px;
  padding: 12px;
  overflow-x: auto;
}

:deep(.w-e-text code) {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', monospace;
}

/* 全屏模式 */
:deep(.w-e-full-screen-container) {
  z-index: 99999 !important;
}

:deep(.w-e-full-screen-editor) {
  background: white !important;
}

/* 修复编辑区域光标和焦点问题 */
:deep(.w-e-text-container [contenteditable="true"]) {
  outline: none !important;
  caret-color: #1890ff !important;
  user-select: text !important;
  -webkit-user-select: text !important;
  cursor: text !important;
}

:deep(.w-e-text-container [contenteditable="true"]:focus) {
  outline: none !important;
  box-shadow: none !important;
}

/* 确保编辑器内容区域不会阻止事件 */
:deep(.w-e-scroll) {
  cursor: text !important;
  user-select: text !important;
  -webkit-user-select: text !important;
}

/* 覆盖可能阻止事件的样式 */
:deep(.w-e-text-container *) {
  pointer-events: auto !important;
}

/* 修复占位符样式 */
:deep(.placeholder) {
  pointer-events: none !important;
}

/* ============ 内联 @ 提及浮层 ============ */
.ft-mention-panel {
  position: fixed;
  z-index: 9999;
  width: 220px;
  max-height: 280px;
  overflow-y: auto;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.14);
  padding: 6px;
  box-sizing: border-box;
}
.ft-mention-empty {
  padding: 12px;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
}
.ft-mention-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s ease;
}
.ft-mention-item.active {
  background: #eef2ff;
}
.ft-mention-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ft-mention-name {
  font-size: 14px;
  color: #334155;
  font-weight: 500;
}
</style>

<style>
/* 引入wangeditor样式 */
@import '@wangeditor/editor/dist/css/style.css';

/* 修复弹窗问题 */
.w-e-menu-tooltip,
.w-e-drop-panel,
.w-e-modal {
  z-index: 9999 !important;
}

/* 自定义表情面板样式 */
.w-e-panel-container-emotion {
  width: 400px !important;
  max-height: 300px !important;
  overflow-y: auto !important;
}

/* 链接编辑框样式 */
.w-e-modal {
  min-width: 400px !important;
}

.w-e-modal .btn-container {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 16px;
}

/* 代码语言选择器样式 */
.w-e-select-list {
  max-height: 200px !important;
  overflow-y: auto !important;
}

/* 图片悬浮工具栏 */
.w-e-hover-bar {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1) !important;
  border-radius: 4px !important;
}

/* 表格悬浮工具栏 */
.w-e-table-hover-bar {
  z-index: 1000 !important;
}

/* 调整工具栏下拉菜单 */
.w-e-drop-panel {
  border-radius: 4px !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1) !important;
  border: 1px solid #e8e8e8 !important;
}

/* 图片上传相关样式 */
.w-e-upload-container {
  border: 2px dashed #d9d9d9 !important;
  border-radius: 6px !important;
  padding: 40px 20px !important;
  text-align: center !important;
  background-color: #fafafa !important;
  cursor: pointer !important;
  transition: border-color 0.3s !important;
}

.w-e-upload-container:hover {
  border-color: #1890ff !important;
}

.w-e-upload-icon {
  font-size: 48px !important;
  color: #999 !important;
  margin-bottom: 16px !important;
}

.w-e-upload-text {
  color: #666 !important;
  font-size: 14px !important;
}

/* 修复编辑器焦点问题 */
.w-e-text-container {
  user-select: text !important;
  -webkit-user-select: text !important;
  position: relative !important;
  cursor: text !important;
}

/* 确保编辑器可以正确响应点击事件 */
.w-e-scroll {
  cursor: text !important;
  position: relative !important;
  z-index: 1 !important;
}

/* 重要：防止编辑器内容区域被阻止点击 */
.w-e-text-container * {
  pointer-events: auto !important;
}

/* 确保光标可见 */
.w-e-text-container [contenteditable="true"] {
  caret-color: #1890ff !important;
}

/* 修复可能影响焦点的样式 */
.w-e-text-container .placeholder {
  pointer-events: none !important;
}
</style>