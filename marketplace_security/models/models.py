# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    """Product Template multicompany. """
    _inherit = [ 'product.template']
    
    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=False, 
        default=lambda self: self.env.user.company_id ,
        index=1
    )

    def _default_website(self):
        """ Find the first company's website, if there is one. """
        company_id = self.env.company.id

        if self._context.get('default_company_id'):
            company_id = self._context.get('default_company_id')

        domain = [('company_id', '=', company_id)]
        return self.env['website'].search(domain, limit=1)

    website_id = fields.Many2one('website', string="Website", ondelete='restrict', default=_default_website)
