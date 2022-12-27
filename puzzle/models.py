from django.db import models


class PuzzlePiece(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()
