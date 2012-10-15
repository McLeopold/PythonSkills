from distutils.core import setup

setup(
    name='skills',
    version='0.2.0',
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
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Games/Entertainment',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
