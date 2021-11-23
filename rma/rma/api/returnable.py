# - 
# Copyright 2021 Jide Olayinka
# for license information ...

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.utils.data import add_days, today
    

GLOBAL_MAIN_SERIES = 'RMM-VCH-.YYYY.-'
GLOBAL_RETURN_SERIES = 'RMM-RET-.YYYY.-'

### make rma EC Due Date cannot be before Posting / Supplier Invoice Date
@frappe.whitelist()
def update_invoice(doc, method):
    '''
    invoice_doc.save()
    return_against: doc
    Main Entry
    REC Entry
    '''
    if(doc.entry_type == "REC Entry" ):
        # it is auto invoice by our rma
        # therefore trap it
        return
    else:
        ###RMA
        if(doc.is_return):
            #print(f'got here for returns \n\n\n')
            #check if paid : life-time or subscription 
            # if freemium return
            print(f'\n Only paid subscription \n')
            #rma_return_submit_invoice(doc)
        else:
            #print(f'got here for main sales \n\n')
            # freemium pass
            rma_main_submit_invoice (doc)

#  Direct Sales
#def rma_main_submit_invoice(data):
def rma_main_submit_invoice (data):
    """begin here"""
    
    voucher_items = ""
    for x in data.items:
        voucher_items +="\'"+ x.item_code+"\',"
    ec_list = []
    replace_ec_list = []
    item_ec_list = []
    ec_remover_list = []
    ''' get the Ec of invoice items that has Ec'''
    items_data = frappe.db.sql(
        """ 
        SELECT
            name AS item_code,
            item_name,
            idx as idx,
            standard_rate,
            main_hrec_tag
        FROM
            `tabItem`
        WHERE
            disabled = 0
            AND is_sales_item = 1
            AND is_fixed_asset = 0
            AND is_rec = 1
            AND main_hrec_tag IN ({0})
        """.format(
            voucher_items[: -1]
        ),
        as_dict=1,
    )

    if (len(items_data)<= 0):
        return

    for x in items_data:
        ec_list.append(x.main_hrec_tag)
        replace_ec_list.append({"tag":x.main_hrec_tag, "code":x.item_code, "rate":x.standard_rate})
    '''modified invoice item list'''
    indexitm = 0
    for vch_item in data.items:
        if vch_item.item_code in ec_list:
            indexitm = ec_list.index(vch_item.item_code)
            ec_remover_list.append({
                "item_code": replace_ec_list[indexitm]["code"],
                "qty": vch_item.qty,
                "rate": replace_ec_list[indexitm]["rate"],
                "uom": vch_item.uom,
                "amount": vch_item.qty * replace_ec_list[indexitm]["rate"],
                "conversion_factor": vch_item.conversion_factor,
                "poi_ec":vch_item.poi_ec,
            })
        else:
            if(vch_item.poi_ec == 1):
                item_ec_list.append({
                    "item_code": vch_item.item_code,
                    "qty": vch_item.qty,
                    "rate": vch_item.rate,
                    "uom": vch_item.uom,
                    "amount": vch_item.qty * vch_item.rate,
                    "conversion_factor": vch_item.conversion_factor,
                    "poi_ec":vch_item.poi_ec,
                })
    ###remove paid EC
    print(f'get first count or leght {len(item_ec_list)} \n\n\n')
    if (len(ec_remover_list) <= 0):
        return

    for rc in item_ec_list:
        for d in ec_remover_list:
            if d['item_code'] == rc['item_code']:
                d['qty'] = d['qty'] - rc['qty']
                d['amount'] = d['qty'] * d['rate']
    
    ## get Totals (qty and amount)
    nqty = 0
    nsum = 0
    print(f'get the length or count {len(ec_remover_list)} \n\n\n ')
    for cal in ec_remover_list:
        nqty += cal['qty']
        nsum += cal['amount']
    
    invoice_doc = frappe.new_doc("Sales Invoice")
    invoice_doc.update({
        "is_pos": 0, "doc.ignore_pricing_rule" : 1, "total" : nsum, "total_qty": nqty,
        "company": data.company, "currency": data.currency ,
        "customer":data.customer, "naming_series" :  "RMM-VCH-.YYYY.-", 
        "set_posting_time":1, "due_date": add_days(data.posting_date, 1), "posting_date": data.posting_date,
        "update_stock":1, "set_warehouse": data.set_warehouse, "set_target_warehouse": data.set_target_warehouse,
        "items": ec_remover_list,
    })

    ## invoice_doc.items = ec_remover_list
    invoice_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    invoice_doc.ignore_pricing_rule = 1
    invoice_doc.entry_type = "REC Entry"
    invoice_doc.set_missing_values()

    invoice_doc.save()
    invoice_doc.submit()
    #return invoice_doc
    ##print(f'\n\n\n\nMain Entry: \n {doc.total},{doc.posting_date}\n {doc.due_date}, {doc.name} \n\n')

  
