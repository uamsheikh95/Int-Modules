# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import calendar

class Subject(models.Model):
    _name = 'exam_bank.subject'
    _description = "Subject"
    _order = "name asc"

    name = fields.Char('Subject Name', required=True)

class Responsible(models.Model):
    _name = 'exam_bank.responsible'
    _description = "Exam Responsible"
    _order = "name asc"

    name = fields.Char('Responsible Name', required=True)
    mobile = fields.Char('Mobile')

class Section(models.Model):
    _name = 'exam_bank.section'
    _description = 'Question Sections'
    _order = 'id asc'

    name = fields.Char(string='Section Name')

class Exam(models.Model):
    _name = "exam_bank.exam"
    _description = "Exam"
    _order = "id desc"

    @api.model
    def check_current_year(self):
		'''Method to get default value of logged in Student'''
		res = self.env['exam_bank.year'].search([('current', '=',
												 True)])
		if not res:
			raise ValidationError('''There is no current Academic Year defined!
                                    Please contact to Administator!''')
		return res.id

    name = fields.Char('Name', required=True)
    level = fields.Selection([('elementary', 'Elementary'), ('secondary', 'Secondary')], 'Level', required=True)
    subject_id = fields.Many2one('exam_bank.subject', string="Subject", required=True)
    exam_marks = fields.Float(string='Exam Marks')
    question_ids = fields.Many2many('exam_bank.question')
    total_questions_marks = fields.Float('Total Marks', default=0)#, compute='_get_total_marks'
    year_id = fields.Many2one('exam_bank.year', string='Year', default=check_current_year)
    section_ids = fields.One2many('exam_bank.exam_section', 'exam_id')

    @api.multi
    def generate_exam(self):
        # Step 1: Get questions are'nt in the last three years
        last_three_years_question_ids = []
        last_three_years_exams_ids = self.env['exam_bank.exam'].search([('subject_id', '=', self.subject_id.id),
                                                            ('level', '=', self.level)], order="id asc")[-4:-1]

        # Step 2: Append last three years question_ids to last_three_years_question_ids variable
        for record in last_three_years_exams_ids:
            if record.question_ids:
                last_three_years_question_ids.append(record.question_ids.ids)

        # Step 3: Loop through section_ids to get section_ids and generate exam questions
        exam_section_ids = []
        for sec in self.section_ids:
            exam_section_ids.append(sec.id)

        for line in exam_section_ids:
            for section in self.env['exam_bank.exam_section'].search([('id', '=', line)]):
                fetched_questions = ''
                fetched_questions_ids = []

                section_id = section.section_id
                marks = section.marks

                # This condition checks if thre is last three years exams or not
                if sum(last_three_years_question_ids, []):
                    fetched_questions = self.env['exam_bank.question'].search([('id', 'not in', sum(last_three_years_question_ids, [])),
                        ('subject_id', '=', self.subject_id.id), ('level', '=', self.level), ('section_id', '=', section_id.id)])
                else:
                    fetched_questions = self.env['exam_bank.question'].search([('subject_id', '=', self.subject_id.id), ('level', '=', self.level),
                                                                                                                ('section_id', '=', section_id.id)])
                # Append fetched_questions ids to fetched_questions_ids variable
                for question in fetched_questions:
                    fetched_questions_ids.append(question.id)

                total_questions_marks = 0.00
                for rec in fetched_questions_ids:
                    if marks > total_questions_marks:
                        self.question_ids = self.question_ids + self.env['exam_bank.question'].search([('id', '=', rec),
                                                                                ('subject_id', '=', self.subject_id.id),
                                                                                ('level', '=', self.level),
                                                                                ('section_id', '=', section_id.id)], order='section_id asc')

                        total_questions_marks = self.total_questions_marks +  self.env['exam_bank.question'].search([('id', '=', rec),
                                                                                ('subject_id', '=', self.subject_id.id),
                                                                                ('level', '=', self.level),
                                                                                ('section_id', '=', section_id.id)]).marks



class Question(models.Model):
    _name = 'exam_bank.question'
    _description = "Question"
    _order = "subject_id asc"

    name = fields.Char('Question')
    responsible_id = fields.Many2one('exam_bank.responsible', string="Prepared by")
    marks = fields.Float('Marks')
    subject_id = fields.Many2one('exam_bank.subject', string="Subject", required=True)
    level = fields.Selection([('elementary', 'Elementary'), ('secondary', 'Secondary')], 'Level', required=True)
    section_id = fields.Many2one('exam_bank.section', string='Section')
    image_ids = fields.One2many('exam_bank.question_images', 'question_id')

class QustionImages(models.Model):
    _name = 'exam_bank.question_images'
    _description = 'Exam Question Images'
    _order = 'id asc'

    image = fields.Binary(string='Image')
    question_id = fields.Many2one('exam_bank.question')

class Year(models.Model):
    _name = 'exam_bank.year'
    _description = "Academic Year"
    _order = "id desc"

    name = fields.Char(string='Name', default='New', help='Year', readonly=True)
    date_start = fields.Date('Start Date', required=True,
    						 help='Starting date of academic year')
    date_stop = fields.Date('End Date', required=True,
    						help='Ending of academic year')
    current = fields.Boolean('Current', help="Set Active Current Year")


    @api.model
    def next_year(self, sequence):
    	'''This method assign sequence to years'''
    	year_id = self.search([('sequence', '>', sequence)], order='id',
    						  limit=1)
    	if year_id:
    		return year_id.id
    	return False

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

    @api.model
    def create(self, vals):

        date_start = datetime.strptime(vals['date_start'], DEFAULT_SERVER_DATE_FORMAT)
        date_stop = datetime.strptime(vals['date_stop'], DEFAULT_SERVER_DATE_FORMAT)
        vals['name'] = str(date_start.year) + ' - ' + str(date_stop.year)
        rec = super(Year, self).create(vals)
        return rec

class ExamSection(models.Model):
    _name = 'exam_bank.exam_section'
    _description = 'Exam Sections'
    _order = 'id asc'
    rec_name = 'section_id'

    section_id = fields.Many2one('exam_bank.section', string='Section', required=True)
    marks = fields.Float(string='Marks', required=True)
    exam_id = fields.Many2one('exam_bank.exam')
