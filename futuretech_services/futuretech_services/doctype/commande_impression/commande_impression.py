import frappe
from frappe.model.document import Document

class CommandeImpression(Document):
    def before_save(self):
        # Calcul automatique du total
        self.total = (self.prix_unitaire or 0) * (self.quantite or 0)

    def on_submit(self):
        # Créer automatiquement une Sales Invoice
        self.create_sales_invoice()

    def create_sales_invoice(self):
        # Vérifier si une facture existe déjà pour cette commande
        existing_invoice = frappe.get_all("Sales Invoice", filters={"commande_impression": self.name})
        if existing_invoice:
            return  # Ne pas créer une double facture

        invoice_data = {
            "doctype": "Sales Invoice",
            "customer": self.client,  # Champ client de Commande Impression
            "posting_date": frappe.utils.nowdate(),
            "due_date": frappe.utils.nowdate(),
            "items": [
                {
                    "item_name": self.type_d_impression,  # Nom de l'article
                    "qty": self.quantite,
                    "rate": self.prix_unitaire,
                    "amount": self.total,
                }
            ],
            "commande_impression": self.name  # Champ lien personnalisé à créer sur Sales Invoice
        }

        invoice = frappe.get_doc(invoice_data)
        invoice.insert()
        invoice.submit()
        frappe.msgprint(f"Sales Invoice {invoice.name} créée pour la commande {self.name}")
