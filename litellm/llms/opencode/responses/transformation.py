"""
OpenCode Responses API configuration, shared by the Zen and Go surfaces.

Routes models in a surface's responses-model set to ``{base}/v1/responses``
with OpenAI-compatible request/response shape. Uses ``Bearer`` auth.
"""

from collections.abc import Mapping
from typing import Any, Final  # noqa: TID251  # OpenAI Responses API wire format uses Any in param/return shapes

from litellm.llms.openai.responses.transformation import OpenAIResponsesAPIConfig
from litellm.llms.opencode.common_utils import (
    resolve_opencode_api_base,
    resolve_opencode_api_key,
    with_opencode_session_header,
)
from litellm.types.router import GenericLiteLLMParams
from litellm.types.utils import LlmProviders

ZEN_MESSAGES_BASE: Final = "https://opencode.ai/zen"
GO_MESSAGES_BASE: Final = "https://opencode.ai/zen/go"


class OpenCodeResponsesAPIConfig(OpenAIResponsesAPIConfig):
    """
    Configuration for the OpenCode gateway's Responses API.

    Inherits from OpenAIResponsesAPIConfig since the gateway's Responses API
    is compatible with OpenAI's Responses API specification.

    Key differences from direct OpenAI:
    - Uses ``{base}/v1/responses`` as the API base (OpenCode gateway)
    - Uses ``OPENCODE_{ZEN,GO}_API_KEY`` for authentication
    - Returns ``Bearer`` auth header (not ``x-api-key``)
    - Go also requires the ``x-opencode-session`` header; it is a no-op on Zen
    """

    def __init__(self, surface: str) -> None:
        super().__init__()
        self.surface: Final = surface

    @property
    def custom_llm_provider(self) -> LlmProviders:
        return LlmProviders.OPENCODE_GO if self.surface == "go" else LlmProviders.OPENCODE_ZEN

    def _default_base(self) -> str:
        return GO_MESSAGES_BASE if self.surface == "go" else ZEN_MESSAGES_BASE

    def validate_environment(
        self,
        headers: dict,  # mutable-ok: signature must match OpenAIResponsesAPIConfig
        model: str,
        litellm_params: GenericLiteLLMParams | None,
    ) -> dict:  # mutable-ok: signature must match OpenAIResponsesAPIConfig
        litellm_params = litellm_params or GenericLiteLLMParams()  # rebind-ok: default to empty params
        api_key: Final = resolve_opencode_api_key(self.surface, litellm_params.api_key)

        if not api_key:
            raise ValueError(
                f"OpenCode {self.surface.title()} API key is required. "
                f"Set OPENCODE_{self.surface.upper()}_API_KEY environment variable or pass api_key parameter."
            )

        headers["Content-Type"] = "application/json"  # rebind-ok: caller expects auth header injected
        headers["Authorization"] = f"Bearer {api_key}"  # rebind-ok: caller expects auth header injected
        return with_opencode_session_header(self.surface, headers, litellm_params.model_dump())

    def get_complete_url(
        self,
        api_base: str | None,
        litellm_params: Mapping[str, Any],
    ) -> str:
        base: Final = (resolve_opencode_api_base(self.surface, api_base) or self._default_base()).rstrip("/")

        if base.endswith("/v1/responses"):
            return base
        if base.endswith("/v1"):
            return f"{base}/responses"
        if base.endswith("/responses"):
            return base
        return f"{base}/v1/responses"

    def supports_native_websocket(self) -> bool:
        """OpenCode does not support native WebSocket for the Responses API."""
        return False


class OpenCodeZenResponsesAPIConfig(OpenCodeResponsesAPIConfig):
    def __init__(self) -> None:
        super().__init__(surface="zen")


class OpenCodeGoResponsesAPIConfig(OpenCodeResponsesAPIConfig):
    def __init__(self) -> None:
        super().__init__(surface="go")
