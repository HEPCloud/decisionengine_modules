FROM hepcloud/decision-engine-ci
# Adding dependencies for GlideinWMS
RUN yum install -y python36-m2crypto python-rrdtool osg-wn-client vo-client voms-clients-cpp \
  python36-ldap3 python36-jwt PyYAML && yum clean all
# User and test setup
COPY entrypoint.sh /entrypoint.sh
RUN groupadd -g 115 decision-engine-ci
RUN useradd -u 1001 -g 115 decision-engine-ci
USER decision-engine-ci
ENTRYPOINT ["/entrypoint.sh"]
