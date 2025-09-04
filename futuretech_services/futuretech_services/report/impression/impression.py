import frappe

def execute(filters=None):
    columns = [
        {"label": "Période", "fieldname": "periode", "fieldtype": "Data", "width": 200},
        {"label": "Total Revenus (FCFA)", "fieldname": "revenus", "fieldtype": "Currency", "width": 200},
    ]

    data = []

    # Revenus journaliers
    daily = frappe.db.sql("""
        SELECT SUM(total)
        FROM `tabCommande Impression`
        WHERE DATE(creation) = CURDATE()
    """)[0][0] or 0
    data.append({"periode": "Aujourd'hui", "revenus": daily})

    # Revenus hebdomadaires
    weekly = frappe.db.sql("""
        SELECT SUM(total)
        FROM `tabCommande Impression`
        WHERE YEARWEEK(DATE(creation), 1) = YEARWEEK(CURDATE(), 1)
    """)[0][0] or 0
    data.append({"periode": "Cette Semaine", "revenus": weekly})

    # Revenus mensuels
    monthly = frappe.db.sql("""
        SELECT SUM(total)
        FROM `tabCommande Impression`
        WHERE MONTH(DATE(creation)) = MONTH(CURDATE())
          AND YEAR(DATE(creation)) = YEAR(CURDATE())
    """)[0][0] or 0
    data.append({"periode": "Ce Mois", "revenus": monthly})

    # Revenus annuels
    yearly = frappe.db.sql("""
        SELECT SUM(total)
        FROM `tabCommande Impression`
        WHERE YEAR(DATE(creation)) = YEAR(CURDATE())
    """)[0][0] or 0
    data.append({"periode": "Cette Année", "revenus": yearly})

    return columns, data
