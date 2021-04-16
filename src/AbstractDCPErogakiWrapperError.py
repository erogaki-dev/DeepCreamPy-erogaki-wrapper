from erogaki_wrapper_shared_python.AbstractErogakiWrapperError import AbstractErogakiWrapperError

class AbstractDCPErogakiWrapperError(AbstractErogakiWrapperError):
    def __init__(self, description):
        self.component = "DeepCreamPy-erogaki-wrapper"
        super().__init__(description)
