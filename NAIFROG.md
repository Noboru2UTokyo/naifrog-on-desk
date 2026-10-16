# Naifrog distribution maintenance

## Baseline

- Upstream: rullerzhou-afk/clawd-on-desk, v1.3.0 (54d359ef).
- Distribution branch: codex/naifrog-edition. Keep main available for upstream synchronization.
- Package/bundle: naifrog-on-desk / io.github.noboru2utokyo.naifrog-on-desk.
- Application and theme versions: 1.3.1.
- The first-run preference is naifrog. Existing selected themes are preserved.
- Published assets and updater endpoints belong only to Noboru2UTokyo/naifrog-on-desk.
- Internal upstream hook markers and ~/.clawd are intentionally retained. Run only one edition at a time.
- The application does not register clawd://; Settings import remains available.

## Release scope and checks

The initial target is macOS Apple Silicon. No Apple Developer ID identity was available on the build host. This is an explicitly ad-hoc, unnotarized community build, not an upstream official release. Never describe it as notarized or as passing Gatekeeper distribution assessment. When a maintainer supplies Developer ID/notarization credentials, use the upstream signing guide and verify the downloaded, quarantined DMG before changing that claim.

The inherited upstream tag and WinGet publishing pipelines are repository-gated. Do not submit this distribution as upstream Clawd or reuse its Windows package identifier. A separate manual Naifrog workflow builds artifacts without publishing them; publish only reviewed packages from this fork.

Required for this fork: release version/contributor checks, full Node suite, strict Naifrog theme validation, repository asset audit, packaged native inventory, packaged Koffi positive-call smoke, Naifrog package contents/default/identity verification, DMG mounting and signature integrity. Record unavailable GUI/platform/update-pair checks as not tested. Upstream's release-v1.3.0 checklist remains historical coverage for that upstream release; this fork does not claim to rerun every external agent matrix.

The fork asset budget is explicitly raised from 64 MiB to 105 MiB (warning at 90 MiB) to include the 32.5 MiB approved theme; all upstream ownership and native-package audit rules remain enabled. No raw source recordings, generation requests, API keys, or local paths should be published. Application icon is an unchanged copy of the approved idle poster, retained in assets/source/naifrog.

## Repeat a release

1. Fetch upstream and review the next stable tag before merging into the distribution branch.
2. Reapply and test only the distribution identity, defaults, updater, theme and documentation changes. Keep upstream code/credits/licenses.
3. Update package.json, package-lock.json, the theme when needed, and docs/releases/release-vVERSION.md. Add the release note to .gitignore's allowlist.
4. Run npm ci, npm test, npm run verify:release, node scripts/validate-theme.js themes/naifrog, and npm run audit:assets after committing the audited tree.
5. Build with npm run build:mac:arm64 -- --publish never. Run packaged checks documented in the release report.
6. Create a draft Release at the exact commit; attach DMG, ZIP, SHA256SUMS.txt and verification evidence. Publish only after inspection. Keep the signing limitation visible until resolved.

## Dependency patch maintenance

The initial fork also updates markdown-it to 15.0.3 and the lockfile resolutions for js-yaml to 4.3.2 and qs to 6.16.1. These compatible fixes address the production dependency audit findings in GHSA-253c-mchw-3w2r, GHSA-2883-xcg3-v3hh and GHSA-4mjr-xmp4-gh2g. No forced major-version update is applied.
