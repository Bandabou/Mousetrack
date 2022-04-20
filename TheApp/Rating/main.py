## load the libraries
from kivy.config import Config
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', 200)
Config.set('graphics', 'top',  200)
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
from kivy.metrics import sp, dp
from kivy.uix.popup import Popup

from random import shuffle, choice
from datetime import datetime
import os
import json

## Initiate some global variables
#This part combines all stimuli pairs in a list, with each option appearing left and right once, and randomizes them. Input the names of the images without the image extention here.
stimList = ['0','1','2','3','4','5','6','7','8','9']
# an empty dictionary to save data
saveData = {}
saveStim = {}
saveStimi = {}

## Design some popups in case of incorrect inputs from the user
popup_username = Popup(title="Woops!", content=Label(text="Please type in your correct participant ID, e.g., '09'"), size_hint=(0.6, 0.6))
popup_rating = Popup(title="Woops!", content=Label(text="Please rating this food item before continuing"), size_hint=(0.6, 0.6))

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
				App.get_running_app().root.current = "instruction_rating"
		else:
				popup_username.open()

	def getText(self):
		return self.username.text

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
		with open("C:\\Users\\20183382\\Desktop\\mouse\\Mousetrack\\App- Final\\Rating\\Data\\p"+login.username.text+"_rating.json", 'w') as f: # modify according to your local path
			json.dump(saveData, f)
		# randomly distribute food pairs to the 4 conditions (top/down, right/left share the 90 pairs)
		

		stimList = ['0','1','2','3','4','5','6','7','8','9']


		stimComb = []
		for i in range(len(stimList)):
				for j in range(i+1, len(stimList)):
					stimComb.append(stimList[i] + stimList[j])

		for i in range(len(stimList)):
				for j in range(i+1, len(stimList)):
					stimComb.append(stimList[j] + stimList[i])

		for i in range(len(stimList)):
				for j in range(i+1, len(stimList)):
					stimComb.append(stimList[j] + stimList[i])

		for i in range(len(stimList)):
				for j in range(i+1, len(stimList)):
					stimComb.append(stimList[j] + stimList[i])

		for i in range(len(stimList)):
				for j in range(i+1, len(stimList)):
					stimComb.append(stimList[j] + stimList[i])

		for i in range(len(stimList)):
				for j in range(i+1, len(stimList)):
					stimComb.append(stimList[j] + stimList[i])
				print(stimComb)
				print(len(stimComb))
				print(saveStim)

		

		shuffle(stimComb)
		saveStimi["Baseline"] = stimComb[0:50]
		saveStimi["Recommendation"] = stimComb[50:140]
		shuffle(stimComb)
		saveStimi["Cursor"] = stimComb[140:230]
				
		print(stimComb)
		print(len(stimComb))
		print(saveStimi)
		print(len(saveStimi))

				
		with open("C:\\Users\\20183382\\Desktop\\mouse\\Mousetrack\\App- Final\\Rating\\Data\\current_stim.json", 'w') as f: # modify according to your local path
			json.dump(saveStimi, f)
		App.get_running_app().stop()

ins_logout = "This is the end of the rating task. Next, you are going to do the\n"\
			"first block of the food-choice task. Please first save data and log out,\n "\
			"and then ask the experimenter to help you with the task."

# create an instance for Logout with a name
logout = Logout(name="logout")

logout.getIns(ins_logout)

