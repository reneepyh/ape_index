ARG LAMBDA_TASK_ROOT="/var/task"

# Use the official Playwright Docker image as the base image, make sure the version matches the one you are using in your project
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy as build-image

# Re-declare ARG so it's available in this stage
ARG LAMBDA_TASK_ROOT
RUN mkdir -p ${LAMBDA_TASK_ROOT}
WORKDIR ${LAMBDA_TASK_ROOT}

# Install aws-lambda-cpp build dependencies
RUN apt-get update && apt-get install -y g++ make cmake unzip libcurl4-openssl-dev

# Install the runtime interface client
RUN pip install --target ${LAMBDA_TASK_ROOT} awslambdaric

# ==== MULTI STAGE BUILD ====

# Use multi-stage build, to keep the final image cleaner
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

# Re-declare ARG so it's available in this stage
ARG LAMBDA_TASK_ROOT
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy in the build image dependencies
COPY --from=build-image ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}

# Get the project dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt

# Install the specified packages
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Create function directory and copy the function code into it
COPY . .

# Considering your handler function is called lambda_handler in app.py
ENTRYPOINT [ "/usr/bin/python", "-m", "awslambdaric" ]
CMD [ "run_pipeline.lambda_handler" ]


