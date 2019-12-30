# -*- coding: utf-8 -*-
import math
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api

# class tadamun-project(models.Model):
#     _name = 'tadamun-project.tadamun-project'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

HOURS_PER_DAY = 8

class Ops(models.Model):
    _name = 'tadamun_project.ops'
    
    name = fields.Char()
    
class Allocation(models.Model):
    _name = 'tadamun_project.allocation'
    
    name = fields.Char()
    
class Allocation(models.Model):
    _name = 'tadamun_project.location'
    
    name = fields.Char()
    
    
class Beneficierytype(models.Model):
    _name = 'tadamun_project.beneficierytype'
    
    name = fields.Char()
    
class PartnerType(models.Model):
    _name = 'tadamun_project.partnertype'
    
    name = fields.Char(required=True)
    
#LOGICAL FRAMEWORK
class ClusterObjectives(models.Model):
    _name = 'tadamun_project.clusterobjectives'
    
    name = fields.Text()
    
class HRPObjectives(models.Model):
    _name = 'tadamun_project.hrpobjectives'
    
    name = fields.Text()
    
class Months(models.Model):
    _name = 'tadamun_project.months'
    
    name = fields.Char()
    
  
class Cluster(models.Model):
    _name = 'tadamun_project.cluster'
    
    name = fields.Char()  
  

#OTHER INFO
class EnviromentalMarker(models.Model):
    _name = 'tadamun_project.enviromentalmarker'
    
    name = fields.Char()
    
class GenderMarker(models.Model):
    _name = 'tadamun_project.gendermarker'
    
    name = fields.Char()



    
    
