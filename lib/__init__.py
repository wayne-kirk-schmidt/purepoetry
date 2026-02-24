"""
Base dunder method for making purepoetry a package when the time is right.
This is for the ./lib directory, and will be for the subfolders as well

Enforce no byte code being written
"""
import sys
sys.dont_write_bytecode = True
