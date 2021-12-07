# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

FROM hepcloud/decision-engine-ci
COPY entrypoint.sh /entrypoint.sh
RUN groupadd -g 115 decision-engine-ci
RUN useradd -u 1001 -g 115 decision-engine-ci
USER decision-engine-ci
ENTRYPOINT ["/entrypoint.sh"]
