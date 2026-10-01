# GyanHQ training portal

Separate Cloudflare Worker + D1 deployment of the existing Docusaurus course.
No Firebase. The original public site and course source remain available.
The initial portal and training updates were merged into `main` in PR #1.
The responsive interface update is on `feature/portal-cloud-ui`.

## Local development

Use Node 24 (the existing documentation workflow also uses Node 24).

```sh
cd doc
npm ci
cd ../portal
npm ci
npm run build
npm test
npx wrangler d1 migrations apply gyanhq-training-local --local --env local
npm run dev
```

Visit `http://localhost:8787/adk-training/`. A development server is not an auth
bypass: Google sign-in needs the local OAuth configuration below. Automated
browser tests seed sessions only in their own in-memory database, never in the
deployed Worker. `npm run test:browser` runs against this disposable test server.
Install Chrome locally or install Playwright Chromium with `npx playwright install chromium`.
Set `PLAYWRIGHT_CHANNEL=chromium` when using Playwright's bundled Chromium.

The portal uses a Google Cloud-inspired light interface with GyanHQ branding.
Signed-in visitors get a workspace shortcut; catalogue search and availability
filters do not change access permissions. The portal-only lesson stylesheet
keeps tables and code scrollable within the reading column and preserves the
existing public site's theme.

Browser checks cover the landing page, catalogue, administration, lessons, and
diagrams at 320, 390, 768, 1024, 1440, and 1920 pixels. To also inspect every
generated course page for overflow at phone and laptop widths, run:

```sh
FULL_RESPONSIVE=1 npm run test:browser
```

Screenshots are written to `portal/generated/browser/` (gitignored). After
rebuilding while Wrangler is running, restart `npm run dev` so its static-asset
manifest picks up the complete new build.

Builds copy current `training/` and root overview documents into
`portal/generated/training/`; they never rewrite teaching source. The selected
config is `doc/docusaurus.portal.config.js`. The public `doc` profile is unchanged.
Portal code generation also uses `portal/generated/docusaurus/`, keeping the
public build's `doc/.docusaurus/` metadata separate.

When another editor is changing the course, you can explicitly validate against
committed content without touching that editor's files:

```sh
PORTAL_CONTENT_REF=feature/training-updates-final npm run build
```

The default always uses the current working tree and never silently substitutes
older content. `generated/build-info.json` records which source was used.
Resolve any current Markdown/MDX build errors before deploying updated lessons.

## Architecture and access rules

- Worker first for every path, including JS, HTML, downloads, and assets.
- Public landing and portal UI assets contain no lessons. All course assets
  require a valid session and, where applicable, a released module/solution.
- Build metadata maps rendered pages and webpack content chunks to permissions;
  mixed-permission chunks and unclassified output fail the build. The manifest
  is bundled into the Worker, not served as a public static endpoint.
- Full document navigation replaces speculative prefetch/client routing. This
  intentionally adds page requests in exchange for straightforward access checks.
- Sessions last 12 hours. Only token hashes are stored in D1. Google `sub` is the
  stable identity; approval emails are normalized without Gmail dot/plus alias
  rewriting and bound to one Google identity on first approved login.
- Exact `ADMIN_EMAIL` is the sole administrator. It bypasses learner release
  rules. Changing it removes admin rights from the old email on its next request.
- Everything starts locked. Releasing lessons also includes playbooks. Solutions
  have a second control. Relocking lessons clears solution release. New modules
  are locked automatically; no database reseed is needed after content updates.
- Activity records are per visit, updated cumulatively about once per minute.
  The browser coordinates focused tabs using Web Locks with a short localStorage
  lease fallback. Lease values contain random tab IDs, not authentication data.
  Timing pauses for hidden/unfocused/idle tabs; it is approximate and client
  reported. It does not establish reading, completion, or integrity of attendance.
- Revocation blocks later requests, but cannot retract previously read/saved
  content. Public GitHub resources remain independently accessible by choice.

## Google configuration

Create a Google OAuth **Web application** client. Configure an external consent
screen supporting the intended Gmail/Workspace learners and request only
`openid email profile`. Finish any Google publishing requirements before inviting
learners outside the consent screen's test-user list. No Gmail API permissions
are requested. Use different clients for staging and production.

Register exact redirect URIs:

- Local: `http://localhost:8787/adk-training/auth/callback`
- Staging: `https://gyanhq-training-staging.<your-subdomain>.workers.dev/adk-training/auth/callback`
- Production: `https://gyanhq.com/adk-training/auth/callback`

