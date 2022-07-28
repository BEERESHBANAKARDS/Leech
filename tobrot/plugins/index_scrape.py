import base64 
import json
import cloudscraper

from urllib.parse import quote as q
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tobrot import LOGGER, UPDATES_CHANNEL
from tobrot.helper_funcs.display_progress import humanbytes
from tobrot.plugins.mediainfo import post_to_telegraph

nexPage = False #ToDo
nexPageToken = "" 

def authorization_token(username, password):
    user_pass = f"{username}:{password}"
    token ="Basic "+ base64.b64encode(user_pass.encode()).decode()
    return token
	 	 
def scrapeURL(payload_input, url, username, password): 
    global nexPage 
    global nexPageToken
    url = url + "/" if  url[-1] != '/' else url
    
    try: 
        headers = {"authorization":authorization_token(username,password)}
    except Exception as e: 
        LOGGER.info(f"[INDEX SCRAPE] Error : {e}")
        return f"Error : {e}", True

    session = cloudscraper.create_scraper(allow_brotli=False)
    enResp = session.post(url, data=payload_input, headers=headers)
    if enResp.status_code == 401: 
        return "Could not Acess your Entered URL!, Check your Username / Password", True
   
    try: 
        deResp = json.loads(base64.b64decode(enResp.text[::-1][24:-20]).decode('utf-8'))
    except Exception as err: 
        LOGGER.info(f"[INDEX SCRAPE] Error : {err}")
        return "Something Went Wrong. Check Index Link / Username / Password Valid or Not", True
       
    pagToken = deResp["nextPageToken"] 
    if pagToken == None: 
        nexPage = False 
    else: 
        nexPage = True 
        nexPageToken = pagToken 

    scpText = ""
   
    if list(deResp.get("data").keys())[0] == "error": 
        return "Nothing Found in Your Entered URL", True
    else:
        file_length = len(deResp["data"]["files"])
        scpText += f"🗄 <i><b> Total Files : </b></i> {file_length} <br><br>"
        for i, _ in enumerate(range(file_length)):
        
            files_type = deResp["data"]["files"][i]["mimeType"]
            files_name = deResp["data"]["files"][i]["name"] 
            if files_type == "application/vnd.google-apps.folder": 
                #ToDo Directory Inside Directory 😇
                pass
            else:
                direct_download_link = url + q(files_name)
                no = i + 1
                LOGGER.info(direct_download_link)
                scpText += f"📄 <strong>{no}. {files_name}</strong> : <br><br><pre>🔖 Index Link :<a href='{direct_download_link}'> Index Link </a> <br>"
                try:
                    files_size = deResp["data"]["files"][i]["size"]
                    scpText += f"<br>📂 Size : {humanbytes(files_size)} | 📋 Type : {files_type} "
                except:
                    pass
                try:
                    files_time   = deResp["data"]["files"][i]["modifiedTime"]
                    scpText += f"| ⏰ Modified Time : {files_time}<br><br>"
                except:
                    pass
            scpText += "</pre>"
        return scpText, False
	        
	
async def index_scrape(client, message):
    '''  /indexscape <link>\n username\n password uscommand '''
    lm = await message.reply_text(
        text="`Scrapping Down ...`",
    )
    username = ""
    password = ""
    user_id_ = message.from_user.id 
    u_men = message.from_user.mention
    _send = message.text.split(" ", maxsplit=1)
    reply_to = message.reply_to_message
    if len(_send) > 1:
        txt = _send[1]
    elif reply_to is not None:
        txt = reply_to.text
    else:
        txt = ""
    url = ""
    if txt != "":
        _lin = txt.split("\n")
        url = _lin[0]
        try:
            username = _lin[1]
            password = _lin[2]
        except:
            username="none"
            password="none"
            pass
    else:
        await lm.edit_text("`Not Provided URL to Scrape`")
        return
    x = 0
    global body_text 
    if url:
        body_text = f"<i>🔗 Raw Index Link :</i> <a href='{url}'> Click Here </a> <br>"
    if username != "none" and password != "none":
        cpass = ""
        cname = ""
        for p in range(0, len(password)): cpass += "*"
        for n in range(0, len(username)): cname += "*"
        body_text += f"<i>👤 Username :</i> {cname} <br><i>📟 Password :</i> {cpass} <br><hr><br>"
    payload = {"page_token":nexPageToken, "page_index": x}	
    LOGGER.info(f"Index Scrape Link: {url}")
    body_txt, error = scrapeURL(payload, url, username, password)

    body_text += str(body_txt)
  
    if error:
        await lm.delete()
        await message.reply_text(body_txt)
        return

    while nexPage == True: #Not to be Executed 
        payload = {"page_index":nexPageToken, "page_index": x}
        print(scrapeURL(payload, url, username, password))
        x += 1

    title = "Index Link Scrapper"
    tgh_link = post_to_telegraph(title, body_text)

    textup = f"""
┏━📮  𝗜𝗻𝗱𝗲𝘅 𝗦𝗰𝗿𝗮𝗽𝗲 𝗥𝗲𝘀𝘂𝗹𝘁 :
┃
┣👤 𝐔𝐬𝐞𝐫 : {u_men} ( #ID{user_id_} )
┃
┣🔗 𝗨𝗥𝗟 : <code> {url} </code>
┃
┗━♦️ℙ𝕠𝕨𝕖𝕣𝕖𝕕 𝔹𝕪 {UPDATES_CHANNEL}♦️━╹
"""
    markup_ = InlineKeyboardMarkup([[InlineKeyboardButton(text="Iɴᴅᴇx Sᴄʀᴀᴘᴇ Lɪɴᴋ", url=tgh_link)]])

    await lm.delete()
    await message.reply_text(text=textup, reply_markup=markup_)

#┣ 📰 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 : {cname}
#┣ 📟 𝗣𝗮𝘀𝘀𝘄𝗼𝗿𝗱 : {cpass}
