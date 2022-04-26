## load the libraries
from kivy.config import Config
Config.set('graphics', 'kivy_clock', 'interrupt')
Config.set('graphics', 'maxfps', '100')
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', 200)
Config.set('graphics', 'top',  50)
Config.write()

from kivy.app import App
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.core.window import Window
# adjust the window size to be the same as on the tablet
Window.size = (875, 500)
Window.borderless = True
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.uix.widget import Widget
from kivy.uix.behaviors import DragBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.metrics import sp, dp
from kivy.clock import Clock

#import random
import random
from random import shuffle, choice
from datetime import datetime
import os
import json


#checking push git
## Initiate some global variables
#This part combines all stimuli pairs in a list, with each option appearing left and right once, and randomizes them. Input the names of the images without the image extention here.
saveData = {}

path = "C:\\Users\\maxhi\\OneDrive\\Desktop\\Good_mouse\\Mousetrack\\TheApp\\Rating\\Data\\"
os.chdir(path)
with open("current_stim.json") as json_data:
	df = json.load(json_data)
#stimComb = df["up"] 
#stim comb,15= 1+5 = patato + paprika
#print(stimComb)
print(df)

#stimCombBase = df["baseline"]
#print(stimCombBase)
#print(stimComb4)
#test list to make testing more efficient
#for i in range(10):
#	stimRec
	
stimComb2 = ['15', '90', '92']
stimComb_base = df["Baseline"]
stimComb_cur =  df["Cursor"]
stimComb_rec =  df["Recommendation"]

#print(len(stimComb))

## Design some popups in case of incorrect inputs from the user
popup_username = Popup(title="Woops!", content=Label(text="Please type in your correct participant ID, e.g., '09'"), size_hint=(0.6, 0.6))

