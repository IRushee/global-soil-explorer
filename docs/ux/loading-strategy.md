# Global Soil Explorer: Loading Strategy Specification

This document defines performance loading patterns, skeletons placement rules, and retry states for coordinate seek cycles.

---

## 1. Visual Loading Patterns

*   **Header & Sidebar Skeleton Loading**: When the app initializes, render light gray animated gradients (`pulse` effect, duration 1.5s) matching the shape of the selectors and list items.
*   **Scientific Information Panel Skeletons**:
    *   Do not show generic spinners.
    *   Render a pulse skeleton representing the vertical soil horizon blocks (5 rows) and table columns.
    *   Render chart axes outlines without plots lines.

---

## 2. Progressive Data Loading

*   **First-Stage Details**: Immediately fetch coordinate lookup attributes (weather, Koppen Climate, coordinate validations). Renders inside the Summary Panel card within **150ms**.
*   **Second-Stage Details (Asynchronous)**: Request deep profiles and chemical properties. Recharts plots are animated into view once values return from the FastAPI endpoint.
*   **Prefetching & Speculative Seeks**:
    *   When the user hovers their mouse pointer over a coordinate for **> 400ms**, TanStack Query pre-fetches the observation details in the background.
    *   If the user clicks, the panel displays details instantly from the L2 cache (0ms latency).

---

## 3. Request Cancellation & Retry Workflows

*   **Active Click Interruption**: If the user clicks coordinate A, and then clicks coordinate B before coordinate A's fetch completes, the coordinate A network request is immediately cancelled using Axios `AbortController`.
*   **Retry Policy**:
    *   Low-priority geocoding searches: No retry.
    *   Scientific coordinates lookup queries: Retry twice with exponential backoff delay (1s, 2s).
    *   If requests fail twice, display a clean recovery button ("Retry Lookup").
