# Copyright (c) 2021, Gross Innovatives and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

from dateutil.parser import parse
import frappe
from frappe.model.document import Document
import json
import subprocess

class ReturnableSetting(Document):
	#pass
	@frappe.whitelist()
	def get_info(self):
		#print(f'\n\n\n\n\n\n\n\n was called \n\n\n\n\n\n\n\n')
		feed = {}
		with open(frappe.get_site_path('rmapp.json')) as jsonfile:
			parsed = json.load(jsonfile)
		
		for key, value in parsed.items():
			feed[key] = value

		for key, value in feed.items():
			self.db_set(key, value) 
