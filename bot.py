import os, sys, re, time, psycopg2, unidecode
from roman import toRoman
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def echo(bot, update):
    if "/c" in update.message.text: #Claves Azules
        claves = re.findall(patron_azules, update.message.text)
        b = 0

        if len(claves) > 0:
            resp  = ""
            for c in claves:
                c = c.upper()
                for n in azules:
                    if c in n[0]:
                        b = 1
                        resp += f"{c} es {n[2]} {n[3].split()[0]} y pertenece a la generación {toRoman(n[1])}.\n"
            if b == 1:
                update.message.reply_text(resp)
            else:
                update.message.reply_text("Parece que no mencionaste a nadie conocido o no esta en mis registros...\nIntenta de nuevo.")

        else:
            update.message.reply_text("Parece que no mencionaste a nadie...\nIntenta de nuevo.")
   
    elif "/n" in update.message.text: #Nombres Azules
        palabras = update.message.text.split()
        nombres_encontrados = ""
        for nombre in palabras:
            if len(nombre) > 2:
                nombre = normaliza(nombre)
                for n in azules:
                    if nombre in normaliza(n[2]):
                        nombres_encontrados += n[0] + ", "

        if len(nombres_encontrados) > 0:
            update.message.reply_text(f"Las siguientes claves tienen ese nombre {nombres_encontrados.strip(', ')}.")
        else:
            update.message.reply_text("Parece que no hay nadie con ese nombre...\nIntenta de nuevo.")

    elif "/a" in update.message.text: #Apellidos Azules
        palabras = update.message.text.split()
        apellidos_encontrados = ""
        for apellido in palabras:
            if len(apellido) > 2:
                apellido = normaliza(apellido) 
                for n in azules:
                    if apellido in normaliza(n[3]):
                        apellidos_encontrados += n[0] + ", "

        if len(apellidos_encontrados) > 0:
            update.message.reply_text(f"Las siguientes claves tienen ese apellidos {apellidos_encontrados.strip(', ')}.")
        else:
            update.message.reply_text("Parece que no hay nadie con ese apellido...\nIntenta de nuevo.")

    elif "/ic" in update.message.text: #Internos Claves
        claves = re.findall(patron_interno, update.message.text)
        b = 0

        if len(claves) > 0:
            resp  = ""
            for c in claves:
                for n in internos:
                    if c.upper() in n[0].upper():
                        b = 1
                        resp += f"{n[0]} es {n[2]} {n[3].split()[0]}. Gen {toRoman(n[1])}.\n"
            if b == 1:
                update.message.reply_text(resp)
            else:
                update.message.reply_text("Parece que no mencionaste a nadie conocido o no esta en mis registros...\nIntenta de nuevo.")

        else:
            update.message.reply_text("Parece que no mencionaste a nadie...\nIntenta de nuevo.")

    elif "/in" in update.message.text: #Internos Nombres
        palabras = update.message.text.split()
        encontrados = ""
        for nombre in palabras:
            if len(nombre) > 2:
                nombre = normaliza(nombre)
                for n in internos:
                    if nombre in normaliza(n[2]):
                        encontrados += f"{n[0]} es {n[2]} {n[3].split()[0]}.\n"

        if len(encontrados) > 0:
            update.message.reply_text(f"{encontrados}Generación {toRoman(n[1])}.")
        else:
            update.message.reply_text("Parece que no hay nadie con ese nombre...\nIntenta de nuevo.")
            
    elif "/h" in update.message.text: #Ayuda
        update.message.reply_text('\
            \nPara buscar por clave usa "/clave" ó "/c" más las claves a buscar.\
            \nPara buscar por nombre usa "/nombre" ó "/n" más los nombres a buscar.\
            \nPara buscar por apellido usa "/apellido"  ó "/a"más los apellidos a buscar.\
            \nPara buscar internos por clave usa "/iclave" ó "/ic" más las claves.\
            \nPara buscar internos por nombre usa "/inombre" ó "/in" más los nombres a buscar.\
            \n\nEjemplo\
            \n"/clave A101 A027 A007 A010*"\
            \n"/c a342"\
            \n"/iclave cKGr"\
            \n"/in Sam"\
            \n"/nombre Luis"\
            \n"/apellido Castillo"\
            \n\nComparte https://t.me/sistemedicbot\
            \nCódigo Fuente https://github.com/mucinoab/SistemedicBot/')

    elif "/s" in update.message.text: #Mensaje Inicial
        update.message.reply_text(\
            'Hola soy el SistemedicBot.\
            \nPara buscar por clave usa "/clave" más las claves a buscar.\
            \nPara buscar por nombre usa "/nombre" más los nombres a buscar.\
            \nPara buscar por apellido usa "/apellido" más los apellidos a buscar.\
            \nPara buscar interno por clave usa "/iclave" más las claves.\
            \nPara buscar internos por nombre usa "/inombre" más los nombres a buscar.\
            \n\nEjemplo\
            \n"/clave A101 A027 A007 A001 A010* A010"\
            \n"/iclave cKGr"\
            \n"/inombre Karol"\
            \n"/nombre Luis"\
            \n"/apellido Castillo"\
            \n\nPara ayuda usa /help')

    else:
        update.message.reply_text('No te entendí...\nIntenta de nuevo o usa "/h" para ayuda.')

    print(f'{update.message.text} {update.message.from_user.first_name}')
    sys.stdout.flush()


def normaliza(text):
    return unidecode.unidecode(text.casefold())

def run(updater):
    PORT = int(os.environ.get("PORT", "8443"))
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    updater.start_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=TOKEN)
    updater.bot.set_webhook(f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")
    updater.idle()

if __name__ == '__main__':
    DATABASE_URL = os.environ['DATABASE_URL']
    TOKEN = os.getenv("TOKEN")
    
    BDD = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = BDD.cursor()

    cur.execute("Select * from bot_claves")
    azules = cur.fetchall()

    cur.execute("Select * from bot_internos")
    internos = cur.fetchall()

    patron_azules = re.compile(r"[Aa]\d{3}\*?")
    patron_interno = re.compile(r"[cC]\S{3}")

    stderr_fileno = sys.stderr

    updater = Updater(TOKEN)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    run(updater)
