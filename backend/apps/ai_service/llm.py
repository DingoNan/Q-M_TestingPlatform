"""
LLM客户端统一封装
适配OpenAI兼容接口（DeepSeek/通义千问/OpenAI等）
"""
import json
import re
import logging
from typing import Optional, Generator, List
from openai import OpenAI
from json_repair import repair_json
from apps.projects.models import AiConfig

logger = logging.getLogger('ai_service')


def _repair_json(text: str) -> str:
    """使用 json_repair 库修复LLM JSON格式错误

    json_repair 能处理: 缺逗号、尾随逗号、单引号、未引用key、
    截断JSON、字符串内换行、注释等各种LLM常见错误。
    """
    # 去除markdown代码块标记
    text = re.sub(r'^```json\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text.strip())
    # json_repair 返回修复后的JSON字符串
    repaired = repair_json(text, return_objects=False)
    return repaired


class LLMClient:
    """LLM客户端，从AiConfig表加载配置"""

    def __init__(self, ai_config_id: int):
        self.config = AiConfig.objects.get(id=ai_config_id, is_active=True, is_delete=False)
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_url,
        )
        self.model = self.config.model_name

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """普通对话调用"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise

    def chat_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.7,
                  max_tokens: int = 8192) -> dict:
        """JSON模式调用，返回解析后的dict。带自动修复+重试"""
        # OpenAI 兼容 API 要求 response_format=json_object 时 prompt 必须包含 "json" 字样，
        # 否则报 400 invalid_request_error。此处兜底确保任何调用方都能通过该校验。
        if 'json' not in f"{system_prompt}\n{user_prompt}".lower():
            system_prompt += '\n请以 JSON 对象格式输出结果，不要输出多余解释。'
        raw_content = None
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
            )
            raw_content = response.choices[0].message.content
            return json.loads(raw_content)
        except json.JSONDecodeError as e:
            logger.warning(f"LLM JSON解析失败（尝试修复）: {e}")
            logger.debug(f"LLM原始输出(前500字): {(raw_content or '')[:500]}")

            # 第一次尝试：自动修复常见格式错误
            if raw_content:
                try:
                    repaired = _repair_json(raw_content)
                    result = json.loads(repaired)
                    logger.info("LLM JSON修复成功")
                    return result
                except json.JSONDecodeError:
                    pass

            # 第二次尝试：截断修复（JSON被截断时，找到最后一个完整的}补齐）
            if raw_content:
                try:
                    # 找到最后一个完整的对象
                    last_brace = raw_content.rfind('}')
                    if last_brace > 0:
                        truncated = raw_content[:last_brace + 1]
                        # 尝试包装成完整JSON
                        brace_count = truncated.count('{') - truncated.count('}')
                        if brace_count > 0:
                            truncated += '}' * brace_count
                        result = json.loads(truncated)
                        logger.info("LLM JSON截断修复成功")
                        # 如果有cases字段，返回修复后的结果
                        if 'cases' in result:
                            return result
                except json.JSONDecodeError:
                    pass

            # 第三次尝试：重试一次，提示LLM返回合法JSON
            try:
                logger.info("LLM JSON修复失败，重试一次")
                retry_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                        {"role": "assistant", "content": raw_content or ""},
                        {"role": "user", "content": "你返回的JSON格式有误，请返回严格合法的JSON，确保所有逗号、引号、括号都正确配对。"},
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"},
                    max_tokens=max_tokens,
                )
                retry_content = retry_response.choices[0].message.content
                return json.loads(retry_content)
            except Exception as retry_e:
                logger.error(f"LLM JSON重试也失败: {retry_e}")
                raise
        except Exception as e:
            logger.error(f"LLM JSON调用失败: {e}")
            raise

    def chat_vision(self, system_prompt: str, text: str,
                    image_base64_list: list = None,
                    temperature: float = 0.7) -> str:
        """多模态对话调用，支持图片输入
        
        参数:
            system_prompt: 系统提示词
            text: 用户文本
            image_base64_list: 图片base64列表 [{'base64': '...', 'type': 'image/png'}, ...]
            temperature: 温度
        """
        try:
            # 构建多模态消息
            user_content = []

            # 添加图片
            if image_base64_list:
                for img in image_base64_list:
                    b64 = img.get('base64', '')
                    img_type = img.get('type', 'image/png')
                    if b64:
                        data_url = f"data:{img_type};base64,{b64}"
                        user_content.append({
                            "type": "image_url",
                            "image_url": {"url": data_url}
                        })

            # 添加文本
            user_content.append({"type": "text", "text": text})

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM多模态调用失败: {e}")
            raise

    def chat_vision_json(self, system_prompt: str, text: str,
                         image_base64_list: list = None,
                         temperature: float = 0.3,
                         max_tokens: int = 4096) -> dict:
        """多模态JSON模式调用，返回解析后的dict

        用于需要结构化输出的视觉分析场景
        """
        # OpenAI 兼容 API 要求 response_format=json_object 时 prompt 必须包含 "json" 字样
        if 'json' not in f"{system_prompt}\n{text}".lower():
            system_prompt += '\n请以 JSON 对象格式输出结果，不要输出多余解释。'
        raw_content = None
        try:
            user_content = []
            if image_base64_list:
                for img in image_base64_list:
                    b64 = img.get('base64', '')
                    img_type = img.get('type', 'image/png')
                    if b64:
                        data_url = f"data:{img_type};base64,{b64}"
                        user_content.append({
                            "type": "image_url",
                            "image_url": {"url": data_url}
                        })
            user_content.append({"type": "text", "text": text})

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
            )
            raw_content = response.choices[0].message.content
            return json.loads(raw_content)
        except json.JSONDecodeError as e:
            logger.warning(f"多模态JSON解析失败: {e}")
            if raw_content:
                try:
                    repaired = _repair_json(raw_content)
                    return json.loads(repaired)
                except json.JSONDecodeError:
                    pass
            raise
        except Exception as e:
            logger.error(f"多模态JSON调用失败: {e}")
            raise

    def chat_stream(self, messages: List[dict], temperature: float = 0.7) -> Generator[str, None, None]:
        """
        流式对话调用，逐chunk返回文本
        messages: [{"role": "system/user/assistant", "content": "..."}]
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"LLM流式调用失败: {e}")
            raise

