from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from .forms import OriginForm , DestForm
import json
import requests
from lxml import html
from collections import OrderedDict
import argparse
import numpy as np
from sklearn import datasets, linear_model
import urllib2
import simplejson
from collections import OrderedDict
def pre_index(request):
	count = 0
	within=0
	if request.method == 'GET':
		count = count + 1
		origin =  request.GET.get("origin")
		dest = request.GET.get("dest")
		date = request.GET.get("date")
		
		print origin , dest,date
		if (origin != None and dest != None and date != None):
			within = 1
			date = date.split("-")
			date = date[1]+"/"+date[2]+"/"+date[0]
			json_data = Parse_Data(origin,dest,date)
			flight_cost = Parse_Json(json_data,request)
			if(len(flight_cost)>0):
				weather_info = weather(origin,request)
				cost = [];flight=[];ActTime=[];Actstop=[];ArrTime=[];DepTime=[];DurTime=[];ADDTime=[]
				w_date=[];temp=[];hum=[];pre=[]
				for j in range(0,len(weather_info[0])):
					w_date.append(weather_info[0][j])
					temp.append(weather_info[1][j])
					hum.append(weather_info[2][j])
					pre.append(weather_info[3][j])
				for i in range(0,len(flight_cost[1])):
					dummy = []
					cost.append(float(flight_cost[1][i]))
					flight.append((flight_cost[0][i]))
					ActTime.append(round(float(flight_cost[2][i]),2))
					Actstop.append(int(flight_cost[3][i]))
					
					flight_cost[0][i] = str(flight_cost[0][i])[3:len(flight_cost[0][i])-3]
					dummy.append((flight_cost[0][i]))
					dummy.append(str(flight_cost[5][i]))
					dummy.append(str(flight_cost[4][i]))
					dummy.append(str(flight_cost[6][i]))
					ADDTime.append(dummy)
				Suggest=[]
				Cheap=[]
				cheap = cost.index(min(cost))
				fR = (flight_cost[0][cheap])
				pR = cost[cheap]
				dR = str(flight_cost[5][cheap])
				aR = str(flight_cost[4][cheap])
				dur = str(flight_cost[6][cheap])
				sR = int(flight_cost[3][cheap])
				Cheap.append(fR);Cheap.append(pR);Cheap.append(dR);Cheap.append(aR);Cheap.append(dur);Cheap.append(sR)
				Suggest.append(Cheap)
				Cheap=[]
				cheap = ActTime.index(min(ActTime))
				fR = (flight_cost[0][cheap])
				pR = cost[cheap]
				dR = str(flight_cost[5][cheap])
				aR = str(flight_cost[4][cheap])
				dur = str(flight_cost[6][cheap])
				sR = int(flight_cost[3][cheap])
				Cheap.append(fR);Cheap.append(pR);Cheap.append(dR);Cheap.append(aR);Cheap.append(dur);Cheap.append(sR)
				Suggest.append(Cheap)
				Cheap=[]
				cheap = Actstop.index(min(Actstop))
				fR = (flight_cost[0][cheap])
				pR = cost[cheap]
				dR = str(flight_cost[5][cheap])
				aR = str(flight_cost[4][cheap])
				dur = str(flight_cost[6][cheap])
				sR = int(flight_cost[3][cheap])
				Cheap.append(fR);Cheap.append(pR);Cheap.append(dR);Cheap.append(aR);Cheap.append(dur);Cheap.append(sR)
				Suggest.append(Cheap)



	if within==0:
		return render(request,'UpdIndex.html')
	elif len(flight_cost)>0:
		return render(request,'NextToSearch.html',{'Origin':origin.upper(),'Dest':dest.upper(),'flight':flight,'cost':cost,'time':ActTime,
			'stop':Actstop,'AddTime':ADDTime,'w_date':w_date,'temp':temp,'hum':hum,'pre':pre,'suggest':Suggest})
	else:
		return render(request,'ErrorIndex.html')


