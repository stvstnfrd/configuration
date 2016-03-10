#!/usr/bin/make -F
# --parameters ParameterKey=string,ParameterValue=string
# --tags Key=string,Value=string

NAME_FLAG=--stack-name sandbox
TEMPLATE_FLAG=--template-body file:///$(PWD)/vpc.json
CF=aws cloudformation
TAGS_FLAG="--tags Key=environment,Value=sandbox"
PARAMETERS=--parameters 'ParameterKey=KeyName,ParameterValue=deployment'
FAIL_FLAG=--on-failure DO_NOTHING

all:
	$(CF) describe-stacks $(NAME_FLAG)
	$(CF) validate-template $(TEMPLATE_FLAG)

clean:
	$(CF) delete-stack $(NAME_FLAG)

create:
	$(CF) create-stack $(NAME_FLAG) $(TEMPLATE_FLAG) $(FAIL_FLAG)--tags 'Key=environment,Value=sandbox' $(PARAMETERS)

	       

update:
	# $(CF) update-stack $(NAME_FLAG) $(TEMPLATE_FLAG) $(PARAMETERS)
	$(CF) update-stack $(NAME_FLAG) $(TEMPLATE_FLAG) --parameters 'ParameterKey=KeyName,ParameterValue=deployment'

list:
	$(CF) list-stack-resources $(NAME_FLAG)
