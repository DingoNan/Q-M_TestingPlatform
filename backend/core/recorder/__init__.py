# -*- coding: utf-8 -*-
"""Q·M 测试平台 · Web 自动化录制 —— 归一化引擎（P0-③）

这个包是「录制事件流 → 可执行步骤用例」的纯逻辑层：

    sources.py        把 Chrome DevTools Recorder / Playwright codegen / 扩展原生
                      三种来源统一成内部事件流
    locator_score.py  定位器打分与候选链排序
    normalizer.py     噪声过滤 → 关键字映射 → 参数化启发式 → 组装 IR

★ 设计约束（重要）：本包**不得 import Django / DRF / 任何 ORM**，
   也不得 import core.step.run_playwright（那会拉进 playwright 与 Django 模型）。
   原因有二：
     1) 只有保持框架无关，才能用 `python -m core.recorder.tests.test_normalizer`
        离线跑完整单测 —— 这是整套方案里唯一能 100% 自动化验证的部分。
     2) 归一化是纯函数式转换（输入事件流 JSON → 输出 IR JSON），
        没有理由让它依赖运行环境。
   关键字名的**真源**是 core/step/run_playwright.py，本包只以字符串形式引用，
   由单测里的一个断言保证「本包产出的 keyword 都真实存在于执行底座」。
"""

__all__ = ['sources', 'locator_score', 'normalizer']
