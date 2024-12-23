import json
import time
from typing import Any, Union

from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool

KEY_TASK = "Task"
KEY_TASK_ID = "TaskId"
KEY_STATUS_TEXT = "StatusText"
KEY_RESULT = "Result"
KEY_SENTENCE = "Sentences"

# 状态值
STATUS_SUCCESS = "SUCCESS"
STATUS_RUNNING = "RUNNING"
STATUS_QUEUEING = "QUEUEING"

REGION_ID = "cn-shanghai"
PRODUCT = "nls-filetrans"
DOMAIN = "filetrans.cn-shanghai.aliyuncs.com"
API_VERSION = "2018-08-17"
POST_REQUEST_ACTION = "SubmitTask"
GET_REQUEST_ACTION = "GetTaskResult"


class AudioToTextTool(BuiltinTool):

    def _invoke_asr(self,
                    user_id: str,
                    file_link: str,
                    access_key_id: str,
                    access_key_secret: str,
                    app_key: str) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        text = ''
        # 创建AcsClient实例
        client = AcsClient(access_key_id, access_key_secret, 'cn-shanghai')
        # 提交录音文件识别请求

        task_id = self._start_task(client, app_key, file_link)
        if not task_id:
            raise Exception('语音识别任务提交失败')
        json_response = self._wait_for_result(client, task_id)

        if not json_response or not json_response[KEY_STATUS_TEXT] == STATUS_SUCCESS:
            raise Exception('语音识别返回结果异常')
        else:
            sentences = json_response[KEY_RESULT][KEY_SENTENCE]
            for sentence in sentences:
                text += '<sentence>' + sentence['Text'] + '</sentence>'
        return self.create_text_message(text=text)

    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> \
            Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        pass

        app_key = self.runtime.credentials.get('app_key', None)
        access_key_id = self.runtime.credentials.get('access_key_id', None)
        access_key_secret = self.runtime.credentials.get('access_key_secret', None)

        if not app_key or not access_key_id or not access_key_secret:
            raise Exception('credentials is invalid')

        file_link = tool_parameters.get('file_link')
        if not file_link:
            raise Exception('file_link is required')

        return self._invoke_asr(
            user_id=user_id,
            file_link=file_link,
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            app_key=app_key
        )

    @staticmethod
    def _start_task(client: AcsClient, app_key: str, file_link: str) -> str:
        request = CommonRequest()
        request.set_domain(DOMAIN)
        request.set_version(API_VERSION)
        request.set_product(PRODUCT)
        request.set_action_name(POST_REQUEST_ACTION)
        request.set_method('POST')

        task = {
            'appkey': app_key,
            'file_link': file_link,
            'version': "4.0",
            'enable_words': False,
            'supervise_type': 2,
            'auto_split': True,
            'speaker_num': 20,
            'first_channel_only': True
        }

        task = json.dumps(task)
        request.add_body_params(KEY_TASK, task)
        task_id = None
        try:
            response = client.do_action_with_exception(request)
            json_response = json.loads(response)
            status_text = json_response[KEY_STATUS_TEXT]
            if status_text == STATUS_SUCCESS:
                task_id = json_response[KEY_TASK_ID]
            else:
                raise Exception("录音文件识别请求失败！")
        except ServerException as e:
            raise Exception('aliyun server exception')
        except ClientException as e:
            raise Exception('aliyun client exception')
        print(f'task id: {task_id}')
        return task_id

    @staticmethod
    def _wait_for_result(client: AcsClient, task_id: str):
        request = CommonRequest()
        request.set_domain(DOMAIN)
        request.set_version(API_VERSION)
        request.set_product(PRODUCT)
        request.set_action_name(GET_REQUEST_ACTION)
        request.set_method('GET')
        request.add_query_param(KEY_TASK_ID, task_id)

        json_response = None
        while True:
            try:
                response = client.do_action_with_exception(request)
                json_response = json.loads(response)
                status_text = json_response[KEY_STATUS_TEXT]
                if status_text in (STATUS_RUNNING, STATUS_QUEUEING):
                    # 继续轮询
                    time.sleep(10)
                else:
                    # 退出轮询
                    break
            except ServerException as e:
                raise Exception('aliyun server exception')
            except ClientException as e:
                raise Exception('aliyun client exception')
        print(f'json response, {json_response}')
        return json_response
