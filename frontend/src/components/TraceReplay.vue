<template>
	<div class="trace-replay">
		<video v-if="logInfo.video_url" class="trace-replay-video" :src="resolveMedia(logInfo.video_url)" controls></video>
		<div class="trace-replay-actions" v-if="logInfo.trace_url">
			<el-button type="primary" size="small" @click="openTrace">
				<el-icon class="trace-btn-icon"><VideoPlay /></el-icon>Trace 回放
			</el-button>
			<el-link type="primary" :href="resolveMedia(logInfo.trace_url)" target="_blank" :underline="false">下载 Trace zip</el-link>
		</div>
		<div class="trace-replay-tip" v-if="logInfo.trace_url">
			<template v-if="canOnlineTrace">Trace 回放可逐步查看每一步的页面快照、网络请求与控制台日志</template>
			<template v-else>当前以 LAN IP + HTTP 访问，浏览器禁止该环境在线回放 Trace；可下载 zip 后本地执行 <code>playwright show-trace</code> 打开，或点击「Trace 回放」查看一次性配置方法</template>
		</div>
		<el-dialog v-model="traceViewerVisible" title="Playwright Trace 回放" fullscreen destroy-on-close append-to-body class="trace-viewer-dialog">
			<iframe v-if="traceViewerVisible" :src="traceViewerSrc" class="trace-viewer-iframe" frameborder="0"></iframe>
		</el-dialog>
	</div>
</template>

<script>
import { base_url } from '../api/index.js'
import { ElMessageBox } from 'element-plus'
import { VideoPlay } from '@element-plus/icons-vue'

export default {
	name: 'TraceReplay',
	components: { VideoPlay },
	props: {
		logInfo: { type: Object, required: true }
	},
	data() {
		return {
			traceViewerVisible: false,
			traceViewerSrc: ''
		}
	},
	computed: {
		// Trace Viewer 依赖 Service Worker, 浏览器仅在 localhost / HTTPS(安全上下文) 下提供该 API
		canOnlineTrace() {
			const host = window.location.hostname
			const isLocal = host === 'localhost' || host === '127.0.0.1' || host === '::1' || host.endsWith('.localhost')
			return window.location.protocol === 'https:' || isLocal || window.isSecureContext === true
		},
		// flag 需要放行的源: 页面源 + API/TraceViewer 源(base_url), 跨端口时是两个不同源
		flagOrigins() {
			const frontOrigin = window.location.origin
			const apiOrigin = new URL(base_url).origin
			return frontOrigin === apiOrigin ? frontOrigin : `${frontOrigin},${apiOrigin}`
		}
	},
	methods: {
		resolveMedia(url) {
			return base_url + url
		},
		openTrace() {
				if (!this.canOnlineTrace) {
					ElMessageBox.alert(
						`<div style="line-height:1.9">
							<p>Trace 官方回放器依赖浏览器 Service Worker，仅在 <b>localhost</b> 或 <b>HTTPS</b> 环境可用，当前为 LAN IP + HTTP。可选择：</p>
							<p><b>方法一（一次性配置）：</b>Chrome/Edge 地址栏打开 <code>chrome://flags/#unsafely-treat-insecure-origin-as-secure</code>，填入 <code>${this.flagOrigins}</code>（页面和接口两个源，逗号分隔），选 Enabled 并点 Relaunch 完全重启浏览器后即可在线回放。</p>
							<p><b>方法二：</b><a href="${this.resolveMedia(this.logInfo.trace_url)}" target="_blank" style="color:#409eff">下载 Trace zip</a>，本地安装 Playwright 后执行 <code>playwright show-trace 文件名.zip</code> 打开。</p>
							<p>上方的执行过程视频不受此限制，可直接播放。</p>
						</div>`,
						'Trace 在线回放受限',
						{ dangerouslyUseHTMLString: true, confirmButtonText: '我知道了' }
					)
					return
				}
			const traceAbs = this.resolveMedia(this.logInfo.trace_url)
			this.traceViewerSrc = `${base_url}/traceviewer/index.html?trace=${encodeURIComponent(traceAbs)}`
			this.traceViewerVisible = true
		}
	}
}
</script>

<style scoped>
	.trace-replay {
		display: flex;
		flex-direction: column;
		gap: 10px;
		padding: 4px 0;
	}

	.trace-replay-video {
		width: 100%;
		max-width: 960px;
		border-radius: 8px;
		background: #000;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
	}

	.trace-replay-actions {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.trace-btn-icon {
		margin-right: 4px;
	}

	.trace-replay-tip {
		font-size: 12px;
		color: #94a3b8;
		line-height: 1.6;
	}

	.trace-replay-tip code {
		background: #f1f5f9;
		padding: 1px 5px;
		border-radius: 4px;
		color: #64748b;
	}
</style>

<style>
	/* 弹窗经 append-to-body 挂载到 body, 使用非 scoped 样式 */
	.trace-viewer-dialog .el-dialog__body {
		padding: 10px 16px 16px 16px;
	}

	.trace-viewer-dialog .trace-viewer-iframe {
		width: 100%;
		height: calc(100vh - 90px);
		border: none;
		border-radius: 8px;
		background: #1e1e1e;
	}
</style>
