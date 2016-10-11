#!/usr/bin/env python

import argparse
import checkin
from apscheduler.scheduler.BlockingScheduler import BlockingScheduler


if __name__ == "__main__":
    # Declaring Arguments to Parse
    parser = argparse.ArgumentParser(description="Checkin a user to a respective Southwest Airlines flight on a specified date")
    parser.add_argument("-n", "--now", action="store_true", help="Checkin the user right now")
    parser.add_argument("FirstName", help="The user's First Name")
    parser.add_argument("LastName", help="The user's Last Name")
    parser.add_argument("ConfirmationNumber", help="The user's Confirmation Number")
    parser.add_argument("Date", help="The date of the flight (yyyy-mm-dd)")
    parser.add_argument("Time", help="The time of the flight (hh:mm)")
    args = parser.parse_args()


    if args.now:
        print "checking in now..."
        checkin.checkin(args.FirstName, args.LastName, args.ConfirmationNumber)
    else:
        # scheduling based on date and time entered
        sched = BlockingScheduler()
        sch_date_time = args.Date + args.Time
        user_info = [args.FirstName, args.LastName, args.ConfirmationNumber]
        sched.add_job(checkin.checkin, args = user_info, trigger='date', next_run_time=sch_date_time)
