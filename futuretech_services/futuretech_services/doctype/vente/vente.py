# Copyright (c) 2025, none and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, flt


class Vente(Document):
    def validate(self):
        # Calcul automatique du total
        self.total = flt(self.prix_unitaire or 0) * flt(self.quantite or 0)
        
        # Validation de base
        if self.quantite and self.quantite <= 0:
            frappe.throw("La quantité doit être supérieure à 0")
        
        if self.prix_unitaire and self.prix_unitaire <= 0:
            frappe.throw("Le prix unitaire doit être supérieur à 0")

    def on_submit(self):
        # Créer automatiquement une Sales Invoice
        self.create_sales_invoice()

    def create_sales_invoice(self):
        # Vérifier si une facture existe déjà pour cette vente
        existing_invoice = frappe.get_all(
            "Sales Invoice",
            filters={"vente_reference": self.name},  # Vous devrez créer ce champ custom
            limit=1
        )
        
        if existing_invoice:
            frappe.msgprint(f"Une facture existe déjà pour cette vente : {existing_invoice[0].name}")
            return

        # Vérifier si le client existe dans Customer
        customer = self.get_or_create_customer()

        invoice_data = {
            "doctype": "Sales Invoice",
            "customer": customer,
            "posting_date": self.date or nowdate(),
            "due_date": self.date or nowdate(),
            "items": [
                {
                    "item_name": self.articles,  # Correspond au champ de votre DocType
                    "description": f"{self.articles} - {self.note or ''}",
                    "qty": self.quantite or 1,
                    "rate": self.prix_unitaire or 0,
                    "amount": self.total or 0,
                }
            ],
            # Champ custom pour lier à la vente (à créer dans Sales Invoice)
            "vente_reference": self.name,
            "remarks": f"Facture générée automatiquement pour la vente {self.name}"
        }

        try:
            invoice = frappe.get_doc(invoice_data)
            invoice.insert(ignore_permissions=True)
            invoice.submit()
            
            frappe.msgprint(f"Sales Invoice {invoice.name} créée avec succès pour la vente {self.name}")
            
            # Optionnel : mettre à jour un champ de statut dans Vente
            self.db_set("sales_invoice", invoice.name, update_modified=False)
            
        except Exception as e:
            frappe.log_error(f"Erreur lors de la création de la facture pour {self.name}: {str(e)}")
            frappe.throw(f"Impossible de créer la facture : {str(e)}")

    def get_or_create_customer(self):
        """
        Vérifie si le client existe, sinon le crée automatiquement
        """
        if not self.client:
            frappe.throw("Le nom du client est requis")
            
        # Vérifier si le client existe déjà
        existing_customer = frappe.get_all(
            "Customer",
            filters={"customer_name": self.client},
            limit=1
        )
        
        if existing_customer:
            return existing_customer[0].name
        
        # Créer un nouveau client
        try:
            customer_doc = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": self.client,
                "customer_type": "Individual",
                "customer_group": "Individual"  # Groupe par défaut
            })
            customer_doc.insert(ignore_permissions=True)
            frappe.msgprint(f"Client '{self.client}' créé automatiquement")
            return customer_doc.name
            
        except Exception as e:
            frappe.log_error(f"Erreur création client {self.client}: {str(e)}")
            frappe.throw(f"Impossible de créer le client : {str(e)}")

    def before_cancel(self):
        """
        Logique à exécuter avant l'annulation de la vente
        """
        # Vérifier s'il y a une facture liée
        if hasattr(self, 'sales_invoice') and self.sales_invoice:
            frappe.throw("Impossible d'annuler cette vente car une facture est déjà générée. Annulez d'abord la facture.")