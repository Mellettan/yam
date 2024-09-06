from django.db import models


class Chart(models.Model):
    position = models.IntegerField()  # Позиция трека в чарте
    name = models.CharField(max_length=255)  # Имя трека
    artists = models.JSONField()  # Список артистов в формате JSON
    track_id = models.CharField(max_length=255)  # ID трека
    timestamp = models.DateTimeField(auto_now_add=True)  # Временная метка создания записи

    def __str__(self):
        return f"{self.position}: {self.name} by {', '.join(str(self.artists))}"
