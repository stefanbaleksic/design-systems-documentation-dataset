# Comparison of the dataset with the evidence

Offline comparison (`scripts/run_compare_from_evidence.py`). Every record is listed.

## Counts by outcome

| outcome | count |
|---|---|
| fetched | 180 |
| match | 524 |
| mismatch | 16 |
| not_comparable | 139 |
| not_recorded | 177 |
| unavailable | 37 |

## Records with a problem (missing, unavailable or mismatch)

### 11 - Astro UXDS
- repo: **unavailable** - GitHub API: git exit 128: fatal: could not read Username for 'https://github.com': terminal prompts disabled

### 14 - Audi UI Kit
- repo: **unavailable** - GitHub API: git exit 128: fatal: could not read Username for 'https://github.com': terminal prompts disabled
- docs: **unavailable** - HTTP 404

### 25 - Bolt Design System
- repo: **unavailable** - GitHub API: git exit 128: fatal: could not read Username for 'https://github.com': terminal prompts disabled

### 28 - Buildit Gravity
- docs: **unavailable** - refused: not https

### 33 - CBRE Blocks
- docs: **unavailable** - URLError: <urlopen error Tunnel connection failed: 502 Bad Gateway>

### 38 - Co-op Experience Library
- repo: **unavailable** - GitHub API: git exit 128: fatal: could not read Username for 'https://github.com': terminal prompts disabled

### 51 - Financial Times Origami
- repo: **unavailable** - GitHub API: git exit 128: fatal: could not read Username for 'https://github.com': terminal prompts disabled
- docs: **unavailable** - RemoteDisconnected: Remote end closed connection without response

### 54 - Flowbite
- docs: **unavailable** - HTTP 403

### 57 - Foyer Design System
- docs: **unavailable** - RemoteDisconnected: Remote end closed connection without response

### 58 - French Government Design System (DSFR)
- docs: **unavailable** - HTTP 403

### 59 - FutureLearn Pattern Library
- docs: **unavailable** - HTTP 403

### 78 - JetBrains Ring UI
- version: **mismatch** - dataset 1.0.9, no package.json has it (packages: root 7.0.133, packages/rollup-css-plugin/package.json 1.0.0, packages/screenshots/package.json 6.0.0, test-helpers/test-app/package.json 1.0.0)

### 79 - Jobber (Atlantis)
- repo: **unavailable** - GitHub API: git exit 128: fatal: could not read Username for 'https://github.com': terminal prompts disabled

### 85 - Lexicon
- docs: **unavailable** - HTTP 404

### 101 - NationBuilder Radius
- docs: **unavailable** - HTTP 403

### 105 - Nordnet
- docs: **unavailable** - HTTP 403

### 112 - Pivotal
- docs: **unavailable** - URLError: <urlopen error [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] ssl/tls alert handshake failure (_ssl.c:1035)>

### 113 - Pluralsight Design System
- version: **mismatch** - dataset 1.3.1, no package.json has it (packages: root 1.0.0, docs/package.json 0.35.6, docs/src/sandboxes/default/package.json 1.0.0, packages/actionmenu/package.json 18.1.2)
- docs: **unavailable** - RemoteDisconnected: Remote end closed connection without response

### 115 - Priceline Design System
- version: **mismatch** - dataset 5.6.0, no package.json has it (packages: apps/docs/package.json 1.0.0, apps/storybook/package.json 1.0.0, common/autoinstallers/rush-prettier/package.json 1.0.0, heft-plugins/heft-styled-components-plugin/package.json 0.2.1)

### 121 - Salesforce Lightning Design System
- docs: **unavailable** - RemoteDisconnected: Remote end closed connection without response

### 123 - SAP Fiori
- docs: **unavailable** - HTTP 403

### 124 - SAP Fundamental
- docs: **unavailable** - HTTP 403

### 125 - SAP OpenUI5
- docs: **unavailable** - HTTP 403

