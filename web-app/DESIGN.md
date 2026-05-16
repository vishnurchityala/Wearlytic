# Web App Design Guide

This document defines the current Wearlytic web-app design style and the rules future UI work should follow. Keep this file updated when major UI patterns change.

## Design Direction

Wearlytic should feel like a focused fashion utility: clean, product-first, direct, and easy to scan. The app should prioritize browsing clothes, selecting products, managing profile context, and seeing generated outputs without unnecessary decoration.

The current design language is:

- black, white, and gray dominant,
- strong borders,
- soft shadows,
- rounded controls,
- product imagery as the main visual content,
- compact operational UI in authenticated areas,
- larger expressive typography only on the landing hero.

## Tech And Styling

Use the current stack:

- React components in JSX.
- Tailwind CSS utility classes.
- Tailwind CSS 4 imported through `src/index.css`.
- Font Awesome React icons for existing icon patterns.
- Public images from `web-app/public/` for brand/product visuals.

Do not add a second component library or CSS framework unless maintainers explicitly approve it.

## Fonts

Font imports live in `src/index.css`.

Use these helper classes:

| Class | Font | Use |
| --- | --- | --- |
| `outfit-regular` | Outfit | Default UI font for forms, buttons, cards, body text, labels, and dashboard-like surfaces. |
| `anton-regular` | Anton | Display typography, mostly landing hero or strong numeric/step accents. |
| `bbh-bartle-regular` | BBH Bartle | Decorative hero headline text only. |

Rules:

- Default to `outfit-regular`.
- Use `anton-regular` sparingly for hero/display moments or small visual markers.
- Do not use decorative fonts inside dense tool surfaces, forms, filters, product cards, or profile panels.
- Do not use viewport-width-based font sizing.
- Keep letter spacing normal unless matching an existing uppercase metadata label.

## Color System

Current palette:

| Role | Tailwind classes |
| --- | --- |
| Page background | `bg-gray-50`, `bg-white` |
| Primary action | `bg-black text-white`, hover `hover:bg-gray-900` |
| Primary text | `text-black`, `text-gray-900`, `text-gray-800` |
| Secondary text | `text-gray-700`, `text-gray-600`, `text-gray-500` |
| Muted text | `text-gray-400` |
| Borders | `border-gray-200`, `border-gray-300` |
| Success/selected | `bg-green-600 border-green-600 text-white` |
| Error | `text-red-600` |

Rules:

- Keep the app neutral and product-led.
- Use black as the primary call-to-action color.
- Use green only for selected or successful states.
- Use red only for errors or destructive warnings.
- Avoid adding large gradients, decorative color blobs, or one-off color themes.

## Layout Principles

### Global Chrome

`Navbar` is the standard top navigation:

- translucent light gray background,
- bottom border,
- logo on the left,
- nav links and login/logout action on the right,
- mobile menu below the nav.

Use `Navbar` on authenticated pages and landing pages unless a page has a specific reason not to.

`Footer` is used on the landing page only.

### Page Widths

Use these width conventions:

- Profile content: `max-w-5xl mx-auto px-4 sm:px-6`.
- Landing content: `max-w-6xl` or `max-w-7xl` depending on visual section.
- Tool panels: fill available height and width rather than using marketing-style centered cards.

### Spacing

Common spacing patterns:

- Page sections: `py-6 sm:py-8`, `py-10 sm:py-14`.
- Panel/card padding: `p-3`, `p-4`, `p-5`, `sm:p-6`.
- Component gaps: `gap-3`, `gap-4`, `gap-6`.
- Form field vertical spacing: `mt-4`, `space-y-3`.

Avoid excessive vertical whitespace inside authenticated workflows.

## Surfaces

### Panels

Use panels for tool regions, profile sections, filters, product lists, and generation history:

```jsx
className="bg-white border-2 border-gray-300 rounded-lg shadow-sm p-4"
```

Current components use:

- `rounded-lg` for profile panels and generation history.
- `rounded-xl` for filters, product sections, product image frames, and compact controls.
- `rounded-2xl` and larger only on existing landing/marketing sections.

Future rule:

- Use `rounded-lg` for new operational panels by default.
- Use `rounded-xl` only when matching existing product/filter controls.
- Reserve `rounded-2xl+` for landing-page promotional sections.

### Cards

Cards should represent repeated content:

- product cards,
- generated image cards,
- step cards on landing,
- past generation cards.

Do not nest cards inside cards unless there is a real repeated sub-item, such as products used inside a past generation.

## Buttons

### Primary Button

Use for main actions:

```jsx
className="px-4 py-1.5 text-sm rounded-full bg-black text-white outfit-regular hover:bg-gray-900 transition-colors disabled:opacity-60"
```

Examples:

- Generate
- Upload
- Save Changes
- Get Started

### Icon Buttons And Icon-Text Buttons

Use Font Awesome icons where current code already uses that icon library.

Examples:

- Login/logout: `faUser`, `faRightFromBracket`
- Save: `faFloppyDisk`
- Upload: `faUpload`
- Product view: `faEye`
- Selected: `faCheck`
- Filters/collapse: `faFilter`, `faChevronDown`, `faChevronUp`

Rules:

- Use icon-only buttons only when the icon is obvious or has a title/aria label.
- Use icon + text for primary form actions.
- Keep icons visually small and aligned with text.

### Disabled State

Use:

- `disabled:opacity-60`
- `cursor-not-allowed` when a disabled state needs stronger affordance.

Do not let disabled controls look identical to active controls.

## Forms

Form style:

```jsx
className="w-full border-2 border-gray-300 px-3 py-2 rounded-xl bg-white outfit-regular"
```

Labels:

