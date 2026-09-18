const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  productionSourceMap: false,
  // parallel:false 关闭 thread-loader + terser-webpack-plugin 的多进程 worker。
  // 原因：本机 node_modules 有 7 万+ 文件，Windows 下多进程 worker 池会与主进程
  // 互等（此前 64 分钟仅耗 3.9s CPU 即为此症状）。串行构建更慢但不死锁。
  parallel: false,
  devServer:{
	  client:{
		  overlay: false
	  }
  }
})
