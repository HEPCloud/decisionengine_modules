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
    VENV=$WORKSPACE/venv

    # Following is useful for running the script outside jenkins
    #if [ ! -d "$WORKSPACE" ]; then
    #    mkdir $WORKSPACE
    #fi

    VIRTUALENV_EXE=virtualenv-3.6
    PIP_EXE=pip

    if [ ! -d $VENV ] ; then
      $VIRTUALENV_EXE $VENV
    fi

    source $VENV/bin/activate

    pip_packages="pylint pycodestyle pytest mock tabulate pandas google-api-python-client boto boto3 gcs_oauth2_boto_plugin urllib3 jsonnet"
    echo "Installing $pip_packages ..."
    pip install --quiet $pip_packages
    if [ $? -ne 0 ]; then
        echo "Installing $pip_packages ... FAILED"
    fi
    pip install classad htcondor

    # Need this because some strange control sequences when using default TERM=xterm
    export TERM="linux"

}


setup_git_product() {
    product_git_repo=$1
    wspace=${2:-`pwd`}
    cd $wspace
    git clone --single-branch --branch 1.3  $product_git_repo
}


setup_glideinwms() {
    dir=$1
    glideinwms_git_repo="https://github.com/glideinWMS/glideinwms.git"
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
    rm -rf $DEPS_DIR
    mkdir $DEPS_DIR
    touch $DEPS_DIR/__init__.py

    # setup decisionengine framework
    setup_de_framework $DEPS_DIR

    # Setup glideinwms
    setup_glideinwms $DEPS_DIR

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