class Project(models.Model):
    _inherit = 'project.project'

    #COVERPAGE
    project_name = fields.Char('Project Name')
    
    project_title = fields.Text(string="Project Title")
    fund_project_code = fields.Char(string="Fund Project Code", readonly=True)
    planned_start_date = fields.Date(default=datetime.today(),
        string="Planned Start Date")
    
    actual_start_date = fields.Date(string="Actual Start Date")
    project_duration = fields.Char(string="Project Duration", readonly=True, store=True)
    
    organizations_project_code = fields.Char(string="External/Organization's Project Code")
    planned_end_date = fields.Date(string="Planned End Date")
    actual_end_date = fields.Date(string="Actual End Date")
    project_budget_in_us = fields.Float(string="Project Budget in US$")
    project_location = fields.Many2one('tadamun_project.location', string="Project Location")
    
    project_summery = fields.Text(string="Project Summery")
    
    boys = fields.Integer(string= "Boys")
    girls = fields.Integer(string="Girls")
    men = fields.Integer(string="Men")
    women = fields.Integer(string="Women")
    no_of_beneficieries = fields.Integer(compute='_compute_fields', readonly=True)
    
    beneficiery_ids = fields.One2many('tadamun_project.beneficieries', 'project_id', string="Total Beneficieries Includeing the Following")
    
    total_other_beneficiaries = fields.Integer(compute='_compute_other_beneficiaries', readonly=True)
    
    
    
    indirect_beneficieries = fields.Text('Indirect Beneficieries')
    catchment_population = fields.Text('Catchment Population')
    link_with_alloc = fields.Text('Link with the Allocation Strategy')
    
    partner_name = fields.Char(string="Partner Name")
    parnter_type = fields.Many2one('tadamun_project.partnertype', string="Partner Type")
    parnter_budget_in_us = fields.Float('Budget in US$')
    partner_budget_total = fields.Float('Total', compute='_compute_partner_budget', readonly=True)
    
    has_other_funding = fields.Boolean('Has other funding been secured  for this project')
    source = fields.Char('Source')
    source_budget_in_us = fields.Float('US$')
    source_budget_total = fields.Float('Total', compute='_compute_source_budget', readonly=True)
    
    org_name = fields.Char('Name')
    title = fields.Char('Title')
    tel = fields.Char('Tel')
    email = fields.Char('Email')
    
    contacts = fields.One2many('tadamun_project.contacts', 'project_id', string="Contacts")
    
    leave_comment = fields.Text('Leave Comment')
    
    #BACKGROUND
    humanitarian_context = fields.Text('Humanitarian Context Analysis')
    need_assessment = fields.Text('Need Assesment')
    description_of_beneficiaries = fields.Text('Description of Beneficieries')
    grant_request = fields.Text('Grant Request Justification')
    complementarity = fields.Text('Complementarity')
    
    leave_comment2 = fields.Text('Leave Comment')
    
    #LOGICAL FARAMEWORK
    overall_project_objective = fields.Text('Overall Project Objectivie')
    cluster_objectives = fields.Many2one('tadamun_project.clusterobjectives')
    hrp_objectives = fields.Many2one('tadamun_project.hrpobjectives')
    percentage_of_activities = fields.Float('Percentage of Activities')
    total_percentage = fields.Float(readonly=True, compute='_total_percentage')
    sector_objectives = fields.Text('Constribution to Cluster/Sector Objectives')
    project_type = fields.Many2many('tadamun_project.cluster', string='Project Type')
    
    
    outcome_ids = fields.One2many('tadamun_project.outcome', 'project_id', string='Outcome')
    
    additional_targets = fields.Text('Additional Targets')
    
    leave_comment3 = fields.Text('Leave Comment')
    
    #WORKPLAN
    
    
    activity_ids = fields.One2many('tadamun_project.activities', 'project_id', string='Activties')
    leave_comment4 = fields.Text('Leave Comment')
    
    #M&R Details
    monitoring_plan = fields.Text('Monitoring & Reporting Plan')
    leave_comment5 = fields.Text('Leave Comment')
    
    #Other Info
    accountability = fields.Text('Accountability to Affected Populations')
    implementation_plam = fields.Text('Implemention Plan')
    cordination_with_orgs = fields.One2many('tadamun_project.coordinatedorganizations', 'project_id', string='Coordination with Other Organizations in Project Area')
    name_of_the_org = fields.Char('Name of the Organization')
    areas_and_activities = fields.Char('Areas/Activities of collaboration and rationale')
    enviromentalmarker = fields.Many2one('tadamun_project.enviromentalmarker', string='Enviromental Marker Code')
    gendermarker = fields.Many2one('tadamun_project.gendermarker', string='Gender Marker Code')
    justify_chosen = fields.Text('Justify Chosen Gender Marker Code')
    protection_mainstreaming = fields.Text('Projection Mainstreaming')
    safety_and_security = fields.Text('Safety and Security')
    access = fields.Text('Access')
    leave_comment6 = fields.Text('Leave Comment')
    
    #Budget
    staff_ids = fields.One2many('tadamun_project.staff', 'project_id')
    staff_total = fields.Monetary('Total', compute='_get_budgets_total', store=True, readonly=True, track_visibility='always')
    supplies_ids = fields.One2many('tadamun_project.supplies', 'project_id')
    supplies_total = fields.Monetary('Total', compute='_get_budgets_total', store=True, readonly=True, track_visibility='always')
    equimpent_ids = fields.One2many('tadamun_project.equipment', 'project_id')
    equimpent_total = fields.Monetary('Total', compute='_get_budgets_total', store=True, readonly=True, track_visibility='always')
    travel_or_transportation_ids = fields.One2many('tadamun_project.travel', 'project_id')
    travel_or_transportation_total = fields.Monetary('Total', compute='_get_budgets_total', store=True, readonly=True, track_visibility='always')
    general_operating_ids = fields.One2many('tadamun_project.generaloperating', 'project_id')
    general_operating_total = fields.Monetary('Total', compute='_get_budgets_total', store=True, readonly=True, track_visibility='always')
    
    direct_cost_total = fields.Monetary('Grand Total For Direct Cost', compute='_get_direct_cost', store=True, readonly=True, track_visibility='always')
    project_support_cost = fields.Float('Project Support Cost (PSC) Rate (insert percentage, not to exceed 7 per cent)')
    direct_cost_and_support_total = fields.Monetary('Grand Total For Both Direct and Support Costs', compute='_get_direct_cost_and_pos', store=True, readonly=True, track_visibility='always')
    
    
    #Report Fields
    
        
    # r - stands for report
    # w - stands for weekly
    # m - stands for monthly
    
    # 1- Weekly :
    
    from_date_w_r = fields.Char('From')
    to_date_w_r = fields.Char('To')
    name_of_person_w_r = fields.Text('Name of person completing this report: (incl. title and e-mail address)')

    
    boys_w_r = fields.Integer('Boys')
    girls_w_r = fields.Integer('Girls')
    men_w_r = fields.Integer('Men')
    women_w_r = fields.Integer('Women')
    no_of_beneficieries_w_r = fields.Integer('Total', compute="_compute_no_of_beneficieries_w_r")
    
    completed_task_ids = fields.One2many('project.task', 'project_id', stirng="Completed Tasks/Activities", domain=[('stage_id','=','Completed')])
    
    
    weekly_remarks_ids = fields.One2many('tadamun_project.weekly_remarks', 'project_id')
    inprogress_tasks_ids = fields.One2many('tadamun_project.inprogress_tasks', 'project_id')
    next_week_tasks_ids = fields.One2many('tadamun_project.next_week_tasks', 'project_id')
    unforeseen_ids = fields.One2many('tadamun_project.unforeseen', 'project_id')
    possible_solutions_ids = fields.One2many('tadamun_project.possible_solutions', 'project_id')
    
    
    # 2- Monthly :
    
    from_date_m_r = fields.Char('From')
    to_date_m_r = fields.Char('To')
    name_of_person_m_r = fields.Text('Name of person completing this report: (incl. title and e-mail address)')
    
    project_overview = fields.Text()
    sum_proj_acheiv = fields.Text()
    
    challenges = fields.Text()
    human_stories = fields.Text()
    
    monthly_palanned_bef = fields.Integer()
    
    boys_m_r = fields.Integer('Boys')
    girls_m_r = fields.Integer('Girls')
    men_m_r = fields.Integer('Men')
    women_m_r = fields.Integer('Women')
    no_of_beneficieries_m_r = fields.Integer('Total', compute="_compute_no_of_beneficieries_m_r")
    
    
    
    monthly_remarks_ids = fields.One2many('tadamun_project.monthly_remarks', 'project_id')
    
    photos = fields.Many2many('ir.attachment', 'monthly', string="Image")
    
    
    # 3- Quarter :
    
    donor = fields.Char()
    quarter_of_reporting = fields.Text()
    introduction = fields.Text()
    
    project_target = fields.Text()
    quarter_target = fields.Text()
    quarter_budget = fields.Text()
    
    boys_q_r = fields.Integer('Boys')
    girls_q_r = fields.Integer('Girls')
    men_q_r = fields.Integer('Men')
    women_q_r = fields.Integer('Women')
    no_of_beneficieries_q_r = fields.Integer('Total', compute="_compute_no_of_beneficieries_q_r")

    
    remaining_target = fields.Text()
    
    quarter_remarks_ids = fields.One2many('tadamun_project.quarter_remarks', 'project_id')
    
    
    lessons_learned = fields.Text()
    challenges_quarter = fields.Text()
    annex = fields.Text()
    case_studies = fields.Text()
    human_stories_quarter = fields.Text()
    activity_photos = fields.Many2many('ir.attachment', 'quarter', string="Activity Photos")
    next_quarter_plan = fields.Text()
    
    
    
    
    
    
    @api.model
    def create(self, vals):
        prefix          =   "PR"
        code            =   "tadamun_project.project"
        name            =   prefix+"_"+code
        implementation  =   "no_gap"
        padding  =   "4"
        dict            =   { "prefix":prefix,
        "code":code,
        "name":name,
        "active":True,
        "implementation":implementation,
        "padding":padding}
        if self.env['ir.sequence'].search([('code','=',code)]).code == code:
            vals['fund_project_code'] =  self.env['ir.sequence'].next_by_code('tadamun_project.project')
        else:
            new_seq = self.env['ir.sequence'].create(dict)
            vals['fund_project_code']    =   self.env['ir.sequence'].next_by_code(code)
        result = super(Project, self).create(vals)
        return result
    
    #calculate project duration
    #@api.onchange('actual_start_date', 'actual_end_date')
    def _get_number_of_days(self, actual_start_date, actual_end_date):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(actual_start_date)
        to_dt = fields.Datetime.from_string(actual_end_date)

        time_delta = to_dt - from_dt
        return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
        
    @api.onchange('actual_start_date')
    def _onchange_date_from(self):
        """ If there are no date set for date_to, automatically set one 8 hours later than
            the date_from. Also update the number_of_days.
        """
        date_from = self.actual_start_date
        date_to = self.actual_end_date

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(hours=HOURS_PER_DAY)
            self.date_to = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.project_duration = self._get_number_of_days(date_from, date_to)
        else:
            self.project_duration = 0

    @api.onchange('actual_end_date')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        date_from = self.actual_start_date
        date_to = self.actual_end_date

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.project_duration = self._get_number_of_days(date_from, date_to)
        else:
            self.project_duration = 0
