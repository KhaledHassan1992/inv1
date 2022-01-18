# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.addons.mentors_electronic_invoice.models.res_company_changes import CLASSIFICATIONS
# Ahmed Salama Code Start ---->


class ResPartnerInherit(models.Model):
	_inherit = 'res.partner'
	
	classification = fields.Selection(CLASSIFICATIONS, "Classification", default='P',
	                                  help="Type of customer {'P':'Personal', 'B':'Business', 'F':'Foreigner'}")
	# Address Details
	floor = fields.Char("Floor")
	room = fields.Char("Room")
	landmark = fields.Char("Landmark")
	additional_info = fields.Char("Additional Info.")

# Ahmed Salama Code End.
