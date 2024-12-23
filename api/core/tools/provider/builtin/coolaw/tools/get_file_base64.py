import base64
from typing import Any, Union

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool
from extensions.ext_storage import storage


class GetFileBase64(BuiltinTool):

    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> \
            Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        file_path = tool_parameters.get('file_path')
        if not file_path:
            raise Exception('file_path is required')
        byte_data = storage.load_once(file_path)
        text = base64.b64encode(byte_data).decode('utf-8')
        return self.create_text_message(text=text)
