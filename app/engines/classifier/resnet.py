# Building ResNet18 from Scratch using PyTorch
# Reference: https://debuggercafe.com/building-resnets-from-scratch-using-pytorch/

import torch.nn as nn
import torch
import argparse

from torch import Tensor
from typing import Type


class BasicBlock(nn.Module):
    """
    Builds the Basic Block of the ResNet model.
    For ResNet18 and ResNet34, these are stackings od 3x3=> 3x 3 convolutional layers
    For ResNet 50 and above, these are stackings of 1x1 => 3x3 => 1x1 (BottleNeck) layers
    """
    def __init__(
            self,
            num_layers: int,
            in_channels: int,
            out_channels: int,
            stride: int = 1,
            expansion: int = 1,
            downsample: nn.Module = None
    ) -> None:
        super(BasicBlock, self).__init__()
        self.num_layers = num_layers

        # Multiplicate factor for the subsequent conv2d layer's output channels.
        # It is 1 for ResNet18 and ResNet34, and 4 for the others.
        self.expansion = expansion
        self.downsample = downsample

        # 1x1 convolution for ResNet50 and above
        if num_layers > 34:
            self.conv0 = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, bias=False)
            self.bn0 = nn.BatchNorm2d(out_channels)
            in_channels = out_channels

        # 3x3 convolution for all
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)

        # 1x1 convolution for ResNet50 and above
        if num_layers > 34:
            self.conv2 = nn.Conv2d(out_channels, out_channels*self.expansion, kernel_size=1, stride=1, bias=False)
            self.bn2 = nn.BatchNorm2d(out_channels * self.expansion)
        else:
            # 3x3 convolution for ResNet18 and Reset 34 and above
            self.conv2 = nn.Conv2d(out_channels, out_channels*self.expansion, kernel_size=3, padding=1, bias=False)
            self.bn2 = nn.BatchNorm2d(out_channels*self.expansion)
    
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x:Tensor) -> Tensor:
        identity = x

        # Through 1x1 convolution if ResNet50 or above.
        if self.num_layers > 34:
            out = self.conv0(x)
            out = self.bn0(out)
            out = self.relu(out)
        
        # Use the above output if ResNet50 and above
        if self.num_layers > 34:
            out = self.conv1(out)
        # Else use the input to the `forward` method
        else:
            out = self.conv1(x)

        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            identity = self.downsample(x)
        
        out += identity
        out = self.relu(out)

        return out

class ResNet(nn.Module):
    def __init__(self, 
                 img_channels: int,
                 num_layers:int,
                 block: Type[BasicBlock],
                 num_classes:int=1000
                 ) -> None:
        super(ResNet, self).__init__()
        if num_layers == 18:
            # The following `layers` list defines the number of `BasicBlock` to use to build the network and how many basic blocks to stack together
            layers = [2, 2, 2, 2]
            self.expansion = 1
        if num_layers == 34:
            layers = [3, 4, 6, 3]
            self.expansion = 1
        if num_layers == 50:
            layers = [3, 4, 6, 3]
            self.expansion = 4
        if num_layers == 101:
            layers = [3, 4, 23, 3]
            self.expansion = 4
        if num_layers == 152:
            layers = [3, 8, 36, 3]
            self.expansion = 4
        
        self.in_channels = 64
        # All ResNets (18 to 152) contain a Conv2d => BN => ReLU for the first three layers. Here, kernel size is 7.
        self.conv1 = nn.Conv2d(in_channels=img_channels, out_channels=self.in_channels, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(self.in_channels)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        self.layer1 = self._make_layer(block, 64, layers[0], num_layers=num_layers)
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2, num_layers=num_layers)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2, num_layers=num_layers)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2, num_layers=num_layers)

        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * self.expansion, num_classes)
    
    def _make_layer(
            self,
            block:Type[BasicBlock],
            out_channels: int,
            blocks: int,
            stride: int = 1,
            num_layers: int = 18
        ) -> nn.Sequential:
        downsample = None
        if stride != 1 or self.in_channels != out_channels * self.expansion:
            """ This should pass from `layer2` to `layer4` or when building ResNets50 and above.
            """
            downsample = nn.Sequential(
                nn.Conv2d(self.in_channels, 
                          out_channels* self.expansion,
                          kernel_size=1,
                          stride=stride,
                          bias=False),
                nn.BatchNorm2d(out_channels * self.expansion),
            )
        layers = []
        layers.append(block(num_layers, self.in_channels, out_channels, stride, self.expansion, downsample))
        self.in_channels = out_channels * self.expansion

        for i in range(1, blocks):
            layers.append(block(
                num_layers,
                self.in_channels,
                out_channels,
                expansion=self.expansion
            ))
        return nn.Sequential(*layers)
    
    def forward(self, x:Tensor) -> Tensor:
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        # The spatial dimension of the final layer's featre map should be (7,7) for all ResNets
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n', '--num-layers', dest='num_layers', default=18,
        type=int,
        help='number of layers to build ResNet with',
        choices=[18, 34, 50, 101, 152]
    )
    args = vars(parser.parse_args())

    tensor = torch.rand([1, 3, 224, 224])
    model = ResNet(img_channels=3, num_layers=args['num_layers'], block=BasicBlock, num_classes=1000)
    print(model)

    # Total parameters and trainable parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"{total_params:,} total parameters")

    total_trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"{total_trainable_params:,} training parameters")

    output = model(tensor)


