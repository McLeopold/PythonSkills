from distutils2.core import setup

setup(
    name='skills',
    packages=['skills',
              'skills.trueskill'
    ],
    version='0.1',
    summary='Implementation of the TrueSkill, Glicko'
            ' and Elo Ranking Algorithms',
    author='Scott Hamilton',
    author_email='mcleopold@gmail.com',
    home_page='http://github.com/McLeopold/PythonSkills/',
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
