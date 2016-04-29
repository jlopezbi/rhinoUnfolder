import unittest

#NOTE: does not reload modules

names = ["test_mesh",
         "test_net",
         "test_islandMaker",
         "test_transformations",
         "test_visualization",
         "test_unfold"]
loader = unittest.TestLoader()

all_suites = []
for name in names:
    all_suites.append(loader.loadTestsFromName(name))

big_suite = unittest.TestSuite(all_suites)
runner = unittest.TextTestRunner(verbosity=2)
runner.run(big_suite)


