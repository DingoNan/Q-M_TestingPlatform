<template>
	<el-row style='background-color: var(--qm-bg-2);'>
	   <el-col :span="10">
		   <el-table :data="func_params" empty-text="选择函数自动带出参数" :span-method="spanMethod">
			<el-table-column label="参数名" prop="type" align="center" min-width="150px">
				<template #default="scope">
					<el-input style="width: 100%; box-sizing: border-box;" v-model="scope.row.params_name" disabled></el-input>
				</template>
			</el-table-column>
			<el-table-column label="参数类型" prop="type" align="center" width="150px">
				<template #default="scope">
					<el-select v-model="scope.row.type" style="width: 100%;" disabled>
						<template  v-for="value in type_list">
							<el-option  v-if="(step_type === StepType.Selenium && scope.$index ===0  && value === 'Obj')|| (step_type === StepType.Selenium &&scope.$index !=0)" :label="value" :value="value" ></el-option>
							<el-option  v-if="(step_type != StepType.Selenium && value != 'Obj')" :label="value" :value="value" ></el-option>
						</template>
					</el-select>
				</template>
			</el-table-column>
			<el-table-column label="参数值" prop="exp" align="center" min-width="200px">
				<template #default="scope">
					<el-input v-if="scope.row.type ==='Str'" style="width: 100%; box-sizing: border-box;" v-model="scope.row.value" :disabled="readOnly" placeholder="请输入预期值"></el-input>
					<el-input-number v-if="scope.row.type ==='Int'" v-model="scope.row.value" :step="1"   style="width: 100%;"/>
					<el-input-number v-if="scope.row.type ==='Float'" v-model="scope.row.value" :precision="5" :step="1"   style="width: 100%;"/>
					<el-checkbox v-if="scope.row.type ==='Bool'" v-model="scope.row.value" label="勾选代表True" size="large"/>
				</template>
			</el-table-column>
		   </el-table>
	   </el-col>
	   <el-col :span='1'></el-col>
	   <el-col :span='13' style='margin-top: 10px;'>
			<el-row>
				<el-col :span='21'>
					  <el-text type="danger">函数调试时是以页面中函数体中代码为准（调试时请注释掉系统内部变量），用例执行时以python函数列表中保存的函数为准</el-text>
				</el-col>
				<el-col :span='3'>
					<el-button  type='primary' @click="singleRunFunction()" style='margin-left: 20px;'>调试</el-button>
				</el-col>
			</el-row>
			<el-row style='background-color: var(--qm-bg-2);'>
				<el-col :span=24>
					<el-collapse v-model="activeNames" style="margin-top: 15px;">
						  <el-collapse-item title="函数说明" name="0">
							 <BodyEdit v-model='pythonFuncData.desc' lang='text' height="60px"></BodyEdit>
						  </el-collapse-item>
						  <el-collapse-item title="导入模块" name="3">
								<BodyEdit v-model='pythonFuncData.package' lang='python' height="60px"></BodyEdit>
						  </el-collapse-item>
						  <el-collapse-item title="函数体" name="1">
							<BodyEdit v-model='pythonFuncData.script' lang='python' height="150px"></BodyEdit>
						  </el-collapse-item>
						  <el-collapse-item title="函数运行结果" name="2">
							  <BodyEdit v-model='func_run_result' lang='text' height="60px"></BodyEdit>
						  </el-collapse-item>
					</el-collapse>
				</el-col>
			</el-row>
	   </el-col>
	</el-row>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import {mapState, mapActions, mapGetters} from 'vuex'
import BodyEdit from './BodyEdit.vue'

export default{
	computed:{
		...mapState(['projectInfo']),
	},
	components:{
		BodyEdit
	},
	emits: ['update:value'],
	props: {
		'pythonFuncData': {
			type: Object,
		},
		'func_params':{
			type: Array,
		},
		'value': {
			type: String,
		},
	},
	data() {
		return {
			localValue: this.value,
			activeNames: '1',
			StepType:{
				PlatformSystemFunction: -1,   
				UserCustomizeFunction: 1,     
				Request: 1,                  
				Selenium: 2,                  
				ComStep:3,                 
				UserCustomizeScript: 4
			},
			editProps:{
			 	emitPath: true,
			 	value: 'id',
			 	label: 'name',
			},
			show_close: false,
			append_to_body: true,
			funcVisible: false,
			// func_list: [],
			func_values: [],
			func_script: "",
			func_desc: "",
			func_package: '',
			func_name: '',
			func_run_result: '',
			type_list: ['Str', 'Int', 'Float', "Dict", "List", 'Bool'],
		}
	},
	methods: {
		handleFocus() {
			this.localValue = this.value
		},
		handleBlur() {
		    this.$emit('update:value', this.localValue);
		},
		handleCommand(command){
			console.log('hehehe')
		   if(command.type === 'func_generate'){
			   this.funcVisible = true	
		   }
		 },
		updateEditRow(key, value) {
		      this.$emit('updateEditRow', key, value);
		},
		async singleRunFunction(){
			for (const key in this.pythonFuncData.params) {
			   if (this.pythonFuncData.params[key].value === null){
				   ElMessage({
					 type: 'error',
					 message: '请先填写函数入参值',
				   })
				   return
				}
			}
			this.pythonFuncData.params = {...this.func_params}
			const response = await this.$api.singleRunUserFunction({python_func_obj: this.pythonFuncData})
			if (response.status === 200){
				this.func_run_result = response.data.result.result.toString()
			}
		this.activeNames = '2'
		},
	},
	created() {
		console.log(this.func_params, 'test')
	}
}

</script>

<style scoped>
	:deep(.el-textarea__inner){
	  border: none;
	  box-shadow: none;
	}

</style>