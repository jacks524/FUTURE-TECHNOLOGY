import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class CommandeImpression(Document):
    def validate(self):
        self.total = (self.prix_unitaire or 0) * (self.quantite or 0)

    def on_submit(self):
        """Créer automatiquement une Sales Invoice lors de la soumission"""
        self.create_sales_invoice()

    def create_sales_invoice(self):
        """Génération de la facture liée à la commande"""

        # Vérifier si une facture existe déjà pour cette commande
        existing_invoice = frappe.get_all(
            "Sales Invoice",
            filters={"commande_impression": self.name}  # nécessite un champ custom
        )
        if existing_invoice:
            return  # Ne pas créer de doublon

        # Données de la facture
        invoice_data = {
            "doctype": "Sales Invoice",
            "customer": self.client,   # ⚠️ assure-toi que `client` est bien un champ Link → Customer
            "posting_date": nowdate(),
            "due_date": nowdate(),
            "items": [
                {
                    "item_name": self.type_d_impression,  # ou item_code si tu utilises les Items ERPNext
                    "qty": self.quantite,
                    "rate": self.prix_unitaire,
                    "amount": self.total,
                }
            ],
            # ⚠️ Champ personnalisé à créer dans Sales Invoice (Link vers Commande Impression)
            "commande_impression": self.name
        }

        # Création et soumission de la facture
        invoice = frappe.get_doc(invoice_data)
        invoice.insert(ignore_permissions=True)
        invoice.submit()

        frappe.msgprint(f"✅ Sales Invoice <b>{invoice.name}</b> créée pour la commande <b>{self.name}</b>")
