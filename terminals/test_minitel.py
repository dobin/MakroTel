#!/usr/bin/env python
# -*- coding: utf-8 -*-

from terminals.terminal_minitel import Minitel
from components.component_menu import ComponentMenu


minitel = Minitel(device="USB3")

minitel.guess_speed()
minitel.identify()
minitel.set_speed(1200)
minitel.set_mode('VIDEOTEX')
minitel.configure_keyboard(extended = True, cursor = True, lowercase = True)
minitel.echo(False)
minitel.clear()
minitel.cursor(False)

options = [
  'Nouveau',
  'Ouvrir',
  '-',
  'Enregistrer',
  'Enreg. sous...',
  'Rétablir',
  '-',
  'Aperçu',
  'Imprimer...',
  '-',
  'Fermer',
  'Quitter'
]

menu = ComponentMenu(minitel, options, 5, 3)
menu.Initial()
menu.Tick()

minitel.close()