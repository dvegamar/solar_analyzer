# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9

EXPOSE 8080

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install -r requirements.txt

# this command works for local test of the container where --server.address=0.0.0.0   has been added
CMD streamlit run --server.port 8080 --server.address=0.0.0.0 --server.enableCORS false energy_analizer_app.py