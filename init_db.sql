-- Table to store basic information about individuals
CREATE TABLE persons(
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    age INT CHECK(age > 0),
    gender ENUM('Male', 'Female'),
    email VARCHAR(255) UNIQUE,
    phone_no VARCHAR(20),
    address VARCHAR(255),
    version VARCHAR(255) NOT NULL DEFAULT '1.0',
    version_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table to store details of each thermal session
CREATE TABLE thermal_sessions(
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT,
    session_date DATE NOT NULL,
    room_temperature DECIMAL(4, 2) CHECK(room_temperature BETWEEN -50.0 AND 50.0),
    view ENUM('Chest', 'Face', 'Back', 'Side'),
    version VARCHAR(255) NOT NULL DEFAULT '1.0',
    version_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE
);

-- Table to store thermal images and their details
CREATE TABLE thermal_images(
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    image_path VARCHAR(255) NOT NULL,
    min_temperature DECIMAL(5, 2) NOT NULL,
    max_temperature DECIMAL(5, 2) NOT NULL,
    region_of_interest ENUM('Chest', 'Face', 'Back', 'Side'),
    version VARCHAR(255) NOT NULL DEFAULT '1.0',
    version_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP.
    FOREIGN KEY (session_id) REFERENCES thermal_sessions(session_id) ON DELETE CASCADE
);

-- Table to store vital sign measurements of individuals
CREATE TABLE vital_signs(
    vital_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT,
    heart_rate INT CHECK(heart_rate > 0),
    oxygen_saturation DECIMAL(3, 2) CHECK(oxygen_saturation BETWEEN 0 AND 100),
    systolic_pressure DECIMAL(4, 1) CHECK(systolic_pressure > 0),
    diastolic_pressure DECIMAL(4, 1) CHECK(diastolic_pressure > 0),
    version VARCHAR(255) NOT NULL DEFAULT '1.0',
    version_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE
);

-- Table to store final health status of the individual
CREATE TABLE health_status(
    status_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT,
    covid_symptoms TEXT,
    forehead_temp DECIMAL(5, 2),
    status ENUM('Healthy', 'Unhealthy'),
    version VARCHAR(255) NOT NULL DEFAULT '1.0',
    version_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES persons(person_id) ON DELETE CASCADE
);