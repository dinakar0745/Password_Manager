# Password Manager Web Application

## Overview

This is a simple web application built with Flask, MySQL, and cryptography to manage user passwords securely. Users can sign up, log in, add passwords, and view their saved passwords.

## Features

- **User Authentication:** Users can sign up with their name, email, phone number, and password. Existing users can log in securely with their email and password.
- **Password Encryption:** User passwords are encrypted using the Fernet encryption algorithm before storing them in the database. This ensures that passwords are securely stored and can only be decrypted with the encryption key.
- **Password Management:** Users can add, view, and manage their saved passwords. Each password entry includes details such as the website, username, and encrypted password.

# Setup

1. **Clone the Repository:** Clone this repository to your local machine.
    ```bash
    git clone https://github.com/dinakar0745/Password_Manager
    ```

2. **Install Dependencies:** Install the required Python packages listed in the 'requirements.txt' file.
    ```bash
    pip install -r requirements.txt
    ```

3. **Database Setup:** Set up your MySQL database and configure the connection details in the 'app.py' file.
    ```bash
    CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
    );
    ```
    ```bash
    CREATE TABLE passwords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    website VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
    );
    ```
    ```bash
    CREATE TABLE encryption_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    encryption_key TEXT NOT NULL
    );
    ```

4. **Run the Application:** Start the Flask application.
    ```bash
    python app.py
    ```

5. **Access the Application:** Access the web application in your browser at 'http://127.0.0.1:5000'

# Contributing
Contributions are welcome! If you have any suggestions, feature requests, or bug reports, please open an issue or submit a pull request.