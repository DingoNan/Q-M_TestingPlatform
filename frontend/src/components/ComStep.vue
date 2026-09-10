<template>
  <el-drawer class='step' v-model="editDrawerVisible" :title="title" direction="ttb" :show-close='false' :size="600" :close-on-click-modal='false'>
  	<el-tabs :tab-position="position" class="demo-tabs" v-model='activeTable'>
		<el-tab-pane name='Args' v-if='step_type === StepType.PlatformSystemFunction || step_type === StepType.Selenium || step_type ===StepType.UserCustomizeFunction'>
			<template #label>
				<span class="custom-tabs-label">
				  <el-tooltip effect="light">
					  <template #content>
						  <el-row v-for='params_txt in content'>
						  	 <el-text type='primary'>{{ params_txt }}</el-text>
						  </el-row>
					  </template>
					  <span>函数入参(Args)</span>
					  <el-icon style="top: 2.3px; left: 2px"><Warning /></el-icon>
				  </el-tooltip>
				</span>
			</template>
			<Args :keyData='edit_row_data.params' :step_type='step_type' :function_name='edit_row_data.function_name'></Args>
		</el-tab-pane>
		<el-tab-pane v-if='step_type === StepType.Request' label="请求头(Headers)" name='api_headers' >
			<KeyTable :keyData='edit_row_data.api_headers' :loadHeader='loadHeader' :isShowLoadBtn='true'></KeyTable>
		</el-tab-pane>
  		<el-tab-pane v-if='step_type === StepType.Request' label="查询参数(Params)" name='api_params' >
  			<KeyTable :keyData='edit_row_data.api_params' :readOnly='false' :loadHeader='loadParams' :isShowLoadBtn='true'></KeyTable>
  		</el-tab-pane>
  		<el-tab-pane label="请求体(Body)" name='api_body' v-if="step_type === StepType.Request">
  			<el-radio-group v-model="edit_row_data.body_type">
  				<el-radio label="json">json</el-radio>
  				<el-radio label="data">data</el-radio>
  			</el-radio-group>
  			<BodyEdit v-model='edit_row_data.api_body' :isShowLoadBtn='true' :loadBody="loadBody"></BodyEdit>
  		</el-tab-pane>
  		<el-tab-pane label="数据提取(Extract)" name='extract'>
			<Extract v-if="step_type === StepType.Request" :keyData='edit_row_data.extract' :readOnly='false' :isShowLoadBtn='true' :loadExtract="loadExtract"></Extract>
  			<FuncExtract  v-if="step_type != StepType.Request" :keyData='edit_row_data.extract' :readOnly='false'></FuncExtract>
  		</el-tab-pane>
  		<el-tab-pane name='check' label="断言(Check)">
  			<Check :keyData='edit_row_data.check' :readOnly='false' :isShowLoadBtn='true' :loadCheck="loadCheck"></Check>
  		</el-tab-pane>
		<el-tab-pane name='Condition' label="逻辑判断(Condition)" >
			<el-tabs :tab-position="position" class="demo-tabs" v-model='condition_tab'>
				<el-tab-pane name='If' label="执行条件(If)" >
					<IsRun :keyData='edit_row_data.run' :readOnly='false'></IsRun>
				</el-tab-pane>
				<el-tab-pane name='For' label="循环执行(For)" >
					<Loop :keyData='edit_row_data.loop' :readOnly='false'></Loop>
				</el-tab-pane>
				<el-tab-pane name='While' label="一直执行(While)" >
					<Until :keyData='edit_row_data.until' :readOnly='false' :step_after='edit_row_data.step_after'></Until>
				</el-tab-pane>
			</el-tabs>
		</el-tab-pane>
  	</el-tabs>
		<template #footer>
			<span class="dialog-footer">
				<el-button type="primary" @click="cance">取消</el-button>
				<el-button type="primary" @click="submit">确认</el-button>
			</span>
		</template>
  </el-drawer>
  <el-table :data="keyData">
  		<el-table-column label="序号" width="70" type="index"/>
  		<el-table-column label="步骤描述" prop="desc" align="center">
  			<template #default="scope">
  				<el-input v-model="scope.row.desc" style="width: 100%; box-sizing: border-box;" :disabled="readOnly"></el-input>
  			</template>
  		</el-table-column>
  		<el-table-column label="步骤关键字" prop="key" align="center" width="400px">
  			<template #default="scope">
				<el-tooltip effect="dark" content="Bottom Center prompts info" placement="bottom">
					<el-cascader collapse-tags v-model='scope.row.key' :options="actionKeys" :props="editProps" style="width: 100%;" filterable @change="editApiParams(scope.$index, scope.row)"/>
				</el-tooltip>
  			</template>
  		</el-table-column>
  		<el-table-column align="center" width="500px">
			<template #header>
				<el-button :icon="Plus" size="small" type='primary' @click="header_push" :disabled="readOnly">新增</el-button>
			</template>
  			<template #default="scope">
			  <el-button v-if="scope.row.key.length === 0" :icon='Edit' size="small" type='primary' :disabled='true' @click="editApiParams(scope.$index, scope.row)">编辑</el-button>
			  <el-button v-if="scope.row.key.length != 0" :icon='Edit' size="small" type='primary' :disabled="false" @click="editApiParams(scope.$index, scope.row)">编辑</el-button>
  			  <el-button :icon="Plus" size="small" type='primary' @click="addApiParams(scope.$index)" :disabled="readOnly">新增</el-button>
  			  <el-button :icon="CopyDocument" size="small" type='primary' @click="copyApiParams(scope.$index, scope.row)" :disabled="readOnly" >复制</el-button>
  			  <el-button :icon="Top" @click="topApiParams(scope.$index)" size="small" type="primary" :disabled="readOnly">上移</el-button>
  			  <el-button :icon="Bottom" @click="bottomApiParams(scope.$index)" size="small" type="primary" :disabled="readOnly">下移</el-button>
  			  <el-button :icon="Delete" @click="deleteApiParams(scope.$index)" size="small" type="danger" :disabled="readOnly">删除</el-button>
  			</template>
  		</el-table-column>
  </el-table>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, Edit, Plus, EditPen, CopyDocument, Top, Bottom, ArrowDown,  Warning} from '@element-plus/icons-vue'
