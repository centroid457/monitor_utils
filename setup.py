from setuptools import setup, find_packages

with open("README.md", "r") as f:
  readme = f.read()

# EDIT ================================================================================================================
# EDIT ================================================================================================================
# EDIT ================================================================================================================
# EDIT ================================================================================================================
# EDIT ================================================================================================================
NAME = "monitor_utils"

setup(
  version="0.0.2",
  description="monotiring exact data (urlTag) and alert on changes by email/telegram (threading)",
  keywords=[
      "monitor changes", "monitor data",
      "url changes", "url tag changes", "url monitor",
      "imap changes", "email changes", "imap monitor", "email monitor",
      "alerts", "notifications", "email alerts", "telegram alerts",
  ],
  classifiers=[
    # "Topic :: ",

    # EDIT ============================================================================================================
    # EDIT ============================================================================================================
    # EDIT ============================================================================================================
    # EDIT ============================================================================================================
    # EDIT ============================================================================================================

    # "Framework :: AsyncIO",
    "Topic :: Software Development :: Libraries :: Python Modules",
    # "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.11",
    "Operating System :: OS Independent",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "Typing :: Typed",
  ],

  name=NAME,
  author="Andrei Starichenko",
  author_email="centroid@mail.ru",
  long_description=readme,
  long_description_content_type="text/markdown",

  url="https://github.com/centroid457/",  # HOMEPAGE
  project_urls={
    # "Documentation": f"https://github.com/centroid457/{NAME}/blob/main/GUIDE.md",
    "Source": f"https://github.com/centroid457/{NAME}",
  },

  packages=[NAME, ],
  install_requires=[],
  python_requires=">=3.6"
)

# =====================================================================================================================
