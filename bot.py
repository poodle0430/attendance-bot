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
weekdayindex = ['mon','tue','wed','thu','fri','sat','sun']

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

GUILD_ID = discord.Object(id=id)

class Client(commands.Bot):
    async def on_ready(self):
        try:
            self.tree.add_command(HelloGroup(name="greetings", description="인사 관련 명령어 그룹"), guild=GUILD_ID)
            self.tree.add_command(UserEditGroup(name="유저", description="유저 정보 관련 명령어 그룹"), guild=GUILD_ID)
            self.tree.add_command(AttandGroup(name="출석", description="출석 관련 명령어 그룹"), guild=GUILD_ID)
            self.tree.add_command(TimeGroup(name="출석시간", description="출석시간 관련 명령어 그룹"), guild=GUILD_ID)
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f'Synced {len(synced)} commands to guild {GUILD_ID.id}')
            
        except Exception as e:
            print(f'Error syncing commands: {e}')

        commands = await self.tree.fetch_commands(guild=GUILD_ID)
        print("Registered commands:")
        for command in commands:
            print(f"- {command.name}: {command.description}")
        
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return
            
    async def on_reaction_add(self, reaction, user):
        await reaction.message.channel.send(f'{user}가 '+f'{reaction} 라고 반응했습니다.')

class HelloGroup(app_commands.Group):
    @app_commands.command(name="hello",description="안녕")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message("안녕하세요!")

    @app_commands.command(name="goodbye",description="안녕")
    async def goodbye(self, interaction: discord.Interaction):
        await interaction.response.send_message("안녕히 가세요!")

class UserEditGroup(app_commands.Group):
    @app_commands.command(name='추가', description='출석부에 내 이름을 적습니다. 이미 출석부에 이름이 있다면 /출석체크를 이용해주세요.')
    async def newUser(self, interaction: discord.Interaction):
        user = interaction.user    
        idlist = make_userlist('attendance')
            
        if(user.id in idlist):
            await interaction.response.send_message(f'{user.mention}님의 이름이 이미 출석부에 있어요!')
        else:
            db.insertDB(schema='public',table='attendance',colum=None,data=(f'{user.id}',f'{user.name}'))
            await interaction.response.send_message(f'{user.mention}님의 이름을 출석부에 적었어요!')

    @app_commands.command(name='제거', description='for develop')
    async def delUser(self, interaction: discord.Interaction):
        user = interaction.user
        idlist = make_userlist('attendance')

        if(user.id not in idlist):
            await interaction.response.send_message(f'{user.mention}님은 출석부에 없어요!')
        else:
            db.deleteDB(schema='public',table='attendance',condition=f'id = {user.id}')
            await interaction.response.send_message(f'{user.mention}님의 이름을 출석부에서 뺐습니다.')


class AttandGroup(app_commands.Group):
    @app_commands.command(name="체크", description="출석체크용 명령어입니다.")
    async def attend(self, interaction: discord.Interaction):
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

    @app_commands.command(name="취소", description="출석체크를 잘못했다면 이용해보세요.")
    async def attendcancel(self, interaction: discord.Interaction):
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

class TimeGroup(app_commands.Group):
    @app_commands.command(name='등록', description='출석시간을 설정하는 명령어입니다.')    
    async def editTime(self, interaction: discord.Interaction, mon: str, tue: str, wed: str, thu: str, fri: str, sat: str, sun: str):
        user = interaction.user
        idlist = make_userlist('studentdb')
        
        if(user.id in idlist):
            db.deleteDB(schema='public',table='studentdb',condition=f'id = {user.id}')
            await interaction.response.send_message(f'{user.mention}님 아직 시간을 바꾸는 기능이 없어요 ㅠㅠ 대신 시간을 초기화 해드렸으니 다시 입력해주세요.')
        else:
            db.insertDB(schema='public',table='studentdb',colum=None,data=(user.id,user.name,mon,tue,wed,thu,fri,sat,sun))
            await interaction.response.send_message(f'{user.mention}님의 시간을 설정했어요.')

    @app_commands.command(name='확인',description='출석시간을 확인하는 명령어입니다.')
    async def checkTime(self, interaction: discord.Interaction):
        user = interaction.user
        idlist = make_userlist('studentdb')
        timetable = list()

        if(user.id not in idlist):
            await interaction.response.send_message(f'{user.mention}님 출석시간을 설정하지 않았어요. \'/출석시간\' 을 이용해보세요.')
        else:
            for i in range(7):
                time = db.readDB(schema='public',table='studentdb',colum=f'{weekdayindex[i]}',condition=f'id = {user.id}')
                timetable.append(time[0][0])
            await interaction.response.send_message(f'{user.mention}님의 출석시간은 {timetable}입니다.')


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

  
@client.tree.command(name="거꾸로", description="뒤에 쓴 내용을 뒤집습니다.", guild=GUILD_ID)
async def word(interaction: discord.Interaction, say: str):
    say = say[::-1]
    await interaction.response.send_message(f'{say}')

client.run(token)