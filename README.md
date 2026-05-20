moonforge-cli
=============

A small CLI utility that manages Moonforge-based projects.

## Installation

You can run moonforge-cli uninstalled from the cloned repository, using the
`moonforge.py` wrapper, e.g.

```sh
$ Project/moonforge-cli/moonforge.py init --name=derivative ~/Projects/meta-derivative
```

You can also use `pip` to install from the cloned repository:

```sh
$ cd moonforge-cli
$ pip3 install --user -e .
```

## Using moonforge-cli

#### Initialization

Use `moonforge init` to initialize a new Moonforge project. The command
below will initialize a "derivative" project under the `meta-derivative`
directory, using the default machine:

```sh
$ moonforge init --name=derivative ~/Projects/meta-derivative
```

You can specify various features at initialization time:

```sh
$ moonforge init \
> --name=derivative \
> --feature=rauc-simple \
> --feature=podman \
> Projects/meta-derivative
```

You can also set layer-specific variables at initalization time:

```sh
$ moonforge init \
> --name=webapp \
> --feature=graphics-wpe \
> --variable WAYLAND_COG_LAUNCH_URL=https://moonforgelinux.org \
> Projects/webapp
```

#### Building

Once a Moonforge has been initialized, you can build it using the `build`
command:

```sh
$ mkdir workspace
$ cd workspace
$ mkdir cache
$ moonforge init --name=test meta-test
$ cd meta-test
$ moonforge config set container.engine podman
$ moonforge config set build.download_dir $PWD/../cache/downloads
$ moonforge config set build.sstate_dir $PWD/../cache/sstate-cache
$ moonforge build .
```

You can use the `shell` command to enter an interactive shell in the build
environment:

```sh
$ moonforge shell .
```

Copyright and licensing terms
-----------------------------

Copyright 2026 Igalia S.L.

This project is released under the terms of the MIT license. See the
[license file](./LICENSES/MIT.txt) for more details.
