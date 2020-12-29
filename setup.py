import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wxtwitterbot-jnsnkrllive",
    version="0.0.1",
    author="Karl Jansen",
    author_email="jnsnkrl@live.com",
    description="Wx Twitter Bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jnsnkrllive/wx-twitter-bot",
    package_dir={'wxtwitterbot': 'src'},
    packages=['wxtwitterbot'],
    python_requires='>=3.8',
)
