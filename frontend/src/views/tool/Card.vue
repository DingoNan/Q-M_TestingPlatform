<template>
	<div v-html="cardContent"></div>
</template>

<script>
import {mapState, mapActions, mapMutations} from 'vuex'
export default {
	data() {
		return {
			cardContent: '',
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
		padding: 5px;
		margin-top: 50px
	}
	.right{
		/* max-width: 1200px; */
	}
</style>