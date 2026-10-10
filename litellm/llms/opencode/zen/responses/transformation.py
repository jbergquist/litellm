"""OpenCode Zen Responses API configuration; see opencode.responses.transformation."""

from litellm.llms.opencode.responses.transformation import OpenCodeResponsesAPIConfig


class OpenCodeZenResponsesAPIConfig(OpenCodeResponsesAPIConfig):
    def __init__(self) -> None:
        super().__init__(surface="zen")
