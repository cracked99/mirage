import traceback
from mirage.core import module,app
from mirage.libs import io
from typing import Any, Optional, Callable

class Scenario:
	'''
	This class defines a scenario. A Scenario is a Mirage entity allowing to customize the behaviour of a module without 
	modifying its code, and can be compared to a list of callbacks called when a specific event (or signal) happens.
	'''
	def __init__(self,name: str = "",module: Optional[module.Module] = None):
		'''
		This constructor allows to define the main attributes of a scenario, especially :
		- name : name of the scenario
		- description : description of the scenario
		- module : the associated module instance
		- args : the arguments of the associated module

		:param name: name of the scenario
		:param module: associated module instance
		'''
		self.name: str = name if name != "" else self.__class__.__name__
		self.description: str = "A generic collection of callbacks"
		self.module: Optional[module.Module] = module
		self.args: Dict[str, Any] = module.args if module else {}
		


	def receiveSignal(self,signal: str,*args: Any, **kwargs: Any) -> Optional[bool]:
		'''
		This method is called when a signal is received, and calls the corresponding method in the scenario if it exists.
		'''
		if signal in [i for i in dir(self) if "__" not in i]:
			try:
				defaultBehaviour = getattr(self,signal)(*args,**kwargs)
				return defaultBehaviour
			except Exception as e:
				if not hasattr(self,signal):
					io.fail(f"Non matching method in scenario {self.name}")
				else:
					io.fail(f"An error occurred in scenario {self.name}!")
					if app.App.Instance.debug_mode:
			    			traceback.print_exception(type(e), e, e.__traceback__)
		else:
			return True

def scenarioSignal(argument: str) -> Callable:
	'''
	Decorator allowing to link a module's method to a specific signal.

	:param argument: signal name
	'''
	def signalDecorator(function: Callable) -> Callable:
		def wrapper(self: Any,*args: Any, **kwargs: Any) -> Any:
			if hasattr(self,"scenario"):
				defaultBehaviour = self.scenario.receiveSignal(argument,*args,**kwargs)
			else:
				defaultBehaviour = True
			if defaultBehaviour is None or defaultBehaviour:
				result = function(self,*args,**kwargs)
			else:
				result = None	
			return result
		return wrapper
	return signalDecorator