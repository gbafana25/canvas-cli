#!/usr/bin/python3
import requests
from datetime import datetime, date, timezone 
from zoneinfo import ZoneInfo
import json
import sys


def setup_config(token):
	conf = open("config.json", "w+")
	url = input("Canvas URL (please include '/' at end): ")
	tzone = input("Time Zone (Country/City): ")
	s = input("Show assignments without due date [y/n]? ")
	show = False
	if s == 'y':
		show = True
	headers = {"Authorization": "Bearer " + str(token).strip()}
	al = requests.get(url+"api/v1/courses?per_page=50", headers=headers)
	o = json.loads(al.text)
	ids = []
	for i in range(len(o)):
		ids.append(o[i]['id'])
	s = json.dumps({"courses": ids, "base_url": url, "time_zone": tzone, "show_items_without_due_date":show})
	conf.write(s)
	conf.close()



def get_config():
	with open("config.json", "r") as c:
		courses = c.read()
		conf = json.loads(courses)

	return conf 

	
def get_token():
	with open("token", "r") as f:
		token = f.read()
	return token


def after_today(month_due, day_due, year_due):
	month = date.today().month 
	day =  date.today().day
	year = date.today().year
	if(month_due == month and day_due >= day and year_due == year):
			return True
	if(month_due == month+1 and year_due == year): 
		return True
	else:
		return False
	

def get_course_name(n, token, base):
	headers = {"Authorization": "Bearer " + str(token).strip()}
	d = requests.get(base+"api/v1/courses/"+n, headers=headers)
	s = json.loads(d.text)
	try:
		print("\033[1;35m--", s['name'], "--\033[0m")
	except KeyError:
		print("Course id "+str(s['id'])+" access restricted")
		raise KeyError
	


def get_assignments(token, config, base, time_zone, show):
	headers = {"Authorization": "Bearer " + str(token).strip()}
	for c in range(len(config)):
		try:
			get_course_name(str(config[c]), token, base)
			# paginatation required (per_page) to show all assignments
			alist = requests.get(base+"api/v1/courses/" + str(config[c]) + "/assignments?per_page=80", headers=headers)
			obj = json.loads(alist.text)
			for a in range(len(obj)):
				# don't show assignments without due date or haven't been submitted
				if obj[a]['due_at'] == None or obj[a]['has_submitted_submissions']:
					if show == True:
						print(obj[a]['name'], "No due date") 
					else:
						pass
				else:
					due = datetime.strptime(obj[a]['due_at'], "%Y-%m-%dT%H:%M:%S%z")
					cst = due.astimezone(time_zone)
					if(after_today(cst.month, cst.day, cst.year)):
						print(obj[a]['name'], "\033[1;32m", cst.month, "/", cst.day, "/", cst.year, "\033[0m")
		except KeyError:
			continue	
			

# test function for specific urls/endpoints
def get_courses(token, url):
	headers = {"Authorization": "Bearer " + str(token).strip()}
	al = requests.get(url+"api/v1/courses?per_page=50", headers=headers)
	o = json.loads(al.text)
	print(o)
	for i in range(len(o)):
		print(o[i]['id'], o[i]['name'])
	print(str(len(o)))
	
		
tok = get_token()

if(len(sys.argv) == 1):
	conf = get_config()
	tz = ZoneInfo(conf['time_zone'])
	get_assignments(tok, conf['courses'], conf['base_url'], tz, conf['show_items_without_due_date'])
elif(sys.argv[1] == "setup"):
	setup_config(tok)

