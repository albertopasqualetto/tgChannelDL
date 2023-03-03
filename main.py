import sys
import os
from tqdm import tqdm
from dotenv import load_dotenv
from telethon.sync import TelegramClient
# maybe move to async version
# maybe download to user's downloads folder https://stackoverflow.com/a/48706260/12506990

load_dotenv()

# argv[1] = "resume" or "restart" if resuming download after deleting files from Telegram
# if resuming download from a certain point, set manually argv[2]=old_id to the last downloaded file number
old_id = 0
if len(sys.argv) > 1:
    old_id = int(sys.argv[2])


def callback(current, total):
    global pbar
    pbar.update(current - pbar.n)


def download_from_chat(client, chat_id):
    messages = client.get_messages(entity=chat_id)
    messages.reverse()  # Download from oldest to newest
    for idm, m in enumerate(messages):  # idm[0] is always the channel creation message
        if len(sys.argv) > 1 and sys.argv[1] == "resume" and idm < old_id:    # skip already downloaded files but re-download the last one (probably corrupted)
            continue
        if m.action or not m.file:  # skip messages without files
            continue

        if len(sys.argv) > 1 and sys.argv[1] == "resume":
            number = idm
        elif len(sys.argv) > 1 and sys.argv[1] == "restart":
            number = idm + old_id

        global pbar
        pbar = tqdm(total=m.file.size, unit='B', unit_scale=True, unit_divisor=1024, desc="Downloading")
        filename = m.file.name if m.file.name else m.file.id+" ({})".format(number)   # cannot download images
        pbar.set_description("Downloading " + filename)
        client.download_media(m, progress_callback=callback, file="./downloads/"+filename)
        pbar.close()


if __name__ == '__main__':
    client = TelegramClient('tgChannelDL', int(os.environ.get('API_ID')), os.environ.get('API_HASH'))
    client.start(os.environ.get('PHONE_NUMBER'), os.environ.get('TWOFA_PASSWORD'))

    print("Download all files from specified channel")
    download_from_chat(client, os.environ.get('CHANNEL_INVITE_LINK'))
    print("Done!")
    client.disconnect()
