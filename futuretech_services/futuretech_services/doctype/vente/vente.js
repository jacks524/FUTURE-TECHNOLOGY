frappe.ui.form.on('Vente', {
    // Calculer le total quand la quantité change
    quantite: function(frm) {
        calculate_total(frm);
    },
    
    // Calculer le total quand le prix unitaire change
    prix_unitaire: function(frm) {
        calculate_total(frm);
    },
    
    // Validation avant sauvegarde
    before_save: function(frm) {
        calculate_total(frm);
    }
});

function calculate_total(frm) {
    let quantite = frm.doc.quantite || 0;
    let prix_unitaire = frm.doc.prix_unitaire || 0;
    let total = quantite * prix_unitaire;
    
    frm.set_value('total', total);
}