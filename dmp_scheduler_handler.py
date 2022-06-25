#!/usr/bin/env python
# coding: utf-8
from util.dmp_worker import DMP_schedule_worker

def run_DMP_scheduler():
    worker = DMP_schedule_worker()
    schedule_datetime_list = worker.get_schedule_datetime_list()
    available_row_index_list = worker.get_alive_row_index_list(schedule_datetime_list)

    for available_row_index in available_row_index_list:
        row_value = worker.get_row_values(available_row_index)
        status = row_value[13]
        if '批准' in status:
            worker.handle_scheduler_by_row_value(row_value)

def run_all(event,context):
    run_DMP_scheduler()


if __name__ == "__main__":
    run_all("","")
    