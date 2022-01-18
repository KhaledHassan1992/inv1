# -*- coding: utf-8 -*-
import logging

import requests

from odoo import models, fields, _, api
from odoo.exceptions import Warning
import json
import os

grey = "\x1b[38;21m"
yellow = "\x1b[33;21m"
red = "\x1b[31;21m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"
green = "\x1b[32m"
blue = "\x1b[34m"

# Ahmed Salama Code Start ---->
CLASSIFICATIONS = [('P', 'Personal'), ('B', 'Business'), ('F', 'Foreigner')]
METHODS = [('GET-/api/v1.0/documenttypes', 'Get Document Types'),
           # ('PUT-/notifications/documents', 'Receive Document Notifications'),
           ('POST-/api/v1/documentsubmissions', 'Submit Documents')]
ENV = {'uat': '../data/EEI - UAT Env.postman_environment.json',  # 'UAT/PREPROD',
       'sit': '../data/EEI - SIT Env.postman_environment.json',  # 'SIT',
       'prod': '../data/EEI - PRD Env.postman_environment.json'}  # 'PRODUCTION'


class ResCompanyInherit(models.Model):
	_inherit = 'res.company'
	
	client_id = fields.Char("Client ID")
	client_secret = fields.Char("Client Secret")
	config_type = fields.Selection([('uat', 'UAT/PREPROD'),
	                                ('sit', 'SIT'),
	                                ('prod', 'PRODUCTION')], required=True,
	                               string='ENVIRONMENT Platform', default="uat",
	                               help="Test environment of the solution (SIT and UAT/PreProd environments) depends on"
	                                    " internally issued certificates. Therefore to be able to properly use either the"
	                                    " Invoicing Portal or get to APIs that solution is exposing,"
	                                    " first you need to configure trust of Root Certificate of the test environment"
	                                    " in your own test and development environments")
	method = fields.Selection(METHODS, "Method")
	taxpayer_activity_code = fields.Char("Taxpayer Activity Code", required=True, default="1061")
	default_type_code_id = fields.Many2one('account.tax.type.code', "Default Tax Type", required=True,
	                                       help="To be used in informing of Egyptian Taxes Foundation.")
	default_sub_type_code_id = fields.Many2one('account.tax.sub.type.code', "Default Sub Tax Type", required=True,
	                                           domain="[('type_id','=',default_type_code_id)]",
	                                           help="To be used in informing of Egyptian Taxes Foundation.")
	signature_tool = fields.Selection([('python', 'Python'), ('c#', 'C#')],
	                                  "Signature Tool", default='c#')
	signature_url = fields.Char("Signature URL(Method1)", default='http://0.0.0.0:5001/sign')
	# Case of hosting http://localhost:PROJ_NAME/api/InvoiceHasher/Serialize
	signature_serializer = fields.Char("Signature Serializer",
	                                   default='http://localhost:5000/api/InvoiceHasher/Serialize')
	signature_hash = fields.Char("Signature Harsh", default='http://localhost:5000/api/InvoiceHasher/Hash')
	signature_pin = fields.Char("Signature PIN")
	signature_label = fields.Char("Signature Label", default="Egypt Trust")
	
	def test_call_e_invoice_api(self):
		message = ""
		if not self.method:
			raise Warning(_("Please select method first to test with"))
		access_token, client_id, client_secret, apiBaseUrl = self.get_access_token()
		message += "Token Success for Client ID: %s\n Secret: %s" % (client_id, client_secret)
		headers = {'Content-Type': "application/json", 'cache-control': "no-cache",
		           'Accept': "application/json", "Accept-Language": "ar", 'Authorization': "Bearer %s" % access_token}
		api_detail = self.method.split('-')
		url = apiBaseUrl + api_detail[1]
		method = api_detail[0]
		message += "URL: %s\n\nMETHOD: %s\n\nHEADERS: %s\n\n" % (url, method, headers)
		if method == "GET":
			try:
				response = requests.request(method=method, url=url, headers=headers, verify=False)
			except Exception as e:
				message = "Could Connect to %s due to connection error:\n %s" % (url, e)
				logging.info(red + message + reset)
				raise Warning(message)
		elif method == "POST":
			with open(os.path.join(os.path.dirname(__file__), '../data/api_example.json'), 'r') as f:
				details = json.dumps(json.load(f), indent=4)
				try:
					response = requests.request(method=method, url=url, headers=headers, data=details, verify=False)
				except Exception as e:
					message = "Could Connect to %s due to connection error:\n %s" % (url, e)
					logging.info(red + message + reset)
					raise Warning(message)
				message += "DATA:%s\n\n" % details
		message += "Response Status :%s Reason: %s\n\n" % (response.status_code, response.reason)
		raise Warning(message)
	
	def get_access_token(self):
		with open(os.path.join(os.path.dirname(__file__), ENV[self.config_type]), 'r') as f:
			distros_dict = json.load(f)
		idSrvBaseUrl = distros_dict['values'][1]['value']
		apiBaseUrl = distros_dict['values'][0]['value']
		token_url = idSrvBaseUrl + "/connect/token"
		
		client_id = self.client_id
		client_secret = self.client_secret
		if not client_id and not client_secret:
			client_id = distros_dict['values'][2]['value']
			client_secret = distros_dict['values'][3]['value']
		headers = {'content-type': "application/x-www-form-urlencoded", 'cache-control': "no-cache"}
		payload = {
			'grant_type': 'client_credentials',
			'client_id': client_id,
			'client_secret': client_secret,
			'scope': 'InvoicingAPI',
		}
		try:
			response = requests.post(token_url, headers=headers, data=payload, verify=False)
		except Exception as e:
			message = "Could Connect to %s due to connection error:\n %s" % (token_url, e)
			logging.info(red + message + reset)
			raise Warning(message)
		result = False
		if response.status_code != 404:
			result = response.json()
		if response.status_code == 200:
			logging.info(green + "Token Respond: %s" % result + reset)
			access_token = result['access_token']
			return access_token, client_id, client_secret, apiBaseUrl
		else:
			result = response.json()
			message = "Connecting Egyptian taxes API to get Access token respond with error code:%s" % response.status_code
			message += "\n\nError Desc.: %s %s" % (response.reason, result and result['error'] or "")
			if self.env.user.has_group('base.group_no_one') and self.env.user.has_group('base.group_system'):
				message += " \n URL:%s \n\n HEADERS:%s\n\n Client Key: [%s]\n Client Secret [%s]" % \
				           (token_url, headers, client_id, client_secret)
			raise Warning(_(message))
	
# Ahmed Salama Code End.
