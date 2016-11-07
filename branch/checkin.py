#!/usr/bin/env python

import requests
import time
import logging

def checkin(first_name, last_name, confirmation_number, email):
    """
    Function call to checkin the user to their respective Southwest Flight.
    """
    # declaring variables
    payload1 = {'confirmationNumber': confirmation_number, 'firstName': first_name, 'lastName': last_name}
    payload2 = {'checkinPassengers[0].selected': 'true', 'printDocuments': 'Check In'}
    payload3 = {'selectedOption': 'optionEmail', 'emailAddress': email, 'book_now': ''}

    url0 = 'https://www.southwest.com'
    url1 = 'https://www.southwest.com/flight/retrieveCheckinDoc.html'
    url2 = 'https://www.southwest.com/flight/selectPrintDocument.html'
    url3 = 'https://www.southwest.com/flight/selectCheckinDocDelivery.html'

    logging.info('checkin.py:')
    logging.info(first_name)
    logging.info(last_name)
    logging.info(confirmation_number)
    logging.info(email)

    # opening session (also acquires cookie)
    s = requests.Session()
    s.get(url0)
    logging.info('checkin.py: Session Open, Cookie Acquired')

    # checking in until successful
    success = 0
    while(success == 0 and success < 200):
        # making most critical POST request to southwest checkin form
        r = s.post(url1, data=payload1)
        logging.info('checkin.py: Checkin POST Made')

        # if checkin successful then make final POST requests
        if "Continue to Create Boarding Pass/Security Document?" in r.text:
            r = s.post(url2, data=payload2)
            if "checked in" in r.text:
                s.post(url3, data=payload3)
                logging.info('User successfully checked in!')
                success = 1
        else: 
            logging.warning('Checkin failed...retrying')
            time.sleep(1)

    s.close()
