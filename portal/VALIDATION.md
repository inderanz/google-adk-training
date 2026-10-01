# Local validation — 1 October 2026

Feature branch: `feature/gyanhq-training-portal`, based on
`feature/training-updates-final` at `7170d6260385de7acd380ff24e67b2d501682c33`.

## Completed

| Check | Result |
|---|---|
| Node/SQLite security and behavior tests | 27 passing |
| Chrome portal browser checks | 20 passing |
| Real local Cloudflare Worker + D1 + static assets | 8 passing |
| Commercial underwriting and OpenAPI normalizer tests | 10 passing |
| Learner Python source syntax | Pass |
| Existing GyanHQ registration backend suite | 17 passing |
| GyanHQ desktop/mobile integration checks | 50 passing |
| D1 migration in Wrangler local emulator | Applied successfully |
| Worker dry-run packaging | Pass; approximately 180 KiB before compression |
| Four-hour, 50-learner functional workload | 12,050 requests, zero failures; 200 active hours recorded |
| Portal build using committed baseline | Pass; 159 pages, 45 modules; below free static-asset size/count limits |
| Portal build using current working-tree content after MDX repair | Pass; 166 pages, 47 modules, 588 protected paths |
| Existing public Docusaurus profile | Pass after the Module 13.5 MDX repair |

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
blocks.

The Module 13.5 parsing error is now repaired: Python fragments are fenced,
the integration instructions sit outside the Python block, and teacher notes
sit outside the Mermaid diagram. All non-fence lesson lines were preserved.
Both the public build and the default portal build now pass against the current
working tree. The portal build records `working-tree snapshot` in its build info.

The earlier browser and Worker checks used the committed baseline:

```sh
PORTAL_CONTENT_REF=7170d62 npm run build
```

This was an explicit test snapshot, not an automatic fallback. Normal
`npm run build` reads the current working tree, including its new draft modules.
The MDX repair was verified with both build profiles. During preparation of the
combined PR against `main`, both builds, all 27 portal tests, all 20 browser
checks, and all 8 Worker checks passed again against the current content.
The 10 commercial underwriting tests and learner Python syntax checks also pass.
The branch includes the local and remote `feature/training-updates-final` tip
at `7170d6260385de7acd380ff24e67b2d501682c33`.

At the user's request, only the older duplicate YAML title fields in Module 14's
playbook and solution were removed, preserving their newer Governance titles.
Those changes are included with the teaching edits in the combined PR; they
were not included in the original feature-only commit.

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
