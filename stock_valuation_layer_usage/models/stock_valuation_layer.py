# 2020 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# @author Jordi Ballester <jordi.ballester@forgeflow.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    usage_ids = fields.One2many(
        comodel_name="stock.valuation.layer.usage",
        inverse_name="stock_valuation_layer_id",
        string="Valuation Usage",
        help="Trace on what stock moves has the stock valuation been used in, "
        "including the quantities taken.",
    )

    incoming_usage_ids = fields.Many2many(
        comodel_name="stock.valuation.layer.usage",
        string="Incoming usages",
        compute="_compute_incoming_usages",
    )

    incoming_usage_quantity = fields.Float(
        string="Incoming Usage quantity",
        compute="_compute_incoming_usages",
    )

    def _compute_incoming_usages(self):
        for rec in self:
            incoming_usages = self.env["stock.valuation.layer.usage"].search(
                [
                    ("stock_move_id", "=", rec.stock_move_id.id),
                ]
            )
            rec.incoming_usage_ids = incoming_usages.ids
            rec.incoming_usage_quantity = sum(incoming_usages.mapped("quantity"))

    usage_quantity = fields.Float(
        string="Usage quantity",
        compute="_compute_usage_values",
        store=True,
    )
    usage_value = fields.Float(
        string="Usage value",
        compute="_compute_usage_values",
        store=True,
    )

    @api.depends(
        "usage_ids.quantity",
        "usage_ids.value",
    )
    def _compute_usage_values(self):
        for rec in self:
            rec.usage_quantity = sum(rec.usage_ids.mapped("quantity"))
            rec.usage_value = sum(rec.usage_ids.mapped("value"))
