Tailwind integration notes and quick start

What I changed
- Replaced the large inline stylesheet in `apps/invitations/templates/invitations/invite_detail.html` with Tailwind utility classes.
- Added a Tailwind build config and minimal PostCSS config:
  - `tailwind.config.js`
  - `postcss.config.js`
  - `package.json` (scripts: `build:css`, `watch:css`)
- Added a placeholder `static/css/tailwind.css` so Django doesn't 404 while you haven't built the real file yet.
- Added a CDN fallback (`<script src="https://cdn.tailwindcss.com"></script>`) so the page already gets Tailwind utilities in development even if you can't run `npm` locally.
- Added a safelist in `tailwind.config.js` for classes toggled by JS.

Why you still need to build Tailwind
- The project includes a placeholder `static/css/tailwind.css` file. To generate a proper, production-ready Tailwind build (purged and minified), you must run the build pipeline locally (Node.js + npm).

Prerequisites
- Node.js + npm installed (recommended: Node 18+ or LTS). If not installed, get the Windows installer from https://nodejs.org/

Commands (Windows `cmd.exe`) — one-time install
1) Install packages (run from project root):

```
npm install
```

2) Build the Tailwind CSS (single build):

```
npm run build:css
```

3) Or run a watch during development (rebuilds on file changes):

```
npm run watch:css
```

What the build does
- Input: `src/styles/tailwind-input.css` (this file imports Tailwind's base/components/utilities). The npm script runs `npx tailwindcss -i ./src/styles/tailwind-input.css -o ./static/css/tailwind.css --minify` which produces `static/css/tailwind.css`.
- The template links to `{% static 'css/tailwind.css' %}`. If you don't build, the page will still have classes available via CDN fallback added to the template.

Testing locally
- Start Django dev server:
```
python manage.py runserver
```
- Open a browser to a sample invite detail page (e.g. `http://127.0.0.1:8000/invitations/detail/<token>/`).
- If you want to confirm the real Tailwind file is being used, view `http://127.0.0.1:8000/static/css/tailwind.css` and confirm it contains compiled CSS and not just the placeholder comment.

Notes and next steps I can do for you
- Remove any leftover inline styles and tiny custom CSS (I already left a couple tiny fallbacks). I can sweep the template to finish the conversion.
- Add a dedicated entrypoint CSS `src/styles/tailwind-input.css` if you prefer a different setup (I created it already).
- Add a README or npm setup script for Windows with nvm-windows instructions if you need help installing Node.
- Optimize safelist if you find specific dynamic classes missing after purge.

If you want, I can now:
- 1) Create the missing `src/styles/tailwind-input.css` file (if not present) and ensure it's configured correctly (I already created it), and update `package.json` if you want different scripts.
- 2) Remove the CDN fallback and rely only on the built CSS (after you confirm `npm install` is available), or leave the CDN for convenience.

Tell me which of the above you want me to do next (e.g. create/adjust files, remove CDN fallback, or keep as-is). If you prefer, I can provide step-by-step help to install Node on your machine and run the build commands yourself.
