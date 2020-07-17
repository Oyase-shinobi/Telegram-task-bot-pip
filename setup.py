from setuptools import setup

setup(
    name='telegram-task-bot',
    version='0.1.1',
    license='LGPLv3',
    description='Library for writing task based telegram bots',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='bb4L',
    author_email='39266013+bb4L@users.noreply.github.com',
    project_urls={"Source Code": "https://github.com/bb4L/telegram-task-bot-pip"},
    packages=['telegramtaskbot', 'telegramtaskbot.Tasks'],
    keywords=['Telegram', 'Bot'],
    install_requires=[
        'python-telegram-bot==12.2.0',
        'python-dotenv==0.10.3',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    include_package_data=True,
)
# python setup.py sdist && twine upload dist/*
