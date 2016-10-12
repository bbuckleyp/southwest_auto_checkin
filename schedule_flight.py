#!/usr/bin/env python

import argparse
import checkin
import logging
import time
import apscheduler.events as events
from apscheduler.schedulers.background import BackgroundScheduler

def sched_listener(event):
    if event.code == events.EVENT_SCHEDULER_STARTED:
        print "SCHEDULER was started"
    elif event.code == events.EVENT_JOB_EXECUTED:
        print "JOB was executed successfully"
    elif event.code == events.EVENT_JOB_ERROR:
        print "JOB raised an exception during execution"

def main():
    # Declaring Arguments to Parse
    parser = argparse.ArgumentParser(description="Checkin a user to a respective Southwest Airlines flight on a specified date")
    parser.add_argument("-n", "--now", action="store_true", help="Checkin the user right now")
    parser.add_argument("FirstName", help="The user's First Name")
    parser.add_argument("LastName", help="The user's Last Name")
    parser.add_argument("ConfirmationNumber", help="The user's Confirmation Number")
    parser.add_argument("Date", help="The date of the flight (yyyy-mm-dd)")
    parser.add_argument("Time", help="The time of the flight (hh:mm)")
    args = parser.parse_args()


    # Initializing logging
    logging.basicConfig(filename='schedule_checkin.log', filemode='w', level=logging.DEBUG) 
    logging.info('Started')
    logging.info('Name: {} {}, Confirmation Number: {} Date-Time {} {}'.format(args.FirstName, args.LastName,
        args.ConfirmationNumber, args.Date, args.Time))


    # Checkin now or submit to scheduler
    if args.now:
        print "checking in now..."
        logging.info('Checking in now')
        checkin.checkin(args.FirstName, args.LastName, args.ConfirmationNumber)
    else:
        # Initializing variables for apscheduler
        sched = BackgroundScheduler()
        sch_date_time = args.Date + " " + args.Time
        user_info = [args.FirstName, args.LastName, args.ConfirmationNumber]

        logging.info('Scheduling checkin time/date')

        # scheduling job
        sched.add_listener(sched_listener)
        sched.add_job(checkin.checkin, args = user_info, trigger='date', next_run_time=sch_date_time)
        sched.start()

    # Checking if job was completed, if so then exit
    while sched.get_jobs():
        time.sleep(10)

    logging.info('Finished')

if __name__ == "__main__":
    main()
