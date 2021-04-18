from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="imaprelay",
    description="IMAP relay: imaprelay filters and distributes messages from an IMAP INBOX to different recipients",
    long_description=long_description,
    author="Andreas Söhlke",
    author_email="githup@soehlke.de",
    url="https://github.com/asoehlke/imaprelay",
    license="MIT",
    version="1.1",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Topic :: Communications :: Email",
        "Topic :: Communications :: Email :: Email Clients (MUA)",
        "Topic :: Communications :: Email :: Mail Transport Agents",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    install_requires=[],
    entry_points={"console_scripts": ["imaprelay = imaprelay.command:main"]},
)
