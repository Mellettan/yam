import os
import io
import base64
from datetime import datetime
from django.db.models import OuterRef, Subquery
from django.shortcuts import render
from django.http import HttpResponse
from dotenv import load_dotenv
from loguru import logger
from yandex_music import Client
from .models import Chart
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

load_dotenv()
YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')
client = Client(YANDEX_TOKEN).init()


def chart_view(request) -> HttpResponse:
    date_str = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
    track = request.GET.get('track', None)
    track_id = None
    track_correct_name = None

    if track:
        try:
            track_find = client.search(track).best.result
            track_id = track_find.id
            track_correct_name = track_find.title
            logger.info(f"Трек поиска: {track}, ID: {track_id}")
        except Exception as e:
            logger.error(e)
    selected_date = datetime.strptime(date_str, '%Y-%m-%d')

    subquery = Chart.objects.filter(
        position=OuterRef('position'),
        timestamp__date=selected_date.date()
    ).order_by('timestamp').values('pk')[:1]

    unique_chart_entries = Chart.objects.filter(
        pk__in=Subquery(subquery)
    ).order_by('position')

    track_entries = Chart.objects.filter(track_id=track_id) if track_id else None

    chart_base64 = None
    if track_entries:
	    # Создание графика с Matplotlib
        dates = [entry.timestamp.date() for entry in track_entries]
        positions = [entry.position for entry in track_entries]

        plt.figure(figsize=(10, 6))

        # Настройка стиля графика
        plt.plot(
            dates, positions,
            marker='o', linestyle='-', color='royalblue', markersize=2)

        plt.gca().invert_yaxis()  # Инвертируем ось Y, чтобы первая позиция была вверху
        plt.ylim(0, 100)  # Фиксируем диапазон оси Y от 0 до 100

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gcf().autofmt_xdate()

        # Добавляем сетку и настройку осей
        plt.grid(visible=True, linestyle='--', linewidth=0.7, alpha=0.5)  # Прозрачная сетка с пунктирной линией
        plt.xticks(fontsize=10)
        plt.yticks(range(0, 101, 10), fontsize=10)  # Метки оси Y с шагом 10

        # Настройка заголовков и подписей
        plt.title(f'Chart positions for {track_correct_name}', fontsize=14, color='green')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Position', fontsize=12)

        # Сохранение графика в байтовый буфер и конвертация в base64
        buffer = io.BytesIO()
        plt.tight_layout()  # Автоматическая корректировка расстояний
        plt.savefig(buffer, format='png', dpi=100)  # Сохранение с заданным разрешением
        buffer.seek(0)
        image_png = buffer.getvalue()
        chart_base64 = base64.b64encode(image_png).decode('utf-8')
        buffer.close()

        plt.close()

    return render(request, 'chart/chart.html', {
        'chart_entries': unique_chart_entries,
        'selected_date': selected_date,
        'track_name': track_correct_name if track_correct_name else '',
        'track_entries': track_entries,
        'chart_base64': chart_base64  # Передача base64 строки изображения в шаблон
    })

