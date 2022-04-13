import asyncio
import discord
from discord.ext import commands
import os
# import traceback
import re
import emoji
import json
import r

prefix = os.getenv('DISCORD_BOT_PREFIX', default='$')
token = os.environ['DISCORD_BOT_TOKEN']
voicevox_key = os.environ['VOICEVOX_KEY']
voicevox_speaker = os.getenv('VOICEVOX_SPEAKER', default='2')
client = commands.Bot(command_prefix=prefix)
db = r.connect()
with open('emoji_ja.json', encoding='utf-8') as file:
    emoji_dataset = json.load(file)

@client.event
async def on_ready():
    presence = "ステンバーイ..."
    await client.change_presence(activity=discord.Game(name=presence))

@client.command()
async def 接続(ctx: commands.Context):
    if ctx.message.guild:
        if ctx.author.voice is None:
            await ctx.send('ボイスチャンネルに接続してから呼び出してください。')
        else:
            if ctx.guild.voice_client:
                if ctx.author.voice.channel == ctx.guild.voice_client.channel:
                    await ctx.send('接続済みです。')
                else:
                    await ctx.voice_client.disconnect()
                    await asyncio.sleep(0.5)
                    await ctx.author.voice.channel.connect()
            else:
                await ctx.author.voice.channel.connect()

@client.command()
async def 切断(ctx: commands.Context):
    if ctx.message.guild:
        if ctx.voice_client is None:
            await ctx.send('ボイスチャンネルに接続していません。')
        else:
            await ctx.voice_client.disconnect()

@client.event
async def on_message(message):
    if message.guild.voice_client:
        if not message.author.bot:
            if not message.content.startswith(prefix):
                text = message.content

                uname = r.get_user_name(message.author.discriminator)
                if uname:
                    text = uname + '、' + text
                else:
                    text = message.author.name + '、' + text

                # Replace new line
                text = text.replace('\n', '、')

                # Replace mention to user
                pattern = r'<@!?(\d+)>'
                match = re.findall(pattern, text)
                for user_id in match:
                    user = await client.fetch_user(user_id)
                    user_name = f'、{user.name}へのメンション、'
                    uname = r.get_user_name(user.discriminator)
                    if uname:
                        user_name = f'、{uname}へのメンション、'
                    text = re.sub(rf'<@!?{user_id}>', user_name, text)

                # Replace mention to role
                pattern = r'<@&(\d+)>'
                match = re.findall(pattern, text)
                for role_id in match:
                    role = message.guild.get_role(int(role_id))
                    role_name = f'、{role.name}へのメンション、'
                    text = re.sub(f'<@&{role_id}>', role_name, text)

                # Replace Unicode emoji
                text = re.sub(r'[\U0000FE00-\U0000FE0F]', '', text)
                text = re.sub(r'[\U0001F3FB-\U0001F3FF]', '', text)
                for char in text:
                    if char in emoji.UNICODE_EMOJI['en'] and char in emoji_dataset:
                        text = text.replace(char, emoji_dataset[char]['short_name'])

                # Replace Discord emoji
                pattern = r'<:([a-zA-Z0-9_]+):\d+>'
                match = re.findall(pattern, text)
                for emoji_name in match:
                    emoji_read_name = emoji_name.replace('_', ' ')
                    text = re.sub(rf'<:{emoji_name}:\d+>', f'、{emoji_read_name}、', text)

                # Replace URL
                pattern = r'https://tenor.com/view/[\w/:%#\$&\?\(\)~\.=\+\-]+'
                text = re.sub(pattern, '画像', text)
                pattern = r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+(\.jpg|\.jpeg|\.gif|\.png|\.bmp)'
                text = re.sub(pattern, '、画像', text)
                pattern = r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+'
                text = re.sub(pattern, '、URL', text)

                # Replace spoiler
                pattern = r'\|{2}.+?\|{2}'
                text = re.sub(pattern, '伏せ字', text)

                # Replace laughing expression
                if text[-1:] == 'w' or text[-1:] == 'W' or text[-1:] == 'ｗ' or text[-1:] == 'W':
                    while text[-2:-1] == 'w' or text[-2:-1] == 'W' or text[-2:-1] == 'ｗ' or text[-2:-1] == 'W':
                        text = text[:-1]
                    text = text[:-1] + '、ワラ'

                # Add attachment presence
                for attachment in message.attachments:
                    if attachment.filename.endswith((".jpg", ".jpeg", ".gif", ".png", ".bmp")):
                        text += '、画像'
                    else:
                        text += '、添付ファイル'

                mp3url = f'https://api.su-shiki.com/v2/voicevox/audio/?text={text}&key={voicevox_key}&speaker={voicevox_speaker}&intonationScale=1'
                while message.guild.voice_client.is_playing():
                    await asyncio.sleep(0.5)
                message.guild.voice_client.play(discord.FFmpegPCMAudio(mp3url))
    await client.process_commands(message)

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None:
        if member.id == client.user.id:
            presence = "チャット読み上げまっす"
            await client.change_presence(activity=discord.Game(name=presence))
        else:
            if member.guild.voice_client is None:
                await asyncio.sleep(0.5)
                # await after.channel.connect()
            else:
                if member.guild.voice_client.channel is after.channel:
                    uname = r.get_user_name(member.discriminator)
                    if uname:
                        text = uname + 'さんが入室しました'
                    else:
                        text = member.name + 'さんが入室しました'
                    mp3url = f'https://api.su-shiki.com/v2/voicevox/audio/?text={text}&key={voicevox_key}&speaker={voicevox_speaker}&intonationScale=1'
                    while member.guild.voice_client.is_playing():
                        await asyncio.sleep(0.5)
                    member.guild.voice_client.play(discord.FFmpegPCMAudio(mp3url))
    elif after.channel is None:
        if member.id == client.user.id:
            presence = "ステンバーイ..."
            await client.change_presence(activity=discord.Game(name=presence))
        else:
            if member.guild.voice_client:
                if member.guild.voice_client.channel is before.channel:
                    if len(member.guild.voice_client.channel.members) == 1:
                        await asyncio.sleep(0.5)
                        await member.guild.voice_client.disconnect()
                    else:
                        uname = r.get_user_name(member.discriminator)
                        if uname:
                            text = uname + 'さんが退室しました'
                        else:
                            text = member.name + 'さんが退室しました'
                        mp3url = f'https://api.su-shiki.com/v2/voicevox/audio/?text={text}&key={voicevox_key}&speaker={voicevox_speaker}&intonationScale=1'
                        while member.guild.voice_client.is_playing():
                            await asyncio.sleep(0.5)
                        member.guild.voice_client.play(discord.FFmpegPCMAudio(mp3url))
    elif before.channel != after.channel:
        if member.guild.voice_client:
            if member.guild.voice_client.channel is before.channel:
                if len(member.guild.voice_client.channel.members) == 1 or member.voice.self_mute:
                    await asyncio.sleep(0.5)
                    await member.guild.voice_client.disconnect()
                    await asyncio.sleep(0.5)
                    await after.channel.connect()

