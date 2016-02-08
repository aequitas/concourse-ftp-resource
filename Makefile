user=aequitas
name=ftp-resource

# get docker config from running VM instance (OSX)
docker=docker $(shell docker-machine config dev)

.PHONY: test

push: build
	$(docker) push $(user)/$(name)

test build:
	$(docker) build -t $(user)/$(name) .
