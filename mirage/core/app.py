import os
from string import Template
from typing import Dict, Any, List, Optional
from mirage.core import interpreter, loader, taskManager, module, config, templates
from mirage.core.module import WirelessModule
from mirage.libs import io, utils, wireless
from mirage.core.config import config
from mirage.libs.logger import logger

class App(interpreter.Interpreter):
	'''
	This class defines the main Application.
	It inherits from ``core.interpreter.Interpreter``, allowing to use Mirage as a command line interpreter.

	'''
	class SetParameterException(Exception):
		"""Base exception for parameter setting errors."""
		pass

	class NoModuleLoaded(SetParameterException):
		"""Exception raised when no module is loaded."""
		pass

	class IncorrectParameter(SetParameterException):
		"""Exception raised when an incorrect parameter is provided."""
		pass

	class MultipleModulesLoaded(SetParameterException):
		"""Exception raised when multiple modules are loaded."""
		pass

	Instance: Optional['App'] = None

	def __init__(self, quiet: bool = False, home_dir: str = "/home/user/.mirage", temp_dir: str = "/tmp/mirage"):
		'''
		Initialize the main attributes and software components used by the framework.

		:param quiet: boolean indicating if Mirage has been launched in quiet mode
		:param home_dir: string indicating the location of the home directory
		:param temp_dir: string indicating the location of the temporary directory
		'''
		super().__init__()
		App.Instance = self
		self.available_commands: List[str] = [
						"start",
						"stop",
						"restart",
						"tasks",
						"clear",
						"list",
						"load",
						"set",
						"run",
						"args",
						"shortcuts",
						"showargs",
						"info",
						"create_module",
						"create_scenario",
						"config"
					]
		self.quiet: bool = quiet
		self.debug_mode: bool = config.get("debug_mode", False)
		self.temp_dir: str = temp_dir
		self.home_dir: str = home_dir
		self.config: config.Config = config.Config(f"{home_dir}/mirage.cfg")
		self.loader: loader.Loader = loader.Loader()
		self.loaded_shortcuts: Dict[str, Any] = self.config.getShortcuts()
		self.modules: List[Dict[str, Any]] = []
		self.task_manager: taskManager.TaskManager = taskManager.TaskManager()
		# Creation of the temporary directory
		if not os.path.exists(self.temp_dir):
			os.mkdir(self.temp_dir)

		logger.info(f"Mirage initialized with home directory: {self.home_dir}")

	def exit(self) -> None:
		'''
		Exit the framework.
		'''
		try:
			self.task_manager.stopAllTasks()

			for emitter in module.WirelessModule.Emitters.values():
				emitter.stop()
			for receiver in module.WirelessModule.Receivers.values():
				receiver.stop()

			utils.stopAllSubprocesses()
			io.info("Mirage process terminated!")
		except Exception as e:
			io.error(f"Error during exit: {str(e)}")
		finally:
			super().exit()

	def start(self, task: str) -> None:
		'''
		Start a specific background task according to its name.

		:param task: Task to start
		'''
		try:
			self.task_manager.startTask(task)
		except Exception as e:
			io.error(f"Failed to start task {task}: {str(e)}")

	def stop(self, task: str) -> None:
		'''
		Stop a specific background task according to its name.

		:param task: Task to stop
		'''
		try:
			self.task_manager.stopTask(task)
		except Exception as e:
			io.error(f"Failed to stop task {task}: {str(e)}")

	def restart(self, task: str) -> None:
		'''
		Restart a specific background task according to its name.

		:param task: Task name to restart
		'''
		try:
			self.task_manager.restartTask(task)
		except Exception as e:
			io.error(f"Failed to restart task {task}: {str(e)}")

	def tasks(self, pattern: str = "") -> None:
		'''
		Display the existing background tasks. A string pattern can be provided as a filter.

		:param pattern: Filter
		'''
		try:
			io.chart(["PID", "Name", "State", "Output"], self.task_manager.getTasksList(pattern), "Background Tasks")
		except Exception as e:
			io.error(f"Failed to retrieve tasks: {str(e)}")

	def create_scenario(self) -> None:
		'''
		Interact with the user to easily generate a user scenario.
		'''
		name = ""
		while name == "":
			name = io.ask("Scenario's name")
			if name == "":
				io.fail("Scenario's name cannot be empty!")

		scenario = Template(templates.__scenario_template__)
		scenario_content = scenario.substitute(name=name)
		scenario_filename = f"{self.home_dir}/scenarios/{name}.py"
		try:
			with open(scenario_filename, 'w') as f:
				f.write(scenario_content)
			io.success(f"Scenario {name} successfully generated: {scenario_filename}")
		except Exception as e:
			io.error(f"Failed to create scenario: {str(e)}")

	def create_module(self) -> None:
		'''
		Interact with the user to easily generate a user module.
		'''
		name = ""
		while name == "":
			name = io.ask("Module's name")
			if name == "":
				io.fail("Module's name cannot be empty!")
		description = io.ask("Module's description")

		type = io.ask("Module's type")

		technology = io.ask("Module's technology", default="ble")

		dependencies = io.ask("Module's dependencies (separated by commas)").replace(" ", "")
		if dependencies != "":
			dependencies = ",".join(['"' + dep + '"' for dep in dependencies.split(",")])

		arguments = {}
		arg_number = 1
		while True:
			arg_name = io.ask(f"Input parameter #{arg_number} (name)").upper()
			if arg_name == "":
				break
			arg_value = io.ask(f"Input parameter #{arg_number} (default value)")
			arguments[arg_name] = arg_value
			arg_number += 1

		module = Template(templates.__module_template__)
		module_content = module.substitute(
					name=name,
					description=description,
					technology=technology,
					type=type,
					dependencies=dependencies,
					arguments=str(arguments))
		module_filename = f"{self.home_dir}/modules/{name}.py"
		try:
			with open(module_filename, 'w') as f:
				f.write(module_content)
			io.success(f"Module {name} successfully generated: {module_filename}")
		except Exception as e:
			io.error(f"Failed to create module: {str(e)}")

	def loop(self) -> None:
		'''
		Run the main interpreter loop.
		'''
		if not self.quiet:
			io.banner()
		interpreter.Interpreter.loop(self)

	def clear(self) -> None:
		'''
		Clear the screen.
		'''
		os.system("clear")

	def list(self, pattern: str = "") -> None:
		'''
		List the different modules available in the framework. A string pattern can be provided as a filter.

		:param pattern: Filter
		'''
		try:
			self.loader.list(pattern)
		except Exception as e:
			io.error(f"Failed to list modules: {str(e)}")

	def shortcuts(self, pattern: str = "") -> None:
		'''
		List the different shortcuts available in the framework. A string pattern can be provided as a filter.

		:param pattern: Filter
		'''
		shortcuts = []
		for shortcut_name, shortcut in self.loaded_shortcuts.items():
			if (pattern == "" or
				pattern in shortcut_name or
				pattern in shortcut["description"] or
				pattern in shortcut["modules"]):
				shortcuts.append([shortcut_name, shortcut["modules"], shortcut["description"]])
		if shortcuts != []:
			io.chart(["Name", "Modules", "Description"], shortcuts, "Shortcuts")
		else:
			io.fail("No shortcut found!")

	def _autocompleteModules(self) -> List[str]:
		'''
		Generate the list of available modules for autocompletion of the "load" command.
		'''
		try:
			return self.loader.getModulesNames() + list(self.loaded_shortcuts.keys())
		except Exception as e:
			io.error(f"Failed to autocomplete modules: {str(e)}")
			return []

	def load(self, module_name: str) -> None:
		'''
		Load a module according to its name.
		It allows to load a sequence of modules by using the pipe (``|``) symbol.

		:param module_name: name of the module (or sequence of modules) to load

		:Example:

		>>> app.load('ble_info')
		>>> app.load('ble_connect|ble_discover')

		'''
		modules = module_name.split("|") if "|" in module_name else [module_name]
		tmp_modules = []
		counter = 1
		no_error = True
		for m in modules:
			output = self.loader.load(m)
			if output is not None:
				io.info(f"Module {m} loaded!")
				tmp_modules.append({"name": m + str(counter) if len(modules) > 1 else m, "module": output})
				counter += 1

				for argument in output.args:
					if self.config.dataExists(m, argument):
						output.args[argument] = self.config.getData(m, argument)

			elif m in self.loaded_shortcuts:
				io.info(f"Shortcut {m} loaded!")
				shortcut_modules = []
				shortcut_classes = []
				shortcut_counter = 1
				shortcut_modules_list = self.loaded_shortcuts[m]["modules"].split("|")
				for n in shortcut_modules_list:
					output = self.loader.load(n)
					shortcut_modules.append({
						"name": n + str(shortcut_counter) if len(shortcut_modules_list) > 1 else n,
						"module": output
					})
					for argument in self.loaded_shortcuts[m]["mapping"]:
						mapping = self.loaded_shortcuts[m]["mapping"][argument]
						if mapping["value"] is not None:
							self._set(argument, mapping["value"], [shortcut_modules[-1]])

					shortcut_counter += 1

				tmp_modules.append({
						"name": m + str(counter) if len(modules) > 1 else m,
						"shortcut": shortcut_modules,
						"mapping": self.loaded_shortcuts[m]["mapping"]
						})
				counter += 1
			else:
				io.fail(f"Unknown module {m}!")
				no_error = False
				break
		if no_error:
			self.modules = tmp_modules
			self.prompt = io.colorize(f" << {module_name} >>~~> ", "cyan")

	def _autocompleteParameters(self) -> List[str]:
		'''
		Generate a list including the available parameters names for autocompletion of the "set" command.
		'''
		if len(self.modules) == 0:
			return []
		elif len(self.modules) == 1:
			if "module" in self.modules[0]:
				return self.modules[0]["module"].args.keys()
			elif "shortcut" in self.modules[0]:
				return self.modules[0]["mapping"].keys()
		else:
			parameters = []
			for module in self.modules:
				if "module" in module and module["module"] is not None:
					parameters += [module["name"] + "." + i for i in module["module"].args.keys()]
				elif "shortcut" in module:
					parameters += [module["name"] + "." + i for i in module["mapping"].keys()]
			return parameters

	def _set(self, name: str, value: Any, modules_list: List[Dict[str, Any]]) -> bool:
		if len(modules_list) == 0:
			raise self.NoModuleLoaded()
			return False
		elif len(modules_list) == 1:
			module = modules_list[0]
			if "module" in module and module["module"] is not None:
				if module["module"].dynamicArgs or name in module["module"].args:
					module["module"].args[name] = value
					return True
				elif (name in wireless.SDRDevice.SDR_PARAMETERS.keys() and
					isinstance(module["module"], WirelessModule)):
					module["module"].sdrConfig[name] = value
					return True
				else:
					raise self.IncorrectParameter()
			elif "shortcut" in module:
				if name in module["mapping"]:
					shortcut_mapping = module["mapping"][name]
					success = True
					for parameters_name in shortcut_mapping["parameters"]:
						success = success and self._set(parameters_name, value, module["shortcut"])
					if (success):
						shortcut_mapping["value"] = value

					return success
				else:
					raise self.IncorrectParameter()
					return False
			else:
				return False
		else:
			if "." in name:
				(module_name, arg_name) = name.split(".")
				for module in modules_list:
					if "module" in module and module["module"] is not None and module_name == module["name"]:
						return self._set(arg_name, value, [module])
					elif "shortcut" in module and module_name == module["name"]:
						if arg_name in module["mapping"]:
							shortcut_mapping = module["mapping"][arg_name]
							success = True
							for parameters_name in shortcut_mapping["parameters"]:
								success = success and self._set(parameters_name, value, module["shortcut"])
							if (success):
								shortcut_mapping["value"] = value
							return success
						else:
							raise self.IncorrectParameter()
							return False

			else:
				raise self.MultipleModulesLoaded()
				return False

	def set(self, name: str, value: Any) -> None:
		'''
		Provide a value for a specific input parameter of the loaded module.

		:param name: parameter's name
		:param value: value of parameter

		:Example:

		>>> app.set("INTERFACE", "hci0")
		>>> app.set("ble_connect1.INTERFACE", "hci0")

		'''
		try:
			self._set(name, value, self.modules)
		except self.NoModuleLoaded:
			io.fail("No module loaded!")
		except self.MultipleModulesLoaded:
			io.fail("No corresponding parameter! Multiple modules are loaded, did you indicate the module's name?")
		except self.IncorrectParameter:
			io.fail("No corresponding parameter!")
		except Exception as e:
			io.error(f"Failed to set parameter: {str(e)}")

	def showargs(self) -> None:
		'''
		Display a chart describing the available input parameters for the loaded module.
		'''
		for module in self.modules:
			current_args = []
			if "shortcut" not in module:
				for argument in module["module"].args:
					arg_name = (module["name"] + "." + argument) if len(self.modules) > 1 else argument
					arg_value = module["module"].args[argument]
					current_args.append([arg_name, arg_value])
				io.chart(["Name", "Value"], current_args, io.colorize(module["name"], "yellow"))
			else:
				for argument in module["mapping"]:
					arg_name = (module["name"] + "." + argument) if len(self.modules) > 1 else argument
					if module["mapping"][argument]["value"] is not None:
						arg_value = module["mapping"][argument]["value"]
					else:
						arg_value = "<auto>"
					current_args.append([arg_name, arg_value])
				io.chart(["Name", "Value"], current_args, io.colorize(module["name"], "green"))

	def args(self) -> None:
		'''
		Alias for ``showargs``.
		'''
		self.showargs()

	def info(self) -> None:
		'''
		Display information about the loaded module, such as the name, technology used, etc.
		'''
		for module in self.modules:
			if "module" in module and module["module"] is not None:
				infos = module["module"].info()
				content = [infos["name"], infos["technology"], infos["type"], infos["description"]]
				io.chart(["Name", "Technology", "Type", "Description"], [content], module["name"])
			elif "shortcut" in module and module["shortcut"] is not None:
				name = module["name"].strip("0123456789")
				description = self.loaded_shortcuts[name]["description"]
				modules = self.loaded_shortcuts[name]["modules"]
				io.chart(["Name", "Modules", "Description"], [[name, modules, description]], module["name"] + " (shortcut)")

	def run(self) -> None:
		'''
		Run the loaded module with the input parameters provided.
		'''
		args = {}
		for module in self.modules:
			if "module" in module and module["module"] is not None:
				for arg in args:
					if arg in module["module"].args or module["module"].dynamicArgs:
						module["module"].args[arg] = args[arg]
				output = module["module"].execute()
				if not output["success"]:
					io.fail(f"Execution of module {module['name']} failed!")
					break
				else:
					args.update(output["output"])
			elif "shortcut" in module:
				for shortcut_module in module["shortcut"]:
					for arg in args:
						if arg in shortcut_module["module"].args or shortcut_module["module"].dynamicArgs:
							shortcut_module["module"].args[arg] = args[arg]
					output = shortcut_module["module"].execute()
					if not output["success"]:
						io.fail(f"Execution of shortcut {module['name']} failed!")
						break
					else:
						args.update(output["output"])

	def config(self, key: Optional[str] = None, value: Optional[str] = None) -> None:
		"""
		Get or set configuration values.

		Usage:
			config                 - Display all configuration
			config <key>           - Get a specific configuration value
			config <key> <value>   - Set a specific configuration value
		"""
		if key is None:
			logger.info("Current configuration:")
			for k, v in config.config.items():
				logger.info(f"{k}: {v}")
		elif value is None:
			logger.info(f"{key}: {config.get(key)}")
		else:
			config.set(key, value)
			logger.info(f"Set {key} to {value}")