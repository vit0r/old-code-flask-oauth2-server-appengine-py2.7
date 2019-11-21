from setuptools import setup

setup(
    name='machinemon-oauth2-server',
    version=0.1,
    license='BSD',
    url='machinemon-oauth2-server.appspot.com',
    author='Vitor Nascimento Araújo',
    author_email='vitornascimentoaraujo@gmail.com',
    description='Simple oauth2 server',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: BSD License',
    ],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    test_suite='nose.collector',
    install_requires=['Flask==1.0', 'Flask-OAuthlib>=0.5.0', 'PyYAML==3.11', 'nose==1.3.7', 'gcloud==0.18.1']
)
