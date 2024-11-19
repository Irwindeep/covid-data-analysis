# Covid Data: Healthy or Unhealthy Classification

This project addresses the challenge of real-time public health monitoring during the Covid-19 pandemic. Using a thermal imaging dataset, it provides an automated pipeline for classifying individuals as "Healthy" or "Unhealthy." This system integrates data engineering, machine learning, and a user-friendly interface for end-to-end functionality.

---

## Features

- **Data Pipeline**: Automated ingestion, preprocessing, and indexing of thermal imaging data using Apache Airflow.
- **Database Integration**: A relational database schema in MySQL to manage structured health and thermal session data.
- **Classification System**: A hybrid deep learning model combining CNNs for image-based features and statistical analysis for handcrafted features.
- **Visualization**: User-friendly interface to display results and pipeline outputs.

---

## Requirements

Install the project dependencies with:

```
pip install -r requirements.txt
```

Ensure you have Docker, MySQL, Apache Airflow, and Elasticsearch configured.

---

## Data Workflow

1. **Data Ingestion**:
   - Datasets like thermal images and health metrics are loaded and validated.
   - MySQL is used for structured data storage.
   - Processed data is indexed in Elasticsearch for fast querying.

2. **Data Preprocessing**:
   - Thermal images are resized and motion patterns are analyzed.
   - Features like local binary patterns and temperature metrics are extracted.

3. **Classification**:
   - A CNN processes spatial features from images.
   - Handcrafted features are combined in a dense network.
   - Outputs classify individuals as "Healthy" or "Unhealthy."

---

## Setup and Usage

1. Clone the repository:
   ```
   git clone https://github.com/Irwindeep/covid-data-analysis.git
   ```
   
2. Navigate to the project directory:
   ```
   cd covid-data-analysis
   ```

3. Configure `.env` or other settings for database credentials and dependencies.

4. Run the pipeline:
   - Start the Airflow web server:
     ```
     airflow webserver -p 8080
     ```
   - Trigger the pipeline through the Airflow interface.

5. Run the classification model:
   ```
   python train.py
   ```

---

## Dataset

The project uses the **Covid-19 Thermal Imaging Dataset (v1.1)** from the PhysioNet Repository. For more details, visit the [dataset page](https://physionet.org/content/covid-19-thermal/1.1).

---

## Contributors

- Irwindeep Singh: ([irwin](https://github.com/Irwindeep))
- Sarthak Malviya ([sarthakm1512](https://github.com/sarthakm1512))

For queries, contact us via the [GitHub repository](https://github.com/Irwindeep/covid-data-analysis).

---
