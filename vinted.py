import json
import requests
import discord
from discord.ext import tasks

TOKEN = ''
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

teste=[{"name":"iphone","desired_price":350,"max_distance":50,"lastItem":None},
       {"name":"RTX","desired_price":600,"max_distance":150,"lastItem":None},
       {"name":"RX","desired_price":600,"max_distance":150,"lastItem":None},
       {"name":"gaming pc","desired_price":600,"max_distance":250,"lastItem":None}]

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
    for x in teste:
        whatIWant=x["name"]
        desired_price=x["desired_price"]
        max_distance=x["max_distance"]
        max_price= desired_price+max_distance
        min_price= desired_price-max_distance
        if(whatIWant!="" and desired_price!=0):
            r1 = requests.get("https://www.vinted.pt/catalog?search_text="+whatIWant+"&order=newest_first")
            r2 = requests.get("https://www.vinted.pt/api/v2/catalog/items?page=1&per_page=1&search_text="+whatIWant+"&order=newest_first&currency=EUR&price_from="+str(min_price)+"&price_to="+str(max_price),cookies=r1.cookies)

            items=json.loads(r2.text)
            if(len(items['items'])>0): #Sometimes Vinted's API returns 0 items for some reason.
                newItem=items['items'][0]
                r3 = requests.get("https://www.vinted.pt/api/v2/users/"+str(newItem["user"]["id"])+"/items?page=1&per_page=1&cond=active&selected_item_id="+str(newItem["id"]),cookies=r1.cookies)
                item = json.loads(r3.text)
                if(len(item["items"])>0):
                    item=item["items"][0]
                    product_price = float(int(float(item['price']['amount'])))
                    if x["lastItem"] is None or x["lastItem"]!=str(item['id']):
                        if x["name"].lower() in item["title"].lower() or x["name"].lower() in item["description"].lower():
                            x["lastItem"]=str(item['id'])

                            embed = discord.Embed(title=item['title'],
                                url=item['url'],colour=discord.Color.from_rgb(int(255 * min((abs(product_price - min_price)) / max_distance, 1.0)), int(255 * min((abs(product_price - desired_price)) / max_distance, 1.0)), int(255 * min((abs(product_price - max_price)) / max_distance, 1.0))))
                            embed.add_field(name="Price",
                                            value=item['price']['amount']+" "+item['currency'],
                                            inline=False)
                            embed.set_image(url=item['photos'][0]['url'])
                            await channel.send(str(item['id']),embed=embed)
client.run(TOKEN)
