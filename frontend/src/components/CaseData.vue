<template>
  <div class="case-params-container">
    <el-dialog
      v-model="exportApiVisible"
      title="导入列数据"
      width="800"
      :append-to-body="true"
      :show-close="true"
      class="import-dialog"
      @closed="handleDialogClosed"
    >
      <div class="import-content">
        <div class="import-header">
          <span class="import-tip">导入格式：每行一个值（value1 换行 value2）</span>
        </div>
        <v-ace-editor
          v-model:value="exportJson"
          lang="json"
          theme="chrome"
          style="height: 350px; border-radius: 4px; border: 1px solid #dcdfe6;"
          :options="editOption"
        />
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="exportApiVisible = false">取消</el-button>
          <el-button type="primary" @click="exportParamsFunc">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="explainVisible"
      title="编辑变量名称"
      width="500"
      :append-to-body="true"
      :show-close="true"
      class="variable-dialog"
      @closed="handleDialogClosed"
    >
      <div class="variable-content">
        <div class="input-header">
          <span class="input-label">变量名称</span>
          <span class="input-tip">（只能输入英文、数字和下划线）</span>
        </div>
        <el-input
          v-model="edit_params_name"
          :autosize="{ minRows: 1 }"
          @input="handleInput"
          class="variable-input"
          size="large"
          placeholder="请输入变量名称"
          clearable
        />
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="explainVisible = false">取消</el-button>
          <el-button type="primary" @click="saveExplainValue">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <div class="case-params-wrapper">
      <div class="table-header">
        <div class="table-title">
          <span class="title-text">参数列表</span>
          <span class="title-sub">（共 {{ tableData.length }} 条数据）</span>
        </div>
        <div class="table-actions">
          <el-tooltip content="新增行" placement="top">
            <el-button :icon="Plus" size="small" circle @click="pushJsonParams" />
          </el-tooltip>
          <el-tooltip content="删除全部" placement="top">
            <el-button :icon="Delete" size="small" circle @click="delAllJsonParams" type="danger" />
          </el-tooltip>
        </div>
      </div>

      <div class="table-container">
        <vxe-table
          border
          stripe
          header-align="center"
          height="600"
          :column-config="{ resizable: true }"
          :row-config="{ height: 60, drag: true, keyField: 'id' }"
          :edit-config="{ trigger: 'click', mode: 'cell', showIcon: false, autoClear: false }"
          :scroll-y="{ enabled: true, gt: 0, mode: 'wheel', oSize: 30, threshold: 0 }"
          :checkbox-config="{ checkField: 'is_required' }"
          show-overflow
          :data="tableData"
          class="params-table"
          @cell-change="handleCellChange"
        >
          <!-- 空数据时的提示 -->
          <template #empty>
            <div class="empty-tips">
              <el-icon class="empty-icon"><InfoFilled /></el-icon>
              <div class="empty-text">
                <p>暂无数据</p>
                <p class="empty-sub">点击上方按钮添加数据，关闭弹窗会自动保存</p>
              </div>
            </div>
          </template>
          
          <vxe-column type="seq" width="70" align="center" title="序号" fixed="left" />

          <vxe-column
            field="_name_"
            width="400"
            tree-node
            header-align="left"
            :edit-render="{ autofocus: true, placeholder: '请输入数据用例名称' }"
          >
            <template #header>
              <div class="column-header">
                <span>数据用例名称</span>
                <el-tooltip content="数据用例的名称，支持函数和变量" placement="top">
                  <el-icon class="header-icon"><InfoFilled /></el-icon>
                </el-tooltip>
              </div>
            </template>
            <template #edit="{ row, rowIndex }">
              <FuncAndParams
                :bind_case_data="params_columns"
                :value="row._name_"
                :row="row"
                :is_case_params="true"
                :step_index="step_index"
                :steps="steps"
                :index="rowIndex"
                :bind_env_params="bind_env_params"
                :bind_global_params="bind_global_params"
                :case_table_data="case_params_data"
                :func_list="func_list"
                @update:value="handleUpdateName(row, $event)"
              />
            </template>
          </vxe-column>

          <vxe-column
            v-for="(column_name, index) in params_columns"
            :key="column_name"
            header-align="left"
            :field="column_name"
            min-width="250"
            :edit-render="{ autofocus: true, placeholder: '请输入变量值' }"
          >
            <template #header>
              <div class="column-header">
                <span class="column-name">{{ column_name }}</span>
                <el-dropdown
                  trigger="click"
                  @command="(command) => handleCommand(command, index)"
                  class="column-dropdown"
                >
                  <el-icon class="dropdown-icon">
                    <MoreFilled />
                  </el-icon>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="1">
                        <el-icon><Edit /></el-icon>
                        <span>编辑列名</span>
                      </el-dropdown-item>
                      <el-dropdown-item command="2">
                        <el-icon><ArrowLeft /></el-icon>
                        <span>向左插入列</span>
                      </el-dropdown-item>
                      <el-dropdown-item command="3">
                        <el-icon><ArrowRight /></el-icon>
                        <span>向右插入列</span>
                      </el-dropdown-item>
                      <el-dropdown-item command="4" divided class="danger-item">
                        <el-icon><Delete /></el-icon>
                        <span>删除列</span>
                      </el-dropdown-item>
                      <el-dropdown-item command="5">
                        <el-icon><Upload /></el-icon>
                        <span>导入数据</span>
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
            <template #edit="{ row, rowIndex }">
              <FuncAndParams
                :bind_case_data="params_columns"
                :value="row[column_name]"
                :row="row"
                :is_case_data="true"
                :is_case_params="true"
                :step_index="step_index"
                :steps="steps"
                :index="rowIndex"
                :bind_env_params="bind_env_params"
                :bind_global_params="bind_global_params"
                :case_table_data="case_params_data"
                :func_list="func_list"
                @update:value="handleUpdateValue(row, column_name, $event)"
              />
            </template>
          </vxe-column>

          <vxe-column title="操作" width="120" header-align="center" fixed="right" align="center">
            <template #default="{ row }">
              <div class="row-actions">
                <el-tooltip content="新增行" placement="top">
                  <el-button
                    :icon="Plus"
                    size="small"
                    circle
                    @click="addJsonParams(row)"
                    class="action-btn"
                  />
                </el-tooltip>
                <el-tooltip content="删除行" placement="top">
                  <el-button
                    :icon="Delete"
                    size="small"
                    circle
                    @click="delJsonParams(row)"
                    class="action-btn danger"
                  />
                </el-tooltip>
              </div>
            </template>
          </vxe-column>
        </vxe-table>
      </div>

      <div class="table-footer">
        <div class="footer-tips">
          <el-icon><InfoFilled /></el-icon>
          <span>提示：数据会实时保存，关闭弹窗后数据将自动同步</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { VAceEditor } from 'vue3-ace-editor'
