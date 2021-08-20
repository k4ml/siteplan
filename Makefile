

test_build:
	poetry build
	cd dist && python -mvenv venv && venv/bin/pip install *.whl
	cd dist && venv/bin/siteplan run -b 127.0.0.1:5000

clean_build:
	rm -rf dist
