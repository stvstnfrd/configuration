#!/usr/bin/make -f
all:
	@echo 'make clean'
	@echo 'make vpc'
	@echo 'make jenkins'
	@echo 'make instance'

clean:
	rm -rf ./.cache
	rm -rf ./*.log

vpc:
	ansible-playbook vpc.yaml -vvvv

jenkins:
	ansible-playbook jenkins.yaml

instance:
	ansible-playbook instance.yaml
