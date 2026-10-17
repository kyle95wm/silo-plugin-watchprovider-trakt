#!/usr/bin/env python3
"""Package already-built binaries for Silo's local plugin installer."""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def write_zip(path, entries):
    # Stable timestamps and Unix modes make archives reproducible.
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data, mode in entries:
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100000 | mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "manifest.json").read_text())
    if args.version != manifest["version"]:
        parser.error("version must match manifest.json; update it before building")

    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    assets = []
    shared = [(name, (ROOT / name).read_bytes(), 0o644)
              for name in ("LICENSE", "NOTICE", "README.md")]
    for platform in manifest["supported_platforms"]:
        suffix = f'{platform["os"]}-{platform["arch"]}'
        binary = dist / f"plugin-{suffix}"
        data = binary.read_bytes()
        checksum = hashlib.sha256(data).hexdigest()
        platform_manifest = {**manifest, "checksum": checksum}
        manifest_data = (json.dumps(platform_manifest, indent=2) + "\n").encode()
        manifest_path = dist / f"manifest-{suffix}.json"
        manifest_path.write_bytes(manifest_data)
        archive_path = dist / f"trakt-community-{args.version}-{suffix}.zip"
        write_zip(archive_path, [("plugin", data, 0o755),
                                 ("manifest.json", manifest_data, 0o644), *shared])
        assets.extend((binary, manifest_path, archive_path))

    # Ship the corresponding source alongside local binaries as well as on GitHub.
    source_paths = [ROOT / name for name in (
        "AGENTS.md", "CONTRIBUTING.md", "LICENSE", "NOTICE", "README.md",
        "Makefile", ".gitignore", "go.mod", "go.sum", "manifest.json",
        "main.go", "main_test.go")]
    for directory in ("provider", "scripts", ".github/workflows"):
        source_paths.extend(path for path in (ROOT / directory).rglob("*")
                            if path.is_file() and "__pycache__" not in path.parts)
    source_archive = dist / f"trakt-community-{args.version}-source.zip"
    write_zip(source_archive, [(str(path.relative_to(ROOT)), path.read_bytes(), 0o644)
                               for path in sorted(source_paths)])
    assets.append(source_archive)
    checksums = "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
                        for path in sorted(assets))
    (dist / "checksums.txt").write_text(checksums)
    print(f"Packaged {manifest['plugin_id']} {args.version} for "
          f"{len(manifest['supported_platforms'])} platforms in {dist}")


if __name__ == "__main__":
    main()
