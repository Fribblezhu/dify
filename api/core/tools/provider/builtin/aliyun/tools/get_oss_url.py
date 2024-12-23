from typing import Any, Union

import oss2

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool


class GetOSSURLTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> \
            Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        access_key_id = self.runtime.credentials.get('access_key_id', None)
        access_key_secret = self.runtime.credentials.get('access_key_secret', None)

        if not access_key_id or not access_key_secret:
            raise Exception('credentials is invalid')

        file_path = tool_parameters.get('file_path')
        if not file_path:
            raise Exception('file_path is required')

        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, 'https://oss-cn-shanghai.aliyuncs.com', 'coolaw-ai')
        url = bucket.sign_url('GET', file_path, 3600, slash_safe=True)
        return self.create_text_message(text=url)


