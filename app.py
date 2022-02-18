#!/usr/bin/python
#coding: utf-8

import requests, time, os, signal, re, pytesseract
from PIL import Image 
from pwn import *

#Variables
url = "http://127.0.0.1"

def def_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, def_handler)

def makeRequest():
    status = 0
    while status == 0:
        try:
            s = requests.session()
            response = s.get(url + "/index.php")

            ran_valu = re.search(r'\d{5,10}', response.text)
            url_image = url + "/captcha.php?rand=" + ran_valu.group(0)
            
            captcha_url = s.get(url_image)
            f = open("captcha.jpg", "wb")
            f.write(captcha_url.content)
            f.close()  

            print("\n-------------------------------------------------")  

            p1 = log.progress("Captcha")
            p1.status("Obteniendo valor de Captcha")
            #time.sleep(1)

            captcha_value = pytesseract.image_to_string(Image.open("captcha.jpg"))
            os.remove("captcha.jpg")

            p1.success("Captcha almacenado")
            #time.sleep(1)

            print("\n---------> %s\n" % captcha_value)

            post_data = {
                'captcha': '%s' % (captcha_value.strip()),
                'submit': 'Submit'
            }
            p2 = log.progress("Validacion")
            p2.status("Proporcionando Captcha")

            r2 = s.post(url + "/index.php", data=post_data)
        

            if "Entered captcha code does not match" not in r2.text and captcha_value.strip():
                p2.success("Captcha introduccido correcto")
                status = 1
            else:
                p2.failure("Captcha introduccido incorecto")

        except Exception as e:
            log.failure("Ha ocurrido un error: %s" % str(e))
            sys.exit(1)
    

if __name__ == '__main__':
    makeRequest()