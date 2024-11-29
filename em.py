import imaplib
import email
from email.header import decode_header
import os
import re
import zipfile
import rarfile
import lectura_xml
from getpass import getpass

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def extract_zip(zip_path, extract_to_folder,folder, file):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        print("extract_to_folder:",extract_to_folder)
        zip_ref.extractall(extract_to_folder)
        for file_info in zip_ref.infolist():
            if file_info.filename.endswith('.xml'):
                _path = f'C:/laragon/www/{folder}/'
                lectura_xml.Charge_Shopping(file_info.filename, _path)
                os.remove(f'{_path}factura.xml')

rarfile.UNRAR_TOOL = r'C:\Program Files\UnRAR\unrar.exe'

def extract_rar(rar_path, extract_to_folder,folder, file):
    try:
        with rarfile.RarFile(rar_path) as rar_ref:
            rar_ref.extractall(extract_to_folder)
            # Leer archivos xml extraídos
            for file_info in rar_ref.infolist():
                if file_info.filename.endswith('.xml'):
                    _path = f'C:/laragon/www/{folder}/'
                    lectura_xml.Charge_Shopping(file_info.filename, _path)
                    os.remove(f'{_path}factura.xml')
    except Exception as e:
        print(f"Error al extraer el archivo RAR: {e}")

def GetEmils(username, password):
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(username, password)
        imap.select("INBOX")
        
        search_criteria = '(UNSEEN FROM "Carlos Del Aguila")'
        status, data = imap.search(None, search_criteria)
        if status != 'OK':
            print("Error al buscar correos")
            return
        
        mail_ids = data[0].split()
        
        for mail_id in mail_ids:
            try:
                res, msg_data = imap.fetch(mail_id, "(RFC822)")
                if res != 'OK':
                    print(f"No se pudo recuperar el mensaje {mail_id}")
                    continue
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = decode_header(msg["Subject"])[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode()
                        from_ = msg.get("From")
                        
                        # print(f"Subject: {subject}")
                        # print(f"From: {from_}")
                        # print("Mensaje obtenido con éxito")
                        
                        sanitized_subject = sanitize_filename(subject)
                        
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                if "attachment" in content_disposition:
                                    filename = part.get_filename()
                                    if filename and (filename.endswith('.zip') or filename.endswith('.rar')):
                                        if not os.path.isdir(sanitized_subject):
                                            os.makedirs(sanitized_subject, exist_ok=True)
                                        
                                        file_path = os.path.join(sanitized_subject, filename)
                                        try:
                                            with open(file_path, "wb") as f:
                                                f.write(part.get_payload(decode=True))
                                            # print(f"Archivo {filename} descargado en {file_path}")
                                            
                                            # Extraer el archivo
                                            if filename.endswith('.zip'):
                                                extract_zip(file_path, sanitized_subject)
                                            elif filename.endswith('.rar'):
                                                extract_rar(file_path, sanitized_subject,subject, filename)
                                        except Exception as e:
                                            print(f"Error al guardar el archivo {filename}: {e}")
            except imaplib.IMAP4.error as e:
                print(f"Error al procesar el mensaje {mail_id}: {e}")
    except Exception as exp:
        print(exp)
    finally:
        try:
            imap.close()
        except:
            pass
        try:
            imap.logout()
        except:
            pass
GetEmils("evansoft.test@gmail.com", "fitwvfmgefslsayy")
