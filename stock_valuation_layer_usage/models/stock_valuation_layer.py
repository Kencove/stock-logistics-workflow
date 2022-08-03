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
    incoming_usage_ids = fields.One2many(
        comodel_name="stock.valuation.layer.usage",
        inverse_name="dest_stock_valuation_layer_id",
        string="Incoming Valuation Usage",
        help="Trace on what stock moves has the stock valuation been used in, "
        "including the quantities taken.",
    )

    incoming_usage_quantity = fields.Float(
        string="Incoming Usage quantity",
        compute="_compute_incoming_usages",
        store=True,
    )
    incoming_usage_value = fields.Float(
        string="Incoming Usage value",
        compute="_compute_incoming_usages",
        store=True,
    )

    @api.depends(
        "incoming_usage_ids.quantity",
        "incoming_usage_ids.value",
    )
    def _compute_incoming_usages(self):
        for rec in self:
            rec.incoming_usage_quantity = sum(rec.incoming_usage_ids.mapped("quantity"))
            rec.incoming_usage_value = sum(rec.incoming_usage_ids.mapped("value"))

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
