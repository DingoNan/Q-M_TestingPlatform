<template>
	<div class="user_projects" :style="{backgroundColor: userColor.body_background_color}">
		<el-container>
			<el-header style="position: fixed; width: 100%; z-index: 1000; padding-left: 10px; padding-right: 10px;">
				<Menu :userColor='userColor'  @collapse-change="handleCollapseChange" :showUser="true"></Menu>
			</el-header>
			<el-main style='padding: 10px; margin-top: 54px;'>
				<router-view :key="$route.path" :style="{backgroundColor: userColor.body_background_color}"></router-view>
			</el-main>
		</el-container>
	</div>

</template>

<script>
import Menu from '../../components/Menu.vue'
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

	}
}
</script>

<style scoped>
	.flex-grow {
	  flex-grow: 1;
	}
	.header .header_user:hover {
	  cursor: pointer;
	}
	.user_projects .header_user{
		height: 30px;
		outline: none;
		position: relative;
		top: 13px;
		right: 10px;
	}
	.header_user :focus-visible {
		outline: none;
	}
	/deep/ .el-scrollbar__bar.is-horizontal .el-scrollbar__thumb{
	    width: 0px !important;
		left: 500px !important;
	}
</style>