#####################################################################################3
        
    @api.one
    @api.depends('boys', 'girls', 'men', 'women')
    def _compute_fields(self):
        if self.boys or self.girls or self.men or self.women:
            self.no_of_beneficieries = self.boys + self.girls + self.men + self.women
    
    
    @api.one
    @api.depends('beneficiery_ids')
    def _compute_other_beneficiaries(self):
        if self.beneficiery_ids:
            self.total_other_beneficiaries = sum(line.no_of_beneficieries for line in self.beneficiery_ids)
    
    #@api.constrains('no_of_beneficieries')
    #def _check_instructor_not_in_attendees(self):
    #	if total_other_beneficiaries > no_of_beneficieries:
    #			raise ValidationError('''The total number of beneficieries should be less than or equal to the total number of beneficieries above''')
                
                
    @api.onchange('total_other_beneficiaries')
    def _check_total_ben(self):
        if self.total_other_beneficiaries > self.no_of_beneficieries:
                raise ValidationError('''The total number of beneficieries should be less than or equal to the total number of beneficieries above''')
    
    
            
    @api.one
    @api.depends('parnter_budget_in_us')
    def _compute_partner_budget(self):
        if self.parnter_budget_in_us:
            self.partner_budget_total = self.parnter_budget_in_us
            
    @api.one
    @api.depends('source_budget_in_us')
    def _compute_source_budget(self):
        if self.source_budget_in_us:
            self.source_budget_total = self.source_budget_in_us
            
    @api.one
    @api.depends('percentage_of_activities')
    def _total_percentage(self):
        if self.percentage_of_activities:
            self.total_percentage = self.percentage_of_activities
            
    


    
            
    @api.one
    @api.depends('staff_ids', 'staff_ids.total','equimpent_ids', 'equimpent_ids.total', 'supplies_ids', 'supplies_ids.total', 'travel_or_transportation_ids', 'travel_or_transportation_ids.total', 'general_operating_ids', 'general_operating_ids.total')
    def _get_budgets_total(self):
        self.staff_total=sum(staff_id.total for staff_id in self.staff_ids)
        self.equimpent_total=sum(equimpent_id.total for equimpent_id in self.equimpent_ids)
        self.supplies_total=sum(supplies_id.total for supplies_id in self.supplies_ids)
        self.travel_or_transportation_total=sum(travel_or_transportation_id.total for travel_or_transportation_id in self.travel_or_transportation_ids)
        self.general_operating_total=sum(general_operating_total_id.total for general_operating_total_id in self.general_operating_ids)
        
    @api.one
    @api.depends('staff_total','equimpent_total','supplies_total','travel_or_transportation_total','general_operating_total')
    def _get_direct_cost(self):
        if self.staff_total or self.equimpent_total or self.supplies_total or self.travel_or_transportation_total or self.general_operating_total:
            self.direct_cost_total=self.staff_total + self.equimpent_total + self.supplies_total + self.travel_or_transportation_total + self.general_operating_total
            
    @api.one
    @api.depends('direct_cost_total', 'project_support_cost')
    def _get_direct_cost_and_pos(self):
        if self.direct_cost_total or self.project_support_cost:
            self.direct_cost_and_support_total = self.direct_cost_total + self.project_support_cost
            
            
    
    @api.one
    @api.depends('boys_w_r', 'girls_w_r', 'men_w_r', 'women_w_r')
    def _compute_no_of_beneficieries_w_r(self):
        if self.boys_w_r or self.girls_w_r or self.men_w_r or self.women_w_r:
            self.no_of_beneficieries_w_r = self.boys_w_r + self.girls_w_r + self.men_w_r + self.women_w_r
            
        
    @api.one 
    @api.depends('boys_m_r', 'girls_m_r', 'men_m_r', 'women_m_r')
    def _compute_no_of_beneficieries_m_r(self): 
        if self.boys_m_r or self.girls_m_r or self.men_m_r or self.women_m_r:
            self.no_of_beneficieries_m_r = self.boys_m_r + self.girls_m_r + self.men_m_r + self.women_m_r
            
    
    @api.one 
    @api.depends('boys_q_r', 'girls_q_r', 'men_q_r', 'women_q_r')
    def _compute_no_of_beneficieries_q_r(self): 
        if self.boys_q_r or self.girls_q_r or self.men_q_r or self.women_q_r:
            self.no_of_beneficieries_q_r = self.boys_q_r + self.girls_q_r + self.men_q_r + self.women_q_r
        
            
