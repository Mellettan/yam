from django.core.management import BaseCommand
from loguru import logger
from yandex_music import Client, Track, Playlist, Chart as YMChart
import os
from dotenv import load_dotenv

from chart.models import Chart

load_dotenv()
YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')
client = Client(YANDEX_TOKEN).init()
logger.debug("Yandex Music API Client инициализирован")


class Command(BaseCommand):
    help = 'Get chart'

    def handle(self, *args, **options):
        logger.info(f'Get russia chart')
        try:
            _chart: Playlist = client.chart('russia').chart
        except Exception as e:
            logger.error(e)
            return
        _chart_tracks = dict()

        for track_short in _chart.tracks:
            track: Track = track_short.track
            chart: YMChart = track_short.chart
            artists: list = []
            if track.artists:
                artists = [artist.name for artist in track.artists]

            # Создаем запись в базе данных
            Chart.objects.create(
                position=chart.position,
                name=track.title,
                artists=artists,
                track_id=track.id,
            )

            logger.info(f"Добавлен новый трек: {chart.position}: {track.title}")

        logger.info('Процесс завершен успешно')
