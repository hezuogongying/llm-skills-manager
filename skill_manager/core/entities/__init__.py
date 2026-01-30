"""Entities - 领域实体（单一职责原则）"""
from .skill import Skill, SkillMetadata
from .message import Message, MessageRole

__all__ = ['Skill', 'SkillMetadata', 'Message', 'MessageRole']