@client.event
async def on_command_error(ctx: commands.Context, error):
    # orig_error = getattr(error, 'original', error)
    # error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send("コマンドが間違っているかも...")

@client.command()
async def 呼び方変更(ctx: commands.Context, uid: str, new_call: str):
    # uidを検索して存在するか確認
    is_find = False
    for m in ctx.message.guild.members:
        if m.discriminator == uid:
            is_find = True
            if db.set(uid, new_call):
                await ctx.send(f"{m.name} さんの呼び方を「{new_call}」に変更したよ。")
    if is_find is False:
        await ctx.send("タグが間違っているか、存在しないかも...")


@client.command()
async def ヘルプ(ctx: commands.Context):
    embed = discord.Embed(title=f"```{prefix} + コマンドで命令できます！```", color=0x00aa00)
    embed.set_author(name=f"◆◇◆{client.user.name}の使い方◆◇◆")
    embed.add_field(name=f"```{prefix}接続```", value="ボイスチャンネルに接続します。", inline=False)
    embed.add_field(name=f"```{prefix}切断```", value="ボイスチャンネルから切断します。", inline=False)
    embed.add_field(name=f"```{prefix}呼び方変更 タグ 新しい呼び方```", value=f"人の呼び方を変更します。タグは「名前#1234」の数字の部分。\n 例：__{ctx.bot.user}__の場合 ```{prefix}呼び方変更 {ctx.bot.user.discriminator} やすお```", inline=False)
    await ctx.send(embed=embed)

# デバッグ用コマンド
# @client.command()
# async def t(ctx: commands.Context):
#     user = ctx.message.guild.members[1]
#     # pprint.pprint(dir(ctx.message.guild.members[0]))
#     print("***********************")
#     print(user.discriminator)
#     print(type(user.discriminator))
#     print(str(user))

client.run(token)
