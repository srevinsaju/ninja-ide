help:
	@echo "help -- print this help"
	@echo "test -- run tests""

run:
	$(PYTHON) $(NINJA_PATH)
test:
	pytest -v
