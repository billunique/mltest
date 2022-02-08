# coding: utf-8
#

from inspect import stack
import sys


def print_whereami_head(inst):
	# print("\n-*-*-*-*-*-*",__file__, inst.__class__.__name__, stack()[0][3], "-*-*-*-*-*-*-\n")
	# print("\n-*-*-*-*-*-*",__file__, inst.__class__.__name__, sys._getframe().f_code.co_name, "-*-*-*-*-*-*-\n")
	# print("\n-*-*-*-*-*-*",__file__, inst.__class__.__name__, getframeinfo(currentframe())[2], "-*-*-*-*-*-*-\n")
	# print("\n-*-*-*-*-*-*",__file__, inst.__class__.__name__, inspect.getmembers(method_), "-*-*-*-*-*-*-\n")
	print("\nhead =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*  ", end="") 
	print(sys.argv[0], inst.__class__.__name__, stack()[1][3], end="")
	print("  =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*\n")


def print_whereami_tail(inst):
	print("\ntail =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#  ", end="") 
	print(sys.argv[0], inst.__class__.__name__, stack()[1][3], end="")
	print("  =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#\n")



def print_whereami(inst):
	print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
	print(sys.argv[0], inst.__class__.__name__, stack()[1][3])
	print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")



def whereami_logger(inst):
	def decorator(func):
		def wrapper():
			print_whereami_head(inst)
			func()
			print_whereami_tail(inst)
		return wrapper
	return decorator

