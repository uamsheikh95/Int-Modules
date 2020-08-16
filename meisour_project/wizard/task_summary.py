from datetime import datetime, timedelta, date
from odoo import models, fields, api

class TaskSummaryWizard(models.TransientModel):
    _name = 'meisour_project.task_summary_wizard'
    _description = 'Task Summary Wizard'

    date_from = fields.Datetime('From', default=datetime.today().replace(day=1, hour=00, minute=00, second=00))
    date_to = fields.Datetime('To', default=fields.Datetime.now)
    report_by = fields.Selection([ ('employee', 'Employee'),('customer', 'Customer')], string='Report by', default='customer', required=True)
    partner_id = fields.Many2one('res.partner', string="Partner/Customer")
    user_id = fields.Many2one('res.users', string="Employee")

    def confirm(self):
        data = {
            'ids': self.ids,
            'model': self._name,
                'form': {
                    'partner_id': [self.partner_id.id, self.partner_id.name],
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'report_by': self.report_by,
                    'user_id': [self.user_id.id, self.user_id.name]
                },
        }

        return self.env.ref('meisour_project.action_task_summary_report').report_action(self, data=data)

    # @api.multi
    # def confirm(self):
		# pass
        # data = {
        #     'ids': self.ids,
        #     'model': self._name,
        #         'form': {
        #             'partner_id': [self.partner_id.id, self.partner_id.name],
        #             'date_from': self.date_from,
        #             'date_to': self.date_to,
        #             'report_by': self.report_by,
        #             'user_id': [self.user_id.id, self.user_id.name]
        #         },
        # }
		#
        # return self.env.ref('meisour_project.action_task_summary_report').report_action(self, data=data)

class TaskSummaryWizardReport(models.AbstractModel):
    _name = 'report.meisour_project.task_summary_wizard_report'
    _description = 'Task Summary Wizard Report'

    # def _get_total_tasks(self, date_from, date_to, report_by, group_by ):
    #     total_tasks = 0
    #
    #     params = []
    #     if date_from and date_to:
    #         params = [date_from, date_to]
    #     elif date_from:
    #         params = [date_from]
    #     elif date_to:
    #         params = [date_to]
    #
    #     query = """
    #         select * from project_task as pt
    #         left join project_task_type as ptt on pt.stage_id=ptt.id
    #         left join project_project as pp on pt.project_id=pp.id
    #         where ptt.name in ('Completed', 'Approved')
    #     """
    #
    #     if date_from:
    #         query +=  " and pt.start_time>=%s"
    #
    #     if date_to:
    #         query +=  " and pt.completed_date<=%s"
    #
    #
    #     if report_by == 'employee':
    #         query +=  " and pt.user_id=" + str(group_by)
    #     elif report_by == 'customer':
    #         query +=  " and pp.partner_id=" + str(group_by)
    #
    #     query +=  " order by 1"
    #
    #     self.env.cr.execute(query, tuple(params))
    #     res = self.env.cr.dictfetchall()
    #
    #     for r in res:
    #         total_tasks = total_tasks + 1
    #
    #     print('------------------------------------------------------dddddddddd----------------------------------------------------')
    #     print(total_tasks)
    #
    #     return total_tasks

    def _get_hours_taken(self, start_time, completed_date):
        hours = 0
        if start_time and completed_date:
            completed_date = datetime.strptime(str(completed_date), '%Y-%m-%d %H:%M:%S')
            start_time = datetime.strptime(str(start_time), '%Y-%m-%d %H:%M:%S')

            time_delta = (completed_date - start_time)
            total_seconds = time_delta.total_seconds()
            # minutes = total_seconds/60
            hours = total_seconds / 3600
            total_seconds %= 3600
            minutes = total_seconds // 60
            total_seconds %= 60
        return hours

    def _lines(self, date_from, date_to, report_by, group_by):
        full_task = []

        # params = []
        # if date_from and date_to:
        params = [date_from, date_to]
        # elif date_from:
        #     params = [date_from]
        # elif date_to:
        #     params = [date_to]

        query = """
            select pt.name, pt.start_time, pt.datetime_deadline, pt.completed_date, pt.user_id, rp.name as partner_name from project_task as pt
            left join project_task_type as ptt on pt.stage_id=ptt.id
            left join project_project as pp on pt.project_id=pp.id
            left join res_partner as rp on pp.partner_id=rp.id
            left join res_users as ru on pt.user_id=ru.id
            where ptt.name in ('Completed', 'Approved')
        """

        if date_from:
            query +=  " and pt.start_time>=%s"

        if date_to:
            query +=  " and pt.completed_date<=%s"
        #
        #
        if report_by == 'employee':
            query +=  " and pt.user_id=" + str(group_by)
        elif report_by == 'customer':
            query +=  " and pp.partner_id=" + str(group_by)

        query +=  " order by 1"

        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()

        for r in res:
            r['user_name'] = self.env['res.users'].search([('id', '=', r['user_id'])]).partner_id.name
            full_task.append(r)

        return full_task

    @api.model
    # def _get_report_values(self, docids, data=None):
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        report_by = data['form']['report_by']
        partner_id = data['form']['partner_id']
        user_id = data['form']['user_id']

        group_by = []

        if report_by == 'customer':
            if partner_id[0]:
                group_by.append(self.env['res.partner'].search([('id', '=', partner_id[0])]))
            else:
                for r in self.env['project.project'].search([]):
                    if r.partner_id and r.partner_id not in group_by :
                        group_by.append(r.partner_id)

        if report_by == 'employee':
            if user_id[0]:
                group_by.append(self.env['res.users'].search([('id', '=', user_id[0])]))
            else:
                for r in self.env['res.users'].sudo().search([]):
                    group_by.append(r)

        print('----------------------------------------------------------------------------------------------------------------------------------------------------')
        print(group_by)
        print('----------------------------------------------------------------------------------------------------------------------------------------------------')



        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'partner_id': partner_id,
            'report_by': report_by,
            'user_id': user_id,
            # 'get_total_tasks': self._get_total_tasks,
            'get_hours_taken': self._get_hours_taken,
            'lines': self._lines,
            'group_by': group_by,
        }
