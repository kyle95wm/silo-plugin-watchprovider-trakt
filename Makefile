.PHONY: build build-all package clean lint test

BINARY=plugin
PLATFORMS=linux/amd64 linux/arm64 darwin/arm64
VERSION ?= $(shell python3 -c 'import json; print(json.load(open("manifest.json"))["version"])')
LDFLAGS=-s -w -X main.version=$(VERSION)

build:
	go build -trimpath -ldflags="$(LDFLAGS)" -o $(BINARY) .

build-all:
	@mkdir -p dist
	@set -e; for platform in $(PLATFORMS); do \
		GOOS=$${platform%%/*} GOARCH=$${platform##*/} CGO_ENABLED=0 \
		go build -trimpath -ldflags="$(LDFLAGS)" -o dist/$(BINARY)-$${platform%%/*}-$${platform##*/} .; \
	done

package: build-all
	python3 scripts/package_release.py --version "$(VERSION)"

test:
	go test ./...

lint:
	golangci-lint run ./...

clean:
	rm -f $(BINARY)
	rm -rf dist
