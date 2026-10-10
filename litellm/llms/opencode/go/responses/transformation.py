"""OpenCode Go Responses API configuration; see opencode.responses.transformation."""

from litellm.llms.opencode.responses.transformation import OpenCodeResponsesAPIConfig


class OpenCodeGoResponsesAPIConfig(OpenCodeResponsesAPIConfig):
    def __init__(self) -> None:
        super().__init__(surface="go")
