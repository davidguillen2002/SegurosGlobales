# Generated by Django 5.1.2 on 2024-10-21 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Reclamo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_poliza', models.CharField(max_length=20)),
                ('monto_reclamo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_siniestro', models.DateField()),
                ('descripcion_siniestro', models.TextField()),
                ('estado', models.CharField(default='Pendiente', max_length=20)),
            ],
        ),
    ]
