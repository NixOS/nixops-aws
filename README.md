# NixOps AWS Plugin

NixOps (formerly known as Charon) is a tool for deploying NixOS
machines in a network or cloud.

This repo contains the NixOps AWS Plugin.

* [Manual](https://nixos.org/nixops/manual/)
* [Installation](https://nixos.org/nixops/manual/#chap-installation) / [Hacking](https://nixos.org/nixops/manual/#chap-hacking)
* [Continuous build](http://hydra.nixos.org/jobset/nixops/master#tabs-jobs)
* [Source code](https://github.com/NixOS/nixops)
* [Issue Tracker](https://github.com/NixOS/nixops/issues)
* [Mailing list / Google group](https://groups.google.com/forum/#!forum/nixops-users)
* [IRC - #nixos on freenode.net](irc://irc.freenode.net/#nixos)

## Developing

To start developing on the NixOps AWS plugin, you can run:

```bash
  $ ./dev-shell
```

Documentation for the `nixops-aws` plugin is in the [nixops repo](https://github.com/NixOS/nixops)

The python code is formatted with the latest release of [black](https://black.readthedocs.io/en/stable)
and is checked in PR validation. See the `black` target in [ci.yaml](./github/workflows/ci.yaml) for the cmd to run.

## Building from source

The command to build NixOps depends on your platform.

See the main NixOps repo instructions for how to built NixOps
with this AWS plugin.

This document is a work in progress.