#for Beneficieries
class Beneficieries(models.Model):
    _name = 'tadamun_project.beneficieries'
    
    bef_type = fields.Many2one('tadamun_project.beneficierytype')
    boys = fields.Integer(string= "Boys")
    girls = fields.Integer(string="Girls")
    men = fields.Integer(string="Men")
    women = fields.Integer(string="Women")
    no_of_beneficieries = fields.Integer(compute='_compute_fields', readonly=True)
    project_id = fields.Many2one('project.project')
    
    @api.one
    @api.depends('boys', 'girls', 'men', 'women')
    def _compute_fields(self):
        if self.boys or self.girls or self.men or self.women:
            self.no_of_beneficieries = self.boys + self.girls + self.men + self.women
            
            
#Contacts
class Contacts(models.Model):
    _name = 'tadamun_project.contacts'
    
    contact_name = fields.Char(required=True, string = "Contact Name")
    title = fields.Char(string = "Title")
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    project_id = fields.Many2one('project.project')


#############################################
# Outcome
#############################################
class Outcome(models.Model):
    _name = 'tadamun_project.outcome'
    
    name = fields.Char(string = "Outcome")
    desc = fields.Char(string = "Description")
    achev = fields.Text()
    project_id = fields.Many2one('project.project', store=True)
    output_ids = fields.One2many('tadamun_project.output', 'outcome_id', string='Output')
    get_proj_id = fields.Integer('Get Project Id', compute="_get_project_id")
    
    @api.one
    @api.depends('project_id')
    def _get_project_id(self):
        if self.project_id:
            self.get_proj_id=self.project_id.id
    
        
    
