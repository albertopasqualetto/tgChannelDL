import sys
import os
from tqdm import tqdm
from dotenv import load_dotenv
from telethon.sync import TelegramClient
# maybe move to async version
# maybe download to user's downloads folder https://stackoverflow.com/a/48706260/12506990

load_dotenv()

# if resuming download from a certain point, set manually argv[1]=old_id to the last downloaded file id
old_id = 0
if len(sys.argv) > 1:
    old_id = int(sys.argv[1])


def callback(current, total):
    global pbar
    pbar.update(current - pbar.n)


def download_from_chat(client, chat_id):
    messages = client.get_messages(entity=chat_id)
    messages.reverse()  # Download from oldest to newest
    for idm, m in enumerate(messages):  # idm[0] is always the channel creation message
        if idm < old_id:    # skip already downloaded files
            continue
        if m.action or not m.file:  # skip messages without files
            continue

        global pbar
        pbar = tqdm(total=m.file.size, unit='B', unit_scale=True, unit_divisor=1024, desc="Downloading")
        filename = m.file.name if m.file.name else m.file.id+" ({})".format(idm+old_id)   # cannot download images
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
