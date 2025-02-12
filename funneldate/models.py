from django.db import models

# Create your models here.
class FunnelDate(models.Model):
    date = models.DateField()
    time = models.TimeField()
    g_meet_code = models.CharField(max_length=255,null =True,blank = True)

    def __str__(self):
        return f"{self.date} - {self.time}"
