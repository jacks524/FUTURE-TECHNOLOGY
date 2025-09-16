import frappe

def execute(filters=None):
    # Debug : Afficher les filtres reçus
    print(f"Filtres reçus: {filters}")

    conditions = ""
    values = {}

    # Gestion des filtres de dates
    if filters:
        if filters.get("from_date") and filters.get("to_date"):
            if filters["from_date"] > filters["to_date"]:
                frappe.throw("La date de début doit être antérieure ou égale à la date de fin.")
        if filters.get("from_date"):
            conditions += " AND date >= %(from_date)s"
            values["from_date"] = filters["from_date"]
        if filters.get("to_date"):
            conditions += " AND date <= %(to_date)s"
            values["to_date"] = filters["to_date"]

    # Requête SQL pour combiner les données de tous les services
    query = f"""
        SELECT 'Impression' as service, SUM(total) as value, date as date_field
        FROM `tabCommande Impression`
        WHERE 1=1 {conditions}
        GROUP BY date
        UNION ALL
        SELECT 'Photographie' as service, SUM(total) as value, date as date_field
        FROM `tabCommande Photographie`
        WHERE 1=1 {conditions}
        GROUP BY date
        UNION ALL
        SELECT 'Secretariat' as service, SUM(total) as value, date as date_field
        FROM `tabSecretariat`
        WHERE 1=1 {conditions}
        GROUP BY date
        UNION ALL
        SELECT 'Vente' as service, SUM(total) as value, date as date_field
        FROM `tabVente`
        WHERE 1=1 {conditions}
        GROUP BY date
        ORDER BY date_field DESC, service ASC
    """

    try:
        # Exécuter la requête SQL
        result = frappe.db.sql(query, values, as_dict=True)

        # Formater les données pour le tableau
        data = []
        for row in result:
            data.append({
                "service": row.service,
                "value": row.value,
                "date_field": row.date_field
            })

        # Définir les colonnes du tableau
        columns = [
            {
                "fieldname": "date_field",
                "label": "Date",
                "fieldtype": "Date",
                "width": 150
            },
            {
                "fieldname": "service",
                "label": "Service",
                "fieldtype": "Data",
                "width": 200
            },
            {
                "fieldname": "value",
                "label": "Revenu",
                "fieldtype": "Currency",
                "width": 150,
                "options": "XAF"
            }
        ]

        # Log pour debug (optionnel)
        # frappe.log_error(f"Rapport généré avec {len(data)} lignes")

        return columns, data

    except Exception as e:
        # Gestion des erreurs
        frappe.log_error(f"Erreur dans le rapport: {str(e)}")
        return [
            {"fieldname": "error", "label": "Erreur", "fieldtype": "Data", "width": 200}
        ], [{"error": f"Erreur: {str(e)}"}]


# Fonction auxiliaire pour obtenir un résumé des ventes
def get_vente_summary(filters=None):
    """
    Fonction pour obtenir un résumé détaillé des ventes
    """
    conditions = ""
    values = {}
    
    if filters:
        if filters.get("from_date"):
            conditions += " AND date >= %(from_date)s"
            values["from_date"] = filters["from_date"]
        if filters.get("to_date"):
            conditions += " AND date <= %(to_date)s"
            values["to_date"] = filters["to_date"]
    
    query = f"""
        SELECT 
            articles,
            SUM(quantite) as total_quantite,
            SUM(total) as total_ventes,
            COUNT(*) as nombre_transactions,
            AVG(prix_unitaire) as prix_moyen
        FROM `tabVente`
        WHERE 1=1 {conditions}
        GROUP BY articles
        ORDER BY total_ventes DESC
    """
    
    try:
        result = frappe.db.sql(query, values, as_dict=True)
        return result
    except Exception as e:
        frappe.log_error(f"Erreur dans get_vente_summary: {str(e)}")
        return []