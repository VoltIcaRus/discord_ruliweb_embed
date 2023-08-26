import discord
import requests
from bs4 import BeautifulSoup

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def summarize_text(text, max_lines=5):
    lines = text.split("\n")
    if len(lines) > max_lines:
        return "\n".join(lines[:max_lines]) + "..."
    else:
        return "\n".join(lines)




@client.event
@client.event
async def on_ready() -> None:
    print(f"{client.user} 근!")
    await client.change_presence(activity=discord.Streaming(name="스마일 근근!", url="https://www.twitch.tv/ruliwebvtuber3"))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if "bbs.ruliweb.com" in message.content:
        # 메세지에서 루리웹 링크를 감시.
        urls = message.content.split()
        ruliweb_urls = [url for url in urls if "bbs.ruliweb.com" in url]
        
        for url in ruliweb_urls:
            # 루리웹 본문요약
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title_element = soup.find('title')
                title = title_element.text.strip() if title_element else "No title available"
                title_url = title_element.find('a')['href'] if title_element.find('a') else url
                
                content = soup.find('div', class_='view_content').get_text("\n", strip=True)
                summarized_content = summarize_text(content, max_lines=2)
                
                image = soup.find('div', class_='view_content').find('img')
                image_url = image['src'] if image else None
                
                # 임베드 메세지 보내기 
                embed = discord.Embed(title=title, description=summarized_content, color=discord.Color.blue(), url=title_url)
                if image_url:
                    embed.set_image(url=image_url)
                
                await message.reply(embed=embed)
                
            except Exception as e:
                await message.reply("글 요약에러.")
                print(e)

client.run('')