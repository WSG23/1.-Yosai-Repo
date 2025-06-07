# Migration Guide

This short guide summarizes the changes made during the UI refactor.
Use it when upgrading older Yosai deployments to the current layout.

- Review the new `ui/` directory for component locations.
- Update callback registration to use `UploadHandlers`.
- Styles are now centralized in `ui/themes/style_config.py` as dictionaries like `UPLOAD_STYLES`.

