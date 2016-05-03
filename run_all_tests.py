import unittest


print "RUNNING ALL TESTS"
print "MAKE SURE TO RESET ENGINE FIRST!"
print "(run -RunPythonScript)"
loader = unittest.TestLoader()
suite = loader.discover(start_dir='.',pattern="test*.py",top_level_dir='.')
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
print "FINISHED RUNNING ALL TESTS"

