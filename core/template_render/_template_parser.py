import math
import json
import random
import secrets
import hashlib
import numpy as np

from ..global_config_manager import GlobalConfigs
from ..user_data_managers.user_config_manager import UserConfigs
from ..assist_struct import RequestUserInfo
from .._info import __version__
from ..clients.model_info import ModelInfo
from jinja2 import Template
from ..auxiliary.text import (
    escape_string
)
from loguru import logger
from datetime import datetime, timedelta, timezone
from ..auxiliary.time import (
    get_timezone_offset,
    calculation_date_countdown,
    format_time_duration,
    date_to_zodiac,
    tz_timestamp,
    calculate_age,
    calculate_precise_age
)
from uuid import uuid4
from typing import Any, Literal
from ..clients.directives import (
    load_prompt_directive,
    load_prompt_directive_from_config,
    prompt_directive_from_config
)

class TemplateParser:
    def __init__(
            self,
            model: ModelInfo | None = None,
            user_info: RequestUserInfo | None = None,
            global_config: GlobalConfigs | None = None,
            user_config: UserConfigs | None = None,
        ):
        self._model = model or ModelInfo()
        self._user_info = user_info or RequestUserInfo()
        self._global_config = global_config or GlobalConfigs()
        self._user_config = user_config or UserConfigs()

    async def render(
            self,
            text: str,
            /,
            **kwargs: Any
        ) -> str:
        if not text:
            return ""
        try:
            environment = self._global_config.text_template.sandbox.get_jinja_env()
            template: Template = environment.from_string(
                source = text
            )
            return await template.render_async(
                **kwargs,
            )
        except Exception as e:
            logger.error(
                "Template Render Error: {error}",
                error = e
            )
            raise

    @staticmethod
    def daily_seed(time: datetime) -> int:
        return time.year ^ time.month ^ time.day
    
    @staticmethod
    def int_to_bytes(n: int, byteorder: Literal["big", "little"] = "big", signed: bool = False) -> bytes:
        length = (n.bit_length() + 7) // 8
        if signed and n < 0:
            length = (n.bit_length() + 8) // 8
        return n.to_bytes(length, byteorder, signed=signed)
    
    @classmethod
    def see_fortune(cls, now: datetime, user_ids: list[str]):
        daily_seed = cls.daily_seed(now)
        hash_value = hashlib.pbkdf2_hmac(
            "sha256",
            cls.int_to_bytes(daily_seed),
            ("\n".join(user_ids)).encode("utf-8"),
            10 ** 5
        )
        seed = int.from_bytes(hash_value, "big")
        rand = random.Random(seed)
        fortunes: dict[str, float] = {
            "Money": rand.random(),
            "Love": rand.random(),
            "Work": rand.random(),
            "Health": rand.random(),
            "Social": rand.random(),
            "Study": rand.random(),
            "Travel": rand.random(),
        }
        average = sum(fortunes.values()) / len(fortunes)
        text_buffer = [f"{key} Fortune: {value:.2%}" for key, value in fortunes.items()]
        extreme_luck_factor = ((average-0.5)**2) / 0.25
        return (
            f"Extreme Luck Factor: {extreme_luck_factor:.2%}\n"
            f"Average Fortune: {average:.2%}\n" +
            "\n".join(text_buffer)
        )

    async def render_ex(
            self,
            text: str,
            user_id: str,
            **kwargs
        ) -> str:
        """
        渲染文本

        :param text: 待渲染的文本
        :param user_id: 用户ID
        :return: 渲染后的文本
        """
        tz_config = self._user_config.timezone
        if tz_config is None:
            tz_config = self._global_config.text_template.time.timezone
        
        now = datetime.now()

        if isinstance(tz_config, str):
            tz_offset = get_timezone_offset(
                timezone = tz_config,
                dt = now
            )
        else:
            tz_offset = timedelta(hours=tz_config)
        
        tz_now = tz_timestamp(
            timestamp = now,
            offset_timezone = tz_offset
        )
        
        def date_countdown(
                target_month:int,
                target_day:int,
                target_hour:int | None = None,
                target_minute:int | None = None,
                target_second:int | None = None,
                precise: bool = False,
                time_delta_output: bool = False,
            ) -> str | timedelta:
            time_delta = calculation_date_countdown(
                target_month = target_month,
                target_day = target_day,
                target_hour = target_hour,
                target_minute = target_minute,
                target_second = target_second,
                current_timestamp = tz_now,
                tz_offset = timezone(tz_offset),
            )
            
            if time_delta_output:
                return time_delta
            elif precise:
                return format_time_duration(time_delta.total_seconds(), use_abbreviation=True)
            else:
                return f"{time_delta.days} days"
        
        default_time_format = self._global_config.text_template.time.time_format

        daily_random = random.Random(
            self.daily_seed(tz_now)
        )
        
        return await self.render(
            text,
            user_id = user_id,
            pymath = math,
            date_countdown = date_countdown,
            escape_str = escape_string,
            version = self._global_config.text_template.version or __version__,
            model_name = self._model.name,
            model_id = self._model.id,
            model_uid = self._model.uid,
            model_detailed = self._model.detailed,
            model_group = self._model.parent,
            user_name = self._user_info.username,
            nick_name = self._user_info.nickname,
            user_custom_name = self._user_config.user_name,
            user_age = self._user_info.age,
            user_custom_age = self._user_config.user_age,
            user_gender = self._user_info.gender,
            user_custom_gender = self._user_config.user_gender,
            user_info = self._user_info.model_dump(exclude_none=True),
            see_fortune = lambda user_ids = None: self.see_fortune(tz_now, [user_id] + (user_ids or [])),
            zodiac = date_to_zodiac,
            time = lambda time_format = default_time_format: tz_now.strftime(time_format),
            now = tz_now,
            age = lambda birthday_year, birthday_month, birthday_day: calculate_age(
                int(birthday_year),
                int(birthday_month),
                int(birthday_day),
                current_timestamp = tz_now
            ),
            precise_age = lambda birthday_year, birthday_month, birthday_day, birthday_hour = None, birthday_minute = None, birthday_second = None: calculate_precise_age(
                int(birthday_year),
                int(birthday_month),
                int(birthday_day),
                int(birthday_hour) if birthday_hour is not None else None,
                int(birthday_minute) if birthday_minute is not None else None,
                int(birthday_second) if birthday_second is not None else None,
                current_timestamp = tz_now
            ),
            random = lambda min, max: random.randint(int(min), int(max)),
            randfloat = lambda min, max: random.uniform(float(min), float(max)),
            randchoice = lambda *args: random.choice(args),
            daily_random = lambda min, max: daily_random.randint(int(min), int(max)),
            daily_randfloat = lambda min, max: daily_random.uniform(float(min), float(max)),
            daily_randchoice = lambda *args: daily_random.choice(args),
            secrets_random = secrets.randbelow,
            secrets_randbits = secrets.randbits,
            secrets_token_hex = secrets.token_hex,
            secrets_token_urlsafe = secrets.token_urlsafe,
            secrets_token_bytes = secrets.token_bytes,
            secrets_random_choice = lambda *args: secrets.choice(args),
            generate_uuid = lambda: uuid4(),
            copy_text = lambda text, number, spacers = "": spacers.join([text] * int(number)),
            text_matrix = lambda text, columns, lines, spacers = " ", line_breaks = "\n": line_breaks.join(spacers.join([text] * int(columns)) for _ in range(int(lines))),
            random_matrix = np.random.rand,
            user_profile = self._user_config.user_profile if self._user_config.user_profile is not None else self._global_config.text_template.default_user_profile,
            user_configs = self._user_config.model_dump(exclude_none=True),
            load_directive = load_prompt_directive,
            directives = lambda base_type: self._load_prompt_directive_from_config(user_id, base_type),
            directive_ids = lambda base_type: self._prompt_directive_from_config(base_type),
            json_loads = json.loads,
            json_dumps = json.dumps,
            **kwargs
        )
    
    async def _load_prompt_directive_from_config(self, user_id: str, base_type: list[str]):
        directives = load_prompt_directive_from_config(
            base_type,
            self._user_config,
            self._global_config
        )
        async for directive in directives:
            yield await self.render_ex(
                text = directive,
                user_id = user_id,
            )
    
    def _prompt_directive_from_config(self, base_type: list[str]):
        directives = prompt_directive_from_config(
            base_type,
            self._user_config,
            self._global_config
        )
        for type, directive in directives:
            yield type, directive