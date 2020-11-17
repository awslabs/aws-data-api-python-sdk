#!/bin/bash
#set -x

sourcedir=~/Github/awslabs/aws-data-api/chalicelib
thisdir=`dirname "$0"`

cp $sourcedir/parameters.py $sourcedir/exceptions.py $thisdir/..
