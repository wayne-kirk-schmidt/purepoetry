"""
Base dunder method for making purepoetry a package when the time is right.
Enforce no byte code being written
"""
import sys
sys.dont_write_bytecode = True
