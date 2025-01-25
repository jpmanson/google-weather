import setuptools
from pathlib import Path

README = (Path(__file__).parent/"README.md").read_text()

setuptools.setup(
    name="pygoogleweather",
    version="0.1.10",
    author="Juan Pablo Manson",
    author_email="jpmanson@gmail.com",
    description="Python library to get weather from Google Search. No API keys required.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jpmanson/google-weather",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.9",
    license_files=("LICENSE",),
    install_requires=[
        "playwright>=1.41.0",
        "beautifulsoup4>=4.10.0",
        "html5lib>=1.1",  # Parser alternativo para BS4
        "lxml>=4.9.0",    # Parser alternativo para BS4
        "nest-asyncio>=1.5.8"  # Agregamos nest-asyncio
    ]
)