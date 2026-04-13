coverage:
	coverage run -m unittest pyrte/tests/*_tests.py
	coverage report
	coverage html
