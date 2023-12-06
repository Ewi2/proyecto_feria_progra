from django.db import models

class Detector(models.Model):
    nombre = models.CharField(max_length=100)
    sensibilidad = models.DecimalField(max_digits=3, decimal_places=1)
    umbral_alarma = models.DecimalField(max_digits=3, decimal_places=1)

    def _str_(self):
        return self.nombre

class Alarma(models.Model):
    fecha = models.DateTimeField()
    detector = models.ForeignKey(Detector, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100)
    descripcion = models.TextField()

    def _str_(self):
        return f'{self.fecha}: {self.detector.nombre}: {self.tipo}'

class Dato(models.Model):
    fecha = models.DateTimeField()
    concentracion_gases = models.BigIntegerField()

    def _str_(self):
        return f'{self.fecha}: {self.concentracion_gases}'