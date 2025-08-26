help:
	@echo "———————————————————————————————"
	@echo " Usage: make [options]"
	@echo " Options:"
	@echo "  help:  show this help message"
	@echo "  graph: generate graph"
	@echo "  clean: clean up the project"
	@echo "———————————————————————————————"

graph:
	.venv/bin/python csv2pronto -s ./input/input.csv -d ./out.ttl -f ttl -o ./ontology/pronto.owl

clean:
	find . -name "__pycache__" -exec rm -fr {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	rm -f ./out.ttl
