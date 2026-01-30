"""Interfaces - 接口定义（依赖倒置原则）"""
from .llm_backend import ILLMBackend, IMessage, IModelConfig

__all__ = ['ILLMBackend', 'IMessage', 'IModelConfig']
