#! /usr/bin/env python3
import kivy
from kivy.app import App
from kivy.uix.label import Label 


class PmakeRecoverGui(App):
	"""docstring for PmakeRecoverGui"""
	def build(self):
		return Label(text='hello world')

gui = PmakeRecoverGui()
gui.run()