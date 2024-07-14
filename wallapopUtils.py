import requests
import discord
from discord.ext import tasks

#https://api.wallapop.com/api/v3/general/search?shipping=true&min_sale_price=300&max_sale_price=500&filters_source=default_filters&keywords=iphone&order_by=newest

#https://api.wallapop.com/api/v3/general/search?shipping=true&min_sale_price=300&max_sale_price=400&keywords=iphone&order_by=newest
def getAllItems(itemName,min_price,max_price):
    itemName.replace(" ","%20")
    s = requests.Session()
    s.get("https://pt.wallapop.com/app/search?filters_source=search_box&keywords="+itemName)
    s.headers.update({'host': 'api.wallapop.com'})
    r1 = s.get("https://api.wallapop.com/api/v3/general/search?shipping=true&min_sale_price="+str(min_price)+"&max_sale_price="+str(max_price)+"&filters_source=default_filters&keywords="+itemName+"&order_by=newest",headers={
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/111.0.0.0 Safari/537.36',
        })
    if(r1.status_code!=200):
        return None
    return r1


def discordEmbed(item,product_price,min_price,max_price,max_distance,desired_price):
    
    embed = discord.Embed(title=item['title'],url="https://pt.wallapop.com/item/"+item["web_slug"], colour=discord.Color.from_rgb(int(255 * min((abs(product_price - min_price)) / max_distance, 1.0)), int(255 * min((abs(product_price - desired_price)) / max_distance, 1.0)), int(255 * min((abs(product_price - max_price)) / max_distance, 1.0))))
    embed.add_field(name="Price",value=str(item['price']) +" "+item['currency'],inline=False)
    embed.set_image(url=item['images'][0]['original'])
    return embed