For local use create gitignored `portal/.dev.vars.local` with `GOOGLE_CLIENT_ID`
and `GOOGLE_CLIENT_SECRET`. Set your administrator email in the local vars in
`wrangler.jsonc`. Do not commit credentials or paste them into chat.

For staging/production use Wrangler secrets (commands prompt securely):

```sh
npx wrangler secret put GOOGLE_CLIENT_ID --env staging
npx wrangler secret put GOOGLE_CLIENT_SECRET --env staging
```

Repeat with `--env production` using the production client. The Worker validates
state, nonce, PKCE, issuer, audience, signature, expiry, and verified email. A
Google account still needs your manual approval. Server sessions never store
Google access/refresh tokens.

## Staging and production

No deployment is performed by the build or test commands. Do not enable paid
plans to run this portal. Check the account is using the intended Workers plan
and inspect existing account usage first: quotas are shared with other apps.

1. Create separate D1 databases with `npx wrangler d1 create gyanhq-training-staging`
   and, after staging validation, `npx wrangler d1 create gyanhq-training`.
2. Replace the respective database ID placeholders in `wrangler.jsonc`. Set the
   staging `ORIGIN` to its exact Workers hostname and set each `ADMIN_EMAIL`.
   Keep production `workers_dev` and preview URLs disabled.
3. Install the corresponding Google secrets and callback configuration.
4. Apply migrations with
   `npx wrangler d1 migrations apply gyanhq-training-staging --remote --env staging`.
5. Build, run tests, run `npm run check`, then `npm run deploy:staging`.
6. In staging, sign in as admin, approve a real test learner, test locked lessons
   and solutions, release them separately, inspect activity, export CSV, revoke
   access, and confirm old sessions fail. Test on mobile and desktop.
7. Inspect actual Workers CPU/request metrics and D1 read/write/storage metrics
   in Cloudflare. Local wall time is not edge CPU. Validate the free 10 ms CPU
   budget, especially cold OAuth key verification and D1 report serialization.
8. Only after successful staging: apply production migrations, deploy the
   production profile, and merge/deploy the GyanHQ integration patch. The
   production routes match exactly `/adk-training` and `/adk-training/*`.

`wrangler.jsonc` intentionally contains nonfunctional setup placeholders.
Never replace them with production values for local/browser tests. No account
quota, successful Google login, or production availability is claimed by local
tests. The `www` host is not a second training origin; link to canonical
`https://gyanhq.com/adk-training/`.

## Reports, retention, and operating limits

Admin report filters: learner email, exact page path, inclusive UTC date range.
Results use 100-visit pages. CSV exports are capped at 10,000 visits; narrow the
filters for a larger history. CSV formula prefixes are escaped. Only the admin
can view/export/delete activity. Deleting activity preserves access approval.

The daily 03:20 UTC cron deletes expired activity/audit data older than 90 days,
expired sessions, and expired OAuth attempts in bounded batches of 5,000 rows
per table. At the target cohort size this exceeds normal daily visit creation;
after a prolonged outage, run cleanup repeatedly until the backlog clears.
Removing approval does not itself delete identity or historical visit records.
Requested full account deletion is an operator task: revoke access, delete
activity, then remove the relevant approval/identity record after confirming
all sessions are gone. Do not delete release settings.

Capacity example: 50 learners × 4 hours × 60 minute updates ≈ 12,000 tracking
requests/day, plus page/asset requests, logins, and administration. Tracking
normally performs one release-table read and one indexed visit upsert per
update, as well as indexed session/approval lookups. SQLite index maintenance
adds written rows; measure real D1 metrics rather than equating requests to rows.
Five-minute idle detection is a heuristic and cannot distinguish quiet reading
from someone leaving a visible page unattended.

Free-tier quota exhaustion causes errors, not public access. Tracking failure
does not prevent an already authorized page from rendering; inability to verify
authorization blocks new content requests. Watch Worker errors and D1 metrics.
The application logs only generic failure names, never OAuth codes/tokens or
learner email addresses. Access and release mutations are recorded in `audit`.

## Rollback

Record the previous Worker deployment/version ID and GyanHQ Pages deployment
before activation. Roll back the Worker version and website patch if needed;
leave additive D1 tables and approval/release data intact. For a first launch,
remove only the two training Worker routes and the website training link to
restore the former routing. This does not affect GyanHQ registration/blog APIs.
Do not make the protected asset directory a public Pages deployment as a fallback.

See `VALIDATION.md` for completed checks and remaining live setup requirements.
