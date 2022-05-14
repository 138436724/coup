from cgitb import text
import httpx
from nonebot import on_command, on_endswith
# from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment

dujitang = on_command("毒鸡汤", priority=9)
caihongpi = on_command("彩虹屁",  priority=9)
zhananmoshi = on_command("渣男模式", priority=9)
zuanmoshi = on_command("祖安模式",  priority=9)

# r'https://nmsl.shadiao.app/api.php?level=min&lang=zh_cn',
# r'https://nmsl.shadiao.app/api.php?level=max&lang=zh_cn'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.81'
}


@dujitang.handle()
async def _(bot: Bot, event: Event, state: T_State):
    url = r'https://du.shadiao.app/api.php'
    text = await get_response(url)
    await dujitang.finish(text)


@caihongpi.handle()
async def _(bot: Bot, event: Event, state: T_State):
    url = r'https://chp.shadiao.app/api.php'
    text = await get_response(url)
    await dujitang.finish(text)


@zhananmoshi.handle()
async def _(bot: Bot, event: Event, state: T_State):
    url = r'https://api.lovelive.tools/api/SweetNothings'
    text = await get_response(url)
    await dujitang.finish(text)


@zuanmoshi.handle()
async def _(bot: Bot, event: Event, state: T_State):
    url = r"https://zuanbot.com/api.php?level=min&lang=zh_cn"
    text = await get_response(url)
    await dujitang.finish(text)


async def get_response(url):
    global headers
    response = httpx.get(url=url, headers=headers)
    response.encoding = 'UTF-8'
    return response.text
