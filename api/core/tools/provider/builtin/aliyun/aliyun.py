from typing import Any

from core.tools.errors import ToolProviderCredentialValidationError
from core.tools.provider.builtin.aliyun.tools.audio_to_text import AudioToTextTool
from core.tools.provider.builtin_tool_provider import BuiltinToolProviderController


class AliyunProvider(BuiltinToolProviderController):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            AudioToTextTool().fork_tool_runtime(
                runtime={
                    "credentials": credentials,
                }
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
