import frappe
import json
import os
from frappe.model.naming import parse_naming_series


#def before_install(): after_install

def after_install ():
    """auto add naming series for sales and sales return"""
    # doctype is naming_series
