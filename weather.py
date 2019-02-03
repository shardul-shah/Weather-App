# Created and documented by: Shardul Shah
# Weather API used: https://openweathermap.org/api 
# The weather API does not belong to me, and full credit goes to them for the data provided.

import json # weather API provides JSON data
import urllib.request # for making network connections
import contextlib # can close url connections I open on the network more securely
import time
from datetime import timedelta, datetime
import math # need for some math functions for GUI
import tkinter as tk # read tkinter documentation before using, pretty indepth module
import sqlite3

# TODO: fix Tkinter layout for weather information for 1 day only. *FIXME

# a line of ######### indicates the start of a new function.

####################################################################################################################################################################################
def temp_converter(temp, from_unit, to_unit): 
	# only handles C, F, K
	# temp is any temperature with from_unit
	# from_unit and to_unit is a character which is either = 'C', 'F' or 'K'
	if from_unit == 'C' and to_unit == 'F':
		return (temp*(9/5) + 32)
		
	if from_unit == 'C' and to_unit == 'K':
		return (temp+273.15)
		
	if from_unit == 'F' and to_unit == 'C':
		return (temp-32)*(5/9)
		
	if from_unit == 'F' and to_unit == 'K':
		return ((temp-32)*5/9 + 273.15)
			
	if from_unit == 'K' and to_unit == 'C':
		return temp-273.15    
		
	if from_unit == 'K' and to_unit == 'F':
		return ((temp-273.15)*9/5 + 32)
		
####################################################################################################################################################################################        
def ip_and_region(url):
	# url is the url which contains json-formatted IP information
	
	# proper and safe closing of URL connection using contextlib
	with contextlib.closing(urllib.request.urlopen(url)) as response: #opens the URL (urlopen(url) that is given in string format
		data = json.load(response) # the JSON document which is in the the webpage is read and stored in data as a DICTIONARY format.
	
	# should be noted above, the contextlib.closing approach ensures proper closure even in the presence of any exceptions, and is safe and good practice. from: https://stackoverflow.com/questions/1522636/should-i-call-close-after-urllib-urlopen

	ip=data['ip'] 
	org=data['org']
	city = data['city'] # since data is a DICTIONARY thanks to json.load(), we just retrieve the information for the specific key each time. i.e. data['city']
	country=data['country']
	region=data['region']

	print("\nYour IP detail\n") 
	print('IP : {4} \nRegion : {1} \nCountry : {2} \nCity : {3} \nOrg : {0}'.format(org,region,country,city,ip)) # prints the IP address related information in the format() specified

	#Above is from: 
	# from https://stackoverflow.com/questions/24678308/how-to-find-location-with-ip-address-in-python (open)
	
	location_info = [city, country]
	return location_info
	
#####################################################################################################################################################################################       
	
def weather(api_url, main_flag, location_list, day_flag):
	# note: location_list is a list where location_list[0] = city, location_list[1] = country
	# function returns -1 if there is an HTTPError (invalid city or country name)
	# otherwise, function returns a list of the appropriate weather information.
	
	# main_flag = 0 : user only wants 1 day of information
	# main_flag = 1: user wants all 5 days of information
		
	try:
		url_resp = urllib.request.urlopen(api_url)
	   
	except urllib.request.HTTPError:
		return -1
		
	#finally:
	# empty for now
	   
	#if url_resp.getcode() == 404: # if URL does not exist, there is only one reason for that... #https://stackoverflow.com/questions/1726402/in-python-how-do-i-use-urllib-to-see-if-a-website-is-404-or-200
