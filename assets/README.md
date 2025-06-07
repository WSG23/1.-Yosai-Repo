# Yosai Bootstrap

# Phase 1 Migration Guide: Upload Component Refactor

## Overview
This phase extracts the upload functionality into a centralized UI component system. The upload component and its handlers are now separated from the main layout and callback files.

## Installation

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install the required packages. Use the production requirements for normal use or the development list for contributing and running tests:

```bash
pip install -r requirements-prod.txt  # Production
pip install -r requirements-dev.txt   # Development
```

## Steps to Implement

### 1. Create New Directory Structure
```bash
mkdir -p ui/components ui/handlers ui/utils
touch ui/__init__.py ui/components/__init__.py ui/handlers/__init__.py ui/utils/__init__.py
```

### 2. Create New Files

#### A. Upload Component
- Create `ui/components/upload.py` with the `UploadComponent` class
- This centralizes all upload-related UI definitions

#### B. Upload Handlers
- Create `ui/handlers/upload_handlers.py` with the `UploadHandlers` class
- This contains all upload callback logic

#### C. Package Init Files
- Create all `__init__.py` files to make packages importable

### 3. Update Existing Files

#### A. Replace `layout/core_layout.py`
- Update the layout to use the new upload component
- Remove upload-specific code, import from ui.components instead

#### B. Update `app.py`
- Import new UI components and handlers
- Update callback registration to use new system
- Remove old upload callback registration

#### C. Keep `callbacks/upload_callbacks.py` (temporarily)
- Comment out or remove the old upload handler
- Keep file for reference during transition

### 4. Test the Migration

#### A. Verify Functionality
1. Upload should work exactly as before
2. All styling should be preserved
3. All callbacks should function normally

#### B. Check for Issues
- Import errors
- Missing dependencies
- Callback conflicts

### 5. Benefits Achieved

#### ✅ Separation of Concerns
- UI definition separate from business logic
- Upload logic centralized in one place

#### ✅ Reusability
- Upload component can be reused in different contexts
- Consistent styling and behavior

#### ✅ Maintainability
- Single place to modify upload appearance
- Clear component boundaries

## File Changes Summary

### New Files Created:
```
ui/
├── __init__.py
├── components/
│   ├── __init__.py
│   └── upload.py          # NEW: Upload component class
├── handlers/
│   ├── __init__.py
│   └── upload_handlers.py # NEW: Upload callback handlers
└── utils/
    └── __init__.py
```

### Modified Files:
- `app.py` - Updated to use new UI system
- `layout/core_layout.py` - Uses new upload component

### Unchanged Files (for now):
- `callbacks/mapping_callbacks.py`
- `callbacks/graph_callbacks.py`
- All `processing/` files
- All `styles/` files

## Testing Checklist

- [ ] Upload area displays correctly
- [ ] Upload icon changes on success/failure
- [ ] CSV processing works as before
- [ ] Column mapping appears after upload
- [ ] Error handling works properly
- [ ] Status messages display correctly
- [ ] All subsequent steps work normally

## Running Tests

Install the development requirements before running the test suite:

```bash
pip install -r requirements-dev.txt
pytest
```

The tests rely on packages such as `pandas` which are included in
`requirements-dev.txt`.

## Next Phase Preview

**Phase 2** will extract:
- Mapping components (`ui/components/mapping.py`)
- Classification components (`ui/components/classification.py`)
- Stats components (`ui/components/stats.py`)

**Phase 3** will extract:
- Graph components (`ui/components/graph.py`)
- Centralized callback registration system
- Shared state management utilities

## Rollback Plan

If issues occur:
1. Restore original `app.py`
2. Restore original `layout/core_layout.py`
3. Uncomment original upload callbacks
4. Remove new `ui/` directory

The migration is designed to be backward-compatible and easily reversible.

## Questions & Support

Common issues and solutions:

**Import Errors**: Check that all `__init__.py` files are created and paths are correct

**Callback Conflicts**: Ensure old upload callbacks are removed/commented out

**Styling Issues**: Verify all style imports are preserved in new components
**Centralized Styles**: Use constants from `ui/themes/style_config.py` like `UPLOAD_STYLES` and `MAPPING_STYLES` instead of inline dicts

**Missing Icons**: Check that asset paths are correctly passed to components
**Missing Icons**: Check that asset paths are correctly passed to components

## Additional Documentation
- [Migration Guide](MIGRATION_GUIDE.md)
- [API Overview](docs/api.md)
- [Deployment Notes](docs/deployment.md)
- [Security Practices](docs/security.md)
- [Troubleshooting](docs/troubleshooting.md)
