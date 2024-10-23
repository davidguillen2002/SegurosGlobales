import csv
from django.http import HttpResponse
from django.shortcuts import render
from .models import Reclamo
import paramiko
import io

# Detalles del servidor SFTP
SFTP_HOST = '127.0.0.1'  # O 'localhost'
SFTP_PORT = 22  # Puerto SFTP
SFTP_USER = 'tester'  # Usuario del servidor SFTP
SFTP_PASS = 'password'  # Contraseña del servidor SFTP
SFTP_REMOTE_PATH = 'reclamos.csv'  # Ruta en el servidor SFTP

# Nueva vista para mostrar la página de exportación
def exportar_reclamos_view(request):
    return render(request, 'reclamos/exportar_reclamos.html')

# Función para transferir el archivo al servidor SFTP
def transferir_archivo_sftp(file_content):
    try:
        # Conectar al servidor SFTP
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)

        sftp = paramiko.SFTPClient.from_transport(transport)

        # Crear un archivo temporal para el contenido
        with open('reclamos_temp.csv', 'w', encoding='utf-8-sig', newline='') as temp_file:
            temp_file.write(file_content)

        # Transferir el archivo generado dinámicamente al servidor SFTP
        sftp.put('reclamos_temp.csv', SFTP_REMOTE_PATH)

        # Cerrar la conexión SFTP
        sftp.close()
        transport.close()

        print("Archivo transferido correctamente a SFTP.")
        return True
    except Exception as e:
        print(f'Error al transferir el archivo SFTP: {e}')
        return False


# Función para exportar reclamos en formato CSV
def exportar_reclamos_csv(request):
    # Crear la respuesta como archivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reclamos.csv"'

    # Usar StringIO para construir el archivo CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)

    # Escribir los encabezados del archivo CSV
    writer.writerow(['Numero Poliza', 'Monto Reclamo', 'Fecha Siniestro', 'Descripcion Siniestro'])

    # Obtener todos los reclamos pendientes
    reclamos = Reclamo.objects.filter(estado='Pendiente')
    for reclamo in reclamos:
        writer.writerow([reclamo.numero_poliza, reclamo.monto_reclamo, reclamo.fecha_siniestro, reclamo.descripcion_siniestro])

    # Obtener el contenido del archivo CSV
    csv_content = output.getvalue()

    # Transferir el archivo CSV a SFTP
    if transferir_archivo_sftp(csv_content):
        print("Archivo CSV transferido correctamente.")
    else:
        print("Error al transferir el archivo CSV.")

    # Añadir el BOM para asegurar la codificación correcta en UTF-8
    response.write('\ufeff'.encode('utf-8'))
    response.write(csv_content.encode('utf-8'))

    return response