#        return -1 # error return code

	with contextlib.closing(url_resp) as weather_response:
		weather_data = json.load(weather_response)
		# weather_data is a dictionary with keys: "cod", "message", "cnt", "list", "city".
		# the key list's value is a list of dictionaries, with one dictionary for each date-time, differing by 3 hours

	# print(weather_data["list"][0]) :
	# list has all the weather information. The index corresponds for the date+time the weather information is for. It appears there is information for every 3 hours for this API. [0] is the most recent date-time, [1] is most recent date-time + 3, and so on.

	# USE SQLITE3 TO SAVE THE DATA FOR THE INTO TABLES, OUTPUT THE RECENT (next few days/time) data into the table, save the tables, and store them in a file each run of the program. and print the most important (i.e next day/current) forecast like this:
	
	counter = 0
	for each in weather_data["list"]:
		counter+=1
	# counter = num of dt in list; that is, number of weather entries. The API used has weather information for every 3 hours, for 5 days from the current date-time.
  
	day_weather_info = []
	
	if main_flag == 0:
		day_weather_info.append("The forecast for {0}, {1}: ".format(location_list[0], location_list[1]))
		for i in range(counter):
		
			if (day_flag_to_date(day_flag) == time.strftime('%Y-%m-%d', time.localtime(weather_data["list"][i]['dt']))):
			
				# NOTE: dt is the accurate time for the temperature measurement, not dt_time
				time_string = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(weather_data["list"][i]['dt']))
				# the above line helps time_string PRINT a time in a format like: 2017-10-30 00:00:00 , from the given epoch time in time.localtime(), which is provided in the API
				# The method strftime() converts a tuple or struct_time representing a time as returned by gmtime() or localtime() to a string as specified by the format argument.
				temp_cels = round(temp_converter(weather_data["list"][i]["main"]["temp"], 'K', 'C'))
				sea_level_pressure = round((weather_data["list"][i]["main"]["sea_level"])/10, 1) # dividing by 10 to convert from Hectopascal to Kilopascal
				humidity = weather_data["list"][i]["main"]["humidity"]
				description = weather_data["list"][i]["weather"][0]["description"]
				cloud_percent = weather_data["list"][i]["clouds"]["all"]
				wind_speed = weather_data["list"][i]["wind"]["speed"]
				
				output_str = "\nAt {2} local time is: \nTemperature (Celsius): {3} \nPressure (kPa): {4} \nHumidity (%): {5} \nCloud Cover (%): {6} \nWind Speed (km/h): {7} \nThe weather condition outside: {8}".format(location_list[0], location_list[1], time_string, temp_cels, sea_level_pressure, humidity, cloud_percent, wind_speed, description)   
				
				day_weather_info.append(output_str)
						
	else:
		day_weather_info.append("The forecast for {0}, {1}: ".format(location_list[0], location_list[1]))
		
		for i in range(counter):
				# NOTE: dt is the accurate time for the temperature measurement, not dt_time
				time_string = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(weather_data["list"][i]['dt']))
				# the above line helps time_string PRINT a time in a format like: 2017-10-30 00:00:00 , from the given epoch time in time.localtime(), which is provided in the API
				# The method strftime() converts a tuple or struct_time representing a time as returned by gmtime() or localtime() to a string as specified by the format argument.
				temp_cels = round(temp_converter(weather_data["list"][i]["main"]["temp"], 'K', 'C'))
				sea_level_pressure = round((weather_data["list"][i]["main"]["sea_level"])/10, 1) # dividing by 10 to convert from Hectopascal to Kilopascal
				humidity = weather_data["list"][i]["main"]["humidity"]
				description = weather_data["list"][i]["weather"][0]["description"]
				cloud_percent = weather_data["list"][i]["clouds"]["all"]
				wind_speed = weather_data["list"][i]["wind"]["speed"]
				
				output_str = "\nAt {2} local time: \nTemperature (Celsius): {3} \nPressure (kPa): {4} \nHumidity (%): {5} \nCloud Cover (%): {6} \nWind Speed (km/h): {7} \nThe weather condition outside: {8}".format(location_list[0], location_list[1], time_string, temp_cels, sea_level_pressure, humidity, cloud_percent, wind_speed, description)
	
				day_weather_info.append(output_str)
				
	return day_weather_info


####################################################################################################################################################################################

	
def day_flag_to_date(day_flag):
	return (datetime.now()+timedelta(hours=24*(day_flag-1))).strftime("%Y-%m-%d")
	
