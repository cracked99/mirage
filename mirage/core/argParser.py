from mirage.libs import io
import sys
from typing import List, Optional

class ArgParser:
	'''
	This class allows to easily parse parameters from command line.
	'''
	def __init__(self, app_instance: Optional['App'] = None):
		'''
		This constructor allows to keep a pointer on the main Application instance.
		
		:param app_instance: instance of the main Application (core.app.App)
		:type app_instance: core.app.App
		'''
		self.app_instance = app_instance


	def debug(self) -> None:
		'''
		This method checks if the debug parameter has been provided by the user on the command line.
		It will modify the attribute ``debugMode`` stored in the provided instance of core.app.App.
		'''
		if "--debug" in sys.argv:
			self.app_instance.debugMode = True
			sys.argv.remove("--debug")


	def quiet(self) -> None:
		'''
		This method checks if the quiet parameter has been provided by the user on the command line.
		It will modify the attribute ``quiet`` stored in the provided instance of core.app.App.
		'''
		if "--quiet" in sys.argv:
			self.app_instance.quiet = True
			sys.argv.remove("--quiet")

	def verbosity(self) -> None:
		'''
		This method checks if the verbosity parameter has been provided by the user on the command line.
		It will modify the variable ``VERBOSITY_LEVEL`` stored in libs.io.
		'''
		verbosity = [arg for arg in sys.argv if "--verbosity=" in arg]
		if len(verbosity) > 0:
			(_,value) = verbosity[-1].split("--verbosity=")
			if value.upper() == "NONE" or value == "0":
				io.VERBOSITY_LEVEL = io.VerbosityLevels.NONE
			elif value.upper() == "NO_INFO_AND_WARNING" or value == "1":
				io.VERBOSITY_LEVEL = io.VerbosityLevels.NO_INFO_AND_WARNING
			elif value.upper() == "NO_INFO" or value=="2":
				io.VERBOSITY_LEVEL = io.VerbosityLevels.NO_INFO
			else:
				io.VERBOSITY_LEVEL = io.VerbosityLevels.ALL

		for arg in sys.argv:
			if "--verbosity=" in arg:
				sys.argv.remove(arg)


	def create_module(self) -> bool:
		'''
		This method checks if the create_module parameter has been provided by the user on the command line.
		It will call the method ``create_module`` of the main application instance (core.app.App).
		'''
		if "--create_module" in sys.argv:
			self.app_instance.create_module()
			return True
		return False

	def create_scenario(self) -> bool:
		'''
		This method checks if the create_scenario parameter has been provided by the user on the command line.
		It will call the method ``create_scenario`` of the main application instance (core.app.App).
		'''
		if "--create_scenario" in sys.argv:
			self.app_instance.create_scenario()
			return True
		return False

	def list(self) -> bool:
		'''
		This method checks if the list parameter has been provided by the user on the command line.
		It will call the method ``list`` of the main application instance (core.app.App).
		'''
		if "--list" in sys.argv:
			self.app_instance.list()
			return True
		else:
			app_list = [arg for arg in sys.argv if "--list=" in arg]
			if len(app_list) > 0:
				(_,pattern) = app_list[-1].split("--list=")
				self.app_instance.list(pattern=pattern)
				return True
		return False

	def launcher(self) -> None:
		'''
		This method checks if a Mirage module to run has been provided by the user on the command line.
		It will load and run the corresponding module with the parameters provided by the user.

		:Example:

		``./mirage.py moduleName PARAMETER1=value1 PARAMETER2=value2 PARAMETER3=value3``

		'''
		module = sys.argv[1]
		self.app_instance.load(module)
		if len(self.app_instance.modules) > 0:
			if "--args" in sys.argv or "--showargs" in sys.argv:
				self.app_instance.args()
				exit(1)
			else:
				for arg in sys.argv[2:]:
					arg = arg.split("=", 1)
					if len(arg) == 2:
						(name,value) = arg
						self.app_instance.set(name,value)
					else:
						io.fail("Incorrect parameter : "+str(arg))
						exit(1)
			self.app_instance.run()
			self.app_instance.exit()


	def run(self) -> None:
		''' 
		This method checks if Mirage has been launched with some parameters.
		- If no Mirage module has been provided by the user on the command line, it will launch the main application loop
			(method ``loop`` of core.app.App)
		- If a Mirage module has been provided by the user, it calls the method ``launcher`` of core.argParser.ArgParser.
		
		'''	
		self.debug()	
		self.quiet()
		self.verbosity()
		if self.create_module() or self.create_scenario():
			self.app_instance.exit()		
		elif not self.list():
			if len(sys.argv) == 1:
				self.app_instance.loop()
			else:
				self.launcher()

