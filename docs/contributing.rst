Contributing
============

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

Communication Channel
---------------------

You can use Discord to communicate with us. Join our Discord server `here <https://discord.gg/G5t5k2JRN6>`_.

Development with GitHub
-----------------------

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.
Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from ``main``
2. If you've changed APIs, update the documentation
3. Issue that pull request!

Bug Reports
-----------

We use GitHub issues to track public bugs. Report a bug by opening a new issue; it's that easy!

Writing Good Bug Reports
~~~~~~~~~~~~~~~~~~~~~~~~

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce

  - Be specific!
  - Give sample code if you can

- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

Coding Style
------------

The Segmind SDK uses pre-commit hooks to ensure style consistency and prevent common mistakes. Enable it by:

.. code-block:: bash

   pre-commit install

After this, pre-commit hooks will be run before every commit.

You can also run this manually on every file using:

.. code-block:: bash

   pre-commit run --all-files

Commit Format
~~~~~~~~~~~~~

Please follow `conventional commits specification <https://www.conventionalcommits.org/>`_ for descriptions/messages.

Examples:

.. code-block:: text

   feat: add support for streaming responses
   fix: handle timeout errors in pixelflows
   docs: update API reference for webhooks
   test: add unit tests for file upload

Development Setup
-----------------

1. **Clone the repository**:

   .. code-block:: bash

      git clone https://github.com/segmind/segmind.git
      cd segmind

2. **Create a virtual environment**:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**:

   .. code-block:: bash

      pip install -e ".[dev]"

4. **Install pre-commit hooks**:

   .. code-block:: bash

      pre-commit install

5. **Run tests**:

   .. code-block:: bash

      pytest

Building Documentation
----------------------

To build the documentation locally:

.. code-block:: bash

   cd docs
   pip install -r requirements.txt
   make html

The built documentation will be available in ``docs/_build/html/``.

Testing
-------

We use pytest for testing. Run the test suite with:

.. code-block:: bash

   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=segmind

   # Run specific test file
   pytest tests/test_client.py

Adding New Features
-------------------

When adding new features:

1. **Write tests first** - Follow test-driven development
2. **Update documentation** - Add examples and API docs
3. **Follow existing patterns** - Look at similar functionality
4. **Add type hints** - All public APIs should be typed
5. **Update examples** - Add usage examples if appropriate

Pull Request Process
--------------------

1. **Create a feature branch** from ``main``
2. **Make your changes** with appropriate tests
3. **Update documentation** if needed
4. **Run the full test suite** to ensure nothing breaks
5. **Submit a pull request** with a clear description

Pull Request Checklist
~~~~~~~~~~~~~~~~~~~~~~

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventional format
- [ ] No merge conflicts with main branch

License
-------

By contributing, you agree that your contributions will be licensed under the same license as the project.
