from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in rma/__init__.py
from rma import __version__ as version

setup(
	name="rma",
	version=version,
	description="Returns made simple",
	author="Gross Innovatives",
	author_email="dev@gross.dev.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
