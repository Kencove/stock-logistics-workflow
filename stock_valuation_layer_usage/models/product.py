# 2020 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# @author Jordi Ballester <jordi.ballester@forgeflow.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _run_fifo_prepare_candidate_update(
        self,
        candidate,
        qty_taken_on_candidate,
        value_taken_on_candidate,
        candidate_vals,
    ):
        candidate_vals = super(ProductProduct, self)._run_fifo_prepare_candidate_update(
            candidate, qty_taken_on_candidate, value_taken_on_candidate, candidate_vals
        )
        move_id = self.env.context.get("used_in_move_id", False)
        out_layer = self.env["stock.valuation.layer"].search(
            [
                ("stock_move_id", "=", move_id),
            ],
            limit=1,
        )
        self.env["stock.valuation.layer.usage"].sudo().create(
            {
                "stock_valuation_layer_id": candidate.id,
                "dest_stock_valuation_layer_id": out_layer.id,
                "stock_move_id": move_id,
                "quantity": qty_taken_on_candidate,
                "value": value_taken_on_candidate,
                "company_id": candidate.company_id.id,
            }
        )
        return candidate_vals

    def _run_fifo_vacuum_prepare_candidate_update(
        self,
        svl_to_vacuum,
        candidate,
        qty_taken_on_candidate,
        value_taken_on_candidate,
        candidate_vals,
    ):
        candidate_vals = super(
            ProductProduct, self
        )._run_fifo_vacuum_prepare_candidate_update(
            svl_to_vacuum,
            candidate,
            qty_taken_on_candidate,
            value_taken_on_candidate,
            candidate_vals,
        )
        move_id = (
            svl_to_vacuum.stock_move_id and svl_to_vacuum.stock_move_id.id or False
        )
        out_layer = self.env["stock.valuation.layer"].search(
            [
                ("stock_move_id", "=", move_id),
            ],
            limit=1,
        )
        if svl_to_vacuum:
            self.env["stock.valuation.layer.usage"].sudo().create(
                {
                    "stock_valuation_layer_id": candidate.id,
                    "dest_stock_valuation_layer_id": out_layer.id,
                    "stock_move_id": move_id,
                    "quantity": qty_taken_on_candidate,
                    "value": value_taken_on_candidate,
                    "company_id": candidate.company_id.id,
                }
            )
        return candidate_vals

    def _get_candidates_domain(self, company):
        res = super()._get_candidates_domain(company)
        reserved_from = self.env.context.get("reserved_from", False)
        reserved_from_moves = self.env["stock.move"]
        if reserved_from:
            reserved_from_moves = self.env["stock.move"].browse(reserved_from)
        in_moves = reserved_from_moves._get_in_moves()
        if in_moves:
            # The layer out has reserved an incoming move,
            # we search among those
            res = expression.AND([res, [("stock_move_id", "in", in_moves.ids)]])
        return res
