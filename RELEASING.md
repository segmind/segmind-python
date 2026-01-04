# Release Process

This document describes the process for releasing new versions of the Segmind Python SDK to PyPI.

## Prerequisites

Before you can create releases, ensure you have:

1. **Maintainer access** to the PyPI package "segmind"
2. **Write access** to the GitHub repository
3. **Trusted Publisher configured** on PyPI (recommended) or API tokens set up

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **Major version (X.0.0)**: Breaking changes that require code updates
- **Minor version (0.X.0)**: New features that are backwards-compatible
- **Patch version (0.0.X)**: Bug fixes and minor improvements

## Release Steps

### 1. Prepare the Release

1. **Update version** in `segmind/__init__.py`:
   ```python
   __version__ = "X.Y.Z"
   ```

2. **Update CHANGELOG.md** (if exists):
   - Move items from "Unreleased" to a new version section
   - Add release date
   - Create comparison links

3. **Run tests locally**:
   ```bash
   make test
   # or
   pytest tests/ -v
   ```

4. **Run linting**:
   ```bash
   make lint
   # or
   pre-commit run --all-files
   ```

5. **Test building locally** (optional but recommended):
   ```bash
   make build-check
   # or
   python -m build && twine check dist/*
   ```

6. **Commit changes**:
   ```bash
   git add segmind/__init__.py CHANGELOG.md
   git commit -m "Bump version to X.Y.Z"
   git push origin main
   ```

### 2. Test with TestPyPI (Recommended)

Before publishing to production PyPI, test the release on TestPyPI:

1. **Trigger manual workflow**:
   - Go to GitHub Actions → "Publish to PyPI" workflow
   - Click "Run workflow"
   - Select branch: `main`
   - Select environment: `testpypi`
   - Click "Run workflow"

2. **Monitor workflow**:
   - Wait for all jobs to complete
   - Check that tests pass
   - Verify build succeeds
   - Confirm publication to TestPyPI

3. **Verify on TestPyPI**:
   - Visit: https://test.pypi.org/project/segmind/
   - Check version number
   - Verify README renders correctly
   - Check metadata (links, description, etc.)

4. **Test installation from TestPyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ segmind
   ```
   Note: `--extra-index-url` is needed for dependencies that aren't on TestPyPI

5. **Test the installed package**:
   ```python
   import segmind
   print(segmind.__version__)

   # Test basic functionality
   client = segmind.SegmindClient(api_key="test")
   ```

### 3. Create Production Release

Once testing is complete:

1. **Create a Git tag**:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

2. **Create GitHub Release**:
   - Go to GitHub repository → Releases → "Draft a new release"
   - Choose tag: `v0.1.0` (the tag you just created)
   - Release title: `v0.1.0` or `Version 0.1.0`
   - Description: Copy relevant sections from CHANGELOG.md
   - Click "Publish release"

3. **Automatic publishing**:
   - Creating the release automatically triggers the publishing workflow
   - The workflow will:
     - Run all tests
     - Run linting checks
     - Build the package
     - Publish to PyPI

4. **Monitor the workflow**:
   - Go to GitHub Actions
   - Watch the "Publish to PyPI" workflow
   - Ensure all jobs complete successfully

5. **Verify on PyPI**:
   - Visit: https://pypi.org/project/segmind/
   - Check the new version is live
   - Verify README and metadata

6. **Test installation**:
   ```bash
   pip install --upgrade segmind
   python -c "import segmind; print(segmind.__version__)"
   ```

## Emergency Release Process

If you need to publish immediately without creating a GitHub Release:

1. **Trigger manual workflow**:
   - Go to GitHub Actions → "Publish to PyPI" workflow
   - Click "Run workflow"
   - Select branch: `main`
   - Select environment: `pypi`
   - Click "Run workflow"

⚠️ **Warning**: This bypasses the normal release process. Use only in emergencies.

## Troubleshooting

### Workflow fails on pre-publish checks

**Problem**: Tests or linting fail during the workflow.

**Solution**:
1. Check the workflow logs to identify failing tests/checks
2. Fix the issues locally
3. Run tests and linting locally to verify fixes
4. Commit and push fixes
5. Retry the release process

### Package already exists on PyPI with same version

**Problem**: Cannot publish because version already exists.

**Solution**:
1. You cannot replace an existing version on PyPI
2. Bump the version number in `segmind/__init__.py`
3. Commit and push
4. Retry the release with the new version

### Trusted Publisher authentication fails

**Problem**: Workflow fails with authentication error.

**Solution**:
1. Verify Trusted Publisher is configured correctly on PyPI
2. Check that:
   - Repository name matches exactly
   - Workflow filename is correct (`publish.yml`)
   - Environment name matches (`pypi` or `testpypi`)
3. If Trusted Publisher isn't configured, use API tokens instead:
   - Add `PYPI_API_TOKEN` to GitHub secrets
   - Modify workflow to use token authentication

### README doesn't render on PyPI

**Problem**: README shows as plain text or has rendering errors.

**Solution**:
1. Ensure README.md uses standard markdown (avoid GitHub-specific syntax)
2. Run `twine check dist/*` locally to validate
3. Test on TestPyPI first to preview rendering

## Setting Up Trusted Publishers

### For PyPI (Production)

1. Go to https://pypi.org/manage/account/publishing/
2. Scroll to "Add a new pending publisher"
3. Fill in:
   - **PyPI Project Name**: `segmind`
   - **Owner**: `segmind` (GitHub organization)
   - **Repository name**: `segmind-python`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
4. Click "Add"

### For TestPyPI (Testing)

1. Go to https://test.pypi.org/manage/account/publishing/
2. Scroll to "Add a new pending publisher"
3. Fill in the same details as above (but use `testpypi` as environment name)
4. Click "Add"

Note: You may need to publish once using API tokens before you can configure Trusted Publishers for an existing project.

## Alternative: Using API Tokens

If Trusted Publishers aren't available:

1. **Generate PyPI API Token**:
   - Go to https://pypi.org/manage/account/token/
   - Create token scoped to "segmind" project
   - Copy the token (starts with `pypi-`)

2. **Add to GitHub Secrets**:
   - Go to GitHub repository → Settings → Secrets and variables → Actions
   - Add secret: `PYPI_API_TOKEN` with the token value
   - Repeat for TestPyPI token: `TEST_PYPI_API_TOKEN`

3. **Update workflow** to use tokens instead of Trusted Publishers (modify the publish jobs)

## Best Practices

1. **Always test on TestPyPI first** before production releases
2. **Keep CHANGELOG.md updated** with all changes
3. **Follow semantic versioning** strictly
4. **Run tests locally** before creating releases
5. **Create meaningful release notes** in GitHub Releases
6. **Announce releases** to users (if applicable)
7. **Monitor PyPI download stats** to track adoption

## Resources

- [PyPI](https://pypi.org/project/segmind/)
- [TestPyPI](https://test.pypi.org/project/segmind/)
- [Semantic Versioning](https://semver.org/)
- [Python Packaging Guide](https://packaging.python.org/)
- [GitHub Actions](https://github.com/segmind/segmind-python/actions)
