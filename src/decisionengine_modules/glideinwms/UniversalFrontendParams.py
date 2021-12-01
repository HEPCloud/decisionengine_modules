import copy

from glideinwms.creation.lib.cvWParams import VOFrontendParams


class UniversalFrontendParams(VOFrontendParams):
    """
    Implements VOFrontendParams with a universal config parser.

    This class overrides the constructor of the Params class to support different configuration formats.
    TODO: This class should be removed when these changes are implemented in the Params class itself.
    """

    def __init__(self, src_dir, config_source):
        """Constructor. Load the default values and override with the configuration content.

        Args:
            src_dir (str): frontend source directory
            config_parser (ConfigSource): configuration source
        """

        self.src_dir = src_dir

        # initialize the defaults
        self.defaults = {}
        self.init_defaults()

        try:
            self.data = config_source
            self.subparams = self.get_subparams_class()(self.data)
            self.subparams.validate(self.defaults, self.get_top_element())

            # make a copy of the loaded data, so that I can always tell what was derived and what was not
            self.org_data = copy.deepcopy(self.data)

            self.subparams.use_defaults(self.defaults)

            # create derived values
            self.derive()
        except RuntimeError as e:
            raise RuntimeError("Unexpected error while loading the config file: %s" % e)
