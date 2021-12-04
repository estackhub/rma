// Copyright (c) 2021, Gross Innovatives and contributors
// For license information, please see license.txt

frappe.ui.form.on('Returnable Setting', {
	
	onload_post_render: function (frm){
		frm.disable_save();
		frm.call('get_info').then( r => {
			frm.refresh();
		})
	}
});
