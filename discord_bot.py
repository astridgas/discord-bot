import psycopg2
import os
import random
import datetime
import asyncio
import requests
import statistics
import discord
from datetime import date
from datetime import timedelta
from datetime import time
from discord.ext import commands

os.environ['DATABASE_URL'] = ''
DATABASE_URL = os.environ['DATABASE_URL']
token = ""

ENV = 'dev'
bot = commands.Bot(command_prefix = '!')

if ENV == 'dev':
    connection = psycopg2.connect(database='', user='', password='', host='127.0.0.1', port='5433') 
    cursor = connection.cursor()
    print('database opened successfully')

elif ENV == 'prod':
    connection = psycopg2.connect(DATABASE_URL, sslmode = 'require')
    cursor = connection.cursor()
    


# GET DATE
def get_date():
    event_date = str(date.today()).replace("-", ".")
    return event_date


@bot.event
async def on_ready():
    print(bot.user.name + ' online')


# AUTO REMIND
async def auto_remind():
    await bot.wait_until_ready()
    while not bot.is_closed():
        cursor.execute("SELECT * FROM events WHERE event_status = 'upcoming'")
        events_list = cursor.fetchall()

        day = datetime.datetime.now().date().day
        hour = datetime.datetime.now().time().hour
        minute = datetime.datetime.now().time().minute
        now = timedelta(days=day, hours=hour, minutes=minute)
        days_7 = timedelta(days=7)
        days_3 = timedelta(days=3)
        hours_24 = timedelta(hours=24)
        hours_8 = timedelta(hours=8)
        hours_2 = timedelta(hours=2)
        hours_m8 = timedelta(hours=-8)

        for event in events_list:
            event_date = timedelta(days=event[1].day, hours=event[2].hour, minutes=event[2].minute)
            time_remaining = event_date - now
            for guild in bot.guilds:
                if str(guild) == event[4]:
                    if days_7 == time_remaining:
                        await guild.channels[2].send(
                            "pozostalo {} czasu do eventu {}".format(time_remaining, event[0]))
                    if days_3 == time_remaining:
                        await guild.channels[2].send(
                            "pozostalo {} czasu do eventu {}".format(time_remaining, event[0]))
                    if hours_24 == time_remaining:
                        await guild.channels[2].send(
                            "pozostalo {} czasu do eventu {}".format(time_remaining, event[0]))
                    if hours_8 == time_remaining:
                        await guild.channels[2].send(
                            "pozostalo {} czasu do eventu {}".format(time_remaining, event[0]))
                    if hours_2 == time_remaining:
                        await guild.channels[2].send(
                            "pozostalo {} czasu do eventu {}".format(time_remaining, event[0]))
                    if hours_m8 == time_remaining:
                        await guild.channels[2].send(
                            "Było bardzo sympatycznie. Pyszne ciasto! {}".format(random.choice(czak_reactions)))
                        cursor.execute("UPDATE events SET event_status = 'finished' WHERE event_name = '{}'".
                                       format(event[0]))
                        connection.commit()

        await asyncio.sleep(60)


async def auto_weather():
    while not bot.is_closed():   
        if timedelta(hours=15) == timedelta(hours=datetime.datetime.now().time().hour):
            weather_array = []        
            weather_array = weather_calc()         
            
            weather = discord.Embed(
                title = 'Hello there! Pogoda na dziś:',
                colour = discord.Color.blue()
            )        
            
            weather.add_field(name = 'rano', value = '{:.1f}°C\n{}'.format(weather_array[0], weather_array[3]), inline = True)
            weather.add_field(name = 'po południu', value = '{:.1f}°C\n{}'.format(weather_array[1], weather_array[4]), inline = True)
            weather.add_field(name = 'w nocy', value = '{:.1f}°C\n{}'.format(weather_array[2], weather_array[5]), inline = True)                            
            weather.set_footer(text='GLHF! {}'.format(random.choice(czak_reactions)))

            for guild in bot.guilds:
                if str(guild) == "czakowy 2":
                    await guild.channels[2].send(embed = weather)                
        await asyncio.sleep(2*1)


