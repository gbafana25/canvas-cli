#!/usr/bin/python3
import requests
from datetime import datetime, date, timezone 
from zoneinfo import ZoneInfo
import json


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
	if(month_due == month and day_due >= day):
			return True
	else:
		return False
	"""
	if(month_due > month and year == year_due):
		return True
	elif(month_due == month and year == year_due and day_due >= day):
		return True
	else:
		return False
	"""

def get_course_name(n, token, base):
	headers = {"Authorization": "Bearer " + str(token).strip()}
	d = requests.get(base+"api/v1/courses/"+n, headers=headers)
	s = json.loads(d.text)
	print("\033[1;35m--", s['name'], "--\033[0m")



def get_assignments(token, config, base, time_zone):
	headers = {"Authorization": "Bearer " + str(token).strip()}
	for c in range(len(config)):
		get_course_name(str(config[c]), token, base)
		# paginatation required (per_page) to show all assignments
		alist = requests.get(base+"api/v1/courses/" + str(config[c]) + "/assignments?per_page=60", headers=headers)
		obj = json.loads(alist.text)
		for a in range(len(obj)):
			# don't show assignments without due date or haven't been submitted
			if(obj[a]['due_at'] == None or obj[a]['has_submitted_submissions']):
				#print(obj[a]['name'], "No due date")
				pass
			else:
				due = datetime.strptime(obj[a]['due_at'], "%Y-%m-%dT%H:%M:%S%z")
				cst = due.astimezone(time_zone)
				if(after_today(due.month, due.day, due.year)):
					print(obj[a]['name'], cst.month, "/", cst.day, "/", cst.year)	
			

# test function for specific urls/endpoints
def get_courses(token):
	headers = {"Authorization": "Bearer " + str(token).strip()}
	al = requests.get(base_url+"api/v1/courses/4080/", headers=headers)
	o = json.loads(al.text)
	print(o['name'])
	"""
	for i in range(len(o)):
		print(o[i]['id'], o[i]['name'])
	#print("Courses showing: " + str(len(o)))
	print(str(len(o)))
	"""
	
		

tok = get_token()
conf = get_config()
tz = ZoneInfo(conf['time_zone'])
get_assignments(tok, conf['courses'], conf['base_url'], tz)
#get_courses(tok)


