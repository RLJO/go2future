# -*- coding: utf-8 -*-

from odoo import models
import logging
_logger = logging.getLogger(__name__)

PARTNER_CHILDREN_CONDITION = 'get_partner_children()'

class IrActionWindow(models.Model):
    _inherit = 'ir.actions.act_window'

    def update_partner_children_domain(self, res):
        if not res:
            return res
        user = self.env.user
        try:
            for r in res:
                action_domain = r.get('domain', [])
                if action_domain and PARTNER_CHILDREN_CONDITION in action_domain:
                    domain_list = eval(action_domain)
                    index_ids = [index for index, tuple in enumerate(domain_list) if PARTNER_CHILDREN_CONDITION in str(tuple[2])]
                    update_domain  = ''
                    for index in index_ids:
                        var = domain_list[index][0]
                        if var == 'children_parent_id.id':
                            update_domain = [('children_parent_id.id', 'in', [user.partner_id.id])]
                    r['domain'] = str(update_domain)
        except Exception as e:
            _logger.info("-----------------%r--------------------", e)
            pass
        return res


    def read(self, fields=None, load='_classic_read'):
        res = super(IrActionWindow, self).read(fields=fields, load=load)
        return self.update_partner_children_domain(res)