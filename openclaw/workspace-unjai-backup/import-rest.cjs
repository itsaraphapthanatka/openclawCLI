#!/usr/bin/env node
/**
 * Import memory files to Pinecone using REST API
 */

const { readFileSync } = require('fs');
require('dotenv').config();

const API_KEY = process.env.PINECONE_API_KEY;
const INDEX_NAME = 'aunjai-knowledge';

// Generate simple embedding (384 dimensions)
function generateEmbedding(text) {
  const vector = new Array(384).fill(0);
  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    vector[i % 384] += (char % 100) / 100;
  }
  // Normalize
  const mag = Math.sqrt(vector.reduce((s, v) => s + v * v, 0));
  return vector.map(v => v / (mag || 1));
}

// Split text into chunks
function chunkText(text, size = 800) {
  const chunks = [];
  for (let i = 0; i < text.length; i += size) {
    const chunk = text.slice(i, i + size).trim();
    if (chunk.length > 100) chunks.push(chunk);
  }
  return chunks;
}

// Upsert to Pinecone
async function upsertVectors(vectors) {
  // Get index host
  const controlResp = await fetch('https://api.pinecone.io/indexes', {
    headers: { 'Api-Key': API_KEY }
  });
  const indexes = await controlResp.json();
  const index = indexes.indexes.find(i => i.name === INDEX_NAME);
  
  const resp = await fetch(`https://${index.host}/vectors/upsert`, {
    method: 'POST',
    headers: {
      'Api-Key': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ vectors, namespace: '' })
  });
  
  if (!resp.ok) throw new Error(await resp.text());
  return await resp.json();
}

// Import all files
async function importAll() {
  const files = [
    'SOUL.md', 'IDENTITY.md', 'AGENTS.md', 'USER.md',
    'TOOLS.md', 'BOOTSTRAP.md', 'HEARTBEAT.md', 'MEMORY.md'
  ];
  
  let total = 0;
  
  for (const filename of files) {
    try {
      console.log(`\n📖 ${filename}...`);
      const content = readFileSync(`./${filename}`, 'utf-8');
      const chunks = chunkText(content, 600);
      console.log(`   ${chunks.length} chunks`);
      
      // Prepare vectors for this file
      const vectors = chunks.map((chunk, i) => ({
        id: `${filename.replace('.md', '')}-${i}`,
        values: generateEmbedding(chunk),
        metadata: {
          text: chunk.substring(0, 1200),
          source: filename,
          chunk: i
        }
      }));
      
      // Upsert in batches of 10
      for (let i = 0; i < vectors.length; i += 10) {
        const batch = vectors.slice(i, i + 10);
        await upsertVectors(batch);
        total += batch.length;
        process.stdout.write(`   ✅ ${total} records\r`);
      }
      
      console.log(`   📊 Done: ${vectors.length} vectors    `);
      
    } catch (err) {
      console.error(`   ❌ Error: ${err.message}`);
    }
  }
  
  console.log(`\n🎉 Total imported: ${total} records`);
  
  // Check stats
  const controlResp = await fetch('https://api.pinecone.io/indexes', {
    headers: { 'Api-Key': API_KEY }
  });
  const indexes = await controlResp.json();
  const index = indexes.indexes.find(i => i.name === INDEX_NAME);
  
  const statsResp = await fetch(`https://${index.host}/describe_index_stats`, {
    headers: { 'Api-Key': API_KEY }
  });
  const stats = await statsResp.json();
  console.log(`📊 Index has ${stats.totalVectorCount} vectors`);
}

importAll().catch(console.error);
