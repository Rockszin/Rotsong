import asyncio
import datetime
from typing import Optional
import disnake
from disnake.ext import commands
from utils.client import BotCore
import psutil
import humanize
from itertools import cycle
from random import shuffle
from os import getpid
import platform


class Misc(commands.Cog):

    def __init__(self, bot: BotCore):
        self.bot = bot
        self.source_owner: Optional[disnake.User] = None
        self.activities = None
        self.task = self.bot.loop.create_task(self.presences())

    def placeholders(self, text: str):

        if not text:
            return ""

        return text \
            .replace("{users}", str(len([m for m in self.bot.users if not m.bot]))) \
            .replace("{playing}", str(len(self.bot.music.players))) \
            .replace("{guilds}", str(len(self.bot.guilds))) \
            .replace("{uptime}", str(datetime.timedelta(seconds=(disnake.utils.utcnow() - self.bot.uptime)
                                                        .total_seconds())).split('.')[0])


    async def presences(self):

        if not self.activities:

            activities = []

            for i in self.bot.config.get("LISTENING_PRESENCES", "").split("||"):
                if i:
                    activities.append({"name":i, "type": "listening"})

            for i in self.bot.config.get("WATCHING_PRESENCES", "").split("||"):
                if i:
                    activities.append({"name": i, "type": "watching"})

            for i in self.bot.config.get("PLAYING_PRESENCES", "").split("||"):
                if i:
                    activities.append({"name": i, "type": "playing"})

            shuffle(activities)

            self.activities = cycle(activities)

        while True:

            await self.bot.wait_until_ready()

            activity_data = next(self.activities)

            if activity_data["type"] == "listening":
                activity = disnake.Activity(type=disnake.ActivityType.listening, name=self.placeholders(activity_data["name"]))

            elif activity_data["type"] == "watching":
                activity = disnake.Activity(type=disnake.ActivityType.watching, name=self.placeholders(activity_data["name"]))

            else:
                activity = disnake.Game(name=self.placeholders(activity_data["name"]))

            await self.bot.change_presence(activity=activity)

            await asyncio.sleep(300)


    @commands.Cog.listener("on_guild_join")
    async def guild_add(self, guild: disnake.Guild):

        if not guild.system_channel:
            return

        embed = disnake.Embed(
            description="Ol??.\nPara ver todos os meus meus comandos use **/help**\n\n"
                        f"Caso os comandos n??o apare??am, use o comando:\n/authorizebot",
            color=self.bot.get_color(guild.me)
        )

        await guild.system_channel.send(embed=embed)

 
    @commands.slash_command(description="Mostrar todos os meus comandos.") ##COMANDO HELP
    async def help(self, inter: disnake.ApplicationCommandInteraction):

        await inter.send(
            
            embed = disnake.Embed(
                colour=self.bot.get_color(inter.guild.me),
                 description="**???? | Meus comandos:**\n\n" \
                        f"> **/about** `Exibir informa????es sobre o bot.`\n"
                        f"> **/authorizebot** `Caso os comandos n??o apare??am use isso!`\n"
                        f"> **/add_dj** `Adicionar um membro ?? lista de DJ??s na sess??o atual do player.`\n"
                        f"> **/add_dj_role** `Adicionar um cargo para a lista de DJ??s do servidor.`\n"
                        f"> **/back** `Voltar para a m??sica a m??sica anterior (ou para o inicio da m??sica caso n??o tenha m??sicas tocando/na fila).`\n"
                        f"> **/change_node** `Migrar o player para outro servidor de m??sica.`\n"
                        f"> **/clear** `Limpar a fila de m??sica.`\n"
                        f"> **/connect** `Me conectar em um canal de voz ou me mover para um.`\n"
                        f"> **/invite** `Exibir meu link de convite.`\n"
                        f"> **/loop_amount** `Definir quantidade de repeti????es da m??sica atual.`\n"
                        f"> **/loop_mode** `Selecionar modo de repeti????o entre: atual/fila ou desativar.`\n"
                        f"> **/move** `Move uma m??sica para a posi????o especificada da fila.`\n"
                        f"> **/nightcore** `Ativar/Desativar o efeito nightcore (M??sica acelerada com tom mais agudo).`\n"
                        f"> **/nodeinfo** `Ver informa????es dos servidores de m??sicas.`\n"
                        f"> **/nonstop** `Ativar/Desativar o modo interrupta do player [24/7].`\n"
                        f"> **/nowplaying** `Reenvia a mensagem do player com a m??sica atual.`\n"
                        f"> **/pause** `Pausar a m??sica.`\n"
                        f"> **/play** `Tocar m??sica em um canal de voz.`\n"
                        f"> **/queue shuffle** `Misturar as m??sicas da fila.`\n"
                        f"> **/queue reverse** `Inverter a ordem das m??sica na fila.`\n"
                        f"> **/queue show** `Exibir as m??sicas que est??o na fila.`\n"
                        f"> **/readd** `Readicionar as m??sicas tocadas na fila.`\n"
                        f"> **/remove** `Remover uma m??sica especifica da fila.`\n"
                        f"> **/remove_dj_role** `Remover um cargo para a lista de DJ's do servidor.`\n"
                        f"> **/resume** `Retomar/Despausar a m??sica.`\n"
                        f"> **/rotate** `Rotacionar a fila para a m??sica especificada.`\n"
                        f"> **/search** `Buscar m??sica e escolher uma entre os resultados para tocar.`\n"
                        f"> **/seek** `Avan??ar/Retomar a m??sica para um tempo especifico.`\n"
                        f"> **/setupplayer** `Criar um canal dedicado para pedir m??sicas e deixar player fixo.`\n"
                        f"> **/skip** `Pular a m??sica atual que est?? tocando.`\n"
                        f"> **/skipto** `Pular para a m??sica especificada.`\n"
                        f"> **/stop** `Parar o player e me desconectar do canal de voz.`\n"
                        f"> **/volume** `Ajustar volume da m??sica.`\n"
                        f"> **/voteskip** `Votar para pular a m??sica atual.`\n",
            ),
            ephemeral=True
        ) ## COMANDO HELP

        


    @commands.slash_command(description="Exibir informa????es sobre mim.")
    async def about(self, inter: disnake.ApplicationCommandInteraction):

        if not self.source_owner:
            self.source_owner = await self.bot.get_or_fetch_user(422023674900512798)

        ram_usage = humanize.naturalsize(psutil.Process(getpid()).memory_info().rss)

        embed = disnake.Embed(
            description=f"**Sobre mim:**\n\n"
                        f"> **Estou em:** `{len(self.bot.guilds)} servidor(es)`\n"
                        f"> **Players ativos:** `{len(self.bot.music.players)}`\n"
                        f"> **Tipo de player usado:** `Lavalink`\n"
                        f"> **Estou na vers??o:** `ffcd132`\n"
                        f"> **Vers??o do Disnake:** `{disnake.__version__}`\n"
                        f"> **Vers??o do python:** `{platform.python_version()}`\n"
                        f"> **Ping:** `{round(self.bot.latency * 1000)}ms`\n"
                        f"> **Uso de RAM:** `{ram_usage}`\n"
                        f"> **Online h??:** `{str((datetime.timedelta(seconds=(disnake.utils.utcnow() - self.bot.uptime).total_seconds()))).split('.')[0]}`\n",
            color=self.bot.get_color(inter.guild.me)
        )

        try:
            embed.set_thumbnail(url=self.bot.user.avatar.with_static_format("png").url)
        except AttributeError:
            pass

        if self.bot.default_prefix:
            embed.description += f"> **Prefixo:** {self.bot.default_prefix}\n"

        try:
            avatar = self.bot.owner.avatar.with_static_format("png").url
        except AttributeError:
            avatar = self.bot.owner.default_avatar.with_static_format("png").url

        embed.set_footer(
            icon_url=avatar,
            text=f"Dev: {self.bot.owner}"
        )
        

        # resolvi add essa op????o...
        # mas caso use, por favor considere de alguma forma fornecer cr??dito :(
        if self.bot.config.get("HIDE_SOURCE_OWNER") != "false" and self.bot.owner.id == self.source_owner.id:
            embed.footer.text += f"I ??? YOU: {self.source_owner}"

        await inter.send(embed=embed)


    @commands.slash_command(description="Autorizar os comandos de / do bot no servidor.") ##AUTORIZAR COMANDOS
    async def authorizebot(self, inter: disnake.ApplicationCommandInteraction):

           await inter.send(
            
            embed = disnake.Embed(
                colour=self.bot.get_color(inter.guild.me),
                 description="**Este comando n??o ?? mais necess??rio ser usado (S?? use se os comandos n??o aparecerem parcialmente!).**\n\n" \
                        f"`Caso os comandos de barra n??o apare??am,` [`clique aqui`](https://discord.com/api/oauth2/authorize?client_id=923604031669157971&permissions=8&scope=bot%20applications.commands) `para me permitir "
                        "criar comandos de barra no servidor.`\n\n" \
                        "`Nota: Em alguns casos os comandos de barra podem demorar at?? uma hora pra aparecer em todos "
                        "os servidores. Caso queira usar os comandos de barra imediatamente neste servidor voc?? ter?? que "
                        f"me expulsar do servidor e em seguida me adicionar novamente atrav??s deste` [`link`](https://discord.com/api/oauth2/authorize?client_id=923604031669157971&permissions=8&scope=bot%20applications.commands)..."
            ),
            ephemeral=True
        ) ##AUTORIZAR COMANDOS

    @commands.user_command(name="avatar")
    async def avatar(self, inter: disnake.UserCommandInteraction):

        embeds = []

        assets = {}

        user = await self.bot.fetch_user(inter.target.id) if not inter.target.bot else self.bot.get_user(
            inter.target.id)

        if inter.target.guild_avatar:
            assets["Avatar (Server)"] = inter.target.guild_avatar.with_static_format("png")
        assets["Avatar (User)"] = user.avatar.with_static_format("png")
        if user.banner:
            assets["Banner"] = user.banner.with_static_format("png")

        for name, asset in assets.items():
            embed = disnake.Embed(description=f"{inter.target.mention} **[{name}]({asset.with_size(2048).url})**",
                                  color=self.bot.get_color(inter.guild.me))
            embed.set_image(asset.with_size(256).url)
            embeds.append(embed)

        await inter.send(embeds=embeds, ephemeral=True)

    def cog_unload(self):

        try:
            self.task.cancel()
        except:
            pass


def setup(bot: BotCore):
    bot.add_cog(Misc(bot))
