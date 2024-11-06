import discord
import pytz
from config import Config
from discord.ext import commands
from discord import app_commands
from editDatabase import CRUD

tz = pytz.timezone("Asia/Seoul") #타임존 변수

db = CRUD()

token = Config.token
id = Config.id

def make_userlist(): # 출석부에서 id만 모아둔 리스트 만들기
    userid = db.readDB(schema='public',table='attendance',colum='id',condition=None)
    userlist = list()
    for i in range(len(userid)):
        userlist.append(userid[i][0])
        
    return userlist

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        
        try:
            guild = discord.Object(id=id)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')
            
        except Exception as e:
            print(f'Error syncing commands: {e}')
        
    async def on_message(self, message):
        if message.author == self.user:
            return
            
    async def on_reaction_add(self, reaction, user):
        await reaction.message.channel.send(f'{user}가 '+f'{reaction} 라고 반응했습니다.')

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=1303084624054059100)
  
@client.tree.command(name="거꾸로", description="뒤에 쓴 내용을 뒤집습니다.", guild=GUILD_ID)
async def word(interaction: discord.Interaction, say: str):
    say = say[::-1]
    await interaction.response.send_message(f'{say}')
    
@client.tree.command(name="출석체크", description="출석체크용 명령어입니다.", guild=GUILD_ID)
async def attend(interaction: discord.Interaction):
    user = interaction.user
    datatime = interaction.created_at.astimezone(tz=tz)
    attdate = db.readDB(schema='public',table='attendance',colum='attdate',condition=f'id = {user.id}')
    atttime = db.readDB(schema='public',table='attendance',colum='atttime',condition=f'id = {user.id}')
    timeNow = datatime.strftime('%H:%M:%S')
    dateNow = datatime.strftime('%Y-%m-%d')
    userlist = make_userlist()
    
    if(user.id not in userlist):
        await interaction.response.send_message(f'출석부에 {user.mention}님이 없어요. \'/유저추가\' 를 이용해 보세요')
    elif((user.id in userlist) & (dateNow == attdate[0][0])):
        await interaction.response.send_message(f'오늘은 이미 {atttime[0][0]}에 출석했어요!')
    else:
        db.updateDB(schema='public',table='attendance',colum='attdate',value=f'{dateNow}',condition=f'id = {user.id} AND {attdate[0][0]} != {dateNow}')
        attdate = db.readDB(schema='public',table='attendance',colum='attdate',condition=f'id = {user.id}')
        db.updateDB(schema='public',table='attendance',colum='atttime',value=f'{timeNow}',condition=f'id = {user.id} AND {attdate[0][0]} = {dateNow}')
        await interaction.response.send_message(f'{user.mention}님이 {datatime.hour}시 {datatime.minute}분 {datatime.second}초에 출석했습니다.')
        
@client.tree.command(name="출석취소", description="출석체크를 잘못했다면 이용해보세요.", guild=GUILD_ID)
async def attendcancel(interaction: discord.Interaction):
    user = interaction.user
    
    
@client.tree.command(name='유저추가', description='출석부에 내 이름을 적습니다. 이미 출석부에 이름이 있다면 /출석체크를 이용해주세요.', guild=GUILD_ID)
async def newUser(interaction: discord.Interaction):
    user = interaction.user    
    userlist = make_userlist()
    
    if(user.id in userlist):
        await interaction.response.send_message(f'{user.mention}님의 이름이 이미 출석부에 있어요!')
    else:
        db.insertDB(schema='public',table='attendance',colum=None,data=(f'{user.id}',f'{user.name}'))
        await interaction.response.send_message(f'{user.mention}님의 이름을 출석부에 적었어요!')
    
@client.tree.command(name='유저제거', description='for develop', guild=GUILD_ID)
async def newUser(interaction: discord.Interaction):
    user = interaction.user
    userlist = make_userlist()

    if(user.id not in userlist):
        await interaction.response.send_message(f'{user.mention}님은 출석부에 없어요!')
    else:
        db.deleteDB(schema='public',table='attendance',condition=f'id = {user.id}')
        await interaction.response.send_message(f'{user.mention}님의 이름을 출석부에서 뺐습니다.')
    
@client.tree.command(name='test',guild=GUILD_ID)
async def test(interaction: discord.Interaction):
    user = interaction.user
    datatime = interaction.created_at.astimezone(tz=tz)
    dateNow = datatime.strftime('%Y-%m-%d')
    timeNow = datatime.strftime('%H:%M:%S')
    attdate = db.readDB(schema='public',table='attendance',colum='attdate',condition=f'id = {user.id}')
    await interaction.response.send_message(dateNow == attdate[0][0])

client.run(token)