```jsx
className="block text-sm text-gray-700 mb-1 outfit-regular"
```

Guidelines:

- Keep labels visible. Do not rely only on placeholders.
- Use `text-sm` labels and `text-xs` helper text.
- Show inline errors near the field or form action.
- Maintain loading state while submitting.
- Do not silently ignore failed saves or uploads.

## Product Browsing UI

Product browsing lives in the playground left panel.

Patterns:

- Filters live inside a collapsible bordered panel.
- Category filters are pill buttons.
- Products are compact cards with image, title, price, select action, and external view action.
- Selected products move to the top of the product list.
- Selection limit is 3 products.

Product card rules:

- Keep images inside fixed-height frames with `object-contain`.
- Use `line-clamp-2` for product titles.
- Keep price visible and near the title.
- Keep external links explicit with an icon or short label.

## Playground Layout

Desktop:

- `react-resizable-panels` splits clothes browsing and tryout canvas.
- The layout fills viewport height below the navbar.
- Separator is narrow, gray, and draggable.

Mobile:

- Stack clothes section above playground section.
- Preserve vertical scrolling.
- Do not force desktop split-panel behavior on mobile.

Tryout canvas:

- Use full available area.
- Keep generated images centered and wrapping.
- Empty state should stay quiet and minimal.

## Landing Page

Landing page is the only place for expressive presentation.

Current patterns:

- large centered hero,
- brand/source logo row,
- product/fashion imagery,
- step cards,
- alternating informational banner,
- simple contact/suggestion section.

Future landing updates:

- Keep product or fashion imagery visible.
- Keep the Wearlytic offer direct.
- Do not add abstract SVG/gradient decoration.
- Do not turn the landing page into a dense dashboard.
- Keep the next section visible below hero on common viewport sizes where practical.

## Profile Page

Profile page style:

- `max-w-5xl` container,
- two-column desktop grid,
- profile image card on left,
- profile details card on right,
- generation history below.

Profile design rules:

- Keep user metadata compact.
- Use disabled inputs for read-only values such as email.
- Use badges/pills for role and token metadata.
- Show upload preview immediately.
- Show success/error text near the upload button.

## Loading, Empty, Error, Success States

### Loading

Use simple spinners:

```jsx
className="w-6 h-6 border-4 border-t-black border-gray-300 rounded-full animate-spin"
```

Use skeleton blocks for profile form initial loading.

### Empty

Use quiet empty states:

- Product list: `no-results.png` plus short text.
- Canvas: `Canvas Output`.
- Generation history: currently returns nothing when empty; future work should add a small empty state.

### Error

Use:

```jsx
className="text-sm text-red-600"
```

Rules:

- Errors must be visible when user action fails.
- Do not rely on `console.error` only for user-triggered actions.

### Success

Use:

```jsx
className="text-sm text-green-600"
```

Use only after confirmed successful API response.

## Responsive Rules

Use Tailwind breakpoints consistently:

- mobile first by default,
- `sm:` for small layout adjustments,
- `md:` for two-column layouts and desktop-only nav,
- `lg:` only for wider landing grids or major layout changes.

Current responsive patterns:

- Navbar links hide on mobile and move into a dropdown.
- Profile grid changes from one column to three-column layout at `md`.
- Landing cards change from one column to two columns to four columns.
- Playground changes from stacked mobile layout to split desktop layout at `md`.

## Images And Assets

Use assets from `public/` with root-relative paths:

```jsx
<img src="/image.png" alt="Wearlytic Logo" />
```

For product and generated images:

- use meaningful `alt` text,
- use `object-contain` for product images,
- use `object-cover` only when cropping is acceptable,
- keep image containers dimensioned to prevent layout shifts.

## Accessibility

Minimum expectations:

- Buttons must have `type="button"` unless they submit a form.
- Icon-only actions need `aria-label` or `title`.
- Images need meaningful `alt` text.
- Links that open new tabs need `target="_blank"` and `rel="noopener noreferrer"`.
- Form controls need visible labels.
- Loading states must not trap the user without feedback.

## Component Organization

Current structure:

- Page components live under `src/pages/<page>/`.
- Page-specific components live under `src/pages/<page>/components/`.
- Shared layout components live in `src/layout/`.
- Auth code lives in `src/auth/`.
- API helper code lives in `src/api/`.

Rules:

- Keep page-specific components local to their page.
- Move shared components only when they are used by multiple pages.
- Avoid creating broad generic abstractions before the same pattern exists in multiple places.

## Copy And Tone

Use direct, short UI copy.

Good:

- `Generate`
- `Upload`
- `Save Changes`
- `No Results`
- `Loading generations...`

Avoid:

- long explanatory text inside tool surfaces,
- technical implementation terms in user-facing copy,
- marketing copy in authenticated workflows.

## Future UI Checklist

Before merging a visual change:

- [ ] Uses existing fonts and neutral color palette.
- [ ] Works on mobile and desktop.
- [ ] Has loading, empty, error, and success states where relevant.
- [ ] Does not introduce a new design system or icon library.
- [ ] Keeps product imagery dimensioned and stable.
- [ ] Uses `apiFetch()` for backend calls.
- [ ] Keeps authenticated workflows compact and task-focused.
- [ ] Uses accessible labels, alt text, and button types.

## Anti-Patterns

Avoid:

- adding large decorative gradients or blobs,
- adding unrelated colors outside the existing neutral palette,
- using decorative fonts in forms or product cards,
- building new pages as marketing sections when they are tools,
- hiding user-action failures in the console only,
- using hardcoded backend URLs in components,
- adding full page reload links where router navigation is expected in authenticated flows,
- changing endpoint paths without updating backend and context docs.
