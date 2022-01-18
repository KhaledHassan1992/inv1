# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

{
    'name': "EgyMentors Electronic Invoice",
    'author': 'EgyMentors, Ahmed Salama',
    'category': 'Accounting',
    'summary': """Electronic Invoice""",
    'website': 'http://www.egymentors.com',
    'license': 'AGPL-3',
    'description': """
""",
    'version': '10.1',
    'depends': ['account', 'product', 'account_accountant'],
    'data': [
        'data/tax_type_sub_type_data.xml',
        
        'security/ir.model.access.csv',
        'security/e_invoice_security.xml',
        
        'views/product_template_view_changes.xml',
        'views/res_company_view_changes.xml',
        'views/res_partner_view_changes.xml',
        'views/account_move_view_changes.xml',
        'wizard/electronic_invoice_result_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
