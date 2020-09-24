#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import getpass
from optparse import OptionParser

import asyncio
import slixmpp
from slixmpp.exceptions import IqError, IqTimeout

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout slixmpp, we will set the default encoding
# ourselves to UTF-8.
'''
if sys.version_info < (3, 0):
    from slixmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input
'''
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class RegisterBot(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)

    def start(self, event):
        
        self.send_presence()
        self.get_roster()
        self.disconnect()

    async def register(self, iq):
        
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            await resp.send()
            print("Account created for %s!" % self.boundjid)
        except IqError as e:
            print("Could not register account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            print("No response from server.")
            self.disconnect()

class Client(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()


if __name__ == '__main__':
    st_log = False

    while st_log == False:
        print("Bienvenido al chat basado en XMPP \n Por favor elija alguna de las siguientes opcions para empezar: \n 1 - Iniciar sesion \n 2 - Registrarse \n 3 - borrar un user\n 4 - salir del chat\n")
        eleccion = input("opcion: ")
        if eleccion == '1':
            #codigo para iniciar sesion
            userJID = input("userJID: ")
            password = input("password: ")
            xmpp = Client(userJID + "@redes2020.xyz", password)
            xmpp.register_plugin('xep_0030') # Service Discovery
            xmpp.register_plugin('xep_0004') # Data Forms
            xmpp.register_plugin('xep_0060') # PubSub
            xmpp.register_plugin('xep_0199') # XMPP Ping
            if xmpp.connect():
                xmpp.process(block=False)
                access = True
                print("login Listo")
                while access:
                    print("elija una de las siguientes opciones: \n1. Mostrar todos los usuarios y su estado \n2. Agregar un usuario a sus contactos \n3. Mostrar detalles de contacto de un usuario \n4. Comunicacion 1 a 1 con algun usuario \n5. participar en conversacion grupal \n6. salir ")
                    opcion = input("opcion a elegir es: ")
                    if opcion == "1":
                        #codigo para mostrar usuarios
                        print("1")
                    if opcion == "2":
                        #codigo para agregar contanto
                        print("2")
                    if opcion == "3":
                        #codigo para mostrar detalles de un contanto
                        print("3")
                    if opcion == "4":
                        #codigo para iniciar conversacion 1 a 1 con otro usuario
                        print("4")
                    if opcion == "5":
                        #codigo para añadirme a un chat grupal
                        print("5")
                    if opcion == "6":
                        xmpp.disconnect()
                        access = False
                    if opcion != "1" or opcion != "2" or opcion != "3" or opcion != "4" or opcion != "5" or opcion != "6": 
                        print("ha escrito mala su eleccion. Por favor, intentelo y sin dejar espacios en blanco")
            else:
                print("Unable to connect.")

        if eleccion == '2':
            #codigo para registrarse
            # Setup the RegisterBot and register plugins. Note that while plugins may
            # have interdependencies, the order in which you register them does
            # not matter.
            userJID = input("userJID: ")
            password = input("password: ")

            xmpp = RegisterBot(userJID + "@redes2020.xyz", password)
            
            # Some servers don't advertise support for inband registration, even
            # though they allow it. If this applies to your server, use:
            
            xmpp.register_plugin('xep_0030') # Service Discovery
            xmpp.register_plugin('xep_0004') # Data forms
            xmpp.register_plugin('xep_0066') # Out-of-band Data
            xmpp.register_plugin('xep_0077') # In-band Registration
            xmpp['xep_0077'].force_registration = True
            xmpp.connect()
            xmpp.process()
        if eleccion == '3':
            userJID = input("userJID: ")
            password = input("password: ")
            xmpp = Client(userJID, password)
            xmpp.register_plugin('xep_0030') # Service Discovery
            xmpp.register_plugin('xep_0004') # Data Forms
            xmpp.register_plugin('xep_0060') # PubSub
            xmpp.register_plugin('xep_0199') # XMPP Ping
            if xmpp.connect():
                xmpp.process(block=False)
                xmpp.del_roster_item(userJID + "@redes2020.zxy")
                xmpp.disconnect()
            else:
                print("Unable to connect.")
        if eleccion == '4':
            st_log = True
        if eleccion != '1' or eleccion != '2' or eleccion != '3' or eleccion != '4':
            print("Por favor, solo elija el numero de las opciones que se le ha proporcionado sin dejar espacios\n")

