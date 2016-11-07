#!/usr/bin/env python

import checkin
import logging
import time
import ConfigParser
import os
from pytz import utc
import apscheduler.events as events
from apscheduler.schedulers.background import BackgroundScheduler

def parse_inputs():
    """Parses through the input file and extracts the user data"""
    config = ConfigParser.ConfigParser()
    config.read([os.path.expanduser('./sw_data.txt')])

    # cycling through the input file and extracting the data
    first_name = []
    last_name = []
    confirmation = []
    email = []
    datetime = []
    num_users = config.get('info', 'num_users')
    for i in range(int(num_users)):
        first_name.append(config.get('user{}'.format(i+1), 'first_name'))
        last_name.append(config.get('user{}'.format(i+1), 'last_name'))
        confirmation.append(config.get('user{}'.format(i+1), 'confirmation'))
        email.append(config.get('user{}'.format(i+1), 'email'))
        datetime.append(config.get('user{}'.format(i+1), 'datetime'))

    retval = {'first_name': first_name, 'last_name': last_name, 'confirmation': confirmation, 'email': email, 'datetime': datetime}
    return retval

def sched_listener(event):
    if event.code == events.EVENT_SCHEDULER_STARTED:
        print "SCHEDULER was started"
    elif event.code == events.EVENT_JOB_EXECUTED:
        print "JOB was executed successfully"
    elif event.code == events.EVENT_JOB_ERROR:
        print "JOB raised an exception during execution"

def main():
    # Initializing logging
    logging.basicConfig(filename='schedule_checkin.log', filemode='w', level=logging.DEBUG) 

    # Reading input file and determining users that need to be checked in 
    user_data = parse_inputs()

    # Submit user data to scheduler
    # TODO START HERE
    sched = BackgroundScheduler(timezone=utc)
    print len(user_data['first_name'])
    for i in range(len(user_data['first_name'])):
        user_info = [user_data['first_name'][i], user_data['last_name'][i] , user_data['confirmation'][i], user_data['email'][i]]
        logging.info('Scheduling checkin time/date')

        # scheduling job
        sched.add_listener(sched_listener)
        print user_data['datetime'][i]
        sched.add_job(checkin.checkin, args = user_info, trigger='date', next_run_time=user_data['datetime'][i])
        logging.info("Adding job to scheduler for user: {}".format(user_data['first_name'][i]))
        #logging.info("Adding job to scheduler for user: " + user_info['first_name'][i])

    # Checking if job was completed, if so then exit
    logging.info("Starting scheduler")
    sched.start()
    while sched.get_jobs():
        time.sleep(10)

    logging.info('Finished')

if __name__ == "__main__":
    main()
