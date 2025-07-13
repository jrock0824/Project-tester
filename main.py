import os
import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from llm_engine import process_question

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASA</title>
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Forum&family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        /* Healing-centered font and color system */
        * {
            margin: 0 !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }

        /* Primary body font - Lato for calming readability */
        html, body, div, span, p, textarea, form {
            font-family: 'Lato', sans-serif !important;
        }

        /* Headers - Forum for elegance and trust */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Forum', serif !important;
        }

        /* Sidebar and navigation - Montserrat for clarity */
        nav, aside, .nav-item, .sidebar, .sidebar * {
            font-family: 'Montserrat', sans-serif !important;
        }

        /* Buttons and interactive elements - Montserrat */
        button {
            font-family: 'Montserrat', sans-serif !important;
        }

        /* Base styling with healing colors */
        body {
            font-family: 'Lato', sans-serif !important;
            background: #EEEEEE !important;
            color: #333333 !important;
            height: 100vh !important;
            overflow: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.6 !important;
        }

        html {
            font-family: 'Lato', sans-serif !important;
        }

        .sidebar svg {
            display: block !important;
            visibility: visible !important;
        }

        .sidebar.collapsed svg {
            display: block !important;
            visibility: visible !important;
        }

        .app {
            display: flex !important;
            height: 100vh !important;
        }

        .sidebar {
            width: 250px !important;
            background: #EEEEEE !important;
            border-right: 2px solid #90A17D !important;
            display: flex !important;
            flex-direction: column !important;
            transition: width 0.3s ease !important;
            position: relative !important;
            z-index: 10 !important;
            font-family: 'Montserrat', sans-serif !important;
        }

        .sidebar.collapsed {
            width: 64px !important;
        }

        .sidebar.collapsed .brand-title {
            display: none !important;
        }

        .sidebar.collapsed .brand-icon {
            display: none !important;
        }

        .sidebar.collapsed .nav-text {
            display: none !important;
        }

        .sidebar.collapsed .nav-item {
            justify-content: center !important;
            padding: 12px 8px !important;
        }

        .nav-text {
            white-space: nowrap !important;
        }

        .nav-text {
            white-space: nowrap !important;
        }

        .sidebar-header {
            padding: 20px !important;
            border-bottom: 1px solid #e2e8f0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
        }

        .sidebar-brand {
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
        }

        .brand-icon {
            width: 32px !important;
            height: 32px !important;
            background: #3b82f6 !important;
            border-radius: 8px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: white !important;
            font-size: 16px !important;
        }

        .brand-title {
            font-size: 18px !important;
            font-weight: 600 !important;
            color: #475569 !important;
        }

        .sidebar-toggle {
            background: none !important;
            border: none !important;
            padding: 8px !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            color: #829460 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 40px !important;
            height: 40px !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            font-family: 'Montserrat', sans-serif !important;
        }

        .sidebar-toggle:hover {
            background: rgba(144, 161, 125, 0.15) !important;
            color: #333333 !important;
        }

        .sidebar.collapsed .sidebar-toggle {
            margin: 0 auto !important;
        }

        .sidebar.collapsed .sidebar-header {
            justify-content: center !important;
            padding: 20px 12px !important;
        }

        .icon-close, .icon-menu {
            position: absolute !important;
            transition: all 0.3s ease !important;
        }

        .sidebar:not(.collapsed) .icon-close {
            opacity: 1 !important;
            transform: rotate(0deg) scale(1) !important;
        }

        .sidebar:not(.collapsed) .icon-menu {
            opacity: 0 !important;
            transform: rotate(90deg) scale(0.8) !important;
        }

        .sidebar.collapsed .icon-close {
            opacity: 0 !important;
            transform: rotate(-90deg) scale(0.8) !important;
        }

        .sidebar.collapsed .icon-menu {
            opacity: 1 !important;
            transform: rotate(0deg) scale(1) !important;
        }

        .sidebar-nav {
            padding: 20px !important;
            flex: 1 !important;
        }

        .nav-item {
            display: flex !important;
            align-items: center !important;
            gap: 14px !important;
            padding: 16px 12px !important;
            margin-bottom: 6px !important;
            border-radius: 12px !important;
            text-decoration: none !important;
            color: #829460 !important;
            transition: all 0.3s ease !important;
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 500 !important;
            font-size: 15px !important;
        }

        .nav-item svg {
            display: block !important;
            visibility: visible !important;
            flex-shrink: 0 !important;
            width: 22px !important;
            height: 22px !important;
        }

        .nav-item:hover {
            background: rgba(144, 161, 125, 0.1) !important;
            color: #333333 !important;
            text-decoration: none !important;
            transform: translateX(4px) !important;
        }

        .nav-item.active {
            background: #90A17D !important;
            color: #EEEEEE !important;
            box-shadow: 0 2px 8px rgba(144, 161, 125, 0.3) !important;
        }

        .main-content {
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
        }

        .chat-header {
            padding: 24px !important;
            border-bottom: 2px solid #90A17D !important;
            background: #EEEEEE !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
        }

        .chat-info {
            display: flex !important;
            align-items: center !important;
            gap: 16px !important;
        }

        .chat-avatar {
            width: 48px !important;
            height: 48px !important;
            background: #FFE1E1 !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #829460 !important;
            font-size: 20px !important;
            box-shadow: 0 2px 8px rgba(255, 225, 225, 0.4) !important;
        }

        .chat-title {
            font-size: 18px !important;
            font-weight: 600 !important;
            margin-bottom: 4px !important;
        }

        .chat-subtitle {
            color: #334155 !important;
            font-weight: 500 !important;
        }

        .messages-container {
            flex: 1 !important;
            padding: 24px !important;
            overflow-y: auto !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 24px !important;
            background: #EEEEEE !important;
        }

        .message {
            display: flex !important;
            gap: 12px !important;
            align-items: flex-start !important;
        }

        .message.user {
            flex-direction: row-reverse !important;
        }

        .message-avatar {
            width: 32px !important;
            height: 32px !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            flex-shrink: 0 !important;
            font-size: 14px !important;
        }

        .ai-avatar {
            background: #FFE1E1 !important;
            color: #829460 !important;
        }

        .ai-avatar.friendly-persona {
            background: #FFA500 !important;
            color: #EEEEEE !important;
        }

        .ai-avatar.humorous-persona {
            background: #FFD700 !important;
            color: #333333 !important;
        }

        .user-avatar {
            background: #90A17D !important;
            color: #EEEEEE !important;
        }

        .message-bubble {
            max-width: 75% !important;
            padding: 16px 20px !important;
            border-radius: 20px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
            line-height: 1.7 !important;
            font-family: 'Lato', sans-serif !important;
            font-size: 15px !important;
        }

        .ai-bubble {
            background: #FFE1E1 !important;
            color: #333333 !important;
            border-bottom-left-radius: 6px !important;
            border: 1px solid rgba(255, 225, 225, 0.6) !important;
        }

        .user-bubble {
            background: #90A17D !important;
            color: #EEEEEE !important;
            border-bottom-right-radius: 6px !important;
        }

        .message-bubble p {
            margin: 0 0 12px 0 !important;
            font-family: 'Lato', sans-serif !important;
            font-weight: 400 !important;
        }

        .message-bubble p:last-child {
            margin-bottom: 0 !important;
        }

        .message-bubble h1, .message-bubble h2, .message-bubble h3, .message-bubble h4 {
            margin: 20px 0 12px 0 !important;
            font-family: 'Forum', serif !important;
            font-weight: 400 !important;
            color: #829460 !important;
            letter-spacing: 0.3px !important;
        }

        .message-bubble h1 { font-size: 22px !important; }
        .message-bubble h2 { font-size: 20px !important; }
        .message-bubble h3 { font-size: 18px !important; }
        .message-bubble h4 { font-size: 16px !important; }

        .message-bubble h1:first-child,
        .message-bubble h2:first-child,
        .message-bubble h3:first-child,
        .message-bubble h4:first-child {
            margin-top: 0 !important;
        }

        .message-bubble ul, .message-bubble ol {
            margin: 16px 0 !important;
            padding-left: 24px !important;
        }

        .message-bubble li {
            margin: 8px 0 !important;
            font-family: 'Lato', sans-serif !important;
            line-height: 1.6 !important;
        }

        .message-bubble strong {
            color: #829460 !important;
            font-weight: 700 !important;
        }

        .chat-input {
            padding: 20px !important;
            border-top: 1px solid #90A17D !important;
            background: rgba(255, 255, 255, 0.8) !important;
            backdrop-filter: blur(10px) !important;
        }

        .input-form {
            display: flex !important;
            gap: 12px !important;
            padding: 12px 16px !important;
            border: 1px solid #90A17D !important;
            border-radius: 24px !important;
            background: white !important;
            transition: all 0.3s ease !important;
        }

        .input-form:focus-within {
            border-color: #90A17D !important;
            box-shadow: 0 0 0 3px rgba(130, 148, 96, 0.5) !important;
        }

        .message-input {
            flex: 1 !important;
            border: none !important;
            outline: none !important;
            background: transparent !important;
            font-family: 'Lato', sans-serif !important;
            font-size: 15px !important;
            resize: none !important;
            min-height: 20px !important;
            max-height: 100px !important;
        }

        .message-input:focus {
            outline: none !important;
            border: none !important;
        }

        .message-input::placeholder {
            color: #94a3b8 !important;
        }

        .send-btn {
            width: 40px !important;
            height: 40px !important;
            border: none !important;
            border-radius: 50% !important;
            background: #90A17D !important;
            color: #EEEEEE !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.3s ease !important;
            font-family: 'Montserrat', sans-serif !important;
            box-shadow: 0 2px 8px rgba(144, 161, 125, 0.3) !important;
        }

        .send-btn:hover:not(:disabled) {
            background: #829460 !important;
            transform: scale(1.08) translateY(-1px) !important;
            box-shadow: 0 4px 16px rgba(144, 161, 125, 0.4) !important;
        }

        .send-btn:disabled {
            background: rgba(144, 161, 125, 0.3) !important;
            cursor: not-allowed !important;
            transform: none !important;
            box-shadow: none !important;
        }

        .typing {
            font-style: italic !important;
            color: #64748b !important;
        }

        .persona-controls {
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
        }

        .persona-selector {
            position: relative !important;
        }

        .persona-button {
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
            padding: 16px 20px !important;
            background: white !important;
            border: 2px solid #90A17D !important;
            border-radius: 16px !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            min-width: 300px !important;
            font-family: 'Montserrat', sans-serif !important;
            box-shadow: 0 2px 8px rgba(144, 161, 125, 0.1) !important;
        }

        .persona-button:hover {
            background: #FFE1E1 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(144, 161, 125, 0.2) !important;
        }

        .persona-icon {
            width: 20px !important;
            height: 20px !important;
            flex-shrink: 0 !important;
        }

        .persona-text {
            flex: 1 !important;
            text-align: left !important;
        }

        .persona-name {
            font-family: 'Forum', serif !important;
            font-weight: 400 !important;
            font-size: 16px !important;
            margin-bottom: 4px !important;
            color: #333333 !important;
            letter-spacing: 0.3px !important;
        }

        .persona-description {
            font-family: 'Lato', sans-serif !important;
            font-size: 13px !important;
            color: #829460 !important;
            line-height: 1.4 !important;
        }

        .chevron {
            width: 16px !important;
            height: 16px !important;
            transition: transform 0.2s !important;
        }

        .persona-selector.open .chevron {
            transform: rotate(180deg) !important;
        }

        .persona-dropdown {
            position: absolute !important;
            top: 100% !important;
            left: 0 !important;
            right: 0 !important;
            margin-top: 8px !important;
            background: white !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
            z-index: 50 !important;
            overflow: hidden !important;
            opacity: 0 !important;
            visibility: hidden !important;
            transform: translateY(-8px) !important;
            transition: all 0.2s ease !important;
        }

        .persona-selector.open .persona-dropdown {
            opacity: 1 !important;
            visibility: visible !important;
            transform: translateY(0) !important;
        }

        .persona-option {
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
            padding: 12px 16px !important;
            cursor: pointer !important;
            transition: background 0.2s !important;
            border: none !important;
            background: none !important;
            width: 100% !important;
            text-align: left !important;
            font-family: 'Inter', sans-serif !important;
        }

        .persona-option:hover {
            background: #f8fafc !important;
        }

        .clear-btn {
            background: none !important;
            border: none !important;
            padding: 8px !important;
            border-radius: 6px !important;
            cursor: pointer !important;
            color: #64748b !important;
            transition: all 0.2s !important;
        }

        .clear-btn:hover {
            background: #f1f5f9 !important;
            color: #334155 !important;
        }

        .suggested-prompts {
            padding: 24px !important;
            border-top: 1px solid #90A17D !important;
            background: #EEEEEE !important;
        }

        .prompts-title {
            font-family: 'Forum', serif !important;
            font-size: 18px !important;
            color: #829460 !important;
            text-align: center !important;
            margin-bottom: 20px !important;
            font-weight: 400 !important;
            letter-spacing: 0.3px !important;
        }

        .prompts-grid {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 16px !important;
        }

        .prompt-button {
            padding: 16px 20px !important;
            background: #FFE1E1 !important;
            border: 1px solid rgba(255, 225, 225, 0.6) !important;
            border-radius: 16px !important;
            color: #333333 !important;
            font-size: 14px !important;
            text-align: left !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            line-height: 1.5 !important;
            font-family: 'Lato', sans-serif !important;
            font-weight: 400 !important;
            box-shadow: 0 2px 8px rgba(255, 225, 225, 0.2) !important;
        }

        .prompt-button:hover {
            background: #90A17D !important;
            color: #EEEEEE !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 16px rgba(144, 161, 125, 0.25) !important;
        }

        @media (max-width: 768px) {
            .prompts-grid {
                grid-template-columns: 1fr !important;
            }
        }
    </style>
