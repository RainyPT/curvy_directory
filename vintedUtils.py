import aiohttp
import discord


async def getAllItems(itemName,min_price,max_price):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.vinted.pt/catalog?search_text="+itemName+"&order=newest_first") as r1:
            if(r1.status!=200):
                return None
                            
            async with session.get("https://www.vinted.pt/api/v2/catalog/items?page=1&per_page=1&search_text="+itemName+"&order=newest_first&currency=EUR&price_from="+str(min_price)+"&price_to="+str(max_price),cookies=r1.cookies) as r2:
                if(r2.status!=200):
                    return None
                return await r2.json()


async def getItemInformation(userId,itemId):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.vinted.pt/catalog?search_text="+str(itemId)+"&order=newest_first") as r1:
            if(r1.status!=200):
                return None
            
            async with session.get("https://www.vinted.pt/api/v2/users/"+str(userId)+"/items?page=1&per_page=1&cond=active&selected_item_id="+str(itemId),cookies=r1.cookies) as r2:
                if(r2.status!=200):
                    return None
                
                return await r2.json()


def discordEmbed(item,product_price,min_price,max_price,max_distance,desired_price):
    embed = discord.Embed(title=item['title'],url=item['url'], colour=discord.Color.from_rgb(int(255 * min((abs(product_price - min_price)) / max_distance, 1.0)), int(255 * min((abs(product_price - desired_price)) / max_distance, 1.0)), int(255 * min((abs(product_price - max_price)) / max_distance, 1.0))))
    embed.add_field(name="Price",value=item['price']['amount'] +" "+item['currency'],inline=False)
    embed.set_image(url=item['photos'][0]['url'])
    return embed