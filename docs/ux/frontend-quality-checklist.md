# Global Soil Explorer: Frontend UX Quality Checklist

This checklist must be verified prior to freezing frontend milestones and release integrations.

---

## 1. Interaction & State Integrity

*   [ ] Every button, select element, and collapsible card supports default, hover, active, focus, and disabled styling.
*   [ ] Screen transitions and sidebar slides employ ease-out cubic-bezier curves (duration <= 250ms).
*   [ ] Click actions on coordinates trigger immediate summary skeleton blocks within 16ms.
*   [ ] Map canvas handles container resizing automatically when sidebars expand/collapse.

---

## 2. Accessibility Verification

*   [ ] Core interactive elements are navigable in sequence using the `Tab` key.
*   [ ] Keyboard focus rings are clearly visible and use `--accent-teal` borders.
*   [ ] ARIA roles (`tablist`, `tab`, `dialog`, `application`) are set with correct expansion attributes.
*   [ ] Contrast ratios for primary text meet or exceed WCAG AA (`4.5:1` target).

---

## 3. Performance & Responsiveness Gates

*   [ ] Layout adapts to mobile, tablet, and desktop breakpoints without clipping.
*   [ ] Large data tables and bookmarks history lists employ virtualization.
*   [ ] Heavy analysis engines and PDF export tools are split into lazy-loaded code chunks.
*   [ ] Multi-stage network requests handle dynamic cancellation (AbortController) on target switches.
