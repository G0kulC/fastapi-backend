################################################################################
#                              COMPILER STAGE                                  #
################################################################################

# Use official Python Alpine image as the base for the compiler stage
FROM python:3.10.9-alpine3.17 as COMPILER
# Install necessary build dependencies for compiling Cython or other extensions
RUN apk add --no-cache build-base
WORKDIR /app
# Copy necessary files for building the Python package
COPY api/ api/
COPY requirements.txt requirements.txt
COPY README.md README.md
COPY setup.py setup.py
COPY version.py version.py
# Install dependencies and build the Python wheel package
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python3 setup.py bdist_wheel

################################################################################
#                               BUILD STAGE                                    #
################################################################################

# Use the official Python Alpine image for the runtime environment
FROM python:3.10.9-alpine3.17
# Set the working directory
WORKDIR /app/
# Copy the wheel package and dependencies from the COMPILER stage
COPY --from=COMPILER /app/dist/api*.whl ./
COPY --from=COMPILER /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=COMPILER /usr/local/bin/*corn /usr/local/bin/
# Install the wheel package in the runtime environment
RUN pip install api*.whl
# Expose the default FastAPI port
EXPOSE 8080
# Command to run the FastAPI app using Uvicorn
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port 8080"]
