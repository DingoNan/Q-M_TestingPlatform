<template>
  <el-table :data="keyData">
  		<el-table-column label="序号" width="70" type="index"/>
  		<el-table-column label="变量名称" prop="key" align="center">
  			<template #default="scope">
  				<el-input v-model="scope.row.key" style="width: 100%; box-sizing: border-box;" :disabled="readOnly"></el-input>
  			</template>
  		</el-table-column>
  		<el-table-column label="JsonPath表达式" prop="value" align="center">
  			<template #default="scope">
  				<el-input style="width: 100%; box-sizing: border-box;" v-model="scope.row.value" :disabled="readOnly" placeholder="请以$.开头"></el-input>
  			</template>
  		</el-table-column>
  		<el-table-column align="center" width="400px">
			<template #header>
				<el-button :icon="Plus" size="small" type='primary' @click="keyData.push(JSON.parse(JSON.stringify(this.json_row_data)))" :disabled="readOnly">新增</el-button>
				<el-button :icon="Loading" size="small" type='primary' @click="loadExtract"  v-if='isShowLoadBtn === true'>加载</el-button>
			</template>
  			<template #default="scope">
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
import { View, Delete, Edit, Plus, EditPen, CopyDocument, Top, Bottom, Loading} from '@element-plus/icons-vue'

export default{
	setup() {
		return {
			Edit,
			Delete,
			Plus,
			View,
			EditPen,
			CopyDocument,
			Top,
			Bottom,
			Loading,
		}
	},
	props: ['keyData', 'readOnly', 'loadExtract', 'isShowLoadBtn'],
	data() {
		return {
			json_row_data: {
				key: '',
				value: '',
				
			},
			bodyType: 'json',
		}
	},
	methods: {
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

<style scoped>
	
</style>