import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wxtwitterbot",
    version="0.1.0",
    author="Karl Jansen",
    author_email="jnsnkrl@live.com",
    license="MIT",
    description="Wx Twitter Bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jnsnkrllive/wx-twitter-bot",
    package_dir={'wxtwitterbot': 'src'},
    packages=['wxtwitterbot', 'wxtwitterbot.tasks'],
    python_requires='>=3.8',
    install_requires=[
        "astral",
        "python-dotenv",
        "pytz",
        "tweepy",
        "requests"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