#############################################
# Outputs
#############################################
class Output(models.Model):
    _name = 'tadamun_project.output'

    
    name = fields.Char(string = "Output")
    desc = fields.Char(string = "Description")
    outcome_id = fields.Many2one('tadamun_project.outcome',  store=True)
    project_id = fields.Many2one('project.project', compute="_get_project_id")
    indicator_ids = fields.One2many('tadamun_project.indicator', 'output_id', string='Indicators')
    activity_ids = fields.One2many('tadamun_project.activities', 'output_id', string='Activties')
    
    @api.one
    @api.depends('outcome_id')
    def _get_project_id(self):
        if self.outcome_id:
            self.project_id=self.env['project.project'].search([('id', '=', self.outcome_id.get_proj_id)])
                
#############################################
# Indicators
#############################################
    
class Indicator(models.Model):
    _name = 'tadamun_project.indicator'
    
    name = fields.Char(string = "Code")
    type = fields.Char(string = "Type", default="Standard")
    cluster = fields.Many2one('tadamun_project.cluster', string="Cluster")
    indicator = fields.Char('Indicator')
    total_end_cycle = fields.Integer('Total End-Cycle Target')
    means_of_verification = fields.Char('Means of Verification')
    output_id = fields.Many2one('tadamun_project.output', ondelete='cascade', index=True)
    
    
