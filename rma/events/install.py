import frappe
from frappe.utils.data import add_days, today
import json
import os
from uuid import uuid4


def before_install():
  
  trials =  add_days(today(), 30) 
  unique_id = str(uuid4())
  

  data = {
    'cuid': unique_id,
    'trial_ends': trials,
    'rma_status': 'freemium',
    'rec_valid_till': trials
  }
  with open(frappe.get_site_path('rmapp.json'), 'w') as outfile:
    json.dump(data, outfile, indent= 2)

  file_path = frappe.utils.get_bench_path() + '/' + \
    frappe.utils.get_site_name(frappe.local.site) + \
      '/rmapp.json'
  
  print('\nfile rmapp.json created at ', file_path, 'with the following settings:')
  for key in data: print("\t{}: {}".format(key, data[key]))
  print('\nChange the values in rmapp.json to change limits\n')