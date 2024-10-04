import configparser
import os
import json
from typing import Dict, Any, Optional
from mirage.libs import io

class Config:
	"""
	This class is used to parse and generate a configuration file in ".cfg" format.
	It also provides a centralized configuration system for the framework.

	Attributes:
		config_dir (str): The directory where the configuration file is stored.
		config_file (str): The path to the configuration file.
		parser (configparser.ConfigParser): The parser for the configuration file.
		datas (Dict[str, Dict[str, str]]): The parsed data from the configuration file.
		shortcuts (Dict[str, Dict[str, Any]]): The parsed shortcuts from the configuration file.
		config (Dict[str, Any]): The main configuration dictionary.
	"""

	_instance = None

	def __new__(cls):
		if cls._instance is None:
			cls._instance = super(Config, cls).__new__(cls)
			cls._instance._initialize_config()
		return cls._instance

	def _initialize_config(self):
		"""Initialize the configuration system."""
		self.config_dir = os.path.join(os.path.expanduser('~'), '.mirage')
		self.config_file = os.path.join(self.config_dir, 'config.json')
		self.parser = configparser.ConfigParser()
		self.datas: Dict[str, Dict[str, str]] = {}
		self.shortcuts: Dict[str, Dict[str, Any]] = {}
		self.config: Dict[str, Any] = {}

		if not os.path.exists(self.config_dir):
			os.makedirs(self.config_dir)

		if os.path.exists(self.config_file):
			with open(self.config_file, 'r') as f:
				self.config = json.load(f)
		else:
			self._create_default_config()

		self.generateDatas()
		self.generateShortcuts()

	def _create_default_config(self):
		"""Create a default configuration if no configuration file exists."""
		default_config = {
			"debug_mode": False,
			"log_level": "INFO",
			"default_interface": "hci0",
			"auto_save_pcap": False,
			"pcap_directory": os.path.join(self.config_dir, 'pcap'),
		}
		self.config = default_config
		self._save_config()

	def _save_config(self):
		"""Save the current configuration to the config file."""
		with open(self.config_file, 'w') as f:
			json.dump(self.config, f, indent=4)

	def generateDatas(self) -> None:
		"""
		Parse the configuration file and store the corresponding arguments in the attribute ``datas``.
		
		Raises:
			configparser.ParsingError: If there's an error parsing the configuration file.
		"""
		try:
			self.parser.read(self.config_file)
			for module in self.parser.sections():
				if "shortcut:" not in module:
					arguments = {key.upper(): value for key, value in self.parser.items(module)}
					self.datas[module] = arguments
		except configparser.ParsingError:
			io.fail("Bad format file!")

	def generateShortcuts(self) -> None:
		"""
		Parse the configuration file and store the corresponding arguments in the attribute ``shortcuts``.
		
		Raises:
			configparser.ParsingError: If there's an error parsing the configuration file.
		"""
		try:
			self.parser.read(self.config_file)
			for section in self.parser.sections():
				if "shortcut:" in section:
					shortcut_name = section.split("shortcut:")[1]
					modules = None
					description = ""
					arguments = {}
					for key, value in self.parser.items(section):
						if key.upper() == "MODULES":
							modules = value
						elif key.upper() == "DESCRIPTION":
							description = value
						else:
							if "(" in value and ")" in value:
								names = value.split("(")[0]
								default_value = value.split("(")[1].split(")")[0]

								arguments[key.upper()] = {
											"parameters": names.split(","),
											"value": default_value
								}
							else:
								arguments[key.upper()] = {
											"parameters": value.split(","),
											"value": None
								}
					if modules is not None:
						self.shortcuts[shortcut_name] = {"modules": modules, "description": description, "mapping": arguments}
		except configparser.ParsingError:
			io.fail("Bad format file!")

	def getShortcuts(self) -> Dict[str, Dict[str, Any]]:
		"""
		Returns the shortcuts loaded from the configuration file.

		:return: dictionary listing the existing shortcuts
		:rtype: dict
		"""
		return self.shortcuts

	def dataExists(self, module_name: str, arg: str) -> bool:
		"""
		Checks if a value has been provided in the configuration file for the argument ``arg`` of the module
		named according to ``module_name``.

		:param module_name: name of the module
		:type module_name: str
		:param arg: name of the argument
		:type arg: str
		:return: boolean indicating if a value has been provided
		:rtype: bool
		"""
		return module_name in self.datas and arg in self.datas[module_name]

	def getData(self, module_name: str, arg: str) -> str:
		"""
		Returns the value provided in the configuration file for the argument ``arg`` of the module
		named according to ``module_name``.

		:param module_name: name of the module
		:type module_name: str
		:param arg: name of the argument
		:type arg: str
		:return: value of the parameter
		:rtype: str
		
		Raises:
			KeyError: If the module or argument doesn't exist in the configuration.
		"""
		try:
			return self.datas[module_name][arg]
		except KeyError:
			io.fail(f"Module '{module_name}' or argument '{arg}' not found in configuration.")
			raise

	def get(self, key: str, default: Any = None) -> Any:
		"""
		Get a configuration value.

		:param key: Configuration key
		:param default: Default value if key is not found
		:return: Configuration value
		"""
		return self.config.get(key, default)

	def set(self, key: str, value: Any) -> None:
		"""
		Set a configuration value.

		:param key: Configuration key
		:param value: Configuration value
		"""
		self.config[key] = value
		self._save_config()

config = Config()