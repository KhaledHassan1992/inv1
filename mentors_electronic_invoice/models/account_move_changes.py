# -*- coding: utf-8 -*-
import json
import logging
import urllib
from datetime import datetime

import pytz
import requests
import base64
from odoo import models, fields, api, _
from odoo.exceptions import Warning

grey = "\x1b[38;21m"
yellow = "\x1b[33;21m"
red = "\x1b[31;21m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"
green = "\x1b[32m"
blue = "\x1b[34m"
# Ahmed Salama Code Start ---->
_TAX_TYPES = [('T1', 'Value added tax/ضريبه القيمه المضافه'),
              ('T2', 'Table tax (percentage)/ضريبه الجدول (نسبيه)'),
              ('T3', 'Table tax (Fixed Amount)/ضريبه الجدول (النوعية)'),
              ('T4', 'Withholding tax (WHT)/الخصم تحت حساب الضريبه'),
              ('T5', 'Stamping tax (percentage)/ضريبه الدمغه (نسبيه)'),
              ('T6', 'Stamping Tax (amount)/ضريبه الدمغه (قطعيه بمقدار ثابت)'),
              ('T7', 'Entertainment tax/ضريبة الملاهى'),
              ('T8', 'Resource development fee/رسم تنميه الموارد'),
              ('T9', 'Service charges/رسم خدمة'),
              ('T10', 'Municipality Fees/رسم المحليات'),
              ('T11', 'Medical insurance fee/رسم التامين الصحى'),
              ('T12', 'Other fees/رسوم أخرى'),
              ('T13', 'Stamping tax (percentage)(Non-Taxable)/ضريبه الدمغه (نسبيه)'),
              ('T14', 'Stamping Tax (amount)(Non-Taxable)/ضريبه الدمغه (قطعيه بمقدار ثابت)'),
              ('T15', 'Entertainment tax(Non-Taxable)/ضريبة الملاهى'),
              ('T16', 'Resource development(Non-Taxable)/fee	رسم تنميه الموارد'),
              ('T17', 'Service charges(Non-Taxable)/رسم خدمة'),
              ('T18', 'Municipality Fees(Non-Taxable)/رسم المحليات'),
              ('T19', 'Medical insurance fee(Non-Taxable)/رسم التامين الصحى'),
              ('T20', 'Other fees(Non-Taxable)/رسوم أخرى'),
              ]
_SUB_TAX_TYPES = [('T1', 'Export	'),
                  ('T2', 'Export to free areas and other areas	تصدير مناطق حرة وأخرى'),
                  ('T3', 'Exempted good or service	سلعة أو خدمة معفاة'),
                  ('T4', 'A non-taxable good or service	سلعة أو خدمة غير خاضعة للضريبة'),
                  ('T5', 'Stamping tax (percentage)/ضريبه الدمغه (نسبيه)'),
                  ('T6', 'Stamping Tax (amount)/ضريبه الدمغه (قطعيه بمقدار ثابت)'),
                  ('T7', 'Entertainment tax/ضريبة الملاهى'),
                  ('T8', 'Resource development fee/رسم تنميه الموارد'),
                  ('T9', 'Service charges/رسم خدمة'),
                  ('T10', 'Municipality Fees/رسم المحليات'),
                  ('T11', 'Medical insurance fee/رسم التامين الصحى'),
                  ('T12', 'Other fees/رسوم أخرى'),
                  ('T13', 'Stamping tax (percentage)(Non-Taxable)/ضريبه الدمغه (نسبيه)'),
                  ('T14', 'Stamping Tax (amount)(Non-Taxable)/ضريبه الدمغه (قطعيه بمقدار ثابت)'),
                  ('T15', 'Entertainment tax(Non-Taxable)/ضريبة الملاهى'),
                  ('T16', 'Resource development(Non-Taxable)/fee	رسم تنميه الموارد'),
                  ('T17', 'Service charges(Non-Taxable)/رسم خدمة'),
                  ('T18', 'Municipality Fees(Non-Taxable)/رسم المحليات'),
                  ('T19', 'Medical insurance fee(Non-Taxable)/رسم التامين الصحى'),
                  ('T20', 'Other fees(Non-Taxable)/رسوم أخرى'),
                  ]
