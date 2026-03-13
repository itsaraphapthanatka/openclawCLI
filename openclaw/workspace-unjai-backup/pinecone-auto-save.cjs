#!/usr/bin/env node
/**
 * Auto-save conversations to Pinecone
 * ใช้เก็บบทสนทนาอัตโนมัติ
 */

require('dotenv').config();

const API_KEY = process.env.PINECONE_API_KEY;
const INDEX_NAME = 'aunjai-knowledge';

// Simple embedding (384 dim)
function embed(text) {
  const vec = new Array(384).fill(0);
  for (let i = 0; i < text.length; i++) {
    vec[i % 384] += (text.charCodeAt(i) % 100) / 100;
  }
  const mag = Math.sqrt(vec.reduce((s, v) => s + v * v, 0));
  return vec.map(v => v / (mag || 1));
}

// Get index host (cache)
let cachedHost = null;
async function getHost() {
  if (cachedHost) return cachedHost;
  const resp = await fetch('https://api.pinecone.io/indexes', {
    headers: { 'Api-Key': API_KEY }
  });
  const data = await resp.json();
  cachedHost = data.indexes.find(i => i.name === INDEX_NAME)?.host;
  return cachedHost;
}

// Save to Pinecone
async function saveToPinecone(id, text, metadata = {}) {
  const host = await getHost();
  
  const vector = {
    id: `${id}-${Date.now()}`,
    values: embed(text),
    metadata: {
      text: text.substring(0, 1500),
      ...metadata,
      savedAt: new Date().toISOString()
    }
  };
  
  const resp = await fetch(`https://${host}/vectors/upsert`, {
    method: 'POST',
    headers: {
      'Api-Key': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ vectors: [vector], namespace: '' })
  });
  
  if (!resp.ok) throw new Error(await resp.text());
  return vector.id;
}

// Save conversation
async function saveConversation(conversationId, messages) {
  // Combine messages into one text
  const fullText = messages.map(m => `${m.role}: ${m.content}`).join('\n\n');
  
  const id = await saveToPinecone(
    `conv-${conversationId}`,
    fullText,
    {
      type: 'conversation',
      conversationId,
      messageCount: messages.length,
      sources: messages.map(m => m.source || 'chat')
    }
  );
  
  console.log(`💾 Saved conversation: ${id}`);
  return id;
}

// Save single message
async function saveMessage(messageId, role, content, extra = {}) {
  const id = await saveToPinecone(
    `msg-${messageId}`,
    `${role}: ${content}`,
    {
      type: 'message',
      role,
      ...extra
    }
  );
  
  console.log(`💾 Saved message: ${id}`);
  return id;
}

// Search memory
async function searchMemory(query, topK = 5) {
  const host = await getHost();
  
  const resp = await fetch(`https://${host}/query`, {
    method: 'POST',
    headers: {
      'Api-Key': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      vector: embed(query),
      topK,
      includeMetadata: true
    })
  });
  
  return await resp.json();
}

module.exports = {
  saveToPinecone,
  saveConversation,
  saveMessage,
  searchMemory,
  embed
};
