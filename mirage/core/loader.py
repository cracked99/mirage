from mirage.libs import io
from typing import Dict, Any, List, Optional
import importlib

class Loader:
	'''
	This class permits to dynamically load the modules.
	'''
	def __init__(self):
		'''
		This constructor generates the modules list.
		'''
		import mirage.modules as modules
		self.modulesList: Dict[str, Any] = {}
		for moduleName, module in modules.__modules__.items():
			try:
				moduleClass = getattr(module, moduleName)
				self.modulesList[moduleName] = moduleClass
			except AttributeError:
				io.error(f"Failed to load module {moduleName}: module class not found")

	def getModulesNames(self) -> List[str]:
		'''
		This method returns a list of existing modules' names.

		:return: list of modules' name
		:rtype: list of str
		'''
		return list(self.modulesList.keys())

	def load(self, moduleName: str) -> Optional[Any]:
		'''
		This method returns an instance of a specific module according to the name provided as parameter.

		:param moduleName: name of a module
		:type moduleName: str
		:return: an instance of the module
		:rtype: core.module.Module
		'''
		try:
			if moduleName in self.modulesList:
				return self.modulesList[moduleName]()
			else:
				io.fail(f"Module {moduleName} not found")
				return None
		except Exception as e:
			io.error(f"Failed to load module {moduleName}: {str(e)}")
			return None

	def list(self, pattern: str = "") -> None:
		'''
		Display the list of module, filtered by the string provided as ``pattern``.

		:param pattern: filter
		:type pattern: str
		'''
		displayDict: Dict[str, List[List[str]]] = {}

		for module in self.modulesList:
			try:
				info = self.modulesList[module]().info()
				technology = (info["technology"][:1]).upper() + (info["technology"][1:]).lower()
				if (
					pattern in info["description"] or
					pattern in info["name"] or
					pattern in info["technology"] or
					pattern in info["type"]
				):
					if technology not in displayDict:
						displayDict[technology] = []
					displayDict[technology].append([info["name"], info["type"], info["description"]])
			except Exception as e:
				io.error(f"Failed to get info for module {module}: {str(e)}")

		for module in sorted(displayDict):
			if displayDict[module]:
				io.chart(["Name", "Type", "Description"], sorted(displayDict[module]), f"{module} Modules")
