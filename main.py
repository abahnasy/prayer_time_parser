import os
import csv

import pdfplumber

"""
Notes: use 24 Hour time format

Based on the calendar from https://www.islamisches-zentrum-muenchen.de/links-downloads/
"""


#============================================#
# USER INPUT DATA
#============================================#
CAL_DIR = "./cals"
# MONTH_LENGTH = 31
START_DAY = 'Di'
YEAR = 2022
# MONTH = 2

#============================================#
# Helper Functions
#============================================#
def get_end_time(start_time):
	h, m = [int(x) for x in start_time.split(":")]
	if m > 50:
		m = (m+10)%60
		h = (h+1)%24
	else:
		m += 10

	return "{:02d}:{:02d}".format(h,m)

def valid_time_slot(start_time):
	if start_time is None:
		return False
	if not len(start_time) == 5: 
		return False
	if start_time[2] != ":":
		return False
	return True

def clean_row(row):
	""" if returned None, should skip this row in table, otherwise the return will be the 6 times needed as a list of string
	"""
	if row[0] is None or row[0] == "":
		return None
	times = []
	for entry in row:
		if valid_time_slot(entry):
			times.append(entry)
	assert len(times) == 6, "wrong parsing for the row"
	return times

#============================================#
# MAIN LOGIC
#============================================#

# parse calendar pdf file dir
calendar_list = sorted(os.listdir(CAL_DIR))
month_length = -1


# ASSERTIONS
TAGES = ['Di', 'Mi', 'Do', 'Fr', 'Sa', 'So', 'Mo']
PRAYERS = ['Fajr', 'Sunrise', 'Duhr', 'Asr', 'Maghrib', 'Isaa']

# create the annual calendar file
f = open('./calendar.csv', 'w')
cal = csv.writer(f)
header = ['Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'All Day Event', 'Description', 'Location']
cal.writerow(header)


# loop over every month
for month_idx, month_cal in enumerate(calendar_list):

	# assertions
	curr_day_no = 1
	curr_day_name = None

	with pdfplumber.open("./cals/{}".format(month_cal)) as pdf:
		first_page = pdf.pages[0]
		tables = first_page.extract_tables()[0]
		
			
		# assertions, get the last day of the current month
		for table in tables[::-1]:
			if table[0] is None or table[0] == "":
				continue
			else:
				month_length = int(table[1])
				break

		for row in tables:
			times = clean_row(row)
			if times is None:
				continue
			if curr_day_no == 1:
				curr_day_name = row[0]
				curr_day_name_idx = TAGES.index(curr_day_name)
				
				assert curr_day_name_idx >= 0 and curr_day_name_idx <= 6
			# assertion on parsed rows
			if int(row[1]) == curr_day_no and \
				int(row[1]) <= month_length and \
					row[0] == curr_day_name:
				# loop over prayers
				prayer_parser_counter = 0
				for idx, entry in enumerate(times):					
					# form a new entry
					cal_event = []
					subject =PRAYERS[prayer_parser_counter]
					prayer_parser_counter += 1
					start_date = "{}/{}/{}".format(month_idx+1, curr_day_no, YEAR)
					start_time = entry
					end_date = start_date
					end_time = get_end_time(entry) # increase start time by 10 mins
					cal_event.append(subject)
					cal_event.append(start_date)
					cal_event.append(start_time)
					cal_event.append(end_date)
					cal_event.append(end_time)
					cal_event.append("FALSE")
					cal_event.append("")
					cal_event.append("")
					cal.writerow(cal_event)
				assert prayer_parser_counter == 6
				curr_day_no += 1
				curr_day_name_idx = (curr_day_name_idx +1) % len(TAGES)
				curr_day_name = TAGES[curr_day_name_idx]






# curr_day_name_idx = 0

# curr_day_name = START_DAY









	
