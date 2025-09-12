# Copyright (c) 2025, none and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class Secretariat(Document):
    def before_save(self):
        # Calcul automatique du total
        self.total = (self.prix_unitaire or 0) * (self.quantite or 0)

    def on_submit(self):
        # Créer automatiquement une Sales Invoice
        self.create_sales_invoice()

    def create_sales_invoice(self):
        # Vérifier si une facture existe déjà pour cette commande
        existing_invoice = frappe.get_all(
            "Sales Invoice",
            filters={"secretariat": self.name}
        )
        if existing_invoice:
            return  # Ne pas créer une double facture

        invoice_data = {
            "doctype": "Sales Invoice",
            "customer": self.client,  # Champ client de CommandePhotographie
            "posting_date": nowdate(),
            "due_date": nowdate(),
            "items": [
                {
                    "item_name": self.type_commande,  # ou item_code si tu as un Item
                    "qty": self.quantite,
                    "rate": self.prix_unitaire,
                    "amount": self.total,
                }
            ],
            # ⚠️ Ce champ doit exister dans Sales Invoice (via Custom Field)
            "secretariat": self.name  
        }

        invoice = frappe.get_doc(invoice_data)
        invoice.insert(ignore_permissions=True)
        invoice.submit()

        frappe.msgprint(f"Sales Invoice {invoice.name} créée pour la commande {self.name}")

