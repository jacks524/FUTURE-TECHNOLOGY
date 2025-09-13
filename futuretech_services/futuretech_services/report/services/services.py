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

    # Requête SQL pour combiner les données
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
                "width": 120,
                "options": "XAF"
            }
        ]

        return columns, data

    except Exception as e:
        # Gestion des erreurs
        frappe.log_error(f"Erreur dans le rapport: {str(e)}")
        return [
            {"fieldname": "error", "label": "Erreur", "fieldtype": "Data", "width": 200}
        ], [{"error": f"Erreur: {str(e)}"}]