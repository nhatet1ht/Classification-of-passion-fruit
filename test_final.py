from ultralytics import YOLO
import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image
from torchvision.models import resnet18
import logging
import os

logging.getLogger('ultralytics').setLevel(logging.CRITICAL)

# Load YOLOv8 model
yolo_model = YOLO(r'C:\work\detection_yolo\working\runs\detect\train6\weights\classify.pt')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load classification model
classification_model = resnet18(pretrained=False, num_classes=4)  # Assume you have a custom trained ResNet18
classification_model.load_state_dict(torch.load('model_weights.pth', map_location=device))  # Adjust path as needed
classification_model.to(device)
classification_model.eval()

# Define image transformations
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
# Setup đường line
line_y = 500
line_color = (0, 255, 0)  # Green line for visibility
line_thickness = 2
# Load video
video_path = r'C:\work\passionfruit_test\video_test_1.avi'
cap = cv2.VideoCapture(video_path)

# Define class names for ResNet18
class_names = ['A', 'B', 'C', 'VIP']

evaluated_tracks = set() 
image_count = 0  # Initialize image counter

# Create directory to save classified images if it doesn't exist
output_dir = 'classify_result'
os.makedirs(output_dir, exist_ok=True)

# Read frames
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_resized = cv2.resize(frame, (1000, 700))
    frame_resized_proc = frame_resized.copy()
    cv2.line(frame_resized, (0, line_y), (1000, line_y), line_color, line_thickness)

    # Track objects
    results = yolo_model.track(frame_resized_proc, persist=True)

    for obj in results[0].boxes:
        # Extract bounding box
        bbox = obj.xyxy[0].cpu().numpy().astype(int)
        x1, y1, x2, y2 = bbox
        if obj.id is not None:
            track_id = int(obj.id.item())
            if track_id not in evaluated_tracks and line_y > y2:
                # Add track_id to evaluated_tracks set
                evaluated_tracks.add(track_id)

                obj_img = frame_resized_proc[y1:y2, x1:x2]

                # Apply transformations
                obj_img_tensor = transform(obj_img).unsqueeze(0).to(device)

                # Classify object
                with torch.no_grad():
                    output = classification_model(obj_img_tensor)
                    _, predicted = torch.max(output, 1)
                    label = class_names[predicted.item()]
                cv2.rectangle(frame_resized, (x1-10, y1-10), (x2+10, y2+20), (255, 0, 0), 2)
                cv2.putText(frame_resized, f'ID: {track_id} {label}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                print('Quả số ' , track_id, ' loại: ', label)

                # Save the classified image
                image_count += 1
                file_name = f'classified_{image_count}_{label}.jpg'
                file_path = os.path.join(output_dir, file_name)
                cv2.imwrite(file_path, obj_img)
            label = class_names[predicted.item()]

            cv2.rectangle(frame_resized, (x1-10, y1-10), (x2+10, y2+20), (255, 0, 0), 2)
            cv2.putText(frame_resized, f'ID: {track_id} {label}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)   
            cv2.rectangle(frame_resized, (x1, y1), (x2, y2), (0, 255, 255), 2)
    # Visualize
    cv2.imshow('frame', frame_resized)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
