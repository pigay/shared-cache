# Introduction

[shared-cache](https://github.com/pigay/shared-cache) helps multiple processes to synchronize in order to share a disk repository on a host. This repository will generally be used to store some readonly data downloaded from another location.

[shared-cache](https://github.com/pigay/shared-cache) is designed to to create the repository, download the specified data in a concurrent-safe manner.

The first process registering for access to the repository will trigger its creation. Other processes can then register for repository use. Each process has to unregister from the repository when it no longer needs access. The last process to unregister will trigger repository deletion.

When defining a repository, [shared-cache](https://github.com/pigay/shared-cache) user will have to specify the download procedure and optionally a repository name. The download procedure is a list of stacked loader modules. Loader modules can point to a procedure for downloading a file from some url. Alternately, thay can handle a kind of transformation (such as checksum, untar, etc.) on files produced from lower loaders in the stack. 

Additionally, [shared-cache](https://github.com/pigay/shared-cache) can look for a directory with enough space to hold a repository (out of a user provided list of directories).

# Using shared-cache

## Installation

Installing [shared-cache](https://github.com/pigay/shared-cache) is only a matter of downloading and extracting a distribution tarball and calling `setup.py` script. For example:

```bash
tar xvf shared-cache-0.1.tar.gz
cd shared-cache-0.1
python setup.py install
```

You can use the `--prefix=<prefix-path>` option to `setup.py` in order to choose where you want to install [shared-cache](https://github.com/pigay/shared-cache). In that case, make sure that `<prefix-path>/bin` is in your `PATH` and `<prefix-path>/lib/pythonx.y/site-packages` is in your `PYTHONPATH` (provided `pythonx.y` correspond to the version of Python you use).

## Use

Using [shared-cache](https://github.com/pigay/shared-cache) usually consists in the following sequence:
1 register
2 use (user application dependent)
3 unregister

Register and unregister steps have to provide the same definition to the repository. This means name of the repository, but also loader stack (unregister command has to figure how to delete files). Considering this, it can be more convenient to store commandline options and loader stack in a shell environment varibale (see examples below).

### Register use on a repository

Registering use on a repository follows this syntax:
```bash
sc --use [option]... [loader]...
```

### Unregister use on a repository

Unregistering is done as in the following:
```bash
sc --unuse [option]... [loader]...
```


### Loader modules

Available modules come in two flavors. Loaders and transformations.

Loaders:
+ `http:<url>` : downloads a file from a HTTP URL
+ `dirac:<lfn>` : downloads a file from DIRAC File Catalog LFN (DIRAC clients have to be installed)

Transformations:
+ `md5:<sum>` : checks lower stacked loader file against provided MD5 hash `<sum>`
+ `tar` : untars lower stacked files

On the command line, loader modules stack from left to right (left loader is lower than right loader). This means that the first module on the command line has to be a loader module (not a transformation).

### Example

The following basic example downloads an archive file from GitHub, checks the result against its expected md5sum and the untar the archive to repository directory. The repository will be created in the first directory on a partition with at least 10GB free (from the default list `/tmp:/var/tmp`), under the path `<base-dir>/test-repo/`.

```bash
url=https://github.com/pigay/vsg/archive/vsg-0.2.0.tar.gz
md5=7b9d54095bd53e27615c96e7b7318af7

repo=test-repo
repo_args="--name=$repo --size=10GB http:$url md5:$md5 tar"

sc --use $repo_args
```

After using this repository, one has to release it to eventually be deleted. We use the same environment variable `$repo_args` in order to be able to correctly clean the repository:

```bash
sc --unuse $repo_args
```

# License

[shared-cache](https://github.com/pigay/shared-cache) comes with its own copy of [flufl.lock](http://launchpad.net/flufl.lock) which is released under the GNU LGPL v2. Refer to [lockfile.py](sharedcache/lockfile.py) for the full license.


For the rest, [shared-cache](https://github.com/pigay/shared-cache) is released under the [WTFPL - Do What the Fuck You Want to Public License](http://www.wtfpl.net/). ![WTPLF](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-2.png)