</head>
<body>
    <div class="app">
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-brand">
                    <div class="brand-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                            <path d="m2 17 10 5 10-5"/>
                            <path d="m2 12 10 5 10-5"/>
                        </svg>
                    </div>
                    <h1 class="brand-title">Asa</h1>
                </div>
                <button class="sidebar-toggle" onclick="toggleSidebar()" id="sidebarToggleBtn">
                    <svg class="icon-close" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 6 6 18"/>
                        <path d="m6 6 12 12"/>
                    </svg>
                    <svg class="icon-menu" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="4" x2="20" y1="6" y2="6"/>
                        <line x1="4" x2="20" y1="12" y2="12"/>
                        <line x1="4" x2="20" y1="18" y2="18"/>
                    </svg>
                </button>
            </div>
            <nav class="sidebar-nav">
                <a href="#" class="nav-item active">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>
                    </svg>
                    <span class="nav-text">Chat</span>
                </a>
                <a href="#" class="nav-item">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
                    </svg>
                    <span class="nav-text">Mood Check-in</span>
                </a>
                <a href="#" class="nav-item">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                    </svg>
                    <span class="nav-text">Resources</span>
                </a>
                <a href="#" class="nav-item">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 3v5h5"/>
                        <path d="M3 8c0-5.5 4.5-10 10-10s10 4.5 10 10"/>
                        <path d="M21 21v-5h-5"/>
                        <path d="M21 16c0 5.5-4.5 10-10 10s-10-4.5-10-10"/>
                    </svg>
                    <span class="nav-text">Progress</span>
                </a>
            </nav>
        </aside>

        <main class="main-content">
            <div class="chat-header">
                <div class="chat-info">
                    <div class="chat-avatar">🫂</div>
                    <div>
                        <h2 class="chat-title">Parenting Support</h2>
                        <p class="chat-subtitle">Your AI parenting companion</p>
                    </div>
                </div>
                <div class="persona-controls">
                    <div class="persona-selector" id="personaSelector">
                        <button class="persona-button" id="personaButton" onclick="togglePersonaDropdown(event)">
                            <svg class="persona-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #2196f3;">
                                <path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                                <rect width="20" height="14" x="2" y="6" rx="2"/>
                            </svg>
                            <div class="persona-text">
                                <div class="persona-name">Professional</div>
                                <div class="persona-description">Clear and structured guidance with expert advice</div>
                            </div>
                            <svg class="chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="m6 9 6 6 6-6"/>
                            </svg>
                        </button>
                        <div class="persona-dropdown" id="personaDropdown">
                            <div class="persona-option" onclick="selectPersona('professional')">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #2196f3;">
                                    <path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                                    <rect width="20" height="14" x="2" y="6" rx="2"/>
                                </svg>
                                <div class="persona-text">
                                    <div class="persona-name">Professional</div>
                                    <div class="persona-description">Clear and structured guidance with expert advice</div>
                                </div>
                            </div>
                            <div class="persona-option" onclick="selectPersona('friendly')">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #4caf50;">
                                    <circle cx="12" cy="12" r="10"/>
                                    <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                                    <line x1="9" x2="9.01" y1="9" y2="9"/>
                                    <line x1="15" x2="15.01" y1="9" y2="9"/>
                                </svg>
                                <div class="persona-text">
                                    <div class="persona-name">Friendly</div>
                                    <div class="persona-description">Warm and conversational, like talking to a trusted friend</div>
                                </div>
                            </div>
                            <div class="persona-option" onclick="selectPersona('humorous')">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #ff9800;">
                                    <circle cx="12" cy="12" r="10"/>
                                    <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                                    <line x1="9" x2="9.01" y1="9" y2="9"/>
                                    <line x1="15" x2="15.01" y1="9" y2="9"/>
                                    <path d="M7 17c0-2.5 1.5-5 5-5s5 2.5 5 5"/>
                                </svg>
                                <div class="persona-text">
                                    <div class="persona-name">Humorous</div>
                                    <div class="persona-description">Gentle humor to help ease tension and stress</div>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>

            <div class="messages-container" id="messages">
                <div class="message">
                    <div class="message-avatar ai-avatar">🤖</div>
                    <div class="message-bubble ai-bubble">
                        <p>Hello! I'm here to be your supportive companion in navigating family relationships. Whether you're a parent, caregiver, or adult child facing challenges with your own parents, I understand how overwhelming family dynamics can be—especially when trauma or difficult emotions are involved.</p>
                        <p>I'm here to listen, support, and help you through these moments. How are things going for you today?</p>
                    </div>
                </div>
            </div>

            <div class="suggested-prompts" id="suggestedPrompts">
                <p class="prompts-title">Here are some ways I can help you get started:</p>
                <div class="prompts-grid">
                    <button class="prompt-button" onclick="selectPrompt('How can I support my child when they\'re having an emotional meltdown?')">
                        How can I support my child when they're having an emotional meltdown?
                    </button>
                    <button class="prompt-button" onclick="selectPrompt('What are some healthy ways to set boundaries with my parents?')">
                        What are some healthy ways to set boundaries with my parents?
                    </button>
                    <button class="prompt-button" onclick="selectPrompt('How do I talk to my child about difficult family experiences?')">
                        How do I talk to my child about difficult family experiences?
                    </button>
                    <button class="prompt-button" onclick="selectPrompt('What are signs that my child might be dealing with unresolved trauma?')">
                        What are signs that my child might be dealing with unresolved trauma?
                    </button>
                </div>
            </div>

            <div class="chat-input">
                <form class="input-form" id="chatForm" onsubmit="return sendMessage(event)">
                    <textarea
                        class="message-input"
                        id="messageInput"
                        placeholder="Share what's on your mind about parenting..."
                        rows="1"
                        oninput="adjustHeight(this); updateSendButton()"
                        onkeydown="handleKeyDown(event)"
                    ></textarea>
                    <button type="submit" class="send-btn" id="sendBtn" disabled>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M7 7h10v10"/>
                            <path d="M7 17 17 7"/>
                        </svg>
                    </button>
                </form>
            </div>
        </main>
    </div>

    <script>
        let isTyping = false;
        let currentPersona = 'professional';

        function adjustHeight(textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
        }

        function updateSendButton() {
            const input = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = !input.value.trim() || isTyping;
        }

        function handleKeyDown(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage(event);
            }
        }

        function toggleSidebar() {
            const sidebar = document.querySelector('.sidebar');
            sidebar.classList.toggle('collapsed');
        }

        function togglePersonaDropdown(event) {
            event.stopPropagation();
            const selector = document.getElementById('personaSelector');
            selector.classList.toggle('open');
        }

        function selectPersona(persona) {
            currentPersona = persona;

            const personas = {
                professional: {
                    name: 'Professional',
                    description: 'Clear and structured guidance with expert advice',
                    icon: `<svg class="persona-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #2196f3;"><path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect width="20" height="14" x="2" y="6" rx="2"/></svg>`
                },
                friendly: {
                    name: 'Friendly',
                    description: 'Warm and conversational, like talking to a trusted friend',
                    icon: `<svg class="persona-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #4caf50;"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" x2="9.01" y1="9" y2="9"/><line x1="15" x2="15.01" y1="9" y2="9"/></svg>`
                },
                humorous: {
                    name: 'Humorous',
                    description: 'Gentle humor to help ease tension and stress',
                    icon: `<svg class="persona-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #ff9800;"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" x2="9.01" y1="9" y2="9"/><line x1="15" x2="15.01" y1="9" y2="9"/><path d="M7 17c0-2.5 1.5-5 5-5s5 2.5 5 5"/></svg>`
                }
            };

            const selected = personas[persona];
            const button = document.getElementById('personaButton');

            // Force update the button content
            const iconElement = button.querySelector('.persona-icon');
            const nameElement = button.querySelector('.persona-name');
            const descElement = button.querySelector('.persona-description');

            if (iconElement && nameElement && descElement) {
                iconElement.outerHTML = selected.icon;
                nameElement.textContent = selected.name;
                descElement.textContent = selected.description;

                // Force a re-render
                button.style.display = 'none';
                button.offsetHeight; // Trigger reflow
                button.style.display = 'flex';
            }

            document.getElementById('personaSelector').classList.remove('open');
        }

        // Close persona dropdown when clicking outside
        document.addEventListener('click', function() {
            document.getElementById('personaSelector').classList.remove('open');
        });

        async function sendMessage(event) {
            if (event) event.preventDefault();

            const input = document.getElementById('messageInput');
            const message = input.value.trim();

            if (!message || isTyping) return false;

            // Add user message
            addMessage(message, 'user');

            // Clear input
            input.value = '';
            adjustHeight(input);
            updateSendButton();

            // Show typing
            showTyping();

            try {
                const response = await fetch(`/ask?question=${encodeURIComponent(message)}&persona=${currentPersona}`);
                const data = await response.json();

                hideTyping();

                if (data.error) {
                    addMessage('Sorry, I encountered an error: ' + data.error, 'ai');
                } else {
                    addMessage(data.answer, 'ai');
                }
            } catch (error) {
                hideTyping();
                addMessage('Sorry, I am having trouble connecting right now. Please try again.', 'ai');
            }

            return false;
        }

        function addMessage(content, sender) {
            const container = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;

            const avatar = sender === 'user' ? '👤' : '🤖';
            const bubbleClass = sender === 'user' ? 'user-bubble' : 'ai-bubble';
            let avatarClass = sender === 'user' ? 'user-avatar' : 'ai-avatar';

            // Add persona-specific styling for AI avatar
            if (sender === 'ai') {
                if (currentPersona === 'friendly') {
                    avatarClass += ' friendly-persona';
                } else if (currentPersona === 'humorous') {
                    avatarClass += ' humorous-persona';
                }
            }

            let formattedContent = content;
            if (sender === 'ai') {
                formattedContent = formatMarkdown(content);
            } else {
                formattedContent = `<p>${escapeHtml(content)}</p>`;
            }

            messageDiv.innerHTML = `
                <div class="message-avatar ${avatarClass}">${avatar}</div>
                <div class="message-bubble ${bubbleClass}">
                    ${formattedContent}
                </div>
            `;

            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }

        function formatMarkdown(text) {
            let html = text;

            // Remove code blocks and markdown artifacts
            html = html.replace(/```[\\s\\S]*?```/g, '');

            // Handle markdown headers (including ####)
            html = html.replace(/^#### (.*$)/gm, '<h4><strong>$1</strong></h4>');
            html = html.replace(/^### (.*$)/gm, '<h3><strong>$1</strong></h3>');
            html = html.replace(/^## (.*$)/gm, '<h2><strong>$1</strong></h2>');
            html = html.replace(/^# (.*$)/gm, '<h1><strong>$1</strong></h1>');

            // Handle headers with underlines
            html = html.replace(/^(.+)\\n=+\\s*$/gm, '<h2><strong>$1</strong></h2>');
            html = html.replace(/^(.+)\\n-+\\s*$/gm, '<h3><strong>$1</strong></h3>');

            // Bold and italic
            html = html.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
            html = html.replace(/\\*(.*?)\\*/g, '<em>$1</em>');

            // Handle numbered lists first
            html = html.replace(/^(\\d+)\\. (.+)$/gm, '<li class="numbered">$2</li>');

            // Handle bullet points
            html = html.replace(/^\\* (.+)$/gm, '<li class="bullet">$1</li>');
            html = html.replace(/^- (.+)$/gm, '<li class="bullet">$1</li>');

            // Wrap consecutive numbered items in ol
            html = html.replace(/((<li class="numbered">[^<]*<\\/li>\\s*)+)/g, '<ol>$1</ol>');
            html = html.replace(/<li class="numbered">/g, '<li>');

            // Wrap consecutive bullet items in ul
            html = html.replace(/((<li class="bullet">[^<]*<\\/li>\\s*)+)/g, '<ul>$1</ul>');
            html = html.replace(/<li class="bullet">/g, '<li>');

            // Clean up multiple consecutive ul/ol tags
            html = html.replace(/<\\/ul>\\s*<ul>/g, '');
            html = html.replace(/<\\/ol>\\s*<ol>/g, '');

            // Handle paragraphs - split by double newlines
            const sections = html.split(/\\n\\s*\\n/);
            html = sections.map(section => {
                section = section.trim();
                if (!section) return '';

                // Don't wrap headers, lists, or already wrapped content
                if (section.match(/^<[h1-6]|^<[uo]l|^<li/)) {
                    return section;
                }

                // Split by single newlines and wrap each line in p tags
                const lines = section.split(/\\n/).filter(line => line.trim());
                return lines.map(line => line.trim() ? `<p>${line.trim()}</p>` : '').join('');
            }).filter(p => p).join('');

            return html;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function showTyping() {
            isTyping = true;
            updateSendButton();

            const container = document.getElementById('messages');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message typing-indicator';

            let avatarClass = 'ai-avatar';
            if (currentPersona === 'friendly') {
                avatarClass += ' friendly-persona';
            } else if (currentPersona === 'humorous') {
                avatarClass += ' humorous-persona';
            }

            typingDiv.innerHTML = `
                <div class="message-avatar ${avatarClass}">🤖</div>
                <div class="message-bubble ai-bubble typing">
                    <p>Thinking...</p>
                </div>
            `;

            container.appendChild(typingDiv);
            container.scrollTop = container.scrollHeight;
        }

        function hideTyping() {
            isTyping = false;
            updateSendButton();

            const typingEl = document.querySelector('.typing-indicator');
            if (typingEl) typingEl.remove();
        }

        function clearChat() {
            const container = document.getElementById('messages');
            container.innerHTML = `
                <div class="message">
                    <div class="message-avatar ai-avatar">🤖</div>
                    <div class="message-bubble ai-bubble">
                        <p>Hello! I'm here to be your supportive parenting companion. Whether you're a single parent, caregiver, or facing challenging situations with your child, I understand that parenting can be overwhelming - especially when dealing with trauma-informed care or unexpected situations.</p>
                        <p>I'm here to listen, support, and help you navigate these moments. How are you and your child doing today?</p>
                    </div>
                </div>
            `;
        }

        function selectPrompt(promptText) {
            const messageInput = document.getElementById('messageInput');
            const suggestedPrompts = document.getElementById('suggestedPrompts');

            // Populate the input field
            messageInput.value = promptText;

            // Hide suggested prompts
            suggestedPrompts.style.display = 'none';

            // Adjust textarea height and enable send button
            adjustHeight(messageInput);
            updateSendButton();

            // Focus on the input
            messageInput.focus();
        }

        // Initialize
        updateSendButton();
    </script>
</body>
</html>""")

@app.get("/ask")
async def ask_parenting_advice(question: str, persona: str):
    logging.info(f"Received question: {question}")
    logging.info(f"Selected persona: {persona}")

    if not question.strip():
        return {"error": "Question cannot be empty."}
    if persona not in ["friendly", "professional", "humorous"]:
        return {"error": f"Invalid persona: {persona}. Choose from 'friendly', 'professional', or 'humorous'."}

    try:
        response = process_question(question, persona)
        return {"answer": response}
    except Exception as e:
        logging.error(f"Error processing question: {e}")
        return {"error": "An error occurred while processing your question."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)