import os
from tqdm import tqdm
from dotenv import load_dotenv
from telethon.sync import TelegramClient
# maybe move to async version

load_dotenv()


def callback(current, total):
    global pbar
    pbar.update(current - pbar.n)


def download_from_chat(client, chat_id):
    messages = client.get_messages(entity=chat_id)
    messages.reverse()  # Download from oldest to newest
    for m in messages:
        if not m.file:
            continue

        global pbar
        pbar = tqdm(total=m.file.size, unit='B', unit_scale=True, unit_divisor=1024, desc="Downloading")
        filename = m.file.name if m.file.name else m.file.id
        pbar.set_description("Downloading " + filename)
        client.download_media(m, progress_callback=callback)    # TODO save to folder
        pbar.close()


if __name__ == '__main__':
    client = TelegramClient('tgChannelDL', int(os.environ.get('API_ID')), os.environ.get('API_HASH'))
    client.start(os.environ.get('PHONE_NUMBER'), os.environ.get('TWOFA_PASSWORD'))

    download_from_chat(client, os.environ.get('CHANNEL_INVITE_LINK'))

    client.disconnect()
