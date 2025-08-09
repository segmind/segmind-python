# Contributing to Segmind

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Communication Channel

You can use Discord to communicate with us. Join our discord server [here](https://discord.gg/G5t5k2JRN6)

## We Develop with Github

We use github to host code, to track issues and feature requests, as well as accept pull requests.
Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've changed APIs, update the documentation.
3. Issue that pull request!

## Report bugs using Github's [issues]()

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Coding Style

`torchtune` uses pre-commit hooks to ensure style consistency and prevent common mistakes. Enable it by:

```bash
pre-commit install
```

After this pre-commit hooks will be run before every commit.

You can also run this manually on every file using:

```bash
pre-commit run --all-files
```

### Commit format

Please follow [conventional commits specification](https://www.conventionalcommits.org/) for descriptions/messages.
