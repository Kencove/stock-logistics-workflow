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

    def _process_taken_data(self, taken_data, rec):
        usage_model = self.env["stock.valuation.layer.usage"]
        for origin_layer_id in taken_data.keys():
            usage_model.create(
                {
                    "stock_valuation_layer_id": origin_layer_id,
                    "dest_stock_valuation_layer_id": rec.id,
                    "stock_move_id": rec.stock_move_id.id,
                    "quantity": taken_data.get(origin_layer_id).get("quantity", 0.0),
                    "value": taken_data.get(origin_layer_id).get("value", 0.0),
                    "company_id": rec.company_id.id,
                }
            )
        return True

    def create(self, values):
        taken_data = {}
        for val in values:
            taken_data = (
                "taken_data" in val.keys() and val.pop("taken_data") or taken_data
            )
        rec = super(StockValuationLayer, self).create(values)
        self._process_taken_data(taken_data, rec)
        return rec

    def write(self, values):
        res = super(StockValuationLayer, self).write(values)
        for rec in self:
            if self.env.context.get("taken_data"):
                self._process_taken_data(self.env.context.get("taken_data"), rec)
        return res
