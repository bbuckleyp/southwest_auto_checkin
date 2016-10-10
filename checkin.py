#!/usr/bin/env python

# import libraries
import requests
import time


def checkin(first_name, last_name, confirmation_number, email):
    # debug variables
    first_name = 'Brandon'
    last_name = 'Buckley'
    confirmation_number = 'BY2FPW'

    # variables
    payload1 = {'confirmationNumber': confirmation_number, 'firstName': first_name, 'lastName': last_name}
    payload2 = {'confirmationNumber': confirmation_number, 'firstName': first_name, 'lastName': last_name}
    url0 = 'https://www.southwest.com'
    url1 = 'https://www.southwest.com/flight/retrieveCheckinDoc.html'
    url2 = 'https://www.southwest.com/flight/retrieveCheckinDoc.html'

    # opening session (also acquires cookie)
    s = requests.Session()
    s.get(url0)

    # checking in until successful
    success = 0
    while(success == 0):
        # making POST request to southwest checkin form
        r = s.post(url1, data=payload1)

        # check if checkin was successful
        if "Checkin successful" in r.text:
            s.post(url2, data=payload2)
            print "User checked in successfully"
            success = 1
        else: 
            time.sleep(5)

    # output results to a file to keep track of data

    # close session connection
    s.close()
