#!/usr/bin/env python
# coding: utf-8
import sys
from util.dmp_worker import DMP_schedule_worker
from util.notification import LineWorker

def run_DMP_scheduler(scheduler_type):
    line_notify_token = "Fms2ZdnfAf2us7knLNEdfTpb0ABbLHhnDcRbmzz3DQC"
    line_worker = LineWorker(line_notify_token)
    # notify
    message = f"開始今日 DMP 預約爬蟲: {scheduler_type}"
    line_worker.send_notification(message)

    worker = DMP_schedule_worker()
    schedule_datetime_list = worker.get_schedule_datetime_list()
    available_row_index_list = worker.get_alive_row_index_list(schedule_datetime_list)

    for available_row_index in available_row_index_list:
        row_value = worker.get_row_values(available_row_index)
        status = row_value[13]
        if '批准' in status:
            worker.handle_scheduler_by_row_value(row_value, scheduler_type)

def run_all(scheduler_type,context):
    run_DMP_scheduler(scheduler_type)

if __name__ == "__main__":
    scheduler_type = sys.argv[1]
    print(f"scheduler_type:{scheduler_type}")

    run_all(scheduler_type,"")
    