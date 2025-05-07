from setuptools import setup, find_packages

setup(
    name="task_manager",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "click>=8.1.0",
        "tqdm>=4.64.0",
    ],
    entry_points={
        "console_scripts": [
            "taskman=src.cli:main",
        ],
    },
    description="A simple, efficient Python task management system",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/1106-Zechter-Heather/CS333_Final_Project",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)