def weather_calc():
    url = 'https://api.openweathermap.org/data/2.5/forecast?q=Warsaw&appid=31184ecca6bda026696765c1ae855fc0&units=metric&lang=pl'
    res = requests.get(url)
    data = res.json()
    
    temperatures = []
    description = []
    description_morning = []
    description_evening = []
    description_night = []
    bezchmurnie = 'bezchmurnie'
    for i in range(8):
        temperatures.append(data['list'][i]['main']['temp'])
        description.append(data['list'][0]['weather'][0]['description'])
    
    mean_temp_morning = statistics.mean(temperatures[0:3])
    mean_temp_evening = statistics.mean(temperatures[3:6])
    mean_temp_night = statistics.mean(temperatures[6:8])

    for i in description[0:3]:
        if i not in description_morning:
            description_morning.append(i)
    if len(description_morning) > 1 and bezchmurnie in description_morning:
        description_morning.remove(bezchmurnie)

    for i in description[3:6]:
        if i not in description_evening:
            description_evening.append(i)
    if len(description_evening) > 1 and bezchmurnie in description_evening:
        description_evening.remove(bezchmurnie)

    for i in description[6:8]:
        if i not in description_night:
            description_night.append(i)
    if len(description_night) > 1 and bezchmurnie in description_night:
        description_night.remove(bezchmurnie)    

    desc_morning=','
    desc_morning = desc_morning.join(description_morning)

    desc_evening=','
    desc_evening = desc_evening.join(description_evening)

    desc_night=','
    desc_night = desc_night.join(description_night)
    
    return mean_temp_morning, mean_temp_evening, mean_temp_night, desc_morning, desc_evening, desc_night


@bot.command()
async def pogoda(ctx, city='Warszawa'):

    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid=31184ecca6bda026696765c1ae855fc0&units=metric&lang=pl'.format(city)
    res = requests.get(url)
    data = res.json()
    try:
        weather = discord.Embed(
                    title = 'Aktualna pogoda w {}'.format(city),
                    colour = discord.Color.blue()
                )        
                
        weather.add_field(name = 'temperatura', value = '{:.1f}°C'.format(data['main']['temp']), inline = True)
        weather.add_field(name = 'opis', value = '{}'.format(data['weather'][0]['description']), inline = True)
        weather.add_field(name = 'wiatr', value = '{:.1f} m/s'.format(data['wind']['speed']), inline = True)
    except KeyError:
        await ctx.send("co Ty piszesz gościu, nie ma takiego miasta")
    else:
        await ctx.send(embed = weather)

# COMMANDS
@bot.command()
async def commands(ctx):
    await ctx.send("!set 'nazwa eventu' dd/mm/yyyy hh:mm\n!remind 'nazwa eventu'\n!events\n!rollback")


# ROLLBACK
@bot.command()
async def rollback(ctx):
    connection.rollback()


# SET EVENT
@bot.command()
async def set(ctx,
              event_name,
              event_date = get_date(),
              event_time = '00:00'):
    try:
        cursor.execute("INSERT INTO events (event_name, event_date, event_time, guild)\
                  VALUES('{}', '{}', '{}', '{}');".format(event_name, event_date, event_time, ctx.guild))
    except psycopg2.IntegrityError as e:
        if e.pgcode == '23505':  # unique_violation
            await ctx.send("Spotkanie {} juz istnieje!".format(event_name))
            connection.rollback()
    except psycopg2.DataError as e:
        if e.pgcode == '22008':  # datetime_field_overflow
            await ctx.send("Data poza zakresem!")
            connection.rollback()
    else:
        cursor.execute("SELECT event_name, event_date, event_time FROM events WHERE event_name = '{}'".
                       format(event_name))
        event = cursor.fetchall()
        connection.commit()
        await ctx.send('Okazja: {} \nData: {} godzina: {}'.
                       format(event[0][0], event[0][1].strftime("%d/%m/%Y"), event[0][2]))


# DEL_EVENT
@bot.command()
async def del_event(ctx, event_name):
    if ctx.author == bot.alo_id:
        cursor.execute("SELECT event_name FROM events WHERE event_name = '{}'".format(event_name))
        event = cursor.fetchall()
        if not event:  # pusta lista zwraca false
            await ctx.send("Nie ma takiego spotkania!")
        else:
            cursor.execute("DELETE FROM events WHERE event_name = '{}'".format(event_name))
            connection.commit()
            await ctx.send("Spotkanie {} usunięto!".format(event_name))
    else:
        await ctx.send("Nie masz takich uprawnień :P")


