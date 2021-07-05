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
* [IRC - #nixos on libera.chat](irc://irc.libera.chat/#nixos)

## Developing

To start developing on the NixOps AWS plugin, you can run:

```bash
  $ nix-shell
  $ poetry install
  $ poetry shell
```
To view active plugins:

```bash
nixops list-plugins
```

Documentation for the `nixops-aws` plugin is in the [nixops repo](https://github.com/NixOS/nixops)

The python code is formatted with the latest release of [black](https://black.readthedocs.io/en/stable)
and is checked in PR validation. See the `black` target in [ci.yaml](./github/workflows/ci.yaml) for the cmd to run.

## Building from source

You can build the Nix package by simply invoking nix-build on the project root:

```bash
$ nix-build
```
See the main NixOps repo for more up-to-date instructions for how to built NixOps
with this AWS plugin.

