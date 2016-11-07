#!/usr/bin/env python

# import modules
import imaplib
import ConfigParser
import os
import email as Email
import pytz
import logging
import re
from datetime import datetime
from tzwhere import tzwhere # TODO IMPORT ONLY needed library
from geopy.geocoders import Nominatim



def read_config_data():
    """ Reads configuration file and returs data"""

    # Read the config file
    config = ConfigParser.ConfigParser()
    config.read([os.path.expanduser('./imap.config')])

    # Collecting data 
    hostname = config.get('Gmail', 'hostname')
    username = config.get('Gmail', 'username')
    password = config.get('Gmail', 'password')
    mailbox_id = config.get('Gmail', 'mailbox')

    return {"hostname":hostname, "username":username, "password":password, "mailbox_id":mailbox_id}

def open_connection(config):
    """ 
    Opens the connection to the IMAP server with information from the config file.
    Returns the IMAP connection instance.
    """

    # Connect to the server
    logging.info("Connecting to" + config["hostname"])
    connection = imaplib.IMAP4_SSL(config["hostname"])

    # Login to the account
    logging.info("Logging in as" + config["username"])

    try: 
        connection.login(config["username"], config["password"])
        logging.info("Successfully connected to SMP Email Server")
        return (True, connection)
    except:
        logging.critical("Cannot connect to the SMP Email Sever")
        return (False, connection)

def utc_time(time, city, state, date):
    """ Given a city, converts the time passed in to UTC"""

    # modules needed to convert time to UTC
    geolocator = Nominatim() 
    tz = tzwhere.tzwhere()

    #  Request longitutde/latitude values given a city input and find the corresponding timezone
    place, (lat, lng) = geolocator.geocode('{}, {}'.format(city, state))
    timezone = tz.tzNameAt(lat, lng)

    # Convert time to UTC datetime
    local = pytz.timezone(timezone)
    date_time = date + " " + time
    dt = datetime.strptime(date_time, "%m-%d-%Y %H:%M")
    local_dt = local.localize(dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt

def parse_email(body):
    """ Verifies that email is in correct format to read. Calls function to email user result."""

    # Iterate through each line in the email and count number of occurance of each. At the end it should equal
    first_name = []
    last_name = []
    confirmation = []
    email = []
    date = []
    city = []
    state = []
    time = []
    datetime = []

    body = body.splitlines()
    email_iterator = iter(body)

    # verifying the length of the email is at least enough information for one person and contains : or - separators 
    for line in email_iterator:
        if len(line.split(" ")) < 5 and "</div>" not in line:
            line = line.strip().lower() 

            # don't split if it's a city because it can have multiple words in a city (aka San Diego)
            if ':' in line or '-' in line:
                if "city" in line: 
                    city.append(re.split('[:-]', line)[-1].strip())
                elif "state" in line and '+' not in line:
                    state.append(re.split('[:-]', line)[-1].strip())
                else:
                    line = line.replace(" ", "")
                    if '>' not in line and '<' not in line:
    
                        if "firstname" in line or "first_name" in line: 
                            first_name.append(re.split('[: -]',line)[-1].upper())
                        elif "lastname" in line or "last_name" in line: 
                            last_name.append(re.split('[: -]',line)[-1].upper())
                        elif "confirmation" in line: 
                            confirmation.append(re.split('[: -]',line)[-1].upper()) 
                        elif "email" in line:
                            email.append(re.split('[: -]',line)[-1].upper()) 
                        elif "date" in line: 
                            l = re.split('[: -]', line, 1)
                            d = l[-1].replace('/', '-')
                            
                            # checking if year contains full 2016 etc not 16
                            d_temp = d.split('-')
                            if len(d_temp[-1]) < 4:
                                d_temp[-1] = "20" + d_temp[-1]
                                d = '-'.join(d_temp)
    
                            date.append(d) # making sure all days are in consistent format with '-' instead of '/'
                        elif "time" in line:
                            l = line.replace('-', ':').split(':')
                            hour = l[1]
                            minute = l[2]
                            
                            # checking if am/pm is delcared and putting in 24 hour format
                            if not l[-1].isdigit(): 
                                minute = minute[:-2] # taking off am/pm declaration
                                if "pm" in l[-1]: 
                                    hour = str(int(hour) + 12)
    
                            time.append(hour + ':' + minute)

    # checking if there's at least 1 value entered for all data fields and it's consistent
    print first_name, last_name, confirmation, date, time, city, state
    if first_name >= 1 and len(first_name) == len(last_name) == len(confirmation) == len(date) == len(time) == len(city) == len(state):
        # convert time, city, state, date to UTC datetimes
        for i in range(len(time)):
            datetime.append(utc_time(time[i], city[i], state[i], date[i]))

        retval = {"first_name":first_name, "last_name":last_name, "confirmation":confirmation, "email":email, "datetime":datetime}
        return True, retval
    else:
        return False, None
    
def email_user():
    return
        
def main():
    """
    Connects to the SMP Email Server. 
    Parses southwest flight data from inbox.
    Outputs data to text file.
    """
    # Initializing logging
    logging.basicConfig(filename='email_parse.log', filemode='w', level=logging.DEBUG) 

    # opening file now so it is blank if connection fails and scheduler sees there's no data
    f = open("sw_data.txt", "w")

    # Reading email config data and opening connection to SMP email server
    email_config = read_config_data()
    result, connection = open_connection(email_config)

    if result == False:
        print "Cannot connect to SMP Email Server right now"
        return

    # For the number of unseen emails, iterate through each one and extract data
    unread_count = int(connection.status(email_config["mailbox_id"], '(UNSEEN)')[1][0].split(" ")[2][0:1])
    total_count = int(connection.select(email_config["mailbox_id"], readonly=False)[1][0]) #NOTE - readonly = True will not mark as read

    # iterate through all unread emails
    num_users = 0
    for i in range(unread_count):
        # Extracting email body text data
        resp, email_data = connection.fetch(str(total_count - i), '(RFC822)')
        email_body = email_data[0][1]

        # parse though email body, collect data, check if format is valid. If format invalid, will return False and will email user
        result, email_data = parse_email(email_body)
        
        # TODO email_user()
        if result == False:
            # email user expected format
            email_user()
            print "FALSE return"
        else:
            # email user email recieved, data collected, scheduling 
            email_user()

            # output data to text file
            for j in range(len(email_data["first_name"])):
                num_users += 1
                f.write("[user{}]\n".format(num_users))
                f.write("first_name = " + email_data["first_name"][j] + '\n')
                f.write("last_name = " + email_data["last_name"][j] + '\n')
                f.write("confirmation = " + email_data["confirmation"][j] + '\n')
                f.write("email = " + email_data["email"][j] + '\n')
                f.write("datetime = " + str(email_data["datetime"][j]) + '\n\n')

    f.write("[info]\n")
    f.write("num_users = " + str(num_users) + '\n')
    f.close()

    connection.close()
    connection.logout()

    return


if __name__ == "__main__":
    main()