def Parse_Data(source,destination,date):
	for i in range(5):
		try:
			url = "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com".format(source,destination,date)
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
			response = requests.get(url, headers=headers, verify=False)
			parser = html.fromstring(response.text)
			json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")
			raw_json =json.loads(json_data_xpath[0] if json_data_xpath else '')
			flight_data = json.loads(raw_json["content"])

			flight_info  = OrderedDict() 
			lists=[]
			for i in flight_data['legs'].keys():
				total_distance =  flight_data['legs'][i].get("formattedDistance",'')
				exact_price = flight_data['legs'][i].get('price',{}).get('totalPriceAsDecimal','')

				departure_location_airport = flight_data['legs'][i].get('departureLocation',{}).get('airportLongName','')
				departure_location_city = flight_data['legs'][i].get('departureLocation',{}).get('airportCity','')
				departure_location_airport_code = flight_data['legs'][i].get('departureLocation',{}).get('airportCode','')
				
				arrival_location_airport = flight_data['legs'][i].get('arrivalLocation',{}).get('airportLongName','')
				arrival_location_airport_code = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCode','')
				arrival_location_city = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCity','')
				airline_name = flight_data['legs'][i].get('carrierSummary',{}).get('airlineName','')
				
				no_of_stops = flight_data['legs'][i].get("stops","")
				flight_duration = flight_data['legs'][i].get('duration',{})
				flight_hour = flight_duration.get('hours','')
				flight_minutes = flight_duration.get('minutes','')
				flight_days = flight_duration.get('numOfDays','')

				if no_of_stops==0:
					stop = "Nonstop"
				else:
					stop = str(no_of_stops)+' Stop'

				total_flight_duration = "{0} days {1} hours {2} minutes".format(flight_days,flight_hour,flight_minutes)
				departure = departure_location_airport+", "+departure_location_city
				arrival = arrival_location_airport+", "+arrival_location_city
				carrier = flight_data['legs'][i].get('timeline',[])[0].get('carrier',{})
				plane = carrier.get('plane','')
				plane_code = carrier.get('planeCode','')
				formatted_price = "{0:.2f}".format(exact_price)

				if not airline_name:
					airline_name = carrier.get('operatedBy','')
				
				timings = []
				for timeline in  flight_data['legs'][i].get('timeline',{}):
					if 'departureAirport' in timeline.keys():
						departure_airport = timeline['departureAirport'].get('longName','')
						departure_time = timeline['departureTime'].get('time','')
						arrival_airport = timeline.get('arrivalAirport',{}).get('longName','')
						arrival_time = timeline.get('arrivalTime',{}).get('time','')
						flight_timing = {
											'departure_airport':departure_airport,
											'departure_time':departure_time,
											'arrival_airport':arrival_airport,
											'arrival_time':arrival_time
						}
						timings.append(flight_timing)

				flight_info={'stops':stop,
					'ticket price':formatted_price,
					'departure':departure,
					'arrival':arrival,
					'flight duration':total_flight_duration,
					'airline':airline_name,
					'plane':plane,
					'timings':timings,
					'plane code':plane_code
				}
				lists.append(flight_info)
			sortedlist = sorted(lists, key=lambda k: k['ticket price'],reverse=False)
			return sortedlist
		
		except ValueError:
			print ("Retrying...")
			
		return [{"error":"failed to process the page",}]

"""def Parse_Json(request):
	return render(request,'charts.html')"""
def Parse_Json(data,request):
	flight_cost = []
	flight=[]
	cost=[]
	ActTime=[]
	Actstop=[]
	ArrTime=[]
	DepTime=[]
	DurTime=[]
	if "error" not in data[0].keys():
		for entry in data:
			time = entry["flight duration"]
			time = time.split(" ")
			stop = entry["stops"].split(" ")
			if stop[0]=="Nonstop":
				stop=0
			else:
				stop = int(stop[0])
			Int_Time = int(time[0])*24*60 + int(time[2])*60 + int(time[4])
			Int_Time = float(Int_Time/60.0)
			Time = time[0]+"D:"+time[2]+"H:"+time[4]+"M"
			depTime = entry["timings"][0]
			arrTime = entry["timings"][len(entry["timings"])-1]
			UpDep = depTime["departure_time"]
			UpArr = arrTime["arrival_time"]
			DurT = time[0]+" DD: "+time[2]+" HH: "+time[4]+" MM: "
			UpDur = DurT
			if entry["plane"]+" "+entry["airline"]+"!@"+str(Time) not in flight:
				flight.append(entry["plane"]+" "+entry["airline"]+"!@"+str(Time))
				cost.append(entry["ticket price"])
				ActTime.append(Int_Time)
				Actstop.append(stop)
				ArrTime.append(UpArr)
				DepTime.append(UpDep)
				DurTime.append(DurT)
			#print flight,"***********************************************************"
		for each in range(0,len(flight)):
			flight[each]=flight[each].split("!@")
			flight[each].remove(flight[each][1])
		#print flight
		flight_cost.append(flight);flight_cost.append(cost);flight_cost.append(ActTime)
		flight_cost.append(Actstop);flight_cost.append(ArrTime);flight_cost.append(DepTime)
		flight_cost.append(DurTime)
	return flight_cost
def weather(dest,request):

	response = urllib2.urlopen("https://api.openweathermap.org/data/2.5/forecast?q={0}&appid=55828c01f13262a42977ba7c8f8f5329".format(dest))
	data = simplejson.load(response)
	
	print len(data["list"])
	date_temp=OrderedDict()
	date_humidity=OrderedDict()
	date_pre=OrderedDict()
	for i in range(0,len(data["list"])):
		parse = data["list"][i]["dt_txt"].split(" ")
		parse = str(parse[0])
		if (parse) not in date_temp.keys():
			date_temp[parse] = round(float(data["list"][i]["main"]["temp_max"]) - 273.15 , 2)
			date_humidity[parse] = round(float(data["list"][i]["main"]["humidity"]),2)
			date_pre[parse] = round(float(data["list"][i]["main"]["pressure"]),2)

		else:
			avg = date_temp[parse]+(float(data["list"][i]["main"]["temp_max"])-273.15)	
			date_temp[parse] = round(avg/2.0,2)
			avg_hum = date_humidity[parse]+float(data["list"][i]["main"]["humidity"])	
			date_humidity[parse] = round(avg_hum/2.0,2)
			avg_pre = date_pre[parse]+float(data["list"][i]["main"]["pressure"])	
			date_pre[parse] = round(avg_pre/2.0,2)
	#print date_temp
	#print date_pre
	#print date_humidity
	date=[]
	temp=[]
	hum=[]
	pre=[]
	for i in (date_temp):
		date.append(i)
		temp.append(date_temp[i])
		hum.append(date_humidity[i])
		pre.append(date_pre[i])
	#print date,temp,hum,pre
	weather_data=[]
	weather_data.append(date)
	weather_data.append(temp)
	weather_data.append(hum)
	weather_data.append(pre)
	return weather_data
