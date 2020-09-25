#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Universidad Del valle de Guatemala
Redes
Josue David Lopez Florian 17081

Codigo e implementacion gracias a los examples de : https://github.com/poezio/slixmpp
Slixmpp Credits
Maintainers:
Florent Le Coz (louiz@louiz.org),
Mathieu Pasquet (mathieui@mathieui.net),
'''

import sys
import logging
import getpass
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
#aqui tenemos el codigo que permite al sys poder detectar la plataforma que esta siendo usada pra ejecutar  los DNDs de Asyncrio
#esto permite evitar el error de loop que aparece si no se pone estas 2 lineas
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#esta es la clase encargada de registrar a los usuarios en el server
class RegisterBot(slixmpp.ClientXMPP):

    def __init__(self, jid, password):
        #se realiza el log in
        slixmpp.ClientXMPP.__init__(self, jid, password)
        #se ejecuta los handlers que manejaran los procesos de forma asyncrona
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)
    #funcion principal que hace trigger al evento llamado  por process
    async def start(self, event):

        self.send_presence()
        await self.get_roster()
        self.disconnect()
    #aqui esta la funcion encargada de ingresar a los usuarios
    async def register(self, iq):
        #aqui se creo el iq stanza para poder mandar al nuevo usuario que sera ingresado al server pasando sus parametros
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        #se procede a tratar de registrar al usuario
        try:
            await resp.send()
            #en caso todo salga bien, obtendremos este mensaje
            print("Account created for %s!" % self.boundjid)
        except IqError as e:
            #en caso exista algun error en registrar al usuario o ya exista, saldra este mensaje de error
            print("Could not register account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            #esto ocurrira en caso el server no este levantado o no se halla podido conectar por alguna razon en especifico
            print("No response from server.")
            self.disconnect()
        self.disconnect()
#Client es la clase principal encargada de los funcionamientas del usuario registrado
#aqui mismo se tienen la segunda parte de las funcionalidades pedidas para este proyecto
class Client(slixmpp.ClientXMPP):

    def __init__(self, user, passw):
        #nos logeamos
        slixmpp.ClientXMPP.__init__(self, user, passw)
        #guardamos los parametros que necesitaremos mas adelante
        self.jid = user
        self.password = passw
        self.room = ""
        self.nick = ""
        #definimos todos los handlers encargado de ejecutar las funciones que requerimos para llevar ciertas funciones del cliente
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("changed_status", self.wait_for_presences)
        self.add_event_handler("groupchat_message", self.muc_message)
        self.add_event_handler("message", self.message)
        #definimos los pluging que posee slixmpp para poder realizar varios de los funcionamientos del protocolo
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0045') # Multi-User Chat
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping
        
        #definimos nuestro reciver y los precense que ejecutaran por eventos asincronos
        self.received = set()
        self.presences_received = asyncio.Event()
    #nuestra funcion para mandar mensajes a un chat grupal
    def muc_message(self, msg):

        if msg['mucnick'] != self.nick and self.nick in msg['body']:
            self.send_message(mto=msg['from'].bare,
                              mbody="I heard that, %s." % msg['mucnick'],
                              mtype='groupchat')
    #esta es la funcion encargada de manejar el chatroom
    def muc_online(self, presence):

        if presence['muc']['nick'] != self.nick:
            self.send_message(mto=presence['from'].bare,
                              mbody="Hello, %s %s" % (presence['muc']['role'],
                                                      presence['muc']['nick']),
                              mtype='groupchat')
    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()

    def wait_for_presences(self, pres):
        """
        Track how many roster entries have received presence updates.
        """
        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()
    #esta es la funcion principal donde se procede a realizar e interactuar con las opciones que ofrece el cliente
    async def start(self, event):
        self.send_presence()
        #await self.get_roster()
        #formamos
        access = True
        print('se ha conectado\n')
        print("login Listo\n")
        while access:
            #mostramos el menu de opciones disponibles para el usuario
            print("elija una de las siguientes opciones: \n1. Mostrar todos los usuarios y su estado \n2. Agregar un usuario a sus contactos \n3. Mostrar detalles de contacto de un usuario \n4. Comunicacion 1 a 1 con algun usuario \n5. participar en conversacion grupal \n6. mensaje de precencia \n7. salir ")
            opcion = input("opcion a elegir es: ")
            if opcion == "1":
                #codigo para mostrar usuarios
                #tratamos de obtener el roster desde el server, sino se mostraran los mensajes de error que impidieron su optencion
                try:
                    await self.get_roster()
                except IqError as err:
                    print('Error: %s' % err.iq['error']['condition'])
                except IqTimeout:
                    print('Error: Request timed out')
                self.send_presence()
                #se realiza una actualizacion de los presence
                print('Waiting for presence updates...\n')
                await asyncio.sleep(10)
                #aqui se procura el desplegar el roster de contatos en el server
                #consta de varios loops que muestran los distintos detalles de los usuarios
                print('Roster for %s' % self.boundjid.bare)
                groups = self.client_roster.groups()
                for group in groups:
                    print('\n%s' % group)
                    print('-' * 72)
                    for self.jid in groups[group]:
                        sub = self.client_roster[self.jid]['subscription']
                        name = self.client_roster[self.jid]['name']
                        if self.client_roster[self.jid]['name']:
                            print(' %s (%s) [%s]' % (name, self.jid, sub))
                        else:
                            print(' %s [%s]' % (self.jid, sub))

                        connections = self.client_roster.presence(self.jid)
                        for res, pres in connections.items():
                            show = 'available'
                            if pres['show']:
                                show = pres['show']
                            print('   - %s (%s)' % (res, show))
                            if pres['status']:
                                print('       %s' % pres['status'])

                #print("1")
            if opcion == "2":
                #codigo para agregar contanto
                new_friend = (input("user: "))
                xmpp.send_presence_subscription(pto= new_friend + "@redes2020.xyz")
                print("Amigo agregado")
                #print("2")
            if opcion == "3":
                #codigo para mostrar detalles de un contanto
                print("ingrese el nombre sel usuario de quien quiere saber su estatus\n")
                #obtenemos el usario a detallar
                userSt =  input("nombre del usuario: ")
                userSt = userSt + "redes2020.xyz"
                self.send_presence()
                #se procura obtener el roster del cliente para luego mostra los detalles del user
                await self.get_roster()
                self.client_roster
                print("Aqui esta: ", self.client_roster.presence(userSt))
                print("3")
            if opcion == "4":
                #codigo para enviar un mensaje 1 a 1 con otro usuario
                #obtenemos el user al cual va dirigido el mensaje y el mensaje a enviar
                Userto = input("ingrese el nombre el usuario a quien va dirigido el mensaje: ")
                mensaje = input("ingrese el mensaje que desea enviar: ")
                self.send_message(mto= Userto + "@redes2020.xyz",
                          mbody= mensaje,
                          mtype='chat')
                #self.process()
                print("4")
            if opcion == "5":
                #codigo para añadirme a un chat grupal y enviar un mensaje
                print("vamos a ingresar a un room\n")
                #obtenemos el nick con el que quiere aparecer el user en el room y luego generamos la variable room
                self.nick = input("ingrese el nombre con le que quiere aparecer en el room: ")
                self.room = self.nick + "@conference.redes2020.xyz"
                #agregamos un eventhandler para manejar el room y quienes ingresan
                self.add_event_handler("muc::%s::got_online" % self.room,self.muc_online)
                await self.get_roster()
                self.send_presence()
                #se establece la creacio o union al room a traves de este plugin
                self.plugin['xep_0045'].join_muc(self.room,
                                         self.nick,
                                         # If a room password is needed, use:
                                         # password=the_room_password,
                                         wait=True)
                #obtenemos el mensaje y luego llamamos a la funcion que lo mandara a los demas unicos al chat
                mensaje = input("mensaje a enviar: ")
                self.muc_message(mensaje)

                print("5")
            if opcion == "6":
                #codigo para el mensaje de presencia
                #obtenemso los datos requeridos para nuestro mensaje de presence que deseamos tener
                shw = input("Estado(chat, away, xa, dnd): ")
                stts = input("Mensaje: ")
                self.send_presence(pshow= shw, pstatus= stts)
                print("Presence cambiado\n")
            if opcion == "7":
                #codigo que nos saca del loop y del programa
                access = False
                print("entraste")
                # exits the program 
                sys.exit("Se ha desconectado")
                break
            #codigo de progra defensiva en caso se elija una opcion incorrecta
            if opcion != "1" or opcion != "2" or opcion != "3" or opcion != "4" or opcion != "5" or opcion != "6" or opcion != "7": 
                print("ha escrito mala su eleccion. Por favor, intentelo y sin dejar espacios en blanco")
        print("saliste")
        self.disconnect()




if __name__ == '__main__':
    st_log = False
    print("todos los mensajes que pidan el nick o user, requieren solo el nombre. el programa agregara el @redes2020.xyz y @conference.redes2020.xyz")
    while st_log == False:
        print("Bienvenido al chat basado en XMPP \n Por favor elija alguna de las siguientes opcions para empezar: \n 1 - Iniciar sesion \n 2 - Registrarse \n 3 - salir del chat\n")
        eleccion = input("opcion: ")
        if eleccion == '1':
            #codigo para iniciar sesion
            userJID = input("userJID: ")
            password = input("password: ")
            xmpp = Client(userJID + "@redes2020.xyz", password)

            #print(xmpp.connect())
            if xmpp.connect() == None:
                xmpp.process()
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
            #xmpp.process()
            print("usuario creado")
        if eleccion == '3':
            st_log = True
        if eleccion != '1' or eleccion != '2' or eleccion != '3':
            print("Por favor, solo elija el numero de las opciones que se le ha proporcionado sin dejar espacios\n")

