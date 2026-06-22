Changelog
=========


1.2.1 (unreleased)
------------------

- Fix IStoredFile's file field name [cadam, gyst]


1.2.0 (2026-06-17)
------------------

NB: this release was refused by PyPi (requires collective_collabora) - it's only available via pypi.quaive.net.

- Reset File object actions on uninstall [gyst]

- Propagate UI language setting to Collabora [gyst]

- Update Github CI infrastructure [gyst]


1.1.0 (2025-07-25)
------------------

- Make it easier to provide custom IStoredField adapters for varying file field names. [gyst]


1.0.1 (2025-04-18)
------------------

- Fix documentation URL in setup.py [gyst]


1.0.0 (2025-04-18)
------------------

- Cleanup unused code [thet]

- Add translations [macagua, gyst]

- Extract documentation to readthedocs [gyst]

- Configure build tooling [gyst]

- Remove unneeded CORS headers [gyst]

- Let Collabora handle locking conflicts [gyst]

- Increase log level on file writes, and document that Collabora
  always saves changes, even on browser exit. [gyst]

- Disable CSRF protection, after exhausting all other options. [gyst]


0.9.0 (2025-04-10)
------------------

- Initial release. [gyst, ale-rt]
