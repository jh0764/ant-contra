## Overview

PostHog's marketing system is built on the visual contradiction at the heart of the brand: a serious open-source product analytics platform rendered as if it were a friendly engineering sketchbook. The chrome runs on a warm cream canvas (`{colors.canvas}` — `#eeefe9`) — not white — and every page is dotted with hand-drawn hedgehog mascots in lab coats, lounge chairs, terminals, and reading glasses, scattered across the layout like marginalia in a textbook. Type sits in IBM Plex Sans Variable at olive-gray (`{colors.body}` — `#4d4f46`) for body and deep olive-charcoal (`{colors.ink}` — `#23251d`) for headlines, with weights stepped tightly between 400, 600, 700, and 800 to create hierarchy without color. The single saturated yellow-orange pill (`{colors.primary}` — `#f7a501`) is the brand's only loud chromatic moment; everything else is cream, olive, white card, and state-driven indicators.

The system features a **data-dense indicator layout**: main dashboard and analysis cards sit on pure white card surfaces (`{colors.surface-card}`), complemented by persistent sidebar/rail modules that maintain structural state accents (Green captured rails, Yellow caution rails, soft blue target blocks, and light yellow alert containers).

Sections stack at `{spacing.section}` (80px) rhythm with cream canvas continuing edge-to-edge between them. There are no decorative gradients, no atmospheric mesh backgrounds, and no full-bleed dark hero chapters; the cream canvas runs uninterrupted top to bottom.

**Key Characteristics:**

