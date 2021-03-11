from odoo import http


class SellerRegistrationController(http.Controller):

    @http.route(['/corporate-registration'], type='http', auth='public',
                website=True, csrf=False, methods=['GET', 'POST'])
    def dti_person_get(self, **kw):
        data = kw

        res_partner = http.request.env['res.partner']
        metodo = http.request.httprequest.method
        sector_list = http.request.env['res.partner.industry'].sudo().search(
            [('active', '=', True)], order="name")

        if metodo == 'GET':
            return http.request.render(
                'g2f_backend.sellers_registration_page_template', {
                    'sector_list': sector_list}
            )

        elif metodo == 'POST':
            sector_ids = http.request.httprequest.form.getlist(
                'sector_id')

            data['sector_id'] = sector_ids

            response = res_partner.sudo().create_seller(data)

            if not response[0]:
                msg1 = """No se pudo registrar el vendedor,
                reporte al administrador"""
                msg2 = response[1]
                return http.request.render(
                    'g2f_backend.warning_sin_contacto_template',
                    {'values': {'msg1': msg1,
                                'msg2': msg2}
                     }
                )

            msg1 = 'Has sido registrado con exito'
            msg2 = 'Sera contactado por un agente'
            return http.request.render(
                'g2f_backend.messageok_page_template',
                {'values': {'msg1': msg1, 'msg2': msg2}})
        else:
            msg1 = 'Solicitud no puede ser procesada.'
            msg2 = 'Reporte el caso al administrador de sistemas: '
            return http.request.render('dti.warning_sin_contacto_template',
                                       {'values':
                                        {'msg1': msg1, 'msg2': msg2}})
