# VidGear Video Streamer Dockerfile
# =====================================
# Multi-stage build for optimized image size
# Includes FFmpeg, GStreamer, and OpenCV with full video support

# Stage 1: Install OpenCV from source with GStreamer and FFmpeg support
FROM ubuntu:22.04 AS opencv-installer

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
    # Build essentials
    build-essential \
    cmake \
    pkg-config \
    git \
    curl \
    python3 \
    python3-pip \
    python3-dev \
    ca-certificates \
    # Python development
    python3-dev \
    # Video and codec libraries
    libavcodec58 \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    ffmpeg \
    yasm \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    # Image format libraries
    libtiff-dev \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    libopenexr-dev \
    # Math libraries
    libatlas-base-dev \
    liblapacke-dev \
    libopenblas-dev \
    # GUI and parallel processing
    libtbb-dev \
    # GStreamer
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    # Other dependencies
    zlib1g-dev \
    libunwind-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory for build
WORKDIR /tmp/opencv-build

# Get Python paths
RUN PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))') && \
    echo "Python version: $PYTHON_VERSION" && \
    echo "PYTHON_VERSION=$PYTHON_VERSION" > /tmp/python_version.env

# Download and install OpenCV from VidGear Source Repository
RUN PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH && \
    PYTHONSUFFIX=$(python3 -c 'import platform; a = platform.python_version(); print(".".join(a.split(".")[:2]))') && \
    echo "Python suffix: $PYTHONSUFFIX" && \
    LATEST_VERSION=$(curl -sL https://api.github.com/repos/abhiTronix/OpenCV-CI-Releases/releases/latest | \
        grep "OpenCV-.*.*-*-$PYTHONSUFFIX.*.deb" | \
        grep -Eo "(http|https)://[a-zA-Z0-9./?=_%:-]*") && \
    echo "Latest OpenCV package URL: $LATEST_VERSION" && \
    curl -LO $LATEST_VERSION && \
    OPENCV_FILENAME=$(basename "$LATEST_VERSION") && \
    python3 -m pip install numpy && \
    dpkg -i ./"$OPENCV_FILENAME" && \
    ln -s /usr/local/lib/python$PYTHONSUFFIX/site-packages/*.so /usr/lib/python3/dist-packages && \
    ldconfig

RUN echo "OpenCV working version is $(python3 -c 'import cv2; print(cv2.__version__)')"

# Stage 2: Runtime image
FROM ubuntu:22.04

# Metadata
LABEL maintainer="VidGear Framework"
LABEL description="VidGear Video Streamer with FFmpeg, GStreamer, and OpenCV support"
LABEL version="1.0"

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
    # Build essentials
    build-essential \
    cmake \
    pkg-config \
    git \
    curl \
    python3 \
    python3-pip \
    python3-dev \
    ca-certificates \
    # Python development
    python3-dev \
    # Video and codec libraries
    libavcodec58 \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    ffmpeg \
    yasm \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    # Image format libraries
    libtiff-dev \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    libopenexr-dev \
    # Math libraries
    libatlas-base-dev \
    liblapacke-dev \
    libopenblas-dev \
    # GUI and parallel processing
    libtbb-dev \
    # GStreamer
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    # Other dependencies
    zlib1g-dev \
    libunwind-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy OpenCV from builder stage
COPY --from=opencv-installer /usr/local/lib/ /usr/local/lib/
COPY --from=opencv-installer /usr/local/include/ /usr/local/include/
COPY --from=opencv-installer /usr/local/bin/ /usr/local/bin/
COPY --from=opencv-installer /usr/local/share/ /usr/local/share/

# Link OpenCV shared libraries to dist-packages for Python
RUN PYTHONSUFFIX=$(python3 -c 'import platform; a = platform.python_version(); print(".".join(a.split(".")[:2]))') && \
    echo "Python suffix: $PYTHONSUFFIX" && \
    ln -s /usr/local/lib/python$PYTHONSUFFIX/site-packages/*.so /usr/local/lib/python$PYTHONSUFFIX/dist-packages || true

# Update library cache
RUN ldconfig

# Create a non-root user for security
RUN groupadd -r vidgear && \
    useradd -r -g vidgear -m -s /bin/bash vidgear && \
    mkdir -p /output && \
    chown -R vidgear:vidgear /output

# Set working directory
WORKDIR /app

# Install Python dependencies
# Copy requirements first for better layer caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --default-timeout=1000 --upgrade pip setuptools
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt
RUN pip install --no-cache-dir --default-timeout=1000 --upgrade "yt-dlp[default]"

# Verify installations
RUN python3 -c "import cv2; print(f'OpenCV: {cv2.__version__}')" && \
    python3 -c "import vidgear; print(f'VidGear: {vidgear.__version__}')" && \
    ffmpeg -version | head -n 1

# Copy application code
COPY /app ./app

# Change ownership of application files
RUN chown -R vidgear:vidgear /app

# Switch to non-root user
USER vidgear

# Run the application
ENTRYPOINT ["python3", "-m", "app.streamer"]
