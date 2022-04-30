from __future__ import division
import json
import math
import csv
import os
from scipy.spatial import distance
import numpy as np
from numpy import trapz
from scipy.integrate import simps
import matplotlib.pyplot as plt

def line(p1,p2):
	A = (p1[1] - p2[1])
	B = (p2[0] - p1[0])
	C = (p1[0]*p2[1] - p2[0]*p1[1])
	return A,B,-C

def intersection(L1, L2):
	D  = L1[0]*L2[1] - L1[1]*L2[0]
	Dx = L1[2]*L2[1] - L1[1]*L2[2]
	Dy = L1[0]*L2[2] - L1[2]*L2[0]
	if D != 0:
		x = Dx / D
		y = Dy / D
		return x,y
	else:
		return False

def find_nearest(array, value):
	idx = (np.abs(array-value)).argmin()
	if array[idx] - value == 0:
		return ([idx])
	elif array[idx] - value < 0:
		return ([idx, idx+1])
	else:
		return ([idx-1, idx])

def get_second(s, ftr = [3600,60,1]):
	return sum([a*b for a,b in zip(ftr, map(float, s.split(':')))])

def get_parameters(m=""):
	# for parameters below, only include trials with more than 10 points (at least 5 unique points) and when there was no touch_up in the middle of the trial (participant did not realse finger)
	if len(df_choice[i]["coor"+m]) > 0:
		#recode time into 101 time bins and coor to [0,0] at start and [1,1] at end
		timestamp = []
		temp_time = []
		coor_ab = []
		for j in d["time"+m]:
			temp_time.append(j)
		timestamp = np.linspace(temp_time[0], temp_time[-1], num=101)
		d["timestamp"] = timestamp
		# reverse the x and y-axis for the vertical conditions
		if d["condition"] == "left" or d["condition"] == "right":
			for index in range(len(d["coor"+m])):
				d["coor"+m][index] = [d["coor"+m][index][1], d["coor"+m][index][0]]
		start = [d["coor"+m][0][0], d["coor"+m][0][1]]
		end = [d["coor"+m][-1][0], d["coor"+m][-1][1]]
		for c in range(len(d["timestamp"])):
			idx = find_nearest(d["time"+m], d["timestamp"][c])
			if (len(idx) == 1) or (d["time"+m][idx[1]] - d["time"+m][idx[0]] == 0):
				coor = [(d["coor"+m][idx[0]][0] - start[0]) / (end[0] - start[0]), (d["coor"+m][idx[0]][1] - start[1]) / (end[1] - start[1])]
			else:
				prop = (d["timestamp"][c] - d["time"+m][idx[0]]) / (d["time"+m][idx[1]] - d["time"+m][idx[0]])
				x_temp = d["coor"+m][idx[0]][0] + (d["coor"+m][idx[1]][0] - d["coor"+m][idx[0]][0]) * prop
				y_temp = d["coor"+m][idx[0]][1] + (d["coor"+m][idx[1]][1] - d["coor"+m][idx[0]][1]) * prop
				coor = [(x_temp - start[0]) / (end[0] - start[0]), (y_temp - start[1]) / (end[1] - start[1])]
			coor_ab.append(coor)
		d["coor_ab"+m] = coor_ab

		# separate x and y values
		if d["coor"+m] != []:
			for j in d["coor"+m]:
				# reverse back when extract raw x and y
				if d["condition"] == "left" or d["condition"] == "right":
					d["coor_x"+m].append(j[1])
					d["coor_y"+m].append(j[0])
				else:
					d["coor_x"+m].append(j[0])
					d["coor_y"+m].append(j[1])
			for j in d["coor_ab"+m]:
				d["coor_x_ab"+m].append(j[0])
				d["coor_y_ab"+m].append(j[1])
				if d["resp"] != "":
					if d["resp"] == d["stim"][0]:
						d["coor_x_ab_direction"+m].append(-j[0])
					else:
						d["coor_x_ab_direction"+m].append(j[0])
				else:
					d["coor_x_ab_direction"+m].append(j[0])
				d["coor_y_ab_direction"+m].append(j[1])
				

		# max deviation
		deviation = []
		R = []
		L1 = line(d["coor_ab"+m][-1], d["coor_ab"+m][0])
		x1, y1 = d["coor_ab"+m][-1]
		x2, y2 = d["coor_ab"+m][0]
		k1 = (y1 - y2) / (x1 - x2)
		for j in d["coor_ab"+m]:
			x0, y0 = j
			k2 = -k1
			b2 = y0 - k2 * x0
			L2 = line([x0, y0], [0, b2])
			r = intersection(L1, L2)
			R.append(r)
			dst = distance.euclidean(j ,r)
			if r != False:
				#only calculate the bulge ones
				if r[1] > y0:
					dst = dst * (-1)
			deviation.append(dst)
		Max = max(deviation)
		Min = min(deviation)
		if abs(Max) >= abs(Min):
			MD = Max
		else:
			MD = Min
		idx_MD = deviation.index(MD)
		d["MD"+m] = MD
		d["y_MD"+m] = d["coor_ab"+m][idx_MD][1]
		d["intersection_point"] = R[idx_MD]

		# min_distance (minimum distance to the unchosen option)
		dst_to_unchosen = []
		for j in d["coor_ab"+m]:
			target = [-1, 1]
			dst = distance.euclidean(j, target)
			dst_to_unchosen.append(dst)
		min_distance = min(dst_to_unchosen)
		d["min_distance"+m] = min_distance

		# number of choice commitments
		AOI = []
		L1_L = line([-1, 0], [0, 1])
		L1_R = line([1, 0], [0, 1])
		k_L = -1
		k_R = 1
		for j in d["coor_ab"+m]:
			x0, y0 = j
			if x0 > 0:
				b2 =  y0 - k_R * x0
				L2 = line(j, [0, b2])
				r = intersection(L1_R, L2)
				#print(r)
				if r != False:
					if r[1] < y0:
						AOI.append(1)
					else:
						AOI.append(0)
				else:
					AOI.append(0)
			elif x0 < 0:
				b2 = y0 - k_L * x0
				L2 = line(j, [0, b2])
				r = intersection(L1_L, L2)
				#print(r)
				if r != False:
					if r[1] < y0:
						AOI.append(-1) 
					else:
						AOI.append(0)
				else:
					AOI.append(0)
			else:
				AOI.append(0)
		count = 0
		for j in range(len(AOI)-1):
			count += abs(AOI[j+1] - AOI[j])
		commitment = (count + 1) / 2
		d["commitment"+m] = commitment

		# complexity on x-direction and y-direction
		seq_x = [d["coor"+m][0][0]]
		seq_y = [d["coor"+m][0][1]]
		delta_x = []
		delta_y = []
		for j in range(len(d['coor'+m])-1):
			delta_x.append(d['coor'+m][j+1][0] - d['coor'+m][j][0])
			delta_y.append(d['coor'+m][j+1][1] - d['coor'+m][j][1])
		for j in range(len(delta_x)-1):
			if delta_x[j] == 0:
				k = j - 1
				while k >= 0:
					if delta_x[k] != 0:
						if delta_x[k] > 0:
							delta_x[j] = 0.0001
						elif delta_x[k] < 0:
							delta_x[j] = -0.0001
						break
					k -= 1
			if delta_y[j] == 0:
				k = j - 1
				while k >= 0:
					if delta_y[k] != 0:
						if delta_y[k] > 0:
							delta_y[j] = 0.0001
						elif delta_y[k] < 0:
							delta_y[j] = -0.0001
						break
					k -= 1
		for j in range(len(delta_x)-1):
			product_x = delta_x[j] * delta_x[j+1]
			product_y = delta_y[j] * delta_y[j+1]
			if product_x < 0:
				seq_x.append(d['coor'+m][j+1][0])
			if product_y < 0:
				seq_y.append(d['coor'+m][j+1][1])
		seq_x.append(d['coor'+m][-1][0])
		seq_y.append(d['coor'+m][-1][1])
		distance_x = []
		distance_y = []
		for j in range(len(seq_x)-1):
			distance_x.append(seq_x[j+1] - seq_x[j])
		for k in range(len(seq_y)-1):
			distance_y.append(seq_y[k+1] - seq_y[k])
		d['x_flip'+m] = len(distance_x) - 1
		d['y_flip'+m] = len(distance_y) - 1
		d['distance_x'+m] = distance_x
		d['distance_y'+m] = distance_y


		#velocity relative location/ms & acceleration relative location/(ms*ms)
		velocity = []
		acceleration = []
		abs_acce = []
		v_time = []
		acce_time = []
		for j in range(len(d['coor_ab'+m])-1):
			v = distance.euclidean(d['coor_ab'+m][j],d['coor_ab'+m][j+1])/(abs(d['timestamp'][j]-d['timestamp'][j+1])*1000)
			v_time.append(d['timestamp'][j+1]*1000)
			velocity.append(v)

		for n in range(len(velocity)-1):
			acce = (velocity[n+1]-velocity[n])/((d['timestamp'][n+2]-d['timestamp'][n+1])*1000)
			acce_time.append(d['timestamp'][n+2]*1000)
			acceleration.append(acce)

		max_velocity = max(velocity)
		d['max_velocity'+m] = max_velocity
		for j in acceleration:
			abs_acce.append(abs(j))
		max_acceleration = max(abs_acce)         
		d['max_acceleration'+m] = max_acceleration

		# AUC
		dx = d['timestamp'][1] - d['timestamp'][0]
		y_coors = []
		x_coors = []
		for j in range(len(d['coor_ab'+m])):
			ycoord = d['coor_ab'+m][j][0]
			x_coors.append(ycoord)
			ycoord = d['coor_ab'+m][j][1]
			y_coors.append(ycoord)
		d['AUC'+m] = trapz(y_coors, x_coors)

		# instaneous movement angles
		d["IMA"+m] = []
		for j in range(len(d['coor_ab'+m])-1):
			x_change = d['coor_x_ab_direction'+m][j+1] - d['coor_x_ab_direction'+m][j]
			y_change = d['coor_y_ab_direction'+m][j+1] - d['coor_y_ab_direction'+m][j]
			if x_change != 0 or y_change != 0:
				IMA_temp = math.atan2(x_change, y_change) * 180 / math.pi
				if abs(IMA_temp) > 90:
					if IMA_temp < 0:
						IMA_temp += 180
					else:
						IMA_temp -= 180
				IMA_current = abs(IMA_temp) * np.sign(x_change)
			else:
				IMA_current = -1
			d["IMA"+m].append(IMA_current)

		# angles from the origin (as computed in Sullivan (2015)'s)
		d["angle"+m] = []
		for j in range(len(d['coor_ab'+m])):
			angle_temp = math.atan2(d["coor_x_ab_direction"+m][j], d["coor_y_ab_direction"+m][j]) * 180 / math.pi
			if abs(angle_temp) > 90:
				if angle_temp < 0:
					angle_temp += 180
				else:
					angle_temp -= 180
			angle_current = abs(angle_temp) * np.sign(d["coor_x_ab_direction"+m][j])
			d["angle"+m].append(angle_current)

	else:
		d["coor_ab"+m] = []
		d["MD"+m] = -1
		d["y_MD"+m] = -1
		d["commitment"+m] = -1
		d["min_distance"+m] = -1
		d["x_flip"+m] = -1
		d["y_flip"+m] = -1
		d["distance_x"+m] = []
		d["distance_y"+m] = []
		d["max_velocity"+m] = -1
		d["max_acceleration"+m] = -1
		d["AUC"+m] = -1
		d["IMA"+m] = []
		d["angle"+m] = []

