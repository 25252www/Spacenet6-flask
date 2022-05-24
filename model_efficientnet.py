import segmentation_models_pytorch as smp
from segmentation_models_pytorch.unet import model


class unet_efficientnet_b5(smp.Unet):
    def __init__(self, pretrained=False):
        super().__init__(encoder_name="efficientnet-b5", in_channels=4)
