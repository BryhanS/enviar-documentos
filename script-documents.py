# %%
from dotenv import dotenv_values
from datetime import datetime, timedelta
import requests
import os
import wget
import zipfile
from os import path




# %%
if not path.exists('./Documentos'):
    os.mkdir('Documentos')
    os.mkdir('Documentos/Online')
    os.mkdir('Documentos/Tienda')


# %%
os.system("rm ./Documentos/Online/*.pdf")
os.system("rm ./Documentos/Tienda/*.pdf")
os.system("rm *.zip")


# %%
config = dotenv_values(".env")

# Usar las variables de entorno
api_key = config["API_KEY_SISTEMA"]
url = config["URL_SISTEMA"]

# %%
day = datetime.now().date()
day_week = day.strftime("%A")
intial_date = ""
final_date = ""


if day_week == 'Monday':
    intial_date = (day - timedelta(days=3)).strftime("%Y%m%d")
    final_date = (day - timedelta(days=1)).strftime("%Y%m%d")    
else:
    intial_date = (day - timedelta(days=1)).strftime("%Y%m%d")
    final_date = (day - timedelta(days=1)).strftime("%Y%m%d")    



url_path = f'{url}api/documents/lists/{intial_date}/{final_date}'

# %%

# Headers with the API token
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',  # Adjust the content type as needed
}

# Make a GET request with headers
response = requests.get(url_path, headers=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # The response data in JSON format
    data_final = response.json()
    # print('API Data:', data_final)s
else:
    # Print an error message if the request was not successful
    print(f'Error in the request. Status code: {response.status_code}')
    print('Error message:', response.text)


# %%

json_data = data_final

# %%

rows = []
for documentos in json_data['data']:

    download_path = ""

    numComprobantePago = documentos["number"].split('-')[0]
    download_pdf = documentos["download_pdf"]
    if numComprobantePago == "B001" or numComprobantePago == "F001":
        download_path = './Documentos/Tienda'

        wget.download(download_pdf, out=download_path)
    else:
        download_path = './Documentos/Online'
        download_pdf = documentos["download_pdf"]
        wget.download(download_pdf, out=download_path)    




    

# %% [markdown]
# 

# %%

def zip_dir(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))

# Ruta de la carpeta que deseas comprimir
folder_to_zip = './Documentos'

# Ruta y nombre del archivo ZIP resultante
zip_file_path = f'./{intial_date}-{final_date}.zip'

# Comprimir la carpeta
zip_dir(folder_to_zip, zip_file_path)

# %%
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# %%
# Configuración del servidor SMTP
api_key = config["API_KEY_SISTEMA"]

smtp_server = 'smtpout.secureserver.net'
smtp_port = 587  # Puerto SMTP (generalmente 587 o 465)
smtp_username = config["EMAIL_USER"]
smtp_password = config["EMAIL_PASS"]

# Configuración del mensaje
sender = config["EMAIL_USER"]
receiver = config["EMAIL_DEST"]
subject = f'Ventas del {intial_date}-{final_date} Facturador'
body = 'Se envia los Documentos emitidos en los puntos de Venta'
archivo_adjunto = zip_file_path

# Crear el mensaje
message = MIMEMultipart()
message['From'] = sender
message['To'] = ','.join(receiver)
message['Subject'] = subject
message.attach(MIMEText(body, 'plain'))

# Adjuntar archivo ZIP
with open(archivo_adjunto, 'rb') as f:
    part = MIMEApplication(f.read(), Name=archivo_adjunto)
    part['Content-Disposition'] = f'attachment; filename="{archivo_adjunto}"'
    message.attach(part)

# Iniciar sesión en el servidor SMTP y enviar el correo
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()  # Habilitar cifrado TLS
    server.login(smtp_username, smtp_password)
    server.sendmail(sender, receiver, message.as_string())

print('Correo electrónico enviado con éxito.')