food_list = ["Sushi", "Chips", "Banana", "Pear", "Radish", "Bell pepper", "Donuts", "Mars", "French fries", "KinderBueno"]

## save data as CSV file
f = csv.writer(open("D:\\PhD\\Projects\\Mouse-tracking_4.0\\Analysis data\\data_merged.csv", "wb+"), delimiter=";")

f.writerow(["ppn", "age", "gender", "length", "weight", "hand", "diet", "diet_text", "allergies", "allergies_text", "goal_health", "hunger", "vegan",
		"tsc1", "tsc2", "tsc3", "tsc4", "tsc5", "tsc6", "tsc7", "tsc8", "tsc9", "tsc10", "tsc11", "tsc12", "tsc13",
		"condition", "direction", "trial_NO", "stim", "stim_1", "stim_2", "health_1","taste_1","health_2","taste_2", "choice",
		"AUC", "MD", "y_MD", "commitment", "min_distance", "max_velocity", "max_acceleration", "x_flip", "distance_x", "y_flip", "distance_y", "RT", "drag_time", "hold_time", "angle", "IMA",
		"coor_x", "coor_y", "coor_x_ab", "coor_y_ab", "coor_x_ab_direction", "coor_y_ab_direction", "AUC2", "MD2", "y_MD2", "commitment2", "min_distance2", "max_velocity2", "max_acceleration2", "x_flip2", "distance_x2", "y_flip2", "distance_y2",
		"drag_time2", "hold_time2", "angle2", "IMA2", "coor_x2", "coor_y2", "coor_x_ab2", "coor_y_ab2", "coor_x_ab_direction2", "coor_y_ab_direction2", "events"]) 

