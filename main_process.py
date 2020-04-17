#!/usr/bin/env python3

# adam's "before you run this script in production environment" checklist:
# 	1. check send_log_email(), make sure recipients and open path delim are correct
# 	2. check get_engine_info(), make sure path to db properties file is correct
# 	3. check if __name__ == "__main__", make sure it's only running main()
# 	4. You're all set!!

# standard library
import os
import re
import sys
import time
import logging
import smtplib
from email.message import EmailMessage
from datetime import datetime
# third-party
import pandas as pd
from sqlalchemy import create_engine
# first-party
import conndb
import download_bot


def send_log_email(log_file_name):
    with open(os.getcwd() + "\\" + log_file_name) as fp:
        msg = EmailMessage()
        msg.set_content(fp.read())

    msg['Subject'] = "Scraper: Failed!"
    msg['From'] = "someguy@gmail.com"
    msg['To'] = [
        "someguy@gmail.com",
        "madame.sysadmin@gmail.com"
    ]

    server = smtplib.SMTP(
        host="localhost",
        port=1025
    )
    server.send_message(msg)
    server.quit()


def get_engine_info():
    props = conndb.parse_props(
        "propspath\\db_config\\config.properties"
    )
    flavor = "postgresql"
    hostname = props["db_host"]
    dbname = props["db_name"]
    username = props["db_user"]
    password = props["db_password"]
    port = props["db_port"]

    engine_info = "{flavor}://{user}:{password}@{host}:{port}/{database}".format(
        flavor=flavor,
        user=username,
        password=password,
        host=hostname,
        port=port,
        database=dbname
    )

    return engine_info


def main():
    """Cleans up data and pushes it to the db"""
    # setup
    logging_filename = "main_process.txt"
    try:
        os.remove(logging_filename)
    except OSError:
        pass
    logging.basicConfig(filename=logging_filename, level=logging.WARNING)
    engine = create_engine(get_engine_info())
    print("Connection established.")
    # get download directory path from download bot
    download_dir = str()
    i = 5
    random_wait_base = 1
    while i > 0:
        try:
            print("STARTING SUBPROCESS: ATTEMPT {}".format(6-i))
            print("{")
            download_dir = download_bot.main(random_wait_base)
            print("}")
            print("Download directory from bot:\n\t", download_dir)
            if i < 5:
                logging.warning("DOWNLOAD BOT SUCCESS AFTER {} FAILED ATTEMPTS".format(5-i))
            break
        except:
            print("}")
            except_msg = "DOWNLOAD BOT FAILED: ATTEMPT {}".format(6-i)
            i -= 1
            random_wait_base += 1
            print(except_msg)
            logging.exception(except_msg)
            if i == 0:
                send_log_email(logging_filename)
                sys.exit()

    # clean up the data
    try:
        # construct df
        time.sleep(5)
        csv_list = list()
        print("Files in download directory:\n\t")
        print(os.listdir(download_dir))
        for csv_path in os.listdir(download_dir):
            # scrubbing em dashes as they are non-ascii
            old_path = download_dir + "\\" + csv_path
            new_path = old_path.split(".")[0] + "_ascii.csv"
            print("Scrubbing original file:\n\t{}".format(old_path))
            with open(new_path, 'w') as outfile:
                with open(old_path, 'r') as infile:
                    oldtext = infile.read()
                    newtext = re.sub("Eco.*Electronic", 'Eco - Electronic', oldtext)
                    outfile.write(newtext)
            print("Reading in scrubbed file:\n\t{}".format(new_path))
            df = pd.read_csv(new_path, sep=",", skiprows=6)
            df = df.loc[:4999, :]
            csv_list.append(df)
            time.sleep(5)
        print("Cleaning up the data...")
        df = pd.concat(csv_list, ignore_index=True, axis=0)
        # de-dup, drop rows without imo
        df = df.drop_duplicates('IMO Number')
        df = df.dropna(subset=['IMO Number'])
        # filter out Ro-Ro (deprecated, but left in just in case download bot messes up somehow)
        df = df.loc[df['Type'].str.contains('Container', na=False)]
        df = df.drop('Type', axis=1)
        df = df.rename(
            columns={
                'IMO Number': 'imo',
                'Name': 'name',
                'Owner': 'owner',
                'Operator': 'operator',
                'Built Date': 'built',
                'Draught (m)': 'draught',
                'LOA (m)': 'loa',
                'Beam (m)': 'beam',
                'Gear (Ind)': 'gear',
                'MMSI (Maritime Mobile Service Identity)': 'mmsi',
                'Speed (knots)': 'speed',
                'TEU': 'teu',
                'Reefer TEU Capacity': 'teu_reefer',
                'TPC': 'tpc',
                'Consumption (tpd)': 'consumption',
                'Tanker Category': 'fuel_type',
                'SOx Scrubber Details': 'sox1_type',
                'SOx Scrubber 1 Retrofit Date': 'sox1_date',
                'Dwt': 'dwt',
                'Eco - Electronic Engine': 'eco_type'
            }
        )
        df['scrape_date'] = datetime.now().strftime('%Y-%m-%d')
        df['built'] = df['built'].apply(lambda x: datetime.strptime(x, '%d-%b-%Y'))
        # push to db
        print("Pushing data to cont.ship_static...")
        df.to_sql('xxxx_static', engine, schema='xxxx', if_exists='append', index=False)
        print("Clarksons Container Ship Process complete.")
    except:
        logging.exception("DATA CLEANUP FAILED.")
        send_log_email(logging_filename)
        sys.exit()


if __name__ == "__main__":
    main()
    # send_log_email("main_process.txt")
