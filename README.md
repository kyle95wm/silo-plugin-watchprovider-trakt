# Trakt Community Watch Provider for Silo

A replacement for Silo's archived Trakt plugin, based on upstream version 0.2.0 and [PR #3](https://github.com/Silo-Server/silo-plugin-watchprovider-trakt/pull/3). It uses Silo's existing `watch_sync_provider.v1` interface and retains the original watch-sync capabilities.

- Plugin ID: `community.watchprovider.trakt`
- Provider shown in Silo: **Trakt (Community)**
- Version: **0.3.0**
- SDK: `silo-plugin-sdk` **v0.21.0**, API **v1**

This is an independent fork. Silo's retired ID, `silo.watchprovider.trakt`, is blocked by the host; this fork has its own ID. Silo assigns community connections a provider key of `plugin:<installation-id>:trakt`. Keep the plugin ID stable when publishing updates.

## Install

Download a platform package from [GitHub Releases](https://github.com/kyle95wm/silo-plugin-watchprovider-trakt/releases/latest). Choose the package for the **Silo server**, which may differ from your desktop:

| Server | Package in `dist/` |
| --- | --- |
| Linux x86-64, including typical Unraid/Docker servers | `trakt-community-0.3.0-linux-amd64.zip` |
| Linux ARM64 | `trakt-community-0.3.0-linux-arm64.zip` |
| macOS Apple Silicon | `trakt-community-0.3.0-darwin-arm64.zip` |

1. In Silo's admin plugin page, upload the matching ZIP using the local plugin installation control. The ZIP contains `manifest.json` and an executable named `plugin`. If your Silo version offers a binary upload instead, upload the matching `plugin-<os>-<arch>` file.
2. Enable **Trakt Community Watch Provider** and open its settings.
3. Configure your Trakt application using the steps below, then connect each profile.

`dist/checksums.txt` contains SHA-256 checksums. From `dist/`, verify with `shasum -a 256 -c checksums.txt` (macOS) or `sha256sum -c checksums.txt` (Linux). The matching `trakt-community-0.3.0-source.zip` contains the modified source.

The host needs plugin watch-sync and device-code support; SDK v0.21 support enables dropped-show sync. Older hosts may ignore dropped shows. No Silo server patch is required for the current community-plugin registration path. Upload controls may differ between Silo versions; catalog-only hosted environments need their operator to permit local plugins.

## Capabilities

- Signs each profile in with Trakt's device code: Silo shows a code, and the profile owner enters it at trakt.tv/activate.
- Imports watched movies and episodes with their play counts and last watch times.
- Imports resume progress for movies and episodes.
- Imports favorites, the watchlist, and movie and show ratings as complete lists, so a title removed on Trakt is removed in Silo.
- Exports completed plays. Trakt stores every play it receives, repeats included, so before writing a batch the plugin reads the Trakt history around those plays and skips any play Trakt already has in the same minute.
- Exports unwatched titles. Trakt removes history by title, so this clears every play of the title.
- Adds and removes favorites and watchlist entries, and sets and clears movie and show ratings. Trakt uses the same 1–10 rating scale as the plugin contract.
- Syncs dropped shows both ways. Dropping a show on Trakt hides it from Up Next, progress, and the calendar without touching its history, and Trakt undrops a show on its own when it is watched again. The plugin imports Trakt's dropped shows as a complete list, and drops and undrops shows on Trakt in batches. Dropping a show that is already dropped, or undropping one that is not, succeeds without a change. Trakt's dropped list leaves out drops that apps make, Silo's included, so Silo keeps a drop it sent rather than reading the omission as an undrop.
- Sends live playback start, pause, and stop events. Trakt records a play when a stop arrives at 80% progress or later.

### How the plugin reads Trakt

Every sync reads the full Trakt lists; Trakt has no change feed the plugin could resume from. Trakt pages its lists, and a list that changes while it is read can shift a row between pages. A list longer than one page is therefore read twice, and the read only counts when both passes match. A list that changes during a sync is read again up to three times; if it keeps changing, or it changes after the plugin has already returned part of it to Silo, that sync stops and the next one starts over.

The plugin keeps to Trakt's rate limits for each connection: one write per second, and paged reads paced to stay under 500 per five minutes. When Trakt asks it to wait ten seconds or less, the plugin waits and retries; a longer wait, or no stated wait (five minutes), pauses that profile's sync until then.

## Configure Trakt

1. Create your own API application on the [Trakt developer portal](https://developer.trakt.tv/apps). Follow the portal's account-verification requirements.
2. If the form requires a redirect URI, enter an HTTPS address you control. This plugin uses device-code sign-in and never sends a redirect URI.
3. In the plugin settings, enter the **Client ID**. The **Client secret** is optional; leave it blank if Trakt did not issue one. If you change to an app without a secret, clear any previously saved secret.
4. For each Silo profile, open watch-provider settings, choose **Trakt (Community)**, and connect. Enter the displayed code at the verification URL, normally [trakt.tv/activate](https://trakt.tv/activate).
5. Let the first sync finish, then confirm that watched titles and resume progress appear as expected. Enable the export options you want in the connection settings.

All profiles use the configured application, while each profile authorizes its own Trakt account. Client-secret-free device polling and refresh are the changes from PR #3. Browser authorization-code sign-in with PKCE is a separate flow and is not implemented in this release. See [Trakt's PKCE guidance](https://developer.trakt.tv/docs/pkce).

The plugin receives configuration and credentials from Silo for each RPC. It does not store or log tokens; Silo owns encrypted credential storage. Every request requires the Client ID, and an optional saved Client secret is sent only to the token endpoints.

## Reconnect after the official plugin is removed

Silo's retirement migration deletes the original Trakt connections and their tokens, disables the official plugin, and preserves already imported watch history. This fork cannot recover deleted credentials. Re-enter the app settings and connect each profile again.

This creates a new connection with fresh sync bookkeeping and a full initial import. The original history-write de-duplication is retained, but an upgraded server with existing history still needs a live smoke test before you rely on exports. Avoid running the old official connection and this replacement together on a pre-retirement server.

Legacy Trakt collections and home rows are host features and are not restored by this watch-sync plugin. Favorites and watchlist sync remain part of the plugin.

## Build and validate

Use Go 1.26.4 or a newer Go 1.26 patch release, Python 3, and Make. Dependencies resolve from the pinned public SDK tag; no local SDK checkout is required.

```sh
GOWORK=off go test -race ./...
GOWORK=off go vet ./...
GOWORK=off go build ./...
GOWORK=off go run . manifest
gofmt -l .
make build
make package
```

`make package` builds static binaries for every declared platform, creates installation ZIPs with executable permissions, writes manifests with actual binary checksums, and includes the corresponding source archive. The default build version comes from `manifest.json`. Update that version before releasing; tag it as `v<version>` to run the release workflow in your own repository.

The workflows publish releases in [kyle95wm/silo-plugin-watchprovider-trakt](https://github.com/kyle95wm/silo-plugin-watchprovider-trakt). They do not notify Silo's official catalog. To publish a new version, update `manifest.json`, push the change, wait for CI, then push a matching `v<version>` tag. Binary downloads belong in GitHub Releases; `dist/` stays out of Git.

## Validation limits

Automated tests use a local Trakt HTTP stub. They cover authentication with and without a Client secret, refresh-token rotation, state imports, event exports, rate limits, and upstream error handling. They do not demonstrate successful live authorization or installation on your Silo server.

After installation, connect a test profile, verify an import, mark one test title watched, and confirm one entry arrives on Trakt. Repeat the sync and check that no extra play appears. Test resume/scrobble events and a reconnect before enabling additional profiles.

## Source and license

Derived from [Silo's original Trakt plugin](https://github.com/Silo-Server/silo-plugin-watchprovider-trakt), with the optional-secret patch proposed by Quick104 in PR #3. See [NOTICE](NOTICE) for provenance and changes. The original AGPL-3.0-only [LICENSE](LICENSE) is retained. Distribute the corresponding modified source with binaries and comply with the license's source-offer requirements for network use.
