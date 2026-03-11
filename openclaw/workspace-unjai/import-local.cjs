#!/usr/bin/env node
/**
 * Simple embedding using local method - No API key needed!
 */

const { Pinecone } = require('@pinecone-database/pinecone');
const { readFileSync } = require('fs');
require('dotenv').config();

// Simple hash-based embedding (384 dimensions)
function simpleEmbedding(text, dim = 384) {
  const vector = new Array(dim).fill(0);
  
  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    vector[i % dim] += char / 1000;
  }
  
  // Normalize
  const magnitude = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0));
  return vector.map(v => v / (magnitude || 1));
}

// Import files to Pinecone
async function importFiles() {
  const pc = new Pinecone({ apiKey: process.env.PINECONE_API_KEY });
  const index = pc.index('aunjai-knowledge');
  
  const files = [
    'SOUL.md',
    'IDENTITY.md', 
    'AGENTS.md',
    'USER.md',
    'TOOLS.md',
    'BOOTSTRAP.md',
    'HEARTBEAT.md',
    'MEMORY.md'
  ];
  
  let totalRecords = 0;
  
  for (const filename of files) {
    try {
      console.log(`\n📖 Processing ${filename}...`);
      const content = readFileSync(`./${filename}`, 'utf-8');
      
      // Split into chunks
      const chunks = content
        .split('\n\n')
        .filter(chunk => chunk.trim().length > 50)
        .slice(0, 15); // 15 chunks per file
      
      for (let i = 0; i < chunks.length; i++) {
        const chunk = chunks[i].trim();
        const id = `${filename.replace('.md', '')}-${i}`;
        
        const embedding = simpleEmbedding(chunk, 384);
        
        await index.upsert([{
          id,
          values: embedding,
          metadata: {
            text: chunk.substring(0, 1500),
            source: filename,
            chunkIndex: i,
            timestamp: new Date().toISOString(),
          }
        }]);
        
        totalRecords++;
        process.stdout.write(`  ✅ ${id} (${totalRecords} total)\r`);
      }
      
      console.log(`  📊 ${chunks.length} chunks saved from ${filename}`);
      
    } catch (error) {
      console.error(`  ❌ Error with ${filename}:`, error.message);
    }
  }
  
  console.log(`\n🎉 Import complete! Total: ${totalRecords} records`);
  
  const stats = await index.describeIndexStats();
  console.log(`📊 Index now has ${stats.totalRecordCount} records`);
}

importFiles().catch(console.error);