# REMIND
@bot.command()
async def remind(ctx, event_name):
    cursor.execute("SELECT * FROM events WHERE event_name = '{}'".format(event_name))
    event = cursor.fetchall()

    if not event:
        await ctx.send("Nie ma takiego spotkania!")
    elif event[0][4] == str(ctx.guild):
        await ctx.send('Przypominam: spotkanie {} odbywa się dnia {} o godzinie {}'.
                       format(event[0][0], event[0][1].strftime("%d/%m/%Y"), event[0][2]))
    else:
        await ctx.send('Zakaz dostępu!')


# EVENTS - checks event list
@bot.command()
async def events(ctx):
    cursor.execute("SELECT * FROM events WHERE event_status = 'upcoming' AND guild = '{}'".format(ctx.guild))
    events_list = cursor.fetchall()

    if not events_list:
        await ctx.send("Brak spotkań, kalendarz jest pusty :(")
    else:
        for event in events_list:
            if event[4] == str(ctx.guild):  # indeks 4 w tabeli events to nazwa gildii
                await ctx.send("spotkanie: {}, data: {}, godzina: {}".
                               format(event[0], event[1].strftime("%d/%m/%Y"), event[2]))


kuchnie = ['Burgery', 'Cing ciong', 'Kebab', 'Pitce', 'Cebule', 'Indian', 'El papito', 'Q&B']
czak_reactions = ["₍ᐢ•ﻌ•ᐢ₎", "ฅ^•ﻌ•^ฅ", "V●ᴥ●V", "V◕ฺω◕ฺV", "(V●ᴥ●V)", "∪･ω･∪", "◖⚆ᴥ⚆◗", "●ᴥ●", "乁[ ◕ ᴥ ◕ ]ㄏ", " -ᄒᴥᄒ-",
                  "୧༼◕ ᴥ ◕༽୨", "ヽ(°ᴥ°)ﾉ", "( ͡° ᴥ ͡°)", "ฅ₍ᐢ•ﻌ•ᐢ₎ฅ"]


@bot.event
async def on_message(message):
    if 'hello there' in message.content.lower():
        await message.channel.send('General {}!. You are a bold one!'.format(message.author.name))
    if 'czak' in message.content.lower():
        await message.channel.send(random.choice(czak_reactions))
    if 'przejade' in message.content.lower():
        await message.channel.send('Przejadę, to ja ci pałką po pysku')
    if 'xD' in message.content:
        await message.channel.send('Hihihi hahaha a pół chuja w dupie')
    if 'bywaj' in message.content.lower():
        await message.channel.send('Ja kurwa jestem, a nie bywam')
    if 'slychać' in message.content.lower():
        await message.channel.send('Stare kurwy nie chcą zdychać')
    if 'witam' in message.content.lower():
        await message.channel.send("Pokaż mi swoje towary")
    if 'fraszk' in message.content.lower():
        await message.channel.send('{0} {0} Ty chuju'.format(message.author.name))
    if 'lenny' in message.content.lower():
        await message.channel.send("( ͡° ͜ʖ ͡°)")
    if 'hmm' in message.content.lower():
        await message.channel.send("Zanosi się na burzę")
    if 'problem' in message.content.lower():
        await message.channel.send("W czarnej dupie jesteśmy, a nie...")
    if 'co kurwa' in message.content.lower():
        await message.channel.send("Coś za jeden? Czego tu nalazł?")
    if 'zycze' in message.content.lower():
        await message.channel.send('I tego wam życzę dostojni panowie zebyscie sie nie posrali')
    if 'andrzej' in message.content.lower():
        await message.channel.send('to jebnie!')

    
    if 'co jemy' in message.content.lower():
        await message.channel.send('Dziś do michy wkładamy: ' + random.choice(kuchnie))
    if 'zamawiamy' in message.content.lower():
        await message.channel.send('Dziś do michy wkładamy: ' + random.choice(kuchnie))
    if 'do jedzenia' in message.content.lower():
        await message.channel.send('Dziś do michy wkładamy: ' + random.choice(kuchnie))

    await bot.process_commands(message)


bot.loop.create_task(auto_remind())
bot.loop.create_task(weather())
bot.run(token)
