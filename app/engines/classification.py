import os, sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import torch
from torchvision import transforms
from PIL import Image

from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # Project root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from engines.fruit_classifier.resnet import ResNet, BasicBlock

transform = transforms.Compose([
                    transforms.ToPILImage(),
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                        std=[0.229, 0.224, 0.225])
                ])

def img_to_tensor(image, device):
    img = image.copy()
    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)
    img /= 255.0
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = (img - mean) / std
    inp = np.transpose(img, (2, 0, 1))
    return torch.from_numpy(inp).float().to(device).unsqueeze(0)


CLASS_NAMES = ['A', 'B', 'VIP', 'C']

class FruitQualityClassifier:
    def __init__(self, device, model_path=None):
        self.device = device
        self.model = ResNet(img_channels=3, num_layers=18, block=BasicBlock, num_classes=4)
        self.model.to(device)

        print(f"[INFO] Loading checkpoint ... {model_path}")
        assert os.path.isfile(model_path), 'Error: No checkpoint file found' 

        checkpoint = torch.load(model_path)
        self.model.load_state_dict(checkpoint['state_dict'])
        self.model.eval()

    def classify(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #img = Image.fromarray(img)
        #img = img.convert('RGB')
        img = transform(img)
        # img = img_to_tensor(img, self.device)

        print(img.shape)

        with torch.no_grad():
            # add one extra batch dimension
            img = img.unsqueeze(0).to(self.device)
            print(img.shape)
            outputs = self.model(img)

        score = torch.softmax(outputs, 1)
        confidence, preds = torch.max(score, 1)
        fruit_class = CLASS_NAMES[preds]
        return fruit_class, confidence
