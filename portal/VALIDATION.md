# Local validation — 1 October 2026

Feature branch: `feature/gyanhq-training-portal`, based on
`feature/training-updates-final` at `7170d6260385de7acd380ff24e67b2d501682c33`.

## Completed

| Check | Result |
|---|---|
| Node/SQLite security and behavior tests | 27 passing |
| Chrome portal browser checks | 20 passing |
| Real local Cloudflare Worker + D1 + static assets | 8 passing |
| Existing GyanHQ registration backend suite | 17 passing |
| GyanHQ desktop/mobile integration checks | 50 passing |
| D1 migration in Wrangler local emulator | Applied successfully |
| Worker dry-run packaging | Pass; approximately 180 KiB before compression |
| Four-hour, 50-learner functional workload | 12,050 requests, zero failures; 200 active hours recorded |
| Portal build using committed baseline | Pass; 159 pages, 45 modules; below free static-asset size/count limits |
| Existing public Docusaurus profile | Passed before the subsequent concurrent document edits described below |

Browser checks include Google-login entry, admin approval, initially locked
modules, separate lesson/solution release, denied solution HTML and JS, Mermaid
rendering, code blocks, mobile layout, activity reports, CSV download, and session
revocation. Google token tests verify actual RSA signatures and rejection of
invalid issuer/audience/nonce/expiry/email-verification claims. The browser tests
seed synthetic accounts only in a disposable database; they do not bypass Google
authentication in the deployed Worker.

## Concurrent course editing

The first successful portal build used the working-tree snapshot (165 pages,
47 modules). The public profile also built successfully. While Gemini continued
editing teaching content, `training/module13_5-firestore-persistence/lab.md`
became invalid MDX: Acorn reports a parse error at line 406, around the raw
`session_ref.update({"state": session.state})` expression amid interrupted code
blocks. That document has not been repaired or reverted by this feature work.

Final reproducible portal checks use:

```sh
PORTAL_CONTENT_REF=7170d62 npm run build
```

This is an explicit test snapshot, not an automatic fallback. Normal
`npm run build` still reads the current working tree and must pass after the
in-progress course edits are complete before publishing those edits. New draft
modules present only in the working tree are not in the committed test snapshot.

At the user's request, only the older duplicate YAML title fields in Module 14's
playbook and solution were removed, preserving their newer Governance titles.
Those changes remain with the user's existing uncommitted teaching edits; they
are not included in the feature-only commit.

Pre-existing documentation warnings include Module 24's external lab Markdown
link and its `evaluating-trajectory-and-tool-use` anchor. This feature does not
rewrite the concurrently edited lessons to address those warnings.

## Live checks still required

No Cloudflare resources, OAuth clients, production routes, or website deployments
were created or changed. The administrator email, Google OAuth credentials,
staging origin, and separate Cloudflare D1 IDs are intentionally unset.

Before production, complete real Google login in staging, learner approval and
revocation, release controls, alternate-host denial, and real account quota/CPU
checks. Local workload timing is Node/SQLite wall time, not Cloudflare edge CPU or
D1 billed row usage. The new GitHub Actions validation workflow is prepared but
has not run remotely.

Generated evidence is gitignored: `generated/build-info.json`,
`generated/capacity.json`, and `generated/browser/`. The GyanHQ integration patch
is preserved in `integration/gyanhq.patch`; its temporary clone was inspected and
tested without a push or deployment.
