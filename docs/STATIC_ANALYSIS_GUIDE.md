# Static Analysis Setup and Usage Guide

## Overview

This document explains the static analysis tools that have been integrated into the ProjectBudgetinator project to improve code quality, type safety, and security.

## Tools Configured

### 1. MyPy - Type Checking
- **Purpose**: Static type checking for Python
- **Configuration**: `mypy.ini` and `pyproject.toml`
- **What it checks**: Type annotations, type consistency, return types
- **Benefits**: Catches type-related bugs before runtime

### 2. Pylint - Code Quality Analysis
- **Purpose**: Comprehensive code quality analysis
- **Configuration**: `.pylintrc` and `pyproject.toml`
- **What it checks**: Code complexity, naming conventions, code smells, refactoring opportunities
- **Benefits**: Improves code maintainability and readability

### 3. Flake8 - Style and Basic Error Checking
- **Purpose**: PEP 8 style enforcement and basic error detection
- **Configuration**: `.flake8` and `pyproject.toml`
- **What it checks**: Code style, line length, unused imports, syntax errors
- **Benefits**: Ensures consistent code style across the project

### 4. Bandit - Security Scanning
- **Purpose**: Security vulnerability detection
- **Configuration**: `.bandit` and `pyproject.toml`
- **What it checks**: Common security issues, hardcoded passwords, SQL injection risks
- **Benefits**: Identifies potential security vulnerabilities

### 5. Black - Code Formatting
- **Purpose**: Automatic code formatting
- **Configuration**: `pyproject.toml`
- **What it does**: Automatically formats code to a consistent style
- **Benefits**: Eliminates formatting debates and ensures consistency

### 6. isort - Import Sorting
- **Purpose**: Automatic import statement organization
- **Configuration**: `pyproject.toml`
- **What it does**: Sorts and organizes import statements
- **Benefits**: Consistent import organization across the project

## How to Run Static Analysis

### Option 1: Run All Tools at Once

#### Using Python Script (Recommended)
```bash
python run_static_analysis.py
```

#### Using Batch File (Windows)
```bash
run_static_analysis.bat
```

#### Using PowerShell (Windows)
```powershell
.\run_static_analysis.ps1
```

### Option 2: Run Individual Tools

#### MyPy Type Checking
```bash
python -m mypy src/ --config-file mypy.ini
```

#### Pylint Code Quality
```bash
python -m pylint src/ --rcfile .pylintrc
```

#### Flake8 Style Check
```bash
python -m flake8 src/ --config .flake8
```

#### Bandit Security Scan
```bash
python -m bandit -r src/ -c .bandit -f txt
```

#### Black Code Formatting (Check)
```bash
python -m black --check --diff src/
```

#### Black Code Formatting (Fix)
```bash
python -m black src/
```

#### isort Import Sorting (Check)
```bash
python -m isort --check-only --diff src/
```

#### isort Import Sorting (Fix)
```bash
python -m isort src/
```

### Option 3: VS Code Tasks

Open VS Code Command Palette (`Ctrl+Shift+P`) and run:
- `Tasks: Run Task` → `Static Analysis - All Tools`
- `Tasks: Run Task` → `Static Analysis - MyPy Type Check`
- `Tasks: Run Task` → `Static Analysis - Pylint Code Quality`
- `Tasks: Run Task` → `Static Analysis - Flake8 Style Check`
- `Tasks: Run Task` → `Static Analysis - Bandit Security Scan`
- `Tasks: Run Task` → `Format Code - Black`
- `Tasks: Run Task` → `Format Code - isort Imports`

## Understanding the Output

### MyPy Output
```
src/main.py:45: error: Function is missing a return type annotation
src/handlers/partner.py:123: error: Argument 1 to "open" has incompatible type "Optional[str]"; expected "Union[str, bytes, int, PathLike[str], PathLike[bytes]]"
```

**How to fix**: Add type annotations to your functions and variables.

### Pylint Output
```
src/main.py:15:0: C0103: Variable name "df" doesn't conform to snake_case naming style (invalid-name)
src/handlers/partner.py:45:0: R0913: Too many arguments (6/5) (too-many-arguments)
```

