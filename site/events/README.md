# Event images

Public nights are built from this folder plus `events.json`. Exact add/update steps: [README.md](../../README.md#adding-or-updating-an-event).

```
<id>/poster.png     lead poster (required to show a picture)
<id>/recap/         recap photos, named 01-, 02-, …
<id>/posters/       extra 11×17 variants for Media
```

After dropping files, update the one object in `events.json`, then:

```bash
node scripts/optimize-event-images.mjs
node scripts/build-site.mjs
```
