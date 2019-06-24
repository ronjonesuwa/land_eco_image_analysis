#!/bin/bash

if [ "$GOOGLE_CLOUD_PROJECT" == "" ]; then
    echo "GOOGLE_CLOUD_PROJECT environment variable must be set"
    return
fi

GOOGLE_APPLICATION_CREDENTIALS=/home/${USER}/key.json

# create service account
gcloud iam service-accounts create my-vision-sa --display-name "my vision service account"
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT --member serviceAccount:my-vision-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com --role roles/editor
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT --member serviceAccount:my-vision-sa@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com --role roles/storage.admin
gcloud iam service-accounts keys create $GOOGLE_APPLICATION_CREDENTIALS --iam-account my-vision-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com

export GOOGLE_APPLICATION_CREDENTIALS