## Define class for login interface, to register user's names
class Login(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(Login, self).__init__(**kwargs)
		self.add_widget(Label(text="User Name", size_hint=(0.5, 0.3), pos_hint={"right":0.755, "top":0.9}, font_size=sp(55)))
		# get username
		self.username = TextInput(text="", multiline=False, size_hint=(0.6, 0.2), pos_hint={"right":0.8, "top":0.6}, font_size=sp(50))
		self.add_widget(self.username)
		self.button = Button(text="NEXT", size_hint=(0.6, 0.2), pos_hint={"right":0.8, "top":0.3}, font_size=sp(30))
		self.button.bind(on_press = self.auth)
		self.add_widget(self.button)
		#time point of leaving this page
		self.leave_time = ""

	# generate a JSON file for data storage and store username in the JSON files
	def auth(self, instance):
		if len(self.username.text) == 2 and self.username.text.isdigit() == True:
				self.leave_time = str(datetime.now().time())
				saveData["login"] = {"ppn":self.username.text, "leave_time": self.leave_time}
				App.get_running_app().root.current = "rec_instruct"
		else:
				popup_username.open()

# create an instance for Login with a name
login = Login(name="login")

## Define class for logout interface
class Logout(Screen, FloatLayout, App):
	def __init__(self, **kwargs):
		super(Logout, self).__init__(**kwargs)
		self.label = Label(text="", size_hint=(0.5, 0.1), pos_hint={"right":0.75, "top":0.6}, font_size=sp(18), color=(1,1,1,1), halign="center")
		self.button = Button(text="Save data and logout", pos_hint={"right":0.7, "top":0.2}, size_hint=(0.4, 0.1), font_size=sp(25), color=(1,1,1,1))
		self.button.bind(on_press=self.on_press)
		self.add_widget(self.label)
		self.add_widget(self.button)
		#time point of leaving this page
		self.leave_time = ""

	def getIns(self, ins):
		self.label.text = ins

	def on_press(self, instance):
		self.leave_time = str(datetime.now().time())
		saveData["logout"] = {"leave_time":self.leave_time}
		with open("C:\\Users\\maxhi\\OneDrive\\Desktop\\Good_mouse\\Mousetrack\\TheApp\\Choice_up\\Data\\p"+login.username.text+"_choice_up.json", 'w') as f: # modify according to your local path
			json.dump(saveData, f)
		App.get_running_app().stop()

ins_logout = "Please first save data and log out, and then ask the experimenter'\n"\
			"for what to do next."

# create an instance for Logout with a name
logout = Logout(name="logout")

logout.getIns(ins_logout)

## Define class for instruction pages
# general instruction
class InstructionGeneral(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(InstructionGeneral, self).__init__(**kwargs)
		self.label1 = Label(text="Instruction: ", size_hint=(0.5,0.1), pos_hint={"right":0.75, "top":0.88}, font_size=sp(30), color=(1,1,1,1), halign="center")
		self.label2 = Label(text="", size_hint=(0.7,0.6), pos_hint={"right":0.85, "top":0.85}, font_size=sp(18), color=(1,1,1,1))
		self.button = Button(text="NEXT", pos_hint={"right":0.6, "top":0.2}, size_hint=(0.2,0.1), font_size=sp(25), color=(1,1,1,1))
		#time point of leaving this page
		self.leave_time = ""
		self.username = login.username.text
		self.button.bind(on_press=self.on_press)
		self.add_widget(self.label1)
		self.add_widget(self.label2)
		self.add_widget(self.button)
		self.next_page = ""

	def getIns(self, ins):
		self.label2.text = ins

	def on_press(self, instance):
		self.leave_time = str(datetime.now().time())
		saveData[self.name] = {"leave_time":self.leave_time}
		App.get_running_app().root.current = "practice_trial"
				
# define the instruction texts
ins_general = "In this block, you are going to complete 50 food choice trials. In each trial,\n"\
			"you will be presented with two food images on the top left and top right\n"\
			"corners of the screen. Your task is to move the blue cursor at the bottom\n"\
			"of the screen to the food item you prefer. The food items will only appear\n"\
			"once you start to move the cursor. Click 'NEXT' to practice a trial"

# make the instances for different instruction pages
instruction_general = InstructionGeneral(name="instruction_general")
instruction_general.getIns(ins=ins_general)

# instructions for different trial types
class InstructionTrial(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(InstructionTrial, self).__init__(**kwargs)
		self.label1 = Label(text="", size_hint=(0.7, 0.6), pos_hint={"right":0.85, "top":0.85}, font_size=sp(18), color=(1,1,1,1))
		self.button = Button(text="NEXT", pos_hint={"right":0.6, "top":0.2}, size_hint=(0.2,0.1), font_size=sp(25), color=(1,1,1,1))
		#time point of leaving this page
		self.leave_time = ""
		self.button.bind(on_press=self.on_press)
		self.add_widget(self.label1)
		self.add_widget(self.button)
		
	def getLabel(self, label):
		self.label1.text = label

	def on_press(self, instance):
		self.leave_time = str(datetime.now().time())
		saveData[self.name] = {"leave_time":self.leave_time}
		App.get_running_app().root.current = "trial_Baseline_0"

label_trial = "Now, if you don't have any further questions, you can start the real trials. Please be\n"\
			"careful and truthful to your choices, as you will be asked to eat a random item you\n"\
			"choose at the end of the experiment. Please click 'NEXT' to proceed."


instruction_trial = InstructionTrial(name="instruction_trial")
instruction_trial.getLabel(label_trial)






#creating a class to test, playing with the classes and their setups.
class rec_instruction(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(rec_instruction, self).__init__(**kwargs)
		self.label1 = Label(text="", size_hint=(0.7, 0.6), pos_hint={"right":0.85, "top":0.85}, font_size=sp(18), color=(1,1,1,1))
		self.button = Button(text="NEXT", pos_hint={"right":0.6, "top":0.2}, size_hint=(0.2,0.1), font_size=sp(25), color=(1,1,1,1))
		#time point of leaving this page
		self.leave_time = ""
		self.button.bind(on_press=self.on_press)
		self.add_widget(self.label1)
		self.add_widget(self.button)
		
	def getLabel(self, label):
		self.label1.text = label

	def on_press(self, instance):
		self.leave_time = str(datetime.now().time())
		saveData[self.name] = {"leave_time":self.leave_time}
		App.get_running_app().root.current = "trial_Recommendation_0"



label2_rec_in = "You've completed the first block of trials\n"\
				"You can take a break for a minute\n"\
				"The next 90 trials contain a recommendation for one of the items\n"\
				"The recommendations are based on a person's average diet"
			


rec_instruct = rec_instruction(name="rec_instruct")
rec_instruct.getLabel(label2_rec_in)



class cursor_instruct(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(cursor_instruct, self).__init__(**kwargs)
		self.label1 = Label(text="", size_hint=(0.7, 0.6), pos_hint={"right":0.85, "top":0.85}, font_size=sp(18), color=(1,1,1,1))
		self.button = Button(text="NEXT", pos_hint={"right":0.6, "top":0.2}, size_hint=(0.2,0.1), font_size=sp(25), color=(1,1,1,1))
		#time point of leaving this page
		self.leave_time = ""
		self.button.bind(on_press=self.on_press)
		self.add_widget(self.label1)
		self.add_widget(self.button)
		
	def getLabel(self, label):
		self.label1.text = label

	def on_press(self, instance):
		self.leave_time = str(datetime.now().time())
		saveData[self.name] = {"leave_time":self.leave_time}
		App.get_running_app().root.current = "trial_Cursor_0"



label3_rec_in = "You've completed the first block of trials\n"\
				"You can take a break for a minute\n"\
				"The next 90 trials contain a recommendation for one of the food items\n"\
				"The cursor will be positioned below the item that is recommended"

			


cursor_ins = cursor_instruct(name="cursor_ins")
cursor_ins.getLabel(label3_rec_in)

















## Create the count down widget and the count down page
class CntDown(Label):
	a = NumericProperty(30)
	def start(self):
		Animation.cancel_all(self)
		self.anim = Animation(a=0, duration=self.a)
		def finish_callback(animation, incr_clock):
				App.get_running_app().root.current = "logout"
		self.anim.bind(on_complete=finish_callback)
		self.anim.start(self)
	def on_a(self, instance, value):
		self.text = str(round(value,1))

class CountDown(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(CountDown, self).__init__(**kwargs)
		self.text2 = "Please take a break and when countdown timer expires, you will be instructed on\n"\
					"what to do next."
		self.clockText = "This is the end of the current block of food-choices. Please click the 'NEXT'\n"\
					"button."
		self.cntdown = CntDown()
		self.button = Button(text="NEXT", pos_hint={"right":0.6, "top":0.2}, size_hint=(0.2, 0.1), font_size=sp(25), color=(1,1,1,1))
		self.lbl = Label(text=self.clockText, size_hint=(0.5, 0.1), pos_hint={"right":0.75, "top":0.55}, font_size=sp(18), color=(1,1,1,1), halign="left")
		self.button.bind(on_release=self.on_press)
		self.add_widget(self.button)
		self.add_widget(self.lbl)

	def on_press(self, instance):
		self.remove_widget(self.button)
		self.remove_widget(self.lbl)
		self.lbl.text = self.text2
		self.lbl.pos_hint = {"right":0.75, "top":0.4}
		self.add_widget(self.lbl)
		self.add_widget(self.cntdown)
		self.cntdown.start()

countDown = CountDown(name="count_down")

## Make the food-choice interface
# create the cursor
class Cursor(Widget):
    pass

Builder.load_string(""" 
<Cursor>:
	size: sp(60), sp(60)
	drag_rectangle: self.x, self.y, self.width, self.height
	drag_timeout: 1000000
	drag_distance: 0
    canvas:
        Rectangle:
            pos: self.pos
            size: self.size
            source: "cursor.png"
""")


#create a function which makes a random location for the cursor.

#position_list = [((Window.width/2-self.width/2), (Window.height/8-self.height/2)),  ((Window.width/0.7-self.width/2), (Window.height/3-self.height/2))]

# Create class to make cursor movable and measure MT parameters 

#########----------------------
#CREATING THE CONTROL DRAGOBJ for the baseline measurement.
class DragObj_base(DragBehavior, Cursor):
	def __init__(self, **kwargs):
		super(DragObj_base, self).__init__(**kwargs)

		
		# position of dragobj
		self.pos = (Window.width/2-self.width/2), (Window.height/8-self.height/2)
		# time of points on dragging trajectory 
		self.timestamp = []
		# events on dragging trajectory
		self.events = []
		# positions (x,y) of dragging trajectory
		self.coor = []
		# response stimulus
		self.response = 0
		# item word on the left
		self.stim1 = ""
		# item word on the right
		self.stim2 = ""
		# screen name
		self.name = ""
		#trial end indicator
		self.end = False
		#define a name for the tracking function to be schedueled
		self.record = None

		# time-based parameters for pilot
		self.timestamp2 = []
		self.coor2 = []

	def getStim(self, stim1, stim2):
		self.stim1 = stim1
		self.stim2 = stim2

	def on_touch_down(self, touch):
		if touch.spos[0]*Window.width >= self.x and touch.spos[0]*Window.width <= self.x+self.width and touch.spos[1]*Window.height >= self.y and touch.spos[1]*Window.height <= self.y+self.height:
				self.timestamp.append(touch.time_update)
				self.coor.append(touch.spos)
				self.events.append("down")
				def getCoor(dt):
					#print(datetime.now().time())
					self.timestamp2.append(str(datetime.now().time()))
					#print(((self.x+self.width/2)/Window.width, (self.y+self.height/2)/Window.height))
					#print(touch.spos)
					self.coor2.append(((self.x+self.width/2)/Window.width, (self.y+self.height/2)/Window.height))
				self.record = Clock.schedule_interval(getCoor, 0.01)
				self.parent.parent.update(self)
		return super(DragObj_base, self).on_touch_down(touch)

	def on_touch_move(self, touch):
		#print(Clock.get_rfps())
		self.timestamp.append(touch.time_update)
		self.events.append("move")
		self.coor.append(touch.spos)
		return super(DragObj_base, self).on_touch_move(touch)

	#Save MT parameters once cursor is released on top of one of the choice options. 
	def on_touch_up(self, touch):
		print(self.pos)
		self.timestamp.append(touch.time_update)
		self.coor.append(touch.spos)
		self.events.append("up")
		if self.record != None:
				self.record.cancel()
		if self.x >= 685 and self.y >= 310:
				self.response = self.stim2
				self.end = True
		if self.x <= 125 and self.y >= 310:
				self.response = self.stim1
				self.end = True
		if self.end == True:
				self.leave_time = str(datetime.now().time())
				saveData[self.name] = {"stim":(self.stim1+self.stim2), "coor":self.coor, "time":self.timestamp, "coor2":self.coor2, "time2":self.timestamp2, "events":self.events, "resp":self.response, "leave_time":self.leave_time}
				if self.name == "trial_Baseline_"+str((len(stimComb_base)-1)):
						App.get_running_app().root.current = 'rec_instruct' 
				
				elif self.name =="practice_trial":
						App.get_running_app().root.current = "instruction_trial"
				
				#elif self.name =="recommendation_trial":
						#App.get_running_app().root.current = "cursor_ins"
				
				#elif self.name == "control_trial":
						#App.get_running_app().root.current = "rec_instruct"
						#print('control check')
					    
				else:
						App.get_running_app().root.current = "trial_Baseline_" + str(int(self.name[15:])+1)
						print("trial_Baseline_" + (str(int(self.name[15:])+1)))
		return super(DragObj_base, self).on_touch_up(touch)




#############################
#Creating the recommendation in between control trials dragobject
############################








class DragObj(DragBehavior, Cursor):
	def __init__(self, **kwargs):
		super(DragObj, self).__init__(**kwargs)

		
		# position of dragobj
		self.pos = (Window.width/2-self.width/2), (Window.height/8-self.height/2)
		# time of points on dragging trajectory 
		self.timestamp = []
		# events on dragging trajectory
		self.events = []
		# positions (x,y) of dragging trajectory
		self.coor = []
		# response stimulus
		self.response = 0
		# item word on the left
		self.stim1 = ""
		# item word on the right
		self.stim2 = ""
		# screen name
		self.name = ""
		#trial end indicator
		self.end = False
		#define a name for the tracking function to be schedueled
		self.record = None

		# time-based parameters for pilot
		self.timestamp2 = []
		self.coor2 = []

	def getStim(self, stim1, stim2):
		self.stim1 = stim1
		self.stim2 = stim2

	def on_touch_down(self, touch):
		if touch.spos[0]*Window.width >= self.x and touch.spos[0]*Window.width <= self.x+self.width and touch.spos[1]*Window.height >= self.y and touch.spos[1]*Window.height <= self.y+self.height:
				self.timestamp.append(touch.time_update)
				self.coor.append(touch.spos)
				self.events.append("down")
				def getCoor(dt):
					#print(datetime.now().time())
					self.timestamp2.append(str(datetime.now().time()))
					#print(((self.x+self.width/2)/Window.width, (self.y+self.height/2)/Window.height))
					#print(touch.spos)
					self.coor2.append(((self.x+self.width/2)/Window.width, (self.y+self.height/2)/Window.height))
				self.record = Clock.schedule_interval(getCoor, 0.01)
				self.parent.parent.update(self)
		return super(DragObj, self).on_touch_down(touch)

	def on_touch_move(self, touch):
		#print(Clock.get_rfps())
		self.timestamp.append(touch.time_update)
		self.events.append("move")
		self.coor.append(touch.spos)
		return super(DragObj, self).on_touch_move(touch)

	#Save MT parameters once cursor is released on top of one of the choice options. 
	def on_touch_up(self, touch):
		print(self.pos)
		self.timestamp.append(touch.time_update)
		self.coor.append(touch.spos)
		self.events.append("up")
		if self.record != None:
				self.record.cancel()
		if self.x >= 685 and self.y >= 310:
				self.response = self.stim2
				self.end = True
		if self.x <= 125 and self.y >= 310:
				self.response = self.stim1
				self.end = True
		if self.end == True:
				self.leave_time = str(datetime.now().time())
				saveData[self.name] = {"stim":(self.stim1+self.stim2), "coor":self.coor, "time":self.timestamp, "coor2":self.coor2, "time2":self.timestamp2, "events":self.events, "resp":self.response, "leave_time":self.leave_time}
				if self.name == "trial_Recommendation_"+str((len(stimComb_rec)-1)):
						
						App.get_running_app().root.current = 'cursor_ins' 
				
				elif self.name =="practice_trial":
						App.get_running_app().root.current = "instruction_trial"
				
				#elif self.name =="recommendation_trial":
						#App.get_running_app().root.current = "cursor_ins"
				
				elif self.name == "control_trial":
						App.get_running_app().root.current = "rec_instruct"
						#print('control check')
					    
				else:
						App.get_running_app().root.current = "trial_Recommendation_" + str(int(self.name[21:])+1)
						print("trial_Recy_" + (str(int(self.name[21:])+1)))
		return super(DragObj, self).on_touch_up(touch)





#------------------------------------------------------------------
#CREATING THE SECOND DRAG OBJECT SWITHC
#------------------------------------------------------------------



class DragObj2(DragBehavior, Cursor):
	def __init__(self, **kwargs):
		super(DragObj2, self).__init__(**kwargs)

		# position of dragobj
		
		if random.choice(["left", "right"]) == "right":
			self.pos = (Window.width/7-self.width/2), (Window.height/8-self.height/2), #(true is right)
			
		else:
			self.pos = (Window.width/1.18-self.width/2), (Window.height/8-self.height/2)  #false is left
		# time of points on dragging trajectory 
		self.timestamp = []
		# events on dragging trajectory
		self.events = []
		# positions (x,y) of dragging trajectory
		self.coor = []
		# response stimulus
		self.response = 0
		# item word on the left
		self.stim1 = ""
		# item word on the right
		self.stim2 = ""
		# screen name
		self.name = ""
		#trial end indicator
		self.end = False
		#define a name for the tracking function to be schedueled
		self.record = None

		# time-based parameters for pilot
		self.timestamp2 = []
		self.coor2 = []

	def getStim(self, stim1, stim2):
		self.stim1 = stim1
		self.stim2 = stim2

	def on_touch_down(self, touch):
		if touch.spos[0]*Window.width >= self.x and touch.spos[0]*Window.width <= self.x+self.width and touch.spos[1]*Window.height >= self.y and touch.spos[1]*Window.height <= self.y+self.height:
				self.timestamp.append(touch.time_update)
				self.coor.append(touch.spos)
				self.events.append("down")
				def getCoor(dt):
					#print(datetime.now().time())
					self.timestamp2.append(str(datetime.now().time()))
					#print(((self.x+self.width/2)/Window.width, (self.y+self.height/2)/Window.height))
					#print(touch.spos)
					self.coor2.append(((self.x+self.width/2)/Window.width, (self.y+self.height/2)/Window.height))
				self.record = Clock.schedule_interval(getCoor, 0.01)
				self.parent.parent.update(self)
		return super(DragObj2, self).on_touch_down(touch)

	def on_touch_move(self, touch):
		#print(Clock.get_rfps())
		self.timestamp.append(touch.time_update)
		self.events.append("move")
		self.coor.append(touch.spos)
		return super(DragObj2, self).on_touch_move(touch)

	#Save MT parameters once cursor is released on top of one of the choice options. 
	def on_touch_up(self, touch):
		print(self.pos)
		self.timestamp.append(touch.time_update)
		self.coor.append(touch.spos)
		self.events.append("up")
		if self.record != None:
				self.record.cancel()
		if self.x >= 685 and self.y >= 310:
				self.response = self.stim2
				self.end = True
		if self.x <= 125 and self.y >= 310:
				self.response = self.stim1
				self.end = True
		if self.end == True:
				self.leave_time = str(datetime.now().time())
				saveData[self.name] = {"stim":(self.stim1+self.stim2), "coor":self.coor, "time":self.timestamp, "coor2":self.coor2, "time2":self.timestamp2, "events":self.events, "resp":self.response, "leave_time":self.leave_time}
				if self.name == "trial_Cursor_"+str((len(stimComb_cur)-1)):
						App.get_running_app().root.current = "count_down"
				
				#elif self.name =="practice_trial":
						#App.get_running_app().root.current = "instruction_trial"
				
				#elif self.name =="recommendation_trial":
						#App.get_running_app().root.current = "cursor_ins"
				
				#elif self.name == "control_trial":
						#App.get_running_app().root.current = "rec_instruct"
					    
				else:
						App.get_running_app().root.current = "trial_Cursor_" + str(int(self.name[13:])+1)
						print("trial_Cursor_" + (str(int(self.name[13:])+1)))
		return super(DragObj2, self).on_touch_up(touch)


#-----------------------------------
#Creating the third drag object which is for the control condition in the cursor posisiton.
#-----------------------------------
class DragObj3(DragBehavior, Cursor):
	def __init__(self, **kwargs):
		super(DragObj3, self).__init__(**kwargs)

		# position of dragobj
		
		self.pos = (Window.width/2-self.width/2), (Window.height/8-self.height/2)
		# time of points on dragging trajectory 
		self.timestamp = []
		# events on dragging trajectory
		self.events = []
		# positions (x,y) of dragging trajectory
		self.coor = []
		# response stimulus
		self.response = 0
		# item word on the left
		self.stim1 = ""
		# item word on the right
		self.stim2 = ""
		# screen name
		self.name = ""
		#trial end indicator
		self.end = False
		#define a name for the tracking function to be schedueled
		self.record = None

		# time-based parameters for pilot
		self.timestamp2 = []
		self.coor2 = []

	def getStim(self, stim1, stim2):
		self.stim1 = stim1
		self.stim2 = stim2

	def on_touch_down(self, touch):
		if touch.spos[0]*Window.width >= self.x and touch.spos[0]*Window.width <= self.x+self.width and touch.spos[1]*Window.height >= self.y and touch.spos[1]*Window.height <= self.y+self.height:
				self.timestamp.append(touch.time_update)
				self.coor.append(touch.spos)
				self.events.append("down")
				def getCoor(dt):
					#print(datetime.now().time())
					self.timestamp2.append(str(datetime.now().time()))
					#print(((self.x+self.width/2)/Window.width, (self.y+self.height/2)/Window.height))
					#print(touch.spos)
					self.coor2.append(((self.x+self.width/2)/Window.width, (self.y+self.height/2)/Window.height))
				self.record = Clock.schedule_interval(getCoor, 0.01)
				self.parent.parent.update(self)
		return super(DragObj3, self).on_touch_down(touch)

	def on_touch_move(self, touch):
		#print(Clock.get_rfps())
		self.timestamp.append(touch.time_update)
		self.events.append("move")
		self.coor.append(touch.spos)
		return super(DragObj3, self).on_touch_move(touch)

	#Save MT parameters once cursor is released on top of one of the choice options. 
	def on_touch_up(self, touch):
		print(self.pos)
		self.timestamp.append(touch.time_update)
		self.coor.append(touch.spos)
		self.events.append("up")
		if self.record != None:
				self.record.cancel()
		if self.x >= 685 and self.y >= 310:
				self.response = self.stim2
				self.end = True
		if self.x <= 125 and self.y >= 310:
				self.response = self.stim1
				self.end = True
		if self.end == True:
				self.leave_time = str(datetime.now().time())
				saveData[self.name] = {"stim":(self.stim1+self.stim2), "coor":self.coor, "time":self.timestamp, "coor2":self.coor2, "time2":self.timestamp2, "events":self.events, "resp":self.response, "leave_time":self.leave_time}
				if self.name == "trial_Cursor_"+str((len(stimComb_cur)-1)):
						App.get_running_app().root.current = "count_down"
				
				#elif self.name =="practice_trial":
						#App.get_running_app().root.current = "instruction_trial"
				
				#elif self.name =="recommendation_trial":
						#App.get_running_app().root.current = "cursor_ins"
				
				#elif self.name == "control_trial":
						#App.get_running_app().root.current = "rec_instruct"
					    
				else:
						App.get_running_app().root.current = "trial_Cursor_" + str(int(self.name[13:])+1)
						print("trial_cur_" + (str(int(self.name[13:])+1)))
		return super(DragObj3, self).on_touch_up(touch)
















#defining a variable which keeps takes a random suggestion between left and right.
################
#Basline mousetravck class
#############
rec_list = ["The machine recommends \n"\
			"the left item" , 
			"The machine recommends the \n"\
			"right item"]
recommendation = (random.choice(rec_list))



class MouseTrack_base(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(MouseTrack_base, self).__init__(**kwargs)
		self.dragObj = DragObj_base()
		self.background = Widget()
		self.dragObj.name = self.name
		#left stim
		self.stim1 = Image(pos_hint={"left":0, "top":1}, size_hint=(0.18, 0.315), source='')
		#right stim
		self.stim2 = Image(pos_hint={"right":1, "top":1}, size_hint=(0.18, 0.315), source='')
		self.black1 = Image(pos_hint={"left":0, "top":1}, size_hint=(0.18, 0.315), source='./black.png')
		self.black2 = Image(pos_hint={"right":1, "top":1}, size_hint=(0.18, 0.315), source='./black.png')

		#add the recommendation in text
		self.label2 = Label(text="", size_hint=(0.5, 0.2), pos_hint={"right":0.75, "top":0.9}, font_size=sp(14), color=(1,1,1,1), halign="center")
		self.black3 = Image(pos_hint={"right":0.75, "top":1}, size_hint=(0.5, 0.45), source='./black.png')
		#self.getrecommend()	


		#question item
		self.label = Label(text="", size_hint=(0.5, 0.2), pos_hint={"right":0.75, "top":0.6}, font_size=sp(18), color=(1,1,1,1), halign = "center")
		self.add_widget(self.stim1)
		self.add_widget(self.stim2)
		self.getLabel()
		self.add_widget(self.label)
		
		#adding the label as a widget
		
		self.add_widget(self.black1)
		self.add_widget(self.black2)
		
		#adding the label and the black image over it
		#self.add_widget(self.label2)
		#self.add_widget(self.black3)

		self.background.add_widget(self.dragObj)
		self.add_widget(self.background)

	def getStim(self, stim1, stim2):
		self.stim1.source=('./images/'+stim1+'.jpg')
		self.stim2.source=('./images/'+stim2+'.jpg')
	
	#define a function to get the recommendation
	#def getrecommend(self):
	#	self.label2.text = random.choice(rec_list)
	#	pass

	def update(self, instance):
		self.remove_widget(self.black1)
		self.remove_widget(self.black2)
		self.remove_widget(self.label)
		

		#remove the added labels.
		#self.remove_widget(self.black3)

	

	def getLabel(self):	
		self.label.text = "Please move the cursor to the food item you prefer."
				

#######
#Mousetrack for inbetween control trials.



#Higher class to combine cursor class to screen and only show choice options once cursor is clicked.
class MouseTrack(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(MouseTrack, self).__init__(**kwargs)
		self.dragObj = DragObj()
		self.background = Widget()
		self.dragObj.name = self.name
		#left stim
		self.stim1 = Image(pos_hint={"left":0, "top":1}, size_hint=(0.18, 0.315), source='')
		#right stim
		self.stim2 = Image(pos_hint={"right":1, "top":1}, size_hint=(0.18, 0.315), source='')
		self.black1 = Image(pos_hint={"left":0, "top":1}, size_hint=(0.18, 0.315), source='./black.png')
		self.black2 = Image(pos_hint={"right":1, "top":1}, size_hint=(0.18, 0.315), source='./black.png')

		#add the recommendation in text
		self.label2 = Label(text="", size_hint=(0.5, 0.2), pos_hint={"right":0.75, "top":0.9}, font_size=sp(14), color=(1,1,1,1), halign="center")
		self.black3 = Image(pos_hint={"right":0.75, "top":1}, size_hint=(0.5, 0.45), source='./black.png')
		#self.getrecommend()


		#question item
		self.label = Label(text="", size_hint=(0.5, 0.2), pos_hint={"right":0.75, "top":0.6}, font_size=sp(18), color=(1,1,1,1), halign = "center")
		self.add_widget(self.stim1)
		self.add_widget(self.stim2)
		self.getLabel()
		self.add_widget(self.label)
		
		#adding the label as a widget
		
		self.add_widget(self.black1)
		self.add_widget(self.black2)
		
		#adding the label and the black image over it
		#self.add_widget(self.label2)
		#self.add_widget(self.black3)

		self.background.add_widget(self.dragObj)
		self.add_widget(self.background)

	def getStim(self, stim1, stim2):
		self.stim1.source=('./images/'+stim1+'.jpg')
		self.stim2.source=('./images/'+stim2+'.jpg')
	
	#define a function to get the recommendation
	#def getrecommend(self):
	#	self.label2.text = random.choice(rec_list)
	#	pass

	def update(self, instance):
		self.remove_widget(self.black1)
		self.remove_widget(self.black2)
		self.remove_widget(self.label)
		

		#remove the added labels.
		#self.remove_widget(self.black3)

	

	def getLabel(self):	
		self.label.text = "Please move the cursor to the food item you prefer."
				




#--------------------------------------------
#RECOMMENDATION CLASS
#--------------------------------------------




#Creating the class for the recommendation.
class MouseTrack_rec(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(MouseTrack_rec, self).__init__(**kwargs)
		self.dragObj = DragObj()
		self.background = Widget()
		self.dragObj.name = self.name
		#left stim
		self.stim1 = Image(pos_hint={"left":0, "top":1}, size_hint=(0.18, 0.315), source='')
		#right stim
		self.stim2 = Image(pos_hint={"right":1, "top":1}, size_hint=(0.18, 0.315), source='')
		self.black1 = Image(pos_hint={"left":0, "top":1}, size_hint=(0.18, 0.315), source='./black.png')
		self.black2 = Image(pos_hint={"right":1, "top":1}, size_hint=(0.18, 0.315), source='./black.png')

		#add the recommendation in text
		self.label2 = Label(text="", size_hint=(0.5, 0.2), pos_hint={"right":0.75, "top":0.9}, font_size=sp(18), color=(1,1,1,1), halign="center")
		self.black3 = Image(pos_hint={"right":1.1, "top":1.3}, size_hint=(1.2, 0.6), source='./black.png')
		self.getrecommend()


		#question item
		self.label = Label(text="", size_hint=(0.5, 0.2), pos_hint={"right":0.75, "top":0.6}, font_size=sp(18), color=(1,1,1,1), halign = "center")
		self.add_widget(self.stim1)
		self.add_widget(self.stim2)
		self.getLabel()
		self.add_widget(self.label)

		#adding the label as a widget
		
		self.add_widget(self.black1)
		self.add_widget(self.black2)
		
		#adding the label and the black image over it
		self.add_widget(self.label2)
		self.add_widget(self.black3)

		self.background.add_widget(self.dragObj)
		self.add_widget(self.background)

	def getStim(self, stim1, stim2):
		self.stim1.source=('./images/'+stim1+'.jpg')
		self.stim2.source=('./images/'+stim2+'.jpg')
	
	#define a function to get the recommendation
	def getrecommend(self):
		self.label2.text = random.choice(rec_list)
		pass

	def update(self, instance):
		self.remove_widget(self.black1)
		self.remove_widget(self.black2)
		self.remove_widget(self.label)
		

		#remove the added labels.
		self.remove_widget(self.black3)

	

	def getLabel(self):	
		self.label.text = "Please move the cursor to the food item you prefer."



#--------------------------------
#CURSOR POSITION TRIAL
#
class MouseTrack_curs(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(MouseTrack_curs, self).__init__(**kwargs)
		self.dragObj = DragObj2()
		self.background = Widget()
		self.dragObj.name = self.name
		#left stim
		self.stim1 = Image(pos_hint={"left":0, "top":1}, size_hint=(0.18, 0.315), source='')
		#right stim
		self.stim2 = Image(pos_hint={"right":1, "top":1}, size_hint=(0.18, 0.315), source='')
		self.black1 = Image(pos_hint={"left":0, "top":1}, size_hint=(0.18, 0.315), source='./black.png')
		self.black2 = Image(pos_hint={"right":1, "top":1}, size_hint=(0.18, 0.315), source='./black.png')

		#add the recommendation in text
		self.label2 = Label(text="", size_hint=(0.5, 0.2), pos_hint={"right":0.75, "top":0.9}, font_size=sp(14), color=(1,1,1,1), halign="center")
		self.black3 = Image(pos_hint={"right":0.75, "top":1}, size_hint=(0.5, 0.45), source='./black.png')
		#self.getrecommend()


		#question item
		self.label = Label(text="", size_hint=(0.5, 0.2), pos_hint={"right":0.75, "top":0.6}, font_size=sp(18), color=(1,1,1,1), halign = "center")
		self.add_widget(self.stim1)
		self.add_widget(self.stim2)
		self.getLabel()
		self.add_widget(self.label)
		
		#adding the label as a widget
		
		self.add_widget(self.black1)
		self.add_widget(self.black2)
		
		#adding the label and the black image over it
		#self.add_widget(self.label2)
		#self.add_widget(self.black3)

		self.background.add_widget(self.dragObj)
		self.add_widget(self.background)

	def getStim(self, stim1, stim2):
		self.stim1.source=('./images/'+stim1+'.jpg')
		self.stim2.source=('./images/'+stim2+'.jpg')
	
	
	def update(self, instance):
		self.remove_widget(self.black1)
		self.remove_widget(self.black2)
		self.remove_widget(self.label)
		

		#remove the added labels.
		#self.remove_widget(self.black3)

	

	def getLabel(self):	
		self.label.text = "Please move the cursor to the food item you prefer."
				

#----------------------------
#Creating a mousetrack for the cursor which connects to the.
class MouseTrack_control(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(MouseTrack_control, self).__init__(**kwargs)
		self.dragObj = DragObj3()
		self.background = Widget()
		self.dragObj.name = self.name
		#left stim
		self.stim1 = Image(pos_hint={"left":0, "top":1}, size_hint=(0.18, 0.315), source='')
		#right stim
		self.stim2 = Image(pos_hint={"right":1, "top":1}, size_hint=(0.18, 0.315), source='')
		self.black1 = Image(pos_hint={"left":0, "top":1}, size_hint=(0.18, 0.315), source='./black.png')
		self.black2 = Image(pos_hint={"right":1, "top":1}, size_hint=(0.18, 0.315), source='./black.png')

		#add the recommendation in text
		self.label2 = Label(text="", size_hint=(0.5, 0.2), pos_hint={"right":0.75, "top":0.9}, font_size=sp(14), color=(1,1,1,1), halign="center")
		self.black3 = Image(pos_hint={"right":0.75, "top":1}, size_hint=(0.5, 0.45), source='./black.png')
		#self.getrecommend()


		#question item
		self.label = Label(text="", size_hint=(0.5, 0.2), pos_hint={"right":0.75, "top":0.6}, font_size=sp(18), color=(1,1,1,1), halign = "center")
		self.add_widget(self.stim1)
		self.add_widget(self.stim2)
		self.getLabel()
		self.add_widget(self.label)
		
		#adding the label as a widget
		
		self.add_widget(self.black1)
		self.add_widget(self.black2)
		
		#adding the label and the black image over it
		#self.add_widget(self.label2)
		#self.add_widget(self.black3)

		self.background.add_widget(self.dragObj)
		self.add_widget(self.background)

	def getStim(self, stim1, stim2):
		self.stim1.source=('./images/'+stim1+'.jpg')
		self.stim2.source=('./images/'+stim2+'.jpg')
	
	
	def update(self, instance):
		self.remove_widget(self.black1)
		self.remove_widget(self.black2)
		self.remove_widget(self.label)
		

		#remove the added labels.
		#self.remove_widget(self.black3)

	

	def getLabel(self):	
		self.label.text = "Please move the cursor to the food item you prefer."







#------------------------
#the various test trials
#------------------------
practice_trial = MouseTrack(name="practice_trial")
practice_trial.getStim("practice1", "practice2")
practice_trial.dragObj.getStim("practice1", "practice2")


control_trial = MouseTrack(name="control_trial")
control_trial.getStim("practice1", "practice2" )
control_trial.dragObj.getStim("practice1", "practice2")


recommendation_trial = MouseTrack_rec(name="recommendation_trial")
recommendation_trial.getStim("practice1", "practice2")
recommendation_trial.dragObj.getStim("practice1", "practice2")

cursor_trial = MouseTrack_curs(name="cursor_trial")
cursor_trial.getStim("practice1", "practice2")
cursor_trial.dragObj.getStim("practice1", "practice2")




#---------------------------
## Build the app
#---------------------------
class MouseTrackApp(App):
	def build(self):
		ScreenM = ScreenManager(transition=WipeTransition())
		
		ScreenM.add_widget(login)
		
		
		ScreenM.add_widget(rec_instruct)

		ScreenM.add_widget(recommendation_trial)

		ScreenM.add_widget(cursor_ins)
		# screens of real trials in block 1
		screen_trial = []

		#test list for easy of testing
		
		
		
		screen_rec = []
		control_list = ["True", "False"]
		#stimComb3 = ['11', '23', '44']
		ranger = len(stimComb_rec)	
		correct_range = (ranger - 1)
		
		for i in range(ranger):	
			chooser = random.choice(["recommendation", "control"])
			if chooser == "control":	
				screen_trial.append(MouseTrack(name="trial_Recommendation_"+str(i)))
				screen_trial[i].getStim(stimComb_rec[i][0], stimComb_rec[i][1])
				screen_trial[i].dragObj.getStim(stimComb_rec[i][0], stimComb_rec[i][1])
				ScreenM.add_widget(screen_trial[i])
			elif chooser =="recommendation":
				screen_trial.append(MouseTrack_rec(name="trial_Recommendation_"+str(i)))
				screen_trial[i].getStim(stimComb_rec[i][0], stimComb_rec[i][1])
				screen_trial[i].dragObj.getStim(stimComb_rec[i][0], stimComb_rec[i][1])
				ScreenM.add_widget(screen_trial[i])
			#	
			print(chooser)

		
		
		
		ScreenM.add_widget(logout)
		return ScreenM

	def on_pause(self): 
		return True

	def on_resume(self):
		pass

if __name__ == "__main__":
	MouseTrackApp().run()
