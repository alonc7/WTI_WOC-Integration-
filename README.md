WooCommerce & WATI Integration with Flask
This project demonstrates a webhook integration between a WATI messaging platform and a WooCommerce store built using the Flask framework in Python.

Project Functionality:

The application acts as a webhook endpoint for WATI, receiving customer data.
It extracts relevant information (name, phone number, and cart items) from the received data.
It creates a new order in the WooCommerce store using the extracted customer information and cart items.
Upon successful order creation, it sends a notification message to the customer's phone number via the WATI API, including a payment link.
Technologies Used:

Flask: A lightweight web application framework for Python.
Requests: A Python library for making HTTP requests to APIs.
dotenv: A library for securely loading environment variables from a .env file.
Code Structure:

app.py: The main Flask application file containing the logic for handling the WATI webhook and interacting with the WooCommerce and WATI APIs.
.env (not included): This file should contain sensitive information like API credentials (not included for security reasons).
Running the Application:

Create a .env file in the project directory.

Add the following environment variables to the .env file, replacing the placeholders with your actual credentials:

WC_API_URL: URL of your WooCommerce API endpoint.
WC_CONSUMER_KEY: WooCommerce consumer key.
WC_CONSUMER_SECRET: WooCommerce consumer secret.
WATI_API_URL: URL of your WATI API endpoint.
WATI_API_KEY: Your WATI API key.
UNIQUE_ID: A unique identifier for your webhook endpoint.
Install required libraries:

Bash
pip install Flask requests python-dotenv
חשוב להשתמש בקוד בזהירות.
content_copy
Run the application:

Bash
python app.py
חשוב להשתמש בקוד בזהירות.
content_copy
Configuration:

The application listens on port 5000 by default. You can change this by modifying the port argument in app.run().
The debug mode is enabled by default (debug=True). This is useful for development but should be disabled in production environments.
Deployment:

This is a basic demonstration and might require adjustments for deployment in a production environment. Consider using a production-grade web server like Gunicorn or uWSGI for deployment.

Additional Notes:

Error handling and logging are implemented for informative debugging.
Security best practices are followed by storing sensitive information in environment variables.
Further Considerations:

This is a simplified example. Real-world integration might involve handling various data formats, error scenarios, and authentication mechanisms.
Consider adding unit tests to ensure code functionality.
I hope this README provides a comprehensive overview of the project. Feel free to reach out if you have any questions.
