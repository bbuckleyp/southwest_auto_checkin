#!/usr/bin/env python

import requests
import time
import logging

def checkin(first_name, last_name, confirmation_number):#, email):
    """
    Function call to checkin the user to their respective Southwest Flight.
    """
    # declaring variables
    payload1 = {'confirmationNumber': confirmation_number, 'firstName': first_name, 'lastName': last_name}
    payload2 = {'confirmationNumber': confirmation_number, 'firstName': first_name, 'lastName': last_name}
    url0 = 'https://www.southwest.com'
    url1 = 'https://www.southwest.com/flight/retrieveCheckinDoc.html'
    url2 = 'https://www.southwest.com/flight/retrieveCheckinDoc.html'

    print first_name
    print last_name
    print confirmation_number


    # opening session (also acquires cookie)
    s = requests.Session()
    s.get(url0)
    logging.info('checkin.py: Session Open, Cookie Acquired')

    # checking in until successful
    success = 0
    while(success == 0):
        # making most critical POST request to southwest checkin form
        r = s.post(url1, data=payload1)
        logging.info('checkin.py: Checkin POST Made')

        # if checkin successful then make final POST
        if "Boarding Pass is more than 24 hours prior" in r.text:
            #s.post(url2, data=payload2)
            print "User checked in successfully"
            logging.info('checkin.py: User successfully checked in!')
            success = 1
        else: 
            print "Checkin failed...retrying"
            logging.warning('Checkin failed...retrying')
            time.sleep(1)

    s.close()
