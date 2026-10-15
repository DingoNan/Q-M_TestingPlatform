from utils.base import BaseSerializer
from apps.elements.models import Element

from rest_framework import serializers
from rest_framework.validators import ValidationError


class ElementSerializers(BaseSerializer):
    module_id = serializers.CharField(source='module.id', read_only=True)
    module_name = serializers.CharField(source='module.name', read_only=True)
    # page_url = serializers.CharField(source='page.url', read_only=True)
    # module_name = serializers.CharField(source='page.module.name', read_only=True)
    plant_name = serializers.CharField(source='page.module.plant.name', read_only=True)
    plant_id = serializers.CharField(source='page.module.plant.id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    # ★ P3 元素健康度：fallback / (hit + fallback)，分母为 0 记 0.0。
    #   用 SerializerMethodField 而不是 FloatField —— 普通列表接口不带该 annotation，
    #   用 getattr 兜底可保证「非 health 接口也永远不报错」。
    degrade_rate = serializers.SerializerMethodField()

    def get_degrade_rate(self, obj):
        value = getattr(obj, 'degrade_rate', None)
        if value is None:
            return 0.0
        try:
            return round(float(value), 4)
        except (TypeError, ValueError):
            return 0.0

    # ==================== P0（2026-10-15）：定位结构保存期校验（DEF-15） ====================
    # ★ 背景：运行期 core/step/run_playwright.py 一律按 dict 使用（web_loc['by'] / obj['web']），
    #   而模型 default=list、保存期零校验 ⇒ 存成数组能保存成功，执行时才崩
    #   `'list' object has no attribute 'get'`，报错与「结构写错了」毫无关联。
    #   这里在保存期收敛形状：旧导入模板的数组形态自动规整为 dict，
    #   缺 by/value 直接报错并给出正确示例。
    LOC_SAMPLE = '{"by": "css", "value": "#username", "opts": {}}'

    def _normalize_locator(self, key, value):
        """把 web/ios/android 的入参规整成运行期期望的 dict。

        返回 None 表示「保持原样」（空值 / 无法规整但不算错）；
        形状确实不对时直接抛 ValidationError。
        """
        if value is None or value == [] or value == {}:
            return None
        if isinstance(value, list):
            items = [x for x in value if isinstance(x, dict)]
            if len(items) == 1:
                value = items[0]
            elif len(items) > 1:
                raise ValidationError(
                    '%s 定位配置里有 %d 个定位项，无法确定用哪一个。'
                    '正确结构是对象（不是数组）：%s' % (key, len(items), self.LOC_SAMPLE))
            else:
                return None
        if not isinstance(value, dict):
            raise ValidationError(
                '%s 定位配置必须是对象，当前是 %s。正确结构：%s'
                % (key, type(value).__name__, self.LOC_SAMPLE))
        missing = [k for k in ('by', 'value') if k not in value]
        if missing:
            raise ValidationError(
                '%s 定位配置缺少必需字段：%s。正确结构：%s'
                % (key, '、'.join(missing), self.LOC_SAMPLE))
        by, loc_value = value.get('by'), value.get('value')
        if not by or (loc_value is None or loc_value == ''):
            raise ValidationError(
                '%s 定位配置的 by 与 value 都不能为空（当前 by=%r，value=%r）。正确结构：%s'
                % (key, by, loc_value, self.LOC_SAMPLE))
        value.setdefault('opts', {})
        return value

    def _locator_ready(self, attrs, key):
        """判断某端定位是否可用（partial 更新时回看库里的旧值）。"""
        if key in attrs:
            value = attrs[key]
        else:
            value = getattr(self.instance, key, None) if self.instance else None
        if isinstance(value, list):
            items = [x for x in value if isinstance(x, dict)]
            value = items[0] if len(items) == 1 else None
        if not isinstance(value, dict):
            return False
        return bool(value.get('by')) and value.get('value') not in (None, '')

    def validate(self, attrs):
        for key in ('web', 'ios', 'android'):
            if key in attrs:
                fixed = self._normalize_locator(key, attrs[key])
                if fixed is not None:
                    attrs[key] = fixed
        elem_type = attrs.get('type', getattr(self.instance, 'type', None))
        if elem_type == 'web' and not self._locator_ready(attrs, 'web'):
            raise ValidationError(
                'Web 元素必须配置定位方式(by)与定位表达式(value)。正确结构：%s' % self.LOC_SAMPLE)
        if elem_type == 'app' and not (self._locator_ready(attrs, 'ios')
                                       or self._locator_ready(attrs, 'android')):
            raise ValidationError(
                'App 元素至少要配置 ios / android 其中一份定位。正确结构：%s' % self.LOC_SAMPLE)
        return attrs
    class Meta:
        model = Element
        fields = '__all__'
