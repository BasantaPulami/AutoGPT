"""Extended-thinking wire support for the baseline (OpenRouter) path.

Anthropic routes on OpenRouter expose extended thinking through
non-OpenAI extension fields that the OpenAI Python SDK doesn't model:

* ``reasoning`` (legacy string) — enabled by ``include_reasoning: true``.
* ``reasoning_content`` — DeepSeek / some OpenRouter routes.
* ``reasoning_details`` — structured list shipped with the unified
  ``reasoning`` request param.

This module keeps the wire-level concerns in one place:

* :class:`OpenRouterDeltaExtension` validates the extension dict pulled off
  ``ChoiceDelta.model_extra`` into typed pydantic models — no ``getattr`` +
  ``isinstance`` duck-typing at the call site.
* :class:`BaselineReasoningEmitter` owns the reasoning block lifecycle for
  one streaming round and emits ``StreamReasoning*`` events so the caller
  only has to plumb the events into its pending queue.
* :func:`reasoning_extra_body` builds the ``extra_body`` fragment for the
  OpenAI client call.  Returns ``None`` on non-Anthropic routes.
"""

from __future__ import annotations

import uuid
from typing import Any

from openai.types.chat.chat_completion_chunk import ChoiceDelta
from pydantic import BaseModel, ConfigDict, Field

from backend.copilot.response_model import (
    StreamBaseResponse,
    StreamReasoningDelta,
    StreamReasoningEnd,
    StreamReasoningStart,
)


class ReasoningDetail(BaseModel):
    """One entry in OpenRouter's ``reasoning_details`` list.

    OpenRouter ships ``type: "reasoning.text"`` / ``"reasoning.summary"`` /
    ``"reasoning.encrypted"`` entries.  Only the first two carry
    user-visible text; encrypted entries are opaque and omitted from the
    rendered collapse.  Unknown future types are tolerated (``extra="ignore"``)
    so an upstream addition doesn't crash the stream.
    """

    model_config = ConfigDict(extra="ignore")

    type: str | None = None
    text: str | None = None
    summary: str | None = None

    @property
    def visible_text(self) -> str:
        """Return the human-readable text for this entry, or ``""``."""
        return self.text or self.summary or ""


class OpenRouterDeltaExtension(BaseModel):
    """Non-OpenAI fields OpenRouter adds to streaming deltas.

    Instantiate via :meth:`from_delta` which pulls the extension dict off
    ``ChoiceDelta.model_extra`` (where pydantic v2 stashes fields that
    aren't part of the declared schema) and validates it through this
    model.  That keeps the parser honest — malformed entries surface as
    validation errors rather than silent ``None``-coalesce bugs — and
    avoids the ``getattr`` + ``isinstance`` duck-typing the earlier inline
    extractor relied on.
    """

    model_config = ConfigDict(extra="ignore")

    reasoning: str | None = None
    reasoning_content: str | None = None
    reasoning_details: list[ReasoningDetail] = Field(default_factory=list)

    @classmethod
    def from_delta(cls, delta: ChoiceDelta) -> "OpenRouterDeltaExtension":
        """Build an extension view from ``delta.model_extra``."""
        return cls.model_validate(delta.model_extra or {})

    def visible_text(self) -> str:
        """Concatenated reasoning text, pulled from whichever channel is set.

        Priority: the legacy ``reasoning`` string, then DeepSeek's
        ``reasoning_content``, then the concatenation of text-bearing
        entries in ``reasoning_details``.  Only one channel is set per
        provider in practice; the priority order just makes the fallback
        deterministic if a provider ever emits multiple.
        """
        if self.reasoning:
            return self.reasoning
        if self.reasoning_content:
            return self.reasoning_content
        return "".join(d.visible_text for d in self.reasoning_details)


def _is_anthropic_route(model: str) -> bool:
    """Mirror of the private ``_is_anthropic_model`` check in service.py.

    Kept as a free function here to avoid a circular import — ``service.py``
    imports this module, not the other way around.
    """
    lowered = model.lower()
    return "claude" in lowered or lowered.startswith("anthropic")


def reasoning_extra_body(model: str, max_thinking_tokens: int) -> dict[str, Any] | None:
    """Build the ``extra_body["reasoning"]`` fragment for the OpenAI client.

    Returns ``None`` for non-Anthropic routes — other OpenRouter providers
    drop the field but we skip it anyway to keep the payload minimal.
    """
    if not _is_anthropic_route(model):
        return None
    return {"reasoning": {"max_tokens": max_thinking_tokens}}


class BaselineReasoningEmitter:
    """Owns the reasoning block lifecycle for one streaming round.

    The AI SDK v5 wire format pairs every ``reasoning-start`` with a
    matching ``reasoning-end``, and treats reasoning / text / tool-use as
    three distinct UI parts that must not interleave.  This class folds
    the state machine (open/closed, block id rotation) behind two methods:

    * :meth:`on_delta` — absorb one streaming chunk's delta, return any
      events to emit (``ReasoningStart`` on first reasoning text, then a
      ``ReasoningDelta`` per chunk).
    * :meth:`close` — idempotently end any open block and rotate the id.
      Call this before emitting text / tool_use, and once more when the
      stream terminates.
    """

    def __init__(self) -> None:
        self._block_id: str = str(uuid.uuid4())
        self._open: bool = False

    @property
    def is_open(self) -> bool:
        return self._open

    def on_delta(self, delta: ChoiceDelta) -> list[StreamBaseResponse]:
        """Return events for the reasoning text carried by *delta*.

        Empty list when the chunk carries no reasoning payload, so this is
        safe to call on every chunk without guarding at the call site.
        """
        ext = OpenRouterDeltaExtension.from_delta(delta)
        text = ext.visible_text()
        if not text:
            return []
        events: list[StreamBaseResponse] = []
        if not self._open:
            events.append(StreamReasoningStart(id=self._block_id))
            self._open = True
        events.append(StreamReasoningDelta(id=self._block_id, delta=text))
        return events

    def close(self) -> list[StreamBaseResponse]:
        """Emit ``StreamReasoningEnd`` for the open block (if any) and rotate.

        Idempotent — returns ``[]`` when no block is open.  The id rotation
        guarantees the next reasoning block starts with a fresh id rather
        than reusing one already closed on the wire.
        """
        if not self._open:
            return []
        event = StreamReasoningEnd(id=self._block_id)
        self._open = False
        self._block_id = str(uuid.uuid4())
        return [event]
