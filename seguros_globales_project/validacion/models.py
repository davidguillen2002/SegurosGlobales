from django.db import models

class ValidacionSiniestro(models.Model):
    numero_poliza = models.CharField(max_length=20)
    resultado_validacion = models.CharField(max_length=10)  # 'Aprobado' o 'Rechazado'

    def __str__(self):
        return f'Validacion {self.numero_poliza} - {self.resultado_validacion}'