import 'ace-builds/src-noconflict/snippets/json'
import 'ace-builds/src-noconflict/mode-json'
import 'ace-builds/src-noconflict/snippets/python'
import 'ace-builds/src-noconflict/mode-python'
import 'ace-builds/src-noconflict/theme-chrome'
import 'ace-builds/src-noconflict/theme-monokai'
import 'ace-builds/src-noconflict/ext-language_tools'
import ace from 'ace-builds'
import { ElMessage, ElMessageBox } from 'element-plus'
import { v4 as uuidv4 } from 'uuid'
import { mapState } from 'vuex'
import FuncAndParams from './FuncAndParams.vue'
import {
  Delete,
  Plus,
  EditPen,
  CopyDocument,
  Menu,
  UploadFilled,
  InfoFilled,
  Edit,
  ArrowLeft,
  ArrowRight,
  Upload,
} from '@element-plus/icons-vue'

ace.config.set(
  'basePath',
  'https://cdn.jsdelivr.net./npm/ace-builds@' +
    require('ace-builds').version +
    '/src-noconflict/'
)

export default {
  name: 'CaseParamsTable',
  
  computed: {
    ...mapState(['projectInfo']),
  },
  
  components: {
    FuncAndParams,
    VAceEditor,
  },
  
  props: {
    tableData: {
      type: Array,
      default: () => [],
    },
    params_columns: {
      type: Array,
      default: () => [],
    },
    isApi: {
      default: true,
    },
    apiJson: {
      type: Array,
      default: () => [],
    },
    func_list: {
      type: Array,
      default: () => [],
    },
    bind_env_params: {
      type: Array,
      default: () => [],
    },
     bind_global_params: {
      type: Array,
      default: () => [],
    },
    case_params_data: {
      type: Array,
      default: () => [],
    },
    steps: {
      type: Array,
      default: () => [],
    },
    step_index: {
      type: Number,
      default: 0,
    },
  },
  
  setup() {
    return {
      Delete,
      Plus,
      EditPen,
      UploadFilled,
      Menu,
      InfoFilled,
      Edit,
      ArrowLeft,
      ArrowRight,
      Upload,
    }
  },
  
  data() {
    return {
      exampleVisible: false,
      loadApiVisible: false,
      explainVisible: false,
      funcVisible: false,
      exportVisible: false,
      exportApiVisible: false,
      show_close: false,
      // 编辑参数说明和参数示例的临时变量
      commond_data: '',
      is_add_params: false,
      edit_params_name: '',
      func_values: [],
      // 设置动态函数时的临时变量
      boolean_list: [true, false],
      column_index: -1,
      json_params: {
        id: uuidv4(),
        _name_: '',
      },
      editOption: {
        fontSize: 14,
        showLineNumbers: true,
        showPrintMargin: false,
        tabSize: 2,
        useWorker: false,
      },
      exportJson: '',
      // 用于标记是否需要更新父组件数据
      updateFlag: false,
      // 记录是否有数据修改
      dataChanged: false,
    }
  },
  
  methods: {
    handleInput(value) {
      // 使用正则表达式替换非英文、数字、下划线的字符
      this.edit_params_name = value.replace(/[^a-zA-Z0-9_]/g, '')
    },
    
    handleCommand(command, index) {
      if (command === '1') {
        this.is_add_params = false
        this.explainVisible = true
        this.column_index = index
        this.edit_params_name = this.params_columns[index]
      } else if (command === '2') {
        this.commond_data = '2'
        this.is_add_params = true
        this.explainVisible = true
        this.column_index = index
        this.edit_params_name = ''
      } else if (command === '3') {
        this.commond_data = '3'
        this.is_add_params = true
        this.explainVisible = true
        this.column_index = index
        this.edit_params_name = ''
      } else if (command === '4') {
        if (this.params_columns.length === 1) {
          ElMessage({
            type: 'error',
            message: '至少保留一列',
          })
        } else {
          ElMessageBox.confirm('确定要删除这一列吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          })
            .then(() => {
              const columnName = this.params_columns[index]
              this.params_columns.splice(index, 1)
              
              // 删除每行对应的列数据
              this.tableData.forEach(row => {
                if (row.hasOwnProperty(columnName)) {
                  delete row[columnName]
                }
              })
              
              ElMessage({
                type: 'success',
                message: '删除成功',
              })
              this.dataChanged = true
              this.triggerUpdate()
            })
            .catch(() => {})
        }
      } else if (command === '5') {
        this.exportApiVisible = true
        this.column_index = index
        this.exportJson = ''
      }
    },
    
    handleUpdateValue(row, column_name, newValue) {
      row[column_name] = newValue
      this.dataChanged = true
      this.triggerUpdate()
    },
    
    handleUpdateName(row, newValue) {
      row._name_ = newValue
      this.dataChanged = true
      this.triggerUpdate()
    },
    
    // 处理单元格变化事件
    handleCellChange() {
      this.dataChanged = true
      this.triggerUpdate()
    },
    
    // 触发数据更新事件
    triggerUpdate() {
      if (!this.updateFlag) {
        this.updateFlag = true
        // 使用$nextTick确保DOM更新完成后再触发事件
        this.$nextTick(() => {
          this.$emit('update:tableData', [...this.tableData])
          this.$emit('update:params_columns', [...this.params_columns])
          this.updateFlag = false
        })
      }
    },
    
    typeChange(row) {
      if (row.type === 'object' || row.type === 'array') {
        row.value = ''
        this.dataChanged = true
        this.triggerUpdate()
      }
    },
    
    pushJsonParams() {
      const newRow = {
        id: uuidv4(),
        _name_: `用例${this.tableData.length + 1}`,
      }
      // 为新行添加所有列的空值
      this.params_columns.forEach((col) => {
        newRow[col] = ''
      })
      this.tableData.push(newRow)
      this.dataChanged = true
      this.triggerUpdate()
    },
    
    findAllChildrenIndexes(data, parentId, indexes = []) {
      data.forEach((item, index) => {
        if (item.parentId === parentId) {
          indexes.push(index)
          this.findAllChildrenIndexes(data, item.id, indexes)
        }
      })
      return indexes
    },
    
    delJsonParams(row) {
      ElMessageBox.confirm('确定要删除这一行吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })
        .then(() => {
          const childrenIndexes = this.findAllChildrenIndexes(this.tableData, row.id)
          // 先删除子行（从后往前删）
          for (let i = childrenIndexes.length - 1; i >= 0; i--) {
            this.tableData.splice(childrenIndexes[i], 1)
          }
          // 再删除父行
          const parentIndex = this.findIndexById(this.tableData, row.id)
          if (parentIndex !== -1) {
            this.tableData.splice(parentIndex, 1)
          }
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
          this.dataChanged = true
          this.triggerUpdate()
        })
        .catch(() => {})
    },
    
    delAllJsonParams() {
      if (this.tableData.length === 0) {
        ElMessage({
          type: 'warning',
          message: '当前没有数据可删除',
        })
        return
      }

      ElMessageBox.confirm('确定要删除全部数据吗？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })
        .then(() => {
          this.tableData.splice(0, this.tableData.length)
          ElMessage({
            type: 'success',
            message: '已删除全部数据',
          })
          this.dataChanged = true
          this.triggerUpdate()
        })
        .catch(() => {})
    },
    
    addJsonParams(row) {
      const index = this.findIndexById(this.tableData, row.id)
      if (index !== -1) {
        const newRow = {
          id: uuidv4(),
          _name_: `用例${this.tableData.length + 1}`,
        }
        // 为新行添加所有列的空值
        this.params_columns.forEach((col) => {
          newRow[col] = ''
        })
        this.tableData.splice(index + 1, 0, newRow)
        this.dataChanged = true
        this.triggerUpdate()
      }
    },
    
    findIndexById(items, id) {
      return items.findIndex((item) => item.id === id)
    },
    
    exportParamsFunc() {
      if (this.column_index === -1 || !this.params_columns[this.column_index]) {
        ElMessage({
          type: 'error',
          message: '请先选择要导入数据的列',
        })
        return
      }

      const columnName = this.params_columns[this.column_index]
      
      if (!this.exportJson.trim()) {
        ElMessage({
          type: 'error',
          message: '请输入要导入的数据',
        })
        return
      }

      try {
        const lines = this.exportJson.split('\n')
        const values = lines
          .map((line) => line.trim())
          .filter((line) => line.length > 0)

        if (values.length === 0) {
          ElMessage({
            type: 'error',
            message: '没有找到有效数据',
          })
          return
        }

        // 如果当前数据行数少于导入的数据，则补充新行
        if (this.tableData.length < values.length) {
          const neededRows = values.length - this.tableData.length
          for (let i = 0; i < neededRows; i++) {
            const newRow = {
              id: uuidv4(),
              _name_: `用例${this.tableData.length + 1}`,
            }
            this.params_columns.forEach((col) => {
              newRow[col] = ''
            })
            this.tableData.push(newRow)
          }
        }

        // 填充数据
        values.forEach((value, index) => {
          if (index < this.tableData.length) {
            this.tableData[index][columnName] = value
          }
        })

        ElMessage({
          type: 'success',
          message: `成功导入 ${values.length} 条数据`,
        })
        this.exportApiVisible = false
        this.exportJson = ''
        this.dataChanged = true
        this.triggerUpdate()
      } catch (e) {
        console.error('导入数据错误:', e)
        ElMessage({
          type: 'error',
          message: '导入数据格式错误',
        })
      }
    },
    
    saveExplainValue() {
      if (this.edit_params_name === '') {
        ElMessage({
          type: 'error',
          message: '请输入变量名称',
        })
        return
      }

      const findIndex = this.params_columns.indexOf(this.edit_params_name)

      if (this.is_add_params) {
        if (findIndex === -1) {
          const oldColumnName = this.params_columns[this.column_index]
          const newColumnName = this.edit_params_name
          
          if (this.commond_data === '2') {
            // 向左插入列
            this.params_columns.splice(this.column_index, 0, newColumnName)
            // 为新列添加空值
            this.tableData.forEach(row => {
              row[newColumnName] = ''
            })
          } else {
            // 向右插入列
            this.params_columns.splice(this.column_index + 1, 0, newColumnName)
            // 为新列添加空值
            this.tableData.forEach(row => {
              row[newColumnName] = ''
            })
          }
          
          ElMessage({
            type: 'success',
            message: '添加列成功',
          })
          this.explainVisible = false
          this.dataChanged = true
          this.triggerUpdate()
        } else {
          ElMessage({
            type: 'error',
            message: '变量名称已存在',
          })
        }
      } else {
        // 编辑列名
        if (findIndex === -1 || findIndex === this.column_index) {
          const oldColumnName = this.params_columns[this.column_index]
          const newColumnName = this.edit_params_name
          
          // 更新列名
          this.params_columns[this.column_index] = newColumnName
          
          // 更新每行的数据键名
          this.tableData.forEach(row => {
            if (row.hasOwnProperty(oldColumnName)) {
              row[newColumnName] = row[oldColumnName]
              delete row[oldColumnName]
            }
          })
          
          ElMessage({
            type: 'success',
            message: '修改列名成功',
          })
          this.explainVisible = false
          this.dataChanged = true
          this.triggerUpdate()
        } else {
          ElMessage({
            type: 'error',
            message: '变量名称已存在',
          })
        }
      }
    },
    
    // 对话框关闭事件
    handleDialogClosed() {
      this.edit_params_name = ''
      this.column_index = -1
      this.commond_data = ''
      this.is_add_params = false
      this.exportJson = ''
    },
    
    // 组件销毁前的钩子，用于提示用户
    beforeUnmount() {
      if (this.dataChanged) {
        ElMessage({
          type: 'success',
          message: '数据已自动保存',
          duration: 2000,
        })
      }
    },
    
    expandAllEvent() {
      const $table = this.$refs.tableRef
      if ($table) {
        $table.setAllTreeExpand(true)
      }
    },
    
    async getPlantElement() {
      const response = await this.$api.getAllPlantElement({ project: this.projectInfo.id })
      if (response.status === 200) {
        this.loc_list = response.data.results
      }
    },
  },
  
  // 如果父组件关闭弹窗会触发组件的销毁，我们可以在销毁前提示
  mounted() {
    // 监听父组件可能的关闭事件（如果父组件是弹窗）
    window.addEventListener('beforeunload', this.handleBeforeUnload)
  },
  
  unmounted() {
    window.removeEventListener('beforeunload', this.handleBeforeUnload)
  },
}
</script>

<style scoped>
.case-params-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.case-params-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.table-header {
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e8eaec;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.title-sub {
  font-size: 12px;
  color: #909399;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.table-container {
  flex: 1;
  padding: 16px;
  background: #fff;
  min-height: 200px;
}

.params-table {
  width: 100%;
  border-radius: 4px;
  overflow: hidden;
}

/* 空数据提示样式 */
.empty-tips {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.empty-text p {
  margin: 0;
  line-height: 1.5;
}

.empty-text p:first-child {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #606266;
}

.empty-sub {
  font-size: 13px;
  color: #909399;
}

/* 修复表格边框和输入框布局问题 */
:deep(.vxe-table--render-wrapper) {
  border-radius: 4px;
  overflow: hidden;
}

:deep(.vxe-table--header-wrapper) {
  background: #f5f7fa;
}

:deep(.vxe-header--column) {
  font-weight: 600;
  color: #303133;
  background: #f5f7fa !important;
}

/* 修复单元格内边距和文本对齐 */
:deep(.vxe-body--column) {
  padding: 0 !important;
  text-align: left;
}

:deep(.vxe-cell) {
  min-height: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  width: 100%;
  box-sizing: border-box;
}

/* 修复编辑单元格的布局问题 */
:deep(.vxe-table--edit-cell) {
  padding: 0 !important;
  margin: 0 !important;
  position: relative;
  width: 100%;
  height: 100%;
}

/* 修复输入框布局，确保居中对齐 */
:deep(.vxe-table--edit-cell .el-input),
:deep(.vxe-table--edit-cell .el-textarea),
:deep(.vxe-table--edit-cell .el-select) {
  width: 100% !important;
  height: 100% !important;
  margin: 0;
  padding: 0;
}

/* 修复输入框内部包装器的样式 */
:deep(.vxe-table--edit-cell .el-input__wrapper),
:deep(.vxe-table--edit-cell .el-textarea__inner),
:deep(.vxe-table--edit-cell .el-select__wrapper) {
  width: 100% !important;
  height: 100% !important;
  min-height: 44px;
  border-radius: 0 !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 12px !important;
  margin: 0 !important;
  background-color: transparent !important;
  display: flex !important;
  align-items: center !important;
}

/* 修复输入框内部元素的对齐 */
:deep(.vxe-table--edit-cell .el-input__inner),
:deep(.vxe-table--edit-cell .el-textarea__inner) {
  height: 100% !important;
  line-height: 44px !important;
  padding: 0 !important;
  margin: 0 !important;
  border: none !important;
  background: transparent !important;
  width: 100% !important;
  text-align: left;
}

/* 修复下拉选择器的对齐 */
:deep(.vxe-table--edit-cell .el-select) {
  display: flex !important;
  align-items: center !important;
}

/* 修复输入框在编辑状态下的边框问题 */
:deep(.vxe-table--edit-cell .el-input.is-focus .el-input__wrapper),
:deep(.vxe-table--edit-cell .el-textarea.is-focus .el-textarea__inner),
:deep(.vxe-table--edit-cell .el-select.is-focus .el-select__wrapper) {
  box-shadow: none !important;
  outline: none !important;
}

/* 修复表格边框显示，确保单元格边框统一 */
:deep(.vxe-table.border--default .vxe-header--column),
:deep(.vxe-table.border--default .vxe-body--column) {
  border-right: 1px solid #e8eaec !important;
  border-bottom: 1px solid #e8eaec !important;
}

:deep(.vxe-table.border--default .vxe-body--row:last-child .vxe-body--column) {
  border-bottom: none !important;
}

/* 修复最后一列的边框 */
:deep(.vxe-table.border--default .vxe-header--column:last-child),
:deep(.vxe-table.border--default .vxe-body--column:last-child) {
  border-right: 1px solid #e8eaec !important;
}

/* 修复编辑单元格的边框，防止输入框超出 */
:deep(.vxe-table--edit-cell) {
  border: none !important;
}

/* 修复单元格内编辑状态的背景色 */
:deep(.vxe-table--edit-cell .el-input__wrapper:hover),
:deep(.vxe-table--edit-cell .el-textarea__inner:hover),
:deep(.vxe-table--edit-cell .el-select__wrapper:hover) {
  background-color: #f5f7fa !important;
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0 12px;
  height: 100%;
  min-height: 40px;
}

.column-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 8px;
}

.header-icon {
  margin-right: 10px;
  color: #909399;
  font-size: 14px;
  cursor: help;
}

.column-dropdown {
  margin-left: auto;
  cursor: pointer;
  flex-shrink: 0;
}

.dropdown-icon {
  color: #909399;
  font-size: 16px;
  margin-right: 10px;
  transition: color 0.3s;
  padding: 4px;
}

.dropdown-icon:hover {
  color: #409eff;
  background-color: #f5f7fa;
  border-radius: 4px;
}

:deep(.danger-item) {
  color: #f56c6c;
}

:deep(.danger-item:hover) {
  background-color: #fef0f0;
}

.row-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.action-btn {
  padding: 4px;
}

.action-btn.danger {
  color: #f56c6c;
  border-color: #fbc4c4;
  background-color: #fef0f0;
}

.action-btn.danger:hover {
  background-color: #f56c6c;
  border-color: #f56c6c;
  color: #fff;
}

.table-footer {
  padding: 12px 20px;
  border-top: 1px solid #e8eaec;
  background: #f8f9fa;
}

.footer-tips {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.footer-tips .el-icon {
  font-size: 14px;
}

/* 对话框样式 */
.import-dialog,
.variable-dialog {
  border-radius: 8px;
  overflow: hidden;
}

.import-content,
.variable-content {
  padding: 8px 0;
}

.import-header {
  margin-bottom: 16px;
}

.import-tip {
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.input-header {
  margin-bottom: 12px;
}

.input-label {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.input-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.variable-input {
  width: 100%;
}

.variable-input :deep(.el-input__inner) {
  border-radius: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px 0;
  border-top: 1px solid #e8eaec;
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .table-container {
    padding: 12px;
  }
  
  :deep(.vxe-body--column) {
    padding: 0 !important;
  }
}

@media screen and (max-width: 768px) {
  .case-params-wrapper {
    border-radius: 4px;
  }
  
  .table-header {
    padding: 12px 16px;
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .table-title {
    justify-content: center;
  }
  
  .table-actions {
    justify-content: center;
  }
  
  .table-container {
    padding: 8px;
  }
  
  .row-actions {
    flex-direction: column;
    gap: 4px;
  }
  
  .empty-tips {
    padding: 40px 16px;
  }
  
  .empty-icon {
    font-size: 36px;
  }
}
</style>