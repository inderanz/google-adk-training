# GyanHQ training portal

Implementation specification approved by the user's implementation request.

The portal runs separately from GyanHQ Pages and the existing public training
site. Google OIDC establishes identity; a D1 allowlist grants portal access.
Only the configured administrator manages approvals, global lesson releases,
separate solution releases, and 90-day learner reports. Everything starts locked.
The public GitHub copies remain public by explicit choice.

Security boundary: the Worker runs before every asset. A build-generated manifest
classifies rendered pages and content-bearing JavaScript by module and solution.
Mixed-permission content chunks fail compilation. Browser navigation uses full
document requests, avoiding speculative loading across permission boundaries.
Unknown assets, failed database checks, invalid sessions, and unknown hosts deny
access. Authentication never falls back to anonymous asset serving.

Existing Markdown and the default Docusaurus/GitHub Pages configuration are not
rewritten. Portal builds use a separate config and a temporary content snapshot.
GyanHQ integration is supplied as a reviewable patch against the inspected clone.

Validation covers authorization, generated content, OAuth, activity, expiry,
retention, migration behavior, two build profiles, and local Worker execution.
Live OAuth, edge CPU, account quotas, and staging/production validation require
the owner's deployment configuration; no production activation is implicit in
local implementation.
