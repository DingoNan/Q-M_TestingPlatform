<template>
  <router-view/>
</template>

<script>
// 判断一个项目对象是否为「可用」：必须是带非空 id 的对象。
function isValidProject(p) {
	return !!(p && typeof p === 'object' && p.id)
}

export default{
	created(){
		// ---------------------------------------------------------------
		// 刷新恢复内存态。
		//
		// 历史实现是一句无条件的 replaceState(Object.assign(state, 快照))，
		// 它会把快照里的**每一个**字段覆盖到内存上。问题出在 projectInfo：
		// 快照（localStorage 的 store 键）是「上一次 beforeunload 时刻」的副本，
		// 如果那一刻 projectInfo 恰好为空（例如用户刚登出、或上次会话没进过项目），
		// 刷新后这行代码就会把**已经修好的** projectInfo 再顶回空值，
		// 导致 qm-projectInfo 明明有值却依然表现为「模块管理空白」。
		//
		// 因此改为：
		//   ① 正常恢复其余字段；
		//   ② projectInfo 单独裁决 —— 以 qm-projectInfo（专键）为准，
		//      仅在专键也无有效值时才退回快照里的副本。
		// 这样两处副本谁有真值就用谁，不再出现「旧值顶掉新值」。
		// ---------------------------------------------------------------
		let snapshot = null
		const raw = localStorage.getItem('store')
		if (raw) {
			try { snapshot = JSON.parse(raw) } catch (e) { snapshot = null }
		}

		if (snapshot && typeof snapshot === 'object') {
			const snapshotProject = snapshot.projectInfo
			const restored = Object.assign({}, snapshot)
			// projectInfo 不参与整体覆盖，下面单独裁决
			delete restored.projectInfo
			this.$store.replaceState(Object.assign(this.$store.state, restored))

			const current = this.$store.state.projectInfo
			if (isValidProject(current)) {
				// 专键有效 —— 保持不动（快照里的旧副本将被下一次写回纠正）
			} else if (isValidProject(snapshotProject)) {
				this.$store.commit('saveProjectInfo', snapshotProject)
			} else {
				// 两处都无效 —— 明确置空，交由路由守卫/页面兜底恢复
				this.$store.commit('clearProjectInfo')
			}
		}

		// 在页面刷新时将 vuex 里的信息保存到 localStorage。
		// 注意：projectInfo 不写入 store 快照 —— 它由 qm-projectInfo 专键单独负责，
		// 避免出现两份副本相互覆盖（这正是历史上「修好了又变空」的原因）。
		window.addEventListener("beforeunload", () => {
			try {
				const state = Object.assign({}, this.$store.state)
				delete state.projectInfo
				localStorage.setItem("store", JSON.stringify(state))
			} catch (e) {
				// 忽略序列化异常，不影响主流程
			}
		})
	}
}

</script>

<style>
</style>