import BodyEdit from './BodyEdit.vue'
import KeyTable from './KeyTable.vue'
import FuncExtract from './FuncExtract.vue'
import Extract from './Extract.vue'
import Check from './Check.vue'
import Args from './Args.vue'
import Loop from './Loop.vue'
import Until from './Until.vue'
export default{
	components: {
		BodyEdit,
		KeyTable,
		FuncExtract,
		Check,
		Extract,
		Args,
		IsRun,
		Loop,
		Until,
	},
	setup() {
		return {
			Edit,
			Delete,
			Plus,
			View,
			EditPen,
			CopyDocument,
			Top,
			ArrowDown,
			Bottom,
			Warning,
		}
	},
	props: ['keyData', 'readOnly', 'actionKeys'],
	data() {
		return {
			StepType:{
				PlatformSystemFunction: -1,   
				UserCustomizeFunction: 1,     
				Request: 1,                  
				Selenium: 2,                  
				ComStep:3,                 
				UserCustomizeScript: 4
			},
			activeTable: 'Args',
			condition_tab: 'Args',
			editDrawerVisible: false,
			func_doc: '',
			content: '',
			edit_index: -1,
			step_type: '',
			api_id: '',
			apiForm: '',
			json_row_data: {
				desc: '',
				key: [],
				api_headers: [],
				api_body: '',
				step_after: false,
				body_type: 'json',
				api_params: [],
				extract: [],
				check: [],
				run: [],
				loop: [],
				until: [],
				params: [],
				function_name: '',
			},
			edit_row_data: {
				desc: '',
				key: [],
				api_headers: [],
				api_body: '',
				step_after: false,
				body_type: 'json',
				api_params: [],
				extract: [],
				check: [],
				run: [],
				loop: [],
				until: [],
				params: [],
				function_name: '',
			},
			editProps:{
				value: 'id',
				label: 'name',
				emitPath: true,
			},
			bodyType: 'json',
		}
	},
	methods: {
		set_body(){
			if (this.apiForm.json){
				this.edit_row_data.body_type = 'json'
				this.edit_row_data.api_body = this.apiForm.json
			}else{
				this.edit_row_data.body_type = 'data'
				this.edit_row_data.api_body = this.apiForm.data
			}
		},
		async loadExtract(){
			if (!this.apiForm){
				const response = await this.$api.getApi(this.api_id)
				if (response.status === 200){
					this.apiForm = {...response.data.result}
					this.edit_row_data.extract = this.apiForm.extract
				}
			}else{
				this.edit_row_data.extract = this.apiForm.extract
			}
			
			
		},
		 async loadBody(){
			if (!this.apiForm){
				const response = await this.$api.getApi(this.api_id)
				if (response.status === 200){
					this.apiForm = {...response.data.result}
					this.set_body()
				}
			}else{
				this.set_body()
			}
			
			
		},
		async loadParams(){
			if (!this.apiForm){
				const response = await this.$api.getApi(this.api_id)
				if (response.status === 200){
					this.apiForm = {...response.data.result}
					this.edit_row_data.api_params = this.apiForm.params
				}
			}else{
				this.edit_row_data.api_params = this.apiForm.params
				
			}
			
			
		},
		async loadCheck(){
			if (!this.apiForm){
				const response = await this.$api.getApi(this.api_id)
				if (response.status === 200){
					this.apiForm = {...response.data.result}
					this.edit_row_data.check = this.apiForm.check
				}
			}else{
				this.edit_row_data.check = this.apiForm.check
				
			}
			
			
		},
		async loadHeader(){
			if (!this.apiForm){
				const response = await this.$api.getApi(this.api_id)
				if (response.status === 200){
					this.apiForm = {...response.data.result}
					this.getHeader()
				}
			}
			else{
				this.getHeader()
			}
			
			
		},
		async getHeader(){
			const response = await this.$api.getHeader(this.apiForm.headers)
			if (response.status === 200){
				this.edit_row_data.api_headers = response.data.result.value
			}
		},
		async getSystemFunctionDoc(step_type, step_key){
			const response = await this.$api.getSystemFunctionDoc({step_key: step_key})
			if (response.status === 200){
				this.content = response.data.result.doc
				this.edit_row_data.params = response.data.result.params
			}
		},
		cance(){
			this.editDrawerVisible = false
			this.apiForm = ''
		},
		submit(){
			this.editDrawerVisible = false
			this.apiForm = ''
			this.keyData[this.edit_index] = JSON.parse(JSON.stringify(this.edit_row_data))
		},
		header_push(){
			this.keyData.push(JSON.parse(JSON.stringify(this.json_row_data)))
		},
		editApiParams(index, row){
			this.step_type = row.key[0]
			const step_key = row.key[row.key.length - 1]
			console.log(this.edit_row_data.params, 'hehe')
			if (this.step_type === this.StepType.PlatformSystemFunction && this.edit_row_data.params.length ==0){
				this.getSystemFunctionDoc(this.step_type, step_key)
			}
			if (this.step_type === this.StepType.Request){
				this.api_id = row.key[row.key.length - 1]
			}
			if (!this.keyData[index].step_after){
				this.keyData[index].step_after = true
			}
			this.edit_row_data = JSON.parse(JSON.stringify(this.keyData[index]))
			this.edit_row_data.function_name = step_key
			this.edit_index = index
			this.editDrawerVisible = true
		},
		addApiParams(index){
			const row_data = JSON.parse(JSON.stringify(this.json_row_data))
			this.keyData.splice(index + 1, 0, row_data)
		},
		deleteApiParams(index){
			this.keyData.splice(index, 1)
		},
		copyApiParams(index, value){
			const row_data = JSON.parse(JSON.stringify(value))
			this.keyData.splice(index + 1, 0, row_data)
		},
		topApiParams(index){
			if(index !=0){
				const row_data = this.keyData[index - 1]
				this.keyData[index - 1] = this.keyData[index]
				this.keyData[index] = row_data
			}
		},
		bottomApiParams(index){
			if(index != this.keyData.length - 1){
				const row_data = this.keyData[index + 1]
				this.keyData[index + 1] = this.keyData[index]
				this.keyData[index] = row_data
			
			}
		},
	},
	created() {
	}
}

</script>

<style>
	el-button {
		width: 100px;
	}
	.step .el-drawer__header{
		height: 0px !important;
		margin-bottom: 0px !important;
		padding-top: 0px !important;
	}
	
</style>