#############################################
# Activities
#############################################
    
class Activities(models.Model):
    _name = 'tadamun_project.activities'
    
    #@api.model
    #def formate_date(self):
        #self.date_project = datetime.datetime.strptime('2019-1-2', '%Y-%m-%d').year
       # self.date_project = datetime.datetime.strptime(self.create_date, "%Y-%m-%d").year    
       # self.date_project = datetime.today().year
    
    #def _default_project_id(self):
    #	return self.env['project.project'].search([('id', '=', self.output_id.outcome_id.project_id)], limit=1)		, default=_default_project_id
    
    name = fields.Char(string = "Activity")
    date_project = fields.Char(string="Year", compute='get_date_project')
    desc = fields.Char(string = "Description")
    output_id = fields.Many2one('tadamun_project.output', ondelete='cascade', index=True)
    project_id = fields.Many2one('project.project', ondelete='cascade', related="output_id.project_id", store=True)
    
    workplan_months = fields.Many2many('tadamun_project.months')
    
    @api.one
    @api.depends('project_id')
    def get_date_project(self):
        if self.project_id:
            a = datetime.strptime(str(self.create_date), '%Y-%m-%d %H:%M:%S').date()
            self.date_project = a.year
    
    

    
    

    
#Other Info
class CoordinatedOrganizations(models.Model):
    _name = 'tadamun_project.coordinatedorganizations'
    
    name = fields.Char(string='Coordinated Organizations')
    project_id = fields.Many2one('project.project')
    
    
#Budget : 1- Staff Budgets
class Staff(models.Model):
    _name = 'tadamun_project.staff'
    
    budget_code = fields.Char(required=True, string = "Code")
    budget_line_description = fields.Char(string = "Description")
    remarks = fields.Text('Remarks')
    d_and_s = fields.Selection([
        ('d', 'D'),
        ('s', 'S'),
        ], string='D/S', default='d')
    unit_quantity = fields.Integer('Quantity')
    unit_cost = fields.Integer('Cost')
    duration = fields.Integer('Duration')
    total_cost = fields.Float('Total Cost %')
    total = fields.Float('Total', compute='_compute_budgets', readonly=True, store=True)
    
    project_id = fields.Many2one('project.project')
    
    @api.one
    @api.depends('unit_quantity', 'unit_cost', 'duration', 'total_cost')
    def _compute_budgets(self):
        if self.unit_quantity or self.unit_cost or self.duration or self.total_cost:
            self.total = self.unit_quantity * self.unit_cost * self.duration * (self.total_cost/100)
            

#Budget : 2- Supplies, Commodities, Materials Budgets
class Supplies(models.Model):
    _name = 'tadamun_project.supplies'
    
    budget_code = fields.Char(required=True, string = "Code")
    budget_line_description = fields.Char(string = "Description")
    remarks = fields.Text('Remarks')
    d_and_s = fields.Selection([
        ('d', 'D'),
        ('s', 'S'),
        ], string='D/S', default='d')
    unit_quantity = fields.Integer('Quantity')
    unit_cost = fields.Integer('Cost')
    duration = fields.Integer('Duration')
    total_cost = fields.Float('Total Cost %')
    total = fields.Float('Total', compute='_compute_budgets', readonly=True, store=True)
    
    project_id = fields.Many2one('project.project')
    
    @api.one
    @api.depends('unit_quantity', 'unit_cost', 'duration', 'total_cost')
    def _compute_budgets(self):
        if self.unit_quantity or self.unit_cost or self.duration or self.total_cost:
            self.total = self.unit_quantity * self.unit_cost * self.duration * (self.total_cost/100)
            
