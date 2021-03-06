from setuptools import setup, find_packages
import os

version = '1.1.1'

setup(name='Products.KarthagoLayout',
      version=version,
      description="Layout for the Karthago website.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Classifier: Framework :: Zope2",
        "Classifier: License :: OSI Approved :: BSD License",
        "Classifier: Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Classifier: Programming Language :: Python",
        ],
      keywords='silva cms zope',
      author='Benno Luthiger',
      author_email='',
      url='http://www.aktion-hip.ch/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Products.Silva',
          'Products.RwLayout',
          'Products.RwCSCollection',
          'setuptools',
          'zope.component',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
