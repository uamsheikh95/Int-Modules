# -*- coding: utf-8 -*-

import re
import calendar
from datetime import datetime
from odoo import models, fields, api
from odoo.modules import get_module_resource
from odoo.exceptions import except_orm
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

try:
    from odoo.tools import image_colorize, image_resize_image_big
except:
    image_colorize = False
    image_resize_image_big = False

class City(models.Model):

    _name = 'ems.city'
    
    name = fields.Char('City Name', required=True)
    code = fields.Char('Code', required=True)
    
    
    # _sql_constraints = [
        # ('city_code_unique', 'unique(code)', 'The code number must me unique'),
    # ]
    
    
    
class Stream(models.Model):

    _name = 'ems.stream'
    
    name = fields.Char('Stream', required=True)
    
class Elective(models.Model):

    _name = 'ems.elective'
    
    name = fields.Char('Elective', required=True)
    
class Medium(models.Model):

    _name = 'ems.medium'
    
    name = fields.Char('Medium', required=True)

    
class Student(models.Model):
    ''' Defining a student information '''
    _name = 'ems.student'
    _order= 'roll_no asc'
    _table = "ems_student"
    _description = 'Student Information'
    
    
    
    @api.multi
    @api.depends('date_of_birth')
    def _compute_student_age(self):
        '''Method to calculate student age'''
        current_dt = datetime.today()
        for rec in self:
            if rec.date_of_birth:
                start = datetime.strptime(rec.date_of_birth,
                                          DEFAULT_SERVER_DATE_FORMAT)
                age_calc = ((current_dt - start).days / 365)
                # Age should be greater than 0
                if age_calc > 0.0:
                    rec.age = age_calc

    @api.constrains('date_of_birth')
    def check_age(self):
        '''Method to check age should be greater than 5'''
        current_dt = datetime.today()
        if self.date_of_birth:
            start = datetime.strptime(self.date_of_birth,
                                      DEFAULT_SERVER_DATE_FORMAT)
            age_calc = ((current_dt - start).days / 365)
            # Check if age less than 5 years
            if age_calc < 5:
                raise ValidationError('''Age of student should be greater
                than 5 years!''')
    

    @api.constrains('image_num')
    def check_image_num(self):
        if self.image_num:
            if not self.image_num.isdigit():
                raise ValidationError('''Image number must contain numbers only!''')

            
    @api.model
    def check_current_year(self):
        '''Method to get default value of logged in Student'''
        res = self.env['ems.year'].search([('current', '=',
                                                 True)])
        if not res:
            raise ValidationError('''There is no current Academic Year
                                    defined!Please contact to Administator!'''
                                    )
        return res.id
        
        
    #@api.model
    #def check_current_student(self):
    #	'''Method to get default value of logged in Student'''
    #	res = self.env['ems.school'].search([('com_name', '=',
    #											 'SMART PRIMARY SCHOOL')])
        
    #	return res.id
        
        

        

    
                             
    name = fields.Char('Student Name', required=True)
    mother_name = fields.Char('Mother Name', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                              'Gender')
    
    image_num = fields.Char('Image Number', store=True)
    
    tel = fields.Char('Tel')
    photo = fields.Binary('Photo')
    
    state = fields.Selection([('to_approve', 'Waiting to Approve'),
                              ('approved', 'Approved')],
                             'Status', readonly=True, default="to_approve")
    
    
    date_of_birth = fields.Date('BirthDate')
    place_of_birth = fields.Char('Place of Birth', required=True)
    age = fields.Integer(string='Age',
                         readonly=True)
                         
    year_of_birth = fields.Integer('Birth Year', required=True)
                         
    reg_date = fields.Date('Registeration Date', default=datetime.today())
    
    country = fields.Many2one('res.country', 'Country')
    region = fields.Many2one('res.country.state', 'State', related='school_id.region', store=True)
    city = fields.Many2one('ems.city', 'City', related='school_id.city', store=True)
    
    #school_id = fields.Many2one('ems.school', 'School')
    
    school_id = fields.Many2one('ems.school', 'School')
    
    year = fields.Many2one('ems.year', 'Academic Year', readonly=True,
                           default=check_current_year)
    
    roll_no = fields.Char('Roll No.')
    
    
    school_type = fields.Selection([('primary', 'Primary'), ('secondary', 'Secondary')], 'Grade',  related='school_id.school_type', store=True)
    
    pid = fields.Char('Student ID', required=True,
                      default=lambda self: ('New'),
                      help='Personal IDentification Number')
    cmp_id = fields.Many2one('res.company', 'Company Name',
                              store=True, default=lambda self: self.env.user.company_id )
                             
    stream = fields.Selection([('general', 'General'), ('science', 'Science'), ('art', 'Art')], 'Stream')
    elective = fields.Selection([('none', 'None'), ('business', 'Business'), ('agriculture', 'Agriculture')], 'Elective')
    medium = fields.Selection([('arabic', 'Arabic'), ('english', 'English'), ('somali', 'Somali')], 'Medium')
    
    
    
    
    @api.model
    def create(self, vals):
        '''Method to create sequence'''
        seq = self.env['ir.sequence'].next_by_code('ems.student') or '/'
        vals['pid'] = seq
        res = super(Student, self).create(vals)
        return res
        
    @api.multi
    def approve(self):
        '''Method to confirm admission'''
                
        self.write({'state': 'approved',})
        return True
            


    
    _sql_constraints = [
        ('image_num_unique', 'unique(image_num)', 'The image number must me unique'),
    ]
    
    
    
    
    