PROD_UNIT_TYPE = ['2Z', '4K', '4O', 'A87', 'A93', 'A94', 'AMP', 'ANN', 'B22', 'B49', 'B75', 'B78', 'B84', 'BAR', 'BG', \
                  'BO', 'C10', 'C39', 'C41', 'C45', 'C62', 'CA', 'CMK', 'CMQ', 'CMT', 'CS', 'CT', 'CTL', 'D10', 'D33',
                  'D41', 'DAY', 'EA', 'FAR', 'FOT', 'FTK', 'FTQ', 'G42', 'GL', 'GLL', 'GM', 'GRM', 'H63', 'HLT', 'HTZ',
                  'HUR', 'IE', 'INH', 'INK', 'KGM', 'KHZ', 'KMH', 'KMK', 'KMQ', 'KMT', 'KSM', 'KVT', 'KWT', 'LTR', 'M',
                  'MAW', 'MGM', 'MHZ', 'MIN', 'MMK', 'MMQ', 'MMT', 'MON', 'MTK', 'MTQ', 'OHM', 'ONZ', 'PAL', 'PF', 'PK',
                  'SH', 'SMI', 'TNE', 'VLT', 'WEE', 'WTT', 'X03', 'YDQ', 'YRD']
INV_TYP = {'out_invoice': 'I', 'out_refund': 'C'}


class AccountTaxInherit(models.Model):
	_inherit = 'account.tax'
	
	type_code_id = fields.Many2one('account.tax.type.code', "Tax Type Code", required=True,
	                               help="To be used in informing of Egyptian Taxes Foundation.")
	sub_type_code_id = fields.Many2one('account.tax.sub.type.code', "Sub Tax Type Code", required=True,
	                                   domain="[('type_id','=',type_code_id)]",
	                                   help="To be used in informing of Egyptian Taxes Foundation.")


class AccountTaxType(models.Model):
	_name = 'account.tax.type.code'
	_description = "Account Tax Type"
	
	name = fields.Char('Name', required=True)
	code = fields.Char("Code", required=True)
	taxable = fields.Boolean("Taxable", )


class AccountTaxSubType(models.Model):
	_name = 'account.tax.sub.type.code'
	_description = "Account Tax Sub Type"
	
	name = fields.Char('Name', required=True)
	type_id = fields.Many2one('account.tax.type.code', "Type", required=True)
	code = fields.Char("Code", required=True)


