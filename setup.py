from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="solfsound-dispatcher",
    version="1.0.0",
    author="SolfSound Team",
    description="A powerful audio extraction and separation tool for videos and music",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Augustino127/solfsound-dispatcher",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydub>=0.25.1",
        "ffmpeg-python>=0.2.0",
        "librosa>=0.10.0",
        "soundfile>=0.12.1",
        "demucs>=4.0.0",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "tqdm>=4.65.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "solfsound=solfsound.cli:main",
        ],
    },
)