class School(models.Model):
    ''' Defining School Information '''
    _name = 'ems.school'
    _inherits = {'res.company': 'company_id'}
    _description = 'School Information'
    _rec_name = "com_name"
    _order = "com_name"

    company_id = fields.Many2one('res.company', 'Company',
                                 ondelete="cascade",
                                 required=True)
    com_name = fields.Char('School Name', related='company_id.name',
                           store=True)
    code = fields.Char('Code', required=True)
    
    school_type = fields.Selection([('primary', 'Primary School'),
                              ('secondary', 'Secondary School')],
                             'School Type')
    
    country = fields.Many2one('res.country', 'Country')
    region = fields.Many2one('res.country.state', 'Region')
    city = fields.Many2one('ems.city', 'City')
    
    version = fields.Selection([('arabic', 'Arabic'), ('somali', 'Somali'), ('english', 'English')], 'School Version')
    male_total = fields.Integer('Male', compute ='count_male_and_female')
    
    female_total = fields.Integer('Female', compute = 'count_male_and_female')
    
    total = fields.Integer('Total', compute = 'count_total')
    
    _sql_constraints = [
        ('school_name_unique', 'unique(com_name)', 'The school name must me unique'),
    ]
    
    
    
    @api.one
    def count_male_and_female(self):
        student=self.env['ems.student']
        
        male_count = student.search(['&',('state', '=', 'approved'), ('school_id', '=', self.id), ('gender', '=', 'male')])
        self.male_total=len(male_count)
        
        female_count = student.search(['&',('state', '=', 'approved'), ('school_id', '=', self.id), ('gender', '=', 'female')])
        self.female_total=len(female_count)
    
    
    @api.one
    @api.depends('male_total', 'female_total')
    def count_total(self):
        if self.male_total or self.female_total:
            self.total = self.male_total + self.female_total
    
    

class Subject(models.Model):
    '''Defining a subject '''
    _name = "ems.subject"
    _description = "Subjects"

    name = fields.Char('Name', required=True)
    maximum_marks = fields.Integer("Maximum marks")
    minimum_marks = fields.Integer("Minimum marks")
    
