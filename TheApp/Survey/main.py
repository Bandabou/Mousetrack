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
from kivy.uix.popup import Popup
from kivy.metrics import sp, dp

from random import shuffle, choice
from datetime import datetime
import os
import json

## Initiate some global variables
saveData = {}

## Design some popups in case of incorrect inputs from the user
popup_username = Popup(title="Woops!", content=Label(text="Please type in your correct participant ID, e.g., '09'"), size_hint=(0.6, 0.6))
popup_survey = Popup(title="Woops!", content=Label(text="Please answer all the questions before continuing"), size_hint=(0.6, 0.6))
popup_age = Popup(title="Woops!", content=Label(text="There's an error in the age you filled in. Please check."), size_hint=(0.6, 0.6))
popup_length = Popup(title="Woops!", content=Label(text="There's an error in the length you filled in. Please check."), size_hint=(0.6, 0.6))
popup_weight = Popup(title="Woops!", content=Label(text="There's an error in the weight you filled in. Please check."), size_hint=(0.6, 0.6))

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
				App.get_running_app().root.current = "survey1"
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
		self.leave_time = ""

	def getIns(self, ins):
		self.label.text = ins

	def on_press(self, instance):
		self.leave_time = str(datetime.now().time())
		saveData["logout"] = {"leave_time":self.leave_time}
		#with open("C:\\Users\\participant\\Desktop\\Mousetrack-main\\TheApp\\Survey\\Data\\p"+login.username.text+"_survey.json", 'w') as f: # backup
		with open("\\Data\\p"+login.username.text+"_survey.json", 'w') as f: # modify according to your local path
			json.dump(saveData, f)
		lastPage.getImage()
		App.get_running_app().root.current = "lastPage"

ins_logout = "This is the end of the experiment. Thanks for your participation\n"\
			"You can save data and log out and call the experimenter for receiving\n"\
			"your food item and debriefing now."

# create an instance for Logout with a name
logout = Logout(name="logout")

# add instruction text to the logout interface
logout.getIns(ins_logout)


