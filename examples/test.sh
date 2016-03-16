#! /bin/bash

url=https://github.com/pigay/vsg/archive/vsg-0.2.0.tar.gz
md5=7b9d54095bd53e27615c96e7b7318af7

repo=test-repo
repo_args="--name=$repo --size=10GB http:$url md5:$md5 tar dummy"

sc --use $repo_args

# do something here with the repo
sleep 10

sc --unuse $repo_args
