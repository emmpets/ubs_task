# Use the official Python image from the Docker Hub
FROM python:3.10.14-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python3-dev \
    python3-setuptools

ARG SQLITE_VERSION=3.46.0
RUN wget https://sqlite.org/2024/sqlite-autoconf-3460000.tar.gz \
    && tar xzf sqlite-autoconf-3460000.tar.gz \
    && cd sqlite-autoconf-3460000 \
    && ./configure \
    && make \
    && make install \
    && cd .. \
    && rm -rf sqlite-autoconf-3460000 \
    && rm sqlite-autoconf-3460000.tar.gz

# Install the required packages
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

RUN sed -i "1 i\__import__('pysqlite3')\nimport sys\nsys.modules['sqlite3'] = sys.modules.pop('pysqlite3')" streamlit_vector_db_app.py

# Expose the port that Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit app
CMD ["python", "-m", "streamlit", "run", "streamlit_vector_db.py", "--server.port=8501", "--server.address=0.0.0.0"]