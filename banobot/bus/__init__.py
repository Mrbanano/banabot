"""Message bus module for decoupled channel-agent communication."""

from banobot.bus.events import InboundMessage, OutboundMessage
from banobot.bus.queue import MessageBus

__all__ = ["MessageBus", "InboundMessage", "OutboundMessage"]
