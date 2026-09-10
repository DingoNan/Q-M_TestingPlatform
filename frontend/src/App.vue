<template>
  <router-view/>
</template>

<script>
export default{
	created(){
		localStorage.getItem("store") && this.$store.replaceState(Object.assign(this.$store.state,JSON.parse(localStorage.getItem("store"))));
		
		//在页面刷新时将vuex里的信息保存到localStorage
		window.addEventListener("beforeunload",()=>{
		    localStorage.setItem("store",JSON.stringify(this.$store.state))
		})
	}
}
	
	   

</script>

<style>
</style>
