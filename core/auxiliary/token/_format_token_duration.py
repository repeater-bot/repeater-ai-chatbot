from ..text import format_carry_duration, Preset, Level, FinalLevel

TOKEN_PRESET = Preset(
    levels = [
        Level("Tokens", "", 1024),
        Level("K Tokens", "K", 1024),
        Level("M Tokens", "M", 1024),
        Level("G Tokens", "G", 1024),
        Level("T Tokens", "T", 1024),
        Level("P Tokens", "P", 1024),
    ],
    final_level = FinalLevel(
        name = "E Tokens",
        abbr = "E"
    ),
    delimiter = " "
)

def format_token(
    token_count: int,
) -> str:
    formated_token_duration = format_carry_duration(
        value = token_count,
        preset = TOKEN_PRESET,
        use_abbreviation = True,
    )
    return f"{token_count}({formated_token_duration}Tokens)"