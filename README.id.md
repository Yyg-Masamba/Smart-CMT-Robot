# Smart-CMT-Robot

<!--Project Title Image-->
<p align="center">
  <img src="https://telegra.ph/file/60a1816cae4e389407ee5.jpg" width="200" height="200"/>
</p>

<!--Table of Contents-->
# Table of Contents
- [[1] About Smart-CMT-Robot](#1-about-smart-cmt-robot)
- [[2] Framework Tools And Server That Used To Build This Bot](#2-framework-tools-and-server-that-used-to-build-this-bot)
- [[3] Support Creator](#3-donation)
- [[4] Notes](#4-notes)
- [[5] Features](#5-features)
- [[6] Variables](#6-variables)
- [[7] Deploying Tutorial](#7-deploy-recommended-using-dockerdocker-compose)
  - [Build And Run Using Legacy Method](#build-and-run-using-legacy-method)
  - [Build And Run Using Docker](#build-and-run-using-docker)
  - [Build And Run The Docker Image Using docker-compose](#build-and-run-the-docker-image-using-docker-compose)
- [[8] Credits](#8-thanks-to)
- [[9] Disclaimer](#8-disclaimer)

# [1] About Smart-CMT-Robot
*Smart-CMT-Robot* is a Telegram Bot built using Python and the Pyrogram library. Many useful features for us to use. I hope that one day this project will be discontinued, someone will continue or develop it again. I gave the name MissKaty because I like cats, a cute animal that likes to be played with and friendly with humans.

## [2] Framework Tools And Server That Used To Build This Bot
 🌱 PyroFork v2.x.x (Fork of Pyrogram with Topics Support and Some Patch)<br>
 🌱 Python 3.11 Support<br>
 🌱 MongoDB as Database<br>
 🌱 PyKeyboard for Building Pagination<br>
 🌱 VS Code<br>
 🌱 VPS/Server With Docker Support (Recommended)<br>


## [3] Notes
If you want help me fixing some error in my bot, you can make pull request to this repo. I'm very glad if you can help me. You can also give support to me for buying server.

## [4] Features

| FEATURE MY BOT |🌱|
| ------------- | ------------- |
| Basic Admin Feature |✔️|
| AFK Feature |✔️|
| Downloader FB, TikTok and YT-DLP Support  |✔️|
| MultiLanguage Support (Unfinished) |⚠️|
| NightMode  |✔️|
| ChatBot based on OpenAI |✔️|
| MissKaty Mata |✔️|
| Inline Search  |✔️|
| Sticker Tools  |✔️|
| PasteBin Tools  |✔️|
| WebScraper (Pahe, MelongMovie, LK21, Terbit21, Kusonime, etc)  |✔️|
| IMDB Search With Multi Language Per User |✔️|
| GenSS From Media and MediaInfo Generator |✔️|
| And Many More.. |✔️|

## [5] Variables

### Required Variables
* `BOT_TOKEN`: Create a bot using [@BotFather](https://t.me/BotFather), and get the Telegram API token.
* `API_ID`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `API_HASH`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `DATABASE_URI`: [mongoDB](https://www.mongodb.com) URI. Get this value from [mongoDB](https://www.mongodb.com). For more help watch this [video](https://youtu.be/1G1XwEOnxxo)
* `LOG_CHANNEL` : A channel to log the activities of bot. Make sure bot is an admin in the channel.

### Optional Variables
* `USER_SESSION` : Session string for Userbot.
* `DATABASE_NAME`: Name of the database in MongoDB
* `COMMAND_HANDLER`: List of handler bot command splitted by space. Ex: `. !` > so bot will respond with `.cmd` or `!cmd`
* `SUDO`: User ID that have access to bot, split by space
* `OPENAI_API`: Get it from OpenAI Web
* `CURRENCY_API`: Get API Key from https://app.exchangerate-api.com/sign-up

## [6] Tutorial Deploy (Recommended using Docker/Docker Compose)

#### Build And Run Using Legacy Method
- Make sure minimum python version is 3.8 to prevent some errors. Check it with this command:
```
python3 --version
```
- Install all dependency that needed bot to run. *(need root access, you can skip this if your server didn't have root access but some plugins will not work)*
```
apt update -y & apt install libjpeg-dev zlib1g-dev libwebp-dev python3-pip python3-lxml git wget curl ffmpeg locales tzdata neofetch mediainfo speedtest-cli -y
```
- Install requirements.txt, if using python 3.11, you need use venv when install pip package.<br/>
*Python < 3.10*
```
pip3 install -r requirements.txt
```
*Python 3.11*
```
Install venv from your terminal and activate it
pip3 install -r requirements.txt 
```
- Setting your config.env or via environment and dont forget fill all required value.
- Run Bot
```
bash start.sh
```

#### Build And Run Using Docker

- Start Docker daemon (Skip if already running):
```
sudo dockerd
```
- Build Docker image:
```
sudo docker build . -t misskaty
```
- Run the image:
```
sudo docker run misskaty
```
- To stop the image:
```
sudo docker ps
sudo docker stop <pid>
```

#### Build And Run The Docker Image Using docker-compose

- Install docker-compose
```
sudo apt install docker-compose
```
- Build and run Docker image or to view current running image:
```
sudo docker-compose up
```
- After editing files with nano for example (nano start.sh):
```
sudo docker-compose up --build
```
- To stop the running image:
```
sudo docker ps
```
```
sudo docker-compose stop <pid>
```

----


## [7] Disclaimer
[![GNU Affero General Public License 2.0](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.en.html#header)    
Licensed under [GNU AGPL 2.0.](https://github.com/Yyg-Masamba/Smart-CMT-Robot/blob/master/LICENSE)
WARNING: Selling The Codes To Other People For Money Is *Strictly Prohibited*. God always sees you.