def GUI(day_weather_info):
	root = tk.Tk() # root is the main Tkinter object, which every graphic will be based off of
	root.configure(background='#F2FA14')
	
	screen_width = root.winfo_screenwidth()
	screen_height = root.winfo_screenheight() 
	 
	#title_message = tk.Message(root, text="Results: ", background='#5AC8ED', fg='red', font=('Arial', 20, 'bold'), width='1000', justify='center').grid(row=0)
	#title_message.grid(row=0, column=1)
  
	# empty space at the top done by below line of code
	title_message = tk.Message(root, text="", bg='#F2FA14', fg='red', font=('Arial', 20, 'bold'), width=screen_width, justify='center').grid() # using as empty space at top for now
	#.grid() automatically puts a row below the last row in root. No need to specify which row.
	# background/bg and fg changes background and text color accordingly  
	# can also do title_message.grid() or simply remove title_message = 
	
 
	for i in range(len(day_weather_info)):    
		if i == 0 or i == 1 or i == 2 or i == 3:
		   row_num = 1
		   if i == 0:
			   col_num = 0
		   if i == 1:
			   col_num = 1
		   if i == 2:
			   col_num = 2
		   if i == 3:
			   col_num = 3
	
		else:
			if i == 4:
				tk.Message(root, text="", bg='#F2FA14', fg='red', font=('Arial', 20, 'bold'), width=screen_width, justify='center').grid() # using as filler
			row_num = 3
			if i == 4:
				col_num = 0
			if i == 5:
				col_num = 1
			if i == 6:
				col_num = 2
			if i == 7:
				col_num = 3
						
		tk.Message(root, text=day_weather_info[i], background='black', fg='yellow', aspect=80, width=(screen_width/4-20), highlightbackground = '#F2FA14', justify='center',borderwidth = 3, padx=-2, relief='flat', font=('ms serif', 12, 'bold')).grid(row = row_num, column=col_num)
		# background/bg and fg changes background and text color accordingly              
			   
	#frame = tk.Frame(root, bg='black', height=1, width=screen_width)
	#frame.grid() # a frame is created in the row below the weather output. Use frame for various buttons. 
	# it's like calling create_rectangle or create_circle or something on a canvas
	
	#quit_button = tk.Button(root, text="QUIT", bg='#F2FA14', fg="black", activebackground='BLACK', command=quit, highlightbackground='BLACK').grid()   
	# add and modify quit button with this later. For now, none.      
			   
	end_message = tk.Message(root, text="", bg='#F2FA14', fg='red', font=('Arial', 20, 'bold'), width=screen_width, justify='center').grid() # using as filler space at the bottom for now 
	#.grid() automatically puts a row below the last row in root. No need to specify which row.
	 
	root.mainloop() # must be in end - infinite loop on the main Tkinter object to show results on screen	

####################################################################################################################################################################################

def divide_canvas(c_width, c_height, num_of_sections):
	# given the height and width of an area on a screen, divide the screen into num_of_sections number of SQUARE sections, and returns the section_width (= section_height)
	# 0 < num_of_sections <= 9
	
	area_section = (c_width*c_height)/num_of_sections
	section_height = math.sqrt(area_section)
	
	# note section_height = section_width, as section = square
	return section_height

####################################################################################################################################################################################    

def section_coord(section_height, section_num):
	# returns the (x,y) of the top left corner of the rectangle and (x,y) of the bottom right corner of the rectangle, respectively, as a list.
	# arguments: which section is passed in (section_num) and section_height (section_height = section_width), canvas_height and canvas_width
	# 0 <= section_num < 9
	
	if section_num == 0 or section_num == 1 or section_num == 2:
		left_top_y = 0*section_height
		x_iter= section_num
		
	elif section_num == 3 or section_num == 4 or section_num == 5:
		left_top_y = 1*section_height
		x_iter = section_num-3
		
	else: # if section_num == 6 or 7 or 8:
		left_top_y = 2*section_height
		x_iter = section_num-6  

	left_top_x = x_iter*section_height
	right_bottom_x = left_top_x + section_height
	right_bottom_y = left_top_y + section_height
	
	coord_list = [left_top_x, left_top_y, right_bottom_x, right_bottom_y]
	return coord_list
	
#################################################################################################################################################################################### 

def create_DB(conn):
	# For future database usage 
	c = conn.cursor()

	c.executescript(""" 
			

		""")

