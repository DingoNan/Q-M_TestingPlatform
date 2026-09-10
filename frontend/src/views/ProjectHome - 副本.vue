<template>
	<div class="all" :style="{backgroundColor: userColor.body_background_color}">
		<el-container direction="horizontal">
			<el-aside :width="aside_width">
				<Menu :userColor='userColor' :width='aside_width' @collapse-change="handleCollapseChange"></Menu>
			</el-aside>
			<el-container direction="vertical" class='right'>
				<el-header height="50px" :style="{'padding': '0', 'z-index': '1000', 'white-space': 'nowrap', 'position': 'fixed', width: `calc(100% - ${aside_width})`}">
					<Tags :userColor='userColor'></Tags>
				</el-header>
				<el-main class='body' :style="{backgroundColor: userColor.body_background_color}" >
					<router-view :key="$route.path" :style="{backgroundColor: userColor.body_background_color}"></router-view>
				</el-main>
			</el-container>
		</el-container>
	</div>
	
</template>

<script>
import Menu from '../components/Menu.vue'
import Tags from '../components/Tags.vue'
import {mapState, mapActions, mapMutations} from 'vuex'
export default {
	data() {
		return {
			userColor: {},
			aside_width: '200px',
		}
	},
	components:{
		Menu,
		Tags,
	},
	computed: {
		...mapState(['user_id', 'pathPermission'])
	},
	methods: {
		  ...mapMutations(['addTags', 'setPathPermission']),
		  async get_color_setting(){
		  	const response = await this.$api.get_color_setting({id: this.user_id})
		  	if(response.status === 200){
		  		this.userColor = {...response.data.result}
		  		
		  	}
		  },
		 handleCollapseChange(isCollapsed) {
		        this.aside_width = isCollapsed ? '64px' : '200px';
		 },
	},
	created() {
		  this.get_color_setting()
	}
}
</script>

<style scoped>
	.all{
		height: 100vh;
		background-color: #f7f8fa;
	}
	.body{
		background-color: #f7f8fa;
		padding: 10px;
		margin-top: 50px
	}
	.right{
		/* max-width: 1200px; */
	}
</style>