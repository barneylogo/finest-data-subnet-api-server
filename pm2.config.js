module.exports = {
    apps: [
        {
            name: "django-app",
            script: "manage.py",
            args: "runserver 0.0.0.0:8000",
            interpreter: "python", // Ensure this points to your Python interpreter
            watch: false, // Optional: watches for file changes
            env: {
                // "DJANGO_SETTINGS_MODULE": "config.settings.local",
            }
        }
    ]
};