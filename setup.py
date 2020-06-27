import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="NASsync", 
    version="0.0.1",
    author="Lorenzo Monacelli",
    description="A package for sync directories between computers trough the NAS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mesonepigreco/NASsync",
    packages=["NASsync"], 
    package_dir = {"NASsync": "Modules"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)