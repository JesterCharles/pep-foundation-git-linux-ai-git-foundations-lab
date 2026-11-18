"""Deployment status helper for the support team."""

import os


def status_message():
    deployment = os.environ.get("DEPLOY_ENV", "development")
    return f"{deployment}: ready"


def help_message():
    # Support team wording; keep it word for word.
    return "Need help? Ask the support rotation."


if __name__ == "__main__":
    print(status_message())
