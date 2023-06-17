tests:
	python3 -m unittest -v can_share_test
benchmark:
	python3 can_share_benchmark.py
coverage:
	coverage run -m unittest can_share_test
	coverage html
	xdg-open ./htmlcov/index.html