- Warm cream canvas (`{colors.canvas}` — #eeefe9) end-to-end with no surface alternation between sections — the page is one continuous sheet
- Single yellow-orange CTA pill (`{colors.primary}` — #f7a501) with deep olive text (`{colors.on-primary}`) — the brand's primary action color
- IBM Plex Sans Variable across every text role with weights 400/500/600/700/800 — no other typeface in the system
- State-driven card indicator system featuring left-border accent rails (`{colors.accent-green}` for captured/positive indicators, `{colors.primary-active}` for neutral/caution indicators)
- 4–8px radius card vocabulary: `{rounded.md}` (6px) for most components, `{rounded.lg}` (8px) for select containers, fully rounded for pill chips

## Colors

### Brand & Accent

- **PostHog Yellow** (`{colors.primary}` — `#f7a501`): universal primary CTA, warning badge outline, neutral indicator pills, and primary action buttons.
- **Yellow Pressed** (`{colors.primary-pressed}` — `#dd9001`): pressed state for primary pill actions.
- **Yellow Active** (`{colors.primary-active}` — `#b17816`): gold-toned border accent for neutral/caution state cards and active indicators.

### Surface

- **Canvas** (`{colors.canvas}` — `#eeefe9`): warm cream page background running end-to-end.
- **Soft Surface** (`{colors.surface-soft}` — `#e5e7e0`): secondary button fill, tab strip backgrounds, inline chip backgrounds.
- **Surface Card** (`{colors.surface-card}` — `#ffffff`): true white card and tile background sitting on top of the cream canvas.
- **Surface Doc** (`{colors.surface-doc}` — `#fcfcfa`): faintly cream-warm white used inside doc/detail cards.
- **Surface Alert Soft** (`{colors.surface-alert-soft}` — `#fdf8e8`): light yellow container background for alert/caution rail cards and indicator summaries.
- **Surface Blue Soft** (`{colors.surface-blue-soft}` — `#eff6ff`): soft blue container background for risk-reward (R:R) and target price blocks.
- **Surface Dark** (`{colors.surface-dark}` — `#23251d`): deep olive-charcoal used for inverted dark code blocks.
- **Hairline** (`{colors.hairline}` — `#bfc1b7`): 1px card border, table rule, and container borders.
- **Hairline Soft** (`{colors.hairline-soft}` — `#dcdfd2`): in-card row dividers and subtle inset rules.

### Text

- **Ink** (`{colors.ink}` — `#23251d`): headlines, bold metrics, button text — deep olive-charcoal.
- **Body** (`{colors.body}` — `#4d4f46`): default paragraph text, indicator descriptions, body copy.
- **Mute** (`{colors.mute}` — `#6c6e63`): metadata, timestamps, secondary labels.
- **Ash** (`{colors.ash}` — `#9b9c92`): disabled-state text and lowest-emphasis utility text.

### Semantic & Indicators

- **Positive / Captured Green** (`{colors.accent-green}` — `#10b981` / `#059669`): left rail accent border on captured indicators, success badges, and positive score callouts.
- **Caution / Neutral Gold** (`{colors.accent-gold}` — `#d97706`): left rail accent border on neutral indicators, caution badges, and alert borders.
- **Alert Red** (`{colors.accent-red}` — `#ef4444`): high/low price markers, extreme loss/fear labels, and alert highlights.
- **Info Blue** (`{colors.accent-blue}` — `#2563eb`): price percentage movement, risk-reward metrics, and informational anchor links.

## Typography

### Hierarchy

| Token                           | Size | Weight | Line Height | Letter Spacing | Use                                             |
| ------------------------------- | ---- | ------ | ----------- | -------------- | ----------------------------------------------- |
| `{typography.display-xl}`       | 36px | 700    | 1.5         | 0              | Main hero title / Stock current price metric    |
| `{typography.display-lg}`       | 24px | 800    | 1.33        | -0.6px         | Section headline, large gauge score value       |
| `{typography.heading-lg}`       | 21px | 700    | 1.4         | -0.5px         | Sub-section heading, main card H2               |
| `{typography.heading-md}`       | 20px | 700    | 1.4         | 0              | Card title, indicator signal name               |
| `{typography.heading-sm}`       | 18px | 700    | 1.5         | 0 (uppercase)  | Category eyebrows ("TODAY'S FEAR TOP 10")       |
| `{typography.heading-sm-mixed}` | 18px | 600    | 1.56        | 0              | Card title in mixed-case                        |
| `{typography.body-md}`          | 16px | 400    | 1.5         | 0              | Default body text, description copy             |
| `{typography.body-strong}`      | 16px | 600    | 1.5         | 0              | Emphasized label, active tab title              |
| `{typography.body-sm}`          | 15px | 400    | 1.71        | 0              | Indicator detail explanation, news article text |
| `{typography.body-xs}`          | 14px | 500    | 1.43        | 0              | Sidebar list item, timestamp, metadata          |
| `{typography.caption-xs}`       | 12px | 600    | 1.33        | 0              | Inline status badges ("포착", "중립")           |
| `{typography.button-md}`        | 14px | 700    | 1.5         | 0              | Primary/secondary action button label           |

## Layout & Structure

### Spacing System

- **Base unit:** 8px
- **Tokens:** `{spacing.xxs}` (2px) · `{spacing.xs}` (4px) · `{spacing.sm}` (8px) · `{spacing.md}` (12px) · `{spacing.lg}` (16px) · `{spacing.xl}` (24px) · `{spacing.section}` (80px).
- **Rhythm:** Standard card grids use `{spacing.lg}` (16px) gutters; card internal padding sits at `{spacing.lg}` (16px) to `{spacing.xl}` (24px).

### Card Accent Rails

- **Captured Rail Card (`indicator-card-captured`):** 1px `{colors.hairline}` border with a 4px solid `{colors.accent-green}` left accent rail.
- **Neutral Rail Card (`indicator-card-neutral`):** 1px `{colors.hairline}` border with a 4px solid `{colors.accent-gold}` left accent rail.
- **Sidebar Alert Card (`sidebar-card-alert`):** 1px solid `{colors.primary-active}` border with `{colors.surface-alert-soft}` background fill.

## Components

### Buttons & Pills

**`button-primary`**

- Background `{colors.primary}` (`#f7a501`), text `{colors.on-primary}` (`#23251d`), type `{typography.button-md}`, height `40px`, rounded `{rounded.md}`.

**`badge-captured`**

- Background `{colors.accent-green}`, text `#ffffff`, type `{typography.caption-xs}`, padding `4px 10px`, rounded `{rounded.full}`. Label: "포착".

**`badge-neutral`**

- Background `{colors.accent-gold}`, text `#ffffff`, type `{typography.caption-xs}`, padding `4px 10px`, rounded `{rounded.full}`. Label: "중립".

### Indicator & Metric Cards

**`indicator-card-captured`**

- Container: Background `{colors.surface-card}`, border 1px solid `{colors.hairline}`, left rail 4px solid `{colors.accent-green}`, padding `16px 20px`, rounded `{rounded.md}`.
- Layout: Icon avatar left, Indicator Title (`{typography.heading-md}`), status badge right, subtitle with parameter value (`{typography.body-strong}`), description (`{typography.body-sm}`).

**`indicator-card-neutral`**

- Container: Background `{colors.surface-card}`, border 1px solid `{colors.hairline}`, left rail 4px solid `{colors.accent-gold}`, padding `16px 20px`, rounded `{rounded.md}`.

**`sidebar-metric-card`**

- Container: Background `{colors.surface-card}`, border 1px solid `{colors.hairline}`, padding `20px`, rounded `{rounded.md}`.
- Layout: Title top, prominent numerical score right (`{typography.display-lg}` in `{colors.accent-green}` or `{colors.ink}`), secondary progress bar or status description below.

**`sidebar-card-alert`**

- Container: Background `{colors.surface-alert-soft}`, border 1px solid `{colors.primary-active}`, padding `16px`, rounded `{rounded.md}`.
- Layout: Top warning icon + message (`{typography.body-strong}`), bottom action button/link (`{colors.primary-active}`).

**`risk-reward-card`**

- Container: Background `{colors.surface-card}`, border 1px solid `{colors.hairline}`, padding `20px`, rounded `{rounded.md}`.
- Contains nested `{colors.surface-blue-soft}` summary block for R:R metrics and target values.

## Do's and Don'ts

### Do

- Keep `{colors.canvas}` (`#eeefe9`) as the page background.
- Preserve the 4px left accent rail system for indicator state differentiation (Green = Captured, Gold = Neutral/Caution).
- Maintain white `{colors.surface-card}` for main data cards and sidebar cards sitting on cream canvas.
- Use `{colors.surface-alert-soft}` for alert summary blocks in the right rail.

### Don't

- Don't replace the warm cream canvas with pure white.
- Don't change sidebar card backgrounds or alter existing right rail colors.
- Don't use drop shadows on cards; maintain flat design with hairline borders and state accent rails.
