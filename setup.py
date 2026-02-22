from setuptools import setup, find_packages

setup(
    name="sergei-mikhailov-tg-channel-reader",
    version="0.1.0",
    description="OpenClaw skill: read Telegram channels via MTProto",
    author="Sergey Mikhailov",
    url="https://github.com/bzSega/sergei-mikhailov-tg-channel-reader",
    license="MIT",
    py_modules=["reader"],
    install_requires=[
        "pyrogram>=2.0.0",
        "tgcrypto>=1.2.0",
    ],
    entry_points={
        "console_scripts": [
            "tg-reader=reader:main",
        ],
    },
    python_requires=">=3.9",
)
