from django.contrib import admin
from .models import Chart


@admin.register(Chart)
class ChartAdmin(admin.ModelAdmin):
    list_display = ('position', 'name', 'track_id', 'timestamp')  # Поля, отображаемые в списке записей
    search_fields = ('name', 'artists', 'track_id')  # Поля, по которым можно искать
    list_filter = ('timestamp',)  # Поля для фильтрации
    ordering = ('position',)  # Сортировка по умолчанию

    def artists_list(self, obj):
        # Отображаем список артистов в читаемом формате
        return ', '.join(obj.artists) if isinstance(obj.artists, list) else str(obj.artists)

    artists_list.short_description = 'Artists'  # Название колонки
