from setuptools import setup, find_packages

setup(
    name="adsgen",
    version="0.1.0",
    description="Adsorption training structure generator using BOSS and MACE",
    author="",
    packages=find_packages(),
    install_requires=[
        "ase",
        "matplotlib",
        "numpy"
    ],
    entry_points={
        "console_scripts": [
            "adsgen-generate=adsgen.generator:main",
            "adsgen-vaspgen=adsgen.structure_io:main",
            "adsgen-compare=adsgen.analysis:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