### 126 - Scania Digital Design System
- repo: **unavailable** - GitHub API: git exit 128: fatal: could not read Username for 'https://github.com': terminal prompts disabled
- docs: **unavailable** - URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1035)>

### 137 - Starbucks Style Guide
- docs: **unavailable** - URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1035)>

### 143 - Twilio Paste
- docs: **unavailable** - HTTP 403

### 150 - U.S. CMS.gov Design System
- licence: **mismatch** - dataset class 'other or custom', evidence MIT (permissive)

### 157 - Welcome UI
- version: **mismatch** - dataset 10.7.5, no package.json has it (packages: lib/package.json 10.7.6, website/package.json 0.1.0)

### 179 - ASU Unity Stack (Arizona State University)
- docs: **unavailable** - HTTP 403

### 180 - UNI Core (uni-design-system)
- docs: **unavailable** - HTTP 403

### 181 - Iowa Design System (UIDS)
- docs: **unavailable** - HTTP 403

### 182 - nulib design-system (Northwestern University Libraries)
- docs: **unavailable** - HTTP 403

### 184 - Chan Zuckerberg Education Design System (EDS)
- docs: **unavailable** - HTTP 403

### 201 - CFT Elephas (Center of Financial Technologies)
- docs: **unavailable** - HTTP 403

### 203 - TDS core legacy v2 (TELUS)
- docs: **unavailable** - URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1035)>

### 204 - Mistica (Telefónica)
- docs: **unavailable** - HTTP 403

### 205 - Polaris (Shopify)
- version: **mismatch** - dataset 10.42.1, no package.json has it (packages: polaris-for-vscode/package.json 1.0.7, polaris-icons/package.json 9.3.1, polaris-migrator/package.json 1.0.7, polaris-react/package.json 13.10.1)

### 210 - Lion (ING)
- version: **mismatch** - dataset 0.11.0, no package.json has it (packages: docs/fundamentals/tools/singleton-manager/example-complex/package.json 1.0.0, docs/fundamentals/tools/singleton-manager/example-fail/package.json 1.0.0, docs/fundamentals/tools/singleton-manager/example-success/package.json 1.0.0, packages-node/astro-lit/package.json 0.1.0)

### 215 - SpareBank 1 Design System
- version: **mismatch** - dataset 1.0.0-alpha.39, no package.json has it (packages: root 1.0.0, buildtool/package.json 102.0.16, examples/DSBanken/package.json 1.0.0, linting/eslint-config-ffe-base/package.json 102.0.16)

### 222 - Lunar (Airbnb)
- docs: **unavailable** - HTTP 403

### 224 - Wonder Blocks (Khan Academy)
- docs: **unavailable** - HTTP 403

### 226 - Utrecht Design System (Municipality of Utrecht)
- version: **mismatch** - dataset 1.0.3, no package.json has it (packages: apps/preact/package.json 1.0.53, components/accordion/package.json 4.1.0, components/action-group/package.json 4.0.1, components/alert-dialog/package.json 3.0.1)

### 230 - Designsystemet (Digdir, Norway)
- version: **mismatch** - dataset 0.13.0, no package.json has it (packages: apps/storybook/package.json 0.1.0, apps/www/package.json 1.24.0, figma/plugin/package.json 1.24.0, figma/ui-kit/package.json 1.24.0)

### 257 - Rivet (Indiana University)
- version: **mismatch** - dataset 1.0.0-alpha.2, no package.json has it (packages: root 2.9.1)

### 261 - Guardian Source (The Guardian)
- version: **mismatch** - dataset 3.13.0, no package.json has it (packages: root 3.12.0, packages/@guardian/eslint-plugin-source-foundations/package.json 8.0.0, packages/@guardian/eslint-plugin-source-react-components/package.json 10.0.0, packages/@guardian/source-foundations/package.json 7.0.1)

### 275 - PrimeNG
- licence: **mismatch** - dataset class 'other or custom', evidence MIT (permissive)

