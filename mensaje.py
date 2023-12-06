import psycopg2
import serial
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import matplotlib.pyplot as plt
from datetime import datetime

# Configuración del puerto serie
ser = serial.Serial('COM5', 9600)  # Ajusta el puerto serie según tu configuración

# Variable de estado para controlar el envío de alertas
alerta_enviada = False

# Configuración del servidor SMTP y credenciales
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'renegonzalezb9@gmail.com'  # Ingresa tu correo electrónico
smtp_password = 'ldbs ggpa asrv nmhp'  # Ingresa tu contraseña

# Configuración del remitente y destinatario
sender_email = 'renegonzalezb9@gmail.com'  # Ingresa tu correo electrónico
receiver_email = 'mariestecruzma70@gmail.com'  # Ingresa el correo de destino

# Listas para almacenar los datos para la gráfica y la base de datos
tiempos = []
niveles_humo = []

# Conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname='proyecto_feria',
    user='postgres',
    password='Rene2004',
    host='localhost'  # Puede variar según la configuración de tu base de datos
)

# Crear un cursor para ejecutar consultas
cursor = conn.cursor()

def guardar_datos_postgresql(dato, fecha):
    try:
        cursor.execute("INSERT INTO appfirefly_dato (concentracion_gases, fecha) VALUES (%s, %s);", (dato, fecha))
        conn.commit()
        print("Datos almacenados en PostgreSQL correctamente.")
    except psycopg2.Error as e:
        print(f"Error al guardar datos en PostgreSQL: {e}")

def send_email(subject, body, attachment_path=None):
    # Crear el objeto mensaje
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Agregar el cuerpo del mensaje
    message.attach(MIMEText(body, 'plain'))

    # Adjuntar archivo si está especificado
    if attachment_path:
        with open(attachment_path, 'rb') as attachment:
            part = MIMEApplication(attachment.read(), Name='alerta.txt')
            part['Content-Disposition'] = f'attachment; filename={part.filename}'
            message.attach(part)

    # Conectar al servidor SMTP y enviar el correo
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

plt.ion()  # Modo interactivo para la gráfica
fig, ax = plt.subplots()
grafica_line, = ax.plot([], [], label='Niveles de Humo')
ax.set_xlabel('Tiempo')
ax.set_ylabel('Niveles de Humo')
ax.set_title('Monitoreo de Niveles de Humo')
ax.legend()

# Bucle principal para escuchar el puerto serie
while True:
    try:
        data = ser.readline().decode().strip()
        if data.startswith("ALERT:"):
            # Se ha recibido una alerta
            alert_value = data.split(":")[1].strip()
            print(f"Alerta de humo detectada: {alert_value}")

            # Verificar si ya se envió una alerta y el nivel de humo es mayor o igual a 1000
            if not alerta_enviada and int(alert_value) >= 1000:
                # Enviar correo electrónico
                subject = 'Alerta de Humo'
                body = f'Se ha detectado un nivel de humo peligroso: {alert_value}'
                send_email(subject, body)

                # Actualizar el estado para evitar enviar más alertas hasta que se restablezca
                alerta_enviada = True
            elif alerta_enviada and int(alert_value) < 1000:
                # Restablecer la alerta cuando el nivel de humo baja por debajo de 1000
                alerta_enviada = False

            # Almacenar datos para la gráfica y la base de datos si hay un cambio significativo
            if not niveles_humo or int(alert_value) != niveles_humo[-1]:
                tiempos.append(len(tiempos) + 1)
                niveles_humo.append(int(alert_value))

                # Obtener la fecha y hora actual en el formato adecuado para PostgreSQL
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S%z")

                # Actualizar la gráfica con los nuevos datos (sin cambios)
                grafica_line.set_xdata(tiempos)
                grafica_line.set_ydata(niveles_humo)
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.05)  # Agregar una pausa para permitir la actualización de la gráfica

                # Guardar el dato y la fecha en PostgreSQL si hay un cambio significativo
                guardar_datos_postgresql(int(alert_value), fecha_actual)

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Error: {e}")

# Cerrar el puerto serie, cursor y la conexión al salir
ser.close()
cursor.close()
conn.close()
