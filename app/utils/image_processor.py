import torch
import torchvision.transforms as T
from PIL import Image

# =================================================
# Image transform for FaceNet
# =================================================
transform = T.Compose([
    T.Resize((160, 160)),        # kích thước input của FaceNet
    T.ToTensor(),                # chuyển ảnh sang tensor
    T.Normalize(                 # chuẩn hóa dữ liệu
        mean=[0.5, 0.5, 0.5],
        std=[0.5, 0.5, 0.5]
    )
])


# =================================================
# Crop ảnh vuông ở giữa
# =================================================
def crop_center_square(image):
    """
    Crop ảnh thành hình vuông ở trung tâm
    """
    width, height = image.size
    size = min(width, height)

    left = (width - size) / 2
    top = (height - size) / 2
    right = (width + size) / 2
    bottom = (height + size) / 2

    image = image.crop((left, top, right, bottom))
    return image


# =================================================
# Chuyển ảnh thành vector embedding
# =================================================
def image_to_feature(image, model):
    """
    Convert image → face embedding vector
    """
    img = image.convert("RGB")         # đảm bảo ảnh RGB
    img = crop_center_square(img)      # crop ảnh

    img_tensor = transform(img).unsqueeze(0)  # thêm batch dimension

    with torch.no_grad():              # không cần gradient
        embedding = model(img_tensor)

    return embedding.squeeze().numpy()


# =================================================
# Get avatar image path for employee
# =================================================
def get_avatar_image(employee_name, dataset_path='static/dataset/'):
    """
    Get avatar image path for an employee.
    
    Args:
        employee_name (str): Name of the employee
        dataset_path (str): Path to dataset folder
    
    Returns:
        str: Path to avatar image or placeholder URL
    """
    import os
    avatar_path_jpg = os.path.join(dataset_path, f"Avatar_{employee_name}.jpg")
    avatar_path_JPG = os.path.join(dataset_path, f"Avatar_{employee_name}.JPG")
    
    if os.path.exists(avatar_path_jpg):
        return avatar_path_jpg
    elif os.path.exists(avatar_path_JPG):
        return avatar_path_JPG
    else:    
        return "https://via.placeholder.com/300?text=No+Photo"