### 277 - Skeleton
- version: **mismatch** - dataset 0.4.1, no package.json has it (packages: packages/cli/package.json 5.0.5, packages/docs/package.json 5.0.5, packages/skeleton-common/package.json 5.0.5, packages/skeleton-react/package.json 5.0.5)

### 278 - Spectrum CSS (Adobe)
- version: **mismatch** - dataset 2.0.0-s2-foundations.0, no package.json has it (packages: .github/actions/file-diff/package.json 2.2.0, .storybook/package.json 12.0.5, components/accordion/package.json 7.2.0, components/actionbar/package.json 10.2.0)

### 285 - Park UI
- version: **mismatch** - dataset 0.20.1, no package.json has it (packages: packages/cli/package.json 1.0.1, packages/preset/package.json 1.0.0)

## All records

| id | name | evidence | findings |
|---|---|---|---|
| 1 | Aalto University | ok | docs=fetched |
| 2 | Adobe Spectrum | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 3 | Adjust Atlas | ok | docs=fetched |
| 4 | Alaska Airlines | ok | last_push=match; archived=not_recorded; licence=not_comparable; version=match; docs=fetched |
| 5 | Ant Design | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 6 | Amplify UI | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded; docs=fetched |
| 7 | Appear Here Styleguide | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded; docs=fetched |
| 8 | Apple Developer Design Guidelines | ok | docs=fetched |
| 9 | Aragon UI | ok | last_push=match; archived=not_comparable; licence=match; version=match; docs=fetched |
| 10 | Artsy Palette | ok | last_push=match; archived=not_comparable; licence=match; version=match; docs=fetched |
| 11 | Astro UXDS | partial | repo=unavailable; docs=fetched |
| 12 | AT UIKIT | ok | last_push=match; archived=not_comparable; licence=match; version=match; docs=fetched |
| 13 | Atlassian Design System | ok | docs=fetched |
| 14 | Audi UI Kit | failed | repo=unavailable; docs=unavailable |
| 15 | Aurora (Government of Canada) | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded; docs=fetched |
| 16 | AutoGuru Overdrive | ok | last_push=match; archived=not_comparable; licence=match; version=match; docs=fetched |
| 17 | AWS Cloudscape Design System | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 18 | Backpack (Skyscanner) | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded; docs=fetched |
| 19 | Basis Design System | ok | last_push=match; archived=not_comparable; licence=match; version=match; docs=fetched |
| 20 | BBC GEL | ok | docs=fetched |
| 21 | Bento DS | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded; docs=fetched |
| 22 | BLiP | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 23 | Blueprint | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 24 | Bold (Bridge Design System) | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 25 | Bolt Design System | partial | repo=unavailable; docs=fetched |
| 26 | Braid Design System | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 27 | British Gas Nucleus | ok | docs=fetched |
| 28 | Buildit Gravity | partial | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=unavailable |
| 29 | Bumbag UI | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 30 | BuzzFeed Solid | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 31 | Buzzvil Design System | ok | docs=fetched |
| 32 | CA Technologies Mineral UI | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 33 | CBRE Blocks | failed | docs=unavailable |
| 34 | Cedar (REI) | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 35 | Chakra UI | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 36 | City of Boston Fleet | ok | last_push=match; archived=not_recorded; licence=not_comparable; version=not_recorded; docs=fetched |
| 37 | Cloudflare cf-ui | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 38 | Co-op Experience Library | partial | repo=unavailable; docs=fetched |
| 39 | Contentful Forma 36 | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 40 | Decathlon Vitamin | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 41 | Decentraland UI | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 42 | Duet | ok | docs=fetched |
| 43 | Duolingo | ok | docs=fetched |
| 44 | eBay Skin | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 45 | Elastic EUI | ok | last_push=match; archived=not_recorded; licence=not_comparable; version=match; docs=fetched |
| 46 | ENGIE Fluid Design System | ok | docs=fetched |
| 47 | Enel | ok | docs=fetched |
| 48 | Enigma Boundless | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 49 | Estonia Country Design Guidelines | ok | docs=fetched |
| 50 | Evergreen | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 51 | Financial Times Origami | failed | repo=unavailable; docs=unavailable |
| 52 | Finland Toolbox | ok | docs=fetched |
| 53 | Firefox Photon | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 54 | Flowbite | partial | last_push=match; archived=not_recorded; licence=match; version=match; docs=unavailable |
| 55 | Fluent UI | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 56 | Foundation | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 57 | Foyer Design System | failed | docs=unavailable |
| 58 | French Government Design System (DSFR) | partial | last_push=match; archived=not_recorded; licence=not_comparable; version=match; docs=unavailable |
| 59 | FutureLearn Pattern Library | failed | docs=unavailable |
| 60 | GitHub Primer | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 61 | GitLab Pajamas | ok | docs=fetched |
| 62 | GoodBarber Design System | ok | docs=fetched |
| 63 | Google Material Design | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 64 | GOV.UK Design System | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded; docs=fetched |
| 65 | Gympass Yoga | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 66 | HashiCorp Helios | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 67 | Help Scout | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 68 | Heroku Purple3 | ok | docs=fetched |
| 69 | Grommet | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 70 | HubSpot Canvas | ok | last_push=match; archived=not_recorded; licence=not_comparable; version=not_recorded; docs=fetched |
| 71 | Hudl Design System | ok | docs=fetched |
| 72 | IBM Carbon | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded; docs=fetched |
| 73 | IBM Design Language | ok | docs=fetched |
| 74 | IBM Northstar | ok | docs=fetched |
| 75 | Intuit Harmony | ok | docs=fetched |
| 76 | Italia Design System | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 77 | JB Design System | ok | docs=fetched |
| 78 | JetBrains Ring UI | ok | last_push=match; archived=not_recorded; licence=match; version=mismatch; docs=fetched |
| 79 | Jobber (Atlantis) | partial | repo=unavailable; docs=fetched |
| 80 | Just Eat Takeaway.com PIE | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 81 | Kaizen (Culture Amp) | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 82 | KoliBri (Public-UI) | ok | last_push=match; archived=not_recorded; licence=not_comparable; version=match; docs=fetched |
| 83 | Kontur | ok | last_push=match; archived=not_recorded; licence=not_comparable; version=not_recorded; docs=fetched |
| 84 | Korea Design System (KRDS) | ok | last_push=match; archived=not_recorded; licence=not_comparable; version=match; docs=fetched |
| 85 | Lexicon | failed | docs=unavailable |
| 86 | Louder Than Ten Manual | ok | docs=fetched |
| 87 | Mail.ru Group Paradigm | ok | docs=fetched |
| 88 | Mailchimp Content Styleguide | ok | docs=fetched |
| 89 | Mantine | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 90 | Marvel Styleguide | ok | docs=fetched |
| 91 | Material Minimal | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 92 | Materialize CSS | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 93 | Mesh Design System | ok | docs=fetched |
| 95 | Mixpanel Design System | ok | docs=fetched |
| 96 | MongoDB Design System | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 97 | Monzo Tone of Voice | ok | docs=fetched |
| 98 | Morningstar Design System | ok | docs=fetched |
| 99 | Mozilla Protocol | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 100 | NASA Web Design System | ok | last_push=match; archived=not_recorded; licence=not_comparable; version=match; docs=fetched |
| 101 | NationBuilder Radius | failed | docs=unavailable |
| 102 | NHS.UK Service Manual | ok | docs=fetched |
| 103 | Nordhealth | ok | docs=fetched |
| 104 | New York State Design System | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 105 | Nordnet | failed | docs=unavailable |
| 106 | Okta Odyssey Design System | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 107 | Ontario Design System | ok | docs=fetched |
| 108 | Oracle Redwood | ok | docs=fetched |
| 109 | Persona Design System | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 110 | Pharos (JSTOR) | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 111 | Pinterest Gestalt | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 112 | Pivotal | partial | last_push=match; archived=not_recorded; licence=match; version=match; docs=unavailable |
| 113 | Pluralsight Design System | partial | last_push=match; archived=not_recorded; licence=match; version=mismatch; docs=unavailable |
| 115 | Priceline Design System | ok | last_push=match; archived=not_recorded; licence=match; version=mismatch; docs=fetched |
| 116 | Pusher Chameleon | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 117 | Radix | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 118 | Rambler UI | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 119 | Rendition | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 120 | Reshaped | ok | docs=fetched |
| 121 | Salesforce Lightning Design System | partial | last_push=match; archived=not_recorded; licence=not_comparable; version=match; docs=unavailable |
| 122 | Sage by Kajabi | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 123 | SAP Fiori | failed | docs=unavailable |
| 124 | SAP Fundamental | partial | last_push=match; archived=not_recorded; licence=match; version=match; docs=unavailable |
| 125 | SAP OpenUI5 | partial | last_push=match; archived=not_recorded; licence=match; version=match; docs=unavailable |
| 126 | Scania Digital Design System | failed | repo=unavailable; docs=unavailable |
| 127 | Seeds (Sprout Social) | ok | docs=fetched |
| 128 | SEEK Style Guide | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 129 | Semi Design | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 130 | Semrush Intergalactic | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 131 | Shoelace | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 133 | Shadcn/ui | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 134 | Siemens iX | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 135 | Singapore Government Design System | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 136 | Stacks (Stack Overflow) | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 137 | Starbucks Style Guide | failed | docs=unavailable |
| 138 | Strapi Design System | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 139 | Teambition Clarity Design | ok | docs=fetched |
| 141 | Thumbprint | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 142 | Tizen CircularUI | ok | last_push=match; archived=not_recorded; licence=not_comparable; version=not_recorded; docs=fetched |
| 143 | Twilio Paste | partial | last_push=match; archived=not_recorded; licence=match; version=match; docs=unavailable |
| 144 | Uber Base Web | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 145 | Ubuntu Vanilla framework | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 146 | Uiverse | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 147 | Untitled UI (React) | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 148 | uSwitch style guide | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 149 | U.S. Web Design Standards (USWDS) | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 150 | U.S. CMS.gov Design System | ok | last_push=match; archived=not_comparable; licence=mismatch; version=match; docs=fetched |
| 151 | Vibe (monday.com) | ok | last_push=match; archived=not_recorded; licence=not_comparable; version=match; docs=fetched |
| 152 | Vimeo Iris | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 153 | VMware Clarity | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 154 | VTEX Styleguide | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 155 | Vue Design System | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 156 | Ray (WeWork) | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 157 | Welcome UI | ok | last_push=match; archived=not_recorded; licence=match; version=mismatch; docs=fetched |
| 158 | West Midlands Network Design System | ok | last_push=match; archived=not_recorded; licence=not_comparable; version=match; docs=fetched |
| 159 | Wix Style React | ok | docs=fetched |
| 160 | Vercel Geist | ok | docs=fetched |
| 161 | Workday Canvas | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 162 | Yelp Styleguide | ok | docs=fetched |
| 163 | Zendesk Garden | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 164 | Australian Government Design System (GOLD) | ok | docs=fetched |
| 165 | Scottish Government Design System | ok | docs=fetched |
| 166 | New Zealand Government Design System (alpha) | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 167 | Tailwind UI | ok | docs=fetched |
| 168 | Preline UI | ok | docs=fetched |
| 169 | HeroUI | ok | docs=fetched |
| 170 | Air France Aero Design System | ok | docs=fetched |
| 171 | Airbus Digital Experience | ok | docs=fetched |
| 172 | UMD Design System | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 173 | UCL Design System | ok | docs=fetched |
| 174 | UCLA Design System | ok | docs=fetched |
| 175 | UQ Design System | ok | docs=fetched |
| 176 | University of Cambridge Design System | ok | docs=fetched |
| 177 | TAMU TUX Design System | ok | docs=fetched |
| 178 | WayneUI (Wayne State University) | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 179 | ASU Unity Stack (Arizona State University) | partial | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=unavailable |
| 180 | UNI Core (uni-design-system) | partial | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=unavailable |
| 181 | Iowa Design System (UIDS) | partial | last_push=match; archived=not_recorded; licence=not_comparable; version=match; docs=unavailable |
| 182 | nulib design-system (Northwestern University Libraries) | partial | last_push=match; archived=not_recorded; licence=not_comparable; version=match; docs=unavailable |
| 183 | UK Department for Education Design System | ok | docs=fetched |
| 184 | Chan Zuckerberg Education Design System (EDS) | partial | last_push=match; archived=not_recorded; licence=match; version=match; docs=unavailable |
| 185 | Home Office Design System | ok | docs=fetched |
| 186 | DWP Design System | ok | docs=fetched |
| 187 | HMRC Design Patterns | ok | docs=fetched |
| 188 | MoJ Design System (Ministry of Justice) | ok | docs=fetched |
| 189 | ONS Design System (Office for National Statistics) | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 190 | The National Archives Design System | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 191 | NICE Design System | ok | docs=fetched |
| 192 | Agriculture Design System (Australia) | ok | docs=fetched |
| 193 | NSW Design System (Digital NSW) | ok | docs=fetched |
| 194 | Australian Health Design System | ok | docs=fetched |
| 195 | Government of Quebec Design System | ok | docs=fetched |
| 196 | UX4G Design System (India) | ok | docs=fetched |
| 197 | California Design System | ok | last_push=match; archived=not_recorded; licence=match; version=match; docs=fetched |
| 198 | Brazilian Government Design System (gov.br) | ok | docs=fetched |
| 199 | GC Design System (Government of Canada) | ok | docs=fetched |
| 200 | B.C. Government Design System | ok | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=fetched |
| 201 | CFT Elephas (Center of Financial Technologies) | partial | last_push=match; archived=not_recorded; licence=match; version=not_recorded; docs=unavailable |
| 202 | Scale (Deutsche Telekom) | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded; docs=fetched |
| 203 | TDS core legacy v2 (TELUS) | partial | last_push=match; archived=not_comparable; licence=match; version=match; docs=unavailable |
| 204 | Mistica (Telefónica) | partial | last_push=match; archived=not_comparable; licence=not_comparable; version=not_recorded; docs=unavailable |
| 205 | Polaris (Shopify) | ok | last_push=match; archived=not_recorded; licence=match; version=mismatch; docs=fetched |
| 206 | CFPB Design System | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=match; docs=fetched |
| 208 | Bank of Canada Design System | ok | docs=fetched |
| 209 | Storefront UI (Vue Storefront) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 210 | Lion (ING) | ok | last_push=match; archived=not_comparable; licence=match; version=mismatch; docs=fetched |
| 211 | Iress Design System (IDS) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 212 | Orange Unified Design System (OUDS) Android | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 213 | NHS Digital website design system | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 214 | Design System Docs (University of Michigan Library) | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=match |
| 215 | SpareBank 1 Design System | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=mismatch |
| 216 | Mistica Web (Telefónica) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 217 | Meteor (Shopware) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 218 | Backbase Design System | ok | docs=fetched |
| 219 | OTTO B2B Design System | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 220 | Dress Code (Zalando) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 221 | Orange Design System iOS | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 222 | Lunar (Airbnb) | partial | last_push=match; archived=not_comparable; licence=match; version=match; docs=unavailable |
| 223 | Travelmakers Design System | ok | last_push=match; archived=not_comparable; licence=match; version=not_comparable; docs=fetched |
| 224 | Wonder Blocks (Khan Academy) | partial | last_push=match; archived=not_comparable; licence=match; version=match; docs=unavailable |
| 225 | Porsche Design System | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 226 | Utrecht Design System (Municipality of Utrecht) | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=mismatch |
| 227 | Paragon (Open edX) | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 228 | Government of Ireland Design System (GOV.IE) | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 229 | Volvo Cars Design System | ok | docs=fetched |
| 230 | Designsystemet (Digdir, Norway) | ok | last_push=match; archived=not_comparable; licence=match; version=mismatch |
| 231 | Försäkringskassans designsystem (Sweden) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 232 | SSB designsystem (Statistics Norway) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 233 | GC Design System tokens (Government of Canada) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 234 | DB UX Design System (Deutsche Bank) | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 235 | Able design system resources (Telstra) | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=not_recorded |
| 236 | NHS.UK frontend | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 237 | NHS App frontend | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 238 | NHS.UK React components (NHS Digital) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 239 | Instructure UI (Canvas LMS) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 240 | Amsterdam Design System (City of Amsterdam) | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=match |
| 241 | Product Kit Core (Mercedes-Benz) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 242 | WISE Design System (Education) | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=not_recorded |
| 243 | MUI (Material UI) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 244 | Vuetify | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=not_recorded |
| 245 | Quasar Framework | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 246 | Bulma | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 247 | Semantic UI | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 248 | PrimeVue | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 249 | Element Plus | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 250 | PatternFly | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 251 | daisyUI | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 252 | Quantinuum UI | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 253 | Kumo (Cloudflare) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 254 | U.S. General Services Administration design system (USDS) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 255 | CAMP Design System (Open Government Products, Singapore) | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=match |
| 256 | Uniform Design System (Open Colleges) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 257 | Rivet (Indiana University) | ok | last_push=match; archived=not_comparable; licence=match; version=mismatch |
| 258 | Spark Design System (Rocket Mortgage) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 259 | Astryx (Meta) | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 260 | UQ Design System (University of Queensland) | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=match |
| 261 | Guardian Source (The Guardian) | ok | last_push=match; archived=not_comparable; licence=match; version=mismatch |
| 262 | Skin (eBay) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 263 | Coinbase Design System (CDS) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 264 | GEL (BBC Global Experience Language) | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=match |
| 265 | Bootstrap | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 266 | Tabler | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 267 | Vaadin Web Components | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=not_recorded |
| 268 | Arco Design (ByteDance) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 269 | Vant (Youzan) | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 270 | Ionic Framework | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 271 | React Native Paper | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 272 | Material Web (Google) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 273 | Spectrum Web Components (Adobe) | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 274 | Angular Material and CDK | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 275 | PrimeNG | ok | last_push=match; archived=not_comparable; licence=mismatch; version=match |
| 276 | NG-ZORRO (Ant Design for Angular) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 277 | Skeleton | ok | last_push=match; archived=not_comparable; licence=match; version=mismatch |
| 278 | Spectrum CSS (Adobe) | ok | last_push=match; archived=not_comparable; licence=match; version=mismatch |
| 279 | Headless UI (Tailwind Labs) | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 280 | VA.gov Design System (Veterans Affairs) | ok | docs=fetched |
| 281 | DIBBS Design System (CDC) | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 282 | Naive UI | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 283 | Tamagui | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 284 | Gluestack UI | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=not_recorded |
| 285 | Park UI | ok | last_push=match; archived=not_comparable; licence=match; version=mismatch |
| 286 | Radix Themes | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 287 | Ant Design Vue | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 288 | Theme UI | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 289 | Rebass | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 290 | WordPress Gutenberg Design System | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 291 | Framework7 | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 292 | Flowbite Svelte | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 293 | Sanity Design System (Sanity UI) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 294 | Helsinki Design System (City of Helsinki) | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 295 | HMCTS Design System | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 296 | Primer CSS (GitHub) | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 297 | BootstrapVue | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 298 | Flowbite React | ok | last_push=match; archived=not_comparable; licence=match; version=not_recorded |
| 299 | Onsen UI | ok | last_push=match; archived=not_comparable; licence=not_comparable; version=match |
| 300 | Kobalte | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 301 | Nuxt UI | ok | last_push=match; archived=not_comparable; licence=match; version=match |
| 302 | MUI Base UI | ok | last_push=match; archived=not_comparable; licence=match; version=match |