## Define the last page to show the selected food item
class LastPage(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(LastPage, self).__init__(**kwargs)
		self.label = Label(text="This is the food item you will receive:", size_hint=(0.5, 0.1), pos_hint={"right":0.75, "top":0.85}, font_size=sp(18), color=(1,1,1,1), halign="center")
		self.image = Image(source="", pos_hint={'right':0.68, 'top':0.7}, size_hint=(0.36, 0.383))
		self.add_widget(self.label)
		self.add_widget(self.image)

	def getImage(self):
		food_list = []
		for orientation in ["up", "down", "right", "left"]:
			path = "..\\Choice_up\\Data\\" # RELATIVEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEe
			os.chdir(path)
			with open("p"+login.username.text+"_choice_up.json") as json_data:
				df = json.load(json_data)
			for i in df.keys():
				if i.find("trial_"+orientation+"_") != -1:
						if df[i]["resp"] != "8" and df[i]["resp"] != "t" and df[i]["resp"] != "c":
								food_list.append(df[i]["resp"])
		self.image.source = "..\\Choice_up\\images\\"+choice(food_list)+".jpg" # RELATIVEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEe

lastPage = LastPage(name="lastPage")

## Make interfaces for survey questionnaires
class Grid(CheckBox):
	def __init__(self, number, **kwargs):
		super(Grid, self).__init__(**kwargs)
		self.number = number

# First part of the survey
class Survey1(Screen, FloatLayout):
	def __init__(self, **kwargs):
		super(Survey1, self).__init__(**kwargs)
		#age
		self.label1 = Label(text='Age:', size_hint=(0.2, 0.1), pos_hint={"right":0.3, "top":0.92}, font_size=sp(20), halign="right", valign="middle")
		self.label1.bind(size=self.label1.setter('text_size'))
		self.add_widget(self.label1)
		self.age = TextInput(text="", multiline=False, size_hint=(0.3, 0.07), pos_hint={"right":0.61, "top":0.9}, font_size=sp(18))
		self.add_widget(Label(text='years old', size_hint=(0.2, 0.1), pos_hint={"right":0.78, "top":0.92}, font_size=sp(20)))
		self.add_widget(self.age)
		#gender
		self.gender = 99
		self.label2 = Label(text='Gender:', size_hint=(0.2, 0.1), pos_hint={"right":0.3, "top":0.8}, font_size=sp(20), halign="right", valign="middle")
		self.label2.bind(size=self.label2.setter('text_size'))
		self.add_widget(self.label2)
		self.male = CheckBox(id="0", group='groupG', background_radio_normal='radiobutton.png', size_hint=(0.1, 0.1), pos_hint={"right":0.4, "top":0.8})
		self.add_widget(Label(text='male',size_hint=(0.1, 0.1), pos_hint={"right":0.46,"top":0.8}, font_size=sp(20)))
		self.female = CheckBox(id="1", group='groupG', background_radio_normal='radiobutton.png', size_hint=(0.1, 0.1), pos_hint={"right":0.56, "top":0.8})
		self.add_widget(Label(text='female', size_hint=(0.1, 0.1), pos_hint={"right":0.63, "top":0.8}, font_size=sp(20)))
		self.male.bind(active=self.checkActive1)
		self.female.bind(active=self.checkActive2)
		self.add_widget(self.male)
		self.add_widget(self.female)
		#length
		self.label3 = Label(text='Height:', size_hint=(0.2, 0.1), pos_hint={"right":0.3, "top":0.68}, font_size=sp(20), halign="right", valign="middle")
		self.label3.bind(size=self.label3.setter('text_size'))
		self.add_widget(self.label3)
		self.length = TextInput(text="", multiline=False, size_hint=(0.3, 0.07), pos_hint={"right":0.61, "top":0.665}, font_size=sp(18))
		self.add_widget(Label(text='cm', size_hint=(0.2, 0.1), pos_hint={"right":0.745, "top":0.68}, font_size=sp(20)))
		self.add_widget(self.length)  
		# weight
		self.label4 = Label(text='weight:', size_hint=(0.2, 0.1), pos_hint={"right":0.3, "top":0.54}, font_size=sp(20), halign="right", valign="middle")
		self.label4.bind(size=self.label4.setter('text_size'))
		self.add_widget(self.label4)
		self.weight = TextInput(text="", multiline=False, size_hint=(0.3, 0.07), pos_hint={"right":0.61, "top":0.525}, font_size=sp(18))
		self.add_widget(Label(text='kg', size_hint=(0.2, 0.1), pos_hint={"right":0.745, "top":0.54}, font_size=sp(20)))
		self.add_widget(self.weight)
		#dominant hand
		self.hand = 99
		self.add_widget(Label(text='Which hand did you mainly use to perform the tasks?', size_hint=(0.2, 0.1), pos_hint={"right":0.62, "top":0.4}, font_size=sp(20))) 
		self.lefth = CheckBox(id="a", group='group1', background_radio_normal='radiobutton.png', size_hint=(0.1,0.1), pos_hint={"right":0.35, "top":0.32})
		self.add_widget(Label(text='left',size_hint=(0.1, 0.1),pos_hint={"right":0.4,"top":0.32},font_size=sp(20)))
		self.righth = CheckBox(id="b", group='group1', background_radio_normal='radiobutton.png', size_hint=(0.1, 0.1), pos_hint={"right":0.54, "top":0.32})
		self.add_widget(Label(text='right', size_hint=(0.1, 0.1), pos_hint={"right":0.60, "top":0.32}, font_size=sp(20)))
		self.both = CheckBox(id="c", group='group1', background_radio_normal='radiobutton.png',size_hint=(0.1,0.1),pos_hint={"right":0.71,"top":0.32})
		self.add_widget(Label(text='both', size_hint=(0.1, 0.1), pos_hint={"right":0.765, "top":0.32}, font_size=sp(20)))

		self.lefth.bind(active=self.checkActive3)
		self.righth.bind(active=self.checkActive4)
		self.both.bind(active=self.checkActive5)
		self.add_widget(self.lefth)
		self.add_widget(self.righth)
		self.add_widget(self.both)
		self.button = Button(text='NEXT', size_hint=(0.2, 0.1), pos_hint={"right":0.6, "top":0.15}, font_size=sp(25))
		self.button.bind(on_press=self.on_press)
		self.add_widget(self.button)

	# move to next page
	def checkActive1(self, *args):
		if args[1]==True:
				self.gender = 0
	def checkActive2(self, *args):
		if args[1]==True:
				self.gender = 1 
	def checkActive3(self, *args):
		if args[1]==True:
				self.hand = 0
	def checkActive4(self, *args):
		if args[1]==True:
				self.hand = 1
	def checkActive5(self, *args):
		if args[1]==True:
				self.hand = 2
	def on_press (self,instance):
		if self.age.text != "" and self.gender != 99 and self.length.text != "" and self.weight.text != "" and self.hand != 99:
				if self.age.text.isdigit() == False or int(self.age.text) <= 12 or int(self.age.text) >= 120:
						popup_age.open()
				elif self.length.text.isdigit() == False or int(self.length.text) <= 80 or int(self.length.text) >= 250:
						popup_length.open()
				elif self.weight.text.isdigit() == False or int(self.weight.text) <= 20 or int(self.weight.text) >= 300:
						popup_weight.open()
				else:
						self.leave_time = str(datetime.now().time())
						saveData[self.name] = {"age":self.age.text, "gender":self.gender, "length":self.length.text, "weight":self.weight.text, "hand":self.hand, "leave_time":self.leave_time}
						App.get_running_app().root.current = "survey2"
		else:
				popup_survey.open()

survey1 = Survey1(name="survey1")

#Second part of the survey
class Survey2(Screen, FloatLayout, ButtonBehavior):
	def __init__(self, **kwargs):
		super(Survey2, self).__init__(**kwargs)
		#button 'NEXT'
		self.button = Button(text='NEXT', size_hint=(0.2, 0.1),pos_hint={"right":0.6, "top":0.15}, font_size=sp(25) )
		self.button.bind(on_press=self.on_press)
		self.add_widget(self.button)
		#allergies
		self.label1 = Label(text='Do you have any allergies?', size_hint=(0.8, 0.1), pos_hint={"right":1, "top":0.9}, font_size=sp(20), halign="left", valign="middle")
		self.label1.bind(size=self.label1.setter('text_size'))
		self.add_widget(self.label1)
		self.allergies = 99
		self.allergies_no = CheckBox(id="0", group='groupA', background_radio_normal='radiobutton.png', size_hint=(0.1, 0.1), pos_hint={"right":0.4, "top":0.815})
		self.add_widget(Label(text='no', size_hint=(0.1, 0.1), pos_hint={"right":0.46, "top":0.815}, font_size=sp(20)))
		self.allergies_yes = CheckBox(id="1", group='groupA', background_radio_normal='radiobutton.png', size_hint=(0.1, 0.1), pos_hint={"right":0.65, "top":0.815})
		self.add_widget(Label(text='yes', size_hint=(0.1, 0.1), pos_hint={"right":0.71, "top":0.815}, font_size=sp(20)))
		self.allergies_no.bind(active=self.checkActiveA1)
		self.allergies_yes.bind(active=self.checkActiveA2)
		self.add_widget(self.allergies_no)
		self.add_widget(self.allergies_yes)
		self.allergies_text = TextInput(text="", multiline=False, size_hint=(0.6, 0.07), pos_hint={"right":0.8, "top":0.7}, font_size=sp(18))
		self.add_widget(self.allergies_text)

		#special diet
		self.label2 = Label(text='Are you currently on a diet? If so, what type?', size_hint=(0.8, 0.1), pos_hint={"right":1, "top":0.55}, font_size=sp(20), halign="left", valign="middle")
		self.label2.bind(size=self.label2.setter('text_size'))
		self.add_widget(self.label2)
		self.diet = 99
		self.diet_no = CheckBox(id="0", group='groupD', background_radio_normal='radiobutton.png', size_hint=(0.1, 0.1), pos_hint={"right":0.4, "top":0.47})
		self.add_widget(Label(text='no', size_hint=(0.1, 0.1), pos_hint={"right":0.46, "top":0.47}, font_size=sp(20)))
		self.diet_yes = CheckBox(id="1", group='groupD', background_radio_normal='radiobutton.png', size_hint=(0.1, 0.1), pos_hint={"right":0.65, "top":0.47})
		self.add_widget(Label(text='yes', size_hint=(0.1, 0.1), pos_hint={"right":0.71, "top":0.47}, font_size=sp(20)))
		self.diet_no.bind(active=self.checkActiveD1)
		self.diet_yes.bind(active=self.checkActiveD2)
		self.add_widget(self.diet_no)
		self.add_widget(self.diet_yes)
		self.diet_text = TextInput(text="", multiline=False, size_hint=(0.6, 0.07), pos_hint={"right":0.8, "top":0.35}, font_size=sp(18))
		self.add_widget(self.diet_text)

	def checkActiveA1(self, *args):
		if args[1]==True:
				self.allergies = 0
	def checkActiveA2(self, *args):
		if args[1]==True:
				self.allergies = 1
	def checkActiveD1(self, *args):
		if args[1]==True:
				self.diet = 0
	def checkActiveD2(self, *args):
		if args[1]==True:
				self.diet = 1

	def on_press(self, instance):
		if self.allergies != 99 and self.diet != 99:
				self.leave_time = str(datetime.now().time())
				saveData[self.name] = {"allergies":self.allergies, "allergiesText":self.allergies_text.text, "diet":self.diet, "dietText":self.diet_text.text, "leave_time":self.leave_time}
				App.get_running_app().root.current = "survey3"
		else:
				popup_survey.open()

survey2 = Survey2(name="survey2")

#Third part of the survey
class Survey3(Screen, FloatLayout, ButtonBehavior):
	def __init__(self, **kwargs):
		super(Survey3, self).__init__(**kwargs)
		self.radiobuttonHunger = []
		self.radiobuttonHealth = []
		self.responseHunger = ""
		self.responseHealth = ""
		#bnutton 'NEXT'
		self.button = Button(text='NEXT', size_hint=(0.2, 0.1), pos_hint={"right":0.6, "top":0.15}, font_size=sp(25))
		self.button.bind(on_press=self.on_press)
		self.add_widget(self.button)
		#hunger
		self.hunger = 99
		self.label1 = Label(text='How hungry are you at this moment?', size_hint=(0.8, 0.1), pos_hint={"right":0.9, "top":0.9}, font_size=sp(20), halign="center", valign="middle")
		self.label1.bind(size=self.label1.setter('text_size'))
		self.add_widget(self.label1)
		self.labelH1 = Label(text="Not at all", size_hint=(0.10, 0.10), pos_hint={"right":0.17, "top":0.83}, font_size=sp(18), color=(1,1,1,1))
		self.labelH2 = Label(text="Very much", size_hint=(0.10, 0.10), pos_hint={"right":0.945, "top":0.83}, font_size=sp(18), color=(1,1,1,1))
		self.add_widget(self.labelH1)
		self.add_widget(self.labelH2)
		for i in range(0,7):
				self.radiobuttonHunger.append(Grid(id ="Hunger", group='groupH', number=i+1,
				background_radio_normal='radiobutton.png',
				size_hint=(0.05, 0.05), pos_hint={"right":0.23+i*0.10, "top":0.8}))
				self.add_widget(self.radiobuttonHunger[-1])
				self.radiobuttonHunger[-1].bind(active=self.checkActiveHunger)
		#goal to eath healthy
		self.health = 99
		self.label2 = Label(text='To what extend do you have the goal to eat healthy?', size_hint=(0.8, 0.1), pos_hint={"right":0.9, "top":0.66}, font_size=sp(20), halign="center", valign="middle")
		self.label2.bind(size=self.label2.setter('text_size'))
		self.add_widget(self.label2)
		self.labelH3 = Label(text="Not at all", size_hint=(0.10, 0.10), pos_hint={"right":0.17, "top":0.585}, font_size=sp(18), color=(1,1,1,1))
		self.labelH4 = Label(text="Very much", size_hint=(0.10, 0.10), pos_hint={"right":0.945, "top":0.585}, font_size=sp(18), color=(1,1,1,1))
		self.add_widget(self.labelH3)
		self.add_widget(self.labelH4)
		for i in range(0,7):
				self.radiobuttonHealth.append(Grid(id ="Health", group='groupH2', number=i+1,
				background_radio_normal='radiobutton.png',
				size_hint=(0.05, 0.05),pos_hint={"right":0.23+i*0.10, "top":0.556}))
				self.add_widget(self.radiobuttonHealth[-1])
				self.radiobuttonHealth[-1].bind(active=self.checkActiveHealth)
		#vegetarian
		self.vegan = 99
		self.label3 = Label(text='Are you a vegetarian?', size_hint=(0.8, 0.1), pos_hint={"right":0.9, "top":0.41}, font_size=sp(20), halign="center", valign="middle")
		self.label3.bind(size=self.label3.setter('text_size'))
		self.add_widget(self.label3)
		self.vegan_yes = CheckBox(id="1", group='group', background_radio_normal='radiobutton.png', size_hint=(0.05, 0.05), pos_hint={"right":0.42, "top":0.31})
		self.vegan_no = CheckBox(id="0", group='group', background_radio_normal='radiobutton.png', size_hint=(0.05, 0.05), pos_hint={"right":0.6, "top":0.31})
		self.add_widget(Label(text='yes', size_hint=(0.1,0.1), pos_hint={"right":0.5, "top":0.34}, font_size=sp(20)))
		self.add_widget(Label(text='no', size_hint=(0.1,0.1), pos_hint={"right":0.68, "top":0.34}, font_size=sp(20)))
		self.vegan_yes.bind(active=self.checkActiveV1)
		self.vegan_no.bind(active=self.checkActiveV2)
		self.add_widget(self.vegan_yes)
		self.add_widget(self.vegan_no)

	#connect the grids to rating class     
	def checkActiveHealth(self,grid, *args):
		if grid.active:
				self.health = grid.number     
	def checkActiveHunger(self,grid,*args):
		if grid.active:
				self.hunger = grid.number
	def checkActiveV1(self,*args):
		if args[1]==True:
				self.vegan = 0
	def checkActiveV2(self,*args):
		if args[1]==True:
				self.vegan = 1
	def on_press (self,instance):
		if self.hunger != 99 and self.health != 99 and self.vegan != 99:
				self.leave_time = str(datetime.now().time())
				saveData[self.name] = {"hunger":self.hunger, "health":self.health, "vegan":self.vegan, "leave_time":self.leave_time}
				App.get_running_app().root.current = "tsc1"
		else:
				popup_survey.open()

survey3 = Survey3(name="survey3")


#Brief Trait Self-Control Scale
class TSC(Screen, FloatLayout, ButtonBehavior):
	def __init__(self, **kwargs):
		super(TSC, self).__init__(**kwargs)
		self.radioButtonQ1 = []
		self.radioButtonQ2 = []
		self.radioButtonQ3 = []
		self.radioButtonQ4 = []
		self.responseQ1 = ""
		self.responseQ2 = ""
		self.responseQ3 = ""
		self.responseQ4 = ""
		self.index = int(self.name[-1])

		#button 'NEXT'
		self.button = Button(text="NEXT", pos_hint={"right":0.6, "top":0.15}, size_hint=(0.2, 0.1), font_size=sp(25), color=(1,1,1,1))
		self.add_widget(self.button)
		self.button.bind(on_release=self.on_press)
		#Q1
		self.question1= Label(text="", size_hint=(0.2,0.1), pos_hint={"right":0.6, "top":0.97}, font_size=sp(20))
		self.labelQ11 = Label(text="Not at all", size_hint=(0.10, 0.10), pos_hint={"right":0.17, "top":0.89}, font_size=sp(18), color=(1,1,1,1))
		self.labelQ12 = Label(text="Very much", size_hint=(0.10,0.10), pos_hint={"right":0.945, "top":0.89}, font_size=sp(18), color=(1,1,1,1))
		self.add_widget(self.question1)
		self.add_widget(self.labelQ11)
		self.add_widget(self.labelQ12)
		for i in range(0,7):
				self.radioButtonQ1.append(Grid(id ="Q1", group='groupQ1', number=i+1,
				background_radio_normal='radiobutton.png', size_hint=(0.05, 0.05), pos_hint={"right":0.23+i*0.10, "top":0.87}))
				self.add_widget(self.radioButtonQ1[-1])
				self.radioButtonQ1[-1].bind(active=self.checkActiveQ1)

		if self.name != "tsc4":
				#Q2
				self.question2 = Label(text="", size_hint=(0.2, 0.1), pos_hint={"right":0.6, "top":0.77}, font_size=sp(20))
				self.labelQ21 = Label(text="Not at all", size_hint=(0.10, 0.10), pos_hint={"right":0.17, "top":0.69}, font_size=sp(18), color=(1,1,1,1))
				self.labelQ22 = Label(text="Very much", size_hint=(0.10, 0.10), pos_hint={"right":0.945, "top":0.69}, font_size=sp(18), color=(1,1,1,1))
				self.add_widget(self.question2)
				self.add_widget(self.labelQ21)
				self.add_widget(self.labelQ22)
				for i in range(0,7):
						self.radioButtonQ2.append(Grid(id ="Q2", group='groupQ2', number=i+1,
						background_radio_normal='radiobutton.png', size_hint=(0.05,0.05), pos_hint={"right":0.23+i*0.10, "top":0.67}))
						self.add_widget(self.radioButtonQ2[-1])
						self.radioButtonQ2[-1].bind(active=self.checkActiveQ2)
				#Q3
				self.question3 = Label(text="", size_hint=(0.2, 0.1), pos_hint={"right":0.6, "top":0.57}, font_size=sp(20))
				self.labelQ31 = Label(text="Not at all", size_hint=(0.10, 0.10), pos_hint={"right":0.17, "top":0.49}, font_size=sp(18), color=(1,1,1,1))
				self.labelQ32 = Label(text="Very much", size_hint=(0.10, 0.10), pos_hint={"right":0.945, "top":0.49}, font_size=sp(18), color=(1,1,1,1))
				self.add_widget(self.question3)
				self.add_widget(self.labelQ31)
				self.add_widget(self.labelQ32)
				for i in range(0,7):
						self.radioButtonQ3.append(Grid(id ="Q3", group='groupQ3', number=i+1,
						background_radio_normal='radiobutton.png', size_hint=(0.05, 0.05), pos_hint={"right":0.23+i*0.10, "top":0.47}))
						self.add_widget(self.radioButtonQ3[-1])
						self.radioButtonQ3[-1].bind(active=self.checkActiveQ3)
				#Q4
				self.question4 = Label(text="", size_hint=(0.2, 0.1), pos_hint={"right":0.6, "top":0.37}, font_size=sp(20))
				self.labelQ41 = Label(text="Not at all", size_hint=(0.10, 0.10), pos_hint={"right":0.17, "top":0.29}, font_size=sp(18),color=(1,1,1,1))
				self.labelQ42 = Label(text="Very much", size_hint=(0.10, 0.10), pos_hint={"right":0.945, "top":0.29}, font_size=sp(18), color=(1,1,1,1))
				self.add_widget(self.question4)
				self.add_widget(self.labelQ41)
				self.add_widget(self.labelQ42)
				for i in range(0,7):
						self.radioButtonQ4.append(Grid(id ="Q4", group='groupQ4', number=i+1,
						background_radio_normal='radiobutton.png', size_hint=(0.05, 0.05),pos_hint={"right":0.23+i*0.10, "top":0.27}))
						self.add_widget(self.radioButtonQ4[-1])
						self.radioButtonQ4[-1].bind(active=self.checkActiveQ4)
		else:
				self.responseQ2 = float("nan")
				self.responseQ3 = float("nan")
				self.responseQ4 = float("nan")
				pass

	def checkActiveQ1(self,grid,*args):
		if grid.active:
				self.responseQ1 = grid.number
	def checkActiveQ2(self,grid,*args):
		if grid.active:
				self.responseQ2 = grid.number
	def checkActiveQ3(self,grid,*args):
		if grid.active:
				self.responseQ3 = grid.number
	def checkActiveQ4(self,grid,*args):
		if grid.active:
				self.responseQ4 = grid.number

	def getQuestion(self, Q1, Q2, Q3, Q4):
		self.question1.text = Q1
		if self.name != "tsc4":
				self.question2.text = Q2
				self.question3.text = Q3
				self.question4.text = Q4
		else:
				pass

	def on_press(self, instance):
		if self.responseQ1 != "" and self.responseQ2 != "" and self.responseQ3 != "" and self.responseQ4 != "":
				self.leave_time = str(datetime.now().time())
				saveData[self.name] = {"Q1":self.responseQ1, "Q2":self.responseQ2, "Q3":self.responseQ3, "Q4":self.responseQ4, "leave_time":self.leave_time}
				if self.name == "tsc4":
						App.get_running_app().root.current = "logout"
				else:
						App.get_running_app().root.current = "tsc"+str(self.index+1)
		else:
				popup_survey.open()


# items in the scale
items = [
	"I am good at resisting temptation.",
	"I have a hard time breaking bad habits.",
	"I am lazy.",
	"I say inappropriate things.",
	"I do certain things that are bad for me, if they are fun.",
	"I wish I had more self-discipline.",
	"Pleasure and fun somethimes keep me from getting work done.",
	"I have trouble concentrating.",
	"I am able to work effectively towards long-term goals.",
	"Sometimes I cant stop myself from doing something, even if I know it is wrong.",
	"I often act without thinking through all the alternatives.",
	"I refuse things that are bad for me.",
	"People would say that I have iron self-discipline."
]

tsc1 = TSC(name="tsc1")
tsc2 = TSC(name="tsc2")
tsc3 = TSC(name="tsc3")
tsc4 = TSC(name="tsc4")
tsc1.getQuestion(items[0], items[1], items[2], items[3])
tsc2.getQuestion(items[4], items[5], items[6], items[7])
tsc3.getQuestion(items[8], items[9], items[10], items[11])
tsc4.getQuestion(items[12], "", "", "")


## Build the app
class MouseTrackApp(App):
	def build(self):
		ScreenM = ScreenManager(transition=WipeTransition())
		ScreenM.add_widget(login)	
		ScreenM.add_widget(survey1)
		ScreenM.add_widget(survey2)
		ScreenM.add_widget(survey3)
		ScreenM.add_widget(tsc1)
		ScreenM.add_widget(tsc2)
		ScreenM.add_widget(tsc3)
		ScreenM.add_widget(tsc4)
		ScreenM.add_widget(logout)
		ScreenM.add_widget(lastPage)

		return ScreenM

	def on_pause(self):
		return True

	def on_resume(self):
		pass

if __name__ == "__main__":
	MouseTrackApp().run()
