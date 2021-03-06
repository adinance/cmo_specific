# -*- coding: utf-8 -*-
from openerp import models, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def proforma_voucher(self):
        res = super(AccountVoucher, self).proforma_voucher()
        # Update to use same OU
        for rec in self:
            invoices = rec.line_ids.mapped('invoice_id')
            ou = invoices.mapped('operating_unit_id')
            if len(invoices) == len(ou) == 1:
                rec.move_id.line_id.write({'operating_unit_id': ou.id})
            else:
                # Case no 1 OU found, try to get it again from move line
                user_ou = self.env.user.default_operating_unit_id
                for line in rec.move_id.line_id:
                    if line.reconcile_id or line.reconcile_partial_id:
                        ml = line.reconcile_id.line_id or \
                            line.reconcile_partial_id.line_partial_ids
                        ou = ml.filtered(lambda l:
                                         l.operating_unit_id != user_ou).\
                            mapped('operating_unit_id')
                        if ou:
                            line.operating_unit_id = ou[0]
                        else:
                            line.operating_unit_id = user_ou
                    else:
                        line.operating_unit_id = user_ou
        return res
