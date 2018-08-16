# ahenk

**Lider Ahenk** is an open source project which provides solutions to manage, monitor and audit unlimited number of different systems and users on a network.

Ahenk is a Linux agent written in Python which enables Lider to manage & monitor clients remotely.

>Add new repo with [this](https://github.com/Pardus-LiderAhenk/lider-ahenk-installer/blob/master/ahenk-installer/conf/liderahenk.list) file

## Documentation

* See [Ahenk wiki](https://github.com/Pardus-LiderAhenk/ahenk/wiki) to get started!
* See how to [setup development environment](https://github.com/Pardus-LiderAhenk/ahenk/wiki/01.-Setup-Development-Environment)
* Learn how to [run](https://github.com/Pardus-LiderAhenk/ahenk/wiki/02.-Running) ahenk.
* Create [Ahenk distribution](https://github.com/Pardus-LiderAhenk/ahenk/wiki/03.-Ahenk-Distribution) as .deb package

## Packaging
Install necessary packages
```bash
sudo apt install build-essential git-buildpackage debhelper debmake
```

Clone the project and switch to branch 'debian'
```bash
git clone https://github.com/Pardus-LiderAhenk/ahenk.git
cd ahenk/
git checkout debian
```

Install build dependencies via git-buildpackage
```bash
sudo mk-build-deps -ir
```

Build binary package
```bash
gbp buildpackage --git-export-dir=/tmp/build-area -b -us -uc
#check the output directory
ls -1 /tmp/build-area
#output should be like this
ahenk_1.0.0-2_all.deb
ahenk_1.0.0-2_amd64.build
ahenk_1.0.0-2_amd64.buildinfo
ahenk_1.0.0-2_amd64.changes
ahenk_1.0.0.orig.tar.gz
```
Build source package
```bash
gbp buildpackage --git-export-dir=/tmp/build-area -S -us -uc
#check the output directory
ls -1 /tmp/build-area
#output should be like this
ahenk_1.0.0-2.debian.tar.xz
ahenk_1.0.0-2.dsc
ahenk_1.0.0-2_source.build
ahenk_1.0.0-2_source.buildinfo
ahenk_1.0.0-2_source.changes
ahenk_1.0.0.orig.tar.gz
```

If the master has new version tagged (eg: 1.0.2), debian branch should rebased
```bash
git rebase 1.0.2
```
Changelog should be updated after rebase and new debian tag should be created
```bash
gbp dch -Rc
gbp buildpackage --git-tag-only
```

## Contribution

We encourage contributions to the project. To contribute:

* Fork the project and create a new bug or feature branch.
* Make your commits with clean, understandable comments
* Perform a pull request

## Other Lider Ahenk Projects

* [Lider](https://github.com/Pardus-LiderAhenk/lider): Business layer running on Karaf container.
* [Lider Console](https://github.com/Pardus-LiderAhenk/lider-console): Administration console built as Eclipse RCP project.
* [Lider Ahenk Installer](https://github.com/Pardus-LiderAhenk/lider-ahenk-installer): Installation wizard for Ahenk and Lider (and also its LDAP, database, XMPP servers).
* [Lider Ahenk Archetype](https://github.com/Pardus-LiderAhenk/lider-ahenk-archetype): Maven archetype for easy plugin development.

## Changelog

See [changelog](https://github.com/Pardus-LiderAhenk/ahenk/wiki/Changelog) to learn what we have been up to.

## Roadmap

#### Today

* 30+ plugins
* Linux agent service written in Python
* Administration console built as Eclipse RCP
* Open sourced, easy to access and setup, stable Lider Ahenk v1.0.0

#### 2017

* Agents for Windows and mobile platforms
* Platform-independent administration console
* Inventory scan & management
* Printer management

#### 2016

* Scalable infrastructure suitable for million+ users & systems
* 10+ new plugins (such as file distribution via torrent, remote installation)
* New reporting module & dashboard

## License

Lider Ahenk and its sub projects are licensed under the [LGPL v3](https://github.com/Pardus-LiderAhenk/ahenk/blob/master/LICENSE).
