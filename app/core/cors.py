
# CORS configuration
CORS_KWARGS = {
    "allow_origins": [
        "https://helperu.com",
        "https://www.helperu.com",
        "http://localhost:5173",  # Development
        "http://localhost:3000",  # Development
    ],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
