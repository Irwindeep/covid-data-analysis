import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Concatenate, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import tensorflow as tf
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import ast, re
from PIL import Image

# Set random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

def clean_data(df, missing_threshold=0.3, n_neighbors=5):
    missing_percent = df.isnull().mean()
    
    cols_to_drop = missing_percent[missing_percent > missing_threshold].index
    df = df.drop(columns=cols_to_drop)

    numerical_cols = df.select_dtypes(include=['number']).columns[1:]
    
    imputer = KNNImputer(n_neighbors=n_neighbors)
    imputed_data = imputer.fit_transform(df[numerical_cols])

    df[numerical_cols] = imputed_data
    
    scaler = MinMaxScaler()
    normalized_data = scaler.fit_transform(df[numerical_cols])
    df[numerical_cols] = normalized_data
        
    return df

def load_data(df: pd.DataFrame):
    image_paths = [f"./dataset/processed_images/{int(person_id)}/Chest.png" for person_id in df['person_id']]
    
    thermal_images = np.array([np.array(Image.open(path)) for path in image_paths])
    lbp_feats = df.drop(columns=['person_id','name','age','gender','health_status','lbp_hist']).values
    labels = df['health_status'].values

    label_mapping = {'Healthy': 1, 'Unhealthy': 0}
    labels = np.array([label_mapping[label] for label in labels])

    thermal_images = thermal_images[..., np.newaxis] / 255.0
    return thermal_images, lbp_feats, labels

# Build CNN model
def build_cnn(input_shape=(128, 128, 1)):
    inputs = Input(shape=input_shape)
    x = Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
    x = MaxPooling2D((2, 2))(x)
    x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2))(x)
    x = Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2))(x)
    x = Flatten()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    cnn_output = Dense(64, activation='relu')(x)
    return Model(inputs=inputs, outputs=cnn_output)

# Build combined model
def build_combined_model(cnn_model, num_handcrafted_features):
    cnn_input = cnn_model.input
    cnn_features = cnn_model.output
    
    handcrafted_input = Input(shape=(num_handcrafted_features,))
    combined = Concatenate()([cnn_features, handcrafted_input])
    
    x = Dense(128, activation='relu')(combined)
    x = Dropout(0.5)(x)
    x = Dense(64, activation='relu')(x)
    output = Dense(1, activation='sigmoid')(x)
    
    model = Model(inputs=[cnn_input, handcrafted_input], outputs=output)
    model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Train the model
def train_model(train_df, test_df):
    print("Preparing training and testing data...")
    
    train_images, train_features, train_labels = load_data(train_df)
    test_images, test_features, test_labels = load_data(test_df)

    print(train_features.shape)

    cnn_model = build_cnn(input_shape=(128, 128, 1))
    combined_model = build_combined_model(cnn_model, train_features.shape[1])
    
    checkpoint_path = "best_model.keras"
    checkpoint = ModelCheckpoint(checkpoint_path, monitor='val_accuracy', save_best_only=True, verbose=1)
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    
    history = combined_model.fit(
        [train_images, train_features], train_labels,
        validation_data=([test_images, test_features], test_labels),
        epochs=20, batch_size=32, callbacks=[checkpoint, early_stopping]
    )
    combined_model.load_weights(checkpoint_path)

    return combined_model, test_images, test_features, test_labels

# Evaluate the model
def evaluate_model(model, test_images, test_features, test_labels):
    print("Evaluating model on test data...")
    predictions = (model.predict([test_images, test_features]) > 0.5).astype(int)
    accuracy = accuracy_score(test_labels, predictions)
    
    print(f"Test Accuracy: {accuracy:.2f}")
    print("Classification Report:")
    print(classification_report(test_labels, predictions))

# Save the trained model
def save_model(model, model_path="final_model.joblib"):
    joblib.dump(model, model_path)
    print(f"Model saved at {model_path}")

def fix_string_format(x):
    x = re.sub(r'\s+', ' ', x)
    return x.replace('\n', ' ').replace(' ', ', ')

if __name__ == "__main__":
    train_df, test_df = pd.read_csv("./dataset/train_data.csv"), pd.read_csv("./dataset/test_data.csv")

    train_df['lbp_hist'] = train_df['lbp_hist'].apply(fix_string_format).apply(ast.literal_eval)
    test_df['lbp_hist'] = test_df['lbp_hist'].apply(fix_string_format).apply(ast.literal_eval)

    train_df = clean_data(train_df)
    test_df = clean_data(test_df)
    
    model, test_images, test_features, test_labels = train_model(train_df, test_df)
    
    evaluate_model(model, test_images, test_features, test_labels)
    save_model(model)
