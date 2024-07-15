import json
import discord
from discord.ext import tasks
import vintedUtils
import wallapopUtils
from dotenv import load_dotenv
import os



intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def resetList(data):
    for x in data:
        x["lastItem"]["vinted"] = 0
        x["lastItem"]["wallapop"] = 0


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!v"):
        channel = client.get_channel(1211347578848026636)
        try:
            if ("add" in message.content):
                try:
                    afterQuotes = message.content.split("\"")
                    name = afterQuotes[1]
                    desired_price = afterQuotes[2].split(" ")[1]
                    range = afterQuotes[2].split(" ")[2]
                except:
                    await channel.send("Command missinputed. Example: !v add \"RTX 4060\" 300 100")
                    return

                for x in data:
                    if x["name"] == name:
                        await channel.send("Item already exists!")
                        return
                data.append({
                    "name": name,
                    "desired_price": int(desired_price),
                    "max_distance": int(range),
                    "lastItem": {"vinted": 0, "wallapop": 0}})

                with open('data.json', "w") as f:
                    resetList(data)
                    json.dump(data, f)

                f.close()

                await channel.send("Item "+name+" added to watchlist!")
            if ("remove" in message.content):
                try:
                    afterQuotes = message.content.split("\"")
                    name = afterQuotes[1]
                except:
                    await channel.send("Command missinputed. Example: !v remove \"RTX 4060\"")
                    return

                for x in data:
                    if (x["name"] == name):
                        data.remove(x)
                        with open('data.json', "w") as f:
                            resetList(data)
                            json.dump(data, f)
                            f.close()
                            await channel.send("Item "+name+" removed from watchlist!")
                            return
                await channel.send("Item was not found in list!")

            if ("list" in message.content):
                await channel.send("Here is the list of everything being tracked:")
                for x in data:
                    await channel.send(x["name"])

            if ("run" in message.content):
                if (getVintedStuff.is_running() == False):
                    getVintedStuff.start()
                    getWallapopStuff.start()

                    await channel.send("Starting the watchlist loop")
                    return
                await channel.send("Its running the watchlist loop!")

            if ("stop" in message.content):
                if (getVintedStuff.is_running()):
                    await channel.send("Stopping the watchlist loop, after last iteration completes.")
                    getVintedStuff.stop()
                    getWallapopStuff.stop()
                    return
                await channel.send("Its not running the watchlist loop!")

            if ("status" in message.content):
                if (getVintedStuff.is_running()):
                    await channel.send("Its running the watchlist loop!")
                    return
                await channel.send("Its not running the watchlist loop!")

        except:
            await channel.send("Unknown command error!")


@tasks.loop(seconds=60)
async def getVintedStuff():

    channel = client.get_channel(1211347578848026636)
    for x in data:
        whatIWant = x["name"]
        desired_price = x["desired_price"]
        max_distance = x["max_distance"]
        max_price = desired_price+max_distance
        min_price = desired_price-max_distance
        if (whatIWant != "" and desired_price != 0):

            if (await vintedUtils.getAllItems(whatIWant, min_price, max_price) == None):
                await channel.send("Vinted issue detected. Breaking cycle.")
                break

            items = await vintedUtils.getAllItems(whatIWant, min_price, max_price)

            # Sometimes Vinted's API returns 0 items for some reason.
            if (len(items['items']) > 0):

                newItem = items['items'][0]
                if (await vintedUtils.getItemInformation(newItem["user"]["id"], newItem["id"]) == None):
                    await channel.send("Vinted issue detected. Breaking cycle.")
                    break

                item = await vintedUtils.getItemInformation(
                    newItem["user"]["id"], newItem["id"])
                
                

                if (len(item["items"]) > 0):
                    item = item["items"][0]
                    product_price = float(int(float(item['price']['amount'])))
                    if x["lastItem"]["vinted"] == 0 or x["lastItem"]["vinted"] != str(item['id']):
                        if x["name"].lower() in item["title"].lower() or x["name"].lower() in item["description"].lower():
                            x["lastItem"]["vinted"] = str(item['id'])
                            embed = vintedUtils.discordEmbed(
                                item, product_price, min_price, max_price, max_distance, desired_price)
                            await channel.send("", embed=embed)


@tasks.loop(seconds=60)
async def getWallapopStuff():
    channel = client.get_channel(1211347578848026636)
    for x in data:
        whatIWant = x["name"]
        desired_price = x["desired_price"]
        max_distance = x["max_distance"]
        max_price = desired_price+max_distance
        min_price = desired_price-max_distance
        if (whatIWant != "" and desired_price != 0):
            if (await wallapopUtils.getAllItems(whatIWant, min_price, max_price) == None):
                await channel.send("Wallapop issue detected. Breaking cycle.")
                break

            wallapopItems = await wallapopUtils.getAllItems(whatIWant, min_price, max_price)
            if (len(wallapopItems["search_objects"]) > 0):
                item = wallapopItems["search_objects"][0]
                product_price = float(int(float(item['price'])))
                if x["lastItem"]["wallapop"] == 0 or x["lastItem"]["wallapop"] != str(item['id']):
                    
                    if x["name"].lower() in item["title"].lower() or x["name"].lower() in item["description"].lower():
                        x["lastItem"]["wallapop"] = str(item['id'])

                        embed = wallapopUtils.discordEmbed(
                            item, product_price, min_price, max_price, max_distance, desired_price)
                        await channel.send("", embed=embed)


global data
try:
    r = open('data.json', 'r')
    data = json.load(r)
except FileNotFoundError:
    with open('data.json', 'w') as file:
        json.dump([], file)
        file.close()

    r = open('data.json', 'r')
    data = json.load(r)

r.close()

load_dotenv()

SECRET_KEY = os.getenv("TOKEN")
client.run(SECRET_KEY)
