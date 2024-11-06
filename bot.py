import discord
import pytz
from config import Config
from decimal import Decimal
from discord.ext import commands
from discord import app_commands
from editDatabase import CRUD

tz = pytz.timezone("Asia/Seoul") #타임존 변수

db = CRUD()

token = Config.token
id = Config.id

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

GUILD_ID = discord.Object(id=id)

def make_userlist(table): # table에서 id만 모아둔 리스트 만들기
    userid = db.readDB(schema='public',table=table,colum='id',condition=None)
    idlist = list()
    for i in range(len(userid)):
        if(userid[i][0] not in idlist):
            idlist.append(userid[i][0])

    return idlist

def make_attdatelist(user): # 출석부에서 attdate만 모아둔 리스트 만들기
    attdate = db.readDB(schema='public',table='attendance',colum='attdate',condition=f'id = {user.id}')
    attdatelist = list()
    for i in range(len(attdate)):
        attdatelist.append(attdate[i][0])
        
    return attdatelist
  
@client.tree.command(name="거꾸로", description="뒤에 쓴 내용을 뒤집습니다.", guild=GUILD_ID)
async def word(interaction: discord.Interaction, say: str):
    say = say[::-1]
    await interaction.response.send_message(f'{say}')
    
@client.tree.command(name="출석체크", description="출석체크용 명령어입니다.", guild=GUILD_ID)
async def attend(interaction: discord.Interaction):
    user = interaction.user
    datatime = interaction.created_at.astimezone(tz=tz)
    dateNow = datatime.strftime('%Y-%m-%d')
    timeNow = datatime.strftime('%H:%M:%S')
    idlist = make_userlist('attendance')
    attdatelist = make_attdatelist(user)
    try:
        db.deleteDB(schema='public',table='attendance',condition='attdate = \'0000-00-00\'')
    except:
        pass
    
    if(user.id not in idlist):
        await interaction.response.send_message(f'출석부에 {user.mention}님이 없어요. \'/유저추가\' 를 이용해 보세요.')
    elif((user.id in idlist) & (dateNow in attdatelist)):
        atttime = db.readDB(schema='public',table='attendance',colum='atttime',condition=f'id = {user.id} AND attdate = \'{dateNow}\'')
        await interaction.response.send_message(f'오늘은 이미 {atttime[0][0]}에 출석했어요!')
    else:
        db.insertDB(schema='public',table='attendance',colum=None,data=(f'{user.id}',f'{user.name}',f'{dateNow}',f'{timeNow}'))
        await interaction.response.send_message(f'{user.mention}님이 '+timeNow+'에 출석했습니다.')
        
@client.tree.command(name="출석취소", description="출석체크를 잘못했다면 이용해보세요.", guild=GUILD_ID)
async def attendcancel(interaction: discord.Interaction):
    user = interaction.user
    datatime = interaction.created_at.astimezone(tz=tz)
    dateNow = datatime.strftime('%Y-%m-%d')
    atttime = db.readDB(schema='public',table='attendance',colum='atttime',condition=f'id = {user.id} AND attdate = \'{dateNow}\'')
    attdatelist = make_attdatelist(user)
    
    if(dateNow in attdatelist):
        db.deleteDB(schema='public',table='attendance',condition=f'id = {user.id} AND attdate = \'{dateNow}\'')
        await interaction.response.send_message(f'{user.mention}님 오늘 '+atttime[0][0]+'에 출석한 기록을 지웠어요.')
    else:
        await interaction.response.send_message(f'{user.mention}님 오늘 출석한 기록이 없어요! \'/출석체크\'를 했는지 확인해 보세요.')
    
    
@client.tree.command(name='유저추가', description='출석부에 내 이름을 적습니다. 이미 출석부에 이름이 있다면 /출석체크를 이용해주세요.', guild=GUILD_ID)
async def newUser(interaction: discord.Interaction):
    user = interaction.user    
    idlist = make_userlist('attendance')
    
    if(user.id in idlist):
        await interaction.response.send_message(f'{user.mention}님의 이름이 이미 출석부에 있어요!')
    else:
        db.insertDB(schema='public',table='attendance',colum=None,data=(f'{user.id}',f'{user.name}'))
        await interaction.response.send_message(f'{user.mention}님의 이름을 출석부에 적었어요!')
    
@client.tree.command(name='유저제거', description='for develop', guild=GUILD_ID)
async def delUser(interaction: discord.Interaction):
    user = interaction.user
    idlist = make_userlist('attendance')

    if(user.id not in idlist):
        await interaction.response.send_message(f'{user.mention}님은 출석부에 없어요!')
    else:
        db.deleteDB(schema='public',table='attendance',condition=f'id = {user.id}')
        await interaction.response.send_message(f'{user.mention}님의 이름을 출석부에서 뺐습니다.')
    
@client.tree.command(name='출석시간등록', description='설명', guild=GUILD_ID)    
async def editTime(interaction: discord.Interaction, mon: str, tue: str, wed: str, thu: str, fri: str, sat: str, sun: str,):
    user = interaction.user
    idlist = make_userlist('studentdb')
    
    if(user.id in idlist):
        db.deleteDB(schema='public',table='studentdb',condition=f'id = {user.id}')
        await interaction.response.send_message(f'{user.mention}님 아직 시간을 바꾸는 기능이 없어요 ㅠㅠ 대신 시간을 초기화 해드렸으니 다시 입력해주세요.')
    else:
        db.insertDB(schema='public',table='studentdb',colum=None,data=(user.id,user.name,mon,tue,wed,thu,fri,sat,sun))
        await interaction.response.send_message(f'{user.mention}님의 출석시간을 설정했어요.')

@client.tree.command(name='test',guild=GUILD_ID)
async def test(interaction: discord.Interaction):
    user = interaction.user
    datatime = interaction.created_at.astimezone(tz=tz)
    dateNow = datatime.strftime('%Y-%m-%d')
    atttime = db.readDB(schema='public',table='attendance',colum='atttime',condition=f'id = {user.id} AND attdate = \'{dateNow}\'')
    await interaction.response.send_message(f'{atttime}')

client.run(token)