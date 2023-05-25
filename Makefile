tests:
	python3 -m unittest can_share_test
coverage:
	coverage run -m unittest can_share_test