import requests
import discord
import sqlite3 as sl
from random import randint
from datetime import date
from discord import Embed



api_key = 'vAhCwFa4GPQybf7KnRiAbMHarVtnvXfUBP0JnDXp'
logo = 'https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo-web-rgb.png'
base_url_nasa = 'https://api.nasa.gov/planetary/apod'
base_url_astrobin = "http://astrobin.com/api/v1/{}&api_key=db2d3e74c4cacf53f150ca1a5f84b07d92ea5826&api_secret=fd08d58d489c3848be8379965f5295945b677127&format=json"
db = 'channel_directory.db'


def random_date():
    current_date = date.today()
    year = randint(1996, current_date.year)
    if year == current_date.year:
        month = randint(1, current_date.month)
        if month == current_date.month:
            day = randint(1, current_date.day)
        else:
            if month in [1, 3, 5, 7, 8, 10, 12]:
                day = randint(1, 31)
            elif month == 2:
                day = randint(1, 28)
            else:
                day = randint(1, 30)
    else:
        month = randint(1, 12)
        if month in [1, 3, 5, 7, 8, 10, 12]:
            day = randint(1, 31)
        elif month == 2:
            day = randint(1, 28)
        else:
            day = randint(1, 30)

    rand_date = str(year)+'-'+str(month).zfill(2)+'-'+str(day).zfill(2)
    return rand_date


def get_apod(day):
    if day == None:
        potd = requests.get(base_url_nasa, params={'api_key': api_key, 'hd': 'true'})
    else:
        potd = requests.get(base_url_nasa, params={'api_key': api_key, 'hd': 'true', 'date': day})

    potd_json = potd.json()

    if 'url' in potd_json and 'youtube' in potd_json['url']:
        embed = Embed(
            title = potd_json['title'],
            description = potd_json['explanation'],
            color = discord.Color.red()
        )

        url = potd_json['url']
        url1 = url.split("/embed/")[0]
        url2 = url.split("/embed/")[1].split("?")[0]
        corrected_url = url1+'/watch?v='+url2

        embed.set_thumbnail(url=logo)
        embed.set_footer(text='NASA Astronomy Picture of the Day (' + potd_json['date'] + ')')
        return [embed, corrected_url]
        print("Sent!")

    elif 'hdurl' in potd_json:
        embed = Embed(
            title = potd_json['title'],
            description = potd_json['explanation'],
            color = discord.Color.red()
        )

        embed.set_image(url=potd_json['hdurl'])
        embed.set_thumbnail(url=logo)
        embed.set_footer(text='NASA Astronomy Picture of the Day (' + potd_json['date'] + ')')
        return [embed]
        print("Sent!")

    elif 'url' in potd_json:
        embed = Embed(
            title = potd_json['title'],
            description = potd_json['explanation'],
            color = discord.Colour.from_rgb(255, 0, 0)
        )

        embed.set_thumbnail(url=logo)
        embed.set_footer(text='NASA Astronomy Picture of the Day (' + potd_json['date'] + ')')
        return [embed, potd_json['url']]
        print("Sent!")


def channel_exists(channel):
    conn = sl.connect(db)
    cursor = conn.cursor()
    channel_exist = "SELECT EXISTS (SELECT * FROM channels WHERE id = {});".format(channel)
    cursor.execute(channel_exist)
    exists = cursor.fetchall()[0][0]
    cursor.close()
    conn.close()

    if exists == 0:
        return False
    else:
        return True


def add_channel(channel, choice):
    conn = sl.connect(db)
    cursor = conn.cursor()

    if not channel_exists(channel):
        query = "INSERT INTO channels (id, {}) VALUES({}, 1);".format(choice, channel)
        result = 1
    else:
        query = "UPDATE channels SET {} = 1 WHERE id = {};".format(choice, channel)
        result = 0

    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    return result


def del_inactive():
    conn = sl.connect(db)
    cursor = conn.cursor()
    query = "DELETE FROM channels WHERE apod = 0 AND iotd = 0;"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


def del_channel(channel, choice):
    conn = sl.connect(db)
    cursor = conn.cursor()

    if not channel_exists(channel):
        result = 0
    else:
        query = "UPDATE channels SET {} = 0 WHERE id = {};".format(choice, channel)
        cursor.execute(query)
        result = 1

    conn.commit()
    cursor.close()
    conn.close()
    return result


def channel_val(channel): #returns 'apod' and 'iotd' values for a given channel
    conn = sl.connect(db)
    cursor = conn.cursor()
    query = "SELECT * FROM channels WHERE id = {}".format(channel)
    cursor.execute(query)
    value = cursor.fetchall()[0][1:]
    cursor.close()
    conn.close()
    return value


def get_channels_apod():
    conn = sl.connect(db)
    cursor = conn.cursor()
    query = "SELECT * FROM channels WHERE apod = 1;"
    cursor.execute(query)
    channels = []
    for i in cursor.fetchall():
        channels.append(i[0])
    cursor.close()
    conn.close()
    return channels


def get_channels_iotd():
    conn = sl.connect(db)
    cursor = conn.cursor()
    query = "SELECT * FROM channels WHERE iotd = 1;"
    cursor.execute(query)
    channels = []
    for i in cursor.fetchall():
        channels.append(i[0])
    cursor.close()
    conn.close()
    return channels


def get_iotd():
    temp = 'imageoftheday/?limit=1'
    url = base_url_astrobin.format(temp)
    j = requests.get(url).json()
    objects = j['objects']
    date = objects[0]['date']
    image = objects[0]['image']
    image_id = image.split('image/')[1]
    temp = image.split('v1/')[1] + '?'
    url = base_url_astrobin.format(temp)
    iotd = requests.get(url).json()
    embed = discord.Embed(
        title="**"+iotd['title']+"**",
        color=discord.Colour.from_rgb(0, 0, 0),
        url='https://www.astrobin.com/' + image_id,
        description=iotd['description']
    )
    embed.set_thumbnail(url='https://i.imgur.com/c3pqpDA.png')
    embed.set_footer(text='AstroBin Image of the Day ' + '(' + iotd['updated'].split('T')[0] + ')')
    embed.set_image(url=iotd['url_hd'])
    embed.set_author(name='By: ' + iotd['user'])
    return embed


def get_toppick():
    temp = 'toppick?limit=20'
    x = randint(0, 19)
    url = base_url_astrobin.format(temp)
    j = requests.get(url).json()
    object = j['objects'][x]
    image = object['image']
    image_id = image.split('image/')[1]
    temp = image.split('v1/')[1] + '?'
    url = base_url_astrobin.format(temp)
    pic = requests.get(url).json()
    embed = discord.Embed(
        title="**" + pic['title'] + "**",
        color=discord.Colour.from_rgb(0, 0, 0),
        url='https://www.astrobin.com/' + image_id,
        description=pic['description']
    )
    embed.set_thumbnail(url='https://i.imgur.com/c3pqpDA.png')
    embed.set_footer(text='AstroBin Top Pick ' + '(' + pic['updated'].split('T')[0] + ')')
    embed.set_image(url=pic['url_hd'])
    embed.set_author(name='By: ' + pic['user'])
    return embed