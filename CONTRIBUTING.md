# Contributing to the Trakt Watch Provider Plugin

This is the community fork maintained at
[kyle95wm/silo-plugin-watchprovider-trakt](https://github.com/kyle95wm/silo-plugin-watchprovider-trakt).
Report plugin problems and propose behavior changes in this fork's issue tracker.
The original Silo Trakt repository is archived and does not maintain this fork.

## Before you start

Open an issue in this fork before changing authentication, reconciliation,
idempotency, supported state, configuration, or advertised capabilities. Include
reproduction steps and redact secrets and personal watch history. This repository
owns the Trakt adapter; SDK contracts and Silo's host orchestration remain in
their respective upstream projects.

## Development setup

Use the Go version declared in `go.mod`. A local `go.work` may point at a sibling
SDK checkout while developing both repositories, but committed code and CI must
resolve the tagged SDK dependency with `GOWORK=off`. Never commit real
deployment URLs, tokens, captured watch history, or a local filesystem `replace`
directive.

## Validate your change

```sh
GOWORK=off go test ./...
GOWORK=off go vet ./...
GOWORK=off go build ./...
GOWORK=off go run . manifest >/dev/null
gofmt -l .
```

The manifest command must exit successfully. `gofmt -l .` should print nothing;
if it reports unrelated pre-existing drift, none of the Go files touched by your
change may appear in the output. Do not add to the output, and report what
remains. Add focused coverage for authentication, identity mapping, retries,
event idempotency, progress conversion, and upstream error handling when those
behaviors change.

## Open the pull request

Use a Conventional Commit title, explain any sync, privacy, or retry risk, and
paste the actual validation results. For AI-assisted changes, disclose the harness, tools, model identifier when
available, and scope of human review. Never claim checks or live verification
that did not run. Review non-trivial changes adversarially before submitting.
