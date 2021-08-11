# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Ijaz Ahammed (odoo@cybrosys.com)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from datetime import datetime, timedelta, date
from pytz import timezone, UTC
import pytz
from odoo import models, fields, api
import datetime as dd

import ftplib
import xlsxwriter
import pandas as pd
from io import BytesIO

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

#     late_check_in = fields.Integer(string="Late Check-in(Minutes)", compute="get_late_minutes")
    
    late_time = fields.Float(string="Late Time", compute="get_late_minutes")

    def get_late_minutes(self):
        for rec in self:
            rec.late_check_in = 0.0
            week_day = rec.sudo().check_in.weekday()
            if rec.employee_id.contract_id:
                work_schedule = rec.sudo().employee_id.contract_id.resource_calendar_id
                for schedule in work_schedule.sudo().attendance_ids:
                    if schedule.dayofweek == str(week_day) and schedule.day_period == 'morning':
                        work_from = schedule.hour_from
                        result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))

                        user_tz = self.env.user.tz
                        dt = rec.check_in

                        if user_tz in pytz.all_timezones:
                            old_tz = pytz.timezone('UTC')
                            new_tz = pytz.timezone(user_tz)
                            dt = old_tz.localize(dt).astimezone(new_tz)
                        str_time = dt.strftime("%H:%M")
                        check_in_date = datetime.strptime(str_time, "%H:%M").time()
                        start_date = datetime.strptime(result, "%H:%M").time()
                        t1 = timedelta(hours=check_in_date.hour, minutes=check_in_date.minute)
                        t2 = timedelta(hours=start_date.hour, minutes=start_date.minute)
                        if check_in_date > start_date:
                            final = t1 - t2
                            rec.sudo().late_check_in = final.total_seconds() / 60

    def late_check_in_records(self):
        existing_records = self.env['late.check_in'].sudo().search([]).attendance_id.ids
        minutes_after = int(self.env['ir.config_parameter'].sudo().get_param('late_check_in_after')) or 0
        max_limit = int(self.env['ir.config_parameter'].sudo().get_param('maximum_minutes')) or 0
        late_check_in_ids = self.sudo().search([('id', 'not in', existing_records)])
        for rec in late_check_in_ids:
            late_check_in = rec.sudo().late_check_in + 210
            if rec.late_check_in > minutes_after and late_check_in > minutes_after and late_check_in < max_limit:
                self.env['late.check_in'].sudo().create({
                    'employee_id': rec.employee_id.id,
                    'late_minutes': late_check_in,
                    'date': rec.check_in.date(),
                    'attendance_id': rec.id,
                })

    def calculate_late_time(self):
        final = 0.0
        week_day = self.check_in.weekday()
        if self.employee_id.contract_id:
            work_schedule = self.employee_id.contract_id.resource_calendar_id
            for schedule in work_schedule.attendance_ids:
                if str(schedule.dayofweek) == str(week_day) and schedule.day_period == 'morning':
                    work_from = schedule.hour_from
                    result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))
                    str_time = datetime.now().time()
                    user_tz = self.env.user.tz
                    dt = self.check_in
                    if user_tz in pytz.all_timezones:
                        old_tz = pytz.timezone('UTC')
                        new_tz = pytz.timezone(user_tz)
                        dt = old_tz.localize(dt).astimezone(new_tz)
                    str_time = dt.strftime("%H:%M")
                    check_in_date = datetime.strptime(str_time, "%H:%M")
                    start_date = datetime.strptime(result, "%H:%M").time()
                    t1 = timedelta(hours=check_in_date.hour, minutes=check_in_date.minute)
                    t2 = timedelta(hours=start_date.hour, minutes=start_date.minute)
                    if check_in_date > start_date:
                        final = (t1 - t2).total_seconds() / 3600
        return final
#         return str(check_in_date) + " "+str(datetime.utcnow().strftime("%H:%M")) + " "+str(str_time) + " "+ str(user_tz) +" "+ str(new_tz)

    def get_late_minutes(self):
        for rec in self:
            late_time = 0.0
            rec.late_time = late_time
            week_day = rec.sudo().check_in.weekday()
            check_late_time = self.env['ir.config_parameter'].sudo().get_param('check_late_time')
            late_check_in_after = float(self.env['ir.config_parameter'].sudo().get_param('late_check_in_after'))
            if check_late_time:
                if rec.employee_id.contract_id:
                    work_schedule = rec.sudo().employee_id.contract_id.resource_calendar_id
                    for schedule in work_schedule.sudo().attendance_ids:
                        if str(schedule.dayofweek) == str(week_day) and schedule.day_period == 'morning':
                            work_from = schedule.hour_from
                            check_in = rec.check_in
                            check_in_utc = pytz.utc.localize(check_in)
                            tz = pytz.timezone(rec.employee_id.tz)
                            check_in_tz = datetime.strptime(check_in_utc.astimezone(tz).strftime("%H:%M"), "%H:%M")
                            
                            check_in_time = timedelta(hours=check_in_tz.hour, minutes=check_in_tz.minute).total_seconds() / 3600
