import requests
import time

[51]
bot_token='5653486266:AAEXoa-iM1pAY5N9eDEwbXJ6-aLGCyEgR5k' # вставьте токен из бота @BotFather
chat_id='624736798' # вставьте id из бота @getmyid_bot
[38]
telegram_delay=8

def getTPSLfrom_telegram():
    strr='https://api.telegram.org/bot'+bot_token+'/getUpdates'
    response = requests.get(strr)
    rs=response.json()
    rs2=rs['result'][-1]
    rs3=rs2['message']
    textt=rs3['text']
    datet=rs3['date']

    if(time.time()-datet)<telegram_delay:
        if 'quit' in textt:
            quit()
        if 'exit' in textt:
            exit()
        if 'hello' in textt:
            telegram_bot_sendtext('Hello. How are you?')


[49]

def telegram_bot_sendtext(bot_message):
    bot_token2 = bot_token
    bot_chatID = chat_id
    send_text = 'https://api.telegram.org/bot' + bot_token2 + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()
