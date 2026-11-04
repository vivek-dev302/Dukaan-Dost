# Dukaan Dost design system

## Product and audience

Dukaan Dost is a working shop book for small Indian retail shops. Shop owners use it between customers to record khata, note what to restock, consult an optional product catalog, and ask a voice assistant to perform shop tasks. The interface should feel dependable, quick to scan, and comfortable on a phone.

Product behavior is part of the design contract. Preserve the existing routes (`/`, `/items`, `/restocking`, `/khata`, `/assistant`, `/agent-logs`), Google sign-in, per-shop data isolation, API calls and payloads, validation, filters, controlled inputs, confirmation timing, stored paise values, and business rules. The catalog is reference-only and has no stock quantities. Restock entries may be outside the catalog. The category field currently required by the restock form remains required unless product behavior is deliberately changed in a separate decision.

## Design principles

1. **A useful shop book, not a generic back office.** Use the visual language of a neighborhood shop ledger: warm paper, clear rules, restrained labels, and deliberate hierarchy.
2. **Make the next task obvious.** On the overview, emphasize the voice action first, outstanding khata second, and restocking needs third. Keep the existing metrics and recent records available.
3. **Trust comes from legibility.** Keep amounts, dates, customer names, selected filters, and confirmation details easy to distinguish. Never invent metrics or imply stock tracking.
4. **Keep familiar paths familiar.** Preserve route destinations and the shared navigation. Responsive layout may reorganize controls, but must not hide destinations or actions.
5. **Feedback follows the existing behavior.** Loading, error, empty, listening, speaking, approval, rejection, and success states should be visible without changing when operations occur.

## Visual direction

Extend the existing shop identity as a **working ledger for a neighborhood shop**. Retain its paper ground, forest-green identity, brass detail, Hindi brand mark, and pairing of Newsreader display type with DM Sans interface type. Use ruled separators, shelf-label-like category tags, and ledger grouping as small product-specific signatures. Avoid charts without real underlying data, decorative dashboard widgets, gradients, glass effects, and ornamental clutter.

## Color palette

The current CSS tokens are the source of truth; keep their values consistent across pages.

| Token | Value | Use |
| --- | --- | --- |
| `--paper` | `#f2efe7` | Main page ground |
| `--surface` | `#fbfaf6` | Cards, forms, and sheets |
| `--surface-warm` | `#f7f4ec` | Quiet secondary surface |
| `--ink` | `#26332d` | Primary text |
| `--muted` | `#70786f` | Supporting text |
| `--line` | `#ded9cc` | Standard separators |
| `--line-strong` | `#c9c1b1` | Control borders and stronger rules |
| `--forest` | `#203f34` | Brand, primary actions, active state |
| `--forest-deep` | `#18342b` | Hover and pressed emphasis |
| `--forest-soft` | `#e6ece5` | Selected and supporting states |
| `--brass` | `#a97a37` | Small emphasis marks and highlights |
| `--brass-soft` | `#f3ead8` | Small category and ledger labels |
| `--danger` | `#9b4b3e` | Destructive actions and errors |
| `--danger-soft` | `#f7e9e5` | Destructive state surface |

Use green as the strongest action color. Brass is a restrained accent, not body text on paper at small sizes. Reserve danger colors for destructive or error states. Do not introduce additional accent families without a product need.

## Typography

- **DM Sans** for controls, body copy, navigation, data, and labels.
- **Newsreader** for page titles, prominent figures, and occasional identity details.
- Use tabular numerals for currency and counts where alignment helps comparison.
- Eyebrows and metadata may use uppercase with generous tracking, but keep them secondary to plain-language labels.
- Keep important labels at least 12px in dense application views; body text should usually be 13–16px.

## Spacing and layout

- Use a consistent 4px base rhythm; common gaps are 8, 12, 16, 20–24, and 32px.
- Keep content within the existing centered maximum width of about 1240px, with 24px desktop gutters and reduced mobile gutters.
- Group related data and controls into paper surfaces with fine rules. Use borders and spacing before adding shadows.
- Keep forms close to the list or entity they affect. Preserve the existing two-column workspaces at wide widths and stack them at narrow widths.
- Align currency and date columns consistently; maintain enough space for long names and descriptions to wrap without covering actions.

## Responsive behavior

- Support widths down to 320px without page-level horizontal overflow.
- Keep all six routes reachable at every width. The existing horizontal navigation may scroll, but its affordance and active destination must remain apparent; do not silently remove route links.
- Stack workspace columns on small screens and keep primary actions visible near their related content.
- Convert dense table rows into readable compact records on narrow screens rather than dropping meaningful fields. Keep row actions reachable.
- Make voice call surfaces and dialogs fit within the viewport, including safe space around controls; preserve full-screen backdrop behavior.
- Prefer touch targets of at least 44px for primary controls and icon-only actions where layout permits.

## Components and states

- **Shared shell:** brand lockup, signed-in account controls, persistent route navigation, page content, and accessible skip link.
- **Page heading:** clear title, concise existing description, optional contextual action.
- **Panels:** paper surface, modest radius, thin ledger rule, consistent interior spacing.
- **Buttons:** forest primary; paper/outlined secondary; text actions for low-emphasis controls; danger treatment only for destructive actions.
- **Forms:** visible labels, existing required/optional semantics, controlled values, inline validation and disabled/loading state without changing submission rules.
- **Lists and tables:** aligned names, amounts, dates, and actions; selected customer/category state must be clear.
- **Dialogs and confirmations:** preserve existing confirmation content and timing; show the affected record/action clearly and keep keyboard focus visible.
- **Voice assistant:** visually distinct listening, sending, speaking, pending approval, retry, and ended states. Preserve the current silence-send, manual-send, transcript, approval/rejection, TTS, and exit flows.
- **Feedback:** use existing toast, empty, loading, error, and confirmation mechanisms; keep messages associated with the operation that produced them.
- **Motion:** short state transitions only; respect `prefers-reduced-motion`.

## Accessibility

- Maintain semantic headings, landmarks, labels, buttons, and link destinations.
- Keep keyboard focus visible and in a logical order. Dialogs must announce their purpose and must not strand keyboard users.
- Do not communicate active, error, approval, or listening state through color alone; pair color with text or an accessible state label.
- Preserve readable contrast for text and controls. Avoid small low-contrast brass labels for essential information.
- Give icon-only controls accessible names, provide status announcements for voice and request state changes, and respect reduced-motion preferences.
- Check keyboard use and narrow viewport reflow whenever shared navigation, forms, tables, or dialogs change.

## Behavior preservation checklist

During visual work, retain these interfaces and rules exactly: route paths; authenticated route gating; Google sign-in and shop scope; catalog category/item operations and no-quantity model; uncatalogued restock entries; khata customer and record CRUD, filters, and paise storage; agent log paging; assistant text/voice requests and payloads; Redis-backed temporary context; protected-action approval and rejection; spoken responses; call exit; and all existing validation, confirmation, and refresh timing.

Do not change factual product copy or accounting behavior as part of visual styling. Flag potentially inaccurate wording for product approval first.
