from . import models


def uninstall_hook(env):
    """Remove uploaded CSVs; never change restored purchase business records."""
    env['ir.attachment'].sudo().search([
        ('res_model', 'in', [
            'ppg.purchase.packaging.restore.job',
            'ppg.purchase.packaging.restore.line',
        ]),
    ]).unlink()
