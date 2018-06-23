#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import traceback
from helpers.botComm import *
from helpers.gui import *
from helpers.pedirInfo import *
from helpers.planearViajes import planearViajes
from helpers.signals import setInfoSignal
from helpers.getJson import getCiudad
from helpers.process import forkear
from helpers.varios import addPuntos
from helpers.recursos import getRecursosDisponibles

def menuRutaComercial(s):
	idCiudadOrigen = None
	rutas = []
	while True:
		if idCiudadOrigen is None:
			banner()
			print('Ciudad de origen:')
			idCiudadOrigen = getIdCiudad(s)
			htmlO = s.get(urlCiudad + idCiudadOrigen)
			ciudadO = getCiudad(htmlO)
			max = getRecursosDisponibles(htmlO)
			total = list(map(int, max))
		banner()
		print('Ciudad de destino')
		idCiudadDestino = getIdCiudad(s, ajenas=True)
		if idCiudadOrigen == idCiudadDestino:
			continue
		htmlD = s.get(urlCiudad + idCiudadDestino)
		ciudadD = getCiudad(htmlD)
		idIsla = ciudadD['islandId']
		banner()
		print('Disponible:')
		resto = total
		for ruta in rutas:
			(origen, _, _, md, vn, mr, cr, az) = ruta
			if origen == idCiudadOrigen:
				resto = (resto[0] - md, resto[1] - vn, resto[2] - mr, resto[3] - cr, resto[4] - az)
		print('Madera {} Vino {} Marmol {} Cristal {} Azufre {}'.format(addPuntos(resto[0]), addPuntos(resto[1]), addPuntos(resto[2]), addPuntos(resto[3]), addPuntos(resto[4])))
		print('Enviar:')
		try:
			md = pedirValor(' Madera:', resto[0])
			vn = pedirValor('   Vino:', resto[1])
			mr = pedirValor(' Marmol:', resto[2])
			cr = pedirValor('Cristal:', resto[3])
			az = pedirValor(' Azufre:', resto[4])
		except KeyboardInterrupt:
			idCiudadOrigen = None
			continue
		if md + vn + mr + cr + az == 0:
			idCiudadOrigen = None
			continue
		banner()
		print('Por enviar de {} a {}'.format(ciudadO['cityName'], ciudadD['cityName']))
		enviado = ''
		if md:
			enviado += 'Madera:{} '.format(addPuntos(md))
		if vn:
			enviado += 'Vino:{} '.format(addPuntos(vn))
		if mr:
			enviado += 'Marmol:{} '.format(addPuntos(mr))
		if cr:
			enviado += 'Cristal:{} '.format(addPuntos(cr))
		if az:
			enviado += 'Azufre:{}'.format(addPuntos(az))
		print(enviado)
		print('¿Proceder? [Y/n]')
		rta = read()
		if rta.lower() == 'n':
			idCiudadOrigen = None
		else:
			ruta = (idCiudadOrigen, idCiudadDestino, idIsla, md, vn, mr, cr, az)
			rutas.append(ruta)
			print('¿Realizar otro envio? [y/N]')
			rta = read()
			otroViaje = rta.lower() == 'y'
			if otroViaje is True:
				idCiudadOrigen = None
			else:
				break

	forkear(s)
	if s.padre is True:
		return

	info = '\nRuta comercial\n'
	for ruta in rutas:
		(idciudadOrigen, idCiudadDestino, idIsla, md, vn, mr, cr, az) = ruta
		html = s.get(urlCiudad + idciudadOrigen)
		ciudadO = getCiudad(html)
		html = s.get(urlCiudad + idCiudadDestino)
		ciudadD = getCiudad(html)
		info = info + '{} -> {}\nMadera: {} Vino: {} Marmol: {} Cristal: {} Azufre: {}\n'.format(ciudadO['cityName'], ciudadD['cityName'], addPuntos(md), addPuntos(vn), addPuntos(mr), addPuntos(cr), addPuntos(az))

	setInfoSignal(s, info)
	try:
		planearViajes(s, rutas)
	except:
		if telegramFileValido():
			msg = 'Error en:\n{}\nCausa:\n{}'.format(info, traceback.format_exc())
			sendToBot(s, msg)
	finally:
		s.logout()