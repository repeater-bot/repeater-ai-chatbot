from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import overload, Iterable, Any
from copy import deepcopy
from openai.types.chat import ChatCompletionMessageParam
from .._exceptions import *
from ._content_role import ContentRole
from ._content_unit import ContentUnit
from ._content_block import ContentBlock
from ...auxiliary.type_checker import is_iterable

class Context(BaseModel):
    """
    上下文对象
    """
    model_config = ConfigDict(
        validate_assignment = True
    )

    prompt: ContentUnit | None = None
    context_list: list[ContentUnit] = Field(default_factory=list)

    def __bool__(self) -> bool:
        """
        判断上下文是否为空
        """
        return bool(self.prompt or self.context_list)

    @overload
    def __getitem__(self, index: int) -> ContentUnit:
        ...

    @overload
    def __getitem__(self, index: slice) -> Context:
        ...
    
    def __getitem__(self, index: int | slice):
        """
        获取上下文列表中的指定项
        
        :param index: 索引
        :return: 指定项
        """
        if isinstance(index, int):
            return self.context_list[index]
        elif isinstance(index, slice):
            return Context(
                prompt=self.prompt,
                context_list=self.context_list[index]
            )
        else:
            raise TypeError("index must be int or slice")
    
    def __setitem__(self, index: int | slice, value: ContentUnit | Iterable[ContentUnit]):
        """
        设置上下文列表中的指定项
        
        :param index: 索引
        :param value: 值
        :return: 构建的对象
        """
        if isinstance(index, int) and isinstance(value, ContentUnit):
            self.context_list[index] = value
        elif not isinstance(index, int) and isinstance(value, ContentUnit):
            self.context_list[index] = [value]
        elif isinstance(index, slice) and is_iterable(value):
            self.context_list[index] = value
        else:
            raise TypeError("index must be int or slice")

    def __len__(self):
        """
        获取上下文列表的长度

        :return: 上下文列表的长度
        """
        if self.prompt:
            return self.context_item_length + 1
        return self.context_item_length
    
    def __iter__(self):
        """
        迭代上下文列表
        
        :return: 上下文列表的迭代器
        """
        # 先 yield 提示词
        if self.prompt:
            yield self.prompt
        # 再正常遍历 context_list
        for content in self.context_list:
            yield content
    
    def __reversed__(self):
        """
        反向迭代上下文列表

        :return: 上下文列表的反向迭代器
        """
        for content in reversed(self.context_list):
            yield content
        if self.prompt:
            yield self.prompt
    
    def clear(self, clear_prompt: bool = False) -> None:
        """
        清空上下文列表

        :param clear_prompt: 是否清空提示词
        :return: None
        """
        if clear_prompt and self.prompt is not None:
            self.prompt = None
        self.context_list.clear()
    
    def update_from_context(self, context: list[dict]) -> None:
        """
        从上下文列表更新上下文
        
        :param context: 上下文列表
        :return: 构建的对象
        """
        other = self.from_context(context)
        self.context_list = other.context_list
        self.prompt = other.prompt
    
    def rewrite(self, content: ContentUnit, index: int = -1) -> None:
        """
        重写上下文列表中的指定项

        :param content: 内容
        :return: 构建的对象
        """
        if not isinstance(content, ContentUnit):
            raise TypeError("content must be a ContentUnit object")
        if not isinstance(index, int):
            raise TypeError("index must be an integer")
        if abs(index) > len(self.context_list):
            raise IndexError("index out of range")
        
        self.context_list[index] = content
    
    @property
    def context_item_length(self):
        """
        获取上下文列表的长度
        
        :return: 上下文列表的长度
        """
        return len(self.context_list)

    @property
    def total_length(self) -> int:
        """
        获取上下文总长度
        
        :return: 上下文总长度
        """
        return (
            sum([len(content) for content in self.context_list])
            +
            (len(self.prompt) if self.prompt else 0)
        )
    
    @property
    def average_length(self) -> float:
        """
        获取上下文平均长度

        :return: 上下文平均长度
        """
        if len(self) == 0:
            return 0
        return self.total_length / len(self)

    def to_context(
            self,
            with_prompt: bool = False,
            remove_reasoning_prompt: bool = False,
            remove_created: bool = False,
            reduce_to_text: bool = False,
        ) -> list[ChatCompletionMessageParam]:
        """
        获取上下文

        :param with_prompt: 是否包含提示词
        :param remove_reasoner_prompt: 是否移除reasoner提示词
        :param remove_created: 是否移除创建时间戳
        :param reduce_to_text: 是否将上下文内容退化为纯文本
        """
        context_list = []
        if with_prompt and self.prompt:
            if reduce_to_text:
                self.prompt = self.prompt.reduce_to_text()
            context_list.append(
                self.prompt.to_content(
                    remove_reasoning_prompt = remove_reasoning_prompt,
                    remove_created = remove_created
                )
            )
        if self.context_list:
            for content in self.context_list:
                if reduce_to_text:
                    content = content.reduce_to_text()
                context_list.append(
                    content.to_content(
                        remove_reasoning_prompt,
                        remove_created
                    )
                )
        return context_list
    
    @property
    def context(self) -> list[ChatCompletionMessageParam]:
        """
        获取上下文
        """
        return self.to_context(
            with_prompt = False,
            remove_reasoning_prompt = False,
            remove_created = True,
            reduce_to_text = False
        )

    def split_to_pairs(self) -> list[list[ContentUnit]]:
        """
        拆分上下文为对话对
        """
        context = self.context_list
        pairs: list[list[ContentUnit]] = []
        for content in context:
            if content.role == ContentRole.USER:
                pairs.append([content])
            elif content.role != ContentRole.USER:
                if not pairs:
                    pairs.append([])
                
                pairs[-1].append(content)
        return pairs
    
    def withdraw(self, length: int | None = None):
        """
        撤销指定长度的内容

        :param length: 撤销长度
        :return: 撤销的内容
        """
        if length is None:
            pop_items: list[ContentUnit] = []
            
            # 安全检查
            if not self.context_list:
                return Context()
            try:
                # 第一步：pop 直到不是用户消息
                while (
                    self.context_list and 
                    self.last_content is not None and
                    self.last_content.role == ContentRole.USER
                ):
                    pop_items.append(self.context_list.pop())
                
                # 第二步：pop 非用户消息
                while (
                    self.context_list and 
                    self.last_content is not None and
                    self.last_content.role != ContentRole.USER
                ):
                    pop_items.append(self.context_list.pop())
                
                # 第三步：pop 相关联的用户消息
                while (
                    self.context_list and 
                    self.last_content is not None and
                    self.last_content.role == ContentRole.USER
                ):
                    pop_items.append(self.context_list.pop())
            except IndexError:
                pass
            
            return Context(
                prompt = None,
                context_list = pop_items[::-1],
            )
        elif isinstance(length, int):
            if length > len(self.context_list):
                raise ValueError("length is too long")
            if length <= 0:
                raise ValueError("length is too short")
            
            # 检查索引是否在上下文范围内
            if 0 <= length < len(self.context_list):
                return self.pop_last_n(length)
            else:
                raise IndexError("Index out of range")
        else:
            raise TypeError("length must be int or None")
    
    def insert(self, content_unit: ContentUnit, index: int | None = None):
        """
        插入内容单元到上下文列表中

        :param content_unit: 内容单元
        :param index: 插入位置，默认为None，表示插入到末尾
        :return: 当前对象
        """
        if index is None:
            self.context_list.append(content_unit)
        elif abs(index) <= len(self.context_list):
            raise IndexError("Index out of range")
        else:
            self.context_list.insert(index, content_unit)
        return self
    
    def role_map(self, role_map: dict[ContentRole, ContentRole | None]):
        """
        将内容单元的 role 映射到新的 role

        :param role_map: 角色映射表
        :return: 当前对象
        """
        context_list: list[ContentUnit] = []
        for content_unit in self.context_list:
            if content_unit.role in role_map:
                role = role_map[content_unit.role]
                if role is None:
                    continue
                else:
                    content_unit.role = role
            context_list.append(content_unit)
        self.context_list = context_list
        return self
    
    @property
    def last_content(self) -> ContentUnit | None:
        """
        获取最后一个上下文单元
        """
        if not self.context_list:
            return None
        return self.context_list[-1]
    
    @last_content.setter
    def last_content(self, content: ContentUnit) -> None:
        """
        设置最后一个上下文单元

        :param content: 上下文单元
        """
        if not self.context_list:
            self.context_list.append(content)
        else:
            self.context_list[-1] = content
    
    def append(self, content: ContentUnit) -> None:
        """
        添加上下文单元
        """
        self.context_list.append(content)
    
    def extend(self, content: Context | list[ContentUnit]) -> None:
        """
        扩展上下文单元

        :param content: 上下文单元或上下文单元列表
        """
        if isinstance(content, Context):
            self.context_list.extend(content.context_list)
        elif isinstance(content, list):
            self.context_list.extend(content)
        else:
            raise TypeError("content must be a list of ContentUnit or ContextObject")
    
    def pop(self, index: int = -1) -> ContentUnit:
        """
        弹出一个上下文单元

        :param index: 弹出第几个上下文单元，默认为最后一个
        :return: 弹出的上下文单元
        :raises IndexOutOfRangeError: 如果index超出范围，则抛出该异常
        """
        if abs(index) > len(self.context_list):
            raise IndexOutOfRangeError("index out of range")
        
        return self.context_list.pop(index)
    
    def pop_last_n(self, n: int) -> list[ContentUnit]:
        """
        弹出最后n个上下文单元

        :param n: 弹出的元素个数
        :return: 弹出的元素列表
        :raises IndexOutOfRangeError: 数量超出范围
        """
        if n > len(self.context_list) or n < 0:
            raise IndexOutOfRangeError("index out of range")
        
        pop_list:list[ContentUnit] = self.context_list[-n:]
        self.context_list = self.context_list[:-n]
        return pop_list
    
    def pop_begin_n(self, n: int) -> list[ContentUnit]:
        """
        弹出头部的n个元素

        :param n: 弹出的元素个数
        :return: 弹出的元素列表
        :raise IndexOutOfRangeError: 数量超出范围
        """
        if n > len(self.context_list) or n < 0:
            raise IndexOutOfRangeError("index out of range")
        
        pop_list = self.context_list[:n]
        self.context_list = self.context_list[n:]
        return pop_list
    
    @property
    def is_empty(self) -> bool:
        """
        上下文是否为空
        """
        return not self.prompt and not self.context_list
    
    def shrink(self, length: int, ensure_role_at_top: ContentRole = ContentRole.USER):
        """
        缩小上下文长度
        
        :param length: 上下文总字数
        :param ensure_role_at_top: 确保指定角色在顶部
        :raise IndexOutOfRangeError: 数量超出范围
        """
        if not isinstance(length, int):
            raise TypeError("length must be int")
        if not isinstance(ensure_role_at_top, ContentRole):
            raise TypeError("ensure_role_at_top must be ContentRole")

        if length < 0:
            raise IndexOutOfRangeError("length must be positive")

        # 当length大于等于实际长度时，不做任何事
        if abs(length) >= self.total_length:
            return
        
        while self.total_length > length:
            self.pop_begin_n(1)
        
        if self.context_list and self.context_list[0].role != ensure_role_at_top:
            # 从头部寻找第一个为ensure_role_at_top的ContextUnit
            for i in range(len(self.context_list)):
                if self.context_list[i].role == ensure_role_at_top:
                    self.context_list = self.context_list[i:]
                    break
            else:
                raise IndexOutOfRangeError(f"Role {ensure_role_at_top} not found in context_list")
    
    def copy(self) -> Context:
        """
        复制对象

        :return: 复制后的对象
        """
        return Context(
            prompt = self.prompt,
            context_list = self.context_list.copy(),
        )
    
    def deepcopy(self) -> Context:
        """
        深度复制对象

        :return: 深度复制后的对象
        """
        return Context(
            prompt = deepcopy(self.prompt),
            context_list = deepcopy(self.context_list),
        )
    
    @classmethod
    def from_context(cls, context: list[dict[str, Any]]) -> Context:
        """
        从上下文列表构建对象
        
        :param context: 上下文列表
        :return: 构建的对象
        """
        if not isinstance(context, list):
            raise TypeError("context must be list")
        context_obj = cls()
        context_obj.context_list = []
        if not context:
            return context_obj
        for content in context:
            if not isinstance(content, dict):
                raise TypeError("context must be list of dict")
            context_obj.context_list.append(ContentUnit(**content))
        return context_obj
    
    def remove_reasoning_content(self) -> Context:
        """
        移除推理内容

        :return: 移除推理内容后的对象
        """
        context_list: list[ContentUnit] = []
        for content in self.context_list:
            if content.reasoning_content:
                copy_content = content.model_copy(deep=True)
                copy_content.reasoning_content = None
                context_list.append(copy_content)
            else:
                context_list.append(content)

        return Context(
            prompt = self.prompt,
            context_list = context_list,
        )
    
    def time_range(self, begin: int | float, end: int | float) -> Context:
        """
        获取指定时间范围内的上下文内容

        :param begin: 开始时间
        :param end: 结束时间
        :return: 指定时间范围内的上下文内容
        """
        context = Context()

        if self.prompt is not None:
            if begin <= self.prompt.created.timestamp() <= end:
                context.prompt = self.prompt
        
        for content in self.context_list:
            if begin <= content.created.timestamp() <= end:
                context.append(content)

        return context