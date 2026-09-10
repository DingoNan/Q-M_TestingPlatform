<template>
	 <el-row style='background-color: white;'>
	    <el-col :span="16">
			<el-table :data="keyData" empty-text="该函数无入参">
					<el-table-column label="序号" width="70" type="index"/>
					<el-table-column label="参数名" prop="type" align="center" width="200px">
						<template #default="scope">
							<el-input style="width: 100%; box-sizing: border-box;" v-model="scope.row.params_name" disabled></el-input>
						</template>
					</el-table-column>
					<el-table-column label="参数类型" prop="type" align="center" width="200px">
						<template #default="scope">
							<el-select v-model="scope.row.type" style="width: 100%;">
								<template  v-for="value in type_list">
									<el-option  v-if="(step_type === StepType.Selenium && scope.$index ===0  && value === 'Obj')|| (step_type === StepType.Selenium &&scope.$index !=0)" :label="value" :value="value" ></el-option>
									<el-option  v-if="(step_type != StepType.Selenium && value != 'Obj')" :label="value" :value="value" ></el-option>
								</template>
							</el-select>
						</template>
					</el-table-column>
					<el-table-column label="参数值" prop="exp" align="center">
						<template #default="scope">
							<el-input v-if="scope.row.type ==='Str'" style="width: 100%; box-sizing: border-box;" v-model="scope.row.value" :disabled="readOnly" placeholder="请输入预期值"></el-input>
							<el-input v-if="scope.row.type ==='Dynamic'" style="width: 100%; box-sizing: border-box;" v-model="scope.row.value" :disabled="readOnly" placeholder="请输入预期值"></el-input>
							<el-input-number v-if="scope.row.type ==='Int'" v-model="scope.row.value" :step="1"   style="width: 100%;"/>
							<el-input-number v-if="scope.row.type ==='Float'" v-model="scope.row.value" :precision="5" :step="1"   style="width: 100%;"/>
							<el-checkbox v-if="scope.row.type ==='Bool'" v-model="scope.row.value" label="勾选代表True" size="large"/>
							<el-cascader v-if="scope.row.type ==='Obj'" collapse-tags v-model='scope.row.value' :options="loc_list" :props="editProps" clearable style="width: 100%;" filterable/>
						</template>
					</el-table-column>
					<!-- <el-table-column align="center" width="400px">
						<template #header>
							<el-button :icon="Loading" size="small" type='primary' @click="loadCheck"  v-if='isShowLoadBtn === true'>加载</el-button>
						</template>
						<template #default="scope">
						  <el-button :icon="Plus" size="small" type='primary' @click="addApiParams(scope.$index)" :disabled="readOnly">新增</el-button>
						  <el-button :icon="CopyDocument" size="small" type='primary' @click="copyApiParams(scope.$index, scope.row)" :disabled="readOnly" >复制</el-button>
						  <el-button :icon="Top" @click="topApiParams(scope.$index)" size="small" type="primary" :disabled="readOnly">上移</el-button>
						  <el-button :icon="Bottom" @click="bottomApiParams(scope.$index)" size="small" type="primary" :disabled="readOnly">下移</el-button>
						  <el-button :icon="Delete" @click="deleteApiParams(scope.$index)" size="small" type="danger" :disabled="readOnly">删除</el-button>
						</template>
					</el-table-column> -->
				</el-table>
		</el-col>
	    <el-col :span='8' style='margin-top: 10px;'>
			<el-row>
				<el-col :span='24'>
					<el-button :icon="VideoPause" size="small" type='primary' @click="singleRunFunction" :disabled="readOnly">单独调试函数</el-button>
					<el-tooltip placement="right" effect="light">
					    <template #content> 鼠标悬浮函数入参Tab标题可查看函数功能介绍</template>
					    <el-icon color='#409eff' style='float:right'><InfoFilled /></el-icon>
					</el-tooltip>
				</el-col>
			</el-row>
			<el-row style='background-color: white;'>
				<el-col :span='24'>
					<el-divider style='margin: 5px 0px'/>
					<el-input
						class="no-border"
					    v-model="func_run_result"
					    type="textarea"
						:rows="22"
					    placeholder="点击单独调试函数显示执行结果"
					  />
				</el-col>
			</el-row>
		</el-col>
	  </el-row>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, Edit, Plus, EditPen, CopyDocument, Top, Bottom, Loading, VideoPause} from '@element-plus/icons-vue'
import {mapState, mapActions, mapGetters} from 'vuex'

export default{
	computed:{
		...mapState(['projectInfo']),
	},
	setup() {
		return {
			Edit,
			Delete,
			Plus,
			View,
			Loading,
			EditPen,
			CopyDocument,
			Top,
			Bottom,
		}
	},
	props: ['keyData', 'step_type', 'function_name'],
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
			editProps:{
				emitPath: false,
				value: 'id',
				label: 'name',
			},
			loc_list: [],
			func_run_result: '',
			type_list: ['Str', 'Int', 'Float', "Bool", "Dynamic", 'Obj'],
			method: [],
			json_row_data: {
				value: '',
				type: 'Str'
				
			},
			bodyType: 'json',
		}
	},
	methods: {
		async singleRunFunction(){
			console.log(this.keyData, '11111')
			const response = await this.$api.singleRunFunction({function_name: this.function_name, params: this.keyData})
			if (response.status === 200){
				this.func_run_result = response.data.result.result
			}
		},
		pushData(){
			const data = JSON.parse(JSON.stringify(this.json_row_data))
			if (this.keyData.length === 0 && this.step_type === this.StepType.Selenium){
				data.type = 'Obj'
			}
			this.keyData.push(data)
		},
		async getPlantElement(){
			const response = await this.$api.getAllPlantElement({project: this.projectInfo.id})
			if (response.status === 200){
				this.loc_list = response.data.results
			}
		},
		addApiParams(index){
			const row_data = JSON.parse(JSON.stringify(this.json_row_data))
			if (this.keyData.length === 0 && this.step_type === this.StepType.Selenium){
				row_data.type = 'Obj'
			}
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
		this.getPlantElement()
	}
}

</script>

<style scoped>
	:deep(.el-textarea__inner){
	  border: none;
	  box-shadow: none;
	}

</style>