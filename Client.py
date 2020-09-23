#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class RegisterBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start, threaded=True)
        self.add_event_handler("register", self.register, threaded=True)

    def start(self, event):
        
        self.send_presence()
        self.get_roster()
        self.disconnect()

    def register(self, iq):
        
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            resp.send(now=True)
            logging.info("Account created for %s!" % self.boundjid)
        except IqError as e:
            logging.error("Could not register account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()


if __name__ == '__main__':
    st_log = False

    while st_log == False:
        print("Bienvenido al chat basado en XMPP \n Por favor elija alguna de las siguientes opcions para empezar: \n 1 - Iniciar sesion \n 2 - Registrarse \n 3 - salir del chat\n")
        eleccion = input("opcion: ")
        if eleccion == '1':
            #codigo para iniciar sesion

            if xmpp.connect():
                xmpp.process(block=True)
                access = True
                print("login Listo")
                while access:
                    print("elija una de las siguientes opciones: \n1. Mostrar todos los usuarios y su estado \n2. Agregar un usuario a sus contactos \n3. Mostrar detalles de contacto de un usuario \n4. Comunicacion 1 a 1 con algun usuario \n5. participar en conversacion grupal \n6. salir ")
                    opcion = input("opcion a elegir es: ")
                    if opcion == "1":
                        #codigo para mostrar usuarios
                    if opcion == "2":
                        #codigo para agregar contanto
                    if opcion == "3":
                        #codigo para mostrar detalles de un contanto
                    if opcion == "4":
                        #codigo para iniciar conversacion 1 a 1 con otro usuario
                    if opcion == "5":
                        #codigo para añadirme a un chat grupal
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
            xmpp = RegisterBot(userJID, password)

            # Some servers don't advertise support for inband registration, even
            # though they allow it. If this applies to your server, use:
            xmpp['xep_0077'].force_registration = True
            xmpp.register_plugin('xep_0030') # Service Discovery
            xmpp.register_plugin('xep_0004') # Data forms
            xmpp.register_plugin('xep_0066') # Out-of-band Data
            xmpp.register_plugin('xep_0077') # In-band Registration
            if xmpp.connect():
                xmpp.process(block=True)
            else:
                print("Unable to connect.")
            xmpp.disconnect()
        if eleccion == '3':
            st_log = True
        if eleccion != '1' or eleccion != '2' or eleccion '3':
            print("Por favor, solo elija el numero de las opciones que se le ha proporcionado sin dejar espacios\n")