class AccountMoveInherit(models.Model):
	_inherit = 'account.move'
	
	@api.onchange('electronic_invoice_uuid', 'electronic_invoice_status')
	def _check_invoice_status(self):
		for invoice in self:
			e_invoice_invalid = e_invoice_valid = hide_sent_button = e_invoice_sent = e_invoice_submitted = False
			if invoice.electronic_invoice_uuid and invoice.type in ('out_invoice', 'out_refund'):
				if invoice.electronic_invoice_status == 'draft':
					e_invoice_sent = True
				elif invoice.electronic_invoice_status == 'Submitted':
					e_invoice_submitted = True
					hide_sent_button = True
				elif invoice.electronic_invoice_status == 'Valid':
					e_invoice_valid = True
					hide_sent_button = True
				elif invoice.electronic_invoice_status == 'Invalid':
					e_invoice_invalid = True
			invoice.e_invoice_submitted = e_invoice_submitted
			invoice.e_invoice_valid = e_invoice_valid
			invoice.hide_sent_button = hide_sent_button
			invoice.e_invoice_sent = e_invoice_sent
			invoice.e_invoice_invalid = e_invoice_invalid
	
	hide_sent_button = fields.Boolean(compute=_check_invoice_status)
	e_invoice_valid = fields.Boolean(compute=_check_invoice_status)
	e_invoice_invalid = fields.Boolean(compute=_check_invoice_status)
	e_invoice_submitted = fields.Boolean(compute=_check_invoice_status)
	e_invoice_sent = fields.Boolean("E-Invoice Informed", copy=False,
	                                help="If checked so the Electronic Invoice is sent")
	e_invoice_json = fields.Text("E_invoice JSON", copy=False)
	e_invoice_canonical = fields.Text("E_invoice Canonical", copy=False)
	electronic_invoice_uuid = fields.Char("E-Invoice ID", readonly=True, copy=False)
	electronic_invoice_url = fields.Char(compute="_compute_e_invoice_url", string="Electronic Invoice", copy=False)
	electronic_invoice_file = fields.Many2one("ir.attachment", "E-Invoice PDF", copy=False)
	electronic_invoice_pdf = fields.Binary("E-Invoice PDF", copy=False)
	invoice_signed = fields.Boolean("Invoice Signed.?", readonly=False, copy=False)
	pdf_name = fields.Char('File Name', copy=False)
	use_static_signature = fields.Boolean("Use Static Sign.?", copy=False)
	static_signature = fields.Text("Static Signature", copy=False)
	static_sign_url = fields.Text("Static Sign URL", copy=False)
	show_results = fields.Boolean('Show Results', copy=False, default=True)
	electronic_invoice_date = fields.Datetime("E-Invoice Date", help="Date of sending E-Invoice,"
	                                                                 " used in validate 72H in case of cancel invoice")
	electronic_invoice_status = fields.Char("E-Invoice Status", help="Status on invoice in Taxes system",
	                                        default='Draft')
	
	@api.onchange('electronic_invoice_uuid')
	def _compute_e_invoice_url(self):
		"""
		Used to generate url for the invoice printed label
		:return:
		"""
		for rec in self:
			electronic_invoice_url = False
			if rec.electronic_invoice_uuid:
				electronic_invoice_url = "https://invoicing.eta.gov.eg/documents/%s" % (
					rec.electronic_invoice_uuid)
			rec.electronic_invoice_url = electronic_invoice_url
	
	def action_send_electronic_invoice(self):
		message = ""
		result_lines = []
		for invoice in self:
			# Generate new token
			access_token, client_id, client_secret, apiBaseUrl = self.env.company.get_access_token()
			self.env.company.taxes_client_token = access_token
			# Assign Headers
			headers = {'Content-Type': "application/json", 'cache-control': "no-cache",
			           'Accept': "application/json", "Accept-Language": "ar",
			           'Authorization': "Bearer %s" % access_token}
			# # Generate Invoice Json
			# invoice_params, canonical, env = invoice.action_generate_json()
			#
			# if env == 'prod':
			# 	if invoice.use_static_signature:
			# 		sign = invoice.static_signature
			# 	else:
			# 		sign = self.env.company.action_sign_document(canonical)
			#
			# 	signatures = [{
			# 		"signatureType": "I",
			# 		"value": sign}]
			# else:
			# 	signatures = [{
			# 		"signatureType": "I",
			# 		"value": ""}]
			# invoice_params['signatures'] = signatures
			if not invoice.e_invoice_json:
				# Generate JSON
				invoice.action_generate_json()
			inv_params = eval(invoice.e_invoice_json)
			if not invoice.invoice_signed:
				if self.env.company.config_type == 'prod':
					invoice.action_sign_invoice()
				else:
					inv_params['signatures'] = [{
						"signatureType": "I",
						"value": ""}]
			req_body = {'documents': [inv_params]}
			submit_url = apiBaseUrl + "/api/v1/documentsubmissions"
			details = json.dumps(req_body, indent=4, ensure_ascii=False).encode('utf8')
			result_json_details = "<b>URL:</b> %s<br/><br/><b>HEADERS:</b> %s <br/><br/><b>CLIENT ID:</b> [%s]<br/><br/>" \
			                      "<b>CLIENT SECRET:</b> [%s]<br/><br/><b>json:</b> %s" \
			                      % (submit_url, headers, client_id, client_secret, details)
			try:
				response = requests.post(url=submit_url, headers=headers, data=details, verify=False)
			except Exception as e:
				message = "Couldn't Connect to %s due to connection error:\n %s" % (submit_url, e)
				logging.info(red + message + reset)
				raise Warning(message)
			if response.status_code == 404:
				message = "Internal error code:1001" \
				          "\n Connecting Egyptian taxes API to submit document respond with error code: [%s]" % response.status_code
				message += "\n\nError Desc.: %s" % response.reason
				raise Warning(_(message))
			elif response.status_code in (200, 202):
				result = response.json()
				logging.info(green + "response: %s" % response + reset)
				logging.info(green + "Result: %s" % result + reset)
				action_name = "Submit Invoice"
				# Extract Results:
				if result.get('acceptedDocuments'):
					message += "<h4 style='color:green'>Success submit of %s Document <h4><br/>" % len(
						result['acceptedDocuments'])
					for accept_detail in result['acceptedDocuments']:
						# Fill Lines of result wizard
						result_lines.append(
							(0, 0, {'move_id': invoice.id, 'internalId': accept_detail.get('internalId'),
							        'uuid': accept_detail['uuid'], 'line_action': 'success'}))
						# Check For Status
						document_status = "Submitted"
						logging.info(yellow + "UUID: %s" % accept_detail['uuid'] + reset)
						# TODO:: This option to auto update is stopped because of 404 that is from non saved uuid on taxes yet
						# status_Value = submitted_invoice._action_get_document('raw', accept_detail['uuid'])
						# logging.info(red + "status_Value: %s" % status_Value + reset)
						# if status_Value:
						# 	document_status = status_Value['status']
						# 	submitted_invoice.action_update_electronic_invoice_pdf()
						# Edit Record
						invoice.write({'electronic_invoice_uuid': accept_detail['uuid'],
						               'e_invoice_sent': True,
						               'electronic_invoice_status': 'Submitted',
						               'electronic_invoice_date': fields.Datetime.now()})
						invoice.message_post(
							body="<b>E-Invoice Sync to Taxes system  accepted with UUID:</b>"
							     "<span  style='color:green'>%s</span?" % accept_detail['uuid'])
				if result.get('rejectedDocuments'):
					message += "<h4 style='color:red'>Errors on submit of %s Document <h4><br/>" % len(
						result['rejectedDocuments'])
					for reject_details in result['rejectedDocuments']:
						
						line_error_desc = ""
						for error in reject_details['error']['details']:
							line_error_desc += "<ul><li><b>Code:</b> %s</li>" % error["code"]
							line_error_desc += "<li><b>Message:</b> %s</li>" % error["message"]
							line_error_desc += "<li><b>Exact field:</b> %s</li></ul>" % error["propertyPath"]
						result_lines.append(
							(0, 0, {'move_id': invoice.id,
							        'internalId': reject_details.get('internalId'),
							        'description': line_error_desc, 'line_action': 'error'}))
						logging.info(red + "\n Invoice %s Rejected" % invoice.display_name + reset)
			else:
				result = response.json()
				message = "Internal error code:1002" \
				          "\n Connecting Egyptian taxes API to submit document respond with error code: [%s]" % response.status_code
				message += "\n\nError Desc.: %s" % response.reason
				message += "\n\nresult: %s" % result
				raise Warning(_(message))
			if invoice.show_results:
				# Return Results in view
				res_id = self.env['electronic.invoice.result'].create({'results': message, 'name': action_name,
				                                                       'line_ids': result_lines,
				                                                       'json_details': result_json_details})
				action = self.env.ref('mentors_electronic_invoice.action_electronic_invoice_result').read()[0]
				action['res_id'] = res_id.id
				return action
		return True
	
	def action_update_electronic_invoice_status(self):
		for invoice in self:
			result = invoice._action_get_document('raw')
			invoice.electronic_invoice_status = result.get('status')
			if invoice.show_results:
				action_name = "Get Document %s Details " % result['internalId']
				validationResults = result.get('validationResults')
				result_lines = []
				if validationResults:
					message = "<h4 style='color:green'>Check Result is: %s<h4><br/>" % validationResults.get('status')
					for accept_detail in validationResults['validationSteps']:
						# Fill Lines of result wizard
						description = "<ul><li><b>Code:</b> %s</li>" % accept_detail["name"]
						description += "<li><b>Status:</b> %s</li>" % accept_detail["status"]
						description += "<li><b>error:</b> %s</li>" % accept_detail["error"]
						description += "</ul>"
						result_lines.append(
							(0, 0, {'internalId': result.get('internalId'), 'description': description,
							        'uuid': result['uuid'],
							        'line_action': 'success' if accept_detail['status'] == 'Valid' else 'error'}))
				else:
					message = result
				# Return Results in view
				res_id = self.env['electronic.invoice.result'].create({'results': message, 'name': action_name,
				                                                       'line_ids': result_lines,
				                                                       'json_details': str(result)})
				action = self.env.ref('mentors_electronic_invoice.action_electronic_invoice_result').read()[0]
				action['res_id'] = res_id.id
				return action
			return True
	
	def action_update_electronic_invoice_pdf(self):
		for invoice in self:
			result = invoice._action_get_document('pdf')
			attachment = invoice._create_attachment('Tax-ETA', result)
			invoice.electronic_invoice_file = attachment
			invoice.electronic_invoice_pdf = attachment.datas
			invoice.pdf_name = attachment.name
	
	def _create_attachment(self, name, datas):
		return self.env['ir.attachment'].sudo().create({
			'name': ("%s-%s" % (self.name, name)).replace('/', '_'),
			'datas': base64.b64encode(datas),
			'mimetype': 'application/x-pdf',
			'type': 'binary',
			'res_model': self._name,
			'res_id': self.id
		})
	
	def _get_personal_details(self, partner, order_total, canonical=''):
		required_fields = ['country_id', 'state_id', 'city', 'street', 'classification', 'street2']
		for field_name in required_fields:
			if not getattr(partner, field_name):
				raise Warning(
					_("Missing one of required details [%s] for partner [%s]" % (field_name, partner.display_name)))
		if partner.classification != 'P' and not partner.vat:
			raise Warning(_("Missing Tax ID for partner [%s]" % partner.display_name))
		elif partner.classification == 'P' and order_total > 50000:
			raise Warning(_("Missing Tax ID (National ID) for partner [%s]" % partner.display_name))
		canonical += '"ADDRESS""COUNTRY""%s""GOVERNATE""%s""REGIONCITY""%s""STREET""%s""BUILDINGNUMBER"' \
		             '"%s""POSTALCODE""%s""FLOOR""%s""ROOM""%s""LANDMARK""%s""ADDITIONALINFORMATION""%s""TYPE""%s"' \
		             % (partner.country_id.code, partner.state_id.display_name, partner.city, partner.street,
		                partner.street2, partner.zip or "12345", partner.floor or "0",
		                partner.room or "0", partner.landmark or "landmark",
		                partner.additional_info or "additionalInformation", partner.classification)
		if partner.vat:
			canonical += '"ID""%s"' % partner.vat
		canonical += '"NAME""%s"' % partner.display_name
		
		return {"address": {"country": partner.country_id.code,
		                    "governate": partner.state_id.display_name,
		                    "regionCity": partner.city,
		                    "street": partner.street,
		                    "buildingNumber": partner.street2,
		                    "postalCode": partner.zip or "12345",  # TODO:: Next is optional
		                    "floor": partner.floor or "0",
		                    "room": partner.room or "0",
		                    "landmark": partner.landmark or "landmark",
		                    "additionalInformation": partner.additional_info or "additionalInformation"
		                    },
		        "type": partner.classification,
		        "id": partner.vat or "",  # 538486562
		        "name": partner.display_name or ""
		        }, canonical
	
	def _get_invoice_lines(self):
		invoice_lines = []
		total_discount = 0.00000
		total_sales_amount = 0.00000
		EGP = self.env.ref('base.EGP')
		invoiceLinesCanonical = '"INVOICELINES"'
		for line in self.invoice_line_ids:
			invoiceLinesCanonical += '"INVOICELINES"'
			amountEGP = line.price_unit if line.price_unit else 1.00
			currencySold = self.env.company.currency_id.name
			amountSold = 0.00
			currencyExchangeRate = 0.00
			total = line.price_total
			if line.currency_id:
				# TODO: NEEDED to be changed
				amountEGP = line.currency_id.compute(line.price_unit, EGP)
				amountSold = line.price_unit if line.price_unit else 1.00
				currencySold = line.currency_id.name
				currencyExchangeRate = 1 / line.currency_id.rate
				total = line.currency_id.compute(line.price_total, EGP)
			price_unit_wo_discount = line.price_unit * (1 - (line.discount / 100.0))
			discount_percentage = line.discount if line.discount else 0.00000
			quantity = line.quantity if line.quantity else 1.000
			sales_total_amount = amountEGP * quantity
			
			discount_amount = (discount_percentage / 100) * sales_total_amount
			
			total_discount += discount_amount
			taxes_res = line.tax_ids._origin.compute_all(price_unit_wo_discount,
			                                             quantity=line.quantity, currency=line.currency_id,
			                                             product=line.product_id,
			                                             partner=line.partner_id)
			total_sales_amount += sales_total_amount
			prd_required_fields = ['hs_code', 'hs_type', 'hs_description']
			for prd_field in prd_required_fields:
				if not getattr(line.product_id, prd_field):
					raise Warning(_("Missing One of required details [%s] for product [%s] !!!" %
					                (prd_field, line.product_id.display_name)))
			if line.product_uom_id.name not in PROD_UNIT_TYPE:
				raise Warning(_("This product uit of measure [%s] not in Tax System unites \n %s" %
				                (line.product_uom_id.name, PROD_UNIT_TYPE)))
			unitType = line.product_uom_id.name or "D41"
			netTotal = sales_total_amount - discount_amount
			invoiceLinesCanonical += '"DESCRIPTION""%s""ITEMTYPE""%s""ITEMCODE""%s""UNITTYPE""%s""QUANTITY""%s"' % \
			                         (line.product_id.hs_description, line.product_id.hs_type,
			                          line.product_id.hs_code, unitType, round(quantity, 5))
			if line.product_id.default_code:
				invoiceLinesCanonical += '"INTERNALCODE""%s"' % line.product_id.default_code
			invoiceLinesCanonical += '"SALESTOTAL""%s""TOTAL""%s""VALUEDIFFERENCE""%s""TOTALTAXABLEFEES""%s""NETTOTAL""%s"' \
			                         % (round(sales_total_amount, 5), round(total, 5), 0.00, 0.00, round(netTotal, 5))
			invoiceLinesCanonical += '"ITEMSDISCOUNT""%s""UNITVALUE""CURRENCYSOLD""%s""AMOUNTSOLD""%s""CURRENCYEXCHANGERATE""%s""AMOUNTEGP""%s"' \
			                         % (0.00, currencySold, amountSold, currencyExchangeRate, round(amountEGP, 5))
			invoiceLinesCanonical += '"DISCOUNT""RATE""%s""AMOUNT""%s"' \
			                         % (round(discount_percentage, 5), round(discount_amount, 5))
			taxableItems, invoiceLinesCanonical = line._get_taxableItems(taxes_res['taxes'], invoiceLinesCanonical)
			
			invoice_lines.append({
				"description": line.product_id.hs_description or '',  # "Computerl"
				"itemType": line.product_id.hs_type,  # "EGS"/"GS1"
				"itemCode": line.product_id.hs_code,  # "EG-113317713-123456"
				"unitType": unitType,
				"quantity": round(quantity, 5),
				"internalCode": line.product_id.default_code or "",  # "ICO"/default_code
				"salesTotal": round(sales_total_amount, 5),  # Total Quantity
				"total": round(total, 5),
				"valueDifference": 0.00,  # TODO::  لازم تبقى 0 دايما (خاصه بالعينات المجانيه)
				"totalTaxableFees": 0.00,  # TODO::  لازم تبقى 0 دايما ومش عارفين السبب
				"netTotal": round(netTotal, 5),
				"itemsDiscount": 0.00,  # TODO::  THIS VALUE NOT USED IN ODOO خصم اضافى على المنتجات كقيمه
				"unitValue": {
					"currencySold": currencySold,  # Currency Code
					"amountSold": round(amountSold, 5),  # amount value in currency
					"currencyExchangeRate": currencyExchangeRate,  # currency Rate
					"amountEGP": round(amountEGP, 5)  # Amount in EGP
				},
				"discount": {  # TODO::  الخصم قبل حساب الضريبه
					"rate": round(discount_percentage, 5),
					"amount": round(discount_amount, 5)},
				"taxableItems": taxableItems,
			})
		return invoice_lines, total_discount, total_sales_amount, invoiceLinesCanonical
	
	def _get_tax_totals(self, tax_lines, canonical):
		taxTotals = []
		canonical += '"TAXTOTALS"'
		if tax_lines:
			for line in tax_lines:
				taxType = line.tax_line_id.type_code_id.code or "T1"
				canonical += '"TAXTOTALS""TAXTYPE""%s""AMOUNT""%s"' % (taxType, round(abs(line.balance), 5))
				taxTotals.append({"taxType": taxType,
				                  "amount": round(abs(line.balance), 5)})
		else:
			taxType = self.env.company.default_type_code_id.code or "T1"
			canonical += '"TAXTOTALS""TAXTYPE""%s""AMOUNT""%s"' % (taxType, 0.00)
			taxTotals.append({"taxType": taxType,
			                  "amount": 0.00})
		return taxTotals, canonical
	
	def _action_get_document(self, endpoint):
		access_token, client_id, client_secret, apiBaseUrl = self.env.company.get_access_token()
		headers = {'Content-Type': "application/json", 'cache-control': "no-cache",
		           'Accept': "application/json", "Accept-Language": "ar",
		           'Authorization': "Bearer %s" % access_token}
		get_details_url = apiBaseUrl + "/api/v1/documents/%s/%s" % (self.electronic_invoice_uuid, endpoint)
		logging.info(yellow + "get_details_url: %s" % get_details_url + reset)
		try:
			response = requests.get(url=get_details_url, headers=headers, verify=False)
		except Exception as e:
			message = "Couldn't Connect to %s due to connection error:\n %s" % (get_details_url, e)
			logging.info(red + message + reset)
			raise Warning(message)
		logging.info(green + "response: %s" % response + reset)
		if response.status_code == 404:
			message = "Connecting Egyptian taxes API to get document respond with error code: [%s]" % response.status_code
			message += "\n\nURL.: %s" % get_details_url
			message += "\n\nError Desc.: %s" % response.reason
			raise Warning(_(message))
		elif response.status_code in (200, 202):
			result = response
			if endpoint == 'raw':
				result = response.json()
				logging.info(green + "Result: %s" % result + reset)
			elif endpoint == 'pdf':
				result = response.content
			return result
		else:
			result = response.json()
			message = "Connecting Egyptian taxes API to Cancel document respond with error code: [%s]" % response.status_code
			message += "\n\nError Desc.: %s" % response.reason
			message += "\n\nURL: %s" % get_details_url
			message += "\n\nDetails: %s" % result
			raise Warning(_(message))
	
	def get_static_sign_url(self):
		for invoice in self:
			signature = False
			if self.env.company.signature_tool == 'python':
				if not invoice.e_invoice_canonical:
					invoice_json, data, env = invoice.action_generate_json()
				static_sign_url = "%s" % self.env.company.signature_url
				# static_sign_url = "%s?" % self.env.company.signature_url
				if self.env.company.signature_pin:
					static_sign_url += "?user_pin=%s" % self.env.company.signature_pin
				if self.env.company.signature_label:
					if not self.env.company.signature_pin:
						static_sign_url += "?token_label=%s" % self.env.company.signature_label
					else:
						static_sign_url += "&token_label=%s" % self.env.company.signature_label
				invoice.static_sign_url = static_sign_url
				try:
					# response = requests.get(static_sign_url).content
					response = requests.post(url=static_sign_url, data={'data': invoice.e_invoice_canonical}).content
					response = eval(response)
				except Exception as e:
					message = "Couldn't Connect to %s due to connection error:\n %s" % (static_sign_url, e)
					logging.info(red + message + reset)
					raise Warning(message)
				if isinstance(response, dict):
					signature = response.get('value')
			elif self.env.company.signature_tool == 'c#':
				req_body = eval(invoice.e_invoice_json)
				invoice_params = json.dumps(req_body, indent=4, ensure_ascii=False).encode('utf8')
				headers = {'Content-Type': "application/json"}
				try:
					serialized = requests.post(url=self.env.company.signature_serializer,
					                           data=invoice_params, headers=headers).content
				except Exception as e:
					message = "Couldn't Connect to %s due to connection error:\n %s" % (
					self.env.company.signature_serializer, e)
					logging.info(red + message + reset)
					raise Warning(message)
				logging.info(green + "serialized: %s" % serialized + reset)
				try:
					hashed = requests.post(url=self.env.company.signature_hash, data=serialized,
					                       headers=headers).content
				except Exception as e:
					message = "Couldn't Connect to %s due to connection error:\n %s" % (
					self.env.company.signature_hash, e)
					logging.info(red + message + reset)
					raise Warning(message)
				invoice.e_invoice_canonical = serialized
				signature = hashed
			invoice.static_signature = signature
	
	def action_generate_json(self):
		env = self.env.company.config_type
		if not env:
			raise Warning(
				_("You must select Platform ENVIRONMENT in company %s first." % self.env.company.display_name))
		if env == 'prod':
			api_version = "1.0"
		else:
			api_version = "0.9"
		invoice_time = datetime.combine(self.invoice_date, datetime.min.time())
		invoice_lines, totalDiscountAmount, totalSalesAmount, invoiceLinesCanonical = self._get_invoice_lines()
		netAmount = (totalSalesAmount - totalDiscountAmount)
		tax_lines = self.line_ids.filtered(lambda l: l.tax_line_id and l.tax_line_id.type_code_id)
		totalAmount = self.amount_total
		invoice_time = invoice_time.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
		taxpayerActivityCode = self.env.company.taxpayer_activity_code or "1061"
		canonical = '"ISSUER"'
		issuer, canonical = self._get_personal_details(self.env.company.partner_id, totalSalesAmount, canonical)
		canonical += '"BRANCHID""0""RECEIVER"'
		issuer["address"]["branchID"] = "0"
		receiver, canonical = self._get_personal_details(self.partner_id, totalSalesAmount, canonical)
		internal_id = self.name.replace("/", "")
		canonical += '"DOCUMENTTYPE""%s""DOCUMENTTYPEVERSION""%s""DATETIMEISSUED""%s""TAXPAYERACTIVITYCODE""%s"' \
		             '"INTERNALID""%s"' % \
		             (INV_TYP[self.type], api_version, invoice_time, taxpayerActivityCode, internal_id)
		canonical += invoiceLinesCanonical
		canonical += '"TOTALDISCOUNTAMOUNT""%s""TOTALSALESAMOUNT""%s""NETAMOUNT""%s"' % \
		             (round(totalDiscountAmount, 5), round(totalSalesAmount, 5), round(netAmount, 5))
		tax_totals_lines, canonical = self._get_tax_totals(tax_lines, canonical)
		canonical += '"TOTALAMOUNT""%s""EXTRADISCOUNTAMOUNT""%s""TOTALITEMSDISCOUNTAMOUNT""%s"' % \
		             (round(totalAmount, 5), 0.00, 0.00)
		invoice_params = {
			"issuer": issuer,
			"receiver": receiver,
			"documentType": INV_TYP[self.type],  # "I/C/D"
			"documentTypeVersion": api_version,
			"dateTimeIssued": invoice_time,
			"taxpayerActivityCode": taxpayerActivityCode,
			"internalID": internal_id,  # "IID1"
			# TODO: ADD Payment
			"invoiceLines": invoice_lines,
			"totalDiscountAmount": round(totalDiscountAmount, 5),
			"totalSalesAmount": round(totalSalesAmount, 5),
			"netAmount": round(netAmount, 5),
			"taxTotals": tax_totals_lines,
			"totalAmount": round(totalAmount, 5),
			"extraDiscountAmount": 0.00,  # TODO::  THIS VALUE NOT USED IN ODOO
			# الخصم الإضافى بعد حساب الضريبه(لاتؤثر على الضريبه نهائى)
			"totalItemsDiscountAmount": 0.00,  # TODO::  لازم تبقى 0 دايما ومش عارفين السبب
			# "signatures": signatures
		}
		self.e_invoice_json = str(invoice_params).encode('utf-8')
		self.e_invoice_canonical = str(canonical).encode('utf-8')
		self.invoice_signed = False
		return invoice_params, canonical, env
	
	def action_sign_invoice(self):
		if not self.e_invoice_json or not self.e_invoice_canonical:
			invoice_params, canonical, env = self.action_generate_json()
		else:
			invoice_params = eval(self.e_invoice_json)
		if not self.static_signature:
			self.get_static_sign_url()
		invoice_params['signatures'] = [{
			"signatureType": "I",
			"value": self.static_signature}]
		self.e_invoice_json = invoice_params
		self.invoice_signed = True


