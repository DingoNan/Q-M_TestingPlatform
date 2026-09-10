import logging

from django.utils import timezone

from apps.messages.models import Message

logger = logging.getLogger(__name__)


def run_one_case_with_message(env_id, case_id, user_id, web_executor_id, app_executor_id,
                              fail_is_continue, case_data, message_id):
    """异步执行单条用例并回写任务消息状态（进行中 -> 已完成/失败）"""
    from core.run_case import run_one_case

    start = timezone.now()
    error = None
    log_id = None
    try:
        log_id = run_one_case(env_id, case_id, user_id, web_executor_id, app_executor_id,
                              0, 0, None, fail_is_continue, case_data=case_data)
    except Exception as e:
        error = str(e)
        logger.error(f"[用例执行任务] case={case_id} 执行异常: {e}", exc_info=True)
    finally:
        _update_run_message(message_id, case_id, log_id, error,
                            duration=(timezone.now() - start).total_seconds())
    return log_id


def _update_run_message(message_id, case_id, log_id, error, duration):
    """用例执行结束后回写任务消息：成功->已完成，失败/错误->失败"""
    if not message_id:
        return
    try:
        from apps.tests.models import Case, CaseRunLog

        case = Case.objects.filter(id=case_id).first()
        case_name = case.name if case else f'用例#{case_id}'
        related_url = f'/resource/scriptCaseEdit?id={case_id}'

        if error:
            Message.objects.filter(id=message_id).update(
                title='用例执行失败',
                content=f'用例: {case_name}\n失败原因: {error}',
                task_status=Message.TaskStatus.FAILED,
                failed_count=1,
                fail_reason=error,
                duration=duration,
                related_url=related_url,
                is_read=False,
                read_time=None,
                update_time=timezone.now(),
            )
            logger.info(f'[用例执行任务] 站内信 {message_id} 已更新为 用例执行失败')
            _push_updated_message(message_id)
            return

        log = CaseRunLog.objects.filter(id=log_id).first()
        result_text = log.get_result_display() if log else '未知'
        success = log is not None and log.result == CaseRunLog.CaseResult.SUCCESS
        env_name = getattr(log.env, 'name', '') if log else ''
        title = '用例执行完成' if success else '用例执行失败'
        content = (
            f'用例: {case_name}\n'
            f'环境: {env_name}\n'
            f'结果: {result_text}\n'
            f'耗时: {duration:.1f} 秒'
        )
        Message.objects.filter(id=message_id).update(
            title=title,
            content=content,
            task_status=Message.TaskStatus.SUCCESS if success else Message.TaskStatus.FAILED,
            success_count=1 if success else 0,
            failed_count=0 if success else 1,
            fail_reason='' if success else f'用例执行结果: {result_text}',
            duration=duration,
            related_url=related_url,
            is_read=False,
            read_time=None,
            update_time=timezone.now(),
        )
        logger.info(f'[用例执行任务] 站内信 {message_id} 已更新为 {title}')
        _push_updated_message(message_id)
    except Exception as e:
        logger.error(f'[用例执行任务] 更新站内信失败: {e}', exc_info=True)


def _push_updated_message(message_id):
    """推送更新后的消息到前端"""
    try:
        from apps.messages.push import push_message_to_user, build_message_payload
        msg = Message.objects.filter(id=message_id).first()
        if msg:
            logger.info(f'[用例执行任务] 推送站内信 message_id={message_id} user_id={msg.user_id}')
            push_message_to_user(msg.user_id, build_message_payload(msg))
            logger.info(f'[用例执行任务] 推送站内信完成 message_id={message_id}')
    except Exception as e:
        logger.error(f'[用例执行任务] 推送站内信失败: {e}', exc_info=True)
