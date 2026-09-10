<template>
  <el-table :data="keyData" :height="'calc(100vh - 485px)'"  >
  		<el-table-column label="用例过滤方式" prop="method" align="center" width="320px">
  			<template #default="scope">
				<el-select v-model="scope.row.method" style="width: 100%;" size='large' class="select" popper-class='select-dropdown-rounded'>
					<el-option v-for="obj in method" :label="obj.lable" :value="obj.id" ></el-option>
				</el-select>
  			</template>
  		</el-table-column>
  		<el-table-column label="用例过滤值" prop="value" align="center" min-width="350px">
  			<template #default="scope">
				<el-select v-model="scope.row.value" style="width: 100%;" v-if="scope.row.method ===3" multiple size='large' class="select" popper-class='select-dropdown-rounded'>
					<el-option v-for="obj in tag_list" :label="obj.name" :value="obj.id" ></el-option>
				</el-select>
				<el-cascader class='cascader' size='large' clscollapse-tags v-model='scope.row.value' :options="plant_module_list" :props="props" clearable style="width: 100%;" v-if="scope.row.method ===2"/>
  			</template>
  		</el-table-column>
		<el-table-column label="与或非" prop="andOr" align="center" width="150px">
			<template #default="scope">
				<el-select v-model="scope.row.andOr" style="width: 100%;" size='large'class="select" popper-class='select-dropdown-rounded'>
					<el-option v-for="value in and_or_list" :label="value" :value="value" ></el-option>
				</el-select>
			</template>
		</el-table-column>
  		<el-table-column align="center" width="60px">
			<template #header>
				<el-tooltip content="新增">
					<el-button :icon="Plus" circle  @click="keyData.push(JSON.parse(JSON.stringify(this.json_row_data)))" :disabled="readOnly"></el-button>
					
				</el-tooltip>
			</template>
  			<template #default="scope">
				<el-tooltip content="删除">
					<el-button :icon="Delete" @click="deleteApiParams(scope.$index)" circle  :disabled="readOnly"></el-button>
					
				</el-tooltip>
  			</template>
  		</el-table-column>
  </el-table>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import {mapState} from 'vuex'
import { View, Delete, Edit, Plus, EditPen, CopyDocument, Top, Bottom, Loading} from '@element-plus/icons-vue'

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
	props: ['keyData', 'readOnly'],
	data() {
		return {
			props: {
				multiple: true,
				emitPath: false,
				value: 'id',
				label: 'name',
			},
			and_or_list: ["And", "Or"],
			plant_module_list: [],
			method: [
				{
				id: 2,
				lable: '按用例模块过滤',
				},
				{
				id: 3,
				lable: '按用例标签过滤',
				},
			],
			tag_list: [],
			json_row_data: {
				method: 3,
				value: '',
				andOr: 'And'
				
			},
			bodyType: 'json',
		}
	},
	methods: {
		async getTags(){
			const response = await this.$api.getTags({project: this.projectInfo.id})
			if (response.status === 200){
				this.tag_list = response.data.results
			}
		},
		async getPlantModule(){
			const response = await this.$api.getAllPlantModule({project: this.projectInfo.id})
			if (response.status === 200){
				this.plant_module_list = response.data.results
			}
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
		this.getPlantModule()
		this.getTags()
	}
}

</script>

<style scoped>
	
</style>