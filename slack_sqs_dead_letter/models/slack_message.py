# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

import boto3, json
from botocore.exceptions import ClientError

class SlackMessage(models.Model):
    _inherit = 'slack.message'        
    
    @api.multi    
    def cron_slack_sqs_dead_letter(self, cr=None, uid=False, context=None):
        slack_log_sqs_dead_letter = self.env['ir.config_parameter'].sudo().get_param('slack_log_sqs_dead_letter')
        ses_sqs_urls = self.env['ir.config_parameter'].sudo().get_param('sqs_dead_letter_urls').split(',')
        AWS_ACCESS_KEY_ID = tools.config.get('aws_access_key_id')        
        AWS_SECRET_ACCESS_KEY = tools.config.get('aws_secret_key_id')
        AWS_SMS_REGION_NAME = tools.config.get('aws_region_name')
        #sqs
        sqs = boto3.client(
            'sqs',
            region_name=AWS_SMS_REGION_NAME, 
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key= AWS_SECRET_ACCESS_KEY
        )
        #operations
        for ses_sqs_url in ses_sqs_urls:                                            
            # Receive message from SQS queue
            total_messages = 10
            while total_messages>0:
                response = sqs.receive_message(
                    QueueUrl=ses_sqs_url,
                    AttributeNames=['All'],
                    MaxNumberOfMessages=10,
                    MessageAttributeNames=['All']
                )
                if 'Messages' in response:
                    total_messages = len(response['Messages'])
                else:
                    total_messages = 0
                #operations
                if 'Messages' in response:
                    for message in response['Messages']:                                
                        message_body = json.loads(message['Body'])
                        #slack_message
                        attachments = [
                            {                    
                                "title": ses_sqs_url,
                                "text": message['Body'],
                                "color": "#ff0000"                                               
                            }
                        ]                        
                        slack_message_vals = {
                            'attachments': attachments,
                            'channel': slack_log_sqs_dead_letter,                                                         
                        }                        
                        slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)                