class Year(models.Model):
    ''' Defines an academic year '''
    _name = "ems.year"
    _description = "Academic Year"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True,
                              help="Sequence order you want to see this year.")
    name = fields.Char('Name', required=True, help='Name of academic year')
    code = fields.Char('Code', required=True, help='Code of academic year')
    date_start = fields.Date('Start Date', required=True,
                             help='Starting date of academic year')
    date_stop = fields.Date('End Date', required=True,
                            help='Ending of academic year')
    month_ids = fields.One2many('ems.month', 'year_id', 'Months',
                                help="related Academic months")
    current = fields.Boolean('Current', help="Set Active Current Year")
    description = fields.Text('Description')

    @api.model
    def next_year(self, sequence):
        '''This method assign sequence to years'''
        year_id = self.search([('sequence', '>', sequence)], order='id',
                              limit=1)
        if year_id:
            return year_id.id
        return False

    @api.multi
    def name_get(self):
        '''Method to display name and code'''
        return [(rec.id, rec.name) for rec in self]

    @api.multi
    def generate_academicmonth(self):
        interval = 1
        month_obj = self.env['ems.month']
        for data in self:
            ds = datetime.strptime(data.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d') < data.date_stop:
                de = ds + relativedelta(months=interval, days=-1)
                if de.strftime('%Y-%m-%d') > data.date_stop:
                    de = datetime.strptime(data.date_stop, '%Y-%m-%d')
                month_obj.create({
                    'name': ds.strftime('%B'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'year_id': data.id,
                })
                ds = ds + relativedelta(months=interval)
        return True

    @api.constrains('date_start', 'date_stop')
    def _check_academic_year(self):
        '''Method to check start date should be greater than end date
           also check that dates are not overlapped with existing academic
           year'''
        new_start_date = datetime.strptime(self.date_start, '%Y-%m-%d')
        new_stop_date = datetime.strptime(self.date_stop, '%Y-%m-%d')
        delta = new_stop_date - new_start_date
        if delta.days > 365 and not calendar.isleap(new_start_date.year):
            raise ValidationError('''Error! The duration of the academic year
                                      is invalid.''')
        if (self.date_stop and self.date_start and
                self.date_stop < self.date_start):
            raise ValidationError('''The start date of the academic year'
                                      should be less than end date.''')
        for old_ac in self.search([('id', 'not in', self.ids)]):
            # Check start date should be less than stop date
            if (old_ac.date_start <= self.date_start <= old_ac.date_stop or
                    old_ac.date_start <= self.date_stop <= old_ac.date_stop):
                raise ValidationError('''Error! You cannot define overlapping
                                          academic years.''')
        return True

    @api.constrains('current')
    def check_current_year(self):
        check_year = self.search([('current', '=', True)])
        if len(check_year.ids) >= 2:
            raise ValidationError('''Error! You cannot set two current
            year active!''')
            
            
class Month(models.Model):
    ''' Defining a month of an academic year '''
    _name = "ems.month"
    _description = "Academic Month"
    _order = "date_start"

    name = fields.Char('Name', required=True, help='Name of Academic month')
    code = fields.Char('Code', required=True, help='Code of Academic month')
    date_start = fields.Date('Start of Period', required=True,
                             help='Starting of academic month')
    date_stop = fields.Date('End of Period', required=True,
                            help='Ending of academic month')
    year_id = fields.Many2one('ems.year', 'Academic Year', required=True,
                              help="Related academic year ")
    description = fields.Text('Description')

    _sql_constraints = [
        ('month_unique', 'unique(date_start, date_stop, year_id)',
         'Academic Month should be unique!'),
    ]

    @api.constrains('date_start', 'date_stop')
    def _check_duration(self):
        '''Method to check duration of date'''
        if (self.date_stop and self.date_start and
                self.date_stop < self.date_start):
            raise ValidationError(''' End of Period date should be greater
                                    than Start of Peroid Date!''')

    @api.constrains('year_id', 'date_start', 'date_stop')
    def _check_year_limit(self):
        '''Method to check year limit'''
        if self.year_id and self.date_start and self.date_stop:
            if (self.year_id.date_stop < self.date_stop or
                    self.year_id.date_stop < self.date_start or
                    self.year_id.date_start > self.date_start or
                    self.year_id.date_start > self.date_stop):
                raise ValidationError('''Invalid Months ! Some months overlap
                                    or the date period is not in the scope
                                    of the academic year!''')

    @api.constrains('date_start', 'date_stop')
    def check_months(self):
        for old_month in self.search([('id', 'not in', self.ids)]):
            # Check start date should be less than stop date
            if old_month.date_start <= \
                    self.date_start <= old_month.date_stop \
                    or old_month.date_start <= \
                    self.date_stop <= old_month.date_stop:
                    raise ValidationError('''Error! You cannot define
                    overlapping months!''')

