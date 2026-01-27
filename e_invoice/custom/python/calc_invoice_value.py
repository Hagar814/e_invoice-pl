from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _

def calc_invoice_value(doc, method):
    # Initialize totals
    doc.total_discount = doc.total_item_discount = doc.total_amount = doc.net_total = 0.0

    for d in doc.items:
        # Ensure all required fields have default values
        net_rate = flt(d.net_rate or 0)
        qty = flt(d.qty or 0)
        discount_before = flt(d.discount_before or 0)
        discount_after = flt(d.discount_after or 0)
        base_net_amount = flt(d.base_net_amount or 0)
        base_amount = flt(d.base_amount or 0)
        tax_rate = flt(d.tax_rate or 0)

        # Calculate net amount
        d.net_amount = flt((net_rate * qty) - discount_before, d.precision("net_amount"))

        # Calculate tax amount
        d.tax_amount = flt(base_net_amount * tax_rate / 100, d.precision("tax_amount"))

        # Calculate total amount
        if doc.discount_amount:
            d.total_amount = flt(
                d.tax_amount + base_amount - discount_after, d.precision("total_amount")
            )
            doc.total_amount = flt(doc.total_amount - doc.discount_amount, d.precision("total_amount"))
        else:
            d.total_amount = flt(
                d.tax_amount + base_net_amount - discount_after, d.precision("total_amount")
            )
            doc.total_amount += round(d.total_amount, 2)

        # Update document-level totals
        doc.total_discount += discount_before
        doc.total_item_discount += discount_after
        doc.net_total += d.net_amount

    # Ensure data integrity
    frappe.db.commit()
