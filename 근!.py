import discord
import requests
from bs4 import BeautifulSoup
import re
import os 


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def summarize_text(text, max_lines=5):
    lines = text.split("\n")
    if len(lines) > max_lines:
        return "\n".join(lines[:max_lines]) + "..."
    else:
        return "\n".join(lines)

def sanitize_filename(filename):
    # Replace special characters with dots and remove .gif and .webp extensions
    sanitized = re.sub(r'[\\/*?:"<>|]', '.', filename)
    sanitized = re.sub(r'\.(gif|webp)$', '', sanitized)
    return sanitized


@client.event
@client.event
async def on_ready() -> None:
    print(f"{client.user} 근!")
    await client.change_presence(activity=discord.Streaming(name="스마일 근근!", url="https://www.twitch.tv/ruliwebvtuber3"))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if "bbs.ruliweb.com" in message.content or "m.ruliweb.com" in message.content:
        # 메세지에서 루리웹 링크를 감시.
        urls = message.content.split()
        ruliweb_urls = [url for url in urls if "bbs.ruliweb.com" in url or "m.ruliweb.com" in url]
        
        for url in ruliweb_urls:
            # 루리웹 본문요약
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title_element = soup.find('title')
                title = title_element.text.strip() if title_element else "No title available"
                title_url = title_element.find('a')['href'] if title_element.find('a') else url
                
                content = soup.find('div', class_='view_content').get_text("\n", strip=True)
                summarized_content = summarize_text(content, max_lines=5)
                
                image = soup.find('div', class_='view_content').find('img')
                image_url = image['src'] if image else None
                
                video = soup.find('div', class_='view_content').find('video')
                video_url = video['src'] if video else None
                
                # 임베드 메세지 보내기 
                embed = discord.Embed(title=title, description=summarized_content, color=discord.Color.blue(), url=title_url)
                embed.set_author(name="루리웹")
                if image_url:
                    embed.set_image(url=image_url)

                if video_url:
                    video_data = requests.get(video_url).content
                    video_filename = sanitize_filename(video_url.split('/')[-1])
                    with open(video_filename, 'wb') as f:
                        f.write(video_data)
                    video_file = discord.File(video_filename)
                    await message.reply(embed=embed, file=video_file)
                    os.remove(video_filename)
                else:
                    await message.reply(embed=embed)
                
            except Exception as e:
                await message.reply("글 요약에러.")
                print(e)

client.run('')
