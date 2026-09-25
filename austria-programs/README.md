# Magyar Programok Ausztriában — national directory MVP

Feature branch: `feature/austria-hungarian-program-platform-20260925`

## What is merged conceptually from the three existing systems

- **okoszisztema** → evidence-first entity model, source hierarchy, AI/LLM trust rules.
- **BMIPROGRAM** → searchable program UX, location-aware event fields, privacy-conscious route links.
- **BMITANAROK** → profile-card pattern and human-readable professional/introduction profiles.

The new layer has its own neutral Austria-wide data model; it does not make BMI-specific assumptions.

## Data model

`data/organizations.json` contains:
- organization identity
- federal state and city
- type
- human-readable introduction
- website/social channels
- primary event surfaces

`data/events.json` contains:
- event + organizer relation
- start/end date
- federal state / city
- venue and address when verified
- source URL
- verification timestamp for automatically discovered records

## Daily curator

`.github/workflows/austria-hungarian-program-curator.yml` runs daily and invokes `scripts/update_events.py`.

The first adapter reads Schema.org Event JSON-LD. Sources without machine-readable event data are logged in `data/source-health.json` and are **not guessed**. Next adapters should cover ICS/RSS, WordPress REST/The Events Calendar, Wix event JSON and selected static pages.

## Next production steps

1. complete event-source discovery for every organization;
2. add source-specific adapters where structured data is absent;
3. generate static SEO organization routes from the registry;
4. add sitemap/robots/canonical once production domain is chosen;
5. visual regression + WCAG + Lighthouse;
6. deploy only after source and privacy review.
