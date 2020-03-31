# -*- coding: utf-8 -*-
# � 2013 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, exceptions, fields, models
from dateutil.relativedelta import relativedelta
from datetime import datetime

import urlparse
import logging
import uuid

_logger = logging.getLogger(__name__)

class SurveyMailComposeMessage(models.TransientModel):
    _inherit = 'survey.mail.compose.message'
    
    @api.one    
    def action_send_survey_mail_message_slack(self, survey_user_input):
        attachments = [
            {                    
                "title": 'Se ha enviado por email la encuesta automaticamente',
                "text": survey_user_input.survey_id.title,                        
                "color": "#36a64f",
                "fields": [                    
                    {
                        "title": "Cliente",
                        "value": survey_user_input.partner_id.name,
                        'short': True,
                    }                    
                ],                                                                                
            }
        ]    
        
        slack_message_vals = {
            'attachments': attachments,
            'model': 'survey.user_input',
            'res_id': survey_user_input.id,
            'channel': self.env['ir.config_parameter'].sudo().get_param('slack_log_calidad_channel'),                                                         
        }                        
        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)