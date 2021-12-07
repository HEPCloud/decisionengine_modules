# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

from glideinwms.lib import classadSupport


class GlideClientClassad(classadSupport.Classad):

    # Class variable: Counter for classad counter.
    # key = (name)
    classad_counter = {}

    def __init__(self, factory_ref, frontend_ref):
        """
        Class Constructor

        @type factory_ref: string
        @param factory_ref: Name of the resource in the glidefactory classad
        @type frontend_ref: string
        @param type: Name of the resource in the glideclient classad
        """

        classadSupport.Classad.__init__(self, "glideclient", "UPDATE_AD_GENERIC", "INVALIDATE_ADS_GENERIC")

        name = f"{factory_ref}@{frontend_ref}"
        # TODO: Identify version dynamically
        self.adParams["GlideinWMSVersion"] = "Decision Engine - v0.01"
        self.adParams["FactoryName"] = f"{factory_ref}"
        self.adParams["ClientName"] = f"{frontend_ref}"
        self.adParams["Name"] = name
        self.adParams["GLIDEIN_In_Downtime"] = "False"

        # First classad number starts with 0
        GlideClientClassad.classad_counter[name] = GlideClientClassad.classad_counter.get(name, -1) + 1
        self.adParams["UpdateSequenceNumber"] = GlideClientClassad.classad_counter[name]


class GlideClientGlobalClassad(classadSupport.Classad):
    # Class variable: Counter for classad counter.
    # key = (name)
    classad_counter = {}

    def __init__(self, factory_ref, frontend_ref):
        """
        Class Constructor

        @type factory_ref: string
        @param factory_ref: Name of the resource in the glidefactory classad
        @type frontend_ref: string
        @param type: Name of the resource in the glideclient classad
        """

        classadSupport.Classad.__init__(self, "glideclientglobal", "UPDATE_AD_GENERIC", "INVALIDATE_ADS_GENERIC")

        name = f"{factory_ref}@{frontend_ref}"
        self.adParams["GlideinWMSVersion"] = "Decision Engine - v0.01"
        self.adParams["ClientName"] = f"{frontend_ref}"
        self.adParams["Name"] = name

        # First classad number starts with 0
        GlideClientGlobalClassad.classad_counter[name] = GlideClientGlobalClassad.classad_counter.get(name, -1) + 1
        self.adParams["UpdateSequenceNumber"] = GlideClientGlobalClassad.classad_counter[name]


class GlideClientClassadAdvertiser(classadSupport.ClassadAdvertiser):
    def __init__(self, pool=None, multi_support=False):
        """
        Constructor

        @type pool: string
        @param pool: Collector address
        @type multi_support: bool
        @param multi_support: True if the installation support advertising multiple classads with one condor_advertise command. Defaults to False.
        """

        classadSupport.ClassadAdvertiser.__init__(self, pool=pool, multi_support=multi_support, tcp_support=True)

        self.adType = "glideclient"
        self.adAdvertiseCmd = "UPDATE_AD_GENERIC"
        self.adInvalidateCmd = "INVALIDATE_ADS_GENERIC"
        self.advertiseFilePrefix = "glideclient_ads"

    def set_glidein_config_limits(self, limits_data):
        self.glidein_config_limits = limits_data


class GlideClientGlobalClassadAdvertiser(classadSupport.ClassadAdvertiser):
    def __init__(self, pool=None, multi_support=True):
        """
        Constructor

        @type pool: string
        @param pool: Collector address
        @type multi_support: bool
        @param multi_support: True if the installation support advertising multiple classads with one condor_advertise command. Defaults to False.
        """

        classadSupport.ClassadAdvertiser.__init__(self, pool=pool, multi_support=multi_support, tcp_support=True)

        self.adType = "glideclientglobal"
        self.adAdvertiseCmd = "UPDATE_AD_GENERIC"
        self.adInvalidateCmd = "INVALIDATE_ADS_GENERIC"
        self.advertiseFilePrefix = "glideclientglobal_ads"
