# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import exceptions
import base64
import urllib2
from odoo.osv import osv
from openerp.tools import ustr


class PhotoAttach(models.TransientModel):
    """
    This wizard will confirm the all the selected not approved students
    """

    _name = "ems.student.attach"
    _description = "Attach Students Photos"
    
    folder_select = fields.Char()
    
    
    
    
    @api.multi
    def attach_photos(self):
    
       
        
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        image_name = ''
        
        for student in self.env['ems.student'].browse(active_ids):
        
        
            #try:
                #1
            if self.folder_select:
                image_name='http://173.249.57.172:8069/web/static/src/stimages/' + ustr(self.folder_select) + '/' + student.image_num +'.jpg'
                if image_name:
                    image = urllib2.urlopen(image_name).read()
                    img = base64.b64encode(image)
                    student.photo = img
                    
            elif not self.folder_select:
                image_name='http://173.249.57.172:8069/web/static/src/stimages/' + str(student.image_num).zfill(4) +'.jpg'
                if image_name:
                    image = urllib2.urlopen(image_name).read()
                    img = base64.b64encode(image)
                    student.photo = img
                

                    
            # except Exception:
                # if self.folder_select:
                    # image_name='http://173.249.57.172:8069/web/static/src/stimages/' + ustr(self.folder_select) + '/' + student.image_num +'.JPG'
                    # if image_name:
                        # image = urllib2.urlopen(image_name).read()
                        # img = base64.b64encode(image)
                        # student.photo = img
                        
                # elif not self.folder_select:
                    # image_name='http://173.249.57.172:8069/web/static/src/stimages/' + student.image_num +'.JPG'
                    # if image_name:
                        # image = urllib2.urlopen(image_name).read()
                        # img = base64.b64encode(image)
                        # student.photo = img
                        
                        
                        
            # try:
                # #1
                # if self.folder_select:
                    # image_name='http://173.249.57.172:8069/web/static/src/stimages/' + self.folder_select + '/DSC' + student.image_num +'.jpg'
                    # if image_name:
                        # image = urllib2.urlopen(image_name).read()
                        # img = base64.b64encode(image)
                        # student.photo = img
                        
                # elif not self.folder_select:
                    # image_name='http://173.249.57.172:8069/web/static/src/stimages/' + 'DSC' + student.image_num +'.jpg'
                    # if image_name:
                        # image = urllib2.urlopen(image_name).read()
                        # img = base64.b64encode(image)
                        # student.photo = img
                

                    
            # except Exception:
                # if self.folder_select:
                    # image_name='http://173.249.57.172:8069/web/static/src/stimages/' + self.folder_select + '/DSC' + student.image_num +'.JPG'
                    # if image_name:
                        # image = urllib2.urlopen(image_name).read()
                        # img = base64.b64encode(image)
                        # student.photo = img
                        
                # elif not self.folder_select:
                    # image_name='http://173.249.57.172:8069/web/static/src/stimages/' + 'DSC' + student.image_num +'.JPG'
                    # if image_name:
                        # image = urllib2.urlopen(image_name).read()
                        # img = base64.b64encode(image)
                        # student.photo = img

            
                    
                
        return {'type': 'ir.actions.act_window_close'}

