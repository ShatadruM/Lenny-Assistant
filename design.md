# UI/UX & Design Document

## 1. UI/UX Principles
- **Premium & Modern Aesthetics:** The application embraces a sleek, dark-mode-first aesthetic (`#0c0a09` backgrounds, `#f5f5f4` text) to reduce eye strain and feel state-of-the-art.
- **Dynamic Interaction:** UI elements feel responsive and alive. Buttons feature subtle scaling and color transitions on hover. The chat bubbles use entrance animations to feel conversational.
- **Uninterrupted Flow:** Users should not have to leave the chat interface to view generated code, UI layouts, or diagrams.

## 2. Information Architecture
- **Authentication Guard:** A minimalist Landing Page gates the application.
- **Main Dashboard:**
  - **Sidebar (Left):** Chat history and session management.
  - **Primary View (Center):** The active conversation thread.
  - **Split-Pane (Right, Collapsible):** The Artifact Viewer, which opens dynamically only when an HTML or Mermaid artifact is requested.

## 3. Key Interaction States
- **Loading States:** While the agent is retrieving RAG context or waiting for the LLM API, a pulsating `Loader` component provides visual feedback.
- **Artifact Discovery:** When the LLM generates a recognized code block (HTML/Mermaid), the frontend hides the raw markdown and replaces it with an actionable "Open in Artifact Viewer" button inside the chat bubble.
- **Sandbox View Mode Toggle:** Inside the Artifact Viewer, users can toggle between a visual "Preview" state and a raw "Code" state to copy the underlying implementation.

## 4. Responsive Behavior
- **Grid to Flex:** On desktop, the layout utilizes CSS Grid for the split-pane experience (Chat + Artifact Viewer). On mobile devices (max-width: 768px), the Artifact Viewer collapses into a full-screen overlay or stacks vertically to preserve readability.
- **Sidebar Drawer:** The chat history sidebar transforms into a slide-out drawer on smaller screens.

## 5. Accessibility Considerations (a11y)
- **Contrast Ratios:** Text colors (e.g., `text-stone-300` on `bg-stone-900`) strictly adhere to WCAG AA contrast standards.
- **Semantic HTML:** Buttons use `<button type="button">`, inputs have associated labels/placeholders, and structural elements (`<aside>`, `<main>`, `<header>`) are used for screen readers.
- **Focus States:** Keyboard navigation is supported via high-visibility focus rings on interactive elements.

## 6. Design Decisions
- **Tailwind CDN in Sandbox:** To ensure high-fidelity UI previews, we inject the Tailwind CSS CDN directly into the isolated iframe's `<head>`. This allows the LLM to write raw HTML using Tailwind classes and have it render perfectly without needing a build step inside the sandbox.
- **Avoidance of Modals:** Instead of trapping artifacts in a modal that blocks the chat, we opted for a side-by-side split pane. This allows the user to continue chatting (e.g., "Make the button red instead") while actively watching the artifact update on the right.