class AccountMoveLineInherit(models.Model):
	_inherit = 'account.move.line'
	
	def _get_taxableItems(self, taxes_res, invoiceLinesCanonical=''):
		"""
		Compute taxable lines
		:param taxes_res:
		:return: taxableItems
		"""
		tax_obj = self.env['account.tax']
		taxableItems = []
		EGP = self.env.ref('base.EGP')
		invoiceLinesCanonical += '"TAXABLEITEMS"'
		if taxes_res:
			for tax_line in taxes_res:
				tax = tax_obj.browse(tax_line['id'])
				amount = abs(tax_line['amount'])
				if self.currency_id:
					# TODO: NEEDED to be changed
					amount = self.currency_id.compute(amount, EGP)
				taxType = tax.type_code_id.code or self.env.company.default_type_code_id.code
				subType = tax.sub_type_code_id.code or self.env.company.default_sub_type_code_id.code
				rate = abs(tax.amount)
				invoiceLinesCanonical += '"TAXABLEITEMS""TAXTYPE""%s""AMOUNT""%s""SUBTYPE""%s""RATE""%s"' % \
				                         (taxType, round(amount, 5), subType, round(rate, 5))
				taxableItems.append({
					"taxType": taxType,
					"amount": round(amount, 5),
					"subType": subType,
					"rate": round(rate, 5)
				})
		else:
			invoiceLinesCanonical += '"TAXABLEITEMS""TAXTYPE""%s""AMOUNT""%s""SUBTYPE""%s""RATE""%s"' % \
			                         (self.env.company.default_type_code_id.code, 0.00,
			                          self.env.company.default_sub_type_code_id.code, 0.00)
			taxableItems = [{"taxType": self.env.company.default_type_code_id.code,
			                 "amount": 0.00,
			                 "subType": self.env.company.default_sub_type_code_id.code,
			                 "rate": 0.00}]
		return taxableItems, invoiceLinesCanonical

# Ahmed Salama Code End.
