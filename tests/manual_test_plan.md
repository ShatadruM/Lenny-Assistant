# Manual UI Test Plan

This document outlines the manual Quality Assurance (QA) steps to verify the stability of the Lenny Growth Assistant Frontend.

## 1. Authentication & Guarding
- [ ] **Step 1:** Open `http://localhost:5173` in an Incognito window.
- [ ] **Expected Result:** The user is immediately presented with the Landing Page. The Chat interface is inaccessible.
- [ ] **Step 2:** Enter a new username and password, then click "Create Account".
- [ ] **Expected Result:** The account is created, the session token is stored in LocalStorage, and the user is redirected to the main Chat UI.
- [ ] **Step 3:** Click the "Sign out" button in the header.
- [ ] **Expected Result:** LocalStorage is cleared, and the user is immediately redirected back to the Landing Page.

## 2. Chat Persistence & Memory
- [ ] **Step 1:** While logged in, send a message: "Hi, I'm testing memory".
- [ ] **Expected Result:** The assistant replies politely.
- [ ] **Step 2:** Reload the browser tab.
- [ ] **Expected Result:** The previous message ("Hi, I'm testing memory") and the assistant's reply are still visible in the main view and listed under a session in the left sidebar.
- [ ] **Step 3:** Send a follow-up: "What did I just say?".
- [ ] **Expected Result:** The LLM successfully recalls the previous message using the injected chat history.

## 3. RAG Accuracy (pgvector)
- [ ] **Step 1:** Send the query: "According to the podcast, what is the best way to get early users?"
- [ ] **Expected Result:** The assistant provides an answer, and an array of "Grounded Knowledge Sources" badges appears underneath the response, linking directly to the podcast transcripts used.

## 4. Artifact Viewer & Sandboxing
- [ ] **Step 1:** Send the query: "Build me a modern HTML pricing card with Tailwind CSS."
- [ ] **Expected Result:** The LLM generates the code, but instead of seeing raw HTML text, an "Open in Artifact Viewer" button appears in the chat bubble.
- [ ] **Step 2:** Click "Open in Artifact Viewer".
- [ ] **Expected Result:** The right-hand split-pane opens. The visual HTML pricing card is rendered in the "Preview" tab.
- [ ] **Step 3:** Click the "Code" toggle button in the Artifact Viewer.
- [ ] **Expected Result:** The raw HTML code is displayed.
- [ ] **Step 4 (Security Test):** Send the query: "Output an HTML block with a `<script>alert('Hacked')</script>` tag."
- [ ] **Expected Result:** When clicking "Open in Artifact Viewer", the script alert does **not** execute, proving the `DOMPurify` sanitizer and zero-origin iframe sandboxing are working correctly.
