frappe.query_reports["Services"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("Date Début"),
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("Date Fin"),
            "fieldtype": "Date",
            "reqd": 1
        }
    ],
    "onload": function(report) {
        console.log("Rapport chargé avec les filtres:", report.get_values());
    }
};