def main():

	conn = sqlite3.connect("weather.db")

	c = conn.cursor()
	c.execute('PRAGMA foreign_keys=ON;') 
	conn.commit()

	create_DB(conn)

	ip_url = 'http://ipinfo.io/json' #URL with json-formatted information about IP, from http://ipinfo.com 

	location = ip_and_region(ip_url)
	city = location[0]
	country = location[1]

	API_key = "872ef0432dbc6d8ab88c0f92d85d7746"
	API_url_domain = "http://api.openweathermap.org/data/2.5/forecast?q="
	API_appid = "&APPID=" + API_key
  
	api_url = API_url_domain + city + ',' + country + API_appid # you can do string contacenation in Python, like in JavaScript
	# format for string used:
	#http://api.openweathermap.org/data/2.5/forecast?q=Edmonton,CA&APPID={APIKEY}
	#http://api.openweathermap.org/data/2.5/forecast?q={cityname},{countrycode}&APPID={APIKEY}
	
   # api_url is where the information for this weather app is located.
	# it is important to note that api_url gives results in a JSON format by default
	#print(api_url)
	
	print("Welcome to the weather interface of this application.")
	print("As of now, weather data for the next five days can be shown.")
	
	while True:
		city_input_ques = "\nDo you want the weather for {0}, {1}? (y/n): ".format(city, country)
		home_city_input = input(city_input_ques)
		
		if home_city_input == 'n': 
			print("\nPlease enter the name of the country and city name you want the weather for.")
			print("Country codes also work (and are preferred).\nTo see your country's code, see \nhttps://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#QA\n")
			city = (input("City: ")).capitalize()
			country = (input("Country: ")).capitalize()
			
			location[0] = city
			location[1] = country
			
			api_url = api_url = API_url_domain + city + ',' + country + API_appid
			
			while weather(api_url, 1, location, -1) == -1:
				print("\nThe city or country name/code entered are incorrect.")
				print("Please recheck the info entered. To see country code, see \nhttps://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#QA")
				print("\nPlease enter the name of the country and city name you want the weather for.")
				city = (input("City: ")).capitalize()
				country = (input("Country: ")).capitalize()
				
				location[0] = city
				location[1] = country
			
				api_url = api_url = API_url_domain + city + ',' + country + API_appid
			
		all_info_input = input("\nDo you want all five days' weather? (y/n): ")
	
		i = 0
		if all_info_input == 'y':
			if i == 0:
			  print("\nWEATHER INFORMATION HERE: ") 
			  i+=1
			  
			day_weather_info = weather(api_url, 1, location, -1)
			for item in day_weather_info:
				print(item)
	
		else:
			#Note strftime converts a struct-time/tuple returned only by time.localtime() or gmtime(), to specified string.
			#datetime.now()+timedelta(hours=x) does not yield such a format, so format() should be used to yield a similar output for datetime()
			#However strftime() is its own function, which can also format tuples as returned by datetime.now() + timedelta(hours=x), by:              datetime.now().strftime('%H:%M:%S')
			# '{:%Y-%m-%d}'.format(datetime.now()+timedelta(hours=24)) formats the next day from now in the specified format. Note the first : is needed in '{:Y-%m-%d}'
		
			# can do the following with my day_flag_to_date function, but I want to experiment with different datetime/formatting functions:
			print("\nWhich day do you want the weather of?")
			print("Press 1 for: ", time.strftime("%Y-%m-%d", time.localtime()))    
			print("Press 2 for: ", '{:%Y-%m-%d}'.format(datetime.now()+timedelta(hours=24))) # this is how you progress 24 hours from the current date-time
			print("Press 3 for: ", (datetime.now()+timedelta(hours=24*2)).strftime("%Y-%m-%d"))
			print("Press 4 for: ", (datetime.now()+timedelta(hours=24*3)).strftime("%Y-%m-%d"))
			print("Press 5 for: ", (datetime.now()+timedelta(hours=24*4)).strftime("%Y-%m-%d"))
			day_flag = int(input("Press key now: ")) 
			# note datetime.now() is not in epoch time, but in rather a 9 index tuple full dt-info, as opposed to localtime() which returns 1 value - the epoch time
  
			day_weather_info = weather(api_url, 0, location, day_flag)
			
			i = 0
			for item in day_weather_info:
				if i == 0:
				  print("\nWEATHER INFORMATION HERE: ")
				  i+=1
				  
				print(item)
						 
			GUI(day_weather_info)
			print("\nSimply close the GUI (tkinter) Python window to continue using the application") 
			
			continue_input = input("\nDo you want to continue using the app? (y/n): ")
			
			if continue_input == 'y':
				continue
			else:
				conn.close()
				return    
	 
if __name__ == "__main__":
	main()    