## load data
os.chdir("D:\\PhD\\Projects\\Mouse-tracking_4.0\\Analysis data\\JSON\\")
for folder in os.listdir("D:\\PhD\\Projects\\Mouse-tracking_4.0\\Analysis data\\JSON\\"):
	os.chdir("D:\\PhD\\Projects\\Mouse-tracking_4.0\\Analysis data\\JSON\\"+folder)
	if os.path.isdir('D:\\PhD\\Projects\\Mouse-tracking_4.0\\Analysis data\\JSON\\'+folder+'\\plots\\') == False:
		os.makedirs('D:\\PhD\\Projects\\Mouse-tracking_4.0\\Analysis data\\JSON\\'+folder+'\\plots\\')
	print(folder)
	with open(folder+"_rating.json") as json_data:
		df_rating = json.load(json_data)
	with open(folder+"_choice_up.json") as json_data:
		df_choice_up = json.load(json_data)
	with open(folder+"_choice_down.json") as json_data:
		df_choice_down = json.load(json_data)
	with open(folder+"_choice_left.json") as json_data:
		df_choice_left = json.load(json_data)
	with open(folder+"_choice_right.json") as json_data:
		df_choice_right = json.load(json_data)
	if folder != "p30": # participant 30 did not complete the practice trials
		with open(folder+"_movement.json") as json_data:
			df_practice = json.load(json_data)
	else:
		df_practice = {}
		# make an empty data for participant 30 in the practice trials
		for i in range(10):
			df_practice["practice_TL_"+str(i)] = {"pos":"", "coor":[], "time":[], "coor2":[], "time2":[], "events":[], "leave_time":""}
			df_practice["practice_BL_"+str(i)] = {"pos":"", "coor":[], "time":[], "coor2":[], "time2":[], "events":[], "leave_time":""}
			df_practice["practice_TR_"+str(i)] = {"pos":"", "coor":[], "time":[], "coor2":[], "time2":[], "events":[], "leave_time":""}
			df_practice["practice_BR_"+str(i)] = {"pos":"", "coor":[], "time":[], "coor2":[], "time2":[], "events":[], "leave_time":""}

	with open(folder+"_survey.json") as json_data:
		df_survey = json.load(json_data)

	df_choice = df_choice_up
	df_choice = dict(df_choice, **df_choice_down)
	df_choice = dict(df_choice, **df_choice_left)
	df_choice = dict(df_choice, **df_choice_right)
	df_choice = dict(df_choice, **df_practice)

	## extract MT parameters based on the event-tracking
	for i in df_choice.keys():
		if i.find("trial_") != -1 or (i.find("practice_") != -1 and i.find("_practice_") == -1 and i.find("practice_trial") == -1):
			d = df_choice[i]

			# trial number, condition, and order of condition
			d["trial_no"] = int(i[i.rfind("_")+1:])
			if i.find("trial_") != -1:
				d["condition"] = i[i.find("_")+1:i.rfind("_")]
			else:
				d["condition"] = i[0:i.find("_")]

			# dragging time
			if d["time2"] != []:
				for k in range(len(d["time2"])):
					d["time2"][k] = get_second(d["time2"][k])

			if d["time"] != []:
				d["drag_time"] = d['time'][-1] - d['time'][0]
				d["hold_time"] = d["time"][1] - d["time"][0]
				d["drag_time2"] = d["time2"][-1] - d["time2"][0]
				for k in range(1, len(d["coor2"])):
					if d["coor2"][k][0] != d["coor2"][k-1][0] or d["coor2"][k][1] != d["coor2"][k-1][1]:
						break
				d["hold_time2"] = d["time2"][k] - d["time2"][0]
			else:
				d["drag_time"] = -1
				d["hold_time"] = -1
				d["drag_time2"] = -1
				d["hold_time2"] = -1

			# RT (time between screens)
			if d["leave_time"] != "":
				if d["trial_no"] != 0:
					d["RT"] = get_second(d["leave_time"]) - get_second(df_choice[i[0:i.rfind("_")+1]+str(d["trial_no"]-1)]["leave_time"])
				else:
					if i.find("up") != -1:
						d["RT"] = get_second(d["leave_time"]) - get_second(df_choice_up["instruction_trial"]["leave_time"])
					elif i.find("down") != -1:
						d["RT"] = get_second(d["leave_time"]) - get_second(df_choice_down["instruction_trial"]["leave_time"])
					elif i.find("left") != -1:
						d["RT"] = get_second(d["leave_time"]) - get_second(df_choice_left["instruction_trial"]["leave_time"])
					elif i.find("right") != -1:
						d["RT"] = get_second(d["leave_time"]) - get_second(df_choice_right["instruction_trial"]["leave_time"])
					elif i.find("TL") != -1:
						d["RT"] = get_second(d["leave_time"]) - get_second(df_practice["instruction_practice_TL"]["leave_time"])
					elif i.find("BL") != -1:
						d["RT"] = get_second(d["leave_time"]) - get_second(df_practice["instruction_practice_BL"]["leave_time"])
					elif i.find("TR") != -1:
						d["RT"] = get_second(d["leave_time"]) - get_second(df_practice["instruction_practice_TR"]["leave_time"])
					elif i.find("BR") != -1:
						d["RT"] = get_second(d["leave_time"]) - get_second(df_practice["instruction_practice_BR"]["leave_time"])
			else:
				d["RT"] = -1

			# run the get_parameters function to extract parameters based on both tracking methods
			d["coor_x"] = []
			d["coor_y"] = []
			d["coor_x_ab"] = []
			d["coor_y_ab"] = []
			d["coor_x_ab_direction"] = []
			d["coor_y_ab_direction"] = []
			d["coor_x2"] = []
			d["coor_y2"] = []
			d["coor_x_ab2"] = []
			d["coor_y_ab2"] = []
			d["coor_x_ab_direction2"] = []
			d["coor_y_ab_direction2"] = []
			if i.find("practice_") != -1:
				# add empty string for variables in practice trials so the same function can process the data
				d["resp"] = "" 
				d["stim"] = ""
			get_parameters(m="")
			get_parameters(m="2")	

			## additional variables
			# choice direction
			if i.find("trial_") != -1:
				if d["resp"] != "":
					if d["resp"] == d["stim"][0]:
						if i.find("up") != -1 or i.find("left") != -1:
							d["direction"] = "TL"
						elif i.find("down") != -1:
							d["direction"] = "BL"
						elif i.find("right") != -1:
							d["direction"] = "TR"
					else:
						if i.find("up") != -1:
							d["direction"] = "TR"
						elif i.find("down") != -1 or i.find("right") != -1:
							d["direction"] = "BR"
						elif i.find("left") != -1:
							d["direction"] = "BL"
				else:
					d["direction"] = ""
			
				# other choice variables
				d["taste_1"] = -1
				d["health_1"] = -1
				d["taste_2"]  = -1
				d["health_2"] = -1
				if d["stim"] != "":
					index_1 = d["stim"][0]
					index_2 = d["stim"][1]
					d["stim_1"] = food_list[int(index_1)]
					d["stim_2"] = food_list[int(index_2)]
					if d["resp"] == d["stim"][0]:
						d["choice"] = d["stim_1"]
					else:
						d["choice"] = d["stim_2"]

					# ratings
					for j in df_rating.keys():
						if j.find("rating") != -1:
							e = df_rating[j]
							if e["stim"] == str(index_1):
								d["taste_1"] = int(e["ratingT"])
								d["health_1"] = int(e["ratingH"])
							if e["stim"] == str(index_2):
								d["taste_2"] = int(e["ratingT"])
								d["health_2"] = int(e["ratingH"])
			else:
				d["direction"] = d["pos"]
				d["stim"] = ""
				d["stim_1"] = ""
				d["stim_2"] = ""
				d["choice"] = ""
				d["health_1"] = ""
				d["health_2"] = ""
				d["taste_1"] = ""
				d["taste_2"] = ""

			## write data
			f.writerow([folder, df_survey["survey1"]["age"], df_survey["survey1"]["gender"], df_survey["survey1"]["length"], df_survey["survey1"]["weight"], df_survey["survey1"]["hand"], 
				df_survey["survey2"]["diet"], df_survey["survey2"]["dietText"], df_survey["survey2"]["allergies"], df_survey["survey2"]["allergiesText"], 
				df_survey["survey3"]["health"], df_survey["survey3"]["hunger"], df_survey["survey3"]["vegan"], 
				df_survey["tsc1"]["Q1"], df_survey["tsc1"]["Q2"], df_survey["tsc1"]["Q3"], df_survey["tsc1"]["Q4"], df_survey["tsc2"]["Q1"], df_survey["tsc2"]["Q2"], df_survey["tsc2"]["Q3"], 
				df_survey["tsc2"]["Q4"], df_survey["tsc3"]["Q1"], df_survey["tsc3"]["Q2"], df_survey["tsc3"]["Q3"], df_survey["tsc3"]["Q4"], df_survey["tsc4"]["Q1"],
				d["condition"], d['direction'], d["trial_no"], d["stim"], d["stim_1"], d["stim_2"], d["health_1"], d["taste_1"], d["health_2"], d["taste_2"], d["choice"],
				d["AUC"], d["MD"], d["y_MD"], d["commitment"], d["min_distance"], d["max_velocity"], d["max_acceleration"], d["x_flip"], d["distance_x"], d["y_flip"], d["distance_y"], d["RT"], d["drag_time"], d["hold_time"], d["angle"], d["IMA"],
				d["coor_x"], d["coor_y"], d["coor_x_ab"], d["coor_y_ab"], d["coor_x_ab_direction"], d["coor_y_ab_direction"], d["AUC2"], d["MD2"], d["y_MD2"], d["commitment2"], d["min_distance2"], d["max_velocity2"], d["max_acceleration2"], d["x_flip2"], d["distance_x2"], d["y_flip2"],
				d["distance_y2"], d["drag_time2"], d["hold_time2"], d["angle2"], d["IMA2"], d["coor_x2"], d["coor_y2"], d["coor_x_ab2"], d["coor_y_ab2"], d["coor_x_ab_direction2"], d["coor_y_ab_direction2"], d["events"]]) 

			## make the plots
			plt.scatter(d['coor_x'], d['coor_y'], color="b")
			plt.scatter(d['coor_x_ab'], d['coor_y_ab'], color='r')
			plt.scatter(d['coor_x2'], d['coor_y2'], color="b", marker='+')
			plt.scatter(d['coor_x_ab2'], d['coor_y_ab2'], color='r', marker='+')
			plt.text(0.7, 0.15, s='AUC = '+str(round(d["AUC"], 2))+"/"+str(round(d["AUC2"], 2)))
			plt.text(0.7, 0.1, s='MD = '+str(round(d["MD"], 2))+"/"+str(round(d["MD2"], 2)))
			plt.text(0.7, 0.05, s='x-flip = '+str(round(d["x_flip"], 1))+"/"+str(round(d["x_flip2"], 1)))
			plt.text(0.7, 0, s='drag_time = '+str(round(d["drag_time"], 2))+"/"+str(round(d["drag_time2"], 2)))
			plt.text(0.7, -0.05, s='commitment = '+str(round(d["commitment"], 1))+"/"+str(round(d["commitment2"], 1)))
			plt.text(0.7, -0.1, s='min_distance = '+str(round(d["min_distance"], 2))+"/"+str(round(d["min_distance2"], 2)))
			plt.savefig('D:\\PhD\\Projects\\Mouse-tracking_4.0\\Analysis data\\JSON\\'+folder+'\\plots\\'+i+".png")
			plt.close()
