"""Message bus module for decoupled channel-agent communication."""

from banabot.bus.events import InboundMessage, OutboundMessage
from banabot.bus.queue import MessageBus

__all__ = ["MessageBus", "InboundMessage", "OutboundMessage"]
