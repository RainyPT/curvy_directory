import json
import discord
from discord.ext import tasks
import vintedUtils
import wallapopUtils

TOKEN = ''
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# https://api.wallapop.com/api/v3/general/search?shipping=true&min_sale_price=300&max_sale_price=500&filters_source=default_filters&keywords=iphone&order_by=newest


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    getVintedStuff.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!v"):
        channel = client.get_channel(1211347578848026636)
        await channel.send("vinted")


@tasks.loop(seconds=5)
async def getVintedStuff():

    channel = client.get_channel(1211347578848026636)
    for x in data:
        whatIWant = x["name"]
        desired_price = x["desired_price"]
        max_distance = x["max_distance"]
        max_price = desired_price+max_distance
        min_price = desired_price-max_distance
        if (whatIWant != "" and desired_price != 0):

            if (vintedUtils.getAllItems(whatIWant, min_price, max_price) == None):
                print("Vinted issue detected. Breaking cycle.")
                continue

            items = vintedUtils.getAllItems(
                whatIWant, min_price, max_price).json()

            # Sometimes Vinted's API returns 0 items for some reason.
            if (len(items['items']) > 0):

                newItem = items['items'][0]
                if (vintedUtils.getItemInformation(newItem["user"]["id"], newItem["id"]) == None):
                    print("Vinted issue detected. Breaking cycle.")
                    continue

                item = vintedUtils.getItemInformation(
                    newItem["user"]["id"], newItem["id"]).json()

                if (len(item["items"]) > 0):
                    item = item["items"][0]
                    product_price = float(int(float(item['price']['amount'])))
                    if x["lastItem"]["vinted"] == 0 or x["lastItem"]["vinted"] != str(item['id']):
                        if x["name"].lower() in item["title"].lower() or x["name"].lower() in item["description"].lower():
                            x["lastItem"]["vinted"] = str(item['id'])
                            embed = vintedUtils.discordEmbed(item,product_price,min_price,max_price,max_distance,desired_price)
                            await channel.send(str(item['id']), embed=embed)

            if (wallapopUtils.getAllItems(whatIWant, min_price, max_price) == None):
                print("Wallapop issue detected. Breaking cycle.")
                continue

            wallapopItems = wallapopUtils.getAllItems(
                whatIWant, min_price, max_price).json()
            if (len(wallapopItems["search_objects"]) > 0):
                item = wallapopItems["search_objects"][0]
                product_price = float(int(float(item['price'])))
                if x["lastItem"]["wallapop"] == 0 or x["lastItem"]["wallapop"] != str(item['id']):
                    if x["name"].lower() in item["title"].lower() or x["name"].lower() in item["description"].lower():
                        x["lastItem"]["wallapop"] = str(item['id'])

                        embed = wallapopUtils.discordEmbed(item,product_price,min_price,max_price,max_distance,desired_price)
                        await channel.send(str(item['id']), embed=embed)


def main():
    print("What do you want to do?\n 1. Run the bot\n 2. Add more items\n 3. Remove items\n\n\n")
    option = input(": ")
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

    if (option == "1"):
        client.run(TOKEN)
    else:
        if (option == "2"):
            name = input("Input name of item: ")
            desired_price = input("Input desired price: ")
            maxdistance = input("Input max price offset: ")
            for x in data:
                if x["name"] == name:
                    print("Item already exists!")
                    return
            data.append({
                "name": name,
                "desired_price": int(desired_price),
                "max_distance": int(maxdistance),
                "lastItem": {"vinted": 0, "wallapop": 0}})

            with open('data.json', "w") as f:
                json.dump(data, f)

            f.close()

        if (option == "3"):
            name = input("Input name of item:")
            for x in range(0, len(data)):
                if (data[x]["name"] == name):
                    data.pop(x)
                    with open('data.json', "w") as f:
                        json.dump(data, f)

            f.close()
        return


main()
