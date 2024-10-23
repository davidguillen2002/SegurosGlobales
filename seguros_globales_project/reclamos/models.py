from django.db import models

class Reclamo(models.Model):
    numero_poliza = models.CharField(max_length=20)
    monto_reclamo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_siniestro = models.DateField()
    descripcion_siniestro = models.TextField()
    estado = models.CharField(max_length=20, default='Pendiente')  # Estado del reclamo

    def __str__(self):
        return f'Reclamo {self.numero_poliza}'
