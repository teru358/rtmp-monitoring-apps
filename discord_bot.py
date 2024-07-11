# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from obs_operator import OBSOperator
from modules.scheduler import Scheduler
from modules.logger import LoggerConfig

def discord_bot(config_ini, stream_status):
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(
        command_prefix=config_ini['discord']['Command_Prefix'],
        intents=intents
    )
    obs_operator = OBSOperator(config_ini, stream_status)
    config = config_ini['discord']
    scheduler = Scheduler()
    logger = LoggerConfig.get_logger(discord_bot.__name__)
    logger.info('discord bot init')

    @bot.event
    async def on_ready():
        print(f'Logged on as {bot.user}!')

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        print('on message')
        await bot.process_commands(message)

    def is_in_target_channel(ctx):
        channels = [int(id) for id in config['Target_Channel_IDs'].split(',') if id.strip()]
        return ctx.channel.id in channels

    @bot.command(name='hello')
    async def hello(ctx):
        if not is_in_target_channel(ctx):
            return
        await ctx.reply('Hello!')

    @bot.command(name='stream')
    async def stream(ctx, args: str):
        if not config['obs_command_control'] :
            return
        if args in ['start', 'on']:
            # 配信開始送信
            # obs_operator.stream_start()
            await ctx.send('配信準備中')

        elif args in ['stop', 'end', 'off']:
            # 配信終了送信
            # obs_operator.stream_stop()
            await ctx.send('配信終了')

        elif args == 'live':
            obs_operator.stream_to_live()
            await ctx.send('配信開始')

        elif args == 'pause':
            obs_operator.stream_switching_pause()
            await ctx.send('待機を切り替えます')

        else:
            await ctx.send('incorrect argument!')

    @bot.command(name='pause')
    async def pause(ctx, args: str = None):
        if not is_in_target_channel(ctx):
            return
        if args == 'on' or args is None:
            obs_operator.scene_change_pause_on()
            await ctx.send('待機に切り替えます')

        elif args == 'off':
            obs_operator.scene_change_pause_off()
            await ctx.send('待機から戻ります')

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('コマンドがないです!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('コマンドの引数が変です!')
        else:
            await ctx.send(f'コマンドエラーです: {error}')

    return bot