#Budget : 3- Equipment Budgets
class Equipment(models.Model):
    _name = 'tadamun_project.equipment'
    
    budget_code = fields.Char(required=True, string = "Code")
    budget_line_description = fields.Char(string = "Description")
    remarks = fields.Text('Remarks')
    d_and_s = fields.Selection([
        ('d', 'D'),
        ('s', 'S'),
        ], string='D/S', default='d')
    unit_quantity = fields.Integer('Quantity')
    unit_cost = fields.Integer('Cost')
    duration = fields.Integer('Duration')
    total_cost = fields.Float('Total Cost %')
    total = fields.Float('Total', compute='_compute_budgets', readonly=True, store=True)
    
    project_id = fields.Many2one('project.project')
    
    @api.one
    @api.depends('unit_quantity', 'unit_cost', 'duration', 'total_cost')
    def _compute_budgets(self):
        if self.unit_quantity or self.unit_cost or self.duration or self.total_cost:
            self.total = self.unit_quantity * self.unit_cost * self.duration * (self.total_cost/100)
            
            
#Budget : 4- Travel Budgets
class Travel(models.Model):
    _name = 'tadamun_project.travel'
    
    budget_code = fields.Char(required=True, string = "Code")
    budget_line_description = fields.Char(string = "Description")
    remarks = fields.Text('Remarks')
    d_and_s = fields.Selection([
        ('d', 'D'),
        ('s', 'S'),
        ], string='D/S', default='d')
    unit_quantity = fields.Integer('Quantity')
    unit_cost = fields.Integer('Cost')
    duration = fields.Integer('Duration')
    total_cost = fields.Float('Total Cost %')
    total = fields.Float('Total', compute='_compute_budgets', readonly=True, store=True)
    
    project_id = fields.Many2one('project.project')
    
    @api.one
    @api.depends('unit_quantity', 'unit_cost', 'duration', 'total_cost')
    def _compute_budgets(self):
        if self.unit_quantity or self.unit_cost or self.duration or self.total_cost:
            self.total = self.unit_quantity * self.unit_cost * self.duration * (self.total_cost/100)
            
            
#Budget : 5- General Operating Budgets
class GeneralOperating(models.Model):
    _name = 'tadamun_project.generaloperating'
    
    budget_code = fields.Char(required=True, string = "Code")
    budget_line_description = fields.Char(string = "Description")
    remarks = fields.Text('Remarks')
    d_and_s = fields.Selection([
        ('d', 'D'),
        ('s', 'S'),
        ], string='D/S', default='d')
    unit_quantity = fields.Integer('Quantity')
    unit_cost = fields.Integer('Cost')
    duration = fields.Integer('Duration')
    total_cost = fields.Float('Total Cost %')
    total = fields.Float('Total', compute='_compute_budgets', readonly=True, store=True)
    
    project_id = fields.Many2one('project.project')
    
    @api.one
    @api.depends('unit_quantity', 'unit_cost', 'duration', 'total_cost')
    def _compute_budgets(self):
        if self.unit_quantity or self.unit_cost or self.duration or self.total_cost:
            self.total = self.unit_quantity * self.unit_cost * self.duration * (self.total_cost/100)
            
            
    
#ٌReport Models
class WeeklyRemarks(models.Model):
    _name = 'tadamun_project.weekly_remarks'
    
    name = fields.Char()
    project_id = fields.Many2one('project.project')
    
class MonthlyRemarks(models.Model):
    _name = 'tadamun_project.monthly_remarks'
    
    name = fields.Char()
    project_id = fields.Many2one('project.project')
    
    
class QuarterRemarks(models.Model):
    _name = 'tadamun_project.quarter_remarks'
    
    name = fields.Char()
    project_id = fields.Many2one('project.project')
    

class InProgressTasks(models.Model):
    _name = 'tadamun_project.inprogress_tasks'
    
    name = fields.Char()
    project_id = fields.Many2one('project.project')
    

class NextWeekTasks(models.Model):
    _name = 'tadamun_project.next_week_tasks'
    
    name = fields.Char()
    project_id = fields.Many2one('project.project')
    

class Unforeseen(models.Model):
    _name = 'tadamun_project.unforeseen'
    
    name = fields.Char()
    project_id = fields.Many2one('project.project')
    
class PossibleSolutions(models.Model):
    _name = 'tadamun_project.possible_solutions'
    
    name = fields.Char()
    project_id = fields.Many2one('project.project')