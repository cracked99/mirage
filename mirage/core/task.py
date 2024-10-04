from mirage.libs import utils
import multiprocessing
import os
import sys
from ctypes import c_char_p
from typing import List, Any, Callable, Optional

class Task(multiprocessing.Process):
	'''
	This class defines a background Task, it inherits from ``multiprocessing.Process``.
	It provides an user friendly API to easily run a given function in background.
	'''
	def __init__(self, function: Callable, name: str, args: List[Any] = [], kwargs: dict = {}):
		'''
		This constructor allows to provide the main characteristics of the task, and initializes the attributes.
		
		:param function: function to run in background
		:type function: function
		:param name: name of the current task
		:type name: str
		:param args: list of unnamed arguments
		:type args: list
		:param kwargs: dictionary of named arguments
		:type kwargs: dict
		'''
		self.function: Callable = function
		self.taskName: str = name
		self.args: List[Any] = args
		self.kwargs: dict = kwargs
		self.manager = multiprocessing.Manager()
		self.state = self.manager.Value(c_char_p, "stopped")
		self.outputFilename: str = ""
		self.outputFile: Optional[Any] = None
		super().__init__()

	def run(self) -> None:
		'''
		This method runs the specified function in background.
		
		.. note:: The standard output is automatically redirected in a temporary file, named ``<taskName>-<taskPID>.out``
		'''
		self.outputFilename = f"{utils.getTempDir()}/{self.taskName}-{os.getpid()}.out"
		self.outputFile = open(self.outputFilename, 'a')
		sys.stdout = self.outputFile
		try:
			self.function(*(self.args), **(self.kwargs))
		except Exception as e:
			print(f"Error in task {self.taskName}: {str(e)}")
		finally:
			self.state.value = "ended"
			if self.outputFile:
				self.outputFile.close()

	def start(self) -> None:
		'''
		This method allows to start the current task.
		'''
		self.state.value = "running"
		super().start()
		self.outputFilename = f"{utils.getTempDir()}/{self.taskName}-{self.pid}.out"

	def stop(self) -> None:
		'''
		This method allows to stop the current task.
		'''
		self.state.value = "stopped"
		self.terminate()
		if self.outputFile is not None:
			self.outputFile.close()

	def toList(self) -> List[str]:
		'''
		This method returns a list representing the current task.
		It is composed of :

			* the task's PID
			* the task's name
			* the task's state
			* the associated output file

		:return: list representing the current task
		:rtype: list of str
		''' 
		return [str(self.pid), self.taskName, self.state.value, self.outputFilename]
