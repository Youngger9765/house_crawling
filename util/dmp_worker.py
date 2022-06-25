from util.gsheet_worker import GsheetWorker
import re
from datetime import datetime, date, time, timezone, timedelta
from util.notification import LineWorker


class DMP_schedule_worker:
    def __init__(self):
        self.tz = timezone(timedelta(hours=8))
        self.sheet_key = '1zmsEScm3fyDSPo0RgRsgsHsjIWAtmHgDp8nHJUP0ZNQ'
        self.appointments_tab_name = 'appointments'
        self.name_line_token_map = "name_line_token_map"
        self.g_worker = GsheetWorker(self.sheet_key)
        self.appointments_sheet = self.g_worker.get_sheet(self.sheet_key).worksheet(self.appointments_tab_name)
        self.name_line_token_map_sheet = self.g_worker.get_sheet(self.sheet_key).worksheet(self.name_line_token_map)
        self.schedule_datetime_col_index = 7
    
    def get_dt(self, datetime_text):
        datetime_patern = r"(.*) 年 (.*) 月 (.*) 日 (pm|am) (.*):(.*)"
#         datetime_text = '2022 年 6 月 23 日 pm 8:30'
        datetime_tuple_list = re.findall(datetime_patern, datetime_text)[0]
        year = int(datetime_tuple_list[0])
        month = int(datetime_tuple_list[1])
        day = int(datetime_tuple_list[2])
        am_pm = datetime_tuple_list[3]
        hour = int(datetime_tuple_list[4]) + 12 if am_pm == "pm" else int(datetime_tuple_list[4])
        minute = int(datetime_tuple_list[5])
        d = date(year, month, day)
        t = time(hour, minute)
        dt = datetime.combine(d, t, tzinfo=self.tz)
        
        return dt
    
    def get_schedule_datetime_list(self):
        appointments_sheet = self.appointments_sheet
        schedule_datetime_list = appointments_sheet.col_values(self.schedule_datetime_col_index)
        
        dt_list = []
        for dt_text in schedule_datetime_list:
            if dt_text == 'Start Time':
                dt_list.append('')
            else:
                dt = self.get_dt(dt_text)
                dt_list.append(dt)
            
        return dt_list
    
    def get_alive_row_index_list(self, schedule_datetime_list):
        now = datetime.now(tz=self.tz)
        available_row_index_list = []
        for i, v in enumerate(schedule_datetime_list):
            if v == '':
                continue
            elif v > now:
                available_row_index_list.append(i+1)
                
        return available_row_index_list
        
    def get_row_values(self, row_index):
        appointments_sheet = self.appointments_sheet
        return appointments_sheet.row_values(row_index)
    
    def get_line_token_by_name(self, name):
        line_token = ""
        name_line_token_map_sheet = self.name_line_token_map_sheet
        name_list = name_line_token_map_sheet.col_values(2)
        for i, v in enumerate(name_list):
            if v == name:
                line_token = name_line_token_map_sheet.row_values(i+1)[2]
        
        return line_token
    
    def handle_scheduler_by_row_value(self, row_value):
        customer_name = row_value[1]
        employee_name = row_value[4]
        service = row_value[5]
        start_time = row_value[6]
        request_content = row_value[15]

        start_time_dt = self.get_dt(start_time)
        now = datetime.now(tz=self.tz)
        dt_diff_days = (start_time_dt - now).days

        # 一天前提醒
        if dt_diff_days >= 1 and dt_diff_days < 2:
            for name in [customer_name, employee_name]:
                try:
                    msg = f"Hi {name}， \n"
                    msg += "這裡是 Dream More 小幫手 \n"
                    msg += "預約上課提醒，建議設定鬧鈴及行事曆 \n"
                    msg += "\n"
                    msg += f"課堂： {service} \n"
                    msg += f"時間： {start_time} \n"
                    msg += f"需求： {request_content} \n"
                    msg += f"Mentor: {employee_name} \n"
                    msg += f"Mentee: {customer_name} \n"
                    self.send_line_notification(name, msg) 
                except:
                    pass

        # 一天內提醒
        elif dt_diff_days < 1:
            for name in [customer_name, employee_name]:
                try:
                    msg = f"Hi {name}， \n"
                    msg += "這裡是 Dream More 小幫手 \n"
                    msg += "今天上課提醒，建議設定鬧鈴及行事曆，並準時進入教室，感謝你的配合 \n"
                    msg += "\n"
                    msg += f"課堂： {service} \n"
                    msg += f"時間： {start_time} \n"
                    msg += f"需求： {request_content} \n"
                    msg += f"Mentor: {employee_name} \n"
                    msg += f"Mentee: {customer_name} \n"
                    self.send_line_notification(name, msg)
                except:
                    pass
        
    def send_line_notification(self, name, msg):
        line_notify_token = self.get_line_token_by_name(name)
        line_worker = LineWorker(line_notify_token)
        line_worker.send_notification(msg)