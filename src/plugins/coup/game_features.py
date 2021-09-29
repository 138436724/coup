"""
其他游戏进程必须内容
"""


async def check_num(message: str) -> int:
    if '1' in message or '一' in message:
        return 1
    elif '2' in message or '二' in message or '两' in message or '俩' in message:
        return 2
    elif '3' in message or '三' in message:
        return 3
    elif '4' in message or '四' in message:
        return 4
    elif '5' in message or '五' in message:
        return 5
    elif '6' in message or '六' in message:
        return 6
    elif '7' in message or '七' in message:
        return 7
    else:
        return -1
