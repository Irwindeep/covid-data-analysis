import cv2
import numpy as np
import pandas as pd
import os
from skimage.transform import resize
from skimage.feature import local_binary_pattern
from sklearn.model_selection import train_test_split

class Preprocessor:
    def __init__(self, session_data, output_size=(128, 128), save_hr_images: bool = False):
        self.person_id = session_data['person_id']
        self.video_path = session_data['image_path']
        self.room_temp = session_data['room_temp']
        self.min_temp = session_data['min_temp']
        self.max_temp = session_data['max_temp']
        self.view = session_data['view']
        self.output_size = output_size
        self.frames = []
        self.optical_flows = []

        self.save_hr_images = save_hr_images

    def load_video(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            resized_frame = resize(gray_frame, self.output_size, anti_aliasing=True)
            self.frames.append(resized_frame)
        cap.release()

    def calculate_optical_flow(self):
        if len(self.frames) < 2:
            return

        prev_frame = self.frames[0]
        for i in range(1, len(self.frames)):
            curr_frame = self.frames[i]
            flow = cv2.calcOpticalFlowFarneback(prev_frame, curr_frame, None,
                                               0.5, 3, 15, 3, 5, 1.2, 0)
            self.optical_flows.append(flow)
            prev_frame = curr_frame

    def generate_high_resolution_image(self):
        if len(self.frames) == 0:
            return None

        hr_image = np.mean(self.frames[25:], axis=0)

        if np.isnan(hr_image).any() or hr_image.size == 0:
            return None

        if self.save_hr_images:
            save_path = f"./dataset/processed_images/{self.person_id}/{self.view}.png"

            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, (hr_image * 255).astype(np.uint8))

        return hr_image

    def extract_features(self, image):
        features = {}

        radius = 3
        n_points = 8 * radius
        lbp = local_binary_pattern((image * 255).astype(np.uint8), n_points, radius, method='uniform')
        features['lbp_hist'] = np.histogram(lbp.ravel(), bins=np.arange(0, n_points + 3), density=True)[0]

        features['temp_variance'] = np.var(image)
        features['mean_temp'] = np.mean(image)
        features['min_temp'] = self.min_temp
        features['max_temp'] = self.max_temp
        features['room_temp'] = self.room_temp

        return features

    def preprocess(self):
        self.load_video()
        self.calculate_optical_flow()
        hr_image = self.generate_high_resolution_image()

        if hr_image is not None:
            features = self.extract_features(hr_image)
            return hr_image, features
        
        return None, None


def preprocess_dataset(df):
    processed_data = []

    for index, row in df.iterrows():
        session1_data = {
            'person_id': row['person_id'],
            'image_path': row['session1_image_path'],
            'room_temp': row['session1_room_temp'],
            'min_temp': row['session1_min_temp'],
            'max_temp': row['session1_max_temp'],
            'view': row['session1_view']
        }

        session2_data = {
            'person_id': row['person_id'],
            'image_path': row['session2_image_path'],
            'room_temp': row['session2_room_temp'],
            'min_temp': row['session2_min_temp'],
            'max_temp': row['session2_max_temp'],
            'view': row['session2_view']
        }

        preprocessor_s1, preprocessor_s2 = Preprocessor(session1_data, save_hr_images=True), Preprocessor(session2_data, save_hr_images=True)
        hr_image_s1, features_s1 = preprocessor_s1.preprocess()
        hr_image_s2, features_s2 = preprocessor_s2.preprocess()

        if (
            hr_image_s1 is not None and
            hr_image_s2 is not None
        ):
            entry = {
                'person_id': row['person_id'],
                'name': row['name'],
                'age': row['age'],
                'gender': row['gender'],
                'health_status': row['health_status'],
                **features_s1,
                **features_s2
            }
            processed_data.append(entry)
    
    return pd.DataFrame(processed_data)

if __name__ == "__main__":
    dataset_path = "./dataset/full.csv"
    df = pd.read_csv(dataset_path)
    
    processed_df = preprocess_dataset(df)
    print(processed_df.head())
    processed_df.to_csv("./dataset/processed_full.csv", index=False)

    processed_df = pd.read_csv("./dataset/processed_full.csv")

    processed_male = processed_df[processed_df['gender'] == 'Male']
    processed_female = processed_df[processed_df['gender'] == 'Female']

    test_size = 0.3

    train_male, test_male = train_test_split(processed_male, test_size=test_size, random_state=42)
    train_female, test_female = train_test_split(processed_female, test_size=test_size, random_state=42)

    train_df = pd.concat([train_male, train_female], axis=0).reset_index(drop=True)
    test_df = pd.concat([test_male, test_female], axis=0).reset_index(drop=True)

    train_df = train_df.sample(frac=1, random_state=42).reset_index(drop=True)
    test_df = test_df.sample(frac=1, random_state=42).reset_index(drop=True)

    print("Training set gender distribution:")
    print(train_df['gender'].value_counts())
    print("\nTesting set gender distribution:")
    print(test_df['gender'].value_counts())

    train_df.to_csv("./dataset/train_data.csv", index=False)
    test_df.to_csv("./dataset/test_data.csv", index=False)