#                             raise Warning(str(check_in_time))
    #                         start_tz = now_tz + relativedelta(hour=0, minute=0)  # day start in the employee's timezone
    #                         start_naive = start_tz.astimezone(pytz.utc).replace(tzinfo=None)
#                             rec.sudo().late_time = 20.12
                            if check_in_time > work_from:
                                late_time = check_in_time - work_from
                                if late_time > late_check_in_after:
                                    rec.sudo().late_time = late_time
#                         result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))
#                         str_time = datetime.now().time()
#                         user_tz = self.env.user.tz
#                         dt = rec.check_in
#                         if user_tz in pytz.all_timezones:
#                             old_tz = pytz.timezone('UTC')
#                             new_tz = pytz.timezone(user_tz)
#                             dt = old_tz.localize(dt).astimezone(new_tz)
#                         str_time = dt.strftime("%H:%M")
#                         check_in_date = datetime.strptime(str_time, "%H:%M").time()
#                         start_date = datetime.strptime(result, "%H:%M").time()
#                         t1 = timedelta(hours=check_in_date.hour, minutes=check_in_date.minute)
#                         t2 = timedelta(hours=start_date.hour, minutes=start_date.minute)
#                         if check_in_date > start_date:
#                             rec.sudo().late_time = (t1 - t2).total_seconds() / 3600

#     def handle_binary(self, more_data):
#         return more_data
        
    def add_attendance(self):
        ftp = ftplib.FTP('185.27.134.11', 'vasts_29323062','asd12345')
#         ftp.connect('185.27.134.11', 21)
#         ftp.login('vasts_29323062','asd12345')
        ftp.cwd("/htdocs")
        files = ftp.dir()
        data = []
        flo = BytesIO()
        ftp.retrbinary('RETR transaction.xlsx', flo.write)
        flo.seek(0)
        df = pd.read_excel(flo)
        attendence_lines = df.groupby(['First Name','Date']).agg({'Time': ['min', 'max']})
#         raise Warning(pd.read_excel(flo))
#         df = pd.read_excel(flo,index_col=0)
#         raise Warning(attendence_lines)
        first = True
        for row in attendence_lines.itertuples():
            partner_id = self.env['hr.employee.public'].search([('name', '=',row[0][0])], limit=1)
            if partner_id:
                user_tz = pytz.timezone(partner_id.tz)
                
                check_in = datetime.combine(row[0][1].to_pydatetime(),datetime.strptime(str(row[1]), "%H:%M:%S").time())
                check_out = datetime.combine(row[0][1].to_pydatetime(),datetime.strptime(str(row[2]), "%H:%M:%S").time())
#                 raise Warning(zz)
#                 raise Warning(datetime.now(dd.timezone.utc).astimezone().tzinfo)
                            
#                 check_out_utc = pytz.utc.localize(check_out)
#                 check_in_utc = pytz.utc.localize(check_in)
#                 raise Warning(str(check_in)+str(check_in_utc))
#                 local = pytz.timezone(tz)
#                 if user_tz in pytz.all_timezones:
#                     old_tz = pytz.timezone('UTC')
#                     new_tz = pytz.timezone(user_tz)
#                     check_in = old_tz.localize(check_in).astimezone(new_tz)
                tz = pytz.timezone(self.env.user.tz)
                check_in_tz = datetime.strptime(check_in.astimezone(tz).strftime("%H:%M"), "%H:%M")
                if first:
                    self.env['hr.attendance'].create({'employee_id': partner_id.id,'check_in': check_in_tz, 'check_out': check_out})
                    first=False
#         for __, row in df.iterrows():
#             partner_id = self.env['hr.employee.public'].search([('name', '=',row.loc['First Name'])], limit=1)
# #             print(str(row.loc['First Name']) + str(row.loc['Last Name']))
#             if partner_id:
        
#                 check_in = datetime.strptime(str(row.loc['Date']) +" "+ str(row.loc['Time']), "%d/%m/%Y %H:%M")
#                 self.env['hr.attendance'].create({'employee_id': partner_id.id,'check_in': check_in,'check_out': check_out})
        