## Define class for instruction pages
class Instruction(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(Instruction, self).__init__(**kwargs)
		self.label1 = Label(text="Instruction: Attribute rating", size_hint=(0.5, 0.1), pos_hint={"right":0.75, "top":0.88}, font_size=sp(30), color=(1,1,1,1), halign="center")
		self.label2 = Label(text="", size_hint=(0.7,0.6), pos_hint={"right":0.85, "top":0.85}, font_size=sp(18), color=(1,1,1,1))
		self.button = Button(text="NEXT", pos_hint={"right":0.6, "top":0.2}, size_hint=(0.2, 0.1), font_size=sp(25), color=(1,1,1,1))
		#time point of leaving this page
		self.leave_time = ""
		self.button.bind(on_press=self.on_press)
		self.add_widget(self.label1)
		self.add_widget(self.label2)
		self.add_widget(self.button)

	def getIns(self, ins):
		self.label2.text = ins

	def on_press(self, instance):
		self.leave_time = str(datetime.now().time())
		saveData["instruction"] = {"leave_time":self.leave_time}
		App.get_running_app().root.current = "rating_0"


# define the instruction texts
ins_rating = "In this first part you will be rating 10 different food items on their\n"\
	"healthiness and tastiness using the rating scales provided.\n"\
	" \n"\
	"If you have no further questions, you can start the real task by clicking\n"\
	"the 'NEXT' button."


instruction_rating = Instruction(name="instruction_rating")
instruction_rating.getIns(ins_rating)


## Make attribute rating interface
class Grid(CheckBox):
	def __init__(self, number, **kwargs):
		super(Grid, self).__init__(**kwargs)
		self.number = number

class Rating_1(Screen, FloatLayout, ButtonBehavior):

	def __init__(self, **kwargs):
		super(Rating_1, self).__init__(**kwargs)
		self.responseH = 0
		self.responseT = 0
		self.stim = ""
		self.qH = ""
		self.qT = ""
		self.im = ""
		self.radioButtonH = []
		self.radioButtonT = []
		self.next_page = ""
		self.index = 0
		#time point of leaving this page
		self.leave_time = ""
		#button "NEXT"
		self.button = Button(text="NEXT", pos_hint={"right":0.6, "top":0.15}, size_hint=(0.2, 0.1), font_size=sp(25), color=(1,1,1,1))
		self.button.bind(on_release=self.on_press)
		self.add_widget(self.button)

		#image
		self.imageS = Image(source="", pos_hint={'right':0.68, 'top':0.97}, size_hint=(0.36, 0.383))

		#question
		self.questionH = Label(text="How healthy is this food?", size_hint=(0.5, 0.1), pos_hint={"right":0.75, "top":0.56}, font_size=sp(20),color=(1,1,1,1), halign="left")
		self.questionT = Label(text="How tasty is this food?", size_hint=(0.5, 0.1), pos_hint={"right":0.75, "top":0.38}, font_size=sp(20),color=(1,1,1,1), halign="left")

		#label
		self.label1 = Label(text="very little", size_hint=(0.15,0.15), pos_hint={"right":0.19, "top":0.51}, font_size=sp(18),color=(1,1,1,1))
		self.label2 = Label(text="very much", size_hint=(0.15,0.15), pos_hint={"right":0.97, "top":0.51}, font_size=sp(18), color=(1,1,1,1))
		self.label3 = Label(text="very much", size_hint=(0.15,0.15), pos_hint={"right":0.97, "top":0.33}, font_size=sp(18), color=(1,1,1,1))
		self.label4 = Label(text="very little", size_hint=(0.15,0.15), pos_hint={"right":0.19, "top":0.33}, font_size=sp(18), color=(1,1,1,1))

		#add on the screen
		self.add_widget(self.questionH)
		self.add_widget(self.questionT)
		self.add_widget(self.label1)
		self.add_widget(self.label2)
		self.add_widget(self.label3)
		self.add_widget(self.label4)
		self.add_widget(self.imageS)

		#Healthiness rating
		for i in range(0, 7):
			self.radioButtonH.append(Grid(id =self.stim+"H", group='group1', number=i+1, background_radio_normal='radiobutton.png', size_hint=(0.05,0.05), pos_hint={"right":0.23+i*0.1, "top":0.46}))
			self.add_widget(self.radioButtonH[-1])
			self.radioButtonH[-1].bind(active=self.checkActiveH)

		#Tastiness rating
		for i in range(0, 7):
			self.radioButtonT.append(Grid(id =self.stim+"T", group='group2',number=i+1,  background_radio_normal='radiobutton.png',  size_hint=(0.05,0.05), pos_hint={"right":0.23+i*0.1, "top":0.28}))
			self.add_widget(self.radioButtonT[-1])
			self.radioButtonT[-1].bind(active=self.checkActiveT)

	def on_press(self, instance):
		if self.responseH != 0 and self.responseT != 0:
				self.leave_time = str(datetime.now().time())
				saveData[self.name]= {"stim":self.stim, "ratingH":self.responseH, "ratingT":self.responseT, "leave_time":self.leave_time}
				if self.name == "rating_9":
						self.next_page = "logout"

				else:
						self.index = int(self.name[self.name.find("_")+1:])
						self.next_page = self.name[0:self.name.find("_")+1] + str(self.index+1)
				App.get_running_app().root.current = self.next_page
		else:
			popup_rating.open()

	def getStim(self, stim):
		self.stim = stim

	def getImage(self, im):
		self.imageS.source = im

	#connect the grid to rating class
	def checkActiveH(self, grid, *args):
		if grid.active:
			self.responseH = grid.number

	def checkActiveT(self, grid, *args):
		if grid.active:
			self.responseT = grid.number



## Build the app
class MouseTrackApp(App):
	def __init_(self, **kwargs):
		super(MouseTrackApp, self).__init__(**kwargs)
		Window.bind(on_keyboard=self.onBackBtn)

	def onBackBtn(self, window, key, **args):
		# If user clickes Back/Esc Key
		if key == 27:
				return True
		pass

	def build(self):
		ScreenM = ScreenManager(transition=WipeTransition())
		ScreenM.add_widget(login)
		ScreenM.add_widget(instruction_rating)
		# screens of attribute ratings
		screen_rating = []
		for i in range(10):
				screen_rating.append(Rating_1(name="rating_"+str(i)))
				screen_rating[i].getStim(stimList[i])
				screen_rating[i].getImage('./'+str(i)+".jpg")
				ScreenM.add_widget(screen_rating[i])

		ScreenM.add_widget(logout)

		return ScreenM

	def on_pause(self):
		return True

	def on_resume(self):
		pass




if __name__ == "__main__":
	MouseTrackApp().run()



