import json
from typing import Any, Union

from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
from alibabacloud_ocr_api20210707.client import Client as ocr_api20210707Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool


class AliyunOCRTool(BuiltinTool):

    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> \
            Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        access_key_id = self.runtime.credentials.get('access_key_id', None)
        access_key_secret = self.runtime.credentials.get('access_key_secret', None)

        if not access_key_id or not access_key_secret:
            raise Exception('credentials is invalid')

        image_url = tool_parameters.get('image_url')

        print(f'parameters: {json.dumps(tool_parameters)}')
        if not image_url:
            raise Exception('image_url is required')
        return self._do_invoke(access_key_id, access_key_secret, image_url)

    def _do_invoke(self, access_key_id: str, access_key_secret: str, image_url: str) -> \
            Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )

        config.endpoint = 'ocr-api.cn-hangzhou.aliyuncs.com'
        client = ocr_api20210707Client(config)

        request = ocr_api_20210707_models.RecognizeAllTextRequest()
        request.url = image_url
        request.type = "Advanced"
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            response = client.recognize_all_text_with_options(request, runtime)
            return self.create_text_message(text=json.dumps(response.body))
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            return self.create_text_message(text=json.dumps(f'invoke error： {error.message}'))

