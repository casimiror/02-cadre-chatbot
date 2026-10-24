# Frontend design

Visual and interaction rules for the chat UI. Styles live in `frontend/src/styles.css`.

## Principles

- **Calm and neutral**: warm off-white page, white card, near-black accent. Cadre's brand is not
  replicated; the UI must not look like an official Cadre property.
- **One focal point**: a single centered chat card, max 560 px wide, full height on phones.
- **Content first**: assistant replies are the product. Readable line length and spacing beat
  decoration.

## Tokens

Defined as CSS custom properties on `:root`. Use tokens, never raw colors, in new rules.

| Token | Use |
| --- | --- |
| `--bg` | page background |
| `--surface` | chat card |
| `--text` / `--muted` | body text / secondary text (typing indicator, hints) |
| `--accent` | primary button |
| `--user` / `--user-text` | user bubble background / text |
| `--assistant` | assistant bubble background |
| `--error` | error messages |

Type: `system-ui` stack, inherited everywhere (`font: inherit` on controls). Radii: 16 px card,
14 px bubbles, 10 px controls.

## Class naming

BEM-style, one block per component:

- Block: `.chat`, `.bubble`
- Element: `.chat__header`, `.chat__messages`, `.chat__input`, `.chat__error`
- Modifier: `.bubble--user`, `.bubble--assistant`, `.bubble--typing`

New UI follows the same pattern (for example `.feedback`, `.feedback__button--active`). No CSS
frameworks or CSS-in-JS.

## Components

- **Bubbles**: user right-aligned on `--user`, assistant left-aligned on `--assistant`, max 85 %
  width. The typing indicator is an assistant bubble with `--muted` text.
- **Markdown in replies**: `.markdown` inside an assistant bubble. Paragraph and list spacing is
  8 px, links inherit the text color and are underlined, inline code gets a faint background. The
  bubble drops `white-space: pre-wrap` when it holds Markdown.
- **Feedback**: two 28 px icon buttons under each stored reply (`.feedback`). Outlined and muted by
  default, filled with `--text` when chosen; hover shows the `--assistant` background. Each button
  has `aria-label` ("Helpful", "Not helpful") and `aria-pressed`; the pair is a labelled `group`.
- **Input bar**: text field + Send button; Send is disabled while a reply is pending or the field is
  empty. `maxLength` matches the backend's `MAX_INPUT_CHARS`.
- **Errors**: one line under the messages, `role="alert"`, plain language, no codes.

## Accessibility

- The message list is `aria-live="polite"` so screen readers announce replies.
- Every control has a visible label or `aria-label`; icon-only buttons need `aria-label` and
  `aria-pressed` when they toggle.
- Keep text contrast at WCAG AA or better against its background.
- Keyboard: everything reachable with Tab; Enter submits the form.

## Responsive

The card fills the viewport height (`100dvh`) with a 16 px gutter; no horizontal scroll at phone
widths.
