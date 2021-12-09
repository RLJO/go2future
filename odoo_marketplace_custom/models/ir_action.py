# -*- coding: utf-8 -*-

from odoo import models
import logging
_logger = logging.getLogger(__name__)

PARTNER_CHILDREN_CONDITION = 'get_partner_children()'
SELLER_CONDITION = 'get_seller()'
CUSTOMER_CONDITION = 'get_customer()'
STOCK_CONDITION = 'get_marketplace_seller_stock()'
SELLER_DOMAIN_STRING = "get_marketplace_seller_id()"


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
                if action_domain and SELLER_CONDITION in action_domain:
                    domain_list = eval(action_domain)
                    index_ids = [index for index, tuple in enumerate(domain_list) if SELLER_CONDITION in str(tuple[2])]
                    update_domain = ''
                    if not user.has_group('odoo_marketplace.marketplace_manager_group'):
                        for index in index_ids:
                            var = domain_list[index][0]
                            if var == 'seller_id.id':
                                ids = user.partner_id.res_partner_children.ids
                                ids.append(user.partner_id.id)
                                update_domain = [('seller_id.id', 'in', ids)]
                    r['domain'] = str(update_domain)
                if action_domain and CUSTOMER_CONDITION in action_domain:
                    domain_list = eval(action_domain)
                    index_ids = [index for index, tuple in enumerate(domain_list) if CUSTOMER_CONDITION in str(tuple[2])]
                    update_domain = ''
                    if not user.has_group('odoo_marketplace.marketplace_manager_group'):
                        for index in index_ids:
                            var = domain_list[index][0]
                            if var == 'partner_id.id':
                                update_domain = [('partner_id.id', 'in', [user.partner_id.id])]
                    r['domain'] = str(update_domain)
                if action_domain and STOCK_CONDITION in action_domain:
                    domain_list = eval(action_domain)
                    index_ids = [index for index, tuple in enumerate(domain_list) if STOCK_CONDITION in str(tuple[2])]
                    update_domain = ''
                    for index in index_ids:
                        var = domain_list[index][0]
                        if var == 'seller_id.id':
                            ids = [user.partner_id.id]
                            if user.partner_id.children_parent_id:
                                ids.append(user.partner_id.children_parent_id.id)
                            update_domain = [('seller_id.id', 'in', ids)]
                    r['domain'] = str(update_domain)
        except Exception as e:
            _logger.info("-----------------%r--------------------", e)
            pass
        return res

    def update_mp_dynamic_domain(self, res):
        if not res:
            return res
        obj_user = self.env.user
        try:
            for r in res:
                mp_dynamic_domain = r.get("domain", [])
                if mp_dynamic_domain and SELLER_DOMAIN_STRING in mp_dynamic_domain:
                    domain_list = eval(mp_dynamic_domain)
                    list_of_index = [index for index, mp_tuple in enumerate(domain_list) if SELLER_DOMAIN_STRING in str(mp_tuple[2])]
                    updated_domain = ""
                    if obj_user.has_group('odoo_marketplace.marketplace_officer_group'):
                        for index in list_of_index:
                            var = domain_list[index][0]
                            if var == "id":
                                domain_list.pop(index)
                            else:
                                domain_list[index] =  (var,'!=', False)
                        updated_domain = str(domain_list)
                    else:
                        seller_id = obj_user.partner_id.id
                        for index in list_of_index:
                            var = domain_list[index][0]
                            if var == "id":
                                r["view_mode"] = "form"
                                r["res_id"] = seller_id
                                r["views"] = [(self.env.ref('odoo_marketplace.wk_seller_form_view').id, "form")]
                            domain_list[index] = (var, 'in', [seller_id, obj_user.children_parent_id.id])
                        updated_domain = str(domain_list)
                    if SELLER_DOMAIN_STRING in (r.get('domain', '[]') or ''):
                        r['domain'] = updated_domain
        except Exception as e:
            _logger.info("~~~~~~~~~~Exception~~~~~~~~%r~~~~~~~~~~~~~~~~~",e)
            pass
        return res

    def read(self, fields=None, load='_classic_read'):
        res = super(IrActionWindow, self).read(fields=fields, load=load)
        return self.update_partner_children_domain(res)
