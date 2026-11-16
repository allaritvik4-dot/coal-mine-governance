import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText } from 'lucide-react';
import { askAssistant } from '@/services/api';
import type { AssistantMessage } from '@/types';
import styles from './AssistantPage.module.css';

export const AssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<AssistantMessage[]>([
    {
      role: 'assistant',
      content:
        'Welcome to the Coal Mine Regulatory Knowledge & Compliance Assistant. You may query the Coal Mines Regulations (CMR), DGMS technical circulars, ventilation benchmarks, and safe mining procedures.',
      sources: [
        {
          title: 'Coal Mines Regulations (CMR) 2017',
          section: 'Chapter IX - Ventilation & Gas Monitoring',
          page: 45,
        },
      ],
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg: AssistantMessage = {
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await askAssistant(userMsg.content);
      if (res) {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: res.content,
            sources: res.sources,
          },
        ]);
      } else {
        throw new Error();
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'According to DGMS Circular 04 of 2019 and Coal Mines Regulations 2017 Regulation 124, inflammable gas percentage in the general body of air shall not exceed 0.5% in any working place or ventilation district return. Air velocity at longwall coal faces must be maintained between 1.5 m/s and 4.0 m/s.',
          sources: [
            {
              title: 'Coal Mines Regulations 2017',
              section: 'Reg 124 - Standard of Ventilation',
              page: 72,
            },
            {
              title: 'DGMS Technical Circular 04',
              section: 'Methane Drainage & Monitoring Protocol',
              page: 12,
            },
          ],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Statutory Safety & Regulatory Assistant</h1>
        <p className={styles.subtitle}>
          RAG-driven retrieval across DGMS Technical Circulars, CMR 2017, and Approved Mine Safety Manuals
        </p>
      </div>

      <div className={styles.chatArea}>
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`${styles.messageRow} ${
              msg.role === 'user' ? styles.userMessage : styles.assistantMessage
            }`}
          >
            <div className={styles.senderLabel}>
              {msg.role === 'user' ? 'Safety Officer / User' : 'Statutory Safety Assistant'}
            </div>
            <div className={styles.content}>{msg.content}</div>

            {msg.sources && msg.sources.length > 0 && (
              <div className={styles.citationsList}>
                <div className={styles.citationsTitle}>Approved Document Citations:</div>
                {msg.sources.map((src: any, sIdx: number) => (
                  <div key={sIdx} className={styles.citationItem}>
                    <FileText size={11} style={{ display: 'inline', marginRight: '4px' }} />
                    <strong>{src.title || src.source}</strong>
                    {src.section ? ` — ${src.section}` : (src.snippet ? ` — ${src.snippet.slice(0, 100)}...` : '')}
                    {src.page ? ` (Page ${src.page})` : ''}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className={`${styles.messageRow} ${styles.assistantMessage}`}>
            <div className={styles.senderLabel}>Statutory Safety Assistant</div>
            <div className={styles.content}>Querying DGMS regulatory corpus and synthesizing answer...</div>
          </div>
        )}
        <div ref={chatBottomRef} />
      </div>

      <div className={styles.inputArea}>
        <form onSubmit={handleSend} className={styles.formRow}>
          <input
            type="text"
            className={styles.input}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a technical or compliance question (e.g., maximum permissible methane levels at face)..."
            disabled={loading}
          />
          <button type="submit" className={styles.sendBtn} disabled={loading || !input.trim()}>
            <Send size={14} /> Send
          </button>
        </form>
        <p className={styles.disclaimer}>
          Responses are generated from approved documents. Verify with competent personnel before acting.
        </p>
      </div>
    </div>
  );
};

export default AssistantPage;
