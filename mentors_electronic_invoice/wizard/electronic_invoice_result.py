# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class ElectronicInvoiceResult(models.TransientModel):
	_name = 'electronic.invoice.result'
	_description = "Result of Electronic Invoice Action"
	
	name = fields.Char("Action Name")
	results = fields.Html("Results:")
	line_ids = fields.One2many('electronic.invoice.result.line', 'result_id', "Lines")
	json_details = fields.Html("JSON Details:")


class ElectronicInvoiceResultLines(models.TransientModel):
	_name = 'electronic.invoice.result.line'
	
	result_id = fields.Many2one('electronic.invoice.result', "Result")
	move_id = fields.Many2one('account.move', "Document")
	move_type = fields.Selection(related='move_id.type')
	internalId = fields.Char("Document Ref")
	uuid = fields.Char("UUID")
	line_action = fields.Selection([('success', 'Success'), ('error', 'Error'), ('warning', 'Warning')], "Type")
	description = fields.Html("Description")
	
# Ahmed Salama Code End.
