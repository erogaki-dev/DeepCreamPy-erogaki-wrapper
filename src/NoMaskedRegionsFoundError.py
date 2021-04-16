from AbstractDCPErogakiWrapperError import AbstractDCPErogakiWrapperError

class NoMaskedRegionsFoundError(AbstractDCPErogakiWrapperError):
    def __init__(self, description):
        super().__init__(description)
