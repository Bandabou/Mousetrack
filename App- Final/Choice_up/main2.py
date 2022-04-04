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

from random import shuffle, choice
from datetime import datetime
import os
import json

## Initiate some global variables
#This part combines all stimuli pairs in a list, with each option appearing left and right once, and randomizes them. Input the names of the images without the image extention here.
saveData = {}

path = "C:\\Users\\20183382\\Desktop\\Mousetrack\\App\\Rating\\Data"
os.chdir(path)
with open("current_stim.json") as json_data:
	df = json.load(json_data)
stimComb = df["up"]

print(len(stimComb))

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
				App.get_running_app().root.current = "instruction_general"
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
		with open("C:\\Users\\20183382\\Desktop\\Mousetrack\\App\\Choice_up\\Data\\p"+login.username.text+"_choice_up.json", 'w') as f: # modify according to your local path
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
		App.get_running_app().root.current = "trial_up_0"

label_trial = "Now, if you don't have any further questions, you can start the real trials. Please be\n"\
			"careful and truthful to your choices, as you will be asked to eat a random item you\n"\
			"choose at the end of the experiment. Please click 'NEXT' to proceed."

instruction_trial = InstructionTrial(name="instruction_trial")
instruction_trial.getLabel(label_trial)

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

# Create class to make cursor movable and measure MT parameters 
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
				if self.name == "trial_up_"+str((len(stimComb)-1)):
						App.get_running_app().root.current = "count_down"
				elif self.name == "practice_trial":
						App.get_running_app().root.current = "instruction_trial"
				else:
						App.get_running_app().root.current = "trial_up_" + str(int(self.name[9:])+1)
		return super(DragObj, self).on_touch_up(touch)

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
		#question item
		self.label = Label(text="", size_hint=(0.5, 0.2), pos_hint={"right":0.75, "top":0.6}, font_size=sp(18), color=(1,1,1,1), halign = "center")
		self.add_widget(self.stim1)
		self.add_widget(self.stim2)
		self.getLabel()
		self.add_widget(self.label)
		self.add_widget(self.black1)
		self.add_widget(self.black2)
		self.background.add_widget(self.dragObj)
		self.add_widget(self.background)

	def getStim(self, stim1, stim2):
		self.stim1.source=('./images/'+stim1+'.jpg')
		self.stim2.source=('./images/'+stim2+'.jpg')

	def update(self, instance):
		self.remove_widget(self.black1)
		self.remove_widget(self.black2)
		self.remove_widget(self.label)

	def getLabel(self):	
		self.label.text = "Please move the cursor to the food item you prefer."
				
practice_trial = MouseTrack(name="practice_trial")
practice_trial.getStim("practice1", "practice2")
practice_trial.dragObj.getStim("practice1", "practice2")

## Build the app
class MouseTrackApp(App):
	def build(self):
		ScreenM = ScreenManager(transition=WipeTransition())
		ScreenM.add_widget(login)
		ScreenM.add_widget(instruction_general)
		ScreenM.add_widget(practice_trial)
		ScreenM.add_widget(instruction_trial)
		# screens of real trials in block 1
		screen_trial = []
		for i in range(len(stimComb)):
			screen_trial.append(MouseTrack(name="trial_up_"+str(i)))
			screen_trial[i].getStim(stimComb[i][0], stimComb[i][1])
			screen_trial[i].dragObj.getStim(stimComb[i][0], stimComb[i][1])
			ScreenM.add_widget(screen_trial[i])

		ScreenM.add_widget(countDown)
		ScreenM.add_widget(logout)

		return ScreenM

	def on_pause(self):
		return True

	def on_resume(self):
		pass

if __name__ == "__main__":
	MouseTrackApp().run()
