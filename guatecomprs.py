

import requests, time, os, signal, pytesseract, cv2, numpy as np
from PIL import Image
from pwn import *
from bs4 import BeautifulSoup

#valiables
url = "https://www.guatecompras.gt/"
path = "captcha.jpg"
path2 = "captcha2.jpg"

def def_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, def_handler)

def cleanImg(path, path2):
    img = cv2.imread(path, 0)
    img = cv2.resize(img, None, fx=2, fy=2)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, blackAndWhite = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackAndWhite, None, None, None, 8, cv2.CV_32S)
    sizes = stats[1:, -1] #get CC_STAT_AREA component
    img2 = np.zeros((labels.shape), np.uint8)

    for i in range(0, nlabels - 1):
        if sizes[i] >= 50:   #filter small dotted regions
            img2[labels == i + 1] = 255

    res = cv2.bitwise_not(img2)
    cv2.imwrite(path2, res)

def makeRequest():

    status = 0

    while status == 0:
        try:
            print("\n-------------------------------------------------")  
            
            #SESION LE PROCESO
            s = requests.session()
            p = log.progress("consultando")
            p.status("Realizando consulta a la url %s\n" % url)
            response = s.get(url + "proveedores/busquedaProvee.aspx")
            
            #FILTA EL CONTENIDO RECUPERADO Y BUSCA LA IMAGEN
            soup = BeautifulSoup(response.content, "html.parser")
            images = soup.find("img", { "id" : "MasterGC_ContentBlockHolder_CaptchaValidacion_CaptchaImage" })
            
            p.success("url captcha recuperado")
          

            p1 = log.progress("Captcha")
            p1.status("Obteniendo valor de Captcha")
            
            url_image = images["src"].replace("../", url)
            captcha_url = s.get(url_image)
            f = open(path, "wb")
            f.write(captcha_url.content)
            f.close()
            
            time.sleep(1)     
            p1.success("Captcha almacenado")
           
            ## limpiar la imagen para ayudar a mejorar la resolucin de la misma
            p2 = log.progress("Limpiar la imagen")
            p2.status("Proceso de limpiesa de imagen")

            cleanImg(path, path2)            

            time.sleep(1)
            p2.success("Finalizo el proseso de remplasar los puntos")

            ## la libreria de resseract lee la imagen para desifrar el texto
            p3 = log.progress("Lectura")
            p3.status("Decodificando imagen")
            #captcha_value = pytesseract.image_to_string(Image.open(path2))
            captcha_value = pytesseract.image_to_string(Image.open(path2), lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            
            #os.remove("captcha.jpg")
           
            captcha_value = captcha_value.replace(" ", "").strip()
            print("\n---------> %s\n" % captcha_value)
            time.sleep(1)
            p3.success("Captcha decodificado exitosamente")

            p4 = log.progress("preparando consultas")
            p4.status("Realizando consulta")

            data_params = {
                'MasterGC$ContentBlockHolder$scriptManager': 'MasterGC$ContentBlockHolder$upnFiltros|MasterGC$ContentBlockHolder$cmdNit',
                '__EVENTTARGET': 'MasterGC$ContentBlockHolder$cmdNit',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': '/wEPDwUKMTk0MTU2NDg1OA9kFgJmD2QWAgIDD2QWBAIBD2QWBAIBDw8WAh4LUG9zdEJhY2tVcmwFKC9Db21wcmFkb3Jlcy9SZWdpc3Ryb1Jlc3VtZW4uYXNweD90eXBlPTFkFgICAQ8PFgIeBFRleHQFC0NvbXByYWRvcmVzZGQCAw8WAh8BZGQCBQ9kFgQCBQ9kFgJmD2QWBAITD2QWAgIBD2QWBGYPDxYEHghDc3NDbGFzcwURYWNjb3JkaW9uQ2FiZWNlcmEeBF8hU0ICAmRkAgEPD2QWAh4Fc3R5bGUFDWRpc3BsYXk6bm9uZTsWAgIBDxAPFgYeDURhdGFUZXh0RmllbGQFC0RFU0NSSVBDSU9OHg5EYXRhVmFsdWVGaWVsZAURVElQT19PUkdBTklaQUNJT04eC18hRGF0YUJvdW5kZ2QQFR8KSU5ESVZJRFVBTBJTT0NJRURBRCBDT0xFQ1RJVkERU09DSUVEQUQgQU7Dk05JTUEcU09DSUVEQUQgRU4gQ09NQU5ESVRBIFNJTVBMRSJTT0NJRURBRCBFTiBDT01BTkRJVEEgUE9SIEFDQ0lPTkVTGFJFU1BPTlNBQklMSURBRCBMSU1JVEFEQRtTVUNVUlNBTCBFTVBSRVNBIEVYVFJBTkpFUkEaQ09OVFJBVE8gRU4gUEFSVElDSVBBQ0nDk04LQ09QUk9QSUVEQUQfUEFUUklNT05JTyBIRVJFRElUQVJJTyBJTkRJVklTTyFCSUVOIEFETUlOSVNUUkFETyBQT1IgRklERUlDT01JU08JQ09OU09SQ0lPI1NPQ0lFREFEIENJVklMIENPTiBGSU5FUyBMVUNSQVRJVk9TC0NPT1BFUkFUSVZBRUFTT0NJQUNJw5NOLCBGVU5EQUNJw5NOLCBJTlNUSVRVQ0nDk04gUkVMSUdJT1NBIFkgT1RSQVMgTk8gTFVDUkFUSVZBUydFTVBSRVNBIEVYVFJBTkpFUkEgSU5TQ1JJVEEgRU4gRUwgUEHDjVMuTUlTScOTTiBESVBMT03DgVRJQ0EgWSBPUkdBTklTTU8gSU5URVJOQUNJT05BTCBPVFJPIFRJUE8gREUgT1JHQU5JWkFDScOTTiBMRUdBTDdFWFRSQU5KRVJPIERJUExPTcOBVElDTyBPIEFHRU5URSBERSBPUkdBTklTTU8gSU5URVJOQUMuDU1VTklDSVBBTElEQUQSRU5USURBRCBERUwgRVNUQURPC0ZJREVJQ09NSVNPLENPTkRPTUlOSU8sIFBST1BJRURBRCBIT1JJWk9OVEFMIFkgU0lNSUxBUkVTIkpVTlRBIEVTQ09MQVIsIENPRURVQ0EgWSBTSU1JTEFSRVM5VGlwbyBkZSBPcmdhbml6YWNpw7NuIHBlbmRpZW50ZSBkZSBjb25maXJtYWNpw7NuIGNvbiBTQVQuOVRpcG8gZGUgT3JnYW5pemFjacOzbiBwZW5kaWVudGUgZGUgY29uZmlybWFjacOzbiBjb24gU0FULjlUaXBvIGRlIE9yZ2FuaXphY2nDs24gcGVuZGllbnRlIGRlIGNvbmZpcm1hY2nDs24gY29uIFNBVC45VGlwbyBkZSBPcmdhbml6YWNpw7NuIHBlbmRpZW50ZSBkZSBjb25maXJtYWNpw7NuIGNvbiBTQVQuOVRpcG8gZGUgT3JnYW5pemFjacOzbiBwZW5kaWVudGUgZGUgY29uZmlybWFjacOzbiBjb24gU0FULjlUaXBvIGRlIE9yZ2FuaXphY2nDs24gcGVuZGllbnRlIGRlIGNvbmZpcm1hY2nDs24gY29uIFNBVC4FVG9kb3MVHwEwATEBMgEzATQBNQE2ATcCMTACMTECMTICMTMCMTQCMTUCMTYCMTcCMTgCMTkCMjACNDkCNTACNTECNTICNTMCNTQCNTUCNTYCNTcCNTgCNjECLTEUKwMfZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2RkAhUPZBYCZg9kFgICAQ8UKwADDxYGHhVFbmFibGVFbWJlZGRlZFNjcmlwdHNnHhJSZXNvbHZlZFJlbmRlck1vZGULKXNUZWxlcmlrLldlYi5VSS5SZW5kZXJNb2RlLCBUZWxlcmlrLldlYi5VSSwgVmVyc2lvbj0yMDE5LjMuMTAyMy40NSwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0xMjFmYWU3ODE2NWJhM2Q0AR4XRW5hYmxlQWpheFNraW5SZW5kZXJpbmdoZBYCHgtDdXJyZW50R3VpZAUkYjBiZGIwNTgtNTMyOS00MTg0LTk2MTUtMDI5MGVmNTIyNGY2FCsAA2RkZBYCAgEPZBYMZg9kFgJmD2QWCGYPDxYKHgZIZWlnaHQbAAAAAAAASUABAAAAHgVXaWR0aBsAAAAAAIBmQAEAAAAfAmUeCEltYWdlVXJsBVx+L1RlbGVyaWsuV2ViLlVJLldlYlJlc291cmNlLmF4ZD90eXBlPXJjYSZpc2M9dHJ1ZSZndWlkPWIwYmRiMDU4LTUzMjktNDE4NC05NjE1LTAyOTBlZjUyMjRmNh8DAoIDZGQCAQ8PFgIfAQUEdGVzdBYCHgV0aXRsZQUEdGVzdGQCAg8WBB4JaW5uZXJodG1sBQ5HZXQgQXVkaW8gQ29kZR4EaHJlZgVkfi9UZWxlcmlrLldlYi5VSS5XZWJSZXNvdXJjZS5heGQ/dHlwZT1jYWgmYW1wO2lzYz10cnVlJmFtcDtndWlkPWIwYmRiMDU4LTUzMjktNDE4NC05NjE1LTAyOTBlZjUyMjRmNmQCAw8WBB8QBRNEb3dubG9hZCBBdWRpbyBDb2RlHxEFZH4vVGVsZXJpay5XZWIuVUkuV2ViUmVzb3VyY2UuYXhkP3R5cGU9Y2FoJmFtcDtpc2M9dHJ1ZSZhbXA7Z3VpZD1iMGJkYjA1OC01MzI5LTQxODQtOTYxNS0wMjkwZWY1MjI0ZjZkAgEPDxYKHwwbAAAAAAAASUABAAAAHw0bAAAAAACAZkABAAAAHwJlHw4FXH4vVGVsZXJpay5XZWIuVUkuV2ViUmVzb3VyY2UuYXhkP3R5cGU9cmNhJmlzYz10cnVlJmd1aWQ9YjBiZGIwNTgtNTMyOS00MTg0LTk2MTUtMDI5MGVmNTIyNGY2HwMCggNkZAICDxYEHxAFDkdldCBBdWRpbyBDb2RlHxEFZH4vVGVsZXJpay5XZWIuVUkuV2ViUmVzb3VyY2UuYXhkP3R5cGU9Y2FoJmFtcDtpc2M9dHJ1ZSZhbXA7Z3VpZD1iMGJkYjA1OC01MzI5LTQxODQtOTYxNS0wMjkwZWY1MjI0ZjZkAgMPFgQfEAUTRG93bmxvYWQgQXVkaW8gQ29kZR8RBWR+L1RlbGVyaWsuV2ViLlVJLldlYlJlc291cmNlLmF4ZD90eXBlPWNhaCZhbXA7aXNjPXRydWUmYW1wO2d1aWQ9YjBiZGIwNTgtNTMyOS00MTg0LTk2MTUtMDI5MGVmNTIyNGY2ZAIED2QWAmYPFgQfDwUXTWlzc2luZyBCcm93c2VyIFBsdWctSW4fEAUXTWlzc2luZyBCcm93c2VyIFBsdWctSW5kAgUPZBYEZg8PFgofAmUeCUFjY2Vzc0tleWUeCFRhYkluZGV4AQAAHgdUb29sVGlwZR8DAgJkZAIBDw8WBh8CBQxtZW5zYWplRXJyb3IfAWUfAwICZGQCBw9kFgJmD2QWAgIDD2QWAgIDDzwrABECARAWABYAFgAMFCsAAGQYAwUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFLU1hc3RlckdDJENvbnRlbnRCbG9ja0hvbGRlciRDYXB0Y2hhVmFsaWRhY2lvbgUnTWFzdGVyR0MkQ29udGVudEJsb2NrSG9sZGVyJGd2UmVzdWx0YWRvD2dkBS1NYXN0ZXJHQyRDb250ZW50QmxvY2tIb2xkZXIkQ2FwdGNoYVZhbGlkYWNpb24PFCsAAgUkYjBiZGIwNTgtNTMyOS00MTg0LTk2MTUtMDI5MGVmNTIyNGY2BgAAAAAAAAAAZEY0ETaUWSHEPeRcLSzfD18HlNp2',
                '__VIEWSTATEGENERATOR': '057445F7',
                '__EVENTVALIDATION': '/wEdADMlNy/W0eNsxlKch+orQLo5je99Gv5nJDYxLMJR3Ni/+VoSYmFn6JSrl3ztwpfEnYTcFg4ZhskzIb/X+k0uuj/V/elSD6xdtpw47iYyOjH0wtn460PgPKMqJ7flgEW14sZhjzCmfBk7kkXErEUOeRSaCi2Yr+jgYfFkqOnluNpiXQ0wDFWKQrZSXLKh5JDaINi1rOxGR61qxl8jF3IfU1xkGfx9xIsW6sLTYH9RGxpBt1cIX8YW4NLSoxVDd9t8ZOmm7MnHGwQbWd3WZBuKnRoDExGlE3WQwIWm5xnVbkH8RUbwL2ZlELoMqxnzBr1ICNukNyVArpxk6HPWVWqGiERX94esEefj1jUshlulokIpaOqYRCC04g7Rs5MOX6u7DgdQOk8f7rFpKSZiUjO2kJ8JhzQ8eQXCl2RmQ9sYrqBVQwjNwmO5qSUV7CWZudgNxYl05BhzNoaF9LvOLiuueXdGp91PcdI7QBJcVChQpFPVvts4zPXq7VyRbvVszZ7D06K41oB4jfKIWPejD9+wD68NBtJHuKib2/2grWzmoB5duHMbWzO3ygERGxMCMYuodc0z1gMD1LLvPKCon62VZvSPJXKqMm22xvSOcxh9sZ47B3oW4xE9Z+NJU5/e7Q+1o/zJBapi5y+o8MHaR5S9i/DnN3EM2KNcI+YJYScii0NJUdMja36MBHjuMPfgpIhvUD7J6l6SHlPFB/yJRIIFp+9B7rebJMnPOFAZBxn6w2CpWVR1WUI92LnnOEqNgs6dC2TanClaR7PoApAgDw4HEjEPrqPPUPlnt1P/MDVZeW9kJkSjhUxDQuMQp9TGVyLv69olnc0WsNRQhaCFCxFzZ88mZYdum3Ckx+h7HpQREObBtY/F8HUnU4BEaYHRSJ2xWqeFU9CeUPavoLGyc982TGi0+Rbx0C/LVKjJDJ3pHb62MwqDqcX/WsXVALeLi2Xs/5jkfQcw1QP5eqEiHOFLaVKgFNuoTRWnqY4IJQFos+oxTNNaWQ/Ti6fxgCZKUdUD0agBJdx83DBgGRb0ssu+x0hkSLkYEvYgba7QPCAQ/4GmeDEc5wVaC/eq47KSTWTN0m4zIQ6gx5XGufFgT0o6IXF72rs4NA==',
                'MasterGC$ContentBlockHolder$txtNit': '57404380',
                'MasterGC$ContentBlockHolder$TextBox7': '',
                'MasterGC$ContentBlockHolder$txtCUI': '',
                'MasterGC$ContentBlockHolder$txtNuevaBusquedaNombre': '',
                'MasterGC$ContentBlockHolder$TextBox5': '',
                'MasterGC$ContentBlockHolder$Accordion1_AccordionExtender_ClientState': -1,
                'MasterGC$ContentBlockHolder$ctl04$ddlBusCarEn': -1,
                'MasterGC$ContentBlockHolder$ctl04$ddlOpcionesNombre': 2,
                'MasterGC$ContentBlockHolder$ctl04$ddlTipo': 3,
                'MasterGC$ContentBlockHolder$CaptchaValidacion$CaptchaTextBox': '%s' % captcha_value,
                'MasterGC_ContentBlockHolder_CaptchaValidacion_ClientState': '',
                '__ASYNCPOST': 'true'
            }
            
            response2 = s.post(url + 'proveedores/busquedaProvee.aspx', data=data_params)  
           
            if 'Detalle del Proveedor' in response2.text:
                soup = BeautifulSoup(response2.text, 'html.parser')
                print(soup.prettify)
                p4.success("consulta realizada")
                status = 1
            else:
                p4.failure("error en la consulta")

            
        except Exception as e:
            log.failure("Ha ocurrido un error: %s" % str(e))
            sys.exit(1)


if __name__ == "__main__":
    makeRequest()
