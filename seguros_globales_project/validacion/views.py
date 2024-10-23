import csv
import paramiko
from django.http import HttpResponse
from django.shortcuts import render
from .models import ValidacionSiniestro
from reclamos.models import Reclamo  # Importamos Reclamo para actualizar el estado
import os

# Detalles del servidor SFTP
SFTP_HOST = '127.0.0.1'
SFTP_PORT = 22
SFTP_USER = 'tester'
SFTP_PASS = 'password'
SFTP_REMOTE_PATH = 'resultado_validacion.csv'  # Ruta en el servidor SFTP

# Función para transferir un archivo al servidor SFTP
def transferir_archivo_sftp(local_path, remote_path):
    try:
        # Conectar al servidor SFTP
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)

        sftp = paramiko.SFTPClient.from_transport(transport)

        # Transferir el archivo local al servidor SFTP
        sftp.put(local_path, remote_path)

        sftp.close()
        transport.close()
        print(f"Archivo transferido correctamente a {remote_path} en el servidor SFTP.")
        return True
    except Exception as e:
        print(f'Error al transferir el archivo SFTP: {e}')
        return False


# Vista para procesar los reclamos CSV y mostrar un formulario para subir el archivo
def procesar_reclamos_csv(request):
    if request.method == 'POST':
        if 'archivo' not in request.FILES:
            return HttpResponse('No se ha proporcionado un archivo', status=400)

        archivo_reclamos = request.FILES['archivo']
        reader = csv.reader(archivo_reclamos.read().decode('utf-8-sig').splitlines(), delimiter=';', quoting=csv.QUOTE_NONNUMERIC)

        next(reader)  # Saltar la cabecera
        resultados = []

        for index, row in enumerate(reader, start=1):
            if len(row) == 0:
                print(f"Advertencia: Fila {index} está vacía.")
                continue

            try:
                numero_poliza = row[0]
            except IndexError:
                print(f"Error: No se encontró el número de póliza en la fila {index}.")
                continue

            try:
                if numero_poliza[-1].isdigit():
                    resultado = 'Aprobado' if int(numero_poliza[-1]) % 2 == 0 else 'Rechazado'
                else:
                    resultado = 'Rechazado'
            except Exception as e:
                print(f"Error procesando la póliza {numero_poliza} en la fila {index}: {e}")
                resultado = 'Rechazado'

            ValidacionSiniestro.objects.create(numero_poliza=numero_poliza, resultado_validacion=resultado)
            resultados.append([numero_poliza, resultado])

        # Generar un archivo CSV con los resultados de la validación
        local_csv_path = 'resultado_validacion.csv'  # Ruta temporal en el servidor local
        with open(local_csv_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(['Numero Poliza', 'Resultado Validacion'])
            writer.writerows(resultados)

        # Transferir el archivo al servidor SFTP
        if transferir_archivo_sftp(local_csv_path, SFTP_REMOTE_PATH):
            print("Archivo transferido correctamente al servidor SFTP.")
        else:
            print("Error al transferir el archivo al servidor SFTP.")

        # Eliminar el archivo local generado temporalmente
        os.remove(local_csv_path)

        # También devolver el archivo generado como respuesta para descarga
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="resultado_validacion.csv"'
        writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(['Numero Poliza', 'Resultado Validacion'])
        writer.writerows(resultados)

        return response

    return render(request, 'validacion/procesar_reclamos.html')


# Función para descargar un archivo desde el servidor SFTP
def descargar_archivo_sftp():
    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)

        sftp = paramiko.SFTPClient.from_transport(transport)

        # Descargar el archivo desde el servidor SFTP a la ubicación local
        sftp.get(SFTP_REMOTE_PATH, 'resultado_validacion.csv')

        sftp.close()
        transport.close()

        return 'resultado_validacion.csv'
    except Exception as e:
        print(f'Error al descargar el archivo SFTP: {e}')
        return None


# Función para actualizar los estados de los reclamos según el archivo descargado
def actualizar_reclamos(request):
    archivo = descargar_archivo_sftp()
    if archivo:
        try:
            with open(archivo, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                next(reader)

                for row in reader:
                    numero_poliza, resultado = row
                    try:
                        reclamo = Reclamo.objects.get(numero_poliza=numero_poliza)
                        reclamo.estado = resultado
                        reclamo.save()
                    except Reclamo.DoesNotExist:
                        print(f"Reclamo con número de póliza {numero_poliza} no encontrado.")

            return HttpResponse('Reclamos actualizados correctamente.')
        except Exception as e:
            return HttpResponse(f"Error procesando el archivo: {e}", status=500)
    return HttpResponse('Error al actualizar los reclamos: No se pudo descargar el archivo.', status=500)