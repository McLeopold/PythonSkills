from setuptools import setup

setup(
    name='skills',
    version='0.3.0',
    author='Scott Hamilton',
    author_email='mcleopold@gmail.com',
    packages=['skills',
              'skills.trueskill',
              'skills.testsuite',
              'skills.testsuite.trueskill'
    ],
    url='http://github.com/McLeopold/PythonSkills/',
    license="BSD",
    description='Implementation of the TrueSkill, Glicko'
                ' and Elo Ranking Algorithms',
    long_description=open('README.rst').read(),
    keywords='skill trueskill glicko elo',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Games/Entertainment',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
