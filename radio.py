import vlc
import time


def play_stream(url):
    # Створення об'єкту медіаплеєра
    instance = vlc.Instance()
    player = instance.media_player_new()

    # Створення об'єкту медіастріму
    media = instance.media_new(url)

    # Підключення медіастріму до медіаплеєра
    player.set_media(media)

    # Відтворення стріму
    player.play()

    # Зачекайте, поки стрім відтвориться (наприклад, 30 секунд)
    time.sleep(30)

    # Зупинка відтворення
    player.stop()


# Приклад використання
stream_url = "http://online.kissfm.ua/KissFM"  # Замініть це на дійсний URL стріму
play_stream(stream_url)