def rma_return_submit_invoice (data):
    """begin here"""
    
    voucher_items = ""
    for x in data.items:
        voucher_items +="\'"+ x.item_code+"\',"
    ec_list = []
    replace_ec_list = []
    item_ec_list = []
    ec_remover_list = []
    ''' get the Ec of invoice items that has Ec'''
    items_data = frappe.db.sql(
        """ 
        SELECT
            name AS item_code,
            item_name,
            idx as idx,
            standard_rate,
            main_hrec_tag
        FROM
            `tabItem`
        WHERE
            disabled = 0
            AND is_sales_item = 1
            AND is_fixed_asset = 0
            AND is_rec = 1
            AND main_hrec_tag IN ({0})
        """.format(
            voucher_items[: -1]
        ),
        as_dict=1,
    )

    print(f'am inside: {len(items_data)} ')
    if (len(items_data) <= 0):
        return

    for x in items_data:
        ec_list.append(x.main_hrec_tag)
        replace_ec_list.append({"tag":x.main_hrec_tag, "code":x.item_code, "rate":x.standard_rate})
    '''modified invoice item list'''
    indexitm = 0
    for vch_item in data.items:
        if vch_item.item_code in ec_list:
            indexitm = ec_list.index(vch_item.item_code)
            ec_remover_list.append({
                "item_code": replace_ec_list[indexitm]["code"],
                "qty": vch_item.qty,
                "rate": replace_ec_list[indexitm]["rate"],
                "uom": vch_item.uom,
                "amount": vch_item.qty * replace_ec_list[indexitm]["rate"],
                "conversion_factor": vch_item.conversion_factor,
                "poi_ec":vch_item.poi_ec,
            })
        else:
            if(vch_item.poi_ec == 1):
                item_ec_list.append({
                    "item_code": vch_item.item_code,
                    "qty": vch_item.qty,
                    "rate": vch_item.rate,
                    "uom": vch_item.uom,
                    "amount": vch_item.qty * vch_item.rate,
                    "conversion_factor": vch_item.conversion_factor,
                    "poi_ec":vch_item.poi_ec,
                })
    ###remove paid EC
   
    
    ## get Totals (qty and amount)
    nqty = 0
    nsum = 0
    print(f'filted out: {len(ec_remover_list)} ')
    if (len(ec_remover_list) <= 0):
        return

    for cal in ec_remover_list:
        nqty -= cal['qty']
        nsum -= cal['amount']
    
    invoice_doc = frappe.new_doc("Sales Invoice")
    invoice_doc.update({
        "is_pos": 0, "doc.ignore_pricing_rule" : 1, "total" : nsum, "total_qty": nqty,
        "company": data.company, "currency": data.currency ,
        "customer":data.customer, "naming_series" : "RMM-RET-.YYYY.-", 
        "set_posting_time":1, "posting_date": data.posting_date,
        "is_return":1, "update_stock":1, "set_warehouse": data.set_warehouse, 
        "set_target_warehouse": data.set_target_warehouse, "items": ec_remover_list,
    })

    invoice_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    invoice_doc.ignore_pricing_rule = 1
    invoice_doc.is_ec_trans = "REC Entry"
    invoice_doc.set_missing_values()

    invoice_doc.save()
    invoice_doc.submit()

