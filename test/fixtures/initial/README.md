# Deploy status helper

Prints which deployment this build talks to.

Run it with:

    python status_message.py

The deployment name comes from the `DEPLOY_ENV` environment variable and
falls back to `development` when it is not set.
