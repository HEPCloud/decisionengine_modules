#!/bin/sh

log_nonzero_rc() {
    echo "`date` ERROR: $1 failed with non zero exit code ($2)" 1>&2
}


setup_python_venv() {
    if [ $# -gt 1 ]; then
        echo "Invalid number of arguments to setup_python_venv. Will accept the location to install venv or use PWD as default"
        exit 1
    fi
    WORKSPACE=${1:-`pwd`}
    VIRTUALENV_VER=15.2.0
    VIRTUALENV_TARBALL=virtualenv-${VIRTUALENV_VER}.tar.gz
    #VIRTUALENV_URL="https://pypi.python.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/$VIRTUALENV_TARBALL"
    VIRTUALENV_URL="https://glideinwms.fnal.gov/downloads/$VIRTUALENV_TARBALL"
    VIRTUALENV_EXE=$WORKSPACE/virtualenv-${VIRTUALENV_VER}/virtualenv.py
    VENV=$WORKSPACE/venv

    # Following is useful for running the script outside jenkins
    if [ ! -d "$WORKSPACE" ]; then
        mkdir $WORKSPACE
    fi

    echo "SETTING UP VIRTUAL ENVIRONMENT ..."
    if [ -f $WORKSPACE/$VIRTUALENV_TARBALL ]; then
        #rm $WORKSPACE/$VIRTUALENV_TARBALL
        echo "Using existing $WORKSPACE/$VIRTUALENV_TARBALL"
    else
    # Get latest virtualenv package that works with python 2.6
    curl -o $WORKSPACE/$VIRTUALENV_TARBALL $VIRTUALENV_URL 
    tar xzf $WORKSPACE/$VIRTUALENV_TARBALL
    fi 
    if [ ! -d $VENV ] ; then
       $VIRTUALENV_EXE --system-site-packages $VENV
    fi

    source $VENV/bin/activate

    # Install dependancies first so we don't get uncompatible ones
    # Following RPMs need to be installed on the machine:
    #pip_packages="astroid pylint pep8 unittest2 coverage sphinx DBUtils pytest"
    pip_packages="argparse WebOb astroid pylint pycodestyle unittest2 coverage sphinx DBUtils pytest mock"
    for package in $pip_packages; do
        echo "Installing $package ..."
        status="DONE"
        pip install --quiet $package
        if [ $? -ne 0 ]; then
            status="FAILED"
        fi
        echo "Installing $package ... $status"
    done

    # Need this because some strange control sequences when using default TERM=xterm
    export TERM="linux"

}


setup_git_product() {
    product_git_repo=$1
    wspace=${2:-`pwd`}
    cd $wspace
    git clone $product_git_repo
}


setup_glideinwms() {
    dir=$1
    glideinwms_git_repo="http://cdcvs.fnal.gov/projects/glideinwms"
    setup_git_product "$glideinwms_git_repo" $dir
}


setup_de_framework() {
    dir=$1
    de_framework_git_repo="https://github.com/HEPCloud/decisionengine.git"
    setup_git_product "$de_framework_git_repo" $dir
}


setup_dependencies() {
    WORKSPACE=${1:-`pwd`}
    DEPS_DIR=$WORKSPACE/dependencies
    #rm -rf $DEPS_DIR
    if [ -e $DEPS_DIR ];then
     echo "Using existing $DEPS_DIR"
    else
    mkdir $DEPS_DIR
    touch $DEPS_DIR/__init__.py

    # setup decisionengine framework
    setup_de_framework $DEPS_DIR

    # Setup glideinwms
    setup_glideinwms $DEPS_DIR
    fi 

    export PYTHONPATH=$DEPS_DIR
    cd $WORKSPACE
}


print_python_info() {
    if [ $# -ne 0 ]; then
        br="<br/>"
        bo="<b>"
        bc="</b>"
    fi
    echo "${bo}HOSTNAME:${bc} `hostname -f`$br"
    echo "${bo}LINUX DISTRO:${bc} `lsb_release -d`$br"
    echo "${bo}PYTHON:${bc} `which python`$br"
    echo "${bo}PYLINT:${bc} `pylint --version`$br"
    echo "${bo}PEP8:${bc} `pycodestyle --version`$br"
}


mail_results() {
    local contents=$1
    local subject=$2
    local to=$3
    local attachments=$4
    local from="parag@fnal.gov"
#    echo "From: parag@fnal.gov;
#To: parag@fnal.gov;
#Subject: $subject;
#Content-Type: text/html;
#MIME-VERSION: 1.0;
#;
#`cat $contents`
#" | sendmail -t
    local attach=""
    [ -n "$attachments" ] && attach=" -a `echo $attachments | sed -e 's|,| -a |g'`"
    mutt -e "set content_type=text/html"  -s "$subject" $to $attach < $contents
}
