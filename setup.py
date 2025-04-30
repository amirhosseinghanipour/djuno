from setuptools import setup, find_packages

setup(
    name="djuno",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "django>=5.2",
        "click>=8.1",
        "django-tailwind>=4.0.1",
        "requests>=2.32.3",
        "watchfiles>=1.0.5",
        "mypy>=1.15.0",
        "lxml>=5.4.0",
    ],
    entry_points={
        "console_scripts": [
            "djuno = djuno.cli:cli",
        ],
    },
    include_package_data=True,
    description="Djuno is a Django component library",
    author="Amirhossein Ghanipour",
    author_email="d3v1ll3n@gmail.com",
    url="https://github.com/amirhosseinghanipour/djuno",
)
