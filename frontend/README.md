# KozakEye OS: Smart Kitchen AI (Frontend)

This is the frontend application for the **Smart Kitchen AI** ecosystem, providing the "KozakEye" Spatial OS interface. It is a modern Single Page Application (SPA) built with Vue 3 and Vite, designed to communicate with the FastAPI backend via Server-Sent Events (SSE).

## 🛠 Tech Stack

- **Framework:** Vue 3 (Composition API & `<script setup>`)
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **State Management:** Pinia
- **Localization:** Vue I18n (`en`, `uk`)

## ✨ Key Features

- **Spatial UI:** 2.5D draggable widgets (Interaction Zone, Fridge Inventory, Advice Display).
- **Real-time Streaming:** Native SSE client (`useChefStream.js`) for typewriter-style AI responses.
- **Polymorphic Artifacts:** Dynamic rendering of Recipes, Analytics, and Shopping Lists with 3D flip animations.
- **Smart Vision:** Client-side canvas preprocessing for receipt scanning before sending to Gemini Vision.

## 🚀 Getting Started

```bash
# Install dependencies
npm install

# Start the development server (runs on localhost:5173 by default)
npm run dev
```

For backend setup, please refer to the root project documentation.
