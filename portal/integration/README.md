# GyanHQ website patch

`gyanhq.patch` applies to `inderanz/gyanhq` main at `844cf75`, inspected in
`/private/tmp/gyanhq-review.w4sQax/gyanhq`. It adds the shared navigation link and
portal-specific privacy text. The clone has these changes for local review.

Apply in a new GyanHQ feature branch, following that repository's approved
specification workflow. The user's portal implementation request approves this
integration scope. Do not merge or deploy it until the protected training route
has passed staging verification.

```sh
git apply --check /path/to/google-adk-training/portal/integration/gyanhq.patch
git apply /path/to/google-adk-training/portal/integration/gyanhq.patch
node --test tests/super30-invite.test.mjs
```

The patch does not modify existing Functions, KV bindings, registration, email
delivery, blog interaction code, DNS, or Cloudflare project settings. Cloudflare
Worker routes are configured in the training project's production profile.
Pages' existing `_headers` do not automatically apply to Worker responses; the
training Worker supplies its own security and no-store headers.