**How to fix**: Follow the recommendations to improve code quality.

### Flake8 Output
```
src/main.py:78:80: E501 line too long (89 > 79 characters)
src/handlers/partner.py:12:1: F401 'os' imported but unused
```

**How to fix**: Shorten long lines and remove unused imports.

### Bandit Output
```
>> Issue: [B108:hardcoded_tmp_directory] Probable insecure usage of temp file/directory.
   Severity: Medium   Confidence: Medium
   Location: src/utils/file_handler.py:45
```

**How to fix**: Review security issues and implement secure alternatives.

## Configuration Files

### `pyproject.toml`
- Main configuration file for all tools
- Contains tool-specific settings
- Preferred modern approach

### Tool-specific Configuration Files
- `mypy.ini` - MyPy configuration
- `.pylintrc` - Pylint configuration  
- `.flake8` - Flake8 configuration
- `.bandit` - Bandit configuration

## Best Practices

### 1. Run Before Committing
Always run static analysis before committing code:
```bash
python run_static_analysis.py
```

### 2. Fix Formatting Issues First
Run Black and isort to fix formatting:
```bash
python -m black src/
python -m isort src/
```

### 3. Address Type Issues Gradually
Start by adding type annotations to new code, then gradually add them to existing code.

### 4. Review Security Issues Carefully
Don't ignore Bandit warnings - review each one and implement secure alternatives.

### 5. Configure Your IDE
Set up your IDE to run these tools automatically:
- Enable format on save for Black
- Enable MyPy checking in real-time
- Show Flake8 warnings inline

## CI/CD Integration

Add static analysis to your continuous integration pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run Static Analysis
  run: |
    pip install -r requirements.txt
    python run_static_analysis.py
```

## Troubleshooting

### Common Issues

#### "Module not found" errors in MyPy
- Install missing type stubs: `pip install types-<package>`
- Add `ignore_missing_imports = True` for the package in `mypy.ini`

#### Pylint false positives
- Disable specific warnings with `# pylint: disable=warning-name`
- Adjust settings in `.pylintrc`

#### Black and other tools conflict
- Black is the source of truth for formatting
- Adjust other tools to be compatible with Black

#### Performance issues
- Exclude large directories in configuration files
- Use `--jobs` parameter for parallel processing

### Getting Help

1. Check tool documentation:
   - [MyPy](https://mypy.readthedocs.io/)
   - [Pylint](https://pylint.readthedocs.io/)
   - [Flake8](https://flake8.pycqa.org/)
   - [Bandit](https://bandit.readthedocs.io/)
   - [Black](https://black.readthedocs.io/)
   - [isort](https://pycqa.github.io/isort/)

2. Check the configuration files for project-specific settings

3. Review the output carefully - most issues have clear explanations

## Integration with Development Workflow

### Pre-commit Hook (Recommended)
Install pre-commit hooks to run static analysis automatically:

```bash
pip install pre-commit
# Create .pre-commit-config.yaml
pre-commit install
```

### VS Code Extensions (Recommended)
Install these extensions for real-time feedback:
- Python (Microsoft)
- Pylint
- MyPy Type Checker
- Black Formatter
- isort

### Editor Configuration
Configure your editor to:
- Format with Black on save
- Show type checking errors inline
- Highlight style violations
- Run imports sorting on save

## Results and Reporting

### Output Files
- Results are saved to `build/static_analysis_results.json`
- Detailed logs available in terminal output
- HTML reports generated for coverage tools

### Metrics to Track
- Number of type errors (MyPy)
- Code quality score (Pylint)
- Style violations (Flake8)
- Security issues (Bandit)
- Test coverage percentage

### Continuous Improvement
- Set targets for reducing violations
- Track progress over time
- Address most critical issues first
- Gradually improve code quality

## Migration Guide

If you're adding static analysis to an existing project:

1. **Start with formatting tools** (Black, isort)
2. **Add style checking** (Flake8) with relaxed settings
3. **Introduce type checking** (MyPy) gradually
4. **Add code quality checks** (Pylint) with disabled warnings
5. **Enable security scanning** (Bandit)
6. **Gradually tighten settings** as code improves

This phased approach minimizes disruption while improving code quality over time.
