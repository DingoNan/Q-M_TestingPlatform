# -*- coding: utf-8 -*-
"""Q·M 测试平台 · 核心执行层（core）

★ 2026-10-13（P0-②）清理：这里原先残留着脚手架期的一段代码，会在**每次 import
  `core.*` 时**执行 `exec()` 并打印一个 1~9 的随机数：

      test = '''
      import random
      def test_func():
          return random.randint(1, 9)
      '''
      exec(test)
      print(test_func())

  它带来了三个实际危害（都不是"洁癖"层面的问题）：
    1) **污染所有日志**：任何 `import core.xxx` 的进程（uvicorn worker、qcluster、
       离线脚本）都会往 stdout 打一个裸数字。排查问题时这些数字与真实日志混在一起，
       极易被误读成退出码/错误码 —— 本次 P0-② 验证时就真的把 `4`、`2` 当成了
       命令退出码去追，白白绕了一圈。
    2) **导入期执行动态代码**：`exec(字符串)` 让静态分析（依赖扫描、安全审计）
       无法判断这个模块到底做了什么。
    3) 已确认全仓库无任何引用（`grep core.test / test_func` 零命中）。

  所以只保留包声明，不再有任何导入副作用。core 下各子包自带 `__init__.py`。
"""
