import React, { useState, useRef, useEffect } from 'react';
import { Bot, X, Send, Trash2, ExternalLink, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { askAssistant } from '@/services/api';
import styles from './FloatingAiAssistant.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{ title?: string; source?: string; snippet?: string }>;
}

export const FloatingAiAssistant: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        'Hello! I am the DGMS Coal Mine AI Safety Assistant. Ask me any regulatory question, colliery procedure, or physical safety observation.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const q = (textToSend || input).trim();
    if (!q || loading) return;

    const userMsg: Message = { role: 'user', content: q };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await askAssistant(q) as any;
      const assistantMsg: Message = {
        role: 'assistant',
        content: res?.content || res?.answer || 'Response generated from statutory safety corpus.',
        sources: res?.sources || [],
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'Unable to reach safety assistant service. Please verify that the local backend service is operational.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Conversation cleared. How can I assist you with colliery statutory compliance?',
      },
    ]);
  };

  const handleOpenFullPage = () => {
    setIsOpen(false);
    navigate('/assistant');
  };

  const sampleChips = [
    'Methane limits in return air?',
    'Who are you?',
    'Opencast bench slope limits',
    'Roof bolting requirements',
  ];

  return (
    <>
      {/* Floating Circular Trigger Button in Bottom Corner */}
      <button
        type="button"
        className={`${styles.floatingButton} ${isOpen ? styles.floatingButtonOpen : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title="Open DGMS AI Safety Assistant"
        aria-label="Open DGMS AI Safety Assistant"
      >
        {isOpen ? <X size={22} /> : <Bot size={24} />}
      </button>

      {/* Floating Chat Drawer */}
      {isOpen && (
        <div className={styles.chatPanel}>
          <div className={styles.chatHeader}>
            <div className={styles.headerTitle}>
              <span className={styles.statusIndicator} />
              <span>AI Safety Assistant</span>
            </div>
            <div className={styles.headerActions}>
              <button
                type="button"
                className={styles.headerBtn}
                onClick={handleOpenFullPage}
                title="Expand to Full Page"
              >
                <ExternalLink size={14} />
              </button>
              <button
                type="button"
                className={styles.headerBtn}
                onClick={handleClear}
                title="Clear Conversation"
              >
                <Trash2 size={14} />
              </button>
              <button
                type="button"
                className={styles.headerBtn}
                onClick={() => setIsOpen(false)}
                title="Close"
              >
                <X size={15} />
              </button>
            </div>
          </div>

          <div className={styles.messagesList}>
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`${styles.messageRow} ${
                  m.role === 'user' ? styles.messageUser : styles.messageAssistant
                }`}
              >
                <div
                  className={`${styles.messageBubble} ${
                    m.role === 'user' ? styles.bubbleUser : styles.bubbleAssistant
                  }`}
                >
                  {m.content}
                </div>

                {m.sources && m.sources.length > 0 && (
                  <div className={styles.sourcesBox}>
                    <div className={styles.sourcesTitle}>Statutory Citations:</div>
                    {m.sources.slice(0, 2).map((s, sIdx) => (
                      <div key={sIdx} style={{ marginBottom: '2px' }}>
                        &bull; {s.title || s.source}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className={`${styles.messageRow} ${styles.messageAssistant}`}>
                <div className={`${styles.messageBubble} ${styles.bubbleAssistant}`}>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                    <RefreshCw size={12} className="spin" />
                    Consulting CMR 2017 & DGMS regulations...
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick suggestions */}
          <div className={styles.chipsContainer}>
            {sampleChips.map((chip, idx) => (
              <button
                key={idx}
                type="button"
                className={styles.chip}
                onClick={() => handleSend(chip)}
                disabled={loading}
              >
                {chip}
              </button>
            ))}
          </div>

          {/* Input Area */}
          <form
            className={styles.inputArea}
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
          >
            <input
              type="text"
              className={styles.inputField}
              placeholder="Ask safety rule, e.g. methane limits..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              className={styles.sendButton}
              disabled={loading || !input.trim()}
              title="Send Message"
            >
              <Send size={14} />
            </button>
          </form>
        </div>
      )}
    </>
  );
};

export default FloatingAiAssistant;
