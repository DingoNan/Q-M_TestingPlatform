/**
 * 功能开关（Feature Flags）
 * ============================================================
 * 为什么要有这个文件：
 *   有些功能暂时用不上，但直接删代码/注释掉，过几个月想恢复时就得
 *   翻 git 历史从一堆 diff 里往外抠。这里把「是否显示」收敛成一个
 *   常量，关掉只是不渲染，代码原样保留；想恢复把 false 改回 true 即可。
 *
 * 用法：
 *   import { isFeatureEnabled } from '@/utils/features'
 *   <el-tab-pane v-if="isFeatureEnabled('appDevice')" ... />
 *
 * ★ 注意：这里只是「界面是否露出」的开关，不是权限。
 *   真正的访问控制仍然走后端 RBAC（pathPermission），两者互不替代。
 */
export const FEATURES = {
  /**
   * 手机设备配置（环境管理 → 环境配置 → 手机设备配置）
   * 现状：平台暂未接入移动端设备池，这一页目前没有可配置的数据源，
   *       留着只会让用户在「环境配置」里多点一次空标签。先隐藏。
   * 恢复条件：接入 Appium 设备集群 / 有真实手机设备需要登记时改回 true。
   */
  appDevice: false
}

/**
 * 判断某个功能当前是否启用。
 * 未知 key 一律返回 false —— 宁可藏起来，也不要因为拼错 key
 * 把一个还没准备好的功能放出去。
 */
export function isFeatureEnabled(key) {
  return FEATURES[key] === true
}

export default FEATURES
